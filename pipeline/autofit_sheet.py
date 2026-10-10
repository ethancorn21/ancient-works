"""Contact sheets and the results table for the auto-fit test (docs/autofit.md).

usage: autofit_sheet.py [tag ...]   (default: auto hand auto_noqwen)
Writes data/autofit/<id>_sheet.jpg from the primary run (tag "auto") and prints a markdown table per tag.
Left panel: relief, hand-fit walls and plate frame (blue), the auto template under the auto fit of the median seed
(red), and the plate frames of all 8 auto fits (thin red; one that sits on the blue frame is a good fit).
Right panel: what the extractor kept on the plate (data/autofit/<id>_walls.jpg).
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import autofit as af  # noqa: E402

BLUE, RED = (40, 110, 230), (220, 30, 50)


def near_hand(S, c):
    """Is a coarse candidate (obj, s, rot_deg, t) inside the hand fit's basin (30 m / 4 deg / 8%)?"""
    _, s, rot_deg, t = c
    drot = (math.radians(rot_deg) - S.hand_rot + math.pi) % (2 * math.pi) - math.pi
    return (np.hypot(*(np.array(t) - S.hand_t)) <= 30 and abs(math.degrees(drot)) <= 4
            and abs(math.log(s / S.hand_s)) <= 0.08)


def sheet(sid, res, out_path, H=900):
    S = af.Site(sid)
    P, N, w = af.load_template(S, res["template"])
    ignore = S.water | S.modern
    img, _ = aw.render_relief(S.z, S.px_m, ignore=ignore, radius_m=S.lrm_radius)
    rel = Image.fromarray(img).convert("RGB")
    k = H / rel.height
    rel = rel.resize((round(rel.width * k), H), Image.LANCZOS)
    d = ImageDraw.Draw(rel)

    def px(en):
        return [((e + S.W_m / 2) / S.px_m * k, (S.H_m / 2 - n) / S.px_m * k) for e, n in en]

    rows = res["sites"][sid]["seeds"]
    order = sorted(range(len(rows)), key=lambda i: rows[i]["corner_rms_m"])
    med = rows[order[len(order) // 2]]
    for r in rows:
        fr = px(S.corners_ground(af.sim(r["s"], math.radians(r["rot_deg"])), np.array(r["t"])))
        d.line(fr + fr[:1], fill=RED, width=1)
    fr = px(S.corners_ground(S.hand_M, S.hand_t))
    d.line(fr + fr[:1], fill=BLUE, width=3)
    hp, _, _ = af.hand_template(S)
    for x, y in px(S.to_ground(hp, S.hand_M, S.hand_t)):
        d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=BLUE)
    Mm = af.sim(med["s"], math.radians(med["rot_deg"]))
    for x, y in px(S.to_ground(P, Mm, np.array(med["t"]))):
        d.rectangle((x - 0.7, y - 0.7, x + 0.7, y + 0.7), fill=RED)
    walls = Image.open(os.path.join(af.OUT, sid + "_walls.jpg")).convert("RGB")
    walls = walls.resize((round(walls.width * H / walls.height), H), Image.LANCZOS)
    top = 64
    out = Image.new("RGB", (rel.width + walls.width + 12, H + top), (250, 247, 238))
    out.paste(rel, (0, top))
    out.paste(walls, (rel.width + 12, top))
    d = ImageDraw.Draw(out)
    n_pass = res["sites"][sid]["n_pass"]
    d.text((8, 6), "%s  template: %s   %d/8 seeds pass   tol %.1f m   blue = hand fit (walls, frame)   "
                   "red = auto fits (8 frames; points = median seed)" % (sid, res["template"], n_pass, S.tol_m),
           fill=(30, 30, 30))
    d.text((8, 24), "median seed %d: corner RMS %.1f m, rotation %+.2f deg, scale x%.3f, median contrast %.3f m "
                    "(null p99 %.3f)" % (med["seed"], med["corner_rms_m"], med["drot_deg"], med["scale_ratio"],
                                         med["median_contrast_m"], med["null_p99_m"]), fill=(30, 30, 30))
    d.text((8, 42), "per seed RMS m: " + ", ".join("%.0f" % r["corner_rms_m"] for r in rows), fill=(30, 30, 30))
    d.text((rel.width + 20, 42), "extracted template (red) and blanked Qwen boxes (blue)", fill=(30, 30, 30))
    out.save(out_path, quality=78, optimize=True)
    return os.path.getsize(out_path) // 1024


def table(tag):
    path = os.path.join(af.OUT, "results_%s.json" % tag)
    if not os.path.exists(path):
        print("(no %s)" % path)
        return
    res = json.load(open(path))
    print("\n### %s (template: %s)\n" % (tag, res["template"]))
    print("| site | tol m | seeds pass | corner RMS m per seed (median) | rot err deg (median abs) | scale ratio range | "
          "median contrast at fit vs null p99 | hand basin in coarse top-8 | objective: fit / at hand fit |")
    print("|---|---|---|---|---|---|---|---|---|")
    sites_pass = 0
    for sid in af.SITES:
        if sid not in res["sites"]:
            continue
        S = af.Site(sid)
        r = res["sites"][sid]
        rows = r["seeds"]
        rms = [x["corner_rms_m"] for x in rows]
        basin = sum(any(near_hand(S, c) for c in x["top_coarse"]) for x in rows)
        sites_pass += r["n_pass"] >= 6
        print("| %s | %.1f | %d/8 | %s (%.0f) | %.2f | %.3f-%.3f | %.3f / %.3f (med) | %d/8 | %.3f / %.3f |" % (
            sid, r["tol_m"], r["n_pass"], " ".join("%.0f" % v for v in rms), float(np.median(rms)),
            float(np.median([abs(x["drot_deg"]) for x in rows])), min(x["scale_ratio"] for x in rows),
            max(x["scale_ratio"] for x in rows), float(np.median([x["median_contrast_m"] for x in rows])),
            float(np.median([x["null_p99_m"] for x in rows])), basin,
            float(np.median([x["objective"] for x in rows])), r["template_objective_at_hand_fit"]))
    n_seed = sum(x["passed"] for r in res["sites"].values() for x in r["seeds"])
    n_tot = sum(len(r["seeds"]) for r in res["sites"].values())
    print("\nSites passing (>= 6/8): %d/%d. Seeds passing: %d/%d." % (sites_pass, len(res["sites"]), n_seed, n_tot))
    fails_null = sum(x["pass_null"] and not (x["pass_rms"] and x["pass_rot"]) for r in res["sites"].values()
                     for x in r["seeds"])
    print("Wrong fits (RMS or rotation fail) that still beat null p99: %d." % fails_null)


if __name__ == "__main__":
    tags = sys.argv[1:] or ["auto", "hand", "auto_noqwen"]
    if "auto" in tags and os.path.exists(os.path.join(af.OUT, "results_auto.json")):
        res = json.load(open(os.path.join(af.OUT, "results_auto.json")))
        for sid in res["sites"]:
            kb = sheet(sid, res, os.path.join(af.OUT, sid + "_sheet.jpg"))
            print("sheet", sid, kb, "KB")
    for t in tags:
        table(t)
