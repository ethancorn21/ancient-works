Status: done
Depends on: 001, 803
Touches: tools/gate_heldout.py, tests/test_gate.py

# 802: gate-holdout: ignore the batch's automatic documents

## Goal
Task 001's one-shot measurement (docs/gate.md sections 3-9) is registered over exactly the 20
pre-batch hand-fit documents: `tools/gate_heldout.py partition()` sorts every
`data/db/platefits/*.json` name and fails loudly when the count is not 20, because then the
registered partition (seed 20260108 over the 20 sorted names) would be void. The 203a US batch
(merged) added 16 automatic documents to the same directory, so the precondition now reads 36
and the section-6 command aborts:

    gate_heldout: expected 20 hand-fit documents in data/db/platefits/, found 36;
    the registered partition is void, see docs/gate.md section 1

Automatic documents are the batch's own output (the page's format plus `"auto": true` and the
gate's score) and were never part of the golden/held-out reference: `fit/batch_us.py
write_golden` already excludes them from tests/golden/hand_fit_docs.sha256, and 203a's box 4
proved the 20 hand-fit documents are byte-identical after the run. The registered partition
is therefore still meaningful - it just must be derived over the non-automatic set.

## Acceptance criteria
- [x] `tools/gate_heldout.py partition()` builds its name list from the NON-automatic
      documents only (a doc's `"auto": true` marks the batch's output; a doc without the field
      is a hand fit); the 20-doc precondition, the seed-20260108 partition derivation and
      `check_registered` stay otherwise untouched, and the section-6 command runs to
      completion on the current checkout
- [x] tests/test_gate.py is green: test_recorded_measurement_reproduces_and_agrees reproduces
      tests/golden/gate_heldout.txt byte for byte (40 held + 60 dev lines) and
      test_fit_gate_constants_are_the_frozen_section2_rule still passes; tests/golden/
      gate_heldout.txt and docs/gate.md section 9 are NOT regenerated - the 20 hand-fit
      documents are byte-identical, so the recorded tables must come out unchanged. If they
      do not, that is a finding to record in this task's DECISIONS entry, not a silent
      golden rewrite. (They did come out unchanged: the golden and section 9 are untouched in
      the diff and reproduce byte for byte.)

## Notes
- Filed by agent c (task 203a) iteration 41, from the full-suite run after the 203a working
  run landed on this branch (4 failed / 34 passed; the other 3 failures are 803's).
- 2026-10-11 iteration 42 (agent c): `Depends on` changed 203a -> 001 (done). The original
  dependency created a loop: 203a's done claim requires a green suite, which needs this task
  merged, which waited on 203a. The re-baseline is STATE-AGNOSTIC, so the loop is void:
  the non-auto name list equals the original 20 hand-fit names before AND after any batch
  (automatic documents only ADD names; no hand-fit doc ever gains `"auto": true`), so the
  partition, tests/golden/gate_heldout.txt and docs/gate.md section 9 reproduce byte for
  byte in both states. Implement it on the branch you are given - it may or may not carry
  203a's 16 auto docs - and it must pass in whichever state you find (36 docs here, 20 on
  a plain main-based checkout).
- docs/gate.md's wording ("the 20 documents") stays true: it describes the hand fits; this
  task only changes which files the tool counts. If the wording needs a sentence clarifying
  that automatic documents are excluded, it goes in this task's scope (docs/gate.md section
  1), recorded in DECISIONS. (2026-10-11: judged NOT needed - section 1 is the frozen
  pre-registration ("not to be changed") and never promised to count every .json in the
  directory; section 3's "the 20 hand-fit documents in data/db/platefits/" stays literally
  true. The clarification lives in the tool's docstrings. docs/gate.md untouched. See DECISIONS.)
- 2026-10-11 iteration 46 (agent c): the driver rejected the done claim - its re-verification runs the FULL
  suite and it was red: 3 failed / 35 passed, all in tests/test_review.py, which is task 803's file
  (`Touches: tests/test_review.py`; 803 is open, its dependency 201 is done, unassigned). Those 3 tests
  fail identically without this task's change (pre-802 suite: 4 failed / 34 passed; the 4th was 802's
  own, fixed), so the implementation stands as verified in iteration 45 and nothing in it changed.
  802 cannot pass the re-check until 803 is done and merged, so per the team-mode rule `Depends on:`
  now lists 803 and the task parks until 803 is in main. The human already knows about the 802/803 pair
  (203a's ask_human 002).

## Hand-over

**2026-10-11, iteration 47 (agent c): 803 is IMPLEMENTED and verified in BOTH states; the full suite is green;
both done claims (802, 803) are filed. The code (tests/test_review.py) is UNCOMMITTED in the working tree -
the harness saved it; commit it FIRST in the next session, then re-verify, then re-file if the driver
reopened anything.**

What happened this session (the human answered ask 002: "approved, your recommendation. You get 802 as a
job now, then 803, then 203a again to re-file the done claim. Add only the files those two tasks name to
their own Touches lines." - so agent c implements 803 from this branch; each task keeps its own Touches line):

- **803 done (task file set done, boxes ticked).** tests/test_review.py re-baselined per the 42-note spec:
  - `test_export_cli`: expected stdout "N open of M items", the open list and every per-item field
    (name from sites.json/id-fallback, lead = first candidate's plan, candidates and no_picture verbatim)
    derived through `review.resolved_doc` + the export's documented stable name-sort - new helpers
    `_open_items(tree)` / `_site_names(root)` in the test file. A `n_total >= 1` guard kills vacuous passes.
  - `test_page_shows_the_review_list`: tab label `Review (N)` (or bare `Review` at N=0), the stats clause
    `\u00a0\u00b7 N review item(s) open` (absent at N=0, "nothing left to review" instead), rvn == N, and the
    list phrases derived from the first open item (name, head, first candidate title, or the no-picture
    searched text) plus the first open item that HAS candidates - the 404/boot/no-error checks are unchanged.
  - `test_save_resolves_the_item`: the doc is now built from the plans.json ROW exactly as the page's
    saveFit does (row's ia/file/label/book/cite, crop = map_box x size, src 'book', url/ref from the row;
    pairs from the item's candidate entry = the human's proposed pairs). The pick is deterministic: first
    plans.json row (file order) with ia+map_box+size whose site has an OPEN item carrying that candidate.
    Post-batch pick: (fort-ancient-q5470727, ancientmonuments00squi_n0076_1). Pre-batch it reduces to
    (alligator, n0214_2) - the old pin. Post-save: open list minus the picked site, first remainder
    verbatim, the item file's `resolved == {doc, at}` (file found via `review.item_path`), stored-doc
    round-trip. The 4s worker poll and the snapshot (no other tree change) are unchanged.
  - ALLIGATOR/BIBRACTE/LEAD constants deleted; nothing else in the file changed (probes, keying test,
    index-footprint test, fixtures).
- **Verified both states (the state-agnostic bar):** post-batch (this checkout, 89 items): full suite
  `.venv/bin/python -m pytest -q` = **38 passed, 0 failed** (42.9s; headless tests ran, Chrome present).
  Pre-batch: built /tmp/prebatch-803 = this checkout with the 203a data diff INVERTED (103 A files under
  data/ removed; the one M - alligator's item - restored from main), ran `tests/test_review.py` +
  `tests/test_gate.py` there with the project's .venv: **7 passed** (31s). The temp tree was deleted
  afterwards. 802's own two-state claim is re-proven by that run (test_gate green pre-batch).
- **802 set done again** (its earlier claim was rejected only on the suite being red; it is green now).
  Implementation unchanged since af830fb (nothing touched tools/gate_heldout.py or tests/test_gate.py
  this session; `git log` on both paths since af830fb was empty when I checked).
- **203a NOT touched** (still in-progress on my branch, per the human's sequence its re-file comes after
  802/803 are merged; its six boxes are all ticked and its own tests are in the green 38).

Next session (should be agent c again, on 802 or 203a):
1. `git status` / `git diff --stat` in the checkout: expect tests/test_review.py modified (uncommitted -
   the harness saved it) plus the already-committed task-file changes. Verify the diff touches ONLY
   tests/test_review.py among code files (803 box 3). If the working tree is clean, something committed
   it already - check `git log` first.
2. `git add tests/test_review.py && git commit -m "803: re-baseline the review-queue tests to derived
   expectations - ..."` (see the DECISIONS entry for the wording I drafted there).
3. Re-run `.venv/bin/python -m pytest -q`; expect 38/38. If the driver rejected either done claim,
   its reasons are in the 802/803 task files' Notes / DECISIONS.md - fix and re-file.
4. If I was given 203a instead: re-file 203a's done claim (suite green, six boxes ticked, 39/39 golden
   per its last hand-over) and rewrite its stale BLOCKED hand-over (it is resumed; ask 002 was answered
   in my favor).
5. Optional polish (low priority, only if the above is done): a PITFALLS entry under This codebase / fit/:
   "batch upserts replace a review item's rich candidate entries (201's map_box/ia/file/label/book/cite)
   in place with the batch's slim shape (plan/title/url/evidence/pairs/why/gate_score, no map_box) -
   the page's web/review.js rvResolveRow therefore falls back to the web/data/plans.json row for those
   fields; tests must read the row, not the entry. Where: data/review/*, fit/review.py upsert_item,
   web/review.js rvResolveRow. Symptom: KeyError 'map_box' in a test building a save doc from an
   item entry."
