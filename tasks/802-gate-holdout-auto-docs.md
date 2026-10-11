Status: in-progress
Depends on: 001, 803
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
- [x] `tools/gate_heldout.py partition()` builds its name list from the NON-automatic
      documents only (a doc's `"auto": true` marks the batch's output; a doc without the field
      is a hand fit); the 20-doc precondition, the seed-20260108 partition derivation and
      `check_registered` stay otherwise untouched, and the section-6 command runs to
      completion on the current checkout
- [x] tests/test_gate.py is green: test_recorded_measurement_reproduces_and_agrees reproduces
      tests/golden/gate_heldout.txt byte for byte (40 held + 60 dev lines) and
      test_fit_gate_constants_are_the_frozen_section2_rule still passes; tests/golden/
      gate_heldout.txt and docs/gate.md section 9 are NOT regenerated - the 20 hand-fit
      documents are byte-identical, so the recorded tables must come out unchanged. If they
      do not, that is a finding to record in this task's DECISIONS entry, not a silent
      golden rewrite. (They did come out unchanged: the golden and section 9 are untouched in
      the diff and reproduce byte for byte.)

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
  1), recorded in DECISIONS. (2026-10-11: judged NOT needed - section 1 is the frozen
  pre-registration ("not to be changed") and never promised to count every .json in the
  directory; section 3's "the 20 hand-fit documents in data/db/platefits/" stays literally
  true. The clarification lives in the tool's docstrings. docs/gate.md untouched. See DECISIONS.)
- 2026-10-11 iteration 46 (agent c): the driver rejected the done claim - its re-verification runs the FULL
  suite and it was red: 3 failed / 35 passed, all in tests/test_review.py, which is task 803's file
  (`Touches: tests/test_review.py`; 803 is open, its dependency 201 is done, unassigned). Those 3 tests
  fail identically without this task's change (pre-802 suite: 4 failed / 34 passed; the 4th was 802's
  own, fixed), so the implementation stands as verified in iteration 45 and nothing in it changed.
  802 cannot pass the re-check until 803 is done and merged, so per the team-mode rule `Depends on:`
  now lists 803 and the task parks until 803 is in main. The human already knows about the 802/803 pair
  (203a's ask_human 002).

## Hand-over

**2026-10-11, iteration 46 (agent c): implementation unchanged and verified; the task now parks on
803 (its tests are the only red in the suite) and the driver brings it back when 803 merges.**

- State: `Depends on:` is now `001, 803` (was `001`); status stays in-progress with both boxes
  ticked. The driver's rejection of the iteration-45 done claim was purely the suite being red,
  not anything in this task's two files. No code changed this iteration; the implementation is
  commit af830fb and `git log` shows nothing later touching tools/gate_heldout.py or
  tests/test_gate.py.
- Verified this iteration in the current checkout: full suite `.venv/bin/python -m pytest -q` =
  3 failed / 35 passed; the 3 failures are exactly 803's population
  (test_export_cli, test_page_shows_the_review_list, test_save_resolves_the_item) and they
  pre-date 802 (pre-802 suite: 4 failed / 34 passed; the 4th was 802's own test_gate failure,
  fixed). tests/test_gate.py is green inside the 35.
- Why park, not patch: tests/test_review.py is 803's file (not on my Touches line) and 803 is
  the task that re-baselines those pins to the 89-item post-batch population (803: open,
  `Depends on: 201` - done, `Touches: tests/test_review.py`, unassigned). Patching it here
  would collide with 803's branch and re-litigate its scope; the driver hands it out and merges
  it, and the human has already been told about the 802/803 pair (203a's ask_human 002).
- Next session (when the driver brings 802 back after 803 merged into main): run
  `.venv/bin/python -m pytest -q` in the current checkout; expect 0 failed, then re-file the
  done claim (Status: done). If my two files' tests are red instead, something on main since
  af830fb touched tools/gate_heldout.py / tests/test_gate.py / the data they read - check
  `git log` on those paths and re-derive: the name list must still be the sorted NON-automatic
  documents (20 of them) and the golden must still reproduce byte for byte.
