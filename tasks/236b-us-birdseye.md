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

(2026-10-14, iteration 187, agent a) **Work A (the batch-2 lead doc) is DONE on disk, UNCOMMITTED**
(the harness saved the edit; the working tree holds the rewritten docs/lead_us_birdseye.md - 715
lines, was 482). This session found iteration 186's uncommitted transcripts on disk
(/tmp/aw236b_verify_186.txt = the 14-QID live --verify, /tmp/aw236b_check_186.txt = the 21-line
offline --check; 186 had hit its context limit before writing the doc), verified both are
content-identical to 185's, cross-checked every title / dimension / licence in the five new city
sections against /tmp/aw236b_b2.json and the fit/src_us_birdseye.py comments, and spliced the doc
in three places (below). Structure verified (19 ## headings in order, fence pairs intact), but
**no fresh-eyes re-read of the full new doc has happened yet**, and the module tests were NOT
re-run this session (last run: 184, 5/5 green - a docs-only change cannot affect them).

### The doc as it now stands (docs/lead_us_birdseye.md, UNCOMMITTED)

1. **QID verification section** (lines 69-175): new intro (14 QIDs re-checked at the batch-2
   close-out; NO P625 flag on any of the fourteen - Q62's two P625s 2.0-2.4 km from its refined
   table point, Q23197's 721 m NE, the ten new-city points ARE the P625s, dist 0; two
   name-search traps: Pittsburgh -> Q235034 University of Pittsburgh ~4.7 km west, Chicago ->
   Q131252 University of Chicago ~10.5 km south - both within the 50 km flag so not flagged, but
   record --live would store the university's point, the staged rows hand-record the city P625s;
   Baltimore P131 two values -> "Baltimore City, Maryland"; St. Louis P131 = Missouri only ->
   "St. Louis City, Missouri"; Milwaukee P131 three counties, point in Milwaukee County) + the
   verbatim 14-QID transcript from /tmp/aw236b_verify_186.txt (header "checked 2026-10-14 - 14
   QIDs (Wikidata)", sorted Q100 ... Q62; identical to 185's run).
2. **Five city sections inserted** between Cincinnati and "Staging and checks" (Louisville line
   475, St. Louis 507, Chicago 552, Detroit 605, Milwaukee 635), batch-1 style: STAGED bullet
   (year / artist / publisher / dims / PD / LC Panoramic no. / angle / same-sheet scans) + DROP
   list with per-item reasons (all titles/dims/licences verified this session against
   /tmp/aw236b_b2.json). Chicago carries the name-search-trap paragraph. Two corrections vs the
   185 hand-over draft: the "Saint Louis"-titled St. Louis detail tile fails the **caption gate**
   (pool gate=False, keep=True - the doc says "fails the caption gate on its title"), and Detroit
   has **SIX** further scans of the staged sheet (LOC .tif twin, LCCN2003666422 .jpg/.tif, Cuerden
   .jpg/.png, "Map image detroit.jpg") - the doc says "Six further scans".
3. **Staging and checks section** (line 669 to end): "All **fourteen** cities... **21 views**
   total (11 owner + one per each of the ten batch-1/batch-2 cities)...; the **ten** site rows
   are in extras_us_birdseye.jsonl" + the verbatim 21-line --check transcript from
   /tmp/aw236b_check_186.txt (ends "evidence: 21 rows, 21 pass, 0 fail, 0 no-tie") + "the golden
   sample pins the 21 rows" + "Not done yet: **11 more US cities** (25 total, 14 done); next
   candidates **Kansas City, New Orleans, Denver, St. Paul, Minneapolis, Cleveland**, ...".

### What to do next (one session, in order)

1. **Fresh-eyes re-read** of the three edited regions of docs/lead_us_birdseye.md (QID section
   69-175, the five city sections 475-668, Staging 669-715) - check the transcripts are intact,
   fences balanced, prose reads right; fix anything. (The content files used for the splice are
   /tmp/aw236b_doc_qid_187.md and /tmp/aw236b_doc_cities_187.md - may be wiped; the doc itself is
   the artifact.)
2. **Run the module tests** (offline): `.venv/bin/python -m pytest tests/test_src_us_birdseye.py
   -q` - expect 5/5 green (docs-only change; last run 184 = 5/5).
3. **Commit**: `git add docs/lead_us_birdseye.md DECISIONS.md tasks/236b-us-birdseye.md && git
   commit -m "236b: batch 2 complete - lead doc: 14-QID verify transcript, five city sections
   (STAGED/DROP), 21-view staging section"`. No full suite this session, so **no 307d png
   disclosure needed**.
4. **Batch 3** (following sessions, ~5 cities each; ~2 batches to reach 25 cities, then box 4
   ticks and Status: done). Per-city procedure (181's playbook, restated in the 184 DECISIONS
   entry): (1) QID check against data/catalog/sites.jsonl + data/catalog/extras.jsonl +
   data/catalog/extras_us_cities.jsonl + web/data/sites.json (never two sites for one QID);
   (2) pool search: per-city Commons file-namespace search, the 6 plain-phrase forms ("bird's-eye
   view of <city>", "bird's eye view of <city>", "birdseye view of <city>", "<city> bird's eye",
   "<city> birdseye", "Birds' eye view of <city>" - quoted-intitle queries find NOTHING) each +
   " filetype:bitmap", commons.info 50/call at 1/s (a batch-3 builder = /tmp/aw236b_b2.py with the
   CITIES list changed - it lives in /tmp, may be wiped, but it is a ~55-line stdlib+commons
   script); gate = commons.keep() + 600-char caption gate (norm(city) in norm(title+desc)) +
   Public domain + >=4000 px wide; (3) pick the ONE steepest view (near-vertical, grid legible;
   DROP pictorial/regional/fort-close-up/photo/street-car/railway/exposition; eyeball 1280 px
   thumbs to dedupe same-sheet scans - thumb URLs via the Commons API imageinfo thumburl
   iiurlwidth=1280 via .venv's commons.get, commons.info has no 'thumb' key - one row per sheet,
   keep the LOC/largest scan); (4) verify the QID live with --verify (watch name-search traps -
   Chicago's Q131252 is the in-table example; a university hit within 50 km is not flagged but
   would be stored by record --live); (5) SITES + SOURCES entries in fit/src_us_birdseye.py (the
   batch-2 entries at ~line 150-213 / 350-400 are the pattern: SITES comment = P625/P131/enwiki/
   point-derivation + name-search trap if any; SOURCES comment = pick + same-sheet scans + drop
   summary pointing at the lead doc); (6) --dry then stage (live commons.info re-check of every
   title) then --check (exit 0); (7) lead-doc section per city in the style above + re-run
   --verify (the transcript grows by one QID per new city); (8) --golden (intended change),
   extend tests/test_src_us_birdseye.py exactly as 184 did (SITES-id table, extras-id table,
   per-title year, evidence-points, named-place, len(files) 21 -> 26 for batch 3), then module
   tests + the full suite (if it rewrites docs/site_flow/307d_*.png, carry them in the commit
   with the 306g-style disclosure). Candidates in order: Kansas City, New Orleans, Denver,
   St. Paul, Minneapolis, Cleveland, ... a city with no usable view gets a lead-doc note and the
   next candidate. Batch 3 = the first five; batch 4 = the remaining ~6 to reach 25.

### State of the files (post-187; doc edit UNCOMMITTED in the working tree)

- docs/lead_us_birdseye.md: **MODIFIED, uncommitted** - the batch-2 lead doc as described above
  (715 lines). Commit per step 3.
- fit/src_us_birdseye.py: 14 SITES / 21 SOURCES (committed; its comments are the source of truth
  and now match the doc).
- data/catalog/extras_us_birdseye.jsonl: 10 site rows; data/commons/files_us_birdseye.jsonl +
  classified_us_birdseye.jsonl: 21 rows each (committed by the driver in f206b2f).
- tests/golden/src_us_birdseye_sample.json: the 21-row pin; tests/test_src_us_birdseye.py: 5/5
  green as of 184.
- /tmp (may be wiped, all regenerable): /tmp/aw236b_verify_186.txt + /tmp/aw236b_check_186.txt
  (now embedded verbatim in the doc - no longer needed); /tmp/aw236b_b2.py (the batch-2 pool
  builder - the template for the batch-3 builder), /tmp/aw236b_b2.json (full 5-city pool with
  per-file metadata - the source of the DROP facts now in the doc), /tmp/aw236b_b2_cands.json,
  /tmp/aw236b_b2_thumbs/ (32 thumbs - the eyeballs are done and recorded; moot). Older b1/check/
  verify/stage/dry transcripts are from batches 1/2 - the doc now carries both transcripts.

### Rules (unchanged)

NEVER write the canonical files (data/commons/files.jsonl etc. - that is 236c); NEVER touch 236a's
extras_us_cities.jsonl (read-only; the module's _shared_site enforces it); run live commands under
.venv/bin/python (system python3 has no numpy; the module top stays stdlib-only); batch size ~5
cities/session to fit the context limit; the golden sample is the contract (--golden only for an
intended change); the full suite rewrites the five docs/site_flow/307d_*.png every run - if the
bytes change, carry them in the commit with the 306g-style disclosure (the 184 commit did); tests
never bind fixed network ports or write outside the project + temp dir.
