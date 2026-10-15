Status: open
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

- [ ] An unflagged run leaves every `docs/site_flow/307d_*.png` in the checkout byte-identical
      (verified by the test's write-surface hash or an equivalent check); the explicit refresh flag
      (the one named in the docstring) re-renders all ten from a run and writes them into
      `docs/site_flow/`.
- [ ] No existing check changed (same flow, same asserts); the refresh flag, the write-surface
      addition and the docstrings are additive.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`) and
      `git status` on `docs/site_flow/` is clean after an unflagged run.
