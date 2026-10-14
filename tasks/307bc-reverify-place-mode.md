Status: open
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
- [ ] test_placement_gestures_and_save_in_the_browser passes end to end on the post-235
      tree: the derived pick is a site the PAGE will show an overlay for (the seed
      check green including the dep layer's visibility), all behaviour checks green
      (the gestures own the mouse, drag moves, wheel scales, shift+wheel turns, pin
      refines, undo restores), the saved doc read back from the temp store is exact
      (the 17-key shape, by:hand, pairs = the placed set), the one-site line's overlay
      lands in the tree's depictions.json, Cancel brings the seeded overlay back, and
      the checkout's write-surface hash is unchanged around the run (hermetic).
- [ ] The full suite is green: `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`
      at the post-235 baseline (at iteration 256 it was 159 passed + 1 skipped + 1
      failed, the lone red this test). If any OTHER test is red, it is a different
      task: file it (next free number 200-499, its own Depends on/Touches) and say so -
      don't fix it here.
- [ ] tasks/307b-on-map.md's box 5 is ticked with this run's evidence recorded in its
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

(2026-10-13, iteration 256, agent a - first session: the task was filed as the driver
returned the parent 307b with both subtasks (307ba, 307bb) done. Nothing to do until
235 merges into main and the driver syncs it in - that is the Depend. Then: run part 4,
run the full suite, tick 307b's box 5 with the evidence, set 307b done. The parent's
hand-over has the iteration-256 verification of everything else.)
