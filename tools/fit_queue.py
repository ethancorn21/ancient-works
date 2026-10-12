"""The "Ready to fit" queue (task 305): the built sites with candidate pictures but no hand fit yet,
one per entry, ordered so the site most worth seeing comes first.

usage: tools/fit_queue.py [--root DIR]  -> web/data/fit_queue.json

The owner's hand fits are the only fits that land right (the automatic ones are tasks 301/302b), so the
page shows him the next site of this queue with its best candidate already loaded, and his save runs the
one-site line on that site (server/serve.py). One site at a time: when he saves, that site is finished.

A site is in the queue exactly when all three hold:

  built        it has an entry in web/data/sites.json AND a web/data/sites/<id>/ directory (the same
               rule as tools/site_done.py);
  a candidate  web/data/plans.json names it in a row's sites field, or one of its data/review/ item
               files holds it a candidate (all item files count, open and resolved: the item's `site`
               field is the key, never the file name);
  no hand fit  none of the site's data/db/platefits/ documents carries by: "hand" (agent documents do
               not disqualify: the owner is still free to place a better one).

The best candidate: a true plan over a bird's-eye view, then the larger drawing area (a book row: its
map_box fraction of the page size in px; a row with no box, or a commons row: the whole page/image; an
item candidate with no size stored: 0), then the plan id (stable). The one-word reason says why it won:
"the only candidate", "a true plan" (a plan chosen while a view exists), "the clearest scan" (best of
several plans), "the clearest view" (the views win). Sites are ordered by the same rule applied to each
site's best candidate, then by the site's name - the cleanest, most ink to click on comes first.

Stdlib only: it reads exactly those four inputs and never opens an image (the sizes come from the json
files), so the owner's Mac can run it with any python. Finder/Amazon data never enters the queue.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The row's named fields, in web/data/plans.json column order (the page's openPlan reads them).
ROW_FIELDS = ("id", "book", "ia", "file", "title", "label", "size", "map_box",
              "sites", "cite", "url", "view", "ref")


def _save_json(path, obj):
    """Atomic JSON write, same convention as the doc store (indent=1, no trailing newline)."""
    path = Path(path)
    tmp = str(path) + "." + str(os.getpid()) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def _load_json(path):
    """The file's JSON, or None when the file is absent (the page is served without it too);
    a malformed file fails loudly."""
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def _plans_rows(root):
    """The web/data/plans.json rows as named dicts, in file order (the page's P.rows shape)."""
    d = _load_json(Path(root) / "web" / "data" / "plans.json") or {}
    cols = {c: i for i, c in enumerate(d.get("cols") or [])}
    return [{k: r[i] for k, i in cols.items()} for r in d.get("rows") or []]


def _built_sites(root):
    """The built sites as (id, name) in sites.json order: an entry in web/data/sites.json and a
    web/data/sites/<id>/ directory (the same rule as tools/site_done.py)."""
    d = _load_json(Path(root) / "web" / "data" / "sites.json")
    ss = d.get("sites") if isinstance(d, dict) else d
    base = Path(root) / "web" / "data" / "sites"
    return [(s["id"], s.get("name") or s["id"]) for s in (ss or [])
            if s.get("id") and (base / s["id"]).is_dir()]


def _item_candidates(root):
    """The candidates of every data/review/ item file, keyed by the item's `site` field (open and
    resolved items alike: a resolved item's candidates are still the site's candidate pictures - what
    takes a site out of the queue is a hand document, not a resolution)."""
    out = {}
    d = Path(root) / "data" / "review"
    if not d.is_dir():
        return out
    for p in sorted(d.iterdir()):
        if p.suffix != ".json":
            continue
        item = json.loads(p.read_text())
        sid = item.get("site")
        if not sid:
            continue
        for c in item.get("candidates") or []:
            if c.get("plan"):
                out.setdefault(sid, []).append(c)
    return out


def _hand_sites(root):
    """The site ids that already have a by: "hand" fit document (the doc's `site` field, or, for a
    doc without one, the id prefix before the first dot of its file name)."""
    out = set()
    d = Path(root) / "data" / "db" / "platefits"
    if not d.is_dir():
        return out
    for p in sorted(d.iterdir()):
        if p.suffix != ".json":
            continue
        doc = json.loads(p.read_text())
        if doc.get("by") == "hand":
            out.add(doc.get("site") or p.name[:-5].split(".", 1)[0])
    return out


def _synth_row(c, site_id):
    """The row the page synthesizes when a candidate has no plans.json row naming the site
    (web/review.js rvResolveRow, same fields): the candidate's stored fields, sites narrowed
    to this site."""
    return {
        "id": c.get("plan"), "book": c.get("book"), "ia": c.get("ia"), "file": c.get("file"),
        "title": c.get("title") or c.get("plan"), "label": c.get("label"), "size": c.get("size"),
        "map_box": c.get("map_box"), "sites": [site_id], "cite": c.get("cite"), "url": c.get("url"),
        "view": c.get("view") or False, "ref": c.get("ref"),
    }


def _candidates(site_id, rows, item_cands):
    """The site's candidate pictures keyed by plan id: the plans.json rows naming it plus its item
    candidates, deduped by plan (a plan in both resolves to the plans row: the richer one). File
    order, plans rows first."""
    out = {}
    for r in rows:
        if r.get("id") and site_id in (r.get("sites") or []):
            out.setdefault(r["id"], r)
    for c in item_cands:
        out.setdefault(c["plan"], _synth_row(c, site_id))
    return out


def _draw_px(row):
    """The drawing's area in page px: the map_box fraction of the page/image size; a row without a
    box is the whole page/image; 0 when no size is stored."""
    size = row.get("size") or [0, 0]
    mb = row.get("map_box")
    if isinstance(mb, (list, tuple)) and len(mb) == 4:
        w = max(0.0, float(mb[2]) - float(mb[0])) * float(size[0])
        h = max(0.0, float(mb[3]) - float(mb[1])) * float(size[1])
        return int(round(w * h))
    return int(float(size[0]) * float(size[1]))


def _best_key(plan, row):
    """True plan over a view, then the larger drawing, then the plan id (stable)."""
    return (bool(row.get("view")), -_draw_px(row), plan)


def _reason(cands):
    """The one word for why the winner won: the only candidate; a true plan (chosen while a view
    exists); the clearest scan (best of several plans); the clearest view (the views win)."""
    if len(cands) == 1:
        return "the only candidate"
    plans = [r for r in cands.values() if not r.get("view")]
    if plans and len(plans) < len(cands):
        return "a true plan"
    if plans:
        return "the clearest scan"
    return "the clearest view"


def _entry(sid, name, cands):
    """The site's queue entry: its best candidate (plan over view, then drawing area, then
    plan id), the one-word reason, and the whole candidate list in the same order."""
    plan, row = min(cands.items(), key=lambda kv: _best_key(kv[0], kv[1]))
    return {
        "site": sid,
        "name": name,
        "best": {"plan": plan, "reason": _reason(cands),
                 "row": {k: row.get(k) for k in ROW_FIELDS}},
        "candidates": [
            {"plan": p, "title": r.get("title") or p, "book": r.get("book"),
             "view": bool(r.get("view")), "draw_px": _draw_px(r)}
            for p, r in sorted(cands.items(), key=lambda kv: _best_key(kv[0], kv[1]))
        ],
    }


def build(root):
    """The queue, ready to serialize: one entry per built site with a candidate and no hand fit,
    ordered by each site's best candidate (plan over view, then drawing area, then name).
    The sites' candidate maps are gathered first and the entries derived from that map, so
    the maps stay available for decisions that must see every site's set at once."""
    rows = _plans_rows(root)
    item_cands = _item_candidates(root)
    hand = _hand_sites(root)
    built = _built_sites(root)
    cands = {}
    for sid, name in built:
        if sid in hand:
            continue
        c = _candidates(sid, rows, item_cands.get(sid) or [])
        if c:
            cands[sid] = c
    entries = [_entry(sid, name, cands[sid]) for sid, name in built if sid in cands]
    entries.sort(key=lambda e: _best_key(e["best"]["plan"], e["best"]["row"]) + (e["name"],))
    return {"at": datetime.now(timezone.utc).isoformat(), "entries": entries}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The 'Ready to fit' queue (task 305) -> web/data/fit_queue.json.")
    ap.add_argument("--root", default=str(ROOT), help="the data root (default: this checkout)")
    a = ap.parse_args(argv)
    q = build(a.root)
    path = Path(a.root) / "web" / "data" / "fit_queue.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    _save_json(path, q)
    n = len(q["entries"])
    print(f"ready-to-fit queue: {n} site(s) -> {path}")
    for i, e in enumerate(q["entries"][:5], 1):
        print(f"  {i}. {e['name']} ({e['site']}): {e['best']['row'].get('title') or e['best']['plan']} - {e['best']['reason']}")
    if n > 5:
        print(f"  ... {n - 5} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
