Status: open
Depends on: none
Touches: fit/src_van_deventer.py, tests/test_src_van_deventer.py

# 222: Van Deventer check/stage accepts the staging rows once 211 has merged them

## Goal
211's live merge (box 1, done on 211's branch) appends every `files_van_deventer*.jsonl` /
`classified_van_deventer*.jsonl` row into `data/commons/files.jsonl` / `classified.jsonl` and the
town sites into `data/catalog/extras.jsonl` - byte-identical, first-row-wins. The staging files
stay in place and the module's `--check` still reads them, but `fit/src_van_deventer.py`'s
`check_staged()` treats any staged `(site, title)` that is already in the canonical
`files.jsonl` as a clash, and its known-site checks (`staged_ids & known.values()`,
`s.get("qid") in known`) self-trigger, because `known_sites()` reads the canonical extras, which
after the merge contain the module's own staged towns. Result: on any tree where the merge has
run, `test_check_staged_files_join_and_pass` and `test_table_and_staged_rows` are red.

Fix the guard, not the data: in `check_staged()` (and any other guard in this module), a staged
row whose key is already in the canonical file is

- OK (a no-op "already merged by 211") when the staged row is equal to the canonical row under
  the merge's identity rule (`json.dumps(..., sort_keys=True, ensure_ascii=False)` - the same
  `norm()` fit/merge.py uses),
- still a problem (keep today's fail-loud behavior) when the key is held by a DIFFERENT row.

For the known-site checks: `known_sites()` gaining the module's own staged sites is not a
collision - a staged id/QID is a problem only when it resolves to a DIFFERENT site
(`known[qid] != staged id`; `staged id in known.values() - staged_ids`). The "six done towns are
not re-staged" check (TOWNS-table based) is unaffected by the merge and stays as it is.

The test covers all three states hermetically (no network, no fixed ports, no writes outside the
project or a temp dir): (a) staged row absent from the canonical file - the current assertions,
unchanged; (b) staged row present in the canonical file with identical content (constructed:
point the module's canonical-file path constants at a temp copy that includes the staged rows)
- check returns 0; (c) same key, different row - still fails loudly. The test must not depend on
211's live merge having run on this checkout.

## Acceptance criteria
- [ ] `check_staged()` returns 0 when every staged row is already present in the canonical
      files.jsonl with identical content (temp-file construction); the QID/site-id problems
      self-triggered by the module's own merged rows are gone.
- [ ] The same key held by a different canonical row is still reported (check rc 1) - the
      pre-merge conflict protection is unchanged; the six done towns are still refused.
- [ ] The pre-merge behavior is unchanged: with the canonical file not containing the staged
      rows, every assertion of test_check_staged_files_join_and_pass and
      test_table_and_staged_rows that passed before still passes.
- [ ] Full suite green on this checkout (the two named tests pass in the unmerged state of
      main, and the new three-state test passes in all three constructed states).

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 223 kip, 224 mackenzie,
  225 limes, 226 numancia, 227 stukeley, 228 artists), filed by agent a on 211, iteration 174,
  after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them, it does not repair a
  red main. 211's merge lands on top once this merges; the merged-state pass on the real files
  is verified there.
