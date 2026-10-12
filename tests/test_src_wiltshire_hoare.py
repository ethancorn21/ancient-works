"""The Hoare Cherhill fetch leg (task 209a, GOAL.md point 4): fit/src_wiltshire_hoare.py adapts the book
machinery's fetch to the human-downloaded copy (data/raw/books/hoare_cherhill1821/, ask_human 001) -
the 207c local-copy pattern. Hermetic: the book directory is monkeypatched to a temp dir holding a
synthetic stand-in book (a few solid-colour page images, unevenly padded names to prove the natural
ordering), and a socket-blocking fixture makes any network attempt fail loud - so these tests also
prove the fetch leg is network-free. The invariant that lets the UNMODIFIED machinery run on the local
copy (the re-encodes land exactly where books.triage_path reads, and the register() wrap passes every
other book id through to the original calls) is pinned in test_register_swaps_in_local_copy_only.
The staging / check / golden tests were never built (209a dropped at iteration 151 - the human declined
the book download); these three fetch-leg tests are all the module has.
"""
import json
import os
import socket
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in (os.path.join(ROOT, "fit"), os.path.join(ROOT, "pipeline")):
    if d not in sys.path:
        sys.path.insert(0, d)
import books_ia  # noqa: E402
import src_wiltshire_hoare as src  # noqa: E402  the module under test


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The fetch leg is local-files only by contract; make any network attempt fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def _page(path, size, color):
    from PIL import Image
    im = Image.new("RGB", size, color)
    im.save(path, "JPEG", quality=95)


def _center(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    return im.size, im.getpixel((im.width // 2, im.height // 2))


def test_fetch_reencodes_orders_and_is_idempotent(tmp_path, monkeypatch, capsys):
    """--fetch on a stand-in book: unevenly padded file names come out in natural (not lexicographic)
    order - n0000 = 1.jpg, n0001 = 2.jpg, n0002 = 10.jpg (lexicographic would say 1,10,11,2); the
    one page over the triage long side is downscaled to 1400 px, the smaller ones keep their size;
    a second run is a no-op (files byte-identical)."""
    _page(tmp_path / "1.jpg", (2000, 1200), (255, 0, 0))    # red, over the long side
    _page(tmp_path / "2.jpg", (600, 400), (0, 255, 0))      # green
    _page(tmp_path / "10.jpg", (800, 800), (0, 0, 255))     # blue
    _page(tmp_path / "11.jpg", (500, 700), (128, 128, 128))  # grey
    monkeypatch.setattr(src, "DIR", str(tmp_path))
    src.fetch()
    out = capsys.readouterr().out
    assert "4 local pages, triage 0/4 done, 4 to encode" in out, out
    assert "triage 4/4" in out, out

    triage = tmp_path / "triage"
    size, (r, g, b) = _center(triage / "n0000.jpg")
    assert size == (1400, 840) and r > 200 and g < 80 and b < 80      # 1.jpg, downscaled, red
    size, (r, g, b) = _center(triage / "n0001.jpg")
    assert size == (600, 400) and g > 200 and r < 80 and b < 80       # 2.jpg, green
    size, (r, g, b) = _center(triage / "n0002.jpg")
    assert size == (800, 800) and b > 200 and r < 80 and g < 80       # 10.jpg, blue (NOT 11)
    size, (r, g, b) = _center(triage / "n0003.jpg")
    assert size == (500, 700) and 90 <= r <= 165 and 90 <= g <= 165 and 90 <= b <= 165  # 11.jpg

    before = sorted((triage / f).read_bytes() for f in os.listdir(triage))
    src.fetch()
    out = capsys.readouterr().out
    assert "4 local pages, triage 4/4 done, 0 to encode" in out, out
    after = sorted((triage / f).read_bytes() for f in os.listdir(triage))
    assert before == after  # idempotent: the re-run wrote nothing


def test_fetch_missing_book_fails_loud(tmp_path, monkeypatch, capsys):
    """No copy yet (the book is still waiting on ask_human 001): --fetch fails with an actionable
    message, not a traceback - for both a missing book dir and an empty one."""
    for dir in (tmp_path, tmp_path / "not-there-yet"):
        monkeypatch.setattr(src, "DIR", str(dir))
        with pytest.raises(SystemExit) as ei:
            src.fetch()
        msg = str(ei.value)
        assert str(dir) in msg and "ask_human 001" in msg, msg


def test_register_swaps_in_local_copy_only(tmp_path, monkeypatch):
    """register(): the book lands in books.BOOKS; for THIS id the machinery's IA-only calls
    (books_ia.pages, books_ia.page_texts, books.fetch_triage) read the local copy, while every other
    book id passes through to the original (here, a recording fake - no other book may be touched by
    this module); a second register() is a no-op. The default book dir must make DIR/triage exactly
    books.triage_path's slot, so the unmodified triage stages find the local re-encodes."""
    from PIL import Image
    import books
    _page(tmp_path / "0001.jpg", (300, 200), (255, 0, 0))
    _page(tmp_path / "0002.jpg", (200, 300), (0, 255, 0))
    monkeypatch.setattr(src, "DIR", str(tmp_path))

    calls = []
    monkeypatch.setitem(books.BOOKS, src.KEY, None)  # register() writes this entry bare; setitem makes the teardown restore (remove) it
    monkeypatch.delattr(books_ia, "_hoare_wrapped", raising=False)
    monkeypatch.setattr(books_ia, "pages", lambda ia_id: calls.append(ia_id) or ["SENTINEL"])
    monkeypatch.setattr(books_ia, "page_texts", lambda ia_id: {"sentinel": 1})
    monkeypatch.setattr(books, "fetch_triage", lambda ia_id, page: f"IA-{ia_id}")

    src.register()
    src.register()  # idempotent

    assert books.BOOKS[src.KEY] == dict(ia=src.ID, region="Europe", year="1821",
                                       cite=src.CITE, why=src.WHY)
    # this id: local pages, no OCR text, local re-encode (no fake call, no network)
    pages = books_ia.pages(src.ID)
    assert [p["n"] for p in pages] == [0, 1] and [p["leafNum"] for p in pages] == [1, 2]
    assert (pages[0]["width"], pages[0]["height"]) == (300, 200)
    assert books_ia.page_texts(src.ID) == {}
    assert books.fetch_triage(src.ID, pages[0]) == src.triage_of(0)
    assert os.path.exists(src.triage_of(0))
    # any other book id: the original call, untouched
    assert books_ia.pages("some-other-book") == ["SENTINEL"]
    assert books_ia.page_texts("some-other-book") == {"sentinel": 1}
    assert books.fetch_triage("some-other-book", {}) == "IA-some-other-book"
    assert calls == ["some-other-book"]  # the fake was called exactly once, never with our id

    # the slot invariant: with the default book dir the triage tree IS books.triage_path's
    expect = os.path.normpath(os.path.dirname(books.triage_path(src.ID, 0)))
    got = os.path.normpath(os.path.join(src.DEFAULT_DIR, "triage"))
    assert got == expect, f"triage slot moved: {got} != {expect} - the unmodified machinery would miss"
