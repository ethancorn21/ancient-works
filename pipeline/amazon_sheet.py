"""Contact sheet of the top candidates of one amazon_find.py run, for checking by eye (stays on this Mac).

usage: amazon_sheet.py <dtm.npz|dtm.tif> <cands.json> <out.jpg> [n=30] [det=ring|enclosure|all]
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amazon_find as F  # noqa: E402
import aw  # noqa: E402


def main(src, cands, out, n=30, det="all"):
    z, valid, px, meta = F.load(src)
    zo = ndimage.grey_opening(aw.fill_nan(z), size=(3, 3))
    img, _ = aw.render_relief(np.where(valid, zo, np.nan), px, clip_m=1.0, radius_m=30)
    img[~valid] = 255
    cs = [c for c in json.load(open(cands))["candidates"] if det == "all" or c["det"] == det][:n]
    T = 220
    S = Image.new("RGB", (6 * T, ((len(cs) + 5) // 6) * (T + 16)), "white")
    d0 = ImageDraw.Draw(S)
    for i, c in enumerate(cs):
        half = int(max(60, 2.2 * c["r_m"]) / px)
        r0, c0 = int(c["row"]), int(c["col"])
        pad = np.pad(img, half, constant_values=255)
        crop = pad[r0:r0 + 2 * half, c0:c0 + 2 * half]
        im = Image.fromarray(crop).convert("RGB").resize((T, T))
        d = ImageDraw.Draw(im)
        k = T / (2 * half)
        rr = c["r_m"] / px * k
        d.ellipse([T / 2 - rr, T / 2 - rr, T / 2 + rr, T / 2 + rr], outline=(220, 40, 40), width=1)
        x, y = (i % 6) * T, (i // 6) * (T + 16)
        S.paste(im, (x, y))
        sc = c.get("vscore", c.get("score"))
        d0.text((x + 3, y + T + 2), f"{i + 1} {c['det'][:4]} r{c['r_m']:.0f} s{sc:.2f}", fill=(0, 0, 0))
    S.save(out, quality=85)
    print(out, len(cs))


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2], int(a[3]) if len(a) > 3 else 30, a[4] if len(a) > 4 else "all")
