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

(2026-10-15, iteration 207, agent c). **Boxes 1, 2, 3 DONE.** Remaining: the docs/sources.md rows,
the frozen-baseline re-baseline, and box 4 (full suite).

**BOX 3 done this session (all 25 US sites through the one-site line, `tools/site_done.py`, matcher
reachable at 127.0.0.1:8091):** baltimore first as a probe (22 s), then the remaining 24 in one batch
(19 m 09 s; one process per site; per-site log in data/merge/site_done.log, all rc=0, no FAILED). OUTCOME
EVERYWHERE: the matcher refused all 47 pictures - 46 with "not sure: 3-8 consistent points (need 10)"
(the confidence gate) and 1 (denver) "consistent points lie nearly on a line (spread 0.63, 10 px): the
scale is not pinned"; NO confident fit, hence NO platefit documents (data/db/platefits/ untouched), NO
overlays, drawings 0 -> 0 for all 25 (consistent with box 2: no old-map layer covers the US, the page
shows live aerial tiles). Every picture therefore landed in its site's review item: 25 NEW item files
under data/review/ (one per site, key = the site's first candidate's plan id, e.g.
nashville-q23197.c_a627153118b524e5.json carries all 5 nashville candidates; washington 6, new-york 7,
san-francisco 8), each entry with the batch's coarse anchor (coarse: true, ground relief/imagery,
scale_m_px from picture size), the files.jsonl evidence block, and the matcher's recorded `why`.
web/data/review.json re-published: 481 OPEN items written (the page lists open only) of 505 items in
the store (24 pre-existing resolved); +25 US items = the 481. The `at` stamp was re-stamped by the last
(washington) run - if the driver's next merge hits the known "at"-line conflict (PITFALLS 1444/1535),
keep the newer `at` and verify the items list (25 US must survive).
VERIFIED: tests/test_merge.py (11) + tests/test_site_done.py::test_site_done_line +
tests/test_fit_provenance.py::test_line_refuses_unmarked_non_auto_doc = 13/13 green (56 s) - the
three count-deriving tests read the open count from the live page, and store+page are consistent, so
the new items do not break them. git status after: M web/data/review.json + the 25 new item files +
data/merge/site_done.log - all in my Touches; nothing else (sites.json byte-unchanged, no 307d PNGs).

**State of this machine (for the lead's sync to the owner's Mac, per Notes):** ALL 25 US sites built
HERE, all 47 picture files fetched HERE, all 25 completed HERE (committed item files - nothing local
left to sync beyond the gitignored build dirs): baltimore-q5092, boston-q100, chicago-q1297,
cincinnati-q43196, cleveland-q37320, columbus-q16567, denver-q16554, detroit-q12439,
indianapolis-q6346, kansas-city-q41819, louisville-q43668, memphis-q16563, milwaukee-q37836,
minneapolis-q36091, nashville-q23197, new-orleans-q34404, new-york-q60, omaha-q43199,
philadelphia-q1345, pittsburgh-q1342, portland-q6106, san-francisco-q62, st-louis-q38022,
st-paul-q28848, washington-q61. Per site: data/sites/<id>/site.json (TRACKED) +
data/sites/<id>/{dem.npy,dem_box.json,dem_credit.json} (gitignored) and web/data/sites/<id>/
{relief.jpg, imagery.jpg, block_h.png, block_top.jpg} (gitignored), lidar_credit "USGS 3DEP",
relief_clip_m ~1.2, 2000 m box, drawings 0, NO depictions.json.

**Remaining steps (in order; every command under `.venv/bin/python`):**
1. docs/sources.md section 9: one row per US lead (236a: 4 city sites / 15 plan rows; 236b: 12 sites /
   23 views; 240: 4/4; 241: 5/5 - staged counts and documented drops from docs/lead_us_cities.md,
   docs/lead_us_birdseye.md, docs/lead_us_birdseye_batch4.md, docs/lead_us_birdseye_batch5.md and
   data/merge/log.jsonl) plus the merge summary (25 sites / 47 views, 0 refused) - the 211/230 pattern.
2. RE-BASELINE the frozen artifacts - SEMANTICS: the baseline is the PRE-PHASE set (the test's own
   docstring; 230's precedent), NOT "post-236c" as it.205's draft had (a post-build baseline makes
   test_new_sites_are_complete's non-empty `new` assertion fail):
   - data/merge/sites_premerge_baseline.jsonl <- the 508 pre-build entries (extract from the now-
     committed web/data/sites.json minus the 25 US ids, or from git history);
   - tests/test_merge.py::test_served_sites_grew_purely constant 499 -> 508 (+ its docstrings:
     "the 508 entries served before 236c's build: 230's 499 plus the nine Roman Scottish forts");
   - data/merge/plans_premerge_keys.jsonl <- the 1572 pre-export keys (same {"id","site"} shape).
3. BOX 4: full suite `tests/ -q -p no:cacheprovider` judged against the CURRENT main baseline
   (194P/1S/0F per 241 it.204) - never by weakening a frozen check. The owner-check pair is IN the
   suite: before any run that may re-encode the 307d PNGs, restore the differing ones to MAIN's
   bytes (hygiene below); after it, restore again and commit only my files.

**Team-mode hygiene on this branch (read before committing):**
- Agent a's 307d lane rides on this branch: the worktree is CLEAN (after my commit, only my files),
  but HEAD differs from main on docs/site_flow/307d_B_1-card.png and 307d_B_5-reload.png
  (A_1-card == main) - agent a is actively working the settle family (242/810/812/814/816).
  NEVER `git add -A`; commit only my Touches paths. The restore target for any owner-check run is
  always MAIN's bytes (`git diff main -- docs/site_flow/`), never HEAD's.
- A full-suite red outside this lane (the owner-check family, roman, the 817/818 lanes): record it,
  do not absorb it, do not claim (the 241-187/188 pattern); new reds in MY lane are mine to fix.

**Re-read:** tests/test_merge.py test_served_sites_grew_purely / test_new_sites_are_complete - the
re-baseline points of step 2 (the 499 constant, the two frozen artifacts, the non-empty `new`
assertion); docs/sources.md section 9 - the exact row shape 211/230 used for their leads (step 1
copies it); fit/review.py export - what the page file contains (OPEN items only; n_total counts the
whole store).
