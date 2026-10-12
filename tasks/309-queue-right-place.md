Status: split
# 309: The queue pairs a drawing with the right place, not a namesake
Carved from: 307 (box 1)
Touches: tools/fit_queue.py, tools/right_place.py, web/data/fit_queue.json, data/review/, web/data/review.json, tests/test_fit_queue.py, docs/site_flow.md

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

(2026-10-12, iteration 100, agent c - session 9 on the 309 lane. The driver handed me 309
(the split parent) again; 804 is in-progress in this lane. Done this session: 804 boxes 1+2
- the two-phase right-place wiring is IN tools/fit_queue.py and verified on real data
(flags == the CLI's 15 exactly; queue 116 -> 114 entries; exactly 5 new review-item files /
6 upserts each carrying the place_reason; a second build is byte-identical - zero churn;
part-1 tests pass unmodified; full suite at baseline 3 failed / 77 passed / 1 skipped). THE
CODE CHANGE IS UNCOMMITTED in the checkout at hand-over (the harness saved it): the next
session commits it first (message like "804: wire the right-place check into build() -
flagged candidates leave the queue, moved to the right site or to review with
place_reason; no-op degrade keeps 305 green") before or with the box-3/box-4 work. ALL
state, the verification evidence (including the exact 5 new item files 805 must reproduce)
and the exact next step (804 box 4: the synthetic namesake test + the real-tree re-
derivation with catalog/books, then box 3: the data/review/README.md place_reason note;
then 805 the rebuild) are in 804's hand-over - read it before anything else. When 804+805
are done the driver returns 309 and I tick its three carved boxes and set it done.)

Carve state: box 1 (the wiring) = 804, in-progress ~4/5 (boxes 1+2 in and verified; box 3
the README note and box 4 the namesake tests pending); box 2 (the site_flow report) = 805,
not started; box 3 (the namesake tests) = 804, pending.


