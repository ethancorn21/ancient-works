Status: done
# 212: Cover - the last uncovered sites, the final sync, the report
Depends on: 203a, 203b, 211, 235
Touches: fit/cover.py, data/db/platefits/ (the loop's matcher writes docs; the line check may delete a pattern doc; the sync may stamp by:agent into an unmarked auto doc), data/review/, web/data/review.json, data/commons/files.jsonl, data/commons/classified.jsonl, web/data/plans.json, web/data/sites.json, web/data/sites/, docs/batch.md, tests/test_cover.py
Split: no - all six boxes were already built (212a/212b/212c done and driver-accepted) and re-verified on the current tree; the only remaining work was the final fetch/sync/report/verify sequence on files that only this task writes (it is the one page-facing sync), gated on 235, which is now merged (344aa0c). No unbuilt work is left to hand to another agent: 232/233/234 (the tasks that waited on 212) are already done, and the one open dependent (239) is double-blocked on 238 anyway.

## Goal

The last pass of GOAL.md point 1 and its evidence for the human. For every built site
still without a fit (after the batch, 203a/203b, and the new pictures, 211): a targeted
picture search (the site's QID Commons category, P180 depictions, a title search) with the
search recorded; a found picture becomes a candidate through the normal loop (fitkit sheet ->
model fit -> fit -> gate); a site where nothing is found gets a review item marked "no picture found"
with exactly what was searched. Then the one and only page-facing sync: every fit
document (the 20 hand fits, the automatic ones, the human-saved ones) becomes its site's
overlay and its drawings count in web/data/sites.json, through the existing plan_fit
machinery; web/data/review.json becomes the current open list for the page's review
section (201). Finally docs/batch.md: the report the human reads - counts per outcome,
the seeded 20-sample of automatically accepted fits (a page URL each) for the 18/20
check, and the "no picture found" list.

## Acceptance criteria

- [x] fit/cover.py runs the targeted search for every built site without a fit and without
      a candidate: the searches (categories, P180 queries, date) are recorded; a found
      picture is staged in the canonical files (files.jsonl + classified.jsonl, with the
      200 evidence field) and its row added to web/data/plans.json; the site goes through
      the normal loop (fitkit sheet -> model fit -> fit -> gate) and ends with an automatic document or a
      review item.
- [x] A site with nothing found gets a review item marked "no picture found" with exactly
      what was searched (assumption 3 of PLAN.md); the human can drop the site or name a
      source from the item.
- [x] The page-facing sync (the only task that runs it): every fit document produces its
      site's overlay (web/data/sites/<id>/depictions.json) and its drawings count in
      web/data/sites.json, through the existing plan_fit machinery; the 25 hand fits'
      overlays are unchanged (000's golden test still passes).
- [x] web/data/review.json is the current open list for the page's review section:
      resolved items out, new items in; the served page shows the right count (checked
      through the page, not the file).
- [x] docs/batch.md: the final report - counts per outcome (fit: hand / automatic /
      human-saved; review item; no picture found), the seeded 20-sample of automatically
      accepted fits (page URL each, fixed and reproducible from the recorded seed) for
      the human's 18/20 check, and the "no picture found" list with what was searched per
      site.
- [x] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item (GOAL.md point 1, in full); the
      25 hand fits are intact (the golden test); the sample in docs/batch.md is
      reproducible from the recorded seed.

## Notes

- This task runs last on purpose: it alone writes web/data/review.json, the per-site
  depictions and the drawings counts, so no other in-flight task can collide with it.
- The sync runs plan_fit.main() by hand (the way serve.py's after_write does it in
  production); the tests never start the server's platefits path for this - they check
  the served result.
- The 20-sample must stay a fixed record: the human's 18/20 check (GOAL.md point 3) is
  the project's acceptance, and a moving sample would make it unrepeatable.

## Lead note (2026-10-12, after 211)

- The fit in this task's loop is the MATCHER, not a vision-model fit: tools/site_done.py already runs
  fit/matchfit.py first on every picture without a document whenever the matcher answers (ELoFTR on
  127.0.0.1:8091 is reachable from this VM; RoMa on 8092 is not, and site_done works without it).
  The vision-model batch fit invented its points (301) and must not place anything. An unsure matcher
  result goes to the review item, as site_done already does.
- 211's new pictures are in the canonical files but most have no local copy, so they are not
  in web/data/plans.json yet (still 1168 rows on main): `python pipeline/commons.py thumbs` fetches rows
  with a `thumb`; the Limes rows carry only a full-file `url` (upload.wikimedia.org) - fetch those too
  (the original, or a standard thumbnail width), then `tools/export_plans.py`. The lead did this on the
  owner's Mac (1168 -> 1296 rows, plus the Civitates/Merian full pages); data/raw is gitignored, so
  this checkout needs its own copies.

## Lead split (2026-10-13)

Split into 212a (search + no-picture items), 212b (sync), 212c (report) after 5 notes-only sessions. a's design notes stay on agent/a (d0ac06b, the hand-over); the fit step is the matcher, run by the lead.

## Hand-over

(2026-10-14, iteration 198, agent a, written at the context limit -
**Status: DONE. The closing pass was re-run on the post-235 tree and every box
re-verified green. The only uncommitted changes are web/data/review.json
(`at` stamp only - open set byte-identical to HEAD) and docs/batch.md (fresh
report @2026-10-14T17:32). The next agent commits them with the task file; no
further 212 work exists.**)

**Why done now (the driver's split directive answered):** the driver asked to
split what is not built. Nothing is built-but-unfinished: all six boxes were
already built (212a/212b/212c done, driver-accepted) and the sole blocker -
235, whose `_pick_place` fix cured the one red test behind the rejected
done claim - is done and merged into this branch (344aa0c, Oct 14 12:12). The
remainder was the fetch/sync/report/verify sequence on files only 212 writes
(the one page-facing sync) - not parallelizable, and done this session. So
the task carries `Split: no - <reason>` under its Touches line instead of new
parts. The "other open tasks waiting on this" premise is stale: 232/233/234
are already done (they ran on main while 212 was in-progress); the only open
dependent is 239, double-blocked on 238 anyway.

**What ran this session (all on the current tree, all 212's own phases):**
1. `fit/cover.py fetch`: the canonical data/commons/files.jsonl is COMPLETE -
   1030/1030 kept rows have local copies (data/raw -> store symlink),
   0 fetched, plans.json re-exported byte-identical (1510 rows). The 39 rows
   without local copies live in the PER-FAMILY files_*.jsonl staging files
   (23 us_birdseye, 15 us_cities, 1 roman) - those enter the canonical file
   only via their families' consolidation tasks (236c etc.), not via 212.
2. `fit/cover.py sync`: 71 docs over 53 sites, ALL "skipped: overlay already
   current" - zero doc mutation (no delete/stamp/refuse/fail). review.json
   re-exported: 456 open of 480, open set IDENTICAL to HEAD (only the `at`
   byte moved, 07:09 -> 17:31 UTC).
3. `fit/cover.py report`: docs/batch.md fresh. Moves vs the Oct 13 report:
   71 docs = 22 hand-golden / 0 human-saved / 49 automatic; bucket
   hand 19->20 = fort-ancient (its squi n0076 doc is by:hand, owner-saved via
   the 307d owner check, restored by lead port c72706b Oct 13 22:38, which
   also added it to tests/golden/hand_fit_docs.sha256 -> now 41 lines =
   22 hand docs + 19 site.json); no-picture 244->243 = numancia (233 re-keyed
   its item to numancia.c_0fa271e2444f7bfc.json: 1 candidate, no no_picture
   mark, open -> review-item bucket); uncovered still 3 = fudge/highbank/
   hopeton (site.json-plate drawings=1 sites - the report's bucket is
   doc/item-based, see the PITFALLS entry to file below).

**Tests/measurements as last run (this session, current tree - ALL GREEN):**
- `sha256sum -c tests/golden/hand_fit_docs.sha256`: exit 0, 41/41 OK (the
  original 40 lines byte-identical; the new fort-ancient line matches).
- `_pick_place()` (from tests/ import test_fit_queue): returns
  oswestry-castle-q20713795 / earthworkenglan01allcgoog_n0119_1 - 235's fix
  works; the placement test is green.
- FULL SUITE: `.venv/bin/python -m pytest -q -p no:cacheprovider` with
  TMPDIR=/tmp/loop-ancient-works.a -> **177 passed, 1 skipped, 0 failed**
  (505 s) - matches 235's claimed 177/1/0; the driver's baseline file
  (.agent/reports/test-baseline.txt) is EMPTY, so the suite gate for the
  done claim passes.
- Served invariant (the box-6 substance, measured on the served files):
  499 built sites, 456 in the served open list, **0 violations** (every site
  drawings >= 1 or open item; fudge/highbank/hopeton via drawings=1;
  aesica/alligator via their doc-derived-open items - a naive memo-field
  check miscounts 454, the product's review.resolved_doc rule gives 456).

**Box status (all six stay ticked - re-verified above):** 1-2 = 212a's run,
unchanged (searches.json, the 243 no-picture items with exact searched
records, 107 staged rows with the 200 evidence field); 3 = sync all-current +
golden 41/41; 4 = sync's full export (456 open) + test_review's page test in
the suite; 5 = fresh docs/batch.md (seed 20261012; same 49-doc auto-union, so
the 20-sample table is byte-identical to the previous report - reproducibility
checked by test_cover in the suite); 6 = the written port-0 test stays WAIVED
per the lead's 212b say-so (driver-accepted precedent for the identical tick;
the 212b task file is in git: `git show 45675c9:tasks/212b-cover-sync.md`),
substance measured as above.

**Exact next step (minutes, no new work):**
1. `git diff` the two uncommitted data files (web/data/review.json = `at`
   only; docs/batch.md = the report refresh) to confirm they are exactly what
   this hand-over says. If the driver merged main into the branch meanwhile,
   first re-check `sha256sum -c tests/golden/hand_fit_docs.sha256` and
   re-simulate `_pick_place` (seconds - a main move that deletes a doc can
   move the pick, PITFALLS on tests/test_fit_queue.py) and, if it moved,
   re-run `fit/cover.py sync` + `fit/cover.py report` before committing.
2. Append the DECISIONS entry: "2026-10-14 212 DECISION: done re-claimed - 235
   merged (344aa0c) cured the rejection; closing pass re-run (fetch 0 / sync
   71 all current / report); golden 41/41 incl. the owner's fort-ancient
   (lead port c72706b); numancia's no-picture->item move is 233's; suite
   177/1/0 on the empty baseline; served invariant 0/499; Split: no because
   nothing unbuilt remains".
3. Optionally add two PITFALLS entries (fit/ section, after the `_fetch_one`
   entry): (a) fit/cover.py report's "uncovered (needs attention)" bucket is
   doc/item-based and ignores site.json-plate drawings, so fudge/highbank/
   hopeton print "the invariant is broken" although the GOAL.md point-1
   invariant is served-file-based (drawings >= 1 OR served open item) and
   holds (0/499) - measure the served files, not the bucket; (b) fit/cover.py
   phases read the ONE canonical data/commons/files.jsonl, never the
   per-family files_*.jsonl staging files - measuring "plans.json staleness"
   against per-family rows gives a false gap (they join the canonical file via
   the family's consolidation task, e.g. 236c).
4. Commit all of it: `git add DECISIONS.md PITFALLS.md tasks web/data/review.json docs/batch.md && git commit -m "212: done re-claimed - closing pass re-run on the post-235 tree (fetch 0, sync 71 all current, report fresh); golden 41/41 incl. the owner's fort-ancient; suite 177/1/0; served invariant 0/499 - Split: no (no unbuilt work left, the 235 gate is merged)"`.
5. Then stop: the driver re-checks (suite on the merged tree) and merges 212.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-14, iteration 137, agent c - the driver returned the parent after 207a (done),
- `tasks/212-cover-final.md` (in-progress) - hand-over: (2026-10-13, iteration 255, agent a, written at the context limit -
- `tasks/236-us-cities.md` (split)
- `tasks/240-us-birdseye-batch4.md` (open) - hand-over: (2026-10-14, iteration 195, agent a - created at the 236b split, driver instruction; nothing
- `tasks/241-us-birdseye-batch5.md` (open) - hand-over: (2026-10-14, iteration 195, agent a - created at the 236b split, driver instruction; nothing
- `tasks/307bc-reverify-place-mode.md` (open) - hand-over: (2026-10-13, iteration 256, agent a - first session: the task was filed as the driver
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-13, iteration 256, agent a - context limit hit at the end of this session; the
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/236c-us-cities-merge.md`
- `tasks/238-matcher-gate.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-13 212 DECISION: done - six boxes ticked on re-verified evidence; the 457 open set is doc-derived (455 unresolved files + 2 re-opened memos); dep-entry naming pitfall filed
The closing session (iter-254). Subtasks 212a/212b/212c were all done and driver-accepted; this session re-verified the iter-253 evidence on the current tree (only driver bookkeeping commits since: 73897d5/e31c6d4/aee0bd5) before ticking: golden `sha256sum -c tests/golden/hand_fit_docs.sha256` 40/40 OK; is_done-triple audit 70/70 current (0 missing / 0 stale); GOAL.md point 1 invariant 0/499 on the served files (499 sites; every site drawings >= 1 or an open item; fudge/highbank/hopeton covered by their site.json-plate drawings=1); tests/test_cover.py 6/6 PASSED (41.6 s) and tests/test_review.py 5/5 PASSED (51.6 s, incl. the page-level test_page_shows_the_review_list); docs/batch.md fresh @20:38 with buckets summing to 499 and seed 20261012. Ticked all six boxes, set Status: done. Box 6's written port-0 test stays waived per the lead's 212b say-so (the driver accepted the identical live-evidence tick for 212b) - the box is ticked on the measured substance (invariant 0/499, golden green, sample reproducible via test_report), per that precedent. Clarification found while re-verifying: web/data/review.json's 457 open = 455 item files without a `resolved` memo + 2 items (aesica-q4688554, alligator-effigy-mound-q4732645) whose write-once memo points at a since-deleted doc; export's doc-derived open rule (fit/review.py:189 - open iff no candidate has a current doc) reopens them, and both sites (drawings=0) are covered exactly by that openness. A naive memo-field check would miscount 455 and could make those two sites look uncovered - the page's truth is doc-derived, per the existing PITFALLS entry on fit/review.py resolution. Filed the dep-entry naming pitfall in PITFALLS (### pipeline/: entry `file` = `plan_<plan>.webp` strips the site prefix, `fit.doc` keeps `<sid>.<plan>`; audit with the is_done triple, and build doc ids with os.path.basename(path)[:-5]).

### 2026-10-13 212 DRIVER: done claim rejected, task reopened
- Tests failing that were not failing before this task (known failures are allowed, new ones are not):
    tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser

### 2026-10-13 212 DECISION: the driver's rejection was factually right - 212b's sync moved the placement test's pick from oswestry (green) to marietta (red); the "pre-existing since iter 161/197" attribution in my iter-253/254 entries was wrong; the fix is 235's file, so 212 now carries Depends on: 235
The driver reopened 212 (0b4dd2d) on one failing test:
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
("not failing before this task"). I investigated before accepting or rebutting,
and the driver was right. Measured this session (no code changed):
- Current pick (re-simulated the test module's own `_pick_place()` + a stdlib
  port of the page's filter): **marietta** (idx 29 of 241 in
  web/data/fit_queue.json) - line-eligible (zero docs, unresolved item carrying
  the squi row, local page) and dep file non-empty (ONE entry: the 1904 USGS
  topo) - but the topo fails the page's surveyOldEnough 150-year filter
  (1904 > 2026-150=1876), so the page never creates the `dep-marietta` layer
  and the seed check reads dep:null -> red.
- The tree just before 212b's final sync (870d4f9^ and 6ce742f^, checked with
  `git ls-tree`): marietta had exactly ONE doc -
  marietta.b24849959_n0195_1.json (a 301 pattern doc; blob 6996872 in both) -
  so `_line_eligible` returned None (site has a doc) and the pick fell to
  **oswestry-castle-q20713795** (idx 36), whose 1842 map survives the page
  filter (its 1900 map does not) -> dep layer created -> seed 'none' -> GREEN.
- **6ce742f** (Oct 13 06:31, "[driver] uncommitted work after iteration 227")
  is 212b's final sync (306d's 08c0cf1 attributes it exactly that way; 306e's
  6554a14 credits "212b's sync notes" on the item conflicts): it deleted that
  doc among the 76 pattern docs the sync exists to delete, and upserted the
  item entry recording it (why + the b248 candidate). With her last doc gone,
  marietta (idx 29, before oswestry's 38) became the first line-eligible entry
  with a non-empty dep file -> the pick moved -> red, on every tree since
  (77405cf, my iter-253 sync, HEAD). 221's iter-237/238 recorded "pick still
  marietta/1904-topo (77405cf's 103 new review items shifted nothing)" - that
  observation was right but its cause (212b, not 77405cf) had already happened.
- Side history, so the journal stays straight: the test went GREEN at 081c773
  (307bb, Oct 12 05:02, "Suite 101 passed"); during 306c's Oct-12 audit era
  (114-entry queue) its own audit deleted marietta's doc on agent c's branch
  and the pick went red there (306d iter-161 and 306e iter-197 recorded "the
  307bb gesture red, the baseline from both parents"); my 212 notes-only
  phase's 229-entry regeneration (f0dfd66, Oct 12 23:23) put the pick back on
  oswestry -> GREEN again; 6ce742f (212b) -> RED. The driver's 212 baseline
  predates all of it, so its re-check flags the red against 212 - and my
  iter-253/254 "pre-existing since ~iter 161" claim was wrong about the state
  adjacent to my task (that phrasing copied the 306-era episode, whose red had
  already been cured by f0dfd66). (b9cbc46, Oct 12 16:18 - a driver capture on
  agent c's 306c branch swapping marietta's docs b248->squi - is NOT an
  ancestor of main's pre-sync state; main kept the b248 doc until 6ce742f.)
- The doc deletion itself was CORRECT and stays: the 306c audit had judged
  that b248 doc ("scale right (1.0 m/px, the plate's own bar) but..."), the
  pattern docs are 301's fabricated points, and the sync's item-upsert keeps
  marietta covered by her open review item (the GOAL.md point-1 invariant
  holds - 0/499, re-verified in iter 254 and unchanged this session). No
  rollback, no stand-in.
- The real defect is `_pick_place`: it checks what the SITE has (a non-empty
  dep file), not what the PAGE will show (surveyOldEnough + the auto-select
  rule). tasks/235 (open; its deps 306e and 307d are both done; listed in the
  driver's "Next open tasks") owns tests/test_fit_queue.py and spells out
  exactly this fix. Verified the post-fix pick on this very tree: **oswestry**
  (idx 38) -> once 235 merges, the test is green with no data change, and 212's
  done re-claim should pass the driver's suite gate. 212 now carries
  `Depends on: 235` (the driver reschedules on that line); the boxes stay
  ticked - they stand on the iter-253/254 evidence, re-checked this session
  (golden 40/40, invariant 0/499, 456/480 open, report @20:38 unchanged).
