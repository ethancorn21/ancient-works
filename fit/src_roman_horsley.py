"""Horsley, *Britannia Romana, or the Roman Antiquities of Britain* (1732) (task 207a, GOAL point 4):
the book's ~121 engraved plates - mostly Roman inscriptions and sculptures (list kind "o") - and its
few genuine site plans (maps of forts/walls/towns, kind "s"), which are the only rows staged: into the
shared roman staging files (files_roman.jsonl + classified_roman.jsonl, rows tagged with this book's
key; extras_roman.jsonl for new sites only), each with the 200 evidence field (the book's own printed
list names the place) and the book's date (1732). 211 consolidates the *_roman staging into the
canonical index. The book is on IA (Google Books scan britanniaromanao00hors, 936 leaves; BookReader
pages + hOCR verified 2026-10-13, iteration 202), so the standard book machinery runs UNMODIFIED - no
local-copy wrap (the key difference from 209a's Hoare and 207c's Roy): books.cmd_fetch downloads the
triage pages, books.run_stage triages them, and books_lists.cmd_ocrmap maps the list to leaves after
an in-process injection of this module's per-leaf table HORSEY_FIGS (the 213/civitates hand-list
pattern). The book has NO printed list of plates (verified 2026-10-13, iteration 215, on both copies:
the Google hOCR's 942 pages hold no LIST/PLATES heading and the British Museum copy's pages were
searched one by one), so the list = the plates' own printed headings, transcribed by eye from the
full-size page images (books_lists' own fallback: "where the book has none, the plate headings
printed in its text"). Per-book artifacts only: triage/britanniaromanao00hors.*.jsonl,
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
       src_roman_horsley.py --list         offline: register() + books_lists.cmd_ocrmap -> the
                                           per-book lists/<ia>.json (the HORSEY_FIGS table's dump)
                                           + .map.json (24 list leaves, site_plan = true for the 17
                                           kind-s maps) only (the shared validation.json /
                                           index.jsonl are never written)
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

Later legs (built as the book lands, in order): --list (done: the 24-entry table HORSEY_FIGS - the 17
kind-s maps (the 15 wall maps + n0114 P.44 and n0185 P.113, both added 2026-10-14 in 220 after that
session proved 219's dismissal of their stage-A flags wrong) + N.11's wall section and the six
kind-o country maps, each leaf's printed heading, corner mark and kind, transcribed by eye
2026-10-13 in 215/216/218), then the stage-B boxes on the
plan pages (the stage-B leg reuses the unmodified machinery now that the list exists:
books.cmd_triage_b runs on A's site pages + the list's kind-s leaves), then --stage / --check /
--golden, and the stage-A/B recall against the list recorded in the Horsley section of
docs/lead_roman.md (books_lists.validate_book, never the shared validation.json). The ~121
inscription/sculpture plates (Roman numerals I-CXXI) trail as HORSEY_PLATES (kind o, indexed but never
staged) and do not block the 90%-of-site-plans box, which counts only kind-s leaves.

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
CITE = ("John Horsley, Britannia Romana, or the Roman Antiquities of Britain: in three books, printed "
        "for John Osborn and Thomas Longman, at the Ship in Pater-Noster Row, London, 1732 (M.DCC.XXXII); "
        "the Google scan is the British Museum volume (shelf mark RB DA 145. H 86 folio, May 25 1883, "
        "on leaf n0015)")
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

# The per-leaf figure table in books_lists' HAND_FIGS format: fig|title|page|kind|kind_by (one line per
# plate leaf, exactly 4 pipes; fig = the leaf's n; page = the printed corner mark or '' - none; kind
# s = a site-plan map that gets staged, o = indexed but never staged, u = unsure; kind_by hand = read
# from the images). The book has NO printed list of plates (verified on both copies, 215), so the list
# = the plates' own printed headings - transcribed by eye from the full-size page images 2026-10-13
# (215/216/218); stage-A captions on this book are parametric hallucinations and were never used -
# except the page-type flags on n0114 and n0185, which 219 dismissed as parametric hallucinations but
# 220 proved GENUINE (the full-size images + the book's own text pp.43-44 and p.113): the flags were
# right, only the invented captions were not, and both plates are in the table below.
# kind s: the 17 site-plan maps that get staged - the 15 wall maps (Book II's P.158 Hadrian's-wall
# series N.1-N.10 + Book III's P.176 Antonine-wall series N.1-N.5) plus n0114 (P.44: the two
# legionary camps of the Mons Graupius campaign, Innerpeffery and Ardoch) and n0185 (P.113: the five
# secondary stations per lineam valli); kind o: N.11 (a wall cross-section, not a site plan) and the
# six country maps (n0060/n0062 the Ptolemy fold-outs, n0706 the Mercator-Ptolemy, n0734 the
# Antonine-Itinerary map, n0832 the Notitia Dignitatum map, n0867 the Peutinger table) - indexed in
# the list mapping, never staged as picture rows. 219 transcribed 22 entries (15 s); 220 added
# n0114/n0185 (17 s) and swept the whole book's hOCR (every page with text <700 chars listed, plus a
# plan-vocabulary scan of every page): no further kind-s leaf exists, so the 24-entry table is
# complete.
HORSEY_FIGS = """
60|A Corrected Map of Britain according to Ptolemy (front-matter fold-out, faded landscape capture)||o|hand
62|A Corrected Map of Britain according to Ptolemy's, or Rectified (front-matter fold-out, full spread)||o|hand
114|Innerpeffery camp. (top plan) and Ardoch camp. (bottom plan): the two legionary camps of the Mons Graupius campaign per the book's text pp.43-44 ("the legions might poflibly have been at Ardoch, or Innerpeffery, before they marched to the battle"); each with its scale (200 / 300 yards), rivers Ruchel and Knoch, a military way and a Praetorium box|P.44|s|hand
185|The five fecondary ftations per lineam valli: five fort plans, I GLANNIBANTA near Lanchester, II ALIONE now Whitley caftle, III BREMETEN RACUM now Old Penrith, IV OLENACUM now Old Carlisle, V VIROSIDUM near Elenborough; Praetorium boxes on I and III, Watling Street, a compass, "A feale of 100 paces"|P.113|s|hand
236|A general map of the Roman walls in the north of England, and so much of the adjacent countryes as includes the secondary stations per lineam valli.|P.158 N.1|s|hand
238|A map of the Roman walls from SEGEDVNAVM to CONDERCVVM.|P.158 N.2|s|hand
240|A map of the Roman wall, from CONDERCVVM to VINDOBALA.|P.158 N.3|s|hand
242|A map of the Roman wall, from VINDOBALA to HANNAVVM.|P.158 N.4|s|hand
244|A map of the Roman wall, from HANNAVVM to CILVRNVA.|P.158 N.5|s|hand
246|A map of the Roman wall, from CILVRNVA to BORCOVACEVS.|P.158 N.6|s|hand
248|A map of the Roman walls from BORCOVACEVS to MAGNA.|P.158 N.7|s|hand
250|A map of the Roman walls from MAGNA to PETRIANA.|P.158 N.8|s|hand
252|A map of the Roman walls in the north of England, from PETRIANA to CONGAVATA.|P.158 N.9|s|hand
254|A map of the Roman walls in the north of England, from CONGAVATA to TVNNOCELVVM.|P.158 N.10|s|hand
256|A section of both the Roman walls between one castellum and another (the south agger, Severus's ditch and vallum, Hadrian's north agger, ditch, principal vallum and south agger; a scale of 9 paces or 15 yards)|P.158 N.11|o|hand
278|A general map of Antoninus's wall in Scotland.|P.176 N.1|s|hand
280|A map of the Roman wall in Scotland from the west end to Bemulie.|P.176 N.2|s|hand
282|A map of the Roman wall in Scotland from Bemulie to Crowy-hill.|P.176 N.3|s|hand
284|A map of the Roman wall in Scotland from Crowy-hill to Falkirk.|P.176 N.4|s|hand
286|A map of the Roman wall in Scotland from Falkirk to the east end.|P.176 N.5|s|hand
706|BRITAIN according to PTOLEMY, taken from MERCATOR.|P.356|o|hand
734|BRITANNIA ROMANA according to ANTONINE'S ITINERARY.|P.380|o|hand
832|BRITANNIA ROMANA in signia Vicarii Britanniarum (the Notitia Dignitatum map: Maxima Caesariensis, Flavia, etc.)|P.472|o|hand
867|TABVLAE ITINERARIAE ANTIQVAE SEGMENTVM PRIMVM (the Peutinger table, Gaul segment; an "A scale of miles" bar)|Pag.505|o|hand
"""

# The books_lists PLATES format: plate|sub|title|page|kind. The ~121 inscription/sculpture plates
# (Roman numerals I-CXXI, scattered through Book I-III) to be transcribed by eye from each plate's own
# printed heading (the book has no list) as a second table, kind o: indexed in the list mapping, each
# naming the site where the stone was found, but never staged as picture rows. The 90%-of-site-plans box
# concerns only the kind-s maps above, so this trails without blocking.
HORSEY_PLATES = None  # set when transcribed; register() injects it into books_lists.PLATES in-process


def now():
    return time.strftime("%Y-%m-%d")


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def register():
    """In-process registration: books.BOOKS gets this book and the per-leaf figure table is injected
    into books_lists.HAND_FIGS (plus the plate list, once HORSEY_PLATES is transcribed) - nothing else
    is touched, the book really is on IA, so the machinery's IA calls (pages, page_texts,
    fetch_triage) run unmodified. Idempotent."""
    import books
    import books_lists
    books.BOOKS[KEY] = dict(ia=IA, region=REGION, year=YEAR, cite=CITE, why=WHY)
    books_lists.HAND_FIGS[IA] = HORSEY_FIGS
    if HORSEY_PLATES is not None:
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
    """Offline: register() (injects HORSEY_FIGS into books_lists.HAND_FIGS) then
    books_lists.cmd_ocrmap - for a HAND_FIGS book it maps the table by leaf n directly (no OCR, no
    LLM, no network beyond the cached bookreader.json) and writes only the per-book lists/<ia>.json
    (the table's dump) + .map.json (the map stays [] until stage A exists, as cmd_ocrmap guards)."""
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
