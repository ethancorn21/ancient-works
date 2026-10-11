Status: open
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

## Hand-over
Iteration 20 (2026-10-11). Step 1 (prep step 1, the environment) is DONE and committed: Google Chrome
155.0.8059.39 installed on this VM (PITFALLS has the rebuild recipe; `npx playwright install chrome`
fails here - only `sudo -n apt-get` is passwordless), and the full page boots headless (shot.mjs probe:
ready:true, 384 sites, 1166 plans, no pageerror; only the expected scans.json/amazon 404s) -> test case 2
can be built exactly as worded. Prep assumption audit: see the DECISIONS entry of today (wrong: 001 now
done; sites.json is a {"sites":[...]} wrapper; data/raw has real content on this VM; commons now 1490 rows
with 109 no-evidence null-title rows = 801's targets; index.html 1703 lines). Everything else in the prep
holds (verified: duplicate ids, composite-key uniqueness, 17 no-lidar sites == no relief.jpg, bibracte
candidate-less, alligator's two candidates + their evidence, 202's dict contract, 203a/203b's upsert/export
expectation). Suite baseline: 12 passed in 9.4s.

Next step (prep step 2): `fit/review.py` per prep section 3.1, stdlib-only, importable by 203a/203b/212:
- `item_path(root, site_id, lead=None)` -> `data/review/<site>.<lead>.json` or `<site>.json`.
- `upsert_item(root, site_id, entries, no_picture=None)`: merge candidates by `plan` (replace same-plan
  entry, keep others, new plans appended); `resolved` is write-once (never cleared, never overwritten);
  never writes web/data/review.json; the lead in the file name follows candidates[0].plan.
- `candidate_evidence(plan_id)`: book rows -> `data/books/index.jsonl` by `id`; commons rows ->
  `data/commons/files.jsonl` by `c_+sha1(title)[:16]` (full-file scan; None when the row or its `evidence`
  field is missing - 109 commons rows have no evidence, 801's targets).
- `resolved_doc(item, root)`: item["resolved"]["doc"] else any existing `data/db/platefits/<site>.<plan>.json`
  for one of the item's candidate plans (resolution is DERIVED from the doc, never a second store).
- `export(root)` -> (n_open, n_total): writes `web/data/review.json` = `{"at": iso, "items": [{site, name,
  lead, candidates (verbatim, incl. producer extras), no_picture_found}]}` - OPEN items only (resolved null
  and no doc), sorted by site name (name from web/data/sites.json's list; missing site -> raw id, logged);
  when it finds a resolving doc it writes `resolved: {doc, at: <doc's at>}` back into the item file.
- CLI: `python3 fit/review.py export [--root DIR]`.
Then the seeds (data/review/README.md states this exact contract for 203a/203b/212):
1. `data/review/alligator-effigy-mound-q4732645.ancientmonuments00squi_n0214_2.json`: candidates = [book row
   (lead: url "books/ancientmonuments00squi/n0214.jpg", map_box [0.03,0.09,0.45,0.49], size [2876,4068]),
   commons row (url "media/commons/alligator-effigy-mound-q4732645/618a6be74dfaff32.jpg", map_box null,
   size [1280,1045])], each with its evidence verbatim; `pairs` per candidate = 202's dict is NOT merged yet,
   so use the deterministic anchor from prep section 1-202: site centre + the row's map_box corners in the
   row's size frame (book: 3-5 pairs, e.g. 3 map_box corners + centre; commons map_box null: the full-frame
   corners + centre); set `coarse: true` and a `note` saying the pairs are the 202-style starting point.
2. `data/review/bibracte-q650053.json`: `candidates: []`, `no_picture_found: {"searched": <what a targeted
   search covers, mirror 212's wording>, "at": <iso>}` (it is one of the 17 no-lidar sites -> aerial ground).
Run the export once; commit `web/data/review.json` (2 open items) with the items.

After that, one commit each: (3) index.html box-5 keying fix alone - in loadPlans build
`P.byId[planKey(r)]` and the fit-list `data-plan` attribute with the same `planKey(r)`
(`r.sites.length ? r.id + '.' + r.sites[0] : r.id`; ids contain no dots; (id, sites[0]) proven unique,
test_data asserts it) so the binding `openPlan(P.byId[b.dataset.plan])` needs no change; (4) `web/review.js`
+ the one script tag (prep section 3.2: state RV {items, seen-from-localStorage}; wrap renderList/setTabHome
at load, idempotent, tolerate pre-boot; Review tab session-only (no hash route - index.html frozen); opener
order select -> setGround(site.lidar===false?'imagery':'relief', site) -> startFit -> openPlan with
RV.pending pairs pushed-then-addPairMarker inside the openPlan wrapper, refit() when P.img loads (skip
silently on 404 - the test tree has no data/raw); saveFit wrapper: after the original returns, check
S.db.doc('platefits/'+P.site.id+'.'+P.plan.id).get() is 200 -> record RV.seen[site] in localStorage, drop
from RV.items, refresh count/badge; the stats line `#body .fit` gains a computed open count from the served
review.json (fetch in review.js; keep the existing sentence byte-for-byte, R8)); (5) tests/test_review.py
per prep section 4 (case 2 now viable; worker churn: PUT a book-src doc only, assert server still answers,
20 hand-fit docs untouched - note tests/golden pins them by sha256 per 203a's prep; keep the whole suite
stdlib-runnable and port-0-only).

Re-read: web/index.html `select(id)` - it returns EARLY when `P.active` (`if (!s || P.active) return;`):
the review opener must `endFit()` first if a fit is active, otherwise select() silently does nothing.
Also `startFit` renders the fit pane's `#body` (the plan list) - after `openPlan` the pane shows the fit
sheet, so no extra rendering is needed for pre-placement; and `endFit(keepSite=true)` re-renders the site
panel, which the saveFit wrapper must not fight with (it only updates RV + count + the home stats line).
