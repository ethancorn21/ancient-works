Status: done
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
- [x] The live run of `tools/site_done.py stonehenge-q39671` (this checkout, the live
      ELoFTR): full stdout+stderr saved and committed as a NEW file under docs/site_flow/
      (e.g. stonehenge-matcher-<date>.log), with the run date and matcher availability
      (ELoFTR up, RoMa down) stated in the record. -> docs/site_flow/stonehenge-matcher-2026-10-14.log
      (run 2026-10-14 02:06-02:10 CDT, exit 0, wall 3m08s; ELoFTR up on 127.0.0.1:8091, RoMa down
      on :8092 -> ELoFTR-only run; the header states both probes verbatim).
- [x] The run's effect on all 14 candidates stated per candidate in the record (what the
      matcher did for each picture, what the batch did, which documents were written or
      deleted and why); the pre-run snapshot of the current 14 entries is recorded in the
      same section. -> the log's per-candidate section (all 14: ELoFTR unsure/empty, batch not
      run, no docs written or deleted, item entries byte-identical) + the 14 pre-run entries
      verbatim in the log's pre-run snapshot section.
- [x] Whatever the line puts on the map is checked in a browser against the real sarsens
      with the 301/306 pattern (tools/shot.mjs: headless Chrome 155,
      NODE_PATH=/home/agent/tools/shot/node_modules, the tree served by
      server/serve.py --port 0): the stonehenge map page, the overlay's stone positions
      against the known circle/avenue layout, an [eval] measurement of the overlay's
      extent, and a screenshot committed as a NEW file under docs/site_flow/. If the line
      placed nothing: the current map page is screenshotted anyway and the record says
      plainly "the method placed nothing on Stonehenge" with the per-candidate reasons -
      that is a passing answer to this box. -> docs/site_flow/stonehenge-matcher-2026-10-14.png
      (headless Chrome on server/serve.py --port 0, page #stonehenge-q39671, [eval] read from the
      page's own state: the one overlay = the 1842 six-inch sheet (c.1900 one-inch out by the
      150-years rule), visible at 85% ink, corners identical to depictions.json, extent
      998.8 x 996.2 m on the 1000 m site box, sarsen centre = sheet centre (0 m off), no plan/drawing
      depiction; in the shot the ink circle rides on the visible standing-stone circle and the ink
      Avenue on the avenue earthwork - checked by looking at the shot). The plain statement is in the
      record (log's final line and docs/site_flow.md's new section).
- [x] A new section in docs/site_flow.md APPENDED at the end of the file (do not edit any
      other section - agent a's 307d work also writes there and both must merge cleanly):
      run date, matcher availability, what was placed (or not), the screenshot name, the
      plain statement. -> appended after the 307d section (agent a's, appended this session by
      the driver's merge; nothing else in the file touched): "## The matcher-first line on
      Stonehenge: the live run, the map check, the plain statement (task 302g, 2026-10-14)".
- [x] The golden files and the 21 hand-fit documents byte-unchanged; no new reds against
      the newest driver loop-start note. web/data/review.json is a generated whole-queue
      publish: if it conflicts at merge time with other tasks' exports, regenerate it
      with fit/review.py export rather than hand-merging. -> all golden lines verify (41/41 OK
      before AND after the run and the suite: the golden now carries 22 platefit docs - Fort Ancient
      joined the hand-fit golden in lead commit c72706b - plus 19 site.json; the box's "21" is the
      pre-merge count) and the full suite is green: 168 passed / 1 skipped / 0 failed (525 s), vs
      the newest driver note's 1 failed (307bb's placement test - now green on this tree) /
      159 passed / 1 skipped of 161; the suite has since grown to 169 tests.

## Hand-over

(2026-10-14, iteration 129, agent c - browser-check session. ALL FIVE BOXES TICKED -
task done, ready for the driver's re-check. No remaining work on this task.)

**Done and committed this session (boxes 3-4; boxes 1/2/5 from iteration 128 stand):**
- Box 3 (the browser check, the 301/306 pattern): served THIS checkout with
  `.venv/bin/python server/serve.py --port 0` (printed base http://127.0.0.1:38859/, killed after
  the shot), then `NODE_PATH=/home/agent/tools/shot/node_modules POSTWAIT=300 node tools/shot.mjs
  <base>/#stonehenge-q39671 docs/site_flow/stonehenge-matcher-2026-10-14.png 8000 1200 800 "<IIFE probe>"`
  (the probe polled S.ready && S.sites.length && S.mapLoaded, settled the map's zoom, then read the
  page's own state; only the known 2 expected 404s plus ArcGIS tile aborts from the flyTo, no pageerrors).
  [eval] result: sel = stonehenge-q39671; the site's ONLY depiction after the 150-years filter
  (surveyOldEnough, web/index.html:445) is the 1842 six-inch sheet - the c.1900 one-inch is out (1900 > 2026-150);
  depSel = six-inch-1st.webp shown as the `dep-stonehenge-q39671` source, visible, opacity 0.85, ink mode;
  its four coordinates identical to depictions.json (shiftCorners' mercator round-trip, 0 at micro-degree
  precision); extent 998.8 m (w) x 996.2 m (h), diagonal 1410.8 m, on the site's 1000 m box; no
  plan/drawing/view depiction anywhere; map centred on (-1.826111, 51.178889) at zoom 15. The sarsen centre
  (the catalog site point) is the sheet's exact centre (frac 0.5/0.5, offM [0,0]) - the sheet is the 1840s
  survey of this ground, so the stones it drew are at their true positions; verified in the shot itself:
  the red-ink circle rides on the visible standing-stone circle, the ink Avenue on the avenue earthwork
  running SW. Site fields as recorded: drawings 0, overlays 1, score 1.1, oldest 1842, lidar true.
- Box 4: appended ONE section to the end of docs/site_flow.md (after agent a's 307d section, which the
  driver's pre-session merge had appended; nothing else in the file touched - append-only as required):
  "## The matcher-first line on Stonehenge: the live run, the map check, the plain statement (task 302g,
  2026-10-14)" - run date, ELoFTR up / RoMa down, the per-picture matcher verdicts and the batch not
  running (pointing at the log for the 14-entry detail), the browser-check numbers, both file names, and
  the plain statement: **the method placed nothing on Stonehenge** - the a-priori expectation the matcher's
  own held-out tables predicted, met by the live line.
- Suite not re-run this session: since the last full run (iteration 128, 168 passed / 1 skipped / 0
  failed, 525 s) the only commits on this branch are the driver's bookkeeping (PROGRESS.md) and agent a's
  four regenerated 307d PNGs - no code changed, so the green state stands on this exact tree; this session
  touched only docs (the .md and the .png). Driver's done re-check will re-run it.
- Committed with EXPLICIT paths: docs/site_flow.md, docs/site_flow/stonehenge-matcher-2026-10-14.png,
  this task file, DECISIONS.md. The 307d PNGs are agent a's files (they drift with every full-suite run
  in any checkout) and were not touched by me.

**Re-read (for the driver or a future agent, if anything reopens this task):** web/index.html's
select() (~line 855: every site opens on the aerial photograph with the latest old map in ink, the
4.5 s flyTo) and loadDeps/surveyOldEnough/applyDep (~lines 445-470: the 150-years filter and the
`dep-<id>` image source); tools/shot.mjs (usage line; [eval] = an expression, write an IIFE; POSTWAIT
env before the screenshot); the probe in this session's DECISIONS.md entry shows the exact [eval]
shape that reads S.dep/S.depSel (a string, not an object - the 128 hand-over's draft had this wrong
once) and map.getSource('dep-<id>').coordinates.
