"""Bird's-eye and panoramic views of US cities (task 236b, GOAL.md point 5: artists' aerial and
bird's-eye views count as much as surveys): the hand-checked file -> QID table for the Library of
Congress "Panoramic Maps" collection (about 1,500 US bird's-eye views, 1847-1929, public domain; this
machine cannot reach loc.gov, so the files are fetched from their Wikimedia Commons mirrors, the
project's established pattern) - the four owner-named cities first, the way 236a staged its plans:
New York (the 1874 Bachmann view, the 1879 Will L. Taylor sheet and the 1907 Ohmann metro-wide view),
Washington DC (the 1883 Sachse sheet, the 1886 B.H. Warner & Co. sheet and the 1921 Olsen view), San
Francisco (the 1854 Henry Bill view - the oldest staged view of the city - the 1868 Goddard view,
the 1878 Parsons/Currier & Ives view and the 1914 C. Merriman Peter sheet) and Nashville (the 1897
Tennessee Centennial Exposition view), then more US cities, each a new site of its own - staged into
this task's own staging files; 236c consolidates the staged rows into the canonical data and builds
the sites.

The four owner-named cities use 236a's site ids (new-york-q60, washington-q61, san-francisco-q62,
nashville-q23197 - data/catalog/extras_us_cities.jsonl, read-only here): never two sites for one
QID, agreed through the catalog slug rule. This module's own extras file is only for cities 236a did
not stage. Bird's-eye views are oblique, so a row's label records its apparent angle where the fit
order depends on it (near-vertical views fit best; the 2000 m town-box overshoots are likely review
items, the NY 1811 / DC ring precedent in docs/lead_us_cities.md).

usage: src_us_birdseye.py --verify     re-verify every table QID (SHARED_SITES + SITES) against Wikidata
                                   (label, every P625 value, P373, P131, enwiki, the first name-search hit
                                   with coordinates - what record --live would resolve); copy the output into
                                   docs/lead_us_birdseye.md
       src_us_birdseye.py [--dry]      stage the sources into this task's own staging files
       src_us_birdseye.py --check      offline (no network): join the staged files and run fit/evidence.py's check
       src_us_birdseye.py --golden     write tests/golden/src_us_birdseye_sample.json (the staged rows, normalized)

Staging writes only this task's files (append-only, idempotent on (site, title)); 236c consolidates them
into the canonical ones and builds the new sites. A row's evidence field is hand-recorded
caption_coords: the caption names the city and the stored coordinates are the verified site point -
record --live would take the first name-search hit instead, and the stage fails loud when the caption
does not print the city. A scan whose file page lost the drawing's date (or printed only its
copyright year) gets the known drawing/publication date on the row and the page value kept as
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
EXTRAS_BIRDS = os.path.join(ROOT, "data", "catalog", "extras_us_birdseye.jsonl")
FILES_BIRDS = os.path.join(ROOT, "data", "commons", "files_us_birdseye.jsonl")
CLASSIFIED_BIRDS = os.path.join(ROOT, "data", "commons", "classified_us_birdseye.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

# The four owner-named cities 236a staged (data/catalog/extras_us_cities.jsonl, read-only here):
# QID -> (236a's site id, the short name the file captions print). The staged file rows must carry
# 236a's site id - never a second site for one QID (the catalog slug rule) - and this table is
# cross-checked against 236a's rows in every run: a drift (236c rebuilt the site under another id,
# 236a's row vanished) fails loud. The point and the full name come from 236a's row (verified there,
# --verify re-checks the QID against Wikidata too).
SHARED_SITES = {
    "Q60": ("new-york-q60", "New York"),
    "Q61": ("washington-q61", "Washington"),
    "Q62": ("san-francisco-q62", "San Francisco"),
    "Q23197": ("nashville-q23197", "Nashville"),
}

# New cities this task stages (only cities 236a does not stage - check data/catalog/
# extras_us_cities.jsonl on main before adding one): hand-verified site facts, the pipeline/sources.py
# slug rule (id = slug + "-" + qid-lower), region "United States" (REGION_NAME in
# pipeline/build_catalog.py carries the display name), kind "town" = 2000 m box, aerial_ok true
# (aerial-photograph ground: no open LiDAR over a built-up city, bare-earth LiDAR erases the streets).
# The note records the view's apparent angle so 236c/the matcher can order oblique views (the task
# Notes). Filled in batch 2+ (>= 25 cities total with the four shared above).
SITES = {}

# New York (checked live 2026-10-14; per-file STAGED/DROP verdicts in docs/lead_us_birdseye.md). The
# 1674 Vardel view is a genuine bird's-eye view but outside the collection's 1847-1929 range (recorded,
# not staged). The 1907 Ohman view is metro-wide: its sheet spans far beyond the 2000 m town box, so
# its fit is likely to end a review item (the NY 1811 / DC ring precedent).
BACHMANN_1874 = [
    # the classic near-vertical harbour view of the island, "NEW YORK" printed on the sheet
    ("File:New York - drawn by J. Bachmann ; print by G. Schlegel, 97 William St. N.Y. LCCN98508526.jpg",
     "Q60", "New York", dict()),
]
TAYLOR_1879 = [
    # the whole island in portrait with the full street grid, drawn by Will L. Taylor, published by
    # Galt & Hoy; File:Taylor map of New York.jpg (12901x22870, the DPLA scan) is the SAME sheet - one
    # row per sheet (the Ratzer precedent), the higher-id LOC scan is staged
    ("File:The city of New York. LOC 75694818.jpg", "Q60", "New York", dict()),
]
OHMANN_1907 = [
    # metro-wide view (Manhattan, the Bronx, Brooklyn, Jersey City) - the sheet spans far beyond the
    # 2000 m town box: a review item (the 1811-sheet precedent), noted on the site's 236a row
    ("File:View of the city of New York and vicinity LOC 78692903.jpg", "Q60", "New York", dict()),
]

# Washington DC (checked live 2026-10-14). DROPS with reasons (lead doc): the 1871 Sachse
# "View of Washington City" (LOC 90683459) - a pictorial view, the Capitol the subject, the city a
# painted background with no surveyed grid at fit scale; the 1861 Bohn "seat of war on the Potomac"
# (LOC 88694227) - a regional view in which Washington is a small part of the frame; the 1866
# "Capitol East Front" - a building close-up, not a city view; the 1861 balloon view (1536x1040) -
# too small to fit (the Butler precedent).
SACHSE_1883 = [
    # the city plus Georgetown, the title printed on the sheet
    ("File:The national capital, Washington City, D.C. LOC 75694904.jpg", "Q61", "Washington", dict()),
]
WARNER_1886 = [
    # prepared by A. G. Gedney for B. H. Warner & Co., copyrighted and published 1st July 1886: the
    # whole city and suburbs, the diagonal avenues and the block-by-block grid
    ("File:B.H. Warner & Co.'s Map showing a bird's-eye view of the city of Washington and suburbs - "
     "locating the public buildings and places of interest LOC 87693417.jpg", "Q61", "Washington", dict()),
]
OLSEN_1921 = [
    # the whole city, the title printed on the sheet (the latest of the collection's DC views staged)
    ("File:Washington, the beautiful capital of the nation LOC 78695113.jpg", "Q61", "Washington", dict()),
]

# San Francisco (checked live 2026-10-14). DROPS with reasons (lead doc): the 1850 hilltop view
# (LCCN2006677456) and the 1884 Bosqui "Yerba Buena in 1846-7" - pictorial views, the city small in
# the frame; the 1906 earthquake aerials (Chadwick/Lawrence) - photographs, not drawings (236a's HABS
# photo precedent); the 1878 Burgess oil on canvas - a painting. The IA Goddard scan and the NYPL
# scan are the SAME sheet as LOC 75693101; the LCCN90715988 pair and the two DPLA/Geographicus Bill
# scans are smaller scans of their staged sheet - one row per sheet each.
BILL_1854 = [
    # the oldest staged view of the city: drawn in 1852 (the sheet says "Drawn according to Act of
    # Congress in the year 1852"), the sheet titled "SAN FRANCISCO. 1854", published for the History
    # of the world by Henry Bill, New York - the oblique hilltop view, the old town a third of the
    # frame, the street grid legible inside the built-up mass; staged from the largest scan (DPLA,
    # 7000x4156; the two Geographicus scans are the same sheet)
    ("File:San Francisco. 1854 (published for the History of the world) - DPLA - Original.jpg",
     "Q62", "San Francisco", dict()),
]
GODDARD_1868 = [
    # the classic 1868 Goddard view from the hills: the whole peninsula and the bay, drawn by George
    # H. Goddard, lith. Britton & Rey, published by Snow & May; the IA and NYPL scans are the same
    # sheet (one row)
    ("File:(Bird's eye view of San Francisco) LOC 75693101.jpg", "Q62", "San Francisco", dict()),
]
PARSONS_1878 = [
    # from the bay looking south-west, drawn by C. F. Parsons, published by Currier & Ives
    ("File:The city of San Francisco. Birds eye view from the bay looking south-west. LOC 75693104.jpg",
     "Q62", "San Francisco", dict()),
]
PETER_1914 = [
    # the pre-1915-exposition whole peninsula, dense grid plus an index, drawn by C. Merriman Peter
    ("File:1914 San Francisco Birds Eye Map by Peter.jpg", "Q62", "San Francisco", dict()),
]

# Nashville (checked live 2026-10-14): the thinnest city. The 1897 exposition view (Schreiner Park,
# the Capitol at the left) depicts PART of the city - the park and its approaches, not a street grid
# - so its fit leans on the Capitol hill, the park bounds and the approach roads; it is the only
# Nashville bird's-eye view that survived the gate. The three Fletcher 1864 Fort Negley views
# (LCCN2003655670/89/90) are DROPS: fort close-ups with no city grid, and 236a found no fort-only
# plan, so no fort site exists to attach them to (their record is in the lead doc).
CENTENNIAL_1897 = [
    # the Tennessee Centennial Exposition in Schreiner Park, 1897, printed by The Henderson Litho.
    # Co., Cincinnati; the sheet's banner says 1897 but the Commons page dates the copyright 1896,
    # so the known drawing/publication year is on the row and the page value kept as date_commons
    # (the Zwolle precedent)
    ("File:Tennessee Centennial Exposition, Nashville, Tennessee, 1897. LOC 77696328.jpg",
     "Q23197", "Nashville", dict(date="1897")),
]

SOURCES = {
    "bachmann_1874": dict(rows=BACHMANN_1874, p="birdseye",
                          label="{name}, the Bachmann bird's-eye view (1874)"),
    "taylor_1879": dict(rows=TAYLOR_1879, p="birdseye",
                        label="{name}, the Will L. Taylor bird's-eye view (1879)"),
    "ohmann_1907": dict(rows=OHMANN_1907, p="birdseye",
                        label="{name}, the Ohmann & Co. bird's-eye view (1907, metro-wide)"),
    "sachse_1883": dict(rows=SACHSE_1883, p="birdseye",
                        label="{name}, the A. Sachse & Co. bird's-eye view (1883)"),
    "warner_1886": dict(rows=WARNER_1886, p="birdseye",
                        label="{name}, the B.H. Warner & Co. bird's-eye view (1886)"),
    "olsen_1921": dict(rows=OLSEN_1921, p="birdseye",
                       label="{name}, the Olsen bird's-eye view (1921)"),
    "bill_1854": dict(rows=BILL_1854, p="birdseye",
                      label="{name}, the Henry Bill bird's-eye view (1854, drawn 1852)"),
    "goddard_1868": dict(rows=GODDARD_1868, p="birdseye",
                         label="{name}, the Goddard bird's-eye view (1868)"),
    "parsons_1878": dict(rows=PARSONS_1878, p="birdseye",
                         label="{name}, the Parsons/Currier & Ives bird's-eye view (1878)"),
    "peter_1914": dict(rows=PETER_1914, p="birdseye",
                       label="{name}, the C. Merriman Peter bird's-eye view (1914)"),
    "centennial_1897": dict(rows=CENTENNIAL_1897, p="birdseye",
                            label="{name}, the Tennessee Centennial Exposition bird's-eye view (1897)"),
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


def _shared_rows():
    """236a's staged site rows for the owner-named cities (READ ONLY): {qid: row}."""
    return {s["qid"]: s for s in _load(EXTRAS_US_CITIES) if s.get("qid") in SHARED_SITES}


def _shared_site(qid):
    """The 236a-staged site for a shared QID, cross-checked: the id must match SHARED_SITES (never
    two site ids for one QID) and 236a's row must still exist. The point and the full name come from
    236a's row (verified there); the short caption name comes from this module's table (236a's
    extras row does not store it)."""
    ref_id, named = SHARED_SITES[qid]
    row = _shared_rows().get(qid)
    if row is None:
        raise SystemExit(f"shared site {qid}: 236a has no staged row in data/catalog/extras_us_cities.jsonl")
    if row.get("id") != ref_id:
        raise SystemExit(f"shared site {qid}: 236a's staged id {row.get('id')!r} differs from {ref_id!r} - "
                         f"never two sites for one QID")
    return dict(qid=qid, id=row["id"], name=row["name"], named=named, lon=row["lon"], lat=row["lat"],
                place=row.get("place"), wikipedia=row.get("wikipedia"))


def known_sites():
    """{qid: site id} over the built sites, the catalog, the extras AND 236a's US-cities extras (a
    source never makes a second site; 236a's file is read here only, never written)."""
    out = {}
    for p in (SITES_JSONL, EXTRAS, EXTRAS_US_CITIES):
        for s in _load(p):
            if s.get("qid") and s["qid"] not in out:
                out[s["qid"]] = s["id"]
    for s in json.load(open(WEB_SITES, encoding="utf-8"))["sites"]:
        if s.get("qid") and s["qid"] not in out:
            out[s["qid"]] = s["id"]
    return out


def _site_table():
    """The full site table for this module: the shared cities (236a's rows, cross-checked) plus the
    new cities this task stages, keyed by QID. Each value carries id/name/named/lon/lat (verify and
    stage both read from here)."""
    table = {}
    for qid in SHARED_SITES:
        table[qid] = _shared_site(qid)
    for qid, s in SITES.items():
        table[qid] = dict(s, qid=qid)
    return table


def verify_qids():
    """Re-verify every table QID against Wikidata (paced) and print the facts for the lead doc: the label,
    every P625 value (flagged when >50 km from the table's site point), P373, P131 (with labels), the
    enwiki title, and the first name-search hit with coordinates (what record --live would resolve for the
    caption route). The four shared QIDs were first verified by 236a (docs/lead_us_cities.md); this is the
    re-check that 236b's own table stands on."""
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
        print(f"  {qid}  {e.get('labels', {}).get('en', {}).get('value')!r}  (site id: {s['id']}, "
              f"{'shared (236a)' if qid in SHARED_SITES else 'new (this task)'})")
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
           "source": f"fit/src_us_birdseye.py {name}"}
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
    does not print the city, a shared site whose 236a row drifted, a QID in neither table. Rows of the
    four shared cities use 236a's site ids as-is (no new site row); new cities get one extras row
    each, here."""
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
            if qid in SHARED_SITES:
                site = _shared_site(qid)  # fails loud on drift; the point comes from 236a's row
            elif qid in SITES:
                site = dict(SITES[qid], qid=qid)
            else:
                raise SystemExit(f"row {title!r}: QID {qid} in neither SHARED_SITES nor SITES")
            sid = known.get(qid) or site["id"]
            if qid not in SHARED_SITES and known.get(qid) is None and sid not in staged_ids:
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
                                 f"in docs/lead_us_birdseye.md")
            ev = evidence_for(qid, site, title, m)
            if ev is None:
                raise SystemExit(f"{title!r}: the caption does not print "
                                 f"{site.get('named') or site['name']!r} - pick a file that does, or record "
                                 f"the drop in docs/lead_us_birdseye.md")
            f = {"site": sid, "qid": qid, "title": title, "year": c.year_of(title, m), "wd_plan": False,
                 "cat": None, "name": src["label"].format(name=label),
                 "by": f"fit/src_us_birdseye.py {name}", **m}
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
    including the four shared cities via 236a's read-only extras file; a staged QID or id is a problem
    only when it resolves to a DIFFERENT site - the module's own rows already merged by 236c are a
    no-op, not a collision; every NEW staged site has a picture; (site, title) unique; a staged row
    whose key is in the canonical files.jsonl must be identical to the canonical row under the merge's
    identity rule (the first-row-wins merge) - a same-key different row still fails loud; classified
    rows 1:1 with the file rows) and run fit/evidence.py's check over the staged rows. Returns the
    exit code (0 iff no problem and no FAIL)."""
    import evidence
    files = _load(FILES_BIRDS)
    sites = _load(EXTRAS_BIRDS)
    cls = _load(CLASSIFIED_BIRDS)
    known = known_sites()  # includes 236a's file: the four shared ids are "existing" sites
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
    valid = set(pics) | set(known.values())  # the shared cities' ids come from known (236a's file)
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
    """Write tests/golden/src_us_birdseye_sample.json: the staged extras, files and classified rows,
    normalized. Regenerate only for an intended change."""
    p = path or os.path.join(ROOT, "tests", "golden", "src_us_birdseye_sample.json")
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
