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
- [ ] Every new site is built: web/data/sites/<id>/ exists for each new site id and
      web/data/sites.json has its entry (at least id/name/lon/lat/corners/size_m/drawings)
      - the served sites.json grows by exactly the new sites; the old 384 entries are
      unchanged (except fields 212 later owns).
- [x] web/data/plans.json is refreshed with tools/export_plans.py: the new picture rows
      are present, every pre-merge (id, sites[0]) key is still present, and (id, sites[0])
      remains unique (the shared-id case stays one row per (picture, site)).
- [ ] docs/sources.md is updated with the per-lead status consolidated from the
      docs/lead_*.md files: what was staged, what was dropped and why, per GOAL.md lead.
- [ ] The human's reference is untouched: the 25 hand fits and their 19 sites (000's
      golden test, tests/test_serve.py) still pass after the merge; the test is hermetic
      (port 0, temp tree, no network).

## Notes
- Row conflicts (the same picture staged by two sources, or a staged row equal to an
  existing canonical row) are resolved by keeping the first and recording the duplicate
  in the merge log - never a silent rewrite of a row that is not byte-identical.
- Building sites is the slow part (DEM fetch, images); it is a working-phase command.
  The test asserts the data-level result (entries, joins, idempotence) on a small fixed
  sample plus the full served-data invariants, not a rebuild.
- The books' triage artifacts that 207/209 left in data/books/ stay as they are; this
  task only reads them and writes the two shared files (index.jsonl, validation.json).

## Hand-over
(2026-10-12, iteration 182, agent a - BOX 4 verified and ticked this session (the refresh had already happened in the unlogged sessions; re-running the export is byte-identical; the re-read resolved as a stable pre-merge matches.jsonl join); BOX 3 still mid-run: 12 of 23 "ok" (last conde), douai building, 10 in the queue - next session MONITORS (never duplicates), then box 3's verify+test, then boxes 5-6; the claim stays gated on 222-228)

State:
- BOX 1 DONE (iter 174): live merge - 381 staging rows into the three canonical files, pure growth (byte-identical prefix), idempotent, 0 refused, data/merge/log.jsonl.
- BOX 2 DONE (iter 175, committed 214c642): data/books/index.jsonl (1068 rows: 8 originals + civitates_liber2 118 + merian_helvete00zeil 60) + validation.json rebuilt with the machinery; 200 evidence re-recorded on all book rows; `fit/evidence.py check` passes offline (0 fail); tests/test_merge.py extended.
- BOX 4 DONE (iter 182): web/data/plans.json = 1168 rows (890 book rows, the 8 original books + 278 commons; the 2 NEW commons rows are shotwick-castle-q7502621 and numancia - the only 2 of the 133 merged picture rows with local copies; the 167 newly indexed book rows have no local full pages and are correctly absent). The refresh had ALREADY happened in unlogged sessions 176-179 (driver snapshot 27a6053), which session 180's reconstruction missed. Verified: re-running `.venv/bin/python tools/export_plans.py` on the current tree is byte-identical (sha256 852089e00006...aab4add), so the committed file is the tool's stable output on current data (not stale); the frozen pre-merge key list data/merge/plans_premerge_keys.jsonl (1166 keys, from the pre-merge plans.json) is a subset of the current keys; (id, sites[0]) is unique; tests/test_merge.py 6/6 (incl. test_plan_list_refresh_is_pure_growth, written in the unlogged session). Re-read resolved: main() joins the EXISTING data/books/matches.jsonl (890 rows, pre-merge) - the stable pre-merge join, no re-matching; the data/catalog/sites.jsonl map only resolves ambiguous-candidate names to ids; 0 (site,title) shadowing collisions between pre-merge (797) and merged (133 new) classified rows, so the dict-later-wins build in commons_rows() cannot flip a pre-merge row. NEVER run `pipeline/books.py match` for this task.
- BOX 3 IN PROGRESS (iters 176-182): the detached `data/merge/run_build.py` (nohup'd; pid 4098676 in 182) is ALIVE: one `build_catalog.py --ids <sid>` subprocess per site, then `build_site.set_drawings(sid)`; append-only log = data/merge/build_sites.log. A killed session leaves a clean boundary at the last finished site; build_catalog skips already-built sites, so resuming with the remaining ids is always safe.
  - Run 3 (started 21:18Z, 23 ids) has 12 "ok" lines: beaumont-q95100, oudenaarde-q12992, soignies-q462985, luxembourg-city-q1842, aire-sur-la-lys-q259903, avesnes-sur-helpe-q217178, bapaume-q317235, bavay-q477176, bethune-q207145, bouchain-q632348, cambrai-q181285, conde-sur-l-escaut-q494533 (last: 21:47Z). Building now: douai-q193826. Queue after douai (10, each 2-5 min: national LiDAR + Cassini/etat-major): gravelines-q323399 hesdin-q467366 landrecies-q632808 le-cateau-cambresis-q329103 le-quesnoy-q180067 maubeuge-q138648 saint-omer-q208793 therouanne-q261399 valenciennes-q163795 vieil-hesdin-q1022768. (beaumont/oudenaarde were already in the HEAD snapshot when run 3 started; the box's target set is the 20 originally-unbuilt sids - at verify time count terminal lines per sid from the log.)
  - Every built site carries LiDAR relief + block + old maps; every new sites.json entry has id/name/lon/lat/4 corners/size_m/drawings + the LiDAR credit. Mid-run invariant re-checked in 182: worktree delta vs HEAD's sites.json = only the in-flight conde (0 removed, 0 changed) - pure growth.

Next session, in order:
1. `ps aux | grep -v grep | grep run_build` + tail data/merge/build_sites.log.
   - Run ALIVE: monitor only (the log tail advances 2-5 min/site). Never start a duplicate - two writers race on web/data/sites.json. If the session ends mid-run: record the last "=== <sid> ok" line in this hand-over, commit, stop; the run survives (now three+ session ends) and the driver snapshots its progress.
   - Run DEAD: read the log's terminal lines ("=== <sid> ok ===" / "NOT BUILT: <sid>" = skipped and listed / "FAILED" = traceback in the log); resume the still-unbuilt: `nohup .venv/bin/python data/merge/run_build.py <those ids...> &` (same log; done sites are skipped by build_catalog itself).
2. When all 20 target sids have a terminal line: verify the final invariants against `git show HEAD:web/data/sites.json` (never a worktree snapshot): added set = exactly the built new sids; nothing removed; every HEAD entry unchanged (object equality); each built id has web/data/sites/<id>/{relief.jpg,block_*,depictions.json} and data/sites/<id>/site.json. Skips (if any) stay listed in the log - that is the box's "skipped and listed" end state. Then extend tests/test_merge.py with box 3's data-level tests (Notes: small fixed sample + full served-data invariants; hermetic - read-only assertions on the data, no rebuild, no network, no fixed ports) and tick box 3.
3. BOX 5: docs/sources.md - per-lead status consolidated from the docs/lead_*.md files: what was staged, what was dropped and why, per GOAL.md lead. Include: 207 stopped by the owner (no roman staging - a later merge re-run picks it up if it resumes); 213's view books now indexed (civitates 118 + merian 60 rows, box 2).
4. BOX 6: the human's reference - re-verify tests/test_serve.py's golden (25 hand fits / 19 sites; hermetic: port 0, temp tree, no network) at claim time.
5. CLAIM: 222-228 (the 7 source-guard fixes) were still OPEN when checked in 182 and gate the done-claim (the driver re-checks the suite; my branch's red set is exactly those 10 source-guard failures). When they land on main and the driver's sync brings them in: re-run the suite (expect fully green; the merge is idempotent - no re-run of it), finish any remaining boxes, tick, set Status: done.

Open thread: imagecodecs 2026.10.10 is installed in the .venv but NOT pinned in requirements.in/.txt (agent c's in-flight 302a/304 own those files) - a from-scratch venv rebuild would lose it and the AHN site builds would fail again (PITFALLS entry filed). File the pin task once c's requirements work has landed (or fold the check into the claim session).

## Lead note (2026-10-12)
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step.
