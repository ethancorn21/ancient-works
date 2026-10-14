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

(2026-10-13, iteration 145, agent a - **DC research is DONE and committed in DECISIONS.md; NO repo files changed this session** (tree clean at limit - the /tmp search scripts were throwaway). Everything below is verified live 2026-10-13. **Next session is mechanical: apply the verdicts to the module, stage, test, doc, commit.** NY remains done (boxes 1/2/4/5 ticked; box 3 stays open until DC+SF+Nashville are staged/documented.)

### DC verdicts (all live-verified; exact titles are case-sensitive - copy from this text, never retype)
**Site row:** `washington-q61` - name "Washington, D.C.", **named "Washington"**, lon/lat = P625 **(-77.036667, 38.895)** (Q61 has ONE P625, verified via `pipeline/catalog_wd` this session: label "Washington, D.C.", P373 'Washington, D.C.', P131 Q3551781, enwiki 'Washington, D.C.', first search hit = Q61 itself - no trap), place "District of Columbia", region "United States", kind "town" (2000 m box), wikipedia https://en.wikipedia.org/wiki/Washington,_D.C., aerial_ok true, note = aerial-photograph ground + "the 1865 defences ring spans ~35 km beyond the box -> likely review item; the ring's forts are candidate kind-'fort' sites (the catalog ALREADY has individual fort sites: Fort Bayard Q3077774, Fort DeRussy Q5471024, Fort Totten Q18150335, Fort Marcy Q61784495, Fort Foote Q14691922, all part_of Q5124610 'Civil War defenses of Washington, D.C.' - checked data/catalog/sites.jsonl)".

**STAGED (3 rows, Q61):**
1. `File:Plan of the city of Washington LOC 88694159.tif` (6426x5105, PD, page date 1792, desc "Printed from the same plate as the map appearing in The universal asylum, and Columbian magazine, Philadelphia, Mar. 1792 ... 1st printed edition of the L'Enfant plan") - **the L'Enfant 1791 plan as its 1792 first-printed edition** (the 1791 manuscript is at NARA, NOT on Commons - searched). **Use the known-date swap: `dict(date="1791")`** (drawing 1791; page 1792 kept as date_commons - same shape as the 1811 NY swap). Label: `{name}, the L'Enfant plan (1791, first printed 1792)`.
2. `File:Plan of the city of Washington in the territory of Columbia - ceded by the states of Virginia and Maryland to the United States of America, and by them established as the seat of their government, (NYPL b15255319-434417).jpg` (6300x4976, PD, 1792, "Scan by NYPL", Slaughter collection, Wheat & Brun 531) - **the Ellicott 1792 engraved plan (first official plan)**; no swap. Label: `{name}, Andrew Ellicott's plan (1792, the first official plan)`.
3. `File:Map of the defences of Washington. LOC 88690674.jpg` (2800x3802, PD, 1865, "From Atlas accompanying Official Records", Atlas v.2 pl. XXXIX no. 1) - **the 1865 Civil War defences map (the fortification ring)**; no swap; classified p_plan 1.0. Label: `{name}, the Civil War defences (1865 map of the fortification ring)`. Note on the row: ring ~35 km beyond the town box -> review-item case (Venice precedent).
All three print "Washington" IN THE TITLE (gate-safe; the gate only sees info()'s 600-char-desc truncation), all pass keep() (no NO-heuristic words in title or 600-char desc; years 1791/1792/1865 <= 1925).

**Boschke lead NOT staged - exact why (record in the lead doc; box 4's city level is still met, DC gets 3 rows):**
- 1861 2nd ed (the named "1857/1861"): `File:Topographical map of the District of Columbia LOC 88694013.jpg` (12313x12090, PD, 1861, "Entered ... 1861, by D. McClelland, Blanchard & Mohun...", Phillips Washington 947) - the caption prints "Washington" only at normalized position ~830 of title+desc, PAST the 600-char truncation stage()/check() use -> named-place gate fails offline -> not staged (fail-loud by design). Same for its DPLA twin `... - DPLA - 24d5b35dccb58b1f43e387a1ccb0f5cb (page 1).jpg` (12430x6367) + `(page 2).jpg` (12564x6338, PD, 1861; EMPTY desc).
- 1857 1st ed: `File:Map of Washington City, District of Columbia. Seat of the Federal Government. Respectfully Dedicated to the Senate and the (IA dr map-of-washington-city-district-of-columbia-seat-of-the-federal-governmen-12363000).jpg` (1457x1536, PD, David Rumsey) - only Boschke file whose TITLE prints the city (gate WOULD pass), but `commons.keep()` drops it: the desc says "a portrait of George Washington" (one of the map's 18 vignette illustrations) and matches the NO heuristic's "portrait" word - false positive (the map is not a portrait); also low-res for the large sheet. (commons.py is NOT in my Touches - do not "fix" the NO regex in this task.)
- 1880 3rd ed: `File:Topographical map of the District of Columbia LOC 88693460.jpg` (6260x6881, PD, 1880) - later edition; same gate failure (no "Washington" in title or 600-char desc).

**Other DC drops (record per-lead in the lead doc):** L'Enfant: `File:Plan of the city intended for the permanent seat of the government of t(he) United States - projected agreeable to the direction of the President of the United States, in pursuance of an act of LOC 91684074.jpg` (12524x9023, PD, **1991** = full-color computer-assisted facsimile of the 1791 manuscript, USGS/LoC/NatGeo - modern production, owner's standing rule), `File:Plan of the city intended for the permanent seat of the government of the United States - projected agreeable to the direction of the President of the United States... (14726320702).jpg` (2000x1354, CC BY 2.0, 2014 BPL photo of the **1882 Boogher redraft** - later redraft + CC photo), `File:L'Enfant plan original.jpg` (6426x5105 - duplicate of the 88694159 LoC raster, mislabeled finding-aid text), `File:L'Enfant plan.jpg` (4179x3404 - smaller duplicate), `File:L'Enfant map of Wash., D.C. LCCN2005691999.jpg` (1536x982, 1792 - small LoC copy), `File:L'Enfant Plan 1791 Square No 15.jpg` (450x336 - detail crop), `File:Plan of the City of Washington - NARA - 102278589 (page 14).jpg` (3086x3190, 1803, no desc - a different/later item, not the 1791 original). Ellicott: `File:Plan of the city of Washington in the territory of Columbia - ceded by the states of Virginia and Maryland to the United States of America, and by them established as the seat of their government, LOC 88694164.tif` (8824x6567, 1792 - page says "Facsimile"; duplicate of the same plan), `(NYPL b15385718-434422).jpg`/.tiff (duplicate NYPL copy), `...(8249620373).jpg` + `(cropped).jpg` (2000x1578, CC BY 2.0, 2012 BPL photo), `File:A Plan of the city of Washington in the territory of Columbia - btv1b53089832z (1 of 2).jpg` (9284x6544) + (2 of 2) (9338x6590, PD, book date c.1800 - book-page scans), `File:Plan of the City of Washington in the Territory of Columbia ceded by the States of Virginia And Maryland to the United (IA dr plan-of-the-city-of-washington-in-the-territory-of-columbia-ceded-by-the-st-00024059).jpg` (6480x4980 - the **Reid & Rollinson 1794/95 atlas copy, "not an exact copy"** = redraft), `File:Plan of the city of Washington. LOC 88694118.jpg` (1794 Morse/Stockdale) + `LOC 88694112.tif` (1798 Weld/Stockdale - later reprints), `File:Ellicott plan.jpg` (800x654 - too small). Defences: `File:Map of fortifications and defenses of Washington. LOC 88690671.jpg`/.tif (1832x2464, 1865, "Appendix A" - book-page copy of the same War Dept map), `File:Map of the environs of Washington - compiled from Boschkes' map ... LOC 88690673.tif` (17457x15796, 1865, Barnard/Boschke/Coast Survey, No. 187 L. - different compilation map, alternative), `File:Defenses of Washington, extract of military map of N.E. Virginia - showing forts and roads LOC 88690675.tif` (4582x5805, 1865, Delafield - NE-Virginia extract, not the ring map), NARA `Defenses of Washington. -Maps 1 through 12 accompanying General Barnard's report.- - NARA - 305800 (page 1..12).jpg` (1865, per-page scans small - the 12 sector maps of Barnard's report; per-fort detail source), 1862 earlier-state maps: `... - DPLA - 7db86d50c1170106213c63fbfbf34dda (page 1).jpg` (14840x13824) and `File:Topographical map of the original District of Columbia and environs showing the fortifications around the city of Washington LOC 88690604.tif` (10513x9635, Colton), NARA Brady photos (Fort Totten/Ft. Carroll/Fort Gaines - photos, not plans).

### EXACT next step (one session - apply, stage, test, doc, commit)
1. **Edit `fit/src_us_cities.py`** (NOT yet edited): SITES += Q61 entry (values above); add lists `LENEANT`/`ELICOTT`/`DEFENCES` (3 rows as above; L'Enfant row carries `dict(date="1791")`) and SOURCES entries `le_1791`/`ellicott`/`defences_1865` (all p="plan", labels above); extend the module docstring ("New York and Washington DC - ...; San Francisco and Nashville follow").
2. **Live**: `.venv/bin/python fit/src_us_cities.py --verify` (now Q60+Q61; WD via c.get may gzip 200 -> fall back to `pipeline/catalog_wd` for Q61 facts, already verified above) and `stage` (expect `staged: 1 new site, 3 new pictures`).
3. **Offline**: `--check` (expect NO join problems; `evidence: 7 rows, 7 pass, 0 fail, 0 no-tie`; 7 PASS caption_coords lines); `--golden`.
4. **Tests** (tests/test_src_us_cities.py): docstring; `set(table) == {"Q60","Q61"}`; extras ids `["new-york-q60","washington-q61"]`; per-QID named check (NY rows "New York", DC rows "Washington"); years dict += the three DC titles (1791/1792/1865); swap asserts += L'Enfant date "1791"/date_commons "1792"; both hardcoded `evidence: 4 rows, 4 pass` -> `7 rows, 7 pass`; add the 3 DC PASS lines to `test_check_staged_files_join_and_pass`; three_states test self-scales (no edit needed). Run: my 2 test files green (offline; socket-blocked fixture) - full suite has 1 pre-existing failure (test_fit_queue.py placement_gestures - agent c's 307, not mine).
5. **docs/lead_us_cities.md**: header line ("New York and Washington DC staged... San Francisco and Nashville in later sessions"); `## QID verification` += Q61 facts (above, or --verify output); REPLACE `## Washington DC (Q61) - later sessions` with the full section (site point; extent decision = same as NY: 2000 m town box, defences ring ~35 km -> review item, forts already individual catalog sites Q3077774/Q5471024/Q18150335/Q61784495/Q14691922 part_of Q5124610; the three STAGED sections with all DROPS and reasons as above; the Boschke not-staged explanation; fit notes - L'Enfant/Ellicott flat-plan similarity fit, defences = review item).
6. **DECISIONS.md + commit** as 236a. Then SF (Q62: TWO P625 ~450 m apart both downtown; the 1849 plans' old-town tip is SOUTH of both - pick the point against the files at staging), then Nashville (Q23197: P625 (-86.7744, 36.1622) downtown; old 1790s town at the confluence ~(-86.788, 36.166) - refine; Fort Negley = own kind-"fort" site, own QID, 3DEP candidate). Note: Q5124610 'Civil War defenses of Washington, D.C.' is a catalog item with member fort sites - a per-fort row for the defences lead is NOT this task (one row per picture on the city site; per-fort sites are the catalog's existing rows or a later task).

### Gotchas (carried from 144, all still true)
- NO repo files were changed this session (research only); the 144 state stands: boxes 1/2/4/5 ticked, NY staged, 7/7 green, tree clean.
- The named-place gate sees ONLY title + the 600-char-truncated desc of `c.info()` (stage and check both use it) - "in the caption" must mean visible inside that window; that is why the DC Boschke files all fail and all three chosen DC files print the city IN THE TITLE.
- `fit/src_us_cities.py` has NO BOOKS/book machinery (verify_qids runs over SITES); `stage()` idempotent on (site, title); row `cat` is null; the known-date swap runs BEFORE `c.keep()` (do not "fix" it back - task 237 aligns src_artists).
- Commons file titles are case-sensitive (PITFALLS); Wikidata through the proxy is flaky (gzip 200s, PITFALLS) - `pipeline/commons.py` constants `CM`/`WD`; `pipeline/catalog_wd.py` = robust WD path (disk cache + retries) with `api()`/`search()`/`labels()`.
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, web/data/sites.json) - 236c. The REGION_NAME line in pipeline/build_catalog.py is already committed.
- The /tmp scripts (/tmp/usdc_search.py, usdc_detail.py, usdc_round2/3/4.py + .out) are throwaway research; if still present they hold the full live transcripts.
- Do not stage the 1991 L'Enfant facsimile (91684074): modern production, owner's standing rule (no modern redraws presented as old); keep() drops it at 1991 anyway.
