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

(2026-10-12, iteration 109, agent c - session 18. Merged main (the lead's 89043b7 RoMa work) into agent/c;
the only conflict, web/data/review.json, resolved by RE-RUNNING `fit/review.py export` on the merged tree
(open-items-only export -> 333 open of 346 = main's 328 + my 5 new items; the lead's 3 RoMa resolutions drop
out; no item file changed). 805 BOX 2 TICKED (verified against the post-merge tree, see below). Next session:
805 box 3, tests/test_right_place_drift.py.)

WHAT THIS SESSION DID (session 18):
- Merge (0fe0254): main's 89043b7 (RoMa fraction>=0.4 rule, 11 eye-checked RoMa fits, full review export) +
  939382a + 8a8b6f6 (307ba re-claim). Conflict analysis: review.json is a generated, open-items-only file;
  the two sides' 336-vs-328 gap = 3 items resolved on main (carisbrooke/dudley/newark) + my 5 items absent
  from main. Never hand-merge a generated JSON - regenerate it (the export changed no item file; all
  write-once resolutions were already on the main side). docs/site_flow.md auto-merged (both sides kept).
- 805 box 2 verified on the POST-MERGE tree (merge touched none of its inputs): `tools/right_place.py
  --root .` -> "checked 324 queue pairing(s): 15 flagged" - the same 9 sites as the section's table
  (alauna, bokerley-dyke, castle-neroche, clun-castle, coria, devil-s-dyke x2, eaton-socon x3, vindomora,
  windmill-hill x3); queue file still 114/309; shotwick's item still listed in the review file (333 open);
  17/17 verbatim-core names still byte-identical to pipeline/books_match.py (zero drift - box 3 must pass
  first run). One accuracy fix to the section: the "336 open of 346" sentence now notes the live count
  moves (the lead's same-day RoMa export resolved Carisbrooke, Dudley, Newark).
- PITFALLS: new entry under the right_place section - the shipped module has NO --live flag and no
  data/fit_place.json (dropped 309-place-check.md spec; single commit fc67bb9; stdlib only).
- Suite after the merge: 80 passed / 1 skipped / 2 failed / 1 error (133 s). Both failures are the standing
  NOT-MINE pair: test_review::test_page_shows_the_review_list (the lead's page rework removed the "built in
  all" stats line; web/index.html + tests/ = agent a's 307) and test_review::test_plan_lookup_is_keyed_by_id
  _and_site (ArcGIS World_Imagery ERR_ABORTED flake, 4/4). The 1 error = TEARDOWN flake in test_fit_queue::
  test_save_runs_the_one_site_line (shutil.Error in temp-tree cleanup; body passed; file passes 6/6 on
  re-run) - that is why 80, not 81. Skip = test_batch_eu::test_union_full_coverage_live (skip-gate).
- Lane state: 804 (done here) is NOT yet on main (tools/right_place.py absent from main; lands with this
  lane's acceptance). tools/right_place.py is read via the working tree on agent/c.

805 STATE: box 1 ticked (session 16: rebuild 114/309, 5 new items, contract fix in fit/review.py export +
fit/batch_eu.py union_check + fit/site_catalog.py, all on this branch); box 2 ticked (this session);
box 3 (tests/test_right_place_drift.py) NOT STARTED; box 4 (queue-shape contract) to be re-verified at
close (the rebuild + 804's tests already satisfy it; the three named pre-existing failures are fixed
main-side per session 16 - "stay as they are" = don't edit their assertions).

NEXT STEP (session 19, one session): 805 box 3 - write tests/test_right_place_drift.py. Hermetic, stdlib,
no network, no fixed ports, no writes outside the tree. For each of the 17 top-level names in the region
between tools/right_place.py's two marker lines ("# ===== the following blocks are copied VERBATIM..." at
line 33; "# ===== end of the verbatim core..." at line 223): US_STATES, ABBR, UK_ABBR, UK_COUNTIES,
GENERIC, norm, name_keys, tokens, place_of, site_place, site_toks, name_lookup_keys, row_inputs,
score_candidate, BOOK_SCOPE, PLACE_WORDS, phrases - extract the block (a top-level `NAME = ...` statement
or `def NAME(...):` + its indented body, until the next top-level line; NOTE SUFFIX is a 18th module-level
regex between name_keys and tokens - it is NOT in the 17-name list, skip it) and assert the exact block
text occurs in pipeline/books_match.py. Verified 17/17 byte-identical today with a throwaway (extraction
rule in the session-18 DECISIONS entry) - the test must pass on first run. If it FAILS, the drift is in
pipeline/books_match.py (source of truth; the lead's/agent a's file) - log it in DECISIONS.md, do NOT edit
it. Name the test file tests/test_right_place_drift.py (805's Touches carries it; 309's Touches line does
NOT name it - that is fine, subtask Touches is authoritative). Then: full suite (expect the not-mine
baseline), tick 805 boxes 3 + 4, set 805 Status: done, and the driver returns parent 309: tick its three
carved boxes (each already delivered by 804/805), set 309 Status: done.

Carried facts: the 15-flag table and dispositions live in docs/site_flow.md "The right-place check"
(section 564+, appended; agent a's 306 also touches that file - keep any future edit to it appended).
Suite mechanics: .venv/bin/python -m pytest only (system python3 has no numpy); stat
.agent/reports/last-test-output.txt before trusting it (stale-report trap). The lead's RoMa work now
sits in fit/matchfit.py + fit/matchfit_queue.py (NOT mine; fit/ is the lead's lane except my
site_catalog.py/review.py/batch_eu.py contract pieces from 805 box 1).
