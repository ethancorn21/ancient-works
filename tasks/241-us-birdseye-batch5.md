Status: in-progress
Depends on: 240
Touches: fit/src_us_birdseye_batch5.py, data/catalog/extras_us_birdseye_batch5.jsonl, data/commons/files_us_birdseye_batch5.jsonl, data/commons/classified_us_birdseye_batch5.jsonl, docs/lead_us_birdseye_batch5.md, tests/test_src_us_birdseye_batch5.py, tests/golden/src_us_birdseye_batch5_sample.json, PITFALLS.md, docs/site_flow/307d_*.png (R5: restoring suite re-encodes to main's bytes before committing - never content changes)

# 241: US bird's-eye views, batch 5 - the final five cities to the 25-city total

## Goal
Second part of the 236b split (2026-10-14, driver instruction; 236b closed done at 16 cities and the
remaining nine went to 240 and this task, each with its own module and staging files so two agents
can build in parallel). Stage batch 5 of the Library of Congress "Panoramic Maps" collection (about
1,500 US bird's-eye views, 1847-1929, public domain; this machine cannot reach loc.gov, so files are
fetched from their Wikimedia Commons mirrors - 236b's route): the FINAL FIVE cities needed for the
25-city total (16 from 236b + 4 from 240 + 5 here), each a new site in this task's own staging
files, one best view per city. 236c consolidates all the staging into the canonical data and checks
the total.

## Acceptance criteria
- [ ] fit/src_us_birdseye_batch5.py holds the hand-checked file -> QID table for its five cities
      (every QID verified live against Wikidata with the module's --verify BEFORE staging: label,
      every P625 value, P373, P131, enwiki, the first name-search hit with coordinates - what
      record --live would resolve; the machine cannot reach loc.gov, so the files are fetched from
      their Wikimedia Commons mirrors, 236b's route). The module copies fit/src_us_birdseye_batch4.py's
      machinery (itself a copy of fit/src_us_birdseye.py's - the template it keeps in sync with);
      its known_sites() reads the catalog plus 236a's extras_us_cities.jsonl, 236b's
      extras_us_birdseye.jsonl and 240's extras_us_birdseye_batch4.jsonl so a QID can never sit on
      two sites.
- [ ] Staged rows in this task's files ONLY: extras_us_birdseye_batch5.jsonl (the new cities' site
      rows - region "United States", kind "town", aerial_ok true, the point = the city's verified
      P625 or a recorded refinement, the note recording the staged view's apparent angle so 236c /
      the matcher can order the oblique views); files_us_birdseye_batch5.jsonl (files.jsonl shape +
      the 200 evidence field); classified_us_birdseye_batch5.jsonl (p_birdseye 1.0, by "hand"). One
      row per city = the steepest (near-vertical), best-scanned whole-city view of the collection
      for that city (Public domain, >= 4000 px wide, the caption names the city); every pool item
      not staged is listed with its reason in the lead doc.
- [ ] fit/evidence.py check passes offline on every staged row (--check exit 0, every row PASS
      caption_coords, no join problems); no staged site id or QID collides with an existing site
      (the catalog, 236a's, 236b's and 240's staging files, web/data/sites.json) - never two sites
      for one QID (the catalog slug rule: id = slug(name) + "-" + qid-lower).
- [ ] Test (no network, the socket-blocking fixture per 236b's test file): the staged files join,
      the evidence check passes, a golden sample tests/golden/src_us_birdseye_batch5_sample.json
      pins the staged rows (regenerated only via the module's --golden for an intended change); a
      full-suite run = baseline (restore the re-encoded docs/site_flow/307d_*.png to main's bytes
      before committing - the PITFALLS test_owner_check rule).
- [ ] FIVE cities staged (the 25 total: 16 from 236b + 4 from 240 + 5 here), each per the boxes
      above; or, if the collection yields fewer usable candidates after a documented search, each
      dropped candidate is recorded with its reason in the lead doc and the shortfall (with the
      final count) is recorded there for 236c's 25-total check.

## Notes (operational facts carried from the 236b split, 2026-10-14 iteration 195)

**Read first (all on main):** 240's task file (its Notes carry the complete per-city playbook, the
module-copy spec and the rules - they apply here verbatim), fit/src_us_birdseye_batch4.py (the
module to copy - change only the staging-file paths to the *_us_birdseye_batch5.* set in the
Touches line, the module name in the rows' "by" / "source" fields, and known_sites() to also read
240's extras_us_birdseye_batch4.jsonl - it will exist by the time this task runs, 240 is done),
240's lead doc (docs/lead_us_birdseye_batch4.md: the STAGED/DROP section format, the QID
transcript format, and its "Not done yet" pointer naming the next candidates), plus 236b's
docs/lead_us_birdseye.md (the Fetch route and evidence-field contract) if you need the original
wording. Do NOT edit fit/src_us_birdseye.py, fit/src_us_birdseye_batch4.py, fit/evidence.py or any
pipeline/ file (read-only for this task; file a task if one of them needs a change). This module
stages no shared (owner-named) cities.

**The candidate list:** start from 240's lead-doc "Not done yet" pointer (240's Notes require it
to name the next two or three candidates in the collection's search order); if it names fewer than
five, continue the LOC Panoramic collection's city list in search order (the six plain-phrase
forms + " filetype:bitmap" over candidate cities - 236b's pool route), skipping cities already
staged anywhere (236b's and 240's site tables, the catalog, web/data/sites.json) and cities whose
pools yield no usable view (record each drop, take the next candidate). This task owes FIVE
staged cities, not specific ones. St. Paul / Minneapolis / Cleveland were 240's candidates - if
240 dropped any of them, they come first here (240's lead doc says why they dropped).

**Per-city landing (the proven 189-194 pattern, one city per session pair):** (1) RESEARCH: the
QID (Wikidata: the label - first-guess mislabels are the usual trap class, every P625 value, P373
(a string is the usual US quirk - write the place from the county + state), P131, P17, enwiki,
the name-search trap check; record everything in the SITES comment; MEASURE every distance claim
with fit/evidence.hav_m + geographic dx/dy before writing it; check no existing site holds the
QID - if one does, tie the row to that site like 236b's shared cities and record it in the lead
doc) + the pool (build, dedupe, filter, 1280 px thumbs eyeballed one by one - the
/tmp/aw236b_b3_dvr.py script is the template). (2) LANDING: module edit -> --verify (save the
exact output; the lead doc carries it verbatim in the QID section) -> --dry -> stage (live
commons.info re-check) -> --check (save the transcript; the Staging section carries it verbatim)
-> lead-doc section (STAGED bullet + the full DROP list + the QID-facts paragraph) -> --golden ->
test extension (mirror tests/test_src_us_birdseye.py / test_src_us_birdseye_batch4.py: the
no_network socket-blocking fixture; the PASS-key list; the SITES-id / extras-id / year / point /
named tables; the golden compare) -> module tests -> the FULL suite (restore the 307d pngs first)
-> commit. The lead doc's Staging section ends with the project total (it should read 25 when all
five land) and a note that 236c consolidates.

**Rules (unchanged from 236b/240):** NEVER write the canonical files (data/catalog/extras.jsonl,
data/commons/files.jsonl, classified.jsonl - that is 236c); NEVER touch 236a's, 236b's or 240's
files (read-only; the module's cross-check enforces); live commands under .venv/bin/python
(system python3 has no numpy; the module top stays stdlib-only); the golden sample is the contract
(--golden only for an intended change); tests never bind fixed network ports or write outside the
project and the temp dir; every full-suite run re-encodes up to ten docs/site_flow/307d_*.png -
restore main's bytes before committing (the PITFALLS test_owner_check entry); one row per sheet
(same-sheet scans recorded in the lead doc, the LOC .jpg staged where it is the best scan).

## Hand-over
(2026-10-14, iteration 175, agent c - **Omaha RESEARCH done (the task's first open question resolved:
236b skipped Omaha with no recorded reason, but its pool has a strong pick); next session = the Omaha
LANDING, batch-5 city 1 of 5**)

**State:**
- Step 0 committed (driver 193e4d2): `fit/src_us_birdseye_batch5.py` (401 lines, `SITES = {}`),
  `docs/lead_us_birdseye_batch5.md` (skeleton), `tests/test_src_us_birdseye_batch5.py` (5 tests),
  `tests/golden/src_us_birdseye_batch5_sample.json` (empty 0/0/0). Working tree clean. Post-174 full
  suite GREEN: 190 passed / 1 skipped / 0 failed (/tmp/aw241_suite_post_174.log; 191 = 186 baseline + 5
  new). The driver's 241 baseline: 0 failing (loop.log) - any red is not this task's (R2).
- Omaha RESEARCH (this session; full record in the DECISIONS 175 entry, the 240 format):
  - **QID Q43199 = Omaha, Nebraska**: label matches; ONE P625 (-95.9375, 41.25861111111111, ~30 m) =
    downtown, no refinement; P373 = STRING "Omaha, Nebraska" -> place "Douglas County, Nebraska"
    (P131 = Q490695 Douglas County only + the state, the Denver pattern); P17 = Q30; enwiki
    "Omaha, Nebraska". Name search (limit 5 AND 20, R5): **NO TRAP** (the first P625 hit at both
    limits is Q43199 itself, dist 0; other hits = album/UNO/film/Beach/namesakes). Q43199 and
    "omaha" are in NO existing site file (catalog, extras, 236a/236b/240 files, web/data/sites.json -
    clean grep); catalog.slug("Omaha") = "omaha" verified -> id **omaha-q43199**.
  - **Pool** (/tmp/aw241_omaha_pool.json, six phrase forms + filetype:bitmap): 39 unique, 8 gate-pass.
    Only TWO true whole-city sheets: **the 1868 E. Ruger sheet** (File:Bird's eye view of the city of
    Omaha, Nebraska 1868. LOC 73693495.tif, 8896x7024, PD, LC Panoramic 467, page date 1868 = title
    year - no Zwolle swap; the .tif is the ONLY scan of the sheet - LCCN search) and **the 1905
    Austen sheet** (File:Panoramic view of Omaha. LOC 75694679.jpg + .tif, 10080x5808, PD, LC
    Panoramic 468, "Supplement to the Omaha Daily Bee, January 1, 1906"). **PICK = the 1868**: steeper
    (the built-up grid fills the sheet from a high vantage over the Missouri River; the river a
    foreground strip with steamboats + a railroad, a thin hill-horizon band at the top) vs the 1905's
    LOW "PANORAMIC VIEW OF OMAHA" oblique (frozen river fills the lower-right quadrant, wide plain
    horizon band ~30% at the top) - the 1905 is the same-genre dupe drop (both its scans). Six other
    gate-pass items eyeballed (/tmp/aw241_omaha_thumbs/) are false positives: Weber stereo PHOTO cards
    x2 (the series line "west from Omaha"), Green River WY 1875 ("846 miles west of Omaha"), the 1893
    Rocky Mountains regional sheet (copyright line "...Omaha, Nebr."), the Great Plains book TEXT
    page. 31 more rows fail a gate (22 too small incl. the 1865 Jackson Bros / Currier set + 9 NYPL
    3072 px + the 1897/98 Trans-Mississippi x2; 6 Union Pacific book sheets; Sioux City; 2 "No
    restrictions" rejects; 1 NBY photo) - full list in the DECISIONS entry.
  - **Verdict on 236b's silent Omaha skip**: stageable - it fell out of 236b's batch order (the 181
    list ran past it to St. Paul/Minneapolis), not for a pool failure. Omaha stays batch-5 city 1;
    next candidates: **Indianapolis, Columbus, Memphis**, then the collection's search order.
- New PITFALLS fit/ entry filed (the pool gate is a substring match - incidental mentions pass;
  eyeball every gate-pass item).
- /tmp artifacts (re-verifiable): aw241_omaha_qid.py/.log, aw241_omaha_pool.py/.json/.log,
  aw241_omaha_thumbs.py + /tmp/aw241_omaha_thumbs/ (8 thumbs). `aw241_omaha_pool.py` is the template
  for the next candidates (change CITIES, the output path, and the thumbs script's slug).

**Next session - the Omaha LANDING (the per-city playbook step 2, the 240 pattern):**
1. Module edit (`fit/src_us_birdseye_batch5.py`): replace the `SITES = {}` preamble with the Q43199
   comment block (mirror batch4's Denver comment: the facts above, no trap, skip-list check, slug)
   + `SITES = {"Q43199": dict(id="omaha-q43199", name="Omaha", named="Omaha", lon=-95.9375,
   lat=41.258611, place="Douglas County, Nebraska", region="United States", kind="town",
   wikipedia="https://en.wikipedia.org/wiki/Omaha,_Nebraska", note=<angle text below>)}`;
   `OMAHA_1868 = [("File:Bird's eye view of the city of Omaha, Nebraska 1868. LOC 73693495.tif",
   "Q43199", "Omaha", dict())]` (empty dict = no Zwolle swap; the page date IS 1868);
   `SOURCES = {"omaha_1868": dict(rows=OMAHA_1868, p="birdseye", label="{name}, the E. Ruger /
   Chicago Lithographing Co. bird's-eye view (1868)")}`. Angle text: "the 1868 E. Ruger sheet
   (the steepest whole-city view in the pool; the 1905 Austen 'panoramic' oblique is the recorded
   dupe): a steep bird's-eye view from a high vantage across the Missouri River (the river a
   foreground strip with steamboats and a railroad along the sheet's bottom, a thin hill-horizon
   band at the top); the city grid fills the sheet beyond the 2000 m town box, so the fit is
   likely to end a review item (the 236a NY-1811 / DC-ring precedent)". NOTE: the page's artist
   field says "Ruger, A.; Chicago Lithographing Co." but the sheet's own signature (lower left)
   says "E. Ruger" - label from the signature and record the mismatch in the lead doc (240's
   Cleveland 1877 is an A. Ruger work - a different person).
2. `.venv/bin/python fit/src_us_birdseye_batch5.py --verify` -> expect exactly 1 QID, NO FLAG/TRAP
   (the first P625 name-search hit is Q43199 itself); save the output VERBATIM into the lead doc's
   QID section (replacing the placeholder).
3. `--dry` -> stage (live commons.info re-check: keep() must pass - date 1868, PD, 8896 px) ->
   `--check` (expect `PASS caption_coords  omaha-q43199|File:Bird's eye view of the city of Omaha,
   Nebraska 1868. LOC 73693495.tif`, `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`, no join: lines);
   save the transcript verbatim into the lead doc's Staging section (append after the skeleton's
   "Nothing is staged yet" - that sentence becomes the running count "1 view / 1 site row so far of
   the final five").
4. Lead-doc city section (`docs/lead_us_birdseye_batch5.md`, mirror batch4's Denver section):
   "## Omaha (site `omaha-q43199`, this task's point = the verified P625; 1 view staged)" with the
   STAGED bullet (the facts + the angle text), the DROP list (the 38 non-staged pool items - the
   full text is in the DECISIONS 175 entry; format it batch4-style: the 1905 dupe first with both
   scans, then the six eyeballed false positives with what the gate caught, then the gate-fail
   groups), the QID-facts paragraph (from the --verify transcript + the live log: the namesake
   hits, the P373 string quirk, no existing site holds the QID). Update the Not-done-yet pointer:
   Omaha done; the remaining four = Indianapolis, Columbus, Memphis, then search order.
5. `--golden` (now 1/1/1 - an intended change) -> extend `tests/test_src_us_birdseye_batch5.py`:
   test 2's key list = [(omaha site, the 1868 title)]; test 4's tables (id omaha-q43199,
   lon/lat -95.9375/41.258611, place, year 1868, named "Omaha"); the hermetic three-states test is
   unguarded (`if staged_files:` becomes live: states a/b/c, the c-state message "join: staged
   title already in the canonical files.jsonl: ('omaha-q43199', '<title>')"); the negative control
   rebinds to files[0] (the real Omaha row with the Venice point 12.33, 45.44 - the 236b pattern;
   drop the Batchville synthetic).
6. Module tests -> the FULL suite (.venv/bin/python -m pytest -q; ALL edits done first - R4;
   restore any re-encoded docs/site_flow/307d_*.png to main's bytes first - R5; expect 191 tests
   plus whatever main merges) -> commit "241: Omaha landed (batch-5 city 1/5) - the 1868 E. Ruger
   sheet (LOC 73693495) - steepest of the pool's two whole-city views".

**Cities 2-5 the same** (Indianapolis, Columbus, Memphis, then the 181 list's remainder - clone
/tmp/aw241_omaha_pool.py per city; the Staging section ends at the total 25 = 16 + 4 + 5, or the
recorded shortfall, with the 236c note; a city whose pool yields no usable view gets the drop note
and the next candidate).

**Rules (unchanged):** never write the canonical files (236c); never touch 236a's/236b's/240's files
(read-only; known_sites() enforces); live commands under .venv/bin/python (module top stays
stdlib-only); the golden is the contract (--golden only for an intended change); tests never bind
fixed ports or write outside the project and /tmp; every full-suite run re-encodes up to ten
docs/site_flow/307d_*.png - restore main's bytes before committing (R5).
