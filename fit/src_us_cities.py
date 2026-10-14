"""Old plans of US cities (task 236a, GOAL.md point 5: a city plan or a fortification plan is a drawing): the
hand-checked file -> QID table for the old plans of New York - the 1660 Castello plan, the 1767 Ratzer map,
the 1811 Commissioners' Plan (bird's-eye) and the 1865 Viele map - of Washington DC - the 1791 L'Enfant plan
(as its 1792 first-printed edition), the 1792 Ellicott plan and the 1865 Civil War defences map - and of San
Francisco - the 1849 Eddy survey map, the 1850 first-published map and the 1854 Eddy 'full and complete'
sheet - staged into this task's own staging files the way src_artists.py does. Nashville follows in a later
session; 236c consolidates the staged rows into the canonical data and builds the sites.

usage: src_us_cities.py --verify     re-verify every table QID (SITES) against Wikidata
                                   (label, every P625 value, P373, P131, enwiki, the first name-search hit
                                   with coordinates - what record --live would resolve); copy the output into
                                   docs/lead_us_cities.md
       src_us_cities.py [--dry]      stage the sources into this task's own staging files
       src_us_cities.py --check      offline (no network): join the staged files and run fit/evidence.py's check
       src_us_cities.py --golden     write tests/golden/src_us_cities_sample.json (the staged rows, normalized)

Staging writes only this task's files (append-only, idempotent on (site, title)); 236c consolidates them into
the canonical ones and builds the sites. The city sites are aerial-photograph ground (no open LiDAR over a
built-up city: bare-earth LiDAR erases the streets) and the street grid, shoreline, squares and church
footprints carry the fit; Civil War fortification plans are the exception - their banks may show on 3DEP
bare earth (pipeline/aw.py). A row's evidence field is hand-recorded caption_coords: the caption names the
city and the stored coordinates are the verified site point - record --live would take the first name-search
hit instead, and the stage fails loud when the caption does not print the city. A scan whose file page lost
the drawing's date gets the known drawing date on the row and the page value kept as date_commons (the
Zwolle precedent; sources.py and src_van_deventer.py swap before the keep() gate, so the drawing's year -
not a 21st-century upload - is what keep() judges). The system python3 has no numpy (commons -> aw), so the
live commands run under .venv/bin/python; the module top stays stdlib-only.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

SITES_JSONL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
EXTRAS = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
EXTRAS_US_CITIES = os.path.join(ROOT, "data", "catalog", "extras_us_cities.jsonl")
FILES_US_CITIES = os.path.join(ROOT, "data", "commons", "files_us_cities.jsonl")
CLASSIFIED_US_CITIES = os.path.join(ROOT, "data", "commons", "classified_us_cities.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

# Hand-verified site facts (verified 2026-10-13, --verify re-checks; docs/lead_us_cities.md records the facts
# and the trap notes). id = slug + "-" + qid-lower (the pipeline/sources.py rule); region "United States"
# (REGION_NAME carries the display name, pipeline/build_catalog.py - the old US extras rows keep "US");
# kind "town" = 2000 m box (build_catalog.BOX); "named" is the short form the file captions print (the
# caption route needs it inside title+desc, fit/evidence.py check_caption). None of the four owner-named
# QIDs is in the catalog yet, so every city gets a new extras row.
SITES = {
    # Q60 (the prep's first memory, Q30492, is the NUMBER "483" - the Barnard Castle trap in action, caught
    # in the verification). P625 (-74.006111, 40.712778) = the Financial District / City Hall: the 2000 m
    # town box covers the harbour tip of Manhattan to ~19th St, the 1660 plan's whole drawn extent; the
    # 1811 and 1865 sheets span well beyond it, so their fits are likely to end review items (the Venice
    # precedent, docs/lead_artists.md) - recorded on the rows' notes, not as an extent field.
    "Q60": dict(id="new-york-q60", name="New York City", named="New York",
                lon=-74.006111, lat=40.712778,
                place="New York County, New York", region="United States", kind="town",
                wikipedia="https://en.wikipedia.org/wiki/New_York_City",
                note="aerial-photograph ground (no open LiDAR over the built-up city: bare-earth LiDAR erases "
                     "the streets); the street grid, the 1865 shoreline, the squares and church footprints "
                     "carry the fit; the 1811 and 1865 sheets span the island beyond the 2000 m town box, so "
                     "those fits are likely to end review items (the Venice precedent, docs/lead_artists.md)"),
    # Q61 (verified 2026-10-13 via pipeline/catalog_wd; --verify re-checks): ONE P625
    # (-77.036667, 38.895) = the old L'Enfant core, so the 1791/1792 flat plans sit inside the 2000 m town
    # box. The 1865 defences ring spans ~35 km beyond it: its fit is likely to end a review item (the
    # Venice precedent), and the ring's forts are the catalog's own sites (the note), not new QIDs. The
    # Boschke map (1857/1861) does not stage: its caption prints "Washington" only past the gate's
    # 600-char truncation (the 1857 file, the only one whose title prints the city, trips
    # commons.keep()'s "portrait" word on one of the map's vignettes - the exact per-file record is in
    # docs/lead_us_cities.md).
    "Q61": dict(id="washington-q61", name="Washington, D.C.", named="Washington",
                lon=-77.036667, lat=38.895,
                place="District of Columbia", region="United States", kind="town",
                wikipedia="https://en.wikipedia.org/wiki/Washington,_D.C.",
                note="aerial-photograph ground (no open LiDAR over the built-up city: bare-earth LiDAR erases "
                     "the streets); the street grid, the diagonal avenues, the Potomac shoreline and the "
                     "squares carry the fit; the 1865 defences ring spans ~35 km beyond the 2000 m town box, "
                     "so that fit is likely to end a review item (the Venice precedent, docs/lead_artists.md); "
                     "the ring's forts are candidate kind-'fort' sites and the catalog already has the "
                     "individuals (Fort Bayard Q3077774, Fort DeRussy Q5471024, Fort Totten Q18150335, "
                     "Fort Marcy Q61784495, Fort Foote Q14691922, all part_of Q5124610 'Civil War defenses of "
                     "Washington, D.C.' - data/catalog/sites.jsonl)"),
    # Q62 (verified 2026-10-13 via pipeline/catalog_wd; --verify re-checks): TWO P625 values
    # (-122.41944444444445, 37.775) and (-122.41638888888889, 37.7775), both downtown, ~2-2.4 km SW of the
    # table point (no >50 km flag from --verify). The point is REFINED, not a P625: every staged plan draws
    # the old town's peninsula - the street grid's NW corner (today's Washington & Jones, the old North
    # Beach tip) down to Rincon Point (today's Spear St between Harrison and Folsom - the corner of the old
    # bay) plus the 1850s growth - so the point is the midpoint of those two web-verified tips (enwiki
    # 'Rincon Point (San Francisco)' + Nominatim street segments; the corner interpolated): the center of
    # the drawn extent, ~(-122.403, 37.792). A P625-centered 4 km box would leave the bay tip outside it;
    # the midpoint box covers tip to tip (the NY/DC extent decision: oversize sheets end as review items,
    # not wider boxes).
    "Q62": dict(id="san-francisco-q62", name="San Francisco", named="San Francisco",
                lon=-122.40289, lat=37.79213,
                place="San Francisco County, California", region="United States", kind="town",
                wikipedia="https://en.wikipedia.org/wiki/San_Francisco",
                note="aerial-photograph ground (no open LiDAR over the built-up city: bare-earth LiDAR erases "
                     "the streets); the street grid, the bay shoreline (the 1854 sheet's red water-front "
                     "line), the squares and the hills carry the fit; the 1849-1854 sheets draw the old "
                     "peninsula tip to tip inside the 2000 m town box - the point is the midpoint of the two "
                     "drawn tips (Washington & Jones / Rincon Point), not a P625 (see the SITES comment); "
                     "the 1854 sheet's 1850s growth (the Center Street grid to the SW) also sits in the box"),
}

# New York leads (checked live 2026-10-13; the per-file STAGED/DROP verdicts - including the 1916
# Adams/Stokes redrafts of the Castello plan that are NOT the 1660 original - are in
# docs/lead_us_cities.md). Each row: (file title, site QID, the label the plan list shows, optional
# per-file facts).
CASTELLO = [
    # the surviving ORIGINAL drawing (Biblioteca Medicea-Laurenziana, Florence) scanned full-size; the file
    # page lost the drawing's date, so the known survey date is used (date_commons keeps the page value)
    ("File:Afbeeldinge van de Stadt Amsterdam in Nieuw Neederlandt (NYPL Hades-118555-54682).tif", "Q60",
     "New York", dict(date="1660")),
]
RATZER = [
    # the only full contemporary-color copy of the 1767/1770 engraving (DateTimeOriginal 1767 on the page)
    ("File:Plan of the City of New York by Bernard Ratzer, 1767.jpg", "Q60", "New York", dict()),
]
PLAN_1811 = [
    # the 1811 Commissioners' Plan in its published bird's-eye form (the page dates the 1821 publication;
    # the plan itself is 1811)
    ("File:Commissioners' Plan of 1811 by John Randel published in 1821.jpg", "Q60", "New York",
     dict(date="1811")),
]
VIELE = [
    # the Sanitary Commission's 1865 topographical map: original water courses and made land
    ("File:Viele Map (Topographical map of the City of New York), 1865.jpg", "Q60", "New York", dict()),
]

# Washington DC leads (checked live 2026-10-13; the per-file STAGED/DROP verdicts - including the Boschke
# map that cannot stage on Commons, with the exact why - are in docs/lead_us_cities.md).
LENEANT = [
    # the 1791 L'Enfant plan: the manuscript is at NARA (not on Commons) - this is its FIRST PRINTED
    # edition (Universal Asylum, Philadelphia, Mar. 1792, the same plate), so the known drawing date is
    # on the row and the page value kept as date_commons
    ("File:Plan of the city of Washington LOC 88694159.tif", "Q61",
     "Washington, D.C.", dict(date="1791")),
]
ELICOTT = [
    # the 1792 Ellicott engraved plan - the first official (surveyed) plan of the city
    ("File:Plan of the city of Washington in the territory of Columbia - ceded by the states of Virginia "
     "and Maryland to the United States of America, and by them established as the seat of their "
     "government, (NYPL b15255319-434417).jpg", "Q61", "Washington, D.C.", dict()),
]
DEFENCES = [
    # the 1865 Civil War defences map (Barnard's ring of forts, Atlas of the Official Records v.2 pl. XXXIX
    # no. 1) - the ring spans ~35 km beyond the town box, the review-item case (the Venice precedent)
    ("File:Map of the defences of Washington. LOC 88690674.jpg", "Q61", "Washington, D.C.", dict()),
]

# San Francisco leads (checked live 2026-10-13; the per-file STAGED/DROP verdicts - including the Ringgold
# 1849 town plan that is NOT on Commons (navy charts only) and the Henry Bill 1856/1858 view map that
# belongs to 236b - are in docs/lead_us_cities.md). All three print "San Francisco" in the title
# (the named-place gate, fit/evidence.py check_caption).
EDDY_1849 = [
    # the 1849 Eddy survey map - THE ORIGINAL manuscript (LOC's presentation copy, Dec. 31st 1849),
    # pen-and-ink and watercolor on cloth: the whole old town, North Beach to Rincon Point, 1:6,600
    ("File:Official map of San Francisco compiled from the field notes of the official re-survey made by "
     "Wm. M. Eddy. surveyor of the town of San Francisco. LOC 77692722.jpg", "Q62", "San Francisco", dict()),
]
MAP_1850 = [
    # the 1850 map body: "MAP OF THE CITY OF SAN FRANCISCO CALIFORNIA - COPIED FROM ORIGINALS WITH
    # CORRECTIONS AND ADDITIONS - 1850" (Sun Lithographic Est., NY) - the first map published after the
    # Eddy map (the inset shows the Apollo storeship, from Joseph P. Beach's journal)
    ("File:Map of San Francisco, Apollo storeship at the bottom.jpg", "Q62", "San Francisco", dict()),
]
EDDY_1854 = [
    # the 1854 Eddy 'full and complete' sheet (the map itself is dated January 15th 1854; the file page
    # lost the drawing's date, so the known survey date is on the row - the Zwolle precedent)
    ("File:Official map of the City of San Francisco, Full and complete to the present date. Compiled by "
     "Wm., M. Eddy. City Surveyor. (IA dr official-map-of-the-city-of-san-francisco-full-and-complete-to-"
     "the-present-5870000).jpg", "Q62", "San Francisco", dict(date="1854")),
]

SOURCES = {
    "castello": dict(rows=CASTELLO, p="plan",
                     label="{name}, the Castello plan (1660 Dutch survey of New Amsterdam)"),
    "ratzer": dict(rows=RATZER, p="plan", label="{name}, Bernard Ratzer's plan (1767)"),
    "plan_1811": dict(rows=PLAN_1811, p="birdseye",
                      label="{name}, the Commissioners' Plan (1811, bird's-eye view; published 1821)"),
    "viele": dict(rows=VIELE, p="plan", label="{name}, Egbert Viele's topographical map (1865)"),
    "le_1791": dict(rows=LENEANT, p="plan",
                    label="{name}, the L'Enfant plan (1791, first printed 1792)"),
    "ellicott": dict(rows=ELICOTT, p="plan",
                     label="{name}, Andrew Ellicott's plan (1792, the first official plan)"),
    "defences_1865": dict(rows=DEFENCES, p="plan",
                          label="{name}, the Civil War defences (1865 map of the fortification ring)"),
    "eddy_1849": dict(rows=EDDY_1849, p="plan",
                     label="{name}, the Eddy survey map (1849, the original)"),
    "map_1850": dict(rows=MAP_1850, p="plan",
                    label="{name}, the first published map (1850, 'Copied From Originals')"),
    "eddy_1854": dict(rows=EDDY_1854, p="plan",
                     label="{name}, the Eddy 'full and complete' sheet (1854)"),
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


def verify_qids():
    """Re-verify every table QID against Wikidata (paced) and print the facts for the lead doc: the label,
    every P625 value (flagged when >50 km from the table's site point), P373, P131 (with labels), the
    enwiki title, and the first name-search hit with coordinates (what record --live would resolve for the
    caption route)."""
    import evidence  # hav_m (the fit/ sibling; needs numpy, run under .venv)
    c = _commons()
    qids = sorted(SITES)
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
        s = SITES[qid]
        print(f"  {qid}  {e.get('labels', {}).get('en', {}).get('value')!r}")
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
    place named is the site's own short name as the file caption prints it, and the stored coordinates are
    the verified site point (record --live would take the first name-search hit instead). None when the
    caption does not print the name - the stage fails loud, never a guessed tie."""
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
           "source": f"fit/src_us_cities.py {name}"}
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
    """Stage the sources into this task's own files (append-only, idempotent on (site, title)). Drift fails
    loud: a title that vanished from Commons, a file commons.keep() would drop, or a caption that does not
    print the city."""
    c = _commons()
    known = known_sites()
    have = {(r.get("site"), r.get("title")) for r in _load(FILES_US_CITIES) + _load(CLASSIFIED_US_CITIES)}
    staged_ids = {s["id"] for s in _load(EXTRAS_US_CITIES)}
    titles = [r[0] for s in SOURCES.values() for r in s["rows"]]
    meta = c.info(titles)
    new_sites, new_files, new_cls, to_build = [], [], [], []
    for name, src in SOURCES.items():
        for title, qid, label, *extra in src["rows"]:
            if qid not in SITES:
                raise SystemExit(f"row {title!r}: QID {qid} not in the SITES table")
            x = extra[0] if extra else {}
            site = SITES[qid]
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
                # the known drawing date on the row, the page value kept as date_commons (the Zwolle
                # precedent: sources.py and src_van_deventer.py swap before the keep() gate, so a scan
                # whose page lost the drawing's date is judged by the drawing's year)
                m = dict(m, date=want, date_commons=m.get("date"))
            if not c.keep(title, m):
                raise SystemExit(f"commons.keep() would drop {title!r}: fix the table or record the drop "
                                 f"in docs/lead_us_cities.md")
            ev = evidence_for(qid, site, title, m)
            if ev is None:
                raise SystemExit(f"{title!r}: the caption does not print "
                                 f"{site.get('named') or site['name']!r} - pick a file that does, or record "
                                 f"the drop in docs/lead_us_cities.md")
            f = {"site": sid, "qid": qid, "title": title, "year": c.year_of(title, m), "wd_plan": False,
                 "cat": None, "name": src["label"].format(name=label),
                 "by": f"fit/src_us_cities.py {name}", **m}
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
    _append(EXTRAS_US_CITIES, new_sites)
    _append(FILES_US_CITIES, new_files)
    _append(CLASSIFIED_US_CITIES, new_cls)


def check_staged():
    """Offline (no network): join the staged files (every file row names a staged or existing site; a staged
    QID or id is a problem only when it resolves to a DIFFERENT site - the module's own rows already merged
    by 236c are a no-op, not a collision; every staged site has a picture; (site, title) unique; a staged
    row whose key is in the canonical files.jsonl must be identical to the canonical row under the merge's
    identity rule (the first-row-wins merge) - a same-key different row still fails loud; classified rows
    1:1 with the file rows) and run fit/evidence.py's check over the staged rows. Returns the exit code
    (0 iff no problem and no FAIL)."""
    import evidence
    files = _load(FILES_US_CITIES)
    sites = _load(EXTRAS_US_CITIES)
    cls = _load(CLASSIFIED_US_CITIES)
    known = known_sites()
    problems = []
    staged_ids = {s["id"] for s in sites}
    known_ids = {}  # id -> the set of known QIDs that hold it
    for qid, sid in known.items():
        known_ids.setdefault(sid, set()).add(qid)
    # after 236c's merge the module's own staged sites sit in the canonical extras (known): a staged
    # id/QID is a problem only when it resolves to a DIFFERENT site (the pre-merge clash protection); a
    # self reference (the same site via the catalog, or its own merged row) is a no-op
    clash = {s["id"] for s in sites if known_ids.get(s["id"], set()) - {s.get("qid")}}
    if clash:
        problems.append(f"staged site ids collide with existing sites: {sorted(clash)}")
    for s in sites:
        if s.get("qid") in known and known[s["qid"]] != s["id"]:
            problems.append(f"staged site {s['id']} re-uses existing QID {s['qid']} ({known[s['qid']]})")
    pics = {s["id"]: 0 for s in sites}
    valid = set(pics) | set(known.values())  # a file row may also name an existing site (no new catalog entry)
    seen, canonical = set(), {}
    for r in _load(FILES_CANONICAL):
        k = (r.get("site"), r.get("title"))
        if k not in canonical:  # first row wins, as in the 236c merge
            canonical[k] = _canon_norm(r)
    for r in files:
        sid = r.get("site")
        if sid not in valid:
            problems.append(f"file row names a site that is neither staged nor existing: {sid!r} ({r.get('title')!r})")
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
    code, text = evidence.check(FILES_US_CITIES, NO_BOOKS, catalog=EXTRAS_US_CITIES)
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
    """Write tests/golden/src_us_cities_sample.json: the staged extras, files and classified rows,
    normalized. Regenerate only for an intended change."""
    p = path or os.path.join(ROOT, "tests", "golden", "src_us_cities_sample.json")
    out = {"extras": _norm(_load(EXTRAS_US_CITIES)), "files": _norm(_load(FILES_US_CITIES)),
           "classified": _norm(_load(CLASSIFIED_US_CITIES))}
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
