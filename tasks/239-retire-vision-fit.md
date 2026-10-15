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

(2026-10-14, iteration 221, agent a - session 5, CONTEXT LIMIT: step (c) is CODE-COMPLETE and
smoke-verified but its code is UNCOMMITTED (the harness saved `tools/site_done.py` + the
`server/serve.py` docstring edit in the working tree); the it.221 DECISIONS entry IS appended in
the same commit as this hand-over. Next session: commit (c) with explicit paths
(`git add tools/site_done.py server/serve.py && git commit -m "239: retire the one-site line's model pass ..."`),
then step (d) fit/cover.py.)

**State:** branch `agent/a`. Uncommitted at the limit: tools/site_done.py (the whole of step (c)),
server/serve.py (docstring only). Committed with this hand-over: the it.221 DECISIONS entry,
this file (Touches extended), tasks/244-how-it-works-doc-code.md (NEW). No tests were run this
session (that is (e)/(h)); the 8-file suite is red by construction until (d)-(f) land.
`.venv` works. Hygiene: after any run that regenerates `docs/site_flow/307d_*.png` (only
test_fit_queue / test_owner_check do), restore `git show HEAD:docs/site_flow/<name>.png > <name>`
before committing; never `git add -A`.

**What (c) changed (all verified this session):**
- `tools/site_done.py::_fit(root, sid, model)` -> `_fit(root, sid)`: rows/docs/item_cands/
  uncovered as before; the matcher block (condition unchanged: any doc-less row AND
  `matchfit.reachable()`) now passes `results=results` to `matchfit.run(str(root), [sid], ...)`
  (238's API) and prints per written path; docs re-read, uncovered recomputed after.
- `reasons` = {e["plan"]: e["why"] for e in results if e["outcome"] == "refused"} when the
  matcher ran, else {r["id"]: "no matcher on this machine" for r in uncovered}. When the matcher
  ran it settled every doc-less candidate (incl. "picture not on this machine"), so run_sites'
  `.get()` fallback only fires when the matcher never ran.
- need_fit unchanged; `run_sites(str(root), [sid], reasons=reasons)`; **the keep re-merge of
  already-covered entries is byte-identical to the old one** (PITFALLS: the only thing protecting
  audit notes) - verified by eye this session.
- detail prints: "skip" -> "skipped: already fitted (doc sid.plan)"; "item" -> "sent to the
  review queue ({why})"; the "auto" branch deleted; the no_picture print unchanged.
- main(): the mutually-exclusive --working/--model-json group, the llm_model/recorded_model
  resolution and the `fit  no model given: ...` print (line 0 of EVERY run) are deleted -> every
  run's stdout shrinks by exactly one line; docstring usage line + step 1 reworded (matcher
  first; the second pass only records reasons). `_summary`'s display fallback
  `cand.get("why") or "no model answer"` stays (data entries may lack why).
- `server/serve.py::_fit_line` docstring reworded the same way (it calls `site_done.main([site])`
  - no flags involved; the server path's runtime behaviour is unchanged except the recorded why).
- Verification done: py_compile clean; `--help` shows only site/--root; an un-built site -> one
  error line, exit 2, no "no model given" line; three-scenario scratch-tree smoke GREEN (pattern
  below); no "model" in any printed line.

**Smoke pattern (if ever needed again):** scratch trees in /tmp, each with web/data/sites.json
(one site: id/region US/lat 51.0/lon -1.0/size_m [1000,800]/corners) + web/data/plans.json (cols
id,sites,title,label,url,ia,file,size,map_box,cite,book,ref,view; commons-style rows c_a/c_b,
size [100,100], map_box [0.1,0.1,0.9,0.9]) + empty data/db/platefits + data/review dirs. Patch
`matchfit.reachable = lambda url=None: False` (PITFALLS: never a bare False) and fake
`matchfit.run` (write_doc + results append). Scenarios: (A) unreachable -> both items
"no matcher on this machine" with the COARSE fallback (the 2-arg `propose.propose_for(sid, plan)`
call inside run_sites reads the LIVE checkout's ROOT by 202's design - a scratch site is not in
it, so the entry gets coarse:True without scale_m_px; pre-existing behaviour, not a 239 bug);
(B) matcher writes c_a -> prints "fit  matcher: fit written (smoke-b.c_a.json)", c_a then
"skipped: already fitted (doc smoke-b.c_a)", c_b's item why = "not sure: 8 consistent points
(need 10)" verbatim; (C) both refused -> both item whys = the matcher's verdict; plus a
pictureless site -> "fit  no picture found: ..." unchanged. The /tmp trees were deleted.

**(a)/(b) done earlier** (see DECISIONS it.219-220): batch_us.run_sites(root, site_ids,
reasons=None) and batch_eu.run_eu(root, reasons=None); both committed.

**Expected fallout until (d)-(f) land (reds in these files are by construction):** fit/cover.py
still forwards --model-json ((d)); the EIGHT test files still pin the deleted line / "no model
answer" ((e)); the 302f fixtures still record the 11/8 stdout line counts and "no model answer"
((f)). The 8-file suite must be green at the done claim (step (h)).

**Remaining steps (one commit each):**

(d) fit/cover.py (session-2 decision): DROP --model-json from the CLI and loop() (loop(root) no
    longer forwards it); main()'s mutually-exclusive group becomes a plain --working flag
    (REFUSED kept: lead ef84a05's placement ban is independent of this retirement); delete the
    a.model_json phase checks; reword usage line 15, flag help 50-53 and the loop docstring's
    "no model answer" wording. Search/classify phases and their model use untouched. No test
    pins cover's CLI (verified session 2).

(e) The eight test files (one commit; no model endpoint configured anywhere; offline replays
    patch `matchfit.reachable = lambda url=None: False`, never a bare False - PITFALLS):
    - test_batch_us.py / test_batch_eu.py: recorded-ANSWER tests -> recorded-REASON tests (a
      fixed {plan: why} dict into run_sites/run_eu; keep socket-blocking fixtures); tests that
      stub the GATE inside run_sites die (the batch no longer calls the gate - the gate stays
      covered by 238's test_matchfit_gate via _settle); "adds files, rewrites none" -> "adds an
      item entry, rewrites none" (no auto docs); report/sample tests stay (a synthetic record
      with a non-empty "auto" passed directly to write_report/_sample pins the seeded
      machinery); golden byte-identity checks (tests/golden/hand_fit_docs.sha256) stay;
      state-awareness: compute expectations from the live tree state, never constants (PITFALLS).
    - test_site_done.py: recount EVERY lines[N] index (the "fit  no model given" line is gone:
      the Stonehenge two-run test 11 -> 10 lines per run); live item-entry expectations (301-era
      "no model answer" whys) are DATA and stay; a test asserting a NEW uncovered candidate's
      item why == "no model answer" now expects the matcher's recorded reason or "no matcher on
      this machine" - check what each test's stub does to the /health probe.
    - test_fit_provenance.py (NEW scope): line 323 `assert lines[0] == 'fit  no model given: ...'`
      is deleted and every subsequent index shifts by -1 (line 0 becomes the site header);
      line 342's `_summary` mirror (`cand.get("why") or "no model answer"`) stays - the fallback
      is still in _summary; reword the "no model" docstring phrasings (21, 173, 423).
    - test_fit_queue.py (NEW scope): test_save_runs_the_one_site_line - the server process has
      every socket dead, so the matcher is unreachable and line 1012's assert becomes
      why == "no matcher on this machine"; reword docstrings 800/903/1002 ("the line has no
      model" -> the matcher was not reachable, recorded as such). test_placement_gestures_and
      _save_in_the_browser has been red since the 2026-10-13 loop start (pre-existing, 307d/242
      family) - do not fix it here.
    - test_owner_check.py (NEW scope; 242 owns the file - keep the edit isolated to check 7):
      want_fit (line 659) drops its first element (the deleted line) and the comment block
      (646-652, "the no-model line prints on every run") is reworded; the `assert not any
      ("matcher" in ln ...)` stays green (the batch never runs there, so no matcher line
      either). Do NOT touch _run_one / the capture / screenshot-copy region (242's).
    - test_cover.py: no CLI is pinned (session 2); only in-process expectations that mentioned
      "no model answer" for the loop phase, if any.
    - test_matchfit_station.py (302f): after (f)'s re-record the test file itself may need no
      change (its assertions read the fixtures) - the two stdout line-count expectations live in
      record.py.

(f) Fixture re-record (working phase; LIVE ELoFTR required - check
    `curl http://127.0.0.1:8091/health` first; it was up when 230 ran it.216): FIRST update
    tests/fixtures/matchfit_station/record.py - its two hardcoded stdout line-count assertions
    (11 -> 10, 8 -> 7) and its header.task ('302f' -> '239') - then
    `.venv/bin/python tests/fixtures/matchfit_station/record.py` and commit the two refreshed
    fixtures (records.json: confident, stdout shrinks; records_unsure.json: stdout shrinks AND
    the new item's cand["why"] becomes "not sure: 8 consistent points (need 10)" instead of
    "no model answer"). Per 302f's PITFALLS this re-record is the causing task's own cleanup.

(g) docs/site_flow.md: reword ONLY (1) the usage block (lines 5-7: drop `[--working |
    --model-json FILE]`; cover's usage line gets its rewording in (d)) and (2) step 1 of the
    one-site-line section (~lines 19-27), mirroring the new site_done docstring step 1 (matcher
    first; the second pass records reasons only; no model pass; no "no model answer"). The file
    is append-only for OTHER tasks' sections (302g's starts ~1722) - only the 300 section at the
    top is this task's.

(h) Verify + close: re-run the 8 files (expect green, the same 1 skip:
    test_batch_eu.py::test_union_full_coverage_live - skip-gated, pre-existing); then the full
    suite `.venv/bin/python -m pytest tests/ -p no:cacheprovider` - no NEW reds vs the driver's
    2026-10-13 loop-start note (only test_fit_queue::test_placement_gestures_and_save_in_the_
    browser red then - if still red: pre-existing, document it, do NOT fix it in 239). Byte-
    unchanged proof: the golden hand_fit_docs.sha256 checks (41 docs) inside test_batch_us/
    test_batch_eu/test_fit_provenance + `git status` clean on data/db/platefits and data/review
    after all runs; restore any regenerated 307d PNGs to HEAD bytes. Tick each acceptance box
    ONLY after its own check passes; set Status: done when all five are ticked.

**Pitfalls relevant (read the full entries before coding):** PITFALLS fit/ -> "batch_us.
pre_docs matches any existing <site>.*.json" (snapshot pre-run state before run_sites in tests),
"Recorded-answer batch tests must be state-aware" (same for recorded-reasons), "write_report
(path=None) silently falls back to docs/batch_us.md"; tests/test_matchfit_station.py -> the
fixture's input_hashes cover the WHOLE index row (any evidence re-stamp since it.216 = rerun
record.py - (f) refreshes them); tools/site_done.py, fit/review.py -> "A batch re-run of a
review-item row replaces that candidate's entry whole - site_done's skip guard is the only thing
protecting audit notes" (the keep re-merge must keep surviving); Model servers -> 8081/8080 LLMs
banned for fit PLACEMENT (ef84a05) - cover keeps --working REFUSED and every other path has no
model flag at all; "Patching matchfit.reachable for an offline replay needs a lambda returning
False - a bare False crashes the run"; A/B in-checkout, never a bare worktree.

**Note for the DECISIONS entry (already appended with this commit - do not re-write it):** the
it.221 entry covers the (c) changes/verification above, the scope discovery (three test files
added to Touches: test_fit_provenance.py:323, test_fit_queue.py:1012+800/903/1002,
test_owner_check.py:659 - owners all done except 242's capture region), the server/serve.py
absorption (no open task owns it: 305 done, 236c doesn't touch it), and task 244 filed
(docs/how-it-works.md's "Doc vs code" Qwen bullet names the now-false `fit/batch_us.py
--working`; the section is stale in more places since before 211/212; 244 = lowest free
200-499, Depends on: 239). Session-3's header accidentally used `###`; entries use `##` per
AGENTS.md (old entries are never rewritten).
