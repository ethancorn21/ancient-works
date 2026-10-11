"""The one-site line (task 300): tools/site_done.py, end to end, hermetic.

The command takes one site through every remaining step - fit the pictures not fitted
yet, sync each fit document to the map, refresh the site's entry in web/data/sites.json,
publish the review queue - and this test runs it on a COPY of Stonehenge's files in the
system temp dir, with the site stripped back to pre-sync (no plan overlay, drawings 0),
so the whole line runs and every output is checked. No network: the subprocess's sockets
are patched to fail loudly, and the big pictures it would otherwise download from
Wikimedia Commons are pre-seeded as flat-colour JPEGs at the exact dimensions of the
real cache files (data/raw/commons/big/<plan>.jpg, read through this checkout's committed
data/raw symlink - the same store the batch tests link into their throwaway trees). The
fit is a similarity transform over the document's point pairs, which depends only on
those dimensions, not on the pixels, so the run reproduces the repository's synced state
exactly. What is checked: exit 0 and the per-picture report (synced / review queue /
skipped, as docs/site_flow.md promises); the site's depictions.json and sites.json
byte-identical to the repository's (the automatic fit is an overlay exactly like a hand
fit, and the entry's drawings count colours the site's square on the map); the review
page recomputed over the whole copied queue equal to the published one; every other
site's item file and every platefit document byte-identical (a one-site run touches only
that site's files); and nothing in this checkout changed. Then a second run: every
document "skipped: overlay already current", all files still byte-identical (the line
is idempotent). The preconditions are pinned like test_batch_us pins its sample: today
Stonehenge's 13 candidate pictures are all covered (7 automatic fit documents + 6
candidates in its review item, disjoint), so no batch run (no model, no network) is
needed; if plans.json or the queue changes for Stonehenge the preconditions fail loudly
and this test must be extended on purpose.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SID = "stonehenge-q39671"

# The subprocess guard: every socket dies loudly, then the copied command runs exactly
# as `tools/site_done.py <site>` would (runpy with run_name="__main__" executes its
# __main__ block; site_done resolves its data root from its own path, so the COPYED
# code runs on the COPYED data, never on this checkout).
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
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _key(p):
    """The file's identity in a hash map: repo-relative inside this checkout, absolute in the temp tree."""
    p = Path(p)
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def _hash_all(paths):
    """Hash every file under the given paths (files directly, directories one level deep -
    every data dir here is flat): the proof the run wrote nothing outside the tree."""
    out = {}
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for f in sorted(p.iterdir()):
                if f.is_file():
                    out[_key(f)] = _h(f)
        else:
            out[_key(p)] = _h(p)
    return out


def _docs():
    """The site's platefit documents in this checkout, by plan id."""
    out = {}
    for p in sorted((ROOT / "data" / "db" / "platefits").glob(SID + ".*.json")):
        doc = json.loads(p.read_text())
        out[doc["plan"]] = doc
    return out


def _item():
    """The site's review item (path, dict) in this checkout, keyed by its site field."""
    for p in sorted((ROOT / "data" / "review").glob("*.json")):
        item = json.loads(p.read_text())
        if item.get("site") == SID:
            return p, item
    return None, None


def _rows():
    """The site's candidate pictures: the web/data/plans.json rows naming it (batch_us' own view)."""
    d = json.loads((ROOT / "web" / "data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(d["cols"])}
    rows = [{k: r[i] for k, i in cols.items()} for r in d["rows"]]
    return [r for r in rows if SID in (r.get("sites") or [])]


def _seed_big(tree, docs):
    """The flat-colour stand-ins for the Commons big pictures, at the real images' dimensions."""
    big = tree / "data" / "raw" / "commons" / "big"
    big.mkdir(parents=True)
    for i, (plan, doc) in enumerate(sorted(docs.items())):
        real = ROOT / "data" / "raw" / "commons" / "big" / (plan + ".jpg")
        if not real.is_file():
            pytest.fail(f"data/raw/commons/big/{plan}.jpg is missing: the data/raw image store "
                        "is not available on this machine (the batch tests link the same store)")
        with Image.open(real) as im:
            size = im.size  # the header only: the pixels never enter a similarity fit
        color = (i * 30 % 250, i * 50 % 250, 200)
        Image.new("RGB", size, color).save(big / (plan + ".jpg"), quality=92)


def _build_tree(tmp_path, docs):
    """The throwaway tree: the code, the site's data stripped to pre-sync, the rest of the
    world (the review queue, every fit document, the full sites.json) copied whole."""
    tree = tmp_path / "tree"
    for d in ("tools", "fit", "pipeline"):
        shutil.copytree(ROOT / d, tree / d, ignore=shutil.ignore_patterns("__pycache__"))
    wd = tree / "web" / "data"
    wd.mkdir(parents=True)
    shutil.copy2(ROOT / "web" / "data" / "plans.json", wd / "plans.json")
    shutil.copy2(ROOT / "web" / "data" / "review.json", wd / "review.json")
    index = json.loads((ROOT / "web" / "data" / "sites.json").read_text())
    for s in index["sites"]:
        if s["id"] == SID:
            s["drawings"] = 0  # pre-sync: the entry gains its drawings from this run
    (wd / "sites.json").write_text(json.dumps(index, indent=1))
    shutil.copytree(ROOT / "data" / "review", tree / "data" / "review")
    shutil.copytree(ROOT / "data" / "db" / "platefits", tree / "data" / "db" / "platefits")
    src = ROOT / "web" / "data" / "sites" / SID
    dst = tree / "web" / "data" / "sites" / SID
    dst.mkdir(parents=True)
    for f in src.iterdir():
        if f.name.startswith("plan_") and f.suffix == ".webp":
            continue  # the plan overlays: the sync recreates them
        shutil.copy2(f, dst / f.name)
    deps = json.loads((src / "depictions.json").read_text())
    deps["depictions"] = [d for d in deps["depictions"] if d.get("kind") not in ("plan", "view")]
    (dst / "depictions.json").write_text(json.dumps(deps, indent=1))
    _seed_big(tree, docs)
    return tree


def _run(tree):
    """The command on the tree: `tools/site_done.py <site>` (copied code, copied data), no model."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-c", GUARD, str(tree / "tools" / "site_done.py"), SID],
                          cwd=str(tree), env=env, capture_output=True, timeout=600)


def test_site_done_line(tmp_path):
    docs = _docs()
    item_path, item = _item()
    rows = _rows()
    n_docs = len(docs)
    n_item = len((item or {}).get("candidates") or [])
    n_rows = len(rows)
    n_doc_rows = sum(1 for r in rows if r["id"] in docs)
    item_plans = {c.get("plan") for c in (item or {}).get("candidates") or []}
    # the pinned preconditions: every candidate picture covered (a doc or the item), the
    # document/item sets disjoint and both inside plans.json, so the line needs no batch run
    if item is None or n_doc_rows != n_docs or n_rows != n_docs + n_item \
            or not item_plans <= {r["id"] for r in rows}:
        pytest.fail("Stonehenge's candidate pictures are no longer fully covered by its fit "
                    "documents and review item (the no-batch-run precondition is void): "
                    f"{n_rows} rows, {n_docs} docs, {n_item} in the item")

    checkout = [ROOT / "web" / "data" / "sites.json",
                ROOT / "web" / "data" / "review.json",
                ROOT / "web" / "data" / "sites" / SID,
                ROOT / "data" / "review",
                ROOT / "data" / "db" / "platefits"]
    checkout += [ROOT / "data" / "raw" / "commons" / "big" / (plan + ".jpg") for plan in docs]
    before = _hash_all(checkout)

    tree = _build_tree(tmp_path, docs)
    proc = _run(tree)
    out = proc.stdout.decode("utf-8")
    err = proc.stderr.decode("utf-8")
    assert proc.returncode == 0, out + err
    assert err == ""
    site = tree / "web" / "data" / "sites" / SID

    # the per-picture report, exactly as the line prints it
    assert f"fit  {n_rows} candidate picture(s): {n_docs} fitted (doc), " \
           f"{n_item} in the review item -> no batch run needed" in out
    for plan, doc in docs.items():
        assert f"({plan}): synced to the map" in out
    assert out.count("sent to the review queue") == n_item
    assert f"entry  web/data/sites.json: drawings 0 -> {n_docs}" in out
    n_open = len(json.loads((ROOT / "web" / "data" / "review.json").read_text())["items"])
    n_total = len(list((ROOT / "data" / "review").glob("*.json")))
    assert f"review {item_path.name}: {n_item} candidate(s), open; " \
           f"page now has {n_open} open of {n_total} items" in out
    assert out.splitlines()[-1] == "done"

    # the overlay and the entry: byte-identical to the repository's synced state
    assert (site / "depictions.json").read_bytes() == \
        (ROOT / "web" / "data" / "sites" / SID / "depictions.json").read_bytes()
    assert (tree / "web" / "data" / "sites.json").read_bytes() == \
        (ROOT / "web" / "data" / "sites.json").read_bytes()
    expected = {f"plan_{p}.webp" for p in docs} | {f"plan_{p}_ink.webp" for p in docs}
    assert {f.name for f in site.iterdir() if f.name.startswith("plan_")} == expected
    for f in site.iterdir():
        if f.name.startswith("plan_"):
            assert f.stat().st_size > 0

    # the review page recomputed over the whole copied queue is the published queue
    tr = json.loads((tree / "web" / "data" / "review.json").read_text())
    rr = json.loads((ROOT / "web" / "data" / "review.json").read_text())
    assert tr["items"] == rr["items"]
    sh = [i for i in tr["items"] if i["site"] == SID]
    assert len(sh) == 1 and [c["plan"] for c in sh[0]["candidates"]] == \
        [c["plan"] for c in item["candidates"]]

    # a one-site run touches only that site's files: no other item, no document, changed
    for name in sorted(set(os.listdir(tree / "data" / "review")) | set(os.listdir(ROOT / "data" / "review"))):
        assert _h(tree / "data" / "review" / name) == _h(ROOT / "data" / "review" / name), name
    for name in sorted(set(os.listdir(tree / "data" / "db" / "platefits")) |
                      set(os.listdir(ROOT / "data" / "db" / "platefits"))):
        assert _h(tree / "data" / "db" / "platefits" / name) == _h(ROOT / "data" / "db" / "platefits" / name), name
    assert _hash_all(checkout) == before  # and the checkout itself is untouched

    # a second run: nothing to do, nothing to change
    hashes = _hash_all([site, tree / "web" / "data" / "sites.json",
                        tree / "web" / "data" / "review.json"])
    proc2 = _run(tree)
    out2 = proc2.stdout.decode("utf-8")
    assert proc2.returncode == 0, out2 + proc2.stderr.decode("utf-8")
    assert out2.count("skipped: overlay already current") == n_docs
    assert f"entry  web/data/sites.json: drawings {n_docs} -> {n_docs}" in out2
    assert out2.splitlines()[-1] == "done"
    # review.json carries a fresh timestamp; compare everything but that
    review_key = _key(tree / "web" / "data" / "review.json")
    h2 = _hash_all([site, tree / "web" / "data" / "sites.json"])
    assert h2 == {k: v for k, v in hashes.items() if k != review_key}
    tr2 = json.loads((tree / "web" / "data" / "review.json").read_text())
    assert tr2["items"] == rr["items"]
    assert _hash_all(checkout) == before
