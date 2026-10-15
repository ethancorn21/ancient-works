Status: in-progress
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

(2026-10-15, iteration 242, agent a - **STATUS (read this first): the settle+subpixel fix is on
MAIN - via the driver's 693b0ea3 takeover carry, NOT via 816 - and this branch's file is 0/0
against it. 230 is done; 817/818 are on main (the roman red that rejected the 194 claim is
dead); 816 is still OPEN with a now-0/0 recipe. This session re-verified everything on the
current tree: ALL GREEN (three unflagged pair runs, full suite 194/1/0). The claim is ONE step
away and is held only for 816's close (a ## Proposed changes is filed on the 816 file
recommending a no-op close). NEXT session, once 816 is done: confirm the 0/0 diff, one fresh
pair run as run-4, restore the PNGs, claim done.)

**Tree state (verified by running, it.242):** `git diff main -- tests/test_owner_check.py` =
0/0. Main's file (top history entry 693b0ea3 "[driver] 814 taken over from agent c: its work
carried (c@26853066)") carries the exact fix: probe-side `settle()` (poll `!map.isMoving()`
at 150 ms, 20 s budget, `[warn]` on timeout) + `subpixel()` (per live marker:
`setSubpixelPositioning(true)` + one forced `setLngLat` re-position), each after ALL EIGHT
settle sites (the q0/q1/q2 quad reads and the five shots); re-run per read because `_fkApply`
(web/fitkit.js ~215) recreates the markers with the fresh false default on every s+/r+ step.
Box 2 (the pick is derived, no check changed) holds by construction: the file is unchanged
on any branch since 63a4e4e (192-194 proved it 54 added / 0 changed), and this session's runs
re-derived the same picks as 192-194 (A = richard-s-castle-q17650937 /
earthworkenglan01allcgoog_n0453_1, bar scale; B = devil-s-dyke-q3307343 /
earthworkenglan01allcgoog_n0662_1, site-size-only; both still LiDAR relief).

**Re-verification evidence (this session, this tree = main in code; the only branch-vs-main
deltas at session start were three re-encoded 307d PNGs):**
- Three consecutive UNFLAGGED pair runs (the driver's exact invocation
  `.venv/bin/python -m pytest tests/test_owner_check.py -q -p no:cacheprovider`):
  70.39 s / 75.11 s / 69.70 s, all `2 passed`. Every captured probe log (A of runs 1-3, B of
  run 3): all 14 checks `[ok]` + "no page errors" + RESULT PASS, zero `[warn] settle`, ratio
  check `[ok]`. The B logs of runs 1-2 were lost to their ~1 s window (new PITFALLS entry
  under tests/playwright); B's end-to-end pass proves its checks passed (a red probe fails
  the test via the RESULT assert).
- Cross-run compare (threshold >32 any channel, the 242 metric): run1 vs run2 - ALL TEN
  views byte-identical except B_5-reload 0.0007%; run2 vs run3 - B_1-card 0.0447% (the
  card-view jitter band) and B_5 0.0003%, the other eight byte-identical. The 28.6-33.6%
  mid-transition drift (the original 199/242 symptom) stays dead on this tree.
- Full suite (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`): 194 passed /
  1 skipped / 0 failed in 598.85 s - ALL green. The 194-claim-rejection red (roman
  test_check_staged_joins_and_passes) is dead (817/818's _canon_norm checked-date zeroing;
  207's box-4 at 4284ed7b verified zero join lines), and the 2026-10-11/13 known reds
  (batch_eu x2, test_serve, fit_queue placement_gestures) are gone too. Box 3 satisfied
  under its strictest reading.
- PNG discipline (R5): A_1 (0.045%), B_1 (0.045%), B_5 (0.128% at HEAD, 0.0026% at the then
  working tree) were dirty vs main at session start - pixel-verified pure re-encodings
  (same picks, sub-jitter); restored to main's bytes (docs/site_flow/307d_*.png added to
  this task's Touches for that). The full suite re-rendered A_1/B_5 (B_1 came out
  byte-identical to main in that run) - restored again before the commit, so
  `git diff main -- docs/site_flow/` is empty at commit time.

**Why the claim is held (not this session):** the driver's note for this forced start lists
816 as the only unfinished dependency, and the 195 design says 814 claims once 816 AND 230
are on main (230 is; 816's file is still open although its content is on main - see its
Proposed changes). 194's claim was rejected on a cross-lane red; that red is now dead, but
re-claiming while 816 is open risks the driver's mechanical dependency gate - do not claim
ahead of it.

**NEXT (when the driver returns this task - it should come back after 816 is done; confirm
`git log main -10` shows the 816 close or its file says done):** 1) `git diff main --
tests/test_owner_check.py` still 0/0 and `git diff main -- docs/site_flow/` empty (if
dirty: `git checkout main -- docs/site_flow/307d_*.png`); 2) ONE fresh unflagged pair run as
run-4 evidence - rig: background-launch the driver's exact invocation and run a 0.1 s
os.walk watcher over `$TMPDIR/pytest-of-agent/` that copies each `pytest-*/owner{A,B}0/
owner_probe.log` out the moment it appears (a green run rmtree's the whole basetemp at
session end and the B log window is ~1 s: the new PITFALLS entry under tests/playwright has
the recipe; /tmp trees do not survive session boundaries, so recreate the two ~20-line
scripts from it); check `2 passed`, zero `[warn] settle`, ratio check `[ok]` in both logs;
3) compare its ten views against run3's (the snapshots: `snap/` per run) - A_4/A_5/B_4/B_5
byte-identical or <0.5%, the rest at/below the 0-1.25% band; 4) restore the PNGs (R5);
5) claim done (all boxes already ticked; record the claim in DECISIONS). If the pair reds
TWICE at step 2: a defect in the fix (816's content) -> file `## Proposed changes` HERE with
the run evidence and stop claiming (the 241-188 path). Never weaken or delete a test to
clear a red.

**Re-read (fresh eyes; 812 is next in the chain and shares this file):**
- tests/test_owner_check.py:PROBE settle/subpixel - the eight call sites; no TEMP
  instrumentation leaked (`grep -E "TEMP|camlog|__cam|dumpHandles"` - verified empty it.242)
- web/fitkit.js `_fkApply`/`_fkScheduleApply` - why subpixel() must re-run per read
- web/vendor/maplibre-gl-5.6.0.js - `setSubpixelPositioning` and `_subpixelPositioning||`
  (the two vendor lines the fix hinges on)
- tasks/816-*.md (its Proposed changes) and tasks/812-813 (the chain after this)
- PITFALLS "test_owner_check re-renders all ten 307d golden PNGs..." (the 242-supersession
  parenthetical was corrected it.242: the settle half is on main via 693b0ea3; the
  refresh-flag half is 813's) and the new "B probe log ~1 s window" entry
