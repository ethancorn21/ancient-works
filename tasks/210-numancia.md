Status: open
# 210: Numancia - the excavation plans of the 1860s
Depends on: 200
Touches: fit/src_numancia.py, data/catalog/extras_numancia.jsonl, data/commons/files_numancia.jsonl, data/commons/classified_numancia.jsonl, docs/lead_numancia.md, tests/test_src_numancia.py

## Goal
GOAL.md point 4: Numancia (the Roman city in Spain, already a built site on the map) gets
its excavation plans of the 1860s. The lead is unverified: find where the plans live (the
1860s-70s excavation reports - the excavations ran under Juan de Dios Villanueva - a book
on Internet Archive, a Spanish archive, or Commons), check that it is old enough, free and
machine-readable, and stage the rows tied to the site. If no free machine-readable copy
exists, document the search and drop the lead.

## Acceptance criteria
- [ ] The source of the 1860s plans is verified and recorded in docs/lead_numancia.md
      (where it is, its date, its freedom/license, how the pages are machine-readable) - or
      the lead is dropped, the file says exactly what was searched (sources, dates,
      paywalls, format problems) and why nothing qualified, and this task ends
      `Status: dropped`.
- [ ] If verified: staged rows - files_numancia.jsonl for every staged plan tied to the
      existing Numancia site (the identification is part of the verification: the plans
      must depict Numancia, and the row records the specific check) with the 200 evidence
      field and a classified row by hand ("plan"); the plan's date (1860s) recorded on the
      row. extras_numancia.jsonl only if the reports show other sites not in the catalog
      yet.
- [ ] fit/evidence.py check passes offline on every staged row; test (no network): the
      staged files join and the evidence check passes, with a golden sample of rows. If
      the lead was dropped, the test asserts the documentation exists and the staging
      files are absent or empty.

## Notes
- Numancia's excavation plans are the rare case where the drawing is younger than 150
  years would be (1860s = just about old enough) - the age is recorded on the row either
  way; plans of the structure are exempt from the 150-year rule (PLAN.md assumption 4).
- The site is already built with (or without) a drawing: this task adds candidate
  pictures, it does not fit them - the batch/cover loop does.

## Hand-over
