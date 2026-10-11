"""The page as the user sees it: it loads, and what it shows agrees with the fit documents on disk.

Drives the real server (conftest) against a temp copy of the tree; no network, ephemeral port.
"""
import json
import os
import urllib.request

from conftest import get, get_json, put_json

C = {"id", "name", "lon", "lat", "corners", "size_m", "drawings"}  # every built site has exactly these at least


def test_page_loads(served):
    base, _ = served
    status, body = get(base + "/")
    assert status == 200
    assert b"Ancient Works" in body
    assert b"maplibre" in body  # the vendored map library the page builds on


def test_sites_data(served):
    base, _ = served
    status, data = get_json(base + "/data/sites.json")
    assert status == 200
    sites = data["sites"]
    # 384 built sites as of the plan (2026-10-10); the map only grows
    assert len(sites) >= 384
    for s in sites:
        assert C <= set(s), s["id"]
        assert isinstance(s["drawings"], int) and s["drawings"] >= 0
        assert len(s["corners"]) == 4
    # the 25 fitted drawings are the human's: they never disappear
    assert sum(s["drawings"] for s in sites) >= 25


def test_hand_fits_are_the_reference(served, golden_sites):
    """Golden: every site of an existing hand fit still has its fitted drawing (and, where the site's
    files are in this checkout, the matching overlay entry in its depictions.json)."""
    base, tree = served
    _, data = get_json(base + "/data/sites.json")
    by_id = {s["id"]: s for s in data["sites"]}
    assert set(golden_sites) <= set(by_id), sorted(set(golden_sites) - set(by_id))
    for sid in golden_sites:
        assert by_id[sid]["drawings"] >= 1, sid
        dep_path = os.path.join(tree, "web", "data", "sites", sid, "depictions.json")
        if os.path.exists(dep_path):  # per-site images are rebuilt by the pipeline; not every checkout has all
            deps = json.load(open(dep_path))["depictions"]
            assert any(d.get("kind") in ("plan", "view") and (d.get("fit") or {}).get("doc", "").startswith(sid + ".")
                       for d in deps), sid


def test_platefits_docs_match_sites(served):
    """Every fit document in the store points at a built site: no orphan fits the page would have to render."""
    base, tree = served
    _, data = get_json(base + "/data/sites.json")
    ids = {s["id"] for s in data["sites"]}
    db = os.path.join(tree, "data", "db", "platefits")
    docs = [json.load(open(os.path.join(db, f))) for f in sorted(os.listdir(db)) if f.endswith(".json")]
    assert docs
    for d in docs:
        assert d["site"] in ids, d
        assert d.get("plan") and d.get("pairs"), d.get("site")


def test_document_store_roundtrip(served):
    """The page's document store (the fit tool saves through it): write, read back, delete.
    Uses a scratch collection, never platefits, so no overlay side effects."""
    base, _ = served
    status, body = put_json(base + "/api/db/awtest/t1", {"a": 1})
    assert status == 200
    assert json.loads(body) == {"ok": True}
    status, doc = get_json(base + "/api/db/awtest/t1")
    assert status == 200 and doc == {"a": 1}
    req = urllib.request.Request(base + "/api/db/awtest/t1", method="DELETE")
    assert urllib.request.urlopen(req).status == 200
    try:
        get_json(base + "/api/db/awtest/t1")
        raise AssertionError("expected 404 after delete")
    except Exception as e:
        assert getattr(e, "code", None) == 404
