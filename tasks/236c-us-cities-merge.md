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

(2026-10-15, iteration 209, agent c). **Boxes 1, 2, 3 DONE; steps 1 and 2 of the 208 hand-over are DONE and committed (bce2a704). Only BOX 4 (full suite) remains.**

**What it.209 did:**
1. Step 1 (docs/sources.md) needed no work: the driver had committed it.208's uncommitted change as 709734c1. Re-read that diff with fresh eyes (Re-read item) and re-measured every number against the live data: all four US lead rows (236a 4/15, 236b 12+4/23, 240 4/4, 241 5/5 + Albuquerque dropped), the closing re-run paragraph (119 staging rows, 25 sites 508->533, plans 1572->1619 = 33 birdseye/14 plan, 47 matcher refusals -> 25 review items/481 open/0 drawings) and the Roman log-parenthetical past-tense fix are all correct and complete. No test references docs/sources.md.
2. Step 2 (re-baseline) executed and verified:
   - `data/merge/sites_premerge_baseline.jsonl` 499 -> **508** (current 533 minus the 25 US ids, served order, `json.dumps(entry, ensure_ascii=False)`; the old 499 lines survive byte-identical; the 9 added ids are exactly the Roman Scottish forts: ardoch, carriden, cilurni, congavata, kirkintilloch, luguvallium-q71551754, petriana, tunnocelum, virosidum).
   - `data/merge/plans_premerge_keys.jsonl` 1510 -> **1572** (current 1619 minus the 47 US rows; {"id","site"} shape, served row order; old 1510 a verified subset, the 62 added keys are the post-211 rows 230's baseline pre-dated).
   - `tests/test_merge.py`: assert 499 -> 508 + all four re-baseline mentions in docstrings updated to "the entries/rows served before 236c's build".
   - Verified by running: `tests/test_merge.py` **11/11 in 37.5 s**; `test_new_sites_are_complete`'s `new` is now exactly the 25 US ids, each complete (dir, required fields, relief.jpg iff the USGS 3DEP credit, no coverable old-map layer over the US). The 9 Roman forts are now INSIDE the pure-growth baseline, so from now on `test_served_sites_grew_purely` guards them against non-marker rewrites too.

**BOX 4 (the only remaining step) - exact plan:**
1. Hygiene first: `git diff main --stat -- docs/site_flow/` - the 307d owner-check PNGs (B_1-card, B_5-reload; A_1-card == main) ride on this branch from agent a's lane and differ from main. Before the run, restore the differing ones to MAIN's bytes (`git checkout main -- docs/site_flow/307d_B_1-card.png docs/site_flow/307d_B_5-reload.png`); after the run, if the owner-check tests re-encoded them, restore again - and NEVER commit them (they are not in my Touches; agent a owns the settle family 242/810/812/814/815/816).
2. Run the full suite: `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~7 min per agent a's 814/816 runs). Judge against the CURRENT main baseline **194P/1S/0F**.
3. The known pre-existing red: `tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser` (driver note 2026-10-13, red at a loop start, failed at its seed check). If it is red at my run time: record it in DECISIONS, do NOT absorb it, do NOT claim it (the 241-187/188 pattern). Any OTHER red outside agent a's owner-check family (roman, the other lanes): record, do not absorb, do not claim; new reds in MY lane (merge/build/export/review) are mine to fix before claiming done.
4. If green except the known red: tick box 4, set `Status: done`, commit my paths only, add a DECISIONS entry with the final counts.

**State of this machine (for the lead's sync to the owner's Mac, per Notes):** unchanged since it.207 - ALL 25 US sites built HERE, all 47 picture files fetched HERE, all 25 completed HERE (committed item files - nothing local left to sync beyond the gitignored build dirs): baltimore-q5092, boston-q100, chicago-q1297, cincinnati-q43196, cleveland-q37320, columbus-q16567, denver-q16554, detroit-q12439, indianapolis-q6346, kansas-city-q41819, louisville-q43668, memphis-q16563, milwaukee-q37836, minneapolis-q36091, nashville-q23197, new-orleans-q34404, new-york-q60, omaha-q43199, philadelphia-q1345, pittsburgh-q1342, portland-q6106, san-francisco-q62, st-louis-q38022, st-paul-q28848, washington-q61. Per site: data/sites/<id>/site.json (TRACKED) + data/sites/<id>/{dem.npy,dem_box.json,dem_credit.json} (gitignored) and web/data/sites/<id>/{relief.jpg, imagery.jpg, block_h.png, block_top.jpg} (gitignored); lidar_credit "USGS 3DEP", relief_clip_m ~1.2, 2000 m box, drawings 0, NO depictions.json.

**Team-mode hygiene on this branch (read before committing):**
- NEVER `git add -A`; commit only my Touches paths (+ my task file + DECISIONS.md). The worktree is clean apart from my own changes; HEAD may differ from main on docs/site_flow/307d_B_1-card.png and 307d_B_5-reload.png (agent a's lane - restore to MAIN's bytes, never HEAD's, around any owner-check run; PITFALLS tests/playwright).
- `web/data/review.json` `at` line: if a driver merge hits the known "at"-line conflict (PITFALLS 1444/1535), keep the newer `at` and verify the items list (the 25 US items must survive).

**Re-read:** none outstanding (the it.208 Re-read items were all consumed this session).
