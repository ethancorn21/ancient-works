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

(2026-10-13, iteration 212, agent a - FIRST session on 308. Investigation done, before-baseline
committed, design complete, NO code changed yet. One step left to implement, then shots/docs.)

**State.**
- Task file byte-identical to the lead's main version (61c6bdb dropped "Depends on: 307").
- Committed 0470610: `docs/site_flow/markers-before-{globe,zoom,legend,phone}.png`. Globe = the
  page's default view (center [-35,45] z2.3, 1440x900 dsf2); zoom = `map.flyTo([-1.9, 51.15], 7.2)`
  (Wiltshire/Devon/Dorset: many sites incl. t4 Old Sarum/Mayburgh; 1440x900 dsf2); legend = clip
  {0,0,396,900} of the left panel (Marker key + list rows, 1440x900 dsf2); phone = 390x844 dsf3
  isMobile of the same zoom view. Take the "after" pair with the identical probe (below).
- `web/index.html` is UNTOUCHED (still squares). No uncommitted code.
- Suite not run this session. Driver notes carry pre-existing failures (newest: test_gate::
  test_recorded_measurement_reproduces_and_agrees; older notes also list test_batch_eu union
  tests and test_serve::test_platefits_docs_match_sites). After the code change run
  `.venv/bin/python -m pytest -q` and compare against that set.

**The marker system (all in web/index.html - there are NO web/*.css files; styles are inline):**
- CSS ~157-179: `.marker` = flex row (`.sq` square + `.tag` label); per-tier sizes/colors:
  t4 15px #8A1230 (border 2px), t3 13px var(--survey), t2 11px #E2697F, t1 9px #F4B4C0,
  plain 7px var(--sheet); base `.marker .sq` 11px + 1.5px var(--ink) border. `.tiers` legend
  swatches repeat the same sizes/colors on their own spans (two places define each colour).
  z-index per tier; `pointer-events` only on `.sq`/`.tag` (comment: the hidden label once
  widened the button - keep it out of layout). `.marker.scan .sq` = dashed sheet square.
- JS: `TIERS` ~452 + `tierOf` (score thresholds) + `LABEL_FROM` (label zoom per tier);
  `addMarkers()` ~466: button `<span class="sq"></span><span class="tag">…</span>`,
  `new maplibregl.Marker({ element: el, anchor: 'left', offset: [-6, 0] })` (= square centre on
  the point); `syncMarkers()` ~480: per-marker box ±8 around the projected point, label box
  [p.x+6, p.y-10, p.x+12+tag.offsetWidth, p.y+10], higher tiers placed first, labels hide on
  overlap; `siteEntries()` line 563 (list-row swatch `<span class="tiers"><span class="sq
  ${tierOf(s)}"></span></span>`); `renderList()` line 589 (the "Marker key" legend spans, the
  plain one inside a plain-string `${S.more ? '…' : ''}` - beware, see below);
  `addScanAreas()` ~1187 (Finder search areas - dashed square at the area's corner: KEEP square
  and its anchor 'left' [-6,0]); line ~1151 resets `mk.el.className` after a save (innerHTML is
  untouched, safe); comment ~811 says "coloured square" (update wording).
- MapLibre 5.6.0 (web/vendor/, minified): the element itself gets class `maplibregl-marker`;
  default offset when none passed is [0,-14] - so PASS `offset: [0,0]` explicitly.
  `anchor: 'bottom'` should put the element's bottom-centre on the coordinate - VERIFY in the
  probe (the after-check below measures it), don't assume.
- Tests: none touch the markers (grep .sq/tiers/markers in tests/ finds nothing but fit-pair
  markers in test_fit_queue's part 4 and unrelated strings). test_review.py::
  test_index_html_review_footprint pins only the review.js script tag - unaffected.

**The design (decided this session - implement exactly this):**
1. Near `TIERS` add: `const AH = '<svg viewBox="0 0 100 100" aria-hidden="true"><path d="M50 99L8 40L34 12L50 24L66 12L92 40Z"/></svg>';`
   (notched arrowhead: tip at bottom (50,99); widest head (8,40)/(92,40); contracting stem to
   shoulders (34,12)/(66,12); central notch dipping to (50,24). Straight edges read crispest at
   7px. Owner's "notched / contracting-stem arrowhead".)
2. CSS: keep every existing size rule and add the tier colour as a custom property in each:
   `.marker.t4 .sq { …; --mks:#8A1230 }` (t3 var(--survey), t2 #E2697F, t1 #F4B4C0, plain
   var(--sheet)) and the SAME `--mks` in each `.tiers .tN` rule. Add:
   `.marker .sq { display: inline-block; … }` (display needed once `.marker` is no longer flex);
   `.marker { display: inline-block; position: relative; … }` (was display:flex);
   `.marker .sq.ah, .tiers .sq.ah { border: 0; background: none; }`; `.marker .sq.ah svg,
   .tiers .sq.ah svg { display:block; width:100%; height:100%; overflow:visible; }`; `.marker
   .sq.ah path, .tiers .sq.ah path { fill: var(--mks, var(--survey)); stroke: var(--ink);
   stroke-width: 1.2px; vector-effect: non-scaling-stroke; }` (non-scaling = 1.2px outline at
   every tier size, crisp on retina; svg overflow visible so the tip stroke isn't clipped).
   Label: `.marker .tag { position: absolute; left: 100%; top: 100%; transform:
   translateY(-50%); margin-left: 5px; …keep existing look… }` (button box = only the `.sq`,
   so the button's bottom-centre = the svg tip = the site point; the tag hangs to the right,
   vertically centred ON the point, same as the flex row did). Scan marker keeps the old
   look: `.marker.scan .tag { top: 50%; }` (its button is centred on the point, anchor 'left').
3. JS: `addMarkers()` - innerHTML `<span class="sq ah">${AH}</span><span class="tag">…</span>`,
   `new maplibregl.Marker({ element: el, anchor: 'bottom', offset: [0, 0] })`. `syncMarkers()`
   - marker footprint box becomes `[p.x-8, p.y-16, p.x+8, p.y+1]` (rename `squares`->`marks`;
   covers the tallest 15px head above the point, tip at the point); label box UNCHANGED
   [p.x+6, p.y-10, p.x+12+tagW, p.y+10] - the rules work as before. `siteEntries()` line 563 -
   `<span class="sq ah ${tierOf(s)}">${AH}</span>`. `renderList()` line 589 - all five legend
   spans get `ah` + `${AH}`; the `${S.more ? '…plain…' : ''}` fragment must become a TEMPLATE
   literal (backticks) or ${AH} won't interpolate. `addScanAreas()` stays as-is (no `.ah`, no
   AH, anchor 'left' [-6,0]). Comment ~811: "coloured square" -> "coloured arrowhead".
   Update the marker-section header comment (square -> arrowhead, tip-anchored, scan stays square).
4. After shots: reuse the probe - it still runs (server: `python3 -m http.server 0 --bind
   127.0.0.1` in web/; this session's was pid in /tmp/aw308-srv.pid, port 44713 - may be dead;
   restart fresh and kill any of mine when done). `node /tmp/aw308shot.mjs <url> <outdir> after`
   (it writes {phase}-globe/zoom/legend/phone.png; for phase 'after' it also reports: anchor =
   worst |tip - site point| over all visible markers per tier (must be ≤ ~1px; if bigger, the
   MapLibre anchor semantics differ - measure and adjust with an offset), click = clicking a
   marker's .sq sets S.sel to its site, shape = counts of svg-bearing .sq in markers/legend/list
   and that .marker.scan .sq still has NO svg). Copy to docs/site_flow/markers-after-*.png.
5. docs/site_flow.md: append a section "## The site markers become arrowheads (task 308, …)":
   what changed (silhouette, tip-anchored, same colours/sizes/collisions, scan areas stay
   squares), and the before/after shot names. Then tick all three boxes (verify: boxes 1-2 via
   the probe's after-checks + the shots, box 3 via the files), Status: done.

**Re-read** (for the next agent): web/index.html ~157-179 (the CSS block being replaced), ~452-500
(TIERS/addMarkers/syncMarkers), 563 (siteEntries swatch), 589 (legend), 805-815 (the "coloured
square" comment), 1145-1155 (className reset), 1180-1195 (addScanAreas).

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/212-cover-final.md` (open) - hand-over: (2026-10-13, iteration 211, agent a - investigation session: every API the test
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/221-review-stats-test.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

(no entries yet)

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (1 tests)
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_gate.py:36: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    1 failed, 59 passed in 63.50s (0:01:03)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-13 308 (agent a, iteration 212)
    First session: before-baseline committed (docs/site_flow/markers-before-*.png), arrowhead design final in the task file's hand-over, NO code changed yet. Next: implement the .ah SVG marker in web/index.html exactly per that hand-over, run /tmp/aw308shot.mjs in phase 'after' (it self-checks tip-anchoring/click/shape), suite, docs/site_flow.md section, tick boxes.
