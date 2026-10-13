Status: open
Depends on: 306c, 306d, 306e, 306f
Touches: tests/test_fit_provenance.py

# 231: Re-point the two fit_provenance pins off the deleted bethlehem doc

## Goal
tests/test_fit_provenance.py has two tests that read a real store doc by id and it no longer
exists: `bethlehem-q2523914.c_a164ee440558d66c` was one of the 3 fabricated bethlehem batch
docs the 306a audit took off the map (a858f48 / main 20277f3; grid-round anchors). The audit's
own task (306a, done) lists this test file in its Touches, so the re-point was meant to happen
there; it did not. Until fixed both tests fail with
`FileNotFoundError: data/db/platefits/bethlehem-q2523914.c_a164ee440558d66c.json` on every
branch (verified on pure main 20277f3 and on agent/a's pre-merge tree).

## The two pins
1. `test_commons_yeared_title_drops_the_repeated_year` - pins the year-once source-line rule on
   that doc (a surviving-shape batch doc whose title states the 4-digit year, 1748; expected
   line: "Plan de Maestricht et environs 1748, detail Severen & Kanjel (cropped), ... Fitted
   automatically by the batch on 4 matching points; ... within 113 m (gate score 39.3 m)" plus
   the assert that " (c. 1748)" is absent). Re-point to a surviving batch doc with a year in
   the title (recompute the expected line from the doc: title, cite, pairs/scale fit text,
   gate score; the doc's by/score fields determine the how-clause).
2. `test_line_refuses_unmarked_non_auto_doc` - case (b): seeds an UNMARKED (no `by`) non-auto
   copy of a doc on a site and pins the one-site line's refusal (plan_fit.NO_PROVENANCE) and
   the item resolution. It builds the seed from `_golden_doc(SEED_PLAN)` (read the current
   test for SEED_PLAN) plus `_preconditions_b`; the deleted bethlehem doc is the store doc the
   test's tree expects to find. Re-point SEED_PLAN to a surviving doc of the same shape, or
   (if the audit leaves no unmarked-shape survivor) construct the seed doc in the temp tree
   instead of reading one from the store - the refusal behaviour does not depend on which doc.

## Acceptance criteria
- [ ] Both tests pass against the post-306 doc store (run alone, then in the full suite; no
      other test's pins disturbed).
- [ ] Every doc the re-pointed pins read still exists in data/db/platefits/ at run time, and
      the expected source-line strings are recomputed from the pinned doc's own fields
      (title/cite/pairs/score) - not copied from the old bethlehem expectation.
- [ ] The test docstrings updated to say which audit removed the original pins (306a) and why
      the case now lives on the new doc(s).

## Notes
- Wait for 306c-f (orphan-fit audits, in flight): they delete more agent docs, and a pin
  chosen before they settle risks being audited off in turn. 306a/306b are done.
- Do not resurrect the bethlehem docs (the audit's verdict stands - the anchors were
  fabricated); only the test's pins move.
- Verified red on pure main (20277f3) in a /tmp worktree, 2026-10-13.
