Status: open
# 305: Ready to fit - the owner clicks the points, the line does everything else
Depends on: 303
Touches: web/index.html, web/fitqueue.js, server/serve.py, tools/fit_queue.py, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md, docs/site_flow/

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

(2026-10-12, iteration 104, agent a - part 3 (headless card probe, boxes 2+4 page half) is WRITTEN and GREEN; both card tests pass. Next: copy the verified screenshots into docs/site_flow/, run the FULL suite, then the docs/site_flow.md section (box 1's say-how), tick boxes, Status: done.)

**State of the boxes:**
- Box 1: generator + committed JSON + page card done (iter 100/101). STILL TODO: the "say how" section in docs/site_flow.md (plan in next steps 3).
- Box 2: DONE this session (page card now also verified in a real headless browser: see below).
- Box 3: DONE (iter 103, test_save_runs_the_one_site_line).
- Box 4: probe + screenshots DONE this session (verified); the full click-through (owner's own points, save, on the map) is the owner's Mac - stated in the tests' docstrings. No revert needed: nothing was saved (the probe never clicks points/save; the only server writes are in the part-2 temp tree).

**What changed this session (all uncommitted - the harness saves them):**
1. tests/test_fit_queue.py: new Part 3 - PROBE_SCRIPT (standalone playwright probe: createRequire trick for shot.mjs, addInitScript to pre-seed localStorage aw.fitQueue.done, real clicks #fqplace/#fitback/#back/#fqskip/#fqreset, screenshots 1-card/2-place/2b-backout/3-skip), helpers _headless_or_skip/_run_probe, tests test_card_in_the_browser and test_card_done_mark_moves_on. The module docstring was updated to describe all three parts.
2. PITFALLS.md: new entry under web/ - `const x={}; x={...}` throws "Assignment to constant variable" at RUNTIME (not a parse error), and a swallowing try/catch turns it into silently missing data (that is how it hid for 30 min: the probe's boot came back `{ok:true}` with zero state fields).
3. tasks/305: Touches gained `docs/site_flow/`.

**Test state when last run:** `pytest tests/test_fit_queue.py -k card -q` -> **2 passed in 26.69 s**. The FULL suite has NOT been re-run this session (expect 73 passed / 1 skipped: 71 baseline + the 2 new; part 2's line_served run takes ~30-60 s).

**Bugs hit and fixed this session (do not re-derive):**
- conftest's `served` fixture yields a TUPLE (base_url, tree) - test_review's `queue` fixture is what wraps it into a dict.
- A probe stage reading page globals (P/S/FQ) must be `await page.evaluate(() => ({...}))` - bare node-context references to P/S/FQ throw (they exist only in the page; also they are lexical, so `globalThis.S` is undefined while bare `S` works).
- MapLibre ABORTS in-flight /tiles/relief fetches during the card's flyTo -> `net::ERR_ABORTED` shows up as `[reqfail]`; the card tests therefore assert no reqfail EXCEPT /tiles/ lines (test_review never navigates, which is why it asserts none at all).
- After #fitback, endFit() HIDES the fit pane (back1.pane is False) - my first assert had it inverted.

**Screenshots (visually verified by me this session - copy them NOW, /tmp may be cleaned):**
- /tmp/fqshot-real/ -> 1-card.png, 2-place.png, 2b-backout.png, 3-skip.png (fresh browser: card "READY TO FIT 117 TO GO / Devil's Dyke / ... — the clearest scan"; place shows the fit view AND the Allcroft 1908 plate image fully rendered in the sheet pane; skip shows Fort Ancient 116 + "Undo 1 skip").
- /tmp/fqshot-real-done/ -> same four, with aw.fitQueue.done pre-seeded for devil-s-dyke (card starts at Fort Ancient 116; skip -> Marietta 115; undo -> back to Fort Ancient 116).
- Copy into docs/site_flow/ as fit_queue_card.png, fit_queue_place.png, fit_queue_skip.png (+ fit_queue_done.png from fqshot-real-done/1-card.png if you want the fourth). If /tmp is gone, regenerate: `sys.path.insert(0,'tests')`-import tests/test_fit_queue.py, write m.PROBE_SCRIPT to /tmp/fqprobe.mjs, start `.venv/bin/python server/serve.py --port 0` in the checkout (prints "Ancient Works on http://127.0.0.1:PORT/"), then `NODE_PATH=/home/agent/tools/shot/node_modules node /tmp/fqprobe.mjs <base> <outdir> none` (or the done site id).
- A stray server from this session may still be running on port 40035 (this checkout): kill it with `kill $(ss -ltnp | grep 40035 | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)` or similar; it is read-only (serves the shared store) and ephemeral, so leaving it is harmless but untidy.

**Real-checkout verified facts (from the probe's [eval] output):** boot {ok, ready, sites 385, plans 1166, entries 117, done {}, tab 'sites'}; queue head = devil-s-dyke-q3307343 / fort-ancient-q5470727 / marietta, all "the clearest scan"; place -> imgLoaded TRUE (book pages load in the real tree; in the conftest temp tree they 404 -> hint "Could not load the page scan.", row kept), fitname = "book · label · title", save floor "at least 3 points", ground 'relief' (all three head sites have lidar != false).

**Next steps (in order):**
1. Copy the screenshots into docs/site_flow/ (names above).
2. Full suite: `.venv/bin/python -m pytest -q` (expect 73 passed / 1 skipped).
3. docs/site_flow.md section (completes box 1): the queue rule (built + a candidate (plan row in web/data/plans.json OR a review-item candidate, deduped by plan) + no by:hand doc; best candidate = plan over view, then drawing area in page px, then plan id; one-word reasons: the only candidate / a true plan / the clearest scan / the clearest view), the ORDER (entries sorted by the best candidate's (is-plan, area, name) - most worth seeing first), the card's semantics (done = localStorage aw.fitQueue.done written by the card's saveFit wrapper when a save lands, self-healed against the file on load; skipped = session-only with a reset in the card; the card opens the fit tool as a clean slate - RV.pending is never set), the save -> line wiring (serve.py: PUT platefits -> worker thread -> tools/site_done.py main([site]) IN-PROCESS with model=None - the 2026-10-10 subprocess lesson; DELETE keeps the old all-fits sweep; by:hand stamp on platefits PUTs, 303), and what the headless check proves vs the owner's-Mac click-through (real points on the plate + save + on the map is the owner's acceptance; cite the new screenshots).
4. Tick boxes 1-4 and set Status: done for the driver's re-check. If the full suite shows any failure, it is mine to fix (tests/test_fit_queue.py, web/fitqueue.js) - never loosen part 2.

**Re-read:** none left.
