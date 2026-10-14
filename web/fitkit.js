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
/* Owner 2026-10-13: "you can't move around the map ... I need to be able to move around
   both". Placed now splits the mouse instead of taking it: a press ON the drawing moves
   the drawing (dragPan is switched off for that one press, in the capture phase, before
   MapLibre's own container listener sees it), a press OFF it pans the map; the plain
   wheel zooms the map, shift+wheel scales and alt+wheel turns the drawing (both stopped
   in the capture phase so the map does not zoom too); right-drag still rotates the map.
   Only double-click and box zoom stay off while placed. */
function _fkSetGestures(on) {
  for (const h of [map.doubleClickZoom, map.boxZoom]) on ? h.enable() : h.disable();
  map.dragPan.enable(); map.scrollZoom.enable();
  map.getCanvas().style.cursor = '';
}

/* The drawing's outline on screen: the four re-emitted map_box corners (pairs 0..3),
   projected. A press inside it moves the drawing; outside, the map. */
function _fkInside(x, y) {
  if (P.pairs.length < 4) return false;
  const q = P.pairs.slice(0, 4).map(p => map.project([p.lon, p.lat]));
  let inside = false;
  for (let i = 0, j = 3; i < 4; j = i++) {
    const a = q[i], b = q[j];
    if ((a.y > y) !== (b.y > y) && x < (b.x - a.x) * (y - a.y) / (b.y - a.y) + a.x) inside = !inside;
  }
  return inside;
}

/* The placement goes away - close (back / Cancel / save all end in endFit) or a new
   openPlan (which clears at its TOP, before the inner chain, so neither review's
   RV.pending push nor "Another plan" can inherit the previous placement). The state
   clears, the window drag listeners detach, and the map's pan and zoom come back.
   P.pairs is left as it is: the page's endFit keeps them and the next startFit
   resets them; _fkLastN is refreshed so a later sync has the right floor. */
function _fkDeactivate() {
  if (!P.placed) return;
  P.placed = false; P.anchor = null; P.anchorStack = []; P.hist = [];
  _fkLastN = P.pairs.length;
  _fkDragStop();
  _fkSetGestures(true);
  _fkSpace(false);
  _fkBarOff();
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
  _fkStyleMarks();
}

/* The five re-emitted pairs are the drawing's frame, not the owner's pins: the owner read
   them as pins 1-5 (2026-10-13). Corners show as small hollow handles, the centre not at
   all, and the owner's own pins are numbered from 1. */
function _fkStyleMarks() {
  P.marks.forEach((m, i) => {
    const el = m.getElement();
    if (i < 5) { el.classList.add('fk-handle'); el.textContent = ''; el.style.display = i === 4 ? 'none' : ''; }
    else { el.classList.remove('fk-handle'); el.textContent = String(i - 4); el.style.display = ''; }
  });
}

/* Where page point (u, v) lands under an anchor, in Mercator metres (the _fkReemit map). */
function _fkAt(a, u, v) {
  const [zx0, zy0] = merc([a.lon, a.lat]), k = Math.cos(a.lat * Math.PI / 180), t = a.rot * Math.PI / 180;
  const ar = a.mpx / k * Math.cos(t), ai = a.mpx / k * Math.sin(t), dr = u - a.u0, di = a.v0 - v;
  return [zx0 + ar * dr - ai * di, zy0 + ai * dr + ar * di];
}

/* The owner's pins decide the placement on their own (2026-10-13 "nothing aligns"): before,
   each pin was least-squared together with the five frame pairs, so one pin pulled the
   drawing a sixth of the way. One pin: the drawing slides so that spot lands exactly
   (scale and turn kept). Two or more: their own similarity fit sets the centre, scale and
   turn. */
function _fkFromPins() {
  const pins = P.pairs.slice(5);
  if (!pins.length || !P.anchor) return;
  if (pins.length === 1) {
    const p = pins[0], now = _fkAt(P.anchor, p.u, p.v), want = merc([p.lon, p.lat]), c = merc([P.anchor.lon, P.anchor.lat]);
    [P.anchor.lon, P.anchor.lat] = unmerc([c[0] + want[0] - now[0], c[1] + want[1] - now[1]]);
    return;
  }
  const f = simFit(pins);
  const [lon, lat] = unmerc(f.at(P.anchor.u0, P.anchor.v0));
  P.anchor = { u0: P.anchor.u0, v0: P.anchor.v0, lon, lat, mpx: f.mpx, rot: f.rot };
}

/* One undo history for everything done while placed (2026-10-13 "there's no undo"):
   every move, wheel burst and pin pushes the anchor it replaced; Undo (the panel button,
   or Cmd/Ctrl+Z) pops the last one, removing the pin if it was a pin. */
let _fkWheelAt = 0;
function _fkPush(pin) { (P.hist ||= []).push({ anchor: { ...P.anchor }, pin }); }
function _fkUndo() {
  if (P.pending) { P.pending = null; refit(); return; }
  const e = (P.hist || []).pop();
  if (!e) return;
  if (e.pin && P.pairs.length > 5) { P.pairs.pop(); P.marks.pop()?.remove(); }
  P.anchor = { ...e.anchor };
  _fkApply();
  refit();
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
    _fkPush(true);
    _fkFromPins();
    _fkApply();
  } else if (n < _fkLastN) {
    // Clear (or the page's own pop): the drawing stays where it stands; pin steps leave the history
    P.hist = (P.hist || []).filter(e => !e.pin);
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
    `${P.anchor.mpx.toFixed(2)} m per page pixel, turned ${P.anchor.rot > 0 ? '+' : ''}${P.anchor.rot.toFixed(1)}°`;
  _fkBarSync();
}

/* Place mode is a tool (owner 2026-10-13: "the keybinds for rotate, scale, undo need to be on the
   screen itself ... a little taskbar at the top"; the tan instruction box and the panel buttons
   were "really ugly" and leaned on the left side). While placed, one bar across the top of the map
   carries every control with its key, and a readout line under it; the panel's step box, buttons
   and fit line are hidden (body.placing) - the buttons stay in the DOM for the page's own save. */
function _fkQueued() { return typeof FQ !== 'undefined' && !!fqPending()[0] && fqPending()[0].site === (P.site && P.site.id); }
function _fkBarEl() {
  let b = $('#fkbar');
  if (b) return b;
  b = document.createElement('div'); b.id = 'fkbar'; b.setAttribute('role', 'toolbar'); b.setAttribute('aria-label', 'Place the drawing');
  b.innerHTML = `
    <div class="fkrow">
      <span class="grp"><b>Move</b><span class="how">drag the drawing</span></span>
      <span class="grp"><b>Scale</b><button data-a="s-" title="Smaller (shift+wheel down)">&minus;</button><button data-a="s+" title="Bigger (shift+wheel up)">+</button><kbd>&#8679; wheel</kbd></span>
      <span class="grp"><b>Turn</b><button data-a="r-" title="Turn left 1&deg; (shift-click 5&deg;)">&#8634;</button><button data-a="r+" title="Turn right 1&deg; (shift-click 5&deg;)">&#8635;</button><kbd>&#8997; wheel</kbd></span>
      <span class="grp"><button data-a="undo" id="fkundo">Undo</button><kbd>&#8984;Z</kbd></span>
      <span class="grp map"><b>Map</b><span class="how">drag off it &middot; wheel zooms &middot; right-drag turns</span></span>
      <span class="sp"></span>
      <button data-a="skip" id="fkbskip">Skip site</button>
      <button data-a="not" id="fkbnot" title="The picture does not show this site (a detail, a building, another place)">Not this structure</button>
      <button data-a="cancel">Cancel</button>
      <button data-a="save" class="primary" id="fkbsave">Save on the map</button>
    </div>
    <div class="fkread"><span id="fkread"></span><span id="fkst"></span></div>`;
  document.body.appendChild(b);
  const step = (fn, e) => { if (!P.placed || !P.anchor) return; _fkPush(false); fn(e && e.shiftKey ? 5 : 1); _fkReemitLive(); _fkScheduleApply(); };
  const act = {
    's-': e => step(() => { P.anchor.mpx /= 1.05; }, e), 's+': e => step(() => { P.anchor.mpx *= 1.05; }, e),
    'r-': e => step(n => { P.anchor.rot -= n; }, e), 'r+': e => step(n => { P.anchor.rot += n; }, e),
    undo: () => _fkUndo(), skip: () => { fqSkip(); _fkNext(); }, not: () => _fkNotThis(),
    cancel: () => endFit(), save: () => saveFit(),
  };
  b.addEventListener('click', e => { const t = e.target.closest('button[data-a]'); if (t && !t.disabled) act[t.dataset.a](e); });
  return b;
}
function _fkBarSync() {
  const b = _fkBarEl(), pins = P.pairs.slice(5);
  $('#fkundo').disabled = !(P.hist && P.hist.length) && !P.pending;
  $('#fkbskip').hidden = !_fkQueued();
  $('#fkbsave').disabled = !S.db;
  let t = `${P.anchor.mpx.toFixed(2)} m per page pixel, turned ${P.anchor.rot > 0 ? '+' : ''}${P.anchor.rot.toFixed(1)}°. `;
  if (P.pending) t += '<b>Now click the same spot on the map.</b>';
  else if (!pins.length) t += 'For an exact spot: click it on the page (Bigger), then on the map.';
  else if (pins.length < 3) t += `${pins.length} pin${pins.length > 1 ? 's' : ''}: ${pins.length === 1 ? 'the drawing slides onto it' : 'they set place, scale and turn'}; a third shows whether the drawing is true.`;
  else {
    // how far each pin is from where the drawing now puts that spot (a move after pinning shows here)
    const k = Math.cos(P.anchor.lat * Math.PI / 180);
    const r = pins.map(p => { const a = _fkAt(P.anchor, p.u, p.v), q = merc([p.lon, p.lat]); return Math.hypot(a[0] - q[0], a[1] - q[1]) * k; });
    t += `Pins off the drawing: ` + r.map((m, i) => `<span class="${m > 15 ? 'bad' : ''}">${i + 1}: ${m.toFixed(0)} m</span>`).join(' · ') +
      (Math.max(...r) > 15 ? ' &mdash; a pin far off is on the wrong spot, or the drawing is not true there: Undo it.' : '');
  }
  $('#fkread').innerHTML = t;
  const st = $('#fitst'); $('#fkst').textContent = st ? st.textContent : '';
}
function _fkBarOff() { const b = $('#fkbar'); if (b) b.remove(); }
// the page writes save/record progress into the panel's #fitst (hidden behind the bar's readout): mirror it
new MutationObserver(() => { const b = $('#fkst'), st = $('#fitst'); if (b) b.textContent = st ? st.textContent : ''; })
  .observe($('#body'), { subtree: true, childList: true, characterData: true });

/* Skip and "Not this structure" sit in the fit panel itself (2026-10-13: "once you're in the
   place the drawing option there's no way to skip it ... you have to go out zoom out then
   say skip"; Machu Picchu's pictures are walls and archways, not the site). Skip shows for a
   site from the Ready to fit queue: it skips the site and opens the next one in place.
   "Not this structure" shows for any picture: it is recorded in the db (notthis/<site>.<plan>;
   the server marks the review candidate dropped, so the matcher never tries it and the queue
   never offers it again) and moves on - the next queued site, or this site's plan list. */
function _fkTools() {
  if (!P.active || !P.plan || !P.site || $('#fknot')) return;
  const save = $('#fsave'); if (!save) return;
  const queued = typeof FQ !== 'undefined' && fqPending()[0] && fqPending()[0].site === P.site.id;
  const row = document.createElement('div');
  row.className = 'tools';
  row.innerHTML = `${queued ? '<button id="fkskip">Skip this site</button>' : ''}<button id="fknot" title="The picture does not show this site (a detail, a building, another place)">Not this structure</button>`;
  save.parentElement.before(row);
  if ($('#fkskip')) $('#fkskip').onclick = () => { fqSkip(); _fkNext(); };
  $('#fknot').onclick = _fkNotThis;
}
async function _fkNotThis() {
  const s = P.site, r = P.plan, st = $('#fitst');
  if (!S.db) { if (st) st.textContent = 'The page is not connected to its server; nothing was recorded.'; return; }
  const id = `${s.id}.${r.id}`;
  const fromQueue = _fkQueued(), btns = ['#fknot', '#fkbnot'].map(q => $(q)).filter(Boolean);
  btns.forEach(x => { x.disabled = true; }); if (st) st.textContent = 'Recording…'; if ($('#fkst')) $('#fkst').textContent = 'Recording…';
  try { await S.db.doc(`notthis/${id}`).set({ site: s.id, plan: r.id, title: r.title || '', at: new Date().toISOString() }); }
  catch (e) { if (st) st.textContent = `Could not record it (${e.message}).`; if ($('#fkst')) $('#fkst').textContent = st ? st.textContent : ''; btns.forEach(x => { x.disabled = false; }); return; }
  _fkNotSet.add(id); lsSet('aw.notThis.last', { id, title: r.title || '' });
  // the PUT returns after the server has rebuilt web/data/fit_queue.json without the picture
  if (typeof FQ !== 'undefined') { FQ.loaded = false; await fqLoad(); }
  if (fromQueue && fqPending()[0]) { endFit(false); await fqPlace(); return; }  // the next queued picture (this site's next, or the next site)
  endFit(false); startFit(s);  // opened from the site: back to its plan list, without this picture
}
function _fkNext() {
  if (fqPending()[0]) { endFit(false); fqPlace(); }
  else endFit();
}

/* The owner's "not this" set, loaded once: the plan list and the queue leave them out at once
   (the server's queue rebuild does the same for the file). */
const _fkNotSet = new Set();
(async () => {
  try { const r = await fetch('api/db/notthis'); if (r.ok) for (const d of (await r.json()).docs || []) _fkNotSet.add(d.id); } catch {}
})();
// the queue honours the set at once too (a queue file rebuilt elsewhere, e.g. on the VM, may predate the drop)
const _fkPending = fqPending;
fqPending = function () { return _fkPending().filter(e => !(e.best && _fkNotSet.has(`${e.site}.${e.best.plan}`))); };
// the last "not this" can be taken back from the queue card (the db doc deleted: the server lifts the drop)
const _fkPatch = fqPatch;
fqPatch = function () {
  _fkPatch();
  const last = lsGet('aw.notThis.last', null), card = document.getElementById('fqcard');
  if (!last || !card || !_fkNotSet.has(last.id) || $('#fknotundo')) return;
  const b = document.createElement('button'); b.id = 'fknotundo';
  b.textContent = `Undo "not this" (${(last.title || last.id).slice(0, 40)})`;
  b.onclick = async () => {
    b.disabled = true;
    try { await S.db.doc(`notthis/${last.id}`).delete(); } catch { b.disabled = false; return; }
    _fkNotSet.delete(last.id); lsSet('aw.notThis.last', null);
    FQ.loaded = false; await fqLoad();
  };
  (card.querySelector('.tools') || card).appendChild(b);
};
const _fkPlanMatches = planMatches;
planMatches = function () {
  const out = _fkPlanMatches();
  return P.site ? out.filter(r => !_fkNotSet.has(`${P.site.id}.${r.id}`)) : out;
};

const _fkRenderFit = renderFit;
renderFit = function () {
  const out = _fkRenderFit();
  _fkTools();
  _fkHint();
  return out;
};

addEventListener('keydown', e => {
  if (!P.placed || !(e.metaKey || e.ctrlKey) || e.key.toLowerCase() !== 'z' || e.shiftKey) return;
  if (e.target.closest && e.target.closest('input, textarea')) return;
  e.preventDefault(); _fkUndo();
});

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
  if (!e.shiftKey && !e.altKey) return;  // the plain wheel zooms the map
  e.preventDefault(); e.stopPropagation();  // capture phase: MapLibre's scroll zoom never sees it
  const dy = e.deltaY || e.deltaX;  // macOS turns a shift+wheel into a horizontal scroll (deltaX)
  if (!dy) return;
  if (performance.now() - _fkWheelAt > 600) _fkPush(false);  // one undo step per wheel burst
  _fkWheelAt = performance.now();
  if (P.pairs.length <= 5) _fkAbsorb();  // a corner dragged since the last transform joins the anchor first (never over pins: they would pull it back)
  if (e.altKey) P.anchor.rot += dy * 0.01;             // 1 degree per 100-unit notch
  else P.anchor.mpx *= Math.exp(-dy * 0.0015);         // the page canvas's own factor: wheel-up grows
  _fkReemitLive();
  _fkScheduleApply();
}
function _fkOnDown(e) {
  if (e.button !== 0 || !P.placed || !P.active || !P.plan || !P.img || !P.anchor) return;
  if (e.target.closest('.maplibregl-marker')) return;  // a marker press is the page's own drag flow
  const r = map.getCanvas().getBoundingClientRect();
  if (!_fkInside(e.clientX - r.left, e.clientY - r.top)) return;  // off the drawing: the map pans
  map.dragPan.disable();  // capture phase, before MapLibre's container listener: this press is the drawing's
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
    P.anchor.lon = _fkDrag.lon; P.anchor.lat = _fkDrag.lat; _fkPush(false); // one undo step per drag
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
  if (_fkDrag) { _fkDrag = null; map.dragPan.enable(); }
  removeEventListener('mousemove', _fkOnMove);
  removeEventListener('mouseup', _fkOnUp);
  map.getCanvas().style.cursor = '';
}
/* The cursor says which one a press will move: a hand over the drawing. */
function _fkHover(e) {
  if (!P.placed || _fkDrag || !P.anchor) return;
  const r = map.getCanvas().getBoundingClientRect();
  map.getCanvas().style.cursor = _fkInside(e.clientX - r.left, e.clientY - r.top) ? 'move' : '';
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
  P.pairs = []; P.pending = null; P.marks.forEach(m => m.remove()); P.marks = []; P.hist = [];
  for (const p of _fkReemit(P.anchor)) { P.pairs.push(p); addPairMarker(p); }  // the frame: 4 corner handles + the hidden centre
  _fkLastN = P.pairs.length;
  _fkStyleMarks();
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
// capture phase: these run before MapLibre's own listeners on the same container (the event's
// target is the canvas inside it), so a press on the drawing can switch dragPan off in time and a
// modified wheel can be stopped before the map zooms
_fkContainer.addEventListener('wheel', _fkOnWheel, { passive: false, capture: true });
_fkContainer.addEventListener('mousedown', _fkOnDown, { capture: true });
_fkContainer.addEventListener('mousemove', _fkHover);

/* The working space (task 307c): "it's super cluttered ... there's like no working space".
   While placing, the map is the surface: the page picture shrinks to a small reference card
   in the map's bottom-right corner (its zoom/crop tools hidden; "Bigger" brings back the old
   pane, for pinning a spot on the page) and the side panel drops what placing does not use
   (the plan/view switch, the per-point list, "Another plan"). The rules live under
   body.placing, set only here, so every other layout of the page is untouched. */
const _fkStyle = document.createElement('style');
_fkStyle.textContent = `
  #fitbig { display: none; }
  body.placing #body .step, body.placing #body .tools, body.placing #body p.fit:not(.source) { display: none; }
  #fkbar { position: fixed; top: 12px; left: 400px; right: 60px; z-index: 30; background: var(--sheet); border: 1.5px solid var(--ink);
    box-shadow: 0 2px 10px rgba(43,39,36,.18); font: 600 12px var(--label); letter-spacing: .02em; color: var(--ink); }
  #fkbar .fkrow { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 14px; padding: 7px 10px; }
  #fkbar .grp { display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; }
  #fkbar .grp b { text-transform: uppercase; letter-spacing: .08em; font-size: 11px; }
  #fkbar .how { font: italic 12.5px var(--title); color: var(--ink-2); }
  #fkbar .grp.map { color: var(--ink-2); }
  #fkbar .sp { flex: 1; }
  #fkbar kbd { font: 600 10.5px var(--label); border: 1px solid var(--rule, #bbb); border-bottom-width: 2px; border-radius: 3px; padding: 1px 5px; background: var(--paper, #fff); color: var(--ink-2); }
  #fkbar button { font: 600 11.5px var(--label); text-transform: uppercase; letter-spacing: .06em; background: var(--sheet); color: var(--ink);
    border: 1px solid var(--ink); padding: 4px 9px; cursor: pointer; }
  #fkbar .grp button { min-width: 26px; padding: 3px 6px; font-size: 14px; line-height: 1; }
  #fkbar button:hover:not(:disabled) { background: var(--paper-2, #eee); }
  #fkbar button:disabled { opacity: .4; cursor: default; }
  #fkbar button.primary { background: var(--ink); color: var(--sheet); }
  #fkbar button[hidden] { display: none; }
  #fkbar .fkread { display: flex; gap: 14px; justify-content: space-between; border-top: 1px solid var(--rule, #ccc); padding: 5px 10px;
    font: 13px var(--title); font-style: italic; text-transform: none; letter-spacing: 0; color: var(--ink-2); }
  #fkbar .fkread b { font-style: normal; color: var(--ink); }
  #fkbar .fkread .bad { color: var(--survey); font-weight: 700; font-style: normal; }
  #fkst { white-space: nowrap; }
  .gpin.fk-handle { width: 9px; height: 9px; border-radius: 0; background: var(--sheet, #fff); border: 1.5px solid var(--survey); }
  #body p.fit span.bad { color: var(--survey); font-weight: 700; }
  body.placing #fitbig { display: inline-block; }
  body.placing .fitpane:not(.big) { top: auto; left: auto; right: 12px; bottom: 36px; width: 300px; height: 240px; }
  body.placing .fitpane.min:not(.big) { height: auto; }
  body.placing .fitpane:not(.big) .fit-tools { display: none; }
  body.placing #body .seg, body.placing #body ol.pairs, body.placing #fother { display: none; }
  @media (max-width: 760px) {
    #fkbar { top: auto; bottom: 8px; left: 8px; right: 8px; }
    #fkbar .grp.map, #fkbar kbd { display: none; }
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
