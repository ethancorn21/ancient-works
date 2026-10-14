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

(2026-10-14, iteration 191, agent a) **Batch 3, city 2 = NEW ORLEANS: QID research + pool search + the pick (1851 Bachman NYPL tif) DONE and verified; the orientation of the view is the one open question - next session lands the city (module + stage + doc + golden + tests).**

### State (tree was clean at session start)

- Kansas City (batch 3 city 1) LANDED and committed by the driver's sweep 7771bc6 (iteration 190's work): module 15 cities, 11 site rows / 22 file rows / 22 classified rows, lead doc at 15 cities / 22 views, golden + tests at 22 rows.
- Re-verified this session: offline `--check` exit 0, 22/22 PASS (transcript /tmp/aw236b_check_191.txt); module tests 5/5 (2.29 s). After New Orleans lands: 16 cities / 23 views / 12 site rows; golden 12 extras / 23 files / 23 classified.
- New Orleans not in any existing site data (checked data/catalog/sites.jsonl, extras.jsonl, extras_us_cities.jsonl, web/data/sites.json); 236a stages only the four owner cities, so extras_us_birdseye.jsonl is the right home (no QID clash possible).

### QID = Q34404 (verified live this session; NOT Q717 - that is Venezuela)

- label "New Orleans", enwiki "New Orleans". **P625: exactly ONE normal-rank value (-90.078333, 29.976111), precision 0.000278 deg (30 m)** - table point = that P625 (dist 0). The point sits in the city's north part (the City Park area, ~2.3 km N of the CBD).
- **P373 = the STRING "New Orleans" (the same Wikidata quirk as Kansas City Q41819 - not a country entity; write the place from P131 + the state, not from P373).** P131 = Q486231 Orleans Parish (SINGLE - New Orleans is a consolidated city-parish) -> place "Orleans Parish, Louisiana". P17 = Q30 (United States) (a proper entity, unlike P373).
- **Name search "New Orleans" (what --verify resolves): NO TRAP** - first hit with P625 is Q34404 itself (dist 0). Search order of the ten hits: Q34404 (city, P625), Q1474157 "LSU New Orleans" (P625 (-90.0671, 30.0275) ~5.7 km - NOT the first hit, in the 50 km flag so not a trap either), Q172339 Pelicans (no P625), Q135264429 (no P625), Q172435 Saints (no), Q170649 Utah Jazz (!, no), **Q2522995 "New Orleans (Rotterdam)" - a BUILDING in Rotterdam (enwiki "New Orleans (Rotterdam)", P625 (4.487222, 51.904722), P373 the string "New Orleans building, Rotterdam") - 7725 km ENE of the city point (measured: 9109 km east + 2432 km north, bearing ~75 deg)** - record in the SITES comment; Q27720369 journal, Q3875298 1929 film, Q61794189 horse (none with P625 except the two above).

### Pool + the pick (research scripts + thumbs in /tmp, may be wiped - regenerate)

- Builders: /tmp/aw236b_b3_no.py (the 6 standard plain-phrase forms, CITIES=["New Orleans"]; template = /tmp/aw236b_b3_kc.py) -> /tmp/aw236b_b3_no.json: **46 unique, 6 good**. /tmp/aw236b_b3_no_extra.py (9 extra forms: "New Orleans, Louisiana", + 1893/1903/1877/1885/1911/Byrne/Robinson/panorama) -> /tmp/aw236b_b3_no_extra.json: 356 fresh, 70 "good" **but all non-views** (Sanborn 1885/1893 fire-insurance plates and Robinson's Atlas 1883 district plates = flat plans, the 236a genre, not bird's-eye; Detroit Publishing photo panoramas c1900-1921 ("New Orleans, La. Panorama c1900-1915.jpg" 42611x7111, "The City from Algiers ... c1900 (panorama).jpg" 30816x6698, "New Orleans panorama 1919.jpg") - PHOTOS, the SF-1906-photograph drop precedent; Bennett 1877 troop-withdrawal lithographs (scene, not a city view); "Plan of New Orleans ... 1876 by S. Augustus Mitchell" (IA David Rumsey) - a FLAT plan, the 236a genre; postcards, ads, street photos, a steamer photo, a Courbet painting, census sheet, etc.).
- **THE ONLY whole-city view through the gate (keep + 600-char caption gate + Public domain + >= 4000 px): `File:Bird's eye view of New Orleans (NYPL Hades-118746-54871).tif` - 5843x4600, PD, page date 1851 = the drawing's year (no Zwolle-style swap; row's extra dict stays empty).** Eyeballed (original downloaded to /tmp/no1851.tif; re-download from https://upload.wikimedia.org/wikipedia/commons/2/2d/Bird%27s_eye_view_of_New_Orleans_%28NYPL_Hades-118746-54871%29.tif if wiped): banner "BIRDS EYE VIEW OF NEW-ORLEANS / PUBLISHED BY THE AGENTS A. GUERBER & Co, 160 Pearl St. New York."; inside the frame "DRAWN FROM NATURE ON STONE BY J. BACHMAN." (left) and "PRINTED BY J. BACHMAN" (right); NYPL desc "Stokes 1851-G-13 / Deak 605". **Drawn AND printed by John Bachman, published by his New York agents A. Guerber & Co. - the OLDEST staged view of the whole project (1851, before the SF 1854 Bill view).** Steep oblique whole-city view: the dense grid legible out to the rural outskirts (city at the left of the sheet), the levee with its steamboats in the foreground, the river, the delta (East/South Pass) and "GULF OF MEXICO" at the right, "LAKE PONTCHARTRAIN" at the top.
- **OPEN QUESTION (the 188 lesson: measure before writing a direction claim): the sheet's compass orientation is NOT yet pinned down.** My readings so far: the river's delta/Gulf is at the sheet's right => downstream (south) runs toward the right; the city (west bank) sits at the UPPER side of the river band; the 1280 px thumb alone is ambiguous (my two candidate rotations clashed, one implies a mirrored sheet, which is impossible - so one of the two sub-readings is wrong). I had just cropped /tmp/no1851_south.jpg (x 0.05-0.60, y 0.30-0.88 at 1.6x) to trace exactly where the river enters and leaves the frame when the limit hit. NEXT: look at that crop (regenerate if wiped), then optionally web_search the standard description of Bachman's 1851 New Orleans view ("drawn from a point ..."); until it is settled, write the note's angle WITHOUT a compass direction: "steep oblique whole-city view drawn from high ground over the river, the levee and its steamboats in the foreground, the river, the delta and Lake Pontchartrain in the sheet's right half" - the Kansas City note is the template. (If the orientation proves e.g. "drawn from the south-east looking north-west", that wording goes in instead.)

### DROPS for the lead-doc New Orleans section (per-item, from the two pools)

- LOC 75693238 "New Orleans, La. and its vicinity." .jpg/.tif (1863, Wells J./Ridgway W./Virtue & Co., 3152x2152, LC Panoramic maps (2nd ed.), 241) - a genuine indexed whole-city bird's-eye view but **too small** (< 4000 px).
- LOC 99447004 "Birds eye view of Louisiana, Mississippi, Alabama and part of Florida" .jpg/.tif (1861, Bachman, 8597x5967, LC Civil War Maps (2nd ed.), 1.7, "Panorama of the seat of war") - **regional**: the Gulf coast centered on the delta, the city a small settlement (the DC 1861 Bohn regional-drop precedent).
- DPLA 89ae745151be1f519f0f61a0dc5e91a8.jpg (Fisher J.H. "VIEW OF ST. LOUIS, 1850-54", 5325x6997) - **a St. Louis view** (search noise: the steamboat "New Orleans" in the description).
- LCCN2012645333.jpg (1840/44, Laclotte/Hoffy/Duval, 5304x4352, U.S. Military Magazine) - the **1815 Battle of New Orleans scene** (the Fort-Negley close-up class: a battle scene, not a city view).
- NARA 26428460.jpg (Tulane SATC Sections A and B, 1917-18, 8646x5792) - a **district PHOTOGRAPH** (barracks), not a view (the photo-drop precedent).
- Fred Harvey NBY strips (NBY 7257 1900, NBY 432193 1903, NBY 432311, NBY 431648, NBY 7794 "Aerial View" 1946 etc., 813-824 px) - **too small** (+ the 1946 one beyond MAX_YEAR). "New Orleans view 1873.jpeg" 567x359, "The City of New Orleans, Louisiana.jpg" 990x652, BirdsEyeCanalStreetCrescentCard 1609x1023, PostcardNewOrleansDistrict CBMason 1633x1031 - too small. The Dennis/Lilienthal/Blessing 1868 stereoscopic-view set (2737 px) - **fail the caption gate** (no "New Orleans" in title+desc) AND too small. "Birds-eye view of Jackson Sqr (NYPL b11707483-...)" tiffs (3072 px) - gate (the title says Jackson Sqr) + too small. "New Orleans and Vicinity Birds Eye 1863.jpg" (2445x1917, J. Wells del./W. Ridgway sc. - the smaller copy of the LOC 75693238 sheet) - too small. The 2017/2008/2022 photo panoramas + the 2018 bird's-eye-MAPLE guitar photos (CC-licensed, beyond MAX_YEAR; the guitar = the Kansas City-section precedent). The extra pool's 70 "good" (above: Sanborn/Robinson plates, photos, Bennett scenes, the 1876 Mitchell plan, the diocesan map, the Hearn-courtyard photo, the census sheet, the milk-cart photo, the Cotton Exchange photo, postcards, ads).

### Exact next step (one session: land New Orleans - the 189/190 Kansas City pattern)

1. **Settle the orientation** (see OPEN QUESTION): look at /tmp/no1851_south.jpg (regenerate from /tmp/no1851.tif with the same crop if wiped), web_search if needed; keep the wording uncommitted to a compass direction until settled.
2. **fit/src_us_birdseye.py**: SITES header line "Batch 3 (checked live 2026-10-14): Kansas City, New Orleans."; Q34404 SITES entry after Q41819 in the batch-3 block: `dict(id="new-orleans-q34404", name="New Orleans", named="New Orleans", lon=-90.078333, lat=29.976111, place="Orleans Parish, Louisiana", region="United States", kind="town", wikipedia="https://en.wikipedia.org/wiki/New_Orleans", note=...)` - the SITES comment = P625 single 30 m value + P373 string quirk + single-parish P131 + no-trap + the Q2522995 Rotterdam building at the measured 7725 km ENE + the Q1474157 LSU hit at ~5.7 km; note = the aerial-ground template + the view's angle (per step 1) + the beyond-the-box review-item line. `BACHMAN_1851` rows list: one row `("File:Bird's eye view of New Orleans (NYPL Hades-118746-54871).tif", "Q34404", "New Orleans", dict())` with the comment (the oldest staged view of the project; drawn+printed by J. Bachman, published by the agents A. Guerber & Co 160 Pearl St NY; 1851 == page date, no swap). SOURCES key `"neworleans_1851": dict(rows=BACHMAN_1851, p="birdseye", label="{name}, the Bachman bird's-eye view (1851)")`.
3. `--verify` (now 16 QIDs; save /tmp/aw236b_verify_191.txt) - expect zero P625 flags; the New Orleans first name-search hit = Q34404 itself.
4. `--dry` (expect 1 new site new-orleans-q34404, 1 new picture) then stage (live commons.info re-check) then `--check` (expect 23/23 PASS; save /tmp/aw236b_check_191b.txt).
5. **Lead doc** (187/190-style splice script, /tmp/aw236b_doc_190.py is the template): (a) QID section = fresh 16-QID verbatim transcript + intro update (sixteen; the twelve new-city points ARE the P625s; New Orleans no-trap + the Rotterdam-building note); (b) NEW "## New Orleans (site new-orleans-q34404, this task's point = the verified P625; 1 view staged)" section after Kansas City: STAGED bullet (1851, drawn from nature on stone and printed by J. Bachman, published by the agents A. Guerber & Co, 160 Pearl St. New York, 5843x4600, PD, NYPL Hades-118746-54871 / Stokes 1851-G-13 / Deak 605, the angle per step 1, the oldest staged view of the project) + the DROP list above + the QID-facts paragraph (single 30 m P625, string-P373 quirk, single-parish P131 -> place, no name-search trap, Q2522995 Rotterdam building 7725 km ENE, Q1474157 LSU 5.7 km); (c) Staging section = sixteen cities / 23 views / twelve site rows / the fresh 23-line --check transcript / golden pins the 23 rows / "Not done yet: 9 more US cities (25 total, 16 done), next: Denver, St. Paul, Minneapolis, Cleveland, ...".
6. `--golden` (12 extras / 23 files / 23 classified) + extend tests/test_src_us_birdseye.py exactly as 190 did (module docstring batch-3 line; test-1 docstring "(batches 1-3)" + the NO PASS key in its key list; test-2 docstring; test-3: docstring lists new-orleans-q34404, SITES-id table, extras-id table, per-title year 1851, evidence point (-90.078333, 29.976111), named-place table "New Orleans", len(files) 22 -> 23) + module tests, then the full suite (if it re-writes docs/site_flow/307d_*.png, carry them in the commit with the 306g-style disclosure).

Then batch 3 closes (4 cities) and batch 4 follows: Denver, St. Paul, Minneapolis, Cleveland + ~5 more to reach 25. The per-city playbook (pool builder, gate, eyeball, verify, stage, doc, golden, tests) is restated in the Kansas City hand-over below.

### State (before this session's work)

- docs/lead_us_birdseye.md: 784 lines, 20 ## sections; 15 cities / 22 views; QID section = 15-QID verbatim transcript; Staging section = the 22-line --check transcript, "Not done yet: 10 more (25 total, 15 done), next: New Orleans, ...".
- fit/src_us_birdseye.py: 15 QIDs (4 shared + 11 SITES); 22 SOURCES keys; batch-3 header comment + Q41819 entry + KANSASCITY_1869 + "kansascity_1869" source key.
- data/catalog/extras_us_birdseye.jsonl: 11 site rows; files/classified_us_birdseye.jsonl: 22 rows each. tests/golden/src_us_birdseye_sample.json: the 22-row pin. Module tests 5/5. Offline --check 22/22 (re-verified this session, /tmp/aw236b_check_191.txt).
- /tmp (may be wiped, all regenerable): the builders /tmp/aw236b_b3_no.py, /tmp/aw236b_b3_no_extra.py (+ their .json pools), /tmp/no1851.tif (the original), /tmp/aw236b_b3_no_thumbs/ (the six good thumbs), the crop scripts inline in bash history (banner/credits/corners re-crop from no1851.tif), /tmp/aw236b_b3_kc.py (the batch-3 builder template), /tmp/aw236b_verify_190.txt (15-QID transcript), /tmp/aw236b_doc_190.py (the doc splice script template).

### Rules (unchanged)

NEVER write the canonical files (data/commons/files.jsonl etc. - that is 236c); NEVER touch 236a's extras_us_cities.jsonl (read-only; the module's _shared_site enforces it); run live commands under .venv/bin/python (system python3 has no numpy; the module top stays stdlib-only); batch size ~5 cities/session to fit the context limit; the golden sample is the contract (--golden only for an intended change); the full suite re-writes the docs/site_flow/307d_*.png every run - if the bytes change, carry them in the commit with the 306g-style disclosure; tests never bind fixed network ports or write outside the project + temp dir; when recording a distance/direction claim in a doc or comment, MEASURE it (the 188 NE/west errors were unmeasured draft-time guesses - and the 191 lesson: a compass direction for a rotated sheet is exactly that class of claim).

(2026-10-14, iteration 189, agent a) **Batch 3, city 1 = KANSAS CITY: research DONE and verified; module edit + stage + doc + golden/tests are the next session's work.** Context limit hit after the QID/pool research, before touching any project file - no module, data, doc or test was changed this session (only /tmp scripts + thumbs). Tests as last run: module 5/5 (188), offline --check 21/21 (188); staged files still 10 site rows / 21 file rows / 21 classified rows.

### What 189 established (all live, re-verify is cheap)

1. **QID = Q41819** (NOT Q31997 - that is "Ažbe Jug"): label "Kansas City", enwiki "Kansas City,
   Missouri", P373 = the STRING "Kansas City, Missouri" (a Wikidata quirk - not a country entity;
   do not use it for the place, note it in the SITES comment). P131 = FOUR counties (Q127238
   Jackson / Q485204 Cass / Q484474 Clay / Q489897 Platte, all Missouri - the city straddles all
   four); the P625 point sits in Jackson County, so place = "Jackson County, Missouri".
   **P625 = exactly ONE normal-rank value: (-94.583333, 39.05), precision 0.0167 deg (1/60 deg)**
   - wbgetentities (what --verify uses) returns only that one; the raw wbgetclaims dump shows 50
   more suppressed-rank 30 m-precision P625s (mass import) that the API hides. Table point =
   (-94.583333, 39.05), dist 0. The point sits in the city's SOUTHERN part (a few km south of the
   downtown core); the 1869 sheet's whole-city extent covers the 2000 m box easily, so no
   refinement is needed (unlike Nashville) - but MEASURE any distance/direction claim before
   writing it (188's lesson).
2. **Name search "Kansas City" (what --verify does): NO TRAP** - the first hit with P625 is Q41819
   itself (dist 0). The second hit is the twin city Q486472 (Kansas City, Kansas, Wyandotte County,
   P625 (-94.676389, 39.106667)) - record it in the SITES comment with the MEASURED distance
   (~10 km WNW by eye; the 189 script died before printing it - measure with
   `evidence.hav_m(-94.676389, 39.106667, -94.583333, 39.05)` or the dx/dy formula before quoting).
   Note: the earlier attempt to fetch the enwiki infobox coords via
   `action=parse&prop=coordinates` got KeyError 'coordinates' - retry with a different action or
   just skip it (the comment does not need it).
3. **Pool** (/tmp/aw236b_b3_kc.py builder, /tmp/aw236b_b3_kc.json full pool, 68 unique / 10 good;
   thumbs in /tmp/aw236b_b3_kc_thumbs/ - all may be wiped, regenerate with the builder): the ONLY
   whole-city view that passes the gate is the **1869 Ruger sheet, LOC 73693480** (.jpg 8752x6912
   staged, the .tif 8752x6912 is the same-sheet twin - one row). Eyeballed: steep oblique drawn
   from high ground across the Missouri (looking south over the city), the river + the rail
   bridges + steamboats in the foreground, the grid dense and legible out to the rural outskirts,
   the "KANSAS CITY / MISSOURI / 1869" cartouche with a landmark index at the bottom, "DRAWN BY
   A. RUGER", photographed by A. C. Christy; artist metadata "Ruger, A.; Christy, A. C.;
   Merchant's Lithographing Company; Ruger & Stoner"; LC Panoramic maps (2nd ed.), **428**; date
   1869 == year (no Zwolle-style swap needed); Public domain.
4. **DROPS for the lead-doc Kansas City section** (per-item reasons): the 1895 Koch
   "Panoramic view of the west bottoms, Kansas City, Missouri & Kansas showing stock yards,
   packing & wholesale houses" (LOC 75694656 .jpg/.tif, 15487x10139, LC Panoramic 429) - a
   near-vertical CLOSE-UP of the West Bottoms stockyard/packinghouse district (inset "Reid Bros.
   Pkg. Co. Ltd."), not a whole-city view (the Fort-Negley-close-up class); the Fred Harvey NBY
   strips (23194/23195 "business section", 5561 "showign Missouri River", 21319/21320 "business
   district" - all 822-829 px) and the 1909 Gillham Road .tif (2984x665) and 1909 Kersey Coats
   Drive (3101x680) - too small (< 4000 px); "Kansas city mo 1869.gif" (546x432) - too small; the
   three 1876 "St. Louis ... Kansas City & Northern" railway sheets (7560x3944 etc.) - St. Louis
   views that already DROP in the St. Louis section (search noise); other-Kansas-city sheets in
   the pool (Lawrence, Leavenworth, Topeka, Wyandotte, Atchison, Ottawa, Baxter Springs, Great
   Bend, Hiawatha, Herington, Meade) - fail the caption gate on their own city names; plus the
   gate/keep rejects (Dutch "Plattegrond" RP-P files, Vernonia Oregon, a John T. Birdseye
   portrait, the Union Pacific "Great Plains" sheet, a cloud photo, a guitar photo).

### Exact next step (one session: land Kansas City)

1. (Optional, quick) measure the Q486472 distance + retry/skip the enwiki infobox (above).
2. **fit/src_us_birdseye.py**: batch-3 header comment + SITES entry
   `"Q41819": dict(id="kansas-city-q41819", name="Kansas City", named="Kansas City",
   lon=-94.583333, lat=39.05, place="Jackson County, Missouri", region="United States",
   kind="town", wikipedia="https://en.wikipedia.org/wiki/Kansas_City,_Missouri", note=...)`
   (slug verified in principle: catalog.slug = NFKD -> ascii -> [^a-z0-9]+ to "-" -> lower ->
   "kansas-city"; the note = the batch-2 aerial-ground template + the 1869 view's angle +
   beyond-the-box review-item line + the twin-city fact); KANSASCITY_1869 rows list (the .jpg)
   + SOURCES key "kansascity_1869" label "{name}, the Ruger bird's-eye view (1869)".
3. `--verify` (now 15 QIDs; save /tmp/aw236b_verify_189.txt) - expect zero flags (P625 dist 0,
   first name-search hit = the city itself).
4. `--dry` then stage (live commons.info re-check) then `--check` (expect 22/22 PASS; save
   /tmp/aw236b_check_189.txt).
5. **Lead doc**: new Kansas City section after the Milwaukee section (batch-2 style: STAGED
   bullet + DROP list + the Q41819 facts: four-county P131, string P373 quirk, single 1/60-deg
   P625, no name-search trap, twin city Q486472 at the measured distance); QID section = fresh
   15-QID verbatim transcript; Staging section = 15 cities / 22 views / 11 site rows, the fresh
   --check transcript, "Not done yet: 10 more cities (25 total, 15 done), next: New Orleans, ...".
6. `--golden` (intended change: 11 extras / 22 files / 22 classified) + extend
   tests/test_src_us_birdseye.py exactly as 184 did (SITES-id table, extras-id table, per-title
   year, evidence points, named-place table, len(files) 21 -> 22) + module tests + the full
   suite (if it rewrites docs/site_flow/307d_*.png, carry them with the 306g-style disclosure).

Then the next sessions: New Orleans, Denver, St. Paul, Minneapolis (batch 3), then batch 4
(Cleveland + the remaining ~5 to reach 25). Everything in /tmp may be wiped: the pool builder
/tmp/aw236b_b3_kc.py is the template (change CITIES); the per-city playbook is restated in the
184 DECISIONS entry.

1. **QID check against existing sites** (never two sites for one QID): grep the city name in
   data/catalog/sites.jsonl, data/catalog/extras.jsonl, data/catalog/extras_us_cities.jsonl,
   web/data/sites.json. New city -> point = the city's P625 (record any refinement).
2. **Pool search**: per-city Commons file-namespace search, the 6 plain-phrase forms ("bird's-eye
   view of <city>", "bird's eye view of <city>", "birdseye view of <city>", "<city> bird's eye",
   "<city> birdseye", "Birds' eye view of <city>" - quoted-intitle queries find NOTHING) each +
   " filetype:bitmap"; commons.info 50/call at 1/s. Batch-2 builder template = /tmp/aw236b_b2.py
   (may be wiped - a ~55-line stdlib+commons script: change the CITIES list). Gate =
   commons.keep() + 600-char caption gate (norm(city) in norm(title+desc)) + Public domain +
   >= 4000 px wide.
3. **Pick the ONE steepest view** (near-vertical, grid legible; DROP pictorial/regional/fort
   close-up/photo/street-car/railway/exposition); eyeball 1280-px thumbs to dedupe same-sheet
   scans (thumb URLs via the Commons API imageinfo thumburl iiurlwidth=1280 through .venv's
   commons.get - commons.info has no 'thumb' key); one row per sheet, keep the LOC/largest scan.
4. **Verify the QID live**: `.venv/bin/python fit/src_us_birdseye.py --verify QID` - watch
   name-search traps (Chicago's Q131252 and Pittsburgh's Q235034 are the in-table examples; a
   university hit within 50 km is NOT flagged but `record --live` would store it).
5. **SITES + SOURCES entries in fit/src_us_birdseye.py** (batch-2 entries ~lines 130-213 /
   350-400 are the pattern: SITES comment = P625/P131/enwiki/point-derivation + any name-search
   trap with the MEASURED distance and direction (dx=dlon*111194.9266*cos(lat0), dy=dlat*110900);
   SOURCES comment = the pick + same-sheet scans + drop summary pointing at the lead doc).
6. **--dry then stage** (live commons.info re-check of every title) then **--check** (must exit 0).
7. **Lead-doc section per city** (batch-2 style: STAGED bullet + DROP list with per-item reasons
   + name-search-trap paragraph when applicable) + **re-run --verify** (the QID transcript in the
   doc grows by one QID per new city - the transcript must stay verbatim) + update the Staging
   section (view count, --check transcript, "Not done yet" list).
8. **--golden** (intended change) + extend tests/test_src_us_birdseye.py exactly as 184 did
   (SITES-id table, extras-id table, per-title year, evidence-points, named-place table,
   len(files) 21 -> 26 for batch 3) + module tests, then the full suite (if it rewrites
   docs/site_flow/307d_*.png, carry them in the commit with the 306g-style disclosure).

A city with no usable view gets a lead-doc note and the next candidate. Batch 4 after batch 3:
the remaining ~6 (Cleveland, ...) to reach 25 cities, then box 4 ticks.

### State

- docs/lead_us_birdseye.md: committed (f3aed14 + this session's fix commit). 715 lines, 19 ##
  sections, 14 cities / 21 views; QID section (14-QID verbatim transcript) + five batch-2 city
  sections + Staging section (verbatim 21-line --check); directions/distances corrected.
- fit/src_us_birdseye.py: 14 SITES / 21 SOURCES; Q1342 SITES comment now "~4.0 km east".
- data/catalog/extras_us_birdseye.jsonl: 10 site rows; data/commons/files_us_birdseye.jsonl +
  classified_us_birdseye.jsonl: 21 rows each. tests/golden/src_us_birdseye_sample.json: the
  21-row pin. Module tests 5/5 (188). Offline --check 21/21 (re-verified 188).
- /tmp (may be wiped, all regenerable): /tmp/aw236b_verify_186.txt (the 14-QID transcript - the
  source of the doc's QID block), /tmp/aw236b_check_188.txt (fresh check), /tmp/aw236b_b2.py +
  /tmp/aw236b_b2.json + /tmp/aw236b_b2_cands.json + /tmp/aw236b_b2_thumbs/ (the batch-2 pool
  builder and full pool - the template for the batch-3 builder).

### Rules (unchanged)

NEVER write the canonical files (data/commons/files.jsonl etc. - that is 236c); NEVER touch 236a's
extras_us_cities.jsonl (read-only; the module's _shared_site enforces it); run live commands under
.venv/bin/python (system python3 has no numpy; the module top stays stdlib-only); batch size ~5
cities/session to fit the context limit; the golden sample is the contract (--golden only for an
intended change); the full suite rewrites the five docs/site_flow/307d_*.png every run - if the
bytes change, carry them in the commit with the 306g-style disclosure (the 184 commit did); tests
never bind fixed network ports or write outside the project + temp dir; when recording a
distance/direction claim in a doc or comment, MEASURE it (the 188 NE/west errors were unmeasured
draft-time guesses).
