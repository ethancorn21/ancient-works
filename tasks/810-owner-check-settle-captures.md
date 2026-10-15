Status: open
Depends on: 307d, 812, 813
Touches: (none - final verification only; the code change moved to 814 (settle) + 812 (double-shot) + 813 (refresh flag + write-surface + docstrings) in the 2026-10-15 splits)

# 810: The 307d owner check - settle the map before the saved/reload captures and stop the per-run in-checkout re-render (explicit refresh flag)

Part 1 of 242's split (2026-10-15). Re-split 2026-10-15 (iteration 190, per the driver: agent a
had nothing to build for 68 minutes while every waiter - 230, 241, 242, 811, and 236c through
241 - waited on this one task alone): the whole code change moved to parts on the one file
tests/test_owner_check.py - **813** (the explicit refresh flag, the ten PNGs into the write
surface, the docstrings) and the settle/double-shot pair, re-split again 2026-10-15
(iteration 191, per the driver: agent a had nothing to build for 76 minutes while the chain
812 -> 813 -> 810 -> 811 -> 242 -> {230, 241} -> 236c waited on 812 alone): **814** (the
settle wait, the flake fix; depends only on done 307d, startable immediately) and **812** (the
in-run double-shot stability assert that proves the settle; Depends: 814; same file, after
814). 813 runs after 812 (same file, and its docstrings describe the 814 settle and the 812
double shot as part of the regime). This task WAITS on 812 + 813 (unchanged) and keeps only
the final verification (the 242 pattern). 811 (the one-time refresh, the docs note, the
PITFALLS rewrite) and 242 (the family's final check) wait on this. The measured-drift
background (28.6-33.6% on the four saved/reload views, the mid-transition signature, the pair
flake) is in 242's goal and in 814's header. The waiters 230 and 241 carry 814 (the flake
fix), 812 and 813 on their Depends lines directly (they are held on the mid-transition flake
814 fixes and the PNG dirt 813 stops).

## Goal

(Kept as the design spec for 812/813/814; the boxes the parts deliver moved with them. In
tests/test_owner_check.py and its embedded PROBE. The pick (derived, never pinned) and every
existing check stay exactly as they are; this is a capture-timing fix, not a flow change. Do
not touch tests/test_fit_queue.py (the 307/235 family) or the page. The pair always runs as
one invocation, A then B (PITFALLS: the B test cannot run in isolation).)

1. **Stable captures** (814). Before the `4-saved` and `5-reload` screenshots (and any other
   view where the map can still be moving - the q1/q2 gesture samples included, where the
   pair flake shows up) wait for the map view to settle: e.g. wait for maplibre's
   `moveend`/`idle` after the last interaction, or disable the page's transitions in the
   test view.
2. **Prove the stability in one run** (812). Once settled, take the capture a second time
   and assert the two shots differ by <0.5% of pixels at threshold 32, so a mid-transition
   regression fails the test instead of dirtying PNGs (additive; no existing assert changes).
3. **Stop the unconditional in-checkout copy** (813). `_run_one` currently copies the ten
   fresh renders into `docs/site_flow/307d_<A|B>_<1..5>.png` on EVERY run and never compares
   them against the committed bytes. The fresh renders stay in the test's private temp tree
   (the test already asserts everything it needs from the temp tree). Copying into
   `docs/site_flow/` happens only on an explicit refresh - an env var or a pytest flag,
   named in the test's docstring - that re-renders all ten from a run and writes them into
   `docs/site_flow/`.
4. **The checkout's PNGs enter the write-surface proof** (813). Add the ten committed
   `docs/site_flow/307d_*.png` to `_write_surface`, so the existing "the run wrote into the
   checkout's shared store" assert proves an unflagged run left them byte-identical.
5. **Update the module and test docstrings** (813) to the new regime: the ten PNGs are a
   pinned snapshot committed in the repo; an ordinary run never touches them; the named flag
   re-renders them.

## Acceptance criteria

(Re-split 2026-10-15, iteration 190, per the driver: the boxes the parts deliver moved with
them - former box 1 (two-run stability, the pair green, the additive discipline of the
settle/double-shot) to 812; former box 2 (checkout byte-identical, the refresh flag) plus
former box 4 (suite green, git status clean) to 813. Nothing was built yet in this task, so
it WAITS on the parts and keeps only the final verification; the plan for the remaining work
is in the hand-over below.)
- [ ] On the merged tree (812 and 813 done): two consecutive unflagged runs of the owner_check
      pair (one invocation per run, A then B) are stable - their ten temp-tree views match
      (the pair's in-run double-shot assert already proves it per run; this is the cross-run
      check) - and both tests pass end to end with the pick still derived and no existing
      check changed.
- [ ] An unflagged run leaves every `docs/site_flow/307d_*.png` in the checkout byte-identical
      (the write-surface proof) and `git status` on `docs/site_flow/` is clean after it.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).

## Hand-over

(2026-10-15, iteration 236, agent a - **STATUS CHANGE (read this first):** the it.235 build
named below (139 lines: zero-duration served-tree transitions + the `window.__awSettle`
idle tracker + settle, plus 812's double shot and 813's refresh flag) was committed by the
driver at 3579c22b, then REPLACED by 693b0ea3 ("814 taken over from agent c: its work
carried"), which put agent c's TESTED 54-line settle + subpixel fix (63a4e4e = the 816
recipe; verified byte-identical in this branch's file at it.236) in tests/test_owner_check.py
instead. The it.235 file survives verbatim at `git show 3579c22b:tests/test_owner_check.py`.
The it.235 build was never verified (the session was cut before its first pair run, and it
still carried the missing-`//` bug); c's fix was verified (194: two green runs, all ten
views stable) - so the cycle now builds on c's recipe, not on the idle tracker described
below.

**State at it.236 (agent a holds the whole cycle; inter-deps count as met):** the pair is
GREEN on this branch with c's settle + subpixel in the file: 3 consecutive unflagged runs
(64.5/65.9/66.7 s), both tests RESULT PASS, zero [warn] settle, the old ratio flake gone.
One NEW red surfaced and was fixed: B red at "line effect (b)" (the tier check) - a page
race (saveFit's one-shot sites.json fetch landed in the 119 ms depiction->re-score gap)
- filed as 245 and fixed on the page (web/index.html, committed ab57da1b); after the fix
the pair is green again, and the cross-run compare (run2 vs run3, threshold 32 per
channel) shows ALL TEN views 0.000% differing - that is this task's box-1 (cross-run)
evidence, in hand. The 307d PNGs were restored to committed bytes after every run (R5).

**What remains (when the driver returns it - after 812+813 are rebuilt and 814/816/230
land on main):** 1) REBUILD the 812 + 813 parts on top of the 816 recipe (port from
3579c22b: the probe's `shot()` double-shot + the Python `_shot_diff` <0.5%-at-thr-32
assert, the ten docs/site_flow/307d_*.png into `_write_surface`, the docs copy gated on
`AW_OWNER_REFRESH=1` moved after the write-surface assert, docstrings; adapt a's settle
references to c's `!map.isMoving()` + subpixel; DROP a's zero-duration served-tree
patching - c's approach leaves the served tree untouched); 2) run the boxes: two
consecutive unflagged pair runs (one invocation each; the in-run double shot proves
per-run stability, this is the cross-run check for box 1 - expect <0.5% on all ten,
realistically ~0%), `git status -- docs/site_flow/` clean after each run (box 2, once
813's write-surface registration is in - until then unflagged runs still re-copy all
ten, so restore to committed bytes after every run), full suite (box 3; last
known-green baseline ~180 passed / 1 skipped / 0 failed, 2026-10-14, per the archive);
3) tick the boxes, set Status: done, claim (the driver re-checks).

**If it flakes after the rebuild:** a settle timeout = the settle gate (814's lane - on
c's recipe that is the `!map.isMoving()` poll; the it.235 escalation was a second gate of
no `render` event for ~700 ms - the /tmp/mplib_probe evidence for maplibre 5.6.0's
`idle` semantics is in the DECISIONS "2026-10-15 810 DECISION" entry); a double-shot
assert failure naming a view = a straggler tile/ink between the two shots (widen the
settle; never weaken the 0.5% line); a tier-check red = 245's lane (point at 245's file
with the probe's [eval] effects block); red at the OLD ratio step = 816's lane (point at
814/816). Never weaken or delete a test; never re-file the fix here.

<superseded it.235 text kept for the design record only - the build it describes no longer
exists in the file; its content lives on at `git show 3579c22b:tests/test_owner_check.py`:

(2026-10-15, iteration 235, agent a - **TAKEN OVER and nearly finished; the next session is
verification + memory only, see below.**) The CYCLE (230/242/810/811/812/813/814 held by agent
a; inter-deps count as met) was broken this session: the whole 242-family code change is now
BUILT in tests/test_owner_check.py on this branch (UNCOMMITTED in the working tree - the
harness saved it): 814 (served-tree zero-duration transitions + the `window.__awSettle` idle
tracker injected into the served index.html + `settle()` before every q read and shot), 812
(`shot()` double-shot per view + Python `_shot_diff` <0.5%-at-thr-32 assert in `_run_one` for
A and B) and 813 (the ten docs/site_flow/307d_*.png in `_write_surface`, the docs copy gated
on `AW_OWNER_REFRESH=1` and moved after the write-surface assert, docstrings to the regime).
Full design + the empirical idle evidence (/tmp/mplib_probe: maplibre 5.6.0 fires one `idle`
when the camera is at rest and the event-driven render loop has no pending frame; after it the
frame count froze for 20 s): DECISIONS.md entry "2026-10-15 810 DECISION" at the bottom.
**KNOWN BUG (the only code fix left):** in the PROBE, line 3 of the settle comment is missing
its `//` prefix - the line `camera is at rest and no frame is pending (no tiles or overlay
arriving), so a screenshot` right after the line ending `...the maplibre 5.6.0 \`idle\` event
means the` - `node --check` on the extracted PROBE fails until it has `//` (extract:
`re.search(r"PROBE = r\"\"\"(.*?)\n\"\"\"", src, re.S)`; Python side already parses, and the
fixture's patching simulation passed - all four duration anchors unique, patched fitkit
parses; the `node --check` on the .html in that snippet was a mistake, skip it).

**EXACT NEXT STEPS (this session's remainder, in order):**
1. Fix the missing `//` (above); re-run the extract + `node --check` until clean.
2. `git status --short` first: the tree should be clean on docs/site_flow/ (this session
   restored the two dirty B_4/B_5 PNGs to committed bytes with `git restore --`; if any run
   dirtied them again, restore before proceeding).
3. Run the pair ONCE, unflagged, WITH retention: `.venv/bin/python -m pytest
   tests/test_owner_check.py -q -p no:cacheprovider --tmp-retention-policy all` (~2 min;
   retention keeps the successful temp trees). Both tests should pass. Then read both probes'
   logs (retained tree: $TMPDIR/pytest-of-agent/pytest-<N>/owner{A,B}0/owner_probe.log,
   TMPDIR=/tmp/loop-ancient-works.a) for `[settle]` lines: expect NO `TIMED OUT` (especially
   labels `1-card` and `5-reload` - that is the real-page confirmation that idle comes).
4. Run the pair a SECOND time, same command (new invocation; A then B - PITFALLS: B cannot
   run alone).
5. 810 box 1 (cross-run check): throwaway /tmp PIL script (never commit) comparing run1 vs
   run2's ten views (1-card ... 5-reload; the <name>b.png double shots may be ignored here -
   the per-run assert already covers them): count pixels differing by >32 on any channel /
   total; expect <0.5% on all ten, realistically ~0% on the map views (card/placed/gestured
   were 0-1.25% cross-run before; the four saved/reload were 28.6-33.6% and must now sit in
   the stable band). Record the per-view percents in DECISIONS.
6. 810 box 2: `git status -- docs/site_flow/` after EACH run is clean (the write-surface
   assert proves byte-identity in-test; this is the external view).
7. 810 box 3: full suite `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~8-10
   min; last known-green baseline ~180 passed / 1 skipped / 0 failed, 2026-10-14, per the
   archive; a pre-existing red NOT caused by tests/test_owner_check.py is logged in
   DECISIONS, not absorbed - do not touch other tasks' tests).
8. Memory + commit: tick 814/812/813 boxes ONLY as verified by steps 3-7 (leave their Status
   OPEN - the driver stamps them in later sessions; write each of their Hand-overs: "built +
   verified on agent/a's branch it.235, done-claim pending the driver re-check"); tick 810's
   three boxes and set 810 `Status: done`; PITFALLS entries (NEW: maplibre 5.6.0 `idle`
   semantics + event-driven render loop, with the /tmp/mplib_probe evidence and the note
   that `window.__awSettle` lives in the SERVED copy only; NEW: the AW_OWNER_REFRESH=1
   pinned-snapshot regime + the fact that unflagged runs no longer touch docs/site_flow/ -
   but do NOT rewrite the old "re-renders all ten 307d golden PNGs..." entry's What-to-do,
   that rewrite + the docs/site_flow.md note is 811's job when it comes); then `git add -A &&
   git commit` (code + memory together; NEVER git add -A over other agents' files - here
   only tests/test_owner_check.py + the memory/task files are dirty on this branch).

**If it flakes:** a `[settle] TIMED OUT` = idle never came (log the label; next fix is a
second gate - no `render` event for ~700 ms - not a looser assert). A double-shot assert
failure naming a view = a straggler tile/ink between the two shots (widen the settle; never
weaken the 0.5% line). If the pair is red at the SAME old step ("toolbar scale and turn
change the drawing on screen") despite the settle: that would refute the mid-transition
hypothesis - stop, record the [settle] log + the measured e1/e2 in DECISIONS, and point at
it in 814's file, do not absorb into 810. Never weaken or delete a test; never re-file the
fix here.
