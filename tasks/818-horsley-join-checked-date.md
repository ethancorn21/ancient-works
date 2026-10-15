Status: open
Depends on: none
Touches: fit/src_roman_horsley.py, tests/test_src_roman_horsley.py

# 818: The 809 horsley (e) join - zero the volatile checked date out of _canon_norm (the same latent as 817)

(2026-10-15, iteration 199, agent c, filed from 809's step-4 A/B: the identical latent in
this book's own module - green today only because the check reads the committed rows)

## Why this task exists (read first)

fit/src_roman_horsley.py's `_canon_norm` was copied verbatim from 207b (the family pattern:
each book module self-contained), so it carries the IDENTICAL latent 817 measured at 199:
`stage()` stamps `location_check.checked = now()` on the site rows (and
`evidence.checked = now()` on the file rows), while `_canon_norm` is a full-row dump with no
date zeroing. The (e) join (join_problems, spec (a)-(f) in the docstring) compares staged
SITE rows against the canonical site rows - today the 809 check passes because it reads the
COMMITTED staged rows (in sync with 230's 2026-10-14 re-stamp), but the moment a fresh
stage() of this book runs after any canonical re-stamp, (e) fires on the checked date alone
- the same daily flake that is red on main in the 207b test right now. Fix it in this
module so a re-stage can never flake the book's own check again.

## Goal

In fit/src_roman_horsley.py: `_canon_norm` zeros `location_check.checked` before the
sorted-key dump (the same `0000-00-00` treatment the module's golden `_norm` already applies
to that field, with the same `if ... .get("checked")` guard so a row without the field
passes through). The rows stage() writes and the staged files keep the live dates: only
the (e) identity comparison normalizes. In tests/test_src_roman_horsley.py: extend
test_check_negative_controls with the regression control - a canonical extras copy whose
staged-site row differs from the staged row ONLY in `location_check.checked` joins clean
(no `(e)` line for it), while the existing same-id-different-row control (the qid
alteration) still fires exactly the one `(e)` line as today. No other behavior changes;
the golden sample and test_check_offline's exact PASS lines stay byte-stable.

## Acceptance criteria

- [ ] `_canon_norm` zeros `location_check.checked` (guard: absent field passes through);
      `--dry` staging still idempotent (0 appended) and the rows written keep the live date.
- [ ] `--check` under the socket-block wrapper still exits 0 with zero `join:` lines and
      `evidence: 17 rows, 17 pass, 0 fail, 0 no-tie` (the committed rows are in sync with
      canonical, so the normalization must not change any current outcome).
- [ ] The new date-only-differs-does-not-fire control and the unchanged qid-differs-fires
      control both pass in tests/test_src_roman_horsley.py; no assertion in any other test
      of this file was edited or deleted; the no_network fixture and the import-by-path
      setup stay as the 809 box built them.
- [ ] tests/golden/src_roman_horsley_sample.json is byte-identical before and after
      (the golden path already normalizes; this change must not move it).
- [ ] No new reds against the branch suite at claim time (.venv/bin/python -m pytest tests/
      --ignore=tests/test_gate.py -q -p no:cacheprovider); if a red appears that also fails
      on this branch without the change (A/B it the 809 way), log it in DECISIONS and stop.

## Notes

- 817 is the twin task for the 207b module (fit/src_roman_maclauchlan.py + its test): the
  same one-field change, independent claim (different files - 817 and 818 can run in
  parallel; they share no file except PITFALLS.md, which neither needs).
- The volatile dates in the file rows' `evidence` block are NOT part of any (e) comparison
  (the join compares site rows only; evidence.check reads stored fields and never compares
  dates), so 818 normalizes location_check.checked in _canon_norm only - do not add
  evidence.date zeroing to the join path.
- Verified at 199: the 809 module is green today on current main (the check reads committed
  rows, all 9 staged roman sites dict-identical to canonical under the current
  full-row-dump norm); the latent fires only on a fresh stage() after a re-stamp - the
  809 test's own `test_check_negative_controls` already has the (e) and (f) mechanics to
  hang the date-only control on.
- After any full-suite run the ten docs/site_flow/307d_*.png may be re-encoded (the 307d
  owner check) - restore main's bytes before committing (PITFALLS, the 809/816 entries).

## Hand-over

(2026-10-15, iteration 199, agent c - created, nothing built yet.)
