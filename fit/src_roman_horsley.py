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
       src_roman_horsley.py [--stage]      OFFLINE (no LLM, no network): stage the book's 17 verified
       [--dry]                             kind-s (site-plan) rows (the 24-entry list's 17 kind-s leaves:
                                           the 15 wall maps + n0114 P.44 + n0185 P.113) into
                                           files_roman.jsonl + classified_roman.jsonl (+
                                           extras_roman.jsonl for the 8 new no-QID sites): append-only,
                                           idempotent (a second run changes no byte), 200 evidence field
                                           per row (the printed list entry is the tie), 1732 on every row;
                                           --dry previews
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
EXTRAS_CANON = os.path.join(ROOT, "data", "catalog", "extras.jsonl")   # the canonical extras: the reuse source (bar-hill-fort, rough-castle-fort)
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
MODULE = "fit/src_roman_horsley.py"   # the by/source tag every staged row of this book carries (207b's landed convention)
LICENSE = "public domain (the 1732 original, pre-copyright era)"   # the book's IA metadata has no license flag (checked 2026-10-14, live + cached)

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


# ---------------------------------------------------------------- staging (box 2/3/4, the 808 decisions)

# The 17 verified kind-s leaves staged into the shared roman files: one row per leaf, in leaf order.
# title = the plate's printed heading (the 24-entry list's entry for the leaf; n0114/n0185 the short
# form of it) - the 200 evidence's named place; name = a short descriptive name; desc = the plate's
# subject + the other forts named on it (the stage-B site_names) + the tie decision (DECISIONS 808
# 147/149). tie = the site the row names: a catalog site id (looked up at run time in sites.jsonl;
# luguvallium in extras_roman.jsonl), a reused extras.jsonl id (bar-hill-fort, rough-castle-fort),
# or a NEW_SITES key below. Multi-fort maps tie to the most-named/planned fort (216's design), the
# others recorded in desc.
STAGE_ROWS = [
    (114, "ardoch",
     "Innerpeffery camp. and Ardoch camp.",
     "The legionary camps of Ardoch and Innerpeffery, two plans, Horsley (1732), P.44",
     "Horsley, Britannia Romana (1732), P.44 (leaf n0114): the two legionary camps of the Mons "
     "Graupius campaign per the book's text pp.43-44 ('the legions might poflibly have been at "
     "Ardoch, or Innerpeffery, before they marched to the battle'): Ardoch camp (the lower plan, "
     "concentric with a Praetorium box, the Knoch river on its west and the Ruchel to its north) and "
     "the Innerpeffery camp (the upper plan, a single circuit with a military way and 'a bank by "
     "which the river has formerly run'; each plan with its 200-yard scale). The Ardoch row is the "
     "Braco camp (Q4788225, Gask Ridge - DECISIONS 808 148); the Innerpeffery camp is recorded here "
     "on this row (the 808 box: no row of its own). Internet Archive britanniaromanao00hors, leaf "
     "n0114 of the 936-leaf Google scan (British Museum volume)."),
    (185, "virosidum",
     "The five fecondary ftations per lineam valli",
     "The five secondary stations per lineam valli, five fort plans, Horsley (1732), P.113",
     "Horsley, Britannia Romana (1732), P.113 (leaf n0185): five fort plans - I GLANNIBANTA "
     "(Lanchester), II ALIONE (Whitley castle), III BREMETEN RACUM (Old Penrith), IV OLENACUM (Old "
     "Carlisle), V VIROSIDUM (near Elenborough), with Praetorium boxes on I and III, Watling Street, "
     "a compass and 'A feale of 100 paces'. I-IV have catalog rows (longovicium-q6674222, "
     "whitley-castle-q7996561, voreda-roman-fort-q17642742, luguvallium-q71551754); the row ties to "
     "V VIROSIDUM, the only one of the five without a catalog row, as the plate's new no-QID 'roman "
     "fort' row - all five plans are equal, so no other ranking (DECISIONS 808 147 item 4). "
     "Internet Archive britanniaromanao00hors, leaf n0185 of the 936-leaf Google scan (British "
     "Museum volume)."),
    (236, "castrum-segedunum-q637958",
     "A general map of the Roman walls in the north of England, and so much of the adjacent countryes as includes the secondary stations per lineam valli.",
     "Hadrian's Wall, general map of the whole secondary-station line, Horsley (1732), N.1",
     "Horsley, Britannia Romana (1732), P.158 N.1 (leaf n0236): a general map of the Roman walls in "
     "the north of England and so much of the adjacent countryes as includes the secondary stations "
     "per lineam valli: the whole line from Segedunum (SEGEDYNVM) to Tunnocelum (TIVN NOCELVM), every "
     "station labelled (B's read: PONSAELII, CONDERCVVM, VINDOBALA, HYNVNVM, CILVRNVM, BORCOVICVS, "
     "PROCOLITIA, MAGNA, PETRIANA, AESTICA, VINDOLANA, ALIONE, GLANNIBANTA, BREMENIVM, BREMETERACVM, "
     "BROCAVVM, BRONONACAE, BLATVM VVLGIVM, CASTRA EXPLORATORVM, CORSTOPITVM, GALLAVA, HABITANCVM, "
     "VINDOMORA, ABALLABA, AMBBOGLANNA, CONGAVATA, AXELODYNYVM, LVGVAVALLIVM, OLENACVM, VIROSIDVM, "
     "GABROSENTVM; a scale of ten miles) - no inset fort plans: the map itself is the series' "
     "subject, so the row ties to the wall's east end, Segedunum (DECISIONS 808 147 item 6). "
     "Internet Archive britanniaromanao00hors, leaf n0236 of the 936-leaf Google scan (British "
     "Museum volume)."),
    (238, "castrum-segedunum-q637958",
     "A map of the Roman walls from SEGEDVNAVM to CONDERCVVM.",
     "Hadrian's Wall, map from Segedunum to Condercum, Horsley (1732), N.2",
     "Horsley, Britannia Romana (1732), P.158 N.2 (leaf n0238): the wall from Segedunum to Condercum, "
     "with Pons Aelius (PONSAELIVM) between them (216's full-size reading; B's names: Severus's "
     "wall, Hadrian's stallum and the Roman way, a scale of two miles). Tied to Segedunum, the "
     "title's first station. Internet Archive britanniaromanao00hors, leaf n0238 of the 936-leaf "
     "Google scan (British Museum volume)."),
    (240, "rudchester-roman-fort-associated-civil-s-q17669775",
     "A map of the Roman wall, from CONDERCVVM to VINDOBALA.",
     "Hadrian's Wall, map from Condercum to Vindobala (Rudchester), Horsley (1732), N.3",
     "Horsley, Britannia Romana (1732), P.158 N.3 (leaf n0240): the wall from Condercum ('now Benwel "
     "hill') to Vindobala ('now Rutchester'), with both forts' inset plans, the Tine river, Severic's "
     "wall and vallum and Hedrican's wall and vallum. Tied to the Vindobala plan (the catalog's "
     "Q17669775 row). Internet Archive britanniaromanao00hors, leaf n0240 of the 936-leaf Google "
     "scan (British Museum volume)."),
    (242, "haltonchesters-roman-fort-settlement-and-q17648018",
     "A map of the Roman wall, from VINDOBALA to HANNAVVM.",
     "Hadrian's Wall, map from Vindobala to Hannavum (Haltonchesters), Horsley (1732), N.4",
     "Horsley, Britannia Romana (1732), P.158 N.4 (leaf n0242): the wall from Vindobala to Hannavum "
     "('now Halton Cheisters'), with the Hannavum plan, two oval camp/fort plans, the Tine river, "
     "Halden Lough, and Severus's wall and Hadrian's vallum. Tied to the Hannavum plan (the catalog's "
     "Q17648018 row). Internet Archive britanniaromanao00hors, leaf n0242 of the 936-leaf Google "
     "scan (British Museum volume)."),
    (244, "cilurni",
     "A map of the Roman wall, from HANNAVVM to CILVRNVA.",
     "Hadrian's Wall, map from Hannavum to Cilurni (Chesters), Horsley (1732), N.5",
     "Horsley, Britannia Romana (1732), P.158 N.5 (leaf n0244): the wall from Hannavum to Cilurni "
     "('now West Chesters'), with the Cilurni plan, Onnum (HVNNVM), Corbridge, the Tine river, the "
     "Hadrian's vallum, the military way and the modern places (Aldon gate, Hollerton, Hulton, "
     "Whittingtons, ...). Tied to the new no-QID cilurni row (the catalog's Q17650519 row sits ~300 m "
     "away; the row stays no-QID per the 808 box's tie list - DECISIONS 808 147/149). Internet "
     "Archive britanniaromanao00hors, leaf n0244 of the 936-leaf Google scan (British Museum "
     "volume)."),
    (246, "birdoswald-roman-fort-and-the-section-of-q17650767",
     "A map of the Roman wall, from CILVRNVA to BORCOVACEVS.",
     "Hadrian's Wall, map from Cilurni to Borcovaceus (Birdoswald), Horsley (1732), N.6",
     "Horsley, Britannia Romana (1732), P.158 N.6 (leaf n0246): the wall from Cilurni to Borcovaceus "
     "(Birdoswald), with the Borcovaceus plan, Procolitia (Carvoran), Cilurni again, the military "
     "way, Severus's wall and Hadrian's wall and vallum. Tied to the Borcovaceus plan (the catalog's "
     "Q17650767 row). Internet Archive britanniaromanao00hors, leaf n0246 of the 936-leaf Google "
     "scan (British Museum volume)."),
    (248, "aesica-q4688554",
     "A map of the Roman walls from BORCOVACEVS to MAGNA.",
     "Hadrian's Wall, map from Borcovaceus to Magna with inset fort plans, Horsley (1732), N.7",
     "Horsley, Britannia Romana (1732), P.158 N.7 (leaf n0248): the wall from Borcovaceus to Magna, "
     "with three inset fort plans on a 100-yard scale - Magna, Vindolana and Aesica. Tied to the "
     "Aesica plan (the box's explicit tie; the catalog's Q4688554 row). Internet Archive "
     "britanniaromanao00hors, leaf n0248 of the 936-leaf Google scan (British Museum volume)."),
    (250, "petriana",
     "A map of the Roman walls from MAGNA to PETRIANA.",
     "Hadrian's Wall, map from Magna to Petriana with inset fort plans, Horsley (1732), N.8",
     "Horsley, Britannia Romana (1732), P.158 N.8 (leaf n0250): the wall from Magna to Petriana, "
     "with two inset fort plans (PETRIANA, AMBOGLANNA). PETRIANA here is Horsley's HYPOTHETICAL "
     "station on the Cumberland coast (between Longhope and the Cark), not the real Petriana = "
     "Rudchester (the VINDOBALA-tied catalog row); the inset plan is a schematic. Tied to the new "
     "no-QID petriana row. Internet Archive britanniaromanao00hors, leaf n0250 of the 936-leaf "
     "Google scan (British Museum volume)."),
    (252, "congavata",
     "A map of the Roman walls in the north of England, from PETRIANA to CONGAVATA.",
     "Hadrian's Wall, map from Petriana to Congavata (Castlesteads), Horsley (1732), N.9",
     "Horsley, Britannia Romana (1732), P.158 N.9 (leaf n0252): the wall from Petriana to Congavata "
     "(Castlesteads), with the Congavata plan, Aballaba, and the Cauda (Peterel), Eden, Irlthing and "
     "Gelt rivers. Tied to the new no-QID congavata row (the catalog's Q17650705 row sits ~200 m "
     "away; the row stays no-QID - DECISIONS 808 149). Internet Archive britanniaromanao00hors, "
     "leaf n0252 of the 936-leaf Google scan (British Museum volume)."),
    (254, "tunnocelum",
     "A map of the Roman walls in the north of England, from CONGAVATA to TVNNOCELVVM.",
     "Hadrian's Wall, map from Congavata to Tunnocelum (Solway fold-out), Horsley (1732), N.10",
     "Horsley, Britannia Romana (1732), P.158 N.10 (leaf n0254): a two-landscape-page fold-out of "
     "the wall from Congavata to Tunnocelum: the west part shows CONGAVATA 'now Stanwicks' at the "
     "Eden mouth (Grinfdale, Stenton, Etterby), the east part shows TVNNOCEIVM 'now Boulneis' by "
     "Braken ridge on the Solway shore north of the Esk estuary (ITVNNAE AESTVARIVM; the Esk mouth "
     "with Ronciff at the SW of the map), with Gabrosentum, Drumbrugh, Axelodunum, Brugh, the Solway "
     "Frith, and Hadrian's and Severus's vallums. Tied to the new no-QID tunnocelum row, which "
     "follows the plate's Boulneis placement (DECISIONS 808 149). Internet Archive "
     "britanniaromanao00hors, leaf n0254 of the 936-leaf Google scan (British Museum volume)."),
    (278, "bar-hill-fort",
     "A general map of Antoninus's wall in Scotland.",
     "Antonine Wall, general map of the wall in Scotland, Horsley (1732), N.1",
     "Horsley, Britannia Romana (1732), P.176 N.1 (leaf n0278): a general map of Antoninus's wall in "
     "Scotland: the whole wall line from the west end to Falkirk, with the forts and camps named "
     "(B's read: New Kirkpatrick, Old Kirkpatrick, Duntocher, Castle-hill, Bemulie, Kirkintilloch, "
     "Auchindavy, Barhill, Crowyhill, Wellerwood, Castle-cary, Rough-castle, Camelon, Falkirk, "
     "Mumrills, Caer-niden, Abercorn, Alaterva, Glasgow, Hamilton, Edinburgh, Leviston, Lindthgow, "
     "Reafew, the Calder, Alordur, Gartnavan, Dangoin hill; a scale of ten miles). Tied to the "
     "wall's west end, Bar Hill (the reused bar-hill-fort row - DECISIONS 808 147 item 6). Internet "
     "Archive britanniaromanao00hors, leaf n0278 of the 936-leaf Google scan (British Museum "
     "volume)."),
    (280, "bar-hill-fort",
     "A map of the Roman wall in Scotland from the west end to Bemulie.",
     "Antonine Wall, map from the west end to Bemulie, Horsley (1732), N.2",
     "Horsley, Britannia Romana (1732), P.176 N.2 (leaf n0280): the wall from the west end to "
     "Bemulie, with three inset fort plans - New Kirkpatrick fort (the west end), Cattle-hill fort "
     "and Duntocher fort - the Clyde, Duntocher water, Bemulie and Old Kirkpatrick; a scale of two "
     "English miles. Tied to the wall's west end, Bar Hill (the reused bar-hill-fort row - "
     "DECISIONS 808 147 item 6). Internet Archive britanniaromanao00hors, leaf n0280 of the 936-leaf "
     "Google scan (British Museum volume)."),
    (282, "kirkintilloch",
     "A map of the Roman wall in Scotland from Bemulie to Crowy-hill.",
     "Antonine Wall, map from Bemulie to Crowy-hill with fort plans, Horsley (1732), N.3",
     "Horsley, Britannia Romana (1732), P.176 N.3 (leaf n0282): the wall from Bemulie to Crowy-hill, "
     "with four inset fort plans - the Peel of Kirkintilloch (concentric), Bemulie fort, Barhull "
     "fort and Auchindavy fort. Tied to the new no-QID kirkintilloch row - the most-planned fort on "
     "the plate. Internet Archive britanniaromanao00hors, leaf n0282 of the 936-leaf Google scan "
     "(British Museum volume)."),
    (284, "rough-castle-fort",
     "A map of the Roman wall in Scotland from Crowy-hill to Falkirk.",
     "Antonine Wall, map from Crowy-hill to Falkirk with fort plans, Horsley (1732), N.4",
     "Horsley, Britannia Romana (1732), P.176 N.4 (leaf n0284): the wall from Crowy-hill to "
     "Falkirk, with three inset fort plans - Cattle-cary fort, Rounthall fort and Welterwood fort. "
     "'Rough castle fort' is labelled twice on the plate = most named; 216's 'Falkirk fort plan' "
     "reading was a misread (no Falkirk plan, only the town label). Tied to the reused "
     "rough-castle-fort row. Internet Archive britanniaromanao00hors, leaf n0284 of the 936-leaf "
     "Google scan (British Museum volume)."),
    (286, "carriden",
     "A map of the Roman wall in Scotland from Falkirk to the east end.",
     "Antonine Wall, map from Falkirk to the east end (Carriden), Horsley (1732), N.5",
     "Horsley, Britannia Romana (1732), P.176 N.5 (leaf n0286): the wall from Falkirk down to the "
     "Firth of Forth ('Borth of Forth'), with the east-end fort labelled Caer-ridden (Carriden) and "
     "the Kinneil fortlet (Kinnelton), Mumrills, Cuffabent and the modern places (Stinghouse, "
     "Collender-house, Lanton, Bevercote, Grange-house, ...; a scale of two English miles) - no "
     "inset fort plan on the plate (the tree-marked Caer-ridden/Kinnelton enclosures are not forts - "
     "147). Tied to the new no-QID carriden row, the wall's east end (kind 'roman site'; renamed "
     "from falkirk-end after the Wikipedia Antonine Wall article fixed the end as Carriden - "
     "DECISIONS 808 149). Internet Archive britanniaromanao00hors, leaf n0286 of the 936-leaf "
     "Google scan (British Museum volume)."),
]

# The 8 new no-QID site rows the staged rows need (216's design + the 808 build decisions, DECISIONS
# 808 147/149/150): region lowercase per site, kind the space form (207a's spec), lon/lat
# cross-checked at build time (Wikipedia/Wikidata/Nominatim + the book's own maps) and recorded in
# location_check (the checked date is injected by stage()). The Antonine reuses (bar-hill-fort,
# rough-castle-fort) stay in the canonical extras.jsonl - looked up at run time, never re-created.
# Key order = the landed 207b extras-row shape (id, qid, name, lon, lat, region, kind, aerial_ok,
# place, location_check, source, note), inserted in STAGE_ROWS first-appearance order.
NEW_SITES = {
    "ardoch": {"id": "ardoch", "qid": None, "name": "Ardoch", "lon": -3.8731, "lat": 56.2742,
               "region": "scotland", "kind": "roman site", "aerial_ok": True,
               "place": "Braco, Gask Ridge, Perth and Kinross, Scotland",
               "location_check": {"status": "confirmed",
                                  "method": "Wikidata Q4788225 (Ardoch camp) P625 (precision 1e-6) cross-checked against the plate's rivers and the book's text pp.43-44 (checked 2026-10-14)",
                                  "note": ("the Braco camp (SM1601, Black Hill beside it) - the only surviving Roman camp named "
                                           "Ardoch, per the plate's rivers (Knoch west, Ruchel north) and pp.43-44 following "
                                           "Gordon 1726; the Wikipedia Antonine Wall article confirms the Gask Ridge area; the "
                                           "Knoch stream is unlocated in the 18th-c. and modern sources checked (Nominatim + "
                                           "Wikipedia, 2026-10-14); the Innerpeffery camp (the other plan on the plate) is "
                                           "recorded on the n0114 files row's desc - no row of its own (the 808 box); kind "
                                           "'roman site' - a legionary camp, not a fort")},
               "source": MODULE,
               "note": "new site staged by 808 (Horsley 1732, P.44, leaf n0114) - DECISIONS 808 148"},
    "virosidum": {"id": "virosidum", "qid": None, "name": "Virosum (near Elenborough, Solway coast)",
                  "lon": -3.482559, "lat": 54.708744, "region": "england", "kind": "roman fort",
                  "aerial_ok": True, "place": "near Maryport (Ellenborough), Solway coast, Cumberland, England",
                  "location_check": {"status": "approx",
                                     "method": "Nominatim (Ellenborough, Maryport) + the book's N.1 map placement between Olenacum and Gabrosentum (checked 2026-10-14)",
                                     "note": ("the P.113 principal - the only one of the five forts without a catalog row "
                                              "(I-IV = longovicium-q6674222/whitley-castle-q7996561/voreda-roman-fort-q17642742/"
                                              "luguvallium-q71551754; DECISIONS 808 147 item 4); Horsley's N.1 places VIROSIDUM near "
                                              "Elenborough between Old Carlisle and Brougham by 'Boulneis' on the Solway coast; the "
                                              "only Elenborough (Ellenborough) in the region is near Maryport (Nominatim 54.708744, "
                                              "-3.482559); no Wikidata item for Virosum; P.113 plan V is a schematic fort with no "
                                              "Praetorium")},
                  "source": MODULE,
                  "note": "new site staged by 808 (Horsley 1732, P.113, leaf n0185) - DECISIONS 808 147 item 4"},
    "cilurni": {"id": "cilurni", "qid": None, "name": "Cilurni (Chesters)", "lon": -2.139, "lat": 55.026,
               "region": "england", "kind": "roman fort", "aerial_ok": True,
               "place": "Chesters, near Corbridge, Northumberland, England",
               "location_check": {"status": "confirmed",
                                  "method": "Wikipedia 'Cilurnum' infobox (55deg01'34'N 2deg08'20'W) + Wikidata Q3818331 P625 (55.026, -2.1391, precision 1e-6) cross-checked against the book's N.5 map (checked 2026-10-14)",
                                  "note": ("the fort ON the wall line (N.5's CILVRNVM 'now West Chesters'); the catalog's "
                                           "Q17650519 row (P625 55.0246, -2.14302) sits ~300 m away, consistent - the row stays "
                                           "no-QID per the 808 box's tie list")},
               "source": MODULE,
               "note": "new site staged by 808 (Horsley 1732, N.5, leaf n0244) - DECISIONS 808 147/149"},
    "petriana": {"id": "petriana", "qid": None,
                "name": "Petriana (Horsley's N.8 Solway-coast station)", "lon": -3.45, "lat": 54.90,
                "region": "england", "kind": "roman fort", "aerial_ok": True,
                "place": "Cumberland coast (Longhope to the Cark), England",
                "location_check": {"status": "approx",
                                   "method": "the book's N.8 map placement (a hypothetical station - no web source exists for it) (checked 2026-10-14)",
                                   "note": ("no real fort - Horsley's N.8 invents PETRIANA on the Cumberland coast; the Roman "
                                            "Petriana of Rudchester is the catalog row rudchester-roman-fort-associated-civil-s-"
                                            "q17669775 (VINDOBALA); the N.8 coastal placement between Longhope and the Cark; "
                                            "the inset plan is a schematic")},
                "source": MODULE,
                "note": "new site staged by 808 (Horsley 1732, N.8, leaf n0250) - DECISIONS 808 147/149"},
    "congavata": {"id": "congavata", "qid": None, "name": "Congavata (Castlesteads)", "lon": -2.761,
                 "lat": 54.965, "region": "england", "kind": "roman fort", "aerial_ok": True,
                 "place": "Castlesteads, Cumbria, England",
                 "location_check": {"status": "confirmed",
                                    "method": "Wikipedia 'Camboglanna' infobox (54deg57'54'N 2deg45'40'W) cross-checked against the book's N.9/N.10 maps (checked 2026-10-14)",
                                    "note": ("the fort on the bluff over the Cam Beck at the Irthing bend ('now Stanwicks' on "
                                             "the N.10 plate); the catalog's Q17650705 row (P625 54.9632, -2.76252) sits ~200 m away, "
                                             "consistent - the row stays no-QID")},
                 "source": MODULE,
                 "note": "new site staged by 808 (Horsley 1732, N.9, leaf n0252) - DECISIONS 808 147/149"},
    "tunnocelum": {"id": "tunnocelum", "qid": None,
                  "name": "Tunnocelum (Boulneis, north of the Esk mouth)", "lon": -3.012, "lat": 54.898,
                  "region": "england", "kind": "roman fort", "aerial_ok": True,
                  "place": "Boulneis (near Bowness), Solway coast, Cumbria, England",
                  "location_check": {"status": "approx",
                                     "method": "the book's N.10 map placement ('now Boulneis', north of the Esk mouth); Nominatim geocoding of the small places (Ronciff/Braken/Boulneis/Drumbrugh) returned nothing (checked 2026-10-14)",
                                     "note": ("Horsley's N.10 places TVNNOCEIVM 'now Boulneis' by Braken ridge on the Solway "
                                              "shore north of the Esk estuary (ITVNNAE AESTVARIVM; the Esk mouth with Ronciff at the "
                                              "SW of the map); no Wikipedia article 'Tunnocelum'; the 'Stanwix' district article "
                                              "says the district is built on the fort 'known as Uxelodunum or Petriana' on the Eden "
                                              "- Horsley's own map puts that (as CONGAVATA 'now Stanwicks') at the Eden mouth, west "
                                              "of the Esk; no catalog row for either - the row follows the plate's Boulneis "
                                              "placement (DECISIONS 808 149)")},
                  "source": MODULE,
                  "note": "new site staged by 808 (Horsley 1732, N.10, leaf n0254) - DECISIONS 808 149"},
    "kirkintilloch": {"id": "kirkintilloch", "qid": None, "name": "Kirkintilloch (the Peel)",
                     "lon": -4.15472222, "lat": 55.93583333, "region": "scotland", "kind": "roman fort",
                     "aerial_ok": True, "place": "Kirkintilloch, East Dunbartonshire, Scotland",
                     "location_check": {"status": "confirmed",
                                        "method": "Wikidata Q2422689 (Kirkintilloch town) P625 (precision 30 m) cross-checked against the book's N.3 map (checked 2026-10-14)",
                                        "note": ("the Peel of Kirkintilloch on the Antonine Wall line at the east end of the "
                                                 "town; coordinates = the town's item Q2422689 P625; Horsley's N.3 shows the "
                                                 "concentric plan (the most-planned fort on the plate)")},
                     "source": MODULE,
                     "note": "new site staged by 808 (Horsley 1732, P.176 N.3, leaf n0282) - DECISIONS 808 149"},
    "carriden": {"id": "carriden", "qid": None,
                "name": "Carriden (east end of the Antonine Wall near Bo'ness)", "lon": -3.564436,
                "lat": 56.010057, "region": "scotland", "kind": "roman site", "aerial_ok": True,
                "place": "near Bo'ness, Falkirk, Scotland",
                "location_check": {"status": "confirmed",
                                   "method": "Wikidata Q81445376 (the Carriden Roman fort, precision 1e-6) cross-checked against the book's N.5 map label 'Caer-ridden' and the Wikipedia Antonine Wall article (checked 2026-10-14)",
                                   "note": ("the wall's east end where it met the Firth of Forth; Horsley's N.5 shows the wall "
                                            "from Falkirk down to the Forth ('Borth of Forth') with the fort labelled Caer-ridden "
                                            "and the Kinneil fortlet (Kinnelton); no fort PLAN on the plate - kind 'roman site'; "
                                            "renamed from falkirk-end after the Wikipedia Antonine Wall article fixed the east "
                                            "end as Carriden (the 147 'Falkirk ~ -3.79' fallback was the wrong end - DECISIONS "
                                            "808 149); Carriden House (Q5046188) and Nominatim agree with the fort item to "
                                            "<500 m")},
                "source": MODULE,
                "note": "new site staged by 808 (Horsley 1732, P.176 N.5, leaf n0286) - DECISIONS 808 149"},
}


def _page_sizes():
    """The BookReader width/height of every leaf, from the cached bookreader.json (offline; the
    staged rows' w/h come from here, never a download). {leaf n: (width, height)}; exits if the
    book has not been fetched."""
    import books_ia
    path = os.path.join(books_ia.RAW, IA, "bookreader.json")
    if not os.path.exists(path):
        raise SystemExit(f"{IA}: no cached bookreader.json - run --fetch first")
    d = json.load(open(path))
    pages = [p for spread in d["data"]["brOptions"]["data"] for p in spread]
    return {n: (p["width"], p["height"]) for n, p in enumerate(pages)}


def _file_row(leaf, tie, title, name, desc, s, wh):
    """The picture row + its hand 'plan' classified row for one staged leaf: 207b's 19-field files
    row (by = this module, url/thumb the stable IA page image, w/h from bookreader.json, the 200
    evidence field: kind caption_coords - named_place = the plate's printed list entry = the row's
    title, so check_caption's norm check is trivially true, and place_* = the tied site's own
    coordinates, so dist_m 0 reproduces offline) + the hand classified row (p_plan 1.0)."""
    w, h = wh
    url = f"https://archive.org/download/{IA}/page/n{leaf:04d}.jpg"
    f = {"site": tie, "qid": s.get("qid"), "title": title, "year": YEAR, "wd_plan": False,
         "cat": None, "name": name, "by": MODULE, "url": url, "thumb": url, "w": w, "h": h,
         "mime": "image/jpeg", "date": str(YEAR), "desc": desc, "artist": "John Horsley",
         "license": LICENSE, "page": f"https://archive.org/details/{IA}",
         "evidence": {"rec": "evidence/1", "kind": "caption_coords", "checked": now(),
                      "named_place": title, "place_qid": s.get("qid"),
                      "place_label": s["name"], "place_lon": s["lon"], "place_lat": s["lat"],
                      "site_lon": s["lon"], "site_lat": s["lat"], "dist_m": 0.0}}
    c = {"site": tie, "title": title, "p_plan": 1.0, "p_birdseye": 0.0, "p_photo": 0.0, "by": "hand"}
    return f, c


def stage(dry=False):
    """OFFLINE (no LLM, no network): append the book's 17 verified kind-s rows - one per leaf of the
    24-entry list's 17 kind-s (the 15 wall maps + n0114 P.44 + n0185 P.113) - to the shared roman
    staging files: the picture rows to files_roman.jsonl, their hand 'plan' rows to
    classified_roman.jsonl, and the new no-QID sites the rows need (the NEW_SITES keys in
    STAGE_ROWS first-appearance order) to extras_roman.jsonl (the Antonine reuses bar-hill-fort /
    rough-castle-fort stay in the canonical extras.jsonl - looked up at run time, never
    re-created). Every row carries the book's date 1732 and the 200 evidence field. Append-only
    and idempotent on (site, title) and site id: a second run changes no byte, and the other
    book's rows (207b) stay byte-identical; --dry previews instead of writing. 211 consolidates
    the *_roman files into the canonical ones."""
    sites = {}
    for r in _load(SITES_JSONL):
        if r.get("id"):
            sites[r["id"]] = r
    for r in _load(EXTRAS_CANON):
        if r.get("id") and r["id"] not in sites:
            sites[r["id"]] = r
    sites.update(NEW_SITES)
    page_sizes = _page_sizes()

    have_file = {(r.get("site"), r.get("title")) for r in _load(FILES_ROMAN)}
    have_cls = {(r.get("site"), r.get("title")) for r in _load(CLASSIFIED_ROMAN)}
    have_site = {r.get("id") for r in _load(EXTRAS_ROMAN)}

    files_rows, cls_rows = [], []
    for leaf, tie, title, name, desc in STAGE_ROWS:
        s = sites.get(tie)
        if not s:
            raise SystemExit(f"leaf n{leaf:04d} ties to {tie!r}, which is not a known site")
        if leaf not in page_sizes:
            raise SystemExit(f"leaf n{leaf:04d} has no page in the cached bookreader.json")
        f, c = _file_row(leaf, tie, title, name, desc, s, page_sizes[leaf])
        files_rows.append(f)
        cls_rows.append(c)

    site_rows, seen = [], set()
    for leaf, tie, title, name, desc in STAGE_ROWS:   # the new sites in STAGE_ROWS first-appearance order
        if tie in NEW_SITES and tie not in seen:
            seen.add(tie)
            if tie in have_site:
                print(f"   extras_roman.jsonl: site {tie} already present (skipped, nothing written)")
                continue
            r = dict(NEW_SITES[tie])
            r["location_check"] = dict(NEW_SITES[tie]["location_check"], checked=now())
            site_rows.append(r)

    for path, rows, have in ((FILES_ROMAN, files_rows, have_file),
                             (CLASSIFIED_ROMAN, cls_rows, have_cls)):
        tag = os.path.basename(path)
        for r in rows:
            k = (r.get("site"), r.get("title"))
            if k in have:
                print(f"   {tag}: row for {k[0]} already present (skipped, nothing written)")
            elif dry:
                print(f"   {tag}: would append {json.dumps(r, ensure_ascii=False)}")
            else:
                with open(path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                print(f"   {tag}: appended 1 row ({k[0]})")
    for r in site_rows:
        if dry:
            print(f"   extras_roman.jsonl: would append {json.dumps(r, ensure_ascii=False)}")
        else:
            with open(EXTRAS_ROMAN, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"   extras_roman.jsonl: appended 1 row ({r['id']})")
    print(f"horsley staging: {len(files_rows)} files rows, {len(cls_rows)} classified, "
          f"{len(site_rows)} of {len(seen)} new site rows appended ({IA})")


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
    elif a and a[0] in ("--stage", "--dry"):
        stage("--dry" in a)
    else:
        raise SystemExit("the check/golden legs are not built yet (809; see the module docstring)")
