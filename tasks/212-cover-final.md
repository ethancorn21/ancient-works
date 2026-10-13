Status: split
# 212: Cover - the last uncovered sites, the final sync, the report
Depends on: 203a, 203b, 211
Touches: fit/cover.py, data/db/platefits/ (the loop's matcher writes docs; the line check may delete a pattern doc; the sync may stamp by:agent into an unmarked auto doc), data/review/, web/data/review.json, data/commons/files.jsonl, data/commons/classified.jsonl, web/data/plans.json, web/data/sites.json, web/data/sites/, docs/batch.md, tests/test_cover.py

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

- [ ] fit/cover.py runs the targeted search for every built site without a fit and without
      a candidate: the searches (categories, P180 queries, date) are recorded; a found
      picture is staged in the canonical files (files.jsonl + classified.jsonl, with the
      200 evidence field) and its row added to web/data/plans.json; the site goes through
      the normal loop (fitkit sheet -> model fit -> fit -> gate) and ends with an automatic document or a
      review item.
- [ ] A site with nothing found gets a review item marked "no picture found" with exactly
      what was searched (assumption 3 of PLAN.md); the human can drop the site or name a
      source from the item.
- [ ] The page-facing sync (the only task that runs it): every fit document produces its
      site's overlay (web/data/sites/<id>/depictions.json) and its drawings count in
      web/data/sites.json, through the existing plan_fit machinery; the 25 hand fits'
      overlays are unchanged (000's golden test still passes).
- [ ] web/data/review.json is the current open list for the page's review section:
      resolved items out, new items in; the served page shows the right count (checked
      through the page, not the file).
- [ ] docs/batch.md: the final report - counts per outcome (fit: hand / automatic /
      human-saved; review item; no picture found), the seeded 20-sample of automatically
      accepted fits (page URL each, fixed and reproducible from the recorded seed) for
      the human's 18/20 check, and the "no picture found" list with what was searched per
      site.
- [ ] Test (no network, port 0): after the sync, every built site in the served
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
- 211's new pictures are in the canonical files but most have no local copy, so they are not in
  web/data/plans.json yet (still 1168 rows on main): `python pipeline/commons.py thumbs` fetches rows
  with a `thumb`; the Limes rows carry only a full-file `url` (upload.wikimedia.org) - fetch those too
  (the original, or a standard thumbnail width), then `tools/export_plans.py`. The lead did this on the
  owner's Mac (1168 -> 1296 rows, plus the Civitates/Merian full pages); data/raw is gitignored, so
  this checkout needs its own copies.

## Lead split (2026-10-13)

Split into 212a (search + no-picture items), 212b (sync), 212c (report) after 5 notes-only sessions. a's design notes stay on agent/a (d0ac06b, the hand-over); the fit step is the matcher, run by the lead.

## Hand-over

(2026-10-13, iteration 233, agent a - **212a done, 212b done, 212c next.**
This replaces the iter-211 investigation note (the file's previous version is in
git: `git show 4b12889:tasks/212-cover-final.md`; the design it cited: the
iter-205 settled design in `git show 953d9ab:tasks/212-cover-final.md`, the
iter-209 note in `git show d31aaec:tasks/212-cover-final.md`).

- **212a (search + no-picture items): done.** The live fetch/search/stage ran
  on the store (211's pictures + the Civitates/Merian full pages staged into
  the canonical files; the lead re-exported plans.json with every local copy at
  aeeb5aa - 1510 rows). The 234 search-set sites carry re-recorded no-picture
  items; the exact searched string per site is in data/cover/searches.json.
  tests/test_cover.py = 212a's 770-line version (search + no-picture), green.
- **212b (the page-facing sync): done (the lead's decision, this session).**
  The live sync ran and was verified (iter-227/228: run1 an exact dry-run
  match, 76 sent / 25 skipped / 30 synced; run2 the 2 lead burcht docs the
  06:07 merge added mid-run; 365 open / 377; golden 40/40; store clean; the
  one pattern doc deleted by the line check; post-sync suite classified -
  only 307bb's pre-existing reds). Box 3 (the no-network port-0 test) was
  ticked on that evidence per the lead's "no more re-measuring"; the written
  test was not produced - its full design is preserved in `git show
  45675c9:tasks/212b-cover-sync.md` and `git show
  1cd9671:tasks/212b-cover-sync.md`.
- **212c (the report): open, next** (its own file has the two boxes). The
  `report` phase already exists in fit/cover.py (212a wrote it):
  `python3 fit/cover.py report` writes docs/batch.md from the store with the
  seed recorded (SEED_212 = 20261012): per-built-site buckets (fit:
  hand-golden / human-saved / automatic; review item; no picture found;
  uncovered-needs-attention), the 20-sample of the automatic-fit union
  (random.Random(20261012) over the sorted doc ids; page URL + gate median
  per row) for the owner's 18/20 check, and the no-picture table (each
  site's exact searched string; fallback data/cover/searches.json).
  docs/batch.md does not exist yet. The test goes into tests/test_cover.py:
  the sample reproducible from the seed recorded in the file, and the bucket
  counts adding up to the built-site total. Two honest-state notes for the
  report: (1) the live run never did the loop phase, so the 103 no-item nofit
  sites bucket as "uncovered (needs attention)" and the invariant line prints
  "the invariant is broken" - correct against the store as-is; (2) the
  20-sample is a fixed record drawn over the 36 matcher docs (the whole
  automatic union) - keep it stable, the owner's 18/20 check must be
  repeatable. State as of 0e6d5df (re-measure in the 212c session if a merge
  moved the world): 499 built; 57 docs (21 hand, 36 by:agent matcher, 0
  unmarked, all is_done); 377 item files / 365 open; plans 1510 rows;
  web/data/review.json = 365 items at 2026-10-13T11:26:15.291892+00:00.)
