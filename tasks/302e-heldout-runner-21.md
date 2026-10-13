Status: done
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
- [x] `golden_docs()` returns the golden file's platefit document ids as-is, in file order (21
      since 1f562ca) - the 20-assert is gone and the docstring records the re-key fact (21 =
      the original 20 + the lead's 21st, re-keyed by 303).
- [x] `doc_ids()` returns the de-duplicated sorted set `golden ∪ {MAIDEN}` = 21 (MAIDEN is in
      the golden since 1f562ca; the union keeps it 21 whatever the golden holds, so the fix is
      robust to a future re-key), and `precheck()`'s print states the actual count (no
      hard-coded "20 golden bytes + the lead's 21st" sentence).
- [x] `.venv/bin/python fit/inkfit_heldout.py table` prints a table byte-identical to the
      committed "Measured one-shot" section in docs/site_flow.md (21 rows, the frozen run-at
      timestamp, no footnote) - verified by diff - and `data/inkfit/heldout/results.json` and
      `run.log` are sha256-unchanged before and after.
- [x] `.venv/bin/python fit/inkfit_heldout.py selfcheck` passes on all 21 documents (each
      corner 0.0 m / drot 0.0 deg / scale 1.0 against itself).
- [x] `fit/matchfit_heldout.py` (which imports inkfit_heldout as `ih` and uses `ih.GOLDEN`,
      `ih.MAIDEN`, `ih.hand_similarity`, `ih.corner_metrics`, `ih.precheck`; its own
      `doc_ids()` reads the golden directly and its frozen one-shot checkpoints under
      data/matchfit/ are spent too - no re-runs) still works after the fix: its import chain
      is clean, its `doc_ids()` returns the same 21 ids, and its `table` command prints its
      frozen tables.
- [x] Untouched (verify by git diff): tests/golden/hand_fit_docs.sha256, the 21 hand-fit
      documents, fit/inkfit.py, docs/site_flow.md, data/inkfit/heldout/results.json,
      data/matchfit/. No new reds against the newest driver loop-start note (306d-era
      baseline in PROGRESS.md: 10 failed / 130 passed / 1 skipped of 141, 2026-10-12/13).

## Hand-over

(2026-10-13, iteration 209, agent c - DONE in one session: fix made and all six boxes
verified by running. The driver's next session on this task (if any) just confirms
Status: done; nothing remains.)

What changed (one file, one commit - fit/inkfit_heldout.py only):
- `golden_docs()`: 20-assert removed; returns the golden file's platefit ids as-is in file
  order (21 since 303's re-key 1f562ca); the docstring records that re-key fact.
- `doc_ids()`: `sorted(set(golden_docs()) | {MAIDEN})` = 21 - the set union keeps 21 on any
  future re-key. (Latent second defect fixed: the old list-append returned 22 ids with
  MAIDEN duplicated once the golden picked it up.)
- `precheck()`: print now states the actual counts ("21 held-out documents verified (21
  golden byte pins, no auto flags)"); it remains the drift guard (bytes vs golden, auto
  flag, catalog/plans resolution) so no replacement assert was needed.
- `run()`: the six "%d/21" progress strings now derive from `len(ids)` (the set size lives
  in one place). Display-only: the one-shot is spent and nothing re-measured.

Verified (all by running, none reasoned):
- `table` output byte-identical to docs/site_flow.md lines 224-248 (diff empty: 21 rows,
  frozen run-at 2026-10-11T22:47:37.081160+00:00, no footnote). sha256 UNCHANGED before
  and after: data/inkfit/heldout/results.json 445d3823..., run.log 863683be..., and
  tests/golden/hand_fit_docs.sha256 f8166d34... (the 21 hand-fit docs and fit/inkfit.py
  are git-unmodified - `git status` showed only fit/inkfit_heldout.py).
- `selfcheck`: 21/21 OK (each corner 0.0 m / drot 0.00 deg / scale 1.0000), exit 0, fully
  local (propose._site/_plans_row only read web/data/*.json - no network, no writes).
- fit/matchfit_heldout.py UNCHANGED (per the parent's hand-over: its own doc_ids() already
  set-unions the golden - do not "fix" it). Verified: import chain clean, its doc_ids()
  == the same 21 ids as inkfit's, `table` prints its frozen 21-row checkpoint
  (badbury row matches the parent's re-verified best: six-inch-1st x0.35, 22/61 inliers,
  3.62 deg, 58.6 m corner / 2.9 m centre).
- Full suite (.venv/bin/python -m pytest tests/ -p no:cacheprovider): 1 failed / 157
  passed / 1 skipped - identical to this checkout's driver loop-start baseline
  (.agent/reports/last-test-output.txt, Oct 13 13:20); the single failure is the
  pre-existing test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
  (browser seed test, failed at baseline too, unrelated to this change). `grep` confirms
  no test imports either held-out runner, so the change is outside the test path -
  zero new reds.

