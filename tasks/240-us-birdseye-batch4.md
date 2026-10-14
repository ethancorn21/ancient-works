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
socket-blocking fixture; the PASS-key list; the SITES-id / extras-id / year / point / named
tables; the golden compare) -> module tests -> the FULL suite (restore the 307d pngs first,
below) -> commit. The lead doc's Staging section ends with the Not-done-yet pointer to 241 naming
the next two or three candidates (the 236b precedent).

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

**St. Paul is RESEARCHED (iteration 162 - the full record is the DECISIONS entry "240 DECISION:
iteration 162" and the hand-over below): QID Q28848, pick = the 1906 Robert M. Saint near-
vertical sheet (LOC 75694650). Minneapolis is RESEARCHED (iteration 165 - the DECISIONS entry
"240 DECISION: iteration 165" and the hand-over below): QID Q36091, pick = the 1885 W. V.
Herancourt / I. Monasch near-vertical sheet (LOC 75694644).** Cleveland: NOT yet researched. Run
the per-city playbook. (The pool search shows which survived the gates; do not trust this note,
verify live.)


## Hand-over
(2026-10-14, iteration 168, agent c - session 9 COMPLETE: the R5 restore of the seven 307d pngs
re-encoded by the iteration-167 full-suite run is committed (9620f1f); the Minneapolis landing
itself already rides in the driver's commit 6cb8ca9 (session 8's uncommitted work). THREE of FOUR
cities are landed and committed: Denver (Q16554), St. Paul (Q28848), Minneapolis (Q36091). The
branch is clean; the last full suite (167) = 182 passed / 1 skipped / 0 failed = the 164 baseline.
NEXT = session 10: CLEVELAND (city 4) RESEARCH.)

**State (verified this session):**
- Staged in the batch4 files (3/3/3 rows): `denver-q16554` (the 1908 Birdseye View Publishing Co.
  sheet, `File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg`, 19338x13294),
  `st-paul-q28848` (the 1906 Robert M. Saint sheet, `File:Bird's eye view of St. Paul, Minnesota.
  LOC 75694650.jpg`), `minneapolis-q36091` (the 1885 W. V. Herancourt / I. Monasch sheet,
  `File:Minneapolis, Minnesota. LOC 75694644.jpg`, 13152x9408). Lead doc
  docs/lead_us_birdseye_batch4.md: three city sections + Staging section (3 views / 3 site rows;
  the Not-done-yet pointer names only CLEVELAND for 240). Golden 3/3/3. batch4 tests 5/5
  (re-run green this session, 2.34 s). Module fit/src_us_birdseye_batch4.py: SITES at line 79
  (3 QIDs), no SHARED machinery, known_sites() at line 276 reads SITES_JSONL + EXTRAS + 236a's
  extras + 236b's extras + 241's (absent) batch5 extras + web/data/sites.json.
- **main has moved past the 164 merge-base (8678c8a)** - agent a's 238 work is on main (its
  hand-over says DONE). There is NO merge of main onto this branch yet (no merge commit on
  agent/c); the driver's main->branch sync is the driver's job - I never merge/rebase myself
  (team-mode rule). FIRST CHECK OF SESSION 10: `git diff main --stat -- docs/site_flow/` - if
  main's 307d bytes moved again since my restore (main's own re-encode jitter; task 242 will
  settle it), `git checkout main -- docs/site_flow/` again BEFORE running anything that hashes
  docs/ (the full suite does). My restore used main's current bytes, so a merge into current
  main sees identical bytes on both sides for all seven files (no binary conflict).
- **/tmp (still alive at session end; wiper-prone - rebuild recipes: entry-165 pool/QID scripts,
  entry-166 the 13152 px original crops):** /tmp/aw240_mpls_qid.py (the QID script template -
  sys.path already points at this checkout), /tmp/aw240_mpls_pool.py (the pool template),
  /tmp/aw240_mpls_thumbs.py + /tmp/aw240_mpls_thumbs/, the /tmp/aw240_m885_* crops (the
  Minneapolis original + the 500 px grid reference), the /tmp/aw240_sp_* St. Paul set, the
  verify/dry/stage/check transcripts for iterations 160/163/167, the suite logs 161-167. The
  /tmp/aw236b_b3_dvr* (Denver) research set is still present too.

**NEXT (session 10) - CLEVELAND (city 4) RESEARCH, in this exact order, all under
.venv/bin/python:**
1. **QID playbook** (clone /tmp/aw240_mpls_qid.py -> /tmp/aw240_cle_qid.py; save the transcripts
   /tmp/aw240_cle_qid_168.txt + _qid2_168.txt): first-guess QID from a "Cleveland, Ohio" search
   + the label check - the mislabel trap has now hit 3 of 4 cities (Denver's Q3101 a person,
   St. Paul's Q16842 a person, Minneapolis's Q3094 a Romanian monastery); every P625 value with
   precision (flag any >50 km from the downtown); P373 (a string is the usual US quirk -
   Cleveland is in Cuyahoga County, Ohio -> place "Cuyahoga County, Ohio"); P131 with labels,
   P17, enwiki; the name-search "Cleveland" limit 20 with the distance from the city's P625 for
   EVERY P625-bearing hit (in-city institution traps - Cleveland has big hospitals, a big
   university, an airport; other-state namesakes: Cleveland TN (the big one near Knoxville),
   TX, MS, WI; foreign: Cleveland, County Monaghan, Ireland - record the FIRST P625 hit: if it
   is NOT the city itself it is the TRAP line the --verify must show); no existing site holds
   the QID (catalog sites.jsonl, catalog/extras.jsonl, 236a's extras_us_cities.jsonl, 236b's
   extras_us_birdseye.jsonl, 241's batch5 file when it exists, web/data/sites.json); verify the
   slug with the module's own slug rule (catalog.slug("Cleveland") - expect "cleveland").
2. **Pool** (clone /tmp/aw240_mpls_pool.py -> /tmp/aw240_cle_pool.py with CITIES=["Cleveland"];
   the six plain-phrase forms + `filetype:bitmap`, srnamespace 6, srlimit 40; dedupe; the gates:
   caption names the city AND commons.keep() judged AFTER any known-date swap AND license
   "Public domain" AND width >= 4000; eyeball every good item's 1280 px thumb one by one -
   /tmp/aw240_mpls_thumbs.py is the thumb template). The pick = the steepest (near-vertical),
   best-scanned whole-city view (the caption names the city). Cleveland sits on the Cuyahoga at
   the Lake Erie shore - check every sheet's lake side and orientation; MEASURE the apparent-
   angle claim before writing it (the entry-166 grid-crop recipe: download the original, crop
   full + quadrants + river zone, draw a 500 px white grid with coordinate labels).
3. **Record:** the full DECISIONS entry (QID facts + pool counts + the eyeball verdicts with
   per-item drop reasons) + a hand-over pointing at session 11's landing edit list.

**Then LANDING (session 11, the proven pattern - the entry-167 steps verbatim):** module edit
(the SITES QID entry with the full comment block + the CLEVELAND_<YEAR> row-list + the SOURCES
entry + docstring/SITES-header updates) -> --verify (4 QIDs; save the transcript verbatim for
the lead doc) -> --dry (expect 1 new site, 1 new picture) -> stage (live commons.info re-check;
if the pick vanished or is no longer PD, take the next-best pool candidate and record the swap)
-> --check (expect 4/4 PASS caption_coords, no join problems; append the transcript to the
Staging section) -> lead doc (the Cleveland section: STAGED bullet + the full DROP list + the
QID-facts paragraph + the --verify transcript verbatim; the Staging section to 4 views / 4
site rows; the Not-done-yet pointer then names only 241's batch 5 - the prep R9 candidate order
after Cleveland is Omaha (skipped in 236b with no recorded drop reason - re-run its pool search
and record the verdict), Indianapolis, Columbus, Memphis - confirm against the live search
order when writing it) -> --golden (4/4/4) -> test extension (the same substitution pattern -
the PASS-key list, the SITES-id/years/points/named dicts, the date assertion - keep the file
pure ASCII) -> batch4 tests -> the FULL suite (~9 min; start it only after ALL edits per R6,
then `git checkout main -- docs/site_flow/` (R5) and commit "240: Cleveland landed (batch 4
city 4) - the <YEAR> <artist> sheet". Baseline: 182P/1S/0F at 164 with main HEAD 8678c8a - if
main has moved, diff the failing SET, not the number) -> commit.

**CLOSE (session 12, after Cleveland lands):** the full-suite tail = the baseline (diff the
failing set if main has moved); --check ends all PASS, no join problems; the four staged
ids/QIDs collide with nothing (the known_sites() guard + the test); tick acceptance boxes 1-4
(each after its test passes); the lead doc's Staging section final (4 views / 4 site rows; the
Not-done-yet names only 241); box 5 (Denver, researched) stays ticked - it was re-verified live
by the 167 --verify run (Denver clean). Status: done.

**Rules that bite (unchanged from the task Notes):** never write the canonical files (236c);
236a's and 236b's files are read-only (the module's cross-checks enforce); live commands under
.venv/bin/python (the module top stays stdlib-only; /tmp scripts repoint sys.path at this
checkout); the golden regenerates only via --golden; tests never bind fixed network ports or
write outside the project and the temp dir; every full-suite run re-encodes up to ten
docs/site_flow/307d_*.png - restore main's bytes before EVERY commit that follows a run (R5);
never edit suite-hashed files mid-run (R6: data/ minus raw, web/data top level, docs/, specs/,
tests/ are snapshotted - finish all edits, THEN run, restore, commit; DECISIONS.md and tasks/
are NOT in the snapshot set, so the bookkeeping can be written while the suite runs); /tmp
artifacts are wiper-prone - the rebuild recipes are in the DECISIONS records; never git
merge/rebase/reset/stash or switch branches (team mode - the driver syncs main; this prompt
asks for no merge work).
