Status: open
# 208: The German Limes - fort plans from the old reports
Depends on: 200
Touches: fit/src_limes.py, data/catalog/extras_limes.jsonl, data/commons/files_limes.jsonl, data/commons/classified_limes.jsonl, docs/lead_limes.md, tests/test_src_limes.py, tests/golden/src_limes_sample.json

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

(2026-10-12, iteration 161, agent a — session 4 of 208. **The QID phase is DONE and the staging set is DECIDED: 56 files** (45 de.wiki + 9 Commons + 2 IA-1895) across ~46 sites. All session-4 data is on disk in /tmp/agent-a-208/commons_leg/ (final_picks.json, qid_search.json, qid_entities.json, qid_routes.json, commons_p373_hits.json, dewiki_meta.json + dewiki_meta2.json, bands.json). No repo files changed this session; docs/lead_limes.md is committed as of a85e414 (session 3). No tests run (data-gathering step); last suite state = the driver's 2026-10-11 loop-start notes (failures all in OTHER tasks' tests). NEXT = session 5: the cross-check leg, then the lead doc, then build fit/src_limes.py + test.)

### What session 2 established (all 2026-10-12, from the cached files + the local PDF)

**1. The lead doc (this session's step).** `docs/lead_limes.md`: §1 the 9-row verification-sweep table (source 1 = IA 1895 ORL vol = PROCEED; IA supply exhausted; Limesblatt text-only; de.wiki ORL set = source 2; Commons twins = the gated leg; 4 blocked/DNS-less hosts recorded); §2 the 1895 volume plate inventory, CORRECTED (see 2); §3 the de.wiki/Commons census (874 files; 824 "tab" plates; **165 "Grundriss"/"Grundrisse" named, every one with long edge >= 1000 px**; 55 fort tokens = 42 two-digit + 11 sub + 2 one-digit strays merged into 04/07; 46 forts with >= 1 Grundriss; 4 non-fort files incl. 2 stageable KK Anhausen plates 2819x2823 / 3111x3130 and one unrelated ORLEN-Lietuva logo); §4 decision = **PROCEED (provisional)** — final once the Commons leg verifies >= 10 stageable Commons twins from >= 2 ORL volumes, else documented drop — plus the full staging plan (row shapes, evidence kinds, check_staged, test, golden).

**2. PLATE-ORDER CORRECTION (the session's main finding).** Session 1's leaf-to-Tafel mapping was off by one plate and both scales were misread at 40 dpi. True order (djvu 1-based = BookReader n + 1; plate leaves are the ODD djvu pages 51-63, versos blank): **Tafel I = p51/n50** (2 photos); **Tafel II = p53/n52** (excavation photo + "Fig. 2 Mithrasrelief" photo); **Tafel III = p55/n54 = the Situationskarte, MAASSTAB 1:5000** (NOT 1:3000); **Tafel IV = p57/n56 = THE fort plan (Grundriss), MAASSTAB 1:1000** (NOT ~1:500): both fort lines (main fort + smaller Anbau), lettered gates, excavated buildings 1-18, legend (Reichsgrabungen wall states), "Aufg. von Lehramtspraktikant H. Leutz und Prof. K. Schumacher, gez. von A. Ebertz, Trier", footer "OBERGERM. - RÄET. LIMES B.". **Tafel IV is a landscape plate rotated 90° in the scanned leaf (its top edge is the page's RIGHT edge; rotate the page image CLOCKWISE to get it upright) — the staging step must record this rotation.** Tafel V = p59/n58 bronze finds; VI = p61/n60 iron; VII = p63/n62 iron; p64 blank. So source 1 = 2 stageable drawings of ONE fort (Osterburken): page n54 (1:5000) + page n56 (1:1000). Title page (djvu p5, OCR): "LIEFERUNG II. ENTHALT: AUS BAND IV, ABTEILUNG B, Nr. 40 KASTELL OSTERBURKEN. HEIDELBERG VERLAG VON OTTO PETTERS 1895" (editors Sarwey + Hettner); the monograph (Petters) is built on the Mannheimer Plan (1867 Mannheimer-Verein excavation, original in Mannheim) + the Reichsgrabungen of 19 Aug 1892-1894.

**3. The evidence contract, verified against fit/evidence.py this session:** `check_caption(row, ev)` (L190) needs ev: named_place (must be a norm-substring of title+" "+desc), place_qid/label/lon/lat, site_lon/lat, dist_m (reproduces hav_m(site, place) within 1000 m; distance <= DIST_TOL_M = 50 km, L70). Kind `category` (L155): the row carries `cat` (the P373 category name); ev needs site_cat == cat and file_cat, either equal or joined by a `via` chain whose last element is cat. `check(files, books, catalog)` (L322) silently skips nonexistent paths — the NO_BOOKS = data/books/.no-books trick (never created) skips the book leg, as src_artists.check_staged does. `catalog_map(catalog)` merges the given catalog file + data/catalog/extras.jsonl by id and qid. Row shapes confirmed (from files.jsonl L1479+, extras.jsonl L67+, classified.jsonl): file row = site, qid, title, year, wd_plan, cat, name, by, url, thumb, w, h, mime, date, desc, artist, license, page, date_commons, evidence; extras row = id, qid, name, lon, lat, region, kind, aerial_ok, source, place, wikipedia; classified = {site, title, p_plan, p_birdseye, p_photo, by:"hand"}.

**4. Pitfalls still to file** (session 1's 6 + session 2's 1; grep PITFALLS.md first — none of them is there yet): (1) portal.dnb.de = Anubis/Techaro JS proof-of-work wall (SRU 404, simpleSearch returns the honeypot, any UA); (2) limesblatt.uni-hd.de unreachable (TCP connect fails http+https; DNS 129.206.119.232); (3) www.deutschedigitalebibliothek.de and digital.ub.uni-heidelberg.de have no DNS on this VM; (4) Google-book djvu XML: each page is `<OBJECT ... usemap="<id>_NNNN.djvu">` — the page number lives in the **usemap** attribute, NOT the data attr (data holds the bare djvu name; a regex on `data="..._NNNN.djvu"` matches nothing); per-leaf OCR = the WORDs inside that OBJECT; (5) de.wikipedia `list=allimages` paginates via the continue key **aicontinue** (aifrom/aipfrom do not advance); (6) never read plate legends/scales off 40 dpi renders (session 1 misread both Tafel scales exactly that way); (7) this VM's clock printed 2026-10-12, consistent with the journal dates.

### Session 3 (2026-10-12, iteration 160) — the Commons leg, FINDINGS (session 4 corrects items 2 and 4 where noted)

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
   in its fort's P373 category (RESOLVED session 4: no plate is in a fort's P373 category — the
   direct-membership hits were a modern photo and a Metallfunde find, neither stageable; so ALL
   staged rows use caption_coords). The lead doc §4 must be updated to this reality (the gate
   itself is UNCHANGED and PASSES). Session 4 re-ran the pick with Abt B first and found the 14/15
   "Abt B Grundrisse" claim was WRONG.
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

### Session 4 (2026-10-12, iteration 161) — QID phase done; staging set fixed at 56 files

**What ran:** `/tmp/agent-a-208/leg_c_qids.py` (fixed leg_b2: zero-padded band-key matching "01"↔"1"/"05a"↔"5a" — B2 had searched "Kastell 01 Limes" and found nothing for ten forts; query variants `X (Limes)`/`X Kastell`/`X (Kastell)`; de.wikipedia pageprops fallback for empties; P131 NameError fixed; Commons-P373 hits; the re-pick; de.wiki fileinfo for the new picks). bands.json VERIFIED against the ORL article's Abteilung B list (names/years correct).

**THE FINAL STAGING SET (decided this session):**
- **de.wiki, 45 files** (final_picks.json): one whole-fort Abt B plan per fort (no ORL_A_/Wp/KK names, no "Vers" dup scans), except 45 Welzheim (both West+Ost) and 42 Oehringen (both sub-forts — stage ONLY if a QID appears in session 5, else drop both). Forts whose only plates are building details keep the best one: 01 Heddesdorf (Kastellbad), 12 Kapersburg (Therme), 33 Stockstadt (PPD). 14/15 (Butzbach/Grüningen) have NO Abt B plates in the de.wiki set (raw 874 list checked) → skipped, doc. 05.10 not a fort (growth area). All 45 verified: free (PD-alt-100/Bild-PD-alt), long edge >= 1538 px, desc names the fort (e.g. "Grundriss des Kastells von Osterburken, ORL 40") — the caption+coords contract is met by the desc alone. Desc quirks: 61a says "Lageplan" (the file is a Grundriss), 64 "Schirenhof" (sic), 42 says "Öhringen" (use that spelling for named_place).
- **Commons, 9 files** (caption+coords; P373 route dead per commons_p373_hits.json): `ORL 01 tab 01 pic 01 Lageplan.jpg` (4223px), `ORL 01 tab 02 pic 01 Grundriss.jpg` (4435px, the Heddesdorf FORT plan the de.wiki set lacks!), `ORL 12 tab 02 pic 01 Grundriss und Profile.jpg` (2824px), `ORL 33 tab 02 pic 01 Grundriss.jpg` (11328px, the whole Stockstadt plan), `ORL 33 tab 03 pic 05 Porta Praetoria Grundriss.jpg` (6816px), `ORL 33 tab 04 pic 01-09 Thermen.jpg` (12600px), `ORL 33 tab 05 pic 01 Mithraeum und Dolichenum Lage.jpg` (15023px), `ORL B 2 3b Taf 1 Kastell Wiesbaden.jpg` (3288px), `ORL B 2 3b Taf 2 Kastell Wiesbaden.jpg` (3276px). All "Public domain", descs name the fort (English or German). Dropped: the Taf-1 crop (derivative), Steindenkmäler, Grabenprofile, Anlegestelle (photo), Metallfunde, 3 Tabula Peutingeriana fragments (992-1235px), ORL A section files, ORL22 Rückingen (CC-BY-SA photo). Commons names use SPACES; de.wiki use underscores — disjoint sets.
- **IA 1895 volume, 2 files** (Osterburken): n54 (Situationskarte 1:5000) + n56 (fort plan 1:1000; landscape plate ROTATED 90° in the leaf — rotate CW to upright; record on the row). Titles/desc must contain "Osterburken". The de.wiki twin ORL_40_tab_04_pic_01_Grundriss.jpg stays (same plate, different host — note in doc, not a double count).

**QID decisions (qid_search/qid_entities/qid_routes; verified label + dewiki article + P625 on the limes route):** CONFIRMED: 01 Heddesdorf Q1735373 [P625 (7.4693,50.4365) — FLAG, see below], 02a Niederberg Q1670400, 03 Arzbach Q1735331 [flag], 05 Hunzel Q1240802, 05a Marienfels Q1359182, 07 Kemel Q1725806 [flag], 08 Zugmantel Q1727277, 12 Kapersburg Q1735382 [flag], 18 Echzell Q1657587, 33 Stockstadt Q1735421, 34 Niedernberg Q1735399, 40 Osterburken Q1243550, 41 Jagsthausen Q1735380, 44 Murrhardt Q1735397, 45 West Q32064057 / 45a Ost Q1735441 (P625 adjacent: (9.6323,48.8722)/(9.6422,48.8712) — the split is right), 46 Lützelbach Q1735392, 46b Seckmauern Q1735419, 47 Hainhaus Q1735367, 48 Eulbach Q1735359, 49 Würzberg Q1445553, 50 Hesselbach Q1411006, 51 Schlossau Q1735418, 52 Oberscheidental Q1735404, 53 West Q1343017 (Ost has NO QID → Ost file NOT staged), 56 Böckingen Q1735374, 58 Benningen Q1735337, 59 Cannstatt Q1735423, 60 Köngen Q1735387, 61b Waldmössingen Q1735435, 63 Lorch Q1433981, 65 Unterböbingen Q1424499, 66a Urspring Q1735430, 66b Heidenheim Q128401126 (en label "Castra Aquileia" is correct), 71a Theilenhofen Q1214616, 72 Weißenburg Q638525, Anhausen Q1746855. **NO QID FOUND** (search + 3 variants + pageprops, all in qid_routes.json): 39 Walldürn, 42 Oehringen, 57 Walheim, 61a Sulz, 64 Schierenhof, 67 Buch → NOT staged, documented as growth area (box 3 still passes comfortably). **31 Wiesbaden was never searched** (its plates are Commons-only) — search "Kastell Wiesbaden"/"Kastell Matho" in session 5; if none, drop the 2 Taf files (still passing).
**FLAGS for the session-5 article cross-check** (the de.wiki article's lead paragraph must name the right modern municipality; P625 alone is untrusted): (a) **01 Heddesdorf Q1735373** — P625 (7.4693,50.4365) + P131=Rhineland-Palatinate, but ORL Nr. 1 "Das Kastell Heddesdorf" (Bodewig 1903) is the famous Heilbronn fort (BW, ~9.20E/49.16N) — the QID may be a different or wrong item; the article lead decides; (b) 04 Ems Q1690694 (en "Castra of Bad Ems", P625 (7.713,50.3359) matches neither Alzey-Ems nor Bad Ems — table-only, not staged); (c) 03 Arzbach (7.7457,50.3753); (d) 07 Kemel (8.0161,50.1655); (e) 12 Kapersburg (8.6365,50.3127).

### Session 5+ exact steps
1. **Cross-check leg** (one paced script, ~2 min; /tmp has everything): (a) search "Kastell Wiesbaden"/"Kastell Matho" for 31; (b) for every QID to be staged, batch `de.wikipedia action=query&prop=extracts&exintro` on the article (the QID's dewiki title) and record each lead's location sentence — settles the flags above; (c) one more retry round for the 6 no-QID forts using only variants NOT already in qid_routes.json (e.g. "Kastell Buch (Oberer Limes)" forms). Save crosscheck.json; then finalize the FORTS table (any QID whose article contradicts the monograph → drop that fort's files or re-point to the article's own wikidata id if the search missed it).
2. **File the 9 PITFALLS entries** never written (sessions 1-4): portal.dnb.de Anubis/Techaro JS wall; limesblatt.uni-hd.de TCP connect fails (http+https); www.deutschedigitalebibliothek.de + digital.ub.uni-heidelberg.de have no DNS on this VM (these three → "This machine and its environment"); Google-book djvu XML page number lives in the OBJECT **usemap** attribute, not data (per-leaf OCR = the WORDs inside that OBJECT) → "pipeline/books.py, pipeline/books_ia.py"; de.wiki `list=allimages` paginates via **aicontinue** (aifrom/aipfrom don't advance) → "Wikimedia APIs"; never read plate legends/scales off 40 dpi renders → "Wikimedia APIs"; de.wiki `titles=File:X` normalizes to `Datei:<space name>` (pages dict keyed by that) → "Wikimedia APIs"; `wbsearchentities` returns `description` as a STRING with language=de, not a dict (crashed B1's qid phase) → "Wikimedia APIs"; zero-padded fort-number searches ("Kastell 01 Limes") return nothing — search the label, not the number+"Limes" → "Wikimedia APIs".
3. **Update docs/lead_limes.md** → final PROCEED: counts (56 files / ~46 sites / Bands 1,2a,2b,3,4,5,6,7 + A1 + source 1's Band 4), route (de.wiki + Commons caption+coords; IA 1895; no category evidence), the no-QID skips, the 42/53-Ost conditional drops, the 14/15 correction, the flags' resolutions; commit.
4. **Build fit/src_limes.py + tests/test_src_limes.py + golden** per the prep §2/§3 shapes (session-4 section above has the full spec: SOURCES ia-1895/dewiki-orl/commons-orl; FORTS table from the QID decisions, P625 = site lon/lat, kind "roman fort", region germany, id = slug-qid lower; stage() idempotent on (site,title), by="fit/src_limes.py <source>", row date = monograph year from bands.json; evidence kind caption_coords for EVERY row: named_place = fort name as printed in the desc, site/place = same P625, dist_m 0.0; 1895 rows url https://archive.org/download/derobergermanis00fabrgoog/page/n{54,56}.jpg); check_staged() = join + evidence.check(FILES_LIMES, NO_BOOKS, catalog=EXTRAS_LIMES); golden. **Add `tests/golden/src_limes_sample.json` to the Touches line before writing it.** Test = src_artists pattern: socket-blocking fixture, join, check_staged, negative control (wrong fort / 10 km off — reported, never written), golden compare, box-3 machine-check (>= 10 plans from >= 2 distinct Band volumes — trivially true now; every row's date recorded). Run `.venv/bin/python -m pytest -q`; tick the boxes.

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
