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
socket-blocking fixture; the PASS-key list; the SITES-id / extras-id / year / point / named tables;
the golden compare) -> module tests -> the FULL suite (restore the 307d pngs first, below) ->
commit. The lead doc's Staging section ends with the Not-done-yet pointer to 241 naming the next
two or three candidates (the 236b precedent).

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
(2026-10-14, iteration 165, agent c - session 6 of 240: Minneapolis (city 3) RESEARCHED this
session - QID Q36091 verified live (first-guess Q3094 is a Romanian monastery - the third
mislabel trap; the name search's first P625 hit = the city itself, 0.0 km - no trap), pool
50 unique / 20 good, all 9 Minneapolis sheets eyeballed one by one, PICK = the 1885 W. V.
Herancourt / I. Monasch near-vertical sheet (LOC 75694644, 13152x9408 - the steepest
whole-city view in the pool). The session ended at the context limit AFTER the records
(DECISIONS entry, this hand-over, the task-Notes line, a new PITFALLS entry) were written: the
PITFALLS.md edit is still UNCOMMITTED in the working tree - fold it into the landing commit.
NO tests ran this session (research only); last test state = the St. Paul-landing run
(iteration 164): 182P/1S/0F, batch4 tests 5/5. NEXT (session 7): the Minneapolis LANDING (the
pattern below); then Cleveland (city 4) research + landing; then CLOSE.)

**State NOW (all committed on agent/c; the St. Paul landing commit 09c3c01 tops the branch
log):**
1. **Module** fit/src_us_birdseye_batch4.py: SITES = Denver (Q16554) + St. Paul (Q28848);
   SOURCES = denver_1908 + st_paul_1906. Staging files 2/2/2. The Minneapolis SITES entry
   (Q36091) + the MINNEAPOLIS_1885 row-list + the SOURCES minneapolis_1885 entry are NOT yet
   added - that is the landing's module edit. The lead doc is complete for Denver + St. Paul
   (the Staging section's Not-done-yet pointer already names Minneapolis + Cleveland for 240).
2. **Test** tests/test_src_us_birdseye_batch4.py (5 offline tests, all green): the PASS-key
   list = Denver + St. Paul; the SITES-id / extras / years / points / named_by_qid tables
   hold both cities; the golden 2/2/2 pins both.
3. **Baselines (R1):** merged-tree 177P/1S/0F; the Denver-landing and St. Paul-landing runs
   were both 182P/1S/0F (main has not moved since R1; main HEAD = 8678c8a). No known reds on
   this tree. The full suite takes ~9 min.
4. **Minneapolis facts (researched this session; the full record = the DECISIONS entry "240
   DECISION: iteration 165" + the /tmp/aw240_mpls_* artifacts, wiper-prone - rebuild recipes
   below and in the 162/163 entries):**
   - **QID Q36091** (the first-guess Q3094 is a Romanian monastery - the mislabel
     trap, caught by the label check): label "Minneapolis"; P625 = ONE 30 m value
     (-93.26916666666666, 44.981944444444444) the downtown core (no refinement); P373 = the
     STRING "Minneapolis" (BARE - the US quirk in its extreme: place written "Hennepin
     County, Minnesota" from P131 + the state); P131 = Hennepin County (Q486229) ONLY; P17 =
     Q30; enwiki "Minneapolis"; name search: first P625 hit = the city itself (0.0 km) - NO
     trap line expected from --verify (Denver's pattern); the in-city institutions (0.4-4.5
     km) and the metro/airport rank behind the city; other P625 hits: Minneapolis, Kansas
     (746.9 km), Minneapolis, NC (1370.2 km). No existing site holds Q36091 (all five files,
     0 hits). Site id = **minneapolis-q36091** (slug verified live).
   - **PICK = `File:Minneapolis, Minnesota. LOC 75694644.jpg`** (13152x9408, PD; page date
     1885 = the drawing's year - no Zwolle swap; LC Panoramic (2nd ed.) 396; W. V. Herancourt
     (draughtsman) + I. Monasch (publisher); banner "BIRD'S EYE VIEW OF MINNEAPOLIS, MINN.
     1885 POPULATION 71,235"; the steepest near-vertical whole-city view in the pool - the
     built-up city fills the whole frame, no horizon band). Orientation for the note field
     (the 1280 px thumb read; MEASURE against the 13152 px original at landing - the St. Paul
     landing needed a fresh-eyes orientation correction): drawn from a high vantage on the
     SW; the Mississippi runs along the sheet's lower/right edge (the flow exits at the
     upper-left, toward St. Paul); the 1885 city proper (west bank) is the dense side, the
     east-bank farmland (pre-1909 Saint Anthony) is the fine-grid side; the Minnesota River
     enters from the west/southwest edge. Same-sheet scan: the 13152x9408 .tif twin.
   - **Pool drops (all 50 accounted for; the per-item reasons go into the lead doc at
     landing):** 1867 "Minneapolis and Saint Anthony" LOC 73693455 (+ .tif) - the twin-cities
     sheet (both pre-merger cities, oblique, pre-annexation scope); 1879 "Panoramic view ...
     1879" LOC 75694642 (+ .tif) - the "Looking north west" oblique; 1879 DPLA 7ccb8501 - a
     second printing of the SAME 1879 sheet (the M&StL Railway Co. edition); 1891 A.M.R. Smith
     & Geo. Renger LOC 75694646 (3 scans: the LOC .jpg, the LOC 75694905 "1/4 size" photocopy
     .jpg/.tif, the DPLA 30b065a3 copy) - near-vertical but recedes to a horizon, shallower
     than the 1885 pick; 1907 "Looking southwest from Guaranty Bldg." LCCN2013647302 (+ .tif)
     - a PHOTOGRAPHIC panorama strip (F.L. Wisthof Photo), low vantage, downtown close-up - a
     photograph, not a drawn bird's-eye view; 1886 "View of Minneapolis - engraved ...
     Hageboeck" LCCN2008677251 .tif (12816x9504; the 1024 px .jpg twin too small) - an oblique
     riverfront-CORRIDOR view (the 3rd Street suspension bridge in the foreground), not a
     whole-city bird's-eye view; DPLA 396e002a "Bird's Eye View of the Minneapolis Public
     Library System" - a schematic library-branch map (the MHL); DPLA 5a20a334 "Minneapolis
     Perspective Map - GIANT Post Card" - a 1937 Langwith postcard (beyond the 1929 edge; a
     street map, not a bird's-eye view); search noise: the Knowles + Eldridge Winona Co. farm
     plates (the same David Rumsey plates that landed in St. Paul's pool), the 1500 Venice
     view (held by the Minneapolis Institute of Art), the Yellowstone Poole Bros. 1898 map.
     The 30 non-good: ten DPLA 2144-2227 px scans (incl. the Flour Milling District
     2191x2813 - the item St. Paul's DROP list attributed to THIS pool, confirmed to belong
     here - and the University of Minnesota campus sheet), NBY postcards 825/824 px, the
     1904 photo 3072 px, Superior WI x2 (caption gate), the cul-de-sac (CC0, 3992 px), MCAD
     (CC BY 3.0, 600 px), "Downtown Minneapolis" DPLA 6016x4763 (keep=0 - undated; also a
     downtown close-up), Lake Minnetonka (gate, 2195 px), the Venice Google Art Project trio
     (keep=0 - 1500 predates the window) + the 800 px detail, three Yellowstone covers, the
     two 2026 Rebel Loon (CC0), Kapkap (CC BY 4.0, gate), the Dark-eyed Junco (CC BY 2.0,
     600 px).

**Landing pattern (proven twice - Denver, St. Paul; reuse verbatim for Minneapolis, then
Cleveland):**
0. **First:** if `git status` still shows the session-6 PITFALLS.md edit (the blank-crop
   quirk entry), it goes into this session's landing commit; if /tmp was wiped, rebuild the
   Minneapolis artifacts from the 162/163/165 DECISIONS records before eyeballing anything
   again.
1. **Module edit:** the SITES entry (full comment block: first-guess mislabel, every P625,
   P373 string, P131, enwiki, name-search TRAP lines, the no-existing-site check across the
   catalog + extras + 236a's + 236b's extras + web/data/sites.json, the slug; name = the
   caption's short form; place = P131 + state) + the <CITY>_<YEAR> row-list (a date= entry
   ONLY for a Zwolle swap - Minneapolis needs none) + the SOURCES entry (label "{name}, the
   {artist} bird's-eye view ({year})") + the module docstring and SITES-header comment (the
   city list).
2. **Live:** --verify (save the exact output verbatim for the lead doc's QID section; for
   Minneapolis NO trap line is expected - if one appears, record it and re-check the QID)
   -> --dry -> stage (live commons.info re-check; if the pick vanished or is no longer PD,
   take the next-best pool candidate and record the swap) -> --check (append the transcript
   to the Staging section; expect all PASS caption_coords, no join problems) -> ALSO MEASURE
   the sheet's orientation here (fresh eyes on the 13152 px original: the river's flow, the
   Minnesota River's entry, the dense vs farmland sides) before writing the note-field angle
   claim.
3. **Lead doc:** the city section (STAGED bullet: year, artist, size, PD, page, apparent
   angle; the DROP list covering every unique pool row with its reason; the QID-facts
   paragraph) + the Staging section's counts (3 views / 3 site rows after this landing).
4. **Close:** --golden -> extend the test (the PASS key, SITES ids, years, points,
   named_by_qid, the date assertion, the header docstring's city list) -> the module tests ->
   the FULL suite (.venv/bin/python -m pytest -q -p no:cacheprovider; expect 182P/1S/0F while
   main is unchanged - if main has moved, diff the new count against the failing set, not the
   number) -> git checkout main -- docs/site_flow/ (R5: restore the re-encoded 307d pngs) ->
   commit "240: Minneapolis landed (batch 4 city 3) - the 1885 Herancourt/Monasch sheet".

**Research pattern (session 8, Cleveland):** (a) QID: clone /tmp/aw240_mpls_qid.py (itself a
clone of the 236b dvr_qid pattern, repointed at this checkout; rebuild from the 162/163/165
DECISIONS records if /tmp was wiped) - first-guess QID + label check (the mislabel trap has
now hit three of four cities: a person, a person, a monastery), every P625 value, P373 (write
the place from the county + state), P131, P17, enwiki, the limit-20 name search with
distances for every P625 hit (Cleveland: check in-city institution traps and the other-state
/ foreign namesakes; record TRAP lines exactly as St. Paul's); save the transcript. (b) Pool:
/tmp/aw240_mpls_pool.py with CITIES=["Cleveland"] (six plain-phrase forms + "
filetype:bitmap", srnamespace 6, srlimit 40; dedupe; the
keep/caption/Public-domain/>=4000 px gates; 1280 px thumbs eyeballed one by one; artifacts
under /tmp, re-verifiable). The pick = the steepest (near-vertical), best-scanned whole-city
view (the caption names the city). Cleveland sits on the Cuyahoga at Lake Erie - check every
sheet's lake side (the twin-city caution had no effect this time: the St. Paul side of the
1885 sheet is pre-annexation farmland).

**After Cleveland (city 4) lands: CLOSE** - final full-suite run = the baseline; --check all
PASS, no join problems; the four ids/QIDs collide with nothing (the known_sites() guard +
the test); extend the test tables to the full set (four keys/ids/years/points/named);
tick boxes 1-4 (each after its test passes); the lead doc's Staging section final (4 views /
4 site rows; the Not-done-yet pointer then names only 241's cities); Status: done.

**Rules that bite (unchanged from the task Notes):** never write the canonical files (236c);
236a's and 236b's files are read-only (the module's cross-check enforces); live commands
under .venv/bin/python (the module top stays stdlib-only; /tmp scripts repoint sys.path at
this checkout); the golden regenerates only via --golden; tests never bind fixed network
ports or write outside the project and the temp dir; every full-suite run re-encodes up to
ten docs/site_flow/307d_*.png - restore main's bytes before EVERY commit (R5) and never edit
suite-hashed files mid-run (R6: data/ minus raw, web/data top level, docs/, specs/, tests/
are snapshotted - finish all edits, THEN run, restore, commit; the memory files DECISIONS.md
and tasks/ are NOT in the snapshot set, so the bookkeeping can be written while the suite
runs); /tmp artifacts are wiper-prone - the rebuild recipes are in the task Notes and the
162/163/165 DECISIONS entries. The full-suite run takes ~9 min - start it, then do the
bookkeeping; check the log tail before committing.
