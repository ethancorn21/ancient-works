Status: done
# 306c: Look at the orphan agent fits, US - 16 docs, 9 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306c.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 16
US platefit documents with `by: agent` that are ORPHANS - in the store, but with no overlay
built on the site and not referenced by any review item, so a visitor sees them not at all.
Render each the way the page would if it ever showed it: the fit tool over the aerial
photograph, and over the LiDAR relief (every site here has a `relief.jpg`), with the doc's
stored pairs placed. The verdict records where the doc stands today (invisible) and whether
the placement is good enough to keep.

## Acceptance criteria
- [x] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief), taken with `tools/shot.mjs` against `server/serve.py --port 0` on this checkout
      (recipe in the parent's Hand-over; GET only, ephemeral port).
- [x] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on (the real mounds, banks, ditches) and
      the verdict (keeps its document / deleted - and it is an orphan today, invisible on the
      page).
- [x] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (`fit/review.py upsert_item`
      pattern), the document is deleted, and the site's review page file is re-exported scoped
      to the site (never another site's item file). The site stays covered for the union check
      (an open item counts). A fit that sits right keeps its document, and its line says so.
- [x] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (16, 9 sites)
- cahokia-q333661.annualreportofbu1218901891smit_n0200_1 - Map of Cahokia group, Madison county, Illinois
- etowah-indian-mounds-q4533107.annualreportofbu1218901891smit_n0386_1 - Plat of the Etowah group (original)
- fort-ancient-q5470727.b24849959_n0264_1 - Fort Ancient, Warren county (Squier & Davis)
- hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1 - Plan of Cemetery Mound, Mt. Vernon
- hodgen-s-cemetery-mound-q5876069.b24849959_n0353_1 - Plan of mound at Mt. Vernon (Squier & Davis)
- marietta.b24849959_n0195_1 - The Marietta works (Squier & Davis)
- mound-cemetery-q6919104.annualreportofbu1218901891smit_n0563_1 - Plan of Cemetery mound, Mt. Vernon, Knox county
- mount-horeb-earthworks-complex-q6921321.c_d1dff07f0da57b0e - Peter Village enclosure, Squier & Davis Plate XIV fig 3
- pyramid-mound-q7263260.ancientmonuments00squi_n0134_1 - (Squier & Davis, untitled)
- serpent-mound-q968802.b24849959_n0313_1 - Serpent Mound; from Holmes
- serpent-mound-q968802.c_15ff865e5f3d8ddb - Serpent Mound by William Jacob Baer
- serpent-mound-q968802.c_2c260a03d1f8df1c - SD35 Serpent Mound, Squier & Davis Plate XXXV
- serpent-mound-q968802.c_52dfe1fc979edf2c - Harper's New Monthly Magazine, vol 104
- serpent-mound-q968802.c_7b01a4bb50d68b56 - 26 of A School History of the United States
- serpent-mound-q968802.c_8ebd42607fbb96d8 - 26 of A School History of the United States (2nd copy)
- serpent-mound-q968802.c_dd2c553d611e610b - 26 of A School History of the United States (3rd copy)

## Notes
- serpent-mound carries the site's one hand fit (n0210_1) on the map; its 7 agent docs are all
  orphans. The hand doc is never touched and its overlay stays whatever this audit decides about
  the agent docs.

## Hand-over
(2026-10-12, iteration 152, agent c - sixth session. **Work is unchanged from iteration 150 and complete (all committed: 0b83599 + driver's 9ab14fc). The done-claim is RE-FILED this session: status set to done again, after re-proving the suite green on a run with headroom and cleaning the 3.5G /tmp run leftover, so the driver's re-verification run now has 6.0G headroom.**)

**Why the claim was re-filed.** The one rejection (driver note 17:06) cited only `test_serve.py::test_document_store_roundtrip` as new (new-failures-306c.txt) - its 17:06 run report shows that failure as `RemoteDisconnected` (the session server died mid-request) inside an ENOSPC cascade (13x `Errno 28`, 30 errors; the 307bb gesture test was an ERROR in that run, not a FAILED - it was not flagged). Diagnosed at iteration 151: the 48G disk was 95% full and the driver's run ran out of /tmp mid-run. It is environmental, not a 306c regression: the roundtrip test writes only the scratch `awtest` collection (plain file writes; serve.py's `after_write` is a no-op for non-platefits) - no route from 306c's changes (one doc deleted, one review item updated, one page re-export, docs) into it.

**What this session did (the only step: re-verify, then re-file).** (1) Confirmed no newer driver report than the 17:06 one, working tree clean, no pytest/chromium processes, /tmp/loop-ancient-works.c at 2.2M; (2) re-ran the full suite (`.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py`, 224 s): **127 passed, 1 skipped, 1 failed** - the sole failure is tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (307bb, agent a) at the same pre-gesture seed step as iterations 150/151 and the A/B at 1ade748 (deterministic pre-existing; PITFALLS tests/test_fit_queue.py); no ENOSPC (disk had 6.0G headroom); (3) deleted the run's 3.5G /tmp/loop-ancient-works.c/pytest-of-agent leftover (ps-verified nothing running) -> 6.0G free / 87% for the driver's run; (4) set Status: done to re-file the claim.

**Work state (unchanged from iteration 150).** Of the 16 US orphan docs: 9 deleted the 303 way (8 in b9cbc46: marietta + the 7 serpent-mound docs; + hodgen n0092: upserted into the site's existing item, doc deleted, scoped export, 333 open); 7 keep their documents (cahokia, etowah, fort-ancient, hodgen n0353, mound-cemetery, mount-horeb, pyramid-mound). The 306c block in docs/site_flow.md (L941) carries all 16 lines plus the final preamble; the 32 shots are in docs/site_flow/agent_fits/; all four acceptance boxes ticked; the one by:hand doc (serpent n0210_1) is git-clean.

**Next session (only if the driver rejects again).** Read the newest driver note in DECISIONS.md + .agent/reports/last-test-output.txt first. (a) ENOSPC again (`Errno 28` / `RemoteDisconnected`, `1 failed ... N errors`): `ps aux | grep -E "pytest|chrom"` must be empty, then `rm -rf /tmp/loop-ancient-works.c/pytest-of-agent/` (never another project's /tmp/loop-*), re-run the suite, clean the fresh leftover, re-file. (b) Any OTHER red on a run with headroom = a real regression: dig (roundtrip -> server/serve.py db routes; anything else -> diff against the report's baseline). (c) If 307bb is flagged as a "new failure": it is agent a's deterministic in-flight 307 red, owned by 307 (web/fitqueue.js is outside 306c's Touches); it was an ERROR, not a FAILED, in the driver's own 17:06 run. Do not fix it here; ask_human with the A/B evidence (this file, iteration 150 entry; PITFALLS) if the driver holds on it.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
own task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/306c-orphan-fits-us.md` (in-progress) - hand-over: (2026-10-12, iteration 147, agent c - second session. 32-shot run CONFIRMED complete; all 7 serpent-mound docs judged (ALL DELETE); 9/16 judged. Session died at the context limit just as the 303-way removal execution was being prepared.)
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

### 2026-10-12 306c driver-note: session at context limit (iteration 146)
- 306c first session: tools/audit_306c.mjs built (clone of 306b's; works on the post-307 page), full 32-shot
  audit run launched in background (log /tmp/audit_306c.log; resumable - skips existing shots), ~30 shots
  written to docs/site_flow/agent_fits/. 1/16 judged: marietta = DELETED case (fit 1 m/px/0 deg matches the
  plate's scale bar, but the drawn Conus mound sits ~1.3 km S-E of the real one in Mound Cemetery) - the
  303-way removal (upsert candidate w/ place_reason -> delete doc -> scoped export) is NOT yet executed.
  Next session: finish the run (re-run driver), judge the other 15 in batches, execute marietta's removal
  (after reading test_batch_eu/test_serve), write the 306c block in docs/site_flow.md, run the suite
  (baseline 128 passed / 1 skipped, --ignore=tests/test_gate.py). Full state in the task's Hand-over.

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/221-review-stats-test.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-12 306 DECISION: split into six look-audits by visibility class and region
- Box 1 of 306 covers ALL 112 non-hand docs (23 on-map, 21 in review items, 68 orphans - the orphan
  class is new to the project: in the store but neither built as an overlay nor referenced by any
  review item, so a visitor can see them not at all; audited by rendering the doc's saved pairs in
  the fit tool). Six subtasks: 306a on-map (23), 306b review (21), 306c orphan US (15), 306d orphan
  UK part 1 (18), 306e orphan UK part 2 (15), 306f orphan continental (17). A before B before C:
  only A sits on the map (the title's "none reaches the map unseen"); only 306a performs the
  removals (box 2). No subtask carries `Depends on: 306` (a split parent deadlocks its own
  subtasks - PITFALLS); the driver hands them out a-f.
- The audit is headless-browser work, not a test: serve the tree once (server/serve.py --port 0,
  ephemeral port, GET-only - safe for parallel checkouts) and drive the real page through
  tools/shot.mjs's [js] argument: select(site) -> setGround('imagery'|'relief', site) ->
  startFit(site) -> openPlan(row) -> push the doc's pairs as {u,v,lon,lat} + addPairMarker +
  refit (refit renders the fitted plate as the fit-prev map source; web/review.js does exactly
  this for item pairs, L142-146/L189-196). On-map docs go the visitor's way instead: open the
  site, activate the depiction (applyDep). This VM HAS internet (Esri World_Imagery 200 in 0.17 s,
  verified this session): the "no-internet headless" pitfall applies only to the no-network test
  runs. LiDAR on the page is the per-site prebuilt relief.jpg (index.html L367-368), not the live
  /tiles/relief (off here, `aw` is Mac-only); shotwick has no relief.jpg (aerial-only).
- For the 21 B docs the doc's stored pairs DIFFER from the review item's candidate pairs (except
  castle-neroche n0110_1): the audit renders the DOC's own pairs (the document is the artifact)
  and the verdict notes where the item's version differs.
- All 112 docs carry 4+ pairs, so every one renders as a fitted plate (simFit needs 3). sites.json
  `drawings` are stale for most A-group sites (0 despite the overlay present; only aldenhaag=1,
  forthill=2, newark=2 non-zero) - 306a's rebuild via tools/site_done.py fixes the counts for the
  sites it changes.

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
