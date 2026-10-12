"""Stukeley, *Stonehenge, a Temple Restor'd to the British Druids* (1740), and the Commons-hosted
Stukeley plates (task 209b, GOAL point 4): two legs, both feeding rows into this task's staging
files data/commons/files_wiltshire_b.jsonl + classified_wiltshire_b.jsonl (211 consolidates).

Leg 1 - the Internet Archive British Museum scan of the 1740 book (ia=bim_eighteenth-century_
stonehenge-a-temple-rest_stukeley-william_1740, 166 leaves; BookReader pages + hOCR verified
2026-10-12): the standard book machinery runs UNMODIFIED (the book really is on IA, so no
local-copy wrap - the key difference from 209a's Hoare), per-book artifacts only (triage/<ia>.*.
jsonl, lists/<ia>.json + .map.json). The book's printed plate list is transcribed from the hOCR
(the --list session) into STUKLEY_PLATES in the books_lists PLATES format; when set, register()
injects it into books_lists.PLATES in-process (pipeline/books_lists.py is owned by 217; the
213/civitates hand-list pattern that cmd_ocrmap's comment points at) and --list runs
books_lists.cmd_ocrmap over it.

Leg 2 - the Commons-hosted Stukeley plates (the 205-Kip pattern, no book machinery): the three
rows in STAGED below, visually verified 2026-10-12 (the Houghton 1743 TAB. VIII Avebury plan ->
avebury-q661855; the 1722 Itinerarium inward view of Stonehenge -> stonehenge-q39671; the 1722
pen drawing of Kit's Coty House -> kit-s-coty-house-q4222497). All three sites are existing
catalog sites (cross-checked against data/catalog/sites.jsonl at stage time; drift fails loud),
so no extras file is needed. The two Petrie 1880 files of the same Commons category are already
canonical (data/commons/files.jsonl rows 713/714) - a title in the canonical files is a hard fail
here; their identification unblocked 209c's Commons fallback (docs/lead_wiltshire.md).

usage: src_wiltshire_stukeley.py --fetch         live: the IA book's triage pages (books.cmd_fetch,
                                               resumable; the book is short, no long background job)
       src_wiltshire_stukeley.py --status       offline: leaf count + triage progress from the cached
                                               bookreader.json, and the LLM ports
       src_wiltshire_stukeley.py --triage A|F|B  live (Qwen replicas on 127.0.0.1): the triage stages
                                               through books.cmd_triage_* unmodified
       src_wiltshire_stukeley.py --list         live until STUKLEY_PLATES is set: print the hOCR text
                                               of the front leaves (the book's plate list, for transcription);
                                               once set: register() + books_lists.cmd_ocrmap -> the per-book
                                               lists/<ia>.json + .map.json only (the shared index.jsonl /
                                               validation.json are never written - 211 rebuilds them)
       src_wiltshire_stukeley.py [--stage]    live (one paced batched metadata call): stage the STAGED
       [--dry]                                 Commons rows into files_wiltshire_b.jsonl +
                                               classified_wiltshire_b.jsonl (--dry previews, --stage is the live run)
       src_wiltshire_stukeley.py --check       offline (no network): join the staged files, run
                                               fit/evidence.py's check over every staged row
       src_wiltshire_stukeley.py --golden      write tests/golden/src_wiltshire_stukeley_sample.json

The system python3 has no numpy (commons -> aw), so every command runs under .venv/bin/python;
the module top stays stdlib-only (books, books_ia, books_lists, commons and books_match import
lazily, the fit/src_kip.py idiom). The existing hand fits (Allcroft Avebury fig. 187, Allcroft
Windmill Hill fig. 186, in data/db/platefits/) are not re-staged or re-fitted: new rows only.
If the human delivers *A survey of Wilts* (1740, the true Wiltshire volume), it joins this module
as a second book via the 209a local-copy wrap pattern.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))  # books / books_ia / books_lists import lazily, at call time

KEY = "stukeley_templerestored1740"
IA = "bim_eighteenth-century_stonehenge-a-temple-rest_stukeley-william_1740"
REGION = "Europe"
YEAR = 1740
CITE = ("William Stukeley, Stonehenge, a Temple Restor'd to the British Druids, London 1740 "
        "(British Museum scan; the exact printed title wording to be confirmed from the hOCR title "
        "page when --list runs)")
WHY = ("Stukeley's 1740 Stonehenge book: the numbered Stonehenge plan, the Avenue plan and the "
       "Wiltshire map tie to stonehenge-q39671. The only Stukeley book on IA - the true Wiltshire "
       "volume, A survey of Wilts (1740), is not on IA; a human-downloaded copy, if it arrives, "
       "joins this task as a second book (the 209a wrap pattern). The IA metadata carries no "
       "title/date/creator, so the cite is hand-written (checked 2026-10-13).")

FILES_B = os.path.join(ROOT, "data", "commons", "files_wiltshire_b.jsonl")
CLASSIFIED_B = os.path.join(ROOT, "data", "commons", "classified_wiltshire_b.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
SITES_JSONL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

# TODO (the IA-leg session, after --fetch / --triage A): transcribe the book's printed list of
# plates from the hOCR (--list prints the front leaves) into the books_lists PLATES format,
#   STUKLEY_PLATES = """
#   I||<title as printed>|<page printed in the list>|<s/o/u kind>
#   II||...
#   """
# (kind s = site plan, o = other, u = unsure - the books_lists header). When set, register()
# injects it into books_lists.PLATES in-process and --list runs books_lists.cmd_ocrmap, which
# writes the per-book lists/<ia>.json + .map.json.
STUKLEY_PLATES = None

# The three sites the Commons rows tie to - all existing catalog sites (no extras file needed).
# Cross-checked against data/catalog/sites.jsonl (and web/data/sites.json) at stage time: a
# missing site, or a moved qid/lon/lat, fails loud.
SITES = {
    "avebury-q661855": dict(qid="Q661855", name="Avebury", lon=-1.854167, lat=51.428611),
    "stonehenge-q39671": dict(qid="Q39671", name="Stonehenge", lon=-1.826111, lat=51.178889),
    "kit-s-coty-house-q4222497": dict(qid="Q4222497", name="Kit's Coty House", lon=0.50261, lat=51.32),
}

# The Commons rows (205-Kip pattern), visually verified 2026-10-12 (docs/lead_wiltshire.md):
# (title, site id, named_place, want, label, kind, w, h). named_place is what the caption prints
# (stage() re-checks it against the live title+desc before any row is written, and
# fit/evidence.py's check_caption re-verifies it offline from the stored fields). want is the
# plate's date, applied as the Kip/Mackenzie date override only when the dump date differs -
# that is the kitscoty row alone (the Commons record has no date: the 1722 Itinerarium style
# attribution, the nuance in docs/lead_wiltshire.md, not on the row beyond date=1722). (w, h) is
# the live size re-asserted on every stage run: a renamed or replaced file fails loud. kind maps
# to the hand classification: plan -> p_plan 1.0, view -> p_birdseye 1.0 (the lead_artists idiom
# for drawn views).
STAGED = [
    ("File:Houghton Arc 855.214 - Stukely, the Druid temple of Abury.jpg",
     "avebury-q661855", "Abury", "1743",
     "Avebury, scenographic view by William Stukeley, 1743 (TAB. VIII of the 1743 second edition of "
     "Abury, a temple of the British druids)",
     "plan", 2269, 1362),
    ("File:Stonehenge Dessin Stukeley 1722 03547.jpg",
     "stonehenge-q39671", "Stonehenge", "1722",
     "Stonehenge, inward view by William Stukeley, 1722 (Itinerarium Curiosum)",
     "view", 4620, 2430),
    ("File:Stukelykitscoty.jpg",
     "kit-s-coty-house-q4222497", "Kitscoty", "1722",
     "Kit's Coty House, pen drawing by William Stukeley, 1722 (Itinerarium, style-attributed - "
     "Commons has no date)",
     "view", 1020, 320),
]


def now():
    return time.strftime("%Y-%m-%d")


def _commons():
    import commons  # lazy: commons -> aw needs numpy (absent from the system python3)
    return commons


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def _append(path, rows):
    if not rows:
        return
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _catalog():
    """{id: site} over the catalog and the web build: the rows may only tie to sites that exist."""
    out = {s["id"]: s for s in _load(SITES_JSONL)}
    for s in json.load(open(WEB_SITES, encoding="utf-8"))["sites"]:
        out.setdefault(s["id"], s)
    return out


def register():
    """In-process registration: books.BOOKS gets this book and NOTHING else is touched - the book
    really is on IA, so the machinery's IA calls (pages, page_texts, fetch_triage) run unmodified
    (the key difference from 209a's Hoare, which wraps all three for its local copy). When
    STUKLEY_PLATES is transcribed, its entry is also injected into books_lists.PLATES in-process
    (books_lists is owned by 217; the 213/civitates hand-list pattern that cmd_ocrmap's comment
    points at). Idempotent: a second register() is a no-op."""
    import books
    books.BOOKS[KEY] = dict(ia=IA, region=REGION, year=YEAR, cite=CITE, why=WHY)
    if STUKLEY_PLATES is not None:
        import books_lists
        books_lists.PLATES[IA] = STUKLEY_PLATES


def fetch():
    """All triage-size page images (books.cmd_fetch, resumable; 166 leaves - a short foreground run)."""
    register()
    import books
    books.cmd_fetch([KEY])


def status():
    """Offline: leaf count and sizes from the cached bookreader.json (never a network fetch - a
    missing cache reports 'not fetched yet'), the triage progress, and which LLM ports answer."""
    import books
    import books_ia
    path = os.path.join(books_ia.RAW, IA, "bookreader.json")
    if not os.path.exists(path):
        print(f"{KEY} {IA}: not fetched yet (no cached bookreader.json; --fetch first)")
    else:
        d = json.load(open(path))
        pages = [p for spread in d["data"]["brOptions"]["data"] for p in spread]
        # the raw page dicts carry no "n" - n is the flat-list index (books_ia.pages assigns it)
        long = [max(p["width"], p["height"]) for p in pages]
        done = sum(1 for n in range(len(pages)) if os.path.exists(books.triage_path(IA, n)))
        print(f"{KEY} {IA}: {len(pages)} leaves, triage {done}/{len(pages)}, "
              f"long side {min(long)}-{max(long)} px")
    up = [u for u in books.LLM_URLS if books.llm_up(u)]
    print("LLM:", ", ".join(up) or "none up (the triage stages exit until a Qwen replica answers)")


def triage(stage):
    """Stage A/F/B through the unmodified books.run_stage (resumable; needs a live Qwen replica,
    else run_stage exits with its own message)."""
    register()
    import books
    {"A": books.cmd_triage_a, "F": books.cmd_triage_f, "B": books.cmd_triage_b}[stage]([KEY])


def list_cmd():
    """Until STUKLEY_PLATES is transcribed: print the hOCR text of the book's front leaves (the
    plate list lives there; the hOCR pair is downloaded once and cached). Once transcribed: run
    books_lists.cmd_ocrmap over the injected plate list - it writes only the per-book
    lists/<ia>.json + .map.json (the map stays [] until stage A exists, as cmd_ocrmap guards)."""
    if STUKLEY_PLATES is None:
        import books_ia
        texts = books_ia.page_texts(IA)  # downloads + caches the hOCR pair (~165 KB)
        for leaf in sorted(texts)[:20]:
            print(f"--- leaf {leaf} ---")
            print(texts[leaf][:1200])
        return
    register()
    import books_lists
    books_lists.cmd_ocrmap([KEY])


def evidence_for(named, s):
    """The hand-recorded caption_coords tie for a staged Commons row (fit/evidence.py's
    check_caption re-verifies it offline from the stored fields alone): named_place is what the
    caption prints (stage() proved it a norm-substring of the live title+desc before the row was
    written), and the stored place coordinates are the site's own verified point - dist_m 0.0,
    never a name-search resolution (the famous namesakes)."""
    return {"rec": "evidence/1", "kind": "caption_coords", "checked": now(),
            "named_place": named, "place_qid": s["qid"], "place_label": s["name"],
            "place_lon": s["lon"], "place_lat": s["lat"],
            "site_lon": s["lon"], "site_lat": s["lat"], "dist_m": 0.0}


def stage(dry=False):
    """Stage the STAGED Commons rows into this task's own files (append-only, idempotent on
    (site, title)). Drift fails loud: a title already in the canonical files.jsonl (the two Petrie
    1880 files - never re-staged, whatever site a rogue row names), a site missing from (or moved
    off) the catalog, a title Commons no longer holds, a live size moved off the table, a named
    place the live caption no longer prints, or a row commons.keep() would drop after the date
    override is applied. One live call: the batched, paced commons.info over the three titles -
    the file bytes are never fetched (PITFALLS: upload.wikimedia.org rate-limits raw downloads,
    not the API)."""
    c = _commons()
    import books_match
    known = _catalog()
    have = {(r.get("site"), r.get("title")) for r in _load(FILES_B) + _load(CLASSIFIED_B)}
    canonical = {r.get("title") for r in _load(FILES_CANONICAL) if r.get("title")}
    meta = c.info([t for t, *_ in STAGED])
    new_files, new_cls = [], []
    for title, sid, named, want, label, kind, w, h in STAGED:
        s = SITES[sid]
        if title in canonical:
            raise SystemExit(f"{title!r} is already in the canonical files.jsonl: never re-staged "
                             f"(the two Petrie 1880 files are the case this title-only guard was built for)")
        cat = known.get(sid)
        if cat is None:
            raise SystemExit(f"STAGED {title!r}: site {sid!r} not in the catalog")
        if (cat.get("qid"), cat.get("lon"), cat.get("lat")) != (s["qid"], s["lon"], s["lat"]):
            raise SystemExit(f"catalog drift for {sid}: table {s['qid']} {s['lon']},{s['lat']} vs "
                             f"catalog {cat.get('qid')} {cat.get('lon')},{cat.get('lat')}")
        m = meta.get(title) or {}
        if not m.get("url"):
            raise SystemExit(f"not on Commons (title changed?): {title}")
        if (m.get("w"), m.get("h")) != (w, h):
            raise SystemExit(f"size drift for {title}: live {(m.get('w'), m.get('h'))} != {(w, h)}")
        if books_match.norm(named) not in books_match.norm(title + " " + (m.get("desc") or "")):
            raise SystemExit(f"the live caption no longer names {named!r} for {title}: the tie is dead")
        if (sid, title) in have:
            continue
        m2 = dict(m)
        if want and c.year_of(title, m2) != c.year_of(title, {"date": want}):
            m2 = dict(m2, date=want, date_commons=m.get("date"))
        if not c.keep(title, m2):
            raise SystemExit(f"commons.keep() would drop {title!r}: fix the table or record the drop in "
                             f"docs/lead_wiltshire.md")
        f = {"site": sid, "qid": s["qid"], "title": title, "year": c.year_of(title, m2), "wd_plan": False,
             "cat": None, "name": label, "by": "fit/src_wiltshire_stukeley.py", **m2,
             "evidence": evidence_for(named, s)}
        new_files.append(f)
        new_cls.append({"site": sid, "title": title,
                        "p_plan": 1.0 if kind == "plan" else 0.0,
                        "p_birdseye": 1.0 if kind == "view" else 0.0,
                        "p_photo": 0.0, "by": "hand"})
    print(f"staged: {len(new_files)} new pictures" + (" (dry run)" if dry else ""))
    for f in new_files:
        print("   ", f["site"], "|", f["title"], "|", f["date"], "|", f"year {f['year']}",
              ("| date_commons " + f["date_commons"]) if "date_commons" in f else "")
    if dry:
        return
    _append(FILES_B, new_files)
    _append(CLASSIFIED_B, new_cls)


def check_staged():
    """Offline (no network): join the staged files (every file row names a catalog or web-built
    site; (site, title) unique; no title already in the canonical files.jsonl; classified rows
    1:1 with the file rows) and run fit/evidence.py's check over every staged row. Returns the
    exit code (0 iff no problem and no FAIL)."""
    import evidence
    files = _load(FILES_B)
    cls = _load(CLASSIFIED_B)
    known = set(_catalog())
    problems = []
    seen = set()
    canonical = {r.get("title") for r in _load(FILES_CANONICAL) if r.get("title")}
    for r in files:
        if not r.get("title"):
            continue
        if r.get("site") not in known:
            problems.append(f"file row names a site that is neither catalog nor web-built: "
                            f"{r['site']!r} ({r['title']!r})")
        k = (r.get("site"), r.get("title"))
        if k in seen:
            problems.append(f"duplicate staged row {k}")
        seen.add(k)
        if r.get("title") in canonical:
            problems.append(f"staged title already in the canonical files.jsonl: {r['title']!r}")
    if {(r.get("site"), r.get("title")) for r in cls} != seen:
        problems.append("the classified rows are not 1:1 with the staged file rows")
    for p in problems:
        print("join:", p)
    code, text = evidence.check(FILES_B, NO_BOOKS)
    print(text)
    return 1 if problems else code


def _norm(rows):
    """The rows for the golden file: "checked" and "date_commons" normalized (they vary with the
    staging date), keys sorted by the dump."""
    out = []
    for r in rows:
        r = dict(r)
        if isinstance(r.get("date_commons"), str):
            r["date_commons"] = "0000-00-00"
        ev = r.get("evidence")
        if isinstance(ev, dict) and ev.get("checked"):
            r["evidence"] = dict(ev, checked="0000-00-00")
        out.append(r)
    return out


def golden(path=None):
    """Write tests/golden/src_wiltshire_stukeley_sample.json: all three staged file rows with
    their classified rows, normalized (one per row flavour: the plan, the dated view, the
    overridden-date view). Regenerate only for an intended change."""
    p = path or os.path.join(ROOT, "tests", "golden", "src_wiltshire_stukeley_sample.json")
    files = _load(FILES_B)
    keyed = {(r["site"], r["title"]) for r in files}
    cls = [r for r in _load(CLASSIFIED_B) if (r.get("site"), r.get("title")) in keyed]
    out = {"files": _norm(files), "classified": _norm(cls)}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", p)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] not in ("--fetch", "--status", "--triage", "--list", "--stage", "--dry", "--check", "--golden"):
        raise SystemExit(__doc__.strip().split("usage:")[1].strip())
    if a and a[0] == "--fetch":
        fetch()
    elif a and a[0] == "--status":
        status()
    elif a and a[0] == "--triage" and len(a) >= 2 and a[1] in "AFB":
        triage(a[1])
    elif a and a[0] == "--list":
        list_cmd()
    elif a and a[0] == "--check":
        raise SystemExit(check_staged())
    elif a and a[0] == "--golden":
        golden()
    else:  # no args / --stage: the live stage; --dry: the preview
        stage(a and a[0] == "--dry")
