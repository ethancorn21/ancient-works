Status: in-progress
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

## Hand-over

(2026-10-12, iteration 129, agent a - **prep session for part 4; no web code touched.** This session: (1) filed tasks/221-review-stats-test.md for the two review-test failures (they fail on PRISTINE main too, and the file is not mine - agent c's 309 edits it, hence `Depends on: 309`); (2) fixed the two card tests' reqfail filters in tests/test_fit_queue.py (added the `arcgisonline` exclusion: Esri URLs are .../MapServer/tile/... SINGULAR, which the old `/tiles/` path filter missed; NOT a weakening - the tests' own comments declare these aborts "page-caused, expected"); (3) new PITFALLS entry (the Esri base-imagery feed, singular tile/ segment). Suite is now **73 passed + 1 skipped + 2 failed** - the 2 failures are exactly the 221 pair in tests/test_review.py. My branch is green for everything that is mine. web/fitkit.js (the gestures + save code, committed in e7af85c) remains verified correct in pixels by the iter-128 throwaway probe: RESULT PASS, 41/41 checks (run128c.log).)

**What remains (307bb's boxes), in order:**
1. **Box 3 - the committed headless part 4 in tests/test_fit_queue.py** (the big remaining chunk; next session). Recipe below.
2. **Box 4 - the place-mode section in docs/site_flow.md**, built on top of the lead's 89043b7 version (now in my branch via the driver sync deb2730 - it touched docs/site_flow.md 9 lines); cite 307c's screenshots (1440x900 before/after in docs/site_flow/) when they land.
3. **Tick boxes 1+2 once part 4 is committed** (box 1's gesture/save behaviour and box 2's doc shape are code-committed in e7af85c and pixel-verified 41/41; their proof is the part-4 test). Then the done-claim: the driver's "not failing before" baseline for my task is the 4-failure state measured at iter 128 on main (2 card = fixed by me this session; 2 review = task 221).

**Part 4 build recipe (from the verified throwaway /tmp/fkverify; if /tmp is wiped, the probe design is in the 2026-10-12 307bb DECISIONS entries and web/fitkit.js's header comment):**
- A new CLEARLY-MARKED section at the end of tests/test_fit_queue.py (agent c's 309 edits this file too - keep mine separate so the merge stays trivial; when 309 lands in main, add ours on top of the merged file). A full-tree fixture cloned from the line_served fixture (~lines 121-610: web+server+tools+fit+pipeline, data minus data/raw, the picked entry's book page materialised into the tree's own data/raw, GUARD with a READER THREAD - not the file-log trick - and `--port 0`). One difference from line_served: the server runs under the pytest process's OWN python (the driver's .venv - numpy present, so the one-site line works; my /tmp build_tree.py only needed to name the venv python because it spawned from bash). A `PLACE_PROBE` script constant (copy /tmp/fkverify/probe.mjs verbatim - 41 checks) + `_run_place_probe` (model: `_run_probe` ~833-850) + `test_placement_gestures_and_save_in_the_browser`.
- Entry pick: FIRST queue entry that has BOTH a local book page and a `propose` key (derive, never pin; today: Devil's Dyke devil-s-dyke-q3307343 / earthworkenglan01allcgoog_n0686_1 / page n0686.jpg). Reuse `_pick_site`'s constraints (unresolved review item, no existing doc) AND require propose + local page, so the one-site line can complete.
- Probe details that cost iterations (keep verbatim): Chrome via createRequire('/home/agent/tools/shot/probe.mjs') -> playwright-core, `chromium.launch({channel:'chrome', headless:true, args:['--use-angle=metal','--enable-gpu','--ignore-gpu-blocklist']})`, viewport 1200x800. page.evaluate AND addInitScript take AT MOST ONE argument (an object) whose keys must match the destructured parameter names EXACTLY (a mismatch = silently undefined inside a try/catch - the depSel seed mystery). The dep seed file = the site's only drawable depiction: six-inch-1st.webp (os1inch is kind 'map' year 1900 -> filtered by loadDeps' surveyOldEnough <= 2026-150); seed aw.depSel as JSON `{site: file}`; the overlay src may be the `_ink` variant (depMode 'ink') - compute the expected src the way applyDep does: `data/sites/<id>/` + (depMode==='ink' && d.ink ? d.ink : d.file). Node: no apostrophes inside single-quoted strings; probe-local names are invisible inside evaluate/init callbacks (pass them in the one object arg). Pin tolerance: CDP mouse coords are quantized to whole pixels, so check pinned lon/lat within 2x the per-pixel lng/lat step (computed in-page from two unprojects 2 px apart), NOT 1e-7. Overlay m_per_px is in WEBP-px units: expected = anchor.mpx * fs / f with fs = image.width/doc.size, f = min(1, 2400 / max crop px) (MAX_PX=2400, plan_fit.py:44); the box's "scale and rotation agreeing with the anchor within rounding" is checked at the DOC level instead: in-page simFit over doc.pairs (4-tuples converted to {u,v,lon,lat} OBJECTS - simFit reads pair objects, raw arrays give nulls) reproduces the anchor within mpx 1e-3 abs / rot 0.01 deg / maxResid < 2. reqfail filter: exclude '/tiles/' AND 'arcgisonline'. Save: #fsave -> doc in tree/data/db/platefits/<site>.<plan>.json (by:hand, pairs == the final re-emitted five, size == image size) -> one-site line ~23 s -> the page polls depictions.json 60x1.5 s=90 s and endFit's; probe polls pane-close at 120 s; give pytest ~300 s. Second run: re-seed aw.fitQueue.done='{}' + aw.depSel, place, #fcancel -> earlier overlay back, same file, same ground, gestures re-enabled.

**Environment notes:**
- Our checkout HAS a .venv now (the driver builds it): suite = `.venv/bin/python -m pytest tests/ -q`. Current state: 73 passed + 1 skipped + 2 failed (the 221 pair only).
- Throwaway /tmp/fkverify/: build_tree.py (venv server, file logging, picks entries[0]), probe.mjs (THE 41-check artifact), diag7.mjs (addInitScript arg diag - the template for any future seed debug), run128c.log = the PASSING run, url/site/plan files, tree/ + its server (ephemeral port; find stale servers with `pgrep -f "serve.py"` + `readlink /proc/$p/cwd`; kill only cwd=/tmp/fkverify/tree). /tmp/maincheck/ = pristine-main scratch (89043b7) - delete or reuse to re-check main's redness.
- Do not touch fit/surveyfit.py or task 304 (agent c). Agent c's 309 shares tests/test_fit_queue.py AND docs/site_flow.md - keep my part-4 section and docs section in clearly-marked areas. Agent c's 309 also owns tests/test_review.py (task 221 waits for 309).
- If part 4 exceeds its 3-session budget: split the headless part from the (already-committed) gestures as announced in the Notes - a new subtask, noted in 307b's hand-over when done.

