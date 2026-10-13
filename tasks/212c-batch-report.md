Status: in-progress
# 212c: docs/batch.md - the final report for the owner
Depends on: 212b
Touches: fit/cover.py, docs/batch.md, tests/test_cover.py

## Goal
The report the owner reads: counts per outcome (fit: hand / matcher / human-saved;
review item; no picture found), a seeded 20-sample of automatic (matcher) fits with a
page URL each for the owner's 18/20 check, and the "no picture found" list with what was
searched per site.

## Acceptance criteria
- [ ] `python3 fit/cover.py report` writes docs/batch.md from the store, seed recorded in the file.
- [ ] Test: the sample is reproducible from the recorded seed; the counts add up to the built-site total.

## Hand-over

(2026-10-13, iteration 234, agent a - first session on 212c. Lead's instruction: first
session = fit/cover.py report plus its test, commit; then docs/batch.md from it; "No
census re-measuring - the store is the source." 212b was closed on main by the lead.)

- The report phase was already in fit/cover.py (212a wrote it) and was verified this
  session against the live store - no code change needed: `.venv/bin/python fit/cover.py
  report` (system python3 has no numpy - use the driver's venv) wrote docs/batch.md:
  499 built; buckets 19 hand-golden / 0 human-saved / 24 automatic / 106 review item /
  244 no picture found / 106 uncovered-needs-attention (sums to 499); the invariant line
  honestly prints "the invariant is broken" for the 106 (the loop phase never ran live -
  the hand-over's honest-state note; the number moved from the 103 estimated at 0e6d5df
  because the store moved - not re-measured per the lead); the sample is
  random.Random(20261012) over the 36 by:agent docs (20 drawn, page URL + gate median
  each - same convention as docs/batch_us.md); the no-picture table is 244 rows = exactly
  the no-picture bucket (cross-checked 1:1 this session; no fitted site carries an open
  no-picture item; one batch-era string renders as-is - a with-candidate site outside
  the 212a search set, the store's own record).
- Test: tests/test_cover.py extended (212a's 5 tests + new test_report). The run fixture
  now runs the report phase on the same tree AFTER the integrity snapshots, under the
  re-armed socket guard, with a fixed at= (docs/batch.md is in IN_PLACE - copied, not
  hard-linked - so its in-place rewrite never reaches the checkout). test_report checks:
  the recorded seed == SEED_212; the automatic total the file names == the store's;
  the six buckets sum to the built-site total the report names, and the invariant line
  agrees with the uncovered bucket; the sample is exactly random.Random(recorded seed).
  sample(sorted auto ids, 20) in draw order, each row with its page URL and gate score;
  the no-picture table names every open no-picture-and-no-candidates item with a
  non-empty searched record. Green this session; suite: 155 passed, the one red is
  307bb's pre-existing gesture test (agent c's 307 series, as classified in iter-228),
  1 skipped.
- Remaining (this session, per the lead): regenerate docs/batch.md fresh
  (`.venv/bin/python fit/cover.py report` - the working-tree preview is stale) and commit
  it, tick both boxes, set done. If the lead runs the loop phase live later, re-run the
  report before any re-publish: it reads the store, not a snapshot.
