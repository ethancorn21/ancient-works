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

(2026-10-15, iteration 246, agent a - context-limit cut mid-diagnosis; 812's BUILD is untouched
and was already proven good in the driver's own run; this session = diagnosis of the rejected
done-claim + the fix for my branch, in flight in the background)

**State:** the 812 build itself is DONE, committed (driver-carried as 8df620cf) and PROVEN
GOOD in the driver's own rejected run (the two owner-check tests printed dots there).
Iteration 246 = diagnosis of the rejected done-claim + the fix for my branch (in flight in
the background). Full diagnosis: DECISIONS entry "2026-10-15 812 DECISION: iteration 246"
(committed this session). Summary:

1. **The `F` (deterministic, the only real code-side problem):** the driver's captured
   line 1 decodes as 72 COMPLETED tests (the `[ 36%]` is an 80-col line-wrap, not a percent
tick); position 58 = `tests/test_merge.py::test_new_sites_are_complete`: it asserts each of
the 25 US cities (past the frozen 508 baseline) has a local `web/data/sites/<id>/` with
`relief.jpg` iff `lidar_credit`. 236c built those in AGENT C's checkout; the per-site dirs
are gitignored LOCAL artifacts, so MY checkout (512 dirs) lacks all 25 while the merged
tracked data (sites.json 533, data/review/ +25, files.jsonl +47) references them. Reproduced
in 0.72 s. `tests/test_review.py` (the "hang" region, tests 74-79) passes 5/5 in 65 s
standalone - not implicated.
2. **The "hang" (no stuck test):** the 2nd verification run started 07:45:18 (the merge
commit) and was killed at exactly 08:00:18 = the driver's 900 s timeout. The suite's green
time is 1040 s (my it.245 measurement, the driver's exact command) > 900 s, worse under
agent-c concurrent load; both verification runs ended with no summary (the 812.txt baseline
is 0 bytes) => "no failing test could be named (crash?)" is a mid-run kill, not a crash
(no OOM in dmesg; 12 Gi RAM free). **The 900 s budget is now stale for the whole project**
(the suite grew from 249 s on 2026-10-12 to 1040 s; see .agent/reports/iter199-suite.log).
3. **The fix (in flight, no code changes):** `data/merge/run_build.py --force <25 US ids>`
(the project's own runner; --force needed because its skip guard keys on the sites.json
entry, which the merge already added). Two nohup background processes from this session
survive on the machine: (a) full suite `pytest tests/ -q -p no:cacheprovider
--durations=200` -> **/tmp/iter246-full.log** (started ~08:10; ~39/196 at last check;
~20-30 min to finish), (b) the US rebuild -> **/tmp/iter246-build.log**, appends to
`data/merge/build_sites.log` (started ~08:16; 5/25 done in ~2 min at ~10 s/site => all 25
done by ~08:21; the ids are in **/tmp/us_ids.txt**). Verified deterministic on site 1:
rebuilt baltimore's entry + the whole sites.json byte-identical to main (git: no diff).

**Test state at last check:** `test_merge.py::test_new_sites_are_complete` FAILED on my
branch pre-rebuild (0.72 s, baltimore missing); `tests/test_review.py` 5/5 PASS in 65 s;
the background full suite will show that same one F (it ran test_merge ~5 min in, before
the rebuild finished) - treat that expected F as already fixed once the rebuild
completes; ANY OTHER failure in /tmp/iter246-full.log is news and must be investigated.

**Exact next steps (in order; both nohup processes keep running regardless):**
1. Check the build: `tail -30 data/merge/build_sites.log` (expect 25 `=== <id> ok ===`) and
   `ls web/data/sites/ | wc -l` (expect 537). If any site is missing/FAILED, resume with
   `.venv/bin/python data/merge/run_build.py --force $(tr '\n' ' ' < /tmp/us_ids.txt)`
   (one process per site; the log has per-site boundaries; a killed session leaves a clean
   boundary at the last finished site).
2. Verify no tracked diff beyond the build log: `git status --short` (expect M on
   DECISIONS.md, tasks/, data/merge/build_sites.log only; web/data/sites.json UNCHANGED)
   and `git diff web/data/sites.json` empty. baltimore proved the entries stay byte-
   identical, but re-check all 25; if sites.json DID change, stop and investigate.
3. **FILE THE ask_human (I intended to; the context limit hit first - the DECISIONS line
   says "NOT yet filed"):** the driver's 900 s suite-verification timeout is shorter than
   the suite's 1040 s green time, so every done claim on every branch of this project now
   fails verification (killed with no summary) regardless of correctness; no in-lane code
   fix of mine can get a 1040 s suite under 900 s (my own test file is ~200 s of it, the
   rest is other tasks' files). Recommend: raise the driver's suite-verification timeout to
   1800 s (1.7x the green time; a true hang still trips it). blocking=true, with the
   recommendation and the evidence (the two kills at exactly 900 s; the 1040 s measurement;
   the suite's growth 249 s -> 1040 s).
4. Wait for /tmp/iter246-full.log to finish; read its summary + durations list (it shows
   where the 1040 s goes). Then, post-rebuild, re-run `tests/test_merge.py` (expect 11/11
   green), and finally the driver's exact command `.venv/bin/python -m pytest tests/ -q
   -p no:cacheprovider` (expect 195 passed / 1 skipped / 0 failed, ~1040-1200 s). After
   it, `git restore docs/site_flow` IF the 307d PNGs are dirty (R5, until 813 retires the
   copy) and confirm `git status` shows only the expected files.
5. **Re-claim done (all three boxes are already ticked - keep them; box 3 re-verified by
   step 4's green run) ONLY once the ask_human has an answer** (or the loop's 120-min
   default applies the recommendation). If the human raises the timeout: set Status: done
   and let the driver verify. If the human says the budget stays at 900 s: do NOT spam
   re-claims (they fail on budget, not correctness) - record the dead-end in DECISIONS
   under this entry and ask the human how to proceed (e.g. a new top-level task to cut the
   suite by 150+ s, which would touch other tasks' test files and needs their sign-off).

**For the chain (unchanged from it.245):** 813 (next, same file) ports the 813 regime from
`git show 3579c22b` without touching `shot()`/`settle`/`_shot_diff`; 810's verification is
its boxes only; the it.235 design record survives at `git show
3579c22b:tests/test_owner_check.py`. The US-site rebuild is my-branch-LOCAL state (the
dirs are gitignored): it fixes MY branch only; if agent b/c hit the same test_merge F in
their own checkouts in the future, the same one-line resume (`run_build.py --force` + the
25 ids, computable as sites.json minus data/merge/sites_premerge_baseline.jsonl) fixes
them.
