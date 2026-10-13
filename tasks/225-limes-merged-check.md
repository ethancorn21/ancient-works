Status: open
Depends on: none
Touches: fit/src_limes.py, tests/test_src_limes.py

# 225: Limes check/stage accepts the staging rows once 211 has merged them

## Goal
211's live merge (box 1, done on 211's branch) appends every staged Limes row (the 56 named
fort plans of 43 ORL forts) into the canonical `data/catalog/extras.jsonl` /
`data/commons/files.jsonl` / `data/commons/classified.jsonl` - byte-identical,
first-row-wins; the staging files stay and the module's `--check` still reads them.
`fit/src_limes.py`'s `check_staged()` (around L1134-1176) records "staged title already in the
canonical files.jsonl" as a problem for every staged row, so on any merged tree
`test_check_staged_files_join_and_pass` is red (as it is on 211's branch).

Fix the guard, not the data: a staged row whose `(site, title)` key is in the canonical file is

- OK (no-op, "already merged by 211") when the staged row is equal to the canonical row under
  the merge's identity rule (`json.dumps(..., sort_keys=True, ensure_ascii=False)` - the same
  `norm()` fit/merge.py uses),
- still a problem (keep today's fail-loud behavior) when the key is held by a DIFFERENT row.

The rest of the check (join to the forts table, row completeness, classified 1:1, the
evidence pass) is unaffected by the merge and stays as it is. The test covers all three states
hermetically (no network, no fixed ports, no writes outside the project or a temp dir):
(a) staged row absent from canonical - current assertions unchanged; (b) staged row in the
canonical file with identical content (point the module's canonical path constants at a
constructed temp copy) - check rc 0; (c) same key, different row - still fails loudly. The test
must not depend on 211's live merge having run on this checkout.

## Acceptance criteria
- [ ] `check_staged()` returns 0 when every staged row is already in the canonical files with
      identical content (constructed temp canonical files).
- [ ] The same key held by a different canonical row is still reported (rc 1) - the pre-merge
      conflict protection is unchanged.
- [ ] The pre-merge behavior is unchanged: test_check_staged_files_join_and_pass and every
      other test_src_limes.py test that passed before still passes with the canonical files not
      containing the staged rows.
- [ ] Full suite green on this checkout.

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  224 mackenzie, 226 numancia, 227 stukeley, 228 artists), filed by agent a on 211, iteration
  174, after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.
