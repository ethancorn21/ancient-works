Status: split
# 307b: Place mode on the map - the drawing starts on the ground, and moves by hand
Depends on: 307a
Touches: tools/fit_queue.py, web/fitkit.js, web/index.html, web/fitqueue.js, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
The owner could not fit by clicking three points: "when I go to place the plan onto the map
it already needs to be overlaid onto the map ... I can move it around, I can scale it around
... then pinpoint this exact spot to here". So place mode opens ON the works: the map flies
to the site's own box (the built site's extent) centred and zoomed so the works fill the
view, before the drawing appears; every overlay already on the site (the fitted drawings and
the survey sheets - whatever the site was showing) is hidden while place mode is open and
comes back exactly as it was when it closes. The drawing itself is on the map from the first
frame: the page's ink (the existing fit-prev preview: survey-red on transparent paper)
mapped by the anchor fit/propose.py already computes - sized from the picture's scale bar
where it has one, otherwise from the site's known size, north-up (or by its north arrow) -
at the opacity slider's value. The owner moves it by dragging, scales and rotates it (a
handle, modifier+drag or the wheel), and saves straight from that placement. Saving writes
the same page-px pairs the three-point flow writes (the placement re-emitted as pairs), so
plan_fit.py, the gate, the one-site line and every existing document keep working unchanged.
Pinning exact spots (a point on the drawing to a point on the ground) stays available on
top as a refinement: new points refine the anchor and re-draw it. Parent 307 boxes 2-4.

## Acceptance criteria
- [ ] The queue file carries the proposal: every entry whose best row admits one gets
      propose: {pairs, scale_m_px, rot_deg, scale_source, coarse, note} computed by
      fit/propose.propose_for (bar scale where recorded, ratio at the book's ppi, the
      site-size fallback, the north arrow where trustworthy). A row the proposal cannot
      anchor (no size, no size_m) gets no propose, and the page falls back to the existing
      three-point flow for it. tools/fit_queue.py stays stdlib-only (fit/propose.py is).
- [ ] Opening a queue site with a proposal (the card's "Place the drawing", or the site
      panel's "Place an old plan" when the site's queued plan is the one picked): the map
      flies to the site's box (its four corners) centred, before the drawing appears;
      while place mode is open, the site's earlier overlays (the dep-* fitted drawings and
      survey sheets applyDep was showing) are hidden; on close (back button, Cancel, or
      saving) they come back exactly as they were (same depiction selected, same ground).
      A site or plan without a proposal opens exactly as today (the three-point flow).
- [ ] The drawing is on the map from the first frame and is the thing being manipulated:
      drag moves it, a handle / modifier+drag / the wheel scales it, a handle /
      shift+wheel (or the equivalent gesture) rotates it, all at the opacity slider's
      value; the page's panel shows the live scale (m per page pixel) and the rotation.
      The three-point pinning still works on top of the placement (the map-click flow is
      unchanged), and undo/clear still work on both.
- [ ] Saving from direct placement alone writes the platefit doc in the existing shape
      (the placement re-emitted as 3-5 page-px -> lon/lat pairs, plus the existing
      crop/size/model/cite fields, "by": "hand" via the 305 save path, the one-site line
      running) and the overlay appears on the map; a fit saved this way passes the checks
      a three-point fit passes (test_fit_provenance and the golden hand-fit set stay
      green; no document in the shared store is ever written by a test).
- [ ] tests/test_fit_queue.py gains a headless part (the 305 part-3 pattern: Chrome via
      tools/shot.mjs-style CDP, a temp tree, ephemeral port, no network): on a real queue
      site with a proposal, the page opens place mode with the map at the site's box and
      the ink on it; scripted input events (a drag, a wheel scale, a shift+wheel rotate)
      change the saved doc's pairs accordingly (the doc is read back from the temp store);
      after close, the site's earlier overlays are back. Hermetic.
- [ ] docs/site_flow.md: what place mode is now (the anchor and where it comes from, the
      three gestures, the refinement, and what the saved doc contains), citing 307c's
      screenshots when they land.

## Notes
- The extension is web/fitkit.js in the fitqueue/review pattern: it loads after them,
  wraps their wrappers (openPlan last in the chain), injects its own <style>, and reaches
  the page's globals (P, map, refit, endFit, S, select) by name - the wrappers must not
  break the 201/205 pinned footprints. web/index.html is in Touches for a small hook only
  if the wrappers cannot reach in; the goal is to leave it byte-identical.
- The maplibre image source maps its texture with an affine built from three corners: the
  rotated-rectangle quad of a similarity is a parallelogram, so the rotated picture lands
  exactly - verify in the headless test (pixels), don't assume.
- Entry points (from the iteration-108 307a investigation, preserved on the record's
  closure): web/index.html (~1710 lines) - refit() (maps P.inkUrl onto the 'fit-prev'
  image source from the least-squares similarity of P.pairs), warpView() (proves the
  image-source quad mechanism), makeInk (survey-red on transparent), openPlan (the fit
  pane/points model); the place-mode flow fitqueue.js drives: endFit -> select(site) ->
  setGround -> loadDeps -> startFit(site) -> openPlan(row). Boxes 2-3 (fly-to on open,
  hide/restore overlays) live in the page's site-view and map-source code; keep the
  extension small and let the page own the map state.
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-12, iteration 115, agent a - 307ba is DONE (all its boxes): the queue file carries
the propose (307b's box 1), propose.py is root-aware, part-1 tests pin every path, the page
(307b's box 2): web/fitkit.js opens place mode ON the works (fly to the site's box, hide the
site's earlier overlay, seed the anchor as the 5 pairs, restore exactly on close), and
docs/site_flow.md's "Ready to fit" documents the propose key. Box 2 verified in a real
headless Chrome (probe: anchor == the propose's centre pair, re-emission drift 0.117 m, the
sheet hidden/restored, fsave enabled, no pageerror - DECISIONS). Remaining = 307bb ONLY:
307b's boxes 3-5 (the gestures on the placement, saving from it, the headless part-4 test)
plus the full place-mode docs section (307b's box 6, with 307c's screenshots when they
land). The page-side design sketch below stands as written for 307bb; the corrections on
the record: propose's private loaders take root=ROOT defaults (the PITFALLS entry), and
fitkit deliberately has NO <style> block yet (box 2 adds no visible UI - 307bb adds one if
its gestures need it; DECISIONS 2026-10-12 307ba).)

**State.** All of 307ba is committed on this branch: cbb36c8 (the data side: the queue file,
propose.py root-aware, part-1 tests), 732fe57 (box 2: web/fitkit.js + the one script tag in
web/index.html - the driver preserved iteration 114's uncommitted work), and 307ba's done
commit (docs/site_flow.md). web/fitqueue.js is byte-identical to cf29be2 and web/index.html's
diff against main is exactly the one tag; the page's own fit code (openPlan/startFit/refit/
saveFit/endFit, index.html ~832-1150) is still 305's, extended only by fitkit's two wrappers.
The queue file (117/117 propose) is a JOINT artifact with agent c's 309 (still in flight at
iteration 115; main tip cf29be2): when 309 merges into main, re-run `python3
tools/fit_queue.py` on the merged branch before further work here - fitkit reads the entry's
propose by name, so no page-code change is expected, but the part-4 test reads the
regenerated file. Suite baseline for 307bb: 70 passed + 1 skipped, with 3 failures that
pre-exist on main (the lead's 309 matcher wiring: test_fit_provenance::
test_line_refuses_unmarked_non_auto_doc, test_fit_queue::test_save_runs_the_one_site_line,
test_site_done::test_site_done_line - agent c's iteration-95 note; they share the review-
queue open-item count signature).

**Measured facts (iteration 110, all by running code):**
- All 117 current queue entries DO anchor: propose_for succeeds for every one (20 bar,
  4 ratio, 93 picture_size; coarse 93). n0686/Devil's Dyke: scale_m_px 0.3621, rot 0, 5 pairs
  centred on the site, note names the bar '0 100 200 300 400 Yards'. So the regenerated
  web/data/fit_queue.json (tracked file, NOT the shared store - `git check-ignore` says
  not ignored) will carry a propose on every current entry; the "no propose" cases only
  exist for rows/sites that lose their size or size_m - covered by the synthetic test.
- propose_for callers (all 2-positional, an optional `root` is safe): fit/batch_us.py:292,
  fit/inkfit.py:309, fit/inkfit_heldout.py, tests/test_batch_us.py, tests/test_batch_eu.py,
  tests/test_propose.py. fit/ has NO __init__.py: the import convention is
  `sys.path.insert(0, str(ROOT / "fit")); import propose` (site_done.py:43, test_propose:46).
- The stage-B fields in data/books/index.jsonl (890 rows): scale_text (508 set),
  blank_boxes (276 carry a {kind:"scale_bar", box}), north_angle_deg/north_arrow (594
  true), map_box, full_size. propose.py's _bar_box reads blank_boxes, not the scale_bar bool.
- web/data/fit_queue.json entry shape today: {site, name, best:{plan,reason,row},
  candidates:[{plan,title,book,view,draw_px}]}; the page (fitqueue.js fqLoad/fqPatch/
  fqPlace) reads site/name/best only - an extra entry-level `propose` key is inert until
  fitkit.js lands (307ba adds it).
- The page's anchor math (propose.py docstring, verified against index.html simFit): the
  similarity is `merc = a*(w - w0) + z0`, w = u - i*v, a = (m_per_px/ground_scale(lat0))*e^{i*theta},
  ground_scale = cos(lat). index.html already has `merc`/`unmerc` (line 324-325), R=6378137.
  The proposal's 5 pairs are [4 panel corners + centre] in row-size frame; pair[4] is the
  centre: its (u,v) = the panel centre (from the index row's map_box, or the page frame),
  its (lon,lat) = where the centre lands. So the page's anchor = {u0: p[4][0], v0: p[4][1],
  lon: p[4][2], lat: p[4][3], mpx: scale_m_px, rot: rot_deg} and re-emitting 5 pairs from
  the anchor (the exact _anchor_pairs math, ported to JS) recovers it; refit()'s least
  squares over those 5 reproduces the anchor to rounding.
- Site view facts: sites.json rows have corners (4 [lon,lat]), size_m, lidar; select() sets
  ground='imagery' then the opener sets it back (relief unless lidar===false); applyDep
  manages ONE `dep-<site.id>` image layer (the selected depiction); endFit() removes the
  'fit-prev' source/layer and re-renders the site view; saveFit's success path itself does
  remove dep layer -> endFit() -> applyDep(s) with depSel already set to the NEW overlay.
  The fit pane (#fitpane) sits at left:398px over the map; the map canvas is behind.
- test_fit_queue.py part 3 (the card) runs headless Chrome via playwright-core
  (CHROME=/opt/google/chrome/chrome, NODE_MODULES=/home/agent/tools/shot/node_modules,
  channel:'chrome', the probe is a .mjs written into the tmp outdir; _headless_or_skip
  skips when absent). Part 2's line_served fixture is the template for a FULL tree
  (web+server+tools+fit+pipeline, data/ minus data/raw, ONE book page materialised into
  the tree's own data/raw, sockets dead via the GUARD, --port 0): needed for a headless
  SAVE test because (a) the page must load the book scan (served trees 404 it otherwise)
  and (b) saveFit waits up to 90 s for the one-site line's overlay (the line measures
  ~23 s in this environment; it runs only with tools/fit/pipeline present).
- Agent c's 309 (the place check) works on tools/fit_queue.py, web/data/fit_queue.json and
  tests/test_fit_queue.py in its own branch - expect a merge of its build() change into
  mine (or vice versa); keep my propose changes localized (one helper + one key per entry +
  docstrings) so the merge is trivial.

**The split (why):** the parent set a 3-session budget for 307b and pre-announced: split
the fly-to/hide-restore from the gestures. Session plan: 307ba session 1 (done,
iteration 111) = box 1 data side (its boxes 1-3); 307ba session 2 = box 2 page side (its
box 4: fitkit.js open/hide/restore) + its box 5 docs; 307bb = boxes 3-6 (gestures, save,
headless part 4, docs place-mode section). If 307bb itself exceeds 3 sessions, split its
headless test from its gestures (note it here when you do).

**Page-side design sketch (for 307bb - my iteration-110 design; the Open half is coded as
written in web/fitkit.js, the gestures are not yet coded):**
- fitkit.js loads after fitqueue.js (the page loads review.js then fitqueue.js at
  index.html:1707-1708; add `<script src="fitkit.js"></script>` after them). Wrap
  openPlan LAST in the chain (fitkit.openPlan wraps fitqueue->review->page; note fitqueue
  does NOT wrap openPlan, only renderList/saveFit) and wrap endFit (page-level; neither
  review nor fitqueue wraps it). Unique lexical names `_fk*` (the web/ PITFALL: one global
  lexical scope per page). Inject its own <style>. Reach P/map/S/select/setGround/etc by
  name.
- Anchor state: `P.placed = true`, `P.anchor = {u0, v0, lon, lat, mpx, rot}` (u0/v0 the
  panel centre in page px from the row's map_box* or the whole page; lon/lat the centre's
  landing; mpx the m-per-px; rot deg). In placed mode P.pairs = re-emit(anchor) ++
  pinnedPairs; re-emit = the 5 pairs of _anchor_pairs ported to JS (round u/v 1 dp,
  lon/lat 7 dp - the doc convention). A pin (the existing map-click flow) then: push the
  pair + marker, push the current anchor on P.anchorStack, anchor = leastSquares(all
  pairs) (the page's simFit already returns mpx/rot; derive a,b then z0=fit(u0,v0),
  mpx=|a|*k, rot=atan2), re-emit. Undo: pop pair+marker, anchor=anchorStack.pop(),
  re-emit. Clear: drop all pins+markers, anchor=anchorStack[0] (the anchor before the
  first pin), re-emit. Gestures (307bb): while placed disable map.dragPan + map.scrollZoom
  (+ touchZoomRotate); drag on the map canvas moves (anchor lon/lat += Mercator delta,
  re-emit, refit; null P.pending once moved > ~4 px - MapLibre's own 3-px click tolerance
  then keeps clicks (pinning) and drags (moving) disjoint); wheel scales about the centre
  (mpx *= exp(-deltaY*f)); shift+wheel rotates about the centre (rot += f*deltaY). On
  close re-enable all. Views (P.model==='view'): gestures edit the same similarity anchor;
  refit's homFit/warpView preview keeps working (the similarity is a subspace of the
  homography) - verify in the headless test, don't assume.
- Open (307ba, done - web/fitkit.js as designed): wrap openPlan - after the inner chain
  returns, if P.plan && FQ has an
  entry for P.site whose best.plan === P.plan.id and entry.propose: seed anchor/pairs from
  entry.propose (needs P.img loaded: the pairs use the row's size frame - openPlan sets
  P.crop from r.map_box*r.size; derive u0/v0 the same way _anchor_pairs does: the
  map_box* size or the page frame), map.fitBounds(P.site.corners, {duration ~1.2 s,
  padding: left 390 when !narrow(), essential}), hide the `dep-<site.id>` layer
  (visibility 'none' if present). Wrap endFit - after the inner endFit (page removes
  fit-prev, re-renders site view), if it was placed: applyDep(site) (restores exactly:
  S.depSel/S.depMode/S.depOpacity/S.depAlign/S.ground are never touched) and clear
  P.placed/anchor/pins. The page's saveFit success path calls endFit() (the global =
  fitkit's wrapper) then its own applyDep - the new overlay shows, which is the designed
  save behaviour. No-proposal open: byte-identical to today (305 part-3 pins it).
- Headless test (307bb, part 4 of test_fit_queue.py): fixture like line_served (FULL tree +
  the picked entry's book page in the tree's data/raw; pick the first queue entry with a
  LOCAL book page AND a propose - derived, never pinned). Probe: home -> card -> Place ->
  wait P.img && P.placed -> assert: map centre/zoom ~ the site box (compare
  map.getBounds() against the corners' bounds), fit-prev source exists and visible, the
  dep layer (seed the site's depSel in localStorage first so one is shown) is hidden,
  anchor.mpx === propose.scale_m_px; then scripted input: mouse drag across the canvas
  (delta in Mercator known from map.project/unproject), wheel (known factor), shift+wheel;
  assert the anchor moved/scaled/rotated and P.pairs re-emitted accordingly; click #fsave
  (enabled: 5 pairs >= the 3 floor) -> poll the tree store until the one-site line's
  overlay lands (180 s budget like part 2) -> read the doc back via GET /api/db/platefits/
  <site>.<plan>: by:hand, pairs == the final re-emitted set (5 or 5+n pins), scale/rotation
  of the doc's pairs agree with the anchor within rounding; then a second run for the
  close paths: back button / Cancel -> the seeded dep overlay is visible again, same
  file, same ground. Hermetic: no network (the server process's sockets dead; the page's
  external Esri fetches are the only live ones - same as part 3, which asserts no reqfail
  outside /tiles/). Realpage screenshots for the docs land in 307c.

**Re-read** (for the next agent = 307bb, the gestures/save/headless part): web/fitkit.js
(the current shape - its header comment is the design doc; P.anchor/P.placed/P.anchorStack
are the state its gestures edit); web/index.html ~340-420
(deps/applyDep: the one `dep-<site.id>` layer, select()/setGround), ~832 endFit and ~902
openPlan (the two functions fitkit wraps) and ~1000-1150 (startFit, makeInk, simFit,
refit, saveFit, the map-click pin flow), 1706-1710 (the script tags);
web/fitqueue.js (the wrap pattern; must stay byte-identical) and web/review.js (how an
earlier extension wraps openPlan); the page-side design sketch above (the authoritative
source for the gestures: null-P.pending-on-move, the 3-px click tolerance, the wheel/
shift+wheel math); tests/test_fit_queue.py part 3 (~716+, the card test whose
line_served fixture is the template for part 4's FULL tree) and /tmp/fkprobe.mjs
(the throwaway probe - part 4's committed headless test is its hardened version; note its
this-VM fixes: the playwright require path, the direct `map` reference in the evaluate
callbacks). The data side and the propose docs need no re-read: they are as committed
(their docstrings and the "Ready to fit" section say what changed).
