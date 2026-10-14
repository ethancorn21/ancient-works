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

(2026-10-14, iteration 184, agent a) **Batch 2 LANDED: 14 cities staged (4 owner + 5 batch 1 + 5
batch 2), 21 file rows, all verified (14-QID --verify clean, --check 21/21 PASS, module tests 5/5,
full suite 177/1/0 green in 517 s).** The context limit hit before the commit: all of it is in the
working tree (the driver will sweep it like it did 183's). What remains: (0) the commit, (A) the
batch-2 lead doc (five city sections + the 14-QID verify transcript + the Staging section), (B)
batch 3 and up (the last 11 cities for box 4, which ticks at >=25 cities total).

### State of the files (post-184)

- fit/src_us_birdseye.py: 14 SITES (batch 1: boston-q100, philadelphia-q1345, baltimore-q5092,
  pittsburgh-q1342, cincinnati-q43196; batch 2: louisville-q43668, st-louis-q38022, chicago-q1297,
  detroit-q12439, milwaukee-q37836) and 21 SOURCES. Unchanged this session (183's edit was committed
  by the driver in 3d367d5). Its comments carry the batch-2 picks, the same-sheet scans and the drop
  reasons - the source of truth for the lead doc.
- data/catalog/extras_us_birdseye.jsonl: 10 site rows (+5 this session); data/commons/
  files_us_birdseye.jsonl and classified_us_birdseye.jsonl: 21 rows each (+5 this session). All new
  rows verified (the 184 DECISIONS entry has the details).
- tests/golden/src_us_birdseye_sample.json: the 21-row pin (regenerated this session - intended).
- tests/test_src_us_birdseye.py: extended for batch 2 this session (SITES/extras/years/points/named
  tables + len(files) 21 + docstrings) - 5/5 green.
- docs/lead_us_birdseye.md: still at the batch-1-complete state (only 183's one-line typo fix since)
  - the batch-2 sections are NOT written. That is work A.
- Transcripts (may be wiped; re-run to regenerate): /tmp/aw236b_verify_184.txt (14 QIDs, all clean),
  /tmp/aw236b_check_184.txt (21-line --check, exit 0), /tmp/aw236b_stage_184.txt, /tmp/aw236b_dry_184
  .txt.
- Batch-2 research (may be wiped; all regenerable): /tmp/aw236b_b2.py (the pool builder: per-city
  Commons file-namespace searches, 6 plain-phrase forms + the St. Louis "Saint Louis bird's eye view"
  form, each + " filetype:bitmap"; commons.info 50/call at 1/s; keep() + 600-char caption gate +
  Public domain + >=4000 px wide), /tmp/aw236b_b2.json (full pool with per-file metadata),
  /tmp/aw236b_b2_cands.json (the 22 good candidates), /tmp/aw236b_b2_thumbs/ (the 1280 px thumbs
  183 eyeballed).

### NEXT (exact, in order)

0. **Commit the uncommitted batch-2 work** (only if the driver has not already swept it - check
   `git status`): the working tree holds data/catalog/extras_us_birdseye.jsonl (+5 site rows),
   data/commons/files_us_birdseye.jsonl and classified_us_birdseye.jsonl (+5 rows each),
   tests/golden/src_us_birdseye_sample.json (the 21-row pin), tests/test_src_us_birdseye.py (the
   batch-2 table extension), this task file, DECISIONS.md, and the five regenerated
   docs/site_flow/307d_*.png (the 307d screenshot test rewrites them every full-suite run; the
   bytes vary between runs). Commit them together: "236b: batch 2 landed - staged Louisville, St.
   Louis, Chicago, Detroit, Milwaukee (10 site rows / 21 file rows), 14-QID verify clean, golden +
   tests extended, suite 177/1/0 - the 307d pngs are this session's test output, not 236b work".
   Then step A.
A. **Batch-2 lead doc** (box 1's per-view coverage for the five new views; all in
   docs/lead_us_birdseye.md):
   1. Replace the "QID verification" section (line ~69, currently the 9-QID transcript) with a fresh
      14-QID transcript: re-run `.venv/bin/python fit/src_us_birdseye.py --verify` (184's run =
      /tmp/aw236b_verify_184.txt: all clean, zero flags; the two in-flag name-search traps are
      Pittsburgh -> Q235034 and Chicago -> Q131252; St. Louis P131 = Missouri only; Milwaukee P131 =
      three counties).
   2. Insert five city sections after the Cincinnati section and before "Staging and checks"
      (Louisville, St. Louis, Chicago, Detroit, Milwaukee), in the batch-1 style: the STAGED view
      (date / artist / publisher / resolution / apparent angle + the same-sheet scans from the module
      comments) plus the DROP list with reasons per non-staged candidate - derive each reason from
      the pool metadata (/tmp/aw236b_b2.json: license, dims, desc) and 183's eyeballs (the thumbs are
      still on disk in /tmp/aw236b_b2_thumbs/; if wiped, re-download the 1280 px thumbs and re-
      eyeball - the pool builder regenerates everything). Known from the module comments: St. Louis =
      seven "(... detail)" tiles + DPLA mirrors (No restrictions, not PD) + two book-print
      photographs; Chicago = the 1893 chromolithograph (the same view in colors); Detroit = four
      further scans of the staged sheet; Louisville = the .tif twin + the 1876 sheet; Milwaukee =
      further 1872 scans + the 1879/1858/1882 views.
   3. Update "Staging and checks": 21 views (11 owner + 5 batch 1 + 5 batch 2), the 10 site rows in
      extras_us_birdseye.jsonl, a fresh 21-line --check transcript (re-run --check), and "not done
      yet: 11 more cities (25 total, 14 done)".
   4. Commit: "236b: batch 2 complete - lead doc: 14-QID verify transcript, five city sections
      (STAGED/DROP), 21-view staging section".
B. **Batch 3 (~5 cities; ~6 remain after it - box 4 ticks at >=25 cities total, then Status: done)**:
   candidates: Kansas City first, then New Orleans, Denver, St. Paul, Minneapolis, Cleveland, ...
   (the LOC Panoramic collection, 1847-1929; a city with no usable view gets a lead-doc note and the
   next candidate). Same per-city procedure as batches 1/2 (181's playbook, restated in the 184
   DECISIONS entry): (1) QID check against sites.jsonl + extras.jsonl + extras_us_cities.jsonl +
   web/data/sites.json (never two sites for one QID); (2) pool search (plain-phrase forms +
   " filetype:bitmap", commons.info 50/call at 1/s, keep() + gate + PD + >=4000 px); (3) pick the
   ONE steepest view (near-vertical, grid legible, PD, >= ~4000 px wide; DROP pictorial/regional/
   fort-close-up/photo/street-car-map/railway-sheet; eyeball 1280 px thumbs to dedupe same-sheet
   scans, one row per sheet, keep the LOC/largest scan); (4) verify the QID live with --verify
   (watch name-search traps - Chicago's is the in-table example); (5) SITES + SOURCES entries;
   (6) --dry, stage, --check (exit 0); (7) lead-doc section per city + re-run --verify (the
   transcript grows); (8) --golden, then the module tests + the full suite (extend the test tables
   exactly as 184 did).

### Rules (unchanged)

NEVER write the canonical files (data/commons/files.jsonl etc. - that is 236c); NEVER touch 236a's
extras_us_cities.jsonl (read-only; the module's _shared_site enforces it); run live commands under
.venv/bin/python (system python3 has no numpy; the module top stays stdlib-only); batch size ~5
cities/session to fit the context limit; the golden sample is the contract (--golden only for an
intended change); the full suite rewrites the five docs/site_flow/307d_*.png every run - if the
bytes change, carry them in the commit with the 306g-style disclosure (the 184 commit did).
