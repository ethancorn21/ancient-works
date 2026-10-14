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

(2026-10-13, iteration 146, agent a - **Washington DC applied and staged.** The staged set is now NY
(4 plans) + DC (3 plans) = 7 rows on 2 sites; --check 7/7, golden regenerated, tests 7/7 green, lead
doc has the full DC section (STAGED/DROP verdicts + the Boschke "exactly why" not-staged record). Box 3
stays open: **San Francisco (Q62), then Nashville (Q23197)** are the remaining two owner-named cities -
each needs live research first, then the same apply/stage/check/golden/test/doc pattern this session
used. When both are done: tick box 3, Status: done.)

### What this session did
1. fit/src_us_cities.py: SITES += Q61 (id washington-q61, name "Washington, D.C.", named "Washington",
   lon/lat = the single P625 (-77.036667, 38.895), place "District of Columbia", region "United
   States", kind "town", wikipedia, note = aerial ground + 35 km ring review-item case + the ring's
   forts as the catalog's existing sites); SOURCES += le_1791 / ellicott / defences_1865 (all p="plan";
   the L'Enfant row carries dict(date="1791")); docstring extended.
2. Live: --verify clean (2 QIDs; Q61 = one P625 = the table point, P373, P131 Q3551781, enwiki, first
   search hit = Q61 itself - no trap; one SSL-handshake timeout, retried by c.get; the 144 gzip-200
   pitfall did not recur). stage: "1 new sites, 3 new pictures; build (236c): washington-q61".
   L'Enfant swap fired: date "1791" / date_commons "1792" (page dates the Mar. 1792 first printing of
   the L'Enfant plan; the 1791 manuscript is at NARA, not on Commons).
3. Offline: --check no join problems, "evidence: 7 rows, 7 pass, 0 fail, 0 no-tie"; --golden rewrote
   tests/golden/src_us_cities_sample.json (2 extras / 7 files / 7 classified).
4. Tests (tests/test_src_us_cities.py): per-QID named dict {Q60: "New York", Q61: "Washington"},
   set(table) == {Q60, Q61}, extras ids [new-york-q60, washington-q61], years dict += 3 DC titles,
   L'Enfant swap assert, both 4-rows asserts -> 7, the 3 DC PASS lines. The three_states test
   self-scales (no edit, as predicted). 7/7 green with tests/test_region.py, offline.
5. docs/lead_us_cities.md: header "both cities staged; SF and Nashville later"; QID-verification
   block = this session's 2-QID --verify output; prep-verified list now Q62/Q23197 only; the full
   `## Washington DC (Q61)` section (site point; extent decision same as NY; ring + forts - no new QID
   work, the catalog already has the individual fort sites Q3077774/Q5471024/Q18150335/Q61784495/
   Q14691922 part_of Q5124610; the three STAGED/DROP per-plan sections with full drop reasons; the
   Boschke "not staged, and exactly why" section: 1861/1880 editions print "Washington" only past the
   gate's 600-char window, 1857 1st ed the only gate-passing file but the NO heuristic's "portrait"
   word false-positives on a vignette + low-res).

### EXACT next step (one session: SF research + apply; the 145/146 pattern)
1. **Live research** (throwaway scripts in /tmp; record the verdict in DECISIONS.md BEFORE editing,
   as 145 did): re-verify Q62 live (pipeline/catalog_wd is the robust path; c.get is flaky) - two
   P625 values ~450 m apart both downtown, first search hit = Q62 (144: no trap, re-confirm); check
   no existing site uses Q62 or the id san-francisco-q62 (grep data/catalog/sites.jsonl,
   data/catalog/extras.jsonl, web/data/sites.json - "San Francisco" hits will be a CA county and
   probably nothing else). **Pick the site point against the files**: the 1849 Eddy and Ringgold
   plans draw the old town's tip (bay-front, today's Financial District / Yerba Buana) which is
   SOUTH of both P625 points - so take the southern P625 or refine to the tip; decide from the
   files' drawn extents, don't guess.
2. **Leads** (verify each: original or facsimile, the drawing's date, licence, resolution; the
   named-place gate needs the city in the title or the 600-char desc - check c.info() before
   staging): the 1849 Eddy plan (the survey), the 1849 Ringgold plan ("A General Plan of the Town of
   San Francisco..."), 1850s city plans (the growth around the bay). Known-date swap where the page
   lost the drawing's date; drops recorded with exact reasons in the lead doc.
3. **Apply**: SITES += Q62, SOURCES entries (labels per plan), docstring; live --verify + stage;
   offline --check (expect 10 rows if 3 SF rows) + --golden; tests (per-QID named += Q62: "San
   Francisco", years, PASS lines, table {Q60, Q61, Q62}); lead doc `## San Francisco (Q62)` section
   (same shape as the DC one: site point, extent decision, staged/drops, fit notes); DECISIONS.md;
   commit as 236a.
4. **Then Nashville (Q23197)** the same way: P625 (-86.7744, 36.1622) downtown vs the old 1790s town
   at the confluence ~(-86.788, 36.166) - pick the point against the files; leads: early town
   plans; **Fort Negley = its own kind-"fort" site, its own QID** (a separate verify; the 3DEP
   LiDAR candidate as in 203a).
5. **When both are staged**: tick box 3, set Status: done. The driver re-checks (suite green).

### Gotchas (all still true)
- The named-place gate sees ONLY the title + the 600-char-truncated desc of c.info() (stage and
  check both use it) - "in the caption" must mean visible inside that window; that is why every
  chosen DC file prints the city IN THE TITLE and why all Boschke editions fail.
- fit/src_us_cities.py has NO BOOKS machinery; stage() is idempotent on (site, title); row `cat` is
  null; the known-date swap runs BEFORE c.keep() (the sources.py/van-Deventer order).
- Commons File titles are case-sensitive (PITFALLS); Wikidata through the proxy is flaky (gzip 200s,
  or SSL-handshake timeouts like today - c.get retries; pipeline/catalog_wd is the robust path);
  CM/WD constants in pipeline/commons.py.
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, web/data/sites.json)
  - that is 236c. The REGION_NAME line in pipeline/build_catalog.py is already committed.
- Do not "fix" pipeline/commons.py's NO regex (not in this task's Touches) - that is why the Boschke
  1857 sheet is recorded, not staged.
- The /tmp usdc_* scripts hold the DC transcripts (throwaway); the SF/Nashville research transcripts
  go to /tmp the same way.
- The full suite has 1 pre-existing failure (test_fit_queue.py::test_placement_gestures_and_save_in_
  the_browser - agent c's 307 work, not mine); run my two test files offline (socket-blocked
  fixture), not the whole suite.
