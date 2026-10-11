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

The model step is injectable: the working phase calls the local model on the fitkit sheet
(`--working`), tests and dry runs supply a fixed recorded answer (`--model-json`, or a callable
to `run_sites`), so no test touches the model server (GOAL: what the model says is a lead to
check, not a fact - the gate is the check, and the gate cannot see a consistent global error,
docs/gate.md section 7).

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


def llm_model(root):
    """The working-phase model: the fitkit sheet of each candidate (its crop next to the site's
    ground, both gridded) to the local vision model (pipeline/llm.py), which reads the grid
    labels and records >= 4 matched features as pairs in the row's size frame. Requires the
    picture locally (fetched earlier in the working phase) and the AI-box tunnel; a missing
    picture or a failed call is reported in the item, never raised."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
    import fitkit
    import llm

    def model(site, row, proposal):
        if not row.get("size"):
            return {"note": "no image size recorded"}
        try:
            im = fitkit.plan_image(row)
        except Exception as e:
            return {"note": "picture not available for the sheet: %s" % e}
        from PIL import Image
        box = _crop_px(row)
        fitkit.sheet(site["id"], row["id"], box)
        g = fitkit.ground(site["id"])
        kind = "LiDAR relief shading" if g.endswith("relief.jpg") else "aerial photograph"
        gsz = Image.open(g).size
        hint = ""
        if proposal:
            hint = ("The proposed starting placement maps the panel onto the site centre at scale "
                    "%s m/px and rotation %s deg (coarse=%s)." % (
                        proposal.get("scale_m_px"), proposal.get("rot_deg"), proposal.get("coarse")))
        prompt = (
            "Left panel: a crop of an old map/plan of %s. Right panel: the ground there today (%s). "
            "Both panels are gridded; the grid labels are pixel coordinates in that panel's own image. "
            "Match at least 4 (up to 8) features that are the SAME feature on both sides: wall or rampart "
            "corners, gate gaps, bastion or mound tips, road junctions, church footprints, river crossings, "
            "field edges. Read each coordinate off the grid labels of its own panel. %s "
            "Answer with JSON only: {\"pairs\": [[u_plan, v_plan, u_ground, v_ground], ...]}"
            % (site.get("name") or site["id"], kind, hint))
        try:
            ans = llm.ask_json(prompt, images=[os.path.join(fitkit.OUT,
                                                           "fit_%s_%s.jpg" % (site["id"], row["id"]))])
        except Exception as e:
            return {"note": "model call failed: %s" % e}
        if isinstance(ans, dict) and ans.get("_unparsed"):
            return {"note": "model answer not parseable: %s" % str(ans["_unparsed"])[:120]}
        pairs = []
        for p in (ans or {}).get("pairs") or []:
            try:
                u, v, ug, vg = float(p[0]), float(p[1]), float(p[2]), float(p[3])
            except (TypeError, ValueError, IndexError):
                continue
            lon, lat = _ground_lonlat(site, ug, vg, gsz)
            pairs.append([u, v, lon, lat])
        if not pairs:
            return {"note": "the model recorded no usable pairs"}
        return {"pairs": pairs}

    return model  # noqa: fitkit.OUT (the sheet's directory) is read where it was set


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
