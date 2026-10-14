Status: open
Depends on: 236b
Touches: fit/src_us_birdseye_batch4.py, data/catalog/extras_us_birdseye_batch4.jsonl, data/commons/files_us_birdseye_batch4.jsonl, data/commons/classified_us_birdseye_batch4.jsonl, docs/lead_us_birdseye_batch4.md, tests/test_src_us_birdseye_batch4.py, tests/golden/src_us_birdseye_batch4_sample.json, docs/site_flow/307d_*.png (R5: restoring suite re-encodes to main's bytes before committing - never content changes)

# 240: US bird's-eye views, batch 4 - Denver, St. Paul, Minneapolis, Cleveland

## Goal
Part of 236 (split out of 236b on 2026-10-14, driver instruction: 236b closed done at 16 cities, and
the remaining cities of the 25-city total go to this task and 241, each with its own module and
staging files so two agents can build in parallel). Stage batch 4 of the Library of Congress
"Panoramic Maps" collection (about 1,500 US bird's-eye views, 1847-1929, public domain; this machine
cannot reach loc.gov, so files are fetched from their Wikimedia Commons mirrors - 236b's route, in
its lead doc): FOUR more US cities, each a new site in this task's own staging files, one best
view per city. The 25-city total spans 236b (16) + 240 (4) + 241 (5); 236c consolidates all the
staging into the canonical data and checks the total.

## Acceptance criteria
- [ ] fit/src_us_birdseye_batch4.py holds the hand-checked file -> QID table for its four cities
      (every QID verified live against Wikidata with the module's --verify BEFORE staging: label,
      every P625 value, P373, P131, enwiki, the first name-search hit with coordinates - what
      record --live would resolve; the machine cannot reach loc.gov, so the files are fetched from
      their Wikimedia Commons mirrors, 236b's route). The module copies fit/src_us_birdseye.py's
      machinery (the verify/stage/check/golden CLI, the 200 caption_coords evidence field, the
      Zwolle date-swap rule, the never-two-sites-for-one-QID cross-check - extended to 236a's and
      236b's staging files); its docstring names fit/src_us_birdseye.py as the template it keeps in
      sync with.
- [ ] Staged rows in this task's files ONLY: extras_us_birdseye_batch4.jsonl (the new cities' site
      rows - region "United States", kind "town", aerial_ok true, the point = the city's verified
      P625 or a recorded refinement, the note recording the staged view's apparent angle so 236c /
      the matcher can order the oblique views); files_us_birdseye_batch4.jsonl (files.jsonl shape +
      the 200 evidence field); classified_us_birdseye_batch4.jsonl (p_birdseye 1.0, by "hand"). One
      row per city = the steepest (near-vertical), best-scanned whole-city view of the collection
      for that city (Public domain, >= 4000 px wide, the caption names the city); every pool item
      not staged is listed with its reason in the lead doc.
- [ ] fit/evidence.py check passes offline on every staged row (--check exit 0, every row PASS
      caption_coords, no join problems); no staged site id or QID collides with an existing site
      (the catalog, 236a's extras_us_cities.jsonl, 236b's extras_us_birdseye.jsonl, 241's file when
      it exists, web/data/sites.json) - never two sites for one QID (the catalog slug rule:
      id = slug(name) + "-" + qid-lower).
- [ ] Test (no network, the socket-blocking fixture per 236b's test file): the staged files join,
      the evidence check passes, a golden sample tests/golden/src_us_birdseye_batch4_sample.json
      pins the staged rows (regenerated only via the module's --golden for an intended change); a
      full-suite run = baseline (restore the re-encoded docs/site_flow/307d_*.png to main's bytes
      before committing - the PITFALLS test_owner_check rule).
- [x] Denver is staged as researched (Q16554; the 1908 Birdseye View Publishing Co. sheet,
      `File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg`, looking south from the
      Twenty-Third Street Viaduct): the Notes below carry the full research record; the first
      session re-verifies it live (--verify) and, if the pick is gone from Commons or no longer PD,
      takes the next-best pool candidate and records the swap in the lead doc.

## Notes (operational facts carried from the 236b split, 2026-10-14 iteration 195)

**Read first (all in 236b, done - on main):** docs/lead_us_birdseye.md (the Fetch route section:
the Commons file-namespace search, the six plain-phrase forms + " filetype:bitmap", the
keep/caption/Public-domain/width gates, the Zwolle date-swap rule, the evidence-field contract,
the STAGED/DROP section format, the QID-verification transcript format, the Staging section with
the verbatim --check transcript format) and fit/src_us_birdseye.py (the template module: SITES /
SHARED_SITES / SOURCES tables + verify_qids / stage / check_staged / golden + the CLI). COPY that
module to fit/src_us_birdseye_batch4.py and change only: the staging-file paths (the four
*_us_birdseye_batch4.* paths in the Touches line above), the module name inside the rows' "by" /
"source" fields, and known_sites() to ALSO read data/catalog/extras_us_birdseye.jsonl (236b) and
data/catalog/extras_us_birdseye_batch5.jsonl (241; absent until it runs - _load() tolerates a
missing file) so a QID can never sit on two sites. Do NOT edit fit/src_us_birdseye.py,
fit/evidence.py or any pipeline/ file (read-only for this task; file a task if one of them needs
a change). This module stages no shared (owner-named) cities: SHARED_SITES stays out of the copy.

**One row per city, the steepest, best-scanned whole-city view** (Public domain, >= 4000 px wide,
caption names the city); shallower same-genre sheets and the non-view pool (street-car scenes,
real-estate ads, district close-ups, regional views, photographs, too-small scans, other-city
sheets, licence rejects) are DROPS recorded with reasons in the lead doc (the 236b precedent).
Batch 4's candidate order: **Denver, St. Paul, Minneapolis, Cleveland** (236b's lead-doc order).
This task owes FOUR staged cities, not specifically these four: a city with no usable view gets a
lead-doc note and the next candidate. Before adding any SITES entry, check that no existing site
holds the QID (catalog/sites.jsonl, catalog/extras.jsonl, 236a's and 236b's extras files,
web/data/sites.json) - if one does, tie the row to that site like 236b's shared cities and record
it in the lead doc (never a second site for one QID). St. Paul especially has name-search traps
(there are other St. Pauls - Louisiana, South Carolina - and big institutions in the city; the
Pittsburgh/Chicago university-trap class in 236b's module comments).

**Per-city landing (the proven 189-194 pattern, one city per session pair):** (1) RESEARCH: the
QID (Wikidata: the label - first-guess mislabels are the usual trap class, every P625 value, P373
(a string is the usual US quirk - write the place from the county + state), P131, P17, enwiki,
the name-search trap check; record everything in the SITES comment; MEASURE every distance claim
with fit/evidence.hav_m + geographic dx/dy before writing it) + the pool (the
/tmp/aw236b_b3_dvr.py script is the template: build, dedupe, filter, 1280 px thumbs eyeballed one
by one - artifacts under /tmp, re-verifiable). (2) LANDING: module edit -> --verify (save the
exact output; the lead doc carries it verbatim in the QID section) -> --dry -> stage (live
commons.info re-check) -> --check (save the transcript; the Staging section carries it verbatim)
-> lead-doc section (STAGED bullet with the view's facts + the full DROP list + the QID-facts
paragraph) -> --golden -> test extension (mirror tests/test_src_us_birdseye.py: the no_network
socket-blocking fixture; the PASS-key list; the SITES-id / extras-id / year / point / named
tables; the golden compare) -> module tests -> the FULL suite (restore the 307d pngs first,
below) -> commit. The lead doc's Staging section ends with the Not-done-yet pointer to 241 naming
the next two or three candidates (the 236b precedent).

**Rules (unchanged from 236b):** NEVER write the canonical files (data/catalog/extras.jsonl,
data/commons/files.jsonl, classified.jsonl - that is 236c); NEVER touch 236a's or 236b's files
(read-only; the module's cross-check enforces); live commands under .venv/bin/python (system
python3 has no numpy; the module top stays stdlib-only); the golden sample is the contract
(--golden only for an intended change); tests never bind fixed network ports or write outside the
project and the temp dir; every full-suite run re-encodes up to ten docs/site_flow/307d_*.png -
restore main's bytes before committing (the PITFALLS test_owner_check entry).

**Denver is RESEARCHED (236b iteration 194, agent a; the full DECISIONS entry "236b DECISION:
iteration 194" is archived with 236b - search DECISIONS-archive.md; the /tmp artifacts
/tmp/aw236b_b3_dvr* still exist, re-verify live if wiped):** QID = **Q16554** (label "Denver", the
consolidated city-county and capital of Colorado; the first-guess Q3101 is a PERSON - Patrick
Ricard - caught by the label check). Live facts: P625 = ONE 30 m value (-104.984722, 39.739167)
the central CBD (no refinement needed); P373 = the STRING "Denver, Colorado" (the usual quirk);
P131 = Q1261 Colorado + Q13052701 Denver County (consolidated city-county - hence place "Denver
County, Colorado"); P17 = Q30; enwiki "Denver"; name search: NO trap (the first hit with P625 is
Q16554 itself, dist 0). No existing site holds it (checked 194 in the catalog, extras, 236a's
file and web/data/sites.json). Site id = **denver-q16554** (catalog.slug("Denver") = "denver",
verified). Pool (194): 65 unique / 33 good. **THE PICK: `File:Bird's eye view of Denver, Colorado,
1908. LOC 75693133.jpg`** (19338x13294, PD; page date 1908 = the drawing's year, no swap; artist
"Birdseye View Publishing Co.; Denver Lith. Co."; banner "BIRD'S EYE VIEW OF DENVER, COLORADO,
1908 LOOKING SOUTH FROM THE TWENTY-THIRD STREET VIADUCT" - the steepest near-vertical whole-city
view in the pool, drawn from the north of the city looking south: the dense grid legible to the
southern suburbs, the Front Range along the top of the sheet (the southern horizon), the South
Platte meandering in from the northwest along the sheet's RIGHT side (the sheet faces south, so
west is right - no mirroring), the landmark index across the bottom; the viaduct is ~1.3 km north
of the site's point, measured 194: 23rd-street lat 39.7508 - P625 39.739167 = 0.0116 deg x
110900 m/deg = 1287 m). Same-sheet scans (one row per sheet, the LOC .jpg staged): the 19338x13294
.tif twin + the 9000x6205 DPLA copy (4ac8083cbba722c01cad3388a37a7a0f). **DROPS (the per-item
reasons are in the 194 DECISIONS entry; 16 distinct sheets):** the 1881 Flett (LOC photocopy,
shallower), the 1887 Rocky Mountain News / Mills, the 1882 Platt / Slocum chromo, the 1874 Glover
(the pool's OLDEST whole-city view - its three 1536 px copies are too small), the 1887
Arbor-Day Colfax-avenue street (thumb fetched, NOT yet eyeballed - confirm), the 1895 "Healer"
street-car scene (thumb fetched, NOT yet eyeballed), the 1907 South Broadway real-estate ad, the
1913 Daniels & Fisher tower PHOTOGRAPH, the Clayton School close-up, the Lookout Mountain regional
view, the state-of-Colorado sheet (the title's "1603" is a FALSE year picked up from the DPLA
hash), other-city rejects (Golden, Pueblo, Canon City, Greeley, Gunnison, Leadville, Maysville,
Colorado Springs + Manitou), too-small (Kilburn, CO Denver 1889, the Great Plains book sheets),
the CC BY-SA 1907 sheet, and the 2021 Union Station photo (beyond the 1925 MAX_YEAR).

**St. Paul is RESEARCHED (iteration 162 - the full record is the DECISIONS entry "240 DECISION:
iteration 162" and the hand-over below): QID Q28848, pick = the 1906 Robert M. Saint near-
vertical sheet (LOC 75694650). Minneapolis is RESEARCHED (iteration 165 - the DECISIONS entry
"240 DECISION: iteration 165" and the hand-over below): QID Q36091, pick = the 1885 W. V.
Herancourt / I. Monasch near-vertical sheet (LOC 75694644).** Cleveland: NOT yet researched. Run
the per-city playbook. (The pool search shows which survived the gates; do not trust this note,
verify live.)
## Hand-over
(2026-10-14, iteration 169, agent c - session 10 COMPLETE: CLEVELAND (city 4) RESEARCH done - QID
Q37320 (the "Cleveland, Ohio" search's first hit IS the city: the batch's first clean first-guess;
the memorized Q131855 was a roadster (bicycle), caught by the label check), pool 51 unique / 9
good with every thumb eyeballed, THE PICK = the 1877 A. Ruger / Shober & Carqueville sheet
(`File:Birds eye view of Cleveland, Ohio 1877. LOC 73694507.jpg`, 10704x6544, PD) - the steepest
near-vertical whole-city view in the pool, drawn from a high vantage OVER LAKE ERIE (south of the
city) looking north. NO project file touched this session (research only); branch clean;
docs/site_flow clean vs main. NEXT = session 11: CLEVELAND LANDING.)

**State (verified this session):**
- Staged in the batch4 files (3/3/3 rows): `denver-q16554` (the 1908 Birdseye View Publishing Co.
  sheet), `st-paul-q28848` (the 1906 Robert M. Saint sheet), `minneapolis-q36091` (the 1885 W. V.
  Herancourt / I. Monasch sheet) - unchanged this session. Lead doc docs/lead_us_birdseye_batch4.md:
  three city sections + Staging section (3 views / 3 site rows; the Not-done-yet pointer names only
  CLEVELAND for 240). Golden 3/3/3. batch4 tests 5/5 (re-run this session, 2.34 s, offline). Module
  fit/src_us_birdseye_batch4.py: SITES at line 79 (3 QIDs), known_sites() at line 276 (SITES_JSONL +
  EXTRAS + 236a's + 236b's + 241's absent batch5 + web sites).
- `git diff main --stat -- docs/site_flow/` = clean (the driver's 26aca9f merge brought main's
  bytes; no R5 restore was needed this session). The 241 batch5 file is still absent (241 not
  started) - the module's forward read tolerates it.

**Cleveland research record (the full detail: DECISIONS entry "240 DECISION: iteration 169"):**
- **QID = Q37320** (live, .venv/bin/python /tmp/aw240_cle_qid.py; transcripts
  /tmp/aw240_cle_qid_169.txt + _qid2_169.txt): label "Cleveland"; P625 = ONE 30 m value
  (-81.69472222222223, 41.49916666666667) the central CBD (no refinement needed); P373 = the STRING
  "Cleveland, Ohio" (the usual US quirk); P131 = Q251267 Cuyahoga County (the only one) -> place
  "Cuyahoga County, Ohio"; P17 = Q30; enwiki "Cleveland". The "Cleveland, Ohio" name search's first
  hit is the city itself (clean first-guess - first of the batch: Denver Q3101 a person, St. Paul
  Q16842 a person, Minneapolis Q3094 a Romanian monastery, Cleveland clean); the memorized Q131855
  is a ROADSTER (bicycle, no P625) - a memory error caught by the label check. Name search
  "Cleveland" (limit 20): NO first-hit trap - the first hit with P625 is Q37320 itself (0 km, the
  Denver/Minneapolis pattern); the in-city institution traps rank behind it (Cleveland State
  University 1.7 km, Cleveland Clinic 6.1, Cleveland Museum of Art 7.0, Cleveland Guardians 0.9,
  Cleveland Browns 0.9); other states (TN 756.0, GA 788.6, Quebec 901.4, MS 1172.0, OK 1400.0) and
  Tasmania 15993.8. No existing site holds the QID (the 169 scan: catalog sites/extras, 236a's and
  236b's extras, 241's absent file, this task's own file, web/data/sites.json - none). Site id =
  **cleveland-q37320** (catalog.slug("Cleveland") = "cleveland", verified live).
- **Pool** (live: /tmp/aw240_cle_pool.py + .json; transcript /tmp/aw240_cle_pool_169.log): 51
  unique / 9 good; all 9 thumbs (1280 px) eyeballed one by one (/tmp/aw240_cle_thumbs/). Three
  distinct Cleveland (Ohio) sheets: the 1853 John W. Hill sheet (11831x8413, DPLA - a mid-steepness
  oblique drawn from Ohio City across the Cuyahoga; the pool's OLDEST whole-city view), **THE 1877
  sheet (the pick, below)**, the 1887 C.H. Vogt & Son sheet (6632x5125/5128, two scans - shallower,
  bigger sky band; its banner prints only "CLEVELAND, OHIO." - the year 1887 comes from the LC
  record alone).
- **THE PICK: `File:Birds eye view of Cleveland, Ohio 1877. LOC 73694507.jpg`** (10704x6544,
  Public domain; page date 1877 = the drawing's year - the sheet's own copyright line - no Zwolle
  swap; LC Panoramic maps (2nd ed.), 687.2): THE steepest (near-vertical) whole-city view in the
  pool - verified on the 19.4 MB original (crops /tmp/aw240_cle_77_* + /tmp/aw240_c77_*): the
  rotated street grid legible across the WHOLE frame (lakefront to the farmland horizon). Banner
  "BIRDS EYE VIEW OF CLEVELAND / OHIO 1877" (three lines, no apostrophe) bottom-centre; "A. RUGER,
  ARTIST" at the image's lower-left corner; "LITH. BY SHOBER & CARQÉVILLE CHICAGO" lower left (the
  accent on the E - the row label keeps the ASCII "Carqueville"); "ENTERED ACCORDING TO ACT OF
  CONGRESS BY J. J. STONER MADISON WIS." lower right; the LC stamp "Division of Maps / FEB 28 1941 /
  Library of Congress" + the handwritten call number "G4084 .C5A3 1877 .R8 / Rug 157". Orientation
  (measured on the original): drawn from a high vantage OVER LAKE ERIE (south of the city; the
  lake with its sailing/steam traffic fills the bottom band) looking NORTH - sheet up = north,
  confirmed three ways (the Cuyahoga enters from the north, the Chippewa to its east, the lake to
  the south - no mirroring possible): the Cuyahoga meanders in from the upper centre (the north)
  to its MOUTH at the sheet's centre-right, crossed by the multi-arch Washington Avenue viaduct
  (label "WASHINGTON" on the sheet) and a truss bridge, the "UNION PASSANGER DOCK" (spelled so) on
  the WEST side of the mouth; the dense downtown core (Public Square with its fountain, on the
  bluff above the lakefront - the site's P625 point sits right at it) at the sheet's centre just
  left of the mouth; the Woodland / Catholic / Cleveland cemeteries and the factory stacks on the
  farmland horizon at the top; the "SUPERIOR" street label lower-left; the "CHIPPEWA RIVER" meander
  upper-right. Twins (one row per sheet, the LOC .jpg staged): the same-scan .tif and the
  DPLA-family "Cleveland 1877.jpg" (the same 10704x6544 sheet, a wider index crop).
- **DROPS (all 42 non-good + the 5 good non-picks, grouped; per-item detail in the 169 DECISIONS
  entry):** the 1884 Molitor Mississippi River sheet (the regional three-band view; "Cleveland"
  only as the publisher's place - it passed the caption gate via the desc, but it is not a city
  view); the 1923 Fairchild "airplane view of the heart of the east end" (a rotogravure of a 1923
  airplane photo of the Euclid/Cedar/E 105th neighbourhood - a district close-up, not the whole
  city); the 1890 Lucien Burleigh "Cleveland, N.Y." sheet (the village on Oneida Lake, Onondaga
  County - a DIFFERENT Cleveland: the same-city-name trap class); the 1853 Hill and the 1887 Vogt &
  Son sheets (shallower than the pick); the DPLA district close-ups (Municipal Stadium, City
  Hospital, Rockefeller Park x2, the Art Museum / Wade Park, the Edgewater bathing beach, the Union
  Terminal aeroplane view - all "No restrictions" and < 4000 px); the industrial-ad scans (Adams
  Paint 2015, Dixie Foundry 1930 - keep() fails); the other-city scans (Canton Ohio 1913 - the
  caption gate rejects it correctly; Hancock and Houghton Michigan - CC BY; Walrus Island - caption
  gate + 1821 px); the false search hits (the Israël Silvestre palace views, the Mackinac book
  sheet, the eight 1864 Lowes letters).

**/tmp (still alive at session end; wiper-prone):** /tmp/aw240_cle_qid.py + the two QID transcripts;
/tmp/aw240_cle_pool.py + /tmp/aw240_cle_pool.json + _169.log; /tmp/aw240_cle_thumbs.py + _169.log +
/tmp/aw240_cle_thumbs/ (9 jpgs); /tmp/aw240_cle_77_orig.jpg (19.4 MB) + the _77_{full,qnw,qne,qsw,
qse,strip,banner} crops; /tmp/aw240_c77_{title,copyr,banner_left,rivers,mouth,dtown}.jpg;
/tmp/aw240_cle_87_orig.jpg (6.8 MB) + the _87_* crops. The mpls/dvr research sets from sessions
1-9 are still present too. Rebuild: clone the mpls scripts (QID: sys.path + the QID/TERM constants;
pool: CITIES=["Cleveland"]; thumbs: the key + the paths).

**NEXT (session 11) - CLEVELAND LANDING, in this exact order (all live commands under
.venv/bin/python; the proven entry-167 pattern, adapted for Cleveland):**
1. **Module edit** (the ONLY code change, fit/src_us_birdseye_batch4.py): (a) the SITES "Q37320"
   entry with the full comment block (in the Denver/Minneapolis comment style: first-guess - the
   memorized Q131855 a roadster (bicycle), caught by the label check, while the "Cleveland, Ohio"
   search's first hit is the city itself; P625 one 30 m value; P373 the string; P131 Cuyahoga only
   -> place; P17 Q30; enwiki; NO first-hit trap (first P625 hit = the city, 0 km) with the in-city
   institution list; no existing site holds the QID (the 169 scan); slug verified) +
   id="cleveland-q37320", name="Cleveland", named="Cleveland", lon=-81.69472222222223,
   lat=41.49916666666667, place="Cuyahoga County, Ohio", region="United States", kind="town",
   wikipedia="https://en.wikipedia.org/wiki/Cleveland", note = the aerial-photograph-ground
   boilerplate + "the street grid, the Cuyahoga and the Lake Erie shoreline carry the fit; the
   1877 staged sheet is the steepest (near-vertical) whole-city view in the pool, drawn from a high
   vantage over Lake Erie (south of the city) looking north - the Cuyahoga meanders in from the
   upper centre to its mouth centre-right (the Washington Avenue arch viaduct and a truss bridge
   over it, the Union Passenger Dock west of the mouth), the dense downtown core (Public Square
   with its fountain) at the sheet's centre just left of the mouth, the rotated grid legible to the
   farmland horizon, the lake with its ship traffic along the bottom - spanning the whole city
   beyond the 2000 m town box, so its fit is likely to end a review item (the 236a NY-1811 /
   DC-ring precedent)". (b) the CLEVELAND_1877 row-list: ONE row ("File:Birds eye view of
   Cleveland, Ohio 1877. LOC 73694507.jpg", "Q37320", "Cleveland", dict()) - NO date= entry (page
   date 1877 = drawing year, no Zwolle swap) - with the sheet-facts comment (banner, artist,
   lithographer, copyright line, LC call number, the twins). (c) the SOURCES entry
   "cleveland_1877": dict(rows=CLEVELAND_1877, p="birdseye",
   label="{name}, the A. Ruger / Shober & Carqueville bird's-eye view (1877)") - the label stays
   ASCII (the sheet's accented "CARQÉVILLE" goes in the comment and the lead doc only). (d)
   docstring + SITES-header updates (the "Cleveland follows in candidate order" lines become
   "Cleveland (the 1877 A. Ruger / Shober & Carqueville sheet)"; four cities). The module itself
   may carry non-ASCII in comments (it already does - Căldărușani); only the TEST FILE must stay
   pure ASCII.
2. **--verify** (4 QIDs; save the transcript verbatim to /tmp/aw240_verify_169.txt for the lead
   doc; expect: Q16554 no trap; Q28848 the expected Q17 São Paulo TRAP line (8953 km); Q36091 no
   trap; Q37320 no trap - the first hit with P625 is the city itself).
3. **--dry** (expect "staged: 1 new sites, 1 new pictures" with cleveland-q37320 -81.69472222222223
   41.49916666666667 Cuyahoga County, Ohio).
4. **stage** (live commons.info re-check; if the pick vanished or is no longer PD, take the next-best
   pool candidate - the 1887 Vogt & Son sheet (File:Cleveland, Ohio. LOC 75694918.jpg) - and record
   the swap in the lead doc + the SITES comment).
5. **--check** (expect 4/4 PASS caption_coords, no join problems; save the transcript and append
   it to the Staging section).
6. **Lead doc** (docs/lead_us_birdseye_batch4.md): the Cleveland section (in the format of the
   Denver/St. Paul/Minneapolis sections: the STAGED bullet with the view's facts + the orientation
   measurement; the full DROP list - all 47 pool rows, grouped like Minneapolis's; the QID-facts
   paragraph; the --verify transcript verbatim in the QID section); the Staging section to
   **4 views / 4 site rows** (4 PASS lines; "4 rows, 4 pass, 0 fail, 0 no-tie"); the Not-done-yet
   pointer rewritten: 240 is DONE (4/4), the remaining cities go to 241 (batch 5, the final five:
   Omaha (skipped in 236b with no recorded drop reason - re-run its pool search and record the
   verdict), Indianapolis, Columbus, Memphis, then whatever the collection's search order adds to
   reach five - confirm against the live search order when writing it).
7. **--golden** (4/4/4).
8. **Test extension** (tests/test_src_us_birdseye_batch4.py, mirroring the entry-163/167
   substitution pattern A-E: the module-header docstring reference; the --check PASS-key list +
   "cleveland-q37320|File:Birds eye view of Cleveland, Ohio 1877. LOC 73694507.jpg"; the
   test_sites_table_and_staged_rows docstring + SITES-id dict; the years/points/named_by_qid
   dicts; the Cleveland 1877 date assertion). Keep the file PURE ASCII (zero non-ASCII bytes;
   verify byte-by-byte; ast.parse OK).
9. **batch4 tests** (expect 5/5) -> **the FULL suite** (~9 min; start it ONLY after ALL edits per
   R6, then `git checkout main -- docs/site_flow/` (R5), then commit "240: Cleveland landed (batch
   4 city 4) - the 1877 A. Ruger / Shober & Carqueville sheet". Baseline 182P/1S/0F at 164 (main
   HEAD 8678c8a) - main has moved since (238's d89e329 etc. now in this branch via 26aca9f): if
   anything fails, diff the FAILING SET against the baseline, not the number; the 307d re-encode
   jitter is handled by the R5 restore.

**CLOSE (session 12, after Cleveland lands):** the full-suite tail = the baseline (diff the
failing set if main moved); --check ends all PASS, no join problems; the four staged ids/QIDs
collide with nothing (the known_sites() guard + the test); tick acceptance boxes 1-4 (each after
its test passes); the lead doc's Staging section final (4 views / 4 site rows; the Not-done-yet
names only 241); box 5 (Denver, researched) stays ticked (re-verified live by the 167 --verify
run and the 169 QID research). Status: done.

**Rules that bite (unchanged from the task Notes):** never write the canonical files (236c);
236a's and 236b's files are read-only (the module's cross-checks enforce); live commands under
.venv/bin/python (the module top stays stdlib-only; /tmp scripts repoint sys.path at this
checkout); the golden regenerates only via --golden; tests never bind fixed network ports or write
outside the project and the temp dir; every full-suite run re-encodes up to ten
docs/site_flow/307d_*.png - restore main's bytes before EVERY commit that follows a run (R5);
never edit suite-hashed files mid-run (R6: data/ minus raw, web/data top level, docs/, specs/,
tests/ are snapshotted - finish all edits, THEN run, restore, commit; DECISIONS.md and tasks/ are
NOT in the snapshot set); /tmp artifacts are wiper-prone - the rebuild recipes are in the
DECISIONS records; never git merge/rebase/reset/stash or switch branches (team mode - the driver
syncs main; this prompt asks for no merge work).
