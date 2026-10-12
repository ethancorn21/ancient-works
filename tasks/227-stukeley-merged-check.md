Status: open
Depends on: none
Touches: fit/src_wiltshire_stukeley.py, tests/test_src_wiltshire_stukeley.py

# 227: Stukeley check/stage accepts the staging rows once 211 has merged them

## Goal
211's live merge (box 1, done on 211's branch) appends the staged Stukeley rows (both legs: the
1740 book plates and the Commons-hosted Stukeley plates, staged into
`files_wiltshire_b*.jsonl` / `classified_wiltshire_b*.jsonl`) into the canonical
`data/commons/files.jsonl` / `data/commons/classified.jsonl` - byte-identical,
first-row-wins; the staging files stay and the module's `--check` still reads them. On 211's
branch three tests are red for the resulting guard clash:

- `test_stage_offline` - the stage command SystemExits on a canonical-title clash;
- `test_check_staged_offline` - the check records the staged titles as canonical clashes;
- `test_book_rows_staged_in_files_b` - the test itself asserts `title not in canonical`
  (the pre-merge invariant, now false by design).

Fix the guard, not the data: a staged row whose `(site, title)` key is in the canonical file is

- OK (no-op, "already merged by 211") when the staged row is equal to the canonical row under
  the merge's identity rule (`json.dumps(..., sort_keys=True, ensure_ascii=False)` - the same
  `norm()` fit/merge.py uses) - so a re-run of the stage command after the merge is an
  idempotent no-op,
- still fail-loud (SystemExit in the stage command, problem in the check) when the key is held
  by a DIFFERENT row (the original purpose of the clash guard, e.g. a Stukeley row colliding
  with a non-Stukeley canonical row of the same name).

Update the test to the three-state logic hermetically (no network, no fixed ports, no writes
outside the project or a temp dir): (a) staged row absent from canonical - the current
assertions, with the blanket "not in canonical" assertion replaced by "not in canonical OR
identical to it"; (b) staged row in the canonical file with identical content (constructed:
point the module's canonical path constants at a temp copy that includes the staged rows) -
check rc 0, stage a no-op; (c) same key, different row - still SystemExit/problem. The test
must not depend on 211's live merge having run on this checkout.

## Acceptance criteria
- [ ] The stage command is a no-op for rows already merged into the canonical files (identical
      content) and still SystemExits for a different row with the same key.
- [ ] The check returns 0 in the merged state (constructed temp canonical files) and still
      reports a same-key/different-row clash.
- [ ] The pre-merge behavior is unchanged: with the canonical file not containing the staged
      rows, every assertion that passed before still passes (the book-rows test keeps asserting
      the row shape - plate/year/ia_id/evidence - and the title is asserted absent-or-identical).
- [ ] Full suite green on this checkout.

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  224 mackenzie, 225 limes, 226 numancia, 228 artists), filed by agent a on 211, iteration 174,
  after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.
