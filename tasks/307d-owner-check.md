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

(2026-10-13, iteration 240, agent a - FIRST session on 307d; investigation only: no files
changed, no tests run this session. 307d is unblocked (307c done, 309 done). Task 235 (open,
owner agent a, `Depends on: 306e, 307d`, `Touches: tests/test_fit_queue.py`) waits on me via
the broad `tests/` gate - so my test is a NEW file in tests/, never test_fit_queue.py.)

**State:** all boxes unticked; the test file does not exist yet. Suite baseline from the
driver's notes (re-run the suite before claiming anything): 155 passed / 1 skipped / 1 failed;
the ONE red is `tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser`
(235's: its `_pick_place` now lands on `marietta`, whose only depiction is a 1904 USGS topo the
page's `loadDeps`/`surveyOldEnough` filter drops -> `dep: null` at the seed check). My new test
must NOT depend on 235's fix: my own picker mirrors the page's filter rules directly (the rules
are in 235's task text; mirror in stdlib, a few lines each).

**Template (307bb part 4, already committed in tests/test_fit_queue.py - read it whole first):**
`place_served` = the 305 part-2 `line_served` recipe (copy web/ + server/tools/fit/pipeline +
data minus data/raw and .npy/.npz into tmp; materialise the picked book page into the tree's own
data/raw/books/<ia>/full/; `sys.executable -c GUARD server/serve.py --port 0`, sockets dead in
the server process, ephemeral port; reader thread; 90s startup poll on `Ancient Works on (\S+)`)
plus the headless-Chrome probe (Chrome /opt/google/chrome/chrome; playwright-core under
/home/agent/tools/shot/node_modules via NODE_PATH; the `createRequire` line to copy is in the
part-3 PROBE_SCRIPT ~L1024). Probe: addInitScript seeds localStorage `aw.fitQueue.done` (card
skips earlier entries), `aw.depSel`, `aw.ground` -> boot-poll S.ready/FQ -> read #fqcard -> click
#fqplace -> poll P.placed -> seed checks (anchor == propose's last pair to 1e-9, 5 pairs/markers,
dep layer hidden, bounds contain the site's corners) -> drag/wheel/shift+wheel -> #fsave -> poll
the TREE's depictions.json for the overlay + the page's dep layer. Test body asserts on the
tree: doc (exact 17 keys, by: hand, pairs == placed five, crop == map_box x natural size
rounded), stdlib `_simfit` port of index.html:983 (R=6378137, k = cos of FIRST pair's lat)
within 1e-3 mpx / 0.01 deg of the placed anchor, overlay fit fields (m_per_px = anchor.mpx*fs/
f_scale; fs = img_w/doc.size[0]; f_scale = min(1, MAX_PX/max(crop px)); MAX_PX read by regex
from pipeline/plan_fit.py - do not hard-code), and a before/after hash of the checkout write
surface (data/db/platefits/*.json, data/review/*.json, web/data/sites.json, web/data/review.json,
the picked site's web dir).

**What 307d adds beyond 307bb part 4 (the parent's box 6):**
- TWO sites per the picker rules below (307bb did one bar-scale site).
- After save, verify the one-site line end to end: (a) overlay in the tree's depictions.json;
(b) the site's SQUARE COLOURED: web/data/sites.json entry gains drawings/overlays/score
(build_site.set_drawings; the page's marker class comes from score via TIERS t4>=2.5 t3>=1.6
t2>=1.2 t1>=0.01 else plain - index.html ~L475, marker class refreshed ~L1169-1172 after the
depictions poll); (c) review item resolved: the tree's data/review/<item>.json gains
`resolved: {doc, at}` (fit/review.export scoped to the site) and the item leaves the open list
in web/data/review.json; (d) THE QUEUE MOVED ON: in-page, FQ.done[site] is set in localStorage
aw.fitQueue.done by _fqSaveFit (web/fitqueue.js) and the card re-patches to the NEXT pending
site (or disappears at the tail).
- Then a PAGE RELOAD (page.reload() in the SAME context - localStorage persists: aw.fitQueue.done
and aw.depSel): the fit loads back unchanged - the new overlay is the selected dep (depSel), the
dep layer visible with its source, and the overlay's fit fields agree with the saved doc's anchor
(same placement: the warped image is a static file built from the doc's pairs, so the fit record
IS the placement).
- Revert: the private tree is discarded by fixture teardown; prove the shared store byte-identical
(the write-surface hash - include BOTH picked sites' dirs); tests/golden/hand_fit_docs.sha256 and
test_fit_provenance stay green because nothing in the checkout store moved; web/data/fit_queue.json
and the review exports are never written by the page or the line (the line writes review.json only
in the PRIVATE tree).

**Ground truth measured this session (re-verify with a fresh scan; the throwaway
/tmp/aw307d/scan_picks.py is a read-only mirror of the test's gates - WARNING: its
line_eligible returns a STRING on failure, a list on pass: filter with `isinstance(li, list)`;
a `None` check silently passes everything):**
- The queue is 241 entries (2026-10-13T14:34Z). The EU batch (agent c's 203b) filled the top with
  commons rows (c_..., no ia/file -> NOT line-eligible). The line-eligible entries (book row with
  a local page, unresolved item carrying the row with >=3 pairs, no docs yet) are ALL
  `lidar: None` (relief ground). There is NO line-eligible site with `lidar: False` today (every
  aerial-only queue site is a commons-row candidate the line cannot read locally) -> the task
  text's "different ground (LiDAR relief vs aerial photograph)" is NOT achievable this session;
  both picks sit on LiDAR relief. Document that plainly in docs/site_flow.md.
- Verified picks (file order): A (bar scale) = [38] oswestry-castle-q20713795, row
  earthworkenglan01allcgoog_n0119_1 (bar "0 100 200 300 Feet", mpx 0.1646, rot 0, uncovered=0,
  auto dep six-inch-1st.webp 1842, no drawing dep, England/Environment Agency LiDAR). B
  (site-size fallback: scale_source 'picture_size', coarse true) = [45] devil-s-dyke-q3307343,
  row earthworkenglan01allcgoog_n0662_1 ("SWEALD", mpx 0.7201, rot 0, uncovered=0,
  six-inch-1st.webp, England/EA). Both uncovered=0 -> the line runs sync+entry+review only, no
  batch run, no model. Other eligibles: [46] richard-s-castle, [47] mount-caburn, [48] bramber,
  [55] totternhoe (bar, rot 53.1); [52] gurnard-s-head, [53] ardotalia, [62] silbury-hill
  (rot -51.4), [63] west-kennet, [64] bokerley, [66] desborough (picture_size, all England/EA);
  [163] maeshowe, [170] norham-castle, [202] stones-of-stenness (picture_size, auto dep
  scot-6-first.webp - Scotland, a different ground source; my scan crashed at [163] on
  row.ia being None - at least one of these may be a commons row; verify ia/file/local, item
  candidates and uncovered before using them).
- SUGGESTED PICKER (derived, never pinned): A = first eligible entry (file order) with
  propose.scale_source=='bar', a page-showable auto dep, no pre-existing drawing dep; B = first
  eligible with scale_source=='picture_size' and same dep rules AND whose sites.json
  lidar_credit differs from A's (falls back to the first qualifying entry when none differ).
  The done seed for each run = the sites of the queue entries BEFORE the pick in file order
  (derived from a fresh parse of the TREE's own web/data/fit_queue.json, the 307bb way) so the
card offers the pick; after save the card moves on to the next entry after the pick.
- One-site line mechanics: server/serve.py after_write -> _fit_line in a worker thread reading
  the TREE's files (sockets dead in the server): tools/site_done.py `_fit` (batch only for
  uncovered rows: matchfit.reachable() false offline; batch_us.run_sites(model=None) is offline -
  uncovered rows get "no model answer" item entries, no images; none here), `_sync` (plan_fit.build
  for by:hand docs, no fabrication check), `_entry` (build_site.set_drawings), `_review`
  (fit/review.export scoped: resolved {doc,at} into the item file, republishes review.json).
  The line measures ~23 s; the 305 test allows 180 s.

**The exact next step (one session):**
1. Re-run the pick scan to re-verify A/B still qualify (population drifts: agent c's 203b and the
   212b/306 family merge into main; a site gaining a doc in a merge drops out of eligibility -
   the picker's doc scan handles that automatically).
2. Write tests/test_owner_check.py (new file; header comment per CODEMAP; may import conftest's
   copy_web): the 307bb part-4 structure with the 307d additions - one module-scoped fixture
   (the line_served-style tree with BOTH picked book pages materialised, one server; yields
   per-site dicts: entry, done seed, depFile, item file name, sites.json before-state), two test
   functions (site A, site B), each: headless Chrome runs the owner's flow (place -> drag ->
   wheel-scale -> save -> line checks (doc by:hand, overlay, square coloured, item resolved,
   card moved on) -> page.reload() -> fit loads back unchanged); a write-surface hash (BOTH sites'
   dirs + store + review exports + fit_queue.json) asserted equal after each test; skip via the
   307bb _headless_or_skip pattern when Chrome is absent.
3. Run `.venv/bin/python -m pytest tests/test_owner_check.py -q` (expect ~5-10 min: two full
   browser runs + two one-site lines). If a check fails: commit the failing test AS-IS (the
   lead's 307bb rule) and fix next session; name the failing check + the probe's out dump in
   the DECISIONS entry.
4. docs/site_flow.md: the verification section (what was checked, the two derived sites and why,
   the line's four effects, the reload, the revert proof, screenshots copied from the probe's
   outdir into docs/site_flow/ as the other sections do; state plainly that no aerial-photograph
   ground was available this session and why). Then tick the boxes, DECISIONS entry, commit.

**Do not touch:** fit/surveyfit.py or task 304 (agent c); tests/test_fit_queue.py (235's file);
any data file in the checkout (the test writes only into its private tree).
