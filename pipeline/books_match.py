"""Match book index rows (data/books/index.jsonl) to catalog sites (data/catalog/sites.jsonl) by name + place.

Rule (no model involved):
  1. From each index row take the printed title (from the book's own list where there is one), the site names
     and place Qwen read off the page, and pull out county / state / country words.
  2. Distinctive name tokens = words left after dropping generic ones ("ancient", "works", "mound", "county"...).
     A row whose title has no distinctive token ("Ancient work, Butler county, Ohio") cannot be matched by name
     and is counted as `generic`, not as a miss.
  3. A catalog site is a candidate when it shares a distinctive token with the row (name or alias) AND does not
     contradict the row's place: the same US state / English county when both are known, and the same county
     when both are known.
  4. Score = share of the row's distinctive tokens found in the site's name/aliases (+0.25 if the county agrees).
     Best candidate accepted at score >= 0.75 and a margin of 0.15 over the runner-up; otherwise `ambiguous`.
  5. Also `ambiguous` (with a `why`) unless an exact name match: no word of the title's name part matches (only the
     parish did); for US sites, the catalog site has no state, or half or less of its name is in the title.

usage: books.py match      -> data/books/matches.jsonl, prints the match rate
"""
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(__file__))
from books import OUT, ROOT  # noqa: E402

CATALOG = os.path.join(ROOT, "data", "catalog", "sites.jsonl")

US_STATES = ["alabama", "arkansas", "georgia", "illinois", "indiana", "iowa", "kentucky", "louisiana", "michigan",
             "minnesota", "mississippi", "missouri", "new york", "north carolina", "ohio", "pennsylvania",
             "south carolina", "tennessee", "virginia", "west virginia", "wisconsin", "florida", "kansas",
             "nebraska", "south dakota", "north dakota", "oklahoma", "texas", "maryland", "manitoba"]
ABBR = {"miss": "mississippi", "s. c": "south carolina", "s.c": "south carolina", "n. c": "north carolina",
        "va": "virginia", "w. va": "west virginia", "ky": "kentucky", "tenn": "tennessee", "ind": "indiana",
        "ill": "illinois", "wis": "wisconsin", "o": "ohio", "ala": "alabama", "ga": "georgia", "la": "louisiana"}
UK_ABBR = {"wilts": "wiltshire", "bucks": "buckinghamshire", "berks": "berkshire", "oxon": "oxfordshire",
           "salop": "shropshire", "northants": "northamptonshire", "notts": "nottinghamshire", "yorks": "yorkshire",
           "cambs": "cambridgeshire", "beds": "bedfordshire", "hants": "hampshire", "herts": "hertfordshire",
           "lincs": "lincolnshire", "glos": "gloucestershire", "leics": "leicestershire", "staffs": "staffordshire"}
UK_COUNTIES = """cornwall devon somerset dorset wiltshire berkshire buckinghamshire oxfordshire shropshire
northamptonshire nottinghamshire yorkshire cambridgeshire bedfordshire hampshire hertfordshire sussex kent essex
derbyshire herefordshire gloucestershire cheshire monmouthshire breconshire anglesey merionethshire caernarvon
caernarvonshire norfolk suffolk lincolnshire leicestershire staffordshire worcestershire warwickshire surrey middlesex
westmorland cumberland northumberland durham lancashire rutland huntingdonshire""".split()
GENERIC = set("""ancient work works mound mounds group groups the of at on in near and county co township town
range sec section east west north south map plan plat plats earthwork earthworks enclosure enclosures inclosure
inclosures fort forts fortified hill camp circle square octagon stone walled small large great old various
localities parts part copy figure fig plate no nos vicinity site sites valley river creek lake miles mile with from
same one enlarged ward state place farm effigy effigies animal bird birds lizard man cross ridge ridges
excavations excavation extremely about between dividing landing bank banks grounds college school addition block
street summit fortification fortifications diagram outline view lines line remains etc t r sections high city way
row pair four form shaped plans indian ward first second home supplementary area acres miles feet scale surveyed surveyor rings ring castle
works roman saxon norman british danish moated homestead hut huts ground barrow barrows tumulus entrenchment
entrenchments rampart camps motte bailey ringwork hall house manor church wood park common after copy""".split())


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"['\u2019]s\b", "", s)  # "Dunlap's works" ~ "Dunlap Works"
    return re.sub(r"[^a-z0-9 ]+", " ", s)


SUFFIX = re.compile(r"\s+(works|earthworks|camp|mound|mounds|group|site|state memorial|state park|state historic site|"
                    r"historic site|archaeological site|archeological site|national historical park|national monument|"
                    r"indian mounds|park)$")


def name_keys(k):
    """A name and its forms with trailing descriptors stripped: "Fort Hill State Memorial" -> "fort hill"."""
    out = {k}
    while True:
        k2 = SUFFIX.sub("", k).strip()
        if k2 == k or not k2:
            return out
        out.add(k2)
        k = k2


def tokens(s):
    return [t for t in norm(s).split() if t not in GENERIC and len(t) > 2 and not t.isdigit()]


def place_of(text):
    t = norm(text)
    out = {}
    m = re.search(r"([a-z]+(?: [a-z]+)?) (?:county|co|parish)\b", t)
    if m:
        out["county"] = m.group(1).split()[-1]
    for st in sorted(US_STATES, key=len, reverse=True):
        if re.search(r"\b%s\b" % st, t):
            out["state"] = st
            break
    raw = (text or "").lower()
    for a, full in ABBR.items():
        if "state" not in out and re.search(r"(^|[\s,(])%s\.?($|[\s,)])" % re.escape(a), raw):
            out["state"] = full
    for a, full in UK_ABBR.items():
        if re.search(r"(^|[\s,(])%s\.?($|[\s,)])" % re.escape(a), raw):
            out["uk_county"] = full
    for c in UK_COUNTIES:
        if re.search(r"\b%s\b" % c, t):
            out["uk_county"] = c
    return out


def site_place(site):
    adm = site.get("admin") or {}
    vals = {k: norm(str(v)) for k, v in adm.items() if v}
    return vals


def site_toks(site):
    """The distinctive tokens of the site's name and aliases - what a row's tokens can hit."""
    toks = set(tokens(site.get("name", "")))
    for a in site.get("aliases") or []:
        toks |= set(tokens(a))
    return toks


def name_lookup_keys(nm, skip_generic=False):
    """The by_name lookup keys of one name: normalized, whitespace-compressed, trailing descriptors stripped
    ("Fort Hill State Memorial" -> "fort hill"). skip_generic: an all-generic name ("Roman Camp") yields none -
    it is no name to look up by."""
    k = re.sub(r"\s+", " ", norm(nm)).strip()
    if skip_generic and not tokens(k):
        return set()
    return {kk for kk in name_keys(k) if kk}


def row_inputs(row):
    """The matcher's extraction from the row's printed text: the distinctive tokens, the name tokens, the
    place words (including the book's default state) and the candidate phrases, shaped by the book's scope.
    Returns (toks, name_toks, place, phrases, regions)."""
    title = row.get("title") or ""
    names = row.get("site_names") or []
    place = {}
    for t in [title, row.get("place") or ""] + names:
        for k, v in place_of(t).items():
            place.setdefault(k, v)
    regions, default_state = BOOK_SCOPE.get(row.get("book"), (None, None))
    if default_state and not place.get("state"):
        place["state"] = default_state
    if place.get("county"):
        place_words = PLACE_WORDS | {place["county"]}
    else:
        place_words = PLACE_WORDS
    toks = []
    for t in [title] + names:
        for x in tokens(t):
            if x not in toks and x not in place_words:
                toks.append(x)
    phr = phrases(title, names)
    # name part = first comma part of the title that has a distinctive word, plus names read off the page; the
    # rest of a title is parish / county ("Gannock's Castle, Tempsford, Beds"), which must not carry a match alone
    name_toks = set()
    for part in re.split(r"[,(;]", re.sub(r"(?i)^(plan|plat|map|ground plan)( and section)? of (the )?", "", title)):
        pt = [x for x in tokens(part) if x not in place_words]
        if pt:
            name_toks |= set(pt)
            break
    for nm in names:
        name_toks |= {x for x in tokens(nm) if x not in place_words}
    return toks, name_toks, place, phr, regions


def score_candidate(site, toks, name_toks, place, regions, is_exact):
    """The matcher's rule for one row side against one catalog site: (score, why) when the site is a
    candidate, None when it contradicts the row's region, state or county and is rejected outright."""
    sp = site_place(site)
    region = site.get("region")
    if regions and region not in regions:
        return None
    if region == "us":
        if place.get("uk_county"):
            return None
        if place.get("state") and sp.get("state") and place["state"] not in sp["state"]:
            return None
    elif region in ("england", "wales"):
        if place.get("state"):
            return None
    county_ok = None
    pc = place.get("uk_county") if region in ("england", "wales") else place.get("county")
    if pc and sp.get("county"):
        county_ok = pc in sp["county"]
        if not county_ok:
            return None
    st = site_toks(site)
    share = len([t for t in toks if t in st]) / len(toks) if toks else 0.0
    if is_exact:
        share = max(share, 1.0)
    why = []
    if not is_exact:
        if name_toks and not (name_toks & st):
            why.append("only a place word matches")
        if region == "us":
            if place.get("state") and not sp.get("state"):
                why.append("catalog site has no state")
            variants = [site.get("name", "")] + list(site.get("aliases") or [])
            cover = max((len([t for t in tokens(v) if t in toks]) / len(tokens(v)) for v in variants
                         if tokens(v)), default=0)
            if cover <= 0.5:
                why.append("half or less of the site's name is in the title")
    return (share + (0.25 if county_ok else 0), why)


def load_catalog():
    sites = [json.loads(l) for l in open(CATALOG) if l.strip()]
    idx, by_name = {}, {}
    for s in sites:
        for j, nm in enumerate([s.get("name", "")] + list(s.get("aliases") or [])):
            for kk in name_lookup_keys(nm, skip_generic=j > 0):
                by_name.setdefault(kk, []).append(s)
    for s in sites:
        for t in site_toks(s):
            idx.setdefault(t, []).append(s)
    return sites, idx, by_name


# What a book covers, from its title page: catalog regions allowed, and the state when a title names none.
BOOK_SCOPE = {"squier_davis_1848": ({"us"}, None), "thomas_1894": ({"us"}, None), "lapham_1855": ({"us"}, "wisconsin"),
              "fowke_1902": ({"us"}, "ohio"), "whittlesey_1850": ({"us"}, "ohio"), "mills_1914": ({"us"}, "ohio"),
              "squier_1851": ({"us"}, "new york"), "allcroft_1908": ({"england", "wales"}, None)}
PLACE_WORDS = set(" ".join(US_STATES).split()) | set(UK_COUNTIES) | set(UK_ABBR) | {"ohio", "county", "co"}


def phrases(title, names):
    """Candidate site names as printed: quoted names ("Fort Hill"), the first comma-separated part of the title
    unless it is a generic heading ("Ancient work", "Plan of ..."), and names Qwen read off the page."""
    out = re.findall(r"[\"“”]([^\"“”]{3,40})[\"“”]", title or "")
    first = re.split(r"[,(;]", title or "")[0].strip()
    first = re.sub(r"^(plan|plat|map|ground plan)( and section)? of (the )?", "", first, flags=re.I).strip()
    # all-generic names ("Fort Hill", "High Bank works") are kept for exact lookup when 2+ words
    if first and (tokens(first) or len(first.split()) >= 2) and \
            not re.match(r"(?i)^(ancient|various|nos?\b|one of|another|mound group|group of|map of)", first):
        out.append(first)
    return [re.sub(r"\s+", " ", norm(x)).strip() for x in out + list(names or []) if norm(x).strip()]


def match_row(row, idx, by_name):
    toks, name_toks, place, phr, regions = row_inputs(row)
    if not toks and not phr:
        return {"status": "generic", "place": place}
    cands = {}
    exact = set()
    for ph in phr:
        for s in [x for k in name_keys(ph) for x in by_name.get(k, [])]:
            cands[s.get("qid") or s["id"]] = s
            exact.add(s.get("qid") or s["id"])
    for t in toks:
        for s in idx.get(t, []):
            cands[s.get("qid") or s["id"]] = s
    scored = []
    for s in cands.values():
        r = score_candidate(s, toks, name_toks, place, regions, (s.get("qid") or s["id"]) in exact)
        if r is not None:
            scored.append((r[0], s, r[1]))
    scored.sort(key=lambda x: (-x[0], len(x[2])))
    if not scored:
        return {"status": "no_candidate", "tokens": toks, "place": place}
    best, s, why = scored[0]
    second = scored[1][0] if len(scored) > 1 else 0
    rec = {"tokens": toks, "place": place, "qid": s.get("qid"), "name": s["name"], "score": round(best, 2),
           "runner_up": round(second, 2), "site_id": s.get("id"), "lon": s.get("lon"), "lat": s.get("lat")}
    pc = place.get("uk_county") if s.get("region") in ("england", "wales") else place.get("county")
    if pc and not site_place(s).get("county"):
        rec["county_unchecked"] = pc  # the title names a county the catalog row cannot confirm (US rows: state only)
    if best >= 0.75 and best - second >= 0.15 and not why:
        rec["status"] = "matched"
    else:
        rec["status"] = "ambiguous"
        rec["why"] = why or (["score below 0.75"] if best < 0.75 else ["runner-up within 0.15"])
        rec["candidates"] = [(round(x, 2), c.get("qid") or c.get("id"), c["name"]) for x, c, _ in scored[:4]]
    return rec


# Matches checked by eye (2026-10-10) that the name rule gets wrong or only half right: (book, title) -> (status, note)
HAND = {
    ("mills_1914", "MAP of Serpent Mound. Warren Co., O."):
        ("rejected_by_eye", "different effigy: Warren County serpent, not Adams County Serpent Mound"),
    ("allcroft_1908", "Banwell Cross"): ("rejected_by_eye", "the cross earthwork, not the hillfort Banwell Camp"),
    ("allcroft_1908", "Cruciform Earthwork at Banwell, Somerset"):
        ("rejected_by_eye", "the cross earthwork, not the hillfort Banwell Camp"),
    ("thomas_1894", "Plat of group near Charleston, Kanawha county, West Virginia"):
        ("doubtful", "group plan; Criel Mound is one mound of it"),
    ("allcroft_1908", "The Old Pale, Eddisbury, Cheshire"):
        ("doubtful", "The Old Pale is a separate enclosure next to Eddisbury hill fort"),
}


def _key(book, title):
    """HAND key that survives a rerun re-reading the title in another case or with other punctuation."""
    return book, re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


HAND = {_key(*k): v for k, v in HAND.items()}


def main(args):
    if not os.path.exists(CATALOG):
        sys.exit(f"no catalog yet at {CATALOG}")
    rows = [json.loads(l) for l in open(os.path.join(OUT, "index.jsonl")) if l.strip()]
    sites, idx, by_name = load_catalog()
    out = []
    for r in rows:
        m = match_row(r, idx, by_name)
        m.update({"row_id": r["id"], "book": r["book"], "title": r.get("title"), "site_names": r.get("site_names")})
        h = HAND.get(_key(r["book"], r.get("title")))
        if h and m["status"] in ("matched", "ambiguous"):
            m["status"], m["note"] = h
        out.append(m)
    with open(os.path.join(OUT, "matches.jsonl"), "w") as f:
        for m in out:
            f.write(json.dumps(m) + "\n")
    from collections import Counter
    c = Counter(m["status"] for m in out)
    named = len(out) - c["generic"]
    print(f"catalog sites: {len(sites)}; index rows: {len(out)}; {dict(c)}")
    print(f"match rate, all rows: {c['matched'] / len(out):.3f}; rows with a distinctive name: "
          f"{c['matched'] / max(1, named):.3f}")
    by_book = Counter((m["book"], m["status"]) for m in out)
    for b in sorted({m["book"] for m in out}):
        print(" ", b, {s: by_book[(b, s)] for s in ("matched", "ambiguous", "no_candidate", "generic")})
    return out


if __name__ == "__main__":
    main(sys.argv[1:])
