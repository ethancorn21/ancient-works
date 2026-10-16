# Book plans not on the map: location pass

Scope: the 413 rows in matches.jsonl from six books (Thomas 1894 was done by another agent). Output: `books_locate.jsonl`, one line per row, same `row_id`s. Nothing under `ancient-works/` was changed.

Every located row has a verbatim OCR quote (`quote`), a lookup chain (`notes`, starting `chain:`) and an uncertainty radius in metres. No coordinate was typed by hand from memory. Each one comes from us_sites.tsv, the Wikipedia NRHP county lists (site coordinates), Wikidata P625, BLM CadNSDI PLSS section geometry, or Nominatim (a town centre plus a distance and bearing stated in the book).

## Totals

| | rows | distinct sites |
|---|---|---|
| existing_site (already in us_sites.tsv) | 48 | 25 site keys -> 20 us_sites ids |
| wikidata (NRHP or Wikipedia point plus a Wikidata item) | 20 | 12 |
| plss (BLM section / quarter-section) | 75 | 53 |
| place_distance (town + stated miles and bearing, or NRHP point with no Wikidata item) | 238 | 153 |
| not_located | 32 | - |
| **total** | **413** | **243 located** |

- Rows carrying a Wikidata QID: 46, covering 24 distinct QIDs.
  - 12 QIDs come with existing us_sites ids (Etowah, Aztalan, Mound City and others).
  - 12 QIDs were found here for works not on the map, across 22 rows: Wolf Plains Q8029881, Barnesville Petroglyph Q4861584, Fortified Hill Works Q5472646, Flint Ridge State Memorial Q5459552, Shawnee Lookout Q7491536, Cross Mound Q14716397, Cedar-Bank Works Q16956235, Colerain Works Q5144607, Old Stone Fort Q7085111, Mount Royal Q6923321, Ganondagan Q5521462 and Junction Group Q16997951. The Junction Group QID is attached to a place_distance row, because that item has no coordinates.
- Located rows: 381. Radius 1 km or less: 85 rows (48 sites). Radius 3 km or less: 307 rows (189 sites). Over 3 km: 74 rows.
- Destroyed per source: 6 rows. Chillicothe east group (Fowke: "entirely disappeared"), Circleville (S&D: "almost entirely destroyed"), Cincinnati (Whittlesey: "now obliterated"), Milwaukee First Ward (Lapham: "formerly two lizard mounds"), and S&D XLIII No. 8 in Richland Co. WI (road; not located). The Junction Group is mostly destroyed according to Wikipedia, but the book does not say so, so that row is not flagged.

## Per book

| book | rows | existing | wikidata | plss | place_distance | not located |
|---|---|---|---|---|---|---|
| squier_davis_1848 | 132 | 20 | 8 | 12 | 80 | 12 |
| lapham_1855 | 113 | 5 | 0 | 61 | 45 | 2 |
| fowke_1902 | 65 | 17 | 7 | 0 | 38 | 3 |
| squier_1851 | 55 | 0 | 1 | 0 | 40 | 14 |
| mills_1914 | 30 | 5 | 4 | 0 | 20 | 1 |
| whittlesey_1850 | 18 | 1 | 0 | 2 | 15 | 0 |

Notes:
- Fowke 1902 and Mills 1914 mostly reprint S&D plates. Those rows share S&D site keys, so one site often carries 3 rows (S&D + Fowke + Mills).
- Lapham gives section/township/range for most works, so PLSS dominates there. Radius is the half-diagonal of the section, about 1.15 km; a quarter-section is about 0.6 km.
- Squier 1851 (NY) gives town + miles. Its 14 not-located rows are non-US comparatives (Tulum, Bury Wood, Knockferral, Banwell, Roman camp, Mexico/Peru), generic Creek town diagrams, and one relic figure.

## Method details

- `town` rule: radius = max(1.6 km, 20% of the stated distance). With no bearing, radius = distance + 1.6 km. Town only, with no distance: 3 km or a stated larger value. Each Nominatim hit was validated against the state or county, and every display name was checked by eye.
  - Some anchors are "Town of X" (NY/WI civil towns) or Ohio townships. For those, the Nominatim point is the town's label node, which is normally the village; Elbridge, Penfield, Clarence and Fulton were checked against their villages and hamlets.
  - One wrong anchor was found and fixed: "Canandaigua" resolved to the Town of Canandaigua, 5 km SW of the 1851 village (now the City), so it was re-queried as the City.
  - Where the book gives only a town lot or farm (Elbridge lot 81, Pompey lot 3, Macomb, Le Ray/Lockport, Franklin Twp Ross), the radius is the half-diagonal of the town bounding box (7.9-13.9 km).
  - Other non-settlement anchors: Lake Koshkonong and Lake Ripley resolve to CDPs on the lakes, with radii of 7 km and 1.5 km. Pike Lake resolves to the Kettle Moraine Pike Lake Unit, about 0.6 km from the lake centre, with radius 1.5 km.
- `plss`: BLM CadNSDI first-division geometry. Section centre or quarter centre; radius = half-diagonal.
- `nrhp`: coordinates from the Wikipedia "NRHP listings in X County" tables. The QID is taken only if a Wikidata item within 1.5 km shares a name token AND is archaeological (an NRHP refnum or an archaeological description).
  - An earlier pass without the archaeological filter matched Conneaut Works to Conneaut High School and Glenford Fort to Glenford village. Indian Point Fort and Flint Ridge matched park items, and Spruce Hill matched the hill. Those QIDs were dropped.
  - Cedar-Bank Works Q16956235 and Colerain Works Q5144607 were attached by exact name search; those items have no coordinates, so the NRHP point is used.

## Problems and uncertainties (all also in row notes)

- **Panel order assumed (one row could swap with its neighbour; location set is unaffected):**
  - Fowke fig. 54: Conneaut first, then Cleveland 3 mi SE.
  - Fowke fig. 55: Cuyahoga 6 vs 8 mi; both rows share one point with radius 3.5 km.
  - Fowke figs. 57/58: Sheffield Twp, two works sharing one point with radius 5 km.
  - Squier 1851 Pl. VII No. 3 = Penfield mound.
- **Identifications by position only, not stated in a source:**
  - Mills "Butler County Fort, 3 mi below Hamilton" = Fortified Hill Works (NRHP 2.8 mi SSW of Hamilton).
  - Whittlesey "3.5 mi E of Painesville" = Indian Point Fort.
  - Mills Worthington plan = S&D XXIX No. 3 (image not checked).
- **Glenford Fort (Whittlesey):** the text says "five miles north-west of Somerset, Sec. 21 T16 R17". The PLSS cell plots 12 km SW of the NRHP fort and contradicts the bearing. The NRHP point is used, because Mills reprints the plan as "Whitelsey's Map of Glenford Fort".
- **PLSS vs description conflicts:**
  - S&D Little Miami work 7 mi above Xenia: Sec. 24 plots about 6 km from the river, so a wider radius is used.
  - S&D Mississippi plate: T4S R7W (Chickasaw meridian) falls in present Tate Co., but the plate title says Lafayette Co. The township is used as given; the township centre has a 7 km radius.
  - Mount Sylvan (Lafayette Co.) and Choctaw bend (Bolivar Co.) are county centroids only (radius 20-25 km). They count as located but are nearly useless.
  - Lapham Koshkonong: caption reads "T. 5, R. 3"; R. 13 is probable, so the lake centroid is used with a 7 km radius.
  - Lapham Mayville: caption "No. 25 T.12 R.17".
  - Lapham Sauk: row title says T5, plate caption says T10. The plate is used.
- **Captions read from page images, where the OCR text lacked the place:**
  - Mills Piqua and Dayton: the djvu OCR reads "5 Mi." where the image shows 3.
  - Whittlesey Columbus 3 mi SW and Northfield 2 mi W. The Northfield row title wrongly says Jackson County.
- **Whittlesey "3 mi from Newark":** the heading says south, the caption says east. No bearing is used; radius 6.4 km.
- **Squier 1851 "Burrville"** is taken to be the hamlet now called Burrs Mills, Town of Watertown NY (not verified).
- **Toledo work** (S&D right bank / Mills "which existed"): Mills's past tense is not an explicit statement of destruction, so it is not flagged.
- **Nearby existing sites, worth a human look (not merged):**
  - Whittlesey "irregular mound 40 ft high, 1 mi N of Newtown" is 1.4 km from `odd-fellows-cemetery-mound-q7077319`. Likely the same mound, but this rests on the 1 mi N offset only.
  - S&D/Fowke Chillicothe circles and plain mound groups lie about 1.8 km from `story-mound-state-memorial-q18617458` (different works; Story Mound is a single mound).
  - Holder-Wright Works (Dublin), Scioto Township Works I (Barnes/Seal Twp), Burrell Fort (Sheffield) and Indian Hills (Toledo) are named in the notes as NRHP candidates. They were not adopted, because the identification was not confirmed.
- NRHP list fetch for NY Montgomery and Otsego counties hit HTTP 429. Fort Plain rows use Nominatim instead.

## Not located (32)

| book | rows | reason |
|---|---|---|
| S&D | 12 | Fayette Co. KY XIV Nos. 3-4 (county only); XLIII Nos. 5 and 8 (river/county only; No. 8 destroyed per source); altar plans and sections (3); generic figs. (23, 49-type sepulchral group, temple mound); Oregon fig. 58; Clarke Co. TN section |
| Fowke | 3 | elephant pipes (artefact); Miami Co. county map; composite figure of three groups |
| Lapham | 2 | Brookfield ridges (Lapham judges them natural); composite excavations plate IX |
| Mills | 1 | Cuyahoga "Ancient work, area 5 acres" (no place) |
| Squier 1851 | 14 | 7 non-US comparatives, 6 generic Creek diagrams, Fig. 5 relic |

## Reproduce

`scratchpad/research/bl/build/resolve.py` reads `data_*.py` (site specs and row-to-site maps) and writes `books_locate.jsonl`. Delete `site_cache.json` after any change to the resolver logic. The PLSS and geocoder caches are in `bl/cache_plss` and `bl/cache_geo`.
