# Southeast (FL, GA, AL, SC, NC) - old plans of mound sites, research 2026-10-15

Rows: `se.jsonl` (same folder). Every row was checked on the page IMAGE (IA page/n<leaf>), not only on OCR.
Tools/downloads: `research/se_bin/` (fts.py = IA full-text search, leafof.py = find leaf by phrase, img.sh = page image),
`research/se_dl/` (texts, djvu xml, page images in `se_dl/img/`).

Region sites in us_sites.tsv: 23 (no NC site is in the list).

## Counts
- 13 rows in se.jsonl: 12 verified, 1 likely (Jones 1861 Etowah, partial scan).
- 7 sites gain rows: Etowah (4: Jones 1873, Whittlesey 1881, Thomas 1891, Jones 1861 likely), Ocmulgee (2), Kolomoki (2),
  Fort Walton (2), Moundville (1), Florence (1), Lake Jackson (1).
- Pre-1931 vs later: 10 rows pre-1931; 3 rows are POST-1931 federal works (Willey 1949 Fort Walton + Lake Jackson, Kelly 1938
  Ocmulgee) - public domain, but outside the project's pre-1931 theme, flagged for the owner.
- Sites in my region still with no plan at all (lead + this search): 14 - Mound Key, Turtle Mound, Safety Harbor, Madira
  Bickel, Portavant, Letchworth-Love, Velda, Rookery, Bottle Creek, Indian Mound Park (Dauphin I.), Fort Toulouse, Santee/
  Fort Watson, Sewee, Lamar (Lamar has only a 1938 locator map). Crystal River and Nacoochee keep only the lead's rows.


## Headline finding: the lead was wrong about C. C. Jones 1873

lead_us_mounds.md section C drops *Antiquities of the Southern Indians* (1873) as "woodcuts are artefacts, the only plan
is Bartram's chunk-yard". The book (IA antiquitiessouthin00jonerich) has full-page site plans made "from personal surveys":
- Pl. I (leaf n156) Tumuli and Fish-Preserves in the Etowah Valley -> Etowah
- Pl. IV (leaf n184) Tumuli on the Ocmulgee River, opposite the City of Macon -> Ocmulgee (street grid + railway + river!)
- Pl. V (leaf n198) Map showing the Messier Mound, Early County -> Kolomoki (survey by engineer J. A. Maxwell)
(Pl. II Little Shoulder-bone Creek / Sparta and Pl. III Savannah River below Augusta are sites not in our list.)

Second process lesson: name-matching misses old names. Kolomoki = "Messier/Mercier mound", "Kolee Mokee", "Colomokee";
Florence = "Ancient work in Alabama" (S&D fig. 21); Fort Walton = "Walton's Camp" / "The Narrows"; Safety Harbor =
"Phillippi's Point / Phillippi Hammock"; Mound Key = "Mound Island / Johnson's Key"; Ocmulgee = "tumuli opposite Macon".
Thomas 1891 *Catalogue of prehistoric works* (BAE Bull. 12, IA smithsonianinsti12smit) is the best county-by-county
index of who "described and figured" what - it led to the Kolomoki, Florence and Etowah finds.

## Per site

### Etowah (pictures_unplaced)
Already in the pipeline (confirmed in ancient-works data/books/matches.jsonl, status matched): Thomas 1894 (12th AR)
figs. 180 (copy of Jones's plat), 181 (copy of Whittlesey's figure), 182 (original BAE plat), plus a burials figure.
NOT matched: S&D 1848 Pl. XXXVIII no. 1 "Ancient works on Etowah river, Alabama" (row ancientmonuments00squi_n0228_1,
status no_candidate - S&D/Rafinesque wrongly put Etowah in Alabama, so the place gate rejects it; Thomas calls this
figure "very erroneous"; low value but it is an Etowah plan).
NEW rows: Jones 1873 Pl. I (verified; Thomas 1894 fig. 180 is a copy of it); Whittlesey, Smithsonian AR 1881 pp.
624-625 figs. 1-2 (verified, federal; prismatic-compass survey of May 1871; fig. 1 = site sketch that Thomas 1894 fig. 181
copies, fig. 2 = plan of mounds A/B/C - new); Thomas 1891 Am. Anthropologist 4:2 fig. 1 (verified; same BAE survey as 1894 fig.
182, alternate scan); Jones 1861 *Monumental Remains of Georgia* folding diagram (likely: only half the fold-out is
captured in monumentalremai00conggoog n33; the other three IA copies lack the plate).
Checked, no plan: BAE 5th AR 1887 (annualreportofbu518831884smit) - Etowah figures are the large-mound view and copper
plates; LoC 1864 Civil War map of the Etowah River (cws00081) - no mounds drawn.

### Ocmulgee (no_picture)
NEW: Jones 1873 Pl. IV (verified, pre-1931). Kelly 1938 BAE Bull. 119 fig. 2 contour map of Macon Plateau (verified,
federal, POST-1931 - owner call).
Checked, nothing usable: LoC "Map of Macon, Ga. and vicinity" 1864 (cws00087) and "Macon, Geo. 1864" (cws00086) - both
show the west-side Confederate lines, not the mounds; LoC bird's-eye "Macon, Ga." 1887 (pm001270) - East Macon at the edge,
mounds not shown; 1912 bird's-eye (pm001280) downloaded, not useful at that scale. Pickett 1851 only mentions "large and
interesting mounds" below Macon.

### Kolomoki (no_picture)
NEW: Jones 1873 Pl. V (verified); McKinley, Smithsonian AR 1872 p. 425 "Pyramid of Kolee Mokee ... surveyed by James N.
Evans, County Surveyor" (verified; federal; bearings+chains survey of mounds, walls, bastions, creek).
Checked, not a plan: Pickett 1851 *History of Alabama* vol. 1 plate at p. 168 (historyofalabama01pick n206) "Ancient Indian
fortifications and mounds in Early County, Georgia, from a sketch by Dr. C. A. Woodruff" - an oblique VIEW, and Jones 1873
calls it erroneous ("haycock appearance"). White 1855 *Historical Collections of Georgia* p. 425 reprints Pickett (not
re-checked on image). McKinley's p. 427 plat is Dry Creek / Walnut Fork, a different site.

### Moundville (pictures_unplaced)
NEW: Moore 1905 *Black Warrior River* folding plate "Mounds near Moundville, Ala. 1905" (blackwarriorriver00moorrich n12;
verified at 800 px; Dr. M. G. Miller's survey, 26 lettered mounds, ravines, county line). Lead had only the 1907 re-print/
revision. Thomas 1894: no Moundville plan.

### Florence / Waumanona mound AL (no_picture)
NEW: S&D 1848 fig. 21 p. 109 "Plan of Ancient Work in Alabama" (ancientmonuments00squi n230; verified) - hexagonal mound,
embankment, Tennessee River, Cane Island. Book is in the pipeline; caption has no "Florence" so the matcher missed it.
Checked, no plan: Moore 1915 Tennessee River (tennesseeriver00moorrich pp. 251-253, text only); Pickett 1851 (mention).

### Fort Walton (no_picture)
In lead: Moore 1901 fig. 13 (single mound).
NEW: Walker, Smithsonian AR 1883, Map 3 Choctawhatchee Bay (verified; WEAK locator, mound is a symbol);
Willey 1949 Map 6 Fort Walton site (verified; federal, POST-1931; mound + US 98 + streets).

### Lake Jackson (no_picture)
NEW: Willey 1949 Map 8 (verified; federal, POST-1931; caption says mound shapes stylized). Nothing pre-1931 found.
Checked: Thomas 1891 catalogue (Leon County: only "W. H. Lester mound, Lake Iamonia", reported by Rogan, no figure);
Moore 1903 Apalachicola, Moore 1918 NW Florida (northwesternflor0000clar), Moore 1901/1902 NW coast - no Lake Jackson.

### Crystal River (no_picture)
Lead already has Moore 1903 figs. 16-17 and Moore 1907 embankment plan. Nothing further found (Willey 1949 discusses it,
no new pre-1931 plan; Walker 1879 lists only "mound 7 miles north of Crystal River").

### Mound Key (no_picture)
Nothing. Moore 1900 (antiquitiesflorida00moorrich) "Mound Island" Fig. 7 is "sketched from an elevation to the north" =
a VIEW; Moore 1905 Misc. Florida - text only; Cushing 1896 Proc. APS 35 (jstor-983594) - text only ("a long series of
enormous elevations"), his plans (Pl. XXX etc.) are Key Marco, Battey's Landing, Demorey Key.
Lead to try: US Coast & Geodetic Survey used "the highest mound on Mound Key" as triangulation station (Lee County, 1884;
geodesytriangflo00uscouoft) - an 1880s Estero Bay T-sheet may draw the mounds. NOAA T-sheet server not reachable from here.

### Turtle Mound (no_picture)
Nothing verified. Checked: Thomas 1891 catalogue (Brinton SI Rep. 1866 p. 357; Le Baron SI Rep. 1882 p. 781 - text);
Le Baron 1882 (annual-report-board-of-regents-smithsonian_1882) text only. CAUTION: Moore's 1892-94 "Turtle Mound,
Brevard Co." in the St Johns shell-heap papers is a DIFFERENT mound (St Johns River near Lake Washington).
Lead to try: Le Baron 1882: "Several of the mounds on the Hillsboro' River and Mosquito Lagoon are shown on these charts"
- US Coast Survey chart No. 4, Inside Passage, East Coast of Florida, Hillsboro' River (NOAA Historical Map & Chart
Collection; search endpoint not reachable from this session). Unverified.

### Safety Harbor (no_picture)
Nothing pre-1931. Walker 1879 (annualreportofbo1879smit) "Mound at Phillippy's Point ... I did not take any measurements
or make any explorations"; Moore 1900: "near Safety Harbor, permission to dig was refused"; Willey 1949 text + Map 9
(regional Tampa Bay site map, locator only). NOT checked: Stirling's report in *Explorations and Field-Work of the
Smithsonian Institution in 1930* (pub. 1931, federal) - no IA id found by metadata search; IA full text for "Safety
Harbor" before 1935 returned only Willey 1949.

### Madira Bickel (Terra Ceia) and Portavant (Snead Island) (no_picture)
Nothing. Moore 1900 Terra Ceia text only ("see map" = his general route map); Willey 1949 text only.
Do NOT re-chase Walker 1879 Pl. IV "Indian Hill, Tampa Bay" ground plan: Indian Hill = Cockroach Key, Hillsborough County
(Willey 1949: 'The key is variously known as "Indian Hill," "Indian Key"'; Moore 1900: "About 3 miles down Tampa Bay from
the mouth" of the Little Manatee). Walker's Pl. III Shaw's Point is the south bank of the Manatee mouth, not Snead Island.

### Letchworth-Love (no_picture)
Nothing. Thomas 1891 catalogue: "Dr. J. D. McLeod Mound ... near Lake Miccosukie. Reported by John P. Rogan" (text);
Thomas 1894, Moore volumes: nothing.

### Velda (no_picture), Rookery Mound (no_picture)
Nothing found in the sources checked; no pre-1931 literature found (Velda is a modern discovery; Rookery not in any Moore/Walker index checked).

### Bottle Creek (no_picture)
Nothing. Moore 1905 "Mound on Bottle creek, Baldwin County" - dimensions only, "No excavation was attempted by us".

### Indian Mound Park, Dauphin Island (no_picture)
Nothing. Moore 1905 "Shell deposit on Dauphin island" - text + sherd figure only. Thomas 1891: Mobile County entries
(Walthall 1859, Mohr SI 1881) are text. Possible lead: 1710s-1720s French plans of Isle Dauphine (not checked).

### Fort Toulouse mound (no_picture)
Nothing verified. Thomas 1894 "Old Fort Jackson works" - text only (mound 45 ft, "most of the site of the fort has been
washed away"); Moore 1899 Alabama River starts below Montgomery; Schoolcraft vol. 5 (1855) "Sketch of Little Tallassie,
or the Hickory Ground" marks "Old French fort Alabama" at 3 miles to the inch - locator only, no mound; Swan 1790 sketch of
"three mounds ten miles below Little Tallassie" (Schoolcraft vol. 5 p. 282) does not match Fort Toulouse (25-ft mound,
33-ft base). Lead: a manuscript "Plan du fort Toulouse" is catalogued in the Library of Parliament (Canada) copies of
French colonial records (IA lancienqubecdes00bcgoog, catalogueoflibra02canauoft); whether it draws the mound is unknown.

### Nacoochee (no_picture)
Lead has Heye 1918 fig. 1 (summit outline). Nothing else: Jones 1873 pp. 213-215 and White 1855 pp. 486-487 are text;
Heye 1918 other figures are sections/artefacts.

### Lamar (no_picture)
Nothing pre-1931. Kelly 1938 (BAE Bull. 119) fig. 1 key map (1 inch = 1 mile) locates the Lamar site - locator only;
Lamar plates there are photographs.

### Santee Indian Mound / Fort Watson (no_picture)
Nothing. Lossing 1851-52 *Pictorial Field-Book* vol. 2 p. 706 fig. "Site of Fort Watson" (pictorialfieldbo02loss n715)
checked on image: a small ground-level VIEW of the wooded tumulus, not a plan; Thomas 1891
catalogue has no Santee/Fort Watson figure (only "mounds near Santee Swamp" from Mills 1826, text); Moore 1898 SC coast
covers Beaufort County only. NOT checked: Mills' Atlas of South Carolina (1825), Sumter/Clarendon
district sheet - roughly 2 miles to the inch, so a locator at best even if it marks the mound.

### Sewee Mound (no_picture)
Nothing. Moore 1898 SC coast (JANSP 11, journalofacad2111897acad) is Beaufort County; its "Bull island" enclosure is the
Beaufort Bull Island, not Bulls Bay. No pre-1931 description found in IA full text. NOT checked: Mills' Atlas
(1825) Charleston district sheet (~2 mi/inch, locator at best).

## Sources checked with no plan for any region site
Cushing 1896 (Key Marco); Moore 1896/1922 Duval & Clay + east coast (additionalmounds00moor); Moore 1895 Duval
(duvalcountyflorida00moorrich); Moore 1897 Georgia coast; Moore 1899 Alabama River; Moore 1901-02 NW Florida coast
(beyond fig. 13); Moore 1903 central west coast (beyond Crystal River figs.); Moore 1918; Walker 1879 (plates are other
Tampa Bay sites); Thomas 1894 Alabama/Georgia/Florida sections (only Etowah, Tally, Rembert, Hollywood figures); BAE 5th AR;
Smithsonian AR 1880, 1881 (Etowah only), 1882; Proc. Calif. Acad. Sci. 4 (Tampa Bay remarks); Pickett 1851;
Lossing vol. 2; LoC map search (Macon, Etowah, Fort Toulouse, Fort Watson, Dauphin Island, Mosquito Inlet, Estero);
Wikimedia Commons (rate-limited; results were modern photos and IA book PDFs).
