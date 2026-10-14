"""How far an old survey sheet sits from today's ground at one site, measured, and the bend that would fix it.

Owner 2026-10-14: survey sheets (TMK 1850, Cassini, Etat-major, OS) are laid on as their archive georeferenced
them (one fit per 30-80 km sheet), never checked at site scale; rivers land in fields, roads in rivers. This
measures each sheet against two independent grounds of the same site box - today's aerial photograph and the
LiDAR relief - with RoMa (dense cross-modal matcher, 5060 Ti, ROMA_URL) and reports:

  rigid  - the best similarity (shift, turn, scale) sheet -> ground over RANSAC inliers; its inlier fraction
           says whether there is any agreement at all.
  bend   - a thin-plate spline through locally consistent matches (grid-thinned), kept only when it predicts
           held-out matches better than the rigid fit and no point moves more than MAX_BEND_M past it.

Features that are gone (a filled river, a lost road) have nothing to match on the aerial, so they cannot pull
the sheet; they ride along with the surrounding matched ground and stay where the surveyor drew them.

usage: fit/sheetfit.py <site> <sheet stem> [...]       (writes data/sheetfit/<site>.<stem>.json + check jpgs)
"""
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "fit"))
sys.path.insert(0, str(ROOT / "tools"))
import matchfit  # noqa: E402  (match(), ransac(): the same client and RANSAC the drawing fits use)
import fitkit  # noqa: E402

OUT = ROOT / "data" / "sheetfit"
RIGID_TOL_M = 25.0      # RANSAC inlier distance for the similarity
MIN_CELL_MATCHES = 5   # a control cell needs this many consistent matches
CELL_TOL_M = 20.0      # a cell's shift must sit within this of its neighbour cells' median
LOCAL_TOL_M = 12.0      # a match is locally consistent when within this of its neighbours' median displacement
CELL_M = 80.0           # thinning grid for the spline's control points
MAX_BEND_M = 80.0       # largest move (95th pct where there is data) the bend may add: 2x the 40 m Etat-major/TMK estimate
SMOOTH = 2.0            # thin-plate smoothing (metres^2 per point, as build_site.warp_plate)


def aerial(sid):
    """Today's aerial photograph of the site box (cached by fitkit in data/raw/aerial, never published)."""
    old = os.environ.get("FITKIT_GROUND")
    os.environ["FITKIT_GROUND"] = "aerial"
    try:
        return fitkit.ground(sid)
    finally:
        if old is None:
            os.environ.pop("FITKIT_GROUND")
        else:
            os.environ["FITKIT_GROUND"] = old


def grounds(sid):
    out = [("aerial", Image.open(aerial(sid)).convert("RGB"))]
    rel = ROOT / "web" / "data" / "sites" / sid / "relief.jpg"
    if rel.is_file():
        out.append(("relief", Image.open(rel).convert("RGB")))
    return out


def measure(sheet, ground, m_px):
    """Matches sheet px -> ground px (ground resized to the sheet's frame) and the rigid fit in metres."""
    g = ground.resize(sheet.size, Image.BILINEAR)
    a, b = matchfit.match(sheet, g, matchfit.ROMA_URL)
    if len(a) < 10:
        return {"matches": int(len(a))}, a, b
    res = matchfit.ransac(a, b, RIGID_TOL_M / m_px)
    if res is None:
        return {"matches": int(len(a)), "inliers": 0}, a, b
    m, s, t = res
    W, H = sheet.size
    c = complex(W / 2, H / 2)
    shift = (s * c + t - c) * m_px
    A = a[:, 0] + 1j * a[:, 1]
    resid = np.abs(s * A[m] + t - (b[m, 0] + 1j * b[m, 1])) * m_px
    # the sheet as laid on today (identity): how many matches already agree, and how closely
    D0 = np.abs(A - (b[:, 0] + 1j * b[:, 1])) * m_px
    m0 = D0 < RIGID_TOL_M
    Dr = np.abs(s * A + t - (b[:, 0] + 1j * b[:, 1])) * m_px
    both = (D0 < 3 * MAX_BEND_M) & (Dr < 3 * MAX_BEND_M)   # matches plausible under either: compare like with like
    return {"matches": int(len(a)), "inliers": int(m.sum()), "fraction": round(float(m.mean()), 3),
            "asis_fraction": round(float(m0.mean()), 3),
            "asis_err_m": round(float(np.median(D0[both])), 1) if both.any() else None,
            "rigid_err_m": round(float(np.median(Dr[both])), 1) if both.any() else None,
            "shift_m": round(abs(shift), 1), "shift_en_m": [round(shift.real, 1), round(-shift.imag, 1)],
            "rot_deg": round(math.degrees(np.angle(s)), 2), "scale": round(abs(s), 4),
            "resid_med_m": round(float(np.median(resid)), 1),
            "spread": matchfit.spread(a[m].tolist()), "_s": s, "_t": t, "_mask": m}, a, b


def bend(a, b, rigid, m_px, size):
    """Thin-plate spline ground px -> sheet px through locally consistent matches; None when it does not earn
    its place (held-out error no better than rigid, or a move past MAX_BEND_M)."""
    from scipy.interpolate import RBFInterpolator
    from scipy.spatial import cKDTree
    s, t = rigid["_s"], rigid["_t"]
    A = a[:, 0] + 1j * a[:, 1]
    B = b[:, 0] + 1j * b[:, 1]
    # residual displacement after the rigid fit, in metres, at each match's ground position
    d = (B - (s * A + t)) * m_px
    near = np.abs(d) < 3 * MAX_BEND_M                       # gross mismatches never enter the bend
    if near.sum() < 30:
        return {"why": f"only {int(near.sum())} matches near the rigid fit"}
    P = np.c_[B.real, B.imag][near] * m_px                   # ground positions (m)
    D = d[near]
    tree = cKDTree(P)
    _, nb = tree.query(P, k=min(12, len(P)))
    med = np.array([np.median(D[i].real) + 1j * np.median(D[i].imag) for i in nb])
    ok = np.abs(D - med) < LOCAL_TOL_M
    P, D = P[ok], D[ok]
    if len(P) < 30:
        return {"why": f"only {len(P)} locally consistent matches"}
    cell = np.floor(P / CELL_M).astype(int)
    keys, inv = np.unique(cell[:, 0] * 100000 + cell[:, 1], return_inverse=True)
    CP = np.array([P[inv == k].mean(0) for k in range(len(keys))])
    CD = np.array([np.median(D[inv == k].real) + 1j * np.median(D[inv == k].imag) for k in range(len(keys))])
    cnt = np.bincount(inv, minlength=len(keys))
    keep = cnt >= MIN_CELL_MATCHES
    CP, CD = CP[keep], CD[keep]
    # cell-level consistency: a cell whose shift disagrees with its neighbouring cells is a bad local match
    # (a field edge matched to a modern street), not map distortion; Douai's suburbs showed 100+ m arrows in
    # clashing directions before this
    for _ in range(2):
        if len(CP) < 9:
            break
        _, nb = cKDTree(CP).query(CP, k=9)
        med = np.array([np.median(CD[i[1:]].real) + 1j * np.median(CD[i[1:]].imag) for i in nb])
        ok = np.abs(CD - med) < CELL_TOL_M
        CP, CD = CP[ok], CD[ok]
    if len(CP) < 6:
        return {"why": f"matches cover only {len(CP)} consistent cells of {CELL_M:.0f} m"}
    # held-out check by cell: rigid error = |CD| (rigid predicts 0 extra displacement), bend error = spline miss
    rng = np.random.default_rng(0)
    fold = rng.integers(0, 5, len(CP))
    err_rigid, err_bend = [], []
    for k in range(5):
        tr, te = fold != k, fold == k
        if te.sum() == 0 or tr.sum() < 4:
            continue
        f = RBFInterpolator(CP[tr], np.c_[CD[tr].real, CD[tr].imag], kernel="thin_plate_spline", smoothing=SMOOTH)
        pr = f(CP[te])
        err_bend += list(np.abs(CD[te] - (pr[:, 0] + 1j * pr[:, 1])))
        err_rigid += list(np.abs(CD[te]))
    f = RBFInterpolator(CP, np.c_[CD.real, CD.imag], kernel="thin_plate_spline", smoothing=SMOOTH)
    W, H = size
    gx, gy = np.meshgrid(np.linspace(0, W * m_px, 25), np.linspace(0, H * m_px, 25))
    Q = np.c_[gx.ravel(), gy.ravel()]
    inside = cKDTree(CP).query(Q)[0] <= 1.5 * CELL_M           # judge the bend where it has data, not extrapolation
    mv = f(Q[inside])
    max_move = float(np.percentile(np.hypot(mv[:, 0], mv[:, 1]), 95))
    out = {"control_cells": int(len(CP)), "consistent_matches": int(len(P)),
           "heldout_rigid_m": round(float(np.median(err_rigid)), 1), "heldout_bend_m": round(float(np.median(err_bend)), 1),
           "max_move_m": round(max_move, 1), "_f": f, "_cp": CP, "_cd": CD}
    if out["heldout_bend_m"] >= 0.8 * out["heldout_rigid_m"]:
        out["why"] = "bend does not predict held-out matches clearly better than the rigid fit"
    elif max_move > MAX_BEND_M:
        out["why"] = f"bend would move ground {max_move:.0f} m past the rigid fit (cap {MAX_BEND_M:.0f})"
    return out


def warp(sheet, rigid, bendf, m_px, support=None):
    """The sheet resampled onto the ground frame: rigid (and bend when given). Output px = ground px."""
    W, H = sheet.size
    gx, gy = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
    G = gx.ravel() + 1j * gy.ravel()
    if bendf is not None:
        # the bend is smooth: evaluate it on a coarse grid (every 16 px) and interpolate, not at every pixel
        from scipy.ndimage import zoom
        step = 16
        cx, cy = np.meshgrid(np.arange(0, W + step, step) + 0.5, np.arange(0, H + step, step) + 0.5)
        C = np.c_[cx.ravel(), cy.ravel()] * m_px
        mv = bendf(C)
        n = np.hypot(mv[:, 0], mv[:, 1])
        mv *= np.minimum(1, MAX_BEND_M / np.maximum(n, 1e-9))[:, None]   # past the data the spline extrapolates: clamp
        if support is not None:   # and fade back to the rigid fit away from the control cells
            from scipy.spatial import cKDTree
            dist = cKDTree(support).query(C)[0]
            mv *= np.clip(1 - (dist - 1.5 * CELL_M) / (2 * CELL_M), 0, 1)[:, None]
        full = [zoom(mv[:, k].reshape(cx.shape), step, order=1)[:H, :W].ravel() for k in (0, 1)]
        G = G - (full[0] + 1j * full[1]) / m_px            # undo the extra displacement first
    S = (G - rigid["_t"]) / rigid["_s"]                       # then invert the rigid map
    from scipy.ndimage import map_coordinates
    arr = np.asarray(sheet.convert("RGBA"), dtype=np.float32)
    out = np.stack([map_coordinates(arr[..., c], [S.imag.reshape(H, W) - 0.5, S.real.reshape(H, W) - 0.5],
                                    order=1, cval=0) for c in range(4)], -1)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA")


def overlay(ground, sheet_rgba, size):
    g = ground.resize(size).convert("RGBA")
    a = np.array(sheet_rgba)
    a[..., 3] = (a[..., 3].astype(float) * 0.75).astype(np.uint8)
    return Image.alpha_composite(g, Image.fromarray(a)).convert("RGB")


def cross_check(fit, other, m_px):
    """The aerial-built correction scored on the relief's matches (never seen by it): median miss in metres of
    the sheet as laid, shifted, and shifted + bent, over relief matches plausible under any of the three."""
    a, b = other["_a"], other["_b"]
    if len(a) < 30:
        return {"why": "too few relief matches"}
    A = a[:, 0] + 1j * a[:, 1]
    B = b[:, 0] + 1j * b[:, 1]
    R = fit["_s"] * A + fit["_t"]
    e0, e1 = np.abs(A - B) * m_px, np.abs(R - B) * m_px
    out = {"asis_m": None, "shift_m": None, "bend_m": None}
    e2 = None
    if fit.get("_bendf") is not None:
        mv = fit["_bendf"](np.c_[R.real, R.imag] * m_px)
        n = np.hypot(mv[:, 0], mv[:, 1])
        mv *= np.minimum(1, MAX_BEND_M / np.maximum(n, 1e-9))[:, None]
        from scipy.spatial import cKDTree
        dist = cKDTree(fit["_cp"]).query(np.c_[R.real, R.imag] * m_px)[0]
        mv *= np.clip(1 - (dist - 1.5 * CELL_M) / (2 * CELL_M), 0, 1)[:, None]
        e2 = np.abs(R + (mv[:, 0] + 1j * mv[:, 1]) / m_px - B) * m_px
    lim = 3 * MAX_BEND_M
    ok = (e0 < lim) | (e1 < lim) | ((e2 < lim) if e2 is not None else False)
    if ok.sum() < 30:
        return {"why": "too few relief matches near any placement"}
    out["n"] = int(ok.sum())
    out["asis_m"] = round(float(np.median(e0[ok])), 1)
    out["shift_m"] = round(float(np.median(e1[ok])), 1)
    if e2 is not None:
        out["bend_m"] = round(float(np.median(e2[ok])), 1)
    out["within_25m"] = {"asis": round(float((e0[ok] < 25).mean()), 3), "shift": round(float((e1[ok] < 25).mean()), 3),
                         "bend": round(float((e2[ok] < 25).mean()), 3) if e2 is not None else None}
    return out


AGREE_M = 30.0      # the aerial and the relief must put the rigid shift within this of each other
AGREE_SCALE = 0.05  # ... and the scale within this
GOOD_M = 12.0       # a sheet already this close is left alone (OS six-inch sits at ~6 m)
ROUGH_OK = 0.4      # share of relief matches within 25 m that still counts as lining up
ACCEPT_M = 30.0     # a fix must also END within this on the relief (Cassini 364 -> 125 m was 'confirmed' before)
GAIN = 0.7          # a correction must cut the median match error to this share of the as-is error


def decide(rep):
    """'as is' (lines up already) | 'shift' (rigid) | 'bend' (rigid + spline) | 'unsure' (could not confirm the
    sheet lines up anywhere: flag it). Corrections are built on the aerial and must also bring the relief's own
    matches closer (cross check): two independent grounds."""
    a = rep["grounds"].get("aerial", {})
    c = rep.get("cross") or {}
    if a.get("rigid_err_m") is None or a.get("asis_err_m") is None:
        return {"use": "unsure", "why": "no consistent matches on the aerial"}
    near = [x for x in (a.get("asis_err_m"), c.get("asis_m")) if x is not None]
    if min(near) <= GOOD_M:
        return {"use": "as is", "why": f"already within {min(near)} m of today's ground"}
    if "asis_m" not in c:
        return {"use": "unsure", "why": "no independent check: " + c.get("why", "no relief")}
    use = "bend" if "why" not in a.get("bend", {"why": 1}) and c.get("bend_m") is not None else "shift"
    for u in ([use, "shift"] if use == "bend" else ["shift"]):
        got = c["bend_m"] if u == "bend" else c["shift_m"]
        if a["rigid_err_m"] <= GAIN * a["asis_err_m"] or u == "bend":
            if got <= GAIN * c["asis_m"] and got <= ACCEPT_M:
                return {"use": u, "why": f"relief matches {c['asis_m']} m as laid -> {got} m ({u})"}
    if c["within_25m"]["asis"] >= ROUGH_OK:
        return {"use": "as is", "why": f"{c['within_25m']['asis']:.0%} of relief matches within 25 m as laid; no confirmed fix"}
    return {"use": "unsure", "why": f"only {c['within_25m']['asis']:.0%} of relief matches within 25 m as laid, and no fix confirmed"}


def run(sid, stem):
    d = ROOT / "web" / "data" / "sites" / sid
    dep = next(x for x in json.loads((d / "depictions.json").read_text())["depictions"]
               if x.get("kind") == "map" and x["file"].split(".")[0] == stem)
    sheet = Image.open(d / dep["file"]).convert("RGB")
    ink = Image.open(d / dep["ink"]).convert("RGBA") if dep.get("ink") and (d / dep["ink"]).is_file() else None
    site = fitkit.site(sid)
    m_px = site["size_m"][0] / sheet.size[0]
    rep = {"site": sid, "sheet": stem, "label": dep.get("label"), "m_per_px": round(m_px, 3), "grounds": {}}
    best, raw = None, {}
    for name, g in grounds(sid):
        r, a, b = measure(sheet, g, m_px)
        if "_s" in r:
            # a sheet already on today's ground gets no bend (Dunster: a 36 m phantom move on a 6 m sheet)
            bd = bend(a, b, r, m_px, sheet.size) if (r["asis_err_m"] or 1e9) > GOOD_M else {"why": "already lines up"}
            r["bend"] = {k: v for k, v in bd.items() if not k.startswith("_")}
            r["_bendf"] = bd.get("_f") if "why" not in bd else None
            r["_cp"] = bd.get("_cp")
            r["_cd"] = bd.get("_cd")
            if name == "aerial" or best is None:
                best = (name, g, r)
        r["_a"], r["_b"] = a, b
        raw[name] = r
        rep["grounds"][name] = {k: v for k, v in r.items() if not k.startswith("_")}
    ga, gr = rep["grounds"].get("aerial", {}), rep["grounds"].get("relief", {})
    if "shift_en_m" in ga and "shift_en_m" in gr:
        rep["grounds_agree_m"] = round(math.dist(ga["shift_en_m"], gr["shift_en_m"]), 1)
    if "aerial" in raw and "_s" in raw["aerial"] and "relief" in raw:
        rep["cross"] = cross_check(raw["aerial"], raw["relief"], m_px)
    rep["decision"] = decide(rep)
    ga = raw.get("aerial", {})
    if "_s" in ga:   # what apply() needs to redo the correction from the raw sheet (aerial-built, metres frame)
        rep["params"] = {"s": [float(ga["_s"].real), float(ga["_s"].imag)], "t": [float(ga["_t"].real), float(ga["_t"].imag)],
                         "m_per_px": m_px, "smooth": SMOOTH, "size": list(sheet.size)}
        if ga.get("_bendf") is not None:
            rep["params"]["cp"] = np.round(ga["_cp"], 2).tolist()
            rep["params"]["cd"] = [[round(float(z.real), 2), round(float(z.imag), 2)] for z in ga["_cd"]]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{sid}.{stem}.json").write_text(json.dumps(rep, indent=1))
    if best:
        name, g, r = best
        top = ink or sheet.convert("RGBA")
        panels = [overlay(g, top, sheet.size), overlay(g, warp(top, r, None, m_px), sheet.size)]
        if r.get("_bendf") is not None:
            panels.append(overlay(g, warp(top, r, r["_bendf"], m_px, r["_cp"]), sheet.size))
        w = 900
        ims = [p.resize((w, round(w * p.height / p.width))) for p in panels]
        sheet_im = Image.new("RGB", (w * len(ims) + 10 * (len(ims) - 1), ims[0].height), "white")
        for i, p in enumerate(ims):
            sheet_im.paste(p, (i * (w + 10), 0))
        sheet_im.save(OUT / f"{sid}.{stem}.check.jpg", quality=82)
    print(json.dumps(rep))
    return rep


def apply(sid, root=None):
    """Write each measured sheet's decision into the site's depictions.json as d["check"]; for shift/bend, bake the
    corrected sheet and ink into <stem>.fit.webp / <stem>.fit_ink.webp. Always rebuilt from the raw <stem>.webp
    (d["file"] never changes), so running it again, or after depict.py rebuilds a sheet, cannot double a move."""
    from scipy.interpolate import RBFInterpolator
    r = Path(root or ROOT)
    d0 = r / "web" / "data" / "sites" / sid
    dp = d0 / "depictions.json"
    if not dp.is_file():
        return
    deps = json.loads(dp.read_text())
    changed = False
    for d in deps.get("depictions", []):
        if d.get("kind") != "map":
            continue
        stem = d["file"].split(".")[0]
        rec = r / "data" / "sheetfit" / f"{sid}.{stem}.json"
        if not rec.is_file():
            continue
        rep = json.loads(rec.read_text())
        dec, prm = rep["decision"], rep.get("params") or {}
        use = dec["use"]
        chk = {"use": use, "why": dec["why"]}
        if use in ("shift", "bend") and prm:
            m_px = prm["m_per_px"]
            rigid = {"_s": complex(*prm["s"]), "_t": complex(*prm["t"])}
            bendf, cp = None, None
            if use == "bend" and prm.get("cp"):
                cp = np.array(prm["cp"])
                bendf = RBFInterpolator(cp, np.array(prm["cd"]), kernel="thin_plate_spline", smoothing=prm["smooth"])
            raw = Image.open(d0 / d["file"])
            if list(raw.size) != prm["size"]:   # the sheet was rebuilt at another size: the record no longer fits it
                chk = {"use": "unsure", "why": "sheet rebuilt since it was measured"}
            else:
                g = rep["grounds"]["aerial"]
                chk["moved_m"] = g["shift_m"]
                if bendf is not None:
                    chk["bent_m"] = g["bend"]["max_move_m"]
                chk["file"] = f"{stem}.fit.webp"
                warp(raw, rigid, bendf, m_px, cp).save(d0 / chk["file"], quality=82, method=4)
                ink = d0 / f"{stem}_ink.webp"
                if ink.is_file():
                    chk["ink"] = f"{stem}.fit_ink.webp"
                    warp(Image.open(ink), rigid, bendf, m_px, cp).save(d0 / chk["ink"], quality=85, method=4)
        if d.get("check") != chk:
            d["check"] = chk
            changed = True
    if changed:
        tmp = dp.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(deps, indent=1))
        os.replace(tmp, dp)


def every():
    """(site, sheet stem) for every survey sheet on every built site."""
    for dp in sorted((ROOT / "web" / "data" / "sites").glob("*/depictions.json")):
        for d in json.loads(dp.read_text()).get("depictions", []):
            if d.get("kind") == "map":
                yield dp.parent.name, d["file"].split(".")[0]


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--apply"]:   # --apply [site ...]: write decisions + corrected sheets into the sites
        for sid in args[1:] or sorted({p.name.split(".")[0] for p in OUT.glob("*.json")}):
            apply(sid)
        sys.exit(0)
    if args == ["--all"]:   # resumable sweep: one RoMa client, sheets already measured are skipped
        for sid, stem in every():
            if (OUT / f"{sid}.{stem}.json").is_file():
                continue
            try:
                run(sid, stem)
            except Exception as e:  # one bad site must not end the sweep
                print(json.dumps({"site": sid, "sheet": stem, "error": repr(e)}), flush=True)
        sys.exit(0)
    for i in range(0, len(args), 2):
        run(args[i], args[i + 1])
