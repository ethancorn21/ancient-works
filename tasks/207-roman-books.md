Status: open
# 207: Roman sites - Roy (1793), Horsley (1732), Maclauchlan (1857)
Depends on: 200
Touches: fit/src_roman.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman.py

## Goal
GOAL.md point 4: index the three old Roman books with the existing book machinery
(pipeline/books.py: fetch, triageA/B, list mapping, validate) - Roy, Military Antiquities of
the Romans in North Britain (1793); Horsley, Britannia Romana (1732); Maclauchlan, the survey
of the Roman Wall (1857) - and stage their site-plan rows tied to Roman sites, existing in
the catalog or new. This task writes only per-book artifacts (its own triage/<ia>.*,
lists/<book>.json) and its own staging files; the shared index.jsonl and validation.json
are rebuilt once by 211 (books.py index regenerates the index from the per-book files).

## Acceptance criteria
- [ ] Each book is fetched from the Internet Archive (data/raw/books/<ia>/) and triaged with
      the existing machinery, per-book artifacts only; the shared data/books/index.jsonl and
      validation.json are NOT written by this task. Each book's own printed list of plates
      is mapped (the books_lists pattern), and the stage-A/B recall against that list is
      recorded in docs/lead_roman.md per book (instead of the shared validation.json).
- [ ] Staged rows: files_roman.jsonl for every site-plan row tied to a Roman site - an
      existing catalog site by QID where one exists, or a new extras_roman.jsonl entry
      (kind "roman fort" / "roman site", QID where it exists, lon/lat from the book's list
      or a cross-check) - each with the 200 evidence field (the book's printed list names
      the place; the specific check - list entry, caption, coordinates distance - recorded
      on the row) and a classified row by hand ("plan"); the book's date (1732-1857) is
      recorded on the row.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one is accounted for in docs/lead_roman.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.

## Notes
- If the three books are too much for a few sessions: split into 207a (Roy), 207b (Horsley),
  207c (Maclauchlan) - one book per subtask, each with its own per-book artifacts and its own
  staging suffix (files_roman_a.jsonl etc.), same shape of boxes; record the per-book page
  list in this parent's hand-over. 211 consolidates whatever staging exists.
- Maclauchlan (1857) also has a survey of the Wall itself: wall sections are not sites and
  are not staged, unless a named fort/structure with a location is in the plate.
- Books already indexed (the 8 in data/books/index.jsonl) are not re-triaged; this task only
  adds its three.

## Hand-over
