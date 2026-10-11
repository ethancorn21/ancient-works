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
Iteration 21 (2026-10-11). Steps 1 (environment) and 2 (fit/review.py + seeds + first export) are DONE and
committed (ad8dbc1). The review-queue contract now exists in the repo:
- `fit/review.py` (stdlib-only, importable under system python3): `item_path`, `upsert_item` (merge by plan,
  in-place replace, append new; lead = candidates[0].plan stable; `resolved` write-once; `no_picture`:
  dict=set, None+entries=clear, None+none=keep), `candidate_evidence` (books by id; commons by
  c_+sha1(title)[:16] full scan; None when missing), `resolved_doc` (derived from platefits docs),
  `export(root)` -> (n_open, n_total) writing web/data/review.json + recording `resolved`, CLI `export [--root]`.
- `data/review/README.md` is the one-page contract 203a/203b/212 read before they write items.
- Seeds: `alligator-effigy-mound-q4732645.ancientmonuments00squi_n0214_2.json` (2 candidates, book lead, each
  with verbatim evidence + 5 pairs = 202-style coarse anchor, coarse:true, note) and `bibracte-q650053.json`
  (no picture found, searched mirrors 212's wording; one of the 17 no-lidar sites -> aerial ground later).
- `web/data/review.json` committed: 2 open items. Re-running the export is idempotent modulo `at`.
Remaining steps, in order, one commit each (prep §6):
3. **Box-5 keying fix, web/index.html alone** (commit it alone): in `loadPlans` at line 819 build
   `P.byId` keyed by a tiny `planKey(r)` = `r.sites.length ? r.id + '.' + r.sites[0] : r.id`, and write the
   SAME `planKey(r)` into the fit-list markup at line 853 (`data-plan="${esc(planKey(r))}"`). The binding at
   858 (`openPlan(P.byId[b.dataset.plan])`) then needs no change - the button carries the full composite key.
   Nothing else in index.html. Re-read lines 815-860 first (file is 1703 lines on this branch; the two
   duplicate ids and (id, sites[0]) uniqueness were verified in iteration 20).
4. **web/review.js + the one script tag** (one commit): `<script src="review.js"></script>` between 1701
   (`</script>`) and 1702 (`</body>`). Per prep §3.2: state RV {items, seen-from-localStorage}; wrap
   renderList/setTabHome at load (idempotent, tolerate pre-boot, kick the review.json fetch when S.sites
   first non-empty); Review tab session-only (no hash route - index.html frozen); list = open items minus
   RV.seen; opener order endFit-if-active -> select(site) -> setGround(site.lidar === false ? 'imagery'
   : 'relief', site) -> startFit -> openPlan (row resolved by r.id === plan && r.sites.includes(siteId),
   else synthesized from the candidate's stored fields, prep R6); RV.pending pairs push-then-addPairMarker
   inside an openPlan wrapper, refit() when P.img loads, skip silently on 404 (the test tree has no
   data/raw); saveFit wrapper: after the original returns, `S.db.doc('platefits/'+P.site.id+'.'+
   P.plan.id).get()` 200 -> RV.seen in localStorage, drop from RV.items, refresh count/badge (no second
   PUT, no data/review write from the page - the durable record is the doc + the item's resolved, caught up
   by the next export); the home stats line `<p class="fit">` at 573 gains a computed open count from the
   served review.json fetch, existing sentence byte-for-byte (R8).
5. **tests/test_review.py per prep §4** (keep it stdlib-runnable, port-0 only): case 1 export->served data
   (subprocess CLI with --root tree; idempotent re-run); case 2 headless page load via tools/shot.mjs (Chrome
   155 verified booting in iteration 20: `NODE_PATH=/home/agent/tools/shot/node_modules node tools/shot.mjs
   <served>/ /tmp/... . 8000 1200 800 "<js>"`, js forces S.tab='review'; assert tab count + item row + the
   stats-line number; no pageerror, 404s only the expected data/raw ones); case 3 save->resolve (PUT a BOOK-
   SRC doc in the exact saveFit shape to api/db/platefits/alligator...ancientmonuments00squi_n0214_2; worker
   fails on the missing raw scan and is swallowed - assert the server still answers and the 20 hand-fit docs
   are byte-unchanged (tests/golden pins them); re-run export -> alligator item gone + resolved recorded, the
   other item still open); case 4 (id,site) keying through the headless page (the Larned/mayburgh duplicate
   ids resolve to the right per-site rows) - with a data-level fallback if headless degrades; case 5 cheap
   guards (index.html carries exactly one src="review.js" and no hardcoded review count).
   The test seeds its own queue in the temp tree (module fixture: clear tree/data/review, write one item) -
   it never relies on the repo's two seeds being copied. Module-fixture seeding via fit/review.py's
   upsert_item (import, not subprocess - it's a test setup; the CLI is tested in case 1).
Then tick the six boxes in order and note in the hand-over what 203a imports (upsert_item + the README).
Env notes: suite runs with .venv/bin/python (12 passed at this commit); system python3 fails 4 tests
(test_gate, test_evidence CLI - no PIL/numpy there) PRE-EXISTING, do not chase; the page boots headless
(ready:true, 384 sites, 1166 plans, no pageerror; only the expected scans.json/amazon 404s).
Re-read: web/index.html `select(id)` (783) returns EARLY when a fit is active (`if (!s || P.active) return;`):
the review opener must `endFit()` first, otherwise select() silently does nothing. `startFit` (822) renders
the fit pane's #body (the plan list) - after openPlan (897) the pane shows the fit sheet, so no extra
rendering is needed for pre-placement. `endFit(keepSite=true)` (827) re-renders the site panel: the saveFit
wrapper must not fight it (it only updates RV + the count + the home stats line). Also `addPairMarker` (1059)
numbers the marker with P.pairs.length AT CALL TIME - like the map-click path, push first, then call.
