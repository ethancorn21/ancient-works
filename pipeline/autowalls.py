"""Automatic wall template from a survey plate's ink (no hand tracing).

The plate crop is rebuilt from the leaf scan WITHOUT the hand blank boxes (see docs/autofit.md), so lettering,
north arrows, scale bars, section drawings, hachure, tree stipple and the engraver's ground tint are all present
and must be dropped here.

usage: autowalls.py [site ...]   writes data/autofit/<id>_template.npz and data/autofit/<id>_walls.jpg
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "autofit")


def load_plate(sid):
    """The plate crop in the same pixel frame as data/sites/<id>/plate_scan.jpg, without hand blanks."""
    sdir = os.path.join(ROOT, "data", "sites", sid)
    spec_path = os.path.join(ROOT, "specs", sid + ".json")
    if not os.path.exists(spec_path):  # fudge: no spec, and its plate_scan.jpg carries no blanks
        return Image.open(os.path.join(sdir, "plate_scan.jpg")).convert("RGB")
    p = json.load(open(spec_path))["plate"]
    x0, y0, x1, y1 = p["crop"]
    im = Image.open(os.path.join(ROOT, p["leaf"])).convert("RGB")
    W, H = im.size
    inb = (max(x0, 0), max(y0, 0), min(x1, W), min(y1, H))
    from PIL import ImageStat
    paper = tuple(int(v) for v in ImageStat.Stat(im.crop(inb)).median)
    out = Image.new("RGB", (x1 - x0, y1 - y0), paper)
    out.paste(im.crop(inb), (inb[0] - x0, inb[1] - y0))
    return out


def ink_level(rgb):
    """0 (paper) .. 1 (full ink)."""
    g = np.asarray(rgb.convert("L"), dtype=np.float64)
    paper, ink = np.percentile(g, 85), np.percentile(g, 1)
    return np.clip((paper - g) / max(paper - ink, 1), 0, 1)


QWEN_PROMPT = """This is a scanned 19th-century survey plate (a plan of prehistoric earthworks).
List bounding boxes for every element that is NOT part of the map's ground plan:
- "title": the title block (site name, county, surveyor credits)
- "text": each label or group of lettering (e.g. "Area 20 Acres", river names, "1050 ft", single letters like "a", "b")
- "north_arrow": the north arrow or compass rose
- "scale": the scale bar and its caption
- "section": each section/profile drawing (cross-section diagrams, usually with a baseline and bumps)
- "frame": inset boxes or panels that belong to a different map
Do not box the earthwork walls, rivers, hills or trees.
Coordinates: [x0, y0, x1, y1] normalised to 0-1000 over the full image width and height (0,0 = top left).
Answer: {"boxes": [{"kind": "...", "box": [x0, y0, x1, y1]}, ...]}"""


QWEN_RETRY = "\nList at most 40 boxes; merge nearby labels into one box. Stop when done."


def qwen_boxes(sid, im, refresh=False):
    """Non-map boxes (plate px) from the local vision model, cached in data/autofit/<id>_qwen.json.

    Convention checked by drawing the boxes on the plates: [x0, y0, x1, y1] in 0-1000 of width/height."""
    path = os.path.join(OUT, sid + "_qwen.json")
    if refresh or not os.path.exists(path):
        import time
        import llm
        t0 = time.time()
        ans = llm.ask_json(QWEN_PROMPT, images=[im], max_px=1600, max_tokens=4000)
        raw = ans if isinstance(ans, list) else ans.get("boxes", ans)
        json.dump({"model": llm.MODEL, "seconds": round(time.time() - t0, 1), "boxes": raw}, open(path, "w"), indent=1)
    rec = json.load(open(path))
    if isinstance(rec["boxes"], dict) and "retry" not in rec:
        # unparsable answer (the model looped until max_tokens on newark and forthill): one retry, smaller
        # image, capped list; the first answer is kept in the file for the record
        import time
        import llm
        t0 = time.time()
        ans = llm.ask_json(QWEN_PROMPT + QWEN_RETRY, images=[im], max_px=1280, max_tokens=3000)
        rec["first_answer"] = rec["boxes"]
        rec["boxes"] = ans if isinstance(ans, list) else ans.get("boxes", ans)
        rec["retry"] = {"seconds": round(time.time() - t0, 1), "max_px": 1280}
        json.dump(rec, open(path, "w"), indent=1)
    raw = rec["boxes"]
    if isinstance(raw, dict) and "_unparsed" in raw:
        # the model sometimes loops until max_tokens (newark: 130 boxes marching off the page); keep the
        # complete objects and let the range check below drop the runaway ones
        import re
        raw = [{"kind": k, "box": [float(v) for v in b.split(",")]} for k, b in re.findall(
            r'\{\s*"kind"\s*:\s*"(\w+)"\s*,\s*"box"\s*:\s*\[([\d\s,.-]+)\]\s*\}', raw["_unparsed"])]
    W, H = im.size
    out = []
    for b in raw if isinstance(raw, list) else []:
        try:
            x0, y0, x1, y1 = [float(v) for v in b["box"]]
        except (KeyError, TypeError, ValueError):
            continue
        if min(x0, y0, x1, y1) < 0 or max(x0, y0, x1, y1) > 1000 or x0 == x1 or y0 == y1:
            continue
        out.append((b.get("kind", "?"), (min(x0, x1) * W / 1000, min(y0, y1) * H / 1000,
                                        max(x0, x1) * W / 1000, max(y0, y1) * H / 1000)))
    return out


# ---- frozen extractor parameters (set by looking at the ink maps only; see docs/autofit.md section 3) ----
P = dict(
    sigmas=(4, 6, 9),     # Frangi ridge scales, plate px. Walls are 6-20 px bands; dropping sigma 2-3 keeps the
                          #   engraver's 1-2 px ground-tint dashes, field lines and hachure strokes faint
    ridge_thr=0.25,       # Frangi response threshold (response distributions are near-identical across plates)
    gamma=0.013,          # Frangi structuredness scale, fixed: the default (half the image's max Hessian norm)
                          #   moves when a dark north arrow is blanked; 0.013 = median default over the 5 plates
    coh_sigma=25.0,       # orientation coherence of the centre lines over ~50 px: drops junctions, lettering
    coh_min=0.6,          #   and wiggly streams; smooth rivers survive (no geometric cue separates them)
    min_len=50,           # skeleton px per surviving piece, after the coherence cut
    min_extent=50,        # bbox long side of a piece, px
    normal_sigma=4.0,     # structure-tensor window for the across-wall direction
    step=2,               # keep ~1 skeleton px in 2 as template points
    margin=20,            # px along the crop edge ignored: plate border and frame lines (hopeton's left edge)
    box_kinds=("title", "north_arrow", "scale", "section", "frame"),  # Qwen boxes blanked. Not "text": labels
                          #   are written along and across walls ("1320 ft", "Parallels"), and the length filter
                          #   already drops lettering
)


def structure_tensor(f, sigma):
    gy, gx = ndi.sobel(f, 0), ndi.sobel(f, 1)
    Jxx = ndi.gaussian_filter(gx * gx, sigma)
    Jyy = ndi.gaussian_filter(gy * gy, sigma)
    Jxy = ndi.gaussian_filter(gx * gy, sigma)
    return Jxx, Jyy, Jxy


def coherence(mask, sigma):
    Jxx, Jyy, Jxy = structure_tensor(ndi.gaussian_filter(mask.astype(float), 1.5), sigma)
    return np.sqrt((Jxx - Jyy) ** 2 + 4 * Jxy ** 2) / np.maximum(Jxx + Jyy, 1e-12), (Jxx, Jyy, Jxy)


def drop_small(mask, min_len, min_extent):
    lab, n = ndi.label(mask, structure=np.ones((3, 3)))
    if not n:
        return mask
    length = ndi.sum(mask, lab, np.arange(1, n + 1))
    ext = np.array([max(s[0].stop - s[0].start, s[1].stop - s[1].start) for s in ndi.find_objects(lab)])
    good = (length >= min_len) & (ext >= min_extent)
    return (lab > 0) & good[np.maximum(lab - 1, 0)]


def extract(im, boxes=(), p=P, debug=False):
    """Plate image -> (points uv [n,2] in plate px, unit normals [n,2] in plate px axes, weights [n]).

    boxes: [(x0, y0, x1, y1)] plate px areas to ignore (Qwen's title/arrow/scale/section/frame boxes)."""
    from skimage.filters import frangi
    from skimage.morphology import skeletonize
    a = ink_level(im)
    m = p["margin"]
    a[:m] = 0
    a[-m:] = 0
    a[:, :m] = 0
    a[:, -m:] = 0
    for x0, y0, x1, y1 in boxes:
        a[max(0, int(y0)):int(math.ceil(y1)), max(0, int(x0)):int(math.ceil(x1))] = 0
    R = frangi(a, sigmas=p["sigmas"], black_ridges=False, beta=0.5, gamma=p["gamma"])
    sk = skeletonize(R > p["ridge_thr"])
    sk = drop_small(sk, p["min_len"], p["min_extent"])
    coh, _ = coherence(sk, p["coh_sigma"])
    keep = drop_small(sk & (coh >= p["coh_min"]), p["min_len"], p["min_extent"])
    # normals: dominant gradient direction of the blurred centre line = across the wall
    _, (Jxx, Jyy, Jxy) = coherence(keep, p["normal_sigma"])
    th = 0.5 * np.arctan2(2 * Jxy, Jxx - Jyy)  # angle of the major eigenvector (x right, y down)
    vv, uu = np.nonzero(keep)
    sel = np.random.default_rng(0).random(len(uu)) < 1.0 / p["step"]
    uu, vv = uu[sel], vv[sel]
    t = th[vv, uu]
    pts = np.stack([uu, vv], 1).astype(float)
    nrm = np.stack([np.cos(t), np.sin(t)], 1)
    out = (pts, nrm, np.ones(len(pts)))
    if debug:
        return out, dict(a=a, R=R, sk=sk, coh=coh, keep=keep)
    return out


def picture(im, keep, boxes, path, max_px=1100):
    """What survived: plate in light grey, kept centre lines in red, blanked Qwen boxes outlined."""
    g = np.asarray(im.convert("L"), float)
    vis = np.stack([255 - (255 - g) * 0.4] * 3, -1)
    vis[ndi.binary_dilation(keep, iterations=2)] = (200, 20, 50)
    v = Image.fromarray(vis.astype(np.uint8))
    d = ImageDraw.Draw(v)
    for b in boxes:
        d.rectangle(b, outline=(40, 90, 200), width=5)
    v.thumbnail((max_px, max_px))
    v.save(path, quality=80)


def main(sites, use_qwen=True, tag=""):
    os.makedirs(OUT, exist_ok=True)
    for sid in sites:
        im = load_plate(sid)
        boxes = [b for k, b in qwen_boxes(sid, im) if k in P["box_kinds"]] if use_qwen else []
        (pts, nrm, w), d = extract(im, boxes, debug=True)
        np.savez_compressed(os.path.join(OUT, sid + "_template%s.npz" % tag), pts=pts, nrm=nrm, w=w,
                            boxes=np.array(boxes, float).reshape(-1, 4))
        picture(im, d["keep"], boxes, os.path.join(OUT, sid + "_walls%s.jpg" % tag))
        print(sid, len(pts), "template points,", len(boxes), "boxes blanked")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args or ["fudge", "hopeton", "newark", "forthill", "highbank"], use_qwen="--no-qwen" not in sys.argv,
         tag="_noqwen" if "--no-qwen" in sys.argv else "")
