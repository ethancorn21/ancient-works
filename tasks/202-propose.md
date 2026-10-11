Status: open
# 202: Proposed point pairs — a placement a person finishes in a minute
Depends on: none
Touches: fit/propose.py, tests/test_propose.py

## Goal
Given a site and an old picture, produce the proposed point pairs that a review item (201) shows the human
and that the fit (the existing `plan_fit` similarity solver) turns into a placement: a good seed, not an
answer. Fitting by matching point pairs works (25 hand fits); fully automatic fitting failed its
pre-registered test (docs/autofit.md, 0/5) and is not re-run here — a wrong proposal just costs the human a
few extra drag-steps, a wrong auto-fit would sit on the map.

## Acceptance criteria
- [ ] For a book plate with a scale bar and north arrow (the stage-B fields of data/books/index.jsonl:
      `scale_bar`, `scale_text`, `north_angle_deg`, `map_box`): the placement anchors the plate at the site
      centre with the recorded scale and rotation; 3-5 proposed pairs on drawn features of the plate
      (plan corners, straight lines), in page pixels.
- [ ] For a picture with no scale information (bird's-eye views, engravings): a coarse anchor (site centre,
      picture centre, scale from the picture size where possible) with 3-5 pairs flagged coarse — the human
      drag is expected to do the work (fixed landmarks carry these fits: roads, churches, river crossings,
      field edges).
- [ ] Pairs are page px → lon/lat exactly as a platefit doc stores them; the ground they refer to is the
      site's ground image (relief, or aerial for a site with no LiDAR — the fitkit `FITKIT_GROUND`
      convention). Pairs are proposed, never snapped.
- [ ] Test (no network): a fixed sample of (site, picture) pairs using in-repo ground (the six tracked
      hand-fit sites) → golden file of the proposed placements; sanity check in the golden file: a re-fit
      from the proposals of a hand-fit site lands within the hand fit's own residual range.

## Notes
- Import the shared helpers read-only: `pipeline/aw.py` (Mercator), `pipeline/plan_fit.py` (the solver, to
  evaluate your own proposals in the test).
- The proposal is deliberately crude where the evidence is crude: a scale-bar anchor beats a texture
  search, which is the bet that already failed.
