Status: open
# 307d: The owner's check - two queue sites end to end, then reverted
Depends on: 307c
Touches: tests/, docs/site_flow.md

## Goal
The last box of 307: "Saving still writes 'by': 'hand' and runs the one-site line (305),
and the existing hand fits load and save unchanged. Checked in a real browser on two queue
sites the way the owner uses it (place, move, scale, save, see it on the map), then the
test fits reverted. Tests cover the queue place-check and the save path." The place-check
tests are 309's; this task proves the save path end to end in a real browser on two queue
sites and proves the shared store comes back byte-identical.

## Acceptance criteria
- [ ] A new tests/ file runs the owner's flow in a real headless browser (Chrome, the
      305-part-3 pattern) against the real server on a private copy of the tree (the 305
      part-2 precedent: real data, no network, ephemeral port): on two queue sites (pick
      ones with a recorded bar scale and a site-size-only fallback, and different ground
      where possible - LiDAR relief vs aerial photograph) the test does what the owner
      does: open the queue, place the drawing (the on-map start), move it, scale it,
      save; then verifies the saved doc carries "by": "hand" and the one-site line ran
      (the overlay on the map in the site's depictions, the site square coloured, the
      review item resolved, the queue moved on), and after a page reload the fit loads
      back unchanged (same placement, same overlay).
- [ ] The test fits are reverted before the test ends: the private tree is discarded, and
      the shared store in the repo is proven byte-identical to before the test (the golden
      hand-fit hash check tests/golden/hand_fit_docs.sha256 and test_fit_provenance stay
      green; web/data/fit_queue.json and the review exports untouched).
- [ ] docs/site_flow.md: the verification section (what was checked, on which two sites,
      which way, and the screenshots), closing the parent's last box.

## Notes
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-13, iteration 241, agent a - SECOND session; investigation only again: re-ran the pick
scan (full run to completion) and read every piece of machinery the test must mirror; NO files
changed, NO tests run. 307d is unblocked (307c done, 309 done). Task 235 (open, mine via 221,
`Depends on: 306e, 307d`, `Touches: tests/test_fit_queue.py`) still waits on me via the broad
`tests/` gate - my test is a NEW file in tests/, never tests/test_fit_queue.py. Next session:
write tests/test_owner_check.py, run it, then the docs section.)

**State:** all boxes unticked; the test file does not exist yet. Suite baseline (driver notes,
re-run before claiming anything): 155 passed / 1 skipped / 1 failed; the ONE red is 235's
test_placement_gestures_and_save_in_the_browser (its `_pick_place` lands on marietta, whose only
dep is a 1904 USGS topo the page's `loadDeps`/`surveyOldEnough` filter drops -> `dep: null`).
My test must NOT depend on 235's fix: it mirrors the page's dep-filter rules itself.

**Template (307bb part 4, in tests/test_fit_queue.py - read it whole first):** `place_served`
L1673 = the 305 part-2 `line_served` L813 recipe (conftest.copy_web(tree, real={site}) + copy
server/tools/fit/pipeline + data minus data/raw and .npy/.npz; materialise the picked book page
into the tree's own data/raw/books/<ia>/full/; `python -c GUARD server/serve.py --port 0` - GUARD
L102 kills every socket in the server process; reader thread; 90 s poll on "Ancient Works on
(\S+)") plus the headless-Chrome probe `PLACE_PROBE` L1289 (node; `createRequire(process.env
.NODE_PATH + '/')` -> playwright-core; CHROME /opt/google/chrome/chrome; NODE_MODULES
/home/agent/tools/shot/node_modules; `_headless_or_skip` L1130). The probe seeds localStorage
`aw.fitQueue.done` via addInitScript -> boot-poll S.ready/FQ -> read #fqcard -> #fqplace -> poll
P.placed -> seed checks (anchor == propose's last pair to 1e-9, 5 pairs/markers, dep layer
hidden) -> inject HELPERS (_fkvAnchorAt/_fkvFitChecks) -> drag (mouse 30+20 px; expected anchor
= anchor-at-down + pointer Mercator delta, the fitkit _fkOnMove math) -> wheel -100 (wheelBase
= simFit(P.pairs).mpx first - the ABSORBED fit; mpx *= exp(0.15)) -> shift+wheel +100 (rot +=
1 deg) -> #fsave -> poll the TREE's depictions.json for the overlay + the page's dep layer ->
page2 cancel check. `_write_surface()` L1723 (hash of data/db/platefits/*.json +
data/review/*.json + web/data/sites.json + web/data/review.json) is the revert proof -
EXTEND it with BOTH picked sites' web/data/sites/<site>/ files and web/data/fit_queue.json.

**What 307d adds beyond 307bb part 4 (the parent's box 6):** TWO sites (307bb did one
bar-scale site); after save, the one-site line end to end: (a) overlay in the tree's
depictions.json; (b) the site's SQUARE COLOURED (sites.json entry gains drawings/score via
build_site.set_drawings; page marker class from score via TIERS); (c) review item resolved
(tree data/review/<item>.json gains `resolved: {doc, at}`; leaves web/data/review.json's open
list); (d) the queue moved on in-page (FQ.done[site] in localStorage aw.fitQueue.done set by
the fitqueue.js saveFit wrapper; the card re-patches to the NEXT pending entry). Then a PAGE
RELOAD in the SAME context (localStorage persists) and a revert proof (write-surface hash,
BOTH sites' dirs; tests/golden/hand_fit_docs.sha256 + test_fit_provenance stay green because
nothing in the checkout store moved; web/data/fit_queue.json is never written by the page or
the line - the line writes review.json only in the PRIVATE tree).

**Picks RE-VERIFIED this session (scan re-run to completion; queue 241 entries, unchanged
`at` 2026-10-13T14:34:09 - the file did not move in the merge, but the eligible SET shifted vs
the 240 notes, now 25):** [28] fort-ancient (ratio), [29] marietta (ratio - the 235 red),
[38] oswestry (bar), [45] devil-s-dyke (picture_size), [46] richard-s-castle, [47]
mount-caburn, [48] bramber, [52] gurnard-s-head, [53] ardotalia, [55] totternhoe (bar rot
53.1), [59] pickering (bar), [62] silbury-hill, [63] west-kennet, [64] bokerley, [65]
stonehenge, [66] desborough (picture_size; all England/EA, six-inch auto dep), [70]
plum-bayou, [100] angel-mounds (bar), [102] etowah (bar), [104] hodgen, [105] mound-cemetery,
[204] pyramid-mound (the USGS-credit ones are all topo-only or depless - no page-showable
auto dep), [185] maumbury-rings (bar). The 240-note Scottish picture_size sites (maeshowe,
norham, stones-of-stenness) are GONE (gained docs in a merge). All eligibles `lidar: None`
(relief ground); NO `lidar: False` (aerial-only) site is line-eligible -> the task's
"different ground (LiDAR relief vs aerial photograph)" is NOT achievable this session; both
picks sit on LiDAR relief - say so plainly in the docs section.
- A (bar scale) = [38] oswestry-castle-q20713795 / row earthworkenglan01allcgoog_n0119_1
  (bar "0 100 200 300 Feet", mpx 0.1646, rot 0, uncovered=0, auto dep six-inch-1st.webp 1842
  kind map, no drawing dep, lidar=None, credit Environment Agency).
- B (site-size fallback) = [45] devil-s-dyke-q3307343 / row earthworkenglan01allcgoog_n0662_1
  (scale_source 'picture_size', coarse, mpx 0.7201, rot 0, uncovered=0, same six-inch auto
  dep, same EA credit).
- PICKER (derived, never pinned): eligible = 307bb `_line_eligible` (book row ia/file, page in
  the CHECKOUT's data/raw/books/<ia>/full/, unresolved item carrying the row with >=3 pairs, no
  platefits docs for the site) AND a page-showable auto dep = first drawing-kind or last map-kind
  after the page's surveyOldEnough filter (drop kind in {map,aerial,topo} unless year <=
  now-150; the 1842 six-inch passes) AND no pre-existing drawing-kind dep. A = first eligible
  with propose.scale_source=='bar'; B = first eligible with 'picture_size' AND lidar_credit !=
  A's, FALLING BACK to the first qualifying when none differ - B is that fallback today (no
  USGS-credit eligible has a showable dep). Done seed for a site's run = sites of ALL queue
  entries BEFORE it in file order (parse the TREE's own web/data/fit_queue.json): for A
  entries 0..37, for B 0..44. Both uncovered=0 -> the line runs sync+entry+review only (no
  batch, no model, offline-safe).
- SCAN SCRIPT CAVEATS (throwaway /tmp/aw307d/scan_picks.py, fixed this session): its
  line_eligible returns a failure STRING / a list on pass - filter with `isinstance(li, list)`
  (a `None` check silently passes everything); guard `page_deps(...) or {...}` (None when no
  depictions.json) before subscripting.

**Mechanics verified this session (read the code; line refs current on this branch):**
- PUT platefits (server/serve.py ~L199-222): stamps `data["by"]="hand"` (~L209), writes the doc
  (indent=1), `after_write("platefits","line",site)` -> worker thread `_fit_line` (L240) ->
  `site_done.main([site])` in-process, sockets dead; prints `one-site line for <site>:
  finished (exit 0)`. For both picks (uncovered=0): `_fit` prints "no batch run needed";
  `_sync` builds the one hand overlay (plan_fit.build: plan_<plan>.webp + _ink.webp,
  depictions.json entry kind=plan, fit {doc,at,pairs,m_per_px,rot_deg,resid_m}, source line
  "Placed by hand"; is_done skips if current); `_entry` = build_site.set_drawings (drawings,
  score, oldest, overlays into sites.json); `_review` = fit/review.export(root, site_id):
  records `resolved: {doc, at: <doc.at>}` write-once into the item file and republishes
  web/data/review.json over the whole queue (the site leaves the open list). Line ~23 s;
  allow 180 s (the 305 test's number).
- Page save (web/index.html `saveFit` ~L1150): builds the doc (site, plan, ia, file, crop =
  rounded P.crop, model similarity, src book, url, ref, size = [naturalW, naturalH], pairs =
  the 5 placed pairs rounded u/v 1dp lon/lat 7dp, label/title/book/cite, at = ISO) -> PUT ->
  status "Saved. Making the overlay…" -> polls `data/sites/<site>/depictions.json?t=` 60x1.5 s
  for an entry with fit.at === at -> then S.depSel[site] = the overlay file (lsSet
  aw.depSel), re-fetches sites.json and copies drawings/score/oldest/overlays into the site,
  marker class = `marker ${tierOf(s)}` (TIERS = [[2.5,'t4'],[1.6,'t3'],[1.2,'t2'],[0.01,'t1']],
  else 'plain' - index.html L475-476; score = build_site.score: per overlay (age/100)/
  (1+(err/100)^2) x kind, site = best + 0.25*rest, rounded 2dp; a hand plan's err = rms of its
  fit resid_m) -> removes the dep layer/source -> endFit() (the fitkit wrapper re-applies the
  dep) -> fitqueue.js `_fqSaveFit` (L117-134) GETs the doc and, on 200, sets FQ.done[site] =
  ISO in localStorage aw.fitQueue.done and fqPatch() -> the card moves to the next pending
  entry (or disappears at the tail). fqLoad self-heals FQ.done against the file on load.
- RELOAD (same context; aw.depSel + aw.fitQueue.done persist): boot reads hash `#<site>`
  (index.html ~L1704) -> `select(id)` UNCONDITIONALLY resets S.ground = 'imagery',
  plateMode/depMode = 'ink' (L828: "every site opens on the aerial photograph") -> loadDeps
  fetches the new depictions.json -> `if (!(s.id in S.depSel))` is FALSE (depSel persisted)
  -> applyDep shows layer `dep-<site>` visible with source `data/sites/<site>/plan_<plan>
  _ink.webp` (depMode 'ink'). So the reload check: S.ground === 'imagery' (the page contract,
  NOT 'relief'), dep layer visible with that source URL, S.depSel[site] === the overlay file,
  marker class === tierOf(the tree's new sites.json score), card still moved on. The overlay's
  fit record IS the placement (the webp is a static file built from the doc's pairs): check
  m_per_px/rot_deg/resid against a stdlib simFit of doc.pairs (R = 6378137 merc, k = cos of
  the FIRST pair's lat) within 1e-3 mpx / 0.01 deg of the placed anchor, exactly as 307bb did;
  m_per_px = anchor.mpx * fs / f_scale with fs = naturalW/doc.size[0] and f_scale =
  min(1, MAX_PX / max crop px) - read MAX_PX by regex from the tree's pipeline/plan_fit.py,
  never hard-code.

**The exact next step (one session):**
1. Re-run the pick scan once (cheap; the population drifts under agent c's merges) and confirm
   A/B still qualify before writing.
2. Write tests/test_owner_check.py (new file; header comment per CODEMAP; import
   conftest.copy_web + get/get_json; copy GUARD/CHROME/NODE_MODULES/_headless_or_skip from
   test_fit_queue.py - do NOT import from that file, 235 owns it). One module-scoped fixture
   `owner_served` = the line_served-style tree with BOTH picked pages materialised and ONE
   server; yields per site: entry, done seed, item file name, depFile, sites.json entry
   before. ONE node probe parameterised (site, plan, doneJson, outdir): card read (assert it
   names THE pick) -> #fqplace -> seed checks (307bb's) -> drag -> wheel -> shift+wheel ->
   #fsave -> in-page line checks (overlay in tree depictions.json; page's dep layer now shows
   the overlay: visible, src the ink file, S.depSel the overlay file; tree sites.json new
   drawings/score; marker class === tierOf; tree item resolved {doc, at === doc.at}; tree
   review.json no longer lists the site; FQ.done[site] in localStorage; card now names the
   next pending entry, derived in-page from FQ.entries minus done/skipped) -> page.reload()
   -> boot-poll -> reload checks (the RELOAD bullet above) -> screenshots (card, place,
   after-save, after-reland) -> RESULT PASS/FAIL + the placed anchor in the [eval] out.
   Two test functions (A first, then B, shared fixture); each asserts: doc (by hand; 5 pairs
   === the page's final pairs; size === natural image size; crop === map_box x natural size
   rounded), the stdlib simFit check, the overlay fit fields, the item/review/sites.json checks
   read from the TREE, and the write-surface hash equal (BOTH sites' web dirs + store + review
   exports + fit_queue.json + web/data/sites.json + web/data/review.json).
3. Run `.venv/bin/python -m pytest tests/test_owner_check.py -q` (~5-10 min: two browser runs +
   two lines). If a check fails: commit the failing test AS-IS (the lead's 307bb rule), name
   the check + the probe's out dump in DECISIONS, fix next session. Then run the full suite once
   to confirm only 235's red remains.
4. docs/site_flow.md: append a section (after the 308 section): what was checked, the two
   derived sites and why (the picker rules; both LiDAR relief - state plainly that no
   aerial-photograph ground was available this session and why), the line's four effects, the
   reload, the revert proof, screenshots copied from the probe's outdir into docs/site_flow/.
   Then tick the boxes, DECISIONS entry, commit.

**Do not touch:** fit/surveyfit.py or task 304 (agent c); tests/test_fit_queue.py (235's file);
tests/conftest.py (ask for shared fixtures in DECISIONS instead); any data file in the checkout
(the test writes only into its private tree).
