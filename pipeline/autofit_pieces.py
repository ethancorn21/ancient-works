"""Exploratory (docs/autofit.md section 5): can the local vision model reject the extractor's junk piece by piece?

The auto template is split into pieces (template points closer than 8 px are one piece; pieces under 15 points are
dropped). Each piece is shown to Qwen as a crop of the plate with the piece traced in red, and Qwen names it.
Pieces named "wall" become template auto_qwenpieces (data/autofit/<id>_template_qwenpieces.npz).
Agreement is reported against the hand traces (a piece is "near" when most of its points are within 15 px of a
hand-traced wall; real walls that were never hand traced count as not near, so precision is a lower bound).

usage: autofit_pieces.py [site ...]
"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image, ImageDraw
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import autofit as af  # noqa: E402
import autowalls  # noqa: E402
import llm  # noqa: E402

PROMPT = """This is a crop of a scanned 1848 survey plate of prehistoric earthworks. One drawn feature is traced in red.
What is the red-traced feature? Choose one:
"wall" = an earthwork embankment or enclosure wall (straight walls, circles, parallel walls, rings around mounds),
"water" = a river, creek, pond or its bank,
"road" = a road, canal, railway, fence or field line,
"hill" = a bluff, terrace edge or hill slope,
"other" = lettering, section drawing, border, scale bar, north arrow.
Answer {"kind": "wall" | "water" | "road" | "hill" | "other"}"""


def pieces(P, r=8.0, min_pts=15):
    pairs = cKDTree(P).query_pairs(r, output_type="ndarray")
    A = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(len(P), len(P)))
    n, lab = connected_components(A, directed=False)
    sizes = np.bincount(lab, minlength=n)
    return [np.nonzero(lab == i)[0] for i in range(n) if sizes[i] >= min_pts]


def crop_for(im, pts, max_px=640):
    x0, y0 = pts.min(0)
    x1, y1 = pts.max(0)
    m = max(150, 0.4 * max(x1 - x0, y1 - y0))
    box = (int(max(0, x0 - m)), int(max(0, y0 - m)), int(min(im.width, x1 + m)), int(min(im.height, y1 + m)))
    c = im.crop(box).convert("RGB")
    d = ImageDraw.Draw(c)
    for x, y in pts - np.array(box[:2]):
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(230, 20, 30))
    c.thumbnail((max_px, max_px))
    return c


def classify(sid):
    S = af.Site(sid)
    z = np.load(os.path.join(af.OUT, sid + "_template.npz"))
    P, N, w = z["pts"], z["nrm"], z["w"]
    im = autowalls.load_plate(sid)
    pcs = pieces(P)
    cache = os.path.join(af.OUT, sid + "_pieces_qwen.json")
    old = json.load(open(cache)) if os.path.exists(cache) else {}

    def ask(i):
        key = str(i)
        if key in old.get("answers", {}):
            return old["answers"][key]
        ans = llm.ask_json(PROMPT, images=[crop_for(im, P[pcs[i]])], max_px=640, max_tokens=60)
        return ans.get("kind", "?") if isinstance(ans, dict) else "?"

    with ThreadPoolExecutor(4) as ex:
        kinds = list(ex.map(ask, range(len(pcs))))
    hp, _, _ = af.hand_template(S)
    d, _ = cKDTree(hp).query(P)
    near = [bool((d[ix] < 15).mean() >= 0.5) for ix in pcs]
    json.dump({"answers": {str(i): k for i, k in enumerate(kinds)}, "near_hand": near,
               "n_points": [int(len(ix)) for ix in pcs]}, open(cache, "w"), indent=1)
    wall = [k == "wall" for k in kinds]
    keep = np.concatenate([pcs[i] for i in range(len(pcs)) if wall[i]] or [np.array([], int)])
    np.savez_compressed(os.path.join(af.OUT, sid + "_template_qwenpieces.npz"), pts=P[keep], nrm=N[keep], w=w[keep])
    npts = np.array([len(ix) for ix in pcs])
    wall, near = np.array(wall), np.array(near)
    tp = npts[wall & near].sum()
    print("%-9s %3d pieces; Qwen walls %3d (%5d pts), near-hand %3d (%5d pts); point recall %.2f, point precision %.2f; "
          "kinds %s" % (sid, len(pcs), wall.sum(), npts[wall].sum(), near.sum(), npts[near].sum(),
                        tp / max(npts[near].sum(), 1), tp / max(npts[wall].sum(), 1),
                        {k: kinds.count(k) for k in sorted(set(kinds))}), flush=True)


if __name__ == "__main__":
    for sid in sys.argv[1:] or af.SITES:
        classify(sid)
