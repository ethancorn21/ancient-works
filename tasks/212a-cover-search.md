Status: open
# 212a: Cover search - a targeted picture search for every uncovered site, "no picture found" items
Depends on: 211, 203b
Touches: fit/cover.py, data/review/, data/commons/files.jsonl, data/commons/classified.jsonl, data/raw/commons/, web/data/plans.json, tests/test_cover.py

## Goal
For every built site with no fit document and no plan candidate in web/data/plans.json:
one targeted search (the site's QID Commons category, P180 depicts, a title search),
recorded. A found picture is staged the normal way (files.jsonl + classified.jsonl with
the 200 evidence field, a local copy under data/raw/commons/, its row in plans.json via
tools/export_plans.py). A site where nothing is found gets a review item marked
"no picture found" with exactly what was searched. The fit itself is NOT this task: the
lead runs fit/matchfit.py + tools/site_done.py over the found pictures afterwards (lead
note ef84a05 - the matcher is the fit, never the vision-model fit).

## Acceptance criteria
- [x] fit/cover.py search: lists the uncovered sites (no platefit doc, no plans.json row),
      searches each, writes found pictures into the canonical files and a local copy,
      re-exports plans.json; prints counts (searched / found / nothing).
- [x] fit/cover.py nothing-found: a review item per site, marked "no picture found",
      listing the queries and the date.
- [x] tests/test_cover.py (no network: a recorded fake search response, sockets dead):
      one site with a hit gets staged rows + a plans row; one site without gets the
      review item with its queries.
- [ ] Run it for real once and commit the results.

## Notes
- Commit working code every session. Notes-only sessions end the job (212 ended that way).

## Hand-over

(2026-10-13, iteration 220, agent a - boxes 1-3 stay DONE and verified
(re-ran tests/test_cover.py today: 5 passed, 33.9 s - still green after the
store grew ~328 files). Box 4 (the live run) still waits on 203b, but THIS
session CORRECTED the reason for the wait and re-measured everything the run
depends on. No code changes.

**WHY THE WAIT (corrected understanding - replaces the iter-219 one):**
203b's file has been Status: done on main since c49aeb9 (2026-10-11, agent c
iter 50 - the 294-site EU run: 94 auto docs + 252 items, union 384/384), and
there is NO driver reopen commit for 203b on main. But this iteration's
driver prompt lists 203b as agent c's CURRENT work (fit/batch_eu.py
data/db/platefits data/review docs/batch_eu.md tests/test_batch_eu.py), and
203b's own hand-over anticipates exactly this: "If this task is ever
reopened (e.g. a 212-era re-coverage run changes the tree), re-verify the
checks below." The batch ran over the 384-site world; the world is now 499
built, and the batch's live union test gates on "Sites run: 294" vs the live
EU partition - so agent c's 203b session is a re-run/re-verify over the
grown world, and its writes (new EU docs + item re-upserts, incl. the
batch's searched wording on search-set items my nopicture also writes) must
land before my live run's commit ("212 runs last on purpose"). 203b is
already on my Depends on line (211 satisfied); the driver brings this task
back once 203b is (re-)merged. Do NOT run the live phases before then
(searches.json is resumable, so nothing is lost by waiting).

Agent c's other in-flight work is FILE-DISJOINT from the live run (verified
on the live tree): 306's audit items are doc-keyed (<site>.<doc>.json) for
doc'd sites; my nopicture writes the 245 EXACT bare <site>.json files of the
no-doc search set (245/245 checked, 0 doc-keyed in the set - upsert_item's
lead follows candidates[0].plan and these items are candidate-less, so the
names never move); 306 exports web/data/sites.json + review.json, I
re-export plans.json. 207 (files_roman/classified_roman jsonl), 302a, 304
disjoint.

**LIVE WORLD RE-MEASURED TODAY (the run recomputes all of this at run time -
these pins feed the diff rules and the expectations):** main is frozen at
77bdf5d (an ancestor of my pre-218 sync 54c0711 - the git world is
byte-identical to what I verified in 217/219):
- 499 built; 131 docs = 21 by:hand + 110 by:agent; nofit 402; cand-sites 601;
  search set 245 = 204 qid + 41 no-qid (first4: aalsum-q3902030,
  abbotsbury-castle-q3662453, aberdeen-mound-q4666953, aden-site-q4682175;
  first no-qid: aggersborg) - matches the iter-217 post-aeeb5aa measurement
  (the 246 in the CORRECTION-4 entry was pre-aeeb5aa, when numancia had no
  row yet).
- files.jsonl: 923 kept rows, only 1 without a local copy - the no-source
  Stukeley TAB XI (stonehenge-q39671, thumb/url null - neither fetches nor
  drops). The ~328 missing copies measured 10-13 all arrived in the shared
  store via the lead's aeeb5aa "data/raw synced both ways Mac<->VM" - **the
  fetch phase is now a no-op** (0 thumb, 0 url, 1 nosrc): it only prints
  counts + re-exports plans.
- plans.json: 1475 rows = 1475 unique (id, sites[0]) pairs, 0 rows
  referencing a search-set site (aeeb5aa's 1474 + numancia's row back) -
  the baseline for the key-set diff rule in step 5; re-record it at run
  time anyway (the 203b re-run or other merges may have moved it).
- data/cover/searches.json: absent (fresh start; the test's build_tree
  unlinks it from the test tree, so the test stays deterministic before AND
  after the live run).
- data/review: 346 items + README (347 files).
- Golden: sha256sum -c tests/golden/hand_fit_docs.sha256 = 40/40 today.

**EXACT NEXT STEP (when 212a reopens, i.e. 203b re-merged) - the live run,
network allowed, in this checkout, one session per phase if it does not fit
in one:**
 1. `.venv/bin/python fit/cover.py fetch` (near-instant now: 0 fetches)
 2. `.venv/bin/python fit/cover.py search` (real Commons/Wikidata, 1/s paced,
    resumable via data/cover/searches.json)
 3. `.venv/bin/python fit/cover.py stage --live` (evidence.record for the new
    rows; ask_human ONLY if new files were found and clef 127.0.0.1:18083 is
    still down: tunnel, or approve the LLM on 8081 as one-off classifier)
 4. `.venv/bin/python fit/cover.py nopicture` (re-stamps no_picture_found on
    the 245 bare items with the exact searched string)
 5. Record the plans.json (id, sites[0]) key-set diff vs the committed file
    (any LOST key = a fetch failure to record as a data finding, never
    silently dropped; expected growth is pure adds), then commit:
    data/cover/searches.json (new to git), grown files.jsonl +
    classified.jsonl, the item files, the re-exported plans.json (data/raw
    is gitignored - note the new copies; expect ~0 new copies today)
 6. `sha256sum -c tests/golden/hand_fit_docs.sha256` must pass 40/40; re-run
    `.venv/bin/python -m pytest tests/test_cover.py -q` green (the test is
    state-aware: the fake-hit site is recomputed as the first qid site still
    in the search set, and the fake-title preconditions re-check themselves).
 The loop (box 1's "site goes through the normal loop") is the LEAD's
 (matcher ELoFTR 127.0.0.1:8091; RoMa 8092 down, skipped; the LLM on 8081 is
 forbidden for placement); sync/export are 212b's; the report is 212c's.

**If the 203b re-run reshapes the world before I run (new EU docs on grown
sites):** every phase recomputes at run time (search set, nofit, fetch,
search, nopicture); the only pinned things are the 40 golden docs and the
pure-adds key-set rule, both of which the re-run respects (203b's
golden-intact hand-over + union check).
---
(iteration 219 hand-over, superseded sections in git: `git show
dfbc286:tasks/212a-cover-search.md`; iteration 217: `git show
0ca160f:tasks/212a-cover-search.md`; iteration 216: `git show
590284f:tasks/212a-cover-search.md`.)
