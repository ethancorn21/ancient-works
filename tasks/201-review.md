Status: open
# 201: Review queue — items the human finishes by dragging
Depends on: none
Touches: fit/review.py, web/review.js, web/index.html, data/review/, web/data/review.json, tests/test_review.py

## Goal
GOAL.md points 1 and 5: every built site without a fitted drawing gets a review item in `data/review/` —
the site, its best candidate pictures (with their evidence field when 200 has produced one), and proposed
point pairs per picture. The human opens the item on the page, drags the pairs onto today's ground, and
saves with the existing fit tool in under a minute. Saving resolves the item; the page shows how many are
left.

## Acceptance criteria
- [ ] A review item is `data/review/<site>.<plan>.json`: the site id, one entry per candidate picture (plan
      id, title, evidence field when present, thumbnail or page-image url) and the proposed pairs per
      picture in platefit format (page px → lon/lat).
- [ ] The page gains a "Review" section in its own file `web/review.js` loaded by one added script tag in
      `web/index.html` (no other change to index.html): the count of open items and a list; opening an item
      brings up the existing fit tool with the picture and the proposed pairs already placed on the right
      ground (relief, or the aerial photograph for a site with no LiDAR — the fitkit convention).
- [ ] Saving corrected pairs uses the existing path (PUT `/api/db/platefits/…` → `plan_fit` overlay → red
      square) and marks the item resolved (out of the queue, with the saved doc id recorded). A human save
      is trusted as-is: the gate (001) constrains only automatic fits.
- [ ] The page's existing stats line shows the open review count, computed from `web/data/review.json`
      (a compact list `fit/review.py` exports from `data/review/`), not hardcoded.
- [ ] The fit tool's plan lookup is keyed by (id, site), not id alone: today two rows sharing an id (one
      picture depicting two sites: the Larned history for Avebury+Stonehenge, Mayburgh-1769 for
      Mayburgh+King Arthur's Round Table) collide in `P.byId` and the wrong row opens.
- [ ] Test (no network, port 0): a temp tree seeded with one review item; a headless load of the page
      (`tools/shot.mjs`) shows the item in the review list; a PUT of a saved pair against the temp doc store
      resolves the item, checked through the served data.

## Notes
- Vanilla JS in the page's existing style; no new dependencies; the page has no build step.
- `data/review/` does not exist yet; create it. The item file is the source of truth; `web/data/review.json`
  is the export the page reads (212 re-exports it when items change later).
- Fit-tool pixel conventions: pairs are page px of the full-size picture (the `crop` and `size` of the
  platefit doc); read the grid labels on a fitkit sheet, never its own pixels.
