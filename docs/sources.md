# Open sources for LiDAR, historical depictions and imagery

Ported from the cloud branch `claude/amazing-carson-c779pq` on 2026-10-10 and trimmed. Two rules from Ethan apply to everything
below: **no USGS topographic quads** (they show roads and fields, not the works), and **no plain survey map or aerial younger than
150 years** (age is the point: how little the works changed). Plans and drawings of the works are not surveys and stay whatever
their age. Rows whose code was not ported say so; `sanborn.py`, `sentinel.py`, `harvest.py`, `inventory.py`, `fetch_plates.py`
and the USGS-topo half of `topo.py` stayed on the branch.

Only sources that answered a real request are listed as working. "Checked" says from where:

- **Mac**: the earlier sessions, open network.
- **Cloud 2026-10-10**: a cloud session whose network allowed only AWS and Google Cloud storage buckets, GitHub and the package
  registries (every other host answered 403 on CONNECT). It is why most of the working rows below are S3 buckets, and why the
  agency web services the pipeline was first built on (3DEP ImageServer, TNM API, Esri) are *not* verified there. They still work on the Mac.

"CORS" = the browser can draw the tiles directly; without it the local server has to fetch and cache them (WebGL needs CORS for raster tiles).

## 1. LiDAR and elevation

| Area | Source | Access | Used by | Checked / notes |
|---|---|---|---|---|
| US | **USGS 3DEP 1 m DEM tiles**, `s3://prd-tnm/StagedProducts/Elevation/1m/Projects/<project>/TIFF/USGS_1M_<utm zone>_x<E>y<N>_<project>.tif` (968 project folders) | 10 km GeoTIFF tiles, 512 px blocks, LZW, overviews: window reads by HTTP range. `x` = west edge / 10 km, `y` = **north** edge / 10 km (not the south), 6 m overlap between tiles | `pipeline/usgs.py`; `aw.fetch_dem` falls back to it, `AW_DEM=s3` forces it | Cloud 2026-10-10. A 2 km box reads in 3-5 s. Fort Hill rebuilt from it matches the relief already on the page (pixel correlation 0.985) |
| US | **Which LiDAR exists where**: `.../Elevation/metadata/WESM.csv` (3,289 work units: collection dates, quality level) and the extent of each project's point cloud (`ept.json` on `usgs-lidar-public`, EPSG:3857) | CSV + 2,289 small JSON files; indexed once into `data/raw/usgs/` | `usgs.lidar_projects()` | Cloud 2026-10-10 |
| US | **1/3 arc-second DEM**, `.../Elevation/13/TIFF/current/n40w084/USGS_13_n40w084.tif` (name = north / west corner) | tiled, LZW: window reads | fallback in `usgs.read_dem` | Cloud 2026-10-10. 0.6 s for a 2 km box; against the 1 m DEM it is within 1.0 m rms, i.e. too coarse for earthworks |
| US | **3DEP point clouds** (EPT), `s3://usgs-lidar-public/<work unit>/ept.json`, `ept-hierarchy/<D-X-Y-Z>.json`, `ept-data/<D-X-Y-Z>.laz` (EPSG:3857, Z in the survey's own units: WESM `vert_crs` 5703 = metres, 6360 = US survey feet, 8228 = feet) | octree of LAZ nodes, depth 11-12 is ~1 m on the ground | `pipeline/ept.py`, called by `usgs.read_dem` for the cells the 1 m DEM tiles do not cover (before the 10 m fallback) | Cloud 2026-10-10. **Rescued Moundville** (the 2023 1 m DEM stops short of the box; the 2016 ADECA point cloud fills the other 41%, with no visible seam), **Bottle Creek, Mound Bottom, Pharr Mounds**, which had only the 10 m DEM. On the part of Moundville both cover, the point-cloud grid differs from the 1 m DEM by a median 0.7 mm (MAD 1.1 cm). Older point-cloud folders are named `USGS_LPC_<work unit>_LAS_<year>`; `usgs.wesm_row` maps them to WESM. Work units WESM does not describe (TN_Nashville_2011, MN_FullState) are skipped: no vertical units. A 1 km box reads ~130 nodes (~50 MB), a 2.4 km box with a big gap ~1,000 |
| Scotland | **Scottish Government, Historic Environment Scotland and Orkney LiDAR**, `s3://srsp-open-data/lidar/<set>/dtm/27700/gridded/` (eu-west-2): HES 25 cm and 50 cm, National LiDAR Programme 50 cm (1 km tiles), Orkney 2023 50 cm, phases 1-6 (1 m and 50 cm) | ready-made DTM GeoTIFFs in British National Grid. Open Government Licence | `pipeline/lidar_scot.py` | Cloud 2026-10-10: Ring of Brodgar (Orkney 2023) read in 21 s. **Tiles are clipped to where there is data** (`NN80_1M_DTM_PHASE1.tif` is 5 km by 3 km, not its 10 km square), so the real extent is read from each header |
| Europe | **open-lidar-data**, `s3://open-lidar-data/data/<CC>/<agency>/<survey>/` (eu-central-1): COPC point clouds with a tile index (`shp/`) per survey. England (`UK/DEFRA`, Environment Agency surveys 2005-2022), Netherlands (AHN4), Denmark (DHM 2018-22), Spain (CNIG PNOA), Estonia, Latvia, Lithuania, Poland, Slovenia, Switzerland (swissSURFACE3D), Wallonia (Hainaut), Saxony, France (IGN, partial), Ireland (Dublin 2015 only), Finland, Sweden, Luxembourg. Licences differ by survey (`license/` in each) | HTTP range reads of only the octree nodes in the box (laspy); ground returns (class 2) gridded and reprojected | `pipeline/lidar_pc.py` | Cloud 2026-10-10: point clouds read and gridded at Avebury, Badbury Rings, Danebury (England), Fyrkat, Jelling (Denmark) and others; Spain's, Estonia's, Switzerland's, Poland's, Slovenia's and Belgium's tile indexes confirmed to cover test sites but not every one read. **Coverage is patchy**: Denmark, Netherlands, Spain, Estonia, Lithuania, Latvia, Slovenia, Hainaut are national or near; England has the surveys the EA published (Avebury yes, Stonehenge, Cissbury, Mam Tor no); Ireland only Dublin; France, Poland, Sweden only where the mirror holds a tile. A survey whose ground returns reach under 30% of the 1 m cells is refused (northern Spain, forest: blotches, not relief) |
| England, Wales, Scotland | **NLS LiDAR hillshades**, `https://mapseries-tilesets.s3.amazonaws.com/lidar/england/{z}/{x}/{y}.png` (EA composite, all England), `lidar/wales/` (Natural Resources Wales; tileset bounds cover all Wales), `lidar/rgb/phase1` ... `phase6` and `hebrides` (Scottish Public Sector LiDAR), `lidar/sherwood/dtm` and `dsm` (zoom to 19) | XYZ PNG, Web Mercator, zoom 1-18 (Scotland 16), colour-tinted hillshade: **images, not heights** (no block diagram can be made from them) | not used: dropped from `nls.py` (the page has no slot for a hillshade, and a site without heights gets no block diagram) | Cloud 2026-10-10: tiles fetched and looked at at Avebury (England: the henge bank and ditch are crisp), a Caernarfonshire farm (Wales: field boundaries, lynchets), Kilmartin (Scotland phase 1). **The only LiDAR-derived source reachable for Wales.** Also `slrm/SLRM_COG_16Bit_ST46NW.tif` (71 MB simplified local relief model COG) |
| global | Copernicus DEM 30 m (`copernicus-dem-30m`, `-90m`), Mapzen terrain tiles (`elevation-tiles-prod`), ESA WorldCover | S3 | nothing | Cloud 2026-10-10: listings; a terrain tile PNG fetched. Context only |
| US states | Indiana `giselevationingov` (LAS, COPC, DEM), Kentucky `kyfromabove` (DEM COGs, point cloud, contours), New Jersey `njogis-elevation`, Vermont `vtopendata-prd`, Colorado `colorado-public-elevation-data`, NOAA coastal `noaa-nos-coastal-lidar-pds` | S3 | nothing | Cloud 2026-10-10: listings only. These are the same surveys 3DEP republishes, sometimes at finer resolution |
| US | 3DEP ImageServer `elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage` | export in EPSG:3857 | `aw.fetch_dem` (default) | Mac. Slow and 5xx-prone; **blocked in the cloud** |
| England, Netherlands, France | EA 1 m composite DTM (WCS), AHN `dtm_05m` (PDOK WCS), IGN LiDAR HD MNT (Geoplateforme WMS-R) | EPSG:27700, 28992, 2154, reprojected to 3857 | `pipeline/dem_sources.py` (live relief tiles and site builds) | Mac. **Blocked in the cloud**; there, England, the Netherlands and France are read from the open-lidar-data point clouds above (`lidar_pc.py`), and Scotland and the other countries are served only by `dem_sources.STATIC` (S3, pre-built sites, not live tiles) |

## 2. Historical maps

| Area | Layer | Years | Service | Projection | CORS | Used by / notes |
|---|---|---|---|---|---|---|
| US | **USGS Historical Topographic Maps** | 1879-2006, 186,060 scans | the catalogue `s3://prd-tnm/StagedProducts/Maps/Metadata/historicaltopo.zip` (extent, year, scale, link of every scan) and the GeoTIFFs under `.../Maps/HistoricalTopo/GeoTIFF/<state>/`. JPEG-compressed, 8-26 MB each, NAD27 polyconic or Lambert | per quad | n/a | **Not used (Ethan: no USGS topos; all are under 150 years).** The branch's `topo.py` (cloud 2026-10-10) replaced the TNM API. `--all-editions` keeps one edition per survey (reprints within 5 years are skipped). Checked against the earlier output: Fort Hill 1915 correlation 0.9966 and **0 px offset**; the 1961 polyconic and 1992 Lambert sheets of Hopeton register within 1 px (2 m). The NAD27 shift needs `us_noaa_conus.tif` (on the branch, not ported); without it PROJ is ±10 m off. Most quads do not draw the works: context, not depictions |
| Britain | **National Library of Scotland map tiles**, `https://mapseries-tilesets.s3.amazonaws.com/<set>/{z}/{x}/{y}.png` (95 top-level sets and 251 under `os/`) | | free XYZ PNG, Web Mercator, zoom to 17 (aerial 16) | 3857 | **no** | `pipeline/nls.py` (cloud 2026-10-10; fetched and looked at). **Ported with only the 150-year-old families: Roy, the six-inch 1st editions of England and Wales, Scotland and Ireland, and Ireland's c. 1860 printing.** The 2nd editions, both 25-inch series (edition only inferred; the Wiltshire set has coloured roads, so it is later) and everything after are left out. England and Wales six-inch, 1st edition (`os/six-inch-<county>`; read off the maps, see below), 2nd edition 1888-1913 (`os/6inchsecond`; tiles found in England and Scotland), 25-inch 1st and 2nd (`25_inch/<county>`, `<county>2nd`), Scotland six-inch 1st (`os/6inchfirst`, 1843-82), Ireland six-inch 1st (`os/<county>`, surveyed 1829-42; it labels the Newgrange passage mound "Moat", the 2nd edition "Newgrange Tumulus"), a later printing (`os/<county>1`, c. 1860) and 2nd edition (`os/<county>_2nd`). Also on the bucket, not used yet: one-inch (`1inch_2nd_ed`...), Roy Military Survey of Scotland, WWI trench maps, estate plans, town plans, the 1:1,250 series, Bartholomew, geological maps. **Corrects the earlier note** that England's six-inch needs a MapTiler key: the tiles are on S3 and free, one set per county (Wiltshire, Dorset and Kent checked) |
| Britain | **More NLS sets** (listing 2026-10-10; the first four are in `nls.py`) | | | | | **`roy/lowlands`, `roy/highlands`**: Roy's Military Survey of Scotland 1747-55, zoom 5-14, looked at near Dunadd; **`scotland_2500_singles`, `scotland_2500_doubles`**: OS 25-inch Scotland (dates inferred, 1892-1949), zoom 18; **`os/10k_1973`**: 1:10,000 map of 1973, zoom 16; **`air-photos-1250`**: 1:1,250 air-photo mosaic of parts of England, zoom 20 (no tile at Avebury; dates inferred). **Seen in the listing, not used**: `towns/*` (Scottish town plans 1840s-90s: aberdeen ... edinburgh1849/1876/1893 ...), `town_england/*` (Bath, Bristol, Salisbury, Swindon ...), `goad/*` (fire-insurance plans), `urbhist/*`, `county/*` (county maps 1771-1831: chester, cumberland, derbyshire, durham, lancashire, lincolnshire, nottinghamshire, westmorland, yorkshire), `estates/*`, `popular`, `newpopular` (one-inch Popular editions), `land_uti_eng`, `land-utilisation-scotland-six-inch` (1930s land use), `1inch_*`, `quarter-inch-*`, `half-inch-*`, `os/1250_*`, `os/2500_1968`..., `os/25000`, `os/britain10knatgrid`, `london_1890s`, `london_1940s`, `trench`, `bartholomew*`, `ireland/bartholomew`. **`os/six-inch-<county>V`** are second scans of the same sheets (darker paper), so `nls.py` leaves them out. `os/6inchfirst27700` is the six-inch first edition in British National Grid, not Web Mercator |
| Britain | NLS terms | | | | | NLS says its tiles are free for personal and research use with credit, and CC-BY on many layers; a third party quotes "personal purposes" for the S3 tiles. Private use here is fine; **check each layer's licence in NLS's Georeferenced Maps viewer before anything public** |
| US towns | **Sanborn fire-insurance maps** (Library of Congress, public domain) | 1884-1961 for Ohio's earthwork towns | `s3://loc-sanborn-maps/maps-by-state/<State>/data/<item>_<sheet>.jpg` with `metadata.csv` (50,600 maps, 440,048 JPEGs; Ohio 2,412) | not georeferenced | n/a | **Not used (under 150 years; not georeferenced).** The branch's `sanborn.py` (cloud 2026-10-10: the 1884 Marietta key sheet shows "Sacra Via", the Public Park and the cemetery). Marietta 9 editions, Newark 8, Chillicothe 8, Circleville 8, Portsmouth 9. Reference images beside a site, not overlays |
| France | Cassini map | 1750s-1790s | Geoplateforme WMTS `BNF-IGNF_GEOGRAPHICALGRIDSYSTEMS.CASSINI`, PNG, zoom 6-14 | 3857 | yes | `pipeline/depict.py` (Mac); open (IGN) |
| France | Etat-major map | 1820-1866 | WMTS `GEOGRAPHICALGRIDSYSTEMS.ETATMAJOR40`, JPEG, zoom 6-15 | 3857 | yes | `pipeline/depict.py` (Mac); open (IGN) |
| France | SCAN50 | 1950 | WMTS `GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN50.1950`, JPEG | 3857 | yes | Mac |
| Netherlands | Topotijdreis (incl. TMK 1850, yearly sheets 1815-2015) | 1815-2015 | `https://tiles.arcgis.com/tiles/nSZVuSZjHpEZZbRo/arcgis/rest/services/Historische_tijdreis_<year>/MapServer` | **28992 (RD)** | ? | `pipeline/depict.py` reprojects it (Mac); Esri NL / Kadaster |

A site near a county line takes every county set that has a tile there. **A neighbouring county's sheet margin is blank paper** (Birdoswald: the Northumberland six-inch sheet covers the Cumberland site with cream paper), so `nls.py` skips a set whose part of the box has under 0.5% ink and puts the first remaining set on top.
Edition labels for the NLS sets were **read off the maps** (tiles side by side at Amesbury and Newgrange) and the NLS county pages seen in search results,
not from NLS's own layer list, which the cloud could not open. `pipeline/nls.py` marks those entries "inferred".

## 3. Historic aerial photographs

| Area | Layer | Years | Service | Georeferenced | Used by / notes |
|---|---|---|---|---|---|
| Britain | **OS air-photo mosaics** (about 20% of Britain at 1:10,560) | 1944-1950 | NLS tiles `air-photos-10560` (England, Wales) and `air-photo` (Scotland), PNG, zoom to 16 | yes (tiles) | not used (under 150 years); the cloud session looked at Stonehenge's Cursus, Avenue and the 1940s fields |
| France | Historic orthophotos | 1950-1965 | WMTS `ORTHOIMAGERY.ORTHOPHOTOS.1950-1965`, style `BDORTHOHISTORIQUE`, PNG, zoom 0-18 | yes | in `depict.py` LAYERS but not built (under 150 years); open (IGN) |
| Iowa | USDA aerials, statewide | 1936-1941 | `https://programs.iowadnr.gov/geospatial/rest/services/reference/imagery1930x/MapServer/tile/{z}/{y}/{x}` (cached, zoom 0-23) | yes | Mac; Iowa DNR / ISU GIS lab; covers Effigy Mounds and the NE Iowa mound groups; CORS (echoes Origin); in `depict.py` LAYERS but not built (under 150 years) |
| Indiana | **Historic frames**, `s3://gisimageryingov/archive/` (us-east-2): `indot/contactprints/<County Co. year>/` 1936-2001 (412 county-year folders, JPEG, 3 MB) and `igws/` 39,920 frames 1937-81 (flat names like `BFR-1G-003.jpg`; `igws/dir_tree.txt` is a UTF-16 listing that says which county and year each belongs to; Randolph 1950 is 251 frames) | 1936-2001 | listing and fetch | **no**: single frames, each needs control points like a plate | Cloud 2026-10-10 (fetched 30 of the 251 Randolph 1950 frames as thumbnails; Winchester was not in the ones sampled). The best route to a 1930s-50s image of the Fudge Site, not done |
| Indiana | Georeferenced: six county COGs 1976-79 (1 ft; Clay, Daviess, Greene, Knox, Sullivan, Vigo) in `imageryoptimized/statewide/1970/`; the statewide 1998 DOQQ in `usgs/1998_doqq/`; orthophoto years 2005, 2011-2026 in `imageryoptimized/statewide/<year>/SPE|SPW/<res>/` (5000 ft tiles named `in2022_02201120_06.tif` with a `.tfw`; 3-inch and 6-inch) | | S3 COGs, CC0 | yes | Cloud 2026-10-10: listings. Not integrated (state-plane tile lookup to write) |
| New Jersey | `s3://njogis-imagery/<year>/` 1930, 1970, 1977, 1995, 2002, 2007, 2012, 2015, 2020 | | COG tiles | yes (1930 about 2 m) | Cloud 2026-10-10: listings; a research pass fetched the 1930 grid and a tile |
| US | More states (Wisconsin WHAIFinder, Illinois ILHAP and 1939 county mosaics, Pennsylvania 1937-42, Tennessee county orthos 1997-2006 on Source Cooperative, Arkansas 1980-86, NARA index sheets): the branch's `docs/research/us_aerials.md` (not ported: all under 150 years). 14 entries were fetched from the cloud, 50 are search results only: **test the endpoints from the Mac** | | | | |

## 4. Modern imagery

| Area | Source | Notes |
|---|---|---|
| world | Esri World Imagery tiles, `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}` | what the page draws for "Aerial photograph" (in the browser, so not affected by the cloud's block) |
| US | USGS imagery export `https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/export` | Mac; saved as `imagery.jpg` by `build_site.py` (the page does not display that file). Blocked in the cloud, so sites built there have none |
| US states | Indiana orthophotos 2005-2026 (to 3 inch), Kentucky `kyfromabove/imagery/orthos`, New Jersey, Vermont `vtopendata-prd/Imagery`, Colorado | cloud: listings |
| world | **Sentinel-2 L2A COGs** `s3://sentinel-cogs/sentinel-s2-l2a-cogs/<UTM zone>/<latitude band>/<100 km square>/<year>/<month>/<scene>/` (TCI.tif 8-bit true colour at 10 m, SCL.tif scene classification at 20 m, 2016 to the present, ~20 scenes a month per tile) | **Not used** (modern, 10 m: the page's Esri aerial tiles are finer everywhere). The branch's `sentinel.py` wrote `sentinel2.webp` (kind `aerial`) for every site: the clearest June-August scene of the latest finished summer, chosen by the share of clear pixels *inside the site box* (SCL), tile by tile (the home tile, then the tiles 8 km either side: swath edges leave no-data corners). Cloud-optimised: a 2 km box is a few range requests, ~8 s a site. Tiles are filed under the band of their centre, so a point at 39.9 N is in tile `17TNE` (the code tries the neighbouring bands). 10 m pixels do not show earthworks, but at Avebury the henge shows as a crop mark; they give the land cover where the page's own Esri tiles are not reachable. 112 of 114 sites got one on the first pass, all 114 after the neighbouring-tile fallback. Contains modified Copernicus Sentinel data (ESA) |
| US | NAIP (`naip-analytic`, `naip-visualization`), Landsat (`usgs-landsat`) | **requester pays**: 403 without AWS credentials |

## 5. Scanned books, plates and survey plans

`docs/research/plates.md` (the JSON twin stayed on the branch): 37 entries, 136 identifiers (Internet Archive, Biodiversity Heritage Library, Library of Congress,
Smithsonian, Gutenberg, Wikimedia Commons) and the **full plate index of Squier & Davis 1848** (48 plates, 91 plate/figure rows, with county and book page).
Every identifier was seen in a search result; none could be fetched from the cloud (archive.org, loc.gov and the rest are blocked there).
The index gives each plate's page in the book; the leaf on the Internet Archive scan is derived as `leaf = book page + 46 + 2 * (plate - 1)`,
which reproduces all six leaves already in this project (n68, n126, n129, n161, n169, n203). The other 43 are derived, so spot-check each scan before fitting it.
The branch's `fetch_plates.py` (untested, written where archive.org was blocked) was not ported: plates come in through `pipeline/commons.py` and the books pipeline on the Mac.
Plates not yet on the page, by site: VI Fortified Hill, VII Fort Ancient, X (Ross Co.), XVIII Cedar Bank, XIX Mound City, XXII Junction and Blackwater groups,
XXIII Dunlap's Works and Wolf Plains, XXVII-XXVIII Portsmouth, XXXV Serpent Mound, XXXVI Alligator Mound and the effigies, XXXVII Wateree (South Carolina),
XXXVIII-XXXIX the Etowah and Mississippi works, XL-XLIV Wisconsin (Dane, Rock River), XLV Marietta's Great Mound.

## 6. Hosts the cloud session could not reach

The proxy answered 403 to CONNECT for these, so anything from them is unverified there. Allowing them (environment settings, Network access, Allowed domains) is
what unlocks the rest of the plan:

| Host | Unlocks |
|---|---|
| `archive.org` and `*.archive.org` | the plate scans (Squier & Davis, Lapham, Thomas, Fowke, Mills' atlas ...) |
| `commons.wikimedia.org`, `upload.wikimedia.org`, `en.wikipedia.org`, `query.wikidata.org` | plate scans organised by plate; coordinates for the catalogue |
| `www.loc.gov`, `tile.loc.gov` | maps, HABS/HAER, Sanborn IIIF tiles |
| `elevation.nationalmap.gov`, `basemap.nationalmap.gov`, `tnmaccess.nationalmap.gov`, `earthexplorer.usgs.gov` | the pipeline's original DEM, imagery and topo sources; 1930s-80s frames |
| `data.geopf.fr`, `remonterletemps.ign.fr`, `service.pdok.nl`, `environment.data.gov.uk` | France (LiDAR HD, 1950-65 aerials, Cassini), the Netherlands, England's EA composite DTM |
| `programs.iowadnr.gov`, `tiles.arcgis.com` | Iowa's 1930s aerials, Dutch Topotijdreis |
| `www.davidrumsey.com`, `babel.hathitrust.org`, `digitalcollections.nypl.org`, `www.biodiversitylibrary.org` | scanned atlases and books |
| `overpass-api.de` | the road/building/water masks `aw.osm_ways` fetches |

## 7. Not available (or not free)

- **Ohio historic aerials:** no free statewide georeferenced mosaic found. County fragments only (Cuyahoga 1937-38 composite via Baldwin Wallace; Stark 1934 not georeferenced).
  ODOT's archive is a KML of frame locations (500,000+ frames from 1946), not a mosaic. Vintage Aerial sells 1940s-2000s mosaics (commercial). **Indiana is the exception**: see section 3.
- **USGS EarthExplorer single frames (1930s+):** free with a USGS account, but frames are not georeferenced; each would need placing by control points, like a plate. Flagship sites only.
- **UK aerial archives (Historic England, NCAP, Britain from Above):** view-only or licensed; skipped. (The OS 1944-50 mosaics above are the free exception.)
- Pennsylvania 1937-42 (Penn Pilot): frames, no confirmed mosaic service. Delaware 1937 has an ImageServer but few earthworks.
- **No LiDAR on any reachable host:** Ireland (outside Dublin), Wales, Northern Ireland, most of England's hillforts (the EA composite DTM is on `environment.data.gov.uk`), France outside the sample, Sweden's mound sites. The branch's `inventory.json` said which sites (not ported; `dem_sources` decides at build time).

## 8. Coordinates and place names (used to check where a site really is)

| Source | Access | Notes |
|---|---|---|
| **GNIS Domestic Names**, `s3://prd-tnm/StagedProducts/GeographicNames/DomesticNames/DomesticNames_<ST>_Text.zip` | one pipe-separated text file per state | Cloud 2026-10-10: 25 states fetched. Names a few summits and populated places ("Nacoochee Indian Mound" as a Summit at (-83.70902, 34.68353) settled that site; "Fort Toulouse (historical)") but most mounds are not in it. |
| **USGS Historical Topographic Maps** | see section 2 | labels such as 'Indian Mound', 'Mound Park', 'Serpent Mound' on quads of 1900-1990 are the best independent check of a US coordinate; read from the rendered quads, not from text |
| **Overture Maps** places, `s3://overturemaps-us-west-2/release/<date>/theme=places/` (parquet) | S3 | reachable, **not used**. Worth trying for the names and points of parks and monuments |
| Wikidata, Wikipedia, GeoNames, OpenStreetMap/Nominatim | | blocked in the cloud session; `data/catalog/sites.jsonl` (Wikidata, from the Mac) is the offline copy |
