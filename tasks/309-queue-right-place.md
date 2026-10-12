Status: in-progress
# 309: The queue pairs a drawing with the right place, not a namesake
Carved from: 307 (box 1)
Touches: tools/fit_queue.py, tools/right_place.py, web/data/fit_queue.json, data/review/, web/data/review.json, tests/test_fit_queue.py, docs/site_flow.md, fit/review.py, fit/batch_eu.py, fit/site_catalog.py, tests/test_site_done.py, tests/test_fit_provenance.py, tests/test_review.py, PITFALLS.md

## Goal
307 box 1, carved out so it runs in parallel with 307's page work (agent a). The queue's first entry paired
Allcroft 1908 Fig. 217, "The Devil's Dyke Camp, near Brighton" (a Sussex hillfort), with devil-s-dyke-q3307343, the
Devil's Dyke in Cambridgeshire, 150 km away. The owner could not find it on the map.

## Acceptance criteria
- [x] (carved to 804 - the wiring in tools/fit_queue.py build(); 805 - the rebuild of the committed
      queue/review data) Every queue entry's candidate is checked to show the same place as its site, not just
      the same name: the caption/place words, county and region in the picture's metadata against the site's
      place, region and coordinates (Wikidata where it helps). A mismatch leaves the queue and goes to the review
      queue with the reason "same name, other place: <caption place> vs <site place>"; where the right site
      exists in the catalog, the candidate is moved to it instead.
- [x] (carved to 805) docs/site_flow.md: how many of the queue's entries were wrong, and the list. Devil's Dyke
      Camp near Brighton is not paired with the Cambridgeshire dyke.
- [x] (carved to 804) tests/test_fit_queue.py covers a namesake mismatch (no network).

## Notes
- Do not touch web/index.html, web/fitqueue.js (agent a, 307) or fit/ (the lead is building the matcher fit
  there). The subtasks' own Touches lines are authoritative for their files; 804 also carries
  data/review/README.md (the reason extra in the pass-through list) and 805 carries
  tests/test_right_place_drift.py.

## Hand-over

(2026-10-12, iteration 110, agent c - session 19. PARENT 309 DONE. Both subtasks
closed: 804 (done, session 11) and 805 (done, this session - its box 3 delivered
tests/test_right_place_drift.py, 17/17 pass first run, containment-based per the
new PITFALLS entry; box 4 re-verified: queue key set identical on main and
agent/c, the three named tests pass 3/3). All three carved boxes ticked: the
wiring (804), the rebuild + docs section (805, queue 114/309, 15 flagged pairs
over 9 sites reported in docs/site_flow.md, Devil's Dyke Camp/Brighton on the
Sussex hillfort, not the Cambridgeshire dyke), and the namesake test (804).
Lane state at close: 804/805 land on main with this lane's acceptance -
tools/right_place.py and the rebuilt queue/review data are on agent/c only
until then. Final suite: 98 passed / 1 skipped / 2 failed - both not-mine
(the lead's page-rework stat line, agent a's 307 files; ArcGIS ERR_ABORTED
flake 5/5). No open work remains in this lane.)
