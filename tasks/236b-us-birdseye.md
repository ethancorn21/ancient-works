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

(2026-10-14, iteration 182, agent a) **Merged main (37a26ee) and COMPLETED BATCH 1's leftover
(9 of 25 cities now staged; box 4 still UNTICKED - 16 cities to go).** The lead-doc edit from this
session is in the WORKING TREE, UNCOMMITTED (the harness saved it) - the next agent commits it after
a fresh-eyes re-read (exact steps below).

### Done this session (182), in order

- **Merge main (37a26ee, committed):** `git merge main` -> only 3 binary conflicts
  (docs/site_flow/307d_A_4-saved.png, 307d_A_5-reload.png, 307d_B_5-reload.png) - both sides are the
  307d screenshot test's own output (it rewrites the pngs every run); resolved to main's version
  (the other agents' finished work), ran the full suite in the merged tree (**177 passed, 1 skipped,
  0 failed in 518 s** - the 307d test passed, no flake), which regenerated 5 pngs (the 3 conflicts +
  307d_A_1-card + 307d_B_4-saved); staged the fresh output and committed the merge (the 306g-style
  disclosure is in the commit message + DECISIONS). Text files auto-merged cleanly.
- **Batch 1's loose ends closed with eyeballs (181's item 3):** the 3 non-LOC same-sheet scans the
  module claims were NEVER eyeballed in 181 (its verification download script had a syntax error and
  never ran) are now ALL CONFIRMED same-sheet against the staged LOC scans (1280 px thumbs from
  w/thumb.php, project UA, 2 s apart; files in /tmp/aw236b_chk182_*.jpg, may be wiped):
  - Philadelphia `File:Bird's-eye view of Philadelphia - drawn and engraved expressly for Harper's
    Weekly from sketches by Theodore R. Davis. LCCN2012645607.jpg` (10173x7287) = same sheet as staged
    LOC 75694509 (identical Harper's title block, grid, Delaware islands/ships; different physical
    copy: ragged margins, different hand-written accession numbers).
  - Pittsburgh `File:Pittsburgh 1902.jpg` (7256x4856, a 2010 scan, identical dimensions + same
    hand-written annotations) and `File:Thaddeus M. Fowler - Pittsburgh, Pennsylvania 1902.jpg`
    (7206x4806, Adam Cuerden, different copy) = same sheet as staged LOC 75696521 (identical
    PITTSBURGH./PENNSYLVANIA./1902 block, numbered index, FOWLER & MOYER copyright line).
  - BONUS (found while at it): Boston `File:1902 birds-eye view map of Boston featuring Beach and
    Clarridge Company.jpg` (8288x5712) = same sheet as staged LOC 75694559 (identical title block,
    key, B&C factory vignette).
  All module comments stand as written - NO softening needed, no code change.
- **Lead doc rewritten for batch 1 (EDIT APPLIED, UNCOMMITTED in the working tree):**
  docs/lead_us_birdseye.md - (a) the QID-verification section now carries the 9-QID transcript from
  the fresh `--verify` run (all clean; Pittsburgh's first search hit = Q235034 University of
  Pittsburgh, within the 50 km flag; Baltimore P131 has Maryland + Province of Maryland); (b) FIVE
  new city sections inserted before Staging (Boston/Philadelphia/Baltimore/Pittsburgh/Cincinnati,
  each: STAGED with date/artist/resolution/angle + same-sheet eyeball notes, DROP with reasons,
  RESERVED where applicable, the Pittsburgh trap called out); (c) "Staging and checks" now says 16
  views (11 owner + 5 batch-1), the 5 site rows in extras_us_birdseye.jsonl, the 16-line --check
  transcript (re-run this session: exit 0, 16/16 PASS), and "Not done yet: 16 more cities (25 total,
  9 done)" with the next candidates (Louisville, St. Louis, Chicago, Detroit, Milwaukee, ...).

### State of the files (post-182)

- fit/src_us_birdseye.py: 9 SITES (4 shared via SHARED_SITES + 5 batch-1: boston-q100,
  philadelphia-q1345, baltimore-q5092, pittsburgh-q1342, cincinnati-q43196), 16 SOURCES; UNCHANGED
  this session. data/catalog/extras_us_birdseye.jsonl: 5 site rows. data/commons/files_us_birdseye
  .jsonl + classified: 16 rows each. tests/golden/src_us_birdseye_sample.json: 16-row pin.
- docs/lead_us_birdseye.md: the 182 edit (above) is UNCOMMITTED - the harness saved it.
- Transcripts (may be wiped, re-run to regenerate): /tmp/aw236b_verify_182.txt (9-QID),
  /tmp/aw236b_check_182.txt (16-line --check); /tmp/aw236b_b1.json + b1.py = batch-1 pool builder
  (query forms + keep()/gate filter; batch 2 should rebuild its own pool the same way).
- Test state at hand-over: module tests 5/5 green after 181's edit; full suite 177/1/0 green on the
  merged tree THIS session (before the lead-doc edit - the doc is not test-covered; nothing in
  fit/pipeline/tests reads it). No code changed since the green run.

### NEXT (exact, in order)

1. Re-read the three edited lead-doc regions with fresh eyes (the doc was written under a context
   limit): the QID-verification block (must match /tmp/aw236b_verify_182.txt word-for-word, or re-run
   `--verify`), the five city sections, the Staging-and-checks block (the transcript must match
   /tmp/aw236b_check_182.txt or a fresh `--check`). Then commit it: `git add docs/lead_us_birdseye.md
   && git commit -m "236b: batch 1 complete - lead doc: 9-QID verify transcript, five city sections
   (STAGED/DROP/RESERVED, same-sheet eyeballs), 16-view staging section"`.
2. `.venv/bin/python -m pytest tests/test_src_us_birdseye.py -q` (expect 5 passed) and the full
   `.venv/bin/python -m pytest -q` (expect 177/1/0; if the 307d pngs regenerate again, carry them in
   the commit with the 306g disclosure, as 37a26ee/af5c91a did).
3. The 182 DECISIONS close-out entry was appended this session (after the 306 entry) - extend it
   only if steps 1-2 change the outcome (e.g. a test red).
4. **Batch 2 (~5 more cities; 16 remain after batch 2):** Louisville, St. Louis, Chicago, Detroit,
   Milwaukee, then Kansas City... - same per-city procedure as batch 1 (181's DECISIONS entry is the
   playbook): (1) catalog QID check first (sites.jsonl + extras.jsonl + extras_us_cities.jsonl -
   never two sites for one QID); (2) Commons file-namespace search (plain-phrase forms: "bird's-eye
   view of <city>", "<city> bird's eye view", "<city> birdseye", + "Birds' eye view of <city>", each
   + " filetype:bitmap" - the batch-1 query set in /tmp/aw236b_b1.py; commons.info 50/call at 1/s,
   keep() + the 600-char caption gate); (3) pick the ONE steepest view (near-vertical, grid legible,
   PD, >= ~4000 px wide; DROP pictorial/regional/fort-close-up/photo/street-car-map; dedupe same-sheet
   scans by EYEBALLING 1280 px thumbs, one row per sheet, keep the LOC/largest scan); (4) verify QID
   live with `--verify` (watch the Barnard-Castle trap - Pittsburgh is the in-table example);
   (5) SITES + SOURCES entry; (6) `--dry`, stage, `--check` (exit 0); (7) lead-doc section per city +
   re-run `--verify` (append the growing transcript); (8) `--golden` then the module tests + full
   suite. Box 4 ticks at >=25 cities total; then Status: done.

### Rules (unchanged)

NEVER write the canonical files (data/commons/files.jsonl etc. - that is 236c); NEVER touch 236a's
extras_us_cities.jsonl (read-only; the module's _shared_site enforces it); run live commands under
.venv/bin/python (system python3 has no numpy; the module top stays stdlib-only); batch size ~5
cities/session to fit the context limit; the golden sample is the contract (`--golden` only for an
intended change).