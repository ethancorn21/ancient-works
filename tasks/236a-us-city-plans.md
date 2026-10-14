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
  - **OVERPASS IS DEAD FROM THIS MACHINE** (file in PITFALLS next session): overpass-api.de -> 406
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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207b-maclauchlan.md` (blocked) - hand-over: (2026-10-13, iteration 204, agent c - NO work on this task. The driver auto-put it back to
- `tasks/207c-roy.md` (blocked) - hand-over: (2026-10-13, iteration 205, agent c - NO work on this task. The driver auto-put it back to
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/212-cover-final.md` (in-progress) - hand-over: (2026-10-13, iteration 255, agent a, written at the context limit -
- `tasks/236a-us-city-plans.md` (in-progress) - hand-over: (2026-10-13, iteration 155, agent a, written at the context limit - main MERGED (commit 3093e4e): review.json conflict resolved to main's side (its port bba5961 = newer complete export: fort-ancient resolved out of the open queue by the port's new platefits doc, numancia gained the owner's Not-this candidate; my side had only a stale at-timestamp, 0 unique items; 456 recomputed open = export, 0 plans lost; 12/12 tests green). SITE-POINT RESEARCH: Fort Nashborough = Q5471739, P625 (36.164167,-86.774444) [Wikidata+Wikipedia+OSM agree] = the Clayton 1804 "former Fort" at the town's SW corner, 217 m NORTH of the city P625; Clayton map READ (town N of the rivers' corner band, Rich Branch enters east of the town) - P625 likely inside the 1804 extent, verdict waits on a 2-anchor georef + Haydon 1860 cross-check (exact recipe in the task file step 1; both maps' re-download URLs there). OSM river data around the CBD unreliable for this; Overpass dead from this machine (PITFALLS). Next: finish the georef, pick the point, then apply like 145-150 (steps 2-6).)
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

### 2026-10-13 236a DECISION: iteration 150 - Vioget 1839 STAGED as the 4th SF row (the first plan of the old town; no date swap): stage "0 new sites, 1 new pictures", --verify unchanged (3 QIDs), --check 11/11, golden regenerated, tests 7/7 green, lead doc updated; Nashville (Q23197) is now the only thing left of box 3
- The 149 hand-over's step 1 (green confirm) + step 2 (stage the Vioget 1839 row) in one session; no new research (the 149 step-5 live checks stand: 2400x2107, Public domain, page date 1839-01-02 = the drawing's date, "San Francisco" in the desc inside the gate's 600-char window, keep() passes).
- fit/src_us_cities.py: docstring += the 1839 Vioget plan (first plan of the old town) in the SF list; VIOGET_1839 = [("File:1839 Plan of Yerba Buena (Jean Jacques Vioget).jpg", "Q62", "San Francisco", dict())]; SOURCES += "vioget_1839" (p="plan", label "{name}, the Vioget plan (1839, the first plan of the old town)"); the SF comment block now records that the Eddy/1850 titles print the city but the Vioget title does not (gate-safe via the description, checked live).
- Live stage: "staged: 0 new sites, 1 new pictures" (Q62 already staged - exactly as the 149 hand-over predicted). No known-date swap: the page date 1839-01-02 IS the drawing's date (the staged row: year 1839, date "1839-01-02", no date_commons). Live --verify: unchanged (3 QIDs; no >50 km flag; no trap - the 'San Francisco' name search's first P625 hit is Q62 itself).
- Offline --check: 11 rows, 11 pass, 0 fail, 0 no-tie (the new line PASS caption_coords san-francisco-q62|File:1839 Plan of Yerba Buena (Jean Jacques Vioget).jpg, on the site's own point). --golden regenerated (3 extras / 11 files / 11 classified).
- Tests (5 edits, all per the 149 list): the module docstring "three of San Francisco" -> "the four ... (1839 Vioget first)"; the check-staged and evidence tests' 10->11 row asserts; the check-staged PASS-line list += the Vioget line; the qid-table years dict += the Vioget title -> 1839 (want/self-scaling parts needed no edit, as predicted). 7/7 green offline (tests/test_src_us_cities.py + tests/test_region.py; the full-suite caveat stands: agent c's test_fit_queue failure).
- docs/lead_us_cities.md (3 edits): the header SF list += the 1839 Vioget plan; the Vioget subsection's heading "- verified, to stage next" -> "- STAGED (2026-10-13, the 4th SF row)" with the staged-row facts; the offline-check transcript now the 11 PASS lines / "evidence: 11 rows, 11 pass, 0 fail, 0 no-tie".
- Boxes: 1/2/4/5 stand (SF is now fully staged: 4 rows). Box 3 stays open for Nashville only: the Q23197 town site (+ the Fort Negley fort site) - next session is live research first (Q23197 re-verify via pipeline/catalog_wd; the early 1790s town plans at the Cumberland/Tennessee confluence; the Fort Negley Civil War plans; verdicts in DECISIONS BEFORE editing), then apply like the 145-150 pattern; when staged, tick box 3 and set Status: done.

### 2026-10-13 236a DECISION: iteration 151 - Nashville research complete (live, 2026-10-13); verdict: stage 4 rows on a new nashville-q23197 site (the 1804 Clayton/Temple map with a known-date swap, the 1860 Haydon & Booth plan, the O.M. Poe LOC survey map with a swap, and the 1861-65 "Official Histories" atlas plate CXIV - nine fortification plans incl. Fort Negley - with a swap); NO Fort Negley fort site (no fort-only plan on Commons: photos and the 3 Fletcher 1864 litho views only - the views are 236b leads); Q23197 and Q5471744 both verified clean, no traps, no catalog collision - next session applies the verdicts
- Research-only session (the 145/147 pattern); every fact verified live: Q23197 + Q5471744 re-verified via pipeline/catalog_wd (the robust WD path per the gzip-200 pitfall; its disk cache in data/raw/catalog/wd/ keeps re-runs free); Commons full-text searches (rounds 1-3: map/plan/town of Nashville, Fort Negley, Negley, defenses, 1790-1865 queries, both cities' P373 categories); 18-file metadata batch; 6 thumbnails looked at. Session hit the context limit after the atlas 404 (below) - no repo file was touched; tests remain 7/7 from 150. The full per-candidate record (sizes, dates, licences, gate windows, exact titles, the DROP list, the 236b leads) is in the task file's hand-over - the entries below are the verdicts.
- **Q23197 (Nashville) re-verified:** label "Nashville", desc "capital city of the U.S. state of Tennessee and seat of Davidson County", ONE P625 (-86.77444444444444, 36.16222222222222) = downtown (EAST of the Cumberland, per the prep), P373 ['Nashville, Tennessee'] (Commons category - its 200 files are modern photos, not a map source), P131 [('Davidson County', 'Q1177705')], enwiki 'Nashville, Tennessee', first name-search hit with P625 = Q23197 itself (no trap). Exact greps: no Q23197 / no "nashville" in data/catalog/sites.jsonl, data/catalog/extras.jsonl, data/catalog/extras_us_cities.jsonl or web/data/sites.json; the only canonical "Nashville" hit is the unrelated "Nashville I" gorget at castalian-springs-mound-site-q5049584 (data/commons/files.jsonl) - no collision, no (site, title) clash risk.
- **Q5471744 (Fort Negley) re-verified:** label "Fort Negley", desc "army fort in Nashville, TN", ONE P625 (-86.774658, 36.145097) (~1.9 km S of the city P625), P373 ['Fort Negley'] (Commons category = 12 files: Barnard/Albee/modern photos + the 3 Fletcher views - NO plan), P131 [('Nashville', 'Q23197')], enwiki 'Fort Negley', first name-search hit with P625 = itself (no trap). Not in the catalog (0 hits in all three files).
- **Site decision (final in the hand-over):** `nashville-q23197`, kind "town" (2000 m -> 2 km x 2 km box), named "Nashville", place "Davidson County, Tennessee". Point: P625 vs a refined point at the old town's center - the 1804 Clayton map (the oldest staged drawing) shows the 1790s town at the Cumberland/Tennessee confluence (west of the Cumberland; P625 is east of it), so the 147/148 drawn-extent-center precedent applies: refine if the P625-centered box misses the confluence tip. Both candidate points leave every P625 <50 km away (no --verify flag) and the evidence tie stores the table point (dist_m 0.0), so --check is offline-safe either way. extent_m: pipeline/catalog.py:686 derives it from the site's box, NOT from the row - the extras row cannot carry one, so the oversize sheets (Haydon, Poe, the Defenses ring) get the review-item note instead (the NY 1811 / DC 1865 ring / Venice precedents).
... (4.7 KB more: `grep -n -A 200 -F '## 2026-10-13 236a DECISION: iteration 151 - Nashville research complete (live, 2026-10-13); verdict: stage 4 rows on a new nashville-q23197 site (the 1804 Clayton/Temple map with a known-date swap, the 1860 Haydon & Booth plan, the O.M. Poe LOC survey map with a swap, and the 1861-65 "Official Histories" atlas plate CXIV - nine fortification plans incl. Fort Negley - with a swap); NO Fort Negley fort site (no fort-only plan on Commons: photos and the 3 Fletcher 1864 litho views only - the views are 236b leads); Q23197 and Q5471744 both verified clean, no traps, no catalog collision - next session applies the verdicts' DECISIONS.md`)

### 2026-10-13 236a DECISION: iteration 152 - both open date checks answered (live, no repo edits); Poe LOC map gets NO swap (page "1860s" = the LOC-verified drawing date "[186-]"; the signature's "(17x29.)" is the SHEET SIZE, not 1864 - 151's thumbnail read was wrong); the Defenses plate swaps to 1895 (the David Rumsey/IA group 1780.000 the scan comes from is cataloged 1895, "Julius Bien & Co., Lith., N.Y. (1891-1895)"; the plate header says "ATLAS TO ACCOMPANY THE OFFICIAL HISTORIES OF THE UNION AND CONFEDERATE ARMIES 1861-1865" - 151's "UNITED STATES" was a misread; panels surveyed Nov 30 - Dec 1864); the first edition's 1884-85 could not be verified online from this machine, so the row takes the scanned copy's verified 1895; site point (Clayton 1804 extent) is the only thing left, then apply like 145-150
- Research-only session (the 145/147 pattern); no repo file touched. Every fact below verified live 2026-10-13.
- **1a (Poe map, LOC 2003630459): no date swap.** https://www.loc.gov/item/2003630459/?fo=json (curl with a browser User-Agent; the web_fetch tool gets HTTP 403 from loc.gov) returns: date "186?", created_published "[186-]", dates facet 1860, APA cite "[186]", contributors "United States. Army. Military Division of the Mississippi. Chief Engrs. Office" + "Poe, O. M. (Orlando Metcalfe), 1832-1895", description: "Detailed city map showing streets, railroads, all buildings ... Relief shown by fold lines. Pen-and-ink (black) and lead pencil. Signed in ink handwriting at bottom: From Chief Eng'rs Office, H'd Qu'rs Mil'y Div'n of the Mis., O.M. Poe, Capt. & Actg. Chf. Eng'r. Oriented with north toward the lower right. ... LC Civil War maps (2nd ed.), 433.2." The Commons page's date "1860s" (DateTimeOriginal, QS precision 8) is that same LOC dating - the drawing's date, not an upload date. I downloaded the 19690x11294 original from upload.wikimedia.org (PIL needed Image.MAX_IMAGE_PIXELS = None - the 222 M-px image trips PIL's 178 M-px decompression-bomb limit; PITFALLS candidate) and cropped the signature at full resolution: it reads "From Chief Eng'rs Office / H'd Qu'rs Mil'y Div'n of the Mis. / O. M. Poe / Capt. & Actg Chf Eng'r (17x29.)" - the parenthetical is the SHEET SIZE (17x29 inches, the Library of Congress cataloguing convention for folded maps), NOT a year. 151 read "1864" in the 1280 px thumbnail - that was wrong. Consequence: no known-date swap; the row keeps date "1860s" (year_of -> 1860; the "2003630459" in the title does not match the YEAR regex; no date_commons key since no swap). keep() passes (1860 <= MAX_YEAR 1925) and the NO regex matches neither title nor the 600-char desc.
... (4.9 KB more: `grep -n -A 200 -F '## 2026-10-13 236a DECISION: iteration 152 - both open date checks answered (live, no repo edits); Poe LOC map gets NO swap (page "1860s" = the LOC-verified drawing date "[186-]"; the signature's "(17x29.)" is the SHEET SIZE, not 1864 - 151's thumbnail read was wrong); the Defenses plate swaps to 1895 (the David Rumsey/IA group 1780.000 the scan comes from is cataloged 1895, "Julius Bien & Co., Lith., N.Y. (1891-1895)"; the plate header says "ATLAS TO ACCOMPANY THE OFFICIAL HISTORIES OF THE UNION AND CONFEDERATE ARMIES 1861-1865" - 151's "UNITED STATES" was a misread; panels surveyed Nov 30 - Dec 1864); the first edition's 1884-85 could not be verified online from this machine, so the row takes the scanned copy's verified 1895; site point (Clayton 1804 extent) is the only thing left, then apply like 145-150' DECISIONS.md`)

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
