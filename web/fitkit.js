/* Open the map on the works (task 307ba, 307b's box 2), and move the drawing by hand
   (task 307bb, 307b's box 3): the 'Ready to fit' queue already knows where each picture
   starts - the entry's `propose` (fit/propose.propose_for: the anchor that maps the
   picture's panel centre onto the site at the recorded scale and rotation, re-emitted
   as 3-5 page-px -> lon/lat pairs) - so opening the queued site's best plan puts the
   drawing ON the map before any clicking, and the owner manipulates IT:

   - the map flies to the site's own box (its four corners), centred beside the fit
     pane, before the ink appears;
   - while place mode is open, the site's earlier overlay (the fitted drawing or survey
     sheet applyDep was showing - the `dep-<site.id>` layer) is hidden, so the drawing
     sits on clean ground ("As soon as you go into that place mode the already placed
     overlay needs to go");
   - the anchor (panel centre on the site centre, its m-per-px and rotation) is seeded
     onto P and re-emitted as the page's 5 pairs (4 panel corners + centre, numbered
     1..5 with the page's own draggable markers): the page's preview, Undo, Clear, Save
     and the map-click pin flow all apply to them unchanged;
   - the three gestures, while placed (the gestures own the mouse; the map's own pan
     and zoom come off and come back on close):
       * a drag moves the whole drawing - the anchor's centre by the pointer's ground
         delta (each pointer point is unprojected and converted to a [lon, lat] array
         first - the page's merc destructures arrays, not unproject's {lng, lat} object
         - then taken in Mercator metres at both positions: exact at any zoom, and
         still right while a fly-to re-zooms under the drag; each move event recomputes
         the anchor from the PRESS-DOWN pointer and anchor - absolute, not
         incremental - so the many move events of one drag cannot accumulate);
       * the wheel scales it about the centre: mpx *= exp(-deltaY * 0.0015) - the page
         canvas's own wheel factor, so wheel-up grows;
       * shift+wheel turns it: 1 degree per 100-unit notch.
     Each is applied to the anchor, re-emitted into the five pairs IN PLACE (the pair
     objects and markers mutate, never rebuild mid-gesture), and the coalesced refit
     re-renders the page's preview from them - at the opacity slider's value. The
     panel's hint line is rewritten after every refit to read the live scale (m per
     page pixel) and rotation;
   - the page's three-point pinning still works ON TOP of the placement: a map-click
     pins (the unchanged flow; the map's 3-px click tolerance keeps a pin and a drag
     disjoint - a move engages at 4 px and a pin at <= 3), and each pin refines the
     anchor by least squares over ALL pairs (the page's own simFit; the anchor stays a
     similarity even for a view preview - a homography of flat ground that IS a
     similarity is that similarity, so warpView keeps working). The anchor stack
     remembers every pre-pin anchor, so Undo and Clear restore them: clear (or an
     undo that falls below the five) leaves whatever anchor is left and re-emits the
     five - the placement is inviolable. A marker the owner drags mutates its own
     pair (the page's dragend, which never touches the anchor); the next pin or
     transform absorbs it into the anchor first;
   - saving needs no new code: with P.pairs = re-emitted five (+ pins), the page's
     saveFit writes exactly the doc the three-point flow writes ("by": "hand" via the
     305 store, the one-site line runs as in part 2);
   - closing (back, Cancel, or saving) brings the overlay back exactly as it was -
     applyDep with S.depSel/S.depMode/S.depOpacity/S.ground never touched - and the
     placement state and the gesture lock clear. A save shows the new overlay: the
     page's saveFit success path runs this same restore before its own applyDep.

   A site or plan without a propose (or whose picture fails to load) opens exactly as
   today: the ordinary three-point flow, byte-identical (the 305 part-3 card test pins
   it - its served tree 404s the page scan, so place mode never activates there).

   index.html takes no fitkit footprint of its own, so this file loads after fitqueue.js
   (itself after review.js) and extends the page the same way they do - by reassigning
   the page's globals: openPlan LAST in the chain (page -> review -> fitkit; fitqueue.js
   wraps renderList/saveFit only), endFit (the page-level original - neither review nor
   fitqueue wraps it) and refit (the one hook the page already calls on every pair-count
   change - its map-click pin, Undo, Clear and marker-dragend all call it). MapLibre
   5.6.0 binds its own gesture listeners on the canvas CONTAINER (not the canvas) at
   map creation, and its dispatcher skips a disabled handler without preventDefault,
   so with the map's pan/zoom toggled off the listeners this file registers on the same
   container see every wheel and mousedown; a non-placed page keeps the map's own
   behaviour (the guards return before preventDefault). The row's page-px frame is the
   loaded image's frame scaled by the row's recorded size: tools/export_plans.py copies
   size and map_box from the book index row, the very fields propose.py read, so the
   propose's pairs are page px (verified: every current queue entry's served image is
   exactly its recorded size). A frame that cannot be related (a non-uniform resample)
   falls back to the ordinary flow. The headless part-4 in tests/test_fit_queue.py
   proves the gestures, the pin/undo/clear sync and the save in pixels on a full temp
   tree. _fk-prefixed names: one global lexical scope per page (the web/ pitfall) -
   review.js's _openPlan et al. stay untouched.
*/

const _fkOpenPlan = openPlan;
const _fkEndFit = endFit;
const _fkRefit = refit;
let _fkLastN = 0;   // the pair count the refit wrapper last saw: the sync's floor
let _fkDrag = null; // the live anchor drag: { x, y, ll, lon, lat, moved } (start pointer, its ground point, the anchor's position at press-down)
let _fkRaf = 0;     // the coalesced apply: at most one refit per frame

/* The loaded image's scale relative to the row's recorded page frame (the plans row's
   `size` = the book index row's full_size): the factor the propose's page-px
   coordinates multiply by to become the page's own u/v frame (the frame the page's
   pins use). 1 when the row records no size (the whole page is the frame, as in
   propose.py) or the image IS the recorded size; 0 when the two frames cannot be
   related (a non-uniform resample would break the similarity): the caller falls back
   to the ordinary flow. */
function _fkFrameScale() {
  const rec = P.plan && P.plan.size;
  if (!rec || !(rec[0] > 0) || !(rec[1] > 0)) return 1;
  const sx = P.img.naturalWidth / rec[0], sy = P.img.naturalHeight / rec[1];
  return sx > 0 && sy > 0 && Math.abs(sx - sy) <= 0.02 * Math.max(sx, sy) ? sx : 0;
}

/* The 5 proposed pairs (4 panel corners + centre) re-emitted from an anchor - the
   exact math of fit/propose.py's _anchor_pairs: a similarity in the very form
   pipeline/plan_fit.similarity inverts, merc = a*(w - w0) + z0 with w = u - i*v (image
   v down) and a = (m_per_px / ground_scale(lat0)) * e^(i*theta) - so a least-squares
   refit over the five recovers the anchor (to the queue file's rounding) and the
   preview sits on the site. u/v 1 dp, lon/lat 7 dp: the platefit-doc convention. */
function _fkReemit(anchor) {
  const s = _fkFrameScale();
  const rec = P.plan && P.plan.size;
  const bw = rec && rec[0] > 0 ? rec[0] : P.img.naturalWidth;
  const bh = rec && rec[1] > 0 ? rec[1] : P.img.naturalHeight;
  let x0 = 0, y0 = 0, x1 = 1, y1 = 1;
  const b = P.plan && P.plan.map_box;
  if (b) [x0, y0, x1, y1] = b;
  // propose.py's degenerate-box guard, in the page px frame
  if ((x1 - x0) * bw * s < 2 || (y1 - y0) * bh * s < 2) [x0, y0, x1, y1] = [0, 0, 1, 1];
  const pts = [[x0 * bw * s, y0 * bh * s], [x1 * bw * s, y0 * bh * s], [x1 * bw * s, y1 * bh * s],
               [x0 * bw * s, y1 * bh * s], [anchor.u0, anchor.v0]];
  const [zx0, zy0] = merc([anchor.lon, anchor.lat]);
  const k = Math.cos(anchor.lat * Math.PI / 180);
  const t = anchor.rot * Math.PI / 180;
  const ar = anchor.mpx / k * Math.cos(t), ai = anchor.mpx / k * Math.sin(t);
  return pts.map(([u, v]) => {
    const dr = u - anchor.u0, di = anchor.v0 - v;  // (u - i v) - (u0 - i v0)
    const z = [zx0 + ar * dr - ai * di, zy0 + ai * dr + ar * di];  // a*(w - w0) + z0
    const [lon, lat] = unmerc(z);
    return { u: Math.round(u * 10) / 10, v: Math.round(v * 10) / 10,
             lon: +lon.toFixed(7), lat: +lat.toFixed(7) };
  });
}

/* While the drawing is the thing being manipulated, the gestures own the mouse: the
   map's own pan and zoom come off (MapLibre 5.6.0's dispatcher skips a disabled
   handler without preventDefault - verified in web/vendor/maplibre-gl-5.6.0.js - so
   the listeners registered on the same canvas container below receive every wheel and
   mousedown; a NON-placed page keeps the map's own behaviour, because each guard
   returns before its preventDefault). touchPan and touchRotate stay on: the box
   hands the gestures the MOUSE; a phone can still re-centre the map. */
function _fkSetGestures(on) {
  for (const h of [map.dragPan, map.scrollZoom, map.touchZoomRotate, map.doubleClickZoom, map.boxZoom])
    on ? h.enable() : h.disable();
  map.getCanvas().style.cursor = on ? '' : 'grab';
}

/* The placement goes away - close (back / Cancel / save all end in endFit) or a new
   openPlan (which clears at its TOP, before the inner chain, so neither review's
   RV.pending push nor "Another plan" can inherit the previous placement). The state
   clears, the window drag listeners detach, and the map's pan and zoom come back.
   P.pairs is left as it is: the page's endFit keeps them and the next startFit
   resets them; _fkLastN is refreshed so a later sync has the right floor. */
function _fkDeactivate() {
  if (!P.placed) return;
  P.placed = false; P.anchor = null; P.anchorStack = [];
  _fkLastN = P.pairs.length;
  _fkDragStop();
  _fkSetGestures(true);
  _fkSpace(false);
}

/* Where the anchor stands, from the pairs the eye sees: the least-squares fit of
   EVERY current pair (the re-emitted five plus the pins - the page's own simFit)
   re-plants the centre at the fit's own position of (u0, v0) and adopts the fit's
   scale and rotation. Over the exact re-emitted five it is a no-op to floating
   point (the fit's a, b equal the re-emitted similarity's a, z0) - but a corner the
   owner has dragged since (the marker's dragend mutates the pair and refits, never
   the anchor) is absorbed, so the next transform moves the fit the eye sees. A drag
   must NOT call this: a move must not change the scale or the rotation. */
function _fkAbsorb() {
  if (!P.anchor || P.pairs.length < 2) return;
  const f = simFit(P.pairs);
  const [lon, lat] = unmerc(f.at(P.anchor.u0, P.anchor.v0));
  P.anchor = { u0: P.anchor.u0, v0: P.anchor.v0, lon, lat, mpx: f.mpx, rot: f.rot };
}

/* The five re-emitted pairs move with the anchor IN PLACE: a gesture must not
   replace the pair objects (the page's marker dragend closures hold them) nor
   rebuild the pane mid-gesture - mutate lon/lat and slide the marker, and let the
   coalesced refit re-render the preview from the same objects. The five u/v are
   invariant (the frame is fixed per open); the pins (pair 6+) are the owner's ground
   truth: they do not move. */
function _fkReemitLive() {
  if (P.pairs.length < 5) return;
  const re = _fkReemit(P.anchor);
  for (let i = 0; i < 5; i++) {
    P.pairs[i].lon = re[i].lon; P.pairs[i].lat = re[i].lat;
    if (P.marks[i]) P.marks[i].setLngLat([re[i].lon, re[i].lat]);
  }
}

/* The full rebuild, after the pair count has changed (the sync calls it): the five
   re-emitted from the current anchor, then the pins exactly as the owner placed
   them. The markers are recreated one at a time so the page's own labelling (the
   number read off P.pairs.length at creation) stays 1..n, and each new marker's
   dragend closure holds the very pair object it labels. */
function _fkApply() {
  const pins = P.pairs.length > 5 ? P.pairs.slice(5) : [];
  P.marks.forEach(m => m.remove()); P.marks = [];
  P.pairs = [];
  for (const p of _fkReemit(P.anchor).concat(pins)) { P.pairs.push(p); addPairMarker(p); }
  _fkLastN = P.pairs.length;
}

/* The sync the wrapped refit runs whenever the pair count changes while placed (a
   pin was added; an undo or a clear removed one). Grew: the new pin(s) refine the
   anchor - push a copy of the pre-pin anchor onto the stack, least-squares over
   every pair, rebuild. Shrank: pop the anchor(s) the removed pin(s) replaced; a
   clear (or an undo that falls below the five) pops the stack dry and leaves the
   anchor where it stands - the placement is inviolable, and the five re-emit from
   whatever anchor is left. */
function _fkSync() {
  const n = P.pairs.length;
  if (n > _fkLastN) {
    for (let i = 0; i < n - _fkLastN; i++) P.anchorStack.push({ ...P.anchor });
    _fkAbsorb();
    _fkApply();
  } else if (n < _fkLastN) {
    let drop = _fkLastN - n;
    while (drop-- > 0 && P.anchorStack.length) P.anchor = { ...P.anchorStack.pop() };
    _fkApply();
  }
}

/* The panel's live readout, rewritten after every refit (the page's renderFit
   resets #fithint to its default as its LAST act, so this overwrites it afterwards
   and stays live on every gesture): the anchor's scale in m per page pixel, its
   rotation, and the three gestures (box 1: the panel shows the live scale and the
   rotation). */
function _fkHint() {
  if (!P.placed || !P.anchor) return;
  $('#fithint').textContent =
    `${P.anchor.mpx.toFixed(2)} m per page pixel, turned ${P.anchor.rot > 0 ? '+' : ''}${P.anchor.rot.toFixed(1)}°` +
    ' · drag to move · wheel to scale · shift+wheel to turn';
  const st = document.querySelector('#body .step');
  if (st) st.textContent = 'Drag the drawing on the map to move it; the wheel scales it, shift+wheel turns it. ' +
    'To pin an exact spot, click it on the page, then on the map.';
}

/* One refit per frame at most: a wheel or a drag fires many events per frame, and
   the refit re-renders the pane - the pointer is on the map canvas (a sibling of
   the pane), so the rewrite does not disturb it. rAF runs in headless Chrome on
   this VM (the 307ba probe's fly-to animations ran on it). */
function _fkScheduleApply() {
  if (_fkRaf) return;
  _fkRaf = requestAnimationFrame(() => {
    _fkRaf = 0;
    if (P.placed && P.anchor) { _fkRefit(); _fkHint(); }
  });
}

/* --- the three gestures, registered once on the map's canvas container ---

   MapLibre 5.6.0 binds its own gesture listeners on the container (not the canvas)
   at map creation, before this file runs; its dispatcher skips a disabled handler
   and its scrollZoom returns before its preventDefault when disabled - so with
   _fkSetGestures(false) on, the map's pan and zoom are inert and every wheel and
   mousedown below lands here.

   Pinning and moving stay disjoint on the map's 3-px click tolerance (MapLibre
   fires its 'click' only when the pointer has moved less than 3 px between
   mousedown and mouseup, and the page pins on that click): a move engages at 4 px
   and nulls P.pending the moment it does - a sub-threshold release pins (the
   page's unchanged flow; the refit wrapper then refines the anchor), a drag moves
   (no click, no pin). A press inside a marker is the page's own flow: its
   draggable marker mutates its pair on dragend and refits, never touching the
   anchor - absorbed by the next pin or transform. */
function _fkOnWheel(e) {
  if (!P.placed || !P.active || !P.plan || !P.img || !P.anchor) return;  // a non-placed page keeps the map's own wheel zoom
  e.preventDefault();
  const dy = e.deltaY;
  if (!dy) return;
  _fkAbsorb();  // a corner dragged since the last transform joins the anchor first
  if (e.shiftKey) P.anchor.rot += dy * 0.01;           // 1 degree per 100-unit notch
  else P.anchor.mpx *= Math.exp(-dy * 0.0015);         // the page canvas's own factor: wheel-up grows
  _fkReemitLive();
  _fkScheduleApply();
}
function _fkOnDown(e) {
  if (e.button !== 0 || !P.placed || !P.active || !P.plan || !P.img || !P.anchor) return;
  if (e.target.closest('.maplibregl-marker')) return;  // a marker press is the page's own drag flow
  const r = map.getCanvas().getBoundingClientRect();
  const u = map.unproject([e.clientX - r.left, e.clientY - r.top]);  // {lng, lat} object -> the [lon, lat] array the page's merc destructures
  _fkDrag = { x: e.clientX - r.left, y: e.clientY - r.top,
              ll: [u.lng, u.lat], lon: P.anchor.lon, lat: P.anchor.lat, moved: false };
  addEventListener('mousemove', _fkOnMove);
  addEventListener('mouseup', _fkOnUp);
  map.getCanvas().style.cursor = 'grabbing';
}
function _fkOnMove(e) {
  if (!_fkDrag || !P.placed || !P.anchor) return;
  const r = map.getCanvas().getBoundingClientRect();
  const x = e.clientX - r.left, y = e.clientY - r.top;
  if (!_fkDrag.moved) {
    if (Math.hypot(x - _fkDrag.x, y - _fkDrag.y) < 4) return;  // 4 px > the map's 3-px click tolerance
    _fkDrag.moved = true;
    if (P.pending) P.pending = null;  // a drag is not a pin
  }
  // the anchor absolute to the press-down: anchor = anchor-at-down + (pointer now -
  // pointer at down), in Mercator metres. NOT an increment on the current anchor - a
  // drag fires many move events and an increment would apply the whole (now - down)
  // delta at each of them, accelerating the drawing away (the 1.5x drag bug, caught
  // in the throwaway probe: 2 move events of 30px moved the anchor by 1.5x the 30px
  // delta). Exact at any zoom, and still right while a fly-to re-zooms the map
  // under the drag.
  const u = map.unproject([x, y]);  // {lng, lat} object -> the [lon, lat] array the page's merc destructures
  const a = merc(_fkDrag.ll), b = merc([u.lng, u.lat]), h = merc([_fkDrag.lon, _fkDrag.lat]);
  [P.anchor.lon, P.anchor.lat] = unmerc([h[0] + b[0] - a[0], h[1] + b[1] - a[1]]);
  _fkReemitLive();
  _fkScheduleApply();
}
function _fkOnUp() {
  _fkDragStop();
}
function _fkDragStop() {
  if (_fkDrag) _fkDrag = null;
  removeEventListener('mousemove', _fkOnMove);
  removeEventListener('mouseup', _fkOnUp);
  map.getCanvas().style.cursor = P.placed ? 'grab' : '';
}

/* Place mode: the queue entry of this site (if any) carries a starting placement for
   the plan just opened - fly to the site's box, hide its earlier overlay, seed the
   anchor and the 5 pairs, and let the page's own preview show the drawing on the
   site. Every guard falls open to the ordinary flow. */
function _fkActivate() {
  if (!P.active || !P.site || !P.plan || !P.img) return;  // no picture: no ink to place - the byte-identical flow
  if (typeof FQ === 'undefined') return;
  const e = FQ.entries.find(x => x && x.site === P.site.id && x.best && x.best.plan === P.plan.id && x.propose);
  if (!e) return;  // not this site's queued plan, or the row admits no starting placement
  const s = _fkFrameScale();
  if (!s) return;  // the row's frame cannot be related to the loaded image
  const pr = e.propose, c = (pr.pairs || [])[pr.pairs.length - 1];  // the centre pair is last
  if (!c || pr.scale_m_px == null) return;
  P.placed = true;
  P.anchor = { u0: c[0] * s, v0: c[1] * s, lon: c[2], lat: c[3],
               mpx: pr.scale_m_px / s, rot: pr.rot_deg || 0 };
  P.anchorStack = [];
  const site = P.site;
  // the site's own box (its four corners), centred beside the fit pane - before the ink appears
  const cs = site.corners && site.corners.length ? site.corners : [[site.lon, site.lat]];
  const ws = cs.map(c => c[0]), ns = cs.map(c => c[1]);
  _fkSpace(true);
  const pad = narrow() ? { top: innerHeight * 0.26 + 16, right: 20, bottom: innerHeight * 0.5, left: 20 }
                       : { left: 390, top: 20, right: 330, bottom: 20 };
  // MapLibre keeps the padding of the last camera move (select's fly-to left 390) and adds this
  // one's on top - the box came out a third of the free map; start the fit from none
  map.setPadding({ top: 0, right: 0, bottom: 0, left: 0 });
  map.fitBounds([[Math.min(...ws), Math.min(...ns)], [Math.max(...ws), Math.max(...ns)]],
                { padding: pad, duration: 900, essential: true });
  // the earlier overlay goes while place mode is open; the endFit wrapper brings it back
  if (map.getLayer('dep-' + site.id)) map.setLayoutProperty('dep-' + site.id, 'visibility', 'none');
  // a fresh start (every path into openPlan reset via startFit): clear anyway, then seed
  P.pairs = []; P.pending = null; P.marks.forEach(m => m.remove()); P.marks = [];
  for (const p of _fkReemit(P.anchor)) { P.pairs.push(p); addPairMarker(p); }  // numbered 1..5, draggable, like the map-click path
  _fkLastN = P.pairs.length;
  _fkSetGestures(false);
  refit();
}

openPlan = async function (r) {
  _fkDeactivate();  // at the TOP, before the inner chain: review's wrapper pushes RV.pending pairs inside the chain, and "Another plan" is endFit(false) -> startFit -> openPlan - either would inherit the previous placement if the clear ran after
  const out = await _fkOpenPlan(r);
  _fkActivate();
  return out;
};

/* After the inner endFit (markers gone, the preview removed, the pane closed, the site
   view re-rendered): if place mode was on, the site's overlay comes back exactly as it
   was - applyDep with S.depSel/S.depMode/S.depOpacity/S.ground never touched - and the
   placement state clears (with the map's pan and zoom back on). The page's saveFit
   success path reaches the same restore, so a save shows the new overlay (its own
   applyDep right after is idempotent). */
endFit = function (keepSite) {
  const wasPlaced = !!P.placed;
  const site = P.site;
  const out = _fkEndFit(keepSite);
  if (wasPlaced && site) applyDep(site);
  _fkDeactivate();
  return out;
};

/* The one hook the page already has for every pair-count change: its map-click (pin),
   Undo, Clear and marker-dragend handlers all call the bare refit() - the global, so
   this wrapper. A changed count while placed syncs the anchor stack and re-emits
   (_fkSync), and the inner refit runs a second time so the preview fits the refined
   anchor; the panel's readout is written last, so it stays live on every gesture.
   While NOT placed this is the page's refit, byte-identical in behaviour. */
refit = function () {
  const out = _fkRefit();
  if (P.placed && P.anchor) {
    if (P.pairs.length !== _fkLastN) { _fkSync(); _fkRefit(); }
    _fkHint();
  }
  return out;
};

const _fkContainer = map.getCanvasContainer();
_fkContainer.addEventListener('wheel', _fkOnWheel, { passive: false });
_fkContainer.addEventListener('mousedown', _fkOnDown);

/* The working space (task 307c): "it's super cluttered ... there's like no working space".
   While placing, the map is the surface: the page picture shrinks to a small reference card
   in the map's bottom-right corner (its zoom/crop tools hidden; "Bigger" brings back the old
   pane, for pinning a spot on the page) and the side panel drops what placing does not use
   (the plan/view switch, the per-point list, "Another plan"). The rules live under
   body.placing, set only here, so every other layout of the page is untouched. */
const _fkStyle = document.createElement('style');
_fkStyle.textContent = `
  #fitbig { display: none; }
  body.placing #fitbig { display: inline-block; }
  body.placing .fitpane:not(.big) { top: auto; left: auto; right: 12px; bottom: 36px; width: 300px; height: 240px; }
  body.placing .fitpane.min:not(.big) { height: auto; }
  body.placing .fitpane:not(.big) .fit-tools { display: none; }
  body.placing #body .seg, body.placing #body ol.pairs, body.placing #fother { display: none; }
  @media (max-width: 760px) {
    body.placing .fitpane:not(.big) { top: 8px; left: 8px; right: auto; bottom: auto; width: 46vw; height: 26vh; }
  }`;
document.head.appendChild(_fkStyle);
const _fkBig = document.createElement('button');
_fkBig.id = 'fitbig';
_fkBig.textContent = 'Bigger';
$('#fitmin').before(_fkBig);
_fkBig.onclick = () => {
  const big = $('#fitpane').classList.toggle('big');
  _fkBig.textContent = big ? 'Smaller' : 'Bigger';
  if (P.img) { cvSize(); fitView(); drawPlan(); }
};

function _fkSpace(on) {
  document.body.classList.toggle('placing', on);
  $('#fitpane').classList.remove('big');
  _fkBig.textContent = 'Bigger';
  if (P.img && !$('#fitpane').hidden) { cvSize(); fitView(); drawPlan(); }
}
