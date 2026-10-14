Status: open
# 236b: US bird's-eye and panoramic city views (1847-1929)
Depends on: none
Touches: fit/src_us_birdseye.py, data/catalog/extras_us_birdseye.jsonl, data/commons/files_us_birdseye.jsonl, data/commons/classified_us_birdseye.jsonl, docs/lead_us_birdseye.md, tests/test_src_us_birdseye.py, tests/golden/src_us_birdseye_sample.json

## Goal
Subtask of 236. GOAL.md point 5: artists' aerial and bird's-eye views count as much as surveys. The Library
of Congress "Panoramic Maps" collection (about 1,500 US bird's-eye views, 1847-1929, public domain; many
mirrored on Wikimedia Commons) is the US equivalent of Braun & Hogenberg. Stage views of the owner's four
cities first (New York, Washington DC, San Francisco, Nashville), then more US cities, in this task's own
staging files, the way 213 staged Civitates.

## Acceptance criteria
- [x] Verified before use (docs/lead_us_birdseye.md): the collection's location and licence, how files are
      fetched (Commons category or loc.gov IIIF), per staged view its date, artist/publisher and resolution;
      unusable ones listed with the reason.
- [x] fit/src_us_birdseye.py holds the hand-checked file -> QID table (every QID verified against label,
      P625, enwiki). Views of a city that 236a also stages use the SAME site id - agree it through the
      catalog slug rule (catalog.slug from QID + name) and record the shared ids in the lead doc; never two
      sites for one QID.
- [x] Staged rows in this task's files only: extras_us_birdseye.jsonl (only for cities not already in the
      catalog and not staged by 236a - check data/catalog/extras_us_cities.jsonl on main before adding one;
      region "United States", kind "town", aerial_ok true), files_us_birdseye.jsonl (files.jsonl shape +
      200 evidence field), classified_us_birdseye.jsonl ("view", by hand).
- [ ] fit/evidence.py check passes offline on every staged row; the four owner-named cities each have at
      least one view staged or the lead doc says why not; at least 25 cities staged in total.
- [x] Test (no network): the staged files join, the evidence check passes, a golden sample of rows.

## Notes
- Bird's-eye views are oblique: the fit is harder than for a plan. Prefer views drawn near-vertical; record
  the view's apparent angle on the row's note so 236c/the matcher can order them.
- Templates: fit/src_artists.py + docs/lead_artists.md (Civitates).
- Do NOT write the canonical files - that is 236c.

## Hand-over

(2026-10-14, iteration 185, agent a) **Step 0 confirmed done by the driver** (f206b2f swept 184's
uncommitted batch-2 work; `git status` was clean at session start; staged files = 10 site rows / 21
file rows / 21 classified rows, golden = 21 pins). **This session finished all verification for work
A (the batch-2 lead doc); the doc itself is NOT written yet.** I (1) re-ran --verify live: 14 QIDs
all clean, exit 0, transcript at /tmp/aw236b_verify_185.txt (86 lines, may be wiped - re-run
`.venv/bin/python fit/src_us_birdseye.py --verify`); (2) re-ran --check offline: exit 0, 21/21 PASS,
no join problems, /tmp/aw236b_check_185.txt (re-run `.venv/bin/python fit/src_us_birdseye.py
--check`); (3) **eyeballed and CONFIRMED every same-sheet claim in the batch-2 module comments**
(thumbs in /tmp/aw236b_b2_thumbs/ incl. 4 fresh downloads this session, see below); (4) pulled exact
pool metadata for every drop-list item from /tmp/aw236b_b2.json. The full pool JSON, cands file,
both transcripts and all 32 thumbs survived on disk.

### What to do next (one session, in order)

1. **Edit docs/lead_us_birdseye.md** (currently still at the batch-1 state; the module comments are
   the source of truth and everything below is verified):
   a. **Replace the "QID verification" section** (starts "## QID verification (re-checked
   2026-10-14, ..." ~line 69): new intro - 14 QIDs re-checked at the batch-2 close-out; **NO P625
   flag fired on any of the fourteen** (Q62's two P625s are 2.0-2.4 km from its refined table point;
   Q23197's is 721 m NE; the ten new-city points ARE the P625s, dist 0); **two search traps**
   (Barnard-Castle class, the 236a Q60 note): Pittsburgh -> Q235034 University of Pittsburgh
   (~4.7 km west) and **Chicago -> Q131252 University of Chicago** (~10.5 km south) - both within the
   50 km flag, so not flagged, but record --live would store the university's point; staged rows
   hand-record the city P625s (dist 0); Baltimore P131 = two values (hence "Baltimore City,
   Maryland"); **St. Louis P131 = ['Missouri'] only** (independent city, hence "St. Louis City,
   Missouri"); **Milwaukee P131 = three counties** (Milwaukee/Washington/Waukesha - the point sits
   in Milwaukee County). Then the verbatim 14-QID transcript (sorted: Q100, Q12439, Q1297, Q1342,
   Q1345, Q23197, Q37836, Q38022, Q43196, Q43668, Q5092, Q60, Q61, Q62) from /tmp/aw236b_verify_185.txt.
   b. **Insert five city sections** between the Cincinnati section and "## Staging and checks", in
   the batch-1 style (**STAGED** bullet: file / year / artist / publisher / dims / PD / LC Panoramic
   no. / angle + same-sheet scans eyeballed this session; **DROP (with reasons)** grouped per city;
   Chicago gets the name-search-trap paragraph like Pittsburgh's). Facts to write:
   - **Louisville** (`louisville-q43668`, point = verified P625; 1 view staged): STAGED
     `File:Birds-eye view of Louisville from the river front and Southern Exposition, 1883. LOC
     75693235.jpg` - 1883, W. F. Clarke, M. P. Levyau & Co., 10864x6928, PD (LC Panoramic 237).
     Two-panel sheet drawn from the river front (Kentucky side): top = the 1883 International
     Exposition of Agriculture, Manufactures and Implements hall (ornament panels + "PUBLIC
     BUILDINGS" index); bottom = the steep near-vertical whole-city view (Ohio + bridges foreground,
     grid dense and legible, "MAP OF LOUISVILLE AND ITS ENVIRONS 1883" inset bottom-right); spans the
     whole city beyond the 2000 m town box -> likely review item (the 236a NY-1811 / DC-ring
     precedent). Same sheet: the .tif twin (10864x6928) + `File:Birdseye-southernexpo.jpg`
     (10757x6905, different copy) - eyeballed 185: identical title block "BIRDS-EYE VIEW OF
     LOUISVILLE FROM THE RIVER FRONT AND SOUTHERN EXPOSITION, 1883. DEDICATED BY THE PUBLISHERS TO
     THE LOUISVILLE BOARD OF TRADE AND MANUFACTURING INDUSTRIES.", identical panels/inset. DROP:
     the 1876 sheet - `File:Bird's eye view of Louisville, Kentucky 1876. LOC 73693416.jpg`
     (7890x5808, A. Ruger, Charles Shober & Co. / Chicago Litho., LC Panoramic 236) + .tif + the
     987x726 copy - **a different, shallower oblique from the Kentucky side** (eyeballed: Ohio +
     bridge foreground, city across the river, printed index of churches / public buildings) - one
     view per city, the steeper 1883 staged. `File:Birds eye view of Louisville, Kentucky
     LCCN2007662142.tif` (1910, 4096x3281) - later sheet, low-res scan. `File:US-KY(1891) p287
     LOUISVILLE, BIRD'S-EYE VIEW.jpg` (1836x1089) - book plate, too small. The 1861 Union-envelope
     print (LCCN2016648172 .jpg/.tif, 1536x860) - small envelope pictorial. Search noise: Audubon
     plates / "Japanese White Eye" photos / book pages / the L&N tourist sheet / the R&D railway
     sheet / the 1861 balloon "War Map of the Middle States" - not Louisville city views.
   - **St. Louis** (`st-louis-q38022`, point = verified P625; 1 view staged): STAGED
     `File:Bird's-Eye View of St. Louis, MO. (full view).jpg` - 1858, James T. Palmatary, 14437x7800,
     PD. **The steepest (near-vertical) and oldest view staged for the city**: drawn from the high
     ground east of the Mississippi ("BIRD'S EYE VIEW OF SAINT LOUIS, MO." banner), the levee and a
     whole steamboat fleet in the foreground, the grid legible from the downtown levee to the far
     suburbs; spans well beyond the 2000 m town box -> likely review item. The **seven "(...
     detail).jpg" tiles** (upper left 14401x11289, upper right 15156x11808, lower left 14150x11635,
     upper-right-center 14944x11591, lower-right-center 15149x11592, lower-left-center 15149x11592,
     upper-left-center 15174x11159; the "Saint Louis"-titled one fails keep() on its title) are
     **high-resolution crops of the same sheet** (eyeballed 185: the upper-left tile's street labels
     40th-44th / Chestnut / Main / Olive / Delaware / Walnut / Locust match the full view's northwest
     district) - one row per sheet, the full-view scan staged. DROP: the 1876 **railway sheet**
     (`File:Birds eye view of St. Louis - showing the new line of the St. Louis, Kansas City &
     Northern Ry. running into the Union Depot. LOC 82695092.jpg` 7560x3944, C. K. Lord, Woodward,
     Tiernan & Hale, LC Panoramic 439.1) + .tif + DPLA mirror fe27966c - the KC&N line into the
     Union Depot is the subject (rail viaducts at both ends, two circular insets - East St. Louis
     bridge / Union Depot tunnel), the city the background. "St. Louis in '93" (LOC 75694659,
     11904x7680, Fred Graf, LC Panoramic 441, copyrighted 1892) - a **shallow skyline view from the
     river** (Eads Bridge, population plates 400,552/550,000, Pfea. Graf Litho.) and "St. Louis in
     1895" (LOC 75694661, 12368x8240, Charles Juehne, LC Panoramic 443, steep with an index and the
     Eads Bridge) - different later sheets, one view per city (the 1858 is older and steeper). `File:
     St Louis Birdseye Map 1896.jpg` (10753x6999, Fred Graf) - another later sheet. The 1904 World's
     Fair sheets ("World's Fair, St. Louis, 1904." 7275x5337 Gray Litho. Co. after Charles Graham;
     "Birdseye view of the Palace of Manufactures from the DeForest Wireless Tower..." 5894x4688
     F. J. Koster) - **exposition close-ups**, not the city. The **DPLA mirrors ("No restrictions",
     not marked Public domain)**: the 1858 full view (4ca97211, 14437x7800 = the staged sheet), its
     detail tiles, and four "horizontal hand-colored steel engraving" views (9a6de5ee / 8e729fb1 /
     c143bc6d / f90661ca, the last dated 1852 - a different older engraving). **Photographs / book
     prints** (the HABS-photo precedent): the 1911 Pierce Building view (DPLA a69ad046, Boehl,
     8154x5988), the 1913/1918 Old Courthouse views (DPLA, Persons), the "steamboats docked along
     the levee" print from Edwards' *Great West* (DPLA dd18ff8a, 7009x5414 - a book print), the
     stereograph sets (Continent Stereoscopic ca. 1865/1885, Robert Benecke ca. 1880, the Robert N.
     Dennis collection 1903-04, the NYPL b11707637/b11707638 scans), the NBY postcard (806x522), and
     the 1837 Catlin Mandan Village painting (1400x1153 - not the city, out of range).
   - **Chicago** (`chicago-q1297`, point = verified P625; 1 view staged): STAGED `File:Bird's eye
     view of Chicago, 1892. LOC 75693206.jpg` - 1892, Peter Roy, 9904x5648, PD (LC Panoramic 151).
     **Steep near-vertical whole-city view drawn from the lake**: Lake Michigan in the foreground,
     the grid dense and legible to the horizon, a numbered index at the bottom and a "VIEW OF
     CHICAGO IN 1832" scroll inset bottom-right; spans the whole city beyond the 2000 m town box ->
     likely review item. **`File:Bird's eye view of Chicago, 1893. LOC 97686545.jpg` is the same
     view in colors** (eyeballed 185: identical composition - same lake, grid, 1832 scroll and index;
     railroads in red, parks in green) - one row per view, the larger 1892 sheet staged. **Name-
     search trap** (Barnard-Castle class, the 236a Q60 note): first "Chicago" search hit with
     coordinates is Q131252 University of Chicago (-87.599722, 41.789722, ~10.5 km south) - within
     the 50 km flag, so --verify does not flag it, but record --live would store the university's
     point; the staged row hand-records the city P625 (dist 0); recorded on the Q1297 SITES comment
     and site note. DROP: the 1857 sheets (`File:1857 Bird's Eye View of Chicago - LOC.jpg`
     24928x15136 + `File:1857 Bird's Eye View of Chicago.jpg` 6424x3698; drawn by I. T. Palmatary,
     lith. Christian Inger, published Braunhold & Sonne) - different earlier sheets (one view per
     city, the 1892 is steeper). The 1853 `File:1853 Chicago Bird's Eye view.jpg` (4236x2141,
     unattributed) and the 1871 Harper's Weekly sheet `File:Bird's-eye-view of Chicago as it was
     before the great fire. LOC 74693213.tif` (6276x4698, T. R. Davis, "From Harper's weekly, October
     21, 1871, pages 984-5") - earlier sheets. `File:1874 Birds eye map of Chicago by Currier &
     Ives.jpg` (7161x5134) and `File:1879 Birds eye view of Chicago.jpg` (3713x2453, Louis
     Klinckerfus & Jacob Richter) - different shallower sheets. The 1898 **business-district** sheets
     (`File:1898 Bird's Eye View of Chicago.jpg` 18144x12992 + `File:Bird's-eye-view of the business
     district of Chicago. LOC 75693212.jpg` 18144x12992, Poole Brothers, LC Panoramic 153) -
     downtown-only partial views. `File:All elevated trains in Chicago stop at the Chicago Rock
     Island and Pacific Railway Station, only one on the Loop LOC 84694897.jpg` (1897, 9573x8700,
     Poole Bros.) - a **railway sheet**. `File:Birds-eye view of the elevated railroads and the
     parks and boulevards of Chicago. LOC 2010592719.jpg` (1908, 13134x7286, Willis J. Champion) - a
     **district sheet** (elevated railroads / parks), not the whole city. The 1893 World's Fair
     sheets (exposition close-ups): `File:World's Columbian Exposition, Chicago 1893 (Bird's-eye
     view) LCCN2003670686.jpg`/`.tif` (5781x3912, Popular Graphic Arts), `File:1893 Birds Eye view
     of Chicago Worlds Columbian Exposition.jpg` (11616x8880, Rand McNally), `File:Grand birds-eye
     view of the grounds and buildings of the great Columbian exposition at Chicago, Illinois,
     1892-3 LCCN2001700243.jpg` (1536x968) + `.tif` (10325x6925, Currier & Ives). `File:1912 Birds
     eye view of Chicago.jpg` (7576x4801) - the 1912 Junction Railway / Central Manufacturing
     District sheet. `File:World's pictorial line - birdseye views in the Rocky Mountains reached
     via the Union Pacific... - DPLA - ae90df794c267feb1cafaecccd8c2562.jpg` (1893, 7000x3160) - a
     **regional** sheet. **Photographs** (HABS-photo precedent): the NBY postcard scans (Downtown
     from the Board of Trade, From Harbor, The Loop, Lincoln Park, Grant Park, Michigan Blvd.
     Bridge, Northwestern Depot, Business District / CNW Terminal) and `File:Bird S Eye View Of
     Chicago (117348765).jpeg` (2015, CC BY - a modern photo). Search noise: the 1866-69 Ruger /
     Koch / Chicago-Litho sheets of Jackson (MI), Lansing (MI), Winona (MN), Pella (IA) (the "
     Chicago Lithographing Co." is the publisher, not the city) and the "Graves of Mabel Birdseye
     Crawford..." photo (the Birdseye surname).
   - **Detroit** (`detroit-q12439`, point = verified P625; 1 view staged): STAGED `File:Birds eye
     view-showing about three miles square-of the central portion of the city of Detroit,
     Michigan. LOC 76693077.jpg` - 1889, Calvert Lithographing Co., 6815x4184, PD (LC Panoramic
     342; sheet: "Used through the kindness of the Imperial Life Ins. Co."). **Steep oblique view
     drawn from the Detroit River**: "about three miles square of the central portion of the city",
     the river and its shipping in the foreground, the grid dense and legible to the hills; covers
     the central city beyond the 2000 m town box -> likely review item. **Five further scans of the
     same sheet** (eyeballed 185: identical title block "BIRDS EYE VIEW—SHOWING ABOUT THREE MILES
     SQUARE—OF THE CENTRAL PORTION OF THE CITY OF DETROIT, MICHIGAN.", same composition, the same
     "THE CALVERT CITY OF DETROIT" side label and the same Library-of-Congress stamps): `File:Birds
     eye view showing about three miles square of the central portion of the city of Detroit,
     Michigan LCCN2003666422.jpg` (10657x6108, the hi-res copy) + `.tif` (10657x6108), `File:Bird's
     eye view of Detroit, Michigan, 1889 - . Calvert Lithographing Co..jpg` (6312x4132, Adam Cuerden
     restoration) + `.png` (6312x4132), `File:Map image detroit.jpg` (5999x3676) and the .tif twin of
     the staged LOC item (6815x4184) - one row per sheet, the LOC scan staged. DROP: `File:Detroit
     1908 Hurd-Martin 1907.jpeg` (4810x2717) and `File:Detroit 1818 Hurd-Martin 1906.jpg` (4798x2640)
     - the Hurd-Martin Co.'s **1818-Detroit postcard pairs** (printed 1906-07; each sheet pairs an
     1818 impression with a 1908 view from the same vantage; "Detroit 1818: historically correct in
     every point of detail") - a postcard publisher's pictorial impression, not a surveyed city
     view. Search noise: the NBY/NYPL postcards (Nantasket, Williams, La Junta, Needles, Kansas
     City business district, Toledo, the Boston waterfront - the "Detroit Publishing Company" is the
     publisher, not the city), the 1875 Philadelphia / 1878 San Francisco / 1879 New York sheets
     (published in Detroit), the Put-In-Bay / Helgoland / Charlestown views, the IA book pages.
   - **Milwaukee** (`milwaukee-q37836`, point = verified P625; 1 view staged): STAGED `File:
     Milwaukee, Wis. LOC 76693067.jpg` - 1872, drawn by H. H. Bailey, Milwaukee Lithographing &
     Engraving Co., published by Holzapfel & Eskuche (banner "MILWAUKEE, WIS."), 11952x8416, PD (LC
     Panoramic 1045). **Steep near-vertical whole-city view drawn from the lake**: two-panel sheet
     (the river and mill-dams at the left, Lake Michigan and the city at the right), the grid dense
     and legible, a printed key of 69 landmarks; spans the whole city beyond the 2000 m town box ->
     likely review item. **Two further scans of the same sheet** (eyeballed 185: identical banner,
     composition and key): `File:Milwaukee 1872.jpg` (11952x8416) and `File:Milwaukee birdseye map
     by Bailey (1872). loc call no g4124m-pm010450.jpg` (9999x6650) - one row per sheet, the LOC
     scan staged. DROP: the other whole-city sheets - `File:Milwaukee, Wis. 1879. LOC
     75696716.jpg` (12656x8384, J. J. Stoner, Beck & Pauli, LC Panoramic 1046) and `File:Milwaukee,
     Wis. LOC 75696717.jpg` (8192x4904, Beck & Pauli, LC Panoramic 1047, 1882) - different later
     sheets, one view per city (the 1872 Bailey is the oldest and steepest). `File:Milwaukee
     1858.jpg` (the title says 1858, the sheet says **1854**; David William Moody, chromo by
     Endicott & Co., New York, 12496x8432) - a **shallower 1854 chromo**, a different earlier sheet.
     The **suburb** sheets - `File:Milwaukee 1892.jpg` / `File:Wauwatosa and the western suburbs of
     Milwaukee 1892. LOC 75696728.jpg` (9424x6288, Marr & Richards, LC Panoramic 1065, "Looking
     east from Wauwatosa") and `File:(Bird's-eye view of South Milwaukee) LOC 87690559.jpg`/`.tif`
     (5846x3418, Binner Engraving, 1906) - Wauwatosa / South Milwaukee, not the city. **Photos**
     (HABS-photo precedent): the four W. H. Sherman Insurance-building views (1870/1875, 2737x1572-
     1608 .jpg/.png). `File:1910 Birds Eye View of Elevated Railroads, Parks and Boulevards.jpg`
     (3789x2061, McComber Directory Co.) - a **district sheet** (the elevated railroads), small
     scan. Search noise (Milwaukee as the publisher's city): the Cheyenne / Bayfield / Concord /.
     Jacksonville / Maysville / Lake Geneva / Antigo / Seattle / Provincetown / Montello /
     Whitehall / Saint Boniface / Columbus sheets (litho by Beck & Pauli / Fowler & Bailey / C. H.
     Vogt, Milwaukee), the Ishpeming bpl scan (CC BY), the Bovill postcard (CC BY), the US Cellular
     Arena photo, the IA book pages.
   c. **Update "## Staging and checks (2026-10-14)"**: "All **fourteen** cities staged so far...: **
     21 views** total (11 for the four owner-named cities - NYC 3, DC 3, SF 4, Nashville 1 - plus
     one for each of the **ten batch-1 and batch-2 cities**)...; the **ten** site rows are in
     `data/catalog/extras_us_birdseye.jsonl`"; replace the 16-line transcript with the fresh 21-
     line one (verbatim from /tmp/aw236b_check_185.txt, ends "evidence: 21 rows, 21 pass, 0 fail, 0
     no-tie", exit 0, no join problems); "the golden sample ... pins the **21** rows"; "**Not done
     yet (next sessions):** the 25-cities box - **11 more US cities** (25 total, **14 done**)... The
     next candidates (in order): **Kansas City, New Orleans, Denver, St. Paul, Minneapolis,
     Cleveland**, ..." (keep the rest of the paragraph).
2. **Commit**: `git add docs/lead_us_birdseye.md tasks/236b-us-birdseye.md DECISIONS.md && git commit
   -m "236b: batch 2 complete - lead doc: 14-QID verify transcript, five city sections (STAGED/
   DROP), 21-view staging section"`. (Only if the full suite is NOT run this session - if it is,
   carry the five docs/site_flow/307d_*.png with the standing 306g-style disclosure, like 184's
   commit.)
3. **Append the DECISIONS.md entry** for this session (the batch-2 lead-doc close-out: verify clean
   / check 21/21 / eyeballs confirmed / doc written).
4. **Then batch 3** (next sessions, per the playbook in the 184 entry): Kansas City first, then New
   Orleans, Denver, St. Paul, Minneapolis, Cleveland, ... (6-7 batches to reach 25 cities).

### State of the files (post-185, all committed - tree clean)

- fit/src_us_birdseye.py: 14 SITES / 21 SOURCES (unchanged this session; its comments remain the
  source of truth - all batch-2 same-sheet claims now eyeball-verified by 185).
- data/catalog/extras_us_birdseye.jsonl: 10 site rows; files_/classified_us_birdseye.jsonl: 21 rows
  each; tests/golden/src_us_birdseye_sample.json: the 21-row pin; tests/test_src_us_birdseye.py: 5/5
  green (batch-2 tables extended in 184).
- docs/lead_us_birdseye.md: **STILL at the batch-1 state** (9-QID transcript, five batch-1 city
  sections, 16-view Staging section) - the batch-2 work above is NOT written yet.
- Transcripts / research (may be wiped; re-run / re-download to regenerate): /tmp/aw236b_verify_185
  .txt (14-QID --verify, exit 0), /tmp/aw236b_check_185.txt (21-line --check, exit 0),
  /tmp/aw236b_b2.py (the pool builder - regenerates /tmp/aw236b_b2.json), /tmp/aw236b_b2.json (the
  full 5-city pool with per-file metadata - needed for the DROP lists), /tmp/aw236b_b2_cands.json
  (the 22 candidates), /tmp/aw236b_b2_thumbs/ (28 original thumbs + 4 downloads by 185: X_Bird's_eye
  _view_of_Detroit... (Cuerden), X_Map_image_detroit.jpg.jpg, X_Milwaukee,_Wis._LOC_76693067.jpg
  .jpg, X_Bird's-Eye_View_of_St._Louis,_Mo._(upper.jpg). Thumb URLs come from the Commons API
  imageinfo thumburl (iiurlwidth=1280) via .venv's commons.get - commons.info has no 'thumb' key).

### Rules (unchanged)

NEVER write the canonical files (data/commons/files.jsonl etc. - that is 236c); NEVER touch 236a's
extras_us_cities.jsonl (read-only; the module's _shared_site enforces it); run live commands under
.venv/bin/python (system python3 has no numpy; the module top stays stdlib-only); batch size ~5
cities/session to fit the context limit; the golden sample is the contract (--golden only for an
intended change); the full suite rewrites the five docs/site_flow/307d_*.png every run - if the
bytes change, carry them in the commit with the 306g-style disclosure (the 184 commit did).

### State of the files (post-184)

- fit/src_us_birdseye.py: 14 SITES (batch 1: boston-q100, philadelphia-q1345, baltimore-q5092,
  pittsburgh-q1342, cincinnati-q43196; batch 2: louisville-q43668, st-louis-q38022, chicago-q1297,
  detroit-q12439, milwaukee-q37836) and 21 SOURCES. Unchanged this session (183's edit was committed
  by the driver in 3d367d5). Its comments carry the batch-2 picks, the same-sheet scans and the drop
  reasons - the source of truth for the lead doc.
- data/catalog/extras_us_birdseye.jsonl: 10 site rows (+5 this session); data/commons/
  files_us_birdseye.jsonl and classified_us_birdseye.jsonl: 21 rows each (+5 this session). All new
  rows verified (the 184 DECISIONS entry has the details).
- tests/golden/src_us_birdseye_sample.json: the 21-row pin (regenerated this session - intended).
- tests/test_src_us_birdseye.py: extended for batch 2 this session (SITES/extras/years/points/named
  tables + len(files) 21 + docstrings) - 5/5 green.
- docs/lead_us_birdseye.md: still at the batch-1-complete state (only 183's one-line typo fix since)
  - the batch-2 sections are NOT written. That is work A.
- Transcripts (may be wiped; re-run to regenerate): /tmp/aw236b_verify_184.txt (14 QIDs, all clean),
  /tmp/aw236b_check_184.txt (21-line --check, exit 0), /tmp/aw236b_stage_184.txt, /tmp/aw236b_dry_184
  .txt.
- Batch-2 research (may be wiped; all regenerable): /tmp/aw236b_b2.py (the pool builder: per-city
  Commons file-namespace searches, 6 plain-phrase forms + the St. Louis "Saint Louis bird's eye view"
  form, each + " filetype:bitmap"; commons.info 50/call at 1/s; keep() + 600-char caption gate +
  Public domain + >=4000 px wide), /tmp/aw236b_b2.json (full pool with per-file metadata),
  /tmp/aw236b_b2_cands.json (the 22 good candidates), /tmp/aw236b_b2_thumbs/ (the 1280 px thumbs
  183 eyeballed).

### NEXT (exact, in order)

0. **Commit the uncommitted batch-2 work** (only if the driver has not already swept it - check
   `git status`): the working tree holds data/catalog/extras_us_birdseye.jsonl (+5 site rows),
   data/commons/files_us_birdseye.jsonl and classified_us_birdseye.jsonl (+5 rows each),
   tests/golden/src_us_birdseye_sample.json (the 21-row pin), tests/test_src_us_birdseye.py (the
   batch-2 table extension), this task file, DECISIONS.md, and the five regenerated
   docs/site_flow/307d_*.png (the 307d screenshot test rewrites them every full-suite run; the
   bytes vary between runs). Commit them together: "236b: batch 2 landed - staged Louisville, St.
   Louis, Chicago, Detroit, Milwaukee (10 site rows / 21 file rows), 14-QID verify clean, golden +
   tests extended, suite 177/1/0 - the 307d pngs are this session's test output, not 236b work".
   Then step A.
A. **Batch-2 lead doc** (box 1's per-view coverage for the five new views; all in
   docs/lead_us_birdseye.md):
   1. Replace the "QID verification" section (line ~69, currently the 9-QID transcript) with a fresh
      14-QID transcript: re-run `.venv/bin/python fit/src_us_birdseye.py --verify` (184's run =
      /tmp/aw236b_verify_184.txt: all clean, zero flags; the two in-flag name-search traps are
      Pittsburgh -> Q235034 and Chicago -> Q131252; St. Louis P131 = Missouri only; Milwaukee P131 =
      three counties).
   2. Insert five city sections after the Cincinnati section and before "Staging and checks"
      (Louisville, St. Louis, Chicago, Detroit, Milwaukee), in the batch-1 style: the STAGED view
      (date / artist / publisher / resolution / apparent angle + the same-sheet scans from the module
      comments) plus the DROP list with reasons per non-staged candidate - derive each reason from
      the pool metadata (/tmp/aw236b_b2.json: license, dims, desc) and 183's eyeballs (the thumbs are
      still on disk in /tmp/aw236b_b2_thumbs/; if wiped, re-download the 1280 px thumbs and re-
      eyeball - the pool builder regenerates everything). Known from the module comments: St. Louis =
      seven "(... detail)" tiles + DPLA mirrors (No restrictions, not PD) + two book-print
      photographs; Chicago = the 1893 chromolithograph (the same view in colors); Detroit = four
      further scans of the staged sheet; Louisville = the .tif twin + the 1876 sheet; Milwaukee =
      further 1872 scans + the 1879/1858/1882 views.
   3. Update "Staging and checks": 21 views (11 owner + 5 batch 1 + 5 batch 2), the 10 site rows in
      extras_us_birdseye.jsonl, a fresh 21-line --check transcript (re-run --check), and "not done
      yet: 11 more cities (25 total, 14 done)".
   4. Commit: "236b: batch 2 complete - lead doc: 14-QID verify transcript, five city sections
      (STAGED/DROP), 21-view staging section".
B. **Batch 3 (~5 cities; ~6 remain after it - box 4 ticks at >=25 cities total, then Status: done)**:
   candidates: Kansas City first, then New Orleans, Denver, St. Paul, Minneapolis, Cleveland, ...
   (the LOC Panoramic collection, 1847-1929; a city with no usable view gets a lead-doc note and the
   next candidate). Same per-city procedure as batches 1/2 (181's playbook, restated in the 184
   DECISIONS entry): (1) QID check against sites.jsonl + extras.jsonl + extras_us_cities.jsonl +
   web/data/sites.json (never two sites for one QID); (2) pool search (plain-phrase forms +
   " filetype:bitmap", commons.info 50/call at 1/s, keep() + gate + PD + >=4000 px); (3) pick the
   ONE steepest view (near-vertical, grid legible, PD, >= ~4000 px wide; DROP pictorial/regional/
   fort-close-up/photo/street-car-map/railway-sheet; eyeball 1280 px thumbs to dedupe same-sheet
   scans, one row per sheet, keep the LOC/largest scan); (4) verify the QID live with --verify
   (watch name-search traps - Chicago's is the in-table example); (5) SITES + SOURCES entries;
   (6) --dry, stage, --check (exit 0); (7) lead-doc section per city + re-run --verify (the
   transcript grows); (8) --golden, then the module tests + the full suite (extend the test tables
   exactly as 184 did).

### Rules (unchanged)

NEVER write the canonical files (data/commons/files.jsonl etc. - that is 236c); NEVER touch 236a's
extras_us_cities.jsonl (read-only; the module's _shared_site enforces it); run live commands under
.venv/bin/python (system python3 has no numpy; the module top stays stdlib-only); batch size ~5
cities/session to fit the context limit; the golden sample is the contract (--golden only for an
intended change); the full suite rewrites the five docs/site_flow/307d_*.png every run - if the
bytes change, carry them in the commit with the 306g-style disclosure (the 184 commit did).
