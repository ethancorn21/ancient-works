"""Cover: the last pass of GOAL.md point 1 and its evidence for the human (task 212, the last task).

For every built site still without a fit: a targeted picture search (its P373 category files, a
P180 depiction re-test on every title gathered, the 3 full-text title searches) with the search
recorded exactly; a found picture staged through the normal loop (the fit is the MATCHER -
fit/matchfit.py first, the rest to the review item - never the vision model, which invented its
points, 301, and the lead ef84a05 forbids it for placement); a site where nothing is found gets a
review item marked "no picture found" with exactly what was searched. Then the one and only
page-facing sync: every fit document (the hand fits, the automatic ones, the human-saved ones)
becomes its site's overlay and its drawings count through the existing plan_fit machinery;
web/data/review.json becomes the current open list; and docs/batch.md is the report the human
reads - counts per outcome, the seeded 20-sample of automatically accepted fits (page URL and
gate score each) for the 18/20 check, and the no-picture list.

usage: .venv/bin/python fit/cover.py <phase> [--root DIR] [--working | --model-json F] [--live]
  phases (run in order by `all`):
    fetch      local copies for every kept files.jsonl row without one (its 1280 thumb; a
               url-only row - the ORL/Limes set - through commons.info's thumburl, falling back
               to the raw url), then regenerate web/data/plans.json (export_plans)
    search     every built site without a fit and without a plans.json candidate: the P373
               category files, the P180 re-test, the title searches; keep with commons.keep
               (1925 cut-off); deduped against files.jsonl; the per-site record of exactly what
               ran (failures included - a 429 is recorded, not hidden) lands in
               data/cover/searches.json as it goes, so the phase is resumable
    stage      the new files into the canonical files.jsonl (the harvest row shape + qid +
               by:"212"), local copies, classified.jsonl through an injectable classifier
               (default the Clef-flash batch, commons' questions - if it does not answer, that
               is an ask_human moment, not a module decision; classifier_note is recorded on
               each classified row when a non-default model answers), the 200 evidence field, and
               plans.json again (growth-only)
    loop       the normal loop, one site at a time through tools/site_done.py's one-site line:
               matchfit first (it places what it is sure of and resolves the item), the rest to
               the review item as "no model answer", a pictureless site the batch's no-picture
               item (the nopicture phase re-records it with the exact searched record)
    nopicture  the search-set sites that ended without a picture get a review item marked "no
               picture found" with exactly what was searched (the human can drop the site or
               name a source from the item)
    sync       the page-facing sync: a plan_fit sweep over EVERY fit document, per-doc proof
               (the one-site line's own decisions: hand builds unchecked; an agent doc through
               the fabrication/spread line check, a pattern is deleted and recorded; an unmarked
               auto doc is stamped by:agent; an unmarked non-auto doc is refused and recorded)
               and per-doc failure containment: one document that cannot be built becomes a
               review entry and the sweep goes on (the fix for the serve worker's
               give-up-the-whole-sweep weakness), prune at the end
    export     web/data/review.json = the current open list for the page's Review section (201)
               - the one and only writer of that page file
    report     docs/batch.md (see the phase)
  --model-json F  recorded model answers for the loop (the batch's dry-run convention);
                  the loop phase's only flag
  --live          stage: evidence.record fetches the live route for the new rows (network)
  --working       REFUSED by this task: the local vision model invented its fit points (301) and
                  the lead (ef84a05) forbids it for placement - 212's fit is the matcher. The
                  flag stays in the parser for the batch-compat; passing it exits 2.

Every phase takes the data root (default: this checkout) so a test drives the phases on a
temp tree. The report's 20-sample is reproducible: random.Random(SEED_212) over the sorted ids
of the whole automatically-accepted-fits union.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import random
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "fit"))
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "tools"))

import aw  # noqa: E402  (UA)
import batch_us  # noqa: E402  (_doc_path, _save_json, _plans_rows, _page_url - reused, not copied)
import commons  # noqa: E402  (paced API, keep/year_of, the classifier questions)
import evidence  # noqa: E402  (the P180 fetchers, record)
import export_plans  # noqa: E402
import plan_fit  # noqa: E402  (who_placed, is_done, build, prune - the sync's primitives)
import review  # noqa: E402
import site_done  # noqa: E402  (the one-site line: the loop's engine, the sync's per-doc decisions)

# The recorded seed of the report's 20-sample (batch 20261010, null 20261011 - the date
# convention): fixed, so the human's 18/20 check (GOAL point 3) is repeatable.
SEED_212 = 20261012


def _now():
    return datetime.now(timezone.utc).isoformat()


def _sha16(title):
    return hashlib.sha1(title.encode("utf-8")).hexdigest()[:16]


def _files_path(root):
    return Path(root) / "data" / "commons" / "files.jsonl"


def _classified_path(root):
    return Path(root) / "data" / "commons" / "classified.jsonl"


def _local_path(root, site, title):
    """The row's local copy: data/raw/commons/<site>/<sha1(title)[:16]>.jpg - the same name
    commons.local and export_plans compute (so a fetched copy is the one the page serves)."""
    return Path(root) / "data" / "raw" / "commons" / site / (_sha16(title) + ".jpg")


def _searches_path(root):
    return Path(root) / "data" / "cover" / "searches.json"


def _load_jsonl(path):
    path = Path(path)
    if not path.is_file():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def _files_rows(root):
    return _load_jsonl(_files_path(root))


def _all_docs(root):
    """(doc id, doc) for every fit document in the store, sorted by id."""
    out = []
    d = Path(root) / "data" / "db" / "platefits"
    if not d.is_dir():
        return out
    for p in sorted(d.iterdir()):
        if p.suffix != ".json":
            continue
        out.append((p.name[:-5], json.loads(p.read_text())))
    return out


def _sites(root):
    """{id: site} of web/data/sites.json - the BUILT sites."""
    d = json.loads((Path(root) / "web" / "data" / "sites.json").read_text())
    ss = d.get("sites") if isinstance(d, dict) else d
    return {s["id"]: s for s in ss if s.get("id")}


def _no_fit_sites(root):
    """The built sites with no fit: no fit document and drawings == 0 (the complement of the
    covered set - a site with a document is fitted even before its overlay is built, and a
    drawings count without a document is the old-style site.json plate fit)."""
    sites = _sites(root)
    doc_sites = {doc.get("site") for _, doc in _all_docs(root)}
    return {sid for sid, s in sites.items() if s.get("drawings", 0) == 0 and sid not in doc_sites}


def _cand_sites(root):
    """The sites that have a plans.json candidate row (the loop's set without the search's)."""
    out = set()
    for r in batch_us._plans_rows(str(root)):
        out.update(r.get("sites") or [])
    return out


def _search_set(root):
    """The built sites the targeted search runs on: no fit AND no plans.json candidate
    (recomputed at run time, so a site that just gained a candidate drops out)."""
    return sorted(_no_fit_sites(root) - _cand_sites(root))


def _load_searches(root):
    path = _searches_path(root)
    if not path.is_file():
        return {}
    return json.loads(path.read_text())


# ---------------------------------------------------------------- fetch

def _fetch_one(url, dst):
    """One picture download to dst, through .part -> rename (commons.thumbs' behaviour):
    atomic (a failed download leaves no partial file) and resumable (the caller skips an
    existing dst). -> True on success."""
    try:
        req = urllib.request.Request(url, headers=aw.UA)
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        open(dst + ".part", "wb").write(data)
        os.replace(dst + ".part", dst)
        return True
    except Exception as e:
        print("   fetch failed %s: %r" % (url[:80], str(e)[:100]), flush=True)
        return False


def _fetch_local(root, title, meta, row):
    """The row's local copy, fetched when missing: its 1280 thumb (the info's thumburl when
    given, else the row's own), else the raw url (utm-stripped). -> (path, fetched)."""
    row = row or {}
    p = _local_path(root, row.get("site"), title)
    if p.exists():
        return p, False
    url = (meta or {}).get("thumb") or (meta or {}).get("url") or row.get("thumb") or row.get("url")
    if url is None:
        return p, False
    if "?utm" in url:
        url = url.split("?utm")[0]
    p.parent.mkdir(parents=True, exist_ok=True)
    return p, _fetch_one(url, p)


def _regen_plans(root):
    """Regenerate web/data/plans.json against this root. tools/export_plans.py and
    pipeline/commons.py bind ROOT/BOOKS/OUT/RAW to this checkout as module constants, so the
    call temporarily re-points them at root and restores them (setup, not product behaviour -
    the live run's root is this checkout anyway; a temp-tree test needs data/books,
    data/catalog and specs/ copied in, as any other test tree)."""
    saved = (export_plans.ROOT, export_plans.BOOKS, commons.OUT, commons.RAW)
    export_plans.ROOT = str(root)
    export_plans.BOOKS = os.path.join(str(root), "data", "books")
    commons.OUT = os.path.join(str(root), "data", "commons")
    commons.RAW = os.path.join(str(root), "data", "raw", "commons")
    try:
        export_plans.main()
    finally:
        export_plans.ROOT, export_plans.BOOKS, commons.OUT, commons.RAW = saved


def fetch(root):
    """Local copies for every kept files.jsonl row without one, then plans.json again
    (the lead's second point: 211's new pictures are in the canonical files but most have no
    local copy, so they are not in plans yet). Paced 1/s, resumable (an existing copy is
    skipped, a failed fetch is recorded and retried on the next run)."""
    root = str(root)
    rows = [r for r in _files_rows(root) if r.get("title") and commons.keep(r["title"], r)]
    thumb_rows, url_rows, n_nosrc = [], [], 0
    for r in rows:
        if _local_path(root, r["site"], r["title"]).exists():
            continue
        if r.get("thumb"):
            thumb_rows.append(r)
        elif r.get("url"):
            url_rows.append(r)
        else:
            n_nosrc += 1
    n_thumb = 0
    for r in thumb_rows:
        _, fetched = _fetch_local(root, r["title"], {}, r)
        n_thumb += fetched
        time.sleep(1.0)
    n_url = 0
    for i in range(0, len(url_rows), 50):
        batch = url_rows[i:i + 50]
        try:
            meta = commons.info([r["title"] for r in batch])
        except Exception as e:
            print("   info batch failed: %r" % str(e)[:120], flush=True)
            meta = {}
        for r in batch:
            _, fetched = _fetch_local(root, r["title"], meta.get(r["title"]) or {}, r)
            n_url += fetched
            time.sleep(1.0)
    n_have = len(rows) - len(thumb_rows) - len(url_rows)
    print("fetch: %d row(s) with a local copy, %d without a source, fetched %d thumb(s) + %d url-only"
          % (n_have, n_nosrc, n_thumb, n_url))
    _regen_plans(root)
    return n_thumb + n_url


# ---------------------------------------------------------------- search

def _claims(root, qids):
    """{qid: claims} via commons.wd_claims, with a per-qid fallback when a batch fails (a
    429 on one batch must not cost every site its category): a qid that still fails is
    recorded as {"error": ...} so the per-site record names it."""
    claims = {}
    try:
        claims.update(commons.wd_claims(sorted(qids)))
    except Exception as e:
        print("   wd_claims batch failed: %r - per-qid fallback" % str(e)[:120], flush=True)
    for q in sorted(qids):
        if q in claims:
            continue
        try:
            claims.update(commons.wd_claims([q]))
        except Exception as e:
            claims[q] = {"error": str(e)[:120]}
    return claims


def _search_site(root, sid, site, claims, existing):
    """The targeted search for one site -> its record: exactly what was searched (the
    category, the qid's P180 re-test, the 3 title queries), what it found that is new (kept
    with commons.keep, deduped against files.jsonl across the run), and every route that
    failed (a 429/timeout is recorded, not hidden - the record must be true)."""
    qid = site.get("qid")
    name = (site.get("name") or sid).replace('"', "")
    c = claims.get(qid) if qid else None
    cat = (c or {}).get("cat")
    rec = {
        "site": sid,
        "name": site.get("name") or sid,
        "date": _now(),
        "qid": qid or "no qid",
        "cat": cat or "none",
        "n_cat_files": 0,
        "n_p180": 0,
        "n_p180_gathered": 0,
        "title_queries": [q.format(n=name) for q in commons.SEARCHES],
        "n_title_hits": 0,
        "n_gathered": 0,
        "n_kept": 0,
        "new": [],
        "failed": [],
    }
    if c and c.get("error"):
        rec["failed"].append("wikidata claims: " + c["error"])
    titles = {}  # title -> set of via tags (first gather wins the order, tags accumulate)

    def add(ts, via):
        for t in ts or []:
            titles.setdefault(t, set()).add(via)

    if qid and c:
        add(["File:" + t for t in c.get("plan", [])], "claims")      # P3311
        add(["File:" + t for t in c.get("image", [])], "claims")     # P18
        if cat:                                                     # (a) the category
            try:
                files = commons.files_of(cat, depth=1)
                rec["n_cat_files"] = len(files)
                add(files, "cat")
            except Exception as e:
                rec["failed"].append("category '%s': %s" % (cat, str(e)[:100]))
        # (b) the P180 re-test on every title gathered so far: the file's own item depicts
        # the site's item - the proven depiction route (evidence's), not a new API
        if titles:
            rec["n_p180_gathered"] = len(titles)
            try:
                pids = evidence.fetch_page_ids(list(titles))
                ents = evidence.fetch_file_entities(pids)
                for t, e in ents.items():
                    if qid in (e.get("p180") or []):
                        rec["n_p180"] += 1
                        titles[t].add("p180")
            except Exception as e:
                rec["failed"].append("P180 re-test: %s" % str(e)[:100])
    try:                                                            # (c) the title search
        hits = commons.search(name)
        rec["n_title_hits"] = len(hits)
        add(hits, "title")
    except Exception as e:
        rec["failed"].append("title search: %s" % str(e)[:100])
    rec["n_gathered"] = len(titles)
    if titles:
        try:
            meta = commons.info(list(titles))
        except Exception as e:
            rec["failed"].append("file info: %s" % str(e)[:100])
            meta = {}
        for t in sorted(titles):
            m = meta.get(t)
            if not m or not m.get("url"):
                continue
            if (m.get("mime") or "").startswith(("video", "audio", "application/pdf")):
                continue
            if not commons.keep(t, m):
                continue
            rec["n_kept"] += 1
            if t in existing:
                continue
            existing.add(t)
            rec["new"].append({
                "title": t,
                "via": sorted(titles[t]),
                "wd_plan": qid is not None and t[5:] in ((claims.get(qid) or {}).get("plan") or []),
                "meta": {k: m[k] for k in ("url", "thumb", "w", "h", "mime", "date",
                                           "desc", "artist", "license", "page")},
            })
    return rec


def search(root):
    """The targeted picture search for every built site without a fit and without a
    plans.json candidate. The per-site record lands in data/cover/searches.json as it goes
    (resumable: a re-run skips what is already recorded) and the stage phase stages each
    record's new files."""
    root = str(root)
    set_ = _search_set(root)
    path = _searches_path(root)
    records = _load_searches(root)
    todo = [sid for sid in set_ if sid not in records]
    print("search: %d site(s) to search, %d already recorded" % (len(todo), len(set_) - len(todo)))
    if todo:
        sites = _sites(root)
        qids = sorted({sites[sid].get("qid") for sid in todo if sites[sid].get("qid")})
        claims = _claims(root, qids) if qids else {}
        existing = {r["title"] for r in _files_rows(root) if r.get("title")}
        for rec in records.values():  # a file recorded by an earlier run is not new again
            for e in rec.get("new") or []:
                existing.add(e["title"])
        for sid in todo:
            rec = _search_site(root, sid, sites[sid], claims, existing)
            records[sid] = rec
            path.parent.mkdir(parents=True, exist_ok=True)
            batch_us._save_json(path, records)
            print("search %s: %d gathered, %d kept old, %d new (%s)" % (
                sid, rec["n_gathered"], rec["n_kept"], len(rec["new"]),
                "; ".join(rec["failed"]) if rec["failed"] else "all routes answered"))
    n_new = sum(len(r.get("new") or []) for r in records.values())
    print("search: %d record(s) on file, %d new file(s) for the stage phase" % (len(records), n_new))
    return records


# ---------------------------------------------------------------- stage

def _clef_classify(rows):
    """The default classifier: the Clef-flash batch with commons' own questions and state
    (pipeline/clef.py against the AI box), so 212's rows classify the way commons.classify
    would. rows: dicts with a local jpg path; -> one {p_plan, p_birdseye, p_photo} per row,
    aligned."""
    import clef
    out = []
    for i in range(0, len(rows), 6):
        ch = rows[i:i + 6]
        ans = clef.decide_batch([(commons.CLEF_STATE, commons.CLEF_Q, [r["local"]]) for r in ch])
        out += [{k: round(float(a[k]["noul"]), 4) for k in commons.CLEF_Q} for a in ans]
    return out


def _stage_row(root, sid, rec, e):
    """One new file's files.jsonl row: the harvest shape (commons.harvest's field set) plus
    the site's qid and by:"212" (this task's rows, so a re-run never re-stages them)."""
    meta = e.get("meta") or {}
    sites = _sites(root)
    return {
        "site": sid,
        "qid": (sites.get(sid) or {}).get("qid"),
        "title": e["title"],
        "year": commons.year_of(e["title"], meta),
        "wd_plan": bool(e.get("wd_plan")),
        "cat": None if rec.get("cat") == "none" else rec.get("cat"),
        "by": "212",
        **meta,
    }


def stage(root, classifier=None, live=False, classifier_note=None):
    """The newly found files into the canonical data: files.jsonl rows (the harvest shape,
    + qid, + by:"212"), their local copies, classified.jsonl through the INJECTABLE
    classifier (default the Clef-flash batch - a test supplies a recorded answer; if the AI
    box does not answer in the working phase that is an ask_human moment, never a silent
    substitution; classifier_note, when given, is recorded on each classified row so the
    file itself says which model answered - the one-off 8080 Qwen approval, lead 003), the
    200 evidence field on the new rows (evidence.record, only the new sites), and
    plans.json again (growth-only: it rewrites no row it already wrote)."""
    root = str(root)
    records = _load_searches(root)
    have = {r["title"] for r in _files_rows(root) if r.get("title")}
    fresh = []
    for sid in sorted(records):
        rec = records[sid]
        for e in rec.get("new") or []:
            if e["title"] not in have:
                fresh.append((sid, rec, e))
    if not fresh:
        print("stage: nothing new to stage")
        _regen_plans(root)
        return 0
    rows = []
    for sid, rec, e in fresh:
        meta = e.get("meta") or {}
        row = _stage_row(root, sid, rec, e)
        p, fetched = _fetch_local(root, e["title"], meta, {"site": sid})
        if fetched:
            time.sleep(1.0)
        rows.append({"row": row, "local": str(p) if p.exists() else None})
    n_classified = 0
    if any(r["local"] for r in rows):
        todo = [r for r in rows if r["local"]]
        ans = (classifier or _clef_classify)(todo)
        classified = _classified_path(root)
        classified.parent.mkdir(parents=True, exist_ok=True)
        with open(classified, "a") as f:
            for r, a in zip(todo, ans):
                d = {"site": r["row"]["site"], "title": r["row"]["title"],
                     "p_plan": a["p_plan"], "p_birdseye": a["p_birdseye"],
                     "p_photo": a["p_photo"]}
                if classifier_note:
                    d["classifier"] = classifier_note
                f.write(json.dumps(d) + "\n")
                n_classified += 1
        for r in rows:
            if not r["local"]:
                print("   no local copy (fetch failed, retried next run): %s" % r["row"]["title"][:80])
    files = _files_path(root)
    with open(files, "a") as f:
        for r in rows:
            f.write(json.dumps(r["row"]) + "\n")
    books = os.path.join(root, "data", "books", "index.jsonl")
    evidence.record(str(files), books, live=live,
                    only={r["row"]["site"] for r in rows})
    _regen_plans(root)
    print("stage: %d file(s) staged (%d classified) -> files.jsonl, classified.jsonl, plans.json"
          % (len(rows), n_classified))
    return len(rows)


# ---------------------------------------------------------------- loop

def loop(root, model_json=None):
    """The normal loop, one site at a time: every built site that still has no fit goes
    through tools/site_done.py's one-site line (fit -> sync -> entry -> review; the line
    syncs each new document itself, refreshes the drawings count, and scopes the review
    export to the site). The fit is the MATCHER: matchfit first (it places what it is sure
    of, including pictures already in a review item - a confident fit resolves the item),
    never the vision model (the lead ef84a05; --working is refused at the CLI). The rest go
    to the site's review item as "no model answer" (batch_us.run_sites' upsert); a site
    with no picture gets the batch's no-picture item, which the nopicture phase re-records
    with the exact searched record. model_json (the batch's recorded dry-run answers) is
    forwarded as --model-json. -> {site: {rc, lines}} for the report."""
    root = str(root)
    out = {}
    for sid in sorted(_no_fit_sites(root)):
        args = [sid, "--root", root]
        if model_json:
            args += ["--model-json", str(model_json)]
        buf = io.StringIO()
        rc = None
        try:
            with contextlib.redirect_stdout(buf):
                rc = site_done.main(args)
        except SystemExit as e:
            rc = int(e.code or 0)
        except Exception as e:
            rc = 1
            buf.write("loop: %s: the one-site line raised: %r\n" % (sid, str(e)[:200]))
        text = buf.getvalue()
        if text:
            sys.stdout.write(text)
        out[sid] = {"rc": rc, "lines": text.splitlines()}
    return out


# ---------------------------------------------------------------- nopicture

def _searched_string(rec):
    """The record as the human reads it on the page (web/review.js shows no_picture_found
    searched verbatim): exactly what was searched, in one line, failures included."""
    qid = rec.get("qid") or "no qid"
    parts = ["wikidata %s" % qid] if qid != "no qid" else ["no wikidata item"]
    if rec.get("cat") and rec["cat"] != "none":
        parts.append("Commons category '%s' (%d file%s)" % (
            rec["cat"], rec["n_cat_files"], "" if rec["n_cat_files"] == 1 else "s"))
    else:
        parts.append("no Commons category")
    if qid != "no qid":
        parts.append("P180 depictions of %s: %d of %d file(s) checked" % (
            qid, rec["n_p180"], rec["n_p180_gathered"]))
    parts.append("title searches: %s (%d hit%s)" % (
        ", ".join('"%s"' % q for q in rec["title_queries"]),
        rec["n_title_hits"], "" if rec["n_title_hits"] == 1 else "s"))
    if rec.get("failed"):
        parts.append("FAILED routes: " + "; ".join(rec["failed"]))
    parts.append(rec["date"][:10])
    return "; ".join(parts)


def nopicture(root):
    """The search-set sites that ended without a picture and no fit: their review item is
    marked "no picture found" with EXACTLY what was searched (the search phase's record,
    replacing the batch's generic plans.json string). entries=[] keeps any existing
    candidates (upsert_item merges by plan; the dict branch sets no_picture_found). A site
    whose search routes all failed gets the item too, with the failures recorded: the
    invariant (every built site: a fit or an open item) holds even when the network lies."""
    root = str(root)
    records = _load_searches(root)
    nofit = _no_fit_sites(root)
    cand = _cand_sites(root)
    n = 0
    for sid in sorted(records):
        if sid not in nofit or sid in cand:
            continue
        s = _searched_string(records[sid])
        review.upsert_item(root, sid, [], no_picture={"searched": s, "at": _now()})
        n += 1
        print("nopicture %s: %s" % (sid, s))
    print("nopicture: %d item(s) marked" % n)
    return n


# ---------------------------------------------------------------- sync

def _fail_entry(sid, plan, doc, detail, root):
    """The review-item candidate for a document the sync could not build: the picture, the
    doc's anchors, and the failure as recorded - so the invariant (a fit or an open item)
    holds even when the overlay cannot be built."""
    entry = {
        "plan": plan,
        "title": doc.get("title") or plan,
        "url": doc.get("url") or ("books/%s/%s" % (doc["ia"], doc["file"]) if doc.get("ia") else None),
        "pairs": doc.get("pairs") or [],
        "why": "sync failed: %s" % detail,
    }
    ev = review.candidate_evidence(plan, root)
    if ev is not None:
        entry["evidence"] = ev
    if doc.get("score") is not None:
        entry["gate_score"] = doc["score"]
    return entry


def sync(root):
    """The one and only page-facing sync (the only task that runs it): every fit document
    - the hand fits, the automatic ones, the human-saved ones - becomes its site's overlay
    and its drawings count, through the existing plan_fit machinery, one document at a
    time with per-doc proof: the one-site line's own decisions (site_done._sync_doc: a hand
    fit builds with no check; an agent document through the fabrication/spread line check,
    a pattern is sent to the review item and its doc deleted; an unmarked auto doc is
    stamped by:agent first; an unmarked non-auto doc is refused, kept and recorded).
    Unlike the serve worker, a failure on one document never stops the sweep: the failure
    is recorded, the site's review item gets the reason, and the sweep goes on (the fix for
    the give-up-the-whole-sweep weakness, PITFALLS pipeline/plan_fit.py). prune drops the
    overlays the deleted pattern docs left behind. -> {site: [{doc, action, detail}]}."""
    root = str(root)
    results = {}
    n = 0
    for name, doc in _all_docs(root):
        sid = doc.get("site") or name.split(".")[0]
        plan = doc.get("plan") or (name[len(sid) + 1:] if name.startswith(sid + ".") else name)
        try:
            action, detail = site_done._sync_doc(root, sid, plan, doc)
        except Exception as e:
            action, detail = "failed", (str(e) or repr(e))[:200]
            review.upsert_item(root, sid, [_fail_entry(sid, plan, doc, detail, root)])
            print("sync %s: FAILED (recorded in the site's review item, the sweep goes on)" % name)
        else:
            print("sync %s: %s%s" % (name, action, (": " + detail) if detail else ""))
        results.setdefault(sid, []).append({"doc": name, "action": action, "detail": detail})
        n += 1
    plan_fit.prune(root)
    print("sync: %d document(s) over %d site(s)" % (n, len(results)))
    return results


# ---------------------------------------------------------------- export / report

def export(root):
    """web/data/review.json = the current open list for the page's Review section (201):
    resolved items out (the derivation records a write-once resolution into the item file),
    new items in. The one and only writer of that page file. -> (n_open, n_total)."""
    root = str(root)
    n_open, n_total = review.export(root)
    print("export: %d open of %d item(s) -> web/data/review.json" % (n_open, n_total))
    return n_open, n_total


def _golden_doc_ids(root):
    """The doc names pinned by tests/golden/hand_fit_docs.sha256 - the hand fits the 000
    golden test protects (the file also pins the 19 hand-fit site.json files; those are not
    documents)."""
    p = Path(root) / "tests" / "golden" / "hand_fit_docs.sha256"
    out = set()
    if not p.is_file():
        return out
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        path = line.split()[-1]
        if path.startswith("data/db/platefits/") and path.endswith(".json"):
            out.add(path[len("data/db/platefits/"):-5])
    return out


def _item_files(root):
    d = Path(root) / "data" / "review"
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.iterdir()):
        if p.suffix == ".json":
            out.append(json.loads(p.read_text()))
    return [i for i in out if i.get("site")]


def _open_items(root):
    """The open item files, by review.export's own rule (a recorded resolution, or a
    resolving document, closes one) - the report reads the store, not the page file, so it
    agrees with the page the export phase just wrote. -> (open, total)."""
    items = _item_files(root)
    open_ = [i for i in items if not review.resolved_doc(i, root)]
    return open_, len(items)


def report(root, at=None):
    """docs/batch.md (box 5): the report the human reads. Counts per outcome over ALL
    built sites, one bucket per site (a fitted site can also carry an item for its other
    pictures - the items are counted separately, the batch's convention); the 20-sample of
    the WHOLE automatically-accepted-fits union drawn with the recorded seed SEED_212 (the
    human's 18/20 check, GOAL point 3, must be repeatable - a moving sample would make it
    unrepeatable); and the no-picture list with each site's exact searched record."""
    root = str(root)
    sites = _sites(root)
    golden = _golden_doc_ids(root)
    docs = _all_docs(root)
    n_hand = n_saved = n_auto = 0
    auto_ids, scores, site_of = [], {}, {}
    docs_by_site = {}
    for name, doc in docs:
        docs_by_site.setdefault(doc.get("site"), []).append((name, doc))
        who = plan_fit.who_placed(doc)
        if doc.get("by") == "hand":
            if name in golden:
                n_hand += 1
            else:
                n_saved += 1
        elif who == "agent":
            n_auto += 1
            auto_ids.append(name)
            scores[name] = doc.get("score")
            site_of[name] = doc.get("site")
    auto_ids.sort()
    open_items, n_items = _open_items(root)
    item_of = {}
    for i in open_items:
        item_of.setdefault(i["site"], i)

    counts = {"fit: hand (the golden set)": [], "fit: human-saved": [], "fit: automatic": [],
              "review item": [], "no picture found": [], "uncovered (needs attention)": []}
    for sid in sorted(sites):
        ds = docs_by_site.get(sid, [])
        item = item_of.get(sid)
        if any(n in golden and d.get("by") == "hand" for n, d in ds):
            counts["fit: hand (the golden set)"].append(sid)
        elif any(d.get("by") == "hand" for n, d in ds):
            counts["fit: human-saved"].append(sid)
        elif any(plan_fit.who_placed(d) == "agent" for n, d in ds):
            counts["fit: automatic"].append(sid)
        elif item is not None and (item.get("candidates") or []):
            counts["review item"].append(sid)
        elif item is not None and item.get("no_picture_found"):
            counts["no picture found"].append(sid)
        elif item is not None:
            counts["review item"].append(sid)
        else:
            counts["uncovered (needs attention)"].append(sid)

    k = min(20, len(auto_ids))
    sample = random.Random(SEED_212).sample(auto_ids, k) if k else []
    recs = _load_searches(root)
    no_pic = []
    for i in sorted(open_items, key=lambda i: (i.get("name") or i["site"]).lower()):
        if i.get("candidates") or not i.get("no_picture_found"):
            continue
        searched = i["no_picture_found"].get("searched")
        if not searched and recs.get(i["site"]):
            searched = _searched_string(recs[i["site"]])
        no_pic.append((i.get("name") or i["site"], i["site"],
                       searched or "nothing has been searched yet"))

    L = ["# The cover (212): the last uncovered sites, the final sync, the report", ""]
    L.append("at: %s" % (at or _now()))
    L.append("")
    L.append("Built sites: %d. %s" % (
        len(sites),
        "Every built site ends with a fit or an open review item."
        if not counts["uncovered (needs attention)"]
        else "%d site(s) still have neither - the invariant is broken, see the items."
        % len(counts["uncovered (needs attention)"])))
    L.append("")
    L.append("Fit documents: %d total: %d hand (the golden set), %d human-saved (by:hand outside it), "
             "%d automatic (by:agent: batch + matcher + line-saved)"
             % (n_hand + n_saved + n_auto, n_hand, n_saved, n_auto))
    L.append("")
    L.append("## Counts (one bucket per built site; a fitted site can also carry an item for its other pictures)")
    L.append("")
    for k2 in counts:
        L.append("- %s: %d" % (k2, len(counts[k2])))
    L.append("- review items open on the page: %d (of %d item files)" % (len(open_items), n_items))
    L.append("")
    L.append("## Sample of automatically accepted fits (for the human's 18/20 check)")
    L.append("")
    L.append("Seed: %d (the sample below is reproducible from it: random.Random(%d) over the "
             "sorted ids of all %d automatic documents)" % (SEED_212, SEED_212, len(auto_ids)))
    L.append("")
    L.append("| doc | page | gate med (m) |")
    L.append("|---|---|---|")
    if sample:
        for name in sample:
            L.append("| %s | %s | %s |" % (name, batch_us._page_url(site_of[name]), scores.get(name)))
    else:
        L.append("| (none) | | |")
    L.append("")
    L.append("## No picture found (exactly what was searched, per site)")
    L.append("")
    L.append("| site | searched |")
    L.append("|---|---|")
    if no_pic:
        for name, sid, searched in no_pic:
            L.append("| %s (%s) | %s |" % (name, sid, searched.replace("|", "\\|")))
    else:
        L.append("| (none) | |")
    L.append("")
    out = Path(root) / "docs" / "batch.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L))
    print("report: %d site(s) bucketed, %d-document sample -> %s" % (len(sites), len(sample), out))
    return str(out)


# ---------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Cover: the last uncovered sites, the final sync, the report (task 212).")
    ap.add_argument("phase", choices=["fetch", "search", "stage", "loop", "nopicture",
                                      "sync", "export", "report", "all"])
    ap.add_argument("--root", default=str(ROOT), help="the data root (default: this checkout)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--working", action="store_true",
                   help="REFUSED by this task: the vision model invented its fit points (301) "
                        "and the lead (ef84a05) forbids it for placement - 212's fit is the matcher")
    g.add_argument("--model-json", default=None,
                   help="recorded model answers for the loop (the batch's dry-run convention); "
                        "the loop phase's only")
    ap.add_argument("--live", action="store_true",
                    help="stage: evidence.record fetches the live route for the new rows (network)")
    a = ap.parse_args(argv)
    if a.working:
        print("refused: --working would place fits with the local vision model; 212's fit is the "
              "matcher (the lead, ef84a05) - never by this task")
        return 2
    if a.model_json and a.phase not in ("loop", "all"):
        print("refused: --model-json applies to the loop phase only")
        return 2
    if a.model_json and not os.path.isfile(a.model_json):
        print("error: --model-json file is missing: %s" % a.model_json)
        return 2
    phases = ["fetch", "search", "stage", "loop", "nopicture", "sync", "export", "report"] \
        if a.phase == "all" else [a.phase]
    for ph in phases:
        try:
            if ph == "fetch":
                fetch(a.root)
            elif ph == "search":
                search(a.root)
            elif ph == "stage":
                stage(a.root, live=a.live)
            elif ph == "loop":
                loop(a.root, model_json=a.model_json)
            elif ph == "nopicture":
                nopicture(a.root)
            elif ph == "sync":
                sync(a.root)
            elif ph == "export":
                export(a.root)
            else:
                report(a.root, at=_now())
        except SystemExit as e:
            print("phase %s: %s" % (ph, e))
            return 1
        except Exception as e:
            print("phase %s failed: %r" % (ph, str(e)[:300]))
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
