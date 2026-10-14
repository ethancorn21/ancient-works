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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207b-maclauchlan.md` (in-progress) - hand-over: (2026-10-14, iteration 134, agent c - the --stage session. READ THIS FIRST.) --stage built and run: the three *_roman staging files created (new site luguvallium-q71551754 Q71551754 + the n0093 row + its "plan" classified row); fit/evidence.py check PASSES offline (rc=0); boxes 3-4 ticked; only box 5 (test + golden) left - 135 builds --check/--golden/tests and re-baselines the suite (a background run's log /tmp/aw134_suite.log was never read)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/212-cover-final.md` (in-progress) - hand-over: (2026-10-13, iteration 255, agent a, written at the context limit -
- `tasks/236a-us-city-plans.md` (in-progress) - hand-over: (2026-10-13, iteration 155, agent a - **MAIN MERGED (commit 3093e4e, 12/12 tests green). Site-point research in progress: Fort Nashborough = Q5471739,
- `tasks/236-us-cities.md` (split)
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-13, iteration 208, agent c - the driver returned the parent: all existing subtasks
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307bc-reverify-place-mode.md` (open) - hand-over: (2026-10-13, iteration 256, agent a - first session: the task was filed as the driver
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-13, iteration 256, agent a - context limit hit at the end of this session; the
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,
- `tasks/807-horsley-list-correction.md` (blocked)
- `tasks/808-horsley-stage.md` (blocked)
- `tasks/809-horsley-check.md` (blocked)

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/235-placement-test-dep-pick.md`
- `tasks/236b-us-birdseye.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 207 DECISION: split into 207a (Horsley), 207b (Maclauchlan), 207c (Roy); reordered so the unblocked books go first
Chose per-book subtasks over one task: the three-book pipeline (fetch + triage A/F/C/B + list mapping + recall + staging + tests + lead doc) is far beyond a few sessions, and the task's own Notes anticipate the split. Reordered from the Notes' (Roy, Horsley, Maclauchlan) to (Horsley, Maclauchlan, Roy): the driver hands out subtasks in a/b/c order, and Roy (207c) is blocked waiting on a human-provided copy (BLOCKER below), so putting it last keeps the pipeline moving.
Copy choices (measured this session via books_ia): Horsley -> `britanniaromanao00hors` (Google Books, 936 leaves, median 2237x3861 px, hOCR + djvu.txt; alternates the bim British Museum copies, 831/827 leaves, ~14000 px images - only if the Google pages are unreadable). Maclauchlan -> `memoirwrittendu00maclgoog` (the 1858 original, 171 leaves, 3290x5182 px, djvu.txt only, no hOCR; the 1971 reprint `memoirwrittendur0000henr`, 292 leaves 1625x2697, has hOCR and is the OCR source for the book's list; stage images only from the 1858 original). Mechanics: each subtask's module registers its book in `books.BOOKS` and patches `books.LLM_URLS` in-process to the live replicas (127.0.0.1:8080-8082, model qwen3.8-27b, verified up this session) - no edits to pipeline/ (215 re-points books.py properly); per-book artifacts only (triage/<ia>.*, lists/<ia>.json/.map.json via `books_lists.cmd_ocrmap` after in-process `books_lists.PLATES[ia]` injection); recall recorded per book in docs/lead_roman.md via `books_lists.validate_book` (the shared validation.json/index.jsonl stay untouched until 211); staging appends to the parent's shared files (files_roman.jsonl etc.) with rows tagged per book, the 204/205 append-only idempotent pattern.

### 2026-10-11 207 BLOCKER: Roy 1793 "Military Antiquities of the Romans in North Britain" is not on the Internet Archive
- Attempt 1: IA advancedsearch by exact title, "romans in north britain", "antiquities of the romans in north britain", creator "Roy, William" (fuzzy: unrelated hits), title:"military antiquities" (20 hits: Grose et al., never Roy), a 1790-1800 year-range text query -> the only related item is a 1917 dissertation ABOUT Roy (macdonald-1917-roy, ~76 journal leaves, no facsimile, no plate list) - not the book
- Attempt 2: ten guessed identifier patterns (militaryantiquit00roy, ...u, ...0, ...w, ...goog, ...0000roy, ...0000royw, militaryantiquities00{,00}roy{,w}, militaryantiquiti00roy, militaryantiquit01roy) -> all return `{}`
- Attempt 3: the NLS complete facsimile (maps.nls.uk/roy/antiquities/, "174 pages, 51 map plates") via web_fetch and curl with three browser UAs, HTML and guessed image paths alike -> HTTP 405 AWS-WAF "Human Verification" captcha challenge on every path; the NLS open S3 tile bucket (mapseries-tilesets) lists fine but holds no antiquities set (roy/ = 1747-55 military survey only, already used by pipeline/nls.py as background maps)
Needed: a human with a real browser to download the NLS facsimile and place it in data/raw/books/roy1793/ (or a decision to drop Roy). Filed ask_human (request 003, open, human_only); 207c set to blocked. 207a/207b proceed independently: the subtasks run in sequence, so the shared staging files (files_roman.jsonl etc.) carry per-book tagged rows without conflict; each subtask's module, triage/lists artifacts and tests are disjoint.

### 2026-10-14 207b DECISION: iteration 130 - n0093 (Fig. 4) is kind s, the PLAN OF CARLISLE (Wall + Vallum course through the town, with the 1857-58 great sewer); its site tie is a NEW extras_roman row "Luguvallium (Carlisle)" Q71551754 (not Carlisle Castle Q614836); stage n0093 ONLY - n0078/n0111 are blank in this copy and get accounted for in the lead doc (the box's disjunct); Housesteads re-verified: the catalog NOW has Q17677378 (123's "no row" is stale)
1. **Kind of n0093 = s** (the one open call of the 123 hand-over; decided by reading djvu leaves 93-99 = printed pp.76-80 verbatim from the cached data/raw/books/memoirwrittendu00maclgoog/memoirwrittendu00maclgoog_djvu.xml this session): p.76 (djvu 93) carries the running heads "Carlisle. The Castle. The great sewer." and discusses the supposed Roman station at Carlisle and the Vallum joining the Castle, traced in the great-sewer excavation; p.77 (djvu 96) runs "CARLISLE, COURSE OF THE WALL AND OF THE YALLUM." and closes the vallum paragraph with "(See Plans, Fig. 4.)"; the binder's list (djvu leaf 119) says "The Plans, Fig. 4, 6, Carlisle and the Camp on Skew Hill at page 76." It is therefore a plan of a NAMED PLACE (Carlisle) showing the Wall/Vallum course and the sewer - not a wall-course section (that is n0090, the Willow Holm plan/section/elevation, kind o). The plate's own "Scale of Chains" (0-20) confirms a town-scale extent, not a fort extent.
2. **Site tie for n0093 = a NEW extras_roman.jsonl row** (the file does not exist yet on this branch; 207b creates it, 808's notes allow it - append-only, rows tagged memoirwrittendu00maclgoog): name "Luguvallium (Carlisle)", qid Q71551754, lon/lat 54.896187/-2.94077 (the item's P625), region "england", kind "roman fort" (space - the 207a/808 spec, not extras.jsonl's underscore form), place "Carlisle, Cumberland, England", location_check recording the cross-check. Q71551754 verified via the Wikidata API this session: label "Luguvallium Legionary Fort - Carlisle", P31 = Q57821 (English label "fortification" - so kind roman fort, not roman site), P131 = Q192896 (the city of Carlisle, whose Latin alias on Wikidata is "Luguvallium"), P625 precision 1e-6, VICI 12444. NOT tied to Carlisle Castle (Q614836, extras.jsonl, kind castle, mackenzie): the plate is the Wall/Vallum course through the town, and the book's supposed station sits on the castle ground - the fort's own item is the right site. No luguvallium row exists anywhere in the catalog (grep sites.jsonl/extras.jsonl/index.jsonl/web/data/sites.json: none).
3. **Row evidence for n0093** (files_roman.jsonl rows run through fit/evidence.py `check` -> `check_commons` -> `check_caption`, re-verified OFFLINE from stored fields only - re-read the module in full this session with fresh eyes): kind caption_coords, named_place "Carlisle" (must appear in norm(title+desc) - the row's title/desc carry it via the binder's-list entry), place Q192896 (Carlisle city P625 54.894722/-2.936389), site = the new extras row, dist_m 324.1 (haversine city->fort point, computed by running it this session; well under the 50 km cap, and the stored distance reproduces within 1 km, so check_caption passes offline).
... (2.1 KB more: `grep -n -A 200 -F '## 2026-10-14 207b DECISION: iteration 130 - n0093 (Fig. 4) is kind s, the PLAN OF CARLISLE (Wall + Vallum course through the town, with the 1857-58 great sewer); its site tie is a NEW extras_roman row "Luguvallium (Carlisle)" Q71551754 (not Carlisle Castle Q614836); stage n0093 ONLY - n0078/n0111 are blank in this copy and get accounted for in the lead doc (the box's disjunct); Housesteads re-verified: the catalog NOW has Q17677378 (123's "no row" is stale)' DECISIONS.md`)

### 2026-10-14 207b DECISION: iteration 131 - list leg built on the HAND_FIGS pattern (the book's list = the binder's instructions, so the per-leaf table IS the list, the 207a/Horsley fallback); per-book lists/*.json + .map.json written OFFLINE and byte-stable; the title pages read from the triage images settle the book's date: survey 1852-1854, imprint MDCCCLVIII (1858) - the parent's "1857-59" is wrong
1. **Module rewritten to the HAND_FIGS pattern** (hand-over item 1): `MACLAUCHLAN_FIGS` = the 6-line per-leaf table (78 Brampton s/65, 90 Willow Holm o/76, 93 Carlisle s/76, 111 Housesteads-gateway s/93, 115 Table of Stations o/97, 129 Binchester tiles o/7; every kind_by hand), register() injects it into books_lists.HAND_FIGS[IA] (no PLATES injection - the book has no OCR-able list, so parse_plates stays None and figure_list falls to parse_hand_figures, exactly 207a's shape); --list is now OFFLINE (register + books_lists.cmd_ocrmap - no djvu page_texts swap, no reprint hOCR: the reprint item is the Nochlin mislabel). The stale docstring claims (the reprint as list source; the djvu swap; "1857-59" in CITE) were all corrected. --djvu kept as the reading leg (its usemap numbers are leafNums = n+1, 1:1-aligned with bookreader here).
2. **--list ran OFFLINE twice (socket-blocking wrapper): no network, no LLM.** It wrote data/books/lists/memoirwrittendu00maclgoog.json ({"plates": null, "figures": 6}, ensure_ascii=False because the ia is in HAND_FIGS after register) + .map.json (6 leaves: n78 site_plan true, n90 false, n93 true, n111 true, n115 false, n129 false) - md5 8479d53f196fed1fa2bb0d7159b58257 / f6593c9e01c19157daf997e7a03bb04a, byte-identical across both runs (idempotent, append-only never violated: the files are per-book artifacts this task owns). Both were UNCOMMITTED at the context limit - the harness saved them; 132 commits them (md5-check first).
3. **Title pages read from the triage images (n0009, n0011, n0012, n0013) - the book's date, decided:** short title (n0009) and full title (n0011) both print "A SURVEY OF THE ROMAN WALL, THROUGH THE COUNTIES OF NORTHUMBERLAND AND CUMBERLAND, IN THE YEARS 1852-1854"; the full title adds "MADE BY DIRECTION OF HIS GRACE THE DUKE OF NORTHUMBERLAND, K.G., PATRON OF THE SOCIETY OF ANTIQUARIES OF NEWCASTLE-UPON-TYNE... LONDON: PRINTED FOR PRIVATE CIRCULATION. MDCCCLVIII." (n0012 verso = Bradbury and Evans, Whitefriars - the djvu 'WHITBY' was OCR garbage; the djvu '1864' in both titles was a misread of 1854, settled by the 4x crop). The preface (n0013) retitles "BETWEEN THE TYNE AND THE SOLWAY, IN THE YEARS 1852-1854" and its footnote dates the survey: Wallsend summer 1852 to Portgate; 1853 to Carvoran; by winter 1854 completed to Bowness. Consequences: (a) the parent task's "the survey ran 1857-59" is WRONG - the book's own title page says 1852-1854; (b) the row's book date stays 1858 (the title page's own imprint MDCCCLVIII, per the task's "use the year printed on the title page"); (c) the discrepancy the lead doc records is: title-page survey 1852-1854 + 1858 printing that also carries later 1857-58 work (the Willow Holm section taken Sep't 7th 1858, the Carlisle plan's 1857-58 great sewer); (d) CITE/WHY in the module are now the corrected wording (uncommitted). A gift leaf (n0007): "Presented to Professor Phillip by the Duke of Northumberland, Alnwick Castle, 17 July 1859" - the copy was in circulation by 1859, consistent with 1858.
4. **Stage A re-verified (171 rows / 0 errors; LLM 8080/8081 up, 8082 down, re-checked today):** n0078 plate_site_plan, n0090 other_illustration, n0093 plate_site_plan, n0111 figure_site_plan, n0115 text_only, n0129 other_illustration. The stage-A site-type set {78,93,111} equals the table's gt_site set exactly, so the next session's validate_book is expected to give recall_pages 3/3 with the two other_illustration leaves (90,129) not in SITE_TYPES (no false positives).
... (0.5 KB more: `grep -n -A 200 -F '## 2026-10-14 207b DECISION: iteration 131 - list leg built on the HAND_FIGS pattern (the book's list = the binder's instructions, so the per-leaf table IS the list, the 207a/Horsley fallback); per-book lists/*.json + .map.json written OFFLINE and byte-stable; the title pages read from the triage images settle the book's date: survey 1852-1854, imprint MDCCCLVIII (1858) - the parent's "1857-59" is wrong' DECISIONS.md`)

### 2026-10-14 207b DECISION: iteration 132 - stage B live on the three site leaves (3/3 ok, 0 errors, 9.7 s on the two up replicas); n0093's Carlisle plan got map_box [100,405,830,880] (norm1000) for the staging row; box 1 (fetch + triage A/B + per-book lists) ticked
1. 131's uncommitted work is committed by the driver (66530ec): working tree clean at session start; both list artifacts md5-match 131's recorded values (8479d53f196fed1fa2bb0d7159b58257 / f6593c9e01c19157daf997e7a03bb04a) - the recipe's item 1 is done, nothing to commit for it.
2. `--triage B` (live; replicas 8080/8081 up, 8082 down - re-checked via --status): run_stage over ns = A's site set ∪ the list's kind-s leaves = {78, 93, 111}; 3/3 pages parse ok, 0 errors, 9.7 s. Wrote data/books/triage/memoirwrittendu00maclgoog.B.jsonl (per-book artifact, append-only, committed). The staging-relevant row: n0093 map_box [100,405,830,880] norm1000 (= px 96,567-800,1232 on the 964x1400 triage image), label "FIG. 4", both scale bars read; the LLM's site_names are street labels, so the row's named place stays "Carlisle" from the binder's list (130's Decision 3). n0078 [160,98,875,860] and n0111 [338,495,595,512] (= the scale-bar strip of the small blank gateway figure) are record-only - both plates blank in this copy, not staged.
3. Box 1 ticked in the task file: fetched 171/171 + A 171/0 + B 3/0 + per-book lists (131); the shared data/books/index.jsonl and validation.json were NOT written (git status showed only the new B file). No stage F needed: A's site set equals the list's kind-s set exactly (no missed site pages).
4. Suite not run this session: data-only leg; no test reads the B jsonl (test_merge.py joins only stage-A .A.jsonl files) and my own test file is not built yet. The driver's 2026-10-13 baseline 159/1/1 stands (lone red = agent a's 307d placement test).
Next: 133 = validate_book offline (expected numbers in the hand-over) -> the "## Maclauchlan" section in docs/lead_roman.md (inserted before "## Roy"), then --stage, then --check/--golden/tests.

### 2026-10-14 207b DECISION: iteration 133 - validate_book run OFFLINE matched the hand-computed numbers exactly (171/171/3/3, recall 1.0, precision 1.0, no misses); wrote the "## Maclauchlan" section into docs/lead_roman.md (after the lead header, before "## Roy"); box 2 ticked
1. Offline validate_book (socket-blocking wrapper: import urllib.request/ssl/socket FIRST, patch socket.socket.connect + connect_ex, socket.create_connection and socket.getaddrinfo to raise, then importlib-load fit/src_roman_maclauchlan.py, register(), books_lists.validate_book(KEY)): no network, no LLM. Output == the 132 hand-over's hand-computed expectations, nothing different: pages 171, triaged_A 171, flagged_site_pages_stageA 3, stageF_pages 0, flagged_site_pages 3; figures listed 6 / site 3 / other 3 / unsure 0 / expected None, gt_site_pages 3, recall_pages 1.0 (±1: 1.0), flagged_nonplate_pages 3, precision_strict 1.0, precision_lenient 1.0, flagged_on_other_only_pages [], flagged_not_in_list [], missed_pages [], stage_A_only {recall 1.0, flagged 3}; no "plates" key (the book has no PLATES list - the figs branch IS the list). Mechanism verified in source: `flagged` = books.site_pages_qwen, which drops stage-A site pages whose ink < BLANK_INK (0.005); measured ink 0.0102/0.0352/0.1048 for n0078/n0093/n0111 so all three stay in (a truly blank page would not) and 90/129 (other_illustration) + 115 (text_only) never enter - filed as a PITFALLS entry under the book-machinery section (offline recipe + the ink-drop trap + Maclauchlan's verified final numbers).
... (2.2 KB more: `grep -n -A 200 -F '## 2026-10-14 207b DECISION: iteration 132 - stage B live on the three site leaves (3/3 ok, 0 errors, 9.7 s on the two up replicas); n0093's Carlisle plan got map_box [100,405,830,880] (norm1000) for the staging row; box 1 (fetch + triage A/B + per-book lists) ticked' DECISIONS.md`)

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)
- Re-verified the 160 hand-over's numbers with fresh measurements BEFORE deleting (AGENTS.md: check facts by running code). Confirmed: 8 pairs = 4 distinct points on a 100-px grid ladder (three on u=100; the 200-px and 100-px lat steps span 0.0053896/0.0017967 deg = 1.5:1 per pixel, no similarity can hit; the page's simFit (exact port) gives resid 10.9-39 m, 2.634 m/px, +1.06 deg - identical to the committed shot's [eval] line). CORRECTIONS to the 160 hand-over: the real hillfort is ~20 m NW of the site point (not '+22 E / -55 N'), its hachured ring is ~80-90 m across (not ~130 m), so the drawn ring (277-342 m at 2.634 m/px, centred at raw (240-248,115) -> (-3.5187, 51.0370) = E -218..-239, N +531) is ~3.5x too big and 554-582 m N-NW (N23-25W) of the real one - on a small hachured wood hill. The 160 '~2x / 535-576 m' survives as a range (540-576 -> 554-582), the direction and the verdict are unchanged. Extra independent check: the plate's own 'SCALE OF FEET 0-300' bar measures ~1.45 m/px vs the fit's 2.634 (1.8x). Distances must be geographic (dx=dlon*111194.9266*cos(lat0), dy=dlat*110900), NOT raw Mercator units (my first pass computed 916 m for the 576 m distance that way).
- Executed the 303 way exactly as 306c did (fit/review.py API, no hand-edited JSON): upsert_item(root,'bury-castle-q5001077',[entry]) with entry = {plan, title, url, pairs (the doc's 8), coarse:false, evidence (from the data/commons/files.jsonl row: rec evidence/1, kind category, checked 2026-10-10, site_cat/file_cat 'Bury Castle, Somerset'), label '1911', cite, ref, size, place_reason '306d audit 2026-10-12: ... Document deleted.'} appended to the existing item (lead n0136_1 kept first, filename unchanged), then deleted data/db/platefits/bury-castle-q5001077.c_de779031cda8a0dc.json, then export(root,'bury-castle-q5001077') (333 open of 346). Only 3 files changed (D doc, M item, M web/data/review.json) - no other site's item touched; the site was already covered for the union check (its item was already open in the page file before the upsert).
- Wrote the 306d block (header + the bury-castle line) into docs/site_flow.md after the 306c block (header is tense-neutral: 17 more lines to come in batches; box 1 ticked - 36 shots re-listed this session).
- TESTS (full suite, main checkout, --ignore=tests/test_gate.py, -p no:cacheprovider, with my changes): 10 failed, 130 passed, 1 skipped (251 s). The 10: test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (FAILED at the seed check, dep:null) + 9 that are agent a's in-flight work already on main (test_merge new_sites_are_complete/new_site_golden_samples = 211's open 222-228 gate; src_artists/limes/mackenzie/numancia/wiltshire_stukeley stage+check tests = the 224 family). Baseline in my task file (123/1, 2026-10-12) is STALE - main has since merged 211/223/224/307 work and the suite grew to 141 tests.
- A/B attempt 1 (worktree at HEAD in /tmp/aw306d_ab): INVALID - web/data/sites/ is mostly gitignored (58 tracked files vs 389 site dirs in the main checkout; the per-site web data + data/raw are local build artifacts), so a fresh worktree lacks stonehenge etc. and fails 3 tests deterministically (site_done_line FileNotFoundError '/tmp/aw306d_ab/web/data/sites/stonehenge-q39671', fit_provenance line_refuses_unmarked_non_auto_doc, fit_queue save_runs) that pass in the main checkout; its placement_gestures 'vacuous ERROR' there is also unprovable (no local depictions). PITFALLS candidate: never A/B this project in a bare worktree/checkout - do it in the main checkout with the changed files temporarily at HEAD. (The worktree is still registered; remove it: git worktree remove --force /tmp/aw306d_ab && git worktree prune.)
... (1.9 KB more: `grep -n -A 200 -F '## 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)' DECISIONS.md`)

### 2026-10-13 DRIVER: test suite failing at loop start (1 tests)
    tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    tests/test_fit_queue.py:1749: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    1 failed, 159 passed, 1 skipped in 424.53s (0:07:04)
    (full test output: .agent/reports/last-test-output.txt)
