Status: in-progress
Depends on: 307d, 814
Touches: tests/test_owner_check.py

# 812: The 307d owner check - prove the settle with an in-run double shot (the stability assert)

Narrowed by its own split (2026-10-15, iteration 191, driver instruction: agent a had nothing
to build for 76 minutes, and every open task in the chain waited on this task alone): the
flake fix (the settle wait) moved to **814** (Depends: done 307d, startable immediately), and
this task keeps the other half of what it was created with - the in-run double-shot
stability assert that proves the settle in a single run. Runs after 814 (same file; the
double shot passes only once the captures are settled); 813 (the pinned-snapshot regime on
the same file) runs after this; 810 keeps the final verification and waits on this + 813;
811 then 242 wait on 810. Chain: 814 -> 812 -> 813 -> 810 -> 811 -> 242 -> {230, 241} ->
236c. The waiters 230 and 241 carry 814 (the flake fix) and this number on their Depends
lines. Background: 814's header (the measured drift, the pair flake) and 242's goal; the
2026-10-14 307bc DECISIONS entry (now in the archive).

## Goal

In tests/test_owner_check.py and its embedded PROBE. The pick (derived, never pinned) and
every existing check stay exactly as they are; this is a capture-timing proof, not a flow
change. Do not touch tests/test_fit_queue.py (the 307/235 family) or the page. The pair
always runs as one invocation, A then B (PITFALLS: the B test cannot run in isolation).

1. **Prove the stability in one run.** Once 814's settle is in, take each of the ten views
   (the five screenshots per run - 1-card, 2-placed, 3-gestured, 4-saved, 5-reload - for A
   and B) a second time, right after the settled shot, and assert the two shots differ by
   <0.5% of pixels at threshold 32 - so a mid-transition regression fails the test instead
   of dirtying the PNGs (additive; no existing assert changes). The probe (node) writes
   both shots per view into the run's outdir; the pixel comparison is on the Python side of
   the test (there is no reusable pixel-diff helper in the repo - 307bc measured with a
   throwaway script; PIL is in the .venv).

## Acceptance criteria

- [x] With 814 merged, the in-run double-shot assert covers all ten views (five per run, A
      and B) and passes: the two settled shots differ by <0.5% of pixels at threshold 32
      (the other six views stay at their historical 0-1.25% encoding noise, comfortably
      under the line); a mid-transition regression fails the test instead of dirtying the
      PNGs.
- [x] The pick is still derived and no existing check changed (same flow, same asserts); the
      double-shot assert and its second shots are additive.
- [x] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).

## Hand-over

(2026-10-15, iteration 245, agent a - context-limit cut right before the final commit; all
build + verification work is DONE)

**State:** 812 is built, verified and this file is marked `Status: done` with all three
boxes ticked (driver re-check pending). The session's commits so far: only
`git add DECISIONS.md tasks` (DECISIONS entry "2026-10-15 812 DECISION: iteration 245" +
hand-over updates in 812/813/810). **STILL UNCOMMITTED in the working tree (harness-saved,
must be committed by the next agent):** `tests/test_owner_check.py` (the whole 812 build:
`_shot_diff` PIL helper + probe `shot()` taking `<name>.png` then `<name>b.png` after settle
+ subpixel + the five `shot('N-...')` call-sites + the `_run_one` assert loop `<0.5%`
before the docs copy; PLUS the one non-812 change: c's settle widened with the additive
render-quiet gate - probe hooks `map.on('render')` on the live map into `window.__awLastRender`,
settle waits `!map.isMoving() && Date.now() - window.__awLastRender > 700`, isMoving gate/
budget/[warn] text preserved) and `PITFALLS.md` (new tests/playwright entry: isMoving() false
while frames still render - the straggler the double shot caught - and the gate).

**Test state at last run (this branch):** with c's original settle: run 1 green (in-run worst
B 5-reload 0.2668%), run 2 red both tests (details lost to the next session's basetemp wipe),
run 3 unrecorded, run 4 red at B (in-run B 2-placed 0.9944% / B 5-reload 0.5267%, frame-wide,
both probe logs RESULT PASS - the straggler that motivated the gate). After the widen:
runs 5-9 = FIVE consecutive green pair runs (90.7-97.2 s; run 9 = the pair inside the full
suite), zero `[warn] settle` in every captured log, ALL 50 in-run double-shot pairs 0.0000%,
cross-run of the two saved runs 9/10 byte-identical (worst B 1-card 0.0447% card band),
picks still derived (A Richard's Castle, B Devil's Dyke). Full suite (driver's exact command):
194 passed / 1 skipped / 0 failed, 1040 s. docs/site_flow restored to committed bytes after
every run (R5, until 813 retires the copy). Python + extracted PROBE both parse clean.

**Current hypothesis:** none open - the build is done; the widen (never weakening the 0.5%
line) is what makes the proof pass on this machine, per this task's own hand-over rule.

**Exact next step (one commit, then stop or move to the driver's queue):** 1) `git
status --short` should show M on DECISIONS/PITFALLS/tasks/810/812/813/tests (the DECISIONS +
tasks part may already be committed or driver-carried - check the log); 2) commit the code:
`git add tests/test_owner_check.py PITFALLS.md && git commit -m "812: in-run double-shot
assert + render-quiet settle gate - proves the settle in-run (five green pair runs, 50/50
pairs 0.0000%, zero [warn] settle, suite 194/1/0)"`; 3) if the driver returns this task
after a re-check rejection, read the DECISIONS entry first - nothing is left to build here.

**For the chain (their hand-overs were updated this session):** 813 (next, same file) ports
the regime from `git show 3579c22b` (`_write_surface` += the ten docs PNGs, docs copy gated
on AW_OWNER_REFRESH=1 after the write-surface assert, docstrings) without touching
`shot()`/`settle`/`_shot_diff`; 810's verification is its boxes only (two consecutive
unflagged pair runs + suite) on the merged file; the it.235 design record survives at
`git show 3579c22b:tests/test_owner_check.py` (source of both ports).
