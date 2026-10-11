"""Mackenzie, The Castles of England (1897), page 212: the five-towered castle plan with no caption (task 206,
GOAL.md point 4) - the only gap in the book's 29 hand-tied plates (pipeline/sources.py). Identified by evidence
as Shotwick Castle (Q7502621, Cheshire) and staged as one row; docs/lead_mackenzie.md carries the evidence chain
(the file's Commons category is the castle's own P373, the book's index and V2 chapter text name Shotwick, the
plate sits in V2 nineteen leaves before the Lancaster plate, and the surviving ground carries the plan's
features).

usage: src_mackenzie.py --fetch     working phase (network): the 839x840 BL Flickr scan to data/raw/books/mackenzie/
                                    (the book copy) and data/raw/commons/<site>/<sha1-16>.jpg (the machinery's
                                    slot); re-verifies the live title/size first (R4: a title change fails loud)
       src_mackenzie.py --verify    working phase (network): the Q7502621 fact sheet (label, every P625, P373,
                                    P31, P131, enwiki) + the file's live description and categories - the text
                                    docs/lead_mackenzie.md records (checked date included)
       src_mackenzie.py --sheet     working phase (network): gridded ground + the page, for the fit session:
                                    the 800 m box (catalog point +/- 400 m) at 1 m/px from the Esri aerial and,
                                    when the national LiDAR answers, the relief, plus the 839x840 page itself -
                                    all gridded with lon/lat (ground) or page-px (page) labels -> $MACK_OUT (default /tmp)
       src_mackenzie.py --zoom      working phase (network): a 200 m ground crop at 0.25 m/px, gridded
       src_mackenzie.py --write-doc x0,y0,x1,y1 u,v=lon,lat ...   write data/db/platefits/<site>.<plan>.json
                                    (the hand-fit shape of the other 25; pairs in page px of the 839x840 frame)
       src_mackenzie.py --gate      offline: fit_gate.gate over the committed doc's pairs (transform=None - the
                                    hand fit's own residual is the claim, docs/gate.md section 4) + the
                                    plan_fit.similarity residuals; fails loud (exit 1) on a REJECT
       src_mackenzie.py [--dry]     stage the row into this task's staging files (dry: print, write nothing):
                                    the file row (the 29 plates' exact shape + the 200 evidence field), the
                                    classified row and the extras row (aerial_ok: the picture is the reason to
                                    build the unbuilt site, so 211 builds it with the plan already tied)
       src_mackenzie.py --check     offline (no network): the join (site in the catalog by QID, rows 1:1, no
                                    clash with the canonical files or the 29 hand-tied plates) + fit/evidence.py
                                    check over the staged row
       src_mackenzie.py --golden    write tests/golden/src_mackenzie_sample.json (staged rows + the doc,
                                    normalized; regenerate only for an intended change)

Staging writes only this task's files (append-only, idempotent on (site, title)); 211 consolidates them into
the canonical ones and builds the site. The system python3 has no numpy (commons -> aw), so every command
here runs under .venv/bin/python; the module top stays stdlib-only.
"""
import datetime
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

TITLE = ("File:212 of 'The Castles of England- their story and structure ... With ... illustrations and ... "
         "plans' (11296081346).jpg")
SITE = "shotwick-castle-q7502621"
QID = "Q7502621"
CAT = "Shotwick Castle"  # Q7502621's P373 and the file's own Commons category (verified, --verify re-checks)
LON, LAT = -2.97608, 53.2272  # the catalog row's point (data/catalog/sites.jsonl)
BOX_M = 800  # build_catalog.BOX: kind "motte" -> 800 m square
PAGE_W, PAGE_H = 839, 840  # the original scan's size (R4: --fetch asserts it against the live file)
PLAN = "c_" + hashlib.sha1(TITLE.encode()).hexdigest()[:16]  # c_e6e5490609414bb9, the export_plans rule
YEAR = "1897"

FILES = os.path.join(ROOT, "data", "commons", "files_mackenzie.jsonl")
CLASSIFIED = os.path.join(ROOT, "data", "commons", "classified_mackenzie.jsonl")
EXTRAS = os.path.join(ROOT, "data", "catalog", "extras_mackenzie.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
EXTRAS_CANONICAL = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
SITES_CANONICAL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
RAW_BOOKS = os.path.join(ROOT, "data", "raw", "books", "mackenzie")
RAW_COMMONS = os.path.join(ROOT, "data", "raw", "commons", SITE, PLAN[2:] + ".jpg")
AERIAL = os.path.join(ROOT, "data", "raw", "aerial", SITE + ".jpg")
DB_DOC = os.path.join(ROOT, "data", "db", "platefits", f"{SITE}.{PLAN}.json")
OUT = os.environ.get("MACK_OUT", "/tmp")

AERIAL_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export"


def now():
    return time.strftime("%Y-%m-%d")


def _commons():
    import commons  # lazy: commons -> aw needs numpy (absent from the system python3)
    return commons


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def _append(path, rows):
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _bbox():
    import aw
    return aw.site_bbox(LON, LAT, BOX_M, BOX_M)


def _corners():
    import aw
    return aw.corners(_bbox())  # [lon, lat] TL, TR, BR, BL, in ground metres at 1 m/px


def _aerial():
    """The Esri World Imagery of the site box at 1 m/px, the same request fitkit.ground makes (cached in
    data/raw/aerial/ - the machine's normal build uses exactly this image for the site's aerial ground)."""
    import aw
    (x0, y0), (x1, y1) = (aw.to_merc(c[0], c[1]) for c in (_corners()[0], _corners()[2]))
    os.makedirs(os.path.dirname(AERIAL), exist_ok=True)
    body = aw._get(AERIAL_URL, {"bbox": f"{x0:.2f},{y0:.2f},{x1:.2f},{y1:.2f}", "bboxSR": 3857, "imageSR": 3857,
                                "size": f"{BOX_M},{BOX_M}", "format": "jpg", "f": "image"})
    open(AERIAL + ".part", "wb").write(body)
    os.replace(AERIAL + ".part", AERIAL)
    return AERIAL


def _grid(im, x0, y0, scale, step, label, color=(0, 90, 230)):
    """fitkit.grid with per-line labels produced by label(pixel value) - page px stay numbers, ground px become
    lon/lat through the box corners."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    W, H = im.size
    v = (x0 // step + 1) * step
    while (v - x0) * scale < W:
        x = (v - x0) * scale
        d.line([(x, 0), (x, H)], fill=color, width=1)
        d.text((x + 2, 2), label(v, 0), fill=color)
        v += step
    v = (y0 // step + 1) * step
    while (v - y0) * scale < H:
        y = (v - y0) * scale
        d.line([(0, y), (W, y)], fill=color, width=1)
        d.text((2, y + 2), label(0, v), fill=color)
        v += step
    return im


def fetch():
    """The scan, twice: the book copy (data/raw/books/mackenzie/) and the machinery's slot
    (data/raw/commons/<site>/<sha1-16>.jpg, where fitkit.plan_image and export_plans look for it)."""
    import urllib.request
    from PIL import Image
    import aw
    c = _commons()
    meta = c.info([TITLE]).get(TITLE) or {}
    if not meta.get("url"):
        raise SystemExit(f"not on Commons (title changed?): {TITLE}")
    if (meta.get("w"), meta.get("h")) != (PAGE_W, PAGE_H):
        raise SystemExit(f"the live file is {meta.get('w')}x{meta.get('h')}, the page is {PAGE_W}x{PAGE_H} - "
                         f"R4 drift, the recorded pairs and golden are stale")
    with urllib.request.urlopen(urllib.request.Request(meta["url"], headers=aw.UA), timeout=120) as r:
        data = r.read()
    im = Image.open(__import__("io").BytesIO(data))
    if im.size != (PAGE_W, PAGE_H):
        raise SystemExit(f"downloaded image is {im.size}, expected {(PAGE_W, PAGE_H)}")
    for p in (os.path.join(RAW_BOOKS, "212.jpg"), RAW_COMMONS):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p + ".part", "wb").write(data)
        os.replace(p + ".part", p)
        print("saved", p)
    print(f"desc: {meta.get('desc')!r}")


def verify():
    """The Q7502621 fact sheet and the file's live page facts, for docs/lead_mackenzie.md (R4 re-run)."""
    import evidence
    c = _commons()
    d = c.get(c.WD, {"action": "wbgetentities", "ids": QID, "props": "claims|sitelinks|labels", "languages": "en"})
    e = d.get("entities", {}).get(QID) or {}
    cl = e.get("claims", {})
    dv = lambda p: [x["mainsnak"]["datavalue"]["value"] for x in cl.get(p, []) if "datavalue" in x["mainsnak"]]
    print(f"checked {now()} - {QID} (Wikidata)")
    print(f"  label: {e.get('labels', {}).get('en', {}).get('value')!r}")
    for v in dv("P625"):
        dist = evidence.hav_m(v["longitude"], v["latitude"], LON, LAT)
        flag = "" if dist <= 1000 else f"   <- FLAG: {dist / 1000:.1f} km from the catalog point"
        print(f"  P625: ({v['longitude']}, {v['latitude']}){flag}")
    print(f"  P373: {dv('P373')}  (row cat: {CAT!r})")
    print(f"  P31:  {[i.get('id') for i in dv('P31')]}")
    p131 = [i.get("id") for i in dv("P131")]
    if p131:
        d2 = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(p131), "props": "labels", "languages": "en"})
        print(f"  P131: {[(d2.get('entities', {}).get(q, {}).get('labels', {}).get('en', {}).get('value'), q) for q in p131]}")
    print(f"  enwiki: {e.get('sitelinks', {}).get('enwiki', {}).get('title')!r}")
    m = c.info([TITLE]).get(TITLE) or {}
    if not m.get("url"):
        raise SystemExit(f"not on Commons (title changed?): {TITLE}")
    d3 = c.get(c.CM, {"action": "query", "titles": TITLE, "prop": "categories"})
    cats = [x["title"].split(":", 1)[1] for x in next(iter(d3["query"]["pages"].values())).get("categories", [])]
    print(f"file: {TITLE}")
    print(f"  size: {m.get('w')}x{m.get('h')}  date: {m.get('date')!r}  artist: {m.get('artist')!r}  license: {m.get('license')!r}")
    print(f"  desc: {m.get('desc')!r}")
    print(f"  categories: {cats}")
    if CAT not in cats:
        raise SystemExit(f"R4 drift: the file is no longer in the {CAT!r} category (categories {cats}) - "
                         f"the category tie is broken, re-identify")
    return 0


def _grid_page(path, step=100):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    sc = 900 / max(im.size)
    c = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    _grid(c, 0, 0, sc, step, lambda v, _: str(v))
    return c


def sheet():
    """The fit session's inputs: the 800 m box and the page, both gridded. Ground grids are labelled in
    lon/lat (the page's px carry the pairs; the labels only help the eye)."""
    import aw
    from PIL import Image, ImageOps
    os.makedirs(OUT, exist_ok=True)
    p = _aerial()
    a = Image.open(p).convert("RGB")
    (lon0, lat1), (lon1, lat0) = _corners()[0], _corners()[2]
    X0, Y1 = aw.to_merc(lon0, lat1)
    X1, Y0 = aw.to_merc(lon1, lat0)

    def lab(col, row):
        x = X0 + (col + 0.5) / a.width * (X1 - X0)
        y = Y1 - (row + 0.5) / a.height * (Y1 - Y0)
        lon, lat = aw.to_lonlat(x, y)
        return f"{lon:.4f},{lat:.4f}"

    sc = 900 / max(a.size)
    ac = a.resize((round(a.width * sc), round(a.height * sc)), Image.LANCZOS)
    _grid(ac, 0, 0, sc, 100, lab)
    page = os.path.join(RAW_BOOKS, "212.jpg")
    if not os.path.exists(page):
        raise SystemExit("the page is not fetched yet (--fetch)")
    pg = _grid_page(page)
    S = Image.new("RGB", (ac.width + pg.width + 10, max(ac.height, pg.height)), "white")
    S.paste(ac, (0, 0))
    S.paste(pg, (ac.width + 10, 0))
    out = os.path.join(OUT, "mackenzie_212_sheet.jpg")
    S.save(out, quality=85)
    print(out, "ground", a.size, f"corners {lab(0, 0)} / {lab(a.width - 1, a.height - 1)}")
    # the LiDAR relief when the national source answers (OQ-5): the earthwork is clearer in it than in the aerial
    try:
        import dem_sources
        bbox = _bbox()
        src = dem_sources.source_for_bbox(bbox)
        if src is not None:
            import numpy as np
            dem = aw.fetch_dem(bbox, 800, 800)
            nz = float(np.sum(~np.isnan(dem)))
            print(f"  LiDAR {src['label']}: {nz:.0f}/640000 px with data", flush=True)
            if nz > 50e4:
                from PIL import Image as I
                img = ImageOps.autocontrast(I.fromarray(((dem - dem.min()) / (dem.max() - dem.min()) * 255).astype("uint8")
                                                        if not np.isnan(dem).all() else np.zeros((800, 800), "uint8")),
                                            cutoff=1).convert("RGB")
                rc = img.resize((round(800 * sc), round(800 * sc)), Image.LANCZOS)
                _grid(rc, 0, 0, sc, 100, lab)
                out2 = os.path.join(OUT, "mackenzie_212_relief.jpg")
                rc.save(out2, quality=85)
                print(out2)
    except Exception as ex:
        print(f"  (relief unavailable: {type(ex).__name__} {ex})", flush=True)


def zoom():
    """A 200 m ground crop at 0.25 m/px, gridded - the towers and the hall at the scale the pairs need."""
    import aw
    from PIL import Image
    os.makedirs(OUT, exist_ok=True)
    (x0, y0), (x1, y1) = (aw.to_merc(c[0], c[1]) for c in (_corners()[0], _corners()[2]))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = 1 / aw.ground_scale(LAT)
    h = 200 / 2 * k
    body = aw._get(AERIAL_URL, {"bbox": f"{cx - h:.2f},{cy - h:.2f},{cx + h:.2f},{cy + h:.2f}",
                                "bboxSR": 3857, "imageSR": 3857, "size": "800,800", "format": "jpg", "f": "image"})
    p = os.path.join(OUT, f"zoom_{SITE}.jpg")
    open(p + ".part", "wb").write(body)
    os.replace(p + ".part", p)
    im = Image.open(p).convert("RGB")
    (lon0, lat1), (lon1, lat0) = _corners()[0], _corners()[2]
    X0, Y1 = aw.to_merc(lon0, lat1)
    X1, Y0 = aw.to_merc(lon1, lat0)

    def lab(col, row):
        x = X0 + (col + 0.5) / im.width * (X1 - X0)
        y = Y1 - (row + 0.5) / im.height * (Y1 - Y0)
        lon, lat = aw.to_lonlat(x, y)
        return f"{lon:.4f},{lat:.4f}"

    sc = 900 / max(im.size)
    c = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    _grid(c, 0, 0, sc, 100, lab)
    out = os.path.join(OUT, f"zoom_{SITE}_sheet.jpg")
    c.save(out, quality=88)
    print(out, "800x800 px over 200 m (0.25 m/px)", f"centre {lab(400, 400)}")


def write_doc(crop, pairs):
    """The platefit doc, the hand-fit shape of the 25 (the castle-rising doc's keys): a new document only -
    the existing platefits are the human's and are never touched."""
    import urllib.parse
    if os.path.exists(DB_DOC):
        old = json.load(open(DB_DOC))
        if old.get("pairs") != pairs or old.get("crop") != crop:
            raise SystemExit(f"the doc {DB_DOC} already exists with different pairs/crop - it is not rewritten")
    c = _commons()
    m = c.info([TITLE]).get(TITLE) or {}
    cite = "; ".join(x for x in [m.get("artist") and f"by {m['artist']}", m.get("license"), m.get("page")] if x)
    doc = {"site": SITE, "plan": PLAN, "ia": None, "file": None, "crop": list(crop), "model": "similarity",
           "src": "commons", "url": f"media/commons/{SITE}/{PLAN[2:]}.jpg", "ref": TITLE,
           "size": [PAGE_W, PAGE_H], "pairs": [[u, v, lon, lat] for u, v, lon, lat in pairs],
           "label": YEAR, "title": f"Shotwick Castle, plan from Mackenzie, The Castles of England ({YEAR})",
           "book": "Wikimedia Commons", "cite": cite,
           "at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    tmp = DB_DOC + ".tmp"
    json.dump(doc, open(tmp, "w"), indent=1)
    os.replace(tmp, DB_DOC)
    print("wrote", DB_DOC)


def gate():
    """The gate on the committed doc's own anchors (docs/gate.md section 4: the hand fit's residual is the
    claim; transform=None solves the similarity from the pairs, exactly plan_fit.similarity)."""
    import fit_gate
    import plan_fit
    doc = json.load(open(DB_DOC))
    pairs = doc["pairs"]
    verdict, stats = fit_gate.gate(pairs)
    a, b, resid, k = plan_fit.similarity(pairs)
    print(f"gate: {verdict}  {stats}")
    print(f"similarity: |a| {abs(a):.5f} m/px-merc  rot {(__import__('math').degrees)(__import__('cmath').phase(a)):+.2f} deg"
          f"  residuals m {[round(float(r), 1) for r in resid]}  max {float(resid.max()):.1f}")
    if verdict != fit_gate.ACCEPT:
        raise SystemExit(f"the gate REJECTS the fit ({stats}) - re-pick the anchors (never move pairs to force a pass)")
    return 0


def _evidence():
    """The hand-recorded 200 tie: the file is in the site's own P373 category (Q7502621's P373 is 'Shotwick
    Castle', and the 2013 Flickr-dump file sits in exactly that category - verify() re-checks both live).
    record --live would reach the same row through the category route; the hand record stores what verify saw."""
    return {"rec": "evidence/1", "kind": "category", "checked": now(),
            "site_cat": CAT, "file_cat": CAT, "via": []}


def _file_row(meta):
    m = dict(meta)
    if _commons().year_of(TITLE, m) != int(YEAR):
        m = dict(m, date=YEAR, date_commons=m.get("date"))  # a scan whose page lost the book's details
    return {"site": SITE, "qid": QID, "title": TITLE, "year": int(YEAR), "wd_plan": False, "cat": CAT,
            "name": f"Shotwick Castle, plan from Mackenzie, The Castles of England ({YEAR})",
            "by": "fit/src_mackenzie.py", **m, "evidence": _evidence()}


def _extras_row():
    """The reason to build the unbuilt site (task Notes): the picture row + aerial_ok. 211 merges it into
    extras.jsonl and builds the site; the catalog's sites.jsonl row (the richer one) reads first in
    build_catalog, and the merge logs the duplicate against it (211 Notes)."""
    return {"id": SITE, "qid": QID, "name": "Shotwick Castle", "lon": LON, "lat": LAT, "region": "england",
            "kind": "motte", "aerial_ok": True, "source": "fit/src_mackenzie.py",
            "wikipedia": "https://en.wikipedia.org/wiki/Shotwick_Castle",
            "note": "built for the 1897 plan (task 206): the picture is the reason; the catalog row (sites.jsonl) "
                    "carries the same id and the full record (admin, heritage, designation)"}


def stage(dry=False):
    """Stage the one row into this task's files (append-only, idempotent on (site, title)). Drift fails loud."""
    c = _commons()
    have = {(r.get("site"), r.get("title")) for r in _load(FILES) + _load(CLASSIFIED)}
    if (SITE, TITLE) in have:
        print("already staged (idempotent, no-op)")
        return
    meta = c.info([TITLE]).get(TITLE) or {}
    if not meta.get("url"):
        raise SystemExit(f"not on Commons (title changed?): {TITLE}")
    if (meta.get("w"), meta.get("h")) != (PAGE_W, PAGE_H):
        raise SystemExit(f"the live file is {meta.get('w')}x{meta.get('h')}, the page is {PAGE_W}x{PAGE_H} - R4 drift")
    if not c.keep(TITLE, meta):
        raise SystemExit(f"commons.keep() would drop {TITLE!r}: fix the row or record the drop in docs/lead_mackenzie.md")
    if any(r.get("id") == SITE for r in _load(EXTRAS) + _load(EXTRAS_CANONICAL)):
        raise SystemExit(f"{SITE} already staged or already in the canonical extras.jsonl - no second row")
    f = _file_row(meta)
    cl = {"site": SITE, "title": TITLE, "p_plan": 1.0, "p_birdseye": 0.0, "p_photo": 0.0, "by": "hand"}
    ex = _extras_row()
    print("staged:", json.dumps(f, ensure_ascii=False)[:200], "...")
    print("classified:", json.dumps(cl))
    print("extras:", json.dumps(ex))
    if dry:
        return
    _append(FILES, [f])
    _append(CLASSIFIED, [cl])
    _append(EXTRAS, [ex])
    print("build (211):", SITE)


def check():
    """Offline (no network): the join + fit/evidence.py check over the staged row."""
    import evidence
    files = _load(FILES)
    cls = _load(CLASSIFIED)
    extras = _load(EXTRAS)
    sites = {s["id"]: s for s in _load(SITES_CANONICAL)}
    canonical = {(r.get("site"), r.get("title")) for r in _load(FILES_CANONICAL)}
    extras_canonical = {s["id"] for s in _load(EXTRAS_CANONICAL)}
    problems = []
    pics = [r for r in files if r.get("title")]
    if len(pics) != 1:
        problems.append(f"expected exactly one staged picture row, found {len(pics)}")
    for r in pics:
        if r.get("site") != SITE:
            problems.append(f"row site {r.get('site')!r} is not {SITE!r}")
        s = sites.get(SITE)
        if s is None or s.get("qid") != QID:
            problems.append(f"site {SITE} not in the catalog with QID {QID} (the existing-by-QID path)")
        if (r.get("site"), r.get("title")) in canonical:
            problems.append(f"staged title already in the canonical files.jsonl: {(r.get('site'), r.get('title'))}")
        if r.get("qid") != QID:
            problems.append(f"row qid {r.get('qid')!r} is not {QID}")
    if {(r.get("site"), r.get("title")) for r in cls} != {(r.get("site"), r.get("title")) for r in pics}:
        problems.append("the classified rows are not 1:1 with the file rows")
    for r in cls:
        if r.get("p_plan") != 1.0 or r.get("by") != "hand":
            problems.append(f"classified row wrong: {r}")
    if len(extras) != 1 or extras[0].get("id") != SITE or not extras[0].get("aerial_ok"):
        problems.append("the extras row is missing, wrong or not aerial_ok (211 would not build the site)")
    if SITE in extras_canonical:
        problems.append(f"{SITE} is already in the canonical extras.jsonl - the merge would double it")
    if os.path.exists(DB_DOC):
        d = json.load(open(DB_DOC))
        if d.get("site") != SITE or d.get("plan") != PLAN or d.get("size") != [PAGE_W, PAGE_H]:
            problems.append("the platefit doc does not match the staged row (site/plan/size)")
        if len(d.get("pairs", [])) < 4:
            problems.append(f"the doc has {len(d.get('pairs', []))} pairs (the gate needs >= 4)")
    else:
        problems.append("the platefit doc is not written yet (the fit session writes it)")
    for p in problems:
        print("join:", p)
    code, text = evidence.check(FILES, os.path.join(ROOT, "data", "books", ".no-books"))
    print(text)
    return 1 if problems else code


def _norm(rows):
    """The rows for the golden file: keys are sorted by the dump, 'checked' and 'date_commons' normalized (they
    vary with the staging date)."""
    out = []
    for r in rows:
        r = dict(r)
        if isinstance(r.get("date_commons"), str):
            r["date_commons"] = "0000-00-00"
        ev = r.get("evidence")
        if isinstance(ev, dict) and ev.get("checked"):
            r["evidence"] = dict(ev, checked="0000-00-00")
        out.append(r)
    return out


def golden(path=None):
    """Write tests/golden/src_mackenzie_sample.json: the staged rows and the doc, normalized."""
    p = path or os.path.join(ROOT, "tests", "golden", "src_mackenzie_sample.json")
    doc = json.load(open(DB_DOC)) if os.path.exists(DB_DOC) else None
    if doc is not None:
        doc = dict(doc, at="0000-00-00T00:00:00+00:00")
    out = {"extras": _norm(_load(EXTRAS)), "files": _norm(_load(FILES)),
           "classified": _norm(_load(CLASSIFIED)), "doc": doc}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", p)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--fetch":
        fetch()
    elif a and a[0] == "--verify":
        raise SystemExit(verify())
    elif a and a[0] == "--sheet":
        sheet()
    elif a and a[0] == "--zoom":
        zoom()
    elif a and a[0] == "--write-doc":
        x0, y0, x1, y1 = [int(float(v)) for v in a[1].split(",")]
        prs = []
        for t in a[2:]:
            l, r = t.split("=")
            prs.append([*map(float, l.split(",")), *map(float, r.split(","))])
        write_doc((x0, y0, x1, y1), prs)
    elif a and a[0] == "--gate":
        raise SystemExit(gate())
    elif a and a[0] == "--dry":
        stage(True)
    elif a and a[0] == "--check":
        raise SystemExit(check())
    elif a and a[0] == "--golden":
        golden()
    else:
        stage(False)
