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

(2026-10-14, iteration 174, agent a). Test-file session (173 hand-over steps 1-2): tests/
test_src_us_cities.py is now at the 15-row shape (the details in the 174 DECISIONS entry);
7/7 green (test_src_us_cities + test_region). Module / staged files / golden are already
committed (9cae53f). Remaining work: rewrite the lead doc (step 3), tick box 3, the done
commit (steps 4-5). No live work needed before then except optionally the /tmp/nash168
examinations below.

### NEXT STEPS (in order)
1. Rewrite docs/lead_us_cities.md (read it in full first; its tail section "## Nashville
   (Q23197) - later sessions" is what gets replaced):
   (a) header: add the four Nashville plans to the plan list; "three cities staged;
       Nashville last" -> all four owner-named cities staged.
   (b) QID section: add Q23197 to the verified list with the 173 --verify transcript
       (below), and re-record the Q5471739 / Q5471744 facts (below - they are NOT SITES
       keys, so no --verify runs for them).
   (c) the full Nashville city section: the site point + mirror-fit verdict (below); the
       four candidate subsections (STAGED: the row facts below; DROP: the 151 archive
       entry - grep "iteration 151" in DECISIONS-archive.md; 236b leads = the 3 Fletcher
       1864 Fort Negley views); the Haydon composite finding (below); extent estimates
       for the LOC 2003630459 and the 1895 sheet (EXAMINE /tmp/nash168/z_loc_whole.png
       2500x1443 and z_def_whole.png 2x first - still on disk at this limit, source jpgs
       loc2003630459.jpg / defnash1895.jpg alongside; if gone, re-download via the
       Commons file pages / Special:FilePath, and for the 1895 sheet the David Rumsey
       zoomable original its desc links, per the 151 entry); the offline check transcript
       (below - or re-run .venv/bin/python fit/src_us_cities.py --check).
2. Tick acceptance box 3, set Status: done.
3. Commit: git add -A && git commit -m "236a: done - Nashville staged (4 plans, 15/15 check) + tests + lead doc".

### Verified (173, do NOT redo)
- --verify (checked 2026-10-14, 4 QIDs): CLEAN, no flags, no traps. Q23197: label
  'Nashville'; P625 [(-86.77444444444444, 36.16222222222222)] vs table (-86.78152, 36.16529)
  = 721 m NE, no flag; P373 ['Nashville, Tennessee']; P131 [('Davidson County',
  'Q1177705')]; enwiki 'Nashville, Tennessee'; search 'Nashville' first P625 hit = Q23197
  itself. Q5471739 Fort Nashborough (36.164167, -86.774444, precision 0.001, P131 Q1509,
  OSM way 130910783 same spot) and Q5471744 Fort Negley (-86.774658, 36.145097, P131
  Q23197, P373 = photos + the 3 Fletcher views only) are NOT SITES keys.
- stage: "staged: 1 new sites, 4 new pictures; build (236c): nashville-q23197". Row facts:
  Clayton 1804: year 1804, date "1804", date_commons "1880" (swap fired); Haydon 1860:
  year 1860, date "1860", NO date_commons; LOC 2003630459: year 1860 (from "1860s",
  precision 8), date = the raw page string "1860s date QS:P,+1860-00-00T00:00:00Z/8", NO
  date_commons (no swap: "1860s" IS the LOC-verified drawing date "[186-]"); Defenses
  1895: year 1895, date "1895", date_commons "" (swap fired, empty page value; the golden
  normalizes it to 0000-00-00). All four classified p_plan 1.0 by hand.
- --check (offline): rc=0, no join problems, 15 PASS lines (the four new ones = the four
  titles in the test's PASS list), "evidence: 15 rows, 15 pass, 0 fail, 0 no-tie".
  --golden regenerated.
- THE 1804 Clayton mirror-fit VERDICT (baked into the module's Q23197 entry): mirror
  similarity w = a*conj(z)+b over anchor A = fort pin (746,1362) <-> Q5471739 (36.164167,
  -86.774444) and B = capitol-hill knoll (1750,1040) <-> Nominatim way 249147622 centroid
  (36.1658290,-86.7842374), ENU origin (36.163,-86.775): a-angle -174.1 deg, scale 0.8520
  m/px; page-up -> 354.1 (~N), page-right -> 264.1 (~W) = near north-up bird's-eye view,
  ~6 deg tilt. Checks: confluence V (490,1680) projects 207 m from the real OSM node
  303579826 (36.1606686,-86.7700322) [rotation fit: 521 m] and 7 m from the mapped
  Cumberland way; Rich-Branch mouth (2222,1620) -> (36.161022,-86.788123) = the WEST
  riverfront (12th-15th Ave S) - agrees with the 165 independent Haydon cross-check; the
  river flows left->right on the page = WESTWARD = the Cumberland's true flow (the 170
  rotation fit w=a*z+b is DEAD - it placed the river N of the town); the fort is the town's
  SE corner. Extents (scene box x 448-2496, y 678-1600): lat 36.16096..36.16963, lon
  -86.79163..-86.77140 = 1.82 x 0.96 km, center (36.16529,-86.78152); P625 2 km box margins
  on it: W -543 (overshoot -> P625 REJECTED) / E +726 / S +860 / N +178 m; the candidate
  point's 2 km box covers the scene with margins W +92 / E +91 / S +519 / N +519 m. Dense
  core (718-1790, 986-1575) = 0.96 x 0.59 km; full ink incl. REFERENCES index + title
  (45-2496, 525-1900) = 2.20 x 1.38 km. Caveat for the lead doc: the drawn street families
  do not match the modern ones under either fit (mirror: map-horizontal -> 84.1/264.1
  matches Division St within 6 deg; map-vertical -> 354.1/174.1 is ~67 deg off modern
  Broadway - perspective convergence and/or the 1796 plat's own orientation; not a fit
  blocker, the anchors are the evidence). The 1804 bottom river band is bent 40-60 deg for
  composition (decorative rivers - trust the town, not the drawn V/mouth).
- Haydon 1860 (10000x6082) is a DECORATIVE COMPOSITE: the labelled CUMBERLAND band runs
  across the sheet's middle (y~3900-4300 for x~3160-6300), the dense downtown core sits
  NORTH of it (x~3250-5750, y~2700-4250) - geographically correct - but the blue TENNESSEE
  arm enters upper-LEFT and the combined river exits lower-LEFT (the map's V at
  (3288,4302) is a right angle while the real confluence is nearly a straight line - the
  rivers are bent for composition); the compass rose (~(7185,1425)) is a decorative 8-point
  star; plates tacked together at different rotations (core plate = modern CBD; OVERTOWN/
  EDGEFIELD diagonal grids; FILLMORE/BARROW grid south of the river; "Shelby" floodplain;
  red 1860 Corporation Line; REFERENCES legend; CHURCHES list). Title block: "CITY OF
  NASHVILLE AND EDGEFIELD, DAVIDSON COUNTY, TENNESSEE. Published by Hayden and Booth. 1860.
  SCALE 400 FEET TO 1 INCH." Consequence: Haydon CANNOT carry a whole-sheet georef; usable
  only qualitatively (core plate = modern CBD) and for the site-note extent estimate from
  labelled landmarks (Franklin Turnpike, the Wesleyan College green, Howard School, the T&A
  RR line, the red Corporation Line). The 1833 waterworks reservoir is dead as an anchor.
  Pins (full sheet): confluence V (3288,4302); capitol (4880,3193); Rich-Branch mouth
  (3836,3981).
- Clayton 1804 sheet (2557x1913), "NASHVILLE IN 1804. From Notes of one then resident, (Mrs
  Temple, Daughter of Genl Robertson.)": REFERENCES index 1-20 tops the sheet. Labeled
  streets: Broad / Church / Cedar (vertical), Summer / College / Market (horizontal); modern
  Broad = Broadway. Pins (full-sheet): fort hatched block centre (746,1362); "White Hall /
  former Fort" (982-1025,1545-1577); "now. Capitol Hill" -> big wooded knoll centre
  (1750,1040); "W. Tate...Best House in town" (1088-1472,1005-1110); "T. Napier"
  (1510-1543,837-860); KNOB (1453-1557,953-977); "Dr. Henning's House & Office"
  (1498-1792,1344-1421); "Nashville Inn" (1485-1702,1472-1523); cemetery (2118,988);
  McNairy's spring (2112-2342,870-896); "Sulphur Spring / Salt made of it"
  (2150-2432,1158-1197) [projects to (36.164345,-86.789199) under the mirror fit - not
  independently verified]; "Judge McNairy's since enlarged" (2099-2496,678-736); Rich
  Branch runs from the springs to its mouth (2222,1620) (label (2165-2210,1350-1505)). The
  bottom hatched band = the Cumberland flowing left->right, exit lower-right ~(2496,1766);
  two arms merge at the V (490,1680) (bent for composition). Scene extent x 448-2496,
  y 678-1600; dense core (718-1790, 986-1575); full ink 45-2496, 525-1900.
- The other two staged sheets (extent estimates for the site note): LOC 2003630459
  (19690x11294, O.M. Poe, Chief Engineer's Office Mil. Div'n of the Mississippi, pen-and-
  ink and pencil on cloth, fold-line relief, every building, north toward the lower right)
  = a big 1860s building-by-building city map, never examined at any zoom -> expect city +
  a few km of country = oversize vs the 2 km box = review item. The 1895 Defenses sheet
  (1536x886 IA book page, atlas plate): nine panels - 1 Chattanooga Battery Erwin, 2
  Battery Coolidge, 3 Nashville Magazine Battery (Dec 1864), 4 Nashville Capitol (Nov 30
  1864), 5 Fort McCook (Dec 21 1864), 6 Fort Morton (Dec 1864), 7 Fort Hill (Dec 1 1864, +
  small "Plan of Nashville, Tenn."), 8 Fort Nashville, 9 the Nashville Heights (Dec 1864);
  header "ATLAS TO ACCOMPANY THE OFFICIAL HISTORIES OF THE UNION AND CONFEDERATE ARMIES
  1861-1865"; first edition 1884-85 per the plate header (unverified online); the scanned
  1895 Julius Bien edition = the row's date; too small to georef (Fort Negley
  (36.145,-86.7747) ~1.9 km S of P625 plus the ring's forts go on the site note).
- DROP list for the lead doc (151 archive entry): the Burns 1906 copy of the 1804 plan
  (same plan, one row per plan); the 1854 Putnam "Detail" (cropped, too small); the 1888
  Sanborn fragment (491x572); the 1916 Marshall & Bruce (outside window, commercial); the
  1887 Cowen battle map (1:110,000, battle not city); the 1895 Bien Nashville-and-Franklin
  battlefield map (look once via its Commons page before dropping); all Fort Negley photos
  (Barnard 1864 lowercase-n undated/no PLANWORD; LCCN2007662878; Webster & Albee ca. 1890;
  2019 CC-BY ruins; modern park shots). 236b leads (record, do not stage): the three
  Fletcher 1864 Fort Negley views (LCCN2003655690/2003655670/2003655689).
- Fort Negley: NO fort-only plan on Commons -> no Q5471744 fort site staged (a staged site
  without a picture fails check_staged()); if a fort-only plan appears later: kind "fort",
  1600 m box, 3DEP LiDAR candidate (the 203a mounds precedent). Recorded on the Q23197 site
  note.

### Standing gotchas (unchanged, still true)
Tests OFFLINE only (socket-blocked fixture); run ONLY tests/test_src_us_cities.py +
tests/test_region.py (7/7 at this limit); live commands under .venv/bin/python (module top
stays stdlib-only, commons->aw needs numpy); named-place gate = title + 600-char-truncated
desc (all 4 Nashville titles print "Nashville" in the title - gate-safe); stage()
idempotent on (site,title), missing title fails loud; town box = 2 km x 2 km centred on the
point (no box_m override; specs/site_boxes.json not in Touches); do NOT write the
canonical files (236c; the REGION_NAME line in pipeline/build_catalog.py is already
committed); do not "fix" pipeline/commons.py's NO regex (not in Touches); Nominatim 1 r/s
project UA (pipeline/aw.py UA), live OSM browser UA (/map?bbox and /api/0.6/* alive per
164/168 - retest per call; /map?bbox arg order minlon,minlat,maxlon,maxlat; the response
root holds BOTH node and way elements); Overpass dead (PITFALLS filed 168); after ANY
full-suite run restore `git checkout main -- docs/site_flow/307d_*.png` (PITFALLS filed
168) - the two task tests never touch site_flow; PIL lives in .venv (Image.MAX_IMAGE_
PIXELS=None for the 222 MP LOC map); /tmp/nash168 is session-scoped (still on disk at this
limit: cbx*.xml OSM dumps, clayton1804.jpg, loc2003630459.jpg, defnash1895.jpg,
z_clayton_whole.png / z_loc_whole.png / z_def_whole.png / z_whole.png crops,
fit_clayton.py; re-download route: the Commons file pages / Special:FilePath, and for the
1895 sheet the David Rumsey zoomable original its desc links). QID facts: Q23197 (label
"Nashville", P625 (-86.774444,36.162222), P373 ['Nashville, Tennessee'], P131 Davidson
County Q1177705, enwiki "Nashville, Tennessee", first name-search hit = itself, NOT in the
catalog); Q5471739 (36.164167,-86.774444) precision 0.001; Q5471744 (-86.774658,36.145097).

### THE VERDICT (172/173, replaces the 170 "VERDICT route")
nashville-q23197 point = (36.16529, -86.78152), NOT a P625 (the 147/148 SF precedent: the
center of the drawn extent, 5 decimals; P625 721 m NE, no >50 km flag). The 170 prior
"P625's box covers the 1804 extent with ~1 km margin -> point = P625" is DEAD (it was
built on the rotation fit). Do NOT use w=a*z+b for this sheet.
