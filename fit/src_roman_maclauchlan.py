"""Maclauchlan, *Memoir, Written During a Survey of the Roman Wall* (1858) (task 207b, GOAL point 4):
the book's plates of Hadrian's Wall - detailed plans of the forts on the wall (Vindolanda,
Vercovicium, the milecastles, ...) alongside wall cross-sections and stretches of the wall itself.
Only the site-plan plates of a NAMED fort/structure with a location are staged: into the shared
roman staging files (files_roman.jsonl + classified_roman.jsonl, rows tagged with this book's key;
extras_roman.jsonl for new sites only), each with the 200 evidence field (the book's own printed
list names the place) and the book's date (the title-page year; the survey itself ran 1857-59 -
the discrepancy is recorded in docs/lead_roman.md). Wall sections alone are NOT sites (207 Notes).
211 consolidates the *_roman staging into the canonical index.

TWO Internet Archive copies, each used for what it does best (chosen 2026-10-11, 207):
  memoirwrittendu00maclgoog  the 1858 original (Google scan, 171 leaves, median 3290x5182 px):
                             the only source of the STAGED images; djvu.txt + djvu.xml only,
                             NO hOCR page index (page_texts 404s - per-leaf OCR comes from the
                             djvu.xml OBJECTs instead, the 208 Google-upload pattern).
  memoirwrittendur0000henr   the 1971 reprint (292 leaves, 1625x2697 px, hOCR present):
                             the OCR source for transcribing the book's printed list of plates
                             (its front matter mirrors the original's); never a staged image.
So: fetch/triage/stage images from the 1858 original; read the list from the 1971 reprint's
hOCR and cross-check it by eye against the original's list-page triage image.

usage: src_roman_maclauchlan.py --fetch         live: triage-size page images of the 1858 original,
                                           all 171 (books.cmd_fetch, resumable; ~15-20 min: run in
                                           the background: nohup .venv/bin/python
                                           fit/src_roman_maclauchlan.py --fetch; check with --status)
       src_roman_maclauchlan.py --status        offline: leaf count + triage progress from the cached
                                           bookreader.json, the triage stage line counts, and which
                                           LLM ports answer
       src_roman_maclauchlan.py --triage A|F|B  live (Qwen replicas on 127.0.0.1:8080/8081): the triage
                                           stages through books.cmd_triage_* unmodified (append-only,
                                           resumable)
       src_roman_maclauchlan.py --list         live until MACLAUCHLAN_PLATES is set: print the 1971
                                           reprint's hOCR front leaves (the printed list of plates,
                                           for transcription). Once set: register() + an in-process
                                           books_ia.page_texts swap to the djvu.xml text +
                                           books_lists.cmd_ocrmap -> the per-book
                                           lists/memoirwrittendu00maclgoog.json + .map.json only (the
                                           shared validation.json / index.jsonl are never written; the
                                           stage-A/B recall goes to the Maclauchlan section of
                                           docs/lead_roman.md via books_lists.validate_book)
       src_roman_maclauchlan.py --djvu [n ...]  live once: download the 1858 original's _djvu.xml (cached)
                                           and print its per-leaf OCR text - all leaves as a
                                           page-count check, or the named leaves (the list page, a
                                           title page, a plate header) for the cross-check against
                                           the reprint's hOCR
       src_roman_maclauchlan.py [--stage]      (not built yet) stage the verified site-plan rows
       [--dry]                                into files_roman.jsonl + classified_roman.jsonl (+
                                           extras_roman.jsonl for new sites)
       src_roman_maclauchlan.py --check        (not built yet) offline (no network): join the staged
                                           roman rows and run fit/evidence.py's check over this book's
                                           rows
       src_roman_maclauchlan.py --golden       (not built yet) write tests/golden/src_roman_maclauchlan_sample.json

Later legs (built as the book lands, in order): --list (transcribe the printed list of plates from
the 1971 reprint's hOCR, verify against the original's list-page triage image - the kind column is
a judgement from the printed title: s = a fort/structure plan to stage, o = a wall section or other
plate, u = unsure), then the stage-B boxes on the plan pages (books.cmd_triage_b runs on A's site
pages + the list's kind-s leaves), then --stage / --check / --golden, and the stage-A/B recall
against the list recorded in the Maclauchlan section of docs/lead_roman.md (books_lists.validate_book,
never the shared validation.json).

The system python3 has no numpy/PIL, so every command runs under .venv/bin/python; the module top
stays stdlib-only (books, books_ia, books_lists import lazily at call time, the fit/src_kip.py
idiom). The LLM replicas serve on 127.0.0.1:8080-8082 (verified 2026-10-13: 8080 and 8081 answer,
8082 down) - books.LLM_URLS' default port list already covers them since 215 re-pointed books.py,
so no in-process patch is needed (the parent's pre-215 note is stale).
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))  # books / books_ia / books_lists import lazily, at call time

KEY = "maclauchlan_roman_wall_1858"
IA = "memoirwrittendu00maclgoog"       # 1858 original: the only source of the staged images
IA_LIST = "memoirwrittendur0000henr"   # 1971 reprint: the hOCR source for the printed plate list
REGION = "Europe"                      # coarse book-level region; a row's region comes from its catalog site
YEAR = 1858                            # the title-page year (the survey ran 1857-59 - see the lead doc)
CITE = ("Henry Maclauchlan, Memoir, Written During a Survey of the Roman Wall: through the Counties of "
        "Northumberland and Durham (printed for private circulation), 1858 (the IA record's 1858; the title "
        "page to be read from the first leaves when the fetch lands - the survey itself ran 1857-59)")
WHY = ("Google scan (memoirwrittendu00maclgoog, the 1858 original): 171 leaves, median 3290x5182 px, djvu.txt "
       "+ djvu.xml only (no hOCR page index) - chosen 2026-10-11 (207) as the source of the staged images. "
       "The 1971 reprint (memoirwrittendur0000henr, 292 leaves, 1625x2697 px, hOCR present) is the OCR source "
       "for the book's printed list only; its lower resolution keeps it out of staging.")

# The shared roman staging files (207a/b/c all append here, rows tagged with their book; 211 consolidates).
FILES_ROMAN = os.path.join(ROOT, "data", "commons", "files_roman.jsonl")
CLASSIFIED_ROMAN = os.path.join(ROOT, "data", "commons", "classified_roman.jsonl")
EXTRAS_ROMAN = os.path.join(ROOT, "data", "catalog", "extras_roman.jsonl")

# The books_lists PLATES format: plate | sub-number | title as printed | page printed in the list | kind.
# The 1858 book's printed list of plates, transcribed from the 1971 reprint's hOCR and verified by eye
# against the original's list-page triage image, set here once transcribed: kind s = a fort/structure
# plan to stage, kind o = a wall section or other plate, kind u = unsure from the title alone.
MACLAUCHLAN_PLATES = None


def now():
    return time.strftime("%Y-%m-%d")


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def register():
    """In-process registration: books.BOOKS gets this book and (once transcribed) its plate list is
    injected into books_lists.PLATES - nothing else is touched, the book really is on IA, so the
    machinery's IA calls (pages, fetch_triage) run unmodified. Idempotent."""
    import books
    books.BOOKS[KEY] = dict(ia=IA, region=REGION, year=YEAR, cite=CITE, why=WHY)
    if MACLAUCHLAN_PLATES is not None:
        import books_lists
        books_lists.PLATES[IA] = MACLAUCHLAN_PLATES


def fetch():
    """All triage-size page images of the 1858 original (books.cmd_fetch, resumable; 171 leaves, run it
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


def djvu_page_texts(ia_id=IA):
    """Per-leaf OCR text of a Google upload from its _djvu.xml (the 1858 original has no hOCR page
    index, so page_texts 404s): one <OBJECT> per page, the leaf number in its usemap
    ('<id>_NNNN.djvu'), the text in the <WORD> elements inside it - the 208 ORL pattern.
    {leafNum: text}; the leaf numbers match the bookreader leafNum convention page_texts uses."""
    import books_ia
    md = books_ia.metadata(ia_id)
    name = next(f["name"] for f in md["files"] if f["name"].endswith("_djvu.xml"))
    xml = books_ia.cached(os.path.join(books_ia.RAW, ia_id, name),
                          f"https://archive.org/download/{ia_id}/{urllib.parse.quote(name)}", binary=False)
    out = {}
    for m in re.finditer(r'<OBJECT[^>]*?usemap="[^"]*_0*(\d+)\.djvu"[^>]*>(.*?)</OBJECT>', xml, re.S):
        words = [html.unescape(w) for w in re.findall(r"<WORD[^>]*>([^<]*)</WORD>", m.group(2))]
        out[int(m.group(1))] = " ".join(words)
    return out


def djvu_cmd(argv):
    """Print the 1858 original's per-leaf djvu.xml text: no args = a one-line-per-leaf digest (length +
    first 80 chars) for the page-count check and to locate the list page; named leaves = their full text
    (the cross-check source against the 1971 reprint's hOCR)."""
    texts = djvu_page_texts(IA)
    if not argv:
        for n in sorted(texts):
            t = " ".join(texts[n].split())
            print(f"n{n} len={len(t)}: {t[:80]}")
        return
    for a in argv:
        n = int(a)
        print(f"--- leaf n{n} ---")
        print(" ".join(texts.get(n, "<missing>").split()))


def list_cmd():
    """Until MACLAUCHLAN_PLATES is transcribed: print the 1971 reprint's hOCR text of its front leaves
    (the printed list of plates lives there; the hOCR pair is downloaded once and cached). Once
    transcribed: run books_lists.cmd_ocrmap over the injected plate list - it writes only the per-book
    lists/<ia>.json + .map.json. The ocrmap's plate->leaf mapping reads the ORIGINAL's per-leaf text
    through the machinery's books_ia.page_texts, which 404s for this djvu-only book, so it is swapped
    in-process to the djvu.xml text (the machinery files stay untouched)."""
    if MACLAUCHLAN_PLATES is None:
        import books_ia
        texts = books_ia.page_texts(IA_LIST)  # downloads + caches the hOCR pair of the reprint
        for leaf in sorted(texts)[:30]:
            print(f"--- reprint leaf {leaf} ---")
            print(texts[leaf][:1200])
        return
    register()
    import books_ia
    orig = books_ia.page_texts

    def page_texts_swapped(ia_id):
        return djvu_page_texts(ia_id) if ia_id == IA else orig(ia_id)

    books_ia.page_texts = page_texts_swapped
    try:
        import books_lists
        books_lists.cmd_ocrmap([KEY])
    finally:
        books_ia.page_texts = orig


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] not in ("--fetch", "--status", "--triage", "--list", "--djvu",
                          "--stage", "--dry", "--check", "--golden"):
        raise SystemExit(__doc__.strip().split("usage:")[1].strip())
    if a and a[0] == "--fetch":
        fetch()
    elif a and a[0] == "--status":
        status()
    elif a and a[0] == "--triage" and len(a) >= 2 and a[1] in "AFB":
        triage(a[1])
    elif a and a[0] == "--list":
        list_cmd()
    elif a and a[0] == "--djvu":
        djvu_cmd(a[1:])
    else:
        raise SystemExit("the stage/check/golden legs are not built yet (see the module docstring)")
