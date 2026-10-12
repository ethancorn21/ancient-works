Status: open
# 307bb: Move the drawing - the three gestures, the save, the headless proof, the docs
Depends on: 307ba
Touches: web/fitkit.js, web/index.html, tests/test_fit_queue.py, docs/site_flow.md

## Goal
Parent 307 (and 307b) boxes 3-6, as renumbered there. On the placement 307ba opens, the
drawing is the thing being manipulated: the owner moves it by dragging, scales it with the
wheel, rotates it with shift+wheel (all at the opacity slider's value, with the live scale
and rotation in the panel), pins exact spots on top as a refinement (the map-click flow
unchanged, undo/clear working on both), and saves straight from that placement - writing the
same page-px pairs the three-point flow writes, "by": "hand", the one-site line running, the
overlay appearing. Proved hermetically in a headless part 4 of tests/test_fit_queue.py, and
written up in docs/site_flow.md.

## Acceptance criteria
- [ ] The drawing is on the map from the first frame and is the thing being manipulated:
      drag moves it, a handle / modifier+drag / the wheel scales it, a handle / shift+wheel
      (or the equivalent gesture) rotates it, all at the opacity slider's value; the page's
      panel shows the live scale (m per page pixel) and the rotation. The three-point
      pinning still works on top of the placement (the map-click flow is unchanged; new
      points refine the anchor and re-draw it), and undo/clear still work on both. While
      placed, the map's pan/zoom are disabled (the gestures own the mouse) and re-enabled on
      close; a sub-threshold click pins, a drag moves (MapLibre's 3-px click tolerance
      keeps them disjoint).
- [ ] Saving from direct placement alone writes the platefit doc in the existing shape
      (the placement re-emitted as 3-5 page-px -> lon/lat pairs, plus the existing
      crop/size/model/cite fields, "by": "hand" via the 305 save path, the one-site line
      running) and the overlay appears on the map; a fit saved this way passes the checks a
      three-point fit passes (test_fit_provenance and the golden hand-fit set stay green;
      no document in the shared store is ever written by a test).
- [ ] tests/test_fit_queue.py gains a headless part (the 305 part-3 pattern: Chrome via the
      part-2 line_served-style full tree - tools/fit/pipeline + the picked entry's book page
      materialised into the tree's own data/raw, ephemeral port, sockets dead in the server):
      on a real queue site with a proposal, the page opens place mode with the map at the
      site's box and the ink on it (a seeded dep overlay hidden); scripted input events (a
      drag, a wheel scale, a shift+wheel rotate) change the saved doc's pairs accordingly
      (the doc is read back from the temp store: by:hand, the final re-emitted set, scale
      and rotation agreeing with the anchor within rounding); after close (back / Cancel),
      the site's earlier overlay is back, same file, same ground. Hermetic.
- [ ] docs/site_flow.md: what place mode is now (the anchor and where it comes from, the
      three gestures, the refinement, and what the saved doc contains), citing 307c's
      screenshots when they land (before/after at 1440x900 in docs/site_flow/).

## Notes
- The design (anchor = {u0, v0, lon, lat, mpx, rot}; P.pairs = 5 re-emitted + pinned;
  gestures transform the anchor; pinning refines via the page's own simFit least squares;
  undo/clear from an anchor stack; the image-source quad of a similarity is a parallelogram
  so the rotated picture lands exactly) is in the parent 307b's ## Hand-over and the
  2026-10-12 307b DECISIONS entry - implement from there. The rotated-parallelogram claim
  must be VERIFIED in the headless test (pixels), not assumed.
- The headless save is the long pole: saveFit waits up to 90 s for the one-site line's
  overlay (the line measures ~23 s in this environment; part 2's 180 s budget applies),
  which is why the tree must carry tools/fit/pipeline and the book page locally (the bare
  `served` tree 404s the scan and has no line - part 3's card test lives with both).
- The rotated drawing over the map is a raster image source with 4 corners; the preview
  (refit) already handles both models (simFit for plans, homFit + warpView for views) - the
  gestures feed the same pairs, so the view path should keep working; check it, don't assume.
- If this task exceeds its 3-session budget, split the headless part 4 from the gestures
  (note it in 307b's hand-over when you do). Do not touch fit/surveyfit.py or task 304
  (agent c); agent c's 309 shares tests/test_fit_queue.py - keep the part-4 additions in
  their own clearly-marked section so the merge stays trivial.
