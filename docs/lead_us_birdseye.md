# Bird's-eye and panoramic views of US cities (task 236b)

GOAL.md point 5 (the 2026-10-13 owner change): the map grows with US cities, and artists' aerial and
bird's-eye views count as much as surveys. The source is the **Library of Congress "Panoramic Maps"
collection** (loc.gov/collections/panoramic-maps): about 1,500 US bird's-eye views, 1847-1929
(LOC's own collection statement; this machine cannot reach loc.gov, see below), public domain - each
staged file below is individually marked **"Public domain"** in its Commons metadata (verified live
at staging, the `license` field on every staged row). Town plans and views are exempt from the
150-year rule; the 1921 Olsen view (the newest staged) is the collection's near-edge of the 1847-1929
range and passes `commons.keep()` on its own date.

## Fetch route (verified before use)

- **loc.gov is unreachable from this machine**: `GET https://www.loc.gov/collections/panoramic-maps/`
  returns **403 Forbidden** (CloudFront bot block; both the plain web fetch and a urllib request with
  the project user-agent - the same wall as other bot-gated CDNs, recorded in `PITFALLS.md`). A
  Wayback Machine snapshot of the collection page (2025-01-02) renders the item list (per-item Date,
  Contributor = artist/publisher, the Phillips "LC Panoramic maps (2nd ed.)" numbers) but its extracted
  text carries no description block, so the collection's size/range stand on GOAL.md's statement, and
  the licence on the per-file Commons metadata (all staged files: Public domain - above).
- **The files are fetched from their Wikimedia Commons mirrors only** (the project's established
  pattern - 236a, src_artists, kip all fetch via Commons `extmetadata`): many LOC Panoramic Maps items
  are mirrored on Commons with the LOC id in the title ("LOC 75694818", "LCCN2009633685", "ppmsca.03354").
  `pipeline/commons.py info()` pulls `url|size|mime|extmetadata` (date, description, artist, license)
  per file; the stage re-verifies every title live and fails loud on drift.
- **Commons organization (verified live 2026-10-14):** New York = Category "Bird's eye view maps of
  New York City" (145 members; the files live in decade subcategories, `members(cat,'file')` alone
  gives only ~12 - the walk must descend); Washington DC = Category "Bird's eye view maps of
  Washington, D.C." (175 members, all direct files, no subcats); San Francisco and Nashville have no
  bird's-eye category at all (only photo-dominated "Views of ..." subcats) - the file-namespace
  full-text search ("bird's-eye view of San Francisco" and the like) is the route there. The candidate
  pool for the four cities is ~383 unique titles, of which 95 (NYC), 10 (DC), 56 (SF) and 5 (Nashville)
  pass `commons.keep()` plus the caption gate.

## The four owner-named cities: shared site ids (agreed with 236a)

The four owner-named cities are already staged by 236a as sites in `data/catalog/extras_us_cities.jsonl`
(its own staging file, **read-only** for this task). This task's file rows use **236a's site ids as-is**
- the catalog slug rule (slug + "-" + qid-lower) was already applied by 236a, so no second site is
created for any QID (never two sites for one QID). The shared ids, recorded here as the agreement:

| QID | site id (from 236a's staged row) | short caption name |
|---|---|---|
| Q60 | `new-york-q60` | New York |
| Q61 | `washington-q61` | Washington |
| Q62 | `san-francisco-q62` | San Francisco |
| Q23197 | `nashville-q23197` | Nashville |

`fit/src_us_birdseye.py:SHARED_SITES` hard-codes this table and **cross-checks it against 236a's file
on every run** (`_shared_site`): a missing 236a row, or 236a's row under a different id, fails the
stage loud (236c rebuilding a site under another id must not silently split one city into two). The
shared cities get **no** row in this task's `data/catalog/extras_us_birdseye.jsonl` (that file is only
for cities 236a does not stage - checked against `extras_us_cities.jsonl` on main before any city is
added). `known_sites()` here reads 236a's file too, so this task's `--check` treats the four ids as
existing sites (a file row naming one passes the "neither staged nor existing" guard).

The city site points and their derivation are 236a's and stand as-is (docs/lead_us_cities.md):
New York `-74.006111, 40.712778` (the P625 itself, Financial District / City Hall), Washington
`-77.036667, 38.895` (the P625, the old L'Enfant core), San Francisco `-122.40289, 37.79213` (the
midpoint of the old town's drawn peninsula, NOT a P625), Nashville `-86.78152, 36.16529` (the center
of the projected 1804 Clayton extent, NOT the P625). All four are **aerial-photograph ground**
(`aerial_ok: true` on 236a's rows; no open LiDAR over a built-up city - bare-earth LiDAR erases the
streets). Every staged view is oblique to near-vertical; the apparent angle is recorded on the module
source comments and here, so 236c/the matcher can order them (near-vertical fits best). The 2000 m
town box covers a whole-island/whole-city sheet only for a small subset: the NYC 1907 metro sheet and
the DC 1921/1883/1886 sheets span far beyond it, so their fits are likely to end **review items**
(the 236a NY-1811 / DC-ring precedent) - recorded on 236a's site notes.

## QID verification (re-checked 2026-10-14, `.venv/bin/python fit/src_us_birdseye.py --verify`)

The four shared QIDs were first verified by 236a (docs/lead_us_cities.md, 2026-10-13/14); the ten
new-city QIDs were verified when their cities were added. This is 236b's re-check (at the batch-2
close-out) that its own table stands on: label, every P625 value (flagged when >50 km from the
table point), P373, P131 (with labels), the enwiki article, and the first name-search hit with
coordinates (what `record --live` would resolve for the caption route). No P625 flag fired on any
of the fourteen (Q62's two P625s are 2.0-2.4 km from its refined table point - the point is a
refinement, not a P625; Q23197's is 721 m SE; the ten new-city points ARE the P625s, dist 0). Two
search traps (the Barnard-Castle class, the 236a Q60 note): **Pittsburgh** -> Q235034 University
of Pittsburgh (~4.0 km east of the city point) and **Chicago** -> Q131252 University of Chicago
(~10.5 km south) - both within the 50 km flag, so the run does not flag them, but `record --live`
would store the university's point instead of the city's; the staged rows hand-record the city's
P625 (dist 0), and both traps are recorded on the Q1342/Q1297 SITES comments and site notes.
Baltimore's P131 carries two values (Maryland and the historic Province of Maryland): the city is
no county of its own, so its place is written "Baltimore City, Maryland" from P373 + the state.
St. Louis's P131 carries **only Missouri** (an independent city, no county of its own), hence
"St. Louis City, Missouri". Milwaukee's P131 carries **three counties** (Milwaukee / Washington /
Waukesha - the city point sits in Milwaukee County). The transcript (14 QIDs, sorted, verbatim):

```
checked 2026-10-14 - 14 QIDs (Wikidata)
  Q100  'Boston'  (site id: boston-q100, new (this task))
      P625: [(-71.05777777777777, 42.360277777777775)]  (table site point: -71.057778, 42.360278)
      P373: ['Boston']
      P131: [('Suffolk County', 'Q54072')]  (table place: 'Suffolk County, Massachusetts')
      enwiki: 'Boston'  (table wikipedia: 'https://en.wikipedia.org/wiki/Boston')
      search 'Boston': first hit with P625 is Q100 'Boston' (-71.05777777777777, 42.360277777777775)
  Q12439  'Detroit'  (site id: detroit-q12439, new (this task))
      P625: [(-83.0475, 42.331666666667)]  (table site point: -83.0475, 42.331667)
      P373: ['Detroit']
      P131: [('Wayne County', 'Q195664')]  (table place: 'Wayne County, Michigan')
      enwiki: 'Detroit'  (table wikipedia: 'https://en.wikipedia.org/wiki/Detroit')
      search 'Detroit': first hit with P625 is Q12439 'Detroit' (-83.0475, 42.331666666667)
  Q1297  'Chicago'  (site id: chicago-q1297, new (this task))
      P625: [(-87.62777777777778, 41.88194444444444)]  (table site point: -87.627778, 41.881944)
      P373: ['Chicago']
      P131: [('Cook County', 'Q108418')]  (table place: 'Cook County, Illinois')
      enwiki: 'Chicago'  (table wikipedia: 'https://en.wikipedia.org/wiki/Chicago')
      search 'Chicago': first hit with P625 is Q131252 'University of Chicago' (-87.599722222222, 41.789722222222)
  Q1342  'Pittsburgh'  (site id: pittsburgh-q1342, new (this task))
      P625: [(-80, 40.44166666666667)]  (table site point: -80.0, 40.441667)
      P373: ['Pittsburgh']
      P131: [('Allegheny County', 'Q156291')]  (table place: 'Allegheny County, Pennsylvania')
      enwiki: 'Pittsburgh'  (table wikipedia: 'https://en.wikipedia.org/wiki/Pittsburgh')
      search 'Pittsburgh': first hit with P625 is Q235034 'University of Pittsburgh' (-79.953274, 40.444565)
  Q1345  'Philadelphia'  (site id: philadelphia-q1345, new (this task))
      P625: [(-75.163611111111, 39.952777777778)]  (table site point: -75.163611, 39.952778)
      P373: ['Philadelphia']
      P131: [('Philadelphia County', 'Q496900')]  (table place: 'Philadelphia County, Pennsylvania')
      enwiki: 'Philadelphia'  (table wikipedia: 'https://en.wikipedia.org/wiki/Philadelphia')
      search 'Philadelphia': first hit with P625 is Q1345 'Philadelphia' (-75.163611111111, 39.952777777778)
  Q23197  'Nashville'  (site id: nashville-q23197, shared (236a))
      P625: [(-86.77444444444444, 36.16222222222222)]  (table site point: -86.78152, 36.16529)
      P373: ['Nashville, Tennessee']
      P131: [('Davidson County', 'Q1177705')]  (table place: 'Davidson County, Tennessee')
      enwiki: 'Nashville, Tennessee'  (table wikipedia: 'https://en.wikipedia.org/wiki/Nashville,_Tennessee')
      search 'Nashville': first hit with P625 is Q23197 'Nashville' (-86.77444444444444, 36.16222222222222)
  Q37836  'Milwaukee'  (site id: milwaukee-q37836, new (this task))
      P625: [(-87.95, 43.05)]  (table site point: -87.95, 43.05)
      P373: ['Milwaukee, Wisconsin']
      P131: [('Milwaukee County', 'Q502294'), ('Washington County', 'Q501559'), ('Waukesha County', 'Q370654')]  (table place: 'Milwaukee County, Wisconsin')
      enwiki: 'Milwaukee'  (table wikipedia: 'https://en.wikipedia.org/wiki/Milwaukee')
      search 'Milwaukee': first hit with P625 is Q37836 'Milwaukee' (-87.95, 43.05)
  Q38022  'St. Louis'  (site id: st-louis-q38022, new (this task))
      P625: [(-90.19944444444444, 38.62638888888889)]  (table site point: -90.199444, 38.626389)
      P373: ['St. Louis, Missouri']
      P131: [('Missouri', 'Q1581')]  (table place: 'St. Louis City, Missouri')
      enwiki: 'St. Louis'  (table wikipedia: 'https://en.wikipedia.org/wiki/St._Louis')
      search 'St. Louis': first hit with P625 is Q38022 'St. Louis' (-90.19944444444444, 38.62638888888889)
  Q43196  'Cincinnati'  (site id: cincinnati-q43196, new (this task))
      P625: [(-84.5125, 39.1)]  (table site point: -84.5125, 39.1)
      P373: ['Cincinnati, Ohio']
      P131: [('Hamilton County', 'Q152891')]  (table place: 'Hamilton County, Ohio')
      enwiki: 'Cincinnati'  (table wikipedia: 'https://en.wikipedia.org/wiki/Cincinnati')
      search 'Cincinnati': first hit with P625 is Q43196 'Cincinnati' (-84.5125, 39.1)
  Q43668  'Louisville'  (site id: louisville-q43668, new (this task))
      P625: [(-85.75138888888888, 38.25611111111111)]  (table site point: -85.751389, 38.256111)
      P373: ['Louisville, Kentucky']
      P131: [('Jefferson County', 'Q500776')]  (table place: 'Jefferson County, Kentucky')
      enwiki: 'Louisville, Kentucky'  (table wikipedia: 'https://en.wikipedia.org/wiki/Louisville,_Kentucky')
      search 'Louisville': first hit with P625 is Q43668 'Louisville' (-85.75138888888888, 38.25611111111111)
  Q5092  'Baltimore'  (site id: baltimore-q5092, new (this task))
      P625: [(-76.615, 39.286388888889)]  (table site point: -76.615, 39.286389)
      P373: ['Baltimore']
      P131: [('Maryland', 'Q1391'), ('Province of Maryland', 'Q2452027')]  (table place: 'Baltimore City, Maryland')
      enwiki: 'Baltimore'  (table wikipedia: 'https://en.wikipedia.org/wiki/Baltimore')
      search 'Baltimore': first hit with P625 is Q5092 'Baltimore' (-76.615, 39.286388888889)
  Q60  'New York City'  (site id: new-york-q60, shared (236a))
      P625: [(-74.00611111111111, 40.71277777777778)]  (table site point: -74.006111, 40.712778)
      P373: ['New York City']
      P131: [('New York', 'Q1384')]  (table place: 'New York County, New York')
      enwiki: 'New York City'  (table wikipedia: 'https://en.wikipedia.org/wiki/New_York_City')
      search 'New York City': first hit with P625 is Q60 'New York City' (-74.00611111111111, 40.71277777777778)
  Q61  'Washington, D.C.'  (site id: washington-q61, shared (236a))
      P625: [(-77.036666666667, 38.895)]  (table site point: -77.036667, 38.895)
      P373: ['Washington, D.C.']
      P131: [('District of Columbia', 'Q3551781')]  (table place: 'District of Columbia')
      enwiki: 'Washington, D.C.'  (table wikipedia: 'https://en.wikipedia.org/wiki/Washington,_D.C.')
      search 'Washington, D.C.': first hit with P625 is Q61 'Washington, D.C.' (-77.036666666667, 38.895)
  Q62  'San Francisco'  (site id: san-francisco-q62, shared (236a))
      P625: [(-122.41944444444445, 37.775), (-122.41638888888889, 37.7775)]  (table site point: -122.40289, 37.79213)
      P373: ['San Francisco']
      P131: [('San Francisco County', 'Q13188841'), ('California', 'Q99')]  (table place: 'San Francisco County, California')
      enwiki: 'San Francisco'  (table wikipedia: 'https://en.wikipedia.org/wiki/San_Francisco')
      search 'San Francisco': first hit with P625 is Q62 'San Francisco' (-122.41944444444445, 37.775)
```

## The evidence field (as in 236a)

Every staged row carries a hand-recorded `caption_coords` tie in the exact key order of
`fit/evidence.py:caption_route`: the caption names the city (the short caption name appears in the
file title or its description within the 600-char gate window) and the stored coordinates are the
verified site point itself (dist 0). `fit/evidence.py check` passes offline from the stored fields,
and the module's `--check` re-runs it. `record --live` would instead take the first name-search hit
- which is why every QID is re-verified above, and why the stage **fails loud** when a file caption
does not print the city (`fit/src_us_birdseye.py:evidence_for`). A scan whose file page lost the
drawing's date (or printed only its copyright year) gets the known drawing/publication date on the
row and the page value kept as `date_commons` (the Zwolle precedent; `sources.py` and
`src_van_deventer.py` swap before the `keep()` gate, so the drawing's year - not a 21st-century
upload - is what `keep()` judges).

## New York (site `new-york-q60`, 236a's point; 3 views staged)

**STAGED** (one row per sheet; dupes dropped, the Ratzer precedent):

- `File:New York - drawn by J. Bachmann ; print by G. Schlegel, 97 William St. N.Y. LCCN98508526.jpg`
  - 1874, drawn by J. Bachmann, printed by G. Schlegel, 10078x6950, Public domain. The classic
  near-vertical harbour view of Manhattan from the north-east, "NEW YORK" printed on the sheet.
- `File:The city of New York. LOC 75694818.jpg` - 1879, Will L. Taylor, published by Galt & Hoy,
  12901x22870, Public domain. The whole island in portrait with the full street grid, plus a run of
  advertiser vignettes at the top and a "REFERENCE" list down the right. **`File:Taylor map of New
  York.jpg` (12901x22870, the DPLA scan) is the SAME sheet** (same vignettes, grid, banner, fold
  lines - eyeballed 2026-10-14): one row per sheet, the LOC scan is staged.
- `File:View of the city of New York and vicinity LOC 78692903.jpg` - 1907, August R. Ohman /
  August R. Ohman & Co., 12720x9136, Public domain. **Metro-wide** (Manhattan, the Bronx, Brooklyn,
  Jersey City) - the sheet spans far beyond the 2000 m town box, so its fit is likely to end a
  review item (the 236a 1811-sheet precedent).

**RESERVED for a later batch** (passers, not needed for the four-cities box): the 1849 Bachmann
Sarony & Major view (9371x6705), the 1854 NYPL harbour panorama (6872x5414), the 1855 Cheltnam view
(7230x5428, CC0), the Currier & Ives views LOC 75694809 (1870), 75694810 (1876), 75694807 (1877) and
the PGA 1877 edition, the C&I views LOC 75694812/22/23/25 (1883-1892, 11-12k px), the 1897
23rd/24th-wards sheet (22240x6176), the 1911 Wellge view (6740x2750, CC0) and the 1912 Ruppert view
(8654x6481).

**DROP:** `File:New York in 1674 - C. Vardel fec(it) - btv1b53143268k.jpg` (5250x4250, Public domain)
- a genuine bird's-eye view but **outside the collection's 1847-1929 range** (the 1674 drawing);
recorded, not staged. The 1906-aerial-era photographs and Flickr-era scans that appear in the pool
die on `commons.keep()` traps ("flickr - ", ".pdf", ".djvu", "geograph", "portrait") or on the
photograph rule - photographs of the city are not drawings.

## Washington DC (site `washington-q61`, 236a's point; 3 views staged)

**STAGED:**

- `File:The national capital, Washington City, D.C. LOC 75694904.jpg` - 1883, A. Sachse & Co.
  (Philadelphia), 9888x12560, Public domain. The city plus Georgetown, the title printed on the
  sheet, near-vertical; spans beyond the town box (likely review item).
- `File:B.H. Warner & Co.'s Map showing a bird's-eye view of the city of Washington and suburbs -
  locating the public buildings and places of interest LOC 87693417.jpg` - 1886, prepared by
  A. G. Gedney for B. H. Warner & Co., copyrighted and published 1st July 1886 (printed on the
  sheet), 7936x6168, Public domain. The whole city and suburbs: the diagonal avenues, the
  block-by-block grid, the Potomac and the Eastern Branch.
- `File:Washington, the beautiful capital of the nation LOC 78695113.jpg` - 1921, drawn by William
  Olsen, A. Graham Co., 13568x8944, Public domain. The whole city, the title printed on the sheet;
  the latest of the collection's DC views staged (the 1847-1929 range's near-edge).

**DROP (with reasons):** `File:View of Washington City. LOC 90683459.jpg` (1871, E. Sachse & Co.,
Boston, 7340x5340) - a **pictorial view**: the Capitol is the foreground subject and the city is a
painted background with no surveyed grid legible at fit scale. `File:District of Columbia and the
seat of war on the Potomac. LOC 88694227.jpg` (1861, Casimir Bohn / E. Sachse & Co., 4047x2689) - a
**regional** view (the Potomac from the Chesapeake to Harpers Ferry, Baltimore and Alexandria in
frame) in which Washington is a small part of the drawing. The 1866 "Capitol, East Front" view
(3355x2248) - a **building close-up**, not a city view. The 1861 balloon view (1536x1040) - **too
small to fit** (the Butler precedent in the 236a lead).

**RESERVED for a later batch:** the 1872 Morrison view (6192x4752) and "The ultimate Washington"
(1915, H. L. V. Hoppin for National Geographic, LOC 87694199, 6394x4705 - the speculative 1915
city).

## San Francisco (site `san-francisco-q62`, 236a's point; 4 views staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:San Francisco. 1854 (published for the History of the world) - DPLA - Original.jpg` - 1854
  (the sheet is titled "SAN FRANCISCO. 1854." and says "Drawn according to Act of Congress in the
  year 1852"; the Commons page itself is undated - the year comes from the title), Henry Bill,
  New York, 7000x4156, Public domain. **The oldest staged view of the city**: the oblique hilltop
  view with the old town a third of the frame (the bay behind, Yerba Buena Island to the right, the
  numbered legend along the top). The file's page lost the drawing's date, so the known 1854 is on
  the row (the Zwolle precedent). The two Geographicus scans (3500x1974 / 4000x2325, the same sheet)
  are the smaller copies - the DPLA scan is staged.
- `File:(Bird's eye view of San Francisco) LOC 75693101.jpg` - 1868, drawn by George H. Goddard,
  lith. Britton & Rey, published by Snow & May, 12912x8176, Public domain. THE classic: the whole
  peninsula and the bay from the hills, the street grid dense in the built-up mass. The IA scan
  (12587x8962, with the title banner) and the NYPL scan (7662x5062, CC0) are the **same sheet**
  (eyeballed 2026-10-14): one row.
- `File:The city of San Francisco. Birds eye view from the bay looking south-west. LOC 75693104.jpg`
  - 1878, drawn by Charles R. Parsons, published by Currier & Ives, 11376x8272, Public domain.
  From the bay looking south-west; the LCCN90715988 .jpg/.tif pair (5581x4009) is a smaller scan of
  the same sheet.
- `File:1914 San Francisco Birds Eye Map by Peter.jpg` - 1914, drawn by C. Merriman Peter,
  11302x8777, Public domain. The pre-1915-exposition whole peninsula, dense grid plus a street
  index.

**DROP (with reasons):** `File:Panoramic view of San Francisco, California, from hilltop, looking
northeast LCCN2006677456.jpg` (1850, 10300x6113) and `File:View of San Francisco, formerly Yerba
Buena, in 1846-7 before the discovery of gold. LOC 74693207.tif` (1884, 8464x6304, Bosqui) -
**pictorial** views, the city small in the frame, no grid at fit scale. The 1906 earthquake aerials
(Chadwick's "captive airship", the smoldering-downtown sheet) - **photographs**, not drawings
(236a's HABS-photo precedent). "'View of San Francisco in 1850', 1878, oil on canvas (Burgess)" -
a **painting**. The Faust flat maps (maps, not views), the "(Covers to)" book covers, and the
Seattle/Port Townsend search noise - not this city / not a view.

## Nashville (site `nashville-q23197`, 236a's point; 1 view staged)

**STAGED:**

- `File:Tennessee Centennial Exposition, Nashville, Tennessee, 1897. LOC 77696328.jpg` - the sheet's
  banner says "NASHVILLE, TENNESSEE, 1897." but the Commons page dates the copyright 1896 (the
  sheet's lower-left "COPYRIGHT 1896"), so the known drawing/publication year **1897** is on the
  row and the page value kept as `date_commons` (the Zwolle precedent). The Henderson Litho. Co.,
  Cincinnati, 13851x9666, Public domain (color). A bird's-eye view of the 1897 exposition grounds
  in Schreiner Park, the state Capitol on the hill at the left: it depicts **PART of the city** -
  the park and its approaches rather than a street grid - so its fit leans on the Capitol hill, the
  park bounds and the approach roads (noted for 236c/the matcher). **The other scans of the same
  sheet** - `File:Tennessee Centennial Exposition 1897 (LOC ppmsca.03354).jpg` (ppmsca.03354 = the
  LOC item id) and the Henderson Litho LCCN95501846 .jpg/.tif pair (6315x4483) - are dropped, one
  row per sheet (the largest scan is staged).

**DROP (with reasons):** the three **Fletcher 1864 Fort Negley views** (W. H. H. Fletcher, 12th
Battery Ind. Vols., all Public domain): `File:South west view of Fort Negley LCCN2003655690.jpg`
(7950x3822) + `.tif` (7964x4356), `File:North west view of Fort Negley LCCN2003655670.tif`,
`File:South east view of Fort Negley LCCN2003655689.jpg` (8082x3978). Each is a **close-up of the
fort on its hill with no city grid** (the SW view eyeballed 2026-10-13: the earthworks and the
batteries, the surrounding country rural) - there is nothing to fit to the city, and 236a found no
fort-only plan, so **no Fort Negley fort site exists** to attach them to (236a's site note says the
same). The 1897 centennial view stands as Nashville's bird's-eye view (the "at least one view or the
lead doc says why" box holds either way).

## Boston (site `boston-q100`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Bird's eye view of Boston. LOC 75694559.jpg` - 1902, Geo. H. Walker & Co., 8288x5712, Public
domain (LC Panoramic 279.1). The **steep near-vertical whole-city view**: the street grid dense and
legible to the suburbs, the harbour and Charles-River shorelines, a printed key of numbered
landmarks (1-14) along the bottom; the sheet spans the whole city far beyond the 2000 m town box, so
its fit is likely to end a review item (the 236a NY-1811 / DC-ring precedent). **`File:1902 birds-eye
view map of Boston featuring Beach and Clarridge Company.jpg` (8288x5712) is the SAME sheet**
(identical title block, key, the B&C factory vignette and the hand-written accession numbers -
eyeballed 2026-10-14, the batch-1 close-out): one row per sheet, the LOC scan is staged. The .tif of
the same LOC item (8288x5712) is the same scan, dropped.

**DROP (with reasons):** the street-car maps - `File:1904 Boston and Worcester Street Railway
bird's eye view map.jpg` (18385x4894), `File:1908 bird's eye view of trolley routes in New
England.jpg` (New England Street Railway Club, 4439x6366) and the 1908/1911/1914/1917 station and
route sheets - railway route maps, not city views. The regional sheets - `File:Birds eye view of
Mass., R.I. & Conn. LOC 79695398.jpg` (1905, Geo. H. Walker & Co. for the Joy Steamship Co.,
6475x5020) and `File:Bird's eye view of Boston Harbor along the South Shore to Plymouth, Cape Cod
Canal, and Provincetown - in colors - showing all steamboat routes. LOC 2010589292.jpg` (1920,
Federal Engraving & Publishing Co., 8112x6632; the 1905 LOC 2008624058 9072x8828 is the same subject)
- the city a small part of a multi-state / harbour sheet. `File:Bird's-eye view of waterfront, Boston,
Mass. LCCN2005691058.jpg` (1890, Detroit Publishing Co., 5541x4401) - a **photographic print** (the
236a HABS-photo precedent). `File:Birds eye view of the White Mountains LOC 2012592589.jpg` (1890,
8551x5957) - search noise (not Boston).

**RESERVED for a later batch** (same-genre obliques, passers - one view per city is staged): the 1850
John Bachmann view (`File:1850 bird's-eye view map of Boston.jpg` 9880x7280, the colour pair
8983x6709), the 1866 Nutting view (`File:1866 BirdsEye Boston byNutting BPL2675751434.jpg`
9587x6671), the 1870 Fuchs view (`File:1870 bird's-eye view map of Boston.jpg` 9872x7560), the 1877
Bachmann/Prang views from the north (`File:Boston - bird's eye view from the north - J. Bachmann del.
and lith. LCCN2001696113.jpg` 8544x6789 + .tif + 5000x4058 copy; `File:Boston bird's-eye view from the
north. LOC 75694554.jpg` 7888x6272), the 1899 Downs/Walker view (`File:1899 bird's eye view map of
Boston.jpg` 7810x5268 + 5400x3600 copy) and the 1872 Great-Fire / burned-district pair
(`File:1872 bird's eye view map of Boston after the Great Fire.jpg` 9176x6336 /
`File:Bird's-eye view of Boston, showing the burned district 01.jpg` 7272x5200).

## Philadelphia (site `philadelphia-q1345`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Bird's eye view of Philadelphia. LOC 75694509.jpg` - 1872, drawn and engraved expressly for
Harper's Weekly from sketches by Theodore R. Davis (the sheet's banner: "SUPPLEMENT TO HARPER'S
WEEKLY, June 15, 1872."), 9744x6816, Public domain (LC Panoramic 828). **The steepest (near-vertical)
view staged for the city**: drawn from the Schuylkill side, the street grid legible from the old town
to the northern suburbs, the squares, the Delaware with its shipping in the foreground; the sheet
spans well beyond the 2000 m town box, so its fit is likely to end a review item (the 236a NY-1811 /
DC-ring precedent). **`File:Bird's-eye view of Philadelphia - drawn and engraved expressly for
Harper's Weekly from sketches by Theodore R. Davis. LCCN2012645607.jpg` (10173x7287) is the SAME
sheet** (identical title block, the same grid, the same islands and shipping in the Delaware; a
different physical copy - ragged margins and a different hand-written accession number - eyeballed
2026-10-14, the batch-1 close-out): one row per sheet, the LOC scan is staged. The .tif of the same
LOC item (9744x6816) is the same scan, dropped.

**DROP (with reasons):** `File:Bird's eye view of Philadelphia. LOC 75696517.jpg` (1857,
Bachmann/Weik/Duval, 11472x9136) - a **shallower oblique** with a large sky band (a pass on the
one-view pick, not on quality). The 1875/76 Centennial / Fairmount sheets (exposition close-ups, no
city grid): `LCCN2003679941` (9836x6924, Philadelphia & centennial grounds), `LCCN93504545`
(8197x6434), `LCCN00650148` (8088x6848), `LCCN90711913` (7226x5580), `LCCN90711914` (7309x5492),
`LCCN2006676664` (8350x6375), the NYPL Hades-118934 scan (6011x5200) and the Fairmount-with-
Exhibition scans. `File:Birds eye view of Manayunk, Wissahickon=Roxborough from West Laurel Hill
Cemetery, Philadelphia, Pennsylvania 1907. LOC 76693090.jpg` (9152x5792) - the **western districts**,
not the city. `File:Hydroplanes - Manufacturers - Navy Aircraft Factroy, Philadephia, Pennsylvania
(NAF) General - ... - NARA - 31484700.jpg` (1917, 9145x6207) - a **photograph/document** of a Navy
plant (the HABS-photo precedent). `File:Birds eye view of Philadelphia and vicinity showing location
of the Philadelphia & Reading Railroad. LOC 76695313.jpg` (1870, 5152x7040) - a **railway map**, not
a city view.

**RESERVED for a later batch:** `File:Bird's-eye view of the city of Philadelphia -its streets,
avenues, and public buildings-and of the Centennial buildings in Fairmount Park. LOC 76695314.jpg`
(1876, Frank Leslie, 9696x6800) - a genuine whole-city view, a shallower oblique than the staged
1872 sheet - and the 1857 Bachmann/Duval pair (5451x4448, LCCN2003679940).

## Baltimore (site `baltimore-q5092`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:The City of Baltimore - sketched and drawn by C.R. Parsons. LCCN90715972.jpg` - 1880, drawn
by C.R. Parsons, published by Currier & Ives, 10206x7171, Public domain. A **steep oblique view
drawn from the south**: the whole city, the Inner Harbour in the foreground, the dense grid and the
parks, a printed key of landmarks; the sheet spans the whole city beyond the 2000 m town box, so its
fit is likely to end a review item (the 236a NY-1811 / DC-ring precedent).

**DROP (with reasons):** the 1862 Sachse pair - `File:View of Baltimore City, Md., looking South -
lith. & print by E. Sachse & Co. 5 N. Liberty St. Balto. LCCN2012648855.jpg` (7953x5983) and
`File:View of Baltimore City, Md., from the North - lith. & print by E. Sachse & Co. 104 S. Charles
St. Baltimore. LCCN2012648854.jpg` (7657x4693) - **pictorial** views: the Washington Monument is the
foreground subject and the city a painted background with no surveyed grid legible at fit scale (the
DC-Sachse precedent, eyeballed 2026-10-14 batch 1). `File:A birds-eye view of the heart of Baltimore.
LOC 75694536.jpg` (1912, Spofford, 9968x6560) - a **downtown-only** partial view. `File:Birds eye
view of the seat of war. Arranged after the latest surveys, ... LOC 99447047.jpg` (1861, Louis Prang,
6360x5021) - a **regional** sheet (Washington, Baltimore, Harpers Ferry, Richmond, Manassas, Ft.
Monroe, Norfolk). The fort / camp sheets (fort close-ups with no city grid, and no fort site exists
to attach them to - the Fort Negley precedent): `Camp Carroll, Baltimore, Md LCCN2003654992.jpg`
(1862, 8984x6078), `Fort McHenry, Baltimore, Md LCCN2003656652.jpg` (1861, 8920x5976), `Fort number
1 - west defences of Baltimore, Md LCCN2003656653.jpg` (1863, 7980x5708), `Camp Belger, Baltimore,
M'd. - 114th Regt. New York S. Volunteers-... LOC 93685279.jpg` (1862, 7128x5485) and the 1863
Illustrated-album-of-Baltimore-City strips (LCCN2003656659/6668). The street-car maps -
`File:United Railways map of Baltimore 1910.jpg` (8495x4670) and `File:Trolley trips in and out of
Baltimore - map of system showing places of interest and how to reach them. LOC 96681722.jpg`
(1913, 16892x4593) - route maps, not city views. `File:Baltimore fire, 1904) Bird's eye view of
Baltimore LCCN2016844565.jpg` (National Photo Company Collection, 8513x6958) - a **photographic
transparency** (the HABS-photo precedent). The small 1869 Sachse station close-ups (Calvert St,
President St, Riverside) - building close-ups, too small to fit.

## Pittsburgh (site `pittsburgh-q1342`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Pittsburgh, Pennsylvania 1902. LOC 75696521.jpg` - 1902, T. M. Fowler for James M. Moyer,
7256x4856, Public domain (LC Panoramic 833). A **steep oblique view drawn from the south**: the whole
city at the confluence, the Allegheny and Monongahela in the foreground, the bridges, the printed
index of numbered landmarks (1-16); the sheet spans the whole city beyond the 2000 m town box, so its
fit is likely to end a review item (the 236a NY-1811 / DC-ring precedent). **Three other scans of the
same sheet (eyeballed 2026-10-14, the batch-1 close-out - identical title block, the same numbered
index, the same "COPYRIGHT BY T. FOWLER & JAMES M. MOYER" line; the Adam Cuerden copy is a different
physical copy):** `File:Pittsburgh, Pennsylvania 1902. LOC 75696521.tif` (the .tif of the same LOC
item, 7256x4856), `File:Pittsburgh 1902.jpg` (7256x4856, a 2010 scan - identical dimensions and the
same hand-written annotations) and `File:Thaddeus M. Fowler - Pittsburgh, Pennsylvania 1902.jpg`
(7206x4806, Adam Cuerden) - one row per sheet, the LOC scan is staged.

**Name-search trap (the Barnard-Castle class, the 236a Q60 note):** the first "Pittsburgh"
name-search hit with coordinates is Q235034 University of Pittsburgh (-79.953274, 40.444565, ~4.0 km
east of the city point) - within the 50 km flag, so `--verify` does not flag it, but `record --live`'s
caption route would store the university's point instead of the city's. The staged row hand-records
the city's P625 (dist 0); the trap is recorded on the Q1342 SITES comment and site note.

**DROP (with reasons):** `File:Pittsburgh 1904.jpg` (1904, William Campbell, 9560x1680) - a
**painted skyline strip** with no street grid. `File:Pittsburgh, Allegheny & Birmingham.jpg` (1871,
Otto Krebs, 5880x3186) - a shallower panorama. `File:View of the ruins of the city of Pittsburgh from
Boyd's Hill - painted by W.C. Wall; on stone by James Queen... LCCN2014648393.jpg` (1850, 5560x3960)
- a **pictorial painting** (the post-flood "ruins" view), not a surveyed city view. `File:Bird's-eye
view of Pittsburgh, Pennsylvania, with river in foreground (cph.3c10668).tif` (1905, 4096x3289) - a
**Library of Congress photograph** (the HABS-photo precedent).

## Cincinnati (site `cincinnati-q43196`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Panoramic view, city of Cincinnati, U.S.A. 1900. LOC 75694914.jpg` - 1900, drawn by John L.
Trout, The Henderson Litho. Co., Cincinnati, 14320x9664, Public domain (LC Panoramic 685). A **steep
view drawn from the south**: the whole city, the Ohio in the foreground, the hillside blocks dense and
legible; the sheet spans the whole city and its hillside suburbs beyond the 2000 m town box, so its
fit is likely to end a review item (the 236a NY-1811 / DC-ring precedent). **`File:Cincinnati-aerial-
view-1900.jpg` (10000x6459, DPLA) is the SAME sheet** (identical title block and fold lines -
eyeballed 2026-10-14, batch 1): one row per sheet, the larger LOC scan is staged. The `(Mill Creek)`
crop (9217x5001) is a detail crop of the same sheet, dropped.

**DROP (with reasons):** `File:Cincinnati, U.S.A LCCN2003691125.jpg` (12519x5168 + the 11100x1609
crop) - the **1900 Ulrich steel-engraving strip**: a second sheet of the same year, and one view per
city is staged (the 1900 Trout sheet is the steeper whole-city view). `File:View of Camp Dennison-
16 miles northeast of Cincinnati, Ohio - lithographed by Middleton, Strobridge & Co....
LCCN2013645282.jpg` (1865, 10317x7499) - a **camp 16 miles out**, not the city. The Price-Hill
inclined-plane sheets (`File:Birds-eye view of Price Hill inclined planes. Cincinnati, O
LCCN2003656969.jpg`/`.tif` 8493x6747, `File:Birds-eye view of Price Hill inclined planes,
Cincinnati.jpg` 7643x6181) - **close-ups** of the hillside works. `File:Bird's eye view of Camp
Chase - DPLA - a43492d77185c5ed15cfd63562098668.jpg` (1898, 4496x3016) - a **camp** (the Civil-War
prison), not the city. Search noise: the 1896/97 Tennessee Centennial sheet (`File:Tennessee
Centennial Exposition, Nashville, Tennessee, 1897. Opens May 1st - Closes Oct. 31st - The Henderson
Litho. Co., Cincinnati. LCCN95501846.jpg` 6315x4483 - made BY The Henderson Litho. Co. of Cincinnati;
that view is 236b's staged Nashville view), `File:View of Georgetown, Colorado, 1874 - DPLA -
eaf2a145a27092ce8408f891af4147a0.jpg` (4000x3171 - a Strobridge sheet published in Cincinnati) and
the Monroe, Ohio photograph.

## Louisville (site `louisville-q43668`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Birds-eye view of Louisville from the river front and Southern Exposition, 1883. LOC
  75693235.jpg` - 1883, W. F. Clarke, M. P. Levyau & Co., 10864x6928, Public domain (LC Panoramic
  237). A **two-panel sheet drawn from the river front (the Kentucky side)**: the 1883
  International Exposition of Agriculture, Manufactures and Implements hall above (ornament
  panels + the "PUBLIC BUILDINGS" index); the steep near-vertical whole-city view below (the Ohio
  and its bridges in the foreground, the grid dense and legible, the "MAP OF LOUISVILLE AND ITS
  ENVIRONS 1883" inset bottom-right); spans the whole city beyond the 2000 m town box, so its fit
  is likely to end a review item (the 236a NY-1811 / DC-ring precedent). **Two further scans of the
  same sheet (eyeballed 2026-10-14, the batch-2 close-out):** the .tif twin of the same LOC item
  (10864x6928) and `File:Birdseye-southernexpo.jpg` (10757x6905, a different copy) - identical
  title block "BIRDS-EYE VIEW OF LOUISVILLE FROM THE RIVER FRONT AND SOUTHERN EXPOSITION, 1883.
  DEDICATED BY THE PUBLISHERS TO THE LOUISVILLE BOARD OF TRADE AND MANUFACTURING INDUSTRIES.",
  identical panels and inset - one row per sheet, the LOC scan is staged.

**DROP (with reasons):** the 1876 sheet - `File:Bird's eye view of Louisville, Kentucky 1876.
LOC 73693416.jpg` (7890x5808, A. Ruger, Charles Shober & Co. / Chicago Litho., LC Panoramic 236) +
the .tif twin (7890x5808) + the 987x726 copy (`File:Bird's eye view of Louisville, Kentucky
1876.jpg`) - **a different, shallower oblique from the Kentucky side** (eyeballed 2026-10-14: the
Ohio and its bridge in the foreground, the city across the river, a printed index of churches /
public buildings) - one view per city, the steeper 1883 is staged. `File:Birds eye view of
Louisville, Kentucky LCCN2007662142.tif` (1910, 4096x3281) - a later sheet, low-res scan. `File:US-
KY(1891) p287 LOUISVILLE, BIRD'S-EYE VIEW.jpg` (1891, 1836x1089) - a book plate, too small. The
1861 Union-envelope prints (LCCN2016648172 .jpg/.tif, 1536x860) - small envelope pictorials. Search
noise: the Audubon plates and the "Japanese White Eye" / duck / vireo photographs (the "birds" of
the search), the *Our own birds* / *The birds of America* book pages, the L&N "Tourist through car
line" sheet (874x1536, Poole Bros. - a railway sheet), the R&D / Florida Central railway sheet
(4911x8485) and the 1861 "War Map of the Middle States" balloon view - not Louisville city views.

## St. Louis (site `st-louis-q38022`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Bird's-Eye View of St. Louis, MO. (full view).jpg` - 1858, James T. Palmatary,
  14437x7800, Public domain. **The steepest (near-vertical) and oldest view staged for the city**:
  drawn from the high ground east of the Mississippi (the "BIRD'S EYE VIEW OF SAINT LOUIS, MO."
  banner), the levee and a whole steamboat fleet in the foreground, the grid legible from the
  downtown levee to the far suburbs; spans well beyond the 2000 m town box, so its fit is likely
  to end a review item (the 236a NY-1811 / DC-ring precedent). **The seven "(... detail).jpg"
  tiles are high-resolution crops of the same sheet** (eyeballed 2026-10-14, the batch-2
  close-out: the upper-left tile's street labels - 40th-44th, Chestnut, Main, Olive, Delaware,
  Walnut, Locust - match the full view's northwest district): the upper-left (14401x11289),
  upper-right (15156x11808), lower-left (14150x11635), upper-right-center (14944x11591),
  lower-right-center (15149x11592 - the "Saint Louis"-titled one, which fails the caption gate on
  its title), lower-left-center (15149x11592) and upper-left-center (15174x11159) - one row per
  sheet, the full-view scan is staged.

**DROP (with reasons):** the 1876 **railway sheet** - `File:Birds eye view of St. Louis - showing
the new line of the St. Louis, Kansas City & Northern Ry. running into the Union Depot.
LOC 82695092.jpg` (7560x3944, C. K. Lord, Woodward, Tiernan & Hale, LC Panoramic 439.1) + the .tif
(7560x3944) + the DPLA mirror (fe27966c, 5843x3063) - the KC&N line running into the Union Depot is
the subject (rail viaducts at both ends, two circular insets - the East St. Louis bridge and the
Union Depot tunnel), the city is the background. The 1893/1895 whole-city sheets - "St. Louis in
'93" (LOC 75694659, 11904x7680, Fred Graf, LC Panoramic 441, copyrighted 1892) - a **shallow
skyline view from the river** (the Eads Bridge, the population plates 400,552/550,000, Pfea. Graf
Litho.) - and "St. Louis in 1895" (LOC 75694661, 12368x8240, Charles Juehne, LC Panoramic 443,
steeper, with a printed index and the Eads Bridge) - different later sheets; one view per city
(the 1858 is older and steeper). `File:St Louis Birdseye Map 1896.jpg` (1896, 10753x6999, Fred
Graf) - another later sheet. The 1904 World's Fair sheets (**exposition close-ups**, not the
city): `"World's Fair, St. Louis, 1904." (Birdseye view of the 1904 Worlds Fair)` (7275x5337,
1903, Gray Litho. Co. after Charles Graham) and `Birdseye view of the Palace of Manufactures from
the DeForest Wireless Tower at the 1904 World's Fair` (5894x4688, F. J. Koster). The **DPLA
mirrors** ("No restrictions", not marked Public domain): the 1858 full view (4ca97211, 14437x7800
= the staged sheet), the detail-tile mirrors, and the four "horizontal hand-colored steel
engraving" views (9a6de5ee / 8e729fb1 / c143bc6d / f90661ca - the last dated 1852, a different
older engraving). **Photographs / book prints** (the HABS-photo precedent): the 1911 Pierce
Building view (DPLA a69ad046, Boehl, 8154x5988), the 1913/1918 Old Courthouse views (DPLA,
Persons), the "steamboats docked along the levee" print from Edwards' *Great West* (DPLA
dd18ff8a, 7009x5414 - a book print), the stereograph sets (Continent Stereoscopic ca. 1865/1885,
Robert Benecke ca. 1880, the Robert N. Dennis collection 1903-04, the NYPL b11707637/b11707638
scans), the NBY postcards (806x522), the *Pictorial St. Louis* plate (5856x4032, 1876), the 1853
DPLA engraving mirror (4615x3049, "No restrictions"), and the 1837 Catlin Mandan Village painting
(1400x1153 - not the city, out of range).

## Chicago (site `chicago-q1297`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Bird's eye view of Chicago, 1892. LOC 75693206.jpg` - 1892, Peter Roy ("Copyright, 1892,
  by Peter Roy" on the sheet), 9904x5648, Public domain (LC Panoramic 151). **Steep near-vertical
  whole-city view drawn from the lake**: Lake Michigan in the foreground, the grid dense and
  legible to the horizon, a numbered index at the bottom and a "VIEW OF CHICAGO IN 1832" scroll
  inset bottom-right; spans the whole city beyond the 2000 m town box, so its fit is likely to
  end a review item (the 236a NY-1811 / DC-ring precedent). **`File:Bird's eye view of Chicago,
  1893. LOC 97686545.jpg` (9104x4480) is the same view in colors** (eyeballed 2026-10-14, the
  batch-2 close-out: identical composition - the same lake, grid, 1832 scroll and index;
  railroads in red, parks in green) - one row per view, the larger 1892 sheet is staged.

**Name-search trap (the Barnard-Castle class, the 236a Q60 note):** the first "Chicago"
name-search hit with coordinates is Q131252 University of Chicago (-87.599722, 41.789722, ~10.5 km
south of the city point) - within the 50 km flag, so `--verify` does not flag it, but `record
--live`'s caption route would store the university's point instead of the city's. The staged row
hand-records the city's P625 (dist 0); the trap is recorded on the Q1297 SITES comment and site
note.

**DROP (with reasons):** the 1857 sheets - `File:1857 Bird's Eye View of Chicago - LOC.jpg`
(24928x15136) and `File:1857 Bird's Eye View of Chicago.jpg` (6424x3698; drawn by I. T. Palmatary,
lith. Christian Inger, published Braunhold & Sonne) - different earlier sheets (one view per city,
the 1892 is steeper). The 1853 `File:1853 Chicago Bird's Eye view.jpg` (4236x2141, unattributed)
and the 1871 Harper's Weekly sheet `File:Bird's-eye-view of Chicago as it was before the great
fire. LOC 74693213.tif` (6276x4698, T. R. Davis, "From Harper's weekly, October 21, 1871, pages
984-5") - earlier sheets. `File:1874 Birds eye map of Chicago by Currier & Ives.jpg` (7161x5134)
and `File:1879 Birds eye view of Chicago.jpg` (3713x2453, Louis Klinckerfus & Jacob Richter) -
different shallower sheets. The 1898 **business-district** sheets (`File:1898 Bird's Eye View of
Chicago.jpg` 18144x12992 + `File:Bird's-eye-view of the business district of Chicago.
LOC 75693212.jpg` 18144x12992, Poole Brothers, LC Panoramic 153) - downtown-only partial views.
`File:All elevated trains in Chicago stop at the Chicago Rock Island and Pacific Railway Station,
only one on the Loop LOC 84694897.jpg` (1897, 9573x8700, Poole Bros.) - a **railway sheet**.
`File:Birds-eye view of the elevated railroads and the parks and boulevards of Chicago.
LOC 2010592719.jpg` (1908, 13134x7286, Willis J. Champion) - a **district sheet** (elevated
railroads / parks), not the whole city. The 1893 World's Fair sheets (**exposition close-ups**):
`File:World's Columbian Exposition, Chicago 1893 (Bird's-eye view) LCCN2003670686.jpg`/`.tif`
(5781x3912, Popular Graphic Arts), `File:1893 Birds Eye view of Chicago Worlds Columbian
Exposition.jpg` (11616x8880, Rand McNally), `File:Grand birds-eye view of the grounds and
buildings of the great Columbian exposition at Chicago, Illinois, 1892-3 LCCN2001700243.jpg`
(1536x968) + the 10325x6925 .tif (Currier & Ives). `File:1912 Birds eye view of Chicago.jpg`
(7576x4801) - the 1912 Junction Railway / Central Manufacturing District sheet. `File:World's
pictorial line - birdseye views in the Rocky Mountains reached via the Union Pacific, the Overland
Route - DPLA - ae90df794c267feb1cafaecccd8c2562.jpg` (1893, 7000x3160) - a **regional** sheet.
**Photographs** (the HABS-photo precedent): the NBY postcard scans (Downtown from the Board of
Trade, From Harbor, The Loop, Lincoln Park, Grant Park, Michigan Blvd. Bridge, Northwestern
Depot, Business District / CNW Terminal) and `File:Bird S Eye View Of Chicago (117348765).jpeg`
(2015, CC BY - a modern photo). Search noise: the 1866-69 Ruger / Koch / Chicago-Litho sheets of
Jackson (MI), Lansing (MI), Winona (MN), Pella (IA) (the "Chicago Lithographing Co." is the
publisher, not the city) and the "Graves of Mabel Birdseye Crawford..." photo (the Birdseye
surname).

## Detroit (site `detroit-q12439`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Birds eye view-showing about three miles square-of the central portion of the city of
  Detroit, Michigan. LOC 76693077.jpg` - 1889, Calvert Lithographing Co., 6815x4184, Public domain
  (LC Panoramic 342; the sheet: "Used through the kindness of the Imperial Life Ins. Co.").
  **Steep oblique view drawn from the Detroit River**: "about three miles square of the central
  portion of the city", the river and its shipping in the foreground, the grid dense and legible
  to the hills; covers the central city beyond the 2000 m town box, so its fit is likely to end a
  review item. **Six further scans of the same sheet (eyeballed 2026-10-14, the batch-2 close-out
  - identical title block "BIRDS EYE VIEW—SHOWING ABOUT THREE MILES SQUARE—OF THE CENTRAL
  PORTION OF THE CITY OF DETROIT, MICHIGAN.", the same composition, the same "THE CALVERT CITY OF
  DETROIT" side label and the same Library-of-Congress stamps):** the .tif twin of the staged LOC
  item (6815x4184), `File:Birds eye view showing about three miles square of the central portion
  of the city of Detroit, Michigan LCCN2003666422.jpg` (10657x6108, the hi-res copy) + its .tif
  (10657x6108), `File:Bird's eye view of Detroit, Michigan, 1889 - . Calvert Lithographing
  Co..jpg` (6312x4132, Adam Cuerden restoration) + its .png (6312x4132), and `File:Map image
  detroit.jpg` (5999x3676) - one row per sheet, the LOC scan is staged.

**DROP (with reasons):** `File:Detroit 1908 Hurd-Martin 1907.jpeg` (4810x2717) and `File:Detroit
1818 Hurd-Martin 1906.jpg` (4798x2640) - the Hurd-Martin Co.'s **1818-Detroit postcard pairs**
(printed 1906-07; each sheet pairs an 1818 impression with a 1908 view from the same vantage;
"Detroit 1818: historically correct in every point of detail") - a postcard publisher's
pictorial impression, not a surveyed city view. Search noise: the NBY/NYPL postcards (Nantasket,
Williams, La Junta, Needles, the Kansas City business district, Toledo, the Boston waterfront -
the "Detroit Publishing Company" is the publisher, not the city), the 1875 Philadelphia / 1878
San Francisco / 1879 New York sheets (published in Detroit), the Put-In-Bay / Helgoland /
Charlestown views, the IA book pages.

## Milwaukee (site `milwaukee-q37836`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Milwaukee, Wis. LOC 76693067.jpg` - 1872, drawn by H. H. Bailey, Milwaukee Lithographing &
  Engraving Co., published by Holzapfel & Eskuche (the banner "MILWAUKEE, WIS."), 11952x8416,
  Public domain (LC Panoramic 1045). **Steep near-vertical whole-city view drawn from the
  lake**: a two-panel sheet (the river and mill-dams at the left, Lake Michigan and the city at
  the right), the grid dense and legible, a printed key of 69 landmarks; spans the whole city
  beyond the 2000 m town box, so its fit is likely to end a review item. **Two further scans of
  the same sheet (eyeballed 2026-10-14, the batch-2 close-out - identical banner, composition and
  key):** `File:Milwaukee 1872.jpg` (11952x8416) and `File:Milwaukee birdseye map by Bailey
  (1872). loc call no g4124m-pm010450.jpg` (9999x6650) - one row per sheet, the LOC scan is
  staged.

**DROP (with reasons):** the other whole-city sheets - `File:Milwaukee, Wis. 1879. LOC
75696716.jpg` (1879, 12656x8384, J. J. Stoner, Beck & Pauli, LC Panoramic 1046) and
`File:Milwaukee, Wis. LOC 75696717.jpg` (1882, 8192x4904, Beck & Pauli, LC Panoramic 1047) -
different later sheets; one view per city (the 1872 Bailey is the oldest and steepest).
`File:Milwaukee 1858.jpg` (the title says 1858, the sheet says **1854**; David William Moody,
chromo by Endicott & Co., New York, 12496x8432) - a **shallower 1854 chromo**, a different earlier
sheet. The **suburb** sheets - `File:Milwaukee 1892.jpg` / `File:Wauwatosa and the western
suburbs of Milwaukee 1892. LOC 75696728.jpg` (1892, 9424x6288, Marr & Richards, LC Panoramic 1065,
"Looking east from Wauwatosa") and `File:(Bird's-eye view of South Milwaukee) LOC 87690559.jpg`/
`.tif` (1906, 5846x3418, Binner Engraving) - Wauwatosa / South Milwaukee, not the city. **Photos**
(the HABS-photo precedent): the four W. H. Sherman Insurance-building views (1870/1875,
2737x1572-1608 .jpg/.png). `File:1910 Birds Eye View of Elevated Railroads, Parks and
Boulevards.jpg` (1910, 3789x2061, McComber Directory Co.) - a **district sheet** (the elevated
railroads), small scan. Search noise (Milwaukee as the publisher's city): the Cheyenne / Bayfield
/ Concord / Jacksonville / Maysville / Lake Geneva / Antigo / Seattle / Provincetown / Montello /
Whitehall / Saint Boniface / Columbus sheets (litho by Beck & Pauli / Fowler & Bailey / C. H.
Vogt, Milwaukee), the Ishpeming bpl scan (CC BY), the Bovill postcard (CC BY), the US Cellular
Arena photo, the IA book pages.

## Staging and checks (2026-10-14)

All fourteen cities staged so far are in this task's own files only: **21 views** total (11 for
the four owner-named cities - NYC 3, DC 3, SF 4, Nashville 1 - plus one for each of the ten
batch-1 and batch-2 cities) in `data/commons/files_us_birdseye.jsonl` (files.jsonl shape + the 200
evidence field) and `data/commons/classified_us_birdseye.jsonl` (`p_birdseye: 1.0`, `by: "hand"`);
the ten new-city site rows are in `data/catalog/extras_us_birdseye.jsonl` (the four owner
cities' sites come from 236a's file, above). `--check` (offline, no network), re-run at the
batch-2 close-out 2026-10-14:

```
PASS caption_coords  new-york-q60|File:New York - drawn by J. Bachmann ; print by G. Schlegel, 97 William St. N.Y. LCCN98508526.jpg
PASS caption_coords  new-york-q60|File:The city of New York. LOC 75694818.jpg
PASS caption_coords  new-york-q60|File:View of the city of New York and vicinity LOC 78692903.jpg
PASS caption_coords  washington-q61|File:The national capital, Washington City, D.C. LOC 75694904.jpg
PASS caption_coords  washington-q61|File:B.H. Warner & Co.'s Map showing a bird's-eye view of the city of Washington and suburbs - locating the public buildings and places of interest LOC 87693417.jpg
PASS caption_coords  washington-q61|File:Washington, the beautiful capital of the nation LOC 78695113.jpg
PASS caption_coords  san-francisco-q62|File:San Francisco. 1854 (published for the History of the world) - DPLA - Original.jpg
PASS caption_coords  san-francisco-q62|File:(Bird's eye view of San Francisco) LOC 75693101.jpg
PASS caption_coords  san-francisco-q62|File:The city of San Francisco. Birds eye view from the bay looking south-west. LOC 75693104.jpg
PASS caption_coords  san-francisco-q62|File:1914 San Francisco Birds Eye Map by Peter.jpg
PASS caption_coords  nashville-q23197|File:Tennessee Centennial Exposition, Nashville, Tennessee, 1897. LOC 77696328.jpg
PASS caption_coords  boston-q100|File:Bird's eye view of Boston. LOC 75694559.jpg
PASS caption_coords  philadelphia-q1345|File:Bird's eye view of Philadelphia. LOC 75694509.jpg
PASS caption_coords  baltimore-q5092|File:The City of Baltimore - sketched and drawn by C.R. Parsons. LCCN90715972.jpg
PASS caption_coords  pittsburgh-q1342|File:Pittsburgh, Pennsylvania 1902. LOC 75696521.jpg
PASS caption_coords  cincinnati-q43196|File:Panoramic view, city of Cincinnati, U.S.A. 1900. LOC 75694914.jpg
PASS caption_coords  louisville-q43668|File:Birds-eye view of Louisville from the river front and Southern Exposition, 1883. LOC 75693235.jpg
PASS caption_coords  st-louis-q38022|File:Bird's-Eye View of St. Louis, MO. (full view).jpg
PASS caption_coords  chicago-q1297|File:Bird's eye view of Chicago, 1892. LOC 75693206.jpg
PASS caption_coords  detroit-q12439|File:Birds eye view-showing about three miles square-of the central portion of the city of Detroit, Michigan. LOC 76693077.jpg
PASS caption_coords  milwaukee-q37836|File:Milwaukee, Wis. LOC 76693067.jpg
evidence: 21 rows, 21 pass, 0 fail, 0 no-tie
```

No join problems (every file row names an existing site - the four shared ids via 236a's file,
the ten new ids staged above; classified rows 1:1; the golden sample `tests/golden/
src_us_birdseye_sample.json` pins the 21 rows, regenerated at the stage).

**Not done yet (next sessions):** the 25-cities box - **11 more US cities** (25 total, 14 done),
each a NEW site in `extras_us_birdseye.jsonl` (region "United States", kind "town", aerial_ok
true, the point = the city's verified P625 or a recorded refinement, the note recording the
view's apparent angle), one best view per city, found by the file-namespace search route above
and QID-verified with `--verify` before staging. The next candidates (in order): **Kansas City,
New Orleans, Denver, St. Paul, Minneapolis, Cleveland**, ... (the LOC Panoramic collection,
1847-1929; a city with no usable view gets a lead-doc note and the next candidate). **Do NOT
write the canonical files - that is 236c.**
