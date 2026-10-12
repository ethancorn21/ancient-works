Status: open
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
- [ ] `check_staged()` returns 0 when every staged row is already in the canonical files with
      identical content (constructed temp canonical files).
- [ ] The same key held by a different canonical row is still reported (rc 1) - the pre-merge
      conflict protection is unchanged.
- [ ] The pre-merge behavior is unchanged: test_check_staged_files_join_and_pass and every
      other test_src_numancia.py test that passed before still passes with the canonical files
      not containing the staged rows.
- [ ] Full suite green on this checkout.

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  224 mackenzie, 225 limes, 227 stukeley, 228 artists), filed by agent a on 211, iteration 174,
  after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.
