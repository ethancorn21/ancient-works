/* Open the map on the works (task 307ba, 307b's box 2): the 'Ready to fit' queue already
   knows where each picture starts - the entry's `propose` (fit/propose.propose_for: the
   anchor that maps the picture's panel centre onto the site at the recorded scale and
   rotation, re-emitted as 3-5 page-px -> lon/lat pairs) - so opening the queued site's
   best plan puts the drawing ON the map before any clicking:

   - the map flies to the site's own box (its four corners), centred beside the fit pane,
     before the ink appears;
   - while place mode is open, the site's earlier overlay (the fitted drawing or survey
     sheet applyDep was showing - the `dep-<site.id>` layer) is hidden, so the drawing
     sits on clean ground ("As soon as you go into that place mode the already placed
     overlay needs to go");
   - the anchor (panel centre on the site centre, its m-per-px and rotation) is seeded
     onto P and re-emitted as the page's 5 pairs (4 panel corners + centre, numbered
     1..5 with the page's own draggable markers): the page's preview, Undo, Clear, Save
     and the map-click pin flow all apply to them unchanged;
   - closing (back, Cancel, or saving) brings the overlay back exactly as it was -
     applyDep with S.depSel/S.depMode/S.depOpacity/S.ground never touched - and the
     placement state clears. A save shows the new overlay: the page's saveFit success
     path runs this same restore before its own applyDep.

   A site or plan without a propose (or whose picture fails to load) opens exactly as
   today: the ordinary three-point flow, byte-identical (the 305 part-3 card test pins
   it - its served tree 404s the page scan, so place mode never activates there).

   index.html takes no fitkit footprint of its own, so this file loads after fitqueue.js
   (itself after review.js) and extends the page the same way they do - by reassigning
   the page's globals: openPlan LAST in the chain (page -> review -> fitkit; fitqueue.js
   wraps renderList/saveFit only) and endFit (the page-level original - neither review
   nor fitqueue wraps it). The row's page-px frame is the loaded image's frame scaled by
   the row's recorded size: tools/export_plans.py copies size and map_box from the book
   index row, the very fields propose.py read, so the propose's pairs are page px
   (verified: every current queue entry's served image is exactly its recorded size). A
   frame that cannot be related (a non-uniform resample) falls back to the ordinary
   flow. The gestures that move, scale and turn the whole drawing (307bb) build on the
   P.anchor this file seeds and keeps current. _fk-prefixed names: one global lexical
   scope per page (the web/ pitfall) - review.js's _openPlan et al. stay untouched.
*/

const _fkOpenPlan = openPlan;
const _fkEndFit = endFit;

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
  const pad = narrow() ? { top: 20, right: 20, bottom: innerHeight * 0.5, left: 20 }
                       : { left: 390, top: 20, right: 20, bottom: 20 };
  map.fitBounds([[Math.min(...ws), Math.min(...ns)], [Math.max(...ws), Math.max(...ns)]],
                { padding: pad, duration: 900, essential: true });
  // the earlier overlay goes while place mode is open; the endFit wrapper brings it back
  if (map.getLayer('dep-' + site.id)) map.setLayoutProperty('dep-' + site.id, 'visibility', 'none');
  // a fresh start (every path into openPlan reset via startFit): clear anyway, then seed
  P.pairs = []; P.pending = null; P.marks.forEach(m => m.remove()); P.marks = [];
  for (const p of _fkReemit(P.anchor)) { P.pairs.push(p); addPairMarker(p); }  // numbered 1..5, draggable, like the map-click path
  refit();
}

openPlan = async function (r) {
  const out = await _fkOpenPlan(r);
  _fkActivate();
  return out;
};

/* After the inner endFit (markers gone, the preview removed, the pane closed, the site
   view re-rendered): if place mode was on, the site's overlay comes back exactly as it
   was - applyDep with S.depSel/S.depMode/S.depOpacity/S.ground never touched - and the
   placement state clears. The page's saveFit success path reaches the same restore, so
   a save shows the new overlay (its own applyDep right after is idempotent). */
endFit = function (keepSite) {
  const wasPlaced = !!P.placed;
  const site = P.site;
  const out = _fkEndFit(keepSite);
  if (wasPlaced) {
    if (site) applyDep(site);
    P.placed = false; P.anchor = null; P.anchorStack = [];
  }
  return out;
};
