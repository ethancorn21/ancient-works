Status: done
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

(iteration 159, 2026-10-14, agent a - **000 re-filed done.** One step this session: the driver's
merge-conflict hold (2026-10-14 DRIVER note: "it cannot go into main yet: your branch conflicts
with main ... in: PLAN.md") is resolved. Merged main, resolved the single conflict keeping both
sides' intent, ran the full suite green on the merged tree, re-verified all seven boxes. No
GOAL.md, no code, no other agent's task file touched.)

**Conflict anatomy (diffed, not reasoned):** merge-base c72706b. Against that base main had
changed exactly three places in PLAN.md: (1) the module-map Roman row -> per-book
`fit/src_roman_horsley.py` / `fit/src_roman_maclauchlan.py` + the 207-split/Roy-drop note; (2)
task-map line 5 -> "207 Horsley/Maclauchlan (Roy 1793 dropped 2026-10-13, owner's call - see
Deviations)"; (3) the Deviations entry recording the 207c drop. Everything else that differed
between the sides was my 2026-10-13 GOAL re-plan (5420291: current state 10-13, matcher-only
architecture, batch retired, assumptions 10-11, waves 6-8, task-map lines 1-3). The one
conflicted region was the module map (lines 105-112): I had rewritten the batch row, inserted
the matchfit row and rewritten the src row; main had rewritten that same src row - adjacent
edits became one conflict (main's side also carried the base batch row).

**The resolution (both sides' intent kept):**
- batch_us/batch_eu row -> HEAD (mine): the model fitting pass is RETIRED by 239 (GOAL
  2026-10-13). Main's side was the base text (the active model loop), which contradicted the
  same merged file's tech choices and architecture (all matcher-first); main's 000 rework had
  never updated that row, so mine is the newer intent.
- matchfit row -> HEAD (mine; a new row with no main counterpart).
- src row -> main's: the per-book Roman split is a fact on main (`fit/src_roman_horsley.py`
  since the base, `fit/src_roman_maclauchlan.py` added by 207b; `fit/src_roman.py` never
  existed - my row carried the stale base text).
- main's three non-conflicting changes (line 5, the Deviations 207c entry) auto-merged and were
  kept verbatim - they are the other agents' finished-work record.
The merged 292-line PLAN.md was read whole: one coherent matcher-first plan with the 207c drop
recorded. Every cross-reference resolves post-merge: 238/239 (my side) and 302f/302g (main's
side) all exist as task files.

**Verification (run, not reasoned):** full suite on the real merged tree (.venv,
-p no:cacheprovider): **166 passed / 1 skipped / 0 failed, 454 s** - better than the loop-start
baseline (1 failed / 159 passed / 1 skipped): the fit_queue placement-gestures red is cleared
on this tree (bba5961's e2e-only rewrite on main; the corrected PITFALLS entry says notes
naming the old signature are stale) and the suite grew 159 -> 166 with 302f's merge. Queue
checker over all 99 task files: no missing/malformed bare-list `Depends on:`/`Touches:` lines,
every dep id names an existing file, no self-references, no cycle in the 14-task pending
graph. 807/808/809 stay blocked on the owner's pending asks (unchanged; out of 000's scope).
All seven acceptance boxes re-verified true against this tree.

**Commits:** merge = eeff0b8; this bookkeeping commit (000 Status: done + this hand-over +
DECISIONS entry).
The full test run re-encoded the ten tracked docs/site_flow/307d_*.png (the 307d
captures: every suite run regenerates them); ac7c5f8 committed those re-encodings by
accident (git add -A) and the next commit restores main's bytes for all ten - the
branch must stay byte-identical to main on them or the driver's merge into main
conflicts (the 207a 4cc34aa precedent; no test pins the PNG bytes).

**If the driver reopens 000 again:** the note in this file / DECISIONS says why. (a) Another
merge-conflict hold -> same procedure: `git merge main`, resolve keeping both sides' intent
(the planning world is mine; the merged-work facts are main's), run the full suite, commit,
re-file done. (b) A GOAL.md change -> diff GOAL.md against the task map, update PLAN.md,
create/drop tasks as needed (new leads take the next free 200-499 number with a bare one-line
`Depends on:` + `Touches:` - the scheduler tokenizes every NNN/NNNx on that line; PITFALLS).
(c) A content rejection -> fix exactly what the note names.

**Next step:** none - 000 is done and the plan is current as of 2026-10-14. The queue tail
(waves 6-8: 302f/302g/235/212 -> 238 -> 239) is in flight on the other agents' branches; a
future GOAL change reopens this task.
