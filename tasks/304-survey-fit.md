Status: open
# 304: Fit a drawing against the old survey map, not the ground - the third try at an automatic fit
Depends on: 302b
Touches: fit/surveyfit.py, fit/surveyfit_heldout.py, data/surveyfit/, tests/test_surveyfit.py, docs/site_flow.md, requirements.in, requirements.txt

## Goal
Two automatic fits have failed: the vision model invents its points (301), and drawing ink against LiDAR relief lands
231-2204 m off on the 21 hand fits (302b, data/inkfit/heldout/results.json). The owner (2026-10-11) chose to try
once more while he fits by hand (305). The idea: many sites already have an old survey map placed on the ground
(the OS six-inch 1st edition, Cassini, the Etat-major: kind "map" in the site's depictions.json, already
georeferenced). A survey map and an antiquarian plan are both ink drawings of the same banks and ditches, often from
the same decades, so matching drawing to drawing should be far easier than drawing to relief. Fit the plan to the
survey sheet, then carry the sheet's georeference over.

## Acceptance criteria
- [ ] fit/surveyfit.py: matching points found between the plan and the site's survey sheet from the images
      themselves (features, line structure, any method you choose, GPU optional if a free card is given to you;
      not a model's list of coordinates), a similarity fit through the sheet's georeference, and a confidence score.
- [ ] The 302b protocol, unchanged in spirit: pre-registered in docs/site_flow.md before the one run, the 21 hand
      fits as truth, held out, a search-matched null, one table (corner error m, rotation, scale, confidence) -
      reported as it comes out. Hand fits whose site has no survey sheet are listed as "no sheet", not dropped.
- [ ] The verdict, written plainly next to the table: the method passes only if a confidence threshold exists under
      which every accepted fit is within 60 m of the hand fit and at least 5 of the 21 are accepted. If it passes,
      write 304b (wire it into tools/site_done.py's fit step, confident -> map, unsure -> review with the reason).
      If it fails, say so, and stop: no wiring, no fourth method.

## Notes
- The hand fits and their golden file stay untouched. 302c and 302d are dropped (the ink fit failed its test).
- Do not take any other task; the lead gives the next one.
