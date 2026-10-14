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

(2026-10-14, iteration 169, agent a, written at the context limit. RESEARCH session, the
151/152/163/164/165/168 pattern: no repo file touched, staged files still 3/11/11, no edits to
fit/src_us_cities.py or the lead doc. Baseline 7/7 (tests/test_src_us_cities.py +
tests/test_region.py) green before research. All session crops live in /tmp/nash168/
(haydon.jpg, clayton1804.jpg, cbx*.xml, and NEW: loc2003630459.jpg 28.8 MB 19690x11294,
defnash1895.jpg 1536x886, plus z_*.png crops; if re-download is needed, get URLs from
commons.info() on the titles "File:Map of Nashville, Tennessee. LOC 2003630459.jpg" and
"File:Defenses of Chattanooga, Tenn. Battery Erwin ... Battery Coolidge. Defenses of Nashville,
Tenn. Capitol (IA dr defenses-of-chattanooga-tenn-battery-erwin-battery-coolidge-defenses-
01104241).jpg" - upload.wikimedia.org with a browser UA).

### MAJOR REVISION: the Haydon 1860 sheet is a decorative composite - the 164/165 premise "the
sheet is NORTH-UP" is WRONG, and the 165 route step 1 (3-anchor least squares over
confluence + capitol + reservoir) is DEAD
- The labelled "C U M B E R L A N D R I V E R" band runs across the sheet's MIDDLE (full-sheet
  y~3900-4300 for x~3160-6300), the dense downtown core sits NORTH of it (x~3250-5750,
  y~2700-4250) - geographically correct (the CBD is north of the Cumberland). BUT the blue
  TENNESSEE arm enters from the sheet's upper-LEFT (map-NW) and the combined river exits
  lower-LEFT (map-SW): the map's V at (3288,4302) is a right angle while the real confluence
  is nearly a straight line (Tennessee from SSE, combined river WNW). No single rotation fits
  all three arms -> the rivers are bent for composition. The compass rose (full-sheet
  ~(7185,1425)) is a decorative 8-point star with a quill-arrow through it, NO letter labels -
  unusable for orientation. Title block (bottom-left): "CITY OF NASHVILLE AND EDGEFIELD,
  DAVIDSON COUNTY, TENNESSEE. Published by Hayden and Booth. 1860. SCALE 400 FEET TO 1 INCH."
- The sheet is a "tacked-up" composite of plates at different rotations: the dense core
  (TAYLOR/SPRUCE/HIGH/CHERRY/COLLEGE/MARKET/WATER/FRONT/ADAMS streets, capitol, Nashville
  Academy, Market Square/City Hall) is one plate; the OVERTOWN/EDGEFIELD diagonal grid
  (OVERTON/FRANKLIN/MIDDLE/TAYLOR ST, CITY HOSPITAL, Queen's Hotel, FRANKLIN TURNPIKE,
  Tennessee & Alabama R.R.) is bottom-LEFT; another diagonal grid (BERRY/WHITFIELD/...)
  bottom-right; the FILLMORE/BARROW/HICKORY/OAK/FULLER/GALLATIN grid south of the river; the
  "Shelby" floodplain; the red "Corporation Line" (1860 city boundary) around the core; a
  REFERENCES legend (full-sheet (4885-5125, 3775-4075)) and a CHURCHES list.
- CAPITOL pin RE-CONFIRMED at (4880,3193) (165 stands): my 169 attempt to re-pin it to
  (4288,2982) was a scale miscalc (the wide crop (2500,2500)-(6500,5200)@1.5x displayed at
  2000 wide means full-sheet = 2500 + display*2, NOT *1.5).
- Consequence: the Haydon map CANNOT carry a whole-sheet georef. It is still usable (a)
  qualitatively - the core plate = the modern CBD - and (b) for the site note's extent
  estimate, from labelled landmarks (Franklin Turnpike = Franklin Pike, the Wesleyan College
  green block = the later Vanderbilt hill, "Residence of J.B. Hayes near Nashville", the
  Howard School, the T&A RR line, the red Corporation Line).
- The 1833 waterworks "Reservar[y]" + University St grid (full-sheet (2740-3100,
  3430-3950), near the bent Tennessee arm) is no longer a candidate third anchor - it sits on
  a bent plate and its modern site was already not pinnable (168: no University St on the west
  bank; modern University St is EAST of the river). DROP it.

### Clayton 1804 re-read (fresh eyes this session) - THE georeferenceable plan
- Sheet 2557x1913. "NASHVILLE IN 1804. From Notes of one then resident, (Mrs Temple, Daughter
  of Genl Robertson)." A building INDEX "REFERENCES" 1-20 tops the sheet (An Old Yellow
  Frame..., Market 40 feet long, Court House, Stocks, Jail with Picket Fence, Tulbot Tavern,
  Stone Tavern Captain Demumbrance, House McKane, D. Robertson, J. B. Craighead, William Tate,
  James Jackson, Tavern Eakin, Ferry and Keel-Boat Landing, ...).
- Labeled streets: "Present Broad St." (vertical, left-center), "Present Church St."
  (vertical, center), "Present Cedar St." (vertical, right-center), "Present summer Str"
  (horizontal, left), "Present College Str." (horizontal, TWO labels: left and right),
  "Market or Main St" (horizontal, center). Modern "Broad Street" = today's Broadway;
  College St survives.
- Freshly confirmed pins (full-sheet): fort "D. Cross's owner / Stone House / former Fort"
  centre (718,1345); "White Hall / former Fort / 2 story" (985-1062, 1478-1523); the
  "now. Capitol Hill" annotation (1393-1650, 1020-1050) points at a wooded hillock
  (1683-1817, 1000-1083) centre ~ (1750,1040) = the modern Capitol hill -> anchor B
  (36.1658290,-86.7842374) (+/-100 m); "W. Tate Occupant / now 1834 Walkers / Best House in
  town" (1088-1472, 1005-1110); "T. Napier occupant / Small 2 story Frame" hatched building
  (1510-1543, 837-860); "KNOB" (1453-1557, 953-977); "Dr. Henning's House & Office"
  (1498-1792, 1344-1421); "Nashville Inn / Mr Parker / 2 story Frame" (1485-1702,
  1472-1523); cemetery marker (2118,988) label (2112-2253, 986-1005); McNairy's spring
  (2112-2342, 870-896); "Sulphur Spring / Salt made of it" (2150-2432, 1158-1197); "Judge
  McNairy's since enlarged" (2099-2496, 678-736). The Rich Branch (labelled thin creek) runs
  from the springs to its Cumberland mouth at (2282,1597) - the 165 pin stands. The
  Cumberland hatched band crosses the bottom (y~1470-1600); the Tennessee enters from the
  bottom-LEFT; the combined river continues down-left. (On THIS sheet the river corner sits
  bottom-LEFT - the Clayton drawing's river geometry still needs a bent-river sanity check
  against OSM before the mouth anchor is trusted, but the fort + capitol-hill anchors do not
  depend on the rivers at all.)
- The drawn town extent (full-ink corners): roughly x 448-2496, y 678-1600 - from the
  Johnson's ferry house (left) through the fort, the core, to Judge McNairy's property
  (right) and down to the river band; the dense core (buildings 1-20) is x~718-1790,
  y~986-1575.

### The other two staged Nashville sheets (checked this session)
- LOC 2003630459 "Map of Nashville, Tennessee" (19690x11294, page date "1860s", pen-and-ink
  and pencil, fold-line relief, streets/railroads/all buildings/streams): a big 1860s
  building-by-building city map. NOT YET EXAMINED at any zoom - the z_loc_whole.png
  downsample (2500x1443) is in /tmp/nash168; look at it to estimate its geographic extent
  (city + how far out) for the site note. Expect the same order as Haydon (city + a few km of
  country) -> oversize vs the 2 km box -> review item, same as Haydon/1895.
- The 1895 Defenses sheet (1536x886 IA book page, "Nine b&w plans, some with sections. LC
  Civil War map", zoomable original at davidrumsey.com): ONE small "Defenses of Nashville,
  Tenn. Capitol" plan among nine on the page. The z_def_whole.png 2x view is in
  /tmp/nash168 - identify the Nashville panel and its drawn extent (city + the fort ring:
  Fort Negley at (36.145,-86.7747) ~1.9 km S of P625, plus the ring's other forts). At
  1536x886 for nine plans the Nashville panel is small - too small to georef, only to
  estimate the ring's span for the note. If the page scan is too small to read, fetch the
  David Rumsey zoomable original (the desc field links it) before giving up.

### VERDICT route (revised - this is the exact next step)
The site point no longer waits on the Haydon georef. The only plan that can be georeferenced
is the Clayton 1804 (the 1790s core), and it is the smallest of the four extents, so the
155/161 rule applies to it:
1. Fit a 2-anchor (or 3-anchor LSQ) similarity over the Clayton 1804: A = fort (718,1345)
   <-> (36.164167,-86.774444) (Q5471739); B = capitol-hill centre (1750,1040) <->
   (36.1658290,-86.7842374). ENU metres at origin (36.163,-86.775) (E=(lon-lon0)*111194.9266*
   cos(lat0), N=(lat-lat0)*110900; map complex z = x - 1j*y). Report scale (m/px), rotation
   (deg) and per-anchor residuals (2-anchor = exact by construction; a 3rd anchor to test:
   the Rich-Branch mouth (2282,1597) projected -> should land on/near the Cumberland bank
   east of the town core; if the projected mouth is >300-500 m off the river, suspect the
   hill-centre pin and re-read the "now. Capitol Hill" target).
2. Cross-check the rotation: the Clayton street grid (Broad/Church/Cedar vertical,
   Summer/College/Market horizontal) should rotate to the modern downtown grid orientation
   (the modern grid is rotated ~20-30 deg from compass; Nominatim College St / Broadway
   segments in the cbx dumps can verify 1-2 street directions).
3. Project the drawn extent corners (full-ink x 448-2496, y 678-1600; dense core
   x 718-1790, y 986-1575) -> geographic box.
4. VERDICT (155/161): point = P625 (36.162222,-86.774444) iff its 2 km box (hw 1000 m: lat
   36.1522-36.1722, lon -86.7844..-86.7644) covers the projected 1804 extent WITH margin;
   else point = the projected-extent centre, 5 decimals (147/148 SF precedent). My prior:
   the 1804 extent is ~1 km x 0.8 km centred near (36.163,-86.775) -> P625's box covers it
   with ~1 km margin -> point = P625. The other three sheets (Haydon, LOC 1860s, 1895
   ring) span beyond the box -> review items, per the NY-1811/DC-ring precedent; their
   extents go on the site note (examine z_loc_whole.png / z_def_whole.png for those).
5. Then the 165 route step 8 (APPLY), unchanged: SITES entry nashville-q23197 (name
   "Nashville", named "Nashville", kind "town", region "United States", place "Davidson
   County, Tennessee", wikipedia https://en.wikipedia.org/wiki/Nashville,_Tennessee, point =
   the verdict) + SOURCES rows for the 4 titles (Clayton swap dict(date="1804"); Haydon no
   swap; LOC 2003630459 NO swap (page "1860s" is the drawing date); Defenses swap
   dict(date="1895"), the "..." is literal) - then live --verify (4 QIDs: Q23197,
   Q5471739, Q5471744 + existing), stage (expect "1 new sites, 4 new pictures; build
   (236c): nashville-q23197"), offline --check (expect 15 rows, 15 pass), --golden, tests
   (row asserts 11->15, PASS-list += 4, qid-table += Q23197 point, extras ids +=, years dict
   += 1804/1860/1860/1895, named_by_qid += {Q23197:"Nashville"}), lead doc Nashville
   section (point + why; per-candidate STAGED/DROP; Fort Negley record; 15-PASS transcript;
   the Haydon composite finding; the 1895 panel extent), tick box 3, Status: done.

### Standing gotchas (unchanged, still true)
Tests OFFLINE only (socket-blocked fixture); run ONLY tests/test_src_us_cities.py +
tests/test_region.py; live commands under .venv/bin/python (module top stays stdlib-only,
commons->aw needs numpy); named-place gate = title + 600-char-truncated desc (all 4
Nashville titles print "Nashville" in the title - gate-safe); stage() idempotent on
(site,title), missing title fails loud; town box = 2 km x 2 km centred on the point (no
box_m override; specs/site_boxes.json not in Touches); do NOT write the canonical files
(236c; the REGION_NAME line in pipeline/build_catalog.py is already committed); do not
"fix" pipeline/commons.py's NO regex (not in Touches); Nominatim 1 r/s project UA
(pipeline/aw.py UA), live OSM browser UA (/map?bbox and /api/0.6/* alive per 164/168 -
retest per call; /map?bbox arg order minlon,minlat,maxlon,maxlat; the response root holds
BOTH node and way elements); Overpass dead (PITFALLS filed 168); after ANY full-suite run
restore `git checkout main -- docs/site_flow/307d_*.png` (PITFALLS filed 168). QID facts:
Q23197 (label "Nashville", P625 (-86.774444,36.162222), P373 ['Nashville, Tennessee'], P131
Davidson County Q1177705, enwiki "Nashville, Tennessee", first name-search hit = itself,
NOT in the catalog); Q5471739 Fort Nashborough (36.164167,-86.774444) precision 0.001;
Q5471744 Fort Negley (-86.774658,36.145097); no Fort Negley fort site is staged (no
fort-only plan on Commons - the 3 Fletcher 1864 views are 236b leads; a fort-only Negley
plan later -> Q5471744 with the 1600 m fort box). DROP list for the lead doc (151
DECISIONS entry): the Burns 1906 copy of the 1804 plan; the 1854 book detail; the 1888
Sanborn fragment; the 1916 LOC 75695990 .tif (outside the window); the two 1887 battle-map
files; the 1895 battlefield map (look once via its Commons page before dropping); all
Fort Negley photos.
