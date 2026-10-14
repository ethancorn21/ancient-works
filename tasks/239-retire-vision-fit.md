Status: in-progress
# 239: The vision-model fitting pass is retired - the matcher is the only automatic fitter
Depends on: 238, 212, 302f, 302g
Touches: fit/batch_us.py, fit/batch_eu.py, tools/site_done.py, fit/cover.py, tests/test_batch_us.py, tests/test_batch_eu.py, tests/test_site_done.py, tests/test_matchfit_station.py, tests/test_cover.py, tests/fixtures/matchfit_station/, docs/site_flow.md

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

(2026-10-14, iteration 218, agent a - session 2: reading COMPLETE (incl. test_cover.py, the last
unread file), cover-flag question RESOLVED, Touches updated (fixtures dir added), 5-file baseline
GREEN and recorded in DECISIONS; zero code changes yet. Next session: implement commit (a) batch_us.)

**State:** branch `agent/a` at f99c04e (driver PROGRESS overview before it.218). Working tree
CLEAN - the driver committed the once-dirty `docs/site_flow/307d_{B_1-card,B_4-saved,B_5-reload}.png`
in 6c830e6, so they now match HEAD bytes. The hygiene rule still stands: after any run that
regenerates 307d PNGs (only `test_fit_queue` / `test_owner_check` do), restore them with
`git show HEAD:docs/site_flow/<name>.png > <name>` before committing, and **never `git add -A`**
(commit explicit paths only). The 5-file baseline below does not touch them (verified clean
afterwards). `.venv` exists and works (driver-built from requirements.txt).

**Baseline (this branch, before any edit):** `.venv/bin/python -m pytest tests/test_batch_us.py
tests/test_batch_eu.py tests/test_site_done.py tests/test_matchfit_station.py tests/test_cover.py
-p no:cacheprovider` -> **21 passed, 1 skipped, 154.54s**. The skip is
`test_batch_eu.py::test_union_full_coverage_live` (skip-gated: `docs/batch_eu.md` says
"Sites run: 294" vs the live EU list; pre-existing, unrelated to 239 - the report machinery
stays). Zero failures = the "no new reds" baseline.

**Cover flag question - RESOLVED (session 2):** NO test pins cover's CLI. `tests/test_cover.py`
(892 ln, read in full) drives the phases in-process only (`cover.fetch/search/stage/nopicture/
report` against a hard-linked throwaway tree; `stage` called with `live=False`); no test anywhere
in tests/ references `fit/cover.py`'s `main()` or its flags. **Decision: drop `--model-json` from
cover's CLI and `loop()`** (it fed only the loop; keeping it would be a dead lie); **keep
`--working` refused** (lead ef84a05's placement ban, independent of this retirement). Cover
edits: usage line 15, flag help lines 50-53, `loop(root, model_json=None)` -> `loop(root)` (drop
the `args += ["--model-json", str(model_json)]` forwarding, lines 528-529; reword docstring
519-523 "no model answer" -> the matcher's recorded reason), main 821-858 (the mutually-exclusive
group 828-832 becomes just the `--working` flag; delete the `a.model_json` checks 841-845;
dispatch line 858 loses the arg).

**Implementation (one commit each, in this order):**
(a) `fit/batch_us.py`: `run_sites(root, site_ids, reasons=None)` - `reasons` = {plan: str} (the
   matcher's recorded per-candidate verdicts). Per site: covered candidates SKIP (unchanged - the
   skip guard is the only thing protecting audit notes); every uncovered candidate -> `_entry`
   with `why = reasons.get(plan, "no matcher on this machine")`, pairs `[]`, 202's proposal fields
   STAY on the entry (they are not model output); NO gate call, NO `write_doc`; no-picture site
   unchanged (the batch's "no picture found" item); detail outcomes: keep "skip", rename
   "reject"/"could-not-fit" -> "item" (tests are the only consumer). DELETE: `_sheet`,
   `_model_prompt`, `_parse_answer`, `_feature_present`, `_ground_lonlat`, `_font`, `_step`,
   `_grid`, `llm_model`, `recorded_model`, the model+gate step in `run_sites`,
   `--working`/`--model-json` in `main`, and the model paragraphs of the module docstring
   (reword to the retired form). KEEP: `gate_placement` (matchfit._settle calls it), `_rho2`,
   `write_doc` (matchfit calls it), `write_item`, `_entry`, `write_report`+`classify`+`_sample`
   +SEED, `write_golden`, `_save_json`, `_sites`, `_plans_rows`, `us_sites`, `candidates`,
   `pre_docs`, `is_pre_fit`, `_doc_path`, `_norm_pairs`, `_crop_px`, `_page_url`.
(b) `fit/batch_eu.py`: `run_eu(root, reasons=None)` mirrors (a); CLI keeps --root/--sites/--report
   only; `union_check`/`union_section`/`write_report` stay; docstring reworded.
(c) `tools/site_done.py`: `_fit(root, sid)` (model param GONE): the matcher block becomes
   `results = []`; when any row lacks a doc and `matchfit.reachable()`: `matchfit.run(str(root),
   [sid], results=results)` (print per written path as now); then re-read docs/uncovered as now.
   reasons: if the matcher RAN: `{e["plan"]: e["why"] for e in results if e["outcome"] ==
   "refused"}` (written ones have docs now, so they are not uncovered; _settle settles every
   doc-less candidate, so refused covers all of them - re-read docs BEFORE computing uncovered,
   as the code already does); if the matcher DID NOT run (unreachable): `{r["id"]: "no matcher on
   this machine" for r in uncovered}` (the 302g recorded-environment-fact pattern). Then
   `rec = batch_us.run_sites(str(root), [sid], reasons=reasons)[sid]` (the need_fit logic and the
   `keep` re-merge of already-covered entries stay as-is: `keep = [c for p, c in item_cands.items()
   if p not in new_ids]` then `review.upsert_item`; the detail-print branches follow (a)'s outcome
   names). DELETE: the first-stdout-line `fit  no model given: ...` print and the
   mutually-exclusive `--working`/`--model-json` parser group in `main`; reword the docstring
   usage line (3) + step 1 (lines 9-13) to the retired form (matcher first; the second pass only
   records reasons into the review item - the matcher's recorded why, or "no matcher on this
   machine" - no model). NOTE: that print is line 0 of EVERY run, so every run's stdout shrinks
   by exactly one line (tests count lines).
(d) `fit/cover.py`: per the RESOLVED decision above (no --model-json, keep --working refusal,
   `loop(root)` no forwarding, docstrings reworded).
(e) Tests:
   - `tests/test_site_done.py`: drop the line-0 "no model given" assertion -> runs shrink
     11->10 lines (recount EVERY `lines[N]` index in the Stonehenge two-run test); live-item-entry
     expectations (301-era "no model answer" whys) are DATA and stay; `_summary`'s
     `cand.get('why') or 'no model answer'` stays as display fallback only. A test asserting a NEW
     uncovered candidate's item why == "no model answer" now expects the matcher's recorded reason
     (or "no matcher on this machine" if its tree makes matchfit unreachable - check what each
     test's stub does to the /health probe).
   - `tests/test_batch_us.py` / `tests/test_batch_eu.py`: rewrite recorded-ANSWERS tests into
     recorded-REASONS tests (pass per-candidate reason strings as fixed inputs - the 302f fixture
     idiom: no model server; the socket-blocking fixture stays); stub-GATE tests die (the batch no
     longer calls the gate); "adds files, rewrites none" tests stay (weaker: only item entries, no
     auto docs); report/sample tests stay (the 22-doc synthetic record pins the sample machinery).
   - `tests/test_matchfit_station.py` (302f): confident fixture 11->10 stdout lines; unsure
     fixture 8->7 lines AND its new item entry's `why` becomes the matcher's "not sure: 8
     consistent points (need 10)" (was "no model answer").
(f) `tests/fixtures/matchfit_station/` RE-RECORD (in Touches): update `record.py` FIRST - its two
   hardcoded stdout line-count assertions (11 -> 10 confident, 8 -> 7 unsure) and its
   `header.task` ('302f' -> '239') - then run it (working phase, live ELoFTR required: check
   `curl http://127.0.0.1:8091/health` first; 230's it.216 ran it successfully, so the matcher is
   up on this machine). Per 302f's PITFALLS the re-record is the causing task's own cleanup.
(g) `docs/site_flow.md`: reword ONLY (1) the usage block (lines 5-7: drop `[--working |
   --model-json FILE]` - cover's usage line 15 gets the same treatment in (d)) and (2) step 1 of
   the one-site-line section (lines ~19-27): matcher first; the second pass records reasons only
   (the matcher's recorded why, or "no matcher on this machine" when unreachable); no model pass;
   no "no model answer". The file is 1730 lines, append-only for other tasks' sections (302g's
   starts ~1722); mine is the original 300 section at the top, so in-place reword is fine.
(h) Verify + close: re-run the 5 files (expect green, the same 1 skip); full suite
   `.venv/bin/python -m pytest tests/ -p no:cacheprovider` for NEW reds vs the driver's 2026-10-13
   loop-start note (only `test_fit_queue::test_placement_gestures_and_save_in_the_browser` red
   then - if still red: pre-existing, document it, do NOT fix it in 239); byte-unchanged proof:
   the golden `tests/golden/hand_fit_docs.sha256` checks inside test_batch_us/test_batch_eu/
   test_fit_provenance (41 docs listed) + `git status` clean on `data/db/platefits` and
   `data/review` after the runs; restore any regenerated 307d PNGs to HEAD bytes; tick each
   acceptance box ONLY after its check passes; set `Status: done` when all five are ticked.

**Pitfalls relevant (read the full entries before coding):** PITFALLS fit/ -> "batch_us.pre_docs
matches any existing <site>.*.json" (snapshot pre-run state before run_sites in tests),
"Recorded-answer batch tests must be state-aware" (same for recorded-reasons: compute
expectations from the live tree state), "write_report(path=None) silently falls back to
docs/batch_us.md"; tests/test_matchfit_station.py -> fixture input_hashes cover the WHOLE index
row (any evidence re-stamp since it.216 = rerun record.py - the re-record in (f) refreshes them);
tools/site_done.py, fit/review.py -> "A batch re-run of a review-item row replaces that
candidate's entry whole - site_done's skip guard is the only thing protecting audit notes" (the
retired run_sites MUST keep skipping covered candidates AND _fit's `keep` re-merge must survive);
Model servers -> 8081/8080 LLMs banned for fit PLACEMENT (ef84a05); A/B in-checkout, never a bare
worktree (web/data/sites partly local).

**Not done yet:** zero code edits. Session 3 starts at commit (a) batch_us.
