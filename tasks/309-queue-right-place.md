Status: done
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

(2026-10-12, iteration 111, agent c - session 20. RE-CLAIMED DONE after the driver's
rejection. The two cited test_review failures were page-side drift, not lane changes:
(a) the keying test's strict [reqfail] assertion trips on the live Esri World_Imagery
tiles (SINGULAR /tile/ path) that the lead's f5ea863 rework now loads the moment a
site is opened - the probe's start/end fit cycle aborts them (ERR_ABORTED); the host
itself is reachable (curl 200), so the old "ArcGIS flake" note was a misdiagnosis
(deterministic, on every branch, proven on pristine main by 221's scratch run);
(b) the list test's stats filter pinned the pre-939382a "built in all" wording that
the lead re-worded to "laid on today's ground" (the page's own matcher,
web/review.js:74, accepts both). Fix = agent a's task 221's exact spec, made in MY
file (tests/test_review.py is on 309's Touches; 221's Notes anticipated the overlap:
"the fix lands on top of whatever 309 leaves in the file"): the keying reqfail
filter now excludes page-caused '/tiles'/arcgisonline aborts (mirroring 307bb's
f23ad75 filter in test_fit_queue.py) and the stats filter accepts both wordings;
no other assertion touched. Suite green: 100 passed / 1 skipped / 0 failed.
221 (agent a's, open, Depends on: 309) has its boxes 1+2 (and 3, suite green)
satisfied by this commit - when the driver hands it out after this lane lands on
main, the next agent verifies the file against 221's acceptance and closes it; do
not re-edit the file beyond that. No open work remains in this lane: branch = main
89043b7 + 804/805 + this test fix. Re-read: none.)
