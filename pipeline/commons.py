"""Old drawings of the sites from Wikimedia Commons: plans, bird's-eye views and engravings made before 1926.

Why: Ethan 2026-10-10 - plain survey sheets (USGS topos, OS) are boring; what is worth seeing is a drawing of the
work itself (an antiquarian plan, a 1500s bird's-eye view of a castle) laid over today's ground.

usage: commons.py harvest [site ids...]   built sites by default (web/data/sites.json) -> data/commons/files.jsonl
       commons.py thumbs                   1280 px thumbnails -> data/raw/commons/<site>/<name>.jpg
       commons.py classify                 Clef-flash p(plan), p(birdseye), p(photo) -> data/commons/classified.jsonl
       commons.py sheet [min_p]            contact sheets of likely plans/views for checking by eye -> data/commons/sheets/

Where files come from: the site's Wikidata item (P373 Commons category, P3311 plan image, P18 image), Commons
full-text search on the site's name with plan/map/engraving words (this is what finds antiquarian plans and the
British Library's book-illustration scans; categories alone gave 1-2 old files per site), and the files in the
site's category and its map/plan/old-picture subcategories.
Kept: made before 1926 by year_of() (the file's date, a book's publication date, or the title; never a year from the
description's prose), or undated with a plan/map/engraving word in the title; never SVGs, reconstructions, museum
finds, paintings "in the style of" or modern geograph photos.
Licences and authors are recorded per file (all Commons files are free; most of these are public domain).
"""
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "commons")
RAW = os.path.join(ROOT, "data", "raw", "commons")
WD = "https://www.wikidata.org/w/api.php"
CM = "https://commons.wikimedia.org/w/api.php"
MAX_YEAR = 1925
PACE_S = 1.0
_last = 0.0
FOLLOW = re.compile(r"map|plan|histor|old |engrav|drawing|print|paint|antiquar|illustrat|survey|lithograph|"
                    r"etching|watercolo|sketch|view|stukeley|hoare|vauban|merian|speed|buck|archaeolog|excavat|aerial",
                    re.I)
SKIP = re.compile(r"people|event|interior|church|coin|artefact|artifact|finds|museum|logo|sign|bus |railway station|"
                  r"pub |shop|street|vehicle|ship|portrait|grave|tomb|stained glass|cricket|football|concert", re.I)
# The google alternative names the junk products (Maps/Earth/Art Project/Street View/satellite), not the bare word:
# a book-scan provenance line like "leaf n0248 of the 936-leaf Google scan (British Museum volume)" names the
# scan's maker, not a screenshot - the bare word silently re-dropped the 17 staged Horsley files rows after
# 230's merge (2026-10-14). The junk the rule targets names its product.
NO = re.compile(r"reconstruct|\.svg$|model|diorama|artist'?s impression|google (?:maps?|earth|art|street view|satellite)|openstreetmap|FindID|geograph\.org|"
                r"\(geograph|panoramio|flickr - |buckle|brooch|coin|portrait|\.webm|\.ogv|\.pdf$|\.djvu$|"
                r"\(style of\)|Bowes Museum|still life", re.I)
PLANWORD = re.compile(r"plan|map|survey|engrav|sketch|view|bird|ichnograph|prospect|plate|lithograph|etching|drawing", re.I)
SEARCHES = ['"{n}" plan', '"{n}" map OR survey', '"{n}" engraving OR drawing OR view OR prospect -"style of"']


def search(name):
    out = []
    for q in SEARCHES:
        d = get(CM, {"action": "query", "list": "search", "srnamespace": "6", "srlimit": "40",
                     "srsearch": q.format(n=name.replace('"', '')) + " filetype:bitmap"})
        out += [h["title"] for h in d.get("query", {}).get("search", [])]
    return out


def get(url, params, tries=4):
    # no maxlag: these are reads, and Wikidata's maxlag also counts query-service lag (often 15+ s), which reads
    # do not add to
    q = dict(params, format="json")
    global _last
    for k in range(tries + 2):
        time.sleep(max(0.0, _last + PACE_S - time.time()))  # one request at a time, PACE_S apart (Wikimedia 429s bursts)
        _last = time.time()
        try:
            req = urllib.request.Request(url + "?" + urllib.parse.urlencode(q), headers=aw.UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.load(r)
            if "error" in d and d["error"].get("code") == "maxlag":
                time.sleep(5 * (k + 1))
                continue
            return d
        except urllib.error.HTTPError as e:
            if e.code != 429 or k == tries + 1:
                raise
            wait = int(e.headers.get("Retry-After") or 30)
            print(f"   429, waiting {wait} s", flush=True)
            time.sleep(wait)
        except Exception as e:
            if k >= tries - 1:
                raise
            print("   retry", repr(e)[:120], flush=True)
            time.sleep(3 * (k + 1))
    raise RuntimeError(f"{url}: still lagged after {tries} tries")


def wd_claims(qids):
    out = {}
    for i in range(0, len(qids), 50):
        d = get(WD, {"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]), "props": "claims"})
        for q, e in d.get("entities", {}).items():
            c = e.get("claims", {})
            val = lambda p: [x["mainsnak"]["datavalue"]["value"] for x in c.get(p, []) if "datavalue" in x["mainsnak"]]
            out[q] = {"cat": (val("P373") or [None])[0], "plan": val("P3311"), "image": val("P18")}
    return out


def members(cat, kind):
    out, cont = [], {}
    while True:
        d = get(CM, {"action": "query", "list": "categorymembers", "cmtitle": "Category:" + cat, "cmtype": kind,
                     "cmlimit": "500", **cont})
        out += [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
        if "continue" not in d:
            return out
        cont = d["continue"]


def files_of(cat, depth=2, seen=None):
    """File titles in a category and in its map/plan/old-picture subcategories."""
    seen = seen if seen is not None else set()
    if cat in seen or len(seen) > 40:
        return []
    seen.add(cat)
    files = members(cat, "file")
    if depth:
        for sub in members(cat, "subcat"):
            name = sub.split(":", 1)[1]
            if SKIP.search(name):
                continue
            if depth == 2 or FOLLOW.search(name):
                files += files_of(name, depth - 1, seen)
    return files


YEAR = re.compile(r"(?<!\d)(1[2-9]\d\d|20[0-2]\d)(?!\d)")
# book scans (the British Library's) carry the upload date in the date field and the book's date in the description
PUBLISHED = re.compile(r"(?:Date of Publishing|Date of publication|Published|Zeichnung von|drawn in|engraved in)\s*:?\s*"
                       r"(1[2-9]\d\d)", re.I)
LIVED = re.compile(r"Unknown date.*?\)|author lived[^)]*\)", re.I)
LIFESPAN = re.compile(r"\((?:c\.\s*)?1[2-9]\d\d\s*[-\u2013]\s*(?:c\.\s*)?1[2-9]\d\d\)")  # a painter's life dates in a title
# the era a title depicts, not when the picture was made: "Kincaid Mounds 1300 CE" (a 2017 painting),
# "Stonehenge vid midsommar 1700 f Kr" (a reconstruction of 1700 BC), "Caddoan Phases in the 1520s map HRoe 2010"
ERA = re.compile(r"(?<!\d)\d{3,4}(?:s\b|\s*(?:CE|BCE|BC|AD|A\.D\.|B\.C\.|f\.?\s?Kr\.?|v\.?\s?Chr\.?|"
                 r"av\.?\s?J\.-C\.)(?![a-z]))", re.I)


def year_of(title, m):
    """Year the picture was made, or None: the file's date, else a publication date in the description, else the
    title. Never a number from the description's prose (a 2025 photo of a castle "abandoned in 1495" is not old)."""
    raw = m.get("date") or ""
    d = raw.split("date QS")[0]
    if LIVED.search(d):
        return None  # "Unknown date (author lived 1607-1677)": the artist's life, not the picture's date
    pub = PUBLISHED.search(m.get("desc") or "")
    if pub:
        return int(pub.group(1))
    ty = [int(y) for y in YEAR.findall(ERA.sub("", LIFESPAN.sub("", title)))]
    ys = [int(y) for y in YEAR.findall(d)]
    if not ys:
        qs = re.search(r"\+(1[2-9]\d\d)-", raw)  # "13th century" -> +1250
        ys = [int(qs.group(1))] if qs else []
    if ys:
        # an upload timestamp on a scan whose title names the year it was drawn: "Plan of Barnard Castle (1897).jpg"
        if min(ys) > MAX_YEAR and ty and min(ty) <= MAX_YEAR and re.match(r"\s*\d{4}-\d\d-\d\d", d):
            return min(ty)
        return min(ys)
    return min(ty) if ty else None


def when_of(title, m):
    """The date as a person would write it, for labels: "17th century", "1870s", "1575-1635", "c. 1748", "1769".
    year_of() stays the number used for sorting and the 1925 cut-off (a century sorts at its middle year)."""
    y = year_of(title, m)
    if y is None:
        return ""
    d = (m.get("date") or "").split("date QS")[0]
    raw = m.get("date") or ""
    if PUBLISHED.search(m.get("desc") or "") or not YEAR.findall(d):
        qs = re.search(r"P571,\+(1[2-9]\d\d)-00-00T00:00:00Z/([78])|^[^,]*,\+(1[2-9]\d\d)-00-00T00:00:00Z/([78])", raw)
        if qs and not PUBLISHED.search(m.get("desc") or ""):
            yy, prec = int(qs.group(1) or qs.group(3)), qs.group(2) or qs.group(4)
            if prec == "7":
                n = yy // 100 + 1
                return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')} century"
            return f"{yy // 10 * 10}s"
        return str(y)
    ys = sorted(int(v) for v in YEAR.findall(d))
    circa = "c. " if re.search(r"\b(circa|ca\.|c\.|about)\s*\d", d, re.I) and ys[0] == y else ""
    if (len(ys) >= 2 and ys[-1] > ys[0] and ys[0] == y and
            re.search(r"\bbetween\b|\d\s*[-\u2013]\s*(?:circa|ca\.|c\.)?\s*\d", d, re.I)):
        return f"{circa}{ys[0]}-{ys[-1]}"
    return f"{circa}{y}"


def keep(title, m):
    """Old enough, or undated with a plan/map/engraving word in the title (the classifier and an eye check decide)."""
    if NO.search(title) or NO.search(m.get("desc") or ""):
        return False
    lived = LIVED.search((m.get("date") or "").split("date QS")[0])
    if lived:
        return max(int(y) for y in YEAR.findall(lived.group(0)) or [9999]) <= MAX_YEAR
    y = year_of(title, m)
    return y <= MAX_YEAR if y is not None else bool(PLANWORD.search(title))


def info(titles):
    out = {}
    for i in range(0, len(titles), 50):
        d = get(CM, {"action": "query", "titles": "|".join(titles[i:i + 50]), "prop": "imageinfo",
                     "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1280"})
        for p in d.get("query", {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            m = {k: html.unescape(re.sub(r"<[^>]+>", " ", str(v.get("value", "")))).strip()
                 for k, v in (ii.get("extmetadata") or {}).items()}
            out[p["title"]] = {"url": ii.get("url"), "thumb": ii.get("thumburl"), "w": ii.get("width"),
                               "h": ii.get("height"), "mime": ii.get("mime"), "date": m.get("DateTimeOriginal", ""),
                               "desc": m.get("ImageDescription", "")[:600], "artist": m.get("Artist", "")[:200],
                               "license": m.get("LicenseShortName", ""), "page": ii.get("descriptionurl")}
    return out


def harvest(ids):
    sites = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "web", "data", "sites.json")))["sites"]}
    ids = ids or [k for k, s in sites.items() if s.get("qid")]
    qids = sorted({sites[i]["qid"] for i in ids if sites.get(i, {}).get("qid")})
    claims = wd_claims(qids)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "files.jsonl")
    done = {json.loads(l)["site"] for l in open(path)} if os.path.exists(path) else set()
    for sid in ids:
        s = sites.get(sid)
        if not s or not s.get("qid") or sid in done:
            continue
        c = claims.get(s["qid"], {})
        titles = ["File:" + t for t in c.get("plan", []) + c.get("image", [])]
        titles += search(s["name"])
        if c.get("cat"):
            titles += files_of(c["cat"], depth=1)
        titles = [t for t in dict.fromkeys(titles) if not NO.search(t)][:600]
        meta = info(titles) if titles else {}
        kept = []
        for t, m in meta.items():
            if not m.get("url") or NO.search(t) or NO.search(m["desc"]) or (m["mime"] or "").startswith(("video", "audio", "application/pdf")):
                continue
            if not keep(t, m):
                continue
            kept.append({"site": sid, "qid": s["qid"], "title": t, "year": year_of(t, m), "wd_plan": t[5:] in c.get("plan", []),
                         "cat": c.get("cat"), **m})
        with open(path, "a") as f:
            for k in kept:
                f.write(json.dumps(k) + "\n")
            if not kept:
                f.write(json.dumps({"site": sid, "qid": s["qid"], "title": None, "cat": c.get("cat"), "n_seen": len(titles)}) + "\n")
        print(f"{sid}: {len(titles)} files seen, {len(kept)} old ones (cat {c.get('cat')})", flush=True)


def rows():
    """Harvested files, judged again with the current keep() / year_of() (rows from older harvests included)."""
    p = os.path.join(OUT, "files.jsonl")
    out = []
    for r in (json.loads(l) for l in open(p)) if os.path.exists(p) else []:
        if r.get("title") and keep(r["title"], r):
            out.append(dict(r, year=year_of(r["title"], r), when=when_of(r["title"], r)))
    return out


def local(r):
    name = hashlib.sha1(r["title"].encode()).hexdigest()[:16] + ".jpg"
    return os.path.join(RAW, r["site"], name)


def thumbs():
    for r in rows():
        p = local(r)
        if os.path.exists(p) or not r.get("thumb"):
            continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        try:
            with urllib.request.urlopen(urllib.request.Request(r["thumb"], headers=aw.UA), timeout=120) as resp:
                data = resp.read()
            open(p + ".part", "wb").write(data)
            os.replace(p + ".part", p)
        except Exception as e:
            print("  thumb failed", r["title"][:80], repr(e)[:100], flush=True)
        time.sleep(1.0)


CLEF_STATE = ("A historical picture (made before 1926) from the Wikimedia Commons category of an archaeological site "
              "or castle. Decide what kind of picture it is.")
CLEF_Q = {
    "plan": {"type": "noul", "instructions": "Is this a plan or map seen straight from above that shows the layout of "
             "the site itself (its walls, ditches, ramparts, mounds or buildings drawn in outline), as opposed to a "
             "view, a photograph, a map of a whole region or a page of text?"},
    "birdseye": {"type": "noul", "instructions": "Is this a drawing, engraving or painting of the site seen from high "
                 "above at an angle (a bird's-eye view) in which its layout can be followed?"},
    "photo": {"type": "noul", "instructions": "Is this a photograph?"},
}


def classify(batch=6):
    import clef
    path = os.path.join(OUT, "classified.jsonl")
    done = {json.loads(l)["title"] + "|" + json.loads(l)["site"] for l in open(path)} if os.path.exists(path) else set()
    todo = [r for r in rows() if os.path.exists(local(r)) and r["title"] + "|" + r["site"] not in done]
    print(f"classify: {len(todo)} to do", flush=True)
    for i in range(0, len(todo), batch):
        ch = todo[i:i + batch]
        try:
            ans = clef.decide_batch([(CLEF_STATE, CLEF_Q, [local(r)]) for r in ch])
        except Exception as e:
            print("  clef error", repr(e)[:200], flush=True)
            time.sleep(10)
            continue
        with open(path, "a") as f:
            for r, a in zip(ch, ans):
                f.write(json.dumps({"site": r["site"], "title": r["title"], **{f"p_{k}": round(float(a[k]["noul"]), 4)
                                                                              for k in CLEF_Q}}) + "\n")
        if i % 60 == 0:
            print(f"  {i}/{len(todo)}", flush=True)


def sheet(min_p=0.3):
    from PIL import Image, ImageDraw
    cl = {(c["site"], c["title"]): c for c in (json.loads(l) for l in open(os.path.join(OUT, "classified.jsonl")))}
    rs = [r for r in rows() if (r["site"], r["title"]) in cl]
    for r in rs:
        c = cl[(r["site"], r["title"])]
        r["p"] = max(c["p_plan"], c["p_birdseye"]) * (1 - c["p_photo"])
    rs = sorted([r for r in rs if r["p"] >= min_p], key=lambda r: -r["p"])
    d = os.path.join(OUT, "sheets")
    os.makedirs(d, exist_ok=True)
    idx = []
    for k in range(0, len(rs), 20):
        S = Image.new("RGB", (5 * 300, 4 * 330), "white")
        dr = ImageDraw.Draw(S)
        for j, r in enumerate(rs[k:k + 20]):
            im = Image.open(local(r)).convert("RGB")
            im.thumbnail((290, 290))
            x, y = (j % 5) * 300, (j // 5) * 330
            S.paste(im, (x + 5, y + 5))
            dr.text((x + 5, y + 298), f"{k + j} p{r['p']:.2f} {r['year']}", fill=(200, 0, 0))
            dr.text((x + 5, y + 312), r["site"][:40], fill=(0, 0, 0))
            idx.append({"i": k + j, "site": r["site"], "title": r["title"], "year": r["year"], "p": round(r["p"], 3)})
        S.save(os.path.join(d, f"sheet_{k // 20:03d}.jpg"), quality=80)
    json.dump(idx, open(os.path.join(d, "index.json"), "w"), indent=0)
    print(len(rs), "pictures on", (len(rs) + 19) // 20, "sheets in", d)


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "harvest":
        harvest(rest)
    elif cmd == "thumbs":
        thumbs()
    elif cmd == "classify":
        classify()
    elif cmd == "sheet":
        sheet(float(rest[0]) if rest else 0.3)
