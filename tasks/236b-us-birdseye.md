Status: open
# 236b: US bird's-eye and panoramic city views (1847-1929)
Depends on: none
Touches: fit/src_us_birdseye.py, data/catalog/extras_us_birdseye.jsonl, data/commons/files_us_birdseye.jsonl, data/commons/classified_us_birdseye.jsonl, docs/lead_us_birdseye.md, tests/test_src_us_birdseye.py, tests/golden/src_us_birdseye_sample.json

## Goal
Subtask of 236. GOAL.md point 5: artists' aerial and bird's-eye views count as much as surveys. The Library
of Congress "Panoramic Maps" collection (about 1,500 US bird's-eye views, 1847-1929, public domain; many
mirrored on Wikimedia Commons) is the US equivalent of Braun & Hogenberg. Stage views of the owner's four
cities first (New York, Washington DC, San Francisco, Nashville), then more US cities, in this task's own
staging files, the way 213 staged Civitates.

## Acceptance criteria
- [x] Verified before use (docs/lead_us_birdseye.md): the collection's location and licence, how files are
      fetched (Commons category or loc.gov IIIF), per staged view its date, artist/publisher and resolution;
      unusable ones listed with the reason.
- [x] fit/src_us_birdseye.py holds the hand-checked file -> QID table (every QID verified against label,
      P625, enwiki). Views of a city that 236a also stages use the SAME site id - agree it through the
      catalog slug rule (catalog.slug from QID + name) and record the shared ids in the lead doc; never two
      sites for one QID.
- [x] Staged rows in this task's files only: extras_us_birdseye.jsonl (only for cities not already in the
      catalog and not staged by 236a - check data/catalog/extras_us_cities.jsonl on main before adding one;
      region "United States", kind "town", aerial_ok true), files_us_birdseye.jsonl (files.jsonl shape +
      200 evidence field), classified_us_birdseye.jsonl ("view", by hand).
- [ ] fit/evidence.py check passes offline on every staged row; the four owner-named cities each have at
      least one view staged or the lead doc says why not; at least 25 cities staged in total.
- [x] Test (no network): the staged files join, the evidence check passes, a golden sample of rows.

## Notes
- Bird's-eye views are oblique: the fit is harder than for a plan. Prefer views drawn near-vertical; record
  the view's apparent angle on the row's note so 236c/the matcher can order them.
- Templates: fit/src_artists.py + docs/lead_artists.md (Civitates).
- Do NOT write the canonical files - that is 236c.

## Hand-over

(2026-10-14, iteration 188, agent a) **Work A (the batch-2 lead doc) is COMPLETE and correct.** The
doc was already committed by the driver in f3aed14; this session finished 187's remaining step (the
fresh-eyes re-read) and found + fixed two factual errors: Nashville's P625 is 721 m **SE** of its
refined table point (doc said NE), and the University of Pittsburgh is **~4.0 km EAST** of the
Pittsburgh city point (doc and the Q1342 SITES comment said "~4.7 km west" - wrong distance AND
direction; both re-computed with the project's distance formula). Both transcripts were
re-verified: the --check block is exactly equal to a fresh offline `--check` run this session
(/tmp/aw236b_check_188.txt), the 85-line QID block is byte-identical to /tmp/aw236b_verify_186.txt
(still on disk; content-identical to 185's run - no drift). Chicago's "~10.5 km south" (10488 m
measured) and Q62's "2.0-2.4 km" (2010/2393 m) verified correct. Module tests 5/5. **Only batches
3+ remain** (box 4, 25 cities: 14 done, 11 to go).

### Next step: batch 3 (Kansas City, New Orleans, Denver, St. Paul, Minneapolis)

One session per city, or two cities if the pool is small. Per-city procedure (181's playbook,
restated in the 184 DECISIONS entry):

1. **QID check against existing sites** (never two sites for one QID): grep the city name in
   data/catalog/sites.jsonl, data/catalog/extras.jsonl, data/catalog/extras_us_cities.jsonl,
   web/data/sites.json. New city -> point = the city's P625 (record any refinement).
2. **Pool search**: per-city Commons file-namespace search, the 6 plain-phrase forms ("bird's-eye
   view of <city>", "bird's eye view of <city>", "birdseye view of <city>", "<city> bird's eye",
   "<city> birdseye", "Birds' eye view of <city>" - quoted-intitle queries find NOTHING) each +
   " filetype:bitmap"; commons.info 50/call at 1/s. Batch-2 builder template = /tmp/aw236b_b2.py
   (may be wiped - a ~55-line stdlib+commons script: change the CITIES list). Gate =
   commons.keep() + 600-char caption gate (norm(city) in norm(title+desc)) + Public domain +
   >= 4000 px wide.
3. **Pick the ONE steepest view** (near-vertical, grid legible; DROP pictorial/regional/fort
   close-up/photo/street-car/railway/exposition); eyeball 1280-px thumbs to dedupe same-sheet
   scans (thumb URLs via the Commons API imageinfo thumburl iiurlwidth=1280 through .venv's
   commons.get - commons.info has no 'thumb' key); one row per sheet, keep the LOC/largest scan.
4. **Verify the QID live**: `.venv/bin/python fit/src_us_birdseye.py --verify QID` - watch
   name-search traps (Chicago's Q131252 and Pittsburgh's Q235034 are the in-table examples; a
   university hit within 50 km is NOT flagged but `record --live` would store it).
5. **SITES + SOURCES entries in fit/src_us_birdseye.py** (batch-2 entries ~lines 130-213 /
   350-400 are the pattern: SITES comment = P625/P131/enwiki/point-derivation + any name-search
   trap with the MEASURED distance and direction (dx=dlon*111194.9266*cos(lat0), dy=dlat*110900);
   SOURCES comment = the pick + same-sheet scans + drop summary pointing at the lead doc).
6. **--dry then stage** (live commons.info re-check of every title) then **--check** (must exit 0).
7. **Lead-doc section per city** (batch-2 style: STAGED bullet + DROP list with per-item reasons
   + name-search-trap paragraph when applicable) + **re-run --verify** (the QID transcript in the
   doc grows by one QID per new city - the transcript must stay verbatim) + update the Staging
   section (view count, --check transcript, "Not done yet" list).
8. **--golden** (intended change) + extend tests/test_src_us_birdseye.py exactly as 184 did
   (SITES-id table, extras-id table, per-title year, evidence-points, named-place table,
   len(files) 21 -> 26 for batch 3) + module tests, then the full suite (if it rewrites
   docs/site_flow/307d_*.png, carry them in the commit with the 306g-style disclosure).

A city with no usable view gets a lead-doc note and the next candidate. Batch 4 after batch 3:
the remaining ~6 (Cleveland, ...) to reach 25 cities, then box 4 ticks.

### State

- docs/lead_us_birdseye.md: committed (f3aed14 + this session's fix commit). 715 lines, 19 ##
  sections, 14 cities / 21 views; QID section (14-QID verbatim transcript) + five batch-2 city
  sections + Staging section (verbatim 21-line --check); directions/distances corrected.
- fit/src_us_birdseye.py: 14 SITES / 21 SOURCES; Q1342 SITES comment now "~4.0 km east".
- data/catalog/extras_us_birdseye.jsonl: 10 site rows; data/commons/files_us_birdseye.jsonl +
  classified_us_birdseye.jsonl: 21 rows each. tests/golden/src_us_birdseye_sample.json: the
  21-row pin. Module tests 5/5 (188). Offline --check 21/21 (re-verified 188).
- /tmp (may be wiped, all regenerable): /tmp/aw236b_verify_186.txt (the 14-QID transcript - the
  source of the doc's QID block), /tmp/aw236b_check_188.txt (fresh check), /tmp/aw236b_b2.py +
  /tmp/aw236b_b2.json + /tmp/aw236b_b2_cands.json + /tmp/aw236b_b2_thumbs/ (the batch-2 pool
  builder and full pool - the template for the batch-3 builder).

### Rules (unchanged)

NEVER write the canonical files (data/commons/files.jsonl etc. - that is 236c); NEVER touch 236a's
extras_us_cities.jsonl (read-only; the module's _shared_site enforces it); run live commands under
.venv/bin/python (system python3 has no numpy; the module top stays stdlib-only); batch size ~5
cities/session to fit the context limit; the golden sample is the contract (--golden only for an
intended change); the full suite rewrites the five docs/site_flow/307d_*.png every run - if the
bytes change, carry them in the commit with the 306g-style disclosure (the 184 commit did); tests
never bind fixed network ports or write outside the project + temp dir; when recording a
distance/direction claim in a doc or comment, MEASURE it (the 188 NE/west errors were unmeasured
draft-time guesses).
