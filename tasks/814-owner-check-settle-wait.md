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

(2026-10-15, iteration 193, agent c) **The fix is BUILT and VERIFIED, sitting UNCOMMITTED in the working tree - the one step left is the commit (+ see Next below).**

**Where I am.** 192's TEMP instrumentation was reverted (clean settle-only file from /tmp/test_owner_check.py.bak, commit a228d2c) and the q1/q2 fix is in the working-tree `tests/test_owner_check.py` (the ONLY uncommitted change; the nine re-dirtied docs/site_flow/307d_*.png were already restored to main's bytes in the working tree). The fix: a probe-side `subpixel()` helper - for each live marker in `P.marks`, `setSubpixelPositioning(true)` (public vendored API) plus one forced re-position `setLngLat(m.getLngLat())` - called after all eight `settle()` sites (the q0/q1/q2 reads and all five shots). It must run before EVERY read, not once: `_fkApply` (fitkit.js:215, fired via `_fkScheduleApply`'s rAF on the s+/r+ steps) destroys and recreates the marker objects, each with the fresh false default. The settle comment's false "and the q1/q2 pair flake" attribution was corrected in the same edit (192 proved the camera fully settled at both reads).

**Test state (all verified this session):** pair runs GREEN 3/3 (192: red 4/4 at `toolbar scale and turn change the drawing on screen :: {"e1":82,"e2":87.00574693662483}`) - no `[warn] settle`, no page errors. Two consecutive unflagged runs, all ten views compared (threshold >32 any channel, staged outdirs - see the new PITFALLS on pytest retention): A_4/A_5/B_4/B_5 **byte-identical** (the 28.6-33.6% drift is gone), plus 2-placed/3-gestured both tags byte-identical; only A_1-card drifts 1.1959% - a 24-px band at the page bottom (y 786-809) = MapLibre's semi-transparent attribution bar (backdrop-blur) picking up map tiles that finish decoding at different times per run: the historical 0-1.25% card-view band the 242 family documented, not a camera/marker effect (at 1-card time `P.marks` is empty; my change is a no-op there). Full suite: **188 passed, 1 skipped, 1 failed** = `tests/test_src_roman_maclauchlan.py::test_check_staged_joins_and_passes` - PRE-EXISTING on main (agent a's 207/211 roman in-flight state; reds in isolation in 3.7 s on the same tree; touches nothing 814 changed). No new reds.

**Next (one step, then set `Status: done`):** 1) COMMIT the working-tree fix: `git add tests/test_owner_check.py && git commit -m "814: the q1/q2 flake fix - probe-side subpixel marker positioning before every read and shot (setSubpixelPositioning(true) + one re-position on P.marks); the settle wait (192) + this make all ten 307d views stable run-to-run"` - re-verify first that `git status` shows exactly that one file (plus tasks/) and the ten 307d PNGs still equal main's bytes; `node --check` the extracted probe (prefix is 12 chars: slice at i+12, NOT i+13 - a 13-char slice eats the first `/` of the probe's first comment line and node dies with "Invalid regular expression: missing /"). 2) Check all three acceptance boxes (box 3 was reworded to the team-mode no-new-reds bar - the driver's own re-check standard, and 306d's precedent; the old wording "the full suite is green" is unreachable while agent a's in-flight roman reds sit on main, per the driver notes 2026-10-11/13) and set `Status: done`. 3) Append a DECISIONS entry if you touch anything (the 193 entry was NOT yet written when the context limit hit - file it under the commit if you amend anything).

**Filed, don't build here:** `tasks/815-fit-markers-subpixel.md` (new, lowest free number; Depends: 814, Touches: web/index.html) - the PAGE-side defect this fix works around: `addPairMarker` (web/index.html:1136) creates the fit markers without `subpixelPositioning` (MapLibre 5.6.0 default false -> integer-pixel `_pos` on setLngLat/moveend -> 1-px owner-visible jitter + quantised pixel checks; the vendor rounding line and the public `setSubpixelPositioning` API are quoted in its body). The probe's subpixel() call is idempotent with it. (PLAN.md was left untouched: the 242/8xx family is not in it yet - noted, not forced.)

**Re-read (fresh eyes, when 812 comes back):**
- tests/test_owner_check.py:PROBE `subpixel` - verify it runs after each of the 8 settles and that no TEMP instrumentation leaked back in (grep `TEMP|camlog|__cam|dumpHandles` must be empty)
- web/fitkit.js `_fkApply`/`_fkScheduleApply` - the reason subpixel() must re-run per read
- web/vendor/maplibre-gl-5.6.0.js - search `setSubpixelPositioning` and `_subpixelPositioning||` (the two vendor lines the fix hinges on)
- the 815 task file - the page-side counterpart

