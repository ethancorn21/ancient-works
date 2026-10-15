Status: done
Depends on: none
Touches: fit/src_roman_maclauchlan.py, tests/test_src_roman_maclauchlan.py, PITFALLS.md

# 817: The 207b roman (e) join - zero the volatile checked date out of _canon_norm (the now() stamp vs the 230 re-stamp daily flake)

(2026-10-15, iteration 199, agent c, filed from 809's step-4 A/B: the maclauchlan red's root
cause measured, not just attributed to 230's timing)

## Why this task exists (read first)

tests/test_src_roman_maclauchlan.py::test_check_staged_joins_and_passes is red on main with
`join: staged site luguvallium-q71551754 differs from its canonical row in extras.jsonl`.
809 measured the root cause at 199: stage() stamps `location_check.checked = now()` (the
staging date, and `evidence.checked = now()` on the file row), but `_canon_norm` is a full-row
dump (json.dumps, sort_keys) with no date zeroing - so the FRESH staged row (today's date)
differs from the canonical row (re-stamped by 230's re-run, landed on main at 197 with
2026-10-14) on the checked date ALONE, every day after any re-stamp until the next one.
It self-heals (the next 230 re-stamp re-syncs it; the test was green on 2026-10-14 and red on
2026-10-15 - the 197 "resolved" state lasted exactly one day), but it recurs, and it is the
exact red that made the driver reject 814's done-claim (the 816 file, "Why this task exists"):
it keeps biting other agents' suite gates until the comparison stops treating a provenance
stamp as content. The module's own golden `_norm` already zeros both volatile `checked` dates
for exactly this reason ("they vary with the staging") - the identity check should ignore
them too.

## Goal

In fit/src_roman_maclauchlan.py: `_canon_norm` zeros `location_check.checked` before the
sorted-key dump (the same `0000-00-00` treatment the golden `_norm` already applies to that
field, with the same `if ... .get("checked")` guard so a row without the field passes
through). The rows stage() writes and the canonical/staged files keep the live dates
unchanged: the date is honest provenance, only the (e) identity comparison normalizes it.
Site rows carry no `evidence` block, so `location_check.checked` is the only volatile field
in the rows (e) compares. In tests/test_src_roman_maclauchlan.py: extend
test_check_staged_joins_and_passes with the regression control - a canonical extras copy
whose staged-site row differs from the freshly staged row ONLY in `location_check.checked`
joins clean (exit 0, no `join:` line, the evidence PASS line as today), while the existing
content-differs control (c: the qid alteration) still fires exactly one `(e)` line as today.
No other behavior changes.

## Acceptance criteria

- [x] `_canon_norm` zeros `location_check.checked` (guard: absent field passes through);
      `stage()` still stamps the live date into the rows it writes and the idempotency test
      (test_stage_writes_one_row_per_file_and_is_idempotent) passes unchanged.
- [x] The test passes in isolation on a tree where the canonical row's checked date differs
      from today (the 199 state: canonical 2026-10-14, staging date 2026-10-15):
      `.venv/bin/python -m pytest tests/test_src_roman_maclauchlan.py -q -p no:cacheprovider`
      all green - i.e. the red cannot come back from date skew alone (verify it passes on
      two different days of the week, or with the canonical copy's date altered in both
      directions, inside one run).
- [x] The new date-only-differs-does-not-fire control and the unchanged qid-differs-fires
      control both pass; no assertion in any other test of this file was edited or deleted.
- [x] tests/golden/src_roman_maclauchlan_sample.json is byte-identical before and after
      (the golden path already normalizes; this change must not move it).
- [x] No new reds against the branch suite at claim time (.venv/bin/python -m pytest tests/
      --ignore=tests/test_gate.py -q -p no:cacheprovider); if a red appears that also fails
      on this branch without the change (A/B it the 809 way), log it in DECISIONS and stop.

## Notes

- The 809 module (fit/src_roman_horsley.py) carries the IDENTICAL copied `_canon_norm` and
  `now()` stamp: that fix is 818, a parallel task (different module, different test file,
  no shared files - claimable independently of this one).
- fit/merge.py's own `norm` is ALSO a full-row dump, but it is deliberately out of scope:
  the 211 merge regenerates the canonical rows from the staged source (a re-stamp is a
  rewrite, first-row-wins on id - no conflict check), and merge.py is the 211/230 family's
  module (agent a's 230 is on it). If the claiming agent finds the merge DOES compare
  checked dates somewhere, stop and file it as a 230-lane note, don't touch merge.py.
- Verified at 199 on current main: all 9 staged roman site rows are dict-identical to their
  canonical twins (the committed staging files are in sync with 230's re-stamp); a fresh
  stage() differs from canonical on location_check.checked ONLY (2026-10-15 vs 2026-10-14)
  - that single field is the entire red.
- After any full-suite run the ten docs/site_flow/307d_*.png may be re-encoded (the 307d
  owner check) - restore main's bytes before committing; this task's own claim run is fine
  since the box only needs this file's tests, but a full-suite A/B for the no-new-reds box
  must follow that rule (PITFALLS, the 809/816 entries).

## Hand-over

(2026-10-15, iteration 239, agent a - DONE, all five boxes verified, no open next step)

**What landed (one commit, module + test + PITFALLS only; no data change):**
- fit/src_roman_maclauchlan.py: (1) `_canon_norm` zeroes `location_check.checked` to 0000-00-00
  before the sort-key dump - the same guard/idiom as the golden `_norm` (`isinstance(lc, dict)
  and lc.get("checked")`), so a row without the field passes through; the (e) identity compare
  no longer treats the provenance stamp as content. (2) `stage()` restored to the live `now()`
  stamp (`import time` + `def now(): return time.strftime("%Y-%m-%d")` back in the module;
  230 it.237's interim `CHECKED = "2026-10-14"` constant and its comment removed) - per my 230
  it.238 cross-lane note ("restore the live stamp after zeroing") and this task's box 1: the
  date is honest provenance (the day the row was staged/checked) and is safe to vary because
  the join ignores it. The `_norm` docstring's stale "see CHECKED" reference restored to the
  original wording; the `--check` docstring line notes the modulo-date. Site rows carry no
  `evidence` block (verified: 0 of 202 extras / 0 of 12603 sites / 0 of 9 roman rows), so
  location_check.checked is the only volatile field the (e) compare sees.
- tests/test_src_roman_maclauchlan.py::test_check_staged_joins_and_passes: extended with (d)/(e)
  regression controls - a canonical extras copy whose staged-site row differs from the freshly
  staged row ONLY in `location_check.checked`, in BOTH directions of the skew inside one run
  (today-1d and today+1d), each joins clean (exit 0, no `join:` line, the evidence PASS line);
  (a)/(b)/(c) untouched (only (a)'s now-stale comment corrected: post-211/230 the real canonical
  extras DOES contain the roman site, so (a) exercises the date-skew join against the real files).
- PITFALLS.md: the 809-filed (e) checked-date entry corrected (maclauchlan half FIXED by 817
  it.239; horsley half still open in 818); PITFALLS.md added to this task's Touches line.

**Verification (all this session, 2026-10-15 = the 199 state itself: canonical rows checked
2026-10-14, staging date 2026-10-15):**
- module tests: 4 passed (6.9 s) - (a) ran against the real canonical files with the live-skewed
  staged row and joined clean: the daily red cannot come back from date skew alone.
- A/B the 809 way (scratch tree /tmp/ab817 = repo skeleton + the pre-it.237 module from
  `git show fa230d24^:fit/src_roman_maclauchlan.py` + the NEW test file): 1 failed / 3 passed -
  the failure is the exact 199 red (`join: staged site luguvallium-q71551754 differs from its
  canonical row in extras.jsonl`, in (a)); the new test catches the old behavior. Direct norm
  check: old `_canon_norm` distinguishes the date-only-differs pair (False), the new one equates
  it (True); an absent location_check passes through byte-identical.
- golden: md5 04637684823db2dc36c14219a7eecd16 before and after the change AND after the full
  suite run - byte-identical.
- branch suite at claim time (driver's exact command, .venv/bin/python -m pytest tests/
  --ignore=tests/test_gate.py -q -p no:cacheprovider): **191 passed, 1 skipped, 0 failed**
  (584.85 s) - no new reds, none at all. Note: 192 collected vs the it.238 run's 195 on a
  byte-identical tests/+data tree (git diff b30f650e..HEAD: only PITFALLS/PROGRESS/307d-PNGs) -
  the delta is environment-dependent parameterization over local (gitignored) build state in
  the batch/owner-check test families (they iterdir local trees at collection), not my change
  (it is test-count-neutral: the module test file still collects 4 tests, verified).
- working tree: the 307d PNGs re-encoded by the full-suite owner-check run (3 files this run) +
  the 4 pre-session dirty ones restored to committed bytes before the commit.
- fit/merge.py checked per the Notes: its `norm` is a raw full-line dump that never compares the
  checked date (the 211 merge regenerates rows, first-row-wins, no conflict check) - out of
  scope, no 230-lane note needed.

**For 818 (agent c's twin, the horsley module) - the recipe:** fit/src_roman_horsley.py `_canon_norm`
(its line ~623) gets the identical zeroing (its `_norm` idiom already shows the guard); its `stage()`
ALREADY stamps `now()` (the it.237 frozen constant was only ever in the maclauchlan module - 809's
latent flag was answered by filing 818, not by changing that module), so 818 = the zeroing + the
same (d)/(e) both-directions controls in tests/test_src_roman_horsley.py, nothing else. The PITFALLS
entry is left accurate for that half.
