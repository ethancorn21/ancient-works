Status: open
Depends on: 212, 306c, 306d, 306e, 306f
Touches: tests/test_fit_queue.py, web/data/fit_queue.json

# 234: Fit queue - align the test's ordering key with the generator, refresh the file

## Goal
tests/test_fit_queue.py::test_fit_queue_real regenerates the queue on a copy of the
checkout's live inputs and asserts the entries are sorted by (view, -draw_px, name)
(the keys built just above the final `keys == sorted(keys)` assert). The generator
(tools/fit_queue.py, `_best_key` plus the name) sorts by the DOCUMENTED key
(view, -draw_px, plan, name) - the plan id is the tie-break when two sites' best
pictures have equal pixel area. Main's new rows (f970500) created a breaking pair:
Lessines (lessines-q667790, best c_0193a1cf01ab0b87) and Avesnes-sur-Helpe
(avesnes-sur-helpe-q217178, best c_61fbbcd3d6051cd9) - both view False, both size
[1280,1842] (= 2357760 px); plan order (c_0193… < c_61fb…) puts Lessines first, name
order would put Avesnes first, so the test's (view, -px, name) assertion fails. The
test is the thing out of date: the plan tie-break is the documented generator
behaviour, and 307bb's headless page-card pins depend on the generated entry order,
so tools/fit_queue.py's sort must NOT change. (The pair exists only in a checkout
whose live web/data/sites store holds both site dirs - it fired in agent/a's tree
after the merge and not in the main worktree, which has no committed site dirs for
the 11 new sites.)

## The work (after 212 and the 306 audits land)
1. tests/test_fit_queue.py: change the real test's ordering key from
   (view, -draw_px, name) to the generator's documented (view, -draw_px, plan, name)
   (insert the best candidate's plan id before the name in the key tuple - one
   field, no other assertion moves). Note in the test docstring that the plan id is
   the generator's documented tie-break for equal-size best pictures and that
   307bb's page-card pins depend on the entry order - the sort is not to be
   "simplified" back to (view, -px, name).
2. web/data/fit_queue.json (currently committed at 229 entries, "at"
   2026-10-13T04:09:15 - the driver's sweep after 206 committed agent/a's probe
   regeneration): 212's sync (per-site drawings/overlays) and the 306c-f audits
   (review candidate upserts, doc deletions) both move the queue's live inputs after
   that timestamp. Regenerate the file with the generator on the settled checkout,
   verify it is byte-reproducible (run the generator twice, byte-compare), and commit
   the refreshed file with its new "at". If the regeneration is byte-identical to the
   committed file, there is nothing to commit there - say so in the commit message.
3. Run test_fit_queue_real (and the other fit_queue tests) against the refreshed
   file; the rest of the suite stays as green as it was before this task.

## Acceptance criteria
- [ ] test_fit_queue_real passes with the (view, -px, plan, name) key, alone and in
      the full suite; the Lessines/Avesnes pair orders by plan id, as the generator
      does.
- [ ] The committed web/data/fit_queue.json equals the generator's output on the
      current live state (byte-reproducible; a new "at" if the state moved).
- [ ] tools/fit_queue.py is untouched (the sort is the documented behaviour 307bb
      depends on).

## Notes
- Depends on 212 (its sync changes the queue's drawing/overlay inputs) and 306c-f
  (their candidate upserts and doc deletions change the review-derived inputs):
  regenerate only after all of them, so the committed file is the settled state, not
  an intermediate one.
