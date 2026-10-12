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
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
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
(2026-10-12, iteration 139, agent c - FIRST session on 306b. Built the headless audit driver and
validated it on one doc; full 42-shot run NOT started yet. Driver is uncommitted - the harness saved it.)

**State.** `tools/audit_306b.mjs` (on my Touches line) is built and half-validated: for each of the 21
docs it opens the site the review-tab way (select -> setGround -> startFit -> openPlan(
rvResolveRow(site, docFields)) -> push the DOC's own 8 pairs + addPairMarker + refit) and takes a
1440x900 shot over the aerial, plus over the LiDAR relief (all 10 sites have relief.jpg -> 42 shots
total). One `server/serve.py --port 0` for the whole run, GET only; idempotent (skips existing pngs);
accepts doc ids as args (`node tools/audit_306b.mjs <docId> [docId ...]`). The argentoratum c_191c
couple was shot twice and is in docs/site_flow/agent_fits/ (uncommitted).

**Two page-behavior traps found and worked around IN THE DRIVER (the page files are agent a's 307
territory - do not edit web/*.js here):**
1. `S.ready` race: `select()` -> `ensureSite()` bails when `!S.ready` (the page's start() sets it after
   loadPlans + catalog/scans/amazon fetches + map 'load'). If it bails, the per-site `rel-<site>`
   relief.jpg layer is never added and the relief shot shows the aerial instead (the live /tiles/relief
   is OFF on this machine - `aw` is Mac-only - so the per-site relief.jpg is the ONLY relief). Fix in
   the IIFE: wait for `S.ready` before select, then re-arm `ensureSite(s); applyAll()` after setGround.
2. Zoom race: `openPlan()` ends with `map.easeTo({center, padding})` - no zoom - so it KEEPS the current
   zoom. If select()'s 4.5 s flyTo is still mid-flight when it fires, the camera settles at country
   zoom (observed 6.38 in a debug run; the aerial then fills the frame and the anchors are a dot
   cluster). Fix in the IIFE: before startFit, poll until `map.getZoom()` is within 0.1 of the target
   (`15 - Math.max(0, Math.log2(span/1800))`, span = max(s.size_m) - select()'s own formula at 1440 px);
   after refit, if zoom is off by > 0.2, re-issue the site's easeTo WITH the explicit target zoom.

**NEXT STEPS, in order.**
1. Re-run the one-doc check with the fixes in: `rm docs/site_flow/agent_fits/argentoratum-q2361353_c_191c6221a81caad0*.png` then
   `node tools/audit_306b.mjs argentoratum-q2361353.c_191c6221a81caad0`. Look at BOTH pngs: the aerial must
   show the town with the fitted plate + anchor dots at a site-scale zoom; the relief must show grey
   hillshade (plus the site's own etatmajor red drawing - that is the faithful visitor view: the dep
   layer draws above the relief) with the fitted plate. Check the [eval] line: `zoom` ~ 13.8, `relLayer`
   'visible' on relief / 'none' on imagery, `img:true`, `layer:true`, `fithint` NOT "Could not load the page scan."
2. Launch the full run in the background: `nohup node tools/audit_306b.mjs > /tmp/audit_306b.log 2>&1 &`
   (~42 shots, est. 15-20 min; it reuses the existing argentoratum pngs). It survives the session.
3. Next session: `tail /tmp/audit_306b.log` for `[audit] FAILURES` / MISSING; re-run any failed docs by id.
4. JUDGE the 42 shots in batches of ~7 and write the 21 lines into docs/site_flow.md under the existing
   "## The agent fits, looked at (task 306)" section (line ~702) - APPEND below 306a's 23 lines (the
   section intro already promises this; bethlehem's 12 lines are the last of 306a's). Line format follows
   306a's: `<doc id> - <source>, <fit kind> (<score/points>, gate/resid): what the lines sit on. STAYS.`
   or `... LEAVES (reason).` NOTE in each line where the review item's own version of the placement
   differs (the item's candidates hold the machine's pairs; their `why` fields already say why the machine
   rejected: median residual > 45 m, or fabricated anchor patterns - read data/review/<site>.<plan>.json).
   The audit looks at the DOC's pairs (the document is the artifact); the viewer of the review tab today
   sees the item's version.
5. Wrong fits (if any): the 303 way, exactly as 306a did (its hand-over has the recipe): `review.upsert_item('.', sid, [entry])`
   with entry = the FULL doc record + `why` = the audit reason (it sits beside/replaces the item's own
   candidate for the same plan); delete `data/db/platefits/<doc>.json`; `plan_fit.prune('.', sid)` (drops any
   overlay - there is none for these 21, but it refreshes the site); then re-export the site's review page
   file SITE-SCOPED: `review.export('.', sid)` (fit/review.py export with site_id - the tools/site_done.py
   semantics my box 3 names; NEVER export another site's item file). The site stays covered (an open item
   counts in the union check). Do NOT run tools/site_done.py on a site whose matcher is reachable (206
   trap: its fit phase would place a NEW unaudited fit). Right fits stay in the store; their line says STAYS.
6. Run the suite (`.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py`; baseline 128 passed,
   1 skipped, test_gate pre-existing red). If a deletion breaks a test that pins one of the 21 docs
   (306a broke 5 this way: mackenzie doc_record, provenance source-line pins), re-point it at a surviving
   doc like 306a did - search tests/ for the doc id first.

**Facts.**
- The 19 Commons docs: plan id `c_<sha1[:16]>` but the raw file is `<sha1[:16]>.jpg` (NO c_ prefix); served
  at /media/commons/<site>/<hash>.jpg -> data/raw/commons/<site>/<hash>.jpg (serve.py strips the media/ segment;
  the regex is 16 hex, so a c_-prefixed path would 404). The 2 IA docs (castle-neroche n0110, cawthorne n0325)
  serve at /books/earthworkenglan01allcgoog/n01{10,25}.jpg -> data/raw/books/<ia>/full/<file> (both present,
  ~1.2 MB). data/raw is a symlink to the shared /home/agent/projects/ancient-works/data/raw tree.
- All 21 docs: by: agent, 8 pairs, model similarity (the 2 IA ones: model None, a crop sub-rectangle, size None).
  plans.json HAS rows for the 2 IA plans (map_box set) - rvResolveRow finds them by plan id; the 19 Commons docs
  synthesize (map_box null -> whole page, which equals their crop anyway).
- review.js WRAPS openPlan (applies RV.pending after it); my IIFE pushes the doc's pairs directly after
  `await openPlan(row)` (the wrapper is a no-op when RV.pending is null) - same visible result, no RV coupling.
- Per-site old-drawing layer (argentoratum: etatmajor ink, 85 %) draws ABOVE the relief and BELOW fit-prev -
  in relief shots you see relief + the site's own drawing + the audited plate. That is what a visitor sees.
- 306a's 45 shots are in docs/site_flow/agent_fits/ (same naming: <site>_<plan>.png / _relief.png); 47 files
  now incl. my 2.
