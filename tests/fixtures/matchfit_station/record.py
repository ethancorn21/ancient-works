"""One-shot recorder for the matcher-station test fixtures (task 302f, working phase only).

usage: .venv/bin/python tests/fixtures/matchfit_station/record.py

The live ELoFTR (127.0.0.1:8091 by default, MATCHER_URL overrides) must be up; RoMa is not
needed (the in-process runs point ROMA_URL at a dead ephemeral port, so matchfit.run's second
pass is deterministically skipped - no RoMa responses are ever recorded).

The script, on the badbury-rings-q798831 / earthworkenglan01allcgoog_n0132_1 hand-fit site:

  1. builds a scratch tree of the site's files (the hand document stays in it here; the
     in-process runs get their own trees with the document deleted - never the checkout's),
  2. sends the site's 15 (plan crop, ground, window) matcher requests to the live matcher
     TWICE, recording every response keyed by the sha256 of the exact request body
     matchfit.match sends - the same key the test's in-process stub looks up -
  3. checks the replay: with matchfit.match replaced by a fake that replays the recorded
     responses, matchfit_heldout.candidates must reproduce the live run candidate for
     candidate; and live must agree with the frozen held-out checkpoint (data/matchfit/
     heldout/results.json, at 2026-10-12) where the GPU has not drifted,
  4. runs tools/site_done.py IN-PROCESS twice on throwaway trees (confident fixture, then
     the unsure variant: the ground-side keypoints of every >=10-inlier response permuted
     with seed 7, so the best candidate lands under the 10-inlier gate) and records the
     exact stdout and every file effect the test asserts on,
  5. writes records.json and records_unsure.json next to this file (indent=1, no trailing
     newline, the store's convention).

The committed fixtures make tests/test_matchfit_station.py hermetic: it replays them over an
ephemeral loopback port with every other socket dead. Rerun this script when the header's
input_hashes no longer match the repo, the matcher model changes, or the test reports drift.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import socket
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]  # tests/fixtures/matchfit_station/ -> checkout root
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "fit"))

import batch_us  # noqa: E402
import matchfit as mf  # noqa: E402
import matchfit_heldout as mfh  # noqa: E402
import plan_fit  # noqa: E402
import propose  # noqa: E402
import review  # noqa: E402
import inkfit_heldout as ih  # noqa: E402

SID = "badbury-rings-q798831"
PLAN = "earthworkenglan01allcgoog_n0132_1"
DOCID = SID + "." + PLAN
MATCHER_URL = os.environ.get("MATCHER_URL", "http://127.0.0.1:8091")
OUT_DIR = Path(__file__).resolve().parent
SITE_DIR = os.path.realpath(ROOT / "web" / "data" / "sites" / SID)  # a symlink to the lead's project dir: copy the real dir


def _h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _h_dir(d):
    """One hash for a flat directory: sha256 of its sorted (name, sha256) list."""
    d = Path(d)
    rows = [[f.name, _h(f)] for f in sorted(d.iterdir()) if f.is_file()]
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def _save(path, obj):
    # default=float like matchfit_heldout.save: ransac's rot is a numpy float64
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=lambda o: float(o))


def _dead_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


DEAD_PORT = _dead_port()


def _plans_row():
    d = json.loads((ROOT / "web" / "data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(d["cols"])}
    rows = [{k: r[i] for k, i in cols.items()} for r in d["rows"]]
    return next(r for r in rows if r["id"] == PLAN)


def _index_row():
    for line in (ROOT / "data" / "books" / "index.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("id") == PLAN:
                return r
    raise SystemExit("no index row for " + PLAN)


def _catalog_row():
    for line in (ROOT / "data" / "catalog" / "sites.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("id") == SID:
                return r
    return None


def _site_entry(root):
    d = json.loads((Path(root) / "web" / "data" / "sites.json").read_text())
    return next(s for s in (d["sites"] if isinstance(d, dict) else d) if s["id"] == SID)


def build_tree(dest, delete_hand_doc):
    """The throwaway tree the test's tree builder copies (the two lists must stay in lockstep)."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    ignore = lambda d, names: [n for n in names if n == "__pycache__"]
    for d in ("tools", "fit", "pipeline"):
        shutil.copytree(ROOT / d, dest / d, ignore=ignore)
    web = dest / "web" / "data"
    web.mkdir(parents=True, exist_ok=True)
    for f in ("sites.json", "plans.json", "review.json"):
        shutil.copy2(ROOT / "web" / "data" / f, web / f)
    (web / "sites").mkdir(parents=True, exist_ok=True)
    shutil.copytree(SITE_DIR, web / "sites" / SID)  # real dir: the symlink target
    shutil.copytree(ROOT / "data" / "review", dest / "data" / "review")
    (dest / "data" / "books").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "data" / "books" / "index.jsonl", dest / "data" / "books" / "index.jsonl")
    (dest / "data" / "commons").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "data" / "commons" / "files.jsonl", dest / "data" / "commons" / "files.jsonl")
    (dest / "data" / "catalog").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "data" / "catalog" / "sites.jsonl", dest / "data" / "catalog" / "sites.jsonl")
    (dest / "data" / "sites" / SID).mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "data" / "sites" / SID / "site.json", dest / "data" / "sites" / SID / "site.json")
    raw = dest / "data" / "raw" / "books" / "earthworkenglan01allcgoog" / "full"
    raw.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "data" / "raw" / "books" / "earthworkenglan01allcgoog" / "full" / "n0132.jpg", raw / "n0132.jpg")
    shutil.copytree(ROOT / "data" / "db" / "platefits", dest / "data" / "db" / "platefits")
    if delete_hand_doc:
        (dest / "data" / "db" / "platefits" / (DOCID + ".json")).unlink()
    return dest


class _Resp:
    """A read-once stand-in for urlopen's response (matchfit.match json.loads its .read())."""

    def __init__(self, body):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _record_urlopen(orig, records, raw, log):
    """Patch urlopen: every /match request is recorded (sha256 of the exact body -> parsed JSON,
    plus the response bytes' sha256 in `raw` for the stability verdict) and served from the live
    matcher; everything else passes through."""

    def patched(req, *args, **kwargs):
        if isinstance(req, str):
            url, data = req, None
        else:
            url, data = req.full_url, req.data
        if data is not None and url.rstrip("/").endswith("/match"):
            resp = orig(req, *args, **kwargs)
            body = resp.read()
            key = hashlib.sha256(data).hexdigest()
            records[key] = json.loads(body)
            raw[key] = hashlib.sha256(body).hexdigest()
            log.append(key)
            return _Resp(body)
        return orig(req, *args, **kwargs)

    return patched


def _fake_match(records):
    """Rebuilds matchfit.match's request body exactly (same images, same json.dumps) so the
    key matches the recorded one; KeyError fails loudly when a key is missing."""

    def fake(a, b, url=None):
        body = json.dumps({"image0": mf._b64(a), "image1": mf._b64(b), "threshold": 0.2, "max_side": 1024}).encode()
        r = records[hashlib.sha256(body).hexdigest()]
        return np.array(r["keypoints0"]).reshape(-1, 2), np.array(r["keypoints1"]).reshape(-1, 2)

    return fake


def _candidate_diffs(live, frozen):
    """Field-by-field live vs frozen held-out candidate, in order (grounds then windows)."""
    diffs = []
    for i, (a, b) in enumerate(zip(live, frozen)):
        if a.get("ground") != b.get("ground") or a.get("window") != b.get("window"):
            diffs.append({"i": i, "field": "order", "frozen": [b.get("ground"), b.get("window")], "live": [a.get("ground"), a.get("window")]})
            continue
        if a.get("error"):
            diffs.append({"ground": a["ground"], "window": a["window"], "field": "error", "live": a["error"]})
            continue
        for k in ("matches", "inliers", "rot", "resid_m"):
            if k in b and a.get(k) != b.get(k):
                diffs.append({"ground": a["ground"], "window": a["window"], "field": k, "frozen": b[k], "live": a[k]})
    return diffs


def _load_site_done():
    spec = importlib.util.spec_from_file_location("site_done_recorder", ROOT / "tools" / "site_done.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _checkout_surface():
    """The checkout files the in-process runs must never touch (the lead's site dir via realpath)."""
    return [
        ROOT / "data" / "db" / "platefits",
        ROOT / "data" / "review",
        ROOT / "data" / "sites" / SID / "site.json",
        ROOT / "data" / "books" / "index.jsonl",
        ROOT / "data" / "commons" / "files.jsonl",
        ROOT / "data" / "catalog" / "sites.jsonl",
        ROOT / "web" / "data" / "sites.json",
        ROOT / "web" / "data" / "plans.json",
        ROOT / "web" / "data" / "review.json",
        Path(SITE_DIR),
    ]


def _hash_surface(paths):
    out = {}
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for f in sorted(p.iterdir()):
                if f.is_file():
                    out[str(f)] = _h(f)
        else:
            out[str(p)] = _h(p)
    return out


def _input_hashes():
    """What the fixtures were recorded from - the test's drift detector (rerun record.py if it fails)."""
    row = _plans_row()
    entry = _site_entry(ROOT)
    return {
        "hand_doc": _h(ROOT / "data" / "db" / "platefits" / (DOCID + ".json")),
        "plan_image": _h(ROOT / "data" / "raw" / "books" / "earthworkenglan01allcgoog" / "full" / "n0132.jpg"),
        "site_dir": _h_dir(SITE_DIR),
        "sites_entry": hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest(),
        "plans_row": hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest(),
        "index_row": hashlib.sha256(json.dumps(_index_row(), sort_keys=True).encode()).hexdigest(),
        "catalog_row": (hashlib.sha256(json.dumps(_catalog_row(), sort_keys=True).encode()).hexdigest()
                        if _catalog_row() else None),
        "site_json": _h(ROOT / "data" / "sites" / SID / "site.json"),
        "data_review": _h_dir(ROOT / "data" / "review"),
    }


def main():
    tmp = Path(tempfile.mkdtemp(prefix="aw302frec_"))
    try:
        _run(tmp)
    except BaseException:
        print("RECORDING FAILED - scratch tree kept for inspection: " + str(tmp), file=sys.stderr)
        raise
    shutil.rmtree(tmp, ignore_errors=True)
    print("wrote " + str(OUT_DIR / "records.json") + " and " + str(OUT_DIR / "records_unsure.json"))
    return 0


def _run(tmp):
    print("matcher:", MATCHER_URL, flush=True)
    health = json.loads(urllib.request.urlopen(MATCHER_URL + "/health", timeout=10).read())
    print("  health:", health, flush=True)

    row = _plans_row()
    site = _site_entry(ROOT)

    # --- live phase: two full passes over the 15 windows on one scratch tree -------------------
    t_live = build_tree(tmp / "t_live", delete_hand_doc=False)
    records, raw1, raw2, log1, log2 = {}, {}, {}, [], []
    orig_urlopen = urllib.request.urlopen
    c1 = c2 = None
    try:
        urllib.request.urlopen = _record_urlopen(orig_urlopen, records, raw1, log1)
        print("live run 1: sending 15 requests", flush=True)
        c1 = mfh.candidates(str(t_live), site, row, MATCHER_URL)
        print("live run 2: sending 15 requests", flush=True)
        urllib.request.urlopen = _record_urlopen(orig_urlopen, records, raw2, log2)
        c2 = mfh.candidates(str(t_live), site, row, MATCHER_URL)
    finally:
        urllib.request.urlopen = orig_urlopen
    if not c1 or len(c1) != 15 or any("error" in c for c in c1 + c2):
        raise SystemExit("the live matcher failed a request: %r" % [c for c in (c1 + c2) if "error" in c])
    assert len(set(log1)) == 15 and len(set(log2)) == 15, "a /match request body repeated"
    key_order_same = log1 == log2
    bytes_same = key_order_same and all(raw1[k] == raw2[k] for k in records)
    print("live: 15/15 keys distinct per run; order same across runs: %s; response bytes identical across runs: %s" % (key_order_same, bytes_same), flush=True)

    # --- frozen held-out checkpoint: live vs frozen, plus corner/centre on the live best -------
    res = json.loads((ROOT / "data" / "matchfit" / "heldout" / "results.json").read_text())
    frozen = res["docs"][DOCID]["candidates"]
    fdiffs = _candidate_diffs(c1, frozen)
    print("live vs frozen held-out: %d discrepancies" % len(fdiffs), flush=True)
    best = max(c1, key=lambda c: c.get("inliers", 0))
    hrow = propose._plans_row(PLAN, SID)
    a_h, b_h, w, h, lat0 = ih.hand_similarity(ROOT, DOCID, hrow)
    a_m, b_m, _r, _k = plan_fit.similarity(best["pairs"])
    corner, drot, srat = ih.corner_metrics(a_h, b_h, a_m, b_m, w, h, lat0)
    centre = mfh.centre_error(a_h, b_h, a_m, b_m, w, h, lat0)
    fbest = next(c for c in frozen if c.get("ground") == best["ground"] and c.get("window") == best["window"])
    print("live best: %s x%s inliers %d (frozen %s), corner %s m (frozen %s), centre %s m (frozen %s)" % (
        best["ground"], best["window"], best["inliers"], fbest.get("inliers"), corner, fbest.get("corner_m"),
        centre, fbest.get("centre_m")), flush=True)

    # --- offline replay: the recorded responses must reproduce the live run --------------------
    orig_match, orig_reach, orig_roma = mf.match, mf.reachable, mf.ROMA_URL
    mf.match = _fake_match(records)
    mf.reachable = lambda url=None: (url is None or url == MATCHER_URL)
    mf.ROMA_URL = "http://127.0.0.1:%d" % DEAD_PORT
    try:
        c3 = mfh.candidates(str(t_live), site, row, None)
    finally:
        mf.match, mf.reachable, mf.ROMA_URL = orig_match, orig_reach, orig_roma
    def _nsec(c):
        # "seconds" is wall-clock timing, never reproducible; everything else must replay identically
        return {k: v for k, v in c.items() if k != "seconds"}

    rdiffs = []
    for a, b in zip(c1, c3):
        da, db = _nsec(a), _nsec(b)
        if da != db:
            for k in set(da) | set(db):
                if da.get(k) != db.get(k):
                    rdiffs.append({"ground": a.get("ground"), "window": a.get("window"), "field": k})
    replay_ok = all(_nsec(a) == _nsec(b) for a, b in zip(c1, c3))
    print("offline replay vs live run 1: %s (seconds field excluded: timing is not reproducible)" %
          ("identical" if replay_ok else "DIFFERS: %r" % rdiffs), flush=True)

    input_hashes = _input_hashes()
    header_base = {
        "task": "302f",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "matcher_url": MATCHER_URL,
        "matcher_health": health,
        "site": SID,
        "plan": PLAN,
        "frozen_heldout": {
            "file": "data/matchfit/heldout/results.json",
            "at": res["at"],
            "best": {"ground": fbest["ground"], "window": fbest["window"], "matches": fbest["matches"],
                     "inliers": fbest["inliers"], "rot": fbest.get("rot"), "resid_m": fbest.get("resid_m"),
                     "corner_m": fbest.get("corner_m"), "centre_m": fbest.get("centre_m")},
            "live_best": {"inliers": best["inliers"], "corner_m": corner, "centre_m": centre},
            "live_vs_frozen_discrepancies": fdiffs,
        },
        "live_runs": {"runs": 2, "requests_per_run": 15, "key_order_same": key_order_same,
                      "response_bytes_identical_across_runs": bytes_same,
                      "responses_recorded": len(records)},
        "offline_replay_matches_live": replay_ok,
        # propose.propose_for's default root is the importing module's own ROOT: the in-process
        # runs below use the CHECKOUT's data (same bytes as the tree copies); the test's
        # subprocess reads the tree copies. The test re-derives the item from its own run, so
        # this only matters for the drift detector below.
        "propose_reads": "checkout",
        "input_hashes": input_hashes,
    }

    # --- confident branch: in-process site_done on a fresh tree with the hand doc deleted -----
    SD = _load_site_done()
    before = _hash_surface(_checkout_surface())
    t1 = build_tree(tmp / "t1", delete_hand_doc=True)
    mf.match = _fake_match(records)
    mf.reachable = lambda url=None: (url is None or url == MATCHER_URL)
    mf.ROMA_URL = "http://127.0.0.1:%d" % DEAD_PORT
    out_s, err_s = io.StringIO(), io.StringIO()
    rc = None
    try:
        with contextlib.redirect_stdout(out_s), contextlib.redirect_stderr(err_s):
            rc = SD.main([SID, "--root", str(t1)])
    finally:
        mf.match, mf.reachable, mf.ROMA_URL = orig_match, orig_reach, orig_roma
    after = _hash_surface(_checkout_surface())
    out, err = out_s.getvalue(), err_s.getvalue()
    print("confident in-process run: rc=%s, stderr=%r" % (rc, err[:400]), flush=True)
    if rc != 0 or err:
        print(out, file=sys.stderr)
        raise SystemExit("the confident run failed (see above)")
    c_out = out.splitlines()
    if len(c_out) != 11:
        print(out, file=sys.stderr)
        raise SystemExit("confident run printed %d lines, expected 11: %r" % (len(c_out), c_out))
    assert after == before, "the in-process confident run wrote outside the tree: %r" % (
        {k: (after.get(k), before.get(k)) for k in set(before) | set(after) if before.get(k) != after.get(k)})

    doc = json.loads((t1 / "data" / "db" / "platefits" / (DOCID + ".json")).read_text())
    doc_fields = {k: v for k, v in doc.items() if k != "at"}
    for k in ("auto", "by", "fitter", "matcher"):
        if k not in doc or doc.get("fitter") != "matcher":
            raise SystemExit("the confident doc is not a matcher doc: %r" % doc_fields)
    g_ratio, g_sd = mf.spread(doc["pairs"])  # the _sync_doc guard values (same function it called)
    guard_pass = g_ratio >= mf.SPREAD_MIN_RATIO and g_sd >= mf.SPREAD_MIN_SD_PX
    depiction = next(d for d in json.loads((t1 / "web" / "data" / "sites" / SID / "depictions.json").read_text())
                     ["depictions"] if d.get("kind") == "plan")
    depiction_rec = {k: (v if k != "fit" else {k2: v2 for k2, v2 in v.items() if k2 != "at"})
                     for k, v in depiction.items()}
    t_entry, repo_entry = _site_entry(t1), _site_entry(ROOT)
    conf_entry_same = t_entry == repo_entry
    review_same = (t1 / "web" / "data" / "review.json").read_bytes() == (ROOT / "web" / "data" / "review.json").read_bytes()
    webp_differs = (t1 / "web" / "data" / "sites" / SID / ("plan_" + PLAN + ".webp")).read_bytes() != \
        (Path(SITE_DIR) / ("plan_" + PLAN + ".webp")).read_bytes()
    print("confident: site entry equal %s (score %s), review.json untouched %s, webp rebuilt %s, guard %s" % (
        conf_entry_same, t_entry.get("score"), review_same, webp_differs, (round(g_ratio, 3), round(g_sd, 1))), flush=True)
    if not guard_pass:
        raise SystemExit("the spread guard FAILED on the recorded pairs (%r): the confident branch cannot build" % (g_ratio, g_sd))

    confident_section = {
        "expected_stdout": c_out,
        "doc": doc_fields,
        "depiction": depiction_rec,
        "site_entry_equal": conf_entry_same,
        "site_entry_after": {k: t_entry[k] for k in ("drawings", "score", "oldest", "overlays")},
        "spread_pairs": [round(g_ratio, 6), round(g_sd, 3)],
        "guard_pass": guard_pass,
        "review_json_untouched": review_same,
        "plan_webp_rebuilt": webp_differs,
    }

    # --- unsure variant: permute the ground keypoints of every >=10-inlier response ------------
    big = [(log1[i], c1[i]) for i in range(len(c1)) if c1[i].get("inliers", 0) >= 10]
    print("responses with >= 10 inliers (permuted for the unsure variant): %r" %
          [(c["ground"], c["window"]) for _, c in big], flush=True)
    seed, unsure_records, r = 7, None, None
    while seed < 37:
        u = dict(records)
        for k, c in big:
            k1 = u[k]["keypoints1"]
            order = np.random.default_rng(seed).permutation(len(k1))
            u[k] = dict(u[k], keypoints1=[k1[i] for i in order])
        mf.match = _fake_match(u)
        r = mf.fit_row(str(t_live), site, row, None, "eloftr")
        # fit_row's best exists only when ransac kept >= 3 inliers; judge's inlier gate fires
        # first, so any best with 3..9 inliers gives exactly the "not sure: N consistent points" line
        if "why" in r and r.get("inliers") is not None and 3 <= r["inliers"] < 10:
            seed, unsure_records = seed, u
            print("unsure variant: seed %d lands best at %s x%s, %s inliers, why: %s" % (
                seed, r.get("ground"), r.get("window"), r.get("inliers"), r["why"]), flush=True)
            break
        seed += 1
    mf.match = orig_match
    if unsure_records is None:
        raise SystemExit("no seed in 7..36 lands the unsure best at 3..9 inliers")

    # --- unsure branch: in-process site_done on a second fresh tree ----------------------------
    t2 = build_tree(tmp / "t2", delete_hand_doc=True)
    review_before = _h_dir(t2 / "data" / "review")
    n_before = len(list((t2 / "data" / "review").iterdir()))
    mf.match = _fake_match(unsure_records)
    mf.reachable = lambda url=None: (url is None or url == MATCHER_URL)
    mf.ROMA_URL = "http://127.0.0.1:%d" % DEAD_PORT
    out_s, err_s = io.StringIO(), io.StringIO()
    rc = None
    try:
        with contextlib.redirect_stdout(out_s), contextlib.redirect_stderr(err_s):
            rc = SD.main([SID, "--root", str(t2)])
    finally:
        mf.match, mf.reachable, mf.ROMA_URL = orig_match, orig_reach, orig_roma
    after2 = _hash_surface(_checkout_surface())
    out, err = out_s.getvalue(), err_s.getvalue()
    print("unsure in-process run: rc=%s, stderr=%r" % (rc, err[:400]), flush=True)
    if rc != 0 or err:
        print(out, file=sys.stderr)
        raise SystemExit("the unsure run failed (see above)")
    u_out = out.splitlines()
    if len(u_out) != 8:
        print(out, file=sys.stderr)
        raise SystemExit("unsure run printed %d lines, expected 8: %r" % (len(u_out), u_out))
    assert after2 == before, "the in-process unsure run wrote outside the tree"

    new_item = t2 / "data" / "review" / (DOCID + ".json")
    if not new_item.is_file():
        raise SystemExit("the unsure run wrote no review item: %s" % list((t2 / "data" / "review").iterdir())[-3:])
    item = json.loads(new_item.read_text())
    n_after = len(list((t2 / "data" / "review").iterdir()))
    changed = [f.name for f in (t2 / "data" / "review").iterdir()
               if f.name != (DOCID + ".json") and f.is_file() and f.read_bytes() !=
               (ROOT / "data" / "review" / f.name).read_bytes()]
    review_line = next(l for l in u_out if l.startswith("review "))
    n_open = int(review_line.split(" page now has ")[1].split(" open of ")[0])
    n_total = int(review_line.split(" open of ")[1].split(" items")[0])
    published = json.loads((t2 / "web" / "data" / "review.json").read_text())["items"]
    pub_bad = [i for i in published if i["site"] == SID]
    print("unsure: item %s, %d review files (was %d), others unchanged: %s, published %d items (%d badbury)" % (
        new_item.name, n_after, n_before, not changed, len(published), len(pub_bad)), flush=True)
    if changed:
        raise SystemExit("the unsure run touched other item files: %r (repo queue inconsistent?)" % changed)
    if n_after != n_before + 1 or len(pub_bad) != 1:
        raise SystemExit("unexpected unsure file effects: %d -> %d files, %d published badbury" % (n_before, n_after, len(pub_bad)))

    unsure_section = {
        "seed": seed,
        "best": {"ground": r.get("ground"), "window": r.get("window"), "inliers": r.get("inliers"),
                 "rot": (float(r["rot"]) if r.get("rot") is not None else None), "why": r["why"]},
        "expected_stdout": u_out,
        "item": item,
        "review_counts": {"n_open": n_open, "n_total": n_total},
        "new_item_file": "data/review/" + new_item.name,
        "other_item_files_unchanged": True,
        "n_published": len(published),
    }

    _save(OUT_DIR / "records.json", {"header": {**header_base, "confident": confident_section},
                                    "responses": records})
    _save(OUT_DIR / "records_unsure.json", {"header": {**header_base, "unsure": unsure_section},
                                            "responses": unsure_records})
    print("confident stdout:")
    print("\n".join(c_out))
    print("unsure stdout:")
    print("\n".join(u_out))


if __name__ == "__main__":
    sys.exit(main())
