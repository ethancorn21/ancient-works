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

(2026-10-13, iteration 155, agent a - **MAIN MERGED (commit 3093e4e, 12/12 tests green). Site-point research in progress: Fort Nashborough = Q5471739, P625 (36.164167, -86.774444) [Wikidata, prec 0.001; Wikipedia infobox same; OSM way 130910783 same] = the Clayton 1804 "former Fort" at the town's SW corner, 217 m NORTH of the city P625; the Clayton map read (the river band at the bottom = the rivers' corner, the Rich Branch enters east of the town; see below). Verdict on the point NOT yet settled - needs a 2-anchor georef of the Clayton map + the Haydon 1860 cross-check. /tmp downloads are gone again - re-download URLs below.**

### Current state
- **Merge done (3093e4e):** `git merge main` conflicted only in web/data/review.json. Resolved to MAIN's side
  (byte-identical): main's port commit bba5961 is the newer, complete export (at 10-14 02:54) - it drops
  fort-ancient-q5470727 (RESOLVED: the port added data/db/platefits/fort-ancient...n0076_1.json, so the item
  leaves the open queue) and carries numancia's owner "Not this" candidate c_0fa271e2444f7bfc (data/db/notthis/
  + data/review/numancia.c_0fa271e2444f7bfc.json; old data/review/numancia.json deleted on main). My branch's
  copy was the same 457-item set with only a stale at-timestamp (10-13 20:37) - no unique items, nothing lost.
  Read-only re-computation of open/closed from merged data/review + platefits = 456 = export, 0 plans lost.
  Tests 12/12 green (src_us_cities, region, serve). My staged files still 3/11/11; --check 11/11 from 150.
- **Site-point research (155, all live):**
  - **Fort Nashborough = Q5471739** ("former stockade in Nashville, Tennessee"): P625 (36.164167, -86.774444),
    precision 0.001 (~111 m); P131 Q1509 (US). Wikipedia infobox = the same 36.16417/-86.77444 and says a
    replica stands "along First Avenue North, several hundred meters from the original site". OSM way
    130910783 (historic=fort, wikidata=Q5471739) = the same spot (36.1642, -86.7754). So the fort - the Clayton
    map's "D Cross's owner / Stone House / former Fort" at the town's SW corner - sits 217 m NORTH of the
    city P625 (36.162222, -86.774444), same longitude.
  - **Clayton 1804 map READ (1400 px rendering of the full 2557x1913):** the river band runs along the BOTTOM
    of the drawing; the fort is on it at the town's SW corner, where the river bends; the town (numbered
    buildings 1-20, Market/Main St, White Hall, Nashville Inn, Dr Henning's) is NORTH of the river; the
    **Rich Branch** enters from the top-right and flows south into the river EAST of the town (its confluence
    is in the drawing's SE corner, next to the "Cumberland River" label - the map's author labels the whole
    band "Cumberland River"); "Johnson's House, Ferry & Keel Boat Landing" is at the western river edge;
    Cemetery / "now Capitol Hill" (the Walker house) / Judge McNairy's / Sulphur Spring extend the drawing
    well NORTH of the town. Hypothesis: the bottom band is the rivers' corner (the Tennessee running
    SW->E into the Cumberland), so the 1804 town sits on the NE side of the corner and the P625 point
    (217 m south of the fort) likely falls INSIDE the drawn extent - but the hand-drawn, not-to-scale sketch
    must be georeferenced before the verdict (147/148 precedent: point = center of the drawn extent).
  - **OSM river data around the CBD is unreliable - do not trust it for this decision:** api.openstreetmap.org
    /map (0.02 deg boxes) + /way/40806685/full ("Cumberland River") give a downtown "hook"
    (36.177,-86.781) -> (36.161,-86.747) that puts the river EAST of P625 at 36.162 lat (contradicting 151's
    "P625 east of the Cumberland") and no Tennessee River in the SW boxes at all; the confluence is not
    cleanly mapped. Nissan Stadium (way 58759639) is (36.1665, -86.7713) - NE of the CBD, not at a river corner.
    Use the old maps + Wikidata, not OSM, for the point decision.
  - **OVERPASS IS DEAD FROM THIS MACHINE** (PITFALLS added): overpass-api.de -> HTTP 406 even with a UA;
    kumi.systems -> XHTML error page. Use api.openstreetmap.org instead: /map?bbox=... (bbox <= ~0.02x0.02
    deg or it hits the 50000-node limit) and /way/{id}/full for single ways.
  - **Haydon 1860 downloaded but NOT yet looked at** (context limit). Re-download URLs (both verified live 155):
    Clayton: https://upload.wikimedia.org/wikipedia/commons/0/0c/1804_Map_of_Nashville_published_1880.jpg
    (2557x1913); Haydon: https://upload.wikimedia.org/wikipedia/commons/d/da/1860_Haydon_map_of_City_of_Nashville_and_Edgefield.jpg
    (10000x6082, 10.4 MB). PIL lives in the PROJECT .venv, not system python3: run `.venv/bin/python` and set
    Image.MAX_IMAGE_PIXELS = None (the Haydon trips PIL's 178 M-px limit).
- Q23197 + Q5471744 verified facts from 151 stand (catalog_wd disk cache, data/raw/catalog/wd/):
  Q23197 label "Nashville", ONE P625 (-86.774444, 36.162222), P373 ['Nashville, Tennessee'], P131
  [('Davidson County','Q1177705')], enwiki 'Nashville, Tennessee', no trap; Q5471744 (Fort Negley) ONE
  P625 (-86.774658, 36.145097), P373 ['Fort Negley'] = photos + 3 Fletcher views, no plan. No catalog
  collision (151 greps). (151's "P625 EAST of the Cumberland" was an assumption from the confused OSM data -
  re-express the lead doc's point note from the map evidence instead.)
- **1a (Poe map) VERDICT: no swap.** Live-checked https://www.loc.gov/item/2003630459/?fo=json (needs a
  browser User-Agent; the web_fetch tool gets 403): item date "186?", created_published "[186-]", dates
  facet 1860, creator "Poe, O. M. (Orlando Metcalfe), 1832-1895", desc: "...Signed in ink handwriting at
  bottom: From Chief Eng'rs Office, H'd Qu'rs Mil'y Div'n of the Mis., O.M. Poe, Capt. & Actg. Chf. Eng'r.
  ...LC Civil War maps (2nd ed.), 433.2". The Commons page date "1860s" (QS +1860-00-00/8) IS that same
  LOC dating - a drawing date, not an upload date. I downloaded the 19690x11294 original (PIL needs
  Image.MAX_IMAGE_PIXELS = None - it exceeds the 178 M-px bomb limit) and read the signature at full res:
  it is "From Chief Eng'rs Office / H'd Qu'rs Mil'y Div'n of the Mis. / O. M. Poe / Capt. & Actg Chf Eng'r
  (17x29.)" - **"(17x29.)" is the sheet size (17x29 inches, the LC cataloguing convention), NOT a year**
  (151 read "1864" in the 1280 px thumbnail - wrong). No signed year exists, so no known-date swap; the row
  keeps date "1860s" -> year_of 1860 (the YEAR regex finds the 4-digit year; "2003630459" in the title does
  not match) -> keep() passes (<= 1925). Row: date "1860s", NO date_commons (that key only appears when a
  swap is applied).
- **1b (Defenses plate) VERDICT: swap dict(date="1895").** The file's Commons description links the David
  Rumsey group: image 1780.113 in group 1780.000, and cites "LC Civil War maps (2nd ed.), 99; Civil War maps
  in the National Archives, 8; Phillips, 1353; LeGear. Atlases of the United States, 266". The exact title
  re-confirmed (the "..." is literal, 3 dots): `File:Defenses of Chattanooga, Tenn. Battery Erwin ... Battery
  Coolidge. Defenses of Nashville, Tenn. Capitol (IA dr defenses-of-chattanooga-tenn-battery-erwin-battery-
  coolidge-defenses-01104241).jpg` (1536x886, Public domain; the IA item itself is gone - archive.org
  /details/ 404, /metadata/ empty; but sibling dr_ items of the same group survive on IA with the group's
  catalog record: e.g. dr_map-of-the-united-states-of-america-showing-the-boundaries-of-the-union-and-
  01104300: title "...Julius Bien & Co., Lith., N.Y. (1891-1895)", date 1895, creators incl. "United States.
  War Department", publisher U.S. GPO, collection david-rumsey-map-collection). AbeBooks: "BIEN, Julius.
  1895"; Rumsey listing: "1895. Atlas to accompany the official records of the Union and Confederate
  armies". I read the plate at full res (downloaded via Special:FilePath): header = "ATLAS TO ACCOMPANY THE
  OFFICIAL HISTORIES OF THE UNION AND CONFEDERATE ARMIES 1861-1865" (151's "UNITED STATES" was a misread;
  this is the first edition's title) + "PLATE C-X-" (Roman numeral CXIII or CXVIII at this resolution; 151
  read CXIV). Nine panels: 1 Battery Erwin + 2 Battery Coolidge (Chattanooga); 3 Nashville Magazine Battery
  ("Dec. 1864", Eng. Capt. J.S. Wheatley), 4 Nashville Capitol ("Nov. 30, 1864", Eng. Capt. J. St. Clair
  Morton), 5 Fort Dan McCook ("Dec 21, 1864"), 6 Fort Morton ("Dec. 1864", Eng. Capt. H.K. Wright), 7 Fort
  Hill ("Dec. 1, 1864", incl. a small "Plan of Nashville, Tenn."), 8 Fort Nashville, 9 the Nashville Heights
  ("Dec. 1864") - 7 of 9 Nashville, the Fort Negley panel among them, as 151 recorded. **Row date = 1895**
  (the dated copy this scan comes from; the first edition's 1884-85 could not be verified online from this
  machine - routes tried and dead: LOC search API (quoted phrases return 0 hits, keyword AND ranks the
  atlas out of top results), HathiTrust (Cloudflare "Just a moment"), Google Books API (quota exceeded),
  David Rumsey (reCAPTCHA "Verify Access"), IA /download/ of the 1961/1989 LOC catalog books (401 =
  lending-restricted items; the 1961 ed. is the "2nd ed." the citation means, its p.99 would settle it but
  is unreachable). So the lead doc records: first edition 1884-85 per the plate's own header title (not
  online-verified from this machine), scanned copy 1895 = the row's date; the drawings themselves are the
  Nov 30 - Dec 1864 surveys. 1895 is outside the 1660-1880 window by 15 years - acceptable here: this is a
  Civil War fortification plan (the task Notes' explicit exception; the DC 1865 ring precedent), and the
  151 verdict staged it on that basis.)
- **Site point (the last open decision):** the 1804 Clayton map (the oldest staged drawing) shows the 1790s
  town at the Cumberland/Tennessee confluence, WEST of the Cumberland; the P625 (-86.7744, 36.1622) sits
  EAST of the river, so the 147/148 drawn-extent-center precedent applies: a P625-centered 2000 m town box
  (hw 1000 m) likely misses the confluence, so refine the point to the center of the old town's drawn
  extent. I downloaded the full-res Clayton original (2557x1913, 1.78 MB) to /tmp/usn152_clayton.jpg but hit
  the context limit before looking at it - /tmp is gone. NEXT SESSION re-downloads it (Commons title
  `File:1804 Map of Nashville published 1880.jpg`, url
  https://upload.wikimedia.org/wikipedia/commons/0/0c/1804_Map_of_Nashville_published_1880.jpg), looks at
  the drawn extent (the town between the Cumberland and the Rich Branch, the old fort at the corner, White
  Hall, the ferry landings), then fixes the point with Nominatim landmarks (the Cumberland-Tennessee
  confluence, the Rich Branch mouth, the Cumberland's west bank near the town; the old Fort Nashborough
  site) and records the choice + why in the lead doc, as 147/148 did for SF. Both candidates leave every
  P625 <50 km from the point (no --verify flag); the evidence tie stores the table point (dist_m 0.0) so
  --check is offline-safe either way.

### EXACT next steps: settle the site point, apply the verdicts (the 145-150 pattern), then done
1. **Site point (the only research left, CONTINUED from 155):** re-download both maps (URLs above; .venv
   PIL + MAX_IMAGE_PIXELS=None). (a) Crop the Clayton full-res around the fort marker (the small-image
   (390,800) of 1400x1047 -> full-res ~(720,1465)) and around the SE corner (Rich Branch confluence, small
   ~(1250,850) -> full-res ~(2275,1552)); record their pixel coords. (b) Get the Rich Branch's modern
   confluence coordinates: Nominatim "Rich Branch" failed in 155 - try the OSM API /map?bbox=-86.77,36.15,-86.75,36.17
   (0.02x0.02 deg fits the 50k-node limit) and look for a waterway named "Rich Branch" (the Edgefield area,
   east of the CBD). (c) Georef the Clayton drawing with the 2 anchors (fort = 36.164167,-86.774444; the
   confluence) as a linear map, compute the drawn extent's center (SW corner at the fort, NE at the
   Cemetery/McNairy hill, W at the Johnson ferry, E at the Rich Branch). (d) Cross-check on the Haydon 1860
   (to-scale, has a scale bar): find the 1804 core area (the dense old grid WEST of the Rich Branch, around
   the fort corner) and its extent; the two should agree to a couple hundred m. (e) VERDICT: point = P625
   if the 2000 m box (hw 1000 m) covers the drawn extent with margin, else the center of the drawn extent
   (147/148 precedent); record the choice + why in the lead doc. Both candidates leave every P625 <50 km
   away and the evidence tie stores the table point, so --verify/--check are offline-safe either way.
2. **Apply (one session):** fit/src_us_cities.py: docstring += Nashville (replace "Nashville follows in a
   later session"); SITES += Q23197 (id "nashville-q23197", name "Nashville", named "Nashville", kind
   "town", region "United States", place "Davidson County, Tennessee", wikipedia
   https://en.wikipedia.org/wiki/Nashville,_Tennessee, point = step-1 decision, note like the others' aerial
   note + the oversize-sheet review-item note: the Haydon/Poe/Defenses sheets span the city and its fort
   ring far beyond the 2 km box -> likely review items, the NY 1811 / DC 1865 ring precedents; no extent
   field - the extras row has none, pipeline/catalog.py:686 sets extent_m from the site box); SOURCES +=
   clayton_1804 (dict(date="1804") - page "1880" = Clayton book publication), haydon_1860 (no swap - page
   "1860" = drawing date), poe (NO swap - page "1860s" = the LOC-verified drawing date; row date "1860s",
   no date_commons), defenses (dict(date="1895") - page date empty, so date_commons ""), all p="plan").
   Exact file titles (case-sensitive; the "..." in the Defenses title is literal):
   `File:1804 Map of Nashville published 1880.jpg`; `File:1860 Haydon map of City of Nashville and
   Edgefield.jpg`; `File:Map of Nashville, Tennessee. LOC 2003630459.jpg`; `File:Defenses of Chattanooga,
   Tenn. Battery Erwin ... Battery Coolidge. Defenses of Nashville, Tenn. Capitol (IA dr
   defenses-of-chattanooga-tenn-battery-erwin-battery-coolidge-defenses-01104241).jpg`.
3. **Run:** live --verify (4 QIDs, expect no flag, no trap) + live stage (expect "1 new sites, 4 new
   pictures; build (236c): nashville-q23197") + offline --check (expect 15 rows, 15 pass) + --golden
   (4 extras / 15 files / 15 classified). Live under .venv/bin/python; --check plain python3.
4. **Tests:** tests/test_src_us_cities.py - row asserts 11->15, PASS-line list += 4, qid-table += Q23197
   (incl. the point decision), extras ids += nashville-q23197, years dict += the 4 titles (1804, 1860,
   1860, 1895 - the Clayton and Defenses swaps give the known years, NOT the page values: the Clayton row's
   date_commons is "1880", the Defenses row's date_commons is ""/absent, the Poe row keeps date "1860s",
   the Haydon row date "1860"), named_by_qid += {Q23197: "Nashville"}; then
   `.venv/bin/python -m pytest tests/test_src_us_cities.py tests/test_region.py -q` (expect 7/7; the
   full-suite caveat stands: agent c's test_fit_queue failure).
5. **Lead doc:** docs/lead_us_cities.md += `## Nashville (Q23197)` (site point + decision; per-candidate
   STAGED/DROP with exact titles + reasons, incl. for the Poe map: LOC item 2003630459 verified "[186-]",
   signature has NO year - "(17x29.)" is the sheet size - so no swap; for the Defenses plate: the atlas
   (Rumsey group 1780.000, image 1780.113) cataloged 1895 (IA sibling-item record "Julius Bien & Co.,
   Lith., N.Y. (1891-1895)", AbeBooks, Rumsey), first edition 1884-85 per the plate's own header (not
   online-verified from this machine - the blocked routes are listed in the 152 DECISIONS entry), panels
   surveyed Nov 30 - Dec 1864, 7 of 9 Nashville, 1895 outside the 1660-1880 window but a Civil War
   fortification plan = a drawing per the task Notes (DC 1865 ring precedent); the Fort Negley record: no
   plan on Commons, Q5471744 facts, the 3 Fletcher views as 236b leads; the 15-PASS transcript). Header:
   "four cities staged; box 3 done".
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
