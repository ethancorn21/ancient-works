Status: done
Depends on: none
Touches: fit/src_van_deventer.py, tests/test_src_van_deventer.py, PITFALLS.md

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
- [x] `check_staged()` returns 0 when every staged row is already present in the canonical
      files.jsonl with identical content (temp-file construction); the QID/site-id problems
      self-triggered by the module's own merged rows are gone.
- [x] The same key held by a different canonical row is still reported (check rc 1) - the
      pre-merge conflict protection is unchanged; the six done towns are still refused.
- [x] The pre-merge behavior is unchanged: with the canonical file not containing the staged
      rows, every assertion of test_check_staged_files_join_and_pass and
      test_table_and_staged_rows that passed before still passes.
- [x] Full suite green on this checkout (the two named tests pass in the unmerged state of
      main, and the new three-state test passes in all three constructed states).

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 223 kip, 224 mackenzie,
  225 limes, 226 numancia, 227 stukeley, 228 artists), filed by agent a on 211, iteration 174,
  after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them, it does not repair a
  red main. 211's merge lands on top once this merges; the merged-state pass on the real files
  is verified there.

## Hand-over
(2026-10-12, iteration 192, agent a - 222 DONE this session; the pattern for 223-228 is set below.)

State of this branch (agent/a, the 211 merge lives here):
- Suite: 8 failed / 133 passed / 1 skipped (loop start: 10 failed / 130 passed / 1 skipped;
  my 2 vd tests greened + 1 new three-state test, ZERO new reds). The 8 remaining are exactly
  the 223-228 sibling guard tests:
    228 artists  test_check_staged_files_join_and_pass
    223 kip      test_check_staged_offline
    225 limes    test_check_staged_files_join_and_pass
    224 mackenzie test_staged_row_and_join
    226 numancia test_check_staged_files_join_and_pass
    227 stukeley test_stage_offline (SystemExit!), test_check_staged_offline, test_book_rows_staged_in_files_b
- NEXT (human lead, in order): 223 kip, then 224, 225, 226, 227, 228. One module per task;
  each is the same fix, copy the pattern below.

THE PATTERN (what 222 did, to reuse verbatim per module):
1. Refactor (own commit, prove same red set): the module's canonical-file paths become
   module-level constants so a test can point them at temp copies. vd already had
   FILES_CANONICAL; I added EXTRAS_CANONICAL / SITES_CATALOG / SITES_WEB and made known_sites()
   read them. For siblings: read their module (fit/src_kip.py etc.), find the paths check_staged
   (or `check` for mackenzie) and known_sites use - some are inlined in known_sites(), some are
   already constants. Note stukeley's stage() also failed (SystemExit) - its stage leg may guard
   against canonical too; inspect before copying (227 is the odd one out).
2. Fix (own commit), in check_staged only:
   - id collision:  staged_ids & (set(known.values()) - staged_ids)   [was: & set(known.values())]
   - QID reuse:     known[s["qid"]] != s["id"] when s["qid"] in known   [was: bare membership]
   - canonical clash: key (site, title) present in canonical files.jsonl is a problem only when
     _canon_norm(staged row) != _canon_norm(canonical row); _canon_norm =
     json.dumps(row, sort_keys=True, ensure_ascii=False) (the same norm fit/merge.py uses on the
     line). Build the canonical map first-row-wins. Keep the original failure message text.
   - the six/done-town TOWNS-table check stays untouched.
3. Test (same commit as 2): (a) update the existing test's known-site assertion to the
   same-site-only semantic (loop: if s["qid"] in known: assert known[s["qid"]] == s["id"]);
   (b) add a three-state hermetic test: monkeypatch the canonical path constants to temp copies -
   state (a) canonical minus this module's staged rows (pre-merge; works on ANY checkout),
   state (b) minus + the staged rows appended verbatim (json.dumps(r, ensure_ascii=False), as the
   merge wrote them) + web sites.json gets {"id","qid"} entries for the staged sites, state (c)
   state (b) with ONE staged row's field changed (I used year+1) in the temp canonical. Assert:
   (a) rc 0 / no "join:" / evidence all-pass line; (b) same; (c) rc 1 and the join lines are
   exactly [the canonical-clash line naming that key]. No network (the no_network fixture), no
   ports, writes only to tmp_path.

Gotchas learned (also in the DECISIONS entry): keep edits to these guard blocks small and verify
line-by-line with `python -c "import ast; ast.parse(...)"` after each edit - I mangled a bracket
on one assert twice; and run live commands under .venv/bin/python (system python3 has no PIL).

Re-read:
- fit/src_van_deventer.py:check_staged - the new guard logic (the pattern source for 223-228).
- tests/test_src_van_deventer.py:test_check_staged_three_states - the pattern test.
- 211's hand-over gate note (tasks/211-merge-build.md) - once all of 222-228 are done, 211's
  next session re-runs the suite for the green claim; 229/230 stay dependency-gated.
