Status: open
# 210: Numancia - the excavation plans of the 1860s
Depends on: 200
Touches: fit/src_numancia.py, data/catalog/extras_numancia.jsonl, data/commons/files_numancia.jsonl, data/commons/classified_numancia.jsonl, data/raw/commons/numancia/, docs/lead_numancia.md, tests/test_src_numancia.py, tests/golden/

## Goal
GOAL.md point 4: Numancia (the Roman city in Spain, already a built site on the map) gets
its excavation plans of the 1860s. The lead is unverified: find where the plans live (the
1860s-70s excavation reports - the excavations ran under Juan de Dios Villanueva - a book
on Internet Archive, a Spanish archive, or Commons), check that it is old enough, free and
machine-readable, and stage the rows tied to the site. If no free machine-readable copy
exists, document the search and drop the lead.

## Acceptance criteria
- [x] The source of the 1860s plans is verified and recorded in docs/lead_numancia.md
      (where it is, its date, its freedom/license, how the pages are machine-readable) - or
      the lead is dropped, the file says exactly what was searched (sources, dates,
      paywalls, format problems) and why nothing qualified, and this task ends
      `Status: dropped`.
- [ ] If verified: staged rows - files_numancia.jsonl for every staged plan tied to the
      existing Numancia site (the identification is part of the verification: the plans
      must depict Numancia, and the row records the specific check) with the 200 evidence
      field and a classified row by hand ("plan"); the plan's date (1860s) recorded on the
      row. extras_numancia.jsonl only if the reports show other sites not in the catalog
      yet.
- [ ] fit/evidence.py check passes offline on every staged row; test (no network): the
      staged files join and the evidence check passes, with a golden sample of rows. If
      the lead was dropped, the test asserts the documentation exists and the staging
      files are absent or empty.

## Notes
- Numancia's excavation plans are the rare case where the drawing is younger than 150
  years would be (1860s = just about old enough) - the age is recorded on the row either
  way; plans of the structure are exempt from the 150-year rule (PLAN.md assumption 4).
- The site is already built with (or without) a drawing: this task adds candidate
  pictures, it does not fit them - the batch/cover loop does.

## Hand-over
(iteration 128, agent c - session 3: **plate EYE-CONFIRMED, license recorded, docs/lead_numancia.md WRITTEN (box 1 ticked)**. No code written yet. Next session = stage + `fit/src_numancia.py` + test.)

**What session 3 established (all re-downloadable; details in docs/lead_numancia.md):**
1. **IA `memoriasdelareal009real` PDF (37.7 MB) downloaded OK this session** (last session's /download/ 500s were transient; `curl -sL -A <UA>`). 766 PDF pages = 766 leaves, 1:1. /tmp/num/ still holds: m009.pdf, memoriasdelareal009real_djvu.txt, m009.json (metadata + page_numbers inline), item.html, all the montages/renders from this and last session.
2. **LÁMINA IV = PDF leaf 507** (eye-confirmed at 400 dpi: /tmp/num/l4_507-507.jpg, 8950x3612 landscape; l4_top/l4_bot = its halves). Figures as printed: 1 sepulcros Calatañazor · 2 Portada de los Mártires de Garray · 3 Muro de Numancia (Alzado 5/Corte 4) · **5 "Plano de las excavaciones hechas en Numancia en 1855."** · 7 Plano de las murallas de Augustóbriga · 8 Alzado de un trozo de muralla de Augustóbriga; scales 1/300, 1/300, 1/1000; lith. J. Domm. Madrid. The **plate caption says 1855, the printed ÍNDICE DE LAS LÁMINAS (leaf 497) says "en el sitio de Numancia en 1853"** — the discrepancy is inside the volume; both = Saavedra's 1853 site-finding campaign. **Fig. 5 is a genuine excavation plan**: hatched excavation area on the hill slope, excavated room-structure with rubble field, dashed survey grid, section line A-B + "Corte por A B", boxed "Monumento hallado".
3. **Full leaf map of the work's end (block 490-514)** (lead doc §2): 490-493 pp. 110-113 (catálogos) · 494-497 blank/índices/ÍNDICE DE LAS LÁMINAS · 498-499 blank/ERRATAS · 500-501 LÁM. I road map "PLANO DE LA VIA ROMANA DE VXAMA á AVGVSTOBRIGA" (2 leaves) + verso · 503 LÁM. II puentes · 505 LÁM. III secciones+inscripciones · **507 LÁM. IV** · 508 verso (blank — **LÁMINA V (pottery) leaf is ABSENT from this scan**; 509 is the next memoir's title) · 509-511 truces title+ADVERTENCIA · 512-514 truces pp. 4-6. The work STARTS at leaf 378 (front matter: índice, half-title "POR D. EDUARDO SAAVEDRA", title "MEMORIA DESCRIPTIVA. INTRODUCCION.").
4. **LÁM. I (the big map) is NOT staged**: it is a road map of the whole route, not an excavation plan; recorded in the lead doc with its leaf numbers (one row per plan).
5. **License (recorded exactly in lead doc §1):** item metadata has NO license/licenseurl field (verified via /metadata/ and the item page); the work is of 1879 (USA public domain, pre-1929) and the author died ~1902 (EU public domain too); BPL 2012 scan; collections bostonpubliclibrary+americana; ARK ark:/13960/t00z8794b. Treated as PDM-equivalent.
6. **Per-leaf direct image URLs do NOT exist for this item**: /download/memoriasdelareal009real_0507.jpg and .jp2 → 404 (zip-only Google scan; BookReaderImages.php and /composite/ 404, confirmed again). **→ the row's image is rendered locally from the PDF** (`pdftoppm` of leaf 507) into `data/raw/commons/numancia/<sha1(title)[:16]>.jpg` — that path was ADDED to the task's Touches this session (plus `tests/golden/` for the golden files). The page uses the local copy as is (prep R3).

**NEXT STEP (session 4) — in this exact order:**
1. Re-read (fresh eyes): `fit/src_van_deventer.py` (the module pattern: REPORTS/PLANS tables, sweep/stage/check_staged/golden, idempotent (site,title) append) · `data/commons/files_van_deventer.jsonl` (exact row shape incl. date/license/thumb conventions for a non-Commons row) · `fit/evidence.py` (`check_caption` rules + `hav_m` + the `check` CLI arg names) · `pipeline/commons.py` `thumbs()` (the EXACT sha1 input and path for the local image, and that an existing local file is never refetched) · `data/catalog/extras.jsonl` line 31 (the numancia site row: lon -2.4443, lat 41.8096).
2. Render the plate image: /tmp/num/m009.pdf (or re-download) → `pdftoppm -jpeg -r 300 -f 507 -l 507` → copy to `data/raw/commons/numancia/<sha1(title)[:16]>.jpg` per the exact rule from thumbs(); record w/h/mime from the rendered file on the row.
3. Stage: ONE file row (site numancia, qid Q623407, title = the plate caption naming Numancia, e.g. "Plano de las excavaciones hechas en el sitio de Numancia (Lám. IV fig. 5, Saavedra 1879; excavations of 1853/1855)" — must contain "Numancia"; url = IA item page; date 1879 with the excavation year in desc; by "fit/src_numancia.py"; name = the plan-list label; license per lead §1; thumb = the IA PDF download URL or per whatever thumbs() expects when a local copy exists — follow the van Deventer row) + ONE classified row {site, same title, p_plan 1.0, p_birdseye 0.0, p_photo 0.0, by "hand"} + evidence **caption_coords** (named_place "Numancia", place_qid Q623407, place_label "Numantia, ancient city and archaeological site", place_lon/lat 41.809392/-2.444447, site_lon/lat from the catalog row, dist_m via hav_m ≈ 26). `extras_numancia.jsonl` stays ABSENT (no new sites — lead §4).
4. `fit/src_numancia.py`: stdlib-only at module top, lazy `import evidence`; CLI `--sweep` (live re-verify: item up, 766 leaves, PDF GETs, the plate leaf renders non-blank), `--stage [--dry]`, `--check` (join + `evidence.check(FILES, NO_BOOKS, catalog=EXTRAS)`), `--golden` (generate tests/golden/src_numancia_evidence.txt by running the check; src_numancia_sample.json = the row(s) sorted/normalized).
5. `tests/test_src_numancia.py` (socket-blocked fixture; no fixed ports; writes only inside the project + temp): (1) join assertions (site=="numancia", (site,title) unique, qid, date on row, classified 1:1 p_plan 1.0 by hand, local image file exists at the thumbs() path); (2) subprocess `[.venv/bin/python, "fit/evidence.py", "check", "--files", "data/commons/files_numancia.jsonl", "--books", <absent>, "--catalog", "data/catalog/extras.jsonl"]` (cwd=ROOT) → rc 0, stderr empty, stdout == golden; (3) in-test synthetic negative (a far-resolving caption row) must NOT pass; (4) golden sample checked in.
6. `pytest -q` (suite state: 1-4 pre-existing unrelated failures per driver notes — test_gate, test_batch_eu, test_serve — not mine). Tick boxes 2-3, set Status: done, final hand-over.

**Re-read (bugs, fresh eyes):** `pipeline/commons.py` thumbs() — how the page fetches/skips my thumb (local copy present ⇒ no fetch; confirm the skip path doesn't 500 on a non-image thumb URL); `fit/evidence.py` check_caption() — norm(named) must appear in norm(title+" "+desc): my title carries "Numancia", desc should carry "Numantia" too (R6) so both forms are findable.

**PITFALLS (file them in session 4 - the context limit hit before I could edit PITFALLS.md):** add a `### Internet Archive (archive.org)` subsection under "This machine and its environment" with two entries: (a) /download/ needs UA + -L (no UA -> 0 bytes; HEAD without -L -> 302 CDN redirect, normal); the backend is flaky per-file (170-byte nginx 500 pages come and go per file/day - dc.xml/page_numbers.json/chocr 500'd all of session 2 while the 37.7 MB PDF succeeded on retry); zip-only Google-scan items have NO per-leaf image derivatives (<item>_NNN.jpg/.jp2 -> 404, BookReaderImages.php 404, /composite/ 404) - get per-leaf images from the PDF via pdftoppm or from the zip; /metadata/<item> returns the page_numbers dict inline when /download/page_numbers.json 500s. (b) In memoriasdelareal009real the hOCR page index / searchtext page order does NOT line up with the PDF leaf sequence (the work that starts at PDF leaf 378 has its running heads at hOCR searchtext entries ~33-38) - same class as the civitatesorbiste00brau hOCR misalignment; ground truth = the PDF (eye-check with pdftoppm) and the djvu.txt stream (matches PDF order for this item). The facts are fully recorded in docs/lead_numancia.md §1 and in the DECISIONS entry above, so nothing is lost.

**State.** Boxes: 1 ticked (lead doc written). 2, 3 open (session 4). Files changed this session: docs/lead_numancia.md (new), task file (Touches + box 1), DECISIONS, PITFALLS. NO code, NO staging files, NO data/raw yet — all still as on main.
