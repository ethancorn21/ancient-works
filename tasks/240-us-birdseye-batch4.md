Status: open
Depends on: 236b
Touches: fit/src_us_birdseye_batch4.py, data/catalog/extras_us_birdseye_batch4.jsonl, data/commons/files_us_birdseye_batch4.jsonl, data/commons/classified_us_birdseye_batch4.jsonl, docs/lead_us_birdseye_batch4.md, tests/test_src_us_birdseye_batch4.py, tests/golden/src_us_birdseye_batch4_sample.json

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
- [ ] Denver is staged as researched (Q16554; the 1908 Birdseye View Publishing Co. sheet,
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
(2026-10-14, iteration 160, agent c - session 1 of 240; the merge is STAGED but NOT committed, the
Denver landing is built in the working tree but untested - next session: commit the merge, record
the baseline, write the test + golden, run the suites, commit the landing.)

**State NOW (all uncommitted; the harness saved the working tree):**
0. **Working-tree noise to clear first:** the background baseline suite (see the Tests note below) was still running when the session ended and re-encoded 5 of the 307d pngs in the working tree (307d_A_1-card, A_4-saved, A_5-reload, B_4-saved, B_5-reload - `MM`/` M` in git status vs the staged main's bytes). The merge commit (step 1) stages only the index (main's bytes), so those re-encodes stay out of it; then **`git checkout -- docs/site_flow/`** to restore them before any further work (R5).
1. **MERGE PENDING:** `git merge main` was run; the 4 binary conflicts (docs/site_flow/
   307d_A_4-saved.png, A_5-reload.png, B_4-saved.png, B_5-reload.png) were resolved by taking
   MAIN's bytes (the other agents' finished 307b work; our side was only test-re-encode jitter -
   the R5 rule). Resolution is STAGED (git checkout main -- <the 4> + git add); PROGRESS/DECISIONS/
   PITFALLS/docs/batch.md/tasks/212/tasks/235/tests/test_fit_queue.py/web/data/review.json
   auto-merged. **First act next session: `git commit -m "merge main into agent/c: 307d png
   conflicts resolved keeping main's bytes (test re-encode jitter)"`** (MERGE_HEAD is set; no other
   changes staged - check with git status).
2. **The batch4 module is BUILT and LIVE-VERIFIED:** fit/src_us_birdseye_batch4.py (full template
   copy with the 5 prep changes: batch4 paths + EXTRAS_BIRDS_236B/_BATCH5 constants; known_sites()
   reads the catalog + extras + 236a's + 236b's + 241's extras + web sites; NO SHARED_SITES;
   by/source strings say fit/src_us_birdseye_batch4.py; docstring names the template). SITES has
   Denver only (Q16554, denver-q16554, point (-104.984722, 39.739167), place "Denver County,
   Colorado"); SOURCES has denver_1908 -> File:Bird's eye view of Denver, Colorado, 1908. LOC
   75693133.jpg.
3. **Denver is STAGED** (live runs all passed, transcripts in /tmp, may be wiped):
   - `--verify` (live Wikidata): Q16554 'Denver'; ONE P625 (-104.98472222222, 39.739166666667) =
     table point, NO FLAG; P373 string 'Denver, Colorado'; P131 Colorado + Denver County; enwiki
     'Denver'; first name-search hit with P625 = Q16554 itself, NO TRAP. The verbatim transcript
     is already spliced into the lead doc's QID section (/tmp/aw240_verify_160.txt).
   - `--dry` + stage: "1 new sites, 1 new pictures", build (236c): denver-q16554. The pick is
     live on Commons, keep() + caption gate + PD + 19338 px all pass; page date 1908 = drawing
     year (no Zwolle swap; no date_commons on the row).
   - `--check` (offline): exit 0, `PASS caption_coords denver-q16554|File:Bird's eye view of
     Denver, Colorado, 1908. LOC 75693133.jpg`, `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`, no
     join problems. Staged files: extras_us_birdseye_batch4.jsonl (1 row), files_us_birdseye_
     batch4.jsonl (1 row: year 1908, Public domain, by/source fit/src_us_birdseye_batch4.py
     denver_1908, evidence caption_coords dist 0), classified_..._batch4.jsonl (1 row p_birdseye
     1.0 by hand). Verified byte-checked earlier this session (all good).
   - Q16554 held by no existing site (catalog/extras/236a/236b extras + web/data/sites.json all
     clean at session start); slug("Denver") = "denver" verified.
   - The two un-eyeballed 194 thumbs were eyeballed OFFLINE this session (they survive in
     /tmp/aw236b_b3_dvr_thumbs/): Arbor-Day Colfax avenue = district close-up (Colfax corridor +
     Montclair subdivision, real-estate souvenir sheet); the "Healer" = a PHOTOGRAPH (street-car
     crowd, title puns). Both drop wordings are finalized in the lead doc.
4. **Lead doc WRITTEN:** docs/lead_us_birdseye_batch4.md (complete for Denver: Fetch route, QID
   section with the verbatim transcript, evidence field, the Denver section with STAGED + full
   16-item DROP list + QID facts, Staging and checks with the verbatim --check transcript, and
   the **Not-done-yet pointer to 241** naming the remaining 3 of THIS task (St. Paul,
   Minneapolis, Cleveland) and 241's next candidates **Omaha (skipped in 236b with no recorded
   drop reason), Indianapolis, Columbus, Memphis** per the 181 candidate order).

**Tests: the baseline suite run is DOUBTFUL - re-establish it.** A full suite was started in the
background right after the merge (.venv/bin/python -m pytest -q -p no:cacheprovider ->
/tmp/aw240_suite_base_160.log; still running at the last check, ~7+ min in) BUT I then created
files under data/ and docs/ MID-RUN - the suite's write-surface integrity snapshot may make that
run show spurious failures (R6). Next session: read the tail of the log; if it finished and its
failures match the known set (candidate: tests/test_fit_queue.py::test_placement_gestures_and_
save_in_the_browser was the one red in this checkout's 2026-10-13 driver run, 1F/159P/1S of 161;
main since grew a few tests via 307b work - the merged-tree baseline should be ~178-181 tests),
record it as the R1 baseline (disclose the caveat). Otherwise RE-RUN the full suite now (after
the merge commit, before adding the new test file) and record THAT as the baseline. The 236b
full-main-tree closeout baseline was 177P/1S/0F.

**Exact next steps (one session should do all of 1-4; St. Paul is the following session pair):**
1. Commit the pending merge (box 0, above). git status first; only the merge may be in flight.
2. Establish the suite baseline as above; restore any re-encoded docs/site_flow/307d_*.png to
   main's bytes (R5) before any commit.
3. **Write tests/test_src_us_birdseye_batch4.py** mirroring tests/test_src_us_birdseye.py (311
   lines, 6 offline tests; its header rationale can be adapted). Spec = prep notes section 3:
   (a) autouse no_network fixture (monkeypatch socket.socket/create_connection/getaddrinfo to
   raise - verbatim 236b pattern); (b) test_check_staged: check_staged() == 0, no "join:" line,
   evidence "1 rows, 1 pass, 0 fail, 0 no-tie", the explicit PASS key list = ["denver-q16554|
   File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg"] (grows to 4 at close, this
   key first); (c) test_check_staged_three_states: monkeypatch FILES_CANONICAL/EXTRAS/WEB_SITES/
   SITES_JSONL to tmp_path files (236b's exact pattern): pre-merge absent -> 0; identical
   content -> 0 no-op; same (site,title) key different row -> 1 naming exactly "join: staged
   title already in the canonical files.jsonl: <k>" and no other join line; (d) test_sites_table_
   and_staged_rows: SITES ids == slug-rule ids (denver-q16554 now; st-paul-q..., minneapolis-q...
   , cleveland-q... at close), region "United States", kind "town", non-empty named/note, the
   extras file == EXACTLY the SITES set (no owner-city rows at all), files rows == SOURCES rows
   one per city, per-title year table (1908 now), evidence point == site's own point (site==place
   == table point), named_place = caption name, dist_m 0.0, license Public domain, no Zwolle
   swap assertions needed (the Denver row has no date_commons); (e) test_evidence_offline_and_
   negative_control: evidence.check(FILES_BIRDS, NO_BOOKS, catalog=EXTRAS_BIRDS) exit 0 all
   pass; temp one-row copy with a foreign point (Venice 12.33, 45.44 - the 236b control) must
   FAIL "does not reproduce (<d> m)"; (f) test_golden_sample_matches_staged_rows: the golden
   equals the normalized staged rows exactly. Use the module's real constants via import
   (sys.path fit/ or importlib - mirror the 236b test file's imports exactly; its header
   docstring carries the project rationale).
4. **Generate the golden:** `.venv/bin/python fit/src_us_birdseye_batch4.py --golden` ->
   tests/golden/src_us_birdseye_batch4_sample.json (1/1/1 rows). Run the new module test (expect
   6 passed), then the FULL suite (.venv/bin/python -m pytest -q -p no:cacheprovider; expect =
   baseline + 6, the known red(s) disclosed not fixed - the fix belongs to 235/212's chain),
   restore the re-encoded 307d pngs to main's bytes, and COMMIT the Denver landing (module, the
   3 staging jsonl, lead doc, test, golden; message "240: Denver landed (batch 4 city 1) - the
   1908 Birdseye View Publishing Co. sheet..." per the per-city commit convention).
5. Then St. Paul per the per-city playbook in the Notes (RESEARCH: QID + pool - St. Paul has the
   name-search traps: other St. Pauls (LA, SC) + in-city institutions; then LANDING exactly as
   Denver: module edit (SITES + SOURCES + a batch-4-city-2 comment) -> --verify (append the
   transcript to the lead doc's QID section) -> --dry -> stage -> --check (append the transcript
   to Staging) -> lead-doc St. Paul section (STAGED + full DROP list + QID facts) -> --golden ->
   extend test keys/tables/counts -> module tests -> full suite (restore pngs) -> commit).

**Rules that bite (unchanged from the task Notes):** never write canonical files (236c); 236a's
and 236b's files are read-only (the module's cross-check enforces); live commands under
.venv/bin/python (module top stdlib-only); golden regenerates only via --golden; tests never
bind fixed ports or write outside project + temp; every full-suite run re-encodes up to ten
307d pngs - restore main's bytes before EVERY commit (R5) and never edit suite-hashed files
mid-run (R6: finish all edits, THEN run, restore, commit). /tmp artifacts (aw236b_b3_dvr*,
aw240_verify/dry/stage/check_160.*) are wiper-prone; the recipes + this note rebuild them.

**Box status:** none ticked yet (box 5's verify-before-stage part is DONE; boxes tick only after
their tests pass). Re-read when picking up: fit/src_us_birdseye_batch4.py (fresh eyes on the
shared-machinery removal - it must stay a clean mechanical copy of the template),
tests/test_src_us_birdseye.py (the spec to mirror), the lead doc (verify the DROP list against
/tmp/aw236b_b3_dvr.json if it survives).
