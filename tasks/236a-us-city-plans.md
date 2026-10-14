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

(2026-10-13, iteration 151, agent a - **Nashville RESEARCH COMPLETE (live, no repo edits). Verdicts in the
DECISIONS entry below/next: stage 4 rows on a new nashville-q23197 site - 1804 Clayton map (date swap 1804),
1860 Haydon, the O.M. Poe LOC map (date swap to the LOC-verified year), the 1861-65 Official Histories atlas
plate CXIV with Fort Negley (date swap to the atlas year). NO Fort Negley fort site: no fort-only plan on
Commons (photos/views only; the 3 Fletcher views = 236b leads). Tests last ran 7/7 green in 150 - nothing
changed since, so still 7/7. NEXT SESSION: the two web date checks, then apply like 145-150, then tick box 3.**

### Current state
- Q23197 + Q5471744 verified live via pipeline/catalog_wd (the robust WD path; catalog_wd's disk cache
  holds the answers in data/raw/catalog/wd/ so re-runs are free): both clean - label, single P625, P373,
  P131, enwiki, first name-search hit with P625 = the QID itself (no trap). Exact greps: no Q23197, no
  "nashville", no Q5471744 in data/catalog/sites.jsonl, data/catalog/extras.jsonl,
  data/catalog/extras_us_cities.jsonl or web/data/sites.json (the only canonical hit is the unrelated
  "Nashville I" gorget at castalian-springs-mound-site-q5049584 - no collision). Q5471744's P373 = Commons
  category "Fort Negley" (12 files: photos + the 3 Fletcher litho views; no plan).
- fit/src_us_cities.py UNCHANGED (3 sites Q60/Q61/Q62, 11 rows; staged 3/11/11; --check 11/11; golden 3/11/11).
  The stage/verify/check/golden pattern needs no structural change.

### EXACT next steps: apply the 151 verdicts (the 145-150 pattern), then done
1. **Two web date checks FIRST (the only research still open):**
   a. LOC item https://www.loc.gov/item/2003630459/ for the Poe map (page says only "1860s" precision 8; the
      map's own signature reads "O.M. Poe, Capt. & Actg. Chf. Eng'r" and a year I read as 1864 in the
      1280px thumbnail). -> known-date swap dict(date="<year>") (the 1791 L'Enfant precedent).
   b. The atlas behind the Defenses plate: David Rumsey image 1780.113 / group 1780.000
      (https://www.davidrumsey.com/loc/1780.113 404'd - try the group page or web-search "Official Histories
      of the United States Armies 1861-1865 atlas" + "Bien" / "Plate CXIV" / "Fort Negley"; the plate header
      reads "ATLAS TO ACCompany THE OFFICIAL HISTORIES OF THE UNIED STATES ARMIES 1861-1865, PLATE CXIV").
      Confirm the atlas publication year (1884/85?) for the row's date swap; the panels carry 1864/1865
      surveyed dates - record both in the lead doc. **If neither date can be verified, DROP the plate** (it
      has no page date and NO PLANWORD in its title, so undated keep() would fail) and stage the other 3.
2. **Apply (one session):** fit/src_us_cities.py: docstring += Nashville; SITES += Q23197 (id
   "nashville-q23197", name "Nashville", named "Nashville", kind "town", region "United States", place
   "Davidson County, Tennessee", wikipedia https://en.wikipedia.org/wiki/Nashville,_Tennessee, aerial note
   like the others + the oversize-sheet review-item note: the Haydon/Poe/Defenses sheets span the city and
   its fort ring far beyond the 2 km box -> likely review items, the NY 1811 / DC 1865 ring precedents - no
   extent field: the extras row has no such field (pipeline/catalog.py:686 sets extent_m from the site's
   box, not from the row); SOURCES += clayton_1804 (dict(date="1804")), haydon_1860, poe (dict(date="<1a>")),
   defenses (dict(date="<1b>")), all p="plan"). **Site point:** the 1804 map (the oldest drawing) shows the
   town at the Cumberland/Tennessee confluence (thumbnail: the grid between the Cumberland and Rich Branch,
   old fort at the corner, White Hall, Nashville Inn) - west of the P625 downtown (-86.7744, 36.1622, which
   sits EAST of the Cumberland). Decide P625 vs a refined point at the old town's center (the 147/148
   precedent: center of the drawn extent, e.g. Nominatim-verified midpoint of the confluence corner and the
   1804 town's far edge) so the 2 km box (hw = width_m/2 of the 2000 m town kind) covers the old town;
   whichever is chosen, all P625s are <50 km away (no --verify flag) and the evidence tie stores the table
   point (dist_m 0.0) so --check is offline-safe. Record which + why in the lead doc.
3. **Run:** live --verify (4 QIDs, expect no flag, no trap) + live stage (expect "1 new sites, 4 new
   pictures; build (236c): nashville-q23197") + offline --check (expect 15 rows, 15 pass) + --golden
   (4 extras / 15 files / 15 classified). Live under .venv/bin/python; --check plain python3.
4. **Tests:** tests/test_src_us_cities.py - row asserts 11->15, PASS-line list += 4, qid-table += Q23197
   (incl. the point decision), extras ids += nashville-q23197, years dict += the 4 titles (1804, 1860,
   <poe year>, <atlas year> - the two swaps give the known years, not the page values; the 1804 row's
   date_commons is "1880", the plate's is empty), named_by_qid += {Q23197: "Nashville"}; then
   `.venv/bin/python -m pytest tests/test_src_us_cities.py tests/test_region.py -q` (expect 7/7; the
   full-suite caveat stands: agent c's test_fit_queue failure).
5. **Lead doc:** docs/lead_us_cities.md += `## Nashville (Q23197)` (site point + decision, per-candidate
   STAGED/DROP with exact titles + reasons, the Fort Negley record: no plan on Commons, Q5471744 facts,
   the 3 Fletcher views as 236b leads, the 15-PASS transcript). Header: "four cities staged; box 3 done".
6. **Done:** tick box 3, set Status: done, commit as 236a. (236b bird's-eye and 236c consolidation are
   separate tasks.)

### STAGED verdicts (4 rows, all print "Nashville" in the title - gate-safe; all Public domain)
1. `File:1804 Map of Nashville published 1880.jpg` (2557x1913, page date "1880") = the 1804 map from the
   notes of Mrs. Temple, daughter of Dunc. Robertson, as engraved in W. W. Clayton's "History of Davidson
   County, Tennessee" (1880). Thumbnail looked at: the 1790s-1804 town at the confluence (Cumberland + Rich
   Branch), Court House, Jail, the "former Fort" (D. Cross's owner), White Hall, Nashville Inn, Cemetery,
   Capitol Hill, the ferry landings, numbered REFERENCES list of the 20 buildings. THE early town plan.
   **Known-date swap dict(date="1804")** (page date 1880 = the book's publication, not the drawing).
2. `File:1860 Haydon map of City of Nashville and Edgefield.jpg` (10000x6082, page date "1860", John Haydon
   and Booth) = the 1860 plan of the city and Edgefield: street grid, ward boundaries, railroads, all
   buildings, 19 building vignettes around the border. No swap (page date = drawing date). Oversize sheet
   (city + Edgefield, ~5-6 km across) -> review-item note on the row.
3. `File:Map of Nashville, Tennessee. LOC 2003630459.jpg` (19690x11294, page date "1860s" precision 8,
   artist "United States. Army. Military Division Of the Mississippi. Chief Engrs. Office; Poe, O. M.
   (Orlando Metcalfe)") = the O.M. Poe pen-and-ink-on-cloth survey map of the whole city: every building,
   contour lines, the Cumberland, the railroads; signed "From Chief Eng'rs Office, H'd Qu'rs Mil'y Div'n of
   the Mis., O. M. Poe, Capt. & Actg. Chf. Eng'r" + a year (1864 per the thumbnail - confirm on the LOC
   item page). **Known-date swap** to the verified year. Oversize sheet -> review-item note.
4. `File:Defenses of Chattanooga, Tenn. Battery Erwin ... Battery Coolidge. Defenses of Nashville, Tenn.
   Capitol (IA dr defenses-of-chattanooga-tenn-battery-erwin-battery-coolidge-defenses-01104241).jpg`
   (1536x886, NO page date, artist "United States. War Department / Julius Bien & Co. / Morton, J. St.
   Clair; Tower, Zealous B.; Willett, James R.; Cowles, Calvin D.; Davis, George B.; Kirkley, JAW.; Perry,
   Leslie J.") = PLATE CXIV of the "Atlas to Accompany the Official Histories of the United States Armies
   1861-1865": nine fortification plans - Chattanooga Battery Erwin + Battery Coolidge, and Nashville:
   the Capitol, Fort McCook, **Fort Negley (panel 5: plan + section on line A-B + magazine section,
   "Scale of Feet")**, Fort Morrison, Fort Hill (with a small "Plan of Nashville, Tenn."), Fort Nashville,
   the Nashville Heights. This IS the Fort Negley fortification-plan lead, but as a city-defences sheet
   (7 of 9 panels are Nashville) -> staged on the CITY (the DC 1865 ring precedent: Barnard's ring map
   staged on Q61, not on a fort). **Known-date swap** to the atlas publication year (undated title has no
   PLANWORD, so the swap is what lets keep() pass).

### DROP verdicts (record these exact reasons in the lead doc)
- `File:Map of Nashville in 1804 created by James Burns from notes of Mrs. Temple daughter of Dunc.
  Robertson.jpg` (1018x704, page date 1906-09-01) = the SAME 1804 plan as the staged Clayton file (a later,
  smaller copy) - one row per plan (the Ratzer re-engraving precedent).
- `File:Detail of map of Nashville Tennessee in 1854.jpg` (1752x1168, 1854, A. W. Putnam's History of
  Middle Tennessee) = a cropped book detail, not a full sheet - too small to carry a fit.
- `File:1888 Sanborn Map of the Eighth Avenue South Reservoir in Nashville TN.jpg` (491x572, 1888) =
  a fragment, too small.
- `File:New map of Nashville, Tennessee. LOC 75695990.tif` (10218x6688, 1916, Marshall & Bruce Co.) =
  outside the 1660-1880 window (236's goal), a commercial street-railway plan.
- `File:Map of the battle of Nashville, dec. 15th & 16th 1864 LOC 99447244.jpg` and `.tif` (2550x2117,
  1887, James Cowen, from Century Illustrated Monthly 1887, 1:110,000) = a small-scale BATTLE map (1887,
  outside the window), not a city/fortification plan.
- `File:Civil war battlefield maps - nashville and franklin 1895.jpg` (10056x6183, page lost the date;
  artist "Julius Bien & Co. Lith NY"; desc "Vintage Civil War Map detailing various battles") = a
  battlefield map of two battles (look at it once via its Commons page before dropping, but expect DROP:
  battle map, not a city plan; 1895 outside the window).
- `File:Fort negley 1864.jpg` (800x600, undated, George Barnard photo) = a photo, not a plan (keep()
  fails: undated + no PLANWORD in title). NOTE the lowercase "negley" - exact title from the search.
- `File:Nashville, Tenn., from Fort Negley looking northeast LCCN2007662878.jpg` (1024x505, Barnard 1864
  albumen photo); `File:Looking East from Fort Negley, Nashville, Tenn, by Webster & Albee.jpg`/.png
  (ca. 1890 photos, empty desc); `File:Negley Ruins.jpg` (2019 CC BY-SA modern photo); `File:Fort Negley
  Park outside Nashville, TN.jpg` (modern) = all photos, not drawings.

### 236b leads (do NOT stage here - bird's-eye views)
The three 1864 Fletcher lithograph VIEWS of Fort Negley (drawn by W.H.H. Fletcher of the 12th Battery Ind.
Vols., Nashville; the SE one inscribed "Filed Dec 31, 1864"; all Public domain, date field "1864";
"Fort Negley" in the title - gate-safe for 236b):
- `File:South west view of Fort Negley LCCN2003655690.jpg` (7950x3822) and `.tif` (7964x4356)
- `File:North west view of Fort Negley LCCN2003655670.tif` (7964x4356)
- `File:South east view of Fort Negley LCCN2003655689.jpg` (8082x3978)
Record them in the lead doc as 236b's (the Henry Bill 1856/1858 precedent).

### Gotchas (all still true)
- Tests OFFLINE only (socket-blocked fixture in the test file); run ONLY tests/test_src_us_cities.py +
  tests/test_region.py - never the full suite (the pre-existing test_fit_queue failure is agent c's).
  Live commands under .venv/bin/python (module top stays stdlib-only; commons -> aw needs numpy).
- Named-place gate: title + the 600-char-truncated desc of c.info(); all four Nashville candidates print
  "Nashville" in the TITLE (gate-safe). File titles are case-sensitive - use the exact strings above.
- The Defenses-plate title has NO PLANWORD: keep() passes only via the known-date swap (stage() swaps
  before keep()). If the atlas year cannot be verified, DROP the plate (staging the other 3 still satisfies
  box 3 - the four owner-named cities are staged; the plate is a lead, not a requirement).
- stage() is idempotent on (site, title); a missing title fails loud. To change a STAGED row's note later:
  hand-edit the jsonl row, keep SITES in lockstep, re-run --golden.
- Town box: kind "town" -> 2000 m -> a **2 km x 2 km** box centered on the point (hw = width_m/2). No
  box_m override (specs/site_boxes.json not in Touches). No Fort Negley fort site: a staged site without a
  picture fails check_staged(); if a fort-only Negley plan appears on Commons later, Q5471744 (P625
  (-86.774658, 36.145097), P131 Nashville, enwiki Fort Negley, no trap) is the verified candidate with the
  1600 m fort box (the DC forts precedent) and a 3DEP LiDAR candidate (203a).
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, sites.json) - that is
  236c. The REGION_NAME line in pipeline/build_catalog.py is already committed.
- Do not "fix" pipeline/commons.py's NO regex (not in Touches).
- /tmp/usn_* (this session's scripts, search transcripts, meta dumps, thumbnails) were session-scoped and
  are gone; the entries above carry every title/size/date/reason. catalog_wd's disk cache keeps the WD
  answers free to re-run.
