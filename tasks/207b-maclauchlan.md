Status: in-progress
# 207b: Maclauchlan, the survey of the Roman Wall (1857-58)
Depends on: 200
Touches: fit/src_roman_maclauchlan.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_maclauchlan.py, tests/golden/src_roman_maclauchlan_sample.json

## Goal
Subtask of 207 (the parent's Hand-over has the full mechanics): index Maclauchlan's survey of
Hadrian's Wall with the existing book machinery and stage its site-plan rows tied to the
forts on the wall. The parent's task says 1857: the survey of the wall's eastern branch ran
1857-59 and the volume was published 1858 - use the year printed on the title page and note
the discrepancy in the lead doc. Chosen IA copy: `memoirwrittendu00maclgoog` (the 1858
original, Google scan, 171 leaves, median 3290x5182 px; djvu.txt only, NO hOCR page index).
Alternative for reading text/list pages: `memoirwrittendur0000henr` (1971 reprint, 292
leaves, 1625x2697 px, hOCR present) - use it to transcribe the book's list, but stage images
only from the 1858 original.
The book's plates include detailed plans of the forts on the wall (Vindolanda, Vercovicium,
etc.) alongside wall cross-sections and stretches of the wall itself. Per the parent's
Notes: wall sections are not sites and are not staged, unless a named fort/structure with a
location is in the plate.

## Acceptance criteria
- [x] The book is fetched from the Internet Archive (data/raw/books/memoirwrittendu00maclgoog/)
      and triaged with the existing machinery, per-book artifacts only
      (triage/memoirwrittendu00maclgoog.*.jsonl, lists/memoirwrittendu00maclgoog.json,
      lists/memoirwrittendu00maclgoog.map.json); the shared data/books/index.jsonl and
      validation.json are NOT written by this subtask.
- [x] The book's own printed list of plates is transcribed (the books_lists PLATES pattern)
      and mapped to leaves; the stage-A/B recall against that list is recorded in the
      Maclauchlan section of docs/lead_roman.md (instead of the shared validation.json).
      (The book has NO printed plate list - its only list is the binder's directions, djvu leaf
      119; the ground truth is the per-leaf hand table per the 207a/Horsley fallback, 131's
      decision; transcribed + mapped + recall recorded as decided.)
- [x] Staged rows (appended to the parent's shared staging files, rows tagged with this
      book): files_roman.jsonl for every verified site-plan page of a named fort/structure
      tied to a Roman site - an existing catalog site by QID where one exists, or a new
      extras_roman.jsonl entry (kind "roman fort" / "roman site", QID where it exists,
      lon/lat from the book's list or a cross-check) - each with the 200 evidence field
      (list entry, caption, coordinates distance recorded on the row) and a classified row
      by hand ("plan"); the book's date (title-page year, 1857/1858) is recorded on the row.
      (n0093 staged 2026-10-14: files_roman +1, classified_roman +1 "plan", extras_roman +1
      the new site luguvallium-q71551754 Q71551754, year 1858 on the row; the other kind-s
      leaves n0078/n0111 are blank in this copy - nothing to stage, accounted for below.)
- [x] fit/evidence.py check passes offline on every staged row (2026-10-14: PASS
      caption_coords, rc=0, dist 324.1 m reproduced from stored fields). At least 90% of the
      verified site-plan pages are staged, or each missing one (wall sections, sections alone)
      is accounted for in docs/lead_roman.md (1 of 3 = 33% < 90%; the two missing are the blank
      plates n0078/n0111, accounted for individually in the lead doc's Maclauchlan section -
      the box's disjunct).
- [ ] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.

## Notes
- Same mechanics as 207a: in-process book registration in books.BOOKS, books.LLM_URLS
  patched to the live replicas (127.0.0.1:8080-8082) when the built-in ports are down,
  per-book triage/lists artifacts only, shared staging files tagged per book.
- Most wall forts are already in the catalog (the 206 England roman_fort rows include the
  wall forts with QIDs, e.g. vindolanda QID-less extra plus hardknott, concangis, glannoventa,
  whitley-castle, milecastles). Tie to them where the plate's site matches; stage a new site
  only for a named place not in the catalog.

## Lead note (2026-10-13)
Blocked: the owner said "Stop 207". Do not start until the owner lifts it.
(2026-10-13: LIFTED - the owner answered ask_human 006/007 (both asking whether the stop
still stands) with "b" = the stop is lifted; 207a was completed on that lift (7e9c829) and
207c dropped on the owner's answer to ask 008. This note records the stop as made.)

## Hand-over
(2026-10-14, iteration 134, agent c - the --stage session. READ THIS FIRST.)

**What happened this session** (all done; code + data changes UNCOMMITTED - the harness saves them for 135 to commit):
1. Built the `--stage` leg in fit/src_roman_maclauchlan.py (docstring updated, main() dispatches --stage/--dry; new constants SITE_NAME/SITE_QID/SITE_LON/LAT/PLACE_QID/PLACE_LON/LAT/FILE_TITLE/FILE_NAME/FILE_DESC above stage()). OFFLINE: the row is built from stored facts only - title = the plate's own printed heading; desc = the binder's-list entry (djvu leaf 119) + the p.77 running head "(See Plans, Fig. 4.)" (the named-place "Carlisle" carrier check_caption re-verifies); year/date 1858; url/thumb = the stable IA /download/ page image; w/h 964x1400 read from the committed stage-B row (data/books/triage/<ia>.B.jsonl img_size - the ONLY dynamic input; fails loud if missing/unreadable); artist Henry Maclauchlan; license "public domain (IA: NOT_IN_COPYRIGHT, the 1858 original)" (live item metadata: no licenseurl, possible-copyright-status NOT_IN_COPYRIGHT). NO map_box on the files row: files.jsonl's shape has no such field - the propose/inkfit fit flow reads map_box from the BOOK-INDEX row (211 consolidates it from the B file) and falls back to the full page when absent (808/809: same).
2. Ran it under the socket-blocking wrapper (0.58 s, no network): the three shared staging files, ABSENT on this branch, created with exactly one row each - extras_roman.jsonl + luguvallium-q71551754 (Q71551754 "Luguvallium (Carlisle)", lon/lat -2.94077/54.896187 the item's P625 precision 1e-6, region "england", kind "roman fort" SPACE form, place "Carlisle, Cumberland, England", aerial_ok true, location_check records the cross-check: P625 on the castle ground where the book's supposed station stands and the plan's Wall+Vallum meet, 324 m from the city's P625, VICI 12444, item has NO enwiki article so no wikipedia field); files_roman.jsonl + the n0093 row (evidence caption_coords: named_place "Carlisle", place Q192896 P625 -2.936388889/54.894722222, site the fort's P625, dist_m 324.1 = evidence.hav_m with its R=6371008.8 so check_caption reproduces it exactly); classified_roman.jsonl + (site,title) p_plan 1.0 by hand. Idempotency verified: a second real --stage and --dry both print "row already present (skipped, nothing written)" and all three files' md5 stayed unchanged.
3. Box 4 verified this session: `.venv/bin/python fit/evidence.py check --files data/commons/files_roman.jsonl --books data/books/.no-books` -> "PASS caption_coords luguvallium-q71551754|FIG. 4...", "1 rows, 1 pass, 0 fail, 0 no-tie", rc=0 (offline, stored fields only). Join (one-off python): every file row names a staged site, every new site has its plan, every file row has its classified row.
4. docs/lead_roman.md: the n0093 inventory line now records the actual staging (site id, QID, caption_coords 324.1 m, offline PASS, year 1858, stable /download/ url). Boxes 3-4 ticked in the task file (box 4's 90% disjunct was already in the section since 133).

**Tests:** a full-suite run was STARTED in the background this session (`nohup .venv/bin/python -m pytest tests/ -q -p no:cacheprovider > /tmp/aw134_suite.log 2>&1 &`, ~7 min) and its result was NEVER READ (context limit). Expectation: baseline 159/1/1 (lone red = agent a's 307d placement test); no committed test reads the new *_roman staging files (test_merge joins only stage-A .A.jsonl). NEXT SESSION: read /tmp/aw134_suite.log (if gone, re-run the same command) and re-baseline the number here.

**Acceptance boxes:** 1 (132), 2 (133), 3 (134), 4 (134) ticked. Only box 5 (test + golden) is left.

**Exact next step (135).**
1. Commit the session's saved changes first (fit/src_roman_maclauchlan.py, the three *_roman staging files, docs/lead_roman.md, this task file; check /tmp/aw134_suite.log first and note the suite state in DECISIONS).
2. Build `--check` (offline: join staged roman rows to catalog+extras - every row names an existing or staged site, every new site has its plans, every file row has its classified row; then fit/evidence.py check over this book's rows) and `--golden` (tests/golden/src_roman_maclauchlan_sample.json = the staged rows as the approved sample) in fit/src_roman_maclauchlan.py (main() still rejects them; the docstring's "(not built yet)" lines say so), then tests/test_src_roman_maclauchlan.py on the tests/test_src_van_deventer.py no_network socket-blocking fixture pattern: run stage() with the module's FILES_ROMAN/CLASSIFIED_ROMAN/EXTRAS_ROMAN constants MONKEYPATCHED to temp-dir paths (stage() reads them as globals at call time - that is the hook; stage() also lazy-imports catalog + evidence, both offline) and assert idempotency (second run changes no byte) + the row shapes + the evidence PASS + the join; no LLM, no network, no fixed ports, writes only inside the project + temp. Then run the full suite, re-baseline, tick box 5 -> Status: done.

**Re-read next session:** fit/src_roman_maclauchlan.py (stage() + the staging constants; --check/--golden NOT built); the three staging files (one row each: data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl); tests/test_src_van_deventer.py (the fixture pattern); docs/lead_roman.md's Maclauchlan section (in sync with the staged rows since this session).

**What happened this session.**
1. Ran `validate_book` OFFLINE: socket-blocking wrapper (import urllib.request/ssl/socket
   FIRST; patch socket.socket.connect + connect_ex, socket.create_connection, socket.getaddrinfo
   to raise; then importlib-load fit/src_roman_maclauchlan.py, register(), books_lists.
   validate_book(KEY)). No network, no LLM. Output matched the 132 hand-over's hand-computed
   expectations EXACTLY: pages 171, triaged_A 171, flagged_site_pages_stageA 3, stageF_pages 0,
   flagged_site_pages 3; figures listed 6 / site 3 / other 3 / unsure 0 / expected None,
   gt_site_pages 3, recall_pages 1.0 (±1: 1.0), flagged_nonplate_pages 3, precision_strict
   1.0, precision_lenient 1.0, flagged_on_other_only_pages [], flagged_not_in_list [],
   missed_pages [], stage_A_only {recall 1.0, flagged 3}; no "plates" key (no printed list -
   the figs branch is the list). Mechanism verified in source: `flagged` = site_pages_qwen =
   stage-A SITE_TYPES rows surviving ink >= BLANK_INK (0.005); measured ink 0.0102 (n0078),
   0.0352 (n0093), 0.1048 (n0111) -> all three in; 90/129 other_illustration, 115 text_only ->
   never flagged. Filed as a PITFALLS entry (validate_book offline-safe + the ink-drop trap).
2. Wrote the "## Maclauchlan" section into docs/lead_roman.md, inserted after the lead header,
   BEFORE "## Roy" (subtask order; if a merge brings 807's Horsley section, mine moves AFTER
   it - never edit 807's text; the lead's own title line still says 1857-58 - I left the
   header untouched and the section records the corrected date). Contents: source (1858
   original the only readable copy; Nochlin mislabel + Wanney LCP-restriction, PITFALLS),
   DATE (survey 1852-1854 + imprint MDCCCLVIII 1858 vs the parent's 1857-59; the 1858 printing
   carries later 1857-58 work - Willow Holm section Sep't 7th 1858, the Carlisle great sewer;
   gift leaf n0007, 1859), the no-list finding (binder's directions verbatim + the hand-table
   fallback), the 6-leaf inventory with per-leaf verdicts (n0078 BLANK, n0090 wall section,
   n0093 the only legible plan - the one that gets staged, n0111 BLANK, n0115 table, n0129
   tiles), the unprinted Figs 2/3/5/6 (122 size census), the stage-A/B recall numbers, and
   the 90% accounting (1 of 3 = 33% < 90%; the two missing each accounted for as blank in
   this copy - the box's disjunct).
3. Box 2 ticked: the list (binder's directions -> per-leaf hand table, 131's decision) is
   transcribed and mapped to leaves (lists/*.json + .map.json, byte-stable since 131), and the
   stage-A/B recall is recorded in the lead doc's Maclauchlan section.
4. Suite NOT run this session (doc/offline-run session; no code changed, no new test). The
   driver's 2026-10-13 baseline 159/1/1 (lone red = agent a's 307d placement test) stands.

**Acceptance boxes:** box 1 (132), box 2 (this session) ticked. Boxes 3-5 untouched.

**Exact next steps (134+, in order).**
1. **Build `--stage`** in fit/src_roman_maclauchlan.py (read tasks/808-horsley-stage.md in
   full first for the row-content conventions; re-read data/commons/files.jsonl row shape,
   a no-QID row of data/catalog/extras.jsonl (the location_check field), fit/evidence.py
   with fresh eyes): create the three shared staging files (ABSENT on this branch) with the
   decided rows - extras_roman.jsonl +1 (Luguvallium (Carlisle), Q71551754, lon/lat
   54.896187/-2.94077, kind "roman fort" SPACE form, region england, place "Carlisle,
   Cumberland, England", location_check per 130's Decision 2); files_roman.jsonl +1 (n0093:
   site = the new extras id, qid Q71551754, title/desc carrying "Carlisle" + the binder's-
   list entry + the p.77 reference; year 1858; url/thumb the IA page image
   https://archive.org/download/memoirwrittendu00maclgoog/page/n0093.jpg; w/h 964x1400 from
   the triage row; map_box [100,405,830,880] from this book's B row; evidence kind
   caption_coords: named_place Carlisle, place Q192896 P625 54.894722/-2.936389, dist_m
   324.1); classified_roman.jsonl +1 ((site,title), class "plan" by hand). Append-only,
   idempotent (a second run changes no byte), rows tagged memoirwrittendu00maclgoog, --dry
   previews. Then verify the lead doc's n0093 line (written this session) matches what was
   actually staged (the tie to the new Luguvallium site).
2. **`--check` (offline: join staged rows to catalog+extras - every row names an existing or
   staged site, every new site has its plans; fit/evidence.py check over this book's rows)
   + `--golden` (tests/golden/src_roman_maclauchlan_sample.json) + tests/
   test_src_roman_maclauchlan.py** (the no_network socket-blocking fixture as in
   tests/test_src_van_deventer.py; no LLM calls in tests; no fixed ports; writes only
   inside the project). Then run the suite (baseline 159/1/1; my tests all pass, the lone
   307d red stays) and re-baseline in the notes.
3. **Boxes 4-5 -> done**: box 4's evidence check is covered by --check's test; the 90%
   accounting is already in the lead doc (the box's disjunct). When boxes 3+4+5 all pass:
   Status: done (the driver re-checks every box + the suite).

**Re-read next session:** `fit/src_roman_maclauchlan.py` (--stage/--check/--golden NOT built
- main() rejects them with the docstring pointer; MACLAUCHLAN_FIGS + docstring current);
`tasks/808-horsley-stage.md` (in full - row-content conventions); `data/commons/files.jsonl`
(row shape); `data/catalog/extras.jsonl` (no-QID row shape, location_check field);
`fit/evidence.py` (check/check_commons/check_caption); `data/books/triage/
memoirwrittendu00maclgoog.B.jsonl` (n0093 map_box [100,405,830,880]); `docs/lead_roman.md`
(the Maclauchlan section written this session - keep it in sync if the staged row differs);
PITFALLS' new validate_book entry (the offline wrapper recipe).
