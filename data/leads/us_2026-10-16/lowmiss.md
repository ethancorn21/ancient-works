# Lower Mississippi / Tennessee / Arkansas / Texas / Oklahoma sites - more old plans (2026-10-15)

Region: MS, LA, AR, TX, OK, TN, MO mound sites in `us_sites.tsv`. Rows are in `lowmiss.jsonl`: 22 rows = 19 verified
+ 3 likely. Split by use: 11 fit-grade plans/contoured sheets (Brown Fig. 7, Brown Fig. 23, Thruston Fig. 3, Myer Figs.
1-2, Setzler Marksville, USGS Shiloh 1934, Shiloh park map c.1920, USGS Scott 1942, Garland 1952, Baton Rouge West
1953), 2 alternate copies of plans already in the lead (Brown Fig. 16 Winterville, Putnam 1878 fold-out still folded),
1 modern federal plan (Pharr, NPS 1972), 5 USGS 1:62,500 pictogram locators (Marksville, Winterville, Jaketown,
Frogmore, Poverty Point), 3 likely (Tallahatchie manuscript not seen; Caddo and Parkin unlabelled contours). "Verified" = the page or map crop was rendered and looked at, and the caption or label is quoted. Rows already
in `lead_us_mounds.md` (Thomas 1894 Pl. XIV Selsertown, Moore 1908 Blum, Fowke 1928 Marksville, Moore 1913 Poverty
Point Mound A, Moore 1915 Shiloh Fig. 20) are not repeated. Thomas 1894 Pl. X Knapp mounds is already staged in
`web/data/plans.json` (`annualreportofbu1218901891smit_n0318_1`) for Plum Bayou, so it is not repeated either.

Downloads (all untrusted data, outside the repo): `research/lowmiss_dl/` (IA texts, Brown 1926 PDF, LoC crops, USGS
GeoPDFs). Scripts: `research/lowmiss_bin/` (`leaf.py` finds the IA leaf of a caption from `_djvu.xml`;
`geopdf_crop.py` crops a USGS GeoPDF around a lat/lon using the sheet's own LGIDict georeference).

## New sources worth adding to the books pipeline

| source | why | basis |
|---|---|---|
| C. S. Brown 1926, *Archeology of Mississippi* (Miss. Geol. Survey). Full scan of the 1926 original at MDEQ: https://www.mdeq.ms.gov/wp-content/uploads/2017/06/Archaeology-OF-Mississippi.pdf (396 pp., 53.7 MB, text layer present). IA has only the 1973 reprint (`archeologyofmiss1973brow`), lending-restricted. | Plans: Fig. 7 Selsertown (own 1917 survey), Fig. 9 Anna mounds, Fig. 12 Spanish Fort enclosure, Fig. 16 Winterville, Fig. 20 Carson (after Thomas), Fig. 23 Batesville, Fig. 5 Ingomar (after Thomas), Fig. 15 Leland/Avondale (after Thomas) | published 1926 |
| W. E. Myer 1922, "Recent archaeological discoveries in Tennessee", *Art and Archaeology* 14:3 (`sim_art-and-archaeology_1922-09_14_3`) | Pinson ("City of Cisco") full survey plan + citadel detail; also Fig. 7 map of Gordontown (not in our list) | published 1922 |
| G. P. Thruston 1890, *Antiquities of Tennessee* (`antiquitiesoften00thru`; 1897 2nd ed. `antiquitiestenn00thurrich`) | Fig. 3 Lebanon (= Sellars) plan with scale bar; Fig. 2 Sumner County works (Rutherford-Kiser farm near Sandersville - not Castalian Springs); Fig. 9 Savannah TN works (not Shiloh) | published 1890 |
| USGS historical topographic quads (TNM, GeoPDF, already georeferenced) | Label or contour the mounds at Toltec, Marksville, Winterville, Jaketown, Frogmore, Battle Mound, Poverty Point, LSU; Shiloh 1934 special 1:9600 park sheet (LoC) | federal |

## Per site

### Mississippi

- **Batesville Mounds** - FOUND: Brown 1926 Fig. 23, plan with railroad and road (verified). Also checked: USGS Sardis
  1952 1:62,500 (nothing drawn at the site), Thomas 1894, Moore 1908/1911.
- **Emerald Mound** - FOUND: Brown 1926 Fig. 7, Brown's own 1917 survey of the Selsertown platform (verified; Fig. 8 is a
  view). Also checked: Squier & Davis 1848 p. 118 (text only, "the great mound at Seltzertown", no plate), USGS Natchez
  1921 1:48,000 and 1922/1939 1:62,500 (site lies just east of the Natchez quad edge; no adjacent pre-1960 quad in TNM).
- **Winterville** - FOUND: Brown 1926 Fig. 16 (redraw of Moore 1908, clean full page) and USGS Refuge 1939 1:62,500
  'INDIAN MOUNDS' (verified). MHS Publications 1902 lists a donated "crayon sketch of a celebrated Indian mound ...
  near Winterville" (museum accession, unpublished - not a row).
- **Jaketown** - FOUND: USGS Mileston 1940 1:62,500 'INDIAN MOUNDS' (verified, locator only). Checked: Moore 1908 (Wasp
  Lake mounds "less than a mile above Jaketown", described, no plan), Brown 1926 (quotes Moore only).
- **Holly Bluff (Lake George)** - NOTHING drawn found. Moore 1908 pp. 590-591 describes the enclosure and 55-60 ft mound
  ("as determined by a recent survey, we are informed") with no plan; Brown 1926 Fig. 13 is a photograph; no pre-1960
  large-scale USGS quad in TNM (only 1:250,000).
- **Nanih Waiya** - NOTHING drawn found. Halbert 1899 (Publ. Miss. Hist. Soc. 2, pp. 223-234, `publicationsmis06socigoog`)
  text only; Brown 1926 Fig. 6 photograph plus Wailes 1854 manuscript notes quoted (text); Smithsonian Explorations
  1925 (Collins) Fig. 90 and 1928 (Fewkes) Fig. 192 are photographs. TNM: only 1:250,000 quads before 1960.
- **Pocahontas** - NOTHING. Brown 1926 p. 29 describes both mounds (text). USGS Raymond 1934 1:48,000 crop: no symbol.
- **Pharr** - FOUND (modern only): Bohannon 1972, NPS, Fig. 2 'Site map' (mounds A-H, contours, scale; verified) -
  a federal plan from 1966 fieldwork, not a historical drawing; owner's call. Nothing old: Brown 1926 (Agnew's 1868
  list of Lee/Prentiss mounds, text), Thomas 1891 Catalogue, TNM (only 1:250,000 before 1960).
- **Aden** - NOTHING. Brown 1926 (Issaquena Co. groups from E. A. Smith's 1870 notes, text), Moore 1908, USGS Onward 1939
  (no symbol at the point).
- **Civil War Earthworks at Tallahatchie Crossing** - LIKELY only: Wilson/Matz Dec. 1862 manuscript map (NARA RG 77,
  CWMF S9-3; MDAH inventory lists "Confederate fortifications" and a section of "Rebel works on Tallahatchie River
  destroyed by Union forces Decbr. 26th, 1862") - not digitized as far as found. Checked: OR Atlas index (Pl. 67 no. 2
  = Fort Pemberton, viewed; Pl. 135-A, 154 small-scale), LoC map search, USGS Potts Camp 1944 (nothing drawn).

### Louisiana

- **Marksville** - FOUND: Setzler 1933 Proc. USNM 82 Fig. 1 (redraw of Fowke with scale bar), USGS Marksville 1940
  'INDIAN FORTIFICATION / INDIAN MOUNDS' (both verified). Checked: Smithsonian Explorations 1926 (Figs. 243-245 are
  photos), Smithsonian Report 1881 (Williamson, text), Beyer (LHS) - nothing.
- **Poverty Point** - FOUND: USGS Mitchiner 1959 1:62,500 'Poverty Pt.' / 'Indian Mounds' with Mound A contoured
  (verified, federal). Checked: Fowke 1928 Fig. 6 "Mound group north of Delhi" (Neil farm, Bayou Macon, 8 mounds,
  hematite plummets and baked-clay objects - Poverty Point-culture debris, but location "17 miles north of Delhi" and the
  8-mound layout do not match Poverty Point itself; diagram "not made to scale"; NOT a row - possibly a nearby site).
- **Frogmore** - FOUND: USGS Red Gum 1939 1:62,500 'INDIAN MOUND' (verified, locator only). Moore 1913 Tensas River
  sites checked - Frogmore not among them.
- **LSU Campus Mounds** - FOUND: USGS Baton Rouge West 1953 1:24,000, two contoured mounds (verified, unlabelled); 1939
  1:62,500 has a label ending '...N MOUNDS'. 1908 Baton Rouge 1:62,500: nothing drawn. Moore 1911/1913 mention Baton
  Rouge only in passing.
- **Balmoral** - NOTHING. Moore 1913 Tensas sites (Flynn, Alphenia, Mound Bayou, Lee places etc.) do not include it; no
  pre-1960 large-scale TNM quad. Mississippi River Commission 1:20,000 charts (1880s-90s, federal) might reach Lake St.
  Joseph - LoC search was rate-limited (HTTP 429) and could not be run.
- **Bayou Grande Cheniere** - NOTHING. Beyer (Publ. La. Hist. Soc. 1895-1917, 7 volumes grepped), Moore 1911/1913, USGS
  Fort Livingston 1893 (site falls in the top margin of the scan) and Bay Batiste 1949 1:31,680 (cheniere ridge drawn,
  no mound label). Coast Survey / MRC charts untried (LoC 429).
- **Watson Brake** - NOTHING expected (identified in the 1980s-90s). USGS Monroe 1940: nothing drawn.

### Arkansas

- **Plum Bayou (Toltec/Knapp)** - FOUND: USGS Scott 1942 1:31,680 'Toltec Mounds', three contoured mounds (verified).
  Thomas 1894 Pl. IX (sketch view) and Pl. X (plat, already staged). Mrs. Gilbert Knapp, Smithsonian Report 1877 pp.
  251-252: text only.
- **Parkin** - LIKELY only: USGS Princedale 1940, unlabelled closed contour at the point. Moore 1910 pp. 303-304 text
  only; Thomas 1894 has no Cross County plan (Thomas 1891 Catalogue Cross County lists Roman mounds etc., not Parkin).
  The lead's note "Moore ... refers to Thomas 1894's plan" for Parkin could not be confirmed.
- **Battle Mound** - FOUND: USGS Garland 1952 1:24,000, the elongated mound in closed contours (verified by shape and
  position, unlabelled). Moore 1912 Red River pp. 566-570 "Battle Place": text (592 ft long, 33 ft high), figures are
  vessels only.

### Texas / Oklahoma

- **Caddo Mounds (George C. Davis)** - LIKELY only: USGS Alto 1946 1:62,500, two small closed-contour ovals near the
  point, unlabelled. No pre-1931 description found in Thomas 1891 Catalogue or Moore.
- **Spiro** - NOTHING public-domain. Not in Thomas 1891 Catalogue; Moore did not reach it; only USGS Sallisaw
  1:125,000 (1900, 1911) before 1946 - too small to show the mounds. The 1936-41 WPA/University of Oklahoma plans were
  published later by non-federal bodies - not PD by date or by federal authorship.

### Tennessee

- **Pinson** - FOUND: Myer 1922 Fig. 1 (full survey plan, scale bar, north arrow) and Fig. 2 (citadel) (verified).
  Checked: Cisco 1879, American Antiquarian 1:259-260 (text only), Thomas 1891 Catalogue, USGS Beech Bluff 1953 (site
  falls off the sheet).
- **Sellars** - FOUND: Thruston 1890 Fig. 3 (verified, best copy) and Putnam 1878 Peabody 11th Report fold-out map
  "Earthwork on the Lindsley Estate ... from a survey by A. H. Buchanan" (verified title, but the IA Google scan shows
  the map still folded - need another scan). Identity: Sellars Farm = Putnam's 1877 "Lindsley estate" site in the bend of
  Spring Creek.
- **Shiloh** - FOUND: USGS 1934 Shiloh NMP 1:9600 sheet labelled 'Indian Mounds', 5-ft contours (verified); park map
  "Map of the battlefield of Shiloh" (General Staff reproduction, 1:10,560, c.1920) drawing seven mounds, unlabelled
  (verified). Smithsonian Report 1862 (letter: "eleven of these parallelograms" at Shiloh) text only.
- **Castalian Springs** - NOTHING drawn found. Haywood 1823 (text, the 16-acre circular enclosure), Thomas 1891
  Catalogue (cites Haywood and Jones only), Jones 1876 (`smithsoniancontr221880smit`, plans are of De Graffenried, West
  Harpeth, Old Town, Old Stone Fort only), Thruston 1890 (mentions only), Myer 1928 BAE 41st (a bowl only), USGS
  Bethpage 1955 (nothing drawn). Lead: W. E. Myer manuscript "Mounds and graves at Castalian Springs" (NAA, c.1891-93,
  unpublished; author d. 1923 so unpublished work is PD) - not seen; may hold a plan.
- **Mound Bottom** (has overlay) - Smithsonian Explorations 1921-23 (`explorationsfiel192123smit`) text says "Figure
  109 shows a map of the Mound Bottom division of the Great Mound Group" (Myer; presumably the same survey as the
  overlay's 1923 Commons map - not viewed); Explorations 1917-20 Fig. 133 and Myer 1922 Fig. 6 are photographs.

### Towns (Memphis, Nashville, New Orleans, St. Louis, Kansas City)

Not searched: covered by the separate cities lead (`docs/lead_us_cities.md`).

## Sources checked with nothing for this region (beyond the above)

Moore 1908 (both scans), 1909 Ouachita (`antiquitiesofoua00moor`, `b31364779`), 1910 St. Francis, 1911 Mississippi
River (`cu31924104075159`), 1912 Red River, 1913 Louisiana/Arkansas; Thomas 1894 full illustration list (Mississippi
and Arkansas figures are other sites: Carson, Clarksdale, Avondale, Champlin, Union Co., Menard, Old Town, Webb, Miller,
Thornton, Taylor Shanty, Pecan Point, Camden, Troyville); Squier & Davis 1848 southern plates (Pl. XXXVIII nos. 2-4,
XXXIX - other sites); Publications of the Mississippi Historical Society (39 volumes 1898-1925); Publications of the
Louisiana Historical Society (7 volumes 1895-1917, incl. Beyer's "Mounds of Louisiana" I-II, Larto, Franklin parish,
Calcasieu); Smithsonian Annual Reports 1860-1884, 1889-1892 (grepped for every county/site name); Smithsonian
Explorations and Field-work 1917-1929; Peabody Museum Reports (`firstthirtyfirs00musgoog`, `reportsofpeabody03peab`);
Thomas 1891 Catalogue (`catalogueprehis01thomgoog`) for county leads.

Not reachable from this machine: HathiTrust and BHL (Cloudflare 403 to curl; Chrome extension not connected), LoC
search after ~10 calls (HTTP 429). Worth a browser pass: HathiTrust for an unfolded Peabody 11th Report map (Sellars),
LoC Mississippi River Commission 1:20,000 charts (Balmoral, LSU, Bayou Grande Cheniere), NARA catalog for CWMF S9-3
(Tallahatchie), NAA for Myer's Castalian Springs manuscript.

## Brief's idea list - how each was worked

- "J. P. Brown" taken to mean Calvin S. Brown 1926 (Archeology of Mississippi) - found and mined (above).
- Squier & Davis Pl. XII "Duck river" = the Old Stone Fort (Coffee Co.), not in `us_sites.tsv`; not a row.
- Myer 1928 BAE 41st: Gordon and Fewkes sites only (not in our list); Castalian Springs = a bowl. Myer 1922/1923 Pinson:
  found (Art and Archaeology 1922).
- Jones 1876 Smithsonian Contributions 22: fetched; no plan of any listed site.
- Haywood 1823: Bledsoe's Lick text only. Halbert (Nanih Waiya): text only.
- Thomas 1891 Catalogue: used for county leads (Stelle 1870 Savannah plats, Cisco 1879 Pinson, Putnam Lebanon).
- Official Records Atlas: Tallahatchie checked (no plan). Shiloh Commission maps: found via LoC.
- Mississippi River Commission charts: not reachable - LoC returned HTTP 429 on 4 retries 90 s apart (2026-10-16); still open.
- NPS / federal modern reports: Pharr found; Emerald (Natchez Trace) - nothing found on IA.

## Fit notes

- USGS GeoPDFs carry their own georeference (polyconic, NAD27/Clarke 1866) - `geopdf_crop.py` places the site point to
  within a few pixels on every sheet tried; they can serve as seeds for the matcher, but most are 1:62,500 locators
  (mound symbols, not outlines). The 1:24,000/1:31,680/1:9,600 sheets (Toltec, Battle, LSU, Shiloh 1934) draw the
  mounds as contours.
- Pinson (Myer 1922) and Sellars (Thruston 1890) have scale bars and drawn creeks/bluffs - the best fit candidates found.
- Marksville Setzler/Fowke: mounds 8-20 are drawn in an offset strip joined at line A-A; shift before fitting.
