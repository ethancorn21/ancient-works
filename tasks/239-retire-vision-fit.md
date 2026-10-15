Status: done
# 239: The vision-model fitting pass is retired - the matcher is the only automatic fitter
Depends on: 238, 212, 302f, 302g
Touches: fit/batch_us.py, fit/batch_eu.py, tools/site_done.py, fit/cover.py, tests/test_batch_us.py, tests/test_batch_eu.py, tests/test_site_done.py, tests/test_matchfit_station.py, tests/test_cover.py, tests/fixtures/matchfit_station/, tests/test_fit_provenance.py, tests/test_fit_queue.py, tests/test_owner_check.py (added it.221: the retirement deletes the line's first stdout line and changes the recorded why of new candidates; all three pin that - their owners are done, except 242 owns test_owner_check.py's capture region, my edit stays on check 7's runlog expectation), server/serve.py (it.221: its _fit_line docstring's "no model answer" wording only), docs/site_flow.md

## Goal
GOAL point 2 (2026-10-13): "The local Qwen models never place a drawing and never write point
pairs or coordinates ... `fit/batch_us.py` / `fit/batch_eu.py`'s model fitting pass is retired."
The pass is still live: the line's second pass (`tools/site_done._fit`) runs
`batch_us.run_sites` with a model (`--working` / `--model-json`) — fitkit sheet -> vision model
-> pairs -> gate — exactly the pass that fabricated ~100 fits on 2026-10-11 (301; 306a-f found
nearly all of them wrong; 212b deleted them). This task retires the fitting and keeps the
queue: uncovered candidates still get review-item entries, and the recorded reason is what the
matcher learned about the picture (238's per-candidate result: the judge's "not sure" clause,
the gate's `why`, "no matcher on this machine"), never a model's coordinates. The Qwen models
keep their non-placement jobs — GOAL and the lead note on 212 name them: find, classify and
tie pictures, write code (212a's cover search and the Clef-flash classification stay as they
are).

## Acceptance criteria
- [x] `fit/batch_us.py`: `run_sites` no longer accepts or calls a model. The fitting machinery
      (`_sheet`, `_model_prompt`, `_parse_answer`, `llm_model`, `recorded_model` and the sheet
      drawing helpers) is deleted; an uncovered candidate yields a review-item entry whose
      "why" is the matcher's recorded reason for that picture (the per-candidate result 238
      exposes, passed through the line); a machine without a reachable matcher records "no
      matcher on this machine" (a recorded environment fact, the 302g pattern); a pictureless
      site still gets the batch's "no picture found" item. The gate adapter (`gate_placement`),
      the upsert (`write_item` / `_entry`) and the report (`write_report`, incl. the seeded
      sample machinery) stay, with the fitting out.
- [x] The line (`tools/site_done.py`): step 1 is reworded to match — matcher first (as it
      already is), the second pass only records reasons, no model; the `--working` /
      `--model-json` flags are gone from the CLI and usage. The line's own checks
      (provenance refusal, the fabrication/spread line check, sync, entry, scoped export) are
      unchanged. `fit/batch_eu.py` (the EU CLI over the same loop) loses its flags the same
      way. `fit/cover.py`'s loop phase stops forwarding `--model-json` to the line and its
      docstring's "no model answer" wording is updated; its search / classify phases and
      their model use are untouched.
- [x] No test calls the model server: `tests/test_batch_us.py`, `tests/test_batch_eu.py`,
      `tests/test_site_done.py`, 302f's `tests/test_matchfit_station.py` and 212's
      `tests/test_cover.py` are updated to the retired line (their `--working` /
      `--model-json` invocations and "no model answer" expectations become the matcher's
      recorded reasons) and all pass with no model endpoint configured and the matcher
      stubbed per 302f's fixture idiom.
- [x] `docs/site_flow.md`: step 1 of the one-site-line section reworded to the retired form
      (matcher first, the item records why each picture is not on the map, no model pass);
      the file stays append-only for the other tasks' sections, as 302g's note requires.
- [x] The 22 golden hand-fit documents and the 49 existing matcher documents are
      byte-unchanged; the suite has no new reds against the newest driver loop-start note.

## Notes
- Depends on 212, not because of code but because `fit/cover.py` is 212's file and 212 is in
  flight (its closing step waits on 235): by the time this task runs, `cover.py`'s loop phase
  is final and only the `--model-json` forwarding and its wording are touched here.
- `docs/batch_us.md` / `docs/batch_eu.md` stay as the historical 203a/203b reports (the
  2026-10-11 vision runs, deleted by 212b); the matcher run's report of record is
  `docs/batch.md` (212) and the lead's `docs/matchfit.md`.
- The batch's SEED (20261010) and sample machinery in `write_report` stay: `docs/batch.md`'s
  seeded 20-sample is drawn from the automatically accepted fits union, which from now on is
  the matcher's documents (GOAL point 3's 18/20 check).


## Hand-over

(2026-10-15, iteration 228, agent a - **DONE and closed.** (h) full-suite verify + close
executed; all 5 acceptance boxes ticked; `Status: done`.)

**What (h) verified (all by running code, tree clean at start):** 242 open / 307d done,
so the owner_check reds were the expected 307d mid-transition family. Pre-checks:
zero `--working`/`--model-json` in fit/batch_us.py, fit/batch_eu.py, tools/site_done.py
(cover.py keeps only its 212-designed CLI refusal: L15/L52/L518/L825/L832); zero
"no model answer" in fit/tools/tests/docs; `sha256sum -c tests/golden/hand_fit_docs.sha256`
all OK (the 22 hand docs); tree clean before the suite. Full suite
`.venv/bin/python -m pytest tests/ -p no:cacheprovider`: **2 failed, 182 passed, 1
skipped, 554.24 s**. The 2 fails = the two test_owner_check tests (A bar-scale probe
"toolbar scale and turn change the drawing on screen" = the deterministic 1.0610 >
1.05+/-0.01 family it.226 A/B-proved on HEAD bytes, 242's; B is its dependent cascade -
needs A's itemBytes). The 1 skip = test_union_full_coverage_live's known skip-gate
(docs/batch_eu.md "Sites run: 294" vs live EU 418, until the next EU batch). **New vs the
2026-10-13 driver note: test_fit_queue::test_placement_gestures_and_save_in_the_browser is
now GREEN** (it was that note's only red) - the red set is strictly inside the bar. After
the suite the only dirty files were docs/site_flow/307d_B_4-saved.png + 307d_B_5-reload.png
(the owner run's re-render of 242's files) - restored with `git checkout -- docs/site_flow/`;
data/db/platefits + data/review byte-clean; golden hand docs re-verified after the run.

**If the driver holds the done claim** (230/0d21b0d precedent: held on the owner_check
family until the 307d stability fix merges): the two reds are 242's - 239's own A/B
(it.226) plus this run are the on-record evidence. When 242 merges and the task is
reopened, re-run just `tests/test_owner_check.py` (restore `docs/site_flow/` PNGs after:
`git checkout -- docs/site_flow/`); if green, re-assert done without re-running the full
suite (nothing else in this task can move: code, tests, fixtures, docs, goldens are all
committed - commits `8adf7b9` (d), `05ac246` (e)1, `8d14844` (e)2, `b5f7b0d` (f)+(g)).

**Hygiene (for anyone re-entering this task):** .venv works (Python 3.12.3). Never
`git add -A` - explicit paths (the 307d PNGs re-render on ANY owner_check run - restore
with `git checkout -- docs/site_flow/`). Tests: no fixed ports, no writes outside
project/tmp. A/B in-checkout only, never a bare worktree (PITFALLS 306d). ELoFTR
(127.0.0.1:8091, zju-community/matchanything_eloftr) is only needed again if the matchfit
fixtures drift (the test's _drift check would say so); it is not needed for the re-verify.
