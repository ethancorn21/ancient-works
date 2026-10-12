Status: open
Depends on: 302c
Touches: pipeline/plan_fit.py, tests/test_fit_provenance.py

# 219: The page's source line states the book's year once (the commons case)

## Goal
303's live shotwick run (docs/site_flow.md, 2026-10-11) exposed a blemish in `plan_fit.build`'s
commons source line:

    Shotwick Castle, plan from Mackenzie, The Castles of England (1897) (1897), Wikimedia
    Commons: by The British Library; No restrictions; ...

The picture's title already states the book's year, and the document's label (`"1897"`) repeats
it. A source line should state each fact once: when the label's year is already in the title,
drop the label's parenthesis; only a title without a year shows the label (or "undated"). The
book branch (`{book}: {title or label}`) and the who-placed clause (303) are not touched.

## Acceptance criteria
- [ ] `plan_fit.build`'s commons branch prints `TITLE (LABEL), Wikimedia Commons: CITE.` with the
      `(LABEL)` parenthesis dropped when the title already contains that year, and "undated" only
      when the title carries no year at all; the book branch and the how-clause are byte-identical
      for every existing document (a test proves it for a book doc and for a yearless commons
      title).
- [ ] The built commons depictions in the repo carry the fixed line - at minimum shotwick's
      `web/data/sites/shotwick-castle-q7502621/depictions.json` (gitignored; its overlay is
      current, so a one-off re-bake of the entry's `source` field is the smallest honest
      re-bake: same corners, same fit record, only the string changes) - and a hermetic test
      pins the new string for the shotwick document end to end.
- [ ] The full suite is green (the 303 tests' pinned strings stay intact: none of them pin the
      commons how-clause with a doubled year).

## Notes
- Filed by 303 (agent a), whose live run produced the string; not fixed there (a string-format
  change in `plan_fit.build` is outside 303's provenance scope).
- Depends on 302c only because both touch `pipeline/plan_fit.py` (keep the edits disjoint; 302c
  is the 302 decision/wiring task).
