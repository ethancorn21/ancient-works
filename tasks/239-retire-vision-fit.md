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

(2026-10-14, iteration 219, agent a - session 3: commit (a) LANDED (fit/batch_us.py retired:
run_sites(reasons=...), ten model functions deleted, matcher-facing helpers kept; verified by
scratch-tree smoke test). Next session: (b) batch_eu, then (c) site_done, (d) cover, (e) the
five test files, (f) fixture re-record, (g) docs/site_flow.md, (h) verify + close. One commit
per step; never `git add -A` (commit explicit paths).)

**State:** branch `agent/a`. Working tree clean after this session's commit (only
fit/batch_us.py was changed: 65 insertions / 365 deletions). `.venv` works. Hygiene: after any
run that regenerates `docs/site_flow/307d_*.png` (only test_fit_queue / test_owner_check do),
restore `git show HEAD:docs/site_flow/<name>.png > <name>` before committing.

**(a) done - what batch_us.py is now:** `run_sites(root, site_ids, reasons=None)`; reasons =
{plan: matcher's recorded verdict} (238's results via the line); uncovered -> item entry
{plan, title, url, evidence?, pairs: [], 202's proposal fields or coarse:True, why};
why = reasons.get(plan) or "no matcher on this machine"; covered -> "skip" (guard KEPT);
no-picture unchanged; detail outcomes "skip"|"item"; record's "auto" key kept, always empty
(classify/_sample/write_report unchanged). Deleted: _sheet, _model_prompt, _parse_answer,
_feature_present, _ground_lonlat, _font, _step, _grid, llm_model, recorded_model; main has no
--working/--model-json. Kept for matchfit: gate_placement, write_doc, _norm_pairs, _save_json,
_crop_px, _plans_rows, pre_docs, candidates, _sites, _page_url, is_pre_fit, us_sites,
_doc_path, write_item, write_report, classify. Details + smoke-test results: session-3
DECISIONS entry.

**Expected fallout until (b)-(f) land (do not be surprised by reds in these files):**
fit/batch_eu.py main + tools/site_done.py main still call deleted batch_us.llm_model/
recorded_model; the five test files still use recorded answers / "no model answer". The 5-file
suite must be green at the done claim (step (h)), not before.

**Remaining steps (one commit each):**

(b) fit/batch_eu.py: `run_eu(root, reasons=None)` -> `batch_us.run_sites(root, eu_sites(root),
    reasons)`; main drops --working/--model-json (keeps --root/--sites/--report); docstring
    reworded to the retired form (the "loop imported from fit/batch_us.py" statement stays
    true); usage block loses the two flag lines. union_check/union_section/write_report stay
    byte-for-byte.

(c) tools/site_done.py: `_fit(root, sid)` (model param GONE): rows/docs/item_cands/uncovered
    as today; then:
      results = []
      if any(r["id"] not in docs for r in rows) and matchfit.reachable():
          for path in matchfit.run(str(root), [sid], results=results):
              print(f"fit  matcher: fit written ({Path(path).name})")
          docs = dict(batch_us.pre_docs(str(root), sid)); uncovered = recompute as today
      reasons = ({e["plan"]: e["why"] for e in results if e["outcome"] == "refused"}
                 if results else {r["id"]: "no matcher on this machine" for r in uncovered})
      need_fit as today -> `rec = batch_us.run_sites(str(root), [sid], reasons=reasons)[sid]`;
      the `keep` re-merge of already-covered entries stays EXACTLY as is (PITFALLS: the only
      thing protecting audit notes). Detail prints: "skip" -> "skipped: already fitted (doc
      sid.plan)"; "item" -> "sent to the review queue ({why})"; delete the "auto" branch;
      no-picture print unchanged. When the matcher RAN, refused covers every uncovered plan
      (matchfit.run settles every doc-less candidate, including "picture not on this
      machine"), so the .get() fallback only fires when the matcher did not run at all.
    main(): delete the mutually-exclusive --working/--model-json group AND the
    `fit  no model given: ...` print (it is line 0 of EVERY run: every run's stdout shrinks
    by exactly one line - tests count lines). Reword the docstring's usage line and step 1
    (matcher first; the second pass only records reasons - the matcher's recorded why, or
    "no matcher on this machine" - no model pass). The line's own checks (provenance
    refusal, fabrication/spread, sync, entry, scoped export) are unchanged. `_summary`'s
    `cand.get('why') or 'no model answer'` is a display fallback only - it stays (data
    entries may lack why).

(d) fit/cover.py: per the session-2 decision: DROP --model-json from the CLI and loop():
    `loop(root)` no longer forwards it (the old `args += ["--model-json", str(model_json)]`);
    main()'s mutually-exclusive group becomes a plain --working flag; delete the a.model_json
    phase checks; usage line 15, flag help lines 50-53 and the loop docstring (the "no model
    answer" wording) reworded. KEEP --working REFUSED (lead ef84a05's placement ban is
    independent of this retirement). Search/classify phases and their model use untouched.
    No test pins cover's CLI (verified session 2).

(e) Tests (one commit; no model endpoint configured anywhere; the matcher is stubbed per
    302f's fixture idiom):
    - test_batch_us.py / test_batch_eu.py: recorded-ANSWER tests -> recorded-REASON tests
      (pass a fixed {plan: why} dict into run_sites/run_eu; keep any socket-blocking
      fixture); tests that stub the GATE inside run_sites die (the batch no longer calls
      the gate - the gate stays covered by 238's test_matchfit_gate via _settle);
      "adds files, rewrites none" -> "adds an item entry, rewrites none" (no auto docs);
      report/sample tests stay (a synthetic record with a non-empty "auto" can still be
      passed directly to write_report/_sample to pin the seeded sample machinery); golden
      byte-identity checks (tests/golden/hand_fit_docs.sha256) stay. Remember the state-
      awareness PITFALLS: compute expectations from the live tree state, never constants.
    - test_site_done.py: recount EVERY lines[N] index (the Stonehenge two-run test: 11 -> 10
      lines per run: the "fit  no model given" line is gone); live item-entry expectations
      (301-era "no model answer" whys) are DATA and stay; a test asserting a NEW uncovered
      candidate's item why == "no model answer" now expects the matcher's recorded reason
      or "no matcher on this machine" - check what each test's stub does to the /health
      probe (offline replay needs `matchfit.reachable = lambda url=None: False`, NOT a bare
      False - PITFALLS).
    - test_cover.py: no CLI is pinned (session 2), so only in-process expectations that
      mentioned "no model answer" for the loop phase, if any.
    - test_matchfit_station.py (302f): after (f)'s re-record the test file itself may need
      no change (its assertions read the fixtures) - check the two stdout line-count
      expectations live in record.py, not the test.

(f) Fixture re-record (working phase; LIVE ELoFTR required - check
    `curl http://127.0.0.1:8091/health` first; it was up when 230 ran it.216): FIRST update
    tests/fixtures/matchfit_station/record.py - its two hardcoded stdout line-count
    assertions (11 confident -> 10, 8 unsure -> 7) and its header.task ('302f' -> '239') -
    then `.venv/bin/python tests/fixtures/matchfit_station/record.py` and commit the two
    refreshed fixtures (records.json: confident, stdout shrinks; records_unsure.json: stdout
    shrinks AND the new item's cand["why"] becomes the matcher's "not sure: 8 consistent
    points (need 10)" instead of "no model answer"). Per 302f's PITFALLS this re-record is
    the causing task's own cleanup.

(g) docs/site_flow.md: reword ONLY (1) the usage block (lines 5-7: drop `[--working |
    --model-json FILE]`; cover's usage line gets its rewording in (d)) and (2) step 1 of the
    one-site-line section (~lines 19-27): matcher first; the second pass records reasons
    only (the matcher's recorded why, or "no matcher on this machine" when unreachable); no
    model pass; no "no model answer". The file is append-only for OTHER tasks' sections
    (302g's starts ~1722); the 300 section at the top is this task's - in-place reword is
    fine.

(h) Verify + close: re-run the 5 files (expect green, the same 1 skip:
    test_batch_eu.py::test_union_full_coverage_live - skip-gated, pre-existing, report
    machinery stays); then the full suite `.venv/bin/python -m pytest tests/ -p
    no:cacheprovider` - no NEW reds vs the driver's 2026-10-13 loop-start note (only
    test_fit_queue::test_placement_gestures_and_save_in_the_browser red then - if still
    red: pre-existing, document it, do NOT fix it in 239). Byte-unchanged proof: the golden
    hand_fit_docs.sha256 checks (41 docs) inside test_batch_us/test_batch_eu/
    test_fit_provenance + `git status` clean on data/db/platefits and data/review after all
    runs; restore any regenerated 307d PNGs to HEAD bytes. Tick each acceptance box ONLY
    after its own check passes; set Status: done when all five are ticked.

**Pitfalls relevant (read the full entries before coding):** PITFALLS fit/ -> "batch_us.
pre_docs matches any existing <site>.*.json" (snapshot pre-run state before run_sites in
tests), "Recorded-answer batch tests must be state-aware" (same for recorded-reasons:
compute expectations from the live tree state), "write_report(path=None) silently falls back
to docs/batch_us.md"; tests/test_matchfit_station.py -> the fixture's input_hashes cover the
WHOLE index row (any evidence re-stamp since it.216 = rerun record.py - (f) refreshes them);
tools/site_done.py, fit/review.py -> "A batch re-run of a review-item row replaces that
candidate's entry whole - site_done's skip guard is the only thing protecting audit notes"
(run_sites keeps the covered-candidate skip; _fit's keep re-merge must survive); Model
servers -> 8081/8080 LLMs banned for fit PLACEMENT (ef84a05) - cover keeps --working REFUSED
and every other path has no model flag at all; A/B in-checkout, never a bare worktree.
