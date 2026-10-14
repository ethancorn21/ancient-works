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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-14, iteration 137, agent c - the driver returned the parent after 207a (done),
- `tasks/212-cover-final.md` (in-progress) - hand-over: (2026-10-13, iteration 255, agent a, written at the context limit -
- `tasks/236b-us-birdseye.md` (open) - hand-over: (2026-10-14, iteration 189, agent a) **Batch 3, city 1 = KANSAS CITY: research DONE and verified; module edit + stage + doc + golden/tests are the nex
- `tasks/236-us-cities.md` (split)
- `tasks/307bc-reverify-place-mode.md` (open) - hand-over: (2026-10-13, iteration 256, agent a - first session: the task was filed as the driver
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-13, iteration 256, agent a - context limit hit at the end of this session; the
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/235-placement-test-dep-pick.md`
- `tasks/236c-us-cities-merge.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-14 236b DECISION: iteration 185 - verified everything the batch-2 lead doc needs (14-QID --verify clean, --check 21/21, ALL batch-2 same-sheet claims re-eyeballed and confirmed) but the context limit hit before writing docs/lead_us_birdseye.md - the doc is the one remaining step of work A, fully specified in the task hand-over
- **Step 0 done by the driver:** `git status` clean at session start - f206b2f swept 184's uncommitted batch-2 work (10 site rows / 21 file rows / 21 classified rows / 21-row golden / batch-2 test tables), so no commit was needed. The staged files were re-counted and matched.
- **--verify (live, 14 QIDs, .venv): all clean, zero P625 flags, exit 0** (transcript /tmp/aw236b_verify_185.txt, 86 lines, may be wiped - re-run to regenerate): the two name-search traps stand exactly as recorded (Pittsburgh -> Q235034 University of Pittsburgh ~4.7 km west; Chicago -> Q131252 University of Chicago ~10.5 km south - both within the 50 km flag, so not flagged); St. Louis P131 = ['Missouri'] only (independent city - hence place "St. Louis City, Missouri"); Milwaukee P131 = three counties (Milwaukee/Washington/Waukesha - the point sits in Milwaukee County); Q62 still the two P625 values (2.0-2.4 km from its refined table point); every other P625 matches its table point (dist 0).
- **--check (offline): exit 0, 21/21 PASS caption_coords, no join problems** (transcript /tmp/aw236b_check_185.txt) - matches 184's run.
- **Eyeballs (the batch-2 lead doc's factual core) - all CONFIRMED same-sheet / as claimed in the module comments:** (a) Louisville: staged LOC 75693235 (1883, two-panel: exposition hall above, steep near-vertical whole-city view below, "MAP OF LOUISVILLE AND ITS ENVIRONS 1883" inset) = `Birdseye-southernexpo.jpg` (10757x6905, different copy) - identical title block "BIRDS-EYE VIEW OF LOUISVILLE FROM THE RIVER FRONT AND SOUTHERN EXPOSITION, 1883. DEDICATED BY THE PUBLISHERS TO THE LOUISVILLE BOARD OF TRADE AND MANUFACTURING INDUSTRIES."; the 1876 sheet (LOC 73693416, 7890x5808, A. Ruger, Charles Shober & Co. / Chicago Litho., LC Panoramic 236) is a DIFFERENT, shallower sheet (Ohio + bridge foreground, index of churches/public buildings). (b) St. Louis: staged 1858 Palmatary full view (14437x7800, "BIRD'S EYE VIEW OF SAINT LOUIS, MO." banner, levee + steamboat fleet foreground) - the seven "(... detail)" tiles are high-res crops of the same sheet (the upper-left tile's street labels 40th-44th / Chestnut / Main / Olive / Delaware / Walnut / Locust match the full view's northwest district); the 1876 KC&N railway sheet (LOC 82695092, 7560x3944), "St. Louis in '93" (LOC 75694659, 11904x7680, Fred Graf, LC Panoramic 441 - shallow skyline with population plates, copyrighted 1892) and "St. Louis in 1895" (LOC 75694661, 12368x8240, Charles Juehne, LC Panoramic 443 - steeper, indexed, Eads Bridge) are all different sheets. (c) Chicago: staged 1892 (LOC 75693206, 9904x5648, Peter Roy, LC Panoramic 151) = 1893 LOC 97686545 (the color edition - identical composition, same "VIEW OF CHICAGO IN 1832" scroll and index, railroads red / parks green). (d) Detroit: SIX scans of the 1889 Calvert sheet all confirmed identical (staged LOC 76693077 .jpg/.tif 6815x4184; LCCN2003666422 .jpg/.tif 10657x6108; Adam Cuerden .jpg/.png 6312x4132; "Map image detroit.jpg" 5999x3676 - identical title block "BIRDS EYE VIEW—SHOWING ABOUT THREE MILES SQUARE—...", "THE CALVERT CITY OF DETROIT" side label, Library-of-Congress stamps); the Hurd-Martin 1906/1907 sheets are 1818+1908 postcard pairs (pictorial). (e) Milwaukee: staged LOC 76693067 (1872 Bailey, "MILWAUKEE, WIS." banner, two-panel, 69-key) = "Milwaukee 1872.jpg" (11952x8416) = g4124m-pm010450 (9999x6650); the 1879 (LOC 75696716, 12656x8384, Stoner) and 1882 (LOC 75696717, 8192x4904, Beck & Pauli) are different later sheets; "Milwaukee 1858.jpg" is the 1854 Moody chromo (12496x8432, Endicott & Co. - the title says 1858, the sheet says 1854).
... (1.0 KB more: `grep -n -A 200 -F '## 2026-10-14 236b DECISION: iteration 185 - verified everything the batch-2 lead doc needs (14-QID --verify clean, --check 21/21, ALL batch-2 same-sheet claims re-eyeballed and confirmed) but the context limit hit before writing docs/lead_us_birdseye.md - the doc is the one remaining step of work A, fully specified in the task hand-over' DECISIONS.md`)

### 2026-10-14 236b DECISION: iteration 187 - batch-2 lead doc WRITTEN into docs/lead_us_birdseye.md (UNCOMMITTED - the harness saved the edit; the next session re-reads the three regions and commits it): the QID section now carries the verbatim 14-QID --verify transcript, the five batch-2 city sections (STAGED/DROP) are inserted, and the Staging section is at 21 views / 10 site rows / the fresh 21-line --check transcript - 14 of 25 cities staged, box 4 still open, batch 3 (Kansas City first) is next
- **Session start:** tree clean; /tmp still held iteration 186's two transcripts (aw236b_verify_186.txt = 14-QID live --verify, aw236b_check_186.txt = 21-line offline --check) - 186 had hit its context limit before writing the doc and committed nothing. diff: verify_186 is content-identical to verify_185 (minus a trailing "exit=0" line), check_186 identical to check_185 - so no live re-run was needed this session (both runs dated 2026-10-14; the doc carries both verbatim).
- **Fact cross-checks (the doc's factual core):** every file title / dimension / licence cited in the five new city sections was checked against /tmp/aw236b_b2.json (the batch-2 pool with per-file metadata w/h/license/year/desc), and the module comments (fit/src_us_birdseye.py: SITES notes Q43668/Q38022/Q1297/Q12439/Q37836, SOURCES comments LOUISVILLE_1883 / STLOUIS_1858 / CHICAGO_1892 / DETROIT_1889 / MILWAUKEE_1872) agree with what is written. Nine initial title mismatches in the check script were all apostrophe/quote typos in my own search strings (the pool uses straight apostrophes), not real discrepancies. Two corrections vs the 185 hand-over draft: (1) the "Saint Louis"-titled St. Louis detail tile has keep=True but gate=False - it fails the 600-char caption gate (its title says "Saint Louis", not "St. Louis"), so the doc says "fails the caption gate on its title" (the draft said "fails keep()" on its title); (2) Detroit has SIX further scans of the staged sheet (the LOC .tif twin, the LCCN2003666422 .jpg/.tif 10657x6108 pair, the Adam Cuerden .jpg/.png 6312x4132 pair, "Map image detroit.jpg" 5999x3676) - the draft said five.
- **The doc (docs/lead_us_birdseye.md, UNCOMMITTED, 715 lines, was 482):** three splices via a small python script that asserts each section heading occurs exactly once, then replaces (content files /tmp/aw236b_doc_qid_187.md and /tmp/aw236b_doc_cities_187.md, the two transcripts inlined from the /tmp files at splice time): (a) "## QID verification" replaced - new intro (14 QIDs at the batch-2 close-out; no P625 flag on any of the fourteen - Q62's two P625s 2.0-2.4 km from its refined table point, Q23197's 721 m NE, the ten new-city points ARE the P625s dist 0; the two name-search traps Pittsburgh -> Q235034 and Chicago -> Q131252, both in-flag, recorded; Baltimore P131 two values -> "Baltimore City, Maryland"; St. Louis P131 = Missouri only -> "St. Louis City, Missouri"; Milwaukee P131 three counties, point in Milwaukee County) + the verbatim 14-QID transcript; (b) five city sections inserted between the Cincinnati section and "## Staging and checks" (Louisville, St. Louis, Chicago, Detroit, Milwaukee) in the batch-1 style - STAGED bullet (year/artist/publisher/dims/PD/LC Panoramic no./angle/same-sheet scans) + DROP list with per-item reasons + Chicago's name-search-trap paragraph; (c) "## Staging and checks" updated - fourteen cities / 21 views / ten site rows in extras_us_birdseye.jsonl / verbatim 21-line --check transcript / golden pins the 21 rows / "Not done yet: 11 more cities (25 total, 14 done), next candidates Kansas City, New Orleans, Denver, St. Paul, Minneapolis, Cleveland, ...". Structure verified after the splice (all 19 ## headings in order, fence pairs intact); a full fresh-eyes re-read of the new doc is NOT done yet (context limit) - it is the next session's step 1, then the module tests, then the commit.
... (4.3 KB more: `grep -n -A 200 -F '## 2026-10-14 236b DECISION: iteration 187 - batch-2 lead doc WRITTEN into docs/lead_us_birdseye.md (UNCOMMITTED - the harness saved the edit; the next session re-reads the three regions and commits it): the QID section now carries the verbatim 14-QID --verify transcript, the five batch-2 city sections (STAGED/DROP) are inserted, and the Staging section is at 21 views / 10 site rows / the fresh 21-line --check transcript - 14 of 25 cities staged, box 4 still open, batch 3 (Kansas City first) is next' DECISIONS.md`)

### 2026-10-14 236b DECISION: iteration 189 - batch 3, city 1 (Kansas City): RESEARCH DONE, module edit is next
- **QID found live: Q41819 = Kansas City, Missouri** (label "Kansas City", enwiki "Kansas City, Missouri"; NOT Q31997 - that is "Ažbe Jug", a Slovenian entity - my initial guess was wrong, caught by checking the label). P373 = the STRING "Kansas City, Missouri" (a Wikidata data-quality quirk - a string, not a country entity; do not use it for the place). P131 = FOUR counties (Q127238 Jackson / Q485204 Cass / Q484474 Clay / Q489897 Platte, all Missouri - the city straddles all four); the P625 point sits in Jackson County, so the site place = "Jackson County, Missouri".
- **P625: exactly ONE normal-rank value (-94.583333, 39.05), precision 0.0167 deg (1/60 deg).** The raw `wbgetclaims` dump shows 50 further suppressed-rank 30 m-precision P625s (a mass import) but `wbgetentities` - the call --verify uses - returns only the normal-rank one (verified live this session). Table point = that P625 (dist 0); the point sits in the city's southern part (a few km south of the downtown core); the 1869 sheet's drawn extent covers the 2000 m town box, so no refinement is needed (unlike Nashville). MEASURE any distance claim before quoting it (188's NE/west lesson).
- **Name search "Kansas City" (what --verify resolves): NO TRAP** - first hit with P625 is Q41819 itself (dist 0); second is the twin city Q486472 Kansas City, Kansas (Wyandotte County, P625 (-94.676389, 39.106667)) - to be recorded in the SITES comment with the measured distance (my session's script died on the enwiki call before printing it: estimate ~10 km WNW, must be measured). The enwiki infobox fetch (`action=parse&prop=coordinates`) returned KeyError 'coordinates' - skip it or retry differently; the comment does not need it.
- **Pool (Commons file-namespace search, /tmp/aw236b_b3_kc.py builder + /tmp/aw236b_b3_kc.json, 68 unique / 10 good; 1280 px thumbs eyeballed in /tmp/aw236b_b3_kc_thumbs/):** the ONLY whole-city view through the gate is the **1869 Ruger sheet, LOC 73693480** (.jpg 8752x6912 to stage; the .tif 8752x6912 is the same-sheet twin - one row per sheet). Eyeballed: steep oblique drawn from high ground across the Missouri (looking south over the city), river + rail bridges + steamboats in the foreground, grid dense and legible out to the rural outskirts, "KANSAS CITY / MISSOURI / 1869" cartouche with a landmark index at the bottom, "DRAWN BY A. RUGER", "PHOTOGRAPHED BY A. C. CHRISTY"; artist metadata "Ruger, A.; Christy, A. C.; Merchant's Lithographing Company; Ruger & Stoner"; LC Panoramic maps (2nd ed.), 428; date 1869 == year (no Zwolle-style swap); Public domain.
- **DROPS (for the lead-doc Kansas City section):** the 1895 Koch "Panoramic view of the west bottoms, Kansas City, Missouri & Kansas showing stock yards, packing & wholesale houses" (LOC 75694656 .jpg/.tif, 15487x10139, LC Panoramic 429) - a near-vertical CLOSE-UP of the West Bottoms stockyard/packinghouse district (a "Reid Bros. Pkg. Co. Ltd." inset), not a whole-city view (the Fort-Negley-close-up class); the Fred Harvey NBY strips (23194/23195, 5561, 21319/21320 - 822-829 px) and the 1909 Gillham Road .tif (2984x665) and 1909 Kersey Coats Drive (3101x680) - too small (< 4000 px); "Kansas city mo 1869.gif" (546x432) - too small; the three 1876 "St. Louis ... Kansas City & Northern" railway sheets - St. Louis views already dropped in the St. Louis section (search noise); other-Kansas-city sheets (Lawrence, Leavenworth, Topeka, Wyandotte, Atchison, Ottawa, Baxter Springs, Great Bend, Hiawatha, Herington, Meade) - fail the caption gate on their own city names; gate/keep rejects: Dutch "Plattegrond" RP-P files, Vernonia (Oregon), a John T. Birdseye portrait, the Union Pacific "Great Plains" sheet, a cloud photo, a guitar photo.
... (6.9 KB more: `grep -n -A 200 -F '## 2026-10-14 236b DECISION: iteration 189 - batch 3, city 1 (Kansas City): RESEARCH DONE, module edit is next' DECISIONS.md`)

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

### 2026-10-14 agent a (iteration 191, context-limit note)

236b hand-over rewritten: batch 3 city 2 (New Orleans) research DONE - QID Q34404 verified live (single 30 m P625, string-P373 quirk, single-parish P131, no name-search trap; the Rotterdam-building same-name at the measured 7725 km ENE), the 1851 Bachman NYPL tif is the only whole-city view through the gate (the project's oldest staged view; full drop list in the task file). The one open question: the sheet's compass orientation (no compass rose on the sheet; the 1280 px thumb is ambiguous) - the next session settles it from /tmp/no1851_south.jpg before landing the city (module + stage + doc + golden + tests, the 189/190 Kansas City pattern).
