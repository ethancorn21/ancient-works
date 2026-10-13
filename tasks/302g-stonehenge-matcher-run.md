Status: open
Depends on: none
# 302g: Stonehenge on the matcher-first line - the run, the browser check, the plain statement
Touches: docs/site_flow.md, docs/site_flow/, data/review/, data/db/platefits/, web/data/sites.json, web/data/review.json, web/data/sites/stonehenge/

## Goal
Parent box 5: "Run on Stonehenge: whatever it puts on the map, checked in a browser
against the real stones (screenshot in docs/site_flow/); say plainly if it places
nothing". This is the method-agnostic box-5 run with the current matcher-first line
(site_done._fit: the pretrained matcher first on every undocumented picture, the vision
batch the second pass, the fabrication and spread guards fencing both) - explicitly NOT
a revival of the dropped 302c/302d ink work.

State at iteration 208 (verified): stonehenge-q39671 = 0 drawings, 1 overlay
(web/data/sites.json); 14 candidates in
data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json (7 "line check:
fabricated...", 4 "median residual > 45 m", 2 feature-based, 1 "no model answer"); no
matcher document anywhere. The only Stonehenge screenshot (docs/site_flow/stonehenge.png,
2026-10-11) predates the matcher. The matcher's only Stonehenge record so far: a near-miss
and a 0.26-fraction RoMa on the earthworks, below the 0.4 bar (docs/matchfit.md
sections 7-8) - so the a-priori expectation is "places nothing", which the box explicitly
accepts; the point is to run the real line, check the result in a browser against the
sarsens, and record it plainly.

Environment (iteration 208): ELoFTR answers at 127.0.0.1:8091 (RTX 5060 Ti); RoMa at
:8092 is refused, so the run degrades to ELoFTR only (matchfit.run use_roma=False) -
record that. The batch's fit model (the Mac-side Qwen per 302's first session; the 8080
vLLM is the approved Clef-flash classifier, not the batch's fit model) is not reachable
from this VM, so uncovered candidates come back with the batch's "no model answer" - a
recorded environment fact, not a defect of this task.

## Acceptance criteria
- [ ] The live run of `tools/site_done.py stonehenge-q39671` (this checkout, the live
      ELoFTR): full stdout+stderr saved and committed as a NEW file under docs/site_flow/
      (e.g. stonehenge-matcher-<date>.log), with the run date and matcher availability
      (ELoFTR up, RoMa down) stated in the record.
- [ ] The run's effect on all 14 candidates stated per candidate in the record (what the
      matcher did for each picture, what the batch did, which documents were written or
      deleted and why); the pre-run snapshot of the current 14 entries is recorded in the
      same section.
- [ ] Whatever the line puts on the map is checked in a browser against the real sarsens
      with the 301/306 pattern (tools/shot.mjs: headless Chrome 155,
      NODE_PATH=/home/agent/tools/shot/node_modules, the tree served by
      server/serve.py --port 0): the stonehenge map page, the overlay's stone positions
      against the known circle/avenue layout, an [eval] measurement of the overlay's
      extent, and a screenshot committed as a NEW file under docs/site_flow/. If the line
      placed nothing: the current map page is screenshotted anyway and the record says
      plainly "the method placed nothing on Stonehenge" with the per-candidate reasons -
      that is a passing answer to this box.
- [ ] A new section in docs/site_flow.md APPENDED at the end of the file (do not edit any
      other section - agent a's 307d work also writes there and both must merge cleanly):
      run date, matcher availability, what was placed (or not), the screenshot name, the
      plain statement.
- [ ] The golden files and the 21 hand-fit documents byte-unchanged; no new reds against
      the newest driver loop-start note. web/data/review.json is a generated whole-queue
      publish: if it conflicts at merge time with other tasks' exports, regenerate it
      with fit/review.py export rather than hand-merging.
