# Bird's-eye views of US cities, batch 5 (task 241): the final five cities of the 25-city total

GOAL.md point 5 (the 2026-10-13 owner change): the map grows with US cities, and artists' aerial
and bird's-eye views count as much as surveys. Batch 5 is the FINAL FIVE cities of the 25-city
total (16 from 236b + 4 from 240 + 5 here) after 236b's sixteen and 240's four (Denver, St. Paul,
Minneapolis, Cleveland), each a new site of its own in this task's own staging files. The source
is the **Library of Congress "Panoramic Maps" collection** (loc.gov/collections/panoramic-maps):
about 1,500 US bird's-eye views, 1847-1929, public domain. One own module
(`fit/src_us_birdseye_batch5.py`), one own staging file set (`*_us_birdseye_batch5.jsonl`) - the
module is a copy of 240's `fit/src_us_birdseye_batch4.py` (itself a copy of 236b's
`fit/src_us_birdseye.py`, the template it keeps in sync with); 236c consolidates every staging
set into the canonical data and checks the 25 total. Candidate order (240's lead-doc "Not done
yet" pointer, continuing the 181 candidate list of the 236b lead doc: "...Kansas City, Omaha,
St. Paul/Minneapolis, Indianapolis, Columbus, Memphis, New Orleans, ..."): **Omaha (LANDED -
city 1 of 5; 236b skipped it with no recorded drop reason and the re-run resolves it stageable -
it simply fell out of 236b's batch order, its pool has a strong pick), Indianapolis (LANDED -
city 2 of 5; the 1925 E. G. Spink Company sheet - the only whole-city view in its pool),
Columbus (LANDED - city 3 of 5; the 1872 H. H. & O. H. Bailey sheet - the only drawn whole-city
view in its pool, staged as its best of three scans), Memphis (LANDED - city 4 of 5; the 1870
A. Ruger sheet - the steepest (true oblique) whole-city view in its pool; the 1887 Wellge and
the 1887 "Appeal" newspaper page dropped on angle/scan), Portland (LANDED - city 5 of 5;
the 1890 J. McI. Wood perspective sheet - the only drawn whole-city view in its pool that
passes the 4000-px gate; the first city-5 candidate, Albuquerque, was researched and
dropped - its section below) - all FIVE LANDED. The task owes FIVE
staged cities, not specifically these - a city with no usable view gets a note here and the next
candidate.

## Fetch route (same as 236b's, re-verified for the batch-5 cities)

The route is the 236b one (full detail in docs/lead_us_birdseye.md, section "Fetch route"):
loc.gov is unreachable from this machine (403, CloudFront bot block), so the files are fetched
from their **Wikimedia Commons mirrors only**; the candidate pool per city is the Commons
file-namespace full-text search in the six plain-phrase forms ("bird's-eye view of <city>", "bird's
eye view of <city>", "birdseye view of <city>", "<city> bird's eye", "<city> birdseye", "Birds' eye
view of <city>", each + ` filetype:bitmap`, srnamespace 6, srlimit 40), deduped, then the gates:
`commons.keep()` (judged AFTER any known-date swap) AND the caption names the city (books_match.norm
over title + description) AND the license is **Public domain** AND the width is **>= 4000 px**.
Re-verified live for each batch-5 city at its landing (the per-city pool counts and verdicts land
in the city sections below).

## QID verification (`.venv/bin/python fit/src_us_birdseye_batch5.py --verify`)

The batch-5 QIDs are verified when their cities are added (label, every P625 value - flagged when
>50 km from the table point, P373, P131 with labels, the enwiki article, and the first name-search
hit with coordinates - what `record --live` would resolve for the caption route). The verbatim
transcript lands here with each landing (the 240 pattern: re-run with every landing and appended).

Transcript for Omaha (the 241 session-4 run 2026-10-14, verbatim):

```
checked 2026-10-14 - 1 QIDs (Wikidata)
  Q43199  'Omaha'  (site id: omaha-q43199, new (this task))
      P625: [(-95.9375, 41.25861111111111)]  (table site point: -95.9375, 41.25861111111111)
      P373: ['Omaha, Nebraska']
      P131: [('Douglas County', 'Q490695')]  (table place: 'Douglas County, Nebraska')
      enwiki: 'Omaha, Nebraska'  (table wikipedia: 'https://en.wikipedia.org/wiki/Omaha,_Nebraska')
      search 'Omaha': first hit with P625 is Q43199 'Omaha' (-95.9375, 41.25861111111111)
```

No FLAG / TRAP line on the Omaha QID: the single P625 IS the table point (dist 0) and the first
name-search hit with coordinates is the city itself (the 236b Pittsburgh/Chicago university
traps do not recur here; the in-city institution Q2495890 - the University of Nebraska Omaha -
never comes first, checked at both limit 5 and limit 20 in the session-3 research run).

Transcript for Indianapolis (the 241 session-6 run 2026-10-14, verbatim):

```
checked 2026-10-14 - 2 QIDs (Wikidata)
  Q43199  'Omaha'  (site id: omaha-q43199, new (this task))
      P625: [(-95.9375, 41.25861111111111)]  (table site point: -95.9375, 41.25861111111111)
      P373: ['Omaha, Nebraska']
      P131: [('Douglas County', 'Q490695')]  (table place: 'Douglas County, Nebraska')
      enwiki: 'Omaha, Nebraska'  (table wikipedia: 'https://en.wikipedia.org/wiki/Omaha,_Nebraska')
      search 'Omaha': first hit with P625 is Q43199 'Omaha' (-95.9375, 41.25861111111111)
  Q6346  'Indianapolis'  (site id: indianapolis-q6346, new (this task))
      P625: [(-86.158055555556, 39.768611111111)]  (table site point: -86.158055555556, 39.768611111111)
      P373: ['Indianapolis']
      P131: [('Marion County', 'Q506230')]  (table place: 'Marion County, Indiana')
      enwiki: 'Indianapolis'  (table wikipedia: 'https://en.wikipedia.org/wiki/Indianapolis')
      search 'Indianapolis': first hit with P625 is Q6346 'Indianapolis' (-86.158055555556, 39.768611111111)
```

No FLAG / TRAP line on either QID: each single P625 IS the table point (dist 0) and the first
name-search hit with coordinates is the city itself (both checked at limit 5 AND limit 20 in the
session-5 research run; for Indianapolis the city is the #1 hit outright at both limits - the
in-city institutions Q1117704 / Q15960623 / Q2311793, the Q600180 / Q8032 / Q172732 facilities
and the Q18153410 Oklahoma namesake never come first). The first-guess QID Q16556 was caught
as PHOENIX, Arizona (the first-guess mislabel trap) - the real city is Q6346.

Transcript for Columbus (the 241 session-8 run 2026-10-14, verbatim):

```
checked 2026-10-14 - 3 QIDs (Wikidata)
  Q16567  'Columbus'  (site id: columbus-q16567, new (this task))
      P625: [(-83.00055555555555, 39.96222222222222)]  (table site point: -83.00055555555555, 39.96222222222222)
      P373: ['Columbus, Ohio']
      P131: [('Franklin County', 'Q113237'), ('Delaware County', 'Q485524'), ('Fairfield County', 'Q490157')]  (table place: 'Franklin County, Ohio')
      enwiki: 'Columbus, Ohio'  (table wikipedia: 'https://en.wikipedia.org/wiki/Columbus,_Ohio')
      search 'Columbus': first hit with P625 is Q16567 'Columbus' (-83.00055555555555, 39.96222222222222)
  Q43199  'Omaha'  (site id: omaha-q43199, new (this task))
      P625: [(-95.9375, 41.25861111111111)]  (table site point: -95.9375, 41.25861111111111)
      P373: ['Omaha, Nebraska']
      P131: [('Douglas County', 'Q490695')]  (table place: 'Douglas County, Nebraska')
      enwiki: 'Omaha, Nebraska'  (table wikipedia: 'https://en.wikipedia.org/wiki/Omaha,_Nebraska')
      search 'Omaha': first hit with P625 is Q43199 'Omaha' (-95.9375, 41.25861111111111)
  Q6346  'Indianapolis'  (site id: indianapolis-q6346, new (this task))
      P625: [(-86.158055555556, 39.768611111111)]  (table site point: -86.158055555556, 39.768611111111)
      P373: ['Indianapolis']
      P131: [('Marion County', 'Q506230')]  (table place: 'Marion County, Indiana')
      enwiki: 'Indianapolis'  (table wikipedia: 'https://en.wikipedia.org/wiki/Indianapolis')
      search 'Indianapolis': first hit with P625 is Q6346 'Indianapolis' (-86.158055555556, 39.768611111111)
```

No FLAG / TRAP line on any of the three QIDs: each single P625 IS the table point (dist 0) and
the first name-search hit with coordinates is the city itself (for Columbus checked at limit 5
AND limit 20 in the session-7 research run: the #1 hit outright at both limits - the other eight
US Columbuses rank 2nd or later, and the in-city institution Q5935366 never comes first). The
first-guess QID Q1405 was caught as AUGUSTUS, the Roman emperor (the first-guess mislabel trap)
- the real city is Q16567.

Transcript for Memphis (the 241 session-10 run 2026-10-14, verbatim):

```
checked 2026-10-14 - 4 QIDs (Wikidata)
  Q16563  'Memphis'  (site id: memphis-q16563, new (this task))
      P625: [(-90.05194444444444, 35.14611111111111)]  (table site point: -90.05194444444444, 35.14611111111111)
      P373: ['Memphis, Tennessee']
      P131: [('Shelby County', 'Q501602')]  (table place: 'Shelby County, Tennessee')
      enwiki: 'Memphis, Tennessee'  (table wikipedia: 'https://en.wikipedia.org/wiki/Memphis,_Tennessee')
      search 'Memphis': first hit with P625 is Q16563 'Memphis' (-90.05194444444444, 35.14611111111111)
  Q16567  'Columbus'  (site id: columbus-q16567, new (this task))
      P625: [(-83.00055555555555, 39.96222222222222)]  (table site point: -83.00055555555555, 39.96222222222222)
      P373: ['Columbus, Ohio']
      P131: [('Franklin County', 'Q113237'), ('Delaware County', 'Q485524'), ('Fairfield County', 'Q490157')]  (table place: 'Franklin County, Ohio')
      enwiki: 'Columbus, Ohio'  (table wikipedia: 'https://en.wikipedia.org/wiki/Columbus,_Ohio')
      search 'Columbus': first hit with P625 is Q16567 'Columbus' (-83.00055555555555, 39.96222222222222)
  Q43199  'Omaha'  (site id: omaha-q43199, new (this task))
      P625: [(-95.9375, 41.25861111111111)]  (table site point: -95.9375, 41.25861111111111)
      P373: ['Omaha, Nebraska']
      P131: [('Douglas County', 'Q490695')]  (table place: 'Douglas County, Nebraska')
      enwiki: 'Omaha, Nebraska'  (table wikipedia: 'https://en.wikipedia.org/wiki/Omaha,_Nebraska')
      search 'Omaha': first hit with P625 is Q43199 'Omaha' (-95.9375, 41.25861111111111)
  Q6346  'Indianapolis'  (site id: indianapolis-q6346, new (this task))
      P625: [(-86.158055555556, 39.768611111111)]  (table site point: -86.158055555556, 39.768611111111)
      P373: ['Indianapolis']
      P131: [('Marion County', 'Q506230')]  (table place: 'Marion County, Indiana')
      enwiki: 'Indianapolis'  (table wikipedia: 'https://en.wikipedia.org/wiki/Indianapolis')
      search 'Indianapolis': first hit with P625 is Q6346 'Indianapolis' (-86.158055555556, 39.768611111111)
```

No FLAG / TRAP line on any of the four QIDs: each single P625 IS the table point (dist 0) and
the first name-search hit with coordinates is the city itself (for Memphis checked at limit 5
AND limit 20 in the session-9 research run: the #1 hit outright at both limits - and no
first-guess QID from memory was used this time, the search identified the city directly, so
the 177/179 first-guess mislabel trap class did not fire).

Transcript for Portland (the 241 session-12 run 2026-10-14, verbatim):

```
checked 2026-10-14 - 5 QIDs (Wikidata)
  Q16563  'Memphis'  (site id: memphis-q16563, new (this task))
      P625: [(-90.05194444444444, 35.14611111111111)]  (table site point: -90.05194444444444, 35.14611111111111)
      P373: ['Memphis, Tennessee']
      P131: [('Shelby County', 'Q501602')]  (table place: 'Shelby County, Tennessee')
      enwiki: 'Memphis, Tennessee'  (table wikipedia: 'https://en.wikipedia.org/wiki/Memphis,_Tennessee')
      search 'Memphis': first hit with P625 is Q16563 'Memphis' (-90.05194444444444, 35.14611111111111)
  Q16567  'Columbus'  (site id: columbus-q16567, new (this task))
      P625: [(-83.00055555555555, 39.96222222222222)]  (table site point: -83.00055555555555, 39.96222222222222)
      P373: ['Columbus, Ohio']
      P131: [('Franklin County', 'Q113237'), ('Delaware County', 'Q485524'), ('Fairfield County', 'Q490157')]  (table place: 'Franklin County, Ohio')
      enwiki: 'Columbus, Ohio'  (table wikipedia: 'https://en.wikipedia.org/wiki/Columbus,_Ohio')
      search 'Columbus': first hit with P625 is Q16567 'Columbus' (-83.00055555555555, 39.96222222222222)
  Q43199  'Omaha'  (site id: omaha-q43199, new (this task))
      P625: [(-95.9375, 41.25861111111111)]  (table site point: -95.9375, 41.25861111111111)
      P373: ['Omaha, Nebraska']
      P131: [('Douglas County', 'Q490695')]  (table place: 'Douglas County, Nebraska')
      enwiki: 'Omaha, Nebraska'  (table wikipedia: 'https://en.wikipedia.org/wiki/Omaha,_Nebraska')
      search 'Omaha': first hit with P625 is Q43199 'Omaha' (-95.9375, 41.25861111111111)
  Q6106  'Portland'  (site id: portland-q6106, new (this task))
      P625: [(-122.67916666666666, 45.515)]  (table site point: -122.67916666666666, 45.515)
      P373: ['Portland, Oregon']
      P131: [('Multnomah County', 'Q450374'), ('Clackamas County', 'Q484404'), ('Washington County', 'Q484538')]  (table place: 'Multnomah County, Oregon')
      enwiki: 'Portland, Oregon'  (table wikipedia: 'https://en.wikipedia.org/wiki/Portland,_Oregon')
      search 'Portland': first hit with P625 is Q6106 'Portland' (-122.67916666666666, 45.515)
  Q6346  'Indianapolis'  (site id: indianapolis-q6346, new (this task))
      P625: [(-86.158055555556, 39.768611111111)]  (table site point: -86.158055555556, 39.768611111111)
      P373: ['Indianapolis']
      P131: [('Marion County', 'Q506230')]  (table place: 'Marion County, Indiana')
      enwiki: 'Indianapolis'  (table wikipedia: 'https://en.wikipedia.org/wiki/Indianapolis')
      search 'Indianapolis': first hit with P625 is Q6346 'Indianapolis' (-86.158055555556, 39.768611111111)
```

No FLAG / TRAP line on any of the five QIDs: each single P625 IS the table point (dist 0)
and the first name-search hit with coordinates is the city itself (for Portland checked at
limit 5 AND limit 20 in the session-11 research run: the #1 hit outright at both limits -
and no first-guess QID from memory was used this time, the search identified the city
directly, so the 177/179 first-guess mislabel trap class did not fire; the hits that never
come first: the other US Portlands - Q49201 Portland (Maine, 2nd at both limits, 4081.9
km), Q753876 Portland (Connecticut, 3991.2 km), Q1807259 Portland (Indiana, 3089.3 km),
Q3308164 Portland (Michigan, 2998.2 km), Q80163 Portland (Arkansas, 2980.8 km), Q980152
Portland (Texas, 2969.3 km) (all measured with evidence.hav_m - the pool mixes the US
Portlands, so every sheet was disambiguated from its caption: the state in the
title/bibliographic desc), Q29168518 Portland (Dorset, England), Q1663450 Portland
(Victoria, Australia, 13324.1 km), Q774215 Isle of Portland, Portland State University
(Q1771717, an in-city institution 0.5 km from the city point - the Pittsburgh/Chicago
trap class, but it never comes first), University of Portland (Q513658, in-city, 7.4 km),
the Blazers/Pilots clubs and the name entities - none comes first).

## The evidence field (as in 236a/236b/240)

As in the 236b and 240 docs: every staged row carries a hand-recorded `caption_coords` tie in the
exact key order of `fit/evidence.py:caption_route` - the caption names the city and the stored
coordinates are the verified site point itself (dist 0); `record --live` would take the first
name-search hit instead, which is why every QID is verified above and the stage fails loud when a
caption does not print the city. A scan whose file page lost the drawing's date gets the known
drawing/publication date on the row and the page value kept as `date_commons` (the Zwolle
precedent; the keep() gate is judged after the swap).

## Omaha (site `omaha-q43199`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Bird's eye view of the city of Omaha, Nebraska 1868. LOC 73693495.tif` - 1868, E. Ruger
  (the sheet's own signature lower left reads "Drawn by E. Ruger" - the page's artist field
  reads "Ruger, A.; Chicago Lithographing Co.", an A. Ruger work like 240's Cleveland 1877
  sheet - two different Rugers; the label runs from the sheet's signature); lith. by the
  Chicago Lithographing Co. (named at the sheet's lower right), 8896x7024, Public domain (LC
  Panoramic maps (2nd ed.), 467). **Steep near-vertical whole-city view drawn from a high
  vantage across the Missouri River**: the lower-centre cartouche reads "BIRD'S EYE VIEW OF THE
  CITY OF / OMAHA / NEBRASKA / 1868"; the "MISSOURI RIVER" label runs diagonally along the
  sheet's lower right (the river a foreground strip with steamboat traffic, the rail yard with
  its rolling stock at the sheet's right), a thin hill-horizon band across the top - the
  built-up grid fills the sheet from a high vantage over the river, spanning the whole city
  beyond the 2000 m town box, so its fit is likely to end a review item (the 236a NY-1811 /
  DC-ring precedent); labelled landmark vignettes along the bottom border (Turner's Hall,
  Central Block, Oakwell Block, ...) and a numbered landmark legend; the LC Division-of-Maps
  stamp (FEB 28 1941) and the handwritten LCCN "73-693495" at the lower right. The page date
  (1868) matches the drawing (no Zwolle-style swap). The .tif is the ONLY scan of the sheet on
  Commons (an LCCN search) - no .jpg mirror to stage instead.

**DROP (with reasons):** the **1905 Austen "PANORAMIC VIEW OF OMAHA" sheet** -
`File:Panoramic view of Omaha. LOC 75694679.jpg`/`.tif` (10080x5808, Public domain, LC
Panoramic 468, "Supplement to the Omaha Daily Bee, January 1, 1906", page artist "Austen,
Edward J.; Bee Publishing Company, Jefferson, Ia.", sheet signature "Edw. J. Austen. 1905 /
Copyright AUSTEN PUBLISHING CO.") - a LOW oblique (the frozen Missouri fills the lower-right
quadrant, a wide flat plain horizon band ~30% across the top, the city a mid-sheet band) -
the same-genre dupe dropped per the 236b/240 steepest-sheet rule (both its scans, one sheet).
The **six eyeballed gate FALSE POSITIVES** (the pool's caption gate is a substring match, so
incidental mentions pass - the fit/ pitfall): two Weber stereoscopic PHOTO cards (DPLA
4b600ac2, Union Pacific "Rocky Mountain Scenery" No. 10 Devil's Gate series, A. J. Russell &
Co.: page 2 = the mountain-top photo, page 1 = the series index listing "443-Bird's-eye view of
Weber from above North's Canyon" - Weber, UT; the gate caught the series line "Across the
continent west from Omaha"), Green River WY 1875 (another-city view; the gate caught "846
miles west of Omaha"), the 1893 Rocky Mountains pictorial (a regional railroad-promo sheet;
the gate caught the copyright line "E. L. Logan, ... Union Pacific System, Omaha, Nebr."), and
the Great Plains book TEXT page (13661x5498, 24 text pages + covers - not a city view at all).
**The 31 gate-fail rows**: 22 too small (< 4000 px: the 1865 Jackson Bros x2 / Frank F. Currier
x6 scans, the 1897/98 Trans-Mississippi & International Exposition LCCN2004668240 x2, the
3072-px NYPL b11707633-G90F431 set x9, the 1890 Great Plains 1536x618, the Great Plains covers
2459x2847), 3 Union Pacific Pacific-Slope book sheets + 3 Salt Lake Basin book sheets (keep()
rejects - no page date; also gate-fail) and Sioux City (gate-fail, another city, 2161x665),
2 licence rejects ("No restrictions": the Sedgwick stereoview-lecture catalogue page - a book
page mentioning "between Omaha and San Francisco" - and the Street railway journal page),
1 NBY 5717 photo (keep() rejects - no page date; 823x516 too small).

**The QID's facts** (verified live 2026-10-14 at the 241 session-3 research run; the
transcript is in the QID section above): Q43199, label "Omaha" (matches the first-guess
candidate - no mislabel), enwiki "Omaha, Nebraska". P625 = ONE value (-95.9375,
41.25861111111111, ~30 m) - the downtown core (no refinement needed). P373 = the STRING
"Omaha, Nebraska" (a Wikidata quirk, not a country entity - the place is written from the
county + the state). P131 = Q490695 Douglas County (the only one, + the state) - hence place
"Douglas County, Nebraska". P17 = Q30 (a proper entity). Name search at limit 5 AND limit 20:
**no trap** (the first hit with P625, what `record --live` would store, is Q43199 itself,
dist 0; other hits: a Ulf Lundell album, the University of Nebraska Omaha (Q2495890, an
in-city institution - the Pittsburgh/Chicago trap class, but it never comes first), a 2025
film, Omaha Beach (France), namesake cities (TX/AR/IL/GA), a racehorse, a ship). No existing
site holds the QID (checked in the catalog, extras, 236a's, 236b's and 240's extras files and
web/data/sites.json); the site id `omaha-q43199` is the catalog slug rule
(catalog.slug("Omaha") = "omaha", verified).

**Verdict on 236b's silent skip of Omaha** (the task's first open question): Omaha is
**stageable** - it simply fell out of 236b's batch order (its 181 list ran Kansas City, then
past Omaha to St. Paul/Minneapolis), not for a pool failure; its pool has a strong candidate
(the 1868 sheet above). Omaha lands as batch-5 city 1 of 5.

## Indianapolis (site `indianapolis-q6346`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Bird's-eye view of Indianapolis showing Spink apartments, hotels, office and industrial buildings - DPLA - d442b7431e1f90b2c13fb4f957e8026f (page 1).jpg`
  - 1925 (the sheet prints NO year in either banner and the Commons page date is EMPTY - see
    the date evidence below; the row carries the known date and keeps the page's empty value as
    `date_commons`, the Zwolle-style swap), the E. G. Spink Company sheet (page 1 of the DPLA /
    Indiana State Library scan, DPLA id d442b7431e1f90b2c13fb4f957e8026f), 11153x7986, Public
    domain. The banners read "BIRD'S-EYE VIEW OF INDIANAPOLIS" (top) and "SHOWING SPINK
    APARTMENTS, HOTELS, OFFICE AND INDUSTRIAL BUILDINGS" (bottom). **Near-vertical whole-city
    view drawn from a high vantage to the SOUTH (the White River side)**: the White River band
    along the sheet's bottom edge, Union Station and the Hotel Spink vignettes lower-centre, the
    built-up grid running up to the "STATE FAIR GROUNDS" band at the top (north) with cemeteries,
    parks and rail lines around - no horizon band (steeper than the Omaha 1905 "panoramic" dupe
    class) - the grid fills the sheet beyond the 2000 m town box, so its fit is likely to end a
    review item (the 236a NY-1811 / DC-ring precedent). The lower-right corner carries the ISL
    shelf label "Map Rm-s / Ind. / 912.772 / IMaI25e / (1925)" (hand-typed library call number,
    not part of the drawing). A real-estate promo sheet (ISL subject includes
    "Adve[rtisements]") - recorded; it IS a whole-city view per its own title, and it is the
    ONLY whole-city view in the pool and the only scan of the sheet on Commons (no LOC-mirror
    found in four extra searches: "Spink Indianapolis", "Spink apartments", "Indianapolis 1913
    LOC", "LCCN Indianapolis bird").

**DROP (with reasons):** the pool is **43 unique rows, 2 gate-pass** - both pages of this one
DPLA sheet; the other 41 rows fail a gate (34) or pass the gate and fail a later one (7):

- `File:Bird's-eye view of Indianapolis showing Spink apartments, hotels, office and industrial buildings - DPLA - d442b7431e1f90b2c13fb4f957e8026f (page 2).jpg`
  - the SAME sheet's text page (11181x7920, Public domain, no page date): the Spink
    bond-department ANNOUNCEMENT, "THE SPINK IDEA", "Spink Directory of Indianapolis",
    "CHRONOLOGICAL HISTORY of Spink Apartments, Hotels, Office and Industrial Buildings"
    (1914-1924), "31 Corporations", "TAXES PAID on SPINK APARTMENTS, IN SIX YEARS" (1919
    $12,979.04 / 1920 $24,806.82 / 1921 $49,353.16 / 1922 $53,632.62 / 1923 $85,767.68 / 1924
    $103,863.70, total $330,403), "PERTINENT FACTS" (appraised at Dec. 31, 1923) - not a view;
    one row per sheet (page 1 staged above). This page is where the drawing's year 1925 is
    corroborated (see the date evidence below).
- The **19 Civil-War letter scans** (DPLA, all 1864, Public domain - letters, not views; the
  full-text search caught the city in the address lines): six William C. Olds letters to Frank
  A. Olds (24 July and 30 July 1864) - `File:William C. Olds letter to Frank A. Olds, 1864-07-24 - DPLA - dec6edb6489e2abd6c9c0dce5c073215 (page 1).jpg`/`(page 2).jpg` and
  `File:William C. Olds letter to Frank A. Olds, 1864-07-30 - DPLA - fbd2f108bca55b21c3fb37ad7e5f4f1d (page 1).jpg`/`(page 2).jpg`/`(page 3).jpg`/`(page 4).jpg` - and
  thirteen William R. Lowes letters to Rody and Lizzi Lowes (27 April and 27 May 1864; each
  letter uploaded under both a long and an ISO date title) - `File:William R. Lowes letter to Rody and Lizzi Lowes, 1864 April 27 - DPLA - 9754d649d9b381540e3b10fd1103b6e8 (page 1-4).jpg` and `... 1864-04-27 - DPLA - 9754d649d9b381540e3b10fd1103b6e8 (page 1-4).jpg`,
  `File:William R. Lowes letter to Rody and Lizzi Lowes, 1864 May 27 - DPLA - b6ba7e0bcb0a00c79df3106f084fadc4 (page 1-3).jpg` and `... 1864-05-27 - DPLA - b6ba7e0bcb0a00c79df3106f084fadc4 (page 1-3).jpg`.
- The **two Gary (Indiana) bird's-eye views** (DPLA, Grose Photo Co., licence "No restrictions" -
  another city and a licence reject): `File:Gary, Indiana bird's eye view - DPLA - 3954f28fbf8a0516b4754aaf0dbfab81.jpg`
  (7686x821) and `File:Gary, Indiana Residence District and Jefferson Park bird's eye view - DPLA - c4d7a8d7f9f02e76e5f6e748b6b5d0d2.jpg`
  (7714x835).
- `File:Bird's eye view of Personnel Training Institute - DPLA - 907de89419174f36e9243bdfe700dd45.jpg`
  - a campus close-up (Public domain, 5020x3605), not a whole-city view.
- The **two Belle Gunness 1908 "death farm" photographs** (Steve Shook, CC BY 2.0, 2327/2297 px
  < 4000, licence reject, and not the city): `File:Bird's-eye View of the Death Farm of Mrs. Gunness, 1908 - Belle Gunness (4231099971).jpg`
  and `File:Birds Eye View of Gunness' Farm, 1908 - Belle Gunness (4231104213).jpg`.
- `File:Indiana Steel Company Mills bird's eye view - DPLA - 084ea318ba65b062f55f310758de7d5f.jpg`
  - a works view (7720x826, licence "No restrictions"), not a city.
- `File:George F. Cram, Historical bird eye view of the Holy Land (FL45582226 3918156).jpg` - not a US city (Public domain, 5037x3216).
- `File:Phelps' hundred cities and large towns of America - with railroad distances throughout the United States, maps of thirteen cities, and other embellishments (1853) (14761215215).jpg`
  - licence "No restrictions" (2960x1500).
- `File:View of Second Avenue looking south, Seattle, 1912 (MOHAI 13225).jpg` - another city (1200x523, a street photo).
- The **three Alexandria (Indiana) 1893 bird's-eye views** (DPLA, Public domain, 7500 px, another
  Indiana city - gate-fail): `File:Alexandria, Indiana - DPLA - 578cedbba0746770a8eb5bb0381f4717 (page 2).jpg` and `File:Alexandria, 1893 - DPLA - 578cedbba0746770a8eb5bb0381f4717 (page 1).jpg`/`(page 2).jpg`.
- The **three "Birdseye, Ind." 1998 photographs** (DPLA, Indiana Landmarks, CC BY 4.0 - the
  "bird's eye" substring near-miss on the gate; a different, small town and a licence
  reject): `File:Birdseye Jail, 1st Street, c1998 (Birdseye, Ind.) - DPLA - b501b1df23bc114c7251ebebc4ca7915.jpg` (5379x3576), `File:Birdsye National Bank, 108 State Road 145, 1998 (Birdseye, Ind.) - DPLA - 820350f19506d93804da84054dcda979.jpg` (3588x5403),
  `File:Koehner and Zimmer Store, 101-103 State Road 145, 1998 (Birdseye, Ind.) - DPLA - 1eb027d9441d6b3d6a1622ef4fa0ea30.jpg` (5379x3576).
- The **gate-passed-but-failed rows (7)**: `File:White City Indianapolis 1906 postcard.jpg`
  (a postcard photo, 1091x667 < 4000); `File:(Map of Illinois). Compliments Of Parry M'F'G. Co. Indianapolis, Ind. Wm. B. Burford, Lith., Indianapolis ... (IA dr map-of-illinois-compliments-of-parry-mfg-co-indianapolis-ind-wm-b-00184028).jpg`
  (a state map, not a bird's-eye view; 878x1536 < 4000); the two "Blood for blood" (1906) book
  TEXT pages (gate-pass on the incidental city mention; 1326/1256 px < 4000 - `File:Image from page 19 of "Blood for blood; a legend of the "big elm tree,"" (1906).jpg`,
  CC0, and `File:Blood for blood; a legend of the "big elm tree," (1906) (14780944641).jpg`,
  "No restrictions"); the two Indiana Historical Society publications book pages (gate-pass on
  the incidental mention; "No restrictions" - `File:Indiana Historical Society publications (1897) (14782732712).jpg`,
  1388x2050, and `File:Indiana Historical Society publications (1919) (14587455569).jpg`,
  1748x2472); and `File:Indianapolis Zoo 029.jpg` (a 2009 photo, CC BY 2.0, 2816x2112 < 4000 -
  a keep() and a licence reject).

**The QID's facts** (verified live 2026-10-14 at the 241 session-5 research run; the transcript
is in the QID section above): Q6346, label "Indianapolis" (the first-guess Q16556 was caught as
PHOENIX, Arizona - the first-guess mislabel trap; the real city is Q6346), enwiki
"Indianapolis" (BARE - no state suffix, unlike Omaha's "Omaha, Nebraska"). P625 = ONE value
(-86.158055555556, 39.768611111111, ~31 m) - the downtown core (no refinement needed). P373 =
the STRING "Indianapolis" (a Wikidata quirk, not a country entity - and not even the
"city, state" form - the place is written from the county + the state). P131 = Q506230 Marion
County (the only one, + the state) - hence place "Marion County, Indiana". P17 = Q30 (a proper
entity). Name search at limit 5 AND limit 20: **no trap** (the first hit with P625, what
`record --live` would store, is Q6346 itself, dist 0 - the #1 hit outright at both limits;
other hits: the Indianapolis Museum of Art (Q1117704, an in-city institution - the
Pittsburgh/Chicago trap class), USS Indianapolis (Q600180, P625 = her sinking place in the
Pacific), Indy Art Center (Q15960623, in-city), the Indianapolis Motor Speedway (Q172732, in
Speedway IN), the Indianapolis 500 race (Q8032, Speedway), Indianapolis, Oklahoma (Q18153410,
another state), Sidney & Lois Eskenazi Hospital (Q2311793, in-city) - none comes first). No
existing site holds the QID (checked in the catalog, extras, 236a's, 236b's and 240's extras
files and web/data/sites.json); the site id `indianapolis-q6346` is the catalog slug rule
(catalog.slug("Indianapolis") = "indianapolis", verified).

**The 1925 date evidence**: the sheet prints NO year in either banner and the Commons page's
date field is EMPTY (the DPLA template's `date =` is blank; no LCCN anywhere on the page - the
DPLA API itself is unreachable from this machine, like loc.gov). The drawing's year = **1925**,
from (a) ISL's own record (fetched live from
indianamemory.contentdm.oclc.org/cdm/ref/collection/p15078coll8/id/5245: "Date of Original:
1925", item id ISL_IND_MapS_Indpls_1925, time period "1920s (1920-1929)"; the same call number,
912.772 IMaI25e (1925), is the sheet's own lower-right shelf label) and (b) the sheet's own
page-2 content (a tax table through 1924 and an appraisal at Dec. 31, 1923 -> printed 1925).
The staging is a Zwolle-style swap: the row carries the known date (1925) and keeps the page's
empty value as `date_commons` (the golden sample normalizes it to "0000-00-00"). **1925 is
exactly commons.MAX_YEAR - keep() passes at the boundary (y <= MAX_YEAR)**, the last year the
bird's-eye route accepts. The LOC catalogue date for the sheet could not be checked (loc.gov
unreachable) - if 236c's consolidation ever surfaces a conflicting LOC date, the sheet's own
content (1925) stands.

## Columbus (site `columbus-q16567`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:1872 Birds Eye View of Columbus Ohio - alternate.png`
  - 1872 (the banner reads "Bird's Eye View of / COLUMBUS, OHIO. / 1872." - the page date 1872
    matches the drawing - no Zwolle-style swap), the H. H. & O. H. Bailey sheet (page artist
    "Drawn by H.H. & O.H. Bailey. Printed by Strobridge & Co. Lith. Cincinnati. O. Published by
    Fowler & Bailey."), 11764x7542, Public domain. **A true oblique whole-city view drawn from a
    high vantage to the SOUTH (the Scioto River side)**: the Scioto River's bend a foreground
    band lower-left, the Statehouse square at centre, the street grid receding north toward a
    visible sky/horizon band along the sheet's top (open farmland beyond the built-up area) - a
    true oblique with a horizon band, unlike the Omaha/Indianapolis near-verticals - the
    built-up grid still fills the sheet beyond the 2000 m town box, so its fit is likely to end
    a review item (the 236a NY-1811 / DC-ring precedent). "Drawn by H.H. & O.H. Bailey" above the
    cartouche; the REFERENCES + CHURCHES landmark tables below. THE ONLY drawn whole-city view
    of Columbus (Ohio) in the pool and on Commons (three extra probes found nothing else).
    Staged as the sheet's **BEST of three scans** - the largest (11764x7542), cleanest (no
    smudge/fold damage), faithful-colour (blue sky, yellow streets, green lawns) of the three;
    the LOC 84690606 .jpg is the faded brown mono copy with vertical fold creases across the
    sheet and a dark smudge lower-left (the page itself says "LC copy imperfect. PM3"), the DPLA
    colour reproduction the smaller yellowed one ("the original can be found at the Ohio History
    Center") - so this .png is staged, not the LOC .jpg (the 1854 San Francisco precedent in
    236b's lead doc: the better non-LOC scan is staged when the LOC scan is the inferior copy).

**DROP (with reasons):** the pool is **87 unique rows, 11 gate-pass** (keep +
caption-names-Columbus + Public domain + >= 4000 px); all 11 good items eyeballed one by one
(1280-px thumbs + banner/centre/top-band zooms). The pool mixes US cities named Columbus (one
1868 Wisconsin; the rest Ohio), as the task Notes' caveat predicted - every sheet was
disambiguated from its caption (the state in the banner + the LCCN):

- The **two same-sheet dupes of the staged Bailey 1872 sheet** (one row per sheet):
  `File:Birds eye view of Columbus, Ohio LOC 84690606.jpg` (11360x7064, Public domain, Bailey / H. & O. H. Bailey, Strobridge & Co. lith.)
  - the LOC copy: banner "Bird's Eye View of / COLUMBUS, OHIO. / 1872." with "Drawn by H.H. & O.H. Bailey" above the cartouche, REFERENCES + CHURCHES tables below - but a **faded brown mono scan with vertical fold creases across the sheet and a dark smudge lower-left** (the page itself says "LC copy imperfect. PM3") -> the inferior scan; and
  `File:Birds eye view of Columbus, Ohio LOC 84690606.tif` (11360x7064, Public domain) - the .tif twin of the same LOC image.
- `File:1872 Bird's Eye View of Columbus Map - DPLA - e49f94947c28afd4055194f533f7e03c.jpg`
  (5400x3598, Public domain, "color reproduction; the original can be found at the Ohio History
  Center") - the same sheet, smaller and yellowed -> the third same-sheet dupe.
- `File:Bird's eye view of Columbus, Columbia Co., Wisconsin 1868. LOC 73694538.jpg` (7192x5008, Public domain, Ruger/Chicago Lith.) - **another city**: Columbus (Wisconsin, ~625 km away) - a plain grid with a small river, no cartouche at thumb size; the title itself says Columbia Co., Wisconsin.
- `File:Bird's eye view of Camp Chase near Columbus, Ohio. LOC 73694505.jpg` (1860, 7800x5936, Public domain, Ruger) - a Civil-War prison camp (a fort), not the city.
- `File:Bird's-Eye View, Columbus, Ohio - DPLA - c640409ff3ed15e40d6bd187c2d8374e (page 3).jpg`
  (4464x15715, Public domain, 1908) - a **photograph** booklet of individual buildings (the
  Grand Hotel, the Arcade, ...), various views, not one whole-city view (the booklet's other 27
  pages are in the gate-fail list below).
- `File:Bird's eye view, Columbus, Ohio flood - DPLA - ef7a6e84b5094f22011f3ca167a61108 (page 2).jpg`
  (4096x2640, Public domain, no page date) - the postcard's **back** (the address side) of a
  1913-flood postcard.
- `File:Bird's eye view of Columbus, Ohio - DPLA - 1b250803005920d1466df1003dc66421 (page 2).jpg`
  (4206x2732, Public domain, postmarked 7 May 1908) - the postcard's **back** (handwritten
  "Mere G. H. Boweitz / New London / Ohio", postmarked Columbus, Ohio 7 May 1908).
- `File:Birdseye view looking east, Columbus, Ohio - DPLA - 3b5c1cbd3d5b67a744c01a32f2979db1 (page 2).jpg`
  (4127x2651, Public domain, 3 September 1908) - the postcard's **back** (postmarked "2-AM
  1908", annotation "Hay WAGONS ON BROAD ST").
- `File:Birdseye view looking east, Columbus, Ohio - DPLA - 3b5c1cbd3d5b67a744c01a32f2979db1 (page 1).jpg`
  (4110x2663, Public domain) - a **photograph** (elevated street view down East Broad Street,
  the Statehouse right, the city in the background) - a partial view, not a drawn whole city.

**The 76 gate-fail rows** (grouped): the 27 pages of the DPLA postcard booklet
`c640409ff3ed15e40d6bd187c2d8374e` (1492-3268 px - individual-building photos, too small);
five 2015 night-aerial photographs (Miami University digital library, "No restrictions"
licence, no-keep: `File:Bird's Eye View of Columbus (16281770635).jpg` 3299x2027,
`File:Bird's Eye View of Columbus (16280937692).jpg` 3251x1991, `File:Birdseye View Looking South (16094330380).jpg` 3227x2027,
`File:Birdseye View Looking East (16279777021).jpg` 3239x2015, `File:Birds Eye View West, Columbus, O. (15659340884).jpg` 3263x2015);
the 1908 `File:Bird's-eye View of Downtown Columbus, Ohio.jpg` (3207x2140, "No restrictions",
a photo, too small); the 1909 Scioto-River-trestle postcard pages 1-2
(`File:Birds Eye View of Downtown Columbus - DPLA - aff54a650bf8b4a07d8714cddf5a4f2b (page 1).jpg`/`(page 2).jpg`, 3273x2118, Public domain, photo, too small);
the 1908 downtown postcard page 2 (`File:Bird's-eye View of Downtown Columbus - DPLA - 5753fff0a4a207ec6d1587b26e2d19c7 (page 2).jpg`,
3194x2118, Public domain, photo, too small, the year field a nonsense 1587); four 1872-Bailey
detail crops (`File:1872 Birds Eye View of Columbus Ohio by Bailey LC-school.jpg` 508x356, `File:1872 Birds Eye View of Columbus Ohio by Bailey LC-Fulton School.jpg` 459x344, `File:1872 Birds Eye View of Columbus Ohio by Bailey LC-Fulton School alt.png` 438x337,
`File:1872 Birds Eye View of Columbus Ohio by Bailey LC (cropped).jpg` 1990x1147 - same-sheet crops, too small);
the 36 no-gate hits of other Ohio towns (18 towns x 2 pages: Lisbon, Ironton, Dunkirk, Glouster,
New Lexington, the Swanton high school, West Point (Columbiana County), the University of
Dayton, the Hotel Lafayette (Marietta), Carey, Somerset, Port Washington, Marion, Lancaster,
the Dayton National Military Home, Fremont, Nelsonville, Oak Harbor - the search matched
"Columbus"/"Columbiana" in title or description).

**EXTRA probes** (beyond the six-form route, to be sure no drawn sheet was missed): "bird's eye
view of 'Columbus, Ohio' filetype:bitmap" (40 hits - all pool members, nothing new),
"'Columbus, Ohio' LOC filetype:bitmap" (40 - the LOC numbered photo-series TIFs "Columbus,
Ohio LOC 01-29.tif" = street photographs, plus Carnegie Library / Ohio Educational Congress /
YMCA Hut / itinerant-photographer photos, and the same LOC 84690606 pair), "columbus ohio
panoramic filetype:bitmap" (40 - the 1913-flood photos, the downtown postcards, the State
Capitol-and-Square views, Ohio State University / Ohio Stadium photos, the Sheraton-Hotel
views, the Blanchard photographer collection, the 1918 conference, and again the same 1872 LOC
pair). **Verdict: the 1872 Bailey sheet is the ONLY drawn whole-city view of Columbus (Ohio)
on Commons.**

**The QID's facts** (verified live 2026-10-14 at the 241 session-7 research run; the
transcript is in the QID section above): Q16567, label "Columbus" (the first-guess Q1405 was
caught as AUGUSTUS, the Roman emperor - the first-guess mislabel trap; the real city is
Q16567), enwiki "Columbus, Ohio". P625 = ONE value (-83.00055555555555, 39.96222222222222,
~31 m) - the downtown core (no refinement needed). P373 = the STRING "Columbus, Ohio" (a
Wikidata quirk, not a country entity - the place is written from the county + the state).
P131 = Franklin Q113237 + Delaware Q485524 + Fairfield Q490157 (the county seat is Franklin) -
hence place "Franklin County, Ohio". P17 = Q30 (a proper entity). Name search at limit 5 AND
limit 20: **no trap** (the first hit with P625, what `record --live` would store, is Q16567
itself, dist 0 - the #1 hit outright at both limits; the hits that never come first: the other
eight US Columbuses (Georgia Q239870, Mississippi Q985648, Indiana Q941870 - 262.9 km away,
Texas Q975782, North Carolina Q2026104, Nebraska Q932391, Kansas Q2232985, Wisconsin
Q1570063, Montana Q961735 - all rank 2nd or later), the Columbus Museum of Art (Q5935366, an
in-city institution 1116 m from the city point - the Pittsburgh/Chicago trap class, measured),
the Columbus Crew (Q457163) and Blue Jackets (Q207507) (in-city clubs, no P625), Christopher
Columbus (Q7322, no P625), the Columbus ISS module (Q155935, no P625), the name entities,
and a Galapagos Islands hit at limit 20). No existing site holds the QID (checked in the
catalog, extras, 236a's, 236b's and 240's extras files and web/data/sites.json - the only
Columbus entries in the catalog are the Columbus Country Club Mound Q104842892 and a Shrum
Mound mention in a site summary); the site id `columbus-q16567` is the catalog slug rule
(catalog.slug("Columbus") = "columbus", verified).

## Memphis (site `memphis-q16563`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Bird's eye view of the city of Memphis, Tennessee 1870. LOC 73694530.jpg`
  - 1870 (the banner reads "MEMPHIS TENNESSEE. 1870." - the page date 1870 matches the drawing -
    no Zwolle-style swap; the row's extra dict is empty, the Omaha pattern), the A. Ruger sheet
    (page artist "Ruger, A."; the sheet's own signature "A. Ruger, 75 B'wd St." lower-left),
    10400x6832, Public domain (LC Panoramic maps (2nd ed.), 901). **A true oblique whole-city
    view drawn from a high vantage across the Mississippi River (from the Missouri side)**:
    the river and its steamboat landings a foreground band lower-left, the city up the bluffs
    across the centre (the downtown grid, the squares, the rail yards), the open plain to the
    horizon upper-left, a visible sky band with clouds along the sheet's top - unlike the
    Omaha/Indianapolis near-verticals (like the Columbus 1872 true oblique) - the built-up grid
    still fills the sheet beyond the 2000 m town box, so its fit is likely to end a review item
    (the 236a NY-1811 / DC-ring precedent). The banner "MEMPHIS TENNESSEE. 1870." with two
    landmark-legend columns; a small hand-written call number in the lower-right legend panel.
    The steepest (true oblique) whole-city view in the pool and the best-scanned drawn sheet of
    Memphis (Tennessee) on Commons (three extra probes found nothing else).

**DROP (with reasons):** the pool is **42 unique rows, 10 gate-pass** (keep +
caption-names-Memphis + Public domain + >= 4000 px); all 10 good items eyeballed one by one
(1280-px thumbs; 1920-px corner/centre crops for the same-scan detection). The pool mixes the
US cities named Memphis (TN dominates; the MO ghost town and the TX/AL small towns have no
drawn views in the pool) - every sheet was disambiguated from its caption (the state in the
banner/LCCN):

- `File:Memphis - Bird's Eye View - Memphis Appeal 15 October 1887.jpg` (10104x7320, Public domain, page date 1887-10-15) - the 1887 "Memphis Appeal" newspaper SUPPLEMENT page (a two-page spread with a centre fold, a printed title band across the bottom, woodcut quality): a drawn whole-city view from across the river (the steamboat landings a foreground band, the city up the bluffs, the plain beyond) but a newspaper page, not a lithograph sheet -> DROPPED (the 1870 Ruger is steeper and better scanned).
- `File:OCLC 5486148 Tennessee State Library Bird's-eye view of the City of Memphis, Tennessee in the 1870s.jpg` (9344x7135, Public domain, page date "1870s") - the 1870 A. Ruger sheet, but a SEPARATE 1873 REISSUE impression (bottom-right note "MEMPHIS, TENNESSEE in 1870 Republished in 1873 by HISTORIC URBAN PLANS, Thiru, New York, from a lithograph in the Library of Congress. This is number 17 1/2 of an edition limited to 350 copies", a hand-written "23 1/4" in the left margin) -> same-sheet dupe (another impression), inferior to the LOC scan.
- `File:Forrest's jail in Memphis from Bird's-eye view of the City of Memphis, Tennessee in the 1870s.jpg` (5445x5269, Public domain) - a DETAIL CROP from the TSL 1870s (Ruger) impression with a red-rectangle annotation marking the jail -> DROPPED (not a whole-city view).
- `File:Bird's eye view of the city of Memphis, Tennessee 1870. LOC 73694530.tif` (10400x6832, Public domain) - the .tif twin of the staged .jpg's exact same scan -> same-sheet dupe.
- `File:Memphis airview 1870.jpg` (10400x6832, Public domain, artist "Albert Ruger") - a RE-UPLOAD of the LOC 73694530 scan under a different name - verified the same physical scan (the 1920-px bottom-right corner crop and the centre crop match pixel-for-pixel, including the hand-written call number) -> same-sheet dupe.
- `File:Perspective map of the city of Memphis, Tenn. 1887. LOC 75696582.jpg` (12960x8880, Public domain, page date 1887, artist "Henry Wellge & Co.") - the 1887 Wellge sheet: monochrome (brown) lithograph, a vertical FOLD LINE down the sheet's centre, inset landmark-building strips across the top and bottom (Crescent City Lumber Co., Zelner & Co., W. B. Bloode & Co., the Gayoso Hotel, the Chickasaw Iron Works, the Pratt Gin Co., N. Wetter Manufacturing, Joe Palace Co., the Cole Manufacturing, Christian Brothers' College, the Chickasaw Land Company), the view from across the river - the LARGEST scan in the pool, but a shallower wide panorama with the fold and no colour -> DROPPED (the 1870 Ruger is steeper and the better scan).
- `File:Bird's eye view of junction of the Ohio & Mississippi Rivers, showing Cairo and part of the southern states.tif` (6608x5160, 1861, Bachmann/Rumpf) + `File:Bird's eye view of junction of the Ohio & Mississippi Rivers, showing Cairo and part of the southern states LOC 99447003.jpg` + `File:Bird's eye view of junction of the Ohio & Mississippi Rivers, showing Cairo and part of the southern states LOC 99447003.tif` - ONE sheet in three scans: a REGIONAL view looking south from Vienna, Illinois; the TITLE names CAIRO, not Memphis (the gate passed on the description's distance table "Memphis 265" and the distant "MEMPHIS, TENN" label) -> DROPPED (not a Memphis sheet; the caption does not name the city).

**The 32 gate-fail rows** (grouped): **26 keep-fails** = the NBY aerial PHOTOs (`File:Aerial View of Memphis Business District (NBY 2544).jpg` 811x505 PD 1940, `File:Skyscraper District, Court Square and Main Street (NBY 7545).jpg` 819x521 PD no date - Public domain but < 4000 px anyway), the zoo/park BEV photos (`File:Memphis Zoo BEV.jpg` 672x480, `File:Overton Park Memphis BEV.jpg` 864x816 - CC BY-SA 3.0, 2012 - licence reject and too small), the Jim Harvey double-neck guitar photos x2 (1958, for Paul Buskirk, Nashville Country Music Hall of Fame museum, CC0, 3024x4032 - the search matched the "bird's-eye maple" in the title), and 20 BIRD photographs (Japanese white-eye x4, White-eyed vireo x3, Dark-eyed junco x13 - all CC BY 2.0 - the search matched the birds' "Memphis"/white-eye names, e.g. "Dark-eyed junco in Overton Park, Memphis, TN"); **6 gate-fails** (the caption gate is a substring match over title + description; these never print "Memphis") = `File:Untitled - General Views (NBY 1648).jpg` (800x496, PD photo, circa 1913), the "The birds of America - from drawings made in the United States and their territories (1840)" plate (2020x3210, No restrictions - the search matched "bird's-eye"), the "War Map of the Middle States - Balloon View of Virginia, Maryland, Kentucky, Tennessee and parts of Arkansas, Missouri" (14538x21054, PD, 1861-era balloon view of the Middle States - a REGIONAL view; "Memphis" appears only in the printed distance labels, so even the gate rejected it), the two "The hunter and the trapper in North America" book plates (2004x1420 / 2000x1420, No restrictions), `File:Breeder and sportsman (1898) (20221728940).jpg` (788x306, No restrictions).

**EXTRA probes** (beyond the six-form route, to be sure no drawn sheet was missed):
"bird's eye view of 'Memphis, Tennessee' filetype:bitmap" (11 hits - all pool members, 0
new), "'Memphis, Tennessee' LOC filetype:bitmap" (40 hits, 36 new), "memphis tennessee
panoramic filetype:bitmap" (19 hits, 13 new; two overlap the previous probe). The 11 distinct
new candidates that could be drawn views were ALL eyeballed (1280-px thumbs): the three 1910
LOC "Panoram"/"Street scene" series (photographs: LCCN2007662799 1536 px river landing,
LCCN2007662814 5065 px elevated city view, LCCN2007662813 5277 px downtown square) - photos;
"Memphis (Tennessee) before the war - sketched by Porte Crayon. LCCN95509535" .jpg/.tif
(4096x3254, 1862 wood engraving; the Harper's Weekly 19 March 1862 page with THREE scene
vignettes - Old Battery at the Navy-Yard, Steamboat Landing, The Cotton Levee) - scenes, not a
whole city; "Scenes in Memphis, Tennessee, during the riot LCCN94507780" .tif/.jpg (3286x4096,
1866; the Harper's Weekly 26 May 1866 page, two wood engravings of the 1866 riot) - scenes, too
small; "The levee at Memphis ... sketched by Mr. Alex Simplot. LCCN95504268.jpg" (1862 scene
sketch, 3384 px); "Map of the city of Memphis - including Fort Pickering and Hopefield, Ark.
LOC 2012586237.jpg" (23471x15189, 1858) - a FLAT cadastral map (hachured relief, lot numbers),
not a bird's-eye; "Memphis-naval-battle.jpg" (1157 px, the 1862 naval-battle engraving after
Simplot); "Riverboats at Memphis.jpg" (9051x7201, c1906 LOC 019395 river-landing PHOTOGRAPH);
plus a batch of modern photos (the Pyramid, Graceland, the Liberty Bowl panorama) and 1940s
photos (Cotton Carnival) from the same probes. **Verdict: the 1870 A. Ruger sheet is the
steepest, best-scanned drawn whole-city view of Memphis (Tennessee) in the pool and in the
probes** (the only other drawn whole-city views are the 1887 Wellge and the 1887 "Appeal"
newspaper page, both dropped above).

**The QID's facts** (verified live 2026-10-14 at the 241 session-9 research run; the
transcript is in the QID section above): Q16563, label "Memphis" (description "city in and
county seat of Shelby County, Tennessee, United States" - no first-guess QID from memory was
used this time, the search identified the city directly, so the 177/179 mislabel trap class
did not fire), enwiki "Memphis, Tennessee". P625 = ONE value (-90.05194444444444,
35.14611111111111, ~31 m) - the downtown core (no refinement needed). P373 = the STRING
"Memphis, Tennessee" (a Wikidata quirk, not a country entity - the place is written from the
county + the state). P131 = Q501602 Shelby County ONLY (no multi-county like Columbus) -
hence place "Shelby County, Tennessee". P17 = Q30 (a proper entity). Name search at limit 5
AND limit 20: **no trap** (the first hit with P625, what `record --live` would store, is
Q16563 itself, dist 0 - the #1 hit outright at both limits; the hits that never come first:
the other US Memphises - Q962034 Memphis (Missouri, a ghost town, 235.5 km from TN), Q979971
Memphis (Texas, 1166.4 km), Q67363 Memphis (Alabama, 195.1 km) (all measured with
evidence.hav_m - the pool mixes the cities, so every sheet was disambiguated from its
caption: the state in the banner/LCCN), Q5715 Memphis (Egypt), Q19343442 (a street in
Amersfoort, Netherlands), the University of Memphis (Q2094177, an in-city institution 12.8 km
from the city point - the Pittsburgh/Chicago trap class, but it never comes first), Memphis
International Airport (Q866831, in-city) - none comes first). No existing site holds the QID
(checked in the catalog, extras, 236a's, 236b's and 240's extras files and web/data/sites.json
- zero case-insensitive "memphis" in all of them); the site id `memphis-q16563` is the
catalog slug rule (catalog.slug("Memphis") = "memphis", verified).

## Albuquerque (DROPPED - no drawn view in the Commons mirror)

The first city-5 candidate (the 183 first-probe list's first: Albuquerque, Portland (OR),
Salt Lake City, San Antonio, Seattle, Richmond, Buffalo, Miami - the 236b/240 "Not done
yet" pointers name no further order, so box 5's fallback governs: any US city with a
usable LOC Panoramic view not staged anywhere). Researched in the 241 session-11 run and
DROPPED:

**The QID** (live Wikidata, the session-11 run): Q34804 = Albuquerque (New Mexico): label
"Albuquerque", description "city and county seat of Bernalillo County, New Mexico,
United States and the largest city in the state". P625 = ONE 31 m value (-106.65027777777777,
35.08444444444444) - the downtown core; no refinement. P373 = the STRING "Albuquerque" (the
usual US string quirk, not even the "city, state" form) -> place would be "Bernalillo
County, New Mexico" (P131 = Q156297 Bernalillo County ONLY). P17 = Q30. enwiki
"Albuquerque, New Mexico". Name search at limit 5 AND limit 20 (R5): **no trap** - the
first hit with P625 at BOTH limits is Q34804 itself (the #1 hit outright at both; no
first-guess QID from memory was used). Hits that never come first (all distances measured
with evidence.hav_m): Q16146839 (family name), Q4712800 (a 1999 "Weird Al" song),
Q3208258 (a 1948 film), Q716981 (Filipe Albuquerque, a racing driver), Q18112876 (an
insect genus), Q16487426 Albuquerque (a Corumbá district, Brazil, 7979.8 km), Q61879324
(a Brazilian politician), Q4712813 Albuquerque Journal (an in-city newspaper),
Q21583958 (a Neil Young song), Q24260754 Albuquerque (a Wilson County TX ghost town,
1044.8 km), Q115557844 (undescriptioned), Q79947122/Q64156862/Q79942596 (photographs),
Q125979435 (a painting), Q96699785 (an academic journal), Q1578972 Albuquerque
International Sunport (an in-city institution, 6.17 km - the Pittsburgh/Chicago trap
class, but it never comes first), Q4712839 (the metropolitan area), Q74368447 (a
researcher). No existing site holds the QID (zero case-insensitive "albuquerque"/"q34804"
hits in the catalog, extras, 236a's, 236b's, 240's and this task's extras files and
web/data/sites.json); catalog.slug("Albuquerque") = "albuquerque" (a would-be site id
albuquerque-q34804 - never staged).

**The pool** (the session-11 run): the six documented plain-phrase forms (236b's route,
srnamespace 6, srlimit 40) returned 0/0/0/0/0/0 - not a rate-limit, a real empty (probed
live, repeated). Root cause (now a PITFALLS entry): Commons search matches FILE TITLES
case-insensitively but OCR FULL TEXT case-sensitively, so the capitalized forms only
matched titles (none exist), and the lowercase variants only found OCR-text false
positives (ornithology books). Extended probes (all logged in /tmp/aw241_city5_probe*.log):
"albuquerque LOC filetype:bitmap" -> HABS single-building surveys, US Veterans
Administration aerial PHOTOs of hospital/airfield buildings, a 1931 foundry photo,
Route-66 photos - no drawn whole-city view; "panoramic albuquerque" -> found
File:Panoram of Albuquerque, N. Mex LCCN2007662623.tif (1915, 4563x697, Public domain, NO
description): a 6:1 PHOTOGRAPHIC PANORAMA strip (eyeballed: a high-vantage wide strip over
the low downtown grid, the sand dunes, the Sandias behind, a big domed building at the
right) - DROPPED (a photograph, not a drawn bird's-eye view; the "Panoram of <city>" is a
LOC Panoramic collection title variant - the mirror's only Albuquerque item); "new mexico
bird eye view" -> the mirror DOES hold drawn LOC Panoramic sheets for OTHER New Mexico
cities: File:Bird's eye view of the city of Santa Fé, N.M. 1882. LOC 75694742.jpg and
File:Bird's eye view of Las Vegas, N.M. c.s. San Miguel County 1882. LOC 75694741.jpg
(both future-candidate pool hits, recorded in the Not-done-yet section for when the queue
reaches them); broad "albuquerque bird" and "albuquerque view LOC" dumps (40 titles
each) -> only birdwatch photos, books, HABS and postcards.

**Verdict**: Albuquerque DROPPED - no drawn bird's-eye view of Albuquerque in the Commons
mirror (a documented-search drop per box 5's disjunct). City 5 = the next probe-list
candidate: **Portland (Oregon) - LANDED below**.

## Portland (site `portland-q6106`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Portland, Oregon 1890 Perspective Birds-eye-view Map.jpg`
  - 1890 (the lower-centre cartouche reads "JAMES MCI. WOOD, REAL ESTATE AND INVESTMENT
    BROKER. / PORTLAND, OREGON. / 1890." - the page date 1890 matches the banner - no
    Zwolle-style swap), the 1890 J. McI. Wood perspective sheet in its LOC mirror
    (13760x9520, Public domain; page artist "Library of Congress, Geography and Map
    Division" - a LOC Panoramic maps item; the title prints "Portland, Oregon"): THE
    steepest AND best-scanned drawn whole-city view in the pool (13760 px, the widest scan
    in the pool) and the only gate-pass one (the 1880 J.K. Gill sheet's only scan is 1742
    px and the two NYPL 1880s scans 3072 px - all under the 4000-px width gate): a
    hand-drawn, hand-colored sheet from a high vantage to the NORTHWEST (the Eastside
    bluffs) looking southeast - the Willamette River runs diagonally upper-left to
    lower-right with the downtown grid on both banks, a long steel-truss railway bridge
    mid-sheet, river traffic, Mt. St. Helens and the Cascade range a background mountain
    band at right, a sky band along the top, prominent-building vignettes framing the sheet
    (a real-estate promo sheet, the Omaha/Indianapolis class, with a mountain horizon
    instead of open farmland) - the built-up grid fills the sheet beyond the 2000 m town
    box, so its fit is likely to end a review item (the 236a NY-1811 / DC-ring precedent).
- `File:Portland, Oregon 1890. LOC 75694939.tif` (13760x9520, Public domain, date 1890,
  artist "Clohessy & Strengele; Elliott Pu Co.", desc "Perspective map not drawn to scale.
  Bird's-eye-view. LC Panoramic maps (2nd ed.), 724 ...") - a SECOND scan of the STAGED
  1890 sheet (NOT in the 12-query pool - its title has no bird's-eye phrase; found by the
  landing's title re-search, the Omaha LCCN-search step): verified a SEPARATE scan, not a
  re-upload (the 1920-px thumbnails differ with mean absolute diff 11 - a re-upload would
  match pixel-for-pixel, the Memphis verification pattern); side-by-side crops
  (cartouche / downtown grid / top vignette band): the staged .jpg is the SHARPER scan -
  crisper vignette linework and cartouche type, cleaner downtown grid; the .tif is
  warmer-toned and slightly hazier in the centre with more smudging in the lower legend
  panels -> the .jpg stays staged (the 1872-Columbus best-of-scans rule), the .tif
  DROPPED (same-sheet dupe).

**DROP (with reasons):** the pool is **55 unique rows, 12 gate-pass** (keep +
caption-names-Portland + Public domain + >= 4000 px; the six documented forms were run in
BOTH capitalizations of the city name per the case-quirk lesson - 12 queries total:
"bird's-eye view of Portland" 40 / "bird's eye view of Portland" 40 / "birdseye view of
Portland" 10 / "Portland bird's eye" 40 / "Portland birdseye" 10 / "Birds' eye view of
Portland" 40 / lowercase twins 40/40/10/40/10/40). The pool mixes the US cities named
Portland (OR and ME dominate; the rest small towns and other states) - every sheet was
disambiguated from its caption (the state in the title/bibliographic desc). All 12 good
items + the 3 width-failing keep-pass eyeballed one by one (1280-px thumbs):

- `File:Bird's eye view of the city of Portland, Maine 1876. LOC 75693248.jpg`/`.tif` (10448x6912, Public domain, Warner/J. J. Stoner/Charles Shober/Chicago Lith.) - a drawn sheet of Portland, MAINE (monochrome litho, "BIRD'S EYE VIEW OF THE CITY OF PORTLAND 1876", the Fore River/Back Cove with the numbered landmark legend) -> DROPPED (another city: Q49201; the .jpg/.tif are same-sheet twins).
- `File:1876 Birds eye view of the city of Portland Maine, by Jos. Warner, from the Digital Commonwealth - commonwealth wd376120q` (10088x7336, Public domain) - the SAME ME 1876 sheet (Warner/J. J. Stoner), a third scan -> DROPPED (same sheet + another city).
- `File:Bird's-eye view of Portland, Oregon with Mt. St. Helens in background LCCN91719502.jpg`/`.tif` (4096x3272, Public domain, 1903) - a PHOTOGRAPHIC print (eyeballed: a hillside view over residential rooftops toward the downtown, Mt. St. Helens towering) -> DROPPED (a photograph, not a drawn view; the .jpg/.tif are same-sheet twins).
- `File:Bird's eye view of Portland LCCN2007662704.tif` (4278x708, Public domain, 1908, NO description) - a 6:1 PHOTOGRAPHIC PANORAMA strip (eyeballed: a hillside wide-strip view over a dome-topped building with mountain ranges behind; the state ambiguous but a photo either way) -> DROPPED (a photograph; the "Panoram" family, like Albuquerque's 1915 item).
- `File:Bird's eye view of Port Townsend, Puget Sound, Washington Territory. From the north-east. 1878 - drawn and published by E.S. Glover, Portland, Oregon ; A.L. Bancroft & Co., lith., San LCCN2003679983.jpg` (8755x5818) and its twin scan (5104x4121) (both Public domain) - a drawn whole-city view of PORT TOWNSEND (the "Portland, Oregon" PUBLISHER credit is what pulled it into this pool) -> DROPPED (another city); recorded as a strong pool hit for when a future batch reaches Port Townsend (the 185 grep found it staged nowhere).
- `File:Birds eye view of Casco Bay, Portland, Maine, and surroundings. LOC 80693592.jpg`/`.tif` (8371x6028, Public domain, 1906) - a REGIONAL view (Portland ME small at left, the bay and its islands, the red rail line, "BIRDS EYE VIEW OF CASCO BAY: PORTLAND, MAINE AND SURROUNDINGS") -> DROPPED (another city + regional, not whole-city).
- `File:Bird's-eye View of the City of Seattle, Puget Sound, Washington Territory, 1878 (MAPS 64).jpg` (7613x4804, Public domain) - a drawn whole-city view of SEATTLE ("Drawn by W. B. Glover, Portland, Oregon; published by A. T. Mott & Co., New York, 1878" - again the "Portland, Oregon" credit pulled it in; the city on the bluffs, the crowded harbor, Mt. Rainier faint at the right horizon, a sky band) -> DROPPED (another city); recorded as a strong pool hit for when the queue reaches Seattle (5th on the 183 probe list).
- The **3 width-failing keep-pass** (gate-pass but < 4000 px - the only other drawn
  Portland OR sheets in the pool): `File:Birds-Eye View of Portland, Oregon.jpg` (J.K. Gill
  Company c1880, 1742x1273, Public domain) - a drawn whole-city view of Portland OR (the
  famous hand-colored 1880 Gill sheet) but the only scan is 1742 px wide -> DROPPED (width
  < 4000); the two NYPL 1880s scans `File:Bird's-eye view of Portland (NYPL b11707231-G89F234 076ZB).tiff`/`076ZF` (3072x1899 / 3072x1940, Public domain, no date, "Scan by
  NYPL") - black-and-white scans of drawn 1880s Portland OR sheets -> DROPPED (width 3072
  < 4000).

**The 40 remaining pool rows** (grouped): **9 keep-fails** =
`File:Bird's Eye View of the Southern End of The Fleet - geograph.org.uk - 2311554.jpg`
(640x384, CC BY-SA 2.0, 2011 - a photo of The Fleet, Isle of Portland (Dorset), modern);
the two NARA 1973 gas-station aerials `File:BIRD'S EYE VIEW OF AN AVERAGE GAS STATION IN PORTLAND ... NARA - 555457.jpg`/`.tif` (2000x1361, Public domain, David Falconer - modern photos, no keep); `File:Birds eye view of Casco Bay, Portland, Maine, and surroundings (2675184791).jpg` (2000x1257, CC BY 2.0, 2008 - a BPL maps.bpl.org re-scan of the 1906 Walker & Co. map - no page date, licence reject); `File:Essayons dredge construction - USACE-p15141coll5-6199.jpeg` (4797x6660, Public domain, c1980 - a shipyard photo, no keep); the four `File:Flounce Rock (...).jpg` (1920x1080 x3 / 1252x1042, Public domain, 2012, BLM - "for a birdseye view of the Upper Rogue area ... from Portland, America" - modern photos, no keep). **11 gate-fails with keep** (the caption gate is a substring match over title + description; these never print "Portland") = `File:Bird's Eye View of Walla Walla, Washington Territory, 1876 (MAPS 127).jpg` (7882x5061, Public domain, E. S. Glover - the "Portland, Oregon" publisher credit sits outside the caption), the two Boston waterfront photo prints `File:Bird's-eye view of waterfront, Boston, Mass. LCCN2005691058.jpg`/`.tif` (5541x4401, Public domain, 1890s, Detroit Publishing Co.), `File:Aiken - Bird's-eye view.jpg` (1320x852, Public domain, 1905 Leighton postcard), `File:Bird's-eye View of Rumford Falls, ME.jpg` (1020x596, Public domain postcard), `File:Bird's-eye View of Machine Shops & Mills, Biddeford, ME.jpg` (649x401, Public domain postcard), `File:Bird's-eye view of Oregon City, Oregon with pedestrian suspension bridge, between 1906 and 1916 (AL+CA 1811).jpg` (768x483, Public domain, Pacific Novelty postcard), `File:Alaska-Yukon-Pacific Exposition birdseye postcard (front).jpg`/`(back).jpg` (1645x1062 / 1652x1067, Public domain, 1909 Seattle), `File:The Architect and engineer of California and the Pacific Coast (1916) (14783351953).jpg` (1352x1698, "No restrictions" - a book page, licence reject too), `File:1753 maps of the African West Coast.jpg` (1268x2000, CC BY 2.0 - licence reject too). **20 keep-pass gate-pass width/licence-fails** (the rest < 4000 px or non-Public-domain) = `File:1876 Birds eye view of the city of Portland Maine BPL.png` (930x663, Public domain - the ME 1876 sheet, BPL scan, too small); the four M. F. King 1865?-1883? Portland ME photos `File:Bird's-eye view of Portland, by M. F. King.jpg`/`.png` (2737x1592) and `File:Bird's-eye view of Portland, Maine, by M. F. King.jpg`/`.png` (2737x1373, all Public domain - photos, too small); `File:Birds eye view of the city of Portland, Maine, 1876 (2675082575).jpg` (2000x1455, CC BY 2.0 - a maps.bpl.org re-scan of the ME 1876 sheet, licence reject); `File:(1882) BIRD'S EYE VIEW OF PORTLAND.jpg` (2934x1881, Public domain, 1882, too small); `File:Bird's-eye View of Wells River, VT.jpg` (828x517, Public domain, a 1907 Leighton postcard of another town, too small); `File:Bird's-eye view of Post Office with Hotel Portland and American Bank Building in the background, Portland, Oregon (AL+CA 1766).jpg` (768x480, Public domain, c1916 in-city photo, too small); the two NYPL Portland ME 1876 scans `File:Bird's-eye view of Portland, Maine (NYPL b11707231-G89F234 036B).tiff`/`036F` (3072x1751 / 3072x1747 - width + another city); `File:Bird's-eye map of Tacoma, Washington, 1878 (WASTATE 651).jpeg` (768x504, Public domain - a photograph of the E. S. Glover Tacoma lithograph, too small); `File:Bird's eye map of buildings and grounds, Alaska-Yukon-Pacific-Exposition, Seattle, Washington, 1909 (AYP 930).jpg` (768x488, Public domain, another city, too small); `File:Bird's-eye View, Meredith, NH.jpg` (645x395, Public domain, a 1905 postcard of another town, too small); `File:1879 map of Portland, Oregon with Goose Hollow boundary and geographical place names overlaid.jpg` (5000x3000, CC BY-SA 3.0, 2012 - a modern overlay map, licence reject); `File:Seattle, Birdseyes, 1888-1889 (SEATTLE 304).jpg` (768x582, Public domain, a pre-fire Seattle postcard, another city, too small); `File:Official catalogue of the Lewis and CLark Centennial and American Pacific Exposition and Oriental Fair, Portland, Oregon, U.S.A., June 1 to October 15, 1905 (1905) (14762958631).jpg` (3488x2136, "No restrictions" - a book page, licence reject); the two Motoring Magazine 1915 street-map pages `File:Portland-Motoring Magazine-1915-070.jpg` (2272x1207) / `File:Portland map from Motoring Magazine 1915.png` (2277x1232, Public domain, too small); `File:Birds-eye view of Winona, Washington, circa 1909 - DPLA - 8cd23a9f4e09eea931fdbfc8b30d0ac8.jpg` (1953x1280, Public domain, a postcard PHOTO of another town, too small).

**The QID's facts** (verified live 2026-10-14 at the 241 session-11 research run; the
transcript is in the QID section above): Q6106, label "Portland" (description "seat of
Multnomah County, and largest city in state of Oregon, United States" - no first-guess QID
from memory was used this time, the search identified the city directly, so the 177/179
mislabel trap class did not fire), enwiki "Portland, Oregon". P625 = ONE value
(-122.67916666666666, 45.515, ~31 m) - the downtown core (no refinement needed). P373 =
the STRING "Portland, Oregon" (a Wikidata quirk, not a country entity - the place is
written from the county + the state). P131 = Q450374 Multnomah (the county seat) +
Q484404 Clackamas + Q484538 Washington (a three-county metro like Columbus, the seat
county leads) - hence place "Multnomah County, Oregon". P17 = Q30 (a proper entity). Name
search at limit 5 AND limit 20: **no trap** (the first hit with P625, what `record --live`
would store, is Q6106 itself, dist 0 - the #1 hit outright at both limits; the hits that
never come first: the other US Portlands - Q49201 Portland (Maine, 2nd at both limits,
4081.9 km), Q753876 Portland (Connecticut, 3991.2 km), Q1807259 Portland (Indiana,
3089.3 km), Q3308164 Portland (Michigan, 2998.2 km), Q80163 Portland (Arkansas, 2980.8
km), Q980152 Portland (Texas, 2969.3 km) (all measured with evidence.hav_m - the pool
mixes the US Portlands, so every sheet was disambiguated from its caption: the state in
the title/bibliographic desc), Q29168518 Portland (Dorset, England), Q1663450 Portland
(Victoria, Australia, 13324.1 km), Q774215 Isle of Portland, Portland State University
(Q1771717, an in-city institution 0.5 km from the city point - the Pittsburgh/Chicago
trap class, but it never comes first), University of Portland (Q513658, in-city, 7.4 km),
the Blazers/Pilots clubs and the name entities - none comes first). No existing site
holds the QID (checked in the catalog, extras, 236a's, 236b's and 240's extras files and
web/data/sites.json - zero case-insensitive "portland" in all of them); the site id
`portland-q6106` is the catalog slug rule (catalog.slug("Portland") = "portland", verified;
a future Portland ME would be portland-q49201 - the id carries the QID, no collision).

## Staging and checks (2026-10-14)

**5 views / 5 site rows - all of the final five** (Omaha staged in the 241 session-4 run;
Indianapolis staged in the 241 session-6 run; Columbus staged in the 241 session-8 run;
Memphis staged in the 241 session-10 run; Portland staged in the 241 session-12 run - all
five LANDED; the first city-5 candidate, Albuquerque, was researched and DROPPED, its
section above). All batch-5 cities stage in this task's own files only: `data/catalog/extras_us_birdseye_batch5.jsonl` (the site rows - region
"United States", kind "town", aerial_ok true, the point = the city's verified P625 or a
recorded refinement, the note recording the staged view's apparent angle so 236c / the matcher
can order the oblique views), `data/commons/files_us_birdseye_batch5.jsonl` (files.jsonl shape
+ the 200 evidence field) and `data/commons/classified_us_birdseye_batch5.jsonl` (p_birdseye
1.0, by "hand"). `--check` (offline, no network), the 241 session-12 run:

```
PASS caption_coords  omaha-q43199|File:Bird's eye view of the city of Omaha, Nebraska 1868. LOC 73693495.tif
PASS caption_coords  indianapolis-q6346|File:Bird's-eye view of Indianapolis showing Spink apartments, hotels, office and industrial buildings - DPLA - d442b7431e1f90b2c13fb4f957e8026f (page 1).jpg
PASS caption_coords  columbus-q16567|File:1872 Birds Eye View of Columbus Ohio - alternate.png
PASS caption_coords  memphis-q16563|File:Bird's eye view of the city of Memphis, Tennessee 1870. LOC 73694530.jpg
PASS caption_coords  portland-q6106|File:Portland, Oregon 1890 Perspective Birds-eye-view Map.jpg
evidence: 5 rows, 5 pass, 0 fail, 0 no-tie
```

No join problems (the file rows name the staged sites; classified rows 1:1; no staged id or QID
collides with an existing site - the module's `known_sites()` reads the catalog, extras,
236a's, 236b's and 240's extras files plus web/data/sites.json on every run). The golden sample
`tests/golden/src_us_birdseye_batch5_sample.json` pins the staged rows (5/5/5; regenerated only
via the module's `--golden` for an intended change).

**All five of this task's cities are LANDED** (Omaha session-4, the 1868 E. Ruger sheet;
Indianapolis session-6, the 1925 E. G. Spink Company sheet; Columbus session-8, the 1872
H. H. & O. H. Bailey sheet; Memphis session-10, the 1870 A. Ruger sheet; Portland session-12,
the 1890 J. McI. Wood perspective sheet; the first city-5 candidate, Albuquerque, was
researched and DROPPED - its section above). The project total is the 25 cities (16 from
236b + 4 from 240 + 5 here) with no shortfall: **236c** now consolidates every staging set
into the canonical data and checks the 25 total. Future-candidate pool hits recorded along
the way (for later batches, NOT staged here - the 185/186 grep found none of them staged
anywhere: Seattle, Salt Lake City, San Antonio, Port Townsend and Buffalo are absent from
all the extras files, the catalog and web/data/sites.json; the "richmond"/"miami" hits in
web/data/sites.json are mention-text in three UK site descriptions (Fort Ancient, Hampton
Court Palace, Stanwick Camp) and the Miamisburg Mound name, not city sites - so Richmond
(VA) and Miami (FL) remain open candidates too): Port Townsend
1878 (the LOC 2003679983 scans, in the Portland pool above), Seattle 1878 (MAPS 64, in the
Portland pool above), Santa Fe 1882 (LOC 75694742, from the 184 Albuquerque probe), Las
Vegas NM 1882 (LOC 75694741 - a DIFFERENT city from Las Vegas, Nevada - disambiguate by
county: San Miguel County; from the same probe) - all Public domain, all >= 4000 px.
**Do NOT write the canonical files - that is 236c; do NOT
re-stage the sixteen cities in 236b or the four in 240's doc.**
