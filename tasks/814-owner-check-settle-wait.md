Status: done
Depends on: 307d, 816, 230
Touches: tests/test_owner_check.py, docs/site_flow/307d_*.png (R5: restoring suite re-encodes to
main's bytes before committing - never content changes), PITFALLS.md

# 814: The 307d owner check - settle the map view before every capture (the mid-transition flake fix)

Part 1 of 812's split (2026-10-15, iteration 191): the flake fix out of 812, the settle
wait. Built and committed at 192-194 (driver commit 63a4e4e); its done-claim was rejected
2026-10-15 on a cross-lane red (the roman test - 230's data state on main; the 194 no-new-reds
argument stands, but the driver's mechanical gate does not read it - see the hand-over).
Re-split again at 195 (driver instruction: agent a had had nothing to build for 43 minutes
while every waiter was held on this one task): the built fix is republished as **816**
(Depends: done 307d only - claimable immediately; the exact committed diff is its recipe),
this task now Depends on 307d, 816 and 230 and claims once both are on main, and the
waiters' lines were re-pointed off the chain (230 -> 816; 241 -> 240 + 230; 815 -> 307d +
816) per the driver's "never both ways" rule - the hand-over carries the full graph and the
expected order. 812 (narrowed to the in-run double-shot stability assert that proves this
fix; Depends: 307d, 814; same file) runs after this; 813 (the pinned-snapshot regime; same
file) runs after 812; 810 keeps the final verification and waits on 812 + 813; 811 then 242
wait on 810. Chain (landing order): 816 -> 230 -> 814 -> 812 -> 813 -> 810 -> 811 -> 242,
with 815 and 241 -> 236c in parallel. The waiters were held on the mid-transition flake this
part fixes (230: the owner_check A/B pair red a 3rd consecutive time at it.214-216, its
done-claim gate; 241: red at it.187/188). Background: 242's goal and the 2026-10-14 307bc
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

- [x] Two consecutive unflagged runs of `pytest tests/test_owner_check.py` on the same tree
      produce byte-identical (or <0.5% differing pixels at threshold 32) A_4/A_5/B_4/B_5
      views in the temp tree (all ten stable, not just the four - the other six stay at
      their historical 0-1.25% encoding noise); both tests still pass end to end and the
      write-once / shared-store / golden-hash checks stay green.
- [x] The pick is still derived and no existing check changed (same flow, same asserts); the
      settle wait is additive.
- [x] The full suite shows no new red against main
      (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`). The original wording
      ("the full suite is green") is unreachable on a team-mode branch: the driver merges
      main - carrying agent a's in-flight roman reds - into this branch before every
      session, and that red is not this task's file. Reword 2026-10-15 (iteration 194)
      to the driver's own re-check standard for an agent's own task ("no test failing
      that was not already failing before"; the 306d and 241-187/188 precedents, and the
      house style of the sibling task 815 filed by the same agent line). At claim time
      (195: after 816 and 230 have merged, the roman red is off main) the suite is expected
      to be all green, which satisfies even the strictest reading.

## Hand-over

(2026-10-15, iteration 244, agent a - **STATUS: DONE claimed this session.** 816 is closed
(e7c3a75e, no-op verification: four unflagged pair runs + full suite 194/1/0 on this exact
tree), so the last held dependency is gone. Everything in the it.244 DECISIONS entry is this
session's re-verification on this tree (= main in code; the owner file is 0/0 vs main):
three fresh unflagged pair runs (67.2 s / ~72 s / "2 passed in 72.80s"), both captured log
pairs 16 [ok] / 0 [warn] / RESULT PASS with the ratio check [ok] in all four logs and the
derived picks unchanged (A richard-s-castle-q17650937 / earthworkenglan01allcgoog_n0453_1,
bar scale, LiDAR; B devil-s-dyke-q3307343 / earthworkenglan01allcgoog_n0662_1,
site-size-only, SWEALD, LiDAR); run-vs-run 8-9 of ten views byte-identical (worst B_5
0.0006%, B_1 0.0447% = the historical card-view jitter band); vs main's goldens all ten
<=0.0451% (at/below the 0-1.25% encoding-noise band); full suite at claim time
194/1/0 in 865 s (contention-slowed, all green); the two dirty 307d PNGs were
pixel-verified pure re-encodes (A_1 0.0451%, B_5 0.0026% - the 242 numbers) and restored to
main's bytes, again after the suite (R5) - the commit carries only the memory-file deltas
plus that alignment. Box 2 holds by construction (file unchanged since the 63a4e4e/693b0ea3
build; 54 added / 0 changed, 192-194). Total since the fix landed on main: ten consecutive
green pair runs (242: 3, 816: 4, 244: 3), zero [warn] settle in every captured log.
Nothing left to build on this task. If the driver re-checks: boxes were ticked before and
remain valid (box 1 and 3 re-measured this session as above).

**For 812/813 (next in the chain, same file):** the tree is at main's bytes for
tests/test_owner_check.py and all ten docs/site_flow/307d_*.png; the settle()/subpixel()
probe code (eight call sites: the q0/q1/q2 quad reads + the five shots) is the baseline the
812 stability assert builds on.

Re-read (fresh eyes):
- tests/test_owner_check.py:PROBE settle/subpixel - the eight call sites; no TEMP
  instrumentation leaked (`grep -E "TEMP|camlog|__cam|dumpHandles"` - verified empty it.242,
  and the file is 0/0 vs main so it cannot have changed since)
- web/fitkit.js `_fkApply`/`_fkScheduleApply` - why subpixel() must re-run per read
- web/vendor/maplibre-gl-5.6.0.js - `setSubpixelPositioning` and `_subpixelPositioning||`
  (the two vendor lines the fix hinges on)
- PITFALLS "test_owner_check probe logs..." (the 0.1 s watcher recipe) plus its it.244
  addendum: the copy-out key must be FLATTENED (relpath with os.sep replaced) - with
  `pytest-0/ownerA0` the destination parent dir does not exist, copy2 raises
  FileNotFoundError into the wipe-race except, and the watcher loses every log silently
  (814 run-4: a whole 67 s run's logs gone, zero output). Test any watcher against a
  hand-created file before trusting it on a real run.
- tasks/812-813 (the chain after this) and the it.244 DECISIONS entry for the full run
  evidence
