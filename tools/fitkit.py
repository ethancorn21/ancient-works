"""Hand-fitting helper for Claude (the page's plate-fitting tool does the same for people).

usage:
  fitkit.py sheet <site> <plan id> [x0,y0,x1,y1]     plan crop | site relief, both gridded -> scratch png
  fitkit.py zoom <site> x0,y0,x1,y1                    relief crop (relief px), contrast-stretched, gridded
  fitkit.py save <site> <plan id> <crop> <model> u,v=col,row ...
                                                      pairs in plan px and relief px -> db platefits (serve.py builds it)
  fitkit.py check <site> <plan id>                     ink overlay on the relief -> scratch png
  fitkit.py find <site>                                harvested Commons pictures of a site (ids for the commands above)
Relief px are pixels of the site's ground image, converted to lon/lat through the site's corners: web/data/sites/<site>/relief.jpg,
or the aerial photograph (Esri World Imagery, the page's "Aerial photograph") for a site with no LiDAR or with FITKIT_GROUND=aerial.
The aerial is for fitting an old map by what has not moved (roads, churches, river crossings, field edges); it is cached in
data/raw/aerial/ (gitignored) and never published.
"""
import datetime
import json
import os
import sys
import time
import urllib.request

from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("FITKIT_OUT", "/tmp")
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import aw  # noqa: E402

Image.MAX_IMAGE_PIXELS = 200_000_000


AERIAL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export"


def ground(sid):
    """Path of the image the fit pixels refer to: the relief, or the aerial photograph of the site box at 1 m a pixel."""
    rel = os.path.join(ROOT, "web", "data", "sites", sid, "relief.jpg")
    if os.path.exists(rel) and os.environ.get("FITKIT_GROUND") != "aerial":
        return rel
    s = site(sid)
    path = os.path.join(ROOT, "data", "raw", "aerial", f"{sid}.jpg")
    if not os.path.exists(path):
        (lon0, lat1), (lon1, _), (_, lat0) = s["corners"][0], s["corners"][1], s["corners"][2]
        x0, y1 = aw.to_merc(lon0, lat1)
        x1, y0 = aw.to_merc(lon1, lat0)
        w, h = (min(4096, round(v)) for v in s["size_m"])
        body = aw._get(AERIAL, {"bbox": f"{x0:.2f},{y0:.2f},{x1:.2f},{y1:.2f}", "bboxSR": 3857, "imageSR": 3857,
                                "size": f"{w},{h}", "format": "jpg", "f": "image"})
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(body)
    return path


def ground_view(sid, im):
    """The ground image for looking at: the relief contrast-stretched in grey, the aerial as it is."""
    if ground(sid).endswith("relief.jpg"):
        return ImageOps.autocontrast(im.convert("L"), cutoff=1).convert("RGB")
    return im.convert("RGB")


def site(sid):
    return next(s for s in json.load(open(os.path.join(ROOT, "web", "data", "sites.json")))["sites"] if s["id"] == sid)


def plan(pid):
    """A row of web/data/plans.json, or any harvested Commons picture (c_<hash>) not exported there yet."""
    d = json.load(open(os.path.join(ROOT, "web", "data", "plans.json")))
    r = next((r for r in d["rows"] if r[0] == pid), None)
    if r is None:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import export_plans
        r = next(r for r in export_plans.commons_rows(min_p=None) if r[0] == pid)
    return dict(zip(d["cols"], r))


def plan_image(p):
    if p.get("url"):
        return Image.open(os.path.join(ROOT, "data", "raw", "commons", *p["url"].split("/")[-2:])).convert("RGB")
    return Image.open(os.path.join(ROOT, "data", "raw", "books", p["ia"], "full", p["file"])).convert("RGB")


def grid(im, x0, y0, scale, step, color=(0, 90, 230)):
    """Draw a grid every `step` source px on an image showing source px from (x0, y0) at `scale`."""
    d = ImageDraw.Draw(im)
    W, H = im.size
    v = (x0 // step + 1) * step
    while (v - x0) * scale < W:
        x = (v - x0) * scale
        d.line([(x, 0), (x, H)], fill=color, width=1)
        d.text((x + 2, 2), str(v), fill=color)
        v += step
    v = (y0 // step + 1) * step
    while (v - y0) * scale < H:
        y = (v - y0) * scale
        d.line([(0, y), (W, y)], fill=color, width=1)
        d.text((2, y + 2), str(v), fill=color)
        v += step
    return im


def sheet(sid, pid, crop=None):
    p = plan(pid)
    im = plan_image(p)
    x0, y0, x1, y1 = crop or [0, 0, im.width, im.height]
    c = im.crop((x0, y0, x1, y1))
    sc = 900 / max(c.size)
    c = c.resize((round(c.width * sc), round(c.height * sc)), Image.LANCZOS)
    step = 100 if max(x1 - x0, y1 - y0) < 1600 else 200 if max(x1 - x0, y1 - y0) < 3200 else 400
    grid(c, x0, y0, sc, step)
    r = ground_view(sid, Image.open(ground(sid)))
    rs = 900 / max(r.size)
    r = r.resize((round(r.width * rs), round(r.height * rs)), Image.LANCZOS)
    grid(r, 0, 0, rs, 100, (230, 40, 40))
    S = Image.new("RGB", (c.width + r.width + 10, max(c.height, r.height)), "white")
    S.paste(c, (0, 0))
    S.paste(r, (c.width + 10, 0))
    path = os.path.join(OUT, f"fit_{sid}_{pid}.jpg")
    S.save(path, quality=85)
    # read positions off the grid labels, never off the sheet's own pixels: the plan is drawn at `sc`, the ground at `rs`
    # (2026-10-10: Castle Rising saved with on-sheet pixels came out 1.21x too small and shifted)
    print(path, "plan size", im.size, "ground size", Image.open(ground(sid)).size,
          f"| sheet scale: plan {sc:.3f}, ground {rs:.3f} (plan px = (sheet x / {sc:.3f}) + {x0})")


def zoom(sid, box):
    x0, y0, x1, y1 = box
    r = ground_view(sid, Image.open(ground(sid)).crop((x0, y0, x1, y1)))
    sc = 900 / max(r.size)
    r = r.resize((round(r.width * sc), round(r.height * sc)), Image.LANCZOS)
    step = 20 if max(x1 - x0, y1 - y0) <= 250 else 50 if max(x1 - x0, y1 - y0) <= 600 else 100
    grid(r, x0, y0, sc, step, (230, 40, 40))
    path = os.path.join(OUT, f"zoom_{sid}.jpg")
    r.save(path, quality=88)
    print(path)


def lonlat(s, col, row):
    W, H = Image.open(ground(s["id"])).size
    (lon0, lat1), (lon1, _), (_, lat0) = s["corners"][0], s["corners"][1], s["corners"][2]
    x0, y1 = aw.to_merc(lon0, lat1)
    x1, y0 = aw.to_merc(lon1, lat0)
    return aw.to_lonlat(x0 + (col + 0.5) / W * (x1 - x0), y1 - (row + 0.5) / H * (y1 - y0))


def save(sid, pid, crop, model, pairs):
    s, p = site(sid), plan(pid)
    im = plan_image(p)
    at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc = {"site": sid, "plan": pid, "ia": p["ia"], "file": p["file"], "crop": crop, "model": model,
           "src": "book" if p["ia"] else "commons", "url": p.get("url"), "ref": p.get("ref"), "size": list(im.size),
           "pairs": [[u, v, *[round(x, 7) for x in lonlat(s, c, r)]] for u, v, c, r in pairs],
           "label": p["label"], "title": p["title"], "book": p["book"], "cite": p["cite"], "at": at}
    url = f"http://127.0.0.1:8642/api/db/platefits/{sid}.{pid}"
    urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(doc).encode(), method="PUT",
                                                  headers={"Content-Type": "application/json"}))
    dep = os.path.join(ROOT, "web", "data", "sites", sid, "depictions.json")
    for _ in range(90):
        time.sleep(1)
        try:
            e = [x for x in json.load(open(dep))["depictions"] if (x.get("fit") or {}).get("at") == at]
        except Exception:
            continue
        if e:
            print("fit", e[0]["fit"])
            return
    print("no overlay after 90 s; see the server log (plan_fit lines)")


def check(sid, pid):
    s = site(sid)
    dep = json.load(open(os.path.join(ROOT, "web", "data", "sites", sid, "depictions.json")))["depictions"]
    e = next(x for x in dep if x["file"] == f"plan_{pid}.webp")
    rel = Image.open(ground(sid)).convert("RGB")
    W, H = rel.size
    (lon0, lat1), (lon1, _), (_, lat0) = s["corners"][0], s["corners"][1], s["corners"][2]
    X0, Y1 = aw.to_merc(lon0, lat1)
    X1, Y0 = aw.to_merc(lon1, lat0)
    px = lambda lon, lat: ((aw.to_merc(lon, lat)[0] - X0) / (X1 - X0) * W, (Y1 - aw.to_merc(lon, lat)[1]) / (Y1 - Y0) * H)
    ink = Image.open(os.path.join(ROOT, "web", "data", "sites", sid, e["ink"])).convert("RGBA")
    # perspective-map the overlay's 4 corners onto relief px (exact for similarity, axis-aligned for views)
    dst = [px(*c) for c in e["corners"]]
    import numpy as np
    src = [(0, 0), (ink.width, 0), (ink.width, ink.height), (0, ink.height)]
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        b += [u, v]
    coef = np.linalg.solve(np.array(A), np.array(b))
    warped = ink.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BILINEAR)
    rel = ground_view(sid, rel).convert("RGBA")
    out = Image.alpha_composite(rel, warped)
    out.thumbnail((1100, 1100))
    path = os.path.join(OUT, f"check_{sid}_{pid}.jpg")
    out.convert("RGB").save(path, quality=85)
    print(path, e["fit"])


def find(sid):
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import export_plans
    for r in export_plans.commons_rows(min_p=None):
        if sid in r[8]:
            print(r[0], r[5] or "-", r[6], r[4][:90])


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    box = lambda t: [int(float(v)) for v in t.split(",")]
    if cmd == "sheet":
        sheet(a[0], a[1], box(a[2]) if len(a) > 2 else None)
    elif cmd == "zoom":
        zoom(a[0], box(a[1]))
    elif cmd == "save":
        prs = []
        for t in a[4:]:
            l, r = t.split("=")
            prs.append([*map(float, l.split(",")), *map(float, r.split(","))])
        save(a[0], a[1], box(a[2]), a[3], prs)
    elif cmd == "check":
        check(a[0], a[1])
    elif cmd == "find":
        find(a[0])
