"""Review queue: items the human finishes by dragging (task 201).

One item per site in ``data/review/<site>.<lead-plan>.json`` (``<site>.json`` when the
site has no candidate picture): the site, its candidate pictures (with the 200 evidence
field when the source row has one), and proposed pairs per candidate in platefit format
(page px of the candidate's image frame -> lon/lat). Saving corrected pairs through the
existing fit tool writes a ``data/db/platefits/<site>.<plan>.json`` doc; that doc
RESOLVES the whole item. ``export`` derives resolution from those docs (never a second
store), records it into the item file, and writes the open list to
``web/data/review.json`` for the page's Review section (web/review.js).

Producers: the batch tasks (203a/203b/212) call ``upsert_item`` to create and update
items; only ``export`` writes the page file. ``resolved`` is write-once: an upsert never
clears or overwrites it. The contract the producers read is data/review/README.md.

Stdlib-only: importable by 203a/203b/212 in any environment (no numpy, no network).
CLI: ``python3 fit/review.py export [--root DIR]``.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _now():
    return datetime.now(timezone.utc).isoformat()


def _items_dir(root):
    return Path(root) / "data" / "review"


def _save_json(path, obj):
    """Atomic JSON write, same convention as the doc store (indent=1, no trailing newline)."""
    path = Path(path)
    tmp = str(path) + "." + str(os.getpid()) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def item_path(root, site_id, lead=None):
    """The item file's path: data/review/<site>.<lead>.json, or <site>.json without a lead."""
    name = site_id if not lead else "%s.%s" % (site_id, lead)
    return str(_items_dir(root) / (name + ".json"))


def _iter_item_files(root):
    d = _items_dir(root)
    if not d.is_dir():
        return
    for p in sorted(d.iterdir()):
        if p.suffix == ".json":
            yield p


def _find_item(root, site_id):
    """The existing item for a site, keyed by its site field (any file name). -> (path, item) or (None, None)."""
    for p in _iter_item_files(root):
        item = json.loads(p.read_text())
        if item.get("site") == site_id:
            return p, item
    return None, None


def upsert_item(root, site_id, entries, no_picture=None):
    """Create or update the item for one site; returns the path written.

    entries: candidate dicts; each needs ``plan``. Candidates are merged by ``plan``:
    a same-plan entry replaces the existing one in place, new plans are appended.
    ``no_picture``: a dict records ``no_picture_found`` (a search that found nothing);
    None keeps the existing record for a candidate-less item (a re-run of "still no
    picture") and clears it once the item has candidates again. ``resolved`` is
    write-once: it is never cleared or overwritten here. ``web/data/review.json`` is
    never written here (export owns it). The file name's lead follows candidates[0].plan;
    a changed lead moves the file.
    """
    entries = list(entries)
    for e in entries:
        if not e.get("plan"):
            raise ValueError("a candidate needs a plan id: %r" % (e.get("title"),))
    _, item = _find_item(root, site_id)
    if item is None:
        item = {"site": site_id, "candidates": [], "no_picture_found": None, "resolved": None}
    cands = item.setdefault("candidates", [])
    index = {c.get("plan"): i for i, c in enumerate(cands)}
    for e in entries:
        if e["plan"] in index:
            cands[index[e["plan"]]] = e
        else:
            index[e["plan"]] = len(cands)
            cands.append(e)
    if isinstance(no_picture, dict):
        item["no_picture_found"] = no_picture
    elif entries:
        item["no_picture_found"] = None
    lead = cands[0]["plan"] if cands else None
    target = Path(item_path(root, site_id, lead))
    old, _ = _find_item(root, site_id)
    if old is not None and old != target:
        old.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    _save_json(target, item)
    return str(target)


def _sha16(title):
    return "c_" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:16]


def candidate_evidence(plan_id, data_root=None):
    """The 200 evidence field of a picture's source row, verbatim, or None.

    Book rows: data/books/index.jsonl by id. Commons rows: data/commons/files.jsonl by
    c_+sha1(title)[:16] (the row stores no id; the plans id hashes the SOURCE title, and
    the row keeps the File: prefix, so a full scan is the lookup). None when the row is
    missing or carries no evidence field (rows 801 will evidence later).
    """
    root = Path(data_root) if data_root else ROOT
    if isinstance(plan_id, str) and plan_id.startswith("c_"):
        path = root / "data" / "commons" / "files.jsonl"
        if path.is_file():
            for line in path.read_text().splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                t = row.get("title")
                if t and _sha16(t) == plan_id:
                    return row.get("evidence")
        return None
    path = root / "data" / "books" / "index.jsonl"
    if path.is_file():
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("id") == plan_id:
                return row.get("evidence")
    return None


def resolved_doc(item, root):
    """The platefit doc id that resolves this item, or None.

    The recorded ``resolved`` wins; otherwise the first candidate that has a
    data/db/platefits/<site>.<plan>.json doc. Resolution is DERIVED from the docs -
    saving any one candidate's pairs resolves the whole item; the item file gains no
    authority of its own.
    """
    rec = item.get("resolved") or {}
    if rec.get("doc"):
        return rec["doc"]
    site = item.get("site")
    for c in item.get("candidates") or []:
        doc = "%s.%s" % (site, c.get("plan"))
        if (Path(root) / "data" / "db" / "platefits" / (doc + ".json")).is_file():
            return doc
    return None


def _site_names(root):
    path = Path(root) / "web" / "data" / "sites.json"
    names = {}
    if path.is_file():
        d = json.loads(path.read_text())
        sites = d.get("sites") if isinstance(d, dict) else d
        for s in sites or []:
            if s.get("id"):
                names[s["id"]] = s.get("name")
    return names


def export(root):
    """Write web/data/review.json: the OPEN items for the page's Review section.

    Open = resolved not recorded AND no platefits doc for any candidate. When it finds
    a resolving doc it records ``resolved: {doc, at: <the doc's at>}`` into the item
    file (write-once). Output entries: {site, name, lead, candidates (verbatim,
    producer extras included), no_picture_found}, open items only, sorted by site name
    (name from web/data/sites.json; a missing site falls back to the raw id).
    Returns (n_open, n_total).
    """
    root = Path(root)
    names = _site_names(root)
    entries, n_total = [], 0
    for p in _iter_item_files(root):
        item = json.loads(p.read_text())
        if not item.get("site"):
            continue
        n_total += 1
        doc = resolved_doc(item, root)
        if doc and not (item.get("resolved") or {}).get("doc"):
            docj = json.loads((root / "data" / "db" / "platefits" / (doc + ".json")).read_text())
            item["resolved"] = {"doc": doc, "at": docj.get("at")}
            _save_json(p, item)
        if doc:
            continue
        name = names.get(item["site"])
        if name is None:
            name = item["site"]
            print("review: site %r not in web/data/sites.json; using the id as name"
                  % item["site"], file=sys.stderr)
        entries.append({
            "site": item["site"],
            "name": name,
            "lead": (item.get("candidates") or [{}])[0].get("plan"),
            "candidates": item.get("candidates") or [],
            "no_picture_found": item.get("no_picture_found"),
        })
    entries.sort(key=lambda e: (e["name"] or "").lower())
    out_path = root / "web" / "data" / "review.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _save_json(out_path, {"at": _now(), "items": entries})
    return len(entries), n_total


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Review queue items: one per site the gate could not fit (data/review/).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("export", help="write web/data/review.json (open items) from data/review/")
    ex.add_argument("--root", default=str(ROOT), help="the project root (default: this checkout)")
    a = ap.parse_args(argv)
    if a.cmd == "export":
        n_open, n_total = export(a.root)
        print("review: %d open of %d items -> web/data/review.json" % (n_open, n_total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
