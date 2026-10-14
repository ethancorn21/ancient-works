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

(2026-10-14, iteration 180, agent a) The four owner cities are STAGED AND VERIFIED: boxes 1/2/3/5
ticked (tests green, lead doc complete, shared ids agreed). **Only box 4 remains: >=25 cities staged
in total (4 done, >=21 new cities to go).** Everything is committed (the 179 "uncommitted" list was
swept into b06513f before this session; this session's work - tests verified, PITFALLS entry, boxes -
is committed on top).

- **Verified this session (all under .venv/bin/python):** `pytest tests/test_src_us_birdseye.py -q`
  -> 5 passed, FIRST TRY (no test fix needed - the 179-guessed risk spots, the per-title year map and
  the 1897/1854 date assertions, were already right). Full suite -> **177 passed, 1 skipped, 0 failed
  in 527 s** (= 172 baseline + 5 new; the standing 1 skip). Also live-re-verified the loc.gov 403
  with BOTH the project UA and a browser UA (curl on the collection page) before writing the PITFALLS
  entry; Wayback snapshots render (the 2025-01-02 item list: Date, Contributor, Phillips numbers -
  no description block, so size/range stand on GOAL.md).
- **State of the files (all committed, all stable):** fit/src_us_birdseye.py (SHARED_SITES cross-checks
  236a's read-only extras_us_cities.jsonl every run and fails loud on drift; SITES={} still; CLI:
  --verify / [--dry] stage / --check / --golden), data/commons/files_us_birdseye.jsonl (11 rows,
  all "Public domain" in metadata, evidence caption_coords dist 0 on 236a's verified points),
  data/commons/classified_us_birdseye.jsonl (11 rows, p_birdseye 1.0 by:hand),
  tests/golden/src_us_birdseye_sample.json (matches staged rows - test asserts it),
  docs/lead_us_birdseye.md (complete for the four cities: fetch route incl. the 403+Wayback, the
  shared-ids table, the --verify transcript, STAGED/DROP/RESERVED per city, the 11-line --check
  transcript). data/catalog/extras_us_birdseye.jsonl does NOT exist yet - correct until a NEW city
  lands; _load() returns [] for it, stage() appends it idempotently on (site, title).
- **NEXT (exact): the new-city batches, ~5 cities per session until >=25 cities total (box 4).**
  Per city, in order: (1) BEFORE anything: check the city is not already in the catalog on main
  (data/catalog/sites.jsonl + extras.jsonl + extras_us_cities.jsonl) - never two sites for one QID.
  (2) Commons file-namespace full-text search: commons.py search with queries like "bird's-eye view of
  <city>", "<city> bird's eye view", "<city> birdseye" (SF and Nashville proved the quoted-intitle
  queries find NOTHING - plain phrase queries are the working form; the four-cities queries + the
  pool builder are in the iter-178 DECISIONS entry: commons.members() + commons.info() 50/call at 1/s,
  keep() + the 600-char caption gate; /tmp/aw236b_good.json holds only the four cities' pools and is
  likely gone - rebuild per batch). (3) Pick the ONE best view: near-vertical, street grid visible
  at fit scale, Public domain, >= ~4000 px wide; DROP pictorial/regional/building-close-up views and
  photographs (236a's HABS-photo precedent), and dedupe same-sheet scans (one row per sheet, keep the
  largest/LOC scan - eyeball thumbnails at https://upload.wikimedia.org/wikipedia/commons/thumb/...;
  /tmp/aw236b_thumbs may be gone). (4) Verify the QID LIVE: pipeline/catalog_wd (or a direct
  wbsearchentities) - watch the Barnard-Castle trap (a name search can hit a different place/number
  with coordinates; >50 km from the expected point = trap, the table point stands). (5) Add the SITES
  entry (id = slug + "-" + qid-lower per pipeline/sources.py's slug rule, region "United States",
  kind "town", aerial_ok true, note records the view's apparent angle) + the SOURCES row to
  fit/src_us_birdseye.py. (6) `.venv/bin/python fit/src_us_birdseye.py --verify` and append its
  transcript to the lead doc. (7) `.venv/bin/python fit/src_us_birdseye.py --dry` then stage (no --dry),
  then `--check` (expect exit 0; new site rows land in extras_us_birdseye.jsonl). (8) Lead doc:
  a section per city (STAGED/DROP/RESERVED, per-view date/artist/resolution, the QID-verify facts).
  (9) `.venv/bin/python -m pytest tests/test_src_us_birdseye.py -q` (if new rows break the golden:
  `--golden` then re-run - the golden pin is the contract) and the full suite before committing.
  **Candidate list (in order, take the first ~21-25 that survive the gates):** Boston, Philadelphia,
  Baltimore, Pittsburgh, Cincinnati, Louisville, St. Louis, Chicago, Detroit, Cleveland, Milwaukee,
  Kansas City, Omaha, St. Paul/Minneapolis, Indianapolis, Columbus, Memphis, New Orleans, Charleston
  (SC), Richmond, Norfolk, Portland (OR), Seattle, Denver, Colorado Springs, Santa Fe, Albuquerque,
  Salt Lake City, San Diego, Los Angeles, Houston, Dallas, San Antonio, Little Rock, Atlanta,
  Birmingham, Savannah, Buffalo, Providence, Hartford, Albany, Worcester, Rochester, Wilmington,
  Fredericksburg. A city whose best view fails the gates gets recorded in the lead doc as DROP with
  the reason and does not count toward the 25 (the four-cities lead section shows the format).
- **Rules (unchanged):** NEVER write the canonical files (data/commons/files.jsonl etc. - that is
  236c), NEVER touch 236a's extras_us_cities.jsonl (read-only; the module's _shared_site enforces it),
  run live commands under .venv/bin/python (system python3 has no numpy; the module top stays
  stdlib-only). Batch size ~5 cities/session to fit the context limit; when all boxes are ticked,
  set Status: done (box 4 only at >=25 cities total).