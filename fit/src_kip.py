"""Johannes Kip's (and Kip & Knyff's) bird's-eye views of UK country houses and their formal gardens
(task 205, GOAL.md point 4): the large scans in the Commons categories "Johannes Kip" (root + its
5 subcategories) and "Britannia Illustrata" - 132 distinct files, every one given a verdict in
INVENTORY. This module stages the fit-sized (long edge >= 1000 px) house/garden views into THIS
task's own staging files - one picture row per staged view (the files.jsonl shape + 200's
evidence field, kind caption_coords from the view's own caption, by "fit/src_kip.py"), one
hand classification (p_birdseye 1.0) and one new "garden" site row per view whose fixed landmark
(the house, the garden's axes, the park) can carry a fit - and 211 consolidates and builds.

The six views already hand-tied in pipeline/sources.py (KIP) are NOT re-staged: their evidence
kind stays "hand-tied QID". The Hampton Court trap applies to every candidate: the place is what
the CAPTION says (the Rijksmuseum's "Gezicht op Hampton Court" is in Herefordshire, not the
palace on the Thames). A view whose house is gone and nothing fixed remains on the ground is a
review-queue candidate recorded in docs/lead_kip.md (201 owns the queue), never a new site.
"Britannia Illustrata" (1707-09) and Kip's later plates (e.g. in Harris's History of Kent) are the
same kind of material: one row per picture, never per book.

usage: src_kip.py --list [--out FILE]   live (paced): list every file of the lead categories with
                                        its metadata; assert the live set and sizes against
                                        INVENTORY (an empty INVENTORY only lists - the first run
                                        builds it); JSON lines to FILE (stdout if omitted)
       src_kip.py --verify               live: re-verify every SITES QID against Wikidata
       src_kip.py [--dry]                stage the table rows into the staging files
       src_kip.py --check                offline (no network): join the staged files, run
                                        fit/evidence.py's check over every staged row
       src_kip.py --golden               write tests/golden/src_kip_sample.json

Staging writes only this task's files (append-only, idempotent on (site, title)). The system
python3 has no numpy (commons -> aw), so the live commands run under .venv/bin/python; the module
top stays stdlib-only (lazy imports, the fit/src_artists.py pattern).
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

EXTRAS_KIP = os.path.join(ROOT, "data", "catalog", "extras_kip.jsonl")
FILES_KIP = os.path.join(ROOT, "data", "commons", "files_kip.jsonl")
CLASSIFIED_KIP = os.path.join(ROOT, "data", "commons", "classified_kip.jsonl")
SITES_JSONL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
EXTRAS = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

# The lead categories (verified live 2026-10-10, one paced read-only run; list_files() re-checks the
# root's subcategory set every run so a re-filed or renamed category fails loud). Out of scope,
# checked and recorded in docs/lead_kip.md: Category:Jan Kip (5 files, all photos of the artist or
# a 1953 flood - no prints) and Category:History of Kent (29 files, all non-Kip).
CATS = ["Johannes Kip",
        "Britannia Illustrata",
        "Prints by Johannes Kip in the Rijksmuseum Amsterdam",
        "The Ancient and Present State of Glocestershire",
        "The history of nature, 1720",
        "Wilderness (garden history)"]

# Fit-sized = long edge >= 1000 px: the smallest staged view (Kingsweston) is 1375 px, the largest
# drop (the 982 px Fairlawne crop) is 63 px below the threshold, and nothing in the lead categories
# falls in 900-1000 px, so the cut needs no exception list (docs/lead_kip.md).
MIN_EDGE = 1000

# The verdicts: "staged" (a staging row goes into this task's files) / "hand-tied" (one of the six
# already in the canonical files - never re-staged) / "drop: <group>" (a documented drop, reason in
# docs/lead_kip.md). INVENTORY is (title, w, h, verdict, reason): the live list_files() run asserts
# the live set and the sizes against it, so a renamed, re-filed or replaced file fails loud.
INVENTORY = []  # filled by the first live run (session 1); every title of the lead categories, once

SITES = {}  # qid -> the verified site facts (id, name, landmark lon/lat, place, wikipedia, note); sessions 2-3


def now():
    return time.strftime("%Y-%m-%d")


def _commons():
    import commons  # lazy: commons -> aw needs numpy (absent from the system python3)
    return commons


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def list_files():
    """Live (paced): every file of the lead categories with its metadata, JSON lines to stdout.
    The root category's live subcategory set must equal CATS[1:] (drift fails loud); when INVENTORY
    is non-empty, the live title set and every (w, h) must equal it. Returns {title: (meta, cats)}."""
    c = _commons()
    subs = [s.split(":", 1)[1] for s in c.members(CATS[0], "subcat")]
    if sorted(subs) != sorted(CATS[1:]):
        raise SystemExit(f"subcategory drift: live {sorted(subs)} != {sorted(CATS[1:])}")
    by_cat = {}
    for cat in CATS:
        for t in c.members(cat, "file"):  # file members carry the "File:" prefix, unlike subcats
            by_cat.setdefault(t, []).append(cat)
    titles = sorted(by_cat)
    if INVENTORY:
        inv = {r[0]: r for r in INVENTORY}
        extra = [t for t in titles if t not in inv]
        gone = [t for t in inv if t not in by_cat]
        if extra or gone:
            raise SystemExit(f"INVENTORY drift: new files {extra}; vanished {gone}")
    meta = c.info(titles)
    for t in titles:
        m = meta.get(t) or {}
        if INVENTORY:
            _, w, h = next(r for r in INVENTORY if r[0] == t)
            if (m.get("w"), m.get("h")) != (w, h):
                raise SystemExit(f"size drift for {t}: live {(m.get('w'), m.get('h'))} != {(w, h)}")
        print(json.dumps({"title": t, "w": m.get("w"), "h": m.get("h"), "date": m.get("date"),
                          "cats": by_cat[t], "desc": m.get("desc")}, ensure_ascii=False))
    return {t: (meta.get(t) or {}, by_cat[t]) for t in titles}


def known_sites():
    """{qid: site id} over the built sites, the catalog and the extras (a source never makes a second site)."""
    out = {}
    for p in (SITES_JSONL, EXTRAS):
        for s in _load(p):
            if s.get("qid") and s["qid"] not in out:
                out[s["qid"]] = s["id"]
    for s in json.load(open(WEB_SITES, encoding="utf-8"))["sites"]:
        if s.get("qid") and s["qid"] not in out:
            out[s["qid"]] = s["id"]
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--list":
        out = a[a.index("--out") + 1] if "--out" in a else None
        if out:
            f = open(out, "w", encoding="utf-8")
            import contextlib
            with contextlib.redirect_stdout(f):
                list_files()
        else:
            list_files()
    else:
        raise SystemExit(__doc__.strip().split("usage:")[1].strip())
