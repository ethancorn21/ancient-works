# Bird's-eye views of US cities, batch 4 (task 240): Denver, St. Paul, Minneapolis, Cleveland

GOAL.md point 5 (the 2026-10-13 owner change): the map grows with US cities, and artists' aerial and
bird's-eye views count as much as surveys. Batch 4 is the next four candidates of the 25-city total
after 236b's sixteen (16 + 4 + 5; 236c consolidates every staging set into the canonical data and
checks the 25 total). This task stages **four more US cities, each a new site of its own**, from the
**Library of Congress "Panoramic Maps" collection** (loc.gov/collections/panoramic-maps): about
1,500 US bird's-eye views, 1847-1929, public domain. One own module (`fit/src_us_birdseye_batch4.py`),
one own staging file set (`*_us_birdseye_batch4.jsonl`) - so 240 and 241 (batch 5, the final five)
build in parallel; 241's candidate order continues from this doc's Staging section. Candidate order:
**Denver, St. Paul, Minneapolis, Cleveland** (the 236b lead-doc order after Kansas City / New
Orleans); the task owes four staged cities, not specifically these four - a city with no usable
view gets a note here and the next candidate.

## Fetch route (same as 236b's, re-verified for the batch-4 cities)

The route is the 236b one (full detail in docs/lead_us_birdseye.md, section "Fetch route"):
loc.gov is unreachable from this machine (403, CloudFront bot block), so the files are fetched
from their **Wikimedia Commons mirrors only**; the candidate pool per city is the Commons
file-namespace full-text search in the six plain-phrase forms ("bird's-eye view of <city>", "bird's
eye view of <city>", "birdseye view of <city>", "<city> bird's eye", "<city> birdseye", "Birds' eye
view of <city>", each + ` filetype:bitmap`, srnamespace 6, srlimit 40), deduped, then the gates:
`commons.keep()` (judged AFTER any known-date swap) AND the caption names the city (books_match.norm
over title + description) AND the license is **Public domain** AND the width is **>= 4000 px**.
Re-verified live for Denver at the 240 session-1 run 2026-10-14 (the pool: 65 unique, 33 good).

## QID verification (`.venv/bin/python fit/src_us_birdseye_batch4.py --verify`)

The batch-4 QIDs are verified when their cities are added (label, every P625 value - flagged when
>50 km from the table point, P373, P131 with labels, the enwiki article, and the first name-search
hit with coordinates - what `record --live` would resolve for the caption route). Transcript for
Denver (the 240 session-1 run 2026-10-14, verbatim; re-run with each landing and appended):

```
checked 2026-10-14 - 1 QIDs (Wikidata)
  Q16554  'Denver'  (site id: denver-q16554, new (this task))
      P625: [(-104.98472222222, 39.739166666667)]  (table site point: -104.984722, 39.739167)
      P373: ['Denver, Colorado']
      P131: [('Colorado', 'Q1261'), ('Denver County', 'Q13052701')]  (table place: 'Denver County, Colorado')
      enwiki: 'Denver'  (table wikipedia: 'https://en.wikipedia.org/wiki/Denver')
      search 'Denver': first hit with P625 is Q16554 'Denver' (-104.98472222222, 39.739166666667)
```

No FLAG / TRAP line on the Denver QID: the single P625 IS the table point (dist 0) and the first
name-search hit with coordinates is the city itself (the 236b Pittsburgh/Chicago university traps
do not recur here).

The St. Paul landing (the 240 session-4 run 2026-10-14, verbatim; re-verifies both batch-4 QIDs
now staged):

```
checked 2026-10-14 - 2 QIDs (Wikidata)
  Q16554  'Denver'  (site id: denver-q16554, new (this task))
      P625: [(-104.98472222222, 39.739166666667)]  (table site point: -104.984722, 39.739167)
      P373: ['Denver, Colorado']
      P131: [('Colorado', 'Q1261'), ('Denver County', 'Q13052701')]  (table place: 'Denver County, Colorado')
      enwiki: 'Denver'  (table wikipedia: 'https://en.wikipedia.org/wiki/Denver')
      search 'Denver': first hit with P625 is Q16554 'Denver' (-104.98472222222, 39.739166666667)
  Q28848  'Saint Paul'  (site id: st-paul-q28848, new (this task))
      P625: [(-93.093611111111, 44.944166666667)]  (table site point: -93.093611, 44.944167)
      P373: ['Saint Paul, Minnesota']
      P131: [('Ramsey County', 'Q491201')]  (table place: 'Ramsey County, Minnesota')
      enwiki: 'Saint Paul, Minnesota'  (table wikipedia: 'https://en.wikipedia.org/wiki/Saint_Paul,_Minnesota')
      search 'St. Paul': first hit with P625 is Q174 'São Paulo' (-46.633947222222, -23.550394444444)   <- TRAP: 8953 km, the live record would store a conflict (kind none)
```

The Q28848 TRAP line is the expected, recorded outcome (the 236b Pittsburgh/Chicago class):
searching "St. Paul" at limit 5, the first hit WITH P625 is Q174 São Paulo (8953 km, measured);
the second hit is Q28848 itself (0 km). The single P625 is the table point (dist 0, no FLAG) and
the hand-recorded `caption_coords` tie (dist 0) is the guard - `record --live` is never run for
these rows.

The Minneapolis landing (the 240 session-8 run 2026-10-14, verbatim; re-verifies all three
batch-4 QIDs now staged):

```
checked 2026-10-14 - 3 QIDs (Wikidata)
  Q16554  'Denver'  (site id: denver-q16554, new (this task))
      P625: [(-104.98472222222, 39.739166666667)]  (table site point: -104.984722, 39.739167)
      P373: ['Denver, Colorado']
      P131: [('Colorado', 'Q1261'), ('Denver County', 'Q13052701')]  (table place: 'Denver County, Colorado')
      enwiki: 'Denver'  (table wikipedia: 'https://en.wikipedia.org/wiki/Denver')
      search 'Denver': first hit with P625 is Q16554 'Denver' (-104.98472222222, 39.739166666667)
  Q28848  'Saint Paul'  (site id: st-paul-q28848, new (this task))
      P625: [(-93.093611111111, 44.944166666667)]  (table site point: -93.093611, 44.944167)
      P373: ['Saint Paul, Minnesota']
      P131: [('Ramsey County', 'Q491201')]  (table place: 'Ramsey County, Minnesota')
      enwiki: 'Saint Paul, Minnesota'  (table wikipedia: 'https://en.wikipedia.org/wiki/Saint_Paul,_Minnesota')
      search 'St. Paul': first hit with P625 is Q174 'São Paulo' (-46.633947222222, -23.550394444444)   <- TRAP: 8953 km, the live record would store a conflict (kind none)
  Q36091  'Minneapolis'  (site id: minneapolis-q36091, new (this task))
      P625: [(-93.26916666666666, 44.981944444444444)]  (table site point: -93.26916666666666, 44.981944444444444)
      P373: ['Minneapolis']
      P131: [('Hennepin County', 'Q486229')]  (table place: 'Hennepin County, Minnesota')
      enwiki: 'Minneapolis'  (table wikipedia: 'https://en.wikipedia.org/wiki/Minneapolis')
      search 'Minneapolis': first hit with P625 is Q36091 'Minneapolis' (-93.26916666666666, 44.981944444444444)
```

The Q36091 QID is clean: no FLAG (the single P625 IS the table point, dist 0) and no TRAP (the
first name-search hit with coordinates is the city itself - Denver's pattern, not St. Paul's);
the Q28848 TRAP line repeats as expected, guarded the same way.

The Cleveland landing (the 240 session-11 run 2026-10-14, verbatim; re-verifies all four
batch-4 QIDs now staged):

```
checked 2026-10-14 - 4 QIDs (Wikidata)
  Q16554  'Denver'  (site id: denver-q16554, new (this task))
      P625: [(-104.98472222222, 39.739166666667)]  (table site point: -104.984722, 39.739167)
      P373: ['Denver, Colorado']
      P131: [('Colorado', 'Q1261'), ('Denver County', 'Q13052701')]  (table place: 'Denver County, Colorado')
      enwiki: 'Denver'  (table wikipedia: 'https://en.wikipedia.org/wiki/Denver')
      search 'Denver': first hit with P625 is Q16554 'Denver' (-104.98472222222, 39.739166666667)
  Q28848  'Saint Paul'  (site id: st-paul-q28848, new (this task))
      P625: [(-93.093611111111, 44.944166666667)]  (table site point: -93.093611, 44.944167)
      P373: ['Saint Paul, Minnesota']
      P131: [('Ramsey County', 'Q491201')]  (table place: 'Ramsey County, Minnesota')
      enwiki: 'Saint Paul, Minnesota'  (table wikipedia: 'https://en.wikipedia.org/wiki/Saint_Paul,_Minnesota')
      search 'St. Paul': first hit with P625 is Q174 'São Paulo' (-46.633947222222, -23.550394444444)   <- TRAP: 8953 km, the live record would store a conflict (kind none)
  Q36091  'Minneapolis'  (site id: minneapolis-q36091, new (this task))
      P625: [(-93.26916666666666, 44.981944444444444)]  (table site point: -93.26916666666666, 44.981944444444444)
      P373: ['Minneapolis']
      P131: [('Hennepin County', 'Q486229')]  (table place: 'Hennepin County, Minnesota')
      enwiki: 'Minneapolis'  (table wikipedia: 'https://en.wikipedia.org/wiki/Minneapolis')
      search 'Minneapolis': first hit with P625 is Q36091 'Minneapolis' (-93.26916666666666, 44.981944444444444)
  Q37320  'Cleveland'  (site id: cleveland-q37320, new (this task))
      P625: [(-81.69472222222223, 41.49916666666667)]  (table site point: -81.69472222222223, 41.49916666666667)
      P373: ['Cleveland, Ohio']
      P131: [('Cuyahoga County', 'Q251267')]  (table place: 'Cuyahoga County, Ohio')
      enwiki: 'Cleveland'  (table wikipedia: 'https://en.wikipedia.org/wiki/Cleveland')
      search 'Cleveland': first hit with P625 is Q37320 'Cleveland' (-81.69472222222223, 41.49916666666667)
```

The Q37320 QID is clean: no FLAG (the single P625 IS the table point, dist 0) and no TRAP
(the first name-search hit with coordinates is the city itself - the batch's first clean
first-guess, Denver's and Minneapolis's pattern); the Q28848 TRAP line repeats as expected,
guarded the same way.

## The evidence field (as in 236a/236b)

As in the 236b doc: every staged row carries a hand-recorded `caption_coords` tie in the exact key
order of `fit/evidence.py:caption_route` - the caption names the city and the stored coordinates
are the verified site point itself (dist 0); `record --live` would take the first name-search hit
instead, which is why every QID is verified above and the stage fails loud when a caption does not
print the city. A scan whose file page lost the drawing's date gets the known drawing/publication
date on the row and the page value kept as `date_commons` (the Zwolle precedent; the keep() gate is
judged after the swap).

## Denver (site `denver-q16554`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg` - 1908, Birdseye View
  Publishing Co.; Denver Lith. Co., 19338x13294, Public domain (LC Panoramic maps (2nd ed.), 66).
  **Steep near-vertical whole-city view drawn from the north of the city (the Twenty-Third Street
  Viaduct) looking south**: the banner reads "BIRD'S EYE VIEW OF DENVER, COLORADO, 1908 LOOKING
  SOUTH FROM THE TWENTY-THIRD STREET VIADUCT"; the dense grid legible to the southern suburbs, the
  Front Range along the top of the sheet (the southern horizon), the South Platte meandering in
  from the northwest along the sheet's RIGHT side (the sheet faces south, so west is right - no
  mirroring), a landmark index across the bottom; the drawn extent spans the whole city beyond the
  2000 m town box, so its fit is likely to end a review item (the 236a NY-1811 / DC-ring
  precedent). **Same-sheet scans (one row per sheet, the LOC .jpg staged): the 19338x13294 `.tif`
  twin and the 9000x6205 DPLA copy (4ac8083cbba722c01cad3388a37a7a0f)** - both eyeballed, identical
  sheet (the 236b batch-3 close-out). The page date (1908) matches the drawing (no Zwolle-style
  swap).

**DROP (with reasons):** the **1881 J. H. Flett whole-city sheet** (the pool's smallest whole-city
view; the LOC copy's own description says "Photocopy", LC Panoramic maps (2nd ed.), 63, inset
"view of Denver 1859") - `File:Bird's eye view of the city of Denver, Colorado, 1881. LOC
75693129.jpg`/`.tif` (4348x2857) + the two 7000x4575 DPLA copies (8799e7c5 / f442e0ad, "Scale not
given") - a steep near-vertical whole-city view, but the shallower-quality same-genre sheet (one
row per city: the 1908 is steeper and sharper). The **1887 Rocky Mountain News / Mills Eng. Co.
sheet** - `File:Bird's-eye view of Denver, 1887. LOC 75693131.jpg`/`.tif` (8048x6016, LC
Panoramic 64) + the two 7000x5238 DPLA copies (0f7a446c / bd8a42c6) - steep oblique from the NW
(Capitol foreground bottom, grid receding to the mountain horizon): shallower than the 1908. The
**1882 C. H. Platt / W. H. Slocum chromolithograph** - DPLA 10000x6774 (2030beda) + 8999x6096
(495911c2) - steep oblique from the north (the Platte in the foreground): same-genre dupe,
shallower. **The 1874 E. S. Glover sheet** (Strobridge & Co. Lith., inset "Denver in 1865") - the
pool's OLDEST whole-city view (from the NW looking SE): DPLA 10000x7749 (f0ef7f8d, page date
1874) + 8999x6974 (7f6b1ead, undated) are same-sheet dupe scans; the three 1536-px copies
(94f7c085 / aae0b82d / d5be6563) are too small. The **1887 "Souvenir of Arbor Day, May 6th 1887.
Birds eye view of Colfax avenue from Montclair, 350 ft. above Denver"** (two 7000x3920: 095a7fee /
d64efa95) - a **district close-up** (the Fort-Negley class): the Colfax-avenue corridor and the
Montclair subdivision fill the sheet (a real-estate dealer's souvenir sheet, W. B. von
Richthofen, The Denver Litho Co.), the city a background at the left - not a whole-city view
(eyeballed at the 240 session-1 run). The **1895 `View in Denver. "Birds-eye view of the line
waiting for the touch of the 'Healer'"`** (.jpg/.tif LCCN92519709, two 4096x3281) - a
**PHOTOGRAPH** (W. A. White, Raton, New Mexico, copyright 1895), not a bird's-eye map: a street
scene of the crowd waiting for the street car - the title's "birds-eye view" is a joke
(eyeballed at the 240 session-1 run; the 236a HABS-photo precedent). The **1907 "Birdseye view
from South Broadway ... showing Harlem, Jacksons Broadway Heights & city of Denver"** - four scans
(LOC 76693078 .jpg/.tif 7888x6144, the two DPLA 7992x6273 copies 72a22de5 / dbc3cc9d, CO Denver
1907.jpg) - a **real-estate ad** ("LOTS FOR SALE", Haraszthy & Vuit, copyright 1908): the suburban
subdivisions fill the sheet, the city a small dot on the horizon. The **1913 "Denver and the
Rockies as viewed from the tower of the Daniels and Fisher Stores Co."** (two 12000x5339/5357 DPLA
scans, page 2/3 of 37476cb8...) - a **PHOTOGRAPH** (copyright 1913 by the store), the city small in
a mountain panorama (the photo + Bohn-class precedent); the 1755x3612 cropped copy (0f5d5a4e) is
too small. The **Clayton Industrial School sheet** (4017x1780) - an institution close-up (the
Fort-Negley class). The **"mountains & plains from 'Lookout Mountain'"** (7000x5587) - **regional**,
Denver a dot (the DC 1861 Bohn regional-drop precedent). The **"Topographical birds-eye view, the
state of Colorado"** (DPLA 5000x3680, Clason Map Co.) - a **STATE-level** view; the pool's "1603"
year for it is a FALSE year picked up from the DPLA hash inside the title (94ad02d5d2fbe5c1603...)
- a year_of title-scan hitting the hash, recorded so it is not mistaken for a 1603 sheet. The
**Union Pacific "World's pictorial line" book sheets** (Knight, Leonard & Co., Chicago: the
"Great Plains" and "Texas Pan Handle" Overland Route books) - **regional book sheets**: the 1890
"Great Plains" sheet (1536x618) and the "(Covers to) Great Plains" (2459x2847) are too small, and
the wide ones (the "(Covers to) Texas Pan Handle" 4087x4634, the two "(Text Page)" sheets
13661x5498/22726x9036 - the verso carries a full-colour birdseye of the states, Denver a small
part of the frame - and the two 1893 Rocky Mountain sheets 7000x3160, the last two caption-gate
rejects) are the regional book-sheet class (the KC Union Pacific book-sheet precedent). The
**other-city caption-gate rejects**: 1873 Golden, 1874 Pueblo, 1882 Canon City (incl. the
"Lincoln Park ... Dewees and Dye" plat), 1882 Greeley, 1882 Gunnison, 1882 Leadville x3, 1882
Maysville, 1882 Colorado Springs + Manitou, Las Animas x3 (one 1904), Buena Vista, Idaho Springs.
**Too small** (< 4000 px): 1865 Kilburn x2 (2737x1391), the 1889 "CO Denver 1889.jpg" (1024x656),
the two NYPL 3072-px tiff pair (b11707599-G90F039 017B/017F). **Licence rejects:** the 1907
"Denver, CO 1907 Bird's Eye View.jpg" (CC BY-SA 4.0, 1500x1000). **keep() rejects:** the 2021
"Union Station North 002.jpg" (CC0, 1904x1413 - beyond the 1925 MAX_YEAR and below the 4000-px
width gate).

**The QID's facts** (verified live 2026-10-14 at the 240 session-1 run; the transcript is in the QID
section above): Q16554, label "Denver" (the consolidated city-county and capital of Colorado; the
first-guess QID Q3101 is a PERSON - Patrick Ricard - caught by the label check, the usual
first-guess trap class), enwiki "Denver". P625 = ONE value (-104.984722, 39.739167, 30 m) - the
central CBD (the 16th-20th street core; no refinement needed). P373 = the STRING "Denver, Colorado"
(a Wikidata quirk, not a country entity - the place is written from the county + the state).
P131 = Q1261 Colorado + Q13052701 Denver County (Denver is a consolidated CITY-COUNTY, the
county-level twin of New Orleans' single-parish case - hence place "Denver County, Colorado").
P17 = Q30 (a proper entity). Name search: **no trap** (the first hit with P625, what `record
--live` would store, is Q16554 itself, dist 0). No existing site holds the QID (checked at the 240
session-1 run in the catalog, extras, 236a's and 236b's extras files and web/data/sites.json); the
site id `denver-q16554` is the catalog slug rule (catalog.slug("Denver") = "denver", verified).
The drawing's vantage, the Twenty-Third Street Viaduct, sits ~1.3 km north of the site's point
(23rd-street lat 39.7508 - P625 39.739167 = 0.0116 deg x 110900 m/deg = 1287 m, measured
2026-10-14).

## St. Paul (site `st-paul-q28848`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:St. Paul, Minn. LOC 75694650.jpg` - 1906, Robert M. Saint, 9888x5600, Public domain
  (LC Panoramic maps (2nd ed.), 411). **Steep near-vertical whole-city view drawn from a high
  vantage on the east (the Minnesota side) looking west**: the banner reads "St. Paul, Minn." and
  the sheet's own "COPYRIGHT 1906: BY ROBT M. SAINT, ST. PAUL." (lower right) - the page date
  (1906) is the drawing's year (no Zwolle-style swap). The Minnesota (from the east, lower
  right) and the Mississippi (from the south, lower left) meet at the sheet's lower centre; the
  joined river runs diagonally up-right (north), the dense 1906 downtown grid (the Capitol, the
  big warehouse blocks) sits centre-right on the Mississippi's WEST bank, the spreading city
  grid beyond it, and the farmland horizon across the top of the sheet (the west) - the drawn
  extent spans the whole city beyond the 2000 m town box, so its fit is likely to end a review
  item (the 236a NY-1811 / DC-ring precedent). The sheet faces ~WSW (orientation verified at
  the 240 session-4 run: the confluence -> downtown bearing is 293 deg (WNW) and the downtown
  cluster sits up-RIGHT of the confluence on the sheet, so the sheet's up direction is ~WSW;
  the Mississippi approaches the confluence from the south and the Minnesota from the east, so
  the rivers cannot be mirrored). **Same-sheet scan (one row per sheet, the LOC .jpg staged):
  the 9888x5600 `.tif` twin** - eyeballed, identical sheet.

**DROP (with reasons):** the **1883 H. Brosius sheet** (LOC 84690615, 12384x8160, LC Panoramic
409.1, "Pop. 75,000", "H. Brosius, del.") - steep Birdseye-style oblique with a row of facades
across the top (the second steepest whole-city view in the pool): one row per city, the 1906 is
steeper (near-vertical). The **1874 Ellsbury / Green sheet** (LOC 75694648 .jpg/.tif,
9408x4912, LC 409) - steep oblique from the west bluffs looking east (third). The **1888 ice-
palace / winter-carnival souvenir** (LOC 78693710, 9040x5392, Marr & Richards / Baker Collins &
Co., LC 409.2) - high-angle but far: the city a small central cluster, the sheet mostly
surrounding farmland (the 1888 ice palace on the Minnesota). The **1853 Thompson Ritchie
chromolithograph** (LOC 78693711, 6608x4832, "10 Oct 1853", LC 406.1) - a scenic river
panorama, the city a thin band on the horizon. The **1873 A. Haagenberg panorama strip** (LOC
75694649, 8016x2832, LC 408) - a river-level panorama strip (flat). The **1907 F. L. Wright
PHOTOGRAPH** (LCCN2013647319 .jpg/.tif, 6668x2240, "Birds eye view of St. Paul free public
baths") - a photo of the riverside free public baths (the photo + Bohn-class precedent). The
**1915 PHOTOGRAPH** (LCCN2007662304 .tif, 4161x700, "Birdseye view of St. Paul from Cathedral
Tower") - a photograph panorama strip from the cathedral tower. **Three search-noise rows that
pass the text gate but are not St. Paul** ("St. Paul" only in a book description / church /
railroad name): the Knowles farm-residence (Whitewater Tp. WI, 5676x6645) and the Eldridge
fruit-farm (Winona MN, 5900x6645) - both from A. T. Andreas's farm-residence book, whose
deluxe edition "added views of Minneapolis, St. Paul, and Winona" - and the Oconomowoc / Waukesha
lake-region ad (LOC 77694096, 11105x6199, Marr & Richards, 1890; "St. Paul" only in the
Chicago, Milwaukee & St. Paul Railway name). **St. Paul sheets passing the gates but rejected
on size (< 4000 px wide):** the 1893 "looking west from Dayton's Bluff" (LOC 75694647 .jpg/.tif,
3312x2552, Brown, Treacy & Co.), the 1904 state capitol (LCCN2003675026 .jpg/.tif, 1536x807),
the 1908 Cedar Street towards the capitol (LCCN94505319 .jpg/.tif, 3243x4096 - a street-level
close-up), and the two NBY postcards (423551 817x506 / 423552 820x505 - also keep() rejects).
**Other-city / noise rows (caption-gate rejects or not this city):** 1870 Buffalo (LOC
LCCN2005686636 .jpg/.tif, 1536x1309 - "from scaffolding of St. Paul's Cathedral tower" -
"St. Paul" = a cathedral name, and it is Buffalo), the 1888 "federal government" sheet
(1880x2572, No restrictions - gate reject), London 1905 (CC BY 2.0, 3285x2052) + 1887 Central
London (5226x3773, gate reject) + the 1910 Christmas-card "Birds Eye View of City" (CC BY 2.0,
1971x3097), Bovill ID 1911 (CC BY 2.0, 1500x938), Valparaiso IN x3 (1920 / 1910 / 1911, CC BY
2.0), Delaware OH x2 (DPLA, No restrictions; "St. Paul's" = a church), Columbus OH 1872 (LOC
84690606, gate reject), Saint Boniface MB 1880 (gate reject), Fargo 1876 (760x440, gate
reject), Syracuse 1908 (864x499), Staten Island (NYPL, gate reject); the St Paul's
(London cathedral) items (1875 "St Paul's old" from Francis Bond; 1873/1540 "St Paul's and the
Neighbourhood"; 2015 Cathedral Dome CC BY-SA 4.0; 2021 Brewer-Ludgate CC BY-SA 4.0); the 2012
capitol photo (CC BY 2.0, 1477x971); the **Minneapolis Flour Milling District sheet (DPLA,
2191x2813, gate reject) - belongs to Minneapolis's (city 3) pool, not a St. Paul drop**; and
the non-view rows (the 1922 Yellowstone road-log book sheet, No restrictions; the Vitanje
postcard; the two NARA cofferdam photographs, 3000x1786, keep() rejects; the Macau 大三巴牌坊
photo, CC BY-SA 4.0; the 1907 "highest priced half mile of real estate" sheet, No restrictions
- gate reject).

**The QID's facts** (verified live at the 240 session-4 run; the transcript is in the QID
section above): Q28848, label "Saint Paul" (the capital of Minnesota and seat of Ramsey
County; the first-guess QID Q16842 is a PERSON - Sami Niemi - caught by the label check, the
usual first-guess trap class), enwiki "Saint Paul, Minnesota". P625 = ONE value (-93.093611,
44.944167, 30 m) - the downtown/Capitol at the river confluence (no refinement needed). P373 =
the STRING "Saint Paul, Minnesota" (a Wikidata quirk, not a country entity - the place is
written from the county + the state). P131 = Q491201 Ramsey County (the only one) - hence
place "Ramsey County, Minnesota". P17 = Q30 (a proper entity). Name search: **TRAP** - the
first hit with P625 for "St. Paul" is Q174 São Paulo (8953.4 km - the 236b Pittsburgh/Chicago
trap class), the second hit is Q28848 itself (0 km). Other P625 hits (nearest first): Iowa
481.9 km, Nebraska 601.4, Missouri 705.1, Kansas 843.7, Indiana 867.9, Arkansas 1015.7,
Alberta 1648.0, Alaska 5255.5, Wiltshire 6330.8, Aachen 6847.7, Erding 7346.6, HK college
12045.7 - no local near-miss (unlike Kansas City's 10.2 km twin). No existing site holds the
QID (checked at the 240 session-4 run in the catalog, extras, 236a's and 236b's extras files
and web/data/sites.json); the site id `st-paul-q28848` is the catalog slug rule
(catalog.slug("St. Paul") = "st-paul", verified), and the SITES name is "St. Paul" (NOT "Saint
Paul") - the caption gate needs the short form the banner prints ("st paul" is not a substring
of "saint paul"; the 236b St. Louis precedent).

## Minneapolis (site `minneapolis-q36091`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Minneapolis, Minnesota. LOC 75694644.jpg` - 1885, W. V. Herancourt (draughtsman);
  I. (Isador) Monasch (publisher), 13152x9408, Public domain (LC Panoramic maps (2nd ed.), 396).
  **THE steepest (near-vertical) whole-city view in the pool: the built-up city fills the whole
  frame with no horizon band**, drawn from a high vantage on the south/southwest of the city (the
  west bank, below the downtown) looking north (slightly west): the banner reads "BIRD'S EYE VIEW
  OF MINNEAPOLIS, MINN. 1885 POPULATION 71,235" and the page date (1885) is the drawing's year
  (no Zwolle-style swap). The sheet faces ~NNW/N (measured on the 13152 px original at the 240
  session-7 run: U ~330-350 deg from the 3rd Street bridge -> river-exit bearing and the core ->
  3rd Street pair): the Mississippi enters upper-left (the rapids below the falls; a long stone
  arch rail viaduct and an iron trestle cross the wide fast water there - NOT the Stone Arch
  bridge at the falls' foot: the on-sheet distance is ~3x the falls-bridge distance at the
  sheet's own ~2 km/1000 px scale, so the viaduct sits further out on the west, its identity
  open; a small creek - a minor tributary, not a river - runs from the viaduct zone through the
  near-side residential quarter, a street bridge over it, a small cascade into the main water, a
  big brick/stone waterwheel mill at the far left) and runs diagonally to the lower-right,
  exiting at the sheet's bottom edge toward the OFF-SHEET confluence with the Minnesota; the
  dense west-bank downtown core (the "HENNEPIN STEAM LAUNDRY" = Hennepin Avenue = the west bank)
  sits on the FAR (upper) side of the river, upper-left of the 3rd Street suspension bridge (the
  big two-tower masonry span at the sheet's mid-right - confirmed by form), a small two-tower
  suspension span near the viaduct (identity unresolved - the 1885 Mississippi had only the 3rd
  Street suspension), and a huge brickyard fills the bottom-right corner; the rivers' identities
  cannot be mirrored (the Mississippi enters upper-left and exits bottom-right). The drawn
  extent spans the whole city beyond the 2000 m town box, so its fit is likely to end a review
  item (the 236a NY-1811 / DC-ring precedent). **Same-sheet scan (one row per sheet, the LOC
  .jpg staged): the 13152x9408 `.tif` twin** - eyeballed, identical sheet.

**DROP (with reasons):** the **1867 "Minneapolis and Saint Anthony, Minnesota" sheet** (LOC
73693455 .jpg/.tif, 8958x6840, LC 393) - the TWIN-CITIES sheet (both pre-merger cities, oblique,
pre-annexation scope). The **1879 "Panoramic view of the city of Minneapolis, Minnesota" sheet**
(LOC 75694642 .jpg/.tif, 10352x6512, LC 395, "Looking north west") - an oblique, shallower than
the 1885 pick; and the **1879 DPLA reprint (7ccb8501, 8999x5988)** - a second printing of the
SAME 1879 sheet (the Minneapolis & St. Louis Railway Co. edition). The **1886 A. Hageboeck
engraved sheet** (LCCN2008677251 .tif, 12816x9504; the .jpg twin 1024x759 is too small) - an
oblique RIVERFRONT-CORRIDOR view (the 3rd Street suspension bridge in the foreground), not a
whole-city bird's-eye view. The **1891 A.M.R. Smith & Geo. Renger sheet** (LOC 75694646,
13248x9344, LC 397) - near-vertical but shallower than the 1885 pick (it recedes to a distinct
horizon + sky band); same-sheet scans: the LOC 75694905 "1/4 size" photocopy .jpg/.tif (6384x4576,
"Unfinished") and the DPLA 30b065a3 copy (11971x8353, "looking south from the Mississippi
River") - one row per sheet. The **1907 "Looking southwest from Guaranty Bldg." photographic
strip** (LCCN2013647302 .jpg/.tif, 6588x2193) - a PHOTOGRAPH (F.L. Wisthof Photo, St. Paul; "1
photographic print (postcard)"), low vantage, downtown close-up - a photograph, not a drawn
bird's-eye view (the 236a photo precedent). **Non-view items passing the gates:** the DPLA
396e002a "Bird's Eye View of the Minneapolis Public Library System" (7922x6349) - a schematic
library-branch map (the MHL), not a bird's-eye view; the DPLA 5a20a334 "Minneapolis Perspective
Map - GIANT Post Card" (4144x5312, "C 1937 W. LaRue", Langwith Map Co.) - a 1937 stylized
postcard (beyond the collection's 1929 edge; a street map, not a bird's-eye view); the four
search-noise rows - the Knowles farm-residence (Whitewater Tp. WI / Winona, 5676x6645) and the
Eldridge fruit-farm (Winona, 5900x6645) plates (both from A. T. Andreas's farm-residence book,
whose deluxe edition "added views of Minneapolis, St. Paul, and Winona" - "Minneapolis" only in
the book description; the same David Rumsey plates that landed in St. Paul's pool), the 1500
Jacopo de' Barbari "View of Venice" held by the Minneapolis Institute of Art (25616x12341 -
"Minneapolis" = the holding institution's name), and the Yellowstone NP Northern Pacific / Poole
Bros. map (6486x8428, 1898 - a regional park map). **The 30 non-good rows:** **too small
(< 4000 px wide)** - the ten DPLA 2144-2227 px scans (af17407d "Aerial" 2224x2871; 36f15008
"Omaha" note 2144x2704; e224b77b "West of Fourth Street" 2202x2784; c3e5eb75 "Business District
from City Hall" 2189x2784; bd25174b Lillehei postcard 2160x2711; 5b4ae258 "from Court House
Tower" 2196x2808; d32e260b "from the East Side" (Beard Art Galleries) 2195x2848; 260ce480
tower-of-City-Hall / Fourth Street 2227x2817; 804818d7 University of Minnesota campus
2200x2720; 0e3d5345 Flour Milling District 2191x2813 - the item that also surfaced in St.
Paul's pool, confirmed to belong here), the Hageboeck .jpg 1024x759 (same sheet as the good
.tif), the two NBY postcards (423111 825x499 / 423112 824x498 - also keep() rejects), the 1904
photo 051907-010-Minneapolis1904.jpg (3072x1800 - a photograph of a portion of the
"Perspectives of St. Paul, Minnesota" document, and too small), the Venice MIA detail (800x800),
the two Yellowstone book covers (2730x2936 - also keep(); 3054x1506). **keep() rejects (no
usable date / beyond 1925 MAX_YEAR):** "Downtown Minneapolis" DPLA bcec1d86 (6016x4763 -
undated; also a downtown close-up), the cul-de-sac photo (CC0, 2018, 3992x2242 - also the
caption gate and the width), the two 2026 "Minneapolis Rebel Loon" images (CC0, ~1952 px - a
Star-Wars-shaped loon graphic, not a view), the Dark-eyed Junco photo (CC BY 2.0, 2006,
1452x1044 - also licence and width). **Licence rejects:** the MCAD campus (CC BY 3.0, 600x399 -
also width) and the Kapkap, Solomon Islands item (CC BY 4.0, 5012x4924 - also the gate).
**Caption-gate rejects (no "Minneapolis" in the caption):** the 1913 Superior, WI sheet (LOC
75696722 .jpg/.tif, 8416x6224, LC 1059), the DPLA Lake Minnetonka plate (2195x2800 - also
width; the "1482" year is a FALSE year picked up from the DPLA hash), the Venice Google Art
Project pair (6727x3222 + the 1240x734 cropped - the 1500 Jacopo de' Barbari, keep() too: 1500
predates the collection window) and the Venice alternative scan (6700x3205).

**The QID's facts** (verified live at the 240 session-8 run; the transcript is in the QID
section above): Q36091, label "Minneapolis" (the largest city of Minnesota and seat of
Hennepin County; the first-guess QID Q3094 is a ROMANIAN MONASTERY - Căldărușani Monastery,
Ilfov County - caught by the label check, the usual first-guess trap class; the third of the
batch: Denver's Q3101 a person, St. Paul's Q16842 a person), enwiki "Minneapolis". P625 = ONE
value (-93.26916666666666, 44.981944444444444, 30 m) - the downtown core (no refinement needed).
P373 = the BARE STRING "Minneapolis" (the usual US quirk in its extreme - the place is written
"Hennepin County, Minnesota" from P131 + the state). P131 = Q486229 Hennepin County (the only
one). P17 = Q30 (a proper entity). Name search: **no first-hit trap** - the first hit with P625
is the city itself (0 km, Denver's pattern); the in-city institution class ranks behind the city
(the Great Northern Depot 0.4 km, Hennepin County Medical Center 1.2, the Minneapolis Institute
of Art 2.6, MCAD 2.8, North Community High 2.8, the Heart Institute 3.3, South Community High
4.5, the metro 6.5, the MSP airport 11.7) so no TRAP line is expected from --verify (none in
the session-8 transcript); other P625 hits: Minneapolis, Kansas (746.9 km) and Minneapolis, NC
(1370.2 km, unincorporated) - no local near-miss (unlike Kansas City's 10.2 km twin). No existing
site holds the QID (checked at the 240 session-6 run in the catalog, extras, 236a's and 236b's
extras files and web/data/sites.json); the site id `minneapolis-q36091` is the catalog slug rule
(catalog.slug("Minneapolis") = "minneapolis", verified), and the SITES name is "Minneapolis"
(the caption prints the full name - no short-form gate issue).

## Cleveland (site `cleveland-q37320`, this task's point = the verified P625; 1 view staged)

**STAGED** (one row per sheet; dupes dropped):

- `File:Birds eye view of Cleveland, Ohio 1877. LOC 73694507.jpg` - 1877, A. Ruger (artist);
  lith. by Shober & Carqueville, Chicago (the sheet's own line "LITH. BY SHOBER & CARQÉVILLE
  CHICAGO" keeps its accent; the row label and the SOURCES label stay ASCII), 10704x6544,
  Public domain (LC Panoramic maps (2nd ed.), 687.2). **THE steepest (near-vertical) whole-city
  view in the pool: the rotated street grid legible across the whole frame (lakefront to the
  farmland horizon)**, drawn from a high vantage OVER LAKE ERIE (south of the city; the lake
  with its sailing/steam traffic fills the bottom band) looking NORTH (sheet up = north,
  confirmed three ways - the Cuyahoga enters from the north, the Chippewa to its east, the lake
  to the south - no mirroring possible; verified on the 19.4 MB original at the 240 session-10
  run): the banner reads "BIRDS EYE VIEW OF CLEVELAND / OHIO 1877" (three lines, no apostrophe)
  bottom-centre; "A. RUGER, ARTIST" at the image area's lower-left corner; "ENTERED ACCORDING
  TO ACT OF CONGRESS BY J. J. STONER MADISON WIS." lower right; the LC stamp "Division of Maps
  / FEB 28 1941 / Library of Congress" and the handwritten call number "G4084 .C5A3 1877 .R8 /
  Rug 157" - the page date (1877) is the drawing's year (no Zwolle-style swap). The Cuyahoga
  meanders in from the upper centre (the north) to its mouth at the sheet's centre-right,
  crossed by the multi-arch Washington Avenue viaduct (label "WASHINGTON" on the sheet) and a
  truss bridge, the "UNION PASSANGER DOCK" (spelled so on the sheet) on the WEST side of the
  mouth; the dense downtown core (Public Square with its fountain, on the bluff above the
  lakefront - the site's P625 point sits right at it) at the sheet's centre just left of the
  mouth; the Woodland / Catholic / Cleveland cemeteries and the factory stacks on the farmland
  horizon at the top; the "SUPERIOR" street label lower-left; the "CHIPPEWA RIVER" meander
  upper-right (east of the Cuyahoga). The drawn extent spans the whole city beyond the 2000 m
  town box, so its fit is likely to end a review item (the 236a NY-1811 / DC-ring precedent).
  **Same-sheet scans (one row per sheet, the LOC .jpg staged): the 10704x6544 `.tif` twin and
  the DPLA-family `File:Cleveland 1877.jpg` (the same sheet, a wider index crop)** - both
  eyeballed, identical sheet.

**DROP (with reasons):** all 48 of the pool's 51 unique rows besides the staged sheet and its
two same-sheet scans (the pool: 51 unique / 9 good, every good thumb eyeballed one by one at
the 240 session-10 run), grouped: the **1853 John W. Hill sheet** (`File:Cleveland, 1853 - DPLA
- 2b1e8d8d2e48334e8a6e02a36fa36987.jpg`, 11831x8413, Public domain) - a mid-steepness oblique
drawn from Ohio City (the independent municipality west of the Cuyahoga, annexed 1854) looking
east, Superior Street at the centre - the pool's OLDEST whole-city view, but shallower than
the 1877 pick (one row per city). The **1887 C.H. Vogt & Son sheet** (two scans: the LOC
`File:Cleveland, Ohio. LOC 75694918.jpg` 6632x5128, LC Panoramic maps (2nd ed.), 689; the
DPLA-family `File:Cleveland 1887.jpg` 6632x5125) - shallower than the pick (a bigger sky band,
the city receding to the farmland horizon); its banner prints only "CLEVELAND, OHIO." - the
year 1887 comes from the LC record alone (the file page's "Birds-eye view of Cleveland, Ohio
in 1887"). The **1884 Edward Molitor "Bird's-eye view of the Mississippi River" sheet**
(`.tif`, 9558x4942, Public domain; its 604x336 cropped copy is too small) - a REGIONAL
three-band view from the mouth of the Missouri to the Gulf of Mexico: "Cleveland" only as the
publisher's place ("Cleveland, Ohio: Brooks and Co Publishers") - it passed the caption gate
via the file description, but it is not a city view (the DC 1861 Bohn regional-drop
precedent). The **1923 Fairchild "Remarkable airplane view of the heart of the east end of
Cleveland"** (`File:Bird's Eye Photograph of the East End of Cleveland - DPLA -
66f1c763439535f396561c8932b904be.jpg`, 9570x6491, Public domain) - a rotogravure (the Sunday
News-Leader, January 7, 1923) of a 1923 airplane PHOTOGRAPH of the Euclid/Cedar/E 105th
neighbourhood - a district close-up (the Fort-Negley class), not the whole city, and a
photograph, not a drawn view. The **1890 Lucien R. Burleigh "Cleveland, N.Y." sheet**
(`File:Cleveland, N.Y. LOC 2009584347.jpg`, 11072x7850, Public domain, Burleigh Litho) - a
DIFFERENT Cleveland: the village on Oneida Lake, Onondaga County, New York (a good sheet of a
different city - the same-city-name trap class). The **DPLA district close-ups (all "No
restrictions" - a licence reject - and all < 4000 px wide):** the Cleveland Municipal
Stadium x2 (3328x2112, "239c2c1e" - the Terminal Tower, the Cleveland Mall), the
Municipal-Stadium-and-downtown x4 (3296x2080 / 3328x2112, "31a647d5" and "50b3f04a"), the
Cleveland City Hospital x4 (3328x2112 / 3296x2080, "031265df" and "e85e3c19" - the "1317"
year in both of those titles is a FALSE year picked up from the DPLA hash inside the title,
the Denver-1603 class), the Rockefeller Park x6 (3296x2080-3360x2144, "f8ea4fc0" - the "1426"
hash year on two of the titles -, "2458aea2", "ae05937b"), the Cleveland Museum of Art / Wade
Park x2 (3296x2080 / 3360x2144, "a373577c"), the Edgewater Park bathing beach x2 (3296x2080,
"5c57a079"), the Art Museum and Fine Arts Garden x2 (3296x2080, "4f9d9309"). The
**industrial-ad scans (keep() rejects):** the Adams Paint Company (3284x2114, No restrictions,
page 2015 - beyond the 1925 MAX_YEAR), the Cleveland-Chandler Motors Corporation HAER
rendering (5000x3963, Public domain, 1968 - an early-20th-century plant rendering, beyond
MAX_YEAR), the Dixie Foundry "16 acre plant" postcard (828x527, Public domain, 1930 - keep()
+ width + the caption gate). The **other-city scans ("Cleveland" only as a name):** Hancock,
Michigan 1873 (2000x1557, CC BY 2.0 - the author is A. J. Cleveland), Houghton, Michigan
1872 (2000x1517, CC BY 2.0 - the publisher is Cleveland & Porter), Canton, Ohio 1913
(3329x700 - the caption gate rejects it correctly), Walrus Island 1873 (1821x1407, Public
domain - the caption gate + width). The **false search hits:** the two Israël Silvestre
château paintings held by the Cleveland Museum of Art (CC0, 5640x4204 Fontainebleau /
5613x4397 Versailles - "Cleveland" is the holding institution's name; the "1679"/"1676" years
are FALSE years picked up from the file names), the 1884 "A lake tour to picturesque
Mackinac" book sheet (2828x1536, No restrictions - a view of Port Huron from the decks of the
steamers City of Mackinac / City of Cleveland; "Cleveland" in the company name), and the
eight 1864 William R. Lowes letter pages (DPLA, 2411-2461 x 3019-3053, Public domain -
Civil-War letters from Lookout Valley, Tennessee; the caption gate rejects them correctly).
The **NBY "Aeroplane View of Union Terminal Group and Public Square" postcard** (514x821,
Public domain, 1930 - a photograph, keep() + width + the caption gate).

**The QID's facts** (verified live at the 240 session-10 research run, re-verified by the
session-11 --verify; the transcript is in the QID section above): Q37320, label "Cleveland"
(the largest city of Ohio and seat of Cuyahoga County; first-guess check: the "Cleveland,
Ohio" name search's first hit IS the city itself - the batch's first clean first-guess
(Denver's Q3101 a person, St. Paul's Q16842 a person, Minneapolis's Q3094 a Romanian
monastery) - though the memorized QID Q131855 turned out to be a ROADSTER (a bicycle; enwiki
"Roadster (bicycle)", no P625) - a memory error caught by the label check), enwiki
"Cleveland". P625 = ONE value (-81.69472222222223, 41.49916666666667, 30 m) - the central CBD
(no refinement needed). P373 = the STRING "Cleveland, Ohio" (the usual US quirk - the place
is written "Cuyahoga County, Ohio" from P131 + the state). P131 = Q251267 Cuyahoga County
(the only one). P17 = Q30 (a proper entity). Name search "Cleveland" (limit 20): **no
first-hit trap** - the first hit with P625 is the city itself (0 km, Denver's and
Minneapolis's pattern); the in-city institution traps rank behind it (Cleveland State
University 1.7 km, Cleveland Clinic 6.1, Cleveland Museum of Art 7.0, Cleveland Guardians
0.9, Cleveland Browns 0.9); other-state namesakes: Cleveland TN 756.0 km (the big one near
Knoxville), Georgia 788.6, Quebec (Canada) 901.4, Mississippi 1172.0, Oklahoma 1400.0;
foreign: Tasmania 15993.8 (Cleveland, Wisconsin and Texas carry no P625 in the top 20) - no
local near-miss. No existing site holds the QID (checked at the 240 session-10 run in the
catalog, extras, 236a's and 236b's extras files, 241's absent batch-5 file, this task's own
file and web/data/sites.json); the site id `cleveland-q37320` is the catalog slug rule
(catalog.slug("Cleveland") = "cleveland", verified), and the SITES name is "Cleveland" (the
caption prints the full name - no short-form gate issue).

## Staging and checks (2026-10-14)

All batch-4 cities are staged in this task's own files only: **4 views / 4 site rows**
(Denver, St. Paul, Minneapolis, Cleveland) in `data/commons/files_us_birdseye_batch4.jsonl`
(files.jsonl shape + the 200 evidence field) and `data/commons/classified_us_birdseye_batch4.jsonl`
(`p_birdseye: 1.0`, `by: "hand"`); the site rows are in `data/catalog/extras_us_birdseye_batch4.jsonl`.
`--check` (offline, no network), the 240 session-11 run:

```
PASS caption_coords  denver-q16554|File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg
PASS caption_coords  st-paul-q28848|File:St. Paul, Minn. LOC 75694650.jpg
PASS caption_coords  minneapolis-q36091|File:Minneapolis, Minnesota. LOC 75694644.jpg
PASS caption_coords  cleveland-q37320|File:Birds eye view of Cleveland, Ohio 1877. LOC 73694507.jpg
evidence: 4 rows, 4 pass, 0 fail, 0 no-tie
```

No join problems (the file rows name the staged sites; classified rows 1:1; no staged id or QID
collides with an existing site - the module's `known_sites()` reads the catalog, extras, 236a's,
236b's and 241's extras files plus web/data/sites.json on every run). The golden sample
`tests/golden/src_us_birdseye_batch4_sample.json` pins the staged rows (4/4/4; regenerated only
via the module's `--golden` for an intended change).

**Not done yet - only 241's batch 5 (this task, 240, is DONE at 4/4 cities: Denver,
St. Paul, Minneapolis, Cleveland, all staged above):** the remaining five cities of the
25 total go to **241** (batch 5: the final five; its own module `fit/src_us_birdseye_batch5.py` copies THIS one, its staging files
`*_us_birdseye_batch5.jsonl`, lead doc, test and golden; it reads THIS task's
`extras_us_birdseye_batch4.jsonl` as the forward no-op becomes a real read - a QID can never sit
on two sites). The 236b lead-doc candidate order after New Orleans (iteration 181) runs
"...Kansas City, Omaha, St. Paul/Minneapolis, Indianapolis, Columbus, Memphis, New Orleans, ..." -
so after this task's four the next candidates to 241 are **Omaha (skipped in 236b with no recorded
drop reason - re-run its pool search and record the verdict), Indianapolis, Columbus, Memphis**,
then whatever the collection's search order adds to reach five. **236c** consolidates every
staging set into the canonical data and checks the 25 total (16 + 4 + 5, or a recorded shortfall).
**Do NOT write the canonical files - that is 236c; do NOT re-stage the nine cities in 236b or
241's doc.**
