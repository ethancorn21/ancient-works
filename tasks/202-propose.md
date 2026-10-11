Status: open
# 202: Proposed point pairs — a placement a person finishes in a minute
Depends on: none
Touches: fit/propose.py, tests/test_propose.py

## Goal
Given a site and an old picture, produce the STARTING POINT for the fit: the anchor (scale bar and
north arrow where recorded, else the site centre) plus 3-5 pairs on drawn features. Since the GOAL
change of 2026-10-10 (point 2), the primary consumer is the model's fitting pass (203a/203b): the
model starts from this anchor and the few pairs, then looks at the fitkit sheet and records at least
four matched-feature pairs of its own. A review item (201) shows the same starting point to the human
when the model could not fit. Explicitly: a placement from a scale bar, a north arrow and the site
centre alone is a starting point, not a fit — it never goes to the gate as a fit and never becomes a
platefit on its own. Fitting by matching point pairs works (25 hand fits); the fully automatic
fitting bet (docs/autofit.md, 0/5) is not re-run.

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
- The model's own pair recording (203a/203b) supersedes this seed wherever the model does better; this
  output is never treated as the fit (GOAL point 2).
