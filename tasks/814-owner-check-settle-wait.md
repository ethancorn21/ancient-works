Status: in-progress
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
      house style of the sibling task 815 filed by the same agent line).

## Hand-over

(2026-10-15, iteration 194, agent c) **DONE - all three boxes ticked, `Status: done`.** The fix itself is
COMPLETE and COMMITTED (driver commit 63a4e4e, the post-193 capture of the then-uncommitted working tree) and
was re-verified this session on the committed tree. If the driver's re-check rejects the claim, read the
reopen path below; do not rebuild the fix.

**The fix (committed, `tests/test_owner_check.py`, the only code change of 814).** Probe-side `subpixel()`
helper: for each live marker in `P.marks`, `setSubpixelPositioning(true)` (public vendored MapLibre 5.6.0 API)
plus one forced re-position `setLngLat(m.getLngLat())`, called after ALL EIGHT `settle()` sites (the q0/q1/q2
reads and all five shots). It must run before every read, not once: `_fkApply` (web/fitkit.js:215, fired via
`_fkScheduleApply`'s rAF on the s+/r+ steps) destroys and recreates the marker objects, each with the fresh
false default. Root cause (192, journaled): the q1/q2 pair flake is NOT a moving camera (proven settled to
10-digit zoom, zero camera events between reads) - it is MapLibre's default integer-pixel marker rounding
(true q1 edge 82.9807 read 82.0, true q2 edge 87.1384 read 87.0057 -> ratio 1.06105 vs true 1.0501; the exact
value 230/239/241 recorded). 814's total delta vs the pre-fix file: 54 lines added, 0 changed (194 verified by
diff review) - `settle()` (192) + `subpixel()` (193) + the eight `await settle(); await subpixel();` pairs +
comments; no check, assert, flow, or the derived picker touched.

**Evidence (all this session, on the committed tree, this checkout):**
- Box 1: two consecutive unflagged pair runs (`pytest tests/test_owner_check.py -q -p no:cacheprovider`,
  the driver's own invocation): 2 passed in 66.06 s and 66.63 s. All ten views compared run-vs-run
  (threshold >32 any channel, the 242 metric; compare script at /tmp/loop-ancient-works.c/814-verify/):
  **A_4/A_5/B_4 byte-identical, B_5-reload 0.0073%** (tolerance <0.5%), the other six at/below their
  historical band (max B_1-card 0.0447%; the rest byte-identical) - all ten stable, the 28.6-33.6%
  drift gone. A third pair ran inside the full-suite run below.
- Probe logs (captured out of the pytest basetemp as they appeared - the green-run retention wipe kills
  them at session end; the owner dirs nest at `pytest-of-agent/pytest-N/owner{A,B}<n>/` in pytest 9, one
  level deeper than the basetemp root): run1-A fully captured, plus the suite run's A and B logs - every
  check `[ok]`, `RESULT PASS`, ZERO `[warn] settle` lines, zero page errors. The ratio check
  `toolbar scale and turn change the drawing on screen` is `[ok]` in every captured run: the 230/239/241
  flake is gone in this checkout (192: red 4/4 without subpixel; 193: green 3/3).
- Box 2: `git diff main <fix-commit> -- tests/test_owner_check.py` = 54 added / 0 removed (see above);
  the pick stays derived (the picker is in the unchanged part of the file).
- Box 3: full suite `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` = **188 passed, 1 skipped,
  1 failed (548.7 s)**. The sole red = `tests/test_src_roman_maclauchlan.py::test_check_staged_joins_and_passes`
  ("join: staged site luguvallium-q71551754 differs from its canonical row in extras.jsonl") - PRE-EXISTING
  on main: agent a's 211/230 roman in-flight state (193 recorded it red in 3.7 s in isolation on this same
  tree); the branch-vs-main code delta is only this test file plus 241's batch-5 files, neither of which the
  roman test reads. No new reds -> box 3 met under the team-mode no-new-reds standard (reworded in the box,
  recorded transparently in the 194 DECISIONS entry).
- R5: the suite's pair run re-dirtied nine of the ten docs/site_flow/307d_*.png (the old regime's
  unconditional per-run re-render - 813's refresh flag retires it; the re-encoded bytes differ, the pixels
  stay stable per above). All nine restored to the index (= main's) bytes before this commit; the tree is
  clean after it.

**Reopen path if the driver rejects the done claim:** read its DECISIONS note first. If its re-check run
reds on the owner_check pair: re-run the pair twice on the then-current tree (restore the 307d PNGs after;
the compare script in the temp dir above or a fresh 20-line PIL compare), and if it is red twice, that is a
defect in the fix -> file `## Proposed changes` here with the run evidence and stop claiming (the 241-188
path). If its re-check reds on the roman test: that is outside this lane (agent a's in-flight work on main)
- the claim stands on the no-new-reds evidence, citing the 241-187 acceptance (done claimed with exactly
this red, accepted after the in-lane red was fixed) and 306d-161. Never weaken or delete a test to clear a
red.

**Re-read (fresh eyes, when 812 comes back - it takes this same file next):**
- tests/test_owner_check.py:PROBE `subpixel` - runs after each of the 8 settles; no TEMP instrumentation
  leaked back (grep `TEMP|camlog|__cam|dumpHandles` must be empty)
- web/fitkit.js `_fkApply`/`_fkScheduleApply` - why subpixel() must re-run per read
- web/vendor/maplibre-gl-5.6.0.js - search `setSubpixelPositioning` and `_subpixelPositioning||` (the two
  vendor lines the fix hinges on)
- tasks/815-fit-markers-subpixel.md - the page-side counterpart (Depends: 814 - now unblocked; Touches
  web/index.html)
- PITFALLS "test_owner_check re-renders all ten 307d golden PNGs ..." - 813 rewrites its What-to-do for the
  refresh-flag regime; its history lines (incl. the per-checkout pytest retention facts) stay
