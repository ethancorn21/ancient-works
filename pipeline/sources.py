"""Old plans and bird's-eye views from named sources, each tied to a site by hand (Ethan 2026-10-10: widen the map with
Mackenzie's 1897 castle plans, Van Deventer's 1550s town plans and Kip & Knyff's 1707 views of country houses).

usage: sources.py <source> [--dry]        source: mackenzie | deventer | kip

Each source is a table of Commons file -> Wikidata item. The QIDs were checked by hand: a name search alone gives the
town for "Barnard Castle", the village for "Richard's Castle", the 19th-century house for "Scotney Castle" and a
Yorkshire namesake for "Duffield Castle". For every row:
  - the site: one already built or in the catalog with the same QID, else a new row in data/catalog/extras.jsonl
    (kind castle / town / garden; "aerial_ok": the picture is reason enough to build it, LiDAR or not);
  - the picture: a row in data/commons/files.jsonl (Commons metadata, as commons.py harvest writes it, plus "name",
    the label the plan list shows) and a hand classification in data/commons/classified.jsonl ("by": "hand").
Prints the new site ids; then: build_catalog.py --ids <them>, commons.py thumbs, tools/export_plans.py.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402
import commons  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "data", "catalog")
WD = "https://www.wikidata.org/w/api.php"

_BL = "File:{} of 'The Castles of England- their story and structure ... With ... illustrations and ... plans' ({}).jpg"
# Mackenzie, J. D. (1897) The Castles of England: their story and structure. Plans from the British Library's Flickr scans
# (page, Flickr id) and from separately uploaded crops. Already harvested for their sites before (not repeated here):
# Dudley, Barnard, Eaton Socon, Clun, Berkhamsted, Fotheringhay. Left out: the photographs (Allington, Corfe, Caister,
# Tattershall), page 121 (Herstmonceux's upper floor), page 212 (a five-towered castle with no caption).
MACKENZIE = [
    ("File:Plan of Caister Castle (1897).jpg", "Q5017844", "england", "Caister Castle"),
    ("File:Plan of Leeds Castle (1897).jpg", "Q746876", "england", "Leeds Castle"),
    ("File:Plan of Norham Castle, (1897).jpg", "Q388705", "england", "Norham Castle"),
    ("File:Plan of Raby Castle (1897).jpg", "Q4583646", "england", "Raby Castle"),
    ("File:Plan of Taunton Castle (1897).jpg", "Q7688781", "england", "Taunton Castle"),
    (_BL.format(42, 11147323666), "Q5167493", "england", "Cooling Castle"),
    (_BL.format(87, 11242001186), "Q5435410", "england", "Farleigh Hungerford Castle"),  # no caption: "Danes Dyke", "Wilts"
    (_BL.format(106, 11240715314), "Q2968744", "wales", "Caldicot Castle"),
    (_BL.format(120, 11297436674), "Q2652207", "england", "Herstmonceux Castle"),
    (_BL.format(132, 11295498795), "Q17530343", "england", "Scotney Castle"),  # Old Scotney Castle, not the 1830s house
    (_BL.format(134, 11145759593), "Q17645407", "england", "Sedgwick Castle"),
    (_BL.format(135, 11146434133), "Q5583571", "england", "Goodrich Castle"),
    (_BL.format(145, 11296694235), "Q17650937", "england", "Richard's Castle"),
    (_BL.format(175, 11241133755), "Q576369", "england", "Ludlow Castle"),
    (_BL.format(188, 11244246185), "Q7618555", "england", "Stokesay Castle"),
    (_BL.format(207, 11148583904), "Q2600886", "england", "Oxford Castle"),  # "The fortress of Oxford"
    (_BL.format(231, 11242140515), "Q2969640", "england", "Lancaster Castle"),
    (_BL.format(252, 11147295504), "Q328595", "england", "Carisbrooke Castle"),
    (_BL.format(337, 11240694796), "Q2524183", "england", "Framlingham Castle"),
    (_BL.format(349, 11243227834), "Q614836", "england", "Carlisle Castle"),
    (_BL.format(356, 11147078984), "Q1049485", "england", "Castle Rising Castle"),
    (_BL.format(378, 11296515666), "Q1188983", "england", "Barnwell Castle"),
    (_BL.format(393, 11241707044), "Q3939808", "england", "Rockingham Castle"),
    (_BL.format(480, 11241748276), "Q6519156", "england", "Leicester Castle"),  # "Leicester in the seventeenth century"
    (_BL.format(528, 11146272565), "Q2968590", "england", "Bolsover Castle"),
    (_BL.format(533, 11147871174), "Q2073299", "england", "Duffield Castle"),  # Derbyshire
]
# Jacob van Deventer's town plans, drawn c. 1545-1565 for Charles V and Philip II (Commons "Maps by Jacob van Deventer",
# 70 town categories). A first six with full-size plans: three Dutch (AHN LiDAR), two Belgian, one French. The QID is the
# municipality (it carries the Wikipedia link); lon/lat put the box on the old town, which the municipality's point misses
# by up to 800 m (Gouda). "date" where Commons has only an upload or reproduction date (Gouda 2013, Zwolle's 1980 photo).
DEVENTER = [
    ("File:Map of Gouda by Jacob van Deventer.jpg", "Q84125", "netherlands", "Gouda",
     dict(lon=4.7105, lat=52.0117, date="circa 1560")),
    ("File:Plattegrond van J. van Deventer, reproductie uit album Rijksdienst voor de Monumenten Zorg te Zeist - Zwolle - 20228487 - RCE.jpg",
     "Q793", "netherlands", "Zwolle", dict(lon=6.0925, lat=52.5125, date="circa 1560")),
    ("File:1560 Kaart van Venlo door Jacob van Deventer.jpg", "Q9777", "netherlands", "Venlo", dict(lon=6.1725, lat=51.3705)),
    ("File:Damme, Belgium ; Deventer map.jpg", "Q323408", "belgium", "Damme", dict(lon=3.2815, lat=51.2510)),
    ("File:Binche - Deventer.jpg", "Q95121", "belgium", "Binche", dict(lon=4.1652, lat=50.4103)),
    ("File:Bergues - Deventer.jpg", "Q244934", "france", "Bergues", dict(lon=2.4342, lat=50.9686)),
]
# Kip & Knyff's bird's-eye views of country houses and their formal gardens (Britannia Illustrata 1707-09, Nouveau
# Theatre de la Grande Bretagne; Kip's later plates), the large scans only: most Britannia Illustrata files on Commons are
# 300-800 px, too small to lay over the ground. Picked where something fixed survives to fit by: the house (Hampton
# Court in Herefordshire, Chevening, Fairlawne, Burlington House), the garden's axes (Chiswick), or the park (Cassiobury, house gone 1927).
_YALE = "File:Jan Kip - {} - Yale Center for British Art.jpg"
KIP = [
    # the Rijksmuseum calls it "Gezicht op Hampton Court"; the caption says Hampton Court in Herefordshire, Lord Coningsby's
    # seat (Q1443802), not the palace on the Thames (built there by mistake first, 2026-10-10)
    ("File:Gezicht op Hampton Court, RP-P-1905-194.jpg", "Q1443802", "england", "Hampton Court, Herefordshire"),
    ("File:An engraving of Chevening by Johannes Kip (d.1722) after Thomas Badeslade (d.1742), published (in History of Kent) "
     "1719 by John Harris.jpg", "Q1070927", "england", "Chevening"),
    ("File:Cassiobury Park by Kip and Knyff.jpg", "Q5049456", "england", "Cassiobury House"),
    (_YALE.format("The House at Chiswick in the County of Middlesex one of the Seats of the Rt Hon Charles Boyle - B1977.14.18672"),
     "Q1074877", "england", "Chiswick House"),
    (_YALE.format("Fair Lawn in ye County of Kent - B2017.35.2"), "Q17530246", "england", "Fairlawne"),
    (_YALE.format("Burlington House in Piccadilly - B1977.14.17783"), "Q225471", "england", "Burlington House",
     dict(date="circa 1707")),  # Britannia Illustrata plate; Yale gives no date
]
SOURCES = {
    "mackenzie": dict(rows=MACKENZIE, kind="castle", p="plan", year=1897,
                      label="{name}, plan from Mackenzie, The Castles of England (1897)",
                      source="Mackenzie, J. D. (1897) The Castles of England: their story and structure (plan on Wikimedia Commons)"),
    "deventer": dict(rows=DEVENTER, kind="town", p="plan", year=None, label="{name}, town plan by Jacob van Deventer"),
    "kip": dict(rows=KIP, kind="garden", p="birdseye", year=None, label="{name}, bird's-eye view engraved by Johannes Kip"),
}


def wd(params):
    u = WD + "?" + urllib.parse.urlencode(dict(params, format="json"))
    with urllib.request.urlopen(urllib.request.Request(u, headers=aw.UA), timeout=60) as r:
        return json.load(r)


def items(qids):
    """{qid: {lon, lat, wiki, place}} from Wikidata (P625; enwiki link; the P131 'located in' label as the place)."""
    out, located = {}, {}
    for i in range(0, len(qids), 50):
        ents = wd({"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]), "props": "claims|sitelinks"})["entities"]
        for q, e in ents.items():
            c = e.get("claims", {})
            co = c["P625"][0]["mainsnak"]["datavalue"]["value"]
            t = e.get("sitelinks", {}).get("enwiki", {}).get("title")
            out[q] = {"lon": round(co["longitude"], 6), "lat": round(co["latitude"], 6),
                      "wiki": "https://en.wikipedia.org/wiki/" + t.replace(" ", "_") if t else None}
            p131 = c.get("P131", [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
            if p131:
                located[q] = p131
    ids = sorted(set(located.values()))
    labels = {}
    for i in range(0, len(ids), 50):
        ents = wd({"action": "wbgetentities", "ids": "|".join(ids[i:i + 50]), "props": "labels", "languages": "en"})["entities"]
        labels.update({k: v.get("labels", {}).get("en", {}).get("value") for k, v in ents.items()})
    for q, p in located.items():
        out[q]["place"] = labels.get(p)
    return out


def known_sites():
    """{qid: site id} over the built sites, the catalog and the extras (a source never makes a second site for a place)."""
    out = {}
    for path in (os.path.join(CAT, "sites.jsonl"), os.path.join(CAT, "extras.jsonl")):
        for l in open(path):
            if l.strip():
                r = json.loads(l)
                if r.get("qid"):
                    out[r["qid"]] = r["id"]
    for s in json.load(open(os.path.join(ROOT, "web", "data", "sites.json")))["sites"]:
        if s.get("qid"):
            out[s["qid"]] = s["id"]
    return out


def run(name, dry=False):
    src = SOURCES[name]
    rows = src["rows"]
    known = known_sites()
    wdi = items(sorted({r[1] for r in rows}))
    meta = commons.info([r[0] for r in rows])
    missing = [r[0] for r in rows if not (meta.get(r[0]) or {}).get("url")]
    if missing:
        raise SystemExit(f"not on Commons (title changed?): {missing}")
    fpath = os.path.join(commons.OUT, "files.jsonl")
    cpath = os.path.join(commons.OUT, "classified.jsonl")
    have = {(r.get("site"), r.get("title")) for r in (json.loads(l) for l in open(fpath))}
    built = {s["id"] for s in json.load(open(os.path.join(ROOT, "web", "data", "sites.json")))["sites"]}
    new_sites, new_files, new_cls, to_build = [], [], [], []
    for title, qid, region, label, *extra in rows:
        x = extra[0] if extra else {}
        sid = known.get(qid)
        if sid is not None and sid not in built and sid not in to_build:
            to_build.append(sid)  # in the catalog, never built (Richard's Castle)
        if sid is None:
            w = wdi[qid]
            sid = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") + "-" + qid.lower()
            row = {"id": sid, "qid": qid, "name": label, "lon": x.get("lon", w["lon"]), "lat": x.get("lat", w["lat"]), "region": region,
                   "kind": src["kind"], "aerial_ok": True, "source": f"pipeline/sources.py {name}"}
            if w.get("place"):
                row["place"] = w["place"]
            if x.get("box_m"):
                row["box_m"] = x["box_m"]
            if w.get("wiki"):
                row["wikipedia"] = w["wiki"]
            new_sites.append(row)
            to_build.append(sid)
            known[qid] = sid
        if (sid, title) in have:
            continue
        m = meta[title]
        want = x.get("date") or (str(src["year"]) if src["year"] else None)
        if want and commons.year_of(title, m) != commons.year_of(title, {"date": want}):
            # a scan whose page lost the book's details (Caldicot: upload date only), a reproduction's photo date (Zwolle)
            m = dict(m, date=want, date_commons=m.get("date"))
        f = {"site": sid, "qid": qid, "title": title, "year": commons.year_of(title, m), "wd_plan": False, "cat": None,
             "name": src["label"].format(name=label), "by": f"pipeline/sources.py {name}", **m}
        if not commons.keep(title, m):
            raise SystemExit(f"commons.keep() would drop {title} (year {f['year']}): fix the row or keep()")
        new_files.append(f)
        p = {"p_plan": 0.0, "p_birdseye": 0.0, "p_photo": 0.0, f"p_{src['p']}": 1.0}
        new_cls.append({"site": sid, "title": title, **p, "by": "hand"})
    print(f"{name}: {len(new_sites)} new sites, {len(new_files)} new pictures")
    for s in new_sites:
        print("  ", s["id"], s["lon"], s["lat"], s.get("place"))
    if dry:
        return
    before = len(commons.rows())
    with open(os.path.join(CAT, "extras.jsonl"), "a") as f:
        for s in new_sites:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    with open(fpath, "a") as f:
        for r in new_files:
            f.write(json.dumps(r) + "\n")
    with open(cpath, "a") as f:
        for r in new_cls:
            f.write(json.dumps(r) + "\n")
    after = len(commons.rows())
    assert after - before == len(new_files), f"commons.rows() kept {after - before} of {len(new_files)} new pictures"
    print("build:", ",".join(to_build))


if __name__ == "__main__":
    run(sys.argv[1], "--dry" in sys.argv)
