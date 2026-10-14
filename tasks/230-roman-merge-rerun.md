Status: in-progress
# 230: The Roman staging into the canonical data - the 211 consolidation re-run
Depends on: 211, 207a, 207b, 807, 808
Touches: fit/merge.py, pipeline/commons.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/books/matches.jsonl, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py

## Goal
211's lead note: the 211 consolidation ran without the Roman books (207 was stopped by
the owner at merge time) and "207a/207b staging, if it ever resumes, goes through a
later re-run of this step." This task is that re-run. Once 211 is done and the Roman
staging (extras_roman.jsonl / files_roman.jsonl / classified_roman.jsonl plus the three
books' per-book lists/triage artifacts) has landed on main, re-run the consolidation:
fold the Roman rows into data/catalog/extras.jsonl, data/commons/files.jsonl and
classified.jsonl; rebuild data/books/index.jsonl and validation.json from ALL books'
per-book artifacts (including the three Roman books) with the existing machinery;
update the Roman row of docs/sources.md section 9; build any new Roman sites (207c's
are mostly new no-QID Scottish forts) and refresh web/data/sites.json and
web/data/plans.json. The page renders the result with no page change (GOAL.md point 5).

If a 207 subtask is dropped before this task runs, edit the Depends on line to the
surviving subtasks and run against the staging that exists (the boxes hold with the
books that landed).

## Acceptance criteria
- [x] The fit/merge.py re-run: every Roman staging row is in the canonical files; every
      pre-run canonical row is still byte-identical (pure growth); a second run changes
      nothing (idempotent); the run is logged in data/merge/log.jsonl (0 refused, or
      each refusal logged with its reason).
- [x] data/books/index.jsonl is rebuilt from the per-book files of all books (the
      post-211 set plus the three Roman books); validation.json regenerated; every row
      that reaches the plan list carries the 200 evidence field; fit/evidence.py check
      passes offline on the merged set including the Roman rows.
- [x] Every new Roman site id has web/data/sites/<id>/; web/data/sites.json grows by
      exactly the new sites and the pre-run entries are unchanged (except the 212-owned
      marker fields); web/data/plans.json: every pre-run (id, sites[0]) key still
      present, (id, sites[0]) still unique, the new Roman picture rows present
      (tools/export_plans.py re-run).
- [x] docs/sources.md section 9: the Roman lead row records what was staged and what
      was dropped, per book, sourced from docs/lead_roman.md and the merge log
      (replacing the "NONE in this merge" row 211 wrote).
- [x] The human's reference is untouched: the 25 hand fits and their 19 sites
      (tests/test_serve.py::test_hand_fits_are_the_reference) still pass after the
      re-run; the re-run's tests are hermetic (port 0, temp tree, no network).

## Notes
- Same invariants as 211: row conflicts (a Roman row equal to a canonical row or to a
  row staged by another source) resolve first-wins, recorded in data/merge/log.jsonl -
  never a silent rewrite.
- Building sites is the slow part (DEM fetch, images); it is a working-phase command.
  The test asserts the data-level result (entries, joins, idempotence) on the served
  data, not a full rebuild.
- When this task runs, tests/test_merge.py's frozen pre-merge baseline (the 385
  entries) shifts to the post-211 state (the 499 entries); update the baseline in the
  test for this intended change.

## Hand-over

(2026-10-14, iteration 215, agent a - DONE, all 5 boxes ticked, committed. it.214's
uncommitted code changes (the commons.NO fix + the 1572 plans.json) were LOST by the
driver's dc7f9ee sweep (it captured only the 307d PNGs); both were restored from the
/tmp backups (/tmp/commons_230s5.py, /tmp/plans_230s5.json) and re-verified from
scratch this session. Nothing remains for 230.)

**What was committed (the final state):**
- pipeline/commons.py - NO: bare `google` -> `google (?:maps?|earth|art|street view|satellite)` + the 4-line why-comment. Fresh re-verify: 17/17 horsley "936-leaf Google scan" files rows pass keep(); 5 junk kinds (Art Project/Earth/Maps/Street View/satellite) still dropped; 0 non-roman files rows contain bare "google".
- web/data/plans.json - 1572 rows (1510 baseline + 44 roman book + 18 roman commons), sha256 dee768f2db7c... - the regeneration is BYTE-IDENTICAL to it.214's verified artifact, and a second export_plans run is byte-identical to the first (the pending idempotence check). 0 lost keys vs the 1510 baseline, (id, sites[0]) unique.
- data/raw in this checkout is a SYMLINK to /home/agent/projects/ancient-works/data/raw (the lead's shared raw store, aeeb5aa "synced both ways Mac<->VM"): `find data/raw -type f` reports 0 (find does not follow the arg symlink) but the roman raw data is all present (britanniaromanao00hors/full 24 leaves, memoirwrittendu00maclgoog/full 6, 18 commons copies) - regeneration is reproducible here.
- tasks/243-matchfit-station-rerecord.md - NEW (Status: open, Depends on: 230): re-record the 302f matcher-station fixtures after this task's index rebuild (37edbfb) re-stamped evidence.checked and drifted header.input_hashes.index_row (4c7be2d0 at 37edbfb^ == the fixture's hash; 003d1d77 now; only field changed: evidence). The 15 request bodies per fixture are unchanged, so it is a header re-stamp + replay validation against the live ELoFTR (127.0.0.1:8091).
- The ten docs/site_flow/307d_*.png restored to main's bytes and committed with this (PITFALLS "test_owner_check re-renders all ten 307d golden PNGs...": the branch must carry main's bytes; the driver's dc7f9ee had committed this run's dirty versions onto this branch - main's bytes clear the pending binary-merge conflict, the 6af207b precedent).
- DECISIONS.md (the it.215 done-claim entry) + PITFALLS.md (2 new entries: the commons.rows re-judgement trap; the matchfit fixture's whole-row hash drift).

**Verification fresh this session (all run, none inferred):**
- fit/merge.py merge --sources roman re-run: +0/+0/+0, refused 0; the 3 canonical files sha256-identical before/after (box 1 idempotence on the current tree).
- fit/evidence.py check: rc 0, "2751 rows, 1456 pass, 0 fail, 1295 no-tie" (box 2).
- web/data/sites.json: 508 entries, all 9 roman site dirs present and complete (ardoch aerial-only: no relief.jpg, depictions present; the 8 others relief.jpg + map depictions) (box 3).
- tests/test_merge.py 10/10; tests/test_data.py 3/3; tests/test_serve.py::test_hand_fits_are_the_reference 1/1 alone + tests/golden/hand_fit_docs.sha256 all OK (box 5).

**Remaining suite reds are NOT 230's (documented in the it.215 DECISIONS entry):**
- test_matchfit_station x2 - caused by 230's INTENDED index rebuild (the drift detector works as designed); remedy = task 243 (created).
- test_owner_check x2 - re-run this session: A fails at "toolbar scale and turn change the drawing on screen" (pick richard-s-castle-q17650937 / earthworkenglan01allcgoog_n0453_1, same as it.214), B fails as a consequence. it.214's one unexamined suspect is REFUTED: all 7 richard-s-castle files (data/sites + web/data/sites) are byte-identical across this checkout, agent c's checkout and main, as are fit_queue.json / review.json / the 71 platefits docs (identical picks), and the Chrome binary is unchanged since 2026-10-05. The red is the 307d mid-transition capture/measurement family (task 242's measurement: same-tree runs an hour apart differ 28.6-33.6% of pixels on the saved/reload views; the measured 1.06105 ~= 1.05 x 82.863 is a camera-settle signature). Remedy = task 242 (queued, Depends on: 307d; 307d's lane, not this task's).
