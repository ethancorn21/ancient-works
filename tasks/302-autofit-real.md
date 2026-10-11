Status: open
# 302: An automatic fit that is not made up - the station that feeds the line
Depends on: 301
Touches: fit/, pipeline/plan_fit.py, tools/site_done.py, tests/, docs/site_flow.md, docs/gate.md

## Goal
The line works, but nothing reaches the end of it: 301 found every one of the batch's 110 automatic fits is the vision
model's fabricated pattern (Stonehenge 0 drawings, Argentoratum 0 drawings). Sending more sites down the line now
only fills the review queue. Under one-piece flow the defect is fixed at the station that makes it: the automatic
fit itself.

The owner's hand fits (20 of them, tests/golden/hand_fit_*; Maiden Castle's DPLA plan was added on the Mac
2026-10-11) are what a right answer looks like: click a few matching spots on the drawing and on the ground, solve
the similarity. An automatic fit must find spots that really match, not invent them.

## Acceptance criteria
- [ ] An automatic fit method whose matching points come from the pictures themselves (the drawing's ink against the
      site's LiDAR relief and/or aerial: edges, ridges, ditch lines - the 2026-10-09 Fudge proof fitted a plate by
      ridge contrast), not from a model's list of coordinates. A vision model may give a starting guess only.
- [ ] Measured against the hand fits as truth, held out (the method never sees the hand pairs): for each of the 20,
      the corner error of the automatic fit against the hand fit, in metres, in a table in docs/site_flow.md. The
      fabrication check passes every automatic fit it produces. Report the numbers as they are, good or bad.
- [ ] The method decides for itself when it is not sure (a score with a threshold set on the held-out table), and an
      unsure fit goes to the review queue with the reason, never to the map.
- [ ] Wired into tools/site_done.py's fit step; a test runs it end to end on one hand-fit site's files (no network).
- [ ] Run on Stonehenge: whatever it puts on the map, checked in a browser against the real stones (screenshot in
      docs/site_flow/); say plainly if it places nothing.

## Notes
- The 20 hand fits and their golden file stay untouched.
- Do not start 207 or any other task: the lead gives the next one when this is done.
