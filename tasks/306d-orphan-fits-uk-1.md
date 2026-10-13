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
(2026-10-13, iteration 169, agent c - merged main first (the review.json conflict was only the "at" timestamp; kept main's newer one). BATCH 3 COMPLETE: all four wrong fits removed the 303 way (duffield, eaton-socon, framlingham, goodrich) + their 4 site_flow lines written; page file now 337 open of 350. Suite: 7 failed / 140 passed / 1 skipped - all 7 A/B-verified pre-existing at merged HEAD (3 known baseline + 4 from agent a's merged 212/307/306a in-flight work). NEXT: batch 4 = the remaining 8 docs (recipe below).)

**State.** Box 1 done (36 shots, 159). Box 2: 10 of 18 lines in the 306d block - bury-castle DEL, cassiobury DEL, chevening KEEPS, cooling KEEPS, coria KEEPS, daw-s KEEPS, duffield DEL, eaton-socon DEL, framlingham DEL, goodrich DEL. Box 3: 6 removals executed (bury-castle + cassiobury at 161/166; the four batch-3 at 169). Box 4 open until the final batch's suite run. Everything committed (the merge commit, then this session's commit).

**Batch 3 removal details (record):** script /tmp/j306d/batch3_remove.py = the template for batch 4 (a REASONS dict of place_reasons, then per doc: upsert_item(ROOT, site, [entry]) with entry = {plan, title, url, evidence (fit/review.candidate_evidence(plan) - resolved all 4), pairs = the doc's own, coarse False, label/cite/ref/size from the doc, place_reason '306d audit 2026-10-13: ...'}; delete the doc; export(ROOT, site)). Changed-file set was exactly 9: 4 D docs; 3 NEW item files (duffield/framlingham/goodrich - single-candidate items, lead = their own plan); 1 M eaton item. EATON: the site already had an item (data/review/eaton-socon-castle-q5331372.earthworkenglan01allcgoog_n0285_1.json, since iteration 50, 6 candidates - none referencing the orphan doc, which is why it was classified orphan) so the upsert APPENDED c_beefc3808de9b125 as the 7th candidate (upsert_item replaces a candidate only when the item already holds that plan); lead n0285_1 and file name unchanged; the item was already open (no candidate had a doc) and stays open. Page file: 334/347 -> 335/348 -> 335/348 -> 336/349 -> 337/350.

**Batch 4 (the remaining 8, task-file order, each 1 doc 1 site):**
- desborough-castle-q5263651.earthworkenglan01allcgoog_n0465_1 - Allcroft 1908 n0465_1 'Desborough Castle, High Wycombe, Bucks' (book-page hillfort plan - the castle-neroche/daw-s class: judge summit/ditches against the OS clip and the aerial).
- devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0662_1 - Allcroft 1908 n0662_1 'SWEALD' (the plate is a LONG STRIP of the dyke - a long narrow subject: the chevening inverse test is weak for strips; judge where the drawn dyke line lands against the real Devil's Dyke (a ~5.6 km linear earthwork in the Sleaford uplands) on the OS clip + aerial; the plate may not span the whole dyke - judge what is drawn).
- gurnard-s-head-q5620199.earthworkenglan01allcgoog_n0262_1 - Allcroft 1908 n0262_1 'Castell-an-Dinas, Cornwall' (headland - the daw-s class: read the headland boundary overlay over the OS clip).
- hardknott-roman-fort-q1584994.c_7dcdfcc9aceb62ec - Commons Roman-fort plan (the coria class: hatched fort vs the OS outline; check the anchor grid's per-pixel spans).
- herstmonceux-castle-q2652207.c_8eb122e93e31c3f6 - Mackenzie 1897 (100-px grid: check for the ladder class BEFORE trusting residuals - framlingham proved a 0.0-resid perfect square can be pinned ~430 m off).
- king-arthur-s-round-table-q283800.c_cfc493f72253fa8e - 'Rude Stone Monuments 0154' (a stone-circles plate - the pyramid-mound concentric class is possible: judge the drawn circle's size + position vs the real circle(s)).
- leicester-castle-q6519156.c_581a9f82b6a805a0 - Mackenzie 1897 (same ladder check; Leicester Castle is on a rock spur ESE of the town).
- ludlow-castle-q576369.c_b24730fd9038ae4a - Mackenzie 1897 (same ladder check; the castle sits NW of the town, above the Dee).

**Per-doc judging recipe (all machinery in /tmp/j306d/, rebuild from the DECISIONS 163/164/168 entries if /tmp was cleared):**
1. `.venv/bin/python /tmp/j306d/j306d_fit.py <docid>` -> /tmp/j306d/<docid>_fit.json (resid, mpx, rot, anchors E/N, centre_EN; the PAGE model comes from the plans.json `view` flag, not the doc's `model`). web/index.html was last verified byte-identical at commit 939382a (165/168) - spot-check `git log --oneline -1 -- web/index.html` FIRST; if it moved (agent a's 307 rework is in flight), re-verify the port before trusting any residuals.
2. `.venv/bin/python /tmp/j306d/j306d_ink.py <docid>` -> the plate ink over the site's OS clip (the decisive judge for plan docs; ink mask = rgb.max(axis=2) > median+40 - NEVER axis=1) + read the plate itself (/tmp/j306d/<docid>_plate.png = the data/raw/commons/<site>/<hash>.jpg copy) to know what each drawn mass is.
3. The three decisive tests: (a) what the drawn WORKS (the subject, not the background) land on; (b) ANCHOR SHAPE - 100-px grid anchors: uniform per-pixel spans both axes = trustworthy transform (coria 118.8 m/100 px, daw-s 430 m/100 px, eaton 0.991 m/px); a 1.2-1.5:1 ladder = no similarity can hit (bury, duffield) - trust only the drawn-subject placement + the plate's own scale bar; (c) the CHEVENING test: inverse-map the site point through the doc's own fit (SIM inverse: u=(cU+dV)/den, v=(dU-cV)/den, U=X-b0, V=Y-b1, den=c^2+d^2, X/Y = the site point's Mercator; hom docs: inv() in j306d_fit.py) - inside the drawn subject = KEEPS (chevening (695,650)); at its garden front / 200+ m off = the miss class (cassiobury (549,671)); always round-trip at() at a few points before trusting an inverse (167's cross-term sign bug).
4. The aerials are the tie-breaker for scale/offset: read <docid>_aerial_{ink,half}_zoom.png + <site>_aerial17_zoom.png (j167_aerial.py + j167_aerial_composite.py - the 168-FIXED versions: crop box from the north/south corners, 4x retry with backoff).
5. Wrong fit -> the 303 way, exactly as batch 3: batch3_remove.py is the template (check `ls data/review/<site>*` first - an existing item gets the entry appended, or a same-plan candidate replaced). Right fit -> a KEEPS line.
6. Write each judged doc's ONE line at its ALPHABETICAL position in the 306d block of docs/site_flow.md (format = the existing lines). The block is currently: bury, cassiobury, chevening, cooling, coria, daw-s, duffield, eaton-socon, framlingham, goodrich - so batch 4 inserts: desborough + devil-s BEFORE duffield, gurnard-s AFTER goodrich, then hardknott, herstmonceux, king-arthur, leicester, ludlow after that (alphabetical).
7. Per batch: df -h (>=5G; rm -rf /tmp/loop-ancient-works.c/pytest-of-agent before the run if present - it grows ~3.5G, rm it after) -> `.venv/bin/python -m pytest --ignore=tests/test_gate.py -q -p no:cacheprovider` (~4 min) -> the reds must equal the 7-red baseline below (if they DIFFER: first `git log --oneline -10 -- web/data/plans.json data/db/platefits/ tests/` for agent a's new main merges, then in-checkout A/B per the PITFALLS idiom: copy my changed files to /tmp/aw306d_mine/, git checkout them + rm my new files, re-run just the failing test files, restore, verify git status; worktree A/B is INVALID here - locally-built site data is not in git). Commit after each batch. When the 8th line lands and the final suite matches the baseline, boxes 2-4 can be ticked.

**Reds baseline at merged HEAD (A/B-verified this session - 7 failed):**
1. test_fit_queue::test_placement_gestures_and_save_in_the_browser (307/306c request-004 family; fails at the seed check, dep:null).
2. test_merge::test_new_sites_are_complete + 3. test_merge::test_new_site_golden_samples (agent a's 211/222-228 open gate).
4. test_fit_provenance::test_line_refuses_unmarked_non_auto_doc + 5. ::test_commons_yeared_title_drops_the_repeated_year (FileNotFoundError on the bethlehem-q2523914.c_a164ee440558d66c.json the fixtures reference - that doc was DELETED ON MAIN by 306a; the tests predate the deletion).
6. test_merge::test_plan_list_refresh_is_pure_growth + 7. test_site_done::test_site_done_line (plans.json: stonehenge-q39671 lists 14 candidates against the expected 13 - 211/212's in-flight plans work).
All 7 are agent a's in-flight work (212/307/306a), not 306d's; none of the driver's 4 loop-start reds (batch_eu x2, gate, serve) remain - they were fixed on main.

Re-read: /tmp/j306d/batch3_remove.py - the removal template (the REASONS format + the upsert/delete/export sequence).
Re-read: fit/review.py L80 upsert_item + L156 resolved_doc + L189 export - the exact call shapes (verified 169).
Re-read: docs/site_flow.md (tail) - the 306d block (10 lines now; next: desborough, devil-s).
