"""The Stukeley 1740 book + the Commons-hosted Stukeley plates (task 209b, GOAL point 4):
fit/src_wiltshire_stukeley.py stages two kinds of rows into this task's own staging files
(files_wiltshire_b.jsonl + classified_wiltshire_b.jsonl): the three visually-verified Commons
rows (205-Kip pattern) and the book's two verified site-plan plates (TAB. XI the numbered plan
as a fold-out, TAB. XXIII the Area plan with the Avenue - offline, the evidence is the plate's
own printed header, since the book has no list of plates). The Internet Archive BMB scan of
*Stonehenge, a Temple Restor'd to the British Druids* (1740, 166 leaves) runs through the
unmodified book machinery (per-book artifacts only - the shared index.jsonl and validation.json
are never written, 211 rebuilds them). The tests are offline: a socket-blocking fixture makes
any network attempt fail loud, so the evidence check runs from the stored fields only (200's
fail-closed box) and commons.info is a recording fake. They pin the stage() guards (a live size
drift, the canonical files.jsonl guard - the three 211-merge states: a staged row absent from the
canonical file, one already merged with identical content, a different row holding the same (site,
title) key - plus the original title-only clash, the two Petrie 1880 files - and the one date
override), the
date bookkeeping on every staged row, the offline --check (join + the evidence pass on every
staged row), the golden sample (regenerated only via --golden, for an intended change),
register() (a BOOKS entry ONLY - no wrap, the key difference from 209a's Hoare) and --status
(offline, from a fabricated bookreader cache). No LLM calls ever run in the tests (the triage
stages are live-only)."""
import json
import os
import socket
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in (os.path.join(ROOT, "fit"), os.path.join(ROOT, "pipeline")):
    if d not in sys.path:
        sys.path.insert(0, d)
import books  # noqa: E402  pipeline/books.py (BOOKS, LLM_URLS, llm_up, the triage stages)
import books_ia  # noqa: E402  pipeline/books_ia.py (RAW, the bookreader cache)
import commons  # noqa: E402  pipeline/commons.py (info/year_of/keep; info is monkeypatched)
import evidence  # noqa: E402  fit/evidence.py (the offline check over the staged rows)
import src_wiltshire_stukeley as src  # noqa: E402  fit/src_wiltshire_stukeley.py, the module under test

FILES_B_REAL = src.FILES_B  # the real staging file, snapshotted before any test monkeypatches src.FILES_B

GOLDEN = os.path.join(ROOT, "tests", "golden", "src_wiltshire_stukeley_sample.json")
PETRIE_TITLE = "File:47 of 'Stonehenge- plans, descriptions and theories' (11135894643).jpg"

# The three live-verified rows, verbatim from the 2026-10-12/13 live check (session 2): the
# dump date as Commons carries it (Houghton already '1743', the Dessin '1722', kitscoty none),
# the description as info() stores it, and the live sizes the STAGED table pins.
FAKE_META = {
    "File:Houghton Arc 855.214 - Stukely, the Druid temple of Abury.jpg": {
        "url": "https://example.org/houghton", "w": 2269, "h": 1362, "mime": "image/jpeg",
        "date": "1743",
        "desc": ("Illustration labeled \"A Scenographic view of the Druid temple of Abury in north "
                 "Wiltshire as in its original\". From  Abury, a temple of the British druids, and "
                 "some others described  (London: 1743), by William Stukeley (1687-1765).  Arc "
                 "855.214*, Houghton Library , Harvard University"),
        "artist": "William Stukeley (author)", "license": "Public domain", "page": "",
    },
    "File:Stonehenge Dessin Stukeley 1722 03547.jpg": {
        "url": "https://example.org/dessin", "w": 4620, "h": 2430, "mime": "image/jpeg",
        "date": "1722", "desc": "Stonehenge Dessin Stukeley 1722.",
        "artist": "G.Garitan", "license": "CC BY-SA 3.0", "page": "",
    },
    "File:Stukelykitscoty.jpg": {
        "url": "https://example.org/kitscoty", "w": 1020, "h": 320, "mime": "image/jpeg",
        "date": "", "desc": "", "artist": "", "license": "", "page": "",
    },
}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The inventory work is offline by contract; make any network attempt in this module's tests
    fail loud (commons.info is monkeypatched per test; the LLM ports are monkeypatched too)."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    monkeypatch.setattr(commons, "info", lambda titles: {t: dict(m) for t, m in FAKE_META.items()})
    monkeypatch.setattr(books, "llm_up", lambda url: False)


def _merge_states(tmp_path, monkeypatch):
    """The 211 merge states of the canonical files.jsonl as a temp copy (the tests hold whether or
    not 211's live merge has run on this checkout). point(files_rows) points the module's
    FILES_CANONICAL at a temp file built in that state: files_pre is the canonical file with this
    module's own rows removed (the other sources' merged rows are untouched; the guards do not
    care about them) and staged_lines are the module's own staged rows, byte-identical to what
    211's first-row-wins merge appends. The staged rows are read from the REAL staging file
    (FILES_B_REAL): some tests monkeypatch src.FILES_B at a temp write target."""
    staged = src._load(FILES_B_REAL)
    skeys = {(r["site"], r["title"]) for r in staged}
    files_pre = [json.dumps(r, ensure_ascii=False) for r in src._load(src.FILES_CANONICAL)
                 if (r.get("site"), r.get("title")) not in skeys]
    staged_lines = [json.dumps(r, ensure_ascii=False) for r in staged]

    def point(files_rows):
        p = tmp_path / "files.jsonl"
        p.write_text("\n".join(files_rows) + "\n", encoding="utf-8")
        monkeypatch.setattr(src, "FILES_CANONICAL", str(p))

    return point, files_pre, staged_lines


def test_stage_offline(tmp_path, monkeypatch, capsys):
    """stage() on a temp tree with the fake meta: the three Commons rows then the book's two plan
    rows (offline; their evidence is the printed list entry, stored verbatim in the row) - five
    rows total. The kitscoty row alone carries the Kip/Mackenzie date override (date '1722' - the
    1722 Itinerarium style attribution - and date_commons '' because the dump date was empty), the
    other Commons rows keep the raw dump date with no date_commons key; the book rows carry no
    dump date at all, only the work's year 1740. The canonical files.jsonl is a temp copy in the
    pre-merge state (no staged rows in it yet), so the test holds whether or not 211's live merge
    has run on this checkout. A second run is an idempotent no-op; and
    fit/evidence.py's check passes offline on all five from the stored fields alone."""
    monkeypatch.setattr(src, "FILES_B", str(tmp_path / "files_b.jsonl"))
    monkeypatch.setattr(src, "CLASSIFIED_B", str(tmp_path / "classified_b.jsonl"))
    point, files_pre, _ = _merge_states(tmp_path, monkeypatch)
    point(files_pre)  # the pre-merge state: the staged rows are not in the canonical file yet
    src.stage()
    out = capsys.readouterr().out
    assert "staged: 3 new pictures" in out and "book: 2 new plan rows" in out, out
    files = src._load(src.FILES_B)
    cls = src._load(src.CLASSIFIED_B)
    assert len(files) == 5 and len(cls) == 5
    assert [(r["site"], r["year"]) for r in files] == [
        ("avebury-q661855", 1743), ("stonehenge-q39671", 1722), ("kit-s-coty-house-q4222497", 1722),
        ("stonehenge-q39671", 1740), ("stonehenge-q39671", 1740)]
    for r in files:
        if r.get("book") == src.KEY:  # the book rows: no Commons dump date, just the work's year
            assert "date" not in r and r["page_type"] == "plate_site_plan" and r["wd_plan"] is False
            assert r["evidence"]["kind"] == "caption_coords" and r["evidence"]["dist_m"] == 0.0
            assert r["evidence"]["list_entry"].startswith((r["plate"] + "|"))
            assert r["evidence"]["list_entry"] in src.STUKLEY_PLATES  # the entry is the evidence
        elif "Stukelykitscoty" in r["title"]:
            assert r["date"] == "1722" and r["date_commons"] == ""  # the only override
        else:
            assert r["date"] in ("1743", "1722") and "date_commons" not in r
        assert r["evidence"]["kind"] == "caption_coords" and r["evidence"]["dist_m"] == 0.0
    assert {(r["site"], r["title"]) for r in cls} == {(r["site"], r["title"]) for r in files}
    assert [r["p_plan"] for r in cls] == [1.0, 0.0, 0.0, 1.0, 1.0]  # the Avebury plan, two views, two book plans
    src.stage()  # a second run: an idempotent no-op
    out = capsys.readouterr().out
    assert "staged: 0 new pictures" in out and "book: 0 new plan rows" in out, out
    assert len(src._load(src.FILES_B)) == 5 and len(src._load(src.CLASSIFIED_B)) == 5
    code, text = evidence.check(src.FILES_B, src.NO_BOOKS)
    assert code == 0, text
    assert "evidence: 5 rows, 5 pass, 0 fail, 0 no-tie" in text, text


def test_canonical_title_clash_fails_loud(tmp_path, monkeypatch):
    """The title-only canonical guard: a STAGED row whose title sits in the canonical
    files.jsonl (here the Petrie 1880 file 47, rows 713/714 - found and already canonical by this
    task's 2026-10-12 Commons check) fails loud no matter what site a rogue row names, and
    nothing is written. The canonical file is a temp copy in the pre-merge state (the Petrie row
    is in it in both states, so the test holds whether or not 211's live merge has run)."""
    monkeypatch.setattr(src, "FILES_B", str(tmp_path / "files_b.jsonl"))
    monkeypatch.setattr(src, "CLASSIFIED_B", str(tmp_path / "classified_b.jsonl"))
    point, files_pre, _ = _merge_states(tmp_path, monkeypatch)
    point(files_pre)
    monkeypatch.setattr(commons, "info", lambda titles: {})  # the clash fires before any meta use
    monkeypatch.setattr(src, "STAGED", [(PETRIE_TITLE, "avebury-q661855", "Abury", "1743",
                                         "rogue", "view", 2245, 2852)] + src.STAGED[1:])  # setitem is dicts only
    with pytest.raises(SystemExit, match="canonical files.jsonl"):
        src.stage()
    assert not os.path.exists(src.FILES_B) and not os.path.exists(src.CLASSIFIED_B)


def test_check_staged_offline(capsys):
    """--check, offline: the staged files join (every row names an existing catalog site - the three
    Commons sites and stonehenge for the book rows, so no extras file -; (site, title) unique; a
    staged row whose (site, title) key is in the canonical files.jsonl is a no-op only when
    identical to the canonical row - 211's first-row-wins merge - a different row holding the key,
    or a title held by a different site, is still a problem; classified rows 1:1) and every staged
    row PASSes the evidence check from stored fields alone."""
    code = src.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, f"join problems:\n{out}"
    assert "evidence: 5 rows, 5 pass, 0 fail, 0 no-tie" in out, out
    rows = src._load(src.FILES_B)
    assert len(rows) == 5
    for r in rows:
        assert f"PASS caption_coords  {r['site']}|{r['title']}" in out, \
            f"missing PASS line for {r['site']}|{r['title']}:\n{out}"


def test_check_staged_three_states(tmp_path, monkeypatch, capsys):
    """The 211 merge states of the --check guard, hermetically (temp copy of the canonical file,
    so the test holds whether or not 211's live merge has run on this checkout): (a) staged rows
    ABSENT from the canonical file (the pre-merge state) - check 0, no join problems, the
    evidence all PASS; (b) staged rows present with IDENTICAL content (the 211 first-row-wins
    merge has run) - check 0, no join problems: an already-merged row is a no-op; (c) the same
    (site, title) key held by a DIFFERENT row - check 1, one join problem naming exactly that
    key and no other."""
    point, files_pre, staged_lines = _merge_states(tmp_path, monkeypatch)
    staged = src._load(src.FILES_B)
    evidence_line = f"evidence: {len(staged)} rows, {len(staged)} pass, 0 fail, 0 no-tie"

    # (a) pre-merge: the staged rows are not in the canonical file yet
    point(files_pre)
    code = src.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert evidence_line in out, out

    # (b) the 211 merge ran: every staged row is in the canonical file with identical content
    point(files_pre + staged_lines)
    code = src.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert evidence_line in out, out

    # (c) the same (site, title) key held by a DIFFERENT row: the pre-merge conflict protection
    # still fires
    victim = staged[0]
    k = (victim["site"], victim["title"])
    other = dict(victim, name="a different row holds this key")
    lines = [json.dumps(other, ensure_ascii=False) if (r["site"], r["title"]) == k
             else json.dumps(r, ensure_ascii=False) for r in staged]
    point(files_pre + lines)
    code = src.check_staged()
    out = capsys.readouterr().out
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: staged row already in the canonical files.jsonl: {k} "
                    f"(a different row holds the key)"], join
    assert evidence_line in out, out


def test_stage_offline_three_states(tmp_path, monkeypatch, capsys):
    """stage() under the 211 merge states, hermetically (temp copy of the canonical file; the live
    Commons metadata served by the autouse fixture; the book leg reads the checked-in stage-A
    file) - no network, no ports, no writes outside the temp dir: (a) staged rows ABSENT from
    the canonical file (pre-merge) - a no-op re-stage (the rows are already in the module's
    staging files); (b) staged rows present with IDENTICAL content (the 211 merge has run) -
    still a no-op: an already-merged row is never re-written; (c) the first staged key (Commons
    leg) held by a DIFFERENT row - SystemExit, nothing written; (d) a book key (book leg) held
    by a different row - the Commons leg passes as a no-op and the book leg is refused."""
    point, files_pre, staged_lines = _merge_states(tmp_path, monkeypatch)
    staged = src._load(src.FILES_B)

    def no_op():
        out = capsys.readouterr().out
        assert "staged: 0 new pictures" in out and "book: 0 new plan rows" in out, out

    # (a) pre-merge: the staged rows are not in the canonical file yet
    point(files_pre)
    before = open(src.FILES_B, encoding="utf-8").read()
    src.stage()
    no_op()
    assert open(src.FILES_B, encoding="utf-8").read() == before

    # (b) the 211 merge ran: every staged row is in the canonical file with identical content
    point(files_pre + staged_lines)
    src.stage()
    no_op()
    assert open(src.FILES_B, encoding="utf-8").read() == before

    # (c) the first staged key (the Houghton Avebury plan) held by a different row: refused, nothing written
    victim = staged[0]
    k = (victim["site"], victim["title"])
    other = dict(victim, name="a different row holds this key")
    lines = [json.dumps(other, ensure_ascii=False) if (r["site"], r["title"]) == k
             else json.dumps(r, ensure_ascii=False) for r in staged]
    point(files_pre + lines)
    with pytest.raises(SystemExit) as exc:
        src.stage()
    assert victim["title"] in str(exc.value) and "different row holds the key" in str(exc.value), str(exc.value)
    assert open(src.FILES_B, encoding="utf-8").read() == before

    # (d) a book key (TAB. XI) held by a different row: the Commons leg is a no-op, the book leg refuses
    book = [r for r in staged if r.get("book") == src.KEY][0]
    bk = (book["site"], book["title"])
    bother = dict(book, name="a different row holds this key")
    lines = [json.dumps(bother, ensure_ascii=False) if (r["site"], r["title"]) == bk
             else json.dumps(r, ensure_ascii=False) for r in staged]
    point(files_pre + lines)
    with pytest.raises(SystemExit) as exc:
        src.stage()
    assert book["title"] in str(exc.value) and "different row holds the key" in str(exc.value), str(exc.value)
    assert open(src.FILES_B, encoding="utf-8").read() == before


def test_golden_sample_matches_staged_rows(tmp_path):
    """tests/golden/src_wiltshire_stukeley_sample.json (written by the module's --golden: all three
    staged file rows with their classified rows, keys sorted, checked/date_commons normalized) is
    the staged rows exactly - the pin the staging files are final against; regenerate only via
    --golden for an intended change."""
    p = tmp_path / "golden.json"
    src.golden(str(p))
    golden = json.load(open(p, encoding="utf-8"))
    files = src._load(src.FILES_B)
    cls = src._load(src.CLASSIFIED_B)
    want = {"files": src._norm(files), "classified": src._norm(cls)}
    assert golden == want, "the staged rows differ from the golden sample - an intended change needs --golden"
    committed = json.load(open(GOLDEN, encoding="utf-8"))
    assert committed == want


def test_register_adds_the_book_entry_and_touches_nothing_else(monkeypatch):
    """register(): books.BOOKS gets the exact entry (ia/region/year/cite/why; the cite is
    hand-written because the IA metadata carries no title/date/creator), and NOTHING else is
    touched - books_ia.pages/page_texts and books.fetch_triage stay the originals (the book
    really is on IA: the key difference from 209a's Hoare, which wraps all three for its local
    copy); with STUKLEY_PLATES transcribed it is injected into books_lists.PLATES in-process
    (the 213/civitates hand-list pattern - pipeline/books_lists.py is owned by 217, so the
    injection is in-process, not a file edit). The BOOKS entry is managed with setitem so the
    teardown removes it (a bare assignment would leak the mutation across tests)."""
    monkeypatch.setitem(books.BOOKS, src.KEY, None)  # a clean baseline, removed again by the teardown
    pages_before, texts_before, fetch_before = books_ia.pages, books_ia.page_texts, books.fetch_triage
    src.register()
    src.register()  # idempotent
    assert books.BOOKS[src.KEY] == dict(ia=src.IA, region=src.REGION, year=src.YEAR,
                                        cite=src.CITE, why=src.WHY)
    assert books_ia.pages is pages_before and books_ia.page_texts is texts_before \
        and books.fetch_triage is fetch_before
    import books_lists
    assert books_lists.PLATES[src.IA] == src.STUKLEY_PLATES  # the hand list is injected in-process


def test_book_rows_staged_in_files_b():
    """The committed staging files hold the book's two verified site-plan plates (209b box 3):
    TAB. XI the numbered plan (a fold-out: leaf_n 56 + leaf_n2 57, one row) and TAB. XXIII the Area
    plan (leaf 111), both stonehenge-q39671 year 1740, each with the 200 caption_coords evidence
    whose list_entry is the plate's own printed header (the book has no list of plates) and whose
    place coordinates are the site's own point (dist 0.0); each has its hand-classified row
    (p_plan 1.0). After 211's merge the titles may sit in the canonical files.jsonl: a title is a
    problem only when a DIFFERENT row holds the (site, title) key (the join check)."""
    files = src._load(src.FILES_B)
    book = [r for r in files if r.get("book") == src.KEY]
    assert len(book) == 2 and len(files) == 5
    assert [r["plate"] for r in book] == ["XI", "XXIII"]
    canonical, canonical_titles = {}, set()
    for x in src._load(src.FILES_CANONICAL):
        if x.get("title"):
            k = (x.get("site"), x.get("title"))
            if k not in canonical:  # first row wins, as in the 211 merge
                canonical[k] = src._canon_norm(x)
            canonical_titles.add(x["title"])
    for r in book:
        assert r["site"] == "stonehenge-q39671" and r["year"] == 1740 and r["ia_id"] == src.IA
        assert r["evidence"]["kind"] == "caption_coords" and r["evidence"]["dist_m"] == 0.0
        assert r["evidence"]["list_entry"] in src.STUKLEY_PLATES
        assert r["title"] not in canonical_titles \
            or canonical[(r["site"], r["title"])] == src._canon_norm(r)
    assert book[0]["leaf_n"] == 56 and book[0]["leaf_n2"] == 57 and book[1]["leaf_n"] == 111
    assert book[0]["id"].endswith("_n0056_n0057") and book[1]["id"].endswith("_n0111")
    cls = src._load(src.CLASSIFIED_B)
    book_cls = [c for c in cls if (c["site"], c["title"]) in {(r["site"], r["title"]) for r in book}]
    assert len(book_cls) == 2 and all(c["p_plan"] == 1.0 for c in book_cls)


def test_status_offline_fabricated_cache(tmp_path, monkeypatch, capsys):
    """--status, offline: the leaf count and sizes come from the CACHED bookreader.json (a
    fabricated stand-in, since data/raw is gitignored and absent in a fresh checkout) and no
    fetch happens; triage progress reads the triage tree under the same root; the LLM ports are
    monkeypatched down."""
    bookdir = tmp_path / "books" / src.IA
    bookdir.mkdir(parents=True)
    pages = [{"leafNum": k + 1, "width": 900 + k, "height": 1200, "uri": ""} for k in range(5)]
    (bookdir / "bookreader.json").write_text(
        json.dumps({"data": {"brOptions": {"data": [pages]}}}), encoding="utf-8")
    monkeypatch.setattr(books_ia, "RAW", str(tmp_path / "books"))
    src.status()
    out = capsys.readouterr().out
    assert "166" not in out and "5 leaves, triage 0/5" in out, out
    assert "long side 1200-1200 px" in out, out
    assert "none up (the triage stages exit until a Qwen replica answers)" in out, out


def test_status_reports_missing_cache(tmp_path, monkeypatch, capsys):
    """--status with no cached bookreader.json (a fresh checkout): it reports 'not fetched yet'
    instead of fetching over the network."""
    monkeypatch.setattr(books_ia, "RAW", str(tmp_path / "books"))
    src.status()
    out = capsys.readouterr().out
    assert "not fetched yet (no cached bookreader.json; --fetch first)" in out, out
