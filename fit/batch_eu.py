"""The batch, EU (task 203b, GOAL.md points 1-2): every built site other than the US goes
through the same fitting loop as 203a's US batch (candidates -> fitkit sheet -> local model
-> plan_fit similarity -> the frozen gate -> an automatic platefit document or a review
item; a site with no candidate at all gets a "no picture found" item).

The loop itself is imported from fit/batch_us.py (203a's module) and is NOT re-implemented
here: this module owns only the EU site list, the EU report (203a's write_report with this
task's title, plus the union section below), the union check (box 2: the two batches'
documents and items against web/data/sites.json), and the CLI.

The EU site list is every site of web/data/sites.json whose region is not "US" - including
the 6 sites with no region field at all (forthill, fudge, highbank, hopeton, marietta,
newark), which must appear in this list, not be dropped. The shared recorded seed of the
sample of automatically accepted fits is 203a's SEED (20261010): the two reports' samples
draw from disjoint document sets, so one seed unambiguously reproduces both.

usage:
  python3 fit/batch_eu.py --working           [--root DIR] [--sites id ...]
  python3 fit/batch_eu.py --model-json F      [--root DIR] [--sites id ...]
  (the working run fetches missing pictures/aerials and calls the local vision model;
   the model-json run is a dry run with recorded answers, no network)
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch_us  # noqa: E402  (203a's loop; imported, not copied)


def eu_sites(root):
    """The built non-US site ids (region != "US" in web/data/sites.json - None included,
    so the 6 region-less sites are never dropped), sorted."""
    return sorted(sid for sid, s in batch_us._sites(root).items() if s.get("region") != "US")


def run_eu(root, model=None):
    """203a's fitting loop over the EU site list (run_sites' records, keyed by site id)."""
    return batch_us.run_sites(root, eu_sites(root), model)


def union_check(root):
    """Box 2: the union of the 203a (US) and 203b (non-US) batch outputs covers every built
    site exactly once, checked against web/data/sites.json.

    The partition comes from sites.json alone: 203a's list is region == "US", 203b's is
    everything else. plans.json rows never contribute to it: 230 of the 1166 rows list at
    least one site id that is not in sites.json (stale refs from dropped entries), and two
    rows (b24849959_n0228_1, ArcheologicalAtlasOfOhio_n0152_2) each list one US and one
    region-less site - one row, two sites, one document each, no collision (a document is
    named per (site, plan), and each batch writes only for the sites of its own list).

    Coverage is counted per site from the files on disk: a platefit document naming the
    site (data/db/platefits/<site>.*.json, keyed by the site field), a review item naming
    the site (any data/review/*.json whose site field matches - the file name's lead plan
    moves around under upsert, so the field, not the name, is the key), or the old-style
    hand fit (the site's data/sites/<site>/site.json plate fit - the 6 region-less sites
    carry theirs this way). "No site in both" is asserted at the list level (a site has
    exactly one region, so the two partition lists are disjoint) and at the file level by
    the orphans and bad-name checks below: a file that named a site outside sites.json, or
    a document whose name did not carry its own site, would be the only way a batch's
    output could speak for a site of the other partition.

    -> {"us", "eu", "regionless", "covered" {site: {"region", "docs", "items", "hand_fit",
    "covered"}}, "missing", "in_both", "orphan_docs", "orphan_items", "bad_doc_names"}
    """
    sites = batch_us._sites(root)
    us = sorted(sid for sid, s in sites.items() if s.get("region") == "US")
    eu = sorted(sid for sid, s in sites.items() if s.get("region") != "US")
    regionless = sorted(sid for sid in eu if not sites[sid].get("region"))

    docs, bad_doc_names, orphan_docs = {}, [], []
    d = Path(root) / "data" / "db" / "platefits"
    if d.is_dir():
        for p in sorted(d.iterdir()):
            if p.suffix != ".json":
                continue
            doc = json.loads(p.read_text())
            sid = doc.get("site")
            # the doc file is named <site>.<plan>.json: the name's site must be the site field
            if p.name.count(".") >= 2 and p.name.split(".")[0] != sid:
                bad_doc_names.append(p.name)
            if sid not in sites:
                orphan_docs.append(p.name)
                continue
            docs.setdefault(sid, []).append(p.name)

    items, orphan_items = {}, []
    r = Path(root) / "data" / "review"
    if r.is_dir():
        for p in sorted(r.iterdir()):
            if p.suffix != ".json":
                continue
            it = json.loads(p.read_text())
            sid = it.get("site")
            if sid not in sites:
                orphan_items.append(p.name)
                continue
            items.setdefault(sid, []).append(p.name)

    covered, missing = {}, []
    for sid in sorted(sites):
        p = Path(root) / "data" / "sites" / sid / "site.json"
        hand = False
        if p.is_file():
            try:
                hand = bool(((json.loads(p.read_text()).get("plate") or {}).get("fit")))
            except ValueError:
                pass
        d_ = docs.get(sid, [])
        i_ = items.get(sid, [])
        rec = {"region": sites[sid].get("region"), "docs": d_, "items": i_,
               "hand_fit": hand, "covered": bool(d_ or i_ or hand)}
        covered[sid] = rec
        if not rec["covered"]:
            missing.append(sid)

    return {"us": us, "eu": eu, "regionless": regionless, "covered": covered,
            "missing": missing, "in_both": sorted(set(us) & set(eu)),
            "orphan_docs": orphan_docs, "orphan_items": orphan_items,
            "bad_doc_names": bad_doc_names}


def union_section(check):
    """The union check as a report section (appended to docs/batch_eu.md)."""
    n = len(check["us"]) + len(check["eu"])
    n_docs = sum(len(v["docs"]) for v in check["covered"].values())
    n_items = sum(len(v["items"]) for v in check["covered"].values())
    n_hand = sum(1 for v in check["covered"].values() if v["hand_fit"])
    lines = ["## Union check (the 203a + 203b outputs vs web/data/sites.json)", ""]
    lines.append("%d built sites: %d US, %d other (the %d with no region field are in the other "
                 "list: %s). The partition lists are disjoint and their union is every built site."
                 % (n, len(check["us"]), len(check["eu"]), len(check["regionless"]),
                    ", ".join(check["regionless"])))
    lines.append("")
    lines.append("Coverage: %d covered, %d missing, %d in both. Documents: %d, review items: %d, "
                 "old-style site.json hand fits: %d."
                 % (sum(1 for v in check["covered"].values() if v["covered"]),
                    len(check["missing"]), len(check["in_both"]),
                    n_docs, n_items, n_hand))
    anomalies = []
    if check["missing"]:
        anomalies.append("missing: %s" % ", ".join(check["missing"]))
    if check["in_both"]:
        anomalies.append("in both partitions: %s" % ", ".join(check["in_both"]))
    if check["orphan_docs"]:
        anomalies.append("documents naming a site not in sites.json: %s" % ", ".join(check["orphan_docs"]))
    if check["orphan_items"]:
        anomalies.append("items naming a site not in sites.json: %s" % ", ".join(check["orphan_items"]))
    if check["bad_doc_names"]:
        anomalies.append("documents whose name does not carry their own site: %s" % ", ".join(check["bad_doc_names"]))
    lines.append("")
    lines.append("Anomalies: %s" % ("none" if not anomalies else "; ".join(anomalies)))
    return "\n".join(lines) + "\n"


def write_report(root, records, path=None):
    """docs/batch_eu.md: 203a's report writer (same format as docs/batch_us.md, the same
    recorded seed) with this task's union section appended over the tree's current state."""
    # path=None would fall through to batch_us's own default (docs/batch_us.md): pin ours
    out = batch_us.write_report(root, records, title="The batch, EU (203b)",
                                path=path or "docs/batch_eu.md")
    with open(out, "a") as f:
        f.write(union_section(union_check(root)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(ROOT), help="the project root (default: this checkout)")
    ap.add_argument("--sites", nargs="*", default=None,
                    help="site ids to run (default: every non-US built site)")
    ap.add_argument("--working", action="store_true",
                    help="the model is the local vision model on the fitkit sheet (network allowed)")
    ap.add_argument("--model-json", default=None,
                    help="recorded model answers (a dry run; no model server, no network)")
    ap.add_argument("--report", default=None, help="report path (default: docs/batch_eu.md)")
    a = ap.parse_args(argv)
    if a.working:
        model = batch_us.llm_model(a.root)
    elif a.model_json:
        model = batch_us.recorded_model(json.loads(Path(a.model_json).read_text()))
    else:
        ap.error("a model is required: --working (the local vision model) or --model-json (recorded answers)")
    site_ids = a.sites or eu_sites(a.root)
    records = batch_us.run_sites(a.root, site_ids, model)
    report = write_report(a.root, records, path=a.report)
    counts = batch_us.classify(records)
    check = union_check(a.root)
    print("batch EU: %d sites: %s" % (len(records),
          ", ".join("%d %s" % (len(v), k) for k, v in counts.items())))
    print("union: %d sites, %d missing, %d in both, %d orphan docs, %d orphan items" % (
        len(check["us"]) + len(check["eu"]), len(check["missing"]), len(check["in_both"]),
        len(check["orphan_docs"]), len(check["orphan_items"])))
    print("report:", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
