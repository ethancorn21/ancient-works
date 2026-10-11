Status: open
# 300: Stonehenge, finished on the map - the first site through the line
Depends on: none
Touches: tools/site_done.py, tests/test_site_done.py, docs/site_flow.md, pipeline/plan_fit.py, pipeline/build_site.py, web/data/sites.json, web/data/sites/stonehenge-q39671/, data/review/

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
- [ ] `tools/site_done.py <site id>` does the whole line for one site with the code that already exists
      (fit/batch_us.py `run_sites` for pictures not fitted yet, pipeline/plan_fit.py for each fit document,
      pipeline/build_site.py for the site entry and its marks), and prints what it did per picture: synced
      to the map, sent to the review queue, or skipped with the reason. It touches only that site's files.
- [ ] Stonehenge's automatic fit is an overlay on its site: web/data/sites/stonehenge-q39671/ and its entry in
      web/data/sites.json carry it (its drawing counts in the site's score and overlays, as the hand fits do).
      Every other picture of Stonehenge is a fit or an open review item.
- [ ] Checked in a browser, the way a visitor sees it: the page opens Stonehenge, the drawing shows over the
      ground in the right place (a screenshot under docs/site_flow/ with one line on what it shows), and the
      site's square on the map is coloured by its new score.
- [ ] tests/test_site_done.py runs the command on a copy of one site's files (no network) and checks the
      overlay and the entry; the full suite passes.
- [ ] docs/site_flow.md: the line, step by step, as the next site's session will run it, with what broke on
      Stonehenge and how it was fixed (so the next site does not meet it again).

## Notes
- The 20 hand fits and their golden file stay untouched.
- If a step of the existing code cannot do one site alone, fix that step here: this is the work of the first
  piece through a new line.
