// Task 306b - headless visual audit of the 21 agent fits whose plan is a candidate of the site's
// review item: the doc is in the store but the site's overlay is not built, so the fit never
// reached the map. Rendered the way a visitor would see it if the page showed it.
//
// Per doc (the parent's recipe, the review-tab flow from web/review.js rvStartFitAt):
//   select(site) -> setGround('imagery'|'relief', site) -> startFit(site) ->
//   openPlan(rvResolveRow(site, cand)) with the DOC's own stored pairs, then refit() - which
//   draws the fitted plate as the map layer 'fit-prev' and shows the residuals in the pane.
// The review tab would pre-place the item's candidate pairs instead; for all 21 docs they differ
// from the doc's (only castle-neroche n0110_1 matches), so this audit looks at the document.
//
// One 307 trap, neutralised in the IIFE (web/*.js is agent a's territory, so the fix lives here):
// the fit queue (web/fit_queue.json + fitkit.js) pre-places a machine candidate (5 anchor
// pairs) whenever a queue entry proposes the same site's plan - nine of the 21 docs match one.
// Those 5 pairs then blend with the doc's 8 in a 13-point least squares, and the preview ink
// (and the fithint) show the blend, not the document. The IIFE empties FQ.entries before
// openPlan (fitkit's _fkActivate falls open when no entry matches) so the shot is the doc's
// own placement; the [eval] line reports fqEntries (count before emptying) and placed
// (P.placed after openPlan) so a contaminated run is visible in the log.
// One 1440x900 shot per doc over the aerial photograph, plus a second over the prebuilt LiDAR
// relief (web/data/sites/<site>/relief.jpg) where the site has one (all 10 sites here do).
//
// GET only, against server/serve.py --port 0 (the OS picks an ephemeral port): safe for
// parallel checkouts. Screenshots land in docs/site_flow/agent_fits/<site>_<plan>.png
// (aerial) and ..._<plan>_relief.png. Re-runs skip a shot whose file already exists.
//
//   node tools/audit_306b.mjs                      # all 21 docs, 10 sites, 42 shots
//   node tools/audit_306b.mjs <docId> [docId ...]  # one or more docs only
//
// Run from the project root with .venv present (the server starts with .venv/bin/python so its
// optional relief-tile import resolves; the audit itself only needs GETs).

import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { mkdirSync, readFileSync, existsSync } from 'node:fs';

// The 21 docs of this task (data/db/platefits/<doc>.json), in the task file's order.
const DOCS = [
  'argentoratum-q2361353.c_191c6221a81caad0', 'argentoratum-q2361353.c_436bea5010beea89',
  'argentoratum-q2361353.c_5badc8c867ef5d98', 'argentoratum-q2361353.c_5bfb0472f266c056',
  'argentoratum-q2361353.c_6acfd94dec8c011b', 'argentoratum-q2361353.c_87dc28a9645f0e59',
  'argentoratum-q2361353.c_8bdbed9b69d51319', 'argentoratum-q2361353.c_b3533cd48dfc6452',
  'argentoratum-q2361353.c_e882645cc479c889', 'argentoratum-q2361353.c_ec1930f8ba9bbabb',
  'carisbrooke-castle-q328595.c_c280ff908ad8318d', 'castle-neroche-q5050201.c_44529cdbe2d10a9c',
  'castle-neroche-q5050201.earthworkenglan01allcgoog_n0110_1', 'castra-lemanis-q499898.c_be12fb0f9a87000b',
  'cawthorne-camp-q5055239.earthworkenglan01allcgoog_n0325_1', 'cenabum-q2710144.c_e73dc8c09b2fea43',
  'dudley-castle-q5311832.c_e66ec095ee45aed0', 'ferme-d-azincourt-q20669811.c_804aa7af3eb2ac7c',
  'watson-brake-q2552689.c_5e7bb19c79b509ed', 'watson-brake-q2552689.c_b52ddcad2ee295c4',
  'zwolle-q793.c_f9cddae6b944a648',
];
const outDir = 'docs/site_flow/agent_fits';

// The candidate object rvResolveRow takes: the doc's own fields (the item's candidate would
// carry its own title/pairs; the row lookup is by plan id, so the doc's copy resolves the same
// plans.json row when one exists - for the two IA book pages - and synthesizes the rest).
const candOf = d => ({
  plan: d.plan, title: d.title || d.plan, url: d.url || null, ia: d.ia || null,
  file: d.file || null, book: d.book || null, label: d.label || null,
  cite: d.cite || null, ref: d.ref || null, map_box: null,
});

const iife = (ground, site, pairs, cand) => `(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let s = null;
  for (let i = 0; i < 200; i++) { s = (typeof S !== 'undefined' && S.byId) ? S.byId[${JSON.stringify(site)}] : null; if (s) break; await sleep(150); }
  if (!s) return { ok: false, why: 'site not in S.byId after 30 s' };
  // let loadPlans() finish so rvResolveRow can find a real plans.json row (the IA book pages), and let the page's
  // start() set S.ready - until then ensureSite() (called from select) bails, and the per-site relief.jpg layer
  // is never added (the live /tiles/relief is off on this machine, so relief.jpg is the only relief the page shows)
  for (let i = 0; i < 200; i++) { if (typeof P !== 'undefined' && P.rows && P.rows.length && S.ready) break; await sleep(150); }
  // 307's fit queue pre-places its machine candidate when a queue entry proposes this site's
  // plan: _fkActivate seeds 5 anchor pairs that the doc's 8 would blend into a 13-point fit, so
  // the preview would show the blend, not the document. The audit looks at the document: wait
  // for the one-shot fetch to land, then empty it (_fkActivate finds no entry and falls open).
  let fqEntries = 'no FQ';
  if (typeof FQ !== 'undefined') {
    for (let i = 0; i < 100 && !FQ.loaded; i++) await sleep(150);
    fqEntries = FQ.entries.length;
    FQ.entries.length = 0;
  }
  select(s.id);
  await loadDeps(s);
  setGround(${JSON.stringify(ground)}, s);
  await loadDeps(s);
  ensureSite(s);  // in case select() ran before the page's start(): re-arm, it is a no-op once loaded
  applyAll();
  // wait for select()'s 4.5 s flyTo to settle before opening the plan: openPlan's easeTo keeps the CURRENT zoom,
  // so if the flyTo is still mid-flight when it fires, the shot lands at country zoom (aerial fills the frame)
  const span = Math.max(...s.size_m);
  const target = 15 - Math.max(0, Math.log2(span / 1800));
  for (let i = 0; i < 80; i++) { if (Math.abs(map.getZoom() - target) < 0.1) break; await sleep(150); }
  startFit(s);
  const row = rvResolveRow(s.id, ${JSON.stringify(cand)});
  await openPlan(row);
  const out = {
    ok: true, site: s.id, plan: P.plan && P.plan.id,
    rowTitle: P.plan && P.plan.title, rowMapBox: P.plan && P.plan.map_box || null,
    img: !!P.img, fithint: ($('#fithint') || {}).textContent || null,
    ground: S.ground, model: P.model, ready: S.ready,
    relLayer: map.getLayer('rel-' + s.id) ? map.getLayoutProperty('rel-' + s.id, 'visibility') : 'absent',
    fqEntries, placed: !!P.placed, anchor: !!P.anchor,
    n: 0, fit: null, layer: !!map.getLayer('fit-prev'),
  };
  if (P.img) {
    for (const p of ${JSON.stringify(pairs)}) {
      const q = { u: +p[0], v: +p[1], lon: +p[2], lat: +p[3] };
      P.pairs.push(q); addPairMarker(q);
    }
    refit();
    out.n = P.pairs.length;
    out.layer = !!map.getLayer('fit-prev');
    if (P.fit) out.fit = { resid: P.fit.resid.map(x => Math.round(x * 10) / 10), mpx: Math.round(P.fit.mpx * 100) / 100, rot: Math.round(P.fit.rot * 10) / 10 };
    await sleep(400);
  }
  if (Math.abs(map.getZoom() - target) > 0.2) {  // the openPlan easeTo grabbed a mid-flight zoom: re-issue the site's camera
    const right = $('#fitpane').getBoundingClientRect().right;
    map.easeTo({ center: [s.lon, s.lat], zoom: target, padding: { left: right + 10, top: 20, right: 20, bottom: 20 }, duration: 900 });
    await sleep(1000);
  }
  out.zoom = Math.round(map.getZoom() * 100) / 100;
  return out;
})()`; 

const runShot = async (shotArgs) => {
  const { url, out, wait, w, h, js, postwait } = shotArgs;
  return new Promise((resolve) => {
    const child = spawn('node', ['tools/shot.mjs', url, out, wait, w, h, js], {
      env: { ...process.env, NODE_PATH: '/home/agent/tools/shot/node_modules', POSTWAIT: postwait },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '', stderr = '';
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });
    const kill = setTimeout(() => { try { child.kill('SIGKILL'); } catch {} }, 180_000);
    child.on('close', (code) => {
      clearTimeout(kill);
      if (stderr.trim()) console.log(stderr.trim());
      for (const line of stdout.split('\n')) {
        if (line.startsWith('[eval]') || line.startsWith('[pageerror]') || line.startsWith('[reqfail]')) console.log(line);
      }
      resolve({ code, ok: existsSync(out) });
    });
  });
};

const main = async () => {
  const want = process.argv.slice(2);
  const docs = want.length ? want.filter(d => DOCS.includes(d)) : DOCS;
  mkdirSync(outDir, { recursive: true });

  // one server for the whole run; the OS picks a free port
  const server = spawn('.venv/bin/python', ['server/serve.py', '--port', '0'], { stdio: ['ignore', 'pipe', 'pipe'] });
  let buf = '';
  let port = await new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('server did not report a port in 20 s')), 20_000);
    server.stdout.on('data', (d) => {
      buf += d;
      const m = buf.match(/Ancient Works on http:\/\/127\.0\.0\.1:(\d+)\//);
      if (m) { clearTimeout(t); resolve(m[1]); }
    });
  });
  console.log(`[audit] server on ${port}; docs: ${docs.length}`);

  const fails = [];
  try {
    for (const doc of docs) {
      const d = JSON.parse(readFileSync(`data/db/platefits/${doc}.json`, 'utf8'));
      const { site, plan } = d;
      const relief = existsSync(`web/data/sites/${site}/relief.jpg`);
      for (const ground of relief ? ['imagery', 'relief'] : ['imagery']) {
        const out = `${outDir}/${site}_${plan}${ground === 'relief' ? '_relief' : ''}.png`;
        if (existsSync(out)) { console.log(`[audit] SKIP ${site} ${plan} ground=${ground} (exists)`); continue; }
        const r = await runShot({
          url: `http://127.0.0.1:${port}/`, out, wait: '5000', w: '1440', h: '900',
          js: iife(ground, site, d.pairs, candOf(d)),
          postwait: ground === 'imagery' ? '12000' : '7000',
        });
        const stat = { pairs: d.pairs.length, score: d.score, model: d.model, by: d.by };
        console.log(`[audit] ${site} ${plan} ground=${ground} code=${r.code} file=${r.ok ? 'written' : 'MISSING'} ${JSON.stringify(stat)}`);
        if (r.code !== 0 || !r.ok) fails.push(`${site} ${plan} ${ground}`);
      }
    }
  } finally {
    try { server.kill('SIGTERM'); await sleep(500); } catch {}
    try { server.kill('SIGKILL'); } catch {}
  }
  console.log(fails.length ? `[audit] FAILURES: ${fails.join(' | ')}` : `[audit] all shots written to ${outDir}`);
  process.exit(fails.length ? 1 : 0);
};

main();
