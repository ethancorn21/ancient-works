"""Batch 4 of the bird's-eye and panoramic views of US cities (task 240, part of 236; GOAL.md
point 5: artists' aerial and bird's-eye views count as much as surveys): FOUR more US cities, each
a new site of its own in this task's own staging files (one module + one staging file set per
batch, so 240 and 241 build in parallel) - staged from the Library of Congress "Panoramic Maps"
collection (about 1,500 US bird's-eye views, 1847-1929, public domain; this machine cannot reach
loc.gov, so the files are fetched from their Wikimedia Commons mirrors - the 236b route, its lead
doc docs/lead_us_birdseye.md): Denver (the 1908 Birdseye View Publishing Co. sheet, looking south
from the Twenty-Third Street Viaduct) first; St. Paul, Minneapolis, Cleveland follow in candidate
order. The 25-city total spans 236b's 16 + 240's four + 241's five; 236c consolidates every
staging set into the canonical data and checks the total.

This module is a COPY of fit/src_us_birdseye.py (236b's module) - the template it keeps in sync
with: the verify/stage/check/golden machinery, the 200 caption_coords evidence field, the Zwolle
date-swap rule, the never-two-sites-for-one-QID cross-check - extended here so known_sites() ALSO
reads 236a's extras_us_cities.jsonl, 236b's extras_us_birdseye.jsonl and 241's
extras_us_birdseye_batch5.jsonl (absent until 241 runs), so a QID can never sit on two sites. The
batch-4 copy stages NO shared (owner-named) cities: 236a's four owner cities are tied to their
236a site ids by 236b's module, which stages all of 236b's own views, so SHARED_SITES and its
machinery stay out of this copy (if research ever found a batch-4 city already held by an existing
site - expected for none - the fix is a small 236b-style shared table pointing at that site,
recorded in the lead doc). One row per city: the steepest (near-vertical), best-scanned
whole-city view of the collection (Public domain, >= 4000 px wide, the caption names the city).
Bird's-eye views are oblique, so the site's note records the staged view's apparent angle where
the fit order depends on it (near-vertical views fit best; the 2000 m town-box overshoots are
likely review items, the 236a NY-1811 / DC-ring precedent in docs/lead_us_cities.md).

usage: src_us_birdseye_batch4.py --verify     re-verify every table QID against Wikidata
                                   (label, every P625 value, P373, P131, enwiki, the first name-search hit
                                   with coordinates - what record --live would resolve); copy the output into
                                   docs/lead_us_birdseye_batch4.md
       src_us_birdseye_batch4.py [--dry]      stage the sources into this task's own staging files
       src_us_birdseye_batch4.py --check      offline (no network): join the staged files and run fit/evidence.py's check
       src_us_birdseye_batch4.py --golden     write tests/golden/src_us_birdseye_batch4_sample.json (the staged rows, normalized)

Staging writes only this task's files (append-only, idempotent on (site, title)); 236c consolidates
them into the canonical ones and builds the new sites. A row's evidence field is hand-recorded
caption_coords: the caption names the city and the stored coordinates are the verified site point -
record --live would take the first name-search hit instead, and the stage fails loud when the
caption does not print the city. A scan whose file page lost the drawing's date (or printed only
its copyright year) gets the known drawing/publication date on the row and the page value kept as
date_commons (the Zwolle precedent: sources.py and src_van_deventer.py swap before the keep() gate,
so the drawing's year - not a 21st-century upload - is what keep() judges). The system python3 has
no numpy (commons -> aw), so the live commands run under .venv/bin/python; the module top stays
stdlib-only.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

SITES_JSONL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
EXTRAS = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
EXTRAS_US_CITIES = os.path.join(ROOT, "data", "catalog", "extras_us_cities.jsonl")  # 236a's file: READ ONLY
EXTRAS_BIRDS_236B = os.path.join(ROOT, "data", "catalog", "extras_us_birdseye.jsonl")  # 236b's file: READ ONLY
EXTRAS_BIRDS_BATCH5 = os.path.join(ROOT, "data", "catalog", "extras_us_birdseye_batch5.jsonl")  # 241's file: ABSENT until 241 runs
EXTRAS_BIRDS = os.path.join(ROOT, "data", "catalog", "extras_us_birdseye_batch4.jsonl")
FILES_BIRDS = os.path.join(ROOT, "data", "commons", "files_us_birdseye_batch4.jsonl")
CLASSIFIED_BIRDS = os.path.join(ROOT, "data", "commons", "classified_us_birdseye_batch4.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

# New cities this task stages (only cities no other staging set holds - check data/catalog/
# sites.jsonl, extras.jsonl, extras_us_cities.jsonl (236a), extras_us_birdseye.jsonl (236b) and
# web/data/sites.json on main before adding one): hand-verified site facts, the pipeline/sources.py
# slug rule (id = slug + "-" + qid-lower, pipeline/catalog.py:slug), region "United States" (REGION_NAME
# in pipeline/build_catalog.py carries the display name), kind "town" = 2000 m box, aerial_ok true
# (aerial-photograph ground: no open LiDAR over a built-up city, bare-earth LiDAR erases the
# streets). Batch 4 (verified live 2026-10-14, --verify re-checks; per-view STAGED/DROP verdicts in
# docs/lead_us_birdseye_batch4.md): Denver (the next candidate after 236b's twelve new cities);
# St. Paul, Minneapolis, Cleveland follow in candidate order (the task owes FOUR staged cities, not
# specifically these four - a city with no usable view gets a lead-doc note and the next
# candidate).
SITES = {
    # Q16554: P625 = ONE 30 m value (-104.984722, 39.739167) - the central CBD (16th-20th street
    # core; no refinement needed). P373 is the STRING "Denver, Colorado" (a Wikidata quirk, not a
    # country entity - the place is written from the county + the state); P131 = Q1261 Colorado +
    # Q13052701 Denver County (Denver is a consolidated CITY-COUNTY, the county-level twin of New
    # Orleans' single-parish case - hence place "Denver County, Colorado"); P17 = Q30 (a proper
    # entity); enwiki "Denver". The first-guess QID Q3101 is a PERSON (Patrick Ricard) - caught by
    # the label check (the usual first-guess trap class). Name search: NO TRAP (the first hit with
    # P625, what record --live would store, is Q16554 itself, dist 0). No existing site holds the
    # QID (checked in the catalog, extras, 236a's and 236b's extras files and web/data/sites.json
    # at the 240 session-1 re-check); site id denver-q16554 (catalog.slug("Denver") = "denver",
    # verified).
    "Q16554": dict(id="denver-q16554", name="Denver", named="Denver",
                   lon=-104.984722, lat=39.739167,
                   place="Denver County, Colorado", region="United States", kind="town",
                   wikipedia="https://en.wikipedia.org/wiki/Denver",
                   note="aerial-photograph ground (no open LiDAR over the built-up city: bare-earth "
                        "LiDAR erases the streets); the street grid, the South Platte and the Front "
                        "Range carry the fit; the 1908 staged sheet is the steepest (near-vertical) "
                        "whole-city view in the pool, drawn from the north (the Twenty-Third Street "
                        "Viaduct, ~1.3 km north of the point) looking south - the grid dense and "
                        "legible to the southern suburbs, the Front Range along the southern "
                        "horizon, a printed landmark index - spanning the whole city beyond the "
                        "2000 m town box, so its fit is likely to end a review item (the 236a "
                        "NY-1811 / DC-ring precedent)"),
}

# Denver (batch 4, city 1; checked live 2026-10-14; the pool 65 unique / 33 good, per-view
# STAGED/DROP verdicts in docs/lead_us_birdseye_batch4.md). One row per city: the steepest,
# best-scanned whole-city view of the collection; the shallower same-genre sheets and the non-view
# pool (district close-ups, real-estate ads, street-car scenes, regional views, photographs,
# too-small scans, other-city sheets, licence rejects) are DROPS recorded in the lead doc (the
# 236b precedent).
DENVER_1908 = [
    # 1908 (Birdseye View Publishing Co.; Denver Lith. Co., LC Panoramic maps (2nd ed.), 66;
    # 19338x13294, Public domain): banner "BIRD'S EYE VIEW OF DENVER, COLORADO, 1908 LOOKING SOUTH
    # FROM THE TWENTY-THIRD STREET VIADUCT" - the steepest (near-vertical) whole-city view in the
    # pool, drawn from the north of the city looking south: the dense grid legible to the southern
    # suburbs, the Front Range along the top of the sheet (the southern horizon), the South Platte
    # meandering in from the northwest along the sheet's RIGHT side (the sheet faces south, so
    # west is right - no mirroring), a landmark index across the bottom; the viaduct sits ~1.3 km
    # north of the site's point (23rd-street lat 39.7508 - P625 39.739167 = 0.0116 deg x 110900
    # m/deg = 1287 m, measured 2026-10-14). The 19338x13294 .tif twin and the 9000x6205 DPLA copy
    # (4ac8083cbba722c01cad3388a37a7a0f) are the same sheet - one row per sheet, the LOC .jpg
    # staged. The page date (1908) matches the drawing (no Zwolle-style swap).
    ("File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg", "Q16554", "Denver", dict()),
]

SOURCES = {
    "denver_1908": dict(rows=DENVER_1908, p="birdseye",
                        label="{name}, the Birdseye View Publishing Co. bird's-eye view (1908)"),
}


def now():
    return time.strftime("%Y-%m-%d")


def _commons():
    import commons  # lazy: commons -> aw needs numpy (absent from the system python3)
    return commons


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def _datavalues(claims):
    return [x["mainsnak"]["datavalue"]["value"] for x in claims if "datavalue" in x.get("mainsnak", {})]


def _ids(claims):
    return [v.get("id") for v in _datavalues(claims) if isinstance(v, dict) and v.get("id")]


def known_sites():
    """{qid: site id} over the built sites, the catalog, the extras, 236a's US-cities extras (READ
    ONLY), 236b's bird's-eye extras (READ ONLY) and 241's batch-5 extras (a forward read: the file
    is absent until 241 runs, a pure no-op while 240 runs - _load() tolerates it) - a source never
    makes a second site, so a QID can never sit on two sites once the batches merge."""
    out = {}
    for p in (SITES_JSONL, EXTRAS, EXTRAS_US_CITIES, EXTRAS_BIRDS_236B, EXTRAS_BIRDS_BATCH5):
        for s in _load(p):
            if s.get("qid") and s["qid"] not in out:
                out[s["qid"]] = s["id"]
    for s in json.load(open(WEB_SITES, encoding="utf-8"))["sites"]:
        if s.get("qid") and s["qid"] not in out:
            out[s["qid"]] = s["id"]
    return out


def _site_table():
    """The site table for this module: the cities this task stages, keyed by QID. Each value
    carries id/name/named/lon/lat (verify and stage both read from here)."""
    return {qid: dict(s, qid=qid) for qid, s in SITES.items()}


def verify_qids():
    """Re-verify every table QID against Wikidata (paced) and print the facts for the lead doc: the label,
    every P625 value (flagged when >50 km from the table's site point), P373, P131 (with labels), the
    enwiki title, and the first name-search hit with coordinates (what record --live would resolve for the
    caption route). This is the re-check that this module's own table stands on."""
    import evidence  # hav_m (the fit/ sibling; needs numpy, run under .venv)
    c = _commons()
    table = _site_table()
    qids = sorted(table)
    d = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(qids), "props": "claims|sitelinks|labels",
                     "languages": "en"})
    ents = d.get("entities", {})
    p131s = sorted({i for q in qids for i in _ids(ents.get(q, {}).get("claims", {}).get("P131", []))})
    labels = {}
    for i in range(0, len(p131s), 50):  # wbgetentities takes at most 50 ids per call
        d2 = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(p131s[i:i + 50]), "props": "labels",
                          "languages": "en"})
        labels.update({k: v.get("labels", {}).get("en", {}).get("value") for k, v in d2.get("entities", {}).items()})
    print(f"checked {now()} - {len(qids)} QIDs (Wikidata)")
    for qid in qids:
        e = ents.get(qid) or {}
        cl = e.get("claims", {})
        s = table[qid]
        print(f"  {qid}  {e.get('labels', {}).get('en', {}).get('value')!r}  (site id: {s['id']}, new (this task))")
        p625 = [(v["longitude"], v["latitude"]) for v in _datavalues(cl.get("P625", [])) if v]
        print(f"      P625: {p625}  (table site point: {s['lon']}, {s['lat']})")
        for lon, lat in p625:
            dist = evidence.hav_m(lon, lat, s["lon"], s["lat"])
            if dist > 50e3:
                print(f"      FLAG: a P625 is {dist / 1000:.0f} km from the table's point (the recorded trap; "
                      f"the table point stands)")
        print(f"      P373: {_datavalues(cl.get('P373', []))}")
        print(f"      P131: {[(labels.get(i), i) for i in _ids(cl.get('P131', []))]}  "
              f"(table place: {s.get('place')!r})")
        print(f"      enwiki: {e.get('sitelinks', {}).get('enwiki', {}).get('title')!r}  "
              f"(table wikipedia: {s.get('wikipedia')!r})")
        sr = c.get(c.WD, {"action": "wbsearchentities", "search": s["name"], "language": "en", "limit": "5"})
        ids = [x["id"] for x in sr.get("search", [])]
        if ids:
            d3 = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(ids), "props": "claims|labels",
                              "languages": "en"})
            for q in ids:
                hits = [(v["longitude"], v["latitude"]) for v in _datavalues(
                    d3.get("entities", {}).get(q, {}).get("claims", {}).get("P625", [])) if v]
                if hits:
                    lon, lat = hits[0]
                    dist = evidence.hav_m(lon, lat, s["lon"], s["lat"])
                    flag = "" if dist <= 50e3 else f"   <- TRAP: {dist / 1000:.0f} km, the live record would " \
                                                  f"store a conflict (kind none)"
                    lab = d3["entities"][q].get("labels", {}).get("en", {}).get("value", "")
                    print(f"      search {s['name']!r}: first hit with P625 is {q} {lab!r} ({lon}, {lat}){flag}")
                    break
    return 0


def evidence_for(qid, site, title, m):
    """The hand-recorded caption_coords tie, in the key order of fit/evidence.py's caption_route(): the
    place named is the site's own short name as the file caption prints it, and the stored coordinates
    are the verified site point (record --live would take the first name-search hit instead). None when
    the caption does not print the name - the stage fails loud, never a guessed tie."""
    import books_match  # lazy: the module top stays stdlib-only
    named = site.get("named") or site["name"]
    if books_match.norm(named) not in books_match.norm(title + " " + (m.get("desc") or "")):
        return None
    return {"rec": "evidence/1", "kind": "caption_coords", "checked": now(),
            "named_place": named, "place_qid": qid, "place_label": site["name"],
            "place_lon": site["lon"], "place_lat": site["lat"],
            "site_lon": site["lon"], "site_lat": site["lat"], "dist_m": 0.0}


def _site_row(qid, site, name):
    row = {"id": site["id"], "qid": qid, "name": site["name"], "lon": site["lon"], "lat": site["lat"],
           "region": site["region"], "kind": site["kind"], "aerial_ok": True,
           "source": f"fit/src_us_birdseye_batch4.py {name}"}
    if site.get("place"):
        row["place"] = site["place"]
    if site.get("wikipedia"):
        row["wikipedia"] = site["wikipedia"]
    row["note"] = site["note"]
    return row


def _append(path, rows):
    if not rows:
        return
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def stage(dry=False):
    """Stage the sources into this task's own files (append-only, idempotent on (site, title)). Drift
    fails loud: a title that vanished from Commons, a file commons.keep() would drop, a caption that
    does not print the city, a QID not in SITES. A new city gets one extras row each, here; a QID a
    known site already holds ties the file row to that site instead (never a second site for one QID
    - recorded in the lead doc if it ever happens; expected for none)."""
    c = _commons()
    known = known_sites()
    have = {(r.get("site"), r.get("title")) for r in _load(FILES_BIRDS) + _load(CLASSIFIED_BIRDS)}
    staged_ids = {s["id"] for s in _load(EXTRAS_BIRDS)}
    titles = [r[0] for s in SOURCES.values() for r in s["rows"]]
    meta = c.info(titles)
    new_sites, new_files, new_cls, to_build = [], [], [], []
    for name, src in SOURCES.items():
        for title, qid, label, *extra in src["rows"]:
            x = extra[0] if extra else {}
            if qid not in SITES:
                raise SystemExit(f"row {title!r}: QID {qid} not in SITES (batch 4 stages no shared "
                                 f"cities; a found collision goes to a 236b-style shared table, "
                                 f"recorded in the lead doc)")
            site = dict(SITES[qid], qid=qid)
            sid = known.get(qid) or site["id"]
            if known.get(qid) is None and sid not in staged_ids:
                new_sites.append(_site_row(qid, site, name))
                staged_ids.add(sid)
                to_build.append(sid)
            if (sid, title) in have:
                continue
            m = meta.get(title) or {}
            if not m.get("url"):
                raise SystemExit(f"not on Commons (title changed?): {title}")
            want = x.get("date")
            if want and c.year_of(title, m) != c.year_of(title, {"date": want}):
                # the known drawing/publication date on the row, the page value kept as date_commons
                # (the Zwolle precedent: sources.py and src_van_deventer.py swap before the keep() gate,
                # so the drawing's year - not the copyright/upload year - is what keep() judges)
                m = dict(m, date=want, date_commons=m.get("date"))
            if not c.keep(title, m):
                raise SystemExit(f"commons.keep() would drop {title!r}: fix the table or record the drop "
                                 f"in docs/lead_us_birdseye_batch4.md")
            ev = evidence_for(qid, site, title, m)
            if ev is None:
                raise SystemExit(f"{title!r}: the caption does not print "
                                 f"{site.get('named') or site['name']!r} - pick a file that does, or record "
                                 f"the drop in docs/lead_us_birdseye_batch4.md")
            f = {"site": sid, "qid": qid, "title": title, "year": c.year_of(title, m), "wd_plan": False,
                 "cat": None, "name": src["label"].format(name=label),
                 "by": f"fit/src_us_birdseye_batch4.py {name}", **m}
            f["evidence"] = ev
            new_files.append(f)
            p = {"p_plan": 0.0, "p_birdseye": 0.0, "p_photo": 0.0}
            p[f"p_{src['p']}"] = 1.0
            new_cls.append({"site": sid, "title": title, **p, "by": "hand"})
    print(f"staged: {len(new_sites)} new sites, {len(new_files)} new pictures")
    for s in new_sites:
        print("   ", s["id"], s["lon"], s["lat"], s.get("place"))
    if to_build:
        print("build (236c):", ",".join(to_build))
    if dry:
        return
    _append(EXTRAS_BIRDS, new_sites)
    _append(FILES_BIRDS, new_files)
    _append(CLASSIFIED_BIRDS, new_cls)


def check_staged():
    """Offline (no network): join the staged files (every file row names a staged or existing site -
    existing = the catalog/extras, 236a's and 236b's extras files and the built web sites, all
    read-only here; a staged QID or id is a problem only when it resolves to a DIFFERENT site - the
    module's own rows already merged by 236c are a no-op, not a collision; every NEW staged site has
    a picture; (site, title) unique; a staged row whose key is in the canonical files.jsonl must be
    identical to the canonical row under the merge's identity rule (the first-row-wins merge) - a
    same-key different row still fails loud; classified rows 1:1 with the file rows) and run
    fit/evidence.py's check over the staged rows. Returns the exit code (0 iff no problem and no
    FAIL)."""
    import evidence
    files = _load(FILES_BIRDS)
    sites = _load(EXTRAS_BIRDS)
    cls = _load(CLASSIFIED_BIRDS)
    known = known_sites()  # includes 236a's and 236b's files: those ids are "existing" sites
    problems = []
    staged_ids = {s["id"] for s in sites}
    known_ids = {}  # id -> the set of known QIDs that hold it
    for qid, sid in known.items():
        known_ids.setdefault(sid, set()).add(qid)
    # after 236c's merge the module's own staged sites sit in the canonical extras (known): a staged
    # id/QID is a problem only when it resolves to a DIFFERENT site (the pre-merge clash protection);
    # a self reference (the same site via the catalog, or its own merged row) is a no-op
    clash = {s["id"] for s in sites if known_ids.get(s["id"], set()) - {s.get("qid")}}
    if clash:
        problems.append(f"staged site ids collide with existing sites: {sorted(clash)}")
    for s in sites:
        if s.get("qid") in known and known[s["qid"]] != s["id"]:
            problems.append(f"staged site {s['id']} re-uses existing QID {s['qid']} ({known[s['qid']]})")
    pics = {s["id"]: 0 for s in sites}  # the no-picture check applies to NEW sites only
    valid = set(pics) | set(known.values())
    seen, canonical = set(), {}
    for r in _load(FILES_CANONICAL):
        k = (r.get("site"), r.get("title"))
        if k not in canonical:  # first row wins, as in the 236c merge
            canonical[k] = _canon_norm(r)
    for r in files:
        sid = r.get("site")
        if sid not in valid:
            problems.append(f"file row names a site that is neither staged nor existing: {sid!r} "
                            f"({r.get('title')!r})")
            continue
        if sid in pics:
            pics[sid] += 1
        k = (sid, r.get("title"))
        if k in seen:
            problems.append(f"duplicate staged row {k}")
        if k in canonical and canonical[k] != _canon_norm(r):
            problems.append(f"staged title already in the canonical files.jsonl: {k}")
        seen.add(k)
    for sid in pics:
        if not pics[sid]:
            problems.append(f"staged site {sid} has no staged picture")
    if {(r.get("site"), r.get("title")) for r in cls} != seen:
        problems.append("the classified rows are not 1:1 with the staged file rows")
    for p in problems:
        print("join:", p)
    code, text = evidence.check(FILES_BIRDS, NO_BOOKS, catalog=EXTRAS_BIRDS)
    print(text)
    return 1 if problems else code


def _canon_norm(r):
    """Row identity under the 236c merge rule (the same norm fit/merge.py uses on the line): key order and
    ASCII escaping don't matter, content does."""
    return json.dumps(r, sort_keys=True, ensure_ascii=False)


def _norm(rows):
    """The rows for the golden file: keys are sorted by the dump, "checked" and "date_commons" normalized
    (they vary with the staging date)."""
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
    """Write tests/golden/src_us_birdseye_batch4_sample.json: the staged extras, files and classified
    rows, normalized. Regenerate only for an intended change."""
    p = path or os.path.join(ROOT, "tests", "golden", "src_us_birdseye_batch4_sample.json")
    out = {"extras": _norm(_load(EXTRAS_BIRDS)), "files": _norm(_load(FILES_BIRDS)),
           "classified": _norm(_load(CLASSIFIED_BIRDS))}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", p)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        stage(False)
    elif a[0] == "--dry":
        stage(True)
    elif a[0] == "--verify":
        raise SystemExit(verify_qids())
    elif a[0] == "--check":
        raise SystemExit(check_staged())
    elif a[0] == "--golden":
        golden()
    else:
        raise SystemExit(__doc__.split("usage:")[1].strip())
