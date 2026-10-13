Status: open
# 212: Cover - the last uncovered sites, the final sync, the report
Depends on: 203a, 203b, 211
Touches: fit/cover.py, data/review/, web/data/review.json, data/commons/files.jsonl, data/commons/classified.jsonl, web/data/plans.json, web/data/sites.json, web/data/sites/, docs/batch.md, tests/test_cover.py

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

## Hand-over
(2026-10-12, iteration 200, agent a - FIRST session on 212; investigation only, no code written yet. fit/cover.py and tests/test_cover.py do NOT exist yet; the task is unsplit and ready to design.)

**Depends on satisfied:** 203a, 203b, 211 all `Status: done` and merged into main (this branch = main + driver housekeeping; my branch tip 5f1767f). Suite last green on the merged tree: 150 passed, 1 skipped (the 1 skip is a standing baseline, see 211 hand-over; the old test_gate red was resolved by the 218 line - verify current suite state first: `.venv/bin/python -m pytest tests/ -q`, NEVER bare pytest - system python has no numpy/PIL).

**Live tree state (measured this session, the numbers to work from):**
- web/data/sites.json: **499** built sites (385 pre-build + 114 new from 211). Regions: England 168, US 90, France 66, Netherlands 46, Germany 45, Belgium 23, Scotland 20, Wales 17, Denmark 6, None 6, Spain 4, Lithuania 2, Italy 2, +4 singles.
- data/db/platefits/: **123 docs = 21 by:hand (ALL 21 byte-identical to tests/golden/hand_fit_docs.sha256, verified) + 102 by:agent auto** (all carry `auto:true` + numeric score; 303 stamped every doc). Pre-batch US auto: 16, EU auto: 94 -> now 102 (8 auto docs were deleted by the line's fabrication check / matcher work in 302/303/306; a few docs were added).
- data/review/: **341 item files** (246 carry `no_picture_found`; the rest have candidates) + README. web/data/review.json: `at=2026-10-12T18:01:52`, **333 open** (derived: resolved items dropped by export c5250a4).
- web/data/plans.json: 1168 rows (574 carry non-empty `sites`).
- **Coverage:** 87 sites have a fit (doc or old-style site.json plate fit); **53 sites have no fit but have plans.json candidates (ALL 53 already have a review item - 0 missing)**; **359 sites have no fit and no candidate** (of these 246 have a batch "no picture found" item - 71 US + 175 EU - whose `no_picture_found.searched` says only "web/data/plans.json (N rows, matched by the sites field)"; **~113 have NO item at all = the new 211 sites**). **313 of the 359 have a qid** (the rest have no qid: only a title search is possible, or record that none was).
- The 246 batch no-picture items + the ~113 item-less sites = the **search set of box 1** (box 1 says "without a fit and without a candidate").

**Key machinery (all read this session):**
- `fit/batch_us.py`: the shared loop. `run_sites(root, site_ids, model)` - candidates from plans.json (`candidates`), skips candidates that already have a doc (`pre_docs`) OR are already in the site's item (site_done's rule - read site_done._fit before reusing run_sites: it computes `uncovered` itself; run_sites alone re-fits itemed candidates, and 201's upsert REPLACES the item's rich entry with a stub - the batch_us 203a hand-over + PITFALLS "Recorded-answer batch tests must be state-aware" warn about exactly this). `write_doc` (auto:true, by:agent, score; never rewrites), `write_item`, `gate_placement`, `classify`, `_sample` (random.Random(SEED).sample), `write_report` (the docs/batch_us.md format - copy its shape for docs/batch.md), `recorded_model` (injectable answers; tests use it), `llm_model` (the working-phase model, needs the AI-box tunnel LLM on 127.0.0.1:8081 and pictures local in data/raw/commons/<site>/). SEED=20261010 is the BATCH's seed; **212 needs its OWN recorded seed** for the combined 20-sample (the 203b hand-over says so: 212 picks from the whole auto-doc union with its own seed).
- `pipeline/plan_fit.py` = the ONLY page-facing sync. `main(args, root=None)`: no args -> sweeps every doc in data/db/platefits; per doc: who_placed (hand -> build, no check; agent -> build; None -> refused, no build no delete), stamps by:agent into unmarked auto docs, `is_done` skips current overlays, `build` writes web/data/sites/<sid>/depictions.json (+ plan_<plan>.webp / _ink.webp via depict.make_ink) and calls `build_site.set_drawings`; `prune` drops overlays of deleted docs. **Box 3 = run exactly this, once, by hand** (the task's Notes: "the sync runs plan_fit.main() by hand (the way serve.py's after_write does it)"). PITFALLS (read them all, section pipeline/plan_fit.py): (1) never call main() bare without root in a throwaway context - it targets the checkout ROOT; for the LIVE run that is the point (the working phase runs it against this checkout, network allowed); for TESTS call `plan_fit.main(args, root=<temp tree>)` with the tree's data/db/platefits seeded; (2) the serve worker's sweep aborts mid-sweep on ANY non-SystemExit (KeyError on a bad commons ref, 429) - plan_fit.main itself catches only SystemExit per doc; my direct run must not die on one bad doc (catch/record and continue, or precheck) - decide and record; (3) build() downloads the big jpg for commons docs (paced 1/s; load_picture caches to data/raw/commons/big/) - a full live sweep of ~100 commons docs is a long download (the shared gitignored data/raw/commons/big store may already have most: check first); book docs read data/raw/books/<ia>/full/<file> locally (shared store, present in this checkout).
- `fit/review.py` (stdlib-only): `upsert_item(root, site_id, entries, no_picture)` - no_picture dict records `{searched, at}`; `export(root, site_id=None)` writes web/data/review.json (OPEN items only: a doc for any candidate => resolved, recorded write-once into the item file) and returns (n_open, n_total). **Box 4 = the full export (site_id=None) after all item changes.** PITFALLS: review.json is a derived page - three count-deriving tests (test_fit_provenance.test_line_refuses_unmarked_non_auto_doc, test_site_done.test_site_done_line, test_fit_queue.test_save_runs_the_one_site_line) fail whenever the committed page goes stale against the live store; my full export + committing web/data/review.json keeps them green. Also `candidate_evidence(plan_id, root)` gives the 200 field for item entries.
- `pipeline/commons.py`: the harvest machinery for the targeted search. `wd_claims(qids)` -> {qid: {cat: P373, plan: P3311, image: P18}}; `files_of(cat, depth)` (category files + map/plan/old-picture subcats, SKIP/FOLLOW regexes); `search(name)` (3 full-text queries, SEARCHES); `info(titles)` (imageinfo + extmetadata, 1280 thumb); `keep(title, m)` + `year_of` (the 1925 cut-off, NO regex); `harvest(ids)` = the ORIGINAL per-site harvest (P3311+P18 titles + name search + depth-1 category files, append sentinel `{site, qid, title: None, cat, n_seen}` when nothing kept); `rows()` re-judges; local(r) = data/raw/commons/<site>/<sha1(title)[:16]>.jpg; `thumbs()` fetches the 1280 jpg; `classify()` uses clef (AIBOX) - **p_plan/p_birdseye/p_photo -> classified.jsonl {site, title, p_*}`. **`fit/evidence.py`: `record_live`/`live_evidence` are the 200 evidence recorder for commons rows (routes cascade: category membership (incl. subcat chain), P3311/P18, P180 via the file's MediaInfo item (fetch_page_ids + fetch_file_entities), caption/part/sheet, none) - and it ALREADY fetches exactly the facts box 1 names (site QID category, P180 depictions, the row's title). `record(files, books, live=True, only=[site ids...])` appends the evidence field, resumable, paced. **This is the search-harder machinery to reuse: it does category + P180 + caption/title against the site; commons.search does the title full-text search. The search record (no_picture_found.searched) must name exactly: the P373 category (or "none"), the P180 query, the title queries, the date.**
- `tools/export_plans.py`: regenerates web/data/plans.json from data/books/index.jsonl + `commons_rows(min_p=0.3)` (a commons row lands in plans only if: in classified.jsonl with p_photo<0.5 and max(p_plan,p_birdseye)>=0.3, AND the local 1280 jpg exists at data/raw/commons/<site>/<sha1(title)[:16]>.jpg; row id = `c_` + sha1(title)[:16], url `media/commons/<site>/<h>.jpg`, sites=[site]). Re-running it after staging new rows is the box-1 "its row added to web/data/plans.json" (211 already proved it is pure growth/idempotent).
- `tools/site_done.py`: the one-site line (fit -> sync -> entry -> review). **Its `_fit` is the correct way to feed a site to the loop without stomping item entries**: it fits only candidates with NEITHER doc NOR item entry, tries fit/matchfit first (only if reachable - it is NOT on this VM; matchfit.reachable() gates it), then batch_us.run_sites. For a search-found candidate that has no doc and no item entry yet, this is exactly the normal loop.
- **The 25 hand fits / 000's golden test** = tests/test_serve.py::test_hand_fits_are_the_reference (fixture golden_sites = tests/golden/hand_fit_sites.txt, 19 sites): every golden site has drawings >= 1 and a matching overlay entry in its depictions.json (served, temp tree). The 21 hand docs + 19 site.json files are in tests/golden/hand_fit_docs.sha256 (40 lines). Box 3's "the 25 hand fits' overlays are unchanged" = that test still passes after my sync. (The "25" of GOAL.md counts fitted drawings across 19 sites; do not try to make it literally 25 - the golden test is the spec. If in doubt, note in DECISIONS.)
- conftest `served` fixture: temp tree, server/serve.py --port 0, web/ + data/ (minus data/raw and .npy/.npz) copied, per-site web dirs LINKED to the checkout (so the served depictions.json IS the checkout's file - a test must never let the served tree WRITE into it: the served server only writes on platefits PUTs; a GET-only serve never rebuilds overlays - PITFALLS 451). `copy_web(tree, real=...)` for sites a test writes into.

**What the next session does (ONE step):**
1. `git log --oneline -8` + `git status` (the driver may have merged new work since my investigation; if any of 302a/304/306 changed fit/ or data/db/platefits, re-measure the 123/21/102 numbers - they drift with the line's work).
2. DESIGN fit/cover.py (no code yet - write the design in DECISIONS first). Skeleton to write down:
   - `search_sites(root)` -> the no-fit-no-candidate set (reuse batch_us._sites/candidates/pre_docs/is_pre_fit logic, do NOT import private names across tasks - batch_us is 203a's module; small duplication of the set math in cover.py is fine, importing run_sites/write_doc/write_item/_sample IS the intended reuse per 203's notes).
   - targeted search per site WITH qid: P373 category files (commons.files_of depth 1 + the site's P3311/P18 claims), P180 (files whose MediaInfo item depicts the qid - the Commons API: `wbgetentities` on the file items of the category/search results is what evidence.fetch_file_entities does; or the MediaWiki query `wbentitytimeseries`... NO - the proven path is: for each candidate file title, evidence.fetch_page_ids+fetch_file_entities and test qid in p180), title search (commons.search(site name) - record the 3 queries). Per site WITHOUT qid: title search only, and say so in the record.
   - found files: apply commons.keep() (1925 cut-off, NO regex); stage into data/commons/files.jsonl (append, the harvest row shape + qid) and data/commons/classified.jsonl (only after the local 1280 jpg exists - fetch with commons.thumbs-style pacing; classify with clef only in the working phase - in the DRY/test phase the classifier is injectable or the rows are staged with a recorded p_*); run `fit/evidence.py record --live --only <site>` (or its functions in-process) to append the 200 evidence field to the new files.jsonl rows; re-run tools/export_plans.py (growth-only).
   - then the loop: for each site that gained candidates, site_done's _fit-equivalent (uncovered = no doc and not in item) via batch_us.run_sites with the working model (llm_model, AI-box tunnel) or recorded answers in tests; then per new doc decide sync-or-item per the one-site line's rules? NO - the sync is the separate box-3 pass; the loop only writes docs/items (batch_us never PUTs).
   - nothing found (or found-but-kept-none): `review.upsert_item(root, sid, [], no_picture={searched: <the exact queries incl. category name, P180, title queries, date>, at})` - for the 246 existing items this RE-RECORDS the richer searched string (upsert with entries=[] keeps existing candidates? NO - entries=[] + no_picture dict keeps the item's existing candidates and updates no_picture - read upsert_item again: it clears no_picture only when entries non-empty; with entries=[] and a dict it sets it - and candidates are untouched).
   - `sync(root)`: plan_fit.main([], root=root) but made per-doc-proof (catch non-SystemExit per doc, print, continue - mirroring what the serve worker lacks; DECISIONS entry) + plan_fit.prune(root) (main already prunes when no args) + then handle docs whose build FAILED with no overlay: upsert a review item for them (why = the build failure) so box 6's invariant (drawings>=1 OR open item) holds for every site.
   - `report(root)`: docs/batch.md in batch_us.write_report's shape but FINAL: counts per outcome over ALL 499 (fit: hand/auto/human-saved split - human-saved = by:hand docs not in the golden's 21, i.e. saved on the page after the batches: compute, don't guess; review item; no picture found), a **212-own seed** (new constant, recorded in the doc) sampling 20 of the whole auto-doc set (102) with page URL + gate score, and the no-picture list with per-site searched record.
   - `export`: fit/review.export(root) full (box 4) - committed page file.
   - CLI: `--working` (live: network + model), `--dry`/`--model-json F` (recorded answers, no network), subcommands for the phases so the test can drive them in-process.
3. Then the next session writes tests/test_cover.py (hermetic: temp tree via conftest patterns; NO network - monkeypatch/stub any commons/wikimedia call; port 0 via the served fixture; the big box-6 test: after running cover's sync+export on the temp tree (with a recorded-model loop and stand-in pictures sized to doc["size"] - the test_site_done pattern: PIL-drawn stand-ins, no downloads), every built site in the SERVED sites.json has drawings>=1 or is in the SERVED review.json open list; golden test re-runs; docs/batch.md sample reproducible from the recorded seed by re-computing random.Random(seed).sample(sorted auto docs, 20)).
4. The WORKING run itself (network + model + downloads) is a later session once the code+tests are green on the temp tree (record everything in docs/batch.md; commit the grown canonical files + review items + review.json + sites.json + depictions + docs/batch.md; the golden 40-line file must stay byte-identical - verify with sha256sum -c at the end).

**Risks to check first next session:** (a) agent c is mid-flight on 302a/304/306 - they touch fit/* and data/db/platefits on THEIR branches; main may gain/lose auto docs before my live run - my code must be state-agnostic (recompute everything from the live tree, no pinned counts in code; the 203b state-aware-test PITFALLS applies to my box-6 test too); (b) clef (AIBOX 127.0.0.1:18083) and the LLM tunnel (127.0.0.1:8081) availability in the working phase (check `curl -s 127.0.0.1:8081/v1/models` etc.; if down, the working phase is blocked -> note in DECISIONS, the dry run still works); (c) data/raw/commons/big may already cache most big jpgs (check `ls data/raw/commons/big | wc -l`) - the live plan_fit sweep's download cost depends on it.

**Do NOT touch:** requirements.in/.txt (302a/304 hold them), tests/conftest.py (ask in DECISIONS), any other task's module. My Touches already cover everything I need: fit/cover.py, data/review/, web/data/review.json, data/commons/files.jsonl, data/commons/classified.jsonl, web/data/plans.json, web/data/sites.json, web/data/sites/, docs/batch.md, tests/test_cover.py. If the design needs tools/fitkit.py or data/raw/... (images) - images are gitignored shared store, no Touches needed; data/db/platefits/ writes happen via batch_us (203a's module writing its own store) - if I end up writing docs directly, ADD data/db/platefits/ to Touches first. Also add web/data/depictions paths? They live under web/data/sites/ (already in Touches).

Tests when last seen: not run this session (investigation only; last suite state per 211 hand-over: 150 passed, 1 skipped on the merged tree - re-run before the first code commit).

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/212-cover-final.md` (in progress, agent a, iteration 200) - hand-over: (2026-10-12, iteration 200, agent a - FIRST session on 212; investigation only, no code written yet. fit/cover.py and tests/test_cover.py do NOT exist yet; the task is unsplit and ready to design.)
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/221-review-stats-test.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

(no entries yet)

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (1 tests)
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_gate.py:36: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    1 failed, 59 passed in 63.50s (0:01:03)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites
