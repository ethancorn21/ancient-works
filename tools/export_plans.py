"""Site plans from the old books (data/books/index.jsonl) as a compact list for the page's plate-fitting tool.

usage: tools/export_plans.py  -> web/data/plans.json
Each row: the page image (served by serve.py from data/raw/books/<ia>/full/), its title, the stage-B map box when
there is one, and the catalog sites the name matcher tied it to (matched first, then ambiguous candidates).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS = os.path.join(ROOT, "data", "books")
SHORT = {"squier_davis_1848": "Squier & Davis 1848", "lapham_1855": "Lapham 1855", "thomas_1894": "Thomas 1894",
         "fowke_1902": "Fowke 1902", "squier_1851": "Squier 1851", "whittlesey_1850": "Whittlesey 1850",
         "allcroft_1908": "Allcroft 1908", "mills_1914": "Mills 1914"}


def commons_rows(min_p=0.3):
    """Old pictures from Wikimedia Commons (pipeline/commons.py) that Clef-flash takes for a plan or a bird's-eye view.
    min_p=None: every harvested picture with a local copy, classified or not (tools/fitkit.py looks plans up here)."""
    import hashlib
    import re
    from PIL import Image
    cd = os.path.join(ROOT, "data", "commons")
    cp = os.path.join(cd, "classified.jsonl")
    if not os.path.exists(cp) and min_p is not None:
        return []
    cl = {(c["site"], c["title"]): c for c in (json.loads(l) for l in open(cp))} if os.path.exists(cp) else {}
    sys.path.insert(0, os.path.join(ROOT, "pipeline"))
    import commons
    out = []
    for r in commons.rows():
        c = cl.get((r["site"], r["title"]))
        if min_p is not None and (not c or c["p_photo"] >= 0.5 or max(c["p_plan"], c["p_birdseye"]) < min_p):
            continue
        h = hashlib.sha1(r["title"].encode()).hexdigest()[:16]
        path = os.path.join(ROOT, "data", "raw", "commons", r["site"], h + ".jpg")
        if not os.path.exists(path):
            continue
        w, hgt = Image.open(path).size
        # a row from pipeline/sources.py names its picture ("Ludlow Castle, plan from Mackenzie ..."): the British Library's
        # scans are titled by page number only
        name = r.get("name") or re.sub(r"\.(jpe?g|png|tiff?|gif)$", "", r["title"][5:], flags=re.I)
        artist = re.sub(r"\s+", " ", r.get("artist") or "").strip()
        cite = "; ".join(x for x in [artist and f"by {artist}", r.get("license"), r.get("page")] if x)
        out.append([f"c_{h}", "Wikimedia Commons", None, None, name, r["when"], [w, hgt],
                    None, [r["site"]], cite, f"media/commons/{r['site']}/{h}.jpg", bool(c) and c["p_birdseye"] > c["p_plan"], r["title"]])
    return out


def main():
    rows = [json.loads(l) for l in open(os.path.join(BOOKS, "index.jsonl")) if l.strip()]
    cat = {}
    for l in open(os.path.join(ROOT, "data", "catalog", "sites.jsonl")):
        s = json.loads(l)
        cat[s["id"]] = s["id"]
        if s.get("qid"):
            cat[s["qid"]] = s["id"]
    matches = {}
    p = os.path.join(BOOKS, "matches.jsonl")
    if os.path.exists(p):
        for l in open(p):
            m = json.loads(l)
            ids = []
            if m["status"] == "matched" and m.get("site_id"):
                ids.append(m["site_id"])
            elif m["status"] == "ambiguous":
                ids += [cat[c[1]] for c in m.get("candidates") or [] if c[1] in cat]
            matches[m["row_id"]] = ids
    alias = {k: v for k, v in json.load(open(os.path.join(ROOT, "specs", "aliases.json"))).items() if not k.startswith("_")}
    matches = {k: list(dict.fromkeys(alias.get(x, x) for x in v)) for k, v in matches.items()}
    out = []
    for r in rows:
        if not r.get("full_local") or not os.path.exists(os.path.join(ROOT, r["full_local"])):
            continue
        label = f"Plate {r['plate']}{r.get('sub') or ''}" if r.get("plate") else (f"Fig. {r['fig']}" if r.get("fig") else "")
        out.append([r["id"], SHORT.get(r["book"], r["book"]), r["ia_id"], os.path.basename(r["full_local"]),
                    r.get("title") or "", label, r.get("full_size"), r.get("map_box"), matches.get(r["id"], []),
                    r.get("cite") or "", None, False, None])
    out += commons_rows()
    cols = ["id", "book", "ia", "file", "title", "label", "size", "map_box", "sites", "cite", "url", "view", "ref"]
    dst = os.path.join(ROOT, "web", "data", "plans.json")
    json.dump({"cols": cols, "rows": out}, open(dst, "w"), separators=(",", ":"))
    print(len(out), "plans,", os.path.getsize(dst) // 1024, "KB ->", dst)


if __name__ == "__main__":
    main()
