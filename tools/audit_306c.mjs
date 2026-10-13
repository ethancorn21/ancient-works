// Task 306c - headless visual audit of the 16 US ORPHAN agent fits: in the store, but neither
// built as an overlay nor referenced by any review item, so a visitor sees them not at all.
// Rendered the way the page would if it ever showed them: the fit tool over the aerial
// photograph, and over the LiDAR relief (every one of the 9 sites has a relief.jpg), with the
// doc's stored pairs placed and refitted.
//
// Per doc (the parent's recipe, the review-tab flow from web/review.js rvStartFitAt):
//   select(site) -> setGround('imagery'|'relief', site) -> startFit(site) ->
//   openPlan(rvResolveRow(site, cand)) with the DOC's own stored pairs, then refit() - which
//   draws the fitted plate as the map layer 'fit-prev' and shows the residuals in the pane.
// Orphans have no review item, so there is no item's candidate to compare against: the row is
// synthesized from the doc's own fields (rvResolveRow's fall-through), and the shot is exactly
// the document.
//
// One 307 trap, neutralised in the IIFE (web/*.js is agent a's territory, so the fix lives here):
// the fit queue (web/fit_queue.json + fitkit.js) pre-places a machine candidate (5 anchor
// pairs) whenever a queue entry proposes the same site's plan - two of the 16 docs match one
// (hodgen-s-cemetery-mound b24849959_n0353_1, pyramid-mound ancientmonuments00squi_n0134_1).
// Those 5 pairs would blend with the doc's in the least squares, and the preview ink (and the
// fithint) would show the blend, not the document. The IIFE empties FQ.entries before openPlan
// (fitkit's _fkActivate falls open when no entry matches) so the shot is the doc's own
// placement; the [eval] line reports fqEntries (count before emptying) and placed (P.placed
// after openPlan) so a contaminated run is visible in the log.
// One 1440x900 shot per doc over the aerial photograph, plus a second over the prebuilt LiDAR
// relief (web/data/sites/<site>/relief.jpg) - all 9 sites have one.
//
// GET only, against server/serve.py --port 0 (the OS picks an ephemeral port): safe for
// parallel checkouts. Screenshots land in docs/site_flow/agent_fits/<site>_<plan>.png
// (aerial) and ..._<plan>_relief.png. Re-runs skip a shot whose file already exists.
//
//   node tools/audit_306c.mjs                      # all 16 docs, 9 sites, 32 shots
//   node tools/audit_306c.mjs <docId> [docId ...]  # one or more docs only
//
// Run from the project root with .venv present (the server starts with .venv/bin/python so its
// optional relief-tile import resolves; the audit itself only needs GETs).

import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { mkdirSync, readFileSync, existsSync } from 'node:fs';

// The 16 docs of this task (data/db/platefits/<doc>.json), in the task file's order.
const DOCS = [
  'cahokia-q333661.annualreportofbu1218901891smit_n0200_1',
  'etowah-indian-mounds-q4533107.annualreportofbu1218901891smit_n0386_1',
  'fort-ancient-q5470727.b24849959_n0264_1',
  'hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1',
  'hodgen-s-cemetery-mound-q5876069.b24849959_n0353_1',
  'marietta.b24849959_n0195_1',
  'mound-cemetery-q6919104.annualreportofbu1218901891smit_n0563_1',
  'mount-horeb-earthworks-complex-q6921321.c_d1dff07f0da57b0e',
  'pyramid-mound-q7263260.ancientmonuments00squi_n0134_1',
  'serpent-mound-q968802.b24849959_n0313_1',
  'serpent-mound-q968802.c_15ff865e5f3d8ddb',
  'serpent-mound-q968802.c_2c260a03d1f8df1c',
  'serpent-mound-q968802.c_52dfe1fc979edf2c',
  'serpent-mound-q968802.c_7b01a4bb50d68b56',
  'serpent-mound-q968802.c_8ebd42607fbb96d8',
  'serpent-mound-q968802.c_dd2c553d611e610b',
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
  console.log(`[audit 306c] server on ${port}; docs: ${docs.length}`);

  const fails = [];
  try {
    for (const doc of docs) {
      const d = JSON.parse(readFileSync(`data/db/platefits/${doc}.json`, 'utf8'));
      const { site, plan } = d;
      const relief = existsSync(`web/data/sites/${site}/relief.jpg`);
      for (const ground of relief ? ['imagery', 'relief'] : ['imagery']) {
        const out = `${outDir}/${site}_${plan}${ground === 'relief' ? '_relief' : ''}.png`;
        if (existsSync(out)) { console.log(`[audit 306c] SKIP ${site} ${plan} ground=${ground} (exists)`); continue; }
        const r = await runShot({
          url: `http://127.0.0.1:${port}/`, out, wait: '5000', w: '1440', h: '900',
          js: iife(ground, site, d.pairs, candOf(d)),
          postwait: ground === 'imagery' ? '12000' : '7000',
        });
        const stat = { pairs: d.pairs.length, score: d.score, model: d.model, by: d.by };
        console.log(`[audit 306c] ${site} ${plan} ground=${ground} code=${r.code} file=${r.ok ? 'written' : 'MISSING'} ${JSON.stringify(stat)}`);
        if (r.code !== 0 || !r.ok) fails.push(`${site} ${plan} ${ground}`);
      }
    }
  } finally {
    try { server.kill('SIGTERM'); await sleep(500); } catch {}
    try { server.kill('SIGKILL'); } catch {}
  }
  console.log(fails.length ? `[audit 306c] FAILURES: ${fails.join(' | ')}` : `[audit 306c] all shots written to ${outDir}`);
  process.exit(fails.length ? 1 : 0);
};

main();
