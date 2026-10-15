Status: done
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
- [x] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`) and
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

(2026-10-15, iteration 258, agent a - **DONE and claimed; both boxes ticked this session from
direct evidence.** The driver's re-check (every box ticked + suite green) runs the same pinned
command I ran; nothing else remains on this task, and it touches no product file.)

**The result - what the merged tree (main at f45c7052, "811: DONE") produces on an ordinary,
unflagged run:**

- **Box 1 (fresh pair run vs the committed pinned snapshot):** one unflagged invocation of the
  pair (`tests/test_owner_check.py`, 76.10 s, 2 passed; no AW_OWNER_REFRESH; `--basetemp` only to
  keep the session-scoped ownerA0/ownerB0 trees alive for the diff - PITFALLS recipe (b), nothing
  about the run itself changed). Rendered views vs the ten committed docs/site_flow/307d_*.png:
  **9/10 byte-identical (sha256); the sole diff B 1-card 0.0452% differing pixels at threshold 32**
  - the known card-view encoding band (246 it.255: 0.0452% run-vs-run on the same view), far under
  the 0.5% tolerance; the old 28.6-33.6% saved/reload mid-transition drift (this task's
  measurement) does not reproduce. Zero `[warn]`/`[settle] TIMED OUT` lines in both probe logs;
  all in-run double shots pass the in-test <0.5% assert; picks DERIVED (A =
  richard-s-castle-q17650937/n0453_1, B = devil-s-dyke-q3307343/n0662_1 - identical to 246's;
  they move with the queue, as designed).
- **Box 2 (the pinned full suite):** `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`
  -> **195 passed, 1 skipped, 0 failed in 674.53 s** (exactly the green baseline: 247 692.72 s,
  811 683.29 s - same counts, different days). After that unflagged run `git status` on
  docs/site_flow/ is clean (sha256-verified: all ten PNGs byte-identical pre/post) and the whole
  tree is untouched. The owner pair inside the run is green with its in-test settle/double-shot/
  write-surface asserts; its probe log is rmtree'd by the green run (PITFALLS), so the dedicated
  probe-log evidence of record is the box-1 pair run above.

**Provenance of the regime it verifies (all merged, archived in DECISIONS-archive.md):** 814 (the
settle gate: `map.isMoving()` false + no new map frame for ~700 ms, 20 s budget - the 816 recipe),
812 (the in-run double shot, <0.5% at threshold 32, so a mid-transition capture fails the test
instead of dirtying the PNGs), 813 (the pinned-snapshot regime: AW_OWNER_REFRESH=1 re-renders the
ten into docs/site_flow/, an unflagged run never touches them, the ten enter the write-surface
hash proof), 810 (gate), 246 (cross-run proof), 247 (suite proof), 811 (the one-time re-pin -
byte-identical, so the committed snapshot was already the settled-era render of the then-derived
picks - plus the docs pinned-snapshot note and the PITFALLS rewrite that retired the
restore-main-bytes workaround).

**If the driver's re-check reds:** a red in the owner-check family points at the owning task per
the routing in this file's Notes (settle/drift = 814/816; double shot = 812; snapshot/refresh =
811; saveFit tier/adopt = 245); a red outside it (e.g. the test_review Esri-tile network flake,
PITFALLS) is that task's lane. This file is verification-only (Touches: none) and no test is ever
weakened or deleted here.

**For a future re-pin** (the picks move with the queue; the page changes): the note in the 307d
section of docs/site_flow.md names the command - `AW_OWNER_REFRESH=1 .venv/bin/python -m pytest
tests/test_owner_check.py -q -p no:cacheprovider` (one invocation, A then B) - and the resulting
ten PNGs are the new pin.
