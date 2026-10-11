Status: open
Depends on: 302b
# 302c: The decision and the wiring - the method decides, site_done's fit step calls it
Touches: fit/inkfit.py, tools/site_done.py, pipeline/plan_fit.py, tests/test_inkfit.py, tests/golden/

## Goal
The method decides for itself when it is not sure (parent box 3): a confidence score with a threshold
SET ON THE 302b HELD-OUT TABLE. Confident fits become automatic platefit documents (auto: true,
"fitter": "ink", the gate's score); unsure fits never reach the map - they go to the site's review
item with the reason (the best starting pairs ride along, so the human drags from a good start).
`tools/site_done.py`'s fit step calls the method on the site's uncovered candidate pictures instead of
the batch's model loop (the station that made the fabricated patterns is replaced at the source; the
line's fabrication check stays as the second line of defence). `pipeline/plan_fit.py`'s build gets the
truth-telling source line for fitter:"ink" documents (today it says "Fitted automatically by the
batch" for any auto doc).

## Acceptance criteria
- [ ] The confidence threshold is fixed on the 302b table (the rule and the chosen value written in
      docs/site_flow.md next to the table) and applied by fit/inkfit.py; an unsure result carries a
      human-readable reason string.
- [ ] site_done's fit step runs the method on uncovered candidates: confident -> new ink-fit document
      (which the existing sync path then checks and builds); unsure -> review-item candidate with the
      reason via fit/review.upsert_item (the item format of data/review/README.md, no new fields the
      page cannot ignore). Covered pictures are still never re-fitted; exit codes unchanged.
- [ ] plan_fit.build prints/stores the correct source line for fitter:"ink" documents (not "by the
      batch"); hand fits and the 20 golden documents stay byte-identical (tests/golden/hand_fit_docs.sha256
      stays green).
- [ ] tests/test_inkfit.py: end to end on ONE hand-fit site's files in the temp tree, no network - the
      site's real plate image and a committed relief seed (data/inkfit/relief/<site>.npz or a
      tests/golden seed, written by this task) drive tools/site_done.py --root; the test asserts through
      the product: the line's per-picture report, the resulting document or review item, and what the
      served page shows for that site. The model step is injectable (a recorded answer), so the test
      never touches a model server.
