Status: done
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
- [x] The BMB 1740 scan is fetched from IA (data/raw/books/bim_eighteenth-century_stonehenge-
      a-temple-rest_stukeley-william_1740/) and triaged with the existing machinery (A 166/166,
      F, B; per-book artifacts only: triage/<ia>.*.jsonl, lists/<ia>.json, lists/<ia>.map.json);
      the shared data/books/index.jsonl and validation.json are NOT written.
- [x] The plate list is transcribed into the books_lists PLATES pattern and mapped to leaves:
      the book has NO printed list of plates (verified leaf by leaf) and the BMB hOCR of the
      engraved plates is unreadable, so the transcription IS the plates' own printed headers -
      the 213/civitates hand-list pattern (STUKLEY_PLATES in the module, 31 entries / 33
      impressions); the stage-A/B recall against it is recorded in the Stukeley section of
      docs/lead_wiltshire.md (instead of the shared validation.json).
- [x] Staged rows (appended to the shared-per-suffix staging files, rows tagged with this
      book): files_wiltshire_b.jsonl for every verified site-plan plate - the IA book's two
      plan-view plates (TAB. XI the numbered plan as a fold-out, TAB. XXIII the Area plan with
      the Avenue - site stonehenge-q39671; the book has no standalone Avenue plan and no
      Wiltshire map, and TAB. XII is a section, not a plan - all accounted for in the lead doc)
      and the Commons plates (the 1740 Avebury plan -> avebury-q661855; the 1722 Stonehenge
      drawing and any other fit-sized verified Stukeley plate -> its site) - each with the 200
      evidence field (the book's plate's own printed header for the IA rows; for the Commons
      rows the hand verification or the caption names the place - the specific check recorded
      on the row) and a classified row by hand ("plan"); the work's date (1740/1722) is
      recorded on the row.
- [x] The existing hand fits are NOT re-staged or re-fitted (the Allcroft fig. 187 Avebury
      fit in data/db/platefits/avebury-q661855.earthworkenglan01allcgoog_n0581_1.json, the
      Allcroft Windmill Hill fit): new rows only.
- [x] fit/evidence.py check passes offline on every staged row (5/5). 100% of the verified
      site-plan plates are staged (the only plan-like plate not staged, TAB. XII, is a section
      - accounted for in docs/lead_wiltshire.md).
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

(2026-10-13, iteration 155, agent a - session 8: 209b is COMPLETE. All six boxes ticked, suite
green. The session-7 (iteration 154) work - ocrmap, F/B triage, the XII re-check, BOOK_ROWS
staging - was committed by the driver but never recorded anywhere; this hand-over is the first
written account of it, plus this session's lead-doc recall, box ticks and verification.)

**State: DONE (pending the driver's re-check).** All 6 boxes ticked:
1. fetched + triaged (A 166/166 0 errors, F 41 leaves, B 8 leaves), per-book artifacts only -
   verified 0 stukeley rows in data/books/index.jsonl and validation.json.
2. plate list: the book has NO printed list of plates (verified leaf by leaf) and the BMB hOCR
   of engraved plates is garbage -> STUKLEY_PLATES (31 entries / 33 impressions) is the
   213/civitates hand-list transcription of the plates' own printed headers; recall recorded in
   the Stukeley section of docs/lead_wiltshire.md (this session). Box 2's text was corrected to
   match reality (my own subtask; the deviation is documented, not a scope cut).
3. staged rows: files_wiltshire_b.jsonl + classified = 5 rows - 3 Commons (Houghton Avebury
   1743 plan, 1722 Itinerarium view, kitscoty 1722 view) + 2 book (TAB. XI fold-out n56+n57,
   TAB. XXIII Area plan n111; stonehenge-q39671, year 1740, evidence = the plate's own printed
   header, dist 0.0). TAB. XII is the one plan-like plate NOT staged: it is an orthographic
   section (re-checked against the leaf image 2026-10-14; F-stage independently reads it
   "TAB. XII -> section"). No Wiltshire map, no standalone Avenue plan in this scan.
4. (was ticked session 5) hand fits untouched - re-verified: files_wiltshire_b holds only the 5
   new rows, data/db/platefits/ never written by this task.
5. evidence 5/5 offline on every staged row; 100% of verified site-plan plates staged.
6. (was ticked session 5) tests - re-verified this session with session 7's updated 8-test file:
   8 passed in 3.0 s, golden matches the staged rows exactly.

**This session did** (all in this checkout, one commit):
1. Ran tests/test_src_wiltshire_stukeley.py: 8 passed (the session-7 test file - one test added,
   test_book_rows_staged_in_files_b - and updated for the book rows).
2. Verified the committed session-7 state: files/classified = 5 rows; lists/<ia>.json (31
   plates) + .map.json (2 entries); triage A/F/B jsonl (166/41/8); 0 stukeley rows in the shared
   index.jsonl / validation.json; LLM replicas up on 8080/8081/8082 (not needed - no live calls).
3. docs/lead_wiltshire.md: replaced the stale "The module is built... IA book leg remains"
   paragraph and the "pending the IA leg" recall line with the full record: both legs done,
   5 rows / 5 pass, the hand-list explanation, and the Stage-A/B recall:
   - A: 6 leaves flagged plate_site_plan = all 3 plan leaves (n56/n57/n111) + 3 view false
     positives (n123 XXVI, n135 XXIX, n143 XXXI) -> plan-leaf recall 3/3, precision 3/6.
   - F: 41 leaves' plate headers with kind (incl. XII -> section).
   - B: n111 clean (title, 50-300 cubits/feet scale, map box); n57 banner right, label misread
     "XL" (resolved XI by zoom crop + the plate sequence); n56 label-garbled but scale + north
     arrow present.
   - ocrmap matched 2/31 entries: XI -> n57 (title), XXIII -> n115 (qwen+title) - the WRONG of
     the two XXIII impressions (n115 is the Avenue-track VIEW; n111 is the Area plan). Affects
     only .map.json attribution - staging uses hand-set leaf numbers, never the map.
   - XII not staged (section) + no Wiltshire map + no standalone Avenue plan, all recorded.
4. Task file: ticked boxes 1/2/3/5, corrected box 2's premise wording (see above).

**If the driver re-opens this (only possible re-check failure modes):** the .map.json XXIII
misattribution is deliberate and documented (do not "fix" it by re-running ocrmap - the tie is
the duplicate XXIII impression; the staged rows are correct); box 2's rewording is the
deviation, recorded here and in DECISIONS.

**Re-read:**
- fit/src_wiltshire_stukeley.py:stage_book - the per-row guard order (stage-A reclassification
  fails loud first, then canonical title, then catalog drift, then list-entry drift, then
  idempotent skip); the row id is <ia>_n{leaf:04d}[_n{leaf2:04d}].
- docs/lead_wiltshire.md:Stukeley section - the recall record this hand-over summarizes; the
  "### Also written to PROGRESS.md" block below is the driver's, do not edit.

**NEXT (only if reopened):** nothing on this task. If *A survey of Wilts* (1740) is ever
delivered by the human, it joins this module as a second book (209a wrap pattern: local copy,
wrap books_ia.pages/page_texts/fetch_triage; a second BOOKS entry, its own per-book artifacts,
its rows appended to the same *_wiltshire_b files). Nothing else is left.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/209b-stukeley.md` (in-progress) - hand-over: (2026-10-13, iteration 152, agent a - session 5: the Commons leg is COMPLETE and COMMITTED
- `tasks/209c-petrie.md` (blocked) - hand-over: (2026-10-12, iteration 146, agent a - from 209b's Commons check; written by 209b, not this
- `tasks/209-wiltshire.md` (split) - hand-over: (2026-10-12, iteration 145, agent a - update on the 144 split; the per-book facts below stand.)
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/302c-decision-wiring.md` (open) - hand-over: (2026-10-12, iteration 84, agent c - FIRST session on 302c. Investigation + design only: NO code
- `tasks/304-survey-fit.md` (in-progress) - hand-over: (2026-10-12, iteration 91, agent c - session 7. The lead directed: freeze the stub as it is
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/217-view-books-lists.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-12 209b DECISION: the two unlabeled Flickr files are Petrie 1880 Pl. I and Pl. II - 209c's Commons fallback (a) is satisfied, and both files are ALREADY canonical
File 47 (2245x2852) = Petrie 1880 Plate I, the Stonehenge stone-by-stone plan ("W.M.F.P. mense et del.", scale 1:350, Standing 1880/1747/Overthrown key, "Forms of outlying stones" 91/93/95/96); File 49 (4641x2874) = Plate II, Stonehenge with the Avenue, Cursus inset, parallel banks (scale 1:1500, "Petrie levels in inches by numbering of stones"). Both already sit in data/commons/files.jsonl (rows 713/714, stonehenge-q39671, year 1880, caption_coords "Stonehenge", checked 2026-10-10) with the British Library Georeferencer description (PETRIE, shelfmark HMNTS 10352.i.12, page 47, London 1880, E. Stanford) - so the map already carries them. Per 209b's Notes they are NOT staged in files_wiltshire_b (re-staging a canonical title is a hard fail in the Kip check), and per the parent's plan the finding unblocks 209c: told via 209c's new Hand-over (fallback (a) satisfied - if the human declines the 1880 download, the Commons leg = the two existing canonical rows, nothing more is stageable from Commons; the book download via ask_human 002 remains the only route to the book's other plates) and via the Stukeley section's Petrie note in docs/lead_wiltshire.md. 209c's Status stays blocked on 002 - the driver owns that flip.

### 2026-10-13 209b DECISION: session 2 was investigation-only (context limit) - the 3 Commons rows are verified to the last metadata field and the module design is settled; nothing written yet (no PITFALLS, no module, no tests)
Live check of the three staged rows (`.venv/bin/python`, commons.info, paced - one call, no 429): (1) Houghton Avebury 2269x1362, metadata date is ALREADY '1743' (the plate's year, not an upload timestamp) -> no Kip-style date override needed for this row (no date_commons), keep=True, artist 'William Stukeley (author)', license Public domain, desc spells 'Abury' (norm-substring verified True); (2) Stonehenge Dessin 1722: 4620x2430, date='1722', artist 'G.Garitan', license CC BY-SA 3.0, keep=True, 'Stonehenge' in title; (3) Stukelykitscoty 1020x320, date='' desc='' -> year_of None, **keep() False** (no date, no plan-word in title) -> the only row needing the Kip/Mackenzie override (date='1722', date_commons=''; year_of/keep re-verified True in-process; 'Kitscoty' a norm-substring of the filename). All three catalog sites confirmed in data/catalog/sites.jsonl (stonehenge-q39671, avebury-q661855, kit-s-coty-house-q4222497 with the exact qid/name/lon/lat in the hand-over) -> no extras file, no new site rows; the join check is 'names an existing site'. Design decisions: (a) the IA book leg needs NO local-copy wrap (the book really is on IA) - register() only adds books.BOOKS['stukeley_templerestored1740'], and --fetch/--triage delegate straight to books.cmd_fetch / books.cmd_triage_*; (b) the transcribed plate list lives as a module constant (STUKLEY_PLATES) injected into books_lists.PLATES in-process, because pipeline/books_lists.py is owned by 217 (the 213/civitates hand-list pattern that cmd_ocrmap's comment points to); --list with the constant set then runs cmd_ocrmap and writes only the per-book lists/<ia>.json + .map.json; (c) metadata.json has title/date/creator ALL None, so the BOOKS cite string is hand-written ('William Stukeley, Stonehenge, a Temple Restor'd to the British Druids, London 1740') and must be confirmed against the hOCR title page when --list runs. The 4 PITFALLS entries (a-d, text in the previous hand-over, restated in the new one) were NOT yet filed - that is the next session's step 1, then the module exactly as designed in the hand-over. Suite baseline stands at 104 passed, 1 skipped, 0 failed (iteration 146; nothing this session changed code).

### 2026-10-13 209b DECISION: session 3 (iteration 149) was read-only - the session-2 design re-verified build-ready against the current code, with 4 corrections; nothing written (no module, no tests, no staging, no PITFALLS edits)
... (5.1 KB more: `grep -n -A 200 -F '## 2026-10-13 209b DECISION: session 2 was investigation-only (context limit) - the 3 Commons rows are verified to the last metadata field and the module design is settled; nothing written yet (no PITFALLS, no module, no tests)' DECISIONS.md`)

### 2026-10-13 209b DECISION: session 5 (iteration 152) ran the 7 unrun tests: 5 passed, 2 failed - one REAL module bug (status() read p["n"] off the raw bookreader.json, which has no n - n is the flat-list index books_ia.pages assigns; fixed to enumerate) and one TEST bug (this pytest's monkeypatch.setitem is Mappings-only and raised on the STAGED list; switched to setattr with a new list); then lead-doc line + boxes 4/6; full suite 111 passed, 1 skipped, 0 failed; committed the Commons leg. The IA book leg (fetch/triage A/plate-list transcription/book rows) is the next session - two LLM replicas answer on 8080/8081 right now, the bookreader cache is present in this checkout (166 leaves, 0/166 triaged, long side 11408-13537 px, i.e. the fetch must re-encode the huge raw pages via IIIF)
Ran tests/test_src_wiltshire_stukeley.py first (the hand-over's step 1): 5 passed, 2 failed, exactly the fragilities the hand-over named, and each failure had a different kind of fix - (1) test_status_offline_fabricated_cache errored with KeyError 'n' inside status(): the raw BookReader page dicts carry only height/leafNum/pageSide/pageType/ppi/uri/width (verified on the real cached 166-leaf file), while books_ia.pages() is what assigns p["n"] = flat index (books_ia docstring: "list index == n of page/n{N}.jpg"); status() reads the cache directly, so p["n"] can never exist - a real module bug the session-3/4 design missed (the hand-over fact 2 spelled out the raw shape but the built code still indexed by n). Fixed the MODULE (enumerate over the flat pages, triage_path(IA, n) on the index) - per the hand-over rule a red test that reflects a real bug gets the module fixed, never the assertion deleted; the test's fabricated 5-page cache (no n keys) was already correct. Verified the fix live: --status now prints "166 leaves, triage 0/166, long side 11408-13537 px" off the real cache with zero network. (2) test_canonical_title_clash_fails_loud errored in monkeypatch.setitem itself: pytest 9.1.1's setitem is Mapping-typed and calls dic.get(name) - it has no list support, so setitem on src.STAGED[0] is invalid, a test bug, not a product bug. Fixed the TEST to monkeypatch.setattr(src, "STAGED", [petrie_row] + src.STAGED[1:]) (teardown restores the original list object). All 7 pass in 2.2 s. Everything else in the hand-over's step list then went as planned: the docs/lead_wiltshire.md Stukeley-section line (module built, 3 rows staged, evidence 3/3 offline, golden + test pointers; the Stage-A/B recall line left PENDING), task boxes 4 (hand fits untouched: the per-task staging files hold only the 3 new rows, the title-only canonical guard is tested, data/db/platefits/ never written) and 6 (offline join + evidence + golden) ticked; boxes 1/2/3/5 stay open for the IA leg. Full suite 111 passed, 1 skipped, 0 failed (181 s) = the 104 baseline + 7 new, no unrelated reds. One observation for the IA-leg session: two LLM replicas answer on 127.0.0.1:8080 and :8081 right now (the --status LLM line), so --fetch + --triage A are runnable without any setup; the raw pages are very large (long side up to 13537 px), so the fetch re-encodes via IIIF at the triage size as the machinery does for every book.

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (1 tests)
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_gate.py:36: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    1 failed, 59 passed in 63.50s (0:01:03)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-13 209b (agent a, iteration 153) WHERE I AM: IA-leg steps 1-3 done - fetch 166/166 triage pages, triage A 166/166 (0 errors), STUKLEY_PLATES transcribed from a visual walk of all 47 plate leaves (the book has no printed list of plates and no Wiltshire map; site plans = TAB. XI/XII/XXIII). Next session: --list (ocrmap), --triage F/B, stage the 3 plan rows, lead-doc recall line, boxes 1/2/3/5. Module edit (STUKLEY_PLATES + CITE) saved by the harness uncommitted.
