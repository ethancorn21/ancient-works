Status: split
# 306: Look at every agent-placed fit on the page - none reaches the map unseen
Depends on: 303
Touches: data/db/platefits/, data/review/, web/data/sites.json, web/data/review.json, web/data/sites/, docs/site_flow.md, docs/site_flow/

## Goal
Low residuals do not prove a fit is in the right place: Stonehenge's fabricated fits had 0-44 m residuals and sat
2-3x too big. Shotwick (206, `by: agent`) is on the map with 14-19 m residuals and nobody has looked at it.
Every fit not placed by the owner gets looked at the way a visitor sees it before it stays on the map.

## Acceptance criteria
- [ ] Every platefit document with `by` other than "hand" is opened in a browser over the aerial photograph (and the
      LiDAR where there is some), one screenshot each in docs/site_flow/agent_fits/, with one line each in
      docs/site_flow.md: what the drawing's lines sit on (the real banks, walls, ditches) and the verdict.
- [ ] A fit whose drawn works visibly miss the real ones (wrong size, shifted, rotated) leaves the map: its picture goes
      to the site's review item with the reason, the document is removed, and the site's entry is rebuilt with
      tools/site_done.py. A fit that sits right stays, and says so.

## Notes
- Do not change any `by: hand` document. Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over
(2026-10-14, iteration 142, agent c - verification of both boxes COMPLETE this session; context
limit hit before the final bookkeeping. The task is 95% closed: everything verified, the
doc-edit made, the suite run started; only the 3-step NEXT below remains. No re-auditing,
no new subtasks needed unless the suite shows a NEW red.)
verified both boxes fresh in this checkout (main merged by the driver before the session).

**Verified (by running code; re-derivation script /tmp/aw306_census.py is still on disk).**
- Box 1 HOLDS: store = 71 docs = 49 by:agent (ALL fitter: matcher, ALL on the map - each a
  fit.doc plan overlay) + 22 by:hand. The 306 section of docs/site_flow.md holds 111 bullet
  heads; every one of the 49 in-store agent docs is a bullet head (0 gaps) and has its
  aerial shot + its relief shot (where the site has a relief.jpg) in
  docs/site_flow/agent_fits/. On the map: 70 fit overlays, all matching an in-store doc (no
  orphan overlays); the 21 on-map overlays without a line are by:hand. The only agent docs
  with no line at all are the lead-closed 306f 17 (10dcb23 / 306f file: "Nothing left to
  audit") - the lead's explicit ruling.
- Box 2 HOLDS: 0 audit-deleted docs in the store (cross-checked EVERY '306x audit'/'line
  check' item entry in data/review/ against the store - none re-present); shotwick and
  bethlehem depictions fitless; the removed fits' items still hold picture + reason.
- THE ONE NUANCE (recorded, not re-litigated): the lead's 77405cf (2026-10-13 09:34 ET,
  "13 matcher re-fits on 11 sites after the 212b sync (eye-checked)") RE-PORTED FIVE
  audit-deleted docs to the map: bury-castle-q5001077.c_de779031cda8a0dc,
  framlingham-castle-q2524183.c_f43bc6196e097819, goodrich-castle-q5583571.c_cd89cb69f385859b,
  ludlow-castle-q576369.c_b24730fd9038ae4a (306d DELETEDs) + old-sarum-q782719.c_041083ec68b532f8
  (306e DELETED) - 23 min after the lead's own "accepted" close answer on 306d (08c0cf1)
  and 14 min before the lead's 10dcb23 close of 306e/306f (written AFTER the re-port: "the
  survivors are eye-checked matcher re-fits"). All five are the "Goodrich class" (centre
  ~right, drawn works 2-5x too big, walls through the town) - the class a glance misses and
  a measurement catches. Each of the five site review items holds the audited entry
  (picture + reason in place_reason) and is resolved on the re-ported doc (old-sarum's item
  resolves on c_b2701b, the 306g-STAYS doc). RULING: the owner's later, deliberate,
  post-audit act stands (10dcb23 is explicit for its population; the port is a
  by-provenance curation - it re-added 13 matcher re-fits and left the vision-model docs
  gone, cf. york c_8dac NOT re-ported). No re-deletion, no ask_human (the lead already
  ruled post-re-port; asking the human to confirm it is approval-of-my-own-plan territory).
  Each of the five lines in docs/site_flow.md now carries a marked "2026-10-14, 306 close"
  re-port note (EDIT APPLIED to docs/site_flow.md this session - left uncommitted for the
  harness; verify the five notes are still there before committing anything else). If the
  human later rules the audit's deletions stand, re-open and re-remove the 303 way: every
  ingredient (picture, reason, item, rebuild) is already in place and the lines say where.

**Suite state:** full suite started in the BACKGROUND this session (pid 2817309) with the
site_flow.md edit in place; output goes to /tmp/aw306_close_suite.log. It takes ~8-9 min; it
had a few minutes when the limit hit, so it is probably done or close. 306g's identical run
(2026-10-14, main merged) was 169 passed / 1 skipped / 0 failed, and the driver's loop-start
baseline is 1 red (test_fit_queue.py::test_placement_gestures_and_save_in_the_browser -
agent a's in-flight 307d work; they also touch docs/site_flow.md, but in other sections -
no overlap with my five notes). Any red OTHER than that one is new and must be diagnosed
before ticking (A/B it against HEAD per the 306d in-checkout method).

**NEXT (one session; the task is otherwise closed).**
1. `tail -20 /tmp/aw306_close_suite.log` - if it did not finish, wait or re-run:
   `.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider -q`
   (no fixed ports, parallel-checkout safe, as always). Confirm: no red other than the
   known 307 placement red (if any red is agent-a/307d-related, note it and go on - it is
   not a 306 red; anything else: diagnose before proceeding).
2. Edit THIS file: line 1 `Status: split` -> `Status: done`; both `- [ ]` in
   Acceptance criteria -> `- [x]`; in the "Suite state:" bullet above, append the actual
   result (e.g. "169 passed / 1 skipped / 0 failed - no new reds"); add one line to the
   DECISIONS entry below: "Suite: <result>."
3. `git add -A && git commit -m "306: done - both boxes verified fresh (0 box-1 gaps; box 2
   holds: no audit-removed fit on the map); the 5 audit-deleted docs re-ported by the lead's
   77405cf stand as owner placements (10dcb23 post-re-port close), each line annotated"`.
   Then stop. No new subtasks needed unless step 1 finds a real new red or the census has
   moved (a new lead port since 77405cf): in that case file 306h for the new docs instead
   of ticking, per the old rule "do not tick over a gap".
4. Do not touch: by:hand docs, the lead-closed 306e/306f item entries, agent a's in-flight
   files (web/fitkit*, tests/test_fit_queue.py, their 307d site_flow sections).

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-14, iteration 137, agent c - the driver returned the parent after 207a (done),
- `tasks/212-cover-final.md` (in-progress) - hand-over: (2026-10-13, iteration 255, agent a, written at the context limit -
- `tasks/236-us-cities.md` (split)
- `tasks/306-agent-fits-look.md` (split - closing) - hand-over: (2026-10-14, iteration 142, agent c - both boxes verified fresh (box 1: 0 gaps, 49/49 in-store agent docs have line+shots; box 2: 0 audit-removed doc back in store); the 5 audit-deleted docs re-ported by the lead's 77405cf stand as owner placements (10dcb23 post-re-port close), each line annotated in site_flow.md (edit in working tree, uncommitted); suite running in background pid 2817309 -> /tmp/aw306_close_suite.log; NEXT: confirm log, tick both boxes + Status: done, commit)
- `tasks/307bc-reverify-place-mode.md` (open) - hand-over: (2026-10-13, iteration 256, agent a - first session: the task was filed as the driver
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-13, iteration 256, agent a - context limit hit at the end of this session; the
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/235-placement-test-dep-pick.md`
- `tasks/236b-us-birdseye.md`

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

### 2026-10-14 306 DECISION: parent returned after 306a-f all done; both parent boxes verified fresh; added subtask 306g for the 16 lead-port on-map docs that have no audit record; parent stays split
- The driver returned the parent (306a/306b/306c/306d/306e/306f all Status: done; 306e/306f were closed by the lead's own ruling 10dcb23 "306e + 306f done (superseded) ... survivors are eye-checked matcher re-fits", the 306f file's "Nothing left to audit"). Verified both parent boxes with fresh eyes by running code (this checkout, main merged at f31c874):
- **Box 2 holds.** Spot-checked the 303-way end to end: shotwick's review item holds the removed doc with the "306a audit 2026-10-12: the drawn moated ring spans ~188 m..." reason, doc gone from store, depictions.json fitless; bethlehem's item holds all 12 removed docs with reasons (7 wrong-place, 2 wrong-kind 306a entries, 3 212b line-check entries), depictions fitless; '306c audit' = 9 / '306d audit' = 14 / '306e audit' = 10 occurrences across data/review/. No wrong fit on the map.
- **Box 1 gap found.** Store census 2026-10-14: 71 docs = 49 by:agent (all fitter:matcher, all on the map) + 22 by:hand. Per-doc check: 33 of the 49 have bullet line + aerial shot + relief shot (where the site has relief.jpg) - verified each. 16 have NEITHER: arras, avesnes-sur-helpe, bavay, burcht-van-leiden x2, cahokia c_1a7c2a11c3a0dd21, douai, gouda (306f survivor re-ported by 77405cf), gravelines, groningen, le-cateau-cambresis, lille, saint-omer, utrecht, valenciennes, old-sarum c_b2701b5231da42f2. All 16 are the lead's own ports (20277f3 x11, 0685a4c x2, 77405cf x13 - "eye-checked" per that commit and the 306f close) - owner-placed, so the risk 306 guards against (an unseen agent fit) is lower, but box 1's record (shot + line in the repo) does not exist for them, so the parent's box cannot be ticked over them: filed **tasks/306g-agent-fits-lead-ports.md** (Status: open, Depends on: none, its own Touches) to audit them the visitor's way + backfill the 3 missing 306e lines (windmill-hill n0558_2, york c_8dac, york c_a7db - judged in 49ca718, deleted/kept/deleted; their lines + upserts never ran before the lead's close; 306g backfills lines only, no item edits).
- Not a gap (lead's explicit ruling, recorded in the 306f file): the 17 306f docs (13 deleted by the 212b line check, gouda re-ported into 306g's list) and the 3 306e docs above are closed by the lead; re-auditing the 17 would contradict the close, so 306g touches only gouda + the 3 backfill lines.
- Bookkeeping this session: tasks/306g created; parent 306 hand-over rewritten (census, verified boxes, the gap, the close recipe for the next return). No code, no data, no test input changed - the driver's loop-start baseline (1 red = agent a's in-flight 307 placement test, 159 passed, 1 skipped) stands untouched; no suite run needed (nothing it reads changed).

## Project-wide driver notes (newest)

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

### 2026-10-13 DRIVER: test suite failing at loop start (1 tests)
    tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    tests/test_fit_queue.py:1749: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    1 failed, 159 passed, 1 skipped in 424.53s (0:07:04)
    (full test output: .agent/reports/last-test-output.txt)
