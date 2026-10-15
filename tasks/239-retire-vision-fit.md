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

(2026-10-14, iteration 222, agent a - step (d) fit/cover.py DONE (commit 8adf7b9). NEXT SESSION:
step (e) the eight test files, one commit.)

**State:** branch `agent/a`, tree clean after the (d) commit. The whole (a)-(d) chain is in:
- (a) `fit/batch_us.py` (b1940ff): `run_sites(root, site_ids, reasons=None)` - the fitting
  machinery is deleted; uncovered candidate -> review item, `why` = `reasons.get(plan)` or
  "no matcher on this machine"; pictureless site -> the batch's no-picture item;
  `gate_placement`/`write_item`/`_entry`/`write_report`(+`_sample`, SEED 20261010) stay.
- (b) `fit/batch_eu.py` (a13e2ed): `run_eu(root, reasons=None)` -> `batch_us.run_sites` over
  `eu_sites(root)`; the two model flags gone; `union_check`/`union_section`/`write_report`
  byte-unchanged.
- (c) `tools/site_done.py` (driver commit 9ff955b) + `server/serve.py` docstring:
  `_fit(root, sid)` matcher-first (`matchfit.run(str(root), [sid], results=results)`),
  `reasons` = the refused results' `why` when the matcher ran else "no matcher on this
  machine" per uncovered row; `run_sites(str(root), [sid], reasons=reasons)`; the keep
  re-merge of already-covered entries byte-identical; `--working`/`--model-json` and the
  first `fit  no model given` stdout line deleted (every run's stdout -1 line); `_summary`
  still shows `cand.get("why") or "no model answer"` as a DISPLAY fallback (data entries may
  lack why) - that string legitimately stays in site_done.py.
- (d) `fit/cover.py` (8adf7b9): `loop(root)` no longer forwards `--model-json`; the flag is
  gone from the CLI and `main()` (its two checks deleted); the mutually-exclusive group is a
  plain `--working` (still REFUSED, exit 2 - the lead ef84a05 ban is independent of this
  retirement); usage line 15, loop-phase doc block, loop docstring reworded to the matcher's
  recorded reasons. Search/stage/classify phases and Clef-flash model use byte-unchanged.

**Remaining steps (one commit each):**

(e) The eight test files, one commit; no model endpoint configured anywhere; offline replays
    patch `matchfit.reachable = lambda url=None: False` (NEVER a bare False - it crashes the
    run, PITFALLS). Files and what changes:
    - `tests/test_batch_us.py` / `tests/test_batch_eu.py`: recorded-ANSWER tests ->
      recorded-REASON tests (a fixed `{plan: why}` dict into `run_sites`/`run_eu`; line 335
      / 428 `entry["why"] == ((answer or {}).get("note") or "no model answer")` becomes the
      passed reason, with "no matcher on this machine" when reasons=None); keep the
      socket-blocking fixtures; tests that stub the GATE inside run_sites die (the batch no
      longer calls the gate - the gate stays covered by 238's test_matchfit_gate via
      _settle); "adds files, rewrites none" -> "adds an item entry, rewrites none" (no auto
      docs any more); report/sample tests stay - a synthetic record with non-empty "auto"
      passed directly to write_report/_sample pins the seeded machinery; golden byte-
      identity checks (tests/golden/hand_fit_docs.sha256) stay. STATE-AWARE: compute
      expectations from the live tree state, never constants (PITFALLS "Recorded-answer
      batch tests must be state-aware" - same for recorded-reasons).
    - `tests/test_site_done.py`: recount EVERY lines[N] index - the "fit  no model given"
      line is gone (line 0 is now the site header; the Stonehenge two-run test 11 -> 10
      lines per run; the line-306/353 `why` mirrors are DISPLAY fallbacks in _summary and
      stay as-is since data entries may lack why). LIVE item entries whose recorded why is
      "no model answer" (301-era data) STAY - they are stored facts, not a template. Only
      assertions that a NEWLY-created uncovered candidate's why == "no model answer" must
      change - to the matcher's recorded reason, or "no matcher on this machine" if that
      test's stub makes matchfit.reachable() false.
    - `tests/test_fit_provenance.py`: line 323
      `assert lines[0] == 'fit  no model given: ...'` deleted and EVERY subsequent index
      shifts by -1 (line 0 becomes the site header); line 342's `_summary` mirror stays
      (the fallback is still in _summary); reword the "no model" docstring phrasings
      (21, 173, 423).
    - `tests/test_fit_queue.py`: `test_save_runs_the_one_site_line` line 1012 assert
      `why == "no model answer"` -> `why == "no matcher on this machine"` (the test's
      server process has every socket dead, so the matcher is unreachable); reword
      docstrings 800/903/1002 ("the line has no model" -> the matcher was not reachable,
      recorded as such). `test_placement_gestures_and_save_in_the_browser` has been red
      since the 2026-10-13 loop start (307d/242 family) - do NOT fix it here.
    - `tests/test_owner_check.py` (242 owns the file - keep the edit ISOLATED to check 7):
      `want_fit` (line 659) drops its first element (the deleted line) and the comment
      block (646-652) is reworded; the `assert not any("matcher" in ln ...)` stays green
      (the batch never runs there, so no matcher line either). Do NOT touch _run_one /
      the capture / screenshot-copy region (242's).
    - `tests/test_cover.py`: no CLI is pinned (session 2) - check only for in-process
      loop-phase expectations mentioning "no model answer"; if none, this file is
      byte-unchanged in (e) (still named in the acceptance box as the file 212's loop
      drives - it passes as-is against the new loop()).
    - `tests/test_matchfit_station.py` (302f): its assertions READ the fixtures, so after
      (f)'s re-record the file itself needs no change; the stdout line-count expectations
      (11/8) live in `tests/fixtures/matchfit_station/record.py`.
(f) Fixture re-record - LIVE ELoFTR required: FIRST check `curl -s
    http://127.0.0.1:8091/health` (up when 230 ran it.216). If up: update
    tests/fixtures/matchfit_station/record.py first - the two hardcoded stdout line-count
    asserts (11 -> 10, 8 -> 7) and header.task ('302f' -> '239') - then run
    `.venv/bin/python tests/fixtures/matchfit_station/record.py` and commit the two
    refreshed fixtures (records.json: stdout shrinks; records_unsure.json: stdout shrinks
    AND the new item's cand["why"] becomes "not sure: 8 consistent points (need 10)"
    instead of "no model answer"). The fixture input_hashes cover the WHOLE index row -
    any evidence re-stamp since it.216 = record.py rerun; (f) refreshes them. Per 302f's
    PITFALLS this re-record is the causing task's own cleanup (239). If ELoFTR is DOWN:
    log a DECISIONS entry, do not fake it, and come back (the fixture refresh is a 239
    acceptance dependency - box 5's suite-green needs it).
(g) docs/site_flow.md - reword ONLY the 300 section at the top: the usage block (lines
    5-7: drop `[--working | --model-json FILE]`; cover's usage line gets its rewording
    already in (d)) and step 1 of the one-site-line section (~lines 19-27: lines 21 and 25
    say "no model answer"; mirror the new site_done docstring step 1 - matcher first; the
    item records the matcher's recorded reason per picture; "no matcher on this machine"
    when unreachable; no model pass). The file is APPEND-ONLY for other tasks' sections
    (302g's starts ~1722; the 206/301-era "no model answer" mentions at 263 and the 302g
    run note at 1726 are historical records - untouched).
(h) Verify + close: re-run the 8 files (expect green; the same 1 pre-existing skip:
    test_batch_eu.py::test_union_full_coverage_live, skip-gated on docs/batch_eu.md's
    "Sites run: 294"); then the full suite `.venv/bin/python -m pytest tests/
    -p no:cacheprovider` - no NEW reds vs the 2026-10-13 driver loop-start note (only
    test_fit_queue::test_placement_gestures_and_save_in_the_browser red then; if still
    red: pre-existing, document it, do NOT fix it in 239). Byte-unchanged proof: the
    golden hand_fit_docs.sha256 checks inside test_batch_us/test_batch_eu/
    test_fit_provenance + `git status` clean on data/db/platefits and data/review after
    all runs. Tick each acceptance box ONLY after its own check passes; set Status: done
    when all five are ticked.

**Hygiene:** .venv works. Never `git add -A` (explicit paths). After any run of
test_fit_queue / test_owner_check (they regenerate docs/site_flow/307d_*.png), restore
`git show HEAD:docs/site_flow/<name>.png > <name>` before committing. A/B in-checkout only,
never a bare worktree (locally-built site data is gitignored).

**Pitfalls to re-read before (e):** PITFALLS fit/ - "batch_us. pre_docs matches any existing
<site>.*.json" (snapshot pre-run state before run_sites in tests), "Recorded-answer batch
tests must be state-aware", "write_report (path=None) silently falls back to
docs/batch_us.md"; tests/test_matchfit_station.py - fixture input_hashes cover the whole
index row; tools/site_done.py, fit/review.py - "A batch re-run of a review-item row
replaces that candidate's entry whole - site_done's skip guard is the only thing
protecting audit notes" (the keep re-merge must keep surviving in the tests' expectations
where relevant); Model servers - 8081/8080 LLMs banned for fit PLACEMENT (ef84a05);
"Patching matchfit.reachable for an offline replay needs a lambda returning False - a bare
False crashes the run".
