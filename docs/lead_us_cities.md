# Old plans of US cities (task 236a)

GOAL.md point 5 (the 2026-10-13 owner change): the map grows with US cities - "lets also add US cities
like nashville or dc or SF or New York. Those had to have had some survey stuff as well." Town plans and
views count as drawings (exempt from the 150-year rule); plain survey sheets (Coast Survey charts, USGS
quads) are background, not drawings. This task stages the **named city plans** (manuscript and engraved
plans, 1660-1880): New York in this session - the **Castello plan (1660)**, the **Ratzer map (1767)**,
the **Commissioners' Plan (1811)** and the **Viele map (1865)**; Washington DC, San Francisco and
Nashville in later sessions. Bird's-eye/panoramic views of the same and other US cities are task 236b.
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

**Staged (in the table):** New York City Q60, re-verified against Wikidata - label, every P625 value
(flagged when >50 km from the table point), P373, P131 (with labels), the enwiki article, and the first
name-search hit with coordinates (what `record --live` would resolve for the caption route). No P625
flag fired; no search trap: the first search hit with coordinates is Q60 itself.

```
checked 2026-10-13 - 1 QIDs (Wikidata)
  Q60  'New York City'
      P625: [(-74.00611111111111, 40.71277777777778)]  (table site point: -74.006111, 40.712778)
      P373: ['New York City']
      P131: [('New York', 'Q1384')]  (table place: 'New York County, New York')
      enwiki: 'New York City'  (table wikipedia: 'https://en.wikipedia.org/wiki/New_York_City')
      search 'New York City': first hit with P625 is Q60 'New York City' (-74.00611111111111, 40.71277777777778)
```

**Prep-verified for the later sessions (checked 2026-10-13 via `pipeline/catalog_wd`; not in the module
table yet - the SF and Nashville site points are not final, the table stays honest):**

- **Q61 "Washington, D.C."** - P625 (-77.036667, 38.895) sits in the old L'Enfant core; the first
  name-search hit with coordinates is Q61 itself (no trap).
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
evidence: 4 rows, 4 pass, 0 fail, 0 no-tie
```

The join rules it enforces: every staged file row names a staged or existing site, a staged id or QID
is a problem only when it resolves to a **different** site (after 236c's first-row-wins merge the
module's own rows are a no-op, not a collision), every staged site has a picture, (site, title)
unique, no clash with the canonical `files.jsonl` (a same-key different row still fails loud), and the
classified rows are 1:1 with the file rows. The same guards, and a staged-row negative control
(Castello row with the Venice point - ~6681 km, the name-search-style resolution a live record could
store - must report FAIL), are pinned in `tests/test_src_us_cities.py` (offline, socket blocked).

## Washington DC (Q61) - later sessions

Leads to verify the same way (Commons or the Library of Congress; original or facsimile; the drawing's
date; licence; resolution): the **L'Enfant plan (1791, LoC)** - the designed city, the anchor; the
**Ellicott engraved plan (1792)** (L'Enfant's plan as surveyed by Ellicott, the first published
version); **Boschke's topographical map (1857/1861)** (the city after four decades of growth); the
**Civil War defences (Barnard, 1865)** - the earthwork ring around the capital (Fort Stevens, Fort
Marcy, ...). The ring spans ~35 km, far beyond the town box: each fort is a candidate **site of its
own** (kind "fort", 1600 m, its own QID) - the 203a precedent for LiDAR-visible earthworks; the whole
ring is the review-item case (as the 1811 sheet above).

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
