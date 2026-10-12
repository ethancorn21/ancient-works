Status: split
# 309: The queue pairs a drawing with the right place, not a namesake
Carved from: 307 (box 1)
Touches: tools/fit_queue.py, tools/right_place.py, web/data/fit_queue.json, data/review/, web/data/review.json, tests/test_fit_queue.py, docs/site_flow.md, fit/review.py, fit/batch_eu.py, fit/site_catalog.py, tests/test_site_done.py, tests/test_fit_provenance.py, tests/test_review.py, PITFALLS.md

## Goal
307 box 1, carved out so it runs in parallel with 307's page work (agent a). The queue's first entry paired
Allcroft 1908 Fig. 217, "The Devil's Dyke Camp, near Brighton" (a Sussex hillfort), with devil-s-dyke-q3307343, the
Devil's Dyke in Cambridgeshire, 150 km away. The owner could not find it on the map.

## Acceptance criteria
- [ ] (carved to 804 - the wiring in tools/fit_queue.py build(); 805 - the rebuild of the committed
      queue/review data) Every queue entry's candidate is checked to show the same place as its site, not just
      the same name: the caption/place words, county and region in the picture's metadata against the site's
      place, region and coordinates (Wikidata where it helps). A mismatch leaves the queue and goes to the review
      queue with the reason "same name, other place: <caption place> vs <site place>"; where the right site
      exists in the catalog, the candidate is moved to it instead.
- [ ] (carved to 805) docs/site_flow.md: how many of the queue's entries were wrong, and the list. Devil's Dyke
      Camp near Brighton is not paired with the Cambridgeshire dyke.
- [ ] (carved to 804) tests/test_fit_queue.py covers a namesake mismatch (no network).

## Notes
- Do not touch web/index.html, web/fitqueue.js (agent a, 307) or fit/ (the lead is building the matcher fit
  there). The subtasks' own Touches lines are authoritative for their files; 804 also carries
  data/review/README.md (the reason extra in the pass-through list) and 805 carries
  tests/test_right_place_drift.py.

## Hand-over

(2026-10-12, iteration 108, agent c - session 17. 805 BOX 2 DONE (UNCOMMITTED - the harness saved it):
docs/site_flow.md gained the "The right-place check" section (appended at the end, after "The
matcher fit"; self-contained - agent a's 306 also touches this file, nothing above it was edited).
Every number in it was re-verified this session by running code (below). Tick 805's box 2, then
box 3 is the next step.)

WHAT THIS SESSION DID (805 box 2, all verified by running code on the current tree):
- Appended the section to docs/site_flow.md (~75 lines): what the check reads (catalog + book
  index + book lists, stdlib, no network), how it decides (H1 explicit county/state word; H2
  towns->classic counties through the catalog, UK book rows only; fail open), the right-site
  rule (matcher's own verbatim core, place gate, min_score 0.5), the 15-flag table (site,
  candidate, caption, verbatim reason - all `same name, other place: ...`), the disposition
  (10 flags found unbuilt right sites -> 6 candidate writes into 5 new review items, 4 dedup
  skips; 5 flags found no catalog site -> stayed in the source item already holding the plan,
  upsert skipped, batch record as written; 0 moves into built-site entries), queue size
  117/325 -> 116/324 -> 114/309, and the --live note (a human-only path from the dropped
  spec; the shipped check is stored-fields only).
- Verified facts behind it: `tools/right_place.py --root .` -> "checked 324: 15 flagged"
  (identical flags to iterations 95/103/109); queue versions 9c805d7 = 117 entries/325
  candidates (shotwick present, its only candidate n0575_1), 939382a = 116/324 (shotwick gone),
  current committed file = 114/309, zero of the 15 flagged (site,plan) pairs in it, n0686_1 in
  no entry; the 5 new item files carry place_reason, the 5 source-site items hold the parked
  plans with NO place_reason (upsert skipped); review.json = 336 open of 346 files, the 5 new
  sites in it; the 17 verbatim-core top-level names in tools/right_place.py are byte-identical
  to pipeline/books_match.py today (zero drift) - that is exactly what box 3's test will pin.
- WHY shotwick left the queue (the doc states it): its site dir web/data/sites/<id>/ is gone
  (no longer "built" per tools/fit_queue.py _built_sites; sites.json drawings: 0) after the
  lead's Oct 12 review export (939382a, sites.json 1925 lines changed) rebuilt site state;
  its fit doc (data/db/platefits/shotwick-castle-...c_e6e5490609414bb9.json) and its review
  item (data/review/...n0575_1.json, tracked since 303's 011e48b) remain; the queue holds
  built sites only, so it is neither in the queue nor checked (the 324 count excludes it).

STATE: docs/site_flow.md is MODIFIED UNCOMMITTED in the worktree (the only changed file).
No test run this session (the edit is docs-only; suite is at the not-mine baseline
81 passed / 1 skipped / 2 failed from session 16 - the 2 = test_review::test_page_shows_the_
review_list (lead's 939382a page rework removed the "built in all" phrase; web/index.html +
tests/ are agent a's 307 - NOT MINE) and test_review::test_plan_lookup_is_keyed_by_id_and_site
(ArcGIS tile ERR_ABORTED flake, 3/3 now, 2/2 in session 15 - NOT MINE). The 1 skip =
test_batch_eu::test_union_full_coverage_live (skip-gated on docs/batch_eu.md staleness).
PITFALLS: run the suite with .venv/bin/python -m pytest, never bare python3 (no numpy in the
system interpreter -> 12 collection ImportErrors via pipeline/fit_gate.py); stat
.agent/reports/last-test-output.txt before trusting it (a day stale in session 16).

NEXT STEP (exact, one session each):
1. 805 box 2 close-out: tick box 2 in tasks/805-fit-queue-rebuild.md (acceptance text: "docs/
   site_flow.md gains the section: ..."); append this session's facts to DECISIONS.md (entry
   "2026-10-12 309 DECISION: iteration 108 (session 17) - 805 box 2: the right-place section
   written into docs/site_flow.md (appended, verified facts: 15 flags over 9 sites, 10->6
   writes/4 dedup/5 parked, 117/325->116/324->114/309, shotwick left via unbuilt status, 336
   of 346 open, verbatim core in sync today); --live/fit_place.json never shipped (dropped
   309-place-check.md spec)"); add the PITFALLS entry (under the "### tools/right_place.py
   (the right-place check...)" section): "The module has NO --live flag and no
   data/fit_place.json - those belong to the DROPPED spec tasks/309-place-check.md (kept as
   reference); the shipped module is a single commit fc67bb9, catalog-driven, stdlib only;
   do not hunt for them or add them without a new task"; then run the full suite
   (.venv/bin/python -m pytest; expect 81/1/2, docs-only edit should change nothing -
   test_serve::test_platefits_docs_match_sites checks data/db/platefits docs, not site_flow)
   and commit (docs/site_flow.md + the task files + DECISIONS + PITFALLS together, or the
   docs commit first and the notes second).
2. 805 box 3: write tests/test_right_place_drift.py (hermetic, stdlib, no network, no ports,
   no writes outside the tree): for each of the 17 top-level names between the two VERBATIM
   markers in tools/right_place.py (US_STATES, ABBR, UK_ABBR, UK_COUNTIES, GENERIC, norm,
   SUFFIX is NOT one of the 17 - it is a module-level regex inside the core but the 805 box
   list is the 17 names in the box text: US_STATES, ABBR, UK_ABBR, UK_COUNTIES, GENERIC,
   norm, name_keys, tokens, place_of, site_place, site_toks, name_lookup_keys, row_inputs,
   score_candidate, BOOK_SCOPE, PLACE_WORDS, phrases), extract the block's text from BOTH
   tools/right_place.py and pipeline/books_match.py and assert byte-identical; the test
   fails when either file drifts. Extraction rule that works (verified this session): in
   right_place.py take the region between the two "# ===== ... VERBATIM ..." marker lines,
   then match each name at the start of a line (US_STATES = ... through the end of the
   statement, def name: def line + its 4-space-indented body) and assert the exact block
   string occurs verbatim in pipeline/books_match.py. I verified all 17 match byte-identical
   today with a throwaway script, so the test must pass on first run. DO NOT edit the
   verbatim core: a real drift is fixed in pipeline/books_match.py (source of truth) - if
   that file is agent a's or the lead's in flight, log it in DECISIONS.md instead. After
   box 3: run the suite, tick 805's boxes 2+3, and 805 is done (box 4, the queue-shape
   contract, is already satisfied by box 1's rebuild + 804's tests - re-verify and tick it
   when you close 805, then the driver returns parent 309 and you tick its three carved
   boxes and set it done, per the iteration-109 plan).

Carried facts (unchanged since session 16): 804 is done (all five boxes, on this branch and
merged); 805 box 1 done (rebuild 117->114, 5 new items, review.json re-exported, the
contract fix in fit/review.py export + fit/batch_eu.py union_check + fit/site_catalog.py,
suite at 81/1/2); the 15-flag list and dispositions: this session's DECISIONS entry and the
new site_flow section; the 2 not-mine failures above.
%%DELETE%%
