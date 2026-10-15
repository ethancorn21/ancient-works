Status: done
# 236c: Consolidate the US cities into the page's data and build the sites
Depends on: 236a, 236b, 240, 241
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/sites/, data/db/platefits/, data/review/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, web/data/review.json, tests/test_merge.py, tests/fixtures/matchfit_station/ (added it.210: the 25 US review items drifted the 302f station fixture's data_review input hash - the 230/243 precedent re-records it in the drifting task; only the two fixture JSONs change, record.py and the test file stay untouched)

## Goal
Subtask of 236. Run the 211 consolidation (fit/merge.py globs every extras_/files_/classified_ staging file)
over 236a's and 236b's staging, build the new sites (aerial ground; 3DEP relief where a fort site has it),
and export plans.json so the new pictures appear on the page and in the fit queue.

## Acceptance criteria
- [x] fit/merge.py consolidates the two new staging sets; no duplicate site per QID; the merge test passes.
- [x] Every new US city site is built (web/data/sites/<id>/ exists, aerial tiles present) and listed in
      web/data/sites.json; plans.json lists their pictures.
- [x] Every new site ends with a fitted drawing or a review item (tools/site_done.py), as in 212.
- [x] The page loads with the new sites (server/serve.py), nothing that worked before breaks; full suite =
      baseline (it.210: 195P/1S/0F = main's 194P/1S/0F at 814's claim + this task's one new test, 196 collected).

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

(2026-10-15, iteration 210, agent c). **ALL FOUR BOXES TICKED; claimed `Status: done` this session.** If the
driver reopens this (e.g. a rejected claim), the state is fully settled: no build work remains, the only
residual is the claim gate itself.

**What it.210 did (box 4 = the full suite, plus the one fix it demanded):**
1. 307d PNG hygiene (agent a's lane): restored all ten to main's bytes before run 1 (2 differed: B_1-card,
   B_5-reload); after each of the two suite runs, restored all ten again. NEVER committed them (not in my
   Touches). HEAD still holds the stale re-encodes of the two; the driver's uncommitted-work commit aligns HEAD.
2. Run 1: full suite 193P/1S/2F of 196 (668.18 s). The 2 reds were BOTH
   `tests/test_matchfit_station.py` (confident + unsure) at the `_drift` precondition: the fixture's
   `data_review` input hash (sha256 over the sorted (name, sha256) list of `data/review/`) moved
   `0322cf07…` (recorded 2026-10-15T01:23Z, pre-US) -> `f11b8ccf…` (my 25 new US item files). A legitimate
   input change from my build, not a code regression.
3. Fix = the 230/243 precedent (243 was dropped and absorbed into 230, which added the same paths to its own
   Touches and re-recorded): I added `tests/fixtures/matchfit_station/` to my Touches line and ran
   `.venv/bin/python tests/fixtures/matchfit_station/record.py` against the live ELoFTR
   (127.0.0.1:8091, zju-community/matchanything_eloftr, RTX 5060 Ti). Verified by running: the 15 response keys
   per fixture are UNCHANGED (request bodies byte-identical - US sites never touch badbury's plan crop/ground/
   window); live-vs-frozen held-out 0 discrepancies; live best identical to the frozen one (six-inch-1st.webp
   x0.35, 22 inliers, corner 58.6 m, centre 2.9 m); offline replay identical; confident in-process run green
   (spread guard 0.228/195.7, site entry equal at score 1.45, review.json byte-identical, webp rebuilt);
   unsure variant seed 7 -> 8 inliers, page 482 open of 506. The only header fields that moved: recorded_at
   (now 2026-10-15T12:12:37Z), data_review, and unsure's review_counts (457/481 -> 482/506). record.py and the
   test file itself are untouched.
4. Station tests: 2/2 green (71.94 s). Run 2 (the claim run): **full suite 195P/1S/0F of 196, RC=0,
   1008.95 s** = main's baseline (194P/1S/0F at 814's claim, 999e5bf3) + my `test_no_qid_is_held_by_two_sites`
   (added by 2f7f7727 for box 1). The 2026-10-13 known red (`test_fit_queue::test_placement_gestures...`)
   did NOT reproduce - it passed on this tree.
5. Committed: the two refreshed fixtures, this task file, DECISIONS.md. Nothing else.

**If reopened:** the driver's claim gate runs its exact command (`.venv/bin/python -m pytest -q`, 900 s budget);
my run 2 took 1009 s under concurrent agent-a load (run 1 same day: 668 s, both all-green) - if a timeout rejects
the claim it is load, not code: re-run the suite in a quiet loop window and re-claim. No Re-read items outstanding.

**State of this machine (for the lead's sync to the owner's Mac, per Notes):** unchanged since it.207 - ALL 25
US sites built HERE, all 47 picture files fetched HERE, all 25 completed HERE (committed item files - nothing
local left to sync beyond the gitignored build dirs): baltimore-q5092, boston-q100, chicago-q1297,
cincinnati-q43196, cleveland-q37320, columbus-q16567, denver-q16554, detroit-q12439, indianapolis-q6346,
kansas-city-q41819, louisville-q43668, memphis-q16563, milwaukee-q37836, minneapolis-q36091,
nashville-q23197, new-orleans-q34404, new-york-q60, omaha-q43199, philadelphia-q1345, pittsburgh-q1342,
portland-q6106, san-francisco-q62, st-louis-q38022, st-paul-q28848, washington-q61. Per site:
data/sites/<id>/site.json (TRACKED) + data/sites/<id>/{dem.npy,dem_box.json,dem_credit.json} (gitignored) and
web/data/sites/<id>/{relief.jpg, imagery.jpg, block_h.png, block_top.jpg} (gitignored); lidar_credit
"USGS 3DEP", relief_clip_m ~1.2, 2000 m box, drawings 0, NO depictions.json.

**Team-mode hygiene (read before committing):**
- NEVER `git add -A`; commit only my Touches paths (+ my task file + DECISIONS.md).
- The ten `docs/site_flow/307d_*.png` are agent a's lane (242/810/812/813/814-816): after ANY test run restore
  them all to main's bytes (`for p in docs/site_flow/307d_*.png; do git show main:"$p" > "$p"; done`) and NEVER
  commit them; check the diff-vs-main, not just the working tree (PITFALLS tests/playwright).
- `web/data/review.json` `at` line: if a driver merge hits the known "at"-line conflict (PITFALLS 1444/1535),
  keep the newer `at` and verify the items list (the 25 US items must survive).
- If any future data/review/ change lands on main while this fixture is pinned, the station tests drift again:
  the fix is the same one-line re-record (`tests/fixtures/matchfit_station/record.py`, live ELoFTR required).

