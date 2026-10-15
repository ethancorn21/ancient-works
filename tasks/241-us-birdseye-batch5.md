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
(2026-10-14, iteration 180, agent c - **COLUMBUS LANDING (city 3/5) is DONE on disk but NOT yet
committed** - the next agent's first step is the commit, then MEMPHIS research (city 4/5). The
180 DECISIONS entry carries the full landing record; the per-city playbook is in the task Notes
above and unchanged.

**State after 180 (UNCOMMITTED - `git status --short` should show exactly these 7 files):**
- fit/src_us_birdseye_batch5.py: SITES = {Q43199 Omaha, Q6346 Indianapolis, Q16567 Columbus} all
  LANDED in the comments (Q16567: id columbus-q16567, point = verified P625
  -83.00055555555555/39.96222222222222, place "Franklin County, Ohio", wikipedia
  https://en.wikipedia.org/wiki/Columbus,_Ohio, note = the true-oblique angle paragraph - a
  sky/horizon band along the sheet's top, unlike the Omaha/Indy near-verticals);
  BAILEY_1872 = [("File:1872 Birds Eye View of Columbus Ohio - alternate.png", "Q16567",
  "Columbus", dict())] (NO Zwolle swap - page date 1872 = the banner's year, the Omaha pattern);
  SOURCES["columbus_1872"] label "{name}, the H. H. & O. H. Bailey bird's-eye view (1872)".
- data/catalog/extras_us_birdseye_batch5.jsonl + data/commons/files_us_birdseye_batch5.jsonl +
  classified_us_birdseye_batch5.jsonl = 3/3/3 (Omaha, Indianapolis, Columbus).
- docs/lead_us_birdseye_batch5.md: new Columbus section (STAGED bullet + the three-scan
  same-sheet note + the full 87-item DROP list + the extra probes + the QID-facts paragraph
  incl. Q1405=Augustus and the measured 1116 m / 262.9 km / 625 km distances), the session-8
  --verify transcript in the QID section, the Staging section at "3 views / 3 site rows" with
  the session-8 --check verbatim, Not-done-yet -> Memphis then the search order.
- tests/golden/src_us_birdseye_batch5_sample.json: 3/3/3 (regenerated via the module's --golden).
- tests/test_src_us_birdseye_batch5.py: PASS key += the columbus key; SITES/points/named/years
  tables += Columbus (year 1872, point -83.00055555555555/39.96222222222222, named "Columbus",
  date "1872" with NO date_commons); the negative control STAYS on files[0] = the Omaha row.

**Tests when last run (all in-session this iteration):** module tests 5/5 (2.37 s); FULL suite
`--ignore=tests/test_gate.py -p no:cacheprovider` = **187 passed, 1 skipped, 0 failed** (535 s)
- green, including test_fit_queue (red in the driver's 2026-10-13 run - flaky/state-dependent;
not 241's to fix; the suite count moved 190->187 across team merges, so compare against the
driver's baseline at done-claim time, not memory). The suite re-encoded 5 of the ten
docs/site_flow/307d_*.png (A_1-card, A_4-saved, A_5-reload, B_1-card, B_5-reload) - **already
restored to main's bytes** before this hand-over (R5); the 7-file list above excludes them.

**Next step 1 (one command):** commit the landing exactly as-is:
`git add fit/src_us_birdseye_batch5.py data/catalog/extras_us_birdseye_batch5.jsonl
data/commons/files_us_birdseye_batch5.jsonl data/commons/classified_us_birdseye_batch5.jsonl
docs/lead_us_birdseye_batch5.md tests/test_src_us_birdseye_batch5.py
tests/golden/src_us_birdseye_batch5_sample.json && git commit -m "241: Columbus (Ohio) landed
(batch-5 city 3/5) - the 1872 H. H. & O. H. Bailey sheet (alternate.png - the best of the three
scans)"`. First verify `git status --short` shows only those 7 files plus this hand-over's
memory files (the driver/harness saved the tree; the working tree IS the state above).

**Next step 2: MEMPHIS RESEARCH (city 4/5)** - the 176-180 pattern:
(1) RESEARCH (live, .venv/bin/python; the /tmp scripts still exist and are the templates:
aw241_col_qid.py (the wbgetentities pattern), aw241_col_pool.py (the six plain-phrase forms +
filetype:bitmap, srnamespace 6, srlimit 40; gates = keep + caption-names-city + Public domain +
>= 4000 px), aw241_col_thumbs.py (1280-px thumbs) - adapt the city name): the QID - **do not
trust a first-guess QID from memory** (the live trap: Q1405=Augustus, Q16556=Phoenix) - look it
up via name search, then verify the label, EVERY P625 value, P373 (a string is the usual US
quirk - write the place from county + state), P131, P17, enwiki, the first name-search hit with
P625 at limit 5 AND limit 20 (R5); measure every distance claim with fit/evidence.hav_m before
writing it; check no existing site holds the QID (grep the catalog, extras, 236a's/236b's/240's
extras, web/data/sites.json for the QID and case-insensitive "memphis"); then the pool (eyeball
EVERY gate-pass item's thumb one by one; disambiguate each sheet from its caption: the state in
the banner + the LCCN - Memphis TN vs Memphis MO/Ink/... mixing is expected). The pick = the
steepest, best-scanned whole-city view (one row per sheet; stage the sheet's best scan - the
1872-Bailey/1854-SF precedent: the better non-LOC scan when the LOC one is inferior).
(2) LANDING: module edit (SITES + <CITY>_<YEAR> + SOURCES + header/SITES comments, city 4 of 5)
-> --verify (transcript verbatim into the lead-doc QID section) -> --dry -> stage (1 new site /
1 new picture) -> --check (expect "evidence: 4 rows, 4 pass, 0 fail, 0 no-tie", zero join lines;
verbatim into the lead doc) -> lead-doc Memphis section (STAGED bullet + full DROP list + QID
facts; Staging count "4 views / 4 site rows"; Not-done-yet -> city 5 = the collection's search
order past Memphis - "...New Orleans, ...", with New Orleans SKIPPED (236b already staged it))
-> --golden (4/4/4) -> test extension (PASS key, tables, year, point, named, date pattern)
-> module tests 5/5 -> FULL suite in-session BLOCKING (restore the re-encoded 307d pngs first)
-> commit.

**After Memphis: city 5/5** from the collection's search order (any US city not in the skip
list: 236a's four, 236b's sixteen, 240's four, this task's staged cities, the catalog,
web/data/sites.json), then the close step (prep notes section 2, step 6: final suite = baseline,
--check ends at 5/5, tick the boxes, Status: done).

**Rules (unchanged):** never write the canonical files (236c); 236a's/236b's/240's files
read-only; live commands under .venv/bin/python (module top stays stdlib-only); the golden is
the contract (--golden only for an intended change); tests never bind fixed ports or write
outside the project and /tmp; every full-suite run re-encodes up to ten
docs/site_flow/307d_*.png - restore main's bytes before committing (R5); run the suite
in-session (blocking), never nohup'd past the session (the 174 driver-kill lesson).

**/tmp artifacts from this session (loop maintenance may wipe them; the 179/180 DECISIONS
entries carry the full record):** aw241_col_qid.py/.log, aw241_col_pool.py/.json/.log,
aw241_col_thumbs.py, /tmp/aw241_col_thumbs/ (11 thumbs + zoom crops + 82_1920.jpg),
aw241_col_verify_180.log, aw241_col_dry_180.log, aw241_col_stage_180.log,
aw241_col_check_180.log, aw241_suite_180.log.
