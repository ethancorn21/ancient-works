Status: dropped
# 304: Fit a drawing against the old survey map, not the ground - the third try at an automatic fit
Depends on: 302b
Touches: fit/surveyfit.py, fit/surveyfit_heldout.py, data/surveyfit/, tests/test_surveyfit.py, docs/site_flow.md, requirements.in, requirements.txt

## Goal
Two automatic fits have failed: the vision model invents its points (301), and drawing ink against LiDAR relief lands
231-2204 m off on the 21 hand fits (302b, data/inkfit/heldout/results.json). The owner (2026-10-11) chose to try
once more while he fits by hand (305). The idea: many sites already have an old survey map placed on the ground
(the OS six-inch 1st edition, Cassini, the Etat-major: kind "map" in the site's depictions.json, already
georeferenced). A survey map and an antiquarian plan are both ink drawings of the same banks and ditches, often from
the same decades, so matching drawing to drawing should be far easier than drawing to relief. Fit the plan to the
survey sheet, then carry the sheet's georeference over.

## Acceptance criteria
- [ ] fit/surveyfit.py: matching points found between the plan and the site's survey sheet from the images
      themselves (features, line structure, any method you choose, GPU optional if a free card is given to you;
      not a model's list of coordinates), a similarity fit through the sheet's georeference, and a confidence score.
- [ ] The 302b protocol, unchanged in spirit: pre-registered in docs/site_flow.md before the one run, the 21 hand
      fits as truth, held out, a search-matched null, one table (corner error m, rotation, scale, confidence) -
      reported as it comes out. Hand fits whose site has no survey sheet are listed as "no sheet", not dropped.
- [ ] The verdict, written plainly next to the table: the method passes only if a confidence threshold exists under
      which every accepted fit is within 60 m of the hand fit and at least 5 of the 21 are accepted. If it passes,
      write 304b (wire it into tools/site_done.py's fit step, confident -> map, unsure -> review with the reason).
      If it fails, say so, and stop: no wiring, no fourth method.

## Notes
- The hand fits and their golden file stay untouched. 302c and 302d are dropped (the ink fit failed its test).
- Do not take any other task; the lead gives the next one.

## Hand-over

(2026-10-12, iteration 91, agent c - session 7. The lead directed: freeze the stub as it is
(it was already frozen with the method), do the live canaries, then the one-shot run. DONE:
both Re-read passes, stub suite re-confirmed 7/7, 3 live canaries eyeballed, devlog written,
the freeze committed as 156aa19, the held-out evaluator written and selfchecked 21/21.
The ONE RUN has NOT started - it is the entire next step.)

**State.** Status: in-progress. Freeze commit **156aa19** contains: data/surveyfit/devlog.md
(new), the 304 section of docs/site_flow.md (amended AT the freeze: frozen config restated
with hash **737508d**, the pre-freeze canaries recorded, sheet count corrected 15->13 of 19),
and fit/surveyfit_heldout.py (new evaluator, mirrors inkfit_heldout). **fit/surveyfit.py is
FROZEN as of 737508d - never touch it again.** Stub suite 7/7 (last full suite per session 6:
75 passed, 1 skipped - re-run after any main merge). ELoFTR answers at 127.0.0.1:8091
(health-checked this session). Evaluator selfcheck: 21/21 OK (0.0 m / 0.0 deg / 1.0). The run
is **22 pairs**: the 21 sheets + the camp-d-attila aerial (row 11, right after its sheet row).

**Canaries (this session, all --no-null, live service; full table in data/surveyfit/devlog.md):**
- maiden (held-out #14, the lead's directed canary): 43 calls, 215 s; chosen theta=94
  (20 pairs / 6 inliers / score 0.2048 / conf 0.0419) - EYEBALL: polygon ~1 km NW of the
  hillfort, OFF (the inlier-fraction score preferred a small tight cluster); the SAME run's
  theta=0 call: 625 pairs / 31 inliers / 0.0311 = the lead's raw smoke (his: 633 pairs - the
  service's pair count drifts a few % between calls). No tuning from any of this.
- barnard (NOT held-out): 43 calls, 44 s; theta=216, 3 pairs / 3 inliers / 0.7262 /
  conf 0.5274 (no null run); polygon ON the earthworks. Note: the frozen score has no
  minimum-pair floor (3/3 -> 0.73) - a method property, not tuned from.
- avaricum (NOT held-out): 43 calls, 98 s; theta=0, 9 pairs / 3 inliers / 0.2364 / 0.0559;
  polygon ON the earthworks.
- Per-call wall time scales with the sheet's PNG re-encode: ~1 s (533 px), ~2.3 s (1600 px),
  ~5 s (dense 1066 px). Full sweep = 43 calls + 2 null calls per doc; expect the whole run
  ~30-60 min. Smoke artifacts: .agent/smoke_{maiden,barnard,avaricum}.{json,log},
  .agent/eyeball_*.png, .agent/eyeball.py (all gitignored).

**Acceptance boxes:** still none ticked. Box 1 (matching points from the images, similarity
through the georeference, confidence) is now proven on real sites (canaries) - tick it once
the one run has produced its table (the run is the box-2 deliverable, so tick 1 and 2
together, after). Box 3 (the verdict written plainly) comes with the table.

**Next step (session 8) - THE ONE RUN (the owner is waiting on the table):**
1. `cd <checkout> && nohup .venv/bin/python fit/surveyfit_heldout.py run > .agent/surveyfit_run.log 2>&1 &`
   (pid lock data/surveyfit/heldout/runner.pid; checkpoints per pair into
   data/surveyfit/heldout/results.json - a cut session resumes; one disclosed re-run per
   errored pair; the run's timestamp is fixed when results.json is first created). The run
   does NOT need the test suite or any other agent's work; it only needs the 8091 service
   (check `curl -s -m 5 http://127.0.0.1:8091/health` first).
2. Monitor: `tail -f .agent/surveyfit_run.log` (per-pair completion lines: placed/corner/drot/
   scale/null/margin/conf). If the service dies mid-run, the errored pair stores an
   exception; when it is back, re-running `run` uses the one permitted re-run on those pairs.
3. When all 22 rows are in the checkpoint: `.venv/bin/python fit/surveyfit_heldout.py table`
   -> paste the output VERBATIM into MY 304 section of docs/site_flow.md, replacing the
   placeholder line "(The measured table is pasted here after the one run, as in the 302b
   section.)". That line + the verdict are the ONLY further edits to the section.
4. The verdict, written plainly next to the table: PASS iff a confidence threshold exists
   under which every accepted fit is within 60 m of the hand fit AND at least 5 of the 21
   docs are accepted (the threshold = the single authorised post-run choice, as in 302b;
   the table is reported as it comes out, no cherry-picking). PASS -> write tasks/304b
   (wire into tools/site_done.py's fit step: confident -> map, unsure -> review with the
   reason) as a NEW top-level task (lowest free number in 800-1099, with Depends on: 304 and
   its own Touches: line - tools/site_done.py is NOT in 304's Touches). FAIL -> say so in
   the section and STOP: no wiring, no fourth method.
5. Then tick the 3 acceptance boxes and set Status: done.

**Never:** read the 21's stored hand pairs outside fit/surveyfit_heldout.py (the evaluator is
the only reader); tune any parameter from the canary numbers, the run numbers, or the lead's
smoke (everything is frozen at 737508d); edit docs/site_flow.md outside my 304 section (agent
a owns 305's parts); change the 302b golden/hand docs; bind fixed network ports in tests (the
stub uses port 0; the run script is not a test); write outside the project + the temp dir
(.agent/ is gitignored and fine for logs); `git merge/rebase/reset/stash` outside a merge
request. Before starting: if main has moved (agent a's 305), confirm after the driver's merge
that my 304 section in docs/site_flow.md is intact (it sits far from 305's parts; re-apply my
freeze lines only if the merge damaged them).

**Re-read:** fit/surveyfit_heldout.py:measure - confirm `surveyfit.fit` is called with
null=True and the right `kinds` (default SHEET_KINDS for the sheet, ("aerial",) for the aerial
pair) and that the entry stores objective/null/margin/confidence exactly as table() and the
verdict need them; run() - confirm the all_done check counts all 22 pair keys (it iterates
pairs() keys, not just the 21 docs); pairs() - the aerial pair sits right after the
AERIAL_DOC sheet row.

## Lead note (2026-10-12)
Dropped: superseded by the matcher fit (fit/matchfit.py matches every plan against the site survey sheets as grounds, as well as relief and aerial). Nothing left to wire.
