"""Artists' aerial and bird's-eye views as sources of old pictures (task 213, GOAL.md point 5: artists' views
count as drawings as much as surveys - of Leonardo's 1502 aerial plan of Imola the owner: "should 100% be on our
map"): Leonardo's 1502 plan of Imola (Royal Collection RCIN 912284), Jacopo de' Barbari's 1500 view of Venice, and
the bird's-eye town views of Braun & Hogenberg's Civitates Orbis Terrarum (1572-1617) and Merian's Topographia
(1640s-1680s).

usage: src_artists.py --verify     re-verify every table QID (SITES + the book towns) against Wikidata
                                   (label, every P625 value, P373, P131, enwiki, the first name-search hit
                                   with coordinates - what record --live would resolve); copy the output into
                                   docs/lead_artists.md
       src_artists.py [--dry]      stage the image-level sources into this task's own staging files
       src_artists.py --check      offline (no network): join the staged files and run fit/evidence.py's check
       src_artists.py --golden     write tests/golden/src_artists_sample.json (the staged rows, normalized)

Staging writes only this task's files (append-only, idempotent on (site, title)); 211 consolidates them into the
canonical ones and builds the sites, 212 runs the model's fitting loop over them. Both image-level sites are
aerial-photograph ground (no open LiDAR here: FITKIT_GROUND=aerial, tools/fitkit.py) and their streets carry the
fit. The evidence field is hand-recorded: `record --live` resolves the caption's place by name search, and for
Venice the first search hit with coordinates is the Los Angeles neighborhood (Q773853, ~9900 km away) - the
hand record stores the verified resolution instead, and check passes offline from the stored fields. For Imola
the live route resolves the right QID (Q50195's P625 is the correct city point), but the hand record pins the
sheet's own centre - the walled old town - rather than the modern city point (docs/lead_artists.md). The
book-scale sources are worked through per-book files
(pipeline/books.py pattern), not staged here. The system python3 has no numpy (commons -> aw), so the live
commands run under .venv/bin/python; the module top stays stdlib-only.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

SITES_JSONL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
EXTRAS = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
EXTRAS_ARTISTS = os.path.join(ROOT, "data", "catalog", "extras_artists.jsonl")
FILES_ARTISTS = os.path.join(ROOT, "data", "commons", "files_artists.jsonl")
CLASSIFIED_ARTISTS = os.path.join(ROOT, "data", "commons", "classified_artists.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

# Hand-verified site facts (verified 2026-10-11, --verify re-checks; docs/lead_artists.md records the checked date
# and the trap notes). id = slug + "-" + qid-lower (the pipeline/sources.py rule); region is the display country
# (build_catalog.REGION_NAME has no "italy" key yet - task 214 adds it, until then make_site shows "US");
# kind "town" = 2000 m box (build_catalog.BOX). The place string is composed by hand from P131 + country (P131
# gives the province: Imola's Bologna, Venice's Venice-province variants). A picture of a site whose QID is
# already in the catalog gets a picture row for that existing site id (known_sites()), never a new catalog entry.
SITES = {
    # The site point is the walled old town's centre (Piazza del Duomo, OSM 44.3535 N 11.7112 E) - where the
    # sheet's view is centred (the walled town with the Rocca Sforzesca at its edge, the Santerno beyond).
    # Q50195's P625 is the correct modern city point (enwiki 44\u00b021'11"N 11\u00b042'53"E agree), 0.27 km east;
    # the prep's earlier "44.245 N 12.367 E centre / bad P625 53 km NW" reading was wrong (that point is Cervia).
    "Q50195": dict(id="imola-q50195", name="Imola", lon=11.7112, lat=44.3535,
                   place="Emilia-Romagna, Italy", region="Italy", kind="town",
                   wikipedia="https://en.wikipedia.org/wiki/Imola", cat="Imola",
                   p625=(11.714722, 44.353056),
                   note="no open LiDAR here: aerial-photograph ground (FITKIT_GROUND=aerial); the walled town's "
                        "street grid, the Santerno crossing, the Rocca Sforzesca and church footprints carry the fit"),
    "Q641": dict(id="venice-q641", name="Venice", lon=12.331944, lat=45.439722,
                 place="Veneto, Italy", region="Italy", kind="town",
                 wikipedia="https://en.wikipedia.org/wiki/Venice", cat="Venice",
                 p625=(12.331944, 45.439722),  # = the table point: Q641's P625 is the sane city point
                 note="the 1500 woodcut spans the whole lagoon city (~8 km) against the 2000 m town box: the fit "
                      "is likely to end a review item (212), not a failure of this task"),
}

# Image-level sources: one row per staged picture (file title, site QID, the name the plan list shows, optional
# per-file facts). A file that is not staged gets its reason in docs/lead_artists.md (a documented drop beats a
# guessed row): the "Google Art Project" scans of both sheets fail commons.keep() (the "google" NO rule is a
# harvest heuristic against map screenshots - and commons.rows() would re-drop them after 211's merge anyway);
# the NGA "block" files are detail crops of Barbari's woodcut, not separate pictures; RCIN 912686 (recto
# sketches) and "Imola 1705.jpg" are different works.
# Documented drops (verified live 2026-10-11, one paced commons.info run; full verdicts in docs/lead_artists.md):
# "File:Leonardo da vinci, Town plan of Imola.jpg" (1030x774, PD, circa 1502) is ANOTHER SCAN OF THE SAME RCIN
# 912284 sheet (same view, walls, river, margin notes) - a second row for the same picture adds nothing;
# "File:...RCIN 912686, Recto Sketches..." (1517x2000 portrait, PD, undated) is a different work (the measured
# survey sketches the sheet was made from); "File:Imola 1705.jpg" (942x710, PD, 1705, Antonio Ferri) is a flat
# plan by another hand from another century - not one of this task's four GOAL sources.
LEONARDO_IMOLA = [
    ("File:Leonardo da Vinci - RCIN 912284, A map of Imola 1502.jpg", "Q50195", "Imola",
     dict(date="1502")),  # the file page has no DateTimeOriginal (upload 2020): the known drawing date, noted
]
BARBARI_VENICE = [
    ("File:(Venice) View of Venice by Jacopo de' Barbari - Museo Correr.jpg", "Q641", "Venice",
     dict()),  # DateTimeOriginal 1500 on the file page
]

# Book-scale leads (confirmed on the Internet Archive in the prep 2026-10-10): at most a few hand-verified
# towns per book. The per-book files (data/books/triage/<ia>.*, data/books/lists/<ia>.json) are written only
# after those exact paths are added to this task's Touches line; the books.py:BOOKS entry is a
# shared-module change - file a task for it, never write it here. Liber secundus is fully worked (213a: triage
# A/F + the hand list); the other five items are 216/217's follow-on scope.
#
# The seven hand-verified towns of Liber secundus (BOOKS["civitates"]["sites"]): every QID verified against
# its label, every P625 value, P373, P131, the enwiki article and the first name-search hit with coordinates -
# never name-search alone (checked 2026-10-11, --verify re-checks; the full fact sheet and the search-trap
# notes are in docs/lead_artists.md). The table point is the verified P625 city point (the book's views centre
# on the walled old towns, within a few km - recorded per town in the lead doc). 216 takes its cite strings
# from the lead doc; 217 takes these QIDs to match the book-index rows to the catalog. The keys run in the
# book's plate order: fig 85 Brussels, 98 Antwerp, 193/194 Vienna, 198/199 Milan, 201/202 Venice, 205/206
# Florence, 209 Rome.
BOOKS = {
    "civitates": dict(years="1572-1617", ia=["civitatesorbiste00brau", "ARes73114", "ARes73115",
                                            "17095748888888bsb-00105587"],
                      sites={
                          # fig 85 BRVXELLA - data trap: the enwiki "Brussels" article is the region (Q240); the
                          # city is Q239 ("City of Brussels"), P373 "Brussels (municipality)".
                          "Q239": dict(name="Brussels", lon=4.351666666666667, lat=50.846666666666664,
                                       place="Brussels-Capital, Belgium",
                                       wikipedia="https://en.wikipedia.org/wiki/City_of_Brussels",
                                       cat="Brussels (municipality)"),
                          # fig 98 ANVERPIA - the title leaf calls it "pars Flandriae".
                          "Q12892": dict(name="Antwerp", lon=4.3997222222222225, lat=51.221111111111114,
                                        place="Flanders, Belgium",
                                        wikipedia="https://en.wikipedia.org/wiki/Antwerp",
                                        cat="Antwerp"),
                          # fig 193/194 VIENNA AVSTRIAE - a federal state; the modern P131 is the country itself.
                          "Q1741": dict(name="Vienna", lon=16.3725, lat=48.208333333333336,
                                        place="Austria",
                                        wikipedia="https://en.wikipedia.org/wiki/Vienna",
                                        cat="Vienna"),
                          # fig 198/199 MEDIOLANVM (the fold-out).
                          "Q490": dict(name="Milan", lon=9.19, lat=45.466944444444,
                                       place="Lombardy, Italy",
                                       wikipedia="https://en.wikipedia.org/wiki/Milan",
                                       cat="Milan"),
                          # fig 201/202 VENETIA (the fold-out, a view on both sides) - also the Barbari staged site.
                          "Q641": dict(name="Venice", lon=12.331944, lat=45.439722,
                                       place="Veneto, Italy",
                                       wikipedia="https://en.wikipedia.org/wiki/Venice",
                                       cat="Venice"),
                          # fig 205/206 FLORENTIA.
                          "Q2044": dict(name="Florence", lon=11.254166666667, lat=43.771388888889,
                                       place="Tuscany, Italy",
                                       wikipedia="https://en.wikipedia.org/wiki/Florence",
                                       cat="Florence"),
                          # fig 209 ROMA.
                          "Q220": dict(name="Rome", lon=12.482777777778, lat=41.893055555556,
                                       place="Lazio, Italy",
                                       wikipedia="https://en.wikipedia.org/wiki/Rome",
                                       cat="Rome"),
                      }),
    "merian": dict(years="1640s-1680s",
                  ia=["topographiahelve00zeil",
                      "rcin.org.pl.WA51_13719_PANB665-r1642_Topographia-Helvetia_152915"]),
}

SOURCES = {
    "leonardo_imola": dict(rows=LEONARDO_IMOLA, kind="town", p="birdseye",
                           label="{name}, aerial plan by Leonardo da Vinci (1502)"),
    "barbari_venice": dict(rows=BARBARI_VENICE, kind="town", p="birdseye",
                           label="{name}, bird's-eye view by Jacopo de' Barbari (1500)"),
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


def table_sites():
    """{qid: site facts} over the SITES table and the book towns (SITES wins a clash: Q641 Venice is both a
    staged site and a book town)."""
    out = {}
    for b in BOOKS.values():
        out.update(b.get("sites", {}))
    out.update(SITES)
    return out


def verify_qids():
    """Re-verify every table QID (the SITES table and the book towns) against Wikidata (paced) and print the
    facts for the lead doc: the label, every P625 value (flagged when >50 km from the table's site point),
    P373, P131 (with labels), the enwiki title, and the first name-search hit with coordinates (what
    record --live would resolve for the caption route)."""
    import evidence  # hav_m (the fit/ sibling; needs numpy, run under .venv)
    c = _commons()
    table = table_sites()
    qids = sorted(table)
    d = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(qids), "props": "claims|sitelinks|labels", "languages": "en"})
    ents = d.get("entities", {})
    p131s = sorted({i for q in qids for i in _ids(ents.get(q, {}).get("claims", {}).get("P131", []))})
    labels = {}
    for i in range(0, len(p131s), 50):  # wbgetentities takes at most 50 ids per call
        d2 = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(p131s[i:i + 50]), "props": "labels", "languages": "en"})
        labels.update({k: v.get("labels", {}).get("en", {}).get("value") for k, v in d2.get("entities", {}).items()})
    print(f"checked {now()} - {len(qids)} QIDs (Wikidata)")
    for qid in qids:
        e = ents.get(qid) or {}
        cl = e.get("claims", {})
        s = table[qid]
        print(f"  {qid}  {e.get('labels', {}).get('en', {}).get('value')!r}")
        p625 = [(v["longitude"], v["latitude"]) for v in _datavalues(cl.get("P625", [])) if v]
        print(f"      P625: {p625}  (table site point: {s['lon']}, {s['lat']})")
        for lon, lat in p625:
            dist = evidence.hav_m(lon, lat, s["lon"], s["lat"])
            if dist > 50e3:
                print(f"      FLAG: a P625 is {dist / 1000:.0f} km from the table's point (the recorded trap; "
                      f"the table point stands)")
        print(f"      P373: {_datavalues(cl.get('P373', []))}  (table cat: {s.get('cat')!r})")
        print(f"      P131: {[(labels.get(i), i) for i in _ids(cl.get('P131', []))]}  (table place: {s.get('place')!r})")
        print(f"      enwiki: {e.get('sitelinks', {}).get('enwiki', {}).get('title')!r}  "
              f"(table wikipedia: {s.get('wikipedia')!r})")
        sr = c.get(c.WD, {"action": "wbsearchentities", "search": s["name"], "language": "en", "limit": "5"})
        ids = [x["id"] for x in sr.get("search", [])]
        if ids:
            d3 = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(ids), "props": "claims|labels",
                              "languages": "en"})
            for q in ids:
                hits = [(v["longitude"], v["latitude"]) for v in _datavalues(d3.get("entities", {}).get(q, {}).get("claims", {}).get("P625", [])) if v]
                if hits:
                    lon, lat = hits[0]
                    dist = evidence.hav_m(lon, lat, s["lon"], s["lat"])
                    flag = "" if dist <= 50e3 else f"   <- TRAP: {dist / 1000:.0f} km, the live record would store a conflict (kind none)"
                    lab = d3["entities"][q].get("labels", {}).get("en", {}).get("value", "")
                    print(f"      search {s['name']!r}: first hit with P625 is {q} {lab!r} ({lon}, {lat}){flag}")
                    break
    return 0


def evidence_for(qid, site):
    """The hand-recorded caption_coords tie, in the key order of fit/evidence.py's caption_route(): the place
    named is the site's own verified name (the file title prints it) and the stored coordinates are the verified
    resolution - record --live would take the first name-search hit instead, which is the trap here."""
    return {"rec": "evidence/1", "kind": "caption_coords", "checked": now(),
            "named_place": site["name"], "place_qid": qid, "place_label": site["name"],
            "place_lon": site["lon"], "place_lat": site["lat"],
            "site_lon": site["lon"], "site_lat": site["lat"], "dist_m": 0.0}


def _site_row(qid, site, name):
    row = {"id": site["id"], "qid": qid, "name": site["name"], "lon": site["lon"], "lat": site["lat"],
           "region": site["region"], "kind": site["kind"], "aerial_ok": True,
           "source": f"fit/src_artists.py {name}"}
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
    """Stage the image-level sources into this task's own files (append-only, idempotent on (site, title)).
    Drift fails loud: a title that vanished from Commons, or a file commons.keep() would drop."""
    c = _commons()
    known = known_sites()
    have = {(r.get("site"), r.get("title")) for r in _load(FILES_ARTISTS) + _load(CLASSIFIED_ARTISTS)}
    staged_ids = {s["id"] for s in _load(EXTRAS_ARTISTS)}
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
            if not c.keep(title, m):
                raise SystemExit(f"commons.keep() would drop {title!r}: fix the table or record the drop "
                                 f"in docs/lead_artists.md")
            want = x.get("date")
            if want and c.year_of(title, m) != c.year_of(title, {"date": want}):
                m = dict(m, date=want, date_commons=m.get("date"))  # a scan whose page lost the drawing's date
            f = {"site": sid, "qid": qid, "title": title, "year": c.year_of(title, m), "wd_plan": False,
                 "cat": site.get("cat"), "name": src["label"].format(name=label),
                 "by": f"fit/src_artists.py {name}", **m}
            f["evidence"] = evidence_for(qid, site)
            new_files.append(f)
            p = {"p_plan": 0.0, "p_birdseye": 0.0, "p_photo": 0.0}
            p[f"p_{src['p']}"] = 1.0
            new_cls.append({"site": sid, "title": title, **p, "by": "hand"})
    print(f"staged: {len(new_sites)} new sites, {len(new_files)} new pictures")
    for s in new_sites:
        print("   ", s["id"], s["lon"], s["lat"], s.get("place"))
    if to_build:
        print("build (211):", ",".join(to_build))
    if dry:
        return
    _append(EXTRAS_ARTISTS, new_sites)
    _append(FILES_ARTISTS, new_files)
    _append(CLASSIFIED_ARTISTS, new_cls)


def check_staged():
    """Offline (no network): join the staged files (every file row names a staged or existing site; a staged
    QID or id is a problem only when it resolves to a DIFFERENT site - the module's own rows already merged
    by 211 are a no-op, not a collision; every staged site has a picture; (site, title) unique; a staged row
    whose key is in the canonical files.jsonl must be identical to the canonical row under the merge's
    identity rule (211's first-row-wins merge) - a same-key different row still fails loud; classified rows
    1:1 with the file rows) and run fit/evidence.py's check over the staged rows. Returns the exit code
    (0 iff no problem and no FAIL)."""
    import evidence
    files = _load(FILES_ARTISTS)
    sites = _load(EXTRAS_ARTISTS)
    cls = _load(CLASSIFIED_ARTISTS)
    known = known_sites()
    problems = []
    staged_ids = {s["id"] for s in sites}
    known_ids = {}  # id -> the set of known QIDs that hold it
    for qid, sid in known.items():
        known_ids.setdefault(sid, set()).add(qid)
    # after 211's merge the module's own staged sites sit in the canonical extras (known): a staged id/QID
    # is a problem only when it resolves to a DIFFERENT site (the pre-merge clash protection); a self
    # reference (the same site via the catalog, or its own merged row) is a no-op
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
        if k not in canonical:  # first row wins, as in the 211 merge
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
    code, text = evidence.check(FILES_ARTISTS, NO_BOOKS, catalog=EXTRAS_ARTISTS)
    print(text)
    return 1 if problems else code


def _canon_norm(r):
    """Row identity under the 211 merge rule (the same norm fit/merge.py uses on the line): key order and
    ASCII escaping don't matter, content does."""
    return json.dumps(r, sort_keys=True, ensure_ascii=False)


def _norm(rows):
    """The rows for the golden file: keys are sorted by the dump, "checked" and "date_commons" normalized (they
    vary with the staging date)."""
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
    """Write tests/golden/src_artists_sample.json: the staged extras, files and classified rows, normalized.
    Regenerate only for an intended change."""
    p = path or os.path.join(ROOT, "tests", "golden", "src_artists_sample.json")
    out = {"extras": _norm(_load(EXTRAS_ARTISTS)), "files": _norm(_load(FILES_ARTISTS)),
           "classified": _norm(_load(CLASSIFIED_ARTISTS))}
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
