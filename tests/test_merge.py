"""The consolidation of task 211 (fit/merge.py): per-source staging into the canonical data files, hermetic.

The real repo's data files are copied into a temp tree and merged there - no network, no fixed ports, nothing
written outside the project and the temp dir:
- every staging row lands in the canonical file; the pre-merge bytes stay a byte-identical prefix (the files
  grow, they are never rewritten);
- the merge is idempotent: a second run changes nothing (canonical files and the merge log are byte-identical);
- on a synthetic tree the failure paths are fail-closed: a conflict keeps the first row and records the drop,
  a picture row without the 200 evidence field (or of kind "none") is refused, and the run exits 1 - stable
  across reruns.
"""
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CANON = ["data/catalog/extras.jsonl", "data/commons/files.jsonl", "data/commons/classified.jsonl"]
STAGING = (
    ["data/catalog/extras_" + n + ".jsonl" for n in ("artists", "kip", "limes", "mackenzie", "van_deventer", "roman")]
    + ["data/commons/files_" + n + ".jsonl" for n in ("artists", "kip", "limes", "mackenzie", "numancia", "van_deventer", "wiltshire_b", "roman")]
    + ["data/commons/classified_" + n + ".jsonl" for n in ("artists", "kip", "limes", "mackenzie", "numancia", "van_deventer", "wiltshire_b", "roman")]
)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def _lines(p):
    return [l for l in open(p, encoding="utf-8") if l.strip()]


def _norm(line):
    return json.dumps(json.loads(line), sort_keys=True, ensure_ascii=False)


def _tree(tmp_path):
    """A throwaway copy of the data files the merge reads and writes, plus the module itself."""
    for p in CANON + STAGING:
        src = os.path.join(ROOT, p)
        if not os.path.exists(src):
            continue  # roman staging appears only once 207 lands
        dst = tmp_path / p
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    (tmp_path / "fit").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, "fit", "merge.py"), tmp_path / "fit" / "merge.py")
    return tmp_path


def _canon_of(staging_path):
    """data/catalog/extras_kip.jsonl -> data/catalog/extras.jsonl (staging name = canonical stem + _<source>).
    Mapped by stem, not by string surgery: source names may contain underscores (wiltshire_b, van_deventer)."""
    for stem in ("data/catalog/extras", "data/commons/files", "data/commons/classified"):
        if staging_path.startswith(stem + "_"):
            return stem + ".jsonl"
    raise ValueError(staging_path)


def run_merge(tree):
    return subprocess.run([sys.executable, "fit/merge.py", "merge", "--root", "."],
                          cwd=str(tree), capture_output=True, text=True)


def hashes(paths):
    return {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in paths}


def test_all_staging_merged_and_prefix_preserved(tmp_path):
    tree = _tree(tmp_path)
    before = {p: open(tree / p, "rb").read() for p in CANON}
    proc = run_merge(tree)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    for p in CANON:
        after = open(tree / p, "rb").read()
        assert after.startswith(before[p]), f"{p}: pre-merge bytes were not preserved byte-identically"
        assert len(after) >= len(before[p])
    # every staging row is in the canonical file (identity that ignores key order)
    for p in STAGING:
        if not (tree / p).exists():
            continue
        canon_p = _canon_of(p)
        have = {_norm(l) for l in _lines(tree / canon_p)}
        for l in _lines(tree / p):
            assert _norm(l) in have, f"{p}: row not in {canon_p}: {l[:120]}"
    # the growth is exactly the staging that was not there yet (no duplicate appends)
    for p in CANON:
        st = [q for q in STAGING if q.startswith(p.rsplit(".", 1)[0])]
        canon_before = {_norm(l) for l in _lines(tree / p) if l.rstrip("\n") in before[p].decode("utf-8").splitlines()}
        assert len(_lines(tree / p)) == len(canon_before) + len({k for n in st if (tree / n).exists() for k in map(_norm, _lines(tree / n))} - canon_before)
    log = json.loads("".join(_lines(tree / "data/merge/log.jsonl")) and "[" + ",".join(_lines(tree / "data/merge/log.jsonl")) + "]")
    assert log, "the merge log is empty although staging was merged"
    assert all(e["action"] == "merged" for e in log), [e for e in log if e["action"] != "merged"][:5]


def test_second_run_changes_nothing(tmp_path):
    tree = _tree(tmp_path)
    assert run_merge(tree).returncode == 0
    watched = [str(tree / p) for p in CANON + ["data/merge/log.jsonl"]]
    after1 = hashes(watched)
    proc = run_merge(tree)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    after2 = hashes(watched)
    assert after1 == after2, {k: (after1[k], after2[k]) for k in after1 if after1[k] != after2[k]}


def test_conflict_and_rejection_are_fail_closed(tmp_path):
    """Synthetic tree: first row wins, a conflict and a row with no evidence are refused, exit 1, stable on rerun."""
    tree = tmp_path / "aw"
    (tree / "fit").mkdir(parents=True)
    (tree / "data/catalog").mkdir(parents=True)
    (tree / "data/commons").mkdir(parents=True)
    shutil.copyfile(os.path.join(ROOT, "fit", "merge.py"), tree / "fit" / "merge.py")

    def row(**kw):
        return json.dumps(kw, ensure_ascii=False) + "\n"

    (tree / "data/catalog/extras.jsonl").write_text(row(id="x1", name="First") + row(id="x0", name="Old"))
    (tree / "data/catalog/extras_s1.jsonl").write_text(row(id="x1", name="Different"))   # conflict
    (tree / "data/catalog/extras_s2.jsonl").write_text(row(id="x2", name="New"))
    (tree / "data/catalog/extras_s3.jsonl").write_text(row(id="x2", name="New"))          # identical duplicate
    (tree / "data/commons/files.jsonl").write_text(row(site="s1"))                        # sentinel: no title
    (tree / "data/commons/files_a.jsonl").write_text(
        row(site="s2", title="T.jpg", evidence={"rec": "evidence/1", "kind": "caption_coords", "dist_m": 0.0}))
    (tree / "data/commons/files_b.jsonl").write_text(row(site="s3", title="Bad.jpg"))      # no evidence field
    (tree / "data/commons/files_c.jsonl").write_text(
        row(site="s4", title="None.jpg", evidence={"rec": "evidence/1", "kind": "none"}))  # no tie
    (tree / "data/commons/classified.jsonl").write_text("")
    (tree / "data/commons/classified_c.jsonl").write_text(row(site="s2", title="T.jpg", p_plan=1.0, p_birdseye=0.0, p_photo=0.0))

    proc = run_merge(tree)
    assert proc.returncode == 1, "a refused row must fail the run: " + proc.stdout

    extras = open(tree / "data/catalog/extras.jsonl").read()
    assert extras.startswith(row(id="x1", name="First")), "the first row holding the key must stay byte-identical"
    assert extras.count('"x2"') == 1, "the identical duplicate must be merged once, not twice"
    assert "Different" not in extras, "a conflicting row must never be written"
    files = open(tree / "data/commons/files.jsonl").read()
    assert files.startswith(row(site="s1")), "the sentinel row is a pre-merge row: byte-identical"
    assert "T.jpg" in files and "Bad.jpg" not in files and "None.jpg" not in files
    log = [json.loads(l) for l in _lines(tree / "data/merge/log.jsonl")]
    actions = {(e["target"], json.dumps(e["key"], sort_keys=True), e["action"]) for e in log}
    assert ("data/catalog/extras.jsonl", '["x1"]', "conflict") in actions
    assert ("data/catalog/extras.jsonl", '["x2"]', "merged") in actions  # both sources of the identical pair
    assert ("data/commons/files.jsonl", '["s3", "Bad.jpg"]', "rejected") in actions
    assert ("data/commons/files.jsonl", '["s4", "None.jpg"]', "rejected") in actions
    assert sum(1 for a in actions if a[2] == "merged") == 3              # x2 twice (two sources), T.jpg, T.jpg classified
    assert all(e["action"] in ("merged", "conflict", "rejected") for e in log)

    # the refusal is stable: the rerun changes nothing and fails the same way
    watched = [str(p) for p in (tree / "data/catalog/extras.jsonl", tree / "data/commons/files.jsonl",
                                tree / "data/commons/classified.jsonl", tree / "data/merge/log.jsonl")]
    before = hashes(watched)
    proc2 = run_merge(tree)
    assert proc2.returncode == 1
    after = hashes(watched)
    assert before == after, "the second run must change nothing, refusal included"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
