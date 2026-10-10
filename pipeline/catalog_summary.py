"""data/catalog/summary.md from sites.jsonl (+ build meta, US coverage and triage results when present).

usage: catalog_summary.py   (or catalog.py summary)
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "catalog")
RAW = os.path.join(ROOT, "data", "raw", "catalog")
REGIONS = ["us", "england", "wales", "netherlands", "france"]

# famous works to look for: (region, display name, QID if known else None, name pattern)
FAMOUS = [
    ("us", "Serpent Mound", "Q968802", r"serpent mound"),
    ("us", "Cahokia", "Q333661", r"^cahokia"),
    ("us", "Monks Mound (Cahokia)", "Q280444", r"monks mound"),
    ("us", "Poverty Point", "Q964745", r"poverty point"),
    ("us", "Newark Earthworks", "Q7016678", r"newark earthworks"),
    ("us", "Fort Ancient", "Q5470727", r"^fort ancient"),
    ("us", "Fort Hill (Ohio)", None, r"^fort hill"),
    ("us", "High Bank Works", None, r"high bank"),
    ("us", "Hopeton Earthworks", "Q5899962", r"hopeton"),
    ("us", "Marietta Earthworks", "Q6763227", r"marietta earthworks"),
    ("us", "Mound City Group", None, r"^mound city group"),
    ("us", "Hopewell Mound Group", None, r"hopewell mound group"),
    ("us", "Seip Earthworks", "Q123916810", r"^seip"),
    ("us", "Grave Creek Mound", "Q5597781", r"grave creek"),
    ("us", "Miamisburg Mound", "Q34827561", r"miamisburg"),
    ("us", "Etowah", "Q4533107", r"etowah"),
    ("us", "Moundville", "Q1320821", r"moundville"),
    ("us", "Ocmulgee", "Q1517500", r"ocmulgee"),
    ("us", "Kincaid Mounds", "Q4220862", r"kincaid"),
    ("us", "Spiro Mounds", "Q2044290", r"spiro"),
    ("us", "Pinson Mounds", "Q4363053", r"pinson"),
    ("us", "Angel Mounds", "Q4530064", r"angel mounds"),
    ("us", "Aztalan", "Q4832928", r"aztalan"),
    ("us", "Effigy Mounds NM", "Q1296201", r"effigy mounds national"),
    ("us", "Toltec Mounds", None, r"toltec"),
    ("us", "Winterville Mounds", None, r"winterville"),
    ("us", "Emerald Mound", None, r"emerald mound"),
    ("us", "Crystal River", None, r"crystal river"),
    ("us", "Watson Brake", None, r"watson brake"),
    ("england", "Maiden Castle (Dorset)", "Q1232816", r"^maiden castle"),
    ("england", "Avebury", "Q661855", r"^avebury"),
    ("england", "Silbury Hill", "Q225896", r"silbury"),
    ("england", "Stonehenge", "Q39671", r"^stonehenge$"),
    ("england", "West Kennet Long Barrow", None, r"west kennet"),
    ("england", "Sutton Hoo", "Q503256", r"^sutton hoo$"),
    ("england", "Danebury", None, r"danebury"),
    ("england", "Uffington Castle", None, r"uffington castle"),
    ("england", "Old Sarum", "Q782719", r"old sarum"),
    ("england", "Thornborough Henges", "Q2428964", r"thornborough"),
    ("england", "Offa's Dyke (spans England and Wales)", "Q1127343", r"^offa'?s dyke$"),
    ("england", "Windmill Hill (Avebury)", "Q4348373", r"^windmill hill$"),
    
    ("netherlands", "Hunneschans", None, r"hunneschans"),
    ("netherlands", "Ezinge (wierde)", None, r"ezinge"),
    ("france", "Bougon tumuli", None, r"bougon"),
    ("france", "Tumulus Saint-Michel", None, r"saint-michel"),
    ("france", "Gergovie", None, r"gergovi"),
    ("france", "Alesia", None, r"al[eé]sia"),
    ("france", "Bibracte", None, r"bibracte"),
]


def load(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def admin_str(s):
    a = s.get("admin", {})
    keys = {"us": ("county", "state"), "england": ("district", "county"), "wales": ("county",),
            "netherlands": ("municipality", "province"), "france": ("departement",)}[s["region"]]
    return ", ".join(a[k] for k in keys if a.get(k))


def find_famous(sites, region, q, pat):
    """By QID first (any region; members and merged items too), else by name pattern in the region."""
    rx = re.compile(pat, re.I)
    if q:
        for s in sites:
            if s.get("qid") == q:
                return [(s, None, "qid")]
            for m in s.get("members", []):
                if m["qid"] == q:
                    return [(s, m, "qid (member)")]
            for m in s.get("merged_from", []):
                if m["qid"] == q:
                    return [(s, None, "qid (merged into)")]
    hits = []
    for s in sites:
        if s["region"] != region:
            continue
        names = [s["name"]] + s.get("aliases", [])
        if any(rx.search(n) for n in names):
            hits.append((s, None, "name"))
        for m in s.get("members", []):
            if rx.search(m["name"]):
                hits.append((s, m, "name (member)"))
    return hits


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows]
    return "\n".join(out)


def main():
    sites = load(os.path.join(OUT, "sites.jsonl"))
    meta = json.load(open(os.path.join(RAW, "build_meta.json"))) if os.path.exists(os.path.join(RAW, "build_meta.json")) else {}
    cov = {r["id"]: r for r in load(os.path.join(OUT, "us_coverage.jsonl"))}
    tv = json.load(open(os.path.join(OUT, "triage_validation.json"))) if os.path.exists(os.path.join(OUT, "triage_validation.json")) else None
    tri = load(os.path.join(OUT, "triage.jsonl"))
    L = []
    L.append("# Site catalog: summary\n")
    L.append(f"Built {meta.get('built', '?')} from Wikidata (CC0) by `pipeline/catalog.py build`; this page by "
             "`pipeline/catalog.py summary`. One line per site in `sites.jsonl`; each entry's facts come from its "
             "Wikidata item, https://www.wikidata.org/wiki/<qid> (synthetic groups carry a `source` note instead). US entries were also selected through English Wikipedia's "
             "'Mounds in the United States' category tree (selection only; see `found_via`).\n")
    L.append(f"Entries: **{len(sites)}** (from {meta.get('candidates', '?')} candidate items before cleaning, "
             "grouping and de-duplication).\n")

    # counts region x kind
    kinds = sorted({s["kind"] for s in sites})
    cnt = collections.Counter((s["region"], s["kind"]) for s in sites)
    rows = [[k] + [cnt[(r, k)] or "" for r in REGIONS] + [sum(cnt[(r, k)] for r in REGIONS)] for k in kinds]
    rows.append(["**total**"] + [sum(cnt[(r, k)] for k in kinds) for r in REGIONS] + [len(sites)])
    L.append("## Counts by region and kind\n")
    L.append(md_table(["kind"] + REGIONS + ["all"], rows))
    L.append("\n`kind` comes from the item's Wikidata class (P31) where one matched. US entries found only by "
             "name or category get a kind from the words in their name/description (`kind_basis` says which); "
             "`mound_site` = 'mound(s)' in the name without a class, `earthwork` = generic.\n")
    basis = collections.Counter((s["region"], s.get("kind_basis", "?")) for s in sites)
    L.append("Kind basis: " + "; ".join(f"{r}: " + ", ".join(f"{b} {n}" for (rr, b), n in sorted(basis.items()) if rr == r)
                                      for r in REGIONS) + "\n")
    grp = [s for s in sites if s.get("members")]
    L.append(f"Groups: {len(grp)} entries list members ({sum(len(s['members']) for s in grp)} member items folded in); "
             f"{sum(1 for s in grp if s.get('synthetic'))} of them are synthetic groups (no Wikidata item of their own, "
             "built from members whose labels share a 'one of a group of ...' or 'forming part of a ...' phrase, "
             "within 2 km of each other).\n")

    # top 50 per region
    L.append("## Top 50 per region by notability\n")
    L.append("Notability = number of Wikipedia language editions with an article (`wiki_links`; Commons and the "
             "bot-generated Cebuano/Waray editions not counted), then raw Wikidata sitelinks. It measures "
             "how much has been written, not size or preservation. Ties are common past the first few dozen in "
             "England and France, where most items have no article at all; order within a tie is by raw "
             "sitelinks, then name, and means nothing.\n")
    for r in REGIONS:
        rs = sorted([s for s in sites if s["region"] == r], key=lambda s: (-s.get("wiki_links", 0), -s.get("sitelinks", 0), s["name"]))
        if not rs:
            continue
        zero = sum(1 for s in rs if not s.get("wiki_links"))
        L.append(f"### {r} ({len(rs)} entries; {zero} without any Wikipedia article)\n")
        rows = []
        for i, s in enumerate(rs[:50], 1):
            c = cov.get(s["id"])
            lid = "" if r != "us" else ("?" if not c else ("1 m" if c.get("lidar_1m") else f"{c.get('best_res_m')} m"))
            rows.append([i, s["name"], s["kind"], admin_str(s), s.get("wiki_links", 0), s.get("sitelinks", 0),
                         s.get("n_members", ""), s.get("qid") or "group"] + ([lid] if r == "us" else []))
        L.append(md_table(["#", "name", "kind", "admin area", "wikis", "sitelinks", "members", "qid"] +
                          (["3DEP"] if r == "us" else []), rows) + "\n")

    # data quality
    L.append("## Data quality (honest notes)\n")
    d = meta.get("dropped", {})
    if d:
        L.append("Dropped during cleaning: " + ", ".join(f"{k} {v}" for k, v in d.items()) + ". Examples:\n")
        for k, ex in meta.get("dropped_examples", {}).items():
            if ex:
                L.append(f"- {k}: " + "; ".join(ex[:6]))
        L.append("")
    m = meta.get("merge", {})
    if m:
        L.append(f"Merged: {m.get('folded_into_group')} items folded into their part-of group (all linked items "
                 f"within 4 km); {m.get('synthetic_members')} items into {m.get('synthetic_groups')} synthetic groups; "
                 f"{m.get('near_folded_as_member', 0)} items named relative to a neighbour ('Bowl barrow 100m south of X') "
                 f"folded in as members of X; {m.get('near_duplicates')} near-duplicates (< 300 m apart, distinctive "
                 "name words overlap, no conflicting register numbers or designators) merged into one entry, the "
                 "lost item listed in `merged_from`. Sample merged pairs (kept <= merged):\n")
        for p in m.get("near_duplicate_pairs", [])[:10]:
            L.append(f"- {p}")
        L.append("")

    L.append("### Famous sites: present or missing\n")
    rows = []
    for region, disp, q, pat in FAMOUS:
        hits = find_famous(sites, region, q, pat)
        if not hits:
            rows.append([region, disp, "**MISSING**", ""])
            continue
        s, mem, how = hits[0]
        where = (f"member of {s['name']}" if mem else s["name"]) + (f" (+{len(hits) - 1} more name matches)" if len(hits) > 1 else "")
        lon, lat = (mem or s)["lon"], (mem or s)["lat"]
        rows.append([region, disp, f"{where} [{(mem or s).get('qid') or 'group'}, {s['kind']}] via {how}", f"{lat:.5f}, {lon:.5f}"])
    L.append(md_table(["region", "site", "catalog entry", "lat, lon"], rows) + "\n")

    # known problems (numbers computed here; examples checked by hand on 2026-10-10)
    us = [x for x in sites if x["region"] == "us"]
    en = [x for x in sites if x["region"] == "england"]
    nl = [x for x in sites if x["region"] == "netherlands"]
    fr = [x for x in sites if x["region"] == "france"]
    kb = collections.Counter(x.get("kind_basis") for x in us)
    nl_generic = sum(1 for x in nl if re.match(r"^(terrein|wierde$|terp$|restant|verhoogde|grafheuvel ?#?\d*$|grafheuvels$|tumulus$)", x["name"], re.I))
    en_rel = sum(1 for x in en if re.search(r"\d+\s*(m|yds)\b", x["name"]))
    mil = [x["name"] for x in sites if x["kind"] == "military_earthwork"]
    L.append("### Known problems\n")
    L.append(f"- **US typing is thin.** Only {kb.get('class', 0)} of {len(us)} US entries carry an earthwork class in "
             f"Wikidata; {kb.get('words', 0)} were found by words in the name/description and {kb.get('category', 0)} only "
             "through a 'Mounds in <state>' Wikipedia category. Cahokia, Poverty Point, Moundville are typed just "
             "'archaeological site'. Their `kind` is a guess from words (`kind_basis`).")
    L.append("- **US recall gaps.** Hopeton Earthworks (Q5899962) has an 'unknown value' coordinate, so it is dropped. "
             "No Wikidata item was found under the labels 'High Bank Works', 'High Banks Works', 'Hopewell Mound Group' "
             "or 'Mound City Group' (Hopewell Culture NHP's point stands in for Mound City). Aztalan, Seip Earthworks and "
             "Windmill Hill (Avebury) are in only because they are in a hand list of seed QIDs (`SEEDS` in catalog.py). "
             "Expect other well-known US works to be missing the same way.")
    L.append(f"- **Kept but not ancient:** {len(mil)} forts typed 'fort' + 'earthworks' (" + ", ".join(mil[:6]) +
             "...) are tagged `military_earthwork` and left out of the triage. Some parks, museums and multi-site "
             "listings are entries (Hopewell Culture NHP, Indian Mounds Park; Kolomoki's museum is listed as a member "
             "of Kolomoki); multi-site listings whose parts lie > 4 km apart are flagged `unit`.")
    L.append("- **Overlapping entries.** Marietta Earthworks, Conus Mound and Mound Cemetery are three entries within "
             "57 m of each other (different names, so not merged). Same name is not same site: Story Mound "
             "(Hamilton Co., NRHP 75001436) and Story Mound State Memorial (Ross Co., 73001529) are 148 km apart; "
             "Emerald Mound (Mississippi) and Emerald Mound and Village Site (Illinois) are different sites. "
             "(I picked the wrong Story Mound as a triage positive by name; the hand check caught it.)")
    L.append(f"- **England:** {sum(1 for x in en if not x.get('wiki_links'))} of {len(en)} entries have no Wikipedia "
             f"article and {en_rel} are named by distance from a landmark (Historic England list-entry style), so "
             "the notability order means little past the top hundred or so. Offa's Dyke is filed under Wales (its "
             "Wikidata admin area is Powys) although it runs through both.")
    L.append(f"- **Netherlands:** {nl_generic} of {len(nl)} entries have generic register names ('Terrein waarin "
             "grafheuvel', 'Wierde', 'Terp'); use the admin area and Rijksmonument number. Some villages are typed "
             "as terps and absorbed their wierde item in the de-duplication (Aalsum, Ranum, Oldorp).")
    L.append(f"- **France is thin ({len(fr)} entries):** Merimee earthworks are mostly typed only 'archaeological "
             "site'; the French word route ('camp', 'enceinte', 'motte'...) adds some noise. "
             f"{sum(1 for x in fr if not x.get('admin', {}).get('departement'))} have no departement in Wikidata.")
    L.append("- **Not included:** Denmark (22,068 items typed as barrows in Wikidata; not trivial "
             "in size and no Danish DEM source in the pipeline) and Flanders (68 Belgian barrows; no DEM source). "
             "UK items not placed in England or Wales (2,502; the sampled ones are Scottish) are dropped by design.\n")

    # coordinates
    L.append("### Coordinates\n")
    prec = collections.Counter()
    for s in sites:
        p = s.get("coord_precision_deg")
        prec[(s["region"], "missing" if p is None else "coarse (>= 0.01 deg, ~1 km)" if p >= 0.01 else
              "medium (0.001-0.01 deg)" if p >= 0.001 else "fine (< 0.001 deg)")] += 1
    rows = [[r] + [prec[(r, k)] for k in ("fine (< 0.001 deg)", "medium (0.001-0.01 deg)", "coarse (>= 0.01 deg, ~1 km)", "missing")] for r in REGIONS]
    L.append("Stated precision of the coordinate (Wikidata `precision`; it says how many decimals were entered, "
             "not how right the point is):\n")
    L.append(md_table(["region", "fine", "medium", "coarse", "missing"], rows) + "\n")
    spread = [s for s in sites if (s.get("coord_spread_m") or 0) > 200]
    L.append(f"Items with several coordinates more than 200 m apart: {len(spread)}"
             + (" (e.g. " + "; ".join(f"{s['name']} {s['coord_spread_m']} m" for s in sorted(spread, key=lambda s: -s['coord_spread_m'])[:6]) + ")" if spread else "") + ".\n")
    same = collections.defaultdict(list)
    for s in sites:
        same[(round(s["lon"], 4), round(s["lat"], 4))].append(s)
    shared = [v for v in same.values() if len(v) >= 3]
    L.append(f"Points shared by 3 or more distinct entries (to 4 decimals): {len(shared)}"
             + (" (e.g. " + "; ".join(f"{len(v)} at {k[1]},{k[0]}: {v[0]['name']} / {v[1]['name']}" for k, v in
                                       [((round(v[0]['lon'], 4), round(v[0]['lat'], 4)), v) for v in shared[:4]]) + ")" if shared else "") + ".\n")

    be_p0 = os.path.join(OUT, "triage_batch_eval.json")
    if os.path.exists(be_p0):
        be0 = json.load(open(be_p0))
        n0 = be0["n_visible"] + be0["n_not_visible"] + be0["n_unclear"]
        L.append(f"**Measured by eye on the top {n0} US entries** (800 m relief crops, middle third): "
                 f"{be0['n_visible']} show an earthwork near the point, {be0['n_not_visible']} do not, "
                 f"{be0['n_unclear']} unclear. 'Do not' mixes points that miss the work (Etowah, Fort Ancient, "
                 "Ocmulgee: the work is in the picture but not near the point), works destroyed or plowed out "
                 "(Adena Mound, Troyville, Monte Sano), works too low or small to see at this scale (effigy mounds), "
                 "and a few junk entries. Treat a Wikidata point as unchecked until its crop has been looked at.\n")

    if cov:
        us = [s for s in sites if s["region"] == "us"]
        c = [cov[s["id"]] for s in us if s["id"] in cov]
        res = collections.Counter(("1 m" if r.get("lidar_1m") else "~3 m (1/9 arc-sec)" if (r.get("best_res_m") or 99) < 5
                                   else "10 m or coarser" if r.get("best_res_m") else "none") for r in c)
        L.append("## US LiDAR coverage (3DEP)\n")
        L.append(f"Checked {len(c)} of {len(us)} US entries (`catalog_cover.py`): one `identify` call for the finest "
                 "3DEP source under the point, plus a 200 x 200 px, 1 m `aw.fetch_dem` export. "
                 f"Data came back for {sum(r.get('ok', False) for r in c)}. The export resamples whatever exists to 1 m, so "
                 "'data came back' is not LiDAR; the finest source is: "
                 + ", ".join(f"{k} {v}" for k, v in res.most_common()) + ".\n")
        hf1 = sorted(r["hf_std_cm"] for r in c if r.get("lidar_1m") and "hf_std_cm" in r)
        hf3 = sorted(r["hf_std_cm"] for r in c if not r.get("lidar_1m") and 2 < (r.get("best_res_m") or 0) < 5 and "hf_std_cm" in r)
        hf10 = sorted(r["hf_std_cm"] for r in c if (r.get("best_res_m") or 0) > 5 and "hf_std_cm" in r)
        if hf1:
            L.append(f"Cross-check, 1-3 m detail in the exported DEM (std of DEM minus a 1.5 px blur): median "
                     f"{hf1[len(hf1) // 2]} cm at {len(hf1)} points with a 1 m source"
                     + (f", {hf3[len(hf3) // 2]} cm at {len(hf3)} with ~3 m" if hf3 else "")
                     + (f", {hf10[len(hf10) // 2]} cm at {len(hf10)} with 10 m" if hf10 else "")
                     + ". It also rises with rough ground and buildings, so it separates 10 m data from LiDAR only "
                     "roughly and does not tell 3 m from 1 m.\n")

    if tv:
        L.append("## Relief-crop triage\n")
        L.append(f"Validation run {tv['run']}: {tv['all']['n_pos']} crops at known-site points (the 6 built sites + "
                 f"famous standing works) and {tv['all']['n_neg']} at random points 3-8 km from any US entry on 1 m "
                 f"LiDAR. Every crop: {tv['size_m']} m square, {tv['px_m']} m/px, one renderer, fixed clip "
                 f"{tv['clip_m']} m. Models see only the picture. Per-image scores: `triage_scores.jsonl`.\n")
        L.append("Three ways of scoring: **all** = against the a-priori truth (site point vs random point); "
                 "**hand-checked** = dropping crops where, by eye, no earthwork is in the middle third of a site crop "
                 f"({tv.get('n_hand_disagree')} of {tv['all']['n_pos']}: point off the work, work off-centre, or plowed out); "
                 "**truth by eye** = keeping those crops as negatives (the case triage is meant to catch). "
                 "Hand checks: Claude looking at the crops before any model output, not a field check.\n")
        rows = []
        for k in ("all", "hand_checked", "truth_by_eye"):
            m = tv.get(k)
            if not m:
                continue
            b1, b2 = m.get("clef_best_in_sample", {}), m.get("clef_v2_best_in_sample", {})
            rows.append([k, f"{m['n_pos']} / {m['n_neg']}", m.get("clef_auc"), m.get("clef_v2_auc"),
                         f"{b2.get('recall')} / {b2.get('false_pos_rate')} at p >= {b2.get('threshold')}",
                         f"{m['qwen_recall']} / {m['qwen_false_pos_rate']}"])
        L.append(md_table(["scoring", "pos / neg", "Clef AUC (question v1)", "Clef AUC (v2)",
                           "Clef v2 recall / false-pos (in-sample best threshold)", "Qwen recall / false-pos"], rows) + "\n")
        sc = load(os.path.join(OUT, "triage_scores.jsonl"))
        mx1 = max((r["clef_p"] or 0) for r in sc)
        mx2 = max((r.get("clef_p_v2") or 0) for r in sc)
        L.append("Clef question v1 is the lead's whole-image question, asked first. v2 (earthwork *near the centre*, "
                 "with what does not count) was written after seeing v1's results on this set, so its numbers here are "
                 "optimistic; the in-sample thresholds are optimistic for both. Clef's probabilities are small "
                 f"(highest on this set: v1 {mx1:.2f}, v2 {mx2:.2f}), so only the ranking means anything. "
                 + tv.get("qwen_note", "") + "\n")
        m = tv.get("truth_by_eye") or tv["all"]
        t = m["qwen_confusion"]
        labs = [k for k in ("earthwork_visible", "unsure", "nothing", "modern_only", "none") if any(t[x][k] for x in t)]
        L.append("Qwen confusion matrix, truth by eye:\n")
        L.append(md_table(["truth \\ Qwen"] + labs, [[x] + [t[x][k] for k in labs] for x in t]) + "\n")
    be_p = os.path.join(OUT, "triage_batch_eval.json")
    if tri:
        L.append(f"Batch: the top {len(tri)} US entries by notability (forts typed 'fort' + 'earthworks' left out), "
                 "Clef scores only, in `triage.jsonl`.\n")
    if os.path.exists(be_p):
        be = json.load(open(be_p))
        L.append(be["text"] + "\n")
    p = os.path.join(OUT, "summary_notes.md")
    if os.path.exists(p):
        L.append(open(p).read())
    with open(os.path.join(OUT, "summary.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("wrote", os.path.join(OUT, "summary.md"))


if __name__ == "__main__":
    main()
