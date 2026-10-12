"""Queue yield of the matcher fit under any accept rule: record every fit_row() result, then read rules off
the record (docs/matchfit.md section 8).

fit/matchfit.py prints only the verdict of its built-in rule (count >= MIN_INLIERS, |rot| <= MAX_ROT_DEG,
spread guard), so a RoMa pass through it hides the inlier fraction of everything it rejects. This runner calls
the same fit_row() on every picture of every queue site and writes the whole best candidate (inliers, matches,
rot, ground, window, spread, m/px, residual) to one JSON line per picture; `table` then applies a rule.

  .venv/bin/python fit/matchfit_queue.py run --matcher http://127.0.0.1:8092 --out data/matchfit/queue_roma/results.jsonl
  .venv/bin/python fit/matchfit_queue.py table data/matchfit/queue_roma/results.jsonl [--min-frac 0.3] [--rot90]

Nothing is written to the site documents; this is a measurement, the line wires its own rule.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matchfit as mf  # noqa: E402
from matchfit import batch_us  # noqa: E402


def run(root, out, url, site_ids=None):
    sites = mf._sites(root)
    rows = batch_us._plans_rows(str(root))
    q = json.loads((Path(root) / "web" / "data" / "fit_queue.json").read_text())
    ids = site_ids or [e["site"] for e in q.get("entries", [])]
    done = set()
    outp = Path(out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    if outp.is_file():
        for ln in outp.read_text().splitlines():
            if ln.strip():
                d = json.loads(ln)
                done.add((d["site"], d["doc"]))
    with outp.open("a") as fh:
        for sid in ids:
            site = sites.get(sid)
            if not site:
                print(f"{sid}: not a built site", flush=True)
                continue
            docs = dict(batch_us.pre_docs(str(root), sid))
            for row in batch_us.candidates(sid, rows):
                if row["id"] in docs or (sid, row["id"]) in done:
                    continue
                t0 = time.time()
                r = mf.fit_row(root, site, row, url)
                r.pop("pairs", None)
                rec = {"site": sid, "doc": row["id"], "title": (row.get("title") or row["id"])[:80],
                       "seconds": round(time.time() - t0, 1), **r}
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                tag = f"{rec.get('inliers', 0)}/{rec.get('matches', 0)} rot {rec.get('rot', 0):.0f}" if "inliers" in rec else "nothing"
                print(f"{sid}  {rec['title'][:50]}: {tag}  {rec.get('why', 'FIT')}", flush=True)


def near90(rot, tol=10.0):
    return abs(((rot + 45) % 90) - 45) <= tol


def table(path, min_frac, rot90, max_rot, min_count=None):
    recs = [json.loads(ln) for ln in Path(path).read_text().splitlines() if ln.strip()]
    acc, rej = [], {}
    for r in recs:
        if "inliers" not in r or not r.get("matches"):
            rej["nothing"] = rej.get("nothing", 0) + 1
            continue
        frac = r["inliers"] / r["matches"]
        ok_rot = near90(r["rot"]) if rot90 else abs(r["rot"]) <= max_rot
        ok_n = frac >= min_frac if min_count is None else r["inliers"] >= min_count
        sp = r.get("spread") or [0, 0]
        ok_sp = sp[0] >= mf.SPREAD_MIN_RATIO and sp[1] >= mf.SPREAD_MIN_SD_PX
        if ok_n and ok_rot and ok_sp:
            acc.append((frac, r))
        else:
            k = "count" if not ok_n else ("rot" if not ok_rot else "spread")
            rej[k] = rej.get(k, 0) + 1
    print(f"{len(recs)} pictures: accepted {len(acc)} on {len({r['site'] for _, r in acc})} sites; rejected {rej}")
    for frac, r in sorted(acc, key=lambda x: -x[0]):
        print(f"  {r['site'][:30]:30s} {r['title'][:44]:44s} {frac:.2f} {r['inliers']:4d}/{r['matches']:<4d} "
              f"{r['ground'][:16]:16s} x{r['window']:<4} rot {r['rot']:6.1f} sp {r['spread'][0]:.2f}/{r['spread'][1]:.0f} "
              f"{r['m_per_px']:.2f} m/px res {r['resid_m']:.0f} m")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["run", "table"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--root", default=str(mf.ROOT))
    ap.add_argument("--matcher", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--sites", nargs="*")
    ap.add_argument("--min-frac", type=float, default=0.3)
    ap.add_argument("--min-count", type=int, default=None, help="use the ELoFTR count rule instead of fraction")
    ap.add_argument("--rot90", action="store_true", help="rotation within 10 deg of k x 90 instead of |rot| <= MAX_ROT_DEG")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        run(a.root, a.out or a.path, a.matcher, a.sites)
    else:
        table(a.path, a.min_frac, a.rot90, mf.MAX_ROT_DEG, a.min_count)


if __name__ == "__main__":
    main()
