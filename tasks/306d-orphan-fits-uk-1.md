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
(2026-10-13, iteration 178, agent c - **DONE**. Human request 005 settled by the lead's message:
the 5 reds are FIXED on main (commit 77bdf5d, tasks 231-234: site_done keeps covered review
entries, the Stonehenge item gained the Stukeley 1722 view so the plans.json 13->14 pin moved,
year-once re-pinned onto a surviving doc, tests derive counts). Merged main into agent/c
(88c5545; the two expected conflicts resolved the 306d way: web/data/review.json kept main's
newer 'at', docs/site_flow.md kept my 306c+306d blocks then main's 308 section after). Full suite
on the merged tree: **149 passed, 1 skipped, 1 red** - the lone red is
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, agent a's in-flight
307 seed flow (probe fails at 'seed: the gestures own the mouse'; 404 /tiles/relief - the live
relief is off on this VM, Mac-only `aw`), which the 161/176/177 A/Bs already proved failing on
pure main. No 306d red remains; no test fails that was not failing before 306d. Status set
done on the lead's instruction; the A/B record (DECISIONS 176/177) stands as the proof.)

**Superseded record - the 5 reds that 005 asked about, all now fixed on main (77bdf5d).**
| red | root | who clears it |
|---|---|---|
| fit_provenance::test_commons_yeared_title_drops_the_repeated_year | the pin bethlehem-q2523914.c_a164ee440558d66c is the 1748 Maastricht batch doc: 4ca9e2c (306a) re-pointed the test onto it (green at that commit - the doc existed), then the lead's 20277f3 "port from Mac: ... 3 fabricated Bethlehem docs removed" deleted it -> FileNotFoundError | task 806 (created this session; re-pin onto a surviving doc: fletio-q2072212.c_80f1e15c04bc5035 "Atlas de Wit 1698" label "c. 1698" recommended, durocortorum-q4896307.c_a60f570e6ce08f39 1894 alternative; fallback restores the doc into tests/golden/ from 20277f3^) |
| fit_provenance::test_line_refuses_unmarked_non_auto_doc + site_done::test_site_done_line (same root) | both pin exactly 13 stonehenge-q39671 candidates (test_fit_provenance.py:257, test_site_done.py:195); the lead's 20277f3 Mac-port plans.json lists 14: the 13 item candidates + source picture c_61b86efb4511e099 "Stonehenge, inward view by William Stukeley, 1722", which never had a store doc and is not an item candidate | a plans.json baseline decision (keep the row: re-pin 13->14 in both tests; drop it: re-export); recommend agent a's in-flight 212 (owns web/data/plans.json) or a driver-assigned small task after 212 |
| merge::test_new_sites_are_complete + merge::test_new_site_golden_samples | 211's four new sites (aardenburg-q955, the-hague-q36600, ostend-q12996, cambrai-q181285) carry their web/data/sites/ builds as per-checkout local artifacts (gitignored; only 58 site dirs tracked) - the dirs exist in NO checkout, main included, so the tests cannot pass on main as-is | agent a's 211/212 (in flight: 212 = "the final sync, the report") |

**CORRECTION to 176's record.** 176 lumped both fit_provenance reds as "bethlehem
FileNotFoundError". Wrong for line_refuses: its SID is stonehenge (test file L68); it fails at the
plans.json 13-row precondition (L257) - the same root as site_done_line (see
/tmp/aw306d_ab_main.log L3-38 and L142-149). Only commons_yeared pins bethlehem - and at 4ca9e2c
the bethlehem doc WAS the 1748 Maastricht doc (docstring, expected string and _build_source call
all name it; 306a's re-point was valid at the time). The deleter was the lead's 20277f3, not
306a. 176's "none of the 5 named tests reads either file" also over-stated it: line_refuses'
_preconditions_b does read web/data/review.json (a late check, after the plans.json check that
fails first; 306d's review.json still lists the stonehenge item, so that check passes).

**NEXT STEP (in order).**
(1) On the human's acceptance of 005 (a) - or the loop's 120-min answer with my recommendation:
set Status: done in this file and commit; the driver's re-check passes against the re-baselined red
set (no test fails that was not failing before: DECISIONS 176 A/B + the root causes above). Do NOT
re-file a done-claim while 005 is open (the 306c/004 pattern).
(2) If the human answers (b) (hold until green): stay in-progress; the 5 clear via 806 (when
merged) and 212 (final sync); re-file done once main's red set is back within the pre-306d
baseline.
(3) If the 5 simply go green on main before any answer: re-file Status: done directly (the A/B
stands as the record).
(4) After 005 is settled: tasks/806 is open (Depends on: none) and in the driver's queue - if it
has not been picked up, it is the one remaining 306d-adjacent red's fix; do not work it from this
task (it is its own task now).

**Cleanup.** rm -rf /tmp/aw306d_main (4.8G, the pure-main A/B copy); /tmp/aw306d_ab_{pristine,mine,
main}.log cited by DECISIONS 176-177, may go after that entry lands; /tmp/aw306d_mine2 (saved file
copies) confirmed restored at 176 - delete; /tmp/j306d keep (batch3/4_remove.py + composites = the
record of the 16 place_reasons).

**Final state (unchanged since 6da5393; re-verified 176 and 177).** 18/18 docs audited (36 shots in
docs/site_flow/agent_fits/); 4 KEEPS (chevening, cooling, coria, daw-s, all by:agent) and 14
DELETED the 303 way (bury, cassiobury, duffield, eaton, framlingham, goodrich, desborough,
devil-s, gurnard-s, hardknott, herstmonceux, king-arthur, leicester, ludlow) - each deleted plan
appears exactly once in a site review item with a '306d audit 2026-10-13: ... Document deleted.'
place_reason (5 new single-candidate items, 3 appends to iteration-50 open items; leads unchanged);
18/18 lines in the docs/site_flow.md 306d block; page file 342 open of 355; no by:hand doc
touched; the page file's 'at' timestamp in web/data/review.json is the known merge-conflict point
with agent a (keep the newer 'at').
