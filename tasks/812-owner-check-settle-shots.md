Status: open
Depends on: 307d
Touches: tests/test_owner_check.py

# 812: The 307d owner check - settle the map view before every capture, proved by a double shot

Part 1 of 810's split (2026-10-15, iteration 190): the flake fix in tests/test_owner_check.py
and its embedded PROBE. 813 (the pinned-snapshot regime on the SAME file) runs after this; 810
keeps the final verification and waits on this and on 813; 811 then 242 wait on 810. The waiters
230 and 241 carry this number on their Depends lines directly - they are held on the
mid-transition flake this part fixes. Background: 242's goal and the 2026-10-14 307bc
DECISIONS entry (now in the archive); the drift is measured, not guessed:

- On the IDENTICAL tree, runs an hour apart differ by 28.6-33.6% of pixels (threshold >32) on
  the four saved/reload views (A_4/A_5/B_4/B_5) - the captures land mid-transition: the
  placement chains the 4.5 s site flyTo (web/index.html:874) with a 900 ms fitBounds
  (web/fitkit.js:573) and the probe's fixed sleeps never wait for `moveend`; visually the
  overlay rectangle shifts slightly relative to the ground imagery. The card/placed/gestured
  views stay 0-1.25% (encoding noise).
- The same mid-transition signature flakes the owner_check A/B pair itself (the gesture check
  `toolbar scale and turn change the drawing on screen`, e2/e1 = 1.06105 ~= 1.05 x 82.863):
  230 it.214-216, 239 it.226-228, 241 it.187-188.

## Goal

In tests/test_owner_check.py and its embedded PROBE. The pick (derived, never pinned) and every
existing check stay exactly as they are; this is a capture-timing fix, not a flow change. Do not
touch tests/test_fit_queue.py (the 307/235 family) or the page. The pair always runs as one
invocation, A then B (PITFALLS: the B test cannot run in isolation).

1. **Stable captures.** Before the `4-saved` and `5-reload` screenshots (and any other view
   where the map can still be moving - the q1/q2 gesture samples included, where the pair
   flake shows up, and the `2-placed` shot and the quad reads after place, which follow the
   4.5 s flyTo + 900 ms fitBounds chain) wait for the map view to settle: e.g. wait for
   maplibre's `moveend`/`idle` after the last interaction, or disable the page's transitions
   in the test view.
2. **Prove the stability in one run.** Once settled, take each capture a second time and
   assert the two shots differ by <0.5% of pixels at threshold 32 (all ten views, not just
   the four - the other six stay at their historical 0-1.25% encoding noise, comfortably
   under the line), so a mid-transition regression fails the test instead of dirtying PNGs
   (additive; no existing assert changes).

## Acceptance criteria

- [ ] Two consecutive unflagged runs of `pytest tests/test_owner_check.py` on the same tree produce
      byte-identical (or <0.5% differing pixels at threshold 32) A_4/A_5/B_4/B_5 views in the temp
      tree (all ten stable, not just the four - the other six stay at their historical 0-1.25%
      encoding noise); both tests still pass end to end and the write-once / shared-store /
      golden-hash checks stay green.
- [ ] The pick is still derived and no existing check changed (same flow, same asserts); the settle
      wait and the double-shot stability assert are additive.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).
