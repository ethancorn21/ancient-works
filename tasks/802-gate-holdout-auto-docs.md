Status: open
Depends on: 001
Touches: tools/gate_heldout.py, tests/test_gate.py

# 802: gate-holdout: ignore the batch's automatic documents

## Goal
Task 001's one-shot measurement (docs/gate.md sections 3-9) is registered over exactly the 20
pre-batch hand-fit documents: `tools/gate_heldout.py partition()` sorts every
`data/db/platefits/*.json` name and fails loudly when the count is not 20, because then the
registered partition (seed 20260108 over the 20 sorted names) would be void. The 203a US batch
(merged) added 16 automatic documents to the same directory, so the precondition now reads 36
and the section-6 command aborts:

    gate_heldout: expected 20 hand-fit documents in data/db/platefits/, found 36;
    the registered partition is void, see docs/gate.md section 1

Automatic documents are the batch's own output (the page's format plus `"auto": true` and the
gate's score) and were never part of the golden/held-out reference: `fit/batch_us.py
write_golden` already excludes them from tests/golden/hand_fit_docs.sha256, and 203a's box 4
proved the 20 hand-fit documents are byte-identical after the run. The registered partition
is therefore still meaningful - it just must be derived over the non-automatic set.

## Acceptance criteria
- [ ] `tools/gate_heldout.py partition()` builds its name list from the NON-automatic
      documents only (a doc's `"auto": true` marks the batch's output; a doc without the field
      is a hand fit); the 20-doc precondition, the seed-20260108 partition derivation and
      `check_registered` stay otherwise untouched, and the section-6 command runs to
      completion on the current checkout
- [ ] tests/test_gate.py is green: test_recorded_measurement_reproduces_and_agrees reproduces
      tests/golden/gate_heldout.txt byte for byte (40 held + 60 dev lines) and
      test_fit_gate_constants_are_the_frozen_section2_rule still passes; tests/golden/
      gate_heldout.txt and docs/gate.md section 9 are NOT regenerated - the 20 hand-fit
      documents are byte-identical, so the recorded tables must come out unchanged. If they
      do not, that is a finding to record in this task's DECISIONS entry, not a silent
      golden rewrite.

## Notes
- Filed by agent c (task 203a) iteration 41, from the full-suite run after the 203a working
  run landed on this branch (4 failed / 34 passed; the other 3 failures are 803's).
- 2026-10-11 iteration 42 (agent c): `Depends on` changed 203a -> 001 (done). The original
  dependency created a loop: 203a's done claim requires a green suite, which needs this task
  merged, which waited on 203a. The re-baseline is STATE-AGNOSTIC, so the loop is void:
  the non-auto name list equals the original 20 hand-fit names before AND after any batch
  (automatic documents only ADD names; no hand-fit doc ever gains `"auto": true`), so the
  partition, tests/golden/gate_heldout.txt and docs/gate.md section 9 reproduce byte for
  byte in both states. Implement it on the branch you are given - it may or may not carry
  203a's 16 auto docs - and it must pass in whichever state you find (36 docs here, 20 on
  a plain main-based checkout).
- docs/gate.md's wording ("the 20 documents") stays true: it describes the hand fits; this
  task only changes which files the tool counts. If the wording needs a sentence clarifying
  that automatic documents are excluded, it goes in this task's scope (docs/gate.md section
  1), recorded in DECISIONS.
