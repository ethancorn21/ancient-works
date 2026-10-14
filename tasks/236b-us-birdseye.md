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
- [ ] Verified before use (docs/lead_us_birdseye.md): the collection's location and licence, how files are
      fetched (Commons category or loc.gov IIIF), per staged view its date, artist/publisher and resolution;
      unusable ones listed with the reason.
- [ ] fit/src_us_birdseye.py holds the hand-checked file -> QID table (every QID verified against label,
      P625, enwiki). Views of a city that 236a also stages use the SAME site id - agree it through the
      catalog slug rule (catalog.slug from QID + name) and record the shared ids in the lead doc; never two
      sites for one QID.
- [ ] Staged rows in this task's files only: extras_us_birdseye.jsonl (only for cities not already in the
      catalog and not staged by 236a - check data/catalog/extras_us_cities.jsonl on main before adding one;
      region "United States", kind "town", aerial_ok true), files_us_birdseye.jsonl (files.jsonl shape +
      200 evidence field), classified_us_birdseye.jsonl ("view", by hand).
- [ ] fit/evidence.py check passes offline on every staged row; the four owner-named cities each have at
      least one view staged or the lead doc says why not; at least 25 cities staged in total.
- [ ] Test (no network): the staged files join, the evidence check passes, a golden sample of rows.

## Notes
- Bird's-eye views are oblique: the fit is harder than for a plan. Prefer views drawn near-vertical; record
  the view's apparent angle on the row's note so 236c/the matcher can order them.
- Templates: fit/src_artists.py + docs/lead_artists.md (Civitates).
- Do NOT write the canonical files - that is 236c.

## Hand-over

(2026-10-14, iteration 179, agent a) Merged main, then the FOUR OWNER CITIES are STAGED: 11 bird's-eye
views (NYC 3, DC 3, SF 4, Nashville 1) in this task's own files, module + lead doc + tests + golden all
written. The 25-cities box and all new-city work are the next sessions.

- **Merge (committed this session):** `git merge main` conflicted in 4 binary files (docs/site_flow/
  307d_{A,B}_{4-saved,5-reload}.png). Resolution: TOOK MAIN'S VERSION for all four. Why: both sides are
  regenerations of agent a's 307d screenshot test; main's come from a FULLY GREEN suite run (306g's
  commit note: 169->172 passed, 0 failed, "the baseline's lone 307 red is fixed on main") while our
  branch's copies were stale working-tree leftovers from the RED run (iter-178 hand-over noted they
  predated the session; the 307 code is identical on both sides, so a fresh run reproduces main's
  bytes). Recorded in DECISIONS.md.
- **Tests state (last full run, after the merge):** 172 passed, 1 skipped, 0 FAILED - fully green
  (the 307 browser test that failed at the 178 baseline is fixed on main). **tests/test_src_us_birdseye.py
  has NEVER been run** (context limit hit right after writing it) - it is uncommitted, as is everything
  else in this list. Module-side state (all run under .venv/bin/python, verified this session):
  `fit/src_us_birdseye.py --check` exit 0, 11/11 PASS caption_coords, no join problems; `--dry` is
  idempotent ("staged: 0 new sites, 0 new pictures"); `--verify` clean for all 4 shared QIDs (no P625
  flag, no search trap; transcript in the lead doc); `--golden` wrote the golden file.
- **UNCOMMITTED (harness saves them - do not lose; commit them next session with the test run):**
  fit/src_us_birdseye.py (new), data/commons/files_us_birdseye.jsonl (11 rows), data/commons/
  classified_us_birdseye.jsonl (11 rows, p_birdseye 1.0 by:hand), tests/test_src_us_birdseye.py (new,
  5 tests), tests/golden/src_us_birdseye_sample.json (new), docs/lead_us_birdseye.md (new, complete for
  the four cities). data/catalog/extras_us_birdseye.jsonl does NOT exist yet - correct: no new cities
  staged yet; _load() returns [] for it. data/catalog/extras_us_cities.jsonl (236a's) was only READ,
  never written (the four shared ids: new-york-q60 / washington-q61 / san-francisco-q62 / nashville-
  q23197; the module's _shared_site cross-checks id per run and fails loud on drift).
- **Visual verdicts locked this session (thumbnails in /tmp/aw236b_thumbs/, incl. chk_Taylor_LOC_
  75694818 + chk_Goddard_IA pulled this session):** DC: STAGE Warner 1886 (true block-by-block view,
  whole city + suburbs, title printed); DROP Sachse 1871 LOC 90683459 (pictorial - the Capitol is the
  subject, the city a painted background, no grid at fit scale); DROP Bohn 1861 LOC 88694227 (regional
  "seat of war on the Potomac" - Washington a small part of the frame). SF: STAGE the Bill 1854 view
  from the DPLA 7000x4156 scan (oldest staged view of the city; drawn 1852 per the sheet, page undated
  -> year 1854 from the title); the two Geographicus Bill scans (3500x1974/4000x2325) are the SAME
  sheet -> dropped. Dup-sheet checks CONFIRMED visually: Taylor 1879 (DPLA "Taylor map of New York"
  = LOC 75694818, keep the LOC row) and Goddard 1868 (IA scan 12587x8962 + NYPL 7662x5062 = LOC
  75693101, keep the LOC row). Nashville: STAGE LOC 77696328 (13851x9666, the largest scan; banner
  says 1897, page says 1896 -> date "1897" + date_commons "1896" on the row); DROP the ppmsca.03354
  and Henderson LCCN95501846 pair (same sheet); DROP all three Fletcher 1864 Fort Negley views (fort
  close-ups, NO city grid, and 236a found no fort-only plan so no fort site exists) - the 1897 view
  stands as Nashville's view, so the "at least one view or the lead doc says why" half of box 4 holds.
  All reasons are written into docs/lead_us_birdseye.md (STAGED/DROP/RESERVED per city).
- **Acceptance boxes:** 1 (lead doc: location/licence/fetch route + per-view date/artist/resolution +
  unusable-with-reason) and 2 (module holds the hand-checked table; shared ids recorded) and 3 (staged
  rows in this task's files only; extras_us_birdseye empty until new cities) are satisfied FOR THE
  FOUR CITIES - tick them once the test run is green. Box 4 (>=25 cities) and box 5 (tests) are NOT
  done. Do NOT tick anything until pytest on the new test file passes.
- **NEXT (exact):** (1) `.venv/bin/python -m pytest tests/test_src_us_birdseye.py -q` (5 tests: join+
  offline PASS, three merge states, shared-table+staged-rows, negative control Venice/6680986 m,
  golden). Fix any mismatch in the TEST (the staged rows are correct - they passed --check; e.g. the
  year map or the date assertions may need touching). (2) Full suite `.venv/bin/python -m pytest -q`
  (expect 177 passed, 1 skipped, 0 failed = 172 + the 5 new). (3) Add the PITFALLS entry: loc.gov is
  403 (CloudFront bot block) from this machine - both web_fetch and urllib with the project UA; use
  the Commons mirrors (URL https://www.loc.gov/collections/panoramic-maps/). (4) Commit the uncommitted
  list above as `236b: stage the four owner cities (11 views) - module + lead doc + tests + golden`.
  (5) THEN the 25-cities batch work (see below). (6) After all boxes tick, tick box 4 only at >=25
  cities total and set Status: done.
- **New-city batches (the remaining work, >=21 cities):** per city: Commons FILE-NAMESPACE full-text
  search (the previous session's queries are in its DECISIONS entry; the candidate pool builder used
  commons.members() + commons.info() 50/call, 1/s pace, keep() + the 600-char caption gate - /tmp/
  aw236b_good.json holds only the four cities' pools) -> pick the one best view (near-vertical, grid
  visible, public domain, >= ~4000 px wide; PICTORIAL/regional/building-close-up views and photos are
  drops) -> verify the QID via pipeline/catalog_wd (watch the Barnard-Castle trap: a name search can
  hit a number/place elsewhere) -> add the SITES entry in fit/src_us_birdseye.py (id = slug + "-" +
  qid-lower, region "United States", kind "town", the note records the view's apparent angle) + the
  SOURCES row -> `--verify` (append to the lead doc's transcript) -> stage -> update the lead doc per
  city (STAGED/DROP/RESERVED) -> `--check`. Candidate city list (in order, first ~25 that work): Boston,
  Philadelphia, Baltimore, Pittsburgh, Cincinnati, Louisville, St. Louis, Chicago, Detroit, Cleveland,
  Milwaukee, Kansas City, Omaha, St. Paul/Minneapolis, Indianapolis, Columbus, Memphis, New Orleans,
  Charleston (SC), Richmond, Norfolk, Portland (OR), Seattle, Denver, Colorado Springs, Santa Fe,
  Albuquerque, Salt Lake City, San Diego, Los Angeles, Houston, Dallas, San Antonio, Little Rock,
  Atlanta, Birmingham, Savannah, Buffalo, Providence, Hartford, Albany, Worcester, Rochester,
  Wilmington, Fredericksburg. Batch size ~5 cities per session fits the context limit. NEVER write the
  canonical files (236c), never touch 236a's extras_us_cities.jsonl, and check that city is not already
  in the catalog / in extras_us_cities.jsonl on main before adding a site (never two sites per QID).