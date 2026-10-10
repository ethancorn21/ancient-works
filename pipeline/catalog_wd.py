"""Wikidata access for the site catalog: SPARQL + wbsearchentities + wbgetentities, cached on disk.

Requests are sequential, carry the project User-Agent and back off on 429 / 5xx (honouring Retry-After).
Every answer is cached under data/raw/catalog/wd/<sha1>.json, so re-runs cost nothing and a long run
can be killed and resumed.

usage (exploration):
    catalog_wd.py search "hillfort"            # label search -> QID | label | description
    catalog_wd.py sparql "SELECT ... "         # prints JSON rows
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "raw", "catalog", "wd")
UA = "ancient-works/0.2 (personal research)"
SPARQL = "https://query.wikidata.org/sparql"
API = "https://www.wikidata.org/w/api.php"
_last = [0.0]


def _fetch(url, data=None, tries=20, min_gap=1.0, timeout=90):
    for i in range(tries):
        gap = time.time() - _last[0]
        if gap < min_gap:
            time.sleep(min_gap - gap)
        _last[0] = time.time()
        req = urllib.request.Request(url, data=data, headers={
            "User-Agent": UA, "Accept": "application/sparql-results+json, application/json"})
        if data is not None:
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                wait = int(e.headers.get("Retry-After") or 0) or 10 * (i + 1)
                print(f"  wd {e.code}, waiting {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            body = e.read()[:400]
            raise RuntimeError(f"HTTP {e.code}: {body!r}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            print(f"  wd {e}, retry", file=sys.stderr)
            time.sleep(10 * (i + 1))
    raise RuntimeError("Wikidata request failed after retries: " + url[:200])


def _cached(key, fn):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, hashlib.sha1(key.encode()).hexdigest() + ".json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    out = fn()
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f)
    os.replace(tmp, path)
    return out


def sparql(query, timeout=90):
    """Rows of a SELECT as a list of {var: value-string}."""
    def run():
        body = _fetch(SPARQL, data=urllib.parse.urlencode({"query": query, "format": "json"}).encode(),
                      timeout=timeout)
        d = json.loads(body)
        return [{k: v["value"] for k, v in b.items()} for b in d["results"]["bindings"]]
    return _cached("sparql:" + query, run)


def api(params):
    params = dict(params, format="json")
    q = API + "?" + urllib.parse.urlencode(sorted(params.items()))
    return _cached("api:" + q, lambda: json.loads(_fetch(q, min_gap=0.5)))


def wp_api(params, lang="en"):
    """Cached MediaWiki API call on <lang>.wikipedia.org."""
    params = dict(params, format="json")
    q = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(sorted(params.items()))
    return _cached("wp:" + q, lambda: json.loads(_fetch(q, min_gap=0.5)))


def category_pages(cat, depth=1, lang="en"):
    """{page title: wikidata QID} for main-namespace pages in a category, recursing `depth` levels into
    subcategories. Pages without a Wikidata item are skipped."""
    out, seen, todo = {}, set(), [(cat, 0)]
    while todo:
        c, d = todo.pop()
        if c in seen:
            continue
        seen.add(c)
        cont = {}
        while True:
            r = wp_api({"action": "query", "generator": "categorymembers", "gcmtitle": c, "gcmlimit": 500,
                        "gcmtype": "page|subcat", "prop": "pageprops", "ppprop": "wikibase_item", **cont}, lang)
            for p in r.get("query", {}).get("pages", {}).values():
                if p["ns"] == 14 and d < depth:
                    todo.append((p["title"], d + 1))
                elif p["ns"] == 0 and p.get("pageprops", {}).get("wikibase_item"):
                    out[p["title"]] = (p["pageprops"]["wikibase_item"], c)
            if "continue" not in r:
                break
            cont = {k: v for k, v in r["continue"].items()}
    return out


def search(text, limit=8):
    d = api({"action": "wbsearchentities", "search": text, "language": "en", "limit": limit, "type": "item"})
    return [(x["id"], x.get("label", ""), x.get("description", "")) for x in d.get("search", [])]


def labels(qids):
    """{qid: (en label, en description)} for any number of QIDs (50 per request)."""
    out = {}
    qids = sorted(set(qids))
    for i in range(0, len(qids), 50):
        d = api({"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]), "props": "labels|descriptions",
                 "languages": "en"})
        for q, e in d.get("entities", {}).items():
            out[q] = (e.get("labels", {}).get("en", {}).get("value", ""),
                      e.get("descriptions", {}).get("en", {}).get("value", ""))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "search":
        for t in sys.argv[2:]:
            print("==", t)
            for q, l, d in search(t):
                print(f"  {q} | {l} | {d}")
    elif sys.argv[1] == "sparql":
        for row in sparql(sys.argv[2]):
            print(json.dumps(row, ensure_ascii=False))
    elif sys.argv[1] == "labels":
        for q, (l, d) in labels(sys.argv[2:]).items():
            print(f"{q} | {l} | {d}")
