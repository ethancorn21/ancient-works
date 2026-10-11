Status: open
Depends on: 001
Touches: tools/gate_heldout.py, tests/test_gate.py

# 218: gate-holdout: let post-registration hand fits coexist with the frozen one-shot registration

## Goal
docs/gate.md section 3 registered the one-shot measurement of the fit gate over exactly the 20
named pre-registration hand-fit documents, and `tools/gate_heldout.py::partition()` re-derives
that registration from `data/db/platefits/`: it fails loudly ("the registered partition is void")
whenever the number of NON-automatic documents is not 20 (802 already made the name list
non-auto-only, so the batch's automatic documents do not count). But every new HAND-fit document
DOES count: 206 (Mackenzie p.212) has committed the 21st,
`shotwick-castle-q7502621.c_e6e5490609414bb9`, and 207a/b/c (the Roman hand fits) add more. Each
one aborts the section-6 command and fails
`tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees`, stalling the task that
wrote it. The registration names the 20 - the frozen set is those named 20, not "whatever is in
the directory". This task changes `partition()` so that all 20 named documents must still be
present and unchanged (a missing or renamed registered name fails loudly, as today), while
additional post-registration hand documents are tolerated: they are excluded from the one-shot
held-out proof (the seed-20260108 partition is still derived over the named 20, so
tests/golden/gate_heldout.txt and docs/gate.md section 9 reproduce byte for byte). The
production fit gate (fit_gate.gate) keeps applying to those documents as before - this tool only
excludes them from the one-shot measurement; it never re-scores them here. docs/gate.md stays
untouched (section 1's "not to be changed" stands; per the 802 precedent, any clarifying wording
lives in the tool's docstrings).

## Acceptance criteria
- [ ] `partition()` fails loudly, as today, when any of the 20 names registered in docs/gate.md
      section 3 (the `REGISTERED` held+dev lists) is missing from, or renamed among, the
      non-automatic documents in `data/db/platefits/` (including a registered document that
      gained `"auto": true`).
- [ ] When all 20 registered names are present, additional non-automatic (hand) documents are
      tolerated: excluded from the held/dev derivation, so the seed-20260108 partition,
      `check_registered`, and the section-6 command's stdout (tests/golden/gate_heldout.txt,
      40 held + 60 dev lines) are byte-identical whether the directory holds exactly the
      registered 20 or the 20 plus any number of post-registration hand documents. The
      additional documents are not scored here: they stay subject to the production fit gate
      (fit_gate.gate) at fit time as usual, and nothing is printed about them (the golden is
      compared byte for byte in the tests).
- [ ] tests/test_gate.py is green and pins the new behaviour with no network and no writes to
      the repo tree: a committed test covers (a) an extra hand document present (stub documents
      in a temp dir, or a temp copy of the checkout) -> partition() returns held/dev equal to
      the registered lists, and (b) a registered name missing -> it fails loudly. The
      state-agnostic bar (the 803 precedent, verified at implementation and recorded in this
      task's DECISIONS entry): on a temp copy of the checkout with exactly the registered 20,
      and on a copy with the 20 plus the additions, `.venv/bin/python tools/gate_heldout.py`
      reproduces the golden byte for byte in both states.
- [ ] On the current checkout (21 non-auto documents: the 20 + shotwick), `.venv/bin/python
      tools/gate_heldout.py` completes and prints the registered tables, and
      tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees passes (the 4th of
      206's four red tests). tests/golden/gate_heldout.txt and docs/gate.md are not regenerated
      or edited (a diff is a finding, per 802's box 2, not a silent rewrite).

## Notes
- Filed by agent a (task 206), iteration 64. 206's platefit doc is the 21st hand document.
  206's four red tests: (1) tests/test_serve.py::test_platefits_docs_match_sites and (2)+(3) the
  two union tests in tests/test_batch_eu.py - owned by 211 (it builds shotwick's site) - and
  (4) the test named in box 4 above - owned by this task. 206 waits on this task through its
  own `Depends on:` line; the dependency is one-way (see below).
- 207a/b/c (agent c, the Roman hand fits) add further hand documents and hit the same wall; when
  they do, they add 218 to their own `Depends on:` line (they own their task files). Design for
  ANY number of post-registration hand documents, not specifically shotwick.
- Flagged for the human/driver (carried from 206's hand-over, since this touches the frozen
  registration's spirit): docs/gate.md section 1 is the frozen pre-registration ("not to be
  changed") and section 3 names the 20. The recommended resolution recorded here: the frozen set
  is the named 20, so tolerating additional hand documents does not void the one-shot proof
  (it is a proof about the named 20), and new hand documents stay fully gated in production.
  802's precedent: no docs/gate.md wording change is needed; the clarification lives in the
  tool's docstrings.
- `Depends on:` is 001 only (done) - state-agnostic per the 802 / 203a-4g lesson: the change
  must pass on any checkout (plain main with exactly the registered 20, or a branch with the
  20 + additions), so it does not wait on 206 or 207 (a part must not wait for the task that
  waits for it). It builds on 802's merged non-auto filter (802 is done and in main).
- Read before implementing: tasks/802-gate-holdout-auto-docs.md (the non-auto filter, its
  state-agnostic verification, and the golden-stays-unchanged bar) and
  tasks/803-review-queue-rebaseline.md (the temp-copy-of-checkout two-state verification
  technique); PITFALLS.md "data/db/platefits/ mixes hand fits and automatic ones" and the
  gate entries under fit/; tools/gate_heldout.py's module docstring (it already documents the
  non-auto filter and the void-registration failure).
