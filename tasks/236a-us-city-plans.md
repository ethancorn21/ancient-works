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

(2026-10-14, iteration 163, agent a - site-point research, CONTINUED. Repo files UNCHANGED this session (staged files still 3/11/11; baseline tests 7/7 green from 161). No test run this session (research only). Big new finding: **the OSM `/api/0.6/` endpoints are ALIVE from this machine** (161's 410s were `/map`-specific or transient): `/api/0.6/relation/{id}`, `/api/0.6/way/{id}`, `/way/{id}/full` and `/node/{id}` all returned **200** (curl, browser UA) on 2026-10-14. This replaces the 181 MB pbf plan with a handful of small requests. The session ended at the context limit right after reading the Tennessee relation XML.)

### OSM route facts (verified live 163)
- **ALIVE**: `api.openstreetmap.org/api/0.6/` - relation/{id} (200), way/{id} (200), way/{id}/full (200 - 161 said 410; re-test, it worked today), node/{id} (200). **DEAD**: `/map?bbox=` (410, per 161 - retest if needed). Use a browser UA (Mozilla/5.0 Chrome/120) - worked.
- **Overpass is fully dead from this machine**: overpass-api.de now **406 Not Acceptable** (NEW behavior; 155/160 had 504/400), maps.mail.ru 504, kumi XHTML error page. Do not retry any Overpass instance.
- **Nominatim** (project UA via pipeline/aw.py `UA`, 1 r/s): `featuretype=waterway` works; **`format=geojson` returns only a centroid POINT for big rivers** (tried geometry=full, extract_way=1, skeletonize - all ignored by this instance). Use it to get the OSM relation IDs, then the /api/0.6/ route for geometry.
- **Relation IDs (from Nominatim, saved in /tmp/nash163/rivers.json)**: Cumberland River = **relation 2182468**; Tennessee River = **relation 2182503** (both verified by name in the response).
- **Tennessee relation 2182503 XML (78 members)**: the FIRST TWO members are `role="mouth"` **nodes 1752049047 and 4636304129** - the river's mouth = the Cumberland confluence (two nodes: the wide river's two banks at the junction). **NEXT: `curl https://api.openstreetmap.org/api/0.6/node/1752049047` and `.../node/4636304129` -> the confluence point(s)** (expect ~ (36.14?, -86.72?); average or take the one that sits on the Cumberland side).
- **No OSM waterway named "Rich Branch" in the Nashville viewbox** (Nominatim bounded: 0 hits; the name exists only far away: near DC (39.09,-77.23), GA (36.12,-82.21), MO (40.26,-90.55), E-TN (35.59,-83.54)). So the 1804 "Rich Branch" stream is NOT name-findable in OSM - the mouth coordinate will come from the georeferenced Haydon map instead (see below); the pbf was only needed as an independent check and can be DROPPED (or done opportunistically: geofabrik tennessee-latest.osm.pbf 181 MB, protobuf in a throwaway venv - spec in the 161 section below).
- **Dead USGS sources**: hdwds.usgs.gov (NHD) 000 unreachable; edits.usgs.gov 000; geonames.usgs.gov (GNIS) 301->dead; www.usgs.gov 403. **Live**: waterdata.usgs.gov (NWIS, gauges - not confluence points) and the LOC API (below).
- **LOC maps search API** (browser UA; note: response shape varies - `results` may be a list or {documents:[...]}): `https://www.loc.gov/maps/?q=nashville&fo=json&fa=original-format:map&dates=1900/1910` -> **NO 1903 USGS quad in LOC** (9 hits: Sanborn sheets, 2012593686 Davidson County, Civil War items). The 1903 quad cross-check is DEAD as a LOC route; try archive.org "usgs" or drop it (the confluence from OSM is now available anyway, so the quad is no longer needed for the confluence - only a nice-to-have check of the stream's 1903 name/position).

### Haydon 1860 map - full-res pixel measurements (10000x6082 sheet; /tmp/nash163/haydon1860.jpg is GONE - re-download, URL below)
- **Title block** (bottom-left, full-res ~ (1250-3250, 1150-2300)): "CITY OF NASHVILLE AND EDGEFIELD, DAVIDSON COUNTY, TENNESSEE. Published by Haydon and Booth Civil Engineers & Surveyors. 1860. **SCALE 400 FEET TO 1 INCH**. DRAWN AND LITHO BY THE SAME." The only scale statement on the sheet.
- **NO graduated scale bar**: the long diagonal line by the compass rose (upper right, rose center ~ (6950,1325)) is the compass AXIS (arrowed), not a scale bar. So scale = 400 ft/inch of the ORIGINAL sheet; to get px/inch of this scan you need the sheet's physical size (Rumsey/LOC metadata) OR just solve scale from the georef anchors (the fitted scale then implies an effective DPI - report it as a sanity number).
- **Confluence (Tennessee meets Cumberland)**: the blue-shaded Tennessee band joins the hatched Cumberland band at **~ (2950, 5240)** (grid crop (2200,4400)-(4400,5450) @0.65: the blue band descends from (2710-2970, 4400-4585) and meets the hatched band at (2890-3000, 5200-5290)). Nearby labels: "Corporation Grounds" (2940-3060, 4490-4570), "CLARKSBY'S LOTS" above, "Perry's Residence" (2500-2900, 4850-5050) SW, "Gen. Barrow's Res." (3660-3810, 5170) E, the "WATSON ST / CATHEDRAL AND / OAK ST / TULIP ST / ED / LEAFEVRE / MINNICK / WELLS" grid (4100-4400, 4700-5300) E of the river.
- **Rich Branch stream**: labeled stream (label "Rich Branch" ~ (6100-6300, 3550-3700); "Sulphur Spring / Bath" label (5450-5600, 3380)) runs SE from the north edge (near CRAWFORD ST, ~ (5270,3180)) down the east side of the diagonal WASHINGTON avenue, crosses CHERRY ST (y~3560) and COLLEGE ST (y~3840), with a meandering S-curve at (6050-6200, 3950-4050) and **the mouth at the red riverfront zone ~ (6150-6300, 4000-4100)** (the hatched river edge below it; the red band tapers out at ~ (6100, 4020)). **NOTE**: a second small wavy line at (6150-6300, 3950-4050) may be a separate tiny stream or an oxbow - **verify with a 2x zoom crop (6000-6500, 3900-4150) before using the mouth**. Street grid in the area: FRONT ST / MILL ST / ADAMS ST, JACKSON ST (vertical ~x6100), "The late H.W. McGavuck's Reserve" E.
- **State Capitol** (the same building that stands today, drawn as a dark block in a green square labeled "STATE CAPITOL"): **~ (5000, 3250)** (h_downtown crop (3700,2400)-(5300,4350) @0.6, display (730,480)).
- **Market Square / City Hall**: ~ (4700-4920, 3620-3780) same crop (display (600-730, 730-830)).
- **Old-town SW corner (= Fort Nashborough site)**: the corner where the dense downtown grid meets the red riverfront by the "WHARF" label: **~ (3980, 3850)** (h_downtown display (170,870)) - **UNVERIFIED with a grid overlay** (the g_swcorner.jpg crop (3650,3550)-(4550,4200) was generated but never viewed; re-check the exact corner pixel, it should be the grid corner NW of the wharf, the 1790s town's SW corner per the fort history).
- **Cumberland river band** (the hatched band = the river, pale center): north bank passes (6000,4020)->(6600,4180) in the east and (4900-5200, 4150-4300) in the west (the h_confluence crop showed the band entering the sheet's left edge ~ (1900-2100, 3600-3800)); the big "D R I V E R" letters run diagonally (D (500-700,4450) ... R (6700-6900,4750-4850)) over the hatching in the SW half; "Shelby" label (5500-5800, 4150-4220) on a pale strip at the N bank (the Shelby district is actually across the river - the strip may be a floodplain/sandbar - check when measuring the bank).

### Clayton 1804 pixel anchors: the 161 measurements stand (below, unchanged). Re-download URL in the 161 section.

### DECISION (this session's conclusion) - the site point will be settled like this
1. **Confluence point** = the OSM mouth node(s) of relation 2182503 (fetch /node/1752049047 + /node/4636304129; one or both will sit at the Cumberland junction; average if two banks, or take the one closer to the projected Haydon junction (2950,5240) once georeferenced). This is anchor-independent (no map input) -> use it as the **third Haydon anchor** (map junction pixel (2950,5240) -> OSM confluence) alongside the Capitol (map (5000,3250) -> Nominatim "Tennessee State Capitol" point - fetch it: Nominatim q=Tennessee State Capitol, featuretype=building, Nashville) and the fort corner (map ~(3980,3850) -> Q5471739 (36.164167,-86.774444); re-verify the corner pixel first).
2. **Least-squares similarity** (scale+rotation+translation, ENU metres at the city) over the 2-3 anchors; report per-anchor residuals in m; **independent checks**: (a) projected Cumberland centerline (sample 3-4 points along the map band, e.g. (2100,3700),(4900,4250),(6300,4150),(8300,4600)) vs the OSM confluence + Nominatim west-segment centroid (36.171,-86.900 - the 3rd Nominatim hit); (b) the fitted scale (m/px) vs "400 ft/inch" implied by a plausible scan DPI (a 10000-px-wide sheet at 400 ft/inch means the original was ~10000/DPI_inches wide - report the implied original size, expect something like 30-50 in); (c) projected street names vs Nominatim (Water St, College St, Cherry St, Adams St, Front St all survive in modern Nashville - a few spot checks).
3. **Mouth of the Rich Branch** = projected from the georeferenced Haydon (pixel ~ (6200,4050) - refine per the 2x zoom) -> this is **anchor B for the Clayton map** (deviation from 161's "OSM point": the stream is unnamed in OSM, Nominatim-bounded 0 hits - recorded here and in DECISIONS). Its uncertainty is the georef residual + the hand-litho accuracy (say ±100-200 m) - fine for the verdict.
4. **Clayton 2-anchor similarity** (A = fort pixel (718,1345) -> Q5471739; B = mouth pixel (2282,1597) -> the Haydon-derived mouth), ENU metres, origin at the fort; project every 161 anchor + the town-extent corners (ferry / Market-row river edge / Walker row / "1 2" houses) + the full-ink corners.
5. **VERDICT (155/161 rule)**: point = P625 (-86.774444, 36.162222) iff the 2000 m P625 box covers the projected town extent with margin; else point = center of the projected town extent, recorded to 5 decimals (the SF precedent). Preliminary read of the 161 numbers: the extent likely exceeds the box to the E (~1.4-2.5 km E of the fort vs 1.0 km box edge) at any plausible scale (1.6-2.8 m/px), so expect **center of extent** - but compute it, don't assume. Both candidates keep every P625 <50 km (no --verify flag); the evidence tie stores the table point (dist_m 0.0) -> --check stays offline-safe.
6. **Cross-checks before recording**: (a) the projected Clayton town extent vs the 1804 old-grid core on the georeferenced Haydon (the dense grid WEST of the stream, around the fort corner - should agree to a couple hundred m); (b) 2-3 Nominatim landmark sanity checks on projected Clayton features (Walker house vs the modern Capitol Hill/Parthenon area, the ferry vs the modern W river end, the cemetery).
7. **Then RECORD** (DECISIONS + the lead doc): the point, both anchors with pixels+coords, the Haydon georef (anchors, scale, residuals, implied original sheet size), the mouth, the projected corners, the verdict + why.
8. **Apply** (next session, the 155-era steps 2-6 below, unchanged): SITES += Q23197 (point = the verdict), SOURCES += the 4 Nashville rows, live --verify/stage, offline --check (expect 15 rows), --golden (4/15/15), the 5 test edits, lead doc `## Nashville (Q23197)`, tick box 3, Status: done.

### Exact next step (fresh session, in order)
1. `mkdir /tmp/nash163 && curl` the two maps (URLs in the 161 section) + re-fetch rivers.json if wanted (the two relation IDs are in this hand-over: 2182468 / 2182503).
2. `.venv/bin/python` or plain python3+urllib (browser UA): fetch /node/1752049047 and /node/4636304129 (the mouth node pair); Nominatim (project UA, pipeline/aw.py `UA`) for "Tennessee State Capitol" (featuretype=building) and keep the west-Cumberland Nominatim centroid (36.171,-86.899) as a check point.
3. Verify the two unconfirmed map pixels with grid-overlay crops (the recipe + crop coords are above): the SW-town corner (~ (3980,3850)) and the Rich-Branch mouth 2x zoom (6000-6500, 3900-4150).
4. Solve the Haydon similarity (3 anchors), checks (a)-(c) in DECISION step 2; then the Clayton 2-anchor projection; verdict; cross-checks; record.
5. Apply (step 8). If the context gets tight: record the georef + mouth + projected corners in the hand-over and DECISIONS first, apply in the following session.

### PITFALLS to file (163, not yet filed - context limit)
- (a) OSM REST: `/api/0.6/{relation,way,way/full,node}/{id}` are LIVE from this machine (browser UA); only `/map?bbox=` is 410-dead (retest per call; 161's "/way/{id}/full 410" is NOT durable); Nominatim geojson returns centroid Points only for big waterways here -> use relation IDs + the API, not polylines.
- (b) Overpass from this VM is dead on all three public instances: overpass-api.de **406** (new), maps.mail.ru 504, kumi XHTML. Do not retry.
- (c) Nominatim `featuretype=waterway` + `viewbox=min_lon,MAX_lat,max_lon,min_lat` + `bounded=1` is the right way to test whether a named waterway exists in a region (Rich Branch: 0 near Nashville, hits only 4 states away).
- (d) LOC maps search API: `https://www.loc.gov/maps/?q=...&fo=json&fa=original-format:map&dates=YYYY/YYYY` (browser UA; results may be a bare list); the 1903 Nashville USGS quad is NOT in the LOC digitized maps (9 hits 1900-1910, none USGS).
- (e) USGS hosts: hdwds.usgs.gov + edits.usgs.gov unreachable (000); geonames.usgs.gov 301-dead; www.usgs.gov 403; waterdata.usgs.gov (NWIS) live.
- (f) (from 161, still unfiled) PIL's 178 M-px limit -> Image.MAX_IMAGE_PIXELS = None.
- (g) (from 161, still unfiled) process fact: a hand-over header that claims details are "below" but the body was never rewritten loses them forever - write details before the header, or not at all.

### [161] site-point research (superseded where 163 conflicts; the Clayton pixel anchors and the apply recipe are still the ones to use)

(2026-10-14, iteration 161, agent a - site-point research, CONTINUED. **Important correction to the 160 header:** its "pixel anchors measured, below" and "BBBike recipe below" were NEVER written - the body of the previous hand-over is the 155-era text; 160's details are lost. This session re-did the Clayton measurement from scratch (numbers below) and re-established the OSM data route (OSM REST API is now DEAD - 410 - geofabrik pbf works). No repo file changed this session; baseline tests 7/7 green (test_src_us_cities + test_region) and staged files still 3/11/11 as at 155/160. Everything measured is recorded here so the next session does not re-read images.)

### Clayton 1804 - full-res pixel anchors (measured 161 on the 2557x1913 original)
- **Fort square** ("D Cross's owner / [f]ormer Stone House / [f]or[mer] Fort", small hatched square at the town's SW corner on the river): center **~(718, 1345)**. = Fort Nashborough = Q5471739, P625 (36.164167, -86.774444) (Wikidata/OSEM/Wikipedia all agree; 217 m N of the city P625).
- **Rich Branch confluence** (the right-hand river's mouth into the hatched "Cumberland River" band, SE corner of the drawing): **~(2282, 1597)** (the V where the branch line meets the band; the band then runs on to the bottom-right).
- **Cemetery** (box with a cross, NE of the town, west of the Rich Branch): **~(2045, 970)**.
- **McNairy's spring** (well symbol, above the Cemetery): **~(2095, 865)**.
- **Sulphur Spring** (well symbol, "Salt made of it", NE of the Rich Branch): **~(2150, 1160)**; its label text runs east to ~x=2420.
- **Walker house** ("WTate Occupant / now 1834 Walkers / 2 Story Frame / Best House in town", "now Capitol Hill" label to its right): **~(1125, 997)**.
- **Dr Henning's House & Office** (1 story frame, SE of the town): **~(1615, 1350)** (area x 1480-1750, y 1310-1390).
- **Market or Main St row** (houses 13,12,11,10,9 + 3): x 1080-1360, y 1320-1380 (just above the top edge of the river band).
- **Johnson's House, Ferry & Keel Boat Landing** (two hatched buildings at the river's western end): **~(580, 1550)** (area x 555-610, y 1520-1580).
- **River band**: hatched Cumberland runs along the bottom; it enters the sheet's LEFT edge at ~(18, 1625) and exits the bottom edge in the SW corner. The Tennessee River is NOT drawn (it joins the Cumberland off-sheet, SW of the drawing).
- **Drawn content** (excluding the REFERENCES list at top, y<~440, and the two title lines "NASHVILLE IN 1804." ~(1169-1571, 1634-1671) and "From Notes &c. of Mrs. Temple, daughter of Dunc. Robertson." ~(822-1826, 1744-1781)): north edge = the row of trees just below REFERENCES at y~480-530 (Judge McNairy's house ~(2100-2136, 648-667) sits under it); south edge = the river band (bottom of the hatching ~y 1700-1740 mid-sheet, the SW corner filling to the sheet edge); west edge = the sheet's left edge (x~18); east edge = the Sulphur Spring label end (~x 2420) / the sheet border x~2520.
- **The town extent** (the built-up area, per the 147/148 SF "center of the drawn extent" precedent - not the open NE ground): W/SW = the ferry (~580,1550) and the fort (~718,1345); S = the river band below the Market row (y~1420-1450 there); E = the small hatched houses "1 2" ~(1440-1510, 1180-1240) and Dr Henning's (~1615,1350) - the Cedar St / College Str edge; N = the Walker-house row (y~950-1000). The Cemetery + McNairy + Sulphur Spring are open ground beyond that.

### OSM river data - the dead and the live routes (verified 161)
- **api.openstreetmap.org is DEAD**: BOTH `/map?bbox=...` AND `/way/{id}/full` now return **410 Gone** (tested even 155's known-good way 40806685 - gone). openstreetmap.de `/map` -> 404. So 155's "use api.openstreetmap.org instead" is a dead end now; 160 evidently hit this and moved to an extract. Overpass was already dead (155/160, PITFALLS has the 504 entry).
- **Nominatim WORKS** (the usual project UA, 1 r/s): but "Rich Branch" (bounded to the Nashville viewbox) returns NOTHING, and "Cumberland River" returns the Greenway park/cycleway, not the river. Nominatim is not the route for the confluence.
- **Geofabrik works**: `https://download.geofabrik.de/north-america/us/tennessee-latest.osm.pbf` = **181 MB, downloaded fine** (161: 190,643,543 bytes; 160's 147 MB was presumably the BBBike variant of the same extract - the BBBike recipe is lost, use geofabrik). `/tmp` is gone: **re-download it**. (The "-latest" file is a live snapshot; fine for research, it is not a project dependency.)
- **Parsing the pbf**: apt `osmium-tool` is 1.16 (too old: no pbf export/--filter); `pyosmium` is NOT on PyPI; `protobuf` 7.36.2 pure-python IS (throwaway venv at /tmp/us161/v in 161 - recreate it). The format spec (fetched 161, full text was in the harness web cache /home/agent/.cache/pi-web/5a61080bee349ad3.txt - may be gone; the essentials are here): classic osmpbf, **BlobHeader{type,indexdata,datasize} / Blob{raw,raw_size,zlib_data} / OSMData block = zlib(PrimitiveBlock{StringTable{repeated string s}, repeated PrimitiveGroup, granularity int32=17 (default 100 nanodeg), lat_offset int64=19, lon_offset int64=20, date_granularity int32=18})**; PrimitiveGroup{repeated Node=1, optional DenseNodes=2, repeated Way=3, repeated Relation=4}; Node{id sint64=1, keys/vals packed uint32=2/3 (string-table indices), lat sint64=8, lon sint64=9}; DenseNodes{id delta-packed sint64=1, DenseInfo=5, lat/lon delta-packed=8/9, keys_vals packed uint32=10: per node <keyid> <valsid> pairs, 0 = end-of-node delimiter}; **Way{id uint64=1, keys packed=2, vals packed=3, Info=4, refs delta-packed sint64=8}** - each Way message is self-contained (my 161 parser draft in /tmp/us161/pbf_rivers.py assumed a WRONG "key/type group" layout - delete it, rewrite against this spec; /tmp is gone anyway). **lat/lon = 1e-9 * (offset + granularity * encoded value)** (delta-decode first, standard zigzag varint). Only need: nodes in an expanded box around downtown (lat 36.11-36.21, lon -86.85..-86.72) + every way whose tags include name AND (waterway or natural); then reconstruct the Cumberland River / Tennessee River / Rich Branch centerlines and find (a) the Rich Branch->Cumberland confluence and (b) the Tennessee->Cumberland confluence (nearest point between centerlines / shared endpoints).
- **161's sweep script** (/tmp/us161/osm_sweep.py, gone) used api.openstreetmap.org - dead; do not resurrect it.

### The decision (unchanged from 155, now with measured anchors)
1. Get the two confluence points from the pbf (above). Anchor A = fort pixel (718,1345) -> (36.164167,-86.774444); Anchor B = confluence pixel (2282,1597) -> the OSM point. 2-anchor similarity (scale+rotation+translation) in ENU metres (E=(lon-lon0)*111194.93*cos(lat0), N=(lat-lat0)*110900; origin = the fort); project every pixel anchor listed above; also project the town-extent corners (ferry / Market-row river edge / Walker row / the "1 2" houses) and the full-ink corners.
2. **VERDICT rule (155 step 1e, the 147/148 SF precedent):** point = **P625 (-86.774444, 36.162222)** if the 2000 m town box centered on it (hw 1000 m: lat +/-0.0090, lon +/-0.0113) covers the projected town extent WITH margin; else point = **center of the projected town extent** (record it to 5 decimals, like the SF midpoint). Both candidates keep every P625 <50 km away (no --verify flag) and the evidence tie stores the table point (dist_m 0.0), so --verify/--check stay offline-safe either way.
3. **Cross-checks before the verdict:** (a) Haydon 1860 (10000x6082, to-scale, scale bar in the sheet - re-download, URL below): find the 1804 old-grid core (the dense grid WEST of the Rich Branch, around the fort corner) and its metre extent via the scale bar; should agree with the Clayton projection to a couple hundred m. (b) Nominatim (works, 1 r/s) for 2-3 of the projected features (e.g. the Walker house vs the modern Capitol Hill / Cumberland Museum / Parthenon area, the ferry vs 5th Ave S / the river) - sanity, not the decider.
4. Record the point + why in DECISIONS, then **apply exactly as the 155-era steps 2-6 below** (they are still the right recipe; the only open input was this point).

### Map re-download URLs (verified live 161)
- Clayton: https://upload.wikimedia.org/wikipedia/commons/0/0c/1804_Map_of_Nashville_published_1880.jpg (2557x1913)
- Haydon: https://upload.wikimedia.org/wikipedia/commons/d/da/1860_Haydon_map_of_City_of_Nashville_and_Edgefield.jpg (10000x6082, 10.4 MB)
- Tennessee pbf: https://download.geofabrik.de/north-america/us/tennessee-latest.osm.pbf (181 MB)
- PIL lives in the PROJECT .venv; for >178 M-px images set Image.MAX_IMAGE_PIXELS = None (both maps are under the limit; Haydon is 60.8 Mpx fine).

### The 155-era apply recipe (steps 2-6, still valid once the point is settled)
2. fit/src_us_cities.py: docstring += Nashville (replace "Nashville follows in a later session"); SITES += Q23197 (id "nashville-q23197", name "Nashville", named "Nashville", kind "town", region "United States", place "Davidson County, Tennessee", wikipedia https://en.wikipedia.org/wiki/Nashville,_Tennessee, point = the verdict, note like the others' aerial note + the oversize-sheet review-item note: the Haydon/Poe/Defenses sheets span the city and its fort ring far beyond the 2 km box -> likely review items, the NY 1811 / DC 1865 ring precedents; no extent field - the extras row has none, pipeline/catalog.py:686 sets extent_m from the site box); SOURCES += clayton_1804 (dict(date="1804") - page "1880" = Clayton book publication), haydon_1860 (no swap - page "1860" = drawing date), poe (NO swap - page "1860s" = the LOC-verified drawing date; row date "1860s", no date_commons), defenses (dict(date="1895") - page date empty, so date_commons ""), all p="plan". Exact file titles (case-sensitive; the "..." in the Defenses title is literal): `File:1804 Map of Nashville published 1880.jpg`; `File:1860 Haydon map of City of Nashville and Edgefield.jpg`; `File:Map of Nashville, Tennessee. LOC 2003630459.jpg`; `File:Defenses of Chattanooga, Tenn. Battery Erwin ... Battery Coolidge. Defenses of Nashville, Tenn. Capitol (IA dr defenses-of-chattanooga-tenn-battery-erwin-battery-coolidge-defenses-01104241).jpg`.
3. Run: live --verify (4 QIDs, expect no flag, no trap) + live stage (expect "1 new sites, 4 new pictures; build (236c): nashville-q23197") + offline --check (expect 15 rows, 15 pass) + --golden (4 extras / 15 files / 15 classified). Live under .venv/bin/python; --check plain python3 works too.
4. Tests: tests/test_src_us_cities.py - row asserts 11->15, PASS-line list += 4, qid-table set += Q23197 (+ the point asserts, incl. the decision), extras ids += nashville-q23197, years dict += the 4 titles (1804, 1860, 1860, 1895 - the Clayton and Defenses swaps give the known years, NOT the page values: the Clayton row's date_commons is "1880", the Defenses row's date_commons is ""/absent, the Poe row keeps date "1860s", the Haydon row date "1860"), named_by_qid += {Q23197: "Nashville"}; then `.venv/bin/python -m pytest tests/test_src_us_cities.py tests/test_region.py -q` (expect 7/7; the full-suite caveat stands: agent c's test_fit_queue failure + the 306 work on main).
5. Lead doc: docs/lead_us_cities.md += `## Nashville (Q23197)` (site point + decision with the pixel anchors above and the OSM confluence points; per-candidate STAGED/DROP with exact titles + reasons incl. the 152 date verdicts; the Fort Negley record; the 15-PASS transcript). Header: "four cities staged; box 3 done".
6. Done: tick box 3, set Status: done, commit as 236a.

### STAGED verdicts (4 rows, all print "Nashville" in the title - gate-safe; all Public domain) - from 151/152, unchanged
1. `File:1804 Map of Nashville published 1880.jpg` (2557x1913, page date "1880") = the 1804 map from the notes of Mrs. Temple, daughter of Dunc. Robertson, as engraved in W. W. Clayton's "History of Davidson County, Tennessee" (1880). THE early town plan. **Known-date swap dict(date="1804")** (page date 1880 = the book's publication, not the drawing).
2. `File:1860 Haydon map of City of Nashville and Edgefield.jpg` (10000x6082, page date "1860", John Haydon and Booth) = the 1860 plan of the city and Edgefield (street grid, wards, railroads, all buildings, 19 vignettes). No swap. Oversize sheet -> review-item note.
3. `File:Map of Nashville, Tennessee. LOC 2003630459.jpg` (19690x11294, page date "1860s" precision 8, Poe/Chief Engrs Office) = the O.M. Poe pen-and-ink-on-cloth survey map of the whole city (buildings, contours, the Cumberland, railroads). **NO swap** (152: the LOC item says "[186-]"; the signature's "(17x29.)" is the sheet size, not a year - 151's "1864" thumbnail read was wrong; page "1860s" IS the LOC drawing date). Oversize sheet -> review-item note.
4. `File:Defenses of Chattanooga, Tenn. Battery Erwin ... Battery Coolidge. Defenses of Nashville, Tenn. Capitol (IA dr defenses-of-chattanooga-tenn-battery-erwin-battery-coolidge-defenses-01104241).jpg` (1536x886, NO page date, artists incl. the War Department / Julius Bien & Co.) = PLATE C-X- (CXIII or CXVIII at that resolution) of the "ATLAS TO ACCOMPANY THE OFFICIAL HISTORIES OF THE UNION AND CONFEDERATE ARMIES 1861-1865" (the plate's own header; 151's "UNITED STATES" was a misread): nine panels, 7 of 9 Nashville incl. **Fort Negley** (plan + section A-B + magazine), surveyed Nov 30 - Dec 1864. Staged on the CITY (the DC 1865 ring precedent). **Known-date swap dict(date="1895")** (152: the scan comes from the David Rumsey group 1780.000/image 1780.113, cataloged 1895 "Julius Bien & Co., Lith., N.Y. (1891-1895)" per the surviving IA sibling item + AbeBooks + the Rumsey listing; first edition 1884-85 per the plate header but NOT online-verifiable from this machine - the blocked routes are in the 152 DECISIONS entry). 1895 is outside the 1660-1880 window by 15 years - acceptable: Civil War fortification plan = a drawing per the task Notes (the DC 1865 ring precedent). The title has NO PLANWORD, so keep() passes only via the swap.

### DROP verdicts (record these exact reasons in the lead doc) - from 151, unchanged
- `File:Map of Nashville in 1804 created by James Burns from notes of Mrs. Temple daughter of Dunc. Robertson.jpg` (1018x704, 1906-09-01) = the SAME 1804 plan as the staged Clayton file (later, smaller copy) - one row per plan.
- `File:Detail of map of Nashville Tennessee in 1854.jpg` (1752x1168, 1854) = a cropped book detail - too small.
- `File:1888 Sanborn Map of the Eighth Avenue South Reservoir in Nashville TN.jpg` (491x572, 1888) = a fragment, too small.
- `File:New map of Nashville, Tennessee. LOC 75695990.tif` (10218x6688, 1916) = outside the 1660-1880 window.
- `File:Map of the battle of Nashville, dec. 15th & 16th 1864 LOC 99447244.jpg` and `.tif` (2550x2117, 1887, 1:110,000) = a small-scale BATTLE map, outside the window, not a city/fortification plan.
- `File:Civil war battlefield maps - nashville and franklin 1895.jpg` (10056x6183, 1895) = a battlefield map, outside the window (look at it once via its Commons page before dropping, expect DROP).
- `File:Fort negley 1864.jpg` (800x600, undated, Barnard photo) and the other Negley photos (the two 1864/1890 photos, `File:Negley Ruins.jpg` 2019, `File:Fort Negley Park outside Nashville, TN.jpg` modern) = **photos, not plans**.

### 236b leads (do NOT stage here - bird's-eye views) - the three 1864 Fletcher lithograph VIEWS of Fort Negley
- `File:South west view of Fort Negley LCCN2003655690.jpg` (7950x3822) and `.tif` (7964x4356); `File:North west view of Fort Negley LCCN2003655670.tif` (7964x4356); `File:South east view of Fort Negley LCCN2003655689.jpg` (8082x3978). All Public domain, date "1864" (the SE one inscribed "Filed Dec 31, 1864"), "Fort Negley" in the title - gate-safe for 236b.

### Verified QID facts (151, via pipeline/catalog_wd; its disk cache in data/raw/catalog/wd/ keeps re-runs free)
- **Q23197 (Nashville):** label "Nashville", ONE P625 (-86.774444, 36.162222), P373 ['Nashville, Tennessee'], P131 [('Davidson County','Q1177705')], enwiki 'Nashville, Tennessee', first name-search hit with P625 = Q23197 itself (no trap). NOT in the catalog (no collision with any site; the only canonical "Nashville" hit is the unrelated "Nashville I" gorget at castalian-springs-mound-site-q5049584).
- **Q5471739 (Fort Nashborough):** "former stockade in Nashville, Tennessee", P625 (36.164167, -86.774444) precision 0.001; enwiki infobox same coords, "a replica stands along First Avenue North, several hundred meters from the original site"; OSM way 130910783 (historic=fort) same spot. = the Clayton "former Fort" anchor.
- **Q5471744 (Fort Negley):** P625 (-86.774658, 36.145097) (~1.9 km S of the city P625), P131 Nashville, enwiki Fort Negley, no trap, NOT in the catalog. **NO Fort Negley fort site is staged** (no fort-only plan on Commons - photos and the 3 Fletcher views only); if a fort-only Negley plan appears later, Q5471744 with the 1600 m fort box (the DC forts precedent) is the candidate.

### Gotchas (all still true)
- Tests OFFLINE only (socket-blocked fixture in the test file); run ONLY tests/test_src_us_cities.py + tests/test_region.py - never the full suite (agent c's test_fit_queue failure + the 306 work). Live commands under .venv/bin/python (module top stays stdlib-only; commons -> aw needs numpy).
- Named-place gate: title + the 600-char-truncated desc of c.info(); all four Nashville candidates print "Nashville" in the TITLE (gate-safe). File titles are case-sensitive.
- stage() is idempotent on (site, title); a missing title fails loud. To change a STAGED row's note later: hand-edit the jsonl row, keep SITES in lockstep, re-run --golden.
- Town box: kind "town" -> 2000 m -> a 2 km x 2 km box centered on the point (hw = width_m/2). No box_m override (specs/site_boxes.json not in Touches).
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, sites.json) - that is 236c. The REGION_NAME line in pipeline/build_catalog.py is already committed.
- Do not "fix" pipeline/commons.py's NO regex (not in Touches).
- /tmp/us161/* (both map downloads, the pbf, the throwaway venv, all scripts) are session-scoped and GONE after this session - re-download from the URLs above. The pbf is the slowest (181 MB).
- **PITFALLS to file when convenient (161):** (a) PIL's 178 M-px decompression-bomb limit -> Image.MAX_IMAGE_PIXELS = None (candidate since 152, never filed); (b) the OSM REST API (api.openstreetmap.org /map AND /way/{id}/full) is DEAD from this machine - 410 Gone on everything - Overpass and openstreetmap.de dead too; use Nominatim (works) or a geofabrik/bbbike pbf extract (works) for river geometry; (c) process fact: a hand-over header that claims details are "below" but the body was never rewritten loses them forever - write the details before the header, or not at all.

### [161] SUPERSEDED 155-era body - kept for reference only; every 161 section above supersedes it (the full research history is in the 150/151/152 DECISIONS entries)

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

### EXACT next steps: 155-era - SUPERSEDED by the 161 "The decision" section above (do not follow these steps 1-6; follow that section instead)
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
