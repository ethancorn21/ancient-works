Status: split
# 307b: Place mode on the map - the drawing starts on the ground, and moves by hand
Depends on: 307a
Touches: tools/fit_queue.py, web/fitkit.js, web/index.html, web/fitqueue.js, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
The owner could not fit by clicking three points: "when I go to place the plan onto the map
it already needs to be overlaid onto the map ... I can move it around, I can scale it around
... then pinpoint this exact spot to here". So place mode opens ON the works: the map flies
to the site's own box (the built site's extent) centred and zoomed so the works fill the
view, before the drawing appears; every overlay already on the site (the fitted drawings and
the survey sheets - whatever the site was showing) is hidden while place mode is open and
comes back exactly as it was when it closes. The drawing itself is on the map from the first
frame: the page's ink (the existing fit-prev preview: survey-red on transparent paper)
mapped by the anchor fit/propose.py already computes - sized from the picture's scale bar
where it has one, otherwise from the site's known size, north-up (or by its north arrow) -
at the opacity slider's value. The owner moves it by dragging, scales and rotates it (a
handle, modifier+drag or the wheel), and saves straight from that placement. Saving writes
the same page-px pairs the three-point flow writes (the placement re-emitted as pairs), so
plan_fit.py, the gate, the one-site line and every existing document keep working unchanged.
Pinning exact spots (a point on the drawing to a point on the ground) stays available on
top as a refinement: new points refine the anchor and re-draw it. Parent 307 boxes 2-4.

## Acceptance criteria
- [x] The queue file carries the proposal: every entry whose best row admits one gets
      propose: {pairs, scale_m_px, rot_deg, scale_source, coarse, note} computed by
      fit/propose.propose_for (bar scale where recorded, ratio at the book's ppi, the
      site-size fallback, the north arrow where trustworthy). A row the proposal cannot
      anchor (no size, no size_m) gets no propose, and the page falls back to the existing
      three-point flow for it. tools/fit_queue.py stays stdlib-only (fit/propose.py is).
- [x] Opening a queue site with a proposal (the card's "Place the drawing", or the site
      panel's "Place an old plan" when the site's queued plan is the one picked): the map
      flies to the site's box (its four corners) centred, before the drawing appears;
      while place mode is open, the site's earlier overlays (the dep-* fitted drawings and
      survey sheets applyDep was showing) are hidden; on close (back button, Cancel, or
      saving) they come back exactly as they were (same depiction selected, same ground).
      A site or plan without a proposal opens exactly as today (the three-point flow).
- [x] The drawing is on the map from the first frame and is the thing being manipulated:
      drag moves it, a handle / modifier+drag / the wheel scales it, a handle /
      shift+wheel (or the equivalent gesture) rotates it, all at the opacity slider's
      value; the page's panel shows the live scale (m per page pixel) and the rotation.
      The three-point pinning still works on top of the placement (the map-click flow is
      unchanged), and undo/clear still work on both.
- [x] Saving from direct placement alone writes the platefit doc in the existing shape
      (the placement re-emitted as 3-5 page-px -> lon/lat pairs, plus the existing
      crop/size/model/cite fields, "by": "hand" via the 305 save path, the one-site line
      running) and the overlay appears on the map; a fit saved this way passes the checks
      a three-point fit passes (test_fit_provenance and the golden hand-fit set stay
      green; no document in the shared store is ever written by a test).
- [ ] tests/test_fit_queue.py gains a headless part (the 305 part-3 pattern: Chrome via
      tools/shot.mjs-style CDP, a temp tree, ephemeral port, no network): on a real queue
      site with a proposal, the page opens place mode with the map at the site's box and
      the ink on it; scripted input events (a drag, a wheel scale, a shift+wheel rotate)
      change the saved doc's pairs accordingly (the doc is read back from the temp store);
      after close, the site's earlier overlays are back. Hermetic.
- [x] docs/site_flow.md: what place mode is now (the anchor and where it comes from, the
      three gestures, the refinement, and what the saved doc contains), citing 307c's
      screenshots when they land.

## Notes
- The extension is web/fitkit.js in the fitqueue/review pattern: it loads after them,
  wraps their wrappers (openPlan last in the chain), injects its own <style>, and reaches
  the page's globals (P, map, refit, endFit, S, select) by name - the wrappers must not
  break the 201/205 pinned footprints. web/index.html is in Touches for a small hook only
  if the wrappers cannot reach in; the goal is to leave it byte-identical.
- The maplibre image source maps its texture with an affine built from three corners: the
  rotated-rectangle quad of a similarity is a parallelogram, so the rotated picture lands
  exactly - verify in the headless test (pixels), don't assume.
- Entry points (from the iteration-108 307a investigation, preserved on the record's
  closure): web/index.html (~1710 lines) - refit() (maps P.inkUrl onto the 'fit-prev'
  image source from the least-squares similarity of P.pairs), warpView() (proves the
  image-source quad mechanism), makeInk (survey-red on transparent), openPlan (the fit
  pane/points model); the place-mode flow fitqueue.js drives: endFit -> select(site) ->
  setGround -> loadDeps -> startFit(site) -> openPlan(row). Boxes 2-3 (fly-to on open,
  hide/restore overlays) live in the page's site-view and map-source code; keep the
  extension small and let the page own the map state.
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-13, iteration 256, agent a - context limit hit at the end of this session; the
work it describes (boxes 1/2/3/4/6 ticked, box 5 unticked, 307bc filed, 307's closure
note, DECISIONS entry) is committed with this hand-over. ONE OPEN SIDE MATTER left
behind: the session's full-suite run regenerated 4 of the 307d screenshots in
docs/site_flow/ (307d_A_2-placed, 307d_A_3-gestured, 307d_B_2-placed, 307d_B_3-gestured
- now MODIFIED, uncommitted). LEAVE THEM UNCOMMITTED: they are out of 307b's Touches
(docs/site_flow.md is named, the PNGs are not) and the driver's sweep carries them as
in aee0bd5/0b4dd2d. Cause: test_owner_check.py:907 copies its five fresh views into
docs/site_flow/ on every run (by design, outside its write-surface hash); the 307d
picks did NOT move (re-ran _picker(): A = oswestry-castle-q20713795 idx 38 bar, B =
devil-s-dyke-q3307343 idx 45 picture_size - exactly what the docs section names), so
the pixel delta is data movement (212b's sync / the lead's 77405cf) reflected in the
views, not flicker and not a pick change. /tmp/b2_head.png vs /tmp/b2_work.png were
staged for a visual compare when the limit hit (the 7KB B_2 shrink suggests a visible
content change - read them if you care). If the delta looks like meaningful drift, file
a small top-level task (236 = the next free number 200-499; Depends on: 306 - agent
c's in-flight 306 subtask touches docs/site_flow.md + docs/site_flow/, the
parallel-safety gate; Touches: tests/test_owner_check.py, docs/site_flow.md) about the
living-screenshots design (reconcile the docs text with the derived picks, or stop the
per-run in-checkout copy) - do not fix it in passing.

The session proper: the driver returned the parent - 307ba and 307bb are both done and
merged into main. This session re-verified 307b's own acceptance boxes by
running code and reading the committed tree, and ticked 1, 2, 3, 4, 6 (evidence below).
Box 5 (the headless part-4 proof) could NOT be ticked: it is red on this branch, and the
red is data drift assigned to task 235, not a page or test defect. Since 212b's sync
(6ce742f, Oct 13 06:31) the test's DERIVED pick moved onto marietta, whose only depiction
(a 1904 USGS topo) the page's own surveyOldEnough filter (150-year cutoff) hides, so the
seed check's `dep === 'none'` sees null (PITFALLS "The placement test's pick is
store-state-derived"; 235's file has the full analysis). Re-measured today: full suite
159 passed + 1 skipped + 1 failed, the lone red exactly this test, the RESULT line
identical to 235's record; every BEHAVIOUR sub-check in the same run (fly-to, anchor-is-
propose, five pairs on the map, drag, wheel scale, shift+wheel turn, pin, undo) reports
[ok]. The driver's done-claim re-check gates on a green suite (it rejected 212 over this
same red), so this task cannot be claimed done until 235 merges. Remaining work = 307bc
ONLY: after 235 is in main, re-run part 4 + the suite, tick box 5, set this done.)

**Box-by-box verification (iteration 256, all on the then-merged branch; machine date 2026-10-13):**
- **Box 1 (ticked):** `pytest tests/test_fit_queue.py::test_fit_queue_synthetic
  ::test_fit_queue_real ::test_fit_queue_namesake` = 3 passed (4.4 s) - part 1 pins the
  propose on a synthetic tree (bar 0.1306 / ratio-fallback 0.2 coarse / the two
  no-propose rows) and the real population, and part 1b (namesake) pins the 309 place
  check. Live web/data/fit_queue.json: 241/241 entries carry a propose with exactly the
  6-key set (13 bar / 4 ratio / 224 picture_size; 224 coarse) - every entry's best row
  anchors, so "every entry whose best row admits one" is met; the fallback (no propose
  -> the ordinary three-point flow) is pinned by the synthetic no-propose rows and
  fall-open guards in fitkit's _fkActivate. stdlib-only holds: tools/fit_queue.py
  imports only argparse/json/os/sys/datetime/pathlib plus tools/right_place.py,
  fit/review.py, fit/propose.py, each verified stdlib-only (argparse/json/os/re/sys/
  unicodedata; +hashlib/datetime; +math).
- **Box 2 (ticked):** web/fitkit.js's _fkActivate (committed, in main): map.fitBounds to
  the site's four corners (zero padding start - 307c's fix) BEFORE the ink appears;
  hides the `dep-<site.id>` layer while placed; the endFit wrapper restores it via
  applyDep with S.depSel/depMode/depOpacity/ground never touched - reached by the back
  button, Cancel, and the save path (the page's saveFit success path calls the wrapped
  endFit first, then its own applyDep shows the NEW overlay). The site panel's "Place an
  old plan" (#fitgo, index.html:793) flows into openPlan, which fitkit wraps LAST, so it
  opens place mode the same way when the queued plan is the one picked. Green at
  307ba's accepted done-claim (driver re-checked the suite then) and re-proven today:
  307d's test_owner_check.py (in today's 159 passed) exercises the open-on-works + hide
  on a page-showable site end to end; today's part-4 red run passed every seed
  sub-check except the dep-visibility one (the 235 pick issue).
- **Box 3 (ticked):** the three gestures are the committed fitkit.js: _fkOnDown/
  _fkOnMove (a drag moves the anchor by the pointer's ground delta, engages at 4 px -
  disjoint from the map's 3-px pin tolerance - absolute from press-down so move events
  cannot accumulate), _fkOnWheel (wheel scales about the centre mpx *= exp(-dy*0.0015);
  shift+wheel turns 1 deg per 100-unit notch), each re-emitted into the five pairs IN
  PLACE with a coalesced refit at the opacity slider's value; _fkHint rewrites the
  panel's live scale + rotation after every refit. Pinning on top is the page's
  unchanged map-click flow; _fkSync keeps P.anchorStack aligned with the pin/undo/clear
  count changes so Undo and Clear restore earlier anchors (the placement itself is
  inviolable). The map's pan/zoom/box-zoom are off while placed and restored on close.
  Green at 307bb's accepted done-claim; today's red run shows all gesture checks [ok].
- **Box 4 (ticked):** saving writes the page's own saveFit doc unchanged - the re-
  emitted five placed pairs (+ pins) at the 1dp/7dp convention plus crop/size/model/
  cite, "by": "hand" stamped by the store, and the one-site line runs from that write.
  Proven at 307bb's acceptance (part 4 read the doc back from the temp store: the exact
  17 keys, by:hand, its own least-squares fit equal to the placed anchor to 1e-3 m/px
  and 0.01 deg, the overlay the same similarity) and re-proven today by 307d's
  test_owner_check.py: two DERIVED queue sites end to end in a real headless browser
  (place, drag, wheel, shift+wheel, save, reload shows it unchanged), the shared store
  proven byte-identical afterwards - test_fit_provenance and the golden hand-fit hash
  set are in today's 159 passed. No test writes the shared store (hash-verified both
  there and in part 4's write-surface check).
- **Box 5 (NOT ticked - 307bc's):** part 4 is committed (tests/test_fit_queue.py
  ~1280-1764: _pick_place at 1654, place_served at 1678, the test at 1731) and is
  hermetic by construction (full temp tree with tools/fit/pipeline, the pick's book
  page materialised, --port 0, the GUARD kills every socket, no network - today's run
  shows only the expected /tiles/relief 404s). It fails today solely on the 235 pick
  drift (the pick checks what the SITE has, not what the PAGE will show). It turned
  green at 307bb's acceptance and stays green whenever the pick lands on a page-
  showable site (it was green again on f0dfd66's 229-entry queue before 6ce742f).
- **Box 6 (ticked):** docs/site_flow.md carries the full place-mode treatment: the
  "starting placement (the propose, 307ba)" section (~line 449: where the anchor comes
  from, the scale ladder bar -> ratio -> site size, the north-arrow rule, the no-
  propose fallback), "Place mode (task 307bb)" (~518: the anchor and five numbered
  points, the three gestures, pin refinement with Undo/Clear, exactly what Save writes,
  Cancel's restore, the part-4 proof, the pointer to 307d), "The working space (task
  307c)" (~530), and "The owner's check" (~1520). 307c's screenshots (place_before.png,
  place_after.png) and 307d's ten 307d_*.png are all present in docs/site_flow/.

**Tree state today (2026-10-13):** web/fitkit.js = the final version (307ba open/hide/
restore + 307bb gestures + 307c working space under body.placing); web/index.html is
byte-identical to main (its one footprint, the `<script src="fitkit.js">` tag at ~1747,
is IN main - the 307ba merge landed it); web/fitqueue.js has no changes since cf29be2
(305); the queue file = 241 entries, all with propose. Full suite: 159 passed + 1
skipped + 1 failed (6 min 29 s) - the lone red is 235's, and it is the driver's recorded
baseline (the 212 rejection, 235's file, the 306d/306e journals all carry it).

**Remaining work = 307bc only** (tasks/307bc-reverify-place-mode.md, Status: open,
Depends on: 235, Touches: tests/test_fit_queue.py + web/fitkit.js): after 235's pick-
rule fix is merged into main and the driver syncs it into this branch, re-run part 4
(all checks green including the dep-visibility one - the post-235 pick on the current
tree is oswestry-castle: eligible, its 1842 map shown, 1900 filtered - per the
PITFALLS entry), confirm the full suite green, tick box 5, set this task done.

**Re-read (for 307bc):** tasks/235-placement-test-dep-pick.md (the exact fix spec:
mirror the page's two rules in _pick_place - the surveyOldEnough 150-year filter over
{map, aerial, topo} and the auto-select of a {plan, drawing, view} depiction else the
last surviving 'map' - before accepting a site); tests/test_fit_queue.py's _pick_place
(1654) / place_served (1678) / test (1731) and the module docstring's Part 4 paragraph
(63-75); PITFALLS "The placement test's pick is store-state-derived" (~line 1410: the
full history and rules - (a) simulate _pick_place() before/after ANY doc deletion,
(b) a parallel task must not "fix" that test file, (c) the GOAL point-1 invariant is
unaffected); web/fitkit.js's header (the design doc). No page code change is expected;
if a post-235 run fails on anything OTHER than the pick, that is a real page defect -
fix it in web/fitkit.js and say so in the hand-over.

**Env/state:** .venv present and current (no requirements change since the 307bb era);
the /tmp/fkverify/ throwaways are stale (the pick has moved twice since); machine date
2026-10-13 (part 4 asserts the doc's `at` startswith '2026-' and the 150-year cutoff is
year-relative - if the machine's year changes, say so in 307bc's hand-over); suite
timing ~6.5 min; headless Chrome at /opt/google/chrome/chrome with the shot node_modules
(both present - part 4 does not skip).
