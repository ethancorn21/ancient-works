Status: done
Depends on: 812
Touches: tests/test_owner_check.py

# 813: The 307d owner check - stop the per-run in-checkout re-render: the explicit refresh flag, the ten PNGs into the write surface, the docstrings

Part 2 of 810's split (2026-10-15, iteration 190): the pinned-snapshot regime in
tests/test_owner_check.py. It runs AFTER 812 (Depends: 812 - after the 2026-10-15
iteration-191 re-split, 812 is the family head over the settle + double-shot pair: 814's
settle wait and 812's in-run double-shot assert; same file, and the docstrings this part
rewrites describe the 814 settle and the 812 double shot as part of the new regime); 810
keeps the final verification and waits on 812 + this; 811 (the one-time refresh, the docs
note, the PITFALLS rewrite)
waits on 810 and runs the flag this part introduces; 242 waits on both. Background: 242's
goal - `_run_one` copies the ten fresh renders into `docs/site_flow/` on EVERY run and never
compares them against the committed bytes (the PITFALLS entry "test_owner_check re-renders
all ten 307d golden PNGs..."): any branch that ran the suite is dirty on up to seven of the
ten PNGs, and a merge of a dirty branch gets a BINARY conflict on each (b14918f, five files).

## Goal

In tests/test_owner_check.py only. The pick (derived, never pinned) and every existing check
stay exactly as they are; this part adds the regime, it does not change the flow. Do not
touch tests/test_fit_queue.py (the 307/235 family) or the page.

1. **Stop the unconditional in-checkout copy.** `_run_one` currently copies the ten fresh
   renders into `docs/site_flow/307d_<A|B>_<1..5>.png` on EVERY run and never compares them
   against the committed bytes. The fresh renders stay in the test's private temp tree (the
   test already asserts everything it needs from the temp tree). Copying into
   `docs/site_flow/` happens only on an explicit refresh - an env var or a pytest flag, named
   in the test's docstring - that re-renders all ten from a run and writes them into
   `docs/site_flow/`.
2. **The checkout's PNGs enter the write-surface proof.** Add the ten committed
   `docs/site_flow/307d_*.png` to `_write_surface`, so the existing "the run wrote into the
   checkout's shared store" assert proves an unflagged run left them byte-identical.
3. **Update the module and test docstrings** to the new regime: the ten PNGs are a pinned
   snapshot committed in the repo; an ordinary run never touches them; the named flag
   re-renders them (812's settle is part of the regime the docstrings describe).

## Acceptance criteria

- [x] An unflagged run leaves every `docs/site_flow/307d_*.png` in the checkout byte-identical
      (verified by the test's write-surface hash or an equivalent check); the explicit refresh flag
      (the one named in the docstring) re-renders all ten from a run and writes them into
      `docs/site_flow/`.
- [x] No existing check changed (same flow, same asserts); the refresh flag, the write-surface
      addition and the docstrings are additive.
- [x] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`) and
      `git status` on `docs/site_flow/` is clean after an unflagged run.

## Hand-over

(2026-10-15, iteration 253, agent a) **813 is BUILT and all three boxes verified this
session - Status: done.** Base = main (812 merged: the 816 recipe with the 812 render-quiet
widen + `shot()`/`_shot_diff`/double-shot loop; worktree clean, ten PNGs == main). The
regime landed exactly per the it.241 prep: `SNAPSHOT_VIEWS` + `REFRESH = bool(os.environ.get(
"AW_OWNER_REFRESH"))` module constants (read at import, the file's `AW_CHROME`/
`AW_NODE_MODULES` convention); the explicit ten into `_write_surface` (comment: explicit
list, never a glob); the unconditional in-checkout copy deleted and re-inserted gated on
`REFRESH` AFTER the write-surface assert (assert statement verbatim; 812's loop gained only
the mechanical `SNAPSHOT_VIEWS` reuse - R1); module + `_run_one` + test A + test B
docstrings describe the pinned-snapshot regime (settle clause worded against the merged
reality: isMoving + ~700 ms render-quiet) and name `AW_OWNER_REFRESH=1`. PROBE untouched
(extract + `node --check` clean). `git diff main` = exactly those four hunk families, no
PNG hunks (811 commits the one-time re-pin).

**Verification (all this session, agent/a, TMPDIR=/tmp/loop-ancient-works.a):** T1 unflagged
pair x2 (80.28s/79.34s; both `2 passed`; `git status --porcelain docs/site_flow/` EMPTY
after each). T2 flagged pair x2 (`AW_OWNER_REFRESH=1`, 79.17s/80.07s; both `2 passed`);
byte reproducibility run1->run2 = 8/10 identical, B_1-card + B_5-reload re-encode at the
byte level. T3 the driver's exact gate: full suite 195 passed / 1 skipped / 0 failed
(670.37s, matches the current baseline), docs/site_flow clean after. In-run double shots
0.0000% on all ten of the flagged run #2's retained trees (zero `[warn] settle` observable
in them; the unflagged runs' logs were pruned by pytest retention, but a passed run with
812's double shot in hand is a settled run - a mid-transition capture fails the assert).

**Fact for 811/810 - the it.241 prep's premise is STALE:** main's committed ten are NOT
the 2026-10-13/14 pre-settle bytes (28.6-33.6% content drift) it described - the 812/814-era
sessions ran the old-regime unconditional copy with the SETTLED recipe, and the driver's
sync commits (f44c6035/b2e8f872/197085de on agent/a) swept the settled re-encodes into main
(814's own claim: "vs main's goldens all ten <=0.0451%" - only possible for settled-era
goldens). Measured here: flagged run #2's fresh renders vs main's committed bytes = all ten
<=0.0006% of pixels at threshold 32 (throwaway PIL, same metric as `_shot_diff`). So 811's
one-time `AW_OWNER_REFRESH=1` re-pin produces NO content change - at most byte-level
re-encoding of B_1-card/B_5-reload; word its docs note and PITFALLS rewrite (box 3: retire
the R5 restore workaround, name the flag) accordingly. The flag's canonical spelling is now
`AW_OWNER_REFRESH=1`, named in the module and both test docstrings.

**If the driver returns this file:** no open sub-work; re-confirm the full suite green and
the ten PNGs clean against main, then hold. The chain continues: 810 (final verification;
waits on 812+813 = both done) -> 811 (one-time refresh + re-commit, docs note, PITFALLS
rewrite) -> 242.
