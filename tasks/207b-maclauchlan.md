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
- [ ] The book is fetched from the Internet Archive (data/raw/books/memoirwrittendu00maclgoog/)
      and triaged with the existing machinery, per-book artifacts only
      (triage/memoirwrittendu00maclgoog.*.jsonl, lists/memoirwrittendu00maclgoog.json,
      lists/memoirwrittendu00maclgoog.map.json); the shared data/books/index.jsonl and
      validation.json are NOT written by this subtask.
- [ ] The book's own printed list of plates is transcribed (the books_lists PLATES pattern)
      and mapped to leaves; the stage-A/B recall against that list is recorded in the
      Maclauchlan section of docs/lead_roman.md (instead of the shared validation.json).
- [ ] Staged rows (appended to the parent's shared staging files, rows tagged with this
      book): files_roman.jsonl for every verified site-plan page of a named fort/structure
      tied to a Roman site - an existing catalog site by QID where one exists, or a new
      extras_roman.jsonl entry (kind "roman fort" / "roman site", QID where it exists,
      lon/lat from the book's list or a cross-check) - each with the 200 evidence field
      (list entry, caption, coordinates distance recorded on the row) and a classified row
      by hand ("plan"); the book's date (title-page year, 1857/1858) is recorded on the row.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one (wall sections, sections alone) is
      accounted for in docs/lead_roman.md.
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
(2026-10-14, iteration 131, agent c - the list-leg session, ended by the context limit mid-commit. READ THIS FIRST.)

**What happened this session.**
1. Rewrote `fit/src_roman_maclauchlan.py` to the 207a/Horsley HAND_FIGS pattern (the hand-over item 1, DONE on disk but UNCOMMITTED - the harness saved it; commit it first next session):
   `MACLAUCHLAN_FIGS` 6-line table (78 Brampton s|65, 90 Willow Holm o|76, 93 Carlisle s|76, 111 gateway s|93,
   115 Table of Stations o|97, 129 Binchester tiles o|7; all kind_by hand) injected into `books_lists.HAND_FIGS[IA]` by
   register(); the MACLAUCHLAN_PLATES/PLATES injection and the djvu page_texts swap are GONE; `--list` is now offline
   (register + cmd_ocrmap); docstring/CITE/WHY fully rewritten (Nochlin mislabel, no-list discovery + binder-list
   transcription, 123 corrections, kind decisions). `--djvu` kept (its leafNum = n+1 numbering is the 1:1-aligned
   convention). `IA_LIST` removed.
2. Ran `--list` OFFLINE (socket-blocking wrapper) TWICE: writes only `data/books/lists/memoirwrittendu00maclgoog.json`
   (table dump, ensure_ascii=False; plates=None, figures=6: s3/o3) + `.map.json` (6 leaves; site_plan true for 78/93/111).
   Byte-stable across runs (both files UNCOMMITTED on disk): .json md5 8479d53f196fed1fa2bb0d7159b58257,
   .map.json md5 f6593c9e01c19157daf997e7a03bb04a - verify before committing. No other file touched.
3. **Read the title pages (n0009/n0011/n0012/n0013) from the triage images - NEW date facts for the lead doc and
   CITE (already corrected in the uncommitted module):** the short title (n0009) and the FULL title (n0011) both print
   "...A SURVEY OF THE ROMAN WALL, THROUGH THE COUNTIES OF NORTHUMBERLAND AND CUMBERLAND, IN THE YEARS 1852-1854.";
   the full title adds "MADE BY DIRECTION OF HIS GRACE THE DUKE OF NORTHUMBERLAND, K.G., PATRON OF THE SOCIETY OF
   ANTIQUARIES OF NEWCASTLE-UPON-TYNE. By HENRY MACLAUCHLAN... LONDON: PRINTED FOR PRIVATE CIRCULATION. MDCCCLVIII.";
   the verso (n0012) = "LONDON: BRADBURY AND EVANS, PRINTERS, WHITEFRIARS." (the djvu 'WHITBY' read was OCR garbage);
   the preface (n0013) retitles "BETWEEN THE TYNE AND THE SOLWAY, IN THE YEARS 1852-1854" with the footnote: survey
   commenced at Wallsend summer 1852, to Portgate that year; 1853 to Carvoran; by the winter of 1854 completed to
   Bowness. **The parent's "survey ran 1857-59" is WRONG** (the djvu OCR's "1852-1864" was also a misread). The 1858
   printing does carry later 1857-58 work (Willow Holm section taken Sep't 7th 1858; the Carlisle plan shows the
   1857-58 great sewer) - THAT is the discrepancy the lead doc records. A gift leaf (n0007): "Presented to Professor
   Phillip by the Duke of Northumberland, Alnwick Castle, 17 July 1859". djvu leafNums = n+1, aligned 1:1 (the
   n0011 full title = djvu 12, preface = djvu 14, imprint = djvu 13).
4. **Stage A re-verified (171/0):** n0078 plate_site_plan (cap "BRAMPTO"), n0090 other_illustration (cap the Willow
   Holm title), n0093 plate_site_plan (cap "Sandridge & Co. Litho London"), n0111 figure_site_plan (cap the gateway
   caption), n0115 text_only (cap "TABLE OF STATIONS."), n0129 other_illustration (cap the tile-marks caption).
   So stage-A flagged = {78,93,111} = exactly the table's gt_site set -> the next session's validate_book should
   give recall_pages 3/3 (clean on both strict/lenient, flagged_nonplate = {90,129} as other_illustration, NOT in
   SITE_TYPES). LLM replicas RE-CHECKED today: 8080/8081 up, 8082 down.

**Suite state:** not run this session (list-leg only; the driver's 2026-10-13 baseline 159/1/1 stands - the lone red
is agent a's 307d placement test). No tests reference this book yet (grep of tests/ empty).

**Acceptance boxes:** box 2 is HALF done (list transcribed + mapped to leaves + artifacts on disk; the stage-A/B
recall record in docs/lead_roman.md is still owed to it - together with the 90% accounting, that lands in the
validate step below). Boxes 1,3,4 untouched this session.

**Exact next steps (132+, in order).**
1. **Commit the uncommitted 131 work**: `git add fit/src_roman_maclauchlan.py data/books/lists/memoirwrittendu00maclgoog.json data/books/lists/memoirwrittendu00maclgoog.map.json && git commit -m "207b: list leg to the HAND_FIGS pattern (6-leaf table) - the book has no printed plate list, the binder's instructions are the book's list; the per-book list artifacts"` (md5-check the two list files against the values above first; re-run --list if a byte differs).
2. **`--triage B`** (live, 8080/8081 up - re-check first): cmd_triage_b runs on A's site pages + the list's kind-s
   leaves = {78,93,111}; only n0093's B row (map_box/title) feeds staging, the other two are for the record. If it
   exits "tunnels down", log it and come back next session (nothing else depends on B except the n0093 staging row).
3. **`books_lists.validate_book(KEY)` (offline, after register) -> the NEW "## Maclauchlan" section in
   `docs/lead_roman.md`, inserted BEFORE the "## Roy" section** (807's Horsley section is absent while 807 is
   blocked - if a merge brings it, move my section after it and NEVER edit 807's text). Record: source (1858
   original; the Nochlin mislabel + the lending-restricted 2015 Wanney presentation, both unusable), the no-list
   discovery + the binder-list verbatim, the 6-line inventory with per-leaf verdicts, the blank-plate findings
   (n0078, n0111), the unprinted Figs 2/3/5/6 (the 122 size census), the DATE DISCREPANCY (title-page survey
   1852-1854 + imprint MDCCCLVIII 1858 vs the parent's 1857-59; the 1858 printing carries 1857-58 addenda; the
   n0007 gift leaf 1859), the stage-A/B recall numbers, and the 90% accounting (1 staged of 3 verified site plans;
   n0078 and n0111 each accounted for individually as blank in this copy).
4. **Build `--stage`** (read tasks/808-horsley-stage.md in full first for the row-content conventions; the parent's
   Notes: append-only, idempotent, rows tagged memoirwrittendu00maclgoog, --dry previews): creates the three shared
   files (absent on this branch) with the decided rows - extras_roman.jsonl +1 (Luguvallium (Carlisle), Q71551754,
   lon/lat 54.896187/-2.94077, kind "roman fort" SPACE form, region england, place "Carlisle, Cumberland, England",
   location_check per Decision 2); files_roman.jsonl +1 (n0093: site = the new extras id, qid Q71551754, title/desc
   carrying "Carlisle" + the binder's-list entry + the p.77 reference, year 1858, url/thumb the IA page image
   https://archive.org/download/memoirwrittendu00maclgoog/page/n0093.jpg, w/h from the triage row [964,1400], the
   caption_coords evidence of Decision 3: named_place Carlisle, place Q192896 P625 54.894722/-2.936389, dist_m
   324.1); classified_roman.jsonl +1 ((site,title), class "plan" by hand).
5. **`--check` (offline: join staged rows to catalog+extras; fit/evidence.py check over this book's rows) +
   `--golden` (tests/golden/src_roman_maclauchlan_sample.json) + tests/test_src_roman_maclauchlan.py** (the
   no_network socket-blocking fixture as in tests/test_src_van_deventer.py - monkeypatch socket.socket/
   create_connection/getaddrinfo; no LLM calls in tests; no fixed ports; writes only inside the project). Then run
   the suite (baseline 159/1/1; my tests must all pass, the lone 307d red stays) and re-baseline in the notes.

**Re-read next session:** `fit/src_roman_maclauchlan.py` (freshly rewritten; MACLAUCHLAN_FIGS + the docstring);
`tasks/808-horsley-stage.md` (in full - the row-content conventions for --stage); `data/commons/files.jsonl`
(the row shape); `data/catalog/extras.jsonl` (a no-QID row for the location_check field shape); `fit/evidence.py`
(check_commons/check_caption - re-read with fresh eyes before wiring --check); the djvu text is cached at
data/raw/books/memoirwrittendu00maclgoog/memoirwrittendu00maclgoog_djvu.xml (leafNums = n+1); the title pages are
triage images n0009/n0011/n0012/n0013 (read above).

---

(2026-10-14, iteration 130, agent c - the kind-decision session. Read djvu leaves 93-99 (printed pp.76-80)
verbatim, re-verified the catalog (Housesteads now HAS a row), verified Q71551754 via the Wikidata API,
filed the two drafted PITFALLS entries. No code written this session; no tests run - the suite stands at
the driver's 2026-10-13 baseline: 159 passed / 1 failed (agent a's 307d test_fit_queue placement test) /
1 skipped. The 122/123 Findings 1-6 all still stand; the open call (n0093 kind) is now DECIDED below.)

**State (verified on this branch this session).**
- `fit/src_roman_maclauchlan.py` (240 lines): register/fetch/status/triage/djvu/list legs built;
  `MACLAUCHLAN_PLATES = None`; --stage/--check/--golden NOT built. The docstring is STALE in two
  places (123): it still claims the list source is the 1971 reprint's hOCR (Finding 1: that item is
  Linda Nochlin's *Realism*) and it still describes a djvu page_texts swap in --list (there is no hOCR
  page index; the list leg goes to the HAND_FIGS pattern instead).
- Stage A done: 171 rows / 0 errors in `data/books/triage/memoirwrittendu00maclgoog.A.jsonl` (row:
  {n, leaf, out:{page_type, numbers, caption}, parse, s, img_size}; n = 0-based triage index =
  bookreader flat index; leaf = n+1). No stage F/B. No `data/books/lists/memoirwrittendu00maclgoog.*`.
  NO roman staging files exist yet (files_roman/classified_roman/extras_roman absent, re-verified
  today; 808 is blocked on 807, so 207b creates them - APPEND-ONLY, IDEMPOTENT, rows tagged
  memoirwrittendu00maclgoog). `docs/lead_roman.md` = header + Roy section only (no Horsley or
  Maclauchlan section yet). LLM replicas: 8080/8081 up, 8082 down as of 122 - RE-CHECK before any B run.

**Plate inventory BY EYE - FINAL (122/123, all five small/quarto leaves read; sizes = triage jpg).**
1. **n0078 (leaf 79, FIG. 1, "BRAMPTO.")** - kind s, the Brampton camp plan (p.65; book p.64: "about
   3 furlongs from the river Irthing ... 120 yards east and west, and about 60 yards north and south";
   p.65 heading "BRAMPTON. - DOUBTFUL POSITION OF ABALLAVA"). **BLANK in this copy** (frame, compass,
   labels and scale bar survive; the drawing faded). Tie (if it were legible): Q17659606 "Brampton Old
   Church Roman fort and the medieval Church of St Martin" (54.9457/-2.76676) - the book's anchor IS
   Brampton Old Church; note the book calls it the doubtful Aballava while the catalog's Aballava is
   Burgh by Sands (Q17675704). NOT STAGED (blank) - accounted for in the lead doc.
2. **n0090 (leaf 91, Willow Holm)** - kind o, never staged (parent Notes). Legible: "Plan, Section, and
   Elevation of the Roman Wall, in Willow Holm, Carlisle", "440 Yards from the West mouth of the
   Sewer", "Scale, 4 Feet to an Inch", "Reduced from M'Me Kie's Section, taken Sep't 7th 1858".
3. **n0093 (leaf 94, FIG. 4) = THE PLAN OF CARLISLE - legible, the ONLY surviving plan in this copy.**
   **Kind DECIDED s this session** (see Decisions 1): a town-scale plan of Carlisle (buildings,
   streets, the "New Sewer" + "Drain", the river, "From Burgh / Trinity Church" and "From WIGTON"
   direction notes, compass, "Scale of Chains" 0-20 + "Scale of Feet" 0-1000, "H M^L delin",
   "Sandridge & Co. Litho London") showing the course of the Wall and the Vallum between Stanwix and
   the Castle plus the 1857-58 great sewer. Text: p.76 "Carlisle. The Castle. The great sewer.";
   p.77 "CARLISLE, COURSE OF THE WALL AND OF THE YALLUM." ending "(See Plans, Fig. 4.)"; the binder's
   list (djvu leaf 119): "The Plans, Fig. 4, 6, Carlisle and the Camp on Skew Hill at page 76."
   **THE row to stage** (Decisions 2-4): new extras_roman site "Luguvallium (Carlisle)" Q71551754.
4. **n0111 (leaf 112) = printed p.93 "GATEWAY RECENTLY DISCOVERED NEAR HOUSESTEADS."** - a quarto text
   page (964x1400), not a plate leaf, with an INLINE figure (NORTH heading, small figure, scale 0-20,
   caption "Gateway discovered near Housesteads (Borcovicus) in 1856."). Discovered 1856 by Clayton in
   the Knag Burn valley, 371 ft east of the station of Borcovicus (PPSA proc. vol i p.186).
   **BLANK in this copy** (123: 3x zoom shows only a faint frame). Kind s in intent; NOT STAGED
   (blank) - accounted for. Catalog (re-verified today): **Q17677378** "Housesteads fort, section of
   Wall and vallum..." (sites.jsonl:4686; members Q1812832 "Housesteads Roman Fort" 55.013/-2.331;
   has_part Q6421716 "Knag Burn Gateway" + Q1812832) - the 123 "no row" finding is STALE (catalog
   grew on main since); no standalone row for Q1812832/Q6421716.
5. **n0115 (leaf 116) = printed p.97 "TABLE OF STATIONS."** - quarto text page (the Notitia/Ravennas/
   Chorographia table, 23 stations). kind o, never staged.
6. **n0129 (leaf 130)** - full-size (890x1400) text p.7 of the Watling Street memoir with an inline
   figure: two boxed Roman tiles with letter-marks, "6 Inches" bar, "MARKS ON ROMAN TILES, BINCHESTER."
   kind o, never staged.
- Djvu alignment (123 correction): djvu leaves and bookreader leaves are ALIGNED 1:1 in this book
  (n0090 = leaf 91 = djvu 91; n0093 = leaf 94 = djvu 94); the 122 "drifts ~1" reading was wrong. Keep
  the safe rule anyway: trust the IMAGES (bookreader leafNum) for plate identity (n0089/n0095 are
  genuine blank leaves).
- **Figures without leaves in this copy:** Fig. 2 (the Mote/Irthington; p.69 "(Plans, Fig. 2.)"),
  Fig. 3 ("&c.", unnamed), Fig. 5/6 (the Camp on Skew Hill, Kirkandrews - p.80 says Fig. 5, the
  binder's list says Fig. 4,6 - OCR ambiguity, same plate). The 122 size census proved no hidden
  full-size plates, so they were never printed in this copy (private-circulation gaps) - record in
  the lead doc; they do NOT count against the 90% box. Only other Maclauchlan on IA:
  `henrymaclauchlan0000macl` (2015 Wanney presentation; LCP/ACS lending-restricted) - optional
  cross-check, don't block on it.

**Decisions (this session - full reasoning in the 2026-10-14 DECISIONS entry).**
1. n0093 kind = **s** (a plan of a named place, Carlisle: the Wall + Vallum course and the sewer -
   NOT a wall-course section; that is n0090).
2. Site tie for n0093 = **NEW extras_roman row** "Luguvallium (Carlisle)": qid Q71551754 (verified
   via the Wikidata API: "Luguvallium Legionary Fort - Carlisle", P31 = Q57821 "fortification",
   P131 = Q192896 the city of Carlisle (Latin alias "Luguvallium"), P625 54.896187/-2.94077
   precision 1e-6, VICI 12444), kind "roman fort" (SPACE - the 207a/808 spec), region "england",
   place "Carlisle, Cumberland, England", location_check{Wikidata P625 cross-check, checked
   2026-10-14}. NOT Carlisle Castle Q614836 (kind castle, the plate is the Wall/Vallum course).
   No luguvallium row exists in the catalog (grep confirmed).
3. n0093 row evidence = **caption_coords**: named_place "Carlisle" (in the row's title/desc via the
   binder's-list entry), place Q192896 (P625 54.894722/-2.936389), site = the new extras row,
   dist_m 324.1 (haversine, computed today) -> fit/evidence.py check_commons/check_caption passes
   OFFLINE (named place in norm(title+desc); stored distance reproduces within 1 km; <= 50 km).
4. **Stage n0093 ONLY** (1 of the 3 verified site plans = 33% < 90%; the box is a disjunct and
   n0078/n0111 are each accounted for in the lead doc as "not staged because the drawing does not
   survive in this copy (plate blank)"). n0090/n0115/n0129 are kind o - never staged (parent
   Notes). The 90% box is met via the "or each missing one ... accounted for in docs/lead_roman.md"
   branch, with the specific per-plate reason.
5. Housesteads/Borcovicus: the catalog NOW has Q17677378 (see inventory item 4) - the n0111
   accounting note names it (the 1856 gateway is its documented part Q6421716).

**Exact next steps (131+, in order).**
1. **Rewrite the module's list leg to the HAND_FIGS pattern** (the proven 207a/Horsley shape;
   books_lists confirmed 123: `parse_hand_figures` maps by leaf n with NO OCR; `cmd_ocrmap` writes
   lists/<ia>.json = the table dump (ensure_ascii=False) + .map.json via `list_pages`, needs stage A
   non-empty - it is): `MACLAUCHLAN_FIGS` string, one line per leaf `fig|title|page|kind|kind_by`:
   n0078 (Fig. 1, the Brampton camp plan, p.65, s), n0090 (Willow Holm wall plan/section/elevation,
   p.76, o), n0093 (Fig. 4, the Carlisle plan, p.76, s), n0111 (the 1856 gateway figure, p.93, s),
   n0115 (Table of Stations, p.97, o), n0129 (Binchester tile marks, p.7, o). register() injects
   `books_lists.HAND_FIGS[IA]`; DROP the MACLAUCHLAN_PLATES/PLATES injection and the djvu page_texts
   swap from --list. Rewrite the module docstring fully: the Nochlin finding, the no-list discovery
   (the binder's instructions ARE the book's list - transcribed verbatim in the DECISIONS/PITFALLS
   entries, so the books_lists HAND_FIGS fallback satisfies box 2 the way 207a did), the 123
   corrections (n0111/n0115 quarto text pages; no djvu drift; n0078/n0111 blank in this copy;
   Figs 2/3/5/6 unprinted), and today's kind decision (n0093 = s, the Carlisle plan).
2. **`--list` OFFLINE** (socket-block wrapper, the 807 one-liner pattern: import urllib.request/ssl/
   socket FIRST, patch socket.socket.connect + socket.create_connection to raise, then
   importlib-load the module, h.register(), books_lists.cmd_ocrmap([KEY])) -> commit
   `data/books/lists/memoirwrittendu00maclgoog.json` + `.map.json`.
3. **`books.cmd_triage_b([KEY])` on n0093 ONLY** (re-check replicas 8080/8081/8082 first) for its
   map_box/title; n0078/n0111 need no B (unstaged).
4. **`books_lists.validate_book(KEY)`** (offline after register) -> the stage-A/B recall -> the NEW
   "## Maclauchlan" section in `docs/lead_roman.md`, inserted BEFORE the "## Roy" section (subtask
   order Horsley, Maclauchlan, Roy; 807's Horsley section is absent while 807 is blocked - if it
   appears after a merge, re-order my section after it and NEVER edit 807's text). Record: source
   (the 1858 original; the two unusable IA copies: the Nochlin contamination + the
   lending-restricted 2015 presentation), the no-list discovery + the binder's-list transcription,
   the 6-line inventory with per-leaf verdicts, the blank-plate findings (n0078, n0111), the
   unprinted figures (2/3/5/6), the date discrepancy (title page 1858; the survey ran 1857-59 - the
   book's own front matter), the stage-A/B recall numbers, and the 90% accounting (1 staged of 3
   verified site plans; each missing one accounted for with its specific reason).
5. **Build `--stage`**: create the three shared files (absent on this branch) and append the
   decided rows, 808's schema (read tasks/808-horsley-stage.md in full first; it was read today and
   its Notes carry the row-content conventions): extras_roman.jsonl +1 (the Luguvallium row);
   files_roman.jsonl +1 (n0093: site = the new extras id, qid Q71551754, title/desc carrying
   "Carlisle" + the binder's-list entry + the p.77 reference, year 1858, url/thumb the IA page image
   https://archive.org/download/memoirwrittendu00maclgoog/page/n0093.jpg, w/h from the triage row,
   the caption_coords evidence of Decision 3); classified_roman.jsonl +1 (the (site,title) row,
   class "plan" by hand). Append-only, idempotent (a second run changes no byte), rows tagged
   memoirwrittendu00maclgoog; --dry previews.
6. **`--check`** (offline: join staged rows to catalog+extras - every row names an existing or
   staged site, every new site has its plans; fit/evidence.py check over this book's rows) +
   **`--golden`** (tests/golden/src_roman_maclauchlan_sample.json) +
   **tests/test_src_roman_maclauchlan.py** (the no_network socket-blocking fixture as in
   tests/test_src_van_deventer.py; no LLM calls in tests). Then run the suite and re-baseline
   (driver baseline: 159/1/1).

**Re-read next session:** `fit/src_roman_maclauchlan.py` (240 lines; the list leg to rewrite);
`fit/src_roman_horsley.py` (the exact pattern to copy); `pipeline/books_lists.py` (HAND_FIGS /
parse_hand_figures / cmd_ocrmap / list_pages / validate_book); `data/commons/files.jsonl` (the row
shape); `data/catalog/extras.jsonl` (the no-QID row shape for the location_check field); the djvu
text is cached at data/raw/books/memoirwrittendu00maclgoog/memoirwrittendu00maclgoog_djvu.xml
(pp.76-80 = djvu pages 93-99, re-read above if needed).
