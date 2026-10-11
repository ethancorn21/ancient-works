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
Iteration 24 (2026-10-11). Steps 1-4 are DONE as before (ad8dbc1, 0b65deb, 6835279). Step 5 is IN
PROGRESS: `tests/test_review.py` is WRITTEN (new file, 5 tests per prep §4, stdlib-only, ~230 lines)
but NOT YET RUN — the session hit its context limit right after writing it. The file is uncommitted
in the working tree; the harness saved it.

NEXT STEP (one step): make it green, then finish the task:
1. `.venv/bin/python -m pytest -q` — expect 18 (13 + the 5 new). Sanity: `python3 -m pytest
   tests/test_review.py -q` (system python has no PIL/numpy; the 4 pre-existing failures in
   test_gate/test_evidence are not this task's).
2. If a new test fails, the dry-run record below is the ground truth of what each case saw.
3. Then step 6: tick the six boxes in order (box 1: case 1; box 2: cases 2+5; box 3: case 3; box 4:
   case 1's computed body + case 2's stats check; box 5: case 4), note for 203a what it imports
   (`fit.review.upsert_item` + `data/review/README.md`), final hand-over, commit.

Dry-run record (scratch tree built exactly like conftest — web/ + server/ + data/ minus data/raw;
venv and system pythons behave identically for these cases): ALL FIVE CASES VERIFIED.
- Case 1 (CLI export): `python3 fit/review.py export --root tree` prints exactly
  "review: 2 open of 2 items -> web/data/review.json\n"; re-run is idempotent (body equal modulo at).
- Case 2 (headless list): shot.mjs probe (tools/shot.mjs, NODE_PATH=/home/agent/tools/shot/node_modules,
  POSTWAIT=300) boots (polls S.ready && S.sites.length && RV.loaded, 30 s budget). After `S.tab=
  'review'; renderList();` the tabs come back `["h-sites=Sites:false","h-finder=Finder:false",
  "h-review=Review (2):true"]`. NOTE: page CSS uppercases list text — innerText came back
  "ALLIGATOR EFFIGY MOUND" etc.; the committed probe reads textContent (raw case) and the test
  lowercases before matching. Stats: the one `#body .fit` containing 'built in all' ends
  "...· 2 review items open". In-page: `data/review.json` fetches 200, `data/scans.json` and
  `data/amazon/areas.json` 404; exactly 2 `[console] error ... 404` lines per load (stable across
  runs; the browser console prints no URL, only the count); no [pageerror], no [reqfail].
- Case 3 (save resolves): PUT the book doc in the exact saveFit shape (built from the seeded
  candidate; crop = [x1*w, y1*h, x2*w, y2*h] from map_box×size — size is [w,h] TWO elements, map_box
  FOUR; an early dry-run script indexed them together and hit IndexError — the test has the right
  form) → 200 {"ok": true}. IMPORTANT CORRECTION to the prep: in the temp tree the plan_fit worker
  does NOT "fail on the missing scan" — conftest copies no pipeline/ at all, so the worker thread
  DIES at `import plan_fit` with ModuleNotFoundError (printed "Exception in thread plan_fit:"
  into the server's stdout pipe, which conftest never reads again — harmless, tiny). Server stays up
  (4× GET / all 200 over 4 s). A 374-file sha256 snapshot (all platefits docs + all depictions.json)
  before/after: the ONLY change is the one new doc file. Re-export → stdout "review: 1 open of 2
  items -> web/data/review.json\n", review.json has bibracte only (still open, searched intact), the
  item file gains `resolved: {doc: "alligator-effigy-mound-q4732645.ancientmonuments00squi_n0214_2",
  at: <PUT at>}` (the test PUTs a fixed at "2026-10-11T12:00:00.000Z" for determinism).
- Case 4 (keying): probe selects each of the four duplicate-id sites, awaits loadDeps, startFit,
  reads `#body [data-plan]` buttons. All four composite keys present in P.byId, each resolving to its
  site's own media url (c_ffb3daac218b481f → ffb3daac218b481f.jpg per site;
  c_984782b9e35e8ded → 984782b9e35e8ded.jpg per site); every button on every site's fit list has
  row:true and has:true; no pageerror. The test checks presence + urls (not set equality), so a
  future task adding rows sharing these ids won't false-fail it.
- Case 5 (guards): served index.html contains src="review.js" exactly once; h-review / rvcount /
  "Review (" all absent from the raw HTML; GET /review.js → 200 (10219 bytes).

Field-name trap hit once: the item file field is `no_picture_found` (not no_picture); the test's
seed helper passes `no_picture=item["no_picture_found"]` to `review.upsert_item`.

Housekeeping for the next agent: leftover scratch artifacts in /tmp (rvtest24_*.py, rvtest24_*
.log, probe2.js, probe4.js, rv24_*.png, rvtest24_url*.txt); a scratch serve.py may still be running
on an ephemeral port — check `ps aux | grep -F serve.py` and kill by PID (NEVER `pkill -f serve.py`:
the pattern matches your own shell's command line and kills the shell — it bit this session).
Re-read (fresh eyes): web/review.js rvPatchStats (the stats line is located by the literal text
'built in all' — silent disappearance if that sentence ever changes); web/review.js rvStartFitAt
(the `await loadDeps` between setGround and startFit is load-bearing — do not reorder);
tests/test_review.py `_shot`/`_probe` (shot.mjs contract: `<url> <png> [waitMs=8000] [1200] [800]
[js]`, one argv element, no shell; the `[eval]` line is JSON.stringify of the probe's return);
index.html line ~531 (`S.tab = lsGet('aw.tab', 'sites')` — review stays session-only by never
writing 'review' there); tests/conftest.py line ~56 (temp tree EXCLUDES data/raw AND has no
pipeline/ — that is why the worker dies on import, case 3).
