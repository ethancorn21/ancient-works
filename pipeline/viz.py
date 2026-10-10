"""Several archaeological views of one LiDAR crop, for the Finder's re-ranker (a vision model sees pictures, so
elevation has to be drawn; each view shows what the others hide).

views(z, px_m) -> dict of uint8 grey images, same size as z:
  relief_s   local relief, 5 m radius     - mounds, narrow walls and ditches
  relief_m   local relief, 15 m radius    - plowed-down walls (the pipeline's usual scale is 24 m)
  relief_l   local relief, 40 m radius    - big enclosures, platform mounds
  svf        sky-view factor, 10 m        - walls and ditches on any slope, independent of light direction
  slope      slope in degrees             - wall flanks, scarps
Fixed stretches (not per-image percentiles), so the same feature looks the same in every crop.
"""
import math

import numpy as np
from scipy.ndimage import gaussian_filter

import aw

CLIPS = {"relief_s": 0.4, "relief_m": 0.6, "relief_l": 1.0}


def _lrm(z, px_m, r_m):
    return z - gaussian_filter(z, r_m / px_m)


def sky_view(z, px_m, r_m=10.0, dirs=16):
    """Share of the sky visible from each point within r_m (1 = open plain, lower = in a ditch or below a wall)."""
    n = max(2, int(round(r_m / px_m)))
    h, w = z.shape
    pad = np.pad(z, n, mode="edge")
    total = np.zeros_like(z)
    for k in range(dirs):
        a = 2 * math.pi * k / dirs
        best = np.full(z.shape, -np.inf)
        for s in range(1, n + 1):
            dy, dx = int(round(-math.sin(a) * s)), int(round(math.cos(a) * s))
            if dy == 0 and dx == 0:
                continue
            dist = math.hypot(dx, dy) * px_m
            nb = pad[n + dy:n + dy + h, n + dx:n + dx + w]
            best = np.maximum(best, (nb - z) / dist)
        total += np.sin(np.arctan(np.maximum(best, 0)))
    return 1 - total / dirs


def views(z, px_m):
    z = aw.fill_nan(z)
    out = {}
    for name, r in (("relief_s", 5.0), ("relief_m", 15.0), ("relief_l", 40.0)):
        c = CLIPS[name]
        out[name] = ((np.clip(_lrm(z, px_m, r) / c, -1, 1) * 0.5 + 0.5) * 255).astype(np.uint8)
    svf = sky_view(z, px_m)
    out["svf"] = (np.clip((svf - 0.94) / 0.06, 0, 1) * 255).astype(np.uint8)  # 0.94..1.00 -> dark..light (a 0.3 m wall dips ~0.02)
    gy, gx = np.gradient(z, px_m)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    out["slope"] = (255 - np.clip(slope / 30, 0, 1) * 255).astype(np.uint8)  # steep = dark
    return out


def panel(v, names=("relief_s", "relief_m", "relief_l", "svf")):
    """The views side by side in one image (for people; the model gets them as separate images)."""
    from PIL import Image
    ims = [Image.fromarray(v[n]) for n in names]
    W = sum(i.width for i in ims) + 8 * (len(ims) - 1)
    out = Image.new("L", (W, ims[0].height), 255)
    x = 0
    for i in ims:
        out.paste(i, (x, 0))
        x += i.width + 8
    return out
