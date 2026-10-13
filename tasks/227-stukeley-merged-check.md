Status: done
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
- [x] The stage command is a no-op for rows already merged into the canonical files (identical
      content) and still SystemExits for a different row with the same key.
- [x] The check returns 0 in the merged state (constructed temp canonical files) and still
      reports a same-key/different-row clash.
- [x] The pre-merge behavior is unchanged: with the canonical file not containing the staged
      rows, every assertion that passed before still passes (the book-rows test keeps asserting
      the row shape - plate/year/ia_id/evidence - and the title is asserted absent-or-identical).
- [x] Full suite green on this checkout. (148 passed / 1 skipped / 1 failed: the single failure
      is tests/test_src_artists.py - the 228 sibling's, proven pre-existing by the 226 session's
      run; no stukeley test fails and none failed that had not been red before this task.)

## Hand-over
(2026-10-12, iteration 197, agent a - DONE, awaiting the driver's re-check. The three-state
211-merge guard is in place on both legs and the hermetic three-state tests follow the 222-226
pattern; verified this session: 10/10 module tests, live --check rc 0 and --dry a no-op on the
merged tree, suite reds down to exactly the 228 (artists) sibling - pre-existing.)

What changed (all in the two files on the Touches line):
- fit/src_wiltshire_stukeley.py: new _canon_norm() (the merge identity rule: json.dumps
  sort_keys/ensure_ascii=False - the same norm fit/merge.py uses). In _stage_commons, stage_book
  and check_staged the canonical scan now builds a first-row-wins (site, title) -> norm map plus
  a title set, and the old blanket title guard became three-state: a key the canonical file
  holds is a no-op ("already merged by 211") only when the module's own staged row (read from
  files_wiltshire_b.jsonl, not the freshly-built row - the built row's evidence.checked is the
  run date) is identical to the canonical row; a same-key DIFFERENT row still SystemExits
  (stage) / is a join problem (check); the original title-only clash (a title held by a
  different site, e.g. the two Petrie 1880 files) is kept as the fallback and still fails loud.
  Guard order in both stage legs is unchanged (in _stage_commons the canonical guard stays the
  FIRST per-row check, so test_canonical_title_clash_fails_loud's "clash fires before any meta
  use" still holds; in stage_book the stage-A reclassification check stays first). Module
  docstring, the usage block and the function docstrings were updated to the three-state rule.
- tests/test_src_wiltshire_stukeley.py: new _merge_states(tmp_path, monkeypatch) helper (the
  222/223 pattern, simplified - stukeley has no extras/web state, only FILES_CANONICAL; it
  builds files_pre = canonical minus the module's own (site, title) keys and staged_lines =
  the module's rows as the byte-identical merge append; it reads the REAL staging file via the
  module-level FILES_B_REAL snapshot because test_stage_offline monkeypatches src.FILES_B at a
  temp write target). test_stage_offline and test_canonical_title_clash_fails_loud now point
  FILES_CANONICAL at the pre-merge temp state, so they hold whether or not 211's live merge
  ran on the checkout. test_book_rows_staged_in_files_b keeps every row-shape assertion and the
  blanket "title not in canonical" became "not in canonical OR the canonical row holding the
  (site, title) key is identical to this one". New test_check_staged_three_states (a: absent
  -> 0; b: identical -> 0; c: same key different row -> 1 with exactly one join problem) and
  test_stage_offline_three_states (a: pre-merge no-op; b: merged no-op; c: Commons-leg same-key
  different row -> SystemExit, nothing written; d: book-leg same-key different row -> the
  Commons leg no-ops and stage_book refuses) - all hermetic: temp canonical copy, the autouse
  no-network fixture's FAKE_META, the checked-in stage-A triage file, no ports.

Verification (this session, this checkout - 211's live merge IS in this branch, 09a9472):
- .venv/bin/python -m pytest tests/test_src_wiltshire_stukeley.py -q -> 10 passed (was 3
  failed / 5 passed at session start: test_stage_offline, test_check_staged_offline,
  test_book_rows_staged_in_files_b red by design on the merged tree).
- Live: fit/src_wiltshire_stukeley.py --check -> rc 0, "evidence: 5 rows, 5 pass, 0 fail, 0
  no-tie", zero join problems (was 5 self-triggered join problems); --dry -> "staged: 0 new
  pictures" / "book: 0 new plan rows" rc 0 (was SystemExit on the Houghton title clash).
- Full suite: pytest tests/ -q -> 148 passed, 1 skipped, 1 failed; the single failure is
  tests/test_src_artists.py::test_check_staged_files_join_and_pass (the 228 sibling, owned by
  its own task; the 226 session's run proved the 227+228 set pre-existing). No stukeley test
  fails; nothing that passed before fails now.

Pre-merge branch note (for 211's gate bookkeeping): on main pre-merge the five Stukeley rows
are NOT in the canonical files, so every test also passes there unmodified - the hermetic
states are constructed, not assumed; this is exactly the 222-226 shape, and 211's merge lands
on top once all seven merge (its box 6 golden reference and the live merged-state check are
verified in 211, not here).

No PITFALLS entry warranted (nothing new beyond what the 222-226 sessions recorded; the
only new wrinkle - _merge_states must not read a monkeypatched module constant - is local to
this test file and commented in it).

If the driver rejects this claim, next step: re-run
`.venv/bin/python -m pytest tests/test_src_wiltshire_stukeley.py -q` and the live --check/--dry
commands above; the 228 red is outside this task (it has its own task file and agent).

## Notes
- One of seven sibling tasks 222-228 (same fix, one module each: 222 van_deventer, 223 kip,
  224 mackenzie, 225 limes, 226 numancia, 228 artists), filed by agent a on 211, iteration 174,
  after the live merge turned these source checks red on 211's branch (211 depends on all
  seven; none touches data/staging rows - only the guard logic and its test).
- On main (pre-merge) the tests are green today; this task extends them. 211's merge lands on
  top once this merges; the merged-state pass on the real files is verified there.
