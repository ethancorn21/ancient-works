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
- [x] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
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
(2026-10-13, iteration 162, agent c - A/B of the bury-castle removal COMPLETE and airtight (zero new failures, both states identical in every scope); my 3 removal files are IN PLACE and committed this session. 1 of 18 docs judged (WRONG, removed). **NEXT STEP: batch 2 - judge cassiobury-house, chevening, cooling-castle, coria (+ daw-s-castle if the session has room).**)

**State (committed):** box 1 done (36 shots in docs/site_flow/agent_fits/, iteration 159 - the dir also holds 306a/b/c shots, do not touch those). Box 2: 1 of 18 lines written (bury-castle line in the "## The agent fits, looked at (task 306)" 306d block at the END of docs/site_flow.md - the block is tense-neutral, it grows with each batch). Box 3: 1 wrong fit dealt with (bury-castle removed the 303 way: D data/db/platefits/bury-castle-q5001077.c_de779031cda8a0dc.json, M data/review/...n0136_1.json = 2 candidates [n0136_1 lead intact + c_de779031cda8a0dc w/ 8 pairs, place_reason], M web/data/review.json page entry 2 candidates). Box 4 stays open until the final batch's suite run (its substance already holds, see A/B).

**A/B verdict (162, in DECISIONS):** full suite with my state = 9 failed, 133 passed, 1 skipped; each red reproduced identically with my 3 files at pristine HEAD (2-file pair run + 5-file run) - all pre-existing at HEAD 4aa6c95: 2 test_merge (211's open 222-228 gate), test_src_artists/limes/numancia check-staged-join, test_src_wiltshire_stukeley x3 (222-228 family; kip+mackenzie went green with 223/224 landing), and test_fit_queue placement_gestures which now fails at the SEED in BOTH states ("RESULT FAIL: seed: the gestures own the mouse (map pan/zoom off), the earlier overlay hidden") since 307's rework landed - 306c's open human request 004 is its owner, NOT 306d. test_gate: 3/3 pass in both states (the 10-12 "pre-existing red" note is stale). If main moves again, re-baseline by re-running just the red files (cheap, ~25 s) before blaming yourself.

**Batch 2 (next) and remaining docs.** Fit facts from the 159 [eval] lines (sim: resid m, m/px, rot deg; VIEW = homography, no mpx/rot - judge the INK only, the residual is meaningless by construction):
- NEXT: cassiobury-house-q5049456.c_3446adfe7a8ed6c7 (VIEW/Kip bird's-eye, 4 pts, resid 0) - the Kip view shows the house + park; judge what the fitted ink sits on. chevening-q1070927.c_6049b89e4ab0570c (VIEW/Kip, 8 pts, resid 4.2-17.9). cooling-castle-q5167493.c_7ebc7630f3197364 (sim, 6 pts, resid 0, 0.8, 0). coria-q3819299.c_d66bfb0db805d2cd (sim, 6 pts, resid <=1.1, 1.19, 0 - Knowles 1909 Corbridge). Optional 5th: daw-s-castle-q5242247.c_8d2281628567a166 (sim, 4 pts, resid <=5.6, 4.32, -0.1).
- Batch 3: duffield-castle-q2073299.c_e915cbfd3af009b4 (sim 8, resid <=52.9, 1.74, 0); eaton-socon-castle-q5331372.c_beefc3808de9b125 (sim 4, resid <=0.5, 0.99, 0); framlingham-castle-q2524183.c_f43bc6196e097819 (sim 8, resid 0, 1.0, 0); goodrich-castle-q5583571.c_cd89cb69f385859b (sim 4, resid <=0.8, 0.84, 0).
- Batch 4: gurnard-s-head-q5620199.earthworkenglan01allcgoog_n0262_1 (sim 8, resid 0, 0.4, 0); hardknott-roman-fort-q1584994.c_7dcdfcc9aceb62ec (sim 8, resid <=2.3, 2.29, 0); herstmonceux-castle-q2652207.c_8eb122e93e31c3f6 (sim 8, resid <=74.6, 0.58, +0.7).
- Batch 5 (final): king-arthur-s-round-table-q283800.c_cfc493f72253fa8e (sim 8, resid <=40.8, 0.86, 0); leicester-castle-q6519156.c_581a9f82b6a805a0 (sim 6, resid 0, 1.0, 0); ludlow-castle-q576369.c_b24730fd9038ae4a (sim 6, resid <=31.7, 0.38, 0).

**Resid-0/near-0 docs (cooling, coria, desborough, devil-s, framlingham, gurnard, leicester, + any other): ALWAYS dump the pairs from data/db/platefits/<doc>.json and check the (u,v) anchors for grid-round values (100-px ladders, uneven lon/lat steps) before trusting the fit** - the bury-castle trap: resid 0 with a degenerate anchor set proves nothing, and even NON-zero residuals can be pure grid inconsistency.

**Judging recipe (proven on bury-castle, 161/162).** (a) Reproduce the page's fit in .venv/bin/python: simFit = complex least squares merc = a*(u - i*v) + b with merc([lon,lat]) = [lon*pi/180*R, ln(tan(pi/4+lat*pi/360))*R], R=6378137; resid = |at(u,v)-Z|*cos(lat0) m; mpx = |a|*cos(lat0); rot = atan2(a_im,a_re) deg (page code: web/index.html L983 simFit, L343-344). (b) Find the drawn subject's centre/span in the RAW image (data/raw/commons/<site>/<hash16>.jpg, or books/<book>/<page>.jpg) with a 400-520 px PIL crop carrying a 50 m crosshair grid (ImageDraw on an RGB convert - 'L' mode rejects tuple fills), read with the read tool; density pixel stats are noisy (trees contaminate). (c) Map the image point through the fit to lon/lat; distance to the site point (web/data/sites.json) in GEOGRAPHIC metres: dx = dlon*111194.9266*cos(lat0), dy = dlat*110900 - never raw Mercator units (overstates 1.3-1.6x at 51 deg N). (d) Compare against the site's own clips: web/data/sites/<site>/relief.jpg and os1inch.webp (1600 px, 1 px = 1 m, centre = site point, y down = south), six-inch-1st.webp (1066 px, 1.5 m/px). (e) Independent cross-check: the plate's own scale bar (bottom of most Somerset/Allcroft plates: 'SCALE OF FEET 0-300') measured in the raw image vs the fit's mpx (bury: bar ~1.45 vs fit 2.634 = 1.8x). (f) Judge by numbers, not the screenshot: the page camera centres the SITE and the plate pane occludes the preview (bury's drawn ring was hidden behind the pane).

**Line format (306c/bury-castle style, at the end of docs/site_flow.md):** what the drawing's lines sit on (the real banks, walls, ditches, streets) + verdict: "KEEPS its document - <why it sits right>" or "DELETED - an orphan today, invisible on the page (the 303 way: ...)". One line per doc, appended in batch order.

**If a doc is wrong, remove it the 303 way (exactly what 161 did for bury):** fit/review.py API, no hand-edited JSON - upsert_item(root, site, [entry]) with entry = {plan (short, e.g. c_de779031cda8a0dc), title, url (media/... or books/... as in the doc), pairs (the doc's own), coarse:false, evidence (from the data/commons/files.jsonl row: rec 'evidence/1', kind 'category', checked date, site_cat/file_cat), label, cite, ref, size, place_reason '306d audit <date>: <one-paragraph verdict>. Document deleted.'} - appended to the site's EXISTING item (lead candidate stays first, item file name unchanged; create one only if the site has none - check data/review/<site>*.json first); then os.remove the doc; then export(root, site) - scoped to that ONE site, never another site's file. The site must stay covered for the union check (an open item counts; if the site had no item at all, the new open item covers it). Study 306c's committed items first: git log --oneline -- data/review/ + git show.

**Housekeeping.** No by:hand docs touched (the only platefit change so far is the one agent-doc deletion). Full-suite runs: df -h first (keep >=5G free; ~7G at 162 start), `.venv/bin/python -m pytest --ignore=tests/test_gate.py -q -p no:cacheprovider` (~4.5 min, ~3.5G into /tmp/loop-ancient-works.c/pytest-of-agent - rm -rf it after). A/B idiom is now a PITFALLS entry (in-checkout, changed files at HEAD; never a fresh worktree - it lacks the locally-built web/data/sites + data/raw). 306c's /tmp/aw306cab worktree is NOT mine - leave it.

Re-read: docs/site_flow.md (tail) - my 306d block: line format + the bury-castle line; extend this block, do not start a new section.
Re-read: fit/review.py:upsert_item/export - the exact call shapes before the next removal.
