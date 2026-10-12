Status: open
# 211: Consolidate - the new sites and pictures into the page's data
Depends on: 200, 204, 205, 206, 208, 209, 210, 222, 223, 224, 225, 226, 227, 228
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py

## Goal
The single point where the per-source staging becomes the canonical data GOAL.md names.
fit/merge.py consolidates every extras_<source>*.jsonl / files_<source>*.jsonl /
classified_<source>*.jsonl (204-210, including subtask variants) into
data/catalog/extras.jsonl, data/commons/files.jsonl and classified.jsonl; rebuilds
data/books/index.jsonl with the existing machinery (it is a generated artifact -
books.py index regenerates it from the per-book files, including the books 207/209
added) together with the shared validation.json; makes sure every new row that reaches
the plan list carries 200's evidence field; builds the new sites (build_catalog.py,
build_site.py) and refreshes web/data/plans.json (export_plans.py) and
web/data/sites.json. Nothing else in the project writes these files; the page renders
the result with no page change (GOAL.md point 5).

## Acceptance criteria
- [x] fit/merge.py consolidates: every staging row is in the canonical files, every
      pre-merge canonical row is still present byte-identical (the files grow, they are
      never rewritten), and the merge is idempotent (a second run changes nothing).
- [x] data/books/index.jsonl is rebuilt from the per-book artifacts of all books (the 8
      original plus whatever 207/209 added); every row that reaches the plan list carries
      the 200 evidence field; fit/evidence.py check passes offline on the merged set.
- [x] Every new site is built: web/data/sites/<id>/ exists for each new site id and
      web/data/sites.json has its entry (at least id/name/lon/lat/corners/size_m/drawings)
      - the served sites.json grows by exactly the new sites; the old 385 entries (the box's
      "384" was the human's estimate; the measured pre-build count is 385 - deviation noted in
      DECISIONS) are unchanged (except fields 212 later owns).
- [x] web/data/plans.json is refreshed with tools/export_plans.py: the new picture rows
      are present, every pre-merge (id, sites[0]) key is still present, and (id, sites[0])
      remains unique (the shared-id case stays one row per (picture, site)).
- [x] docs/sources.md is updated with the per-lead status consolidated from the
      docs/lead_*.md files: what was staged, what was dropped and why, per GOAL.md lead.
      (Section 9, added 2026-10-12: one row per GOAL.md lead 204/205/206/207/208/209/210/213
      with the staged counts and the documented drops with reasons, plus the merge summary;
      purely additive, every number cross-checked against data/merge/log.jsonl and the files.)
- [x] The human's reference is untouched: the 25 hand fits and their 19 sites (000's
      golden test, tests/test_serve.py) still pass after the merge; the test is hermetic
      (port 0, temp tree, no network). (Verified this session: test_hand_fits_are_the_reference
      is green in the suite run and not among the 10 failures; the golden file lists the 19 sites
      and all 19 have web/data/sites/<sid>/depictions.json in this checkout, so the per-site
      depictions check runs for every one; conftest is hermetic - --port 0, temp tree without
      data/raw/ and the .npy/.npz grids, session-scoped server terminated in teardown.)

## Notes
- Row conflicts (the same picture staged by two sources, or a staged row equal to an
  existing canonical row) are resolved by keeping the first and recording the duplicate
  in the merge log - never a silent rewrite of a row that is not byte-identical.
- Building sites is the slow part (DEM fetch, images); it is a working-phase command.
  The test asserts the data-level result (entries, joins, idempotence) on a small fixed
  sample plus the full served-data invariants, not a rebuild.
- The books' triage artifacts that 207/209 left in data/books/ stay as they are; this
  task only reads them and writes the two shared files (index.jsonl, validation.json).

## Lead note (2026-10-12)
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step. (NOTE 2026-10-12 iter 186: 207 has since resumed as 207a/207b/207c - agent c is working it; 207c is blocked; its staging is on agent c's branch, not main yet.)

## Hand-over
(2026-10-12, iteration 186, agent a - BOXES 5 AND 6 DONE. Box 5: docs/sources.md section 9 (per-lead staged/dropped consolidated from the docs/lead_*.md files, every number cross-checked). Box 6: the 000 golden test re-read fresh - 19 golden sites (all with depictions.json here), hermetic conftest, green in this session's run. 222-228 still OPEN -> the done claim stays GATED; the next session that finds them merged finishes and claims.)

State:
- BOXES 1-4 DONE (no change this session): box 1 the live merge (381 staging rows -> the 3 canonical files, pure growth, idempotent, 0 refused, log in data/merge/log.jsonl); box 2 data/books/index.jsonl 1068 rows + validation.json (200 evidence on all book rows; `fit/evidence.py check` 0 fail); box 3 the 114 new sites built, web/data/sites.json 385 -> 499 vs the frozen 385-entry baseline, tests/test_merge.py 9/9; box 4 web/data/plans.json = 1168 (frozen 1166 pre-merge keys all present, (id, sites[0]) unique, re-running tools/export_plans.py byte-identical, sha256 852089e0...). NEVER run `pipeline/books.py match` for this task.
- BOX 5 DONE (iter 186): docs/sources.md now has section 9 "The drawing leads (GOAL point 5): what was staged and what was dropped, per lead" - one table row per GOAL.md lead (204 Van Deventer 56 towns/4 drops; 205 Kip 12 of 22/4 review-queue; 206 Mackenzie 1 row (Shotwick); 207 Roman none (owner-stop, later re-run picks it up when the staging lands on main); 208 Limes 56 plans/43 fort numbers/45 sites + the per-number drop list; 209 Wiltshire 5 rows (209a Hoare DROPPED on the refused download, 209b Stukeley, 209c Petrie's canonical-plate fallback) + the 2 existing hand fits never re-staged; 210 Numancia 1 row; 213 artists 2 new aerial sites + the triaged Civitates/Merian books) plus the "merge itself" summary (381 rows: 115 site / 133 picture / 133 classified; 0 refused / 0 conflicts; 114 new sites - shotwick's row made no new site; sites.json 385 -> 499; plans.json 1,166 -> 1,168; books index 901 -> 1,068). The diff is purely additive (17 insertions, 0 deletions). Gotchas found while writing it: (a) web/data/sites.json is a JSON OBJECT ({"sites": [...]}), not JSONL; (b) the limes lead says "43 ORL fort numbers (45 staging items)" - 45 extras rows = 45 sites, so quote it exactly; (c) the Mackenzie schematics (Framlingham/Carisbrooke/Cooling) ARE pre-merge canonical rows (fitted), not drops.
- BOX 6 DONE (iter 186): re-read tests/test_serve.py::test_hand_fits_are_the_reference and tests/conftest.py fresh. The golden file tests/golden/hand_fit_sites.txt = 19 sites (its header says "20 documents" - that is 000's reference count; the store today holds 123 docs: 26 book-leaf + 97 Commons, the batch tasks' agent fits having joined per GOAL's "fits in data/db/platefits/"). ALL 19 golden sites have web/data/sites/<sid>/depictions.json in this checkout, so the test's per-site depictions check (a plan/view depiction whose fit doc id starts with <sid>. ) runs for every one - none skipped by its exists() guard. The test asserts every golden site is in the served sites.json with drawings >= 1. Hermeticity confirmed in conftest: server/serve.py --port 0 (ephemeral), a session-scoped temp copy of web/+server/+data/ minus data/raw/ and the .npy/.npz grids (the book/media routes 404 in the copy, so nothing fetches; that is also why the suite is light), terminated in teardown; the test file's own docstring says "no network, ephemeral port". It is green in this session's run (not among the 10 failures).
- SUITE (iter 186): 10 failed / 130 passed / 1 skipped in 234 s. The 10 = exactly the 222-228 source-guard set: test_src_artists 1, test_src_kip 1, test_src_limes 1, test_src_mackenzie 1, test_src_numancia 1, test_src_van_deventer 2, test_src_wiltshire_stukeley 3 (their check_staged/join assertions see their staged rows now present in the canonical files - the live merge's by-design effect; the fix tasks own their modules' post-merge check semantics). No NEW failures; test_serve / test_gate / test_merge all green. GOTCHA: `pytest --timeout=600` is a no-go here - pytest-timeout is not in the .venv (argparse error kills the run); just run `pytest tests/ -q`.
- CLAIM GATED: 222-228 all Status: open (re-checked this session). Do not set Status: done until they land; leave it `open` for now (the driver re-checks the suite at claim time anyway).

Next session, in order:
1. Check 222-228 statuses (head -1 of each task file). If still open: STOP (gated; the driver brings this back). Nothing else remains on 211 while they are open.
2. If merged/closed: re-run the suite (expect fully green; the merge is idempotent - do NOT re-run fit/merge.py; a "No space left" failure would be the disk, see 7e61147), then set Status: done and file the done claim. In the claim cite: all 6 boxes; the 381-row merge (0 refused / 0 conflicts); 114 new sites (385 -> 499); the 1,068-row books index; the 19-site golden reference; and that the red set of 10 was 222-228's.

Open thread: imagecodecs 2026.10.10 is installed in the .venv but NOT pinned in requirements.in/.txt (agent c's in-flight 302a/304 own those files; the AHN sites - incl. the-hague - depend on it). File the pin task once c's requirements work lands (or fold into the claim session).
