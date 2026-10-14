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

(2026-10-14, iteration 193, agent a) **Batch 3, city 2 = NEW ORLEANS: fully LANDED and committed (fac9933) - module + staged files + lead doc + golden + tests all at 16 cities / 23 views / 12 site rows; full suite 177/1/0 green. Next session: batch 3, city 3 = DENVER (playbook below).**

### What 193 did

1. **Driver-mandated merge main -> agent/a (commit c882104):** six `docs/site_flow/307d_{A_2-placed,A_3-gestured,A_4-saved,A_5-reload,B_4-saved,B_5-reload}.png` conflicts. Per PITFALLS (test_owner_check re-renders all ten 307d PNGs every run and never diffs against the committed bytes; neither side of such a conflict carries unique content): resolved to main's bytes (`git checkout --theirs`), ran `tests/test_owner_check.py` in the merged tree (2 passed, 68 s) + the full suite (175 passed / 1 skipped / 2 failed - the two failures were this branch's expected in-flight state, inherited from the driver's sweep de6a463: staged 23 rows vs the then-22-row golden/tests). Committed the merge with that disclosed.
2. **New Orleans landing (the 192 hand-over's exact next steps, all done):**
   - **Doc splice**: ran `.venv/bin/python /tmp/aw236b_doc_192.py` (it survived in /tmp; I verified its preconditions first: 20 ## sections, both headings exact, the two transcripts carry its asserted markers). docs/lead_us_birdseye.md is now 875 lines / 21 ## sections: the QID section (new 16-QID intro + verbatim /tmp/aw236b_verify_192.txt), the NEW "## New Orleans (site `new-orleans-q34404`, ...; 1 view staged)" section between Kansas City and Staging (STAGED bullet: 1851, drawn from nature on stone + printed by J. Bachman, published by the agents A. Guerber & Co, 5843x4600, PD, NYPL Hades-118746-54871 / Stokes 1851-G-13 / Deak 605, LOC twin 93500720 LC Panoramic 240.1, drawn from the river side looking east/northeast, the oldest staged view of the project + the full DROP list + the QID-facts paragraph), and the Staging section at sixteen cities / 23 views / twelve site rows + verbatim /tmp/aw236b_check_192.txt + "golden pins the 23 rows" + "Not done yet: 9 more (25 total, 16 done), next: Denver, St. Paul, Minneapolis, Cleveland".
   - **--golden**: tests/golden/src_us_birdseye_sample.json = 12 extras / 23 files / 23 classified.
   - **tests/test_src_us_birdseye.py extended exactly as 190 did** (pattern: commit 7771bc6's diff): module docstring batch-3 line "Kansas City the 1869 Ruger ... and New Orleans the 1851 Bachman view (the oldest staged view of the whole project)" + "twelve new-cities site rows"; test-1's PASS-key list + the NO key; test-3: docstring site list, SITES-id table +Q34404, extras-id table +new-orleans-q34404, years +1851 for the NYPL Hades tif, evidence point +(-90.078333, 29.976111), named-place table +"New Orleans", len(files) 22 -> 23.
3. **Verification:** module tests 5/5 (2.3 s); offline `--check` exit 0, 23/23 PASS (matches the 192 transcript in the doc); full suite **177 passed / 1 skipped / 0 failed** (506 s). The suite run re-encoded seven 307d PNGs - restored all ten to main's bytes before committing, so fac9933 carries only the doc + golden + tests (the PITFALLS restore rule, not the 184-style carry).

### State (fresh for the next session)

- docs/lead_us_birdseye.md: 875 lines, 21 ## sections: Fetch route, the four owner-named cities, QID verification, The evidence field, then 16 city sections (New York, Washington DC, San Francisco, Nashville, Boston, Philadelphia, Baltimore, Pittsburgh, Cincinnati, Louisville, St. Louis, Chicago, Detroit, Milwaukee, Kansas City, New Orleans), Staging and checks.
- fit/src_us_birdseye.py: 16 QIDs (4 shared + 12 SITES), 23 SOURCES keys. All committed.
- Staged files (committed): data/catalog/extras_us_birdseye.jsonl 12 site rows; data/commons/files_us_birdseye.jsonl + classified_us_birdseye.jsonl 23 rows each.
- tests/golden/src_us_birdseye_sample.json: the 12/23/23 pin. Module tests 5/5; full suite green (baseline 177/1/0).
- Box 4 progress: 16 of 25 cities staged. 9 remain; the doc's "Not done yet" order: **Denver, St. Paul, Minneapolis, Cleveland**, ... (batch 3 was 4 cities per the 189 plan: Kansas City, New Orleans, Denver, St. Paul; batch 4 after).

### Next session: batch 3, city 3 = DENVER (the per-city playbook, the 189/190/192 pattern)

1. **QID check against existing sites** (never two sites for one QID): grep the city name in data/catalog/sites.jsonl, data/catalog/extras.jsonl, data/catalog/extras_us_cities.jsonl, web/data/sites.json. New city -> point = the city's P625 (record any refinement). Watch the string-P373 quirk (Kansas City/New Orleans had it - the place is written from P131 + the state, never from a string P373); a single-parish/city P131 (like New Orleans) is the consolidated-city case.
2. **Pool search**: per-city Commons file-namespace search, the 6 plain-phrase forms ("bird's-eye view of <city>", "bird's eye view of <city>", "birdseye view of <city>", "<city> bird's eye", "<city> birdseye", "Birds' eye view of <city>" - quoted-intitle queries find NOTHING) + " filetype:bitmap"; commons.info 50/call at 1/s. Builder template: /tmp/aw236b_b3_kc.py or /tmp/aw236b_b3_no.py (change CITIES; both ~55-line stdlib+commons scripts - if /tmp is wiped, the 189 hand-over text in DECISIONS.md describes the shape). Gate = commons.keep() + 600-char caption gate (norm(city) in norm(title+desc)) + Public domain + >= 4000 px wide.
3. **Pick the ONE steepest view** (near-vertical, grid legible; DROP pictorial/regional/fort close-up/photo/street-car/railway/exposition); eyeball 1280-px thumbs (imageinfo thumburl iiurlwidth=1280 via .venv's commons.get) to dedupe same-sheet scans; one row per sheet, keep the LOC/largest scan.
4. **Verify the QID live**: `.venv/bin/python fit/src_us_birdseye.py --verify QID` - watch name-search traps (a university hit within 50 km is in-flag, NOT a trap; the real traps are the Chicago Q131252 / Pittsburgh Q235034 class where the FIRST hit with P625 is not the city). Save the fresh 17-QID transcript to /tmp/aw236b_verify_194.txt (the doc carries it verbatim - the transcript must be the run's exact output).
5. **Module edit**: SITES header batch line gains Denver; SITES entry (id = catalog.slug of name + QID, the P625 point, place from P131 + state, note = the aerial-ground template + the view's apparent angle + the beyond-the-box review-item line); SOURCES key + rows list (comment = the pick + same-sheet scans + drop summary pointing at the lead doc). **MEASURE every distance/direction claim before writing it** (188's NE/west errors, 191's 9109->7943 km, 192's orientation clash are exactly that class).
6. **--dry -> stage (live commons.info re-check) -> --check** (expect 24/24 PASS; save /tmp/aw236b_check_194.txt).
7. **Lead doc** (splice script pattern = /tmp/aw236b_doc_192.py: asserts each heading occurs once, splices, self-checks fences/order; /tmp may be wiped - the 193 DECISIONS entry describes the three regions): (a) QID section = new 17-QID verbatim transcript + intro update; (b) new "## Denver (site `denver-q...`, ...)" section after New Orleans (STAGED bullet + DROP list with per-item reasons + QID-facts paragraph); (c) Staging = seventeen cities / 24 views / thirteen site rows + verbatim check transcript + golden pins the 24 rows + "Not done yet: 8 more (25 total, 17 done), next: St. Paul, Minneapolis, Cleveland".
8. **--golden** (13 extras / 24 files / 24 classified) + extend tests/test_src_us_birdseye.py exactly as 190/193 did (SITES-id table, extras-id table, per-title year, evidence point, named-place table, len(files) 23 -> 24, the PASS-key line in test-1) + module tests (expect 5/5), then the full suite; **restore all ten docs/site_flow/307d_*.png to main's bytes before committing** (PITFALLS rule); commit `236b: Denver staged (...) - ...`.

### Rules (unchanged)

NEVER write the canonical files (that is 236c); NEVER touch 236a's extras_us_cities.jsonl (read-only; the module's _shared_site enforces it); run live commands under .venv/bin/python (system python3 has no numpy; the module top stays stdlib-only); batch size ~5 cities/session to fit the context limit; the golden sample is the contract (--golden only for an intended change); the full suite re-encodes up to ten docs/site_flow/307d_*.png every run - restore main's bytes before committing (the PITFALLS entry on test_owner_check); tests never bind fixed network ports or write outside the project + the temp dir; when recording a distance/direction claim in a doc or comment, MEASURE it.
