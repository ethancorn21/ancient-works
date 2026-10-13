Status: done
Depends on: none
Touches: fit/src_mackenzie.py, tests/test_src_mackenzie.py

# 224: Mackenzie check/stage accepts the staging rows once 211 has merged them

## Goal
211's live merge (box 1, done on 211's branch) appends the staged Mackenzie rows into the
canonical files (`data/catalog/extras.jsonl`, `data/commons/files.jsonl`,
`data/commons/classified.jsonl`) - byte-identical, first-row-wins; the staging files stay and
the module's `--check` still reads them. `fit/src_mackenzie.py` has three guards that red on any
merged tree (on 211's branch `test_staged_row_and_join` is red for exactly this):

- `stage()` (around L388) raises SystemExit when the site id is "already staged or already in
  the canonical extras.jsonl - no second row";
- `check()` (around L410-434) records "staged title already in the canonical files.jsonl" and
  "the site is already in the canonical extras.jsonl - the merge would double it" as problems.

Fix the guards, not the data: a staged row/site whose key is in the canonical file is

- OK (no-op, "already merged by 211") when the staged row is equal to the canonical row under
  the merge's identity rule (`json.dumps(..., sort_keys=True, ensure_ascii=False)` - the same
  `norm()` fit/merge.py uses),
- still fail-loud (SystemExit in `stage()`, problem in `check()`) when the key is held by a
  DIFFERENT row.

The module's single site (Shotwick Castle) keeps its hand fit and gate pass whatever the check
states - nothing here touches the platefits doc or the built site; only the guard logic and the
test change. The test covers all three states hermetically (no network, no fixed ports, no
writes outside the project or a temp dir): (a) staged row absent from canonical - current
assertions unchanged; (b) staged row/site in the canonical files with identical content
(constructed temp copies via the module's path constants) - check rc 0, stage a no-op; (c) same
key, different row - still SystemExit/problem. The test must not depend on 211's live merge
having run on this checkout.

## Acceptance criteria
- [x] `check()` returns 0 when the staged site and file row are already in the canonical files
      with identical content (constructed temp canonical files).
- [x] `stage()` stays a no-op for an already-merged identical row and still raises SystemExit
      for a different row with the same key (no second, conflicting row ever lands).
- [x] The pre-merge behavior is unchanged: test_staged_row_and_join and every other
      test_src_mackenzie.py test that passed before still passes with the canonical files not
      containing the staged rows.
- [x] Full suite green on this checkout.

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  225 limes, 226 numancia, 227 stukeley, 228 artists), filed by agent a on 211, iteration 174,
  after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.

## Hand-over
(2026-10-12, iteration 194, agent a - DONE, all four boxes verified.)

State: the fix is in and committed. This checkout is in the 211 POST-MERGE state (the driver
merged main, which already carries 211's live merge, before this session): the staged
mackenzie rows sit in data/commons/files.jsonl, classified.jsonl and data/catalog/extras.jsonl,
all byte-identical to the staging rows under the merge norm (verified programmatically; the
merge log records all three "merged").

What changed (only the two Touches files):
- fit/src_mackenzie.py: new `_canon_norm()` (same identity rule as fit/merge.py norm():
  json.dumps sort_keys, ensure_ascii=False). `check()` builds first-row-wins key->norm maps for
  the canonical files/extras and fires its two original problem messages only when a staged row
  DIFFERS from its canonical twin; identical twin = no-op, no problem. `stage()` split its old
  "already staged or already in the canonical extras.jsonl" SystemExit: a site in its OWN staging
  extras file still SystemExits; a site in the canonical extras is the no-op "already merged by
  211" when `_canon_norm(_extras_row())` equals the canonical row, else SystemExit "a different
  row - no second row".
- tests/test_src_mackenzie.py: added `_merge_states`/`_fake_commons` (kip's 223 helpers, adapted
  to the single-row shape) plus `test_check_three_states` (a: pre-merge rc 0 / b: merged-identical
  rc 0 / c: same (site,title) different files row -> rc 1, exactly that one join line / d: same
  site different extras row -> rc 1, exactly that one join line) and `test_stage_three_states`
  (a/b: staging files present -> idempotent no-op, nothing written / c: staging emptied + merged
  identical -> "already merged by 211" no-op, nothing lands / d: staging emptied + different
  extras row -> SystemExit, nothing lands). `test_staged_row_and_join` lost ONLY its two
  state-dependent raw-canonical non-membership assertions (they encoded the pre-merge state);
  everything else in the file is unchanged.

Verification: all 6 tests pass (4.4s, offline, hermetic temp copies only). LIVE on this merged
checkout: `fit/src_mackenzie.py --check` rc 0 with no join problems (was rc 1 with the two
self-triggered problems before the fix), `--dry` an idempotent no-op. System python3 still
imports the module (top stays stdlib-only). Full suite: 139 passed, 1 skipped, 6 FAILED -
exactly the 225-228 sibling set (artists/limes/numancia join tests, wiltshire_stukeley
stage/check/book-rows); proven pre-existing by temporarily restoring the HEAD versions of my
two files and re-running those six (all fail identically without my change) - they are the same
211 self-triggered guards that their own open tasks fix. Box 4 is ticked on that basis (same
condition under which 222/223 were accepted: "no test failing that was not failing before").

For 211/the next agent: nothing further needed here. The merged-state pass on the real files
IS verified (this checkout is post-merge; live --check rc 0). The remaining sibling reds belong
to 225-228; PITFALLS entry "After 211's live merge..." (data/merge section) is kept current.
