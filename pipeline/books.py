"""Index the site plans (plates and text figures) in the key public-domain books on ancient earthworks.

Steps (each resumable, each cached):
    books.py fetch   [key ...]   triage-size page images (long side 1400 px) -> data/raw/books/<ia>/triage/
    books.py triageA [key ...]   Qwen stage A on every page: page type + printed numbers -> data/books/triage/<ia>.A.jsonl
    books.py triageB [key ...]   Qwen stage B on site-plan pages: one entry per plan, boxes -> data/books/triage/<ia>.B.jsonl
    books.py ocrmap  [key ...]   list-of-plates entries -> leaves by OCR text (fallback/validation)  (books_lists.py)
    books.py validate            recall/precision of stage A against each book's own list -> data/books/validation.json
    books.py index               data/books/index.jsonl (one row per site plan)
    books.py full    [key ...]   full-resolution images of site-plan pages -> data/raw/books/<ia>/full/
    books.py draw <key> n...     draw stage-B boxes on pages (box check) -> data/books/checks/

Qwen (pipeline/llm.py) only classifies pages and reads printed text; nothing it says is used as a fact
unless it matches the printed list or the page.
"""
import concurrent.futures as cf
import io
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import books_ia as ia  # noqa: E402

ROOT = ia.ROOT
OUT = os.path.join(ROOT, "data", "books")
TRIAGE_PX = 1400

# Chosen scans. Reasons measured 2026-10-10 from IA metadata + BookReader page sizes (see summary.md).
BOOKS = {
    "squier_davis_1848": dict(
        ia="ancientmonuments00squi", region="US", year=1848,
        cite="E. G. Squier and E. H. Davis, Ancient Monuments of the Mississippi Valley (Smithsonian Contributions "
             "to Knowledge vol. 1), Washington 1848",
        why="Library of Congress scan at 500 ppi (median page 2888x4068 px), the highest of the four copies on IA "
            "(two Smithsonian Libraries copies smithsoniancontr11848smit/-smith are 300 ppi, ~2400x3500 px; "
            "ancientmonuments0000squi is a lending-only 1998 reprint). Already used for the six fitted plates."),
    "lapham_1855": dict(
        ia="antiquitiesofwis00saph", region="US", year=1855,
        cite="I. A. Lapham, The Antiquities of Wisconsin, as Surveyed and Described (Smithsonian Contributions to "
             "Knowledge vol. 7), Washington 1855",
        why="Library of Congress scan, median page 2984x4301 px, fold-out plates scanned unfolded up to 5768x5906 px. "
            "Alternatives: antiquitiesofwis00laph (Pittsburgh, 2204x3125 px), smithsoniancontr71855smit (whole vol. 7, "
            "2460x3524 px, fold-outs up to 4041 px), 11215174bsb (BSB, 72 ppi metadata). IA dates this item 1853; "
            "the book is the 1855 Smithsonian edition (check title page)."),
    "thomas_1894": dict(
        ia="annualreportofbu1218901891smit", region="US", year=1894,
        cite="Cyrus Thomas, Report on the Mound Explorations of the Bureau of Ethnology, in 12th Annual Report of the "
             "Bureau of Ethnology 1890-91, Washington 1894",
        why="Smithsonian Libraries scan of the whole 12th Annual Report, 360 ppi, median page 1919x3279 px, with 7 "
            "wide and 3 tall pages (fold-out plates scanned unfolded, up to 5889x6318 px). The UC scan "
            "bureauofethnology00thomrich is 500 ppi (2690x4530 px) but has no wide pages, so its fold-outs are "
            "folded or missing; it stays the alternate for higher-resolution text figures. BPL annualreportofbu9091smit "
            "(300 ppi) and Allen County twelfthannualrep1890powe (350 ppi) are lower."),
    "fowke_1902": dict(
        ia="b24849959", region="US", year=1902,
        cite="Gerard Fowke, Archaeological History of Ohio: the Mound Builders and Later Indians, Columbus 1902",
        why="Wellcome Library scan, 500 ppi, colour, median page 2456x4075 px, one double-page spread unfolded. "
            "archologicalhist00fowkrich (UC, 500 ppi, 2444x3906) is equivalent; Cornell cu31924005690155 (1662x2517), "
            "IA archologicalhist00fowk (350 ppi) and Google/Harvard archaeologicalh00pubgoog are lower or bitonal."),
    "squier_1851": dict(
        ia="b30449492", region="US", year=1851,
        cite="E. G. Squier, Aboriginal Monuments of the State of New-York (Smithsonian Contributions to Knowledge "
             "vol. 2), Washington 1851",
        why="Wellcome Library scan, median page 3113x4653 px, the largest of the copies on IA (Cornell "
            "cu31924104075308 2385x3510; the full vol. 2 smithsoniancontr21851smit 2373x3481)."),
    "whittlesey_1850": dict(
        ia="descriptionsofan00whit", region="US", year=1850,
        cite="Charles Whittlesey, Descriptions of Ancient Works in Ohio (Smithsonian Contributions to Knowledge "
             "vol. 3, art. 7), Washington 1850 [IA dates the item 1851]",
        why="Smithsonian Libraries / BHL scan, median page 3120x4255 px; the only other copy, Cornell "
            "cu31924104077353, is 2498x3659 px."),
    "allcroft_1908": dict(
        ia="earthworkenglan01allcgoog", region="Europe", year=1908,
        cite="A. Hadrian Allcroft, Earthwork of England: Prehistoric, Roman, Saxon, Danish, Norman and Mediaeval, "
             "London 1908",
        why="Google scan of the NYPL copy, 600 ppi greyscale, median page 3367x5050 px. The Harvard Google copy "
            "earthworkenglan00allcgoog is bitonal (no grey levels: line hatching breaks up); the Toronto and UC "
            "MSN scans are 400 ppi greyscale (~2050x3300 px) and stay the fallback if a page is cropped here."),
    "mills_1914": dict(
        ia="ArcheologicalAtlasOfOhio", region="US", year=1914,
        cite="William C. Mills, Archeological Atlas of Ohio, Columbus: Ohio State Archaeological and Historical "
             "Society 1914",
        why="Added at the lead's request. The only copy on IA (advancedsearch: 1 hit). 150 ppi colour, each image a "
            "two-page opening, median 2054x1654 px: low resolution for small red symbols, but nothing better on IA. "
            "No hOCR per-page text on IA (only djvu.txt without page breaks)."),
    # The artists'-view books (verified 2026-10-11, docs/lead_artists.md, task 213; cite strings verbatim from its
    # table, markdown stripped). All six are free BookReader streams. The book-level region is coarse, as in the
    # entries above: a town's region comes from its catalog row, not the book, so each entry's cite string names
    # the volume's dominant region (European towns; the Merian volumes, the Swiss cantons).
    "civitates_liber2": dict(
        ia="civitatesorbiste00brau", region="Europe", year=1575,
        cite="Georg Braun and Frans Hogenberg, Civitates Orbis Terrarum, Liber secundus, Antwerp 1575 (Aegidius Rade) - "
             "towns of western Europe and the Mediterranean",
        why="292 leaves; the only Civitates volume already triaged (213: A 292/292, F 118/118, zero errors; its hand "
            "list is data/books/lists/civitatesorbiste00brau.json - 217 lifts it into the module). Metadata and all "
            "292 triage images cached 2026-10-11: fetch runs offline, nothing to re-download."),
    "civitates_liber4": dict(
        ia="ARes73114", region="Europe", year=1586,
        cite="Georg Braun and Frans Hogenberg, Civitates Orbis Terrarum, Tomus quartus, 1586 - towns of Europe (the "
             "dominant region; each town's region comes from its catalog row, not the book)",
        why="BookReader stream, free; metadata cached 2026-10-11 (docs/lead_artists.md). Not triaged yet - fetch, "
            "triageA/F and the hand list are the follow-on scope with 217."),
    "civitates_liber5": dict(
        ia="ARes73115", region="Europe", year=1597,
        cite="Georg Braun and Frans Hogenberg, Civitates Orbis Terrarum, Liber quintus, 1597 - towns of Europe (the "
             "dominant region; each town's region comes from its catalog row, not the book)",
        why="BookReader stream, free; metadata cached 2026-10-11 (docs/lead_artists.md). Not triaged yet - fetch, "
            "triageA/F and the hand list are the follow-on scope with 217."),
    "civitates_liber1": dict(
        ia="17095748888888bsb-00105587", region="Europe", year=1600,
        cite="Georg Braun and Frans Hogenberg, Civitates Orbis Terrarum, Liber primus, 1600 (BSB scan) - towns of "
             "Europe (the dominant region; each town's region comes from its catalog row, not the book)",
        why="Bayerische Staatsbibliothek (BSB) scan on IA, BookReader stream, free; metadata cached 2026-10-11 "
            "(docs/lead_artists.md). Not triaged yet - fetch, triageA/F and the hand list are the follow-on scope "
            "with 217."),
    "merian_helvete00zeil": dict(
        ia="topographiahelve00zeil", region="Europe", year=1654,
        cite="Matthaeus Merian and Martin Zeiller, Topographia Helvetiae, Rhaetiae et Valesiae, Frankfurt 1654 "
             "(Merianischen Erben) - the Swiss cantons",
        why="BookReader stream, free; metadata + bookreader index cached 2026-10-11 (docs/lead_artists.md). Not "
            "triaged yet - fetch, triageA/F and the hand list are the follow-on scope with 217."),
    "merian_panb665": dict(
        ia="rcin.org.pl.WA51_13719_PANB665-r1642_Topographia-Helvetia_152915", region="Europe", year=1642,
        cite="Matthaeus Merian, Topographia Helvetiae, Rhaetiae et Valesiae, 1642 (PAN Poland) - the Swiss cantons",
        why="PAN Poland's copy on IA (rcin.org.pl item), BookReader stream, free; metadata cached 2026-10-11 "
            "(docs/lead_artists.md). Not triaged yet - fetch, triageA/F and the hand list are the follow-on scope "
            "with 217."),
}


def book(key):
    return BOOKS[key]


def keys(args):
    return args or list(BOOKS)


# ---------- page images ----------

def iiif_url(page, long_side):
    q = urllib.parse.parse_qs(urllib.parse.urlparse(page["uri"]).query)
    zipname = os.path.basename(q["zip"][0])
    path = urllib.parse.quote(f"{q['id'][0]}/{zipname}/{q['file'][0]}", safe="")
    size = f"{long_side}," if page["width"] >= page["height"] else f",{long_side}"
    return f"https://iiif.archive.org/image/iiif/3/{path}/full/{size}/0/default.jpg"


NO_IIIF = {"earthworkenglan01allcgoog"}  # IIIF timed out on most of its second half (2026-10-10)


def triage_path(ia_id, n):
    return os.path.join(ia.RAW, ia_id, "triage", f"n{n:04d}.jpg")


def fetch_triage(ia_id, page):
    path = triage_path(ia_id, page["n"])
    if os.path.exists(path):
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        if ia_id in NO_IIIF:
            raise RuntimeError("IIIF times out for this item")
        body = ia.get(iiif_url(page, TRIAGE_PX), tries=2)
        im = Image.open(io.BytesIO(body))
    except Exception:  # IIIF failed: BookReader at 1/2 or 1/4, shrink locally
        k = 2 if max(page["width"], page["height"]) < 5 * TRIAGE_PX else 4
        im = Image.open(io.BytesIO(ia.get(ia.page_image_url(page, k))))
    im = im.convert("RGB")
    if max(im.size) > TRIAGE_PX * 1.05:
        im.thumbnail((TRIAGE_PX, TRIAGE_PX), Image.LANCZOS)
    tmp = f"{path}.{os.getpid()}.{threading.get_ident()}.part.jpg"  # fetcher and triage may race on a page
    im.save(tmp, "JPEG", quality=88)
    os.replace(tmp, path)
    return path


def cmd_fetch(args):
    for key in keys(args):
        ia_id = book(key)["ia"]
        ps = ia.pages(ia_id)
        todo = [p for p in ps if not os.path.exists(triage_path(ia_id, p["n"]))]
        print(f"{key} {ia_id}: {len(ps)} pages, {len(todo)} to fetch", flush=True)
        t0 = time.time()
        def safe(p):
            try:
                return fetch_triage(ia_id, p)
            except Exception as e:
                print(f"  n{p['n']} failed: {e!r:.150}", flush=True)

        with cf.ThreadPoolExecutor(2) as ex:
            for i, _ in enumerate(ex.map(safe, todo)):
                if i % 50 == 0:
                    print(f"  {i}/{len(todo)} {time.time() - t0:.0f}s", flush=True)


# ---------- Qwen triage ----------

PROMPT_A = """This is one scanned page (or fold-out) from a 19th or early 20th century book about ancient earthworks, mounds and hillforts.
Classify the page into exactly one page_type:
- "plate_site_plan": a separate plate (engraved or lithographed, usually captioned PLATE or PL. with a roman numeral, no running body text) whose main content is one or more plan views (seen from above) of an ancient work: earthwork, enclosure, fort, camp, mound group, effigy mounds, village site, or a map of a valley or district showing such works.
- "figure_site_plan": a page of body text that also carries one or more plan views of an ancient work (usually captioned "Fig." with a number).
- "other_illustration": illustrations that are not plan views of ancient works: artifacts, pottery, pipes, skulls, bones, sections or profiles drawn on their own, perspective views, landscapes, portraits, maps of a whole state or country.
- "text_only": only text, tables, title page, contents, list of plates, blank page, cover, colour chart.
Also copy every printed plate or figure number you can read on the page exactly as printed (for example "PLATE XXV", "Pl. XXI", "Fig. 20"), and the main printed title of the illustration exactly as printed (at most 20 words; "" if none). Do not guess text you cannot read.
Return {"page_type": "...", "numbers": ["..."], "caption": "..."}"""

PROMPT_A_MILLS = """This is one scanned opening (usually two facing pages) from the 1914 Archeological Atlas of Ohio.
Classify it into exactly one page_type:
- "county_site_map": a map of one Ohio county (township grid, streams, roads, towns) on which small symbols mark mounds, enclosures, village sites and burials.
- "plate_site_plan": one or more plan views (seen from above) of individual ancient works, e.g. "Ancient Works, Ross County Ohio", "Hopeton Works".
- "other_illustration": the state map, the Indian trails map, the table of symbols, photographs, other drawings.
- "text_only": text, tables, title page, blank pages.
If several apply, county_site_map wins over plate_site_plan, and plate_site_plan wins over the others.
Copy exactly as printed: the county name of a county map, the map's scale wording (e.g. "Scale, one inch equals three miles"), the titles of any plans, and any printed page numbers. Use "" when not printed.
Return {"page_type": "...", "county": "", "scale_text": "", "titles": [""], "page_numbers": [""]}"""

# Stage F: second pass, figure by figure, on pages stage A called other_illustration or figure_site_plan.
# Stage A gives one label per page and calls mixed pages (a small plan beside a view or an artifact) "other";
# listing the figures one by one recovered 6 of 8 such misses in a test on S&D and Lapham.
PROMPT_F = """List every separate drawing (figure) on this scanned book page. For each one say what it shows:
- "plan": a plan view seen from above of an ancient work, earthwork, enclosure, fort, mound or group of mounds, effigy mound outline, or a map of a site.
- "view": a perspective or landscape view, or a picture of a mound seen from the side.
- "section": a cross-section or profile.
- "object": an artifact, pipe, pot, tool, skull, ornament.
- "other": anything else (natural features, diagrams, maps of natural features).
Copy the printed figure number if any.
Return {"figures": [{"number": "Fig. 12", "shows": "plan|view|section|object|other"}]}"""

PROMPT_B = """This scanned page from an old archaeology book contains one or more plan views (maps seen from above) of ancient works (earthworks, enclosures, mounds, forts).
For EACH separate plan view on the page return an entry. Read text only as printed on the page; use "" when not printed or not legible. Never guess names or places that are not printed.
- label: the sub-number printed next to that plan, e.g. "No. 1", "Fig. 3", or ""
- title: that plan's printed title, exactly as printed
- site_names: names of the works or sites as printed
- place: county, township, state or country as printed
- scale_bar: true if that plan has a drawn scale bar
- scale_text: the printed scale wording and numbers, e.g. "Scale 200 feet to the inch" or "0 100 200 300 Feet"
- north_arrow: true if that plan has a north arrow or meridian line
- north_tip, south_end: if there is a north arrow, the point [x, y] at its NORTH end (marked by N, a fleur-de-lis, a feather or the pointed head) and the point at the opposite end of the same arrow line; null if no arrow
- map_box: [x0, y0, x1, y1] tight box around that plan's drawing only (not its title text)
Also list page-level boxes of things that would have to be blanked before tracing the walls: titles, captions, legends/keys, section or profile drawings, insets, scale bars, north arrows, blocks of body text.
All boxes and points use coordinates normalised to 0-1000 on each axis: x from the left edge (0) to the right edge (1000), y from the top (0) to the bottom (1000).
Return {"plans": [{"label": "", "title": "", "site_names": [], "place": "", "scale_bar": false, "scale_text": "", "north_arrow": false, "north_tip": null, "south_end": null, "map_box": [0, 0, 0, 0]}], "blank_boxes": [{"kind": "title|caption|legend|section|inset|scale_bar|north_arrow|text", "box": [0, 0, 0, 0]}]}"""


def repair_json(text):
    """Qwen sometimes leaves a trailing comma or a short box; strip fences/trailing commas and retry the parse."""
    import llm
    t = re.sub(r"```(?:json)?", "", text)
    t = re.sub(r",\s*([\]}])", r"\1", t)
    try:
        return llm.parse_json(t)
    except Exception:
        return None


# every port a Qwen replica has been served on: the harness VM's llmtunnel forwarder serves 8080-8082, the Mac's
# old tunnel 18080/18081 (task 215: the list named only the latter and every book stage exited "tunnels down" on
# the VM). run_stage uses whichever answer; LLM_PORTS="8080,8081" overrides.
LLM_PORTS = os.environ.get("LLM_PORTS", "8080,8081,8082,18080,18081")
LLM_URLS = [f"http://127.0.0.1:{p.strip()}/v1/chat/completions" for p in LLM_PORTS.split(",") if p.strip()]
_tl = threading.local()


def ask(prompt, img, max_tokens):
    import llm
    url = getattr(_tl, "url", LLM_URLS[0])
    out = llm.ask_json(prompt, images=[img], max_px=TRIAGE_PX, max_tokens=max_tokens, url=url)
    if "_unparsed" in out:
        fixed = repair_json(out["_unparsed"])
        if fixed is not None:
            return fixed, "repaired"
        out = llm.ask_json(prompt, images=[img], max_px=TRIAGE_PX, max_tokens=max_tokens, temperature=0.3, url=url)
        if "_unparsed" in out:
            fixed = repair_json(out["_unparsed"])
            return (fixed, "retry_repaired") if fixed is not None else (out, "unparsed")
        return out, "retry"
    return out, "ok"


def llm_up(url):
    try:
        with urllib.request.urlopen(url.replace("/chat/completions", "/models"), timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


def _jsonl(path):
    if not os.path.exists(path):
        return []
    return [json.loads(line) for line in open(path) if line.strip()]


def run_stage(key, stage, ns=None, workers=4):
    """workers = concurrent requests per live server (every LLM_URLS entry that answers /v1/models)."""
    urls = [u for u in LLM_URLS if llm_up(u)]
    if not urls:
        sys.exit(f"no LLM answers on 127.0.0.1 ports {LLM_PORTS}; not starting. (Needs a Qwen replica or tunnel.)")
    slots = [u for u in urls for _ in range(workers)]
    slot_lock = threading.Lock()
    ia_id = book(key)["ia"]
    path = os.path.join(OUT, "triage", f"{ia_id}.{stage}.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    done = {r["n"] for r in _jsonl(path) if "error" not in r}
    ps = {p["n"]: p for p in ia.pages(ia_id)}
    todo = [n for n in (ns if ns is not None else sorted(ps)) if n not in done]
    print(f"{key} {stage}: {len(todo)} pages to do ({len(done)} done)", flush=True)
    lock = threading.Lock()
    prompt = {"A": PROMPT_A, "B": PROMPT_B, "F": PROMPT_F}[stage]
    if stage == "A" and ia_id == "ArcheologicalAtlasOfOhio":
        prompt = PROMPT_A_MILLS

    def one(n):
        if not hasattr(_tl, "url"):
            with slot_lock:
                _tl.url = slots.pop() if slots else urls[0]
        img = fetch_triage(ia_id, ps[n])
        t0 = time.time()
        try:
            out, how = ask(prompt, img, {"A": 300, "F": 600, "B": 2500}[stage])
            row = {"n": n, "leaf": ps[n]["leafNum"], "out": out, "parse": how, "s": round(time.time() - t0, 1),
                   "img_size": list(Image.open(img).size)}
        except Exception as e:
            row = {"n": n, "error": repr(e)[:300]}
        with lock:
            with open(path, "a") as f:
                f.write(json.dumps(row) + "\n")
        return row

    t0 = time.time()
    with cf.ThreadPoolExecutor(workers * len(urls)) as ex:
        for i, row in enumerate(ex.map(one, todo)):
            if i % 25 == 0:
                print(f"  {i}/{len(todo)} {time.time() - t0:.0f}s last={json.dumps(row.get('out', row))[:120]}",
                      flush=True)
    return path


def latest(path):
    """Last good row per n."""
    rows = {}
    for r in _jsonl(path):
        if "error" not in r:
            rows[r["n"]] = r
    return rows


def stage_a(ia_id):
    return latest(os.path.join(OUT, "triage", f"{ia_id}.A.jsonl"))


def stage_b(ia_id):
    return latest(os.path.join(OUT, "triage", f"{ia_id}.B.jsonl"))


def stage_f(ia_id):
    return latest(os.path.join(OUT, "triage", f"{ia_id}.F.jsonl"))


def f_has_plan(row):
    figs = (row or {}).get("out", {}).get("figures") or []
    return any(isinstance(f, dict) and f.get("shows") == "plan" for f in figs)


def ink(ia_id, n):
    """Fraction of clearly dark pixels on the triage image (blank pages ~0)."""
    import numpy as np
    im = np.asarray(Image.open(triage_path(ia_id, n)).convert("L"), dtype=np.float32)
    h, w = im.shape
    core = im[int(h * .06):int(h * .94), int(w * .06):int(w * .94)]
    return float((core < np.median(core) - 50).mean())


BLANK_INK = 0.005  # below this a page is blank or only show-through (Thomas: backs of fold-outs, ink <= 0.004)

# A book whose scans show show-through darker than the default floor needs its own: Merian's fold-out backs
# read 0.0054-0.0097 (Qwen typed them plate_site_plan, one inventing a title from another book), while every
# genuine plate leaf in the item is >= 0.183. 0.01 separates the two with room to spare (217).
BLANK_INK_BOOKS = {"topographiahelve00zeil": 0.01}


def site_pages_model(ia_id):
    """{n: "qwen" | "clef"}: the model's site-plan pages. Plates from Qwen stage A; text pages with a plan figure
    from Qwen stage F where it ran, else Qwen stage A's figure_site_plan; plus Clef-flash p(plan) >= CLEF_T on
    pages Qwen typed other_illustration / left unparsed / never reached (Allcroft second half). Pages with no
    real ink are dropped: on the show-through backs of Thomas's fold-outs Qwen typed "plate_site_plan" and
    invented captions (per-book floor for the books whose show-through is darker: BLANK_INK_BOOKS)."""
    a, f, c = stage_a(ia_id), stage_f(ia_id), stage_c(ia_id)
    blank = BLANK_INK_BOOKS.get(ia_id, BLANK_INK)
    out = {}
    for n, r in c.items():
        if n in f or (n in a and a[n]["out"].get("page_type") in SITE_TYPES):
            continue
        if r["out"]["p_plan"] >= CLEF_T and ink(ia_id, n) >= blank:
            out[n] = "clef"
    for n, r in a.items():
        t = r["out"].get("page_type")
        if t in SITE_TYPES + ("other_illustration",) and ink(ia_id, n) < blank:
            continue
        if t == "plate_site_plan":
            out[n] = "qwen"
        elif t in ("figure_site_plan", "other_illustration"):
            if n in f:
                if f_has_plan(f[n]):
                    out[n] = "qwen"
            elif t == "figure_site_plan":
                out[n] = "qwen"
    return out


def site_pages_qwen(ia_id):
    return set(site_pages_model(ia_id))


# ---------- Clef-flash (fixed-option probabilities; cannot read text) ----------
# Used after the Qwen servers were withdrawn (2026-10-10, lead's instruction): on pages Qwen typed
# other_illustration or left unparsed (the job stage F did), and for every Allcroft page (Qwen got half way).
CLEF_STATE = "A scanned page from a 19th or early 20th century book about ancient earthworks, mounds and hillforts."
CLEF_Q = {
    "plan": {"type": "noul", "instructions": "Does this page show a plan view, seen from above, of an ancient work, "
             "earthwork, enclosure, camp, fort, mound or group of mounds (a site plan or site map)? Perspective "
             "views, sections, artifacts and plain text do not count."},
    "drawing": {"type": "noul", "instructions": "Does this page carry any drawing, map, engraving or photograph "
                "(not only printed text)?"},
}
CLEF_T = 0.5  # fixed in advance (probability 0.5), not tuned on the ground truth


def stage_c(ia_id):
    return latest(os.path.join(OUT, "triage", f"{ia_id}.C.jsonl"))


def run_clef(key, ns, batch=6):
    import clef
    ia_id = book(key)["ia"]
    path = os.path.join(OUT, "triage", f"{ia_id}.C.jsonl")
    done = set(stage_c(ia_id))
    ps = {p["n"]: p for p in ia.pages(ia_id)}
    todo = [n for n in ns if n not in done and os.path.exists(triage_path(ia_id, n))]
    print(f"{key} C: {len(todo)} pages to do ({len(done)} done)", flush=True)
    t0 = time.time()
    for i in range(0, len(todo), batch):  # one batch in flight
        ch = todo[i:i + batch]
        try:
            ans = clef.decide_batch([(CLEF_STATE, CLEF_Q, [triage_path(ia_id, n)]) for n in ch])
        except Exception as e:
            print("  clef error", repr(e)[:200], flush=True)
            time.sleep(10)
            continue
        with open(path, "a") as f:
            for n, a in zip(ch, ans):
                f.write(json.dumps({"n": n, "leaf": ps[n]["leafNum"], "out": {
                    "p_plan": round(float(a["plan"]["noul"]), 4), "p_drawing": round(float(a["drawing"]["noul"]), 4)}})
                        + "\n")
        if i % 60 == 0:
            print(f"  {i}/{len(todo)} {time.time() - t0:.0f}s", flush=True)


def clef_pages(key):
    ia_id = book(key)["ia"]
    a = stage_a(ia_id)
    if ia_id == "earthworkenglan01allcgoog":
        return [p["n"] for p in ia.pages(ia_id)]
    return sorted(n for n, r in a.items() if r["out"].get("page_type") in ("other_illustration", None))


def cmd_clef(args):
    for key in keys(args):
        run_clef(key, clef_pages(key))


def cmd_triage_f(args):
    for key in keys(args):
        ia_id = book(key)["ia"]
        a = stage_a(ia_id)
        ns = sorted(n for n, r in a.items() if r["out"].get("page_type") in ("figure_site_plan", "other_illustration"))
        run_stage(key, "F", ns)


SITE_TYPES = ("plate_site_plan", "figure_site_plan")


def cmd_triage_a(args):
    for key in keys(args):
        run_stage(key, "A")


def cmd_triage_b(args):
    for key in keys(args):
        ia_id = book(key)["ia"]
        ns = sorted(site_pages_qwen(ia_id) | set(extra_site_pages(key)))
        run_stage(key, "B", ns)


def extra_site_pages(key):
    """Site-plan leaves found by the OCR list mapping that stage A missed (filled in by books_lists)."""
    p = os.path.join(OUT, "lists", f"{book(key)['ia']}.map.json")
    if not os.path.exists(p):
        return []
    m = json.load(open(p))
    return [e["n"] for e in m if e.get("site_plan") and e.get("n") is not None]


# ---------- box drawing (convention check) ----------

def to_px(box, size, conv="norm1000"):
    w, h = size
    x0, y0, x1, y1 = box
    if conv == "norm1000":
        return [x0 * w / 1000, y0 * h / 1000, x1 * w / 1000, y1 * h / 1000]
    return [x0, y0, x1, y1]


def draw(ia_id, n, row, conv="norm1000", out_dir=None):
    im = Image.open(triage_path(ia_id, n)).convert("RGB")
    d = ImageDraw.Draw(im)
    out = row["out"]
    for p in out.get("plans", []):
        if p.get("map_box") and len(p["map_box"]) == 4:
            d.rectangle(to_px(p["map_box"], im.size, conv), outline=(220, 0, 0), width=5)
            x0, y0 = to_px(p["map_box"], im.size, conv)[:2]
            d.text((x0 + 6, y0 + 4), (p.get("label") or "plan")[:20], fill=(220, 0, 0))
    for bb in out.get("blank_boxes", []):
        if bb.get("box") and len(bb["box"]) == 4:
            d.rectangle(to_px(bb["box"], im.size, conv), outline=(0, 90, 220), width=3)
            x0, y0 = to_px(bb["box"], im.size, conv)[:2]
            d.text((x0 + 4, y0 + 2), bb.get("kind", "")[:12], fill=(0, 90, 220))
    out_dir = out_dir or os.path.join(OUT, "checks")
    os.makedirs(out_dir, exist_ok=True)
    im.thumbnail((900, 900))
    p = os.path.join(out_dir, f"{ia_id}_n{n:04d}_{conv}.jpg")
    im.save(p, "JPEG", quality=70)
    return p


def cmd_draw(args):
    key, ns = args[0], [int(x) for x in args[1:]]
    ia_id = book(key)["ia"]
    b = stage_b(ia_id)
    for n in ns:
        print(draw(ia_id, n, b[n]))


# ---------- full-resolution site-plan pages ----------

def cmd_full(args):
    rows = _jsonl(os.path.join(OUT, "index.jsonl"))
    for key in keys(args):
        ia_id = book(key)["ia"]
        ns = sorted({r["leaf_n"] for r in rows if r["ia_id"] == ia_id})
        ps = ia.pages(ia_id)
        d = os.path.join(ia.RAW, ia_id, "full")
        os.makedirs(d, exist_ok=True)
        todo = [n for n in ns if not os.path.exists(os.path.join(d, f"n{n:04d}.jpg"))]
        print(f"{key}: {len(ns)} site-plan pages, {len(todo)} to download", flush=True)

        def one(n):
            try:
                return _one(n)
            except Exception as e:  # keep going; a rerun picks up what failed
                print(f"  n{n}: FAILED {e}", flush=True)
                return None

        def _one(n):
            body = ia.get(ia.page_image_url(ps[n], 1), timeout=300)
            Image.open(io.BytesIO(body)).verify()
            p = os.path.join(d, f"n{n:04d}.jpg")
            with open(p + ".part", "wb") as f:
                f.write(body)
            os.replace(p + ".part", p)
            return n

        with cf.ThreadPoolExecutor(2) as ex:
            for i, n in enumerate(ex.map(one, todo)):
                if i % 20 == 0:
                    print(f"  {i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd in ("validate", "index", "ocrmap"):
        import books_lists
        getattr(books_lists, "cmd_" + cmd)(rest)
    elif cmd == "match":
        import books_match
        books_match.main(rest)
    else:
        {"fetch": cmd_fetch, "clef": cmd_clef, "triageA": cmd_triage_a, "triageB": cmd_triage_b, "triageF": cmd_triage_f, "draw": cmd_draw,
         "full": cmd_full}[cmd](rest)
