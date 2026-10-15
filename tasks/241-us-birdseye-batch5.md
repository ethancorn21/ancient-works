Status: in-progress
Depends on: 240
Touches: fit/src_us_birdseye_batch5.py, data/catalog/extras_us_birdseye_batch5.jsonl, data/commons/files_us_birdseye_batch5.jsonl, data/commons/classified_us_birdseye_batch5.jsonl, docs/lead_us_birdseye_batch5.md, tests/test_src_us_birdseye_batch5.py, tests/golden/src_us_birdseye_batch5_sample.json, PITFALLS.md, docs/site_flow/307d_*.png (R5: restoring suite re-encodes to main's bytes before committing - never content changes)

# 241: US bird's-eye views, batch 5 - the final five cities to the 25-city total

## Goal
Second part of the 236b split (2026-10-14, driver instruction; 236b closed done at 16 cities and the
remaining nine went to 240 and this task, each with its own module and staging files so two agents
can build in parallel). Stage batch 5 of the Library of Congress "Panoramic Maps" collection (about
1,500 US bird's-eye views, 1847-1929, public domain; this machine cannot reach loc.gov, so files are
fetched from their Wikimedia Commons mirrors - 236b's route): the FINAL FIVE cities needed for the
25-city total (16 from 236b + 4 from 240 + 5 here), each a new site in this task's own staging
files, one best view per city. 236c consolidates all the staging into the canonical data and checks
the total.

## Acceptance criteria
- [ ] fit/src_us_birdseye_batch5.py holds the hand-checked file -> QID table for its five cities
      (every QID verified live against Wikidata with the module's --verify BEFORE staging: label,
      every P625 value, P373, P131, enwiki, the first name-search hit with coordinates - what
      record --live would resolve; the machine cannot reach loc.gov, so the files are fetched from
      their Wikimedia Commons mirrors, 236b's route). The module copies fit/src_us_birdseye_batch4.py's
      machinery (itself a copy of fit/src_us_birdseye.py's - the template it keeps in sync with);
      its known_sites() reads the catalog plus 236a's extras_us_cities.jsonl, 236b's
      extras_us_birdseye.jsonl and 240's extras_us_birdseye_batch4.jsonl so a QID can never sit on
      two sites.
- [ ] Staged rows in this task's files ONLY: extras_us_birdseye_batch5.jsonl (the new cities' site
      rows - region "United States", kind "town", aerial_ok true, the point = the city's verified
      P625 or a recorded refinement, the note recording the staged view's apparent angle so 236c /
      the matcher can order the oblique views); files_us_birdseye_batch5.jsonl (files.jsonl shape +
      the 200 evidence field); classified_us_birdseye_batch5.jsonl (p_birdseye 1.0, by "hand"). One
      row per city = the steepest (near-vertical), best-scanned whole-city view of the collection
      for that city (Public domain, >= 4000 px wide, the caption names the city); every pool item
      not staged is listed with its reason in the lead doc.
- [ ] fit/evidence.py check passes offline on every staged row (--check exit 0, every row PASS
      caption_coords, no join problems); no staged site id or QID collides with an existing site
      (the catalog, 236a's, 236b's and 240's staging files, web/data/sites.json) - never two sites
      for one QID (the catalog slug rule: id = slug(name) + "-" + qid-lower).
- [ ] Test (no network, the socket-blocking fixture per 236b's test file): the staged files join,
      the evidence check passes, a golden sample tests/golden/src_us_birdseye_batch5_sample.json
      pins the staged rows (regenerated only via the module's --golden for an intended change); a
      full-suite run = baseline (restore the re-encoded docs/site_flow/307d_*.png to main's bytes
      before committing - the PITFALLS test_owner_check rule).
- [ ] FIVE cities staged (the 25 total: 16 from 236b + 4 from 240 + 5 here), each per the boxes
      above; or, if the collection yields fewer usable candidates after a documented search, each
      dropped candidate is recorded with its reason in the lead doc and the shortfall (with the
      final count) is recorded there for 236c's 25-total check.

## Notes (operational facts carried from the 236b split, 2026-10-14 iteration 195)

**Read first (all on main):** 240's task file (its Notes carry the complete per-city playbook, the
module-copy spec and the rules - they apply here verbatim), fit/src_us_birdseye_batch4.py (the
module to copy - change only the staging-file paths to the *_us_birdseye_batch5.* set in the
Touches line, the module name in the rows' "by" / "source" fields, and known_sites() to also read
240's extras_us_birdseye_batch4.jsonl - it will exist by the time this task runs, 240 is done),
240's lead doc (docs/lead_us_birdseye_batch4.md: the STAGED/DROP section format, the QID
transcript format, and its "Not done yet" pointer naming the next candidates), plus 236b's
docs/lead_us_birdseye.md (the Fetch route and evidence-field contract) if you need the original
wording. Do NOT edit fit/src_us_birdseye.py, fit/src_us_birdseye_batch4.py, fit/evidence.py or any
pipeline/ file (read-only for this task; file a task if one of them needs a change). This module
stages no shared (owner-named) cities.

**The candidate list:** start from 240's lead-doc "Not done yet" pointer (240's Notes require it
to name the next two or three candidates in the collection's search order); if it names fewer than
five, continue the LOC Panoramic collection's city list in search order (the six plain-phrase
forms + " filetype:bitmap" over candidate cities - 236b's pool route), skipping cities already
staged anywhere (236b's and 240's site tables, the catalog, web/data/sites.json) and cities whose
pools yield no usable view (record each drop, take the next candidate). This task owes FIVE
staged cities, not specific ones. St. Paul / Minneapolis / Cleveland were 240's candidates - if
240 dropped any of them, they come first here (240's lead doc says why they dropped).

**Per-city landing (the proven 189-194 pattern, one city per session pair):** (1) RESEARCH: the
QID (Wikidata: the label - first-guess mislabels are the usual trap class, every P625 value, P373
(a string is the usual US quirk - write the place from the county + state), P131, P17, enwiki,
the name-search trap check; record everything in the SITES comment; MEASURE every distance claim
with fit/evidence.hav_m + geographic dx/dy before writing it; check no existing site holds the
QID - if one does, tie the row to that site like 236b's shared cities and record it in the lead
doc) + the pool (build, dedupe, filter, 1280 px thumbs eyeballed one by one - the
/tmp/aw236b_b3_dvr.py script is the template). (2) LANDING: module edit -> --verify (save the
exact output; the lead doc carries it verbatim in the QID section) -> --dry -> stage (live
commons.info re-check) -> --check (save the transcript; the Staging section carries it verbatim)
-> lead-doc section (STAGED bullet + the full DROP list + the QID-facts paragraph) -> --golden ->
test extension (mirror tests/test_src_us_birdseye.py / test_src_us_birdseye_batch4.py: the
no_network socket-blocking fixture; the PASS-key list; the SITES-id / extras-id / year / point /
named tables; the golden compare) -> module tests -> the FULL suite (restore the 307d pngs first)
-> commit. The lead doc's Staging section ends with the project total (it should read 25 when all
five land) and a note that 236c consolidates.

**Rules (unchanged from 236b/240):** NEVER write the canonical files (data/catalog/extras.jsonl,
data/commons/files.jsonl, classified.jsonl - that is 236c); NEVER touch 236a's, 236b's or 240's
files (read-only; the module's cross-check enforces); live commands under .venv/bin/python
(system python3 has no numpy; the module top stays stdlib-only); the golden sample is the contract
(--golden only for an intended change); tests never bind fixed network ports or write outside the
project and the temp dir; every full-suite run re-encodes up to ten docs/site_flow/307d_*.png -
restore main's bytes before committing (the PITFALLS test_owner_check entry); one row per sheet
(same-sheet scans recorded in the lead doc, the LOC .jpg staged where it is the best scan).

## Hand-over
(2026-10-14, iteration 185, agent c) **Portland LANDING half-done: module edited + staged
(5/5/5) + --verify clean + --check green + --golden written - ALL UNCOMMITTED in the working
tree (harness-saved). The lead doc, the tests, the suite and the close are still to do -
specs below, everything recorded here so no research is repeated.**

**State on this tree (verify before trusting):** tree at session start was clean (the 184
research commit d1f3bcc was the tip); the working tree now has, UNCOMMITTED: the module
(all 5 edits: header docstring city list, SITES-header comment, new SITES["Q6106"] entry
with full QID-facts comment, new PORTLAND_1890 source block, SOURCES["portland_1890"]), the
three staging files at 5/5/5, the golden at 5/5/5. Run `git status --short` and `--check`
first to confirm. The 4 earlier cities are unchanged and committed (Omaha Q43199 / Indy
Q6346 / Columbus Q16567 / Memphis Q16563).

**What was done this session (all recorded here - /tmp artifacts may be wiped):**
1. Pre-stage mirror search (the Omaha LCCN-search step; /tmp/aw241_pdx_mirror.log):
   title searches found ONE new item: **"File:Portland, Oregon 1890. LOC 75694939.tif"** -
   13760x9520, Public domain, date 1890, artist "Clohessy & Strengele; Elliott Pu Co.", desc
   "Perspective map not drawn to scale. Bird's-eye-view. LC Panoramic maps (2nd ed.), 724
   Available also through the Library of Congress Web site as a raster image. Includes
   illus. and index to points of interest." = a SECOND scan of the same 1890 J. McI. Wood
   sheet (it was NOT in the 12-query pool - its title has no bird's-eye phrase). Verified a
   SEPARATE scan, not a re-encoding: 1920-px thumbnails differ with mean absolute diff 11
   (a Memphis-style re-upload would match pixel-for-pixel; a distinct scan shows this);
   eyeballed side-by-side crops (cartouche, downtown grid, top vignette band):
   the staged .jpg (artist "Library of Congress, Geography and Map Division") is the
   SHARPER scan - crisper vignette linework and cartouche type, cleaner downtown grid;
   the .tif is warmer-toned and slightly hazier in the centre with more smudging in the
   lower legend panels. VERDICT: the .jpg stays staged (the 1872-Columbus best-of-scans
   rule); the .tif is a DROP (same-sheet dupe) - it goes in the lead-doc DROP list with
   this comparison record. Note: 4096-px on-demand Wikimedia thumbs 400 (use <=1920 px);
   urllib gets 403 from thumb.wikimedia.org (use curl, as the pool scripts do).
2. Module edits exactly per the old hand-over spec (plus the dupe sentence in the
   PORTLAND_1890 comment block).
3. `--verify` (live Wikidata): **clean - 5 QIDs, zero FLAG/TRAP lines**. Verbatim transcript
   (paste into the lead-doc QID section; also /tmp/aw241_pdx_verify.log):
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
   (Q6106 facts for the lead-doc paragraph: label "Portland"; P625 ONE 31 m value = the
   downtown core, no refinement; P373 STRING "Portland, Oregon" -> place "Multnomah
   County, Oregon" (P131 = Multnomah Q450374 (county seat) + Clackamas Q484404 +
   Washington Q484538 - the three-county pattern, like Columbus); P17 = Q30; enwiki
   "Portland, Oregon"; NO TRAP at limit 5 AND 20 - Q6106 is the #1 hit outright at both
   limits, no first-guess QID from memory (the 177/179 mislabel class did not fire);
   never-first hits measured in 184: Q49201 Maine 2nd (4081.9 km), CT 3991.2, IN 3089.3,
   MI 2998.2, AR 2980.8, TX 2969.3, Dorset EN, Australia 13324.1, PSU 0.5 km, U. of
   Portland 7.4 km; no existing site holds Q6106 - grep clean in all seven files; id =
   portland-q6106, a future Portland ME would be portland-q49201.)
4. `--dry` then stage: **"staged: 1 new sites, 1 new pictures"** (portland-q6106, live
   commons.info re-check passed); staging files are 5/5/5. New file row verified:
   year 1890, date "1890", NO date_commons (no Zwolle swap), Public domain, 13760x9520,
   evidence named_place "Portland", site+place point = (-122.67916666666666, 45.515),
   dist 0.
5. `--check` (offline): **"evidence: 5 rows, 5 pass, 0 fail, 0 no-tie", ZERO join lines**
   (verbatim in /tmp/aw241_pdx_check.log; paste the 5 PASS lines into the lead-doc
   Staging section - the four old ones + the new
   `PASS caption_coords  portland-q6106|File:Portland, Oregon 1890 Perspective Birds-eye-view Map.jpg`).
6. `--golden` written 5/5/5 (intended change).
7. Pool analysed from /tmp/aw241_pdx_pool.json (55 rows, flags keep/gate/good): **12
   good** ([0] ME1876 .jpg, [2] 2007662704 .tif, [6] PICK, [9] ME1876 DigitalCommonwealth,
   [13]/[25] 91719502 .jpg/.tif, [21]/[26] Port Townsend x2, [22]/[40] Casco Bay .jpg/.tif,
   [27] Seattle 1878); **9 keep-fails** ([11] Fleet 640, [14]/[35] NARA gas-station
   1973 2000x1361, [29] Casco BPL 2000 CC BY, [46] Essayons dredge 1980 4797, [47]-[50]
   Flounce Rock 2012 x4); **11 gate-fails with keep** ([24] Walla Walla 7882, [28]/[31]
   Boston waterfront LCCN2005691058 5541x4401, [30] Aiken 1320, [33] Rumford Falls 1020,
   [37] Biddeford 649, [38] Oregon City 768, [41]/[42] AYP Seattle postcard x2, [45]
   Architect & Engineer 1352 "No restrictions", [54] 1753 West-Coast map 1268 CC BY 2.0);
   **23 keep-pass gate-pass width/licence-fails** ([1] BPL 930, [3]-[7] M.F. King 1865
   Portland ME photos 2737 x5, [8] BPL ME1876 2000 CC BY, [10] (1882) 2934, [12] Wells
   River 828, [15] Post Office 768, [16] Gill 1880 1742, [17]-[20] NYPL 3072 x4, [32]
   Tacoma 768, [34] AYP 768, [36] Meredith 645, [39] 1879 map 5000 CC BY-SA 3.0, [43]
   Seattle 1888-89 768, [44] L&L catalogue 3488 "No restrictions", [51]/[52] Motoring
   1915 2272/2277, [53] Winona 1953). The 12 good + the 3 eyeballed width-fails ([16],
   [17]/[18]) get their own bullets; the other 40 get grouped bullets (see the 184
   DECISIONS entry's grouping, which this breakdown confirms and extends).
   **Future-candidate grep (this session):** Seattle, Salt Lake City, San Antonio,
   Port Townsend, Buffalo are NOT staged in any extras/catalog/web-sites file; "richmond"
   and "miami" DO hit in data/catalog/sites.jsonl (existing sites - check they are the US
   cities before listing as future candidates; likely Richmond VA / Miami FL = not
   candidates). So the lead doc's future-candidate hits: Port Townsend 1878 (LOC
   2003679983 x2 scans), Seattle 1878 (MAPS 64), Santa Fe 1882 (LOC 75694742), Las Vegas
   NM 1882 (LOC 75694741) - all PD, all >= 4000 px (the last two from the 184 Albuquerque
   probe; note "Las Vegas NM" is a DIFFERENT city from Nevada - disambiguate by county).

**NEXT (one session, in this order):**
1. **Lead doc** (docs/lead_us_birdseye_batch5.md, 582 lines) - FIVE edits:
   (a) intro paragraph: after "Memphis (LANDED - city 4 of 5; ...)" add "Portland (LANDED
   - city 5 of 5; the 1890 J. McI. Wood perspective sheet - the only drawn whole-city view
   in its pool that passes the 4000-px gate; the first city-5 candidate, Albuquerque, was
   researched and dropped - its section below)", and mark all five done.
   (b) QID section: append "Transcript for Portland (the 241 session-12 run 2026-10-14,
   verbatim):" + the transcript above (5 QIDs) + the no-FLAG/no-TRAP paragraph (pattern of
   the Memphis one, with the Q6106 never-first hits from item 3 above).
   (c) NEW section "## Albuquerque (DROPPED - no drawn view in the Commons mirror)" AFTER
   the Memphis section: full content = the 184 DECISIONS entry's Albuquerque bullets (QID
   facts incl. all never-first hits, the 0/0/0/0/0/0 pool + the case-quirk root cause,
   the extended probes: "albuquerque LOC" -> HABS/Veterans-Admin aerial photos/1931
   foundery/Route-66; "panoramic albuquerque" -> the 1915 LCCN2007662623 4563x697 photo
   strip (the mirror's only Albuquerque item); "new mexico bird eye view" -> Santa Fe
   1882 + Las Vegas NM 1882 (future hits); broad dumps -> only bird photos/books/HABS/
   postcards) + verdict + "city 5 = the next probe-list candidate: Portland (Oregon) -
   LANDED below".
   (d) NEW section "## Portland (site `portland-q6106`, this task's point = the verified
   P625; 1 view staged)" after it: STAGED bullet (the pick's full description - from the
   module's PORTLAND_1890 comment block: 1890 = banner, no swap; LOC Panoramic item;
   cartouche JAMES MCI. WOOD...; NW vantage; Willamette diagonal; truss bridge; Mt. St.
   Helens/Cascades band; vignettes; 13760 px widest + steepest + only gate-pass drawn
   sheet); DROP list = the 12 good items itemised (from item 7 above + the 184 entry's
   per-item descriptions) + the 3 eyeballed width-fails + the 40 grouped; **EXTRA probes
   sub-block: the landing's mirror search found the LOC 75694939 .tif dupe (item 1 above
   verbatim: dimensions, artist, desc, the 1920-px mean-diff-11 = separate scan, .jpg
   sharper -> stays staged, .tif DROP) - plus the future-candidate hits from item 7);
   QID-facts paragraph (the 184 entry's Q6106 block, pattern of the other four).
   (e) Staging section: "**4 views / 4 site rows so far of the final five**" ->
   "**5 views / 5 site rows - all of the final five** (Omaha session-4; Indianapolis
   session-6; Columbus session-8; Memphis session-10; Portland staged in the 241
   session-12 run - all five LANDED; Albuquerque was the first city-5 candidate and is
   DROPPED, its section above)"; replace the 4-line --check transcript with the 5-line
   one (item 5); golden "4/4/4" -> "5/5/5"; Not-done-yet -> "**All five of this task's
   cities are LANDED** ..." + the 236c consolidation note (it now consolidates and checks
   the 25 total = 16 + 4 + 5, no shortfall) + the future-candidate hits + the standing
   "Do NOT write the canonical files" paragraph (keep its current tail).
2. **Tests** (tests/test_src_us_birdseye_batch5.py): test_check_staged_files_join_and_pass
   += the Portland PASS key (item 5); test_sites_table_and_staged_rows: SITES-id map +=
   "Q6106": "portland-q6106", years dict += the .jpg title: 1890, points +=
   "portland-q6106": (-122.67916666666666, 45.515), named_by_qid += "Q6106": "Portland",
   + a Portland row date check (date "1890", NO date_commons - the Omaha pattern); golden
   docstring 4/4/4 -> 5/5/5; negative control UNCHANGED (files[0] = Omaha).
3. **Module tests**: `.venv/bin/python -m pytest tests/test_src_us_birdseye_batch5.py -p
   no:cacheprovider` -> expect 5/5 (the three-state test's victim stays files[0] = Omaha).
4. **FULL suite IN-SESSION BLOCKING**: `.venv/bin/python -m pytest tests/ --ignore=
   tests/test_gate.py -p no:cacheprovider` (expect ~187P/1S/0F on this tree; zero red =
   the criterion; the only tolerated red = test_fit_queue
   test_placement_gestures_and_save_in_the_browser = agent a's 239; the 183 entry has the
   decomposition; the three test_gate tests pass standalone). NEVER nohup past the session
   (174 lesson).
5. **R5**: `git checkout main -- docs/site_flow/307d_*.png` (this run re-encodes up to ten;
   the 183 run found one already-divergent - restore all of them), verify
   `git diff main -- docs/site_flow/` empty.
6. **Commit** everything (module, lead doc, golden, test, the three 5/5/5 staging files,
   restored PNGs, DECISIONS, this hand-over): `git add -A && git commit -m "241: Portland
   (city 5 of 5) landed - ..."`.
7. **CLOSE**: final `--check` = 5/5 PASS no join problems, FULL suite zero red, tick ALL
   FIVE acceptance boxes, `Status: done` (the driver re-checks; 236c then consolidates).
   Append the 185 DECISIONS entry first (it already exists - see the journal; verify it
   covers items 1-7 and amend if the harness trimmed it).

**Rules (unchanged):** never write the canonical files (236c); 236a's/236b's/240's files
read-only; live commands under .venv/bin/python (module top stays stdlib-only); the golden
is the contract (--golden only for an intended change - it was already regenerated this
session, do NOT re-run it); tests never bind fixed network ports or write outside the
project + temp dir; every full-suite run re-encodes up to ten docs/site_flow/307d_*.png -
restore main's bytes before committing (R5).

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-14, iteration 137, agent c - the driver returned the parent after 207a (done),
- `tasks/236-us-cities.md` (split)
- `tasks/241-us-birdseye-batch5.md` (in-progress) - hand-over: (2026-10-14, iteration 185, agent c) **Portland LANDING half-done: module edited + staged (5/5/5) + --verify clean + --check 5 PASS + --golden written - ALL UNCOMMITTED in the working tree (harness-saved). The lead doc, the tests, the suite and the close are still to do - specs below.**

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/236c-us-cities-merge.md`
- `tasks/239-retire-vision-fit.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-14 241 DECISION: iteration 181 - MEMPHIS RESEARCH complete (batch-5 city 4/5): the pick is the 1870 A. Ruger sheet (staged scan = the LOC 73694530 .jpg, 10400x6832, Public domain) - the steepest, best-scanned drawn whole-city view in the 42-row pool (the 1887 Wellge and the 1887 "Appeal" newspaper page are the only other drawn whole-city views - both dropped on angle/scan); the page date 1870 matches the banner (no Zwolle swap); Q16563 verified live with NO name-search trap (the search identified it directly this time - no first-guess QID from memory, so the mislabel trap class did not fire)
- QID (live Wikidata, /tmp/aw241_mem_qid.log, the wbgetentities pattern): **Q16563 = Memphis (Tennessee)**: label "Memphis", description "city in and county seat of Shelby County, Tennessee, United States". P625 = ONE value (-90.05194444444444, 35.14611111111111, precision 0.0002777777777777778 ~31 m) - the downtown core; no refinement. P373 = the STRING "Memphis, Tennessee" (the usual US string quirk) -> place "Shelby County, Tennessee" (P131 = Shelby County Q501602 ONLY - no multi-county like Columbus). P17 = Q30 (a proper entity). enwiki = "Memphis, Tennessee" -> https://en.wikipedia.org/wiki/Memphis,_Tennessee. Name search at limit 5 AND limit 20 (R5): **NO TRAP** - the first hit with P625 at BOTH limits is Q16563 itself (the #1 hit outright at both limits). No first-guess QID from memory was used this time (the search identified the city directly) - the 177/179 mislabel trap class (Q16556=Phoenix, Q1405=Augustus) did not fire. The other P625 hits that never come first: the other US Memphises - Q962034 Memphis (Missouri, a ghost town, 235.5 km from TN), Q979971 Memphis (Texas, 1166.4 km), Q67363 Memphis (Alabama, 195.1 km) (all measured with fit/evidence.hav_m - the pool mixes them, so every sheet was disambiguated from its caption: the state in the banner/LCCN), Q5715 Memphis (Egypt), Q19343442 (a street in Amersfoort, Netherlands), the University of Memphis (Q2094177, an in-city institution 12.8 km from the city point - the Pittsburgh/Chicago trap class, but it never comes first), Memphis International Airport (Q866831, in-city). No existing site holds Q16563 (grep: zero hits in data/catalog/sites.jsonl, extras.jsonl, 236a's extras_us_cities.jsonl, 236b's extras_us_birdseye.jsonl, 240's extras_us_birdseye_batch4.jsonl, this task's extras_us_birdseye_batch5.jsonl, web/data/sites.json; zero case-insensitive "memphis" in all of them). catalog.slug("Memphis") = "memphis" -> site id **memphis-q16563**.
- POOL (/tmp/aw241_mem_pool.json; the six plain-phrase forms + filetype:bitmap, srnamespace 6, srlimit 40; "bird's-eye view of Memphis" 21 / "bird's eye view of Memphis" 21 / "birdseye view of Memphis" 0 / "Memphis bird's eye" 40 / "Memphis birdseye" 0 / "Birds' eye view of Memphis" 21): **42 unique, 10 gate-pass** (keep + caption-names-Memphis + Public domain + >= 4000 px). The pool mixes the US cities named Memphis (TN dominates; the MO ghost town and the TX/AL small towns have no drawn views in the pool). ALL 10 good items eyeballed one by one (1280-px thumbs /tmp/aw241_mem_thumbs/; 1920-px corner/centre crops /tmp/aw241_mem_crops/ for the same-scan detection):
  - [0] "Memphis - Bird's Eye View - Memphis Appeal 15 October 1887.jpg" (10104x7320, PD, page date 1887-10-15) - the 1887 "Memphis Appeal" newspaper SUPPLEMENT page (a two-page spread with a centre fold, a printed title band across the bottom, woodcut quality): a drawn whole-city view from across the river (the steamboat landings a foreground band, the city up the bluffs, the plain beyond) but a newspaper page, not a lithograph sheet -> DROPPED (the 1870 Ruger is steeper and better scanned).
... (9.8 KB more: `grep -n -A 200 -F '## 2026-10-14 241 DECISION: iteration 181 - MEMPHIS RESEARCH complete (batch-5 city 4/5): the pick is the 1870 A. Ruger sheet (staged scan = the LOC 73694530 .jpg, 10400x6832, Public domain) - the steepest, best-scanned drawn whole-city view in the 42-row pool (the 1887 Wellge and the 1887 "Appeal" newspaper page are the only other drawn whole-city views - both dropped on angle/scan); the page date 1870 matches the banner (no Zwolle swap); Q16563 verified live with NO name-search trap (the search identified it directly this time - no first-guess QID from memory, so the mislabel trap class did not fire)' DECISIONS.md`)

### 2026-10-14 241 DECISION: iteration 182 - MEMPHIS LANDING (batch-5 city 4/5) executed: the 1870 A. Ruger sheet (LOC 73694530 .jpg, 10400x6832, Public domain) staged to memphis-q16563 - --verify clean (4 QIDs, NO FLAG/TRAP, first name-search hit = the city itself at both limits), stage "1 new sites, 1 new pictures" (no Zwolle swap - the page date 1870 = the banner year, the Omaha pattern), --check green ("evidence: 4 rows, 4 pass, 0 fail, 0 no-tie", zero join lines), lead doc (Memphis section: STAGED + the 42-item DROP list rebuilt item-for-item from the surviving /tmp/aw241_mem_pool.json + extra probes + QID facts + the 4-QID transcript) + golden (4/4/4) + tests extended, module tests 5/5 (2.4 s). REMAINING (harness cut the session at the context limit, before the full suite): the FULL suite run in-session (blocking, .venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider) + R5 (restore the re-encoded docs/site_flow/307d_*.png to main's bytes) + the commit of all seven changed files (module, lead doc, golden, test, the three staging files) - exact steps in the task hand-over
- Executed the 181 LANDING SPEC exactly (module edit -> --verify -> --dry -> stage -> --check -> lead doc -> --golden -> tests -> module tests; the session ended at the context limit before the full-suite step, which the hand-over now specifies verbatim).
- Module edit: SITES["Q16563"] (id memphis-q16563, point = the verified P625 -90.05194444444444/35.14611111111111, place "Shelby County, Tennessee", the enwiki URL, note = the staged view's true-oblique angle like the Columbus 1872 + the 2000 m box likely review item), RUGER_1870 (the LOC 73694530 .jpg row, EMPTY extra dict - no Zwolle swap, unlike Indianapolis), SOURCES["memphis_1870"] (label "the A. Ruger bird's-eye view (1870)"); header, SITES block and source-section comments all mark Memphis LANDED (city 4 of 5).
- --verify (live Wikidata, the session-10 run): 4 QIDs (Q16563, Q16567, Q43199, Q6346), the new Memphis row clean on every field, NO FLAG / TRAP lines (each single P625 IS the table point; the first name-search hit with P625 is the city itself at both limit 5 and 20 - the search identified Q16563 directly in the session-9 research, so no first-guess QID was used and the 177/179 mislabel trap class did not fire). Transcript verbatim in the lead-doc QID section and /tmp/aw241_mem_verify.log.
- --dry: "staged: 1 new sites, 1 new pictures" (the live commons.info re-check passes; the caption gate passes: the title prints "Memphis, Tennessee"; keep() judges 1870 PD 10400 px). The real stage: same output, 4th row appended to all three staging files (append-only idempotence held - no dupes of the first three rows).
- --check (offline): "evidence: 4 rows, 4 pass, 0 fail, 0 no-tie", ZERO join lines (no staged id or QID collides with an existing site; classified 1:1; no canonical-key clash). Verbatim in the lead-doc Staging section and /tmp/aw241_mem_check.log.
- Lead doc: the Memphis section (STAGED bullet with the full view description; the DROP list with all 10 gate-passes itemised - the 1887 Appeal newspaper page, the TSL 1873 reissue, the Forrest's-jail crop, the .tif twin, the "Memphis airview 1870" re-upload, the 1887 Wellge, the Cairo regional view x3 scans - and the 32 gate-fails grouped 26 keep-fails/6 gate-fails, rebuilt item-for-item from /tmp/aw241_mem_pool.json which survived loop maintenance; the three extra probes with all 11 new candidates eyeballed; the QID's facts incl. the three other US Memphises' measured distances; the 4-QID transcript; the Staging section at "4 views / 4 site rows"; Not-done-yet updated: New Orleans SKIPPED (236b's new-orleans-q34404), city 5 = the next city in the 181 list's order not staged anywhere).
- Golden regenerated 4/4/4 (the intended change: the 4th row; the Memphis row: date "1870", year 1870, NO date_commons, PD, 10400x6832, artist "Ruger, A.", evidence = caption_coords dist 0 at the site point).
... (1.0 KB more: `grep -n -A 200 -F '## 2026-10-14 241 DECISION: iteration 182 - MEMPHIS LANDING (batch-5 city 4/5) executed: the 1870 A. Ruger sheet (LOC 73694530 .jpg, 10400x6832, Public domain) staged to memphis-q16563 - --verify clean (4 QIDs, NO FLAG/TRAP, first name-search hit = the city itself at both limits), stage "1 new sites, 1 new pictures" (no Zwolle swap - the page date 1870 = the banner year, the Omaha pattern), --check green ("evidence: 4 rows, 4 pass, 0 fail, 0 no-tie", zero join lines), lead doc (Memphis section: STAGED + the 42-item DROP list rebuilt item-for-item from the surviving /tmp/aw241_mem_pool.json + extra probes + QID facts + the 4-QID transcript) + golden (4/4/4) + tests extended, module tests 5/5 (2.4 s). REMAINING (harness cut the session at the context limit, before the full suite): the FULL suite run in-session (blocking, .venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider) + R5 (restore the re-encoded docs/site_flow/307d_*.png to main's bytes) + the commit of all seven changed files (module, lead doc, golden, test, the three staging files) - exact steps in the task hand-over' DECISIONS.md`)

### 2026-10-14 241 DECISION: iteration 183 - MEMPHIS LANDING COMMITTED (batch-5 city 4/5): the full suite is green at EXACTLY the 178 baseline (190P/1S/0F over 191 tests once tests/test_gate.py's 3 tests are counted in - the hand-over's expected "190P" vs the run's "187P" is the 3 test_gate tests the 178 run included but the hand-over's --ignore command excludes; no regression, decomposition measured), R5 restored five re-encoded docs/site_flow/307d_*.png to main's bytes, and the city-5 pointer is resolved: the 181 candidate list ends with "..." after New Orleans, so the box-5 fallback applies (any US city with a usable LOC Panoramic view not staged anywhere)
- Session found the tree clean: the seven Memphis-landing files (module, lead doc, golden, test, the three 4/4/4 staging files) had already been saved by driver commit 986234a "[driver] uncommitted work after iteration 182" (the 182 session was cut at the context limit before committing; the harness/driver preserved them). Re-verified rather than trusting notes: `--check` offline green ("evidence: 4 rows, 4 pass, 0 fail, 0 no-tie", zero join lines, exit 0) and module tests 5/5 (2.29 s, socket-blocking).
- FULL SUITE (in-session, blocking, the 174 nohup-kill lesson): `.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider` -> **187 passed / 1 skipped / 0 failed** (542.84 s). The hand-over expected "the 190P/1S/0F baseline of 178" and said to re-grep if the counts differ - done. Investigation (AGENTS.md: check facts by running code): `git diff 8aedcac..HEAD -- tests/` (8aedcac = the 178 commit) shows only my two batch5 files changed; `--collect-only` collects 188 tests in BOTH the 8aedcac worktree and HEAD. The decomposition: the common base (everything except the batch4/batch5 module tests) = 178 tests in both eras; the 178 run = 178 common + 5 batch4 + 5 batch5 + 3 test_gate = 191 tests (its entry's "190P/1S/0F (191 = 186 baseline + 5 module tests)" - that "186 baseline" includes the 3 gate tests); the 183 run = 178 + 5 + 5 = 188 = 187P/1S/0F. The three tests/test_gate.py tests pass standalone on this tree (3 passed in 2.25 s) -> the complete picture = 190P/1S/0F over 191 tests, IDENTICAL to the 178 baseline: zero red, no regression. (240's closeout note "suite 172 = 185P/1S/0F (baseline + 3 new main tests)" uses agent-a's own checkout counts at its merge point - 186 = 178 common + 5 batch4 + 3 gate fits; its "172" is not reconstructable from main's history and is immaterial - my two runs decompose exactly.)
- R5: this run re-encoded four of the ten docs/site_flow/307d_*.png (A_1-card, A_4-saved, A_5-reload, B_5-reload); B_1-card had already been committed on agent/c in a re-encoded form by an earlier run (it differed from main before this session's run). All five restored to main's bytes (`git checkout main -- docs/site_flow/307d_*`); docs/site_flow/ now matches main byte-for-byte (the PITFALLS test_owner_check entry: the re-encoding is machine-specific, never a content change).
- Committed the Memphis landing (the seven files were driver-saved, so this commit is the five restored PNGs + this entry + the hand-over rewrite).
... (14.4 KB more: `grep -n -A 200 -F '## 2026-10-14 241 DECISION: iteration 183 - MEMPHIS LANDING COMMITTED (batch-5 city 4/5): the full suite is green at EXACTLY the 178 baseline (190P/1S/0F over 191 tests once tests/test_gate.py's 3 tests are counted in - the hand-over's expected "190P" vs the run's "187P" is the 3 test_gate tests the 178 run included but the hand-over's --ignore command excludes; no regression, decomposition measured), R5 restored five re-encoded docs/site_flow/307d_*.png to main's bytes, and the city-5 pointer is resolved: the 181 candidate list ends with "..." after New Orleans, so the box-5 fallback applies (any US city with a usable LOC Panoramic view not staged anywhere)' DECISIONS.md`)

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
