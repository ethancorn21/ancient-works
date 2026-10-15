Status: in-progress
Depends on: 307d, 816, 230
Touches: tests/test_owner_check.py

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

(2026-10-15, iteration 236, agent a - **STATUS (read this first):** agent a now holds the
whole cycle (230/242/810/811/812/813/814); inter-deps count as met. The 195 first action
(the nine 307d PNGs) needed only TWO restores on THIS branch (B_4/B_5 - agent c's nine were
on c's branch): done, committed e484aa07, `git diff main -- docs/site_flow/` is empty. The
driver then CARRIED c's built fix into this branch (693b0ea3, from c@26853066 = 63a4e4e):
tests/test_owner_check.py on this branch is EXACTLY the 816 recipe (54 added / 0 changed vs
main, verified line-for-line at it.236; zero instrumentation residue). The 195/194 fix
description below therefore applies to the file verbatim (the 192 root-cause record -
integer-pixel marker rounding, the 1.06105 signature - stands). **Pair state at it.236:**
3 consecutive unflagged runs GREEN on this branch (64.5/65.9/66.7 s), zero [warn] settle,
ratio check [ok] in every run, and the cross-run compare (run2 vs run3) shows ALL TEN views
0.000% differing at threshold 32 - stricter than the 194 evidence. One NEW red surfaced
and was fixed in the PAGE (245: saveFit's one-shot sites.json fetch could land in the
119 ms depiction->re-score gap and adopt the stale tier - web/index.html now re-fetches
until the entry's `overlays` exceeds the pre-save value; committed ab57da1b). **Re-claim
when the driver returns this task (after 816 and 230 are on main):** the 195 NEXT list
below is the procedure; with the pair green on this branch it is a re-verification
formality - run the pair twice, compare, full suite (with 230 on main expect all green),
restore any re-rendered PNGs, claim. The 812 -> 813 rebuild (double shot + refresh flag,
from `git show 3579c22b:tests/test_owner_check.py`) comes BEFORE 810/811/242 per their
hand-overs; it does not change this file's 816-recipe diff.

<superseded 195 text (agent c) kept as the design record - everything factual in it still
holds; only the branch ownership and PNG list changed:

(2026-10-15, iteration 195, agent c) **SPLIT designed and mostly executed this session; NO code changed**
(the fix stays committed at 63a4e4e). Session cut by the context limit after the 230/815/241 edits, the
816 file and the DECISIONS/PITFALLS entries were still pending (check their current state first - the
harness saves uncommitted file edits; commit whatever is done: `git add DECISIONS.md tasks`).

**Why the split (the claim cycle, verified this session):** the 194 done-claim was REJECTED (the note in
DECISIONS): the driver's mechanical re-check counts the roman test red -
tests/test_src_roman_maclauchlan.py::test_check_staged_joins_and_passes, verified RED again this session
(2.29 s: "join: staged site luguvallium-q71551754 differs from its canonical row in extras.jsonl") - as a
new red on this branch. The 194 no-new-reds argument (the red is 230's in-flight data on main, not this
file) still stands, but re-claiming today fails identically: the red clears only when 230 merges, and 230's
claim was HELD on this task's old chain (its Depends carried 242, 810, 812, 813, 814) - a formal wait cycle
(814's gate needs 230 on main; 230's claim needed the chain that starts at 814): the driver's forbidden
"a task must not wait, directly or through others, on a task that waits on it". Hence the 195 split:
- **816 (new file, lowest free number in 800-1099)** = this built fix republished as an independently
  claimable part: its recipe is the EXACT committed diff (generate it: `git diff main 63a4e4e --
  tests/test_owner_check.py` = 54 added / 0 changed against the CURRENT main file - verified this session:
  main's file has zero settle/subpixel lines, so the diff applies verbatim to any branch); Depends: done
  307d only -> claimable immediately (agent a, whose checkout already carries 230's data, so its suite gate
  has no roman red). Once merged, the pair is stable on every branch.
- **230** Depends re-pointed `211, 207a, 207b, 807, 808, 242, 810, 812, 813, 814` -> `211, 207a, 207b,
  807, 808, 816` + a dated note in its Notes (its done-claim gate was red on exactly its own data (fixed on
  its branch, boxes ticked it.215) + the owner_check flake (= 816); the per-run 307d PNG re-render fails no
  test - the R5 restore discipline covers the dirt - so the chain no longer HOLDS it; the old line closed
  the cycle). The "Next session (returned after 242 merged)" block there is stale in its trigger only:
  return is now after 816.
- **241 (mine)** Depends `240, 242, 810, 812, 813, 814` -> `240, 230` + 195 note in its Hand-over: its claim
  (all five boxes ticked; staging complete at 188) needs 230's data on main (the roman red), not the chain -
  this branch already carries the fix (63a4e4e, byte-identical to 816's), so the pair is green here with or
  without the chain; it claims right after 230, then 236c consolidates the 25-city total.
- **815** Depends `814` -> `307d, 816` + one-line note: the page-side subpixel (web/index.html) then builds
  IN PARALLEL with the chain (disjoint file).
- **814 (this)** now Depends on `307d, 816, 230` (edit done this session) and claims once both are on main.
Graph (re-verified acyclic over every open Depends line): 816 -> 307d (done); 230 -> 816; 814 -> {816, 230};
812 -> 814; 813 -> 812; 810 -> {812, 813}; 811 -> 810; 242 -> {810, 811}; 815 -> 816; 241 -> 230;
236c -> 241. Nothing waits on a task that waits on it - the "never both ways" rule holds (814 waiting on
816/230 is fine because neither waits back, directly or transitively). Expected order: agent a takes 809
(lowest claimable) and/or 816 -> 816 merges -> 230 returns and claims (its suite then all green) -> 230
merges (roman red OFF main) -> 814 re-claims (below) -> 812 -> 813 -> 810 -> 811 -> 242; 815 and 241 -> 236c
in parallel.

**THE FIRST ACTION OF THE NEXT 814 SESSION (discovered this session, NOT yet done):** nine of the ten
docs/site_flow/307d_*.png on THIS branch (A_1..A_5, B_2..B_5 - B_1-card matches main) differ byte-wise from
MAIN's (the 193-era re-encoded bytes got committed in 63a4e4e; 194's "restore to the index" restored to
index bytes that were themselves not main's - `git diff main HEAD -- docs/site_flow/` shows the 9). A
merge of this branch into main would BINARY-conflict all nine (the b14918f precedent). Fix before any
commit/claim: `git checkout main -- docs/site_flow/307d_A_1-card.png 307d_A_2-placed.png 307d_A_3-gestured.png
307d_A_4-saved.png 307d_A_5-reload.png 307d_B_2-placed.png 307d_B_3-gestured.png 307d_B_4-saved.png
307d_B_5-reload.png` (only those nine; B_1-card and the rest already match), verify
`git diff main HEAD -- docs/site_flow/` is empty, commit. (The pixels are stable per 194; only the
re-encoding bytes differ. 813's refresh flag retires the re-render itself once it lands.)

**The fix (unchanged since 194; 63a4e4e = the 816 recipe, byte-identical):** probe-side `settle()` (poll
`!map.isMoving()` at 150 ms, 20 s budget, `[warn]` on timeout) + `subpixel()` (per live marker in `P.marks`:
`setSubpixelPositioning(true)` - public vendored MapLibre 5.6.0 API - + one forced `setLngLat(m.getLngLat())`),
each called after ALL EIGHT settle sites (the q0/q1/q2 reads and the five shots). Root cause (192, journaled):
the q1/q2 flake is NOT a moving camera (settled to 10-digit zoom, zero camera events between reads) - it is
MapLibre's default integer-pixel marker rounding (true q1 edge 82.9807 read 82.0, true q2 edge 87.1384 read
87.0057 -> 1.06105 vs true 1.0501; the exact value 230/239/241 recorded); `_fkApply` (web/fitkit.js ~215)
recreates the markers with the fresh false default on each s+/r+ step, so subpixel() re-runs per read. Delta
vs the pre-fix file: 54 added / 0 changed; no check, assert, flow or picker touched.

**Evidence carried forward (194, on the committed tree):** two consecutive unflagged pair runs green
(66.06 s / 66.63 s, the driver's own invocation); run-vs-run all ten views: A_4/A_5/B_4 byte-identical,
B_5-reload 0.0073%, the rest at/below the 0.0447% historical band (the 28.6-33.6% drift gone); probe logs
every check `[ok]`, zero `[warn] settle`, the ratio check `[ok]` in every captured run (192: red 4/4
without the fix; 193-194: green 6/6); full suite 188 passed / 1 skipped / 1 failed (the roman red, cross-
lane). Compare-script pattern for re-verification: 20-line PIL diff counting pixels differing by >32 on
any channel, report the fraction per view.

**NEXT (when the driver brings 814 back - it should not return before 816 AND 230 have merged; confirm both
in `git log --oneline main -15`):** 0) the PNG restore above (if still dirty vs main); 1) two consecutive
unflagged pair runs (one invocation each: `.venv/bin/python -m pytest tests/test_owner_check.py -q -p
no:cacheprovider`), both green, zero `[warn] settle`, ratio check `[ok]` in each log; 2) compare all ten
views run-vs-run (the 242 metric): A_4/A_5/B_4/B_5 byte-identical or <0.5%, the other six at/below 0-1.25%;
3) `git diff main -- tests/test_owner_check.py`: expect 0/0 (the fix reached main via 816) or the identical
54/0 - either way the pick is derived and no check changed; 4) full suite
(`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`): with 230 on main, expect ALL green; restore
any re-rendered 307d PNGs to main's bytes before committing (R5; 813 retires this); 5) claim done (boxes
already ticked; record the re-verification in DECISIONS). If the pair reds TWICE on re-verification: a
defect in the fix (816's content) -> file `## Proposed changes` here with the run evidence and stop claiming
(the 241-188 path). Never weaken or delete a test to clear a red.

**Re-read (fresh eyes, for the next agent taking this file - 812 is next in the chain):**
- tests/test_owner_check.py:PROBE `subpixel` - runs after each of the 8 settles; no TEMP instrumentation
  leaked back (grep `TEMP|camlog|__cam|dumpHandles` must be empty - verified empty this session)
- web/fitkit.js `_fkApply`/`_fkScheduleApply` - why subpixel() must re-run per read
- web/vendor/maplibre-gl-5.6.0.js - search `setSubpixelPositioning` and `_subpixelPositioning||` (the two
  vendor lines the fix hinges on)
- tasks/816-*.md - the recipe this file's committed fix was republished from; after 816's claim, this
  file's diff against main is 0/0
- PITFALLS "test_owner_check re-renders all ten 307d golden PNGs ..." - 813 rewrites its What-to-do for the
  refresh-flag regime; its history lines (incl. the per-checkout pytest retention facts) stay
