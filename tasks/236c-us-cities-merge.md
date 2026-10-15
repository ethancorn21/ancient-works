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
- [ ] Every new site ends with a fitted drawing or a review item (tools/site_done.py), as in 212.
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

(2026-10-15, iteration 206, agent c). **Boxes 1 and 2 DONE** (merge it.205; build + fetch + plans
export this session, all verified by running). Remaining: box 3 (per-site completion) and box 4
(full suite).

**State of this machine (for the lead's sync to the owner's Mac, per Notes):** ALL 25 US sites built
here, all 47 picture files fetched here: baltimore-q5092, boston-q100, chicago-q1297, cincinnati-q43196,
cleveland-q37320, columbus-q16567, denver-q16554, detroit-q12439, indianapolis-q6346, kansas-city-q41819,
louisville-q43668, memphis-q16563, milwaukee-q37836, minneapolis-q36091, nashville-q23197,
new-orleans-q34404, new-york-q60, omaha-q43199, philadelphia-q1345, pittsburgh-q1342,
portland-q6106, san-francisco-q62, st-louis-q38022, st-paul-q28848, washington-q61. Per site:
data/sites/<id>/site.json (TRACKED - committed here) + data/sites/<id>/{dem.npy,dem_box.json,
dem_credit.json} (gitignored) and web/data/sites/<id>/{relief.jpg, imagery.jpg, block_h.png,
block_top.jpg} (gitignored), lidar_credit "USGS 3DEP", relief_clip_m ~1.2, 2000 m box, drawings 0,
NO depictions.json (no old-map layer covers the US - the page shows live aerial tiles).

**Done this session (all verified by running):**
- Built all 25 with `data/merge/run_build.py` (baltimore as a probe: 14 s; then the remaining 24 in
  one batch: 6 m 22 s; one process per site, log appended to data/merge/build_sites.log, all rc=0,
  no NOT BUILT/FAILED in the run). web/data/sites.json 508 -> 533, PURE GROWTH (the 508 HEAD entries
  byte-identical in content, zero changed; the 9 non-baseline ones in HEAD are Roman Scottish forts:
  ardoch, carriden, cilurni, congavata, kirkintilloch, luguvallium-q71551754, petriana, tunnocelum,
  virosidum).
- `pipeline/commons.py thumbs`: a read-only probe (rows() + local()) showed exactly 47 missing-with-
  thumb (new-york 7, washington 6, san-francisco 8, nashville 5, the other 21 one each) - all 47
  fetched in 1 min, 0 remaining (the one missing-without-thumb row is skipped by design).
- `tools/export_plans.py`: web/data/plans.json 1572 -> 1619, EXACTLY +47 US rows (33 birdseye p=1.0,
  14 plan p=1.0, 0 photo), zero lost keys, no duplicate (id, sites[0]), all 1510 frozen pre-merge
  keys survive. The DecompressionBombWarnings (a few ~90-110 Mpx book scans) are pre-existing/harmless.
- tests/test_merge.py 11/11 green both before and after the export (the 499-baseline pure-growth
  check passes because the build touched no baseline entry; new-sites completeness passes for all 34
  non-baseline sites including the 25 US ones).
- serve.py smoke on an ephemeral port: the page serves 533 sites (25 US-region) and 1619 plans;
  baltimore's imagery.jpg 200.

**Remaining steps (in order; every command under `.venv/bin/python`):**
1. BOX 3: `tools/site_done.py <sid>` per site for all 25 (matcher reachable, 127.0.0.1:8091): a
   confident fit becomes a matcher document in data/db/platefits/ + a synced overlay; the rest land
   in the site's review item (data/review/<sid>.<lead>.json) with the matcher's recorded `why`; the
   drawings count in sites.json and web/data/review.json refresh. Every new site must end with a
   fitted drawing OR a review item. Its writes land in the paths added to my Touches this session:
   data/db/platefits/, data/review/, web/data/review.json. One site per run; covered pictures are
   never re-fitted; batch across sessions if needed.
2. docs/sources.md section 9: one row per US lead (236a: 4 city sites / 15 plan rows; 236b: 12 sites /
   23 views; 240: 4/4; 241: 5/5 - staged counts and documented drops from docs/lead_us_cities.md,
   docs/lead_us_birdseye.md, docs/lead_us_birdseye_batch4.md, docs/lead_us_birdseye_batch5.md and
   data/merge/log.jsonl) plus the merge summary (25 sites / 47 views, 0 refused) - the 211/230 pattern.
3. RE-BASELINE the frozen artifacts - SEMANTICS: the baseline is the PRE-PHASE set (the test's own
   docstring; 230's precedent), NOT "post-236c" as it.205's draft had (a post-build baseline makes
   test_new_sites_are_complete's non-empty `new` assertion fail):
   - data/merge/sites_premerge_baseline.jsonl <- the 508 pre-build entries (extract from the now-
     committed web/data/sites.json minus the 25 US ids, or from git history);
   - tests/test_merge.py::test_served_sites_grew_purely constant 499 -> 508 (+ its docstrings:
     "the 508 entries served before 236c's build: 230's 499 plus the nine Roman Scottish forts");
   - data/merge/plans_premerge_keys.jsonl <- the 1572 pre-export keys (same {"id","site"} shape).
4. BOX 4: full suite `tests/ -q -p no:cacheprovider` judged against the CURRENT main baseline
   (194P/1S/0F per 241 it.204) - never by weakening a frozen check. The owner-check pair is IN the
   suite: before any run that may re-encode the 307d PNGs, restore the differing ones to MAIN's
   bytes (hygiene below); after it, restore again and commit only my files.

**Team-mode hygiene on this branch (read before committing):**
- Agent a's 307d lane rides on this branch: the worktree is CLEAN, but HEAD differs from main on
  docs/site_flow/307d_B_1-card.png and 307d_B_5-reload.png (A_1-card == main) - agent a is actively
  working the settle family (242/810/812/814/816). NEVER `git add -A`; commit only my Touches paths.
  The restore target for any owner-check run is always MAIN's bytes (`git diff main --
  docs/site_flow/`), never HEAD's.
- A full-suite red outside this lane (the owner-check family, roman, the 817/818 lanes): record it,
  do not absorb it, do not claim (the 241-187/188 pattern); new reds in MY lane are mine to fix.

**Re-read:** tools/site_done.py _fit - the matcher-first flow and the review-item `why` recording
(the next step goes through exactly this); fit/review.py item_path - the item file layout
(data/review/<site>.<lead>.json); tests/test_merge.py test_served_sites_grew_purely /
test_new_sites_are_complete - the re-baseline points of step 3 and the non-empty `new` assertion.
