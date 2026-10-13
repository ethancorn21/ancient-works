Status: open
# 236c: Consolidate the US cities into the page's data and build the sites
Depends on: 236a, 236b
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py

## Goal
Subtask of 236. Run the 211 consolidation (fit/merge.py globs every extras_/files_/classified_ staging file)
over 236a's and 236b's staging, build the new sites (aerial ground; 3DEP relief where a fort site has it),
and export plans.json so the new pictures appear on the page and in the fit queue.

## Acceptance criteria
- [ ] fit/merge.py consolidates the two new staging sets; no duplicate site per QID; the merge test passes.
- [ ] Every new US city site is built (web/data/sites/<id>/ exists, aerial tiles present) and listed in
      web/data/sites.json; plans.json lists their pictures.
- [ ] Every new site ends with a fitted drawing or a review item (tools/site_done.py), as in 212.
- [ ] The page loads with the new sites (server/serve.py), nothing that worked before breaks; full suite =
      baseline.

## Notes
- Site dirs and data/raw are per machine (gitignored): record in the hand-over which sites were built here,
  so the lead syncs them to the owner's Mac.
