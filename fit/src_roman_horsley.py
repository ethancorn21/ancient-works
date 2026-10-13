"""Horsley, *Britannia Romana, or the Roman Antiquities of Britain* (1732) (task 207a, GOAL point 4):
the book's ~121 engraved plates - mostly Roman inscriptions and sculptures (list kind "o") - and its
few genuine site plans (maps of forts/walls/towns, kind "s"), which are the only rows staged: into the
shared roman staging files (files_roman.jsonl + classified_roman.jsonl, rows tagged with this book's
key; extras_roman.jsonl for new sites only), each with the 200 evidence field (the book's own printed
list names the place) and the book's date (1732). 211 consolidates the *_roman staging into the
canonical index. The book is on IA (Google Books scan britanniaromanao00hors, 936 leaves; BookReader
pages + hOCR verified 2026-10-13, iteration 202), so the standard book machinery runs UNMODIFIED - no
local-copy wrap (the key difference from 209a's Hoare and 207c's Roy): books.cmd_fetch downloads the
triage pages, books.run_stage triages them, and (once HORSEY_PLATES is transcribed)
books_lists.cmd_ocrmap maps the list to leaves after an in-process injection into books_lists.PLATES
(the 213/civitates hand-list pattern). Per-book artifacts only: triage/britanniaromanao00hors.*.jsonl,
lists/britanniaromanao00hors.json + .map.json; the shared index.jsonl / validation.json are never
written by this module (211 rebuilds them).

usage: src_roman_horsley.py --fetch         live: triage-size page images, all 936 (books.cmd_fetch,
                                           resumable; the long pole of this task - run it in the
                                           background: nohup .venv/bin/python fit/src_roman_horsley.py
                                           --fetch; check progress with --status)
       src_roman_horsley.py --status        offline: leaf count + triage progress from the cached
                                           bookreader.json, the triage stage line counts, and which
                                           LLM ports answer
       src_roman_horsley.py --triage A|F|B  live (Qwen replicas on 127.0.0.1:8080/8081): the triage
                                           stages through books.cmd_triage_* unmodified (append-only,
                                           resumable)
       src_roman_horsley.py --list         live until HORSEY_PLATES is set: print the hOCR text of
                                           the book's front leaves (the printed list of plates, for
                                           transcription); once set: register() +
                                           books_lists.cmd_ocrmap -> the per-book lists/<ia>.json +
                                           .map.json only (the shared validation.json / index.jsonl
                                           are never written)
       src_roman_horsley.py [--stage]      stage the verified kind-s (site-plan) rows into
       [--dry]                            files_roman.jsonl + classified_roman.jsonl (+
                                           extras_roman.jsonl for new sites): append-only,
                                           idempotent, 200 evidence field per row (the printed list
                                           entry is the tie), 1732 on every row; --dry previews
       src_roman_horsley.py --check        offline (no network): join the staged roman rows (every row
                                           names an existing or staged site; every new site has its
                                           plans) and run fit/evidence.py's check over this book's
                                           staged rows
       src_roman_horsley.py --golden       write tests/golden/src_roman_horsley_sample.json

Later legs (built as the book lands, in order): --list (transcribe the printed list of plates from
the front-matter hOCR, verify against the list-page images - the kind column is a judgement from the
printed title, as in the 213/civitates pattern), then the stage-B boxes on the plan pages (the
stage-B leg reuses the unmodified machinery once the list exists: books.cmd_triage_b runs on A's
site pages + the list's kind-s leaves), then --stage / --check / --golden, and the stage-A/B recall
against the list recorded in the Horsley section of docs/lead_roman.md (books_lists.validate_book,
never the shared validation.json).

The system python3 has no numpy/PIL, so every command runs under .venv/bin/python; the module top
stays stdlib-only (books, books_ia, books_lists and evidence import lazily at call time, the
fit/src_kip.py idiom). The LLM replicas serve on 127.0.0.1:8080-8082 (verified 2026-10-13: 8080 and
8081 answer, 8082 down) - books.LLM_URLS' default port list already covers them since 215
re-pointed books.py, so no in-process patch is needed (the parent's pre-215 note is stale).
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))  # books / books_ia / books_lists import lazily, at call time

KEY = "horsley_britannia_romana_1732"
IA = "britanniaromanao00hors"
REGION = "Europe"
YEAR = 1732
CITE = ("John Horsley, Britannia Romana, or the Roman Antiquities of Britain: in three books, London 1732 "
        "(title per the IA record; the exact title page to be read from the first leaves when the fetch lands)")
WHY = ("Google Books scan (britanniaromanao00hors): 936 leaves, long side 2576-4116 px, hOCR page text + "
       "djvu.txt present - chosen 2026-10-11 (207) as the working copy. The British Museum copies "
       "(bim_eighteenth-century_britannia-romana-or-the_horsley-john_1732, 831 leaves ~14000 px images; "
       "the ..._0 copy, 827) stay the alternates only if specific pages of the Google copy are unreadable.")

# The shared roman staging files (207a/b/c all append here, rows tagged with their book; 211 consolidates).
FILES_ROMAN = os.path.join(ROOT, "data", "commons", "files_roman.jsonl")
CLASSIFIED_ROMAN = os.path.join(ROOT, "data", "commons", "classified_roman.jsonl")
EXTRAS_ROMAN = os.path.join(ROOT, "data", "catalog", "extras_roman.jsonl")
SITES_JSONL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")

# The books_lists PLATES format: plate|sub|title|page|kind. The printed list of plates (the front matter)
# transcribed here once the fetch lands: kind s = the few site plans/maps that get staged, kind o = the
# inscription and sculpture plates (indexed in the list mapping, each naming the site where the stone was
# found, but not staged as picture rows), kind u = unsure from the title alone.
HORSEY_PLATES = None  # set when transcribed; register() injects it into books_lists.PLATES in-process


def now():
    return time.strftime("%Y-%m-%d")


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def register():
    """In-process registration: books.BOOKS gets this book and (once transcribed) its plate list is
    injected into books_lists.PLATES - nothing else is touched, the book really is on IA, so the
    machinery's IA calls (pages, page_texts, fetch_triage) run unmodified. Idempotent."""
    import books
    books.BOOKS[KEY] = dict(ia=IA, region=REGION, year=YEAR, cite=CITE, why=WHY)
    if HORSEY_PLATES is not None:
        import books_lists
        books_lists.PLATES[IA] = HORSEY_PLATES


def fetch():
    """All triage-size page images (books.cmd_fetch, resumable; 936 leaves - the long pole, run it
    in the background; the download is to gitignored data/raw/books/<ia>/triage/)."""
    register()
    import books
    books.cmd_fetch([KEY])


def status():
    """Offline: leaf count and sizes from the cached bookreader.json (never a network fetch), the
    triage image count, the per-stage line counts, and which LLM ports answer."""
    import books
    import books_ia
    path = os.path.join(books_ia.RAW, IA, "bookreader.json")
    if not os.path.exists(path):
        print(f"{KEY} {IA}: not fetched yet (no cached bookreader.json; --fetch first)")
        return
    d = json.load(open(path))
    pages = [p for spread in d["data"]["brOptions"]["data"] for p in spread]
    long = [max(p["width"], p["height"]) for p in pages]
    done = sum(1 for n in range(len(pages)) if os.path.exists(books.triage_path(IA, n)))
    print(f"{KEY} {IA}: {len(pages)} leaves, triage {done}/{len(pages)}, long side {min(long)}-{max(long)} px")
    for stage in "AFB":
        p = os.path.join(books.OUT, "triage", f"{IA}.{stage}.jsonl")
        if os.path.exists(p):
            rows = _load(p)
            print(f"  stage {stage}: {len(rows)} rows ({sum(1 for r in rows if 'error' in r)} errors)")
    up = [u for u in books.LLM_URLS if books.llm_up(u)]
    print("LLM:", ", ".join(up) or "none up (the triage stages exit until a Qwen replica answers)")


def triage(stage):
    """Stage A/F/B through the unmodified books.run_stage (append-only, resumable; needs a live
    Qwen replica on 127.0.0.1, else run_stage exits with its own message)."""
    register()
    import books
    {"A": books.cmd_triage_a, "F": books.cmd_triage_f, "B": books.cmd_triage_b}[stage]([KEY])


def list_cmd():
    """Until HORSEY_PLATES is transcribed: print the hOCR text of the book's front leaves (the
    printed list of plates lives there; the hOCR pair is downloaded once and cached). Once
    transcribed: run books_lists.cmd_ocrmap over the injected plate list - it writes only the
    per-book lists/<ia>.json + .map.json (the map stays [] until stage A exists, as cmd_ocrmap
    guards)."""
    if HORSEY_PLATES is None:
        import books_ia
        texts = books_ia.page_texts(IA)  # downloads + caches the hOCR pair
        for leaf in sorted(texts)[:24]:
            print(f"--- leaf {leaf} ---")
            print(texts[leaf][:1500])
        return
    register()
    import books_lists
    books_lists.cmd_ocrmap([KEY])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] not in ("--fetch", "--status", "--triage", "--list", "--stage", "--dry", "--check", "--golden"):
        raise SystemExit(__doc__.strip().split("usage:")[1].strip())
    if a and a[0] == "--fetch":
        fetch()
    elif a and a[0] == "--status":
        status()
    elif a and a[0] == "--triage" and len(a) >= 2 and a[1] in "AFB":
        triage(a[1])
    elif a and a[0] == "--list":
        list_cmd()
    else:
        raise SystemExit("the stage/check/golden legs are not built yet (see the module docstring)")
