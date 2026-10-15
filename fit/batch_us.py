"""The batch, US (task 203a, GOAL point 2): the 90 built US sites go through the fitting loop.

The vision model's fitting pass is retired (GOAL point 2, 2026-10-13: "the local Qwen models
never place a drawing and never write point pairs or coordinates"; the pass fabricated ~100
fits on 2026-10-11 - 301 - that 306a-f found nearly all wrong, and 212b deleted). The
pretrained matcher (fit/matchfit.py) is the only automatic fitter now: the one-site line
(tools/site_done.py) offers every uncovered picture to it first, and a fit it is sure of
becomes a matcher document. This batch does the remainder: every candidate picture without a
document gets a review item in data/review/ (fit/review.py's upsert, 201's format) whose
`why` is the matcher's recorded verdict for that picture - the judge's clause ("not sure:
8 consistent points (need 10)"), the gate's clause when the matcher's fit was gate-refused,
"picture not on this machine" - the per-candidate result 238 records, passed through the
line as `run_sites`'s `reasons`; a plan the matcher never saw (it was not reachable) is
recorded as "no matcher on this machine", a recorded environment fact, not a defect. 202's
proposal fields stay on the entry as the human's starting placement. A site with no
candidate at all gets an item marked "no picture found".

The 22 pre-batch hand-fit documents and the 19 hand-fit site.json files are never touched
(pinned by tests/golden/hand_fit_docs.sha256), and a candidate that already has a document
(hand or matcher) is skipped: the item upsert replaces a candidate's entry whole, so the
skip guard is the only thing protecting the audit notes.

`gate_placement` and `write_doc` stay in this module for the matcher: the frozen 001 gate
(`pipeline.fit_gate`, the frozen rule of docs/gate.md section 2) is the last word on every
automatic fit (its median residual is the document's score), and a matcher document is an
ordinary platefit document in data/db/platefits/ (the page's existing format plus
`"auto": true`, the gate's score and the provenance mark `"by": "agent"` - task 303: every
fit says who placed it). This batch writes ONLY the review items, directly (aw's atomic JSON
convention). It never PUTs to the server: a PUT would wake the page-facing sync (overlays,
depictions, the drawings counts), which belongs to the one pass of task 212.
203b (the rest of the world) imports `run_sites`/`write_report` and points them at its own
site list; it does not rewrite this loop.

usage:
  python3 fit/batch_us.py --golden            regenerate tests/golden/hand_fit_docs.sha256
  python3 fit/batch_us.py [--sites id ...]    offline: record a review item for every
  [--report PATH]                             uncovered candidate (the matcher belongs to
                                              the one-site line, not to this batch)
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
    the document already exists (the automatic fit store adds files, it rewrites none - a
    pre-existing doc, hand or automatic, is never touched). Called by the matcher (238), whose
    documents are by: agent, auto true."""
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
        "by": "agent",
    }
    if row.get("ia"):
        doc.update({"ia": row["ia"], "file": row["file"], "book": row.get("book")})
    else:  # a commons picture: the page's own keys for that kind (pipeline/plan_fit.py)
        doc.update({"ia": None, "file": None, "model": "similarity", "src": "commons",
                    "url": row.get("url"), "ref": row.get("ref"), "size": row.get("size")})
    path.parent.mkdir(parents=True, exist_ok=True)
    _save_json(path, doc)
    return str(path)


def _entry(root, row, why, proposal):
    """A review-item candidate (201's format, data/review/README.md): the picture, the 200 evidence
    field when present, 202's proposed starting placement, and what the matcher recorded about this
    picture. The retired batch records no pairs (the matcher's points ride in its own document) and
    no gate score (this batch calls no gate: the `why` already carries the clause when the
    matcher's fit was gate-refused)."""
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
    e["pairs"] = []
    if proposal:
        for k in ("coarse", "ground", "scale_m_px", "rot_deg", "scale_source", "note"):
            if proposal.get(k) is not None:
                e[k] = proposal[k]
    else:
        e["coarse"] = True
    e["why"] = why
    return e


def write_item(root, site_id, entries, no_picture=None):
    """Upsert the site's review item (201's writer; one item per site, resolved never cleared)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fit"))
    import review
    return review.upsert_item(root, site_id, entries, no_picture=no_picture)


def run_sites(root, site_ids, reasons=None):
    """The loop 203b points at its own site list.

    The vision model's fitting pass is retired (GOAL point 2): this writes no documents, calls
    no model and calls no gate. `reasons` is a {plan id: recorded reason} of the matcher's
    per-candidate verdicts (238's results, passed through the line): the judge's clause ("not
    sure: 8 consistent points (need 10)"), the gate's clause (the matcher's fit was
    gate-refused), or "picture not on this machine". A plan with no recorded reason (the
    matcher never saw it - it was not reachable) is recorded as "no matcher on this machine",
    a recorded environment fact, not a defect. Every uncovered candidate (no existing
    document) becomes a review-item entry whose `why` is that reason, with 202's proposal fields
    when a proposal exists; a candidate that already has a document (hand or matcher) is
    skipped, because the item upsert replaces a candidate's entry whole and the skip guard is
    the only thing protecting the audit notes. A site with no candidate at all and no
    pre-existing fit gets an item marked "no picture found". Per site it returns a record:

      {"site", "pre_fit" (a doc or site.json plate fit already existed), "pre_docs",
       "auto" (always empty: this batch writes no documents anymore), "item" (a review item
       was written), "no_picture",
       "detail" {plan: {"outcome": "skip"|"item", "why"}}}

    A site ends covered when it has a fit (pre-existing, or the matcher's, written by the
    line) or a review item: GOAL point 1.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fit"))
    import propose
    sites = _sites(root)
    rows = _plans_rows(root)
    reasons = reasons or {}
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
            why = reasons.get(row["id"]) or "no matcher on this machine"
            rec["detail"][row["id"]] = {"outcome": "item", "why": why}
            entries.append(_entry(root, row, why, prop))
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
    "review item" (a candidate the matcher could not fit), else "no picture found".
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
    """Regenerate tests/golden/hand_fit_docs.sha256 (box 1): every platefit doc the owner placed
    by hand (`"by": "hand"`, 303) - automatic documents are the batch's own output and never part
    of the golden state; an unmarked doc (auto or not) is not a hand fit either - plus the 19
    hand-fit sites' data/sites/<id>/site.json files, as sha256sum -c lines."""
    paths = []
    d = Path(root) / "data" / "db" / "platefits"
    if d.is_dir():
        for p in sorted(d.iterdir()):
            if p.suffix != ".json":
                continue
            doc = json.loads(p.read_text())
            if doc.get("by") != "hand":
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(ROOT), help="the project root (default: this checkout)")
    ap.add_argument("--golden", action="store_true",
                    help="regenerate tests/golden/hand_fit_docs.sha256 and exit")
    ap.add_argument("--sites", nargs="*", default=None,
                    help="site ids to run (default: all region-US sites)")
    ap.add_argument("--report", default=None, help="report path (default: docs/batch_us.md)")
    a = ap.parse_args(argv)
    if a.golden:
        print(write_golden(a.root))
        return 0
    site_ids = a.sites or us_sites(a.root)
    records = run_sites(a.root, site_ids)
    report = write_report(a.root, records, path=a.report, at=_now())
    counts = classify(records)
    print("batch US: %d sites: %s" % (len(records),
          ", ".join("%d %s" % (len(v), k) for k, v in counts.items())))
    print("report:", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
