Status: in-progress
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
- [ ] `fit/batch_us.py`: `run_sites` no longer accepts or calls a model. The fitting machinery
      (`_sheet`, `_model_prompt`, `_parse_answer`, `llm_model`, `recorded_model` and the sheet
      drawing helpers) is deleted; an uncovered candidate yields a review-item entry whose
      "why" is the matcher's recorded reason for that picture (the per-candidate result 238
      exposes, passed through the line); a machine without a reachable matcher records "no
      matcher on this machine" (a recorded environment fact, the 302g pattern); a pictureless
      site still gets the batch's "no picture found" item. The gate adapter (`gate_placement`),
      the upsert (`write_item` / `_entry`) and the report (`write_report`, incl. the seeded
      sample machinery) stay, with the fitting out.
- [ ] The line (`tools/site_done.py`): step 1 is reworded to match — matcher first (as it
      already is), the second pass only records reasons, no model; the `--working` /
      `--model-json` flags are gone from the CLI and usage. The line's own checks
      (provenance refusal, the fabrication/spread line check, sync, entry, scoped export) are
      unchanged. `fit/batch_eu.py` (the EU CLI over the same loop) loses its flags the same
      way. `fit/cover.py`'s loop phase stops forwarding `--model-json` to the line and its
      docstring's "no model answer" wording is updated; its search / classify phases and
      their model use are untouched.
- [ ] No test calls the model server: `tests/test_batch_us.py`, `tests/test_batch_eu.py`,
      `tests/test_site_done.py`, 302f's `tests/test_matchfit_station.py` and 212's
      `tests/test_cover.py` are updated to the retired line (their `--working` /
      `--model-json` invocations and "no model answer" expectations become the matcher's
      recorded reasons) and all pass with no model endpoint configured and the matcher
      stubbed per 302f's fixture idiom.
- [ ] `docs/site_flow.md`: step 1 of the one-site-line section reworded to the retired form
      (matcher first, the item records why each picture is not on the map, no model pass);
      the file stays append-only for the other tasks' sections, as 302g's note requires.
- [ ] The 22 golden hand-fit documents and the 49 existing matcher documents are
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

(2026-10-15, iteration 227, agent a - (a)-(g) are all DONE and committed. NEXT SESSION:
(h) the full-suite verify + close - no live matcher needed, no fixture re-record needed.)

**State:** branch `agent/a`, tree clean. Commits: (a)-(d) in the log (`8adf7b9` is (d));
(e) part 1 in the driver's `05ac246`, (e) part 2 in `8d14844`; **(f)+(g) in `b5f7b0d`**
(record.py 302f->239 + 11->10/8->7 asserts, both fixtures re-recorded live, site_flow 300
section reworded). test_cover.py stays byte-unchanged through the whole task.

**Verified this session (all by running code):** ELoFTR re-curl UP (zju-community/
matchanything_eloftr, RTX 5060 Ti) -> re-record ran live and landed EXACTLY as the it.226
hand-over predicted: 15/15 keys distinct, **0 live-vs-frozen held-out discrepancies**,
replay identical, confident 10 lines (guard 0.228346/195.702), unsure seed 7 -> 8 inliers,
why "not sure: 8 consistent points (need 10)", 7 lines, item 481->482 files / 457 published;
per fixture the 15 response keys and all 9 input_hashes are UNCHANGED (the 0d21b0d re-stamp
is still current; agent c's 207a/241 merges did not re-stamp the badbury-relevant rows).
`pytest tests/test_matchfit_station.py` **2/2 green** (was red by construction); 
`tests/test_matchfit_gate.py` 3/3 green (consumes the same fixture; its "302f" mention is a
name only). The only reds left in the suite are the known three families minus matchfit:
placement_gestures (pre-existing since the 2026-10-13 loop start - do not touch) and
owner_check x2 (the 307d mid-transition family - 242's, proven not 239's by A/B in it.226;
230's done claim is held by the driver on exactly this family per 0d21b0d).

**(h) verify + close (no matcher, no code - one session):** 1. Full suite:
`.venv/bin/python -m pytest tests/ -p no:cacheprovider` (~7 min per the 2026-10-13 driver
note; if the run is threatened by the 424 s test_gate.py, `--ignore=tests/test_gate.py` -
its status is covered by the driver's loop-start note). Accept: **NO red outside**
{test_fit_queue::test_placement_gestures_and_save_in_the_browser, test_owner_check x2}.
If test_owner_check is GREEN by then, 242/307d have merged - even better, say so. If you
took the owner_check family down (ran it) restore `docs/site_flow/307d_*.png` with
`git checkout -- docs/site_flow/` before the claim. 2. Golden byte-identity:
`sha256sum -c tests/golden/hand_fit_docs.sha256` (the 22 hand docs) and the
`tests/golden/src_...` sample checks the suite already runs; `git status` clean on
data/db/platefits + data/review (the recorder runs are in-process on throwaway trees -
the checkout surface is hash-checked by record.py itself, so it must be). 3. Tick all 5
acceptance boxes (all now verifiably true: (a)-(d) code, (e) the eight test files, (f)
fixtures green, (g) doc reworded), set `Status: done`, commit. 4. If the driver rejects
the claim its reasons land in DECISIONS.md; the 230/0d21b0d A/B accounting is the
precedent for the owner_check family.

**Hygiene:** .venv works. Never `git add -A` (explicit paths; the 307d PNGs re-render on
any owner_check run - restore with `git checkout -- docs/site_flow/`). Tests: no fixed
ports, no writes outside project/tmp. A/B in-checkout only, never a bare worktree
(PITFALLS 306d). ELoFTR is only needed again if the matchfit fixtures drift (the test's
_drift check would say so).
