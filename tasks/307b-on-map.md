Status: open
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
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).
