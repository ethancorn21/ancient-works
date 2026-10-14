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
