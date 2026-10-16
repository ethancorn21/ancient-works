// Resurface logo: the hero study's tContours (crt-hero/hero.js), same formula, written out as SVG.
const TAU = Math.PI * 2;
function rings(K, pick, N = 160) {
  const out = [];
  for (let k = 0; k < K; k++) {
    if (pick && !pick(k)) continue;
    const r0 = .1 + .9 * k / (K - 1), poly = [];
    for (let i = 0; i < N; i++) { const t = i / N * TAU; const r = r0 * (1 + .1 * Math.sin(2 * t + .4) + .06 * Math.sin(3 * t + k * .15) + .04 * Math.cos(5 * t - k * .1)); poly.push([r * Math.cos(t) * 1.25 + .06 * (1 - r0), r * Math.sin(t) * .8]); }
    out.push({ k, poly });
  }
  return out;
}
function svg(rs, size, pad, wOf, opts = {}) {
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  rs.forEach(r => r.poly.forEach(([x, y]) => { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }));
  const W = size[0], H = size[1], sc = Math.min((W - 2 * pad) / (x1 - x0), (H - 2 * pad) / (y1 - y0));
  const ox = (W - (x1 - x0) * sc) / 2 - x0 * sc, oy = (H - (y1 - y0) * sc) / 2 - y0 * sc, f = v => +v.toFixed(2);
  const paths = rs.map(r => `<path d="M${r.poly.map(([x, y]) => f(ox + x * sc) + ' ' + f(oy + y * sc)).join('L')}Z" stroke-width="${wOf(r.k)}"/>`).join('');
  const bg = opts.bg ? `<rect width="${W}" height="${H}" fill="${opts.bg}"/>` : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}">${bg}<g fill="none" stroke="${opts.ink || '#CE2E4E'}" stroke-linejoin="round">${paths}</g></svg>`;
}
const fs = require('fs'); process.chdir(process.argv[2] || '.');
// full logo: all 18 rings, every fifth an index contour, as in the study
fs.writeFileSync('logo.svg', svg(rings(18), [400, 260], 8, k => k % 5 === 4 ? 2.1 : .95));
// small mark (wordmark, ~24px): 6 rings, the 4th heavy
fs.writeFileSync('mark.svg', svg(rings(6, null, 72), [60, 40], 2, k => k === 3 ? 3.2 : 1.6, { ink: 'currentColor' }));
// favicon: 4 rings on paper
fs.writeFileSync('favicon.svg', svg(rings(4, null, 64), [32, 32], 2.5, k => k === 2 ? 2.4 : 1.4, { bg: '#F3EDDC' }));
