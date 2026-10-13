"""Numancia (task 210, GOAL.md point 4): the excavation plan of the 1860s campaigns - LÁMINA IV, fig. 5,
"Plano de las excavaciones hechas en Numancia en 1855" of Eduardo Saavedra's 'Descripción de la vía
romana de Úxama á Augustóbriga', as published in RAH Memorias de la Real Academia de la Historia tomo IX
(Madrid, 1879). The free machine-readable copy is Internet Archive item memoriasdelareal009real (Boston
Public Library 2012 scan, 300 ppi, 766 leaves; the 1879 work is public domain in the USA and the EU, the
item carries no license field - docs/lead_numancia.md §1). The plate is PDF leaf 507; the item has no
per-leaf image derivatives (the zip-only Google scan - per-leaf .jpg/.jp2/BookReader/composite all 404),
so the row's picture is rendered locally from the PDF (--render) into
data/raw/commons/numancia/<sha1(title)[:16]>.jpg - the slot the page and the fit tool read. data/raw/ is
gitignored: the image is re-derived per worktree, the row therefore carries no fetchable thumb (nothing
could repopulate it), and the tests never require the file's existence (they check the path convention
and validate the image when present). The row is tied to the EXISTING catalog site `numancia`
(data/catalog/extras.jsonl; no new site, extras_numancia.jsonl stays absent). The GOAL's "1860s" lead
resolves to this 1853/55 plan as printed 1879 (Saavedra's site-finding campaign, the same campaigns the
lead asks for) - plans are 150-year-exempt (PLAN.md assumption 4) and 1879 <= 1925 keeps the row
page-eligible, the date is recorded on the row either way.

usage: src_numancia.py --render       working phase (network): the IA PDF (with retries - /download/ is
                                      flaky per file) -> pdftoppm leaf 507 at 300 ppi quality 85 ->
                                      data/raw/commons/numancia/0fa271e2444f7bfc.jpg (.part + replace) -
                                      re-run in every worktree before the page or the fit tool needs the
                                      picture (the row is otherwise absent from plans.json, by design)
       src_numancia.py --sweep        working phase (network): re-verify the source (lead doc §1-§2): the
                                      item up with 766 leaves, the PDF and the djvu.txt present at their
                                      recorded sizes, no license field and not borrow-only, the printed
                                      index line of the plan in the djvu text, the PDF range-GETs with the
                                      %PDF magic, and the local render - when present - is a valid
                                      non-blank 6713x2709 JPEG (its absence is reported, not a failure)
       src_numancia.py stage [--dry]  stage the one row into this task's files (append-only, idempotent
                                      on (site, title)): the file row (with the 200 evidence field,
                                      evidence LAST) + the classified row; fail loud if the local render
                                      is missing (--render first)
       src_numancia.py --check        offline (no network): the join (the row names the existing numancia
                                      site, whose catalog point matches the stored evidence point; (site,
                                      title) unique; a staged row already in the canonical files.jsonl is
                                      a no-op only when identical to the canonical row (211's first-row-
                                      wins merge) - a same-key different row still fails loud; classified
                                      1:1; the image-path convention holds and the render, when present,
                                      matches the row) + the fit/evidence.py check over the staged row
       src_numancia.py --golden       write tests/golden/src_numancia_sample.json (the staged rows,
                                      checked normalized) and src_numancia_evidence.txt (the exact
                                      stdout of the offline evidence check); regenerate only for an
                                      intended change

The working-phase commands run under .venv/bin/python (PIL for the image checks, numpy for evidence);
the module top stays stdlib-only. Staging writes only this task's files; 211 consolidates them into the
canonical ones and builds (the page shows the row only in worktrees that have run --render).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The source (docs/lead_numancia.md §1): every value below was verified live 2026-10-12 and is asserted
# by --sweep (drift fails loud).
ITEM = "memoriasdelareal009real"  # IA item: RAH Memorias tomo IX (1879), BPL 2012 scan
META_URL = f"https://archive.org/metadata/{ITEM}"
PDF_URL = f"https://archive.org/download/{ITEM}/{ITEM}.pdf"
PDF_SIZE = "37664978"
DJVU_URL = f"https://archive.org/download/{ITEM}/{ITEM}_djvu.txt"
DJVU_SIZE = "1979917"
ITEM_PAGE = f"https://archive.org/details/{ITEM}"
LEAF = 507           # LÁMINA IV (eye-confirmed 2026-10-12, lead doc §2; the djvu page order is not the PDF's)
LEAF_COUNT = 766     # the scan's leaf count (page_numbers.pages, 1:1 with the PDF pages)
# The one printed line that identifies the plan: the ÍNDICE DE LAS LÁMINAS (leaf 497) names it "en el
# sitio de Numancia en 1853" (the plate caption says 1855 - the discrepancy is inside the volume). The
# djvu OCR doubles spaces and mangles the LÁMINA numbering (LAMINA IV prints twice as "LAMINA 3."), so
# the sweep asserts this whitespace-collapsed line and never a plate number.
DJVU_LINE = "Plano de las excavaciones hechas en el sitio de Numancia en 1853"

SITE = "numancia"  # the existing catalog site (data/catalog/extras.jsonl; already built - no new row)
QID = "Q623407"    # Numantia: the item the site row implicitly is (labels en "Numantia" / es "Numancia")
TITLE = ("Plano de las excavaciones hechas en el sitio de Numancia "
         "(Lám. IV, fig. 5, Saavedra 1879; excavations of 1853/1855)")
W, H = 6713, 2709  # the 300 ppi render of leaf 507 (the image bytes re-derive byte-identically)
# The evidence specifics (lead doc §3): Q623407's P625 and the site row's point (catalog extras.jsonl).
# "printed 1879" (not "Published 1879") keeps commons.PUBLISHED from firing on the desc, so year_of
# takes the row's own date field; title/desc carry both name forms (Numancia/Numantia) for the check.
DESC = ("Lám. IV (leaf 507) of Eduardo Saavedra, 'Descripción de la vía romana de Úxama á Augustóbriga', "
        "RAH Memorias de la Real Academia de la Historia tomo IX, printed 1879, Madrid; rendered locally "
        "from the Internet Archive volume scan (item memoriasdelareal009real, 300 ppi) - the item has no "
        "per-leaf image. Numancia (Numantia), the Roman city at the Cerro de la Muela near Soria, Spain. "
        "Fig. 5 (scale 1/1000): the excavation plan of Numancia from Saavedra's 1853/1855 campaign: the "
        "hatched dig area on the hill slope, the excavated room-structure with its rubble field, the "
        "dashed survey grid, section A-B ('Corte por A B'), 'Monumento hallado'. The same plate carries "
        "figs 1-2 (the Calatañazor rock tombs, the ermita of the Mártires de Garray, 1/300), fig 3 (the "
        "'Muro de Numancia', alzado 5 / corte 4, 1/300) and figs 7-8 (the Augustóbriga walls and a "
        "wall-section, 1/300 and 1/1000). Lith. J. Domm. Madrid. Public domain: printed 1879, author "
        "d. c. 1902; the IA item carries no license field.")
ARTIST = "Eduardo Saavedra (lith. J. Domm., Madrid)"
LICENSE = "public domain (1879, author d. c. 1902; the IA item carries no license field)"
PLACE_LON, PLACE_LAT = -2.444447, 41.809392  # Q623407's P625
SITE_LON, SITE_LAT = -2.4443, 41.8096        # the catalog row's point (re-verified by --check)

FILES = os.path.join(ROOT, "data", "commons", "files_numancia.jsonl")
CLASSIFIED = os.path.join(ROOT, "data", "commons", "classified_numancia.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
EXTRAS_CANONICAL = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
SITES_WEB = os.path.join(ROOT, "web", "data", "sites.json")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file
UA = {"User-Agent": "ancient-works research agent (task 210)"}  # IA /download/ needs a UA (bare: 0 bytes)
PDFTOPPM = "/usr/bin/pdftoppm"  # poppler-utils, present on this machine (PITFALLS)


def now():
    return time.strftime("%Y-%m-%d")


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def _append(path, rows):
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _image_path():
    """The page's slot for the plate: data/raw/commons/<site>/<sha1(title)[:16]>.jpg, the commons.local
    rule (pipeline/commons.py) - the file the page and the fit tool read when this row reaches
    files.jsonl. 0fa271e2444f7bfc for the pinned title."""
    return os.path.join(ROOT, "data", "raw", "commons", SITE,
                        hashlib.sha1(TITLE.encode()).hexdigest()[:16] + ".jpg")


def _gray_std(im):
    """The image's grayscale std from its histogram (a blank page is ~0, a drawn plate is tens):
    the non-blank test without numpy."""
    hist = im.convert("L").histogram()
    n = sum(hist)
    mean = sum(i * c for i, c in enumerate(hist)) / n
    return (sum(c * (i - mean) ** 2 for i, c in enumerate(hist)) / n) ** 0.5


def _ia_get(url, tries=3, timeout=600, range_end=None):
    """GET (or a Range GET) of an archive.org object with the UA; the /download/ backend is flaky per
    file (transient 170-byte nginx 500 pages come and go - retry with backoff). Returns (status, bytes)."""
    last = None
    for k in range(tries):
        headers = dict(UA)
        if range_end is not None:
            headers["Range"] = f"bytes=0-{range_end}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
                return r.status, r.read()
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            last = e
            print(f"  {url}: retry {k + 1}/{tries} ({e!r})", flush=True)
            time.sleep(5 * (k + 1))
    raise SystemExit(f"IA GET of {url} failed after {tries} tries: {last!r}")


# ---------------------------------------------------------------- the working phase (network)

def render():
    """The plate image, re-derived (the only one this row can have - the item has no fetchable per-leaf
    image): download the IA PDF, render leaf 507 at 300 ppi quality 85 (the session-3 recipe; the output
    is byte-identical across runs), into the page's slot (.part + replace). Run in every worktree before
    the page or the fit tool needs the picture: data/raw/ is gitignored, so the image never travels."""
    from PIL import Image
    tmp = tempfile.mkdtemp(prefix="numancia_")
    pdf = os.path.join(tmp, ITEM + ".pdf")
    status, data = _ia_get(PDF_URL)
    if data[:4] != b"%PDF":
        raise SystemExit(f"the download is not a PDF (status {status}, {len(data)} bytes - an IA error "
                         "page?): retry later")
    open(pdf, "wb").write(data)
    out = _image_path()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # -singlefile: one <prefix>.jpg with no page-number suffix (the only page rendered)
    subprocess.run([PDFTOPPM, "-jpeg", "-r", "300", "-jpegopt", "quality=85",
                    "-f", str(LEAF), "-l", str(LEAF), "-singlefile", pdf, out + ".part"], check=True)
    im = Image.open(out + ".part")
    if im.size != (W, H):
        raise SystemExit(f"the render is {im.size[0]}x{im.size[1]}, expected {(W, H)} - the scan changed; "
                         f"re-verify the leaf map (lead doc §2) before staging")
    if _gray_std(im) < 1.0:
        raise SystemExit("the render is blank - pdftoppm rendered an empty page (the leaf changed?)")
    os.replace(out + ".part", out)
    print(f"rendered {out} ({W}x{H}, {os.path.getsize(out)} bytes)")


def sweep():
    """Live re-verification of the source (lead doc §1-§2), one pass; exit 1 on any failure - the staging
    files and the golden were verified against this state. The local render is validated when present
    (its absence only reminds to run --render)."""
    from PIL import Image
    fails = []
    # (a) the item's metadata: the leaf count, the two files at their recorded sizes, the license state,
    # not borrow-only
    _, body = _ia_get(META_URL)
    d = json.loads(body)
    md = d.get("metadata") or {}
    pages = (d.get("page_numbers") or {}).get("pages")
    files = {f.get("name"): f.get("size") for f in d.get("files") or []}
    print(f"checked {now()} - IA {ITEM}")
    if not pages or len(pages) != LEAF_COUNT:
        fails.append(f"page_numbers has {len(pages) if pages else 0} leaves, expected {LEAF_COUNT}")
    else:
        print(f"  leaves: {len(pages)} (1:1 with the PDF pages)")
    for name, size in ((ITEM + ".pdf", PDF_SIZE), (ITEM + "_djvu.txt", DJVU_SIZE)):
        if files.get(name) != size:
            fails.append(f"{name} is {files.get(name)!r}, expected size {size}")
        else:
            print(f"  {name}: {size} bytes (as recorded)")
    if md.get("access-restricted-item") == "true":
        fails.append("the item is now borrow-only (was not in 2026-10-12)")
    print(f"  license field: {md.get('license')!r} / licenseurl {md.get('licenseurl')!r} "
          f"(None = none on the item; the 1879 work is PDM, lead doc §1)")
    # (b) the djvu text carries the printed index line of the plan (whitespace-collapsed: the OCR doubles
    # spaces; the plate numbers are mangled, so only this line is asserted)
    _, body = _ia_get(DJVU_URL)
    text = re.sub(r"\s+", " ", body.decode("utf-8", "replace"))
    if DJVU_LINE not in text:
        fails.append("the djvu text no longer carries the ÍNDICE DE LAS LÁMINAS line of the plan "
                     "(re-identify the plate - it may have moved)")
    else:
        print(f"  djvu text: the plate's index line is present")
    # (c) the PDF is downloadable (a Range GET with the %PDF magic; the /download/ backend is flaky)
    status, head = _ia_get(PDF_URL, range_end=65535)
    if status not in (200, 206) or head[:4] != b"%PDF":
        fails.append(f"the PDF range GET came back {status} without the %PDF magic")
    else:
        print(f"  PDF: range GET {status} (206 = ranged OK) with the %PDF magic")
    # (d) the local render, when present: a valid non-blank 6713x2709 JPEG
    p = _image_path()
    if os.path.exists(p):
        try:
            im = Image.open(p)
            im.load()
            ok = (im.format == "JPEG" and im.size == (W, H) and _gray_std(im) >= 1.0)
            print(f"  render: {p} {im.format} {im.size[0]}x{im.size[1]} std {_gray_std(im):.1f}"
                  + ("" if ok else "   <- INVALID"))
            if not ok:
                fails.append(f"the local render is not the {W}x{H} non-blank JPEG (run --render)")
        except Exception as e:
            fails.append(f"the local render does not open: {e!r} (run --render)")
    else:
        print(f"  render: {p} absent (run --render before the page needs the picture - not a failure)")
    if fails:
        for f in fails:
            print("sweep FAIL:", f)
        return 1
    print("sweep: the source is as recorded (lead doc §1-§2)")
    return 0


# ---------------------------------------------------------------- staging (this task's files only)

def _row(checked):
    """The one staged file row, exactly as pinned (the hand-over of 2026-10-12): every field audited -
    year 1879 passes commons.keep()'s 1925 cut, the NO regex is clean on title and desc, the date field
    (not the desc's prose) carries the year, no thumb (nothing fetchable could repopulate the image).
    The evidence field is filled LAST, with the distance computed, never guessed."""
    import evidence  # lazy: commons -> aw needs numpy (absent from the system python3)
    row = {"site": SITE, "qid": QID, "title": TITLE, "year": 1879, "wd_plan": False, "cat": None,
           "name": "Numancia, excavation plan, Saavedra 1879 (excavations of 1853/1855)",
           "by": "fit/src_numancia.py", "url": ITEM_PAGE, "w": W, "h": H, "mime": "image/jpeg",
           "date": "1879", "desc": DESC, "artist": ARTIST, "license": LICENSE, "page": ITEM_PAGE}
    row["evidence"] = {"rec": "evidence/1", "kind": "caption_coords", "checked": checked,
                       "named_place": "Numancia", "place_qid": QID, "place_label": "Numantia",
                       "place_lon": PLACE_LON, "place_lat": PLACE_LAT,
                       "site_lon": SITE_LON, "site_lat": SITE_LAT,
                       "dist_m": round(evidence.hav_m(SITE_LON, SITE_LAT, PLACE_LON, PLACE_LAT), 1)}
    return row


def stage(dry=False):
    """Stage the one row into this task's files (append-only, idempotent on (site, title)); 211
    consolidates them. Working phase: fail loud if the local render is missing (--render first) - the
    row's size fields are the render's, and the page only shows the row where the image exists."""
    from PIL import Image
    p = _image_path()
    if not os.path.exists(p):
        raise SystemExit(f"{p} is missing: run `--render` first (the item has no fetchable per-leaf "
                         "image and data/raw/ is gitignored - the page reads this file as is)")
    im = Image.open(p)
    if im.size != (W, H):
        raise SystemExit(f"the local render is {im.size[0]}x{im.size[1]}, expected {(W, H)} - re-run "
                         f"--render and re-verify (lead doc §2)")
    have = {(r.get("site"), r.get("title")) for r in _load(FILES) + _load(CLASSIFIED)}
    if (SITE, TITLE) in have:
        print("already staged (idempotent, no-op)")
        return
    f = _row(now())
    cl = {"site": SITE, "title": TITLE, "p_plan": 1.0, "p_birdseye": 0.0, "p_photo": 0.0, "by": "hand"}
    print("staged:", json.dumps(f, ensure_ascii=False)[:200], "...")
    print("classified:", json.dumps(cl, ensure_ascii=False))
    if dry:
        return
    _append(FILES, [f])
    _append(CLASSIFIED, [cl])


def _canon_norm(r):
    """Row identity under the 211 merge rule (the same norm fit/merge.py uses on the line): key order and
    ASCII escaping don't matter, content does."""
    return json.dumps(r, sort_keys=True, ensure_ascii=False)


def check_staged():
    """Offline (no network): the join of the staged files + the fit/evidence.py check over the staged
    row. The catalog for the check is the canonical extras.jsonl (the site is a catalog site, not a
    staged one); the caption route never consults the catalog, so the verdict is stable after 211's
    consolidation. A staged row whose (site, title) key is in the canonical files.jsonl is a no-op
    ("already merged by 211") only when it is identical to the canonical row under the merge's identity
    rule - a same-key different row still fails loud (the pre-merge clash protection). Returns the exit
    code (0 iff no join problem and no FAIL)."""
    import evidence
    files = _load(FILES)
    cls = _load(CLASSIFIED)
    problems = []
    sites = {s["id"]: s for s in _load(EXTRAS_CANONICAL)}
    web = {}
    if os.path.exists(SITES_WEB):
        web = {s["id"]: s for s in json.load(open(SITES_WEB, encoding="utf-8"))["sites"]}
    if len(files) != 1:
        problems.append(f"expected exactly one staged file row, found {len(files)}")
    for r in files:
        k = (r.get("site"), r.get("title"))
        if r.get("site") != SITE:
            problems.append(f"row site {r.get('site')!r} is not the existing catalog site {SITE!r}")
        s = sites.get(SITE) or web.get(SITE)
        if s is None:
            problems.append(f"the {SITE!r} site row is missing from the catalog and from web/data/sites.json")
        if r.get("qid") != QID:
            problems.append(f"row qid {r.get('qid')!r} is not {QID} (the site's implicit Wikidata item)")
        if r.get("year") != 1879:
            problems.append(f"row year {r.get('year')} is not 1879 (the publication)")
        if r.get("by") != "fit/src_numancia.py" or not r.get("name"):
            problems.append(f"row by/name wrong: {r.get('by')!r} {r.get('name')!r}")
        ev = r.get("evidence") or {}
        if s is not None and (ev.get("site_lon"), ev.get("site_lat")) != (s.get("lon"), s.get("lat")):
            problems.append(f"stored site point {ev.get('site_lon')}, {ev.get('site_lat')} differs from "
                            f"the catalog row {s.get('lon')}, {s.get('lat')}")
        if r.get("mime") != "image/jpeg":
            problems.append(f"row mime {r.get('mime')!r} is not image/jpeg")
    if {(r.get("site"), r.get("title")) for r in files} != {(r.get("site"), r.get("title")) for r in cls}:
        problems.append("the classified rows are not 1:1 with the file rows")
    for r in cls:
        if r.get("p_plan") != 1.0 or r.get("p_birdseye") != 0.0 or r.get("p_photo") != 0.0 or r.get("by") != "hand":
            problems.append(f"classified row wrong: {r}")
    canonical = {}
    for r in _load(FILES_CANONICAL):
        k = (r.get("site"), r.get("title"))
        if k not in canonical:  # first row wins, as in the 211 merge
            canonical[k] = _canon_norm(r)
    seen = set()
    for r in files:
        k = (r.get("site"), r.get("title"))
        if k in seen:
            problems.append(f"duplicate staged row {k}")
        if k in canonical and canonical[k] != _canon_norm(r):
            problems.append(f"staged title already in the canonical files.jsonl: {k}")
        seen.add(k)
    # the image-path convention (commons.local): <sha1(title)[:16]>.jpg in the site's data/raw/commons
    # dir. The file is worktree-local (gitignored): never fail on its absence, validate it when present.
    p = _image_path()
    r = files[0] if files else {}
    h = hashlib.sha1((r.get("title") or "").encode()).hexdigest()[:16]
    if os.path.dirname(p) != os.path.join(ROOT, "data", "raw", "commons", SITE) or \
            os.path.basename(p) != h + ".jpg":
        problems.append(f"the image path {p} breaks the sha1(title)[:16] convention")
    if os.path.exists(p):
        try:
            from PIL import Image
            im = Image.open(p)
            im.load()
            if im.format != "JPEG" or im.size != (W, H) or (r and (r.get("w"), r.get("h")) != (W, H)) \
                    or _gray_std(im) < 1.0:
                problems.append(f"the render {p} is not the {W}x{H} non-blank JPEG the row records")
        except Exception as e:
            problems.append(f"the render {p} does not open: {e!r}")
    else:
        print(f"note: {p} absent in this worktree (gitignored - run --render; not a failure)")
    for pb in problems:
        print("join:", pb)
    code, text = evidence.check(FILES, NO_BOOKS, catalog=EXTRAS_CANONICAL)
    print(text)
    return 1 if problems else code


def _norm(rows):
    """The rows for the golden file: keys are sorted by the dump, 'checked' normalized (it varies with
    the staging date)."""
    out = []
    for r in rows:
        r = dict(r)
        ev = r.get("evidence")
        if isinstance(ev, dict) and ev.get("checked"):
            r["evidence"] = dict(ev, checked="0000-00-00")
        out.append(r)
    return out


def golden():
    """Write the two pins (regenerate only for an intended change): src_numancia_sample.json (the staged
    rows, checked normalized) and src_numancia_evidence.txt (the exact stdout of the offline evidence
    check - the subprocess test compares against it byte for byte)."""
    import evidence
    gdir = os.path.join(ROOT, "tests", "golden")
    os.makedirs(gdir, exist_ok=True)
    files = _load(FILES)
    cls = _load(CLASSIFIED)
    p = os.path.join(gdir, "src_numancia_sample.json")
    out = {"count": {"files": len(files), "classified": len(cls)},
           "files": _norm(files), "classified": _norm(cls)}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", p)
    code, text = evidence.check(FILES, NO_BOOKS, catalog=EXTRAS_CANONICAL)
    p2 = os.path.join(gdir, "src_numancia_evidence.txt")
    with open(p2, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    if code != 0:
        raise SystemExit("the evidence check does not pass - the golden would pin a FAIL")
    print("wrote", p2)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "stage":
        stage("--dry" in a)
    elif a[0] == "--render":
        render()
    elif a[0] == "--sweep":
        raise SystemExit(sweep())
    elif a[0] == "--check":
        raise SystemExit(check_staged())
    elif a[0] == "--golden":
        golden()
    else:
        raise SystemExit(__doc__.split("usage:")[1].strip())
