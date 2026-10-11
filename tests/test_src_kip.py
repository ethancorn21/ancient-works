"""The Kip bird's-eye-view inventory (task 205, GOAL.md point 4): fit/src_kip.py holds the 132-file verdict
table for the lead Commons categories (Johannes Kip root + its 5 subcategories; Britannia Illustrata) - the
source of docs/lead_kip.md §1 and §3 - and stages the large scans (long edge >= 1000 px) of UK country
houses and gardens into this task's staging files; 211 consolidates and builds. The staging-file tests
(join, evidence check, golden) arrive with the staging files; these tests pin what exists now: the
inventory's own rules (the 1000 px threshold, the verdict tally, the six hand-tied titles that must never
be re-staged - cross-checked against pipeline/sources.py's KIP table and the canonical files.jsonl) and
the lead-doc mirror (its §3 table and §1 headline numbers must equal the module's INVENTORY, so a doc edit
that drifts from the inventory fails loud). Offline: a socket-blocking fixture makes any network attempt
fail loud."""
import json
import os
import socket
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in (os.path.join(ROOT, "fit"), os.path.join(ROOT, "pipeline")):
    if d not in sys.path:
        sys.path.insert(0, d)
import sources  # noqa: E402  pipeline/sources.py (the KIP table the six hand-tied titles must equal)
import src_kip  # noqa: E402  fit/src_kip.py, the module under test

LEAD = os.path.join(ROOT, "docs", "lead_kip.md")
FILES = os.path.join(ROOT, "data", "commons", "files.jsonl")
TALLIES = {  # the §3 tally, in the document's order
    "staged": 12, "hand-tied": 6, "drop: review-queue": 4, "drop: duplicate impression": 11,
    "drop: not a house": 18, "drop: church": 7, "drop: foreign": 19, "drop: city prospect": 11,
    "drop: photo": 8, "drop: too small": 36,
}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """The inventory work is offline by contract; make any network attempt in this module's tests fail loud."""
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def _bare(t):
    assert t.startswith("File:")
    return t[5:]


def test_inventory_thresholds_and_tally():
    """The 132-row verdict table is complete and consistent with the 1000 px threshold rule (the §1 claim):
    every staged view is fit-sized, every 'too small' drop is not, nothing 'too small' falls in the
    900-1000 band, and the tally per verdict group is the §3 one (so box 1 is machine-checkable)."""
    rows = src_kip.INVENTORY
    assert len(rows) == 132 and len({r[0] for r in rows}) == 132
    assert all(len(r) == 5 and isinstance(r[1], int) and isinstance(r[2], int) and r[1] > 0 and r[2] > 0
               and r[4].strip() for r in rows)
    assert all(r[3] in TALLIES for r in rows)
    tally = {}
    for r in rows:
        tally[r[3]] = tally.get(r[3], 0) + 1
    assert tally == TALLIES
    staged = [r for r in rows if r[3] == "staged"]
    too_small = [r for r in rows if r[3] == "drop: too small"]
    assert all(max(r[1], r[2]) >= src_kip.MIN_EDGE for r in staged)
    assert all(max(r[1], r[2]) < src_kip.MIN_EDGE for r in too_small)
    assert min(max(r[1], r[2]) for r in staged) == 1375  # Kingsweston, the smallest staged view
    assert max(max(r[1], r[2]) for r in too_small) == 822  # Siston Court, the largest drop
    band = [r for r in rows if 900 <= max(r[1], r[2]) < 1000]
    # the threshold needs no exception list: the three files in the band drop for their own reasons
    assert {r[3] for r in band} == {"drop: foreign", "drop: duplicate impression", "drop: church"}
    assert len([r for r in rows if max(r[1], r[2]) >= 1000]) == 92


def test_hand_tied_is_the_sources_kip_table_and_never_re_staged():
    """The six 'hand-tied' verdicts are exactly pipeline/sources.py's KIP table, and exactly the six
    canonical files.jsonl rows it produced (kind hand_tied) - they are the views that must never be
    re-staged (their evidence kind stays 'hand-tied QID')."""
    kip = sources.SOURCES["kip"]["rows"]
    assert len(kip) == 6
    hand_tied = {r[0] for r in src_kip.INVENTORY if r[3] == "hand-tied"}
    assert hand_tied == {r[0] for r in kip}
    assert {r[1] for r in kip} == {"Q1443802", "Q1070927", "Q5049456", "Q1074877", "Q17530246", "Q225471"}
    canonical = [json.loads(l) for l in open(FILES, encoding="utf-8") if l.strip()]
    rows = [r for r in canonical if r.get("by") == "pipeline/sources.py kip"]
    assert {r["title"] for r in rows} == hand_tied
    assert all(r["evidence"]["kind"] == "hand_tied" for r in rows)
    for p in (src_kip.FILES_KIP, src_kip.CLASSIFIED_KIP):  # the six never land in the staging files
        for r in src_kip._load(p):
            assert r["title"] not in hand_tied, f"{p}: {r['title']} re-stages a hand-tied view"


def test_lead_doc_mirrors_the_inventory():
    """docs/lead_kip.md §3 is the INVENTORY table row for row (size, verdict, reason; the date column is
    dump-derived and not pinned here), and §1's headline numbers (category counts, the 1000 px threshold,
    the 92/40 split, the 822/1375 extremes, the out-of-scope siblings, the six hand-tied with their QIDs)
    match the module - a doc edit that drifts from the inventory fails loud."""
    text = open(LEAD, encoding="utf-8").read()
    sec3 = text.split("## 3. ", 1)[1].split("\n## 4.", 1)[0]
    rows = [[c.strip() for c in line.split("|")[1:-1]] for line in sec3.splitlines()
            if line.startswith("|") and line.count("|") == 6]
    data = [r for r in rows if r[0].strip() != "File" and not set(r[0].strip()) <= {"-"}]
    assert len(data) == 132  # the 132 inventory rows (header and --- separator skipped by name, not index)
    inv = {}
    for t, w, h, v, reason in src_kip.INVENTORY:
        assert _bare(t) not in inv
        inv[_bare(t)] = (f"{w} × {h}", v, reason)
    for bare, size, _date, verdict, reason in data:
        assert bare in inv, f"doc row not in the inventory: {bare[:60]}"
        assert (size, verdict, reason) == inv[bare], f"doc drift for {bare[:60]}"
    assert {d[0] for d in data} == set(inv)
    tally_line = next(l for l in sec3.splitlines() if l.startswith("Tally:"))
    for v, n in TALLIES.items():
        assert f"{v} {n}" in tally_line, tally_line
    # §1 headline numbers
    sec1 = text.split("## 1.", 1)[1].split("## 2.", 1)[0]
    for needle in (
        "| `Johannes Kip` (root) | 65 |",
        "| **distinct** | **132** | **92** |",
        "long edge ≥ 1000 px",
        "92 of the 132 files are fit-sized, 40 are under 1000 px",
        'largest file dropped as "too small" is 822 px',
        "smallest staged view is 1375 px",
        "`Category:Jan Kip` = 5 files",
        "`Category:History of Kent` = 29 files",
    ):
        assert needle in sec1, f"missing in §1: {needle}"
    for t, qid, *_ in sources.SOURCES["kip"]["rows"]:
        assert f"{_bare(t)} | " in sec1 and qid in sec1, f"hand-tied {t[:40]} missing from §1"
