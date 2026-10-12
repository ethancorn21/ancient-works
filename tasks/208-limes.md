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

### Session 3 (2026-10-12, iteration 160) — the Commons leg, FINDINGS + remaining steps

**The Commons leg ran; it changed the plan.** The lead doc's assumption ("the same plates exist on
Commons with space naming") is FALSE for the plate set. Findings (all verified live, 2026-10-12):

1. **Commons vs de.wiki are DISJOINT ORL sets.** Commons `list=allimages&aiprefix=ORL` = 262 files
   (1 page; the rest is ORLANDO/ORLA/ORLEY air-cargo noise). ~103 are ORL-ish: ~85 modern photos
   (`ORL<NR>_Kastellbad/Infopavillon/Lageplan.png/Ziegelstempel/Inschrift...` — NOT stageable) and
   ~15 genuine plates: `ORL_01_tab_01_pic_01_Lageplan`, `ORL_01_tab_02_pic_01_Grundriss`,
   `ORL_12_tab_02_pic_01_Grundriss_und_Profile`, `ORL_33_tab_02/03/04/05/06/16_*`,
   `ORL_56_tab_03_*Metallfunde`, `ORL_A_01_tab_09`, `ORL_A_04_tab_07/10`, `ORL_A_05_tab_14`,
   `ORL_B_2_3b_Taf_1/2/9_Kastell_Wiesbaden`. The de.wiki 874-file set (165 Grundrisse, 46 forts)
   has ZERO name overlap with Commons (checked both directions, normalized). The session-2 search
   hit "ORL 12 tab 02 pic 01 Grundriss und Profile.jpg" IS the underscore-named Commons file
   (MediaWiki search displays underscores as spaces; `aiprefix="ORL 12"` matches
   `ORL_12_tab_02_pic_01_Grundriss_und_Profile.jpg` — verified).
2. **Revised staging route:** stage the DE.WIKI files (free: all verified PD-alt-100 / Bild-PD-alt;
   machine-readable at upload.wikimedia.org/wikipedia/de/; names + descriptions carry the fort tie)
   with **kind `caption_coords`**; the few Commons plates ride `caption_coords` too UNLESS one sits
   in its fort's P373 category (then `category` — the direct-membership check ran in run B2;
   subcat chains can be walked later). The lead doc §4 must be updated to this reality (the gate
   itself is UNCHANGED and PASSES: 45/48 picks verified free+>=1000px+named, across Abt B Bands
   1-7 + Abt A + source 1's Band 4 → >= 10 plans from >= 2 sources under any reading).
3. **de.wiki API quirk:** `titles=File:X` normalizes to `Datei:ORL 40 tab 04 pic 01 Grundriss.jpg`
   (German ns prefix + SPACES) — the returned pages dict is keyed by that, so look up by
   normalized name (strip prefix, space<->underscore, lower), not "File:"+underscore name.
4. **05.10 is NOT a fort number** — it's Abt A Limes-section material (104 files: Wp watchtower
   drawings + KK Robern/Trienz/Seitzenbuche/Zwing fortlets). Exclude from the fort-plan set; record
   as a growth area. **The pick heuristic in leg_b_meta.py had Abt A FIRST (inverted)** — for 01, 02,
   03, 04, 05, 07, 08, 14, 15, 05.10 it picked Wp/watchtower/fortlet files (Limes drawings, not fort
   plans) instead of the Abt B Hauptkastell Grundrisse that also exist for those numbers
   (e.g. 01 has `ORL_01_tab_03_pic_01_Grundriss_Kastellbad.jpg`; 05 has Abt B files; 14 = Butzbach,
   15 = Grüningen have Abt B Grundrisse). **Re-pick with Abt B first, and drop names containing
   `_wp`/`Wp`/`Wachturm` from the primary set** (the Wp files may be a later growth area).
   Fort-number semantics: 42 = Oehringen (Rendelkastell + Bürgkastell), 45/45a = Welzheim
   (West/Ost), 53/53.1 = Neckarburken (West/Ost), 54/55 = Wimpfen (no Grundriss file), 19 =
   Ober-Florstadt (1 file, 0 Grundriss — skip unless it is a Lageplan), 69 = Dambach (726 px —
   too small, skip), 02a = Niederberg Principia (part of a fort — borderline, keep out of the
   primary count unless needed). 40 (Osterburken) stages from the IA 1895 volume (source 1); the
   de.wiki twin `ORL_40_tab_04_pic_01_Grundriss.jpg` (3466x2838) is the same plate — note it in the
   doc, don't double-count it.
5. **QID search bug (fixed in leg_b2_qids.py):** `wbsearchentities` returns `description` as a
   STRING (with language=de), not a dict — leg_b_meta.py crashed on that after ~11 of ~28 searches
   (qid_search.json has the partial results; B2 reuses it). Run B2 ALSO does the batch
   wbgetentities (P625/P373/P131/labels/dewiki) and the Commons-P373-direct-membership check,
   printing the fact sheet for the hand check.

**Exact next steps (session 4):**
1. If /tmp survived: `.venv/bin/python /tmp/agent-a-208/leg_b2_qids.py` (paced, idempotent, ~2 min).
   If /tmp was wiped: re-run in order leg_a_list.py, leg_b_meta.py, leg_b2_qids.py (all idempotent;
   leg_a re-fetches article + Commons list, leg_b re-fetches the 103+48 fileinfos).
2. Read the printed QID fact sheet; record the chosen QID per fort (or "no QID, name+coords") in
   THIS hand-over — it becomes the FORTS table of fit/src_limes.py. Cross-check P625 against the
   fort's location (>50 km = the R6 trap); note which forts have NO QID. P373 values go to the
   `category`-evidence decision for the ~15 Commons plates (commons_p373_hits.json).
3. Re-pick the primary set (Abt B first, no Wp names) → ~25-35 final staging files; confirm each
   pick's desc names its fort (the printed de.wiki desc already does, verified in dewiki_meta.json).
4. Update docs/lead_limes.md: §3 add the Commons-leg result (disjoint sets, the ~15 Commons plates
   listed, the route change to de.wiki caption+coords), §4 flip the decision to **PROCEED (final)**
   with the counts; commit.
5. **Build** `fit/src_limes.py` mirroring `fit/src_artists.py`: SOURCES (source 1 = IA 1895 volume
   Band IV; source 2 = de.wiki ORL set; source 3 = Commons ORL set), FORTS table (nr, band, name,
   year, qid-or-None, lon/lat, files), `stage()` (3 staging files, idempotent on (site,title),
   by="fit/src_limes.py", row date = monograph year from the Band table), `check_staged()` =
   offline join + `evidence.check(FILES_LIMES, NO_BOOKS, catalog=EXTRAS_LIMES)`, `golden()`.
   Evidence: `caption_coords` for everything (named_place = the fort name as printed — the de.wiki
   desc text carries it; place = the fort, coords from P625/report; the 1895 rows: url
   `https://archive.org/download/derobergermanis00fabrgoog/page/n{54,56}.jpg`, n56 = CW-rotated
   landscape plate, title/desc MUST contain "Osterburken"); `category` only for a Commons plate in
   its fort's P373 category (site_cat=file_cat or a recorded via chain). **Before writing the golden
   file, add `tests/golden/src_limes_sample.json` to this task's Touches line.**
6. `tests/test_src_limes.py` = the src_artists pattern: no_network socket-blocking fixture, join of
   the 3 staging files, `check_staged()`, built-in negative control (caption names the wrong fort /
   coords 10 km off — reported, never written), golden sample; assert box 3 from the staged rows
   (>= 10 plans, >= 2 distinct volumes/bands, every row's date recorded). Then tick the boxes.

### Environment (unchanged from before, still true 2026-10-12)

- /tmp/agent-a-208/: orl_dewiki.json (cached 874-entry de.wiki list), orl_census.json (per-fort
  census), recheck/ (70 dpi bands), orl/ (40 dpi — untrustworthy), dnb_limesblatt.html, and
  **commons_leg/** (this session: orl_article_wikitext.json [the Band table lives in its "Abteilung
  B" list, lines 31-38], commons_orl_list.json [262], candidates.json [48 picks + all_grund per
  fort], commons_genuine.json [103 names], commons_meta.json, dewiki_meta.json [48, keys are
  `Datei:...` SPACE names — normalize before lookup], qid_search.json [partial, ~11 names],
  bands.json [Band->nr->(name,year) table], leg_a_list.py / leg_b_meta.py / leg_b2_qids.py [the
  scripts; all idempotent, run under .venv/bin/python]). /tmp may be wiped; the de.wiki list
  refetches in 4 aicontinue calls if needed, the book is in data/raw/books/derobergermanis00fabrgoog/.
- .venv has pillow; pdftoppm installed; Wikimedia 429s after rapid bursts — every script paces at
  2 s via commons.get (Retry-After aware) and saves incrementally.
- 200 is merged (fit/evidence.py in main); the evidence contract was re-read this session:
  `check_category` (L155) needs row.cat + ev.site_cat==cat + ev.file_cat (==cat or via-chain ending
  at cat); `check_caption` (L190) needs ev.named_place (norm-substring of title+" "+desc),
  place/site lon/lat, dist_m reproducing hav_m within 1000 m and <= 50 km; `check(files, books,
  catalog)` skips a nonexistent books path (NO_BOOKS = data/books/.no-books, never created) and
  catalog_map merges the given catalog file + data/catalog/extras.jsonl by id and qid.
- 211 merges the staging files when this task is done.
