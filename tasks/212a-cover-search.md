Status: open
# 212a: Cover search - a targeted picture search for every uncovered site, "no picture found" items
Depends on: 211
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
- [ ] fit/cover.py search: lists the uncovered sites (no platefit doc, no plans.json row),
      searches each, writes found pictures into the canonical files and a local copy,
      re-exports plans.json; prints counts (searched / found / nothing).
- [ ] fit/cover.py nothing-found: a review item per site, marked "no picture found",
      listing the queries and the date.
- [ ] tests/test_cover.py (no network: a recorded fake search response, sockets dead):
      one site with a hit gets staged rows + a plans row; one site without gets the
      review item with its queries.
- [ ] Run it for real once and commit the results.

## Notes
- Commit working code every session. Notes-only sessions end the job (212 ended that way).
