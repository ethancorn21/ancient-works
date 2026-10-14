# Old plans of US cities (task 236a)

GOAL.md point 5 (the 2026-10-13 owner change): the map grows with US cities - "lets also add US cities
like nashville or dc or SF or New York. Those had to have had some survey stuff as well." Town plans and
views count as drawings (exempt from the 150-year rule); plain survey sheets (Coast Survey charts, USGS
quads) are background, not drawings. This task stages the **named city plans** (manuscript and engraved
plans, 1660-1880): New York - the **Castello plan (1660)**, the **Ratzer map (1767)**, the
**Commissioners' Plan (1811)** and the **Viele map (1865)** - and Washington DC - the **L'Enfant plan
(1791, first printed 1792)**, the **Ellicott plan (1792)** and the **Civil War defences (1865)** - both
cities staged; San Francisco and Nashville in later sessions. Bird's-eye/panoramic views of the same and other US cities are task 236b.
The picture rows are staged in this task's own files (`data/catalog/extras_us_cities.jsonl`,
`data/commons/files_us_cities.jsonl`, `data/commons/classified_us_cities.jsonl`); **236c** consolidates
them into the canonical data and builds the sites, 212's cover runs the fitting loop.

**None of the four owner-named QIDs is in the catalog yet** (checked against `data/catalog/sites.jsonl`
and `extras.jsonl`, 2026-10-13), so every city gets a **new extras site row**, not picture rows on an
existing site. The region string "United States" needed a one-line addition to
`pipeline/build_catalog.py:REGION_NAME` (`"united states": "United States"` - 236b adds the identical
line; the old US extras rows keep their "US" region and are untouched).

**Ground.** The city sites are **aerial-photograph ground** (`aerial_ok: true` on every staged site row;
no open LiDAR over a built-up city - bare-earth LiDAR erases the streets). The street grid, the
shoreline, the squares and the church footprints carry the fit. Civil War fortification plans are the
exception: their earthwork banks may show on 3DEP bare earth (`pipeline/aw.py`), so each fort is a
candidate **site of its own** (kind "fort" = 1600 m box, its own QID) - the later DC/Barnard and
Nashville/Fort Negley sessions.

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

## QID verification (checked 2026-10-13, re-run with `.venv/bin/python fit/src_us_cities.py --verify`)

**Staged (in the table):** New York City Q60 and Washington DC Q61, re-verified against Wikidata -
label, every P625 value (flagged when >50 km from the table point), P373, P131 (with labels), the enwiki
article, and the first name-search hit with coordinates (what `record --live` would resolve for the
caption route). No P625 flag fired; no search trap: the first search hit with coordinates is the city
itself in both cases.

```
checked 2026-10-13 - 2 QIDs (Wikidata)
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
```

**Prep-verified for the later sessions (checked 2026-10-13 via `pipeline/catalog_wd`; not in the module
table yet - the SF and Nashville site points are not final, the table stays honest):**

- **Q62 "San Francisco"** - **TWO P625 values ~450 m apart, both downtown**; the old town's tip (the
  1849 plans' drawn extent) lies south of both, so the site point will be refined against the files at
  staging. The first search hit with coordinates is Q62 itself (no trap).
- **Q23197 "Nashville"** - P625 (-86.7744, 36.1622) is downtown east of the Cumberland; the old 1790s
  town sat at the river confluence (~-86.788, 36.166) - refine at staging. The first search hit with
  coordinates is Q23197 itself (no trap).

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

## Offline check

`.venv/bin/python fit/src_us_cities.py --check` (2026-10-13): no join problems, and

```
PASS caption_coords  new-york-q60|File:Afbeeldinge van de Stadt Amsterdam in Nieuw Neederlandt (NYPL Hades-118555-54682).tif
PASS caption_coords  new-york-q60|File:Plan of the City of New York by Bernard Ratzer, 1767.jpg
PASS caption_coords  new-york-q60|File:Commissioners' Plan of 1811 by John Randel published in 1821.jpg
PASS caption_coords  new-york-q60|File:Viele Map (Topographical map of the City of New York), 1865.jpg
PASS caption_coords  washington-q61|File:Plan of the city of Washington LOC 88694159.tif
PASS caption_coords  washington-q61|File:Plan of the city of Washington in the territory of Columbia - ceded by the states of Virginia and Maryland to the United States of America, and by them established as the seat of their government, (NYPL b15255319-434417).jpg
PASS caption_coords  washington-q61|File:Map of the defences of Washington. LOC 88690674.jpg
evidence: 7 rows, 7 pass, 0 fail, 0 no-tie
```

The join rules it enforces: every staged file row names a staged or existing site, a staged id or QID
is a problem only when it resolves to a **different** site (after 236c's first-row-wins merge the
module's own rows are a no-op, not a collision), every staged site has a picture, (site, title)
unique, no clash with the canonical `files.jsonl` (a same-key different row still fails loud), and the
classified rows are 1:1 with the file rows. The same guards, and a staged-row negative control
(Castello row with the Venice point - ~6681 km, the name-search-style resolution a live record could
store - must report FAIL), are pinned in `tests/test_src_us_cities.py` (offline, socket blocked).

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

## San Francisco (Q62) - later sessions

Leads: the **1849 plans (Eddy, Ringgold)** - the first surveys of the town that became the city;
**1850s city plans** (the growth around the bay). Q62 has **two P625 values ~450 m apart** (both
downtown); the site point will be the old town's tip (the drawn extent of the 1849 plans), refined
against the files at staging - recorded in the QID section.

## Nashville (Q23197) - later sessions

Leads: **early town plans** (the 1790s town at the confluence of the Cumberland and the Tennessee,
south of the modern downtown point); the **Civil War fortification plans of Fort Negley** (a large
earthwork on the west side of the city - a 3DEP LiDAR candidate, its own kind-"fort" site with its own
QID, as the DC forts).
