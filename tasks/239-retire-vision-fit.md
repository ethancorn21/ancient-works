Status: open
# 239: The vision-model fitting pass is retired - the matcher is the only automatic fitter
Depends on: 238, 212, 302f, 302g
Touches: fit/batch_us.py, fit/batch_eu.py, tools/site_done.py, fit/cover.py, tests/test_batch_us.py, tests/test_batch_eu.py, tests/test_site_done.py, tests/test_matchfit_station.py, tests/test_cover.py, docs/site_flow.md

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

(2026-10-14, iteration 217, agent a - session 1: READING ONLY, no code changed yet, no tests
run yet; all dependencies verified done: 238, 212, 302f, 302g all `Status: done`.)

**State:** branch `agent/a` at dfd1ef5 (driver PROGRESS overview before it.217). Working tree
carries 3 dirty `docs/site_flow/307d_{B_1-card,B_4-saved,B_5-reload}.png` (mine from the 307d
owner-check work in 230's sessions; they drift on every full-suite run) - **NEVER `git add
-A`** on this branch (230's it.216 lesson; 230's hand-over says restore them with
`git show HEAD:docs/site_flow/<name>.png > <name>` after any owner_check run and commit only
explicit paths).

**What I read (full files, all on this branch):**
- `fit/batch_us.py` (entire). To DELETE: `_sheet`, `_model_prompt`, `_parse_answer`,
  `_feature_present`, `_ground_lonlat`, `_font`, `_step`, `_grid`, `llm_model`,
  `recorded_model`, the model step + gate/doc-writing in `run_sites`, `--working`/`--model-json`
  in `main`, and the model paragraphs of the module docstring. To KEEP: `gate_placement`
  (the 001 adapter - matchfit._settle calls it), `_rho2`, `write_doc` (matchfit calls it),
  `write_item`, `_entry` (change: its `pairs`/proposal/why fields, see design), `write_report`
  + `classify` + `_sample` + SEED, `write_golden`, `_save_json`, `_sites`, `_plans_rows`,
  `us_sites`, `candidates`, `pre_docs`, `is_pre_fit`, `_doc_path`, `_norm_pairs`, `_crop_px`,
  `_page_url`.
- `fit/matchfit.py` (entire): 238 already added what I need - `run(root, site_ids, dry,
  url, roma_url, results=None)` / `_settle(..., results=None)` append one entry per settled
  candidate: `{'site','plan','outcome':'written'|'refused'|'dry','path','why','kind'}`; its
  docstring says "the caller (239) records refused candidates from it". `run` skips candidates
  with a doc or `dropped` in the item; every other candidate gets an entry (fit_row's `why`:
  "picture not on this machine", "the matcher found nothing consistent", the judge's
  "not sure: ..." clauses, or 238's gate clause). `reachable(url)` = /health probe.
- `tools/site_done.py` (entire): `_fit(root, sid, model)` - matcher block runs when any row
  lacks a doc and `matchfit.reachable()`; then `need_fit` triggers `batch_us.run_sites(...,
  model)`. `main` has a mutually-exclusive `--working`/`--model-json` group and prints
  `fit  no model given: unfitted pictures (if any) go to the review item as "no model
  answer"` as its FIRST stdout line when neither. Step 1 of the docstring + the usage block
  must be reworded (matcher first, second pass only records reasons, no model).
- `fit/batch_eu.py` (entire): `run_eu(root, model=None)` and `main`'s flags; `union_check`,
  `union_section`, `write_report` stay.
- `fit/cover.py` (entire): `loop(root, model_json=None)` forwards `--model-json` to
  site_done (lines: `if model_json: args += ["--model-json", str(model_json)]`); the CLI has
  `--working` (REFUSED, exit 2 - the lead ef84a05) and `--model-json` ("the loop phase's
  only"); docstring line ~"the rest to the review item as 'no model answer'". Design
  decision to CONFIRM next session: since --model-json fed ONLY the loop, I intend to drop
  the --model-json flag from cover's CLI too (a kept-but-dead flag would lie); --working stays
  (its refusal documents the lead's placement ban, independent of this task). Check
  test_cover.py's assertions before committing to that reading.
- ALL FIVE TEST FILES read except test_cover.py: `tests/test_batch_us.py` (677 ln, full),
  `tests/test_batch_eu.py` (841 ln, full), `tests/test_site_done.py` (363 ln, full),
  `tests/test_matchfit_station.py` (340 ln, full), plus the 302f recorder
  `tests/fixtures/matchfit_station/record.py` (full).
- `docs/site_flow.md`: the one-site-line section is lines 1-~90 (header + `## The line, step
  by step`); step 1's "A brand-new site needs a model here: --working ... or --model-json ...
  with neither, unfitted pictures land in the review item as 'no model answer'" is the text to
  reword. 302g's section is at 1722+ (append-only after it; I only touch step 1 + the usage
  block). The file is 1730 lines; other tasks' sections come after 302g's.

**Design (my working plan, not yet coded):**
1. `run_sites(root, site_ids, reasons=None)`: `reasons` = {plan_id: str} (what the matcher
   recorded for that picture). Per site: skip candidates with a doc; every uncovered
   candidate becomes a `_entry` with `why = reasons.get(plan) or <default>` (default when the
   caller passed nothing: needs a name - I propose "no matcher on this machine" for the
   unreachable case set by the caller, and something like "the matcher did not settle this
   picture" only if needed; decide from the line's two call shapes below); no gate call,
   no `write_doc`, pairs always `[]`, 202's proposal fields (coarse/ground/scale_m_px/...) on
   the entry STAY (they are 202's deterministic proposal, not model output - the unsure
   fixture's item already carries them). No-picture site: unchanged. Record detail outcome
   "item" (replacing "reject"/"could-not-fit") + "skip".
2. `site_done._fit(root, sid)` (model param gone): matcher block -> `results = []`; when a
   row lacks a doc and `matchfit.reachable()`: `matchfit.run(root, [sid], results=results)`;
   else (unreachable): reasons for ALL uncovered = "no matcher on this machine" (the 302g
   recorded-environment-fact pattern - 302g's hand-over: the 8080 model "not reachable from
   this VM, so uncovered candidates come back with ... a recorded environment fact, not a
   defect"). Build reasons from results: refused -> entry['why']; (written -> the candidate
   has a doc, re-read docs first, so it won't be uncovered). Pass reasons to run_sites.
   Delete the `no model given` print (line 0 of every run) and the --working/--model-json
   parser group; reword step 1 of the docstring + usage.
3. `batch_eu`: `run_eu(root, reasons=None)`; main loses both flags (CLI: --root/--sites/
   --report only); docstring reworded.
4. `cover.loop(root)` (model_json gone); CLI: drop --model-json (CONFIRM vs test_cover),
   keep --working refusal; docstring "no model answer" -> the matcher-reason wording.
5. Tests: test_site_done - drop the line-0 "no model given" assertion (11-line runs become
   10; the Stonehenge test's runs print 3+7+2+13+1 -> recount: the no-batch-run branch is
   unaffected except line 0 disappears; the second run's lines[2] stays); its
   _preconditions/_summary expectations read the LIVE item entries (some say "no model
   answer" from the 301 era) - those are DATA, unchanged, so _summary's `cand.get('why') or
   'no model answer'` fallback stays as a display fallback only. test_batch_us/test_batch_eu
   - rewrite the recorded-answers tests to recorded-REASONS tests (per-candidate reason
   strings as fixed inputs, the 302f fixture idiom: no model server, socket-blocking
   fixture stays); stub-gate tests die (no gate in the batch anymore) or become
   stub-reasons item-writer pins; the "adds files, rewrites none" tests stay (weaker now:
   no new auto docs, only item entries); report tests stay but auto lists are empty in real
   runs (syn-records 22-doc synthetic stays to pin the sample machinery). test_matchfit_
   station - confident: 11->10 stdout lines (line 0 gone); unsure: 8->7 lines AND the new
   item's cand['why'] becomes the MATCHER's "not sure: 8 consistent points (need 10)"
   (currently 'no model answer') -> **both fixtures must be RE-RECORDED with the live
   ELoFTR** (127.0.0.1:8091, per the 302f PITFALLS: re-recording is the causing task's own
   cleanup -> add `tests/fixtures/matchfit_station/` to my Touches line first; record.py
   itself needs its two hardcoded line-count assertions 11/8 updated to the new counts, and
   its `header.task` '302f' -> '239').
6. `docs/site_flow.md`: reword ONLY the usage block (line 5-7: drop `[--working | --model-json
   FILE]`) and step 1 (line ~19-27) to the retired form; nothing else in the file (append-only
   for the other tasks' sections; my section is the ORIGINAL 300 section at the TOP, so
   rewording it in place is fine - it is 300's/this project's own text, not another task's
   appended block).

**Exact next steps (fresh agent):**
1. Read `tests/test_cover.py` (892 ln) - I never reached it; it pins cover's CLI (the
   --working refusal, --model-json forwarding to the loop, the loop's stdout lines incl. any
   "no model answer" wording) - that decides step 4's flag question above.
2. Add to the task's Touches line: `tests/fixtures/matchfit_station/` (fixture re-record,
   230/243 precedent: the causing task absorbs its own re-record).
3. Baseline BEFORE any edit: run the 5 test files on this branch:
   `.venv/bin/python -m pytest tests/test_batch_us.py tests/test_batch_eu.py
   tests/test_site_done.py tests/test_matchfit_station.py tests/test_cover.py -p
   no:cacheprovider` (expect: green per 230's it.216 for the station pair; the batch/suite
   state otherwise per the 2026-10-13 loop-start note - only test_fit_queue was red then;
   re-verify .venv exists: driver builds it from requirements.txt). Record the result in
   DECISIONS as the 239 baseline.
4. Then implement in this order, one commit each: (a) batch_us retirement (run_sites
   reasons-based, deletions, docstring, CLI); (b) batch_eu; (c) site_done; (d) cover; (e) the
   test files; (f) re-record the 302f fixtures (live ELoFTR 127.0.0.1:8091 - check
   `/health` first: `curl http://127.0.0.1:8091/health`); (g) docs/site_flow.md reword; (h)
   full suite, verify the 22 golden hand-fit docs + 49 matcher docs byte-unchanged
   (tests/golden/hand_fit_docs.sha256 + `git status` on data/db/platefits) and no new reds
   vs the baseline; tick the boxes.
5. After ANY full-suite run on this branch: restore the 307d PNGs to HEAD bytes before
   committing (230's hand-over step 4) and commit with EXPLICIT paths only.

**Pitfalls already relevant (read the full entries before coding):** PITFALLS fit/ ->
"batch_us.pre_docs matches any existing <site>.*.json" (snapshot pre-run state before
run_sites in tests), "Recorded-answer batch tests must be state-aware" (same discipline for
recorded-reasons tests: compute expectations from live tree state), "write_report(path=None)
silently falls back to docs/batch_us.md"; tests/test_matchfit_station.py -> fixture
input_hashes cover the WHOLE index row (any evidence re-stamp since it.216 = rerun
record.py); tools/site_done.py,fit/review.py -> "A batch re-run of a review-item row replaces
that candidate's entry whole - site_done's skip guard is the only thing protecting audit
notes" (the retired run_sites MUST keep skipping covered candidates AND the line's `keep`
re-merge of already-covered entries must survive - see _fit's `keep = [c for p, c in
item_cands.items() if p not in new_ids]`); Model servers -> 8081/8080 LLMs banned for fit
PLACEMENT (ef84a05); A/B in-checkout not in a worktree (web/data/sites is partly local).

**Not done yet:** zero code edits, zero test runs. Nothing in DECISIONS.md for 239 yet
(first entry owed: baseline + the cover-flag decision).
