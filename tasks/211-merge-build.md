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
- [ ] web/data/plans.json is refreshed with tools/export_plans.py: the new picture rows
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
(2026-10-12, iteration 180, agent a - boxes 1+2 done (committed 214c642); BOX 3 IN PROGRESS: a detached build run is alive and working through the last 18 of the 20 new sites - the next session MONITORS that run (never starts a duplicate), finishes box 3's verification + test when the run ends, then boxes 4-6)

State:
- BOX 1 DONE (iter 174): live merge - 381 staging rows into the three canonical files, pure growth (byte-identical prefix), idempotent, 0 refused, data/merge/log.jsonl.
- BOX 2 DONE (iter 175, committed 214c642): data/books/index.jsonl (1068 rows: 8 originals + civitates_liber2 118 + merian_helvete00zeil 60) + validation.json rebuilt with the machinery; 200 evidence re-recorded on all book rows; `fit/evidence.py check` passes offline (0 fail); tests/test_merge.py extended (5/5).
- BOX 3 IN PROGRESS (iters 176-180): 20 of the merged extras.jsonl's sids were unbuilt (173 of its 193 were already built by earlier waves). data/merge/run_build.py (committed 176) was nohup'd by session 179 and IS STILL ALIVE (checked with ps in 180): one `build_catalog.py --ids <sid>` subprocess per site, then `build_site.set_drawings(sid)`; append-only log = data/merge/build_sites.log. A killed session leaves a clean boundary at the last finished site; build_catalog skips already-built sites, so resuming with the remaining ids is always safe.
  - Built so far (5/20): beaumont-q95100, oudenaarde-q12992, soignies-q462985, luxembourg-city-q1842, aire-sur-la-lys-q259903. All carry LiDAR relief + block + an old map; every new sites.json entry has id/name/lon/lat/4 corners/size_m/drawings + the LiDAR credit (luxembourg oldest=1780 from Cassini).
  - Remaining (18, run order): avesnes-sur-helpe-q217178 bapaume-q317235 bavay-q477176 bethune-q207145 bouchain-q632348 cambrai-q181285 conde-sur-l-escaut-q494533 douai-q193826 gravelines-q323399 hesdin-q467366 landrecies-q632808 le-cateau-cambresis-q329103 le-quesnoy-q180067 maubeuge-q138648 saint-omer-q208793 therouanne-q261399 valenciennes-q163795 vieil-hesdin-q1022768 (each 2-5 min: national LiDAR fetch + Cassini/etat-major maps).
  - Mid-run invariant verified in 180: web/data/sites.json = 481 entries = HEAD 478 + {soignies, luxembourg-city, aire-sur-la-lys} (beaumont/oudenaarde were already in the HEAD snapshot); 0 removed, 0 changed shared entries (object-equality diff) - pure growth, exactly what the box demands. Re-check this at each session end.

Next session, in order:
1. `ps aux | grep -v grep | grep run_build` + tail data/merge/build_sites.log.
   - Run ALIVE: monitor (the log tail advances 2-5 min/site). Never start a duplicate - two writers race on web/data/sites.json. If the session is ending mid-run: record the last "=== <sid> ok" line in this hand-over, commit, stop; the run survives (it has now survived two session ends) and the driver snapshots its progress.
   - Run DEAD: read the log tail; resume the still-unbuilt of the 18 with `nohup .venv/bin/python data/merge/run_build.py <those ids...> &` (same log; done sites are skipped by build_catalog itself). "NOT BUILT: <sid>" = the machinery skipped it (no LiDAR and no old map, or the id matched no row); "FAILED" = non-zero exit, traceback in the log.
2. When all 20 sids have a terminal line in the log: verify the final invariants against `git show HEAD:web/data/sites.json` (never a working-tree snapshot): added set = exactly the built new sids; nothing removed; every HEAD entry unchanged (object equality); each built id has web/data/sites/<id>/{relief.jpg,block_*,depictions.json} and data/sites/<id>/site.json. Skips (if any) stay listed in the log - that is the box's "skipped and listed" end state. Then extend tests/test_merge.py with box 3's data-level tests (Notes: small fixed sample + full served-data invariants; hermetic - read-only assertions on the data, no rebuild, no network, no fixed ports) and tick box 3.
3. BOX 4: refresh web/data/plans.json with tools/export_plans.py (new picture rows present; every pre-merge (id, sites[0]) key still present; (id, sites[0]) stays unique). Do NOT re-run `pipeline/books.py match` (export_plans joins the existing matches.jsonl; re-matching against the grown extras could re-point pre-merge keys, which the box forbids). First resolve the re-read: tools/export_plans.py:main - confirm with the web/ consumers (grep for plans.json there) whether the "sites" column tracks the grown catalog or stays the stable pre-merge join (the box wording points to stable).
4. BOX 5: docs/sources.md - per-lead status consolidated from docs/lead_*.md (what was staged, what was dropped and why, per GOAL.md lead). Include: 207 stopped by the owner (no roman staging - a later merge re-run picks it up if it resumes); 213's view books now indexed (118 + 60 rows).
5. BOX 6: the human's reference - re-verify tests/test_serve.py's golden (25 hand fits / 19 sites; hermetic: port 0, temp tree, no network) at claim time.
6. CLAIM: 222-228 (the 7 source-guard fixes) were still OPEN when checked in 180 and gate the done-claim (the driver re-checks the suite; my branch's red set is exactly those 10 source-guard failures). When they land on main and the driver's sync brings them in, re-run the suite (expect fully green; the merge is idempotent, no re-run of it), finish any remaining boxes, tick, set Status: done.

Open thread: imagecodecs 2026.10.10 is installed in the .venv but NOT pinned in requirements.in/.txt (agent c's in-flight 302a/304 own those files) - a from-scratch venv rebuild would lose it and the AHN site builds would fail again (PITFALLS entry filed). File the pin task once c's requirements work has landed (or fold the check into the claim session).
## Lead note (2026-10-12)
207 (Roman books) is stopped by the owner; this consolidation runs without it. 207a/207b staging, if it ever resumes, goes through a later re-run of this step.
