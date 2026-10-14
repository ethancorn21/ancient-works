Status: open
Depends on: 236b
Touches: fit/src_us_birdseye_batch4.py, data/catalog/extras_us_birdseye_batch4.jsonl, data/commons/files_us_birdseye_batch4.jsonl, data/commons/classified_us_birdseye_batch4.jsonl, docs/lead_us_birdseye_batch4.md, tests/test_src_us_birdseye_batch4.py, tests/golden/src_us_birdseye_batch4_sample.json, docs/site_flow/307d_*.png (R5: restoring suite re-encodes to main's bytes before committing - never content changes)

# 240: US bird's-eye views, batch 4 - Denver, St. Paul, Minneapolis, Cleveland

## Goal
Part of 236 (split out of 236b on 2026-10-14, driver instruction: 236b closed done at 16 cities, and
the remaining cities of the 25-city total go to this task and 241, each with its own module and
staging files so two agents can build in parallel). Stage batch 4 of the Library of Congress
"Panoramic Maps" collection (about 1,500 US bird's-eye views, 1847-1929, public domain; this machine
cannot reach loc.gov, so files are fetched from their Wikimedia Commons mirrors - 236b's route, in
its lead doc): FOUR more US cities, each a new site in this task's own staging files, one best
view per city. The 25-city total spans 236b (16) + 240 (4) + 241 (5); 236c consolidates all the
staging into the canonical data and checks the total.

## Acceptance criteria
- [ ] fit/src_us_birdseye_batch4.py holds the hand-checked file -> QID table for its four cities
      (every QID verified live against Wikidata with the module's --verify BEFORE staging: label,
      every P625 value, P373, P131, enwiki, the first name-search hit with coordinates - what
      record --live would resolve; the machine cannot reach loc.gov, so the files are fetched from
      their Wikimedia Commons mirrors, 236b's route). The module copies fit/src_us_birdseye.py's
      machinery (the verify/stage/check/golden CLI, the 200 caption_coords evidence field, the
      Zwolle date-swap rule, the never-two-sites-for-one-QID cross-check - extended to 236a's and
      236b's staging files); its docstring names fit/src_us_birdseye.py as the template it keeps in
      sync with.
- [ ] Staged rows in this task's files ONLY: extras_us_birdseye_batch4.jsonl (the new cities' site
      rows - region "United States", kind "town", aerial_ok true, the point = the city's verified
      P625 or a recorded refinement, the note recording the staged view's apparent angle so 236c /
      the matcher can order the oblique views); files_us_birdseye_batch4.jsonl (files.jsonl shape +
      the 200 evidence field); classified_us_birdseye_batch4.jsonl (p_birdseye 1.0, by "hand"). One
      row per city = the steepest (near-vertical), best-scanned whole-city view of the collection
      for that city (Public domain, >= 4000 px wide, the caption names the city); every pool item
      not staged is listed with its reason in the lead doc.
- [ ] fit/evidence.py check passes offline on every staged row (--check exit 0, every row PASS
      caption_coords, no join problems); no staged site id or QID collides with an existing site
      (the catalog, 236a's extras_us_cities.jsonl, 236b's extras_us_birdseye.jsonl, 241's file when
      it exists, web/data/sites.json) - never two sites for one QID (the catalog slug rule:
      id = slug(name) + "-" + qid-lower).
- [ ] Test (no network, the socket-blocking fixture per 236b's test file): the staged files join,
      the evidence check passes, a golden sample tests/golden/src_us_birdseye_batch4_sample.json
      pins the staged rows (regenerated only via the module's --golden for an intended change); a
      full-suite run = baseline (restore the re-encoded docs/site_flow/307d_*.png to main's bytes
      before committing - the PITFALLS test_owner_check rule).
- [x] Denver is staged as researched (Q16554; the 1908 Birdseye View Publishing Co. sheet,
      `File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg`, looking south from the
      Twenty-Third Street Viaduct): the Notes below carry the full research record; the first
      session re-verifies it live (--verify) and, if the pick is gone from Commons or no longer PD,
      takes the next-best pool candidate and records the swap in the lead doc.

## Notes (operational facts carried from the 236b split, 2026-10-14 iteration 195)

**Read first (all in 236b, done - on main):** docs/lead_us_birdseye.md (the Fetch route section:
the Commons file-namespace search, the six plain-phrase forms + " filetype:bitmap", the
keep/caption/Public-domain/width gates, the Zwolle date-swap rule, the evidence-field contract,
the STAGED/DROP section format, the QID-verification transcript format, the Staging section with
the verbatim --check transcript format) and fit/src_us_birdseye.py (the template module: SITES /
SHARED_SITES / SOURCES tables + verify_qids / stage / check_staged / golden + the CLI). COPY that
module to fit/src_us_birdseye_batch4.py and change only: the staging-file paths (the four
*_us_birdseye_batch4.* paths in the Touches line above), the module name inside the rows' "by" /
"source" fields, and known_sites() to ALSO read data/catalog/extras_us_birdseye.jsonl (236b) and
data/catalog/extras_us_birdseye_batch5.jsonl (241; absent until it runs - _load() tolerates a
missing file) so a QID can never sit on two sites. Do NOT edit fit/src_us_birdseye.py,
fit/evidence.py or any pipeline/ file (read-only for this task; file a task if one of them needs
a change). This module stages no shared (owner-named) cities: SHARED_SITES stays out of the copy.

**One row per city, the steepest, best-scanned whole-city view** (Public domain, >= 4000 px wide,
caption names the city); shallower same-genre sheets and the non-view pool (street-car scenes,
real-estate ads, district close-ups, regional views, photographs, too-small scans, other-city
sheets, licence rejects) are DROPS recorded with reasons in the lead doc (the 236b precedent).
Batch 4's candidate order: **Denver, St. Paul, Minneapolis, Cleveland** (236b's lead-doc order).
This task owes FOUR staged cities, not specifically these four: a city with no usable view gets a
lead-doc note and the next candidate. Before adding any SITES entry, check that no existing site
holds the QID (catalog/sites.jsonl, catalog/extras.jsonl, 236a's and 236b's extras files,
web/data/sites.json) - if one does, tie the row to that site like 236b's shared cities and record
it in the lead doc (never a second site for one QID). St. Paul especially has name-search traps
(there are other St. Pauls - Louisiana, South Carolina - and big institutions in the city; the
Pittsburgh/Chicago university-trap class in 236b's module comments).

**Per-city landing (the proven 189-194 pattern, one city per session pair):** (1) RESEARCH: the
QID (Wikidata: the label - first-guess mislabels are the usual trap class, every P625 value, P373
(a string is the usual US quirk - write the place from the county + state), P131, P17, enwiki,
the name-search trap check; record everything in the SITES comment; MEASURE every distance claim
with fit/evidence.hav_m + geographic dx/dy before writing it) + the pool (the
/tmp/aw236b_b3_dvr.py script is the template: build, dedupe, filter, 1280 px thumbs eyeballed one
by one - artifacts under /tmp, re-verifiable). (2) LANDING: module edit -> --verify (save the
exact output; the lead doc carries it verbatim in the QID section) -> --dry -> stage (live
commons.info re-check) -> --check (save the transcript; the Staging section carries it verbatim)
-> lead-doc section (STAGED bullet with the view's facts + the full DROP list + the QID-facts
paragraph) -> --golden -> test extension (mirror tests/test_src_us_birdseye.py: the no_network
socket-blocking fixture; the PASS-key list; the SITES-id / extras-id / year / point / named tables;
the golden compare) -> module tests -> the FULL suite (restore the 307d pngs first, below) ->
commit. The lead doc's Staging section ends with the Not-done-yet pointer to 241 naming the next
two or three candidates (the 236b precedent).

**Rules (unchanged from 236b):** NEVER write the canonical files (data/catalog/extras.jsonl,
data/commons/files.jsonl, classified.jsonl - that is 236c); NEVER touch 236a's or 236b's files
(read-only; the module's cross-check enforces); live commands under .venv/bin/python (system
python3 has no numpy; the module top stays stdlib-only); the golden sample is the contract
(--golden only for an intended change); tests never bind fixed network ports or write outside the
project and the temp dir; every full-suite run re-encodes up to ten docs/site_flow/307d_*.png -
restore main's bytes before committing (the PITFALLS test_owner_check entry).

**Denver is RESEARCHED (236b iteration 194, agent a; the full DECISIONS entry "236b DECISION:
iteration 194" is archived with 236b - search DECISIONS-archive.md; the /tmp artifacts
/tmp/aw236b_b3_dvr* still exist, re-verify live if wiped):** QID = **Q16554** (label "Denver", the
consolidated city-county and capital of Colorado; the first-guess Q3101 is a PERSON - Patrick
Ricard - caught by the label check). Live facts: P625 = ONE 30 m value (-104.984722, 39.739167)
the central CBD (no refinement needed); P373 = the STRING "Denver, Colorado" (the usual quirk);
P131 = Q1261 Colorado + Q13052701 Denver County (consolidated city-county - hence place "Denver
County, Colorado"); P17 = Q30; enwiki "Denver"; name search: NO trap (the first hit with P625 is
Q16554 itself, dist 0). No existing site holds it (checked 194 in the catalog, extras, 236a's
file and web/data/sites.json). Site id = **denver-q16554** (catalog.slug("Denver") = "denver",
verified). Pool (194): 65 unique / 33 good. **THE PICK: `File:Bird's eye view of Denver, Colorado,
1908. LOC 75693133.jpg`** (19338x13294, PD; page date 1908 = the drawing's year, no swap; artist
"Birdseye View Publishing Co.; Denver Lith. Co."; banner "BIRD'S EYE VIEW OF DENVER, COLORADO,
1908 LOOKING SOUTH FROM THE TWENTY-THIRD STREET VIADUCT" - the steepest near-vertical whole-city
view in the pool, drawn from the north of the city looking south: the dense grid legible to the
southern suburbs, the Front Range along the top of the sheet (the southern horizon), the South
Platte meandering in from the northwest along the sheet's RIGHT side (the sheet faces south, so
west is right - no mirroring), the landmark index across the bottom; the viaduct is ~1.3 km north
of the site's point, measured 194: 23rd-street lat 39.7508 - P625 39.739167 = 0.0116 deg x
110900 m/deg = 1287 m). Same-sheet scans (one row per sheet, the LOC .jpg staged): the 19338x13294
.tif twin + the 9000x6205 DPLA copy (4ac8083cbba722c01cad3388a37a7a0f). **DROPS (the per-item
reasons are in the 194 DECISIONS entry; 16 distinct sheets):** the 1881 Flett (LOC photocopy,
shallower), the 1887 Rocky Mountain News / Mills, the 1882 Platt / Slocum chromo, the 1874 Glover
(the pool's OLDEST whole-city view - its three 1536 px copies are too small), the 1887
Arbor-Day Colfax-avenue street (thumb fetched, NOT yet eyeballed - confirm), the 1895 "Healer"
street-car scene (thumb fetched, NOT yet eyeballed), the 1907 South Broadway real-estate ad, the
1913 Daniels & Fisher tower PHOTOGRAPH, the Clayton School close-up, the Lookout Mountain regional
view, the state-of-Colorado sheet (the title's "1603" is a FALSE year picked up from the DPLA
hash), other-city rejects (Golden, Pueblo, Canon City, Greeley, Gunnison, Leadville, Maysville,
Colorado Springs + Manitou), too-small (Kilburn, CO Denver 1889, the Great Plains book sheets),
the CC BY-SA 1907 sheet, and the 2021 Union Station photo (beyond the 1925 MAX_YEAR).

**St. Paul, Minneapolis, Cleveland: NOT yet researched.** Run the per-city playbook. (All three
have classic bird's-eye views in the LOC collection - the pool search shows which survived the
gates; do not trust this note, verify live.)


## Hand-over
(2026-10-14, iteration 161, agent c - session 2 of 240: the merge was already committed by the
driver (483d528); the R1 baseline is ESTABLISHED (177P/1S/0F); the batch4 test + golden are
committed and the Denver landing is COMMITTED (boxes 1-4 stay open - they span all four cities;
box 5 (Denver) is ticked). NEXT: St. Paul (city 2) - research QID + pool, then the landing.)

**State NOW (all committed on agent/c):**
1. **The batch4 module** fit/src_us_birdseye_batch4.py (clean mechanical copy of the 236b
   template with the 5 prep changes; fresh-eyes diff confirmed this session) with SITES = Denver
   (Q16554) only so far; SOURCES has denver_1908. Staging files: extras_us_birdseye_batch4.jsonl
   (1 site row: denver-q16554, point (-104.984722, 39.739167), place "Denver County, Colorado"),
   files_..._batch4.jsonl (1 row: the 1908 LOC 75693133 pick, year 1908, Public domain, evidence
   caption_coords dist 0), classified_..._batch4.jsonl (1 row p_birdseye 1.0 by hand). All in the
   driver's 3562737 commit.
2. **The test** tests/test_src_us_birdseye_batch4.py (5 offline tests mirroring the 236b file;
   the no_network socket-blocker; the PASS-key list = Denver key only so far, GROWS one entry per
   city landing; the three-states 236c-merge test; the SITES/extras/files tables - the extras file
   is EXACTLY the SITES set, one view per city; the Venice negative control (8673157 m); the
   golden compare) and **the golden** tests/golden/src_us_birdseye_batch4_sample.json (1/1/1) -
   committed this session with the Denver landing.
3. **Baselines (R1, both in DECISIONS):** merged-tree baseline = 177P/1S/0F (the iteration-160
   background run completed clean; it matches 236b's full-main-tree closeout). Post-landing
   confirmation run this session = **182P/1S/0F** (/tmp/aw240_suite_161.log, 516 s) = baseline +
   the 5 new tests, zero failures. The long-flagged red
   test_fit_queue::test_placement_gestures_and_save_in_the_browser is GONE from the merged tree
   (agent a's 235 fix 344aa0c landed on main) - this checkout's suite has NO known reds.
4. **Lead doc** docs/lead_us_birdseye_batch4.md: complete for Denver (Fetch route; QID section
   with the verbatim --verify transcript; evidence field; Denver STAGED + the full 16-item DROP
   list + QID facts with the 1287 m viaduct measurement; Staging and checks with the verbatim
   --check transcript at 1 view / 1 site row; the Not-done-yet pointer to 241 naming Omaha,
   Indianapolis, Columbus, Memphis). The Staging section's running counts (1 view / 1 site row)
   and the QID/Staging transcripts must be EXTENDED per landing (2/2, 3/3, 4/4).
5. **307d pngs:** restored to main's bytes before both commits this session (R5); they re-encode
   on EVERY full-suite run - restore again before every commit (`git checkout main --
   docs/site_flow/`).

**Exact next steps (St. Paul, city 2 - one session pair, the proven 189-194 pattern):**
1. **RESEARCH (live; /tmp artifacts wiper-prone - rebuild from the recipes if wiped):**
   - QID: clone /tmp/aw236b_b3_dvr_qid.py (repoint its sys.path at THIS checkout - it points at
     ancient-works.a) and run under .venv/bin/python: the label (St. Paul, Minnesota - the
     first-guess mislabel is the usual trap), EVERY P625 value with precision, P373 (a string is
     the usual US quirk - write the place from the county + state), P131 with labels, P17,
     enwiki, and the name search: other St. Pauls (St. Paul, Louisiana; St. Paul, South Carolina)
     and big in-city institutions are the trap class (Pittsburgh/Chicago university precedent in
     the 236b module comments) - record the first hit with P625 + measured distance (hav_m +
     geographic dx/dy, NOT raw Mercator). Check no existing site holds the QID (catalog
     sites.jsonl + extras.jsonl + 236a's + 236b's extras files + web/data/sites.json).
   - Pool: clone /tmp/aw236b_b3_dvr.py for the city name (the SIX plain-phrase Commons
     file-namespace forms + " filetype:bitmap", srnamespace 6, srlimit 40; dedupe; gates: caption
     names the city AND commons.keep() (judged AFTER any Zwolle known-date swap) AND license
     "Public domain" AND width >= 4000). Eyeball every good item's 1280-px thumb one by one
     (upload.wikimedia thumb endpoint, project UA, paced - upload.wikimedia rate-limits raw
     downloads separately from the API). THE PICK = the steepest (near-vertical), best-scanned
     whole-city view (Public domain, >= 4000 px, caption names the city); one row per sheet
     (same-sheet scans recorded, the best scan staged); record EVERY non-staged pool item with
     its reason.
2. **LANDING (exactly as Denver):** module edit (SITES entry with the full comment block + a
   batch-4-city-2 comment + the `<CITY>_<YEAR>` row-list + the SOURCES entry) -> --verify (save
   the EXACT output; append it to the lead doc's QID section; expect no FLAG/TRAP or refine the
   point and record why) -> --dry -> stage (live commons.info re-check; a vanished/no-longer-PD
   pick fails loud -> box 5's swap: next-best pool candidate, recorded) -> --check (append the
   transcript to Staging) -> lead-doc St. Paul section (STAGED bullet with the view's facts +
   the full DROP list + the QID-facts paragraph; update the Staging counts) -> --golden ->
   extend the test (PASS-key list + the SITES/extras/years/points/named tables) -> module tests
   -> the FULL suite (.venv/bin/python -m pytest -q -p no:cacheprovider; expect = previous run
   + new tests) -> restore the re-encoded 307d pngs (R5) -> commit "240: St. Paul landed
   (batch 4 city 2) - <the view>".
3. **Then Minneapolis (city 3) and Cleveland (city 4)** the same way. **After Cleveland: close**
   - final full-suite run = baseline, --check all PASS no join problems, the four ids/QIDs
   collide with nothing (the known_sites() guard + the test), extend the test tables to the full
   set, boxes 1-4 tickable (each after its test passes), the lead doc's Staging section final
   (4 views / 4 site rows), Status: done.

**Rules that bite (unchanged from the task Notes):** never write the canonical files (236c);
236a's and 236b's files are read-only (the module's cross-check enforces); live commands under
.venv/bin/python (module top stays stdlib-only; the /tmp qid/pool scripts point their sys.path
at ancient-works.a - repoint); golden regenerates only via --golden; tests never bind fixed
ports or write outside project + temp; every full-suite run re-encodes up to ten 307d pngs -
restore main's bytes before EVERY commit (R5) and never edit suite-hashed files mid-run (R6:
data/ minus raw, web/data top level, docs/, specs/, tests/ are snapshotted - finish all edits,
THEN run, restore, commit). /tmp artifacts (aw236b_b3_dvr*, aw240_*_160/161.*) are wiper-prone;
the recipes in the Notes + prep section 1 rebuild them. The full-suite run takes ~9 min - start
it, then do the bookkeeping; check the log tail before committing.
