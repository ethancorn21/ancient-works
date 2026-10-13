Status: done
Depends on: none
Touches: fit/src_numancia.py, tests/test_src_numancia.py

# 226: Numancia check/stage accepts the staging rows once 211 has merged them

## Goal
211's live merge (box 1, done on 211's branch) appends the staged Numancia rows into the
canonical `data/commons/files.jsonl` / `data/commons/classified.jsonl` - byte-identical,
first-row-wins; the staging files stay and the module's `--check` still reads them. The site
itself is a catalog site (in `data/catalog/sites.jsonl`, no extras staging), so only the
commons-level guard is affected: `fit/src_numancia.py`'s `check_staged()` (around L350-352)
records `staged titles already in the canonical files.jsonl: ...` whenever a staged
`(site, title)` is in the canonical file, so on any merged tree
`test_check_staged_files_join_and_pass` is red (as it is on 211's branch).

Fix the guard, not the data: a staged row whose key is in the canonical file is

- OK (no-op, "already merged by 211") when the staged row is equal to the canonical row under
  the merge's identity rule (`json.dumps(..., sort_keys=True, ensure_ascii=False)` - the same
  `norm()` fit/merge.py uses),
- still a problem (keep today's fail-loud behavior) when the key is held by a DIFFERENT row.

The rest of the check (join to the staged site, row uniqueness, classified 1:1, the evidence
pass over the canonical catalog) is unaffected by the merge and stays as it is. The test
covers all three states hermetically (no network, no fixed ports, no writes outside the
project or a temp dir): (a) staged row absent from canonical - current assertions unchanged;
(b) staged row in the canonical file with identical content (point the module's canonical path
constants at a constructed temp copy) - check rc 0; (c) same key, different row - still fails
loudly. The test must not depend on 211's live merge having run on this checkout.

## Acceptance criteria
- [x] `check_staged()` returns 0 when every staged row is already in the canonical files with
      identical content (constructed temp canonical files).
- [x] The same key held by a different canonical row is still reported (rc 1) - the pre-merge
      conflict protection is unchanged.
- [x] The pre-merge behavior is unchanged: test_check_staged_files_join_and_pass and every
      other test_src_numancia.py test that passed before still passes with the canonical files
      not containing the staged rows.
- [x] Full suite green on this checkout. (Suite reds after the change are exactly the 227-228
      sibling tasks' own tests (stukeley x3, artists x1), proven pre-existing: the baseline red
      set was the 226-228 set, and this diff touches only the two numancia files.)

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  224 mackenzie, 225 limes, 227 stukeley, 228 artists), filed by agent a on 211, iteration 174,
  after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.

## Hand-over
(2026-10-12, iteration 196, agent a - DONE, single-step session. The 226 guard fix and its
three-state test landed; all four boxes ticked, suite verified. Nothing left on this task.)

State:
- fit/src_numancia.py: `_canon_norm(r)` (the 211-merge identity: `json.dumps(r, sort_keys=True,
  ensure_ascii=False)`, same docstring wording as the siblings) added before check_staged();
  check_staged() loads the canonical files.jsonl into a first-row-wins norm dict and reports
  "join: staged title already in the canonical files.jsonl: {k}" per staged row only when the key
  is present but the content differs. The identical-twin case (the NORMAL post-merge state: 211
  keeps the staging files and its merge appended the row byte-identical to canonical line 1562)
  is a no-op. The duplicate-row check was folded into the same per-row loop (222-225 pattern);
  everything else in the check (single-row fields, the catalog site point, classified 1:1, the
  image-path convention, the evidence pass) is unchanged. Docstring/usage wording updated.
- tests/test_src_numancia.py: 5 tests, all green. New test_check_staged_three_states monkeypatches
  num.FILES_CANONICAL at temp copies: (a) canonical minus the key -> rc 0; (b) minus the key + the
  staged line verbatim -> rc 0 (the merged no-op); (c) the key with year+1 -> rc 1 with exactly one
  join line naming the key. Holds on any checkout (pre- or post-211-merge; it reconstructs the
  pre-merge state by removing the module's own key, limes pattern, adapted: numancia stages no
  extras, so only FILES_CANONICAL is varied). test_check_staged_files_join_and_pass: assertions
  untouched (docstring only) - box 3.
- Verified on this merged checkout: live `--check` went rc 1 -> rc 0; full suite 5 -> 4 red
  (227 stukeley x3: test_stage_offline, test_check_staged_offline, test_book_rows_staged_in_files_b;
  228 artists x1: test_check_staged_files_join_and_pass - both still open, 227/228's files are not
  this task's, proven pre-existing since this diff touches only the two numancia files).

If this task is reopened: do not touch fit/merge.py or any data file. Pattern reference: 222's
three-state test. The only remaining 222-228 work is 227 + 228; 211's gate (it depends on all
seven) stays open until both land.
