"""Export one site for the globe: relief + imagery images, plate ink/paper images, and its entry in sites.json.

usage: build_site.py data/sites/<id>/site.json [--refresh-imagery]
Writes web/data/sites/<id>/{relief.jpg,imagery.jpg,plate_ink.png,plate_paper.jpg} and updates web/data/sites.json.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web", "data")
INK = (206, 46, 78)  # survey red, as on the ore bodies of USGS plates; reads on sepia relief and on photos
SEPIA = np.array([[46, 38, 34], [176, 164, 146], [251, 247, 236]], float)  # sunken, level, raised
TOP_LO, TOP_HI = np.array([178, 160, 148], float), np.array([253, 249, 238], float)
WATER = np.array([196, 222, 220], float)
CONTOUR = np.array([132, 98, 80], float)


def duotone(gray):
    t = gray.astype(float) / 255.0
    lo = SEPIA[0] + (SEPIA[1] - SEPIA[0]) * np.clip(t * 2, 0, 1)[..., None]
    return np.where((t < 0.5)[..., None], lo, SEPIA[1] + (SEPIA[2] - SEPIA[1]) * np.clip(t * 2 - 1, 0, 1)[..., None])


def plate_ink(scan, inside=None):
    """Plate scan -> RGBA where alpha follows ink darkness and paper turns transparent.
    `inside` limits the paper/ink tone estimate to the plate itself (a warped sheet has blank margins)."""
    g = np.asarray(scan.convert("L"), dtype=np.float64)
    sample = g if inside is None else g[inside]
    paper, ink = np.percentile(sample, 85), np.percentile(sample, 2)
    # paper grain and the engraver's faint ground shading sit just below paper tone; drop them
    a = np.clip((paper - g) / max(paper - ink, 1) * 1.35 - 0.18, 0, 1) ** 0.9
    out = np.zeros(g.shape + (4,), np.uint8)
    out[..., :3] = INK
    out[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def warp_plate(scan, warp, site, max_px=2400):
    """Rubber-sheet the plate onto the site grid with a thin-plate spline (ground metres -> plate px).

    Returns an RGBA image covering the site bbox exactly; alpha is 0 outside the plate."""
    from scipy.interpolate import RBFInterpolator
    from scipy.ndimage import map_coordinates, zoom
    W_m, H_m = site["width_m"], site["height_m"]
    opx = max(site.get("px_m", 1.0), max(W_m, H_m) / max_px)
    ow, oh = int(round(W_m / opx)), int(round(H_m / opx))
    # fit in metres on both sides so the smoothing (m^2) means the same thing on fine and coarse plates
    k = site["plate"]["fit"]["m_per_px"]
    if warp:
        tps_m = RBFInterpolator(np.array(warp["dst_m"]), np.array(warp["src_px"]) * k, kernel="thin_plate_spline",
                                smoothing=site["plate"].get("warp_smoothing", 2000.0))
        tps = lambda q: tps_m(q) / k
    else:  # plain fit: invert the affine (ground = M [u-u0, -(v-v0)] + t)
        a = site["plate"]["fit"]["affine"]
        Minv = np.linalg.inv(np.array([[a[0], a[1]], [a[2], a[3]]]))
        u0, v0 = site["plate"]["fit"]["u0v0"]
        def tps(q):
            d = (q - np.array(a[4:6])) @ Minv.T
            return np.stack([d[:, 0] + u0, v0 - d[:, 1]], 1)
    step = 16
    cols, rows = np.arange(0, ow + step, step), np.arange(0, oh + step, step)
    E = (cols + 0.5) * opx - W_m / 2
    N = H_m / 2 - (rows + 0.5) * opx
    EE, NN = np.meshgrid(E, N)
    uv = tps(np.stack([EE.ravel(), NN.ravel()], 1)).reshape(len(rows), len(cols), 2)
    U = zoom(uv[..., 0], step, order=1)[:oh, :ow]
    V = zoom(uv[..., 1], step, order=1)[:oh, :ow]
    rgb = np.asarray(scan.convert("RGB"), dtype=np.float32)
    out = np.zeros((oh, ow, 4), np.uint8)
    for c in range(3):
        out[..., c] = np.clip(map_coordinates(rgb[..., c], [V, U], order=1, cval=255), 0, 255)
    inside = (U >= 0) & (U < scan.width - 1) & (V >= 0) & (V < scan.height - 1)
    out[..., 3] = inside * 255
    return Image.fromarray(out, "RGBA")


def build_block(z, px_m, out, water_or_modern, max_mesh=512, max_tex=2048):
    """Assets for the isometric block view: a height map (16-bit split over R and G of a PNG) and a top
    texture drawn like a USGS plate surface (shaded relief in warm paper tones, contours, tinted water)."""
    from scipy.ndimage import gaussian_filter, zoom
    z = aw.fill_nan(z)
    h, w = z.shape
    k = min(1.0, max_mesh / max(h, w))
    zm = zoom(gaussian_filter(z, 0.5 / k), k, order=1) if k < 1 else z
    zmin, zmax = float(zm.min()), float(zm.max())
    cm = np.clip(np.round((zm - zmin) * 100), 0, 65535).astype(np.uint32)
    rg = np.dstack([(cm >> 8).astype(np.uint8), (cm & 255).astype(np.uint8), np.zeros_like(cm, np.uint8)])
    Image.fromarray(rg, "RGB").save(os.path.join(out, "block_h.png"), optimize=True)

    kt = min(1.0, max_tex / max(h, w))
    zt = zoom(z, kt, order=1) if kt < 1 else z
    tpx = px_m / kt
    hs = aw.hillshade(zt, tpx, az=315, alt=40, exag=4.0)
    rel = np.clip(aw.local_relief(zt, tpx) / 0.8, -1, 1) * 0.5 + 0.5
    tone = np.clip(0.55 * hs + 0.45 * rel, 0, 1)[..., None]
    rgb = TOP_LO + (TOP_HI - TOP_LO) * tone
    water = aw.water_mask(zt, tpx, grow_m=0.5)
    rgb[water] = WATER
    rng = zmax - zmin
    ci = next(c for c in (0.25, 0.5, 1, 2, 5, 10, 20, 50) if rng / c <= 40)
    zs = gaussian_filter(zt, 1.5)
    band = np.floor(zs / ci)
    edge = np.zeros_like(band, bool)
    edge[:, 1:] |= band[:, 1:] != band[:, :-1]
    edge[1:, :] |= band[1:, :] != band[:-1, :]
    index = edge & (np.mod(band, 5) == 0)
    edge &= ~water
    rgb[edge] = rgb[edge] * 0.55 + CONTOUR * 0.45
    rgb[index & ~water] = CONTOUR
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(os.path.join(out, "block_top.jpg"), quality=86, optimize=True)
    return {"w": int(zm.shape[1]), "h": int(zm.shape[0]), "zmin": round(zmin, 2), "zmax": round(zmax, 2),
            "contour_m": ci, "height": "block_h.png", "top": "block_top.jpg"}


def main(path, refresh_imagery=False):
    sdir = os.path.dirname(path)
    site = json.load(open(path))
    sid = site["id"]
    out = os.path.join(WEB, "sites", sid)
    os.makedirs(out, exist_ok=True)
    px_m = site.get("px_m", 1.0)
    bbox = aw.site_bbox(site["lon"], site["lat"], site["width_m"], site["height_m"])
    w, h = int(site["width_m"] / px_m), int(site["height_m"] / px_m)

    dem_cache = os.path.join(sdir, "dem.npy")
    if os.path.exists(dem_cache):
        z = np.load(dem_cache)
    else:
        z = aw.fetch_dem(bbox, w, h)
        np.save(dem_cache, z)
    mask_path = os.path.join(sdir, "modern_mask.npy")
    ignore = aw.water_mask(z, px_m)
    if os.path.exists(mask_path):
        ignore = ignore | np.load(mask_path)
    img, clip = aw.render_relief(z, px_m, clip_m=site.get("relief_clip_m"), ignore=ignore)
    Image.fromarray(duotone(img).astype(np.uint8)).save(os.path.join(out, "relief.jpg"), quality=84, optimize=True)
    entry_block = build_block(z, px_m, out, ignore)

    imagery = os.path.join(out, "imagery.jpg")
    if refresh_imagery or not os.path.exists(imagery):
        aw.fetch_imagery(bbox, min(w, 4096), min(h, 4096)).save(imagery, quality=80, optimize=True)

    entry = {k: site[k] for k in ("id", "name", "aka", "place", "lon", "lat", "status", "summary", "notes")
             if k in site}
    entry["corners"] = aw.corners(bbox)
    entry["relief_clip_m"] = round(clip, 2)
    entry["block"] = entry_block
    entry["size_m"] = [site["width_m"], site["height_m"]]
    if "plate" in site and "corners" in site["plate"]:
        p = site["plate"]
        scan = Image.open(os.path.join(sdir, p["image"])).convert("RGB")
        for f in ("plate_ink.png", "plate_paper.jpg", "plate_ink.webp", "plate_paper.webp"):
            if os.path.exists(os.path.join(out, f)):
                os.remove(os.path.join(out, f))
        if True:  # every plate becomes a sheet aligned to the site box (rubber-sheeted when it has a warp)
            sheet = warp_plate(scan, p.get("warp"), site)
            ink = plate_ink(sheet.convert("RGB"), inside=np.asarray(sheet)[..., 3] > 0)
            a = np.minimum(np.asarray(ink)[..., 3], np.asarray(sheet)[..., 3])
            ink = Image.fromarray(np.dstack([np.asarray(ink)[..., :3], a]), "RGBA")
            ink.save(os.path.join(out, "plate_ink.webp"), quality=85, method=6)
            sheet.save(os.path.join(out, "plate_paper.webp"), quality=78, method=6)
            files, corners = ("plate_ink.webp", "plate_paper.webp"), entry["corners"]
        else:
            plate_ink(scan).save(os.path.join(out, "plate_ink.png"), optimize=True)
            scan.save(os.path.join(out, "plate_paper.jpg"), quality=82, optimize=True)
            files, corners = ("plate_ink.png", "plate_paper.jpg"), p["corners"]
        entry["plate"] = {"corners": corners, "ink": files[0], "paper": files[1], "source": p["source"],
                          "fit": p.get("fit"), "features": p.get("features"), "warped": bool(p.get("warp")),
                          "label": p.get("label", "")}

    index_path = os.path.join(WEB, "sites.json")
    index = json.load(open(index_path)) if os.path.exists(index_path) else {"sites": []}
    index["sites"] = [s for s in index["sites"] if s["id"] != sid] + [entry]
    index["sites"].sort(key=lambda s: s["name"])
    aw.save_json(index_path, index)
    sizes = {f: os.path.getsize(os.path.join(out, f)) // 1024 for f in os.listdir(out)}
    print(sid, "relief clip", round(clip, 2), "m;", sizes, "KB")


if __name__ == "__main__":
    main(sys.argv[1], "--refresh-imagery" in sys.argv)
