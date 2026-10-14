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
(2026-10-14, iteration 177, agent c - **INDIANAPOLIS RESEARCH complete; the LANDING is this
session's one step** (city 2/5). The Omaha landing is committed (driver commit 01de446; 177
re-verified in-session: module tests 5/5, --check 1/1/1 green, tree clean - nothing left from
176's uncommitted tree). The full research record and landing spec are in the 177 DECISIONS
entry; the QID/pool scripts, the full-res downloads and crops survive in /tmp (aw241_indy_*).

**INDIANAPOLIS research verdicts (details in the 177 DECISIONS entry):**
- **QID = Q6346** (NOT Q16556 - my first-guess was live-verified to be **Phoenix**: the
  first-guess mislabel trap). Label "Indianapolis"; P625 ONE value (-86.158055555556,
  39.768611111111, ~31 m) - no refinement; P373 = the STRING "Indianapolis" (the usual US
  quirk, even bare - no "city, state" form) -> place "Marion County, Indiana" (P131 = Q506230
  Marion County only); P17 = Q30; enwiki = "Indianapolis" (BARE - no state suffix, unlike
  Omaha) -> wikipedia https://en.wikipedia.org/wiki/Indianapolis. Name search at limit 5 AND
  20: first P625 hit = Q6346 itself at BOTH limits -> NO TRAP (in-city institutions - IMA,
  Eskenazi Hospital, Indy Art Center - the USS Indianapolis sinking spot, the Speedway
  facilities and the Oklahoma namesake never come first). No existing site holds Q6346 (all
  catalog/extras/236a/236b/240 extras files and web/data/sites.json clean). slug =
  "indianapolis" -> **site id indianapolis-q6346**.
- **PICK = page 1 of the E. G. Spink Company sheet** (DPLA item
  d442b7431e1f90b2c13fb4f957e8026f, contributed by the Indiana State Library; title "Bird's-eye
  view of Indianapolis showing Spink apartments, hotels, office and industrial buildings",
  11153x7986, Public domain NoC-US): the ONLY whole-city view in the 43-row pool (41 gate-fail
  drops + the page-2 same-sheet text page) and the ONLY scan of the sheet on Commons (no
  LOC-mirror found in four extra searches). Near-vertical: vantage from the south (the White
  River band along the bottom edge, Union Station + Hotel Spink lower-centre, the grid up to
  the State Fair Grounds at the top; no horizon band). The banners print NO year; the Commons
  page date is EMPTY; **drawing year = 1925** (ISL "Date of Original" 1925 + the sheet's own
  page-2 tax table 1919-1924 / Dec-31-1923 appraisal; the ISL shelf label "912.772 IMaI25e
  (1925)" is printed on the sheet's lower right). **1925 is exactly commons.MAX_YEAR - keep()
  passes at the boundary (y <= MAX_YEAR); do NOT "correct" it to another year.** The sheet is
  a real-estate promo (ISL subject: Advertisements) - recorded; it is still a whole-city view
  per its own title.

**Landing, exact steps (mirrors 176; live commands under .venv/bin/python):**
1. Module edit (fit/src_us_birdseye_batch5.py): SITES["Q6346"] = dict(id="indianapolis-q6346",
   name="Indianapolis", named="Indianapolis", lon=-86.158055555556, lat=39.768611111111,
   place="Marion County, Indiana", region="United States", kind="town",
   wikipedia="https://en.wikipedia.org/wiki/Indianapolis", note=<the staged view's apparent
   angle: near-vertical, vantage from the south across the grid to the State Fair Grounds,
   Union Station / White River at the bottom; the city grid fills the sheet beyond the 2000 m
   town box -> the fit is likely to end a review item, the 236a NY-1811 / DC-ring precedent>)
   with the full QID-facts comment (the 175/176 SITES-comment shape: the Q6346 facts, the
   Q16556=Phoenix mislabel caught, the name-search verdict, the no-collision check);
   SPINK_1925 = [("File:Bird's-eye view of Indianapolis showing Spink apartments, hotels,
   office and industrial buildings - DPLA - d442b7431e1f90b2c13fb4f957e8026f (page 1).jpg",
   "Q6346", "Indianapolis", dict(date=1925))] (the Zwolle-style swap: the page has no date, so
   the row's date = 1925 and date_commons = the page's empty value);
   SOURCES["indianapolis_1925"] = dict(rows=SPINK_1925, p="birdseye",
   label="{name}, the E. G. Spink Company bird's-eye view (1925)"); header comment marks
   Indianapolis LANDED (city 2 of 5).
2. --verify (live): expect 2 QIDs (Q43199, Q6346), NO FLAG / NO TRAP on Q6346 (first
   name-search hit = itself); P625 printed = the table point. Copy the transcript VERBATIM
   into the lead doc's QID section.
3. --dry then stage (live commons.info re-check): expect "staged: 1 new sites, 1 new pictures"
   (+ the build line naming indianapolis-q6346); keep() passes AT the boundary (1925 <= 1925);
   the caption gate passes (the title prints "Indianapolis"); the file row gets year=1925,
   date=1925, date_commons="" (the page has no date).
4. --check (offline): expect both rows PASS caption_coords + "evidence: 2 rows, 2 pass, 0
   fail, 0 no-tie", zero join lines. Copy the transcript VERBATIM into the lead doc's Staging
   section (running count becomes "2 views / 2 site rows so far of the final five").
5. Lead doc (docs/lead_us_birdseye_batch5.md): the Indianapolis city section = the STAGED
   bullet (page 1: the banner wording, the ISL shelf label, the 1925 date evidence = the ISL
   record + the sheet's own tax table / appraisal, page 2 = the same-sheet text page) + the
   full 42-item DROP list (the 41 gate-fails grouped as in the 177 entry + page 2) + the
   QID-facts paragraph (incl. the Q16556=Phoenix mislabel) + the verbatim --verify transcript;
   update the Not-done-yet pointer (next: Columbus, Memphis, then the collection's search
   order; New Orleans skipped - 236b's).
6. --golden (2/2/2; date_commons normalizes to "0000-00-00" in the golden - intended).
7. Tests (tests/test_src_us_birdseye_batch5.py, the 236b/240 shape): test 1's key list += the
   Indianapolis PASS line; test 4's SITES/years/points/named tables += Indianapolis (year
   1925, point -86.158055555556/39.768611111111, named "Indianapolis") + the date check WITH
   the Zwolle swap (year 1925 + date_commons "0000-00-00"); test 5's negative control STAYS on
   files[0] = the Omaha row (the batch4 "Denver row" pattern - do NOT rebind it).
8. Module tests (expect 6/6) -> FULL suite in-session BLOCKING (.venv/bin/python -m pytest -q;
   R2: the driver's 241 baseline is 0 failing - any red first goes to the PITFALLS Esri-flake /
   pytest-temp-tree entries + an isolated re-run). The run re-encodes up to ten
   docs/site_flow/307d_*.png: restore main's bytes (git checkout -- docs/site_flow/) BEFORE the
   commit (R5). Commit: "241: Indianapolis landed (batch-5 city 2/5) - the 1925 E. G. Spink
   Company sheet (DPLA/Indiana State Library) - the only whole-city view in the pool".
9. Then: COLUMBUS research (3/5) next session, Memphis (4/5), then one more from the
   collection's search order (5/5); the Staging section ends at the total (25 = 16 + 4 + 5, or
   a recorded shortfall) with the 236c note.

**Rules (unchanged):** never write the canonical files (236c); 236a's/236b's/240's files
read-only; live commands under .venv/bin/python (module top stays stdlib-only); the golden is
the contract (--golden only for an intended change); tests never bind fixed ports or write
outside the project and /tmp; every full-suite run re-encodes up to ten
docs/site_flow/307d_*.png - restore main's bytes before committing (R5); run the suite
in-session (blocking), never nohup'd past the session (the 174 driver-kill lesson).
