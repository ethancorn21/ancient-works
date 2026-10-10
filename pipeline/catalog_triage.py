"""Relief-crop triage of US catalog entries with the local vision model (Qwen on the AI box).

The model only classifies a picture; it never writes facts. It sees no name, kind or place: just the relief
crop and a fixed description of what the picture is.

usage:
    catalog_triage.py validate      # crops + scores for the validation set (known positives, random negatives)
    catalog_triage.py batch [N]     # crops + Clef scores for the top N US entries by notability (default 150)
    catalog_triage.py sheet <set>   # contact sheets of the crops (validate | batch) for eyeball checks
    catalog_triage.py blind         # batch contact sheets with no scores, for labelling by eye first
    catalog_triage.py score_batch   # Clef vs the by-eye batch labels (triage_batch_handcheck.json)

Crops:   data/raw/catalog/crops/<id>.jpg (+ <id>.json: bbox, size, clip, valid share)
Labels:  data/raw/catalog/triage/<model>/<id>.json   (one file per crop, so runs resume)
Summary: data/catalog/triage_validation.json, data/catalog/triage.jsonl
"""
import json
import math
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "catalog")
CROPS = os.path.join(RAW, "crops")
OUT = os.path.join(ROOT, "data", "catalog")
SITES = os.path.join(OUT, "sites.jsonl")
LABELS = ("earthwork_visible", "nothing", "modern_only", "unsure")
PROMPT_VERSION = "v1"

PROMPT = """This picture is a LiDAR terrain image (bare earth, trees and buildings removed). Brightness shows \
local relief: ground higher than its surroundings is light, lower ground is dark, with a faint hillshade lit \
from the north-west. North is up. The picture covers {w} x {h} metres (1 pixel = {px} m).

Question: is there an artificial earthwork near the centre of the picture (within the middle third)?

Earthworks means things built of earth by people long ago, for example: burial mounds (round or oval bumps, \
usually 5-100 m across), flat-topped platform mounds with straight sides, low effigy mounds shaped like \
animals, embankment walls forming circles, squares, octagons or long lines, walls with ditches around a hilltop.

Not earthworks: roads, railways, highway embankments, field edges, plough marks, farm terraces, levees, \
ponds, quarries, building pads, golf courses, natural hills, gullies and river banks.

Labels:
- "earthwork_visible": an earthwork as described is clearly visible near the centre
- "modern_only": near the centre there are only modern features (roads, buildings, quarries, fields...)
- "nothing": near the centre there is only natural ground
- "unsure": something is there but you cannot tell whether it is an earthwork

Answer as JSON: {{"label": one of the four labels, "reason": "one short sentence on what you see"}}"""


def crop_size(site):
    """Ground size (m) of the crop: 800 m, or the members' spread + 400 m margin, capped at 2000 m."""
    size = VAL_SIZE
    if site.get("members"):
        from catalog import hav_m
        ext = max(hav_m(site["lon"], site["lat"], m["lon"], m["lat"]) for m in site["members"])
        size = max(size, min(2000, 2 * ext + 400))
    if site.get("extent_m"):
        size = max(size, min(2000, 2 * site["extent_m"] + 400))
    return int(size), int(size)


CLIP_M = 0.8    # one fixed contrast for every crop (validation and batch): per-crop auto contrast could
VAL_SIZE = 800  # leak the answer, e.g. a site with tall mounds gets a different stretch than flat farmland
DEMS = os.path.join(RAW, "dem")


def make_crop(cid, lon, lat, w_m, h_m, px=1.0, clip_m=CLIP_M):
    """Relief crop via aw.fetch_dem + aw.render_relief at a fixed clip. The DEM is cached
    (data/raw/catalog/dem/<id>.npz) so a re-render with other settings needs no download."""
    import aw
    os.makedirs(CROPS, exist_ok=True)
    os.makedirs(DEMS, exist_ok=True)
    jpg, meta_p = os.path.join(CROPS, cid + ".jpg"), os.path.join(CROPS, cid + ".json")
    want = {"lon": lon, "lat": lat, "w_m": w_m, "h_m": h_m, "px_m": px, "clip_m": clip_m}
    if os.path.exists(meta_p):
        meta = json.load(open(meta_p))
        if all(meta.get(k) == v for k, v in want.items()) and (meta.get("error") or os.path.exists(jpg)):
            return meta
    w, h = int(round(w_m / px)), int(round(h_m / px))
    bbox = aw.site_bbox(lon, lat, w_m, h_m)
    dem_p = os.path.join(DEMS, cid + ".npz")
    z = None
    if os.path.exists(dem_p):
        d = np.load(dem_p)
        if list(d["bbox"]) == list(bbox) and d["z"].shape == (h, w):
            z = d["z"].astype(np.float64)
    if z is None:
        z = aw.fetch_dem(bbox, w, h)
        np.savez_compressed(dem_p, z=z.astype(np.float32), bbox=np.array(bbox))
    valid = float(np.isfinite(z).mean())
    meta = {"id": cid, **want, "bbox": bbox, "valid_frac": round(valid, 3)}
    if valid < 0.5:
        meta["error"] = "no elevation data"
    else:
        img, clip = aw.render_relief(z, px, clip_m=clip_m)
        Image.fromarray(img).save(jpg, quality=90)
    json.dump(meta, open(meta_p, "w"))
    return meta


def label_dir():
    import llm
    return os.path.join(RAW, "triage", llm.MODEL + "-" + PROMPT_VERSION)


SERVERS = ["http://127.0.0.1:18080/v1/chat/completions",   # vLLM on the 3090 Ti
           "http://127.0.0.1:18081/v1/chat/completions"]   # second Qwen server on the 3090 (1 image/request)


QWEN_ENABLED = False  # 2026-10-10: the Qwen servers belong to Ethan's coding agents; our load slowed them, so
                     # the lead closed the tunnels. Only labels already cached (the validation run) are read.


def classify(cid, meta, url=None):
    import llm
    d = label_dir()
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, cid + ".json")
    crop = {k: meta.get(k) for k in ("lon", "lat", "w_m", "h_m", "px_m", "clip_m")}
    if os.path.exists(p):
        old = json.load(open(p))
        if old.get("crop") == crop:  # a label is reused only for the very same picture
            return old
    if not QWEN_ENABLED:
        return {"id": cid, "label": None, "error": "qwen disabled"}
    if meta.get("error"):
        out = {"id": cid, "label": None, "error": meta["error"]}
    else:
        prompt = PROMPT.format(w=meta["w_m"], h=meta["h_m"], px=meta["px_m"])
        t = time.time()
        ans = llm.ask_json(prompt, images=[os.path.join(CROPS, cid + ".jpg")], max_px=1600, max_tokens=300,
                           url=url or llm.URL)
        lab = ans.get("label") if isinstance(ans, dict) else None
        out = {"id": cid, "label": lab if lab in LABELS else None, "reason": (ans.get("reason") if isinstance(ans, dict) else None),
               "raw": None if lab in LABELS else ans, "seconds": round(time.time() - t, 1),
               "server": (url or llm.URL).split(":")[2][:5]}
    out["crop"] = crop
    json.dump(out, open(p, "w"))
    return out


def run(items, per_server=4):
    """items: [(cid, lon, lat, w_m, h_m)] -> {cid: label record}. Crops are fetched one at a time
    (3DEP is slow and 5xx-prone); requests alternate between the model servers, up to `per_server` at once
    on each (same model and weights on both; temperature 0)."""
    metas = {}
    for i, (cid, lon, lat, w_m, h_m) in enumerate(items):
        try:
            metas[cid] = make_crop(cid, lon, lat, w_m, h_m)
        except Exception as e:
            metas[cid] = {"id": cid, "error": "crop failed: " + str(e)[:200]}
        if i % 20 == 0:
            print(f"  crop {i + 1}/{len(items)} {cid}", flush=True)
    ids = [c for c, *_ in items]
    if not QWEN_ENABLED:  # cached labels only, no requests
        return {c: classify(c, metas[c]) for c in ids}
    up = [u for u in SERVERS if _alive(u)]
    if not up:
        raise SystemExit("no model server answers on " + ", ".join(SERVERS) + " (tunnel down?)")
    with ThreadPoolExecutor(per_server * len(up)) as ex:
        res = list(ex.map(lambda ic: classify(ic[1], metas[ic[1]], up[ic[0] % len(up)]), enumerate(ids)))
    return {r["id"]: r for r in res}


def _alive(url):
    import urllib.request
    try:
        with urllib.request.urlopen(url.replace("/chat/completions", "/models"), timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


# ---------------------------------------------------------------- validation set

KNOWN_POSITIVES = [  # standing works with a catalog point; each crop is still eyeballed (handcheck file)
    "Q968802",   # Serpent Mound
    "Q280444",   # Monks Mound (Cahokia)
    "Q964745",   # Poverty Point
    "Q4533107",  # Etowah Indian Mounds
    "Q1320821",  # Moundville
    "Q5470727",  # Fort Ancient
    "Q5597781",  # Grave Creek Mound
    "Q34827561",  # Miamisburg Mound
]
EXTRA_POSITIVES = os.path.join(OUT, "triage_extra_positives.json")  # more QIDs, picked from the catalog by eye
HANDCHECK = os.path.join(OUT, "triage_handcheck.json")  # {crop id: {"agrees": bool, "note": str}} by eye
CLEF_STATE = ("A LiDAR local-relief image: bare-earth elevation minus a smoothed copy, so ground higher than its "
              "surroundings is light and lower ground is dark. {w} x {h} m, 1 m per pixel, north up.")
CLEF_QUESTIONS = {
    # v1: the lead's question, asked first and unchanged
    "v1": {"earthwork": {"type": "noul", "instructions":
                         "Does this image show an ancient earthwork (a geometric enclosure wall or a burial mound)?"}},
    # v2: asked after seeing v1's results on the validation set, so its validation numbers are optimistic
    "v2": {"earthwork": {"type": "noul", "instructions":
                         "Is there an ancient earthwork near the centre of this image: a round or flat-topped mound, "
                         "or an earthen wall forming a circle, square or enclosure? Roads, railways, field edges, "
                         "ponds, quarries and natural gullies do not count."}},
}


def load_sites():
    return [json.loads(l) for l in open(SITES)]


def built_sites():
    """The six built sites, each at its site.json centre. (Their centres are the middle of the whole
    surveyed area, so the work itself is not always at the centre: see the handcheck.)"""
    out = []
    d = os.path.join(ROOT, "data", "sites")
    for sid in sorted(os.listdir(d)):
        p = os.path.join(d, sid, "site.json")
        if os.path.exists(p):
            s = json.load(open(p))
            out.append(("built-" + sid, s["lon"], s["lat"]))
    return out


def find_qid(sites, q):
    for s in sites:
        if s.get("qid") == q:
            return s, None
        for m in s.get("members", []):
            if m["qid"] == q:
                return s, m
    return None, None


def random_negatives(sites, n, seed=7):
    """Random points 3-8 km from every US catalog entry (and member), around notable US entries (so on
    similar terrain), where 3DEP has a 1 m LiDAR DEM."""
    import catalog_cover as cc
    pts = []
    for s in sites:
        if s["region"] != "us":
            continue
        pts.append((s["lon"], s["lat"]))
        pts += [(m["lon"], m["lat"]) for m in s.get("members", [])]
    P = np.radians(np.array(pts))
    rng = random.Random(seed)
    anchors = [s for s in sites if s["region"] == "us" and s.get("wiki_links", 0) >= 3]
    cache_p = os.path.join(RAW, "negatives.json")
    out = [tuple(x) for x in json.load(open(cache_p))] if os.path.exists(cache_p) else []
    tries = 0
    while len(out) < n and tries < 600:
        tries += 1
        a = rng.choice(anchors)
        r, th = rng.uniform(3000, 8000), rng.uniform(0, 2 * math.pi)
        lat = a["lat"] + r * math.cos(th) / 111320
        lon = a["lon"] + r * math.sin(th) / (111320 * math.cos(math.radians(a["lat"])))
        la, lo = math.radians(lat), math.radians(lon)
        d = 2 * 6371000 * np.arcsin(np.sqrt(np.sin((P[:, 1] - la) / 2) ** 2 +
                                            np.cos(la) * np.cos(P[:, 1]) * np.sin((P[:, 0] - lo) / 2) ** 2))
        if d.min() < 3000 or d.min() > 8000:
            continue
        cov = cc.check(lon, lat)
        if not cov.get("lidar_1m") or not cov.get("ok"):
            continue
        out.append((f"neg-{len(out):02d}", round(lon, 6), round(lat, 6)))
        print(f"  negative {len(out)}: {lon:.5f},{lat:.5f} near {a['name']} ({d.min():.0f} m from nearest entry)",
              flush=True)
        json.dump(out, open(cache_p, "w"))
    return out[:n]


def val_items(n_neg=35):
    sites = load_sites()
    pos = list(built_sites())
    qs = list(KNOWN_POSITIVES)
    if os.path.exists(EXTRA_POSITIVES):
        qs += [q for q in json.load(open(EXTRA_POSITIVES)) if q not in qs]
    for q in qs:
        s, m = find_qid(sites, q)
        if s is None:
            print("  known positive not in catalog:", q)
            continue
        pt = m or s
        pos.append((f"pos-{q.lower()}", pt["lon"], pt["lat"]))
    neg = random_negatives(sites, n_neg)
    return [(c, lon, lat, VAL_SIZE, VAL_SIZE, "positive") for c, lon, lat in pos] + \
           [(c, lon, lat, VAL_SIZE, VAL_SIZE, "negative") for c, lon, lat in neg]


def clef_scores(ids, q="v1", batch_size=6):
    """{crop id: P(earthwork)} from Clef-flash, cached per crop and question; one batch in flight at a time."""
    import clef
    d = os.path.join(RAW, "triage", "clef-flash" if q == "v1" else f"clef-flash-{q}")
    os.makedirs(d, exist_ok=True)
    out, todo, crops = {}, [], {}
    for c in ids:
        p, mp = os.path.join(d, c + ".json"), os.path.join(CROPS, c + ".json")
        if not os.path.exists(os.path.join(CROPS, c + ".jpg")) or not os.path.exists(mp):
            continue
        m = json.load(open(mp))
        crops[c] = {k: m.get(k) for k in ("lon", "lat", "w_m", "h_m", "px_m", "clip_m")}
        old = json.load(open(p)) if os.path.exists(p) else {}
        if old.get("crop") == crops[c]:
            out[c] = old["p"]
        else:
            todo.append(c)
    for i in range(0, len(todo), batch_size):
        chunk = todo[i:i + batch_size]
        ans = clef.decide_batch([(CLEF_STATE.format(w=crops[c]["w_m"], h=crops[c]["h_m"]), CLEF_QUESTIONS[q],
                                  [os.path.join(CROPS, c + ".jpg")]) for c in chunk])
        for c, a in zip(chunk, ans):
            out[c] = float(a["earthwork"]["noul"])
            json.dump({"id": c, "p": out[c], "raw": a, "crop": crops[c], "question": CLEF_QUESTIONS[q]},
                      open(os.path.join(d, c + ".json"), "w"))
    return out


def best_threshold(P, N):
    """In-sample threshold with the best recall - false-positive rate (Youden). Optimistic by construction."""
    best = (None, -1, None, None)
    for t in sorted(set(P + N)):
        r = sum(p >= t for p in P) / len(P)
        f = sum(n >= t for n in N) / len(N)
        if r - f > best[1]:
            best = (t, r - f, r, f)
    return {"threshold": round(best[0], 4), "recall": round(best[2], 3), "false_pos_rate": round(best[3], 3)}


def auc(pos, neg):
    """Mann-Whitney AUC (ties count half)."""
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return round(wins / (len(pos) * len(neg)), 3)


QWEN_SCORE = {"earthwork_visible": 1.0, "unsure": 0.5, "nothing": 0.0, "modern_only": 0.0, "none": 0.0}


def validate(n_neg=35):
    items = val_items(n_neg)
    res = run([i[:5] for i in items])
    cl = clef_scores([i[0] for i in items], "v1")
    cl2 = clef_scores([i[0] for i in items], "v2")
    hand = json.load(open(HANDCHECK)) if os.path.exists(HANDCHECK) else {}
    rows = []
    for cid, lon, lat, w, h, truth in items:
        r = res[cid]
        rows.append({"file": f"data/raw/catalog/crops/{cid}.jpg", "id": cid, "lon": lon, "lat": lat, "label": truth,
                     "qwen_label": r.get("label") or "none", "qwen_reason": r.get("reason"),
                     "clef_p": cl.get(cid), "clef_p_v2": cl2.get(cid), "hand_agrees": hand.get(cid, {}).get("agrees"),
                     "hand_note": hand.get(cid, {}).get("note"), "error": r.get("error")})
    with open(os.path.join(OUT, "triage_scores.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    def metrics(rs):
        table = {t: {l: 0 for l in LABELS + ("none",)} for t in ("positive", "negative")}
        for r in rs:
            table[r["label"]][r["qwen_label"]] += 1
        P = [r for r in rs if r["label"] == "positive"]
        N = [r for r in rs if r["label"] == "negative"]
        tp = sum(r["qwen_label"] == "earthwork_visible" for r in P)
        fp = sum(r["qwen_label"] == "earthwork_visible" for r in N)
        m = {"n_pos": len(P), "n_neg": len(N), "qwen_confusion": table,
             "qwen_recall": round(tp / len(P), 3) if P else None,
             "qwen_false_pos_rate": round(fp / len(N), 3) if N else None,
             "qwen_accuracy": round((tp + len(N) - fp) / len(rs), 3) if rs else None,
             "qwen_auc_from_labels": auc([QWEN_SCORE[r["qwen_label"]] for r in P], [QWEN_SCORE[r["qwen_label"]] for r in N]),
             "clef_auc": auc([r["clef_p"] for r in P if r["clef_p"] is not None],
                             [r["clef_p"] for r in N if r["clef_p"] is not None]),
             "clef_v2_auc": auc([r["clef_p_v2"] for r in P if r["clef_p_v2"] is not None],
                                [r["clef_p_v2"] for r in N if r["clef_p_v2"] is not None])}
        for key in ("clef_p", "clef_p_v2"):
            pp = [r[key] for r in P if r[key] is not None]
            nn = [r[key] for r in N if r[key] is not None]
            if pp and nn:
                m[key.replace("_p", "") + "_at_0.5"] = {"recall": round(sum(x >= 0.5 for x in pp) / len(pp), 3),
                                                        "false_pos_rate": round(sum(x >= 0.5 for x in nn) / len(nn), 3)}
                m[key.replace("_p", "") + "_best_in_sample"] = best_threshold(pp, nn)
        return m

    allm = metrics(rows)
    checked = [r for r in rows if r["hand_agrees"] is not False]
    # truth = what the picture shows by eye: a known-site crop whose work is not in the middle third counts as
    # a negative (that is the case the triage exists to catch: a point that misses the work)
    seen = [dict(r, label="negative" if r["label"] == "positive" and r["hand_agrees"] is False else r["label"])
            for r in rows]
    out = {"model": label_dir().rsplit("/", 1)[-1], "clip_m": CLIP_M, "size_m": VAL_SIZE, "px_m": 1.0,
           "prompt": PROMPT, "clef_state": CLEF_STATE, "clef_questions": CLEF_QUESTIONS, "all": allm,
           "qwen_note": ("Qwen labels come from one run on these 70 crops (prompt v1, two servers, temperature 0) "
                         "made before the lead stopped all Qwen use; no Qwen calls were made after that, and the "
                         "top-150 batch has no Qwen labels."),
           "hand_checked": metrics(checked) if hand else None,
           "truth_by_eye": metrics(seen) if hand else None,
           "n_hand_disagree": sum(r["hand_agrees"] is False for r in rows), "run": time.strftime("%Y-%m-%d %H:%M"),
           "note": ("'all' scores against the a-priori truth (known site vs random point). 'hand_checked' drops "
                    "crops where looking at the picture contradicts that truth (e.g. a site point that misses the "
                    "work, a random point that lands on a mound). Hand checks were done by Claude looking at the "
                    "same crops, not by a field archaeologist. 'truth_by_eye' keeps every crop but counts a known-site crop "
                    "whose work is not visible in the middle third as a negative.")}
    json.dump(out, open(os.path.join(OUT, "triage_validation.json"), "w"), indent=1)
    for k in ("all", "hand_checked", "truth_by_eye"):
        m = out[k]
        if m:
            print(k, {x: m.get(x) for x in ("n_pos", "n_neg", "qwen_recall", "qwen_false_pos_rate", "qwen_accuracy",
                                             "qwen_auc_from_labels", "clef_auc", "clef_v2_auc", "clef_best_in_sample",
                                             "clef_v2_best_in_sample")})
    return out


def batch(n=150):
    """Top n US entries by notability (forts typed 'fort' + 'earthworks', mostly Civil War, left out: not the
    kind of work this triage is for). Clef scores (questions v1 and v2) per crop; no Qwen."""
    sites = [s for s in load_sites() if s["region"] == "us" and s["kind"] != "military_earthwork"]
    sites.sort(key=lambda s: (-s.get("wiki_links", 0), -s.get("sitelinks", 0), s["name"]))
    top = sites[:n]
    items = [(s["id"], s["lon"], s["lat"], *crop_size(s)) for s in top]
    res = run(items)
    cl = clef_scores([s["id"] for s in top], "v1")
    cl2 = clef_scores([s["id"] for s in top], "v2")
    cov_p = os.path.join(OUT, "us_coverage.jsonl")
    cov = {r["id"]: r for r in map(json.loads, open(cov_p))} if os.path.exists(cov_p) else {}
    with open(os.path.join(OUT, "triage.jsonl"), "w") as f:
        for s in top:
            w, h = crop_size(s)
            f.write(json.dumps({"id": s["id"], "qid": s.get("qid"), "name": s["name"], "crop_m": w,
                                "clef_p": cl.get(s["id"]), "clef_p_v2": cl2.get(s["id"]),
                                "dem_res_m": cov.get(s["id"], {}).get("best_res_m"),
                                "model": "clef-flash", "clip_m": CLIP_M}, ensure_ascii=False) + "\n")
    print("scored", sum(s["id"] in cl for s in top), "of", len(top))


BATCH_HAND = os.path.join(OUT, "triage_batch_handcheck.json")  # {id: {"visible": true|false|null, "note": str}}


def blind_sheets(ids, name, per=12, cols=4, thumb=450):
    """Contact sheets with only index + id under each crop (no scores), for labelling by eye before looking
    at any model output. Middle third outlined."""
    os.makedirs(os.path.join(RAW, "sheets"), exist_ok=True)
    paths = []
    for k in range(0, len(ids), per):
        chunk = ids[k:k + per]
        rows = math.ceil(len(chunk) / cols)
        sh = Image.new("RGB", (cols * thumb, rows * (thumb + 18)), "white")
        d = ImageDraw.Draw(sh)
        for i, cid in enumerate(chunk):
            x, y = (i % cols) * thumb, (i // cols) * (thumb + 18)
            p = os.path.join(CROPS, cid + ".jpg")
            if os.path.exists(p):
                im = Image.open(p).convert("RGB")
                im.thumbnail((thumb - 4, thumb - 4))
                sh.paste(im, (x + 2, y + 2))
                w3, h3 = im.width / 3, im.height / 3
                d.rectangle([x + 2 + w3, y + 2 + h3, x + 2 + 2 * w3, y + 2 + 2 * h3], outline=(255, 0, 0))
            d.text((x + 4, y + thumb + 2), f"{k + i}: {cid[:52]}", fill="black")
        p = os.path.join(RAW, "sheets", f"{name}_{k // per:02d}.jpg")
        sh.save(p, quality=85)
        paths.append(p)
    return paths


def score_batch():
    """Clef on the batch against labels by eye (made before looking at the scores). The batch was not used to
    write question v2 or pick thresholds, so this is the out-of-sample test for both."""
    v = json.load(open(os.path.join(OUT, "triage_validation.json")))
    thr = {k: v["truth_by_eye"][k.replace("_p", "") + "_best_in_sample"]["threshold"] for k in ("clef_p", "clef_p_v2")}
    hand = json.load(open(BATCH_HAND))
    rows = [json.loads(l) for l in open(os.path.join(OUT, "triage.jsonl"))]
    for r in rows:
        h = hand.get(r["id"], {})
        r["hand_visible"], r["hand_note"] = h.get("visible"), h.get("note")
    with open(os.path.join(OUT, "triage.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    cur = {x["id"]: x for x in load_sites()}
    for r in rows:  # entries re-tagged or dropped by catalog fixes made after this batch ran
        x = cur.get(r["id"])
        r["catalog_now"] = "dropped" if x is None else ("military_earthwork" if x["kind"] == "military_earthwork" else None)
        if r["catalog_now"] is None:
            r.pop("catalog_now")
    with open(os.path.join(OUT, "triage.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    lab = [r for r in rows if r["hand_visible"] is not None and r.get("clef_p") is not None]
    P = [r for r in lab if r["hand_visible"]]
    N = [r for r in lab if not r["hand_visible"]]
    out = {"n_labelled": len(lab), "n_visible": len(P), "n_not_visible": len(N),
           "n_unclear": sum(r["hand_visible"] is None for r in rows), "thresholds_from_validation": thr}
    for k in ("clef_p", "clef_p_v2"):
        pp, nn = [r[k] for r in P], [r[k] for r in N]
        t = thr[k]
        out[k] = {"auc": auc(pp, nn), "recall_at_val_threshold": round(sum(x >= t for x in pp) / len(pp), 3) if pp else None,
                  "false_pos_at_val_threshold": round(sum(x >= t for x in nn) / len(nn), 3) if nn else None}
    t2 = thr["clef_p_v2"]
    cm = {"visible_yes": sum(r["clef_p_v2"] >= t2 for r in P), "visible_no": sum(r["clef_p_v2"] < t2 for r in P),
          "notvisible_yes": sum(r["clef_p_v2"] >= t2 for r in N), "notvisible_no": sum(r["clef_p_v2"] < t2 for r in N)}
    out["clef_v2_confusion_at_val_threshold"] = cm
    later = [r["name"] + " (" + r["catalog_now"] + ")" for r in rows if r.get("catalog_now")]
    out["text"] = (f"Batch check by eye (Claude, before looking at the scores): of {len(rows)} crops, "
                   f"{len(P)} show an earthwork in the middle third, {len(N)} do not, {out['n_unclear']} unclear. "
                   f"Clef on this held-out set: question v1 AUC {out['clef_p']['auc']}, v2 AUC {out['clef_p_v2']['auc']}; "
                   f"at the thresholds picked on the validation set, v1 recall {out['clef_p']['recall_at_val_threshold']} "
                   f"/ false-pos {out['clef_p']['false_pos_at_val_threshold']}, v2 recall "
                   f"{out['clef_p_v2']['recall_at_val_threshold']} / false-pos {out['clef_p_v2']['false_pos_at_val_threshold']}. "
                   f"Clef v2 at p >= {t2}: of {cm['visible_yes'] + cm['notvisible_yes']} crops it passes, "
                   f"{cm['visible_yes']} show a work by eye; of {cm['visible_no'] + cm['notvisible_no']} it flags, "
                   f"{cm['notvisible_no']} show none. Entries in this batch that later catalog fixes dropped or "
                   f"re-tagged: " + (", ".join(later) or "none") + ".")
    json.dump(out, open(os.path.join(OUT, "triage_batch_eval.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


def sheet(which, per=20, thumb=380):
    """Contact sheets with the id + model label under each crop, for checking by eye."""
    if which == "validate":
        rows = [(r["id"], f"{r['label'][:3]} q={r['qwen_label']} c={r['clef_p']:.2f}" if r["clef_p"] is not None
                 else f"{r['label'][:3]} q={r['qwen_label']}") for r in map(json.loads, open(os.path.join(OUT, "triage_scores.jsonl")))]
    else:
        rows = [(r["id"], r["label"] or "none") for r in map(json.loads, open(os.path.join(OUT, "triage.jsonl")))]
    os.makedirs(os.path.join(RAW, "sheets"), exist_ok=True)
    paths = []
    for k in range(0, len(rows), per):
        chunk = rows[k:k + per]
        cols = 5
        H = math.ceil(len(chunk) / cols)
        sh = Image.new("RGB", (cols * thumb, H * (thumb + 34)), "white")
        d = ImageDraw.Draw(sh)
        for i, (cid, lab) in enumerate(chunk):
            p = os.path.join(CROPS, cid + ".jpg")
            x, y = (i % cols) * thumb, (i // cols) * (thumb + 34)
            if os.path.exists(p):
                im = Image.open(p).convert("RGB")
                im.thumbnail((thumb - 6, thumb - 6))
                sh.paste(im, (x + 3, y + 3))
                # middle third outlined (on the sheet only, never on the model's input)
                w3, h3 = im.width / 3, im.height / 3
                d.rectangle([x + 3 + w3, y + 3 + h3, x + 3 + 2 * w3, y + 3 + 2 * h3], outline=(255, 0, 0))
            d.text((x + 4, y + thumb), f"{k + i}: {cid[:44]}", fill="black")
            d.text((x + 4, y + thumb + 15), lab, fill="black")
        p = os.path.join(RAW, "sheets", f"{which}_{k // per:02d}.jpg")
        sh.save(p, quality=85)
        paths.append(p)
    print("\n".join(paths))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "validate":
        validate()
    elif cmd == "batch":
        batch(int(sys.argv[2]) if len(sys.argv) > 2 else 150)
    elif cmd == "sheet":
        sheet(sys.argv[2])
    elif cmd == "blind":  # blind sheets of the batch crops
        ids = [json.loads(l)["id"] for l in open(os.path.join(OUT, "triage.jsonl"))]
        print("\n".join(blind_sheets(ids, "batch_blind")))
    elif cmd == "score_batch":
        score_batch()
