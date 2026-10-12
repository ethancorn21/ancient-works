Status: open
# 306b: Look at the agent fits that sit in review items - 21 docs, 10 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306b.mjs

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 21
platefit documents with `by: agent` whose plan is a candidate of the site's review item (the doc
is in the store, but the site's overlay is not built - the fit never reached the map). Render
each the way a visitor would see it if the page showed it: the fit tool over the aerial
photograph, and over the LiDAR relief where the site has a `relief.jpg`, with the DOC's stored
pairs placed. For these 21 the doc's pairs DIFFER from the review item's candidate pairs (the
review tab would pre-place the item's version instead - only castle-neroche n0110_1 matches), so
the verdict must say which placement was looked at.

## Acceptance criteria
- [x] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief where the site has one), taken with `tools/shot.mjs` against `server/serve.py
      --port 0` on this checkout (recipe in the parent's Hand-over; GET only, ephemeral port).
- [ ] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on and the verdict, noting where the
      review item's own version of the placement differs (it is what the review tab shows the
      owner today).
- [ ] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (replacing/sitting beside the
      item's own candidate for the same plan as `fit/review.py upsert_item` does), the document
      is deleted, and the site's review page file is re-exported scoped to the site
      (`fit/review.py export --site` semantics, as tools/site_done.py does - never another
      site's item file). The site stays covered (an open item counts in the union check). A fit
      that sits right stays where it is, and its line says so.
- [ ] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (21, 10 sites)
- argentoratum-q2361353.c_191c6221a81caad0 - Plan de Strasbourg, réduit (d'après Villot)
- argentoratum-q2361353.c_436bea5010beea89 - Strasbourg-Krutenau-Plan de 1852 (12)
- argentoratum-q2361353.c_5badc8c867ef5d98 - Plan Strasbourg projet Conrath 1880
- argentoratum-q2361353.c_5bfb0472f266c056 - 1831. Strasbourg (Tirage avec changement)
- argentoratum-q2361353.c_6acfd94dec8c011b - 91 of Strassburg und seine Bauten
- argentoratum-q2361353.c_87dc28a9645f0e59 - Strasbourg-Krutenau-Plan de 1852 (15)
- argentoratum-q2361353.c_8bdbed9b69d51319 - Plan mur et tours Argentoratum
- argentoratum-q2361353.c_b3533cd48dfc6452 - Strasbourg-Krutenau-Plan de 1852 (13)
- argentoratum-q2361353.c_e882645cc479c889 - Plan topographique de la Ville de Strasbourg, 4 cantons
- argentoratum-q2361353.c_ec1930f8ba9bbabb - Strasbourg plan 1870
- carisbrooke-castle-q328595.c_c280ff908ad8318d - Carisbrooke Castle, Mackenzie 1897 (UK)
- castle-neroche-q5050201.c_44529cdbe2d10a9c - Castle Neroche Somerset Map (UK)
- castle-neroche-q5050201.earthworkenglan01allcgoog_n0110_1 - Castle Neroche, Somerset (Allcroft 1908)
- castra-lemanis-q499898.c_be12fb0f9a87000b - Plan Portus Lemanis (UK)
- cawthorne-camp-q5055239.earthworkenglan01allcgoog_n0325_1 - Cawthorn Camps, Pickering, Yorks (UK)
- cenabum-q2710144.c_e73dc8c09b2fea43 - Plan général de la ville et des environs en 1828 (France)
- dudley-castle-q5311832.c_e66ec095ee45aed0 - 45 of An Illustrated Guide to Dudley Castle (UK)
- ferme-d-azincourt-q20669811.c_804aa7af3eb2ac7c - Azincourt - cadastre de 1810 (France)
- watson-brake-q2552689.c_5e7bb19c79b509ed - Watson Brake - Map (US)
- watson-brake-q2552689.c_b52ddcad2ee295c4 - Watson Brake Mounds - Map (US)
- zwolle-q793.c_f9cddae6b944a648 - Zwolle, town plan by Jacob van Deventer (Netherlands)

## Hand-over
(2026-10-12, iteration 144, agent c - sixth session. ALL 21/21 DOCS JUDGED - ALL STAYS, NO
REMOVALS. The 6 final lines are WRITTEN into docs/site_flow.md (uncommitted - the harness keeps
that edit; commit it with the done work). Only boxes + suite + done remain. Session hit the
context limit right after the 6-line append landed.)

**State.** Box 1 ticked (42 pngs, verified clean). docs/site_flow.md: the 306b block (preamble +
all 21 lines, every one STAYS) sits after the last 306a line (bethlehem c_fc4566d6947287f4);
section header "## The agent fits, looked at (task 306)" at line 702. The first 15 lines were
committed by the driver after iteration 143; the last 6 (cenabum, dudley, ferme-d-azincourt,
watson-brake x2, zwolle) were appended this session and are UNCOMMITTED in the working tree.
No data/review/platefits change at all this session - all 6 STAYS, so no removals, no re-exports.
No by:hand doc ever touched. Last full suite run: at 306a's done commit (baseline 128 passed,
1 skipped; test_gate.py pre-existing red per the driver's loop-start note) - NOT re-run yet this
session (due with the done claim).

**The 6 verdicts (STAYS each; details in the written lines).**
- cenabum c_e73dc8 (5.41 m/px, +1.1°, 2537/5000 vs etatmajor): the plate is Jollois 1833 'Plan
  général de la ville et des environs D'ORLÉANS en 1828'. KEY FACT: the site's canonical point
  (1.909, 47.9025 - Wikidata Q2710144 'Cenabum') IS the city of Orléans (1.9°E, 47.9°N), NOT Tours
  and NOT Epinal: the 1850s IGN état-major tiles show 'ORLÉANS' printed at exactly that point
  (radial old town, fortified quays, bridges; (2.09, 47.90) is open Mardre/Donnery country - I
  initially mis-remembered Orléans at 2.09°E). The drawn 1828 city sits on the real city: radial
  centre + Faubourg St-Vincent align with the georeferenced 1850s survey within 100-200 m; fitted
  5.41 m/px = the plate's ~1:20000 printed scale (no scale bar on the scan; derived from mpx at
  96-110 dpi). The item's 'Epinal' Q173695 (~350 km NE) evidence is a sheet-level red herring.
- dudley c_e66ec (0.69, +24.9°, 2639/4998 vs six-inch-1st): 1885 'Plan of Dudley Castle Grounds'
  on the real conical Castle Rock - summit anchor on the real summit (aerial + relief), contours
  26-36 on the real slopes, priory/church/station aligned. Item cand coarse 0.4379, 33% textured.
- ferme-d-azincourt c_804aa7 (1.23, -1.5°, weak 11/203): the plate is the 1810 cadastre of the
  Ferme d'Azincourt hamlet ('Monts d'Azincourt') of the Émerchicourt commune (NORD) = this site
  itself - NOT the Agincourt village of the Somme (the plate's road labels 'Chemin d'Émerchicourt',
  'Chemin de Boursolain', 'Bonnay' prove it; the drawn river is the Scarpe near Aniche; Nominatim:
  anchor 1 = 'Rue d'Azincourt, Émerchicourt'). Red farm cluster on the real hamlet, roads on roads.
  Fitted 1.23 agrees with the item's own points (1.171); its stated 0.55 does not. Item cand coarse
  0.7246, 50x50 m rect, 363 m off.
- watson-brake c_5e7bb (1.28, -0.9°, 2399/5000 vs relief) and c_b52dd (0.52, -1.6°, 2926/4999 vs
  relief): both versions of the Watson Brake mounds map sit on the real earthworks - RELIEF was
  decisive: drawn round Gentry Mound + S-ring of North/South Mounds + Watson Bayou meanders trace
  the real ring and bayou; aerial agrees. 1.28 agrees with item points 1.448 (cand's stated 0.625
  does not); item cands coarse 0.625, 0%/33%-texture rejected, 146/187 m off.
- zwolle c_f9cdda (2.53, -6.2°, 1981/4998 vs tmk1850): van Deventer 1563 walled town on the real
  Zwolle core, drawn Swol river on the real meanders (aerial + relief). Item cand coarse 1.5625
  (hand-tied 8 bastion/gate pts, 38% textured), thin 800x99 m rect, 455 m off.

**NEXT STEP (in order).** (1) Tick box 2 (all 21 lines written) and box 3 (all fits stay; the
  303-way removal path was never needed) in this task file. (2) Run the suite:
  `.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py` - expected baseline 128
  passed, 1 skipped (test_gate pre-existing red per driver note; it stays excluded). Nothing was
  deleted, so no test needs re-pointing. (3) Tick box 4 (no by:hand touched; suite green). (4)
  `Status: done`, commit everything (task file + DECISIONS.md + docs/site_flow.md's 6-line append
  - the uncommitted working-tree edit). (5) FILE THE PITFALLS ENTRIES this session's discoveries
  need (I could not edit PITFALLS.md at the context limit): (a) Orléans is at ~1.9°E, 47.9°N -
  reverse-geocode before assuming a French city's coordinates (my 2.09°E memory was wrong;
  2.09, 47.9 = Mardre/Donnery); (b) web/data/sites/<site>/etatmajor.webp (and sibling survey
  layers) are 1 px = 1 m blocks centred on the site's point (pipeline/depict.py sample_xyz) -
  crop them as local ground truth; (c) this VM has internet for Nominatim/Wikidata lookups
  (curl with a UA header works; Nominatim /search needs a query param or it 400s). Then the driver
  returns parent 306 for the orphan subtasks 306c-f.

**Materials persist in /tmp**: /tmp/306b_judge.md (per-doc item-cand detail), /tmp/audit_306b.log
+ /tmp/audit_306b_reshoot.log ([eval] transforms). Re-shoot only if ever needed: `node
tools/audit_306b.mjs <doc-id>` (driver empties FQ.entries before openPlan; check placed:false,
n:8).

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
- `tasks/306b-agent-fits-in-review.md` (open) - hand-over: (2026-10-12, iteration 142, agent c - fourth session. All 42 shots done and clean; argentoratum (10/10 docs) judged; 11 docs left to judge, then lines
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

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

### 2026-10-12 306b DECISION: audit the 21 review-queue docs with a fit-tool headless driver (built, half-validated; full run pending)
- First session on 306b. The 21 docs (10 sites, all with relief.jpg -> 42 shots) were verified present in the
  store and in their site's review item (each item's candidate holds the machine's own pairs with a rejection
  `why`; only castle-neroche n0110_1's item pairs match the doc's). Built tools/audit_306b.mjs on 306a's
  pattern: per doc, select -> setGround -> startFit -> openPlan(rvResolveRow) -> push the DOC's 8 pairs ->
  refit, shot over imagery and relief, one `server/serve.py --port 0`, idempotent, doc-id args.
- Two page-behavior traps hit in the argentoratum test shot and fixed IN THE DRIVER (web/*.js is agent a's
  307 territory, not mine to edit): (1) `select()` -> `ensureSite()` bails when `!S.ready`, so the per-site
  relief.jpg layer can be missing (relief shot shows the aerial; live /tiles/relief is off on this machine) -
  wait for S.ready, re-arm ensureSite after setGround; (2) openPlan's trailing easeTo keeps the CURRENT zoom,
  so if select()'s flyTo is mid-flight the shot lands at country zoom (observed 6.38) - poll for the target
  zoom before startFit and re-issue the easeTo with the explicit target zoom after refit.
- The earlier "commons images missing" scare was a wrong path guess: the plan id is `c_<sha1[:16]>` but the
  raw file is `<sha1[:16]>.jpg` (no prefix) and serve.py strips the `media/` segment - all 19 Commons images
  and both IA pages serve fine (verified by path, sizes, and a 200 from the live server).
- Suite not re-run this session (no test-affecting change yet); baseline at 306a's done commit: 128 passed,
  1 skipped, test_gate pre-existing red. NEXT: one-doc re-check with the fixes, then the background full run,
  then judging (21 lines appended under the 306 section of docs/site_flow.md) and 303-way removals of any
  wrong fits (site-scoped `review.export('.', sid)`, never tools/site_done.py on a matcher-reachable site).

### 2026-10-12 306b DECISION: one-doc re-check passed with both race fixes; full 42-shot run launched in the background (pid 3719656, log /tmp/audit_306b.log)
- Second session on 306b. Re-shot the argentoratum c_191c6221a81caad0 couple with the fixed driver and
  verified both page-behavior fixes actually work: imagery shot `relLayer: none`, relief shot
  `relLayer: visible`, zoom 14.97/14.99 (site-scale, not the pre-fix country zoom 6.38), `img: true`,
  `layer: true`, `n: 8`, fithint normal, fit resid 0.0-0.1 m / mpx 2.17 / rot -32.3. Visual check of both
  pngs: town at site scale with the 1833 Villot plate fitted, anchor dots 1-8 on the plate and on the map,
  etatmajor red ink (85 %) above the aerial (imagery) and above grey hillshade + the Ill river (relief) -
  the faithful visitor view. The earlier hand-over's zoom estimate (~13.8) was off; the driver's own
  target formula gives ~14.97 for argentoratum's size_m and that is the correct site-scale view.
- The full run is now in the background (nohup, one `server/serve.py --port 0`, server on 44225 at launch;
  21 docs, 42 shots, 40 to write, skips the 2 existing pngs; est. 15-20 min at ~22 s/shot). Next session:
  tail /tmp/audit_306b.log for FAILURES/MISSING (or just re-run the driver - it is idempotent), then judge
  the 42 shots and append the 21 lines to the end of docs/site_flow.md's task-306 section (which is the
  file's last section; 306a's last line is bethlehem fc4566d6947287f4).
- No test-affecting change this session (two pngs re-shot in docs/site_flow/agent_fits/), so the suite was
  not re-run; it stays due at the judging/removals session.

### 2026-10-12 306b DECISION: judging-prep sheet built; discovered all 10 items are RESOLVED by my own 21 docs (no review-tab presence today); deletions are union-safe
- Third session on 306b. Audit run (pid 3719656, log /tmp/audit_306b.log) healthy: 12/21 docs (24
  pngs) done by 13:49 CDT, zero failures; ~45-50 s/doc in practice (22 s estimate was optimistic),
  ~20 min left. Next session: confirm completion (re-run idempotently if dead), judge from
  argentoratum.
- The review-queue state differs from the task's wording in one way that must be reflected in the
  verdict lines: ALL 10 item files carry a recorded `resolved`, and every resolver is one of my 21
  docs (argentoratum: c_e882645cc479c889; the other 9 sites: their own doc). None of the 10 sites
  is in web/data/review.json today (333 open items, file written 18:01 UTC) - the review tab shows
  nothing for them. So "the review tab would pre-place the item's version" is a counterfactual:
  each line notes the item's own coarse candidate for the same plan (6-anchor rectangle/center,
  scale_m_px from picture size) and its rejection `why` as the version the owner WOULD see when/if
  the item reopens. (fit/review.py: `resolved` is write-once; `resolved_doc` falls back to the
  first candidate that has a store doc only after the recorded one is deleted.)
- Coverage is safe under my deletions: union_check (fit/batch_eu.py) counts a site covered by ANY
  doc OR ANY item file (open or resolved), and upsert_item never deletes an item file. The 10
  item files always exist -> the 10 sites stay covered no matter what I delete. Deleting a site's
  LAST remaining doc reopens its item (all store docs for these sites are my 21; no by:hand);
  306a's bethlehem is the working precedent (item now open, in today's open list).
- Built /tmp/306b_judge.md (persists in /tmp across iterations): per doc - the item candidate (why,
  gate_score, evidence) vs the doc placement (center/extent in metres, matcher inliers/rot), plus
  site context (name/region/size, web/data/site dir, relief flag). Noted in it: weak matcher
  inliers on 5 docs (c_e882645 32/1822, castle-neroche c_44529 52/98, n0110_1 15/26, castra-lemanis
  c_be12fb 15/25, ferme c_804aa7 11/203) - judge the image, not the stats; two candidates with
  200-evidence CONFLICTS (c_e882645: "Ville" Q1165252 ~350 km west near Paris; cenabum c_e73dc8:
... (0.4 KB more: `grep -n -A 200 -F '## 2026-10-12 306b DECISION: one-doc re-check passed with both race fixes; full 42-shot run launched in the background (pid 3719656, log /tmp/audit_306b.log)' DECISIONS.md`)

### 2026-10-12 306b DECISION: audit complete (42 shots); found + neutralised a 307 fit-queue trap that contaminated 9 shots (re-shot clean); argentoratum judged 10/10 STAYS; 11 docs left
- Fourth session. The 42-shot run finished (zero failures). NEW DISCOVERY: nine of my 21 docs
  (c_436bea, c_c280ff, n0110_1, c_be12fb, n0325, c_e66ec, c_804aa7, c_b52dd, c_f9cdda) match a
  web/data/fit_queue.json entry proposing the same site's plan; 307's web/fitkit.js _fkActivate
  then seeds 5 anchor pairs that blend with my 8 doc pairs into a 13-point least squares, so the
  preview ink + fithint showed the blend, not the document. Fix in MY driver tools/audit_306b.mjs
  (web/*.js stays agent a's): the IIFE waits for FQ.loaded, empties FQ.entries before openPlan
  (fitkit falls open), and reports fqEntries/placed/anchor in [eval]. All 18 reshoots verified
  clean (placed:false, n:8, resid ~0); the [eval] numbers in /tmp/audit_306b_reshoot.log are the
  docs' own transforms. If another task ever drives openPlan headlessly with its own pairs, it
  hits this too: check P.placed / pair count in the shot log.
- Judging: argentoratum 10/10 STAYS (all ten sit on the real old town / fort ring / Roman castrum /
  Krutenau district; details in the task hand-over, with per-doc mpx/rot and the item candidate's
  rejection). c_e8826 - the item's recorded resolver - verified right, so the item stays resolved
  by a fit that is actually good; its "Ville" Q1165252 evidence conflict is a sheet-level red
  herring. NEXT (in order): judge the remaining 11 docs (hand-over has per-doc numbers; earthwork
  sites - neroche, lemanis, cawthorne, watson-brake x2 - judge the RELIEF image first), append all
  21 lines to the END of docs/site_flow.md (section "## The agent fits, looked at (task 306)"
  starts line 702; last existing line = bethlehem fc4566d6947287f4 at line 800), 303-way removals
  of any misses (upsert_item full doc + why, delete doc, site-scoped review export; NEVER
  tools/site_done.py on these 10 sites), then tick boxes and run the suite
  (.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py; baseline 128 passed /
  1 skipped at 306a's done commit 4ca9e2c; re-point any test pinning a removed doc at a
  surviving one - never loosen).

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

### 2026-10-12 306b (agent c, iteration 143) session status
    15/21 docs judged (ALL STAYS, no removals yet); all 15 lines + 306b preamble written to
    docs/site_flow.md (UNCOMMITTED - the harness keeps that edit for the next agent to commit
    together with the remaining work); box 1 ticked. NEXT: judge the remaining 6 (cenabum
    c_e73dc8 - check real Tours vs the Epinal red herring; dudley c_e66ec; azincourt c_804aa7;
    watson-brake x2 - RELIEF decides; zwolle c_f9cdda), append their 6 lines at the end of the
    306b block, 303-way any miss (upsert_item + rm doc + site-scoped export, never
    tools/site_done.py on the 10 sites), tick boxes 2-4, run the suite. Full state in
    tasks/306b-agent-fits-in-review.md Hand-over.
