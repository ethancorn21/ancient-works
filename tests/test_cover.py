"""Cover search (task 212a, GOAL.md point 1): fit/cover.py's fetch -> search -> stage -> nopicture, hermetic.

Every phase is driven in-process against a throwaway tree of this checkout (web/ data/ docs/ specs/
tests/ hard-linked, near-zero disk), so nothing the phase writes can reach the checkout: the three
files the phases rewrite in place (web/data/plans.json, data/commons/files.jsonl,
data/commons/classified.jsonl) are real copies, data/raw is a REAL directory of hard links to the
shared image store (the phases write new picture copies into it - new inodes, never the store's),
and every other write the phases make is an atomic tmp+os.replace new inode. web/data/sites/<id>
are skipped (the 212a phases never touch them; the parent task's sync phase flips include_sites).

No network: every network route the phases use is a recorded fake (a pure function of its inputs),
and a socket guard fails loudly on any connection attempt. The one site the fake search answers for
(the first qid site of the search set, computed at run time) gets four category files - two kept
(1701/1850, one of them the site's P3311 plan and a P180 depiction of the site's item), one made in
2010 (kept out by the 1925 cut-off), one a video (kept out by the mime filter); every other site's
search answers nothing. The two kept pictures are staged the normal way (files.jsonl + classified
rows, local copies, plans.json) and every remaining search-set site gets its "no picture found"
review item with exactly what was searched. The fit itself is NOT this task: the loop/sync/report
phases (212b/212c) extend this same file (the seams: PHASES, include_sites).

After all phases the checkout is byte-identical (sha256 of data/ minus data/raw, web/data top level,
docs/ specs/ tests/) and the shared store gained nothing for the fake site.
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fit"))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import commons  # noqa: E402  (the patched module: wd_claims/files_of/search/info, OUT/RAW)
import cover  # noqa: E402  (the phases under test; its module-level imports pull evidence/export_plans)
import evidence  # noqa: E402  (the patched module: the P180 fetchers)
import export_plans  # noqa: E402  (the module _regen_plans re-points)
from PIL import Image  # noqa: E402

# the shared image store (the target of the checkout's data/raw symlink)
STORE = os.path.realpath(os.path.join(ROOT, "data", "raw"))

# The 212a phase sequence (the parent task extends this: loop, sync, export, report).
PHASES = ["fetch", "search", "stage", "nopicture"]

# The files the 212a phases rewrite in place (open("a") appends and export_plans' open("w")):
# real copies in the tree, or the write would land in this checkout through the hard link.
IN_PLACE = {"web/data/plans.json", "data/commons/files.jsonl", "data/commons/classified.jsonl"}

# The injected classifier's answer for every staged row (a confident plan, aligned with the todo list).
FAKE_SCORES = {"p_plan": 0.9, "p_birdseye": 0.1, "p_photo": 0.1}


def _sha16(t):
    return hashlib.sha1(t.encode("utf-8")).hexdigest()[:16]


def _iso(ts):
    return datetime.fromisoformat(ts)


class Fakes:
    """The recorded search response: pure functions of their inputs (no network, no clock, no disk
    state). One site - the test's hit, chosen in build_world - gets a category with four files and a
    P3311/P180 answer for the first of them; everything else answers nothing (a failure site, if the
    no-qid-with-title set is ever non-empty again, raises on its title search and the phase records
    the failure instead of hiding it)."""

    def __init__(self, hit_sid, site, fail_name=None):
        self.hit_sid = hit_sid
        self.qid = site["qid"]
        self.name = site["name"]
        self.t_plan = "File:Plan of %s (c. 1701).jpg" % self.name
        self.t_view = "File:View of %s (c. 1850).jpg" % self.name
        self.t_new = "File:Photo of %s (c. 2010).jpg" % self.name        # kept out: made in 2010
        self.t_video = "File:Flyover of %s (c. 1900).webm" % self.name    # kept out: a video
        self.cat = "Fake category of %s" % self.name
        self.fail_name = fail_name
        self._meta = {t: self.meta(t, date="2010-05-01T00:00:00Z" if t == self.t_new else "")
                      for t in (self.t_plan, self.t_view, self.t_new)}
        self._meta[self.t_video] = self.meta(self.t_video, mime="video/mp4")

    def meta(self, t, date="", mime="image/jpeg"):
        h = _sha16(t)
        return {
            "url": "https://upload.wikimedia.org/wikipedia/commons/%s/%s" % (h[0], h),
            "thumb": "https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/1280px-%s" % (h[0], h, h),
            "w": 1280, "h": 960, "mime": mime, "date": date,
            "desc": "", "artist": "", "license": "",
            "page": "https://commons.wikimedia.org/wiki/%s" % t,
        }

    def wd_claims(self, qids):
        out = {}
        for q in qids:
            if q == self.qid:
                out[q] = {"cat": self.cat, "plan": [self.t_plan[5:]], "image": []}
            else:
                out[q] = {"cat": None, "plan": [], "image": []}
        return out

    def files_of(self, cat, depth=2, seen=None):
        if cat == self.cat:
            return [self.t_plan, self.t_view, self.t_new, self.t_video]
        return []

    def search(self, name):
        if name == self.name:
            return [self.t_plan, self.t_view]
        if self.fail_name is not None and name == self.fail_name:
            raise RuntimeError("429 Too Many Requests (the recorded failure)")
        return []

    def info(self, titles):
        # the four fake titles know their own meta; anything else (the fetch phase's url-only rows)
        # gets a generic fetchable picture
        return {t: self._meta.get(t) or self.meta(t) for t in titles}

    def fetch_page_ids(self, titles):
        return {t: 1000 + i for i, t in enumerate(titles)}

    def fetch_file_entities(self, page_ids):
        return {t: {"item": "M%d" % pid, "p180": [self.qid] if t == self.t_plan else []}
                for t, pid in page_ids.items()}

    def fetch_one(self, url, dst):
        # a valid solid-colour 1280x960 JPEG (export_plans PIL-opens every local copy it exports)
        h = int(hashlib.sha1(url.encode("utf-8")).hexdigest()[:6], 16)
        im = Image.new("RGB", (1280, 960), ((h >> 16) & 255, (h >> 8) & 255, h & 255))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im.save(dst, "JPEG")
        return True

    def classify(self, rows):
        return [dict(FAKE_SCORES) for _ in rows]

    def install(self, saved):
        saved["commons.wd_claims"] = commons.wd_claims
        saved["commons.files_of"] = commons.files_of
        saved["commons.search"] = commons.search
        saved["commons.info"] = commons.info
        saved["evidence.fetch_page_ids"] = evidence.fetch_page_ids
        saved["evidence.fetch_file_entities"] = evidence.fetch_file_entities
        saved["cover._fetch_one"] = cover._fetch_one
        saved["time.sleep"] = commons.time.sleep
        commons.wd_claims = self.wd_claims
        commons.files_of = self.files_of
        commons.search = self.search
        commons.info = self.info
        evidence.fetch_page_ids = self.fetch_page_ids
        evidence.fetch_file_entities = self.fetch_file_entities
        cover._fetch_one = self.fetch_one
        commons.time.sleep = lambda *a, **k: None  # cover.time IS the global time module: kill the pacing

    def restore(self, saved):
        commons.wd_claims = saved["commons.wd_claims"]
        commons.files_of = saved["commons.files_of"]
        commons.search = saved["commons.search"]
        commons.info = saved["commons.info"]
        evidence.fetch_page_ids = saved["evidence.fetch_page_ids"]
        evidence.fetch_file_entities = saved["evidence.fetch_file_entities"]
        cover._fetch_one = saved["cover._fetch_one"]
        commons.time.sleep = saved["time.sleep"]


def _no_network(saved):
    """The socket guard: any connection attempt - by a phase route the fakes missed - fails loudly
    instead of touching the network. Held from the baseline re-export to the last phase."""
    def guard(*a, **k):
        raise AssertionError("the 212a test never opens a socket: %r" % (a[:2],))
    saved["socket.create_connection"] = socket.create_connection
    saved["socket.socket.connect"] = socket.socket.connect
    socket.create_connection = guard
    socket.socket.connect = guard


def _network_again(saved):
    if "socket.create_connection" in saved:
        socket.create_connection = saved.pop("socket.create_connection")
        socket.socket.connect = saved.pop("socket.socket.connect")


# ---------------------------------------------------------------- the world (state-aware)

def build_world():
    """Measure the checkout's live state ONCE (the tree is a byte-copy, so checkout values == tree
    values pre-run). Fails loudly on a precondition the design needs, instead of drifting."""
    sites = cover._sites(ROOT)
    nofit = cover._no_fit_sites(ROOT)
    cand = cover._cand_sites(ROOT)
    ss = cover._search_set(ROOT)
    assert ss, "the search set is empty - 212a has nothing to search"

    qid_sites = [s for s in ss if sites[s].get("qid")]
    assert qid_sites, "no qid site in the search set - the fake has no hit to answer for"
    hit = qid_sites[0]  # the fake's hit: the first qid search-set site, sorted
    site = sites[hit]
    name = site.get("name") or hit
    assert site.get("qid"), "the hit site must have a qid (the fake answers its P373/P3311)"
    assert '"' not in name, "the fake titles use the site name verbatim"

    fakes = Fakes(hit, site)
    files = cover._files_rows(ROOT)
    titles = {r["title"] for r in files if r.get("title")}
    for t in (fakes.t_plan, fakes.t_view, fakes.t_new, fakes.t_video):
        assert t not in titles, "the fake title %s is already in files.jsonl" % t
    for t in (fakes.t_plan, fakes.t_view):  # both pass the 1925 cut-off with the fake meta
        assert commons.keep(t, fakes.meta(t)), "the fake kept title %s must pass commons.keep" % t

    # D1 (the parent's design): the failure site is the first no-qid search-set site with an existing
    # files.jsonl title; when that set is empty every record's failed must be empty.
    fail_site = next((s for s in ss if not sites[s].get("qid")
                      and any(r.get("site") == s and r.get("title") for r in files)), None)
    if fail_site:
        fakes.fail_name = (sites[fail_site].get("name") or fail_site).replace('"', "")

    # the kept titled rows: who has a local copy, and who is fetchable (the fetch phase's work)
    kept = []
    for r in files:
        if r.get("title") and commons.keep(r["title"], r):
            p = cover._local_path(ROOT, r["site"], r["title"])
            kept.append({"row": r, "has_copy": p.exists(),
                         "fetchable": bool(r.get("thumb") or r.get("url")),
                         "thumb": bool(r.get("thumb"))})
    n_have = sum(1 for k in kept if k["has_copy"])
    n_nosrc = sum(1 for k in kept if not k["has_copy"] and not k["fetchable"])
    n_thumb = sum(1 for k in kept if not k["has_copy"] and k["fetchable"] and k["thumb"])
    n_url = sum(1 for k in kept if not k["has_copy"] and k["fetchable"] and not k["thumb"])

    # the committed plans.json (the pure-growth baseline) and every item file
    plans = json.loads((Path(ROOT) / "web/data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(plans["cols"])}
    keys = {(r[cols["id"]], (r[cols["sites"]] or [None])[0]) for r in plans["rows"]}
    items = {}
    d = Path(ROOT) / "data" / "review"
    for p in sorted(d.iterdir()) if d.is_dir() else []:
        if p.suffix != ".json":
            continue
        it = json.loads(p.read_text())
        if it.get("site"):
            items[str(p)] = {"item": it, "bytes": p.read_bytes()}

    return {
        "sites": sites, "nofit": nofit, "cand": cand, "ss": ss, "hit": hit,
        "qid_sites": qid_sites, "noqid_sites": [s for s in ss if not sites[s].get("qid")],
        "fakes": fakes, "kept": kept,
        "n_have": n_have, "n_nosrc": n_nosrc, "n_thumb": n_thumb, "n_url": n_url,
        "fail_site": fail_site,
        "plans_committed": plans, "keys_committed": keys, "items": items,
        "files_bytes": (Path(ROOT) / "data" / "commons" / "files.jsonl").read_bytes(),
        "classified_bytes": (Path(ROOT) / "data" / "commons" / "classified.jsonl").read_bytes(),
        "plans_bytes": (Path(ROOT) / "web" / "data" / "plans.json").read_bytes(),
    }


# ---------------------------------------------------------------- the tree

def _link_dir(src, dst, skip=(), in_place=None, follow=()):
    """Hard-link every file of src into dst (new directory inodes, shared file inodes); a symlink is
    re-linked, never followed, unless its name is in `follow` (then its target is walked). `skip` holds
    paths relative to src whose subtree is neither linked nor walked. Writes the phases make in dst
    are new inodes and never touch the originals."""
    skip = set(skip)
    os.makedirs(dst, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        d = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(d, exist_ok=True)
        for name in list(dirnames):
            s = os.path.join(dirpath, name)
            if os.path.relpath(s, src) in skip:
                dirnames.remove(name)  # not linked, not walked
                continue
            if os.path.islink(s):
                if name in follow:  # a symlinked subtree that must be a real (linked) tree here
                    _link_dir(os.path.realpath(s), os.path.join(d, name), skip, in_place, ())
                else:
                    os.symlink(os.readlink(s), os.path.join(d, name))
                continue
        for name in filenames:
            s = os.path.join(dirpath, name)
            if name.endswith((".npy", ".npz")):
                continue
            t = os.path.join(d, name)
            if os.path.islink(s):
                os.symlink(os.readlink(s), t)
            elif in_place is not None and os.path.relpath(s, ROOT) in in_place:
                shutil.copy2(s, t)
            else:
                os.link(s, t)


def build_tree(tree, include_sites=False):
    """The throwaway tree (D3, 212a-scoped): web/ data/ docs/ specs/ tests/ hard-linked (the 3 in-place
    files copied); data/raw a REAL directory of hard links to the shared store (the phases write new
    copies into it - never the store's); web/data/sites/<id> skipped unless include_sites (the parent's
    sync needs them; the 212a phases never open them - an empty dir is left, as before)."""
    for top in ("web", "data", "docs", "specs", "tests"):
        skip = set()
        if top == "data":
            skip.add("raw")  # rebuilt from the store as a real directory below
        if top == "web" and not include_sites:
            skip.add("data/sites")
        _link_dir(os.path.join(ROOT, top), os.path.join(tree, top), skip=skip, in_place=IN_PLACE)
    if not include_sites:
        os.makedirs(os.path.join(tree, "web", "data", "sites"), exist_ok=True)
    # data/raw: a real directory of hard links to the store (every file, new inodes for new writes)
    raw = os.path.join(tree, "data", "raw")
    _link_dir(STORE, raw)
    # the live run (later) leaves data/cover/searches.json in the checkout; the search phase skips
    # already-recorded sites, which would hide the fake hit - drop it in the tree (the live file keeps
    # its own inode: the unlink removes only the tree's directory entry)
    rec = os.path.join(tree, "data", "cover", "searches.json")
    if os.path.exists(rec):
        os.unlink(rec)
    return tree


def checkout_hashes():
    """sha256 of everything the phases could leak through a hard link: data/ (the data/raw symlink
    skipped - the store is shared and other agents write to it), the web/data top-level files (the
    per-site dirs are store views the 212a phases never touch), docs/ specs/ tests/."""
    out = {}
    for top in ("data", "docs", "specs", "tests"):
        base = os.path.join(ROOT, top)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [n for n in sorted(dirnames)
                           if n != "__pycache__"
                           and not (top == "data" and os.path.join(dirpath, n) == os.path.join(ROOT, "data", "raw"))]
            for n in sorted(filenames):
                if n.endswith((".npy", ".npz")):
                    continue
                p = os.path.join(dirpath, n)
                if os.path.islink(p):
                    continue
                with open(p, "rb") as f:
                    out[os.path.relpath(p, ROOT)] = hashlib.sha256(f.read()).hexdigest()
    for n in sorted(os.listdir(os.path.join(ROOT, "web", "data"))):
        p = os.path.join(ROOT, "web", "data", n)
        if os.path.isfile(p):
            with open(p, "rb") as f:
                out["web/data/" + n] = hashlib.sha256(f.read()).hexdigest()
    return out


# ---------------------------------------------------------------- the expected values

def expected_record(sid, site, world, fakes):
    """The per-site record the search phase must write, field for field (the date is checked
    separately: it is the run's clock)."""
    qid = site.get("qid")
    name = (site.get("name") or sid).replace('"', "")
    rec = {
        "site": sid,
        "name": site.get("name") or sid,
        "qid": qid or "no qid",
        "cat": "none",
        "n_cat_files": 0,
        "n_p180": 0,
        "n_p180_gathered": 0,
        "title_queries": [q.format(n=name) for q in commons.SEARCHES],
        "n_title_hits": 0,
        "n_gathered": 0,
        "n_kept": 0,
        "new": [],
        "failed": [],
    }
    if sid == world["hit"]:
        rec.update({
            "cat": fakes.cat, "n_cat_files": 4, "n_p180": 1, "n_p180_gathered": 4,
            "n_title_hits": 2, "n_gathered": 4, "n_kept": 2,
            "new": [
                # the plan file is gathered by every route: the category, the P3311 claims, the P180
                # re-test and the title search (tags accumulate, sorted on the record)
                {"title": fakes.t_plan, "via": ["cat", "claims", "p180", "title"], "wd_plan": True,
                 "meta": fakes.meta(fakes.t_plan)},
                {"title": fakes.t_view, "via": ["cat", "title"], "wd_plan": False,
                 "meta": fakes.meta(fakes.t_view)},
            ],
        })
    if world["fail_site"] == sid:
        rec["failed"] = ["title search: 429 Too Many Requests (the recorded failure)"]
    return rec


def expected_searched(rec):
    """The record as the human reads it on the page - the 212a contract for no_picture_found.searched
    (mirrors fit/cover.py::_searched_string; the two spot-checked sites in test_nopicture pin the
    wording literally, so a drift in either copy fails)."""
    qid = rec.get("qid") or "no qid"
    parts = ["wikidata %s" % qid] if qid != "no qid" else ["no wikidata item"]
    if rec.get("cat") and rec["cat"] != "none":
        parts.append("Commons category '%s' (%d file%s)" % (
            rec["cat"], rec["n_cat_files"], "" if rec["n_cat_files"] == 1 else "s"))
    else:
        parts.append("no Commons category")
    if qid != "no qid":
        parts.append("P180 depictions of %s: %d of %d file(s) checked" % (
            qid, rec["n_p180"], rec["n_p180_gathered"]))
    parts.append("title searches: %s (%d hit%s)" % (
        ", ".join('"%s"' % q for q in rec["title_queries"]),
        rec["n_title_hits"], "" if rec["n_title_hits"] == 1 else "s"))
    if rec.get("failed"):
        parts.append("FAILED routes: " + "; ".join(rec["failed"]))
    parts.append(rec["date"][:10])
    return "; ".join(parts)


def planned_row(hit, t, name, when, fakes):
    """The exact plans.json row the stage phase's re-export must write for a staged picture
    (tools/export_plans.py::commons_rows, field for field), as a dict over the writer's 13 cols:
    for a commons row title holds the picture's name, label its when, ref the File: title."""
    meta = fakes.meta(t)
    cite = meta["page"]  # artist/license empty in the fake: only the page survives
    return {"id": "c_" + _sha16(t), "book": "Wikimedia Commons", "ia": None, "file": None,
            "title": name, "label": when, "size": [1280, 960], "map_box": None,
            "sites": [hit], "cite": cite, "url": "media/commons/%s/%s.jpg" % (hit, _sha16(t)),
            "view": False, "ref": t}


# ---------------------------------------------------------------- the run

@pytest.fixture(scope="module")
def tmp_path_retention_policy():
    # the tree is hard-linked (near-zero disk), but keep only failed runs: the 48 GB box
    return "failed"


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    """Build the tree, run the 212a phases once (fetch -> search -> stage -> nopicture) under the
    fakes, re-run search/stage/nopicture for the resumability checks, and hand back every state the
    assertions need (before/after snapshots, stdout per phase, the records)."""
    world = build_world()
    fakes = world["fakes"]
    tree = str(tmp_path_factory.mktemp("cover212a"))
    build_tree(tree, include_sites=False)

    before = {
        "plans_bytes": (Path(tree) / "web" / "data" / "plans.json").read_bytes(),
        "files_bytes": (Path(tree) / "data" / "commons" / "files.jsonl").read_bytes(),
        "classified_bytes": (Path(tree) / "data" / "commons" / "classified.jsonl").read_bytes(),
        "searches_bytes": None,
        "items": _tree_items(tree),  # tree paths: the same key space as after["items"]
        "checkout": checkout_hashes(),
    }
    assert before["plans_bytes"] == world["plans_bytes"], "the tree's plans.json must be a byte-copy"

    saved = {}
    out = {"tree": tree, "world": world, "fakes": fakes, "before": before,
           "stdout": {}, "n": {}, "records": None}
    _no_network(saved)  # from here on (the baseline re-export included): no network on any route
    try:
        # the baseline re-export of the PRISTINE tree: what this machine's export produces before
        # any phase (the key-set arithmetic below is measured against it, so machine drift in the
        # store reads as explainable environment, not a phase bug)
        with contextlib.redirect_stdout(io.StringIO()):
            cover._regen_plans(tree)
        out["keys_baseline"] = _plans_keys(tree)
        (Path(tree) / "web" / "data" / "plans.json").write_bytes(before["plans_bytes"])  # restore the committed file

        fakes.install(saved)
        for phase in PHASES:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                if phase == "fetch":
                    out["n"]["fetch"] = cover.fetch(tree)
                elif phase == "search":
                    out["ss_at_search"] = cover._search_set(tree)
                    out["records"] = cover.search(tree)
                elif phase == "stage":
                    out["n"]["staged"] = cover.stage(tree, classifier=fakes.classify, live=False)
                elif phase == "nopicture":
                    out["n"]["marked"] = cover.nopicture(tree)
            out["stdout"][phase] = buf.getvalue()
            if phase in ("fetch", "stage"):  # the key set right after this phase's own re-export
                out["keys_after_" + phase] = _plans_keys(tree)

        # resumability: search re-runs nothing (everything recorded), stage re-stages nothing,
        # nopicture re-marks the same items (the at-timestamp re-stamp is the 201 contract)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out["records2"] = cover.search(tree)
        out["stdout"]["search2"] = buf.getvalue()
        out["searches_bytes_after_first"] = (Path(tree) / "data" / "cover" / "searches.json").read_bytes()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out["n"]["staged2"] = cover.stage(tree, classifier=fakes.classify, live=False)
        out["stdout"]["stage2"] = buf.getvalue()
        out["files_bytes_after_stage"] = (Path(tree) / "data" / "commons" / "files.jsonl").read_bytes()
        out["classified_bytes_after_stage"] = (Path(tree) / "data" / "commons" / "classified.jsonl").read_bytes()
        out["plans_bytes_after_stage"] = (Path(tree) / "web" / "data" / "plans.json").read_bytes()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out["n"]["marked2"] = cover.nopicture(tree)
        out["stdout"]["nopicture2"] = buf.getvalue()
    finally:
        if "commons.wd_claims" in saved:
            fakes.restore(saved)
        _network_again(saved)

    after = {
        "searches_bytes": (Path(tree) / "data" / "cover" / "searches.json").read_bytes(),
        "items": _tree_items(tree),
        "checkout": checkout_hashes(),
    }
    out["after"] = after
    out["store_hit_dir"] = os.path.join(STORE, "commons", world["hit"])
    return out


def _tree_items(tree):
    """{path: bytes} of every item file in the tree's data/review - the before/after snapshots
    (tree paths, so the two key sets match)."""
    d = Path(tree) / "data" / "review"
    if not d.is_dir():
        return {}
    return {str(p): p.read_bytes() for p in sorted(d.iterdir()) if p.suffix == ".json"}


def _plans_keys(tree):
    d = json.loads((Path(tree) / "web" / "data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(d["cols"])}
    return {(r[cols["id"]], (r[cols["sites"]] or [None])[0]) for r in d["rows"]}


def _plans_rows(tree):
    d = json.loads((Path(tree) / "web" / "data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(d["cols"])}
    return [{k: r[i] for k, i in cols.items()} for r in d["rows"]]


def _load_searches(tree):
    return json.loads((Path(tree) / "data" / "cover" / "searches.json").read_text())


def _find_item(tree, sid):
    d = Path(tree) / "data" / "review"
    for p in sorted(d.iterdir()) if d.is_dir() else []:
        if p.suffix != ".json":
            continue
        it = json.loads(p.read_text())
        if it.get("site") == sid:
            return str(p), it
    return None, None


# ---------------------------------------------------------------- the assertions

def test_search_records(run):
    """(i) data/cover/searches.json: exactly the search set, every field of every record as the
    fakes' inputs determine it, and the re-run records nothing new (byte-identical, resumable)."""
    world, fakes = run["world"], run["fakes"]
    ss = run["ss_at_search"]
    recs = _load_searches(run["tree"])
    assert set(recs) == set(ss), "searches.json keys must be exactly the search set at search time"
    now = datetime.now(timezone.utc)
    for sid in ss:
        rec, exp = recs[sid], expected_record(sid, world["sites"][sid], world, fakes)
        assert rec["date"], "the record carries its date"
        assert abs((now - _iso(rec["date"])).total_seconds()) < 3600, rec["date"]
        assert {k: v for k, v in rec.items() if k != "date"} == exp, (
            "record for %s:\n got %r\n exp %r" % (sid, {k: v for k, v in rec.items() if k != "date"}, exp))
    if world["fail_site"]:
        pass  # the failed entry is in expected_record
    else:
        assert all(r["failed"] == [] for r in recs.values()), "no route failed, so no record may record one"
    # the hit's two new files, in sorted-title order, with their gather tags and the P3311 flag
    hit = recs[world["hit"]]
    assert [e["title"] for e in hit["new"]] == sorted([fakes.t_plan, fakes.t_view])
    # resumable: the re-run recorded nothing new and rewrote nothing
    assert recs == run["records2"], "the re-run must not change a record"
    assert run["after"]["searches_bytes"] == run["searches_bytes_after_first"], (
        "the search re-run must leave searches.json byte-identical")


def test_counts(run):
    """(ii) the stdout counts the phase contract promises: searched / found / nothing, per phase."""
    world, fakes = run["world"], run["fakes"]
    n = run["n"]
    s, ss = run["stdout"], run["ss_at_search"]

    f = s["fetch"].splitlines()
    # the fetch line is the product's own arithmetic over the kept rows: the no-source rows count in
    # "with a local copy" (neither fetched nor fetchable), and the fake fetch never fails
    exp = "fetch: %d row(s) with a local copy, %d without a source, fetched %d thumb(s) + %d url-only" % (
        world["n_have"] + world["n_nosrc"], world["n_nosrc"], world["n_thumb"], world["n_url"])
    assert f[0] == exp, "got %r exp %r" % (f[0], exp)
    assert n["fetch"] == world["n_thumb"] + world["n_url"]
    # the fetch phase's re-export reports the same row count the key set has
    assert any("%d plans," % len(run["keys_after_fetch"]) in line for line in f), s["fetch"]

    g = s["search"].splitlines()
    assert g[0] == "search: %d site(s) to search, 0 already recorded" % len(ss), g[0]
    assert g[-1] == "search: %d record(s) on file, 2 new file(s) for the stage phase" % len(ss), g[-1]
    hit_line = "search %s: 4 gathered, 2 kept old, 2 new (all routes answered)" % world["hit"]
    assert hit_line in s["search"], s["search"]
    other = [x for x in ss if x != world["hit"]]
    if other:
        assert "search %s: 0 gathered, 0 kept old, 0 new (all routes answered)" % other[0] in s["search"]

    assert "stage: 2 file(s) staged (2 classified) -> files.jsonl, classified.jsonl, plans.json" in s["stage"]
    assert "evidence recorded: 0 hand-tied, 0 book, 0 live" in s["stage"], (
        "live=False with by:212 must record no evidence (no source table, no live fetch)")

    marked = [x for x in ss if x != world["hit"]]
    assert s["nopicture"].strip().splitlines()[-1] == "nopicture: %d item(s) marked" % len(marked)


def test_stage(run):
    """(iii) the staged rows: files.jsonl gained exactly the two rows (original bytes preserved,
    appended), classified.jsonl the two classifier answers, local copies that PIL-opens at
    1280x960, and the plans.json re-export: pure growth over the committed keys (any loss or
    addition beyond the two new rows must be explainable by this machine's image store), the two
    new rows exact, and the re-run re-stages nothing."""
    world, fakes = run["world"], run["fakes"]
    hit = world["hit"]

    row1 = {"site": hit, "qid": world["sites"][hit]["qid"], "title": fakes.t_plan, "year": 1701,
            "wd_plan": True, "cat": fakes.cat, "by": "212", **fakes.meta(fakes.t_plan)}
    row2 = {"site": hit, "qid": world["sites"][hit]["qid"], "title": fakes.t_view, "year": 1850,
            "wd_plan": False, "cat": fakes.cat, "by": "212", **fakes.meta(fakes.t_view)}
    l1 = json.dumps(row1) + "\n"
    l2 = json.dumps(row2) + "\n"
    assert run["files_bytes_after_stage"] == run["before"]["files_bytes"] + l1.encode() + l2.encode(), (
        "files.jsonl must be the original bytes plus exactly the two staged rows, in order")
    c1 = json.dumps({"site": hit, "title": fakes.t_plan, **FAKE_SCORES}) + "\n"
    c2 = json.dumps({"site": hit, "title": fakes.t_view, **FAKE_SCORES}) + "\n"
    assert run["classified_bytes_after_stage"] == run["before"]["classified_bytes"] + c1.encode() + c2.encode()

    # the local copies: the page's own names, valid images at the meta's size
    for t in (fakes.t_plan, fakes.t_view):
        p = cover._local_path(run["tree"], hit, t)
        assert p.is_file(), p
        with Image.open(p) as im:
            assert im.size == (1280, 960)
    # and no copy leaked into the shared store
    assert not os.path.isdir(run["store_hit_dir"]), (
        "the phases must write the new copies into the tree's data/raw, never the shared store")

    # plans.json: growth over the committed keys, except what this machine's store cannot show
    kc, kb, kf, ks = run["world"]["keys_committed"], run["keys_baseline"], run["keys_after_fetch"], run["keys_after_stage"]
    lost = kc - kf
    files = {r["title"]: r for r in cover._files_rows(run["tree"]) if r.get("title")}
    idx = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(run["tree"], "data", "books", "index.jsonl")) if l.strip()}
    for k in sorted(lost):
        if k[0].startswith("c_"):
            t = k[0][2:]
            r = files.get(t)
            assert r is not None and not cover._local_path(run["tree"], r["site"], t).exists() and not (r.get("thumb") or r.get("url")), (
                "lost committed key %r: the row has no copy and no source on this machine" % (k,))
        else:
            r = idx.get(k[0])
            assert r is not None and not (r.get("full_local") and os.path.exists(os.path.join(run["tree"], r["full_local"]))), (
                "lost committed book key %r: no local page image on this machine" % (k,))
    gained = kb - kc
    for k in sorted(gained):
        if k[0].startswith("c_"):
            r = files.get(k[0][2:])
            assert r is not None and cover._local_path(run["tree"], r["site"], k[0][2:]).exists(), (
                "key %r appeared in this machine's export but not in the committed file" % (k,))
        else:
            r = idx.get(k[0])
            assert r is not None and os.path.exists(os.path.join(run["tree"], r.get("full_local", ""))), (
                "book key %r appeared in this machine's export but not in the committed file" % (k,))

    # the stage's two new rows: exact, and the only growth
    new_keys = {("c_" + _sha16(fakes.t_plan), hit), ("c_" + _sha16(fakes.t_view), hit)}
    assert ks == kf | new_keys, "stage adds exactly the two staged rows to the plans key set"
    rows = {r["id"]: r for r in _plans_rows(run["tree"])}
    name = world["sites"][hit]["name"]
    assert rows["c_" + _sha16(fakes.t_plan)] == planned_row(hit, fakes.t_plan, "Plan of %s (c. 1701)" % name, "1701", fakes)
    assert rows["c_" + _sha16(fakes.t_view)] == planned_row(hit, fakes.t_view, "View of %s (c. 1850)" % name, "1850", fakes)

    # the re-run re-stages nothing and rewrites nothing (the re-export is deterministic: same
    # inputs, same bytes; files.jsonl and classified.jsonl were already pinned above)
    assert run["n"]["staged2"] == 0
    assert "stage: nothing new to stage" in run["stdout"]["stage2"]
    assert (Path(run["tree"]) / "web" / "data" / "plans.json").read_bytes() == run["plans_bytes_after_stage"]
    assert (Path(run["tree"]) / "data" / "commons" / "files.jsonl").read_bytes() == run["files_bytes_after_stage"]
    assert (Path(run["tree"]) / "data" / "commons" / "classified.jsonl").read_bytes() == run["classified_bytes_after_stage"]


def test_nopicture(run):
    """(iv) the no-picture items: every search-set site except the hit (now a candidate site) gets
    its item marked with EXACTLY what was searched - the batch-era generic string replaced by the
    record's - candidates and resolution untouched; the hit's item byte-identical; every other item
    file byte-identical; the re-run re-marks the same items with the same searched strings."""
    world, fakes = run["world"], run["fakes"]
    ss, hit = run["ss_at_search"], world["hit"]
    recs = _load_searches(run["tree"])
    marked = [sid for sid in sorted(ss) if sid != hit]

    # every marked site: its item carries the exact searched string and its pre-run candidates/resolution
    for sid in marked:
        p, item = _find_item(run["tree"], sid)
        assert p is not None, "no review item for %s" % sid
        assert item.get("no_picture_found"), sid
        assert item["no_picture_found"]["searched"] == expected_searched(recs[sid]), (
            "%s: %r" % (sid, item["no_picture_found"]["searched"]))
        assert _iso(item["no_picture_found"]["at"]), "the at-timestamp is ISO"
        pre = world["items"].get(p) or _pre_by_site(world, sid)
        if pre is not None:
            assert item.get("candidates", []) == pre["item"].get("candidates", []), (
                "%s: the candidates must survive the mark" % sid)
            assert item.get("resolved") == pre["item"].get("resolved"), sid

    # spot-check the wording literally (the 212a contract as the human reads it on the page)
    spot_q = next((x for x in ss if x != hit and world["sites"][x].get("qid")), None)
    if spot_q:
        rec = recs[spot_q]
        qid = world["sites"][spot_q]["qid"]
        _, item = _find_item(run["tree"], spot_q)
        exp = ("wikidata %s; no Commons category; P180 depictions of %s: 0 of 0 file(s) checked; "
               "title searches: %s (0 hits); %s") % (
            qid, qid, ", ".join('"%s"' % q for q in rec["title_queries"]), rec["date"][:10])
        assert item["no_picture_found"]["searched"] == exp, item["no_picture_found"]["searched"]
    spot_n = next((x for x in ss if not world["sites"][x].get("qid")), None)
    if spot_n:
        rec = recs[spot_n]
        _, item = _find_item(run["tree"], spot_n)
        exp = ("no wikidata item; no Commons category; title searches: %s (0 hits); %s") % (
            ", ".join('"%s"' % q for q in rec["title_queries"]), rec["date"][:10])
        assert item["no_picture_found"]["searched"] == exp, item["no_picture_found"]["searched"]

    # the hit: its item (the batch-era no-picture note) is untouched - it has a picture now, and the
    # re-record of its note is the loop's job, not the search's
    p, _ = _find_item(run["tree"], hit)
    if p is not None:
        assert run["after"]["items"].get(p) == run["before"]["items"].get(p), (
            "the hit site's item must stay byte-identical (it is out of the nopicture set)")
    # every item file that is not a marked search-set site is byte-identical
    for path, b in run["after"]["items"].items():
        sid = json.loads(b).get("site")
        if sid in marked:
            continue
        assert b == run["before"]["items"].get(path), "the item file %s changed" % path

    # the re-run: same count, same searched strings, the at-timestamp re-stamped (write-once never
    # applies to no_picture_found - re-marking is the phase's contract)
    assert run["n"]["marked2"] == len(marked)
    assert run["stdout"]["nopicture2"].strip().splitlines()[-1] == "nopicture: %d item(s) marked" % len(marked)
    for sid in marked:
        p, item = _find_item(run["tree"], sid)
        assert item["no_picture_found"]["searched"] == expected_searched(recs[sid]), sid


def _pre_by_site(world, sid):
    for path, v in world["items"].items():
        if v["item"].get("site") == sid:
            return v
    return None


def test_checkout_integrity(run):
    """(v) nothing the phases wrote reached the checkout: every file the hard links share is
    byte-identical to before the run (data/ minus the raw symlink, web/data top level, docs/
    specs/ tests/)."""
    before, after = run["before"]["checkout"], run["after"]["checkout"]
    diff = {p: (before.get(p), after.get(p)) for p in set(before) | set(after)
            if before.get(p) != after.get(p)}
    assert not diff, "checkout files changed by the phases: %r" % list(diff)[:10]
