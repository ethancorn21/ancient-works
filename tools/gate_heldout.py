"""The one-shot measurement of the fit gate on the hand fits (docs/gate.md, sections 3-6).

Deterministic, offline, numpy only - no network, no ports, no writes. For each document of a set
(default held; `--set dev` for the 12 documents the thresholds were chosen on) it re-derives the
registered partition (the 20 document names section 3 registered - the frozen set is those names,
not whatever is in the directory - sorted, seed 20260108; every document added after the
registration is excluded from the one-shot proof, the automatic ones (`"auto": true`, the batch's
own output) and new hand fits (which stay subject to the production fit gate, fit_gate.gate, at
fit time and are never scored here); it fails loudly if a registered name is not among the
NON-automatic documents - renamed, deleted, or gained `"auto": true` - because then the
registration is void), builds the five placements of section 4 - true; moved 60 m NE; turned 10 deg; scaled 15% (each about the
placement's centroid); cross-site, re-centred onto the next site's box centre, cycling - and
scores each with fit_gate.gate, printing one machine-stable line per (doc, case):

    <doc>  <case>  n=<n>  med=<med>  slope_o=<slope_o>  io=<io>  <verdict>

The section-6 command is `.venv/bin/python tools/gate_heldout.py`; its stdout (40 lines for held,
60 for dev) is what section 9 records. It only reads data/db/platefits/*.json and
web/data/sites.json (both read-only per GOAL); the partition step reads each document only for its
`auto` flag, and the held-out documents' contents are scored by this tool only in the one-shot run.
The five recipes are section 4 in Web-Mercator (a, b) form - the full a*w + b composition, not the
short form (see PITFALLS, "composing a rotated/scaled Web-Mercator similarity about a centroid").
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import aw  # noqa: E402
import fit_gate  # noqa: E402
import plan_fit  # noqa: E402

SEED = 20260108  # the registered winning seed (docs/gate.md section 3)

# The sets registered in docs/gate.md section 3 (names only). They are the frozen set: the
# one-shot proof is about exactly these 20 names, not whatever is in data/db/platefits/.
# Documents added after the registration are excluded from the proof - the batch's automatic
# output ("auto": true) and any new hand fit, which stays subject to the production fit gate
# (fit_gate.gate) at fit time; both only ever ADD names. If a registered name stops being a
# non-automatic document (renamed, deleted, or gained "auto": true) the registered partition is
# void: fail loudly instead of scoring a silently different set.
REGISTERED = {
    "held": [
        "arbor-low-q630312.earthworkenglan01allcgoog_n0597_1",
        "avebury-q661855.earthworkenglan01allcgoog_n0581_1",
        "aztalan-state-park-q4832928.antiquitiesofwis00saph_n0182_1",
        "badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1",
        "cadbury-castle-q1025082.c_1fab2a0abe5b99d7",
        "cahokia-q333661.c_aff1b996dce7fe3a",
        "camp-d-attila-q18749222.c_6a912845c1e1aa28",
        "old-sarum-q782719.earthworkenglan01allcgoog_n0142_1",
    ],
    "dev": [
        "bergues-q244934.c_4bbca705be732b1c",
        "berkhamsted-castle-q4892150.c_1699141d593ead5a",
        "calleva-atrebatum-q1027253.earthworkenglan01allcgoog_n0360_1",
        "castle-rising-castle-q1049485.c_70f937b71ae63d6a",
        "hembury-q3784763.earthworkenglan01allcgoog_n0108_1",
        "little-solsbury-hill-q548780.c_7ff7261c6b3574b6",
        "maiden-castle-q1232816.earthworkenglan01allcgoog_n0124_1",
        "mayburgh-henge-q1469390.c_984782b9e35e8ded",
        "mound-bottom-q14710093.c_0b98157d7af17d6e",
        "old-sarum-q782719.c_8192abb966d030a3",
        "serpent-mound-q968802.ancientmonuments00squi_n0210_1",
        "whitley-castle-q7996561.c_802bb5ba395d4d29",
    ],
}

CASES = ("true", "moved", "rot10", "scale15", "xsite")


def partition(platefits_dir=None):
    """(names, held, dev): the registered partition re-derived over the 20 document names
    docs/gate.md section 3 registered - the frozen set is those names, not whatever is in the
    directory. Post-registration documents are excluded from the one-shot proof: a doc's
    "auto": true is the batch's own output (fit/batch_us.py), and any later hand fit stays
    subject to the production fit gate (fit_gate.gate) at fit time, which this tool never
    re-scores here. Both only ever ADD names, so the derivation is the same before and after
    any batch or new hand fit. A registered name missing from the non-automatic documents
    (renamed, deleted, or gained "auto": true) voids the registration: fail loudly instead of
    scoring a silently different set. Sort the 20 names, seed 20260108 picks 8 positions
    (docs/gate.md section 3), dev is the rest."""
    if platefits_dir is None:
        platefits_dir = os.path.join(ROOT, "data", "db", "platefits")
    non_auto = [os.path.basename(p)[:-5]
                for p in sorted(glob.glob(os.path.join(platefits_dir, "*.json")))
                if not json.load(open(p)).get("auto")]  # a doc without the field is a hand fit
    registered = set(REGISTERED["held"]) | set(REGISTERED["dev"])
    missing = sorted(registered - set(non_auto))
    if missing:
        raise SystemExit(
            f"gate_heldout: registered documents missing from the non-automatic documents in "
            f"data/db/platefits/ (renamed, deleted, or gained \"auto\": true): {missing}; "
            "the registered partition is void, see docs/gate.md section 1")
    names = sorted(registered)
    held = sorted(names[int(i)] for i in np.random.default_rng(SEED).choice(20, 8, replace=False))
    dev = [n for n in names if n not in set(held)]
    return names, held, dev


def check_registered(held, dev):
    """Fail loudly if the seed no longer reproduces the registered names (a silent set change
    would turn the held-out set into dev data and void the measurement)."""
    for which, derived in (("held", held), ("dev", dev)):
        if derived != REGISTERED[which]:
            raise SystemExit(
                f"gate_heldout: seed {SEED} no longer reproduces the {which} set registered in "
                f"docs/gate.md section 3 (registration void); derived: {derived}")


def load_sites():
    return {s["id"]: s for s in json.load(open(os.path.join(ROOT, "web", "data", "sites.json")))["sites"]}


def box_centre_ground(site):
    """Ground-metre centre of a site's box: the mean of its corners in Mercator metres, scaled by
    k at the site's latitude (the same computation the dev calibration used)."""
    pts = [aw.to_merc(*c) for c in site["corners"]]
    k = aw.ground_scale(site["lat"])
    return k * (sum(p[0] for p in pts) / len(pts) + 1j * sum(p[1] for p in pts) / len(pts))


def placements(name, doc, site_ids, sites):
    """The five placements of docs/gate.md section 4 as Web-Mercator (a, b) pairs for this
    document's anchors. true is the canonical similarity solved from D's own pairs; moved, rot10
    and scale15 are about the placement's centroid; xsite re-centres onto the next site's box
    centre (section 4's stand-in for the best placement the search finds on another site)."""
    pairs = doc["pairs"]
    p = np.asarray(pairs, float)
    sid = doc["site"]
    if sid != name.split(".")[0]:
        raise SystemExit(f"gate_heldout: {name}: doc site {sid!r} != the name's site prefix")
    a, b = plan_fit.similarity(pairs)[:2]
    k = aw.ground_scale(float(p[:, 3].mean()))
    w = p[:, 0] - 1j * p[:, 1]
    c_m = (a * w + b).mean()  # placement centroid, Mercator metres
    c = k * c_m               # placement centroid, ground metres
    r10 = np.exp(1j * math.radians(10))
    next_sid = site_ids[(site_ids.index(sid) + 1) % len(site_ids)]
    return {
        "true": (a, b),
        "moved": (a, b + (60 / math.sqrt(2)) * (1 + 1j) / k),
        "rot10": (r10 * a, r10 * b + (1 - r10) * c_m),
        "scale15": (1.15 * a, 1.15 * b - 0.15 * c_m),
        "xsite": (a, b + (box_centre_ground(sites[next_sid]) - c) / k),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="score the five docs/gate.md section-4 placements of a "
                                             "set of hand fits with the fit gate")
    ap.add_argument("--set", choices=("held", "dev"), default="held")
    args = ap.parse_args(argv)
    _names, held, dev = partition()
    check_registered(held, dev)
    chosen = sorted(held if args.set == "held" else dev)
    site_ids = sorted({doc_site for doc_site in (n.split(".")[0] for n in chosen)})
    sites = load_sites()
    for name in chosen:
        doc = json.load(open(os.path.join(ROOT, "data", "db", "platefits", name + ".json")))
        for case in CASES:
            verdict, stats = fit_gate.gate(doc["pairs"], placements(name, doc, site_ids, sites)[case])
            print(f"{name}  {case}  n={stats['n']}  med={stats['med']:.1f}  "
                  f"slope_o={stats['slope_o']:.4f}  io={stats['io']:.1f}  {verdict}")


if __name__ == "__main__":
    main()
