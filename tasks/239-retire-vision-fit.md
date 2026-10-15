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

(2026-10-14, iteration 225, agent a - (e) is HALF DONE: the two batch test files are rewritten
on disk (uncommitted, harness-saved); the FIVE patch files are still untouched; no tests were
run this session. NEXT SESSION: apply the five targeted patches below, run the four fast test
files, commit all eight in ONE commit, then do (f) - ELoFTR was UP at it.225 start.)

**State:** branch `agent/a`, tree: only `tests/test_batch_us.py` and `tests/test_batch_eu.py`
modified (the (e) rewrites, verified by git status at session end). (a)-(d) all committed
(DECISIONS it.220-222). test_cover.py stays byte-unchanged in (e) (re-grep-verify at session
start: zero model hits).

**it.225 live re-verification (all confirmed by running code; tree clean at start):**
US 90 / EU 418 sites. serpent 16 cands / pre-doc ancientmonuments00squi_n0210_1 / 15 item
cands / unresolved; cahokia 5 / pre-docs [c_1a7c2a11c3a0dd21, c_aff1b996dce7fe3a] / 4 item
cands / resolved by c_1a7c2a11c3a0dd21 (uncov=3: the item holds one doc'd cand too);
mound-bottom 1 cand = its doc / no item; first zero-cand US sorted = aberdeen-mound-q4666953
(no item, no pre_fit). newark 21 / ArcheologicalAtlasOfOhio_n0098_1 / 21 item / resolved /
uncov=20; forthill 4 / b24849959_n0269_1 / 4 / resolved / uncov=3; marietta 4 / 0 / 4 /
unresolved; fudge+highbank+hopeton 0 cands + site.json pre_fit, NO item (all six region-less
is_pre_fit=True); yeavering-bell-camp-q17643662 0 cands / no pre_fit / HAS the 212a
no-picture item (CORRECTION to the it.223/224 "no item" note: the batch re-stamps its
no_picture_found.searched with its own string - upsert_item replaces it when passed a dict -
and the file name stays <site>.json with no lead); avebury 7 / earthworkenglan01allcgoog_
n0581_1 / 5 item / uncov=6; old-sarum 5 / 4 pre-docs / 3 item / resolved / uncov=1.
platefits/ = 71 docs = 22 by:hand + 49 fitter:matcher; golden = 41 lines (22 docs + 19
site.json). docs/batch_eu.md "Sites run: 294" != live EU 418 -> test_union_full_coverage_live
skip-gates (expected). ELoFTR UP at 127.0.0.1:8091 (zju-community/matchanything_eloftr, RTX
5060 Ti) -> (f) is doable next session. API re-checks: review.upsert_item (dict no_picture
replaces, None+entries clears, None+no-entries keeps; resolved write-once; lead =
candidates[0]); item_path lead-None -> <site>.json; propose.propose_for(sid, plan, root=
default checkout) - the batch's _entry calls it 2-arg, the tests' _check_entry mirrors that.

**(e) part 1 DONE - the two rewrites (on disk, uncommitted):** tests/test_batch_us.py
(4 tests: test_sample_run_records_reasons, test_no_reasons_records_no_matcher,
test_batch_adds_items_rewrites_none, test_report_reproducible_from_seed) and
tests/test_batch_eu.py (7: the same 4 EU-shaped - the no-reasons one uses batch_eu.run_eu
over all 418 - plus test_hand_fitted_sites_get_items_for_their_other_pictures
[AVEBURY/OLDSARUM], test_union_check, test_union_full_coverage_live). Shape per the it.224
designs: NO_MATCHER + _VERDICTS(3) + state-aware _recorded_reasons (sha1(plan)%3) +
_check_entry (2-arg propose, pairs==[], no gate_score) + _syn_records (2,11); the US
report test parses the 5-cell per-candidate table and pins random.Random(SEED).sample
for both synthetic branches (k==n IS a seeded shuffle). Read them fresh before committing.

**(e) part 2 - the FIVE patches to apply (exact old -> new; all were re-verified in place this
session):**

1. **tests/test_site_done.py** (5 spots): (i) module docstring line 16: "network attempt
   fails loudly; no model is needed and no picture is fetched);" -> "network attempt fails
   loudly: the pretrained matcher is unreachable so it is never called, and no picture is
   fetched);". (ii) _run docstring line 243: "`, no model.`" -> " (sockets dead: the
   matcher is unreachable and never called).". (iii) first run: DELETE line 285
   `assert lines[0] == 'fit  no model given: ...'`; `lines[1]` -> `lines[0]` (site header),
   the fit-summary two-line assert `lines[2]` -> `lines[1]` (its text UNCHANGED:
   `{len(rows)} candidate picture(s): {len(docs)} fitted (doc), {len(orig)} in the review
   item -> no batch run needed`). (iv) `assert len(lines) == 3 + len(docs) + 2 + len(rows)
   + 1` -> `2 + ...`. (v) second run: keep `lines2[0] == lines[0]`; DELETE `lines2[1] ==
   lines[1]` (the fit summaries now DIFFER: 7 vs 0 fitted); the explicit
   `lines2[2] == (f"fit  {len(rows)} candidate picture(s): 0 fitted (doc), {len(cands)} in
   the review item -> no batch run needed")` becomes `lines2[1] == ...`. The two _summary
   mirrors (lines 306, 353: `cand.get("why") or "no model answer"`) STAY (display
   fallback; every live Stonehenge entry has a why). Rationale: Stonehenge uncovered == 0
   in both runs -> matchfit.reachable() IS called (dead sockets -> False, caught) ->
   matcher never runs -> need_fit False -> "no batch run".
2. **tests/test_fit_provenance.py** (case b + docstrings): module docstring case b:
   "sockets dead, no model - the refusal precedes the build, so nothing is downloaded" ->
   "sockets dead: the matcher is unreachable so it is never called, and the refusal
   precedes the build, so nothing is downloaded"; _run docstring line 173 as in 1(ii);
   _mini_tree docstring line 423 "needs no download, no model, no network" -> "needs no
   download and no network". Case b asserts (lines 323-342): DELETE the lines[0] "no model
   given" assert and shift: lines[1]->[0] site header, lines[2]-[3]->[1] fit summary
   (`{n_item} ... 1 fitted (doc), {n_item-1} ...`), lines[4]->[2] sync refused, lines[5]->
   [3] entry, lines[6]->[4] review line; `lines[6:6+len(expected)]` -> `[5:5+len(expected)]`;
   `lines[6+len(expected)] == "done"` -> `[5+len(expected)]`; `len(lines) == 6 + len(
   expected) + 1` -> `5 + len(expected) + 1`. The `cand.get("why") or "no model answer"`
   mirror (line 342) STAYS. Second run `out2.splitlines() == lines` stays.
3. **tests/test_fit_queue.py** (5 spots; do NOT touch test_placement_gestures... -
   pre-existing red since 2026-10-13): line ~800 _pick_site docstring: "so the line's
   model=None path runs and lands in the item as "no model answer"" -> "so the
   no-matcher path runs and lands in the item as "no matcher on this machine""; line ~814
   sort comment "the no-model path runs" -> "the no-matcher path runs"; test docstring
   line ~903: "The line's model is None and every socket in the server process is dead, so
   the run is network-free: any unfitted candidate lands in the item as "no model answer""
   -> "Every socket in the server process is dead, so the matcher is unreachable and the
   run is network-free: any unfitted candidate is recorded in the item as "no matcher on
   this machine""; comment lines ~1002-1003 -> "was recorded in the item as "no matcher on
   this machine" (the matcher was not reachable in the server process)"; assert line
   ~1012 -> `after_cands.get(u, {}).get("why") == "no matcher on this machine", u`.
4. **tests/test_owner_check.py** (ISOLATE to check 7; do NOT touch _run_one/_capture/
   screenshot-copy - 242's): comment block lines ~646-651: "The no-model line prints on
   every run (the worker runs the line without a model) and so does the no-batch line:
   every candidate is the saved doc or an item candidate, so the batch never runs." ->
   "The no-batch line prints on every run: every candidate is the saved doc or an item
   candidate, so the matcher (unreachable - sockets dead) is never called and the batch
   never runs."; want_fit (line ~659) drops its first element -> only `f"fit  {len(rows)}
   candidate picture(s): {n_doc} fitted (doc), {len(rows) - n_doc} in the review item -> no
   batch run needed"`. `assert not any("matcher" in ln ...)` stays green (matcher never
   runs -> no "matcher" line; "no matcher on this machine" is never printed either since
   uncovered == 0 -> reasons {}).
5. **tests/test_matchfit_station.py** (2 edits; the fixtures STAY until (f)): module
   docstring lines ~19-21: "the candidate in the site's review item with the batch's own
   reason ("no model answer", from the socket-dead vision pass) plus the scale-bar
   proposal" -> "... with the matcher's recorded reason ("not sure: 8 consistent points
   (need 10)" - the RoMa port is dead, so no "; RoMa ..." suffix) plus the scale-bar
   proposal"; line 313: `cand["why"] == "no model answer"` -> `cand["why"] == "not sure:
   8 consistent points (need 10)"`. The stdout asserts read the fixture's
   expected_stdout - they fail until (f) re-records (RED BY CONSTRUCTION, do not "fix"
   by weakening).

**Then (one commit):** `git add tests/test_batch_us.py tests/test_batch_eu.py tests/
test_site_done.py tests/test_fit_provenance.py tests/test_fit_queue.py tests/test_owner_
check.py tests/test_matchfit_station.py && git commit -m "239: retire the vision pass in
the tests - the batch tests pass recorded matcher reasons (no model, no gate, no docs);
the line/provenance/queue/owner/matchfit tests drop the deleted first stdout line and the
'no model answer' expectations (the matcher's recorded reasons take their place)"`.
**Expected red until (f):** test_matchfit_station (stale fixtures: 11/8-line stdout +
"no model answer" item) and the pre-existing test_fit_queue::
test_placement_gestures_and_save_in_the_browser. Everything else in the 8-file set must be
green. Run: `.venv/bin/python -m pytest tests/test_batch_us.py tests/test_batch_eu.py
tests/test_site_done.py tests/test_fit_provenance.py -p no:cacheprovider` (batch trees are
hard-linked, fast); test_fit_queue::test_save_runs_the_one_site_line ~30-180 s, worth
running; owner_check is browser-heavy - if run, `git checkout -- docs/site_flow/` after
(307d PNGs regenerate). If a batch test fails: it is a state-drift (a new plans.json row
for a sample site) or a bug in my rewrites - check which, fix the test only if the live
state moved, never weaken an assertion.

**(f) fixture re-record (ELoFTR was UP at it.225 start - re-check `curl -s
http://127.0.0.1:8091/health` first):** in tests/fixtures/matchfit_station/record.py
update the two stdout line-count asserts 11->10 and 8->7, header.task '302f'->'239', then
`.venv/bin/python tests/fixtures/matchfit_station/record.py`; commit the two refreshed
fixtures (expected_stdout loses line 0; unsure's lines 3+6 and item.why become "not sure:
8 consistent points (need 10)"; responses/input_hashes/matcher_health re-recorded). If
down: DECISIONS entry + come back. record.py is the only writer - never hand-edit.

**(g)** docs/site_flow.md: reword ONLY the 300 section (usage block lines 5-7 drop
`[--working | --model-json FILE]`; step 1 ~lines 19-27 mirrors the new site_done docstring:
matcher first, second pass records reasons, no model pass). Append-only for every other
section (302g's rule).

**(h) verify + close:** the 8-file set green (only the pre-existing placement_gestures red);
full suite no NEW reds vs the 2026-10-13 driver note; golden byte-identity + git status
clean on data/db/platefits and data/review; tick the 5 acceptance boxes, Status: done.

**Hygiene:** .venv works. Never `git add -A` (explicit paths). Tests: no fixed ports, no
writes outside project/tmp. A/B in-checkout only, never a bare worktree (PITFALLS 306d).
**Pitfalls to re-read before applying the patches:** PITFALLS fit/ - "pre_docs matches any
existing <site>.*.json" (snapshot pre-run state before run_sites), "Recorded-answer batch
tests must be state-aware" (same for recorded reasons), "write_report (path=None) silently
falls back to docs/batch_us.md" (batch_eu pins its own); "A batch re-run of a review-item
row replaces that candidate's entry whole" (the upsert replaces same-plan entries in place,
keeps other plans' entries whole, resolved write-once - the tests assert exactly that);
"Patching matchfit.reachable for an offline replay needs a lambda returning False - a bare
False crashes the run" (the batch tests need no such patch: the batch never calls the
matcher; the line tests rely on reachable()'s own except-Exception).
