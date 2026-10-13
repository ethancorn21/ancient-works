Status: open
# 308: Site markers as small arrowheads, not squares
Touches: web/index.html, web/*.css, web/vendor/, docs/site_flow.md, docs/site_flow/

## Goal
The owner (2026-10-11): "instead of the squares we're going to move to a new shape ... keep the color gradient and all
that stuff ... a shape that says this is a point of interest ... like an old arrowhead ... a notched arrowhead ... it
would need to be small though, like a contracting stem arrowhead".

## Acceptance criteria
- [ ] Every site marker on the map and in the legend/list is a small contracting-stem (or notched) arrowhead
      silhouette, point down onto the site's location, with the existing colour gradient (older/truer darker) and the
      existing size tiers. Readable at the smallest tier on a phone and a 1440x900 screen, crisp on retina.
- [ ] The point of the arrowhead is the site's coordinate (the marker anchors at its tip, not its centre); clicking
      and the label placement/collision rules work as before.
- [ ] Screenshots before/after (the globe view, a zoomed region with many sites, the legend) in docs/site_flow/.

## Lead note (2026-10-13)
Dependency on 307 removed: 307's only open part is 307d, the owner's own check, which the markers do not need. Marker code only; commit working code each session.

## Hand-over

(2026-10-13, iteration 213, agent a - merge done + CODE IMPLEMENTED in web/index.html (uncommitted, in the
working tree); probe self-checks mostly green; one measurement fix applied but NOT yet re-run. Next session:
re-run probe, shots -> docs, tick boxes.)

**State.**
- main merged into agent/a, commit 4b12889 (2 parents b26b97a+735ec66). Conflicts resolved:
  tasks/212-cover-final.md = union (lead note + lead split from main, my iter-211 design hand-over kept last,
  per the lead split's "a's design notes stay on agent/a"); tasks/308-arrowhead-markers.md = my side (main's was
  empty). The merge brought NO code changes (main's new commits 61c6bdb/735ec66 are task-file-only).
- **web/index.html: the arrowhead is IMPLEMENTED in the working tree (uncommitted; the harness saved it).**
  All 7 edits landed and node-syntax-checked: the AH svg constant near TIERS; the markers CSS block rewritten
  (each tier keeps its size AND carries `--mks:` colour; `.sq.ah` rules with the non-scaling-stroke path; tag
  absolute left:100%/top:100%/translateY(-50%); `.marker.scan .tag { top: 50% }`); addMarkers (`.sq ah` + AH,
  anchor 'bottom' offset [0,0]); syncMarkers (`squares`->`marks`, box [x±8, y-16..y+1], label box unchanged);
  siteEntries swatch; the Marker-key legend (all 5 spans `.ah` + AH; the S.more fragment is now a backtick
  template literal); addScanAreas untouched (square, anchor 'left' [-6,0]); comments updated ("coloured
  arrowhead" at ~811, "most of the arrowheads" at ~340, section headers).
  DEVIATION from the iter-212 design (logged in DECISIONS): `.marker` stays `display: flex` (not inline-block)
  with `position: relative` - flex keeps the button box to exactly the .sq (an inline-block parent would add
  line-box descender height and shift the tip).
- **KEY FINDING: the map is a MapLibre 5.6 GLOBE (`projection: {type:'globe'}`, index.html ~324).**
  `map.project(lnglat)` returns the FLAT 2D map plane - NOT the on-screen position of a globe marker (up to
  ~3000 px apart at z2.3). A marker's own inline transform `translate(-50%,-100%) translate(Xpx,Ypx)` carries
  the on-globe screen position MapLibre computed from the lnglat. So the anchor check compares the measured
  tip to THAT transform point, and map.project only as a loose cross-check. (Write this as a PITFALLS entry:
  "MapLibre 5.6 globe mode: map.project() != marker screen position".)
- **Probe** /tmp/aw308shot.mjs (survives in /tmp; usage `node /tmp/aw308shot.mjs <url> <outdir> after`):
  rewritten this session (checks reordered: shape -> anchorZoom -> legend shot -> anchorGlobe -> click; anchor
  now = svg-box bottom-centre vs the marker's own transform point + the visual path-tip offset; latest edit:
  skip markers whose rect is outside the 1440x900 viewport - off-view markers carry wrapped/2D-plane positions
  that made the "worst" 3023 px before the fix). Last run's results: shape 499/499 site + 328/328 legend +
  324/324 list rows all carry the svg (scan markers: none on the page, Finder tab closed); click OK (aalsum
  opens); worstTipBelow 0.15 px (visual tip vs the svg box bottom - sub-pixel, fine); the 3023 worst was the
  off-view artifact the latest edit removes. **The re-run with the viewport filter has NOT happened yet.**
- Server for the probe: `python3 -m http.server 0 --bind 127.0.0.1` in web/, pid in /tmp/aw308-srv.pid (was
  port 33187; may be dead - restart fresh, log /tmp/aw308-srv.log, port via `ss -tlnp`). The 6 console 404s in
  the probe report are the known handled fallbacks (data/scans.json, data/amazon/areas.json, api/db/ping ...).
- After-shots from the pre-fix run are in /tmp/aw308shots/after-{globe,zoom,legend,phone}.png - REGENERATE after
  the final probe run, then copy to docs/site_flow/markers-after-{globe,zoom,legend,phone}.png (before-pair is
  already committed in docs/site_flow/). Eyeball after-zoom.png: tips land on the earthworks.
- **Suite**: full `.venv/bin/python -m pytest -q` on the merged tree was running in the background at session
  end (log /tmp/aw308-suite-merged.log, ends with a `SUITE-EXIT:n` line; last check: 2 Fs so far - expected
  231/232 merge-reds per my 212 hand-over). The pre-merge last-test-output (driver's, older) had 3 failed:
  test_fit_provenance x2 (231), test_site_done_line (232) - the 233/234 tests were NOT among them (the lead's
  aeeb5aa fixed them on main).
- **233/234 (my tasks) - pending bookkeeping, per the lead's instruction in my 212 hand-over** ("WHEN MAIN IS
  MERGED ... mark tasks/233 and 234 Status: done with all boxes ticked"; the lead did their work in aeeb5aa).
  NOT marked yet. Verify from /tmp/aw308-suite-merged.log: 233 box 1 = tests/test_merge.py::
  test_plan_list_refresh_is_pure_growth passes; 233 box 2 = all pre-212 (id, sites[0]) keys present in
  web/data/plans.json (1474 committed incl. numancia c_0fa271e2444f7bfc - check it's in the file); 233 box 3 =
  machine-dependence recorded (test docstring + PITFALLS export_plans entry - check both, extend if needed);
  234 box 1 = test_fit_queue_real passes with the (view,-px,plan,name) key (check the test's key tuple in
  tests/test_fit_queue.py); 234 box 2 = committed web/data/fit_queue.json byte-reproducible by tools/fit_queue.
  py on the current tree (run it twice, compare, note the "at" field); 234 box 3 = tools/fit_queue.py
  untouched (`git diff main -- tools/fit_queue.py`). If any box fails: don't tick it, log in DECISIONS, leave
  the task open. 231/232 stay open (their deps 306c-f/212 - see the 212 hand-over in tasks/212-cover-final.md).

**Exact next step.**
1. `tail /tmp/aw308-suite-merged.log` (the SUITE-EXIT line) - record the merged-tree failure set in DECISIONS.
2. Re-run the probe: ensure the web/ server (see above), `node /tmp/aw308shot.mjs http://127.0.0.1:<port>/ /tmp/aw308shots after`.
   Pass = per-tier worstTransform <= ~1 px in BOTH anchorZoom and anchorGlobe (globe view: the transform is the
   only valid reference; project will show a few-px globe-curvature difference - informational only),
   worstTipBelow <= 1, shape all-equal, click ok. If worstTransform > 1 for an ON-screen marker: the button box
   isn't exactly the .sq - measure `k.el.offsetWidth/Height` vs the .sq box and fix the flex/CSS, don't offset
   the anchor blindly.
3. Eyeball the 4 after-shots; copy to docs/site_flow/markers-after-*.png; append to docs/site_flow.md a section
   "## The site markers become arrowheads (task 308, 2026-10-13)": silhouette (notched contracting stem, tip on
   the point), same colours/sizes/collision rules, scan areas stay dashed squares at the area corner, before/
   after shot names.
4. Tick the three boxes, Status: done, commit (web/index.html + shots + docs).
5. Mark 233/234 per the verification list above (their own commits), commit.
6. Write the PITFALLS entry (MapLibre globe map.project vs marker transform; where: web/index.html ~324,
   /tmp/aw308shot.mjs; symptom: anchor deltas of ~3000 px at z2.3). Kill the http server.

**Re-read** (next agent, with fresh eyes): web/index.html ~157-195 (the rewritten markers CSS - check the
  .ah rules come AFTER the tier rules: equal specificity, order wins) and ~455-500 (AH/TIERS/addMarkers/
  syncMarkers), 563-600 (swatches/legend), /tmp/aw308shot.mjs (the anchorCheck function).
