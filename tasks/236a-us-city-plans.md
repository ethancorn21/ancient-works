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

(2026-10-13, iteration 149, agent a - **SF APPLIED + corrected to the true box geometry; lead doc now
has the full SF section. Vioget 1839 found and verified as a 4th stageable SF row (staged next
session). Tests last run 7/7 GREEN (after the golden regen; the lead-doc edit after it is docs-only).
Everything code/data/lead-doc is in the tree, UNCOMMITTED (the harness saves it). Nothing committed
yet by me this session.**

### What this session did (all in the uncommitted tree)
1. **Fixed tests/test_src_us_cities.py line 73**: the 148 "stray `"""` removal" had left `""""` (4
   quotes) -> SyntaxError on import. Now `added."""` - clean. (The file also had stray CRs the edit
   removed; `grep -c $'\r'` = 0 now.)
2. **Tests run offline: 7/7 green** (`.venv/bin/python -m pytest tests/test_src_us_cities.py
   tests/test_region.py -q`) - after the fix, and AGAIN after step 3's golden regen.
3. **Corrected the 148 box-geometry error**: the 148 hand-over's "4 km x 4 km box" was a hw = width_m
   miscalculation. Measured: kind "town" = width_m = height_m = 2000 (build_catalog.BOX) and
   `aw.site_bbox` uses hw = width_m/2 -> the box is **2 km x 2 km** centered on the point
   (lat 37.78315..37.80111, lon -122.41426..-122.39152). Against it: both P625s 2.0-2.4 km OUTSIDE
   (no flag, --verify flags only >50 km); the two drawn tips ~30 m overshoot (Rincon past the east
   edge, W&J past the west); the 1854 sheet's 1850s growth (Market & 10th-11th corner, geocoded this
   session) reaches past the SW corner -> oversize sheet -> review-item case (NY 1811 / DC ring
   precedent). Fixes: `fit/src_us_cities.py` Q62 SITES **comment** rewritten to the measured numbers;
   Q62 SITES **note** rewritten ("1849/1850 sheets ... ~30 m overshoot at each drawn tip ... the 1854
   sheet's 1850s growth ... reaches past the box's SW corner - likely a review item"); the staged
   `data/catalog/extras_us_cities.jsonl` Q62 row's **note** hand-rewritten to the SAME new text
   (pulled from SITES programmatically so they cannot drift); `--golden` regenerated
   (tests/golden/src_us_cities_sample.json now carries the new note); `--check` re-run: **10 rows, 10
   pass, 0 fail, 0 no-tie**.
4. **docs/lead_us_cities.md** (4 edits, applied): header "three cities staged; Nashville last" + SF in
   the city list; QID-verification block = the 3-QID transcript (from /tmp/ussf_verify.out, still in
   /tmp) with "no flag (Q62's 2.0-2.4 km); no trap in all three"; prep-verified list now **Q23197
   only** (Q62's stale "~450 m / tip south of both" bullet removed - the correction is recorded in the
   SF section); the old "## San Francisco (Q62) - later sessions" stub replaced by the **full section**
   (site point + full tip derivation + correction note; the measured extent decision; staged rows;
   per-plan STAGED/DROP subsections with exact file titles and reasons; **Vioget 1839 subsection**; the
   Ringgold-NOT-on-Commons subsection with the exact chart titles; the views/photos/noise drops incl.
   the Henry Bill 1856/1858 = **236b lead**); the offline-check transcript now the 10 PASS lines +
   "evidence: 10 rows, 10 pass, 0 fail, 0 no-tie".
5. **New verified lead (this session, live)**: `File:1839 Plan of Yerba Buena (Jean Jacques Vioget).jpg`
   surfaced in the 147 searches but the 147 verdict never covered it. Checked live: 2400x2107, Public
   domain, page date 1839-01-02 (= drawing date, no swap needed), `keep()` passes; the desc prints
   "Plan of Yerba Buena (which was later renamed to San Francisco)" -> "San Francisco" INSIDE the
   600-char window -> **gate-safe**. It is the FIRST plan of the old town (1839 Vioget grid centered on
   Portsmouth Square, hachured shoreline, NARA 33300 deposition exhibit, published 1853) and its drawn
   extent (~1 km old core) sits inside the 2 km box. **Stage it next session as the 4th SF row.**

### EXACT next steps
1. **Confirm the tree is still green** (offline): `.venv/bin/python -m pytest tests/test_src_us_cities.py
   tests/test_region.py -q` (expect 7/7; the lead-doc edit since the last run is docs-only, this is a
   cheap re-confirm). Then **COMMIT the uncommitted 149 tree**: `git add -A && git commit -m "236a: SF
   records corrected to the true 2 km town box (the 148 '4 km' was a hw miscalculation) + full lead-doc
   SF section (3 staged rows, all drops with reasons, Vioget 1839 lead, Ringgold not on Commons, Henry
   Bill = 236b lead) - tests 7/7, 10/10 evidence green"` (tick NO boxes yet: box 3 stays open until
   Nashville is staged; the Vioget row is a bonus within box 3's "verified before use" scope - box 1
   stands as is).
2. **Stage the Vioget 1839 row** (the 146 pattern, mechanical - everything verified in step 5 above):
   `fit/src_us_cities.py` SOURCES += `"vioget_1839": dict(rows=[("File:1839 Plan of Yerba Buena (Jean
   Jacques Vioget).jpg", "Q62", "San Francisco", dict())], p="plan", label="{name}, the Vioget plan
   (1839, the first plan of the old town)")` (NO date dict - page date = drawing date 1839); docstring
   += the Vioget mention ("the 1839 Vioget plan (first plan of the old town), the 1849 Eddy ...").
   Live: `stage` (expect "0 new sites, 1 new pictures" - Q62 already staged), `--verify` (expect
   unchanged, 3 QIDs), offline `--check` (expect **11 rows, 11 pass**) + `--golden` (regenerates). Tests:
   the 10->11 row asserts (2 places: check-staged test's "evidence: 10 rows, 10 pass" -> 11/11 + its
   PASS-line list += `"san-francisco-q62|File:1839 Plan of Yerba Buena (Jean Jacques Vioget).jpg"`; the
   evidence test's same line; the qid-table test's `years` dict += the Vioget title -> 1839 - note the
   test builds `want` from SOURCES so it self-scales, but the `years` dict and PASS-line lists do not).
   Lead doc: the Vioget subsection's "to stage next" -> STAGED bullet (with the file facts) + offline-
   check transcript -> 11 PASS lines. DECISIONS entry; commit as 236a.
3. **Then Nashville (Q23197)** (the 145-149 pattern): live research first (re-verify Q23197 via
   pipeline/catalog_wd: P625 (-86.7744, 36.1622) downtown east of the Cumberland vs the old 1790s town
   at the Cumberland/Tennessee confluence ~(-86.788, 36.166); grep no existing site uses Q23197 /
   nashville-q23197; find the early town plans + **Fort Negley's Civil War plans** (own kind-"fort"
   site, own QID - verify that QID too, 1600 m fort box, 3DEP LiDAR candidate as in 203a); thumbnails +
   metadata + gate window; **verdict in DECISIONS BEFORE editing**). Then apply in one session
   (SITES += Q23197 (+ the fort site); live --verify (4 QIDs) + stage; offline --check + --golden; tests;
   lead-doc Nashville section). **When both are staged: tick box 3, set Status: done** (the driver
   re-checks suite green; the full suite has the 1 pre-existing failure test_fit_queue.py::
   test_placement_gestures_and_save_in_the_browser - agent c's 307 work, not mine).

### Gotchas (all still true)
- Tests OFFLINE only (socket-blocked fixture in the test file); run ONLY my two files (test_src_us_cities
  .py + test_region.py) - never the full suite (the pre-existing test_fit_queue failure is agent c's).
- Named-place gate: title + the 600-char-truncated desc of c.info(); all staged SF titles print "San
  Francisco" IN THE TITLE (gate-safe); the Vioget file is gate-safe via the DESC (checked live). File
  titles case-sensitive. c.info batches of ~10 titles are fine (the 414 was 50 long titles).
- stage() is idempotent on (site, title) and appends a NEW site row only for unseen ids; re-running
  stage after this session is a no-op. The known-date swap runs before c.keep(); a missing title fails
  loud. To change a STAGED row's note (as done here) you hand-edit the jsonl row (stage() has no update
  path) then re-run --golden - keep SITES and the staged row in lockstep (pull the string from SITES).
- Town box: kind "town" -> width_m = height_m = 2000 -> a **2 km x 2 km** box centered on the point
  (site_bbox hw = width_m/2). Do NOT write the 4 km version again. Do NOT add a box_m override (the
  NY/DC precedent: oversize sheets end as review items, not wider boxes); specs/site_boxes.json is not
  in this task's Touches.
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, web/data/sites.json) -
  that is 236c. The REGION_NAME line in pipeline/build_catalog.py is already committed.
- Do not "fix" pipeline/commons.py's NO regex (not in Touches).
- /tmp still holds: ussf_verify.out / ussf_check.out / ussf_stage.out (the 148 transcripts - check.out
  shows 10 rows; it predates this session's note fix but the PASS lines are identical), ussf_meta*.out
  (exact drop titles - all now in the lead doc), ussf_search*.out, sf_0..sf_7.jpg (147 thumbnails),
  **yb1839.jpg + yb1839_small.jpg** (the Vioget 1839 scan, 2400x2107 - throwaway; the original URL is
  in the lead doc's Vioget subsection via the file page). The lead doc now carries every title needed.
