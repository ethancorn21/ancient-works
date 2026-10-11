# Decisions and dead ends

Your journal: append only, newest at the bottom. When a task is finished, the driver moves its entries verbatim to
DECISIONS-archive.md (search it with grep) and lists the task in an index at the top of this file. Formats:

    ## <date> <task id> DECISION: <the choice>
    Chose X over Y because Z.

    ## <date> <task id> BLOCKER: <short title>
    - Attempt 1: tried A -> failed because B
    - Attempt 2: tried C -> failed because D

A fact that stays true after this task (a tool quirk, an environment limit, a trap in the code) is not a journal
entry: it goes to PITFALLS.md.

The task id is the task file's number, with its letters for a subtask (e.g. 025a).

## 2026-10-10 DRIVER: .venv could not be built from requirements.txt
    ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    Every package needs a pinned version and hash (AGENTS.md, Research and packages); full pip output: .agent/reports/venv.txt

## 2026-10-10 000 DECISION: new fitting-pipeline modules live in a new top-level fit/ directory, not pipeline/
    Chose a new `fit/` directory over adding to `pipeline/` because the seeded gate task 001 declares
    `Touches: pipeline/, tools/, docs/gate.md, tests/` and runs in wave 1 alongside 200/201/202; the team rule
    is per-file, and a directory-level declaration must be treated as covering the whole directory. fit/
    modules import pipeline/aw.py and pipeline/plan_fit.py read-only.

## 2026-10-10 000 DECISION: pinned requirements.txt generated with pip-compile --generate-hashes from a throwaway venv
    The driver's venv build failed (unpinned requirements.txt, see PROGRESS). Created requirements.in
    (numpy, scipy, pillow, tifffile, pyproj, rasterio, laspy[lazrs], requests, pyshp, pytest) and generated
    requirements.txt with pip-compile 7.6.2 from /tmp/aw-pto (throwaway venv outside the project, per AGENTS.md).
    Verified the driver's exact flow: .venv built with `pip install --require-hashes -r requirements.txt`, and
    `python3 -m pytest -q` passes (8 tests) under both .venv and system python. PyPI is reachable from this VM.

## 2026-10-10 000 DECISION: parallel source tasks write per-source staging files, consolidated once by task 211
    The seven growth leads (204-210) all run in one wave; if each wrote the shared data/catalog/extras.jsonl,
    data/commons/files.jsonl, classified.jsonl, web/data/plans.json and web/data/sites.json they would collide
    (the driver replays the schedule when shared files make tasks wait). Each source task therefore writes only
    its own extras_<src>.jsonl / files_<src>.jsonl / classified_<src>.jsonl plus its fit/src_<src>.py module;
    211 (wave 3) consolidates into the canonical files GOAL.md names, then runs build_catalog.py and
    tools/export_plans.py once. Same reason the batch (203a/b) writes only platefits docs + review items and
    212 alone runs the page-facing plan_fit sync (depictions + drawings counts in sites.json + the review list).

## 2026-10-10 000 DECISION: the batch is 203 (parent, split) with subtasks 203a (US) / 203b (rest of world)
    One batch over 384 sites is too big for one task and a single batch module would block wave 3 (211) behind
    it; splitting by region keeps 203b and 211 in the same wave (disjoint files). The parent's boxes are covered
    jointly by the two subtasks; the parent returns when both are done.

## 2026-10-10 000 OBSERVATION: plans.json rows may share an id; the page's P.byId collides on them
    Two rows each: one Commons picture depicting two sites ("The new Larned History..." for avebury +
    stonehenge; "File:Mayburgh-1769.png" for mayburgh-henge + king-arthur-s-round-table). Not a data error —
    the true key is (id, sites[0]). The page keeps only the last row in P.byId, so clicking one of the two list
    entries can open the wrong site's row. Fix scoped into 201 (fit tool keys by (id, site)); the test in
    000's test_data.py asserts (id, site) uniqueness, not id uniqueness. Also noted: web/data/sites.json
    entries only universally have id/name/lon/lat/corners/size_m/drawings — place/kind/qid are absent on some
    sites, so tests must not require them.
