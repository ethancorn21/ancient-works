"""Petrie, *Stonehenge, Avebury, and other Stone Age monuments of the British Isles* (E. Stanford for
Macmillan, 1880) - the Wiltshire leg of GOAL point 4 (task 209c): the book leg and the Commons leg.

The book is NOT on IA (verified 2026-10-13: title/description/identifier searches return 0; the only
1880 'stonehenge' item is an Oxfordshire Rollright pamphlet) and NOT on Commons as a book (Category:Books
by Flinders Petrie = 71 files, all his Egypt books); HathiTrust holds it (US public domain, full view)
and Google Books serves a PDF, but both refuse this VM (403/429 - the 209a finding). The only way the
copy could arrive was human-downloaded (the 207c-Roy local-copy pattern): ask_human 002 asked for it
(data/raw/books/petrie1880/, one image per leaf page) and was REFUSED (iteration 151, journal date
2026-10-13, the 001-Hoare pattern: "Just skip it and move on"), so the book leg is off the table for
good - no fetch wrap is built dormantly (209a's pre-dated its refusal).

The Commons leg is the designed fallback (a): the two unlabeled fit-sized files of the Flickr set
'Stonehenge- plans, descriptions and theories' are Petrie 1880 Pl. I and Pl. II (visually verified
2026-10-12 by 209b: the W.M.F.P. signature, the plate numbers, the scales 1:350 / 1:1500), and they are
ALREADY in the canonical data/commons/files.jsonl (stonehenge-q39671, year 1880, the caption_coords tie
from the British Library Georeferencer description - PETRIE, shelfmark HMNTS 10352.i.12, pp. 47/49,
E. Stanford 1880 - checked 2026-10-10). A title that is already canonical is never re-staged, so this
module stages nothing and keeps no book artifacts (no triage/lists files, no data/raw/books/petrie1880/):
it verifies the two canonical rows (and their machine classification rows) and pins them in the golden
sample. The rest of the book's plates (Avebury, Silbury Hill, the West Kennet long barrow, the other
Wiltshire earthworks) are not on Commons and are undelivered - recorded in docs/lead_wiltshire.md; if a
complete copy ever lands in data/raw/books/petrie1880/ (a library digitisation), the 209a-style
local-copy wrap (register + triage A/F/B + list transcription from the copy's own list pages + staging +
the stage-A/B recall) is added here then. The existing hand fits (Allcroft Avebury fig. 187, Allcroft
Windmill Hill fig. 186, in data/db/platefits/) are not re-staged or re-fitted: new rows only.

usage: src_wiltshire_petrie.py --check    offline (no network): verify the two canonical Petrie rows -
                                          the PETRIE_ROWS table match (site, QID, the book's year 1880,
                                          the live size, the caption_coords tie), the never-re-staged
                                          guard over the *_wiltshire_c staging files, the join (every
                                          staged row names a catalog or web-built site; classified rows
                                          1:1), and fit/evidence.py's check over both rows from stored
                                          fields alone
       src_wiltshire_petrie.py --golden   write tests/golden/src_wiltshire_petrie_sample.json (the two
                                          canonical file rows and their classified rows, normalized;
                                          regenerate only for an intended change)

The module top stays stdlib-only (fit/evidence.py needs numpy, run under .venv/bin/python).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES_C = os.path.join(ROOT, "data", "commons", "files_wiltshire_c.jsonl")
CLASSIFIED_C = os.path.join(ROOT, "data", "commons", "classified_wiltshire_c.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
CLASSIFIED_CANONICAL = os.path.join(ROOT, "data", "commons", "classified.jsonl")
SITES_JSONL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
GOLDEN = os.path.join(ROOT, "tests", "golden", "src_wiltshire_petrie_sample.json")

# (title, site, plate, w, h) - the two canonical rows, visually identified as Petrie 1880 by 209b
# (2026-10-12, docs/lead_wiltshire.md): Pl. I the stone-by-stone plan (scale 1:350, the sarsen/bluestone
# key Standing 1880 / Standing 1747 / Overthrown, the outlying-stone forms 91/93/95/96), Pl. II
# Stonehenge with the Avenue and the Cursus inset (scale 1:1500, "Petrie levels in inches by numbering
# of stones"). Both signed W.M.F.P. A title that drifts off the canonical file, or a (site, year, size)
# that moves, fails loud in check_staged().
PETRIE_ROWS = [
    ("File:47 of 'Stonehenge- plans, descriptions and theories' (11135894643).jpg",
     "stonehenge-q39671", "I", 2245, 2852),
    ("File:49 of 'Stonehenge- plans, descriptions and theories' (11133409654).jpg",
     "stonehenge-q39671", "II", 4641, 2874),
]

# The one site both plates show (the canonical rows tie to it). Cross-checked against the catalog at
# check time: a missing site, or a moved qid/lon/lat, fails loud.
SITES = {
    "stonehenge-q39671": dict(qid="Q39671", name="Stonehenge", lon=-1.826111, lat=51.178889),
}

YEAR = 1880


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def _catalog():
    """{id: site} over the catalog and the web build: a row may only tie to a site that exists."""
    out = {s["id"]: s for s in _load(SITES_JSONL)}
    for s in json.load(open(WEB_SITES, encoding="utf-8"))["sites"]:
        out.setdefault(s["id"], s)
    return out


def _canonical_rows():
    """The canonical file rows of the PETRIE_ROWS titles, in table order (a missing title fails loud)."""
    canonical = {r.get("title"): r for r in _load(FILES_CANONICAL) if r.get("title")}
    out = []
    for title, *_ in PETRIE_ROWS:
        r = canonical.get(title)
        if r is None:
            raise SystemExit(f"{title!r} no longer in the canonical files.jsonl (renamed on Commons?): "
                             f"the Commons leg is broken")
        out.append(r)
    return out


def check_staged():
    """Offline (no network): the Commons-leg verification. Per PETRIE_ROWS entry: the canonical row
    exists and matches the table (site, QID, the book's year, the live size), its stored evidence is
    the caption_coords tie, and fit/evidence.py's check passes it from stored fields alone. Guard:
    none of the Petrie titles is in a *_wiltshire_c staging file (a canonical title is a hard fail -
    never re-staged); when a staging file exists it joins (every row names a catalog or web-built
    site, (site, title) unique, classified rows 1:1). Returns the exit code (0 iff no problem and
    no FAIL)."""
    import evidence  # lazy: evidence -> commons -> aw needs numpy (absent from the system python3)
    cats = evidence.catalog_map()
    known = _catalog()
    canonical = {r.get("title"): r for r in _load(FILES_CANONICAL) if r.get("title")}
    petrie = {t for t, *_ in PETRIE_ROWS}
    staged_files = _load(FILES_C)
    staged_cls = _load(CLASSIFIED_C)
    problems = []
    n = len(PETRIE_ROWS)
    npass = nfail = nnone = 0
    for title, sid, plate, w, h in PETRIE_ROWS:
        r = canonical.get(title)
        if r is None:
            nfail += 1
            print(f"FAIL canonical        {sid}|{title}  no longer in files.jsonl")
            problems.append(f"{title!r} (Pl. {plate}) no longer in the canonical files.jsonl: the "
                            f"Commons leg is broken")
            continue
        s = SITES[sid]
        if (r.get("site"), r.get("qid"), r.get("year")) != (sid, s["qid"], YEAR):
            problems.append(f"{title!r}: the canonical row moved off the table (site {r.get('site')!r} "
                            f"qid {r.get('qid')!r} year {r.get('year')!r})")
        if (r.get("w"), r.get("h")) != (w, h):
            problems.append(f"{title!r}: size drift {(r.get('w'), r.get('h'))} != {(w, h)}")
        cat = known.get(r.get("site"))
        if cat is None:
            problems.append(f"{title!r}: site {r.get('site')!r} no longer in the catalog or the web build")
        elif (cat.get("qid"), cat.get("lon"), cat.get("lat")) != (s["qid"], s["lon"], s["lat"]):
            problems.append(f"catalog drift for {r.get('site')}: table {s['qid']} {s['lon']},{s['lat']} vs "
                            f"catalog {cat.get('qid')} {cat.get('lon')},{cat.get('lat')}")
        v, kind, reason = evidence.check_commons(r, cats)
        print(f"{v:4s} {kind:15s} {r.get('site')}|{r.get('title')}  (Pl. {plate}, {r.get('year')})"
              + (f"  {reason}" if reason else ""))
        if v == "PASS":
            npass += 1
        elif v == "NONE":
            nnone += 1
            problems.append(f"{title!r}: no tie ({reason})")
        else:
            nfail += 1
            problems.append(f"{title!r}: {v} ({reason})")
    # the never-re-staged guard + the join over the (possibly absent) *_wiltshire_c staging files
    for p in staged_files + staged_cls:
        if p.get("title") in petrie:
            problems.append(f"a *_wiltshire_c staging file re-stages the canonical Petrie title "
                            f"{p['title']!r}")
    seen = set()
    for r in staged_files:
        if not r.get("title"):
            continue
        if r.get("site") not in known:
            problems.append(f"file row names a site that is neither catalog nor web-built: "
                            f"{r['site']!r} ({r['title']!r})")
        k = (r.get("site"), r.get("title"))
        if k in seen:
            problems.append(f"duplicate staged row {k}")
        seen.add(k)
    if (staged_files or staged_cls) and \
            {(r.get("site"), r.get("title")) for r in staged_cls} != seen:
        problems.append("the classified rows are not 1:1 with the staged file rows")
    for p in problems:
        print("check:", p)
    print(f"evidence: {n} rows, {npass} pass, {nfail} fail, {nnone} no-tie")
    return 1 if problems else 0


def _norm(rows):
    """The rows for the golden file: "checked" normalized (it varies with the evidence re-record
    date - a re-record is an intended change, regenerated with --golden)."""
    out = []
    for r in rows:
        r = dict(r)
        ev = r.get("evidence")
        if isinstance(ev, dict) and ev.get("checked"):
            r["evidence"] = dict(ev, checked="0000-00-00")
        out.append(r)
    return out


def golden(path=None):
    """Write tests/golden/src_wiltshire_petrie_sample.json: the two canonical Petrie file rows and
    their machine-classified rows, normalized. Regenerate only for an intended change."""
    p = path or GOLDEN
    files = _canonical_rows()
    titles = {r["title"] for r in files}
    cls = [r for r in _load(CLASSIFIED_CANONICAL) if r.get("title") in titles]
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"files": _norm(files), "classified": cls}, f, ensure_ascii=False, indent=1,
                  sort_keys=True)
        f.write("\n")
    print("wrote", p)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] not in ("--check", "--golden"):
        raise SystemExit(__doc__.strip().split("usage:")[1].strip())
    if a and a[0] == "--check":
        raise SystemExit(check_staged())
    if a and a[0] == "--golden":
        golden()
    print(__doc__.strip().split("usage:")[1].strip())
