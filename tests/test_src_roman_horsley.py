"""The Horsley staging (task 809, GOAL point 4): the 17 verified kind-s site-plan maps of Horsley's
*Britannia Romana* (1732) staged by fit/src_roman_horsley.py into the shared roman staging files
(files_roman/classified_roman.jsonl + the 8 new no-QID sites in extras_roman.jsonl; 207b's Maclauchlan
row coexists in the same files, tagged by book). The tests are offline: the no_network fixture
patches the socket connect methods so any network attempt fails loud (urllib.request/ssl are
imported at the top of this file BEFORE the patch - the 809 box's pattern: a naive
`socket.socket = fn` breaks a later `import ssl`, PITFALLS - so the fixture patches the methods,
not the class), and the module is imported by path via importlib, so register(), the join and the
evidence check run from the committed staging files and per-book artifacts only: the LLM never
runs, no fixed ports. The negative controls pin the traps the stored evidence and the join exist
for: a stored distance that does not reproduce from the stored coordinates, a caption that no
longer names the place, a file row whose site exists neither staged nor in the catalog (including
the cascade on a single-picture staged site), and the 211-merge states (pre-merge /
merged-identical / same-id-different-row, plus the QID collision) - all on temp copies, with the
committed files sha256-verified untouched. The golden file (tests/golden/
src_roman_horsley_sample.json) pins the staged rows; it is regenerated only via the module's
--golden flag for an intended change.
"""
import hashlib
import importlib.util
import json
import os
import socket
import sys
import urllib.request  # noqa: F401  the 809 box: import (with ssl) BEFORE no_network patches socket -
import ssl  # noqa: F401  # a naive `socket.socket = fn` breaks a later `import ssl` (PITFALLS)

import pytest

from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in (os.path.join(ROOT, "fit"), os.path.join(ROOT, "pipeline")):
    if d not in sys.path:
        sys.path.insert(0, d)   # BEFORE exec_module: the module's lazy `import evidence` (fit/) resolves via it

_spec = importlib.util.spec_from_file_location("src_roman_horsley",
                                              os.path.join(ROOT, "fit", "src_roman_horsley.py"))
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)

STAGED = 17   # this book's staged kind-s rows (the 24-entry list's 17 kind-s leaves)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The 809 box: these tests are offline by contract; make any network attempt fail loud. The
    fixture patches socket.socket.connect / socket.create_connection / socket.getaddrinfo (methods,
    not the class) because a naive `socket.socket = fn` breaks any later `import ssl` - hence the
    urllib.request/ssl imports at the top of this file."""
    def dead(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket.socket, "connect", dead)
    monkeypatch.setattr(socket, "create_connection", dead)
    monkeypatch.setattr(socket, "getaddrinfo", dead)


def test_register():
    """register() (offline): books.BOOKS gets this book (ia/region/year/cite/why) and the 24-entry
    per-leaf table is injected into books_lists.HAND_FIGS - 24 lines, 17 kind-s (the 15 wall maps +
    n0114 P.44 + n0185 P.113). The LLM never runs in this test."""
    import books
    import books_lists
    h.register()
    b = books.BOOKS[h.KEY]
    assert (b["ia"], b["region"], b["year"], b["cite"], b["why"]) == (h.IA, h.REGION, h.YEAR, h.CITE, h.WHY)
    assert books_lists.HAND_FIGS[h.IA] == h.HORSEY_FIGS
    lines = [l for l in h.HORSEY_FIGS.strip().splitlines() if l.strip()]
    assert len(lines) == 24
    assert sum(1 for l in lines if l.split("|")[3] == "s") == 17


def test_check_offline(capsys):
    """--check, offline (no network, no LLM): the join over the whole staged roman set (this book's
    17 rows + Maclauchlan's 1, coexisting tagged in the shared files) holds, and fit/evidence.py's
    check passes on all 17 of this book's rows from the stored fields alone - including the 8 new
    no-QID extras_roman sites."""
    code = h.check_staged()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "join:" not in out, out
    assert f"evidence: {STAGED} rows, {STAGED} pass, 0 fail, 0 no-tie" in out, out
    line = lambda site, title: f"{'PASS':4s} {'caption_coords':15s} {site}|{title}"  # evidence._line's format
    for l in (line("ardoch", "Innerpeffery camp. and Ardoch camp."),
              line("virosidum", "The five fecondary ftations per lineam valli"),
              line("castrum-segedunum-q637958",
                   "A general map of the Roman walls in the north of England, and so much of the "
                   "adjacent countryes as includes the secondary stations per lineam valli.")):
        assert l in out, f"{l!r} not in:\n{out}"


def test_join_problems():
    """The join holds (join_problems() == []) and the per-row facts it rests on are non-vacuous:
    17 of this book's file rows (+ Maclauchlan's 1 = 18 in the shared file), 18 classified rows 1:1
    with the 18 (site, title) keys, all 9 staged sites have at least one staged picture, and every
    file row's site is a catalog, canonical-extras or staged site."""
    assert h.join_problems() == []
    files = h._load(h.FILES_ROMAN)
    cls = h._load(h.CLASSIFIED_ROMAN)
    sites = h._load(h.EXTRAS_ROMAN)
    mine = [r for r in files if r.get("by") == h.MODULE]
    assert len(mine) == STAGED
    assert len(files) == STAGED + 1 and len(cls) == STAGED + 1   # + 207b's Maclauchlan row
    assert len({(r["site"], r["title"]) for r in files}) == STAGED + 1
    assert Counter((c["site"], c["title"]) for c in cls) == Counter((r["site"], r["title"]) for r in files)
    assert len(sites) == 9 and len({s["id"] for s in sites}) == 9
    pics = Counter(r["site"] for r in files)
    for s in sites:
        assert pics[s["id"]] >= 1, f"staged site {s['id']} has no staged picture"
    known = ({r["id"] for r in h._load(h.SITES_JSONL) if r.get("id")}
             | {r["id"] for r in h._load(h.EXTRAS_CANON) if r.get("id")}
             | {s["id"] for s in sites})
    for r in files:
        assert r["site"] in known, r["site"]


def _copies(tmp_path, monkeypatch):
    """Point the module's five path constants at temp copies of the real files; returns (orig, clean)
    where orig[name] = (real path, sha256) and clean[name] = the parsed rows, so a sub-run can
    corrupt a copy and restore it."""
    names = ("FILES_ROMAN", "CLASSIFIED_ROMAN", "EXTRAS_ROMAN", "SITES_JSONL", "EXTRAS_CANON")
    orig, clean = {}, {}
    for name in names:
        src = getattr(h, name)
        data = open(src, encoding="utf-8").read()
        (tmp_path / os.path.basename(src)).write_text(data, encoding="utf-8")
        monkeypatch.setattr(h, name, str(tmp_path / os.path.basename(src)))
        orig[name] = (src, hashlib.sha256(data.encode("utf-8")).hexdigest())
        clean[name] = [json.loads(l) for l in data.splitlines() if l.strip()]
    return orig, clean


def test_check_negative_controls(tmp_path, monkeypatch, capsys):
    """The traps the stored evidence and the join exist for, on temp copies (the committed staging
    and catalog files are sha256-verified untouched):
      (a) a stored distance that does not reproduce from the stored coordinates -> FAIL, never kept;
      (b) a caption that no longer names the stored place -> FAIL;
      (c) a file row whose site is neither staged nor in the catalog -> the join says so, and the
          cascade: corrupting the ONLY row of a single-picture staged site fires all three join
          problems it implies;
      (d) the 211-merge states, hermetically: pre-merge joins clean, merged-identical joins clean,
          a same-id different canonical row fails the (e) conflict check alone, and (pre-merge) a
          staged QID held by a different catalog site fails (f)."""
    orig, clean = _copies(tmp_path, monkeypatch)

    def rewrite(name, rows):
        with open(getattr(h, name), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def run():
        code = h.check_staged()
        return code, capsys.readouterr().out

    files, cls, sites = clean["FILES_ROMAN"], clean["CLASSIFIED_ROMAN"], clean["EXTRAS_ROMAN"]
    cilurni = next(r for r in files if r["site"] == "cilurni")

    # (a) stored distance 48000 m does not reproduce from the stored coordinates (they are 0 m apart)
    bad = dict(cilurni)
    bad["evidence"] = dict(cilurni["evidence"], dist_m=48000)
    rewrite("FILES_ROMAN", [bad if r is cilurni else r for r in files])
    code, out = run()
    assert code == 1, out
    assert "join:" not in out, out
    expect = f"{'FAIL':4s} {'caption_coords':15s} cilurni|{cilurni['title']}"
    expect += "  stored distance 48000 m does not reproduce (0 m)"
    assert expect in out, out
    assert f"evidence: {STAGED} rows, {STAGED - 1} pass, 1 fail, 0 no-tie" in out, out
    rewrite("FILES_ROMAN", files)

    # (b) a caption that no longer names the stored place (the modern-place substitution the check
    # exists for); the classified row moves with it, so the 1:1 join (tested in (c)) stays clean
    bad = dict(cilurni)
    bad["title"] = "A map of the Roman wall, from HANNAVVM to WEST CHESTERS."
    bad["desc"] = ""
    rewrite("FILES_ROMAN", [bad if r is cilurni else r for r in files])
    rewrite("CLASSIFIED_ROMAN", [dict(c, title=bad["title"])
                                 if c["site"] == "cilurni" and c["title"] == cilurni["title"]
                                 else c for c in cls])
    code, out = run()
    assert code == 1, out
    assert "join:" not in out, out
    expect = f"{'FAIL':4s} {'caption_coords':15s} cilurni|{bad['title']}"
    expect += f"  the caption does not name {cilurni['evidence']['named_place']!r}"
    assert expect in out, out
    assert f"evidence: {STAGED} rows, {STAGED - 1} pass, 1 fail, 0 no-tie" in out, out
    rewrite("FILES_ROMAN", files)
    rewrite("CLASSIFIED_ROMAN", cls)

    # (c) a file row whose site is neither staged nor in the catalog: a two-picture CATALOG site
    # loses one picture - the join fires the unknown-site line and the 1:1 line, and no picture
    # problem (a catalog site is never "staged")
    n236 = next(r for r in files if "n0236" in r["url"])
    rewrite("FILES_ROMAN", [dict(r, site="no-such-site") if r is n236 else r for r in files])
    code, out = run()
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: file row names a site that is neither staged nor existing: "
                    f"'no-such-site' ({n236['title']!r})",
                    "join: the classified rows are not 1:1 with the staged file rows"], join
    assert f"evidence: {STAGED} rows, {STAGED} pass, 0 fail, 0 no-tie" in out, out
    rewrite("FILES_ROMAN", files)

    # (c) cascade: corrupt the ONLY row of a single-picture staged site (n0114 -> ardoch): three
    # join problems fire together (the unknown site, that site's missing picture, the 1:1 mismatch)
    n114 = next(r for r in files if "n0114" in r["url"])
    rewrite("FILES_ROMAN", [dict(r, site="no-such-site") if r is n114 else r for r in files])
    code, out = run()
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: file row names a site that is neither staged nor existing: "
                    f"'no-such-site' ({n114['title']!r})",
                    "join: staged site ardoch has no staged picture",
                    "join: the classified rows are not 1:1 with the staged file rows"], join
    rewrite("FILES_ROMAN", files)

    # (d) the 211-merge states, hermetically: the canonical copies vary, the staged copies stay clean
    staged_ids = {s["id"] for s in sites}
    canon_extras = clean["EXTRAS_CANON"]
    premerge = [r for r in canon_extras if r["id"] not in staged_ids]
    assert len(premerge) == len(canon_extras) - 9

    # (d-a) pre-merge: none of the 9 staged roman sites is in the canonical files yet -> joins clean
    rewrite("EXTRAS_CANON", premerge)
    code, out = run()
    assert code == 0, out
    assert "join:" not in out, out
    assert f"evidence: {STAGED} rows, {STAGED} pass, 0 fail, 0 no-tie" in out, out

    # (d-b) merged-identical: the staged site rows are in the canonical extras, identical -> a no-op
    rewrite("EXTRAS_CANON", canon_extras)
    code, out = run()
    assert code == 0, out
    assert "join:" not in out, out
    assert f"evidence: {STAGED} rows, {STAGED} pass, 0 fail, 0 no-tie" in out, out

    # (d-c) same id, a DIFFERENT canonical row: the (e) conflict protection fires alone
    ardoch = next(r for r in canon_extras if r["id"] == "ardoch")
    rewrite("EXTRAS_CANON", [dict(r, qid="Q99999999") if r is ardoch else r for r in canon_extras])
    code, out = run()
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == ["join: staged site ardoch differs from its canonical row in extras.jsonl"], join
    assert f"evidence: {STAGED} rows, {STAGED} pass, 0 fail, 0 no-tie" in out, out

    # (d-f) pre-merge, a staged QID held by a DIFFERENT existing site: (f) fires
    holder_map = {}
    for p in (h.SITES_JSONL, h.EXTRAS_CANON):
        for r in h._load(p):
            if r.get("qid"):
                holder_map.setdefault(r["qid"], r["id"])
    holder = holder_map["Q39671"]   # stonehenge's item; no staged site holds it in this state
    assert holder != "ardoch"
    rewrite("EXTRAS_ROMAN", [dict(s, qid="Q39671") if s["id"] == "ardoch" else s for s in sites])
    rewrite("EXTRAS_CANON", premerge)
    code, out = run()
    assert code == 1, out
    join = [l for l in out.splitlines() if l.startswith("join:")]
    assert join == [f"join: staged site ardoch re-uses QID Q39671 held by {holder}"], join
    rewrite("EXTRAS_ROMAN", sites)
    rewrite("EXTRAS_CANON", canon_extras)

    # the committed files were never touched
    for name, (src, digest) in orig.items():
        assert hashlib.sha256(open(src, encoding="utf-8").read().encode("utf-8")).hexdigest() == digest, src


def test_golden_matches_staged():
    """tests/golden/src_roman_horsley_sample.json (written by the module's --golden: the four
    tie-flavour file rows in leaf order (114/185/236/278), the new extras_roman sites those rows
    name (ardoch, virosidum), the subset's classified rows, and the WHOLE book's counts
    8/17/17 - dates normalized, keys sorted) is the staged rows re-derived with the module's own
    rules exactly."""
    golden = json.load(open(h.GOLDEN, encoding="utf-8"))
    files = [r for r in h._load(h.FILES_ROMAN) if r.get("by") == h.MODULE]
    leaf = {int(r["url"].rsplit("/n", 1)[1].split(".")[0]): r for r in files}
    sub = [leaf[n] for n in sorted(h.GOLDEN_LEAVES)]
    sids = {r["site"] for r in sub}
    keys = {(r["site"], r["title"]) for r in sub}
    all_keys = {(r["site"], r["title"]) for r in files}
    my_sites = [s for s in h._load(h.EXTRAS_ROMAN) if s.get("source") == h.MODULE]
    sites = [s for s in my_sites if s["id"] in sids]
    cls = [c for c in h._load(h.CLASSIFIED_ROMAN) if (c.get("site"), c.get("title")) in keys]
    assert [int(r["url"].rsplit("/n", 1)[1].split(".")[0]) for r in golden["files"]] == [114, 185, 236, 278]
    assert golden["count"] == {"files": STAGED, "classified": STAGED, "extras": 8}
    assert golden == {"count": golden["count"], "files": h._norm(sub),
                      "extras": h._norm(sites), "classified": h._norm(cls)}
