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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/212-cover-final.md` (in-progress) - hand-over: (2026-10-13, iteration 255, agent a, written at the context limit -
- `tasks/236a-us-city-plans.md` (in-progress) - hand-over: (2026-10-14, iteration 172, agent a, written at the context limit. RESEARCH session: NO repo file touched, staged files still 3/11/11. THE SITE-POINT VERDICT IS SETTLED: the 170 rotation fit is dead (it maps the river N of the town); the correct transform is the MIRROR similarity w=a*conj(z)+b over the same two anchors (fort (746,1362)<->Q5471739, capitol hill (1750,1040)<->(36.1658290,-86.7842374)): 0.8520 m/px, page-up->354.1, page-right->264.1 = near north-up bird's-eye view, ~6 deg tilt; confluence V 207 m from the real node; mouth on the WEST riverfront per the 165 Haydon cross-check. VERDICT per 155/161: the projected 1804 scene (1.82 x 0.96 km, lat 36.16096..36.16963, lon -86.79163..-86.77140) does NOT fit the P625 2 km box (W overshoot 543 m) -> nashville-q23197 point = (36.16529, -86.78152) (5 decimals, 147/148 SF precedent; 721 m from P625, no flag; its box covers the scene, margins 92-519 m). NEXT SESSION: APPLY (146/148 pattern) per the hand-over's APPLY block: SITES+SOURCES in fit/src_us_cities.py (Q23197 + 4 rows: Clayton swap 1804, Haydon no swap, LOC 2003630459 no swap, Defenses swap 1895; exact titles in docs/lead_us_cities.md), live --verify, stage (expect 1 new sites, 4 new pictures; build (236c): nashville-q23197), offline --check (15/15), --golden, tests (11->15 rows etc.), lead doc Nashville section, box 3 tick, done.
- `tasks/236-us-cities.md` (split)
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-13, iteration 208, agent c - the driver returned the parent: all existing subtasks
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307bc-reverify-place-mode.md` (open) - hand-over: (2026-10-13, iteration 256, agent a - first session: the task was filed as the driver
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-13, iteration 256, agent a - context limit hit at the end of this session; the
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,
- `tasks/807-horsley-list-correction.md` (blocked)
- `tasks/808-horsley-stage.md` (blocked)
- `tasks/809-horsley-check.md` (blocked)

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/235-placement-test-dep-pick.md`
- `tasks/236b-us-birdseye.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-14 236a DECISION: iteration 164 - site-point research (live, no repo edits): the confluence point IS found = OSM node 303579826 (36.1606686,-86.7700322), the V-join of the Kentucky (N chain) + Cumberland (E chain) inside the single mis-named way 40806685 (163's "mouth nodes" were the Mississippi terminus at Blytheville, not Nashville; the Tennessee relation 2182503 skips the Nashville stretch entirely); /map?bbox is ALIVE again (400-node-limit, not 410); Tennessee State Capitol = Nominatim way 249147622 centroid (36.1658290,-86.7842374) = anchor A; Haydon map FRESH re-survey: the sheet is NORTH-UP (blue band = Kentucky from the N-NW, hatched from the right = Cumberland from the E, hatched stub S-SW = downstream Tennessee); the confluence V is at full-sheet ~(2950-3100,4500-4700) (163's (2950,5240) too far south); capitol block ~(4890-4910,3110-3180) (163's (5000,3250) off ~100 px); the 163 "fort corner" (3980,3850) is the 1860 riverfront, NOT the fort (the fort is demolished - must pin the 1796 plat's NE corner instead); the 163 Rich-Branch-mouth pixel (6200,4050) is WRONG (that area = plain riverfront, no stream) - re-search the riverfront x 4500-6000
- Research-only session (the 145/147/151/152/163 pattern); no repo file touched. Baseline tests re-run 7/7 green (tests/test_src_us_cities.py + tests/test_region.py) before the research. Both maps re-downloaded to /tmp/nash164/ (session-scoped; URLs in the 161 hand-over section).
- **The 163 "mouth nodes" were the terminus, not the headwaters.** Tennessee relation 2182503's first two members (role="mouth" nodes 1752049047 = 37.0833199,-88.5779023 and 4636304129 = 37.0918233,-88.5895801) sit at the Mississippi River confluence near Blytheville, Arkansas - the river's downstream END. The relation has no source node; its member order is source->mouth and the first main_stream way (77442872) starts at the Smokies headwater (35.9591561,-83.8505169). I scanned ALL 46 main_stream ways (/way/{id}/full, browser UA, 1 r/s): the course runs Knoxville (35.96,-83.93) -> (35.0,-85.62) -> way 164024430 jumps straight to (34.37,-86.39) at the Alabama border -> Florence (34.8,-87.4) -> one 336-node way (164267067) (35.06..37.01, -88.32..-87.92) -> mouth. The Nashville loop is absent: NO way of this relation passes through (36.16,-86.77) (within ~5 km of the city). (OSM's river course around the Cumberland Plateau is mapped as a shortcut, or the Nashville stretch belongs elsewhere - either way this relation is useless for Nashville geometry.) Confluence nodes found in the scan: (35.760,-84.188), (35.730,-84.316), (35.624,-84.781), (37.057,-88.547) - none near Nashville.
- **Cumberland relation 2182468 (Q1143718) = the UPPER Cumberland, not the Nashville stretch.** Tags: destination=Ohio River; 31 main_stream ways from (36.8453363,-83.3251415) to (36.2880413,-85.9402030) (eastern/central Kentucky); its mouth node 303572366 = (37.1421398,-88.4098655). 163's Nominatim "Cumberland = relation 2182468" (from a viewbox search) was a mis-hit. The Nashville stretch of the Cumberland = way 316706277 (a 16-node stub around (36.177,-86.904); Nominatim bounded search returns it with centroid 36.1712410,-86.8998905 = the western check point) and way 40806685 (below).
... (6.2 KB more: `grep -n -A 200 -F '## 2026-10-14 236a DECISION: iteration 164 - site-point research (live, no repo edits): the confluence point IS found = OSM node 303579826 (36.1606686,-86.7700322), the V-join of the Kentucky (N chain) + Cumberland (E chain) inside the single mis-named way 40806685 (163's "mouth nodes" were the Mississippi terminus at Blytheville, not Nashville; the Tennessee relation 2182503 skips the Nashville stretch entirely); /map?bbox is ALIVE again (400-node-limit, not 410); Tennessee State Capitol = Nominatim way 249147622 centroid (36.1658290,-86.7842374) = anchor A; Haydon map FRESH re-survey: the sheet is NORTH-UP (blue band = Kentucky from the N-NW, hatched from the right = Cumberland from the E, hatched stub S-SW = downstream Tennessee); the confluence V is at full-sheet ~(2950-3100,4500-4700) (163's (2950,5240) too far south); capitol block ~(4890-4910,3110-3180) (163's (5000,3250) off ~100 px); the 163 "fort corner" (3980,3850) is the 1860 riverfront, NOT the fort (the fort is demolished - must pin the 1796 plat's NE corner instead); the 163 Rich-Branch-mouth pixel (6200,4050) is WRONG (that area = plain riverfront, no stream) - re-search the riverfront x 4500-6000' DECISIONS.md`)

### 2026-10-14 236a DECISION: iteration 165 - merged main (5 binary conflicts in the 307d golden PNGs, resolved to main's bytes - test-run re-encodings of the same finished owner-check views; all 10 restored to main's bytes per 6af207b; full suite after the merge 168/1/0 - agent c's test_fit_queue failure is fixed on main); site-point research: Haydon 1860 close-up re-pins - confluence V (3288,4302), capitol (4880,3193), Rich-Branch mouth FOUND (3836,3981) = the only stream on the south riverfront; scale flag (~0.71 m/px from the two anchors vs the nominal ~0.43-0.55); next session: 3-anchor least-squares georef -> mouth -> Clayton 2-anchor projection -> verdict -> apply (hand-over step 8)
- **The merge:** `git merge main` (the driver's request) conflicted in exactly 5 BINARY files, docs/site_flow/307d_{A_1-card,A_4-saved,A_5-reload,B_1-card,B_5-reload}.png (all three versions - merge-base 6af207b, HEAD, main - differ in each). History check: every one of the ten 307d PNGs' changes since the common port c72706b are driver "[driver] uncommitted work" commits on both sides (my 4c8799d; main's f516b1e/cb06a3a) - i.e. test-run re-encodings, not content. tests/test_owner_check.py::_run_one copies the freshly rendered owner-check views into docs/site_flow/307d_* on EVERY run and never compares against the committed bytes (agent c's 302f iter-127 entry documents the same dirt from her branch). Neither side's bytes are unique, so resolved to MAIN's side (`git checkout --theirs` on the 5, per "main holds the other agents' finished work") and, per the 6af207b precedent (the branch must stay byte-identical to main on these for a conflict-free merge into main), ALL 10 were restored to main's bytes after the post-merge suite run re-encoded 4 of them on this machine (A_4/A_5 = new encodings, B_1/B_5 = my branch's earlier encoding; the other 6 match main). Merge commit b14918f.
- **Full suite after the merge: 168 passed / 1 skipped / 0 failed (543.28 s)** - strictly better than the driver's 2026-10-13 loop-start note (1 failed test_fit_queue placement_gestures / 159 passed): agent c's fix for it landed on main (302f's 127-conclusion entry records her own 168/1/0 too). The suite grew 159->168 (agent c's tests/test_matchfit_station.py + its two fixtures landed). My task's standing "run only src_us_cities + region" habit still stands, but the known-failure list is now empty.
- **Haydon 1860 close-up re-pins (the 164 next step):** the sheet is 10000x6082, north up (re-downloaded to /tmp/nash165/haydon.jpg, gone). (a) CONFLUENCE V: the blue Tennessee band (from the south) meets the hatched "CUM" Cumberland (from the east) at the vertex **(3288, 4302)** full-sheet (z-crop (3000,4050)-(3500,4550) @2x: display (575,505)/2). 164's rough (2950-3100, 4500-4700) was ~200 px off, 163's (2950,5240) further. (b) CAPITOL: the dark building footprint ("STATE CAPITOL" label, park block around) centres at **(4880, 3193)** (z-crop (4680,2980)-(5080,3380) @2x: display (400,425)/2); close to 164's (4890-4910, 3110-3180). (c) THE MOUTH: the 164 "re-search the riverfront x 4500-6000" is empty (plain "SHELBYS"-flats riverfront, no streams; the second blue "inlet" near Water St/Wharf ~(4530,3900) is the river's own bank line) - but west of that, at **(3836, 3981)**, a thin meandering double-line creek comes down from the town side (past the "Foun d ry" foundry, between the numbered lots 14/15) and enters the hatched Cumberland (z-crop (3700,3700)-(4100,4100) @2x: mouth display (272,462)/2; no label visible on the creek at 2x). It is the ONLY stream on the south riverfront between the confluence (x~3300) and x~6400, and it sits just south of the old town core (the fort maps by rough linear estimate to ~(3780,3550)), i.e. the same stream Clayton 1804 draws entering the river band east of the town = the 1804 Rich Branch. Rough geographic position (linear mix of the two anchors) ~ (36.162, -86.775), just S of P625.
... (1.6 KB more: `grep -n -A 200 -F '## 2026-10-14 236a DECISION: iteration 165 - merged main (5 binary conflicts in the 307d golden PNGs, resolved to main's bytes - test-run re-encodings of the same finished owner-check views; all 10 restored to main's bytes per 6af207b; full suite after the merge 168/1/0 - agent c's test_fit_queue failure is fixed on main); site-point research: Haydon 1860 close-up re-pins - confluence V (3288,4302), capitol (4880,3193), Rich-Branch mouth FOUND (3836,3981) = the only stream on the south riverfront; scale flag (~0.71 m/px from the two anchors vs the nominal ~0.43-0.55); next session: 3-anchor least-squares georef -> mouth -> Clayton 2-anchor projection -> verdict -> apply (hand-over step 8)' DECISIONS.md`)

### 2026-10-13 236a DECISION: iteration 155 - merged main (conflict in web/data/review.json only, resolved to main's side: its port bba5961 is the newer complete export - fort-ancient left the open queue because the port added its resolving platefits doc, numancia gained the owner's "Not this" candidate; my side was the same 457 items with a stale at-timestamp, 0 unique; 456 recomputed open = export, 0 plans lost; 12/12 tests). Site-point research: Fort Nashborough = Q5471739, P625 (36.164167, -86.774444) = the Clayton 1804 "former Fort" at the town's SW corner, 217 m NORTH of the city P625; the Clayton drawing's bottom band is the rivers' corner (Rich Branch enters east of the town) so P625 likely falls inside the 1804 extent - but the verdict waits on a 2-anchor georef + the Haydon 1860 cross-check (context limit after reading the Clayton; both re-download URLs in the hand-over). OSM river data around the CBD is unreliable (do not trust for this), and Overpass is dead from this machine (406/XHTML) - use api.openstreetmap.org /map (<=0.02x0.02 deg) and /way/{id}/full
- **The merge (done, commit 3093e4e):** `git merge main` (the driver's request) conflicted in ONE file, web/data/review.json, on the "at" timestamp (HEAD 2026-10-13T20:37 vs main 2026-10-14T02:54). Analysis before resolving: (a) HEAD-vs-merge-base d286196: review.json identical in all 457 items, only "at" differs (a driver regeneration); (b) main-vs-merge-base: exactly one new commit, the owner port bba5961, which (i) ADDED data/db/platefits/fort-ancient-q5470727.ancientmonuments00squi_n0076_1.json (at 02:53) - fit/review.py's export() only lists OPEN items ("resolved not recorded AND no platefits doc for any candidate"), so the fort-ancient item correctly LEFT the open queue in main's export (457->456); (ii) deleted data/review/numancia.json and added data/review/numancia.c_0fa271e2444f7bfc.json + data/db/notthis/numancia.c_0fa271e2444f7bfc.json (at 02:52) - the owner used the ported fit tool's "Not this" action on numancia's candidate, so the item's no_picture_found cleared and the lead became c_0fa271e2444f7bfc. Both intents preserved: resolved to main's file byte-identical (git checkout --theirs); my side had no unique content. Read-only consistency re-computation after the merge: 480 item files -> 456 open (items with a resolving platefits doc or a recorded "resolved") = the 456 exported, none missing, none stale. Tests 12/12 green (tests/test_src_us_cities.py + tests/test_region.py + tests/test_serve.py; the known-failing test_fit_queue is agent c's 302/306 in-flight work, skipped per the standing caveat).
- **Site point - the fort is pinned (Q5471739):** Wikidata (via pipeline/catalog_wd, the robust cached path): Q5471739 "Fort Nashborough - former stockade in Nashville, Tennessee", ONE P625 (36.164167, -86.774444) precision 0.001, P131 Q1509. The enwiki "Fort Nashborough" infobox is the SAME 36.16417/-86.77444 and says a small replica stands "in Downtown Nashville along First Avenue North, several hundred meters from the original site". OSM way 130910783 (historic=fort, wikidata=Q5471739, source=Bing) is at (36.1642, -86.7754) - the same spot. Three independent sources agree: the fort = (36.164167, -86.774444) = the Clayton map's "D Cross's owner / Stone House / former Fort", 217 m NORTH of the city P625 (36.162222, -86.774444) at the same longitude. Consequence: 151's framing ("the 1790s town WEST of the Cumberland; P625 east of the river") was built on confused OSM river data (below) and does not hold; the Clayton drawing itself places the town NORTH of the rivers' corner with the fort at its SW corner, so P625 (just south of the fort) plausibly sits inside the 1804 drawn extent - to be confirmed by the georef, not assumed.
... (3.1 KB more: `grep -n -A 200 -F '## 2026-10-13 236a DECISION: iteration 155 - merged main (conflict in web/data/review.json only, resolved to main's side: its port bba5961 is the newer complete export - fort-ancient left the open queue because the port added its resolving platefits doc, numancia gained the owner's "Not this" candidate; my side was the same 457 items with a stale at-timestamp, 0 unique; 456 recomputed open = export, 0 plans lost; 12/12 tests). Site-point research: Fort Nashborough = Q5471739, P625 (36.164167, -86.774444) = the Clayton 1804 "former Fort" at the town's SW corner, 217 m NORTH of the city P625; the Clayton drawing's bottom band is the rivers' corner (Rich Branch enters east of the town) so P625 likely falls inside the 1804 extent - but the verdict waits on a 2-anchor georef + the Haydon 1860 cross-check (context limit after reading the Clayton; both re-download URLs in the hand-over). OSM river data around the CBD is unreliable (do not trust for this), and Overpass is dead from this machine (406/XHTML) - use api.openstreetmap.org /map (<=0.02x0.02 deg) and /way/{id}/full' DECISIONS.md`)

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)
- Re-verified the 160 hand-over's numbers with fresh measurements BEFORE deleting (AGENTS.md: check facts by running code). Confirmed: 8 pairs = 4 distinct points on a 100-px grid ladder (three on u=100; the 200-px and 100-px lat steps span 0.0053896/0.0017967 deg = 1.5:1 per pixel, no similarity can hit; the page's simFit (exact port) gives resid 10.9-39 m, 2.634 m/px, +1.06 deg - identical to the committed shot's [eval] line). CORRECTIONS to the 160 hand-over: the real hillfort is ~20 m NW of the site point (not '+22 E / -55 N'), its hachured ring is ~80-90 m across (not ~130 m), so the drawn ring (277-342 m at 2.634 m/px, centred at raw (240-248,115) -> (-3.5187, 51.0370) = E -218..-239, N +531) is ~3.5x too big and 554-582 m N-NW (N23-25W) of the real one - on a small hachured wood hill. The 160 '~2x / 535-576 m' survives as a range (540-576 -> 554-582), the direction and the verdict are unchanged. Extra independent check: the plate's own 'SCALE OF FEET 0-300' bar measures ~1.45 m/px vs the fit's 2.634 (1.8x). Distances must be geographic (dx=dlon*111194.9266*cos(lat0), dy=dlat*110900), NOT raw Mercator units (my first pass computed 916 m for the 576 m distance that way).
- Executed the 303 way exactly as 306c did (fit/review.py API, no hand-edited JSON): upsert_item(root,'bury-castle-q5001077',[entry]) with entry = {plan, title, url, pairs (the doc's 8), coarse:false, evidence (from the data/commons/files.jsonl row: rec evidence/1, kind category, checked 2026-10-10, site_cat/file_cat 'Bury Castle, Somerset'), label '1911', cite, ref, size, place_reason '306d audit 2026-10-12: ... Document deleted.'} appended to the existing item (lead n0136_1 kept first, filename unchanged), then deleted data/db/platefits/bury-castle-q5001077.c_de779031cda8a0dc.json, then export(root,'bury-castle-q5001077') (333 open of 346). Only 3 files changed (D doc, M item, M web/data/review.json) - no other site's item touched; the site was already covered for the union check (its item was already open in the page file before the upsert).
- Wrote the 306d block (header + the bury-castle line) into docs/site_flow.md after the 306c block (header is tense-neutral: 17 more lines to come in batches; box 1 ticked - 36 shots re-listed this session).
- TESTS (full suite, main checkout, --ignore=tests/test_gate.py, -p no:cacheprovider, with my changes): 10 failed, 130 passed, 1 skipped (251 s). The 10: test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (FAILED at the seed check, dep:null) + 9 that are agent a's in-flight work already on main (test_merge new_sites_are_complete/new_site_golden_samples = 211's open 222-228 gate; src_artists/limes/mackenzie/numancia/wiltshire_stukeley stage+check tests = the 224 family). Baseline in my task file (123/1, 2026-10-12) is STALE - main has since merged 211/223/224/307 work and the suite grew to 141 tests.
- A/B attempt 1 (worktree at HEAD in /tmp/aw306d_ab): INVALID - web/data/sites/ is mostly gitignored (58 tracked files vs 389 site dirs in the main checkout; the per-site web data + data/raw are local build artifacts), so a fresh worktree lacks stonehenge etc. and fails 3 tests deterministically (site_done_line FileNotFoundError '/tmp/aw306d_ab/web/data/sites/stonehenge-q39671', fit_provenance line_refuses_unmarked_non_auto_doc, fit_queue save_runs) that pass in the main checkout; its placement_gestures 'vacuous ERROR' there is also unprovable (no local depictions). PITFALLS candidate: never A/B this project in a bare worktree/checkout - do it in the main checkout with the changed files temporarily at HEAD. (The worktree is still registered; remove it: git worktree remove --force /tmp/aw306d_ab && git worktree prune.)
... (1.9 KB more: `grep -n -A 200 -F '## 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)' DECISIONS.md`)

### 2026-10-13 DRIVER: test suite failing at loop start (1 tests)
    tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    tests/test_fit_queue.py:1749: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    1 failed, 159 passed, 1 skipped in 424.53s (0:07:04)
    (full test output: .agent/reports/last-test-output.txt)
