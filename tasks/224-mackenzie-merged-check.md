Status: open
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
- [ ] `check()` returns 0 when the staged site and file row are already in the canonical files
      with identical content (constructed temp canonical files).
- [ ] `stage()` stays a no-op for an already-merged identical row and still raises SystemExit
      for a different row with the same key (no second, conflicting row ever lands).
- [ ] The pre-merge behavior is unchanged: test_staged_row_and_join and every other
      test_src_mackenzie.py test that passed before still passes with the canonical files not
      containing the staged rows.
- [ ] Full suite green on this checkout.

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  225 limes, 226 numancia, 227 stukeley, 228 artists), filed by agent a on 211, iteration 174,
  after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.
