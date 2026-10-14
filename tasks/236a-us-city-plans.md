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

(2026-10-14, iteration 172, agent a, written at the context limit. RESEARCH session,
145/147/151/152/163/164/165/168/169/170 pattern: NO repo file touched, staged files still
3/11/11, no edits to fit/src_us_cities.py or the lead doc. Baseline 7/7 (tests/test_src_us_cities.py
+ tests/test_region.py) was green at the 169/170 limits and the tree is unchanged since
(only the driver's merge 7f6d6f4 after 170). ### THE VERDICT IS NOW SETTLED - see below -
and the next session APPLIES it (the 146/148 pattern, the old route step 5). The 170
fit_clayton.py (rotation fit w=a*z+b) is WRONG - it maps the river N-NW of the town (page-down
-> 29.6 NNE): the correct transform is the MIRROR fit w=a*conj(z)+b (page-up -> 354.1 ~N,
page-right -> 264.1 ~W): the 1804 sheet is a near north-up bird's-eye view with a ~6 deg tilt.

### THE VERDICT (computed this session, replaces the 170 "VERDICT route")
- MIRROR fit over the same two anchors (A = fort pin (746,1362) <-> Q5471739 (36.164167,
  -86.774444); B = capitol-hill knoll (1750,1040) <-> Nominatim way 249147622 centroid
  (36.1658290,-86.7842374)), ENU origin (36.163,-86.775): a-angle -174.1 deg, scale 0.8520
  m/px (scene 2048 px wide -> 1.74 km; consistent with the sheet). Checks: (a) confluence
  V (490,1680) projects to (36.161941,-86.771715) = 207 m from real confluence node
  303579826 (36.1606686,-86.7700322) [rotation fit: 521 m]; 7 m from the mapped Cumberland
  way. (b) Rich-Branch mouth (2222,1620) -> (36.161022,-86.788123) = the WEST riverfront
  (12th-15th Ave S area, on the Cumberland's north bank) - agrees with the 165 independent
  Haydon-1860 cross-check (the only stream on the south riverfront, west of the core; the
  170 "east of the town" read was the rotation-fit artefact). (c) River flows left->right
  on the page = WESTWARD under the mirror = the Cumberland's true flow; under the rotation
  fit it would place the river N of the town (impossible). (d) The fort is the old town's
  SE corner (page lower-left = SE), consistent with the fort standing on the bluff by the
  corner. So: the mirror fit is correct; do NOT use w=a*z+b for this sheet. (Caveat for the
  lead doc: the drawn street families do not match the modern ones under either fit -
  segment-level OSM: modern "N-S" streets run ~240/60 and E-W streets exactly 90/270, the
  old grid is non-orthogonal; mirror fit: map-horizontal -> 84.1/264.1 matches Division
  within 6 deg, map-vertical -> 354.1/174.1 is ~67 deg off modern Broadway - perspective
  convergence and/or the 1796 plat's own orientation; not a fit blocker, the anchors are
  the evidence.)
- Extents under the MIRROR fit (scene box per the 170 definition, unchanged): 1804 SCENE
  (x 448-2496, y 678-1600) -> lat 36.16096..36.16963, lon -86.79163..-86.77140, 1.82 x 0.96
  km, center (36.16529, -86.78152); P625 2 km box margins: W -543 / E +726 / S +860 / N
  +178 m (W overshoot -> P625 REJECTED as the site point). Candidate point = the projected
  extent centre, 5 decimals: (36.16529, -86.78152) (721 m from P625 -> no --verify >50 km
  flag); its 2 km box covers the whole scene with margins W +92 / E +91 / S +519 / N +519
  m. Dense core (718-1790, 986-1575) -> 0.96 x 0.59 km, fits P625's box too. Full ink
  (45-2496, 525-1900) -> 2.20 x 1.38 km (the REFERENCES index + title block; the scene box
  is the verdict's extent, as in 170). The other three sheets (Haydon 1860, LOC 1860s,
  1895 ring) still span beyond the box -> review items, their extents go on the site note
  (estimate from z_loc_whole.png / z_def_whole.png when writing the note).
- VERDICT: nashville-q23197 point = (36.16529, -86.78152), NOT a P625 (the 147/148 SF
  precedent: the center of the drawn extent, 5 decimals). The 170 prior "P625's box covers
  the 1804 extent with ~1 km margin -> point = P625" is DEAD (it was built on the rotation
  fit).

### APPLY (exact next step, the 146/148 pattern)
1. fit/src_us_cities.py: SITES += "Q23197": dict(id="nashville-q23197", name="Nashville",
   named="Nashville", lon=-86.78152, lat=36.16529, place="Davidson County, Tennessee",
   region="United States", kind="town", wikipedia="https://en.wikipedia.org/wiki/
   Nashville,_Tennessee", note=...) - the note: aerial ground; the 1804 Clayton is a near
   north-up bird's-eye view (mirror fit, ~6 deg tilt, 0.852 m/px); the point is the center
   of the projected 1804 extent (P625 721 m NE, its box overshoots W 543 m); the other 3
   sheets oversize -> likely review items (NY-1811/DC-ring precedent); Fort Negley Q5471744
   record (no fort-only plan on Commons; the 3 Fletcher 1864 views are 236b leads; a
   fort-only plan later -> a Q5471744 fort site with the 1600 m fort box). SOURCES += 4
   rows: Clayton 1804 swap dict(date="1804"); Haydon 1860 no swap; LOC 2003630459 no swap
   (page "1860s" is the drawing date); Defenses 1895 swap dict(date="1895") (the "..." in
   its title is literal). Exact title strings: docs/lead_us_cities.md candidate list
   (read it first; the LOC re-download title is "File:Map of Nashville, Tennessee. LOC
   2003630459.jpg" and the 1895 one is "File:Defenses of Chattanooga, Tenn. Battery Erwin
   ... (IA dr defenses-of-chattanooga-tenn-...-01104241).jpg" - both in /tmp/nash168 as
   loc2003630459.jpg / defnash1895.jpg; the LOC jpg needs Image.MAX_IMAGE_PIXELS=None, 222
   MP). Module docstring: update the "Nashville follows in a later session" line.
2. Live (under .venv/bin/python, Nominatim/OSM gotchas as in the 170 standing block below):
   --verify (now 4 SITES keys Q60/Q61/Q62/Q23197; record the Q23197 facts + the 721 m P625
   no-flag into the lead doc; also re-record Q5471739/Q5471744 facts there - they are NOT
   SITES keys, no --verify for them). stage (expect "1 new sites, 4 new pictures; build
   (236c): nashville-q23197"); offline --check (expect 15 file rows, 15 pass); --golden.
3. tests/test_src_us_cities.py: staged row asserts 11->15, PASS-list += 4 titles, qid
   table += Q23197 (lon -86.78152, lat 36.16529, named "Nashville"), extras ids +=, years
   dict += 1804/1860/1860/1895, named_by_qid += {"Q23197": "Nashville"}. Run ONLY
   tests/test_src_us_cities.py + tests/test_region.py (offline; 7/7 + the 4 new passes).
4. docs/lead_us_cities.md Nashville section: the verdict (point + why, the mirror fit,
   the rotation-fit dead end, margins); per-candidate STAGED/DROP (the 151 DROP list below);
   Fort Negley record; the --verify transcript (15-row check, 15 pass); the Haydon
   composite finding (the 168 block below); the other sheets' extent estimates (from
   z_loc_whole.png 2500x1443 and z_def_whole.png 2x - examine them first; if the 1895
   page scan is unreadable fetch the David Rumsey zoomable original the desc links).
5. Tick acceptance box 3, Status: done (all 5 boxes).

### The Haydon 1860 sheet is a decorative composite (168 finding, unchanged)
The labelled "C U M B E R L A N D R I V E R" band runs across the sheet's MIDDLE
(full-sheet y~3900-4300 for x~3160-6300), the dense downtown core sits NORTH of it
(x~3250-5750, y~2700-4250) - geographically correct. BUT the blue TENNESSEE arm enters
from the sheet's upper-LEFT and the combined river exits lower-LEFT: the map's V at
(3288,4302) is a right angle while the real confluence is nearly a straight line - the
rivers are bent for composition. The compass rose (~(7185,1425)) is a decorative 8-point
star, no letter labels. Title block: "CITY OF NASHVILLE AND EDGEFIELD, DAVIDSON COUNTY,
TENNESSEE. Published by Hayden and Booth. 1860. SCALE 400 FEET TO 1 INCH." Tacked-together
plates at different rotations (core plate = modern CBD; OVERTOWN/EDGEFIELD diagonal grid
bottom-left; another diagonal grid bottom-right; FILLMORE/BARROW grid south of the river;
"Shelby" floodplain; red 1860 Corporation Line; REFERENCES legend (4885-5125,3775-4075);
CHURCHES list). Capitol pin RE-CONFIRMED (4880,3193) (165 stands; the 169 re-pin attempt
(4288,2982) was a scale miscalc: wide crop (2500,2500)-(6500,5200)@1.5x displayed 2000
wide -> full-sheet = 2500 + display*2). Consequence: Haydon CANNOT carry a whole-sheet
gereof; usable only qualitatively (core plate = modern CBD) and for the site note's
extent estimate from labelled landmarks (Franklin Turnpike, the Wesleyan College green =
the later Vanderbilt hill, "Residence of J.B. Hayes near Nashville", Howard School, T&A RR
line, the red Corporation Line). The 1833 waterworks reservoir is DEAD as an anchor (168).

### Clayton 1804 pins (170 re-read, unchanged; the mirror fit uses them)
Sheet 2557x1913, "NASHVILLE IN 1804. From Notes of one then resident, (Mrs Temple, Daughter
of Genl Robertson)." REFERENCES index 1-20 tops the sheet. Labeled streets: Broad /
Church / Cedar (vertical), Summer / College (2 labels) / Market (horizontal); modern Broad
= Broadway. Pins (full-sheet): fort hatched block (727-765,1345-1380) centre (746,1362);
"White Hall / former Fort" (982-1025,1545-1577); "now. Capitol Hill" annotation (1400-1650,
1020-1055) -> big wooded knoll (1685-1825,990-1110) centre (1750,1040); "W. Tate...Best
House in town" (1088-1472,1005-1110); "T. Napier" (1510-1543,837-860); KNOB (1453-1557,
953-977); "Dr. Henning's House & Office" (1498-1792,1344-1421); "Nashville Inn" (1485-1702,
1472-1523); cemetery (2118,988); McNairy's spring (2112-2342,870-896); "Sulphur Spring /
Salt made of it" (2150-2432,1158-1197) [projects to (36.164345,-86.789199) under the
mirror fit - not independently verified; Nominatim/web searches for "Sulphur Spring,
Nashville" and "Rich Branch, Nashville" return nothing useful]; "Judge McNairy's since
enlarged" (2099-2496,678-736); Rich Branch runs from the springs to its mouth (2222,1620)
(label (2165-2210,1350-1505)). The bottom hatched band = the Cumberland flowing left->right,
exit lower-right ~(2496,1766); two arms merge at the V (490,1680) (bent ~40-60 deg for
composition - decorative rivers, same class as Haydon; do not trust the drawn V/mouth,
do trust the town). Scene extent x 448-2496, y 678-1600 (ferry left through the fort, the
core, to Judge McNairy's property, down to the river band); dense core (718-1790,
986-1575). Full-ink 45-2496, 525-1900 (index + title included).

### The other two staged sheets (for the site note, when applying)
- LOC 2003630459 "Map of Nashville, Tennessee" (19690x11294, page date "1860s", pen-and-
  ink and pencil, fold-line relief, streets/railroads/all buildings/streams): a big 1860s
  building-by-building city map. NOT YET EXAMINED at any zoom - z_loc_whole.png (2500x1443)
  is in /tmp/nash168; estimate its geographic extent for the note. Expect city + a few km
  of country -> oversize vs the 2 km box -> review item.
- The 1895 Defenses sheet (1536x886 IA book page, "Nine b&w plans, some with sections. LC
  Civil War map", zoomable original at davidrumsey.com): ONE small "Defenses of Nashville,
  Tenn. Capitol" plan among nine. z_def_whole.png 2x is in /tmp/nash168 - identify the
  Nashville panel and the ring's span (Fort Negley (36.145,-86.7747) ~1.9 km S of P625 plus
  the ring's other forts) for the note; too small to georef. If unreadable, fetch the
  David Rumsey zoomable original (desc links it) before giving up.

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
restore `git checkout main -- docs/site_flow/307d_*.png` (PITFALLS filed 168). /map?bbox
data (nash164/168 dumps): the downstream Cumberland WEST of ~-86.783 is NOT in OSM here
(cbx.xml/cbx2/cbx3 have no river way; cbx4 has the Bing water=river face 36.166..-86.783
and way 40806685 = E arm + N arm only) - river-distance checks west of the confluence are
unreliable (corroborates 155). QID facts: Q23197 (label "Nashville", P625 (-86.774444,
36.162222), P373 ['Nashville, Tennessee'], P131 Davidson County Q1177705, enwiki
"Nashville, Tennessee", first name-search hit = itself, NOT in the catalog); Q5471739
Fort Nashborough (36.164167,-86.774444) precision 0.001; Q5471744 Fort Negley
(-86.774658,36.145097); no Fort Negley fort site is staged (no fort-only plan on Commons -
the 3 Fletcher 1864 views are 236b leads; a fort-only Negley plan later -> Q5471744 with
the 1600 m fort box). DROP list for the lead doc (151 DECISIONS entry): the Burns 1906
copy of the 1804 plan; the 1854 book detail; the 1888 Sanborn fragment; the 1916 LOC
75695990 .tif (outside the window); the two 1887 battle-map files; the 1895 battlefield
map (look once via its Commons page before dropping); all Fort Negley photos.
