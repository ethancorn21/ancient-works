Status: done
# 300: Stonehenge, finished on the map - the first site through the line
Depends on: none
Touches: tools/site_done.py, tests/test_site_done.py, docs/site_flow.md, docs/site_flow/, pipeline/plan_fit.py, pipeline/build_site.py, fit/review.py, web/data/sites.json, web/data/sites/stonehenge-q39671/, web/data/review.json, data/review/, data/raw/commons/big/

## Goal
The owner, 2026-10-11: "I would rather the flow be completing 1 spot on the map, then move on to the next
spot. Rather than fit all spots on the map, create all UI elements for the map, etc." From now on work goes
one site at a time, all the way to the map, and the lead gives the next site only when this one is done.

Stonehenge is the first. It already has an automatic fit from the batch (203b):
data/db/platefits/stonehenge-q39671.c_098c4cb138676939.json, 8 pairs, gate score 7.4 m. Nothing from the batch
is on the page yet: the batch wrote fit documents, and 212's single sync was going to put them all on the map
at the end. This task takes Stonehenge through every remaining step, and turns those steps into one command
that the next sites reuse.

## Acceptance criteria
- [x] `tools/site_done.py <site id>` does the whole line for one site with the code that already exists
      (fit/batch_us.py `run_sites` for pictures not fitted yet, pipeline/plan_fit.py for each fit document,
      pipeline/build_site.py for the site entry and its marks), and prints what it did per picture: synced
      to the map, sent to the review queue, or skipped with the reason. It touches only that site's files.
- [x] Stonehenge's automatic fit is an overlay on its site: web/data/sites/stonehenge-q39671/ and its entry in
      web/data/sites.json carry it (its drawing counts in the site's score and overlays, as the hand fits do).
      Every other picture of Stonehenge is a fit or an open review item.
- [x] Checked in a browser, the way a visitor sees it: the page opens Stonehenge, the drawing shows over the
      ground in the right place (a screenshot under docs/site_flow/ with one line on what it shows), and the
      site's square on the map is coloured by its new score.
- [x] tests/test_site_done.py runs the command on a copy of one site's files (no network) and checks the
      overlay and the entry; the full suite passes.
- [x] docs/site_flow.md: the line, step by step, as the next site's session will run it, with what broke on
      Stonehenge and how it was fixed (so the next site does not meet it again).

## Notes
- The 20 hand fits and their golden file stay untouched.
- If a step of the existing code cannot do one site alone, fix that step here: this is the work of the first
  piece through a new line.

## Hand-over
(DONE, iteration 66, agent c - all five boxes ticked; nothing left.)

**Final state of the task:**
- The one-site line: `.venv/bin/python tools/site_done.py <site id>` (fit -> sync -> entry -> review, per
  picture reported; `--root` for a data root other than the checkout; `--working`/`--model-json` when the
  site still has unfitted pictures). The line's steps, what broke on Stonehenge and the fixes are in
  docs/site_flow.md - the next site's session runs that document.
- Stonehenge is on the map: web/data/sites/stonehenge-q39671/ carries the 7 automatic-fit overlays (plus its
  2 maps) and its sites.json entry has drawings 7 (coloured square); its 6 unfitted candidates sit in the
  published review queue (web/data/review.json, 339 open of 340); the browser screenshot is
  docs/site_flow/stonehenge.png.
- tests/test_site_done.py (the last box): runs the COPIED tools/site_done.py on a tmp tree with the site
  stripped to pre-sync (no plan webp, drawings 0, depictions = 2 maps), sockets killed in the child
  (python -c guard + runpy; a monkeypatch in the parent never reaches a subprocess - PITFALLS Python),
  and the 7 Commons big pictures seeded as flat-colour JPEGs at the REAL cache dimensions (the doc's
  `size` is the browser image's, and m_per_px depends on the big file's fs - PITFALLS pipeline/; pixels
  never enter the fit). Asserts: exit 0, empty stderr, the exact per-picture report, depictions.json and
  sites.json byte-identical to the repo's synced state, the recomputed review page equal to the published
  one, every other site's item file and all 130 fit docs byte-identical, the checkout untouched, and a
  second run fully idempotent. Pinned preconditions (all 13 candidates covered: 7 docs + 6 item, disjoint)
  fail loudly if Stonehenge's plans.json/queue changes.
- Suite: 60 passed in 76.8 s. The hand fits and their golden file stayed untouched throughout.

**For the next site's session:** read docs/site_flow.md first; the only site-specific input is the site id.
