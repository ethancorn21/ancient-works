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
(2026-10-13, iteration 166, agent c - cassiobury judged WRONG and removed the 303 way (the 165 judge images had a 256x scale bug that masked the miss); all five batch-2 lines written; the 3 remaining reds A/B-proven pre-existing. **NEXT: batch 3 - duffield, eaton-socon, framlingham, goodrich (all Mackenzie 1897, sim); then the remaining 8.**)

**State.** Box 1 done (36 shots, 159). Box 2: 6 of 18 lines in the 306d block (bury-castle DEL, cassiobury DEL, chevening/cooling/coria/daw-s KEEPS). Box 3: 2 removals executed (bury-castle, cassiobury - both the 303 way). Box 4 open until the final batch's suite run. The committed tree now carries: my 3 cassiobury files (D doc `data/db/platefits/cassiobury-house-q5049456.c_3446adfe7a8ed6c7.json`, M `web/data/review.json` 334 open of 347, NEW `data/review/cassiobury-house-q5049456.c_3446adfe7a8ed6c7.json` = single open candidate with the full place_reason) + the 5 site_flow lines + 4 PITFALLS entries.

**cassiobury (DELETED, the key facts for the line already written):** the 165 judge images were built with mpp = (360/2^z·111194.93·cos lat) - per TILE, not per pixel (missing /256) - so every marker was drawn 1-2 px from the site point and the fit looked concentric. Rebuilt at 0.74 m/px (z17): drawn house (E -364..-47, N +179..+427, 360 m NW) = the Cassiobury school complex (playfields + rectangular pool) where no house stood; drawn oval pond (E +406, N -202, 453 m SE) = mid-residential, no water; plate wood masses map EAST while the real park (woods, round lake, River Gade) is WEST. The Wikipedia Q5049456 infobox (51.66500N 0.41889W) == the catalog site point EXACTLY: the house was demolished 1927 and its site is now the Temple Close/Parkside Drive housing - so the fit's house is 360 m off its own site. 165's "1933 replacement house" hypothesis is dead (that is the Bedford-NY house built from these bricks; the only survivor is the Grade II stables, Cassiobury Court).

**Batch 3 (NEXT STEP) - all four Mackenzie 1897 plans, similarity model:**
- duffield-castle-q2073299.c_e915cbfd3af009b4 - Duffield Castle, plan from Mackenzie
- eaton-socon-castle-q5331372.c_beefc3808de9b125 - Plan of Eaton Socon (1897)
- framlingham-castle-q2524183.c_f43bc6196e097819 - Framlingham Castle, plan from Mackenzie
- goodrich-castle-q5583571.c_cd89cb69f385859b - Goodrich Castle, plan from Mackenzie
Then the remaining 8 in task-file order: desborough-castle (Allcroft n0465_1), devil-s-dyke (Allcroft n0662_1, 'SWEALD'), gurnard-s-head (Allcroft n0262_1, Castell-an-Dinas), hardknott-roman-fort, herstmonceux-castle (Mackenzie), king-arthur-s-round-table (Rude Stone Monuments 0154), leicester-castle (Mackenzie), ludlow-castle (Mackenzie).

**Judging recipe (as 163-166, all in /tmp/j306d/):**
1. `.venv/bin/python /tmp/j306d/j306d_fit.py <docid>...` - EXACT port of web/index.html simFit L983-1004 + homFit L1014-1053 (incl. the page's solve()); verified byte-identical at 165 and web/index.html's newest commit (939382a) PRE-DATES that verification, so it still stands - spot-check anyway (`git log --oneline -1 -- web/index.html` should still say 939382a; if not, re-verify the port). Writes /tmp/j306d/<docid>_fit.json (H/Hi/a/b, resid, mpx, rot, anchors E/N, centre_EN; reads data/db/platefits/<docid>.json + sites.jsonl/extras.jsonl + web/data/plans.json `view` flag - the PAGE model comes from plans.json's row `view`, not the doc's `model`).
2. Judge (plan docs): `.venv/bin/python /tmp/j306d/j306d_ink.py <docid>...` -> <docid>_ink_on_<osmap>.png (plate INK over the site's OS clip: os1inch.webp or six-inch-1st.webp per web/data/sites/<site>/; the decisive judge - plate lines and map lines at once) + the plain composite. Read the plate itself (/tmp/j306d/<docid>_plate.png or re-fetch) to know what each drawn mass is.
3. The three decisive tests: (a) what the drawn WORKS (the subject, not the background) land on in the composite; (b) ANCHOR SHAPE - 100-px grid anchors: if per-pixel spans are uniform in both axes (coria 118.8 m/100 px, daw-s 430 m/100 px) the grid encodes the true transform (snapped) and the fit is trustworthy; if a 1.5:1 ladder (bury) no similarity can hit it and the residuals measure only the grid's inconsistency - then trust only the drawn-subject placement vs the OS/real ground, and check the plate's own scale bar (daw-s's bar is 4.9x off, bury's 1.8x - both flagged in their lines); (c) the CHEVENING test: the site point inverse-mapped through the doc's own fit (inv() in j306d_fit.py) - where does it land on the plate? (inside the drawn subject = strong KEEPS signal, as chevening; on its front garden 200-300 m off = the miss class, as cassiobury).
4. Wrong fit -> the 303 way EXACTLY as this session did for cassiobury: fit/review.py upsert_item(root, site, [entry]) (entry: plan, title, url, evidence from the data/commons/files.jsonl row for that site+ref - NOTE files.jsonl is JSONL, json.loads per line - or the books row, pairs = the doc's own, coarse false, label/cite/ref/size from the doc, place_reason '306d audit 2026-10-13: ... Document deleted.'), then delete the doc file, then export(root, site) (the site stays covered: an open item counts). If the site already has an item file (check `ls data/review/<site>*`), the entry is appended to it (lead order = candidates[0].plan; a changed lead moves the file - upsert_item handles it).
5. Write each judged doc's ONE line at its ALPHABETICAL position in the 306d block of docs/site_flow.md (the block ends at the tail of the file; format = the cassiobury/bury lines: doc id - source (points, model, resid, m/px, rot): where the lines sit + caveats. KEEPS/DELETED - an orphan today, invisible on the page (the 303 way: ...)). Extend the block; do not start a new section.

**Tests (only when docs were deleted in the session):** df -h first (keep >=5G free; rm -rf /tmp/loop-ancient-works.c/pytest-of-agent before the run; it grows ~3.5G and I rm it after) -> `.venv/bin/python -m pytest --ignore=tests/test_gate.py -q -p no:cacheprovider` (~4.5 min) -> current baseline at HEAD (166): exactly 3 failed - test_fit_queue::test_placement_gestures_and_save_in_the_browser (307/306c request-004 family) + test_merge::test_new_sites_are_complete + test_new_site_golden_samples (agent a's 211/222-228 gate; the other six 162-baseline reds were fixed on main between 162 and 166) - if the reds DIFFER, in-checkout A/B per the PITFALLS entry (copy my changed files to /tmp/aw306d_*_mine, git checkout them + rm new files, re-run just the failing test files, restore, re-verify git status).

Re-read: /tmp/j306d/j306d_fit.py + /tmp/j306d/j306d_ink.py - the judging machinery (rebuild from the DECISIONS 163/164 entries if /tmp was cleared; the 163 PNG composites for batch 2 survive in /tmp/j306d/).
Re-read: docs/site_flow.md (tail) - the 306d block (6 lines now; next alphabetical: desborough-castle).
Re-read: fit/review.py:upsert_item/export - the exact call shapes before any removal (this session's cassiobury script is the template; it is in the DECISIONS 166 entry's git diff).
Re-read: the batch-3 plate docs in data/db/platefits/ (4 Mackenzie plans) - pairs are all 100-px-snapped; check each anchor set's per-pixel spans for the ladder class before trusting residuals.
