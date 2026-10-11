"""Finish one site, end to end: fit, sync to the map, the sites.json entry, the review queue (task 300).

usage: .venv/bin/python tools/site_done.py <site id> [--root DIR] [--working | --model-json FILE]

From now on the work goes one site at a time, all the way to the map (Ethan 2026-10-11). The line
uses only code that already exists:

  1. fit   fit/batch_us.py run_sites, but only for the site's candidate pictures that have NEITHER
           a platefit document NOR a review-item entry yet. Covered pictures are never re-fitted:
           the batch's item upsert replaces a candidate's entry whole, so a blind re-run would swap
           the rich entries (gate scores, pairs, the why) for "no model answer" stubs.
  2. sync  pipeline/plan_fit.py build for every one of the site's fit documents (the overlay on the
           map); a document whose overlay is already current is left as is.
  3. entry pipeline/build_site.py set_drawings: the site's drawing count in web/data/sites.json
           (the page colours its square by it).
  4. review fit/review.py export (scoped to this site: it publishes web/data/review.json over the
           whole queue but records resolution only into this site's item file).

Prints what it did per picture: synced to the map, sent to the review queue (with the why), or
skipped with the reason. --root redirects the DATA paths (the test runs it on a copy of one
site's files; the code stays this checkout's). Exit codes: 2 = the site is not built,
1 = a document failed to sync, 0 = done.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "fit"))
sys.path.insert(0, str(ROOT / "pipeline"))

import batch_us  # noqa: E402
import build_site  # noqa: E402
import plan_fit  # noqa: E402
import review  # noqa: E402


def _sites_list(index):
    return index.get("sites") if isinstance(index, dict) else index


def _site_built(root, sid):
    """(built, reason): the site has an entry in web/data/sites.json AND its web/data/sites/<id>/ dir."""
    r = Path(root)
    index_path = r / "web" / "data" / "sites.json"
    if not index_path.is_file():
        return False, "web/data/sites.json is missing"
    if not any(s.get("id") == sid for s in _sites_list(json.loads(index_path.read_text()))):
        return False, f"no entry for {sid} in web/data/sites.json (build it: pipeline/build_site.py)"
    if not (r / "web" / "data" / "sites" / sid).is_dir():
        return False, f"web/data/sites/{sid}/ is missing (build it: pipeline/build_site.py)"
    return True, None


def _fit(root, sid, model):
    """Fit the site's uncovered candidate pictures. Returns (docs, item_path, item, item_cands)."""
    rows = batch_us.candidates(sid, batch_us._plans_rows(str(root)))
    docs = dict(batch_us.pre_docs(str(root), sid))
    # review items are keyed by their `site` field, not the file name (data/review/README.md)
    item_path, item = review._find_item(str(root), sid)
    item_cands = {c.get("plan"): c for c in (item.get("candidates") or [])} if item else {}
    uncovered = [r for r in rows if r["id"] not in docs and r["id"] not in item_cands]
    need_fit = bool(uncovered) or (not rows and not batch_us.is_pre_fit(str(root), sid) and item is None)
    if need_fit:
        rec = batch_us.run_sites(str(root), [sid], model)[sid]
        if rec.get("error"):
            print("fit  " + rec["error"])
        rows_by_id = {r["id"]: r for r in rows}
        for plan, d in sorted(rec["detail"].items()):
            title = (rows_by_id.get(plan) or {}).get("title") or plan
            if d.get("outcome") == "auto":
                print(f"fit  {title}: fit written (doc {sid}.{plan}, gate {d.get('score')} m)")
            elif d.get("outcome") == "skip":
                print(f"fit  {title}: skipped: already fitted (doc {sid}.{plan})")
            else:  # reject / could-not-fit: the batch's upsert put it in the item
                print(f"fit  {title}: sent to the review queue ({d.get('why')})")
        if rec.get("no_picture"):
            print("fit  no picture found: the site's review item records that")
    else:
        if rows:
            n_doc = sum(1 for r in rows if r["id"] in docs)
            print(f"fit  {len(rows)} candidate picture(s): {n_doc} fitted (doc), "
                  f"{len(rows) - n_doc} in the review item -> no batch run needed")
        elif batch_us.is_pre_fit(str(root), sid):
            print("fit  already fitted (a fit document or plate fit existed) -> no batch run needed")
        else:
            print("fit  no candidate pictures and the review item already records that -> no batch run needed")
    # re-read after the run: new documents may exist and the item's entries may have changed
    docs = dict(batch_us.pre_docs(str(root), sid))
    item_path, item = review._find_item(str(root), sid)
    item_cands = {c.get("plan"): c for c in (item.get("candidates") or [])} if item else {}
    return docs, item_path, item, item_cands


def _sync(root, sid, docs):
    """Build the map overlay for each of the site's fit documents. Returns the number that failed."""
    failed = 0
    for plan, doc in sorted(docs.items()):
        title = doc.get("title") or plan
        if plan_fit.is_done(doc, f"{sid}.{plan}", root):
            print(f"sync {title}: skipped: overlay already current (at {doc.get('at')})")
            continue
        try:
            plan_fit.build(doc, root)
        except SystemExit as e:
            failed += 1
            print(f"sync {title}: FAILED: {e}")
        else:
            sc = f", gate {doc.get('score')} m" if doc.get("score") is not None else ""
            print(f"sync {title}: synced to the map (plan_{plan}.webp, {len(doc.get('pairs') or [])} pairs{sc})")
    return failed


def _entry(root, sid, before):
    """Refresh the site's drawing count in web/data/sites.json (the page colours its square by it).
    `before` was read before the sync: plan_fit.build already refreshes the count as it goes."""
    index_path = Path(root) / "web" / "data" / "sites.json"
    build_site.set_drawings(sid, root)
    after = next(s.get("drawings") for s in _sites_list(json.loads(index_path.read_text())) if s["id"] == sid)
    print(f"entry  web/data/sites.json: drawings {before} -> {after}")


def _review(root, sid, item_path, item, resolved):
    """Publish the open items to web/data/review.json (scoped: only this site's item file is written)."""
    if item is None:
        print("review no review item (every picture is a fit)")
        return
    n_open, n_total = review.export(str(root), site_id=sid)
    n = len(item.get("candidates") or [])
    state = f"resolved by {resolved}" if resolved else "open"
    print(f"review {Path(item_path).name}: {n} candidate(s), {state}; "
          f"page now has {n_open} open of {n_total} items")


def _summary(root, sid, docs, item, item_cands, resolved):
    """One line per candidate picture of the site: where it ended up."""
    rows = batch_us.candidates(sid, batch_us._plans_rows(str(root)))
    if not rows and item is None:
        print("pictures none: no candidate pictures in web/data/plans.json")
        return
    for row in sorted(rows, key=lambda r: r["id"]):
        pid, title = row["id"], row.get("title") or row.get("label") or pid
        if pid in docs:
            doc = docs[pid]
            sc = f", gate {doc.get('score')} m" if doc.get("score") is not None else ""
            print(f"  {title} ({pid}): synced to the map{sc}")
        elif pid in item_cands:
            cand = item_cands[pid]
            gate = cand.get("gate_score")
            why = (f"gate {gate} m - " if gate is not None else "") + (cand.get("why") or "no model answer")
            line = f"  {title} ({pid}): sent to the review queue ({why})"
            if resolved:
                line += f"; the item is resolved by {resolved}"
            print(line)
        else:
            print(f"  {title} ({pid}): no doc and no review item - the line left this picture uncovered")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Finish one site, end to end (fit, sync, entry, review).")
    ap.add_argument("site", help="the site id (web/data/sites.json)")
    ap.add_argument("--root", default=str(ROOT), help="the data root (default: this checkout)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--working", action="store_true",
                   help="unfitted pictures go to the local vision model (the batch's working phase)")
    g.add_argument("--model-json", default=None,
                   help="recorded model answers for unfitted pictures (a dry run; no model, no network)")
    a = ap.parse_args(argv)
    if a.working:
        model = batch_us.llm_model(a.root)
    elif a.model_json:
        model = batch_us.recorded_model(json.loads(Path(a.model_json).read_text()))
    else:
        model = None
        print('fit  no model given: unfitted pictures (if any) go to the review item as "no model answer"')
    built, why = _site_built(a.root, a.site)
    if not built:
        print(f"error: {a.site} is not built: {why}")
        return 2
    print(f"site {a.site}: the one-site line (fit -> sync -> entry -> review)")
    docs, item_path, item, item_cands = _fit(a.root, a.site, model)
    before = next(s.get("drawings") for s in _sites_list(
        json.loads((Path(a.root) / "web" / "data" / "sites.json").read_text())) if s["id"] == a.site)
    failed = _sync(a.root, a.site, docs)
    _entry(a.root, a.site, before)
    resolved = review.resolved_doc(item, str(a.root)) if item else None
    _review(a.root, a.site, item_path, item, resolved)
    _summary(a.root, a.site, docs, item, item_cands, resolved)
    if failed:
        print(f"done with {failed} document(s) that failed to sync")
        return 1
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
