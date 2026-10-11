Status: open
# 203b: The batch, rest of world - every non-US built site
Depends on: 203a
Touches: fit/batch_eu.py, data/db/platefits/, data/review/, docs/batch_eu.md, tests/test_batch_eu.py

## Goal
The same loop as 203a, for every other built site: all sites with region != "US" plus the 6
sites with no region field at all (294 of 384) - none of them may be skipped. The shared loop
is imported from fit/batch_us.py (203a's module); this task writes only the non-US documents
and items. 203a's US output is already merged into this branch when the task starts.

## Acceptance criteria
- [ ] fit/batch_eu.py imports the loop from fit/batch_us.py and runs it over every non-US built
      site; every such site ends with at least one automatic platefit document (score
      recorded) or an open review item - or an existing hand fit.
- [ ] The union of the two batch outputs covers every built site exactly once: a check against
      sites.json over the documents and items both tasks wrote - no site in both, none missing
      (the 6 region-less sites must appear in the EU list, not be dropped).
- [ ] docs/batch_eu.md in the same format as docs/batch_us.md: counts (automatic fit / review
      item / already hand-fitted / no picture found), the recorded seed, and the seeded sample
      of automatically accepted fits (20 where there are at least 20, a page URL each).
- [ ] After the run the hand-fit documents are still byte-identical to
      tests/golden/hand_fit_docs.sha256; the test (no network, port 0) runs the loop on a
      fixed sample of non-US sites with in-repo ground and asserts the invariants.

## Notes
- Do not re-implement the loop in fit/batch_eu.py: import it. If a change to the loop itself
  is genuinely needed, request it in a DECISIONS entry to the owner of fit/batch_us.py rather
  than copying it (one place for each piece of knowledge).
- The 20-sample lists of the two reports are separate (one per region); 212 picks the final
  combined 20-sample for the human's 18/20 check from the whole set.

## Hand-over
