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

## GOAL.md changed (2026-10-10 22:58)
The human changed GOAL.md. Update PLAN.md and the task queue to match: add tasks, change your own tasks, or set tasks that no longer fit to `Status: dropped`; keep finished work that still fits. Then check and tick the boxes above again. The change:
```diff
@@ -3,12 +3,15 @@
 Ancient Works is a map of old earthworks, castles, Roman forts, walled towns and lost gardens. Each built site shows
 today's ground (LiDAR relief where there is open LiDAR, the aerial photograph everywhere) and, on top of it, old
 pictures of the place. What makes a site worth opening is an **old drawing of the structure itself** (an
-antiquarian plan, a survey plate, a castle plan, a town plan, a bird's-eye view) laid over today's ground, so you see
+antiquarian plan, a survey plate, a castle plan, a town plan, a bird's-eye view, an artist's aerial view) laid over
+today's ground, so you see
 how little has changed. Plain survey sheets (Ordnance Survey, Cassini) do not count; they are background.
 
-Today 25 of 384 built sites have such a drawing fitted. On the map they are the red squares; the rest are small plain
-squares. The owner wants the red squares to be the rule: Stonehenge, Numancia, the Roman forts and every other built
-site should have at least one, and the map should keep growing with new sites that come with their own old pictures.
+Today 25 of 384 built sites have such a drawing fitted. The owner wants that to be the rule: Stonehenge, Numancia, the
+Roman forts and every other built site should have at least one, and the map should keep growing with new sites that
+come with their own old pictures. (Since 2026-10-10 the owner's copy of the map also colours sites whose only overlay
+is a survey sheet 150 or more years old. That does not change this goal: survey sheets are not drawings, and the
+number to grow is the count of fitted drawings.)
 
 ## What done looks like
 
@@ -35,6 +38,11 @@
    Barnard Castle and the village for Richard's Castle.
 5. **The map grows.** New sites come with their own old pictures, through `pipeline/sources.py` or something better.
    Leads, none of them verified yet (check each one exists and is old enough before using it):
+   - Artists' aerial and bird's-eye views count as much as surveys (owner, 2026-10-10, of Leonardo da Vinci's aerial
+     plan of Imola, 1502: "should 100% be on our map"). Leonardo's plan of Imola (Royal Collection, RCIN 912284;
+     there is no open LiDAR at Imola here, so it is an aerial-photograph site and its streets carry the fit); Jacopo
+     de' Barbari's view of Venice (1500); Braun and Hogenberg, *Civitates Orbis Terrarum* (1572-1617), hundreds of
+     walled towns; Merian, *Topographia* (1640s-1680s).
    - Jacob van Deventer's town plans: 64 towns not yet added (Commons "Maps by Jacob van Deventer").
    - Kip's bird's-eye views of houses and gardens: the large scans in Commons "Johannes Kip", "Britannia Illustrata".
    - Mackenzie, *The Castles of England* (1897): page 212, a five-towered castle with no caption.
```

## Hand-over

Iter 12 (2026-10-10). Driver reopened 000 for two GOAL.md changes (21:11: new point 2 — the local
model does the fitting itself; 22:58: artists' aerial/bird's-eye views count as drawings, new lead;
owner's copy also colours >=150-year survey-sheet-only sites — explicitly not a goal change).
This session did the planning update; it was cut near the end. **Remaining work is small (steps 1-6
below), then set Status: done.**

Done in this session (on disk; the task-file edits below ride in this commit, PLAN.md's edits are
uncommitted — the harness saves them):
- PLAN.md: current state (eight leads + the GOAL-change note), architecture diagram (fitkit sheet ->
  model -> solver -> gate; queue = overflow, not a plan for every site), module map (202 = starting
  point; 203a/203b = the model's fitting loop; `fit/src_artists.py` added), new tech choice "The model
  fits, the gate decides" (pipeline/llm.py at $AW_LLM_URL; the model step is an injectable function so
  tests stay hermetic), assumption 3 reworded, NEW assumption 9 (owner's-copy survey colouring is out
  of scope), out-of-scope bullet, six-point GOAL->task map, waves 4/7/3/2/1 (213 in wave 2), test
  policy (no test calls the model server).
- Tasks: 202 (goal: starting point, never a fit), 201 (queue = overflow per point 2), 203 (parent goal
  + loop note), 203a (model loop: fitkit sheet -> >=4 matched-feature pairs -> solver -> gate;
  injectable model step; test = no model-server call), 203b (goal wording).
- Verified facts: no package.json (test command `python3 -m pytest -q`); .venv exists here and has the
  deps (system python3 does NOT); fitkit has `sheet`/`zoom`/`save`/`check`/`lonlat`; pipeline/llm.py
  has `ask`/`ask_json` (URL = $AW_LLM_URL, default 127.0.0.1:18080); 001 is blocked awaiting the
  owner's box-2 ruling (1 in 8 vs 1 in 20) — the batch stays behind it, which is why it could be edited
  pre-run.

Next steps (in order):
1. `tasks/212-cover-final.md`: my 3 edits were rejected atomically (whitespace mismatch — the file
   wraps lines differently than head showed). Redo after checking exact text with `sed -n '25,35p'
   tasks/212-cover-final.md | cat -A` and `sed -n '55,70p' ... | cat -A`: (a) goal line "a found picture
   becomes a candidate through the normal loop (propose ->\n      fit -> gate)" -> "(fitkit sheet ->\n
   model fit -> fit -> gate)"; (b) box 1 "the site goes through the normal loop (propose -> fit ->
   gate)" -> "(fitkit sheet -> model fit -> fit -> gate)"; (c) Notes "the human's 18/20 check
   (GOAL.md point 2)" -> "(GOAL.md point 3)".
2. CREATE `tasks/213-artist-views.md` (lowest free number in 200-499; 200-212 taken, 800/801 outside
   the band). Format like tasks/204-van-deventer.md. `Status: open` / `# 213: Artists' views -
   Leonardo's Imola, Barbari's Venice, Braun & Hogenberg, Merian` / `Depends on: 200` / `Touches:
   fit/src_artists.py, data/catalog/extras_artists.jsonl, data/commons/files_artists.jsonl,
   data/commons/classified_artists.jsonl, docs/lead_artists.md, tests/test_src_artists.py`. Goal:
   GOAL point 5's new lead (owner, of Leonardo's 1502 Imola plan: "should 100% be on our map"): verify
   each source exists + age + free machine-readable access (views of the structure are exempt from the
   150-year rule), tie with 200's evidence, stage in this task's own files; 211 consolidates + builds,
   212's cover pass runs the model's fitting loop. Imola is the anchor: NEW site, no open LiDAR here ->
   aerial-photograph site, its streets carry the fit (FITKIT_GROUND=aerial, fixed landmarks). Boxes:
   per-source verification in docs/lead_artists.md (documented drop beats a guessed row); Imola staged
   as a new site (extras row: id/name/place/lon-lat/region/kind/QID/wikipedia; files row with 200
   evidence + classified row; row notes no LiDAR/aerial ground); hand-checked file->QID table in
   fit/src_artists.py (sources.py pattern; Barnard Castle trap; existing-catalog QID -> picture row for
   the existing site, no new entry); at least Imola + one further source staged; IF Civitates/Merian
   turn out to be IA books, declare the exact per-book data/books/ paths in this task's Touches first
   (the 208 pattern); hermetic test (staged files join + evidence check + golden sample). Notes:
   Leonardo (Royal Collection) and Barbari are image-level like leads 204-206; split into 213a-... by
   source if it grows past a few sessions.
3. `CODEMAP.md` top: replace "- (none yet: add the rules every change must respect, e.g. ..." under
   "Architecture rules:" with the standing rules (my iter-2 hand-over claimed they were here; they
   were never written): (1) the 25 hand fits (pre-batch data/db/platefits/ docs, data/sites/*/site.json
   plates) and the private Finder/Amazon data are never changed or deleted by new code or tests; (2)
   new fitting code lives in fit/ (one module per task) and imports pipeline/ (aw.py, plan_fit.py,
   llm.py, books.py) read-only; (3) per-source staging only — canonical files (data/catalog/extras
   .jsonl, data/commons/files.jsonl + classified.jsonl, data/books/index.jsonl + validation.json,
   web/data/sites.json, web/data/plans.json) written only by 211 (merge) and 212 (cover/sync); (4) the
   fitting loop treats the model as a lead, not a fact: fitkit sheet, >= 4 matched-feature pairs, gate
   (001) score required before anything reaches data/db/platefits/; the model step is injectable so
   tests never call the model server (no network, port 0, temp tree); (5) web/index.html takes exactly
   one change for the whole build (201's script tag); the review section lives in web/review.js.
4. DONE - the DECISIONS.md entry `## 2026-10-10 000 DECISION: plan re-checked for the two GOAL changes
   ...` is appended (committed with this hand-over). Steps 5-6 remain:
5. Check every task file (001, 200-213, 800, 801) has `Depends on:` and `Touches:` lines:
   `grep -L "Depends on:" tasks/*.md; grep -L "Touches:" tasks/*.md` (expect no output).
6. Verify the test command: `.venv/bin/python -m pytest -q` in the checkout (expect the suite green —
   last known: 8 passed at iter 2 close; nothing here touches code). Then tick all seven acceptance
   boxes of 000 (they are all met by the state above) and set the first line to `Status: done`.

If the driver sends this back again: same procedure — diff GOAL.md against PLAN.md's task map, edit
only planner-created task files (never 001), new leads take the lowest free 200-499 number with
Depends on + Touches, re-check the boxes, re-set Status.
