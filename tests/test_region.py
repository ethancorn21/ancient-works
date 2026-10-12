"""A site's region on the page (task 214): build_catalog.make_site shows REGION_NAME.get(region) or "US", so a
region missing from the table silently displays as "US" (213's Italian sites, Imola and Venice, would have).
The audit test reads every region string the data actually uses (data/catalog/*.jsonl, web/data/sites.json)
and fails on one that would fall back to "US" while not being a US site. Offline: a socket-blocking fixture.
"""
import glob
import json
import os
import socket
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import build_catalog  # noqa: E402


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*args, **kwargs):
        raise AssertionError(f"network access attempted: {args} {kwargs}")
    monkeypatch.setattr(socket, "socket", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)


def test_italy_is_not_us():
    site = build_catalog.make_site({"id": "imola-test", "name": "Imola", "lon": 11.71, "lat": 44.35,
                                    "region": "Italy", "box_m": 800})
    assert site["region"] == "Italy"


def _shown(region):
    return build_catalog.REGION_NAME.get(str(region or "").lower()) or "US"


def test_every_region_in_the_data_resolves():
    """No silent US: a region string shows as itself (any case) or as US only when it is a US region (us/US) or
    absent on a row west of 30 W (the US coverage rows carry no region)."""
    rows = []
    for f in glob.glob(os.path.join(ROOT, "data", "catalog", "*.jsonl")):
        for line in open(f):
            if line.strip():
                rows.append(json.loads(line))
    d = json.load(open(os.path.join(ROOT, "web", "data", "sites.json")))
    rows += d["sites"] if isinstance(d, dict) else d
    bad = set()
    for r in rows:
        region, shown = r.get("region"), _shown(r.get("region"))
        if region is None:
            if r.get("lon") is not None and float(r["lon"]) > -30:
                bad.add(("<none>", r.get("id")))
        elif str(region).lower() == "us":
            assert shown == "US"
        elif shown.lower() != str(region).lower():
            bad.add((region, shown))
    assert not bad, f"regions that would display wrongly: {sorted(bad)[:10]}"
