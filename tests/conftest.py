"""Test harness for Ancient Works: the real product, end to end.

Tests drive the page through the real server: server/serve.py is started with --port 0 (an ephemeral
port, so two checkouts can run their tests at the same time) against a throwaway copy of the tree in
the system temp dir, so a test never writes into the checkout and never needs the network (the copy
has no data/raw/, so the book-page and media routes simply 404 and nothing fetches).

Shared fixtures live here. Each task adds its own test_*.py file and does not edit this one: ask for
a shared fixture in a DECISIONS entry instead, so two agents never change the same file.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")


def get(url, timeout=10):
    """GET through the real thing; returns (status, body bytes)."""
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status, r.read()


def get_json(url, timeout=10):
    status, body = get(url, timeout)
    return status, json.loads(body)


def put_json(url, obj, timeout=10):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="PUT",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def copy_web(tree, real=()):
    """Copy web/ into a test tree, with the per-site folders (web/data/sites/<id>, ~500 once the
    sites are built) LINKED to the checkout's, not copied: every full-tree fixture used to copy them
    all and the suite runs filled the VM disk (2026-10-12). `real` names the sites a test writes into
    (the one-site line's pick): those are real copies, so a write can never reach the checkout."""
    src, dst = os.path.join(ROOT, "web"), os.path.join(str(tree), "web")
    shutil.copytree(src, dst, ignore=lambda d, names: ["sites"] if d == os.path.join(src, "data") else [])
    sites = os.path.join(src, "data", "sites")
    os.makedirs(os.path.join(dst, "data", "sites"), exist_ok=True)
    for n in sorted(os.listdir(sites)):
        s, t = os.path.join(sites, n), os.path.join(dst, "data", "sites", n)
        if n in real:
            shutil.copytree(s, t)  # follows the checkout's own link into the shared store
        else:
            os.symlink(os.path.realpath(s), t)


@pytest.fixture(scope="session")
def served(tmp_path_factory):
    """The real server on an ephemeral port, serving a temp copy of the project (web/, server/, data/ minus data/raw/).

    Yields (base_url, tree): base_url like http://127.0.0.1:39411/, tree the copied project root.
    """
    tree = tmp_path_factory.mktemp("aw")
    copy_web(tree)
    shutil.copytree(os.path.join(ROOT, "server"), os.path.join(tree, "server"))
    # the whole data/ tree except data/raw/ (GB of book scans and downloads the tests never need):
    # data/db (document store), data/books, data/commons, data/catalog, data/review ...
    # and the per-site elevation grids (data/sites/*/dem.npy, gitignored, ~1.6 GB once the sites are built):
    # every full-tree copy carried them and the test runs filled the VM disk (2026-10-12)
    def ignore(d, names):
        return [n for n in names if os.path.join(d, n) == os.path.join(ROOT, "data", "raw")
                or n.endswith((".npy", ".npz"))]
    shutil.copytree(os.path.join(ROOT, "data"), os.path.join(tree, "data"), ignore=ignore)
    proc = subprocess.Popen([sys.executable, "server/serve.py", "--port", "0"],
                            cwd=str(tree), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    url = None
    deadline = time.time() + 90
    while time.time() < deadline and proc.poll() is None:
        line = proc.stdout.readline()
        m = re.match(r"Ancient Works on (\S+)", line) if line else None
        if m:
            url = m.group(1)
            break
    assert url, "server did not report its address (startup: %r)" % proc.stdout.read()[-2000:]
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            if get(url + "/")[0] == 200:
                break
        except OSError:
            time.sleep(0.2)
    else:
        raise AssertionError("server is not answering at " + url)
    try:
        yield url.rstrip("/"), tree
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(scope="session")
def golden_sites():
    """The sites of the existing hand fits: the reference nothing may ever delete (one id per line)."""
    with open(os.path.join(GOLDEN, "hand_fit_sites.txt")) as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
