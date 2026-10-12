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

(2026-10-12, iteration 131, agent a - **orientation + verification only; the part-4 section is still NOT written into tests/test_fit_queue.py.** Working tree carries ONE uncommitted change (the harness keeps it): the module docstring's Part 4 paragraph (added after the part 3 paragraph). Everything else in the repo is as committed (0177e3a). The whole next session = write the section, run it, commit. The complete check-by-check design remains the iteration-130 design in the entry just below this section's predecessor - read the iteration-130 DECISIONS entry, /tmp/fkverify/probe.mjs and tests/test_fit_queue.py part 2 (line_served) before writing.)

**Verified this session (no drift from the iter-130 design, two refinements):**
- Pick = entries[4] oswestry-castle-q20713795, re-confirmed under the full 3-constraint picker (propose AND _line_eligible AND _default_dep_file): entries 0-3 fail the line constraints (iter 130) and, additionally, 1 fort-ancient and 2 marietta have NO drawable default depiction (_default_dep_file -> None), while 3 forthill's default is a plan overlay (plan_b24849959_n0269_1.webp), not a survey sheet. Dep defaults of the first six entries measured: 0 and 4 = six-inch-1st.webp, 1 and 2 = None, 3 and 5 = a plan overlay. Done-seed sites = the four entries before the pick (file order, never pinned).
- **Refinement 1 - openPlan's crop frame (index.html:918): P.crop = map_box * the image's NATURAL size (W = P.img.naturalWidth), not row.size.** The Python-side expected crop must be computed from `out["imgSize"]` (the page's own W/H, which the probe records), mb or [0,0,W,H], JS-style rounding `int(v + 0.5)`; for n0119 natural == row.size == [3367,5050] so it equals the row derivation anyway.
- **Refinement 2 - the throwaway's final honesty checks covered ONLY run 1 (latent bug, fixed in the committed probe):** run-2 lines were tagged '[console2]'/'[pageerror2]'/'[reqfail2]', so the `startsWith('[pageerror]')` / `startsWith('[reqfail]')` filters could never match a run-2 line (run128c passed only because no such lines occurred at all). The committed probe tags BOTH runs without the '2' suffix (the runs are sequential, so no ambiguity), which makes noPageErrors and noReqfailOutsideKnown cover both runs.
- Button IDs exist as used by the probe: #fcancel and #fsave (index.html:904), #fundo (900), #fitcv (243).
- MAX_PX = 2400 at pipeline/plan_fit.py:44; the design's `re.search(r"^MAX_PX = (\d+)", text, re.M)` matches; the probe reads the TREE's copy the same way. Machine date is 2026-10-12, so the doc `at` startswith '2026-'.
- The THREE seed keys in both runs' addInitScript (one object arg, destructured names exactly `{sid, f, d}`): `aw.fitQueue.done` = Object.fromEntries(doneCsv.split(',').filter(Boolean).map(s => [s, '2026-10-12T00:00:00.000Z'])), `aw.depSel` = {sid: f}, `aw.ground` = 'relief' (the page's default, made explicit; select() later re-sets it via setGround in the place flow anyway). aw.depSel is persisted by saveFit (index.html:1147), so run 2's re-seed with the original survey file overwrites run 1's saved choice - that is why run 2's Cancel check sees the survey back. The page's other ls keys (aw.depMode 'ink', aw.plateOpacity, ...) are left at the page's own defaults.
- n0119.jpg verified present in the checkout's data/raw; /home/agent/tools/shot/node_modules present (createRequire + NODE_PATH both work, as part 3 proves).

**The one next step (one session):** append the part-4 section at the END of tests/test_fit_queue.py (after test_card_done_mark_moves_on's last two lines `assert data["card4"]["text"] == c1["text"]` / `assert e1["name"] not in data["card4"]["text"]`, which together are unique in the file; agent c's 309 edits the file's other parts, so this stays in its own banner area): (1) banner comment (the part is 307bb's, self-contained on purpose); (2) `_default_dep_file(root, site)` = the index.html select()/loadDeps port (keep d if kind not in (map,aerial,topo) or (d.year and d.year <= now.year-150); then first kind in (plan,drawing,view) else LAST 'map' kind -> file or None); (3) `_pick_place_site()` = FIRST entry in file order (no sort) with propose AND `_line_eligible(e, _review_items()[e["site"]]) is not None` AND `_default_dep_file(ROOT, site)` a file -> (entry, item, uncovered, depFile) or None; (4) `place_served` fixture, function-scoped, `_headless_or_skip()` FIRST, then line_served's recipe VERBATIM (copy web+server+tools+fit+pipeline, data minus data/raw, the picked row's page copied into the tree's own data/raw, `[sys.executable, "-c", GUARD, "server/serve.py", "--port", "0"]` cwd=tree, blocking reader thread), yield {"base","tree","proc","entry","item","uncovered","depFile","doneSites","out"} with doneSites from a FRESH parse of the tree's fit_queue.json breaking on `e["site"] == entry["site"]`; (5) `PLACE_PROBE` = /tmp/fkverify/probe.mjs transcribed with the iter-130 list (a)-(f) PLUS refinement 2 above, check names exactly: boot, fitkit, cardOffersPick, seed: opensOnWorks / anchorIsPropose / fivePairsOnMap / gesturesOwnMouse / hintLive, drag: moves / keepsScaleRot / keepsUv / centrePairTracks / fitAgrees / cornersLand, wheel: scalesAboutCentre / fitAgrees / hintLive, shift+wheel: turnsOneDegree / keepsScale / cornersLandExactly, pin: addsSixth / refinesAnchor / fiveReemitExact / sixthIsTheClick / fitAgrees, undo: restores / fitAgrees, save: closesPane / stateCleared / newOverlayShowing / docFitsThePlacedAnchor / overlayIsSameSimilarity, cancel: overlayBack / stateCleared, noPageErrors, noReqfailOutsideKnown; `out` carries card1, seed, p0, dragStart, dragOut, wheelBase, wheelOut, turn, pinOut, undoOut, saveStatus, closed, pairsBefore, imgSize, doc, overlay, shown, docFit, cancelOut; one final `console.log('[eval] ' + JSON.stringify({ checks, out }))` + all console/pageerror/reqfail lines + RESULT, exit 1 on any failure (report() also used for the two early bails: boot, no clear drag point); drag-start grid widened to x 900-1150 step 25, y 250-550 step 50; screenshots 1-place/2-dragged/3-turned/4-saved/cancel into the tmp outdir (docs/site_flow is 307c's); (6) `_run_place_probe(base, tree, site, plan, dep_file, done_sites, outdir)` = _run_probe's shape (write outdir/place_probe.mjs, argv `<base> <site> <plan> <dep_file> <tree> <done_csv|none> <out_dir>`, node with NODE_PATH, timeout=600, parse [eval], assert rc 0); (7) `test_placement_gestures_and_save_in_the_browser(place_served, tmp_path_factory)`: hash the checkout write surface first (data/db/platefits/*, web/data/sites/<site>/*, web/data/sites.json, web/data/review.json, data/review/*, via the existing `_h` bytes helper, as a {str(path): bytes} dict), run the probe, assert every check by name (info from data["out"] + p.stdout tail), then the Python-side doc read (by:hand, site/plan, model 'similarity', pairs == out.pairsBefore, size == out.imgSize, crop from refinement 1, ia/file/src 'book'/url/ref null/label/title/book/cite from the row, at startswith '2026-', EXACT 17-key set incl 'by') and the Python-side overlay read (kind 'plan', file plan_<plan>.webp, ink plan_<plan>_ink.webp, fit.doc/at/pairs=5/model 'similarity', resid_m all < 1, m_per_px vs anchor.mpx*fs/f within 1e-3 rel and rot within 0.01 - MAX_PX read from the checkout's pipeline/plan_fit.py, fs = imgSize[0]/doc.size[0], f = min(1, MAX_PX/max crop px in image frame)), then the hermetic re-hash must equal the first. Then run `.venv/bin/python -m pytest tests/test_fit_queue.py -q` (expect ~5-8 min for the whole file: part 2 ~30s, part 3 ~2x45s, part 4 ~2-3 min) and commit `<task>: headless part 4 - ...`.

**Env/state:** our checkout HAS .venv (suite command `.venv/bin/python -m pytest tests/ -q`). Pre-session suite (iter 129): 73 passed + 1 skipped + 2 failed (the 221 pair in test_review.py - agent c's file, waits on 309). /tmp/fkverify/ is intact: probe.mjs (434 lines - the transcription source), run128c.log, tree/ (STALE server possible: `pgrep -f serve.py` + `readlink /proc/$p/cwd`, kill only cwd=/tmp/fkverify/tree). No split this session: the pre-announced 307bc split was already ruled out (iter-130 entry, letter-ordering trap) and the write fits in one session per the iter-130 plan. After part 4 lands: tick boxes 1-3, then box 4 (docs/site_flow.md place-mode section on the lead's 89043b7 version, citing 307c's screenshots when they land), then the done-claim against the 4-failure main baseline (2 card = fixed by me iter 129; 2 review = task 221).

