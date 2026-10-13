Status: in-progress
# 212a: Cover search - a targeted picture search for every uncovered site, "no picture found" items
Depends on: 211, 203b (203b in flight, agent c - my 212a re-coverage gave bibracte plans rows, which voids 203b's pinned zero-candidate no-picture case in test_batch_eu; the test's own docstring assigns that list extension to a 203b session)
Touches: fit/cover.py, fit/cover_qwen8080.py, data/cover/ (searches.json + the run log + the stage record), data/review/, data/commons/files.jsonl, data/commons/classified.jsonl, data/raw/commons/, web/data/plans.json, web/data/fit_queue.json, web/data/review.json, tests/test_cover.py

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
- [x] Run it for real once and commit the results.

## Notes
- Commit working code every session. Notes-only sessions end the job (212 ended that way).


## Hand-over

(2026-10-13, iteration 223, agent a - DONE. All 4 boxes ticked, Status: done.
Small session per the iter-222 hand-over's exact next steps: Touches gained
web/data/review.json, the export phase ran, the two reds I owned are fixed,
the remaining two reds are 203b's (Depends on line; agent c on 203b now).
Nothing more for me on this task; the lead's loop over the 16 found-picture
sites, 212b's sync and 212c's report come after this merges.)

**FINAL STATE:**
- Box 1-3 (code + test): fit/cover.py search/nopicture phases; tests/
  test_cover.py green (in the final suite run).
- Box 4 (the live run, committed): search (e6ff1a0 - 245 records: 204 qid
  + 41 no-qid, 107 new files on 16 sites, 0 failed routes) -> stage
  (9c48d94 - the lead's one-off 8080 Qwen answer to request 003; 107/107
  fetched + classified, every row carries the one-off note; evidence
  recorded live; plans.json 1475->1510, key-set diff = 0 lost / 35 gained
  = exactly the gate-passing rows) -> nopicture (9c48d94 - 234 items
  re-stamped with the exact searched string) -> fit_queue (9c48d94 -
  229->241, 0 sites lost) -> export (a7f5dda - web/data/review.json
  re-derived: same 333 open sites, 0 lost/gained, exactly 234 entries
  changed = the re-stamps, all 346 item files byte-identical, no
  write-once resolutions written because the run built no docs).
- Suite at done: 2 failed, 153 passed, 1 skipped. Golden sha256 40/40.
  web/data/review.json is consistent with the items again (test_site_done
  + test_fit_provenance green: 8 passed).

**THE TWO REMAINING REDS (both test_batch_eu.py, 203b's - mechanism verified
for agent c's notes):**
1. test_sample_run_real_gate:539 - bibracte (NO_PIC) is asserted
   zero-candidates -> the batch's no-picture re-stamp. My run gave bibracte
   plans rows (18 found, several gate-passing), so candidates() is
   non-empty and run_sites instead writes "no model answer" entries
   (_recorded_model has no answer for those fresh rows) -> rec["no_picture"]
   False. The test's own docstring assigns extending these pins to a future
   203b session when plans.json gains rows for the pinned sites.
2. test_batch_adds_files_rewrites_none:708 - the same upsert changed
   bibracte's lead (0 candidates -> N) so review.upsert_item MOVED the item
   file (<site>.json -> <site>.<lead>.json; old unlinked at fit/review.py:
   115); the test reads its recorded pre-run path -> FileNotFoundError.

**GATES AT DONE:** golden 40/40 (data/db/platefits untouched by the export);
test_cover green; page file consistent with the items; the 11 rowed
found-picture sites stay no-doc (the lead's matcher loop covers them next)
and the 5 all-below-gate sites (arbeia, carnac-stones, craig-phadrig,
indian-mounds-park, ocmulgee-mounds) stay no-picture.

---
(iteration 222 hand-over in git: `git show 99188ad:tasks/212a-cover-search.md`;
iteration 221: `git show 372101b:tasks/212a-cover-search.md`; iteration 220:
`git show 32fc092:tasks/212a-cover-search.md`; iteration 219:
`git show dfbc286:tasks/212a-cover-search.md`.)
