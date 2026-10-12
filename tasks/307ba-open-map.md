Status: in-progress
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
  full recipe is in the hand-over. 805's in-run full review export subsumes my 220 filing.
- The stage-B row shape: data/books/index.jsonl (scale_text, blank_boxes[{kind:"scale_bar",
  box}], north_angle_deg, north_arrow, map_box, full_size). fit/ has no __init__.py; import
  via sys.path.insert(0, str(ROOT / "fit")) like tools/site_done.py:43.
- Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-12, iteration 117, agent a - WAIT, now exact. main is still cf29be2: no 309/804/805
commits, web/data/review.json byte-identical to main's stale copy (md5 b6506007, 340 open of
341) - so the 3 re-claim-blocking failures are unchanged and a re-claim now would fail the
same way (do not re-claim). Since iteration 116: agent c SPLIT 309 into 804 + 805 (on
agent/c; main's 309 file still says open). I read both specs on agent/c and mapped the merge
surface against this branch (recipe below); I refreshed my own filing 220 (its stale dep
note now describes the split; it keeps Depends on: 309 - the driver-visible gate - and gets
a runner's hand-over). The re-claim chain: 804 merges -> 805 merges (its in-run FULL review
export - fit/review.py export(root, site_id=None), necessarily full because the namesake
upserts span sites - records the same 6 write-once resolutions 220 targets; the iteration-
116 scratch verified the semantics and the no-op second run) -> 309 closes (bookkeeping
only: checks its three carved boxes; the tools/right_place.py module file lands then, inert
to the 3 tests' data) -> 220 runs as a no-op verify -> the driver syncs main into this
branch -> the 3 failures go green -> re-claim done.)

**Wait condition for a future session (check in this order):**
1. `git log main --oneline -20`: still cf29be2 (no 804/805/309 commits)? Nothing to build -
   this task waits on agent c. Do NOT touch data/review, web/data/review.json or re-
   baseline any test (the stale page is a real store invariant; iteration-116 DECISIONS
   entry). Cheap unchanged-check: `git show main:web/data/review.json | md5sum` ==
   b6506007.
2. main carries 804 and/or 805 (or 309 closed)? The driver has synced it into this branch:
   expect text conflicts in tools/fit_queue.py, tests/test_fit_queue.py, web/data/
   fit_queue.json (both sides rewrote them). Resolve with the recipe below and run `.venv/
   bin/python -m pytest -q`. Once 805's (or 220's) export is in the synced tree: expect 73
   passed + 1 skipped, no known failures -> re-claim done. If only 804 is in (805/220 not
   yet): the 3 review-page failures remain - wait, do not re-claim.

**Merge recipe (the next session that sees 804/805 on main executes it):**
- tools/fit_queue.py build(): take 804's two-phase structure (ALL flag decisions computed
  over the pre-mutation candidate sets, then drops/moves/upserts, then entries recomputed).
  Keep MY wiring at its current position: the `_entry_propose(root, sid, plan)` call at the
  END of the per-site loop - after the final best selection, before entries.append - so a
  move that changes a site's best candidate recomputes that entry's propose; keep the
  `_entry_propose` helper, the `import propose` line, the docstring's fifth-input paragraph,
  and the propose key order {pairs, scale_m_px, rot_deg, scale_source, coarse, note} after
  "candidates".
- tests/test_fit_queue.py: keep BOTH sides - my part 1 (synthetic stage-B tree, 7 entries,
  the propose pinned against propose_for called in-test) and 804's namesake test plus its
  re-derived test_fit_queue_real (copies data/catalog + data/books into the temp tree).
  804's synthetic-tree additions must not flag my fictional sites (no county words ->
  right_place fails open, the module's documented rule) - verify by RUNNING the merged
  file, not by assume; if a synthetic site gets flagged, make its place neutral, never
  loosen the propose assertions. Parts 2-3 stay as written; the part-2 open_after delta
  goes green once the synced tree has the in-sync page.
- web/data/fit_queue.json (both sides regenerated -> conflict): regenerate with the merged
  build `python3 tools/fit_queue.py --root .` and commit the joint file (805's right-place
  drops/moves + my propose on the surviving entries; if 805 ran before my branch merged,
  its committed version lacks propose - the regeneration adds it back on top of the wired
  build).
- web/data/review.json + data/review/: 805's/220's - take THEIRS (my branch's copies are
  main's stale ones); never edit them from this task.
- docs/site_flow.md: keep both sections (my "Ready to fit" propose paragraph, 805's
  namesake-report section) - disjoint regions, clean merge expected; flag any overlap in
  DECISIONS.
- fit/propose.py, web/fitkit.js, web/index.html: only mine - keep mine (804's spec forbids
  touching agent a's web files; web/index.html stays exactly one line over main and
  web/fitqueue.js byte-identical - the part-3 pin).

**State (all committed, unchanged this session):** cbb36c8 (boxes 1-3, the data side),
732fe57 (box 4: web/fitkit.js + the one script tag), 7f7e7c0 (box 5: docs), 9efb944 (the
rejected done claim), cc6e9ed (the iteration-116 diagnosis). Suite on this branch: 70
passed + 1 skipped + the 3 stale-page failures (test_fit_provenance::
test_line_refuses_unmarked_non_auto_doc, test_fit_queue::test_save_runs_the_one_site_line,
test_site_done::test_site_done_line) - all three wait on 805's/220's in-sync export, as
analysed in the iteration-116 DECISIONS entry (page 340 open of 341 vs the current code's
335; the full export records the 6 write-once resolutions and makes all three pass by
construction).

**Re-read (only when the 804/805 merge lands):** tools/fit_queue.py (where my _entry_propose
sits in build()); tests/test_fit_queue.py parts 1-2 (the synthetic tree 804 extends; the
save test whose open_after delta trips on the stale page). The iteration-116 Re-read list
(fitkit, index.html ~832/902/1706, part 3, /tmp/fkprobe.mjs) belongs to 307bb, not this
task.
