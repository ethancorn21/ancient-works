Status: done
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
- [x] Staged rows in this task's files only: extras_us_cities.jsonl (id, qid, name, lon/lat of the area
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

(2026-10-14, iteration 177, agent a). **TASK DONE** - all five acceptance boxes checked,
Status: done. This session changed no code or data: iteration 176 had already done the last
remaining work (the lead-doc rewrite, 174 step 3) and was cut by its context limit before
writing its own notes; the driver committed it as 1d2a5fe ("[driver] uncommitted work after
iteration 176", docs/lead_us_cities.md +286/-52) - so the 175 hand-over's "next step" was
stale. This session re-verified the whole acceptance set fresh:
- `.venv/bin/python fit/src_us_cities.py --check` (offline): rc=0, no join problems, 15/15
  PASS, "evidence: 15 rows, 15 pass, 0 fail, 0 no-tie" - byte-identical to the docs/
  lead_us_cities.md "## Offline check" transcript.
- Tests: tests/test_src_us_cities.py + tests/test_region.py = 7/7 green (the suite's known-red
  tests/test_fit_queue.py is agent c's 306 in-flight work - the standing caveat).
- Lead doc (764 lines, read in full) matches the 174/175 checklist: header "all four
  owner-named cities staged (2026-10-14)"; the QID section with the Q23197 --verify transcript
  plus Q5471739/Q5471744; the Nashville section with the site point (36.16529, -86.78152) and
  the mirror-fit verdict (a-angle -174.1 deg, 0.8520 m/px, the V/mouth/flow checks), all four
  candidates (STAGED: Clayton 1804, Haydon 1860, LOC 2003630459, Defenses 1895; DROP list with
  reasons), the Haydon composite finding, the LOC extent (~1:13,500 from the printed bar =
  ~0.50-0.51 m/px, 17x29 in sheet ~= 10 x 5.7 km -> 3-5x over-size = review item; the
  handwritten "1" = 10000" note disagrees with the bar, recorded as-is), the 1895 nine-panel
  plate (panel 5 Fort Dan McCook confirmed at 6x; the panels 3/8/9 caption conflicts carried
  with an explicit legibility hedge; Fort Negley NOT among the panels), the Fort Negley
  fort-site candidate + the 236b Fletcher leads, the dropped-plans list (the 1895 Bien
  battle maps settled via IA 01104200/01104201), and the offline-check transcript.
- Staged rows (box 3): extras_us_cities.jsonl = 4 site rows (nashville-q23197 carries every
  box-3 field: id, qid, name, lon/lat, region "United States", kind "town", aerial_ok true,
  place, wikipedia, note); files_us_cities.jsonl = 15 rows (the four Nashville date facts per
  the 173/174 hand-over: Clayton 1804/1880 swap, Haydon 1860 no swap, LOC raw precision-8
  "1860s" page value year 1860, Defenses 1895/empty swap); classified_us_cities.jsonl = 15
  rows (Nashville 4x p_plan 1.0 by hand). NONE of Q60/Q61/Q62/Q23197/Q5471739/Q5471744 is in
  the canonical data/catalog/sites.jsonl or extras.jsonl, so box 3's "city whose QID is
  already in the catalog" clause is N/A. The canonical files were never written by this task
  (that is 236c).
Left for the other tasks: 236c consolidates the three us_cities staging files (4 site rows,
15 picture rows) into the canonical data and builds the four sites; 236b's Nashville leads
are the three Fletcher 1864 Fort Negley views (file names in the lead doc). No further work
on 236a.
