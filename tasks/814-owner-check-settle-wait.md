Status: open
Depends on: 307d
Touches: tests/test_owner_check.py

# 814: The 307d owner check - settle the map view before every capture (the mid-transition flake fix)

Part 1 of 812's split (2026-10-15, iteration 191, driver instruction: agent a had nothing to
build for 76 minutes, and every open task in the chain waited on 812 alone): the flake fix
out of 812, the settle wait. Depends only on done 307d, so it is STARTABLE IMMEDIATELY - the
first claimable unit of the 242 family again. 812 (narrowed to the in-run double-shot
stability assert that proves this fix; Depends: 814; same file) runs after this; 813 (the
pinned-snapshot regime; same file) runs after 812; 810 keeps the final verification and
waits on 812 + 813; 811 then 242 wait on 810. Chain: 814 -> 812 -> 813 -> 810 -> 811 -> 242
-> {230, 241} -> 236c. The waiters 230 and 241 carry this number on their Depends lines
directly - they are held on the mid-transition flake this part fixes (230: the owner_check
A/B pair red a 3rd consecutive time at it.214-216, its done-claim gate; 241: red at
it.187/188). Background: 242's goal and the 2026-10-14 307bc DECISIONS entry (now in the
archive); the drift is measured, not guessed:

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

In tests/test_owner_check.py and its embedded PROBE. The pick (derived, never pinned) and
every existing check stay exactly as they are; this is a capture-timing fix, not a flow
change. Do not touch tests/test_fit_queue.py (the 307/235 family) or the page (the served
private tree the test already builds is the place to intervene, not web/index.html or
web/fitkit.js on disk). The pair always runs as one invocation, A then B (PITFALLS: the B
test cannot run in isolation).

1. **Stable captures.** Wherever the map can still be moving at capture time, wait for the
   map view to settle first: the quad reads q0 (after the place chain), q1 (after the drag),
   q2 (after the toolbar scale/turn) - where the pair flake shows up - and the `2-placed`
   shot and the `4-saved` / `5-reload` shots, which follow the 4.5 s flyTo + 900 ms
   fitBounds chain (the reload re-fires the flyTo via the deep link). The `1-card` and
   `3-gestured` shots measured stable (0-1.25%) but a uniform settle before all five shots
   is fine if it is cheap. Mechanism options: the page exposes the maplibre `map` global to
   `page.evaluate` (the probe already reads `map.getCanvas()` / `map.project`), so e.g. wait
   on `!map.isMoving()` / a `moveend` event with a timeout after each interaction chain, or
   run the page with its camera transitions disabled in the test view (zero durations in the
   served tree). Keep any wait bounded (a timeout must not hang the test).

## Acceptance criteria

- [ ] Two consecutive unflagged runs of `pytest tests/test_owner_check.py` on the same tree
      produce byte-identical (or <0.5% differing pixels at threshold 32) A_4/A_5/B_4/B_5
      views in the temp tree (all ten stable, not just the four - the other six stay at
      their historical 0-1.25% encoding noise); both tests still pass end to end and the
      write-once / shared-store / golden-hash checks stay green.
- [ ] The pick is still derived and no existing check changed (same flow, same asserts); the
      settle wait is additive.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).

## Hand-over

(2026-10-15, iteration 235, agent a) **BUILT on agent/a's branch with 812 + 813 in the same
file (tests/test_owner_check.py), uncommitted until 810's session commits.** The settle:
`owner_served` patches the SERVED tree's private copies only (on-disk web/ untouched) - zeroes
the four owner-flow camera transitions (the 4.5 s site flyTo index.html:874, the 900 ms
endFit/openPlan easeTos index.html:906/983, the 900 ms fitBounds fitkit.js:573) with `count ==
1` anchor asserts that fail loudly if the page edits, and injects `window.__awSettle =
{ idle: false }` plus render/idle listeners before the unique `map.once('load', ...)` anchor.
The probe's `settle(label)` waits on that flag (30 s timeout, proceeds + logs `[settle] ...`
or `[settle] ... TIMED OUT`) before every q0/q1/q2 read and every shot. Why idle: maplibre
5.6.0 fires `idle` exactly when the camera is at rest and the event-driven render loop has no
pending frame - verified 2026-10-15 on this build (/tmp/mplib_probe: after the 4.5 s + 900 ms
chain the camera kept moving to ~8 s and frames to ~9.5 s, one `idle` at 9.49 s, then zero
events for 20 s) - so the old fixed sleeps always landed mid-transition (the 28.6-33.6%
saved/reload drift, the 1.06105 q1/q2 pair flake). Pick still derived; no existing check
changed. **Boxes unticked**: 810's session (next) runs the pair twice + the full suite and
ticks these boxes per 810's hand-over (the work itself is complete); when the driver returns
this task, re-confirm the suite green and claim. Design rationale in DECISIONS.md "2026-10-15
810 DECISION". The pre-run "restore the re-rendered PNGs" workaround is RETIRED by 813 (an
unflagged run no longer touches docs/site_flow/ at all).
