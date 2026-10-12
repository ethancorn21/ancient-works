// Task 306a - headless visual audit of the 23 agent fits that are ON the map.
//
// For each A-group doc (the overlay is built in web/data/sites/<site>/depictions.json, fit.doc ==
// the doc id) the site is opened the visitor's way (select -> the doc's depiction selected ->
// ground layer), and a 1440x900 screenshot is taken over the aerial photograph, plus a second
// over the prebuilt LiDAR relief (web/data/sites/<site>/relief.jpg) where the site has one
// (shotwick is aerial-only). The [audit] line per shot reports the stored fit statistics
// (resid_m, m_per_px, rot_deg from depictions.json) and the page's own confirmation (the
// [eval] line) that the doc's depiction layer is the active one on screen.
//
// GET only, against server/serve.py --port 0 (the OS picks an ephemeral port): safe for
// parallel checkouts. Screenshots land in docs/site_flow/agent_fits/<site>_<plan>.png
// (aerial) and ..._<plan>_relief.png.
//
//   node tools/audit_306a.mjs                     # all 23 docs, 12 sites
//   node tools/audit_306a.mjs <site> [site ...]   # one or more sites
//
// Run from the project root with .venv present (the server starts with .venv/bin/python so its
// optional relief-tile import resolves; the audit itself only needs GETs).
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import { mkdirSync, readFileSync, existsSync } from 'node:fs';

const SITES = [
  'aldenhaag-q23650779', 'alligator-effigy-mound-q4732645', 'avaricum-q281826',
  'barnard-castle-q4185811', 'barwick-in-elmet-castle-q4865964', 'bethlehem-q2523914',
  'binche-q95121', 'bolsover-castle-q2968590', 'burlington-house-q225471',
  'forthill', 'newark', 'shotwick-castle-q7502621',
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
  const sites = process.argv.slice(2).length ? process.argv.slice(2) : SITES;
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
  console.log(`[audit] server on ${port}`);

  const fails = [];
  try {
    for (const site of sites) {
      const depPath = `web/data/sites/${site}/depictions.json`;
      if (!existsSync(depPath)) { console.log(`[audit] SKIP ${site}: no depictions.json`); continue; }
      const deps = JSON.parse(readFileSync(depPath, 'utf8')).depictions || [];
      const relief = existsSync(`web/data/sites/${site}/relief.jpg`);
      for (const dep of deps) {
        const doc = (dep.fit || {}).doc;
        if (!doc) continue;
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
    }
  } finally {
    try { server.kill('SIGTERM'); await sleep(500); } catch {}
    try { server.kill('SIGKILL'); } catch {}
  }
  console.log(fails.length ? `[audit] FAILURES: ${fails.join(' | ')}` : `[audit] all shots written to ${outDir}`);
  process.exit(fails.length ? 1 : 0);
};

main();
