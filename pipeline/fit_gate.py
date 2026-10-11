"""The fit gate: does a proposed fit of an old drawing (anchor pairs plus a placement) pass the
pre-registered rule of docs/gate.md section 2, and so deserve to be shown on the map without a human
looking at it?

usage: as a module - gate(pairs, transform=None) -> (verdict, stats). pairs are rows [u, v, lon, lat]
(plate pixel -> ground point, the doc's recorded anchors); transform is the claimed placement as a
Web-Mercator similarity (a, b) with T(w) = k*(a*w + b), w = u - i*v, k = cos(mean anchor latitude) -
None means solve it, exactly as plan_fit.similarity does. verdict is ACCEPT or REJECT, stats is
{n, med, slope_o, io} in ground metres. No images, no network: numpy only, aw and plan_fit imported
read-only. The thresholds are the frozen constants of section 2, tuned on the 12 dev documents
(section 5) before the one-shot held-out run (section 6); they are never re-tuned on held-out data.
The gate cannot see a consistent global error (anchors and placement wrong together): section 7
documents that limit and its backstops (the review queue and the human's sample of accepted fits).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import plan_fit  # noqa: E402

# The frozen rule, docs/gate.md section 2 (all values ground metres). Chosen on the dev documents only
# (section 5) and committed before the gate ever saw the held-out set (section 1); changing them on
# held-out evidence would void the registration.
N_MIN = 3          # fewer anchors: the statistics are noise (production asks the model for >= 4)
RHO2_MIN = 1.0     # m^2: below this the anchors have no radial spread and the pattern statistics are undefined
MED_MAX = 45.0     # a 60 m move and any cross-site placement sit far above the worst true fit
SLOPE_MAX = 0.145  # a 10 degree turn adds 2*sin(5 deg) = 0.1745 per metre of radius; this sits ~20% below
SLOPE_PATTERN = 0.11  # with the inner/outer clause below, catches the 15% scale whose slope is attenuated at n = 3-6
IO_MIN = -10.0     # the radial gradient a true fit does not have: inner-half residuals smaller than outer-half's

ACCEPT = "accept"
REJECT = "reject"


def placement(pairs, transform=None):
    """The placement's image of each anchor, in ground metres, plus the anchors' ground points and k.

    transform is a Web-Mercator similarity (a, b) - the placement's own coordinates; None solves the
    canonical similarity from the pairs, exactly plan_fit.similarity (docs/gate.md section 2).
    """
    p = np.asarray(pairs, float)
    if p.ndim != 2 or p.shape[1] != 4:
        raise ValueError("pairs: rows of [u, v, lon, lat]")
    w = p[:, 0] - 1j * p[:, 1]
    xy = np.array([aw.to_merc(lon, lat) for lon, lat in p[:, 2:4]])
    z = xy[:, 0] + 1j * xy[:, 1]  # the recorded anchor ground points, in Mercator metres
    k = aw.ground_scale(float(p[:, 3].mean()))
    if transform is None:
        a, b = plan_fit.similarity(pairs)[:2]
    else:
        a, b = transform
    return k * (a * w + b), z, k


def score(pairs, transform=None):
    """Per anchor, ground metres (docs/gate.md section 2): r_i = how far the placement puts anchor i from
    where the doc recorded it; rho_i = its distance from C, the centroid of the placement's own anchors."""
    t, z, k = placement(pairs, transform)
    c = t.mean()
    return np.abs(t - k * z), np.abs(t - c)


def _inner_outer(r, rho):
    """io: inner-half minus outer-half mean residual, halves split by rho (odd n: drop the middle anchor
    first). Undefined for n < 2."""
    n = len(r)
    if n < 2:
        return float("nan")
    r = r[np.argsort(rho, kind="stable")]
    if n % 2:
        r = np.delete(r, n // 2)
    h = len(r) // 2
    return float(r[:h].mean() - r[-h:].mean())


def gate(pairs, transform=None):
    """(verdict, stats): the frozen rule of docs/gate.md section 2 applied to this placement against its
    recorded anchors - REJECT if n < N_MIN or sum(rho^2) < RHO2_MIN (degenerate) or med > MED_MAX or
    slope_o > SLOPE_MAX or (slope_o > SLOPE_PATTERN and io < IO_MIN); otherwise ACCEPT. stats is
    {n, med, slope_o, io}; slope_o and io are nan when the anchors are degenerate. A consistent global
    error (anchors and placement both off) passes: the limit documented in section 7."""
    r, rho = score(pairs, transform)
    n = len(r)
    rho2 = float(np.sum(rho ** 2))
    degenerate = n < N_MIN or rho2 < RHO2_MIN
    med = float(np.median(r)) if n else float("nan")
    slope_o = float(np.sum(r * rho) / rho2) if not degenerate else float("nan")
    io = _inner_outer(r, rho) if not degenerate else float("nan")
    accept = not degenerate and med <= MED_MAX and slope_o <= SLOPE_MAX \
        and not (slope_o > SLOPE_PATTERN and io < IO_MIN)
    return (ACCEPT if accept else REJECT), {"n": n, "med": med, "slope_o": slope_o, "io": io}
