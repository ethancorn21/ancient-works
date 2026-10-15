Status: open
Depends on: none
Touches: fit/src_roman_maclauchlan.py, tests/test_src_roman_maclauchlan.py

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

- [ ] `_canon_norm` zeros `location_check.checked` (guard: absent field passes through);
      `stage()` still stamps the live date into the rows it writes and the idempotency test
      (test_stage_writes_one_row_per_file_and_is_idempotent) passes unchanged.
- [ ] The test passes in isolation on a tree where the canonical row's checked date differs
      from today (the 199 state: canonical 2026-10-14, staging date 2026-10-15):
      `.venv/bin/python -m pytest tests/test_src_roman_maclauchlan.py -q -p no:cacheprovider`
      all green - i.e. the red cannot come back from date skew alone (verify it passes on
      two different days of the week, or with the canonical copy's date altered in both
      directions, inside one run).
- [ ] The new date-only-differs-does-not-fire control and the unchanged qid-differs-fires
      control both pass; no assertion in any other test of this file was edited or deleted.
- [ ] tests/golden/src_roman_maclauchlan_sample.json is byte-identical before and after
      (the golden path already normalizes; this change must not move it).
- [ ] No new reds against the branch suite at claim time (.venv/bin/python -m pytest tests/
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

(2026-10-15, iteration 199, agent c - created, nothing built yet.)
