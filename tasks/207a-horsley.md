Status: in-progress
# 207a: Horsley, Britannia Romana (1732)
Depends on: 200
Touches: fit/src_roman_horsley.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_horsley.py, tests/golden/src_roman_horsley_sample.json

## Goal
Subtask of 207 (the parent's Hand-over has the full mechanics): index John Horsley's
*Britannia Romana* (1732) with the existing book machinery and stage its site-plan rows tied
to Roman sites. Chosen IA copy: `britanniaromanao00hors` (Google Books scan, 936 leaves,
median 2237x3861 px, hOCR page text + djvu.txt present). Alternatives (only if specific pages
of the Google copy are unreadable): `bim_eighteenth-century_britannia-romana-or-the_horsley-john_1732`
(British Museum, 831 leaves, median 7984x13809 px) and the `..._0` copy (827 leaves,
8328x14257 px) - much larger images.
Note: this book's ~121 engraved plates are mostly Roman inscriptions and sculptures (list
kind "o"); its true site plans are the few maps (kind "s"). Stage the site plans; the
inscription plates are indexed in the list mapping (each names the site where the stone was
found) but are not staged as picture rows.

## Acceptance criteria
- [ ] The book is fetched from the Internet Archive (data/raw/books/britanniaromanao00hors/)
      and triaged with the existing machinery, per-book artifacts only
      (triage/britanniaromanao00hors.*.jsonl, lists/britanniaromanao00hors.json,
      lists/britanniaromanao00hors.map.json); the shared data/books/index.jsonl and
      validation.json are NOT written by this subtask.
- [ ] The book's own printed list of plates is transcribed (the books_lists PLATES pattern)
      and mapped to leaves; the stage-A/B recall against that list is recorded in the
      Horsley section of docs/lead_roman.md (instead of the shared validation.json).
- [ ] Staged rows (appended to the parent's shared staging files, rows tagged with this
      book): files_roman.jsonl for every verified site-plan page tied to a Roman site - an
      existing catalog site by QID where one exists, or a new extras_roman.jsonl entry
      (kind "roman fort" / "roman site", QID where it exists, lon/lat from the book's list
      or a cross-check) - each with the 200 evidence field (the book's printed list names
      the place; the specific check - list entry, caption, coordinates distance - recorded
      on the row) and a classified row by hand ("plan"); the book's date (1732) is recorded
      on the row.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one is accounted for in docs/lead_roman.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.

## Notes
- The LLM replicas serve on 127.0.0.1:8080-8082 (model qwen3.8-27b); since 215 re-pointed
  pipeline/books.py's LLM_PORTS to 8080,8081,8082,18080,18081, no in-process LLM_URLS patch is
  needed (verified 10-13: 8080/8081 answer, 8082 down). This subtask's module registers the
  book in books.BOOKS in-process only; it does not edit pipeline/ (the parent's Hand-over has
  the full recipe).
- The catalog already holds the major British Roman forts with QIDs (305 roman_fort rows:
  206 England, 54 Wales, 22 Netherlands, 17 France, plus 6 no-QID extras: vindolanda and the
  four Antonine Wall camps, aventicum). Tie Horsley's maps to those where the site matches;
  stage a new site only for a place not already in the catalog.
- The LLM triage of 936 pages is the long pole: run it as a resumable background job (the
  stage jsonl is append-only and skips done pages; see the "long background data jobs"
  PITFALLS entry).

## Hand-over
(2026-10-13, iteration 219, agent c - the module edit landed and is committed: CITE from the title page,
the 22-entry HORSEY_FIGS table (now the single source of truth for the list), register() injects
books.BOOKS + books_lists.HAND_FIGS, and --list = offline register + cmd_ocrmap. --list ran verified-
fully-offline (socket-blocked) and wrote the two per-book list files. validate_book (in-process,
offline) measured stage-A recall = 1.0 on all 15 gt map leaves. NEXT = stage B (17 pages, minutes),
then --stage/--check/--golden + tests + the lead-doc section. /tmp/horsley_full/ still holds every
full-size image + crop (277 files).)

**State.**
- fit/src_roman_horsley.py: done through --list (215 recipe steps 1-3: fetch 202, triage A 212, list
  219). HORSEY_FIGS holds the 22 entries with its comment (the no-list discovery; the kinds; transcribed
  by eye 215/216/218; stage-A captions = parametric hallucinations, never used). HORSEY_PLATES is still
  None (the ~121 inscription plates trail as kind o: indexed, never staged).
- lists/britanniaromanao00hors.json = {"plates": null, "figures": 22} (the table's dump, UTF-8);
  .map.json = 22 leaves, site_plan=true exactly on n236-254 even + n278-286 even (15 s maps), false on
  [60, 62, 256, 706, 734, 832, 867].
- validate_book figures block (stage A; the offline numbers for the lead doc): listed 22 (s 15 / o 7 /
  u 0); A typed 80 plate_site_plan, the BLANK_INK=0.005 floor keeps 17 (63 are blank/ghost show-through
  versos; no figure_site_plan, no F/C for this book), so flagged = 17: recall_pages 1.0,
  recall_pages_pm1 1.0, precision_strict = precision_lenient 0.882, flagged_not_in_list [114, 185]
  (n114's A caption "Innerpeffery camp. Ardoch camp." - Scottish hillforts from parametric memory;
  n185 "The five fecondary ftations per lineam valli." - a garbled echo of n236's printed title),
  flagged_on_other_only_pages [] (no kind-o leaf flagged), missed_pages [].
- Tests: 1 failed / 156 passed / 1 skipped (389 s; .venv/bin/python -m pytest tests/ --ignore=
  tests/test_gate.py -p no:cacheprovider). The lone red = agent a's 307d placement test (known
  pre-existing red, PITFALLS; same signature: seed check + /tiles/relief 404). 155->156 passed = main
  growth (212 subtask tests); no new reds from this change (nothing imports the module; the two list
  files are new per-book artifacts).
- Acceptance boxes: 1 done (fetch + triage A committed); 2 half (the list is transcribed into the
  module; the lead-doc recall recording is step 2, with B added); 3/4/5 pending (steps 3-4).

**CORRECTION to the 216/218 hand-overs (stage B is not the long pole):** books.cmd_triage_b runs on
site_pages_qwen (A/F/C after the ink floor = 17 here) | extra_site_pages (the 15 kind-s leaves from
.map.json, all already flagged by A) = 17 pages - a few minutes on live replicas, run foreground.
Stage F is not needed: A's recall on the 15 gt leaves is already 1.0, and other_illustration rows only
enter the B set through an F confirmation (this book has none). The 216 "A's 80 site pages" estimate
predicated B on the unfiltered A type.

**EXACT NEXT STEPS (one session each, in order):**
1. Stage B: check replicas up (the module's --status prints which of 8080/8081/8082 answer; 8080/8081
   were up at 218, 8082 down), then `.venv/bin/python fit/src_roman_horsley.py --triage B` (foreground,
   17 pages; nohup only if a replica is busy). Commit the B file when the writer is gone + mtime
   settled (the long-background-job PITFALLS).
2. Re-run the validate_book one-liner below + compute B's own verdict on the 17 pages (how many B
   confirms as plan; the two false positives should drop). Write docs/lead_roman.md's Horsley section:
   the no-list discovery (verified on both copies, 215), that the list = the plates' own printed
   headings, the 22-entry list (15 s maps + the N.11 wall section + six country maps), stage A/B recall
   (A: 1.0 / 1.0 / 0.882, flagged_not_in_list [114, 185] with their captions; B: whatever it confirms
   and drops), N.11 = a wall cross-section (kind o), the country maps indexed but never staged, and
   the stage-B page-count correction above.
3. Build --stage: one files_roman.jsonl row per kind-s map leaf (15 rows), each tied to its principal
   named fort (216's staging design; multi-fort maps tie to the most-named/planned fort, the others
   recorded in desc). Catalog QIDs verified in 216: castrum-segedunum-q637958 (SEGEDUNVM), pons-aelius-
   q7227963 (PONSAELIVM), rudchester-roman-fort-associated-civil-s-q17669775 (VINDOBALA), haltonchesters-
   roman-fort-settlement-and-q17648018 (HANNAVVM), aesica-q4688554 (the Aesica plan on N.7), birdoswald-
   roman-fort-and-the-section-of-q17650767 (BORCOVACEVS); NEW extras_roman.jsonl rows (the no-QID shape
   from extras.jsonl: kind "roman fort"/"roman site", QID where one exists, lon/lat from the book's
   map or a cross-check, region lowercase) for: Condercum (N.2/N.3, "now Benwell hill"), Cilurni/
   Chesters (N.5, "now West Chesters"), Procolitia (N.6, near Stanwix), Magna (N.7/N.8), Petriana
   (N.8/N.9), Congavata (N.9/N.10, "now Somersets"), Tunnocelum (N.10, "now Bonholm"), and the Antonine
   forts where not already in catalog/extras: Old Kilpatrick (check extras bar-hill-fort),
   Kirkintilloch (the Peel of Kirkintilloch, N.3), Balmuildie (Bemulie/Balmure, N.3), Rough Castle
   (check extras rough-castle-fort, N.4), Falkirk-end (N.5). Row fields: site, qid, title (the plate's
   printed title + its series), year 1732, url/thumb (the IA page), w/h, desc (the printed list entry
   = the plate heading: the 200 evidence's "list entry"), evidence {rec "evidence/1", kind
   caption_coords, checked <date>, named_place, place_qid, place_label, place_lon, place_lat,
   site_lon, site_lat, dist_m} - fit/evidence.py's check_caption verifies this OFFLINE from the stored
   fields only (named place in norm(title+desc); the stored distance reproduces within 1 km and is
   <= 50 km), so --check needs no network even for new extra sites.
4. --check (offline join: every staged row names an existing or staged site; every new extra has its
   plans; fit/evidence.py's check over this book's rows) + --golden (write tests/golden/
   src_roman_horsley_sample.json) + tests/test_src_roman_horsley.py (the no_network socket-blocking
   fixture as in tests/test_src_van_deventer.py; import the module by path via importlib + register()
   in-process; the LLM never runs in tests).
5. Later sessions: transcribe the ~121 inscription plates (Roman numerals I-CXXI, scattered through
   n0067-n0900; each plate prints its own heading + the find-site) into HORSEY_PLATES in batches
   (kind o, indexed, never staged). It does not block the 90% box, which counts kind-s leaves only
   (all 15 get staged in step 3, so the box already stands on that).

**The validate_book one-liner (offline; run with .venv/bin/python):**
    import urllib.request, ssl, socket   # FIRST - the ssl import must precede the patch (PITFALLS)
    def dead(*a, **k): raise RuntimeError("network blocked in this run")
    socket.socket.connect = dead; socket.create_connection = dead
    import importlib.util
    spec = importlib.util.spec_from_file_location("h207a", "fit/src_roman_horsley.py")
    h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h); h.register()
    import books_lists
    rep = books_lists.validate_book(h.KEY)   # print rep["figures"] + rep["flagged_site_pages"]

**Images (if /tmp is gone, re-download):** /tmp/horsley_full/ = every full-size jpg + all crops made
in 215/216/218. Re-download: https://archive.org/download/britanniaromanao00hors/page/nNNNN.jpg with
a browser UA (the way 215 did). Reading conventions: rotated sheets (P.158 N.1-N.10, P.176 N.1) =
rotate CW, title box at the sheet's bottom edge, corner mark at its top edge; upright sheets (P.176
N.2-N.5, N.11, the four Book-III country maps, the two front-matter Ptolemy fold-outs) = title box at
the captured page's top or bottom as noted in the DECISIONS entries 215/216/218.
