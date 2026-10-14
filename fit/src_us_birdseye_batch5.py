"""Batch 5 of the bird's-eye and panoramic views of US cities (task 241, part of 236; GOAL.md
point 5: artists' aerial and bird's-eye views count as much as surveys): the FINAL FIVE US cities
of the 25-city total, each a new site of its own in this task's own staging files (one module + one
staging file set per batch, so 240 and 241 built in parallel) - staged from the Library of Congress
"Panoramic Maps" collection (about 1,500 US bird's-eye views, 1847-1929, public domain; this
machine cannot reach loc.gov, so the files are fetched from their Wikimedia Commons mirrors - the
236b route, its lead doc docs/lead_us_birdseye.md). The 25-city total spans 236b's 16 + 240's four
+ 241's five; 236c consolidates every staging set into the canonical data and checks the total.
The candidate order (240's lead-doc "Not done yet" pointer, continuing the 181 candidate list of
the 236b lead doc): Omaha (landed first: the 1868 E. Ruger sheet - the 236b silent-skip question
resolves stageable: it fell out of 236b's batch order, its pool has a strong pick), Indianapolis,
Columbus, Memphis, then whatever the collection's search order adds to reach five. This task
owes FIVE staged cities, not specifically these - a city with no usable view gets a lead-doc
note and the next candidate.

This module is a copy of fit/src_us_birdseye_batch4.py (240's module), which is itself a copy of
fit/src_us_birdseye.py (236b's module) - the template this module keeps in sync with: the
verify/stage/check/golden machinery, the 200 caption_coords evidence field, the Zwolle date-swap
rule, the never-two-sites-for-one-QID cross-check - extended here so known_sites() reads the
catalog, 236a's extras_us_cities.jsonl, 236b's extras_us_birdseye.jsonl and 240's
extras_us_birdseye_batch4.jsonl (all read-only), so a QID can never sit on two sites. The batch-5
copy stages NO shared (owner-named) cities: 236a's four owner cities are tied to their 236a site
ids by 236b's module, which stages all of 236b's own views, so SHARED_SITES and its machinery stay
out of this copy (if research ever found a batch-5 city already held by an existing site - expected
for none - the fix is a small 236b-style shared table pointing at that site, recorded in the lead
doc). One row per city: the steepest (near-vertical), best-scanned whole-city view of the
collection (Public domain, >= 4000 px wide, the caption names the city). Bird's-eye views are
oblique, so the site's note records the staged view's apparent angle where the fit order depends on
it (near-vertical views fit best; the 2000 m town-box overshoots are likely review items, the 236a
NY-1811 / DC-ring precedent in docs/lead_us_cities.md).

usage: src_us_birdseye_batch5.py --verify     re-verify every table QID against Wikidata
                                   (label, every P625 value, P373, P131, enwiki, the first name-search hit
                                   with coordinates - what record --live would resolve); copy the output into
                                   docs/lead_us_birdseye_batch5.md
       src_us_birdseye_batch5.py [--dry]      stage the sources into this task's own staging files
       src_us_birdseye_batch5.py --check      offline (no network): join the staged files and run fit/evidence.py's check
       src_us_birdseye_batch5.py --golden     write tests/golden/src_us_birdseye_batch5_sample.json (the staged rows, normalized)

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
EXTRAS_BIRDS_BATCH4 = os.path.join(ROOT, "data", "catalog", "extras_us_birdseye_batch4.jsonl")  # 240's file: READ ONLY
EXTRAS_BIRDS = os.path.join(ROOT, "data", "catalog", "extras_us_birdseye_batch5.jsonl")
FILES_BIRDS = os.path.join(ROOT, "data", "commons", "files_us_birdseye_batch5.jsonl")
CLASSIFIED_BIRDS = os.path.join(ROOT, "data", "commons", "classified_us_birdseye_batch5.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

# New cities this task stages (only cities no other staging set holds - check data/catalog/
# sites.jsonl, extras.jsonl, extras_us_cities.jsonl (236a), extras_us_birdseye.jsonl (236b),
# extras_us_birdseye_batch4.jsonl (240) and web/data/sites.json on main before adding one):
# hand-verified site facts, the pipeline/sources.py slug rule (id = slug + "-" + qid-lower,
# pipeline/catalog.py:slug), region "United States" (REGION_NAME in pipeline/build_catalog.py
# carries the display name), kind "town" = 2000 m box, aerial_ok true (aerial-photograph ground:
# no open LiDAR over a built-up city, bare-earth LiDAR erases the streets). Batch 5 is the FINAL
# FIVE cities of the 25-city total (16 from 236b + 4 from 240 + 5 here); the candidate order
# (240's lead-doc "Not done yet" pointer, continuing the 181 candidate list of the 236b lead
# doc): Omaha (LANDED, city 1 of 5 - the 1868 E. Ruger sheet; the 236b silent-skip question
# resolves stageable: it fell out of 236b's batch order, its pool has a strong pick),
# Indianapolis, Columbus, Memphis, then whatever the collection's search order
# adds to reach five (each new entry verified live, --verify re-checks; per-view STAGED/DROP
# verdicts in docs/lead_us_birdseye_batch5.md). This task owes FIVE staged cities, not
# specifically these - a city with no usable view gets a lead-doc note and the next candidate.
SITES = {
    # Q43199: P625 = ONE 30 m value (-95.9375, 41.25861111111111) - the downtown core (no
    # refinement needed). P373 is the STRING "Omaha, Nebraska" (a Wikidata quirk, not a country
    # entity - the place is written from the county + the state); P131 = Q490695 Douglas County
    # (the only one, + the state) - hence place "Douglas County, Nebraska"; P17 = Q30 (a proper
    # entity); enwiki "Omaha, Nebraska". Name search at limit 5 AND limit 20 (the 241 session-3
    # research run): NO TRAP - the first hit with P625, what record --live would store, is Q43199
    # itself (dist 0); the other hits are a Ulf Lundell album, the University of Nebraska Omaha
    # (Q2495890, an in-city institution - the Pittsburgh/Chicago trap class, but it never comes
    # first), a 2025 film, Omaha Beach (France), namesake cities (TX/AR/IL/GA), a racehorse, a
    # ship. No existing site holds the QID (checked at the 241 session-3 run in the catalog,
    # extras, 236a's, 236b's and 240's extras files and web/data/sites.json); site id
    # omaha-q43199 (catalog.slug("Omaha") = "omaha", verified).
    "Q43199": dict(id="omaha-q43199", name="Omaha", named="Omaha",
                   lon=-95.9375, lat=41.25861111111111,
                   place="Douglas County, Nebraska", region="United States", kind="town",
                   wikipedia="https://en.wikipedia.org/wiki/Omaha,_Nebraska",
                   note="aerial-photograph ground (no open LiDAR over the built-up city: bare-earth "
                        "LiDAR erases the streets); the street grid and the Missouri carry the fit; "
                        "the 1868 E. Ruger sheet is the steepest (near-vertical) whole-city view in "
                        "the pool (the 1905 Austen 'panoramic' oblique is the recorded dupe): drawn "
                        "from a high vantage across the Missouri River - the river a foreground "
                        "strip with steamboats and a railroad along the sheet's bottom, a thin "
                        "hill-horizon band across the top - the city grid fills the sheet beyond "
                        "the 2000 m town box, so its fit is likely to end a review item (the 236a "
                        "NY-1811 / DC-ring precedent)"),
}

# The per-view source rows land here as each city lands, keyed by <city>_<year> like the batch-4
# module's DENVER_1908 etc.: one row per city = the steepest (near-vertical), best-scanned
# whole-city view of the collection (Public domain, >= 4000 px wide, the caption names the city);
# the shallower same-genre sheets and the non-view pool (district close-ups, real-estate ads,
# street-car scenes, regional views, photographs, too-small scans, other-city sheets, licence
# rejects) are DROPS recorded in the lead doc (the 236b/240 precedent).
# Omaha (batch 5, city 1; checked live 2026-10-14; the pool 39 unique / 8 gate-pass, per-view
# STAGED/DROP verdicts in docs/lead_us_birdseye_batch5.md). One row per city: the steepest,
# best-scanned whole-city view of the collection; the shallower same-genre sheets and the
# non-view pool (a low panoramic oblique, stereoscopic photo cards, book text pages, regional
# and other-city sheets, too-small scans, licence rejects) are DROPS recorded in the lead doc
# (the 236b/240 precedent).
OMAHA_1868 = [
    # 1868 (the sheet's own signature lower left reads "Drawn by E. Ruger" - the page's artist
    # field reads "Ruger, A.", an A. Ruger work like 240's Cleveland 1877 sheet - a different
    # Ruger, the label runs from the sheet's signature; lith. by the Chicago Lithographing Co.,
    # its name at the sheet's lower right; LC Panoramic maps (2nd ed.), 467; 8896x7024, Public
    # domain): the lower-centre cartouche reads "BIRD'S EYE VIEW OF THE CITY OF / OMAHA /
    # NEBRASKA / 1868" (labelled landmark vignettes along the bottom border: Turner's Hall,
    # Central Block, Oakwell Block, the court house, ...; a numbered landmark legend) - THE
    # steepest (near-vertical) whole-city view in the pool: drawn from a high vantage across the
    # Missouri River - the "MISSOURI RIVER" label runs diagonally along the sheet's lower right,
    # the steamboat traffic and the rail yard with its rolling stock at the sheet's right, a thin
    # hill-horizon band across the top - the built-up grid fills the sheet beyond the 2000 m
    # town box, so its fit is likely to end a review item (the 236a NY-1811 / DC-ring precedent);
    # the LC Division-of-Maps stamp (FEB 28 1941) and the handwritten LCCN "73-693495" at the
    # lower right. The page date (1868) matches the drawing (no Zwolle-style swap). The .tif is
    # the ONLY scan of the sheet on Commons (an LCCN search) - no .jpg mirror to stage instead.
    ("File:Bird's eye view of the city of Omaha, Nebraska 1868. LOC 73693495.tif", "Q43199", "Omaha", dict()),
]

SOURCES = {
    "omaha_1868": dict(rows=OMAHA_1868, p="birdseye",
                       label="{name}, the E. Ruger / Chicago Lithographing Co. bird's-eye view (1868)"),
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
    ONLY), 236b's bird's-eye extras (READ ONLY) and 240's batch-4 extras (READ ONLY) - a source
    never makes a second site, so a QID can never sit on two sites once the batches merge."""
    out = {}
    for p in (SITES_JSONL, EXTRAS, EXTRAS_US_CITIES, EXTRAS_BIRDS_236B, EXTRAS_BIRDS_BATCH4):
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
           "source": f"fit/src_us_birdseye_batch5.py {name}"}
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
                raise SystemExit(f"row {title!r}: QID {qid} not in SITES (batch 5 stages no shared "
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
                                 f"in docs/lead_us_birdseye_batch5.md")
            ev = evidence_for(qid, site, title, m)
            if ev is None:
                raise SystemExit(f"{title!r}: the caption does not print "
                                 f"{site.get('named') or site['name']!r} - pick a file that does, or record "
                                 f"the drop in docs/lead_us_birdseye_batch5.md")
            f = {"site": sid, "qid": qid, "title": title, "year": c.year_of(title, m), "wd_plan": False,
                 "cat": None, "name": src["label"].format(name=label),
                 "by": f"fit/src_us_birdseye_batch5.py {name}", **m}
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
    existing = the catalog/extras, 236a's, 236b's and 240's extras files and the built web sites,
    all read-only here; a staged QID or id is a problem only when it resolves to a DIFFERENT site - the
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
    """Write tests/golden/src_us_birdseye_batch5_sample.json: the staged extras, files and classified
    rows, normalized. Regenerate only for an intended change."""
    p = path or os.path.join(ROOT, "tests", "golden", "src_us_birdseye_batch5_sample.json")
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
