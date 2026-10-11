Status: split
# 203: The batch - every built site gets a fit or a ready review item
Depends on: 001, 200, 201, 202
Touches: tests/test_batch.py

## Goal
The heart of GOAL.md points 1 and 2. For every built site in web/data/sites.json: take its candidate
pictures (web/data/plans.json, evidence-checked by 200), and have the local model fit each one the way
the 25 hand fits were made — fitkit sheet, grid labels, at least four matched-feature pairs, 202's
scale/north/centre seed as the starting point (never the fit). The fitted pairs go through the existing
plan_fit similarity solver and then the gate (001): accepted -> an automatic platefit document with the
gate's score; refused or could-not-fit -> a review item (201's format) the human finishes by dragging in
under a minute. The 25 hand fits are never touched. Split into 203a (US built sites) and 203b (all the
rest); this parent comes back when both are done and verifies the whole original site set.

## Acceptance criteria
- [ ] (203a) every built site with region "US" (90 of 384) has run through the loop: at least one
      automatic platefit document (the gate's score recorded in the document) in
      data/db/platefits/ or an open review item in data/review/ - or an existing hand fit (that
      site stays exactly as it is).
- [ ] (203b) the same for every other built site: region != "US" plus the 6 sites with no region
      field at all (they must not be skipped).
- [ ] (203a) the hand fits are byte-identical after the batch: tests/golden/hand_fit_docs.sha256
      (created before the first batch write) records all 20 pre-batch platefit documents, and the
      test asserts every one of them is still byte-identical and the batch added files, none
      rewritten.
- [ ] (203a) docs/batch_us.md: how many US sites got an automatic fit / a review item / were
      already hand-fitted / had no candidate, the recorded seed, and the seeded sample list of
      automatically accepted fits (20 where there are at least 20, a page URL each) for the
      human's 18/20 check.
- [ ] (203b) the same report as docs/batch_eu.md; and the two reports agree on the union: every
      built site is covered exactly once, no site in both.
- [ ] (203, on return) the final coverage check over the original site set: every built site that
      existed before the source growth (204-210) has a fit (hand or automatic) or an open review
      item - tests/test_batch.py. Coverage of the new sites built by 211 is asserted by 212, not
      here (212 runs after the parent and re-covers the new material itself).

## Notes
- The shared loop (candidates -> fitkit sheet -> model fit -> fit -> gate -> document or item) lives
  in fit/batch_us.py (203a's); 203b imports it and does not rewrite it.
- A site whose pictures all fail the gate gets its review item anyway: GOAL.md wants a fit OR a
  ready item, and the human's drag is the authority. A site with no candidate at all gets a
  review item marked "no picture found" (212 later searches harder).
- The automatic documents use the page's existing platefit format (site, plan, pairs, crop,
  size) plus a recorded score and an "auto" mark, so the page's fit tool and 212's sync treat
  them exactly like a human save minus the authority (a human save bypasses the gate, 001's
  scope).
- Tests are hermetic: they run the loop on a fixed sample of sites that have in-repo ground
  (the tracked hand-fit sites), never the full 90/294 (most have no ground in this checkout and
  the tests have no network); the full runs are working-phase commands recorded in the reports.

## Hand-over
