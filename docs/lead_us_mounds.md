# Old plans for the US mound sites that have none (lead, 2026-10-15)

Owner question (2026-10-15): "what happened to the US sites ... can you find resources for them so that the local
models can place them?" This lead answers the "resources" half for the agents. Nothing here is a fit; every row
still goes through the evidence rule and the numeric gate (GOAL.md), and no row may become a document whose
points were not measured on the picture and on the ground.

## Where the US sites stand (web/data/sites.json + web/data/review.json, Mac main 4e26e6f)

121 US sites are built and live. 12 carry an overlay (the six 2026-10-09/10 hand fits, Aztalan, Cahokia, Fort
Ancient, Mound Bottom, Serpent Mound; Watson Brake's two pictures are modern LiDAR maps and stay off). The other 109:

| bucket | sites | why |
|---|---|---|
| no picture at all | 70 | 212a's cover search (Commons + the seven US books in `pipeline/books.py:BOOKS`) found none |
| pictures, none placed | 14 mound sites | 1848-1902 line plates vs relief: the matchers find too few matches (docs/matchfit.md s3, s8) |
| pictures, none placed | 25 cities | oversize bird's-eye views / plans vs aerial (docs/lead_us_cities.md fit notes) |

The nine "automatic fits" in docs/batch_us.md (Etowah, Mound Cemetery, Hodgen's, Pyramid Mound, Alligator, Mount
Horeb ...) were vision-model pattern documents (anchors on a 100-px ladder, resid 0.0) and 212b's sync removed them;
they were never real placements.

## A. Plans already in our cached books, missed by the name matcher (cheapest first)

`data/books/matches.jsonl` was matched by name against the catalog of the day. The 1848-1902 captions use landowner
or 19th-century names, and three of these sites (Frankfort Works, Hopewell Mound Group, Biggs Site) were added to
the catalog after the match ran. Each row below is backed by the book's own OCR (`data/raw/books/<ia>/hocr_searchtext.txt.gz`)
or plate list (`data/books/lists/<ia>.json`); the place gate still decides.

| site id | book, plate/figure | evidence in the book |
|---|---|---|
| hopewell-mound-group | S&D 1848 Pl. X; Fowke 1902 fig. 39 | S&D: "PLATE X. Clark's work; North Fork of Paint Creek"; Fowke list: "Clark's works, or Hopewell group, Ross county" |
| frankfort-works | Fowke 1902 fig. 30 (row b24849959_n0214_2 "FRANKFORT WORKS", status no_candidate) | "Works at Frankfort, Ross county" |
| seip-earthworks-q123916810 | Fowke 1902 fig. 41 | "Pricer works, near Bainbridge, Ross county" (Seip is also called Seip-Pricer; check by place) |
| indian-mound-reserve-q2493254 | S&D 1848 (Massie's Creek plate, list row "Ancient work, Greene county, Ohio"); Fowke 1902 fig. 52 | S&D: "situated on Massie's creek, a tributary of the Little Miami river"; Fowke: "Work on Massie's creek, Greene county" (= Pollock Works, inside the reserve) |
| emerald-mound-site-q5370466 | Thomas 1894 Pl. XIV (rows annualreportofbu1218901891smit_n0346_1/_2, no_candidate) | "Selsertown group, Adams county, Mississippi"; text: "about a mile northwest of the site of the old village of Selsertown" |
| criel-mound-q5185117 | Thomas 1894 Pl. XXVII; figs. 291-297 | text: "commencing with the Criel mound (No. 1, Pl. XXVII)". `books_match.py:HAND` marks it "doubtful" because it is a group plan; the group plan contains the mound, so it is a valid drawing of the site - lift the HAND entry |
| biggs-site | Fowke 1902 figs. 19-20; S&D Pl. XXVIII (Portsmouth group A) | "Mound and concentric circles in Kentucky", "Mound within enclosure, Greenup county Kentucky" - check which one by place |
| horseshoe-mound-q116268128 | S&D Pl. XXVIII (Portsmouth groups B/C); Fowke figs. 16, 18 | "Portsmouth works", "Works on the site of Portsmouth" - check which group holds Mound Park's horseshoe |
| story-mound-state-memorial-q18617458 | S&D Pl. II | "Map of a section of 12 miles of Scioto valley" (Chillicothe) - only if the mound is drawn; a 12-mile sheet is coarse |
| miamisburg-mound-q34827561 | S&D Pl. III | "Map of a section of 6 miles of Miami valley" - same caveat. S&D fig. 1 and Fowke fig. 91 are a view and a photograph, not plans |

Halvorson and Blackhawk Country Club mound groups (Madison WI): check whether Lapham 1855 Pl. XXXII "Ancient
Works, Madison" reaches Yahara Heights (43.155, -89.392) and Shorewood Hills (43.080, -89.461). Not checked.

## B. New books (verified on Internet Archive 2026-10-15: identifier resolves, full text downloads, not lending-restricted)

All are public domain in the US: published before 1931, and the BAE reports are US government works whatever the
year. Each row names the figure caption found in the volume's OCR; the leaf number is for the books pipeline
(`books_ia.py`, `books_lists.py`) to resolve, as for the seven existing books. Pick the best scan per volume the way
`BOOKS[...]["why"]` records it (resolution, fold-outs unfolded); alternates are listed.

| site id | book | IA identifier (alternates) | caption / text in the volume |
|---|---|---|---|
| crystal-river | C. B. Moore 1903, Certain aboriginal mounds of the Florida central west-coast (JANSP 12) | floridawestcoast00moorrich | "Fig. 16. Plan. Mounds, shell-heaps and causeway. Crystal river."; "Fig. 17. Plan and elevations. Place of burial." |
| crystal-river, moundville-archaeological-site-q1320821 | C. B. Moore 1907, Moundville revisited. Crystal River revisited. Mounds of the lower Chattahoochee and lower Flint rivers (JANSP 13) | crystalriverrevisted00moorrich | "A plan of the Moundville mounds, prepared by Dr. M. G. Miller"; Crystal River: "The plan given herewith shows the embankment (C C)". Moundville today has only a dropped modern diagram |
| shiloh-indian-mounds-site-q7496730 | C. B. Moore 1915, Aboriginal sites on Tennessee River (JANSP 16) | tennesseeriver00moorrich (aboriginalsiteso00moor, gri_33125017157781) | "Fig. 20. Plan of mounds on Shiloh Battlefield, Tenn." |
| winterville-site-q4470180 | C. B. Moore 1908, Certain mounds of Arkansas and of Mississippi (JANSP 13) | arkmisscertmound00moorrich (certainmoundsofa00moor, cu31924104075076) | "The Blum group of mounds, in Washington county, Miss. (see map)"; "the accompanying plat of a survey made by Dr. M. G. Miller"; index "Blum mounds, map of, 595" |
| marksville-prehistoric-indian-site-q6771408 | G. Fowke 1928, Archeological investigations II, in 44th Annual Report of the BAE (1926-27) | annualreportofbu44smit (annualreportofbu44smithso) | "Plan of the Marksville, La., works" (list of illustrations, p. 412); "PLAN OF THE MARKSVILLE WORKS" |
| poverty-point-q964745 | C. B. Moore 1913, Some aboriginal sites in Louisiana and in Arkansas (JANSP 16) | cu31924104075142 (b31350446) | "Fig. 29. Plan. Mound A. Poverty Point Plantation"; "Plan of great mound on Poverty Point, 68" - one mound only, weak for a fit |
| fort-walton-mound-q5472236 | C. B. Moore 1901, Certain aboriginal remains of the northwest Florida coast, pt. 1 (JANSP 11) | certainaboriginal01moorrich (nwcertainabori00mooruoft) | "Fig. 13. Plan of mound at Walton's Camp, showing excavations" - single mound, weak |
| nacoochee-mound-q4312576 | Heye, Hodge and Pepper 1918, The Nacoochee mound in Georgia (MAI Contributions 4:3) | nacoocheemoundin00heye (nacoocheemoundin00heyeiala, nacoocheemoundin3419heye) | "Fig. 1. Outline of the summit of the Nacoochee mound" - summit only, weak |

Weak rows (one mound outline) are worth staging only if the outline is drawn with surroundings (roads, river,
fences) a fit can hold on; otherwise record them as no-fit-possible, do not force a document.

## C. Checked and dropped, or not verified

Dropped (volume fetched, no plan of the site): C. C. Jones 1873, Antiquities of the Southern Indians (cu31924091024426
etc.: woodcuts are artefacts, the only plan is Bartram's Creek chunk-yard) - Ocmulgee, Lamar, Etowah; C. B. Moore 1916
Green River / lower Ohio (someaboriginalsi00mooruoft): Kincaid described, "seen but not measured", no plan; Moore 1910
St. Francis (stfranciswhiteblk00moorrich): Parkin only artefacts, refers to Thomas 1894's plan; Winchell 1910
(prehistoricabori0000winc): a 34-leaf pamphlet with no plans; Myer, BAE 41st AR (annualreportofbu41smit): Castalian
Springs described, no plan caption found in OCR.

Not verified (leads for a search task, not rows):
- N. H. Winchell 1911, The Aborigines of Minnesota (T. H. Lewis's Northwestern Archaeological Survey plats): Grand
  Mound, Indian Mounds Park St Paul. Not on IA under that title; try HathiTrust full view.
- Official Records Atlas (atlastoaccompany00unit, 1891-95): Civil War Earthworks at Tallahatchie Crossing - check
  whether a plate draws the Tallahatchie crossing works.
- The Wisconsin Archeologist (IA wisconsinarcheol*, 1901-): Lizard Mound, Madison groups - pre-1931 volumes only.
- Moore's other Florida volumes (Mound Key, Turtle Mound, Lake Jackson, Safety Harbor, Portavant/Snead Island, Terra
  Ceia/Madira Bickel): Moore 1900 (antiquitiesflorida00moorrich) and 1918 (northwesternflor0000clar) carry no plan
  captions for them in OCR; other Moore Florida volumes (1894-1905 east coast, 1905 "Miscellaneous investigation") not
  fetched.
- Spiro, Caddo Mounds (TX), LSU, Pharr, Pocahontas, Sewee, Aden, Batesville, Balmoral, Frogmore: no pre-1931 plan
  known; expect them to stay pictureless.

## D. Placement aids (the 14 + any new rows): what the local model can measure from

The pattern documents failed because the model reported coordinates it had not measured. docs/autofit.md s5 shows the
automatic fitter works from tight seeds (about +-3 deg, +-5 %, 50 m) with a cleaned template, and fails from loose
ones. So the missing input is a measured seed, not a better picture. Sources a seed can come from:

1. **BLM PLSS sections** (public domain). Live 2026-10-15: `https://gis.blm.gov/arcgis/rest/services/Cadastral/BLM_Natl_PLSS_CadNSDI/MapServer`,
   layer 1 township, 2 section (point query at Emerald Mound returned `MS320080N0010W0`, Section 41). Thomas 1894 and
   Lapham plats often state "Sec. N, T. N, R. W" or draw section lines: the section polygon gives scale, rotation (the
   lines run N-S/E-W) and a window. Not usable in Ross County and the rest of the Virginia Military District of Ohio
   (metes and bounds, no PLSS).
2. **Mound summits in 3DEP.** Thomas's and Moore's plats are mostly mound groups with numbered mounds; summits are
   local maxima on the bare-earth DEM. Matching drawn mound centres to detected summits (RANSAC similarity on points)
   uses no image appearance, which is where the matchers fail. This is a proposal: before any accept, pre-register a
   held-out test on groups with known fits (Cahokia, Mound Bottom, Aztalan), as docs/autofit.md did.
3. **Published control points for the city plans.** Allmaps annotations (`https://annotations.allmaps.org`, live) and
   Map Warper (`https://mapwarper.net/api/v1/maps`, live) hold georeferences people already made for many old US city
   maps. Licence-check each set before use (owner rule: modern data is licence-checked at adoption; the old map itself
   publishes with credit).

## Proposed task (for the lead to file on the VM)

"US mound plans: re-match the cached books by place (section A rows, lift the Criel HAND entry), add the section B
books to `BOOKS` (pick scans, triage, lists), stage pictures with evidence, and run the cover loop. Acceptance: every
section A/B site ends with a gated fit or a review item that names the picture and why it could not be placed; no
document without measured pairs; section D item 2 only after its held-out test passes."
