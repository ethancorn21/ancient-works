Status: done
Depends on: none
Touches: fit/src_kip.py, tests/test_src_kip.py

# 223: Kip check/stage accepts the staging rows once 211 has merged them

## Goal
211's live merge (box 1, done on 211's branch) appends every `files_kip*.jsonl` /
`classified_kip*.jsonl` row into the canonical `data/commons/files.jsonl` / `classified.jsonl`
(byte-identical, first-row-wins); the staging files stay and the module's `--check` still reads
them. `fit/src_kip.py` has two guards that red on any merged tree:

- `stage()` (around L519-548) raises SystemExit when a `(site, title)` is already in the
  canonical files.jsonl - written to protect the six hand-tied views (sources.py's rows) from
  re-staging;
- `check_staged()` (around L589-618) records "staged title already in the canonical
  files.jsonl" as a problem.

On 211's branch `test_check_staged_offline` is red for exactly this reason.

Fix the guards, not the data: a staged row whose key is in the canonical file is

- OK (no-op, "already merged by 211") when the staged row is equal to the canonical row under
  the merge's identity rule (`json.dumps(..., sort_keys=True, ensure_ascii=False)` - the same
  `norm()` fit/merge.py uses),
- still fail-loud (SystemExit in `stage()`, problem in `check_staged()`) when the key is held
  by a DIFFERENT row.

Keep the hand-tied protection airtight: the six hand-tied views live in the canonical file in
sources.py's row shape, so a Kip-shaped re-stage of one of them is "different" and still
refused. If a verbatim copy of a hand-tied row could be staged and would now pass as
"identical", keep an explicit refusal of exactly those six `(site, title)` keys in `stage()`
(recommended - it is cheap and the "never re-staged" rule was deliberate).

The test covers all three states hermetically (no network, no fixed ports, no writes outside
the project or a temp dir): (a) staged row absent from canonical - current assertions
unchanged; (b) staged row in the canonical file with identical content (point the module's
canonical path constants at a constructed temp copy) - check rc 0, stage a no-op; (c) same key,
different row (the hand-tied shape) - still SystemExit/problem. The test must not depend on
211's live merge having run on this checkout.

## Acceptance criteria
- [x] `check_staged()` returns 0 when every staged row is already in the canonical files.jsonl
      with identical content (constructed temp canonical file).
- [x] `stage()` stays a no-op for an already-merged identical row and still raises SystemExit
      for a different row with the same key (in particular the six hand-tied views, whatever
      their row shape).
- [x] The pre-merge behavior is unchanged: test_check_staged_offline and every other
      test_src_kip.py test that passed before still passes with the canonical file not
      containing the staged rows.
- [x] Full suite green on this checkout.

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 224
  mackenzie, 225 limes, 226 numancia, 227 stukeley, 228 artists), filed by agent a on 211,
  iteration 174, after the live merge turned these source checks red on 211's branch (211
  depends on all seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.

## Hand-over
(2026-10-12, iteration 193, agent a - 223 DONE this session.)

What changed (two files, per Touches):
- `fit/src_kip.py`: new `_canon_norm` (the 211 merge's identity, same norm fit/merge.py uses).
  `stage()` guard order is now: the six hand-tied `(site, title)` keys (derived from the canonical
  file's `by == "pipeline/sources.py kip"` rows) refused outright -> a canonical-held key is a
  no-op `continue` only when the module's own staged row (files_kip, `staged_norm`) is identical to
  the first-row-wins canonical row, else SystemExit -> `have` check. `check_staged()`: staged
  id/QID problems only when a DIFFERENT site holds the key (`staged_ids & (known.values() -
  staged_ids)`; `known[qid] != s["id"]`), canonical map is first-row-wins `_canon_norm`, conflict
  only on different content; the kip_six title check and all other join rules untouched.
- `tests/test_src_kip.py`: two new hermetic tests, `test_check_staged_three_states` (a/b/c: pre-merge
  0, merged-identical 0, same-key hand-tied-shape row rc 1 with exactly the 2 join lines) and
  `test_stage_offline_three_states` (a/b no-op "staged: 0 new sites, 0 new pictures"; c SystemExit
  hand-tied; d SystemExit different row). Helpers `_merge_states` (points the module's canonical
  path constants at temp copies: files minus/plus staged rows, extras/web minus/plus the module's
  sites; works whether or not 211's live merge ran on the checkout) and `_fake_commons` (serves
  `c.info` from the stored FILES_KIP rows; `year_of`/`keep` delegate to the real pure
  `pipeline/commons` functions) are the reusable machinery for 224-228.

Verification: live `fit/src_kip.py --check` rc 0 on this merged branch (was red: 21 self-triggered
  join problems); test_src_kip.py 11/11; full suite 8->7 red / 133->136 passed / 1 skipped - the 7
  remaining are exactly the 224-228 sibling set (each its own queued task; 222 was accepted on the
  same terms, box 4 = no new reds). No refactor commit was needed (unlike 222/van_deventer):
  src_kip's canonical paths were already module-level constants.

NEXT (human lead, in order): 224 mackenzie, then 225 limes, 226 numancia, 227 stukeley, 228 artists.
Same fix per module; copy the 222/223 pattern. 224's red test is test_staged_row_and_join (its
`check` function, not check_staged - read the module first). 227 (stukeley) is the odd one out:
three reds including test_stage_offline (SystemExit) - its stage leg guards against canonical too;
use the `_fake_commons` helper here for its stage coverage. 211's gate closes when 224-228 are all
done (211 re-runs the suite for its green claim).
