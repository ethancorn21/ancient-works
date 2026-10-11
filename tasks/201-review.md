Status: done
# 201: Review queue — items the human finishes by dragging
Depends on: none
Touches: fit/review.py, web/review.js, web/index.html, data/review/, web/data/review.json, tests/test_review.py

## Goal
GOAL.md points 1 and 2: the review queue for the fits the gate (001) refuses, the pictures the model
could not fit (fewer than four matched-feature pairs), and the sites with no picture found at all —
the human's drag is the authority there. Since the GOAL change of 2026-10-10 the queue is explicitly
that overflow, not a plan for every site; point 1 still holds, so every built site without a fitted
drawing ends with an item in `data/review/` — the site, its best candidate pictures (with their
evidence field when 200 has produced one), and the pairs to drag (the model's where it made any, else
the 202 starting point). The human opens the item on the page, drags the pairs onto today's ground, and
saves with the existing fit tool in under a minute. Saving resolves the item; the page shows how many
are left.

## Acceptance criteria
- [x] A review item is `data/review/<site>.<plan>.json`: the site id, one entry per candidate picture (plan
      id, title, evidence field when present, thumbnail or page-image url) and the proposed pairs per
      picture in platefit format (page px → lon/lat).
- [x] The page gains a "Review" section in its own file `web/review.js` loaded by one added script tag in
      `web/index.html` (no other change to index.html): the count of open items and a list; opening an item
      brings up the existing fit tool with the picture and the proposed pairs already placed on the right
      ground (relief, or the aerial photograph for a site with no LiDAR — the fitkit convention).
- [x] Saving corrected pairs uses the existing path (PUT `/api/db/platefits/…` → `plan_fit` overlay → red
      square) and marks the item resolved (out of the queue, with the saved doc id recorded). A human save
      is trusted as-is: the gate (001) constrains only automatic fits.
- [x] The page's existing stats line shows the open review count, computed from `web/data/review.json`
      (a compact list `fit/review.py` exports from `data/review/`), not hardcoded.
- [x] The fit tool's plan lookup is keyed by (id, site), not id alone: today two rows sharing an id (one
      picture depicting two sites: the Larned history for Avebury+Stonehenge, Mayburgh-1769 for
      Mayburgh+King Arthur's Round Table) collide in `P.byId` and the wrong row opens.
- [x] Test (no network, port 0): a temp tree seeded with one review item; a headless load of the page
      (`tools/shot.mjs`) shows the item in the review list; a PUT of a saved pair against the temp doc store
      resolves the item, checked through the served data.

## Notes
- Vanilla JS in the page's existing style; no new dependencies; the page has no build step.
- `data/review/` does not exist yet; create it. The item file is the source of truth; `web/data/review.json`
  is the export the page reads (212 re-exports it when items change later).
- Fit-tool pixel conventions: pairs are page px of the full-size picture (the `crop` and `size` of the
  platefit doc); read the grid labels on a fitkit sheet, never its own pixels.

## Hand-over
Iteration 25 (2026-10-11) - TASK COMPLETE, Status: done. All six boxes ticked and
verified (the evidence is the test suite: `.venv/bin/python -m pytest -q` -> 18 passed,
13 pre-existing + 5 in tests/test_review.py; no network, ephemeral port).

What exists now (all committed on this branch):
- `data/review/`: the README (the item contract) + the two seed items (alligator: two
  candidates, book lead, 5 pairs each, coarse anchor; bibracte: no picture, searched
  record). `fit/review.py` (stdlib-only): item_path / upsert_item / candidate_evidence /
  resolved_doc / export + the CLI. `web/data/review.json`: the committed export (2 open).
- `web/index.html`: the one script tag (after the inline script, before </body>) + the
  (id, sites[0]) keying in loadPlans via planKey(r) (committed separately, 0b65deb).
- `web/review.js`: the Review tab (session-only), the list, open-item with pre-placed
  pairs, save-resolves (localStorage), the stats-line clause, the injected style.
- `tests/test_review.py`: 5 cases (export CLI + idempotency; headless list/stats/404
  count; save-resolves via a PUT in the exact saveFit shape; (id, site) keying through
  the live page; the one-line index.html footprint).

What 203a/203b/212 import (their prep's assumption, now real code): from `fit/review.py`
- `upsert_item(root, site_id, entries, no_picture=None)` (merges by plan, never clears
  `resolved`, writes the item file only), `candidate_evidence(plan_id)` (the 200
  evidence field verbatim), `resolved_doc(item, root)`; the contract lives in
  `data/review/README.md`. Only `fit/review.py export` writes `web/data/review.json`;
  the batch never writes it, and 212 re-exports at project end.

This session's fix (both were test bugs, not product bugs; see the DECISIONS entry):
PROBE_LIST now re-fetches only data/review.json (a 200), so the n404 == 2 assertion sees
only the page's own two boot 404s; PROBE_KEYING's success return now carries
`boot: true` (the test asserts it).

Re-read (fresh eyes): none outstanding. The iteration-24 list is consumed: rvPatchStats
is guarded by the test's stats assertion, rvStartFitAt's await-loadDeps ordering
verified, conftest's tree shape verified by the response-level probe, index.html's
`S.tab = lsGet('aw.tab', 'sites')` line intact.

If this task is ever reopened: the driver re-runs the suite with .venv; the headless
cases skip (not fail) when Chrome is missing (`_headless_or_skip`); the two PITFALLS
entries added this session (shot.mjs's 404-line attribution; system-python collection
dies on task 801's PIL import) cover the only non-obvious traps left in this code.
