"""The review queue (task 201, GOAL points 1-2): the fits the machine could not place, and the sites with
no picture at all - the human's drag is the last word. Driven end to end against the real product in the
temp tree: the CLI export and the page data it writes (the item file is the source of truth), a headless
load of the page (the Review tab, the list, the stats-line count), a human save through the existing
document-store path (which resolves the item on the next export), and the fit tool's (id, site) row keying.
The test owns the queue: the temp tree's copy of the repo's two seed items is deleted and re-seeded
through fit/review.py's upsert API. No network, ephemeral port; the headless cases run only when the
machine has Chrome (the install recipe is in PITFALLS)."""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from conftest import get, get_json, put_json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fit"))
import review  # noqa: E402  (the upsert/export API - the same code 203a/203b/212 will call)

CHROME = "/opt/google/chrome/chrome"
NODE_MODULES = "/home/agent/tools/shot/node_modules"

ALLIGATOR = "alligator-effigy-mound-q4732645"
BIBRACTE = "bibracte-q650053"
LEAD = "ancientmonuments00squi_n0214_2"

# The Review tab, the list and the stats line, as the user sees them (checked through the page, not the file).
PROBE_LIST = """(async () => {
  const t0 = Date.now();
  while (Date.now() - t0 < 30000) {
    if (S.ready && S.sites.length && RV.loaded) break;
    await new Promise(r => setTimeout(r, 250));
  }
  if (!(S.ready && S.sites.length && RV.loaded))
    return { boot: false, ready: !!S.ready, mapLoaded: !!S.mapLoaded, sites: S.sites.length,
             plans: P.rows.length, rvloaded: RV.loaded, rvn: RV.items.length };
  S.tab = 'review'; renderList();
  const tabs = [...document.querySelectorAll('#body .tabs button')]
    .map(b => b.id + '=' + b.textContent + ':' + b.getAttribute('aria-pressed'));
  const list = (document.querySelector('#body') || {}).textContent || '';
  S.tab = 'sites'; renderList();
  const fits = [...document.querySelectorAll('#body .fit')].map(p => p.textContent);
  const check = {};
  for (const u of ['data/review.json', 'data/scans.json', 'data/amazon/areas.json']) {
    try { check[u] = (await fetch(u)).status; } catch (e) { check[u] = 'error'; }
  }
  return { boot: true, tabs, list, fits, rvn: RV.items.length, check };
})()"""

# The (id, site) keying of the fit tool: every fit-list button of the four duplicate-id sites must open
# the row of its own site, and the two shared plan ids must resolve to two distinct composite keys.
PROBE_KEYING = """(async () => {
  const t0 = Date.now();
  while (Date.now() - t0 < 30000) {
    if (S.ready && S.sites.length && P.rows.length) break;
    await new Promise(r => setTimeout(r, 250));
  }
  if (!(S.ready && S.sites.length && P.rows.length))
    return { boot: false, ready: !!S.ready, mapLoaded: !!S.mapLoaded,
             sites: S.sites.length, plans: P.rows.length };
  const sites = ['avebury-q661855', 'stonehenge-q39671',
                 'king-arthur-s-round-table-q283800', 'mayburgh-henge-q1469390'];
  const dups = {};
  for (const k of Object.keys(P.byId))
    if (k.startsWith('c_ffb3daac218b481f.') || k.startsWith('c_984782b9e35e8ded.')) dups[k] = P.byId[k].url;
  const per = {};
  for (const sid of sites) {
    const s = S.byId[sid];
    if (!s) { per[sid] = 'no site'; continue; }
    if (P.active) endFit();
    select(sid);
    try { await loadDeps(s); } catch (e) {}
    await new Promise(r => setTimeout(r, 100));
    startFit(s);
    per[sid] = [...document.querySelectorAll('#body [data-plan]')].map(b => {
      const k = b.dataset.plan, row = P.byId[k];
      return { k, row: !!row, url: row && row.url, has: row ? (row.sites || []).includes(sid) : false };
    });
    endFit();
  }
  return { dups, per };
})()"""


def repo_items():
    """The committed seed items: the known state the test re-seeds the temp tree with."""
    out = {}
    for name in sorted(os.listdir(os.path.join(ROOT, "data", "review"))):
        if name.endswith(".json"):
            item = json.load(open(os.path.join(ROOT, "data", "review", name)))
            out[item["site"]] = item
    return out


def run_export(tree):
    p = subprocess.run([sys.executable, "fit/review.py", "export", "--root", str(tree)],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, (p.returncode, p.stderr)
    return p


def seed_queue(tree):
    """Reset the temp tree's queue to the repo's seed items, written through the upsert API.

    conftest copies the repo's committed items into the tree, so they are deleted first: the test owns
    what the queue contains, never the repo's."""
    for p in (Path(tree) / "data" / "review").glob("*.json"):
        p.unlink()
    page = Path(tree) / "web" / "data" / "review.json"
    if page.exists():
        page.unlink()
    for item in repo_items().values():
        review.upsert_item(str(tree), item["site"], item["candidates"],
                           no_picture=item["no_picture_found"])
    run_export(tree)  # the page reads the export; the headless cases need it present


@pytest.fixture(scope="module")
def queue(served):
    base, tree = served
    seed_queue(tree)
    return {"base": base, "tree": tree}


def _shot(base, png, js):
    env = dict(os.environ, NODE_PATH=NODE_MODULES, POSTWAIT="300")
    try:
        return subprocess.run(["node", os.path.join(ROOT, "tools", "shot.mjs"), base + "/",
                               str(png), "8000", "1200", "800", js],
                              cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired as e:
        raise AssertionError("shot.mjs timed out:\n" + (e.stdout or b"")[-2000:].decode(errors="replace"))


def _probe(base, png, js):
    p = _shot(base, png, js)
    for ln in p.stdout.splitlines():
        if ln.startswith("[eval]"):
            return json.loads(ln[len("[eval]"):]), p
    raise AssertionError("no [eval] line in shot.mjs output:\n" + p.stdout[-2000:])


def _headless_or_skip():
    if not (os.path.exists(CHROME) and os.path.isdir(NODE_MODULES)):
        pytest.skip("headless Chrome is not installed on this machine (the recipe is in PITFALLS.md)")


def test_export_cli(queue):
    """Box 1 + 4: the CLI export publishes the open items to web/data/review.json, computed from
    data/review/ (name, lead, candidates verbatim, the no-picture record) and re-running it is idempotent."""
    base, tree = queue["base"], queue["tree"]
    p = run_export(tree)
    assert p.stdout == "review: 2 open of 2 items -> web/data/review.json\n", p.stdout + p.stderr
    status, body1 = get_json(base + "/data/review.json")
    assert status == 200 and "at" in body1 and isinstance(body1["items"], list)
    run_export(tree)  # idempotent: same body apart from the timestamp
    status, body2 = get_json(base + "/data/review.json")
    assert status == 200
    a, b = dict(body1), dict(body2)
    a.pop("at"), b.pop("at")
    assert a == b, "re-running the export must not change the page data"

    seeds = repo_items()
    _, sites = get_json(base + "/data/sites.json")
    names = {s["id"]: s.get("name") for s in sites["sites"]}
    # open items only, sorted by site name (the page's count is len(items) - computed, never hardcoded)
    assert [it["site"] for it in body1["items"]] == [ALLIGATOR, BIBRACTE]
    it, want = body1["items"][0], seeds[ALLIGATOR]
    assert it["name"] == names[ALLIGATOR] == "Alligator Effigy Mound"
    assert it["lead"] == want["candidates"][0]["plan"] == LEAD
    assert len(it["candidates"]) == 2
    for got, w in zip(it["candidates"], want["candidates"]):
        for field in ("plan", "title", "url", "evidence", "pairs", "coarse"):
            assert got[field] == w[field], (w["plan"], field)
    assert it["no_picture_found"] is None
    b2, want2 = body1["items"][1], seeds[BIBRACTE]
    assert b2["name"] == names[BIBRACTE] == "Bibracte"
    assert b2["lead"] is None and b2["candidates"] == []
    assert b2["no_picture_found"]["searched"] == want2["no_picture_found"]["searched"]


def test_page_shows_the_review_list(queue, tmp_path_factory):
    """Box 2 + 4: a headless load of the page shows the Review tab with its open count, the two seeded
    items in the list (candidates, and the no-picture record with what was searched), and the home
    stats line carries the same computed count."""
    _headless_or_skip()
    base = queue["base"]
    data, p = _probe(base, tmp_path_factory.mktemp("rvshot") / "list.png", PROBE_LIST)
    assert data.get("boot") is True, (data, p.stdout[-2000:])
    assert "[pageerror]" not in p.stdout, p.stdout[-2000:]
    assert "[reqfail]" not in p.stdout, p.stdout[-2000:]
    # the only 404s a page load can make in this tree: data/scans.json and data/amazon/areas.json
    # (absent generated files; the browser console does not print their urls, only the count is stable)
    n404 = sum(1 for ln in p.stdout.splitlines()
               if ln.startswith("[console] error") and "404" in ln)
    assert n404 == 2, p.stdout
    assert data["check"] == {"data/review.json": 200, "data/scans.json": 404,
                             "data/amazon/areas.json": 404}, data["check"]
    tabs = {t.split("=", 1)[0]: t.split("=", 1)[1] for t in data["tabs"]}
    assert tabs["h-review"] == "Review (2):true", tabs
    lst = data["list"].lower()
    for phrase in ("alligator effigy mound", "2 candidate pictures",
                   '"the alligator," licking county, ohio', "bibracte", "no picture found",
                   "p180 depictions", "open this site's plan search"):
        assert phrase in lst, phrase
    stats = [f for f in data["fits"] if "built in all" in f]
    assert stats and "2 review items open" in stats[0], stats
    assert data["rvn"] == 2


def test_save_resolves_the_item(queue):
    """Box 3: a human save through the existing path (PUT platefits/<site>.<plan>) resolves the item -
    the next export records the saved doc id and drops the item from the queue. The PUT wakes the
    plan_fit worker, which in this tree has no pipeline/ and dies on the import: the server stays up
    and nothing else in the tree changes."""
    base, tree = queue["base"], queue["tree"]

    def snapshot():
        out = {}
        for f in sorted(os.listdir(os.path.join(tree, "data", "db", "platefits"))):
            if f.endswith(".json"):
                out["platefits/" + f] = hashlib.sha256(
                    open(os.path.join(tree, "data", "db", "platefits", f), "rb").read()).hexdigest()
        for d in sorted(os.listdir(os.path.join(tree, "web", "data", "sites"))):
            p = os.path.join(tree, "web", "data", "sites", d, "depictions.json")
            if os.path.exists(p):
                out["depictions/" + d] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        return out

    before = snapshot()
    # the document exactly as the page's saveFit saves it: the book candidate's stored fields, the
    # crop from its map_box, the pairs in platefit format
    cand = [c for c in repo_items()[ALLIGATOR]["candidates"] if c["plan"] == LEAD][0]
    mb, size = cand["map_box"], cand["size"]
    doc = {"site": ALLIGATOR, "plan": cand["plan"], "ia": cand["ia"], "file": cand["file"],
           "crop": [round(mb[0] * size[0]), round(mb[1] * size[1]),
                    round(mb[2] * size[0]), round(mb[3] * size[1])],
           "model": "similarity", "src": "book", "url": None, "ref": None,
           "size": list(size), "pairs": [list(p) for p in cand["pairs"]],
           "label": cand["label"], "title": cand["title"], "book": cand["book"],
           "cite": cand["cite"], "at": "2026-10-11T12:00:00.000Z"}
    status, body = put_json(base + "/api/db/platefits/%s.%s" % (ALLIGATOR, LEAD), doc)
    assert status == 200 and json.loads(body) == {"ok": True}

    t0 = time.time()
    while time.time() - t0 < 4:  # let the worker wake (and die) - the server must keep answering
        status, _ = get(base + "/")
        assert status == 200
        time.sleep(0.5)
    after = snapshot()
    added = {k for k in after if k not in before}
    assert added == {"platefits/%s.%s.json" % (ALLIGATOR, LEAD)}
    for k in before:
        assert before[k] == after[k], "the worker must not touch %s" % k

    p = run_export(tree)
    assert p.stdout == "review: 1 open of 2 items -> web/data/review.json\n", p.stdout + p.stderr
    status, body = get_json(base + "/data/review.json")
    assert status == 200 and [it["site"] for it in body["items"]] == [BIBRACTE]
    assert body["items"][0]["no_picture_found"]["searched"] == \
        repo_items()[BIBRACTE]["no_picture_found"]["searched"]  # the other seeded item is still open
    item = json.loads((Path(tree) / "data" / "review" / (ALLIGATOR + "." + LEAD + ".json")).read_text())
    assert item["resolved"] == {"doc": "%s.%s" % (ALLIGATOR, LEAD), "at": doc["at"]}
    status, stored = get_json(base + "/api/db/platefits/%s.%s" % (ALLIGATOR, LEAD))
    assert status == 200 and stored["pairs"] == doc["pairs"] and stored["at"] == doc["at"]


def test_plan_lookup_is_keyed_by_id_and_site(queue, tmp_path_factory):
    """Box 5: the fit tool's plan lookup is keyed by (id, sites[0]) - the two pictures that each depict
    two sites (the Larned history, Mayburgh-1769) keep two rows, and every fit-list button of the four
    sites opens the row of its own site."""
    _headless_or_skip()
    base = queue["base"]
    data, p = _probe(base, tmp_path_factory.mktemp("rvshot") / "keying.png", PROBE_KEYING)
    assert data.get("boot") is True, (data, p.stdout[-2000:])
    assert "[pageerror]" not in p.stdout, p.stdout[-2000:]
    assert "[reqfail]" not in p.stdout, p.stdout[-2000:]
    expect = {
        "c_ffb3daac218b481f.avebury-q661855": "media/commons/avebury-q661855/ffb3daac218b481f.jpg",
        "c_ffb3daac218b481f.stonehenge-q39671": "media/commons/stonehenge-q39671/ffb3daac218b481f.jpg",
        "c_984782b9e35e8ded.king-arthur-s-round-table-q283800":
            "media/commons/king-arthur-s-round-table-q283800/984782b9e35e8ded.jpg",
        "c_984782b9e35e8ded.mayburgh-henge-q1469390":
            "media/commons/mayburgh-henge-q1469390/984782b9e35e8ded.jpg",
    }
    # the shared ids keep both rows, one composite key per site, each with its own picture
    for key, url in expect.items():
        assert data["dups"].get(key) == url, key
    all_btns = {}
    for sid, btns in data["per"].items():
        assert isinstance(btns, list) and btns, (sid, btns)  # all four sites built, each with a fit list
        for b in btns:
            assert b["row"] and b["has"], (sid, b)  # every button resolves to the row of its own site
            all_btns[b["k"]] = b
    for key, url in expect.items():
        assert all_btns[key]["url"] == url, key


def test_index_html_review_footprint(queue):
    """Box 2 + 4 (delivery level): index.html carries exactly one review footprint - the script tag -
    and no review count or markup; the count the page shows is computed from web/data/review.json."""
    base = queue["base"]
    status, body = get(base + "/")
    assert status == 200
    assert body.count(b'src="review.js"') == 1
    assert b"h-review" not in body and b"rvcount" not in body and b"Review (" not in body
    status, body = get(base + "/review.js")
    assert status == 200 and len(body) > 1000
