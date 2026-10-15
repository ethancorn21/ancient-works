Status: open
# 236c: Consolidate the US cities into the page's data and build the sites
Depends on: 236a, 236b, 240, 241
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/sites/, data/db/platefits/, data/review/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, web/data/review.json, tests/test_merge.py

## Goal
Subtask of 236. Run the 211 consolidation (fit/merge.py globs every extras_/files_/classified_ staging file)
over 236a's and 236b's staging, build the new sites (aerial ground; 3DEP relief where a fort site has it),
and export plans.json so the new pictures appear on the page and in the fit queue.

## Acceptance criteria
- [x] fit/merge.py consolidates the two new staging sets; no duplicate site per QID; the merge test passes.
- [x] Every new US city site is built (web/data/sites/<id>/ exists, aerial tiles present) and listed in
      web/data/sites.json; plans.json lists their pictures.
- [x] Every new site ends with a fitted drawing or a review item (tools/site_done.py), as in 212.
- [ ] The page loads with the new sites (server/serve.py), nothing that worked before breaks; full suite =
      baseline.

## Notes
- Site dirs and data/raw are per machine (gitignored): record in the hand-over which sites were built here,
  so the lead syncs them to the owner's Mac.

## Proposed changes
(2026-10-14, iteration 195, agent a - the 236b split, driver instruction.) The bird's-eye staging now
spans THREE source tasks: 236b (16 cities, closed done), 240 (batch 4: Denver, St. Paul, Minneapolis,
Cleveland) and 241 (batch 5: the final five). `Depends on:` now carries 240 and 241 (they must land
before the consolidation). Suggested box changes: (a) box 1's "the two new staging sets" should read
"every staging set under the extras_/files_/classified_ prefixes" - fit/merge.py already globs them
all (verified: its TARGETS pair each canonical file with prefix + "*.jsonl", so 236a's
extras_us_cities, 236b's *_us_birdseye, 240's *_us_birdseye_batch4 and 241's *_us_birdseye_batch5 are
all picked up; the Goal's "over 236a's and 236b's staging" reads the same) - and (b) the 25-city
total that was 236b's box 4 before the split now lives here: add to box 1 (or as a new box) - the
consolidated new US city sites total at least 25 (16 + 4 + 5), or the lead docs record a shortfall
and this task's hand-over records the final count.

## Hand-over

(2026-10-15, iteration 208, agent c). **Boxes 1, 2, 3 DONE. Remaining step 1 (docs/sources.md) was WRITTEN this session but left UNCOMMITTED** (context limit hit before the commit; the harness saved the worktree change). Remaining: review+commit the docs change, the frozen-baseline re-baseline (step 2), then box 4 (full suite).

**What it.208 did (verify with `git diff docs/sources.md` - the change is in the worktree, NOT committed):** section 9 gained the US-cities content in the 211/230 pattern: (a) the intro line extended with "; the US cities by the 2026-10-15 re-run, task 236c"; (b) FOUR new table rows - 236a (4 owner-city sites / 15 plan rows: NY 4, DC 3, SF 4, Nashville 4; drops: Boschke gate wall, Ringgold not on Commons, 1916/1991 modern redrawings, per-plan dupes/crops, Negley photos, battle maps, small fragments, outside-window, 1803 NARA item), 236b (12 new + 4 shared sites / 23 views; per-city drops: same-genre shallower sheets, pictorial/painted, railway, regional, outside-window, Negley fort views, photos, noise; same-genre passers RESERVED), 240 (4/4), 241 (5/5 + **Albuquerque DROPPED** - no drawn view in the Commons mirror, the documented-search drop - so the 25 total has no shortfall); (c) a new closing paragraph "The 2026-10-15 re-run (task 236c, the US cities)" - 119 staging rows (25 site 202->227, 47 picture 1748->1795, 47 classified 1055->1102), 0 refused, log = this run's 119-line snapshot (34/58/12/15); 25 new sites 508->533 (aerial ground, USGS 3DEP, 2000 m town box, region "United States"); plans 1572->1619 (33 birdseye + 14 plan); pure growth; site_done: all 47 refused by the matcher (46 confidence, 1 spread) -> 25 review items, 481 open, 0 drawings; (d) the Roman row's log parenthetical corrected to past tense (the log is no longer its 45-line snapshot - it now holds the 236c 119-line one; the old snapshot is in git history). EVERY number was verified by running code on the live files (not reasoning): the 12 staged_* row counts, the 25 US ids in extras (region "United States"), sites.json (25 US, drawings 0, no depictions), plans.json (47 US rows: 33 birdseye / 14 plan), review.json (25 US open items of 481), the 119-line log, plus the pre/post counts from the it.205/206/207 DECISIONS entries. No test references docs/sources.md (grepped tests/ fit/ tools/ server/), so it cannot break the suite.

**Remaining steps (in order; every command under `.venv/bin/python`):**
1. Commit the uncommitted docs/sources.md (it belongs with the next step's commit; the worktree diff is the whole change).
2. RE-BASELINE the frozen artifacts - SEMANTICS: the baseline is the PRE-PHASE set (the test's own docstring; 230's precedent): a post-build baseline would make test_new_sites_are_complete's non-empty `new` assertion fail. The arithmetic was VERIFIED on the live data this session:
   - `data/merge/sites_premerge_baseline.jsonl` <- the current 533 `web/data/sites.json` entries MINUS the 25 US ids = the 508 pre-build entries (== the existing 499 baseline + exactly the nine Roman Scottish forts: ardoch, carriden, cilurni, congavata, kirkintilloch, luguvallium-q71551754, petriana, tunnocelum, virosidum - the measured set difference).
   - `tests/test_merge.py::test_served_sites_grew_purely`: constant 499 -> 508 (the assert at ~line 368) + its docstring (~line 364: "the 508 entries served before 236c's build: 230's 499 plus the nine Roman Scottish forts").
   - `data/merge/plans_premerge_keys.jsonl` <- the current 1,619 `web/data/plans.json` rows MINUS the 47 US rows = the 1,572 pre-export keys, same {"id","site"} shape (site = the row's `sites` list's first element or null; the current frozen 1,510 keys are its verified subset).
   - After re-baselining, run `tests/test_merge.py`: test_served_sites_grew_purely asserts 508, and test_new_sites_are_complete's `new` is exactly the 25 US sites (non-empty, all complete).
3. BOX 4: full suite `tests/ -q -p no:cacheprovider` judged against the CURRENT main baseline (194P/1S/0F per agent a's recent 814/816 sessions; the 2026-10-13 driver note in PROGRESS listed test_fit_queue.py::test_placement_gestures_and_save_in_the_browser red at a loop start - if it is red at my run time, record it, do not absorb it, do not claim it - the 241-187/188 pattern). The owner-check pair is IN the suite: before any run that may re-encode the 307d PNGs, restore the differing ones to MAIN's bytes (hygiene below); after it, restore again and commit only my files.

**State of this machine (for the lead's sync to the owner's Mac, per Notes):** unchanged since it.207 - ALL 25 US sites built HERE, all 47 picture files fetched HERE, all 25 completed HERE (committed item files - nothing local left to sync beyond the gitignored build dirs): baltimore-q5092, boston-q100, chicago-q1297, cincinnati-q43196, cleveland-q37320, columbus-q16567, denver-q16554, detroit-q12439, indianapolis-q6346, kansas-city-q41819, louisville-q43668, memphis-q16563, milwaukee-q37836, minneapolis-q36091, nashville-q23197, new-orleans-q34404, new-york-q60, omaha-q43199, philadelphia-q1345, pittsburgh-q1342, portland-q6106, san-francisco-q62, st-louis-q38022, st-paul-q28848, washington-q61. Per site: data/sites/<id>/site.json (TRACKED) + data/sites/<id>/{dem.npy,dem_box.json,dem_credit.json} (gitignored) and web/data/sites/<id>/{relief.jpg, imagery.jpg, block_h.png, block_top.jpg} (gitignored); lidar_credit "USGS 3DEP", relief_clip_m ~1.2, 2000 m box, drawings 0, NO depictions.json.

**Team-mode hygiene on this branch (read before committing):**
- Agent a's 307d lane rides on this branch: after my commits the worktree should be clean (only my files), but HEAD may differ from main on docs/site_flow/307d_B_1-card.png and 307d_B_5-reload.png (A_1-card == main) - agent a is actively working the settle family (242/810/812/814/815/816 per the driver). NEVER `git add -A`; commit only my Touches paths (+ my task file + DECISIONS.md). The restore target for any owner-check run is always MAIN's bytes (`git diff main -- docs/site_flow/`), never HEAD's (PITFALLS tests/playwright).
- A full-suite red outside this lane (the owner-check family, roman, the other lanes): record it, do not absorb it, do not claim (the 241-187/188 pattern); new reds in MY lane are mine to fix.
- `web/data/review.json` `at` line: if a driver merge hits the known "at"-line conflict (PITFALLS 1444/1535), keep the newer `at` and verify the items list (the 25 US items must survive).

**Re-read:** the UNCOMMITTED `git diff docs/sources.md` (the whole it.208 change - step 1's commit); tests/test_merge.py test_served_sites_grew_purely (the 499 constant at ~line 368 and its docstring ~line 364) and test_new_sites_are_complete (how `new` is derived, the non-empty assertion) - the re-baseline points of step 2; data/merge/sites_premerge_baseline.jsonl / plans_premerge_keys.jsonl (frozen content 499 / 1,510 entries - REPLACE the files, do not append).
