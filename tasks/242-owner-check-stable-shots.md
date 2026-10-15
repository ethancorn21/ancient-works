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
- [x] On the merged tree (810 and 811 done), a fresh unflagged run of the owner_check pair
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

(2026-10-15, iteration 258, agent a - **TAKEN OVER from agent c**; the split's bookkeeping
checked out as still valid - all chain parts done and merged: 814/812/813 -> 810 (gate closed
on 246+247) -> 811 -> this; nothing redone).** Box 1 TICKED this session from direct evidence;
box 2 (the full-suite run) is the only remaining work.** No product file is touched by this
task (Touches: none) - it is verification only, and no fix is re-filed here.

**State after this session (evidence in the DECISIONS "2026-10-15 242 DECISION: iteration 258"
entry):** the whole 242 chain is merged into main (main at f45c7052, "811: DONE"); this branch's
only diff vs main was memory files. **Box 1 (fresh unflagged pair vs the committed pinned
snapshot):** one unflagged invocation of the pair (`tests/test_owner_check.py`, 76.10 s, 2
passed; no AW_OWNER_REFRESH; `--basetemp=$TMPDIR/aw242-bt1` so the session-scoped ownerA0/
ownerB0 trees survive the green-run basetemp rmtree - PITFALLS recipe (b)) rendered views that
diff against the ten committed docs/site_flow/307d_*.png as: **9/10 byte-identical (sha256),
only B 1-card at 0.0452% differing pixels at threshold 32** - the known card-view encoding band
(246 measured 0.0452% run-vs-run on the same view; the docs' tolerance is 0.5%), all ten far
under it. Zero `[warn]`/`[settle] TIMED OUT` lines in both probe logs; all in-run double shots
passed the in-test <0.5% assert. Picks derived and identical to 246's: A =
richard-s-castle-q17650937 / earthworkenglan01allcgoog_n0453_1, B = devil-s-dyke-q3307343 /
earthworkenglan01allcgoog_n0662_1 (queue ~171-172 entries this run; the picks move with the
queue, as designed). `git status` on docs/site_flow/ clean after the run (external view of
813's in-test write-surface proof). Baseline hashes: $TMPDIR/aw242-pre.sha256 (lane dies at the
session boundary - the DECISIONS entry is the record).

**Remaining (box 2, ~12 min):** run the pinned exact command
`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` once (green baseline on this tree:
247's 195 passed / 1 skipped / 0 failed, 692.72 s; 811's 683.29 s). Then: (a) counts green - a
count change must have a reason (merged work adding/removing tests); a red NOT in the
owner-check family (e.g. the test_review Esri-tile network flake, PITFALLS) is logged in
DECISIONS with a pointer to the owning task - never fixed/weakened here, and it blocks the
tick; (b) `git status` on docs/site_flow/ clean after that unflagged run -> tick box 2, set
Status: done, claim. The owner pair runs once inside the suite (its in-test asserts cover the
settle/double-shot regime; its probe log is rmtree'd by the green run - the pair's dedicated
probe-log evidence is this session's box-1 run, already recorded). Re-run the suite in the SAME
session as the tick (a background run dies at the session boundary).

**If it flakes** (never weaken or delete a test; log in DECISIONS and re-file into the owning
task with this run's evidence): `[settle] TIMED OUT` or a saved/reload view back near the old
28.6-33.6% drift = 814's lane (814/816); a double-shot assert failure = 812's lane; the docs
note or the snapshot refresh = 811's lane; the saveFit tier/adopt behaviour = 245's lane.
