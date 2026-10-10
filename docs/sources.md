# Historical depiction sources (checked 2026-10-10)

Only sources that answered a real request are listed as working. "CORS" = the browser can draw the tiles
directly; without it the local server has to fetch and cache them (WebGL needs CORS for raster tiles).

## Working

| Area | Layer | Years | Service | Projection | CORS | Notes |
|---|---|---|---|---|---|---|
| France | Cassini map | 1750s-1790s | Geoplateforme WMTS `BNF-IGNF_GEOGRAPHICALGRIDSYSTEMS.CASSINI`, PNG, zoom 6-14 | 3857 | yes | open (IGN) |
| France | Etat-major map | 1820-1866 | WMTS `GEOGRAPHICALGRIDSYSTEMS.ETATMAJOR40`, JPEG, zoom 6-15 | 3857 | yes | open (IGN) |
| France | Historic orthophotos | 1950-1965 | WMTS `ORTHOIMAGERY.ORTHOPHOTOS.1950-1965`, style `BDORTHOHISTORIQUE`, PNG, zoom 0-18 | 3857 | yes | open (IGN); the sure source of historic aerials |
| France | SCAN50 | 1950 | WMTS `GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN50.1950`, JPEG | 3857 | yes | |
| Great Britain | OS One-inch, 2nd edition (hachured ramparts, "Tumulus", "Camp") | 1890s | `https://mapseries-tilesets.s3.amazonaws.com/1inch_2nd_ed/{z}/{x}/{y}.png`, zoom up to 16 | 3857 | **no** | NLS, re-use CC-BY (NLS); proxy through the server |
| Scotland | OS Six-inch, 1st edition | 1843-1882 | `.../os/6inchfirst/{z}/{x}/{y}.png` | 3857 | no | Scotland only on the free tiles |
| Netherlands | Topotijdreis (incl. TMK 1850, yearly sheets 1815-2015) | 1815-2015 | `https://tiles.arcgis.com/tiles/nSZVuSZjHpEZZbRo/arcgis/rest/services/Historische_tijdreis_<year>/MapServer` | **28992 (RD)** | ? | Esri NL / Kadaster; needs reprojection to 3857 (per-site pre-build or server-side) |
| Iowa | USDA aerials, statewide | 1936-1941 | `https://programs.iowadnr.gov/geospatial/rest/services/reference/imagery1930x/MapServer/tile/{z}/{y}/{x}` (cached, zoom 0-23) | 3857 | yes (echoes Origin) | Iowa DNR / ISU GIS lab; covers Effigy Mounds and the NE Iowa mound groups |
| US | USGS historical topographic quadrangles | 1880s-2000s | TNM Access API `datasets=Historical Topographic Maps`, GeoTIFF on `prd-tnm.s3.amazonaws.com` | per quad | n/a | GeoTIFF exists (no GDAL needed). Most quads do not draw the works: context, not depictions |

## Not available (or not free)

- **Ohio / Indiana historic aerials:** no free statewide georeferenced mosaic found. County fragments only
  (Cuyahoga 1937-38 composite via Baldwin Wallace; Stark 1934 not georeferenced). ODOT archive is a KML of
  frame locations, not a mosaic. Vintage Aerial sells 1940s-2000s mosaics (commercial).
- **USGS EarthExplorer single frames (1930s+):** free with a USGS account, but frames are not georeferenced;
  each would need placing by control points, like a plate. Possible for flagship sites only.
- **England OS Six-inch (1840s-1890s):** NLS serves it behind an API key (MapTiler), not on the free tiles.
  A free MapTiler account would likely unlock it - Ethan's call.
- **UK aerial archives (Historic England, NCAP, Britain from Above):** view-only or licensed; skipped.
- Pennsylvania 1937-42 (Penn Pilot): frames, no confirmed mosaic service. Delaware 1937 has an ImageServer
  but few earthworks.
