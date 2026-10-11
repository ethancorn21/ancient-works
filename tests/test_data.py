"""The data the page's plate-fitting tool works from: web/data/plans.json agrees with the sources
that produced it (the book index and the Commons harvest). Driven through the real server; no network.
"""
import hashlib
import json
import os

from conftest import get_json

COLS = ["id", "book", "ia", "file", "title", "label", "size", "map_box", "sites", "cite", "url", "view", "ref"]


def _rows(base):
    status, data = get_json(base + "/data/plans.json")
    assert status == 200
    assert data["cols"] == COLS
    rows = [dict(zip(COLS, r)) for r in data["rows"]]
    assert len(rows) >= 1100  # 1166 as of the plan; the list only grows
    # one row per (picture, site): the same picture may depict two sites, but never twice for one
    keys = [(r["id"], r["sites"][0] if r["sites"] else None) for r in rows]
    assert len(set(keys)) == len(rows), "duplicate (plan, site) rows"
    assert all(len(r) == len(COLS) for r in rows)
    return rows


def test_book_plans_join_books_index(served):
    base, tree = served
    idx = {json.loads(l)["id"] for l in open(os.path.join(tree, "data", "books", "index.jsonl")) if l.strip()}
    bad = [r["id"] for r in _rows(base) if r["ia"] and r["id"] not in idx]
    assert bad == [], bad[:5]


def test_commons_plans_join_files(served):
    base, tree = served
    files = {}
    for l in open(os.path.join(tree, "data", "commons", "files.jsonl")):
        if l.strip():
            r = json.loads(l)
            files[(r["site"], r["title"])] = r
    bad = []
    for r in _rows(base):
        if not r["url"]:
            continue
        f = files.get((r["sites"][0], r["ref"])) if r.get("ref") else None
        if not f or hashlib.sha1(f["title"].encode()).hexdigest()[:16] != r["id"][2:]:
            bad.append(r["id"])
    assert bad == [], bad[:5]


def test_catalog_data(served):
    """The catalog pins the page plots (every known earthwork, built or not)."""
    base, _ = served
    status, data = get_json(base + "/data/catalog.json")
    assert status == 200
    cols, rows = data["cols"], data["rows"]
    assert len(rows) >= 384  # 12600 as of the plan
    id_i, lon_i, lat_i = cols.index("id"), cols.index("lon"), cols.index("lat")
    for r in rows:
        assert r[id_i] and r[lon_i] is not None and r[lat_i] is not None, r
