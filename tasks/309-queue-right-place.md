Status: open
# 309: The queue pairs a drawing with the right place, not a namesake
Depends on: 305
Carved from: 307 (box 1)
Touches: tools/fit_queue.py, web/data/fit_queue.json, data/review/, web/data/review.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
307 box 1, carved out so it runs in parallel with 307's page work (agent a). The queue's first entry paired
Allcroft 1908 Fig. 217, "The Devil's Dyke Camp, near Brighton" (a Sussex hillfort), with devil-s-dyke-q3307343, the
Devil's Dyke in Cambridgeshire, 150 km away. The owner could not find it on the map.

## Acceptance criteria
- [ ] Every queue entry's candidate is checked to show the same place as its site, not just the same name: the
      caption/place words, county and region in the picture's metadata against the site's place, region and
      coordinates (Wikidata where it helps). A mismatch leaves the queue and goes to the review queue with the reason
      "same name, other place: <caption place> vs <site place>"; where the right site exists in the catalog, the
      candidate is moved to it instead.
- [ ] docs/site_flow.md: how many of the queue's entries were wrong, and the list. Devil's Dyke Camp near Brighton is
      not paired with the Cambridgeshire dyke.
- [ ] tests/test_fit_queue.py covers a namesake mismatch (no network).

## Notes
- Do not touch web/index.html, web/fitqueue.js (agent a, 307) or fit/ (the lead is building the matcher fit there).
