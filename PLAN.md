# PLAN: red squares everywhere — an old drawing on every built site

GOAL.md, in one line: every built site in `web/data/sites.json` either has an old drawing of the structure
fitted onto today's ground (a red square on the map), or a review item a human can finish by dragging in
under a minute; acceptance of automatic fits is decided by a validated numerical gate; every picture is
tied to its place with machine-checkable evidence; and the map keeps growing with new sites that come with
their own old pictures.

## Current state (2026-10-10)

- 384 built sites; **25 fitted drawings** (19 of them from 20 documents in `data/db/platefits/`, the human's
  hand fits — the reference nothing may ever change).
- The page (`web/index.html`, served by `server/serve.py`) already renders built sites, red squares for the
  fitted ones, live LiDAR relief, and a working plate-fitting tool (click pairs → PUT `/api/db/platefits/…` →
  `pipeline/plan_fit.py` builds the overlay → the page polls it).
- 1166 candidate pictures in `web/data/plans.json` (8 old books indexed in `data/books/`, 1490 harvested
  Commons rows in `data/commons/`); 25 are fitted, the rest are not.
- Fully automatic fitting (wall extraction + wide search) **failed its pre-registered test, 0/5**
  (`docs/autofit.md`); fitting by matching point pairs is the method that works (25 hand fits prove it).
- Seven named growth leads in GOAL.md (Van Deventer's remaining 64 towns, Kip's bird's-eye views, Mackenzie
  p. 212, the Roman books, the German Limes reports, Hoare/Stukeley/Petrie for Wiltshire, Numancia's
  excavation plans), none of them verified as free and machine-readable yet.

## Architecture

The new work is a pipeline that turns candidate pictures into accepted fits or review items. New modules
live in **`fit/`** (a new top-level directory); they import the existing shared helpers (`pipeline/aw.py`
for Mercator math, `pipeline/plan_fit.py` for the similarity solver) **read-only** and never edit other
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
                                    fit/propose.py (202): proposed point pairs per (site, picture)
                                                     ▼
                             pipeline/plan_fit.py (existing similarity solver)
                                                     ▼
                                    the gate (001, validated on held-out hand fits)
                                    accept ──► data/db/platefits/<site>.<plan>.json (auto, with score)
                                    reject ──► data/review/<site>.<plan>.json  (fit/review.py, 201)
                                                     │
                              human opens the item on the page (web/review.js, 201),
                              drags the proposed pairs, saves through the existing fit tool
                                                     ▼
                          platefits document (human-saved) → overlay → red square → item resolved
```

Page-facing flow: `fit/merge.py` (211) consolidates the per-source rows, runs the existing
`build_catalog.py`/`export_plans.py`, so new sites and pictures appear in `web/data/sites.json` and
`web/data/plans.json` — the page renders them with no page change. `fit/cover.py` (212) re-runs the batch
over the new material, builds the page's review list, and writes the final report.

Module map (one module per task, so agents never collide):

| module | task | job |
|---|---|---|
| (gate module of 001's choosing, in `pipeline/` or `tools/`) | 001 | accept/reject a fit by numbers, validated on held-out hand fits |
| `fit/evidence.py` | 200 | record + offline-check the place-tie evidence of every picture row |
| `fit/review.py` | 201 | the review queue: item format, page section (`web/review.js`), resolution |
| `fit/propose.py` | 202 | proposed point pairs per (site, picture): a seed a human finishes in a minute |
| `fit/batch_us.py` / `fit/batch_eu.py` | 203a / 203b | the whole loop over the built sites (US / rest of world); each writes its report (`docs/batch_us.md` / `docs/batch_eu.md`); the parent 203, on return, checks the original site set is fully covered |
| `fit/src_van_deventer.py`, `fit/src_kip.py`, `fit/src_mackenzie.py`, `fit/src_roman.py`, `fit/src_limes.py`, `fit/src_wiltshire.py`, `fit/src_numancia.py` | 204-210 | the seven growth leads: find, verify age + free access, tie, stage rows in its own staging files and its own `docs/lead_<name>.md` (book leads write per-book artifacts only) |
| `fit/merge.py` | 211 | consolidate per-source rows into the canonical files; rebuild the book index (the shared one, once); build the new sites; refresh the page data; consolidate the lead statuses into `docs/sources.md` |
| `fit/cover.py` | 212 | targeted picture search for the still-uncovered sites; the only page-facing sync; the final report (`docs/batch.md`) and the current 20-sample |

## Tech choices (and why)

- **The existing stack, unchanged**: Python 3.12 with the pinned deps (`requirements.in` → `requirements.txt`,
  hashed); numpy/scipy/PIL for geometry and images, pyproj/rasterio for geodata; vanilla JS + vendored
  MapLibre for the page. No new framework or service. Reason: the pipeline already does everything this
  project is (georeferencing old plates, matching to ground, building site entries); the failed autofit was
  a search-width failure, not a stack failure, and point-pair fitting is proven by 25 fits.
- **Web Mercator similarity fit** (existing `plan_fit.similarity`: conformal, so a similarity in Mercator
  metres is a similarity on the ground). No new fitting model. The gate (001) scores fits, it does not fit.
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

## Out of scope

- Re-running the fully automatic fitting bet as it stands (`docs/autofit.md`, 0/5). A search may exist as
  the gate's null model (001 decides) or as a coarse proposal seed (202) — never as the accepted fit.
- The Finder (searching for earthworks nobody has recorded) and the Amazon/EBA Finder work; public
  publishing; ground photographs; historic aerials; anything touching the private Finder/Amazon data
  (`web/data/scan`, `web/data/amazon`, `data/finder`, `data/db/marks|surveyseen|verdicts`); changing or
  deleting the existing hand fits.

## Task map (every point of GOAL.md)

| GOAL.md point | delivered by |
|---|---|
| 1. every built site has a fitted drawing **or a ready review item** | 201 (the queue + page), 202 (proposed pairs), 203a/203b (the loop over all built sites), 204-210 (pictures for the new sites), 211 (build), 212 (final cover: no site left without a picture or an item) |
| 2. a fit is accepted by numbers via a gate validated on held-out hand fits; 18/20 of a 20-sample of auto fits must be right | 001 (the gate), 203a/203b (their reports list the seeded 20-sample for the human check; 212 keeps it current until 999 checks it) |
| 3. every picture tied to its place with machine-checkable evidence in its row | 200 (the checker), 204-210 (each lead records the evidence of its rows), 211 (consolidates) |
| 4. the map grows: the seven leads, each verified before use | 204 Van Deventer, 205 Kip, 206 Mackenzie p. 212, 207 Roy/Horsley/Maclauchlan, 208 German Limes, 209 Hoare/Stukeley/Petrie, 210 Numancia; 211 builds them |
| 5. the page shows what changed without breaking anything | 201 (review section, only page change), 211 (new sites/pictures via the existing data files), every task's test re-runs the served page |

## Waves (all tasks of a wave can run at once; two agents pick from each wave)

| wave | tasks | why they can run together |
|---|---|---|
| 1 | **001** (gate), **200** (evidence), **201** (review queue), **202** (proposals) | 001 writes `pipeline/`/`tools/`/`docs/gate.md`; the other three write `fit/`, `web/review.js` (+ one script tag in `index.html`) and their own test files - no file is shared. (001 declares `tests/` as a directory; every task's tests are separate `test_*.py` files, `conftest.py` is owned by 000 - the driver's replay keeps the directory apart where it must.) |
| 2 | **203a** (batch: US built sites), **204** (Van Deventer), **205** (Kip), **206** (Mackenzie p.212), **207** (Roman books), **210** (Numancia) | 203a writes `fit/batch_us.py`, US docs/items, the hand-fit golden hashes; each source writes only its own module + its own staging files + its own `docs/lead_<name>.md`. 207 is the only book-machinery user of this wave. 206 depends on 001 (its identification must pass the gate). |
| 3 | **203b** (batch: rest of world), **208** (German Limes), **209** (Wiltshire) | 203b writes `fit/batch_eu.py`, non-US docs/items; 208 and 209 write only their own staging/modules. 209 is the only book-machinery user left: 207 and 209 share the `data/books/` directory (in practice only per-book files, named by the book's ia id), so they never run together; 208 uses the book machinery at all only if the Limes reports turn out to be IA books - then it declares the exact per-book paths in its own `Touches` line first. |
| 4 | **203** (the parent, on return), **211** (merge & build) | the parent's remaining work is one test file (the coverage check over the original site set); 211 alone writes the canonical data files, the rebuilt shared book index (`index.jsonl`, `validation.json`), `web/data/sites.json` + `plans.json` and `docs/sources.md`. |
| 5 | **212** (final cover, sync & report) | the last task: everything it needs is done; it alone runs the page-facing sync (per-site depictions, the `drawings` counts, `web/data/review.json`) and owns `docs/batch.md`. |

Most waves have two or more tasks (4 / 6 / 3 / 2 / 1). A task with unmet `Depends on:` simply waits; the
driver hands each agent whatever else is open. The book leads (207/209) are in separate waves only
because they share the `data/books/` directory, not because one needs the other's output.

## Test policy

- Command: `python3 -m pytest -q` (the driver builds `.venv` from the hashed `requirements.txt` first).
- No test binds a fixed network port: the server fixture uses `--port 0` and parses the bound address.
- No test writes outside the project and the system temp dir: the session fixture copies
  `web/`, `server/`, `data/` (minus the 1.9 GB `data/raw/`) into a temp tree and the server serves that;
  tests read the checkout only.
- No test needs the network: evidence and fit checks run on stored row fields and in-repo images
  (the six tracked hand-fit sites provide real ground); golden files pin the reference state.
- Each task adds exactly one `tests/test_<name>.py`; shared fixtures go through a DECISIONS request to the
  owner of `conftest.py`, never an edit of it by a second agent.

## Deviations from GOAL.md

(empty — filled with the evidence when a number settles elsewhere)
