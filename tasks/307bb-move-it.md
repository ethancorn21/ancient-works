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

(2026-10-12, iteration 130, agent a - **part 4 in progress: the `_pick_site` refactor is committed (0177e3a) and proven (part 1 + part 2 = 3 passed in 20.24 s); the part-4 section itself is DESIGNED in full but NOT yet written into tests/test_fit_queue.py - writing it is the whole next session.** No uncommitted code; the repo is clean apart from this note.)

**What remains (307bb's boxes):** 1. Write + run + commit part 4 (box 3) per the design below. 2. Box 4: the place-mode section in docs/site_flow.md on the lead's 89043b7 version, citing 307c's screenshots when they land. 3. Tick boxes 1+2 once part 4 lands (their code is committed in e7af85c + the 0177e3a refactor; the part-4 test is their proof), then the done-claim against the 4-failure main baseline (2 card = fixed by me iter 129; 2 review = task 221, which Depends on 309 - agent c).

**Part 4 design (everything verified this session against the live tree):**
- **Append a clearly-marked section** at the end of tests/test_fit_queue.py (agent c's 309 edits this file - keep mine in its own banner-commented area). Reuse only: `_line_eligible`, `_review_items`, `_rows_naming`, `GUARD`, `CHROME`, `NODE_MODULES`, `_headless_or_skip`.
- **`_default_dep_file(root, site)`** - port of web/index.html select()/loadDeps: keep `d` if kind not in (map,aerial,topo) or (d.year and d.year <= now.year-150); default = first kind in (plan,drawing,view) else LAST map-kind; -> file or None.
- **`_pick_place_site()`** - FIRST entry in file order (NOT uncovered-sorted): has `propose` AND `_line_eligible(e, _review_items()[e["site"]]) is not None` AND `_default_dep_file` gives a file. Today = **entries[4] oswestry-castle-q20713795** (plan earthworkenglan01allcgoog_n0119_1, page n0119.jpg 3367x5050 == row size -> _fkFrameScale 1, so anchor EXACTLY equals the propose: mpx 0.1646 rot 0; dep default six-inch-1st.webp; lidar None -> ground 'relief'; title 'Camp, Old Oswestry, Salop'). **entries 0-3 are rejected** (0 devil-s-dyke has an AGENT doc, 1 fort-ancient doc, 2 marietta doc, 3 forthill resolved item + doc) - all confirmed by running the mirror. So the card does NOT naturally show the pick: **the probe seeds aw.fitQueue.done with the 4 earlier entry sites** (the page's own done-map mechanism, part 3 proved seeding works) in BOTH runs.
- **`place_served` fixture** (function-scoped; call `_headless_or_skip()` FIRST so a Chrome-less machine skips before the expensive copy): pick, then line_served's copy VERBATIM (web+server+tools+fit+pipeline, data minus data/raw, the picked row's book page materialised into the tree's own data/raw, server `[sys.executable, "-c", GUARD, "server/serve.py", "--port", "0"]` cwd=tree, PIPE stdout with the blocking reader thread - NOT the file-log trick, the test process outlives the pipe; sys.executable IS the driver's .venv when the driver runs, numpy present). Yield {"base","tree","proc","entry","item","uncovered","depFile","doneSites","out"} where doneSites = sites of entries before the pick (break on `e["site"] == entry["site"]` - a fresh parse, never `is`).
- **`PLACE_PROBE`** = /tmp/fkverify/probe.mjs VERBATIM except: (a) header says it is the committed part-4 probe; (b) argv gains `done_csv` before outdir (`<base> <site> <plan> <dep_file> <tree> <done_csv|none> <out_dir>`); (c) BOTH runs' addInitScript seed THREE keys, ONE object arg with EXACTLY matching destructured names `{sid, f, d}` (the iter-128 silent-undefined trap): `aw.fitQueue.done` = Object.fromEntries(doneCsv.split(',').map(s=>[s,'2026-10-12T00:00:00.000Z'])) and `aw.depSel` = {sid: f}; (d) `check(name,cond,info)` now also records `checks[name]=!!cond` and every stage object lands in an `out` object, printed ONCE at the end as `console.log('[eval] ' + JSON.stringify({ checks, out }))` (keep the human-readable [ok]/[FAIL] lines and RESULT + exit 1 on failures); (e) after boot (before #fqplace) read the card and check `cardOffersPick` (text contains FQ entry's name + row title + 'Ready to fit' - proves the done seed advanced the card to the pick); (f) screenshots 1-place/2-dragged/3-turned/4-saved/cancel into outdir (docs/site_flow is 307c's - mine stay in the tmp dir). **Keep VERBATIM** (all 41 behaviours passed in run128c): the HELPERS evaluate (`_fkvAnchorAt`, `_fkvFitChecks`), the drag-start candidate search (widen the grid a bit: x 900-1150 step 25, y 250-550 step 50, first point clear of the 5 projected markers by 30 px, else fail with info), dragStart's mirror math (unproject -> [u.lng,u.lat] -> merc, absolute from press-down), wheel base = simFit(P.pairs).mpx then wheel(0,-100) -> mpx*exp(0.15), shift+wheel(0,+100) -> rot+1, the pin pair (pane-canvas click at crop centre via P.view, then map click at anchor centre +(25,-15), per-px tolerance from two 2px-apart unprojects), undo, #fsave then poll `!P.active` 120 s, doc read from `<tree>/data/db/platefits/<site>.<plan>.json`, overlay poll on depictions.json 40x1.5 s, the doc-fit (in-page simFit over doc.pairs converted to {u,v,lon,lat} objects vs the FINAL anchor = out.turn.a within mpx 1e-3 / rot 0.01 deg / maxResid<2) and the overlay m_per_px relation `anchor.mpx * fs / f` (fs = imgSize[0]/doc.size[0]; f = min(1, MAX_PX/max crop px in image frame); **read MAX_PX from the source, don't copy it**: Python `re.search(r"^MAX_PX = (\d+)", (ROOT/"pipeline"/"plan_fit.py").read_text(), re.M)` and JS the same on the tree copy - it is pipeline/plan_fit.py:44 today = 2400). **createRequire('/home/agent/tools/shot/probe.mjs')** as in the throwaway: the file need not exist (createRequire resolves from the path's directory; node_modules is there) - part 3's committed script even uses a nonexistent Mac path and passes via NODE_PATH.
- **`_run_place_probe(base, tree, site, plan, dep_file, done_sites, outdir)`** = `_run_probe`'s shape (write PLACE_PROBE to outdir/place_probe.mjs, node with NODE_PATH, timeout=600, parse the `[eval]` line, assert returncode 0). done_sites -> comma csv or 'none'.
- **`test_placement_gestures_and_save_in_the_browser(place_served, tmp_path_factory)`** asserts (each from `data["checks"]`, info from `data["out"]`, plus its own disk reads): boot ok+fitkit; cardOffersPick; seed: opensOnWorks/anchorIsPropose/fivePairsOnMap/gesturesOwnMouse(5 handlers off + dep layer 'none')/hintLive; drag: moves/keepsScaleRot/keepsUv/centrePairTracks/fitAgrees/cornersLand(<0.2 m); wheel: scalesAboutCentre/fitAgrees/hintLive; shift+wheel: turnsOneDegree/keepsScale/cornersLandExactly; pin: addsSixth/refinesAnchor/fiveReemitExact/sixthIsTheClick/fitAgrees; undo: restores/fitAgrees; save: closesPane/stateCleared; **then read the doc back from the temp store in PYTHON**: by:hand, site/plan, model 'similarity', pairs == data.out.pairsBefore (the final re-emitted five, 1dp/7dp), size == data.out.imgSize, crop == row map_box*row.size rounded (n0119: [0.198*3367, 0.168*5050, 0.875*3367, 0.778*5050] rounded), ia/file/book('Allcroft 1908')/label('Fig. 17')/title/cite from the row, src 'book', url/ref null, at ~2026-, EXACT key set = those 16 + 'by'; **overlay from the tree's depictions.json in PYTHON**: kind plan, file plan_<plan>.webp, ink, fit.doc/at/pairs=5, resid_m<1, m_per_px/rot via the MAX_PX relation; newOverlayShowing (vis/sel/src the way applyDep computes); docFitsThePlacedAnchor; cancel run: overlayBack (visible, sel == dep_file, src == want, ground 'relief')/stateCleared; noPageErrors; no reqfail outside '/tiles/' and 'arcgisonline' (scan p.stdout, same filter as part 3). **Hermetic proof**: hash before/after the run: ROOT/data/db/platefits/*, ROOT/web/data/sites/<site>/*, ROOT/web/data/sites.json, ROOT/web/data/review.json, ROOT/data/review/* (the line's full write surface) must be byte-identical - no document in the shared store is ever written by a test.

**Env/state notes:** suite command `.venv/bin/python -m pytest tests/ -q` (our checkout HAS .venv). Last run this session: the 3 part1/part2 tests, 3 passed 20.24 s (post-refactor). Pre-session suite: 73 passed + 1 skipped + 2 failed (the 221 pair in test_review.py - agent c's file, waits on 309). /tmp/fkverify/ is intact (probe.mjs, run128c.log, tree/ with a STALE server - `pgrep -f serve.py` + `readlink /proc/$p/cwd`, kill only cwd=/tmp/fkverify/tree). The throwaway's done-seed used entries[0] directly; the committed version's multi-site seed is the ONE untested mechanism (low risk: part 3 proved single-site seeding). If this next session also runs out of room: commit the section with the test SKIPPED-not-yet-run is NOT allowed - instead split: new subtask 307bc (the part-4 test) after 307bb (fixture+probe+test written), noting it here.

