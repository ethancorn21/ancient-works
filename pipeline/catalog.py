"""Site catalog: archaeological earthworks with coordinates, seeded from Wikidata (CC0).

usage:
    catalog.py counts            # candidate counts per country x kind (cheap; for planning)
    catalog.py build             # discover + fetch + clean + merge -> data/catalog/sites.jsonl
    catalog.py summary           # data/catalog/summary.md from sites.jsonl (+ coverage / triage if present)

Everything fetched is cached (catalog_wd.py, data/raw/catalog/entities.jsonl), so `build` can be re-run or
resumed after a kill at no cost.

Where entries come from (each entry records the routes that found it in `found_via`):
  class:<kind>   Wikidata items whose P31 is one of the kind's classes (subclass trees via P279*, pruned of
                 junk subclasses, see KINDS). Main route for England, Wales, the Netherlands and France.
  arch:name-en   US archaeological sites (P31/P279* Q839954) whose English label, alias or description names
                 a mound or earthwork. Most famous US works (Cahokia, Serpent Mound, Moundville...) are typed
                 only 'archaeological site' in Wikidata, so the class route alone misses them.
  arch:name-fr   the same for France with French words (tumulus, oppidum, motte, camp, enceinte, eperon
                 barre, retranchement, tertre, castrum).
  enwiki:<cat>   pages in English Wikipedia's 'Mounds in the United States' category tree (two levels:
                 'Mounds in <state>' and the Mound Builders culture categories). Used for selection only:
                 every fact in an entry still comes from the Wikidata item.
  hop:P361/P527  one hop along part-of / has-part from an entry already found (e.g. Monks Mound -> Cahokia).
  seed:manual    a few famous works that no route finds (SEEDS; each QID looked up).
"""
import json
import math
import os
import re
import sys
import time
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog_wd as wd  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "catalog")
RAW = os.path.join(ROOT, "data", "raw", "catalog")
ENT_STORE = os.path.join(RAW, "entities.jsonl")

# kind -> classes. "tree": class + all P279* subclasses; "direct": the class itself only; "drop": sub-trees
# removed. Found by listing each tree: the 'mound' (Q1584134) and 'earthworks' (Q1349587) trees hold mud
# volcanoes, road cuttings, trench shoring and foxholes, so both are used as direct classes only.
KINDS = {
    "barrow": {"tree": ["Q34023", "Q5737", "Q20529645", "Q18292693", "Q19947271"],
               "direct": ["Q1584134", "Q1260913"]},          # mound (direct only), moot hill
    "platform_mound": {"tree": ["Q7202294"]},
    "effigy_mound": {"tree": ["Q4356478"]},
    "shell_ring": {"direct": ["Q7493724"]},
    "enclosure": {"tree": ["Q5375483", "Q1363360", "Q16963827", "Q452212", "Q1787688"]},
    "hillfort": {"tree": ["Q744099", "Q192601"], "drop": ["Q263274"]},   # drop kremlin
    "henge": {"direct": ["Q1035294"]},                       # its tree holds standing stones, Gorsedd stones
    "causewayed_enclosure": {"tree": ["Q325017"]},
    "roman_fort": {"tree": ["Q88205", "Q80838255"], "drop": ["Q21086297"]},  # drop castellum aquae
    "motte": {"tree": ["Q80446812", "Q92062", "Q7335033"], "drop": ["Q603492"]},  # drop stins
    "linear_earthwork": {"tree": ["Q60748075"]},
    "celtic_field": {"tree": ["Q1053214"]},
    "terp": {"tree": ["Q505963"]},
    "earthwork": {"direct": ["Q1349587"]},                   # generic 'earthworks' (Newark, Offa's Dyke)
}
# when an item matches several kinds, the first in this order names it
KIND_ORDER = ["effigy_mound", "platform_mound", "henge", "causewayed_enclosure", "hillfort", "roman_fort",
              "motte", "linear_earthwork", "celtic_field", "shell_ring", "terp", "enclosure", "barrow",
              "earthwork", "mound_site", "military_earthwork"]

COUNTRIES = {"Q30": "us", "Q145": "uk", "Q55": "netherlands", "Q142": "france"}
BBOX = {  # lon0, lat0, lon1, lat1: trims overseas territories, Alaska, Hawaii, Caribbean NL
    "us": (-125.0, 24.3, -66.8, 49.5), "england": (-6.5, 49.8, 2.0, 55.9), "wales": (-5.5, 51.3, -2.6, 53.5),
    "netherlands": (3.2, 50.7, 7.3, 53.7), "france": (-5.3, 41.3, 9.7, 51.2),
}
UK_PART = {"Q21": "england", "Q25": "wales"}
HERITAGE = {"P649": "nrhp", "P1216": "nhle", "P4117": "he_research", "P3007": "cadw", "P359": "rijksmonument",
            "P380": "merimee", "P3596": "dk_fund", "P1764": "flanders", "P718": "canmore"}
LOCAL_WIKI = {"wales": "cywiki", "netherlands": "nlwiki", "france": "frwiki"}
LANGS = "en|nl|fr|cy|mul"  # mul = Wikidata's language-neutral default label
ADMIN_TYPES = {  # admin-area classes looked for up the P131 chain -> field name (labels checked 2026-10-10)
    "Q35657": "state", "Q47168": "county",                                   # US
    "Q6465": "departement",                                                  # France
    "Q134390": "province", "Q2039348": "municipality",                       # Netherlands
    "Q180673": "county", "Q769603": "county", "Q1136601": "county",          # England: ceremonial /
    "Q1187580": "district", "Q349084": "district", "Q1002812": "district",   #   non-metropolitan county /
    "Q211690": "district", "Q1115575": "parish",                             #   unitary authority area
    "Q15979307": "county", "Q630638": "county",                              # Wales principal area
}
# Wikidata sitelinks that say nothing about notability: Commons, bot-generated Cebuano / Waray / Swedish
# GNIS and geo stubs, species/wikivoyage/data
NON_NOTABLE_SITES = {"commonswiki", "cebwiki", "warwiki", "specieswiki", "wikidatawiki", "metawiki"}
# P31 classes that make an item not a site (seen in the data: GNIS summits named 'Indian Mound', plaques...)
JUNK_P31 = {"Q5", "Q465299", "Q4167410", "Q13433827", "Q3305213", "Q721747", "Q479257", "Q7725634",
            "Q571", "Q47461344", "Q11060274", "Q486972", "Q532", "Q515", "Q3957", "Q498162", "Q17343829",
            "Q1093829", "Q62049", "Q15127012", "Q13406463", "Q2087181", "Q11446", "Q4022", "Q47521"}
WAR_RE = re.compile(r"\bcivil war\b|\bbattle of\b|\bbattlefield\b|\bconfederate\b|\brevolutionary war\b|"
                    r"\bwar of 1812\b", re.I)  # not bare 'battle': Battle Mound (Arkansas) is a Caddo mound
MEGALITH_P31 = {"Q101659", "Q193475", "Q1935728"}  # dolmen, menhir, stone circle (labels checked)
MILITARY_P31 = {"Q1785071", "Q57821", "Q57831", "Q18691599", "Q245016"}  # fort, fortification, fortress, military installation, military base
SUMMIT_P31 = {"Q8502", "Q54050", "Q1437459", "Q207326"}  # mountain, hill, ... GNIS summit imports
ARCH_HINT_P31 = {"Q839954", "Q56320584", "Q1349587", "Q34023", "Q7202294", "Q4356478", "Q1584134"}
NAME_RE = re.compile(r"\b(mounds?|earthworks?|works|effigy|enclosures?|serpent|tumul(?:us|i)|embankments?|"
                     r"shell rings?|octagon|fort ancient)\b", re.I)  # not 'circle': Miami Circle, False Kiva
NOT_WORKS_RE = re.compile(r"\b(iron|salt|water|gas|brick|glass|powder|lime|steel|pottery|boat|paper|cotton|"
                          r"woolen|woollen|machine|lead|zinc|copper|furnace|locomotive|tile|stone)\s+works\b", re.I)


def qid(uri):
    return uri.rsplit("/", 1)[-1]


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- discovery

def kind_classes():
    """{kind: set(class QIDs)} with subclass trees expanded (cached)."""
    out = {}
    for kind, spec in KINDS.items():
        cls = set(spec.get("direct", []))
        for root in spec.get("tree", []):
            cls.add(root)
            for r in wd.sparql(f"SELECT ?c WHERE {{ ?c wdt:P279+ wd:{root} . }}"):
                cls.add(qid(r["c"]))
        drop = set(spec.get("drop", []))
        for d in list(drop):
            for r in wd.sparql(f"SELECT ?c WHERE {{ ?c wdt:P279+ wd:{d} . }}"):
                drop.add(qid(r["c"]))
        out[kind] = cls - drop
    return out


def class_candidates(country, classes):
    """Items with a coordinate, P17 = country and P31 in classes -> {qid: set(classes)}."""
    out = {}
    cl = sorted(classes)
    for i in range(0, len(cl), 40):
        vals = " ".join("wd:" + c for c in cl[i:i + 40])
        q = f"SELECT ?item ?cls WHERE {{ VALUES ?cls {{ {vals} }} ?item wdt:P31 ?cls; wdt:P17 wd:{country}; wdt:P625 [] . }}"
        for r in wd.sparql(q, timeout=120):
            out.setdefault(qid(r["item"]), set()).add(qid(r["cls"]))
    return out


FR_NAME_RE = re.compile(r"\b(tumulus|tumuli|oppidum|mottes?|camp|enceintes?|[ée]peron barr[ée]|retranchements?|"
                        r"tertres?|castrum)\b", re.I)
FR_NOT_RE = re.compile(r"concentration|internement|prisonniers|transit|camping|camp militaire|camp de base", re.I)
# region -> (country, label language, match, reject). Archaeological sites (P31/P279* Q839954) whose label /
# alias / description in that language names an earthwork. France needs it as much as the US: most Merimee
# items are typed only 'archaeological site'.
NAME_ROUTES = {"us": ("Q30", "en", NAME_RE, NOT_WORKS_RE), "france": ("Q142", "fr", FR_NAME_RE, FR_NOT_RE)}


def arch_by_name(country, lang, rx, notrx):
    """Archaeological sites in `country` whose label / alias / description in `lang` matches rx -> QIDs."""
    rows = wd.sparql(f"""SELECT ?item ?l ?d (GROUP_CONCAT(?a; separator="|") AS ?as) WHERE {{
      ?item wdt:P31/wdt:P279* wd:Q839954; wdt:P17 wd:{country}; wdt:P625 [] .
      OPTIONAL {{ ?item rdfs:label ?l FILTER(lang(?l)="{lang}") }}
      OPTIONAL {{ ?item schema:description ?d FILTER(lang(?d)="{lang}") }}
      OPTIONAL {{ ?item skos:altLabel ?a FILTER(lang(?a)="{lang}") }}
    }} GROUP BY ?item ?l ?d""", timeout=120)
    out = set()
    for r in rows:
        text = " | ".join([r.get("l", ""), r.get("d", ""), r.get("as", "")])
        if rx.search(text) and not notrx.search(text) and not works_only(text):
            out.add(qid(r["item"]))
    return out, len(rows)


INDUSTRIAL_RE = re.compile(r"\b(bolt|iron|steel|brass|copper|lead|zinc|salt|glass|brick|tile|pottery|paper|cotton|"
                           r"wool(?:l)?en|silk|machine|engine|wagon|carriage|gun|arms|powder|chemical|gas|water|electric|"
                           r"foundry|factory|mill|company|brothers|manufactur\w*|furnace|forge|kiln|tannery)\b", re.I)


def works_only(text):
    """'works' is the only earthwork word and the name reads industrial: a factory ('Berry Brothers Bolt Works'),
    not 'Highbank Park Works'."""
    words = {m.group(1).lower() for m in NAME_RE.finditer(text)}
    return words == {"works"} and bool(INDUSTRIAL_RE.search(text))


ENWIKI_CATS = [("Category:Mounds in the United States", 2)]
# Famous works no route above finds (checked 2026-10-10): typed only 'archaeological site' + park/hill, no
# earthwork word in the label, not in a 'Mounds in <state>' category. Each QID looked up, not guessed.
SEEDS = {
    "Q4832928": "Aztalan State Park (Wisconsin)",
    "Q4348373": "Windmill Hill causewayed enclosure (Avebury, England)",
    "Q123916810": "Seip Earthworks (Ohio; typed National Historical Park)",
}


def enwiki_candidates():
    """{qid: category} from the English Wikipedia mound categories."""
    out = {}
    for cat, depth in ENWIKI_CATS:
        for title, (q, c) in wd.category_pages(cat, depth).items():
            out.setdefault(q, c)
    return out


# ---------------------------------------------------------------- entity store (slim wbgetentities)

def _slim(e):
    if e.get("missing") is not None or "claims" not in e:
        return {"id": e.get("id"), "missing": True}
    c = e["claims"]

    def items(p):
        out = []
        for s in c.get(p, []):
            if s.get("rank") == "deprecated":
                continue
            v = s["mainsnak"].get("datavalue", {}).get("value")
            if isinstance(v, dict) and "id" in v:
                out.append(v["id"])
        return out

    def strings(p):
        return [s["mainsnak"]["datavalue"]["value"] for s in c.get(p, [])
                if s.get("rank") != "deprecated" and "datavalue" in s["mainsnak"]]

    coords = []
    for s in c.get("P625", []):
        v = s["mainsnak"].get("datavalue", {}).get("value")
        if s.get("rank") == "deprecated" or not v or not v.get("globe", "").endswith("Q2"):
            continue
        coords.append([round(v["longitude"], 6), round(v["latitude"], 6), v.get("precision"), s.get("rank")])
    sl = e.get("sitelinks", {})
    return {
        "id": e["id"],
        "labels": {k: v["value"] for k, v in e.get("labels", {}).items()},
        "desc": {k: v["value"] for k, v in e.get("descriptions", {}).items()},
        "aliases": {k: [a["value"] for a in v] for k, v in e.get("aliases", {}).items()},
        "P31": items("P31"), "P279": items("P279"), "P17": items("P17"), "P131": items("P131"),
        "P361": items("P361"), "P527": items("P527"), "P2596": items("P2596"), "P2348": items("P2348"),
        "P1435": items("P1435"), "P625": coords,
        "ids": {HERITAGE[p]: strings(p) for p in HERITAGE if c.get(p)},
        "sitelinks": {k: v["title"] for k, v in sl.items() if k in ("enwiki", "nlwiki", "frwiki", "cywiki", "dawiki")},
        "n_sitelinks": len(sl),
        "n_wiki": len([k for k in sl if k not in NON_NOTABLE_SITES and k.endswith("wiki")]),
    }


class Store:
    def __init__(self, path=ENT_STORE):
        self.path, self.d = path, {}
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    try:
                        e = json.loads(line)
                    except ValueError:  # a line cut short by a kill
                        continue
                    self.d[e["id"]] = e

    def get(self, qids, label="", langs=LANGS):
        need = sorted({q for q in qids if q and q not in self.d and re.fullmatch(r"Q\d+", q)})
        if need:
            log(f"  fetching {len(need)} entities {label}")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "a") as f:
            for i in range(0, len(need), 50):
                batch = need[i:i + 50]
                q = wd.API + "?" + wd.urllib.parse.urlencode({
                    "action": "wbgetentities", "ids": "|".join(batch), "format": "json",
                    "props": "labels|descriptions|aliases|claims|sitelinks", **({"languages": langs} if langs else {})})
                d = json.loads(wd._fetch(q, min_gap=0.5))
                for qq in batch:
                    e = d.get("entities", {}).get(qq, {"id": qq, "missing": ""})
                    s = _slim(e)
                    s["id"] = qq  # redirects come back under the target id; keep the asked one
                    self.d[qq] = s
                    f.write(json.dumps(s, ensure_ascii=False) + "\n")
                f.flush()
                if (i // 50) % 20 == 0 and len(need) > 200:
                    log(f"    {i + len(batch)}/{len(need)}")
        return {q: self.d[q] for q in qids if q in self.d}

    def relabel(self):
        """Re-fetch items that came back with no label in en/nl/fr/cy (fetched before 'mul' was asked for)."""
        bad = [q for q, e in self.d.items() if not e.get("missing") and e.get("relabelled") != 2
               and not any(e["labels"].get(l) for l in ("en", "nl", "fr", "cy", "mul"))]
        for q in bad:
            del self.d[q]
        got = self.get(bad, "(no label in en/nl/fr/cy/mul: refetch all languages)", langs=None)
        with open(self.path, "a") as f:
            for q, e in got.items():
                e["relabelled"] = 2
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

    def label(self, q, langs=("en", "nl", "fr", "cy", "mul")):
        e = self.d.get(q, {})
        for l in langs:
            if e.get("labels", {}).get(l):
                return e["labels"][l]
        for l, v in sorted(e.get("labels", {}).items()):  # any other language (e.g. Basque-only items)
            return v
        return q


# ---------------------------------------------------------------- helpers

def slug(s, n=40):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:n].rstrip("-") or "site"


def hav_m(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(min(1, a)))


def in_bbox(lon, lat, b):
    return b[0] <= lon <= b[2] and b[1] <= lat <= b[3]


def best_coord(e):
    """Preferred-rank coordinate first, else the first; plus the spread between all of them (m)."""
    cs = e["P625"]
    if not cs:
        return None, None, 0.0
    pref = [c for c in cs if c[3] == "preferred"] or cs
    lon, lat, prec = pref[0][0], pref[0][1], pref[0][2]
    spread = max((hav_m(lon, lat, c[0], c[1]) for c in cs), default=0.0)
    return (lon, lat), prec, spread


def admin_chain(store, start, max_up=8):
    """Climb P131 from an item's admin targets; returns {field: label} plus the UK part QID if met."""
    out, uk = {}, None
    frontier, seen = list(start), set()
    for _ in range(max_up):
        frontier = [q for q in frontier if q not in seen]
        if not frontier:
            break
        seen.update(frontier)
        ents = store.get(frontier, "(admin areas)")
        nxt = []
        for q in frontier:
            e = ents.get(q)
            if not e or e.get("missing"):
                continue
            if q in UK_PART:
                uk = uk or q
            for t in e["P31"]:
                f = ADMIN_TYPES.get(t)
                if f and f not in out:
                    out[f] = store.label(q)
            nxt.extend(e["P131"])
        frontier = nxt
    return out, uk


GENERIC = set("""the and of in on at near from with by to a an part forming one two three four five six seven eight nine
ten north south east west northeast northwest southeast southwest nne ene ese sse ssw wsw wnw nnw ne nw se sw n s e w
immediately adjacent site sites mound mounds barrow barrows bowl bell disc pond saucer round long oval cairn cairns tumulus
tumuli group groups cemetery earthwork earthworks enclosure enclosures camp fort hillfort hill farm house church
archaeological historic state park prehistoric roman iron age bronze neolithic medieval later early settlement hut huts
circles circle field fields system motte bailey ringwork castle dyke cross linear platform effigy shell ring complex
monument scheduled remains associated including des du de la le les et sur tumulus grafheuvel grafheuvels""".split())


def name_tokens(s):
    """Distinctive name words: no kinds, directions, distances or numbers ('Bowl barrow 120m NNE of X Farm' -> {x})."""
    toks = re.findall(r"[a-z0-9']+", unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode())
    return {t for t in toks if len(t) > 1 and not re.search(r"\d", t) and t not in GENERIC}


DESIGNATORS = set("""i ii iii iv v vi vii viii ix x xi xii north south east west middle upper lower inner outer great little
greater lesser northeast northwest southeast southwest nne ene ese sse ssw wsw wnw nnw ne nw se sw""".split())


def designators(s):
    """Words that tell neighbouring monuments apart: 'Dod Law East' / 'Middle Dod Law', 'Cairn II' / 'Cairn III',
    'grafheuvel #45168' / '#45169', 'High Knowes A' / 'B'."""
    toks = re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode())
    return {t for t in toks if t in DESIGNATORS or re.fullmatch(r"\d+[a-z]?|[a-z]", t)}


# 'Bowl barrow 200m south of Windmill Hill' is a monument near Windmill Hill, not Windmill Hill
RELATIVE_RE = re.compile(r"\b\d+\s*(?:m|yds?|yards|km|ft)\b|\b(?:n|s|e|w|ne|nw|se|sw|nne|ene|ese|sse|ssw|wsw|wnw|nnw|"
                         r"north|south|east|west|north[- ]?east|north[- ]?west|south[- ]?east|south[- ]?west) of\b|"
                         r"\bnear\b|\badjacent to\b|\boutside\b", re.I)


def ids_conflict(a, b):
    """Two items listed under different numbers of the same heritage register are two monuments."""
    ha, hb = a.get("heritage", {}), b.get("heritage", {})
    return any(set(ha[k]) and set(hb[k]) and not set(ha[k]) & set(hb[k]) for k in set(ha) & set(hb))


# ---------------------------------------------------------------- build

GROUP_RE = re.compile(r"\bone of (?:a|two|three|four|five|six|seven|eight|nine|ten|\d+)?\s*((?:group|pair|line|"
                      r"cemetery|linear group|row|cluster)s? of .+)$", re.I)
PART_RE = re.compile(r"\b(?:forming|which forms?|form(?:s|ing)?) (?:a )?part of (?:a|an|the) (.+)$", re.I)


def build():
    t0 = time.time()
    store = Store()
    store.relabel()
    kc = kind_classes()
    cls2kind = {}
    for kind in KIND_ORDER:
        for c in kc.get(kind, ()):
            cls2kind.setdefault(c, kind)

    cand = {}  # qid -> {"via": set, "kinds": set}

    def add(q, via, kind=None):
        c = cand.setdefault(q, {"via": set(), "kinds": set()})
        c["via"].add(via)
        if kind:
            c["kinds"].add(kind)

    for country in COUNTRIES:
        for kind, cls in kc.items():
            for q, cs in class_candidates(country, cls).items():
                add(q, "class:" + kind, kind)
        log(f"{country}: {len(cand)} candidates so far")
    n_scanned = {}
    for region, (country, lang, rx, notrx) in NAME_ROUTES.items():
        hits, n = arch_by_name(country, lang, rx, notrx)
        for q in hits:
            add(q, f"arch:name-{lang}")
        n_scanned[region] = (n, len(hits))
        log(f"{region} arch sites scanned {n}, name matches {len(hits)}")
    for q, cat in enwiki_candidates().items():
        add(q, "enwiki:" + cat)
    for q in SEEDS:
        add(q, "seed:manual")
    log(f"after enwiki: {len(cand)}")

    ents = store.get(list(cand), "(candidates)")
    # one hop along part-of / has-part (only kept later if in region with coordinates)
    hop = set()
    for q in list(cand):
        e = ents.get(q, {})
        for p in ("P361", "P527"):
            for t in e.get(p, []):
                if t not in cand:
                    hop.add((t, p))
    hents = store.get([t for t, _ in hop], "(part-of / has-part hop)")
    for t, p in hop:
        e = hents.get(t)
        if e and not e.get("missing") and e["P625"]:
            add(t, "hop:" + p)
    ents = store.get(list(cand), "(candidates)")
    # labels for classes / cultures / periods / designations / part-of targets
    refs = set()
    for e in ents.values():
        if not e.get("missing"):
            refs.update(e["P31"] + e["P2596"] + e["P2348"] + e["P1435"] + e["P361"])
    store.get(list(refs), "(referenced labels)")
    # prefetch the P131 chains level by level (one batched pass per level instead of one call per item)
    frontier = {t for e in ents.values() if not e.get("missing") and e["P625"] for t in e["P131"]}
    seen = set()
    for level in range(8):
        frontier -= seen
        if not frontier:
            break
        seen |= frontier
        got = store.get(list(frontier), f"(admin level {level + 1})")
        frontier = {t for e in got.values() if not e.get("missing") for t in e["P131"]}

    dropped = {"missing": 0, "no_coord": 0, "out_of_region": 0, "junk_class": 0, "summit_only": 0,
               "hop_not_site": 0, "uk_other_part": 0, "not_site_like": 0, "culture_category_only": 0, "megalith": 0}
    dropped_examples = {k: [] for k in dropped}
    rows = []
    for q, c in cand.items():
        e = ents.get(q)
        if not e or e.get("missing"):
            dropped["missing"] += 1
            continue
        (ll, prec, spread) = best_coord(e)
        if ll is None:
            dropped["no_coord"] += 1
            continue
        p31 = set(e["P31"])
        via = c["via"]
        name = store.label(q)

        def drop(why):
            dropped[why] += 1
            if len(dropped_examples[why]) < 12:
                dropped_examples[why].append(f"{q} {name}")

        if not c["kinds"]:  # found by name / category / hop only: needs to look like a site
            if p31 & JUNK_P31 and not p31 & ARCH_HINT_P31:
                drop("junk_class")
                continue
            if p31 and p31 <= SUMMIT_P31:
                drop("summit_only")
                continue
            words = " ".join([name, e["desc"].get("en", ""), e["labels"].get("fr", ""), e["desc"].get("fr", "")])
            has_words = bool((NAME_RE.search(words) and not works_only(words)) or FR_NAME_RE.search(words))
            if via <= {"hop:P361", "hop:P527"} and not p31 & (ARCH_HINT_P31 | set(cls2kind)) and not has_words:
                drop("hop_not_site")
                continue
            if not p31 & (ARCH_HINT_P31 | set(cls2kind) | {"Q1152199"}) and not has_words:
                drop("not_site_like")  # e.g. Everglades National Park, Pearl Street (NYC) from shell-midden categories
                continue
            if p31 & MEGALITH_P31 and not c["kinds"]:
                drop("megalith")  # 'Caixa del Camp de l'Obra' (a dolmen) matched 'camp'
                continue
            if not has_words and all(v.startswith("enwiki:") and not v.startswith("enwiki:Category:Mounds in")
                                     for v in via):
                drop("culture_category_only")  # villages from 'Fort Ancient culture' etc. (SunWatch, Anhaica)
                continue
        countries = set(e["P17"])
        region = None
        if "Q30" in countries and in_bbox(*ll, BBOX["us"]):
            region = "us"
        elif "Q55" in countries and in_bbox(*ll, BBOX["netherlands"]):
            region = "netherlands"
        elif "Q142" in countries and in_bbox(*ll, BBOX["france"]):
            region = "france"
        elif "Q145" in countries:
            if e["ids"].get("nhle"):
                region = "england"
            elif e["ids"].get("cadw"):
                region = "wales"
            else:
                region = "uk?"
        if region is None and not countries and in_bbox(*ll, BBOX["us"]) and any(
                v.startswith(("enwiki:", "arch:name-en")) for v in via):
            region = "us"  # no country statement (new items made from Wikipedia articles); US route + US box
        if region is None:
            drop("out_of_region")
            continue
        admin, uk = admin_chain(store, e["P131"])
        if region == "uk?":
            region = UK_PART.get(uk)
            if region is None:
                drop("uk_other_part")
                continue
        if region in ("england", "wales") and not in_bbox(*ll, BBOX[region]):
            drop("out_of_region")
            continue
        kinds = sorted(c["kinds"], key=KIND_ORDER.index)
        if kinds == ["earthwork"] and p31 & MILITARY_P31:
            kinds = ["military_earthwork"]  # forts typed 'earthworks' (US: mostly Civil War forts)
        if region == "us" and WAR_RE.search(name + " " + e["desc"].get("en", "")):
            # 'Civil War Earthworks at Tallahatchie Crossing', 'Battle of Island Mound State Historic Site'
            kind, basis = "military_earthwork", "words"
        elif kinds:
            kind, basis = kinds[0], "class"
        else:
            text = " ".join([name, e["desc"].get("en", ""), e["labels"].get("fr", ""), e["desc"].get("fr", "")]).lower()
            kind = ("effigy_mound" if re.search(r"effigy|serpent", text) else
                    "platform_mound" if "platform mound" in text else
                    "hillfort" if re.search(r"oppidum|[ée]peron barr", text) else
                    "motte" if re.search(r"\bmottes?\b", text) and region == "france" else
                    "barrow" if re.search(r"tumul|tertre", text) and region == "france" else
                    "mound_site" if re.search(r"\bmounds?\b|tumul", text) or any(
                        v.startswith("enwiki:Category:Mounds in") for v in via) else
                    "enclosure" if region == "france" else
                    "earthwork")
            basis = ("words" if NAME_RE.search(text) or FR_NAME_RE.search(text) else
                     "category" if any(v.startswith("enwiki:") for v in via) else "part-of link")
        aliases = []
        for lang in ("en", LOCAL_WIKI.get(region, "en")[:2]):
            for a in [e["labels"].get(lang)] + e["aliases"].get(lang, []):
                if a and a != name and a not in aliases:
                    aliases.append(a)
        wp = {}
        if e["sitelinks"].get("enwiki"):
            wp["en"] = "https://en.wikipedia.org/wiki/" + e["sitelinks"]["enwiki"].replace(" ", "_")
        lw = LOCAL_WIKI.get(region)
        if lw and e["sitelinks"].get(lw):
            wp[lw[:2]] = f"https://{lw[:2]}.wikipedia.org/wiki/" + e["sitelinks"][lw].replace(" ", "_")
        rows.append({
            "id": slug(name) + "-" + q.lower(), "qid": q, "name": name, "aliases": aliases[:12],
            "lon": ll[0], "lat": ll[1], "coord_precision_deg": prec,
            "coord_spread_m": round(spread) if len(e["P625"]) > 1 else None,
            "region": region, "admin": admin, "kind": kind, "kinds": kinds if len(kinds) > 1 else None,
            "kind_basis": basis,
            "classes": [store.label(x) for x in e["P31"]],
            "culture": [store.label(x) for x in e["P2596"]], "period": [store.label(x) for x in e["P2348"]],
            "designation": [store.label(x) for x in e["P1435"]],
            "heritage": e["ids"], "wikipedia": wp, "sitelinks": e["n_sitelinks"], "wiki_links": e["n_wiki"],
            "part_of": [{"qid": x, "name": store.label(x)} for x in e["P361"]],
            "has_part": e["P527"], "_has_part_named": [{"qid": x, "name": store.label(x)} for x in e["P527"]],
            "found_via": sorted(via),
        })
    log(f"kept {len(rows)} rows; dropped {dropped}")

    rows, merge_log = merge(rows)
    rows.sort(key=lambda r: (r["region"], -r["wiki_links"], -r["sitelinks"], r["name"]))
    os.makedirs(OUT, exist_ok=True)
    meta = {"built": time.strftime("%Y-%m-%d %H:%M"), "dropped": dropped, "dropped_examples": dropped_examples,
            "merge": merge_log, "arch_name_route": n_scanned, "candidates": len(cand), "seconds": round(time.time() - t0)}
    with open(os.path.join(OUT, "sites.jsonl.tmp"), "w") as f:
        for r in rows:
            f.write(json.dumps({k: v for k, v in r.items() if v not in (None, [], {}, "")}, ensure_ascii=False,
                               separators=(",", ":")) + "\n")
    os.replace(os.path.join(OUT, "sites.jsonl.tmp"), os.path.join(OUT, "sites.jsonl"))
    with open(os.path.join(RAW, "build_meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    log(f"wrote {len(rows)} entries in {meta['seconds']} s")


GROUP_M = 4000  # members of a complex lie within this distance of its point (Cahokia's mounds: about 3 km)


def merge(rows):
    """1) fold members into their group (P361 / P527, all linked items within GROUP_M), 2) fold 'one of a group of X' items
    into a synthetic group, 3) merge near-duplicates (< 300 m, overlapping names)."""
    by_q = {r["qid"]: r for r in rows}
    log_ = {"folded_into_group": 0, "synthetic_groups": 0, "synthetic_members": 0, "near_duplicates": 0,
            "near_duplicate_pairs": []}
    # parent -> linked children (either direction). A parent whose linked children reach further than
    # GROUP_M is a multi-site unit (a park, a World Heritage listing), not a complex: nothing folds into it.
    links = {}
    for r in rows:
        for p in r.get("part_of", []):
            if p["qid"] in by_q and p["qid"] != r["qid"]:
                links.setdefault(p["qid"], set()).add(r["qid"])
        for child in r.get("has_part", []):
            if child in by_q and child != r["qid"]:
                links.setdefault(r["qid"], set()).add(child)
    member_of = {}
    for g, kids in links.items():
        G = by_q[g]
        far = max(hav_m(G["lon"], G["lat"], by_q[k]["lon"], by_q[k]["lat"]) for k in kids)
        if far > GROUP_M:
            G["unit"] = True
            log_["units"] = log_.get("units", 0) + 1
            continue
        for k in kids:
            member_of.setdefault(k, g)
    # resolve chains (a -> b -> c) and refuse cycles
    def top(q, seen=()):
        g = member_of.get(q)
        return q if g is None or g in seen else top(g, seen + (q,))
    for q in list(member_of):
        t = top(q)
        if t == q:
            del member_of[q]
        else:
            member_of[q] = t
    for q, g in member_of.items():
        m = by_q[q]
        by_q[g].setdefault("members", []).append(
            {"qid": q, "name": m["name"], "lon": m["lon"], "lat": m["lat"], "kind": m["kind"],
             **({"heritage": m["heritage"]} if m.get("heritage") else {})})
    rows = [r for r in rows if r["qid"] not in member_of]
    log_["folded_into_group"] = len(member_of)

    # synthetic groups from labels like "Bowl barrow: one of a group of round barrows in Bourne Bottom"
    keyed = {}
    for r in rows:
        m = GROUP_RE.search(r["name"]) or PART_RE.search(r["name"])
        if m:
            r["_phrase"] = re.sub(r"\s+", " ", m.group(1).strip().rstrip("."))
            phrase = r["_phrase"].lower()
            # a phrase without a place ('a round barrow cemetery') only groups items of the same parish
            place = "" if re.search(r"\b(in|on|at|near|around|of|north|south|east|west|between)\b\s+[a-z]",
                                    phrase.split(" of ", 1)[-1]) else r["admin"].get("parish", r["admin"].get("district", "?"))
            keyed.setdefault((r["region"], phrase, place), []).append(r)
    drop = set()
    new = []
    for (region, phrase, place), ms in keyed.items():
        clusters = []
        for r in ms:  # single-link clustering at 2 km
            hit = [c for c in clusters if any(hav_m(r["lon"], r["lat"], o["lon"], o["lat"]) <= 2000 for o in c)]
            merged = [r] + [o for c in hit for o in c]
            clusters = [c for c in clusters if c not in hit] + [merged]
        for c in clusters:
            if len(c) < 2:
                continue
            lon = sum(o["lon"] for o in c) / len(c)
            lat = sum(o["lat"] for o in c) / len(c)
            orig = c[0].get("_phrase", phrase)
            name = orig[0].upper() + orig[1:] + (f" ({place})" if place else "")
            ext = max(hav_m(lon, lat, o["lon"], o["lat"]) for o in c)
            best = max(c, key=lambda o: (o["wiki_links"], o["sitelinks"]))
            heritage = {}
            for o in c:
                for k, v in o.get("heritage", {}).items():
                    heritage.setdefault(k, [])
                    heritage[k] += [x for x in v if x not in heritage[k]]
            new.append({
                "id": slug(name) + "-grp-" + c[0]["qid"].lower(), "qid": None, "name": name, "synthetic": True,
                "lon": round(lon, 6), "lat": round(lat, 6), "extent_m": round(ext), "region": region,
                "admin": best["admin"], "kind": best["kind"], "kinds": sorted({o["kind"] for o in c}, key=KIND_ORDER.index),
                "kind_basis": "members", "heritage": heritage, "wikipedia": {},
                "sitelinks": max(o["sitelinks"] for o in c), "wiki_links": max(o["wiki_links"] for o in c),
                "members": [{"qid": o["qid"], "name": o["name"], "lon": o["lon"], "lat": o["lat"], "kind": o["kind"],
                             **({"heritage": o["heritage"]} if o.get("heritage") else {})} for o in c],
                "found_via": sorted({v for o in c for v in o["found_via"]}),
                "source": "members' Wikidata items; grouped by the shared 'one of a group of ...' / 'forming part of "
                          "a ...' phrase in their labels, members within 2 km of each other",
            })
            drop.update(o["qid"] for o in c)
            log_["synthetic_groups"] += 1
            log_["synthetic_members"] += len(c)
    rows = [r for r in rows if r["qid"] not in drop] + new

    # near-duplicates: different items < 300 m apart whose names share tokens
    rows.sort(key=lambda r: (r["region"], r["lat"]))
    gone = set()
    for i, a in enumerate(rows):
        if id(a) in gone:
            continue
        ta = name_tokens(a["name"] + " " + " ".join(a.get("aliases", [])))
        for b in rows[i + 1:]:
            if b["region"] != a["region"] or b["lat"] - a["lat"] > 0.003:
                break
            if id(b) in gone or hav_m(a["lon"], a["lat"], b["lon"], b["lat"]) > 300:
                continue
            tb = name_tokens(b["name"] + " " + " ".join(b.get("aliases", [])))
            if not ta or not tb or len(ta & tb) / min(len(ta), len(tb)) < 0.75 or ids_conflict(a, b):
                continue
            soft = {"earthwork", "enclosure", "mound_site"}
            near = RELATIVE_RE.search(a["name"]) or RELATIVE_RE.search(b["name"])
            if a["kind"] != b["kind"] and (near or (a["kind"] not in soft and b["kind"] not in soft)):
                continue  # 'Carrow Hill Round Barrow Pair' is not 'Carrow Hill Roman fort'
            da, db = designators(a["name"]), designators(b["name"])
            if da and db and da != db:
                continue
            if near:  # 'Bowl barrow 100m south of X, part of the X cemetery': near X, not X -> member of X
                keep, lose = (b, a) if RELATIVE_RE.search(a["name"]) and not RELATIVE_RE.search(b["name"]) else \
                             (a, b) if RELATIVE_RE.search(b["name"]) and not RELATIVE_RE.search(a["name"]) else \
                             (a, b) if (a["wiki_links"], a["sitelinks"]) >= (b["wiki_links"], b["sitelinks"]) else (b, a)
                keep.setdefault("members", []).append(
                    {"qid": lose["qid"], "name": lose["name"], "lon": lose["lon"], "lat": lose["lat"],
                     "kind": lose["kind"], **({"heritage": lose["heritage"]} if lose.get("heritage") else {})})
                keep.setdefault("members", []).extend(lose.get("members", []))
                gone.add(id(lose))
                log_["near_folded_as_member"] = log_.get("near_folded_as_member", 0) + 1
                if lose is a:
                    break
                continue
            keep, lose = (a, b) if (a["wiki_links"], a["sitelinks"], len(a.get("heritage", {}))) >= \
                                   (b["wiki_links"], b["sitelinks"], len(b.get("heritage", {}))) else (b, a)
            keep.setdefault("merged_from", []).append({"qid": lose["qid"], "name": lose["name"]})
            for k, v in lose.get("heritage", {}).items():
                keep.setdefault("heritage", {}).setdefault(k, [])
                keep["heritage"][k] += [x for x in v if x not in keep["heritage"][k]]
            keep["found_via"] = sorted(set(keep["found_via"]) | set(lose["found_via"]))
            keep.setdefault("members", []).extend(lose.get("members", []))
            gone.add(id(lose))
            log_["near_duplicates"] += 1
            if len(log_["near_duplicate_pairs"]) < 40:
                log_["near_duplicate_pairs"].append(f"{keep['qid']} {keep['name']} <= {lose['qid']} {lose['name']}")
            if lose is a:
                break
    rows = [r for r in rows if id(r) not in gone]
    for r in rows:
        r.pop("has_part", None)
        r["has_part"] = r.pop("_has_part_named", [])  # P527 as {qid, name}, folded or not
        r.pop("_phrase", None)
        if r.get("members"):
            r["n_members"] = len(r["members"])
        if r.get("unit"):
            r["unit_note"] = "multi-site unit (its parts lie more than 4 km apart); parts kept as their own entries"
    return rows, log_


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "counts":
        kc = kind_classes()
        for country in ["Q30", "Q145", "Q55", "Q142", "Q35", "Q31"]:
            for kind, cls in kc.items():
                print(country, kind, len(class_candidates(country, cls)), flush=True)
    elif cmd == "build":
        build()
    elif cmd == "summary":
        import catalog_summary
        catalog_summary.main()
