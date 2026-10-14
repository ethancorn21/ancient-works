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

The four shared QIDs were first verified by 236a (docs/lead_us_cities.md, 2026-10-13/14); this is
236b's re-check that its own table stands on: label, every P625 value (flagged when >50 km from the
table point), P373, P131 (with labels), the enwiki article, and the first name-search hit with
coordinates (what `record --live` would resolve for the caption route). No P625 flag fired (Q62's two
values are 2.0-2.4 km from its table point - the point is a refinement, not a P625; Q23197's is
721 m NE); no search trap: the first search hit with coordinates is the city itself in all four cases.
New-cities batches re-run `--verify` as they are added (the table grows in `fit/src_us_birdseye.py:
SITES`).

```
checked 2026-10-14 - 4 QIDs (Wikidata)
  Q23197  'Nashville'  (site id: nashville-q23197, shared (236a))
      P625: [(-86.77444444444444, 36.16222222222222)]  (table site point: -86.78152, 36.16529)
      P373: ['Nashville, Tennessee']
      P131: [('Davidson County', 'Q1177705')]  (table place: 'Davidson County, Tennessee')
      enwiki: 'Nashville, Tennessee'  (table wikipedia: 'https://en.wikipedia.org/wiki/Nashville,_Tennessee')
      search 'Nashville': first hit with P625 is Q23197 'Nashville' (-86.77444444444444, 36.16222222222222)
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

## Staging and checks (2026-10-14)

The four owner-named cities are staged (11 views total: NYC 3, DC 3, SF 4, Nashville 1) in this
task's own files only: `data/commons/files_us_birdseye.jsonl` (files.jsonl shape + the 200 evidence
field) and `data/commons/classified_us_birdseye.jsonl` (`p_birdseye: 1.0`, `by: "hand"`);
`data/catalog/extras_us_birdseye.jsonl` stays **empty** until the new-city batches land (the four
owner cities' sites come from 236a's file, above). `--check` (offline, no network) on 2026-10-14:

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
evidence: 11 rows, 11 pass, 0 fail, 0 no-tie
```

No join problems (every file row names an existing site - the four shared ids via 236a's file;
classified rows 1:1; the golden sample `tests/golden/src_us_birdseye_sample.json` pins the rows).

**Not done yet (next sessions):** the 25-cities box - at least 21 more US cities, each a NEW site in
`extras_us_birdseye.jsonl` (region "United States", kind "town", aerial_ok true, the point = the
city's verified P625 or a recorded refinement, the note recording the view's apparent angle), one
best view per city, found by the file-namespace search route above and QID-verified with `--verify`
before staging. The four owner-named cities are done. **Do NOT write the canonical files - that is
236c.**
