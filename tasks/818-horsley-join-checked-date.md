Status: done
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

- [x] `_canon_norm` zeros `location_check.checked` (guard: absent field passes through);
      `--dry` staging still idempotent (0 appended) and the rows written keep the live date.
- [x] `--check` under the socket-block wrapper still exits 0 with zero `join:` lines and
      `evidence: 17 rows, 17 pass, 0 fail, 0 no-tie` (the committed rows are in sync with
      canonical, so the normalization must not change any current outcome).
- [x] The new date-only-differs-does-not-fire control and the unchanged qid-differs-fires
      control both pass in tests/test_src_roman_horsley.py; no assertion in any other test
      of this file was edited or deleted; the no_network fixture and the import-by-path
      setup stay as the 809 box built them.
- [x] tests/golden/src_roman_horsley_sample.json is byte-identical before and after
      (the golden path already normalizes; this change must not move it).
- [x] No new reds against the branch suite at claim time (.venv/bin/python -m pytest tests/
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

(2026-10-15, iteration 201, agent c - BUILT AND VERIFIED; all five boxes ticked, ready for the
driver's re-check.)

Done this session (one step = the whole 818 recipe):
- fit/src_roman_horsley.py: `_canon_norm` zeros `location_check.checked` ("0000-00-00", the same
  `isinstance(lc, dict) and lc.get("checked")` guard the golden `_norm` uses) before the
  sorted-key dump; the `join_problems` (e) docstring documents the both-sides zeroing. `stage()`
  and every row it writes keep the live date (that code is untouched).
- tests/test_src_roman_horsley.py: new (d-d) negative control in `test_check_negative_controls`
  (a canonical ardoch row differing from the staged row ONLY in `location_check.checked` joins
  clean; the (d-c) qid-alteration control and every other assertion unchanged - the diff is
  additions only: two docstring lines + the (d-d) block).
- Pre-fix proof (the 809 way): the control run against the UNFIXED module fails with exactly one
  line, `join: staged site ardoch differs from its canonical row in extras.jsonl`, exit 1 - the
  control pins the daily flake. Post-fix the same state joins clean (exit 0, no join line).
- Verified: test file 5/5 green; `--dry` and a real `--stage` both 0-appended with the staging
  files byte-identical (sha256 vs /tmp/818-baseline-shas.txt); a scratch re-stage (one file row
  + one site row deleted) re-appended rows carrying today's live date (2026-10-15) and
  `_canon_norm` zeroed it; `--check` exits 0, zero join lines, `evidence: 17 rows, 17 pass, 0
  fail, 0 no-tie`; the golden is byte-identical (af87ec84... before and after).
- Full suite WITH the change: 3 failed / 188 passed / 1 skipped (589 s). A/B with both files
  restored to HEAD: the SAME 3 reds (test_owner_check ×2 = agent a's 307d lane;
  test_src_roman_maclauchlan ×1) - no new reds from this change, logged in DECISIONS. The two
  re-encoded 307d PNGs were committed restored to main's bytes.

What a later agent touching this file needs to know:
- The fix is COMPLETE in this module; the twin 817 (the maclauchlan module) is still open. Main now
  carries agent a's fa230d24 ("230: done") with an INTERIM patch to that module (a fresh re-stage
  keeps a stored CHECKED constant instead of now() - per the 207 note, it.200: that constant
  self-ages at the next 230 re-stamp, so 817's _canon_norm zeroing remains the permanent fix there;
  whoever claims 817 should read fa230d24 first, since its test's "passes on two different days"
  criterion now plays out against the stored-constant shape, not a now() stamp). fa230d24 is NOT
  yet in this branch (its last main sync predates it); my branch is untouched in that file, so the
  driver's next merge is clean.
- PITFALLS line ~1105 ("...until 817/818 zero the date out") is half-stale now (818 done); per
  818's Notes neither task edits PITFALLS - the 817 owner or the driver should update it.
- This branch is behind main on fit/src_roman_maclauchlan.py (230's fix), tests/test_owner_check.py
  and the deleted tasks/245 (agent a's 307d re-split): all untouched in my worktree, so the
  driver's next merge of main should be clean.
- Scratch scripts /tmp/818-prefix-repro.py and /tmp/818-freshdate.py (plus the two orig file
  copies) are throwaway, not part of the repo; delete at will.
