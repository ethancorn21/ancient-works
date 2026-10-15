Status: in-progress
# 230: The Roman staging into the canonical data - the 211 consolidation re-run
Depends on: 211, 207a, 207b, 807, 808, 242
Touches: fit/merge.py, pipeline/commons.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/books/matches.jsonl, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py, tests/test_matchfit_station.py, tests/fixtures/matchfit_station/, PITFALLS.md

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
- [x] The fit/merge.py re-run: every Roman staging row is in the canonical files; every
      pre-run canonical row is still byte-identical (pure growth); a second run changes
      nothing (idempotent); the run is logged in data/merge/log.jsonl (0 refused, or
      each refusal logged with its reason).
- [x] data/books/index.jsonl is rebuilt from the per-book files of all books (the
      post-211 set plus the three Roman books); validation.json regenerated; every row
      that reaches the plan list carries the 200 evidence field; fit/evidence.py check
      passes offline on the merged set including the Roman rows.
- [x] Every new Roman site id has web/data/sites/<id>/; web/data/sites.json grows by
      exactly the new sites and the pre-run entries are unchanged (except the 212-owned
      marker fields); web/data/plans.json: every pre-run (id, sites[0]) key still
      present, (id, sites[0]) still unique, the new Roman picture rows present
      (tools/export_plans.py re-run).
- [x] docs/sources.md section 9: the Roman lead row records what was staged and what
      was dropped, per book, sourced from docs/lead_roman.md and the merge log
      (replacing the "NONE in this merge" row 211 wrote).
- [x] The human's reference is untouched: the 25 hand fits and their 19 sites
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

(2026-10-15, iteration 236, agent a - I hold the WHOLE CYCLE (230/242/810/811/812/813/814,
driver 236: inter-deps count as met; build them together on this branch so the tests pass
with all of it in place). STATE: all four reds of the a423d19 done-claim rejection are
GREEN on this branch now; the ONE remaining gate for the done-claim is a full-suite run.

**This session (it.236):**
1. Merged main: CLEAN (the driver's warned 814 conflict did not occur - my 693b0ea3 and
   main's 8694e910 carried identical 814 content; the merge only added tasks/816).
2. Restored docs/site_flow/307d_B_4-saved.png + B_5-reload.png to main's bytes
   (committed e484aa07) - they were re-encoded dirt from the it.216 failed pair run; all
   ten 307d PNGs now match main (merge-clean, b14918f precedent).
3. Verified tests/test_owner_check.py on this branch is EXACTLY the 816 recipe (54 added
   / 0 changed vs main; the settle + subpixel fix; zero instrumentation residue). The
   driver's 693b0ea3 REPLACED my it.235 810-session build (139-line settle/double-shot/
   refresh-flag, in git at 3579c22b) with agent c's tested 54-line fix - see 810/812/813
   hand-overs: the 812 double-shot + 813 refresh-flag still need REBUILDING on top of the
   816 recipe (their designs survive in the 3579c22b file + their hand-overs).
4. Pair run 1 (unflagged, retention=all): A GREEN (the it.214-216 ratio flake is GONE -
   the 816 fix works), B RED at a NEW step: "line effect (b): the site's square takes its
   new score's tier" (markerClass "marker t1" vs tier "t2"; score 1.45 post / 1.1 pre;
   reload read the correct t2; the probe's 120 s poll never saw a change). ROOT CAUSE
   (measured): the one-site line (server/serve.py _fit_worker -> tools/site_done.py) writes
   depictions.json 01:57:23.310 and re-scores sites.json :23.429 (119 ms later - the
   order is mandatory, the score is computed from the built overlays); web/index.html
   saveFit() polls depictions.json every 1.5 s and, when the depiction appears, fetches
   sites.json ONCE and adopts the tier from that fetch - a poll in the gap adopts the
   stale score and the marker keeps its old tier until reload (a real owner-visible
   defect, not a test flake; no test-side wait can fix a one-shot adoption).
5. Filed tasks/245-owner-check-stale-tier.md (Depends on: 815, Touches: web/index.html) and
   BUILT the fix on this branch (committed ab57da1b): saveFit's one-shot fetch is now a
   bounded re-fetch loop (8 x 250 ms) that adopts the fields each time and breaks when the
   fetched entry's `overlays` exceeds the pre-save in-memory value (new depiction = +1
   overlay); missing `overlays` on either side keeps today's single-fetch behaviour; the
   marker-class line and everything else in the function unchanged; all six script blocks
   pass `node --check`.
6. Verification: pair runs 2 and 3 (after the fix): 2 passed each (64.5/65.9/66.7 s),
   "new score's tier" [ok] for A and B in EVERY run, zero [warn] settle; cross-run
   (run2 vs run3, PIL compare, threshold 32 per channel): ALL TEN views 0.000% differing
   - better than 814's 194 evidence (B_5 0.0073%, rest <=0.0447%); this is also 810's box-1
   (cross-run) evidence in hand, and 816's boxes 2-3 evidence. The 307d PNGs were restored
   to committed bytes after every run (9 of 10 re-encode; B_1-card always identical).
7. test_matchfit_station 2/2 green (55.9 s, hermetic) - the it.216 re-record still stands.

**NEXT SESSION (exact steps):**
1. Memory housekeeping this session was cut before: (a) add the PITFALLS entry for the tier
   race under the `### web/` section (fact: "saveFit's one-shot sites.json fetch could land
   in the depiction->re-score gap (~119 ms) and adopt the pre-rescore tier; 245 re-fetches
   until overlays exceeds the pre-save value; the pipeline order is mandatory, never
   reorder; a probe-side longer poll cannot fix a one-shot adoption" - full evidence is in
   the it.236 DECISIONS entry); (b) 245's Hand-over still says "pending" - update it with
   the run evidence (3 green runs, the cross-run 0.000% numbers); (c) if any of the 810/812/
   813/814 hand-over updates below were not committed, finish them.
2. THE GATE: one full-suite run: `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`
   (~8-10 min; TMPDIR=/tmp/loop-ancient-works.a). After its owner_check run, restore the
   re-rendered 307d PNGs to the committed bytes (git restore docs/site_flow/) - 813's
   refresh flag is not in the branch file yet, so unflagged runs still re-copy all ten;
   NEVER git add -A over them. Last known-green baseline ~180 passed / 1 skipped / 0
   failed (2026-10-14, per the archive).
3. If ALL green: re-claim 230 done (the five boxes were ticked it.215; data-level numbers
   stand: merge idempotent +0/+0/+0, evidence 1456 pass / 0 fail, sites 508, plans 1572
   sha256 dee768f2db7c..., test_merge 10/10, test_data 3/3, hand-fits 1/1). If a red
   appears: owner_check at the tier check = a 245 defect (point at 245's file with the
   probe's [eval] effects block - markerClass vs tier vs score); owner_check at the OLD
   ratio step = 816 defect (point at 814/816); roman tests red = 230's own data lane -
   re-verify against the it.215 numbers; anything else = cross-lane, log it in DECISIONS,
   do NOT absorb another lane's fix, and do not claim.
4. After 230 merges (or whenever the driver returns them), the next builds on this branch
   are the 812/813 rebuild (double-shot assert + AW_OWNER_REFRESH regime) on top of the
   816 recipe - the it.235 build survives verbatim at `git show 3579c22b:tests/test_owner_check.py`
   (rebase its parts onto the current file, keeping c's settle/subpixel), then 811
   (one-time refresh + pinned PNGs + docs note + PITFALLS rewrite), then the 810/242
   verification passes. See those files' hand-overs.

**Standing discipline:** the pair always runs in ONE invocation (A then B - B cannot run
alone); after ANY owner_check run, restore the ten docs/site_flow/307d_*.png to committed
bytes before committing (R5); the probe logs of a green run die with the session - read
them from `$TMPDIR/pytest-of-agent/pytest-<N>/owner{A,B}0/owner_probe.log` with retention
(`-o tmp_path_retention_policy=all`; NOTE: `--tmp-retention-policy` is NOT a valid pytest
CLI flag in 9.1.1, use the `-o` override; retention_count=1 in pytest.ini keeps only the
latest run - copy a run's PNGs out before the next one if you need a cross-run compare).

**Hand-over updates written this session (my cycle's files):** 810 (the it.235 build was
replaced by 693b0ea3; rebuild 812+813, then verify), 812 + 813 (build replaced; designs
survive in 3579c22b + their hand-overs; rebuild pending), 814 (PNG-restore first action
done on this branch; the file is now the 816 recipe itself; re-claim after 816+230 merge
is a re-verification formality - the pair is green here, 3 runs).
