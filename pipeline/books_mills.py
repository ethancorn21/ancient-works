"""Mills 1914, Archeological Atlas of Ohio: county site maps -> data/books/mills_county_maps.jsonl + full-res images.

Each county map marks the mounds, enclosures, village sites and burials recorded by 1914 with small red symbols.
Qwen (stage A, PROMPT_A_MILLS) tags the page type and copies the county name and scale wording as printed;
the county name is then checked against the 88 Ohio counties, each of which is also printed as a county
heading in the atlas's own OCR text (checked by `check_names`). Nothing here extracts symbols.

usage:
    books_mills.py maps      write the jsonl, report missing / duplicate counties
    books_mills.py full      download the county maps at full resolution
"""
import concurrent.futures as cf
import io
import json
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import books_ia as ia  # noqa: E402
from books import OUT, stage_a  # noqa: E402

IA_ID = "ArcheologicalAtlasOfOhio"
COUNTIES = """Adams Allen Ashland Ashtabula Athens Auglaize Belmont Brown Butler Carroll Champaign Clark Clermont
Clinton Columbiana Coshocton Crawford Cuyahoga Darke Defiance Delaware Erie Fairfield Fayette Franklin Fulton Gallia
Geauga Greene Guernsey Hamilton Hancock Hardin Harrison Henry Highland Hocking Holmes Huron Jackson Jefferson Knox
Lake Lawrence Licking Logan Lorain Lucas Madison Mahoning Marion Medina Meigs Mercer Miami Monroe Montgomery Morgan
Morrow Muskingum Noble Ottawa Paulding Perry Pickaway Pike Portage Preble Putnam Richland Ross Sandusky Scioto Seneca
Shelby Stark Summit Trumbull Tuscarawas Union Van_Wert Vinton Warren Washington Wayne Williams Wood Wyandot""".split()
COUNTIES = [c.replace("_", " ") for c in COUNTIES]
FULL = os.path.join(ia.RAW, IA_ID, "full")


def check_names():
    t = ia.djvu_txt(IA_ID).upper()
    return [c for c in COUNTIES if not re.search(r"\b%s\s+COUNTY" % c.upper(), t)]


def county_of(text):
    t = (text or "").upper()
    hits = [c for c in COUNTIES if re.search(r"\b%s\b" % c.upper(), t)]
    return max(hits, key=len) if hits else None


def maps():
    A = stage_a(IA_ID)
    ps = ia.pages(IA_ID)
    rows = []
    for n in sorted(A):
        o = A[n]["out"]
        if o.get("page_type") != "county_site_map":
            continue
        p = ps[n]
        rows.append({
            "ia_id": IA_ID, "leaf_n": n, "leaf_jp2": p["leafNum"], "page_type": "county site map",
            "county_printed": o.get("county") or None, "county": county_of(o.get("county")),
            "scale_text": o.get("scale_text") or None, "page_numbers": o.get("page_numbers"),
            "full_url": ia.full_url(IA_ID, n), "full_local": f"data/raw/books/{IA_ID}/full/n{n:04d}.jpg",
            "full_size": [p["width"], p["height"]],
            "source": "W. C. Mills, Archeological Atlas of Ohio, 1914; scan Internet Archive " + IA_ID,
        })
    with open(os.path.join(OUT, "mills_county_maps.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    got = [r["county"] for r in rows]
    missing = [c for c in COUNTIES if c not in got]
    dup = sorted({c for c in got if c and got.count(c) > 1})
    print(f"triaged {len(A)}/{len(ps)} openings; county maps: {len(rows)}; distinct counties {len(set(got) - {None})}/88")
    print("missing:", missing)
    print("duplicates:", dup, "unreadable county:", [r["leaf_n"] for r in rows if not r["county"]])
    print("county names not found as headings in the atlas OCR:", check_names())
    return rows, missing, dup


def full():
    rows = [json.loads(l) for l in open(os.path.join(OUT, "mills_county_maps.jsonl"))]
    ps = ia.pages(IA_ID)
    os.makedirs(FULL, exist_ok=True)

    def one(r):
        path = os.path.join(FULL, f"n{r['leaf_n']:04d}.jpg")
        if os.path.exists(path):
            return path
        body = ia.get(ia.page_image_url(ps[r["leaf_n"]], 1), timeout=300)
        Image.open(io.BytesIO(body)).verify()
        with open(path + ".part", "wb") as f:
            f.write(body)
        os.replace(path + ".part", path)
        return path

    with cf.ThreadPoolExecutor(2) as ex:
        done = list(ex.map(one, rows))
    print(len(done), "county maps at full resolution in", FULL)


if __name__ == "__main__":
    {"maps": maps, "full": full}[sys.argv[1]]()
