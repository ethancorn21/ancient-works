// Task 306g - headless visual audit of the 16 lead-port on-map matcher re-fits (the last platefit
// documents with no audit record in this repo).
//
// Each of the 16 docs is an overlay built in its site's web/data/sites/<site>/depictions.json
// (fit.doc == the doc id), placed on the map by the lead's own ports (commits 20277f3, 0685a4c,
// 77405cf) as fitter: matcher re-fits (8 stored pairs each, residuals <= 0.3 m - georeferenced
// sheets whose sheet frame is the fit). The audit is the visitor's way, exactly as 306a: open the
// site (select -> the doc's depiction activated -> ground layer), 1440x900 over the aerial
// photograph, plus a second over the prebuilt LiDAR relief (relief.jpg) where the site has one.
// The [eval] line per shot confirms the doc's depiction is the active layer on screen and
// reports the stored fit statistics (resid_m, m_per_px, rot_deg from depictions.json).
//
// GET only, against server/serve.py --port 0 (the OS picks an ephemeral port): safe for parallel
// checkouts. Screenshots land in docs/site_flow/agent_fits/<site>_<plan>.png (aerial) and
// ..._<plan>_relief.png.
//
//   node tools/audit_306g.mjs                      # all 16 docs, 15 sites
//   node tools/audit_306g.mjs <doc-id> [doc ...]   # a subset (doc ids as in data/db/platefits/)
//
// Run from the project root with .venv present (the server starts with .venv/bin/python so its
// optional relief-tile import resolves; the audit itself only needs GETs).
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { mkdirSync, readFileSync, existsSync } from 'node:fs';

// (site, doc) pairs; the doc id's site prefix is not a reliable split in general, so it is stated.
const DOCS = [
  ['arras-q131329', 'arras-q131329.c_4e242bc2623751a0'],
  ['avesnes-sur-helpe-q217178', 'avesnes-sur-helpe-q217178.c_61fbbcd3d6051cd9'],
  ['bavay-q477176', 'bavay-q477176.c_e8345a33509010ae'],
  ['burcht-van-leiden', 'burcht-van-leiden.c_2ed7167f77ea05d4'],
  ['burcht-van-leiden', 'burcht-van-leiden.c_b790b0ce40d7d26b'],
  ['cahokia-q333661', 'cahokia-q333661.c_1a7c2a11c3a0dd21'],
  ['douai-q193826', 'douai-q193826.c_661c074bcd04d49a'],
  ['gouda-q84125', 'gouda-q84125.c_ba646ea988fc6bc8'],
  ['gravelines-q323399', 'gravelines-q323399.c_173e0d61c038bada'],
  ['groningen-q749', 'groningen-q749.c_498f9aa12d03fc30'],
  ['le-cateau-cambresis-q329103', 'le-cateau-cambresis-q329103.c_f613a7c2165ba280'],
  ['lille-q648', 'lille-q648.c_1f7cce1c856a7bcb'],
  ['saint-omer-q208793', 'saint-omer-q208793.c_df791c935a4905f7'],
  ['utrecht-q803', 'utrecht-q803.c_f5f96070065c0763'],
  ['valenciennes-q163795', 'valenciennes-q163795.c_0b5e6f27e6aeba51'],
  ['old-sarum-q782719', 'old-sarum-q782719.c_b2701b5231da42f2'],
];
const outDir = 'docs/site_flow/agent_fits';

// Open the site the visitor's way and confirm the doc's depiction is the active one.
// select() forces ground 'imagery' and depMode 'ink' (the visitor's default view: the drawing
// in ink lines over the aerial); we then pick the doc's depiction file and the ground wanted.
const iife = (ground, site, file) => `(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let s = null;
  for (let i = 0; i < 200; i++) { s = (typeof S !== 'undefined' && S.byId) ? S.byId[${JSON.stringify(site)}] : null; if (s) break; await sleep(150); }
  if (!s) return { ok: false, why: 'site not in S.byId after 30 s' };
  select(${JSON.stringify(site)});
  await loadDeps(s);
  const files = (S.dep[s.id] || []).map(x => x.file);
  const present = files.includes(${JSON.stringify(file)});
  S.depSel[s.id] = ${JSON.stringify(file)};
  setGround(${JSON.stringify(ground)}, s);
  applyDep(s);
  await sleep(300);
  const L = 'dep-' + s.id;
  return {
    present,
    ground: S.ground,
    layer: !!map.getLayer(L),
    visible: map.getLayer(L) ? map.getLayoutProperty(L, 'visibility') : null,
    active: S.depUrl[L] || null,
    zoom: map.getZoom(),
  };
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
  const pick = process.argv.slice(2);
  const jobs = pick.length ? DOCS.filter(([, d]) => pick.includes(d)) : DOCS;
  mkdirSync(outDir, { recursive: true });

  // one server for the whole run; the OS picks a free port
  const server = spawn('.venv/bin/python', ['server/serve.py', '--port', '0'], { stdio: ['ignore', 'pipe', 'pipe'] });
  let buf = '';
  let port = await new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('server did not report a port in 20 s')), 20_000);
    server.stdout.on('data', (d) => {
      buf += d;
      const m = buf.match(/(?:Resurface|Ancient Works) on http:\/\/127\.0\.0\.1:(\d+)\//);
      if (m) { clearTimeout(t); resolve(m[1]); }
    });
  });
  console.log(`[audit] server on ${port}`);

  const fails = [];
  try {
    for (const [site, doc] of jobs) {
      const depPath = `web/data/sites/${site}/depictions.json`;
      if (!existsSync(depPath)) { console.log(`[audit] SKIP ${doc}: no depictions.json for ${site}`); fails.push(`${doc} no depictions`); continue; }
      const deps = JSON.parse(readFileSync(depPath, 'utf8')).depictions || [];
      const dep = deps.find(x => (x.fit || {}).doc === doc);
      if (!dep) { console.log(`[audit] SKIP ${doc}: not an overlay in ${site} (the 16 must all be on the map)`); fails.push(`${doc} not on map`); continue; }
      const relief = existsSync(`web/data/sites/${site}/relief.jpg`);
      const plan = doc.slice(site.length + 1);
      for (const ground of relief ? ['imagery', 'relief'] : ['imagery']) {
        const out = `${outDir}/${site}_${plan}${ground === 'relief' ? '_relief' : ''}.png`;
        const r = await runShot({
          url: `http://127.0.0.1:${port}/`, out, wait: '5000', w: '1440', h: '900',
          js: iife(ground, site, dep.file),
          postwait: ground === 'imagery' ? '12000' : '7000',
        });
        const stat = { resid_m: dep.fit?.resid_m, m_per_px: dep.fit?.m_per_px, rot_deg: dep.fit?.rot_deg, label: dep.label };
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
