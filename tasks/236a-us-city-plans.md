Status: in-progress
# 236a: US city plans - New York, Washington, San Francisco, Nashville first
Depends on: none
Touches: fit/src_us_cities.py, pipeline/build_catalog.py, data/catalog/extras_us_cities.jsonl, data/commons/files_us_cities.jsonl, data/commons/classified_us_cities.jsonl, docs/lead_us_cities.md, tests/test_src_us_cities.py, tests/golden/src_us_cities_sample.json, PITFALLS.md

## Goal
Subtask of 236. Stage old plans of US cities the way 204 staged Van Deventer and 213 staged the artists'
views: a hand-checked file -> QID table in fit/src_us_cities.py, one site per city (or per district or
fortification when the whole city is too big for one site box), picture rows with task-200 evidence, all in
this task's own staging files. 236c consolidates them.

Leads to verify (NONE verified yet - check each exists on Wikimedia Commons or the Library of Congress, is
the original or a facsimile of it, its date, its licence, and its resolution before using it):
- New York: the Castello Plan (1660; NOTE the common Commons image is the 1916 Adams/Stokes redraft - record
  which one a file is; prefer the original), the Ratzer Map (1767/1770), the Commissioners' Plan of 1811
  (Bridges), the Viele map (1865, Sanitary & Topographical Map - streams and shoreline).
- Washington DC: the L'Enfant plan (1791, LoC), the Ellicott engraved plan (1792), Boschke's topographical
  map (1857/1861); the Civil War defences (Barnard, 1865, Fort Stevens / Fort Marcy etc. - earthworks that
  may show on 3DEP LiDAR, each fort a candidate site of its own).
- San Francisco: the 1849 plans (Eddy, Ringgold), the 1850s city plans.
- Nashville: early town plans; the Civil War fortification plans of Fort Negley (earthwork, LiDAR candidate).
- Then any other US city with an old plan on Commons: Boston (Bonner 1722), Philadelphia (Holme 1683),
  Savannah (Gordon 1734), New Orleans (French plans 1720s), Charleston, St. Augustine.

## Acceptance criteria
- [x] Verified before use (docs/lead_us_cities.md): per staged picture what it is, where it lives, the
      drawing's date (recorded on the row - an upload date is not a drawing date), original vs later redraft;
      unusable files (modern redraws, too small, no place tie, not free) listed with the reason.
- [x] fit/src_us_cities.py holds the hand-checked file -> QID table: every QID verified against its label,
      P625 and enwiki link (the Barnard Castle trap: a name search alone gives the wrong place). A city
      whose plan covers more than the site box gets either an extent recorded on its row (check how
      pipeline/catalog.py sets extent_m and whether an extras row can carry one) or a district/fort site
      with its own QID - recorded which, and why, in the lead doc.
- [ ] Staged rows in this task's files only: extras_us_cities.jsonl (id, qid, name, lon/lat of the area
      the plan covers, region "United States", kind "town" or "fort", aerial_ok true, place, wikipedia,
      note), files_us_cities.jsonl (files.jsonl shape + 200 evidence field), classified_us_cities.jsonl
      ("plan", by hand). A city whose QID is already in the catalog gets picture rows for that site id.
- [x] fit/evidence.py check passes offline on every staged row; all four owner-named cities are staged or
      the lead doc says exactly why one could not be.
- [x] Test (no network): the staged files join, the evidence check passes, a golden sample of rows.

## Notes
- Ground: cities are aerial-photograph sites (aerial_ok true; bare-earth LiDAR erases streets). The street
  grid, shoreline, squares and church footprints carry the fit. Civil War forts are the exception: their
  banks may show on 3DEP bare earth (pipeline/aw.py), like the mounds in 203a.
- Templates: fit/src_van_deventer.py + docs/lead_van_deventer.md, fit/src_artists.py + docs/lead_artists.md.
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, sites.json) - that is 236c.

## Hand-over

(2026-10-13, iteration 150, agent a - **Vioget 1839 STAGED: San Francisco is now complete (4 rows).
Tests 7/7 green (offline). Everything committed. Next: Nashville (Q23197) - the last thing left of
box 3.**

### Current state
- `fit/src_us_cities.py`: SITES = {Q60 New York, Q61 Washington DC, Q62 San Francisco}; 11 source
  rows (4 NY + 3 DC + 4 SF incl. the 1839 Vioget, no date swap - page date = drawing date). The
  stage/check/verify/golden pattern is stable (143 -> 150, no structural change needed once).
- Staged (this task's files only): extras_us_cities.jsonl 3 sites; files_us_cities.jsonl 11 rows;
  classified_us_cities.jsonl 11 rows; golden 3/11/11.
- --check offline: **11 rows, 11 pass, 0 fail, 0 no-tie**. --verify live (iteration 150): unchanged
  (3 QIDs, no >50 km flag, no trap - each city's name search resolves to itself).
- docs/lead_us_cities.md: full NY/DC/SF sections (per-plan STAGED/DROP with exact titles and
  reasons; Vioget = STAGED subsection; Ringgold NOT on Commons; Henry Bill 1856/1858 = 236b lead);
  the offline transcript is the 11 PASS lines / 11/11.
- Tests: tests/test_src_us_cities.py (5 offline tests: check-staged, three merge states
  self-scaling, qid table + staged rows, evidence + Venice negative control, golden) +
  tests/test_region.py = **7/7 green**.

### EXACT next steps: Nashville (Q23197), then done
1. **Live research FIRST (no editing before the verdicts are in DECISIONS - the 145/147 pattern):**
   a. Re-verify Q23197 via pipeline/catalog_wd (the robust WD path): label, EVERY P625 value
      (downtown ~(-86.7744, 36.1622) is EAST of the Cumberland; the 1790s town was at the
      Cumberland/Tennessee confluence ~(-86.788, 36.166) - check where the old town sits relative
      to the P625 and decide the site point accordingly, like Q62's refined tip-midpoint), P373,
      P131 (Davidson County, Tennessee), enwiki, the first name-search hit with P625 (trap check);
      exact greps: no existing site uses Q23197 / nashville-q23197 (data/catalog/sites.jsonl,
      extras.jsonl, web/data/sites.json - watch Q23197x substring hits).
   b. Find the candidates: **early town plans** (the 1790s town plat / 1800s-1820s "Town of
      Nashville" plans on Commons) and **the Civil War fortification plans of Fort Negley** (the
      large earthwork on the west side - NARA holdings; its own kind-"fort" site, own QID verified
      the same way - 1600 m fort box, a 3DEP LiDAR candidate as the DC forts / 203a mounds). For
      each candidate: thumbnail, metadata (resolution, licence, page date vs drawing date), and the
      gate window (title + the 600-char desc must print the city; titles case-sensitive).
   c. **Verdicts in DECISIONS.md BEFORE editing** (what stages, what drops and why, the site point
      decision(s), whether Fort Negley is stageable at all).
2. **Apply in one session (the 146/148/150 pattern):** SITES += Q23197 (+ the fort site if staged);
   SOURCES += rows (p="plan"; known-date swap with date_commons only when the page lost the
   drawing date); docstring += Nashville; live --verify (expect N QIDs, no flag, no trap) + live
   stage; offline --check (11 + M rows, all pass) + --golden; tests (row-count asserts, PASS-line
   list, years dict, the qid-table asserts incl. the point, named_by_qid) then run the two test
   files; lead doc gets the Nashville section (site point + extent decision, per-plan STAGED/DROP,
   transcript).
3. **Done:** with Nashville staged, all four owner-named cities are staged - tick box 3 (the last
   open box; 1/2/4/5 already stand), set Status: done. The driver re-checks the suite: my two test
   files must be green (the full suite has 1 pre-existing failure,
   test_fit_queue.py::test_placement_gestures_and_save_in_the_browser - agent c's 307 work, not
   mine).

### Gotchas (all still true)
- Tests OFFLINE only (socket-blocked fixture in the test file); run ONLY tests/test_src_us_cities.py
  + tests/test_region.py - never the full suite (the pre-existing test_fit_queue failure is agent
  c's). Live commands run under .venv/bin/python (the module top stays stdlib-only; commons -> aw
  needs numpy).
- Named-place gate: title + the 600-char-truncated desc of c.info(); every staged SF title prints
  "San Francisco" in the title EXCEPT the Vioget 1839 (gate-safe via the DESC - verified live in
  149, staged in 150). File titles case-sensitive. c.info batches of ~10 titles fine (the 414 was
  50 long titles).
- stage() is idempotent on (site, title) and appends a NEW site row only for unseen ids; the
  known-date swap runs before c.keep(); a missing title fails loud. To change a STAGED row's note
  you hand-edit the jsonl row (stage() has no update path), keep SITES and the staged row in
  lockstep (pull the string from SITES), then re-run --golden.
- Town box: kind "town" -> width_m = height_m = 2000 -> a **2 km x 2 km** box centered on the point
  (site_bbox hw = width_m/2). Do NOT write the 4 km version again. Fort box: kind "fort" = 1600 m
  (the DC forts precedent). Do NOT add a box_m override (specs/site_boxes.json is not in this
  task's Touches).
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, sites.json) -
  that is 236c. The REGION_NAME line in pipeline/build_catalog.py is already committed.
- Do not "fix" pipeline/commons.py's NO regex (not in Touches).
- /tmp still holds: the ussf_* transcripts (verify/check/stage), ussf_search*/ussf_meta* (exact
  drop titles - all now in the lead doc), sf_0..sf_7.jpg + yb1839*.jpg thumbnails (throwaway). The
  lead doc carries every title needed.
- Nashville is the last city: after it stages, the only work left in this task is ticking box 3
  and setting done (236b bird's-eye and 236c consolidation are separate tasks).
