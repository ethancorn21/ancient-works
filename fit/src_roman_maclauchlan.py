"""Maclauchlan, *Memoir, Written During a Survey of the Roman Wall* (1858) (task 207b, GOAL point 4):
a privately-circulated survey of the eastern branch of Hadrian's Wall - the book's plates are detailed
plans of the forts on the wall (Vindolanda, Vercovicium, the milecastles, ...) alongside wall
cross-sections and stretches of the wall itself. Only the site-plan plates of a NAMED fort/structure
with a location are staged: into the shared roman staging files (files_roman.jsonl +
classified_roman.jsonl, rows tagged with this book's key; extras_roman.jsonl for new sites only), each
with the 200 evidence field (the book's own list names the place) and the book's date (the title
page's imprint MDCCCLVIII = 1858; the title page itself dates the survey 1852-1854, NOT the 1857-59 the
parent's task file guessed - the 1858 printing also carries later work, the Willow Holm section taken
Sep't 7th 1858 and the Carlisle great-sewer plan - the discrepancy is recorded in docs/lead_roman.md).
Wall sections alone are NOT sites (207 Notes). 211 consolidates the *_roman staging into the canonical
index.

The book is on IA, but in ONE copy only: memoirwrittendu00maclgoog (the 1858 original, Google scan,
171 leaves, median 3290x5182 px; djvu.txt + djvu.xml only, NO hOCR page index - per-leaf OCR comes
from the djvu.xml OBJECTs instead, the 208 pattern; the djvu.xml's page numbers are leafNums = n+1,
aligned 1:1 with the bookreader leaves here). The other IA copies are unusable (PITFALLS, verified
2026-10-13/14):
  memoirwrittendur0000henr  the "1971 reprint" candidate is a MISLABELED item - its pages are Linda
                             Nochlin's *Realism* (IA re-scan mix-up, re-scanned 2024-01-31): never an
                             OCR source for this book.
  henrymaclauchlan0000macl  the 2015 Wanney presentation, lending-restricted (LCP/ACS) - not readable
                             from this machine; an optional cross-check only.
So: fetch/triage/stage images from the 1858 original, and read the book's text from the djvu.xml.

The book has NO printed list of plates (a privately-circulated original: no LIST / PLATES heading
anywhere in the front or back matter). Its only list is the DIRECTIONS TO THE BINDER (djvu leaf 119),
verbatim (filed in PITFALLS): "The Plans, Fig. 1, 2, 3, and 6, showing the Mote, Brampton, &c., to be
inserted at page 65. The Plans, &c. of the Roman Wall in Willow Holm, at page 76. The Plans, Fig. 4,
6, Carlisle and the Camp on Skew Hill at page 76." So, per books_lists' own fallback ("where the book
has none, the plate headings printed in its text"), the ground truth is the per-leaf hand table
MACLAUCHLAN_FIGS below: each plate/figure leaf's own printed heading/caption, transcribed by eye
(iterations 122/123/130) from the triage images + the djvu.xml text - the three small-format plate
leaves (n0078 Fig. 1 Brampton, n0090 Willow Holm, n0093 Fig. 4 Carlisle) and three text pages carrying
inline figures (n0111 the 1856 gateway near Housesteads, n0115 the Table of Stations, n0129 the
Binchester tile marks). Figs 2, 3 and 5/6 (the Mote, &c., the Camp on Skew Hill) were NEVER printed in
this copy (the 122 size census leaves no room for hidden plates) and do not count against the 90% box.
Fig. 1 and the gateway figure are BLANK in this copy (the drawing faded; only frame, labels and the
scale bar survive) - the legible n0093 plan of Carlisle is the only site plan that gets a staged row;
the two blanks are accounted for individually in the Maclauchlan section of docs/lead_roman.md (the
box's disjunct).

usage: src_roman_maclauchlan.py --fetch         live: triage-size page images of the 1858 original,
                                           all 171 (books.cmd_fetch, resumable; run it in the
                                           background: nohup .venv/bin/python
                                           fit/src_roman_maclauchlan.py --fetch; check with --status)
       src_roman_maclauchlan.py --status        offline: leaf count + triage progress from the cached
                                           bookreader.json, the triage stage line counts, and which
                                           LLM ports answer
       src_roman_maclauchlan.py --triage A|F|B  live (Qwen replicas on 127.0.0.1:8080-8082): the triage
                                           stages through books.cmd_triage_* unmodified (append-only,
                                           resumable)
       src_roman_maclauchlan.py --list         OFFLINE: register() (injects MACLAUCHLAN_FIGS into
                                           books_lists.HAND_FIGS) + books_lists.cmd_ocrmap -> the
                                           per-book lists/memoirwrittendu00maclgoog.json (the table's
                                           dump, ensure_ascii=False) + .map.json (the six list leaves,
                                           site_plan = true for the three kind-s leaves) only (the
                                           shared validation.json / index.jsonl are never written; the
                                           stage-A/B recall goes to the Maclauchlan section of
                                           docs/lead_roman.md via books_lists.validate_book)
       src_roman_maclauchlan.py --djvu [n ...]  live once: download the 1858 original's _djvu.xml
                                           (cached) and print its per-leaf OCR text - all leaves as a
                                           page-count digest, or the named leaves (leafNums, n+1:
                                           12 = n0011 the full title page) for reading the book
       src_roman_maclauchlan.py [--stage]      OFFLINE (no LLM, no network): append the book's one
       [--dry]                                legible site-plan row (n0093, Fig. 4, the plan of
                                           Carlisle - the other kind-s leaves are blank in this copy
                                           or are not sites: the Maclauchlan section of
                                           docs/lead_roman.md) to files_roman.jsonl +
                                           classified_roman.jsonl ("plan" by hand), and its new site
                                           (Luguvallium Q71551754) to extras_roman.jsonl (creating
                                           each if absent); append-only, idempotent on (site, title)
                                           and site id, rows tagged with this book's module; --dry
                                           previews
       src_roman_maclauchlan.py --check        (not built yet) offline (no network): join the staged
                                           roman rows and run fit/evidence.py's check over this book's
                                           rows
       src_roman_maclauchlan.py --golden       (not built yet) write tests/golden/src_roman_maclauchlan_sample.json

The system python3 has no numpy/PIL, so every command runs under .venv/bin/python; the module top
stays stdlib-only (books, books_ia, books_lists import lazily at call time, the fit/src_kip.py
idiom). The LLM replicas serve on 127.0.0.1:8080-8082 (verified 2026-10-14: 8080 and 8081 answer,
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
IA = "memoirwrittendu00maclgoog"       # 1858 original: the only readable IA copy; the sole source of staged images
REGION = "Europe"                      # coarse book-level region; a row's region comes from its catalog site
YEAR = 1858                            # the title page's own imprint MDCCCLVIII (n0011); the survey years it prints are 1852-1854
CITE = ("Henry Maclauchlan, Memoir, Written During a Survey of the Roman Wall, through the Counties of "
        "Northumberland and Cumberland, in the Years 1852-1854, made by direction of His Grace the Duke "
        "of Northumberland, K.G., Patron of the Society of Antiquaries of Newcastle-upon-Tyne; London, "
        "printed for private circulation (Bradbury and Evans, Whitefriars), MDCCCLVIII = 1858 (title "
        "page n0011; the preface dates the survey Wallsend summer 1852 to Bowness by winter 1854, and "
        "the 1858 printing carries later work - the Willow Holm section of Sep't 7th 1858, the Carlisle "
        "great-sewer plan)")
WHY = ("Google scan (memoirwrittendu00maclgoog, the 1858 original): 171 leaves, median 3290x5182 px, "
       "djvu.txt + djvu.xml only (no hOCR page index) - the only readable IA copy, chosen 2026-10-11 "
       "(207). The '1971 reprint' candidate (memoirwrittendur0000henr) is a mislabeled item (Linda "
       "Nochlin, Realism - PITFALLS), and the 2015 Wanney presentation (henrymaclauchlan0000macl) is "
       "lending-restricted, so all reading goes to the original's djvu.xml text and its triage images.")

# The shared roman staging files (207a/b/c all append here, rows tagged with their book; 211 consolidates).
FILES_ROMAN = os.path.join(ROOT, "data", "commons", "files_roman.jsonl")
CLASSIFIED_ROMAN = os.path.join(ROOT, "data", "commons", "classified_roman.jsonl")
EXTRAS_ROMAN = os.path.join(ROOT, "data", "catalog", "extras_roman.jsonl")

# The per-leaf figure table in books_lists' HAND_FIGS format: fig|title|page|kind|kind_by (one line per
# plate/figure leaf, exactly 4 pipes; fig = the leaf's n; page = the printed page the binder's list
# inserts the plate at (the quarto text pages' own printed page for the inline figures); kind
# s = a site plan of a named place to be staged, o = indexed but never staged (a wall section, a
# printed table, an artifact figure), u = unsure; kind_by hand = read from the images). The book has
# NO printed plate list (the binder's instructions on djvu leaf 119 are the book's only list - the
# module docstring), so this table IS the list: every plate/figure leaf's own printed
# heading/caption, transcribed by eye (122/123/130). kind s: the three plans of named places - n0078
# the Brampton camp (the doubtful position of Aballava), n0093 the Carlisle plan (the Wall and Vallum
# course through the town with the 1857-58 great sewer), n0111 the 1856 gateway near Housesteads - of
# which ONLY n0093 survives legible in this copy (n0078/n0111 blank, the drawing faded); kind o:
# n0090 the Willow Holm wall plan/section/elevation (a wall section - not a site, 207 Notes), n0115
# the printed Table of Stations, n0129 the Binchester tile-mark figure. Figs 2, 3, 5/6 were never
# printed in this copy.
MACLAUCHLAN_FIGS = """
78|FIG. 1. BRAMPTO. (plan of the Brampton camp, the doubtful position of Aballava, discussed pp.64-65; blank in this copy - frame, compass, labels and scale bar survive)|65|s|hand
90|Plan, Section, and Elevation of the Roman Wall, in Willow Holm, Carlisle (440 yards from the west mouth of the sewer; scale 4 feet to an inch; reduced from M'Me Kie's section, taken Sep't 7th 1858)|76|o|hand
93|FIG. 4. CARLISLE, COURSE OF THE WALL AND OF THE YALLUM. (plan of Carlisle: the course of the Wall and the Vallum between Stanwix and the Castle, with the 1857-58 great sewer and its drain; 'From Burgh / Trinity Church' and 'From WIGTON' direction notes, compass, scale of chains and scale of feet; 'H M^L delin', 'Sandridge & Co. Litho London')|76|s|hand
111|GATEWAY RECENTLY DISCOVERED NEAR HOUSESTEADS. (inline figure on printed p.93: the gateway of 1856 near the station of Borcovicus in the Knag Burn valley; caption 'Gateway discovered near Housesteads (Borcovicus) in 1856.'; blank in this copy - faint frame only)|93|s|hand
115|TABLE OF STATIONS. (printed p.97: the stations of the Notitia, the Ravenna and the Chorographus, with their distances)|97|o|hand
129|MARKS ON ROMAN TILES, BINCHESTER. (inline figure on p.7 of the Watling Street memoir: two boxed letter-marks from Roman tiles with a 6-inches bar)|7|o|hand
"""


def now():
    return time.strftime("%Y-%m-%d")


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def register():
    """In-process registration: books.BOOKS gets this book and the per-leaf figure table is injected
    into books_lists.HAND_FIGS - nothing else is touched, the book really is on IA, so the machinery's
    IA calls (pages, fetch_triage) run unmodified. Idempotent."""
    import books
    import books_lists
    books.BOOKS[KEY] = dict(ia=IA, region=REGION, year=YEAR, cite=CITE, why=WHY)
    books_lists.HAND_FIGS[IA] = MACLAUCHLAN_FIGS


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
    ('<id>_NNNN.djvu'), the text in the <WORD> elements inside it - the 208 ORL pattern. The
    extracted numbers are leafNums (= the bookreader's n + 1; the djvu leaves align 1:1 with the
    bookreader leaves in this book). {leafNum: text}."""
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
    first 80 chars) for the page-count check and to locate list-like pages; named leafNums (= n+1) =
    their full text (the reading source for the book, since the item has no hOCR page index)."""
    texts = djvu_page_texts(IA)
    if not argv:
        for n in sorted(texts):
            t = " ".join(texts[n].split())
            print(f"n{n} len={len(t)}: {t[:80]}")
        return
    for a in argv:
        n = int(a)
        print(f"--- leafNum n{n} ---")
        print(" ".join(texts.get(n, "<missing>").split()))


# ---------------------------------------------------------------- staging (box 3, the 130 decisions)

# The one legible site plan (n0093, Fig. 4, the plan of Carlisle) stages to a NEW site: the book's
# supposed Roman station sits on the castle ground, where the plan's Wall and Vallum meet (pp.76-77),
# so the site is the fort's own item Q71551754 "Luguvallium Legionary Fort - Carlisle" (P31 Q57821
# fortification -> kind "roman fort", P131 Q192896, VICI 12444, P625 precision 1e-6), NOT Carlisle
# Castle (Q614836, kind castle) - DECISIONS 207b 130. The evidence's named place is "Carlisle" (the
# binder's list names it; the title and desc carry it), resolved to the city's item Q192896 P625.
SITE_NAME = "Luguvallium (Carlisle)"
SITE_QID = "Q71551754"
SITE_LON, SITE_LAT = -2.94077, 54.896187              # the item's P625 (verified 2026-10-14)
PLACE_QID = "Q192896"                                 # the city of Carlisle (the item's P131)
PLACE_LON, PLACE_LAT = -2.936388889, 54.894722222     # the city's P625 (verified 2026-10-14)
FILE_TITLE = "FIG. 4. CARLISLE, COURSE OF THE WALL AND OF THE YALLUM."  # the plate's own printed heading
FILE_NAME = ("Carlisle, plan of the course of the Wall and of the Vallum between Stanwix and the Castle, "
             "with the 1857-58 great sewer, Maclauchlan (1858)")
FILE_DESC = ("Maclauchlan, Memoir, Written During a Survey of the Roman Wall (1858), Fig. 4: the binder's "
             "directions (djvu leaf 119) say 'The Plans, Fig. 4, 6, Carlisle and the Camp on Skew Hill at "
             "page 76.'; the running head on p.77 is 'CARLISLE, COURSE OF THE WALL AND OF THE YALLUM.' "
             "(See Plans, Fig. 4.). Plan of Carlisle: the course of the Wall and the Vallum between "
             "Stanwix and the Castle, with the 1857-58 great sewer and its drain; 'H M^L delin', "
             "Sandridge & Co. Litho London. The only site plan still legible in this copy (n0078 and "
             "n0111 are blank here - docs/lead_roman.md). Internet Archive memoirwrittendu00maclgoog, "
             "leaf n0093 of the 171-leaf 1858 original.")


def stage(dry=False):
    """OFFLINE (no LLM, no network): append the book's one legible site-plan row to the shared roman
    staging files - n0093, Fig. 4, the plan of Carlisle (n0078/n0111 are blank in this copy,
    n0090/n0115/n0129 are not sites: the per-leaf verdicts are in the Maclauchlan section of
    docs/lead_roman.md) - as (a) the new site row (Luguvallium Q71551754) to extras_roman.jsonl,
    (b) the picture row to files_roman.jsonl (the 200 evidence field: kind caption_coords, the named
    place "Carlisle" from the binder's list resolving to the city's P625, 324 m from the fort point;
    fit/evidence.py check_caption re-verifies it from stored fields only), and (c) its hand "plan"
    classified row to classified_roman.jsonl. Append-only and idempotent on (site, title) and site id
    (a second run changes no byte); --dry prints the rows instead of writing them. The row's w/h
    comes from the committed stage-B row (data/books/triage/<ia>.B.jsonl); the url/thumb is the stable
    /download/ page image. 211 consolidates the *_roman files into the canonical ones."""
    import catalog   # the site-id slug rule lives in one place (pipeline/catalog.py, the sources.py rule)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import evidence  # hav_m: the stored dist_m must reproduce under check_caption (fit/evidence.py)

    b = {r["n"]: r for r in _load(os.path.join(ROOT, "data", "books", "triage", f"{IA}.B.jsonl"))}
    row = b.get(93)
    if not row or row.get("parse") != "ok" or not row.get("out", {}).get("plans"):
        raise SystemExit(f"the n0093 stage-B row is missing or unreadable ({IA}.B.jsonl) - run --triage B first")
    w, h = row["img_size"]
    dist = round(evidence.hav_m(SITE_LON, SITE_LAT, PLACE_LON, PLACE_LAT), 1)

    site = {"id": catalog.slug("Luguvallium") + "-" + SITE_QID.lower(), "qid": SITE_QID,
            "name": SITE_NAME, "lon": SITE_LON, "lat": SITE_LAT, "region": "england",
            "kind": "roman fort", "aerial_ok": True, "place": "Carlisle, Cumberland, England",
            "location_check": {"status": "confirmed",
                               "method": "Wikidata P625 (precision 1e-6) cross-checked against the plate and the city of Carlisle (Q192896)",
                               "note": (f"the item's P625 sits on the castle ground, where the book's supposed "
                                         f"station stands (pp.76-77) and the plan's Wall and Vallum meet; {dist:.0f} m "
                                         "from the city's P625 point; VICI 12444; the item has no enwiki article "
                                         "(sitelinks checked 2026-10-14)"),
                               "checked": now()},
            "source": "fit/src_roman_maclauchlan.py",
            "note": ("new site staged by 207b (Maclauchlan 1858, Fig. 4, leaf n0093): the fort's own item, "
                     "not Carlisle Castle (Q614836) - DECISIONS 207b 130")}
    url = f"https://archive.org/download/{IA}/page/n0093.jpg"
    f = {"site": site["id"], "qid": SITE_QID, "title": FILE_TITLE, "year": YEAR, "wd_plan": False,
         "cat": None, "name": FILE_NAME, "by": "fit/src_roman_maclauchlan.py", "url": url, "thumb": url,
         "w": w, "h": h, "mime": "image/jpeg", "date": "1858", "desc": FILE_DESC,
         "artist": "Henry Maclauchlan", "license": "public domain (IA: NOT_IN_COPYRIGHT, the 1858 original)",
         "page": f"https://archive.org/details/{IA}",
         "evidence": {"rec": "evidence/1", "kind": "caption_coords", "checked": now(),
                      "named_place": "Carlisle", "place_qid": PLACE_QID, "place_label": "Carlisle",
                      "place_lon": PLACE_LON, "place_lat": PLACE_LAT,
                      "site_lon": SITE_LON, "site_lat": SITE_LAT, "dist_m": dist}}
    c = {"site": site["id"], "title": FILE_TITLE, "p_plan": 1.0, "p_birdseye": 0.0, "p_photo": 0.0,
         "by": "hand"}

    have_site = {r.get("id") for r in _load(EXTRAS_ROMAN)}
    have_file = {(r.get("site"), r.get("title")) for r in _load(FILES_ROMAN)}
    have_cls = {(r.get("site"), r.get("title")) for r in _load(CLASSIFIED_ROMAN)}
    print(f"staged: new site {site['id']} (Q{SITE_QID[1:]}, dist {dist} m), picture {FILE_TITLE!r}")
    for path, r, present in ((EXTRAS_ROMAN, site, site["id"] in have_site),
                             (FILES_ROMAN, f, (f["site"], f["title"]) in have_file),
                             (CLASSIFIED_ROMAN, c, (c["site"], c["title"]) in have_cls)):
        tag = os.path.basename(path)
        if present:
            print(f"   {tag}: row already present (skipped, nothing written)")
        elif dry:
            print(f"   {tag}: would append {json.dumps(r, ensure_ascii=False)}")
        else:
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"   {tag}: appended 1 row")


def list_cmd():
    """Offline: register() (injects MACLAUCHLAN_FIGS into books_lists.HAND_FIGS) then
    books_lists.cmd_ocrmap - for a HAND_FIGS book it maps the table by leaf n directly (no OCR, no
    LLM, no network beyond the cached files) and writes only the per-book lists/<ia>.json (the
    table's dump, ensure_ascii=False) + .map.json (the six list leaves, site_plan = true for the
    three kind-s leaves). The book's only list is the binder's instructions (the module docstring),
    so there is no OCR list to map: the table IS the list."""
    register()
    import books_lists
    books_lists.cmd_ocrmap([KEY])


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
    elif a and a[0] in ("--stage", "--dry"):
        stage("--dry" in a)
    else:
        raise SystemExit("the check/golden legs are not built yet (see the module docstring)")
