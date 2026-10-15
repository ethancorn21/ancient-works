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
(2026-10-14, iteration 183, agent c) **Memphis (city 4/5) is fully committed. NEXT: city 5/5 -
research (one session) + landing (one session), then the close step.**

**State (all verified in the 183 session):**
- FOUR cities LANDED + committed: Omaha (Q43199, 1868 E. Ruger .tif), Indianapolis (Q6346,
  1925 Spink page-1 .jpg, Zwolle swap), Columbus (Q16567, 1872 Bailey alternate.png), Memphis
  (Q16563, 1870 Ruger .jpg). Staging files 4/4/4, golden 4/4/4, lead doc complete (four city
  sections, Staging at "4 views / 4 site rows", Not-done-yet pointer naming city 5).
- Full suite GREEN at exactly the 178 baseline: 187P/1S/0F with `--ignore=tests/test_gate.py`
  (542.84 s, in-session) + tests/test_gate.py standalone 3P (2.25 s) = 190P/1S/0F over
  191 tests. Zero red. The 182 hand-over's "expect 190P" vs the 187 the run reports = the 3
  test_gate tests 178 included but the hand-over command excludes - measured decomposition in
  the 183 DECISIONS entry, NOT a regression.
- docs/site_flow/ matches main byte-for-byte again (5 re-encoded 307d PNGs restored - R5;
  the suite re-encodes up to ten on EVERY run).
- `--check` offline re-verified green (4/4 PASS caption_coords, exit 0, zero join lines);
  module tests 5/5 (2.29 s).

**CITY 5 = the last city (session N: research, session N+1: landing, then close).**
The 181 candidate list ends with "..." after New Orleans (already staged by 236b - skipped),
so the box-5 fallback governs: **any US city with a usable LOC Panoramic view that is not
staged anywhere** (the task owes FIVE cities, not specific ones). Suggested first-probe
list, in order (name-checked clean against all five staging sets + catalog + web/data/
sites.json in 183; the QID-level no-collision check still happens per city in research):
**Albuquerque, Portland (OR), Salt Lake City, San Antonio, Seattle, Richmond, Buffalo,
Miami.** Probe in that order with the six plain-phrase forms + `filetype:bitmap`
(srnamespace 6, srlimit 40; the 236b lead-doc Fetch route; the /tmp/aw236b_b3_dvr.py pool
builder is the template if it survived loop maintenance - rebuild from the 181 entry if
not); the first city whose pool yields a usable view (Public domain, >= 4000 px, caption
names the city, drawn whole-city view, steepest/best-scanned picked from the gate-passes)
is city 5. A city whose pool yields none: record the drop with its reason in the lead doc,
take the next probe city. The skip list is also enforced mechanically by the module's
known_sites() at --verify/--check (catalog + 236a's + 236b's + 240's extras + web/data/
sites.json) - never a second site for a QID.

**RESEARCH (live, /tmp artifacts named aw241_city5_*; the 179/181 per-city record is the
pattern - both are in DECISIONS.md / DECISIONS-archive.md):** (1) QID via Wikidata
wbgetentities (the 181 /tmp/aw241_mem_qid.py pattern if it survived): label, EVERY P625
(measure all distances with fit/evidence.hav_m before writing them), P373 (a string is the
usual US quirk -> place = county + state), P131, P17, enwiki, name search at limit 5 AND 20
(first hit with P625). The mislabel trap class hit in 177 (Q16556 = Phoenix), 179
(Q1405 = Augustus) and 240 (Q131855 = a roadster): never trust a first-guess QID from
memory - take the QID from the live search hit. (2) Pool: build, dedupe, gates (keep after
the Zwolle known-date swap + caption names the city + Public domain + >= 4000 px), eyeball
every gate-pass with a 1280-px thumb one by one. Record EVERY non-staged pool item with
its reason (same-sheet dupes, shallow, regional, photo, other-city, licence, small).

**LANDING (the 176-182 pattern, one city per step-set):** module edit (SITES entry with the
verified P625 point + the staged view's apparent-angle note, <CITY>_<YEAR> row, SOURCES
entry, header/comments marking city 5 LANDED) -> `--verify` (save the exact output; it goes
verbatim into the lead-doc QID section; expect no FLAG/TRAP) -> `--dry` -> stage (live
commons.info re-check; "1 new sites, 1 new pictures") -> `--check` (expect "evidence:
5 rows, 5 pass, 0 fail, 0 no-tie", zero join lines; verbatim into the lead-doc Staging
section) -> lead-doc section (STAGED bullet + full DROP list + QID facts; Staging ->
"5 views / 5 site rows" + the note that 236c consolidates and checks the 25 total,
16+4+5) -> `--golden` (5/5/5, an intended change) -> tests (PASS key, SITES/years/points/
named tables += city 5, golden docstring count 5/5/5; the negative control stays on
files[0] = the Omaha row) -> module tests 5/5 -> FULL suite in-session BLOCKING (expect
187P/1S/0F with `--ignore=tests/test_gate.py` on this tree - main may have grown since;
zero red is the criterion, and if the ONLY failure is
test_fit_queue.py::test_placement_gestures_and_save_in_the_browser it is agent a's
in-flight 239 work, not yours - any other failure: stop and investigate) -> R5 restore
(`git checkout main -- docs/site_flow/307d_*.png`) -> commit.

**CLOSE (same session as the landing, once city 5 is in):** final full suite = baseline
(zero red), `--check` ends at 5/5 PASS with no join problems, tick ALL FIVE acceptance
boxes (they are verified at that point), set `Status: done`. 236c consolidates the staging
into the canonical data and checks the 25 total - never write the canonical files here.

**Rules (unchanged):** never write the canonical files (236c); 236a's/236b's/240's files
read-only (the module's cross-check enforces); live commands under .venv/bin/python (module
top stays stdlib-only; system python3 has no numpy); the golden is the contract (--golden
only for an intended change); tests never bind fixed network ports or write outside the
project and the temp dir; every full-suite run re-encodes up to ten docs/site_flow/307d_*.
png - restore main's bytes before committing (R5); run the suite in-session (blocking),
never nohup'd past the session (the 174 driver-kill lesson).

**/tmp artifacts (loop maintenance may wipe; the lead doc + the DECISIONS entries carry
the full record verbatim):** 183 added none (verification + bookkeeping only). The Memphis
research set (aw241_mem_*) and the pool-builder template (aw236b_b3_dvr.py) are listed in
the 181/179 DECISIONS entries.
