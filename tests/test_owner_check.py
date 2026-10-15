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
platefits doc, every review item, sites.json, review.json, fit_queue.json, every file under
both picks' site dirs, and the ten committed docs/site_flow/307d_*.png, hashed through the
checkout's own symlinks into the store). The golden hand-fit hash check
(tests/golden/hand_fit_docs.sha256) and test_fit_provenance run on the same checkout and
stay green for the same reason.

The ten docs/site_flow/307d_*.png are a PINNED snapshot committed in the repo: an ordinary
run never touches them (they enter the write-surface proof above, which proves an unflagged
run left them byte-identical), and they are re-rendered from a run only under the explicit
env var AW_OWNER_REFRESH=1, named here and in the test docstrings. The captures themselves
are taken settled (242 family: 814 the settle, 812 the in-run double shot, 813 this regime):
the served private tree runs the page with the owner-flow camera transitions zeroed (the
4.5 s site flyTo, the 900 ms fit bounds, the pane open/close easeTos), and before every quad
read and every shot the probe waits on the map's idle flag - maplibre 5.6.0 fires `idle`
when the camera is at rest and no frame is pending, and its render loop is event-driven,
so the flag stays true until the next change (verified 2026-10-15 on this build) - and each
view is then shot twice in a row: the two shots must differ by <0.5% of pixels at threshold
32, so a mid-transition regression fails the test instead of dirtying the PNGs (measured
2026-10-14: without the settle, same-tree runs an hour apart differed 28.6-33.6% on the four
saved/reload views while card/placed/gestured stayed at 0-1.25% encoding noise).
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

CHROME = os.environ.get("AW_CHROME", "/opt/google/chrome/chrome")
NODE_MODULES = os.environ.get("AW_NODE_MODULES", "/home/agent/tools/shot/node_modules")
AT = "2026-10-12T00:00:00.000Z"  # the done-map timestamp 307bb's card runs seed with

# The page's own filter and default pick (web/index.html): surveys only at 150 years or older,
# then the auto depiction is the first drawing or the LAST map.
SURVEY_KINDS = frozenset({"map", "aerial", "topo"})
DRAWING_KINDS = frozenset({"plan", "drawing", "view"})
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
        # [] = line-eligible with NO uncovered rows: the no-batch path is the only path
        if _line_eligible(e, items.get(e["site"])) != []:
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
    """The page's tierOf (web/index.html: TIERS.find(t => (s.score || 0) >= t[0]) || [0, 'plain'])[1]) -
    note the find yields the [threshold, tier] pair, so the tier is the element, never an index into it."""
    return next((t for th, t in TIERS if (score or 0) >= th), "plain")


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
    return {"mpx": math.hypot(a0, a1) * k, "rot": math.degrees(math.atan2(a1, a0)), "resid": resid, "at": at}


def _unmerc(x, y):
    """Web Mercator metres -> (lon, lat) degrees (the inverse of _merc)."""
    R = 6378137.0
    return math.degrees(x / R), math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2)


def _shot_diff(p1, p2, thr=32):
    """812: the fraction of pixels differing by >thr on any channel between two same-size
    shots. The in-run double shots of a settled view must be near-identical; PIL (pinned in
    requirements.in) makes the compare C-speed over the 1280x820 frames."""
    from PIL import Image, ImageChops
    a, b = Image.open(p1).convert("RGB"), Image.open(p2).convert("RGB")
    if a.size != b.size:
        raise AssertionError(f"double-shot sizes differ: {a.size} vs {b.size}")
    d = ImageChops.difference(a, b).split()
    mask = d[0].point(lambda v: 255 if v > thr else 0)
    for ch in d[1:]:
        mask = ImageChops.lighter(mask, ch.point(lambda v: 255 if v > thr else 0))
    return mask.histogram()[255] / (a.size[0] * a.size[1])


PROBE = r"""// node owner_probe.mjs <base_url> <site> <plan> <tree> <out_dir> <done_json> <item_file>
// The owner's check (task 307d), end to end in headless Chrome on the served private tree, reading
// only what the owner sees or gets (rewritten 2026-10-13, the owner's rule "no unit tests, only end
// to end"): the page's DOM and pixels, where the drawing's corner handles are on screen, the map's
// view (where a ground point is, which file a layer shows) and the files the server serves. Never
// the page's own variables. The card names the pick -> Place puts the drawing on the works under
// the toolbar -> one drag on the drawing, toolbar scale and turn -> Save on the toolbar -> the
// overlay is on the map where the drawing was placed, the site's square takes its new tier, the
// site leaves the open review list, the card moves on -> a reload shows the fit back. Prints one
// [eval] line, then RESULT PASS/FAIL; exit 0/1.
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
const readJson = p => { try { return JSON.parse(readFileSync(p, 'utf8')); } catch { return null; } };
const served = async path => (await fetch(url.replace(/\/$/, '') + '/' + path + '?t=' + Date.now())).json();
// 814: wait for the served tree's settle flag. Its camera transitions run at zero duration
// (the fixture zeros them in the served copy) and the maplibre 5.6.0 `idle` event means the
camera is at rest and no frame is pending (no tiles or overlay arriving), so a screenshot
taken while the flag is false can land mid-transition (measured 2026-10-14: 28.6-33.6% of
pixels on the saved/reload views, same tree, runs an hour apart). Bounded: a timeout
proceeds - it must never hang the test - and logs for the failure forensics.
const settle = async label => {
  const t0 = Date.now();
  try {
    await page.waitForFunction(() => !!(window.__awSettle && window.__awSettle.idle), null, { timeout: 30000 });
    console.log('[settle] ' + label + ' after ' + (Date.now() - t0) + ' ms');
  } catch {
    console.log('[settle] ' + label + ' TIMED OUT after ' + (Date.now() - t0) + ' ms; proceeding');
  }
};
// 814 + 812: capture a view only once settled, then a second time at once: the two shots
// must differ by <0.5% of pixels at threshold 32 (the Python side compares them), so a
// mid-transition regression fails the test instead of dirtying the docs PNGs.
const shot = async name => {
  await settle(name);
  await page.screenshot({ path: outdir + '/' + name + '.png' });
  await page.screenshot({ path: outdir + '/' + name + 'b.png' });
};
// the marker tiers as the page draws them (web/index.html tierOf): score -> class
const TIERS = [[2.5, 't4'], [1.6, 't3'], [1.2, 't2'], [0.01, 't1']];
const tierOf = s => { for (const [lo, t] of TIERS) if ((s || 0) >= lo) return t; return 'plain'; };

const queue = await served('data/fit_queue.json');
const entries = queue.entries;
const pick = entries.find(e => e.site === site);
const propC = pick.propose.pairs[pick.propose.pairs.length - 1];  // the queue's starting centre [u, v, lon, lat]
const pending = entries.filter(e => !(e.site in doneMap));
const nextAfter = pending[pending.findIndex(e => e.site === site) + 1];

const browser = await chromium.launch({ channel: 'chrome', headless: true,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 820 }, colorScheme: 'light' });
const lines = [];
page.on('pageerror', e => lines.push('[pageerror] ' + e.message));
page.on('requestfailed', r => lines.push('[reqfail] ' + r.url() + ' ' + (r.failure() && r.failure().errorText)));
// seed the card past the earlier entries only once: the reload must keep what the page itself stored
await page.addInitScript(({ done }) => {
  if (localStorage.getItem('aw.fitQueue.done')) return;
  try { localStorage.setItem('aw.fitQueue.done', JSON.stringify(done)); } catch {}
}, { done: doneMap });
await page.goto(url);
await page.waitForSelector('#fqcard #fqplace', { timeout: 60000 });

const cardText = () => page.evaluate(() => { const c = document.getElementById('fqcard');
  return c ? { name: (c.querySelector('.fq-site b') || {}).textContent || null, text: c.textContent } : null; });
const card1 = await cardText();
check('the card names the pick and its best row', !!card1 && card1.name === (pick.name || pick.site) &&
  card1.text.includes(pick.best.row.title || pick.best.row.id), { card1, want: pick.name });
await shot('1-card');

// ---- place
const quad = () => page.evaluate(() => [...document.querySelectorAll('.gpin.fk-handle')]
  .filter(el => el.style.display !== 'none').map(el => { const r = el.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }));
const inside = (q, x, y) => { let c = false; for (let i = 0, j = q.length - 1; i < q.length; j = i++) {
  const a = q[i], b = q[j]; if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) c = !c; } return c; };
const groundOnScreen = ll => page.evaluate(ll => { const r = map.getCanvas().getBoundingClientRect(), q = map.project(ll); return [q.x + r.left, q.y + r.top]; }, ll);
const layer = () => page.evaluate(s => ({ vis: map.getLayer('dep-' + s) ? map.getLayoutProperty('dep-' + s, 'visibility') : null,
  src: map.getSource('dep-' + s) ? map.getSource('dep-' + s).url : null }), site);
const before = await layer();
await page.click('#fqplace');
await page.waitForSelector('#fkbar', { timeout: 60000 });
await page.waitForFunction(() => [...document.querySelectorAll('.gpin.fk-handle')].filter(el => el.style.display !== 'none').length === 4, null, { timeout: 30000 });
await sleep(2500);
await settle('q0');
const q0 = await quad(), c0 = await groundOnScreen([propC[2], propC[3]]);
const sites0 = await served('data/sites.json');
const entry0 = (sites0.sites || sites0).find(x => x.id === site) || {};
check('place: the drawing opens on the works under the toolbar', q0.length === 4 && inside(q0, ...c0), { q0, c0 });
check('place: the earlier overlay is hidden while placing', !before.vis || (await layer()).vis === 'none', before);
check('place: the site\'s own ground is pressed (LiDAR relief unless the site has none)',
  await page.evaluate(id => document.getElementById(id) ? document.getElementById(id).getAttribute('aria-pressed') === 'true' : true,
    entry0.lidar === false ? 'g-imagery' : 'g-relief'));
await shot('2-placed');

// ---- move it the way the owner does: a drag on it, the toolbar's scale and turn
const mid = [q0.reduce((s, p) => s + p[0], 0) / 4, q0.reduce((s, p) => s + p[1], 0) / 4];
await page.mouse.move(...mid); await page.mouse.down(); await page.mouse.move(mid[0] + 30, mid[1] + 20, { steps: 6 }); await page.mouse.up();
await sleep(400);
await settle('q1');
const q1 = await quad();
check('drag on the drawing moves it by the pointer', q1.every((p, i) => Math.hypot(p[0] - q0[i][0] - 30, p[1] - q0[i][1] - 20) < 2.5), { q0, q1 });
await page.click('#fkbar [data-a="s+"]'); await page.click('#fkbar [data-a="r+"]'); await sleep(500);
await settle('q2');
const q2 = await quad();
const edge = q => Math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]);
check('toolbar scale and turn change the drawing on screen', Math.abs(edge(q2) / edge(q1) - 1.05) < 0.01, { e1: edge(q1), e2: edge(q2) });
await shot('3-gestured');

// ---- save from the toolbar: where the corners sit now is what must land
const placedLL = await page.evaluate(q => { const r = map.getCanvas().getBoundingClientRect();
  return q.map(([x, y]) => { const u = map.unproject([x - r.left, y - r.top]); return [u.lng, u.lat]; }); }, q2);
const mpp = await page.evaluate(() => 156543.03392 * Math.cos(map.getCenter().lat * Math.PI / 180) / 2 ** map.getZoom());
await page.click('#fkbar [data-a="save"]');
await page.waitForFunction(() => !document.getElementById('fkbar'), null, { timeout: 120000 }).catch(() => {});
check('save: the toolbar closes once the overlay is on the map', await page.evaluate(() => !document.getElementById('fkbar')));
const doc = readJson(tree + '/data/db/platefits/' + docId + '.json');

// the effects, polled through what the server serves and what the page shows
let effects = null;
for (let i = 0; i < 120; i++) {
  const deps = await served('data/sites/' + site + '/depictions.json');
  const ov = (deps.depictions || []).find(d => (d.fit || {}).doc === docId) || null;
  const sites = await served('data/sites.json');
  const entry = (sites.sites || sites).find(x => x.id === site) || {};
  const review = await served('data/review.json');
  const shown = await layer();
  const markerClass = await page.evaluate(n => { const el = [...document.querySelectorAll('button.marker')].find(b => b.getAttribute('aria-label') === 'Open ' + n); return el ? el.className : null; }, entry.name || pick.name);
  effects = { overlayFile: ov && ov.file, overlayInk: ov && ov.ink, overlayAt: ov && ov.fit && ov.fit.at, corners: ov && ov.corners,
              depVis: shown.vis, depSrc: shown.src, markerClass, tier: tierOf(entry.score), drawings: entry.drawings, score: entry.score,
              inOpen: (review.items || []).some(x => x.site === site) };
  if (ov && doc && effects.overlayAt === doc.at && shown.vis === 'visible' && !effects.inOpen &&
      (markerClass || '').split(/\s+/).includes(effects.tier)) break;
  await sleep(1000);
}
check('line effect (a): the overlay is made and the map shows its ink',
  !!effects.overlayInk && effects.depVis === 'visible' && effects.depSrc === 'data/sites/' + site + '/' + effects.overlayInk, effects);
if (effects.corners) {
  const k = Math.cos(placedLL[0][1] * Math.PI / 180), M = ll => [ll[0] * 111319.49 * k, ll[1] * 111319.49];
  const err = effects.corners.map((c, i) => Math.hypot(M(c)[0] - M(placedLL[i])[0], M(c)[1] - M(placedLL[i])[1]));
  check('line effect (a): the overlay\'s corners are where the drawing was placed (3 screen px)', Math.max(...err) <= 3 * mpp + 0.5, { err, mpp });
}
check('line effect (b): the site\'s square takes its new score\'s tier',
  (effects.markerClass || '').split(/\s+/).includes('marker') && (effects.markerClass || '').split(/\s+/).includes(effects.tier), effects);
check('line effect (c): the site left the open review list', effects.inOpen === false, effects);
await shot('4-saved');

// ---- the card moves on
await page.click('#back', { timeout: 20000 });
await page.waitForSelector('#fqcard', { timeout: 20000 }).catch(() => {});
const card2 = await cardText();
check('after save: the card names the next pending entry, not the pick',
  !!card2 && !!nextAfter && card2.name === (nextAfter.name || nextAfter.site), { card2, next: nextAfter && nextAfter.name });

// ---- reload on the site: the fit comes back as the owner left it
// a real reload, deep-linked to the site (a hash change alone does not reload the page)
await page.evaluate(s => { location.hash = s; }, site);
await page.reload();
await page.waitForSelector('#g-imagery', { timeout: 60000 });
let reload = null;
for (let i = 0; i < 60; i++) {
  const shown = await layer();
  reload = await page.evaluate(() => ({
    title: (document.querySelector('#body h2.site-title') || {}).textContent || null,
    aerial: (document.getElementById('g-imagery') || {}).getAttribute && document.getElementById('g-imagery').getAttribute('aria-pressed') === 'true',
    ink: (document.getElementById('d-ink') || {}).getAttribute && document.getElementById('d-ink').getAttribute('aria-pressed') === 'true',
    selected: ([...document.querySelectorAll('#body [data-dep][aria-pressed="true"]')][0] || {}).dataset || null,
  }));
  reload.depVis = shown.vis; reload.depSrc = shown.src;
  reload.markerClass = await page.evaluate(n => { const el = [...document.querySelectorAll('button.marker')].find(b => b.getAttribute('aria-label') === 'Open ' + n); return el ? el.className : null; }, pick.name);
  reload.selectedDep = reload.selected ? reload.selected.dep : null; delete reload.selected;
  if (reload.depVis === 'visible' && reload.selectedDep === effects.overlayFile) break;
  await sleep(500);
}
check('reload: the site opens with the saved drawing selected and on the map, in ink, on the aerial photograph',
  reload.selectedDep === effects.overlayFile && reload.depVis === 'visible' && reload.depSrc === 'data/sites/' + site + '/' + effects.overlayInk &&
  reload.aerial && reload.ink, reload);
await sleep(3000);
await shot('5-reload');
await page.click('#back', { timeout: 20000 });
await page.waitForSelector('#fqcard', { timeout: 20000 }).catch(() => {});
const card3 = await cardText();
check('after reload: the card still names the next pending entry', !!card3 && !!nextAfter && card3.name === (nextAfter.name || nextAfter.site), card3);

console.log('[eval] ' + JSON.stringify({ card1, placedLL, mpp, doc, effects, card2, reload, card3 }));
for (const ln of lines) console.log(ln);
check('no page errors in the run', !lines.some(ln => ln.startsWith('[pageerror')));
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

    # 814 (the 242 family): the served tree is a private copy, and it runs the page with the
    # owner flow's camera transitions zeroed (the site flyTo, the fit bounds, the pane
    # open/close easeTos): the view reaches its final centre/zoom at once instead of after
    # the 4.5 s / 900 ms animations, so no capture can land mid-transition (measured:
    # the probe's fixed sleeps landed inside the flyTo, and on the globe projection the
    # camera kept moving ~3 s past the nominal transition end). The on-disk web/ is
    # untouched; a page edit that breaks an anchor fails loudly here.
    idx = tree / "web" / "index.html"
    html = idx.read_text(encoding="utf-8")
    for old, new in (
        ("duration: 4500, essential: true, padding: pad",
         "duration: 0, essential: true, padding: pad"),
        ("padding: { left: 390, top: 20, right: 20, bottom: 20 }, duration: 900",
         "padding: { left: 390, top: 20, right: 20, bottom: 20 }, duration: 0"),
        ("padding: { left: right + 10, top: 20, right: 20, bottom: 20 }, duration: 900",
         "padding: { left: right + 10, top: 20, right: 20, bottom: 20 }, duration: 0"),
    ):
        assert html.count(old) == 1, (old, html.count(old))
        html = html.replace(old, new)
    # the map's idle flag (maplibre 5.6.0: `idle` fires when the camera is at rest and no
    # frame is pending; the render loop is event-driven, so it stays quiet until the next
    # change - verified 2026-10-15 on this build). The probe's captures wait on it.
    anchor = "map.once('load', () => { S.mapLoaded = true; });"
    assert html.count(anchor) == 1, html.count(anchor)
    html = html.replace(anchor,
                        "window.__awSettle = { idle: false };\n"
                        "map.on('render', () => { window.__awSettle.idle = false; });\n"
                        "map.on('idle', () => { window.__awSettle.idle = true; });\n"
                        + anchor)
    idx.write_text(html, encoding="utf-8")
    fk = tree / "web" / "fitkit.js"
    fitkit = fk.read_text(encoding="utf-8")
    old = "duration: 900, essential: true"
    assert fitkit.count(old) == 1, (old, fitkit.count(old))
    fk.write_text(fitkit.replace(old, "duration: 0, essential: true"), encoding="utf-8")

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
    # 813: the ten committed docs/site_flow/307d_*.png - the pinned snapshot an unflagged
    # run must leave byte-identical
    paths += sorted((ROOT / "docs" / "site_flow").glob("307d_*.png"))
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
    (outdir / "owner_probe.log").write_text(proc.stdout + "\n=== stderr ===\n" + proc.stderr,
                                            encoding="utf-8")  # survives the failure: the [eval] dump and RESULT line
    assert proc.returncode == 0 and "RESULT PASS" in proc.stdout, \
        (proc.returncode, proc.stdout[-4000:], proc.stderr[-2000:], out[-30:])
    data = next(json.loads(ln[len("[eval]"):]) for ln in proc.stdout.splitlines() if ln.startswith("[eval]"))
    # the line runs in the server's worker thread, after the page already saw the overlay: wait
    # for its finished report before slicing runlog, so runlog holds the run's complete output
    deadline = time.time() + 30
    while time.time() < deadline and not any(ln.strip() == f"one-site line for {site}: finished (exit 0)"
                                             for ln in out):
        time.sleep(0.2)
    runlog = out[n0:]
    (outdir / "server_runlog.log").write_text("\n".join(runlog) + "\n", encoding="utf-8")  # survives a failure: check 7's exact-match asserts

    # 1. the saved doc (read from the tree's store): by hand, exactly the placed pairs
    doc = data["doc"]
    assert doc is not None, "the doc was not written to the tree's store"
    assert doc["by"] == "hand", doc.get("by")
    assert doc["site"] == site and doc["plan"] == plan
    assert doc["ia"] == row["ia"] and doc["file"] == row["file"]
    assert doc["model"] == "similarity" and doc["src"] == "book" and doc["url"] is None and doc["ref"] is None
    for k in ("label", "title", "book", "cite"):  # saveFit copies them verbatim from the row
        assert doc[k] == row[k], (doc.get(k), row.get(k))
    assert doc["size"] == row["size"]
    mb, W, H = row.get("map_box"), row["size"][0], row["size"][1]
    want_crop = ([round(mb[0] * W), round(mb[1] * H), round(mb[2] * W), round(mb[3] * H)] if mb
                 else [0, 0, W, H])
    assert doc["crop"] == want_crop, (doc["crop"], want_crop)
    assert re.match(r"^2026-\d\d-\d\dT\d\d:\d\d:\d\d", doc["at"]), doc["at"]

    # 2. the doc's own fit puts the drawing's corners where the owner saw them at Save (3 screen px)
    f = _simfit([{"u": q[0], "v": q[1], "lon": q[2], "lat": q[3]} for q in doc["pairs"]])
    assert max(f["resid"]) < 2, max(f["resid"])
    lat0 = data["placedLL"][0][1]
    kx = 111319.49 * math.cos(math.radians(lat0))
    x0, y0, x1, y1 = doc["crop"]
    for (u, v), ll in zip([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], data["placedLL"]):
        mx, my = f["at"](u, v)
        lon, lat = _unmerc(mx, my)
        err = math.hypot((lon - ll[0]) * kx, (lat - ll[1]) * 111319.49)
        assert err <= 3 * data["mpp"] + 0.5, (err, data["mpp"])

    # 3. the overlay (the tree's depictions.json): the same similarity, as webp, with the
    #    hand-placed source line
    deps = json.loads((sd / "depictions.json").read_text())["depictions"]
    ov = next(d for d in deps if (d.get("fit") or {}).get("doc") == doc_id)
    assert ov["kind"] == "plan"
    assert ov["file"] == f"plan_{plan}.webp" and ov["ink"] == f"plan_{plan}_ink.webp"
    assert ov["label"] == f"{row['book']}: {row['title'] or row['label'] or 'site plan'}", ov["label"]
    assert not sd.is_symlink(), "the pick's site dir in the tree is a symlink (the fixture must copy it)"
    for name in (ov["file"], ov["ink"]):
        fp = (sd / name).resolve()
        assert fp.is_file() and fp.is_relative_to(tree), name
    fit = ov["fit"]
    assert fit["at"] == doc["at"] and fit["pairs"] == 5 and fit["model"] == "similarity"
    assert len(fit["resid_m"]) == 5 and max(fit["resid_m"]) < 1
    assert ov["year"] == int(re.search(r"(?<!\d)(1[2-9]\d\d)(?!\d)",
                                       (doc.get("book") or "") + " " + str(doc.get("label") or "")
                                       ).group(1))
    sys.path.insert(0, str(ROOT / "pipeline"))
    import plan_fit  # the checkout's own source-line writer: the same string the build writes
    m = math.ceil(max(f["resid"]))
    assert ov["source"] == plan_fit.source_line(doc, len(doc["pairs"]), m, "hand"), ov["source"]

    # 4. the site's marker fields in the tree's sites.json: exactly what build_site's own marks()
    #    recomputes from the tree's depictions (the line called set_drawings -> marks on this very
    #    tree). The real functions, not a port: the old port assumed the counted set and it was the
    #    source of the only remaining failure (session 249). Every assert below carries the full diag
    #    (the entry, the recomputation, every depiction it saw, the page's marker classes), so a
    #    failure names its own cause instead of dying with a bare AssertionError.
    entry = next(x for x in json.loads((tree / "web" / "data" / "sites.json").read_text())["sites"]
                 if x["id"] == site)
    before = p["sitesBefore"]
    sys.path.insert(0, str(ROOT / "pipeline"))
    import build_site  # the line's own writer of these fields (pipeline/ imports numpy: .venv)
    exp_ovs = build_site.overlays(site, entry.get("plate"), str(tree))
    exp = {
        "drawings": build_site.drawings(site, entry.get("plate"), str(tree)),
        "score": build_site.score(exp_ovs),
        "oldest": min((y for y, _, _ in exp_ovs), default=None),
        "overlays": len(exp_ovs),
    }
    diag = {
        "entry": {k: entry.get(k) for k in ("drawings", "score", "oldest", "overlays")},
        "expected": exp, "ovs": exp_ovs, "plate": entry.get("plate"), "before": before,
        "deps": [(d.get("kind"), d.get("year"), d.get("file"), d.get("label"),
                  (d.get("fit") or {}).get("doc"), (d.get("fit") or {}).get("resid_m")) for d in deps],
        "effectsClass": data["effects"].get("markerClass"), "reloadClass": data["reload"].get("markerClass"),
        "tier": _tier_of(entry["score"]),
    }
    assert entry["drawings"] == before["drawings"] + 1 == exp["drawings"], diag
    assert entry["score"] == exp["score"], diag
    assert entry["overlays"] == exp["overlays"], diag
    assert entry["oldest"] == exp["oldest"], diag
    t = _tier_of(entry["score"])
    # the page sets 'marker <tier>' on the marker element, but MapLibre's own constructor adds
    # maplibregl-marker / maplibregl-marker-anchor-* to elements it owns, so class membership, never full equality
    assert "marker" in (data["effects"]["markerClass"] or "").split() and t in (data["effects"]["markerClass"] or "").split(), diag
    assert "marker" in (data["reload"]["markerClass"] or "").split() and t in (data["reload"]["markerClass"] or "").split(), diag

    # 5. the review item (the tree): resolved by the saved doc
    it = json.loads((tree / "data" / "review" / p["itemFile"]).read_text())
    assert it["resolved"] == {"doc": doc_id, "at": doc["at"]}, it.get("resolved")

    # 6. the tree's review.json: this site left the open list (B's run leaves A's behind)
    open_sites = {x["site"] for x in json.loads((tree / "web" / "data" / "review.json").read_text())["items"]}
    gone = {p["site"]} if tag == "A" else {p["site"], fx["picks"]["A"]["site"]}
    want = set(fx["picks"]["reviewBefore"]) - gone
    assert open_sites == want, (sorted(open_sites ^ want))

    # 7. the server log: the line's report and the line's own prints, exactly. The no-batch line
    #    prints on every run: every candidate is the saved doc or an item candidate, so the
    #    matcher (unreachable - sockets dead) is never called and the batch never runs.
    #    _summary's per-picture lines are two-space indented (not 'fit  ' lines) and may say
    #    'sent to the review queue' for the unfitted candidates - that is the line's own record.
    #    The finished reports are filtered by their own shape, never by the phrase: the line's own
    #    header (site_done: 'site <sid>: the one-site line (fit -> sync -> entry -> review)') also
    #    contains the phrase and would join an in-substring filter.
    line_lines = [ln for ln in runlog if ln.startswith("  one-site line for ")]
    assert line_lines == [f"  one-site line for {site}: finished (exit 0)"], line_lines
    rows = _rows_naming(tree, site)
    doc_plans = {json.loads(pth.read_text()).get("plan") for pth
                 in (tree / "data" / "db" / "platefits").glob("*.json") if pth.name.startswith(site + ".")}
    n_doc = sum(1 for r in rows if r["id"] in doc_plans)
    want_fit = [f"fit  {len(rows)} candidate picture(s): {n_doc} fitted (doc), "
                f"{len(rows) - n_doc} in the review item -> no batch run needed"]
    fit_lines = [ln for ln in runlog if ln.startswith("fit  ")]
    assert fit_lines == want_fit, fit_lines
    assert not any("matcher" in ln for ln in runlog), runlog
    assert not any("attempted a network connection" in ln for ln in runlog), runlog
    assert not any(ln.startswith("sync ") and ("refused" in ln or "FAILED" in ln
                  or "sent to the review queue" in ln) for ln in runlog), runlog

    # 8. the reload, as the page showed it, cross-checked against the tree
    assert data["reload"]["selectedDep"] == ov["file"]
    assert data["reload"]["aerial"] is True and data["reload"]["ink"] is True
    assert data["reload"]["depVis"] == "visible" and data["reload"]["depSrc"] == f"data/sites/{site}/{ov['ink']}"
    assert data["effects"]["drawings"] == entry["drawings"] and data["effects"]["score"] == entry["score"]

    # the checkout (the shared store) is byte-identical around the run - the ten committed
    # docs/site_flow/307d_*.png included (they are in _write_surface)
    assert _write_surface(fx["picks"]) == surface, "the run wrote into the checkout's shared store"

    # 812: the in-run double shot proves the view was settled when the primary shot landed -
    # a mid-transition regression fails here instead of dirtying the docs PNGs
    for name in ("1-card", "2-placed", "3-gestured", "4-saved", "5-reload"):
        frac = _shot_diff(outdir / f"{name}.png", outdir / f"{name}b.png")
        assert frac < 0.005, (f"{tag} {name}: not settled at shot time "
                              f"({frac:.2%} of pixels differ between the in-run shots)")

    # 813: the docs' ten PNGs are the pinned snapshot - an unflagged run leaves them
    # byte-identical (the write-surface assert above), AW_OWNER_REFRESH=1 re-renders them
    if os.environ.get("AW_OWNER_REFRESH"):
        docs = ROOT / "docs" / "site_flow"
        for name in ("1-card", "2-placed", "3-gestured", "4-saved", "5-reload"):
            shutil.copy2(outdir / f"{name}.png", docs / f"307d_{tag}_{name}.png")
    if tag == "A":
        # B's run must not rewrite A's already-resolved item file (write-once): record the bytes
        fx["picks"]["A"]["itemBytes"] = _h(tree / "data" / "review" / p["itemFile"])
    return data


def test_owner_save_bar_scale(owner_served, tmp_path_factory):
    """A: the owner's flow on the derived BAR-SCALE queue site (a recorded scale bar sets the
    starting scale): card -> place on the works -> drag -> wheel -> shift+wheel -> save -> the
    line's four effects -> the fit loads back unchanged on reload; the checkout's shared store
    (the ten pinned docs/site_flow/307d_*.png included) is byte-identical around the run, and
    an unflagged run never touches that snapshot - it is re-rendered only under
    AW_OWNER_REFRESH=1 (the module docstring names the flag)."""
    _run_one(owner_served, "A", tmp_path_factory)


def test_owner_save_site_size_fallback(owner_served, tmp_path_factory):
    """B: the same on the derived SITE-SIZE-ONLY queue site (the fallback scale: no recorded
    bar, the site's known size over the recorded page size). Its run sees A's tree state (the
    shared private tree): B's line must not rewrite A's already-resolved item file, and the
    checkout's shared store (the pinned docs/site_flow/307d_*.png included) is still
    byte-identical when B finishes."""
    data = _run_one(owner_served, "B", tmp_path_factory)
    a = owner_served["picks"]["A"]
    assert a.get("itemBytes"), "test A did not run first (the write-once check records A's item bytes)"
    assert _h(owner_served["tree"] / "data" / "review" / a["itemFile"]) == a["itemBytes"], \
        "B's run rewrote A's already-resolved item file"
