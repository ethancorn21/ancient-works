Status: open
Depends on: 302a
# 302b: The one-shot held-out measurement - 21 hand fits, corner error against the method
Touches: fit/inkfit_heldout.py, data/inkfit/, docs/site_flow.md

## Goal
Measure the ink-fit method against the hand fits as truth, held out (the method never reads the hand
pairs; only the evaluator does), and record the numbers in docs/site_flow.md, good or bad - the
acceptance of the whole task is read off this table. The runner `fit/inkfit_heldout.py` (checkpointing
per site, like autofit.run, so a cut session continues) takes the 21 hand-fit documents (the original
20 of tests/golden/hand_fit_docs.sha256 plus the lead's 21st, maiden-castle-q1232816.c_c20ff6b1f16d173d,
no auto flag on main), runs the frozen method of 302a on each (the method sees only the site, the plate
image and the relief), and for each writes: the corner error in metres (RMS over the 4 full-image
corners mapped to ground, autofit.Site.corner_rms convention) between the method's similarity and the
hand fit's similarity (plan_fit.similarity on the doc's pairs), plus rotation error, scale ratio, the
frozen gate's verdict on the method's own pairs, whether plan_fit.fabrication_pattern is silent on them,
and the search-matched-null margin.

## Acceptance criteria
- [ ] BEFORE the run: a committed section in docs/site_flow.md registering the protocol - the frozen
      configuration, the 21 sorted document ids, the corner-error metric, the null recipe, and the
      statement that the method never sees the hand pairs. The run may only happen after this commit.
- [ ] The one-shot run completed on all 21 documents (network for DEMs/pictures allowed in the working
      phase; results checkpointed under data/inkfit/heldout/).
- [ ] The table in docs/site_flow.md: one row per document with the numbers above, reported verbatim as
      measured (no cherry-picking, no re-tuning of anything on this table except the 302c confidence
      threshold, which box 3 of the parent authorises).
- [ ] The fabrication check passes every automatic fit the method produced (every row: fabrication_pattern
      silent). If any row fired, that is recorded here as a method defect, not fixed by editing the table.
- [ ] A DECISIONS.md entry: the table summary, which sites fit and which did not, and what that means
      for the 302c threshold.
