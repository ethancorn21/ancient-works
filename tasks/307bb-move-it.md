Status: in-progress
# 307bb: Move the drawing - the three gestures, the save, the headless proof, the docs
Depends on: 307ba
Touches: web/fitkit.js, web/index.html, tests/test_fit_queue.py, docs/site_flow.md

## Goal
Parent 307 (and 307b) boxes 3-6, as renumbered there. On the placement 307ba opens, the
drawing is the thing being manipulated: the owner moves it by dragging, scales it with the
wheel, rotates it with shift+wheel (all at the opacity slider's value, with the live scale
and rotation in the panel), pins exact spots on top as a refinement (the map-click flow
unchanged, undo/clear working on both), and saves straight from that placement - writing the
same page-px pairs the three-point flow writes, "by": "hand", the one-site line running, the
overlay appearing. Proved hermetically in a headless part 4 of tests/test_fit_queue.py, and
written up in docs/site_flow.md.

## Acceptance criteria
- [ ] The drawing is on the map from the first frame and is the thing being manipulated:
      drag moves it, a handle / modifier+drag / the wheel scales it, a handle / shift+wheel
      (or the equivalent gesture) rotates it, all at the opacity slider's value; the page's
      panel shows the live scale (m per page pixel) and the rotation. The three-point
      pinning still works on top of the placement (the map-click flow is unchanged; new
      points refine the anchor and re-draw it), and undo/clear still work on both. While
      placed, the map's pan/zoom are disabled (the gestures own the mouse) and re-enabled on
      close; a sub-threshold click pins, a drag moves (MapLibre's 3-px click tolerance
      keeps them disjoint).
- [ ] Saving from direct placement alone writes the platefit doc in the existing shape
      (the placement re-emitted as 3-5 page-px -> lon/lat pairs, plus the existing
      crop/size/model/cite fields, "by": "hand" via the 305 save path, the one-site line
      running) and the overlay appears on the map; a fit saved this way passes the checks a
      three-point fit passes (test_fit_provenance and the golden hand-fit set stay green;
      no document in the shared store is ever written by a test).
- [ ] tests/test_fit_queue.py gains a headless part (the 305 part-3 pattern: Chrome via the
      part-2 line_served-style full tree - tools/fit/pipeline + the picked entry's book page
      materialised into the tree's own data/raw, ephemeral port, sockets dead in the server):
      on a real queue site with a proposal, the page opens place mode with the map at the
      site's box and the ink on it (a seeded dep overlay hidden); scripted input events (a
      drag, a wheel scale, a shift+wheel rotate) change the saved doc's pairs accordingly
      (the doc is read back from the temp store: by:hand, the final re-emitted set, scale
      and rotation agreeing with the anchor within rounding); after close (back / Cancel),
      the site's earlier overlay is back, same file, same ground. Hermetic.
- [ ] docs/site_flow.md: what place mode is now (the anchor and where it comes from, the
      three gestures, the refinement, and what the saved doc contains), citing 307c's
      screenshots when they land (before/after at 1440x900 in docs/site_flow/).

## Notes
- The design (anchor = {u0, v0, lon, lat, mpx, rot}; P.pairs = 5 re-emitted + pinned;
  gestures transform the anchor; pinning refines via the page's own simFit least squares;
  undo/clear from an anchor stack; the image-source quad of a similarity is a parallelogram
  so the rotated picture lands exactly) is in the parent 307b's ## Hand-over and the
  2026-10-12 307b DECISIONS entry - implement from there. The rotated-parallelogram claim
  must be VERIFIED in the headless test (pixels), not assumed.
- The headless save is the long pole: saveFit waits up to 90 s for the one-site line's
  overlay (the line measures ~23 s in this environment; part 2's 180 s budget applies),
  which is why the tree must carry tools/fit/pipeline and the book page locally (the bare
  `served` tree 404s the scan and has no line - part 3's card test lives with both).
- The rotated drawing over the map is a raster image source with 4 corners; the preview
  (refit) already handles both models (simFit for plans, homFit + warpView for views) - the
  gestures feed the same pairs, so the view path should keep working; check it, don't assume.
- If this task exceeds its 3-session budget, split the headless part 4 from the gestures
  (note it in 307b's hand-over when you do). Do not touch fit/surveyfit.py or task 304
  (agent c); agent c's 309 shares tests/test_fit_queue.py - keep the part-4 additions in
  their own clearly-marked section so the merge stays trivial.

## Hand-over

(2026-10-12, iteration 132, agent a - **merge done + committed (c8e6cab); part-4 pick RE-DERIVED on the merged tree and verified; the part-4 section is STILL NOT written into tests/test_fit_queue.py.** Working tree clean, no uncommitted code. The whole next session = transcribe /tmp/fkverify/probe.mjs into the PLACE_PROBE constant + the Python helpers/fixture/test, append after `test_card_done_mark_moves_on`'s last two lines (`assert data["card4"]["text"] == c1["text"]` / `assert e1["name"] not in data["card4"]["text"]` - together unique in the file), run the file, commit, tick boxes 1-3. Read the iter-131 hand-over section in git history (d53bee0) for the full check-by-check design; everything below refines it against the merged tree.)

**Merge (done this session):** `git merge main` -> conflict only in tests/test_fit_queue.py (two card-test reqfail filters: my `arcgisonline` host form vs main's `MapServer/tile/` path form). Resolved as the UNION (both patterns excluded, merged comment) - main's test_review.py (b5cdf19) uses the host form like mine, so neither convention was discarded. Suite: **100 passed + 1 skipped + 0 failed** (matches main's b5cdf19 baseline; the old 221 pair is fixed by c's own commit). Committed c8e6cab. Main brought: 309/804/805 (right-place check in tools/fit_queue.py + the namesake test + regenerated 114-entry web/data/fit_queue.json + 5 new data/review items), the 304 surveyfit work, test_review/test_fit_provenance/test_site_done/test_right_place_drift additions. requirements.in/.txt UNCHANGED (the venv needs no rebuild). web/fitkit.js on my branch is the final gesture version (main never advanced it past 307ba) - the merge kept mine.

**Pick RE-DERIVED on the merged tree (ran /tmp/fkverify/pickmirror.py - keep it until the test lands; it prints the full rejection map):** the queue went 117 -> 114 entries (309 dropped namesake pairs: devil-s-dyke is OUT). New pick = **entries[3] oswestry-castle-q20713795** (was entries[4] pre-merge), row earthworkenglan01allcgoog_n0119_1, view False. Rejection map of entries 0-2: fort-ancient (has doc b24849959_n0264_1, dep: no depictions.json), marietta (has doc b24849959_n0195_1, dep: has file but nothing survives the 150y filter), forthill (item resolved). Pick facts (all re-measured on the merged tree): propose mpx=0.1646 rot=0.0 scale bar '0 100 200 300 Feet' 5 pairs; item data/review/oswestry-castle-q20713795.earthworkenglan01allcgoog_n0119_1.json unresolved, 1 candidate = the row with 3 pairs; NO uncovered rows (the conditional "no model answer" assertion does not fire); site record: name 'Oswestry Castle', lidar None -> ground 'relief', corners present ([-3.0612..,-3.04929] x [52.86469.., 52.85750..]); **done-seed sites = the THREE earlier entries in file order: fort-ancient-q5470727, marietta, forthill** (was four pre-merge - derived in the fixture from the tree's own file, never pinned: doneSites = entries before the pick in the fresh parse of the tree's fit_queue.json). n0119.jpg present in the checkout's data/raw, natural [3367,5050] == row size -> frame scale 1, anchor mpx === propose mpx exactly. **dep default = six-inch-1st.webp** (map 1842; os1inch 1900 filtered by the 150y rule) - from **web/data/sites/<site>/depictions.json** (the page fetches `data/sites/...` through the web static root; the checkout's oswestry dir is a REAL dir, most others are symlinks into the shared store - the fixture's copytree materializes both; `data/sites/` at the repo root has only site.json - do not read it). MAX_PX=2400 at pipeline/plan_fit.py:44 (`^MAX_PX = (\d+)` multiline matches). Machine date 2026-10-12.

**NEW run-2 insight (this session - the throwaway's run-2 seed was only valid because its pick was entries[0]):** playwright `browser.newPage()` makes a NEW CONTEXT (fresh localStorage) - run 1's saved aw.depSel/aw.fitQueue.done do NOT leak into run 2. So run 2's card offers entries[0] (fort-ancient) unless we seed it: **run 2's addInitScript must seed the SAME three keys as run 1: aw.fitQueue.done = the same done-csv, aw.depSel = {pick: six-inch-1st.webp}, aw.ground = 'relief'** (one object arg, destructured names exactly `{sid, f, d}`; one playwright-core argument max). With the done seed the card offers the pick again; site_done.py does NOT regenerate fit_queue.json (verified: no reference in it), so the tree's 114-entry file is unchanged after the save and entries[3] is still the pick. (The iter-131 "run 2's re-seed overwrites run 1's saved choice" wording is obsolete in a fresh context - the re-seed is just explicit insurance for the default.) The throwaway's `localStorage.setItem('aw.fitQueue.done', '{}')` in run 2 must be REPLACED by the done-csv seed, not kept.

**Page-side facts re-verified this session (all as in the committed code - the probe can rely on them):** fitkit.js: anchor {u0,v0,lon,lat,mpx,rot}, P.placed, P.anchorStack; wheel `mpx *= exp(-dy*0.0015)` (dy=-100 -> x exp(0.15)), shift+wheel `rot += dy*0.01` (+100 -> +1.0 deg), drag engages at 4px (the map's 3-px click tolerance keeps pin/drag disjoint), _fkSetGestures toggles [dragPan, scrollZoom, touchZoomRotate, doubleClickZoom, boxZoom] + cursor 'grab'; _fkHint text = `${mpx.toFixed(2)} m per page pixel, turned ${rot>0?'+':''}${rot.toFixed(1)}° · drag to move · wheel to scale · shift+wheel to turn`; _fkActivate finds the FQ entry by site AND best.plan AND propose, seeds anchor from the propose's last pair (centre), fitBounds to the site's corners, hides `dep-<site>`; endFit wrapper applyDep's on close. index.html: openPlan (917) P.crop = map_box * NATURAL W/H unrounded; saveFit (1130): doc = {site, plan, ia, file, crop: P.crop.map(Math.round), model 'similarity', src 'book' (r.ia), url null, ref null, size [naturalW, naturalH], pairs 1dp/7dp, label, title, book, cite, at} + server stamps by:hand (serve.py:216) = exactly 17 keys; saveFit then polls data/sites/<s>/depictions.json 60x1.5s for fit.at===at, sets S.depSel to the NEW overlay, endFit(), applyDep; the PUT /api/db/platefits runs the one-site line in-process (~23 s, 180 s budget). fqPlace calls setGround('relief' for lidar None) after select() (persists aw.ground); card text "Ready to fit <span>N to go</span>" with N = fqPending().length (built + not-done + not-skipped; on the tree = 114 - 3 = 111 after the seed, but COMPUTE it in the probe: FQ.entries.length minus the seeded done sites that are in the file); S.db set at index.html:1693 via openDb (present when served - run128c proved the save path works in a tree).

**The exact next step (one session):** append the part-4 section at the END of tests/test_fit_queue.py (banner: 307bb's, self-contained on purpose): (1) `_default_dep_file(root, site)` - the index.html select()/loadDeps port: read web/data/sites/<site>/depictions.json; keep d if kind not in (map,aerial,topo) or (d.year and d.year <= now.year-150); then first kind in (plan,drawing,view) else LAST 'map' kind -> file or None; (2) `_pick_place_site()` - first entry in file order (no sort) with propose AND `_line_eligible(e, _review_items()[e["site"]]) is not None` AND `_default_dep_file(ROOT, site)` a file -> (entry, item, uncovered, depFile) or None; (3) `place_served` fixture, function-scoped, `_headless_or_skip()` FIRST, then line_served's recipe VERBATIM (copy web+server+tools+fit+pipeline, data minus data/raw, the picked row's page copied into the tree's own data/raw, `[sys.executable, "-c", GUARD, "server/serve.py", "--port", "0"]` cwd=tree, blocking reader thread, 90 s startup / 30 s ready polls), yield {"base","tree","proc","entry","item","uncovered","depFile","doneSites","out"} with doneSites from a FRESH parse of the tree's fit_queue.json = the entries before the pick in file order; (4) `PLACE_PROBE` = /tmp/fkverify/probe.mjs transcribed with: the 3-key addInitScript in BOTH runs (done-csv, depSel, aw.ground='relief'); run 1 gains a card1 read right after boot and the `cardOffersPick` check (card text has 'Ready to fit' + the pick's name + `"%d to go" % (FQ.entries.length - nSeededPresent)` and #fqplace exists); run 2 keeps the throwaway's flow but with the done-csv seed (NOT '{}'); run-2 event lines tagged WITHOUT the '2' suffix (one shared `lines` list; both runs then covered by noPageErrors/noReqfailOutsideKnown); reqfail exclusion = `'/tiles/' in ln or 'arcgisonline' in ln or 'MapServer/tile/' in ln`; drag-start grid widened to x 900-1150 step 25, y 250-550 step 50; MAX_PX read inside the probe from the TREE's pipeline/plan_fit.py (argv: `<base> <site> <plan> <dep_file> <tree> <done_csv|none> <out_dir>`); screenshots 1-place/2-dragged/3-turned/4-saved/cancel into the tmp outdir (docs/site_flow is 307c's); check names EXACTLY: boot, fitkit, cardOffersPick, seed: opensOnWorks/anchorIsPropose/fivePairsOnMap/gesturesOwnMouse/hintLive, drag: moves/keepsScaleRot/keepsUv/centrePairTracks/fitAgrees/cornersLand, wheel: scalesAboutCentre/fitAgrees/hintLive, shift+wheel: turnsOneDegree/keepsScale/cornersLandExactly, pin: addsSixth/refinesAnchor/fiveReemitExact/sixthIsTheClick/fitAgrees, undo: restores/fitAgrees, save: closesPane/stateCleared/newOverlayShowing/docFitsThePlacedAnchor/overlayIsSameSimilarity, cancel: overlayBack/stateCleared, noPageErrors, noReqfailOutsideKnown; `out` carries card1, seed, p0, dragStart, dragOut, wheelBase, wheelOut, turn, pinOut, undoOut, saveStatus, closed, pairsBefore, imgSize, doc, overlay, shown, docFit, cancelOut; ONE final `console.log('[eval] ' + JSON.stringify({ checks, out }))` then all lines then RESULT; exit 1 on any failure (report() for the two early bails: boot, no clear drag point). The throwaway's throwaway-only bits to DROP in the transcription: the `[api]` request logging, the `[console]` echo via log1/log2 (collect silently into the shared lines list), the separate `console.log('[seed]...')` (fold into out.seed); the _fkvAnchorAt/_fkvFitChecks HELPERS injection stays (it is the pixel proof of the rotated-parallelogram claim: fit-prev source corners vs the anchor similarity, closure + maxCorner < 0.2 m). (5) `_run_place_probe(base, tree, site, plan, dep_file, done_sites, outdir)` = _run_probe's shape: write outdir/place_probe.mjs, argv above (done_csv = comma-join or 'none'), node with NODE_PATH=NODE_MODULES, timeout=600, parse [eval], assert rc 0, return (data, p); (6) `test_placement_gestures_and_save_in_the_browser(place_served, tmp_path_factory)`: hash the checkout's write surface FIRST via the existing `_h` (data/db/platefits/*, web/data/sites/<site>/*, web/data/sites.json, web/data/review.json, data/review/*; a {str(path): bytes} dict), run the probe, assert every check by name (on failure include data["out"] + p.stdout[-2000:]), then the Python-side doc read from the TREE (tree/data/db/platefits/<site>.<plan>.json): by 'hand', site/plan, model 'similarity', pairs == out.pairsBefore, size == out.imgSize, **crop = JS-round (int(v + 0.5)) of map_box * out.imgSize (refinement 1)** or [0,0,W,H], ia/file/src 'book'/url None/ref None/label/title/book/cite from the entry's row, at startswith '2026-', and the EXACT 17-key set incl 'by'; then the Python-side overlay read (tree's web/data/sites/<site>/depictions.json): the entry with fit.doc == doc_id has kind 'plan', file 'plan_<plan>.webp', ink 'plan_<plan>_ink.webp', fit.at == doc.at, fit.pairs == 5, fit.model 'similarity', all fit.resid_m < 1, fit.m_per_px within 1e-3 rel of anchor.mpx*fs/f and fit.rot_deg within 0.01 of the anchor rot (MAX_PX read from the CHECKOUT's pipeline/plan_fit.py; fs = imgSize[0]/doc.size[0]; f = min(1, MAX_PX/max crop px in the image frame = max((crop[2]-crop[0])*fs, (crop[3]-crop[1])*fs)); the anchor comes from out.turn (the post-gesture, pre-pin anchor - the saved one)); then the re-hash must equal the first (hermetic). Then run `.venv/bin/python -m pytest tests/test_fit_queue.py -q` (expect ~5-8 min for the whole file: part 2 ~30 s, part 3 ~2x45 s, part 4 ~2-3 min incl the ~23 s one-site line twice... note run 2 does NOT save, so the line runs once) and commit `<task>: headless part 4 - ...`. After it passes: tick boxes 1-3 of the task, then box 4 (docs/site_flow.md place-mode section on the lead's 89043b7 version - now merged in; cite 307c's screenshots when they land).

**Env/state:** .venv present and current (requirements unchanged by the merge); suite at 100+1/0 post-merge (measured). /tmp/fkverify/ intact: probe.mjs (434 lines - the transcription source; its run-2 '{}' done seed is the ONE thing to replace), pickmirror.py (this session's picker mirror - delete or keep after the test lands), run128c.log (the last all-green throwaway run: 41/41), tree/ (STALE server possible: `pgrep -f serve.py` + `readlink /proc/$p/cwd`, kill only cwd=/tmp/fkverify/tree). No split (the iter-130 ruling stands: only the test + docs remain, letter-ordering would delay the critical path). Done-claim baseline: the suite must be green (it is, at 100+1/0); when claiming done for 307bb, the driver compares against the then-current main state - 309 is now merged, so the old "4-failure baseline" note is obsolete.

**Re-read:** the iter-131 hand-over (git show d53bee0:tasks/307bb-move-it.md) for the original check-by-check list; /tmp/fkverify/probe.mjs + run128c.log; tests/test_fit_queue.py parts 2-3 (line_served ~828, _run_probe ~1129, the two card tests at the end - the append anchor); web/fitkit.js (header = design doc); /tmp/fkverify/pickmirror.py (the merged-tree rejection map).

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/307bb-move-it.md` (in-progress) - hand-over: (2026-10-12, iteration 131, agent a - **orientation + verification only; the part-4 section is still NOT written into tests/test_fit_queue.py.** Worki
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/216-view-books-entries.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-12 307b DECISION: box 1 (the queue carries the propose) designed in full; 307b split into 307ba (boxes 1+2) and 307bb (boxes 3-6) - no code written this session (investigation only)
The owner's rework spans the queue's data and the page, so 307b is split along the same seam
the parent pre-announced (fly-to/hide-restore vs gestures): 307ba = the queue file carries
the propose (box 1) + place mode opens on the works (box 2); 307bb = the gestures, the save,
the headless proof, the docs (boxes 3-6). Both subtask files written; the parent 307's
hand-over box map updated; no letter reorder.

Box 1, implemented-by-design (the 307ba agent codes it; nothing here failed, it was never
attempted yet):
- **fit/propose.py becomes root-aware** (added to 307ba's Touches): the four loaders
  (_index_row, _plans_rows, _plans_row, _site) take a `root` arg and _CACHE is keyed
  (str(root), kind) so a temp tree never collides with the checkout's data; propose_for
  gains `root=ROOT` (default = today's behaviour, byte-identical for every existing 2-arg
caller: batch_us, inkfit, inkfit_heldout, test_batch_us/eu/propose). Contract docstring
  updated for the optional param. WHY not monkeypatch ROOT/`_CACHE` from fit_queue.py:
  the cache is keyed by nothing today, so two roots in one process would silently read
  each other's files; a root param is the one-place-for-one-knowledge fix, and it lets
  the TESTS derive expected proposals against the same temp tree the generator ran on.
- **tools/fit_queue.py**: `sys.path.insert(0, str(ROOT / "fit")); import propose as _propose`
  (the site_done.py:43 convention; fit/ has no __init__.py - implicit namespace or
  sys.path, both work, but the codebase uses the sys.path insert). Per entry in build():
  try _propose.propose_for(e["site"], plan, root=root) except Exception -> NO propose key
  (fail open: the page falls back to the three-point flow; covers no size, no size_m, no
  stage-B row, missing index.jsonl). On success: entry["propose"] = the six keys in box
  order {pairs, scale_m_px, rot_deg, scale_source, coarse, note}; "ground" is dropped
  (the page derives it from site.lidar, as it already does in fqPlace). Key lands after
  "candidates" in the entry dict. Docstrings: the tool reads a fifth input
  (data/books/index.jsonl, stage-B fields) and stays stdlib-only (propose.py is too).
- **Regenerate web/data/fit_queue.json in the checkout** (it is a TRACKED file -
  `git check-ignore` says no - not the shared store): all 117 current entries anchor
  (measured: 20 bar, 4 ratio, 93 picture_size; n0686 = scale_m_px 0.3621, rot 0).
  After agent c's 309 merges its place check into main, the next regeneration on this
  branch is the joint behaviour - regenerate on top of whatever the branch shows.
- **Tests (part 1 of test_fit_queue.py; parts 2-3 untouched - they read the file the page
  ignores propose in)**: extend _build_synthetic_tree - sites gain lon/lat/size_m; add a
  data/books/index.jsonl with stage-B rows: row-a1 (s-alpha, book "Book A") scale_text
  "0 100 200 300 Feet" + a scale_bar box [0.15,0.6,0.85,0.62] on size [1000,1000] -> bar,
  scale 91.44 m / 700 px = 0.1306 (hand-pinned), north_angle_deg 20 + arrow true ->
  rot 20.0 (trustworthy); row-e1 (s-eta, book "Book E") scale_text "500 Feet to the Inch."
  but "Book E" has no ppi in BOOK_PPI -> ratio unusable -> picture_size fallback
  (s-eta size_m [200,150] -> 0.2, coarse true); row-g1 (s-gamma) no scale text and s-gamma
  deliberately WITHOUT size_m -> no propose (the no-size_m case); NEW site s-nope + row
  row-n1 whose plans size is null and whose index row has no full_size -> no propose
  (the no-size case; s-nope still has a size_m, so size is the missing piece). Entry count
  6 -> 7, s-nope sorts last (draw_px 0, plan id after the rest); the pinned stdout line
  becomes "ready-to-fit queue: 7 site(s) -> ...". Assertions: each anchoring entry's
  propose equals the 6-key dict derived by calling propose.propose_for(site, plan,
  root=tree) in-test (the algorithm is pinned by 202's golden tests/golden/propose_202.json,
... (3.9 KB more: `grep -n -A 200 -F '## 2026-10-12 307b DECISION: box 1 (the queue carries the propose) designed in full; 307b split into 307ba (boxes 1+2) and 307bb (boxes 3-6) - no code written this session (investigation only)' DECISIONS.md`)

### 2026-10-12 307bb DECISION: iteration 129 - filed task 221 for the two review-test failures (test-side drift on pristine main: the Esri feed's singular 'tile/' URLs and the re-worded home stats line); fixed my two card tests' reqfail filters (added the arcgisonline exclusion); suite now 73 passed + 1 skipped + 2 failed (exactly the 221 pair)
Executed the iter-128 plan steps 1-4.

- **tasks/221-review-stats-test.md created** (Status: open, `Depends on: 309`, `Touches: tests/test_review.py`, 221 = lowest free number in 200-499): the two review tests fail on PRISTINE main (proved iter 128 via the /tmp/maincheck scratch of 89043b7), so they are test-side drift, not regressions: (a) test_plan_lookup_is_keyed_by_id_and_site's strict `"[reqfail]" not in p.stdout` chokes on the page's live Esri base-imagery fetches (server.arcgisonline.com/.../MapServer/tile/... - the SINGULAR 'tile/' segment defeats the '/tiles/' path exclusion the other tests use); (b) test_page_shows_the_review_list filters the home stats line by "built in all" while the lead's 939382a re-worded it (web/index.html:588) to "laid on today's ground" and web/review.js:74 already accepts both wordings. `Depends on: 309` is a same-file race gate (agent c edits tests/test_review.py now). The boxes say: fix, don't delete/loosen.
- **tests/test_fit_queue.py (MY file): both card-test reqfail predicates now exclude `arcgisonline` in addition to `/tiles/`** (lines 874-881, 941-948), each with a comment naming the host and the singular-tile fact. Verified not a weakening: the tests' own comments already declare the relief-tile aborts "page-caused, expected"; the Esri World_Imagery feed (web/index.html:314) is the page's base imagery and this machine has no internet, so those fetches die by design - the filter was simply missing that URL class. Ran both card tests after the change: **2 passed** (31.6 s).
- **PITFALLS.md**: new entry "the page's base imagery is a live Esri feed ... SINGULAR 'tile/'" under This machine and its environment (the relief-tile sibling's missing twin).
- **Suite: 73 passed + 1 skipped + 2 failed** (115.9 s). The 2 failures are exactly the 221 pair (both in tests/test_review.py, the Esri reqfail and the stats wording) - they were failing before my change (part of the 4-failure main state), so my delta took the suite from 4 failed to 2. No test that was green before is red now.
- Driver sync deb2730 merged main into my branch this session, so the lead's 89043b7 (docs/site_flow.md 9 lines, fit/matchfit*, the review export shrink) is now in my tree - box 4 will build on the lead's docs version.

### 2026-10-12 307bb DECISION: iteration 130 - committed the _pick_site refactor (0177e3a, proven 3 passed/20s); derived the part-4 pick (entries[4] oswestry-castle: entries 0-3 fail the line's own constraints, so the committed pick is NOT entries[0] and the card needs a MULTI-site done seed - the one new mechanism vs the throwaway); part-4 section fully designed (hand-over) but not yet written
- **Refactor (committed 0177e3a):** the one-site line's per-entry constraints left _pick_site's loop and became `_line_eligible(e, it)` -> uncovered or None (same checks, same order, same comments), plus `_review_items()` for the items dict the old loop built inline. `_pick_site` is unchanged in behaviour: picks sorted uncovered-first, returns (entry, item, uncovered). Proven: test_fit_queue_synthetic + test_fit_queue_real + test_save_runs_the_one_site_line = 3 passed in 20.24 s. Needed because the part-4 pick requires the SAME line constraints plus two extras (a propose, a drawable earlier overlay) - AGENTS.md: extract, don't copy.
- **The part-4 pick is entries[4], not entries[0] (the throwaway's Devil's Dyke):** verified by running a mirror of the final picker over the live queue: [0] devil-s-dyke-q3307343 REJECTED (an agent doc exists: devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0662_1.json, by:agent - the "no existing doc" constraint), [1] fort-ancient-q5470727 (doc b24849959_n0264_1), [2] marietta (doc b24849959_n0195_1), [3] forthill (item resolved b24849959_n0269_1 + doc) -> [4] oswestry-castle-q20713795 passes all (plan earthworkenglan01allcgoog_n0119_1 / page n0119.jpg local; item unresolved with the row as candidate, 4 pairs; no docs; dep default six-inch-1st.webp (1842 <= 1876, os1inch 1900 filtered); propose mpx 0.1646 rot 0). Consequence the throwaway never faced: the card shows entries[0] on a fresh browser, so the probe must seed aw.fitQueue.done with the 4 EARLIER entry sites in BOTH runs (the page's own done-map; part 3 proved single-site seeding - multi-site is the one new mechanism, Object.fromEntries of a comma list). Done-seed sites = devil-s-dyke-q3307343, fort-ancient-q5470727, marietta, forthill (derived in the fixture by file order, never pinned).
- **n0119 row verified:** size [3367,5050] == actual n0119.jpg (3367x5050) -> _fkFrameScale = 1, so the seeded anchor EXACTLY equals the propose (the probe's exact-equality checks hold); map_box [0.198,0.168,0.875,0.778]; book 'Allcroft 1908', label 'Fig. 17', title 'Camp, Old Oswestry, Salop', cite present, url/ref null, view false; site lidar None -> ground 'relief'; corners present.
- **saveFit's doc shape re-read (web/index.html ~1122-1148):** doc = {site, plan, ia, file, crop: P.crop rounded, model: view?'homography':'similarity', src: ia?'book':'commons', url||null, ref||null, size: [natural W,H], pairs: [[u 1dp, v 1dp, lon 7dp, lat 7dp]...], label, title, book, cite, at} + the store stamps by:hand = exactly 17 keys (the test asserts the EXACT key set). The page's saveFit then polls data/sites/<site>/depictions.json 60x1.5 s for a plan/view depiction with fit.at === at, refreshes S.dep/depSel to it, endFit() (fitkit's wrapper restores the dep layer, _fkDeactivate clears placement + re-enables gestures) and applyDep - the overlay that shows after a save is the NEW one; run 2's re-seeded aw.depSel (the original survey) overrides it in the fresh page's localStorage.
- **MAX_PX handling:** do not copy the 2400 constant - read it where it lives, pipeline/plan_fit.py:44 (re.search(r"^MAX_PX = (\d+)", ..., re.M) in the test; the probe reads the tree's copy the same way) - one place for the knowledge.
- **Still open:** the whole part-4 section (banner + _default_dep_file + _pick_place_site + PLACE_PROBE + _run_place_probe + place_served fixture + test) is designed in the hand-over to the last detail and must be written next session, then run (expect ~60-90 s: boot + place + gestures + the ~23 s one-site line + run 2) and committed. No code is uncommitted; this session's only change is the refactor commit plus these notes.
... (1.4 KB more: `grep -n -A 200 -F '## 2026-10-12 307bb DECISION: iteration 130 - committed the _pick_site refactor (0177e3a, proven 3 passed/20s); derived the part-4 pick (entries[4] oswestry-castle: entries 0-3 fail the line's own constraints, so the committed pick is NOT entries[0] and the card needs a MULTI-site done seed - the one new mechanism vs the throwaway); part-4 section fully designed (hand-over) but not yet written' DECISIONS.md`)

### 2026-10-12 307bb DECISION: iteration 131 - orientation + verification only; the part-4 section is still unwritten (context limit hit at the docstring edit). Two refinements to the iter-130 design recorded: (1) openPlan (index.html:918) computes P.crop from map_box * the image's NATURAL W/H, not row.size - so the Python-side expected crop must be derived from the probe's recorded out.imgSize (page's own W/H), JS-style rounding int(v + 0.5); for n0119 natural == row.size so the value is unchanged; (2) the throwaway's run-2 lines were tagged '[console2]'/'[pageerror2]'/'[reqfail2]', so its final honesty filters (startsWith('[pageerror]') / startWith('[reqfail]')) could never match a run-2 line - run128c passed only because no such lines occurred at all; the committed probe drops the '2' suffix (the runs are sequential) so noPageErrors and noReqfailOutsideKnown cover both runs. Also recorded: the third of the seed's three keys (one object arg {sid, f, d}) is aw.ground = 'relief' (the page's default, made explicit); aw.depSel is persisted by saveFit (index.html:1147), so run 2's re-seed with the original survey file is what makes the Cancel check see the survey back. Pick re-confirmed as entries[4] oswestry-castle-q20713795 under the full 3-constraint picker (propose AND _line_eligible AND _default_dep_file), with the rejection map refined: entries 0-3 fail the line constraints (iter 130), and additionally 1 fort-ancient and 2 marietta have NO drawable default depiction at all (dep default None) while 3 forthill's default is a plan overlay (plan_b24849959_n0269_1.webp), not a survey sheet; dep defaults of the first six entries measured (0 and 4 = six-inch-1st.webp, 1 and 2 = None, 3 and 5 = plan overlays). Nothing failed, nothing run (no test execution this session; last run remains iter 130's 3 passed/20.24 s post-refactor). Verified by running the picker mirror and reading the live tree: n0119.jpg present in the checkout's data/raw; MAX_PX = 2400 at pipeline/plan_fit.py:44 (the ^MAX_PX = (\d+) multiline regex matches); machine date 2026-10-12 (so the doc at startswith '2026-' holds); buttons #fcancel/#fsave (index.html:904), #fundo (900), #fitcv (243) exist; /home/agent/tools/shot/node_modules present. Only working-tree change this session: tests/test_fit_queue.py's module docstring gains the Part 4 paragraph (uncommitted - the harness keeps it for the next agent, which appends the section after test_card_done_mark_moves_on and runs the file).

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (1 tests)
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_gate.py:36: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    1 failed, 59 passed in 63.50s (0:01:03)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-12 AGENT A (307bb, iteration 132): where I stand
Merge of main into agent/a is DONE and committed (c8e6cab) - the one flagged conflict (tests/test_fit_queue.py card-test reqfail filters) resolved as the union of both sides' Esri exclusions (/tiles/ + arcgisonline + MapServer/tile/); suite 100 passed / 1 skipped / 0 failed. The part-4 pick was RE-DERIVED on the merged tree: it is now entries[3] oswestry-castle-q20713795 (devil-s-dyke left the queue with 309's right-place check), so the card's done-seed is the three earlier entries (fort-ancient, marietta, forthill). The part-4 section of tests/test_fit_queue.py is still unwritten: next session transcribes /tmp/fkverify/probe.mjs (run-2 done-csv seed correction + card1/cardOffersPick + the iter-131 run-2 tag fix + union reqfail filter), appends the section at the file's end, runs the file, commits, ticks boxes 1-3, then box 4 (docs). Full design in the task's hand-over.
