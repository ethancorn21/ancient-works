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
(2026-10-12, iteration 159, agent c - FIRST session. Driver built and ALL 36 shots taken and verified; no verdicts written yet. Next session starts judging, batch 1 below.)

**State.** `tools/audit_306d.mjs` is committed (adapted verbatim from 306c's driver: same IIFE, my 18 docs; the page API survived 307's rework - all of select/setGround/ensureSite/applyAll (a const arrow fn, grep `const applyAll` not `function`)/startFit/rvResolveRow/openPlan/refit/addPairMarker/`fit-prev`/`rel-<site>`/FQ still exist in this checkout's web/). One `server/serve.py --port 0` per run; re-runs skip existing PNGs (idempotent). All 36 shots are in `docs/site_flow/agent_fits/` (`<site>_<plan>.png` aerial + `_relief.png`; all 18 sites have relief.jpg). Every [eval] line verified: ok, img loaded, n = the doc's pair count, fit-prev drawn, zoom ~15, relLayer visible/none as expected, FQ (114 entries) emptied in-page so no queue blend. Full log was /tmp/aw306d_run159.log (ephemeral; the fit facts are in the table below). The ArcGIS `ERR_ABORTED` reqfail lines in the log are the live World_Imagery feed aborting at page close - expected, not a failure.

**Fit facts per doc (from the [eval] lines; aerial and relief agree per doc).** sim = similarity (mpx m/px, rot deg), view = homography (NO mpx/rot by design, PITFALLS L892: judge from the rendered ink, never the residual):
- bury-castle c_de779031cda8a0dc: sim 8 pts, resid 10.9-39, 2.63 m/px, +1.1 deg. (I viewed both shots this session: the drawn hachured hillfort ring lands on the real moated ring by the map's own "Burr Castle" label, upper right; prelim read: STAYS - confirm formally in batch 1.)
- cassiobury-house c_3446adfe7a8ed6c7: VIEW (Kip bird's-eye) 4 pts, resid 0 BY CONSTRUCTION - ink placement decides.
- chevening c_6049b89e4ab0570c: VIEW (Kip) 8 pts, resid 4.2-17.9.
- cooling-castle c_7ebc7630f3197364: sim 6 pts, resid 0, 0.8 m/px, 0 deg (Mackenzie 1897).
- coria c_d66bfb0db805d2cd: sim 6 pts, resid <=1.1, 1.19 m/px, 0 deg (Knowles 1909 Corbridge).
- daw-s-castle c_8d2281628567a166: sim 4 pts, resid <=5.6, 4.32 m/px, -0.1 deg (Somerset Map 1911).
- desborough-castle n0465_1: sim 8 pts, resid 0, 1.0 m/px, 0 deg (Allcroft 1908, IA book page).
- devil-s-dyke n0662_1: sim 4 pts, resid 0, 0.6 m/px, 0 deg (Allcroft 1908, SWEALD sheet).
- duffield-castle c_e915cbfd3af009b4: sim 8 pts, resid <=52.9, 1.74 m/px, 0 deg (Mackenzie 1897).
- eaton-socon-castle c_beefc3808de9b125: sim 4 pts, resid <=0.5, 0.99 m/px, 0 deg (1897 plan).
- framlingham-castle c_f43bc6196e097819: sim 8 pts, resid 0, 1.0 m/px, 0 deg (Mackenzie 1897).
- goodrich-castle c_cd89cb69f385859b: sim 4 pts, resid <=0.8, 0.84 m/px, 0 deg (Mackenzie 1897).
- gurnard-s-head n0262_1: sim 8 pts, resid 0, 0.4 m/px, 0 deg (Allcroft 1908, Castell-an-Dinas).
- hardknott-roman-fort c_7dcdfcc9aceb62ec: sim 8 pts, resid <=2.3, 2.29 m/px, 0 deg.
- herstmonceux-castle c_8eb122e93e31c3f6: sim 8 pts, resid <=74.6, 0.58 m/px, +0.7 deg (Mackenzie 1897).
- king-arthur-s-round-table c_cfc493f72253fa8e: sim 8 pts, resid <=40.8, 0.86 m/px, 0 deg (Rude Stone Monuments 0154).
- leicester-castle c_581a9f82b6a805a0: sim 6 pts, resid 0, 1.0 m/px, 0 deg (Mackenzie 1897).
- ludlow-castle c_b24730fd9038ae4a: sim 6 pts, resid <=31.7, 0.38 m/px, 0 deg (Mackenzie 1897).

**Judging rules (from 306b/306c's accepted verdicts; re-derive the pattern if unsure).** (1) The relief (LiDAR) is the deciding view where the aerial is uniform tree/crop; judge where the drawn works sit relative to the real banks/walls/ditches/streets. (2) resid 0 with mpx ~1.0 / rot 0 is NOT proof: 306b's "REJECTED AS FABRICATED" lines and 306c's serpent c_2c260a03d1f8df1c (resid 0, 1.0 m/px, 0 deg, yet ~4x too big and 145-190 m off) show grid-round or internally-consistent anchors can sit anywhere - for every resid-0 doc (cooling, desborough, devil-s, framlingham, gurnard, leicester) check the ink on the ground, and cross-check mpx against the plate's own scale bar where one is printed (the 306b method). (3) For the two VIEW docs, the residual proves nothing (homography); judge ink placement only. (4) A doc whose drawn subject sits on farmland/parcels with no matching real work, or at a grossly wrong scale (compare the drawn span to the real work's known size), is WRONG -> 303-way removal. (5) Line format: copy 306c's block (docs/site_flow.md L941+): source/title, model (n pts, resid, m/px, deg), what the lines sit on, verdict STAYS / "DELETED - an orphan today, invisible on the page (the 303 way: ...; the document was deleted <date>)". My block is a new section header after the 306c block (find its end; the 306c block ends before any later section): "306d - the 18 UK orphan documents (sites a-l): ..." with the same lead-in style.

**Removal recipe (only when a shot shows a wrong fit; the 303/306c way).** `fit/review.py upsert_item` pattern: put the doc's picture + its own points into the site's review item with the reason (see 306c's committed data/review item changes: `git log --oneline -- data/review/` then `git show <306c commit> -- data/review/ serpent-mound-q968802.earthworkenglan01allcgoog_n0558_2.json` etc. - note 306c's upserts are already on THIS branch, agent/c, unmerged to main: 9 US docs deleted, 3 US items upserted; my UK sites are disjoint from those), delete the doc file, re-export the site's review page file scoped to the site (never another site's item file). No overlay exists for orphans, so NO site_done.py rebuild is needed (306c didn't run it either); the site stays covered for the union check because the open item counts. `by: hand` docs: none of my 18 (all `by: agent`); don't touch other sites' docs/items.

**Next step (session N+1).** Judge batch 1 in task-file order: bury-castle (re-view both shots; prelim STAYS), cassiobury-house, chevening, cooling-castle, coria (10 shots; keep context small - max ~5 docs/session). Write their 5 lines into docs/site_flow.md (create the 306d block at that time; tick box 1 as its shots exist, box 2 as lines land). Sessions N+2+: remaining batches (daw-s..devil-s, duffield..goodrich, gurnard..hardknott, herstmonceux..king-arthur, leicester..ludlow). Final session(s): any removals + re-run the suite (disk is ~94% full: a full-suite run writes ~3.5G into /tmp/loop-* - if /tmp is tight, clean stale /tmp/loop-*/pytest-of-agent dirs first; a false ENOSPC red is the 306c rejection story) + tick boxes + done-claim. Baseline to beat (driver loop-start, PROGRESS 2026-10-11): test_gate pre-existing red; everything else green in my task's 2026-10-12 note (123 passed, 1 skipped) - re-verify the baseline if main moved since (the 307bb fit-queue test was red on agent/c because of 306c's marietta shift; human request 004 is open on that, do NOT touch 307bb's files or re-file 306c's claim).
