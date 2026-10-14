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

(2026-10-13, iteration 144, agent a - **New York is done end-to-end and committed.** Boxes 1/2/4/5 ticked.
Tests green 7/7 (test_src_us_cities 5 + test_region 2, offline). **Remaining work: stage Washington DC,
then San Francisco, then Nashville - one city per session, same pattern.** Box 3 stays unticked until
those three are staged or documented. Everything this session is committed; the tree is clean.)

### What this session did
1. **Ran the never-run tests**: one failure - the negative-control distance. The prep's computed
   10407617 m for (-74.006111,40.712778)->(12.33,45.44) was simply miscalculated; `evidence.hav_m`
   (R=6371008.8, the standard haversine) gives **6680986 m** (~6681 km, the true NYC-Venice distance).
   Fixed the assert and both docstring mentions ("~10408 km" -> "~6681 km"), and cleaned the sloppy
   `years and "..."` truthiness line the 143 hand-over flagged. Now 7/7.
2. **Live re-checks (network fine this session)**: the Ratzer 1776 re-engravings are NOT deleted -
   the prep's batch had the wrong title case ("City" vs lowercase "city"; Commons file titles are
   case-sensitive, the search index was stale). Live: `File:Plan of the city of New York by Ratzer,
   1776.jpg` (2202x1446 PD), `...in North America by Ratzer, 1776.jpeg` (563x760), btv (1 of 2)
   (11310x7795) + (2 of 2) (11310x5194) - all PD, dated 1776 -> documented DROPS (re-engraving of the
   same plan already staged as its 1767 original; one row per plan). 1811 grid files re-checked live:
   `Grid 1811.jpg` (250 px, page date 2005), `NYC-GRID-1811.png` (page date 1893 - a 19th-c reproduction
   of the 1807 provisional map), `Alphabet-City-area...png` (a detail crop) - all confirmed drops.
   The two Randel "surrounding country" atlas sheets (Philadelphia / Connecticut-and-Long-Island, page
   1821) are live but not New York pictures: their page DESCRIPTIONS carry the atlas title "The City of
   New York as laid out ... with the surrounding country" - the named-place gate checks name PRESENCE,
   never location, so a live record would wrongly tie them; the human reads such sheets (the lead doc
   says so).
3. **Wrote docs/lead_us_cities.md**: header (owner point, staging files, 236c's role, aerial ground,
   hand-recorded caption_coords), `## QID verification` (--verify output for Q60 + the prep-verified
   Q61/Q62/Q23197 facts + the recalled-QIDs-wrong-twice trap note), `## New York (Q60)` (site point,
   the extent decision, the four per-plan sections with STAGED/DROP verdicts, fit notes), `## Offline
   check`, and the DC/SF/Nashville lead sections.
4. **PITFALLS.md**: two new entries in the Wikimedia APIs section - (a) Wikidata through this machine's
   proxy intermittently returns 200s with a GZIP body urllib does not decode (json.JSONDecodeError char
   0; fixes: Accept-Encoding: identity, or use pipeline/catalog_wd.py); (b) Commons file titles are
   case-sensitive (the Ratzer 1776 "deleted" misdiagnosis). Added PITFALLS.md to this task's Touches
   (the 204/211/212 convention).
5. **Committed**, ticked boxes 1/2/4/5 (box 4 on the lead doc's later-session statements for DC/SF/
   Nashville; box 3 stays open until all four cities are staged or documented).

### EXACT next step - Washington DC (one session)
1. **Verify the DC leads live** (Commons `c.info` batches; for Wikidata use `pipeline/catalog_wd` -
   see PITFALLS (a)): the **L'Enfant plan 1791** (LoC - on Commons the LoC scans carry `LOC`-style
   titles, PD US-government; search "L'Enfant plan"), the **Ellicott engraved plan 1792**, **Boschke's
   topographical map 1857/1861**, the **Barnard 1865 Civil War defences** (forts). For each candidate:
   size, page date, license, description; judge original-vs-redraft and one-row-per-picture as in the
   NY section. If a named lead has no good Commons file at all, say so in the lead doc (box 4's
   "exactly why" branch) - do not invent a substitute.
2. **Add Q61 to SITES**: id `washington-q61`, name "Washington, D.C.", named "Washington" (the short
   form the captions print - check each file's title+desc actually prints it; the gate is
   presence, never location - the Randel lesson), lon/lat = P625 (-77.036667, 38.895, the old
   L'Enfant core - refine only if the staged files' drawn extent argues otherwise), place
   "District of Columbia", wikipedia, note (aerial ground + the 1865 defences ring ~35 km = review
   item / own fort sites).
3. **Stage** (live; re-runs are idempotent), run `--check`, extend the lead doc with a proper
   `## Washington DC (Q61)` section (replace the short lead section, same structure as New York).
4. **Update the tests**: `set(table) == {"Q60"}` -> add Q61; the HARDCODED `evidence: 4 rows` count
   and the four PASS lines in `test_check_staged_files_join_and_pass` -> grow them (the
   three_states test scales from the file lengths by itself); regenerate `--golden` (an intended
   change).
5. **Commit** as 236a. Then San Francisco (Q62: TWO P625 values ~450 m apart, both downtown; the
   1849 plans' old-town tip is SOUTH of both - pick the site point against the files at staging),
   then Nashville (Q23197: P625 downtown east of the Cumberland; the old 1790s town is at the river
   confluence ~(-86.788, 36.166) - refine; Fort Negley earthwork = its own kind-"fort" site, 1600 m,
   own QID, 3DEP LiDAR candidate like the 203a mounds).

### Gotchas
- `fit/src_us_cities.py` has NO BOOKS/book machinery (verify_qids runs over SITES); do not mirror it
  back in. `stage()` is idempotent on (site, title). The row's `cat` is null (all rows are the
  caption route). The known-date swap runs BEFORE `c.keep()` (the sources.py/vdD order, task 237
  aligns src_artists) - do not "fix" it back.
- The named-place gate (evidence_for) checks that the caption PRINTS the site's `named` short form -
  it never checks WHERE the named place is. A file whose description names the city but pictures a
  different region (the Randel surrounding-country sheets) passes the gate: a human reads those.
- Commons file titles are case-sensitive; always take exact titles from the search results (new
  PITFALLS entry), never from memory.
- Wikidata through the proxy is flaky (gzip 200s); Commons was reliable all session (new PITFALLS
  entry). `pipeline/commons.py` constants: `CM` (Commons), `WD` (Wikidata).
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, web/data/sites.json)
  - 236c. The REGION_NAME line in pipeline/build_catalog.py is already committed (236b adds the
  identical line; identical additions merge cleanly).
- Suite state at loop start (driver): 1 pre-existing failure,
  tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (agent c's 307 in-flight
  work on main - not mine). My two test files: 7/7 green this session.
