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

(2026-10-12, iteration 123, agent a - FIRST session on 307bb; investigation + design only, NO code written. web/fitkit.js is untouched (md5 2857c9b17f6f5a988be08796e942529b = the committed 307ba state); the only file changed this session is this one's Status line (open -> in-progress). Tests were NOT run this session; the suite baseline to beat is 307ba's re-claim (iteration 122): 75 passed + 1 skipped, 0 failed (~114 s; the skip is agent c's 203b live-population drift). The DECISIONS entry "2026-10-12 307bb" has the MapLibre 5.6.0 findings and the full design; the design is restated below - implement from it, do not re-derive.)

**NEXT STEP (one step, then suite, then commit):** rewrite web/fitkit.js with the gestures exactly as designed below, keeping 307ba's `_fkFrameScale`/`_fkReemit`/`_fkActivate` core byte-identical (extend, don't rephrase). Then throwaway headless verification (recipe below), then the full suite, then commit `307bb: the placement gestures in fitkit.js - <why>`. The committed headless part-4 test (box 3) and the docs (box 4) are the following steps; if the gestures step itself overruns a session, split this task into 307bb-a (gestures) / 307bb-b (headless part-4) / 307bb-c (docs) and note it in 307b's hand-over.

**The design (all verified against the sources this session):**

New top-level names, all `_fk`-prefixed (one global lexical scope per page - the web/ PITFALLS: re-declaring a name rejects the WHOLE script, only `[pageerror]` shows it, `node --check` passes): `const _fkRefit = refit;` (fitkit is the only script wrapping refit), `let _fkLastN = 0` (pair count the re-emit logic last saw), `let _fkDrag = null`, `let _fkRaf = 0`; function declarations `_fkDeactivate`, `_fkSetGestures`, `_fkAbsorb`, `_fkReemitLive`, `_fkApply`, `_fkSync`, `_fkHint`, `_fkOnDown`, `_fkOnMove`, `_fkOnUp`, `_fkOnWheel`, `_fkScheduleApply`. Use `let` for anything assigned twice (the other web/ pitfall: reassigning a const throws at runtime and a swallowing catch hides it).

1. `_fkSetGestures(on)`: enable/disable exactly `['dragPan','scrollZoom','touchZoomRotate','doubleClickZoom','boxZoom']` on `map`; set `map.getCanvas().style.cursor = on ? 'grab' : ''` ('grabbing' while a drag is live). touchPan/touchRotate stay enabled (the box: gestures own the MOUSE; a phone can still re-centre).
2. `_fkDeactivate()`: `if (!P.placed) return;` then P.placed=false, P.anchor=null, P.anchorStack=[], _fkLastN=P.pairs.length, _fkDrag=null, _fkSetGestures(true). Called at the TOP of the openPlan wrapper (before the inner chain: review.js's openPlan wrapper pushes RV.pending pairs INSIDE the chain, and "Another plan" is endFit(false)->startFit->openPlan - both would otherwise inherit the previous placement) and at the END of the endFit wrapper.
3. `_fkActivate()`: the committed 307ba guards/seed stay byte-identical (incl. the P.img-first guard - the 404 page path stays byte-identical, part 3 depends on it); after seeding the 5 pairs+markers add `_fkLastN = P.pairs.length; _fkSetGestures(false);` before the existing final `refit();` (now the wrapped one: n==_fkLastN -> hint only).
4. Wrappers: `openPlan = async function (r) { _fkDeactivate(); const out = await _fkOpenPlan(r); _fkActivate(); return out; }`; `endFit = function (keepSite) { const wasPlaced = !!P.placed; const site = P.site; const out = _fkEndFit(keepSite); if (wasPlaced && site) applyDep(site); _fkDeactivate(); return out; }` (the page's endFit does NOT reset P.pairs - the _fkLastN bookkeeping is inert while placed=false; saveFit's success path calls the wrapped endFit then applyDep - the new overlay shows, as designed).
5. `_fkAbsorb()`: `if (!P.anchor || P.pairs.length < 2) return;` `const f = simFit(P.pairs); const [lon, lat] = unmerc(f.at(P.anchor.u0, P.anchor.v0)); P.anchor = { u0: P.anchor.u0, v0: P.anchor.v0, lon, lat, mpx: f.mpx, rot: f.rot };` - a no-op in the normal case (verified algebraically this session: simFit's a,b equal the re-emitted similarity's a,z0, so least squares over the exact re-emitted five recovers the anchor to fp rounding), and it absorbs a re-emitted corner the owner dragged (the page's marker-dragend mutates the pair and refits without touching the anchor) so the next gesture starts from the fit's position.
6. `_fkReemitLive()`: `if (P.pairs.length < 5) return;` re = _fkReemit(P.anchor); for i<5: mutate P.pairs[i].lon/lat IN PLACE (never replace the object: the page's addPairMarker dragend closure holds the pair object) and `P.marks[i].setLngLat([re[i].lon, re[i].lat])`. The five u/v are invariant (frame fixed per open).
7. `_fkApply()`: `const pins = P.pairs.length > 5 ? P.pairs.slice(5) : [];` remove all P.marks, P.marks=[]; P.pairs=[]; then for each p of _fkReemit(P.anchor)++pins: `P.pairs.push(p); addPairMarker(p);` (push one at a time so the .gpin labels number 1..n, like the map-click path); `_fkLastN = P.pairs.length`.
8. `_fkSync()`: n=P.pairs.length. If n>_fkLastN: push (n-_fkLastN) copies of the current P.anchor onto P.anchorStack, `_fkAbsorb()` (the pin(s) refine the anchor: least squares over ALL pairs; view mode included - the anchor is a similarity even when the preview is a homography), `_fkApply()`. If n<_fkLastN: drop=_fkLastN-n; `while (drop-- > 0 && P.anchorStack.length) P.anchor = {...P.anchorStack.pop()};` `_fkApply()` (clear -> the anchor before the first pin; an undo that pops below the five re-emitted floor with an empty stack leaves the anchor unchanged and re-emits the five: the placement is inviolable). n==_fkLastN: nothing.
9. `refit = function () { const out = _fkRefit(); if (P.placed && P.anchor) { if (P.pairs.length !== _fkLastN) { _fkSync(); _fkRefit(); } _fkHint(); } return out; }` - NO extra map.on('click') listener: the page's click/undo/clear/marker-drag handlers all call the bare refit(), which is the global = this wrapper, so every pair-count change syncs. The second `_fkRefit()` re-renders the preview after the sync mutated pairs. (The inner refit's renderFit rewrites #body at ~60fps during a live drag - tolerated: the drag pointer is on the map canvas, a sibling of #body, so no click-target churn; the page's own fitcv pan already does drawPlan per move.)
10. `_fkHint()`: if (P.placed && P.anchor): `$('#fithint').textContent` = live readout, e.g. `<mpx .toFixed(2)> m/px - turned <rot .toFixed(1)> deg - drag to move - wheel to scale - shift+wheel to turn` (match the page's text style; the page's renderFit sets the default text at the end of every refit and this overwrites it after, so it stays live on every gesture). This is box 1's "live scale and rotation in the panel" (the page's own `<p class=fit>` fit line updates too).
11. Gestures: `const container = map.getCanvasContainer()` - MapLibre 5.6.0 binds ALL its gesture listeners on the container, NOT the canvas (verified in web/vendor/maplibre-gl-5.6.0.js: mousedown/mousemove/mouseup/dblclick/click/wheel{passive:false} on the container, mousemove{capture}/mouseup on document). Attach once at load: `container.addEventListener('wheel', _fkOnWheel, { passive: false })` and `container.addEventListener('mousedown', _fkOnDown)`.
    - `_fkOnWheel(e)`: if (!P.placed || !P.active || !P.plan || !P.img) return; `e.preventDefault();` (safe: with scrollZoom disabled MapLibre's own wheel handler is skipped by the dispatcher and does not preventDefault/stopPropagation - verified; a non-placed page keeps normal map wheel-zoom because we return before preventDefault); dy=e.deltaY; if (!dy) return; `_fkAbsorb();` if (e.shiftKey) `P.anchor.rot += dy * 0.01;` (1 deg per 100-unit notch) else `P.anchor.mpx *= Math.exp(-dy * 0.0015);` (0.0015 = the page canvas's own wheel factor: wheel-up grows, same feel); `_fkReemitLive(); _fkScheduleApply();`.
    - `_fkOnDown(e)`: if (e.button !== 0 || !P.placed || !P.active || !P.plan || !P.img) return; pos = [e.clientX - map.getCanvas().getBoundingClientRect().left, e.clientY - ...top]; `_fkDrag = { x, y, ll: map.unproject(pos), lon: P.anchor.lon, lat: P.anchor.lat, moved: false }`; window.addEventListener('mousemove', _fkOnMove); window.addEventListener('mouseup', _fkOnUp); cursor 'grabbing'. (No setPointerCapture: MapLibre's own pointer bookkeeping could miss the up; window listeners catch the drag wherever it goes.)
    - `_fkOnMove(e)`: if (!_fkDrag || !P.placed) return; pos as above; if (!_fkDrag.moved) { if (Math.hypot(pos.x - _fkDrag.x, pos.y - _fkDrag.y) < 4) return; _fkDrag.moved = true; if (P.pending) P.pending = null; } (4px > MapLibre's 3px click tolerance - verified: the always-enabled user-event handler fires the map 'click' only when the mousedown->click distance is < clickTolerance (3) - so a real click (<=3px) pins via the page's handler and a drag (>=4px) moves, disjoint; nulling P.pending on move is the design: a drag is not a pin); then `const d = [merc(map.unproject(pos))[0] - merc(_fkDrag.ll)[0], merc(map.unproject(pos))[1] - merc(_fkDrag.ll)[1]]; const c = unmerc([merc([_fkDrag.lon, _fkDrag.lat])[0] + d[0], merc([_fkDrag.lon, _fkDrag.lat])[1] + d[1]]); P.anchor.lon = c[0]; P.anchor.lat = c[1]; _fkReemitLive(); _fkScheduleApply();` (delta in ground metres via unproject at both points - exact at any zoom, and transform-change tolerant while a fly-to is running; do NOT absorb on a move: a move must not change mpx/rot).
    - `_fkOnUp(e)`: remove the window listeners; restore cursor to 'grab'; `_fkDrag = null`. A sub-threshold release lets MapLibre fire its own 'click' -> the page pins (if P.pending) -> the refit wrapper syncs (n grows -> refine).
    - `_fkScheduleApply()`: rAF-coalesced: `if (_fkRaf) return; _fkRaf = requestAnimationFrame(() => { _fkRaf = 0; if (!P.placed || !P.anchor) return; _fkRefit(); _fkHint(); });` (rAF runs in headless Chrome on this VM - the 307ba probe relied on fly-to animations).

**Headless verification recipe (throwaway now; hardened into the committed part-4 next step):** Chrome /opt/google/chrome/chrome, playwright via NODE_PATH=/home/agent/tools/shot/node_modules; the probe is a .mjs written into the tmp outdir with `import { createRequire } from 'module'; const require = createRequire('/home/agent/tools/shot/probe.mjs'); const { chromium } = require('playwright-core');` (the 307ba throwaway /tmp/fkprobe.mjs - if it still exists - is the template: the direct `map`/`P` reference inside page.evaluate callbacks, channel:'chrome', headless, viewport 1200x800, console/pageerror/requestfailed lines). Full tree = copy web+server+tools+fit+pipeline + data minus data/raw + the picked entry's book page materialised into the tree's data/raw (test_fit_queue.py's line_served fixture + its GUARD are the template; `server/serve.py --port 0`). Pick the FIRST queue entry with a local book page AND a propose (Devil's Dyke, devil-s-dyke-q3307343, plan n0686: scale 0.3621 rot 0 - derive, never pin). Seed aw.depSel in localStorage with the site's current dep file (so there is an overlay to hide/restore). Flow: card -> #fqplace -> wait P.placed===true && P.img -> snapshot anchor0 -> (a) drag on a map-canvas point OUTSIDE the fitpane (viewport 1200: the pane spans 398..~950px, so use x in (950,1200), e.g. (1075,400): mouse.down, two mouse.move, mouse.up) -> wait ~300ms (rAF) -> assert anchor1 equals the in-page formula `unmerc(merc([a0.lon,a0.lat]) + [merc(unproject(p1))[i] - merc(unproject(p0))[i]])` and P.pairs[4] == [u0/v0 to 1dp, 7dp lon/lat of anchor1] and pairs 1-4 moved; (b) mouse.wheel(0,-100) at (1075,400) -> mpx *= exp(0.15); (c) keyboard.down('Shift'), mouse.wheel(0,+100), keyboard.up('Shift') -> rot += 1.0; after each gesture assert P.fit.mpx ~ anchor.mpx (1e-3), P.fit.rot ~ anchor.rot (0.01 deg), max residual < ~2 m (the rounded re-emitted five fit the anchor similarity to rounding - this is the rotated-parallelogram consistency the Notes demand be proven in pixels; the actual pixel-level check of the fit-prev source's four corners lands with part-4 in 307bb-b); (d) click #fsave (enabled: 5 >= 3) -> poll the tree's data/db/platefits/<site>.<plan>.json via node fs -> by:hand, pairs == the final re-emitted five as the page rounds them (0.1 px / 7 dp), at == a fresh ISO; then poll web/data/sites/<site>/depictions.json up to ~120 s for the overlay (the one-site line, ~23 s; the page itself waits 90 s and then endFit's -> the new dep overlay shows, S.depSel == the new file); (e) second run or continue: #fcancel -> the seeded dep layer visible again, same file, same ground, P.placed false, gestures re-enabled (map.scrollZoom.isEnabled() === true). No network: the server process's sockets are dead (GUARD); the page's external Esri fetches are the only live ones (same as part 3, which asserts no reqfail outside /tiles/).

**Regression watch (run the full suite after the change):** part-3 card tests (served tree, no data/raw -> book page 404s -> P.img null -> _fkActivate returns at the FIRST guard, before _fkFrameScale - keep that guard first) must stay byte-identical: pl.imgLoaded false, hint 'Could not load the page scan.', saveDisabled true. The 307ba headless verification (/tmp/fkprobe.mjs) reports `hint` but does not assert it - it should still pass (placed opens, overlay hidden, cancel restores). Nothing else in the suite touches fitkit. If a part-3 assertion breaks, the openPlan wrapper's pre-chain _fkDeactivate is the first suspect. Re-read items for the next agent: web/fitkit.js as committed (the header comment is the design doc), web/index.html ~832 endFit, ~902 openPlan, ~1000-1150 startFit/makeInk/simFit/refit/saveFit + the map.on('click') pin flow and the fitcv IIFE, web/review.js's openPlan wrapper (the pre-chain RV.pending push), tests/test_fit_queue.py parts 2-3 (line_served + PROBE_SCRIPT are the part-4 templates).
