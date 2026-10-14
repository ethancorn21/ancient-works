"""The matcher station, end to end (task 302f): tools/site_done.py on the hand-fit site
badbury-rings-q798831 with the pretrained matcher (fit/matchfit.py) in the line, hermetically.

The ELoFTR responses are replayed from committed fixtures (tests/fixtures/matchfit_station/
records.json and records_unsure.json) that a one-off working-phase run of record.py recorded
live against 127.0.0.1:8091, keyed by the sha256 of the exact request body matchfit.match
sends. The test serves them from an in-process stub on an ephemeral loopback port (never a
fixed one) and runs the copied line as a subprocess whose sockets die loudly unless they
reach the stub (the guard, a pass-through variant of test_site_done's dead-socket guard):
that is the "no network" proof.

  confident  the recorded 22-inlier six-inch-1st.webp x0.35 fit passes judge: the line writes
             the matcher document (by: agent, auto: true, fitter: matcher, its matcher block),
             the sync's spread guard passes and builds the overlay, the single candidate is
             covered so the vision batch never runs, no review item, the site entry stays
             1.45, the published review page is byte-identical.
  unsure     a fixture variant in which the ground keypoints of the two >=10-inlier responses
             are permuted so the best candidate lands at 8 inliers: the "not sure: N
             consistent points (need 10)" line, no document, the candidate in the site's
             review item with the batch's own reason ("no model answer", from the
             socket-dead vision pass) plus the scale-bar proposal, the page grows by exactly
             that one item.

Drift: each fixture header records the sha256 of every repo input it was recorded from; the
test fails with "rerun record.py" (working phase, live matcher required) when the repo no
longer matches, and the in-process baseline export re-checks the review queue's consistency.
"""
import hashlib
import http.server
import importlib.util
import json
import os
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIX = ROOT / "tests" / "fixtures" / "matchfit_station"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The recorder (working-phase tool, import-safe: no live work at import): the tree builder the
# tmp roots share with it, its hash/surface helpers, and its constants.
rec = _load(FIX / "record.py", "matchfit_station_recorder")
SID, PLAN, DOCID = rec.SID, rec.PLAN, rec.DOCID
REVIEW = _load(ROOT / "fit" / "review.py", "review_under_test")  # stdlib-only; export is root-scoped


def _dead_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


# The subprocess guard (a pass-through variant of test_site_done's): every socket attempt dies
# loudly UNLESS it reaches the stub's loopback port (env GUARD_ALLOW). socket.socket.connect and
# connect_ex are patched (NOT create_connection - it must flow to the patched instance method,
# which http.client uses). A refused dead RoMa port raises here and reachable()'s except
# Exception turns it into False, deterministically.
GUARD = r"""
import os
import runpy
import socket
import sys


def _allow(address):
    try:
        return (isinstance(address, tuple) and len(address) == 2 and address[0] == "127.0.0.1"
                and int(address[1]) == int(os.environ["GUARD_ALLOW"]))
    except (KeyError, TypeError, ValueError):
        return False


def _connect(self, address, *args, **kwargs):
    if not _allow(address):
        raise AssertionError("the hermetic run attempted a network connection: %r" % (address,))
    return _orig_connect(self, address, *args, **kwargs)


def _connect_ex(self, address, *args, **kwargs):
    if not _allow(address):
        raise AssertionError("the hermetic run attempted a network connection: %r" % (address,))
    return _orig_connect_ex(self, address, *args, **kwargs)


_orig_connect = socket.socket.connect
_orig_connect_ex = socket.socket.connect_ex
socket.socket.connect = _connect
socket.socket.connect_ex = _connect_ex

args = sys.argv[1:] if sys.argv[0] == "-c" else sys.argv
script, *rest = args
sys.argv = [script] + rest
runpy.run_path(script, run_name="__main__")
"""


def _start_stub(fixture):
    """The in-process ELoFTR stand-in on an ephemeral loopback port (the test_surveyfit idiom):
    GET /health answers the fixture's recorded health, POST /match the fixture's recorded
    response by sha256 of the exact request body (500 when unrecorded - matchfit turns that
    into a loud per-window error). -> (server, request log, port)."""
    responses = fixture["responses"]
    health = json.dumps(fixture["header"]["matcher_health"]).encode()
    served = []

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _reply(self, code, body):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            served.append(("GET", self.path, None, 200 if self.path == "/health" else 404))
            self._reply(200 if self.path == "/health" else 404,
                        health if self.path == "/health" else b'{"error": "unknown path"}')

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            key = hashlib.sha256(body).hexdigest()
            code = 200 if key in responses else 500
            served.append(("POST", self.path, key, code))
            if self.path != "/match":
                self._reply(404, b'{"error": "unknown path"}')
                return
            self._reply(code, json.dumps(responses[key]).encode() if code == 200
                        else b'{"error": "unrecorded matcher request"}')

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, served, server.server_address[1]


def _run(tree, stub_port, roma_port):
    """The one-site line on the tree, as a subprocess: copied code, copied data, sockets
    allowed only to the stub (the guard's GUARD_ALLOW), RoMa at a dead port."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8",
               MATCHER_URL="http://127.0.0.1:%d" % stub_port,
               ROMA_URL="http://127.0.0.1:%d" % roma_port,
               GUARD_ALLOW=str(stub_port))
    return subprocess.run([sys.executable, "-c", GUARD, str(tree / "tools" / "site_done.py"), SID],
                          cwd=str(tree), env=env, capture_output=True, timeout=600)


def _site_entry(root):
    d = json.loads((Path(root) / "web" / "data" / "sites.json").read_text())
    return next(s for s in d["sites"] if s["id"] == SID)


def _drift(fixture):
    """The fixture's recorded input hashes vs the repo now: the rerun trigger."""
    then = fixture["header"]["input_hashes"]
    now = rec._input_hashes()
    bad = {k: (then.get(k), now.get(k)) for k in set(then) | set(now) if then.get(k) != now.get(k)}
    if bad:
        pytest.fail("the fixture's inputs drifted since the recording (rerun record.py in the "
                    "working phase): %r" % bad)


def _preconditions(fixture):
    _drift(fixture)
    if not (ROOT / "data" / "db" / "platefits" / (DOCID + ".json")).is_file():
        pytest.fail(f"the repo no longer holds the {DOCID} hand document: the trees delete it only "
                    f"in their own copies (rerun record.py)")
    for p in sorted((ROOT / "data" / "review").glob("*.json")):
        if json.loads(p.read_text()).get("site") == SID:
            pytest.fail(f"the repo now holds a {SID} review item: the fixtures assume none "
                        "(rerun record.py)")
    if any(i.get("site") == SID for i in json.loads(
            (ROOT / "web" / "data" / "review.json").read_text())["items"]):
        pytest.fail(f"the published review page lists {SID}: the fixtures assume it is absent "
                    "(rerun record.py)")


def _stub_traffic(served):
    """(health count, (key, code) list for /match, the off-stub requests): the no-network proof
    is that the list is empty and every /match is one of the fixture's recorded responses."""
    health = sum(1 for m, p, k, c in served if m == "GET" and p == "/health")
    matches = [(k, c) for m, p, k, c in served if m == "POST" and p == "/match"]
    other = [s for s in served if not ((s[0] == "GET" and s[1] == "/health")
                                       or (s[0] == "POST" and s[1] == "/match"))]
    return health, matches, other


def test_confident_matcher_station(tmp_path):
    """A confident matcher fit becomes a document, is built, and the line never touches the queue."""
    fixture = json.loads((FIX / "records.json").read_text())
    hdr = fixture["header"]["confident"]
    _preconditions(fixture)

    before = rec._hash_surface(rec._checkout_surface())
    tree = rec.build_tree(tmp_path / "tree", delete_hand_doc=True)  # the single candidate is uncovered
    server, served, port = _start_stub(fixture)
    try:
        proc = _run(tree, port, _dead_port())
    finally:
        server.shutdown()
        server.server_close()
    out, err = proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8")
    assert proc.returncode == 0, out + err
    assert err == ""
    assert out.splitlines() == hdr["expected_stdout"]  # line 3 is the "FIT (eloftr) 22/61 ..." line

    # the matcher document the line wrote (the fixture's recorded fields, plus a fresh "at")
    doc = json.loads((tree / "data" / "db" / "platefits" / (DOCID + ".json")).read_text())
    assert "at" in doc
    assert {k: v for k, v in doc.items() if k != "at"} == hdr["doc"]
    assert (doc["by"], doc["auto"], doc["fitter"]) == ("agent", True, "matcher")
    assert set(doc["matcher"]) == {"model", "inliers", "matches", "ground", "window", "rot_deg", "spread"}

    # the build replaced the same-file plan depiction (the matcher's fit) and rebuilt the webps
    dep = next(d for d in json.loads(
        (tree / "web" / "data" / "sites" / SID / "depictions.json").read_text())["depictions"]
        if d.get("kind") == "plan")
    assert {k: (v if k != "fit" else {k2: v2 for k2, v2 in v.items() if k2 != "at"})
            for k, v in dep.items()} == hdr["depiction"]
    assert dep["fit"]["at"] == doc["at"]
    site, repo_site = tree / "web" / "data" / "sites" / SID, Path(rec.SITE_DIR)
    main_webp = "plan_" + PLAN + ".webp"
    assert (site / main_webp).read_bytes() != (repo_site / main_webp).read_bytes()  # rebuilt, not copied
    assert (site / ("plan_" + PLAN + "_ink.webp")).is_file()

    # the site entry stays as in the repo (the matcher fit's markers round to the hand fit's)
    if hdr["site_entry_equal"]:
        assert _site_entry(tree) == _site_entry(ROOT)
    else:  # the narrow-margin fallback the recorder records: field-level, not whole-entry
        assert {k: _site_entry(tree)[k] for k in ("drawings", "score", "oldest", "overlays")} == \
            hdr["site_entry_after"]

    # the confident branch never opens a queue item: the page is byte-identical, no item file moves
    assert (tree / "web" / "data" / "review.json").read_bytes() == \
        (ROOT / "web" / "data" / "review.json").read_bytes()
    assert sorted(os.listdir(tree / "data" / "review")) == sorted(os.listdir(ROOT / "data" / "review"))
    for name in os.listdir(tree / "data" / "review"):
        assert (tree / "data" / "review" / name).read_bytes() == \
            (ROOT / "data" / "review" / name).read_bytes(), name
    # the document store: the matcher doc replaced the deleted hand doc, every other file untouched
    assert sorted(os.listdir(tree / "data" / "db" / "platefits")) == \
        sorted(os.listdir(ROOT / "data" / "db" / "platefits"))
    for name in os.listdir(tree / "data" / "db" / "platefits"):
        if name != DOCID + ".json":
            assert (tree / "data" / "db" / "platefits" / name).read_bytes() == \
                (ROOT / "data" / "db" / "platefits" / name).read_bytes(), name
    assert (tree / "data" / "sites" / SID / "site.json").read_bytes() == \
        (ROOT / "data" / "sites" / SID / "site.json").read_bytes()

    # the only network: one health check and the 15 recorded /match responses, all of them, no 500s
    health, matches, other = _stub_traffic(served)
    assert other == [] and health == 1
    assert sorted(k for k, _ in matches) == sorted(fixture["responses"])
    assert all(c == 200 for _, c in matches) and len(matches) == 15
    assert rec._hash_surface(rec._checkout_surface()) == before  # and the checkout is untouched


def test_unsure_matcher_station(tmp_path):
    """An unsure matcher fit goes to the queue with the reason, never to the map (the parent's
    box-3 contract, end to end): no document, one new item, the page grows by exactly it."""
    fixture = json.loads((FIX / "records_unsure.json").read_text())
    hdr = fixture["header"]["unsure"]
    _preconditions(fixture)

    # baseline: the queue as it stands (no badbury item), exported in-process on its own copy -
    # the published page the run must grow by exactly the new badbury item
    baseline = rec.build_tree(tmp_path / "baseline", delete_hand_doc=False)
    n_open, n_total = REVIEW.export(str(baseline))
    assert (n_open, n_total) == (hdr["review_counts"]["n_open"] - 1, hdr["review_counts"]["n_total"] - 1), \
        f"the queue drifted since the fixture (rerun record.py): the baseline export gives " \
        f"{n_open}/{n_total}, the fixture recorded {hdr['review_counts']}"
    for f in sorted((baseline / "data" / "review").iterdir()):  # the repo queue is consistent:
        assert f.read_bytes() == (ROOT / "data" / "review" / f.name).read_bytes(), f.name
    baseline_items = json.loads((baseline / "web" / "data" / "review.json").read_text())["items"]
    assert not any(i.get("site") == SID for i in baseline_items)
    name = _site_entry(ROOT)["name"]
    assert sum(1 for i in baseline_items if i.get("name") == name) <= 1  # the new entry's name is unique

    before = rec._hash_surface(rec._checkout_surface())
    tree = rec.build_tree(tmp_path / "tree", delete_hand_doc=True)
    server, served, port = _start_stub(fixture)
    try:
        proc = _run(tree, port, _dead_port())
    finally:
        server.shutdown()
        server.server_close()
    out, err = proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8")
    assert proc.returncode == 0, out + err
    assert err == ""
    assert out.splitlines() == hdr["expected_stdout"]  # line 3 is the "not sure: N consistent points" line
    assert "not sure:" in out and "(need 10)" in out

    # no document for the plan; the new review item, exactly what the fixture recorded
    assert not (tree / "data" / "db" / "platefits" / (DOCID + ".json")).is_file()
    item = json.loads((tree / "data" / "review" / (DOCID + ".json")).read_text())
    assert item == hdr["item"]
    cand = item["candidates"][0]
    assert cand["plan"] == PLAN and cand["why"] == "no model answer" and cand["pairs"] == []

    # data/review: every repo file byte-identical, exactly one new file
    tr, rr = sorted(os.listdir(tree / "data" / "review")), sorted(os.listdir(ROOT / "data" / "review"))
    assert tr == sorted(rr + [DOCID + ".json"])
    for name_ in rr:
        assert (tree / "data" / "review" / name_).read_bytes() == \
            (ROOT / "data" / "review" / name_).read_bytes(), name_

    # nothing built: the site dir is byte-identical (depictions and both plan webps)
    site, repo_site = tree / "web" / "data" / "sites" / SID, Path(rec.SITE_DIR)
    assert {f.name: (site / f.name).read_bytes() for f in site.iterdir() if f.is_file()} == \
        {f.name: (repo_site / f.name).read_bytes() for f in repo_site.iterdir() if f.is_file()}
    assert _site_entry(tree) == _site_entry(ROOT)  # the entry's markers come from the unchanged depictions

    # the published page: the baseline's items plus exactly the new badbury item, name-sorted
    new_entry = {"site": SID, "name": name, "lead": PLAN,
                 "candidates": item["candidates"], "no_picture_found": item.get("no_picture_found")}
    pub = json.loads((tree / "web" / "data" / "review.json").read_text())["items"]
    assert pub == sorted(baseline_items + [new_entry], key=lambda e: (e["name"] or "").lower())
    assert len(pub) == len(baseline_items) + 1

    # the only network: one health check and the 15 recorded (perturbed) /match responses
    health, matches, other = _stub_traffic(served)
    assert other == [] and health == 1
    assert sorted(k for k, _ in matches) == sorted(fixture["responses"])
    assert all(c == 200 for _, c in matches) and len(matches) == 15
    assert rec._hash_surface(rec._checkout_surface()) == before  # and the checkout is untouched
