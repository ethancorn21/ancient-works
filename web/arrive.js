/* Arrival from the ethanlawcorn.com hub. The hub ends its "Ancient Works" morph as survey contours in red ink on
   Resurface paper, then comes here with ?via=hub&b=x,y,w,h&v=W,H (the contours' box and the hub's viewport, CSS px).
   This script redraws that exact last frame before anything else paints, waits for the map, then lifts the
   contours off (outer ring first) and fades the paper away, so the hand-off reads as one motion.
   It must load first in <head>, before the stylesheets. Without ?via=hub it does nothing.
   The contour generator below is a verbatim copy of tContours/fit/resample in the hub
   (digitalgarden strata/template.html); change both together or the frames stop matching. */
(function () {
  'use strict';
  var q;
  try { q = new URLSearchParams(location.search); } catch (e) { return; }
  if (q.get('via') !== 'hub') return;
  try {
    q.delete('via'); var bs = q.get('b'), vs = q.get('v'); q.delete('b'); q.delete('v');
    var rest = q.toString();
    history.replaceState(history.state, '', location.pathname + (rest ? '?' + rest : '') + location.hash);
  } catch (e) {}
  var reduce = false;
  try { reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  var b = (bs || '').split(',').map(Number), v = (vs || '').split(',').map(Number);
  if (reduce || b.length !== 4 || b.some(isNaN)) return;

  var PAPER = '#F3EDDC', INK = '#CE2E4E', TAU = Math.PI * 2, K = 18, P = 96;
  var root = document.documentElement;
  root.style.background = PAPER;
  var lerp = function (a, c, t) { return a + (c - a) * t; };
  var clamp = function (x) { return x < 0 ? 0 : x > 1 ? 1 : x; };

  /* ---- verbatim from the hub ---- */
  function resample(poly, closed) {
    var pts = closed ? poly.concat([poly[0]]) : poly, L = [0];
    for (var i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    var tot = L[L.length - 1] || 1, out = new Float32Array(P * 2), j = 1, n = closed ? P : P - 1;
    for (var p = 0; p < P; p++) {
      var d = tot * p / n;
      while (j < L.length - 1 && L[j] < d) j++;
      var t = (d - L[j - 1]) / ((L[j] - L[j - 1]) || 1);
      out[2 * p] = lerp(pts[j - 1][0], pts[j][0], t); out[2 * p + 1] = lerp(pts[j - 1][1], pts[j][1], t);
    }
    return out;
  }
  function fit(strokes, box) {
    var x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    strokes.forEach(function (s) { s.poly.forEach(function (q) { x0 = Math.min(x0, q[0]); x1 = Math.max(x1, q[0]); y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); }); });
    var sc = Math.min(box.w / (x1 - x0), box.h / (y1 - y0)), ox = box.x + (box.w - (x1 - x0) * sc) / 2 - x0 * sc, oy = box.y + (box.h - (y1 - y0) * sc) / 2 - y0 * sc;
    return strokes.map(function (s) {
      return { pts: resample(s.poly.map(function (q) { return [ox + q[0] * sc, oy + q[1] * sc]; }), s.closed), closed: s.closed, w: s.w || 1.2 };
    });
  }
  function contours(box) {
    var st = [];
    for (var k = 0; k < K; k++) {
      var r0 = .1 + .9 * k / (K - 1), poly = [];
      for (var i = 0; i < 90; i++) {
        var t = i / 90 * TAU;
        var r = r0 * (1 + .1 * Math.sin(2 * t + .4) + .06 * Math.sin(3 * t + k * .15) + .04 * Math.cos(5 * t - k * .1));
        poly.push([r * Math.cos(t) * 1.25 + .06 * (1 - r0), r * Math.sin(t) * .8]);
      }
      st.push({ poly: poly, closed: true, w: k % 5 === 4 ? 2.1 : .95 });
    }
    return fit(st, box);
  }
  /* ---- end of the copy ---- */

  var ov = document.createElement('div');
  ov.setAttribute('aria-hidden', 'true');
  ov.style.cssText = 'position:fixed;inset:0;z-index:2147483000;background:' + PAPER + ';pointer-events:none;transition:opacity .9s ease;';
  var cv = document.createElement('canvas');
  cv.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block;';
  ov.appendChild(cv);
  root.appendChild(ov);
  var cx = cv.getContext('2d'), W = 0, H = 0, D = 1, S = null;
  function size() {
    W = window.innerWidth; H = window.innerHeight; D = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = Math.round(W * D); cv.height = Math.round(H * D);
    /* if the viewport changed in between (a phone's address bar), move and scale the box with it */
    var sx = v[0] > 0 ? W / v[0] : 1, sy = v[1] > 0 ? H / v[1] : 1, s = Math.min(sx, sy);
    var cxB = (b[0] + b[2] / 2) * sx, cyB = (b[1] + b[3] / 2) * sy;
    S = contours({ x: cxB - b[2] * s / 2, y: cyB - b[3] * s / 2, w: b[2] * s, h: b[3] * s });
  }
  /* lift: 0 = the hub's last frame; 1 = gone. Outer contours lift first, each undrawn along its own path */
  function draw(lift) {
    cx.setTransform(D, 0, 0, D, 0, 0); cx.clearRect(0, 0, W, H);
    cx.strokeStyle = INK; cx.lineJoin = 'round'; cx.lineCap = 'round';
    for (var k = 0; k < K; k++) {
      var s = S[k], d = (K - 1 - k) / (K - 1) * .45, f = 1 - clamp((lift - d) / .55);
      if (f <= 0) continue;
      var n = Math.max(2, Math.round(P * f));
      cx.lineWidth = s.w; cx.beginPath();
      for (var p = 0; p < n; p++) { var x = s.pts[2 * p], y = s.pts[2 * p + 1]; if (p) cx.lineTo(x, y); else cx.moveTo(x, y); }
      if (f >= 1 && s.closed) cx.closePath();
      cx.stroke();
    }
  }
  size(); draw(0);
  window.addEventListener('resize', function () { size(); draw(0); });

  var t0 = performance.now(), done = false;
  function ready() { return !!document.querySelector('.maplibregl-canvas'); }
  function go() {
    if (done) return; done = true;
    var s0 = performance.now(), dur = 1100;
    (function step(now) {
      var x = clamp((now - s0) / dur), e = x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
      draw(e);
      if (x > .35) ov.style.opacity = '0';
      if (x < 1) requestAnimationFrame(step);
      else setTimeout(function () { ov.remove(); root.style.background = ''; }, 950);
    })(s0);
  }
  /* the map's canvas exists and has had a moment to draw; never hold the page longer than 3 s */
  (function wait() {
    var el = performance.now() - t0;
    if ((ready() && el > 1200) || el > 3000) go(); else setTimeout(wait, 100);
  })();
})();
