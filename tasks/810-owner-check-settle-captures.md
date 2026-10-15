Status: open
Depends on: 307d
Touches: tests/test_owner_check.py

# 810: The 307d owner check - settle the map before the saved/reload captures and stop the per-run in-checkout re-render (explicit refresh flag)

Part 1 of 242's split (2026-10-15): the whole code change. 242 waits on this and on 811, and 811
waits on this (this is the critical path - nothing else blocks it: its only dependency, 307d, is
done). Background: 242's goal; the drift is measured, not guessed (the 2026-10-14 307bc DECISIONS
entry, now in the archive, and the PITFALLS entry "test_owner_check re-renders all ten 307d golden
PNGs..."):

- On the IDENTICAL tree, runs an hour apart differ by 28.6-33.6% of pixels (threshold >32) on the
  four saved/reload views (A_4/A_5/B_4/B_5) - the captures land mid-transition: the placement
  chains the 4.5 s site flyTo (web/index.html:874) with a 900 ms fitBounds (web/fitkit.js:573) and
  the probe's fixed sleeps never wait for `moveend`; visually the overlay rectangle shifts slightly
  relative to the ground imagery. The card/placed/gestured views stay 0-1.25% (encoding noise).
- The same mid-transition signature flakes the owner_check A/B pair itself (the gesture check
  `toolbar scale and turn change the drawing on screen`, e2/e1 = 1.06105 ~= 1.05 x 82.863): 230
  it.214-216, 239 it.226-228, 241 it.187-188 - both waiters are held on "Depends on: 242" and have
  this number on their lines directly.

## Goal

In tests/test_owner_check.py and its embedded PROBE. The pick (derived, never pinned) and every
existing check stay exactly as they are; this is a capture-timing fix, not a flow change. Do not
touch tests/test_fit_queue.py (the 307/235 family) or the page. The pair always runs as one
invocation, A then B (PITFALLS: the B test cannot run in isolation).

1. **Stable captures.** Before the `4-saved` and `5-reload` screenshots (and any other view where
   the map can still be moving - the q1/q2 gesture samples included, where the pair flake shows up)
   wait for the map view to settle: e.g. wait for maplibre's `moveend`/`idle` after the last
   interaction, or disable the page's transitions in the test view.
2. **Prove the stability in one run.** Once settled, take the capture a second time and assert the
   two shots differ by <0.5% of pixels at threshold 32, so a mid-transition regression fails the
   test instead of dirtying PNGs (additive; no existing assert changes).
3. **Stop the unconditional in-checkout copy.** `_run_one` currently copies the ten fresh renders
   into `docs/site_flow/307d_<A|B>_<1..5>.png` on EVERY run and never compares them against the
   committed bytes. The fresh renders stay in the test's private temp tree (the test already asserts
   everything it needs from the temp tree). Copying into `docs/site_flow/` happens only on an
   explicit refresh - an env var or a pytest flag, named in the test's docstring - that re-renders
   all ten from a run and writes them into `docs/site_flow/`.
4. **The checkout's PNGs enter the write-surface proof.** Add the ten committed
   `docs/site_flow/307d_*.png` to `_write_surface`, so the existing "the run wrote into the
   checkout's shared store" assert proves an unflagged run left them byte-identical.
5. **Update the module and test docstrings** to the new regime: the ten PNGs are a pinned snapshot
   committed in the repo; an ordinary run never touches them; the named flag re-renders them.

## Acceptance criteria

- [ ] Two consecutive unflagged runs of `pytest tests/test_owner_check.py` on the same tree produce
      byte-identical (or <0.5% differing pixels at threshold 32) A_4/A_5/B_4/B_5 views in the temp
      tree (all ten stable, not just the four - the other six stay at their historical 0-1.25%
      encoding noise); both tests still pass end to end and the write-once / shared-store /
      golden-hash checks stay green.
- [ ] An unflagged run leaves every `docs/site_flow/307d_*.png` in the checkout byte-identical
      (verified by the test's write-surface hash or an equivalent check); the explicit refresh flag
      (the one named in the docstring) re-renders all ten from a run and writes them into
      `docs/site_flow/`.
- [ ] The pick is still derived and no existing check changed (same flow, same asserts); the settle
      wait and the double-shot stability assert are additive.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`) and
      `git status` on `docs/site_flow/` is clean after an unflagged run.
