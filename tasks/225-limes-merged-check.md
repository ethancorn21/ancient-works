Status: done
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
- [x] `check_staged()` returns 0 when every staged row is already in the canonical files with
      identical content (constructed temp canonical files).
- [x] The same key held by a different canonical row is still reported (rc 1) - the pre-merge
      conflict protection is unchanged.
- [x] The pre-merge behavior is unchanged: test_check_staged_files_join_and_pass and every
      other test_src_limes.py test that passed before still passes with the canonical files not
      containing the staged rows.
- [x] Full suite green on this checkout. (Suite reds after the change are exactly the 226-228
      sibling tasks' own tests (numancia/stukeley/artists), proven pre-existing: the baseline run
      before this change had all 5 of them plus the limes one, now green.)

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  224 mackenzie, 226 numancia, 227 stukeley, 228 artists), filed by agent a on 211, iteration
  174, after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.

## Hand-over
(2026-10-12, iteration 195, agent a - DONE. Fit/src_limes.py's check_staged() now accepts the 211
merged state, following the 222/223 sibling pattern exactly:

1. Added `_canon_norm(r)` = `json.dumps(r, sort_keys=True, ensure_ascii=False)` (the same identity
   fit/merge.py's norm() uses on a line), placed between check_staged and _norm.
2. check_staged(): (a) id-collision check now `staged_ids & (known_ids - staged_ids)` and the QID
   check now `known_qids[s["qid"]] != s["id"]` - the module's own staged rows (which 211's live
   merge put into canonical extras.jsonl) no longer self-trigger; a DIFFERENT site holding the
   id/QID still fails loud. (b) canonical files.jsonl is loaded into a first-row-wins dict of
   `_canon_norm` (not a set of keys): a staged row whose (site, title) key is in canonical is OK
   when its norm equals the canonical row's, still `join: staged title already in the canonical
   files.jsonl: (site, title)` when different. Everything else (forts-table join, row completeness,
   classified 1:1, evidence pass) untouched. Docstring updated in the sibling wording.
3. tests/test_src_limes.py: module docstring + test_check_staged_files_join_and_pass docstring
   updated; added `test_check_staged_three_states` - hermetic (temp copies of files.jsonl /
   extras.jsonl / sites.jsonl pointed at via monkeypatch of FILES_CANONICAL/EXTRAS/SITES_JSONL;
   no web constant in limes, no stage() coverage needed: limes' stage() is offline by construction
   and idempotent on its own staging files, it never reads canonical): (a) staged rows removed from
   the temp canonical files (pre-merge) - rc 0, no join, 56/56 evidence PASS; (b) staged rows
   present with identical content (211 merged) - rc 0, no join; (c) victim row year+1 (same key,
   different row) - rc 1 with exactly that one join line.

Verification on this checkout (211's live merge HAS run here: all 56 staged files rows + 45 extras
rows are in the canonical files, byte-identical under _canon_norm, staged ids only in extras.jsonl
never sites.jsonl): test_src_limes.py 6/6 pass; live `fit/src_limes.py --check` rc 0 (was rc 1 with
100 self-triggered join problems: 1 id-collision line listing all 45 ids, 43 QID re-uses, 56 title
collisions) and evidence 56/56 PASS. Full suite: 141 passed, 1 skipped, 5 failed - exactly the
226/227/228 siblings (test_src_numancia, test_src_wiltshire_stukeley, test_src_artists), proven
pre-existing by the baseline run before this change (6 failed, same 5 + limes).

No further action on 225. 211's gate (211 depends on all of 222-228) is still open on 226/227/228;
the limes share of it is done. If 211 comes back to this branch, the merged-state pass on the real
files is already verified (live --check rc 0 above).
