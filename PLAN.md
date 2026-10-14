# PLAN: red squares everywhere — an old drawing on every built site

GOAL.md, in one line: every built site in `web/data/sites.json` either has an old drawing of the structure
fitted onto today's ground (a red square on the map), or a review item a human can finish by dragging in
under a minute; acceptance of automatic fits is decided by a validated numerical gate; every picture is
tied to its place with machine-checkable evidence; and the map keeps growing with new sites that come with
their own old pictures.

## Current state (2026-10-13)

- 499 built sites (up from 384: the growth leads added sites, 211); **57 of them have a fitted drawing**:
  22 hand fits (the human's — the reference nothing may ever change; the golden's 41 lines) and **49
  matcher fits on 35 sites** (35 MatchAnything-RoMa + 14 ELoFTR; 37 matched against an old survey sheet
  already placed on the map, 12 against the LiDAR relief, 0 against the aerial photograph).
- The page (`web/index.html`, served by `server/serve.py`) renders the built sites, the fitted overlays,
  live LiDAR relief, the plate-fitting tool and the review section; 456 review items in the open queue
  (`web/data/review.json`).
- 1510 candidate pictures in `web/data/plans.json` (the old books plus the Commons harvest); the fitted
  minority above, the rest unfitted or in the queue.
- Every fitting method before the matcher failed its own test: fully automatic fitting (wall extraction
  + wide search, `docs/autofit.md`) 0/5; the vision-model batch fit (203a/203b, 2026-10-11, ~100 fits)
  was the model's fabricated pattern class (301; the 306a-f look audits found nearly all of them wrong
  and 212b deleted them); the hand-built ink fit (302a/302b) landed 231-2204 m off on the held-out hand
  fits. The pretrained cross-modality matcher (`fit/matchfit.py`, the lead, 2026-10-11) is the first
  method whose placements are right where it is confident: it places about **1 picture in 10**, an old
  drawing matching an old survey sheet far better than LiDAR shading.
- GOAL.md changed a third time (2026-10-13 23:39; the driver reopened this task): point 2 now names the
  image matcher as the ONLY automatic placement and retires the vision-model fitting pass (owner:
  "the image matching model should be the only thing that's doing the matching"); its numbers record
  the 49 matcher fits and the ~1-in-10 yield. The 2026-10-10 changes (the model-fitting point 2, the
  artists' lead) stand as history; assumption 9 (the owner's-copy survey-sheet colouring) is unchanged.
  This session (iteration 157) finished re-checking the plan against that change.

## Architecture

The new work is a pipeline that turns candidate pictures into accepted fits or review items. New modules
live in **`fit/`** (a new top-level directory); they import the existing shared helpers (`pipeline/aw.py`
for Mercator math, `pipeline/plan_fit.py` for the similarity solver, `pipeline/llm.py` for the model)
**read-only** and never edit other
modules' code. The new directory exists so the parallel-work rule (no two in-flight tasks touch the same
file) can hold: the seeded gate task 001 declares `pipeline/` and `tools/` in its `Touches`, so nothing
else in wave 1 may write there.

```
sources                      picture rows               candidates              fit decision
─────────                    ────────────               ──────────              ────────────
8 old books (data/books/)    data/books/index.jsonl ─┐
Commons harvest (pipeline/   data/commons/files.jsonl┼→ web/data/plans.json ─┐
commons.py, tools/           (+ classified.jsonl)    │   (existing exporter)  │
per-lead source modules      each row gains an       │   rows matched to a    │
fit/src_*.py (204-210)       "evidence" field:       │   site by their        │
  one module, one lead       P373 category / P180 /  │   "sites" column       │
  file → QID table,          caption+coords,         │                        │
  hand-checked QIDs          machine-checkable       │                        │
                             (fit/evidence.py, 200)  │                        │
                                                     ▼                        ▼
                                    fit/propose.py (202): the STARTING POINT per (site, picture): the
                                    scale bar / north arrow / site-centre anchor plus a few pairs -
                                    a starting point, never a fit (GOAL point 2)
                                                     ▼
fit/matchfit.py (the lead, 2026-10-11): the ONLY automatic placement. The plan's map-box crop against
every georeferenced ground image of the site - the LiDAR relief (relief.jpg), the aerial photograph
and the old survey sheets already placed on the map (depictions kind "map": OS six-inch / one-inch,
Cassini, Etat-Major) - whole and as centred windows (the site box is often 3-4x the plan's extent);
MatchAnything-ELoFTR first (inliers >= 10, rotation within 30 deg of north, the near-line spread
guard), then MatchAnything-RoMa on the pictures ELoFTR is not sure of (match fraction >= 0.4, the
same spread guard). RANSAC similarity on the matched points; a document is written only when both
the matcher's judge AND the frozen 001 gate accept (238)
                                                     ▼
                                    the gate (001, validated on held-out hand fits)
                                    accept ──► data/db/platefits/<site>.<plan>.json (auto, fitter: matcher, gate score)
                                    judge refusal / gate refusal / LiDAR rule ──► data/review/<site>.<plan>.json (fit/review.py, 201)
                                                     │
                              the review queue is for the gate's and the judge's refusals, the
                              pictures the matcher could not place and sites with no picture
                              found (GOAL points 1-2) - not a plan for every site. The human
                              opens the item on the page (web/review.js, 201), drags the pairs,
                              saves through the fit tool. The Qwen models never appear in this
                              path: they find, classify and tie pictures and write code (GOAL
                              point 2, 2026-10-13; the lead note on 212). Automatic placement
                              runs on LiDAR sites only (239, assumption 10): a site whose
                              georeferenced ground is the aerial photograph alone keeps its
                              review items for the human. (The batch's vision-model fitting
                              pass - fitkit sheet -> model -> pairs -> gate, 203a/203b - is
                              RETIRED by 239; the batch keeps the queue upsert, the no-picture
                              record and the report.)
                                                     ▼
                          platefits document (human-saved) → overlay → red square → item resolved
```

Page-facing flow: `fit/merge.py` (211) consolidates the per-source rows, runs the existing
`build_catalog.py`/`export_plans.py`, so new sites and pictures appear in `web/data/sites.json` and
`web/data/plans.json` — the page renders them with no page change. `fit/cover.py` (212) re-runs the
matcher-first loop over the new material (the lead note on 212: the loop's fit is the matcher, the
vision model is refused at its CLI), builds the page's review list, and writes the final report.

Module map (one module per task, so agents never collide):

| module | task | job |
|---|---|---|
| (gate module of 001's choosing, in `pipeline/` or `tools/`) | 001 | accept/reject a fit by numbers, validated on held-out hand fits |
| `fit/evidence.py` | 200 | record + offline-check the place-tie evidence of every picture row |
| `fit/review.py` | 201 | the review queue: item format, page section (`web/review.js`), resolution |
| `fit/propose.py` | 202 | the starting point per (site, picture) the model's fit pass begins from: scale / north / centre anchor plus a few pairs - a starting point, never a fit (GOAL point 2) |
| `fit/batch_us.py` / `fit/batch_eu.py` | 203a / 203b (done) | the 2026-10-11 vision-model fitting loop over the built sites; its model pass (fitkit sheet -> model -> pairs -> gate) is RETIRED by 239 (GOAL 2026-10-13): what remains is the review-item upsert (the matcher's recorded reason, never a model's), the no-picture record and the report (`docs/batch_us.md` / `docs/batch_eu.md` stay the historical record of the 203 runs) |
| `fit/matchfit.py` | the lead (2026-10-11); 302a/302b/302e (the method family and the held-out measurements), 302f (the station end to end, no network), 302g (the Stonehenge run), 238 (the gate on its fits) | the only automatic placement: MatchAnything RoMa/ELoFTR correspondences between the plan and the site's georeferenced ground images -> RANSAC similarity -> the judge (inliers/fraction, rotation, spread) -> the frozen 001 gate (238) -> a document (`fitter: matcher`) or the review item with the reason. (The lead also keeps exploratory companions outside the line: `matchfit2.py` (two-stage: coarse hit, then windows) and `matchfit_queue.py` (accept-rule sweep).) |
| `fit/src_van_deventer.py`, `fit/src_kip.py`, `fit/src_mackenzie.py`, `fit/src_roman.py`, `fit/src_limes.py`, `fit/src_wiltshire.py`, `fit/src_numancia.py`, `fit/src_artists.py` | 204-210, 213 | the eight growth leads: find, verify age + free access, tie, stage rows in its own staging files and its own `docs/lead_<name>.md` (book leads write per-book artifacts only; 213 uses the book machinery only if Civitates/Merian turn out to be IA books) |
| `fit/merge.py` | 211 | consolidate per-source rows into the canonical files; rebuild the book index (the shared one, once); build the new sites; refresh the page data; consolidate the lead statuses into `docs/sources.md` |
| `fit/src_<lead>.py` (check/stage guards only) | 222-228 (one per module: 222 van_deventer, 223 kip, 224 mackenzie, 225 limes, 226 numancia, 227 stukeley, 228 artists) | accept the staging rows once 211 has merged them: a staged row identical to its canonical twin is an already-merged no-op, a different row with the same key still fails loud, known-site self-references are not collisions |
| `fit/cover.py` | 212 | targeted picture search for the still-uncovered sites; the only page-facing sync; the final report (`docs/batch.md`) and the current 20-sample |

## Tech choices (and why)

- **The existing stack, unchanged**: Python 3.12 with the pinned deps (`requirements.in` → `requirements.txt`,
  hashed); numpy/scipy/PIL for geometry and images, pyproj/rasterio for geodata; vanilla JS + vendored
  MapLibre for the page. No new framework or service. Reason: the pipeline already does everything this
  project is (georeferencing old plates, matching to ground, building site entries); the failed autofit was
  a search-width failure, not a stack failure, and point-pair fitting is proven by 25 fits.
- **Web Mercator similarity fit** (existing `plan_fit.similarity`: conformal, so a similarity in Mercator
  metres is a similarity on the ground). No new fitting algorithm. The gate (001) scores fits, it does not fit.
- **The image matcher fits, the gate decides** (GOAL point 2, rewritten by the owner 2026-10-13). The only
  automatic placement is fit/matchfit.py (MatchAnything RoMa/ELoFTR) against a georeferenced ground image, on
  LiDAR sites only. The local vision model never places a drawing or writes point pairs: the model fitting pass
  of fit/batch_us.py / fit/batch_eu.py is retired (its ~100 fits of 2026-10-11 failed the 306 look audits).
- **Evidence as row fields, checked offline.** Wikidata/Commons metadata is fetched in the working phase
  and stored in the row (`"evidence"`); the check pass re-verifies rows from stored fields only, so tests
  never touch the network (Commons and Wikidata are rate-limited and flaky by nature).
- **Per-lead source modules with hand-checked `file → QID` tables** — the proven pattern of
  `pipeline/sources.py` (name searches give the wrong place: Barnard Castle the town, Richard's Castle the
  village, Scotney the 19th-century house). Each lead is one module; a lead that cannot be verified free
  and old enough is documented and dropped, not guessed.
- **Per-source staging files, consolidated once.** Parallel source tasks would otherwise collide on
  `data/catalog/extras.jsonl`, `data/commons/files.jsonl`/`classified.jsonl`, `web/data/plans.json` and
  `web/data/sites.json`. Each source task writes only its own `extras_<source>.jsonl` / `files_<source>.jsonl`
  / `classified_<source>.jsonl`; 211 consolidates them into the canonical files (GOAL.md's named
  destinations) in a single task, then builds.
- **The batch writes fit documents and review items only.** The page-facing sync (site overlays, the
  `drawings` counts in `sites.json`, the review list) is done by the one task (212) that runs the existing
  `plan_fit` sync over the new documents — so two tasks in the same wave never write the same file.
- **Tests**: pytest; the real `serve.py` on `--port 0` against a temp copy of the tree (session fixture in
  `tests/conftest.py`); golden files in `tests/golden/`; no network in tests; one `tests/test_<name>.py` per
  task; `conftest.py` is owned by the planning task (000) — shared fixtures are requested, not edited.

## Assumptions (where GOAL.md is silent)

1. **Human saves bypass the gate.** The gate constrains automatic fits; a human who corrects and saves a
   review item is the authority (that is what the review queue is for). GOAL's 18/20 human sample check
   applies to the *automatically accepted* fits, listed in the batch report with a fixed recorded seed.
2. **"Under a minute" means one screen:** open the item → the existing fit tool opens with the picture and
   the proposed pairs already placed → drag → save. No modal chains, no extra pages.
3. **A site with no findable picture** (even after the targeted search of 212) still gets a review item,
   marked "no picture found", recording exactly what was searched; the human decides (drop the site, or
   name a source). GOAL's "with its best candidate pictures" is read as: candidates whenever they exist.
   Since the GOAL change of 2026-10-10 the queue is explicitly overflow (gate refusals, pictures the model
   could not fit, no-picture sites), not a plan for every site; this is the one case where a site ends
   with an item without a model fit having been attempted.
4. **The 150-year rule** applies to survey sheets and survey aerials only; plans, drawings and views of the
   structure are exempt (GOAL says so), including modern published drawings such as the German Limes
   fort plans — the age of each picture is recorded on its row either way.
5. **The map only grows.** Built sites are never removed; the 25 hand fits and their sites are the
  permanent reference (golden test). Test assertions use `>=`, so merged work cannot break them.
6. **Tests are hermetic**: all network (Commons, Wikidata, Internet Archive, DEM/imagery services) happens
   in the working phase; tests run on the temp tree copy plus the fixed data committed in the repo.
7. **The German Limes lead is the least certain** of the seven: if no free machine-readable fort plans
   exist, 208 documents that in `docs/sources.md` and is dropped — the other six leads stand on their own.
8. **Page quirk noted, fixed in 201's scope**: two plan rows can share an `id` when one picture depicts two
   sites (Larned history for Avebury+Stonehenge, Mayburgh-1769 for Mayburgh+King Arthur's Round Table); the
   page's `P.byId` keeps only the last of such a pair. 201 keys the fit tool by (id, site).
9. **The owner's copy colours survey-sheet-only sites.** Since 2026-10-10 the owner's map also colours
   sites whose only overlay is a survey sheet 150 or more years old. GOAL states this does not change this
   goal (survey sheets are not drawings; the number to grow is the count of fitted drawings), so this
   project does not add that colouring (out of scope).
10. **The LiDAR-only ruling, read with the sentence before it.** The 2026-10-13 owner ruling "automatic
   fitting runs on LiDAR sites only" is read together with the preceding one (the ground image is "the
   LiDAR relief, or an old survey sheet already placed on the map"): the matcher may place on a site that
   has the LiDAR relief, and it may also place against an old survey sheet already placed on the map —
   even when the site has no LiDAR (5 of the 49 current fits are exactly that, French sites whose only
   placed ground is the Etat-Major sheet). What is excluded is a site whose georeferenced ground is the
   aerial photograph alone — no LiDAR relief and no placed sheet: its pictures keep their review items
   for the human. On this VM the exclusion is a guard, not a cleanup: 425 sites have a relief, 0 are
   aerial-only, 74 have neither image yet. (239 implements it; the stricter reading — the aerial never a
   placement ground, even on LiDAR sites — would be a one-line change in `fit/matchfit.grounds`.)
11. **The matcher's yield is a property of the ground image, not of re-running.** The matcher is
   deterministic: the same picture against the same ground image gives the same answer, so re-running it
   on a picture it already refused cannot place it. A better yield needs a better ground image (more and
   better placed survey sheets) or a better matcher — never a language model placing points, and never
   loosening the frozen judge or gate thresholds.

## Out of scope

- Re-running the fully automatic fitting bet as it stands (`docs/autofit.md`, 0/5). A search may exist as
  the gate's null model (001 decides) or as a coarse starting point (202) — never as the accepted fit.
- The owner's-copy colouring of sites whose only overlay is a survey sheet 150 or more years old (GOAL
  states it does not change this goal; assumption 9).
- The Finder (searching for earthworks nobody has recorded) and the Amazon/EBA Finder work; public
  publishing; ground photographs; historic aerials; anything touching the private Finder/Amazon data
  (`web/data/scan`, `web/data/amazon`, `data/finder`, `data/db/marks|surveyseen|verdicts`); changing or
  deleting the existing hand fits.
- Re-running the matcher on pictures it already refused, or loosening the matcher's judge / the gate's
  thresholds, as a yield strategy (both frozen; assumption 11). The ~1-in-10 yield is a property of the
  ground images: an old drawing matches an old survey sheet far better than LiDAR shading.

## Task map (every point of GOAL.md)

| GOAL.md point | delivered by |
|---|---|
| 1. every built site has a fitted drawing **or a ready review item** | 201 (the queue + page), the matcher station on the one-site line (`fit/matchfit.py`, wired by 300/301, tested by 302f, run on Stonehenge by 302g), 204-210 + 213 (pictures for the new sites), 211 (build), 212 (final cover: the matcher-first loop; no site left without a fit or an item) |
| 2. the image matcher does the fitting, never a language model (the only automatic placement is `fit/matchfit.py`: MatchAnything RoMa/ELoFTR against a georeferenced ground image; a fit is kept only when enough matched points agree; the Qwen models find, classify and tie pictures and write code, never place; the batch's model fitting pass is retired; automatic fitting runs on LiDAR sites only; the queue receives what the matcher could not place) | `fit/matchfit.py` (the lead's module), 302a/302b/302e (the method family and its held-out measurements, done), 302f (the matcher station end to end, no network), 302g (Stonehenge on the matcher-first line: the run, the browser check, the plain statement), 238 (every matcher fit passes the frozen 001 gate), 239 (the vision-model fitting pass retired: no model in the batch, no model pass in the line; the LiDAR-only rule; the queue records the matcher's reasons), 212 (the cover loop is matcher-first), 201 (the queue) |
| 3. a fit is accepted by numbers via a gate validated on held-out hand fits; 18/20 of a 20-sample of auto fits must be right | 001 (the gate), 238 (every matcher fit passes it: the matcher's own judge is not the gate), 212 (`docs/batch.md` keeps the seeded 20-sample of the automatically accepted fits — now the matcher's — current until 999 checks it) |
| 4. every picture tied to its place with machine-checkable evidence in its row | 200 (the checker), 204-210 + 213 (each lead records the evidence of its rows), 211 (consolidates) |
| 5. the map grows: the eight leads, each verified before use | 204 Van Deventer, 205 Kip, 206 Mackenzie p. 212, 207 Roy/Horsley/Maclauchlan, 208 German Limes, 209 Hoare/Stukeley/Petrie, 210 Numancia, 213 artists' views (Leonardo's Imola, Barbari's Venice, Braun & Hogenberg, Merian); 211 builds them |
| 6. the page shows what changed without breaking anything | 201 (review section, only page change), 211 (new sites/pictures via the existing data files), 212 (the fit documents become overlays and drawings counts), every task's test re-runs the served page |

## Waves (all tasks of a wave can run at once; two agents pick from each wave)

| wave | tasks | why they can run together |
|---|---|---|
| 1 | **001** (gate), **200** (evidence), **201** (review queue), **202** (proposals) | 001 writes `pipeline/`/`tools/`/`docs/gate.md`; the other three write `fit/`, `web/review.js` (+ one script tag in `index.html`) and their own test files - no file is shared. (001 declares `tests/` as a directory; every task's tests are separate `test_*.py` files, `conftest.py` is owned by 000 - the driver's replay keeps the directory apart where it must.) |
| 2 | **203a** (batch: US built sites), **204** (Van Deventer), **205** (Kip), **206** (Mackenzie p.212), **207** (Roman books), **210** (Numancia), **213** (artists' views) | 203a writes `fit/batch_us.py`, US docs/items, the hand-fit golden hashes; each source writes only its own module + its own staging files + its own `docs/lead_<name>.md`. 207 is the only unconditional book-machinery user of this wave; 213 uses the book machinery only if Civitates/Merian turn out to be IA books, then per-book files named by the book's ia id, declared in its own `Touches` first (the 208 pattern). 206 depends on 001 (its identification must pass the gate). |
| 3 | **203b** (batch: rest of world), **208** (German Limes), **209** (Wiltshire) | 203b writes `fit/batch_eu.py`, non-US docs/items; 208 and 209 write only their own staging/modules. 209 is the only book-machinery user left: 207 and 209 share the `data/books/` directory (in practice only per-book files, named by the book's ia id), so they never run together; 208 uses the book machinery at all only if the Limes reports turn out to be IA books - then it declares the exact per-book paths in its own `Touches` line first. |
| 4 | **203** (the parent, on return), **211** (merge & build), **222-228** (the seven source-check post-merge fixes) | the parent's remaining work is one test file (the coverage check over the original site set); 211 alone writes the canonical data files, the rebuilt shared book index (`index.jsonl`, `validation.json`), `web/data/sites.json` + `plans.json` and `docs/sources.md`. 222-228 each touch only their own module + test (211's live merge turned their guards red - it depends on all seven; they can all run at once and on main they only extend green tests). |
| 5 | **212** (final cover, sync & report) | the last task: everything it needs is done; it alone runs the page-facing sync (per-site depictions, the `drawings` counts, `web/data/review.json`) and owns `docs/batch.md`. |

Most waves have two or more tasks (4 / 7 / 3 / 2 / 1). A task with unmet `Depends on:` simply waits; the
driver hands each agent whatever else is open. The book leads (207/209) are in separate waves only
because they share the `data/books/` directory, not because one needs the other's output.

### The remaining work (2026-10-13: the matcher's line and the retirement)

Waves 1-5 above are history (done or in their closing steps). The queue's tail, after the GOAL change of
2026-10-13:

| wave | tasks | why they can run together |
|---|---|---|
| 6 | **302f** (the matcher station end to end, no network), **302g** (Stonehenge on the matcher-first line), **235** (the placement test's pick mirrors the page's filter), **212** (in flight, closing on 235) | 302f writes only its new test + fixtures; 302g only its docs/data/web records; 235 only its own test file; 212 its own module — no file shared |
| 7 | **238** (every matcher fit through the frozen 001 gate) | waits on wave 6: it changes what `matchfit.run` writes, and 302f/302g record the current behaviour of the line. One module (`fit/matchfit.py`) plus its own new test and one appended `docs/gate.md` section |
| 8 | **239** (the vision-model fitting pass retired: the batch's model path and the line's second pass) | waits on 238 (it consumes the matcher's per-candidate refusal reasons) and on 212 (in flight: `fit/cover.py`'s loop still forwards the batch's `--model-json`; 212's closing step lands first). The batch, the line, `cover.py`'s forwarding and their tests are one module for this change; `docs/site_flow.md`'s step 1 is reworded (append-only for the other tasks' sections) |

## Test policy

- Command: `python3 -m pytest -q` (the driver builds `.venv` from the hashed `requirements.txt` first).
- No test binds a fixed network port: the server fixture uses `--port 0` and parses the bound address.
- No test writes outside the project and the system temp dir: the session fixture copies
  `web/`, `server/`, `data/` (minus the 1.9 GB `data/raw/`) into a temp tree and the server serves that;
  tests read the checkout only.
- No test needs the network: evidence and fit checks run on stored row fields and in-repo images
  (the six tracked hand-fit sites provide real ground); golden files pin the reference state.
- No test calls the model server: the batch loop's model step is an injectable function (the working
  phase calls `pipeline/llm.py` on the fitkit sheet; tests supply a fixed recorded answer).
- Each task adds exactly one `tests/test_<name>.py`; shared fixtures go through a DECISIONS request to the
  owner of `conftest.py`, never an edit of it by a second agent.

## Deviations from GOAL.md

- **Task 001 box 2 - wrong fits the gate accepts: the owner's "at most 1 in 20" vs the measured
  1 in 8.** GOAL point 3 says: auto-acceptance goes through a gate validated on the held-out hand
  fits, and the human checks a random 20-fit sample of auto-accepted fits, at least 18 of them
  right. The project does: the registered gate (docs/gate.md section 2, one-shot measured in
  section 9) accepts 4 of 32 deliberate wrong placements - all 15% scale errors (1 in 8, not 1 in
  20) - and rejects every moved, rotated and cross-site placement (0 of 24). A 15% scale residual
  pattern is structurally indistinguishable from a true sloppy fit's own scatter at n = 3-6
  anchors (gate.md section 7; the 12 dev documents show the same 2 of 12), so no re-tuned
  threshold on the spent held-out set can remove the misses without also refusing true fits (the
  registration, section 6, forbids that re-tuning). Evidence the human would not notice the
  difference in production: the model fits by matching features, so a pure 15% scale error is the
  rarest miss class, and the 1-in-8 rate is the worst case of the recipe applied to every
  held-out document, not the model's output distribution; and the checks GOAL point 1 and 3 build
  into the design (everything the gate refuses goes to the review queue; the 20-fit human sample
  must be 18/20 right) are exactly the checks that would catch a production wrong-fit rate at
  that level. Ruling applied (owner, 2026-10-11, .agent/asks/001.md): (a) - accept the gate as
  measured; box 2 re-worded to the registered contract ("at most 1 in 20, or the measured
  numbers are recorded in docs/gate.md section 9 and the review queue absorbs the difference")
  and the task is done.
