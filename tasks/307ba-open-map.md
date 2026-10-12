Status: done
# 307ba: Open the map - the queue carries the proposal, and place mode opens ON the works
Depends on: 307a, 220
Touches: fit/propose.py, tools/fit_queue.py, web/fitkit.js, web/index.html, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md, tasks/220-review-page-reexport.md (my own filing - kept in sync with the 309 split)

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
- [x] Opening a queue site with a proposal (the card's "Place the drawing", or the site
      panel's "Place an old plan" when the site's queued plan is the one picked): the map
      flies to the site's box (its four corners) centred, before the drawing appears; while
      place mode is open, the site's earlier overlay (the dep-* fitted drawing or survey
      sheet applyDep was showing) is hidden; on close (back button, Cancel, or saving) it
      comes back exactly as it was (same depiction selected, same ground). web/fitkit.js is
      a new extension in the fitqueue/review pattern (loads after them, wraps openPlan last
      in the chain and endFit; the <style> injection the pattern names stays out until
      307bb's gestures need one - box 4 adds no visible UI, recorded in DECISIONS;
      _fk-prefixed saved names);
      web/index.html changes by the one script tag alone; web/fitqueue.js stays
      byte-identical.
- [x] docs/site_flow.md's "Ready to fit" section: the entry's new propose field (what it is,
      where the anchor comes from, the fail-open to the three-point flow). The full place-mode
      section (gestures, save, screenshots) is 307bb/307c's.

## Notes
- The full box-1 design and the page-side design sketch (anchor model, wrap points, hide/
  restore, the no-propose byte-identity rule) are in the parent 307b's ## Hand-over and the
  2026-10-12 307b DECISIONS entry (iteration 110) - implement from there, they are precise.
- Agent c's 309 is SPLIT (on agent/c; main still shows it open) into 804 (the right-place
  wiring in tools/fit_queue.py) and 805 (the rebuild of the committed queue/review data;
  depends on 804): expect their merge of build() and the queue file; keep the propose wiring
  localized (one helper, one key per entry, docstrings) so the merge stays trivial - the
  full recipe is in the hand-over. 805's in-run full review export would have subsumed my
  220 filing - overtaken: the lead ran that export themselves (c5250a4) before 309 closed
  and ordered a resume without waiting for c's chain; 220 closed as done (iteration 121);
  805's rebuild is now a later snapshot update, not a precondition for my re-claim.
- The stage-B row shape: data/books/index.jsonl (scale_text, blank_boxes[{kind:"scale_bar",
  box}], north_angle_deg, north_arrow, map_box, full_size). fit/ has no __init__.py; import
  via sys.path.insert(0, str(ROOT / "fit")) like tools/site_done.py:43.
- Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-12, iteration 122, agent a - DONE. The driver's sync 81d8dfc merged main
(57b3988) into agent/a; web/data/review.json became c5250a4's 220 export (md5
2609ecef185bd893617cda94bedc40b7, 335 open of 341), so the 3 stale-page tests flipped
green with no test change, exactly as the iteration-121 prediction. Full suite =
75 passed + 1 skipped, 0 failed (113.7 s; the one skip is test_batch_eu's known
live-population drift skip, agent c's 203b domain). All 5 boxes re-verified on the
post-sync tree: box 1 = 117/117 queue entries carry the 6-key propose in box order
(20 bar / 4 ratio / 93 picture_size); box 2 = fit/propose.py root-aware, byte-identical
through the sync, its golden + batch callers green in the suite; box 3 = part-1 tests
green; box 4 = web/fitkit.js + the one script tag (index.html:1709) byte-identical
through the sync (the headless verification stood from iteration 116); box 5 =
docs/site_flow.md untouched by the sync. The sync's diff touched none of my files
(only PITFALLS, the 6 review item files, pipeline/books.py+build_catalog.py,
tests/test_region.py, web/data/review.json and 2 task statuses). 307bb's start
condition (main synced + 307ba re-claimed) is now met; its baseline is this 75+1
suite and its design source is the parent 307b's hand-over, unchanged.)

**If this done claim is rejected again (or a future session bounces off a 309-chain
merge) - diagnose, never re-baseline:**
- The 3 count-deriving tests read the committed review page, a snapshot of the item
  population at the last full export. First step always: scratch copy of the current
  tree, `fit/review.py export --root <copy>` (seed the copy with the gitignored store
  elements: a web/data/sites copy + the data/raw symlink - du=0, PITFALLS). No-op
  export + still-red tests = item-population drift (203b/207/805 wrote new data/review
  items after c5250a4) -> fix = one more full export in the checkout (`fit/review.py
  export --root .`, commit the two store paths). The PITFALLS entry "the committed
  review page is a snapshot" has the full recipe and all three triggers.
- If agent c's 309 chain (804/805) lands on main and a merge hands me a text conflict
  (both sides rewrote tools/fit_queue.py, tests/test_fit_queue.py,
  web/data/fit_queue.json): resolve per the full re-pinned recipe in the 2026-10-12
  307ba iteration-120 DECISIONS entry - their two-phase build() as the base, my
  `_entry_propose` as a POST-PASS between the entries comprehension and the sort, one
  pair of path-inserts + three imports, tests are a union, the queue file regenerated
  with the merged build (expect ~114 entries at their data state - never pin a
  count); their review.json/data/review win; my fitkit.js/index.html/fit/propose.py
  win. tools/right_place.py must land together with the rewired fit_queue.py (never
  cherry-pick one without the other; right_place.load degrades per-store optional,
  so no-catalog temp trees stay pure no-ops).
- 307bb (parent boxes 3-6) starts on this branch state: its full-tree fixtures see a
  consistent page (c5250a4) and its headless save flow runs the one-site line against
  a 75+1 baseline.
