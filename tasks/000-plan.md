Status: open
# 000: Plan the project from GOAL.md

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

## Hand-over

Iter 1 (2026-10-10). What exists now (committed or saved by harness, NOT yet in git):
- `PLAN.md` (root): full plan — current state, architecture (new `fit/` dir, module map, data-flow), tech
  choices, 8 assumptions, out-of-scope, GOAL→task map, waves 4/8/2/1, test policy, empty Deviations section.
- `requirements.in` + `requirements.txt` (pinned, `--hash=` lines; made with pip-compile 7.6.2 from throwaway
  venv /tmp/aw-pto). Fixes the driver's venv-build failure (PROGRESS note). `.venv/` was built from it and works.
- `server/serve.py`: prints the actually-bound address (was `a.port`, useless for `--port 0`); default port 8642 unchanged.
- `tests/`: `conftest.py` (session fixture `served` — real serve.py on `--port 0` over a temp copy of web/, server/,
  data/ minus data/raw/; `golden_sites` fixture; get/get_json/put_json helpers), `test_serve.py` (5 tests incl.
  golden hand-fit reference), `test_data.py` (3 tests: plans.json↔books index, plans.json↔commons files, catalog.json),
  `golden/hand_fit_sites.txt` (19 site ids of the 20 hand-fit docs).
- Task files `tasks/200-evidence.md`, `201-review.md`, `202-propose.md` (wave 1; 001 is the seeded fourth).

Test state at last run: **8 passed** (`.venv/bin/python -m pytest -q` and system `python3 -m pytest -q`).

STILL TO DO (in this order):
1. Write the remaining task files exactly as the wave table in PLAN.md says:
   - `tasks/203-batch-fit.md` — PARENT, `Status: split`; subtasks below cover its boxes; put the rest-of-work plan in its `## Hand-over`.
     Boxes: whole loop per built site (candidates from plans.json → propose → plan_fit solver → gate 001 → auto platefits doc with score OR review item); never touches hand fits (test asserts bytes unchanged); report docs/batch.md with counts + seeded 20-sample for the human's 18/20 check.
   - `tasks/203a-batch-us.md` — `Depends on: 001, 200, 201, 202`; `Touches: fit/batch_us.py, data/db/platefits/, data/review/, tests/test_batch_us.py`. US built sites (region "US").
   - `tasks/203b-batch-eu.md` — `Depends on: 203a`; `Touches: fit/batch_eu.py, data/db/platefits/, data/review/, tests/test_batch_eu.py`. All non-US built sites. (203b writes EU docs only after 203a merged; both import a shared helper — 203b imports 203a's, does not re-write it.)
   - `tasks/204-van-deventer.md` (64 towns, Commons category; split into 204a/b batches of ~16 if too big),
     `205-kip.md` (Kip & Knyff bird's-eye views), `206-mackenzie-p212.md` (identify the uncaptioned five-towered castle; drop with evidence if unidentifiable),
     `207-roman-books.md` (Roy 1793 / Horsley 1732 / Maclauchlan 1857 via the existing books machinery),
     `208-limes.md` (German Limes plans — least certain lead; document + drop if not free/machine-readable),
     `209-wiltshire.md` (Hoare/Stukeley/Petrie for the existing Stonehenge/Avebury sites), `210-numancia.md` (1860s excavation plans).
     All sources: `Depends on: 200`; `Touches: fit/src_<name>.py, data/catalog/extras_<name>.jsonl, data/commons/files_<name>.jsonl, data/commons/classified_<name>.jsonl, tests/test_src_<name>.py` — their own staging files ONLY (211 consolidates into the canonical files; do not write extras.jsonl/files.jsonl/plans.json/sites.json from a source task).
   - `tasks/211-merge-build.md` — `Depends on: 200, 204, 205, 206, 207, 208, 209, 210`; `Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, web/data/sites.json, web/data/plans.json, tests/test_merge.py`. Consolidate per-source staging into the canonical files, run build_catalog.py --ids for the new sites, run tools/export_plans.py, refresh web/data/plans.json.
   - `tasks/212-cover-final.md` — `Depends on: 203a, 203b, 211`; `Touches: fit/cover.py, data/review/, web/data/review.json, docs/batch.md, tests/test_cover.py`. Targeted Commons/Wikidata picture search for built sites still without candidates; re-run the batch over the new material; the ONLY task that runs the page-facing plan_fit sync (updates site depictions + drawings counts) and writes the final report + the current 20-sample list.
2. Add to `tasks/000-plan.md` right after the `# 000:` title line: `Depends on: none` and
   `Touches: PLAN.md, CODEMAP.md, tasks/, requirements.in, requirements.txt, tests/, server/serve.py`.
3. `CODEMAP.md` hand-written top: add the architecture rules (fit/ dir rule; hand fits + Finder/Amazon data never modified; one test file per task, conftest owned by 000; page edited only by 201; tests hermetic/port 0) — text from PLAN.md "Tech choices"/"Test policy".
4. Add PITFALLS entries: (a) driver venv needs ==-pinned + hashed requirements.txt (generate from requirements.in with pip-compile --generate-hashes in a throwaway venv; PyPI reachable, cp312 wheels fine); (b) sites.json universal keys are only id/name/lon/lat/corners/size_m/drawings (place/kind/qid missing on some); (c) plans.json rows may share an id when one picture depicts two sites — key by (id, sites[0]); the page's P.byId collides on that (fix scoped to 201); (d) serve.py runs plan_fit only after a platefits write, never at startup — GET-only test servers are safe/offline.
5. Run `.venv/bin/python -m pytest -q` (expect 8 passed) and tick 000's acceptance boxes against the finished state (all should tick: PLAN.md complete; GOAL points 1-5 mapped in the task map; tasks 200-212 + subtasks exist with Goal/boxes/Depends/Touches; test command green; waves 4/8/2/1; no fixed ports). Set 000 `Status: done`.
6. Commit everything: `git add -A && git commit -m "000: plan - PLAN.md, task queue 200-212, pinned hashed requirements, test harness"`.

Design decisions (details in DECISIONS.md): fit/ is a NEW directory because 001 declares pipeline/ and tools/
in wave 1; batch tasks write only platefits docs + review items, page-facing sync only in 212 (keeps wave 3 file-disjoint);
per-source staging files consolidated once by 211 (keeps wave 2 file-disjoint). The human's 25 hand fits and all
Finder/Amazon private data stay untouched by every task.
