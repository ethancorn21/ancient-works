Status: done
Depends on: 307d, 814
Touches: tests/test_owner_check.py, web/data/sites/, web/data/sites.json, data/sites/, data/merge/build_sites.log
Split: no - the build (the in-run double-shot assert and the probe's second shots) is complete and
committed (boxes 1-2); the only remaining work was one final verification run and the done claim -
one session's work, nothing to divide into parts. The chain's remaining work already lives in
separate tasks (813 -> 810 -> 811 -> 242) and unblocks in order as each merges.
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
811 then 242 wait on 810. Chain: 814 (done) -> 812 (this, claimed done it.252) -> 813 -> 810
-> 811 -> 242; the later waiters 230, 241 and 816 are done. Background: 814's header (the
measured drift, the pair flake) and 242's goal; the 2026-10-14 307bc DECISIONS entry (now in
the archive).

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

(2026-10-15, iteration 252, agent a) **DONE, claimed this session.** Request 004 was
AUTO-DECIDED (120-min default applied my recommendation: the driver's suite-verification
budget raised 900 s -> 1800 s; DECISIONS it.252, `AUTO-DECIDED request 004`). Everything
the task needed is verified on the current tree:

1. **Box 3 (full suite green):** the it.247 session-proof run
   (/tmp/iter247-full.log; TMPDIR outside the wiped /tmp/loop-* namespace) finished
   **195 passed, 1 skipped, 0 failed in 642.25 s** - it even sits under the old 900 s
   budget, let alone the new 1800 s.
2. **The one delta since that run:** the it.248/249 main merge (1927be75) brought 815's
   4-line `web/index.html` hunk (`addPairMarker` subpixelPositioning) - the only
   product-file change; the it.252 merge (be9a7b98) is memory-only. 815 is provably
   neutral to this task's asserts (the probe's `subpixel()` workaround is idempotent
   with it; the double-shot compares two shots of the SAME page build; this regime
   copies, never compares, the docs PNGs) - and verified by a fresh module run on the
   current tree: **tests/test_owner_check.py = 2 passed in 75.86 s** (log
   /tmp/iter252-owner.log). Main's own 245 claim ran the full suite green with 815 in
   (195P/1S/0F, 593 s), so the driver's verification of the merged tree (main + this)
   has no untested delta.
3. **Hygiene:** git status clean after the run (all ten re-encoded 307d PNGs
   byte-identical - no PNG hunks in this claim); the three stale 816-verify watchlog
   orphans killed; the 25 US site dirs (537 total) still built. If a FUTURE checkout
   (fresh from main) hits test_merge's box-3 F (missing US site dirs), fix it the way
   it.246/247 did: `run_build.py --force` over the 25 ids (ids = web/data/sites.json
   minus data/merge/sites_premerge_baseline.jsonl), append data/merge/build_sites.log.
   If the human overrides the auto-decision and the budget is reverted, a re-claim
   fails on budget only (see the it.247 entry) - re-file the ask, never weaken a test.

**Next in the chain: 813** (its only remaining dep was this one; same file). 813 ports
the pinned-snapshot regime from the it.235 design record at
`git show 3579c22b:tests/test_owner_check.py` WITHOUT touching the settle/double-shot
work; from 813 on the run must not dirty docs/site_flow/ (it retires the R5
copy-and-restore regime). 810's verification is its own boxes only; 811 then 242 wait
on 810.
