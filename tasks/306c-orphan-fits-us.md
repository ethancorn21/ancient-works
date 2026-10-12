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
(2026-10-12, iteration 149, agent c - third session. 15/16 judged: 8 DELETED (all executed 303-way in the PREVIOUS session, committed), 7 STAYS (verdicts below), pyramid-mound PENDING final call. Next: finish pyramid-mound call, write the 8 pending-doc lines (or 7 + pyramid line) into the 306c block, execute hodgen n0092's 303-way removal (+ pyramid's if it deletes), run the suite.)

**KEY DISCOVERY this session.** The hand-over's "8 removals NOT yet executed" was STALE: the previous session (147/148) already executed all 8 judged removals the 303 way, and the driver committed them in `b9cbc46`. Verified on disk: the 8 doc files are GONE from data/db/platefits/ (only serpent-mound-q968802.ancientmonuments00squi_n0210_1.json remains of the 9); data/review/serpent-mound-q968802.annualreportofbu1218901891smit_n0636_1.json and data/review/marietta.ancientmonuments00squi_n0169_1.json already carry the 7 + 1 upserted candidates WITH place_reason ("306c audit 2026-10-12: ... Document deleted."); web/data/review.json is re-exported (333 open, at 2026-10-12T21:12:09, both items open with the new candidates). docs/site_flow.md already has the 306c block at L941: preamble + 8 lines (marietta + 7 serpent). So box 3 (the 303 way) is DONE for those 8 - do not re-upsert (upsert merges by plan; re-running is harmless but pointless).

**fit/review.py (read this session, full bodies).** upsert_item(root, site_id, entries, no_picture=None): merges candidates by plan (same-plan replaces in place, new plans appended); CREATES a missing item ({site, candidates, no_picture_found:null, resolved:null}); file name = <site>.<candidates[0].plan>.json (a changed lead MOVES the file, old unlinked); resolved is write-once (never cleared); web/data/review.json is never written by it. export(root, site_id=None): recomputes web/data/review.json over the WHOLE queue (open = no resolved AND no platefits doc for any candidate); records resolved into item files ONLY for site_id when a resolving doc appears (none of mine: docs deleted, items stay open). union_check coverage predicate (fit/batch_eu.py L46+): a site is covered iff it has ANY platefits doc naming it OR ANY data/review item naming it (by the site FIELD, open or not) OR an old-style site.json hand fit - so a site whose only doc is deleted stays covered while its item file exists. test_platefits_docs_match_sites: every remaining doc must name a built site with plan+pairs (deletions keep it green).

**VERDICTS (this session, from the 16 pending shots' map panes, cropped 2.6x; the full shots are in docs/site_flow/agent_fits/):**
- cahokia-q333661.annualreportofbu1218901891smit_n0200_1 (Thomas 1894 Plate VI "Map of Cahokia group", 8 pts, 1.3 m/px, -3 deg, resid 9.5-174.7 m) - **STAYS**: the plate's dense mound-group cluster (its subject) sits on the REAL Cahokia mound complex on the LiDAR (bright mound cluster in the dark floodplain depression); the "St. Louis and Collinsville Road" dashed line follows the real road; the Mississippi hatch sits on the real river (dark band, right edge); the Horse-Shoe slough is at the NE end. Residuals are frame-level (the 1894 survey grid's page skew, -3 deg), not subject misplacement.
- etowah-indian-mounds-q4533107.annualreportofbu1218901891smit_n0386_1 (Thomas 1894 Fig. 182 "Plat of the Etowah group", 8 pts, 1.0 m/px, 0 deg, resid 0) - **STAYS**: georeferenced plate; the drawn great ditch traces the real ditch band in the aerial, the hatched platform mound "a" (great mound) sits on the real grassy mound, mounds b/c on the real mounds, the Etowah River line follows the real channel.
- fort-ancient-q5470727.b24849959_n0264_1 (Fowke 1902 Fig. 59 "Fort Ancient, Warren county", 8 pts, 1.0 m/px, 0 deg, resid 0) - **STAYS**: the drawn walled loops (north/south forts) trace the real ditch/bank bands (light lines in the aerial), the creek line follows the real meander at the SE, the park is centred.
- hodgen-s-cemetery-mound-q5876069.b24849959_n0353_1 (Fowke 1902 Fig. 96 "Plan of mound at Mt. Vernon", 8 pts, 0.78 m/px, -0.1 deg, resid 8-33 m) - **STAYS**: the drawn hatched mound ring is CONCENTRIC on the real cemetery mound - the distinct round LiDAR bump (bright centre, dark ring) in the residential block by the Big Sandy; the drawn ring is ~2x the real diameter but centred on it.
- hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1 (Mills 1914 "Plan of Cemetery Mound, Mt. Vernon", 4 pts, 1.0 m/px, 0 deg, resid 0) - **DELETE**: the 100x100 m anchor square (and the drawn mound it encloses) sits ~110 m S-E of the real mound's LiDAR bump, on flat residential ground - the real mound is just outside the drawn extent at its NW. Same mound as n0353 (which sits right) - this copy is mis-placed. 303-way removal NOT yet executed (see NEXT STEP).
- mound-cemetery-q6919104.annualreportofbu1218901891smit_n0563_1 (Thomas 1894 Fig. 306 "Plan of Cemetery mouud, Mt. Vernon. Knox county", 8 pts, 1.0 m/px, 0 deg, resid 0) - **STAYS**: the drawn big concentric "Cemetery Mound" circle sits ON the real conical mound (the ringed disc of Mound Cemetery, Marietta - bright LiDAR bump with dark ring), the drawn fence circle spans the real cemetery parcel, the drawn streets (Market/High/North St) follow the real street grid; the page's "MARIETTA WORKS" label is centred in the drawing. (The caption's "Mt. Vernon, Knox county" is the source's own labelling; the plan matches the Marietta cemetery.)
- mount-horeb-earthworks-complex-q6921321.c_d1dff07f0da57b0e (S&D 1848 Plate XIV Fig. 3 "Peter Village enclosure", drawn by C. Rafinesque, 5 pts, 1.0 m/px, 0 deg, resid 0) - **STAYS**: the drawn bank/ditch arc (hatched double line) lies on the real bright bank band + dark ditch line of the earthwork in the LiDAR, following the real ditch's S-bend near anchor 3; the plate's own "500 ft to the inch" is consistent with the fitted 1.0 m/px.
- pyramid-mound-q7263260.ancientmonuments00squi_n0134_1 (S&D 1848 n0134, untitled doc; the plate is FIG. 9: a big double-ring circular earthwork with an entrance gap at the SW + a small square enclosure at the left; 4 pts, 0.54 m/px, -5.5 deg, resid 17.7-33.9 m) - **PENDING final call**: the real subject is the dark-ringed ~100 m circular mound at ~(-87.5056, 38.6705) ~= the site point (-87.5061, 38.6706). The drawn double-ring circle's centre works out at ~(-87.5063, 38.6705): the real mound sits INSIDE the drawn outer ring but ~60 m east of its centre, near the east rim (ring outer diameter ~230 m vs real mound ~100 m); the drawn square enclosure (anchor 4's feature) lands ~300 m west, over residential ground with no visible earthwork. My lean: STAYS - the drawn earthwork (the circle/ditch, the plate's subject) does enclose the real mound and the fit is tight (18-34 m); a 60 m centre offset on a 230 m ring is not the serpent-mound class of miss (180-265 m, drawn subject on foreign ground). Verify by re-reading /tmp/crop_pyramid-mound-q7263260_r.png (or re-crop from the repo shot) before committing the call; if DELETE, the 303 way (below) applies with the doc's 4 pairs.

**Tests.** NOT run yet this session. Baseline to match (306b, 2026-10-12, this checkout): `.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py` = 128 passed, 1 skipped; test_gate is the pre-existing driver-baseline red (do not run it as part of the check). Union coverage after the hodgen n0092 removal: the site keeps its n0353 doc (STAYS) AND gains/keeps an item - covered either way; pyramid-mound keeps its doc (if STAYS) or gets an item (if DELETE) - covered either way.

**NEXT STEP (exact).** 1) Final pyramid-mound call (lean STAYS; re-read the relief crop to confirm the drawn ring encloses the real mound). 2) 303-way removal of hodgen n0092 (and pyramid's if it deletes): candidate = the doc's fields (plan, title, book, ia, file, label, cite, url, view, ref, size where the doc has them - read data/db/platefits/<doc>.json) + the doc's pairs + place_reason = the audit verdict sentence above ("306c audit 2026-10-12: ... Document deleted."); `cd /home/agent/projects/ancient-works.c && .venv/bin/python -c "import sys; sys.path.insert(0,'fit'); import review; review.upsert_item('.', '<site>', [cand])"` - NO existing item file for hodgen (data/review has none for that site; upsert creates data/review/hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1.json - the lead is candidates[0].plan; if the site already has an item, upsert merges into it and may MOVE the file name to the new lead); THEN `rm data/db/platefits/hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1.json`; THEN scoped export: `.venv/bin/python -c "...import review; review.export('.', 'hodgen-s-cemetery-mound-q5876069')"` (NEVER another site's file; export always rewrites the whole web/data/review.json page file - that is correct). 3) Append 8 (or 9) lines to the 306c block of docs/site_flow.md (after the c_dd2c553d611e610b line, L994-995) - one per doc: the doc's title + fit stats (n pts, resid, m/px, deg) + what the lines sit on + verdict; update the block's preamble which currently says "All nine judged in this pass ... The remaining 8 docs ... are pending judgment" (that sentence is now stale: 15 judged, 7 STAYS among them). 4) Run the suite (expect 128/1 + any new passes; no NEW failures); 5) tick the 3 acceptance boxes (box 1: 32 shots exist - verified; box 2: 16 lines in the section; box 3: 303-way done for every DELETE - 8 previous + hodgen n0092 [+ pyramid if applicable]; box 4: no by:hand doc touched, suite at baseline) and set Status: done. 6) File the PITFALLS entries from the old hand-over if still missing (grep first): (a) depictions.json is a DICT {'depictions': [...]}; (b) some data/review lines parse to non-dict JSON - isinstance-check; (c) PIL is in .venv not system python3; (d) plans.json `view:true` rows fit via 8-param homFit with no mpx/rot - 0 resid proves nothing (near-collinear anchors are under-constrained); (e) relief.jpg maps linearly to site.corners (image px -> lon/lat) - the way to read real-works position from LiDAR without a live tile service; (f) NEW this session: two docs of the SAME site get their /tmp crops overwritten by a shared site-prefixed crop name - suffix crops with the plan id.

**Machine notes.** All 32 shots are committed in the repo (b9cbc46), so /tmp re-crops are always re-derivable: crop (1040,0,w,880) of the 1440x900 shot = the map pane, 2.6x LANCZOS. The map pane shows ground (aerial or relief.jpg over site.corners) + the fitted plate as a red overlay + numbered anchor markers; the centre pane is the raw plate. [eval] lines in /tmp/audit_306c.log (if still present) hold per-doc resid/mpx/rot/placed.

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
