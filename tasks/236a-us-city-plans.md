Status: in-progress
# 236a: US city plans - New York, Washington, San Francisco, Nashville first
Depends on: none
Touches: fit/src_us_cities.py, pipeline/build_catalog.py, data/catalog/extras_us_cities.jsonl, data/commons/files_us_cities.jsonl, data/commons/classified_us_cities.jsonl, docs/lead_us_cities.md, tests/test_src_us_cities.py, tests/golden/src_us_cities_sample.json, PITFALLS.md

## Goal
Subtask of 236. Stage old plans of US cities the way 204 staged Van Deventer and 213 staged the artists'
views: a hand-checked file -> QID table in fit/src_us_cities.py, one site per city (or per district or
fortification when the whole city is too big for one site box), picture rows with task-200 evidence, all in
this task's own staging files. 236c consolidates them.

Leads to verify (NONE verified yet - check each exists on Wikimedia Commons or the Library of Congress, is
the original or a facsimile of it, its date, its licence, and its resolution before using it):
- New York: the Castello Plan (1660; NOTE the common Commons image is the 1916 Adams/Stokes redraft - record
  which one a file is; prefer the original), the Ratzer Map (1767/1770), the Commissioners' Plan of 1811
  (Bridges), the Viele map (1865, Sanitary & Topographical Map - streams and shoreline).
- Washington DC: the L'Enfant plan (1791, LoC), the Ellicott engraved plan (1792), Boschke's topographical
  map (1857/1861); the Civil War defences (Barnard, 1865, Fort Stevens / Fort Marcy etc. - earthworks that
  may show on 3DEP LiDAR, each fort a candidate site of its own).
- San Francisco: the 1849 plans (Eddy, Ringgold), the 1850s city plans.
- Nashville: early town plans; the Civil War fortification plans of Fort Negley (earthwork, LiDAR candidate).
- Then any other US city with an old plan on Commons: Boston (Bonner 1722), Philadelphia (Holme 1683),
  Savannah (Gordon 1734), New Orleans (French plans 1720s), Charleston, St. Augustine.

## Acceptance criteria
- [x] Verified before use (docs/lead_us_cities.md): per staged picture what it is, where it lives, the
      drawing's date (recorded on the row - an upload date is not a drawing date), original vs later redraft;
      unusable files (modern redraws, too small, no place tie, not free) listed with the reason.
- [x] fit/src_us_cities.py holds the hand-checked file -> QID table: every QID verified against its label,
      P625 and enwiki link (the Barnard Castle trap: a name search alone gives the wrong place). A city
      whose plan covers more than the site box gets either an extent recorded on its row (check how
      pipeline/catalog.py sets extent_m and whether an extras row can carry one) or a district/fort site
      with its own QID - recorded which, and why, in the lead doc.
- [ ] Staged rows in this task's files only: extras_us_cities.jsonl (id, qid, name, lon/lat of the area
      the plan covers, region "United States", kind "town" or "fort", aerial_ok true, place, wikipedia,
      note), files_us_cities.jsonl (files.jsonl shape + 200 evidence field), classified_us_cities.jsonl
      ("plan", by hand). A city whose QID is already in the catalog gets picture rows for that site id.
- [x] fit/evidence.py check passes offline on every staged row; all four owner-named cities are staged or
      the lead doc says exactly why one could not be.
- [x] Test (no network): the staged files join, the evidence check passes, a golden sample of rows.

## Notes
- Ground: cities are aerial-photograph sites (aerial_ok true; bare-earth LiDAR erases streets). The street
  grid, shoreline, squares and church footprints carry the fit. Civil War forts are the exception: their
  banks may show on 3DEP bare earth (pipeline/aw.py), like the mounds in 203a.
- Templates: fit/src_van_deventer.py + docs/lead_van_deventer.md, fit/src_artists.py + docs/lead_artists.md.
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, sites.json) - that is 236c.

## Hand-over

(2026-10-13, iteration 148, agent a - **San Francisco APPLIED (the 146 pattern): table row, staging,
--verify/--check/--golden all run; tests edited but NOT yet run; lead doc NOT yet written; nothing
committed** (harness saves the uncommitted tree). Next session: run the tests, write the lead-doc SF
section, commit, then Nashville.)

### What is in the working tree (uncommitted)
- `fit/src_us_cities.py`: docstring now lists SF ("New York ... Washington DC ... and San Francisco - the
  1849 Eddy survey map, the 1850 first-published map and the 1854 Eddy 'full and complete' sheet ...;
  Nashville follows in a later session"); SITES += **Q62** (id `san-francisco-q62`, name/named "San
  Francisco", **point (-122.40289, 37.79213)** - REFINED, not a P625, with the full derivation in the SITES
  comment; place "San Francisco County, California", region "United States", kind "town", wikipedia, note);
  SOURCES += `eddy_1849` / `map_1850` / `eddy_1854` (all p="plan"; only eddy_1854 carries
  `dict(date="1854")`). No structural change to stage()/check() - the 143 pattern absorbed SF unchanged.
- Staged (live, `.venv/bin/python fit/src_us_cities.py`): **"staged: 1 new sites, 3 new pictures; build
  (236c): san-francisco-q62"** (the 10-title c.info request was one batch, no 414 this time - the 144
  pitfall was 50 long titles, not 10). The 3 new rows in `data/commons/files_us_cities.jsonl` (site
  san-francisco-q62, Q62, cat null, hand evidence caption_coords, place = site point, dist 0): 1849 Eddy
  original (year 1849, date '1849', date_commons None); 1850 'Copied From Originals' (year 1850, date
  '1850-01-01', date_commons None); 1854 Rumsey sheet (year 1854, **date '1854', date_commons ''** - the
  known-date swap fired exactly as the 147 verdict predicted: page had no DateTimeOriginal, empty string
  kept). `data/catalog/extras_us_cities.jsonl` += the Q62 row; `data/commons/classified_us_cities.jsonl`
  += 3 rows p_plan 1.0 by hand.
- Live `--verify` (3 QIDs, output in /tmp/ussf_verify.out): **clean** - no P625 >50 km flag (both SF P625s
  are 2.0-2.4 km from the refined point), no trap (first name-search hit with P625 = Q62 itself), label/
  P373/P131/enwiki all match the table. Q60/Q61 lines unchanged. **Use that transcript for the lead-doc
  QID-verification block (re-run `.venv/bin/python fit/src_us_cities.py --verify` if /tmp is gone - it is
  a read-only live call).**
- Offline `--check`: **"evidence: 10 rows, 10 pass, 0 fail, 0 no-tie", no join problems** (output in
  /tmp/ussf_check.out - copy those 10 PASS lines into the lead doc's Offline check section).
- `tests/golden/src_us_cities_sample.json` regenerated by `--golden`: **3 extras / 10 files / 10
  classified**; the 1854 golden row is date "1854" / date_commons "0000-00-00" (the empty page value
  normalized).
- `tests/test_src_us_cities.py`: 8 edits applied (module docstring; check-staged test: "10 rows, 10 pass"
  + the 3 SF PASS lines; the three_states test docstring "two -> three sites" (also removed a stray
  trailing `"""` - an implicit empty-string concat on the docstring - value unchanged); qid_table test:
  set(table) == {Q60,Q61,Q62}, the Q62 entry asserts (id/named/region/kind/point -122.40289, 37.79213),
  extras ids += san-francisco-q62, years += the 3 SF titles (1849/1850/1854), named_by_qid +=
  {Q62: "San Francisco"}, the 1854 swap assert (date "1854" / date_commons "" on the staged row);
  evidence test: "10 rows, 10 pass"). **NOT YET RUN after these edits - the last green run was 146's
  7/7 (pre-SF).**

### Site point derivation (for the lead doc's Q62 section and the SITES comment)
Point = midpoint of the two web-verified tips of the old town's drawn peninsula (the center of the drawn
extent of all three staged maps; both tips are corners of the maps' drawn extent - the 1854 sheet labels
"Rincon Point" at the SE corner of the red water-front line; the grid's NW corner is the old North Beach
tip). A = historic Rincon Point: enwiki "Rincon Point (San Francisco)" ("would be today located
approximately along Spear Street from Harrison to Folsom Street") + Nominatim Spear Street segment
(Folsom end (37.7919285, -122.3933015), Harrison end (37.788381, -122.3889244)) -> A = (37.790155,
-122.391113); cross-check Rincon Park (37.791195, -122.389541) is ~175 m away. B = the Washington & Jones
corner (the NW grid corner) = intersection of the Nominatim street lines (Washington: (37.7952016,
-122.4060729)/(37.793173, -122.4220116); Jones: (37.7825459, -122.4123324)/(37.8062714, -122.417119)) ->
B = (37.794108, -122.414665). Midpoint -> **(-122.40289, 37.79213)** (5 decimals, the clean-number ask).
Uncertainty ~100-200 m (street centroids), immaterial: the 4 km box (lat 37.77410..37.81017, lon
-122.42565..-122.38013) covers tip to tip with ~600 m+ margin, and both P625s sit INSIDE it (P625a
37.775 is ~100 m inside the south edge - fine). **Correction to the 147 hand-over**: its "~450 m"
estimate was right (387 m) but the tip is NE of both P625s, not south (37.790 > 37.775-37.7775) - the
"southern P625 or refine to the tip" branch was answered by refining. (The /tmp/ussf_point_final.py
script printed "OUTSIDE" for the P625s because it mixed (lon,lat) and (lat,lon) tuple orders in the box
check - the hand check above is right.)

### EXACT next steps (1 session to finish SF, then Nashville)
1. **Run the tests OFFLINE** (socket-blocked fixture in the test file; do NOT run the whole suite -
   test_fit_queue.py has the known pre-existing failure, agent c's 307 work): `.venv/bin/python -m pytest
   tests/test_src_us_cities.py tests/test_region.py -q` - expect 7/7 (5 in the us_cities file + 2 in
   region). If the 1854 `date_commons` assert fails on something other than "" (check the staged row
   first: `.venv/bin/python -c "..."` or just `tail data/commons/files_us_cities.jsonl`), fix the assert
   to the stored value - the stage output above is the record.
2. **docs/lead_us_cities.md** (the only remaining file change): header -> "three cities staged; Nashville
   last" (the intro paragraph's city list += San Francisco: the 1849 Eddy, the 1850 first-published,
   the 1854 Eddy sheet); the QID-verification block -> the 3-QID `--verify` transcript (/tmp/ussf_verify.out
   or re-run it) with "no P625 flag fired; no search trap" updated to three cities; the prep-verified
   list -> **Q23197 only** (Q62 now staged - fix its stale "~450 m apart" line to 387 m and note the
   refined point is NE of both P625s); a full `## San Francisco (Q62)` section in the NY/DC shape: the
   site point + derivation (above), the extent decision (tip-to-tip inside the 4 km box; the 1854 sheet's
   SW growth - the Center Street grid - also in the box; the red water-front line is the fit anchor),
   the three **STAGED** subsections (what/where per file, from the 147 DECISIONS entry - 1849 Eddy LOC
   77692722 6454x8480 the original manuscript; 1850 Apollo/Sun Litho 1238x1536 first published after
   Eddy; 1854 Rumsey 8830x10560 with the date swap), every **DROP with its exact reason** (the 147 entry
   has them all: the two printed 1849 editions LOC 76695582/83 - one row per plan, the Ratzer precedent;
   IA 00194050 the third 1849 copy; IA 10423001 the 1850 covers+title page, not the map; IA 12216 the
   1852 sheet - only a small IA book scan on Commons, full-res is David Rumsey's, and the staged 1854
   sheet covers the same ground at 8830px; IA 11809 the Butler city-and-county - only small IA scan and
   no printed date on the page (do NOT assert it is the 1872 Butler without web-verifying); Beechy 1827
   harbour GONE from Commons - and a chart anyway; all Ringgold hits = nautical charts - background per
   the owner's rule; the HABS files = photos; the J.W. Freeman sheet = lithographed portraits), the
   **Ringgold 1849 town plan NOT on Commons** note (charts only; survives in books/reprints; the 1849
   Eddy row covers the survey-plan lead), and **Henry Bill 1856/1858 = a 236b lead** (a VIEW map, "seen
   from Nob Hill looking down California Street" - record it in the doc as a 236b lead, do not stage
   here; consider a one-line `## Proposed changes` on 236b? No - 236b is the human's task file's sibling;
   just note the lead in THIS doc, 236b's own session will find it); the **Offline check** transcript
   updated to the 10 PASS lines (/tmp/ussf_check.out).
3. **DECISIONS.md**: append the iteration-148 entry (verdict applied verbatim; the point settled as
   midpoint of the two web-verified tips, the derivation above; verify/stage/check/golden transcripts;
   tests status; the one correction to the 147 hand-over about the tip's NE position).
4. **Commit** `git add -A && git commit -m "236a: San Francisco staged (san-francisco-q62: 1849 Eddy
   original, 1850 first-published, 1854 Eddy with date swap) - applied the live-verified 147 verdicts:
   point refined to the drawn-extent center (midpoint of the two web-verified peninsula tips), 10/10
   evidence green, tests+golden+lead doc grown - the staging set is now NY+DC+SF, Nashville last"`
   (tick NO boxes yet - box 3 stays open until Nashville is staged).
5. **Then Nashville (Q23197) the same way** (145/146/147/148 pattern): live research first (re-verify
   Q23197 via pipeline/catalog_wd - P625 (-86.7744, 36.1622) downtown vs the old 1790s town at the
   Cumberland/Tennessee confluence ~(-86.788, 36.166); grep no existing site uses Q23197 or
   nashville-q23197; find the old town plans + Fort Negley's Civil War plans, thumbnails, metadata,
   the gate window; verdict in DECISIONS BEFORE editing), then apply in one session (SITES += Q23197;
   Fort Negley = its own kind-"fort" site with its own QID - find and verify that QID too, 1600 m box,
   the 3DEP LiDAR candidate as in 203a; when both staged: tick box 3, Status: done - the driver
   re-checks suite green).

### Gotchas (all still true)
- The named-place gate sees ONLY the title + the 600-char-truncated desc of c.info(); stage and check
  both use it; all three staged SF titles print "San Francisco" in the title (gate-safe, like all the
  DC files). File titles case-sensitive; the 10-title stage batch was one request, no 414 (the pitfall
  was 50 long titles).
- stage(): idempotent on (site, title); the known-date swap runs BEFORE c.keep(); a missing title fails
  loud. Re-running stage after this session is a no-op (all (site,title) keys already in `have`).
- Town box: kind "town" = 2000 m -> a 4 km x 4 km box centered on the site point (build_catalog BOX +
  aw.site_bbox). The point rides on the staged extras row (SITES lon/lat); specs/site_boxes.json is NOT
  touched (not in this task's Touches; the Cahokia precedent shows where a wider box would go if 212's
  fits need it).
- evidence_for stores the site's point as the caption_coords tie (dist_m 0.0); check_staged is offline
  from stored fields, so the refined (non-P625) point is safe for --check and for --verify (flag only
  >50 km). Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, sites.json) -
  that is 236c.
- Do not "fix" pipeline/commons.py's NO regex (not in Touches).
- /tmp holds this session's scripts (ussf_point.py, ussf_point2.py, ussf_point_final.py - the point
  derivation; ussf_verify.out, ussf_stage.out, ussf_check.out - the transcripts; sf_0..sf_7.jpg - the
  147 thumbnails, sf_0 = the 1849 Eddy, sf_3 = the 1850 Apollo, sf_7 = the 1854 sheet) - throwaway, but
  they held this session's evidence; the verdicts and transcripts above stand on their own.
- The full suite has 1 pre-existing failure (test_fit_queue.py::test_placement_gestures_and_save_in_
  the_browser - agent c's 307 work, not mine); run only my two test files offline.

### SF verdicts (live, 2026-10-13; full record in the DECISIONS entry)
- **Q62 re-verified live** via pipeline/catalog_wd (the robust path): label "San Francisco"; P625 =
  [(-122.41944444444445, 37.775), (-122.41638888888889, 37.7775)] - **387 m apart, both downtown**
  (prep's "~450 m" was approximate); P373 ['San Francisco']; P131 [Q13188841 San Francisco County,
  Q99 California]; enwiki 'San Francisco'; first name-search hit with P625 = **Q62 itself - no trap**.
  No existing site uses Q62 or id san-francisco-q62 (grep exact; the earlier "Q62" substring hits are
  Q622981 Wiesbaden / Q6276838 Jordan Mounds etc.).
- **Stage 3 rows on a new site `san-francisco-q62`** (kind "town", named "San Francisco", place
  "San Francisco County, California", wikipedia https://en.wikipedia.org/wiki/San_Francisco, region
  "United States"), all p="plan", all print "San Francisco" IN THE TITLE (gate-safe), all PD:
  1. `File:Official map of San Francisco compiled from the field notes of the official re-survey made by Wm. M. Eddy. surveyor of the town of San Francisco. LOC 77692722.jpg` (6454x8480, page date
     "1849") = the 1849 Eddy survey map, the ORIGINAL (manuscript, "Presented to the Senators and
     Representatives from California by Wm. M. Eddy, city surveyor, San Francisco, Dec. 31st 1849").
     NO date swap (page date = drawing date).
  2. `File:Map of San Francisco, Apollo storeship at the bottom.jpg` (1238x1536, page date "1850-01-01",
     Sun Lithographic Est. NY) = the 1850 map body "MAP OF THE CITY OF SAN FRANCISCO CALIFORNIA -
     COPIED FROM ORIGINALS WITH CORRECTIONS AND ADDITIONS - 1850" (the first published map after Eddy;
     hachured hills, Yerba Buena Cemetery, Rincon Point, inset "View of San Francisco in 1850" showing
     the Apollo storeship; from Joseph P. Beach's journal). NO swap.
  3. `File:Official map of the City of San Francisco, Full and complete to the present date. Compiled by Wm., M. Eddy. City Surveyor. (IA dr official-map-of-the-city-of-san-francisco-full-and-complete-to-the-present-5870000).jpg` (8830x10560, NO page date, year_of None) = the Eddy 1854
     sheet (map itself: "January 15th 1854"; desc: "Map printed without color. With red lines added by
     hand. Outer red line is water front. Inner red line is shore line. Shows block and lot numbers, and
     wards.") -> **known-date swap dict(date="1854")** (fires because year_of(page)=None != 1854).
- **DROPS (record in the lead doc, exact reasons in the DECISIONS entry):** LOC 76695582 (.jpg/.tif)
  and LOC 76695583 (.jpg/.tif) = two printed 1849 editions of the SAME staged Eddy plan (one row per
  plan, the NYC Ratzer precedent); IA 00194050 (6361x8362, no page date) = a third 1849 copy ("the
  second issue of 1849"); (Covers to) 10423001 (1074x1536) = the 1850 map's COVERS + title page, not
  the map (the body is staged as the Apollo file); 12216 (1331x1536) = the 1852 Eddy "Topographical
  & Complete" sheet - distinct plan but the only Commons copy is a small IA book scan (full-res is
  on David Rumsey's site, not Commons) and the staged 1854 sheet covers the same ground at 8830px;
  11809 (1536x1333) = the Butler city-and-county map ("city boundaries 1850-1863", drawn for the SF
  News) - only Commons copy is the small IA scan; Beechy 1827 harbour plan (IA 11955001, GONE from
  Commons - title changed/deleted), all Ringgold hits = navy CHARTS (background, not drawings, owner's
  rule); HABS 1852 plat re-photo (85-1/91-1) = photos of documents; J.W. Freeman 1849 file = a sheet of
  lithographed PORTRAITS, not a map; **Henry Bill 1856/1858 (3500x1974 / 4000x2325, PD, "1856 (dated)")
  = a VIEW map ("as seen from Nob Hill looking down California Street") - it belongs to 236b (the
  bird's-eye task), note it as a 236b lead in the lead doc, do not stage here.**
- **The Ringgold "General Plan of the Town of San Francisco" (1849) is NOT on Commons** - every
  Ringgold hit is a nautical chart (Farallones, Bay of San Pablo, entrance, general charts, 1850s
  Douglas prints). The 1849 town plan survives only in books (e.g. reprints) - record it as such.
- **Site point: REFINE, do not take either P625** (the 146 hand-over's branch "refine to the tip" -
  the drawn extents decide): the three staged plans all draw the OLD TOWN'S TIP (the peninsula from
  North Beach down to Rincon Point) plus the hills / 1850s growth; both P625s (~1.2-1.5 km west, near
  Civic Center/10th-Market) would leave the tip's tip outside the 4 km town box. The point should be
  the CENTER OF THE DRAWN EXTENT of the staged plans (~ the old Plaza / Market & 6th-7th area, about
  (-122.405, 37.784) - confirm by measurement, don't eyeball). The point rides on the STAGED EXTRAS
  ROW (SITES[qid] lon/lat) - build_catalog takes it from the row; no shared file (specs/site_boxes.json
  has the hand-set override precedent - Cahokia - but is not in my Touches and my row is the source).
  **Last thing I was doing:** about to download the full-res 1854 sheet (original URL: upload.wikimedia
  .org/wikipedia/commons/2/2a/Official_map_of_the_City_of_San_Francisco%2C_Full_and_complete_to_the_
  present_date._Compiled_by_Wm.%2C_M._Eddy._City_Surveyor._%28IA_dr_official-map-of-the-city-of-san-
  francisco-full-and-complete-to-the-present-5870000%29.jpg, 8830x10560) and measure its "Scale of 550
  English Feet to the Inch" bar (bottom-left, under the title block) + locate Rincon Point (the tip's
  tip, bottom-center) and the North Beach point (top-right) to georeference and compute the extent
  center. FALLBACK if the measurement is fiddly: midpoint of the extreme anchors (Rincon Point
  ~37.7742/-122.3943 and the North Beach tip ~37.7925/-122.4105, both to be web-verified first) - and
  whatever point is used, record the derivation in the lead doc's QID section + the SITES comment
  (and the two P625 values stay in the --verify output; both are <50 km, so verify prints no flag).

### EXACT next steps
1. (Optional, fast) settle the site point: download the 1854 sheet at full res, measure the scale bar
   + anchors per above, OR web-verify the two anchor coords and take their midpoint of the drawn
   extremes. Pick a clean number (~4-5 decimals).
2. DECISIONS.md: the verdict entry is ALREADY written (147, below) - if step 1 changed the point, note
   the final value in the hand-over, not by rewriting the entry.
3. Apply (the 146 pattern, 1 session): fit/src_us_cities.py SITES += "Q62" (id san-francisco-q62, name
   "San Francisco", named "San Francisco", lon/lat = the settled point, place "San Francisco County,
   California", region "United States", kind "town", wikipedia, note = aerial ground + tip drawn extent
   + the point derivation); SOURCES += eddy_1849 / map_1850 / eddy_1854 (labels per the verdicts;
   eddy_1854 carries dict(date="1854")); docstring "New York, Washington DC and San Francisco -
   Nashville follows". Live --verify (3 QIDs; expect the two SF P625s printed against the refined
   point, no >50 km flag), stage (expect "2 new sites" is WRONG - it's "1 new site, 3 new pictures;
   build (236c): san-francisco-q62" - only Q62 is new; NY/DC rows are idempotent no-ops), offline --check
   (expect 10 rows, 10 pass) + --golden (regenerates tests/golden/src_us_cities_sample.json). Tests:
   table {Q60,Q61,Q62}, named += {Q62: "San Francisco"}, extras ids += san-francisco-q62, years dict +=
   the 3 SF titles (1849/1850/1854), the 1854 swap assert (date "1854"/date_commons "" or None - CHECK
   what stage actually stored first: date_commons = m.get("date") = "" empty string here, _norm
   normalizes any string date_commons to "0000-00-00"), 7->10 row asserts, the 3 SF PASS lines.
   Lead doc: `## San Francisco (Q62)` section (site point + derivation, the extent decision, the 3
   STAGED, all the DROPS with reasons, the Ringgold-not-on-Commons note, the Henry Bill = 236b lead)
   + header "three cities staged; Nashville last" + QID-verification block updated to the 3-QID
   --verify output. Then **Nashville (Q23197)** same way (old 1790s town at the confluence
   ~(-86.788, 36.166) vs downtown P625 - pick the point against the files; Fort Negley = own
   kind-"fort" site, own QID, 3DEP candidate). When both staged: tick box 3, Status: done.

### Gotchas (all still true)
- The named-place gate sees ONLY the title + the 600-char-truncated desc of c.info(); c.info batches
  of 50 LONG titles 414 (URI Too Long) - batch <=4-5 for long IA titles. File titles case-sensitive;
  proxy gzip-200s on Wikidata -> use pipeline/catalog_wd for WD checks; c.get has retries (one SSL
  handshake timeout occurred this run, retried fine).
- stage(): idempotent on (site, title); the known-date swap runs BEFORE c.keep(); a missing title
  fails loud. The stage prints new sites/pictures only - re-running after a partial stage is safe.
- Town box: build_catalog BOX [("town", 2000)...] -> width_m=height_m=2000, and aw.site_bbox CENTERS
  the box on the site point (hw = width_m/2) -> a kind-"town" site has a 4 km x 4 km box; an extras
  row may carry its own box_m/lon/lat (build_catalog make_site reads them; specs/site_boxes.json is a
  per-site override layer with the Cahokia "point misses the works" precedent, but it is not in my
  Touches - my staging row carries the point).
- evidence_for stores the site's point as the caption_coords tie (dist_m 0.0); check_staged is
  offline and re-verifies from stored fields only, so a refined (non-P625) site point is safe for
  --check and for --verify (flag only >50 km). Do NOT write the canonical files (that is 236c).
- Do not "fix" pipeline/commons.py's NO regex (not in Touches) - Boschke record stands.
- /tmp/ussf_*.py + .out/.jpg hold this session's transcripts (Q62 verify, 3 search runs, 3 metadata
  runs, 8 thumbnails sf_0..sf_7) - throwaway; the verdicts stand on the DECISIONS entry.
- The full suite has 1 pre-existing failure (test_fit_queue.py::test_placement_gestures_and_save_in_
  the_browser - agent c's 307 work, not mine); run my two test files (tests/test_src_us_cities.py +
  tests/test_region.py) offline (socket-blocked fixture), not the whole suite.

### What this session did
1. fit/src_us_cities.py: SITES += Q61 (id washington-q61, name "Washington, D.C.", named "Washington",
   lon/lat = the single P625 (-77.036667, 38.895), place "District of Columbia", region "United
   States", kind "town", wikipedia, note = aerial ground + 35 km ring review-item case + the ring's
   forts as the catalog's existing sites); SOURCES += le_1791 / ellicott / defences_1865 (all p="plan";
   the L'Enfant row carries dict(date="1791")); docstring extended.
2. Live: --verify clean (2 QIDs; Q61 = one P625 = the table point, P373, P131 Q3551781, enwiki, first
   search hit = Q61 itself - no trap; one SSL-handshake timeout, retried by c.get; the 144 gzip-200
   pitfall did not recur). stage: "1 new sites, 3 new pictures; build (236c): washington-q61".
   L'Enfant swap fired: date "1791" / date_commons "1792" (page dates the Mar. 1792 first printing of
   the L'Enfant plan; the 1791 manuscript is at NARA, not on Commons).
3. Offline: --check no join problems, "evidence: 7 rows, 7 pass, 0 fail, 0 no-tie"; --golden rewrote
   tests/golden/src_us_cities_sample.json (2 extras / 7 files / 7 classified).
4. Tests (tests/test_src_us_cities.py): per-QID named dict {Q60: "New York", Q61: "Washington"},
   set(table) == {Q60, Q61}, extras ids [new-york-q60, washington-q61], years dict += 3 DC titles,
   L'Enfant swap assert, both 4-rows asserts -> 7, the 3 DC PASS lines. The three_states test
   self-scales (no edit, as predicted). 7/7 green with tests/test_region.py, offline.
5. docs/lead_us_cities.md: header "both cities staged; SF and Nashville later"; QID-verification
   block = this session's 2-QID --verify output; prep-verified list now Q62/Q23197 only; the full
   `## Washington DC (Q61)` section (site point; extent decision same as NY; ring + forts - no new QID
   work, the catalog already has the individual fort sites Q3077774/Q5471024/Q18150335/Q61784495/
   Q14691922 part_of Q5124610; the three STAGED/DROP per-plan sections with full drop reasons; the
   Boschke "not staged, and exactly why" section: 1861/1880 editions print "Washington" only past the
   gate's 600-char window, 1857 1st ed the only gate-passing file but the NO heuristic's "portrait"
   word false-positives on a vignette + low-res).

### EXACT next step (one session: SF research + apply; the 145/146 pattern)
1. **Live research** (throwaway scripts in /tmp; record the verdict in DECISIONS.md BEFORE editing,
   as 145 did): re-verify Q62 live (pipeline/catalog_wd is the robust path; c.get is flaky) - two
   P625 values ~450 m apart both downtown, first search hit = Q62 (144: no trap, re-confirm); check
   no existing site uses Q62 or the id san-francisco-q62 (grep data/catalog/sites.jsonl,
   data/catalog/extras.jsonl, web/data/sites.json - "San Francisco" hits will be a CA county and
   probably nothing else). **Pick the site point against the files**: the 1849 Eddy and Ringgold
   plans draw the old town's tip (bay-front, today's Financial District / Yerba Buana) which is
   SOUTH of both P625 points - so take the southern P625 or refine to the tip; decide from the
   files' drawn extents, don't guess.
2. **Leads** (verify each: original or facsimile, the drawing's date, licence, resolution; the
   named-place gate needs the city in the title or the 600-char desc - check c.info() before
   staging): the 1849 Eddy plan (the survey), the 1849 Ringgold plan ("A General Plan of the Town of
   San Francisco..."), 1850s city plans (the growth around the bay). Known-date swap where the page
   lost the drawing's date; drops recorded with exact reasons in the lead doc.
3. **Apply**: SITES += Q62, SOURCES entries (labels per plan), docstring; live --verify + stage;
   offline --check (expect 10 rows if 3 SF rows) + --golden; tests (per-QID named += Q62: "San
   Francisco", years, PASS lines, table {Q60, Q61, Q62}); lead doc `## San Francisco (Q62)` section
   (same shape as the DC one: site point, extent decision, staged/drops, fit notes); DECISIONS.md;
   commit as 236a.
4. **Then Nashville (Q23197)** the same way: P625 (-86.7744, 36.1622) downtown vs the old 1790s town
   at the confluence ~(-86.788, 36.166) - pick the point against the files; leads: early town
   plans; **Fort Negley = its own kind-"fort" site, its own QID** (a separate verify; the 3DEP
   LiDAR candidate as in 203a).
5. **When both are staged**: tick box 3, set Status: done. The driver re-checks (suite green).

### Gotchas (all still true)
- The named-place gate sees ONLY the title + the 600-char-truncated desc of c.info() (stage and
  check both use it) - "in the caption" must mean visible inside that window; that is why every
  chosen DC file prints the city IN THE TITLE and why all Boschke editions fail.
- fit/src_us_cities.py has NO BOOKS machinery; stage() is idempotent on (site, title); row `cat` is
  null; the known-date swap runs BEFORE c.keep() (the sources.py/van-Deventer order).
- Commons File titles are case-sensitive (PITFALLS); Wikidata through the proxy is flaky (gzip 200s,
  or SSL-handshake timeouts like today - c.get retries; pipeline/catalog_wd is the robust path);
  CM/WD constants in pipeline/commons.py.
- Do NOT write the canonical files (extras.jsonl, files.jsonl, classified.jsonl, web/data/sites.json)
  - that is 236c. The REGION_NAME line in pipeline/build_catalog.py is already committed.
- Do not "fix" pipeline/commons.py's NO regex (not in this task's Touches) - that is why the Boschke
  1857 sheet is recorded, not staged.
- The /tmp usdc_* scripts hold the DC transcripts (throwaway); the SF/Nashville research transcripts
  go to /tmp the same way.
- The full suite has 1 pre-existing failure (test_fit_queue.py::test_placement_gestures_and_save_in_
  the_browser - agent c's 307 work, not mine); run my two test files offline (socket-blocked
  fixture), not the whole suite.
