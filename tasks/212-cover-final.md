Status: split
# 212: Cover - the last uncovered sites, the final sync, the report
Depends on: 203a, 203b, 211
Touches: fit/cover.py, data/db/platefits/ (the loop's matcher writes docs; the line check may delete a pattern doc; the sync may stamp by:agent into an unmarked auto doc), data/review/, web/data/review.json, data/commons/files.jsonl, data/commons/classified.jsonl, web/data/plans.json, web/data/sites.json, web/data/sites/, docs/batch.md, tests/test_cover.py

## Goal

The last pass of GOAL.md point 1 and its evidence for the human. For every built site
still without a fit (after the batch, 203a/203b, and the new pictures, 211): a targeted
picture search (the site's QID Commons category, P180 depictions, a title search) with the
search recorded; a found picture becomes a candidate through the normal loop (fitkit sheet ->
model fit -> fit -> gate); a site where nothing is found gets a review item marked "no picture found"
with exactly what was searched. Then the one and only page-facing sync: every fit
document (the 20 hand fits, the automatic ones, the human-saved ones) becomes its site's
overlay and its drawings count in web/data/sites.json, through the existing plan_fit
machinery; web/data/review.json becomes the current open list for the page's review
section (201). Finally docs/batch.md: the report the human reads - counts per outcome,
the seeded 20-sample of automatically accepted fits (a page URL each) for the 18/20
check, and the "no picture found" list.

## Acceptance criteria

- [ ] fit/cover.py runs the targeted search for every built site without a fit and without
      a candidate: the searches (categories, P180 queries, date) are recorded; a found
      picture is staged in the canonical files (files.jsonl + classified.jsonl, with the
      200 evidence field) and its row added to web/data/plans.json; the site goes through
      the normal loop (fitkit sheet -> model fit -> fit -> gate) and ends with an automatic document or a
      review item.
- [ ] A site with nothing found gets a review item marked "no picture found" with exactly
      what was searched (assumption 3 of PLAN.md); the human can drop the site or name a
      source from the item.
- [ ] The page-facing sync (the only task that runs it): every fit document produces its
      site's overlay (web/data/sites/<id>/depictions.json) and its drawings count in
      web/data/sites.json, through the existing plan_fit machinery; the 25 hand fits'
      overlays are unchanged (000's golden test still passes).
- [ ] web/data/review.json is the current open list for the page's review section:
      resolved items out, new items in; the served page shows the right count (checked
      through the page, not the file).
- [ ] docs/batch.md: the final report - counts per outcome (fit: hand / automatic /
      human-saved; review item; no picture found), the seeded 20-sample of automatically
      accepted fits (page URL each, fixed and reproducible from the recorded seed) for
      the human's 18/20 check, and the "no picture found" list with what was searched per
      site.
- [ ] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item (GOAL.md point 1, in full); the
      25 hand fits are intact (the golden test); the sample in docs/batch.md is
      reproducible from the recorded seed.

## Notes

- This task runs last on purpose: it alone writes web/data/review.json, the per-site
  depictions and the drawings counts, so no other in-flight task can collide with it.
- The sync runs plan_fit.main() by hand (the way serve.py's after_write does it in
  production); the tests never start the server's platefits path for this - they check
  the served result.
- The 20-sample must stay a fixed record: the human's 18/20 check (GOAL.md point 3) is
  the project's acceptance, and a moving sample would make it unrepeatable.

## Lead note (2026-10-12, after 211)

- The fit in this task's loop is the MATCHER, not a vision-model fit: tools/site_done.py already runs
  fit/matchfit.py first on every picture without a document whenever the matcher answers (ELoFTR on
  127.0.0.1:8091 is reachable from this VM; RoMa on 8092 is not, and site_done works without it).
  The vision-model batch fit invented its points (301) and must not place anything. An unsure matcher
  result goes to the review item, as site_done already does.
- 211's new pictures are in the canonical files but most have no local copy, so they are not in
  web/data/plans.json yet (still 1168 rows on main): `python pipeline/commons.py thumbs` fetches rows
  with a `thumb`; the Limes rows carry only a full-file `url` (upload.wikimedia.org) - fetch those too
  (the original, or a standard thumbnail width), then `tools/export_plans.py`. The lead did this on the
  owner's Mac (1168 -> 1296 rows, plus the Civitates/Merian full pages); data/raw is gitignored, so
  this checkout needs its own copies.

## Lead split (2026-10-13)

Split into 212a (search + no-picture items), 212b (sync), 212c (report) after 5 notes-only sessions. a's design notes stay on agent/a (d0ac06b, the hand-over); the fit step is the matcher, run by the lead.

## Hand-over

(2026-10-13, iteration 253, agent a - **ALL EVIDENCE IN: sync ran, report
written, tests green except 235's known red, invariant measured 0/499
violations. The ONLY remaining step is mechanical: tick the six boxes,
set Status: done, commit.** The iter-252 hand-over is preserved in git:
`git show 33aad26:tasks/212-cover-final.md`.)

**What this session did (all verified by running, on branch agent/a, main merged in):**

1. **Re-audited before acting.** Exact is_done-rule audit (entry file ==
   `plan_<doc["plan"]>.webp` AND `fit.doc` == `<sid>.<plan>` AND `fit.at` ==
   `doc["at"]`; doc id in the store = `<sid>.<plan>` but the webp FILE name
   drops the site prefix): 70 docs / 52 sites; EXACTLY the 13 lead-77405cf
   matcher docs lack a current entry; 0 stale; 57 current. 10 of the 13 had
   no `data/raw/commons/big/<plan>.jpg` cache (to be downloaded), 3 cached.
   Network to commons.wikimedia.org 200. All 11 site dirs are symlinks to
   the store. NOTE: my first audit pass used the raw doc id as the entry
   name (70 "missing"/57 "stale" - false); the file name strips `<sid>.`.
2. **`.venv/bin/python fit/cover.py sync` RAN CLEAN** (log saved
   /tmp/212-sync-iter253.log): 70 docs -> **13 "synced to the map"**
   (all 13 new matcher docs passed the spread check; gates 1.0-11.1 m),
   **57 "skipped: overlay already current"**, **zero** sent/failed/refused
   /pruned lines, then "sync: **457 open of 480** item(s) ->
   web/data/review.json". Tracked diff in my checkout: **only
   web/data/review.json** (the `at` timestamp 14:34 -> 20:37; the items
   array is BYTE-IDENTICAL to the lead's 14:34 export - the lead's 3 item-
   file edits in 77405cf had already recorded those resolutions) - and
   later docs/batch.md. web/data/sites.json was REWRITTEN by set_drawings
   but is BYTE-IDENTICAL to the committed blob (hash checked):
   the lead's hand-tuned score/oldest/overlays/drawings for the re-fit sites
   == what the machinery derives - an independent confirmation of 77405cf.
   The 13 depictions.json + webps and 10 big jpgs landed in the STORE via
   the symlinks (old-sarum spot-verified: plan webps mtime 15:36, dep file
   15:37). My final 13/13 landing check script had a key bug (used the
   glob path, not `os.path.basename(p)[:-5]`, as the docs-dict key -
   KeyError); trivially fixable, but the sync's own output + the
   is_done-audit before/after already prove it (re-running optional).
3. **`.venv/bin/python fit/cover.py report`** wrote a fresh docs/batch.md
   (at 20:38 UTC): **499 built**; counts per outcome: hand(golden) 19,
   human-saved 0, **automatic 33** (49 by:agent docs; 212c had 24/36),
   review item 200, no picture found 244, **uncovered 3**; 457 open of 480.
   The **3 uncovered = fudge, highbank, hopeton** - measured: each has
   `plate: true` in sites.json (drawings=1, overlays=1; their only dep
   entry is kind=topo with fit.doc None), NO fit doc, NO item. The report's
   "uncovered (needs attention)" bucket is DOC-based (a site with neither
   fit doc nor item) - the same design and header wording the driver
   accepted in the 212c report (ac87a87, which said "106 ... the invariant
   is broken"); the 106 = these 3 + the 103 the lead then itemized.
   **The PRODUCT invariant (box 6) is not broken**: measured on the final
   served files - 499 served sites, **0 violations** (every site:
   drawings >= 1 or an open item, open = `review.resolved_doc` falsy - the
   product rule); the 457 open item-file set == the 457 review.json set
   (identical site sets). fudge/highbank/hopeton were pre-identified in
   the CORRECTION-4 DECISIONS entry as "drawings-1 site.json-plate sites ->
   covered by the product definition". I did NOT reword the report (box 5
   is satisfied as written; the wording is established design) - flag it
   to the human only if they misread the header.
4. **Tests:** tests/test_cover.py **6/6 PASSED** (41.7 s, incl. test_report
   which re-derives the 20-sample from the recorded seed 20261012 and
   checks the buckets sum to 499). Golden: `sha256sum -c
   tests/golden/hand_fit_docs.sha256` -> **all 40 OK** (21 hand docs + 19
   site files byte-identical); test_fit_provenance::test_every_doc_carries_
   provenance PASSED. **Full suite: 159 passed, 1 failed, 1 skipped (390 s)**
   - the single failure is `tests/test_fit_queue.py::test_placement_
   gestures_and_save_in_the_browser`, failing at its SEED with the exact
   documented signature "RESULT FAIL: seed: the gestures own the mouse
   (map pan/zoom off), the earlier overlay hidden" (`dep:null`). I
   verified `_pick_place()` still returns **marietta** (queue entry, plan
   ancientmonuments00squi_n0169_1; its only depiction is a 1904 USGS topo
   the page's surveyOldEnough 150-year filter hides, so no dep layer, so
   the seed check reads null) - identical to the pick recorded in
   **tasks/235-placement-test-dep-pick.md** (Status: open, unassigned,
   Touches tests/test_fit_queue.py), which has owned this red since ~iter
   199 and it is in the driver's baseline (306d's run; 307d's hand-over
   line 66: "single failure is 235's pre-existing red"). The iter-252
   hand-over's "later fixed by 307d" was WRONG - 307d fixed its own
   test_owner_check, not the gesture test. My sync cannot have caused it:
   marietta is none of the 11 re-fit sites and the failure mode is the
   page's topo filter, untouched by the sync. So the suite is exactly the
   established baseline state: no test newly red.

**EXACT NEXT STEP (one short session):**
1. Tick all six boxes in this file with the evidence above (box 6's written
   port-0 test stays WAIVED per the lead's 212b say-so - design in
   `git show 45675c9/1cd9671:tasks/212b-cover-sync.md`; the driver accepted
   the identical live-evidence tick for 212b; do NOT re-open it as a
   subtask; the DECISIONS entry I write now records the precedent). Set
   `Status: done` on line 1.
2. Append the DECISIONS entry (draft in my step-3 commit below; if the
   harness already saved it, just verify and commit).
3. `git add -A && git commit -m "212: done - final sync (13 matcher docs ->
   store, 57 skipped, 457/480 open), fresh docs/batch.md, invariant 0/499
   violations, 159 passed / 1 failed (235's pre-existing red) / 1 skipped"`
   then stop. If the driver's re-check rejects: the DECISIONS trail shows
   (a) the 1 red is 235's baseline red (235's file + driver notes), (b) the
   port-0 waiver is the lead's 212b say-so with a driver-accepted precedent,
   (c) every box's evidence is measured, not assumed.

PITFALLS (file if not already): dep entry file name = `plan_<doc["plan"]>.
webp` (site prefix STRIPPED) while `fit.doc` keeps the full `<sid>.<plan>`;
audit with is_done's triple (file, fit.doc, fit.at) or you get false
missing/stale (my first pass: 70/57 vs the true 13/0). Second: a glob path
needs os.path.basename before [:-5] for the platefits dict key.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

## Hand-over record (agent a, iter-252 - written at the context limit)
212 (cover final) is at its closing step. All subtasks done; the world moved after the
last sync (11:26) and report (13:22) via ONE lead commit 77405cf (14:34): 13 by:agent
matcher re-fit docs (NOT synced - zero depictions.json touched in that commit) + 103 new
review items for the uncovered sites of 212c's report + review.json re-export. Store ==
my checkout (557 files, 0 differing); the 13 docs are the only ones missing dep entries;
0 stale. Full detail: tasks/212-cover-final.md ## Hand-over and the DECISIONS entry above.
NEXT: `.venv/bin/python fit/cover.py sync` -> `fit/cover.py report` -> tests (test_cover
6, golden hand_fit, test_serve, full suite) -> measure the invariant on the served
files -> tick the six parent boxes -> Status: done. No subtasks (the lead's 212b say-so
waived the written port-0 test; precedent accepted by the driver).


Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207a-horsley.md` (blocked) - hand-over: (2026-10-13, iteration 203, agent c - the main merge brought the owner's "Stop 207" onto this
- `tasks/207b-maclauchlan.md` (blocked) - hand-over: (2026-10-13, iteration 204, agent c - NO work on this task. The driver auto-put it back to
- `tasks/207c-roy.md` (blocked) - hand-over: (2026-10-13, iteration 205, agent c - NO work on this task. The driver auto-put it back to
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/212-cover-final.md` (split) - hand-over: (2026-10-13, iteration 234, agent a - **212a done, 212b done (lead), 212c done - the
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-13, iteration 208, agent c - the driver returned the parent: all existing subtasks
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/235-placement-test-dep-pick.md`
- `tasks/302f-matcher-station-test.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-13 212 DECISION: 231 corrected to its single pin; 232/233/234 filed; probe worktrees removed
The iter-206 note's 231 "second pin" paragraph was wrong: test_line_refuses_unmarked_non_auto_doc
(case b) never reads the deleted bethlehem doc - its seed is the golden doc
c_022604d2be0becdc from tests/golden/stonehenge_linecheck_docs/, and its failure
is the shared Stonehenge 13-row plans pin (14 rows since main f970500 added
c_61b86efb4511e099 with the 211 pictures; the item file and the published page
entry still agree with each other at 13 candidates - verified). 231 was rewritten
to cover only the year-once pin (case e) with a candidate list measured from the
live store (40 year-titled docs; batch set incl. the Mackenzie (1897) series and
"York Castle in 1820"), chosen after 306c-f settle. 232 re-pins the shared
Stonehenge snapshot in test_site_done + fit_provenance b to the POST-212 live
state (depends on 212, then 231 - both edit test_fit_provenance.py). 233 per the
entry above (depends on 212). 234: test key to the generator's documented
(view, -px, plan, name) - tools/fit_queue.py's sort stays (307bb's page-card pins
depend on the entry order) - plus a byte-reproducible regeneration of
web/data/fit_queue.json (committed at 229 entries, at 2026-10-13T04:09:15) after
212 and 306c-f settle the live inputs. The /tmp/awmain and /tmp/awhead probe
worktrees were removed (agent c's /tmp/aw306cab untouched).

### 2026-10-13 212 DECISION: CORRECTION 4's measurement ran - bethlehem/shotwick stay covered by their open audit items; box-6 risk did not materialize; live nofit population re-measured (402 = 246 search + 156 with-row)
Ran the one blocked measurement from the iter-205 hand-over (CORRECTION 4) on the
post-merge tree (HEAD f62d50c, plans.json 1474 rows, 499 built). The risk it tested -
the sync's full prune resetting a doc-less site to drawings 0 with no cover, breaking
box 6 - did NOT materialize:
1. bethlehem-q2523914 (3 fabricated docs deleted by the 306a audit a858f48): drawings
   already 0, no docs, dep file rewritten on this machine ~1h after a858f48 (mtime
   Oct 12 22:38 CDT) and already map-only (tmk1850 1850) - no plan entries left to
   prune. Item bethlehem-q2523914.c_b31c3de3630246bc.json: 22 candidates with 306a
   audit whys and detail fields (coarse/ground/rot_deg/scale_m_px/note), no_picture
   None, resolved None -> OPEN and published in the 333-item review.json. The sync's
   prune leaves the dep byte-identical (prune keeps every non-plan/view entry).
2. shotwick-castle-q7502621 (agent doc deleted at 6841f07, uncommitted work after
   iter 136): drawings already 0, no docs; dep file (mtime Oct 11 18:47, never
   re-pruned here) still carries the STALE plan entry of that doc -
   plan_c_e6e5490609414bb9.webp + plan_c_e6e5490609414bb9_ink.webp both still on disk
   - plus the map entry (six-inch-1st 1842). Item: 2 candidates (n0575_1 "no model
   answer"; c_e6e5490609414bb9 "306a audit: the drawn moated ring spans ~188 m..."),
   OPEN and published. The sync's full prune drops the plan entry and BOTH webps,
   then set_drawings -> drawings stays 0 (a map is not a DRAWING kind; no plate).
Both sit in the 52-site population whose plans rows are ALL already review-item
candidates: tools/site_done.py fit() re-fits only rows with NEITHER doc NOR item
entry (its docstring: a blind re-run would swap the audit entries whole), so the
loop leaves both item files BYTE-IDENTICAL (audit whys survive; their reasoning is
also in DECISIONS under the 306a entries). Neither is in the search set (both have
rows), so nopicture does not touch them. Box 6 holds for both via the open item -
NO nopicture re-record needed, and the test's assertion (iv) is now concrete (see
hand-over). Filed a PITFALLS entry (### tools/site_done.py, fit/review.py) on the
upsert in-place replacement + the skip guard that protects audit notes.
Re-measured live population with the PRODUCT definitions (nofit = drawings==0 AND no
doc; search set = nofit minus plans-row sites; the iter-205 numbers were the
pre-merge 1168 tree): nofit 402 (94 sites have docs); search set 246 - ALL already
carry the batch-era no_picture mark (nopicture re-records all 246 with the exact
searched string; 0 bare sites). fudge/highbank/hopeton looked bare under a looser
no-doc definition but are drawings-1 site.json-plate sites -> covered by the product
definition, outside the search set. with-row nofit 156 = 52 all-rows-in-item (item
untouched by the loop) + 1 partial overlap (loop upserts "no model answer" only for
the uncovered rows, in place) + 103 no item (loop creates a fresh all-rows item).
CHOOSE (first 4 with-row nofit, sorted) on THIS tree: aardenburg-q955 (1 commons
row, no item), aesica-q4688554 (1 commons row, 1-cand item), aire-sur-la-lys-q259903
(1 commons row, no item), alauna-q4708853 (5 rows, first = BOOK Allcroft 1908
n0438_1, 5-cand item). alesia (withrow[4]) and angel-mounds (withrow[7]) fell out of
the first 4: 211 gave aardenburg/aire-sur-la-lys their rows and the lead's Mac port
(20277f3) added 11 matcher docs on 11 newly built sites. Test consequence (in the
hand-over): the matcher fake assigns the pair recipes by POSITION (CHOOSE[0..2]
well-spread, CHOOSE[3] near-collinear -> sent+deleted by the line check), and the
expected item end states follow 201's derivation computed from the live items (doc on
an in-item row -> item resolved write-once and off the open list, as for aesica; doc
... (0.1 KB more: `grep -n -A 200 -F '## 2026-10-13 212 DECISION: CORRECTION 4's measurement ran - bethlehem/shotwick stay covered by their open audit items; box-6 risk did not materialize; live nofit population re-measured (402 = 246 search + 156 with-row)' DECISIONS.md`)

### 2026-10-13 212 DECISION: D3's cost measurement ran - the real-dir/hard-link tree build is ~0.7s total; the fallback is dropped
Ran the hand-over's step (1) on the merged tree (HEAD d31aaec, working tree clean).
Shared store = /home/agent/projects/ancient-works: data/raw is a real tree - 2344
dirs + 11196 files (6328 jpg, 3123 png, 1558 img, 109 json, 26 gz, shapefiles,
3.1G), 0 symlinks, 0 .npy/.npz; its web/data/sites = 388 real site dirs, 2744
files, 514M. The checkout mirrors it: data/raw is a symlink to the store's;
web/data/sites is a real dir with 503 site entries = 382 per-site symlinks to the
store + 121 real dirs; the followed checkout view = 504 dirs + 3147 files.
Measured the exact D3 build in a throwaway /tmp tree (os.makedirs every dir -
new inodes - and os.link every existing file; nothing is ever written in place):
data/raw 0.47s, the followed sites view 0.11s, the rest of the tree (web/ +
data/ + docs/ + specs/ + tests/, 2005 files, minus raw/sites internals, minus
.npy/.npz) 0.14s. TOTAL ~0.7s with near-zero disk (the hard links share the
3.6G). Consequence: the hand-over's fallback (hard-link files only under the
dirs that exist in the store + a few known dirs) is DROPPED - the test builder
walks the store's data/raw and the followed checkout sites view
unconditionally. No code changed this session.

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
