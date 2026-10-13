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
- [x] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on (the real banks, walls, ditches,
      streets) and the verdict (keeps its document / deleted - and it is an orphan today,
      invisible on the page).
- [x] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (`fit/review.py upsert_item`
      pattern), the document is deleted, and the site's review page file is re-exported scoped
      to the site (never another site's item file). The site stays covered for the union check
      (an open item counts). A fit that sits right keeps its document, and its line says so.
- [x] No `by: hand` document is touched; no new test failures against the driver's newest
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
(2026-10-13, iteration 175, agent c - **task done.** Batch 4's 8 removals (the last UK orphan
docs, all judged WRONG) were executed at 174 and committed by the driver as 6da5393; this
session ran the final suite, ticked boxes 2-4 and closed the task. Nothing left to do; no
Re-read items.)

**Final state (all in commit 6da5393 on this branch):**
- All 18 docs in the list above audited (box 1: 36 shots in docs/site_flow/agent_fits/, done at
  159): 4 KEEPS - chevening, cooling, coria, daw-s (their fits sit on the real works; they keep
  their documents) - and 14 DELETED the 303 way: bury-castle + cassiobury (batches 1-2,
  161/166), duffield + eaton-socon + framlingham + goodrich (batch 3, 169), desborough +
  devil-s-dyke + gurnard-s + hardknott + herstmonceux + king-arthur + leicester + ludlow
  (batch 4, 174). Each deletion: the picture + the doc's own points upserted into the site's
  review item with a '306d audit 2026-10-13: ... Document deleted.' place_reason (book docs as
  url 'books/<ia>/<file>' + book/ia/file, commons docs with ref/size), the doc deleted from
  data/db/platefits, the site's page file re-exported scoped to the site.
- All 18 lines in docs/site_flow.md's 306d block (alphabetical), each stating what the lines
  sit on and the verdict.
- Review items: 5 new single-candidate items (desborough, hardknott, herstmonceux, leicester,
  ludlow) + 3 appends to pre-existing open items (devil-s n0599_1 item += n0662_1; gurnard
  n0076_1 item += n0262_1; king-arthur c_984782b9e35e8ded item += c_cfc493f72253fa8e - leads and
  filenames unchanged, items stay open). Page file 342 open of 355 total (13 resolved not
  exported); all 18 sites stay covered for the union check (an open item counts).
- Suite (iteration 175, `.venv/bin/python -m pytest --ignore=tests/test_gate.py -q -p
  no:cacheprovider`, 231 s): 6 failed, 141 passed, 1 skipped = the 169 A/B-verified 7-red
  baseline MINUS test_merge::test_plan_list_refresh_is_pure_growth, which main fixed (aeeb5aa's
  plans.json re-export; the test reads only plans.json / plans_premerge_keys.jsonl /
  files.jsonl - never review.json). The remaining 6 reds are all agent a's in-flight work
  (307/306c-request-004 placement-gestures; 211/222-228 merge gate x2; the 2 fit_provenance
  reds on the bethlehem doc 306a deleted on main; 212's stonehenge 14-vs-13 plans.json row).
  ZERO new reds from this task's 18 files -> box 4 holds.

**Notes for the parent's remaining work (306e/306f, the other UK/continental orphan docs):**
the whole machinery (fits, inks, aerial composites, the batchN_remove.py template, the
site_flow-line format, the 303 way, the in-checkout A/B idiom) is recorded in DECISIONS entries 159-175 (the driver moves this task's entries to DECISIONS-archive.md when it
closes) and the batch-3/4 hand-over stacks in the archive;
/tmp/j306d survives with batch3_remove.py + batch4_remove.py (the record of all 16 place_reasons)
and the 171-174 composites. The page file's 'at' timestamp in web/data/review.json is the
known merge-conflict point with agent a (keep the newer 'at').
