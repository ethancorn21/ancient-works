Status: open
# 200: Evidence — every picture tied to its place, machine-checkable
Depends on: none
Touches: fit/evidence.py, data/commons/files.jsonl, data/commons/classified.jsonl, data/books/index.jsonl, tests/test_evidence.py

## Goal
GOAL.md point 3: every picture row records evidence a program can check that ties the picture to the site
it depicts: the file is in the Commons category of the site's Wikidata item (P373), or its structured data
says it depicts (P180) that item, or its title or caption names the place and the coordinates agree. Why:
the Rijksmuseum's "Gezicht op Hampton Court" is Hampton Court in Herefordshire (its caption says so), not
the palace; a name search alone gives the town for Barnard Castle and the village for Richard's Castle.

## Acceptance criteria
- [ ] `fit/evidence.py` records, in the `"evidence"` field of each picture row (data/commons/files.jsonl and
      the book index rows in data/books/index.jsonl that reach the plan list), which kind of tie holds —
      category (P373) / depicts (P180) / caption+coords / hand-tied QID — plus the specifics that proved it
      (the category page, the property value, the place named, the distance to the site) and a checked date.
- [ ] `evidence.py check` re-verifies every row offline from the stored fields only and lists failures; it
      runs clean on the committed rows.
- [ ] It fails closed: a row whose caption names a place that resolves to a different location (the Hampton
      Court trap) does not get a passing field; a row with no tie at all is reported, not silently kept.
- [ ] Test (no network): a fixed in-repo sample of rows with known-good and known-bad ties; golden output of
      the check over that sample.

## Notes
- The rows of `pipeline/sources.py` are hand-checked QIDs: their evidence kind is "hand-tied QID" (record the
  source name); verify each against the source's table, don't re-fetch.
- Wikidata/Commons metadata is fetched live in the working phase and stored in the row; `check` reads stored
  fields only (tests never fetch).
- Extend rows, never move or delete them; keep every existing field byte-identical.
