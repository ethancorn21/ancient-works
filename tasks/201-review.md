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
Iteration 23 (2026-10-11). Steps 1-4 are DONE (step 2: commit ad8dbc1; step 3: 0b65deb; step 4: the commit after this edit). State:
- `fit/review.py` + `data/review/` (README + 2 seeds) + `web/data/review.json` (2 open) as before.
- `web/index.html`: only +1 line (`<script src="review.js"></script>` between `</script>` and `</body>`) plus the step-3 keying fix. 1707 lines now.
- `web/review.js` (new, ~200 lines, vanilla, no deps): `RV = {items, seen (localStorage 'aw.reviewResolved'), loaded, fetching, pending}`.
  Wraps the page's globals (installed once at load, all reassignments of the big script's function globals):
  * `renderList`: original first, then - S.tab==='review' -> `rvRender()` (tabs row + lede + items); else `rvPatchTabs()` (appends `<button id="h-review">` spanning the 1fr-1fr grid, via injected `<style id="review-style">`) + `rvPatchStats()`; kicks `rvLoad()` once.
  * `rvLoad()`: fetch `data/review.json` (404 = empty queue); filters `RV.seen`.
  * `rvPatchStats()`: finds the home stats `<p class="fit">` BY THE TEXT 'built in all' (not by position), appends a `<button id="rvcount">` "· N review items open" (only when N>0; removed when 0). Original sentence stays byte-for-byte.
  * `setTabHome('review')`: S.tab='review', clears hash, re-renders. NEVER writes 'aw.tab' (index.html line 531 restores S.tab from it at boot; review is session-only by that omission).
  * `openPlan`: after the original, if `P.img && RV.pending`: push each pair then `addPairMarker(p)` then `refit()` (map-click order: markers number 1..n); on 404 (no `data/raw`) clears pending silently.
  * `saveFit`: after the original (both overlay-found and 90 s timeout paths reach here), GETs `platefits/<site>.<plan>`; if it exists and the plan is one of the item's candidates, `rvResolved()` (seen + lsSet + splice out of RV.items). No second PUT, no data/review write; the item's `resolved` is caught up by the next export. `rvResolved` mirrors the export's derivation (any candidate's doc resolves the item).
  * `loadDeps`: dedupes in-flight fetches per site (rvDepFlight) - REQUIRED: without it, `select()`'s async `loadDeps().then(renderSite)` lands after `startFit`/`openPlan` and clobbers the fit sheet. `rvStartFitAt` awaits it between `setGround` and `startFit` (microtask order: select's .then runs first, on the same promise).
  * Opener `rvStartFitAt(it, c)`: `if (P.active) endFit()` -> `select(site.id)` -> `setGround(lidar===false?'imagery':'relief', site)` (select force-sets imagery; this restores fitkit) -> `await loadDeps` -> `startFit` -> `openPlan(row)`. Row = `P.rows.find(r => r.id===plan && r.sites.includes(siteId))` (the step-3 keying makes duplicate-id rows resolvable) else synthesized from the candidate's stored fields (missing map_box -> null -> whole page; missing view -> false).
  Headless-verified this iteration (scratch tree + tools/shot.mjs, Chrome 155): tab "Review (2)" + aria-pressed, list rows (Alligator 2 candidates lead first; Bibracte no-picture chip + searched + "Open this site's plan search"), stats line "…384 built in all; … · 2 review items open"; opening the alligator item: ground=relief, book row loaded 2876x4068, crop from map_box, 5 pairs pre-placed, markers "1..5", fit mpx 0.7374 (seed 0.7375), Save enabled; no-picture item: ground=imagery, plan search with status; then real save via the page: PUT 200 -> worker (pipeline + .venv python) ran plan_fit (resids ~0) -> overlay depiction in ~14 s, red-square map source added, item gone, badge "Review (1)", stats 25->26 drawings.
NEXT STEP 5: `tests/test_review.py` per prep §4 (keep stdlib-runnable, port 0, no network). Details that matter now that 4 is built:
- Module fixture: reset the temp tree's queue: delete `tree/data/review/*` and the copied `tree/web/data/review.json`, then write seed item(s) via `import fit.review` (`upsert_item`, NOT the CLI - the CLI is case 1). The repo's two seeds ARE copied into the tree by conftest, so deleting first is essential (the test owns the queue).
- Case 1: CLI export (subprocess `[sys.executable, 'fit/review.py', 'export', '--root', str(tree)]`) -> GET data/review.json (200, items, name, lead, candidate fields, no-picture searched); idempotent re-run (same body modulo `at`).
- Case 2: headless via `NODE_PATH=/home/agent/tools/shot/node_modules node tools/shot.mjs <served>/ <tmpfile.png> 8000 1200 800 "<js>"` (the png path must be in a temp dir). Probe pattern that WORKS (used above): an async IIFE that polls `S.sites.length && RV.loaded`, then `S.tab='review'; renderList();` and reads `#body .tabs button` text + `#body` innerText, then `S.tab='sites'; renderList();` and reads the stats `#body .fit`. Assert badge count, item rows, stats number; assert no `[pageerror]` in the subprocess stdout and 404s only the expected ones (scans.json, amazon areas, and - in the raw-less temp tree - the book/media image of the opened plan, IF the probe opens one). In the pytest tree `data/raw` is ABSENT (conftest excludes the symlink) so any opened picture 404s: assert the list/count/stats, not the pre-placed pairs (the happy path was verified against a scratch tree where raw resolved).
- Case 3: PUT a BOOK-src doc (ia set, url null, model similarity, >=3 pairs, at) to `api/db/platefits/alligator-effigy-mound-q4732645.ancientmonuments00squi_n0214_2` in the exact saveFit shape -> 200; the worker (venv python HAS numpy; no raw) fails on the missing scan and is swallowed - assert the server still answers GET / and the 20 golden hand-fit docs are byte-unchanged in the tree; re-run the export -> alligator item gone with `resolved.doc` recorded in the item file, the other seeded item still open.
- Case 4: (id,site) keying - the iteration-22 scratch check PASSED against the live web/ root; repeat through the temp tree if cheap (evaluate P.byId composite keys + the four duplicate-id sites' fit-list buttons), else data-level fallback: composite-key uniqueness over served plans.json + test_data still passing; note the gap in DECISIONS if degraded.
- Case 5: guards: served index.html contains exactly one `src="review.js"` and no review count in the raw HTML; review.json numbers are computed (case 1 already checks the body).
Run `.venv/bin/python -m pytest -q` (suite is 13 at this commit: 12 + 801's; all pass) - new cases must not bind fixed ports or write outside the tree/temp dir.
Then step 6: tick the six boxes in order, note what 203a imports (`fit.review.upsert_item` + `data/review/README.md`), final hand-over.
Re-read (fresh eyes):
- web/review.js `rvPatchStats` - the stats line is located by the literal text 'built in all'; if a later task changes that sentence, the review count clause silently disappears (no error). 211/212 touch the page data - watch this.
- web/review.js `rvStartFitAt` - the `await loadDeps(site)` between `setGround` and `startFit` is load-bearing (select's async renderSite otherwise clobbers the fit sheet); do not reorder.
- web/index.html line 531 `S.tab = lsGet('aw.tab', 'sites')` - the prep's claim "S.tab is never read from localStorage at boot" was WRONG; review.js keeps review session-only by never writing 'review' to 'aw.tab' (the setTabHome wrapper). If a future task stores other tab values there, this stays correct only while 'review' itself is never stored.
- tests/conftest.py line 56 - the temp tree EXCLUDES `data/raw` (a symlink to /home/agent/projects/ancient-works/data/raw in the repo; `du` on it shows 0 - it is NOT empty, it is a link; my /tmp scratch copies followed it, which is why the scratch "test tree" served real pictures).
Env: suite = 13 passed under .venv/bin/python (driver); system python3 fails 4 (test_gate, test_evidence CLI - no PIL/numpy there) PRE-EXISTING, do not chase. Chrome at /opt/google/chrome/chrome; shot.mjs needs `NODE_PATH=/home/agent/tools/shot/node_modules` (Mac-path createRequire in shot.mjs resolves only with it). The page boots headless here (WebGL warnings are noise; GPU-stall warnings are noise).
