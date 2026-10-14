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

(2026-10-14, iteration 194, agent a) **Batch 3, city 3 = DENVER: RESEARCH DONE, nothing staged yet. No
project file was touched this session (the tree is at the 193 baseline: module 16 QIDs / 23 rows, doc
875 lines / 21 sections, suite baseline 177/1/0) - all research artifacts live in /tmp (below). The landing
(module edit -> --verify -> stage -> --check -> doc splice -> --golden -> tests -> commit) is the whole of
the next session.**

### What 194 found (all artifacts in /tmp; re-verify anything you rely on)

- **QID = Q16554** (Denver, the consolidated city-county and capital of Colorado). My first guess Q3101 is
  a PERSON (Patrick Ricard) - caught by the label check, the usual class. Live facts (script
  /tmp/aw236b_b3_dvr_qid.py, run under .venv): label "Denver"; **P625 = the city's ONLY value
  (-104.984722, 39.739167, precision 0.000278 deg = 30 m)** - the central CBD (the 16th-20th-street core);
  **P373 = the STRING "Denver, Colorado"** (the usual quirk - write the place from the county + state);
  **P131 = Q1261 Colorado + Q13052701 Denver County** (Denver is a consolidated city-county, like New
  Orleans is a city-parish - hence place **"Denver County, Colorado"**); P17 = Q30; enwiki "Denver".
  **Name search: NO TRAP** - the first hit with P625 is Q16554 itself (dist 0). No existing site holds
  Denver (grep of data/catalog/{sites,extras,extras_us_cities}.jsonl + web/data/sites.json: nothing).
  Site id = catalog.slug("Denver") + qid = **denver-q16554** (slug verified: catalog.slug returns "denver").
- **Pool** (/tmp/aw236b_b3_dvr.py -> /tmp/aw236b_b3_dvr.json; log /tmp/aw236b_b3_dvr.log): the 6 plain-phrase
  forms + " filetype:bitmap" -> **65 unique, 33 good** (good = commons.keep() + caption gate + Public domain
  + >= 4000 px wide).
- **THE PICK: `File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg`** (19338x13294, PD, page
  date 1908 = the drawing's year so no Zwolle swap; artist "Birdseye View Publishing Co.; Denver Lith.
  Co."; desc "Perspective map not drawn to scale. Includes illus. and index to points of interest. LC
  Panoramic maps (2nd ed.), 66"). Sheet banner: "BIRD'S EYE VIEW OF DENVER, COLORADO, 1908 LOOKING SOUTH
  FROM THE TWENTY-THIRD STREET VIADUCT" - **the steepest (near-vertical) whole-city view in the pool, drawn
  from the north of the city looking south** (the viaduct ~1.3 km north of the site's point: measured
  23rd-street lat 39.7508 vs P625 39.7392 = 0.0116 deg x 110900 m/deg = 1287 m): the dense grid legible to
  the southern suburbs, the Front Range along the top of the sheet (the southern horizon), the South Platte
  meandering in from the northwest along the sheet's RIGHT side (the sheet faces south, so west is right),
  landmark index across the bottom. **Same-sheet scans (one row per sheet, the LOC .jpg staged): the
  19338x13294 .tif twin and the 9000x6205 DPLA copy
  `File:Birdseye view of Denver, Colorado, 1908 - DPLA - 4ac8083cbba722c01cad3388a37a7a0f.jpg`.**
- **DROPS (for the lead-doc section; the 1280-px eyeball pass is in /tmp/aw236b_b3_dvr_thumbs/, 16 files
  covering every distinct sheet):** (1) 1881 J. H. Flett `LOC 75693129` .jpg/.tif (4348x2857, "Photocopy",
  LC Panoramic 63, an inset "view of Denver 1859") - steep near-vertical whole-city view, but the LOC copy
  is a PHOTOCOPY and the pool's smallest: shallower-quality same-genre sheet (one row per city, 1908 is
  steeper and sharper). (2) 1887 Rocky Mountain News / Mills Eng. Co. `LOC 75693131` .jpg/.tif (8048x6016,
  LC Panoramic 64) + two 7000x5238 DPLA copies (0f7a446c6bae62a89803fc9a678bd56d /
  bd8a42c6f6cc094cdbb1f945dea8bc03) - steep oblique from the NW (the Capitol foreground bottom, the grid
  receding to the mountain horizon): shallower than the 1908. (3) 1882 C. H. Platt / W. H. Slocum chromo
  DPLA 10000x6774 (2030beda70ef9c5d6b411eb7b9238320) + 8999x6096 (495911c20e204fc964c6cb98161cd41c) -
  steep oblique from the north (the Platte in the foreground): same-genre dupe, shallower. (4) **1874
  E. S. Glover** (Strobridge & Co. Lith., "Denver in 1865" inset): the pool's oldest whole-city view, from
  the NW looking SE - DPLA 10000x7749 (f0ef7f8d025e3af38f550c86d8f0e99e, page date 1874) + 8999x6974
  (7f6b1ead5d4aa502d6bdaf3c7b43167a, undated) are same-sheet dupe scans; the three 1536-px copies
  (94f7c085b5e7fb9adaa7558d17cb6db7 / d5be6563e467387d78d7d7e524a9cb99 / aae0b82d22cdb8dd268462fb955a8838)
  are TOO SMALL (<4000 px). (5) 1887 "Souvenir of Arbor Day, May 6th 1887. Birds eye view of Colfax avenue
  from Montclair, 350 ft. above" (two 7000x3920 copies) - district close-up (the Fort-Negley class);
  THUMB FETCHED (aw236b_b3_dvr_thumbs3.log) but NOT yet eyeballed - confirm before final wording. (6) 1895
  "View in Denver. 'Birds-eye view of the line waiting for the touch of the Healer'" (two 4096x3281
  copies) - a street-car SCENE, not a city view; thumb fetched, not yet eyeballed. (7) 1907 "Birdseye view
  from South Broadway ... showing Harlem, Jacksons Broadway Heights & city of Denver" - four scans (two
  7888x6144 incl. `CO Denver 1907.jpg`, two 7992x6273) - a REAL-ESTATE AD ("LOTS FOR SALE", A.F. Haraszthy
  & W.J. Vuit, copyright 1908): the suburban subdivisions fill the sheet, the city a small dot on the
  horizon. (8) 1913 "Birds-eye view of Denver and the Rockies as viewed from the tower of the Daniels and
  Fisher Store" (two 12000x5339/5357 copies) - a PHOTOGRAPH (copyright 1913 by the Daniels & Fisher Store
  Co.), city small in a mountain panorama (the photo + Bohn-class precedent); the 1755x3612 copy of it is
  too small. (9) "Bird's eye view Clayton Industrial School Denver, Colorado" (4017x1780) - institution
  close-up (the Fort-Negley class). (10) "Bird's eye view of the mountains & plains from 'Lookout Mountain'
  Denver's summer resort" (7000x5587) - regional view, Denver a dot bottom-centre (the DC-Bohn
  precedent). (11) "Topographical birds-eye view, the state of Colorado" (DPLA 5000x3680, Clason Map Co.)
  - STATE-level view; the pool's "1603" year is a FALSE year picked up from the DPLA hash in the title
  (94ad02d5d2fbe5c1603...). (12) other-city caption-gate rejects: 1873 Golden, 1874 Pueblo, 1882 Canon
  City / Greeley / Gunnison / Leadville (three) / Maysville / Colorado Springs+Manitou, 1904 Las Animas
  (two); too-small: 1865 Kilburn (two, 2737x1391), 1889 `CO Denver 1889.jpg` (1024x656), 1890 "World's
  pictorial line ... Great Plains" (1536x618) and its "(Covers to)" / "(Text Page to)" Great Plains +
  Texas Panhandle book sheets (1536x612, 2459x2847, 4026x1680, 4087x4634, 22726x9036 - the KC Union Pacific
  book-sheet precedent, regional); 1907 CC BY-SA `Denver, CO 1907 Bird's Eye View.jpg` (1500x1000);
  2021 `Union Station North 002.jpg` (CC0, 1904x1413, beyond the 1925 MAX_YEAR); the 4000x2867 Buena Vista
  and 7000x3180 Idaho Springs sheets (caption gate).

### Next session: the Denver LANDING (the per-city playbook, the 189/190/192/193 pattern)

1. Quick re-checks: eyeball the two fetched-but-unseen thumbs (Arbor Day / Healer) in
   /tmp/aw236b_b3_dvr_thumbs/ to finalize their drop wording; re-confirm the pick is still on Commons and
   PD (the stage's live commons.info re-check does this anyway).
2. **Module edit** (fit/src_us_birdseye.py): SITES header batch line "Batch 3 (checked live
   2026-10-14): Kansas City, New Orleans, Denver."; SITES entry for Q16554 AFTER Q34404 (id denver-q16554,
   name/named "Denver", lon -104.984722, lat 39.739167, place "Denver County, Colorado", region United
   States, kind town, wikipedia https://en.wikipedia.org/wiki/Denver; comment = single-P625 30 m
   central-CBD / consolidated city-county P131 (Colorado + Denver County) / string-P373 / P17 Q30 / no
   name-search trap / the Q3101-mislabel note; note = the aerial-ground template + "steep near-vertical
   whole-city view drawn from the north of the city (the sheet's title: 'Looking South from the
   Twenty-Third Street Viaduct', ~1.3 km north of the site's point) - the dense grid legible to the
   southern suburbs, the Front Range along the top of the sheet (the southern horizon), the South Platte
   meandering in from the northwest along the sheet's right side (the sheet faces south, so west is
   right), spanning the whole city far beyond the 2000 m town box, so its fit is likely to end a review
   item (the 236a NY-1811 / DC-ring precedent)"); `DENVER_1908` rows list after BACHMAN_1851 (the .jpg
   row, comment = the pick + the two same-sheet scans + pointer to the lead doc); SOURCES key
   `"denver_1908": dict(rows=DENVER_1908, p="birdseye", label="{name}, the Birdseye View Publishing Co.
   bird's-eye view (1908)")`.
3. **`--verify`** (17 QIDs, all table QIDs re-checked) -> save the run's EXACT output to
   /tmp/aw236b_verify_194.txt (the doc carries it verbatim; the module prints the Denver line with
   `P625: [(-104.98472222222, 39.739166666667)]`, `P373: ['Denver, Colorado']`,
   `P131: [('Colorado', 'Q1261'), ('Denver County', 'Q13052701')]`, enwiki 'Denver', search first hit with
   P625 = Q16554 dist 0).
4. **--dry** (expect 1 new site denver-q16554 / 1 new picture) -> **stage** (live commons.info re-check) ->
   **--check** (expect 24/24 PASS caption_coords; save /tmp/aw236b_check_194.txt).
5. **Lead doc** splice (script pattern /tmp/aw236b_doc_192.py, three regions: (a) QID section = new
   17-QID verbatim transcript + intro updated to "seventeen" and the batch-3 close-out mention of Denver;
   (b) NEW "## Denver (site `denver-q16554`, this task's point = the verified P625; 1 view staged)"
   section BETWEEN New Orleans and Staging: STAGED bullet (the 1908 sheet per step 2's note, the two
   same-sheet scans, the 1908 date, no swap) + the DROP list above (per-item reasons) + the QID-facts
   paragraph; (c) Staging = **seventeen cities / 24 views / thirteen site rows** + the new verbatim check
   transcript + "golden pins the 24 rows" + "Not done yet: 8 more (25 total, 17 done), next: St. Paul,
   Minneapolis, Cleveland").
6. **--golden** (13 extras / 24 files / 24 classified) + **extend tests/test_src_us_birdseye.py exactly as
   190/193 did**: module docstring batch-3 line gains Denver (the 1908 Birdseye View Publishing Co.
   view) + "thirteen new-cities site rows"; test-1 PASS-key list + the Denver key
   (denver-q16554|File:Bird's eye view of Denver, Colorado, 1908. LOC 75693133.jpg); test-3: SITES-id
   table +Q16554:denver-q16554, extras-id table + the same, years +the 1908 title:1908, points
   +denver-q16554:(-104.984722, 39.739167), named_by_qid +Q16554:Denver, len(files) 23 -> 24.
7. **Module tests 5/5, then the FULL suite; restore all ten docs/site_flow/307d_*.png to main's bytes
   before committing** (the PITFALLS test_owner_check rule); commit `236b: Denver staged (the 1908
   Birdseye View Publishing Co. view, looking south from the Twenty-Third Street Viaduct) - ...`.

### Rules (unchanged)

NEVER write the canonical files (that is 236c); NEVER touch 236a's extras_us_cities.jsonl (read-only; the
module's _shared_site enforces it); run live commands under .venv/bin/python (system python3 has no numpy;
the module top stays stdlib-only); the golden sample is the contract (--golden only for an intended
change); the full suite re-encodes up to ten docs/site_flow/307d_*.png every run - restore main's bytes
before committing (the PITFALLS entry on test_owner_check); tests never bind fixed network ports or write
outside the project + the temp dir; when recording a distance/direction claim in a doc or comment,
MEASURE it (the 1.3 km viaduct distance above is measured: 23rd-street lat 39.7508 - P625 39.739167 =
0.0116 deg x 110900 m/deg = 1287 m).
