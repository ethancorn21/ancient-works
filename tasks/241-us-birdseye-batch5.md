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
(2026-10-14, iteration 176, agent c - **Omaha LANDING functionally complete, changes saved
UNCOMMITTED by the context limit** (the harness holds them for the next agent): module tests 5/5,
full suite GREEN 190 passed / 1 skipped / 0 failed in 553 s (in-session blocking run; the 307d
PNGs were restored to main's bytes after it). Next session: step 1 = re-verify + COMMIT the
landing, then the INDIANAPOLIS research + landing (city 2/5), the same per-city playbook.)

**What the saved tree contains (the Omaha landing, batch-5 city 1/5):**
- `fit/src_us_birdseye_batch5.py`: SITES[Q43199] (id omaha-q43199; point = the verified P625 at
  full precision -95.9375/41.25861111111111; place "Douglas County, Nebraska"; the note = the
  staged view's apparent angle), OMAHA_1868 (the single .tif row; empty dict = no Zwolle swap -
  the page date 1868 IS the drawing's year) and SOURCES["omaha_1868"] (label from the sheet's own
  signature "E. Ruger", NOT the page's artist field "Ruger, A." - two different Rugers; the
  mismatch is recorded in the lead doc). Header comments say Omaha is LANDED.
- Staging files at 1/1/1 (extras/files/classified_us_birdseye_batch5.jsonl); --check green (PASS
  caption_coords, "evidence: 1 rows, 1 pass, 0 fail, 0 no-tie", no join problems); golden = 1/1/1.
- Lead doc: the Omaha city section (STAGED bullet - the cartouche banner re-verified from the
  surviving 175 thumb with zoomed crops; the 38-item DROP list; the QID-facts paragraph; the
  236b-silent-skip verdict), the verbatim --verify transcript (no FLAG/TRAP), the Staging section
  count "1 view / 1 site row so far of the final five" + the verbatim --check transcript, and the
  updated Not-done-yet pointer (next: Indianapolis, Columbus, Memphis; New Orleans is 236b's -
  skip it in the search order).
- Tests extended per the 236b/240 pattern: test 1's key list = the Omaha PASS line; test 3's (c)
  is now unguarded (live from the first landing on); test 4's tables filled + the Omaha 1868 date
  check (no date_commons); test 5's negative control rebound to files[0] (the real Omaha row) with
  the Venice point -> FAIL "does not reproduce (8036016 m)" (hav_m measured this session).

**Next session, exact steps:**
1. `git status` to confirm the saved tree (module, 3 staging files, lead doc, golden, test file
   dirty; 307d pngs clean). Run `.venv/bin/python -m pytest tests/test_src_us_birdseye_batch5.py
   -q` - expect 5/5. If green: `git add -A && git commit -m "241: Omaha landed (batch-5 city
   1/5) - the 1868 E. Ruger sheet (LOC 73693495) - steepest of the pool's two whole-city views"`
   (R2: the driver's 241 baseline is 0 failing - any red first goes to the PITFALLS Esri-flake /
   pytest-temp-tree entries and an isolated re-run; if a suite re-run re-dirties the 307d PNGs,
   restore them before committing - R5).
2. INDIANAPOLIS research (city 2/5; live): QID (label - the first-guess mislabel is the usual
   trap; every P625; P373 - a string is the usual US quirk, place = county + state; P131; P17;
   enwiki; the name-search trap check at BOTH limit 5 AND limit 20 (R5); no existing site holds
   the QID - catalog, extras, 236a's/236b's/240's and this task's staging files, web/data/
   sites.json; catalog.slug(name) -> id) + the pool (the six plain-phrase forms +
   "filetype:bitmap", srnamespace 6, srlimit 40, deduped; gates = keep() + the caption names the
   city + Public domain + >= 4000 px; EYEBALL every 1280-px thumb of every gate-pass item - the
   pool gate is a substring match: the fit/ PITFALLS entry). The 175 /tmp scripts are the
   templates, but /tmp trees get wiped by the loop maintenance - if gone, the 175 DECISIONS entry
   carries the full recipe.
3. Landing mirrors 176: module edit -> --verify (expect 2 QIDs, no FLAG/TRAP on the new one;
   transcript verbatim into the lead doc's QID section) -> --dry -> stage -> --check (transcript;
   the count becomes "2 views / 2 site rows so far of the final five") -> lead-doc city section
   (STAGED bullet + DROP list + QID-facts paragraph; update the Not-done-yet pointer) -> --golden
   (2/2/2) -> tests (key list, SITES/years/points/named tables, the date check; the negative
   control STAYS on files[0] = the Omaha row, the batch4 "Denver row" pattern) -> module tests ->
   the FULL suite in-session (restore any re-encoded 307d PNGs first, R5) -> commit.
4. Then Columbus (3/5), Memphis (4/5), then one more from the collection's search order (5/5);
   the Staging section ends at the total (25 = 16 + 4 + 5, or a recorded shortfall) with the 236c
   note.

**Rules (unchanged):** never write the canonical files (236c); 236a's/236b's/240's files read-only;
live commands under .venv/bin/python (module top stays stdlib-only); the golden is the contract
(--golden only for an intended change); tests never bind fixed ports or write outside the project
and /tmp; every full-suite run re-encodes up to ten docs/site_flow/307d_*.png - restore main's
bytes before committing (R5); run the suite in-session (blocking), never nohup'd past the session
(the 174 driver-kill lesson).
