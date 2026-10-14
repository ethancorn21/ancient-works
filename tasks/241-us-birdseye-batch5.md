Status: in-progress
Depends on: 240
Touches: fit/src_us_birdseye_batch5.py, data/catalog/extras_us_birdseye_batch5.jsonl, data/commons/files_us_birdseye_batch5.jsonl, data/commons/classified_us_birdseye_batch5.jsonl, docs/lead_us_birdseye_batch5.md, tests/test_src_us_birdseye_batch5.py, tests/golden/src_us_birdseye_batch5_sample.json, docs/site_flow/307d_*.png (R5: restoring suite re-encodes to main's bytes before committing - never content changes)

# 241: US bird's-eye views, batch 5 - the final five cities to the 25-city total

## Goal
Second part of the 236b split (2026-10-14, driver instruction; 236b closed done at 16 cities and the
remaining nine went to 240 and this task, each with its own module and staging files so two agents
can build in parallel). Stage batch 5 of the Library of Congress "Panoramic Maps" collection (about
1,500 US bird's-eye views, 1847-1929, public domain; this machine cannot reach loc.gov, so files are
fetched from their Wikimedia Commons mirrors - 236b's route): the FINAL FIVE cities needed for the
25-city total (16 from 236b + 4 from 240 + 5 here), each a new site in this task's own staging
files, one best view per city. 236c consolidates all the staging into the canonical data and checks
the total.

## Acceptance criteria
- [ ] fit/src_us_birdseye_batch5.py holds the hand-checked file -> QID table for its five cities
      (every QID verified live against Wikidata with the module's --verify BEFORE staging: label,
      every P625 value, P373, P131, enwiki, the first name-search hit with coordinates - what
      record --live would resolve; the machine cannot reach loc.gov, so the files are fetched from
      their Wikimedia Commons mirrors, 236b's route). The module copies fit/src_us_birdseye_batch4.py's
      machinery (itself a copy of fit/src_us_birdseye.py's - the template it keeps in sync with);
      its known_sites() reads the catalog plus 236a's extras_us_cities.jsonl, 236b's
      extras_us_birdseye.jsonl and 240's extras_us_birdseye_batch4.jsonl so a QID can never sit on
      two sites.
- [ ] Staged rows in this task's files ONLY: extras_us_birdseye_batch5.jsonl (the new cities' site
      rows - region "United States", kind "town", aerial_ok true, the point = the city's verified
      P625 or a recorded refinement, the note recording the staged view's apparent angle so 236c /
      the matcher can order the oblique views); files_us_birdseye_batch5.jsonl (files.jsonl shape +
      the 200 evidence field); classified_us_birdseye_batch5.jsonl (p_birdseye 1.0, by "hand"). One
      row per city = the steepest (near-vertical), best-scanned whole-city view of the collection
      for that city (Public domain, >= 4000 px wide, the caption names the city); every pool item
      not staged is listed with its reason in the lead doc.
- [ ] fit/evidence.py check passes offline on every staged row (--check exit 0, every row PASS
      caption_coords, no join problems); no staged site id or QID collides with an existing site
      (the catalog, 236a's, 236b's and 240's staging files, web/data/sites.json) - never two sites
      for one QID (the catalog slug rule: id = slug(name) + "-" + qid-lower).
- [ ] Test (no network, the socket-blocking fixture per 236b's test file): the staged files join,
      the evidence check passes, a golden sample tests/golden/src_us_birdseye_batch5_sample.json
      pins the staged rows (regenerated only via the module's --golden for an intended change); a
      full-suite run = baseline (restore the re-encoded docs/site_flow/307d_*.png to main's bytes
      before committing - the PITFALLS test_owner_check rule).
- [ ] FIVE cities staged (the 25 total: 16 from 236b + 4 from 240 + 5 here), each per the boxes
      above; or, if the collection yields fewer usable candidates after a documented search, each
      dropped candidate is recorded with its reason in the lead doc and the shortfall (with the
      final count) is recorded there for 236c's 25-total check.

## Notes (operational facts carried from the 236b split, 2026-10-14 iteration 195)

**Read first (all on main):** 240's task file (its Notes carry the complete per-city playbook, the
module-copy spec and the rules - they apply here verbatim), fit/src_us_birdseye_batch4.py (the
module to copy - change only the staging-file paths to the *_us_birdseye_batch5.* set in the
Touches line, the module name in the rows' "by" / "source" fields, and known_sites() to also read
240's extras_us_birdseye_batch4.jsonl - it will exist by the time this task runs, 240 is done),
240's lead doc (docs/lead_us_birdseye_batch4.md: the STAGED/DROP section format, the QID
transcript format, and its "Not done yet" pointer naming the next candidates), plus 236b's
docs/lead_us_birdseye.md (the Fetch route and evidence-field contract) if you need the original
wording. Do NOT edit fit/src_us_birdseye.py, fit/src_us_birdseye_batch4.py, fit/evidence.py or any
pipeline/ file (read-only for this task; file a task if one of them needs a change). This module
stages no shared (owner-named) cities.

**The candidate list:** start from 240's lead-doc "Not done yet" pointer (240's Notes require it
to name the next two or three candidates in the collection's search order); if it names fewer than
five, continue the LOC Panoramic collection's city list in search order (the six plain-phrase
forms + " filetype:bitmap" over candidate cities - 236b's pool route), skipping cities already
staged anywhere (236b's and 240's site tables, the catalog, web/data/sites.json) and cities whose
pools yield no usable view (record each drop, take the next candidate). This task owes FIVE
staged cities, not specific ones. St. Paul / Minneapolis / Cleveland were 240's candidates - if
240 dropped any of them, they come first here (240's lead doc says why they dropped).

**Per-city landing (the proven 189-194 pattern, one city per session pair):** (1) RESEARCH: the
QID (Wikidata: the label - first-guess mislabels are the usual trap class, every P625 value, P373
(a string is the usual US quirk - write the place from the county + state), P131, P17, enwiki,
the name-search trap check; record everything in the SITES comment; MEASURE every distance claim
with fit/evidence.hav_m + geographic dx/dy before writing it; check no existing site holds the
QID - if one does, tie the row to that site like 236b's shared cities and record it in the lead
doc) + the pool (build, dedupe, filter, 1280 px thumbs eyeballed one by one - the
/tmp/aw236b_b3_dvr.py script is the template). (2) LANDING: module edit -> --verify (save the
exact output; the lead doc carries it verbatim in the QID section) -> --dry -> stage (live
commons.info re-check) -> --check (save the transcript; the Staging section carries it verbatim)
-> lead-doc section (STAGED bullet + the full DROP list + the QID-facts paragraph) -> --golden ->
test extension (mirror tests/test_src_us_birdseye.py / test_src_us_birdseye_batch4.py: the
no_network socket-blocking fixture; the PASS-key list; the SITES-id / extras-id / year / point /
named tables; the golden compare) -> module tests -> the FULL suite (restore the 307d pngs first)
-> commit. The lead doc's Staging section ends with the project total (it should read 25 when all
five land) and a note that 236c consolidates.

**Rules (unchanged from 236b/240):** NEVER write the canonical files (data/catalog/extras.jsonl,
data/commons/files.jsonl, classified.jsonl - that is 236c); NEVER touch 236a's, 236b's or 240's
files (read-only; the module's cross-check enforces); live commands under .venv/bin/python
(system python3 has no numpy; the module top stays stdlib-only); the golden sample is the contract
(--golden only for an intended change); tests never bind fixed network ports or write outside the
project and the temp dir; every full-suite run re-encodes up to ten docs/site_flow/307d_*.png -
restore main's bytes before committing (the PITFALLS test_owner_check entry); one row per sheet
(same-sheet scans recorded in the lead doc, the LOC .jpg staged where it is the best scan).

## Hand-over
(2026-10-14, iteration 173, agent c - **step 0 done (prep-note plan): the batch5 module, the lead-doc
skeleton and the test skeleton are WRITTEN in the working tree (uncommitted; the harness carries them);
the pre-change full-suite baseline is RUNNING in the background. 240 is DONE (4/4: Denver, St. Paul,
Minneapolis, Cleveland) - read and verified.)

**State of the working tree (check `git status` first; nothing of mine is committed yet):**
- `fit/src_us_birdseye_batch5.py` (401 lines) - the batch4 module copied with ONLY the intended
  changes (verified by `diff fit/src_us_birdseye_batch4.py fit/src_us_birdseye_batch5.py` - look ONLY
  at: docstring, the 4 path constants, the SITES preamble + `SITES = {}`, `SOURCES = {}`, known_sites()
  reading `EXTRAS_BIRDS_BATCH4` instead of the then-absent batch5 file, the "by"/"source" strings,
  the two lead-doc references, the check_staged docstring, the golden path). AST parsed OK. `--check`
  works on the absent staging files (evidence.check tolerates a missing path -> 0 rows, exit 0);
  `c.info([])` is a safe no-op (empty batch loop). `--verify` on an EMPTY SITES would send a bad
  Wikidata call - do not run it until SITES has an entry.
- `docs/lead_us_birdseye_batch5.md` (skeleton): header with the candidate order (Omaha - re-run its
  pool search - Indianapolis, Columbus, Memphis, then the 181 list's remainder), Fetch route,
  QID-verification and evidence-field pointer sections, a Staging section that says "nothing staged
  yet", and the Not-done-yet pointer. City sections land here per landing (the 240 pattern).
- `tests/test_src_us_birdseye_batch5.py` (six offline tests, mirroring batch4's 249-line file, pure
  ASCII, NOT yet run): no_network fixture; --check join/PASS (empty key list); the hermetic
  three-states test with state (c) guarded by `if staged_files:` (re-enabled by the first landing);
  the sites-table test with the empty tables (grows per landing); the negative control SYNTHETIC
  (Batchville site point (-95.933889, 41.256944) vs Venice (12.33, 45.44), distance formatted from
  `evidence.hav_m` - no magic number); the golden test. The 236b/240 pattern rebinds the negative
  control to the real first staged row (files[0] with the Venice point) at the first landing.
- `docs/site_flow/307d_*.png`: five were re-encoded in the working tree from the 240 close-out era
  and were restored to main's bytes at session start (they are STAGED in the index and ride this
  hand-over commit; R5 - never a content change; the batch4 task carried the same Touches entry).

**Baseline (R2):** pre-change full suite running BEFORE any file was created:
`.venv/bin/python -m pytest -q > /tmp/aw241_suite_pre_173.log` (background pid 2670235 at session
end; ~45 of ~186 tests done then). `.venv` exists (Python 3.12.3); the driver's test command is
exactly that. `.agent/reports/last-failing-tests.txt` still names
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (the driver's 2026-10-13
loop-start red) - 240's run 172 (today, main) was 185P/1S/0F, so it is probably STALE; the baseline
result is the truth. If it is red, it is not 241's to fix (R2) - record it and move on.

**Next session, in order (do these before any research):**
1. `git status` + `tail /tmp/aw241_suite_pre_173.log` (or `ps -p 2670235`): record the baseline
   result (expect ~185P/1S/0F). If the process is dead with no summary line, re-run it (it is
   pre-change state still, since my files are additive-only: a new module/test/doc - nothing
   shared is touched, so a re-run is still a valid baseline).
2. `.venv/bin/python fit/src_us_birdseye_batch5.py --golden` ->
   tests/golden/src_us_birdseye_batch5_sample.json (empty: {"classified": [], "extras": [], "files": []}).
3. `.venv/bin/python -m pytest tests/test_src_us_birdseye_batch5.py -q` (offline) -> expect 6/6;
   then the post-change full suite (R4: ALL edits done first - i.e. after step 2), restore any
   re-encoded docs/site_flow/307d_*.png to main's bytes (`git checkout main -- <files>`), and
   commit: `241: batch5 module + lead-doc/test skeleton (empty) - the step-0 setup before Omaha
   research` (add the uncommitted files with `git add` - the five 307d pngs already in the index
   ride along; if the suite re-encoded more pngs, restore+add those too).
4. **OMAHA RESEARCH (the per-city playbook step 1, 240's Notes):** QID first (Wikidata live, the
   wbgetentities pattern: label, every P625, P373, P131, P17, enwiki, the first name-search hit with
   P625 at limit 5 AND limit 20 (R5: limit=5 misses well-known short names; a label search with
   parentheses returns EMPTY); first-guess QIDs are the usual mislabel trap - Omaha's first guess is
   probably a person/monastery/namesake; record the memory-error if the memorized QID fails the
   label check). Skip-list check (catalog, extras, 236a/236b/240 files, web/data/sites.json - the
   module's known_sites() enforces this at stage). Then the POOL: clone
   /tmp/aw236b_b3_dvr.py (still present; the aw240 pool scripts may be gone - the 240 Notes' b3
   template is the canonical one): six plain-phrase forms + " filetype:bitmap", srnamespace 6,
   srlimit 40, dedupe, commons.info gates (keep() after any date swap, caption names the city,
   Public domain, >= 4000 px), 1280 px thumbs eyeballed one by one (/tmp artifacts, ~2 s pace, the
   Wikimedia 429 back-off is in commons.get). THE PICK = the steepest near-vertical best-scanned
   whole-city view; record every non-staged pool item with its reason (the 236b/240 DROP-list
   format). Save the pool JSON + thumbs + a log under /tmp/aw241_omaha_* (re-verifiable). Record
   everything in DECISIONS (the 240 DECISION-entry format: QID facts, pool counts, the pick, the
   drops). Omaha was skipped in 236b with NO recorded drop reason (the 181 list ran past it to
   St. Paul/Minneapolis) - its research verdict (usable pick, or a documented drop + next
   candidate) is the first open question of the task.

**Landing session after research (the per-city playbook step 2):** module edit (SITES entry + the
per-view `<CITY>_<YEAR>` row + SOURCES entry) -> --verify (verbatim output into the lead doc's QID
section) -> --dry -> stage (live commons.info re-check) -> --check (verbatim transcript into the
Staging section) -> lead-doc city section (STAGED bullet with the apparent angle, full DROP list,
QID-facts paragraph) -> --golden -> test extension (the key list, the id/points/years/named
tables, the negative control rebind) -> module tests -> FULL suite (restore the 307d pngs) ->
commit. Cities 2-5 the same (Indianapolis, Columbus, Memphis, then the 181 remainder); the Staging
section ends with the project total 25 (16 + 4 + 5, or the recorded shortfall) and the 236c note.

**Rules (unchanged):** never write the canonical files (236c); never touch 236a's/236b's/240's files
(read-only; the known_sites() cross-check enforces); live commands under .venv/bin/python (the
module top stays stdlib-only); the golden is the contract (--golden only for an intended change);
tests never bind fixed network ports or write outside the project and /tmp; every full-suite run
re-encodes up to ten docs/site_flow/307d_*.png - restore main's bytes before committing (R5).
Re-read: fit/src_us_birdseye_batch5.py:known_sites - confirm it reads exactly SITES_JSONL, EXTRAS,
EXTRAS_US_CITIES, EXTRAS_BIRDS_236B, EXTRAS_BIRDS_BATCH4 + WEB_SITES (box 1) - the diff check above
says it does, but re-verify with fresh eyes.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-14, iteration 137, agent c - the driver returned the parent after 207a (done),
- `tasks/236-us-cities.md` (split)
- `tasks/241-us-birdseye-batch5.md` (in-progress) - hand-over: (2026-10-14, iteration 173, agent c - step 0 done: batch5 module + lead-doc/test skeletons (empty SITES) uncommitted in the working tree; pre-change full-suite baseline running in background (pid 2670235, /tmp/aw241_suite_pre_173.log); next: record baseline, --golden, run the 6 skeleton tests, commit, then Omaha research)

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/236c-us-cities-merge.md`
- `tasks/239-retire-vision-fit.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

(no entries yet)

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
