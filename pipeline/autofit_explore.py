"""Exploratory runs after the pre-registered verdict (docs/autofit.md section 5). Not part of the criterion.

usage: autofit_explore.py <wide|tight> <hand|auto|auto_oracle|auto_qwenpieces> [site ...]
  tight seeds: scale x U(0.95, 1.05), rotation +- 3 deg, centre within 50 m (a scale bar and north arrow read
               correctly, coordinates good to 50 m); window rotation +- 6 deg, scale x0.92-x1.09, shift +- 80 m
               (the size of the hand-set windows fit_plate.py used).
  auto_oracle: the auto template's points within 15 plate px of the hand-traced walls only, i.e. perfect junk
               rejection, as if a person clicked the wall pieces. Uses the hand traces, so it is an upper bound.
Writes data/autofit/results_x_<seeds>_<kind>.json.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import autofit as af  # noqa: E402


def tight_seeds():
    rng = np.random.default_rng(af.RNG_SEED + 1)
    out = {}
    for sid in af.SITES:
        out[sid] = []
        for _ in range(af.N_SEEDS):
            k = rng.uniform(0.95, 1.05)
            dr = rng.uniform(-3, 3)
            rad = 50 * math.sqrt(rng.uniform())
            ang = rng.uniform(0, 2 * math.pi)
            out[sid].append(dict(scale_factor=k, rot_offset_deg=dr, centre_offset_m=[rad * math.cos(ang), rad * math.sin(ang)]))
    return out


_load = af.load_template


def load_template(S, kind):
    if kind != "auto_oracle":
        return _load(S, kind)
    from scipy.spatial import cKDTree
    P, N, w = _load(S, "auto")
    hp, _, _ = af.hand_template(S)
    d, _ = cKDTree(hp).query(P)
    keep = d < 15
    return P[keep], N[keep], w[keep]


if __name__ == "__main__":
    mode, kind = sys.argv[1], sys.argv[2]
    af.load_template = load_template
    if mode == "tight":
        af.make_seeds = tight_seeds
        af.WIN_ROT, af.WIN_LOGS, af.WIN_T = math.radians(6), (math.log(0.92), math.log(1.09)), 80.0
    af.run("x_%s_%s" % (mode, kind), kind, sys.argv[3:] or af.SITES)
