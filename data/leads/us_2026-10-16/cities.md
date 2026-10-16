# Flat plans + existing georeferences for the 25 US city sites (2026-10-15/16)

Rows: `cities.jsonl` (72 rows, 25 cities; `georef` = best single georef (Allmaps CC0 with 4+ GCPs first), others in `georef_alt`; every row re-fetched by `scripts/build.py`; the fetched
JSON for each row and each georeference is saved in `cities_dl/verify/`). Raw search dumps:
`cities_dl/allmaps/*.json` (Allmaps spatial hits per city), `cities_dl/mapwarper/*.json`,
`cities_dl/allmaps_table.txt`, `cities_dl/labels.json` (Rumsey + Leventhal metadata),
`cities_dl/uchicago_titles.json`.

## Headline

- **Flat plan found: 25 / 25 cities.** Pre-1880 flat plan: 22/25. Exceptions: Kansas City
  (best = Wright's 1882, BnF), Portland OR (best = 1912), Minneapolis (best = 1881 Davison & Abbott).
- **Some existing georeference: 24 / 25** (no georeference of any kind for Kansas City).
- **CC0 georeference (Allmaps) with 4+ GCPs on a pre-1931 flat plan: 20 / 25.** Cities without one:
  Cleveland, Denver, Kansas City, Memphis, Nashville. Those have mapwarper.net GCPs only (licence not
  declared) or nothing.
- **CC0 georeference on a pre-1880 flat plan: 16 / 25** (Baltimore, Boston, Chicago, Cincinnati,
  Columbus, Detroit, Indianapolis, Louisville, Milwaukee, New Orleans, New York, Philadelphia,
  Pittsburgh, St Louis, San Francisco, Washington).

## Best per city

"GCPs" counts the control points in the existing georeference. Allmaps = CC0. mw = mapwarper.net (no
declared licence).

| City | Best plan to place | Existing georef | Earliest flat plan (if different) |
|---|---|---|---|
| Baltimore | Mitchell, Plan of Baltimore 1860 (Rumsey) | Allmaps 7 | Folie 1792 (LoC 2002624037), mw 5; 1804/1836 LoC plans in Allmaps but only 3 GCPs each |
| Boston | Bonner/Price, A new plan of ye great town of Boston 1743 (Leventhal) | Allmaps **69** | Bonner 1723 (Allmaps 12) |
| Chicago | Blanchard 1857 Map of Chicago (Rumsey) / Principal section 1863 (UChicago, 3.7 km) | Allmaps 10 / 10 | Thompson plat 1830 (Commons): none |
| Cincinnati | Mendenhall 1860 (Rumsey) | Allmaps 53 | Manuscript town plat 1792, mw 28; Plan 1815, mw 29 |
| Cleveland | Hopkins City Atlas 1881, plate 1 | mw 16 | Ahaz Merchant 1835 (Commons): none |
| Columbus | Bowen 1872 City of Columbus (Rumsey) | Allmaps 10 | Joel Wright 1812 plat (1825 copy, Commons): none |
| Denver | Fosdick 1859 Plan of Denver, Auraria and Highland (DPL) | mw 7 | (same) |
| Detroit | Mitchell 1874 Plan of Detroit (Rumsey) | Allmaps 22 | Farmer 1835 (LoC 79691130, 1:2,400): none |
| Indianapolis | Andreas 1876 Plan of Indianapolis (Rumsey) | Allmaps 15 | Ralston/Platt 1821 plat: mw 4 |
| Kansas City | Wright's map of Kansas City 1882 (BnF, Commons) | **none** | (same) |
| Louisville | Melish 1812 Falls of Ohio (Rumsey; chart with town plan) | Allmaps 9 | (same) |
| Memphis | Rucker 1858 Map of the city of Memphis (LoC 2012586237) | mw 4 (match to this map assumed) | Goedecke 1819 plan: none |
| Milwaukee | Mitchell 1874 Plan of Milwaukee (Rumsey) | Allmaps 19 | 1836 harbour-entrance chart (NARA): none |
| Minneapolis | Map of the City of Minneapolis 1889 (MDL) | Allmaps 7 | Davison & Abbott 1881: mw 5 |
| Nashville | City Directory map 1860-61, lith. J. F. Wagner (TEVA) | mw 9 | Clayton 1804 (staged): none |
| New Orleans | Mitchell 1874 Plan of New Orleans (Rumsey) | Allmaps 31 | Plan de la Nouvelle Orleans 1722 (LoC 2003623130): none |
| New York | Ratzer, Plan of the City of New York (to Sir Henry Moore) 1767/69 (NYPL image 434408) | Allmaps 25 | Duke's Plan 1664 (1859 facsimile), Allmaps 15 |
| Omaha | Everts, Omaha Central 1885 (Rumsey) | Allmaps 18 | Omaha District Map 1866: mw 12 |
| Philadelphia | Tanner 1836 (Rumsey) / Varle 1796 (Leventhal) | Allmaps 82 / 48 | Holme 1683: mw 11; Scull & Heap 1762 (LoC 74692589): none |
| Pittsburgh | Hayes 1877 Pittsburgh and Allegheny (Rumsey) | Allmaps 5 | John Hills 1787 lot plan (LoC 74692580, 1:1,600): none |
| Portland OR | American Map & Reproducing Co. 1912 (Leventhal) | Allmaps 10 | (same; nothing earlier found) |
| St Louis | Beck, Plan of St. Louis 1823 (Rumsey, 1.6 km) | Allmaps 16 | (same) |
| St Paul | Cram 1889 (Rumsey) | Allmaps 18 | Nichols 1852 (LoC 2012593356): none |
| San Francisco | Eddy, Official map of the City of San Francisco 1851 (Rumsey) | Allmaps 48 | Eddy 1849 (LoC 76695582): Allmaps 5 + mw 9 + mw 11 |
| Washington | Ellicott/Thackara & Vallance 1792 (Leventhal) | Allmaps 53 | L'Enfant 1791 manuscript (LoC 88694194): Allmaps 4 |

## Ties to the staged pictures (236a/236b)

- **New York.** Viele 1865: LoC 2006629795 has an Allmaps georef (24 GCPs) on the same map as the
  staged Commons Viele, so the GCPs can move over by image-to-image registration. Commissioners' Plan:
  LoC 2005625335 (Bridges, 5 GCPs). This is not the staged Randel 1821 sheet. Ratzer: the
  NYPL 1767/69 plan and the Leventhal copy (Allmaps da7eb52f5ba36401, 7 GCPs) are both georeferenced.
  The staged Commons Ratzer is the large plan, a different plate.
- **Washington.** The L'Enfant manuscript (4 GCPs) and Ellicott 1792 (53 GCPs, Leventhal copy) are both
  in Allmaps. If the staged Commons files are the same drawings, these GCPs carry over.
- **San Francisco.** Eddy 1849 (staged): the LoC scan has three independent georeferences.
- **Nashville.** Haydon & Booth 1860 (staged) has no georef. The mapwarper "Map of the City of
  Nashville (1860)" is a different map (the city-directory map lithographed by J. F. Wagner). The Poe
  survey (LoC 2003630459) has no Allmaps georef. mapwarper 81793 "Nashville Map (Poe)" has 3 GCPs and
  no source.

## How a fit can use these GCPs

Allmaps GCPs are `resourceCoords` (pixels in that exact IIIF image) paired with lon/lat (WGS84). To use
them directly, fetch the same IIIF image, at full size or with coordinates scaled. A Commons copy of the
same plan is a different pixel frame and needs an image-to-image registration first (homography or
feature match). After that registration the GCPs give an instant placement. A 3-GCP georef is an exact
affine with no residual check, so treat it as a seed only. mapwarper GCPs refer to the uploader's file
(`width`/`height` are in the API record). That file is often not the library master scan.

## Georeference services: API, terms, coverage

### Allmaps: the main source (CC0)

- **Spatial query** (the route that found almost everything):
  `GET https://api.allmaps.org/maps?intersects=LAT1,LNG1,LAT2,LNG2&minarea=M2&maxarea=M2&limit=200`.
  The order is **lat,lng**, checked in the source code at `packages/api-shared/src/queries/maps.ts`.
  Passing lon,lat silently returns world maps.
  - Results are ordered by `scale` descending (most detailed first).
  - The public limit is 200 per request (50 by default), and there are no usable pagination params.
  - Workaround: split by `minarea`/`maxarea` (m², the georef mask area) and bisect any band that
    returns 200. Chicago needed 11 bands (1,405 maps, almost all UChicago).
  - Sanity check: sqrt(area) of the Leventhal 1743 Boston plan is 2.65 km, which matches the peninsula.
  - Each map record carries `gcps` (resource px + geo), `resourceMask`, and `resource.partOf` with the
    manifest label when it is known.
  - The query used a ±300 m box around each site point, in bands of 1 km² to 2,000 km² plus 0.2 to
    1 km². Small atlas sheets (<0.2 km²) and Sanborn sheets were excluded on purpose.
- **Lookup by IIIF URL:** the id is the first 16 hex characters of sha1(URL).
  - `https://annotations.allmaps.org/manifests/{sha1(manifest URL)}`
  - `https://annotations.allmaps.org/images/{sha1(image service URL)}`
  - `https://annotations.allmaps.org/maps/{map id}`
  - Verified against the documented example (zlb.de manifest -> 6f5a7b547c8f6fbe) and against LoC
    items (sha1 of `https://www.loc.gov/item/{lccn}/manifest.json` hits for 76695582, 88694194,
    2006629795, 2005625335, 77691636, 2002624026, 79691615).
  - `annotations.allmaps.org/?url=` returns 403 (Cloudflare). Use the hash route.
- **End-to-end test:** `cities_dl/verify/am_cb59269309f5c97e.json` (Boston 1743, 69 GCPs, full
  Georeference Annotation with SVG mask and `polynomial` transformation). Every Allmaps georef in the
  jsonl was fetched the same way (`cities_dl/verify/am_*.json`).
- **Terms: CC0 1.0.** From the allmaps/allmaps README: "georeference data published through the
  Allmaps project is licensed under the CC0 license". From apps/homepage iiif-partnership.mdx: "All
  Georeference Annotations generated through Allmaps Editor or otherwise added to the Allmaps database
  are licensed as CC0 (public domain) and published daily as an open dataset". Bulk files are
  advertised at files.allmaps.org, but the root returns 404, so use the per-file paths from the
  homepage table.
- **The Rumsey GCPs in Allmaps** were bulk-created on 2025-02-26 by `allmaps/rumsey-scripts` from the
  Stanford dataset "David Rumsey Map Collection: Georeferenced Maps Metadata"
  (doi:10.25740/ss311gz1992). Stanford PURL: "This work is licensed under a Creative Commons Zero v1.0
  Universal license (CC0)". So the Rumsey GCPs are CC0 at the source too. The Rumsey **scans** are
  CC BY-NC-SA 3.0 (Stanford catalogue records). That NC clause applies to the image, not the GCPs.
- **Image licences of the hosts seen:**
  - Leventhal/BPL (Digital Commonwealth): "No known copyright restrictions".
  - UChicago Library: CC BY-NC 4.0 (manifest `rights`).
  - LoC: no known restrictions.
  - NYPL: catalogue not reachable, so not checked.
- **Coverage, by host** (counts of hits in the 1 to 2,000 km² bands over the 25 cores):
  - Leventhal: Boston is very dense; scattered elsewhere.
  - Rumsey: 238 hits, mostly atlas city plans 1823-1903 (Mitchell, Colton, Tanner, Cram).
  - UChicago: Chicago 1830s-1930s, about 1,400 maps; titles resolved via n2t.net for about 500.
  - NYPL: about 300 hits over New York.
  - LoC: 49 hits.
  - Minnesota Digital Library: Minneapolis.

### mapwarper.net: secondary

- **API:**
  - Search: `GET https://mapwarper.net/api/v1/maps?query=TEXT&per_page=100&page=N`. Each record has
    `bbox`, `status`, `width`/`height`, `source_uri`.
  - GCPs: `GET https://mapwarper.net/api/v1/maps/{id}/gcps` returns JSON with x, y, lat, lon, error.
    This works anonymously and was tested end to end (Boston 1789, map 8736; every mapwarper georef
    in the jsonl is saved as `cities_dl/verify/mw_{id}_gcps.json`).
  - The HTML `/maps/{id}/gcps.csv` redirects to a "verify-human" wall. Use the API.
- **Terms:** no licence is declared for GCPs. mapwarper.net/privacy says contributions "are public and
  available for others to view and use" and "Control points can also be downloaded by others". It is
  a one-person hobby service (Tim Waters). **Not cleared under the owner's licence-check rule.** Ask
  before adopting, or use the GCPs only as a private seed and re-pick points.
- **Coverage:** user uploads, often with no `source_uri`. Best finds: the Cincinnati early plats
  (1792, 1802, 1815, 1830, 1834, 1838; CHPL sources), Denver 1859/1878 (DPL), Indianapolis 1821,
  Baltimore 1792/1801/1836, Philadelphia 1683, and New Orleans Zimpel 1834. The St Louis and St Paul
  searches must use "Louis"/"Paul" (the query does not match "St.").

### Other services

- **NYPL Map Warper** (maps.nypl.org/warper): **dead**. Every URL redirects (301) to an Archive-It
  Wayback snapshot from 2021-05-20. The NYPL georefs now appear in Allmaps as `iiif.nypl.org` images,
  but without manifest links, so titles must be found by looking at the image. NYPL Digital
  Collections is Incapsula-walled for curl and WebFetch. The two NYC NYPL rows were identified by
  viewing the image (`cities_dl/nypl_thumbs/big_*.jpg`, contact sheets `cities_dl/nypl_sheet_*.jpg`).
- **David Rumsey Georeferencer** (georeferencer.com): the Luna metadata field `georeferencer_status`
  marks georeferenced items. A search result says GeoTIFF download needs sign-in (not tested). Not
  needed: the same GCPs are in the CC0 Stanford dataset and in Allmaps.
- **OldMapsOnline**: a discovery portal over Klokan/Rumsey holdings with no GCP export of its own. Not
  queried.
- **Harvard WorldMap / Warp**: moved to ArcGIS Online in 2021. No Warp GCP API was found. Not used.
- **LoC's own GeoTIFFs**: only special sets (e.g. the Austro-Hungarian 3rd survey). None found for
  these cities.

## Fetch notes

- loc.gov blocks curl (Cloudflare 403). tile.loc.gov IIIF works with curl, and every LoC row's
  `info.json` was fetched. LoC search JSON came through WebFetch. LoC dates for 77691636 (1804) and
  2002624026 (1836) come from that WebFetch summary only.
- Commons API (curl) verified every Commons row: title, size and licence.
- Year source: Rumsey `date` field and Leventhal `date_tsim`. For others, the year comes from the
  title/LoC record. The raw tables' regex years are hints only (they catch birth years and depicted
  dates).

## Per-city notes (what a fit can hold on)

Each jsonl row's `notes` carries its anchors. Recurring good anchors:

- Grids that survive unchanged: the Vieux Carré; the Indianapolis Mile Square + circle + diagonals;
  Penn's squares in Philadelphia; the L'Enfant radials; Detroit's Woodward radials; the Memphis
  squares.
- Shorelines that moved a lot (use with low weight): Boston, Chicago, San Francisco's Yerba Buena Cove,
  the Baltimore Basin, the New Orleans batture.
- Standing buildings: Old State House / Old North Church / Faneuil Hall (Boston); St Paul's Chapel
  1766 (NY); Independence Hall (Philadelphia); Washington Monument 1815-29 (Baltimore); the Tennessee
  Capitol 1859 (Nashville).

## Gaps / not done

- **Kansas City:** no pre-1882 flat plan in open sources found. The 1855 Town of Kansas plat
  (Missouri Valley Special Collections, KC Public Library) was not checked.
- **Portland, Omaha, Minneapolis, St Paul:** the earliest flat plans are 1852-1889, and the
  georeferenced ones are 1885-1912.
- About 900 UChicago and about 250 NYPL Allmaps hits are still without titles.
- No row uses Sanborn sheets. Sanborn key maps were seen in Allmaps (Boston, Chicago) but skipped.
