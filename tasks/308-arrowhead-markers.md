Status: done
# 308: Site markers as small arrowheads, not squares
Depends on: none
Touches: web/index.html, web/*.css, web/vendor/, docs/site_flow.md, docs/site_flow/

## Goal
The owner (2026-10-11): "instead of the squares we're going to move to a new shape ... keep the color gradient and all
that stuff ... a shape that says this is a point of interest ... like an old arrowhead ... a notched arrowhead ... it
would need to be small though, like a contracting stem arrowhead".

## Acceptance criteria
- [x] Every site marker on the map and in the legend/list is a small contracting-stem (or notched) arrowhead
      silhouette, point down onto the site's location, with the existing colour gradient (older/truer darker) and the
      existing size tiers. Readable at the smallest tier on a phone and a 1440x900 screen, crisp on retina.
- [x] The point of the arrowhead is the site's coordinate (the marker anchors at its tip, not its centre); clicking
      and the label placement/collision rules work as before.
- [x] Screenshots before/after (the globe view, a zoomed region with many sites, the legend) in docs/site_flow/.

## Lead note (2026-10-13)
Dependency on 307 removed: 307's only open part is 307d, the owner's own check, which the markers do not need. Marker code only; commit working code each session.

## Hand-over

(2026-10-13, iteration 215, agent a - **308 DONE and committed**: all boxes ticked, after-shots in docs, docs section
written, both PITFALLS entries written. The 214 nohup'd suite's extra reds were investigated and proven environmental
(pytest shared-basetemp race - new PITFALLS entry); the in-session suite is green apart from the known 231/232 reds.
This file is done: the next session's step (233/234 bookkeeping) is described below and lives on agent a, not here.)

**What happened this session.**
- The 214 nohup'd suite (log /tmp/aw308-suite-final.log) had 4 test_serve HTTPError-404 + 5 test_review
  FileNotFoundError ON TOP of the expected 231/232 reds. Per the hand-over: investigated before ticking. The failing
  paths are inside the run's own temp tree (/tmp/loop-ancient-works.a/pytest-of-agent/pytest-0/aw0), which is now
  near-empty (web/, server/, most of data/ gone; only dirs the tests recreated after the deletion remain). Mechanism
  (from pytest 9.1.1 source): the harness sets `TMPDIR=/tmp/loop-$(basename $P)` for every process (a .agent/harness
  script), so ALL pytest sessions of this checkout share `$TMPDIR/pytest-of-<user>` as basetemp; at session end a
  GREEN session (policy=failed, no explicit --basetemp) rmtree's the WHOLE basetemp root, and the numbered-dir cleanup
  (keep=1) removes other sessions' pytest-N dirs. My nohup'd run outlived the 214 session and was wiped ~80s in (the
  erasing run's process is gone; the 01:23/01:24 pytest+node processes I saw were agent c's, in c's checkout = c's own
  basetemp, not a factor). Innocence of 308 and the tree, two ways: the 00:40 run of the same tree (no concurrent
  sessions) had those tests green; a fresh IN-SESSION run (plain `&`, not nohup): **3 failed / 147 passed / 1 skipped =
  exactly the known 231 (test_fit_provenance x2 - the lead removed the bethlehem docs a858f48) / 232 (test_site_done_line)
  reds** (log /tmp/aw308-suite-215.log, SUITE-EXIT:1).
- Finished 308: copied the 4 fixed after-shots to docs/site_flow/markers-after-{globe,zoom,legend,phone}.png (the
  before-pair markers-before-*.png already committed; dimensions verified: 2880x1800 globe/zoom, 792x1800 legend =
  sidebar crop, 1170x2532 phone @3x; content eyeballed this session: tips on their earthworks in zoom, four gradient
  arrowheads in the Marker-key row, arrowhead list-row swatches); appended "## The site markers become arrowheads
  (task 308, 2026-10-13)" to docs/site_flow.md (silhouette + tip anchoring + unchanged gradient/tiers/labels + the
  .scan squares stay + the parking-trap note + before/after shot names); ticked the three boxes, Status: done. The
  web/index.html fix itself was already committed by the driver as f51e342 after the 214 context limit.
- PITFALLS: (1) the CORRECTED MapLibre marker entry under web/ (replaces the planned-but-never-written 213 globe
  entry: vendor `.maplibregl-marker { position:absolute; top:0; left:0 }` parking, a later flowing-position rule
  re-enters the marker into flow, 500-3000px offsets; acceptance = rect-minus-transform a small CONSTANT; the globe-
  projection theory was a misdiagnosis, transform vs map.project() agree within 0.35px; globe canvas 1440x3038 note).
  (2) NEW `### pytest (9.1.1, project .venv)` subsection under "This machine": the shared-TMPDIR basetemp race and the
  rule - run the full suite in the foreground of your session, never nohup'd, never a second run while one runs.

**Next session (NOT this task): 233/234 bookkeeping** per the lead's 212-instruction ("WHEN MAIN IS MERGED ... mark
tasks/233 and 234 Status: done with all boxes ticked"; the lead did the work in aeeb5aa; main is merged here -
400431f). Check tasks/233-* and tasks/234-* (status/owner) first; then verify each box from evidence and tick+done
only if it passes: 233 box 1 = tests/test_merge.py::test_plan_list_refresh_is_pure_growth passes (it passed in the
01:2x in-session run); 233 box 2 = all pre-212 (id, sites[0]) keys present in web/data/plans.json (1474 committed,
incl. numancia c_0fa271e2444f7bfc - check it's in the file); 233 box 3 = machine-dependence recorded (test docstring +
PITFALLS tools/export_plans.py entry - check both, extend if needed); 234 box 1 = test_fit_queue_real passes with the
(view,-px,plan,name) key (check the test's key tuple in tests/test_fit_queue.py); 234 box 2 = committed
web/data/fit_queue.json byte-reproducible by tools/fit_queue.py on the current tree (run twice, compare, note the
"at" field); 234 box 3 = tools/fit_queue.py untouched (`git diff main -- tools/fit_queue.py`). If any box fails: don't
tick it, log in DECISIONS, leave the task open. 231/232 stay open (deps 306c-f/212 - see the 212 hand-over in
tasks/212-cover-final.md). And: never nohup the suite (PITFALLS, pytest 9.1.1 entry).
