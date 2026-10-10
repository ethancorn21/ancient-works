"""Contact sheet of ranked Finder candidates (tune area, or any area's exported list) for checking by eye.

usage: finder_sheet.py <area> <ranker> <start> <n> <out.jpg>
Never run on held-out areas before the final evaluation.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from finder_common import AREAS  # noqa: E402
from finder_rerank import render  # noqa: E402


def main(area, ranker, start, n, out):
    if AREAS.get(area, (0, 0, 0, 0, "tune"))[4] == "heldout" and os.environ.get("FINAL") != "1":
        raise SystemExit("held-out area: set FINAL=1 only after the final evaluation")
    import finder_rank as fr
    cands = fr.ranked(area, ranker)[start:start + n]
    panels = []
    for i, c in enumerate(cands):
        half = 150 if c["kind"] == "mound" else max(150, 1.6 * c["r_m"])
        im = render(c["lon"], c["lat"], "relief_s", half).resize((300, 300))
        d = ImageDraw.Draw(im)
        if c["kind"] == "mound":
            txt = f"#{start + i + 1} M h{c['h_m']} d{c['diam_m']} r{c['round']} sl{c['base_slope']} snr{c['snr']}"
        else:
            txt = f"#{start + i + 1} R r{c['r_m']} snr{c['snr']} bs{c.get('band_slope')}"
        if c.get("p_reranker") is not None:
            txt += f" p{c['p_reranker']:.2f}"
        d.rectangle((0, 0, 300, 12), fill=(255, 255, 255))
        d.text((2, 0), txt, fill=(0, 0, 0))
        panels.append(im)
    cols = 6
    S = Image.new("RGB", (cols * 304, math.ceil(len(panels) / cols) * 304), "white")
    for i, p in enumerate(panels):
        S.paste(p, ((i % cols) * 304, (i // cols) * 304))
    S.save(out, quality=85)
    print("wrote", out)


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], int(a[3]), int(a[4]), a[5])
