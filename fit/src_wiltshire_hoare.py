"""Hoare, Ancient Wiltshire, the Hundred of Cherhill (1821): the volume carrying the old plans of
Stonehenge, Avebury, Silbury Hill and the West Kennet long barrow (task 209a, GOAL.md point 4).
The book is not on IA (searched 2026-10-12/13) and its two remaining sources refuse this VM
(HathiTrust HTTP 403, Google Books 429), and the human declined to download it (ask_human 001,
refused between iterations 145 and 151: "just skip it"): task 209a is DROPPED and this module is DORMANT - it stays in
the tree so that, if a complete scan of the volume ever lands in data/raw/books/hoare_cherhill1821/
(one image per leaf page, filenames sorting in book order - a library digitisation, an IA
acquisition), this module adapts the fetch to those local files - the 207c pattern - and
everything after the triage images runs on the unmodified book machinery (books.run_stage,
books_lists, fit/evidence.py).

usage: src_wiltshire_hoare.py --fetch        local (no network): re-encode the human-downloaded
                                             pages to triage size (1400 px long side, JPEG q88)
                                             at data/raw/books/hoare_cherhill1821/triage/n%04d.jpg
                                             (books.triage_path's exact slot; resumable, idempotent)
       src_wiltshire_hoare.py --status       offline: leaf count and sizes, triage progress, LLM ports
       src_wiltshire_hoare.py --triage A|F|B working phase (Qwen replicas on 127.0.0.1): run the stage
                                             through books.run_stage unmodified (register() swaps in
                                             the local page list and local fetch for this book id only)

Later legs (never built - the copy never arrived; add them if the module is ever revived with a
scan): --list (transcribe the printed list of plates, books_lists PLATES pattern, into
data/books/lists/hoare_cherhill1821.json + .map.json via books_lists.cmd_ocrmap), --stage (rows
into data/commons/files_wiltshire_a.jsonl + classified_wiltshire_a.jsonl, plus
extras_wiltshire_a.jsonl when a plate shows a Wiltshire earthwork not in the catalog; the 200
evidence field and the 1821 date on every row), --check (offline join + fit/evidence.py),
--golden (tests/golden/src_wiltshire_hoare_sample.json). The lead record: docs/lead_wiltshire.md
(the Hoare section records the drop). The system python3 has no numpy/PIL, so every command runs
under .venv/bin/python; the module top stays stdlib-only (books, books_ia and PIL import lazily).
"""
import concurrent.futures as cf
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))  # books / books_ia import lazily, at call time

KEY = "hoare_cherhill1821"
ID = "hoare_cherhill1821"  # doubles as the books.BOOKS ia field; the triage slot is ia.RAW/<ID>/triage/
DEFAULT_DIR = os.path.join(ROOT, "data", "raw", "books", ID)  # the human-downloaded copy (gitignored)
DIR = DEFAULT_DIR  # a test may point this at a temp stand-in book; the triage tree follows it
TRIAGE_PX = 1400  # books.TRIAGE_PX, re-stated so the fetch leg does not import books
REGION = "Europe"
YEAR = "1821"
CITE = ("R. C. Hoare, Ancient Wiltshire: the Hundred of Cherhill (vol. 3), London 1821 "
        "(title wording to be finalized from the copy's title page)")
WHY = ("The volume that carries the Stonehenge/Avebury/Silbury/West Kennet plans. Not on IA "
       "(2026-10-12/13 searches, docs/lead_wiltshire.md); HathiTrust 403s and Google Books 429s "
       "this VM and the human declined to download it (ask_human 001, refused before iteration "
       "151, task 209a dropped) - the module stays dormant for a copy that never arrived. If a complete "
       "scan ever lands in data/raw/books/hoare_cherhill1821/, the local fetch leg below feeds the "
       "unmodified machinery (the 207c pattern).")

IMG_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp"}


def _natkey(path):
    """Natural order of the file name: '2.jpg' before '10.jpg' (unevenly padded download names)."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", os.path.basename(path))]


def local_files():
    return sorted((os.path.join(DIR, f) for f in os.listdir(DIR)
                  if os.path.splitext(f)[1].lower() in IMG_EXTS),
                  key=_natkey)


def local_pages():
    """The BookReader-shaped page list of the local copy: n = 0-based leaf index (n0000 = first leaf),
    leafNum = 1-based (the books_ia convention), width/height from the file itself."""
    from PIL import Image
    if not os.path.isdir(DIR):
        raise SystemExit(f"no local copy in {DIR} yet - the human-downloaded pages (ask_human 001): one "
                         f"image per leaf page, filenames sorting in book order (0001.jpg, 0002.jpg, ...), "
                         f"or the book's PDF (say so in the reply to the request)")
    files = local_files()
    if not files:
        raise SystemExit(f"no page images in {DIR} yet - the human-downloaded pages (ask_human 001): one "
                         f"image per leaf page, filenames sorting in book order (0001.jpg, 0002.jpg, ...), "
                         f"or the book's PDF (say so in the reply to the request)")
    pages = []
    for n, f in enumerate(files):
        with Image.open(f) as im:
            w, h = im.size
        pages.append({"n": n, "leafNum": n + 1, "width": w, "height": h, "file": f, "uri": ""})
    return pages


def triage_of(n):
    return os.path.join(DIR, "triage", f"n{n:04d}.jpg")


def fetch_local(page):
    """One local page -> the triage slot (1400 px long side, JPEG q88, .part + rename like books.fetch_triage).
    Idempotent: an existing triage image is kept."""
    from PIL import Image
    target = triage_of(page["n"])
    if os.path.exists(target):
        return target
    os.makedirs(os.path.dirname(target), exist_ok=True)
    im = Image.open(page["file"]).convert("RGB")
    if max(im.size) > TRIAGE_PX * 1.05:
        im.thumbnail((TRIAGE_PX, TRIAGE_PX), Image.LANCZOS)
    import threading
    tmp = f"{target}.{os.getpid()}.{threading.get_ident()}.part.jpg"  # fetcher and triage may race on a page
    im.save(tmp, "JPEG", quality=88)
    os.replace(tmp, target)
    return target


def fetch():
    """All local pages -> triage images. The default book dir makes DIR/triage exactly
    books.triage_path(<ID>, n) (the test pins that invariant), so the unmodified triage stages
    read these files; a temp DIR (the test) keeps the whole tree inside the temp dir."""
    pages = local_pages()
    todo = [p for p in pages if not os.path.exists(triage_of(p["n"]))]
    print(f"{ID}: {len(pages)} local pages, triage {len(pages) - len(todo)}/{len(pages)} done, "
          f"{len(todo)} to encode", flush=True)
    if not todo:
        return
    os.makedirs(os.path.join(DIR, "triage"), exist_ok=True)

    def one(p):
        try:
            return fetch_local(p)
        except Exception as e:
            print(f"  n{p['n']} failed: {e!r:.150}", flush=True)

    with cf.ThreadPoolExecutor(4) as ex:
        list(ex.map(one, todo))
    done = sum(1 for p in pages if os.path.exists(triage_of(p["n"])))
    print(f"{ID}: triage {done}/{len(pages)}", flush=True)


def status():
    import books
    try:
        pages = local_pages()
    except SystemExit as e:
        print("book:", e, flush=True)
        pages = []
    if pages:
        done = sum(1 for p in pages if os.path.exists(triage_of(p["n"])))
        long = [max(p["width"], p["height"]) for p in pages]
        print(f"{ID}: {len(pages)} leaves, triage {done}/{len(pages)}, long side {min(long)}-{max(long)} px",
              flush=True)
    up = [u for u in books.LLM_URLS if books.llm_up(u)]
    print("LLM:", ", ".join(up) or "none up (the triage stages exit until a Qwen replica answers)",
          flush=True)


def register():
    """In-process registration + the local-copy adaptation (the 207c pattern): books.BOOKS gets this
    book, and books_ia.pages / books_ia.page_texts / books.fetch_triage are wrapped so that, for this
    id only, the machinery's IA-only calls read the human-downloaded files (no OCR text on a local
    copy: page_texts -> {}, the plate anchors come from Qwen). Every other book id passes through
    to the original call. Idempotent: a second register() is a no-op."""
    import books
    import books_ia
    if getattr(books_ia, "_hoare_wrapped", False):
        return
    books.BOOKS[KEY] = dict(ia=ID, region=REGION, year=YEAR, cite=CITE, why=WHY)
    orig_pages, orig_texts, orig_fetch = books_ia.pages, books_ia.page_texts, books.fetch_triage

    def pages(ia_id):
        return local_pages() if ia_id == ID else orig_pages(ia_id)

    def page_texts(ia_id):
        return {} if ia_id == ID else orig_texts(ia_id)

    def fetch_wrap(ia_id, page):
        return fetch_local(page) if ia_id == ID else orig_fetch(ia_id, page)

    books_ia.pages = pages
    books_ia.page_texts = page_texts
    books.fetch_triage = fetch_wrap
    books_ia._hoare_wrapped = True


def triage(stage):
    """Stage A/F/B through the unmodified books.run_stage (resumable; needs a live Qwen replica,
    else run_stage exits with its own message)."""
    local_pages()  # fails loud (no copy yet) before any LLM work
    import books
    register()
    {"A": books.cmd_triage_a, "F": books.cmd_triage_f, "B": books.cmd_triage_b}[stage]([KEY])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--fetch":
        fetch()
    elif a and a[0] == "--status":
        status()
    elif a and a[0] == "--triage" and len(a) >= 2 and a[1] in "AFB":
        triage(a[1])
    else:
        raise SystemExit(__doc__)
