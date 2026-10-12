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

(2026-10-12, iteration 107, agent c - session 16 on the 309 lane. 805 BOX 1 CLOSED
(ticked): the suite sits at the recorded not-mine baseline 81 passed / 1 skipped /
2 failed. This session's fix: renamed fit/catalog.py -> fit/site_catalog.py - the
bare name shadowed pipeline/catalog.py in the shared-sys.path tests and broke
test_src_van_deventer (AttributeError: module 'catalog' has no attribute 'slug');
session 15's 3-file verification never ran that test. Committed. NEXT STEP (exact):
805 box 2 - the docs/site_flow.md section: how many of the queue's 117 entries were
wrong (15 pairs over 9 sites, with the list: site, caption, reason), which candidates
moved to which site and which went to review, the queue's size before and after
(117 -> 114), and how the check decides (stored fields only: the caption's explicit
county/state word, its towns resolved to classic counties through the catalog, the
site's county/state from its catalog record; an unknown place never flags - fail
open; the --live Wikidata path is for a human re-run, never in the build). The
15-flag list and the per-flag dispositions are in the DECISIONS entries of
iterations 102/103 (grep '309 DECISION: iteration 10' DECISIONS.md) and the 805
Goal. Then box 3: tests/test_right_place_drift.py (hermetic, stdlib, no network:
for each top-level name between tools/right_place.py's two VERBATIM markers,
extract the block's text from both that file and pipeline/books_match.py and assert
byte-identical). Do not edit the verbatim core: a real drift is fixed in
pipeline/books_match.py (the source of truth) - and if that file is agent a's or
the lead's in flight, log it in DECISIONS.md rather than editing it. The 2
test_review failures stay NOT MINE (below) - agent a's 307 reworks web/index.html
+ tests/.)

State of the tree (all committed; worktree clean):
- 805 box 1 complete. The rebuilt web/data/fit_queue.json (117 -> 114 entries) and
  the 5 new data/review/ items (unbuilt catalog right sites: a-saucer-barrow, castle-
  dyke, devil-s-dyke-hillfort, down-end-castle, oval-barrow; each with place_reason)
  are in the driver's 1914931 merge commit; web/data/review.json (336 open of 346,
  the 5 catalog names) is the session-15 in-process fit/review.py export; the
  contract fix (fit/review.py export name chain sites.json -> catalog -> id; fit/
  batch_eu.py union_check's catalog-aware unbuilt_items bucket; the catalog-aware
  temp-tree builders in test_site_done/test_fit_provenance; the test_review
  _site_names helper) is in 268d1f5; this session's rename commit finishes it.
  No test assertion was ever edited.
- The owner's case verified on the current data: n0686_1 (Devil's Dyke Camp near
  Brighton) is paired with NO queue entry - devil-s-dyke-q3307343 (Cambridgeshire)
  is narrowed to n0662_1, its only remaining candidate - and n0686_1 lives in the
  review item devil-s-dyke-hillfort-q17674160.earthworkenglan01allcgoog_n0686_1.json
  (the Sussex hillfort, unbuilt). That is 804's rule applied: right site exists in
  the catalog but is unbuilt -> review item, not queue.
- Suite: 81 passed / 1 skipped / 2 failed (145 s). The skip = test_batch_eu::
  test_union_full_coverage_live (skip-gated on docs/batch_eu.md's "Sites run"
  matching the live EU partition - expected, not a failure).

The 2 remaining failures are NOT MINE (do not fix; both in tests/test_review.py,
which agent a's 307 - web/index.html + tests/ - is actively reworking):
(a) test_page_shows_the_review_list: asserts the home stats line contains "built in
    all"; the lead's 939382a PAGE REWORK replaced that line (git show 939382a --
    web/index.html). The page otherwise boots cleanly (boot, no pageerror, the
    tabs and the list all pass; only the phrase is gone).
(b) test_plan_lookup_is_keyed_by_id_and_site: external ArcGIS World_Imagery tile
    requests abort in flight while the probe keeps the page open ([reqfail] ... net::
    ERR_ABORTED); now 3/3 failing (2/2 in session 15). Machine/network flake - my
    data files add no map tiles, and the boot/plan-lookup assertions pass.

Pitfalls added this session (PITFALLS.md is now on the 309/805 Touches lines):
(i) run the suite with `.venv/bin/python -m pytest`, never bare python3 (system
interpreter: no numpy - 12 collection ImportErrors via pipeline/fit_gate.py); (ii)
.agent/reports/last-test-output.txt can be a day stale (the one I read at session
start was mtime 2026-10-11 17:14 and listed 3 shotwick failures that no longer
exist: shotwick is now a built site - 385 in sites.json - and the untracked item it
named has no git history in any ref). Stat the report and cross-check PROGRESS
note dates before chasing anything in it.

Carried facts: the 15-flag list, the 117 -> 114 rebuild, the 5-item / 340 -> 336
open history: DECISIONS iterations 100-103 (grep '309 DECISION'). Box 1's
"three pre-existing main-side failures stay as they is" wording is stale (the lead
fixed those three main-side); the current not-mine set is the two test_review
failures above - same spirit: no assertion edits outside my Touches, re-baseline
if a merge moves them.
%%DELETE%%
