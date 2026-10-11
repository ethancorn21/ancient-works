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
- Task file format: tasks/README.md. Every task file starts with the line `Status: open`.
- Research what you need (web_search, web_fetch) before settling on a stack you are unsure of; say why in PLAN.md.
- A question only the human can answer (an account, hardware, a preference that changes the plan): ask_human. Prefer a stated assumption in PLAN.md and a non-blocking question over waiting.
- This task is the plan only: create PLAN.md, the task files and the test setup, not the product.
- When every box above is ticked, set this file's first line to `Status: done`: that is what ends the planning task.
- Two agents build this project at the same time, each in its own checkout; a task goes to one agent once all its `Depends on:` tasks are finished, and never while the other agent works on a task that touches the same files. Put shared foundations first (project skeleton, data model, the interfaces between modules), so the later tasks can go ahead independently. A subtask that needs the result of another task says so in its own `Depends on:` line. Avoid hotspot files: when many tasks would edit the same file (README, a central config module, the sample config), give each module its own file or section, or make those edits once in an early task; the driver replays the schedule and sends the plan back once if shared files make tasks wait that their dependencies would let run at once. List only real dependencies: tasks that touch the same files are already kept apart.

## GOAL.md changed (2026-10-10 21:11)
The human changed GOAL.md. Update PLAN.md and the task queue to match: add tasks, change your own tasks, or set tasks that no longer fit to `Status: dropped`; keep finished work that still fits. Then check and tick the boxes above again. The change:
```diff
@@ -16,16 +16,24 @@
    has at least one drawing fitted to the ground (`"drawings" >= 1`), or has a review item in `data/review/` with its
    best candidate pictures and proposed point pairs, which the human opens in the page, corrects by dragging, and
    saves with the existing fit tool. Opening a review item and saving it takes the human under a minute.
-2. **A fit is accepted by numbers, never by a model's opinion.** Automatic acceptance goes through a gate validated
+2. **The local model does the fitting itself.** The owner wants far more fitted drawings than the 25 made by hand,
+   without making them by hand. So the fitting is done here, by the model, the way those 25 were made: it looks at the
+   drawing and at the site's ground (`tools/fitkit.py` sheets, reading their grid labels), finds the same features on
+   both (wall corners, gate gaps, bastion tips, road junctions, church footprints, river crossings), records at least
+   four such point pairs, and saves the fit. Pairs placed only from a scale bar, a north arrow and the site centre are
+   a starting point, not a fit: they say nothing about whether the drawing matches the ground. Every fit the model
+   makes goes to the gate (point 3); the review queue is for the fits the gate refuses and the pictures the model could
+   not fit, not the plan for every site. The number to grow is the count of fitted drawings.
+3. **A fit is accepted by numbers, never by a model's opinion.** Automatic acceptance goes through a gate validated
    on the existing hand fits with a held-out set (task 001). The human will check a random sample of 20 automatically
    accepted fits on the map; at least 18 must be right (the drawing's walls, streets or gardens on the matching
    features of today's ground). Anything the gate does not accept goes to the review queue.
-3. **Every picture is tied to its place with evidence a program can check**, recorded in its row: the file is in the
+4. **Every picture is tied to its place with evidence a program can check**, recorded in its row: the file is in the
    Commons category of the site's Wikidata item (P373), or its structured data says it depicts (P180) that item, or
    its title or caption names the place and the coordinates agree. Why: the Rijksmuseum's "Gezicht op Hampton Court"
    is Hampton Court in Herefordshire (its caption says so), not the palace; a name search alone gives the town for
    Barnard Castle and the village for Richard's Castle.
-4. **The map grows.** New sites come with their own old pictures, through `pipeline/sources.py` or something better.
+5. **The map grows.** New sites come with their own old pictures, through `pipeline/sources.py` or something better.
    Leads, none of them verified yet (check each one exists and is old enough before using it):
    - Jacob van Deventer's town plans: 64 towns not yet added (Commons "Maps by Jacob van Deventer").
    - Kip's bird's-eye views of houses and gardens: the large scans in Commons "Johannes Kip", "Britannia Illustrata".
@@ -34,7 +42,7 @@
      (1732); Maclauchlan's survey of the Roman Wall (1857); the German Limes reports (ORL, fort plans).
    - Stonehenge and Avebury: Hoare, *Ancient Wiltshire* (1812-21); Stukeley (1740s); Petrie's Stonehenge plan (1880).
    - Numancia: the 1860s excavation plans.
-5. **The page shows what changed.** New sites, new fits and review items appear on the existing page
+6. **The page shows what changed.** New sites, new fits and review items appear on the existing page
    (`web/index.html`, served by `server/serve.py`) without breaking anything that works today.
 
 ## Rules that do not change
```

## Hand-over

Iter 2 (2026-10-10). **Task finished** (Status: done). Final state for anyone who reads this later
(mostly the 999 goal check):

- PLAN.md is final: current state / architecture (the new `fit/` directory, module map, data flow) /
  tech choices with reasons / 8 assumptions / out of scope / GOAL→task map / waves 4/6/3/2/1 /
  test policy / empty `## Deviations from GOAL.md`. Re-read it before touching the task queue.
- Task queue complete: 001 (seed, wave 1), 200/201/202 (wave 1), 203 parent (split) with 203a/203b
  (waves 2/3), 204-210 (the seven growth leads), 211 (wave 4), 212 (wave 5, last). Every file has
  Status / Depends on / Touches; the book-machinery leads (207, 209) are in different waves because
  they share the data/books/ directory (per-book files only; 211 rebuilds the shared index).
- Test harness (owned by this task): tests/conftest.py (session `served` fixture: real serve.py on
  --port 0 against a temp copy of web/ + server/ + data/ minus data/raw/; `golden_sites` fixture),
  tests/test_serve.py, tests/test_data.py, tests/golden/hand_fit_sites.txt (19 hand-fit sites). Test
  state at close: 8 passed (both `.venv/bin/python -m pytest -q` and system `python3 -m pytest -q`).
  requirements.in/requirements.txt are pinned + hashed (the driver builds .venv from them).
- Standing rules for the build (also in CODEMAP.md top and PITFALLS.md): hand fits + private
  Finder/Amazon data never change; canonical data files only via 211/212; per-source staging only;
  one test file per task (conftest is this task's property); hermetic tests (port 0, temp tree, no
  network); the page's index.html gets exactly one edit (201's script tag).
- If the driver ever sends this task back: the likely cause is the schedule replay flagging shared
  files between same-wave tasks (most probable: 001's seeded `Touches: tests/` directory vs the
  specific test files of wave 1). Adjust the PLAN.md wave table, not the seeded 001 (it is the
  human's).
