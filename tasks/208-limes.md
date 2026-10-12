Status: open
# 208: The German Limes - fort plans from the old reports
Depends on: 200
Touches: fit/src_limes.py, data/catalog/extras_limes.jsonl, data/commons/files_limes.jsonl, data/commons/classified_limes.jsonl, docs/lead_limes.md, tests/test_src_limes.py

## Goal
GOAL.md point 4, the least certain of the seven leads: fort plans from the German Limes
reports (ORL and its successors; the forts of the Upper and Lower Germanic Limes are a
natural growth area - many are not in the catalog yet). Verify first whether free,
machine-readable fort plans exist (old government reports are public domain, but the scans
must actually be available: a library site, an archive, Internet Archive, or Commons). If
yes: stage the plans tied to their forts. If no: document exactly what was searched and
drop the lead - the other six leads stand on their own (PLAN.md assumption 7).

## Acceptance criteria
- [ ] docs/lead_limes.md records the verification either way: what sources were checked
      (names, URLs, dates), what is free and machine-readable, and the decision (proceed /
      drop). A dropped lead ends this task with `Status: dropped`, the documentation
      committed, and no staging files.
- [ ] If proceeding: staged rows - files_limes.jsonl for every staged fort plan (with the
      200 evidence field: the report's list/caption names the fort; coordinates from the
      report cross-checked where possible) and extras_limes.jsonl for forts not in the
      catalog (QID from Wikidata where it exists, kind "roman fort", lon/lat from the
      report); a classified row by hand per picture; the plan's date recorded on the row
      (the 150-year rule: fort plans of structures are exempt, recorded anyway).
- [ ] At least 10 fort plans staged from at least 2 sources, or the documentation accounts
      for every missing one with a reason (a verified drop beats a guessed row).
- [ ] fit/evidence.py check passes offline on every staged row; test (no network): the
      staged files join and the evidence check passes, with a golden sample. If the lead
      was dropped, the test asserts the documentation exists and the staging files are
      absent or empty.

## Notes
- If the reports turn out to be Internet Archive books indexable with pipeline/books.py,
  work in per-book files only (triage/<ia>.*, lists/<book>.json) and add those exact paths
  to this task's Touches line before writing them - never the shared index.jsonl or
  validation.json (211 rebuilds both).
- The forts' QIDs are patchy on Wikidata: name+coordinates from the report is an acceptable
  tie when no QID exists, recorded as such on the row (the evidence kind says so).

## Hand-over

(2026-10-12, iteration 159, agent a — session 2 of 208. **docs/lead_limes.md is WRITTEN (box 1 done, provisional PROCEED decision)** — it was uncommitted at the context cut; the harness saved it, so the next session: `git status` first, keep it, and commit it with the next step. No tests run this session (doc-only step); last suite state = the driver's 2026-10-11 loop-start notes (all failures in OTHER tasks' tests: test_gate, test_batch_eu, test_serve — not mine). Session 3 = the paced Commons leg, then the build.)

### What session 2 established (all 2026-10-12, from the cached files + the local PDF)

**1. The lead doc (this session's step).** `docs/lead_limes.md`: §1 the 9-row verification-sweep table (source 1 = IA 1895 ORL vol = PROCEED; IA supply exhausted; Limesblatt text-only; de.wiki ORL set = source 2; Commons twins = the gated leg; 4 blocked/DNS-less hosts recorded); §2 the 1895 volume plate inventory, CORRECTED (see 2); §3 the de.wiki/Commons census (874 files; 824 "tab" plates; **165 "Grundriss"/"Grundrisse" named, every one with long edge >= 1000 px**; 55 fort tokens = 42 two-digit + 11 sub + 2 one-digit strays merged into 04/07; 46 forts with >= 1 Grundriss; 4 non-fort files incl. 2 stageable KK Anhausen plates 2819x2823 / 3111x3130 and one unrelated ORLEN-Lietuva logo); §4 decision = **PROCEED (provisional)** — final once the Commons leg verifies >= 10 stageable Commons twins from >= 2 ORL volumes, else documented drop — plus the full staging plan (row shapes, evidence kinds, check_staged, test, golden).

**2. PLATE-ORDER CORRECTION (the session's main finding).** Session 1's leaf-to-Tafel mapping was off by one plate and both scales were misread at 40 dpi. True order (djvu 1-based = BookReader n + 1; plate leaves are the ODD djvu pages 51-63, versos blank): **Tafel I = p51/n50** (2 photos); **Tafel II = p53/n52** (excavation photo + "Fig. 2 Mithrasrelief" photo); **Tafel III = p55/n54 = the Situationskarte, MAASSTAB 1:5000** (NOT 1:3000); **Tafel IV = p57/n56 = THE fort plan (Grundriss), MAASSTAB 1:1000** (NOT ~1:500): both fort lines (main fort + smaller Anbau), lettered gates, excavated buildings 1-18, legend (Reichsgrabungen wall states), "Aufg. von Lehramtspraktikant H. Leutz und Prof. K. Schumacher, gez. von A. Ebertz, Trier", footer "OBERGERM. - RÄET. LIMES B.". **Tafel IV is a landscape plate rotated 90° in the scanned leaf (its top edge is the page's RIGHT edge; rotate the page image CLOCKWISE to get it upright) — the staging step must record this rotation.** Tafel V = p59/n58 bronze finds; VI = p61/n60 iron; VII = p63/n62 iron; p64 blank. So source 1 = 2 stageable drawings of ONE fort (Osterburken): page n54 (1:5000) + page n56 (1:1000). Title page (djvu p5, OCR): "LIEFERUNG II. ENTHALT: AUS BAND IV, ABTEILUNG B, Nr. 40 KASTELL OSTERBURKEN. HEIDELBERG VERLAG VON OTTO PETTERS 1895" (editors Sarwey + Hettner); the monograph (Petters) is built on the Mannheimer Plan (1867 Mannheimer-Verein excavation, original in Mannheim) + the Reichsgrabungen of 19 Aug 1892-1894.

**3. The evidence contract, verified against fit/evidence.py this session:** `check_caption(row, ev)` (L190) needs ev: named_place (must be a norm-substring of title+" "+desc), place_qid/label/lon/lat, site_lon/lat, dist_m (reproduces hav_m(site, place) within 1000 m; distance <= DIST_TOL_M = 50 km, L70). Kind `category` (L155): the row carries `cat` (the P373 category name); ev needs site_cat == cat and file_cat, either equal or joined by a `via` chain whose last element is cat. `check(files, books, catalog)` (L322) silently skips nonexistent paths — the NO_BOOKS = data/books/.no-books trick (never created) skips the book leg, as src_artists.check_staged does. `catalog_map(catalog)` merges the given catalog file + data/catalog/extras.jsonl by id and qid. Row shapes confirmed (from files.jsonl L1479+, extras.jsonl L67+, classified.jsonl): file row = site, qid, title, year, wd_plan, cat, name, by, url, thumb, w, h, mime, date, desc, artist, license, page, date_commons, evidence; extras row = id, qid, name, lon, lat, region, kind, aerial_ok, source, place, wikipedia; classified = {site, title, p_plan, p_birdseye, p_photo, by:"hand"}.

**4. Pitfalls still to file** (session 1's 6 + session 2's 1; grep PITFALLS.md first — none of them is there yet): (1) portal.dnb.de = Anubis/Techaro JS proof-of-work wall (SRU 404, simpleSearch returns the honeypot, any UA); (2) limesblatt.uni-hd.de unreachable (TCP connect fails http+https; DNS 129.206.119.232); (3) www.deutschedigitalebibliothek.de and digital.ub.uni-heidelberg.de have no DNS on this VM; (4) Google-book djvu XML: each page is `<OBJECT ... usemap="<id>_NNNN.djvu">` — the page number lives in the **usemap** attribute, NOT the data attr (data holds the bare djvu name; a regex on `data="..._NNNN.djvu"` matches nothing); per-leaf OCR = the WORDs inside that OBJECT; (5) de.wikipedia `list=allimages` paginates via the continue key **aicontinue** (aifrom/aipfrom do not advance); (6) never read plate legends/scales off 40 dpi renders (session 1 misread both Tafel scales exactly that way); (7) this VM's clock printed 2026-10-12, consistent with the journal dates.

### Exact next steps (session 3: the Commons leg, ONE paced run, then the build)

1. **Commons leg (R7 pacing via `commons.get`, ~2 s between calls, keep it to ONE run):** for the candidate Grundriss files (the per-fort list is in docs/lead_limes.md §3; start with 01, 03, 05/05.10, 08, 12, 14, 15, 33, 34, 39-42, 44-49, 50-53, 56-60, 63-65, 67, 72 + the two KK Anhausen files), find the SPACE-named Commons twin (`ORL <nr> tab <n> pic <m> <content>.jpg`) and take `commons.info()`: size (>= 1000 px long edge), license (must be free), date (the Commons DateTimeOriginal — pitfall: not always the original's date), categories, and whether the file sits in the fort's P373 category (or a recorded subcat chain). Write each result to a scratch file as you go (a 429 window must not lose work). **Gate:** >= 10 stageable files from >= 2 distinct ORL volumes (source 1 is Band IV Abt B; any other volume counts as the second) → PROCEED final; else documented drop (the doc's §1 already satisfies box 1 for a drop; set Status: dropped, test per the 209c pattern).
2. **QIDs:** per chosen fort via de.wiki pageprops (paced) or Wikidata; Saalburg Q542329 and Eining Q1735352 are known to exist, all others verify per fort; no-QID forts stage on name + report coordinates, recorded as such.
3. **Build:** `fit/src_limes.py` mirroring `fit/src_artists.py` (SOURCES + hand-checked FORTS tables; `stage()` writing the 3 staging files, append-only, idempotent on (site,title), by="fit/src_limes.py", row date = the plate/volume date; `check_staged()` = the offline join + `evidence.check(FILES_LIMES, NO_BOOKS, catalog=EXTRAS_LIMES)`; `golden()`). Evidence: a Commons twin inside the fort's P373 category → kind `category`; everything else (incl. the two IA 1895 rows, url = `https://archive.org/download/derobergermanis00fabrgoog/page/n{54,56}.jpg`, the n56 row's desc records the CW rotation) → kind `caption_coords`. The 1895 rows' title/desc MUST contain "Osterburken" (check_caption norm-substring); the place = the fort/town with its coordinates, dist_m to the site. `tests/test_src_limes.py` = the src_artists pattern (no_network socket-blocking fixture, join, check, built-in negative control, golden sample). **Before writing the golden file, add `tests/golden/src_limes_sample.json` to this task's Touches line** (the only path beyond the current six; the staging session may also need the per-fort scratch notes — keep them in data/raw or /tmp, never in git).

### Environment

- /tmp/agent-a-208/: orl_dewiki.json (the cached 874-entry de.wiki list), orl_census.json (this session's per-fort census), recheck/ (70 dpi top/bottom bands of PDF pages 49-64 + p57 rotated CW/CCW), orl/ (session 1's 40 dpi renders — untrustworthy for legends), dnb_limesblatt.html. /tmp may be wiped between sessions; the de.wiki list refetches in 4 aicontinue calls, the book is in data/raw/books/derobergermanis00fabrgoog/ (PDF, _djvu.xml, _djvu.txt, page_n54.jpg, page_n56.jpg full-res).
- .venv has pillow (crops/rotation); pdftoppm installed; Wikimedia 429s after ~12-20 rapid calls — pace via commons.get (Retry-After-aware), one run.
- 200 is merged (fit/evidence.py in main, 850 lines); nothing else in flight is a dependency. 211 merges the staging files when this task is done.
