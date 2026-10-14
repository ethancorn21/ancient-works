Status: open
Depends on: 307d
Touches: tests/test_owner_check.py, docs/site_flow.md, docs/site_flow/

# 242: Pin the 307d owner-check screenshots - settle before shooting, stop the per-run in-checkout re-render

## Goal
`tests/test_owner_check.py::_run_one` re-renders all ten `307d_*.png` views into `docs/site_flow/`
on EVERY run and never compares them against the committed bytes. Measured 2026-10-14 (iteration
199, agent a): the card/placed/gestured views are stable run-to-run (0-1.25% differing pixels,
threshold 32), but the four saved/reload views (A_4/A_5/B_4/B_5) differ by 28.6-33.6% of pixels
between two runs one hour apart on the IDENTICAL tree - visual inspection shows the map view not
settled at shot time (the overlay rectangle shifts slightly relative to the ground imagery between
runs, i.e. the captures land mid-transition). Consequences: any branch that ran the suite is dirty
on up to 7 of the ten PNGs (the driver's sweep must carry them; the b14918f merge produced binary
conflicts on them - see the PITFALLS entry "test_owner_check re-renders all ten 307d golden PNGs..."),
and the docs' PNGs no longer correspond to the 307d-acceptance bytes they replaced. The 307b
hand-over (iteration 256) filed this on the condition that the drift looked meaningful; it does.

Fix the design:

1. **Stable captures.** Before the saved/reload captures (and any other view where the map can
   still be moving), wait for the map view to settle (e.g. wait for the maplibre `moveend`/idle
   after the last interaction, or disable the page's transitions in the test view). The pick
   (derived, never pinned) and every check must stay exactly as they are; this is a capture-
   timing fix, not a flow change.
2. **Stop the unconditional in-checkout copy.** The fresh renders stay in the test's private
   temp tree (the test already asserts everything it needs from the temp tree). Copying into
   `docs/site_flow/307d_*.png` happens only on an explicit refresh (an env var or a pytest flag
   named in the test's docstring). The ordinary run must leave the checkout's ten PNGs
   byte-identical (add them to the test's existing write-surface hash check if that is the
   natural place).
3. **Regenerate once, under the new regime.** Run the explicit refresh once on the current
   tree and commit the ten PNGs (they become the pinned snapshot the docs cite).
4. **Docs.** The 307d section in docs/site_flow.md ("The owner's check...") gains one short
   note: the screenshots are a pinned snapshot (date + how to refresh); the existing text
   (dated "on the 241-entry queue of 2026-10-13") stays - the picks it names are still the
   derived picks (oswestry n0119_1 bar / devil-s-dyke n0662_1 picture_size), only the queue
   indices shifted with re-exports (38/45 -> 3/8 on the 180-entry queue).

## Acceptance criteria
- [ ] Two consecutive unflagged runs of `pytest tests/test_owner_check.py` on the same tree
      produce byte-identical (or <0.5% differing pixels at threshold 32) A_4/A_5/B_4/B_5 views
      in the temp tree (all ten stable, not just the four); both tests still pass end to end
      and the write-once / shared-store / golden-hash checks stay green.
- [ ] An unflagged run leaves every `docs/site_flow/307d_*.png` in the checkout byte-identical
      (verified by the test's write-surface hash or an equivalent check); the explicit
      refresh flag re-renders all ten from a run and writes them into `docs/site_flow/`.
- [ ] The ten PNGs are regenerated once under the new regime and committed; the 307d section
      of docs/site_flow.md carries the pinned-snapshot note with the refresh command.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`) and
      `git status` on docs/site_flow/ is clean after an unflagged run.

## Notes
- The PITFALLS entry "test_owner_check re-renders all ten 307d golden PNGs into
  docs/site_flow/ on EVERY run..." currently prescribes the workaround (restore main's bytes
  before committing; resolve merge conflicts to main's bytes). On this task's merge, rewrite
  that entry's What-to-do to describe the new design and point at the refresh flag; keep the
  history lines. Agent c's 302f iter-127 entry documents the same dirt from her side.
- The drift was measured, not guessed: HEAD-vs-worktree and same-data run-vs-run pixel
  comparisons plus a visual diff (the overlay/ground relative shift) are in the 2026-10-14
  307bc DECISIONS entry and in this file's goal.
- Do not touch tests/test_fit_queue.py (the 307/235 family) or the page; this task is the
  owner-check test and its docs section only.
