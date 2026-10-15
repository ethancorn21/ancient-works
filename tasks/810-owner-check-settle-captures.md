Status: open
Depends on: 307d, 812, 813
Touches: (none - final verification only; the code change moved to 812 (settle + double-shot) and 813 (refresh flag + write-surface + docstrings) in the 2026-10-15 iteration-190 re-split)

# 810: The 307d owner check - settle the map before the saved/reload captures and stop the per-run in-checkout re-render (explicit refresh flag)

Part 1 of 242's split (2026-10-15). Re-split 2026-10-15 (iteration 190, per the driver: agent a
had nothing to build for 68 minutes while every waiter - 230, 241, 242, 811, and 236c through
241 - waited on this one task alone): the whole code change moved to two parts on the one file
tests/test_owner_check.py - **812** (the settle wait and the double-shot stability assert, the
flake fix; depends only on done 307d, startable immediately) and **813** (the explicit refresh
flag, the ten PNGs into the write surface, the docstrings; after 812 because it is the same
file and its docstrings describe 812's settle as part of the regime). This task now WAITS on
both and keeps only the final verification (the 242 pattern). 811 (the one-time refresh, the
docs note, the PITFALLS rewrite) and 242 (the family's final check) wait on this. The
measured-drift background (28.6-33.6% on the four saved/reload views, the mid-transition
signature, the pair flake) is in 242's goal and in 812's header. The waiters 230 and 241
carry 812 and 813 on their Depends lines directly (they are held on the mid-transition flake
812 fixes and the PNG dirt 813 stops).

## Goal

(Kept as the design spec for 812/813; the boxes the parts deliver moved with them. In
tests/test_owner_check.py and its embedded PROBE. The pick (derived, never pinned) and every
existing check stay exactly as they are; this is a capture-timing fix, not a flow change. Do
not touch tests/test_fit_queue.py (the 307/235 family) or the page. The pair always runs as
one invocation, A then B (PITFALLS: the B test cannot run in isolation).)

1. **Stable captures** (812). Before the `4-saved` and `5-reload` screenshots (and any other
   view where the map can still be moving - the q1/q2 gesture samples included, where the
   pair flake shows up) wait for the map view to settle: e.g. wait for maplibre's
   `moveend`/`idle` after the last interaction, or disable the page's transitions in the
   test view.
2. **Prove the stability in one run** (812). Once settled, take the capture a second time
   and assert the two shots differ by <0.5% of pixels at threshold 32, so a mid-transition
   regression fails the test instead of dirtying PNGs (additive; no existing assert changes).
3. **Stop the unconditional in-checkout copy** (813). `_run_one` currently copies the ten
   fresh renders into `docs/site_flow/307d_<A|B>_<1..5>.png` on EVERY run and never compares
   them against the committed bytes. The fresh renders stay in the test's private temp tree
   (the test already asserts everything it needs from the temp tree). Copying into
   `docs/site_flow/` happens only on an explicit refresh - an env var or a pytest flag,
   named in the test's docstring - that re-renders all ten from a run and writes them into
   `docs/site_flow/`.
4. **The checkout's PNGs enter the write-surface proof** (813). Add the ten committed
   `docs/site_flow/307d_*.png` to `_write_surface`, so the existing "the run wrote into the
   checkout's shared store" assert proves an unflagged run left them byte-identical.
5. **Update the module and test docstrings** (813) to the new regime: the ten PNGs are a
   pinned snapshot committed in the repo; an ordinary run never touches them; the named flag
   re-renders them.

## Acceptance criteria

(Re-split 2026-10-15, iteration 190, per the driver: the boxes the parts deliver moved with
them - former box 1 (two-run stability, the pair green, the additive discipline of the
settle/double-shot) to 812; former box 2 (checkout byte-identical, the refresh flag) plus
former box 4 (suite green, git status clean) to 813. Nothing was built yet in this task, so
it WAITS on the parts and keeps only the final verification; the plan for the remaining work
is in the hand-over below.)
- [ ] On the merged tree (812 and 813 done): two consecutive unflagged runs of the owner_check
      pair (one invocation per run, A then B) are stable - their ten temp-tree views match
      (the pair's in-run double-shot assert already proves it per run; this is the cross-run
      check) - and both tests pass end to end with the pick still derived and no existing
      check changed.
- [ ] An unflagged run leaves every `docs/site_flow/307d_*.png` in the checkout byte-identical
      (the write-surface proof) and `git status` on `docs/site_flow/` is clean after it.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).

## Hand-over

(2026-10-15, iteration 190, agent c) **RE-SPLIT per the driver's instruction** (agent a had
nothing to build for 68 minutes while every waiter - 230, 241, 242, 811, and 236c through 241
- waited on this one task alone; the 189 split had made this the whole code change). Nothing
of the code was built yet, so per the split rule this task WAITS on the parts (never both
ways) and keeps only the final verification (the 242 pattern): `Depends on:` is now
`307d, 812, 813`; `Touches:` cut to none. No cycle: 812 (depends only on done 307d, startable
immediately) -> 813 (same file, after 812) -> 810 (this) -> 811 -> 242 -> {230, 241} -> 236c.

The parts (the lowest free numbers in 800-1099; both Touches the one file tests/test_owner_check.py,
so they are serial, not parallel):
- **812** (tasks/812-owner-check-settle-shots.md) - the flake fix: the settle wait
  (maplibre `moveend`/`idle` after each interaction chain - the 4.5 s flyTo
  web/index.html:874 + 900 ms fitBounds web/fitkit.js:573 that the probe's fixed sleeps
  never waited for) before every capture, and the in-run double-shot assert (two shots per
  view, <0.5% differing pixels at threshold 32, all ten views). Carried former box 1 and the
  settle/double-shot half of former box 3. The pick stays derived; every existing check
  unchanged; tests/test_fit_queue.py and the page untouched.
- **813** (tasks/813-owner-check-refresh-flag.md) - the pinned-snapshot regime: the explicit
  refresh flag (env var or pytest flag, named in the docstring) replacing the unconditional
  in-checkout copy, the ten docs/site_flow/307d_*.png into `_write_surface`, the module and
  test docstrings to the new regime. Carried former box 2, the additive discipline of former
  box 3 for the regime, and former box 4. Runs after 812 (same file; the docstrings describe
  812's settle as part of the regime).

Waiters updated per the driver's rule: 230's Depends is now "211, 207a, 207b, 807, 808, 242,
810, 812, 813" and 241's "240, 242, 810, 812, 813" (812/813 added directly - both are blocked
by the mid-transition flake 812 fixes and the PNG dirt 813 stops; the rest reaches them
transitively through 810/242). 811 (Depends: 810, unchanged - the one-time refresh runs
813's flag, which 810 has verified) and 242 (307d, 810, 811, unchanged) and 236c (unchanged)
need no new numbers; 242's hand-over chain line was corrected to the new shape.

**What remains HERE (verification only, no file changes):** when the driver returns this task
(after 812+813 merge): (1) run the unflagged owner_check pair twice (one invocation per run,
A then B - PITFALLS: B cannot run alone) and check the two runs' ten temp-tree views match
(the in-run double-shot assert covers per-run; this is the cross-run check) and both tests
pass -> tick box 1; (2) confirm `git status` on docs/site_flow/ is clean after an unflagged
run (813's write-surface assert proves it in-test; git status is the external view) -> tick
box 2; (3) run the full suite -> tick box 3, set Status: done, claim. If the captures still
drift or the checkout dirt reappears: that is a defect in 812's or 813's lane - put the run
evidence in "## Proposed changes" on that task file and hold this task; never re-file the fix
here, never weaken or delete a test.
