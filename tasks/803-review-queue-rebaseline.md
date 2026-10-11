Status: open
Depends on: 203a
Touches: tests/test_review.py

# 803: review-queue tests: re-baseline to the post-batch item population

## Goal
Task 201's tests were calibrated to the pre-batch review population: data/review/ held the
201-seeded alligator item (2 candidates) and the bibracte no-picture item - 2 items, both
open. The 203a US batch (merged) upserted 88 more item files (one per US site with a
candidate, plus 71 "no picture found" items), and alligator's item gained a DERIVED
resolution: its c_618a candidate became an automatic document, and 201's export derives
that as resolved. The population is now 89 items, 88 open. Three tests fail on that
delta:

- `test_export_cli`: asserts the stdout "review: 2 open of 2 items" and pins the open
  list to [alligator, bibracte]; now the export prints "review: 88 open of 89 items"
  and the open list is the 88 others (alligator's item is resolved).
- `test_page_shows_the_review_list`: pins the Review tab count ("Review (2)"), the
  home stats line ("2 review items open") and the item phrases to the 2-item population.
- `test_save_resolves_the_item`: builds the human-save document from alligator's LEAD
  entry's stored fields (`map_box`, `size`, `ia`, `file`, `label`, `book`, `cite`). The
  batch's upsert replaced that entry with 203a's item-entry shape (plan, title, url,
  evidence, pairs, why, gate_score - no map_box/ia/file/...), so the test dies with
  KeyError 'map_box'; and alligator's item no longer ends "open after the save" the way
  the test expects, because the export already derives it resolved from the c_618a
  document.

The 201 behavior under test (the upsert merge, the export derivation of `resolved` from
data/db/platefits/ documents, the resolve-on-save flow, the page's review view) is
unchanged and believed correct: the failures are the tests' hardcoded pre-batch
population, not the writer. If a failure instead proves the writer wrong, record it in
this task's DECISIONS entry before changing anything - that is an 803 finding, not a
silent fix in fit/review.py.

## Acceptance criteria
- [ ] tests/test_review.py is green: the expected export stdout, the open-item list, the
      page's review count/stats and the resolve-on-save flow are derived from data/review/
      through 201's own rules (upsert merge, export derivation of `resolved` from
      data/db/platefits/ documents) instead of hardcoded pre-batch numbers - so a future
      batch (203b) adding items does not break them again
- [ ] `test_save_resolves_the_item` picks its site and plan deterministically from a row
      that still carries the fields the page's save needs (a book row with `map_box` and
      `size` in web/data/plans.json, whose site's item is still open after the export
      derivation) instead of from the item entry's stored fields; the PUT-resolves-item
      flow it checks is the same as before
- [ ] no behavior change in fit/review.py, the page or the data files: the only files this
      task writes are its own test and (if the wording drifts) this task file; any needed
      writer change is recorded in a DECISIONS entry with evidence first

## Notes
- Filed by agent c (task 203a) iteration 41, from the full-suite run after the 203a
  working run landed on this branch (4 failed / 34 passed; the other failure is 802's).
- The test's queue fixture already re-seeds the temp tree from the repo's items through
  the upsert API, so the post-batch population is what the fixture serves; only the
  assertions (and the save test's row selection) are out of date.
