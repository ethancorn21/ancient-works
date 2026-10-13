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

(2026-10-13, iteration 219, agent a - **Boxes 1-3 DONE and verified:
tests/test_cover.py passed on its FIRST run (5 passed, 33.8 s, no defects - the
iter-218 fixes had already covered all five known defects from the iter-217
hand-over; before running I re-verified every pinned string/shape against
fit/cover.py and tools/export_plans.py and found no drift, so no changes were
needed). Full suite 155 passed / 1 skipped on this VM. My old step C is MOOT:
the lead marked 231-234 done with all boxes ticked in 77bdf5d (now in my
branch); 233's pure-growth and 234's fit-queue tests pass on this VM as part of
the green suite, so the lead's marking holds on both machines.

**ONLY BOX 4 (the live run) REMAINS, and it genuinely waits for 203b** (agent
c, in flight: the batch writes data/db/platefits + data/review, and my live
run's commit grows data/commons/files.jsonl + classified.jsonl, writes the
review items and re-exports web/data/plans.json - the same files; 212 runs
last on purpose). Per the team-mode rule 203b is now on my Depends on line;
the driver brings this task back once 203b merges. Do NOT run the live phases
before then (searches.json is resumable, so nothing is lost by waiting).

**EXACT NEXT STEP (when 212a reopens, 203b merged) - the live run, network
allowed, in this checkout, one session per phase if it does not fit in one:**
 1. `.venv/bin/python fit/cover.py fetch` (1/s paced, resumable; re-measure the
    missing-copy count first - ~328 kept rows today; the one row without a
    source (Stukeley TAB XI, no thumb no url, not in the committed plans.json)
    neither fetches nor drops anything)
 2. `.venv/bin/python fit/cover.py search` (real Commons/Wikidata, resumable
    via data/cover/searches.json - it now accumulates in the checkout; the
    test's build_tree unlinks it from its tree, so the test stays deterministic
    before AND after the live run)
 3. `.venv/bin/python fit/cover.py stage --live` (evidence.record for the new
    rows; ask_human ONLY if new files were found and clef 127.0.0.1:18083 is
    still down: tunnel, or approve the LLM on 8081 as one-off classifier)
 4. `.venv/bin/python fit/cover.py nopicture`
 5. Record the plans.json (id, sites[0]) key-set diff vs the committed file
    (any LOST key = a fetch failure to record as a data finding, never silently
    dropped; expected growth is pure adds), then commit: data/cover/searches.json
    (new to git), grown files.jsonl + classified.jsonl, the item files, the
    re-exported plans.json (data/raw is gitignored - note the new copies)
 6. `sha256sum -c tests/golden/hand_fit_docs.sha256` must pass 40/40; re-run
    `.venv/bin/python -m pytest tests/test_cover.py -q` green (the test is
    state-aware: the fake-hit site is recomputed as the first qid site still in
    the search set, and the fake-title preconditions re-check themselves).
 The loop (box 1's "site goes through the normal loop") is the LEAD's (matcher
 ELoFTR 127.0.0.1:8091; RoMa 8092 down, skipped; the LLM on 8081 is forbidden
 for placement); sync/export are 212b's; the report is 212c's.

**VERIFIED THIS SESSION (all against the merged tree; main tip in my branch):**
- fit/cover.py re-read against the test's pins, no drift: _search_site (the
    fake's hit record: t_plan gathers on cat+claims+p180+title, t_view on
    cat+title; n_kept counts kept-before-dedup, so the per-site line is "4
    gathered, 2 kept old, 2 new (all routes answered)"; a non-hit qid site's
    claims dict is non-empty but carries no cat/plan/image, so n_* stay 0);
    fetch (n_have = len(rows)-thumb-url, i.e. it COUNTS the no-source rows in
    "with a local copy"); _searched_string (== the test's expected_searched,
    char for char, incl. the no-qid variant); nopicture (marks the search-set
    sites that are nofit and NOT cand - the hit drops out of cand via its new
    plans row after stage; entries=[] keeps candidates; re-stamp is the 201
    contract); stage (_stage_row's field order == the test's row bytes;
    evidence.record no-ops here: by:"212" is not in source_tables() and every
    book row already carries rec, so files.jsonl is never rewritten);
    _now (tz-aware ISO - the test parses it with fromisoformat).
- tools/export_plans.py re-read: cols == the test's planned_row keys
    (id book ia file title label size map_box sites cite url view ref); a
    commons row's title is the FILE-derived name (title[5:] minus extension -
    NOT the site name: the test's planned_row `name` argument is that
    file-derived name, passed at the call site), label = when_of (1701/1850
    from the fake titles), cite = page only (artist/license empty in the
    fake), view = p_birdseye > p_plan, url = media/commons/<site>/<sha16>.jpg;
    main() prints "<n> plans, <kb> KB -> <dst>" (the test's third fetch-line
    check) and needs only data/books, data/catalog/sites.jsonl,
    data/books/matches.jsonl (optional), specs/aliases.json - all in the tree.
- commons.year_of/keep on the fake titles (1701/1850 kept via the title year
    with an empty date; the 2010 title dropped by MAX_YEAR; the video dropped
    by the mime filter) and SEARCHES (3 queries, the {n} format) confirmed.
- The test module (driver-committed in ccafaa0, blob 9f30f4c, 770 lines) is
  CORRECT AS-IS: no changes this session. Its seams for 212b/212c stand:
  PHASES (add loop/sync/export/report) and build_tree's include_sites flag.
- Costs (measured): the module alone 33.8 s (tree ~1 s, fetch fake 328 x ~5 ms,
  two export passes ~2-3 s each, search pure fakes, nopicture ~2 s - _find_item
  is 4 ms, not the iter-216 200-300 ms estimate); full suite 4 m 44 s.
- The store (shared, behind data/raw) keeps growing with other agents' writes:
  NO store file-count assertions (the test only checks no <hit> dir appears in
  it); the checkout-integrity check hashes data/ (raw symlink skipped), the
  web/data top-level files, docs/ specs/ tests/.
---
(iteration 217 hand-over, superseded sections in git: `git show
0ca160f:tasks/212a-cover-search.md`; iteration 216: `git show
590284f:tasks/212a-cover-search.md`.)
