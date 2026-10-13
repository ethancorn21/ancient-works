Status: done
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
(2026-10-13, iteration 200, agent c - **FINAL CLOSE**. Processed the human's answer to request
005: "LEAD: accepted. 306d is closed on main (12b2274); the reds it was blamed for were fixed
on main (77bdf5d)". Restored Status: done - that is the lead's own close (12b2274 set the file
to done on main); the driver's 122ac9e "resumed" put it back to in-progress on this branch only
to deliver the answer, exactly as f1ad899 did for 306c. This processes the answer; it is not a
new done-claim, and 005 stays closed - do not re-file it.)

**Expect the driver to reject the restore on this tree and re-open the file** (the 306c
precedent: I did exactly this at 199, the driver rejected it - ebe1228 - naming the one red).
The driver's re-check compares the suite against its known-failure set; on this checkout the
only red is agent a's in-flight 307 test
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser - re-ran at 200
(53 s): fails at the seed check "the gestures own the mouse (map pan/zoom off), the earlier
overlay hidden" plus 404s on GET /tiles/relief (live relief is off on this VM: Mac-only `aw`
DEM upstream - PITFALLS; the test and web/fitkit* are agent a's 307 Touches; agent a is
actively reworking 307). Not 306d's, not fixable from 306d's Touches.
**Recipe for the next session if the file comes back in-progress with a driver note:**
(1) sanity (30 s): 36 shots present (ls docs/site_flow/agent_fits/ | grep the 18 site
prefixes), the 306d block still has 18 bullets (grep -cE '^- ' between the '306d - the 18 UK
orphan documents' line and the '306e -' line), grep '306d audit' data/review/ = 14 files,
git diff --name-status main..HEAD contains no 306d deliverable;
(2) run that one 307 test (53 s): if it is STILL the only red (same seed-check + /tiles/relief
404 family), restore Status: done and commit again - the lead's decision stands, the red
clears via agent a's 307 merge (or the driver's baseline catching up); if ANY other test is
red, diagnose it before touching the status (that would be new information, not the known
red). Do not file an ask: 005 is answered, and this blocker is on its 1st/2nd attempt, not the
3rd (the stuck rule does not trigger).

**The audit itself (all on main; git diff main..HEAD = bookkeeping files only, so nothing
diverges).** 18/18 UK orphan docs (sites a-l) audited 2026-10-12/13: 36 shots in
docs/site_flow/agent_fits/ (<site>_<plan>.png aerial + _relief.png; all 18 sites have a
relief.jpg); 18 verdict lines in docs/site_flow.md's "## The agent fits, looked at (task
306)" 306d block (starts at the '306d - the 18 UK orphan documents' line, ends before the
'306e -' line: 18 bullets, one per doc); 14 WRONG fits deleted the 303 way - each deleted
plan appears exactly once in its site's review item with a '306d audit ... Document deleted.'
place_reason (14 item files, re-verified by grep at 200); 4 KEEPS (chevening,
cooling-castle, coria, daw-s); no by:hand doc touched. All 4 boxes were ticked and verified
before the first driver rejection (175); none has been edited since.

**Current store state (re-verified at 200; supersedes the 178 record's '4 KEEPS'):** ALL 18
docs are gone from data/db/platefits/ - the 14 by 306d's own 303-way deletions, and the 4
KEEPs by main's 212b final sync (6ce742f, iteration 227: the documented 301/303 line
behaviour - fabricated anchor pattern, grid-round page coordinates -> review item entry, doc
deleted; 306e's 198 hand-over is the full record). All 18 plans remain review-item
candidates at their sites (14 carry the 306d audit entry; the 4 KEEP sites' items carry
212b-style entries - why='line check: fabricated anchor pattern...', gate_score, no
place_reason). The anchor-pattern check overrode the visual KEEP verdict (the grid anchors
are what a screenshot cannot show). Nothing restores or re-upserts any of the 18; the 18
lines in docs/site_flow.md stand as the audit's record of the time (a KEEP line reads as the
audit verdict, not a live instruction). Sites stay covered for the union check (open items
count).

**Cleanup done at 200.** /tmp/aw306d_* deleted (the A/B logs/sh, handover_177, the item/
review mine copies, run159, siteflow_mine - 178 claimed this was done, it was not; the A/B
record is fully in DECISIONS 161/176/177). Kept: /tmp/j306d (batch3/4_remove.py + composites
= the record of the 16 place_reasons); /tmp/aw306cab (306c's, leave it to 306c's sessions);
the /tmp/aw306d_ab worktree was already gone (git worktree list clean).

**Remaining for agent c (other tasks, not 306d's):** 306e in-progress (last 2 sites'
303-way upserts + lines + task 807; recipe in its 198/199 hand-over) and 306f open (17
continental docs, all deleted on main by 6ce742f -> verdict work against the surviving item
entries; 306e's final form is the template). Task 806 (open) is likely MOOT now: it re-pins
fit_provenance's yeared-title test, and main's 77bdf5d (tasks 231-234) already re-pinned it -
verify at pick-up and drop it if so.
