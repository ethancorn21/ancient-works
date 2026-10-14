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
(2026-10-13, iteration 123, agent c - plate-transcription session. ALL candidate plate
images read by eye (triage jpgs are at native size for the quarto leaves: 964x1400; crops
at /tmp/n0078_plate_zoom.jpg, /tmp/n0111_fig_zoom.jpg if /tmp survived). No code written,
no tests run - suite baseline 158 passed / 1 skipped on the merged tree (7e9c829) stands.
The 122 hand-over's Findings 1-3 still stand; 123 REFINES Findings 4/6 (corrections
below) and CHANGES the staging plan. The old 122 "Exact next steps" 1-2 (read the
captions, fix the kinds) are DONE except the n0093 kind decision, which is now step 1
below; steps 3-6 of 122's list survive as steps 3-7 here, corrected. The stale 204-era
"State / Resume recipe" blocks were deleted (all that work is done).)

**State (verified on this branch this session).**
- `fit/src_roman_maclauchlan.py` exists (240 lines): register/fetch/status/triage/djvu/
  list legs built; `MACLAUCHLAN_PLATES = None`; --stage/--check/--golden not built. The
  docstring still claims the 1971-reprint-hOCR list source (WRONG - 122 Finding 1: that
  item is Linda Nochlin's *Realism*) and a djvu page_texts swap in --list (to be
  replaced by the HAND_FIGS injection per step 3 below).
- 1858 original `memoirwrittendu00maclgoog`: all 171 triage pages fetched (gitignored);
  stage A done: 171 rows / 0 errors in
  `data/books/triage/memoirwrittendu00maclgoog.A.jsonl` (row: {n, leaf, out:{page_type,
  numbers, caption}, parse, s, img_size}; n = 0-based triage-file index = bookreader
  flat index; leaf = n+1). Flags: n0078 plate_site_plan "BRAMPTO", n0090
  other_illustration (Willow Holm), n0093 plate_site_plan "FIG. 4 / Sandridge & Co.
  Litho London", n0111 figure_site_plan (Housesteads gateway caption), n0115 text_only
  "TABLE OF STATIONS", n0129 other_illustration ("MARKS ON ROMAN TILES, BINCHESTER").
  No stage F/B; no `data/books/lists/memoirwrittendu00maclgoog.*`; NO roman staging
  files exist yet (files_roman/classified_roman/extras_roman absent - 808 may create
  them for Horsley first; either way APPEND ONLY). `docs/lead_roman.md` = header + Roy
  section only (no Horsley or Maclauchlan section yet; 807 blocked on 207a's list
  correction). LLM replicas 8080/8081 up, 8082 down (122; re-check before any B run).

**Plate inventory BY EYE - FINAL (123; all five small leaves + n0129 read).**
1. **n0078 (leaf 79, FIG. 1, "BRAMPTO.")** - the plate frame, compass rose, "BRAMPTO."
   label and "Scale of Feet" bar (0..1000) + "Sandridge & Co. Litho London / H M^L
   delin" survive; **the fort plan itself is BLANK in this copy (faded)** - no drawing.
   Sits between printed pp.64/65; the book's own plate list (below) sends "Fig. 1, 2,
   3, and 6, showing the Mote, Brampton, &c." to page 65, and p.66 refers to it "(See
   the accompanying Plans, Fig. 1.)". p.64 text: the camp "about 3 furlongs from the
   river Irthing, and about 3 1/2 furlongs south-east of Brampton Old Church; ... 1 mile
   3 1/2 furlongs south of Petriana; ... 120 yards east and west, and about 60 yards
   north and south" (heading on p.65: "BRAMPTON. - DOUBTFUL POSITION OF ABALLAVA").
   **Tie found: catalog site Q17659606 "Brampton Old Church Roman fort and the
   medieval Church of St Martin" (id brampton-old-church-roman-fort-and-the-m-q17659606,
   lon -2.76676 lat 54.9457, parish Brampton, Cumberland, roman_fort, part_of
   Hadrian's Wall)** - the book's camp anchor IS Brampton Old Church; the book calls
   it the doubtful Aballava while the catalog's Aballava is Burgh by Sands (Q17675704,
   alias "Aballava") - note the question on the row and in the lead doc.
2. **n0090 (leaf 91, Willow Holm)** - legible (122 read it): elevation + transverse
   section of the wall, "440 Yards from the West mouth of the Sewer", "Scale, 4 Feet to
   an Inch", "Reduced from M'Me Kie's Section, taken Sep't 7th 1858". **kind o (wall
   section) - never staged** (parent Notes).
3. **n0093 (leaf 94, FIG. 4) = THE PLAN OF CARLISLE - legible, the ONLY surviving plan
   in this copy.** Read by eye: the river "Calderv" (the Calderv of CARLISLE - not
   Wigton; the earlier "Wigton plan" guess in the 122 notes is wrong), the town's
   buildings and streets (a "Tindale Street"-type label), an "E" label, a "New Sewer"
   and "Drain" line upper-right (the 1857-58 Carlisle great sewer Maclauchlan
   surveyed), "From Burgh / Trinity Church" and "From WIGTON" direction notes
   lower-left, compass upper-right, "Scale of Chains" (0-20) + "Scale of Feet"
   (0-1000), "H M^L delin", "Sandridge & Co. Litho London". Provenance: **djvu leaf
   119 holds the book's own plate list, "DIRECTIONS TO THE BINDER"**: "The Plans, Fig.
   1, 2, 3, and 6, showing the Mote, Brampton, &c., to be inserted at page 65. The
   Plans, &c. of the Roman Wall in Willow Holm, at page 76. The Plans, Fig. 4, 6,
   Carlisle and the Camp on Skew Hill at page 76. THE END. [B]RADBURY AND EVANS,
   PR[IN]TERS, WHIT[E]FRIARS..." (raw OCR: OLADfiURY AND EVANS, PR1MTEB8, WHITBFBIABS).
   p.80 (djvu leaf 99) refers "(See the accompanying Plans, Fig. 5.)" for the
   Kirkandrews/Skew Hill camp. Surrounding text (djvu leaves 93/96 = printed pp.76/77:
   "The great sewer", "CARLISLE, COURSE OF THE WALL AND OF THE YALLUM") matches the
   drawing. **KIND DECISION PENDING (the one open call)**: s (a plan of a named place,
   Carlisle, showing the wall/vallum crossing + the sewer) vs o (a wall-segment plan
   like Horsley N.11 - though unlike Horsley N.1-N.10, which WERE staged kind-s maps).
   The binder's list names the PLACE ("Carlisle"), which leans s; it is also the only
   surviving legible plan in the book and GOAL point 4 wants the wall's plans on the
   map. **Recommended default: kind s** unless a full read of pp.76-80 proves the text
   presents it as a mere wall-course section. If s: the site tie is the weakest of the
   book - the book's "supposed station at Carlisle" is unproven and the catalog has
   Carlisle Castle (Q614836, extras.jsonl, kind castle - NOT a roman site); likely a
   NEW extras_roman row "Carlisle (supposed Roman station; Wall and Vallum crossing)"
   kind "roman site" no-QID, lon/lat ~(-2.94, 54.90) cross-checked; evidence = the
   caption naming Carlisle (caption_coords) - check score >= 0.75 and runner-up margin
   >= 0.15 against the CURRENT catalog (fit/evidence.py check_book_caption, read in
   full 123).
4. **n0111 (leaf 112) is NOT a plate leaf: it is printed page 93, "GATEWAY RECENTLY
   DISCOVERED NEAR HOUSESTEADS."** (on a quarto-sized sheet - that is why its leaf is
   964x1400 wide) with an INLINE figure: "NORTH." heading, a small (now BLANK/faded -
   3x zoom shows only a faint frame) figure, scale bar 0-20, caption "Gateway
   discovered near Housesteads (Borcovicus) in 1856." Text: discovered in 1856 by Mr.
   Clayton, "in the valley of the Knag Burn, 371 feet east of the station of
   Borcovicus", ground-plan communicated to the Society of Antiquaries (Proc. vol i
   p.186). **The figure drawing is blank in this copy - same fading as n0078.** Kind s
   in intent (a plan of a named structure at Housesteads/Borcovicus), but with no
   visible drawing. **Catalog: 123's grep found NO housesteads/borcovicus row in
   sites.jsonl or extras.jsonl - the 122 "existing QID row" claim is unverified,
   re-grep next session** (if absent: new extras_roman row "Borcovicus (Housesteads)",
   roman fort, with its Wikidata QID if it resolves, lon/lat ~(-2.48, 54.99)
   cross-checked).
5. **n0115 (leaf 116) is NOT a plate leaf: printed page 97, "TABLE OF STATIONS."**
   (quarto sheet: the Notitia Imperii / Ravennas / Chorographia table, 23 stations,
   with the Aballava/Pontesell-Borcovicus-Bremiennaeao note). kind o, never staged.
6. **n0129 (leaf 130)** - full-size (890x1400) text page 7 of the Watling Street
   memoir ("WATLING STREET, DURHAM AND NORTHUMBERLAND. 7") with an inline
   illustration: two boxed Roman tiles with letter-marks, "6 Inches" scale bar,
   caption "MARKS ON ROMAN TILES, BINCHESTER." kind o, never staged.
- **CORRECTION to 122 Finding 4's "djvu drifts ~1" claim**: 123's direct dump of the
  cached djvu.xml shows djvu leaf 89 = p.74, 90 = blank, 91 = the Willow Holm caption
  OCR (garbled), 92 = p.75 (STANWIX), 93 = p.76, 94 = the FIG. 4 plate (garbled),
  95 = blank, 96 = p.77 - i.e. djvu leaves and bookreader leaves are ALIGNED 1:1 here
  (the plate text sits on the plate's own leaf: n0090 = leaf 91 = djvu 91; n0093 =
  leaf 94 = djvu 94). 122's drift reading was wrong. **Keep the safe rule anyway: for
  this book trust the IMAGES (bookreader leafNum) for plate identity** - two leaves
  (n0089, n0095) are genuine blanks that a text-based mapping could misassign.
- **Figures without leaves in this copy** (binder's list minus the five leaves): Fig. 2
  (the Mote/Irthington Thuadlus; p.69 "(Plans, Fig. 2.)"), Fig. 3 ("&c.", unnamed),
  Fig. 5/6 (the Camp on Skew Hill, Kirkandrews; p.80 says "Fig. 5", the binder's list
  says "Fig. 4, 6" - OCR ambiguity, same plate), i.e. 2-3 more unprinted figures. The
  size census (122) proved there are no hidden full-size plates, so these were never
  printed in this copy (private-circulation printing gaps) - record in the lead doc;
  they do not count against the 90% box.
- **Only other Maclauchlan on IA** (122): `henrymaclauchlan0000macl` (2015 Wanney
  presentation of the Watling Street memoir; LCP/ACS lending-restricted) - optional
  cross-check for the Watling Street memoir only; don't block on it.

**The 90% box recomputed with the 123 facts.** "Verified site-plan pages of a named
fort/structure" = n0078 (Fig. 1 Brampton - kind s, BLANK in this copy), n0093 (Fig. 4
Carlisle - kind s recommended, legible), n0111 (gateway figure at Housesteads - kind s
in intent, BLANK in this copy). n0090/n0115/n0129 = kind o (wall section, table,
tiles) - never staged, accounted for by the parent Notes. The evidence contract
(fit/evidence.py, read in full 123): `check` FAILs only on rows whose recorded tie no
longer re-verifies; a kind "none" row is reported, never a failure. Note
`check_book` FAILs a books/index.jsonl book row with kind "hand_tied" ("no
hand-checked table for book rows yet") - such a row must be caption_coords or none.
The files_roman.jsonl staging rows are NOT books/index.jsonl rows (211 converts them
at consolidation); 808/809 (Horsley, both blocked on 807) set the precedent for their
shape: 808's schema = site/qid/title/year/wd_plan/cat/url/thumb/w/h/mime/date/desc/
evidence, one row per kind-s leaf, tagged per book; 809's --check runs
fit/evidence.py over the staged rows and the tests are no-network. DECIDE in 124 how
many of {n0078, n0093, n0111} get rows given n0078/n0111 are blank images:
recommended = stage n0093 (the one legible plan) and ACCOUNT FOR n0078/n0111 in the
lead doc (blank-in-this-copy, kind s, not staged because the drawing does not survive
- the honest reading of the task box "each missing one ... accounted for in
docs/lead_roman.md"); optionally also stage n0078 with an explicit "plate blank in
this copy" note IF the check can pass it (a caption tie to Q17659606 would, distance
~220-350 m < 50 km) - a row for a blank plate is low value, so the recommendation
stays: stage n0093 only, account for the other two.

**Exact next steps (124, in order).**
1. Decide the n0093 kind: read djvu leaves 93-97 (printed pp.76-80; the text was
   dumped in 123's DECISIONS entry, cached file data/raw/books/
   memoirwrittendu00maclgoog/memoirwrittendu00maclgoog_djvu.xml). Confirm s (place
   plan of Carlisle with the wall/vallum + sewer) vs o (wall-course section). If s:
   settle the site tie (new extras_roman "Carlisle (supposed Roman station)" vs
   tying to Carlisle Castle Q614836 vs another catalog row - grep the catalog for
   carlisle roman rows first) and the evidence kind (caption_coords via "Carlisle"
   in the caption, or an honest none-with-reason).
2. Re-verify Housesteads/Borcovicus in the catalog: `grep -in "housestead\|borcovic"
   data/catalog/sites.jsonl data/catalog/extras.jsonl data/books/index.jsonl
   web/data/sites.json`; 123's grep found no row. If absent, the n0111 row (if
   staged at all) gets a new extras_roman row with the Wikidata QID (verify online)
   + cross-checked lon/lat. DECIDE whether a BLANK figure gets a row at all
   (recommended: no - account for it, as for n0078).
3. Rewrite the module's list leg to the HAND_FIGS pattern (the proven 207a/Horsley
   shape; books_lists confirmed 123: `parse_hand_figures` maps by leaf n with NO OCR;
   `cmd_ocrmap` writes lists/<ia>.json = the table dump (ensure_ascii=False) +
   .map.json via `list_pages` (needs stage_a non-empty - it is)):
   `MACLAUCHLAN_FIGS` string, one line per plate leaf `fig|title|page|kind|kind_by`:
   n0078 (Fig. 1 Brampton plan, p.65, s), n0090 (Willow Holm wall elevation+section,
   p.76, o), n0093 (Fig. 4 Carlisle plan, p.76, s-or-o per step 1), n0111 (gateway
   figure, p.93, s), n0115 (Table of Stations, p.97, o), n0129 (Binchester tile
   marks, p.7, o). register() injects `books_lists.HAND_FIGS[IA]`; DROP the
   MACLAUCHLAN_PLATES/PLATES injection and the djvu page_texts swap from --list.
   Update the module docstring fully: Finding 1 (the "reprint" is Nochlin's Realism),
   Finding 2 (no LIST/PLATES heading; the binder's instructions ARE the book's list -
   transcribed verbatim above, so box 2's "printed list" is satisfied by the binder's
   list + the plates' own printed figure numbers, the books_lists HAND_FIGS
   fallback, same as 207a), the 123 corrections (n0111/n0115 are quarto text pages;
   no djvu drift; n0078/n0111 blank in this copy; Figs 2/3/5/6 unprinted).
4. `--list` OFFLINE (socket-block wrapper, the 807 one-liner pattern: import
   urllib.request, ssl, socket FIRST, patch socket.socket.connect +
   socket.create_connection to raise, then importlib-load the module, h.register(),
   books_lists.cmd_ocrmap([KEY])) -> `data/books/lists/memoirwrittendu00maclgoog.json`
   + `.map.json` (commit both). Then `books.cmd_triage_b([KEY])` on the kind-s leaves
   only (8080/8081 up per 122; re-check first) if any kind-s leaf still needs its
   map_box/title for staging (n0093 does if it is s; n0078/n0111 need no B if
   unstaged).
5. `books_lists.validate_book(KEY)` (offline after register) -> the stage-A/B recall
   -> NEW "## Maclauchlan" section in `docs/lead_roman.md`, inserted BEFORE the "##
   Roy" section (in subtask order Horsley, Maclauchlan, Roy; 807's Horsley section
   lands in the same file but 807 is blocked - if its section is absent, put the
   Maclauchlan section between the lead's header and Roy and leave a note for 807 to
   order its own section first; NEVER edit 807's text if it appears). Record: source
   (the 1858 original; the two unusable IA copies: Nochlin contamination + the
   lending-restricted 2015 presentation), the no-list discovery + the binder's-list
   transcription, the 6-line inventory with per-leaf verdicts, the blank-plate
   findings (n0078, n0111), the unprinted figures, the date discrepancy (title page
   1858; survey ran 1857-59 - the book's own front matter), the stage-A/B recall
   numbers, and the 90% accounting (staged vs accounted-for).
6. Stage the decided rows into the shared files - 808's schema (READ 808's task file
   in full first; it is blocked on 807, so the files may not exist yet - 808's Notes
   say 207b may create them in parallel: APPEND-ONLY, IDEMPOTENT, tag every row with
   this book's key, never rewrite other rows; if Horsley rows land after a merge,
   re-run --stage to stay consistent). Row evidence: record_book_row-style
   caption_coords (re-derivable offline) or an honest none-with-reason; check must
   not FAIL. Book date 1858 on every row (the survey 1857-59 goes in the lead doc).
7. `--check` (offline: join staged rows to catalog+extras - every row names an
   existing or staged site, every new site has its plans; fit/evidence.py check over
   this book's rows) + `--golden` (tests/golden/src_roman_maclauchlan_sample.json) +
   `tests/test_src_roman_maclauchlan.py` (the no_network socket-blocking fixture as in
   tests/test_src_van_deventer.py; no LLM calls in tests). Re-baseline the suite
   (158/1 at 7e9c829; the known lone red at times = agent a's 307d placement test).

**Re-read next session:** `fit/src_roman_horsley.py` (the exact pattern to copy - read
in full 123); `tasks/808-horsley-stage.md` + `tasks/809-horsley-check.md` (the roman
row schema, append-only/idempotency rules, and the --check/--golden/test shape 809
will set as precedent - 123 read 808 fully but NOT 809's body); `fit/evidence.py`
(read in full 123: check_book FAILs hand_tied book rows; check_book_caption re-
derives books_match offline, score >= 0.75 + runner-up margin >= 0.15; NONE never
fails; catalog_map = sites.jsonl + extras.jsonl); `pipeline/books_lists.py`
(cmd_ocrmap/list_pages/parse_hand_figures - read in full 123); `data/catalog/
sites.jsonl` (Q17659606 = the Brampton tie, verified 123; NO housesteads row found -
re-verify) + `data/catalog/extras.jsonl` (Carlisle Castle Q614836 kind castle;
vindolanda no-QID extra); djvu leaves 93-97 from the cached
data/raw/books/memoirwrittendu00maclgoog/memoirwrittendu00maclgoog_djvu.xml (the
pp.76-80 text around the Carlisle plan).

**PITFALLS to add** (merge into the 122-drafted entries once the steps settle):
(a) `memoirwrittendur0000henr` = Linda Nochlin's *Realism* (1971), NOT the Maclauchlan
reprint - IA item title/content mismatch (item re-scanned 2024-01-31); never use it.
(b) Maclauchlan 1858 original (memoirwrittendu00maclgoog): no printed plate list -
the book's list is the DIRECTIONS TO THE BINDER on djvu leaf 119; exactly five
small-format (985x1431) leaves n0078/n0090/n009