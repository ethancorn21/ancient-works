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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/212-cover-final.md` (split) - hand-over: ## Lead note (2026-10-12, after 211)
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/306c-orphan-fits-us.md` (in-progress) - hand-over: (2026-10-12, iteration 158, agent c - ninth session. **Work has been COMPLETE and committed since iteration 150 (9 wrong-fit US orphan docs deleted th
- `tasks/306d-orphan-fits-uk-1.md` (in-progress) - hand-over: (2026-10-13, iteration 175, agent c - **task done.** Batch 4's 8 removals (the last UK orphan
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/212a-cover-search.md`

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

### 2026-10-13 306d DECISION: iteration 173 - ludlow re-verified DELETE with corrected measurements (bar 0.147 m/px not 0.117; fit is 2.6x the plate's bar not 3.2x; 28-ft tower independent check agrees); 3 of the 8 batch-4 sites discovered to have pre-existing iteration-50 open review items (append pattern); removals still NOT executed
- No repo file changed (all work /tmp/j306d + this entry); the committed tree is still 53ba1b6's state. Removals + 8 site_flow lines + final suite = next session's single step (exact recipe in the task hand-over).
- LUDLOW re-check (the hand-over's one open question - fresh eyes on the composite + plate, bar re-measured, new tower check): the bar's five ticks sit at plate x 317/423.5/525/730/940 (line y 1380-1383) = 623 px for 300 ft = 0.147 m/px - 172's 0.117 came from a rough tick estimate. Independent check 172 did not have: the plate's text ('28 feet in diameter inside, with walls 4 feet' - the round tower, outer ~11 m) vs the drawn tower circle (54.5 px, centre (531,487.5)): at the bar's scale that is 8.0 m (~ the stated 8.5 m inside), at the stored fit 20.6 m (2x the stated outer) - bar and text agree, so the plate was drawn at ~0.14-0.15 m/px and the stored 0.378 m/px fit is 2.6x the plate's own scale. Drawn outer-wall enclosure (plate corners ~(430,300)/(1135,325)/(1095,1195)/(300,1215)) = ~315x340 m at fit scale, centred E +151/N -60, vs the real cliff-top complex (aerial grassland ~230x165 m, centred ~40 m E of the site point; OS 6-inch hatched core = the 12th-c rounded portion at the site point): the drawn E wall runs ~150 m east over the town blocks (Brewery Yard/Linney Villa) and the S wall ~140 m over the town near the Wye, while the rounded W curtain + hatched buildings sit ON the real hatched core. goodrich class (centre ~right, drawn works bigger than the real complex, walls through the town) -> DELETE, confirming 172's default; 172's '465x382 m' included the hachure margin (the wall itself is ~315x340).
- ITEM DISCOVERY (171/172 hand-over said 'batch-4 sites all expected to have NO item' - wrong for three): devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0599_1.json (2 cands, n0599_1 + n0686_1), gurnard-s-head-q5620199.earthworkenglan01allcgoog_n0076_1.json (1 cand), king-arthur-s-round-table-q283800.c_984782b9e35e8ded.json (1 cand, coarse true) all pre-exist from iteration 50, are OPEN, reference none of the orphan plans, and have no resolving docs -> the 303-way upsert APPENDS the orphan plan (eaton pattern; lead/filename unchanged; items stay open). The other 5 sites get new single-candidate items (duffield pattern). Page file 337 open of 350 before -> 342 open of 355 after.
- Also verified: the pre-173 main merge (6eb4f99, incl. aeeb5aa's plans.json re-export) left all 8 docs untouched (by:agent, view=False -> sim) so all 8 verdicts stand; candidate_evidence resolves for all 8; entry field shapes differ by source (book docs have ia/file but no url/ref/size - batch3_remove.py would KeyError on them; 306c's book entries used url 'books/<ia>/<file>' plus book/ia/file keys).

### 2026-10-13 306d DECISION: iteration 175 - batch 4's 8 removals (executed at 174) confirmed committed as 6da5393; final suite = 6 reds = the 169-verified 7-red baseline minus test_plan_list_refresh_is_pure_growth (fixed on main by aeeb5aa's plans.json re-export); zero new reds -> boxes 2-4 ticked, task done
- Pre-checks: the driver committed 174's 18-file tree as 6da5393 (174's context limit hit before the commit; the file set is exactly the 8 deleted docs, the 5 new review item files, the 3 appended item files, docs/site_flow.md, web/data/review.json, the task file). No non-driver commits since the pre-173 main merge 6eb4f99, so 174's pre-check stands: all 8 batch-4 docs were by:agent with view=False (sim model) at verdict time. Working tree clean; no new reds could come from a clean tree.
- Suite (`.venv/bin/python -m pytest --ignore=tests/test_gate.py -q -p no:cacheprovider`, 231 s): 6 failed, 141 passed, 1 skipped. The 6 = the 169 A/B-verified 7-red baseline minus test_merge::test_plan_list_refresh_is_pure_growth, which now PASSES: that test reads only web/data/plans.json + data/merge/plans_premerge_keys.jsonl + data/commons/files.jsonl (never web/data/review.json or any of my 18 files), and aeeb5aa (233+234, on main via 6eb4f99) re-exported plans.json - the shift the 173/174 notes anticipated. Remaining 6 reds, all agent a's in-flight work: (1) test_fit_queue::test_placement_gestures_and_save_in_the_browser (307/306c request-004 family, fails at the seed check dep:null); (2)+(3) test_merge::test_new_sites_are_complete + test_new_site_golden_samples (211/222-228 open gate); (4)+(5) test_fit_provenance::test_line_refuses_unmarked_non_auto_doc + test_commons_yeared_title_drops_the_repeated_year (FileNotFoundError on bethlehem-q2523914.c_a164ee440558d66c.json - the doc 306a deleted ON MAIN, the tests predate it); (6) test_site_done::test_site_done_line (stonehenge 14 candidates in plans.json vs the expected 13, 212 in-flight). Since none of the reds is outside the baseline, no A/B was needed (the in-checkout A/B idiom stays in PITFALLS if a future red appears).
- Closed the task: box 2 (all 18 site_flow lines in the 306d block), box 3 (14 removals across the 4 batches, all the 303 way, no other site's item touched, no by:hand doc touched), box 4 (no new failures vs the baseline; the 6 reds are pre-existing on main and all documented as agent a's work in entries 161/169/171-174). Verdict record: 4 KEEPS (chevening, cooling, coria, daw-s) and 14 DELETED (bury, cassiobury, duffield, eaton, framlingham, goodrich, desborough, devil-s, gurnard, hardknott, herstmonceux, king-arthur, leicester, ludlow); the 16 place_reasons are preserved verbatim in /tmp/j306d/batch3_remove.py + batch4_remove.py and in the review items themselves.

### 2026-10-13 306d DRIVER: done claim rejected, task reopened
- Tests failing that were not failing before this task (known failures are allowed, new ones are not):
    tests/test_fit_provenance.py::test_commons_yeared_title_drops_the_repeated_year
    tests/test_fit_provenance.py::test_line_refuses_unmarked_non_auto_doc
    tests/test_merge.py::test_new_site_golden_samples
    tests/test_merge.py::test_new_sites_are_complete
    tests/test_site_done.py::test_site_done_line

## Project-wide driver notes (newest)

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

### 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)
- Re-verified the 160 hand-over's numbers with fresh measurements BEFORE deleting (AGENTS.md: check facts by running code). Confirmed: 8 pairs = 4 distinct points on a 100-px grid ladder (three on u=100; the 200-px and 100-px lat steps span 0.0053896/0.0017967 deg = 1.5:1 per pixel, no similarity can hit; the page's simFit (exact port) gives resid 10.9-39 m, 2.634 m/px, +1.06 deg - identical to the committed shot's [eval] line). CORRECTIONS to the 160 hand-over: the real hillfort is ~20 m NW of the site point (not '+22 E / -55 N'), its hachured ring is ~80-90 m across (not ~130 m), so the drawn ring (277-342 m at 2.634 m/px, centred at raw (240-248,115) -> (-3.5187, 51.0370) = E -218..-239, N +531) is ~3.5x too big and 554-582 m N-NW (N23-25W) of the real one - on a small hachured wood hill. The 160 '~2x / 535-576 m' survives as a range (540-576 -> 554-582), the direction and the verdict are unchanged. Extra independent check: the plate's own 'SCALE OF FEET 0-300' bar measures ~1.45 m/px vs the fit's 2.634 (1.8x). Distances must be geographic (dx=dlon*111194.9266*cos(lat0), dy=dlat*110900), NOT raw Mercator units (my first pass computed 916 m for the 576 m distance that way).
- Executed the 303 way exactly as 306c did (fit/review.py API, no hand-edited JSON): upsert_item(root,'bury-castle-q5001077',[entry]) with entry = {plan, title, url, pairs (the doc's 8), coarse:false, evidence (from the data/commons/files.jsonl row: rec evidence/1, kind category, checked 2026-10-10, site_cat/file_cat 'Bury Castle, Somerset'), label '1911', cite, ref, size, place_reason '306d audit 2026-10-12: ... Document deleted.'} appended to the existing item (lead n0136_1 kept first, filename unchanged), then deleted data/db/platefits/bury-castle-q5001077.c_de779031cda8a0dc.json, then export(root,'bury-castle-q5001077') (333 open of 346). Only 3 files changed (D doc, M item, M web/data/review.json) - no other site's item touched; the site was already covered for the union check (its item was already open in the page file before the upsert).
- Wrote the 306d block (header + the bury-castle line) into docs/site_flow.md after the 306c block (header is tense-neutral: 17 more lines to come in batches; box 1 ticked - 36 shots re-listed this session).
- TESTS (full suite, main checkout, --ignore=tests/test_gate.py, -p no:cacheprovider, with my changes): 10 failed, 130 passed, 1 skipped (251 s). The 10: test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (FAILED at the seed check, dep:null) + 9 that are agent a's in-flight work already on main (test_merge new_sites_are_complete/new_site_golden_samples = 211's open 222-228 gate; src_artists/limes/mackenzie/numancia/wiltshire_stukeley stage+check tests = the 224 family). Baseline in my task file (123/1, 2026-10-12) is STALE - main has since merged 211/223/224/307 work and the suite grew to 141 tests.
- A/B attempt 1 (worktree at HEAD in /tmp/aw306d_ab): INVALID - web/data/sites/ is mostly gitignored (58 tracked files vs 389 site dirs in the main checkout; the per-site web data + data/raw are local build artifacts), so a fresh worktree lacks stonehenge etc. and fails 3 tests deterministically (site_done_line FileNotFoundError '/tmp/aw306d_ab/web/data/sites/stonehenge-q39671', fit_provenance line_refuses_unmarked_non_auto_doc, fit_queue save_runs) that pass in the main checkout; its placement_gestures 'vacuous ERROR' there is also unprovable (no local depictions). PITFALLS candidate: never A/B this project in a bare worktree/checkout - do it in the main checkout with the changed files temporarily at HEAD. (The worktree is still registered; remove it: git worktree remove --force /tmp/aw306d_ab && git worktree prune.)
... (1.9 KB more: `grep -n -A 200 -F '## 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)' DECISIONS.md`)

### 2026-10-13 306d (iteration 176, agent c) - where I am
Work COMPLETE and committed since 6da5393 (14 docs deleted the 303 way, 4 kept, 36 shots, 18 site_flow lines; state re-verified this session). The driver REJECTED the 175 done-claim (8200a33) on 5 tests; I A/B-proved all 5 fail on pure main 735ec66 (none of agent/c's work) and identically with 306d's changes reverted - full evidence in DECISIONS (176) and the task hand-over. NEXT (session 177): create tasks/806 (re-point the two bethlehem-pinning fit_provenance tests, 306a/4ca9e2c way) + file blocking ask_human 005 (recommendation: accept 306d, baseline the 5 - same class as 004/306c) + commit; keep Status: in-progress while 005 is open (306c pattern).
