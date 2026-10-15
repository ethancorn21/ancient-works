Status: open
# 236c: Consolidate the US cities into the page's data and build the sites
Depends on: 236a, 236b, 240, 241
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py

## Goal
Subtask of 236. Run the 211 consolidation (fit/merge.py globs every extras_/files_/classified_ staging file)
over 236a's and 236b's staging, build the new sites (aerial ground; 3DEP relief where a fort site has it),
and export plans.json so the new pictures appear on the page and in the fit queue.

## Acceptance criteria
- [x] fit/merge.py consolidates the two new staging sets; no duplicate site per QID; the merge test passes.
- [ ] Every new US city site is built (web/data/sites/<id>/ exists, aerial tiles present) and listed in
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

(2026-10-15, iteration 205, agent c). **Box 1 DONE and committed** (the scoped live merge over all
four US staging sets, verified; test_merge updated, 11/11 green). Boxes 2-4 remain: build, per-site
finish, sources.md, the re-baseline, full suite. Box 1 was ticked on its current wording ("the two
new staging sets"); the merge in fact covered all four (236a/236b/240/241) - the wording change is
in Proposed changes for the human/driver, as is the 25-total check: the measured total is 25
(4 + 12 + 4 + 5), no shortfall, so that proposed box holds as written.

**Done this session (all verified by running, on this checkout):**
- Live merge: `.venv/bin/python fit/merge.py merge --sources us_cities,us_birdseye,us_birdseye_batch4,us_birdseye_batch5`
  -> extras.jsonl 202->227 (+25), files.jsonl 1748->1795 (+47), classified.jsonl 1055->1102 (+47),
  refused 0; data/merge/log.jsonl now this run's snapshot (119 lines, all "merged": us_cities 34,
  us_birdseye 58, batch4 12, batch5 15). Committed.
- Verified: pure growth (pre-merge bytes a byte-identical prefix in all three canonical files);
  idempotent (second identical run: +0/0/0, all four files byte-identical); QID unique (172 unique in
  extras after; 0 held by two site ids, including the union over every extras_* staging file; the only
  QID the Wikidata catalog also holds, shotwick-q7502621, carries the catalog's own id in both).
- tests/test_merge.py (my file): STAGING now lists the four US sources in all three categories (the
  230 pattern); new test_no_qid_is_held_by_two_sites (the durable box-1 guard: extras + every
  extras_* staging one QID -> one site id; extras vs catalog same QID -> same id). File: 11/11.
- The four US modules' tests stayed green after the merge (22/22 with test_region): their --checks
  treat already-merged rows as no-ops BY DESIGN (the 222-228 pattern, written in before 236c ran).
- fit/merge.py unchanged (it already globs all staging prefixes and supports --sources; 230 did
  not change it either).

**Remaining steps (in order; every command under `.venv/bin/python`):**
1. BUILD the 25 sites: `data/merge/run_build.py <ids...>` - one process per site, resumable (a killed
   session resumes with the remaining ids; build_catalog skips already-built; --force only for a
   half-built site), appends to data/merge/build_sites.log; per site it runs build_catalog (3DEP DEM
   -> relief.jpg, USGS aerial copy -> imagery.jpg, block diagram, sites.json entry with lidar_credit)
   then set_drawings. Batch the ids across sessions and RECORD HERE which were built (Notes: the site
   dirs and data/raw are gitignored - the lead syncs them to the owner's Mac). The 25 ids (all new;
   none built yet at it.205): baltimore-q5092, boston-q100, chicago-q1297, cincinnati-q43196,
   cleveland-q37320, columbus-q16567, denver-q16554, detroit-q12439, indianapolis-q6346,
   kansas-city-q41819, louisville-q43668, memphis-q16563, milwaukee-q37836, minneapolis-q36091,
   nashville-q23197, new-orleans-q34404, new-york-q60, omaha-q43199, philadelphia-q1345,
   pittsburgh-q1342, portland-q6106, san-francisco-q62, st-louis-q38022, st-paul-q28848,
   washington-q61. (kind "town" -> 2000 m box; region "United States"; no old-map layers cover the
   US, so no depictions.json is expected - the page shows live aerial tiles.)
2. FETCH the 47 picture files: `pipeline/commons.py thumbs` (downloads every titled files.jsonl row
   whose local copy is missing: all 47 US rows at it.205, each data/raw/commons/<site>/
   <sha1(title)[:16]>.jpg from its `thumb` field; existing files skipped). ~47 x (fetch + 1 s) ->
   a few minutes.
3. `tools/export_plans.py` -> web/data/plans.json: the 47 rows reach the list through commons_rows()
   (p_birdseye 1.0 / p_photo 0 in the classified rows, local files now present). Pure growth -
   check every pre-existing (id, sites[0]) key survives and stays unique.
4. PER SITE `tools/site_done.py <sid>` (box 3): the matcher is reachable (127.0.0.1:8091, verified at
   it.205) so confident fits become matcher documents synced to overlays; the rest land in the
   site's review item with the matcher's recorded reason; the drawings count in sites.json and
   web/data/review.json refresh. Every new site must end with a fitted drawing OR a review item.
5. docs/sources.md section 9: one row per US lead (236a: 4 city sites / 15 plan rows; 236b: 12 sites /
   23 views; 240: 4/4; 241: 5/5 - staged counts and documented drops sourced from
   docs/lead_us_cities.md, docs/lead_us_birdseye.md, docs/lead_us_birdseye_batch4.md,
   docs/lead_us_birdseye_batch5.md and data/merge/log.jsonl) plus the merge summary (25 sites /
   47 views, 0 refused) - the 211/230 pattern for their leads.
6. RE-BASELINE the frozen artifacts (230's precedent; my Touches): data/merge/
   sites_premerge_baseline.jsonl <- the post-236c web/data/sites.json entries (524 = 499 + 25 if all
   build); update the constant `len(pre) == 499` in tests/test_merge.py::test_served_sites_grew_purely
   and its docstrings to the new count; data/merge/plans_premerge_keys.jsonl <- the post-236c
   (id, sites[0]) keys. (Box 4's "full suite = baseline" is judged against the CURRENT main baseline
   194P/1S/0F per 241's it.204, not by weakening any frozen check.)
7. Box 4: full suite `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`. The owner-check pair
   is IN the suite (tests/test_owner_check.py): before any run that may re-encode the 307d PNGs,
   restore the differing ones to MAIN's bytes (see hygiene below) so the run starts from the committed
   regime; after it, restore again and commit only my files.

**Team-mode hygiene on this branch (read before committing):**
- This branch carries agent a's 241/816-line 307d PNGs: at it.205 the worktree differed from main on
  B_1-card and B_5-reload (A_1-card == main) and HEAD differed from main on all three (the driver's
  023fa2cc re-committed older re-encodes on this branch; main never re-touched the files). NEVER
  `git add -A`; commit only my Touches paths. The R5 restore target is always MAIN's bytes
  (`git diff main -- docs/site_flow/` to list them), never HEAD's.
- If a full-suite red is outside this lane (the owner-check family, roman, the 817/818 lanes): record
  it, do not absorb it, do not claim (the 241-187/188 pattern); new reds in MY lane are mine to fix.

**Re-read:** fit/merge.py run_target - the identity rule (first row wins; norm = sorted-keys JSON) and
the evidence gate (titled files rows need rec evidence/1, kind != "none"); tools/site_done.py _fit -
the matcher-first flow and the review-item `why` recording; data/merge/run_build.py - the resume
contract (one process per site, --force semantics); tests/test_merge.py - the re-baseline points of
step 6.
