Status: in-progress
# 209b: Stukeley (1740s) - the Temple Restor'd scan on IA + his Commons plates
Depends on: 200
Touches: fit/src_wiltshire_stukeley.py, data/books/triage/, data/books/lists/, data/commons/files_wiltshire_b.jsonl, data/commons/classified_wiltshire_b.jsonl, docs/lead_wiltshire.md, tests/test_src_wiltshire_stukeley.py, tests/golden/src_wiltshire_stukeley_sample.json

## Goal
Subtask of 209 (the parent's Hand-over has the full mechanics - read it): get Stukeley's
drawings of the Wiltshire sites onto the map. Two legs, both from sources reachable from this
VM: (1) the complete British Museum scan of *Stonehenge, a Temple Restor'd to the British
Druids* (1740), ia=`bim_eighteenth-century_stonehenge-a-temple-rest_stukeley-william_1740`
(BookReader pages + hOCR verified 2026-10-13), indexed with the standard book machinery -
its plates (Stukeley's numbered Stonehenge plan, the Avenue plan, the Wiltshire map) tie to
stonehenge-q39671; (2) the Commons-hosted Stukeley plates (the 205-Kip pattern, no book
machinery) - first the 1740 Avebury plan `File:Houghton Arc 855.214 - Stukely, the Druid
temple of Abury.jpg` (2269x1362, visually verify first - it has no description metadata),
then every other fit-sized (>= 1000 px) Stukeley plate in `Category:William Stukeley` that
shows a catalog site. If the human also delivers *A survey of Wilts* (1740, the true
Wiltshire volume - see the open ask_human in 209a/209c), it is added here as a second
local-copy book.

## Acceptance criteria
- [ ] The BMB 1740 scan is fetched from IA (data/raw/books/bim_eighteenth-century_stonehenge-
      a-temple-rest_stukeley-william_1740/) and triaged with the existing machinery, per-book
      artifacts only (triage/<ia>.*.jsonl, lists/<ia>.json, lists/<ia>.map.json); the shared
      data/books/index.jsonl and validation.json are NOT written.
- [ ] The book's printed plate list is transcribed (the books_lists PLATES pattern, from the
      hOCR; the book is short - check the leaf count from scandata first) and mapped to
      leaves; the stage-A/B recall against that list is recorded in the Stukeley section of
      docs/lead_wiltshire.md (instead of the shared validation.json).
- [ ] Staged rows (appended to the shared-per-suffix staging files, rows tagged with this
      book): files_wiltshire_b.jsonl for every verified site-plan plate - the IA book's
      Stonehenge/Avenue plans (site stonehenge-q39671) and the Commons plates (the 1740
      Avebury plan -> avebury-q661855; the 1722 Stonehenge drawing and any other fit-sized
      verified Stukeley plate -> its site) - each with the 200 evidence field (the book's
      printed list entry for the IA rows; for the Commons rows the hand verification or the
      caption names the place - the specific check recorded on the row) and a classified row
      by hand ("plan"); the work's date (1740/1722) is recorded on the row.
- [x] The existing hand fits are NOT re-staged or re-fitted (the Allcroft fig. 187 Avebury
      fit in data/db/platefits/avebury-q661855.earthworkenglan01allcgoog_n0581_1.json, the
      Allcroft Windmill Hill fit): new rows only.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages/plates are staged, or each missing one is accounted for in
      docs/lead_wiltshire.md.
- [x] Test (no network): the staged files join (every row names an existing or staged site)
      and the evidence check passes; a golden sample of rows
      (tests/golden/src_wiltshire_stukeley_sample.json).

## Notes
- First session: re-baseline the test suite, then VISUALLY verify the Commons candidates by
  downloading them (Commons API `url` field) and looking at them: the Houghton Avebury plan
  (expect Stukeley's 1740 plan of the circle with numbered stones and the Longstones),
  `File:Stonehenge Dessin Stukeley 1722 03547.jpg` (4620x2430, expect the 1722 Itinerarium
  drawing), `File:Stonehenge Stukley Oxford 03543.jpg` (3606x2976, source unverified -
  identify it), and the two unlabeled Flickr files
  `File:47 of 'Stonehenge- plans, descriptions and theories' (11135894643).jpg`
  (2245x2852) / `File:49 of '...' (11133409654).jpg` (4641x2874) - if either is the Petrie
  1880 plan, that finding unblocks 209c (tell the 209c agent / the driver) and the file is
  NOT staged here. Everything else in Category:William Stukeley is <1000 px (too small) or
  not a site drawing (the Clarendon palace ruins 1723 is Roman/medieval - check whether it is
  a catalog site before any staging).
- The Commons leg needs no LLM; only the IA book leg uses the triage stages (ports per the
  parent's mechanics; the book is short, so no long background job expected).
- LLM calls never run in tests (the no_network socket-blocking fixture as in
  tests/test_src_kip.py).

## Hand-over

(2026-10-13, iteration 153, agent a - session 6: IA-leg steps 1-3 DONE (fetch 166/166, triage A
166/166, plate list visually transcribed into STUKLEY_PLATES and committed to the module -
uncommitted at this moment, harness saves it). NEXT = ocrmap, then F/B, then stage the 3 plan rows.)

**What this session did (all in this checkout):**
1. `--fetch`: 166/166 triage pages in ~105 s (IIIF re-encode at 1400 px; log data/books/logs/
   stukeley_fetch.log). `--triage A`: 166/166, 0 errors (log .../stukeley_triageA.log).
   Distribution: text_only 119, other_illustration 41, plate_site_plan 6 (n56, n57, n111, n123,
   n135, n143).
2. `--list` (PLATES was None) printed the hOCR of leaves 0-19: GARBAGE on this BMB scan -
   leaf 0 = the Chyndonath frontispiece portrait (sculpt. I. W. Gucht), leaf 1 = the real title
   page. VISUAL read of leaf 1: "STONEHENGE, A TEMPLE RESTOR'D TO THE BRITISH DRUIDS. By WILLIAM
   STUKELEY, M. D. Rector of All Saints in STAMFORD ... LONDON: M.DCC.XL." (Innys & Manby) ->
   CITE in the module is now confirmed (no more "to be confirmed").
3. Leaves 10-12 are blank/preface: **the book has NO printed list of plates** - the plates' own
   headers are the only list. Visual walk of ALL 47 plate leaves (shrunken scratch copies in
   /tmp/stukeley_small - gone in a fresh checkout; the 1400 px originals remain in
   data/raw/books/bim_.../triage/): every header transcribed into STUKLEY_PLATES (31 lines, 33
   plates). Numbering: I(11), II(15 P2) + II(19/20 P4 - two different plates both labelled II),
   III(24/26 P6 duplicate impressions), V(30/31 P8), VI(35 measures table, no P), VII(39 P12
   faint), VIII(43 P14), IX(47 P16), X(51 P18), XI(56/57 P20), XII(61 P22), XIII(66 P24 view +
   70 P26 section), XIV(74 P28), XV(78 P30), XVI(82/83 P32), XVII(87/88 P34), XVIII(92/93 P36),
   XIX(97/98 P38), XX(102 label cut in scan), [XXI absent], XXII(106/107 P42), XXIII(111 P44 +
   115 P46), [XXIV absent], XXV(119 P48), XXVI(123 P50), XXVII(127 P52), XXVIII(131 P54),
   XXIX(135 P56), XXX(139 P58), XXXI(143 P60), XXXII(147 P62), XXXIIII(151 P64 old-style 34),
   XXXIII(155 P66 + 157 P68 duplicates), XXXV(161 P70 Persepolis - Persia, not Wiltshire).
4. **Site plans found: exactly three** - TAB. XI (the famous numbered plan, fold-out: n56 left
   half rotated 90 deg with the scale bars/the Gate/the Cell; n57 right half with the banner
   "P.20. TAB.XI." - note: I first misread "XL" at 1400 px; the zoom crop reads XI and the
   sequence VII..XII proves it), TAB. XII ("The Orthography of Stonehenge", n61, plan with the
   Avenue), TAB. XXIII ("The Area of Stonehenge", n111, plan with ditch + circle + altar +
   Avenue). **NO Wiltshire map anywhere in this book** (all 166 leaves checked - n117 is text
   p. 47, n32/n67 blank, n163 the INDEX; the map, if it exists at all, is in A survey of
   Wilts, not on IA). No standalone Avenue plan: the Avenue appears in the XXIII area plan and
   in the perspective views (XXV/XXVII/XXIX/XXX). Stage A's plan label was wrong in BOTH
   directions here: n115/n123/n135/n143 are views, and it also calls some near-blank/text
   leaves text_only (civitates pitfall confirmed again).
5. Module edits (committed with this hand-over by the harness; git status will show them):
   docstring corrected (no printed list; hOCR garbage; hand-list pattern), CITE confirmed,
   WHY updated (no map in this book), STUKLEY_PLATES set (the 31-line transcription above).

**State of the world:**
- Commons leg: done (3 rows staged, golden, 7 tests) - unchanged this session.
- IA leg: triage pages + stage A DONE in this checkout; STUKLEY_PLATES set in the module.
  data/books/lists/ has NO stukeley files yet; data/books/triage/ has <ia>.A.jsonl (166 rows);
  data/books/index.jsonl untouched (0 stukeley rows - correct, 211 rebuilds it).
- LLM replicas were up on 127.0.0.1:8080/:8081 at session start (F/B need them).
- Suite last full run (session 5): 111 passed, 1 skipped, 0 failed. This session changed ONLY
  fit/src_wiltshire_stukeley.py (constant + strings) - the 7 existing tests should be
  unaffected (check() still 3/3; golden unchanged) but re-run them first next session.

**Re-read:**
- fit/src_wiltshire_stukeley.py:register - injects books_lists.PLATES[IA] when STUKLEY_PLATES
  is set; list_cmd() then runs books_lists.cmd_ocrmap([KEY]).
- pipeline/books_lists.py:map_plates - anchors by (Qwen numeral + OCR numeral + title
  similarity) with an increasing DP chain; numerals_in SKIPS strings containing "p.\s*\d" -
  stage A stored this book's headers as "P. 20. TAB. XI.", so the Qwen-numeral anchor will
  mostly fail; the title-similarity and OCR anchors carry the mapping. If a kind-s plate
  misses its leaf (esp. XXIII, where n111/n115 tie on area), note it - it only affects the
  map.json attribution, NOT the manual staging.
- pipeline/books.py:cmd_triage_f / cmd_triage_b - verify which pages each targets (F = pages
  A called other_illustration/figure_site_plan; B = plate_site_plan pages) before running.

**NEXT SESSION (runbook, .venv/bin/python; everything resumable):**
1. `.venv/bin/python fit/src_wiltshire_stukeley.py --list` (STUKLEY_PLATES now set) ->
   books_lists.cmd_ocrmap writes data/books/lists/bim_..._1740.json + .map.json ONLY.
   Inspect both: plate count 31 (33 lines? no - 31 lines parsed, duplicates share numerals),
   which leaves got kind-s entries (want XI->n56/57, XII->n61, XXIII->n111).
2. `--triage F` then `--triage B` (needs the live replicas; run_stage exits with its own
   message if no port answers - check `--status` first). Logs: data/books/logs/.
3. Stage the IA-book plan rows into the SAME files_wiltshire_b.jsonl +
   classified_wiltshire_b.jsonl: TAB. XI (fold-out: one row - look how another book's
   fold-out plate is represented in data/books/index.jsonl: id <ia>_n{nnnn}_{k}), TAB. XII
   (n61), TAB. XXIII (n111) - all site stonehenge-q39671, year 1740, cite = CITE, evidence =
   the book's printed list entry (fit/evidence.py check_book/check_book_caption - copy the
   row shape from an existing book row in data/books/index.jsonl). Extend stage()/--check/
   --golden/tests for the book rows (the Commons rows stay exactly as they are).
4. docs/lead_wiltshire.md Stukeley section: record Stage-A/B recall against the hand list
   (replace the "pending the IA leg" line; also state: no Wiltshire map in this scan, Avenue
   only in the XXIII area plan) -> box 2.
5. Tick boxes 1 (fetched+triaged, per-book artifacts only), 2, 3 (book rows staged, date
   1740 on the row), 5 (evidence on every staged row; 3/3 verified plans staged = 100%) as
   they land; full suite each session; when all 6 ticked: Status: done.

**Do not:** write data/books/index.jsonl / validation.json (211); re-stage the two Petrie
files (canonical) or any hand fit; edit pipeline/ (books_lists.py is 217's - in-process
PLATES injection is the sanctioned pattern); run tests with bare python3 (numpy/PIL are
venv-only); bind fixed network ports in tests; git merge/rebase/reset/stash/branch-switch.

**What this session did (committed):**
1. Ran the 7 session-4 tests first: 5 passed, 2 failed - exactly the fragilities the old
   hand-over named, and each needed a different kind of fix:
   - **REAL module bug** in `status()`: it read the cached bookreader.json and indexed
     `p["n"]`, but the raw page dicts have NO "n" key (keys: height/leafNum/pageSide/
     pageType/ppi/uri/width - verified on the real 166-leaf cache) - `books_ia.pages()` is
     what assigns `p["n"] = flat index`. Fixed status() to enumerate the flat pages
     (`triage_path(IA, n)` on the index). The test's fabricated 5-page cache (no n) was
     already correct; the module got the fix, not the test.
   - **TEST bug** in test_canonical_title_clash_fails_loud: pytest 9.1.1's
     `monkeypatch.setitem` is Mapping-only (it calls `dic.get(name)`) and has no list
     support, so `setitem(src.STAGED, 0, ...)` raised AttributeError in the harness, not
     the test. Fixed the test: `setattr(src, "STAGED", [petrie_row] + src.STAGED[1:])`.
   - All 7 pass in 2.2 s.
2. `--status` verified LIVE off the real cached bookreader.json in this checkout:
   "166 leaves, triage 0/166, long side 11408-13537 px" + LLM line - zero network, zero
   triage pages yet (the fetch never ran in any session).
3. docs/lead_wiltshire.md: the "The module is built (iteration 150, checked 2026-10-13)"
   line added after the Commons-candidates table; the "Stage-A/B recall ... pending the
   IA leg" line kept.
4. Task boxes 4 (hand fits untouched - per-task files hold only the 3 new rows, the
   title-only canonical guard tested, data/db/platefits/ never written) and 6 (offline
   join + evidence 3/3 + golden, all green) ticked. Boxes 1/2/3/5 stay open: all need
   the IA book leg.
5. Full suite: **111 passed, 1 skipped, 0 failed** (181 s) = 104 baseline + 7 new, no
   unrelated reds.
6. One commit: module status() fix + test fix + lead-doc line + box ticks + DECISIONS +
   this hand-over (the session-4 files were already committed by the driver's
   defdc54 "uncommitted work" commit, so this commit is small).

**State of the world:**
- Commons leg DONE: data/commons/files_wiltshire_b.jsonl + classified_wiltshire_b.jsonl
  hold the 3 rows (Houghton Avebury TAB. VIII 1743 plan -> avebury-q661855; 1722
  Itinerarium inward view -> stonehenge-q39671; Stukelykitscoty 1722 view ->
  kit-s-coty-house-q4222497), each with caption_coords evidence (the site's own
  coordinates, dist 0.0) and hand classification (plan 1.0 / birdseye 1.0 / birdseye
  1.0); evidence 3/3 offline; golden at tests/golden/src_wiltshire_stukeley_sample.json.
- fit/src_wiltshire_stukeley.py: --fetch/--triage A|F|B delegate to the unmodified
  books machinery (register() adds ONLY the BOOKS entry - no wrap, the book really is
  on IA); --status offline (fixed this session); --list prints the first 20 leaves'
  hOCR while STUKLEY_PLATES is None (the transcription input); STUKLEY_PLATES=None +
  TODO comment (books_lists PLATES format `plate|sub|title|page|kind`, kind s/o/u) -
  when set, register() injects books_lists.PLATES[IA] in-process and --list runs
  books_lists.cmd_ocrmap (writes ONLY per-book lists/<ia>.json + .map.json).
- data/raw/books/bim_eighteenth-century_stonehenge-a-temple-rest_stukeley-william_1740/
  has the cached bookreader.json + metadata.json in THIS checkout (data/raw is
  gitignored: absent in fresh checkouts, but the driver merges main into this branch,
  so if the checkout is rebuilt the --fetch step restores the cache - pages() fetches
  bookreader.json itself on a cache miss).
- LLM replicas: two answer on 127.0.0.1:8080 and :8081 as of this session (books.
  LLM_URLS ports 8080,8081,8082,18080,18081) - the triage stages are runnable right
  now, no setup.

**Re-read:**
- fit/src_wiltshire_stukeley.py:stage - the 8-tuple guard order (canonical title FIRST,
  then catalog drift, then live meta, then size, then named-place, then idempotent
  skip, then date override + keep) - the same shape is needed for the IA-leg rows.
- fit/src_wiltshire_stukeley.py:status - the enumerate fix (raw bookreader pages have
  no "n"; n = flat list index).

**NEXT SESSION (the IA book leg; run everything under .venv/bin/python):**
1. `fit/src_wiltshire_stukeley.py --fetch` - the 166 triage pages (raw pages are huge:
   long side up to 13537 px, so IIIF re-encodes at the triage size; fetch_triage is
   resumable/idempotent - re-running picks up where it stopped). Run in the FOREGROUND
   with a generous timeout (nohup + tail the log if it is slow; ~84 spreads).
2. `fit/src_wiltshire_stukeley.py --triage A` (needs the live replicas; run_stage exits
   with its own message if no port answers). Resumable: data/books/triage/<ia>.A.jsonl.
3. `fit/src_wiltshire_stukeley.py --list` - prints the first 20 leaves' hOCR. Find the
   book's printed LIST OF PLATES (it is short - 166 leaves) and transcribe it into
   STUKLEY_PLATES in the module (format `plate|sub|title|page|kind`, kind s = site
   plan, o = other, u = unsure; also CONFIRM the exact printed title from the hOCR
   title page and correct CITE if it differs - the 1740 book's own plates include the
   numbered Stonehenge plan, the Avenue plan, a Wiltshire map). Commit the transcription.
4. Re-run `--list` (STUKLEY_PLATES set): runs books_lists.cmd_ocrmap -> writes ONLY
   data/books/lists/<ia>.json + .map.json (map stays [] until stage A exists - already
   done by step 2, so the map should populate).
5. `--triage F` and `--triage B` on the flagged pages (stage A's output drives which
   pages F/B look at - see books.run_stage; the F/B jsonl files are resumable).
6. Stage the IA-book rows into the SAME files_wiltshire_b.jsonl (+classified): evidence
   = the book's printed list entry naming the place (a check_book / book-caption-style
   row per the 200 machinery - see how the other books' book rows look in
   data/books/index.jsonl and fit/evidence.py check_book/check_book_caption; date
   1740). Sites: stonehenge-q39671 for the Stonehenge plan + Avenue plan; the
   Wiltshire map - look at what it shows first: if it maps a whole region, record it
   in the lead doc instead of staging it. Add the book rows to the stage()/--check/
   --golden/tests (extend, don't rework - the Commons rows stay exactly as they are).
7. Record the Stage-A/B recall against the printed plate list in the Stukeley section
   of docs/lead_wiltshire.md (replace the "pending the IA leg" line) - box 2.
8. Tick boxes 1 (fetched + triaged, per-book artifacts only - the shared
   data/books/index.jsonl and validation.json are NEVER written by this task, 211
   rebuilds them), 2 (recall recorded), 3 (book rows staged with evidence + the 1740
   date on the row), 5 (evidence passes on every staged row, >=90% of verified
   site-plan pages staged or each missing one accounted for in the lead doc) as they
   land; re-run the full suite each session (last: 111 passed, 1 skipped, 0 failed).
   When all 6 boxes are ticked: Status: done (the driver re-checks).

**Do not:** write the shared data/books/index.jsonl / validation.json (211); re-stage
the two Petrie files (canonical, files.jsonl rows 713/714 - the title-only guard
enforces this in code) or any hand fit (Allcroft Avebury fig. 187, Allcroft Windmill
Hill fig. 186 in data/db/platefits/); edit pipeline/ or other tasks' files (books_
lists.py is 217's - the in-process PLATES injection is the pattern its cmd_ocrmap
comment points at; the hoare/mackenzie/kip src modules are other tasks' files); git
merge/rebase/reset/stash/branch-switch; run tests with bare python3 (numpy/PIL are
venv-only). If the human later delivers *A survey of Wilts* (1740), it joins this
module as a second book via the 209a wrap pattern (note: 209a was DROPPED on the
human's refusal of book downloads - see its Hand-over; the wrap pattern still
applies to any copy that arrives).
