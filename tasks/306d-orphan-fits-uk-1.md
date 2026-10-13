Status: in-progress
# 306d: Look at the orphan agent fits, UK part 1 (a-l) - 18 docs, 18 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306d.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 18
UK platefit documents with `by: agent` (sites a-l) that are ORPHANS - in the store, but with no
overlay built on the site and not referenced by any review item, so a visitor sees them not at
all. Render each the way the page would if it ever showed it: the fit tool over the aerial
photograph, and over the LiDAR relief where the site has a `relief.jpg`, with the doc's stored
pairs placed. The verdict records where the doc stands today (invisible) and whether the
placement is good enough to keep.

## Acceptance criteria
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief where the site has one), taken with `tools/shot.mjs` against `server/serve.py
      --port 0` on this checkout (recipe in the parent's Hand-over; GET only, ephemeral port).
- [ ] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on (the real banks, walls, ditches,
      streets) and the verdict (keeps its document / deleted - and it is an orphan today,
      invisible on the page).
- [ ] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (`fit/review.py upsert_item`
      pattern), the document is deleted, and the site's review page file is re-exported scoped
      to the site (never another site's item file). The site stays covered for the union check
      (an open item counts). A fit that sits right keeps its document, and its line says so.
- [ ] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (18, 18 sites)
- bury-castle-q5001077.c_de779031cda8a0dc - Bury Castle Somerset Map
- cassiobury-house-q5049456.c_3446adfe7a8ed6c7 - Cassiobury House, bird's-eye view engraved by Johannes Kip
- chevening-q1070927.c_6049b89e4ab0570c - Chevening, bird's-eye view engraved by Johannes Kip
- cooling-castle-q5167493.c_7ebc7630f3197364 - Cooling Castle, plan from Mackenzie, The Castles of England (1897)
- coria-q3819299.c_d66bfb0db805d2cd - Knowles 1909, Corbridge Excavations, fig 1 site plan
- daw-s-castle-q5242247.c_8d2281628567a166 - Daws Castle Somerset Map
- desborough-castle-q5263651.earthworkenglan01allcgoog_n0465_1 - Desborough Castle, High Wycombe, Bucks (Allcroft 1908)
- devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0662_1 - SWEALD (Allcroft 1908)
- duffield-castle-q2073299.c_e915cbfd3af009b4 - Duffield Castle, plan from Mackenzie, The Castles of England (1897)
- eaton-socon-castle-q5331372.c_beefc3808de9b125 - Plan of Eaton Socon (1897)
- framlingham-castle-q2524183.c_f43bc6196e097819 - Framlingham Castle, plan from Mackenzie, The Castles of England (1897)
- goodrich-castle-q5583571.c_cd89cb69f385859b - Goodrich Castle, plan from Mackenzie, The Castles of England (1897)
- gurnard-s-head-q5620199.earthworkenglan01allcgoog_n0262_1 - Castell-an-Dinas, Cornwall (Allcroft 1908)
- hardknott-roman-fort-q1584994.c_7dcdfcc9aceb62ec - Hardknott Roman Fort
- herstmonceux-castle-q2652207.c_8eb122e93e31c3f6 - Herstmonceux Castle, plan from Mackenzie, The Castles of England (1897)
- king-arthur-s-round-table-q283800.c_cfc493f72253fa8e - Rude Stone Monuments 0154
- leicester-castle-q6519156.c_581a9f82b6a805a0 - Leicester Castle, plan from Mackenzie, The Castles of England (1897)
- ludlow-castle-q576369.c_b24730fd9038ae4a - Ludlow Castle, plan from Mackenzie, The Castles of England (1897)

## Hand-over
(2026-10-12, iteration 160, agent c - batch 1 judging, doc 1 of 5. **bury-castle is WRONG (the previous session's prelim STAYS is DISPROVEN)**; 0 of 18 lines written, 0 removals done. Next: write the 306d block header + the bury-castle line, then judge cassiobury-house.)

**State.** All 36 shots committed (iteration 159; `docs/site_flow/agent_fits/`, `tools/audit_306d.mjs` committed, the IIFE recipe and [eval] verification are in the DECISIONS entry of 2026-10-12 306d and still valid). No repo files changed this session (investigation + /tmp scripts only). `docs/site_flow.md` is 1046 lines; the 306c block ends at the pyramid-mound STAYS line (~L1043) - my new 306d block goes after it (the file has no later section; verify before writing).

**bury-castle-q5001077.c_de779031cda8a0dc = WRONG, to be deleted the 303 way (line 1 of my block).** The evidence (all computed, not eyeballed):
- The doc's 8 stored pairs are 4 distinct points on a 100-px grid: (100,100), (100,300), (100,400) on the left edge (a 1D ladder) + (400,400). Their lon/lat values are uneven (200 px -> 0.0053896 deg lat, then 100 px -> 0.0017967 - a 1.5:1 ratio), so a similarity cannot hit them: the 10.9-39 m residuals measure the grid's internal inconsistency only (the exact 306b "REJECTED AS FABRICATED" / 306c serpent c_2c260a03d1f8df1c pattern).
- The page's own simFit reproduced exactly (index.html L983 `function simFit`, `merc` L343-344, `R = 6378137` L342; complex least squares `merc = a*(u - iv) + b`): resid [35.5, 24.9, 10.9, 39, ...] m, 2.634 m/px, +1.06 deg - identical to the committed shot's [eval] line, so this IS the placement the shot shows.
- The drawn hachured hillfort ring (centre at raw-image px ~(248,115) of the 590x475 Commons file, outer span ~103x130 px) maps through that fit to (-3.518434, 51.036988) = 576 m from the site centre (Wikidata Q5001077 = the real hillfort: -3.51531, 51.0322) and 535 m from the real OS "Burr Castle (Remains of)" hachured ring (measured on the site's own clipped web/data/sites/bury-castle-q5001077/six-inch-1st.webp and its relief.jpg: ring +22 m E / -55 m N of the site centre; the LiDAR bump is there too). Bearing N22W: the drawn ring lands on the Clump of Firs / Peter's Piece plantation hill. Drawn ring 271x342 m vs the real ~130 m hillfort - ~2x too big on top of ~2x off-centre.
- Why the eye missed it in the shots: the map camera centres the SITE (a throwaway headless run - audit driver's IIFE plus `map.getCenter()/getZoom()/getPadding()` and `map.project(lon/lat)` in the [eval]; script pattern still at /tmp/measure_306d.mjs if it survives) reports centre = site, zoom 15, padding left ~976, site centre at screen (1198,450); the fitpane (the plate pane) spans x 0..1062, so the drawn ring (screen (1052,95)) is mostly HIDDEN BEHIND THE PLATE PANE - the shot looks like a plate over red OS ink with no visible discrepancy. Judge by the numbers, not the screenshot, when the pane occludes the preview.
- Its line (306c format): Somerset Map 1911 (Bothamley), similarity (8 pts, resid 10.9-39, 2.63 m/px, +1.1 deg): the drawn hachured hillfort sits ~540-576 m N-NW of the real Burr Castle hillfort, on the Clump of Firs/Peter's Piece hill, at ~2x the real ~130 m size; the 8 anchors are a 100-px grid ladder (three on the left edge) whose uneven spacing the 10.9-39 m residuals only measure - placement wrong. DELETED - an orphan today, invisible on the page (the 303 way: ...).

**Removal (do in the session that writes this line, box 3).** 306c/303 way: upsert bury-castle's picture + its own 8 points into the site's review item with this reason (fit/review.py upsert_item pattern; study 306c's committed data/review changes first: `git log --oneline -- data/review/` + `git show` the serpent-mound item), delete data/db/platefits/bury-castle-q5001077.c_de779031cda8a0dc.json, re-export the site's review page file scoped to bury-castle only. No overlay exists (orphan) -> no site_done.py. Then tick box 3 for this doc (keep the box unticked until all wrong fits in the 18 are dealt with; box 2 as each line lands; box 1 is tickable now - all 36 shots exist and were verified in 159).

**Batch 1 remaining (4 docs, 8 shots) - next session after bury's line:** cassiobury-house-q5049456.c_3446adfe7a8ed6c7 (VIEW/Kip bird's-eye, 4 pts, resid 0 BY CONSTRUCTION - judge ink only), chevening-q1070927.c_6049b89e4ab0570c (VIEW/Kip, 8 pts, resid 4.2-17.9 - judge ink), cooling-castle-q5167493.c_7ebc7630f3197364 (sim, 6 pts, resid 0, 0.8 m/px, 0 deg - resid-0: check anchor grid-ness in the doc JSON + ink on the ground + scale bar), coria-q3819299.c_d66bfb0db805d2cd (sim, 6 pts, resid <=1.1, 1.19 m/px, 0 deg - Knowles 1909 Corbridge; same resid-0 checks). The resid-0 docs (also desborough, devil-s, framlingham, gurnard, leicester in later batches): always dump the pairs from data/db/platefits/<doc>.json and look for grid-round u/v before trusting the fit (the bury-castle trap: even NON-zero residuals can be pure grid inconsistency).

**Judging toolbox that worked (reuse it).** (a) Reproduce the page's fit in .venv/bin/python: simFit math as above; the doc's pairs are the 4-tuples in its JSON. (b) Find the drawn subject's centre in the RAW image (data/raw/<src>/<hash>.jpg - for Commons docs `data/raw/commons/<site>/<hash>.jpg`) by cropping (PIL) and viewing, or by pixel density; measure its span. (c) Map that image point through the fit to lon/lat; compare with the site centre (web/data/sites.json `lon`/`lat` = the Wikidata point) and with the real subject's position on the site's own clipped maps (web/data/sites/<site>/six-inch-1st.webp, relief.jpg, os1inch.webp - 1.6 km square, 1 px = 1 m on the 1600 px relief). (d) Where a shot's camera is in doubt, the throwaway headless [eval] pattern reports map.getCenter/getZoom/getPadding + map.project of any lon/lat. (e) Optional visual: rasterise the raw image through the fit's inverse (Mercator complex inverse: ainv = conj(a)/|a|^2 applied to Z - b) over the site's clipped OS/relief - the /tmp version of this had a tuple-division bug (`ainv = (ar,-ai)/(ar*ar+ai*ai)` - fix by computing the two components separately, and delete the dead `inv()` fn referencing undefined `inv_uv`); the numbers above already settle bury without it.

**Rest of the task (unchanged from 159).** Fit facts per doc (from the [eval] lines): bury-castle sim 8 pts resid 10.9-39 2.63 +1.1 (WRONG, above); cassiobury VIEW 4 pts resid 0; chevening VIEW 8 pts resid 4.2-17.9; cooling sim 6 pts resid 0 0.8 0; coria sim 6 pts resid <=1.1 1.19 0; daw-s-castle sim 4 pts resid <=5.6 4.32 -0.1; desborough n0465_1 sim 8 pts resid 0 1.0 0; devil-s-dyke n0662_1 sim 4 pts resid 0 0.6 0; duffield sim 8 pts resid <=52.9 1.74 0; eaton-socon sim 4 pts resid <=0.5 0.99 0; framlingham sim 8 pts resid 0 1.0 0; goodrich sim 4 pts resid <=0.8 0.84 0; gurnard-s-head n0262_1 sim 8 pts resid 0 0.4 0; hardknott sim 8 pts resid <=2.3 2.29 0; herstmonceux sim 8 pts resid <=74.6 0.58 +0.7; king-arthur-s-round-table sim 8 pts resid <=40.8 0.86 0; leicester sim 6 pts resid 0 1.0 0; ludlow sim 6 pts resid <=31.7 0.38 0. (VIEW docs: homography, no mpx/rot - judge ink only.) Batches of ~5 docs/session: (daw-s..devil-s), (duffield..goodrich), (gurnard..hardknott), (herstmonceux..king-arthur), (leicester..ludlow). Line format: the 306c block (docs/site_flow.md L941+). Bigger batches or a full-suite run: check disk first (df -h; a suite run writes ~3.5 G to /tmp/loop-*) - at session start 160 the disk was 84% (7.6 G free, enough). Suite baseline: 123 passed, 1 skipped, test_gate pre-existing red (2026-10-12 note; re-verify if main moved - the 307bb fit-queue red is 306c's open human request 004, do not touch). Do not touch `by: hand` docs or other sites' items.
