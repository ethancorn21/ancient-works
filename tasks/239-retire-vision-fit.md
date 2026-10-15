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

(2026-10-14, iteration 223, agent a - (e) NOT started (no edits this session); the FULL
reconnaissance for (e) is done - the next session writes the new test files straight from
the designs below. NEXT SESSION: (e) the eight test files, one commit.)

**State:** branch `agent/a`, tree clean. The whole (a)-(d) chain is in (see DECISIONS it.220-222):
(a) fit/batch_us.py `run_sites(root, site_ids, reasons=None)` - no model/gate/docs, uncovered ->
item `why` = reasons.get(plan) or "no matcher on this machine"; pictureless -> no-picture item;
`gate_placement`/`write_doc`/`write_item`/`_entry`/`write_report`(+`_sample`, SEED 20261010) stay
(gate_placement/write_doc are the matcher's, covered by 238's tests/test_matchfit_gate.py line 191
and the matchfit tests - the batch's stub-gate tests may die safely).
(b) fit/batch_eu.py `run_eu(root, reasons=None)` -> run_sites over eu_sites(root).
(c) tools/site_done.py `_fit(root, sid)` matcher-first (`matchfit.run(..., results=results)`),
reasons = refused results' why or "no matcher on this machine"; `--working`/`--model-json` and
the first `fit  no model given` stdout line deleted (every run's stdout -1 line); `_summary`
keeps the DISPLAY fallback `cand.get("why") or "no model answer"` (data entries may lack why -
the test mirrors of that line STAY as-is).
(d) fit/cover.py loop(root) no --model-json forwarding; --working plain-refused; wording reworded.

**(e) reconnaissance COMPLETE this session - verified facts and per-file plans:**

- **No dangling refs:** only test_batch_us/test_batch_eu still call the deleted
  `batch_us.recorded_model` (grep-verified tree-wide; plan_fit.py:148 mentions "llm_model"
  only in a historical docstring comment about the fabrication class - NOT in 239's Touches,
  leave it).
- **test_cover.py is byte-unchanged in (e)** (grep: zero "no model"/"model-json"/"--working"/
  "recorded_model" hits; session-2 finding confirmed again).
- **test_matchfit_station.py DOES need two edits** (last hand-over's "no change" was wrong for
  them): docstring lines 19-21 ("with the batch's own reason ('no model answer', from the
  socket-dead vision pass)" -> "with the matcher's recorded reason ('not sure: 8 consistent
  points (need 10)')") and line 313
  `cand["why"] == "no model answer"` -> `cand["why"] == "not sure: 8 consistent points (need 10)"`.
  The stdout asserts read the fixture (`hdr["expected_stdout"]`) - unchanged here, refreshed in
  (f). VERIFIED the clean why: in that test RoMa is at a dead port -> `use_roma =
  reachable(roma)` False (matchfit.py:331; reachable() catches all exceptions, :106-112) -> the
  "; RoMa ..." suffix (matchfit.py:348) never fires; judge() (:97) gives exactly "not sure: 8
  consistent points (need 10)" for 8 inliers (MIN_INLIERS=10).
- **test_site_done.py:** Stonehenge run has uncovered = 0 (all 13 rows are docs or item
  candidates) -> `matchfit.reachable()` IS called (any() true first) but returns False (dead
  sockets, caught) -> matcher never runs, need_fit False -> both runs are "no batch run"
  runs. Edits: delete `assert lines[0] == 'fit  no model given: ...'` (:285); :286 lines[1]
  -> lines[0] (site header), :287-288 lines[2] -> lines[1]; `len(lines) == 3 + len(docs) + 2 +
  len(rows) + 1` -> `2 + len(docs) + 2 + len(rows) + 1`; second run: `lines2[0] == lines[0]`
  stays (both site header), DELETE `lines2[1] == lines[1]` (the fit-summary lines now DIFFER:
  7 vs 0 fitted), keep the explicit `lines2[1] == f"fit  {len(rows)} candidate picture(s):
  0 fitted (doc), {len(cands)} in the review item -> no batch run needed"` as lines2[1].
  Docstrings :16 and :243 reword ("no model is needed" -> matcher unreachable, never called
  because uncovered is empty). The _summary mirrors at :306/:353 stay verbatim (display
  fallback; all live entries have a why, so the fallback never fires there).
- **test_fit_provenance.py (case b):** delete :323 (lines[0] assert); shift EVERY later index
  by -1: :324->:323 site header, :325-326->:324 fit summary (n_item, 1 fitted), :327->:325
  sync-refused, :328->:326 entry, :329-332->:327-330 (n_open/n_total then the review line),
  :339-340 -> `lines[5:5+len(expected)] == expected`, :341 -> `lines[5+len(expected)] ==
  "done"`, :342 -> `len(lines) == 5 + len(expected) + 1`. Docstrings: :21 ("sockets dead, no
  model" -> matcher unreachable, never called), :173 (_run docstring), :423 (_mini_tree:
  "no download, no model, no network" -> "no download and no network"). :354 mirror (cand's
  recorded why or display fallback) stays. Second run: `out2.splitlines() == lines` stays
  (idempotent, both lost the model line).
- **test_fit_queue.py:** :800 _pick_site docstring + :814 sort comment ("the no-model path
  runs" -> "the no-matcher path runs"); :903 test docstring ("The line's model is None..." ->
  "every socket in the server process is dead, so the matcher is unreachable and the run is
  network-free"); :1002-1004 comment ("went to the item as 'no model answer' (the line has
  no model)" -> "recorded as 'no matcher on this machine' (the matcher was not reachable
  in the server process)"); :1012 assert -> `why == "no matcher on this machine"` (the server
  process runs site_done.main([site]) with all sockets dead -> reachable() False -> that
  exact path). Do NOT touch test_placement_gestures... (pre-existing red since 2026-10-13).
- **test_owner_check.py (242 owns - ISOLATE to check 7):** comment block :646-651 reword
  ("The no-model line prints on every run (the worker runs the line without a model) and so
  does the no-batch line" -> "The no-batch line prints on every run: every candidate is the
  saved doc or an item candidate, so the matcher (unreachable - sockets dead) is never
  called and the batch never runs"); :659 want_fit drops its first element -> only the
  `f"fit  {len(rows)} candidate picture(s): {n_doc} fitted (doc), {len(rows) - n_doc} in the
  review item -> no batch run needed"` line. `assert not any("matcher" in ln ...)` stays
  green (matcher never runs -> no matcher line). DO NOT touch _run_one / capture /
  screenshot-copy (242's).
- **test_batch_us.py / test_batch_eu.py: FULL REWRITES** (write tool; each ~350 lines). Keep
  verbatim: no_network, _link_tree, _WRITE_IN_PLACE, tree, tmp_path_retention_policy, _sha,
  _golden, _rows, _row_for (eu only), _sites, _pre, _item_files, _item, _source_evidence,
  _table, _syn_records, GOLDEN, the site-id constants (US: SERPENT/CAHOKIA/MOUNDBOTTOM; EU:
  REGIONLESS list, NO_PIC=yeavering-bell-camp-q17643662, AVEBURY, OLDSARUM). DELETE:
  _answers/_short_answers/_answer_pairs/_corner_pairs/_expected/_stub_site/STUB_*_consts/
  _recorded_model/the pinned *ANSWER_PLANS and *_SHORT lists/fit_gate+plan_fit imports (us
  keeps propose only; eu keeps propose only too). NEW shared shape in each file:
  ```
  NO_MATCHER = "no matcher on this machine"
  _VERDICTS = ("not sure: 8 consistent points (need 10)",
               "median residual 106.4 m > 45.0 m", "picture not on this machine")
  def _recorded_reasons(sids):  # STATE-AWARE: live candidates, one verdict per plan by sha1(plan)%3
      out = {}
      for sid in sids:
          for r in batch_us.candidates(sid, _rows()):
              out[r["id"]] = _VERDICTS[int(hashlib.sha1(r["id"].encode()).hexdigest(), 16) % 3]
      return out
  def _check_entry(sid, row, entry, why):  # plan/title/url vs row; why == why (the passed reason);
      # evidence == _source_evidence; pairs == []; no gate_score; propose.propose_for(sid, plan)
      # 2-arg fields (or coarse fallback) - the old tail of _check_entry, minus the pairs/gate branches
  ```
  New tests (us, 4): test_sample_run_records_reasons (reasons=_recorded_reasons(sample);
  per site: detail == {skip} for pre-docs and {item, why: reasons[plan]} for uncovered;
  auto == []; pre_fit == pre-run; no_picture == (no cands and not pre_fit); item == (uncovered
  or no_picture); the item: one file, resolved write-once, new entries via _check_entry, old
  pre-existing entries survive BYTE-EQUAL (`c == old`), candidate set == pre-union-uncovered;
  mound-bottom: all skip, no item; zero-cand site: no-picture item, searched string, candidates
  []); test_no_reasons_records_no_matcher (run_sites(tree, sample) CLI form: every uncovered
  detail/item why == NO_MATCHER; assert at least one uncovered exists); test_batch_adds_items_
  rewrites_none (golden equal pre+post; every pre-existing file byte-identical except sample
  sites' own item files - site/resolved/plans preserved; NO new file under data/db/platefits;
  every new file is a sample-site review item); test_report_reproducible_from_seed (real
  records -> byte-identical twice, title "# The batch, US (203a)", seed, Sites run, counts,
  automatic fit == 0, sample table == ["(none)"]; per-candidate table parsed from 5-cell rows:
  pre-docs ("skip", ""), uncovered ("item", NO_MATCHER), zero-cand ("no-picture", "");
  synthetic: _syn_records(1,3) -> all docs listed, _syn_records(2,11) -> exactly
  random.Random(batch_us.SEED).sample(sorted 22, 20) in order, page URL "#" per row).
  EU (5): same 4 with the EU sample (REGIONLESS + NO_PIC) plus:
  test_hand_fitted_sites_get_items_for_their_other_pictures (AVEBURY/OLDSARUM: pre-docs skip,
  fresh -> item entries with the passed reasons merged into the live item, no new doc for any
  fresh candidate, golden byte-identical) and test_report's retired counts:
  automatic fit == []; already hand-fitted == {s in REGIONLESS: is_pre_fit(tree, s)};
  no-picture == [NO_PIC] iff NO_PIC has no candidates else []; review item == the complement
  (NO_PIC is the only non-pre-fit in the sample; region-less sites with items stay in
  "already hand-fitted" because classify checks pre_fit first). test_union_check/test_union_
  full_coverage_live stay as-is (the live one skip-gates on docs/batch_eu.md "Sites run: 294"
  vs 418 live EU sites - expected skip).
- **Live tree state (measured this session, for the state-aware expectations):**
  US: serpent-mound 16 cands / pre_docs [ancientmonuments00squi_n0210_1] / item 15 cands;
  cahokia 5 cands / pre_docs [c_1a7c2a11c3a0dd21, c_aff1b996dce7fe3a] / item 4 cands / RESOLVED
  by c_1a7c2a11c3a0dd21; mound-bottom 1 cand = its doc / no item; aberdeen-mound (first
  zero-cand US, sorted) no item candidates / no-picture item. EU: newark 21 cands / 1 pre-doc
  (ArcheologicalAtlasOfOhio_n0098_1) / item 21 / resolved; forthill 4 / 1 (b24849959_n0269_1) / 4 /
  resolved; marietta 4 / 0 / 4 / unresolved; fudge+highbank+hopeton 0 cands + site.json pre_fit,
  no item; yeavering-bell 0 cands / no pre_fit / no-picture item; avebury 7 cands / 1 pre-doc
  (earthworkenglan01allcgoog_n0581_1, golden hand fit) / item 5; old-sarum 5 cands / 4 pre-docs /
  item 3 / resolved. eu_sites = 418. classify() order: error > auto > pre_fit > no_picture >
  item.
- **One commit** for all of (e) (8 files named; test_cover.py and possibly nothing else in it
  stays byte-unchanged - it still passes against the new loop()). Suite is RED BY CONSTRUCTION
  after (e) until (f) re-records the matchfit_station fixtures (records.json/records_unsure.json
  still carry the old 11/8-line stdout and "no model answer" item) - expected, do not "fix"
  by weakening; (f) makes it green.

**Remaining steps:** (f) fixture re-record (LIVE ELoFTR: FIRST `curl -s
http://127.0.0.1:8091/health`; if up: update record.py's two stdout line-count asserts 11->10,
8->7 and header.task '302f'->'239', run `.venv/bin/python tests/fixtures/matchfit_station/record.py`,
commit both refreshed fixtures; if down: DECISIONS + come back). (g) docs/site_flow.md: reword
ONLY the 300 section (usage block lines 5-7 drop `[--working | --model-json FILE]`; step 1
~lines 19-27 mirror the new site_done docstring; append-only otherwise). (h) verify + close:
8 files green, full suite no NEW reds vs 2026-10-13 (only test_fit_queue::
test_placement_gestures_and_save_in_the_browser pre-existing red), golden byte-identity + git
status clean on data/db/platefits and data/review, tick boxes, Status: done.

**Hygiene:** .venv works. Never `git add -A` (explicit paths). After running
test_fit_queue / test_owner_check restore `git show HEAD:docs/site_flow/<name>.png > <name>`
(they regenerate docs/site_flow/307d_*.png; agent c works 241 in its own checkout but the
driver merges, so don't leave them dirty). A/B in-checkout only, never a bare worktree.

**Pitfalls to re-read before (e):** PITFALLS fit/ - "batch_us. pre_docs matches any existing
<site>.*.json" (snapshot pre-run state BEFORE run_sites in tests), "Recorded-answer batch
tests must be state-aware" (same rule for recorded-reasons: compute uncovered from the LIVE
tree), "write_report (path=None) silently falls back to docs/batch_us.md"; tools/site_done.py,
fit/review.py - "A batch re-run of a review-item row replaces that candidate's entry whole -
site_done's skip guard is the only thing protecting audit notes" (the upsert replaces
same-plan entries in place, keeps other plans' entries whole, resolved write-once - the tests
assert exactly that); Model servers - 8081/8080 LLMs banned for fit PLACEMENT (ef84a05);
"Patching matchfit.reachable for an offline replay needs a lambda returning False - a bare
False crashes the run" (the batch tests need no such patch: they never call the matcher).
