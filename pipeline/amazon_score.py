"""Score the frozen Amazon Finder on the test strips against the frozen positives (docs/finder_amazon.md section 1).

usage: amazon_score.py   (reads data/finder/amazon/positives.json and the strips' *.cands.json; prints aggregates
                          only: never candidate coordinates)

K: 20 candidates per 100 km2 of swath, pooled over the test strips (top round(0.2 * total km2) by rank_score).
A positive is recalled if a top-K candidate in its strip lies within max(60 m, half its radius) of the point.
Also printed: every positive's rank inside its own strip (first candidate within tolerance), or "none".
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amazon_dtm  # noqa: E402

D = "data/finder/amazon"


def main():
    pos = json.load(open(f"{D}/positives.json"))["positives"]
    strips = sorted({p["strip"] for p in pos})
    runs = {s: json.load(open(f"{D}/dtm/{s}.cands.json")) for s in strips}
    area = sum(r["area_km2"] for r in runs.values())
    K = round(0.2 * area)
    pooled = sorted(((c["rank_score"], s, i) for s, r in runs.items() for i, c in enumerate(r["candidates"])),
                    reverse=True)[:K]
    top = {(s, i) for _, s, i in pooled}
    hits = 0
    print(f"strips {len(strips)}  swath {area:.2f} km2  K pooled = {K}  positives n = {len(pos)}")
    for n, p in enumerate(pos, 1):
        meta = runs[p["strip"]]["meta"]
        r0, c0 = amazon_dtm.to_frame(meta, p["x"], p["y"])
        rank, hit = None, False
        for i, c in enumerate(runs[p["strip"]]["candidates"]):
            d = math.hypot(c["row"] - r0, c["col"] - c0) * meta["px_m"]
            if d <= max(60.0, 0.5 * c["r_m"]):
                rank = rank or i + 1
                hit = hit or (p["strip"], i) in top
        hits += hit
        n_c = len(runs[p["strip"]]["candidates"])
        print(f"  positive {n} ({p['strip']}): in-strip rank {rank or 'none'} of {n_c}; in pooled top-K: {hit}")
    print(f"recall at K = {K}: {hits} of {len(pos)} (indicative, n < 15)")
    for s, r in runs.items():
        print(f"  {s}: {r['area_km2']} km2, {len(r['candidates'])} candidates, top score "
              f"{r['candidates'][0]['rank_score'] if r['candidates'] else '-'}")


if __name__ == "__main__":
    main()
