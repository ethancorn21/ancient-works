Status: done
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
- [x] The queue file carries the proposal: every entry whose best row admits one gets
      propose: {pairs, scale_m_px, rot_deg, scale_source, coarse, note} computed by
      fit/propose.propose_for (bar scale where recorded, ratio at the book's ppi, the
      site-size fallback, the north arrow where trustworthy). A row the proposal cannot
      anchor (no size, no size_m) gets no propose, and the page falls back to the existing
      three-point flow for it. tools/fit_queue.py stays stdlib-only (fit/propose.py is).
- [x] Opening a queue site with a proposal (the card's "Place the drawing", or the site
      panel's "Place an old plan" when the site's queued plan is the one picked): the map
      flies to the site's box (its four corners) centred, before the drawing appears;
      while place mode is open, the site's earlier overlays (the dep-* fitted drawings and
      survey sheets applyDep was showing) are hidden; on close (back button, Cancel, or
      saving) they come back exactly as they were (same depiction selected, same ground).
      A site or plan without a proposal opens exactly as today (the three-point flow).
- [x] The drawing is on the map from the first frame and is the thing being manipulated:
      drag moves it, a handle / modifier+drag / the wheel scales it, a handle /
      shift+wheel (or the equivalent gesture) rotates it, all at the opacity slider's
      value; the page's panel shows the live scale (m per page pixel) and the rotation.
      The three-point pinning still works on top of the placement (the map-click flow is
      unchanged), and undo/clear still work on both.
- [x] Saving from direct placement alone writes the platefit doc in the existing shape
      (the placement re-emitted as 3-5 page-px -> lon/lat pairs, plus the existing
      crop/size/model/cite fields, "by": "hand" via the 305 save path, the one-site line
      running) and the overlay appears on the map; a fit saved this way passes the checks
      a three-point fit passes (test_fit_provenance and the golden hand-fit set stay
      green; no document in the shared store is ever written by a test).
- [x] tests/test_fit_queue.py gains a headless part (the 305 part-3 pattern: Chrome via
      tools/shot.mjs-style CDP, a temp tree, ephemeral port, no network): on a real queue
      site with a proposal, the page opens place mode with the map at the site's box and
      the ink on it; scripted input events (a drag, a wheel scale, a shift+wheel rotate)
      change the saved doc's pairs accordingly (the doc is read back from the temp store);
      after close, the site's earlier overlays are back. Hermetic.
- [x] docs/site_flow.md: what place mode is now (the anchor and where it comes from, the
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

(2026-10-14, iteration 199, agent a via 307bc - 307b is DONE. All six boxes ticked; the
driver's returned-parent verification (iteration 256) covered boxes 1-4 and 6 on the then-
merged branch, and box 5 closed this session on the post-235 re-run. No page code changed
at any point: web/fitkit.js, web/index.html, web/fitqueue.js are byte-identical to their
accepted states.)

Box 5 evidence (the post-235 re-run, this session; machine date 2026-10-14, still 2026, so
part 4's `at` startswith-'2026-' assert and the year-relative 150-year cutoff are
unaffected):
- 235 is in this branch (driver merged main at 8c967c8; the fix = `_survives_page_filter`
  / `_page_auto_select` + the gated `_pick_place` at tests/test_fit_queue.py:1517-1558).
- Pre-run pick simulation (PITFALLS rule (a)): `_pick_place()` = oswestry-castle-q20713795,
  idx 3 of the 180-entry queue, plan earthworkenglan01allcgoog_n0119_1 (bar 0.1646 m/px,
  north-up): the 1842 six-inch map survives surveyOldEnough (2026-150=1876), the 1900 map
  is filtered. marietta (idx 1) is skipped by exactly the 235 rule (no-page-showable-dep)
  - the defect the red run was showing.
- part 4: tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser PASSES
  (1 passed, 66.21 s): the card's "Place the drawing" opens the placement on the works
  (map at the site's box, the propose anchor with its five pairs), the seed check green
  INCLUDING the dep layer's visibility (the 1842 map's layer hidden while placed, restored
  by Cancel), all behaviour checks green (gestures own the mouse; drag moves, wheel scales,
  shift+wheel turns, pin refines, undo restores), the saved doc read back from the TEMP
  store is exact (the 17-key shape, by:hand, pairs = the placed set), the one-site line's
  overlay lands in the temp tree's depictions.json, and the checkout's write-surface hash
  is unchanged around the run (hermetic; the only server-log noise is the known harmless
  /tiles/relief 404s).
- Full suite: 177 passed, 1 skipped, 0 failed (527 s) - exactly 235's recorded baseline,
  so no other red; nothing to file. (Iteration 256's 159/1/1 was the pre-235-merge
  baseline; the suite grew with 235's helpers and the merged 212/302g work.)
- Side matter closed: the 307d screenshot drift the previous hand-over left open is
  measured, not guessed - two same-data runs one hour apart differ 28.6-33.6% of pixels on
  the four saved/reload views (map not settled at shot time; the overlay shifts slightly
  relative to the ground) and 0-1.25% on card/placed/gestured. The "meaningful drift"
  condition is met, so task 242 was filed (Depends on: 307d; Touches:
  tests/test_owner_check.py, docs/site_flow.md, docs/site_flow/). Before this commit the
  ten 307d PNGs were restored to main's bytes (the PITFALLS workaround, 6af207b precedent)
  so this branch stays byte-identical to main on them.

Boxes 1-4 and 6: verified in the iteration-256 hand-over (now in git history and in the
2026-10-13 307b DECISIONS entry, which the driver archives with this task) and re-proven
by this session's green run (307d's two owner-check tests are in the 177).
