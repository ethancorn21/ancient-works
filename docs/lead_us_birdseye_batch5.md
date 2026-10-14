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
Columbus, Memphis**, then whatever the collection's search order adds to reach five. The task owes FIVE
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

## Staging and checks (2026-10-14)

**2 views / 2 site rows so far of the final five** (Omaha staged in the 241 session-4 run;
Indianapolis staged in the 241 session-6 run; the remaining three land in this task's files the
same way; the counts end at FIVE views / FIVE site rows, or a recorded shortfall, when the five
are done). All batch-5 cities stage in this task's own files only: `data/catalog/extras_us_birdseye_batch5.jsonl` (the site rows - region
"United States", kind "town", aerial_ok true, the point = the city's verified P625 or a
recorded refinement, the note recording the staged view's apparent angle so 236c / the matcher
can order the oblique views), `data/commons/files_us_birdseye_batch5.jsonl` (files.jsonl shape
+ the 200 evidence field) and `data/commons/classified_us_birdseye_batch5.jsonl` (p_birdseye
1.0, by "hand"). `--check` (offline, no network), the 241 session-6 run:

```
PASS caption_coords  omaha-q43199|File:Bird's eye view of the city of Omaha, Nebraska 1868. LOC 73693495.tif
PASS caption_coords  indianapolis-q6346|File:Bird's-eye view of Indianapolis showing Spink apartments, hotels, office and industrial buildings - DPLA - d442b7431e1f90b2c13fb4f957e8026f (page 1).jpg
evidence: 2 rows, 2 pass, 0 fail, 0 no-tie
```

No join problems (the file rows name the staged sites; classified rows 1:1; no staged id or QID
collides with an existing site - the module's `known_sites()` reads the catalog, extras,
236a's, 236b's and 240's extras files plus web/data/sites.json on every run). The golden sample
`tests/golden/src_us_birdseye_batch5_sample.json` pins the staged rows (2/2/2; regenerated only
via the module's `--golden` for an intended change).

**Not done yet - this task's five (batch 5, the final five of the 25 total): Omaha done (city
1/5, the 1868 E. Ruger sheet staged above), Indianapolis done (city 2/5, the 1925 E. G. Spink
Company sheet staged above).** The remaining three in the candidate order: **Columbus,
Memphis**, then whatever the collection's search order adds to reach five (the 181 candidate
list continues past Memphis: "...New Orleans, ..." - New Orleans is already staged by 236b, so
it is skipped; the collection has ~1,500 views, so any US city not already staged - the skip
list: 236a's four, 236b's sixteen, 240's four, this task's staged cities, the catalog,
web/data/sites.json - is fair game as the search continues). A city whose pool yields no usable
view gets a drop note here and the next candidate. **236c** consolidates every staging set into
the canonical data and checks the 25 total (16 + 4 + 5, or a recorded shortfall for a city whose
pool yields no usable view). **Do NOT write the canonical files - that is 236c; do NOT
re-stage the sixteen cities in 236b or the four in 240's doc.**
