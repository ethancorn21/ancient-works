Status: open
Depends on: 302c
# 302d: Stonehenge through the line - what the ink fit actually places on the stones
Touches: docs/site_flow.md, docs/site_flow/, data/review/, data/db/platefits/, web/data/sites.json, web/data/review.json, web/data/sites/stonehenge/

## Goal
Run `tools/site_done.py stonehenge` in this checkout with the new fit step (parent box 5): whatever the
method places goes on the map through the normal sync, and whatever it does not place goes to the
review queue with its reason. Then check what the page shows, in a browser, against the real stones.

## Acceptance criteria
- [ ] The line ran end to end on stonehenge (its 13 candidates are the batch's leftovers: 7 deleted
      fabricated-pattern documents re-fitted from scratch by the new method, the 6 review-item
      candidates included); per-picture report printed; exit code 0.
- [ ] Browser screenshot in docs/site_flow/ (tools/shot.mjs against a local serve.py, the 301 pattern):
      the site open on the aerial/relief with whatever drawing(s) the method placed, checked against the
      real sarsens' positions and extent as they appear in the picture.
- [ ] docs/site_flow.md records the result plainly, the way the Stonehenge and Argentoratum sections do:
      what was placed (with its gate score and null margin), what went to review and why, the screenshot,
      and an explicit sentence if the method placed nothing.
- [ ] No hand-fit document and no file of another site changed by this run (the line's scoping rules
      held; the 20+1 hand fits and their golden hashes untouched).
