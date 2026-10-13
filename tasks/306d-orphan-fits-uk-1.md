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
(2026-10-13, iteration 176, agent c - **the 175 done-claim was REJECTED by the driver (8200a33):
5 named "new" failures; this session proved all 5 fail on main itself (A/B, two independent
methods) - none is caused by 306d. Work has been COMPLETE and committed since 6da5393; the
task is waiting on the human (request 005, filing is the next step) - do not re-file a
done-claim while 005 is open, exactly as 306c does while 004 is open. No Re-read items.)

**What the driver rejected.** 8200a33 names 5 tests "failing that were not failing before
this task": test_fit_provenance::{test_commons_yeared_title_drops_the_repeated_year,
test_line_refuses_unmarked_non_auto_doc}, test_merge::{test_new_site_golden_samples,
test_new_sites_are_complete}, test_site_done::test_site_done_line. It does NOT name
test_fit_queue::test_placement_gestures_and_save_in_the_browser (it attributes that one to
306c: .agent/reports/new-failures-306c.txt; the same file .agent/reports/new-failures-306d.txt
holds my 5). My 175 entry's premise ("no A/B was needed") was wrong: the driver's baseline
is not my 169-verified 7-red baseline.

**The A/B (this session, both methods conclusive; details in the DECISIONS 176 entry).**
(1) In-checkout (the PITFALLS idiom): 306d's 14 deleted docs restored from baseline 6374286
(pre-159), the 14 item files (9 new deleted, 5 appended restored to 6374286), the 36 shots
and tools/audit_306d.mjs removed; site_flow.md + web/data/review.json deliberately left as-is
(the main side changed them after 6374286 - mostly deletions - and NO driver-named test
reads either file). Ran the 6 tests (my 5 + fit_queue): ALL 6 FAIL, byte-identical
signatures to the with-my-changes run (logs /tmp/aw306d_ab_{pristine,mine}.log). Restored;
git status clean (0 delta) at the limit. (2) Pure main (735ec66 = the tip my branch merged
via 6eb4f99, contains NONE of agent/c's 306a/c/d work beyond main's own): copied the main
checkout to /tmp/aw306d_main (4.8G; main's .venv; .git/.venv excluded - none of the 5 needs
git), ran the 5: ALL 5 FAIL with the same messages (log /tmp/aw306d_ab_main.log). They are
main's own reds, independent of anything agent/c ever did:
- fit_provenance x2: FileNotFoundError data/db/platefits/bethlehem-q2523914.
c_a164ee440558d66c.json - the doc 306a deleted ON MAIN (absent in the main checkout too).
  306a's merge commit 4ca9e2c re-pointed 5 audit-broken provenance tests to surviving docs
  but these two still pin bethlehem (test_line_refuses via SEED_PLAN/_golden_doc/_build_tree_b;
  grep the main log for test_commons_yeared's exact failing line next session - only ONE
  FileNotFoundError appears in each log, so confirm each test's own failure mode).
- merge x2: aardenburg-q955 "no web/data/sites directory" and the-hague-q36600 "missing
  relief.jpg" - 211's new-site builds are per-checkout LOCAL artifacts (web/data/sites is
  gitignored except 58 files); the four sample site dirs (aardenburg, the-hague, ostend,
  cambrai) exist in NO checkout, main included -> these two tests cannot pass on main as-is.
- site_done: plans.json lists 14 stonehenge-q39671 rows vs the expected 13 - aeeb5aa
  (233+234, lead) re-exported plans.json on main; identical 14 on main and on my branch.

**Fresh-eyes spot-check of the final state (all clean, matches 175's record):** 14 docs
absent / 4 kept present with by:agent (chevening, cooling, coria, daw-s); each deleted doc's
plan appears exactly once in an item with a '306d audit ...' place_reason; page file in sync
(342 open of 355 per fit/review.py resolved_doc - 13 resolved excluded; an earlier quick
heuristic said 341, that was the heuristic, not the file); 18/18 site_flow lines present
exactly once each in the 306d block.

**NEXT STEP (in order).** (1) Create tasks/806-*.md: "Fix the two fit_provenance tests that
still pin the bethlehem doc 306a deleted on main" - lowest free number in 800-1099 (800-805
taken), Status: open, `Depends on: none` (all owners 303/219/306a are done), Touches:
tests/test_fit_provenance.py (plus tests/golden/ only if the re-point needs a golden change;
keep one module per task), goal: re-point them the 306a way (4ca9e2c) to surviving docs so
main's suite loses these 2 reds; before writing, confirm each test's exact failing line in
/tmp/aw306d_ab_main.log. (2) File ask_human request 005 (blocking=true, NOT human_only,
number = next free in .agent/asks/ after 004), self-contained: 306d's 18-doc UK orphan audit
is complete and committed (batches at 161/166/169/174, final tree 6da5393, 4 KEEPS + 14
DELETED the 303 way, 36 shots, 18 lines); the driver rejected the 175 done-claim on the 5
tests above; A/B in DECISIONS 176 shows all 5 fail on main itself (bethlehem x2 = 306a on
main; merge x2 = 211 per-checkout artifacts no checkout has; site_done = aeeb5aa's plans.json
re-export) and fail identically with 306d's changes reverted; recommend (a) accept 306d as
done and add the 5 to the driver's known-failure baseline - same class as open request 004
(306c) - and let the reds clear on their own (merge/site_done with agent a's 211/212 final
sync; the fit_provenance pair via new task 806); (b) hold 306d until the 5 go green on main;
(recommend: a). (3) Keep Status: in-progress while 005 is open (306c's exact pattern: no
re-filed done-claim while the request is pending; the loop answers with my recommendation
after 120 min of silence). (4) Commit the task file + DECISIONS + 806. On the human's
acceptance (or the loop's 120-min answer): set Status: done and commit - the driver's
re-check will then pass against the re-baselined red set. If instead the 5 simply go green
on main before any answer: re-file Status: done directly (the A/B stands as the record).

**Cleanup for the next session:** rm -rf /tmp/aw306d_main (4.8G; keep the three small logs
/tmp/aw306d_ab_{pristine,mine,main}.log until the DECISIONS entry cites them, then they too
may go); /tmp/aw306d_mine2 holds my saved file copies (safe to delete once confirmed
restored - it was). /tmp/j306d still holds batch3/4_remove.py + composites (the record of
the 16 place_reasons).

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
