Status: open
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

- [ ] With 814 merged, the in-run double-shot assert covers all ten views (five per run, A
      and B) and passes: the two settled shots differ by <0.5% of pixels at threshold 32
      (the other six views stay at their historical 0-1.25% encoding noise, comfortably
      under the line); a mid-transition regression fails the test instead of dirtying the
      PNGs.
- [ ] The pick is still derived and no existing check changed (same flow, same asserts); the
      double-shot assert and its second shots are additive.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).

## Hand-over

(2026-10-15, iteration 235, agent a) **BUILT on agent/a's branch with 814 + 813 in the same
file (tests/test_owner_check.py), uncommitted until 810's session commits.** The double shot:
the probe's `shot(name)` takes `<name>.png` and immediately `<name>b.png` after ONE settle
(10 per pair: A and B x 1-card/2-placed/3-gestured/4-saved/5-reload); Python `_shot_diff`
(PIL ImageChops - per-channel >32 masks OR'd via ImageChops.lighter, C-speed; pillow already
pinned in requirements.in) asserts the differing fraction <0.5% in `_run_one` for BOTH tags,
so a mid-transition regression fails the test here instead of dirtying the docs PNGs. A
double-shot assert failure naming a view = a straggler tile/ink between the two shots -
widen the settle (814's lane), never weaken the 0.5% line. Pick still derived; no existing
assert changed. **Boxes unticked**: 810's session (next) runs the pair twice + the full
suite and ticks these boxes per 810's hand-over; when the driver returns this task,
re-confirm the suite green and claim. Design rationale in DECISIONS.md "2026-10-15 810
DECISION". The pre-run "restore the re-rendered PNGs" workaround is RETIRED by 813 (an
unflagged run no longer touches docs/site_flow/ at all).
