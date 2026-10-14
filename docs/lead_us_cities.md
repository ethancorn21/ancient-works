# Old plans of US cities (task 236a)

GOAL.md point 5 (the 2026-10-13 owner change): the map grows with US cities - "lets also add US cities
like nashville or dc or SF or New York. Those had to have had some survey stuff as well." Town plans and
views count as drawings (exempt from the 150-year rule); plain survey sheets (Coast Survey charts, USGS
quads) are background, not drawings. This task stages the **named city plans** (manuscript and engraved
plans, 1660-1880, plus the 1895 Civil War fortification atlas plate - the Civil War exception, in the
Nashville section): New York - the **Castello plan (1660)**, the **Ratzer map (1767)**, the
**Commissioners' Plan (1811)** and the **Viele map (1865)** - Washington DC - the **L'Enfant plan
(1791, first printed 1792)**, the **Ellicott plan (1792)** and the **Civil War defences (1865)** - and
San Francisco - the **1839 Vioget plan (the first plan of the old town)**, the **1849 Eddy survey map**,
the **1850 first-published map** and the **1854 Eddy 'full and complete' sheet** - and Nashville - the
**1804 Clayton/Temple plan** (as its 1880 publication), the **1860 Haydon & Booth plan**, the **1860s
O.M. Poe military survey** and the **1895 Civil War fortification atlas plate** (the panels surveyed
Nov 30 - Dec 1864) - all four owner-named cities staged (2026-10-14). Bird's-eye/panoramic views of
the same and other US cities are task 236b.
The picture rows are staged in this task's own files (`data/catalog/extras_us_cities.jsonl`,
`data/commons/files_us_cities.jsonl`, `data/commons/classified_us_cities.jsonl`); **236c** consolidates
them into the canonical data and builds the sites, 212's cover runs the fitting loop.

**None of the four owner-named QIDs is in the catalog yet** (checked against `data/catalog/sites.jsonl`,
`data/catalog/extras.jsonl` and `web/data/sites.json`, 2026-10-13/14 - the two Nashville fort QIDs
included), so every city gets a **new extras site row**, not picture rows on an existing site. The region string "United States" needed a one-line addition to
`pipeline/build_catalog.py:REGION_NAME` (`"united states": "United States"` - 236b adds the identical
line; the old US extras rows keep their "US" region and are untouched).

**Ground.** The city sites are **aerial-photograph ground** (`aerial_ok: true` on every staged site row;
no open LiDAR over a built-up city - bare-earth LiDAR erases the streets). The street grid, the
shoreline, the squares and the church footprints carry the fit. Civil War fortification plans are the
exception: their earthwork banks may show on 3DEP bare earth (`pipeline/aw.py`), so each fort is a
candidate **site of its own** (kind "fort" = 1600 m box, its own QID) - the DC ring's forts (the
catalog already holds the individuals, see the Washington section) and Nashville's Fort Negley
(no fort-only plan on Commons yet - recorded on the city's site note).

**The evidence field on every staged row is hand-recorded `caption_coords`** in the exact key order of
`fit/evidence.py:caption_route`: the caption names the city (the site's `named` short form appears in
the file title + description) and the stored coordinates are the verified site point itself
(dist 0). `fit/evidence.py check` passes offline from the stored fields, and the module's `--check`
re-runs it. `record --live` would instead take the first name-search hit for the caption - which is why
every QID below is re-verified, and why the stage **fails loud** when a file caption does not print the
city (the named-place gate, `fit/src_us_cities.py:evidence_for`). A scan whose file page lost the
drawing's date gets the known drawing date on the row with the page value kept as `date_commons` (the
Zwolle precedent; `sources.py` and `src_van_deventer.py` swap before the `keep()` gate, so the
drawing's year - not a 21st-century upload - is what `keep()` judges). The hand-checked file -> QID
table lives in `fit/src_us_cities.py` (the `pipeline/sources.py` pattern, no book machinery).

## QID verification (checked 2026-10-13/14, re-run with `.venv/bin/python fit/src_us_cities.py --verify`)

**Staged (in the table):** New York City Q60, Washington DC Q61, San Francisco Q62 and Nashville
Q23197, re-verified against Wikidata - label, every P625 value (flagged when >50 km from the table
point), P373, P131 (with labels), the enwiki article, and the first name-search hit with coordinates
(what `record --live` would resolve for the caption route). No P625 flag fired (Q62's two values are
2.0-2.4 km from its table point; Q23197's is 721 m NE of the table point - the point is a refinement,
not a P625 - see the Nashville section); no search trap: the first search hit with coordinates is the
city itself in all four cases.

```
checked 2026-10-13 - 3 QIDs (Wikidata)
  Q60  'New York City'
      P625: [(-74.00611111111111, 40.71277777777778)]  (table site point: -74.006111, 40.712778)
      P373: ['New York City']
      P131: [('New York', 'Q1384')]  (table place: 'New York County, New York')
      enwiki: 'New York City'  (table wikipedia: 'https://en.wikipedia.org/wiki/New_York_City')
      search 'New York City': first hit with P625 is Q60 'New York City' (-74.00611111111111, 40.71277777777778)
  Q61  'Washington, D.C.'
      P625: [(-77.036666666667, 38.895)]  (table site point: -77.036667, 38.895)
      P373: ['Washington, D.C.']
      P131: [('District of Columbia', 'Q3551781')]  (table place: 'District of Columbia')
      enwiki: 'Washington, D.C.'  (table wikipedia: 'https://en.wikipedia.org/wiki/Washington,_D.C.')
      search 'Washington, D.C.': first hit with P625 is Q61 'Washington, D.C.' (-77.036666666667, 38.895)
  Q62  'San Francisco'
      P625: [(-122.41944444444445, 37.775), (-122.41638888888889, 37.7775)]  (table site point: -122.40289, 37.79213)
      P373: ['San Francisco']
      P131: [('San Francisco County', 'Q13188841'), ('California', 'Q99')]  (table place: 'San Francisco County, California')
      enwiki: 'San Francisco'  (table wikipedia: 'https://en.wikipedia.org/wiki/San_Francisco')
      search 'San Francisco': first hit with P625 is Q62 'San Francisco' (-122.41944444444445, 37.775)
```

```
checked 2026-10-14 - Q23197 (Wikidata; the same --verify ran all four table QIDs in one pass)
  Q23197  'Nashville'
      P625: [(-86.77444444444444, 36.16222222222222)]  (table site point: -86.78152, 36.16529; 721 m NE - no >50 km flag)
      P373: ['Nashville, Tennessee']
      P131: [('Davidson County', 'Q1177705')]  (table place: 'Davidson County, Tennessee')
      enwiki: 'Nashville, Tennessee'  (table wikipedia: 'https://en.wikipedia.org/wiki/Nashville,_Tennessee')
      search 'Nashville': first hit with P625 is Q23197 'Nashville' (-86.77444444444444, 36.16222222222222)
```

**The two Nashville fort QIDs (checked 2026-10-14 via `pipeline/catalog_wd`; not in the module
table - the table holds the city site only; a fort gets its own site only when a fort-only plan
appears):**

- **Q5471739 "Fort Nashborough"** - P625 (36.164167, -86.774444), precision 0.001, P131 Q1509; the
  enwiki infobox gives the same coordinates (a small replica stands along First Avenue N in modern
  downtown) and OSM way 130910783 (historic=fort) sits at the same spot - three independent sources
  agree. This is the Clayton 1804 plan's hatched "former Fort" block, the 1790s town's SE corner,
  217 m north of the city P625 at the same longitude - anchor A of the mirror fit in the Nashville
  section.
- **Q5471744 "Fort Negley"** - P625 (-86.774658, 36.145097), ~1.9 km south of the city P625, P131
  Q23197, P373 = 12 files: photos (Barnard, Webster & Albee, modern park) and the three Fletcher
  1864 lithograph views - **no plan**. The Fort Negley fort-site candidate (Nashville section
  below).

**The "Barnard Castle trap" in action (task's warning, confirmed):** the prep's *recalled* QIDs were
wrong twice - New York first remembered as **Q30492, which is the NUMBER "483"**, and Nashville first
remembered as Q15190 (not Nashville). A name search alone gives the wrong place; the QIDs stand on
label + P625 + enwiki verification, never on the search. The enwiki-infobox-coordinates cross-check
came back empty from the wp API (the `coordinates` property) - not blocking; the fields above stand.

## New York (Q60)

- **The site point.** `new-york-q60` at Q60's P625 (-74.006111, 40.712778) - the Financial District /
  City Hall. Kind "town" = the 2000 m site box; the box covers the whole drawn Manhattan of the 1660
  plan (harbour tip to ~19th St).
- **The extent decision (acceptance box 2).** Extras rows CAN carry their own `box_m`
  (`pipeline/build_catalog.py:make_site` does `entry.get("box_m") or box_m(entry)`; precedents
  biggs-site 800 m, frankfort-works 1000 m; per-site overrides live in `specs/site_boxes.json`, 211's
  territory). `extent_m` (`pipeline/catalog.py`) is the synthetic-group spread used for
  `catalog_triage` crop sizing - **not** the site box, so it is not the mechanism. **Decision: the
  city sites keep the kind-"town" 2000 m box.** The 1811 and 1865 sheets span well beyond it
  (Manhattan + Long Island, ~8.5 km for the 1811 bird's-eye), so those fits are **likely to end as
  review items, not fitted plans** - the Venice precedent (`docs/lead_artists.md`: an 8 km view on a
  2000 m box, staged, left for the review queue); it is recorded on the site row's `note` and here,
  not as an extent field. The DC 1865 defences ring (~35 km) follows the same rule in its session.
- **Staged rows.** `extras_us_cities.jsonl`: `new-york-q60` (name, place "New York County, New York",
  lon/lat above, region "United States", kind "town", QID, wikipedia, `aerial_ok: true`, the note
  above). `files_us_cities.jsonl`: the four rows below, each with the hand-recorded `caption_coords`
  evidence (`named_place` "New York", `place_qid` Q60, place = site point, dist 0; `cat: null` - the
  caption route, as the van Deventer rows). `classified_us_cities.jsonl`: plan/plan/birdseye/plan,
  `by: "hand"`.

### The Castello plan (1660)

- **What it is.** The surviving ORIGINAL drawing of the Castello plan of New Amsterdam (1660), the
  first detailed plan of the city - the surviving sheet in the Biblioteca Medicea-Laurenziana,
  Florence. Nuance (recorded, not a drop reason): per Deak the sheet was probably **copied by an
  unknown draftsman c. 1665-1670** from Cortelyou's summer-1660 survey - 1660 is the survey/tradition
  date; it is still the 17th-century original sheet, **not the 1916 redraft** the task warns about.
- **Where the files live.**
  - **STAGED** - `File:Afbeeldinge van de Stadt Amsterdam in Nieuw Neederlandt (NYPL Hades-118555-54682).tif`
    (4753x3598, Public domain, "Scan by NYPL"): the full-size photograph of the surviving original. The
    file page lost the drawing's date ("[Date not available]"), so the known survey date is on the row
    (`date: "1660"`, `date_commons: "[Date not available]"` - the swap fired).
  - DROP - `File:Stad Amsterdam in Nieuw Nederland (City Amsterdam in New Netherland) Castello Plan 1660.jpg`
    (3888x2916, the enwiki main image): the page description says "New Amsterdam (Manhattan)", not
    "New York" - it fails the named-place gate (the caption must print the city the site row names).
  - DROP - `File:CastelloPlanOriginal.jpg` (2100x1398) and `File:Afbeeldinge van de stadt Amsterdam in
    Nieuw Neederlandt, Bestanddeelnr 189006 012.tif` (3064x2528, CC0, Met/Spaarnestad): **duplicate
    scans of the same Florence sheet** - one row per picture.
  - DROP - **the 1916 Adams/Stokes redrafts, the trap the task names** (their pages honestly date 1916
    - `year_of` -> 1916, they would pass `keep()` as 1916 drawings - but they are **redrawings**, never
    staged as the 1660 original): `File:Redraft of the Castello Plan New Amsterdam in 1660 by John
    Wolcott Adams.jpg` (5776x4197, "redrawn in 1916"), `File:Castello Plan Redraft New Amsterdam 1660
    Colored John W Adams.jpg` (the color version), `File:Castelloplan.jpg` (3267x2401, "Drawn in 1916"),
    `File:Redraft of the Castello plan (NYPL Hades-118556-54683).tif` (5645x4060).
- **Fit note for 212.** A flat plan of the drawn Manhattan tip (harbour to ~19th St) inside the 2000 m
  box - the street grid, the harbour shoreline and the church footprints are the anchors; a similarity
  fit (scale + translation, the flat-plan model) is the right model here.

### The Ratzer map (1767)

- **What it is.** Bernard Ratzer's 1767 plan of the City of New York, the city as surveyed 1767 - the
  staged file is the **only full contemporary-color copy** of the 1767/1770 engraving.
- **Where the files live.**
  - **STAGED** - `File:Plan of the City of New York by Bernard Ratzer, 1767.jpg` (5430x7080, Public
    domain, DateTimeOriginal 1767 on the page - no swap needed).
  - DROP - `File:Ratzer Map 1767.jpg` (706x477): **too small** to fit.
  - DROP - `File:Ratzer fasimile, NYC map, 1767.JPG`: the page date is 2015-10-21 - a **2015 photograph
    of a facsimile**, not the drawing.
  - DROP - `File:Ratzer lower Manhattan 1/2.jpg`: a **detail crop**.
  - DROP - the 1776 re-engravings of the same 1767 survey (Jefferys & Faden, London; live and free,
    re-checked 2026-10-13): `File:Plan of the city of New York by Ratzer, 1776.jpg` (2202x1446),
    `File:Plan of the city of New York in North America by Ratzer, 1776.jpeg` (563x760),
    `File:Plan of the city of New York - B. Ratzer - btv1b53089813k (1 of 2).jpg` (11310x7795) and
    `(2 of 2).jpg` (11310x5194). The prep's batch queries had the wrong title case (File titles are
    case-sensitive - lowercase "city"), so they looked deleted (stale search index); they are up.
    They re-enact the same plan already staged as its 1767 original: **one row per plan**.
- **Fit note for 212.** Flat plan, Manhattan to the Battery area; same model as the Castello plan,
  denser street grid (the numbered building index makes it the richer of the two for fitting).

### The Commissioners' Plan (1811)

- **What it is.** The Commissioners' Plan of 1811 - the street grid that is today's Manhattan - in its
  **published bird's-eye form** (John Randel Jr.'s atlas sheet, published 1821). The plan itself is
  1811; the page dates the 1821 publication, so the known-date swap fired (`date: "1811"`,
  `date_commons: "1821"`). Classified `p_birdseye: 1.0` (by hand).
- **Where the files live.**
  - **STAGED** - `File:Commissioners' Plan of 1811 by John Randel published in 1821.jpg` (11841x8252,
    Public domain).
  - DROP - `File:Grid 1811.jpg` (250x720, page date 2005-04-21): a thumbnail-size modern upload of the
    1807 provisional map - **too small**, and not the 1811 plan itself (checked live 2026-10-13).
  - DROP - `File:NYC-GRID-1811.png` (1362x4131, page date 1893-06): a **19th-century reproduction of
    the 1807 provisional map**, not the 1811 plan itself (checked live).
  - DROP - `File:Alphabet-City-area-of-1811-plan-for-Manhattan.png` (2064x1808, page date 1811-11-16):
    "**the portion extracted here**" - a **detail crop** of the lettered-avenues area (checked live).
  - Not this site's pictures (same Randel atlas, other sheets): `File:1811 commissioners' plan of
    Phiadelphia.jpg` (3628x1705) and `File:1811 commissioners' plan of Connecticut and Long Island.jpg`
    (3614x3243) - sheets of the **surrounding country** (their page descriptions carry the atlas title
    "The City of New York as laid out ... with the surrounding country", so a live caption route would
    wrongly tie them to New York - the named-place gate is not a place check, a human reads these).
    Possible later leads for their own cities (the Long Island sheet spans the whole island).
- **Fit caveat for 212 (the extent case).** The bird's-eye sheet spans Manhattan **plus Long Island**
  (~8.5 km) against the 2000 m town box, so 212's similarity fit is **likely to end as a review
  item**, not a fitted plan - staging is what this task owes, not a fit (the Venice precedent). If a
  wider box is wanted, `specs/site_boxes.json` is where it gets adjusted (211's territory).

### The Viele map (1865)

- **What it is.** Egbert Viele's 1865 topographical map of the City of New York, made for the Sanitary
  Commission - the **original water courses and made land**, the city's coastline as it was before the
  filling of the East River and the Hudson shore.
- **Where the files live.**
  - **STAGED** - `File:Viele Map (Topographical map of the City of New York), 1865.jpg` (19706x6054,
    Public domain, DateTimeOriginal 1865 on the page).
  - DROP - `File:Viele Map 1865.jpg` (9621x2837), `File:Viele Map 1865-Topographical New York City.jpg`,
    `File:Viele Map Collect Pond Five Points.jpg` (detail crop) and `File:Topographical map of the City
    of New York - showing original water courses and made land LOC 2006629795.tif` (the LOC scan):
    **duplicates or crops of the same picture** - one row per picture.
- **Fit note for 212.** Flat map, wider than the town box (Manhattan to the Brooklyn/Queens shore) -
  same review-item caveat as the 1811 sheet. Its **made-land coastline and the original water courses
  are the strongest anchors**: features that moved (filled ground) versus features that did not
  (the pre-1835 shoreline) give the fit something to hang on.

## Washington DC (Q61)

- **The site point.** `washington-q61` at Q61's single P625 (-77.036667, 38.895) - the old L'Enfant
  core, which the 1791/1792 plans draw in their entirety. Kind "town" = the 2000 m site box (the same
  extent decision as New York: oversize sheets end as review items, not wider boxes).
- **The defences ring and the forts.** The 1865 fortification ring spans ~35 km beyond the box, so its
  fit is **likely to end as a review item, not a fitted plan** - the Venice precedent; recorded on the
  site row's `note`. The ring's forts need **no new QID work**: the catalog already has the individual
  fort sites (Fort Bayard Q3077774, Fort DeRussy Q5471024, Fort Totten Q18150335, Fort Marcy
  Q61784495, Fort Foote Q14691922 - all `part_of` Q5124610 "Civil War defenses of Washington, D.C."
  in `data/catalog/sites.jsonl`); they stay candidates for their own kind-"fort" rows in a later task
  (the 203a earthwork precedent for 3DEP-visible banks).
- **Staged rows.** `extras_us_cities.jsonl`: `washington-q61` (name "Washington, D.C.", place
  "District of Columbia", lon/lat above, region "United States", kind "town", QID, wikipedia,
  `aerial_ok: true`, the note). `files_us_cities.jsonl`: the three rows below, each with the
  hand-recorded `caption_coords` evidence (`named_place` "Washington", `place_qid` Q61, place = site
  point, dist 0; `cat: null`). `classified_us_cities.jsonl`: plan/plan/plan, `by: "hand"`.

### The L'Enfant plan (1791, first printed 1792)

- **What it is.** Pierre Charles L'Enfant's 1791 plan of the city - the designed grid, the diagonal
  avenues, the squares - as its **first printed edition** (The universal asylum, and Columbian
  magazine, Philadelphia, Mar. 1792, printed from the same plate). The 1791 manuscript itself is at
  NARA, not on Commons (searched), so the known drawing date is on the row: `date: "1791"`,
  `date_commons: "1792"` (the known-date swap fired, same shape as the 1811 NY swap).
- **Where the files live.**
  - **STAGED** - `File:Plan of the city of Washington LOC 88694159.tif` (6426x5105, Public domain,
    page date 1792; the page's own finding-aid note: "1st printed edition of the L'Enfant plan").
  - DROP - `File:Plan of the city intended for the permanent seat of the government of t(he) United
    States - projected agreeable to the direction of the President of the United States, in
    pursuance of an act of LOC 91684074.jpg` (12524x9023, Public domain, page date **1991**): a
    full-color **computer-assisted facsimile** of the 1791 manuscript (USGS/LoC/NatGeo) - a modern
    production, the owner's standing rule (no modern redraws presented as old); `keep()` would drop
    it at 1991 anyway.
  - DROP - `File:Plan of the city intended for the permanent seat of the government of the United
    States - projected agreeable to the direction of the President of the United States...
    (14726320702).jpg` (2000x1354, CC BY 2.0): a **2014 British Library photo of the 1882 Boogher
    redraft** - a later redraft, and a CC-licensed photograph, not the drawing.
  - DROP - `File:L'Enfant plan original.jpg` (6426x5105 - a duplicate of the staged 88694159 LoC
    raster with mislabeled finding-aid text), `File:L'Enfant plan.jpg` (4179x3404 - a smaller
    duplicate), `File:L'Enfant map of Wash., D.C. LCCN2005691999.jpg` (1536x982, 1792 - the small LoC
    copy) and `File:L'Enfant Plan 1791 Square No 15.jpg` (450x336 - a **detail crop**) - **
    duplicates or crops of the same picture** - one row per picture.
  - DROP - `File:Plan of the City of Washington - NARA - 102278589 (page 14).jpg` (3086x3190, 1803,
    no description): a different/later item, not the 1791 original.
- **Fit note for 212.** A flat plan of the drawn city, the whole L'Enfant grid well inside the 2000 m
  box: a similarity fit (scale + translation) of the street grid, the diagonal avenues and the
  shoreline - the strongest of the three DC anchors.

### The Ellicott plan (1792)

- **What it is.** Andrew Ellicott's 1792 engraved plan of the city - L'Enfant's design **surveyed and
  plotted from the true meridional line**, the **first official plan** of Washington (the page quotes
  Ellicott's meridional-line note; Slaughter collection, Wheat & Brun 531).
- **Where the files live.**
  - **STAGED** - `File:Plan of the city of Washington in the territory of Columbia - ceded by the
    states of Virginia and Maryland to the United States of America, and by them established as the
    seat of their government, (NYPL b15255319-434417).jpg` (6300x4976, Public domain, "Scan by NYPL")
    - no swap (page date = drawing date 1792).
  - DROP - `File:Plan of the city of Washington in the territory of Columbia - ... (NYPL
    b15385718-434422).jpg` and `.tiff`: **duplicate NYPL copies** of the same plan.
  - DROP - `File:Plan of the city of Washington in the territory of Columbia - ceded by the states
    of Virginia and Maryland to the United States of America, and by them established as the seat of
    their government, LOC 88694164.tif` (8824x6567, 1792): the page says **"Facsimile"** - a duplicate
    copy of the same plan, not the best file.
  - DROP - `File:Plan of the city of Washington in the territory of Columbia, ceded by the states
    of Virginia and Maryland to the United States of America ... (8249620373).jpg` and
    `(cropped).jpg` (2000x1578, CC BY 2.0): a **2012 British Library photo** (and a crop of it) - a
    photograph, not the drawing.
  - DROP - `File:A Plan of the city of Washington in the territory of Columbia - btv1b53089832z
    (1 of 2).jpg` (9284x6544) and `(2 of 2).jpg` (9338x6590, Public domain, book date c. 1800):
    **book-page scans** of a printed edition - the plan inside a book, a later reprint.
  - DROP - `File:Plan of the City of Washington in the Territory of Columbia ceded by the States of
    Virginia And Maryland to the United (IA dr plan-of-the-city-of-washington-in-the-territory-of-
    columbia-ceded-by-the-st-00024059).jpg` (6480x4980): the **Reid & Rollinson 1794/95 atlas copy -
    the page says "not an exact copy"** - a redraft of the plan, and a later one at that.
  - DROP - `File:Plan of the city of Washington. LOC 88694118.jpg` (1794, Morse/Stockdale) and
    `File:Plan of the city of Washington. LOC 88694112.tif` (1798, Weld/Stockdale): **later
    reprints** of the same plan.
  - DROP - `File:Ellicott plan.jpg` (800x654): **too small** to fit.
- **Fit note for 212.** Flat plan, the same extent as the L'Enfant drawing: a similarity fit; where
  the 1791 and 1792 sheets disagree (survey corrections), both rows anchor the same grid.

### The Civil War defences (1865)

- **What it is.** The War Department's 1865 map of the fortification ring around the capital
  (Barnard's ring - Fort Stevens, Fort Marcy, Fort Totten, ...), from the Atlas accompanying the
  Official Records (v. 2, pl. XXXIX, no. 1): the earthworks of the Civil War, hachured, with the city
  centre inside.
- **Where the files live.**
  - **STAGED** - `File:Map of the defences of Washington. LOC 88690674.jpg` (2800x3802, Public
    domain, 1865, "From Atlas accompanying Official Records"); classified `p_plan: 1.0` by hand.
  - DROP - `File:Map of fortifications and defenses of Washington. LOC 88690671.jpg` and `.tif`
    (1832x2464, 1865, "Appendix A"): a **book-page copy** of the same War Department map.
  - DROP - `File:Map of the environs of Washington - compiled from Boschkes' map of the District of
    Columbia and from surveys of the U.S. Coast Survey showing the line of the defences of Washington
    as constructed LOC 88690673.tif` (17457x15796, 1865, Barnard/Boschke/Coast Survey, No. 187 L.):
    a **different compilation map** (the same ring, larger and coarser) - an alternative, not the
    ring map itself.
  - DROP - `File:Defenses of Washington, extract of military map of N.E. Virginia - showing forts
    and roads LOC 88690675.jpg` and `.tif` (4582x5805, 1865, Delafield): the **NE-Virginia extract**
    of the military map - the same region, not the city ring map.
  - DROP - `File:Defenses of Washington. -Maps 1 through 12 accompanying General Barnard's report.-
    - NARA - 305800 (page 1..12).jpg` (1865, per-page scans): the **twelve sector maps** of
    Barnard's report - the per-fort detail source for the forts' own sites, too small per page for
    the ring.
  - DROP - the earlier-state (1862) maps: `File:Topographical Map of the Original District of
    Columbia and Environs Showing the Fortifications around the City of Washington - DPLA -
    7db86d50c1170106213c63fbfbf34dda (page 1).jpg` (14840x13824) and `File:Topographical map of the
    original District of Columbia and environs showing the fortifications around the city of
    Washington LOC 88690604.tif` (10513x9635, Colton): the ring **before its completion** - an
    earlier state of the same ring (and the DPLA copy does not print "Washington" inside the
    gate's 600-char window either).
  - DROP - the NARA Brady photographs (Fort Totten, Fort Carroll, Fort Gaines): **photographs**,
    not plans.
- **Fit caveat for 212 (the extent case).** The drawn ring spans ~35 km against the 2000 m town box,
  so the similarity fit is **likely to end as a review item**, not a fitted plan - the Venice
  precedent; staging is what this task owes, not a fit. (The ring's earthworks are the 3DEP LiDAR
  case, like the mounds in 203a - for the forts' own sites.)

### The Boschke map (1857/1861) - not staged, and exactly why

The lead named in the task (the city after four decades of growth) **cannot be staged on Commons** -
not a missing file, a gate/heuristic wall, recorded here so the next session does not re-search:

- **1861, 2nd edition** - `File:Topographical map of the District of Columbia LOC 88694013.jpg`
  (12313x12090, Public domain, 1861, "Entered ... 1861, by D. McClelland, Blanchard & Mohun...",
  Phillips Washington 947) and its DPLA twins `File:Topographical Map of the District of Columbia
  Surveyed in the Years 1856, '57, '58 & '59 - DPLA - 24d5b35dccb58b1f43e387a1ccb0f5cb (page
  1).jpg` (12430x6367) and `(page 2).jpg` (12564x6338, Public domain, 1861, empty description):
  the caption prints **"Washington" only past the 600-character truncation** that `stage()`/`check()`
  use (normalized position ~830 in title+desc for the LoC copy; the DPLA twins do not print it at
  all), so the **named-place gate fails offline** - the design fail-loud (a live caption route would
  tie the file to a place only a name search found; we do not stage that).
- **1857, 1st edition** - `File:Map of Washington City, District of Columbia. Seat of the Federal
  Government. Respectfully Dedicated to the Senate and the (IA dr map-of-washington-city-district-
  of-columbia-seat-of-the-federal-governmen-12363000).jpg` (1457x1536, Public domain, David Rumsey):
  the only Boschke file whose **title** prints the city (the gate WOULD pass), but `commons.keep()`
  drops it: the description says **"a portrait of George Washington"** (one of the map's eighteen
  vignette illustrations) and matches the `NO` heuristic's "portrait" word - a **false positive**
  (the map is not a portrait). Also low-res for the large sheet. `pipeline/commons.py` is not in
  this task's `Touches:` - the `NO` regex is not changed here; the 1857 sheet is recorded, not
  staged.
- **1880, 3rd edition** - `File:Topographical map of the District of Columbia LOC 88693460.jpg`
  (6260x6881, Public domain, 1880): a later edition besides, and the same gate failure (no
  "Washington" in the title or the 600-char description).

## San Francisco (Q62)

- **The site point (REFINED, not a P625).** `san-francisco-q62` at (-122.40289, 37.79213) - the
  **midpoint of the two web-verified tips of the old town's drawn peninsula**, not either of Q62's two
  P625s (387 m apart, both downtown near the Civic Center / 10th & Market, 2.0-2.4 km SW of the point
  - outside the town box, no flag since `--verify` flags only >50 km). A = the historic **Rincon
  Point** (the SE corner of the drawn peninsula; enwiki "Rincon Point (San Francisco)": today
  "approximately along Spear Street from Harrison to Folsom Street"; the Nominatim Spear-street segment
  (37.7919285, -122.3933015)/(37.788381, -122.3889244) -> A (37.790155, -122.391113); cross-checked
  against Rincon Park (37.791195, -122.389541), ~175 m away). B = the **Washington & Jones corner**
  (the NW corner of the 1849 street grid - the old North Beach tip), the intersection of the Nominatim
  street lines (Washington St (37.7952016, -122.4060729)/(37.793173, -122.4220116); Jones St
  (37.7825459, -122.4123324)/(37.8062714, -122.417119)) -> B (37.794108, -122.414665). The midpoint,
  five decimals; the ~100-200 m street-centroid uncertainty is immaterial against the box below. (For
  the record: the 147 hand-over's "the tip lies south of both P625s / ~450 m" was wrong - the tip is
  NE of both, and the separation is 387 m; refining to the midpoint was the right branch anyway.)
- **The extent decision (acceptance box 2).** Kind "town" = the 2000 m box - 2 km x 2 km centered on
  the site point (`build_catalog.BOX` + `aw.site_bbox`, hw = width_m/2) - the same kind-default
  decision as New York and Washington DC (oversize sheets end as review items, not wider boxes).
  Measured, the box is lat 37.78315..37.80111, lon -122.41426..-122.39152: it covers the drawn
  peninsula tip to tip (2.1 km) **except a ~30 m overshoot at each drawn tip** (Rincon ~30 m past the
  east edge, Washington & Jones ~30 m past the west edge). The 1854 sheet's 1850s growth (the Center
  Street grid, the Market & 10th-11th corner, geocoded 2026-10-13) reaches the box's SW corner and
  slightly past it - an **oversize sheet**, so its fit is likely to end as a **review item**, not a
  fitted plan (the NY 1811 / DC ring precedent). (Correction: the 148 hand-over's "4 km box" was a
  hw = width_m miscalculation - the kind-default box is 2 km; every number in this section is
  measured against it.)
- **Staged rows.** `extras_us_cities.jsonl`: `san-francisco-q62` (name "San Francisco", place "San
  Francisco County, California", lon/lat above, region "United States", kind "town", QID, wikipedia,
  `aerial_ok: true`, the note). `files_us_cities.jsonl`: the three rows below, each with the
  hand-recorded `caption_coords` evidence (`named_place` "San Francisco", `place_qid` Q62, place =
  site point, dist 0; `cat: null`). All three print "San Francisco" **in the title** (gate-safe).
  `classified_us_cities.jsonl`: plan/plan/plan, `by: "hand"`.

### The Eddy survey map (1849)

- **What it is.** William M. Eddy's map **compiled from the field notes of the official re-survey** of
  the town - the ORIGINAL manuscript (LOC's presentation copy: "Presented to the Senators and
  Representatives from California by Wm. M. Eddy, city surveyor, San Francisco, Dec. 31st 1849"),
  pen-and-ink and watercolor on cloth, 1:6,600: the whole old town, North Beach down to Rincon Point.
- **Where the files live.**
  - **STAGED** - `File:Official map of San Francisco compiled from the field notes of the official
    re-survey made by Wm. M. Eddy. surveyor of the town of San Francisco. LOC 77692722.jpg`
    (6454x8480, Public domain, page date "1849" - no swap: page date = drawing date).
  - DROP - `File:Official map of San Francisco. LOC 76695582.jpg`/`.tif` and `File:Official map of San
    Francisco, compiled from the field notes of the official re-survey made by William M. Eddy,
    surveyor of the town of San Francisco, California. LOC 76695583.jpg`/`.tif` (Public domain, 1849,
    "Entered ... by Henry Reed", lith. F. Michelin, NY): **two printed 1849 editions of the same
    staged plan** - one row per plan, the NYC Ratzer re-engraving precedent.
  - DROP - `File:Official Map of San Francisco, Compiled from the Field Notes of the Official
    Re-Survey made by William M. Eddy. Surveyor of (IA dr
    official-map-of-san-francisco-compiled-from-the-field-notes-of-the-officia-00194050).jpg`
    (6361x8362, no page date): a **third 1849 copy** ("the Eddy Map of San Francisco, the first City
    map, here in the second issue of 1849") - the same plan.
- **Fit note for 212.** Flat plan, the whole old peninsula tip to tip in the 2 km box (the ~30 m tip
  overshoots above): a similarity fit; the street grid, the 1849 shoreline and the tip carry it.

### The first published map (1850)

- **What it is.** The 1850 map body "MAP OF THE CITY OF SAN FRANCISCO CALIFORNIA - COPIED FROM
  ORIGINALS WITH CORRECTIONS AND ADDITIONS - 1850" (Sun Lithographic Establishment, NY) - the first
  map **published** after the Eddy survey: all streets, Agnew's Steamboat Landing, Central Wharf, the
  Apollo storeship, Yerba Buena Cemetery, Rincon Point, hachured hills, and the inset "View of San
  Francisco in 1850". The staged scan is from Joseph P. Beach's journal (son of Moses Yale Beach, New
  York Sun).
- **Where the files live.**
  - **STAGED** - `File:Map of San Francisco, Apollo storeship at the bottom.jpg` (1238x1536, Public
    domain, page date "1850-01-01" - no swap).
  - DROP - `File:(Covers to) Map of The City Of San Francisco, California. Copied From Originals with
    Corrections and Additions. 1850. View of (IA dr
    covers-to-map-of-the-city-of-san-francisco-california-copied-from-origi-10423001).jpg`
    (1074x1536): the same map's **leather covers + title page with the printer's ad**, not the map
    (the body is the staged Apollo file).
- **Fit note for 212.** Flat plan, the same extent as the 1849 sheet with the 1850 additions - the
  same similarity fit; the smallest of the three staged scans (1238x1536).

### The Eddy 'full and complete' sheet (1854)

- **What it is.** The Eddy 1854 sheet (the map itself is dated **January 15th 1854**; printed without
  color, red lines added by hand - the outer red line is the water front, the inner the shore line;
  block and lot numbers, wards) - the 1850s growth around the old town. The file page lost the
  drawing's date, so the known survey date is on the row (`date: "1854"`, `date_commons: ""` - the
  swap fired; the golden normalizes the empty page value to 0000-00-00).
- **Where the files live.**
  - **STAGED** - `File:Official map of the City of San Francisco, Full and complete to the present
    date. Compiled by Wm., M. Eddy. City Surveyor. (IA dr
    official-map-of-the-city-of-san-francisco-full-and-complete-to-the-present-5870000).jpg`
    (8830x10560, Public domain, David Rumsey scan).
  - DROP - `File:A Topographical & Complete Map of San Francisco. Compiled from the Original Map, from
    the recent Surveys of W.M. Eddy (IA dr
    a-topographical-complete-map-of-san-francisco-compiled-from-the-original-12216000).jpg`
    (1331x1536): the **1852 Eddy sheet** (a pocket-map copy, the covers dated 1853; Heckrotte 30) - a
    distinct plan, but the only Commons copy is a small IA book scan (the full-res original is on
    David Rumsey's site, not Commons) and the staged 1854 sheet covers the same ground at 8830 px -
    the NYC 1811-grid precedent (too small to carry a fit).
  - DROP - `File:Map of the City and County of San Francisco- carefully compiled from recent surveys
    ... Drawn for the San Francisco News (IA dr
    map-of-the-city-and-county-of-san-francisco-carefully-compiled-from-recent-11809000).jpg`
    (1536x1333): the **Butler city-and-county map** (drawn for the San Francisco News / Pacific Mining
    Journal; "city boundaries 1850-1863", ranchos) - the only Commons copy is a small IA scan, and
    the page prints no date (the well-known Butler map is 1872 - web-verify before asserting it
    anywhere).
- **Fit caveat for 212 (the extent case).** The sheet extends past the box's SW corner into the 1850s
  growth (above) - **likely a review item**, not a fitted plan (the NY 1811 / DC ring precedent);
  staging is what this task owes, not a fit. The **red water-front line** is the strongest anchor
  where the shoreline is still recognizable.

### The Vioget plan (1839) - STAGED (2026-10-13, the 4th SF row)

`File:1839 Plan of Yerba Buena (Jean Jacques Vioget).jpg` (2400x2107, Public domain, page date
1839-01-02 = the drawing's date, no swap): the **first plan of the old town** - Yerba Buena, the
settlement that became the city (the page: "Plan of Yerba Buena (which was later renamed to San
Francisco), as laid out by Jean Jacques Vioget"), published 1853 as a deposition exhibit (NARA 33300):
the street grid centered on Portsmouth Square, the hachured shoreline, the named lots - the drawn
extent (the old core, ~1 km) sits inside the 2 km box. **Gate-safe**: the description prints "San
Francisco" inside the 600-char window, `commons.keep()` passes (both checked live 2026-10-13). It
surfaced in the 147 searches **after** that verdict's drop list was written, so it is not among the
rows above. **STAGED (iteration 150)**: the 4th SF row - no known-date swap (the page date IS the
drawing's date), the staged row's `name` is "San Francisco, the Vioget plan (1839, the first plan of
the old town)"; `--check` now 11/11.

### The Ringgold 1849 town plan - NOT on Commons

The task's "Ringgold" lead ("A General Plan of the Town of San Francisco...") is **not on Commons**:
every Ringgold + San Francisco query (checked live 2026-10-13) returns only **nautical charts** -
e.g. `Chart of the Farallones and entrance to the Bay of San Francisco, California by Cadwalader
Ringgold, Commander (IA dr ...00894047).jpg`, `Chart of the Bay of San Pablo Straits Of Carquines and
part of the Bay of San Francisco California By Cadwalader Ringgold (IA dr ...00894037).jpg`,
`General Chart, Embracing Surveys of the Bays of San Francisco and San Pablo, Straits of Carquines and
Suisun Bay (IA dr ...2590005).jpg`, `General chart embracing surveys of the Farallones, entrance to
the Bay of San Francisco, bays of San Francisco and San Pablo (IA dr ...00894046).jpg` - charts and
survey sheets are background, not drawings (the owner's standing rule). The town plan survives in
books and reprints, not as a Commons file; the 1849 Eddy row above covers the survey-plan lead.

### Dropped views, photos and noise (this task's searches)

- **Henry Bill 1856/1858** - `1856 Henry Bill Map and View of San Francisco, California - Geographicus
  - SanFrancisco-bill-1856.jpg` (3500x1974) and `-1858.jpg` (4000x2325) (both Public domain, page date
  "1856 (dated)"): a **VIEW** map - "Reveals San Francisco as seen from Nob Hill looking down
  California Street". Bird's-eye views are **task 236b's** domain (its own staging files); recorded
  here as a **236b lead**, not staged by this task.
- The **HABS files** from the same searches (1849-50 abandoned ships, the 1849 G. H. Burgess view, the
  1852 plat-map re-photograph): **photographs**, not plans.
- `J.W. Freeman, J.W. Aldrich, P.G. Everett, James Moore 1849, F.J. Barnes, I.R. Loranger, R.L. Beamer
  1849. (Drawn by) E. W(yttenbach). De (IA dr ...01104336).jpg`: a sheet of seven **lithographed
  portraits**, not a map (search noise).
- `Map of the harbour of San Francisco and its vicinity. By Captn. F. W. Beechy R. No. Published by
  James Gordon Bennett (IA dr ...11955001).jpg` (the Beechy 1827 harbour plan): **gone from Commons**
  (title changed/deleted, info() returns no url) - and a harbour chart anyway.

## Nashville (Q23197)

The fourth owner-named city (staged 2026-10-14, iteration 173): four plans on the new
`nashville-q23197` site - the 1804 Clayton/Temple plan, the 1860 Haydon & Booth plan, the 1860s O.M.
Poe military survey and the 1895 Civil War fortification atlas plate (the panels surveyed
Nov 30 - Dec 1864). All four titles print "Nashville" in the title itself, so the named-place gate
(`fit/evidence.py:check_caption`) is safe on every row.

- **The site point (REFINED, not a P625).** `nashville-q23197` at (-86.78152, 36.16529) - the
  **center of the projected 1804 drawn extent** (1.82 x 0.96 km, the mirror fit below), not Q23197's
  P625 (-86.774444, 36.162222): P625 is 721 m NE of the point (no >50 km flag), and its 2000 m town
  box overshoots the 1804 extent's west edge by 543 m (margins on the extent: W -543 / E +726 / S
  +860 / N +178 m) - the 147/148 San Francisco precedent (center of the drawn extent, five
  decimals). The 2 km box centred on this point covers the 1804 scene with margins W +92 / E +91 /
  S +519 / N +519 m. Kind "town" = the 2000 m box: the other three staged sheets span well beyond
  it, so their fits are **review items, not wider boxes** (the NY 1811 / DC 1865 ring precedent; an
  extras row cannot carry its own extent - see the New York extent decision).
- **Staged rows.** `extras_us_cities.jsonl`: `nashville-q23197` (name "Nashville", place "Davidson
  County, Tennessee", lon/lat above, region "United States", kind "town", QID, wikipedia,
  `aerial_ok: true`, the note - aerial ground, the mirror fit, the P625 rejection, the oversize
  review-item caveat, and the Fort Negley fort-site candidate). `files_us_cities.jsonl`: the four
  rows below, each with the hand-recorded `caption_coords` evidence (`named_place` "Nashville",
  `place_qid` Q23197, place = site point, dist 0; `cat: null`). `classified_us_cities.jsonl`: plan
  on all four, `by: "hand"`. Row date facts: the Clayton row takes the known-date swap
  (`date: "1804"`, `date_commons: "1880"` - the page's 1880 is Clayton's book publication); Haydon
  needs no swap (page date 1860 = drawing date); the LOC/Poe row needs no swap either (the page's
  precision-8 "1860s" IS the LOC-verified drawing date "[186-]", so the row keeps the raw page
  string, `year: 1860`); the 1895 plate swaps to the atlas's verified publication year
  (`date: "1895"`, `date_commons: ""` - the title is undated; the golden normalizes the empty page
  value to 0000-00-00).

### The Clayton/Temple plan (1804)

- **What it is.** The 1790s town of Nashville "from the notes of one then resident (Mrs Temple,
  Daughter of Genl Robertson)" - the oldest staged Nashville drawing, engraved in 1880 for
  Clayton's History of Davidson County. The sheet (2557x1913) is a **near north-up bird's-eye view**
  of the town between the rivers' corner and the Rich Branch: a REFERENCES index (1-20) tops the
  sheet; the labelled streets are Broad / Church / Cedar (vertical) and Summer / College / Market
  (horizontal) - modern Broadway is the drawn "Broad"; the hatched fort block, White Hall ("former
  Fort"), the Nashville Inn, Dr. Henning's house, the cemetery, McNairy's and the Sulphur springs
  all carry their 1804 labels; the rivers' corner runs as a hatched band along the bottom (the 1804
  author labelled the whole band "Cumberland River"), two arms merging at a V in the sheet's SE
  corner, with the Rich Branch entering east of the town.
- **Where the files live.**
  - **STAGED** - `File:1804 Map of Nashville published 1880.jpg` (2557x1913, Public domain, page
    date 1880 = the book's publication): the known-date swap fired (`date: "1804"`,
    `date_commons: "1880"`).
  - DROP - the Burns 1906 copy of the same 1804 plan (1018x704, page 1906): the same plan - one row
    per plan (the Ratzer precedent).
- **The mirror fit (212's fit model, and the basis of the site point).** The sheet is a view from
  above the town, so the right model is a mirror similarity w = a*conj(z) + b (a page-up
  reflection), NOT a flat-plan similarity. Over anchor A = the fort pin (746,1362) <-> Q5471739
  (36.164167, -86.774444) and B = the "now. Capitol Hill" wooded knoll (1750,1040) <-> Nominatim way
  249147622's centroid (36.1658290, -86.7842374), with the ENU origin (36.163, -86.775), it gives
  a-angle -174.1 deg, 0.8520 m/px: page-up projects to 354.1 deg (~N) and page-right to 264.1 deg
  (~W) - a near north-up bird's-eye view with a ~6 deg tilt. Independent checks: the drawn rivers'
  V (490,1680) projects **207 m** from the real OSM confluence node 303579826 (36.1606686,
  -86.7700322) (the dead rotation fit would place it 521 m away) and 7 m from the mapped Cumberland
  way; the Rich Branch mouth (2222,1620) projects to (36.161022, -86.788123) - the west riverfront
  (12th-15th Ave S) - agreeing with the independent Haydon 1860 cross-check (below); the river
  flows left -> right on the page = **westward = the Cumberland's true flow** (the 170 rotation fit
  w = a*z + b is dead: it placed the river north of the town); the fort is the town's SE corner.
  Projected scene extent (scene box x 448-2496, y 678-1600): lat 36.16096..36.16963, lon
  -86.79163..-86.77140 = 1.82 x 0.96 km (the dense core (718-1790, 986-1575) is 0.96 x 0.59 km; the
  full ink including the REFERENCES index and the title is 2.20 x 1.38 km - it still fits the 2 km
  box). **Fit note for 212:** use the mirror similarity, anchored on the fort and the capitol
  knoll. Caveat (recorded, not a fit blocker): the drawn street families do not match the modern
  ones under either fit (map-horizontal -> 84.1/264.1 matches Division St within 6 deg; map-vertical
  -> 354.1/174.1 is ~67 deg off modern Broadway) - perspective convergence and/or the 1796 plat's
  own orientation; the anchors are the evidence. The bottom river band is bent 40-60 deg for
  composition (the decorative-rivers pattern: trust the town, not the drawn V or the mouth).

### The Haydon & Booth plan (1860)

- **What it is.** John Haydon and Booth's 1860 city plan - title block: "CITY OF NASHVILLE AND
  EDGEFIELD, DAVIDSON COUNTY, TENNESSEE. Published by Hayden and Booth. 1860. SCALE 400 FEET TO 1
  INCH." A **decorative composite, not a single survey sheet** (the finding below).
- **Where the files live.**
  - **STAGED** - `File:1860 Haydon map of City of Nashville and Edgefield.jpg` (10000x6082, Public
    domain, page 1860 = drawing date - no swap).
- **The composite finding (why it cannot carry a whole-sheet georef).** The labelled CUMBERLAND
  band runs across the sheet's middle (y ~3900-4300 for x ~3160-6300) and the dense downtown core
  sits NORTH of it (x ~3250-5750, y ~2700-4250) - geographically correct - but the blue TENNESSEE
  arm enters upper-left and the combined river exits lower-left: the map's V (3288,4302) is a right
  angle while the real confluence is nearly a straight line - the rivers are **bent for
  composition** (the Clayton pattern); the compass rose (~(7185,1425)) is a decorative 8-point
  star; the plates are tacked together at different rotations (the core plate is the modern CBD;
  the OVERTOWN/EDGEFIELD diagonal grids; the FILLMORE/BARROW grid south of the river; the "Shelby"
  floodplain; the red 1860 Corporation Line; the REFERENCES legend and the CHURCHES list).
  Consequence: the sheet is usable only **qualitatively** (the core plate = the modern CBD) and for
  the site-note extent estimate from labelled landmarks (the Franklin Turnpike, the Wesleyan College
  green, Howard School, the T&A RR line, the red Corporation Line); the 1833 waterworks reservoir
  is dead as an anchor (the 1860 built-up ground covers the site). Pins (full sheet): confluence V
  (3288,4302), capitol (4880,3193), Rich Branch mouth (3836,3981) - the mouth is the cross-check
  that closed the site point: it projects to the west riverfront under the 1804 mirror fit, an
  independent 1860 confirmation of the 1804 sheet. **Fit caveat for 212:** the sheet spans well
  beyond the 2 km box (the ring of suburbs and the two arms of the bent river) - its fit is likely
  to end as a **review item** (the NY 1811 precedent).

### The O.M. Poe survey map (1860s, LOC 2003630459)

- **What it is.** The big 1860s building-by-building survey of the whole city, from the Chief
  Engineer's Office, Headquarters Military Division of the Mississippi: pen-and-ink (black) and
  lead pencil on cloth, fold-line relief, every building. The signature (lower right, confirmed at
  6x): "From Chief Eng'rs Office / H'd Qu'rs Mil'y Div'n of the Mis. / O.M. Poe / Capt. & Actg
  Chf Eng'r (17x29.)" - the (17x29.) is the **sheet size** (17 x 29 inches, the LOC cataloguing
  convention), not a date, and the scan (19690x11294, ~664-679 px/in) is the whole sheet. The LOC
  record (loc.gov/item/2003630459) dates the drawing "[186-]" - the Commons page's precision-8
  "1860s" IS the LOC-verified drawing date, so there is **no known-date swap** (the row keeps the
  raw page value, `year: 1860`).
- **Where the files live.**
  - **STAGED** - `File:Map of Nashville, Tennessee. LOC 2003630459.jpg` (19690x11294, Public
    domain).
- **The extent estimate (the review-item number).** The printed scale bar spans 0-12000 ft with
  100-ft subdivisions over the first 500; the ticks measure ~600-604 px per 1000 ft ->
  **~0.50-0.51 m/px, scale ~1:13,500** (1 in ~= 1100 ft). A 29 x 17 in sheet at that scale is
  **~10.0 x 5.7-5.8 km**, and the drawn content (the city core, a ring of named suburbs, both
  rivers, the N&C and N&W RRs plus a "Proposed RR", the City and Catholic cemeteries and country
  with contours) runs nearly to **all four sheet edges** - ~10 x 5.7 km drawn against the 2 km town
  box = **3-5x over-size -> review item** (the NY 1811 / DC 1865 ring precedent). Orientation: the
  LOC record says "Oriented with north toward the lower right"; the independent read agrees with
  the street grid (Broad/Union/Decatur/Washington vertical, Vine/College/Market/High/Park
  horizontal; the State Capitol hill and building, Market Square/City Hall/Court House, the
  University & Western Military Institute all legible). The rivers' confluence is drawn as a
  compressed ~90-degree V at the lower-right of the dense core (junction ~0.7 km from the capitol
  by pixel measure vs ~1.4 km real - the rivers bent for composition; for any future fit, trust
  the street grid, not the V). The handwritten "1" = 10000" scale note (1:120,000) **disagrees
  with the bar** - impossible for a building-by-building map (a 10 m house would be 0.08 mm) - the
  bar's value stands, the note is recorded as a discrepancy.

### The Civil War fortification atlas plate (1895, surveyed Nov 30 - Dec 1864)

- **What it is.** One page (1536x886) of the **atlas to accompany the official histories of the
  Union and Confederate armies, 1861-1865** - the header, confirmed at 6x zoom, reads exactly that
  (plus "PLATE" and a Roman numeral: CXIII/CXIV/CXVIII - not legible at this resolution, the hedge
  stands). The scanned copy is the **Julius Bien 1895 edition** (the first edition is 1884-85 per
  the plate header; not verifiable online from this machine - the routes died, the blocked-route
  notes in DECISIONS 152/175); the row's date is the scanned copy's verified 1895. The task's
  1660-1880 window is a description, not a rule: a Civil War fortification plan is a drawing by the
  owner's standing rule (the DC 1865 ring precedent), and this is that case. The page is a
  **multi-panel plate: nine independent fort/battery plans, each with its own "Scale of Feet" bar
  (~100-400 m per panel at those bars)** - too small to georef individually; the only city-wide
  content is the small "Plan of Nashville, Tenn." inset in the Fort Hill panel, which shows the
  whole ring a few centimetres wide - too small to georef. The panels (surveyed Nov 30 - Dec
  1864): 1 Chattanooga Battery Erwin, 2 Battery Coolidge, 3 Nashville Magazine Battery "Dec. 1864"
  (Eng. Capt. J.S. Wheatley), 4 Nashville Capitol "Nov. 30, 1864" (Eng. Capt. J. St. Clair Morton),
  5 Fort Dan McCook "Dec. 21, 1864" (planned by Brig. Gen. James Ste. Clair Morton; showing
  changes by Brig. Gen. J.H. Torbert, U.S. Eng'rs - confirmed at 6x), 6 Fort Morton "Dec. 1864"
  (Eng. Capt. H.K. Wright), 7 Fort Hill "Dec. 1, 1864" (+ the small "Plan of Nashville, Tenn."),
  8 Fort Nashville, 9 the Nashville Heights "Dec. 1864" - **7 of 9 Nashville**. **Panel-caption
  caveat:** panels 3, 8 and 9 are only partly legible at 1536 px and the two sessions that read
  them differ (panel 3: "Nashville Magazine Battery" vs a "BATTERY FOR CASI..." [= ? Casino Hill]
  designed for the Tennessee Army; panel 8: "Fort Nashville" vs "Fort Washington, Tenn."; panel
  9: "the Nashville Heights, Dec. 1864" vs "Redoubt on Hill No. 230. Not yet completed. November
  30th, 1864.") - no high-res route works from this machine (David Rumsey is reCAPTCHA-walled on
  every ID form, the LOC keyword search does not surface the atlas, the IA item 01104241 is gone) -
  the readings above (152) stand with that explicit hedge; the row's date 1895 and the surveyed
  Nov 30 - Dec 1864 range stand either way. **Fort Negley (Q5471744) is NOT among the nine panels
  on this sheet** (151's thumbnail-era reading claimed a "Fort Negley (plan + A-B section +
  magazine)" panel; the 152/175 close reads settle the nine as listed - and the fort's P373
  category holds only photos and the three Fletcher views, no plan): the sheet is the task's Fort
  Negley lead realized as the **city-defences** sheet (the DC 1865 ring precedent), staged on the
  city, not on a fort.
- **Where the files live.**
  - **STAGED** - `File:Defenses of Chattanooga, Tenn. Battery Erwin ... Battery Coolidge. Defenses
    of Nashville, Tenn. Capitol (IA dr
    defenses-of-chattanooga-tenn-battery-erwin-battery-coolidge-defenses-01104241).jpg` (1536x886,
    Public domain; the "..." in the title is three literal dots; no page date - the atlas's
    verified 1895 publication is on the row, and required: the undated title has no
    plan/map/survey word for `keep()`).
- **Fit caveat for 212 (the extent case).** Each panel is ~100-400 m (its own scale bar), but the
  nine panels together span the whole defences ring (the Nashville heights north/east of the city,
  plus the Chattanooga batteries at the plate's other end) - well beyond the 2 km town box - so
  the sheet's fit is likely to end as a **review item**, not a fitted plan (the DC 1865 ring
  precedent); the 1864 earthworks are the 3DEP LiDAR case (the mounds in 203a), like the DC ring.

**Fort Negley (Q5471744) - a fort site only when a fort-only plan appears.** The large Civil War
earthwork sits ~1.9 km south of the city P625 (36.145097, -86.774658). No fort-only plan is on
Commons (the fort's P373 category is photos and the three Fletcher 1864 views; every
"Negley"/"plan of Fort Negley"/"defenses" search came up with none) - and a staged site without a
picture fails `check_staged()` - so **no fort site is staged**: the candidate is recorded on the
city's site note (kind "fort", 1600 m box, a 3DEP LiDAR candidate - the 203a mounds precedent) and
this task is done. **236b leads (record, do not stage here):** the three Fletcher 1864 lithograph
VIEWS of Fort Negley (drawn by W.H.H. Fletcher, 12th Battery Ind. Vols.; the SE one inscribed
"Filed Dec 31, 1864"; Public domain, page date 1864) - `File:South west view of Fort Negley
LCCN2003655690.jpg` (7950x3822) + `.tif` (7964x4356), `File:North west view of Fort Negley
LCCN2003655670.tif` (7964x4356), `File:South east view of Fort Negley LCCN2003655689.jpg`
(8082x3978) - bird's-eye views are task 236b's domain (the Henry Bill precedent).

### Dropped plans, maps and photos (this task's searches, 2026-10-13)

- **The Burns 1906 copy of the 1804 plan** (1018x704, page 1906): the same plan as the staged
  Clayton file - one row per plan (the Ratzer precedent).
- **The 1854 Putnam "Detail"**: a cropped fragment - too small to fit.
- **The 1888 Sanborn fragment** (491x572): too small.
- **The 1916 Marshall & Bruce map**: outside the 1660-1880 window, commercial.
- **The 1887 Cowen battle map** (1:110,000): a battle map, not a city plan (outside the window
  besides).
- **The 1895 Bien Nashville-and-Franklin battlefield map** - settled 2026-10-14: the atlas group's
  own battle pages, IA items 01104200 and 01104201 of the same David Rumsey group (1780.000) as the
  staged plate - 01104200: "Battle-fields in front of Nashville, Tenn., where the United States
  forces commanded by Major-General Geo. H. Thomas, defeated and routed the rebel army under
  General Hood, December 15th and 16th 1864. Surveyed and drawn under the direction of Gen. Tower
  by M. Peseux, C.S. Mergell, auth. (with) Battle-field in front of Franklin, Tenn. ... November
  30th, 1864 ... Julius Bien & Co., Lith., N.Y. (1891-1895)" (year 1895); 01104201: the companion
  Merrill/Willett topographical battle-field sheet - **DROP: a battle map, not a city plan** (the
  Cowen precedent).
- **All the Fort Negley photos** (the fort's P373 category, 12 files): Barnard 1864 ("Fort negley
  1864.jpg", lowercase n - undated, no plan/map/survey word, fails `keep()`); LCCN2007662878;
  Webster & Albee ca. 1890; 2019 CC-BY ruins; the modern park shots - **photographs, not plans**
  (the three Fletcher views among them are the 236b leads, above).

## Offline check

`.venv/bin/python fit/src_us_cities.py --check` (2026-10-14, all 15 staged rows): no join problems,
and

```
PASS caption_coords  new-york-q60|File:Afbeeldinge van de Stadt Amsterdam in Nieuw Neederlandt (NYPL Hades-118555-54682).tif
PASS caption_coords  new-york-q60|File:Plan of the City of New York by Bernard Ratzer, 1767.jpg
PASS caption_coords  new-york-q60|File:Commissioners' Plan of 1811 by John Randel published in 1821.jpg
PASS caption_coords  new-york-q60|File:Viele Map (Topographical map of the City of New York), 1865.jpg
PASS caption_coords  washington-q61|File:Plan of the city of Washington LOC 88694159.tif
PASS caption_coords  washington-q61|File:Plan of the city of Washington in the territory of Columbia - ceded by the states of Virginia and Maryland to the United States of America, and by them established as the seat of their government, (NYPL b15255319-434417).jpg
PASS caption_coords  washington-q61|File:Map of the defences of Washington. LOC 88690674.jpg
PASS caption_coords  san-francisco-q62|File:Official map of San Francisco compiled from the field notes of the official re-survey made by Wm. M. Eddy. surveyor of the town of San Francisco. LOC 77692722.jpg
PASS caption_coords  san-francisco-q62|File:Map of San Francisco, Apollo storeship at the bottom.jpg
PASS caption_coords  san-francisco-q62|File:Official map of the City of San Francisco, Full and complete to the present date. Compiled by Wm., M. Eddy. City Surveyor. (IA dr official-map-of-the-city-of-san-francisco-full-and-complete-to-the-present-5870000).jpg
PASS caption_coords  san-francisco-q62|File:1839 Plan of Yerba Buena (Jean Jacques Vioget).jpg
PASS caption_coords  nashville-q23197|File:1804 Map of Nashville published 1880.jpg
PASS caption_coords  nashville-q23197|File:1860 Haydon map of City of Nashville and Edgefield.jpg
PASS caption_coords  nashville-q23197|File:Map of Nashville, Tennessee. LOC 2003630459.jpg
PASS caption_coords  nashville-q23197|File:Defenses of Chattanooga, Tenn. Battery Erwin ... Battery Coolidge. Defenses of Nashville, Tenn. Capitol (IA dr defenses-of-chattanooga-tenn-battery-erwin-battery-coolidge-defenses-01104241).jpg
evidence: 15 rows, 15 pass, 0 fail, 0 no-tie
```

The join rules it enforces: every staged file row names a staged or existing site, a staged id or QID
is a problem only when it resolves to a **different** site (after 236c's first-row-wins merge the
module's own rows are a no-op, not a collision), every staged site has a picture, (site, title)
unique, no clash with the canonical `files.jsonl` (a same-key different row still fails loud), and the
classified rows are 1:1 with the file rows. The same guards, and a staged-row negative control
(Castello row with the Venice point - ~6681 km, the name-search-style resolution a live record could
store - must report FAIL), are pinned in `tests/test_src_us_cities.py` (offline, socket blocked).
