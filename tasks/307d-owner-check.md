Status: open
# 307d: The owner's check - two queue sites end to end, then reverted
Depends on: 307c
Touches: tests/, docs/site_flow.md, docs/site_flow/

## Goal
The last box of 307: "Saving still writes "by": "hand" and runs the one-site line (305),
and the existing hand fits load and save unchanged. Checked in a real browser on two queue
sites the way the owner uses it (place, move, scale, save, see it on the map), then the
test fits reverted. Tests cover the queue place-check and the save path." The place-check
tests are 309's; this task proves the save path end to end in a real browser on two queue
sites and proves the shared store comes back byte-identical.

## Acceptance criteria
- [ ] A new tests/ file runs the owner's flow in a real headless browser (Chrome, the
      305-part-3 pattern) against the real server on a private copy of the tree (the 305
      part-2 precedent: real data, no network, ephemeral port): on two queue sites (pick
      ones with a recorded bar scale and a site-size-only fallback, and different ground
      where possible - LiDAR relief vs aerial photograph) the test does what the owner
      does: open the queue, place the drawing (the on-map start), move it, scale it,
      save; then verifies the saved doc carries "by": "hand" and the one-site line ran
      (the overlay on the map in the site's depictions, the site square coloured, the
      review item resolved, the queue moved on), and after a page reload the fit loads
      back unchanged (same placement, same overlay).
- [ ] The test fits are reverted before the test ends: the private tree is discarded, and
      the shared store in the repo is proven byte-identical to before the test (the golden
      hand-fit hash check tests/golden/hand_fit_docs.sha256 and test_fit_provenance stay
      green; web/data/fit_queue.json and the review exports untouched).
- [ ] docs/site_flow.md: the verification section (what was checked, on which two sites,
      which way, and the screenshots), closing the parent's last box.

## Notes
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-13, iteration 250, agent a - TENTH session. **The test is FULLY GREEN.** All three
acceptance boxes are satisfied and verified; only the tick + Status done + final commit remain
(the working tree is uncommitted - the harness saves it). Full details in the DECISIONS entry
(tenth session).

**What this session changed (all in tests/test_owner_check.py + docs/site_flow.md):**
1. Check 4 no longer ports build_site's formula: it calls the REAL `build_site.overlays / drawings
   / score` (pipeline/, numpy ok in .venv) pointed at the PRIVATE TREE via the root-aware
   `_root(root)` pattern (the same pattern the one-site line uses) - one source of knowledge;
   the old `_score_of_deps` port and its `SERIES_ERR_M` table are DELETED. Every check-4 assert
   now carries a self-describing `diag` (the entry, the recomputation, every depiction, both
   phases' markerClass, the tier) instead of dying with a bare AssertionError.
2. `server_runlog.log` is dumped into the run's outdir right after the runlog slice (the ninth
   session's planned step 2).
3. **`_tier_of` fixed** - the real culprit of runs 2-5's "check 4, no message" failures:
   `next(t for th, t in TIERS if ...)[1]` indexes into the tier STRING (`'t2'[1]` -> `'2'`). Now
   `next((t for th, t in TIERS if (score or 0) >= th), "plain")`, mirroring the page's
   `TIERS.find(...)[1]` (web/index.html:475-476; the test's TIERS mirror matches it exactly).
4. Check 7's filter was the phrase `"one-site line" in ln`, which also catches the line's own
   HEADER `site <sid>: the one-site line (fit -> sync -> entry -> review)` (tools/site_done.py:326,
   present since 300's build - the eighth session's static verification missed it; check 7 had
   never actually run before this session). Now a shape filter `ln.startswith("  one-site line for ")`
   (the server worker's report; also catches the unavailable/failed variants, which the exact-equality
   assert would then fail on, as intended).
5. Test B's write-once compare: `_h(a["itemBytes"])` called `Path()` on ALREADY-READ BYTES ->
   TypeError (the 6th session's itemBytes fix stored bytes; the compare wrapped them in `_h` again).
   Now `_h(file) == a["itemBytes"]`, with a guard that fails loudly if test A didn't run first.

**Test state (last runs, this session):**
- `.venv/bin/python -m pytest tests/test_owner_check.py -q` -> **2 passed in 74.06s** (both sites:
  probe + all eight python-side checks + the revert proof + the ten screenshots).
- Full suite (background, 0:06:44): **1 failed, 159 passed, 1 skipped** - the ONLY failure is the
  pre-existing 235 red `tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser`
  (the seed check "the gestures own the mouse (map pan/zoom off), the earlier overlay hidden" -
  documented in PITFALLS, present in the driver's loop-start baseline; my two new tests are the
  157->159 delta). `tests/test_fit_provenance.py` 7 passed; `-k hand_fit` (the golden
  tests/golden/hand_fit_docs.sha256 checks) 2 passed. So box 2's "golden hash check and
  test_fit_provenance stay green" is satisfied.

**Docs (box 3, done):** docs/site_flow.md gained the 307d section at the file's end (after the
308 section): what was checked and how, the two derived picks + picker rules, the four effects with
measured values (both sites 1.1->1.45 t1->t2; 1.45 = 1.18 from the 1908 drawing at 0.0 m residual -
the saved pairs define the similarity exactly - plus 0.25 x 1.10 from the 1842 six-inch; item
resolved write-once; card moves on to 39/46), the unchanged reload, the revert proof, the ten
screenshots, and the PLAIN statement that both picks sit on LiDAR relief because no aerial-photo-only
(lidar false) site was line-eligible in the 2026-10-13 queue - the "different ground where possible"
hedge is not satisfiable today. All ten shots exist in docs/site_flow/ (307d_A_1-card..5-reload.png,
307d_B_*).

**Exact next step (one session, in order):**
(1) Optional, cheap: add the two PITFALLS entries this session earned - (a) under the existing
    `tools/site_done.py, fit/review.py` section: the one-site line prints the header `site <sid>:
    the one-site line (fit -> sync -> entry -> review)` (site_done.py:326) BEFORE its own work, and
    the server worker prints `  one-site line for <sid>: finished (exit N)` - a runlog filter keyed
    on the phrase "one-site line" catches the header too; filter the finished reports by their
    2-space-indented shape. (b) under "Agent tools and harness": in team mode /tmp/pytest-of-agent
    is SHARED by every agent's pytest sessions and their retention cleanup deletes other sessions'
    tmp trees (this session's ownerA0/ownerB0/awowner0 evidence vanished mid-session under agent c's
    concurrent runs) - do not plan around /tmp retention; dump evidence into the repo or read it in
    the session it was made.
(2) Tick all three acceptance boxes in this task file and set `Status: done` (verified: box 1 = the
    green run above; box 2 = the `_write_surface` byte-identity asserts held around BOTH runs in that
    run + the golden/provenance green in the full suite; box 3 = the docs section above).
(3) `git add -A && git commit -m "307d: the owner's check green end to end (two derived queue sites:
    place/move/scale/save, the line's four effects, unchanged reload, byte-identical revert) + the
    docs section closes the parent's last box"` - the working tree carries tests/test_owner_check.py,
    docs/site_flow.md, the ten 307d screenshots, DECISIONS.md, this task file (+ PITFALLS.md if (1) is
    done). Nothing else: no web/, no fit/, no data files, no other tasks' files.
(4) If the driver re-runs the suite: expect 159 passed / 1 skipped / 1 failed (235's red only).

**Retained facts (in case a re-run misbehaves):** picks A = [38]
  oswestry-castle-q20713795 / earthworkenglan01allcgoog_n0119_1 (bar 0.1646 rot 0, Allcroft 1908
  "Camp, Old Oswestry, Salop"); B = [45] devil-s-dyke-q3307343 / n0662_1 (picture_size 0.7201,
  "SWEALD"; its item file is named after lead n0599_1). Queue 241 at 2026-10-13T14:34:09.559141+00:00.
  Both LiDAR (lidar null, EA credit); before both {drawings 0, score 1.1 (t1), oldest 1842, overlays 1}
  (one 1842 six-inch map); after both {drawings 1, score 1.45, oldest 1842, overlays 2} (t2). The
  9th session's "1.45 unreachable" doubt was an arithmetic slip: (2026-1908)/100 = 1.18, not 0.98.
  No-batch line counts: A 1/1/0, B 3/1/2 (from the tree's plans.json rows). review.json open count
  457 -> 456 (A) -> 455 (B). The probe's .mjs was NOT touched this session (no node --check needed).
  Team mode: agent c runs concurrent pytest sessions in its .c checkout (its 302f baseline writes
  /tmp/aw302f_baseline.log); my tests bind only ephemeral ports and write only into their tmp tree -
  no interference observed.

**Do not touch:** fit/surveyfit.py or task 304 (agent c); web/* (not in my Touches); 235's
  tests/test_fit_queue.py (the pre-existing red stays the only suite red); tests/conftest.py; any
  checkout data file (the test writes only into its private tmp tree; the revert proof checks that).
