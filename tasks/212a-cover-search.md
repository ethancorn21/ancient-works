Status: open
# 212a: Cover search - a targeted picture search for every uncovered site, "no picture found" items
Depends on: 211, 203b (203b in flight, agent c - my 212a re-coverage gave bibracte plans rows, which voids 203b's pinned zero-candidate no-picture case in test_batch_eu; the test's own docstring assigns that list extension to a 203b session)
Touches: fit/cover.py, fit/cover_qwen8080.py, data/cover/ (searches.json + the run log + the stage record), data/review/, data/commons/files.jsonl, data/commons/classified.jsonl, data/raw/commons/, web/data/plans.json, web/data/fit_queue.json, tests/test_cover.py

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

(2026-10-13, iteration 222, agent a - the live run is DONE and committed (box 4's
work: stage + nopicture + re-export + gates); the session hit the context limit
with 4 suite failures to resolve - 2 are MINE (one command away), 2 are 203b's
(added to my Depends on). NEXT SESSION IS SMALL: follow EXACT NEXT STEPS 1-5.)

**STATE:** Box 4 executed per the lead's answer to request 003 (option b
modified: the VM's OWN 8080 vLLM qwen3.8-27b as ONE-OFF classifier, not 8081;
Clef-flash is dead - the 5060 Ti serves the matchers). Committed this session:
870d4f9 (fit/cover_qwen8080.py one-off adapter + stage's optional
classifier_note - no default change, test bytes untouched) and 9c48d94 (the
whole live run, 242 files):
- data/commons/files.jsonl +107 (by:"212", ALL with the 200 evidence field,
  recorded live - 0 failures) and classified.jsonl +107 (every row carries the
  note "qwen3.8-27b vLLM 127.0.0.1:8080 (one-off, lead's answer to request
  003)");
- web/data/plans.json 1475 -> 1510: KEY-SET DIFF = 0 LOST, 35 gained = exactly
  the gate-passing pictures (p_photo<0.5 AND max(p_plan,p_birdseye)>=0.3 -
  export_plans' design, PITFALLS filed). 11 of the 16 found-picture sites got
  rows; 5 (arbeia, carnac-stones, craig-phadrig, indian-mounds-park,
  ocmulgee-mounds) had ALL pictures fall below the gate (photos/views) and
  stay no-picture sites;
- 234 no-picture items re-stamped with the exact searched string (245 records
  minus the 11 now-in-cand) - NOT the 229 the previous hand-over guessed;
- web/data/fit_queue.json regenerated via tools/fit_queue.py: 229 -> 241
  entries, 0 sites lost (+12: my 11 + numancia live drift); the test is
  derived-never-pinned and passed;
- data/cover/stage_qwen8080.json (the one-off record the lead asked for) +
  stage.run.log; data/cover/ stays on Touches (now "...+ the stage record").
Golden gate after the run: sha256sum -c tests/golden/hand_fit_docs.sha256 =
40/40 OK. Untouched by me, per pins: the 40 golden docs, the 52 all-in-item
items, bethlehem/shotwick, stonehenge's rows/item (it has rows -> never in
the search set).

**TWO REAL BUGS found + fixed this session (both in 9c48d94, PITFALLS filed):**
(a) fit/cover.py _fetch_one did `open(dst + ".part")` on a PosixPath -
TypeError swallowed by its per-file except as "fetch failed ... unsupported
operand type(s) for +: 'PosixPath' and 'str'" for EVERY file (the tests never
reach this path: their trees pre-seed every local copy, so p.exists()
short-circuits - the live run was the first to actually download). (b) my
adapter's first version returned {plan,birdseye,photo} instead of
p_-prefixed keys (KeyError: 'p_plan' in the stage writer).

**POST-RUN SUITE (ran once, after the commit): 4 failed, 151 passed, 1
skipped. Full trace: /tmp/aw222-postsuite.log (persists on this VM).**
1. test_site_done.py::test_site_done_line:330 - MINE TO FIX: the repo's
   web/data/review.json is STALE (it predates my nopicture re-stamps; aalsum's
   item now carries the exact searched string, the page file the batch-era
   "web/data/plans.json ..." string). The test re-derives the open list in
   its tree from the re-stamped items and compares to the repo page file.
   FIX: add `web/data/review.json` to my Touches line, run
   `.venv/bin/python fit/cover.py export` (my module's phase - the one and
   only writer of that page file; it re-derives the open list from the
   current items, write-once resolutions only - no docs changed this session
   so expect no item-file writes, only the page file), commit, re-run that
   test. The lead's loop + 212b run sync+export again later; this just makes
   my branch's page file consistent with my items.
2. test_fit_provenance.py::test_line_refuses_unmarked_non_auto_doc:377 - NOT
   YET DIAGNOSED (context limit). It copies ROOT data (my re-stamped items,
   my plans.json) into a tree and runs the one-site line on stonehenge
   (unchanged by me: it has rows). READ /tmp/aw222-postsuite.log lines 153-246
   first. Working hypothesis: it also compares against the stale repo
   review.json (same root cause as 1 -> the export fixes it). If instead the
   assertion touches something my data changed, fix data-side - NEVER edit
   their test (it belongs to the 303/232 line; the 232 re-pin is done by the
   lead in 77bdf5d).
3. + 4. test_batch_eu.py::test_sample_run_real_gate AND
   ::test_batch_adds_files_rewrites_none - 203b's, NOT mine to fix: bibracte
   is 203b's NO_PIC site pinned "zero candidates, 201-era no-picture item";
   my run gave bibracte plans rows (18 found, several gate-passing) and
   234-item re-stamps, so (1) the no-picture expectation is void and (2) its
   item file is missing from the run's tree post-run (hypothesis: resolved by
   a doc the batch built -> the site's scoped export deleted it; read log
   lines 84-153 to confirm). The test's own docstring: "if plans.json gains
   rows for these sites ... a future 203b session extends the lists for an
   intended change" - my 212a run IS that change, and agent c is working on
   203b RIGHT NOW (the driver lists it as their current task; their
   hand-over anticipated a "212-era re-coverage run"). 203b is therefore on
   my Depends on line (the 231-234 precedent: merge-induced reds owned by
   other tasks). If my done claim is rejected on these two, that is the
   mechanism; the driver re-checks after 203b merges.

**EXACT NEXT STEPS (one small session):**
 1. Add `web/data/review.json` to the Touches line.
 2. `.venv/bin/python fit/cover.py export` (expect: writes
    web/data/review.json only - verify `git status` shows exactly that one
    web/ file; if it writes item files, inspect WHY before committing -
    write-once resolutions on items that gained a doc would be a finding).
 3. Commit it ("212a: export phase - web/data/review.json re-derived after
    the 234 no-picture re-stamps").
 4. Read /tmp/aw222-postsuite.log lines 153-246 (fit_provenance:377) and run
    `.venv/bin/python -m pytest tests/test_site_done.py
    tests/test_fit_provenance.py -q` - expect both GREEN after step 3 (if
    not, diagnose per item 2 above; data-side fix only).
 5. Re-run the FULL suite: expect exactly 2 failed (the two test_batch_eu
    ones - 203b's), everything else green. Then tick box 4, set Status:
    done (the lead's loop over the 16 found-picture sites, sync, the 212b
    export and the report are NOT this task - they run after; my export here
    is only the consistency fix my re-stamps required). If the driver rejects
    the claim on the two 203b reds, that is handled by the Depends on line
    (203b in flight now).
 Gates to keep passing at done: golden 40/40 (re-check if anything touches
 the docs - nothing should), tests/test_cover.py (its tree unlinks
 searches.json, so the committed searches.json doesn't affect it).

**Depends on line: 211 (done) + 203b (in flight, agent c - for the two
batch_eu reds above).**

---
(iteration 221 hand-over in git: `git show 372101b:tasks/212a-cover-search.md`;
iteration 220: `git show 32fc092:tasks/212a-cover-search.md`; iteration 219:
`git show dfbc286:tasks/212a-cover-search.md`; iteration 217: `git show
0ca160f:tasks/212a-cover-search.md`; iteration 216: `git show
590284f:tasks/212a-cover-search.md`.)
