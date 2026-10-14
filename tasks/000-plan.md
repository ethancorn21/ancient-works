Status: in-progress
# 000: Plan the project from GOAL.md
Depends on: none
Touches: PLAN.md, CODEMAP.md, tasks/, requirements.in, requirements.txt, tests/, server/serve.py, PITFALLS.md, DECISIONS.md

## Goal
GOAL.md says, in the human's own words, what this project should be. Turn it into a plan and a task queue that the following sessions build from, one task at a time. You own the plan: choose the approach and the tech, and split the work the way you think best. GOAL.md is the human's: never edit it. Its numbers are the human's intuition, not measured requirements (AGENTS.md, Tasks).

## Acceptance criteria
- [ ] PLAN.md describes what will be built, the architecture (the main parts and how they fit together), the tech choices with the reason for each, the assumptions you made where GOAL.md is silent, and what is out of scope
- [ ] PLAN.md maps every point of GOAL.md to the task number(s) that deliver it, and has a `## Deviations from GOAL.md` section (empty until the evidence settles a number elsewhere or a request decides otherwise)
- [ ] Task files tasks/001-<name>.md onward exist in build order, each with a Goal and testable Acceptance criteria and small enough for a few sessions; the first ones produce something that runs
- [ ] The project's test command works (`npm test` when there is a package.json, otherwise `python3 -m pytest -q`), even if there are only a few tests so far
- [ ] Every task file besides 000 and 999 has a `Depends on:` line (the numbers of the tasks that must be finished first, or `none`) and a `Touches:` line (the files and directories the task will create or change)
- [ ] The work is split into modules that two agents can build at the same time: tasks that could run at once touch different files, and PLAN.md shows the order as waves (all tasks of a wave can run at once, and most waves have two or more tasks)
- [ ] Tests never bind a fixed network port (use port 0) or write outside the project and the system temp dir: two checkouts of this project run their tests at the same time

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

Done (iteration 13, 2026-10-10). The plan update for the two GOAL.md changes is complete and 000 is
closed:
- PLAN.md: the six-point GOAL->task map (point 2 = the model's fitting loop: 202 starting point,
  203a/203b sheet->model->solver->gate, 201 overflow queue, 001 the gate; point 5 = the eight leads
  incl. 213), waves 4/7/3/2/1, the tech choice "The model fits, the gate decides" (injectable model
  step; no test calls the model server), assumption 9 + the out-of-scope bullet for the owner's-copy
  survey-sheet colouring, Deviations = the 001 box-2 ruling only.
- Tasks 001, 200-213, 800, 801 all exist with Depends on: and Touches: (grep -L verified empty).
  212's three rewordings landed (loop = fitkit sheet -> model fit -> fit -> gate; the 18/20 check is
  GOAL.md point 3); 213 (artists' views) created - Imola is the anchor: new site, no open LiDAR,
  FITKIT_GROUND=aerial (verified at tools/fitkit.py:38), its streets carry the fit; the conditional
  IA-book machinery follows the 208 pattern (declare per-book paths in Touches before writing).
  CODEMAP's Architecture rules block written (five standing rules; they had been claimed in the
  iteration-2 hand-over but never written).
- Test command verified in this checkout: .venv (pinned requirements.txt, commit 676a0d4) runs the
  suite green, 12 passed. The driver's ".venv could not be built" note is about main, which still
  carries the unpinned file (e2d4060, verified with git show); open 800 (agent c) lands the pinned
  file on main. This session left requirements.in/requirements.txt untouched (800's files).

If the driver reopens 000 for another GOAL.md change: diff GOAL.md against PLAN.md's task map, edit
only planner-created task files (never 001), new leads take the lowest free 200-499 number (214
next) with Depends on + Touches, re-check the seven boxes, re-set Status.
