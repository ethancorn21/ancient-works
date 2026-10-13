"""The batch, parent (task 203 box 6, GOAL.md point 1): the final coverage check over the
original site set.

The 203a/203b batches ran the fitting loop over the 384 built sites that existed before
the source growth (204-210) and 211's merge; this test re-checks the live checkout that
every one of them is still covered - a fit (any platefits doc naming the site, automatic
or hand, or the old-style site.json plate fit) or an open review item - so that a later
change (a merge, a 212 sync, a fit taken off the map) can never leave an original site
without either. The growth's new sites are 212's assertion (tests/test_cover.py), not
here.

The original set is the union of the two batches' committed records: the "Per candidate"
tables of docs/batch_us.md and docs/batch_eu.md, each batch's list of every site it ran
(90 US + 294 non-US, disjoint, matching each report's "Sites run" line, 384 total - the
pre-growth population of 203's box 1).

"Open" is 201's derivation (fit/review.resolved_doc), not the item file's recorded
``resolved``: a recorded resolution counts only while its document exists, so a fit
taken off the map (Aesica's automatic doc rejected on sight, 2026-10-11) brings its item
back to the queue and keeps the site covered. The page file (web/data/review.json) is
checked too: a site whose only coverage is an open item must be in the exported open
list, because that is what the page's Review section shows the human.

Read-only over the live checkout (the pattern of test_batch_eu.test_union_full_coverage_
live): no network (a socket guard fails loudly), no server, no writes, no temp tree.
"""
import json
import os
import re
import socket
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "fit"))
import batch_us  # noqa: E402  (the batches' sites.json reader)
import review  # noqa: E402  (201's open-item derivation)

US_REPORT = os.path.join(ROOT, "docs", "batch_us.md")
EU_REPORT = os.path.join(ROOT, "docs", "batch_eu.md")
# The pre-growth population: the built sites the two batches ran (203's box 1: "90 of 384")
ORIGINAL_TOTAL = 384


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Hermetic: every connection attempt fails loudly (this test only reads local files)."""
    def dead(*_a, **_k):
        raise AssertionError("the batch coverage test attempted a network connection")
    monkeypatch.setattr(socket.socket, "connect", dead)
    monkeypatch.setattr(socket, "create_connection", dead)


# ---------------------------------------------------------------- helpers


def _sites():
    return batch_us._sites(ROOT)


def _report_sites(path):
    """The distinct site ids of a batch report's "Per candidate" table, in order."""
    sites, seen = [], set()
    in_sec = False
    for ln in Path(path).read_text().splitlines():
        if ln.startswith("## Per candidate"):
            in_sec = True
            continue
        if in_sec and ln.startswith("## "):
            break
        if in_sec and ln.startswith("|"):
            sid = ln.strip("|").split("|")[0].strip()
            if sid and sid not in ("site", "---") and sid not in seen:
                seen.add(sid)
                sites.append(sid)
    return sites


def _sites_run(path):
    """The report's "Sites run" line (the batch's own record of its population)."""
    m = re.search(r"Sites run: (\d+)", Path(path).read_text())
    assert m, "%s has no 'Sites run' line" % path
    return int(m.group(1))


def _original_set():
    """(us, eu): the original pre-growth site set from the two committed batch reports."""
    return _report_sites(US_REPORT), _report_sites(EU_REPORT)


@pytest.fixture()
def coverage():
    """The live coverage of every site, indexed once: platefits docs by site field,
    review items by site field, old-style site.json plate fits on demand."""
    docs, items = {}, {}
    d = Path(ROOT) / "data" / "db" / "platefits"
    if d.is_dir():
        for p in sorted(d.iterdir()):
            if p.suffix != ".json":
                continue
            doc = json.loads(p.read_text())
            if doc.get("site"):
                docs.setdefault(doc["site"], []).append(p.name)
    r = Path(ROOT) / "data" / "review"
    if r.is_dir():
        for p in sorted(r.iterdir()):
            if p.suffix != ".json":
                continue
            it = json.loads(p.read_text())
            if it.get("site"):
                items.setdefault(it["site"], []).append((p.name, it))

    def hand(sid):
        p = Path(ROOT) / "data" / "sites" / sid / "site.json"
        if p.is_file():
            try:
                return bool(((json.loads(p.read_text()).get("plate") or {}).get("fit")))
            except ValueError:
                pass
        return False

    return {"docs": docs, "items": items, "hand": hand}


# ---------------------------------------------------------------- tests


def test_original_set_is_the_reports_union():
    """The set for box 6 and the reports' agreement (box 5): the two partitions are
    disjoint, each "Per candidate" table matches its report's "Sites run" line, their
    union is the pre-growth 384, the region-less originals sit in the EU table, and no
    original site was lost from sites.json by the later merges."""
    us, eu = _original_set()
    assert us and eu
    assert not set(us) & set(eu), "a site in both batch reports: %s" % sorted(set(us) & set(eu))
    assert len(us) == _sites_run(US_REPORT), \
        "the US table (%d sites) does not match its 'Sites run' (%d)" % (len(us), _sites_run(US_REPORT))
    assert len(eu) == _sites_run(EU_REPORT), \
        "the EU table (%d sites) does not match its 'Sites run' (%d)" % (len(eu), _sites_run(EU_REPORT))
    orig = set(us) | set(eu)
    assert len(orig) == ORIGINAL_TOTAL, \
        "the original site set is %d, expected %d (the pre-growth population)" % (len(orig), ORIGINAL_TOTAL)
    sites = _sites()
    assert orig <= set(sites), \
        "original sites lost from sites.json: %s" % ", ".join(sorted(orig - set(sites)))
    regionless = {sid for sid in orig if not sites[sid].get("region")}
    assert regionless <= set(eu), \
        "region-less original sites missing from the EU table: %s" % sorted(regionless - set(eu))


def test_original_sites_still_covered(coverage):
    """Box 6: every original site still has a fit or an open review item. Fit = any
    platefits doc naming the site (automatic or hand) or the old-style site.json plate
    fit; open = 201's derivation (a recorded resolution stops counting when its document
    is gone). A site covered by an open item only must also be in the page's exported
    open list, since that is what the human sees in the Review section."""
    us, eu = _original_set()
    orig = sorted(set(us) | set(eu))
    docs, items, hand = coverage["docs"], coverage["items"], coverage["hand"]

    missing, item_only = [], []
    for sid in orig:
        has_doc = bool(docs.get(sid))
        has_hand = hand(sid)
        open_items = [name for name, it in items.get(sid, [])
                      if review.resolved_doc(it, ROOT) is None]
        if not (has_doc or open_items or has_hand):
            missing.append(sid)
        elif not has_doc and not has_hand:
            item_only.append(sid)
    assert not missing, "original sites without a fit or an open item: %s" % ", ".join(missing)

    page_path = Path(ROOT) / "web" / "data" / "review.json"
    assert page_path.is_file(), \
        "web/data/review.json missing: the page's Review section would show no items"
    page = {e.get("site") for e in json.loads(page_path.read_text())["items"]}
    absent = [sid for sid in item_only if sid not in page]
    assert not absent, \
        "open items the page's Review section does not show: %s" % ", ".join(absent)
