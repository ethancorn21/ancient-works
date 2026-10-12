"""The right-place check (task 309): does the queue pair a picture with the right place, not a namesake?

usage: tools/right_place.py [--root DIR] [--all] [FILTER ...]

The matcher ties a picture to a site by name, and two places can share a name (the Devil's Dyke
near Brighton vs the Devil's Dyke in Cambridgeshire - the case this exists for). This check
re-reads each queue pairing's own metadata: the picture's caption (the book's list title
beats the machine-read one), the county/state word it prints, the towns it names resolved
to classic counties through the catalog's admin values, and the site's catalog record. A
pairing is flagged when the places cannot both be right (an explicit word the site's
county/state is not, or - with no explicit word - the picture's towns all resolving to
other counties, UK only). For a flag it also lists the catalog sites the picture would
score against with the matcher's own rule plus a place gate, so the picture can be moved
to the place it belongs to.

Stdlib only: the owner's Mac runs it with any python (no PIL, no pipeline/ imports).
Every input store is optional; with no catalog, no book index and no book lists the check
prints a no-op and leaves the queue alone.

The blocks marked VERBATIM below are copied from pipeline/books_match.py (the matcher's
norm/tokens/place_of/score_candidate core); a venv-only test guards them against drift, so
that file stays the single source of truth for the matcher's word rules - edit there.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ===== the following blocks are copied VERBATIM from pipeline/books_match.py (task 309);
# a venv-only drift test compares them against the live matcher - do not edit them here =====

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
# ===== end of the verbatim core; everything below is new (task 309) =====

# Words that are not towns: the matcher's generic words, plus OCR splits of real names
# ("Mem bury", "More ton"), author attributions and county words in a second spelling.
# Kept separate from GENERIC on purpose: the copied matcher core must stay byte-identical.
TOWN_STOP = set(GENERIC) | {
    "bury", "down", "ross", "lodge", "maiden", "cotton", "more", "shire",
}

# County words that print in captions but are not in the matcher's UK_COUNTIES (Scottish
# counties, -shire spellings): printed word -> classic county. The copied place_of keeps
# the matcher's own list; this check does the extended scan on top of it.
EXT_WORDS = {
    "perthshire": "perthshire", "peeblesshire": "peeblesshire", "berwickshire": "berwickshire",
    "somersetshire": "somerset", "devonshire": "devon", "dorsetshire": "dorset",
}
UK_COUNTIES_EXT = UK_COUNTIES + sorted(EXT_WORDS)

# Modern administrative county -> the classic county a book of this vintage means by it.
# Complete for every distinct value of the current catalog (verified 2026-10-12, task 309,
# against the 111 UK county values and 27 US state values: the decision for each is in
# DECISIONS.md); approximations are marked there. A value in neither this table nor
# IDENTITY leaves the site's county None - never a false flag - and the CLI warns about it.
CLASSIC_UNITS = {
    # N/E/W/S splits -> parent
    "east sussex": "sussex", "west sussex": "sussex",
    "north yorkshire": "yorkshire", "west yorkshire": "yorkshire", "south yorkshire": "yorkshire",
    "east riding of yorkshire": "yorkshire", "middlesbrough": "yorkshire",
    "redcar and cleveland": "yorkshire",
    "north lincolnshire": "lincolnshire", "north east lincolnshire": "lincolnshire",
    "north northamptonshire": "northamptonshire", "west northamptonshire": "northamptonshire",
    "north somerset": "somerset",
    # cities -> county
    "bedford": "bedfordshire", "central bedfordshire": "bedfordshire", "luton": "bedfordshire",
    "west berkshire": "berkshire", "bracknell forest": "berkshire", "wokingham": "berkshire",
    "windsor and maidenhead": "berkshire", "reading": "berkshire",
    "bath and north east somerset": "somerset", "city of bristol": "somerset",
    "brighton and hove": "sussex",
    "cheshire east": "cheshire", "cheshire west and chester": "cheshire", "warrington": "cheshire",
    "city of york": "yorkshire", "city of plymouth": "devon",
    "city of portsmouth": "hampshire", "city of southampton": "hampshire",
    "city of derby": "derbyshire", "city of leicester": "leicestershire",
    "city of milton keynes": "buckinghamshire", "city of peterborough": "cambridgeshire",
    "medway": "kent", "southend on sea": "essex", "thurrock": "essex",
    "darlington": "durham", "county durham": "durham", "stockton on tees": "durham",
    # multiple districts -> county
    "bournemouth christchurch and poole": "dorset", "poole": "dorset",
    "greater london": "middlesex", "greater manchester": "lancashire", "merseyside": "lancashire",
    "blackburn with darwen": "lancashire", "west midlands": "staffordshire",
    "telford and wrekin": "shropshire", "south gloucestershire": "gloucestershire",
    "swindon": "wiltshire", "tyne and wear": "northumberland",
    "westmorland and furness": "westmorland",
    # islands
    "isles of scilly": "cornwall", "isle of anglesey": "anglesey", "cumbria": "cumberland",
    # Wales: the modern county / borough -> the classic county it sits in
    "wrexham county borough": "wrexham", "conwy county borough": "caernarvonshire",
    "blaenau gwent": "monmouthshire", "merthyr tydfil county borough": "monmouthshire",
    "torfaen": "monmouthshire", "newport": "monmouthshire",
    "bridgend county borough": "glamorgan", "caerphilly county borough": "glamorgan",
    "cardiff": "glamorgan", "neath port talbot": "glamorgan", "rhondda cynon taf": "glamorgan",
    "swansea": "glamorgan", "the vale of glamorgan": "glamorgan",
}

# The classic names themselves (a value that maps to itself): the matcher's list, the Welsh
# and island classics the catalog actually carries, and the US states (identity).
IDENTITY = set(UK_COUNTIES) | {
    "carmarthenshire", "ceredigion", "gwynedd", "denbighshire", "flintshire",
    "pembrokeshire", "powys", "wrexham", "glamorgan", "isle of wight",
} | {s.lower() for s in US_STATES} | {"massachusetts"}

# The classic names split by side of the Atlantic: which implied words become the
# row's uk_county and which become its state (score_candidate's native place check).
UK_CLASSICS = set(UK_COUNTIES) | set(EXT_WORDS) | {
    "carmarthenshire", "ceredigion", "gwynedd", "denbighshire", "flintshire",
    "pembrokeshire", "powys", "wrexham", "glamorgan", "isle of wight",
}
US_CLASSICS = {s.lower() for s in US_STATES} | {"massachusetts"}


def _load_json(path):
    """The file's JSON, or None when the file is absent (a missing store is a no-op);
    a malformed file fails loudly."""
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _classic(rec, unmapped):
    """The site's classic county (UK) or state (US) from its catalog admin value; a value in
    neither table leaves it None (an unplaceable site is never a false flag) and is collected
    so the CLI can warn about catalog growth."""
    adm = rec.get("admin") or {}
    if rec.get("region") in ("england", "wales"):
        v = re.sub(r"\s+", " ", norm(adm.get("county") or "")).strip()
        classic = CLASSIC_UNITS.get(v) or (v if v in IDENTITY else None)
        if v and classic is None:
            unmapped.append(v)
        rec["county"], rec["state"] = classic, None
    elif rec.get("region") == "us":
        # the catalog stores US sites as {"state": ...} only - no US town signal (the US
        # county value is ignored); a row with no state gets state None, never a flag
        v = re.sub(r"\s+", " ", norm(adm.get("state") or "")).strip()
        classic = CLASSIC_UNITS.get(v) or (v if v in IDENTITY else None)
        if v and classic is None:
            unmapped.append(v)
        rec["county"], rec["state"] = None, classic
    else:
        rec["county"], rec["state"] = None, None


def load(root):
    """Everything the check reads, each store optional: the catalog (with the classic
    county/state and the word->counties index), the book index rows, the book lists.
    Missing files stay empty and the check degrades to a no-op."""
    data = {"catalog": {}, "by_qid": {}, "token_idx": {}, "by_name": {},
            "word_counties": {}, "lists": {}, "index": {}, "unmapped": []}

    path = os.path.join(root, "data", "catalog", "sites.jsonl")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                rec.setdefault("aliases", [])
                _classic(rec, data["unmapped"])
                if rec.get("id"):
                    data["catalog"][rec["id"]] = rec
                if rec.get("qid"):
                    data["by_qid"][rec["qid"].lower()] = rec
                for t in site_toks(rec):
                    data["token_idx"].setdefault(t, []).append(rec)
                # the matcher's own by_name rule: the primary name always indexed, aliases
                # only when they carry a distinctive word (load_catalog in books_match.py)
                for j, nm in enumerate([rec.get("name") or ""] + list(rec.get("aliases") or [])):
                    for k in name_lookup_keys(nm, skip_generic=j > 0):
                        data["by_name"].setdefault(k, []).append(rec)
        # town word -> the classic counties of the catalog sites that carry it in an admin
        # value (UK: parish + district + county; US: state only); words pointing at more
        # than four counties are too broad to be towns ("little", "new", "king") and drop
        for rec in data["catalog"].values():
            classic = rec["county"] or rec["state"]
            if not classic:
                continue
            adm = rec.get("admin") or {}
            raws = ([adm.get("parish"), adm.get("district"), adm.get("county")]
                    if rec.get("region") in ("england", "wales") else [adm.get("state")])
            for raw in raws:
                for w in norm(raw or "").split():
                    # the county words (both lists) and the matcher's generics are not towns;
                    # US state words stay ("york" of "New York" is a town word: it resolved the
                    # York vs alauna case in the session-2 verification)
                    if len(w) < 4 or w.isdigit() or w in TOWN_STOP or w in UK_COUNTIES_EXT:
                        continue
                    data["word_counties"].setdefault(w, set()).add(classic)
        data["word_counties"] = {w: s for w, s in data["word_counties"].items() if len(s) <= 4}

    d = os.path.join(root, "data", "books", "lists")
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json") or fn.endswith(".map.json"):
                continue  # .map.json is the page map, not the list of figures
            obj = _load_json(os.path.join(d, fn)) or {}
            lst = {}
            for e in obj.get("figures") or []:
                if e.get("fig") is not None and e.get("title"):
                    lst[str(e["fig"])] = e["title"]
            for e in obj.get("plates") or []:
                key = " ".join(x for x in [e.get("plate"), e.get("sub")] if x not in (None, ""))
                if key and e.get("title"):
                    lst[key] = e["title"]
            if lst:
                data["lists"][fn[:-5]] = lst

    path = os.path.join(root, "data", "books", "index.jsonl")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get("id"):
                    data["index"][r["id"]] = r
    return data


# Attribution fragments in the printed caption: "{after Cotton", "{after Roy)" (the OCR
# loses the closing brace), "(after Roy)" - the artist's name is not the picture's place.
ATTRIBUTION = re.compile(r"\{[^}]{0,80}\}?|\(after [^)]{0,80}\)?")


def _town_parts(caption, pw):
    """The caption's comma parts after the name part (the first part with a distinctive
    word - the matcher's own rule, with the county words of both lists as place words);
    all parts when no part has one."""
    parts = re.split(r"[,(;]", caption or "")
    for i, p in enumerate(parts):
        if any(t not in pw for t in tokens(p)):
            return parts[i + 1:]
    return parts


def picture_facts(data, plan, row):
    """What the picture itself says about its place: the caption (the book's own list
    title, then the index title, then the row title - the printed caption beats the
    machine-read one), the county/state word it prints (H1), and the towns it names,
    resolved to classic counties through the catalog (H2)."""
    idx = data["index"].get(plan) or {}
    ia = idx.get("ia_id") or row.get("ia")
    caption = None
    lst = data["lists"].get(ia) if ia else None
    if lst:
        key = None
        if idx.get("fig") is not None:
            key = str(idx["fig"])
        elif idx.get("plate") is not None:
            key = " ".join(x for x in [idx.get("plate"), idx.get("sub")] if x not in (None, ""))
        if key:
            caption = lst.get(key)
    caption = caption or idx.get("title") or row.get("title") or ""
    place = idx.get("place") or ""
    names = idx.get("site_names") or []
    book = idx.get("book") or (row.get("book") if row.get("book") in BOOK_SCOPE else "")
    # the matcher's own extraction, run on the caption instead of the index title
    toks, name_toks, pwords, phr, regions = row_inputs(
        {"book": book, "title": caption, "place": place, "site_names": names})

    text = norm(" ".join([caption, place] + names))
    explicit_uk = set()
    if pwords.get("uk_county"):
        explicit_uk.add(pwords["uk_county"])
    for ext, classic in EXT_WORDS.items():
        if re.search(r"\b%s\b" % re.escape(ext), text):
            explicit_uk.add(classic)
    explicit_us = pwords.get("state")

    pw = PLACE_WORDS | set(UK_COUNTIES_EXT)
    town_words = []
    # the county words of both lists and the county abbreviations stay out of the town
    # words (they are the explicit word, not a town); US state words may in: they resolve
    # to their state through the catalog (the session-2 verification kept them too -
    # "york" had to survive)
    for p in _town_parts(ATTRIBUTION.sub(" ", caption), pw) + [place]:
        for t in tokens(p):
            if len(t) >= 3 and not t.isdigit() and t not in TOWN_STOP and t not in UK_COUNTIES_EXT \
                    and t not in UK_ABBR and t not in town_words:
                town_words.append(t)
    resolved = set()
    for w in town_words:
        resolved |= data["word_counties"].get(w, set())
    implied = set(explicit_uk) | resolved

    # the place as printed, for the reason string: the caption's tail parts (attribution
    # stripped, punctuation trimmed) or the first explicit word
    tails, seen = [], set()
    for t in _town_parts(ATTRIBUTION.sub(" ", caption), pw) + [place]:
        t = re.sub(r"[\s.,:]+", " ", t).strip(" .,:")
        if t and t not in seen:
            seen.add(t)
            tails.append(t)
    caption_place = ", ".join(tails)
    if not caption_place:
        caption_place = (sorted(explicit_uk)[0] if explicit_uk else
                         (explicit_us or ""))

    return {"plan": plan, "book": book, "caption": caption, "place": place,
            "toks": toks, "name_toks": name_toks, "phrases": phr, "regions": regions,
            "explicit_uk": explicit_uk, "explicit_us": explicit_us,
            "town_words": town_words, "resolved": resolved, "implied": implied,
            "caption_place": caption_place, "book_row": bool(idx)}


def _region_bucket(region):
    r = (region or "").lower()
    if r in ("england", "wales", "scotland"):
        return "uk"
    if r in ("us", "usa", "united states"):
        return "us"
    return "other"


def site_facts(data, site):
    """The site's own place facts: the catalog record (by the site id, then by the Q-id
    the site id carries) with its classic county/state; without a catalog row the
    sites.json place string is read (a UK county word, the extended Scottish list, or a
    US state). A site with no county/state is unknown - never a contradiction."""
    rec = data["catalog"].get(site.get("id"))
    if rec is None and re.search(r"-(q\d+)$", site.get("id") or "", re.I):
        rec = data["by_qid"].get(site["id"].rsplit("-", 1)[1].lower())
    bucket = _region_bucket(site.get("region"))
    place = site.get("place")
    if not place and rec is not None:
        adm = rec.get("admin") or {}
        place = ", ".join(str(adm[k]) for k in ("parish", "district", "county", "state")
                          if adm.get(k))
    county = rec.get("county") if rec else None
    state = rec.get("state") if rec else None
    if county is None and bucket == "uk":
        county = place_of(place or "").get("uk_county")
        if county is None:
            text = norm(place or "")
            for ext, classic in EXT_WORDS.items():
                if re.search(r"\b%s\b" % re.escape(ext), text):
                    county = classic
                    break
    if state is None and bucket == "us":
        state = place_of(place or "").get("state")
    return {"site": site["id"], "name": site.get("name") or site["id"],
            "region_bucket": bucket, "county": county, "state": state,
            "place": place or "", "rec": rec}


def check_pairing(site, facts):
    """(flagged, reason). H1: the picture prints a county/state word the site's known
    county/state is not (either direction, and any word against the other side of the
    Atlantic). H2, UK sites only and only with no explicit word, and only for book rows
    (their titles follow the book's "Name, Place" list convention; a commons file title
    is a description, not a place, so its words never resolve): the picture's towns all
    resolve to counties the site's is not. A site with an unknown county/state passes."""
    if facts["explicit_uk"]:
        if site["region_bucket"] == "us":
            kind = "h1"
        elif site["county"] and site["county"] not in facts["explicit_uk"]:
            kind = "h1"
        else:
            kind = None
    elif facts["explicit_us"]:
        if site["region_bucket"] == "uk":
            kind = "h1"
        elif site["state"] and site["state"] != facts["explicit_us"]:
            kind = "h1"
        else:
            kind = None
    else:
        kind = None
        if facts["book_row"] and site["region_bucket"] == "uk" and site["county"] \
                and facts["resolved"] and site["county"] not in facts["resolved"]:
            kind = "h2"
    if kind is None:
        return (False, "")
    reason = "same name, other place: %s vs %s" % (facts["caption_place"] or facts["caption"],
                                                  site["place"] or site["name"])
    return (True, reason)


def find_right_site(data, facts, exclude, top=3, min_score=0.5):
    """The catalog sites the picture would land on: the matcher's own two channels (exact
    name lookup, shared distinctive token) scored by the matcher's own rule, with the
    picture's implied county as the place gate - the single implied county becomes the
    row's uk_county (the native county rejection plus the 0.25 bonus do the rest), and
    when several counties are implied a candidate is dropped unless its classic county or
    state is one of them. `exclude` (a site id) keeps out the site the pairing was flagged
    against. A candidate scoring below min_score (0.5: the matcher itself accepts at
    0.75) is no confident "right site" and is not returned."""
    cands, exact = {}, set()
    for ph in facts["phrases"]:
        for k in name_keys(ph):
            for s in data["by_name"].get(k, []):
                key = s.get("qid") or s.get("id")
                cands[key] = s
                exact.add(key)
    for t in facts["toks"]:
        for s in data["token_idx"].get(t, []):
            cands[s.get("qid") or s.get("id")] = s
    implied = facts["implied"]
    uk_implied = implied & UK_CLASSICS
    us_implied = implied & US_CLASSICS
    place = {}
    if len(uk_implied) == 1:
        place["uk_county"] = sorted(uk_implied)[0]
    elif len(us_implied) == 1:
        place["state"] = sorted(us_implied)[0]
    regions = BOOK_SCOPE.get(facts["book"], (None, None))[0]
    out = []
    for key, s in cands.items():
        if s.get("id") == exclude or key == exclude:
            continue
        if not place and implied:
            classic = s.get("county") or s.get("state")
            if classic is not None and classic not in implied:
                continue
        r = score_candidate(s, facts["toks"], facts["name_toks"], place, regions, key in exact)
        if r is None or r[0] < min_score:
            continue
        out.append((r[0], s, r[1]))
    out.sort(key=lambda x: (-x[0], len(x[2])))
    return out[:top]


def _signal(site, facts):
    """The one line of which rule fired: the explicit word or the towns and where they go."""
    bits = []
    if facts["explicit_uk"]:
        bits.append("explicit uk: " + ", ".join(sorted(facts["explicit_uk"])))
    if facts["explicit_us"]:
        bits.append("explicit us: " + facts["explicit_us"])
    if facts["town_words"]:
        bits.append("towns: %s -> %s" % (", ".join(facts["town_words"]),
                                         ", ".join(sorted(facts["resolved"])) if facts["resolved"]
                                         else "(no catalog hit)"))
    if not bits and site["county"]:
        bits.append("site county: " + site["county"])
    return "; ".join(bits) if bits else "(no signal)"


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="The right-place check (task 309): which queue pairings pair a picture "
                    "with a namesake, not the place?")
    ap.add_argument("--root", default=ROOT, help="the data root (default: this checkout)")
    ap.add_argument("--all", action="store_true", help="print the ok pairings too")
    ap.add_argument("filter", nargs="*",
                    help="substring filter on site id / plan id / caption (case-insensitive)")
    a = ap.parse_args(argv)

    data = load(a.root)
    if not data["catalog"] and not data["index"] and not data["lists"]:
        print("no catalog, book index or book lists under %s - nothing to check" % a.root)
        return 0
    if data["unmapped"]:
        vals = sorted(set(data["unmapped"]))
        print("warning: %d catalog admin value(s) not in CLASSIC_UNITS (their site stays "
              "unflagged): %s" % (len(vals), ", ".join(vals)))

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fit_queue

    sites = (_load_json(os.path.join(a.root, "web", "data", "sites.json")) or {}).get("sites") or []
    site_by_id = {s["id"]: s for s in sites if s.get("id")}
    rows = fit_queue._plans_rows(a.root)
    item_cands = fit_queue._item_candidates(a.root)
    hand = fit_queue._hand_sites(a.root)

    n = flagged = 0
    for sid, name in fit_queue._built_sites(a.root):
        if sid in hand:
            continue
        site = site_by_id.get(sid) or {"id": sid, "name": name}
        cands = fit_queue._candidates(sid, rows, item_cands.get(sid) or [])
        if not cands:
            continue
        s = site_facts(data, site)
        for plan in sorted(cands):
            row = cands[plan]
            f = picture_facts(data, plan, row)
            n += 1
            if a.filter and not any(x in (sid + " " + plan + " " + f["caption"]).lower()
                                    for x in a.filter):
                continue
            ok, reason = check_pairing(s, f)
            if ok:
                flagged += 1
                print("FLAG  %s (%s)  <-  %s" % (sid, s["name"], plan))
                print("      caption:  %s" % f["caption"])
                print("      signal:   %s" % _signal(s, f))
                print("      reason:   %s" % reason)
                if s["county"] or s["state"]:
                    print("      site:     %s" % (s["county"] or s["state"]))
                right = find_right_site(data, f, exclude=sid)
                if right:
                    print("      right:    " + " | ".join(
                        "%.2f %s (%s)" % (x, c.get("name"), c.get("county") or c.get("state") or "?")
                        for x, c, _w in right))
                else:
                    print("      right:    (no passing catalog site)")
            elif a.all:
                print("ok    %s  <-  %s  (%s)" % (sid, plan, f["caption"]))
    print("checked %d queue pairing(s): %d flagged" % (n, flagged))
    return 0


if __name__ == "__main__":
    sys.exit(main())
