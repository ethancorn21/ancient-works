Status: open
# 230: The Roman staging into the canonical data - the 211 consolidation re-run
Depends on: 211, 207a, 207b, 807, 808
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py

## Goal
211's lead note: the 211 consolidation ran without the Roman books (207 was stopped by
the owner at merge time) and "207a/207b staging, if it ever resumes, goes through a
later re-run of this step." This task is that re-run. Once 211 is done and the Roman
staging (extras_roman.jsonl / files_roman.jsonl / classified_roman.jsonl plus the three
books' per-book lists/triage artifacts) has landed on main, re-run the consolidation:
fold the Roman rows into data/catalog/extras.jsonl, data/commons/files.jsonl and
classified.jsonl; rebuild data/books/index.jsonl and validation.json from ALL books'
per-book artifacts (including the three Roman books) with the existing machinery;
update the Roman row of docs/sources.md section 9; build any new Roman sites (207c's
are mostly new no-QID Scottish forts) and refresh web/data/sites.json and
web/data/plans.json. The page renders the result with no page change (GOAL.md point 5).

If a 207 subtask is dropped before this task runs, edit the Depends on line to the
surviving subtasks and run against the staging that exists (the boxes hold with the
books that landed).

## Acceptance criteria
- [ ] The fit/merge.py re-run: every Roman staging row is in the canonical files; every
      pre-run canonical row is still byte-identical (pure growth); a second run changes
      nothing (idempotent); the run is logged in data/merge/log.jsonl (0 refused, or
      each refusal logged with its reason).
- [ ] data/books/index.jsonl is rebuilt from the per-book files of all books (the
      post-211 set plus the three Roman books); validation.json regenerated; every row
      that reaches the plan list carries the 200 evidence field; fit/evidence.py check
      passes offline on the merged set including the Roman rows.
- [ ] Every new Roman site id has web/data/sites/<id>/; web/data/sites.json grows by
      exactly the new sites and the pre-run entries are unchanged (except the 212-owned
      marker fields); web/data/plans.json: every pre-run (id, sites[0]) key still
      present, (id, sites[0]) still unique, the new Roman picture rows present
      (tools/export_plans.py re-run).
- [ ] docs/sources.md section 9: the Roman lead row records what was staged and what
      was dropped, per book, sourced from docs/lead_roman.md and the merge log
      (replacing the "NONE in this merge" row 211 wrote).
- [ ] The human's reference is untouched: the 25 hand fits and their 19 sites
      (tests/test_serve.py::test_hand_fits_are_the_reference) still pass after the
      re-run; the re-run's tests are hermetic (port 0, temp tree, no network).

## Notes
- Same invariants as 211: row conflicts (a Roman row equal to a canonical row or to a
  row staged by another source) resolve first-wins, recorded in data/merge/log.jsonl -
  never a silent rewrite.
- Building sites is the slow part (DEM fetch, images); it is a working-phase command.
  The test asserts the data-level result (entries, joins, idempotence) on the served
  data, not a full rebuild.
- When this task runs, tests/test_merge.py's frozen pre-merge baseline (the 385
  entries) shifts to the post-211 state (the 499 entries); update the baseline in the
  test for this intended change.

## Hand-over
(2026-10-14, iteration 207, agent a - FIRST session. Investigation done; prep step half
landed. No test was run this session. 207c is DROPPED (owner, ask 008) so this re-run
covers the TWO books that landed (Horsley, Maclauchlan) - the task's Notes say the boxes
hold with the books that landed; the Depends on line already matches (207c was never on
it), no edit needed.)

**State on disk now (uncommitted, in this checkout):**
1. fit/merge.py: `--sources NAME[,NAME...]` flag ADDED (edits landed): a run names the
   source families to merge; log records that run only. WHY: merge.py's glob picks up
   EVERY files_*/extras_*/classified_* file - an unfiltered run would fold in the US
   families' still-pending staging (files_us_cities/us_birdseye.jsonl etc., owned by 236c,
   open) into the canonical files and my log. 236c will need the same flag for its run.
2. data/merge/sites_premerge_baseline.jsonl: RE-BASELINED to the post-211 state - 499
   entries, one full web/data/sites.json entry per line (json.dumps, ensure_ascii=False),
   was the 385 entries from commit 406562b.
3. data/merge/plans_premerge_keys.jsonl: RE-BASELINED - 1510 keys
   {"id": <plan id>, "site": sites[0] or null} from the current web/data/plans.json
   (was 1166 pre-211). Uniqueness verified before writing.
4. tests/test_merge.py: UNTOUCHED (all three edit attempts aborted atomically - one had a
   path typo ENOENT; none applied). The 4 pending edits are specified in the DECISIONS
   entry for this iteration, with the new test's full code there.
5. Do NOT commit docs/site_flow/307d_*.png (4 modified in the working tree: agent c's 240
   files, suite-side-effect churn - PITFALLS "the 307d PNG churn" note). Commit only:
   fit/merge.py, data/merge/, tests/test_merge.py, tasks/230, DECISIONS.md, (PITFALLS.md
   if you file the merge-glob entry). Never `git add -A` in this checkout.

**Investigation findings (all verified on this tree, 2026-10-14):**
- Roman staging IS on main (808's commit 9adaf16 + 207b): data/catalog/extras_roman.jsonl
  9 rows (luguvallium-q71551754 Q71551754 + 8 no-QID: ardoch, virosidum, cilurni, petriana,
  congavata, tunnocelum, kirkintilloch, carriden - NONE in web/data/sites.json yet, all 9
  need building); files_roman 18, classified_roman 18 (17 Horsley + 1 Maclauchlan n0093).
  Per-book lists/triage for both books tracked; docs/lead_roman.md has both sections.
- Post-211 canonical: extras.jsonl 193, files.jsonl 1730 (211's 1623 + 212a's 107 direct
  appends, commit 9c48d94), classified 1037, index.jsonl 1068, validation.json, sites.json
  499 unique, plans.json 1510 rows. data/merge/log.jsonl = 211's snapshot (my scoped run
  will REPLACE it with the Roman-only snapshot by design; 211's is in git history).
- docs/sources.md section 9: the Roman row currently reads "**none in this merge** - the
  task was stopped by the owner..."; box 4 replaces it with what was staged/dropped per
  book, sourced from docs/lead_roman.md + the merge log. The "The merge itself
  (2026-10-12)" summary paragraph records the 211 run; decide in the doc phase whether to
  extend it with the re-run (box only mandates the Roman row).
- Book-index rebuild mechanism (box 2): pipeline/books.py's BOOKS dict does NOT contain
  the Roman books - fit/src_roman_horsley.py / src_roman_maclauchlan.py register() add
  them in-process (into books.BOOKS + books_lists HAND_FIGS/PLATES). index.jsonl is
  written by books_lists.py cmd_index (~line 1093, writer at ~1210); validation.json by
  cmd_validate (line 979, merges into the existing file, key "book"). So the rebuild = a
  small in-process driver: import both roman modules, call each register(), then run
  books_lists.cmd_index(None) and cmd_validate(None) (they iterate (args or BOOKS), which
  now includes the roman keys). Both are offline (no LLM in index/validate - they read
  triage/lists/djvu locally; 207b ran validate_book offline). Afterwards:
  `fit/evidence.py record` (book rows record OFFLINE via the matcher; existing rows stay
  byte-identical) then `fit/evidence.py check` must exit 0 with " 0 fail".
- Matcher risk (box 2): pipeline/books_match.py reads CATALOG = data/catalog/sites.jsonl
  ONLY (not extras.jsonl) - book-index rows for the NEW roman extras sites get no matcher
  tie -> recorded kind "none" (reported, never a failure; every index row still carries
  the rec "evidence/1" field, which is what test_index_and_plan_list_rows_carry_evidence
  asserts). Rows whose names match existing catalog sites (Housesteads etc.) get real ties.
  Do NOT extend the matcher for this task.
- Site build (box 3, the slow part, next-next sessions): data/merge/run_build.py
  `<sid>...` (one process per site; pipeline/build_catalog.py --ids then
  build_site.set_drawings; logs to data/merge/build_sites.log; --force to rebuild a
  half-built site). OPEN QUESTION to resolve first: what DEM/LiDAR source does
  build_catalog.py have for UK sites (read its source table) - precedent: the four no-QID
  Antonine Wall camps (bar-hill-fort, inchtuthil, raedykes, rough-castle-fort) are already
  in extras.jsonl; check their web/data/sites/ dirs (relief.jpg? lidar_credit?) to see
  what a UK site build produces, or whether UK sites end up aerial-only/none.
- tests/test_merge.py already lists "roman" in STAGING and _tree() copies whatever exists
  (its "roman staging appears only once 207 lands" comment is now stale - clean it in the
  same edit pass). The temp-tree merge tests will dry-verify the Roman rows pass the gate
  (log all "merged", rc 0) both before and after the live re-run. The US staging files are
  NOT in STAGING, so the tests are unaffected by them either way.

**Tests last run:** not this session. Stale on record: this checkout's
.agent/reports/last-test-output.txt is from 2026-10-13 (159 passed, 1 failed = agent a's
307bb placement red - since fixed on main by my 212 work). Newest measurements: 238
(180/1/0), 207b (172/1/0), 808 (169/1/0), all 2026-10-14. Next session: run
`tests/test_merge.py` first (all should pass PRE re-run), re-baseline the full-suite
expectation on the final run. ALWAYS `.venv/bin/python -m pytest` (never bare pytest).

**Exact next steps (in order):**
1. Apply the 4 pending tests/test_merge.py edits from the DECISIONS entry (this
   iteration) - exact oldText strings are there; verify current file text with sed before
   applying (I aborted 3 times, so re-read, don't trust memory).
2. `.venv/bin/python -m pytest tests/test_merge.py -v -p no:cacheprovider` -> expect all
   green (proves the 45 roman rows pass the merge gate with 0 refused/0 conflicts in the
   temp tree) + the new --sources test green.
3. Commit the prep (fit/merge.py + data/merge/ baselines + tests + memory files).
4. NEXT SESSION: the live re-run - `fit/merge.py merge --sources roman` in this tree;
   verify: extras 193->202, files 1730->1748, classified 1037->1055, pre-run bytes
   prefix-identical, second run no-op, log.jsonl = the 45-row Roman snapshot (0 refused
   expected); commit. Then the index rebuild (finding above) + record/check; then
   docs/sources.md section 9 Roman row; then the 9 site builds (run_build.py, check the
   UK-DEM question first) + tools/export_plans.py re-run (must be pure growth over the
   new 1510-key baseline); full suite; done claim.
