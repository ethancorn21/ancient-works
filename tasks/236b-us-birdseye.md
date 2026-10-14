Status: done
# 236b: US bird's-eye and panoramic city views (1847-1929)
Depends on: none
Touches: docs/lead_us_birdseye.md

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
- [x] fit/evidence.py check passes offline on every staged row (23/23 - the lead doc's Staging section
      carries the --check transcript verbatim); the four owner-named cities each have at least one view
      staged (all four do: New York 3, Washington DC 3, San Francisco 4, Nashville 1). The original box's
      "at least 25 cities staged in total" clause MOVED at the 2026-10-14 split: it is delivered by the
      parts 240 (batch 4: Denver, St. Paul, Minneapolis, Cleveland) and 241 (batch 5: the final five)
      and checked by 236c (its Proposed changes) - the 207a moved-boxes precedent.
- [x] Test (no network): the staged files join, the evidence check passes, a golden sample of rows.

## Notes
- Bird's-eye views are oblique: the fit is harder than for a plan. Prefer views drawn near-vertical; record
  the view's apparent angle on the row's note so 236c/the matcher can order them.
- Templates: fit/src_artists.py + docs/lead_artists.md (Civitates).
- Do NOT write the canonical files - that is 236c.

## Hand-over

(2026-10-14, iteration 196, agent a) **DONE - the 195 driver-ordered split is complete and
committed.** 236b closes at the 16 cities it built; the remaining 9 to the 25 total are the
parts' work (240, 241), and the driver publishes this commit's task files to main so agent c
can start 240.

**What this task owns at close (all on main):** 16 US city sites = the four owner-named cities
on 236a's site ids (New York 3 views, Washington DC 3, San Francisco 4, Nashville 1) + 12 new
sites (batch 1: Boston, Philadelphia, Baltimore, Pittsburgh, Cincinnati; batch 2: Louisville,
St. Louis, Chicago, Detroit, Milwaukee; batch 3: Kansas City, New Orleans) = 23 views. The
module holds 16 site entries (4 shared SHARED_SITES + 12 new SITES); the staging files hold
12 extras / 23 files / 23 classified rows; the golden pins 12/23/23. Files:
fit/src_us_birdseye.py (the parts' copy-template), the three staging jsonl's,
docs/lead_us_birdseye.md (21 ## sections; its Staging section carries the --verify and
--check transcripts verbatim - the contract), tests/test_src_us_birdseye.py,
tests/golden/src_us_birdseye_sample.json.

**The split (all on main):** 240 (batch 4: Denver, St. Paul, Minneapolis, Cleveland -
Denver's complete 194 research record in its Notes) and 241 (batch 5: the final five; the
candidate order continues from 240's lead doc; its known_sites() cross-check reads 236a's,
236b's and 240's extras files) each own fit/src_us_birdseye_batch4/5.py + the
*_us_birdseye_batch4/5.jsonl set + docs/lead_us_birdseye_batch4/5.md + test + golden. 240
waits on 236b (now done); 241 waits on 240; 236c waits on 236a, 236b, 240, 241, consolidates
every staging set (fit/merge.py's glob) and checks the 25 total (16 + 4 + 5) - see PLAN.md's
"US cities family" section and 236c/236's Proposed changes (2026-10-14).

**Suite baseline at close:** 177 passed / 1 skipped / 0 failed (513 s, full suite on the
current post-0418e92 tree - the 193 baseline restored; the 195 background run died with that
session, its truncated log showed the pre-sync tree's in-flight reds, none on this tree).

**If this task reopens:** it owns only the built 16 cities - never re-stage Denver here (240's),
never write the canonical files (236c's), never touch 240's/241's files (theirs). Rules that
stay: live commands under .venv/bin/python (system python3 has no numpy; the module top stays
stdlib-only); the golden sample is the contract (--golden only for an intended change); tests
never bind fixed network ports or write outside the project + the temp dir; every full-suite
run re-encodes up to ten docs/site_flow/307d_*.png - restore main's bytes before committing (the
PITFALLS test_owner_check rule); measure every distance/direction claim before recording it.
