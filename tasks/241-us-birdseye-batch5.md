Status: in-progress
Depends on: 240, 242, 810
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
- [x] fit/src_us_birdseye_batch5.py holds the hand-checked file -> QID table for its five cities
      (every QID verified live against Wikidata with the module's --verify BEFORE staging: label,
      every P625 value, P373, P131, enwiki, the first name-search hit with coordinates - what
      record --live would resolve; the machine cannot reach loc.gov, so the files are fetched from
      their Wikimedia Commons mirrors, 236b's route). The module copies fit/src_us_birdseye_batch4.py's
      machinery (itself a copy of fit/src_us_birdseye.py's - the template it keeps in sync with);
      its known_sites() reads the catalog plus 236a's extras_us_cities.jsonl, 236b's
      extras_us_birdseye.jsonl and 240's extras_us_birdseye_batch4.jsonl so a QID can never sit on
      two sites.
- [x] Staged rows in this task's files ONLY: extras_us_birdseye_batch5.jsonl (the new cities' site
      rows - region "United States", kind "town", aerial_ok true, the point = the city's verified
      P625 or a recorded refinement, the note recording the staged view's apparent angle so 236c /
      the matcher can order the oblique views); files_us_birdseye_batch5.jsonl (files.jsonl shape +
      the 200 evidence field); classified_us_birdseye_batch5.jsonl (p_birdseye 1.0, by "hand"). One
      row per city = the steepest (near-vertical), best-scanned whole-city view of the collection
      for that city (Public domain, >= 4000 px wide, the caption names the city); every pool item
      not staged is listed with its reason in the lead doc.
- [x] fit/evidence.py check passes offline on every staged row (--check exit 0, every row PASS
      caption_coords, no join problems); no staged site id or QID collides with an existing site
      (the catalog, 236a's, 236b's and 240's staging files, web/data/sites.json) - never two sites
      for one QID (the catalog slug rule: id = slug(name) + "-" + qid-lower).
- [x] Test (no network, the socket-blocking fixture per 236b's test file): the staged files join,
      the evidence check passes, a golden sample tests/golden/src_us_birdseye_batch5_sample.json
      pins the staged rows (regenerated only via the module's --golden for an intended change); a
      full-suite run = baseline (restore the re-encoded docs/site_flow/307d_*.png to main's bytes
      before committing - the PITFALLS test_owner_check rule).
- [x] FIVE cities staged (the 25 total: 16 from 236b + 4 from 240 + 5 here), each per the boxes
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
(2026-10-15, iteration 188, agent c) **HELD on "Depends on: 242" (the 230 it.216 path): the driver rejected the
187 done claim (3 new reds after the main merge); this session FIXED the test_merge red in this checkout
(the 9 Roman site directories 230's merge added - built byte-identical to agent a's reference build;
test_merge now 10/10) and found the owner_check pair red a 2nd consecutive time (the 307d mid-transition
family - the fix is open task 242). No done claim while held; when the driver brings 241 back after 242
merges: re-verify, then claim.**

**State (all committed; tree clean):** Status: in-progress, Depends on: 240, 242, all five boxes ticked -
the staging work is COMPLETE and verified (5/5 cities staged; lead doc 779 lines; golden 5/5/5; module
tests 5/5; --check 5/5 zero-join). The driver committed my 187 session's files (f8f99a3/d8084b5/a5d4b3b)
and merged main (411a9e5) before rejecting (c034a56). This session changed no data rows: it only built
the gitignored web/data/sites/<id>/ directories for the nine Roman sites the merge added to
web/data/sites.json (build log /tmp/aw241_build_188.log may be wiped; data/raw + data/tilecache +
data/sites/*/dem* caches are the gitignored build inputs) and restored web/data/sites.json + the three
re-rendered docs/site_flow/307d_*.png to committed bytes (R5).

**Facts established this session (verified by running):**
- The test_merge red was deterministic local build state, not a code bug: the nine new sites (ardoch,
  carriden, cilurni, congavata, kirkintilloch, luguvallium-q71551754, petriana, tunnocelum, virosidum =
  808's no-QID extras rows) had sites.json entries but no directories in this checkout (the main checkout
  lacks all nine too - the reference build is in agent a's checkout). Fixed with
  `.venv/bin/python pipeline/build_catalog.py --ids <9 ids> --force`: built 9, skipped 0, failed 0
  (EA WCS x6 english, srsp-open-data S3 DTM x2 scottish, ardoch aerial-only - no scot tiles on its box,
  matching its committed no-credit entry). relief_clip_m matched the committed entries exactly; every
  built file byte-identical to agent a's reference (cmp -s, zero diff). The only tracked file dirtied was
  web/data/sites.json (--force zeroes rebuilt sites' score/oldest/overlays - build_catalog does not
  recompute markers; 230's --marks pass did) -> `git checkout -- web/data/sites.json`. test_merge 10/10
  here now, deterministic for the driver's re-check too. (New PITFALLS entry under data/merge/.)
- The owner_check A/B pair RED a 2nd consecutive time in this checkout (187, 188): A test_owner_save_bar_scale
  (the 307d mid-transition probe), B test_owner_save_site_size_fallback (the designed cascade, A's
  itemBytes None). Machine-state flake: green here at it.168/169, red on agent a's it.226/228; 242 measured
  28.6-33.6% pixel drift between runs an hour apart on the identical tree (captures land mid-transition).
  The fix is task 242 (open; Depends on: 307d merged; next in the driver's queue after 236c; its regime:
  settle before shooting + no unconditional in-checkout re-render of the 307d PNGs).
- The driver's "fix the combination" = these two: red 1 fixed, reds 2+3 await 242 - the exact 230 it.216
  hold (230 is still in flight on the same declaration).

**NEXT (one session, when the driver brings 241 back after 242 merges):** 1) Confirm 242 is merged
(git log / driver notes; 242 commits the ten pinned 307d PNGs and the settle-before-shooting fix in
tests/test_owner_check.py). 2) Re-verify in this checkout: module tests (5/5), --check (5/5), test_merge
(10/10), the owner_check pair (should be deterministically green under 242's regime; if any 307d PNG ends
up dirtied, investigate before claiming). 3) One full-suite run for the record; if green, claim done
(Status: done; boxes already ticked) - the driver re-checks, and 236c (Depends on 241) then consolidates
the 25-city total (16 + 4 + 5). 4) If the pair is STILL red post-242, that is a 242 defect: add
"## Proposed changes" to tasks/242-*.md with the run evidence and stop claiming (do not edit 242's files;
never weaken or delete a test).
