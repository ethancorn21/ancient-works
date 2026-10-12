Status: in-progress
# 306c: Look at the orphan agent fits, US - 16 docs, 9 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306c.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 16
US platefit documents with `by: agent` that are ORPHANS - in the store, but with no overlay
built on the site and not referenced by any review item, so a visitor sees them not at all.
Render each the way the page would if it ever showed it: the fit tool over the aerial
photograph, and over the LiDAR relief (every site here has a `relief.jpg`), with the doc's
stored pairs placed. The verdict records where the doc stands today (invisible) and whether
the placement is good enough to keep.

## Acceptance criteria
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief), taken with `tools/shot.mjs` against `server/serve.py --port 0` on this checkout
      (recipe in the parent's Hand-over; GET only, ephemeral port).
- [ ] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on (the real mounds, banks, ditches) and
      the verdict (keeps its document / deleted - and it is an orphan today, invisible on the
      page).
- [ ] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (`fit/review.py upsert_item`
      pattern), the document is deleted, and the site's review page file is re-exported scoped
      to the site (never another site's item file). The site stays covered for the union check
      (an open item counts). A fit that sits right keeps its document, and its line says so.
- [ ] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (16, 9 sites)
- cahokia-q333661.annualreportofbu1218901891smit_n0200_1 - Map of Cahokia group, Madison county, Illinois
- etowah-indian-mounds-q4533107.annualreportofbu1218901891smit_n0386_1 - Plat of the Etowah group (original)
- fort-ancient-q5470727.b24849959_n0264_1 - Fort Ancient, Warren county (Squier & Davis)
- hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1 - Plan of Cemetery Mound, Mt. Vernon
- hodgen-s-cemetery-mound-q5876069.b24849959_n0353_1 - Plan of mound at Mt. Vernon (Squier & Davis)
- marietta.b24849959_n0195_1 - The Marietta works (Squier & Davis)
- mound-cemetery-q6919104.annualreportofbu1218901891smit_n0563_1 - Plan of Cemetery mound, Mt. Vernon, Knox county
- mount-horeb-earthworks-complex-q6921321.c_d1dff07f0da57b0e - Peter Village enclosure, Squier & Davis Plate XIV fig 3
- pyramid-mound-q7263260.ancientmonuments00squi_n0134_1 - (Squier & Davis, untitled)
- serpent-mound-q968802.b24849959_n0313_1 - Serpent Mound; from Holmes
- serpent-mound-q968802.c_15ff865e5f3d8ddb - Serpent Mound by William Jacob Baer
- serpent-mound-q968802.c_2c260a03d1f8df1c - SD35 Serpent Mound, Squier & Davis Plate XXXV
- serpent-mound-q968802.c_52dfe1fc979edf2c - Harper's New Monthly Magazine, vol 104
- serpent-mound-q968802.c_7b01a4bb50d68b56 - 26 of A School History of the United States
- serpent-mound-q968802.c_8ebd42607fbb96d8 - 26 of A School History of the United States (2nd copy)
- serpent-mound-q968802.c_dd2c553d611e610b - 26 of A School History of the United States (3rd copy)

## Notes
- serpent-mound carries the site's one hand fit (n0210_1) on the map; its 7 agent docs are all
  orphans. The hand doc is never touched and its overlay stays whatever this audit decides about
  the agent docs.

## Hand-over
(2026-10-12, iteration 147, agent c - second session. 32-shot run CONFIRMED complete; all 7 serpent-mound docs judged (ALL DELETE); 9/16 judged in total. Session died at the context limit just as the 303-way removal execution was being prepared. Next session: execute the 8 removals, write the 306c block into docs/site_flow.md, run the suite.)

**State.** (1) The audit run FINISHED: /tmp/audit_306c.log ends with `[audit 306c] all shots written to docs/site_flow/agent_fits`. All 32 shots (16 docs x aerial+relief) are in docs/site_flow/agent_fits/ (uncommitted; the harness keeps them). All [eval] lines: img/layer true, `placed:false` for every doc - the two FQ-contaminated docs (hodgen-s-cemetery-mound b24849959_n0353_1, pyramid-mound ancientmonuments00squi_n0134_1) verified UNcontaminated (fqEntries=114 is the total queue count, not a match). (2) Tests: NOT run this session. Baseline in this checkout (306b, 2026-10-12): 128 passed, 1 skipped with `.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py` (test_gate pre-existing red per the driver's loop-start note). Run after the data change. (3) fit/review.py: I had just grepped the entry points - `item_path` L56, `upsert_item(root, site_id, entries, no_picture=None)` L80, `resolved_doc(item, root)` L156, `export(root, site_id=None)` L189 - READ THEIR BODIES first; I did not yet see the candidate field list or whether upsert_item creates a missing item file (the 303 fabrication path used it to create items, so it should).

**VERDICTS (9 of 16). All 7 serpent-mound docs: DELETE; marietta: DELETE. None is a duplicate of the hand fit.** Reference truth established this session: the owner's hand fit n0210_1 (S&D 1848 Plate XXXV) sits on the REAL effigy - visible on the site's LiDAR relief.jpg (1600x1600 mapped to site corners [-83.4373820,39.0312477],[ -83.4235060,39.0312477], [-83.4235060,39.0204679], [-83.4373820,39.0204679]): head coil at image px ~(980,860) -> (-83.4288, 39.0254), tail coil ~(690,800) -> (-83.4314, 39.0258), centre ~(-83.4301,39.0256) = the hand-fit plate quad centre (-83.43065,39.02560; quad corners in web/data/sites/serpent-mound-q968802/depictions.json: [-83.4324978,39.0272962], [-83.4288031,39.0270005], [-83.4292129,39.0239094], [-83.4329076,39.0242051]). Judged from the 14 serpent shots (aerial+relief; in every shot the hand-fit S&D serpent is the red line on the real ridge, the agent plates are the fit-prev layers):
- serpent-mound-q968802.c_8ebd42607fbb96d8 (School History 1893 p26, cropped; 8 pairs, 1.0 m/px, 0 deg, resid 0): the plate's serpent + "Mound 10 ft. high" spiral land ~255 m NORTH of the real effigy (hatched hill on farm/NE hills); the real effigy is occupied only by the hand fit. DELETED.
- serpent-mound-q968802.c_dd2c553d611e610b (same figure, "no cap": 8 pairs): same, ~265 m north. DELETED.
- serpent-mound-q968802.c_7b01a4bb50d68b56 (same figure, full page; 4 pairs): serpent ~230 m north. DELETED.
- serpent-mound-q968802.b24849959_n0313_1 (Fowke 1902 Fig. 81 from Holmes; 5 pairs, 0.41 m/px, +2 deg, resid 9-66 m): the Holmes S is drawn N-S down the page and is stretched to ~800 m ground span (the real effigy runs E-W, ~400 m); 66 m mid residual is the stretch; rings/hills sit NW/SE of the real ones. DELETED.
- serpent-mound-q968802.c_15ff865e5f3d8ddb (Baer 1889 engraving, VIEW row; 4 near-collinear pairs, resid 22/61/27/0): homFit (8-param) through 4 points is exact BY CONSTRUCTION - the non-zero resid shows the normal-equations solve is ill-conditioned (near-collinear); the engraved serpent lands ~180 m NW of the real one. DELETED.
- serpent-mound-q968802.c_2c260a03d1f8df1c (S&D Plate XXXV via Commons = a SECOND copy of the very plate the owner hand-placed; 4 pairs, 1.0 m/px, 0 deg, resid 0): placed ~145-190 m SE of the hand fit AND at ~4x the true scale (the Commons file is the plate alone, 1280 px wide = 1.28 km at 1 m/px, vs the real ~320 m figure): the drawn S is bigger than and offset from the real effigy. Not a duplicate of the hand fit. DELETED.
- serpent-mound-q968802.c_52dfe1fc979edf2c (Harper's 1902 engraving, VIEW row; 8 near-collinear pairs along the north ridge line, resid 0): homography under-constrained perpendicular to the anchor line (0 proves nothing); engraved serpent lands ~200 m NE of the real one (plate centre maps to (-83.43055, 39.02681)); the hatched terrain overhangs flat farmland E and S of the preserve. DELETED.
- marietta.b24849959_n0195_1 (Fowke 1902 Fig. 15; judged in the PREVIOUS session - details there): scale right (1 m/px per the plate's own bar), placement ~1.3 km S-E of the real Conus mound. DELETED.

**NOT yet judged (7 docs, shots all exist and verified rendered):** cahokia-q333661.annualreportofbu1218901891smit_n0200_1 (8 pairs, 1.3 m/px, -3 deg, resid 9-175 m); etowah-indian-mounds-q4533107.annualreportofbu1218901891smit_n0386_1 (8 pairs, exact 0); fort-ancient-q5470727.b24849959_n0264_1 (8 pairs, exact 0); hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1 (4 pairs, exact 0); hodgen-s-cemetery-mound-q5876069.b24849959_n0353_1 (8 pairs, 0.78 m/px, resid 8-33 m); mound-cemetery-q6919104.annualreportofbu1218901891smit_n0563_1 (8 pairs, exact 0); mount-horeb-earthworks-complex-q6921321.c_d1dff07f0da57b0e (5 pairs, exact 0); pyramid-mound-q7263260.ancientmonuments00squi_n0134_1 (4 pairs, 0.54 m/px, -5.5 deg, resid 18-34 m). (That is 8 docs - I miscounted: 16 total = 1 marietta + 7 serpent + 8 remaining.) For each: read the aerial shot (and relief if ambiguous), locate the real works (site point can be a modern city - the 306b sites.json pitfall; for these US mound sites the site point is the mound complex), cross-check scale vs the plate's own bar (PIL in .venv, 306b technique), compare against the site's hand depictions where any exist (none of these 8 sites have hand fits except none - all 8 sites' depictions are topo/imagery only; the only hand fit in the whole 306c set is serpent-mound's).

**NEXT STEP (exact).** 1) Read the bodies of fit/review.py L56-230 (item_path, upsert_item, resolved_doc, export) and the 303 removal precedent in DECISIONS-archive.md (`grep -n -i "303.*upsert\|upsert.*303" DECISIONS-archive.md`). 2) Read tests/test_batch_eu.py::test_union_check and tests/test_serve.py::test_platefits_docs_match_sites and confirm the 8 doc deletions + 2 new/updated review items keep both green (union: a site is covered iff it has an OPEN item OR a built overlay - confirm the exact predicate; serp-mound keeps its hand overlay anyway; marietta's item becomes open with the upserted candidate). 3) Execute the 8 removals the 303 way, per site in this order: build the candidate (the doc's fields: plan, title, book, ia, file, label, cite, url, view, ref, size, map_box where the doc has them, + the doc's 4+ pairs + place_reason = this audit's verdict sentence), upsert_item('.', <site>, [cand]) - for serpent-mound upsert all 7 candidates into its ONE item in a single call (or 7 calls; check upsert_item's merge semantics in its body), THEN delete the 8 doc files from data/db/platefits/, THEN `review.export('.', <site>)` for serpent-mound and marietta (scoped; never another site's file). 4) Write the 306c block into docs/site_flow.md after 306b's last line (the zwolle line; file is 939 lines, section at L702): preamble (16 US orphans - in the store but no overlay and no review item, so the page shows them not at all today; each rendered in the fit tool over the aerial + the LiDAR relief; the serpent-mound lines judged against the site's hand fit, the reference placement on the real effigy) + one line per judged doc (the 8 above, verdict DELETED + the 303-way action + what the lines sat on) - append the remaining 8 lines in later sessions, keeping one line per doc. 5) Run the suite (128/1 baseline); commit shots + docs + data changes; tick boxes as verified. The 306c box 3 says "the site stays covered for the union check (an open item counts)" - verify that predicate in test_batch_eu before deleting.

**Pitfalls (file when convenient).** (1) web/data/sites/<site>/depictions.json is a DICT {'depictions': [...]} (a scanner crashed on .get over a float). (2) some data/review/*.json lines parse to non-dict JSON (bare float) - scanners must isinstance-check. (3) PIL 12.3.0 is in the project .venv (system python3 has none) for scale-bar measurement. (4) NEW: a plans.json row with `view: true` makes refit() use the 8-param homFit, whose result has NO mpx/rot keys - [eval] then reports mpx:null/rot:null (NOT an error; two 306c docs are view rows). A homFit through 4 points (or 8 near-collinear points) is exact by construction: 0.0 resid proves nothing about placement; the near-collinear case is under-constrained in the perpendicular direction. (5) NEW: the site relief.jpg maps to site.corners (index.html ensureSite L367-368): image px -> lon/lat linearly over the corners rect - a reliable way to read the real works' position off the LiDAR without a live tile service (used to pin the serpent effigy: head (-83.4288,39.0254), tail (-83.4314,39.0258)).

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
own task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/306c-orphan-fits-us.md` (in-progress) - hand-over: (2026-10-12, iteration 147, agent c - second session. 32-shot run CONFIRMED complete; all 7 serpent-mound docs judged (ALL DELETE); 9/16 judged. Session died at the context limit just as the 303-way removal execution was being prepared.)
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

### 2026-10-12 306c driver-note: session at context limit (iteration 146)
- 306c first session: tools/audit_306c.mjs built (clone of 306b's; works on the post-307 page), full 32-shot
  audit run launched in background (log /tmp/audit_306c.log; resumable - skips existing shots), ~30 shots
  written to docs/site_flow/agent_fits/. 1/16 judged: marietta = DELETED case (fit 1 m/px/0 deg matches the
  plate's scale bar, but the drawn Conus mound sits ~1.3 km S-E of the real one in Mound Cemetery) - the
  303-way removal (upsert candidate w/ place_reason -> delete doc -> scoped export) is NOT yet executed.
  Next session: finish the run (re-run driver), judge the other 15 in batches, execute marietta's removal
  (after reading test_batch_eu/test_serve), write the 306c block in docs/site_flow.md, run the suite
  (baseline 128 passed / 1 skipped, --ignore=tests/test_gate.py). Full state in the task's Hand-over.

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/221-review-stats-test.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-12 306 DECISION: split into six look-audits by visibility class and region
- Box 1 of 306 covers ALL 112 non-hand docs (23 on-map, 21 in review items, 68 orphans - the orphan
  class is new to the project: in the store but neither built as an overlay nor referenced by any
  review item, so a visitor can see them not at all; audited by rendering the doc's saved pairs in
  the fit tool). Six subtasks: 306a on-map (23), 306b review (21), 306c orphan US (15), 306d orphan
  UK part 1 (18), 306e orphan UK part 2 (15), 306f orphan continental (17). A before B before C:
  only A sits on the map (the title's "none reaches the map unseen"); only 306a performs the
  removals (box 2). No subtask carries `Depends on: 306` (a split parent deadlocks its own
  subtasks - PITFALLS); the driver hands them out a-f.
- The audit is headless-browser work, not a test: serve the tree once (server/serve.py --port 0,
  ephemeral port, GET-only - safe for parallel checkouts) and drive the real page through
  tools/shot.mjs's [js] argument: select(site) -> setGround('imagery'|'relief', site) ->
  startFit(site) -> openPlan(row) -> push the doc's pairs as {u,v,lon,lat} + addPairMarker +
  refit (refit renders the fitted plate as the fit-prev map source; web/review.js does exactly
  this for item pairs, L142-146/L189-196). On-map docs go the visitor's way instead: open the
  site, activate the depiction (applyDep). This VM HAS internet (Esri World_Imagery 200 in 0.17 s,
  verified this session): the "no-internet headless" pitfall applies only to the no-network test
  runs. LiDAR on the page is the per-site prebuilt relief.jpg (index.html L367-368), not the live
  /tiles/relief (off here, `aw` is Mac-only); shotwick has no relief.jpg (aerial-only).
- For the 21 B docs the doc's stored pairs DIFFER from the review item's candidate pairs (except
  castle-neroche n0110_1): the audit renders the DOC's own pairs (the document is the artifact)
  and the verdict notes where the item's version differs.
- All 112 docs carry 4+ pairs, so every one renders as a fitted plate (simFit needs 3). sites.json
  `drawings` are stale for most A-group sites (0 despite the overlay present; only aldenhaag=1,
  forthill=2, newark=2 non-zero) - 306a's rebuild via tools/site_done.py fixes the counts for the
  sites it changes.

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (1 tests)
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_gate.py:36: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    1 failed, 59 passed in 63.50s (0:01:03)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites
