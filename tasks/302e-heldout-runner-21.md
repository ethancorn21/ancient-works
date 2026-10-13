Status: open
Depends on: 302a
# 302e: Held-out runner compatibility - the golden is 21, the runner still asserts 20
Touches: fit/inkfit_heldout.py, fit/matchfit_heldout.py, data/inkfit/

## Goal
Since 303's re-key (1f562ca) the golden file `tests/golden/hand_fit_docs.sha256` pins 21 platefit
documents (the original 20 plus the lead's 21st, `maiden-castle-q1232816.c_c20ff6b1f16d173d`),
but `fit/inkfit_heldout.py::golden_docs()` still asserts exactly 20, so every command of the
ink one-shot runner dies with SystemExit "expected the 20 golden hand-fit documents, found 21"
(re-verified by running in iteration 208: `table` dies; `run` and `selfcheck` call the same
function). The one-shot measurement is SPENT (checkpoint `data/inkfit/heldout/results.json`:
21 entries, 0 errors, 0 re-runs, fixed at 2026-10-11T22:47:37.081160+00:00; the table in
docs/site_flow.md is frozen), so this is a compatibility fix - make the runner work against the
re-keyed golden without changing a single measured number and without re-running anything.

## Acceptance criteria
- [ ] `golden_docs()` returns the golden file's platefit document ids as-is, in file order (21
      since 1f562ca) - the 20-assert is gone and the docstring records the re-key fact (21 =
      the original 20 + the lead's 21st, re-keyed by 303).
- [ ] `doc_ids()` returns the de-duplicated sorted set `golden ∪ {MAIDEN}` = 21 (MAIDEN is in
      the golden since 1f562ca; the union keeps it 21 whatever the golden holds, so the fix is
      robust to a future re-key), and `precheck()`'s print states the actual count (no
      hard-coded "20 golden bytes + the lead's 21st" sentence).
- [ ] `.venv/bin/python fit/inkfit_heldout.py table` prints a table byte-identical to the
      committed "Measured one-shot" section in docs/site_flow.md (21 rows, the frozen run-at
      timestamp, no footnote) - verify by diff - and `data/inkfit/heldout/results.json` and
      `run.log` are sha256-unchanged before and after.
- [ ] `.venv/bin/python fit/inkfit_heldout.py selfcheck` passes on all 21 documents (each
      corner 0.0 m / drot 0.0 deg / scale 1.0 against itself).
- [ ] `fit/matchfit_heldout.py` (which imports inkfit_heldout as `ih` and uses `ih.GOLDEN`,
      `ih.MAIDEN`, `ih.hand_similarity`, `ih.corner_metrics`, `ih.precheck`; its own
      `doc_ids()` reads the golden directly and its frozen one-shot checkpoints under
      data/matchfit/ are spent too - no re-runs) still works after the fix: its import chain
      is clean, its `doc_ids()` returns the same 21 ids, and its `table` command prints its
      frozen tables.
- [ ] Untouched (verify by git diff): tests/golden/hand_fit_docs.sha256, the 21 hand-fit
      documents, fit/inkfit.py, docs/site_flow.md, data/inkfit/heldout/results.json,
      data/matchfit/. No new reds against the newest driver loop-start note (306d-era
      baseline in PROGRESS.md: 10 failed / 130 passed / 1 skipped of 141, 2026-10-12/13).
