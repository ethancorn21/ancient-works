Status: in-progress
# 236a: US city plans - New York, Washington, San Francisco, Nashville first
Depends on: none
Touches: fit/src_us_cities.py, pipeline/build_catalog.py, data/catalog/extras_us_cities.jsonl, data/commons/files_us_cities.jsonl, data/commons/classified_us_cities.jsonl, docs/lead_us_cities.md, tests/test_src_us_cities.py, tests/golden/src_us_cities_sample.json

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
- [ ] Verified before use (docs/lead_us_cities.md): per staged picture what it is, where it lives, the
      drawing's date (recorded on the row - an upload date is not a drawing date), original vs later redraft;
      unusable files (modern redraws, too small, no place tie, not free) listed with the reason.
- [ ] fit/src_us_cities.py holds the hand-checked file -> QID table: every QID verified against its label,
      P625 and enwiki link (the Barnard Castle trap: a name search alone gives the wrong place). A city
      whose plan covers more than the site box gets either an extent recorded on its row (check how
      pipeline/catalog.py sets extent_m and whether an extras row can carry one) or a district/fort site
      with its own QID - recorded which, and why, in the lead doc.
- [ ] Staged rows in this task's files only: extras_us_cities.jsonl (id, qid, name, lon/lat of the area
      the plan covers, region "United States", kind "town" or "fort", aerial_ok true, place, wikipedia,
      note), files_us_cities.jsonl (files.jsonl shape + 200 evidence field), classified_us_cities.jsonl
      ("plan", by hand). A city whose QID is already in the catalog gets picture rows for that site id.
- [ ] fit/evidence.py check passes offline on every staged row; all four owner-named cities are staged or
      the lead doc says exactly why one could not be.
- [ ] Test (no network): the staged files join, the evidence check passes, a golden sample of rows.

## Notes
- Ground: cities are aerial-photograph sites (aerial_ok true; bare-earth LiDAR erases streets). The street
  grid, shoreline, squares and church footprints carry the fit. Civil War forts are the exception: their
  banks may show on 3DEP bare earth (pipeline/aw.py), like the mounds in 203a.
- Templates: fit/src_van_deventer.py + docs/lead_van_deventer.md, fit/src_artists.py + docs/lead_artists.md.
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, sites.json) - that is 236c.

## Hand-over

(2026-10-13, iteration 143, agent a - **New York end-to-end done except: tests not yet run, lead doc not written, nothing committed yet.** All of this session's changes are in the working tree uncommitted (the harness keeps them): fit/src_us_cities.py, pipeline/build_catalog.py, data/catalog/extras_us_cities.jsonl, data/commons/files_us_cities.jsonl, data/commons/classified_us_cities.jsonl, tests/test_src_us_cities.py, tests/golden/src_us_cities_sample.json, tasks/237-artists-keep-order.md. All four acceptance boxes are still unticked; the next session ticks them after the work below.)

### State verified this session (all live 2026-10-13, network worked)
- **Staged**: `new-york-q60` in extras_us_cities.jsonl (Q60, "New York City", -74.006111/40.712778, region "United States", kind "town", aerial_ok, place "New York County, New York", wikipedia, note); 4 file rows (Castello TIF year 1660 with date "1660"/date_commons "[Date not available]" = the known-date swap fired; Ratzer 1767; Commissioners' 1811 with date "1811"/date_commons "1821" = swap from the page's publication date; Viele 1865); 4 classified rows (plan/plan/birdseye/plan, by "hand").
- **`--check` (offline) PASSES**: no join problems, `evidence: 4 rows, 4 pass, 0 fail, 0 no-tie`, exit 0. **`--golden`** wrote tests/golden/src_us_cities_sample.json.
- **`--verify` (Wikidata) clean output** (paste into the lead doc):
```
checked 2026-10-13 - 1 QIDs (Wikidata)
  Q60  'New York City'
      P625: [(-74.00611111111111, 40.71277777777778)]  (table site point: -74.006111, 40.712778)
      P373: ['New York City']
      P131: [('New York', 'Q1384')]  (table place: 'New York County, New York')
      enwiki: 'New York City'  (table wikipedia: 'https://en.wikipedia.org/wiki/New_York_City')
      search 'New York City': first hit with P625 is Q60 'New York City' (-74.00611111111111, 40.71277777777778)
```
  No P625 flag, no search trap (first hit with coordinates is Q60 itself).
- **`pipeline/build_catalog.py:REGION_NAME`** got the one line `"united states": "United States"` (required: tests/test_region.py globs every data/catalog/*.jsonl, incl. my new file; without it the region would display "US").
- **tasks/237-artists-keep-order.md filed**: src_artists.py:stage runs `c.keep()` BEFORE the known-date swap; sources.py (L186-191) and src_van_deventer.py swap FIRST (Zwolle precedent, keep() must judge the drawing's year) - latent in artists (its two rows pass keep() pre-swap via title years), my module uses the sources.py/vdD order.

### EXACT next step (one session, then DC/SF/Nashville)
1. **Run the tests** (never run yet): `.venv/bin/python -m pytest tests/test_src_us_cities.py tests/test_region.py -p no:cacheprovider`. test_region must pass with the uncommitted REGION_NAME line + staged file. If the negative-control distance assert is off by a digit, recompute with evidence.hav_m (I computed 10407617 m for (-74.006111,40.712778)->(12.33,45.44) with the same R=6371008.8 formula).
2. **Clean one sloppy line in tests/test_src_us_cities.py:~195**: `assert by_title[years and "File:Afbeeldinge ... .tif"]...` - `years and` is a truthiness accident that works but is dumb; make it a plain `by_title["File:Afbeeldinge van de Stadt Amsterdam in Nieuw Neederlandt (NYPL Hades-118555-54682).tif"]["date"] == "1660"`.
3. **Write docs/lead_us_cities.md** (pattern: docs/lead_artists.md, 302 lines): (a) header: owner's 2026-10-13 point (task 236), sources, the staging files, who does what (236c consolidates), aerial-ground note (bare-earth LiDAR erases city streets), hand-recorded caption_coords evidence note; (b) `## QID verification (checked 2026-10-13, re-run with .venv/bin/python fit/src_us_cities.py --verify)` - paste the --verify output above + the prep-verified facts for the not-yet-staged cities (Q61 DC P625 -77.036667/38.895 fine as old-core point; Q62 SF **TWO P625 values** ~450 m apart, old town tip ~(-122.40,37.78) is south of both so the site point is probably not P625 - refine against the files; Q23197 Nashville P625 downtown east of the Cumberland, old 1790s town at the river confluence ~(-86.788,36.166) - refine); for all four the first name-search hit with coordinates is the city itself (no trap); enwiki-infobox-coords cross-check came back empty from wp_api - not blocking; **the prep's recalled QIDs were wrong twice** (NY first remembered as Q30492 = the NUMBER "483", Nashville as Q15190) - the Barnard Castle trap in action; (c) `## New York (Q60)` - extent decision: extras rows CAN carry box_m (build_catalog.make_site: `entry.get("box_m") or box_m(entry)`, precedents biggs-site 800 / frankfort-works 1000) but `extent_m` is the synthetic-group spread (catalog.py, catalog_triage crop sizing), NOT the site box; DECISION: city sites keep the kind-"town" 2000 m box (NY's P625 box covers the 1660 plan's whole drawn Manhattan: harbour tip to ~19th St), the 1811/1865 sheets span the island beyond the box so their fits are likely to end review items (the Venice precedent, docs/lead_artists.md) - noted on the extras row + here, not as an extent field; Civil War forts = their own kind-"fort" sites (1600 m) with own QIDs in a later session; then the four map sections (What it is / Where the files live with STAGED + DROPS / Staged rows / fit note) - **the full STAGED/DROP verdicts are in my DECISIONS entry below** (the 1916 Adams/Stokes redrafts are the named trap: they honestly date 1916, would pass keep() as 1916 drawings, but they are redrawings - never stage as the 1660 original); (d) `## Offline check` with the --check output (the 4 PASS lines + summary, as in the artists doc); (e) short sections for Washington DC / San Francisco / Nashville: leads (L'Enfant 1791, Ellicott 1792, Boschke 1857/61, Barnard 1865 defences / Eddy + Ringgold 1849, 1850s plans / early town plans + Fort Negley), each a later session, same pattern.
4. **Add the PITFALLS.md entry** (Wikimedia APIs section; I could not edit it at the context limit): Wikidata through this machine's proxy intermittently returns 200 responses with GZIP bodies urllib does not decode (a few % of calls, worse with concurrent agents on the same IP) -> `json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`; fixes: send header `Accept-Encoding: identity` on the request, or use pipeline/catalog_wd.py (20 retries + 429 backoff - it got through in the prep session). The Commons API (commons.wikimedia.org) was reliable all session.
5. **Commit everything** as 236a (module, REGION_NAME line, the 3 staging files, golden, tests, lead doc, tasks/237). Ticks: box 1 after (3); box 2 after (3) (Q60 verified + extent decision recorded; the other cities' QIDs are recorded in the same section); box 3 after (1) for the NY rows (the box stays unticked until all four owner cities are staged or documented - DC/SF/Nashville pending); box 4 after (1) (the evidence check passes offline on every staged row); box 5 after (1).
6. **Then the other three cities** (later sessions, same pattern per city): verify leads live (Commons API: c.info batch; Wikidata flaky - use catalog_wd if --verify hits the gzip error), add each QID to SITES + SOURCES rows, stage, extend the lead doc, the tests scale automatically (the three_states test is written to grow; regenerate --golden for each intended change; update the evidence count asserts 4->N).

### Gotchas
- `fit/src_us_cities.py` has NO BOOKS/table_sites (src_artists' book machinery is not needed here) - verify_qids runs over SITES directly; do not "mirror back" in. The SITES entries carry `named` ("New York") = the short form the captions print; evidence_for returns None when norm(named) is not in norm(title+desc) and stage fails loud on that (src_van_deventer's gate) - check_caption uses the same rule, so stage and check can't disagree.
- stage() is idempotent on (site, title) - a re-run is safe and prints "staged: 0 new sites, 0 new pictures".
- The row's `cat` is null (no P373-category route; all four rows are caption route) - same as vdD's caption-route rows.
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, web/data/sites.json) - 236c.
- docs/site_flow/307d_*.png were driver-committed in 9c541a5 (not mine); the tree is otherwise clean apart from my uncommitted work.
- Tests last run: NONE for my new file (it is written but unverified). Suite state at loop start (driver): 1 pre-existing failure (tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, main's 307 in-flight work - not mine).
