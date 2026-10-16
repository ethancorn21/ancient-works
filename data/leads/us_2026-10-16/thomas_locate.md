# Thomas 1894 (12th BAE report) - locating unmatched plan rows

Input: `data/books/matches.jsonl`, book `thomas_1894`, status no_candidate / ambiguous / doubtful = **179 rows** (all processed, 179 records in `thomas_locate.jsonl`, same order as matches.jsonl). Nothing under `ancient-works/` was modified.

Every located record carries: a verbatim quote from Thomas (OCR of IA `annualreportofbu1218901891smit`, hyphenation repaired, leaf noted in `notes`), the lookup that turned it into coordinates (GNIS feature id, BLM PLSS id, Wikidata QID + P625, OSM way id, or Nominatim result), and a radius in metres. Sub-figures (sections, burial plans of a mound already placed) inherit their parent's location and say so in `notes`.

## Counts

| method | rows |
|---|---|
| place_distance (gazetteer anchor + Thomas's distance/direction, or named OSM feature) | 96 |
| plss (BLM PLSS section / quarter / township from Thomas's legal description) | 43 |
| existing_site (already in Resurface site list) | 14 |
| wikidata (named archaeological site with P625) | 13 |
| not_located | 13 |

Radius, located rows (166): **<=1 km: 87**, 1-3 km: 50, >3 km: 29. Of the >3 km rows, 7 are regional maps or artifacts (`kind`), leaving 22 true site plans with a radius over 3 km (mostly "N miles from town" with no direction, or river-mile distances).

Rows with a Wikidata QID: 30 (13 as method wikidata, the rest as supporting ids on existing-site or place_distance rows, incl. some QIDs without coordinates). Rows matched to an existing Resurface site: 14 (Newark x4, High Bank x3, Hopeton x2, Emerald Mound/Selsertown x2, Criel x2, Cahokia as regional-map reference x1).

`kind` flag: 6 `regional_map` (located only to a reference centre, large radius), 6 `not_a_plan` (artifact, earthquake-damage diagram, fireplace, "battle ground" diagram, French fort).

## Not located (13)

| row | why |
|---|---|
| n0132_1 Sue Coulee group, WI | coulee not in GNIS/OSM; no distance in text |
| n0208_1 stone graves on bluff, Randolph IL | "road from Glasgow to Prairie du Rocher"; Glasgow not found |
| n0229_1 Round Pond mounds, Union IL | Round Pond not in GNIS/OSM |
| n0237_1 Ben Proffer mound, Cape Girardeau MO | Bird creek mouth not in GNIS/OSM |
| n0242_1 Peter Bess, Bollinger MO | anchored on Lakeville, not found |
| n0244_1 Lakeville settlement, Stoddard MO | Lakeville not found |
| n0245_1 County line settlement, Stoddard MO | needs 1890 Dexter-Malden road trace |
| n0266_1 Power's fort, Butler MO | no distance; no coordinates in Wikidata |
| n0294_1 Sherman mound, Mississippi AR | Wikidata Q55315979 exists but has no coordinates; Young's lake / Pitman's landing not found |
| n0297_1 Bradley mounds, Crittenden AR | Oldham (Bradley's landing) not found |
| n0309_2 Barney mound, Phillips AR | no locality in text |
| n0312_1 Old French fort, Desha AR | no distance; European work, not a mound plan |
| n0626_1 Baum works square, Ross OH | no locality in text; absent from GNIS, OSM, Wikidata, en.wikipedia |

The six Missouri/Arkansas misses are all historical place names (post offices, landings, lakes) missing from current GNIS and OSM. A historical-topo or 1890s county-map lookup would likely place most of them.

## Problems and judgement calls

- **Thomas's directions are sometimes wrong.** Menard mounds (n0301_1): Thomas says 7 mi west of Arkansas Post; the Menard-Hodges site (Q4290309) is ~8 km ESE. The row was placed by name, not by his direction.
- **OCR/print township numbers.** Glenford stone fort (n0601_1): "T. 7" read as T17N, which is where BLM puts Glenford. Linn's place (n0225_1): OCR "T.15S" read as T13S, because T15S is in Alexander Co. and Thomas's own cross-reference fits T13S. Each fix is stated in its record.
- **Ohio US Military District (Knox Co.)**: Thomas's "Sec. 1" is a quarter-township whose BLM label could not be mapped with certainty, so the Staats mound rows (n0558_1, n0561_1) use the whole township (radius 5.5 km).
- **Caption/text conflicts in Thomas**: Hale's place (n0217_1) is captioned Jackson Co., but the text puts it in Alexander Co. by Mill Creek. Meyers mounds (n0264_1) are captioned Scott Co., but the text's "midway Cairo-Charleston road" falls in Mississippi Co. Records follow the text and widen the radius.
- **Wikidata coordinates not trusted blindly.** Tallassee (Cherokee town) Q7680081 sits 6 km downstream of where Thomas puts it and copies the modern community's coordinates; it was not used. Carson Mounds Q19864530, Sherman Mound Q55315979 and Hopeton Q5899962 have no P625.
- **Hollywood mound, GA (n0413_1, n0418_1)**: the flag station is in no gazetteer. Position rebuilt from Thomas's three distances along the modern Norfolk Southern line (OSM; assumed but unverified to follow the 1891 Georgia Central route) and checked against Silver Bluff (4.7 mi vs his 5). Radius 4 km. A straight-line interpolation landed in South Carolina and was rejected.
- **Seal township works (n0633_1)** anchored on GNIS Sargents (Sargent heirs' land in Thomas); Barnes Cemetery (OSM) adjoins it. The Sargent-family link is assumed, so the radius is 2.5 km.
- **Mount Vernon cemetery mound (n0563_1)**: "the cemetery at Mount Vernon" taken as Mound View Cemetery (named for the mound). This is an inference from the name.
- **Hopeton square vs circle**: OSM's two polygons are unlabelled, so both rows use the site centroid (r 350 m).
- **OSM/NPS polygon coordinates**: the component coordinates for Newark (Observatory and Great circles), High Bank (circle and octagon) and Liberty (small circle and square) are centroids of OSM `historic=archaeological_site` ways tagged `source=NPS`. The way ids are in `notes`. The method enum has no slot for this evidence type, so these rows are filed as existing_site or place_distance.
- WDQS and the Wikidata API rate-limit heavily (about 1 query a minute). Name lookups were done in throttled batches, and coordinate searches used bulk per-state downloads.

## Notable identifications

- Thomas's Souris river "elongate mounds" (n0090_1, n0091_1) = **Linear Mounds National Historic Site**, Manitoba (Q23693532).
- The Little Tennessee groups are Overhill Cherokee towns now under Tellico Lake: Toco = **Toqua** (Q7825216), Bacon/McGee = **Chota** (Q5105371), Latimore/McSpaddin = **Citico** (Q5122463), McMurray = Chilhowee (Q5098913), Lenoir's island = **Bussell Island** (Q1017693).
- Beckwith's fort / Pin Hook ridge = **Towosahgy** (Q7830296). Selsertown = **Emerald Mound** (existing site).
- Union Co. MS group (n0351_1) is probably Ingomar Mounds, placed by PLSS. The Taylor mounds (n0313_1) sit 0.8 km from Q16901341 "Taylor Log House and Site" (NRHP), which is a weak name match. Both are recorded only as notes, not as matches.
- Several "plans" are really regional maps (W Madison Co. IL around Cahokia, the Little Tennessee valley, Timberlake's 1762 map, the Kanawha valley below Charleston, SW Crawford Co. WI, Kingsport graves). They are flagged `regional_map`.

## Reproduction

Scripts are in `scratchpad/thomas/`: `dec1.py`-`dec5.py` (per-row decisions: quote regex, anchor, offset, radius, notes), `resolve.py` (quote extraction, GNIS/PLSS/Nominatim/Wikidata resolution, nearby-site cross-check), `build.py` (resolves all 179 rows, checks coverage, writes the jsonl). HTTP responses are cached in `httpcache.json`.
