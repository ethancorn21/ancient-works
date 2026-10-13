"""The owner's check (task 307d, the parent 307's last box): the save path, end to end, in a real
headless browser on two queue sites the way the owner uses it, then the test fits reverted.

The two sites are DERIVED, never pinned (the queue's population moves under the batch tasks):
A is the first queue entry that is one-site-line eligible (fit/propose's bar scale recorded on
its row, a book page in this checkout's data/raw, an unresolved review item carrying the row
with the save-floor pairs, no platefits doc for the site yet, a page-showable auto depiction,
no pre-existing drawing depiction, and an entry following it so the card can move on); B is
the same with the site-size-only fallback scale (and a different ground credit where one
exists). As of this run both picks sit on LiDAR relief (lidar null): no aerial-photograph-only
(lidar false) site is line-eligible in the current queue - the docs section says so plainly.

Each run (one headless Chrome page against the real server on a private copy of the tree, the
307bb part-4 recipe: every socket in the server process dead, ephemeral port, both picks' site
dirs materialised into the tree, both book pages copied into the tree's own data/raw) does
what the owner does: opens the queue, reads the card (it names the pick), clicks 'Place the
drawing' (the placement opens on the works: the propose's anchor, the five pairs and markers,
gestures on, the earlier overlay hidden), drags the drawing, scales it with the wheel, turns
it with shift+wheel, saves. Then the test verifies what the one-site line (305) does from that
save alone: the saved doc is by: hand with exactly the placed pairs (read from the tree), its
own fit agrees with the placed anchor, the overlay lands in the tree's depictions.json and is
what the page shows on the map, the site's square is recoloured in sites.json, the review item
is resolved and the site leaves the open review list, the card's done map marks the site and
the card moves on to the next pending entry. A page reload then shows the fit loading back
unchanged (the persisted selected depiction is the new overlay ink, the same square tier, the
done map kept), and the card still names the next pending.

Reverted before the test ends: the private tree is discarded (tmp dir), and the shared store
in the repo is proven byte-identical to before each run (the checkout's write surface - every
platefits doc, every review item, sites.json, review.json, fit_queue.json and every file under
both picks' site dirs, hashed through the checkout's own symlinks into the store). The
golden hand-fit hash check (tests/golden/hand_fit_docs.sha256) and test_fit_provenance run on
the same checkout and stay green for the same reason.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from conftest import copy_web

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHROME = "/opt/google/chrome/chrome"
NODE_MODULES = "/home/agent/tools/shot/node_modules"
AT = "2026-10-12T00:00:00.000Z"  # the done-map timestamp 307bb's card runs seed with

# The page's own filter and default pick (web/index.html): surveys only at 150 years or older,
# then the auto depiction is the first drawing or the LAST map.
SURVEY_KINDS = frozenset({"map", "aerial", "topo"})
DRAWING_KINDS = frozenset({"plan", "drawing", "view"})
# pipeline/build_site.py: the series error in metres, keyed by a substring of the depiction label
SERIES_ERR_M = {
    "Ordnance Survey six-inch": 8,
    "Etat-major": 40,
    "Topographic and Military Map of the Netherlands": 40,
    "Cassini": 250,
    "Roy's Military Survey": 250,
}
MIN_AGE_YEARS = 150  # pipeline/depict.py

# The page's marker tiers (web/index.html)
TIERS = [(2.5, "t4"), (1.6, "t3"), (1.2, "t2"), (0.01, "t1")]

# The subprocess guard: every socket dies loudly, then the server runs exactly as
# `server/serve.py --port 0` would (copied from tests/test_fit_queue.py: 235 owns that file).
GUARD = r"""
import runpy
import socket
import sys

def _dead(*args, **kwargs):
    raise AssertionError("the hermetic run attempted a network connection: %r" % (args,))

socket.socket.connect = _dead
socket.socket.connect_ex = _dead
socket.create_connection = _dead

args = sys.argv[1:] if sys.argv[0] == "-c" else sys.argv
script, *rest = args
sys.argv = [script] + rest
runpy.run_path(script, run_name="__main__")
"""


def _h(p):
    return Path(p).read_bytes()


def _item_of(root, site):
    """The site's review item in a tree, keyed by its `site` field (data/review/README.md).
    -> (path, item) or (None, None)."""
    d = Path(root) / "data" / "review"
    if not d.is_dir():
        return None, None
    for p in sorted(d.glob("*.json")):
        item = json.loads(p.read_text())
        if item.get("site") == site:
            return p, item
    return None, None


def _rows_naming(root, site):
    """The plans.json rows that name the site (the line's candidate rows)."""
    d = json.loads((Path(root) / "web" / "data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(d["cols"])}
    return [{k: r[i] for k, i in cols.items()} for r in d["rows"] if site in (r[cols["sites"]] or [])]


def _review_items():
    """The checkout's review items keyed by their `site` field (data/review/README.md)."""
    items = {}
    for p in (ROOT / "data" / "review").glob("*.json"):
        it = json.loads(p.read_text())
        if it.get("site"):
            items[it["site"]] = it
    return items


def _line_eligible(e, it):
    """The one-site line's constraints on a queue entry (tests/test_fit_queue.py's, copied: 235
    owns that file): a book row whose page is in this checkout's data/raw (the line reads it
    locally), an unresolved review item for the site carrying that row as a candidate with the
    page's save-floor pairs, and no platefits documents for the site yet.
    -> the site's uncovered rows, or None when any constraint fails."""
    row = e["best"]["row"]
    ia, file_ = row.get("ia"), row.get("file")
    if not (ia and file_):
        return None
    if not (ROOT / "data" / "raw" / "books" / ia / "full" / file_).is_file():
        return None
    if not it or (it.get("resolved") or {}).get("doc"):
        return None
    cand = next((c for c in it.get("candidates") or [] if c.get("plan") == row["id"]), None)
    if not cand or len(cand.get("pairs") or []) < 3:
        return None
    docs = {json.loads(p.read_text()).get("plan")
            for p in (ROOT / "data" / "db" / "platefits").glob("*.json")
            if p.name.startswith(e["site"] + ".")}
    if docs:
        return None
    item_plans = {c.get("plan") for c in it["candidates"]}
    return [r["id"] for r in _rows_naming(ROOT, e["site"])
            if r["id"] not in docs and r["id"] not in item_plans]


def _auto_dep(site):
    """The depiction the page's select() opens the site on (web/index.html, mirrored): the
    surveyOldEnough filter, then the first drawing-kind or the LAST map-kind depiction.
    -> the depiction or None."""
    dep = ROOT / "web" / "data" / "sites" / site / "depictions.json"
    if not dep.is_file():
        return None
    year_now = datetime.now(timezone.utc).year
    kept = [d for d in json.loads(dep.read_text()).get("depictions") or []
            if d.get("kind") not in SURVEY_KINDS or (d.get("year") and d["year"] <= year_now - MIN_AGE_YEARS)]
    for d in kept:
        if d.get("kind") in DRAWING_KINDS:
            return d
    maps = [d for d in kept if d.get("kind") == "map"]
    return maps[-1] if maps else None


def _picker():
    """The two owner-check sites, derived from the checkout (never pinned):
    A = the first line-eligible queue entry with a page-showable auto depiction, no
          pre-existing drawing depiction, an entry following it, and a RECORDED BAR scale;
    B = the same with the SITE-SIZE-ONLY fallback scale (a different lidar_credit than A when
          one exists; today every eligible site is Environment Agency LiDAR, so B is the first).
    -> ((queue index, entry, auto dep, sites.json record) for A, the same for B) or (None, None)."""
    q = json.loads((ROOT / "web" / "data" / "fit_queue.json").read_text())
    items = _review_items()
    sites = {s["id"]: s for s in json.loads((ROOT / "web" / "data" / "sites.json").read_text())["sites"]}
    elig = []
    for i, e in enumerate(q["entries"]):
        if not e.get("propose") or i + 1 >= len(q["entries"]):
            continue
        if not isinstance(_line_eligible(e, items.get(e["site"])), list):
            continue
        auto = _auto_dep(e["site"])
        if not auto:
            continue
        deps = json.loads((ROOT / "web" / "data" / "sites" / e["site"] / "depictions.json").read_text())["depictions"]
        if any(d.get("kind") in DRAWING_KINDS for d in deps):
            continue
        elig.append((i, e, auto, sites.get(e["site"])))
    a = next((t for t in elig if t[1]["propose"]["scale_source"] == "bar"), None)
    if a is None:
        return None, None
    b = next((t for t in elig if t[1]["propose"]["scale_source"] == "picture_size"
              and t[3] and a[3] and t[3].get("lidar_credit") != a[3].get("lidar_credit")), None) \
        or next((t for t in elig if t[1]["propose"]["scale_source"] == "picture_size"), None)
    return a, b


def _tier_of(score):
    """The page's tierOf (web/index.html)."""
    return next(t for th, t in TIERS if (score or 0) >= th)[1] if any((score or 0) >= th for th, _ in TIERS) else "plain"


def _score_of_deps(deps):
    """pipeline/build_site.py's overlays()+score() ported to the standard library: drawings at
    their fit residual, survey maps only at 150 years or older, at the series error.
    -> (score, number of counted overlays)."""
    year_now = datetime.now(timezone.utc).year
    newest = year_now - MIN_AGE_YEARS
    ovs = []
    for d in deps:
        y = d.get("year")
        if not y:
            continue
        if d.get("kind") in DRAWING_KINDS:
            res = (d.get("fit") or {}).get("resid_m")
            rms = math.sqrt(sum(r * r for r in res) / len(res)) if res else 30.0
            ovs.append((y, rms, True))
        elif y <= newest:
            err = next((e for k, e in SERIES_ERR_M.items() if k in (d.get("label") or "")), 100)
            ovs.append((y, err, False))
    vals = sorted(((year_now - y) / 100.0 / (1.0 + (e / 100.0) ** 2) * (1.0 if dr else 0.6)
                   for y, e, dr in ovs), reverse=True)
    return (round(vals[0] + 0.25 * sum(vals[1:]), 2), len(ovs)) if vals else (0, 0)


def _merc(lon, lat):
    """The page's merc (web/index.html: R = 6378137)."""
    r = 6378137.0
    return lon * math.pi / 180.0 * r, math.log(math.tan(math.pi / 4.0 + lat * math.pi / 360.0)) * r


def _simfit(pairs):
    """web/index.html's simFit ported to the standard library: least-squares similarity of
    (page px -> Mercator metres) as a complex number, with per-pair residuals in metres."""
    n = len(pairs)
    W = [(p["u"], -p["v"]) for p in pairs]
    Z = [_merc(p["lon"], p["lat"]) for p in pairs]
    wm = [sum(w[0] for w in W) / n, sum(w[1] for w in W) / n]
    zm = [sum(z[0] for z in Z) / n, sum(z[1] for z in Z) / n]
    nr = ni = d = 0.0
    for (wr0, wi0), (zr0, zi0) in zip(W, Z):
        wr, wi = wr0 - wm[0], wi0 - wm[1]
        zr, zi = zr0 - zm[0], zi0 - zm[1]
        nr += zr * wr + zi * wi
        ni += zi * wr - zr * wi
        d += wr * wr + wi * wi
    a0, a1 = nr / d, ni / d
    b0 = zm[0] - (a0 * wm[0] - a1 * wm[1])
    b1 = zm[1] - (a0 * wm[1] + a1 * wm[0])

    def at(u, v):
        return [a0 * u + a1 * v + b0, a1 * u - a0 * v + b1]

    k = math.cos(math.radians(pairs[0]["lat"]))
    resid = [math.hypot(at(p["u"], p["v"]) [0] - z[0], at(p["u"], p["v"])[1] - z[1]) * k
             for p, z in zip(pairs, Z)]
    return {"mpx": math.hypot(a0, a1) * k, "rot": math.degrees(math.atan2(a1, a0)), "resid": resid}


PROBE = r"""// node owner_probe.mjs <base_url> <site> <plan> <tree> <out_dir> <done_json> <item_file>
// The owner's check (task 307d): the owner's save path in headless Chrome on the served private
// tree: the card names the pick -> Place opens the placement on the works -> one drag, one wheel,
// one shift+wheel (each checked against the page's own fit, as in 307bb) -> Save -> the one-site
// line's four effects on the site view (the overlay on the map, the recoloured square, the item
// resolved, the done map written, the card moved on to the next pending) -> a page reload, where
// the fit loads back unchanged and the card still names the next pending. Prints one [eval] line
// with every state, then every console/pageerror/reqfail line, RESULT PASS/FAIL, exit 0/1.
import { createRequire } from 'module';
import { readFileSync } from 'fs';
const require = createRequire(process.env.NODE_PATH + '/');
const { chromium } = require('playwright-core');
const [url, site, plan, tree, outdir, doneJson, itemFile] = process.argv.slice(2);
const doneMap = JSON.parse(doneJson);
const docId = site + '.' + plan;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const failures = [];
const check = (name, cond, info) => {
  console.log((cond ? '[ok] ' : '[FAIL] ') + name + (cond ? '' : ' :: ' + JSON.stringify(info)));
  if (!cond) failures.push(name);
};

// installed as page globals once: the anchor's own similarity and the fit-vs-anchor checks the
// gestures must keep true at every step (the 307bb helper, verbatim)
const HELPERS = `
  window._fkvAnchorAt = (a, u, v) => {
    const [zx0, zy0] = merc([a.lon, a.lat]);
    const k = Math.cos(a.lat * Math.PI / 180);
    const t = a.rot * Math.PI / 180;
    const ar = a.mpx / k * Math.cos(t), ai = a.mpx / k * Math.sin(t);
    const dr = u - a.u0, di = a.v0 - v;
    return [zx0 + ar * dr - ai * di, zy0 + ai * dr + ar * di];
  };
  window._fkvFitChecks = () => {
    const a = P.anchor, f = P.fit, k = Math.cos(a.lat * Math.PI / 180);
    const maxResid = f ? Math.max(...f.resid) : -1;
    const [x0, y0, x1, y1] = P.crop;
    const corners = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
    const src = map.getStyle().sources['fit-prev'] ? map.getStyle().sources['fit-prev'].coordinates : null;
    let maxC = -1, closure = -1;
    if (f && src) {
      const ms = src.map(c => merc(c));
      const exps = corners.map(([u, v]) => _fkvAnchorAt(a, u, v));
      maxC = Math.max(...exps.map((z, i) => Math.hypot(ms[i][0] - z[0], ms[i][1] - z[1]))) * k;
      closure = Math.hypot((ms[2][0] - (ms[1][0] + ms[3][0] - ms[0][0])),
                           (ms[2][1] - (ms[1][1] + ms[3][1] - ms[0][1]))) * k;
    }
    return { dmpx: a ? Math.abs(f.mpx - a.mpx) : -1, drot: a ? Math.abs(f.rot - a.rot) : -1,
             maxResid, maxCorner: maxC, closure };
  };
`;

const browser = await chromium.launch({ channel: 'chrome', headless: true,
  args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 800 }, colorScheme: 'light' });
const lines = [];
const log1 = t => lines.push(t);
page.on('console', m => log1('[console] ' + m.type() + ' ' + m.text()));
page.on('pageerror', e => log1('[pageerror] ' + e.message));
page.on('requestfailed', r => log1('[reqfail] ' + r.url() + ' ' + (r.failure() && r.failure().errorText)));
// the card's done map seeded past the earlier queue entries puts the card on the pick (one object
// argument: this playwright-core takes at most one; its keys must match the destructured names)
await page.addInitScript(({ done }) => {
  try { localStorage.setItem('aw.fitQueue.done', JSON.stringify(done)); } catch {}
}, { done: doneMap });
await page.goto(url);

const boot = await page.evaluate(async () => {
  let ok = false;
  try {
    const t0 = Date.now();
    while (Date.now() - t0 < 60000) {
      if (S.ready && S.sites.length && FQ.loaded && FQ.entries.length) { ok = true; break; }
      await new Promise(r => setTimeout(r, 250));
    }
  } catch {}
  return { ok, fitkit: typeof _fkReemit === 'function' && typeof _fkOnWheel === 'function' };
});
if (!boot.ok) { console.log('[FAIL] boot :: ' + JSON.stringify(boot)); process.exit(1); }
check('boot: home view, fitkit loaded', boot.fitkit, boot);
await page.evaluate(HELPERS);

// ---- the card (home view): names the pick, its best row and the queue count
const card1 = await page.evaluate(s => {
  const c = document.getElementById('fqcard');
  if (!c) return null;
  const e = FQ.entries.find(x => x.site === s && x.best && x.best.row);
  const name = (c.querySelector('.fq-site b') || {}).textContent || null;
  const fit = (c.querySelector('.fit') || {}).textContent || '';
  return { text: c.textContent, name, fit,
           expectName: e ? (e.name || e.site) : null,
           expectTitle: e ? (e.best.row.title || e.best.row.id) : null };
}, site);
check('the card names the pick and its best row (not another entry)',
  !!card1 && !!card1.expectName && card1.name === card1.expectName &&
  card1.fit.includes(card1.expectTitle), card1);
await page.screenshot({ path: outdir + '/1-card.png' });

// ---- place: the card's own button (307bb's seed, verbatim, plus the ground)
await page.click('#fqplace', { timeout: 20000 });
const placed = await page.evaluate(async () => {
  const t0 = Date.now();
  while (Date.now() - t0 < 60000) {
    try { if (P.placed === true && P.img) return true; } catch {}
    await new Promise(r => setTimeout(r, 250));
  }
  return false;
});
await sleep(2500); // let the fly-to settle
check('place mode opened on the works', placed);
const seed = await page.evaluate(id => {
  const e = FQ.entries.find(x => x.site === id && x.propose);
  const a = P.anchor, c = e.propose.pairs[e.propose.pairs.length - 1];
  return { mpx: [a.mpx, e.propose.scale_m_px], rot: [a.rot, e.propose.rot_deg],
           centre: [a.lon, a.lat, c[2], c[3]], n: P.pairs.length, nMarks: P.marks.length,
           gestures: [map.dragPan.isEnabled(), map.scrollZoom.isEnabled(), map.touchZoomRotate.isEnabled(),
                      map.doubleClickZoom.isEnabled(), map.boxZoom.isEnabled()],
           dep: map.getLayer('dep-' + id) ? map.getLayoutProperty('dep-' + id, 'visibility') : null,
           fitPrev: !!map.getSource('fit-prev'),
           ground: S.ground, lidar: (S.byId[id] || {}).lidar,
           hint: (document.getElementById('fithint') || {}).textContent };
}, site);
console.log('[seed] ' + JSON.stringify(seed));
check('seed: anchor matches the propose (derived from the served queue file)',
  Math.abs(seed.mpx[0] - seed.mpx[1]) < 1e-9 && Math.abs(seed.rot[0] - seed.rot[1]) < 1e-9 &&
  Math.abs(seed.centre[0] - seed.centre[2]) < 1e-9 && Math.abs(seed.centre[1] - seed.centre[3]) < 1e-9, seed);
check('seed: the five pairs and markers are on the map, the drawing preview is up',
  seed.n === 5 && seed.nMarks === 5 && seed.fitPrev, seed);
check('seed: the gestures own the mouse (map pan/zoom off), the earlier overlay hidden',
  seed.gestures.every(v => v === false) && seed.dep === 'none', seed);
check('seed: the ground is the site\\'s own (LiDAR relief when lidar is not false)',
  seed.ground === (seed.lidar === false ? 'imagery' : 'relief'), { ground: seed.ground, lidar: seed.lidar });
check('seed: the panel readout shows the live scale and rotation',
  seed.hint.includes(seed.mpx[0].toFixed(2)) && seed.hint.includes('m per page pixel'), seed);
await page.screenshot({ path: outdir + '/2-placed.png' });

// ---- (a) drag: the pointer's ground delta moves the anchor's centre (307bb, verbatim)
const p0 = await page.evaluate(() => {
  // a map-canvas point right of the fit pane, clear of the five markers
  const r = map.getCanvas().getBoundingClientRect();
  const cands = [1075, 1105, 1040, 1140, 1000].map(x => [x, 400]);
  const proj = P.pairs.map(p => map.project([p.lon, p.lat]));
  const hit = q => proj.some(m => Math.hypot(m.x - q[0], m.y - q[1]) < 30);
  const q = cands.find(p => !hit(p)) || cands[0];
  return { x: q[0] + r.left, y: q[1] + r.top, q, proj: proj.map(p => [p.x, p.y]) };
});
check('drag start point clear of markers',
  Math.min(...p0.proj.map(m => Math.hypot(m[0] - p0.q[0], m[1] - p0.q[1]))) >= 30,
  { q: p0.q, proj: p0.proj });
const sx = p0.x + 30, sy = p0.y + 20;
const dragStart = await page.evaluate(({ x0, y0, x1, y1 }) => {
  // mirror the page's own drag math exactly: canvas-relative client point, unproject to a
  // [lon, lat] array (unproject's {lng, lat} object does not pass to merc), anchor' =
  // anchor + pointer delta in Mercator metres
  const r = map.getCanvas().getBoundingClientRect();
  const ll = (cx, cy) => { const u = map.unproject([cx - r.left, cy - r.top]); return [u.lng, u.lat]; };
  const a0 = { ...P.anchor };
  const a = merc(ll(x0, y0)), b = merc(ll(x1, y1)), h = merc([a0.lon, a0.lat]);
  return { a0, expected: unmerc([h[0] + b[0] - a[0], h[1] + b[1] - a[1]]) };
}, { x0: p0.x, y0: p0.y, x1: sx, y1: sy });
await page.mouse.move(p0.x, p0.y);
await page.mouse.down();
await page.mouse.move(sx, sy, { steps: 2 });
await page.mouse.up();
await sleep(400); // rAF-coalesced refit
const dragOut = await page.evaluate(() => ({
  a: P.anchor, fit: _fkvFitChecks(),
  pairs4: { u: P.pairs[4].u, v: P.pairs[4].v, lon: P.pairs[4].lon, lat: P.pairs[4].lat }
}));
check('drag: anchor moved by the pointer ground delta',
  Math.abs(dragOut.a.lon - dragStart.expected[0]) < 1e-6 && Math.abs(dragOut.a.lat - dragStart.expected[1]) < 1e-6,
  { got: [dragOut.a.lon, dragOut.a.lat], want: dragStart.expected });
check('drag: mpx and rot untouched', dragOut.a.mpx === dragStart.a0.mpx && dragOut.a.rot === dragStart.a0.rot);
check('drag: u/v invariant', dragOut.a.u0 === dragStart.a0.u0 && dragOut.a.v0 === dragStart.a0.v0);
check('drag: pair 5 (the centre) tracks the anchor at the doc rounding',
  dragOut.pairs4.lon === +dragOut.a.lon.toFixed(7) && dragOut.pairs4.lat === +dragOut.a.lat.toFixed(7) &&
  dragOut.pairs4.u === +dragOut.a.u0.toFixed(1) && dragOut.pairs4.v === +dragOut.a.v0.toFixed(1));
check('drag: fit agrees with the anchor (mpx 1e-3, rot 0.01 deg)',
  dragOut.fit.dmpx < 1e-3 && dragOut.fit.drot < 0.01, dragOut.fit);
check('drag: max residual < 2 m (the rounded five fit the similarity to rounding)',
  dragOut.fit.maxResid >= 0 && dragOut.fit.maxResid < 2, dragOut.fit);
check('drag: fit-prev source corners are the anchor similarity image (rotated rect lands exactly)',
  dragOut.fit.maxCorner < 0.2 && dragOut.fit.closure < 0.2, dragOut.fit);

// ---- (b) wheel: scale about the centre, the page canvas's own factor (307bb, verbatim)
const wheelBase = await page.evaluate(() => simFit(P.pairs).mpx);
await page.mouse.move(p0.x, p0.y);
await page.mouse.wheel(0, -100);
await sleep(400);
const wheelOut = await page.evaluate(() => ({
  a: P.anchor, fit: _fkvFitChecks(), hint: document.getElementById('fithint').textContent
}));
check('wheel: mpx scaled by exp(0.15) about the absorbed fit, centre and rotation held',
  Math.abs(wheelOut.a.mpx - wheelBase * Math.exp(0.15)) / wheelBase < 1e-3 && Math.abs(wheelOut.a.rot) < 0.01 &&
  Math.abs(wheelOut.a.lon - dragOut.a.lon) < 1e-6 && Math.abs(wheelOut.a.lat - dragOut.a.lat) < 1e-6,
  { got: wheelOut.a, want: wheelBase * Math.exp(0.15) });
check('wheel: fit agrees with the anchor, the corners still land exactly',
  wheelOut.fit.dmpx < 1e-3 && wheelOut.fit.drot < 0.01 && wheelOut.fit.maxCorner < 0.2 &&
  wheelOut.fit.closure < 0.2 && wheelOut.fit.maxResid < 2, wheelOut.fit);
check('wheel: the panel readout is live', wheelOut.hint.includes(wheelOut.a.mpx.toFixed(2)), wheelOut.hint);

// ---- (c) shift+wheel: turn it, 1 degree per 100-unit notch (307bb, verbatim)
await page.keyboard.down('Shift');
await page.mouse.wheel(0, +100);
await page.keyboard.up('Shift');
await sleep(400);
const turnOut = await page.evaluate(() => ({ a: P.anchor, fit: _fkvFitChecks() }));
check('shift+wheel: rotation advanced 1 degree (1 per 100-unit notch)',
  Math.abs(turnOut.a.rot - (wheelOut.a.rot + 1.0)) < 0.01, turnOut.a);
check('shift+wheel: scale held (the pre-turn absorb re-fit only rounds it)',
  Math.abs(turnOut.a.mpx - wheelOut.a.mpx) / wheelOut.a.mpx < 1e-3,
  { before: wheelOut.a.mpx, after: turnOut.a.mpx });
check('shift+wheel: the rotated fit-prev source still lands exactly (the parallelogram claim)',
  turnOut.fit.maxCorner < 0.2 && turnOut.fit.closure < 0.2 && turnOut.fit.maxResid < 2 &&
  turnOut.fit.dmpx < 1e-3 && turnOut.fit.drot < 0.01, turnOut.fit);
await page.screenshot({ path: outdir + '/3-gestured.png' });

// ---- (e) save from the placement alone
const anchorBeforeSave = await page.evaluate(() => P.anchor);
const pairsBefore = await page.evaluate(() => P.pairs.map(p => [p.u, p.v, p.lon, p.lat]));
const imgSize = await page.evaluate(() => [P.img.naturalWidth, P.img.naturalHeight]);
await page.click('#fsave', { timeout: 10000 });
const saveOut = await page.evaluate(async () => {
  // the page's own poll: it endFit's when its fetch finds the overlay (fit.at === its own at)
  const t0 = Date.now();
  while (Date.now() - t0 < 120000) {
    try { if (!P.active) return true; } catch {}
    await new Promise(r => setTimeout(r, 250));
  }
  return false;
});
check('save: the page closed the fit view (the overlay landed, the page endFit)', saveOut);

// ---- the one-site line's effects, read through the page on the site view (the page sits there
//      after endFit; the card is only in the home view, so it is checked after the #back click)
const effects = await page.evaluate(async ({ site, plan, tree, itemFile }) => {
  const docId = site + '.' + plan;
  const doc = JSON.parse(readFileSync(tree + '/data/db/platefits/' + docId + '.json', 'utf8'));
  const t0 = Date.now();
  let ok = false, state = {};
  while (Date.now() - t0 < 120000 && !ok) {
    try {
      const deps = await fetch('data/sites/' + site + '/depictions.json?t=' + Date.now()).then(r => r.json());
      const overlay = (deps.depictions || []).find(d => (d.fit || {}).doc === docId) || null;
      const sites = await fetch('data/sites.json?t=' + Date.now()).then(r => r.json());
      const entry = (Array.isArray(sites) ? sites : sites.sites).find(x => x.id === site) || {};
      const item = await fetch('data/review/' + itemFile + '?t=' + Date.now()).then(r => r.json());
      const review = await fetch('data/review.json?t=' + Date.now()).then(r => r.json());
      const lid = 'dep-' + site;
      const d = (S.dep[site] || []).find(x => x.file === S.depSel[site]);
      const want = d ? 'data/sites/' + site + '/' + (S.depMode === 'ink' && d.ink ? d.ink : d.file) : null;
      const mk = markers.find(k => k.id === site);
      const doneVal = FQ.done[site];
      state = {
        docAt: doc.at, docBy: doc.by,
        overlayFile: overlay && overlay.file, overlayInk: overlay && overlay.ink,
        overlayAt: overlay && overlay.fit && overlay.fit.at,
        depVis: map.getLayer(lid) ? map.getLayoutProperty(lid, 'visibility') : null,
        depSrc: map.getSource(lid) ? map.getSource(lid).url : null, want,
        depSel: S.depSel[site], depMode: S.depMode,
        drawings: entry.drawings, score: entry.score, oldest: entry.oldest, overlays: entry.overlays,
        markerClass: mk ? mk.el.className : null, tier: tierOf(entry),
        resolved: item.resolved || null,
        inOpen: (review.items || []).some(x => x.site === site),
        doneOk: doneVal !== undefined && !Number.isNaN(Date.parse(doneVal))
      };
      ok = !!overlay && state.overlayAt === doc.at && state.depSel === state.overlayFile &&
        state.depVis === 'visible' && state.depSrc === state.want && state.markerClass === 'marker ' + state.tier &&
        state.resolved && state.resolved.doc === docId && state.resolved.at === doc.at &&
        !state.inOpen && state.doneOk;
    } catch {}
    if (!ok) await new Promise(r => setTimeout(r, 1000));
  }
  return { ok, state };
}, { site, plan, tree, itemFile });
check('line effect (a): the overlay landed in the tree and the page shows its ink on the map',
  effects.ok && effects.state.depVis === 'visible' && !!effects.state.overlayInk &&
  effects.state.depSrc === 'data/sites/' + site + '/' + effects.state.overlayInk, effects.state);
check('line effect (b): the site square recolours to the new score\\'s tier',
  effects.ok && effects.state.markerClass === 'marker ' + effects.state.tier, effects.state);
check('line effect (c): the review item is resolved by the saved doc and the site left the open list',
  effects.ok && !!effects.state.resolved && !effects.state.inOpen, effects.state);
check('line effect (d): the card\\'s done map carries a parseable timestamp for the site',
  effects.ok && effects.state.doneOk, effects.state);
await page.screenshot({ path: outdir + '/4-saved.png' });

// ---- the card moves on: back to the home view (the card is only there)
await page.click('#back', { timeout: 20000 });
const cardPoll = (s) => page.evaluate(async (s) => {
  const t0 = Date.now();
  while (Date.now() - t0 < 20000) {
    const c = document.getElementById('fqcard');
    if (c) {
      const pend = (typeof fqPending === 'function') ? fqPending() : [];
      const next = pend.length ? { name: pend[0].name || pend[0].site, site: pend[0].site } : null;
      return { name: (c.querySelector('.fq-site b') || {}).textContent || null,
               text: c.textContent, next, n: pend.length };
    }
    await new Promise(r => setTimeout(r, 250));
  }
  return null;
}, s);
const card2 = await cardPoll(site);
check('after save: the card names the next pending entry, not the pick',
  !!card2 && !!card2.next && card2.name === card2.next.name && card2.next.site !== site &&
  !card2.text.includes(card2.expect ?? '') && card2.name !== (await page.evaluate(s =>
    (FQ.entries.find(x => x.site === s) || {}).name || s, site)),
  card2);

// ---- the reload: the fit loads back unchanged (same context: aw.depSel, aw.fitQueue.done
//      and aw.ground persist; the hash '#<site>' drove select() again)
await page.reload();
const boot2 = await page.evaluate(async (s) => {
  let ok = false;
  try {
    const t0 = Date.now();
    while (Date.now() - t0 < 60000) {
      if (S.ready && S.sites.length && S.sel === s) { ok = true; break; }
      await new Promise(r => setTimeout(r, 250));
    }
  } catch {}
  return ok;
}, site);
check('reload: the page booted straight onto the site view (the deep link)', boot2);
const reload = await page.evaluate(async ({ site, plan, wantScore, wantDrawings }) => {
  const docId = site + '.' + plan;
  const t0 = Date.now();
  let ok = false, state = {};
  while (Date.now() - t0 < 60000 && !ok) {
    try {
      const deps = await fetch('data/sites/' + site + '/depictions.json?t=' + Date.now()).then(r => r.json());
      const overlay = (deps.depictions || []).find(x => (x.fit || {}).doc === docId) || null;
      const lid = 'dep-' + site;
      const d = (S.dep[site] || []).find(x => x.file === S.depSel[site]);
      const want = d ? 'data/sites/' + site + '/' + (S.depMode === 'ink' && d.ink ? d.ink : d.file) : null;
      const mk = markers.find(k => k.id === site);
      const s = S.byId[site] || {};
      state = {
        sel: S.sel, ground: S.ground, depMode: S.depMode, plateMode: S.plateMode,
        depSel: S.depSel[site], overlayFile: overlay && overlay.file,
        depVis: map.getLayer(lid) ? map.getLayoutProperty(lid, 'visibility') : null,
        depSrc: map.getSource(lid) ? map.getSource(lid).url : null, want,
        markerClass: mk ? mk.el.className : null, tier: tierOf(s),
        drawings: s.drawings, score: s.score,
        doneOk: FQ.done[site] !== undefined && !Number.isNaN(Date.parse(FQ.done[site]))
      };
      ok = state.sel === site && state.ground === 'imagery' && state.depMode === 'ink' &&
        state.plateMode === 'ink' && state.overlayFile && state.depSel === state.overlayFile &&
        state.depVis === 'visible' && state.depSrc === state.want &&
        state.markerClass === 'marker ' + state.tier && state.doneOk &&
        state.drawings === wantDrawings && state.score === wantScore;
    } catch {}
    if (!ok) await new Promise(r => setTimeout(r, 500));
  }
  return { ok, state };
}, { site, plan, wantScore: effects.state.score, wantDrawings: effects.state.drawings });
check('reload: the saved fit loads back (the persisted selection is the overlay ink, the square ' +
      'and the done map are kept, the page contract ground/ink restored)',
  reload.ok, reload.state);
await sleep(5000); // the fly-to settles: the shot shows the overlay on the map
await page.screenshot({ path: outdir + '/5-reload.png' });
// back to the home view once more: the card still moved on
await page.click('#back', { timeout: 20000 });
const card3 = await cardPoll(site);
check('after reload: the card still names the next pending entry, not the pick',
  !!card3 && !!card3.next && card3.name === card3.next.name && card3.next.site !== site &&
  card3.name !== (await page.evaluate(s =>
    (FQ.entries.find(x => x.site === s) || {}).name || s, site)),
  card3);

const out = {
  boot, card1, seed,
  anchorBeforeSave, pairsBefore, imgSize,
  doc: (() => { try { return JSON.parse(readFileSync(tree + '/data/db/platefits/' + docId + '.json', 'utf8')); } catch { return null; } })(),
  effects: effects.state, card2, reload: reload.state, card3
};
console.log('[eval] ' + JSON.stringify(out));
for (const ln of lines) if (!ln.startsWith('[console')) console.log(ln);
check('no page errors in the run', !lines.some(ln => ln.startsWith('[pageerror')));
// Esri's own URLs are .../MapServer/tile/... (singular) - the '/tiles/' exclusion misses them
check('no network-level request failures outside the map tiles',
  !lines.some(ln => ln.startsWith('[reqfail') && !ln.includes('/tiles/') && !ln.includes('arcgisonline') && !ln.includes('MapServer/tile/')));
console.log(failures.length ? 'RESULT FAIL: ' + failures.join(' | ') : 'RESULT PASS');
await browser.close();
process.exit(failures.length ? 1 : 0);
"""


def _headless_or_skip():
    if not (os.path.exists(CHROME) and os.path.isdir(NODE_MODULES)):
        pytest.skip("headless Chrome is not installed on this machine (the recipe is in PITFALLS.md)")


@pytest.fixture(scope="module")
def owner_served(tmp_path_factory):
    """The real server on an ephemeral port over a FULL private copy of the tree (the one-site
    line's home: tools/fit/pipeline present, both picks' site dirs real copies, both book pages
    in the tree's own data/raw, every socket in the server process dead). ONE server for both
    runs: B's run sees A's tree state by design (pytest runs the tests in file order; both dirs
    are real copies, so A's writes stay in the tree).
    -> {"base", "tree", "out", "picks": {"A": {...}, "B": {...}}}"""
    _headless_or_skip()
    a, b = _picker()
    assert a and b, "no derived pick: need a bar-scale and a site-size-only line-eligible queue " \
                    "entry with a page-showable auto dep, no drawing dep and a following entry - vacuous"
    q = json.loads((ROOT / "web" / "data" / "fit_queue.json").read_text())
    items = _review_items()
    picks = {}
    for tag, t in (("A", a), ("B", b)):
        i, e, auto, rec = t
        site = e["site"]
        p, item = _item_of(ROOT, site)
        assert p is not None, "the pick has no review item"
        picks[tag] = {
            "site": site, "plan": e["best"]["plan"], "row": e["best"]["row"], "entry": e,
            "item": item, "itemFile": p.name, "depFile": auto["file"],
            "sitesBefore": dict(rec),
            "done": {x["site"]: AT for x in q["entries"][:i]},
            "scale_source": e["propose"]["scale_source"],
            "lidar_credit": (rec or {}).get("lidar_credit"),
        }
    assert picks["A"]["site"] != picks["B"]["site"]
    tree = tmp_path_factory.mktemp("awowner")
    copy_web(tree, real={picks["A"]["site"], picks["B"]["site"]})
    for tag in "AB":
        assert not (tree / "web" / "data" / "sites" / picks[tag]["site"]).is_symlink()
    for d in ("server", "tools", "fit", "pipeline"):
        shutil.copytree(str(ROOT / d), str(tree / d))

    def ignore(d, names):  # data/raw (book scans) and the gitignored elevation grids
        return [n for n in names if os.path.join(d, n) == str(ROOT / "data" / "raw")
                or n.endswith((".npy", ".npz"))]

    shutil.copytree(str(ROOT / "data"), str(tree / "data"), ignore=ignore)
    for tag in "AB":
        row = picks[tag]["row"]
        src = ROOT / "data" / "raw" / "books" / row["ia"] / "full" / row["file"]
        dst = tree / "data" / "raw" / "books" / row["ia"] / "full" / row["file"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), dst)
    picks["reviewBefore"] = {x["site"]: x for x in
                             json.loads((tree / "web" / "data" / "review.json").read_text())["items"]}
    proc = subprocess.Popen([sys.executable, "-c", GUARD, "server/serve.py", "--port", "0"],
                            cwd=str(tree), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = []

    def _reader():
        for line in proc.stdout:
            out.append(line.rstrip("\n"))

    threading.Thread(target=_reader, daemon=True).start()
    url = None
    deadline = time.time() + 90
    while time.time() < deadline and proc.poll() is None and not url:
        for line in list(out):
            m = re.match(r"Ancient Works on (\S+)", line)
            if m:
                url = m.group(1)
                break
        time.sleep(0.2)
    if not url:
        proc.kill()
        raise AssertionError("server did not report its address (startup: %r)" % out[-10:])
    yield {"base": url.rstrip("/"), "tree": Path(tree), "out": out, "picks": picks}
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def _write_surface(picks):
    """Every file a run could touch in the CHECKOUT (the shared store): every platefits doc and
    review item, the page data files, and every file under both picks' site dirs (they are
    symlinks into the store - hashing through them proves the store never moved)."""
    paths = list((ROOT / "data" / "db" / "platefits").glob("*.json")) + list((ROOT / "data" / "review").glob("*.json"))
    paths += [ROOT / "web" / "data" / "sites.json", ROOT / "web" / "data" / "review.json",
              ROOT / "web" / "data" / "fit_queue.json"]
    for tag in "AB":
        sd = ROOT / "web" / "data" / "sites" / picks[tag]["site"]
        paths += [p for p in sd.rglob("*") if p.is_file()]
    return {str(p): _h(p) for p in paths if p.is_file()}


def _run_one(fx, tag, tmp_path_factory):
    """One owner run on the fixture's shared private tree: the probe (the browser), then the
    Python-side checks read from the tree, then the revert proof and the screenshots."""
    base, tree, out = fx["base"], fx["tree"], fx["out"]
    p = fx["picks"][tag]
    site, plan, row = p["site"], p["plan"], p["row"]
    doc_id = f"{site}.{plan}"
    sd = tree / "web" / "data" / "sites" / site

    surface = _write_surface(fx["picks"])
    n0 = len(out)
    outdir = tmp_path_factory.mktemp(f"owner{tag}")
    (outdir / "owner_probe.mjs").write_text(PROBE, encoding="utf-8")
    proc = subprocess.run(["node", str(outdir / "owner_probe.mjs"), base, site, plan, str(tree),
                           str(outdir), json.dumps(p["done"]), p["itemFile"]],
                          cwd=str(ROOT), env=dict(os.environ, NODE_PATH=NODE_MODULES),
                          capture_output=True, encoding="utf-8", errors="replace", timeout=600)
    assert proc.returncode == 0 and "RESULT PASS" in proc.stdout, \
        (proc.returncode, proc.stdout[-4000:], proc.stderr[-2000:], out[-30:])
    runlog = out[n0:]
    assert not any("attempted a network connection" in ln for ln in runlog), runlog
    data = next(json.loads(ln[len("[eval]"):]) for ln in proc.stdout.splitlines() if ln.startswith("[eval]"))

    # 1. the saved doc (read from the tree's store): by hand, exactly the placed pairs
    doc = data["doc"]
    assert doc is not None, "the doc was not written to the tree's store"
    assert doc["by"] == "hand", doc.get("by")
    assert doc["site"] == site and doc["plan"] == plan
    assert doc["ia"] == row["ia"] and doc["file"] == row["file"]
    assert doc["model"] == "similarity" and doc["src"] == "book" and doc["url"] is None and doc["ref"] is None
    assert doc["size"] == data["imgSize"] == row["size"]
    mb, W, H = row.get("map_box"), row["size"][0], row["size"][1]
    want_crop = ([round(mb[0] * W), round(mb[1] * H), round(mb[2] * W), round(mb[3] * H)] if mb
                 else [0, 0, W, H])
    assert doc["crop"] == want_crop, (doc["crop"], want_crop)
    assert doc["pairs"] == data["pairsBefore"], "the doc pairs are not exactly the placed five"
    assert re.match(r"^2026-\d\d-\d\dT\d\d:\d\d:\d\d", doc["at"]), doc["at"]

    # 2. the doc's own fit agrees with the placed anchor (the page's simFit, stdlib)
    f = _simfit([{"u": q[0], "v": q[1], "lon": q[2], "lat": q[3]} for q in doc["pairs"]])
    anchor = data["anchorBeforeSave"]
    assert abs(f["mpx"] - anchor["mpx"]) < 1e-3, (f["mpx"], anchor["mpx"])
    assert abs(f["rot"] - anchor["rot"]) < 0.01, (f["rot"], anchor["rot"])
    assert max(f["resid"]) < 2, max(f["resid"])

    # 3. the overlay (the tree's depictions.json): the same similarity, as webp, with the
    #    hand-placed source line
    deps = json.loads((sd / "depictions.json").read_text())["depictions"]
    ov = next(d for d in deps if (d.get("fit") or {}).get("doc") == doc_id)
    assert ov["kind"] == "plan"
    assert ov["file"] == f"plan_{plan}.webp" and ov["ink"] == f"plan_{plan}_ink.webp"
    assert not sd.is_symlink(), "the pick's site dir in the tree is a symlink (the fixture must copy it)"
    for name in (ov["file"], ov["ink"]):
        fp = (sd / name).resolve()
        assert fp.is_file() and fp.is_relative_to(tree), name
    fit = ov["fit"]
    assert fit["at"] == doc["at"] and fit["pairs"] == 5 and fit["model"] == "similarity"
    assert len(fit["resid_m"]) == 5 and max(fit["resid_m"]) < 1
    max_px = int(re.search(r"^MAX_PX = (\d+)", (tree / "pipeline" / "plan_fit.py").read_text(), re.M).group(1))
    fs = data["imgSize"][0] / row["size"][0]
    fpx = min(1.0, max_px / max((doc["crop"][2] - doc["crop"][0]) * fs, (doc["crop"][3] - doc["crop"][1]) * fs))
    want_mpx = anchor["mpx"] * fs / fpx
    assert abs(fit["m_per_px"] - want_mpx) / want_mpx < 1e-3, (fit["m_per_px"], want_mpx)
    assert abs(fit["rot_deg"] - anchor["rot"]) < 0.01, (fit["rot_deg"], anchor["rot"])
    assert ov["year"] == int(re.search(r"(?<!\d)(1[2-9]\d\d)(?!\d)",
                                       (doc.get("book") or "") + " " + str(doc.get("label") or "")
                                       ).group(1))
    sys.path.insert(0, str(ROOT / "pipeline"))
    import plan_fit  # the checkout's own source-line writer: the same string the build writes
    m = math.ceil(max(f["resid"]))
    assert ov["source"] == plan_fit.source_line(doc, len(doc["pairs"]), m, "hand"), ov["source"]

    # 4. the site's marker fields in the tree's sites.json: recomputed build_site formula
    entry = next(x for x in json.loads((tree / "web" / "data" / "sites.json").read_text())["sites"]
                 if x["id"] == site)
    before = p["sitesBefore"]
    assert entry["drawings"] == before["drawings"] + 1, (entry["drawings"], before["drawings"])
    score, n_ov = _score_of_deps(deps)
    assert entry["score"] == score, (entry["score"], score)
    assert entry["overlays"] == n_ov, (entry["overlays"], n_ov)
    assert entry["oldest"] == min(x for x, _, _ in
                                  [(y, 0, 0) for y in
                                   [d["year"] for d in deps
                                    if d.get("year") and (d.get("kind") in DRAWING_KINDS or
                                                          d["year"] <= datetime.now(timezone.utc).year - MIN_AGE_YEARS)]])
    assert data["effects"]["markerClass"] == "marker " + _tier_of(entry["score"])
    assert data["reload"]["markerClass"] == "marker " + _tier_of(entry["score"])

    # 5. the review item (the tree): resolved by the saved doc
    it = json.loads((tree / "data" / "review" / p["itemFile"]).read_text())
    assert it["resolved"] == {"doc": doc_id, "at": doc["at"]}, it.get("resolved")

    # 6. the tree's review.json: this site left the open list (B's run leaves A's behind)
    open_sites = {x["site"] for x in json.loads((tree / "web" / "data" / "review.json").read_text())["items"]}
    gone = {p["site"]} if tag == "A" else {p["site"], fx["picks"]["A"]["site"]}
    want = set(fx["picks"]["reviewBefore"]) - gone
    assert open_sites == want, (sorted(open_sites ^ want))

    # 7. the server log: the one-site line finished, no matcher, no batch, nothing failed
    assert any(ln.strip() == f"one-site line for {site}: finished (exit 0)" for ln in runlog), runlog
    assert not any(ln.strip().startswith(f"one-site line for {site} failed") for ln in runlog), runlog
    assert not any("matcher" in ln or "sent to the review queue" in ln or
                   "no model answer" in ln for ln in runlog), runlog

    # 8. the reload state the probe checked in the browser, cross-checked against the tree
    assert data["reload"]["sel"] == site
    assert data["reload"]["ground"] == "imagery" and data["reload"]["depMode"] == "ink" \
        and data["reload"]["plateMode"] == "ink"
    assert data["reload"]["depSel"] == ov["file"]
    assert data["reload"]["depVis"] == "visible" and data["reload"]["depSrc"] == f"data/sites/{site}/{ov['ink']}"
    assert data["reload"]["drawings"] == entry["drawings"] and data["reload"]["score"] == entry["score"]

    # the checkout (the shared store) is byte-identical around the run
    assert _write_surface(fx["picks"]) == surface, "the run wrote into the checkout's shared store"

    # the owner's five views of this run, kept with the docs
    docs = ROOT / "docs" / "site_flow"
    for name in ("1-card", "2-placed", "3-gestured", "4-saved", "5-reload"):
        shutil.copy2(outdir / f"{name}.png", docs / f"307d_{tag}_{name}.png")
    return data


def test_owner_save_bar_scale(owner_served, tmp_path_factory):
    """A: the owner's flow on the derived BAR-SCALE queue site (a recorded scale bar sets the
    starting scale): card -> place on the works -> drag -> wheel -> shift+wheel -> save -> the
    line's four effects -> the fit loads back unchanged on reload; the checkout's shared store
    is byte-identical around the run and the five views land in docs/site_flow/."""
    _run_one(owner_served, "A", tmp_path_factory)


def test_owner_save_site_size_fallback(owner_served, tmp_path_factory):
    """B: the same on the derived SITE-SIZE-ONLY queue site (the fallback scale: no recorded
    bar, the site's known size over the recorded page size). Its run sees A's tree state (the
    shared private tree): B's line must not rewrite A's already-resolved item file, and the
    checkout's shared store is still byte-identical when B finishes."""
    data = _run_one(owner_served, "B", tmp_path_factory)
    a = owner_served["picks"]["A"]
    assert _h(owner_served["tree"] / "data" / "review" / a["itemFile"]) == _h(a["itemBytes"]), \
        "B's run rewrote A's already-resolved item file"
