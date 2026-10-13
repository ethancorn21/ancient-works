Status: open
Depends on: 212, 231
Touches: tests/test_site_done.py, tests/test_fit_provenance.py

# 232: Re-pin the shared Stonehenge snapshot (14th candidate in, post-212 state)

## Goal
Two tests pin one shared snapshot of stonehenge-q39671 and both fail on the merged
tree (main 20277f3): tests/test_site_done.py::test_site_done_line and
tests/test_fit_provenance.py::test_line_refuses_unmarked_non_auto_doc (case b). The
snapshot they pin: plans.json rows naming the site (13), the site's review item
(data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json: 13 candidates =
7 "line check:" entries from the 7 golden pattern docs in
tests/golden/stonehenge_linecheck_docs/ + 6 batch entries), zero Stonehenge fit docs in
the store, 0 drawings, and the published review.json entry matching the item.

What moved: main f970500 (the lead's Mac port, the 211 pictures) added a 14th plans
row for the site: c_61b86efb4511e099 "Stonehenge, inward view by William Stukeley,
1722 (Itinerarium Curiosum)" (Wikimedia Commons, File:Stonehenge Dessin Stukeley 1722
03547.jpg, [1280,673]). It is not in the item file (13 candidates, verified
post-merge; the published page entry matches the item file), so both tests'
"plans.json holds exactly the 13 site candidates" precondition fails (site_done:
"plans.json no longer lists exactly the 13 … candidates (14 rows): the no-batch-run
precondition is void"; fit_provenance b: "plans.json no longer lists 13 … candidates:
the no-batch-run precondition is void"). The 14th candidate arrived with the 211
pictures, not with a batch run - say so in the docstrings when re-pinning.

212 (runs before this task) then changes the same snapshot live: its loop runs the
one-site line on Stonehenge (14 unfitted candidates, no docs, 0 drawings), so the run
upserts the 14th candidate into the item (why "no model answer" unless the matcher
places a fit for it), and if the ELoFTR matcher places a doc that passes the gate and
the line check, the store gains a stonehenge doc (by: agent), the item then RESOLVES
(201's derived resolution: any candidate with a doc in the store) and leaves the open
page, and the site ends with drawings >= 1. Either end state is correct behaviour;
this task re-derives the pins from whatever live state 212 leaves (and from whatever
the 306c-f audits then leave, if they touch it).

## The work (after 212 and 306c-f land)
1. Read the live state: plans rows naming the site (expect 14); the item file
   (candidates: 14 if no doc was placed, else the pre-run 13 + the placed plan's
   entry, with the resolved field set); the store (0 or 1 stonehenge docs);
   sites.json's drawings for the site; the review.json entry (it must equal the item
   file's candidates - 212's sync re-exports it; if a doc resolved the item, the page
   no longer lists it).
2. Re-pin both tests to that state: the preconditions (row count; candidate count and
   membership; golden-doc vs live-doc split; page entry == item, or absent) and the
   expected line-by-line outputs (the per-picture report now includes the 14th row;
   the fit line's "N candidate picture(s): M fitted (doc)" counts; the review line's
   "open of N items" counts). Derive the expected bytes by running the copied line in
   the test's temp tree on the live snapshot (both tests already do this) - never by
   hand-typing entries.
3. test_site_done's rewind: pre_item = the live item minus its "line check:" entries.
   If the live run placed a matcher doc, the tree also carries that doc (the copy
   loop copies the whole store) - its expected treatment (skipped: overlay current,
   or built) and the second run's expectations come out of the same live run;
   re-derive them from the tree's actual output.
4. test_fit_provenance case b: the seed stays the golden doc c_022604d2be0becdc minus
   its auto mark (first verify it is still an unmarked auto golden doc - the goldens
   are frozen files); only the 13-to-live snapshot pins and the expected lines move.
   If the live run's matcher doc happens to be the seed plan, re-derive the seed from
   another of the 7 goldens and say why in the docstring.
5. Both docstrings: the 14th candidate came in with the 211 pictures (main f970500),
   not a batch run; if a matcher doc is part of the snapshot, say 212's live loop
   placed it (the ELoFTR matcher - never a vision-model fit, 301's model must not
   place).

## Acceptance criteria
- [ ] Both tests pass against the post-212 (and post-audit) live state, run alone and
      in the full suite; no other test's pins disturbed (231 already re-pointed case
      e's pin, so case b is the only fit_provenance pin this task moves).
- [ ] Every doc/item/row the pins read exists in the repo at run time, and the
      expected strings are re-derived from the live files (recorded item entries
      recomputed with the line's own entry builders - the tests already do this for
      the 7 golden docs; extend it to whatever the live run added).
- [ ] The docstrings carry the provenance note of step 5.

## Notes
- Depends on 212 (it writes the item/store/page state this task re-derives - do it
  after) and on 231 (both edit tests/test_fit_provenance.py - 231 first; it touches
  only case e, this task only case b).
- If the 306c-f orphan audits delete a doc this snapshot carries, re-derive again
  from whatever they leave - the recipe is the same.
