Status: open
Depends on: 307d, 812, 813, 246, 247
Touches: (none - final verification only; the code change is 814 (settle) + 812 (double-shot) + 813 (refresh flag + write-surface + docstrings), all done and merged; the verification work moved to 246 (cross-run pair stability, the byte-identical snapshot) and 247 (the full-suite green run) in the 2026-10-15 iteration-254 split)

# 810: The 307d owner check - settle the map before the saved/reload captures and stop the per-run in-checkout re-render (explicit refresh flag)

Part 1 of 242's split (2026-10-15). The code change went out as parts on the one file
tests/test_owner_check.py - **814** (the settle wait, the flake fix: before every capture
the probe waits until the page's own map.isMoving() is false and no new map frame has been
drawn for ~700 ms, 20 s bounded budget), **812** (the in-run double-shot stability assert:
each of the ten views shot twice, <0.5% differing pixels at threshold 32) and **813** (the
explicit refresh flag AW_OWNER_REFRESH=1, the ten docs/site_flow/307d_*.png into the
write-surface proof, the docstrings) - all three are DONE and on main (814's built fix
carried in as the 816 recipe; 812 claimed at it.252; 813 merged as d3223f6a), together with
815's page hunk and 245's saveFit fix: the settled-capture regime IS the current code.
Re-split 2026-10-15 (iteration 254, per the driver: agent c had had nothing to build for
32 minutes while every open task in the chain - 811, then 242 - waited on this one task
alone, and nothing of this task's verification had been run on the merged tree yet): the
verification work - this task's three boxes - moved to two parts that need nothing from
each other and can build in parallel in two checkouts: **246** (two consecutive unflagged
pair runs: the cross-run stability proof, the pair green end to end with the pick still
derived, the ten docs/site_flow/307d_*.png byte-identical after each run with git status
clean; former boxes 1-2) and **247** (the full-suite green run on the merged tree; former
box 3). Per the split rule, nothing of this task was built yet, so it WAITS on both parts
(their numbers added to its Depends line; done 307d/812/813 stay on it for provenance) and
keeps only the gate: when 246 and 247 land on main with their boxes ticked, this task
ticks its boxes from their recorded evidence (the DECISIONS entries) and claims. 811 (the
one-time refresh, the docs note, the PITFALLS rewrite; Depends: 810 unchanged - it needs
the whole verified regime, not a part) and 242 (the family's final check; Depends: 307d,
810, 811 unchanged) wait on this. Chain now: 246 + 247 (parallel, claimable immediately)
-> 810 (this gate) -> 811 -> 242. The measured-drift background (28.6-33.6% on the four
saved/reload views, the mid-transition signature, the pair flake) is in 242's goal and in
814's header.

## Goal

(Kept as the design spec for the 242 family; items 1-5 are the DONE code work (814/812/813,
merged) and the three verification boxes moved to 246 and 247 in the iteration-254 split.
In tests/test_owner_check.py and its embedded PROBE. The pick (derived, never pinned) and
every existing check stay exactly as they are; this is a capture-timing fix, not a flow
change. Do not touch tests/test_fit_queue.py (the 307/235 family) or the page. The pair
always runs as one invocation, A then B (PITFALLS: the B test cannot run in isolation).)

1. **Stable captures** (814, done). Before the `4-saved` and `5-reload` screenshots (and any
   other view where the map can still be moving - the q1/q2 gesture samples included, where
   the pair flake shows up) wait for the map view to settle: e.g. wait for maplibre's
   `moveend`/`idle` after the last interaction, or disable the page's transitions in the
   test view.
2. **Prove the stability in one run** (812, done). Once settled, take the capture a second
   time and assert the two shots differ by <0.5% of pixels at threshold 32, so a
   mid-transition regression fails the test instead of dirtying PNGs (additive; no
   existing assert changes).
3. **Stop the unconditional in-checkout copy** (813, done). `_run_one` currently copies the
   ten fresh renders into `docs/site_flow/307d_<A|B>_<1..5>.png` on EVERY run and never
   compares them against the committed bytes. The fresh renders stay in the test's private
   temp tree (the test already asserts everything it needs from the temp tree). Copying
   into `docs/site_flow/` happens only on an explicit refresh - an env var or a pytest
   flag, named in the test's docstring - that re-renders all ten from a run and writes
   them into `docs/site_flow/`.
4. **The checkout's PNGs enter the write-surface proof** (813, done). Add the ten committed
   `docs/site_flow/307d_*.png` to `_write_surface`, so the existing "the run wrote into the
   checkout's shared store" assert proves an unflagged run left them byte-identical.
5. **Update the module and test docstrings** (813, done) to the new regime: the ten PNGs
   are a pinned snapshot committed in the repo; an ordinary run never touches them; the
   named flag re-renders them.

## Acceptance criteria

(Split 2026-10-15, iteration 254, per the driver: the verification work moved to the parts
- former box 1 (the two consecutive unflagged pair runs stable across runs, the pair green
end to end, the pick still derived, no existing check changed) and former box 2 (the ten
PNGs byte-identical after a run, git status on docs/site_flow/ clean) to **246**; former
box 3 (the full suite green) to **247**. Both parts depend on nothing (the merged tree is
final) and build in parallel. Nothing of this task was built yet, so it WAITS on both and
keeps only the gate below; the plan for the remaining work is in the hand-over.)
- [ ] **246 is done with its boxes ticked** - two consecutive unflagged runs of the
      owner_check pair are stable across runs (their ten temp-tree views match, <0.5% per
      view at threshold 32), both tests pass end to end with the pick still derived and no
      existing check changed, and each run leaves the ten docs/site_flow/307d_*.png
      byte-identical with git status on docs/site_flow/ clean (the write-surface proof).
- [ ] **247 is done with its boxes ticked** - the full suite is green on the merged tree
      (0 failed; the owner_check pair inside it green with settled captures) and the run
      leaves docs/site_flow/ clean.

## Hand-over

(2026-10-15, iteration 254, agent a - **SPLIT per the driver's instruction; nothing of this
task is built yet, so it WAITS on its parts 246 + 247** (never both ways). The driver puts
the two part files into main at once so an idle agent can take them in parallel (c had had
nothing to build for 32 minutes: its 813 just merged, its next queue task 811 is held on
this gate). 811 and 242 need the whole verified regime, not a part, so their Depends lines
are unchanged (811: 810; 242: 307d, 810, 811). No cycle: 246 and 247 are leaves.

**State:** the settled-capture regime is all merged on main (and synced into this checkout
at b2a4c94f, working tree clean): 814's settle gate (isMoving() false + no new map frame
for ~700 ms, 20 s budget, the built fix carried in as the 816 recipe), 812's in-run
double shot (<0.5% at thr 32, 20 shots per pair run), 813's pinned-snapshot regime
(AW_OWNER_REFRESH=1, the ten docs/site_flow/307d_*.png in the write-surface proof, the
docstrings; merged as d3223f6a), plus 815's page hunk and 245's saveFit fix. Baseline on
this tree (DECISIONS 2026-10-15 + the 813 merge commit): full suite 195 passed / 1
skipped / 0 failed (~600-1040 s); five consecutive green pair runs; all 50 in-run
double-shot pairs 0.0000%; zero [warn] settle; it.245's cross-run compare of two saved
runs: 9/10 views byte-identical, worst B 1-card 0.0447% (the known card band, comfortably
under 0.5%).

**Exact next step (the driver brings this task back once 246 and 247 are both done):**
tick the gate from their recorded evidence - (1) read the DECISIONS entries "2026-10-15
246 DECISION" and "2026-10-15 247 DECISION" (and the parts' hand-overs): 246 must record
the per-view cross-run percentages (all ten <0.5%; the card band ~0.05%; the four
saved/reload in the stable band, not the old 28.6-33.6%), no [settle] TIMED OUT / [warn]
lines, the derived picks (named), the module at the merged bytes (git diff main empty),
git status on docs/site_flow/ clean after each of its two runs; 247 must record the suite
counts (0 failed; 195P/1S expected, count change with reason if any) and docs/site_flow
clean after the run. (2) If both check out: tick the two boxes, set Status: done, and
claim (the driver re-checks; the done-claim follows the 812/245 pattern - green evidence
on the merged tree, memory-only commit). (3) If a box's evidence is missing or a number
is out of band: do NOT tick - log the gap in DECISIONS and re-file it into the part's
task file (the driver reopens that task); never run the pair or the suite here (246/247's
lanes) and never re-file the fix into 811 or 242.

**History:** the superseded it.235 hand-over that followed this section (the whole
242-family code change built in one session on this branch; its build no longer exists in
the file) lives on at `git show 3579c22b:tests/test_owner_check.py` and in the DECISIONS
entry "2026-10-15 810 DECISION: built the whole 242-family code change..." - the design
record for the settle/double-shot/regime mechanism that c's settle, the 812 port and the
813 merge reconstructed. The it.236/it.245 status paragraphs of the previous version of
this file survive in this file's git history.
