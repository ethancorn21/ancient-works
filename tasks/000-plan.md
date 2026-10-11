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
- Task file format: tasks/README.md. Every task file starts with the line `Status: open`.
- Research what you need (web_search, web_fetch) before settling on a stack you are unsure of; say why in PLAN.md.
- A question only the human can answer (an account, hardware, a preference that changes the plan): ask_human. Prefer a stated assumption in PLAN.md and a non-blocking question over waiting.
- This task is the plan only: create PLAN.md, the task files and the test setup, not the product.
- When every box above is ticked, set this file's first line to `Status: done`: that is what ends the planning task.
- Two agents build this project at the same time, each in its own checkout; a task goes to one agent once all its `Depends on:` tasks are finished, and never while the other agent works on a task that touches the same files. Put shared foundations first (project skeleton, data model, the interfaces between modules), so the later tasks can go ahead independently. A subtask that needs the result of another task says so in its own `Depends on:` line. Avoid hotspot files: when many tasks would edit the same file (README, a central config module, the sample config), give each module its own file or section, or make those edits once in an early task; the driver replays the schedule and sends the plan back once if shared files make tasks wait that their dependencies would let run at once. List only real dependencies: tasks that touch the same files are already kept apart.

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
