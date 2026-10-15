Status: open
Depends on: 307d, 810, 811
Touches: (none - final verification only; the code/doc work moved to 810 and 811 in the 2026-10-15 split)

# 242: Pin the 307d owner-check screenshots - settle before shooting, stop the per-run in-checkout re-render

## Goal
`tests/test_owner_check.py::_run_one` re-renders all ten `307d_*.png` views into `docs/site_flow/`
on EVERY run and never compares them against the committed bytes. Measured 2026-10-14 (iteration
199, agent a): the card/placed/gestured views are stable run-to-run (0-1.25% differing pixels,
threshold 32), but the four saved/reload views (A_4/A_5/B_4/B_5) differ by 28.6-33.6% of pixels
between two runs one hour apart on the IDENTICAL tree - visual inspection shows the map view not
settled at shot time (the overlay rectangle shifts slightly relative to the ground imagery between
runs, i.e. the captures land mid-transition). Consequences: any branch that ran the suite is dirty
on up to 7 of the ten PNGs (the driver's sweep must carry them; the b14918f merge produced binary
conflicts on them - see the PITFALLS entry "test_owner_check re-renders all ten 307d golden PNGs..."),
and the docs' PNGs no longer correspond to the 307d-acceptance bytes they replaced. The 307b
hand-over (iteration 256) filed this on the condition that the drift looked meaningful; it does.

Fix the design:

1. **Stable captures.** Before the saved/reload captures (and any other view where the map can
   still be moving), wait for the map view to settle (e.g. wait for the maplibre `moveend`/idle
   after the last interaction, or disable the page's transitions in the test view). The pick
   (derived, never pinned) and every check must stay exactly as they are; this is a capture-
   timing fix, not a flow change.
2. **Stop the unconditional in-checkout copy.** The fresh renders stay in the test's private
   temp tree (the test already asserts everything it needs from the temp tree). Copying into
   `docs/site_flow/307d_*.png` happens only on an explicit refresh (an env var or a pytest flag
   named in the test's docstring). The ordinary run must leave the checkout's ten PNGs
   byte-identical (add them to the test's existing write-surface hash check if that is the
   natural place).
3. **Regenerate once, under the new regime.** Run the explicit refresh once on the current
   tree and commit the ten PNGs (they become the pinned snapshot the docs cite).
4. **Docs.** The 307d section in docs/site_flow.md ("The owner's check...") gains one short
   note: the screenshots are a pinned snapshot (date + how to refresh); the existing text
   (dated "on the 241-entry queue of 2026-10-13") stays - the picks it names are still the
   derived picks (oswestry n0119_1 bar / devil-s-dyke n0662_1 picture_size), only the queue
   indices shifted with re-exports (38/45 -> 3/8 on the 180-entry queue).

## Acceptance criteria
(Split 2026-10-15, per the driver: the boxes the parts deliver moved with them - former box 1
(two-run stability, tests green) and box 2 (checkout byte-identical, the refresh flag) to 810;
former box 3 (one-time regeneration + the docs pinned-snapshot note, plus the PITFALLS rewrite
the Notes describe) to 811. This task waits on both and keeps the final verification; the plan
for the remaining work is in the hand-over below.)
- [ ] On the merged tree (810 and 811 done), a fresh unflagged run of the owner_check pair
      produces views matching the ten committed pinned PNGs (byte-identical, or <0.5% differing
      pixels at threshold 32 for all ten) - the docs' screenshots correspond to what an ordinary
      run produces again.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`) and
      `git status` on docs/site_flow/ is clean after an unflagged run.

## Notes
- The PITFALLS entry "test_owner_check re-renders all ten 307d golden PNGs into
  docs/site_flow/ on EVERY run..." currently prescribes the workaround (restore main's bytes
  before committing; resolve merge conflicts to main's bytes). On this task's merge, rewrite
  that entry's What-to-do to describe the new design and point at the refresh flag; keep the
  history lines. Agent c's 302f iter-127 entry documents the same dirt from her side.
- The drift was measured, not guessed: HEAD-vs-worktree and same-data run-vs-run pixel
  comparisons plus a visual diff (the overlay/ground relative shift) are in the 2026-10-14
  307bc DECISIONS entry and in this file's goal.
- Do not touch tests/test_fit_queue.py (the 307/235 family) or the page; this task is the
  owner-check test and its docs section only.

## Hand-over

(2026-10-15, iteration 189, agent c) **SPLIT per the driver's instruction** (agent a's 230 and my
241 had nothing to build waiting on this task alone, and nothing of this task was built yet - so,
per the split rule, this task WAITS on the parts). `Depends on:` is now `307d, 810, 811` (307d is
done - the file the parts touch was built there; kept on the line per repo convention). `Touches:`
cut to none: what remains here is verification only. No cycle: 814 -> 812 -> 813 -> 810 (the
2026-10-15 iteration-191 re-split: 814 the settle wait, depends only on done 307d, startable
immediately; 812 the in-run double-shot assert after it; 813 the pinned-snapshot regime after
812; 810 waits on 812 + 813, verification only) ->
811 (depends on 810) -> 242 (this).

The parts (the lowest free numbers in 800-1099):
- **810** (tasks/810-owner-check-settle-captures.md; Touches tests/test_owner_check.py) - the whole
  code change, carrying former boxes 1-2: the settle wait before the saved/reload captures (the
  flake mechanism: the 4.5 s flyTo web/index.html:874 + 900 ms fitBounds web/fitkit.js:573 that the
  probe's fixed sleeps never waited for), the additive double-shot <0.5%-at-threshold-32 stability
  assert, the explicit refresh flag (named in the docstring) replacing the unconditional
  in-checkout copy, the ten docs/site_flow/307d_*.png into _write_surface, docstrings to the new
  regime. The pick stays derived; every existing check unchanged; tests/test_fit_queue.py and the
  page untouched (the Notes carry over).
- **811** (tasks/811-owner-check-pin-snapshot.md; Touches the ten PNGs + docs/site_flow.md +
  PITFALLS.md) - former box 3 + the Notes' PITFALLS rewrite: the one-time refresh and commit of
  the ten pinned PNGs under 810's regime, the pinned-snapshot note in the 307d section of
  site_flow.md (date + refresh command; existing text kept; the picks it names are still the
  derived picks oswestry n0119_1 bar / devil-s-dyke n0662_1 picture_size, indices 38/45 -> 3/8 on
  the 180-entry queue, moving with the queue), and the PITFALLS rewrite (the per-run re-render
  entry's What-to-do -> the new design + the flag; history lines kept; the neighbouring B-test
  entry's stale "task 242's" pointers corrected).

Waiters updated per the driver's rule: 230's Depends is now "211, 207a, 207b, 807, 808, 242, 810"
and 241's "240, 242, 810" (810 added directly - both are blocked by the mid-transition flake / PNG
dirt that 810 fixes; the rest reaches them transitively through 242). 236c unchanged.

**What remains HERE (both boxes verification only, no file changes):** when the driver returns
this task (after 810+811 merge): (1) run the unflagged owner_check pair once (one invocation, A
then B - PITFALLS: B cannot run alone) and diff its ten temp-tree renders against the ten
committed PNGs (byte-identical, or <0.5% differing pixels at threshold 32 for all ten) -> tick
box 1; (2) run the full suite `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` and
confirm `git status` on docs/site_flow/ is clean after that unflagged run -> tick box 2, set
Status: done, claim. If the committed snapshot does not match a fresh render, or the pair flakes
after 810's settle: that is a defect in 810's lane - put the run evidence in "## Proposed changes"
on tasks/810-owner-check-settle-captures.md and hold this task; never re-file the fix here, never
weaken or delete a test.

Deviation recorded: this file's Notes section says the PITFALLS rewrite happens "on this task's
merge"; with the split it happens in 811 (the part that completes the design) - same intent (it
lands with the 242 family, history lines kept, the 302f iter-127 pointer preserved). Working tree
at split time: docs/site_flow/307d_B_4/B_5 were dirty from the pre-split run and were restored to
the committed bytes; no code changed this session.
