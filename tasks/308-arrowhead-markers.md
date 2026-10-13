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

(2026-10-13, iteration 214, agent a - ROOT CAUSE FOUND AND FIXED in web/index.html (uncommitted: harness holds it);
probe fully green; 4 after-shots regenerated and eyeballed. Next session: check suite log, shots -> docs, tick boxes,
corrected PITFALLS entry, commit; then the 233/234 bookkeeping.)

**What happened this session.**
- Re-ran the viewport-filtered probe: still failing (worstTransform 2641 zoom / 568 globe). DOM-chain probes showed the
  marker element's transform point and map.project() agree within 0.35px, but the measured rect sits 500-3023px below:
  the element was in NORMAL FLOW. **Root cause: my 308 CSS `.marker { ... position: relative }` (inline style, loads
  AFTER the vendor <link>; equal specificity 0,1,0) overrode the vendor's `.maplibregl-marker { left:0; position:
  absolute; top:0; }`** (web/vendor/maplibre-gl-5.6.0.css, in the minified blob). MapLibre parks marker elements at the
  canvas origin and places them purely via the inline transform; in flow each marker stacks below the previous in DOM
  order, so the transform lands it hundreds to thousands of px from its site. The iter-213 "KEY FINDING" (globe:
  transform = on-globe position, project = flat plane) was a MISDIAGNOSIS of this bug. A/B proof (0470610 served from
  /tmp/aw308before port 44269 vs current port 33187): BEFORE all 324 shown markers in-view, rect-minus-transform one
  constant 9.5px (old square's anchor geometry); AFTER-BROKEN only 61/324 in-view (globe), flow offsets 505-3023px.
- **Fix (UNCOMMITTED, in web/index.html):** `.marker { ...; position: absolute; top: 0; left: 0; }` - restates the
  vendor rule explicitly; comment added explaining why it must not be a flowing position. (This supersedes the iter-213
  "deviation" note: .marker stays display:flex, but the position is now absolute, not relative.)
- Verified: rect-minus-transform = 0/0 for every shown marker in default/zoom/globe; inView 324/324 (globe/default),
  98 (zoom) - matching the BEFORE baseline (98-100). Full probe re-run ALL GREEN: shape 499/499 site + 328/328 legend +
  324/324 list rows carry the arrowhead svg (scan markers: none on page, addScanAreas untouched); anchorZoom n=98
  worstTransform 0 / worstProject 0.69px; anchorGlobe n=324 worstTransform 0 / worstProject 0.68px; worstTipBelow
  0.15px; click opens the site. The .ah box has border:0, so the tip (svg bottom-centre) sits EXACTLY on the assigned
  point (the old square was 9.5px off due to its border-box/content-box anchor mismatch - the arrowhead is strictly
  more accurate).
- Eyeballed the 4 regenerated after-shots (/tmp/aw308shots/after-{globe,zoom,legend,phone}.png, 2x/3x retina): globe
  distribution identical to the committed baseline (markers on the disc, UK/Continental clusters) but as small arrowheads;
  zoom: tips sit on their earthworks, labels correct; Marker-key: four gradient arrowheads (15/13/11/9px, notch visible
  at 9px, non-scaling ink outline); list-row swatch an arrowhead; phone: readable at 3x. The broken-session shots were
  replaced in /tmp/aw308shots/.
- Suite: merged-tree run (pre-fix) = 3 failed/147 passed/1 skipped (test_fit_provenance x2 = 231, test_site_done_line
  = 232; same reds as the driver's pre-merge run; none attributable to 308). Fresh full suite after the CSS fix started
  at context limit: log /tmp/aw308-suite-final.log (no SUITE-EXIT marker this time - just tail for the summary line;
  expect the same 3 failed).

**Exact next step.**
1. `tail -15 /tmp/aw308-suite-final.log` - record the post-fix suite set (expect 3 failed/147 passed/1 skipped, the
   231/232 reds only). If anything new failed: investigate before ticking boxes.
2. Copy /tmp/aw308shots/after-{globe,zoom,legend,phone}.png -> docs/site_flow/markers-after-{globe,zoom,legend,phone}.png
   (the before-pair markers-before-*.png is already committed in docs/site_flow/).
3. Append to docs/site_flow.md a section "## The site markers become arrowheads (task 308, 2026-10-13)": silhouette
   (small notched contracting-stem arrowhead, tip pointing down ON the site's point - the marker anchors at its tip),
   same colour gradient and size tiers as the squares (older/truer darker), same label/collision rules (the head's box
   is [x±8, y-16..y+1] instead of ±8 centred), Finder search areas stay dashed squares at the area corner, before/after
   shot names, and the note that the marker's box is exactly the silhouette (position:absolute restated from the vendor
   css, so the tip lands on the coordinate at every zoom).
4. Tick the three 308 boxes, Status: done.
5. Write the CORRECTED PITFALLS entry (replace the planned globe one from iter-213): "MapLibre 5.6 marker elements are
   parked at the canvas origin by the vendor css .maplibregl-marker { position: absolute; top: 0; left: 0 } and placed
   only by their inline transform. Any page rule on the marker element with equal-or-higher specificity (e.g. our
   .marker { position: relative }) that loads after the vendor <link> overrides it (inline style wins the cascade tie),
   the marker re-enters normal flow, stacks in DOM order, and renders 500-3000px off its site - only markers with a
   small enough flow offset stay in the viewport, and off-view markers can be pushed INTO view. Where: web/index.html
   .marker + web/vendor/maplibre-gl-5.6.0.css. Symptom: rect bottom-centre minus the transform point is a large, varying
   (not constant) offset; most markers missing in globe view. Check: rect-minus-transform must be a small CONSTANT
   (= the anchor geometry). The earlier "globe projection" theory (transform = on-globe position, project = flat plane,
   3023px apart) was a misdiagnosis of this bug: transform and project agree within 0.35px." Plus keep a note that in
   globe mode the canvas container is larger than the viewport (1440x3038 at 1440x900) - informational.
6. Commit: web/index.html (the position fix) + shots + docs/site_flow.md + task file: "308: markers as notched
   arrowheads - the .marker position:absolute was overriding the vendor parking (placement bug found+fixed in 214);
   after-shots + docs; boxes done".
7. NEXT SESSION - 233/234 bookkeeping per the lead's instruction in my 212 hand-over ("WHEN MAIN IS MERGED ... mark
   tasks/233 and 234 Status: done with all boxes ticked"; lead's work in aeeb5aa). Verify from the suite log: 233 box 1
   = tests/test_merge.py::test_plan_list_refresh_is_pure_growth passes; 233 box 2 = all pre-212 (id, sites[0]) keys
   present in web/data/plans.json (1474 committed incl. numancia c_0fa271e2444f7bfc - check it's in the file); 233 box 3
   = machine-dependence recorded (test docstring + PITFALLS export_plans entry - check both, extend if needed); 234 box 1
   = test_fit_queue_real passes with the (view,-px,plan,name) key (check the test's key tuple in tests/test_fit_queue.py);
   234 box 2 = committed web/data/fit_queue.json byte-reproducible by tools/fit_queue.py on the current tree (run it
   twice, compare, note the "at" field); 234 box 3 = tools/fit_queue.py untouched (`git diff main -- tools/fit_queue.py`).
   If any box fails: don't tick it, log in DECISIONS, leave the task open. 231/232 stay open (deps 306c-f/212 - see the
   212 hand-over in tasks/212-cover-final.md).

**Re-read** (next agent, with fresh eyes): web/index.html ~160-200 (markers CSS - the .marker position:absolute restatement
   and the .ah rules that must stay after the tier rules), ~455-500 (AH/TIERS/addMarkers anchor 'bottom' offset [0,0]/
   syncMarkers box [x±8, y-16..y+1]), 563-600 (swatches/legend), /tmp/aw308cmp.mjs (the flow-offset A/B probe: dump each
   marker's transform, rect bottom-centre, and their difference - the acceptance check is that the difference is a small
   CONSTANT, ~0 for the borderless .ah).
