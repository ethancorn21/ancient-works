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
(2026-10-14, iteration 184, agent c) **City 5 RESEARCH complete: Albuquerque DROPPED (no drawn
bird's-eye view in the Commons mirror), Portland (Oregon) researched - the pick is the 1890
J. McI. Wood sheet (File:Portland, Oregon 1890 Perspective Birds-eye-view Map.jpg, 13760x9520,
Public domain). NEXT: the Portland landing (one session), then the close.**

**State (all verified in the 184 session):**
- FOUR cities LANDED + committed (unchanged): Omaha (Q43199, 1868 E. Ruger .tif), Indianapolis
  (Q6346, 1925 Spink page-1 .jpg), Columbus (Q16567, 1872 Bailey alternate.png), Memphis
  (Q16563, 1870 Ruger .jpg). Staging files 4/4/4, golden 4/4/4, lead doc at "4 views / 4 site
  rows". Tree clean (git status empty) at session start; no repo file changed this session
  (research only: DECISIONS.md + PITFALLS.md + this hand-over).
- FULL suite was green at exactly the 178 baseline when the four landed (187P/1S/0F with
  `--ignore=tests/test_gate.py`; 190P/1S/0F over 191 tests counting the 3 green test_gate
  tests standalone; the 183 entry has the decomposition). No suite has run since - the
  landing session runs the FULL suite again (expect the same: 187P/1S/0F on this tree, zero
  red; main may have grown - zero red is the criterion, and the only tolerated exception is
  test_fit_queue.py::test_placement_gestures_and_save_in_the_browser = agent a's in-flight 239).

**CITY 5 = Portland (Oregon), Q6106 - LANDED next session, then close.**
Research record (verbatim in the 184 DECISIONS entry; /tmp artifacts aw241_pdx_* and
aw241_city5_* - loop maintenance may wipe them, the DECISIONS entry is the record):
- Q6106 (live Wikidata, NO trap - Q6106 is the #1 search hit at both limits 5 and 20, the
  first hit with P625 at both): label "Portland"; P625 = ONE 31 m value
  (-122.67916666666666, 45.515) the downtown core, no refinement; P373 = the STRING
  "Portland, Oregon" (the usual US quirk) -> place "Multnomah County, Oregon" (P131 =
  Q450374 Multnomah (county seat) + Q484404 Clackamas + Q484538 Washington - the
  three-county pattern, like Columbus); P17 = Q30; enwiki "Portland, Oregon". Other
  Portlands never come first (Q49201 Maine 4081.9 km 2nd, CT 3991.2, IN 3089.3, MI 2998.2,
  AR 2980.8, TX 2969.3, Dorset EN, Australia 13324.1; in-city institutions PSU 0.5 km,
  University of Portland 7.4 km - all measured). No existing site holds Q6106 (grep clean
  in all seven files). id = **portland-q6106** (slug verified; a future Portland ME would
  be portland-q49201 - no collision, the id carries the QID).
- The pick: "File:Portland, Oregon 1890 Perspective Birds-eye-view Map.jpg" - 13760x9520,
  Public domain, page date 1890 = the banner (NO Zwolle swap), artist field "Library of
  Congress, Geography and Map Division" (a LOC Panoramic maps item), the caption (title)
  prints "Portland, Oregon". The hand-drawn hand-colored sheet, lower-centre cartouche
  "JAMES MCI. WOOD, REAL ESTATE AND INVESTMENT BROKER. / PORTLAND, OREGON. / 1890": drawn
  from a high vantage to the northwest looking southeast - the Willamette River diagonal
  upper-left to lower-right with the downtown grid both banks, a steel-truss railway
  bridge mid-sheet, river traffic, Mt. St. Helens + the Cascades a background mountain
  band at right, a sky band along the top, building vignettes framing the sheet (the
  Omaha/Indianapolis near-vertical class with a mountain horizon). The ONLY gate-pass
  drawn whole-city view of Portland OR in the pool: the 1903 LCCN91719502 photo (x2
  scans) and the 1908 LCCN2007662704 photo-panorama strip drop as photos; the 1880 J.K.
  Gill sheet (1742 px) and two NYPL 1880s scans (3072 px) drop on width; the rest of the
  55-row pool is the other Portlands (Maine 1876 x3 scans, Casco Bay 1906 x2), other
  cities (Port Townsend 1878 x2, Seattle 1878 - all "published/drawn by ..., Portland,
  Oregon" credits; Boston/Tacoma/Walla Walla/etc. postcards and photos), books and
  OCR hits - every item itemised in the 184 DECISIONS entry (full per-row flags in
  /tmp/aw241_pdx_pool.json if it survived).
- Albuquerque (the first probe) is DROPPED and needs its lead-doc section at the landing
  (the drop reason: six documented forms 0/0/0/0/0/0 - the Commons case-quirk, now a
  PITFALLS entry - plus the only LOC Panoramic item is the 1915 photographic "Panoram of
  Albuquerque, N. Mex LCCN2007662623.tif" 4563x697 strip, a photo; extended probes found
  no drawn sheet).

**LANDING (the 176-182 pattern, one step-set):** module edit (SITES["Q6106"] with the
verified P625 point + the staged view's apparent-angle note - northwest-oblique, grid
fills the sheet beyond the 2000 m town box + mountain horizon, likely a review item like
the other four; the Q6106 SITES comment with the full QID-facts
pattern used for the other four; PORTLAND_1890 row
("File:Portland, Oregon 1890 Perspective Birds-eye-view Map.jpg", "Q6106", "Portland",
dict()) - EMPTY extra dict, no Zwolle swap; SOURCES["portland_1890"] (label "the J. McI.
Wood perspective bird's-eye view (1890)"); header/SITES/source comments mark city 5
LANDED) -> `--verify` (save the exact output verbatim for the lead-doc QID section;
expect 5 QIDs, NO FLAG/TRAP for the new one) -> `--dry` -> stage (live commons.info
re-check; "1 new sites, 1 new pictures"; before staging re-search by title for
same-sheet mirrors and record the result) -> `--check` (expect "evidence: 5 rows, 5
pass, 0 fail, 0 no-tie", zero join lines; verbatim into the lead-doc Staging section) ->
lead-doc sections (the Albuquerque DROP section with its probe record + the Portland
STAGED bullet with the full DROP list + the QID-facts paragraph with the transcript;
Staging -> "5 views / 5 site rows" + the note that 236c consolidates and checks the 25
total = 16 + 4 + 5; Not-done-yet -> all five done) -> `--golden` (5/5/5, an intended
change) -> tests (PASS key + SITES/years/points/named tables += portland-q6106, the
1890 year, the (-122.67916666666666, 45.515) point, named "Portland"; golden docstring
count 5/5/5; the negative control stays on files[0] = the Omaha row) -> module tests
5/5 -> FULL suite in-session BLOCKING (expect 187P/1S/0F with
`--ignore=tests/test_gate.py` on this tree, zero red = the criterion; see the tolerated
exception above) -> R5 restore (`git checkout main -- docs/site_flow/307d_*.png`) ->
commit.

**CLOSE (same session as the landing, once city 5 is in):** final full suite = baseline
(zero red), `--check` ends at 5/5 PASS with no join problems, tick ALL FIVE acceptance
boxes (they are verified at that point), set `Status: done`. 236c consolidates the
staging into the canonical data and checks the 25 total - never write the canonical
files here.

**Rules (unchanged):** never write the canonical files (236c); 236a's/236b's/240's files
read-only (the module's cross-check enforces); live commands under .venv/bin/python
(module top stays stdlib-only; system python3 has no numpy); the golden is the contract
(--golden only for an intended change); tests never bind fixed network ports or write
outside the project and the temp dir; every full-suite run re-encodes up to ten
docs/site_flow/307d_*.png - restore main's bytes before committing (R5); run the suite
in-session (blocking), never nohup'd past the session (the 174 driver-kill lesson).
The new PITFALLS entry (Commons search case-quirk) applies to every future pool search:
run the six forms in both capitalizations, and probe the lowercase + "Panoram of" +
"<state> bird eye view" variants when a pool comes back empty.
