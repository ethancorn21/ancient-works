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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-14, iteration 137, agent c - the driver returned the parent after 207a (done),
- `tasks/236-us-cities.md` (split)
- `tasks/240-us-birdseye-batch4.md` (open) - hand-over: (2026-10-14, iteration 164, agent c - session 5 of 240: St. Paul (city 2) LANDED this
- `tasks/241-us-birdseye-batch5.md` (open) - hand-over: (2026-10-14, iteration 195, agent a - created at the 236b split, driver instruction; nothing

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/236c-us-cities-merge.md`
- `tasks/238-matcher-gate.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-14 240 DECISION: iteration 162 - St. Paul RESEARCHED (batch 4, city 2): QID Q28848 (first-guess Q16842 is a PERSON; the name search's first P625 hit is São Paulo, 8953 km - a TRAP to record); pool 51 unique / 13 good / 8 St. Paul sheets (6 drawn + 2 photographs) eyeballed; PICK = the 1906 Robert M. Saint near-vertical sheet (LOC 75694650); landing is the next session
- **QID (live, .venv/bin/python /tmp/aw240_sp_qid.py -> /tmp/aw240_sp_qid_162.txt + _qid2_162.txt):** the first-guess QID Q16842 is a PERSON ("Sami Niemi", no P625) - the usual mislabel trap class, caught by the label check. The city is **Q28848** (label "Saint Paul", description "capital city of the U.S. state of Minnesota and seat of Ramsey County"): P625 = ONE 30 m value (-93.093611, 44.944167) - the downtown/Capitol at the river confluence, no refinement needed; P373 = the STRING "Saint Paul, Minnesota" (the usual US quirk - place written "Ramsey County, Minnesota" from P131 + the state); P131 = Ramsey County (Q491201) ONLY; P17 = Q30 (a proper entity); enwiki "Saint Paul, Minnesota". Name search "St. Paul" (limit 20): **NAME-SEARCH TRAP** - the first hit WITH P625 is **Q174 São Paulo (8953.4 km)**; the second hit is Q28848 itself (0.0 km). Other P625 hits: Q1925291 St. Paul Iowa (481.9 km - nearest), Q952972 Nebraska (601.4), Q967930 Missouri (705.1), Q941244 Kansas (843.7), Q2182555 Indiana (867.9), Q2331494 Arkansas (1015.7), Q1745995 Alberta (1648.0), Q80107 Alaska (5255.5), Q19850778 Wiltshire (6330.8), Q56098775 Aachen (6847.7), Q41243576 Erding (7346.6), Q7591071 HK college (12045.7) - no local near-miss (unlike Kansas City's 10.2 km twin); the trap class here is the foreign-name first-hit, the 236b Pittsburgh/Chicago precedent. No existing site holds Q28848 (checked catalog sites.jsonl + extras.jsonl + 236a's extras_us_cities.jsonl + 236b's extras_us_birdseye.jsonl + web/data/sites.json). Site id = **st-paul-q28848** (catalog.slug("St. Paul") = "st-paul", verified; the SITES name is "St. Paul" per the 236b St. Louis precedent - the caption gate matches the sheet's "ST. PAUL" banner, and "st paul" is NOT a substring of "saint paul", so the short form is required for the gate). SITES `place` = "Ramsey County, Minnesota".
- **Pool (live run today, /tmp/aw240_sp_pool.py -> /tmp/aw240_sp_pool.json, log _pool_162.log):** 6 plain-phrase forms + " filetype:bitmap", srnamespace 6, srlimit 40 -> **51 unique titles, 13 good** (caption + keep() + Public domain + >= 4000 px). The 13 good: 8 distinct St. Paul sheets (1853, 1873, 1874, 1883, 1888, 1906 drawn; 1907, 1915 photographs; the 1906 and 1907 have .jpg/.tif pairs) + 3 search-noise non-St. Paul sheets (the Knowles farm-residence Whitewater Tp. WI 5676x6645; the Eldridge farm-residence Winona MN 5900x6645; the Oconomowoc/Waukesha WI lake-region railroad ad 11105x6199 - "St. Paul" only in a church/railroad name). Non-good: 4 gate-passing St. Paul sheets rejected on width (1893 Dayton's Bluff 3312x2552 .jpg/.tif; 1904 state capitol 1536x807 .jpg/.tif; 1908 Cedar Street 3243x4096 .jpg/.tif; NBY 423551/423552 817/820 px) + ~30 noise rows (other cities: Buffalo 1870, London 1905/1887/1910, Bovill ID, Valparaiso IN x2, Delaware OH x2, Columbus OH, Saint Boniface MB, Fargo, Syracuse, Staten Island; the Minneapolis Flour Milling District - city 3's pool; Yellowstone/Vitanje/Macau/NARA-cofferdam/street-photo noise; St. Paul's church items 1875/1873/2015/2021; the 2012 capitol photo CC BY 2.0; the 1888 federal-government page No restriction).
... (3.5 KB more: `grep -n -A 200 -F '## 2026-10-14 240 DECISION: iteration 162 - St. Paul RESEARCHED (batch 4, city 2): QID Q28848 (first-guess Q16842 is a PERSON; the name search's first P625 hit is São Paulo, 8953 km - a TRAP to record); pool 51 unique / 13 good / 8 St. Paul sheets (6 drawn + 2 photographs) eyeballed; PICK = the 1906 Robert M. Saint near-vertical sheet (LOC 75694650); landing is the next session' DECISIONS.md`)

### 2026-10-14 240 DECISION: iteration 163 - St. Paul LANDING nearly complete (module + staging + lead doc + golden done, all live commands green; the test-file extension is the remaining step - its 5 substitution pairs A-E are recorded here)
- **Live landing (all under .venv/bin/python, this session):** module edits to fit/src_us_birdseye_batch4.py (the SITES Q28848 entry with the full comment block, the ST_PAUL_1906 row-list, the SOURCES st_paul_1906 entry, docstring + SITES-header comment updated) -> `--verify` (2 QIDs: Denver clean; Q28848 P625 dist 0, P373 string, P131 Ramsey County, enwiki, and the EXPECTED TRAP line: first "St. Paul" name-search hit with P625 = Q174 São Paulo 8953 km - the 236b Pittsburgh/Chicago class, recorded, the hand-recorded caption_coords dist 0 is the guard) -> `--dry` (1 new site, 1 new picture) -> stage (live commons.info re-check passed; pick still on Commons, Public domain, page date 1906 = drawing year, no Zwolle swap; 2/2/2 staged) -> `--check` (exit 0, 2/2 PASS caption_coords, no join problems) -> lead doc complete (new St. Paul section: STAGED bullet + the full DROP list covering all 51 unique pool rows + the QID-facts paragraph; the session-4 --verify transcript appended verbatim; Staging section now 2 views / 2 site rows with the fresh --check transcript, the Not-done-yet pointer now names Minneapolis, Cleveland for 240) -> `--golden` (2/2/2). Transcripts saved: /tmp/aw240_verify_163.txt, _dry_163.txt, _stage_163.txt, _check_163.txt (all also transcribed into the lead doc, so nothing is lost if /tmp is wiped).
- **ORIENTATION CORRECTION (fresh-eyes, session 4):** the session-3 reading of the 1906 sheet ("drawn from the high ground SE of the river confluence looking NW; the Minnesota bottom-left, the Mississippi bottom-right") is WRONG. Measured this session: the confluence -> downtown bearing is 293.4 deg (downtown is 2046 m WEST + 887 m NORTH of the confluence), and on the sheet the dense downtown cluster sits UP-RIGHT of the confluence, so the sheet's up direction is ~WSW (the sheet faces ~west, drawn from a high vantage on the EAST side, the Minnesota side). River identities cannot be mirrored: the Mississippi approaches the confluence from the SOUTH (lower left on the sheet) and the Minnesota from the EAST (lower right); the joined river runs diagonally up-right (north) along the RIGHT side of the downtown cluster, which sits on the Mississippi's WEST bank. The 1883 sheet (eyeballed again) is consistent (same east-side vantage). Corrected in the module comment, the SITES note and the lead doc.
- **REMAINING (exact next step): extend tests/test_src_us_birdseye_batch4.py** (still the Denver-only state; it is currently RED on test_sites_table_and_staged_rows, which asserts SITES ids == {"Q16554": "denver-q16554"} - it will pass again after the extensions; the other four tests already hold with 2 rows). Five substitutions, each old block unique (count == 1 verified for all of them):
  - **A** (module header docstring, ~line 8): old `Co. sheet looking south from the Twenty-Third Street Viaduct - St. Paul, Minneapolis and Cleveland\nfollow in candidate order (the task owes FOUR staged cities, not specifically these four: a city\nwith no usable view gets a lead-doc note and the next candidate). The tests are offline: a` -> new `Co. sheet looking south from the Twenty-Third Street Viaduct - then St. Paul (the 1906 Robert M.\nSaint sheet); Minneapolis and Cleveland follow in candidate order (the task owes FOUR staged\ncities, not specifically these four: a city with no usable view gets a lead-doc note and the next\ncandidate). The tests are offline: a` (keep the preceding "Denver first - the 1908 ..." line as-is).
  - **B** (test_check_staged_files_join_and_pass, the key list): old `    for key in ("denver-q16554|File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg",):` -> new two lines: `    for key in ("denver-q16554|File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg",` / `                "st-paul-q28848|File:St. Paul, Minn. LOC 75694650.jpg"):`.
... (4.7 KB more: `grep -n -A 200 -F '## 2026-10-14 240 DECISION: iteration 163 - St. Paul LANDING nearly complete (module + staging + lead doc + golden done, all live commands green; the test-file extension is the remaining step - its 5 substitution pairs A-E are recorded here)' DECISIONS.md`)

### 2026-10-14 240 DECISION: iteration 164 - St. Paul LANDING complete (batch 4, city 2): the session-4 remainder (the test-file extension, substitutions A-E) applied, batch4 tests 5/5, full suite 182P/1S/0F (exactly the Denver-landing run's count - main unchanged since the R1 baseline), the four re-encoded 307d pngs restored to main's bytes, committed "240: St. Paul landed (batch 4 city 2) - the 1906 Robert M. Saint sheet"; Minneapolis (city 3) is the next session pair
- **Session-4 remainder applied as recorded:** tests/test_src_us_birdseye_batch4.py went from the Denver-only state to Denver + St. Paul via the five recorded substitutions A-E (module header docstring; the --check PASS-key list; test_sites_table_and_staged_rows' docstring + SITES-id dict; the years/points/named_by_qid dicts; the St. Paul date assertion after the Denver one). The file was pure ASCII before and remains pure ASCII (zero U+2018/2019/201C/201D, verified byte-by-byte; ast.parse OK, 231 lines). Batch4 tests 5/5 in 2.4 s (test_sites_table_and_staged_rows, red since the session-4 module edit, is green again).
- **Session-4's edit-tool "pitfall" did NOT reproduce (probed this session, so no PITFALLS entry was filed):** (1) a no-op replacement on an apostrophe-bearing line: the tool matched and reported identical content, no write (short-circuit); (2) a real single-line replacement with apostrophes in both oldText and newText on a scratch file: matched, wrote straight U+0027; (3) the exact multi-line C1-shape block (apostrophes + double quotes, four lines) on the scratch file: matched, wrote byte-exact. So session 4's diagnosis ("the edit-tool payload's apostrophes come out curly U+2019 while the file has straight U+0027") is not reproducible in iteration 164 - it may have been session-specific, or one of its blocks had an undetected difference. The fallback stays recorded in the hand-over: on a "Could not find", apply via the bash-heredoc + .venv/bin/python count==1 script (session 4's recipe is in the iteration-163 entry).
- **Full suite** (.venv/bin/python -m pytest -q -p no:cacheprovider, started after all edits per R6, /tmp/aw240_suite_164.log): 182 passed, 1 skipped, 0 failed in 490.91 s - exactly the Denver-landing confirmation run (iteration 161, /tmp/aw240_suite_161.log, 182P/1S/0F in 516.09 s): the St. Paul extensions add no tests (batch4 stays at five) and main has not moved since the R1 merged-tree baseline (main HEAD = 8678c8a "307: parent closed", which touches only DECISIONS.md, the 307 task file and the 307d pngs; the 1fc26b5 sync merged that same commit, verified by git show --stat). No known reds on this tree. The run re-encoded four 307d pngs (A_4-saved, A_5-reload, B_4-saved, B_5-reload - the set varies run to run, hence the "up to ten" rule); all restored to main's bytes (git checkout main -- docs/site_flow/; git diff main -- docs/site_flow/ clean) before committing (R5).
- **Committed this session:** tests/test_src_us_birdseye_batch4.py (the St. Paul extension), the task file (hand-over rewritten), this entry. The session-4 half (module + staging files + lead doc + golden) was already on the branch via the driver's 8b0efc5 work commit.
- **Next: Minneapolis (city 3)** - session 6 = RESEARCH (QID first-guess + label check, every P625, P373, P131, P17, enwiki, the name-search trap check; the pool via the 236b dvr template with CITIES=["Minneapolis"]; eyeball the 1280 px thumbs; pick the steepest near-vertical whole-city view), session 7 = LANDING (the proven pattern, in the hand-over). Twin-city caution: the two cities sit on opposite banks of the Mississippi - check every sheet's river side and keep the pools apart (the St. Paul DROP list recorded the Minneapolis Flour Milling District sheet, DPLA 2191x2813, as Minneapolis's). After Cleveland (city 4): CLOSE per the hand-over.

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)
- Re-verified the 160 hand-over's numbers with fresh measurements BEFORE deleting (AGENTS.md: check facts by running code). Confirmed: 8 pairs = 4 distinct points on a 100-px grid ladder (three on u=100; the 200-px and 100-px lat steps span 0.0053896/0.0017967 deg = 1.5:1 per pixel, no similarity can hit; the page's simFit (exact port) gives resid 10.9-39 m, 2.634 m/px, +1.06 deg - identical to the committed shot's [eval] line). CORRECTIONS to the 160 hand-over: the real hillfort is ~20 m NW of the site point (not '+22 E / -55 N'), its hachured ring is ~80-90 m across (not ~130 m), so the drawn ring (277-342 m at 2.634 m/px, centred at raw (240-248,115) -> (-3.5187, 51.0370) = E -218..-239, N +531) is ~3.5x too big and 554-582 m N-NW (N23-25W) of the real one - on a small hachured wood hill. The 160 '~2x / 535-576 m' survives as a range (540-576 -> 554-582), the direction and the verdict are unchanged. Extra independent check: the plate's own 'SCALE OF FEET 0-300' bar measures ~1.45 m/px vs the fit's 2.634 (1.8x). Distances must be geographic (dx=dlon*111194.9266*cos(lat0), dy=dlat*110900), NOT raw Mercator units (my first pass computed 916 m for the 576 m distance that way).
- Executed the 303 way exactly as 306c did (fit/review.py API, no hand-edited JSON): upsert_item(root,'bury-castle-q5001077',[entry]) with entry = {plan, title, url, pairs (the doc's 8), coarse:false, evidence (from the data/commons/files.jsonl row: rec evidence/1, kind category, checked 2026-10-10, site_cat/file_cat 'Bury Castle, Somerset'), label '1911', cite, ref, size, place_reason '306d audit 2026-10-12: ... Document deleted.'} appended to the existing item (lead n0136_1 kept first, filename unchanged), then deleted data/db/platefits/bury-castle-q5001077.c_de779031cda8a0dc.json, then export(root,'bury-castle-q5001077') (333 open of 346). Only 3 files changed (D doc, M item, M web/data/review.json) - no other site's item touched; the site was already covered for the union check (its item was already open in the page file before the upsert).
- Wrote the 306d block (header + the bury-castle line) into docs/site_flow.md after the 306c block (header is tense-neutral: 17 more lines to come in batches; box 1 ticked - 36 shots re-listed this session).
- TESTS (full suite, main checkout, --ignore=tests/test_gate.py, -p no:cacheprovider, with my changes): 10 failed, 130 passed, 1 skipped (251 s). The 10: test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (FAILED at the seed check, dep:null) + 9 that are agent a's in-flight work already on main (test_merge new_sites_are_complete/new_site_golden_samples = 211's open 222-228 gate; src_artists/limes/mackenzie/numancia/wiltshire_stukeley stage+check tests = the 224 family). Baseline in my task file (123/1, 2026-10-12) is STALE - main has since merged 211/223/224/307 work and the suite grew to 141 tests.
- A/B attempt 1 (worktree at HEAD in /tmp/aw306d_ab): INVALID - web/data/sites/ is mostly gitignored (58 tracked files vs 389 site dirs in the main checkout; the per-site web data + data/raw are local build artifacts), so a fresh worktree lacks stonehenge etc. and fails 3 tests deterministically (site_done_line FileNotFoundError '/tmp/aw306d_ab/web/data/sites/stonehenge-q39671', fit_provenance line_refuses_unmarked_non_auto_doc, fit_queue save_runs) that pass in the main checkout; its placement_gestures 'vacuous ERROR' there is also unprovable (no local depictions). PITFALLS candidate: never A/B this project in a bare worktree/checkout - do it in the main checkout with the changed files temporarily at HEAD. (The worktree is still registered; remove it: git worktree remove --force /tmp/aw306d_ab && git worktree prune.)
... (1.9 KB more: `grep -n -A 200 -F '## 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)' DECISIONS.md`)

### 2026-10-13 DRIVER: test suite failing at loop start (1 tests)
    tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    tests/test_fit_queue.py:1749: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    1 failed, 159 passed, 1 skipped in 424.53s (0:07:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-14 240 (agent c, iteration 165) HAND-OVER STATE: Minneapolis (city 3) RESEARCHED - QID Q36091 (first-guess Q3094 a Romanian monastery; no name-search trap), pool 50/20 all eyeballed, PICK = the 1885 Herancourt/Monasch near-vertical sheet (LOC 75694644); records committed (DECISIONS entry + task file); PITFALLS.md edit (blank-crop quirk) left in the working tree for the landing session; next = the Minneapolis LANDING (session 7).
