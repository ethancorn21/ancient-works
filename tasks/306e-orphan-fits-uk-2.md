Status: open
# 306e: Look at the orphan agent fits, UK part 2 (o-y) - 17 docs, 13 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306e.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 17
UK platefit documents with `by: agent` (sites o-y) that are ORPHANS - in the store, but with no
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

## Docs (17, 13 sites)
- offa-s-dyke-q1127343.c_1cca85e7b4b5a89e - OS 1902 Nantcribba 02
- okehampton-castle-q1419982.c_0edd7f87db67ff20 - Plan of Okehampton Castle
- old-sarum-q782719.c_041083ec68b532f8 - Ancient Plan of Old Sarum
- old-sarum-q782719.c_ff62c9585a92b375 - Plan & elevations of Old Sarum (DPLA)
- oxford-castle-q2600886.c_ba6b308580428184 - Oxford Castle, plan from Mackenzie, The Castles of England (1897)
- pilsbury-castle-q7194511.c_7ff765c177ca7bae - Pilsbury Castle plan
- pontefract-castle-q1949590.c_3213330a52fe6018 - The history of the ancient borough of Pontefract (14739695456)
- pontefract-castle-q1949590.c_d135fb32326df430 - The history of the ancient borough of Pontefract (14762763065)
- portus-adurni-q762664.c_42bedb90fffce1d4 - Portchester Castle, derived from the Penny Cyclopaedia (1836) v6 p 354
- portus-adurni-q762664.c_4912bb54aa79f3ea - Burg von Portchester, Penny Cyclopaedia 1836 p 354
- raby-castle-q4583646.c_fe1d6c7f0ba858cb - Raby Castle, plan from Mackenzie, The Castles of England (1897)
- richborough-roman-fort-q1309736.c_edad7da41d234534 - Richborough Castle, derived from the Penny Cyclopaedia (1836) v6 p 353
- stanton-drew-stone-circles-q1516300.c_59a5c636a9e00703 - Penny Magazine 1836: plan of the druidical temple at Stanton Drew
- taunton-castle-q7688781.c_05cb4a02bd58e82e - Taunton Castle, plan from Mackenzie, The Castles of England (1897)
- windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 - WINDMILL SITES, LEWES DOWN (Allcroft 1908)
- york-castle-q80637.c_8dac5aacd73916b8 - York Castle in 1820
- york-castle-q80637.c_a7db545536f13e24 - Plan of Center, Broome County 1855 (Gifford Wenig)

## Hand-over
(2026-10-13, iteration 178, agent c - **ALL 34 SHOTS DONE and committed (129590d)**; 306d claimed done per the
lead's message; judgment batch 1 started (offa + okehampton seen; okehampton undecided at cutoff).

**What the lead's message triggered (all done + committed).** (1) Merged main into agent/c
(88c5545): two conflicts, both resolved the known way - `web/data/review.json` kept main's newer
'at' (07:07 > my 05:48); `docs/site_flow.md` kept my unmerged 306c+306d blocks then main's 308
arrowheads section after them (both sides were additions at the same anchor). (2) Full suite on the
merged tree: **149 passed, 1 skipped, 1 red** - the red is
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, agent a's in-flight 307
seed flow (probe: 'RESULT FAIL: seed: the gestures own the mouse'; 404 /tiles/relief - the live
relief is Mac-only `aw`); the 161/176/177 A/Bs already proved it red on pure main. (3) 306d set
`Status: done` (74f80e3) on the lead's instruction (005 settled by the fix: the 5 reds are fixed on
main, 77bdf5d, tasks 231-234). /tmp/aw306d_main + /tmp/aw306d_mine2 deleted.

**Shots (box 1 evidence, all in docs/site_flow/agent_fits/, committed 129590d).** 17 docs x 2
(aerial + relief; all 13 sites have relief.jpg) = 34, via tools/audit_306e.mjs (clone of the 306d
recipe, in Touches) against serve.py --port 0. Every [eval] line: ok, img true, layer true, n =
doc pair count, placed:false (FQ emptied - 114 entries loaded, 11 of my 13 sites have queue entries
but none contaminated). Suite baseline for my task: the driver's newest loop-start note era had the
5 now-fixed reds; today's merged-tree red set = the 307 one above (pre-existing, agent a's).

**Metadata (from the doc JSONs; useful next session).** All by:agent. Scores: offa 42.6 (4 pairs),
okehampton 1.0 (4), old-sarum c_0410 19.1 (6) + c_ff62 0.0 (6), oxford 0.0 (4), pilsbury 15.8 (4),
pontefract c_3213 9.5 (8) + c_d135 24.5 (8), portus-adurni both 0.0 (6+6), raby 0.0 (4),
richborough 0.0 (6), stanton 0.0 (6), taunton 0.0 (4), windmill-hill 0.0 (6, **model None** - the
page's default plan model fits it: the relief shot shows resid 0, 1.0 m/px, 0 deg, rowMapBox
[0.56,0.38,0.85,0.58] from plans.json), york c_8dac 31.7 (4) + c_a7db 13.6 (4). York c_a7db's title
= 'Plan-of-Center-Broome-County-1855-Gifford-Wenig' - Center is a TOWN in Broome County, NEW YORK
= the 306d devil-s-dyke/bethlehem toponymic-collision class; its first audit job is to say what the
picture shows (an 1855 US town plan) - almost certainly DELETED as wrong place.

**Review items for the 13 sites (for the 303-way deletions, box 3).** Existing items (candidates in
brackets): old-sarum [c_b2701b5231da42f2], pontefract [c_ba5dfa2d2dbc645e + 6 more], richborough
[c_1dcd5a7171573663], windmill-hill [earthworkenglan01allcgoog_n0557_1, _n0558_1 - same Allcroft
book, my doc is page n0558_2], york-castle [c_81ecab4a9284f156 + 4 more]. NO item (create one, the
306d way): offa-s-dyke, okehampton, oxford-castle, pilsbury, portus-adurni, raby-castle,
stanton-drew, taunton. Upsert via fit/review.py upsert_item, delete doc, export scoped to the site
(NEVER another site's item file); 'at' timestamp in web/data/review.json is the known agent-a
merge-conflict point - keep the newer.

**Judgment state.**
- **offa-s-dyke-q1127343.c_1cca85e7b4b5a89e** (OS 1902 1:2500 Montgomeryshire sheet xxx8
'Nantcribba 02'; 4 pts, 1.44 m/px, +2.1 deg, resid 42-73 m): SEEN (aerial + relief). The sheet (a
hatched Nantcribba wood, a 'Lodge' building, a hatched path, dashed boundary, spot heights 847/850)
sits over the Knighton-area aerial: the drawn wood covers the real dark-green wood at the panel's
bottom-centre, but the sheet's N-E half covers the TOWN (buildings where the sheet has open field),
and anchor 4 sits on bare ground S of the wood. Site point (-3.049, 52.344, kind earthwork) is the
Offa's-Dyke point at the sheet's S-W edge area. LEANING: the sheet is the right local area (Nantcribba
is the wood/stream W of the site point along the Dyke) but placed ~1-2 km E over the town - needs
one web check (where Nantcribba 1:2500 sheet xxx8 sits vs the site point; the real wood vs the drawn
one on the relief) to call DELETED (wrong place) vs KEEPS. Decisive measurement: inverse-map the
site point onto the plate (where on the sheet is the site point? on the wood or on the open field?)
and/or where the drawn 'Nant-criba' label lands vs the real stream.
- **okehampton-castle-q1419982.c_0edd7f87db67ff20** (Commons 1915 'Plan of Okehampton Castle',
'Underlying map Edward H. Young (d. 1932)'; 618x674 px; 4 pts a 100-px grid (150-420,100-500);
page fit 1.20 m/px, -0.3 deg, resid <=1.1 m, score 1.0): SEEN (aerial + relief). The plate is a long
NE-SW CHAIN of ~10 multi-room buildings (A-G) with dense radial tree hatching - NOT a
motte-and-bailey; it is placed centred on the site point (-4.0083, 50.7306, kind motte) and its
buildings line up with the real town-centre building cluster (1842 OS red overlay + modern aerial;
the dashed line by A on a real road/stream, trees on the real park). WIKIPEDIA (fetched, cached at
/home/agent/.cache/pi-web/1387d53e134165ed.txt): the real castle is a Norman (1068-1086) keep on a
long thin ROCKY OUTCROP (mote 29.5x15.5 m top, 32 m high), bailey N of the motte, stream N, the town
~1 km away, the 690-ha deer park S cleared to farmland by 1915; Simmons cleared/repaired 1911-13.
So the drawn 600 m building chain is ~10x the real ruin - it is a map of the TOWN (Edward Young was
Okehampton's local mapmaker), correctly georeferenced (near-identity over the real buildings),
mislabelled 'Castle'. UNDECIDED at cutoff - next session: (a) re-read the 2 shots and pin the plate
centre vs the town cluster vs the red 1842 'Okehampton Castle' label; (b) one web check of the
real castle's position relative to the town (Higham 1984 'Okehampton Castle'; the motte grid ref)
to see whether the site point (kind=motte) is on the castle or on the town; (c) verdict: if the
drawn works sit on the real town and the site point is the town centre -> the plate is a right
local map but the WRONG KIND of subject for a motte site (the bethlehem 'wrong kind' class) -
likely DELETED; if the site point is genuinely the castle 1 km from the town, the placement is also
the wrong PLACE. Either way the line must say what it is (a 1915 town plan) and where it sits.

**Exact next step (batch 1 of ~8, in task-file order).**
1. Finish offa (one web check on Nantcribba's position; write its line).
2. Finish okehampton as above; write its line.
3. Read old-sarum x2 (c_0410 'Ancient Plan of Old Sarum' Ditchfield 1901 - a famous real plan; site
drawings=2 so the site already has 2 built depictions - check what they are in
web/data/sites/old-sarum-q782719/depictions.json; c_ff62 is the 1806 Camden/Basire DPLA plate),
then oxford (Mackenzie 1897) and pilsbury (J.C. Cox 1905 motte plan) - read 10 more shots, judge,
write 5 lines. Write the 306e block header (306c/306d style: '306e - the 17 UK orphan documents
(o-y): ...') BEFORE the first 306e line, after the 306d block and before the 308 section in
docs/site_flow.md. Tick box 1 when all 34 shots are listed (already true - 34 files committed);
box 2 when all 17 lines are in; box 3 after any deletions; box 4 = suite check (merged-tree red
set = the 307 one only).
4. Batches 2-3 next sessions: pontefract x2 (two pages of the 1807 borough history, 8 pairs each),
portus-adurni x2 (twin Penny Cyclopaedia 1836 plans, one German-titled), raby, richborough; then
stanton-drew (Penny Magazine druidical temple plan), taunton (Mackenzie), windmill-hill (Allcroft
1908 n0558_2 - the site's item already holds n0557_1+n0558_1, merge into that item if deleted),
york x2 (c_8dac 'York Castle in 1820' watercolour; c_a7db the Broome County NY collision).

**Pitfalls that bite here (all in PITFALLS.md, don't re-learn).** The mpp/256 judge-composite bug
(line 314) - judge from the real 1440x900 shots, not hand-rolled composites. In-checkout A/B only
(never a bare worktree - locally-built site dirs are gitignored). Geographic distances: dx=dlon
*111194.9266*cos(lat0), dy=dlat*110900 (not raw Mercator). My hand-rolled pure-Python similarity
fit of a doc's pairs gets the v-axis convention wrong (the page's simFit flips plate v; my naive
least squares came out rotation -45 deg / 0.85 m/px, residuals 200-800 m, GARBAGE - the pane's
[eval] fit line is the truth; use it, or use inversions of single points only for spot checks).
**Suite state:** last full run (merged tree, this session): 149 passed, 1 skipped, 1 red (the 307
one, pre-existing). .venv present. The audit server (nohup'd node) has exited; /tmp/audit_306e.log
has the full [eval] record for all 34 shots. /tmp/aw306cab (306c's worktree) still registered -
not mine to remove.

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
- `tasks/306d-orphan-fits-uk-1.md` (in-progress) - hand-over: (2026-10-13, iteration 177, agent c - **waiting on human request 005** (filed this session,
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,
- `tasks/806-yeared-title-repin.md` (open) - hand-over: (2026-10-13, created by agent c in 306d iteration 177; the full A/B record of the five rejected reds

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

### 2026-10-13 306e (agent c, iteration 178): where I am
- 306e: all 34 orphan shots taken + committed (129590d); batch-1 judging started (offa leaning
  deleted; okehampton = mislabelled 1915 town map, undecided). Full detail in the 306e hand-over.
- Per the lead's message: merged main (88c5545; review.json 'at' + site_flow.md 308-section
  conflicts resolved), suite on merged tree 149/1/1 (lone red = agent a's in-flight 307
  placement seed, A/B-proven on pure main at 161/176/177), 306d claimed done (74f80e3).
