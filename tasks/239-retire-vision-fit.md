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

(2026-10-14, iteration 226, agent a - (a)-(e) are all DONE and committed. NEXT SESSION:
(f) the fixture re-record (ELoFTR was UP at it.226 end - re-curl first), then (g) and (h).)

**State:** branch `agent/a`, tree clean. Commits: (a)-(d) in the log (`8adf7b9` is (d); the
it.220/221 work is in `9ff955b`); (e) part 1 (the two batch test rewrites) in the driver's
`05ac246`; (e) part 2 (the five targeted patches: test_site_done, test_fit_provenance,
test_fit_queue, test_owner_check, test_matchfit_station) in `8d14844` (test-files only;
the owner run's re-rendered 307d_B_4/B_5 PNGs were restored to committed bytes first - they
are 242's files). test_cover.py stays byte-unchanged through the whole task.

**Verified this session:** fast four (batch_us, batch_eu, site_done, fit_provenance) =
18 passed / 1 skipped (the skip = test_union_full_coverage_live's expected skip-gate:
docs/batch_eu.md "Sites run: 294" != live EU 418). test_fit_queue::
test_save_runs_the_one_site_line green (18.6 s). test_matchfit_station 2/2 red EXACTLY at
the stale fixtures' expected_stdout (red by construction until (f); no drift check fired).
owner_check 2/2 red - NOT 239's: see DECISIONS it.226.

**Red inventory for the (h) done claim (no NEW reds = exactly these three families):**
1. test_fit_queue::test_placement_gestures_and_save_in_the_browser - pre-existing red since
   the 2026-10-13 driver note (before any 239 code landed); the suite's only red at that
   loop start. Do not touch.
2. test_matchfit_station (2) - red by construction until (f) re-records the fixtures
   against the retired line. (f) fixes both.
3. test_owner_check (2) - the 307d mid-transition flake family, proven not 239's by A/B
   (it.226: probe fails at owner_probe.mjs:333 with 87.00574693662483/82 = 1.06105 vs
   1.05+/-0.01, deterministic, identical with my file at HEAD bytes). Remedy queued as
   242 (Depends on: 307d; Touches test_owner_check.py + docs/site_flow/); 230's done claim
   is held by the driver on exactly this family (0d21b0d: "the driver holds the done claim
   until the 307d stability fix merges"). If 242/307d have not merged by my done claim,
   document it that way (the 230 precedent) - do not fix 242's files.

**(f) fixture re-record (the one remaining code step):** ELoFTR was UP at it.226 end
(`curl -s -m 5 http://127.0.0.1:8091/health` -> zju-community/matchanything_eloftr, RTX
5060 Ti) - RE-CURL FIRST; if down, log a DECISIONS entry and come back next session.
Then: (1) in tests/fixtures/matchfit_station/record.py (the ONLY writer - never
hand-edit the fixtures): L360 `"task": "302f"` -> `"239"`, L408 `len(c_out) != 11` (+ its
SystemExit text "expected 11") -> 10, L493 `len(u_out) != 8` (+ "expected 8") -> 7. (2)
Run `.venv/bin/python tests/fixtures/matchfit_station/record.py` (live ELoFTR; it
re-records both fixtures, re-stamps the 9 input hashes, validates the replay against the
frozen held-out data/matchfit/heldout/results.json). (3) Expected refreshed content: both
expected_stdout lose line 0 (11->10, 8->7); the unsure item's candidate why and the
unsure stdout's per-picture lines become "not sure: 8 consistent points (need 10)"
(the RoMa port is dead -> no "; RoMa ..." suffix); recorded_at moves; the 15 request-body
sha256 keys per fixture should be unchanged (same crops/grounds/windows - the only drift
since the 302f/238 record was 230's index evidence re-stamp, which 0d21b0d already
re-recorded). (4) Run `pytest tests/test_matchfit_station.py` -> 2/2 green. (5) Commit
record.py + both fixtures.

**(g) docs/site_flow.md - ONLY the 300 section** (append-only for every other section,
302g's rule): the usage block drops `[--working | --model-json FILE]` and step 1's
wording mirrors tools/site_done.py's current module docstring (matcher first; the second
pass only records the matcher's reasons, never model coordinates; "no matcher on this
machine" when unreachable).

**(h) verify + close:** full suite (`.venv/bin/python -m pytest tests/ -p
no:cacheprovider`, --ignore=tests/test_gate.py if you hit its 424 s - the 2026-10-13
driver note ran it in 7 min; the owner_check 2 + placement_gestures 1 are the accepted
reds per the inventory above) must show NO red outside those three families; golden
byte-identity (`sha256sum -c tests/golden/hand_fit_docs.sha256` and the
tests/golden/src_... sample checks) and `git status` clean on data/db/platefits +
data/review; tick the 5 acceptance boxes, set Status: done, commit. If the driver rejects
the claim, its reasons land in DECISIONS.md - the 230/0d21b0d A/B accounting is the
precedent for the owner_check family.

**Hygiene:** .venv works. Never `git add -A` (explicit paths; the 307d PNGs re-render on
any owner_check run - restore with `git checkout -- docs/site_flow/`). Tests: no fixed
ports, no writes outside project/tmp. A/B in-checkout only, never a bare worktree
(PITFALLS 306d: locally-built site data is not in git).

**Re-read before (f):** record.py's run flow (it serves the line's subprocess over a
private tree, so read what it asserts beyond the line counts - the replay/heldout
validation is the real gate) and tests/test_matchfit_station.py's _drift (it recomputes
the 9 input hashes - if (f)'s re-record lands while agent c's 207a/241 work re-stamps
index/catalog rows on main, the next merge could re-fire the drift check; that is (f)'s
known exposure, the remedy is re-running record.py, which needs the live matcher).
