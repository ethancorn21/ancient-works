"""Evidence: which machine-checkable tie holds every picture row to the site it depicts, and an offline
re-verification of those ties (task 200, GOAL.md point 4).

A picture row (a titled row of data/commons/files.jsonl, a book-index row of data/books/index.jsonl) gets an
appended "evidence" field naming which kind of tie holds and the specifics that proved it:
  hand_tied        the file -> site QID was checked by hand in a table in the repo (pipeline/sources.py; later fit/src_*.py)
  category         the file is a member of the site's P373 Commons category, or of a recorded subcategory of it
                   (specifics: the category page, the file's category, the subcategory chain)
  depicts          structured data: the file's own item depicts the site's item (P180) - the file's item is the
                   global Wikidata item (a Q id) or the local MediaInfo item (an M id, stored in "file_qid") - or the
                   site's item lists the file as its plan (P3311) or image (P18) (specifics: the property, the value,
                   the item)
  caption_coords   the title or caption names the place and that place resolves to coordinates within 50 km of the
                   site (specifics: the place named, its resolved item/coordinates, the distance to the site)
  part_mention     the title or caption names a documented part of the site (the catalog's has_part) and that
                   part's coordinates (the site's own point when the part has none) sit within 50 km of the site
  sheet_mention    the map's own place list (the title/description, walked in reading order: 2-word pairs, then
                   3-word phrases, then singles): the first candidate that resolves to coordinates within 50 km of
                   the site names the sheet's subject (specifics: the candidate, its resolved item/coordinates,
                   the distance)
  none             no tie holds: the row is reported by check, never silently kept

Fail-closed: a caption that names a place resolving to a different location (the Hampton Court trap: the
Herefordshire seat, not the palace) does not get a passing field; it is stored as kind "none" with the conflict
recorded. A row with no tie at all is a "none", which check prints. The recorded live facts (a category
membership, a subcategory hop, an item claim, a place resolution) were fetched once by `record`; `check`
re-verifies every row from stored fields only - no network - and lists one line per row:
  PASS   a recorded tie that re-verifies
  FAIL   a recorded tie the stored fields do not support (a pass the data no longer backs)
  NONE   no tie (reported, not a failure)
`check` exits 1 iff any row FAILs; NONE rows do not fail it. Book rows: the tie is the catalog site the
name+place matcher (pipeline/books_match.py) tied the row to; check re-derives the matcher's own one-pair rule
from the row's printed text and the current catalog row (its tokens, place words incl. the book's default
state, the exact-name and token tie, the score and the "why" clauses) and requires it to reproduce the stored
record at the stored score. Only the runner-up margin stays stored: the catalog is not monotone - a new site
can take the margin - and a full re-run would fail on data growth.

usage: fit/evidence.py check  [--files P] [--books P] [--catalog P]
       fit/evidence.py record [--live] [--redo-none] [--only SITE ...]
`record` appends the "evidence" field (existing fields keep their order and bytes): the hand-tied sources rows
and the book rows are recorded offline; with --live it also fetches Commons/Wikidata (paced) for the remaining
commons rows - categories, site claims, file items, place resolutions. With --live and --redo-none it re-runs
that fetch for the rows already recorded as "none" (including their stored conflicts), so the part and sheet
routes can pick them up; every other recorded row is skipped, so a plain rerun stays a no-op.
"""
import json
import math
import os
import re
import sys
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import books_match  # noqa: E402  (norm, place_of, HAND - the check must use the matcher's own rules)
import commons  # noqa: E402  (paced API get, 429 handling)
import sources  # noqa: E402  (the hand-checked file -> QID tables)

CATALOG_SITES = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
CATALOG_EXTRAS = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
REC = "evidence/1"
DIST_TOL_M = 50e3  # "the coordinates agree": the same place or near it, never another county
R = 6371008.8  # earth mean radius, as pipeline/finder_common.py hav_m


def hav_m(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def now():
    return time.strftime("%Y-%m-%d")


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def set_field(line, field, value):
    """Append a field to a stored JSONL row without moving or re-encoding any existing field.
    The line terminator is preserved: rewrite() replaces whole lines, a dropped newline glues two
    rows into one unparseable line."""
    r = json.loads(line)
    r[field] = value
    return json.dumps(r, ensure_ascii=False) + ("\n" if line.endswith("\n") else "")


def rewrite(path, changes):
    """Write the file back, replacing the lines in changes (1-based) and keeping every other byte."""
    lines = open(path, encoding="utf-8").readlines()
    for n, line in changes.items():
        lines[n - 1] = line
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.writelines(lines)
    os.replace(tmp, path)


def catalog_map(catalog=CATALOG_SITES):
    """{id: site, qid: site} over the catalog and the extras (the extras are the source sites)."""
    out = {}
    for p in (catalog, CATALOG_EXTRAS):
        if not os.path.exists(p):
            continue
        for s in load_jsonl(p):
            if s["id"] not in out:
                out[s["id"]] = s
            if s.get("qid") and s["qid"] not in out:
                out[s["qid"]] = s
    return out


def source_tables():
    """{source name: {(qid, title)}} from the hand-checked tables in the repo - never re-fetched."""
    out = {}
    for name, src in sources.SOURCES.items():
        out["pipeline/sources.py " + name] = {(r[1], r[0]) for r in src["rows"]}
    return out


# ---------------------------------------------------------------- the check

def check_commons(row, cats):
    """Verdict for one commons row, from stored fields only. Returns (verdict, kind, reason)."""
    ev = row.get("evidence")
    if ev is None:
        return "NONE", "-", "no evidence recorded"
    kind = ev.get("kind")
    if kind not in ("hand_tied", "category", "depicts", "caption_coords", "part_mention", "sheet_mention", "none"):
        return "FAIL", kind or "?", "unknown kind"
    if kind == "none":
        return check_none(ev)
    if kind == "part_mention":
        ok, reason = check_part(row, ev, cats)
    elif kind == "sheet_mention":
        ok, reason = check_sheet(row, ev)
    else:
        ok, reason = {"hand_tied": check_hand_tied, "category": check_category,
                      "depicts": check_depicts, "caption_coords": check_caption}[kind](row, ev)
    return ("PASS" if ok else "FAIL"), kind, reason


def check_hand_tied(row, ev):
    tables = source_tables()
    src = ev.get("source")
    if src not in tables:
        return False, f"no source table {src!r} in the repo"
    if (row.get("qid"), row.get("title")) not in tables[src]:
        return False, f"({row.get('qid')}, {row.get('title')!r}) not in the {src} table"
    return True, ""


def check_category(row, ev):
    cat = row.get("cat")
    if not cat:
        return False, "the row has no P373 category recorded"
    if ev.get("site_cat") != cat:
        return False, f"site category {ev.get('site_cat')!r} differs from the row's {cat!r}"
    fc, via = ev.get("file_cat"), ev.get("via") or []
    if not fc:
        return False, "no file category recorded"
    if not via and fc != cat:
        return False, f"file category {fc!r} differs from the site's with no recorded chain"
    if via and (via[-1] != cat or fc in via):
        return False, "the subcategory chain does not run from the file's category to the site's"
    return True, ""


def check_depicts(row, ev):
    prop, val = ev.get("property"), ev.get("value")
    if prop == "P180":  # the file's own item (Q or local M) says it depicts the site's item
        if not ev.get("file_qid"):
            return False, "no file item recorded"
        if val != row.get("qid"):
            return False, f"depicts {val}, not the site's {row.get('qid')}"
        return True, ""
    if prop in ("P3311", "P18"):  # the site's item lists this file as its plan / image
        if val != row.get("title"):
            return False, "the site's claim does not name this file"
        if ev.get("site_qid") != row.get("qid"):
            return False, f"site item {ev.get('site_qid')} differs from the row's {row.get('qid')}"
        if prop == "P3311" and not row.get("wd_plan"):
            return False, "the row is not flagged wd_plan"
        return True, ""
    return False, f"unknown depicts property {prop!r}"


def check_caption(row, ev):
    named = ev.get("named_place")
    if not named:
        return False, "no place named"
    hay = books_match.norm((row.get("title") or "") + " " + (row.get("desc") or ""))
    if books_match.norm(named) not in hay:
        return False, f"the caption does not name {named!r}"
    try:
        d = hav_m(ev["site_lon"], ev["site_lat"], ev["place_lon"], ev["place_lat"])
    except (KeyError, TypeError):
        return False, "no stored coordinates"
    if abs(d - (ev.get("dist_m") or 0)) > 1000:
        return False, f"stored distance {ev.get('dist_m')} m does not reproduce ({d:.0f} m)"
    if d > DIST_TOL_M:
        return False, f"named place is {d / 1000:.0f} km from the site (the trap), not a tie"
    return True, ""


def check_part(row, ev, cats):
    site = cats.get(row.get("site"))
    if site is None:
        return False, f"site {row.get('site')!r} no longer in the catalog"
    named = ev.get("named_place")
    if not named:
        return False, "no part named"
    hay = books_match.norm((row.get("title") or "") + " " + (row.get("desc") or ""))
    if books_match.norm(named) not in hay:
        return False, f"the caption no longer names the part {named!r}"
    if not any(p.get("qid") == ev.get("part_qid") for p in (site.get("has_part") or [])):
        return False, f"part {ev.get('part_qid')} no longer a part of the site"
    try:
        d = hav_m(ev["site_lon"], ev["site_lat"], ev["place_lon"], ev["place_lat"])
    except (KeyError, TypeError):
        return False, "no stored coordinates"
    if abs(d - (ev.get("dist_m") or 0)) > 1000:
        return False, f"stored distance {ev.get('dist_m')} m does not reproduce ({d:.0f} m)"
    if d > DIST_TOL_M:
        return False, f"part is {d / 1000:.0f} km from the site (the trap), not a tie"
    return True, ""


def check_sheet(row, ev):
    named = ev.get("named_place")
    if not named:
        return False, "no place named"
    # the candidate is a glued run of the title/description's own words (e.g. "York Castle" out of
    # "New York. Castle Garden") that a plain norm-substring would miss, so re-run the extractor: the
    # stored candidate must still be derivable from the row's printed text
    if named not in sheet_candidates(row.get("title"), row.get("desc")):
        return False, f"the title/description no longer yields the candidate {named!r}"
    try:
        d = hav_m(ev["site_lon"], ev["site_lat"], ev["place_lon"], ev["place_lat"])
    except (KeyError, TypeError):
        return False, "no stored coordinates"
    if abs(d - (ev.get("dist_m") or 0)) > 1000:
        return False, f"stored distance {ev.get('dist_m')} m does not reproduce ({d:.0f} m)"
    if d > DIST_TOL_M:
        return False, f"named place is {d / 1000:.0f} km from the site (the trap), not a tie"
    return True, ""


def check_none(ev):
    c = ev.get("conflict")
    if c:
        try:
            d = hav_m(c["site_lon"], c["site_lat"], c["place_lon"], c["place_lat"])
        except (KeyError, TypeError):
            return "FAIL", "none", "recorded conflict without coordinates"
        if d <= DIST_TOL_M:
            return "FAIL", "none", f"recorded conflict no longer conflicts ({d / 1000:.0f} km)"
        return "NONE", "none", (f"conflict: {c.get('route', 'caption')} {c.get('named_place')!r} resolves to "
                                f"{c.get('place_qid')}, {d / 1000:.0f} km from the site")
    return "NONE", "none", ev.get("reason") or "no tie"


def check_book(row, cats):
    ev = row.get("evidence")
    if ev is None:
        return "NONE", "-", "no evidence recorded"
    kind = ev.get("kind")
    if kind == "caption_coords":
        return check_book_caption(row, ev, cats)
    if kind == "none":
        key = books_match._key(row.get("book"), row.get("title"))
        if key in books_match.HAND:
            return "NONE", "none", f"hand-rejected: {books_match.HAND[key][1]}"
        return "NONE", "none", ev.get("reason") or "no tie"
    if kind == "hand_tied":
        return "FAIL", kind, "no hand-checked table for book rows yet (fit/src_*.py)"
    return "FAIL", kind or "?", "unknown kind"


def _site_lookup_keys(site):
    """The matcher's by_name lookup keys of the site's current name and aliases (the exact-lookup side of the tie)."""
    keys = set()
    for j, nm in enumerate([site.get("name", "")] + list(site.get("aliases") or [])):
        keys |= books_match.name_lookup_keys(nm, skip_generic=j > 0)
    return keys


def check_book_caption(row, ev, cats):
    """Re-verify a stored book match from stored fields only, with the matcher's own rules: the row's printed
    text must still yield the record's place words (incl. the book's default state), and the matcher's one-pair
    rule must still tie that printed text to the current catalog row at the stored score."""
    toks, name_toks, place, phr, regions = books_match.row_inputs(row)
    if place != (ev.get("place") or {}):
        return "FAIL", "caption_coords", f"stored place {ev.get('place')} recomputes to {place}"
    s = cats.get((ev.get("site") or {}).get("id"))
    if s is None:
        return "FAIL", "caption_coords", f"site {ev.get('site', {}).get('id')!r} no longer in the catalog"
    for f in ("qid", "name", "lon", "lat"):
        if (ev.get("site") or {}).get(f) != s.get(f):
            return "FAIL", "caption_coords", f"site {f} changed since the check"
    key = books_match._key(row.get("book"), row.get("title"))
    if key in books_match.HAND:
        return "FAIL", "caption_coords", f"hand-rejected: {books_match.HAND[key][1]}"
    is_exact = any(kk in _site_lookup_keys(s) for ph in phr for kk in books_match.name_keys(ph))
    r = books_match.score_candidate(s, toks, name_toks, place, regions, is_exact)
    if r is None:
        return "FAIL", "caption_coords", f"site {s.get('name')!r} contradicts the row's region or place"
    score, why = r
    if why:
        return "FAIL", "caption_coords", f"matched with reasons {why}"
    if round(score, 2) != (ev.get("score") or 0):
        return "FAIL", "caption_coords", f"stored score {ev.get('score')} recomputes to {round(score, 2)}"
    if score < 0.75:
        return "FAIL", "caption_coords", f"score {round(score, 2)} below 0.75"
    if score - (ev.get("runner_up") or 0) < 0.15:
        return "FAIL", "caption_coords", f"runner-up {ev.get('runner_up')} within 0.15 of the score"
    return "PASS", "caption_coords", ""


def check(files, books, catalog=CATALOG_SITES):
    """One line per picture row; returns (exit code, printed text)."""
    cats = catalog_map(catalog)
    out, n, cnt = [], 0, {"PASS": 0, "FAIL": 0, "NONE": 0}
    for r in (load_jsonl(files) if os.path.exists(files) else []):
        if not r.get("title"):
            continue  # a sentinel row records a site with no old files, not a picture
        n += 1
        v, kind, reason = check_commons(r, cats)
        cnt[v] += 1
        out.append(_line(v, kind, f'{r["site"]}|{r["title"]}', reason))
    if os.path.exists(books):
        for r in load_jsonl(books):
            n += 1
            v, kind, reason = check_book(r, cats)
            cnt[v] += 1
            out.append(_line(v, kind, r["id"], reason))
    summary = f"evidence: {n} rows, {cnt['PASS']} pass, {cnt['FAIL']} fail, {cnt['NONE']} no-tie"
    return (1 if cnt["FAIL"] else 0, "\n".join(out + [summary]))


def _line(v, kind, key, reason):
    return f"{v:4s} {kind:15s} {key}" + (f"  {reason}" if reason else "")


# ---------------------------------------------------------------- the record

def record_commons_row(row):
    """Offline evidence for a commons row: the hand-tied sources rows; None otherwise (needs --live)."""
    by = row.get("by") or ""
    if by in source_tables():
        return {"rec": REC, "kind": "hand_tied", "checked": now(), "source": by}
    return None


def record_book_row(row, idx, by_name, cats):
    m = books_match.match_row(row, idx, by_name)
    h = books_match.HAND.get(books_match._key(row.get("book"), row.get("title")))
    if h and m["status"] in ("matched", "ambiguous"):
        m["status"], m["note"] = h
    base = {"rec": REC, "checked": now()}
    if m["status"] == "matched" and not m.get("why") and m.get("site_id") in cats:
        s = cats[m["site_id"]]
        return {**base, "kind": "caption_coords", "named_place": m["name"], "place": m["place"],
                "site": {"id": s["id"], "qid": s.get("qid"), "name": s["name"], "lon": s.get("lon"),
                         "lat": s.get("lat"), "admin": s.get("admin") or {}},
                "score": m["score"], "runner_up": m["runner_up"], "why": []}
    reason = m["status"]
    if m.get("why"):
        reason += ": " + "; ".join(m["why"])
    if m.get("note"):
        reason += " - " + m["note"]
    return {**base, "kind": "none", "reason": reason}


def record(files, books, live=False, only=None, redo_none=False):
    """Append the "evidence" field to every picture row lacking it (resumable). Prints the counts."""
    n_hand = n_book = n_live = 0
    chg, pend = {}, []
    for i, l in enumerate(open(files, encoding="utf-8"), 1):
        if not l.strip():
            continue
        r = json.loads(l)
        if not r.get("title") or (only and r["site"] not in only):
            continue
        ev = r.get("evidence") or {}
        if ev.get("rec") == REC and not (redo_none and ev.get("kind") == "none"):
            continue
        ev = record_commons_row(r)
        if ev is None:
            if not live:
                continue
            pend.append((i, l, r))
        else:
            n_hand += 1
            chg[i] = set_field(l, "evidence", ev)
    if chg:
        rewrite(files, chg)
    if pend:
        n_live = record_live(pend, files)
    if books and os.path.exists(books):
        sites, idx, by_name = books_match.load_catalog()
        cats = catalog_map()
        chg = {}
        for i, l in enumerate(open(books, encoding="utf-8"), 1):
            if not l.strip():
                continue
            r = json.loads(l)
            if r.get("evidence", {}).get("rec") == REC:
                continue
            ev = record_book_row(r, idx, by_name, cats)
            n_book += 1
            chg[i] = set_field(l, "evidence", ev)
        if chg:
            rewrite(books, chg)
    print(f"evidence recorded: {n_hand} hand-tied, {n_book} book, {n_live} live")
    return n_hand + n_book + n_live


# live fetching for the remaining commons rows (paced via commons.get; run with `record --live`)

def fetch_file_cats(titles):
    """{file title: [category names]} in batches of 50."""
    out = {}
    for i in range(0, len(titles), 50):
        d = commons.get(commons.CM, {"action": "query", "titles": "|".join(titles[i:i + 50]),
                                     "prop": "categories", "cllimit": "max"})
        for p in d.get("query", {}).get("pages", {}).values():
            out[p["title"]] = [c["title"].split(":", 1)[1] for c in p.get("categories", [])]
        print(f"   categories {i + 50}/{len(titles)}", flush=True)
    return out


def fetch_site_claims(qids):
    """{qid: {cat, p3311, p18, p625}} for the site items."""
    out = {}
    for i in range(0, len(qids), 50):
        d = commons.get(commons.WD, {"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]), "props": "claims"})
        for q, e in d.get("entities", {}).items():
            c = e.get("claims", {})
            val = lambda p: [x["mainsnak"]["datavalue"]["value"] for x in c.get(p, []) if "datavalue" in x["mainsnak"]]
            p373, p625 = val("P373"), val("P625")
            out[q] = {"cat": (p373 or [None])[0], "p3311": val("P3311"), "p18": val("P18"),
                      "p625": (p625[0]["longitude"], p625[0]["latitude"]) if p625 else (None, None)}
    return out


def fetch_subcats(cats):
    """{category: set of subcategory names}."""
    out = {}
    for c in sorted(set(cats)):
        members, cont = [], {}
        while True:
            d = commons.get(commons.CM, {"action": "query", "list": "categorymembers", "cmtitle": "Category:" + c,
                                         "cmtype": "subcat", "cmlimit": "500", **cont})
            members += [m["title"].split(":", 1)[1] for m in d.get("query", {}).get("categorymembers", [])]
            if "continue" not in d:
                break
            cont = d["continue"]
        out[c] = set(members)
    return out


def fetch_page_ids(titles):
    """{file title: page id} in batches of 50: a file page's local MediaInfo item is M<page id>."""
    out = {}
    for i in range(0, len(titles), 50):
        d = commons.get(commons.CM, {"action": "query", "titles": "|".join(titles[i:i + 50]), "prop": "info"})
        for p in d.get("query", {}).get("pages", {}).values():
            out[p["title"]] = p.get("pageid")
        print(f"   page ids {i + 50}/{len(titles)}", flush=True)
    return out


def fetch_file_entities(page_ids):
    """{file title: {"item": id, "p180": [depicted Q ids]}}: the P180 values of the file's MediaInfo item - the
    local M<page id> item, or the global item it normalizes to - batched 50/call; no entry when the page has
    neither (the row then falls through to the caption route)."""
    out, global_of = {}, {}
    ids = [f"M{pid}" for pid in page_ids.values() if pid]
    by_mid = {f"M{pid}": (t, pid) for t, pid in page_ids.items() if pid}
    for i in range(0, len(ids), 50):
        d = commons.get(commons.CM, {"action": "wbgetentities", "ids": "|".join(ids[i:i + 50]), "props": "statements"})
        for mid, e in d.get("entities", {}).items():
            if not by_mid.get(mid):
                continue
            t, pid = by_mid[mid]
            g = e.get("normalized", {}).get("item")
            if g:  # the page has a global Wikidata item instead of a local one
                global_of[g] = t
                continue
            st = e.get("statements", e.get("claims", {}))  # the local wiki returns "statements"
            out[t] = {"item": f"M{pid}",
                      "p180": [x["mainsnak"]["datavalue"]["value"]["id"] for x in st.get("P180", [])
                               if x.get("mainsnak", {}).get("snaktype") == "value"
                               and x["mainsnak"].get("datavalue", {}).get("value", {}).get("entity-type") == "item"]}
        print(f"   file entities {i + 50}/{len(ids)}", flush=True)
    gs = sorted(global_of)
    for i in range(0, len(gs), 50):
        d = commons.get(commons.WD, {"action": "wbgetentities", "ids": "|".join(gs[i:i + 50]), "props": "claims"})
        for g, e in d.get("entities", {}).items():
            if g in global_of:
                out[global_of[g]] = {"item": g,
                                     "p180": [x["mainsnak"]["datavalue"]["value"]["id"]
                                              for x in e.get("claims", {}).get("P180", [])
                                              if x.get("mainsnak", {}).get("snaktype") == "value"
                                              and x["mainsnak"].get("datavalue", {}).get("value", {}).get("entity-type") == "item"]}
        print(f"   global file items {i + 50}/{len(gs)}", flush=True)
    return out


def resolve_places(names):
    """{name: (qid, label, lon, lat)}: the first Wikidata search hit with coordinates (a search per name, then one
    batched claims fetch for all the candidates)."""
    cands = {}
    for nm in sorted(set(names)):
        d = commons.get(commons.WD, {"action": "wbsearchentities", "search": nm, "language": "en", "limit": "5"})
        ids = [e["id"] for e in d.get("search", [])]
        if ids:
            cands[nm] = ids
    ents, all_ids = {}, sorted({q for ids in cands.values() for q in ids})
    for i in range(0, len(all_ids), 50):
        ents.update(commons.get(commons.WD, {"action": "wbgetentities", "ids": "|".join(all_ids[i:i + 50]),
                                             "props": "claims|labels", "languages": "en"}).get("entities", {}))
    print(f"   places: {len(cands)} searched, {len(all_ids)} candidates", flush=True)
    out = {}
    for nm, ids in cands.items():
        for q in ids:
            e = ents.get(q, {})
            p625 = [x["mainsnak"]["datavalue"]["value"] for x in e.get("claims", {}).get("P625", [])
                    if "datavalue" in x["mainsnak"]]
            if p625:
                out[nm] = (q, e.get("labels", {}).get("en", {}).get("value"),
                           p625[0]["longitude"], p625[0]["latitude"])
                break
    return out


def named_places_in(row, site):
    """The site's own names (name, aliases, place) that the row's title/desc actually prints."""
    hay = books_match.norm((row.get("title") or "") + " " + (row.get("desc") or ""))
    out = []
    for nm in [site.get("name")] + list(site.get("aliases") or []) + [site.get("place") or ""]:
        if nm and books_match.norm(nm) in hay:
            out.append(nm)
    return out


# ---------------------------------------------------------------- the sheet-mention extractor (task 801)

# The capitalized-word candidates of a map's own place list (an OS sheet's description enumerates every place
# on the map): NFKD-normalize, strip the "File:" prefix, truncate the description to a word boundary at 600,
# split on non-letters AND case/digit boundaries, keep capitalized words (never digits, never all-caps
# acronyms, never the STOP list - mined from the 354 no-tie rows' capitalized-word frequencies), merge a lone
# "St" with the next kept word ("St. Louis" -> "St Louis"), and read the runs of adjacent kept words (a comma,
# a lowercase word of len>=3 or a digit between them breaks a run) into, per run: 2-word pairs, then 3-word
# phrases, then singles. The STOP list only cuts cost: the 50 km distance guard is the mechanism, a person name
# or a mis-resolved place simply does not pass it.
TOKEN = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+")
REAL_WORD = re.compile(r"[a-z]{3,}")  # a lowercase word of len>=3 between kept words breaks a run
STOP = set("""file book this that all image images page pages title year years author authors identifier
subjects subject publisher catalog catalogs catalogue viewer digitizing sponsor contributing library
libraries collection collections about entry description describes includes volume volumes edition
shelfmark date dates dimension dimensions medium media technique techniek materiaal material
afmetingen afmeting fysiek omschrijving opschriften merken datering plaats afbeelding afbeeldingen
naaukeurige voornaamste sterke steden stad gezichten gezicht detail details extrait avec sur sous
entre pour dans une carte cartes plan plano vue vues planche legende echelle hauteur largeur
couverture langue editeur appartient publicatie uitgave datum nummer num code bron texte photo
photograph photographs museum exhibit exhibits display art arts sciences academy institute society
royal navy army military engineers board office commission committee department bureau service
company limited inc corp trust foundation bank railroad railway railways road bridge highway avenue
lane street streets district historic heritage historyworks creative commons license licence rights
reserved public domain work works note notes source sources reference references transcription
program number numbers copy copies printed print engraved engraving sheet sheets map maps atlas
atlases survey surveys view views plan plans drawing drawings one inich inch published plattegrond
reproductie identificatie titel objecttype objectnummer vervaardiging vervaardiger auteur sujet
zeven
the of de van la le les du des en on in by at to or and for with from op bij met naar per
ordnance quartier house design pattern textile numerisation onderdeel english roman
bewerkt nativite nativity gemeentelijke deze rotterdamblindstempel reisalbum georeferencer
dessins digue digues amenagement dyffryn jazz built ancient archaeological biodiversity center
home nursing prospect fleuron bowes click landscape appearing text everything figures franse
internet archive before history
""".split())


def sheet_candidates(title, desc):
    """The ordered place candidates of a picture's title/description, for the sheet route: per run in order of
    appearance, 2-word pairs, then 3-word phrases, then singles; title before description; <=12, deduped.
    Deterministic over the stored text, so check_sheet re-runs it to re-verify a stored candidate."""
    d = (desc or "")[:600]
    if len(desc or "") > 600 and " " in d:
        d = d[:d.rfind(" ")]  # word boundary: never present a cut-off word as a candidate
    text = unicodedata.normalize("NFKD", (title or "") + " " + d).encode("ascii", "ignore").decode()
    if text.startswith("File:"):
        text = text[5:]
    toks = TOKEN.findall(text)
    spans = [(m.start(), m.end()) for m in TOKEN.finditer(text)]
    kept = []  # (tok, is_first_token, orig_tok_index)
    for i, t in enumerate(toks):
        if t.upper() == "ST" and len(t) <= 2:
            kept.append(("St", i == 0, i))  # merge marker: "St. Louis" -> "St Louis"
            continue
        # a digit is never kept (it leaked into v2 and formed junk pairs: barcodes, year ranges, hex fragments)
        if (t[0].isalpha() and len(t) >= 3 and not t.islower()
                and not (t == t.upper() and t.isalpha()) and t.lower() not in STOP):
            kept.append((t, i == 0, i))
    # merge a lone "St" with the next kept word ("St. Louis" -> "St Louis"): only when no comma, no lowercase
    # word and no digit sits between them (else "St" would swallow an unrelated word)
    merged, skip = [], set()
    for j, (t, first, oi) in enumerate(kept):
        if j in skip:
            continue
        if t == "St" and j + 1 < len(kept):
            _, _, ni = kept[j + 1]
            between = text[spans[oi][1]:spans[ni][0]]
            if not ("," in between or REAL_WORD.search(between) or any(c.isdigit() for c in between)):
                merged.append(("St " + kept[j + 1][0], first, oi))
                skip.add(j + 1)
                continue
        merged.append((t, first, oi))
    kept = merged
    if len(kept) == 1 and kept[0][1]:
        kept = []  # a lone leading word is a heading, not a place
    runs, run = [], []
    prev_i = None
    for j, (t, first, oi) in enumerate(kept):
        if prev_i is not None:
            between = text[spans[prev_i][1]:spans[oi][0]]
            if ("," in between or REAL_WORD.search(between) or any(c.isdigit() for c in between)):
                runs.append(run)
                run = []
        run.append(t)
        prev_i = oi
    if run:
        runs.append(run)
    out = []
    for r in runs:
        for L in (2, 3):  # pairs first, then 3-word phrases, then singles
            for i in range(len(r) - L + 1):
                out.append(" ".join(r[i:i + L]))
        out += r
    seen, ded = set(), []
    for c in out:
        if c not in seen:
            seen.add(c)
            ded.append(c)
    return ded[:12]


def part_hits(row, site):
    """The site's documented parts (the catalog's has_part) whose name the row's title/desc actually prints."""
    hay = books_match.norm((row.get("title") or "") + " " + (row.get("desc") or ""))
    return [p for p in (site.get("has_part") or []) if p.get("name") and books_match.norm(p["name"]) in hay]


def site_point(site, claims):
    """The site's own coordinates: the catalog's lon/lat, falling back to the site item's P625 claim."""
    lon, lat = site.get("lon"), site.get("lat")
    if lon is None:
        lon, lat = claims.get("p625", (None, None))
    return lon, lat


def caption_route(row, site, claims, places):
    """The caption route: the site's own names printed by the title/desc, resolved to coordinates - the
    nearest resolution within 50 km proves the caption_coords tie; when every resolution is farther, the
    nearest one is recorded as the conflict (the Hampton-Court trap, never a pass). Returns None when the
    caption does not decide the row (no coordinates, no place named, or no place resolved), so the caller
    can try further routes."""
    slon, slat = site_point(site, claims)
    if slon is None:
        return None
    best, conflicts = None, []
    for nm in named_places_in(row, site):
        r = places.get(nm)
        if not r:
            continue
        d = hav_m(slon, slat, r[2], r[3])
        if d <= DIST_TOL_M and (best is None or d < best[0]):
            best = (d, nm, r)
        else:
            conflicts.append((d, nm, r))
    if best:
        d, nm, (pqid, plab, plon, plat) = best
        return {"rec": REC, "kind": "caption_coords", "checked": now(), "named_place": nm,
                "place_qid": pqid, "place_label": plab, "place_lon": plon, "place_lat": plat,
                "site_lon": slon, "site_lat": slat, "dist_m": round(d, 1)}
    if conflicts:
        d, nm, (pqid, plab, plon, plat) = min(conflicts, key=lambda x: x[0])
        return {"rec": REC, "kind": "none", "checked": now(),
                "conflict": {"named_place": nm, "place_qid": pqid, "place_label": plab,
                             "place_lon": plon, "place_lat": plat, "site_lon": slon, "site_lat": slat}}
    return None


def part_route(row, site, claims, part_coords):
    """The part route: the row prints the name of a documented part of the site (the catalog's has_part) and
    that part's own coordinates (the site's own point when the part has none) sit within 50 km of the site -
    the Clifford's-Tower-on-York-castle tie. The nearest hit within 50 km passes (kind part_mention); when
    every hit is farther, the nearest one is stored as the conflict. Returns None when no part decides the
    row, so the caller can try further routes."""
    slon, slat = site_point(site, claims)
    if slon is None:
        return None
    best, conflicts = None, []
    for p in part_hits(row, site):
        qid = p.get("qid")
        lon, lat = (part_coords or {}).get(qid, (None, None))
        if lon is None:  # the part has no coordinates: the site's own point (0 m, always a pass)
            lon, lat, src_qid = slon, slat, site.get("qid")
        else:
            src_qid = qid
        d = hav_m(slon, slat, lon, lat)
        if d <= DIST_TOL_M and (best is None or d < best[0]):
            best = (d, p, src_qid, lon, lat)
        else:
            conflicts.append((d, p, src_qid, lon, lat))
    if best:
        d, p, src_qid, plon, plat = best
        return {"rec": REC, "kind": "part_mention", "checked": now(), "named_place": p["name"],
                "part_qid": p.get("qid"), "place_qid": src_qid, "place_label": p.get("name"),
                "place_lon": plon, "place_lat": plat, "site_lon": slon, "site_lat": slat, "dist_m": round(d, 1)}
    if conflicts:
        d, p, src_qid, plon, plat = min(conflicts, key=lambda x: x[0])
        return {"rec": REC, "kind": "none", "checked": now(),
                "conflict": {"route": "part", "named_place": p["name"], "place_qid": src_qid,
                             "place_label": p.get("name"), "place_lon": plon, "place_lat": plat,
                             "site_lon": slon, "site_lat": slat}}
    return None


def sheet_route(row, site, claims, places):
    """The sheet route: an OS-sheet-like picture names many places in its title/description; WALK the ordered
    candidates (per run: pairs, then phrases, then singles; title before description) and let the FIRST
    candidate that resolves to coordinates decide the row: within 50 km of the site the sheet mentions the
    site (kind sheet_mention), farther the row keeps kind "none" with that resolution stored as the conflict.
    A walk, not a nearest-wins: a glued word inside a farther place ("York" inside "New York") must not pass
    a New York row. Returns None when no candidate resolves, so the caller can keep the row "none"."""
    slon, slat = site_point(site, claims)
    if slon is None:
        return None
    for c in sheet_candidates(row.get("title"), row.get("desc")):
        r = (places or {}).get(c)
        if not r:
            continue
        d = hav_m(slon, slat, r[2], r[3])
        if d <= DIST_TOL_M:
            return {"rec": REC, "kind": "sheet_mention", "checked": now(), "named_place": c,
                    "place_qid": r[0], "place_label": r[1], "place_lon": r[2], "place_lat": r[3],
                    "site_lon": slon, "site_lat": slat, "dist_m": round(d, 1)}
        return {"rec": REC, "kind": "none", "checked": now(),
                "conflict": {"route": "sheet", "named_place": c, "place_qid": r[0], "place_label": r[1],
                             "place_lon": r[2], "place_lat": r[3], "site_lon": slon, "site_lat": slat}}
    return None


def live_evidence(row, ctx):
    """The evidence for one commons row, computed offline from the live facts prefetched into ctx
    (categories, site claims, the file's own item, part coordinates, resolved places) - no network here.
    The routes cascade: the first one to return a pass or a conflict decides the row."""
    site = ctx["cats"].get(row.get("site")) or {}
    claims = ctx["claims"].get(row.get("qid"), {})
    fcats = ctx["file_cats"].get(row["title"], [])
    if claims.get("cat"):
        if claims["cat"] in fcats:
            return {"rec": REC, "kind": "category", "checked": now(), "site_cat": claims["cat"],
                    "file_cat": claims["cat"], "via": []}
        subs = ctx["subcats"].get(claims["cat"])
        if subs is None:
            subs = ctx["subcats"][claims["cat"]] = fetch_subcats([claims["cat"]]).get(claims["cat"], set())
        for fc in fcats:
            if fc in subs:
                return {"rec": REC, "kind": "category", "checked": now(), "site_cat": claims["cat"],
                        "file_cat": fc, "via": [claims["cat"]]}
    if row["title"] in claims.get("p3311", []):
        return {"rec": REC, "kind": "depicts", "checked": now(), "property": "P3311",
                "value": row["title"], "site_qid": row["qid"]}
    if row["title"] in claims.get("p18", []):
        return {"rec": REC, "kind": "depicts", "checked": now(), "property": "P18",
                "value": row["title"], "site_qid": row["qid"]}
    fe = ctx["file_entities"].get(row["title"])
    if fe and row.get("qid") in fe["p180"]:
        return {"rec": REC, "kind": "depicts", "checked": now(), "property": "P180",
                "file_qid": fe["item"], "value": row["qid"]}
    ev = caption_route(row, site, claims, ctx["places"])
    if ev is not None:
        return ev
    ev = part_route(row, site, claims, ctx.get("part_coords"))
    if ev is not None:
        return ev
    ev = sheet_route(row, site, claims, ctx["places"])
    if ev is not None:
        return ev
    return {"rec": REC, "kind": "none", "checked": now(),
            "reason": "no tie: not in the site's category, no item claim, no place named in the caption"}


def record_live(pend, files):
    """Fetch the live facts for every pending row (batched, paced) and record each one's evidence, flushing the
    file in chunks of 25 so an interrupted run keeps its progress (a rerun skips the recorded rows)."""
    titles = [r["title"] for _, _, r in pend]
    cats = catalog_map()
    ctx = {"cats": cats,
           "file_cats": fetch_file_cats(titles),
           "claims": fetch_site_claims(sorted({r["qid"] for _, _, r in pend if r.get("qid")})),
           "subcats": {}}
    ctx["file_entities"] = fetch_file_entities(fetch_page_ids(titles))
    part_qids = sorted({p.get("qid") for _, _, r in pend
                        for p in ((cats.get(r.get("site")) or {}).get("has_part") or []) if p.get("qid")})
    ctx["part_coords"] = {q: c["p625"] for q, c in fetch_site_claims(part_qids).items()} if part_qids else {}
    names = set()
    for _, _, r in pend:
        s = cats.get(r.get("site")) or {}
        names |= set(named_places_in(r, s))
        names |= set(sheet_candidates(r.get("title"), r.get("desc")))
    ctx["places"] = resolve_places(names)
    chg, done = {}, 0
    for i, l, r in pend:
        chg[i] = set_field(l, "evidence", live_evidence(r, ctx))
        done += 1
        if done % 25 == 0:
            rewrite(files, chg)
            chg = {}
            print(f"   recorded {done}/{len(pend)}", flush=True)
    if chg:
        rewrite(files, chg)
    return done


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in ("check", "record"):
        raise SystemExit(__doc__.strip().splitlines()[-1])
    def opt(flag, default):
        return args[args.index(flag) + 1] if flag in args else default
    if args[0] == "check":
        files = opt("--files", os.path.join(ROOT, "data", "commons", "files.jsonl"))
        books = opt("--books", os.path.join(ROOT, "data", "books", "index.jsonl"))
        code, text = check(files, books, opt("--catalog", CATALOG_SITES))
        print(text)
        raise SystemExit(code)
    only = set(args[args.index("--only") + 1:]) if "--only" in args else None
    live = "--live" in args
    if "--redo-none" in args and not live:
        print("note: --redo-none only applies with --live", file=sys.stderr)
    record(opt("--files", os.path.join(ROOT, "data", "commons", "files.jsonl")),
           opt("--books", os.path.join(ROOT, "data", "books", "index.jsonl")),
           live=live, only=only, redo_none="--redo-none" in args and live)
