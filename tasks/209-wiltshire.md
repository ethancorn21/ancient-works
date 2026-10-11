Status: open
# 209: Wiltshire - Hoare, Stukeley, Petrie for Stonehenge and Avebury
Depends on: 200
Touches: fit/src_wiltshire.py, data/books/triage/, data/books/lists/, data/commons/files_wiltshire.jsonl, data/commons/classified_wiltshire.jsonl, docs/lead_wiltshire.md, tests/test_src_wiltshire.py

## Goal
GOAL.md point 4: old drawings of the two most famous sites on the map - Stonehenge and
Avebury - from Hoare, Ancient Wiltshire (1812-21), Stukeley's Wiltshire volume (1740s) and
Petrie's Stonehenge (1880). Index the relevant plates with the existing book machinery
(per-book files only; the shared index.jsonl and validation.json are rebuilt by 211), and
stage the rows tied to the existing sites (stonehenge, avebury, and the other Wiltshire
henges the plates show). The sites are already built; this task adds their pictures. An
extras file is only needed if a plate shows a Wiltshire earthwork not in the catalog yet.

## Acceptance criteria
- [ ] The three works are fetched from the Internet Archive (data/raw/books/<ia>/) and
      triaged with the existing machinery, per-book artifacts only (lists/<key>.json,
      triage/<ia>.*); the shared data/books/index.jsonl and validation.json are NOT written
      by this task. Each work's printed list of plates is mapped (the books_lists pattern)
      and the stage-A/B recall recorded in docs/lead_wiltshire.md per work.
- [ ] Staged rows: files_wiltshire.jsonl for every staged Stonehenge / Avebury / Wiltshire
      earthwork plate tied to an existing site (by QID, or by the work's printed list where
      no QID exists), each with the 200 evidence field (the specific check - list entry,
      caption, coordinates distance - recorded on the row) and a classified row by hand
      ("plan"); the work's date (1740-1880) recorded on the row.
- [ ] The human's existing hand fits on these sites (already in data/db/platefits/ and
      fitted onto the pages) are not re-staged or re-fitted by this task: new rows only.
- [ ] fit/evidence.py check passes offline on every staged row; test (no network): the
      staged files join (every row names an existing site, or a staged extras row if any)
      and the evidence check passes, with a golden sample of rows.

## Notes
- Stukeley's Wiltshire (1740s) has several volumes/editions on IA: use the one with the
  complete plate set, recorded in docs/lead_wiltshire.md.
- If the three works are too much for a few sessions: split into 209a (Hoare), 209b
  (Stukeley), 209c (Petrie) - one work per subtask, each with its own per-book artifacts and
  its own staging suffix (files_wiltshire_a.jsonl etc.), same shape of boxes; record the
  per-work page list in this parent's hand-over. 211 consolidates whatever staging exists.
- A plate that shows a site outside Wiltshire (Stukeley travelled) is still staged, with the
  right site - the task is named for the lead, not a boundary.

## Hand-over
