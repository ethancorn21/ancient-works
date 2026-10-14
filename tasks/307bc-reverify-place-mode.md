Status: done
Depends on: 235
Touches: tests/test_fit_queue.py, web/fitkit.js

# 307bc: Re-run the place-mode headless proof on the fixed pick, and close 307b

## Goal
Parent 307b's box 5: the part-4 headless proof in tests/test_fit_queue.py (headless
Chrome on a full temp tree: the card's "Place the drawing" opens the placement on the
works, one scripted drag, a wheel scale, a shift+wheel turn, Save from the placement
alone read back from the temp store with the one-site line's overlay, a fresh run's
Cancel restoring the earlier overlay, the checkout's write surface hash-verified around
the run) is committed and was green at 307bb's acceptance, but it has been red since
212b's sync (6ce742f, Oct 13) moved its DERIVED pick onto marietta - a site whose only
depiction (a 1904 USGS topo) the page's own surveyOldEnough filter (150-year cutoff)
hides, so the seed check's `dep === 'none'` sees null. Task 235 (open; its two deps,
306e and 307d, are done) fixes the pick to mirror the page's two depiction rules. Once
235 is merged into main and the driver has synced it into this branch, re-run the proof
and close 307b.

## Acceptance criteria
- [x] test_placement_gestures_and_save_in_the_browser passes end to end on the post-235
      tree: the derived pick is a site the PAGE will show an overlay for (the seed
      check green including the dep layer's visibility), all behaviour checks green
      (the gestures own the mouse, drag moves, wheel scales, shift+wheel turns, pin
      refines, undo restores), the saved doc read back from the temp store is exact
      (the 17-key shape, by:hand, pairs = the placed set), the one-site line's overlay
      lands in the tree's depictions.json, Cancel brings the seeded overlay back, and
      the checkout's write-surface hash is unchanged around the run (hermetic).
- [x] The full suite is green: `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`
      at the post-235 baseline (at iteration 256 it was 159 passed + 1 skipped + 1
      failed, the lone red this test). If any OTHER test is red, it is a different
      task: file it (next free number 200-499, its own Depends on/Touches) and say so -
      don't fix it here.
- [x] tasks/307b-on-map.md's box 5 is ticked with this run's evidence recorded in its
      hand-over, and the file set to Status: done.

## Notes
- The parent's hand-over (iteration 256) carries the box-by-box verification of 307b's
  boxes 1-4 and 6 - all ticked and standing; only box 5 waits on this run.
- Do NOT change the pick to make the test pass: 235 owns tests/test_fit_queue.py's
  _pick_place, and this task runs AFTER it merges (the driver syncs main before
  handing this out). If the post-merge pick still lands on a site with no page-visible
  depiction, that is 235's defect to fix in its own run: report it (its hand-over or
  the driver's note), don't re-fix the pick here.
- web/fitkit.js is in Touches only for a real page defect a post-235 run would expose;
  the page code is expected unchanged (green at 307bb/307c/307d acceptance, and the
  iteration-256 red run shows every behaviour check green).
- PITFALLS "The placement test's pick is store-state-derived" (~line 1410): the full
  green/red history and the practical rules (simulate _pick_place() before/after any
  doc deletion; no parallel task edits that test file).
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-14, iteration 199, agent a - DONE in this session, all three boxes ticked by
running code; no code files changed at all - web/fitkit.js needed nothing, confirming
the note's expectation.)

What was done:
1. Confirmed 235 is in this branch (driver merged main at 8c967c8): `_pick_place` at
   tests/test_fit_queue.py:1543 now gates on `_page_auto_select` (1528), which applies
   `_survives_page_filter` (1517) - the page's surveyOldEnough (web/index.html:444-445)
   + select() auto-select (:688/:866) mirrored in stdlib.
2. Simulated the pick before running (PITFALLS rule (a)): `_pick_place()` =
   oswestry-castle-q20713795, idx 3 of the current 180-entry queue, plan
   earthworkenglan01allcgoog_n0119_1 (bar 0.1646 m/px, rot 0, coarse false). Entries
   before it: idx 0 fort-ancient ineligible, idx 1 marietta skipped by exactly the
   235 rule (no-page-showable-dep: her only 1904 USGS topo fails the 150-year filter),
   idx 2 forthill ineligible. The oswestry site's surviving depiction = the 1842
   six-inch map (auto-selected; the 1900 map filtered).
3. Ran part 4: tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
   - PASS, 66.21 s (1 passed). Every sub-check in it: seed (gestures own the mouse,
   dep layer hidden incl. visibility), gestures (drag/wheel/shift+wheel/pin/undo),
   save (doc read back from the temp store: 17 keys, by:hand, pairs = the placed set),
   one-site line (overlay in the temp tree's depictions.json), Cancel (earlier overlay
   restored), write-surface hash unchanged (hermetic).
4. Full suite: 177 passed, 1 skipped, 0 failed (527 s) = 235's recorded baseline; no
   other red, so nothing filed under box 2.
5. Ticked 307b's box 5 with this evidence in its (new, final) hand-over and set
   307b to Status: done; added the closure note to parent 307's hand-over (all four
   subtasks 307a/307b/307c/307d now done - the parent is ready for the driver to
   return it).
6. Judged the 307b hand-over's open side matter (the 307d screenshot drift): it is
   meaningful AND not just data movement - see the 2026-10-14 307bc DECISIONS entry
   for the measurements (same-data run-to-run 28.6-33.6% pixel diff on the four
   saved/reload views; the map is not settled at shot time). Filed tasks/242
   (Depends on: 307d; Touches: tests/test_owner_check.py, docs/site_flow.md,
   docs/site_flow/). Before committing, restored the ten 307d PNGs to main's bytes
   (the PITFALLS workaround; HEAD differed from main on six of them - the driver's
   sweep had committed the iteration-256 re-renders into this branch, 1cff9fc).
7. Updated the PITFALLS 307d-PNG entry with the iter-199 measurement and the 242
   pointer.

Nothing left: this task is closed; 307b is done; the only open follow-on is 242 (the
driver will hand it out when free). Environment notes for whoever touches this area
next: machine date 2026-10-14 (part 4 asserts the doc `at` startswith '2026-' and the
150-year cutoff is year-relative - flag it in the hand-over if the year rolls);
headless Chrome at /opt/google/chrome/chrome with the shot node_modules; suite
timing ~9 min; the /tmp/fk307bc_run1/ + /tmp/fkA4_run{1,2}.png throwaways hold this
session's drift evidence (stale after a data move).
