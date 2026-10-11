Status: open
# 206: Mackenzie - the five-towered castle on page 212
Depends on: 001, 200
Touches: fit/src_mackenzie.py, data/catalog/extras_mackenzie.jsonl, data/commons/files_mackenzie.jsonl, data/commons/classified_mackenzie.jsonl, docs/lead_mackenzie.md, tests/test_src_mackenzie.py

## Goal
GOAL.md point 4: page 212 of Mackenzie, The Castles of England (1897) is a five-towered
castle plan with no caption - the only gap in the book's already hand-tied 29 plates
(pipeline/sources.py). Identify the castle with evidence (the book is arranged by county:
the plates around p.212 - p.207 Oxford, p.231 Lancaster - constrain it; five-towered plans
are rare; the surviving ground is the final check), tie it to a site, stage the row, and let
the fit prove the identification. If it cannot be identified with evidence, document the
search and drop the lead: a wrong castle on the map is worse than none.

## Acceptance criteria
- [ ] The p.212 scan is found (the British Library's Flickr scans, the same URL pattern as
      the hand-tied rows) and downloaded to data/raw/books/ in the working phase; the
      five-towered plan is drawn out and available for comparison (its shape, tower count,
      and any scale/north information recorded in docs/lead_mackenzie.md).
- [ ] The castle is identified by evidence recorded in docs/lead_mackenzie.md: the book's
      county context, the plan's shape against candidate castles, and the surviving ground
      (relief/aerial) matching the plan - or the lead is dropped, and the file says exactly
      what was searched, what candidates were considered, and why none was accepted.
- [ ] If identified: the site (an existing one by QID, or a new extras row) and the picture
      row are staged (files_mackenzie.jsonl with the 200 evidence field - caption+coords or
      QID, the source book recorded - and a classified row "plan" by hand), and a fit of the
      plan on the site's ground passes the gate (001): the identification is proven by
      numbers, not just asserted.
- [ ] Test (no network): the staged row joins and passes fit/evidence.py check offline, with
      a golden sample. If the lead was dropped, the test asserts the documentation exists
      and the staging files are absent or empty.

## Notes
- The other 29 Mackenzie plates stay where they are (sources.py hand ties); this task adds
  at most one row. The fit is proposed through 202's machinery if available; otherwise a
  hand proposal (fitkit) is fine - this is one plate, not a batch.
- A castle whose site is not built yet: the extras row gets the picture as its reason to
  build (aerial_ok) so 211 builds it with the plan already tied.

## Hand-over
