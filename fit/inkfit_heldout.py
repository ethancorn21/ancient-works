"""The one-shot held-out measurement of the ink fit (task 302b).

The protocol is pre-registered in docs/site_flow.md ("The one-shot held-out measurement of
the ink fit") BEFORE any document of the set was measured: the 21 documents (the original 20
of tests/golden/hand_fit_docs.sha256 plus the lead's 21st, maiden-castle-q1232816.c_c20ff6b1f16d173d,
all without an auto flag), the frozen method fit/inkfit.py (as of commit f7dbba6), the corner-error
metric, and the rule that the method never reads the hand pairs. This runner is the evaluator,
the ONLY reader of the hand fits: it runs the frozen method once per document (the method sees
only the site catalog, the plate picture and the relief), then compares the method's placement
with the hand fit's similarity (plan_fit.similarity on the document's stored pairs) and records,
per document: corner error in ground metres (RMS over the four full-image corners of the size
frame mapped to ground, k0 = aw.ground_scale at the mean hand-pair latitude), rotation error
((arg a_m - arg a_h) in (-180, 180] degrees), scale ratio, the frozen gate's verdict on the
method's own pairs, whether plan_fit.fabrication_pattern is silent on them, and the
search-matched-null margin.

One-shot discipline: each document is measured exactly once; the results checkpoint per
document into data/inkfit/heldout/results.json (a cut session resumes where it stopped). The
only permitted re-run is an entry that stored an exception (never a completed measurement);
it may happen once and is disclosed in the table's footnote. The run's timestamp is fixed
when the checkpoint is first created and stamped on every measurement.

usage:
  python3 fit/inkfit_heldout.py run            # the one-shot loop (resumable; a pid lock guards it)
  python3 fit/inkfit_heldout.py table          # the markdown table, generated verbatim from the checkpoint
  python3 fit/inkfit_heldout.py selfcheck [doc]  # the evaluator against itself: corner error must be 0.0
"""

import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import aw  # noqa: E402
import plan_fit  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkfit  # noqa: E402
import propose  # noqa: E402

GOLDEN = os.path.join(ROOT, "tests", "golden", "hand_fit_docs.sha256")
MAIDEN = "maiden-castle-q1232816.c_c20ff6b1f16d173d"   # the lead's 21st hand fit (no auto flag)
HOLDOUT = os.path.join(ROOT, "data", "inkfit", "heldout")
RESULTS = os.path.join(HOLDOUT, "results.json")
LOCK = os.path.join(HOLDOUT, "runner.pid")
METHOD_COMMIT = "f7dbba6"   # fit/inkfit.py as registered in the protocol


# ---------------------------------------------------------------- the held-out set

def golden_docs():
    """The 20 registered hand-fit document ids, in file order (path -> 'site.plan' stem)."""
    out = []   # the golden file also pins 19 site.json files: take only the platefit docs
    for line in open(GOLDEN):
        line = line.strip()
        if not line or "platefits/" not in line:
            continue
        out.append(line.split()[-1].split("platefits/")[-1][:-len(".json")])
    if len(out) != 20:
        raise SystemExit("expected the 20 golden hand-fit documents, found %d" % len(out))
    return out


def doc_ids():
    """The 21 held-out documents, sorted - exactly the list registered in the protocol."""
    return sorted(golden_docs() + [MAIDEN])


def precheck(ids):
    """Before the first measurement: the truth set is exactly what the protocol registered.
    Each golden doc's bytes still match its registered sha256, no doc carries an auto flag,
    and every doc resolves to a catalog site and a plans row. Aborts on any drift."""
    import hashlib
    pins = {}
    for line in open(GOLDEN):
        if line.strip() and "platefits/" in line:
            sha, path = line.split()
            pins[path.split("platefits/")[-1][:-len(".json")]] = sha
    for doc in ids:
        path = os.path.join(ROOT, "data", "db", "platefits", doc + ".json")
        if not os.path.exists(path):
            raise SystemExit("held-out document missing: %s" % path)
        hdoc = json.load(open(path))
        if hdoc.get("auto"):
            raise SystemExit("held-out document %s carries an auto flag: the truth set is void" % doc)
        if doc in pins:
            sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
            if sha != pins[doc]:
                raise SystemExit("held-out document %s no longer matches its golden sha256: the truth set is void" % doc)
        site, plan = doc.split(".", 1)
        propose._site(site)          # raises if the site is not in the catalog
        propose._plans_row(plan, site)  # raises if the plan row does not resolve
    print("precheck: 21 held-out documents verified (20 golden bytes + the lead's 21st, no auto flags)")


# ---------------------------------------------------------------- checkpoint

def _json_default(o):
    if isinstance(o, np.bool_):
        return bool(o)
    return float(o)


def load_results():
    if os.path.exists(RESULTS):
        res = json.load(open(RESULTS))
    else:
        res = {"at": datetime.now(timezone.utc).isoformat(), "docs": {}}
    res.setdefault("at", datetime.now(timezone.utc).isoformat())
    res.setdefault("docs", {})
    return res


def save_results(res):
    os.makedirs(HOLDOUT, exist_ok=True)
    tmp = RESULTS + ".tmp"
    json.dump(res, open(tmp, "w"), indent=1, default=_json_default)
    os.replace(tmp, RESULTS)   # atomic: a cut session never sees a half-written checkpoint


# ---------------------------------------------------------------- the evaluator

def corner_metrics(a_h, b_h, a_m, b_m, w, h, lat0):
    """The protocol's corner-error metric: both similarities are Web-Mercator similarities in the
    document's size frame (merc = a*(u - iv) + b); the four full-image corners mapped by both,
    their difference in Mercator metres at k0 = aw.ground_scale(lat0) (ground metres per Mercator
    metre at the mean hand-pair latitude) is the corner error - the autofit.Site.corner_rms
    convention. -> (corner error ground m, rotation error in (-180, 180] deg, scale ratio)."""
    corners = np.array([[0.0, 0.0], [w, 0.0], [w, h], [0.0, h]])
    ww = corners[:, 0] - 1j * corners[:, 1]
    err = (a_m - a_h) * ww + (b_m - b_h)
    k0 = aw.ground_scale(lat0)
    corner = float(np.sqrt(np.mean(np.abs(err) ** 2))) * k0
    drot = math.degrees(math.atan2(a_m.imag, a_m.real) - math.atan2(a_h.imag, a_h.real))
    drot = (drot + 180.0) % 360.0 - 180.0
    return round(corner, 1), round(drot, 2), round(abs(a_m) / abs(a_h), 4)


def hand_similarity(root, doc, row):
    """The hand fit's similarity in the document's size frame: a, b (Web-Mercator convention),
    the size frame and the mean hand-pair latitude. This function is the ONLY place the
    stored hand pairs are read."""
    hdoc = json.load(open(os.path.join(ROOT, "data", "db", "platefits", doc + ".json")))
    a, b, _resid, _k = plan_fit.similarity(hdoc["pairs"])
    size = hdoc.get("size") or row.get("size")
    if not size:
        raise SystemExit("held-out document %s has no size frame" % doc)
    lat0 = float(np.mean([p[3] for p in hdoc["pairs"]]))
    return a, b, float(size[0]), float(size[1]), lat0


def measure(root, doc, at, reruns):
    """One held-out document: the frozen method once, then the evaluator's comparison with the
    hand fit. Any exception is stored as {"error": ...} (the one re-run this permits)."""
    site, plan = doc.split(".", 1)
    se = propose._site(site)
    row = propose._plans_row(plan, site)
    try:
        def log(*a):
            print("    " + " ".join(str(x) for x in a), flush=True)

        r = inkfit.fit(se, row, model=None, null=True, at=at, log=log)
    except Exception as e:
        return {"doc": doc, "site": site, "plan": plan, "reruns": reruns, "error": repr(e)}
    a_h, b_h, w, h, lat0 = hand_similarity(root, doc, row)
    placed = r["placement"] is not None
    corner = drot = scale = None
    if placed:
        a_m = complex(r["placement"]["a"][0], r["placement"]["a"][1])
        b_m = complex(r["placement"]["b"][0], r["placement"]["b"][1])
        corner, drot, scale = corner_metrics(a_h, b_h, a_m, b_m, w, h, lat0)
    entry = {
        "doc": doc, "site": site, "plan": plan, "at": at, "reruns": reruns,
        "model": r["model"], "reason": r["reason"],
        "n_pieces": r["n_pieces"], "n_points": r["n_points"], "seed": r["seed"],
        "objective": r["objective"], "null": r["null"], "confidence": r["confidence"],
        "placed": placed,
        "corner_error_m": corner, "drot_deg": drot, "scale_ratio": scale,
        "gate": r["gate"], "fabrication": r["fabrication"],
        "seconds": r["seconds"],
    }
    return entry


# ---------------------------------------------------------------- the one-shot run

def _lock_alive():
    if not os.path.exists(LOCK):
        return False
    try:
        pid = int(open(LOCK).read().strip())
        cmd = open("/proc/%d/cmdline" % pid, "rb").read().decode(errors="ignore")
        if "inkfit_heldout" not in cmd:
            return False
        os.kill(pid, 0)
        return True
    except (ValueError, OSError):
        return False


def run(argv):
    os.makedirs(HOLDOUT, exist_ok=True)
    if _lock_alive():
        print("another runner is active (pid %s); refusing to double-run" % open(LOCK).read().strip())
        return 1
    open(LOCK, "w").write(str(os.getpid()))
    try:
        ids = doc_ids()
        res = load_results()
        precheck(ids)
        done_before = sum(1 for d in ids if "error" not in res["docs"].get(d, {}))
        print("one-shot run: %d/21 measured already, run at %s" % (done_before, res["at"]))
        for i, doc in enumerate(ids, 1):
            e = res["docs"].get(doc)
            if e is not None and "error" not in e:
                print("[%d/21] %s: measured (checkpoint), skipping" % (i, doc), flush=True)
                continue
            if e is not None and int(e.get("reruns", 0)) >= 1:
                print("[%d/21] %s: error stands (re-run already used): %s" % (i, doc, e.get("error")), flush=True)
                continue
            reruns = 0 if e is None else int(e.get("reruns", 0)) + 1
            if e is not None:
                print("[%d/21] %s: RE-RUN 1 (disclosed) after %s" % (i, doc, e.get("error")), flush=True)
            t0 = time.time()
            print("[%d/21] %s: fitting..." % (i, doc), flush=True)
            entry = measure(ROOT, doc, res["at"], reruns)
            res["docs"][doc] = entry
            save_results(res)
            if "error" in entry:
                print("[%d/21] %s: ERROR after %.0fs: %s" % (i, doc, time.time() - t0, entry["error"]), flush=True)
            else:
                print("[%d/21] %s: %.0fs  placed=%s  corner=%s m  drot=%s  scale=%s  "
                      "null=%s  margin=%s  gate=%s  fab=%s" % (
                          i, doc, time.time() - t0, entry["placed"], entry["corner_error_m"],
                          entry["drot_deg"], entry["scale_ratio"], entry["null"],
                          entry["confidence"],
                          (entry["gate"] or {}).get("verdict"), entry["fabrication"]), flush=True)
        all_done = all("error" not in res["docs"][d] or int(res["docs"][d].get("reruns", 0)) >= 1 for d in ids)
        if all_done:
            print("\n" + table(res))
    finally:
        try:
            os.remove(LOCK)
        except OSError:
            pass
    return 0


# ---------------------------------------------------------------- the table

def _f(x, dp):
    return "—" if x is None else ("%.*f" % (dp, x))


def table(res):
    """The markdown table of the run, generated verbatim from the checkpoint (the box-3 text:
    one row per document, measured as-is, good or bad; unplaced documents carry the method's
    reason in the corner-error cell; a footnote discloses any exception re-run and the run's
    fixed timestamp)."""
    ids = doc_ids()
    rows = []
    rerun_note = []
    for i, doc in enumerate(ids, 1):
        e = res["docs"].get(doc)
        if e is None:
            rows.append("| %d | %s | not yet measured | | | | | | |" % (i, doc))
            continue
        if "error" in e:
            rows.append("| %d | %s | ERROR: %s | | | | | | |" % (i, doc, e["error"]))
            if int(e.get("reruns", 0)) >= 1:
                rerun_note.append(doc)
            continue
        if e["placed"]:
            corner = _f(e["corner_error_m"], 1)
            drot = _f(e["drot_deg"], 2)
            scale = _f(e["scale_ratio"], 4)
        else:
            corner = drot = scale = e["reason"] or "not placed"
        obj = (e["objective"] or {}).get("fit")
        rows.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            i, doc, corner, drot, scale,
            _f(obj, 4), _f(e["null"], 4), _f(e["confidence"], 4),
            (e["gate"] or {}).get("verdict") if e["gate"] else "—",
            "silent" if e["fabrication"] is None else e["fabrication"]))
        if int(e.get("reruns", 0)) >= 1:
            rerun_note.append(doc)
    head = (
        "**Measured one-shot, run at %s.** Method: `fit/inkfit.py` as of commit %s, the frozen "
        "no-model variant (the protocol above). Each document measured once; a document the "
        "method could not place carries the method's reason in the corner-error cell. Rounding: "
        "corner error 0.1 m, rotation 0.01 deg, scale 0.0001, objectives 0.0001.\n"
        % (res["at"], METHOD_COMMIT)
    )
    cols = ("| # | document | corner error (m) | rotation error (deg) | scale ratio | objective | null | null margin | gate | fabrication |")
    rule = "|---|---|---|---|---|---|---|---|---|---|"
    foot = ""
    if rerun_note:
        foot = "\n\nFootnote: measured twice (an exception on the first attempt, the one re-run the protocol permits): %s.\n" % ", ".join(rerun_note)
    return head + "\n" + cols + "\n" + rule + "\n" + "\n".join(rows) + foot


def selfcheck(argv):
    """The evaluator against itself: the hand similarity compared with itself must give a
    corner error of exactly 0.0 (rotation 0.0, scale 1.0) - proves the metric and the
    size-frame handling without the method, without any network."""
    ids = doc_ids() if not argv else [argv[0]]
    for doc in ids:
        site, plan = doc.split(".", 1)
        row = propose._plans_row(plan, site)
        a, b, w, h, lat0 = hand_similarity(ROOT, doc, row)
        c, drot, scale = corner_metrics(a, b, a, b, w, h, lat0)
        status = "OK" if (c == 0.0 and drot == 0.0 and scale == 1.0) else "FAIL"
        print("%-55s %s  corner %.1f m, drot %.2f deg, scale %.4f  (size %dx%d, lat0 %.5f)"
              % (doc, status, c, drot, scale, w, h, lat0))
        if status == "FAIL":
            return 1
    return 0


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    mode, rest = argv[0], argv[1:]
    if mode == "run":
        return run(rest)
    if mode == "table":
        print(table(load_results()))
        return 0
    if mode == "selfcheck":
        return selfcheck(rest)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
