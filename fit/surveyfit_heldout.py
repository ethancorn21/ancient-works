"""The one-shot held-out measurement of the survey-sheet fit (task 304).

The protocol is pre-registered in docs/site_flow.md ("The one-shot held-out measurement of
the survey-sheet fit") BEFORE any document of the set was measured by this method: the
21 documents (the 21 hand fits pinned in tests/golden/hand_fit_docs.sha256 - the original
20 plus the lead's 21st, the DPLA Maiden Castle plan, all without an auto flag), the frozen
method fit/surveyfit.py (as of commit 737508d), the corner-error metric (identical to the
302b one), and the rule that the method never reads the hand pairs. This runner is the
evaluator, the ONLY reader of the hand fits: it runs the frozen method once per
(document, ground) pair - each document against its site's finest-scale survey sheet, plus
camp-d-attila (the only held-out site with an aerial depiction) against its 1957 aerial,
the sheet row first - then compares the method's placement with the hand fit's similarity
(plan_fit.similarity on the document's stored pairs) and records, per pair: corner error in
ground metres (RMS over the four full-image corners of the size frame mapped to ground,
k0 = aw.ground_scale at the mean hand-pair latitude), rotation error ((arg a_m - arg a_h)
in (-180, 180] degrees), scale ratio, the objective, the null, the margin and the
confidence.

One-shot discipline: each (document, ground) pair is measured exactly once; the results
checkpoint per pair into data/surveyfit/heldout/results.json (a cut session resumes where
it stopped). The only permitted re-run is an entry that stored an exception (never a
completed measurement); it may happen once and is disclosed in the table's footnote. The
run's timestamp is fixed when the checkpoint is first created and stamped on every
measurement.

usage:
  .venv/bin/python fit/surveyfit_heldout.py run            # the one-shot loop (resumable; a pid lock guards it)
  .venv/bin/python fit/surveyfit_heldout.py table          # the markdown table, generated verbatim from the checkpoint
  .venv/bin/python fit/surveyfit_heldout.py selfcheck [doc]  # the evaluator against itself: corner error must be 0.0
"""

import hashlib
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
import propose  # noqa: E402
import surveyfit  # noqa: E402

GOLDEN = os.path.join(ROOT, "tests", "golden", "hand_fit_docs.sha256")
HOLDOUT = os.path.join(ROOT, "data", "surveyfit", "heldout")
RESULTS = os.path.join(HOLDOUT, "results.json")
LOCK = os.path.join(HOLDOUT, "runner.pid")
METHOD_COMMIT = "737508d"   # fit/surveyfit.py as registered in the protocol
AERIAL_DOC = "camp-d-attila-q18749222.c_6a912845c1e1aa28"   # the only held-out site with an aerial

# The 21 held-out documents - exactly the list registered in the 302b section of
# docs/site_flow.md (the 20 golden hand fits plus the lead's 21st).
DOCS_302B = [
    "arbor-low-q630312.earthworkenglan01allcgoog_n0597_1",
    "avebury-q661855.earthworkenglan01allcgoog_n0581_1",
    "aztalan-state-park-q4832928.antiquitiesofwis00saph_n0182_1",
    "badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1",
    "bergues-q244934.c_4bbca705be732b1c",
    "berkhamsted-castle-q4892150.c_1699141d593ead5a",
    "cadbury-castle-q1025082.c_1fab2a0abe5b99d7",
    "cahokia-q333661.c_aff1b996dce7fe3a",
    "calleva-atrebatum-q1027253.earthworkenglan01allcgoog_n0360_1",
    "camp-d-attila-q18749222.c_6a912845c1e1aa28",
    "castle-rising-castle-q1049485.c_70f937b71ae63d6a",
    "hembury-q3784763.earthworkenglan01allcgoog_n0108_1",
    "little-solsbury-hill-q548780.c_7ff7261c6b3574b6",
    "maiden-castle-q1232816.c_c20ff6b1f16d173d",
    "maiden-castle-q1232816.earthworkenglan01allcgoog_n0124_1",
    "mayburgh-henge-q1469390.c_984782b9e35e8ded",
    "mound-bottom-q14710093.c_0b98157d7af17d6e",
    "old-sarum-q782719.c_8192abb966d030a3",
    "old-sarum-q782719.earthworkenglan01allcgoog_n0142_1",
    "serpent-mound-q968802.ancientmonuments00squi_n0210_1",
    "whitley-castle-q7996561.c_802bb5ba395d4d29",
]


# ---------------------------------------------------------------- the held-out set

def golden_docs():
    """The hand-fit document ids pinned in the golden file, in file order (path -> stem)."""
    out = []
    for line in open(GOLDEN):
        line = line.strip()
        if not line or "platefits/" not in line:
            continue
        out.append(line.split()[-1].split("platefits/")[-1][:-len(".json")])
    return out


def doc_ids():
    """The 21 held-out documents, sorted - exactly the list registered in the protocol."""
    golden = golden_docs()
    if len(golden) != 21 or set(golden) != set(DOCS_302B):
        raise SystemExit("the golden file no longer pins exactly the 21 registered held-out "
                         "documents (%d pinned): the truth set is void" % len(golden))
    return sorted(DOCS_302B)


def precheck(ids):
    """Before the first measurement: the truth set is exactly what the protocol registered.
    Every doc's bytes still match its registered sha256, no doc carries an auto flag, and
    every doc resolves to a catalog site and a plans row. Aborts on any drift."""
    pins = {}
    for line in open(GOLDEN):
        line = line.strip()
        if not line or "platefits/" not in line:
            continue
        sha, path = line.split()
        pins[path.split("platefits/")[-1][:-len(".json")]] = sha
    for doc in ids:
        path = os.path.join(ROOT, "data", "db", "platefits", doc + ".json")
        if not os.path.exists(path):
            raise SystemExit("held-out document missing: %s" % path)
        hdoc = json.load(open(path))
        if hdoc.get("auto"):
            raise SystemExit("held-out document %s carries an auto flag: the truth set is void" % doc)
        sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if sha != pins.get(doc):
            raise SystemExit("held-out document %s no longer matches its golden sha256: the truth set is void" % doc)
        site, plan = doc.split(".", 1)
        propose._site(site)          # raises if the site is not in the catalog
        propose._plans_row(plan, site)  # raises if the plan row does not resolve
    print("precheck: 21 held-out documents verified (21 pinned in the golden file, no auto flags)")


# ---------------------------------------------------------------- checkpoint

def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
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


def _key(doc, ground):
    """The checkpoint key of a (document, ground) pair: the doc for the sheet, the doc plus
    ' (aerial)' for the aerial (camp-d-attila only)."""
    return doc if ground == "sheet" else doc + " (aerial)"


# ---------------------------------------------------------------- the evaluator

def corner_metrics(a_h, b_h, a_m, b_m, w, h, lat0):
    """The protocol's corner-error metric (identical to the 302b one): both similarities are
    Web-Mercator similarities in the document's size frame (merc = a*(u - iv) + b); the four
    full-image corners mapped by both, their difference in Mercator metres at k0 =
    aw.ground_scale(lat0) (ground metres per Mercator metre at the mean hand-pair latitude)
    is the corner error - the autofit.Site.corner_rms convention. -> (corner error ground m,
    rotation error in (-180, 180] deg, scale ratio)."""
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
    hdoc = json.load(open(os.path.join(root, "data", "db", "platefits", doc + ".json")))
    a, b, _resid, _k = plan_fit.similarity(hdoc["pairs"])
    size = hdoc.get("size") or row.get("size")
    if not size:
        raise SystemExit("held-out document %s has no size frame" % doc)
    lat0 = float(np.mean([p[3] for p in hdoc["pairs"]]))
    return a, b, float(size[0]), float(size[1]), lat0


def measure(root, doc, at, reruns, ground):
    """One held-out (document, ground) pair: the frozen method once, then the evaluator's
    comparison with the hand fit. ground = 'sheet' (the site's finest-scale map/topo
    depiction, the method's default) or 'aerial' (camp-d-attila's 1957 ortho). Any
    exception is stored as {"error": ...} (the one re-run this permits)."""
    site, plan = doc.split(".", 1)
    se = propose._site(site)
    row = propose._plans_row(plan, site)
    kinds = ("aerial",) if ground == "aerial" else surveyfit.SHEET_KINDS
    try:
        def log(*a):
            print("    " + " ".join(str(x) for x in a), flush=True)

        r = surveyfit.fit(se, row, null=True, kinds=kinds, at=at, log=log)
    except Exception as e:
        return {"doc": doc, "site": site, "plan": plan, "ground": ground,
                "reruns": reruns, "error": repr(e)}
    a_h, b_h, w, h, lat0 = hand_similarity(root, doc, row)
    placed = r["placement"] is not None
    corner = drot = scale = None
    if placed:
        a_m = complex(r["placement"]["a"][0], r["placement"]["a"][1])
        b_m = complex(r["placement"]["b"][0], r["placement"]["b"][1])
        corner, drot, scale = corner_metrics(a_h, b_h, a_m, b_m, w, h, lat0)
    sheet = r.get("sheet")
    return {
        "doc": doc, "site": site, "plan": plan, "ground": ground, "at": at, "reruns": reruns,
        "reason": r["reason"],
        "sheet_file": (sheet or {}).get("file"),
        "sheet_scale": (sheet or {}).get("scale"),
        "priors": r["priors"], "theta": r["theta"],
        "n_matches": r["n_matches"], "n_inliers": r["n_inliers"], "rms_px": r["rms_px"],
        "objective": r["objective"], "null": r["null"], "margin": r["margin"],
        "confidence": r["confidence"],
        "placed": placed,
        "corner_error_m": corner, "drot_deg": drot, "scale_ratio": scale,
        "seconds": r["seconds"],
    }


# ---------------------------------------------------------------- the one-shot run

def pairs():
    """The (document, ground) pairs in protocol order: every doc against its sheet; the
    aerial pair (camp-d-attila only) directly after its sheet row."""
    out = [(doc, "sheet") for doc in doc_ids()]
    out.insert(out.index((AERIAL_DOC, "sheet")) + 1, (AERIAL_DOC, "aerial"))
    return out


def _lock_alive():
    if not os.path.exists(LOCK):
        return False
    try:
        pid = int(open(LOCK).read().strip())
        cmd = open("/proc/%d/cmdline" % pid, "rb").read().decode(errors="ignore")
        if "surveyfit_heldout" not in cmd:
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
        ps = pairs()
        done_before = sum(1 for p in ps
                          if _key(*p) in res["docs"] and "error" not in res["docs"][_key(*p)])
        print("one-shot run: %d/%d pairs measured already, run at %s"
              % (done_before, len(ps), res["at"]))
        for i, (doc, ground) in enumerate(ps, 1):
            key = _key(doc, ground)
            e = res["docs"].get(key)
            if e is not None and "error" not in e:
                print("[%d/%d] %s (%s): measured (checkpoint), skipping" % (i, len(ps), doc, ground), flush=True)
                continue
            if e is not None and int(e.get("reruns", 0)) >= 1:
                print("[%d/%d] %s (%s): error stands (re-run already used): %s"
                      % (i, len(ps), doc, ground, e.get("error")), flush=True)
                continue
            reruns = 0 if e is None else int(e.get("reruns", 0)) + 1
            if e is not None:
                print("[%d/%d] %s (%s): RE-RUN 1 (disclosed) after %s"
                      % (i, len(ps), doc, ground, e.get("error")), flush=True)
            t0 = time.time()
            print("[%d/%d] %s (%s): fitting..." % (i, len(ps), doc, ground), flush=True)
            entry = measure(ROOT, doc, res["at"], reruns, ground)
            res["docs"][key] = entry
            save_results(res)
            if "error" in entry:
                print("[%d/%d] %s (%s): ERROR after %.0fs: %s"
                      % (i, len(ps), doc, ground, time.time() - t0, entry["error"]), flush=True)
            else:
                print("[%d/%d] %s (%s): %.0fs  placed=%s  corner=%s m  drot=%s  scale=%s  "
                      "null=%s  margin=%s  conf=%s" % (
                          i, len(ps), doc, ground, time.time() - t0, entry["placed"],
                          entry["corner_error_m"], entry["drot_deg"], entry["scale_ratio"],
                          entry["null"], entry["margin"], entry["confidence"]), flush=True)
        all_done = all("error" not in res["docs"].get(k, {}) or int(res["docs"][k].get("reruns", 0)) >= 1
                       for k in (_key(*p) for p in ps))
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


def _ground_label(doc, ground, e):
    if ground == "aerial":
        return "aerial %s" % (e["sheet_file"] if e else "fr_ortho1950.webp")
    if e and e.get("sheet_file"):
        return "sheet %s %s" % (e["sheet_file"], e.get("sheet_scale") or "n.s.")
    if e and e.get("reason") and e["reason"].startswith("no sheet"):
        return "no sheet"
    return "sheet (the site's finest-scale map/topo)"


def table(res):
    """The markdown table of the run, generated verbatim from the checkpoint (the box-2
    text: one row per (document, ground) pair, measured as-is, good or bad; an unplaced
    pair carries the method's reason in the corner-error cell; a footnote discloses any
    exception re-run and the run's fixed timestamp)."""
    ps = pairs()
    rows = []
    rerun_note = []
    for i, (doc, ground) in enumerate(ps, 1):
        e = res["docs"].get(_key(doc, ground))
        if e is None:
            rows.append("| %d | %s | %s | not yet measured | | | | | | |"
                        % (i, doc, _ground_label(doc, ground, None)))
            continue
        if "error" in e:
            rows.append("| %d | %s | %s | ERROR: %s | | | | | | |"
                        % (i, doc, _ground_label(doc, ground, e), e["error"]))
            if int(e.get("reruns", 0)) >= 1:
                rerun_note.append(_key(doc, ground))
            continue
        if e["placed"]:
            corner = _f(e["corner_error_m"], 1)
            drot = _f(e["drot_deg"], 2)
            scale = _f(e["scale_ratio"], 4)
        else:
            corner = drot = scale = e["reason"] or "not placed"
        obj = (e["objective"] or {}).get("fit")
        rows.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            i, doc, _ground_label(doc, ground, e), corner, drot, scale,
            _f(obj, 4), _f(e["null"], 4), _f(e["margin"], 4), _f(e["confidence"], 4)))
        if int(e.get("reruns", 0)) >= 1:
            rerun_note.append(_key(doc, ground))
    head = (
        "**Measured one-shot, run at %s.** Method: `fit/surveyfit.py` as of commit %s, "
        "frozen (the protocol above). Each (document, ground) pair measured once; a pair "
        "the method could not place carries the method's reason in the corner-error cell. "
        "Rounding: corner error 0.1 m, rotation 0.01 deg, scale 0.0001, objectives 0.0001.\n"
        % (res["at"], METHOD_COMMIT)
    )
    cols = ("| # | document | ground | corner error (m) | rotation error (deg) | scale ratio "
            "| objective | null | margin | confidence |")
    rule = "|---|---|---|---|---|---|---|---|---|---|"
    foot = ""
    if rerun_note:
        foot = "\n\nFootnote: measured twice (an exception on the first attempt, the one " \
               "re-run the protocol permits): %s.\n" % ", ".join(rerun_note)
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
