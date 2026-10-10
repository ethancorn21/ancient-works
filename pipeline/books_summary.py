"""Tables for data/books/summary.md, computed from the files (validation.json, index.jsonl, mills, matches).

usage: books_summary.py  -> prints markdown tables (pasted into summary.md under the hand-written notes)
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from books import BOOKS, OUT, stage_a, stage_b, stage_f  # noqa: E402
import books_ia as ia  # noqa: E402


def jl(p):
    p = os.path.join(OUT, p)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def main():
    idx = jl("index.jsonl")
    V = {r["book"]: r for r in json.load(open(os.path.join(OUT, "validation.json")))} \
        if os.path.exists(os.path.join(OUT, "validation.json")) else {}
    print("| book | IA id | pages | stage A | stage F | stage B | index rows | site-plan pages | by Qwen | by list only |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for k, b in BOOKS.items():
        i = b["ia"]
        rows = [r for r in idx if r["book"] == k]
        pages = {r["leaf_n"]: r for r in rows}
        q = sum(1 for r in pages.values() if "qwen" in r["found_by"])
        lo = sum(1 for r in pages.values() if r["found_by"] == ["list"])
        print(f"| {k} | {i} | {len(ia.pages(i))} | {len(stage_a(i))} | {len(stage_f(i))} | {len(stage_b(i))} | "
              f"{len(rows)} | {len(pages)} | {q} | {lo} |")
    print()
    print("| book | site plates listed | mapped to a leaf | Qwen typed site plan | Qwen read the numeral | "
          "other plates called site plan |")
    print("|---|---|---|---|---|---|")
    for k, v in V.items():
        p = v.get("plates")
        if not p:
            continue
        print(f"| {k} | {p['site']} | {p['site_mapped_to_leaf']} | {p['recall_site_plan_type']} | "
              f"{p['qwen_read_numeral_on_site_plates']} | {p['other_plates_flagged_as_site']} |")
    print()
    print("| book | figures parsed / listed | site-plan pages in list | recall A | recall A+Clef | recall A+Clef (+-1 leaf) "
          "| precision A (strict/lenient) | precision A+Clef (strict/lenient) |")
    print("|---|---|---|---|---|---|---|---|")
    for k, v in V.items():
        f = v.get("figures")
        if not f:
            continue
        a = f.get("stage_A_only", {})
        print(f"| {k} | {f['parsed_with_page_on_a_leaf']}/{f['expected']} | {f['gt_site_pages']} | {a.get('recall')} | "
              f"{f['recall_pages']} | {f['recall_pages_pm1']} | {a.get('precision_strict')}/{a.get('precision_lenient')} | "
              f"{f['precision_strict']}/{f['precision_lenient']} |")
    print()
    c = Counter(r["page_type"] for r in idx)
    print("index rows by page type:", dict(c))
    print("rows with a map box:", sum(1 for r in idx if r["map_box"]), "/", len(idx),
          "; with scale text:", sum(1 for r in idx if r["scale_text"]),
          "; with a north arrow end-point pair:", sum(1 for r in idx if r.get("north_angle_deg") is not None))
    m = jl("matches.jsonl")
    if m:
        print("matches:", dict(Counter(x["status"] for x in m)))


if __name__ == "__main__":
    main()
