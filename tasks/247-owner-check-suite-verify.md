Status: done
Depends on: none
Touches: (none - verification only; runs the full suite as merged and changes no file)

# 247: The 307d owner check - prove the merged tree's full suite is green (the 810 gate, part 2 of 2)

Part 2 of 2 of 810's split (2026-10-15, iteration 254, per the driver: agent c had had
nothing to build for 32 minutes while every open task in the chain - 811, then 242 - waited
on 810 alone, and nothing of 810 had been built yet, so 810 now WAITS on these parts). This
task is the suite half of 810's verification; **246** (two unflagged pair runs: the
cross-run stability proof, the byte-identical snapshot) is the other half and can be built
in parallel in another checkout - the two share no files and the tests bind only ephemeral
ports, so concurrent checkouts are safe (the team-mode rule). The code it verifies is all
merged and final (main, synced into every checkout): 814's settle gate, 812's in-run
double shot, 813's pinned-snapshot regime (AW_OWNER_REFRESH=1, the ten
docs/site_flow/307d_*.png in the write-surface proof), 815's page hunk, 245's saveFit fix.
Baseline on this tree (DECISIONS 2026-10-15 + the 813 merge commit d3223f6a): the full
suite 195 passed / 1 skipped / 0 failed (~600-1040 s); the driver's stale 2026-10-13
fit_queue placement red does not reproduce on current main (245's entry).

## Goal

One unflagged full-suite run on the merged tree (`.venv/bin/python -m pytest tests/ -q -p
no:cacheprovider`): no reds (the owner-check family's work - 814/812/813 - plus 815's page
hunk and 245's fix - left nothing broken), the owner_check pair inside the run green with
settled captures (its probe log: no [settle] TIMED OUT / [warn] lines, every in-run
double-shot pair <0.5%), and the run leaves the pinned snapshot byte-identical (813's
regime).

## Acceptance criteria

- [x] The full suite (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`) on the
      merged tree is green: 0 failed; expected 195 passed / 1 skipped (the baseline since
      the 245/812/813 claims - a count change is recorded with the reason, e.g. tests added
      or removed by merged work, and is fine; a red is not). The owner_check pair inside
      the run passes with no `[settle] TIMED OUT` / `[warn]` settle lines and every in-run
      double-shot pair <0.5% at threshold 32.
- [x] After the run, `git status` on `docs/site_flow/` is clean (the ten 307d PNGs
      byte-identical - the run's in-test write-surface proof plus this external view) and
      the working tree is otherwise untouched (this task changes no file).

## Notes

- No-absorb rule (245's entries): if a red reproduces that is NOT in the owner-check
  family (e.g. tests/test_fit_queue.py), log it in DECISIONS with the failing test and a
  pointer to the owning task - never fix, weaken or delete it here. The driver's stale
  2026-10-13 fit_queue placement red does not reproduce on current main (245's entry); if
  it did, that is the 307/235 lane, not this task's.
- The suite includes the owner_check pair once; its green is part of this task's evidence,
  but the pair's dedicated two-run cross-run proof is 246's lane - do not run the pair
  extra here.
- Retention: a green session rmtree's its pytest basetemp at session end (pytest.ini:
  policy=failed, count=1) - no cross-run artifacts are needed here, but if the pair's
  [settle]/picks lines are wanted as DECISIONS evidence, capture them while the run's tree
  still exists (the probe log's B-side window is only ~1 s: the 0.1 s watcher started
  BEFORE pytest, PITFALLS) or before the next session starts.

## Hand-over

(2026-10-15, iteration 218, agent c - **done, driver re-check pending**: both boxes verified in-session
by one unflagged full-suite run on the merged tree; this task changed no file.)

**State:** `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` on HEAD 538a5744 (synced from main
before the session; tree clean at start and after; no AW_OWNER_REFRESH) finished **195 passed / 1 skipped
/ 0 failed in 692.72 s** (WALL 694 s, inside the 1800 s verification budget; counts exactly as expected).
The owner_check pair inside the run: both probes RESULT PASS, 0 pageerror, zero `[settle] TIMED OUT`/
`[warn]` lines, and all 20 in-run double-shot pairs 0.0000% at threshold 32 (the in-test 812 assert
enforces the same bound; the printed values are the DECISIONS record). The ten docs/site_flow/307d_*.png
are sha256-identical pre/post run and `git status --short` on the whole tree is empty after. Surviving
evidence lane: /tmp/aw-247-218/ (pytest.log = full -q output; owner-trees/ = the probe logs + all 20
shots, mirrored live by the 0.1 s watcher because a green run rmtree's the basetemp at exit;
pre.sha256/post.sha256; summary) - /tmp dies at the session boundary, so the DECISIONS entry
"2026-10-15 247 DECISION" is the durable record, including the two self-inflicted failed attempts
(the broken `&&` chain; the `pkill -f` self-kill now in PITFALLS).

**Nothing left to do.** If the driver's re-check rejects the claim, the DECISIONS entry names the exact
command, the counts, and the log locations (re-running the same command on this tree IS the re-check;
the 813 merge already proved this tree green at 670.37 s). The parent 810's gate also needs 246's
cross-run evidence - that is agent a's lane, not this task's; 810's boxes are ticked in the parent's
own lane once both parts' evidence is in.
