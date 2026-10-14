Status: in-progress
# 000: Plan the project from GOAL.md
Depends on: none
Touches: PLAN.md, CODEMAP.md, tasks/, requirements.in, requirements.txt, tests/, server/serve.py, PITFALLS.md, DECISIONS.md

## Goal
GOAL.md says, in the human's own words, what this project should be. Turn it into a plan and a task queue that the following sessions build from, one task at a time. You own the plan: choose the approach and the tech, and split the work the way you think best. GOAL.md is the human's: never edit it. Its numbers are the human's intuition, not measured requirements (AGENTS.md, Tasks).

## Acceptance criteria
- [x] PLAN.md describes what will be built, the architecture (the main parts and how they fit together), the tech choices with the reason for each, the assumptions you made where GOAL.md is silent, and what is out of scope
- [x] PLAN.md maps every point of GOAL.md to the task number(s) that deliver it, and has a `## Deviations from GOAL.md` section (empty until the evidence settles a number elsewhere or a request decides otherwise)
- [x] Task files tasks/001-<name>.md onward exist in build order, each with a Goal and testable Acceptance criteria and small enough for a few sessions; the first ones produce something that runs
- [x] The project's test command works (`npm test` when there is a package.json, otherwise `python3 -m pytest -q`), even if there are only a few tests so far
- [x] Every task file besides 000 and 999 has a `Depends on:` line (the numbers of the tasks that must be finished first, or `none`) and a `Touches:` line (the files and directories the task will create or change)
- [x] The work is split into modules that two agents can build at the same time: tasks that could run at once touch different files, and PLAN.md shows the order as waves (all tasks of a wave can run at once, and most waves have two or more tasks)
- [x] Tests never bind a fixed network port (use port 0) or write outside the project and the system temp dir: two checkouts of this project run their tests at the same time

## Notes
- Earlier GOAL.md changes are planned in already: `git log -p GOAL.md` has them.
- Task file format: tasks/README.md. Every task file starts with the line `Status: open`.
- Research what you need (web_search, web_fetch) before settling on a stack you are unsure of; say why in PLAN.md.
- A question only the human can answer (an account, hardware, a preference that changes the plan): ask_human. Prefer a stated assumption in PLAN.md and a non-blocking question over waiting.
- This task is the plan only: create PLAN.md, the task files and the test setup, not the product.
- When every box above is ticked, set this file's first line to `Status: done`: that is what ends the planning task.
- Two agents build this project at the same time, each in its own checkout; a task goes to one agent once all its `Depends on:` tasks are finished, and never while the other agent works on a task that touches the same files. Put shared foundations first (project skeleton, data model, the interfaces between modules), so the later tasks can go ahead independently. A subtask that needs the result of another task says so in its own `Depends on:` line. Avoid hotspot files: when many tasks would edit the same file (README, a central config module, the sample config), give each module its own file or section, or make those edits once in an early task; the driver replays the schedule and sends the plan back once if shared files make tasks wait that their dependencies would let run at once. List only real dependencies: tasks that touch the same files are already kept apart.

## GOAL.md changed (2026-10-13 23:39)
The human changed GOAL.md. Update PLAN.md and the task queue to match: add tasks, change your own tasks, or set tasks that no longer fit to `Status: dropped`; keep finished work that still fits. Then check and tick the boxes above again. The change:
```diff
@@ -19,14 +19,18 @@
    has at least one drawing fitted to the ground (`"drawings" >= 1`), or has a review item in `data/review/` with its
    best candidate pictures and proposed point pairs, which the human opens in the page, corrects by dragging, and
    saves with the existing fit tool. Opening a review item and saving it takes the human under a minute.
-2. **The local model does the fitting itself.** The owner wants far more fitted drawings than the 25 made by hand,
-   without making them by hand. So the fitting is done here, by the model, the way those 25 were made: it looks at the
-   drawing and at the site's ground (`tools/fitkit.py` sheets, reading their grid labels), finds the same features on
-   both (wall corners, gate gaps, bastion tips, road junctions, church footprints, river crossings), records at least
-   four such point pairs, and saves the fit. Pairs placed only from a scale bar, a north arrow and the site centre are
-   a starting point, not a fit: they say nothing about whether the drawing matches the ground. Every fit the model
-   makes goes to the gate (point 3); the review queue is for the fits the gate refuses and the pictures the model could
-   not fit, not the plan for every site. The number to grow is the count of fitted drawings.
+2. **The image matcher does the fitting, never a language model.** The owner wants far more fitted drawings than
+   the ones made by hand, without making them by hand. The only automatic placement is the purpose-built image
+   matcher (`fit/matchfit.py`: MatchAnything RoMa and ELoFTR), which finds the same points on the drawing and on a
+   georeferenced ground image (the LiDAR relief, or an old survey sheet already placed on the map) and keeps a fit
+   only when enough matched points agree. The local Qwen models never place a drawing and never write point pairs or
+   coordinates (owner, 2026-10-13: "the image matching model should be the only thing that's doing the matching").
+   Why: on 2026-10-11 the agents placed about 100 drawings by reading the fitkit sheets themselves; the look audits
+   (306a-f) found nearly all of them wrong and 212b deleted them. The Qwen models find, classify and tie pictures and
+   write code; `fit/batch_us.py` / `fit/batch_eu.py`'s model fitting pass is retired. Automatic fitting runs on LiDAR
+   sites only (owner, 2026-10-13: fits on aerial photographs alone mostly do not line up); aerial-only sites keep
+   their review items for the human. Every matcher fit goes to the gate (point 3); the pictures the matcher cannot
+   place go to the review queue. The number to grow is the count of fitted drawings.
 3. **A fit is accepted by numbers, never by a model's opinion.** Automatic acceptance goes through a gate validated
    on the existing hand fits with a held-out set (task 001). The human will check a random sample of 20 automatically
    accepted fits on the map; at least 18 must be right (the drawing's walls, streets or gardens on the matching
@@ -76,6 +80,10 @@
   10-30 m (Castle Rising, Bergues). Read the grid labels on a fitkit sheet, never its own pixels.
 - Where there is no LiDAR the ground is the aerial photograph (`tools/fitkit.py ground`, `FITKIT_GROUND=aerial`);
   fixed landmarks (roads, churches, river crossings, field edges) carry the fit there.
+- The image matcher places about 1 drawing in 10 (2026-10-13: 49 fits on the map, 35 RoMa + 14 ELoFTR; 37 matched
+  against old survey sheets, 12 against the LiDAR relief). An old drawing matches an old survey sheet far better than
+  LiDAR shading. Pictures it already refused do not get better by re-running it: a better yield needs a better
+  ground image or a better matcher, never a language model placing points.
 - Candidate pictures already found: 1166 plans in `web/data/plans.json` (8 old books plus Commons), with their
   page images in `data/raw/books` and `data/raw/commons`. Most are not fitted yet.
 - This VM's copy has the built sites' images (`web/data/sites`) but not their elevation models (`data/sites/*/dem.npy`);
```

## Hand-over

(iteration 157, 2026-10-13, agent a - **the 2026-10-13 23:39 GOAL change (point 2: the image
matcher is the ONLY automatic placement, never a language model) is fully PLANNED and all file
edits are made in the working tree.** The session hit the context limit before the DECISIONS.md
append and the commit; the next session does the commit (exact steps at the end). No code or
tests changed by this task - planner files only.)

**Where I am (all in the working tree, NOT yet committed):**
- PLAN.md re-checked against the 2026-10-13 change (7 edits, all applied): Current state
  rewritten (499 sites; 57 covered = 22 hand fits + 49 matcher fits — 35 RoMa + 14 ELoFTR,
  37 on placed survey sheets, 12 on LiDAR relief, 0 on aerial; the three failed methods:
  autofit 0/5, the vision batch ~100 fabricated (deleted by 212b), inkfit 231-2204 m held-out;
  the matcher places ~1/10). The architecture diagram's batch-model block is replaced by the
  matcher station (RANSAC on the matched points; a doc is written only when the matcher's
  judge AND the frozen 001 gate accept — 238; the queue records every refusal reason; the
  LiDAR-only rule — 239; the Qwen models never in the path: find/classify/tie/write code;
  the vision fitting pass RETIRED). The module map gains the fit/matchfit.py row (the lead's
  module; 302a/b/e, 302f, 302g, 238) and retires the 203a/203b model pass. The task map's
  point 1/2/3 rows re-mapped (point 2 -> matchfit/302f/302g/238/239/212/201; point 3 -> 001 +
  238 + 212's sample). Assumptions 10-11 added (10: "LiDAR sites only" read WITH the preceding
  sentence — placed old survey sheets stay a valid ground even without LiDAR, 5 current fits
  are exactly that; excluded = aerial-only ground, a guard here since 0 of 499 sites are
  aerial-only; the stricter variant is a one-line change in fit/matchfit.grounds. 11: the
  matcher is deterministic — re-running refused pictures cannot place them; better yield =
  better ground images or a better matcher). Out of scope: no re-run / no threshold-loosening
  yield strategy. The waves section gains "The remaining work (2026-10-13)": wave 6 =
  302f + 302g + 235 + 212 (all parallel, no shared files), wave 7 = 238 (waits on 6),
  wave 8 = 239 (waits on 238 + 212).
- NEW task files (written, uncommitted): tasks/238-matcher-gate.md (every matcher fit through
  the frozen 001 gate: matchfit.run writes a doc only when judge AND fit_gate.gate(pairs,
  None) accept; score = the gate's median; the gate's `why` exposed per candidate; appends one
  section to docs/gate.md; deps 302f, 302g) and tasks/239-retire-vision-fit.md (the batch's
  _sheet/_model_prompt/_parse_answer/llm_model/recorded_model deleted; the line's second pass
  becomes the matcher-reason upsert; --working/--model-json off the line, batch_eu and
  cover.py's loop forwarding; tests + docs/site_flow.md step 1 updated; deps 238, 212, 302f,
  302g). Both have Depends on: + Touches: one-line per the README; lowest free 200-499
  numbers (240 is next free). No file overlap between them or with the open 302f/302g/235.
- tasks/000-plan.md: all seven acceptance boxes re-verified and ticked [x] (box 5 needed the
  fix below); Status set to done.
- Box 5 fix: tasks/302a-inkfit-method.md, tasks/308-arrowhead-markers.md,
  tasks/309-queue-right-place.md (all done, agent-created) lacked the one-line `Depends on:`
  (302a removed it deliberately at done; 308/309 never had it) — `Depends on: none` added
  after the title, so every task file besides 000/999 now carries the three lines the driver
  reads.
- Facts verified by running code (not reasoned): 49 matcher docs in data/db/platefits (0
  against imagery.jpg; 5 against Etat-Major sheets on sites without relief.jpg); 22
  non-matcher docs = the golden's 22 hand docs (41 lines = 22 docs + 19 site.json, incl.
  Fort Ancient after the lead's port); 499 sites (425 with relief.jpg, 0 aerial-only, 74 with
  neither); 1510 plans rows; 456 review items in web/data/review.json; site_done._fit still
  runs batch_us.run_sites as the model second pass; matchfit.run writes docs on judge()
  silence with score = raw median matcher residual (the 001 gate never runs on matcher docs —
  that is the 238 gap); fit_gate.gate(pairs, transform=None) solves the canonical similarity
  and the matcher's RANSAC refit is the same least squares over its inliers, so the gate is
  directly applicable; cover.py refuses --working at the CLI but still forwards --model-json
  (hence 239's dep on the in-flight 212); the lead's port d286196 (10-13 18:57) had already
  updated GOAL.md and ONE PLAN.md tech-choice bullet — the rest of the plan was still the
  2026-10-10 wording, which this session finished.

**Tests:** not run this session (planner bookkeeping; no code touched). Last known state per
the newest driver loop-start note: 1 failed (tests/test_fit_queue.py::
test_placement_gestures_and_save_in_the_browser — the known 212/235 red, unrelated), 159
passed, 1 skipped.

**Current hypothesis:** nothing outstanding on 000 itself — the plan is complete, the boxes
stand, and the driver's re-check (box list + the suite gate, where the known 212/235 red is
"was already failing before") should accept the done claim once committed. No ask_human was
needed: the LiDAR-only reading is stated as assumption 10 with the stricter variant noted as
a one-line change, and GOAL's own 49-fits count includes the 5 sheet-only fits, so the read
is the owner's.

**Exact next step (one small session):**
1. Append the DECISIONS.md entry below (a new `## ` section at the end of DECISIONS.md — the
   full intended text is in the session record; at minimum: what changed in GOAL, that the
   lead's d286196 had planned only one PLAN bullet, the investigation facts, and the two
   decisions — 238/239 added, 302a/308/309 `Depends on: none` format fix).
2. `git add -A && git commit -m "000: plan re-checked for the 2026-10-13 GOAL change - the
   matcher is the only automatic placement (238/239 added; boxes re-ticked)"`. (The harness
   has saved this session's uncommitted file changes: PLAN.md, tasks/000/238/239/302a/308/309.
   Verify with `git status` first; if anything of these is missing from the tree, restore it
   from this hand-over before committing.)
3. Stop. If the driver reopens 000 for another GOAL.md change: diff GOAL.md against PLAN.md's
   task map, edit only planner-created task files (never 001), new leads take the lowest free
   200-499 number (240 next) with Depends on + Touches, re-check the seven boxes, re-set
   Status.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/000-plan.md` (in-progress) - hand-over: Done (iteration 13, 2026-10-10). The plan update for the two GOAL.md changes is complete and 000 is
- `tasks/207b-maclauchlan.md` (blocked) - hand-over: (2026-10-13, iteration 204, agent c - NO work on this task. The driver auto-put it back to
- `tasks/207c-roy.md` (blocked) - hand-over: (2026-10-13, iteration 205, agent c - NO work on this task. The driver auto-put it back to
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

## Where I am (iteration 157, agent a, task 000 - written at the context limit)

The 2026-10-13 23:39 GOAL change (point 2: the image matcher is the ONLY automatic placement,
never a language model) is fully planned in tasks/000-plan.md. Done and committed in f828ce0:
tasks/238-matcher-gate.md (every matcher fit through the frozen 001 gate; deps 302f, 302g) and
tasks/239-retire-vision-fit.md (the vision-model fitting pass retired; deps 238, 212, 302f,
302g) created; 000's seven boxes re-verified and ticked, Status: done; `Depends on: none`
format line added to done tasks 302a/308/309. The DECISIONS.md entry above records the
investigation facts and the decisions (incl. the LiDAR-only reading = PLAN assumption 10).
STILL UNCOMMITTED in the working tree: PLAN.md (the seven plan edits - current state 2026-13,
matcher-station architecture, module map, task map points 1/2/3, assumptions 10-11,
out-of-scope, waves 6-8). NEXT 000 SESSION (one small step): `git add -A && git commit -m
"000: plan re-checked for the 2026-10-13 GOAL change - the matcher is the only automatic
placement (238/239 added; boxes re-ticked)"` (check `git status` first; the only expected
change is PLAN.md), then stop. No code or tests touched; suite state per the loop-start note
above (the 212/235 red is pre-existing to 000).
