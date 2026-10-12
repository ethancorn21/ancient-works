"""The review queue (task 201, GOAL points 1-2): the fits the machine could not place, and the sites with
no picture at all - the human's drag is the last word. Driven end to end against the real product in the
temp tree: the CLI export and the page data it writes (the item file is the source of truth), a headless
load of the page (the Review tab, the list, the stats-line count), a human save through the existing
document-store path (which resolves the item on the next export), and the fit tool's (id, site) row keying.
The test owns the queue: the temp tree's copy of the repo's seed items is deleted and re-seeded
through fit/review.py's upsert API. No network, ephemeral port; the headless cases run only when the
machine has Chrome (the install recipe is in PITFALLS).

Task 803 (re-baseline): the queue grew with the batches (203a's 88 upserted items; the batch also
records a gate verdict on the candidates of a failed fit and writes an automatic platefit doc that
DERIVES an item's resolution), so the counts, the open list, the page phrases and the save-flow pick
are all computed from the repo's data/review/ through 201's own rules (resolved_doc; the export's
documented name-sorted order; the page's documented render) instead of pinned to a population. On
the pre-batch population the same derivation reduces exactly to the values this file pinned when it
was written: "2 open of 2", the open list [alligator, bibracte], Review (2) / rvn == 2 /
"2 review items open", and the save pick landing on alligator's book row n0214_2 (the only open site
with a book row carrying map_box and size)."""
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
  // The probe re-fetches only the path that must exist (data/review.json). Re-fetching the two
  // expected-404 paths (data/scans.json, data/amazon/areas.json) would add two more console 404
  // lines on top of the page's own boot fetches, which the n404 count in the test (== 2) cannot
  // attribute: the browser console prints no URL, only the count.
  let check;
  try { check = (await fetch('data/review.json')).status; } catch (e) { check = 'error'; }
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
  return { boot: true, dups, per };
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


def _site_names(root):
    """Site id -> display name: web/data/sites.json, then the catalog (data/catalog/
    sites.jsonl) - the export's name source (309's right-place check names its unbuilt
    right sites from the catalog)."""
    names = {}
    path = os.path.join(root, "web", "data", "sites.json")
    if os.path.exists(path):
        d = json.load(open(path))
        sites = d.get("sites") if isinstance(d, dict) else d
        for s in sites or []:
            names[s["id"]] = s.get("name")
    cat = os.path.join(root, "data", "catalog", "sites.jsonl")
    if os.path.exists(cat):
        for line in open(cat):
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("id") and not names.get(r["id"]):
                names[r["id"]] = r.get("name")
    return names


def _open_items(tree):
    """The queue's open items through 201's own rules: review.resolved_doc decides which item has
    a resolving platefit doc (the recorded field wins, otherwise any candidate's doc), and the
    export's documented order (sorted by site name - the export's name source: sites.json,
    then the catalog, then the id - stable) decides the list. -> (open sites in that order,
    total item count, names)"""
    items = {}
    d = os.path.join(tree, "data", "review")
    for name in sorted(os.listdir(d)):
        if name.endswith(".json"):
            item = json.loads(open(os.path.join(d, name)).read())
            if item.get("site"):
                items[item["site"]] = item
    names = _site_names(tree)
    resolved = {s: review.resolved_doc(it, tree) for s, it in items.items()}
    open_sites = sorted((s for s, r in resolved.items() if not r),
                        key=lambda s: (names.get(s) or s).lower())
    return open_sites, len(items), names


def seed_queue(tree):
    """Reset the temp tree's queue to the repo's committed items, written through the upsert API.

    conftest copies the repo's committed items into the tree, so they are deleted first: the test owns
    what the queue contains, never the repo's. Re-upserting an item's own entries is a no-op merge
    (same plans replaced in place, no_picture re-recorded), so the re-seeded queue equals the repo's."""
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
    data/review/ (name, lead, candidates verbatim, the no-picture record) and re-running it is idempotent.
    The expected stdout counts, the open list and the per-item fields are derived from the queue
    through 201's own rules (resolved_doc; the export's documented name-sorted order), never pinned
    to a population (803)."""
    base, tree = queue["base"], queue["tree"]
    open_sites, n_total, names = _open_items(tree)
    assert n_total >= 1, "the queue is empty - the derivation above is vacuous"
    p = run_export(tree)
    assert p.stdout == "review: %d open of %d items -> web/data/review.json\n" % (len(open_sites), n_total), \
        p.stdout + p.stderr
    status, body1 = get_json(base + "/data/review.json")
    assert status == 200 and "at" in body1 and isinstance(body1["items"], list)
    run_export(tree)  # idempotent: same body apart from the timestamp
    status, body2 = get_json(base + "/data/review.json")
    assert status == 200
    a, b = dict(body1), dict(body2)
    a.pop("at"), b.pop("at")
    assert a == b, "re-running the export must not change the page data"

    seeds = repo_items()
    # open items only, sorted by site name (the export's documented order; the page's count is
    # len(items) - computed, never hardcoded)
    assert [it["site"] for it in body1["items"]] == open_sites, \
        ([it["site"] for it in body1["items"]], open_sites)
    for it, want in zip(body1["items"], [seeds[s] for s in open_sites]):
        # the entry is the item's own record: the name from sites.json (id fallback), the lead the
        # first candidate's plan, the candidates and the no-picture record verbatim (producer extras
        # included) - the export transforms nothing
        assert it["name"] == (names.get(it["site"]) or it["site"]), (it["site"], it["name"])
        want_lead = (want.get("candidates") or [{}])[0].get("plan")
        assert it["lead"] == want_lead, (it["site"], it["lead"], want_lead)
        assert it["candidates"] == (want.get("candidates") or []), it["site"]
        assert it["no_picture_found"] == want.get("no_picture_found"), it["site"]


def test_page_shows_the_review_list(queue, tmp_path_factory):
    """Box 2 + 4: a headless load of the page shows the Review tab with its open count, the open
    items in the list and the home stats line with the same computed count. The count and every
    phrase checked are derived from the queue through the page's documented render (803): the
    first open item's name and head (its no-picture record's searched text when it has no
    candidates), the same for the first open item that has candidates, and the stats clause."""
    _headless_or_skip()
    base = queue["base"]
    data, p = _probe(base, tmp_path_factory.mktemp("rvshot") / "list.png", PROBE_LIST)
    assert data.get("boot") is True, (data, p.stdout[-2000:])
    assert "[pageerror]" not in p.stdout, p.stdout[-2000:]
    assert "[reqfail]" not in p.stdout, p.stdout[-2000:]
    # the only 404s a page load can make in this tree: data/scans.json and data/amazon/areas.json
    # (absent generated files, each fetched once at boot; a response-level probe that logs every
    # url found exactly these two). The browser console prints no URL, only the count, which the
    # probe's own fetches must not inflate - hence the check loop above re-fetches review.json only
    n404 = sum(1 for ln in p.stdout.splitlines()
               if ln.startswith("[console] error") and "404" in ln)
    assert n404 == 2, p.stdout
    assert data["check"] == 200, data["check"]

    open_sites, _n_total, names = _open_items(queue["tree"])
    n = len(open_sites)
    tabs = {t.split("=", 1)[0]: t.split("=", 1)[1] for t in data["tabs"]}
    assert tabs["h-review"] == (("Review (%d):true" % n) if n else "Review:true"), tabs
    lst = data["list"].lower()
    # the home stats line, by either wording: the lead's 939382a re-worded "built in all"
    # to "laid on today's ground"; the page's own matcher accepts both
    # (web/review.js: /built in all|laid on today/)
    stats = [f for f in data["fits"] if "built in all" in f or "laid on today" in f]
    assert stats, "the home stats line must be present"
    if n:
        seeds = repo_items()
        first = open_sites[0]
        want = seeds[first]
        assert (names.get(first) or first).lower() in lst, (first, lst[:2000])
        cands = want.get("candidates") or []
        if cands:
            head = "%d candidate picture%s" % (len(cands), "" if len(cands) == 1 else "s")
            assert head in lst, (head, lst[:2000])
            assert (cands[0].get("title") or cands[0]["plan"]).lower() in lst
        else:
            assert "no picture found" in lst, lst[:2000]
            nppf = want.get("no_picture_found")
            searched = nppf["searched"] if nppf else "nothing has been searched yet"
            assert searched.lower() in lst, (searched, lst[:2000])
            assert "open this site's plan search" in lst, lst[:2000]
        # the first open item that has candidates (a different site when the queue starts with a
        # no-picture item): its head and first candidate title reach the page too
        withc = [s for s in open_sites if (seeds[s].get("candidates"))]
        if withc:
            s0 = withc[0]
            c0 = seeds[s0]["candidates"][0]
            assert (names.get(s0) or s0).lower() in lst, s0
            n0 = len(seeds[s0]["candidates"])
            assert "%d candidate picture%s" % (n0, "" if n0 == 1 else "s") in lst, lst[:2000]
            assert (c0.get("title") or c0["plan"]).lower() in lst
        clause = "\u00a0\u00b7 %d review item%s open" % (n, "" if n == 1 else "s")
        assert clause in stats[0], (clause, stats[0])
    else:
        assert "nothing left to review" in lst, lst[:2000]
        for f in stats:
            assert "review item" not in f, f
    assert data["rvn"] == n


def test_save_resolves_the_item(queue):
    """Box 3: a human save through the existing path (PUT platefits/<site>.<plan>) resolves the item -
    the next export records the saved doc id and drops the item from the queue. The document is built
    exactly as the page's saveFit builds it: from the plans.json row for (plan, site) (map_box and
    size for the crop, the book's ia/file/label/book/cite), with the candidate's proposed pairs as
    the human's drag - never from the item entry's stored fields, which a batch upsert may have
    replaced with its slimmer shape (803). The site and plan are picked deterministically: the
    first plans.json row (file order) with a book id, a map_box and a size, whose site has an OPEN
    item carrying that candidate - the page's rvResolveRow opens exactly that row. Before the batch
    that pick is alligator's book row n0214_2; after, the first such open site. The PUT wakes the
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
    open_sites, n_total, names = _open_items(tree)
    assert open_sites, "the queue has no open item to resolve - the derivation is vacuous"
    seeds = repo_items()
    open_set = set(open_sites)
    plans = json.load(open(os.path.join(tree, "web", "data", "plans.json")))
    rows = [dict(zip(plans["cols"], r)) for r in plans["rows"]]
    pick = None
    for r in rows:
        if not (r.get("ia") and r.get("map_box") and r.get("size")):
            continue  # only a book row carries the fields the page's save needs
        for s in r.get("sites") or []:
            if s in open_set and any(c.get("plan") == r["id"] for c in seeds[s].get("candidates") or []):
                pick = (s, r)
                break
        if pick:
            break
    assert pick, "no book row with map_box and size for an open item carrying its candidate"
    site, row = pick
    cand = [c for c in seeds[site]["candidates"] if c["plan"] == row["id"]][0]
    # the document exactly as the page's saveFit saves it: the row's fields, the crop from the
    # row's map_box and size, the candidate's proposed pairs in platefit format
    mb, size = row["map_box"], row["size"]
    doc = {"site": site, "plan": row["id"], "ia": row.get("ia"), "file": row.get("file"),
           "crop": [round(mb[0] * size[0]), round(mb[1] * size[1]),
                    round(mb[2] * size[0]), round(mb[3] * size[1])],
           "model": "similarity", "src": "book", "url": row.get("url"), "ref": row.get("ref"),
           "size": list(size), "pairs": [list(p) for p in cand.get("pairs") or []],
           "label": row.get("label"), "title": row.get("title"), "book": row.get("book"),
           "cite": row.get("cite"), "at": "2026-10-11T12:00:00.000Z"}
    status, body = put_json(base + "/api/db/platefits/%s.%s" % (site, row["id"]), doc)
    assert status == 200 and json.loads(body) == {"ok": True}

    t0 = time.time()
    while time.time() - t0 < 4:  # let the worker wake (and die) - the server must keep answering
        status, _ = get(base + "/")
        assert status == 200
        time.sleep(0.5)
    after = snapshot()
    added = {k for k in after if k not in before}
    assert added == {"platefits/%s.%s.json" % (site, row["id"])}
    for k in before:
        assert before[k] == after[k], "the worker must not touch %s" % k

    p = run_export(tree)
    assert p.stdout == "review: %d open of %d items -> web/data/review.json\n" % (len(open_sites) - 1, n_total), \
        p.stdout + p.stderr
    status, body = get_json(base + "/data/review.json")
    assert status == 200
    # the saved site leaves the open list, its order and the rest of the items unchanged; the
    # first remaining open item is still served verbatim (before the batch: bibracte, with its
    # no-picture record)
    want_rest = [s for s in open_sites if s != site]
    assert [it["site"] for it in body["items"]] == want_rest, \
        ([it["site"] for it in body["items"]], want_rest)
    if want_rest:
        w = seeds[want_rest[0]]
        assert body["items"][0]["name"] == (names.get(want_rest[0]) or want_rest[0])
        assert body["items"][0]["candidates"] == (w.get("candidates") or [])
        assert body["items"][0]["no_picture_found"] == w.get("no_picture_found")
    lead = (seeds[site].get("candidates") or [{}])[0].get("plan")
    item = json.loads(open(review.item_path(tree, site, lead)).read())
    assert item["resolved"] == {"doc": "%s.%s" % (site, row["id"]), "at": doc["at"]}
    status, stored = get_json(base + "/api/db/platefits/%s.%s" % (site, row["id"]))
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
    # Page-caused reqfails, expected: opening a site lists its aerial open, so the page's
    # base imagery is the live Esri feed (server.arcgisonline.com/.../MapServer/tile/... -
    # note the SINGULAR 'tile/', which a '/tiles/' exclusion alone misses); the probe's
    # start/end fit cycle aborts those in-flight fetches (ERR_ABORTED). No other request
    # may fail at the network level.
    assert not any(ln.startswith("[reqfail]") and "/tiles/" not in ln and "arcgisonline" not in ln
                   for ln in p.stdout.splitlines()), p.stdout[-2000:]
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
