"""The consolidation of task 211 (fit/merge.py): per-source staging into the canonical data files, hermetic.

The real repo's data files are copied into a temp tree and merged there - no network, no fixed ports, nothing
written outside the project and the temp dir:
- every staging row lands in the canonical file; the pre-merge bytes stay a byte-identical prefix (the files
  grow, they are never rewritten);
- the merge is idempotent: a second run changes nothing (canonical files and the merge log are byte-identical);
- on a synthetic tree the failure paths are fail-closed: a conflict keeps the first row and records the drop,
  a picture row without the 200 evidence field (or of kind "none") is refused, and the run exits 1 - stable
  across reruns.

Box 2 (the rebuilt book index): the test asserts the data-level result, never a rebuild - every index row
and every titled files row carries the 200 evidence field, the index rows join to their stage-A triage,
`fit/evidence.py check` passes offline on the merged set, and `record` is a byte-identical no-op once every
row is recorded.

Box 4 (the refreshed plan list): the test asserts the data-level result of the tools/export_plans.py
refresh, read-only - every (id, sites[0]) key of the frozen pre-run list (data/merge/plans_premerge_keys.jsonl,
230 re-baselined it to the post-211 rows) is still present, (id, sites[0]) stays unique (the shared-id picture
keeps one row per (picture, site)), the merged pictures that qualify as plans/bird's-eye views reach the
list, and every picture row joins a files row carrying the 200 evidence field.

Box 3 (the built sites): the test asserts the data-level result of the build phase, read-only on the
served data (never a rebuild). web/data/sites.json grew purely against the frozen pre-run baseline
(data/merge/sites_premerge_baseline.jsonl, the 499 entries served after 211's consolidation - the 385
pre-211 set plus 211's 114 builds, re-baselined by 230 before the Roman re-run): nothing removed, no
entry rewritten except the marker fields 212's page-facing sync later owns; and every site built in this
phase is complete (its directory, the page's required fields, relief.jpg iff the entry credits a LiDAR
source, and a coverable old-map layer implies a depictions.json), with three sites pinned to the exact
values their recorded builds produced.
"""
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time

from collections import Counter

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
            continue  # a staging file is absent until its source task lands it
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


def test_sources_filter_merges_only_named_sources(tmp_path):
    """--sources scopes a run to one source family (230's Roman re-run must not fold in the US families'
    still-pending staging, whose own consolidation is 236c): only the named families' rows enter the
    canonical files and the log, and the later unfiltered rerun picks up the rest exactly once."""
    tree = tmp_path / "aw"
    (tree / "fit").mkdir(parents=True)
    (tree / "data/catalog").mkdir(parents=True)
    (tree / "data/merge").mkdir(parents=True)
    shutil.copyfile(os.path.join(ROOT, "fit", "merge.py"), tree / "fit" / "merge.py")

    def row(**kw):
        return json.dumps(kw, ensure_ascii=False) + "\n"

    (tree / "data/catalog/extras.jsonl").write_text(row(id="x0", name="Old"))
    (tree / "data/catalog/extras_a.jsonl").write_text(row(id="xa", name="A"))
    (tree / "data/catalog/extras_b.jsonl").write_text(row(id="xb", name="B"))

    p = subprocess.run([sys.executable, "fit/merge.py", "merge", "--root", ".", "--sources", "b"],
                       cwd=str(tree), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr + p.stdout
    extras = open(tree / "data/catalog/extras.jsonl").read()
    assert '"xb"' in extras and '"xa"' not in extras, "the filter must merge only the named source"
    log = [json.loads(l) for l in _lines(str(tree / "data/merge/log.jsonl"))]
    assert log and all(e["source"] == "b" for e in log), "the log records the filtered run only"

    p = subprocess.run([sys.executable, "fit/merge.py", "merge", "--root", "."],
                       cwd=str(tree), capture_output=True, text=True)
    assert p.returncode == 0, p.stderr + p.stdout
    extras = open(tree / "data/catalog/extras.jsonl").read()
    assert '"xa"' in extras and extras.count('"xb"') == 1, "the unfiltered rerun picks up the rest, once"


def test_index_and_plan_list_rows_carry_evidence():
    """Full-data invariant (no rebuild): every book-index row and every titled files row carries the 200
    evidence field; every index row joins to its book's stage-A triage; the offline re-check passes."""
    idx = [json.loads(l) for l in _lines(os.path.join(ROOT, "data/books/index.jsonl"))]
    assert idx, "the book index is empty"
    for r in idx:
        ev = r.get("evidence")
        assert isinstance(ev, dict) and ev.get("rec") == "evidence/1", f"{r['id']}: no 200 evidence field"
        # the index is regenerated from the per-book artifacts: a row can only exist for a triaged book
        assert os.path.exists(os.path.join(ROOT, "data/books/triage", r["ia_id"] + ".A.jsonl")), r["id"]
        assert r["id"].startswith(r["ia_id"] + "_n"), r["id"]
    for r in [json.loads(l) for l in _lines(os.path.join(ROOT, "data/commons/files.jsonl"))]:
        if r.get("title"):
            ev = r.get("evidence")
            assert isinstance(ev, dict) and ev.get("rec") == "evidence/1", f"{r['site']}|{r['title']}: no 200 evidence field"
    # the offline re-check over the merged set: every recorded tie re-verifies from stored fields (rc 0, no FAIL)
    proc = subprocess.run([sys.executable, "fit/evidence.py", "check"], cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout[-2000:]
    assert " 0 fail" in proc.stdout, proc.stdout[-2000:]


def test_record_appends_evidence_and_rerun_is_a_noop(tmp_path):
    """Small fixed sample: record appends the evidence field to a row missing it (the stored fields keep
    their values), leaves an already-recorded row byte-identical, and a second run changes nothing."""
    books = tmp_path / "index.jsonl"
    files = tmp_path / "files.jsonl"
    bare = json.dumps({"id": "zzzbook_n0001_1", "book": "zzzbook", "title": "No such place on any sheet"},
                      ensure_ascii=False) + "\n"
    done = json.dumps({"id": "zzzbook_n0002_1", "book": "zzzbook", "title": "Kept row",
                       "evidence": {"rec": "evidence/1", "kind": "caption_coords", "score": 0.9}},
                      ensure_ascii=False) + "\n"
    books.write_text(bare + done, encoding="utf-8")
    files_text = json.dumps({"site": "s-sentinel"}) + "\n"  # no title: never recorded
    files.write_text(files_text, encoding="utf-8")
    argv = [sys.executable, os.path.join(ROOT, "fit/evidence.py"), "record", "--files", str(files), "--books", str(books)]
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    lines = open(books, encoding="utf-8").read().splitlines()
    got = json.loads(lines[0])
    assert got["evidence"]["rec"] == "evidence/1", "the bare row must be recorded"
    for k, v in json.loads(bare).items():
        assert got[k] == v, f"existing field {k} changed by record"
    assert lines[1] == done.rstrip("\n"), "an already-recorded row must stay byte-identical"
    assert open(files, encoding="utf-8").read() == files_text, "the sentinel files row has no title: untouched"
    h = {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (str(books), str(files))}
    proc2 = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    assert proc2.returncode == 0, proc2.stderr + proc2.stdout
    assert {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (str(books), str(files))} == h, \
        "the second record run must change nothing"


def test_plan_list_refresh_is_pure_growth():
    """Box 4, read-only on the served data: web/data/plans.json was refreshed with tools/export_plans.py
    after the merge. Every key of the frozen pre-run list (the post-211 rows) is still present, (id,
    sites[0]) stays unique, the merged pictures that qualify as plans reach the list, and each picture
    row's files row carries the 200 evidence field."""
    pre = [json.loads(l) for l in _lines(os.path.join(ROOT, "data/merge/plans_premerge_keys.jsonl"))]
    assert pre, "the frozen pre-merge key list is empty"
    d = json.load(open(os.path.join(ROOT, "web", "data", "plans.json")))
    assert d["cols"] == ["id", "book", "ia", "file", "title", "label", "size", "map_box", "sites",
                         "cite", "url", "view", "ref"]
    i_id = d["cols"].index("id"); i_book = d["cols"].index("book"); i_sites = d["cols"].index("sites"); i_ref = d["cols"].index("ref")
    key = lambda r: (r[i_id], r[i_sites][0] if r[i_sites] else None)
    # (id, sites[0]) unique - the shared-id picture stays one row per (picture, site)
    for k, n in Counter(map(key, d["rows"])).items():
        assert n == 1, f"plan key repeated {n} times: {k}"
    keys = set(map(key, d["rows"]))
    # the refresh only grew the list: every pre-merge key survived
    for k in pre:
        assert (k["id"], k["site"]) in keys, f"pre-merge plan key lost by the refresh: {k}"
    # the merged pictures that qualify as plans/bird's-eye views reach the list (206's Mackenzie Shotwick, 210's Numancia)
    for site, book in (("shotwick-castle-q7502621", "Wikimedia Commons"), ("numancia", "Wikimedia Commons")):
        hit = [r for r in d["rows"] if r[i_sites] == [site] and r[i_book] == book]
        assert hit, f"no {book} plan row for the merged picture of {site}"
    # every picture row (ref = the files title) joins a files row carrying the 200 evidence field
    files = {(r["site"], r["title"]): r.get("evidence")
             for r in (json.loads(l) for l in _lines(os.path.join(ROOT, "data/commons/files.jsonl"))) if r.get("title")}
    for r in d["rows"]:
        if r[i_ref] is None:
            continue  # a book row: its evidence is asserted on the index row by test_index_and_plan_list_rows_carry_evidence
        ev = files.get((r[i_sites][0], r[i_ref]))
        assert isinstance(ev, dict) and ev.get("rec") == "evidence/1", \
            f"plan row {r[i_id]} joins a files row without the 200 evidence field"


# The four marker fields build_site.marks() re-writes whenever a fit is saved or deleted; 212's
# page-facing sync owns them for every site, so the baseline identity check tolerates changes to
# exactly these (the box: "the old entries are unchanged except fields 212 later owns").
MARKERS = ("drawings", "score", "oldest", "overlays")


def _site_entries():
    return json.load(open(os.path.join(ROOT, "web", "data", "sites.json")))


def _baseline_entries():
    return [json.loads(l) for l in _lines(os.path.join(ROOT, "data/merge/sites_premerge_baseline.jsonl"))]


def test_served_sites_grew_purely():
    """Box 3, read-only: the served sites.json grew without ever rewriting the pre-run set. The frozen
    baseline is the 499 entries served after 211's consolidation (the 385 pre-211 set plus its 114 builds;
    230 re-baselined it before the Roman re-run). Nothing was removed, and no baseline entry changed
    outside the marker fields 212 later owns."""
    pre = _baseline_entries()
    assert len(pre) == 499, f"the frozen baseline holds {len(pre)} entries, expected 499"
    sites = _site_entries()["sites"]
    assert len({s["id"] for s in sites}) == len(sites), "duplicate site ids in the served file"
    by_id = {s["id"]: s for s in sites}
    for p in pre:
        c = by_id.get(p["id"])
        assert c is not None, f"pre-build site removed from the served file: {p['id']}"
        diff = {k for k in set(c) | set(p) if c.get(k) != p.get(k)}
        outside = diff - set(MARKERS)
        assert not outside, f"pre-build site rewritten: {p['id']}: {sorted(outside)}: {[(p.get(k), c.get(k)) for k in outside]}"


def test_new_sites_are_complete():
    """Box 3, read-only: every site built in this phase is complete by the machinery's own rule - its
    directory exists, the entry carries the fields the page renders, relief.jpg is present exactly when
    the entry credits a LiDAR source, and a site under a coverable old-map layer (depict.LAYERS: covers
    and old enough, year <= now - MIN_AGE_YEARS) has a depictions.json; an aerial-only site correctly
    has none."""
    pre_ids = {s["id"] for s in _baseline_entries()}
    sys.path.insert(0, os.path.join(ROOT, "pipeline"))
    import depict  # noqa: E402  (read-only: covers() is a box check, no network at import)
    newest = time.gmtime().tm_year - depict.MIN_AGE_YEARS
    new = [s for s in _site_entries()["sites"] if s["id"] not in pre_ids]
    assert new, "no new sites: the build phase produced nothing"
    for s in new:
        sdir = os.path.join(ROOT, "web", "data", "sites", s["id"])
        assert os.path.isdir(sdir), f"{s['id']}: no web/data/sites directory"
        for k in ("id", "name", "lon", "lat", "corners", "size_m", "drawings"):
            assert k in s, f"{s['id']}: entry field {k} missing"
        relief = os.path.exists(os.path.join(sdir, "relief.jpg"))
        assert relief == bool(s.get("lidar_credit")), \
            f"{s['id']}: relief.jpg={relief} but lidar_credit={s.get('lidar_credit')!r}"
        coverable = [n for n, L in depict.LAYERS.items()
                     if depict.covers(L, s["lon"], s["lat"]) and L["year"] <= newest]
        if coverable:
            assert os.path.exists(os.path.join(sdir, "depictions.json")), \
                f"{s['id']}: old-map layer {coverable} covers it but depictions.json is missing"


def test_new_site_golden_samples():
    """Box 3: three built sites pinned to the exact values their recorded builds produced - an AHN Dutch
town with the 1850 military map, an aerial-only Belgian city (relief, no depictions), an IGN French city
with the two 18th/19th-century French maps. A regression in the build machinery shows up here."""
    by_id = {s["id"]: s for s in _site_entries()["sites"]}
    samples = {
        "the-hague-q36600": dict(score=0.91, oldest=1850, overlays=1, relief_clip_m=0.65,
                                 lidar_credit="AHN (Rijkswaterstaat)",
                                 files=["relief.jpg", "tmk1850.webp", "depictions.json"]),
        "ostend-q12996": dict(score=0, oldest=None, overlays=0, relief_clip_m=1.2,
                              lidar_credit="Wallonia (EODaS), 2015 (35.06 points/m2)",
                              files=["relief.jpg"],
                              absent=["depictions.json"]),
        "cambrai-q181285": dict(score=1.01, oldest=1780, overlays=2, relief_clip_m=1.2,
                                lidar_credit="IGN, LiDAR HD (Licence Ouverte 2.0)",
                                files=["relief.jpg", "cassini.webp", "etatmajor.webp", "depictions.json"]),
    }
    for sid, exp in samples.items():
        s = by_id[sid]
        sdir = os.path.join(ROOT, "web", "data", "sites", sid)
        for k, v in exp.items():
            if k == "files":
                for f in v:
                    assert os.path.exists(os.path.join(sdir, f)), f"{sid}: missing {f}"
            elif k == "absent":
                for f in v:
                    assert not os.path.exists(os.path.join(sdir, f)), f"{sid}: {f} must not exist (aerial-only site)"
            else:
                assert s.get(k) == v, f"{sid}.{k}: {s.get(k)!r} != {v!r}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
