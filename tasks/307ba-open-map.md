Status: in-progress
# 307ba: Open the map - the queue carries the proposal, and place mode opens ON the works
Depends on: 307a
Touches: fit/propose.py, tools/fit_queue.py, web/fitkit.js, web/index.html, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
Parent 307 (and 307b) boxes 1-2, as renumbered there. The "Ready to fit" queue file carries a
starting placement for each entry (the proposal fit/propose.py already computes: the anchor
mapping the picture's panel centre onto the site at the recorded scale and rotation, re-emitted
as 3-5 page-px -> lon/lat pairs), and opening a queue site with a proposal puts the drawing ON
the map before any clicking: the map flies to the site's own box, the site's earlier overlays
are hidden, the ink appears at the anchor, and closing brings everything back exactly as it was.
A site or plan without a proposal opens exactly as today (the three-point flow, byte-identical -
305 part 3 pins it). The owner's words: "when I go to place the plan onto the map it already
needs to be overlaid onto the map ... the overlay that's already there doesn't disappear from
the map ... As soon as you go into that place mode the already placed overlay needs to go."

## Acceptance criteria
- [x] The queue file carries the proposal: every entry whose best row admits one gets
      propose: {pairs, scale_m_px, rot_deg, scale_source, coarse, note} computed by
      fit/propose.propose_for (bar scale where recorded, ratio at the book's ppi, the
      site-size fallback, the north arrow where trustworthy). A row the proposal cannot
      anchor (no size, no size_m, no stage-B row) gets no propose, and the page falls back
      to the existing three-point flow for it. tools/fit_queue.py stays stdlib-only
      (fit/propose.py is); the committed web/data/fit_queue.json is regenerated (all 117
      current entries anchor: 20 bar, 4 ratio, 93 picture_size).
- [x] fit/propose.py gains an optional root (default: this checkout): its data loaders read
      from it and its cache is keyed by it, so the generator and the tests run it against a
      temp tree; every existing 2-arg caller (batch_us, inkfit, the tests) and
      tests/test_propose.py's golden file stay green unchanged.
- [x] tests/test_fit_queue.py part 1: the synthetic tree gains stage-B index rows and
      site sizes covering every path (a bar + trustworthy north arrow, a ratio without a
      recorded ppi -> the site-size fallback, a no-scale site without size_m -> no propose,
      a sizeless row -> no propose, an item candidate with no index row -> no propose);
      the propose field is checked against the same propose_for called on the tree, plus
      hand-pinned constants. The real test derives per-entry admissibility (never a pinned
      count) and checks presence/equality/key order. Parts 2-3 are untouched and stay green.
- [ ] Opening a queue site with a proposal (the card's "Place the drawing", or the site
      panel's "Place an old plan" when the site's queued plan is the one picked): the map
      flies to the site's box (its four corners) centred, before the drawing appears; while
      place mode is open, the site's earlier overlay (the dep-* fitted drawing or survey
      sheet applyDep was showing) is hidden; on close (back button, Cancel, or saving) it
      comes back exactly as it was (same depiction selected, same ground). web/fitkit.js is
      a new extension in the fitqueue/review pattern (loads after them, wraps openPlan last
      in the chain and endFit, injects its own <style>, _fk-prefixed saved names);
      web/index.html changes by the one script tag alone; web/fitqueue.js stays
      byte-identical.
- [ ] docs/site_flow.md's "Ready to fit" section: the entry's new propose field (what it is,
      where the anchor comes from, the fail-open to the three-point flow). The full place-mode
      section (gestures, save, screenshots) is 307bb/307c's.

## Notes
- The full box-1 design and the page-side design sketch (anchor model, wrap points, hide/
  restore, the no-propose byte-identity rule) are in the parent 307b's ## Hand-over and the
  2026-10-12 307b DECISIONS entry (iteration 110) - implement from there, they are precise.
- Agent c's 309 works on tools/fit_queue.py / web/data/fit_queue.json / tests/test_fit_queue.py
  in its own branch (the place check): expect a merge of its build() change; keep the propose
  wiring localized (one helper, one key per entry, docstrings) so the merge stays trivial.
- The stage-B row shape: data/books/index.jsonl (scale_text, blank_boxes[{kind:"scale_bar",
  box}], north_angle_deg, north_arrow, map_box, full_size). fit/ has no __init__.py; import
  via sys.path.insert(0, str(ROOT / "fit")) like tools/site_done.py:43.
- Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-12, iteration 114, agent a - box 4 WRITTEN, not yet verified: web/fitkit.js is a
NEW file (uncommitted - the context limit stopped the session; the harness saved it) and
web/index.html gained its one script tag. The re-emit math is numerically verified. Next:
run the /tmp smoke probe, then the full suite, then box 5 docs.)

**State of the branch.** Boxes 1-3 committed (cbb36c8). Uncommitted this session:
- web/fitkit.js (new, ~120 lines): wraps openPlan LAST in the chain (page->review->
  fitkit) and endFit (the page original - review/fitqueue don't wrap it); `_fk`-prefixed
  names only. Activation (openPlan wrapper, after the inner chain returns): P.active &&
  P.site && P.plan && P.img (the GATE: no picture -> ordinary flow, byte-identical) AND
  an FQ entry with site === P.site.id && best.plan === P.plan.id && propose. On
  activate: (1) map.fitBounds to the site's corners FIRST (padding left 390 /
  narrow bottom-sheet, duration 900, essential); (2) hide `dep-<site.id>` (visibility
  'none' if present); (3) P.placed=true, P.anchor={u0,v0,lon,lat,mpx,rot} from the LAST
  propose pair (the centre) scaled by _fkFrameScale() (natural/recorded size; 1 for all
  117 current entries; 0 on a >2% non-uniform resample -> fall back), P.anchorStack=[];
  (4) re-emit 5 pairs (4 panel corners from map_box*recordedSize*scale + centre; the
  exact port of propose.py's _anchor_pairs: merc=a*(w-w0)+z0, a=(mpx/cos(lat))*e^{i*rot},
  u/v 1dp, lon/lat 7dp) into P.pairs with the page's own numbered draggable markers;
  refit(). endFit wrapper: after the inner endFit, if wasPlaced: applyDep(site) (the
  exact restore: S.depSel/depMode/depOpacity/ground never touched) and clear
  placed/anchor/anchorStack. No <style> block on purpose (box 4 adds zero visible UI -
  the page's own copy already works; 307bb adds the block if its gestures need one -
  recorded in DECISIONS). No fetches (the card test allows no reqfail outside /tiles/).
- web/index.html: exactly one line added - `<script src="fitkit.js"></script>` after
  fitqueue.js (~line 1708). web/fitqueue.js untouched.

**Verified numerically this session (/tmp/fkverify.js, throwaway):** _fkReemit against
the queue file's real propose output: the centre pair re-emits IDENTICALLY (it is the
anchor origin); corner pairs drift <=0.12 m = exactly the 4-dp scale rounding in the
queue file applied over ~3000 px (expected; sub-decimeter is the seed's design
precision). Corner frame math hand-checked (Forthill 170.64->170.6 etc.). Cross-checks:
all 117 queue entries have plans.size == index.full_size AND plans.map_box ==
index.map_box (tools/export_plans.py:78 copies both from the index row) and the served
image's natural size == recorded size -> the propose frame IS the page frame (s=1).
test_review.py checked: its probes never call openPlan (the save test is an HTTP PUT;
PROBE_KEYING's endFit hits the wrapper with placed=false, a no-op) -> fitkit cannot
fire there.

**NEXT (exact):**
1. Smoke probe (throwaway, NOT a committed test - the committed headless test is
   307bb's part 4). Scratch tree /tmp/fkscratch exists (web/server/data minus raw +
   Devil's Dyke's book page earthworkenglan01allcgoog/full/n0686.jpg). Start
   `cd /tmp/fkscratch && python3 server/serve.py --port 0 &` (read the port from the
   "Ancient Works on ..." line), take the map depiction's `file` from
   web/data/sites/devil-s-dyke-q3307343/depictions.json (a 'map' entry - a fresh
   browser auto-selects nothing there: maps are not in DRAWING and the site has
   LiDAR), then `NODE_PATH=/home/agent/tools/shot/node_modules node /tmp/fkprobe.mjs
   <base> /tmp/fkout <depFile>`. The probe seeds aw.depSel for Devil's Dyke, clicks
   #fqplace, waits P.placed&&P.img, then asserts: anchor.mpx===propose.scale_m_px,
   anchor.centre===propose's last pair, maxPairDriftM small, map.project(site centre)
   ~ the padded-viewport centre ((390+width-20)/2, height/2), getBounds() contains the
   site corners, the dep layer HIDDEN while placed, fsave enabled; then clicks #fcancel
   and asserts placed=false, anchor=null, dep layer VISIBLE again, depSel/ground
   unchanged. If the depLayerState() helper returns null, simplify it: the evaluate
   callback may reference `map` directly (a page global lexical binding). Look at the
   screenshots in /tmp/fkout to see the drawing sit ON the site's box. Kill the server
   after.
2. Full suite `.venv/bin/python -m pytest -q` (baseline 73 passed + 1 skipped). The 305
   part-3 card tests pin byte-identity: their served tree 404s the scan so P.img stays
   null and fitkit never activates; test_review must stay green. Confirm
   `git diff web/fitqueue.js` empty and `git diff web/index.html` = the one tag.
3. Box 5 (docs): docs/site_flow.md's "Ready to fit" section - add what the entry's new
   `propose` field is (the starting placement: the panel-centre anchor at the recorded
   scale/rotation - the ladder bar > ratio-at-ppi > site-size, the north arrow where
   trustworthy - re-emitted as 3-5 page-px->lon/lat pairs), where it comes from
   (data/books/index.jsonl stage-B fields via fit/propose.propose_for), and the
   fail-open (a row that cannot anchor gets no key; the page does the ordinary
   three-point flow). Do NOT write the full place-mode section (gestures/save/
   screenshots) - that is 307bb/307c's. Agent c's 309 also edits docs/site_flow.md
   (its own section) - keep my addition local to the "Ready to fit" section.
4. Commit: one commit for fitkit.js + index.html once verified ("307ba: box 4 - place
   mode opens on the works ..."), box 5 docs with it or separately, then tick boxes
   4-5 and set the task done when the suite is green.

**Watch first:** agent c's 309 (still unmerged at iteration 114; main tip cf29be2) -
it rewrites tools/fit_queue.py build(), web/data/fit_queue.json and
tests/test_fit_queue.py. If it merges before my commit, the propose wiring is isolated
in _entry_propose so any conflict is small; I do NOT need to re-run the generator
(boxes 4-5 don't touch the generator output) unless the merge changes entry shapes.
No git merge/rebase/reset unless the prompt asks.

**Re-read:** web/fitkit.js (mine, uncommitted - its header comment is the design doc);
web/index.html ~832 endFit, ~902 openPlan, ~1000-1150 (startFit/makeInk/simFit/refit/
saveFit/pin flow), 1706-1710 (the three script tags); web/review.js's wrapper block
(bottom) and web/fitqueue.js (the pattern it imitates); tests/test_fit_queue.py part 3
(~716-967, the byte-identity pin); the parent 307b hand-over's page-side design sketch
(authoritative); docs/site_flow.md "Ready to fit" section (box 5).
