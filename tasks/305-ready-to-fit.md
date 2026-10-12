Status: open
# 305: Ready to fit - the owner clicks the points, the line does everything else
Depends on: 303
Touches: web/index.html, web/fitqueue.js, server/serve.py, tools/fit_queue.py, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
The owner's hand fits are the only fits that land right (automatic ones: 301, 302b). He likes doing them ("clicking
three points on the diagram and then clicking the points on the map ... certified cool"). So the line becomes:
agents prepare a site all the way to the clicks, the owner places the drawing on the page, and the line takes it to
the map. One site at a time: the page shows him the next site to fit, and when he saves, that site is finished.

## Acceptance criteria
- [ ] tools/fit_queue.py writes web/data/fit_queue.json: built sites with at least one candidate plan or bird's-eye
      picture (web/data/plans.json, the review items) and no hand fit yet, one entry per site with its best
      candidate first (a true plan over a view, a clear scan over a faint one; the reason in a word), ordered so that
      the sites most worth seeing come first (say how in docs/site_flow.md). Finder/Amazon data never enters it.
- [ ] The page: a "Ready to fit" entry (from the start view) opens the next site in the queue with its best
      candidate already loaded in the existing "Place an old plan" tool; skip moves to the next site. The existing
      tool's clicking is not changed.
- [ ] When the owner saves a fit, server/serve.py runs the one-site line (tools/site_done.py) for that site, so the
      drawing is on the map, the site's square is coloured and its review item is resolved without any other step;
      the saved document carries "by": "hand" (303). The queue moves on to the next site.
- [ ] Checked in a browser the way the owner uses it: open the queue, place a candidate on one site with real clicks,
      save, see it on the map (screenshots in docs/site_flow/). Revert that test fit afterwards: only the owner's
      fits are hand fits. tests/test_fit_queue.py covers the queue and the save -> line step without network.

## Notes
- The page runs on the owner's Mac (server/serve.py --lan, port 8642); keep it stdlib like the rest of serve.py.
- Do not touch fit/inkfit.py, fit/surveyfit.py or the 302/304 tasks (agent c).

## Hand-over

(2026-10-12, iteration 103, agent a - step 4 DONE: the serve.py worker + part 2 test are run and GREEN; suite 71 passed / 1 skipped. Next: headless card probe + screenshots (box 4) and the docs/site_flow.md section (box 1's "say how").
Commit state at session end: this task file and DECISIONS.md are committed by the final hand-over commit; tests/test_fit_queue.py, web/data/fit_queue.json (regenerated, content identical, stamp moved) and PITFALLS.md were left UNCOMMITTED in the working tree (the driver saves uncommitted work in its own commit, as it did after iteration 102).)

**State of the boxes:**
- Box 1: generator + committed JSON done (iteration 100, re-verified this session: `tools/fit_queue.py --root .`
  regenerates byte-identical content, only the `at` stamp moves; committed in this iteration's commit).
  STILL TODO: the "say how" in docs/site_flow.md (the queue rule + ordering rationale + card semantics +
  save -> line wiring).
- Box 2: page card built (iteration 101: web/fitqueue.js after review.js, index.html L1708) and headless
  smoke-verified (place/skip/undo). Not yet re-confirmed in a fresh browser session with screenshots.
- Box 3: DONE this session: tests/test_fit_queue.py part 2 green (see below).
- Box 4: TODO: the browser probe with screenshots into docs/site_flow/ (the dir already exists:
  argentoratum.png, stonehenge.png from 300/301). NOTE for Touches: it only names docs/site_flow.md -
  ADD `docs/site_flow/` to the Touches line before writing the screenshot files. No revert step is needed:
  the test fits live only in pytest temp trees (the fixture's realpath assert guards the shared store),
  and the headless card probe never saves (placing points with real clicks is impossible headless; the
  owner's Mac is the click-through acceptance - say so in the docstring/doc).

**This session's changes (all committed):**
1. `tests/test_fit_queue.py` part 2 fixed and green:
   - `_pick_site()` generalized (the population moved: every usable site is now fully covered by its item
     candidates - after a batch run the item holds every non-auto row - and Devil's Dyke's last uncovered
     row, n0662_1, now has an agent doc). Hard conditions: book row with a page in THIS checkout's data/raw,
     unresolved item carrying that row with >=3 pairs, and NO platefits docs for the site (the line then
     builds exactly one overlay -> drawings +1, open count -1, item resolves by the saved doc). "Uncovered
     rows" (row naming the site, in neither docs nor item) is a SOFT preference: the pick prefers a site
     with one (the model=None upsert path runs and is asserted); a pick without one skips that block.
     Current pick: **forthill / ancientmonuments00squi_n0068_1** (3 pairs, 0 uncovered, page 2844x4064
     1.6 MB).
   - Fixture: the `sd.unlink()` + re-copy of the picked site's web/data/sites dir is GONE - copytree already
     materializes the checkout's per-site symlinks into the tree (real dirs were the crash: IsADirectoryError).
     The site dirs in web/data/sites are: 382 symlinks into /home/agent/projects/ancient-works + 6 tracked
     real dirs (forthill fudge highbank hopeton marietta newark) + 1 untracked real dir
     (shotwick-castle-q7502621 - built here, no shared-store copy, never symlinked). PITFALLS updated.
   - The drain of the server's stdout is now a dedicated READER THREAD (`for line in proc.stdout` into an
     `out` list, yielded in the fixture dict); the old select()+readline pattern is the bug - see PITFALLS
     (Python section): select on a buffered reader's fd never fires again once readline pre-fetches the
     pipe. The fit-entry poll and the "finished (exit 0)" wait merged into ONE 180 s loop (1 s tick,
     `get(base + "/")` assert every tick); 180 s = 8x the measured runtime.
2. `web/data/fit_queue.json`: re-generated (content identical, stamp moved).
3. PITFALLS.md: new Python entry (select + buffered reader on a coprocess pipe; includes the one-off
   whole-process stall of ~4 min observed under parallel-agent load - a watchdog time.sleep(60) never woke;
   the identical run completes in 23 s elsewhere, so it is an OS-level stall, not a deadlock) and the
   shared-store entry's dir counts corrected.

**Verified facts (do not re-derive):**
- The one-site line in the server's process takes **~23 s end to end on this machine** (PUT at +1 s; the
  first worker print AND "finished (exit 0)" both at +23 s). The ~22 s is the heavy FIRST import of
  batch_us/build_site/plan_fit/review (numpy/scipy/PIL chain) inside the worker; the build itself
  (2844x4064 page, two webps at method=6, depictions, set_drawings, scoped export over ~340 item files)
  is seconds. Full suite with the test: 88 s (71 passed, 1 skipped; baseline at loop start 70+1).
- The worker's stdout sequence for the forthill run (what the test scans): "fit no model given: ..." ->
  "site forthill: the one-site line (fit -> sync -> entry -> review)" -> "fit 4 candidate picture(s):
  1 fitted (doc), 3 in the review item -> no batch run needed" -> plan_fit.build's line
  "forthill ancientmonuments00squi_n0068_1: 3 pairs, similarity, residuals m [...]" -> "sync <title>:
  synced to the map (plan_<plan>.webp, 3 pairs)" -> "entry web/data/sites.json: drawings 1 -> 2" ->
  "review <item file>: 4 candidate(s), resolved by <doc>; page now has 339 open of 341 items" -> 4 summary
  lines -> "done" -> "  one-site line for forthill: finished (exit 0)".
- This venv does NOT import relief_tiles ("relief tiles off (relief_tiles not importable)" on server
  startup; harmless: no test requests /tiles/). numpy/scipy/PIL themselves import fine (the worker uses
  them in 23 s).
- fit_queue.json content is stable under agent-c's merges as long as no site gains/loses a HAND fit or
  its built/candidate status changes; agent docs do not move a site out of the queue. If a future run's
  `tools/fit_queue.py --root .` changes more than the `at` line, read the diff before committing.

**Next steps (in order):**
1. Headless card probe (box 4, the "checked in a browser" half): a shot.mjs-style probe like
   tests/test_review.py's headless tests (CHROME=/opt/google/chrome/chrome,
   NODE_PATH=/home/agent/tools/shot/node_modules - the iteration-101 smoke's setup; check that file for
   the exact _shot/_probe pattern). Boot the page on a conftest-style stripped tree is FINE for the card
   (it never writes; the committed fit_queue.json answers 200). Assert: card present with the site name,
   best candidate's title and one-word reason, "N to go"; DOM-click #fqplace -> fit tool active with the
   entry's site/plan/ground (the page image 404s in the temp tree - openPlan keeps the row and shows the
   hint; assert DOM state, not pixels); back out -> card unchanged; #fqskip -> advances to entry 2 and the
   reset link appears; #fqreset -> back. NEW this time vs iteration 101: also verify the done-mark skip -
   set localStorage `aw.fitQueue.done` = {"<first entry site>": true} before load and assert the card
   starts at entry 2 (the self-heal/skip half of "the queue moves on"); Re-read web/fitqueue.js's saveFit
   wrapper to confirm it writes that exact key on a landed doc (the full click-through save is the
   owner's-Mac acceptance - say so in the docstring). Screenshots (card, place, skip) -> docs/site_flow/
   (add the dir to Touches first).
2. docs/site_flow.md section (completes box 1): the queue rule (built + a candidate (plan row in
   web/data/plans.json OR a review-item candidate, deduped by plan) + no by:hand doc; best candidate =
   plan over view, then drawing area in page px, then plan id; one-word reasons), the ORDER (entries
   sorted by the best candidate's (is-plan, area, name) - most worth seeing first: true plans beat views,
   big clear scans beat faint small ones, ties by name), the card's semantics (done = localStorage
   aw.fitQueue.done, self-healed against the file on load; skipped = session-only with a reset; the card
   opens the fit tool as a clean slate - RV.pending is never set), the save -> line wiring (serve.py:
   PUT platefits -> worker thread -> tools/site_done.py main([site]) IN-PROCESS with model=None - the
   2026-10-10 subprocess lesson; DELETE keeps the old all-fits sweep; by:hand stamp on platefits PUTs
   (303)), and what the headless check shows vs the owner's-Mac click-through.
3. Re-run the full suite; then tick the boxes that are now fully verified (2 and 3 at minimum; 1 after
   the doc, 4 after the probe) and set Status: done for the driver's re-check. If anything in the probe
   fails, fix web/fitqueue.js (mine) - never the page's fit tool.

**Re-read:** none left (the iteration-102 list is fully consumed: tests/test_serve.py was read whole in
iteration 101; the worker is now tested; the pick/fixture/drain were rebuilt this session).
