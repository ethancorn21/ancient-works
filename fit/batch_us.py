"""The batch, US (task 203a, GOAL.md points 1-2): the 90 built US sites go through the fitting loop.

For every site in the given list (default: every region-"US" site of web/data/sites.json):
candidates are the web/data/plans.json rows whose `sites` contains the site; each candidate picture
goes  fitkit sheet (the picture's crop next to the site's ground, both gridded) -> the local vision
model (>= 4 matched-feature point pairs; 202's proposal is its starting point) ->
`pipeline.plan_fit.similarity` -> the fit gate (`pipeline.fit_gate`, the frozen rule of
docs/gate.md section 2). An accepted fit becomes a NEW automatic platefit document in
data/db/platefits/ (the page's existing format plus `"auto": true` and the gate's score); a
gate refusal or a picture the model could not fit becomes a review item in data/review/
(fit/review.py's upsert, 201's format, carrying the model's pairs); a site with no candidate at all
gets an item marked "no picture found". The 20 pre-batch hand-fit documents and the 19 hand-fit
site.json files are never touched (pinned by tests/golden/hand_fit_docs.sha256), and a candidate
that already has a document is skipped.

The model step is injectable: the working phase calls the local model on a fitkit-style sheet
(`--working`), tests and dry runs supply a fixed recorded answer (`--model-json`, or a callable
to `run_sites`), so no test touches the model server (GOAL: what the model says is a lead to
check, not a fact - the gate is the check, and the gate cannot see a consistent global error,
docs/gate.md section 7; the sheet, prompt and parse in `llm_model` are built with that in mind:
they ask the model to name its features and state the scale, and they route out-of-range or
self-contradictory answers to review instead of to an automatic document; a third counterweight
is the feature-presence check of `_feature_present`: the answer's ground points must sit on at
least half as textured ground as a typical region of the site's own image, or the answer is
trimmed to a review item. The check only routes to review - it never loosens the gate. It does
not see a fabrication anchored on strong ground texture (a road network, field boundaries);
docs/gate.md section 7's human 18/20 sample remains the backstop for that class).

This batch writes ONLY the document files and the review items, directly (aw's atomic JSON
convention). It never PUTs to the server: a PUT would wake the page-facing sync (overlays,
depictions, the drawings counts), which belongs to the one pass of task 212 after both batches.
203b (the rest of the world) imports `run_sites`/`write_report` and points them at its own
site list; it does not rewrite this loop.

usage:
  python3 fit/batch_us.py --golden            regenerate tests/golden/hand_fit_docs.sha256
  python3 fit/batch_us.py --working           full run over the 90 US sites (LLM on the fitkit sheet)
  python3 fit/batch_us.py --model-json F [--sites id ...]
                                              dry run: the model's answers come from F
  (the working run fetches missing pictures/aerials; everything else runs offline)
"""

import argparse
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The recorded seed of the automatically-accepted-fits sample in the report (20 where there are
# at least 20, for the human's 18/20 check, GOAL point 3): fixed so the sample is reproducible.
SEED = 20261010


def _now():
    return datetime.now(timezone.utc).isoformat()


def _save_json(path, obj):
    """Atomic JSON write, same convention as the doc store (indent=1, no trailing newline)."""
    path = Path(path)
    tmp = str(path) + "." + str(os.getpid()) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def _sites(root):
    d = json.loads((Path(root) / "web" / "data" / "sites.json").read_text())
    ss = d.get("sites") if isinstance(d, dict) else d
    return {s["id"]: s for s in ss if s.get("id")}


def us_sites(root):
    """The built US site ids (region "US" in web/data/sites.json), sorted."""
    return sorted(sid for sid, s in _sites(root).items() if s.get("region") == "US")


def _plans_rows(root):
    d = json.loads((Path(root) / "web" / "data" / "plans.json").read_text())
    cols = {c: i for i, c in enumerate(d["cols"])}
    return [{k: r[i] for k, i in cols.items()} for r in d["rows"]]


def candidates(site_id, rows):
    """The plans.json rows whose `sites` contains the site id, in file order."""
    return [r for r in rows if site_id in (r.get("sites") or [])]


def _doc_path(root, site_id, plan_id):
    return Path(root) / "data" / "db" / "platefits" / ("%s.%s.json" % (site_id, plan_id))


def pre_docs(root, site_id):
    """The (plan_id, doc) pairs of data/db/platefits/<site>.* documents that already exist."""
    out = []
    d = Path(root) / "data" / "db" / "platefits"
    if not d.is_dir():
        return out
    for p in sorted(d.iterdir()):
        if p.suffix == ".json" and p.name.startswith(site_id + "."):
            doc = json.loads(p.read_text())
            out.append((doc.get("plan") or p.name[len(site_id) + 1:-5], doc))
    return out


def is_pre_fit(root, site_id):
    """A pre-existing fit for the site: a platefits doc, or the old-style site.json plate fit."""
    if pre_docs(root, site_id):
        return True
    p = Path(root) / "data" / "sites" / site_id / "site.json"
    if p.is_file():
        try:
            return bool(((json.loads(p.read_text()).get("plate") or {}).get("fit")))
        except ValueError:
            pass
    return False


def gate_placement(pairs, transform=None):
    """The 001 adapter: score a placement against its recorded anchors with the frozen gate.

    -> (accepted, score, why). `pairs` are rows [u, v, lon, lat] (plate px -> ground); `transform`
    is the claimed placement (a, b) or None (solve it, as plan_fit.similarity does). `score` is
    the gate's median residual in ground metres (NaN when degenerate); `why` names the clause that
    refused (docs/gate.md section 2) or None when accepted.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
    import fit_gate

    verdict, stats = fit_gate.gate(pairs, transform)
    if verdict == fit_gate.ACCEPT:
        return True, round(float(stats["med"]), 1), None
    n, med, slope, io = stats["n"], stats["med"], stats["slope_o"], stats["io"]
    rho2 = _rho2(pairs, transform)
    bad = lambda x: x != x  # NaN: it fails every >/< comparison, so the clauses must name it
    if n < fit_gate.N_MIN:
        why = "degenerate: %d anchors (< %d)" % (n, fit_gate.N_MIN)
    elif bad(rho2) or rho2 < fit_gate.RHO2_MIN:
        why = "degenerate: no radial spread (sum rho^2 < 1 m^2)"
    elif bad(med) or med > fit_gate.MED_MAX:
        why = "median residual %s m > %s m" % (med, fit_gate.MED_MAX)
    elif bad(slope) or slope > fit_gate.SLOPE_MAX:
        why = "radial gradient: slope_o %s > %s" % (slope, fit_gate.SLOPE_MAX)
    else:
        why = "radial gradient: slope_o %s > %s and io %s < %s" % (
            slope, fit_gate.SLOPE_PATTERN, io, fit_gate.IO_MIN)
    return False, (None if bad(med) else round(float(med), 1)), why


def _rho2(pairs, transform):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
    import numpy as np
    import fit_gate
    _, rho = fit_gate.score(pairs, transform)  # already in ground metres (placement scales by k)
    return float(np.sum(rho ** 2)) if np.all(np.isfinite(rho)) else float("nan")


def _crop_px(row):
    """The doc's crop in page px: the row's map_box (fractions of the page) scaled to its size
    frame, clamped to a real box, else the full frame."""
    size = row.get("size") or [0, 0]
    w, h = size
    box = row.get("map_box")
    if not box or w < 2 or h < 2:
        return [0, 0, int(w), int(h)]
    x0, y0, x1, y1 = [int(round(f * (w if i % 2 == 0 else h))) for i, f in enumerate(box)]
    if x1 - x0 < 2 or y1 - y0 < 2:
        return [0, 0, int(w), int(h)]
    return [x0, y0, x1, y1]


def _norm_pairs(pairs):
    """The platefit convention: page px -> lon/lat, 1 dp px / 7 dp lon-lat."""
    return [[round(float(u), 1), round(float(v), 1), round(float(lon), 7), round(float(lat), 7)]
            for u, v, lon, lat in pairs]


def write_doc(root, site_id, row, pairs, score, at=None):
    """Write the automatic platefit document for one accepted fit; returns the path, or None when
    the document already exists (the batch adds files, it rewrites none - a pre-existing doc, hand
    or automatic, is never touched)."""
    path = _doc_path(root, site_id, row["id"])
    if path.exists():
        return None
    doc = {
        "site": site_id,
        "plan": row["id"],
        "crop": _crop_px(row),
        "pairs": _norm_pairs(pairs),
        "label": row.get("label") or None,
        "title": row.get("title") or None,
        "cite": row.get("cite") or None,
        "at": at or _now(),
        "auto": True,
        "score": score,
    }
    if row.get("ia"):
        doc.update({"ia": row["ia"], "file": row["file"], "book": row.get("book")})
    else:  # a commons picture: the page's own keys for that kind (pipeline/plan_fit.py)
        doc.update({"ia": None, "file": None, "model": "similarity", "src": "commons",
                    "url": row.get("url"), "ref": row.get("ref"), "size": row.get("size")})
    path.parent.mkdir(parents=True, exist_ok=True)
    _save_json(path, doc)
    return str(path)


def _entry(root, row, pairs, why, score, proposal):
    """A review-item candidate (201's format, data/review/README.md): the picture, the 200 evidence
    field when present, the pairs the human starts from (the model's when it made any, else 202's
    proposed starting point), and what the batch learned about this picture."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fit"))
    import review
    e = {
        "plan": row["id"],
        "title": row.get("title") or row.get("label") or "",
        "url": row.get("url") if row.get("url") else
               ("books/%s/%s" % (row["ia"], row["file"]) if row.get("ia") else None),
    }
    ev = review.candidate_evidence(row["id"], root)
    if ev is not None:
        e["evidence"] = ev
    if pairs:
        e["pairs"] = _norm_pairs(pairs)
    else:
        e["pairs"] = []
    if proposal:
        for k in ("coarse", "ground", "scale_m_px", "rot_deg", "scale_source", "note"):
            if proposal.get(k) is not None:
                e[k] = proposal[k]
    else:
        e["coarse"] = True
    e["why"] = why
    if score is not None:
        e["gate_score"] = score
    return e


def write_item(root, site_id, entries, no_picture=None):
    """Upsert the site's review item (201's writer; one item per site, resolved never cleared)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fit"))
    import review
    return review.upsert_item(root, site_id, entries, no_picture=no_picture)


def run_sites(root, site_ids, model=None):
    """The loop 203b points at its own site list.

    `model` is callable(site, row, proposal) -> None | {"pairs": [[u, v, lon, lat], ...], "note": str}
    in the row's `size` frame (the working LLM step or a recorded answer); None skips the model
    (every candidate then goes to the review item). Per site it returns a record:

      {"site", "pre_fit" (a doc or site.json plate fit already existed), "pre_docs",
       "auto" (docs written this run), "item" (a review item was written), "no_picture",
       "detail" {plan: {"outcome": "auto"|"reject"|"could-not-fit"|"skip", "score", "why"}}}

    A site ends covered when it has a fit (pre-existing or new) or a review item: GOAL point 1.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fit"))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
    import propose
    import plan_fit
    sites = _sites(root)
    rows = _plans_rows(root)
    records = {}
    for sid in sorted(set(site_ids)):
        site = sites.get(sid)
        if site is None:
            records[sid] = {"site": sid, "pre_fit": False, "pre_docs": [], "auto": [],
                            "item": False, "no_picture": False, "detail": {},
                            "error": "not in web/data/sites.json"}
            continue
        rec = {"site": sid, "pre_fit": is_pre_fit(root, sid),
               "pre_docs": [p for p, _ in pre_docs(root, sid)], "auto": [], "item": False,
               "no_picture": False, "detail": {}}
        have = set(rec["pre_docs"])
        cands = candidates(sid, rows)
        entries = []
        for row in cands:
            if row["id"] in have:
                rec["detail"][row["id"]] = {"outcome": "skip"}
                continue
            prop = None
            try:
                prop = propose.propose_for(sid, row["id"])
            except (ValueError, KeyError) as e:
                prop = None
            ans = model(site, row, prop) if model else None
            pairs = (ans or {}).get("pairs") or []
            note = (ans or {}).get("note")
            if len(pairs) >= 4:
                a, b, _, _ = plan_fit.similarity(pairs)
                accepted, score, why = gate_placement(pairs, (a, b))
                if accepted:
                    if write_doc(root, sid, row, pairs, score) is None:
                        rec["detail"][row["id"]] = {"outcome": "skip"}
                        have.add(row["id"])
                    else:
                        rec["auto"].append(row["id"])
                        rec["detail"][row["id"]] = {"outcome": "auto", "score": score}
                    continue
                rec["detail"][row["id"]] = {"outcome": "reject", "score": score, "why": why}
                entries.append(_entry(root, row, pairs, why, score, prop))
            else:
                why = note or ("model could not fit: %d of 4 pairs" % len(pairs)
                               if ans is not None else "no model answer")
                rec["detail"][row["id"]] = {"outcome": "could-not-fit", "why": why}
                entries.append(_entry(root, row, pairs, why, None, prop))
        if entries:
            write_item(root, sid, entries)
            rec["item"] = True
        elif not cands and not rec["pre_fit"]:
            write_item(root, sid, [], no_picture={"searched":
                          "web/data/plans.json (%d rows, matched by the sites field)" % len(rows),
                          "at": _now()})
            rec["no_picture"] = True
            rec["item"] = True
        records[sid] = rec
    return records


def classify(records):
    """The site-level counts of the report: every site in exactly one bucket.

    "automatic fit" (a new doc), else "already hand-fitted" (a pre-existing fit), else
    "review item" (a candidate the model could not pass the gate), else "no picture found".
    """
    out = {"automatic fit": [], "already hand-fitted": [], "review item": [],
           "no picture found": [], "error": []}
    for sid, r in records.items():
        if r.get("error"):
            out["error"].append(sid)
        elif r["auto"]:
            out["automatic fit"].append(sid)
        elif r["pre_fit"]:
            out["already hand-fitted"].append(sid)
        elif r.get("no_picture"):
            out["no picture found"].append(sid)
        elif r["item"]:
            out["review item"].append(sid)
        else:
            out["error"].append(sid)  # has candidates, nothing written, no pre-fit: report it
    return {k: sorted(v) for k, v in out.items()}


def _page_url(sid):
    return "#%s" % sid


def _sample(records):
    """The seeded sample of automatically accepted fits: 20 where there are at least 20, else all."""
    auto = sorted("%s.%s" % (r["site"], plan) for r in records.values() for plan in r["auto"])
    k = min(20, len(auto))
    if k == 0:
        return []
    return random.Random(SEED).sample(auto, k)


def write_report(root, records, title="The batch, US (203a)", path=None, at=None):
    """docs/batch_us.md: the counts, the recorded seed, the per-candidate table, and the seeded
    sample of automatically accepted fits (a page URL each) for the human's 18/20 check.
    Deterministic for the same records/seed (`at` only appears when given)."""
    counts = classify(records)
    n_sites = len(records)
    n_items = sum(1 for r in records.values() if r.get("item"))
    lines = ["# %s" % title, ""]
    lines.append("Sites run: %d. %s" % (n_sites,
                "Every site ends with a fit or an open review item." if not counts["error"]
                else "%d site(s) need attention below." % len(counts["error"])))
    lines.append("")
    lines.append("## Counts (one bucket per site; a hand-fitted site can also get an item for its other pictures)")
    lines.append("")
    for k in ("automatic fit", "review item", "already hand-fitted", "no picture found"):
        lines.append("- %s: %d" % (k, len(counts[k])))
    if counts["error"]:
        lines.append("- error (no outcome): %d" % len(counts["error"]))
    lines.append("- review items written: %d (one per site with a candidate that did not become a fit)" % n_items)
    lines.append("")
    lines.append("Seed: %d (the sample below is reproducible from it)" % SEED)
    lines.append("")
    lines.append("## Sample of automatically accepted fits (for the human's 18/20 check)")
    lines.append("")
    lines.append("| doc | page | gate med (m) |")
    lines.append("|---|---|---|")
    scores, docsites = {}, {}
    for r in records.values():
        for plan in r["auto"]:
            doc = "%s.%s" % (r["site"], plan)
            scores[doc] = (r["detail"].get(plan) or {}).get("score")
            docsites[doc] = r["site"]
    if _sample(records):
        for doc in _sample(records):
            lines.append("| %s | %s | %s |" % (doc, _page_url(docsites[doc]),
                                               scores.get(doc)))
    else:
        lines.append("| (none) | | |")
    lines.append("")
    lines.append("## Per candidate")
    lines.append("")
    lines.append("| site | plan | outcome | gate med (m) | why |")
    lines.append("|---|---|---|---|---|")
    for sid in sorted(records):
        r = records[sid]
        if r.get("error"):
            lines.append("| %s | - | %s | | |" % (sid, r["error"]))
            continue
        for plan in sorted(r["detail"]):
            d = r["detail"][plan]
            lines.append("| %s | %s | %s | %s | %s |" % (
                sid, plan, d["outcome"],
                d.get("score") if d.get("score") is not None else "",
                d.get("why") or ""))
        if not r["detail"]:
            lines.append("| %s | - | %s | | |" % (sid,
                           "no-picture" if r.get("no_picture") else "no candidate changed"))
    lines.append("")
    out = Path(root) / (path or "docs/batch_us.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    return str(out)


def write_golden(root):
    """Regenerate tests/golden/hand_fit_docs.sha256 (box 1): every NON-automatic platefit doc (the
    hand fits: automatic documents are the batch's own output and never part of the golden state)
    plus the 19 hand-fit sites' data/sites/<id>/site.json files, as sha256sum -c lines."""
    paths = []
    d = Path(root) / "data" / "db" / "platefits"
    if d.is_dir():
        for p in sorted(d.iterdir()):
            if p.suffix != ".json":
                continue
            doc = json.loads(p.read_text())
            if doc.get("auto"):
                continue
            paths.append(str(p.relative_to(root)))
    for line in (Path(root) / "tests" / "golden" / "hand_fit_sites.txt").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            paths.append("data/sites/%s/site.json" % line)
    paths = sorted(paths)
    out = Path(root) / "tests" / "golden" / "hand_fit_docs.sha256"
    with open(out, "w") as f:
        for p in paths:
            f.write("%s  %s\n" % (hashlib.sha256((Path(root) / p).read_bytes()).hexdigest(), p))
    return str(out)


def _font():
    """Grid-label font: a real 22 px typeface. fitkit's own grid uses PIL's default bitmap
    font, which is illegible to a 27 B vision model once the sheet is downscaled for the API
    call (pilot 2026-10-11: the model then fabricated internally perfect patterns that
    passed the gate, docs/gate.md section 7)."""
    from PIL import ImageFont
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except OSError:
        return ImageFont.load_default()


def _step(scale):
    """Grid line step in source px: the first of 100/200/500/1000 that lands at least 90 sheet
    px apart, so a 900 px panel carries at most ~10 lines its labels do not crowd."""
    for s in (100, 200, 500, 1000):
        if s * scale >= 90:
            return s
    return 1000


def _grid(im, x0, y0, scale, step, color, font):
    """fitkit's grid, with the label at BOTH ends of every line: the model reads a coordinate
    off whichever end is closer to its feature, and two ends cross-check each other."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    W, H = im.size
    def wh(s):
        b = d.textbbox((0, 0), s, font=font)
        return b[2] - b[0], b[3] - b[1]
    v = (x0 // step + 1) * step
    while (v - x0) * scale < W:
        x = (v - x0) * scale
        d.line([(x, 0), (x, H)], fill=color, width=1)
        d.text((x + 2, 2), str(v), fill=color, font=font)
        _, th = wh(str(v))
        d.text((x + 2, H - th - 2), str(v), fill=color, font=font)
        v += step
    v = (y0 // step + 1) * step
    while (v - y0) * scale < H:
        y = (v - y0) * scale
        d.line([(0, y), (W, y)], fill=color, width=1)
        d.text((2, y + 2), str(v), fill=color, font=font)
        tw, _ = wh(str(v))
        d.text((W - tw - 2, y + 2), str(v), fill=color, font=font)
        v += step
    return im


def _sheet(site, row, box):
    """The fit sheet for the model: the picture's crop and the site's ground as two 900 px
    panels (fitkit's sources: the plan image, the relief or the aerial), each gridded in bold
    with its own labels at both ends of every line. Saves fitkit.OUT/fit_<site>_<plan>.jpg
    (the same name fitkit.sheet uses) -> (path, ground_size, ground_m), ground_m being the
    ground box's Mercator x-span in metres, what the right panel's labels cover."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
    import fitkit
    import aw
    from PIL import Image
    x0, y0, x1, y1 = box
    c = fitkit.plan_image(row).crop(box)
    sc = 900.0 / max(c.size)
    c = c.resize((round(c.width * sc), round(c.height * sc)), Image.LANCZOS)
    _grid(c, x0, y0, sc, _step(sc), (0, 0, 200), _font())
    gpath = fitkit.ground(site["id"])
    gsz = Image.open(gpath).size
    g = fitkit.ground_view(site["id"], Image.open(gpath))
    rs = 900.0 / max(g.size)
    g = g.resize((round(g.width * rs), round(g.height * rs)), Image.LANCZOS)
    _grid(g, 0, 0, rs, _step(rs), (200, 0, 0), _font())
    S = Image.new("RGB", (c.width + g.width + 10, max(c.height, g.height)), "white")
    S.paste(c, (0, 0))
    S.paste(g, (c.width + 10, 0))
    path = os.path.join(fitkit.OUT, "fit_%s_%s.jpg" % (site["id"], row["id"]))
    S.save(path, quality=85)
    (lon0, lat1), (lon1, _), (_, lat0) = site["corners"][0], site["corners"][1], site["corners"][2]
    xm0, _ = aw.to_merc(lon0, lat1)
    xm1, _ = aw.to_merc(lon1, lat0)
    return path, gsz, (xm1 - xm0)


def _model_prompt(site, row, box, gsz, gbox, kind, proposal):
    """The prompt that keeps the model honest: the labelled coordinate ranges of both panels
    (the parser enforces them), their metre coverage, the 202 seed's scale window, and the
    anti-fabrication clauses (no grid intersections / even spacing / collinear points; never
    pad a short list). The answer names each matched feature and states the panel's scale, so
    both can be checked against its own pairs."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gw, gh = gsz
    p = proposal or {}
    scale = p.get("scale_m_px")
    cover = (" covering about %d x %d metres" % (round(w * scale), round(h * scale))
             if isinstance(scale, (int, float)) and not isinstance(scale, bool) and scale > 0
             else "")
    hint = ("The proposed starting placement maps the panel onto the site at scale %s m/px and "
            "rotation %s deg (coarse=%s); a true match should be within about 50%% of that scale. "
            % (scale, p.get("rot_deg"), p.get("coarse")) if scale is not None else "")
    return (
        "Left panel: a crop of an old map/plan of %s. Its grid labels run %d-%d across and %d-%d down "
        "(a %dx%d px crop%s). Right panel: the ground there today (%s); its grid labels run 0-%d across "
        "and 0-%d down (covering about %d x %d metres). %s"
        "Match 4 to 8 features that are the SAME real feature on both sides: wall or rampart corners, "
        "gate gaps, bastion or mound tips, road junctions, church footprints, river crossings, field edges. "
        "Every coordinate must lie inside its panel's labelled range above. Do NOT pick grid-line "
        "intersections, evenly spaced points or points along a straight line: real features have "
        "irregular spacing, so the gaps between your pairs must vary, and at least three of your points "
        "must not lie on one straight line. If you cannot confidently identify 4 real matched features, "
        "answer with only the pairs you truly see (even 0 or 1) - never pad a list with guessed or "
        "evenly spaced points. "
        "Answer with JSON only: {\"scale_m_px\": <your estimate of the left panel's metres per pixel>, "
        "\"features\": [\"one short name per pair, in order\"], "
        "\"pairs\": [[u_plan, v_plan, u_ground, v_ground], ...]}"
        % (site.get("name") or site["id"], x0, x1, y0, y1, w, h, cover, kind,
           gw, gh, round(gbox), round(gbox), hint))


def _parse_answer(ans, box, gsz, site):
    """The model's answer -> (pairs, feature names). Pairs whose plan point leaves the crop's
    labelled range or whose ground point leaves the ground image are dropped: the grid labels
    are the contract, and a coordinate outside them was guessed, not read."""
    x0, y0, x1, y1 = box
    gw, gh = gsz
    names = (ans or {}).get("features") or []
    pairs, feats = [], []
    for i, p in enumerate((ans or {}).get("pairs") or []):
        try:
            u, v, ug, vg = float(p[0]), float(p[1]), float(p[2]), float(p[3])
        except (TypeError, ValueError, IndexError):
            continue
        if not (x0 <= u <= x1 and y0 <= v <= y1 and 0 <= ug <= gw and 0 <= vg <= gh):
            continue
        lon, lat = _ground_lonlat(site, ug, vg, gsz)
        pairs.append([u, v, lon, lat])
        feats.append(str(names[i]) if i < len(names) and names[i] is not None else "")
    return pairs, feats


def _feature_present(site, pts_ll, gpath):
    """The third batch-side counterweight (routing only; the gate stays frozen): a
    feature-presence check on the site's own ground image. The 4c pilot found the fabrication
    the other two checks all pass - a correct-scale, wrong-translation answer whose points sit
    on structureless ground (docs/gate.md section 7): no consistency check can see it, but the
    ground image can. Each of the answer's ground points (`pts_ll`, lon/lat) is scored by the
    std of a 24 m box (R=12 px at the 1 m/px ground image) centred on it, and the answer
    passes only if at least half its points score at or above the median of a 400-point null
    sampled from the same image (fixed seed 20261011, distinct from the report's SEED 20261010).
    Calibrated on all 20 hand fits + the pilot answers: it over-refuses only genuinely faint
    features (serpent 0/3, mayburgh 1/3, little-solsbury 2/5) - a deliberate strict-gate cost,
    since the pairs still ride to the review item as a lead. A fabrication anchored on strong
    texture (roads, field boundaries) passes this check; section 7's human sample is the
    backstop for that class. -> (ok, frac); any read failure -> (True, None): no evidence never
    blocks a fit - the gate and the human are still downstream."""
    R = 12  # a 24 m box at the 1 m/px ground image
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
        import aw
        import numpy as np
        from PIL import Image
        a = np.asarray(Image.open(gpath).convert("L"), dtype=np.float64) / 255.0
        H, W = a.shape
        (lon0, lat1), (lon1, _), (_, lat0) = site["corners"][0], site["corners"][1], site["corners"][2]
        x0, y1 = aw.to_merc(lon0, lat1)
        x1, y0 = aw.to_merc(lon1, lat0)
        def boxstd(cx, cy):
            cx = min(max(cx, R), W - R - 1)
            cy = min(max(cy, R), H - R - 1)
            b = a[max(0, cy - R):cy + R + 1, max(0, cx - R):cx + R + 1]
            return float(b.std())
        rng = np.random.default_rng(20261011)  # the null's seed: distinct from the report's SEED
        null = np.array([boxstd(int(rng.integers(0, W)), int(rng.integers(0, H)))
                         for _ in range(400)])
        med = float(np.median(null))
        ps = []
        for (lon, lat) in pts_ll:  # the inverse of _ground_lonlat through the site corners
            x, y = aw.to_merc(lon, lat)
            ps.append(boxstd(int((x - x0) / (x1 - x0) * W), int((y1 - y) / (y1 - y0) * H)))
        if not ps:
            return True, None
        frac = float(sum(1 for s in ps if s >= med) / len(ps))
        return frac >= 0.5, frac
    except Exception:
        return True, None  # no evidence never blocks a fit


def llm_model(root):
    """The working-phase model: each candidate's fit sheet (its crop next to the site's ground,
    both gridded bold, _sheet) to the local vision model (pipeline/llm.py). The model reads
    the grid labels, names the features it matched, states the panel's scale, and records the
    pairs in the row's size frame. The pilots (4a, 4c) showed this model fabricates internally
    perfect regular patterns (identity maps, corner-to-corner, diagonal ladders) and, worst of
    all, a correct-scale wrong-translation answer on structureless ground that a
    consistency-only gate accepts, docs/gate.md section 7 - so the answer is checked before
    the gate is ever asked: out-of-range points are dropped (_parse_answer); a stated scale
    that disagrees by 2x or more with the magnitude of its own points' similarity (the scale
    cross-check), and an answer whose ground points mostly sit on less textured ground than a
    typical region of the site (_feature_present), each trim it to 3 pairs, which routes the
    picture to the review item instead of an automatic document (over-refusing genuinely faint
    features is the deliberate cost of a strict gate: the pairs still ride to the item as a
    lead). Requires the picture locally (fetched earlier in the working phase) and the AI-box
    tunnel; a missing picture or a failed call is reported in the item, never raised."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
    import fitkit
    import llm
    import plan_fit

    def model(site, row, proposal):
        if not row.get("size"):
            return {"note": "no image size recorded"}
        box = _crop_px(row)
        try:
            sheet, gsz, gbox = _sheet(site, row, box)
            kind = ("LiDAR relief shading" if fitkit.ground(site["id"]).endswith("relief.jpg")
                    else "aerial photograph")
        except Exception as e:
            return {"note": "picture not available for the sheet: %s" % e}
        try:
            ans = llm.ask_json(_model_prompt(site, row, box, gsz, gbox, kind, proposal),
                               images=[sheet])
        except Exception as e:
            return {"note": "model call failed: %s" % e}
        if isinstance(ans, dict) and ans.get("_unparsed"):
            return {"note": "model answer not parseable: %s" % str(ans["_unparsed"])[:120]}
        pairs, feats = _parse_answer(ans, box, gsz, site)
        if not pairs:
            return {"note": "the model recorded no usable pairs"}
        note = ("features: " + ", ".join(f for f in feats if f)) if any(feats) else None
        stated = ans.get("scale_m_px") if isinstance(ans, dict) else None
        if (len(pairs) >= 3 and isinstance(stated, (int, float))
                and not isinstance(stated, bool) and stated > 0):
            a, _, _, k = plan_fit.similarity(pairs[:min(8, len(pairs))])
            implied = abs(a) * k  # a is complex (scale + rotation): its magnitude is the scale
            if implied == implied and implied > 0 and max(implied / stated, stated / implied) > 2.0:
                note = ((note + "; ") if note else "") + (
                    "stated scale %.3f disagrees with its own points (%.3f m/px): not trusted"
                    % (stated, implied))
                pairs, feats = pairs[:3], feats[:3]  # <4: run_sites routes it to the item
        if len(pairs) >= 4:
            ok, frac = _feature_present(site, [(p[2], p[3]) for p in pairs],
                                        fitkit.ground(site["id"]))
            if not ok:
                note = ((note + "; ") if note else "") + (
                    "only %d%% of the recorded points sit on more textured ground than a typical "
                    "region of this site: the features are not visible where claimed - not trusted"
                    % round(frac * 100))
                pairs, feats = pairs[:3], feats[:3]  # <4: run_sites routes it to the item
        return {"pairs": pairs, "note": note}

    return model


def _ground_lonlat(site, col, row, size):
    """Ground image px -> lon/lat through the site's corners (fitkit.lonlat's formula)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
    import aw
    (lon0, lat1), (lon1, _), (_, lat0) = site["corners"][0], site["corners"][1], site["corners"][2]
    x0, y1 = aw.to_merc(lon0, lat1)
    x1, y0 = aw.to_merc(lon1, lat0)
    W, H = size
    return aw.to_lonlat(x0 + (col + 0.5) / W * (x1 - x0), y1 - (row + 0.5) / H * (y1 - y0))


def recorded_model(answers):
    """A model whose answers come from a fixed recorded file:
    {"<site id>": {"<plan id>": {"pairs": [[u, v, lon, lat], ...], "note": ...}}}.
    The test's fixed answers (and dry runs) use it: no network, no model server."""
    def model(site, row, proposal):
        rec = (answers.get(site["id"]) or {}).get(row["id"])
        if rec is None:
            return None
        return dict(rec)
    return model


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(ROOT), help="the project root (default: this checkout)")
    ap.add_argument("--golden", action="store_true",
                    help="regenerate tests/golden/hand_fit_docs.sha256 and exit")
    ap.add_argument("--sites", nargs="*", default=None,
                    help="site ids to run (default: all region-US sites)")
    ap.add_argument("--working", action="store_true",
                    help="the model is the local vision model on the fitkit sheet (network allowed)")
    ap.add_argument("--model-json", default=None,
                    help="recorded model answers (a dry run; no model server, no network)")
    ap.add_argument("--report", default=None, help="report path (default: docs/batch_us.md)")
    a = ap.parse_args(argv)
    if a.golden:
        print(write_golden(a.root))
        return 0
    if a.working:
        model = llm_model(a.root)
    elif a.model_json:
        model = recorded_model(json.loads(Path(a.model_json).read_text()))
    else:
        ap.error("a model is required: --working (the local vision model) or --model-json (recorded answers)")
    site_ids = a.sites or us_sites(a.root)
    records = run_sites(a.root, site_ids, model)
    report = write_report(a.root, records, path=a.report, at=_now())
    counts = classify(records)
    print("batch US: %d sites: %s" % (len(records),
          ", ".join("%d %s" % (len(v), k) for k, v in counts.items())))
    print("report:", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
