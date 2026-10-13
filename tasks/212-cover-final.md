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

(2026-10-13, iteration 252, agent a - **closing 212: the world moved after the
last sync and the last report; the one step left is the final sync + report +
tests + tick.** This replaces the iter-234 hand-over, which is preserved in
git: `git show 9c8a46a:tasks/212-cover-final.md` (and earlier versions at
4b12889/953d9ab/d31aaec as before).

**What changed since 212c's report (13:22 UTC) - all in ONE lead commit,
`77405cf` (14:34 UTC, author "Claude", on main, merged into this branch):
"[lead] port: 13 matcher re-fits on 11 sites after the 212b sync (eye-checked);
review items for the 103 uncovered sites in 212c's report; test_batch_us allows a
resolving doc beside its item entry". It touched: 13 NEW by:agent docs in
data/db/platefits (all `fitter: "matcher"`, 8 pairs, model similarity, src
commons; get the exact names with `git show 77405cf --name-only --
data/db/platefits`: bolsover-castle, bury-castle, cahokia, coria, daw-s-castle,
framlingham, goodrich, gouda, ludlow, old-sarum x2, portus-adurni x2); 103 NEW
item files in data/review (the 377 -> 480 jump; they are the 103 uncovered
sites of 212c's report, mostly Civitates/Merian/Limes book sites - venice,
wiesbaden, walheim, welzheim, wurzburg, zugmantel, stockstadt, weienburg, ...);
web/data/review.json re-exported at 14:34:07; web/data/sites.json (score/
oldest/overlays hand-edited for the re-fit sites, e.g. score 0.91/oldest 1850/
overlays 1 with drawings 0); web/data/fit_queue.json; tests/test_batch_us.py.
It touched ZERO depictions.json files - the port came from the lead's Mac
without the overlay webps.)

**Verified this session (measured, not assumed):**
- Store and my checkout AGREE on all 557 tracked data files (0 differing);
  working tree clean; `.venv/bin/python` has numpy/scipy/PIL ok.
- Exact dep audit (entry name must be `plan_<doc["plan"]>.webp`): of 70 docs
  (21 hand + 49 by:agent), EXACTLY the 13 new docs lack a current dep entry;
  the other 57 all have one; 0 stale entries (no doc-less plan entries to
  prune). NOTE: a naive substring check on the source file name is wrong -
  book docs' entries are `plan_<ia>_nXXXX_Y.webp` and c_ docs' are
  `plan_c_<sha16>.webp`; match on the full `doc["plan"]`.
- The 10 of 13 with missing `data/raw/commons/big/<plan>.jpg` cache
  (cahokia, coria, daw-s-castle, framlingham, goodrich, gouda, ludlow,
  old-sarum c_b2701b5231da42f2, portus-adurni x2) will be DOWNLOADED from
  Commons by `plan_fit.load_picture` during the sync (paced, 429-retried;
  the 212b live sync did the same fine from this VM). The other 3 have cache.
- The 13 new docs' 11 sites: check each dir under web/data/sites is a
  symlink to the store (old-sarum confirmed LINK; the 13-book-doc sites I
  did check were a different, already-synced set) so the built webps land
  in the store (the publish source).
- fit/cover.py's `sync` phase (line 615) is the final sync: per doc
  `site_done._sync_doc` (hand: build no check; agent: matcher docs get
  matchfit.spread check, others fabrication_pattern; pattern -> item + doc
  deleted; unmarked -> stamp/refuse; is_done -> skip), then plan_fit.prune,
  then review.export (review.json = current open list). It is safe to run on
  my checkout: the only writes are the 13 not-done builds (+ any prune) and
  the export; the other 57 docs are is_done and skip without touching images.
  In-flight risk assessed low: agent c's open 302f/302g/207a work touches
  different files (302g stonehenge; 207 blocked); 230/235 open but
  unassigned.

**Exact next step (one session, in this order):**
1. `.venv/bin/python fit/cover.py sync` on this checkout. Expect 13 lines
   "synced to the map" (or fewer if a spread check sends one to review -
   report any "sent"/"failed"/"refused" to DECISIONS and do NOT re-fit),
   57 "skipped: overlay already current", then prune (expect nothing), then
   "sync: 480 open of N item(s) -> web/data/review.json" (open count will
   move: the sweep writes resolution records - e.g. a new doc resolving a
   candidate in an open item - and the 103 new items are mostly open).
   Inspect the diff afterwards (git status --short; git diff --stat): expect
   web/data/sites/<the 11 sites>/depictions.json + webps (in the store via
   symlink), web/data/sites.json (set_drawings refresh: drawings/oldest/
   overlays/score re-derived by the machinery, overwriting the lead's
   hand-tuned fields - that is the point of "through the existing plan_fit
   machinery"), web/data/review.json, and item-file resolution stamps in
   data/review/.
2. `.venv/bin/python fit/cover.py report` -> fresh docs/batch.md (the lead's
   own 212c note says re-run if the store moved; it did). Expect: 499 built;
   automatic bucket up (24 -> ~34 sites; by:agent docs 49), uncovered bucket
   down (106 -> ~3: the 103 got items, some of the 13 re-fits add drawings),
   sample re-drawn random.Random(20261012) over the 49 sorted by:agent ids
   (the 20-sample changes ONLY because the automatic population changed -
   the seed is fixed; this is the final record for the owner's 18/20 check).
3. Run the tests: `.venv/bin/python -m pytest tests/test_cover.py -v` (6
   tests: search_records/counts/stage/nopicture/checkout_integrity/report -
   the report one runs the report phase on the hard-link tree; it was green
   at iter-234 and the tree now carries docs/batch.md via the IN_PLACE
   copy path). Then the golden: find it (`grep -rn hand_fit_docs.sha256 tests/`;
   it was "golden 40/40" in 212b and "golden hand_fit green" in 307d) and run
   it - the 21 hand fits' overlays must be byte-identical (the 13 new docs
   must not have touched any hand site). Also run tests/test_serve.py (the
   served-page checks incl. the review count) and the full suite if time
   allows (baseline at iter-234: 155 passed / 1 red = 307bb's pre-existing
   gesture test, later fixed by 307d - expect all green now).
4. MEASURE the invariant on the final served files (the box-6 claim, the way
   212b's was ticked on live evidence): every site in web/data/sites.json
   has drawings >= 1 or an open review item (open = the item file's
   review.resolved_doc is None). With the 103 new items + the re-fit
   drawings it should now hold (or nearly: list any stragglers in
   DECISIONS).
5. Tick the parent boxes with that evidence: 1 (search+stage+loop: 212a live
   run + 212a's 5 tests + the 13 re-fits went through the matcher line in
   this sync), 2 (234 re-recorded no-picture items, searches.json, test
   nopicture), 3 (final sync done by this task per its note "the only task
   that runs it"; hand fits' overlays byte-identical = golden), 4 (review.json re-exported by the sync;
   page count via test_serve), 5 (fresh
   docs/batch.md from the final world), 6 (invariant measured on the served
   files post-sync - the 212b box-3 precedent, driver-accepted; golden
   green; test_report green. The written port-0 test remains waived by the
   lead - design preserved in git show 45675c9/1cd9671:tasks/212b-cover-sync.md;
   do NOT re-open it as a subtask: the lead closed 212b on that say-so, and
   if the driver rejects the tick on that ground, the DECISIONS trail shows
   the precedent). Set Status: done.
6. If the sync's line check deletes any of the 13 (a pattern fires) or the
   invariant still has stragglers after the 103 items: do NOT force them -
   log it, add a `## Proposed changes` note to this task file only if a box
   cannot honestly be ticked, and leave the box unticked with a 212d subtask
   instead. (Not expected: the lead eye-checked the 13.)

PITFALLS candidate for next session: dep-entry name = "plan_" + doc["plan"]
+ ".webp" exactly (is_done matches fit.at + fit.doc; a substring search on
the source file name false-flags book docs with the _N suffix).
