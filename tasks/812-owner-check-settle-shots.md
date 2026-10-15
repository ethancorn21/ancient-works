Status: in-progress
Depends on: 307d, 814
Touches: tests/test_owner_check.py, web/data/sites/, web/data/sites.json, data/sites/, data/merge/build_sites.log
(the extra paths: rebuilding the 25 US sites 236c built in agent c's checkout - this checkout's local
build state lags main's tracked data after the merge, and test_merge's box-3 completeness check fails
on it until the sites are built here too; run_build.py --force is the project's own runner)

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

(2026-10-15, iteration 247, agent a) **WAITING ON HUMAN REQUEST 004** (filed this session;
blocking - the loop brings this task back when the human answers, or when its 120-min
default applies my recommendation: raise the driver's suite-verification timeout 900 s ->
1800 s). The 812 build is done and everything verifiable without the budget answer is
verified; on return the only work left is one green run and the re-claim.

**State:**
1. **Rebuild DONE (the my-branch fix):** all 25 US site dirs built here via `run_build.py
   --force` (08:16-08:23; log appended to data/merge/build_sites.log - the only tracked
   diff, committed). `web/data/sites/` = 537 dirs, all 25 present, none missing;
   `web/data/sites.json` byte-identical to main (`git diff` empty). `tests/test_merge.py`
   = 11/11 GREEN (27 s; pre-rebuild: F in 0.72 s).
2. **The it.246 nohup run's 17 reds (10F+7E in 817 s) are 100% environmental - zero
   product bugs** (full tracebacks in /tmp/iter246-full.log; analysis in DECISIONS
   it.247): 6 in test_merge ran before the rebuild finished (fixed); 11 (2 owner_check +
   4 review + 4 serve + 1 matchfit_station) were hit by the SESSION-BOUNDARY WIPE - my
   session start (08:21:47) recreated /tmp/loop-ancient-works.a out from under the
   still-running nohup process (third wiper; disk was at 70%, so not the pressure one;
   added to PITFALLS).
3. **Clean re-verification IN FLIGHT, session-proof:** nohup pid 4033629, started ~08:27:
   `env TMPDIR=/tmp/aw-it247-tmp .venv/bin/python -m pytest tests/ -q -p no:cacheprovider`
   -> **/tmp/iter247-full.log**. TMPDIR points at a self-managed dir OUTSIDE the
   harness-wiped /tmp/loop-* namespace (tests follow TMPDIR via tmp_path_factory; none
   hard-code it), and the log is in bare /tmp (that location already survived one wipe).
   Expected: 196 passed / 1 skipped / 0 failed (the suite is now 196: +1 test from the
   08:21:40 main merge) in 817-1040+ s (started ~08:27 => ~08:41-08:46; longer under
   agent-c load). At write time (~08:31): 42 tests, zero red, alive.

**On return (answer to 004, or the 120-min default = 1800 s budget):**
1. Read **/tmp/iter247-full.log**. If the run is still going (`pgrep -f 'pytest tests/ -q
   -p no:cacheprovider'`), wait it out - it is the box-3 evidence; it cannot be killed by
   a session wipe now. If it finished: expect "196 passed, 1 skipped". ANY red this time
   is REAL (the wipe can no longer be the cause - the temp area is outside the namespace):
   read its tracebacks in the log; if the culprit is another task's file, record it in
   DECISIONS and leave the file alone (the driver's verification re-runs the suite after
   merging main, so it must be green on the merged tree anyway).
2. Hygiene before claiming: `git status --short` should show only my memory files pending
   (the build log was committed this session); `git restore docs/site_flow` IF the 307d
   PNGs are dirty (R5, until 813 retires the copy).
3. **Re-claim:** set `Status: done` (all three boxes keep their ticks; box 3 = this green
   run). If the human instead keeps the 900 s budget: do NOT re-claim (it would fail on
   budget, not correctness) - record the dead-end in DECISIONS under the it.247 entry and
   ask how to proceed (e.g. a new top-level task to trim the suite by 150+ s, touching
   other tasks' test files, needing their sign-off).

**For the chain (unchanged from it.245/246):** 813 (next, same file) ports the 813 regime
from `git show 3579c22b` without touching `shot()`/`settle`/`_shot_diff`; 810's
verification is its boxes only; the it.235 design record survives at `git show
3579c22b:tests/test_owner_check.py`. The US-site rebuild is my-branch-LOCAL state (the
dirs are gitignored): it fixes MY branch only; any other checkout that hits the same
test_merge F fixes itself the same way (`run_build.py --force` + the 25 ids; /tmp/us_ids.
txt may be gone after a wipe - recompute: the site ids in web/data/sites.json minus those
in data/merge/sites_premerge_baseline.jsonl).
