Status: done
# 207: Roman sites - Roy (1793), Horsley (1732), Maclauchlan (1857)
Depends on: 200, 807, 808, 809, 817
Touches: fit/src_roman_horsley.py, fit/src_roman_maclauchlan.py, fit/src_roman_roy.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_horsley.py, tests/test_src_roman_maclauchlan.py, tests/test_src_roman_roy.py, tests/golden/, tasks/807-horsley-list-correction.md, tasks/808-horsley-stage.md, tasks/809-horsley-check.md, docs/site_flow/307d_B_1-card.png

## Goal
GOAL.md point 4: index the three old Roman books with the existing book machinery
(pipeline/books.py: fetch, triageA/B, list mapping, validate) - Roy, Military Antiquities of
the Romans in North Britain (1793); Horsley, Britannia Romana (1732); Maclauchlan, the survey
of the Roman Wall (1857) - and stage their site-plan rows tied to Roman sites, existing in
the catalog or new. This task writes only per-book artifacts (its own triage/<ia>.*,
lists/<book>.json) and its own staging files; the shared index.jsonl and validation.json
are rebuilt once by 211 (books.py index regenerates the index from the per-book files).

## Acceptance criteria
- [x] Each book is fetched from the Internet Archive (data/raw/books/<ia>/) and triaged with
      the existing machinery, per-book artifacts only; the shared data/books/index.jsonl and
      validation.json are NOT written by this task. Each book's own printed list of plates
      is mapped (the books_lists pattern), and the stage-A/B recall against that list is
      recorded in docs/lead_roman.md per book (instead of the shared validation.json).
      (Roy 207c DROPPED per owner ask 008 - unobtainable from this VM, the owner declined to
      supply it; the lead records that boxes 1-4 stand on the two obtained books alone.)
- [x] Staged rows: files_roman.jsonl for every site-plan row tied to a Roman site - an
      existing catalog site by QID where one exists, or a new extras_roman.jsonl entry
      (kind "roman fort" / "roman site", QID where it exists, lon/lat from the book's list
      or a cross-check) - each with the 200 evidence field (the book's printed list names
      the place; the specific check - list entry, caption, coordinates distance - recorded
      on the row) and a classified row by hand ("plan"); the book's date (1732-1857) is
      recorded on the row. (Maclauchlan rows carry 1858, the year printed on the title page
      - the lead's date investigation.)
- [x] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one is accounted for in docs/lead_roman.md.
      (Horsley 17/17 = 100%; Maclauchlan 1/3, the two missing are blank in this copy, each
      accounted in the lead's 90%-box subsection per the disjunct.)
- [x] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.
      (Verified it.203 after 817/818 landed on main: horsley 5/5 green incl. golden, maclauchlan
      4/4 green incl. test_check_staged_joins_and_passes - the daily (e)-join red is dead on any
      day; both modules' offline --check RC=0, 17/17 and 1/1, zero join lines.)

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
(2026-10-15, iteration 203, agent c - DONE. All four boxes verified and ticked.)

**This session (merged main into agent/c, then closed box 4):**
- Merge e401ce58: 817 (45f4757f) and 818 (a95bcbfa) both landed on main - `_canon_norm`
  zeroes the volatile `location_check.checked` date (0000-00-00, the golden _norm idiom) in
  BOTH roman modules, and stage() stamps the live now() again (230 it.237's interim CHECKED
  constant removed). The two 307d PNG merge conflicts (A_1-card, B_5-reload) resolved to
  main's bytes per the PITFALLS 307d recipe (neither side carries unique content).
- Box 4 verified on the merged tree: `tests/test_src_roman_maclauchlan.py` 4/4 (incl.
  test_check_staged_joins_and_passes - the daily red is dead; 817's new (d)/(e) date-only
  controls pass both directions) and `tests/test_src_roman_horsley.py` 5/5 (incl. golden,
  byte-stable); offline `fit/src_roman_horsley.py --check` RC=0 (17/17, zero join lines) and
  `fit/src_roman_maclauchlan.py --check` RC=0 (1/1, zero join lines).
- Boxes 1-3 (ticked it.200) re-confirmed standing: no roman data files touched by this
  session; the merge brought only the 817/818/230 module/test code changes.
- Merge hygiene: the branch also carried a stale re-encode of docs/site_flow/307d_B_1-card.png
  (an earlier driver "uncommitted work" commit; main never touched it since the base, so it
  was not a conflict). Restored all ten 307d PNGs to main's bytes (only B_1 changed) so this
  branch merges into main without a binary-conflict spiral (PITFALLS 307d, the 6af207b
  precedent); B_1 added to this task's Touches line for it.
- Status: done. If the driver rejects, the reopen recipe: re-run the two test files
  (`.venv/bin/python -m pytest tests/test_src_roman_{maclauchlan,horsley}.py -q -p
  no:cacheprovider`) + the two offline --checks on the current tree; nothing else is left
  in this lane.

**Standing facts (kept):**
- Roy is DROPPED (owner 008, final word): no re-ask, no stand-ins. If a complete scan of
  the book (any layout) ever lands in data/raw/books/roy1793/, the resume recipe = the
  Wiltshire-Hoare 3-point in-process wrap (books_ia.pages / books_ia.page_texts /
  books.fetch_triage for this id only, re-encoded into the books.triage_path slots),
  transcribe the book's printed 51-plate list by eye (no OCR text exists for it), stage
  rows year 1793 region scotland, tie to the four no-QID Antonine camps where a plate
  matches, recall in the lead's Roy section, tests + golden as for the other books.
- Books: Horsley -> britanniaromanao00hors (936 leaves, hOCR + djvu.txt; the ~121
  inscription plates are kind o, indexed never staged); Maclauchlan ->
  memoirwrittendu00maclgoog (171 leaves, djvu only; the 1971 "reprint"
  memoirwrittendur0000henr is a MISLABELED Nochlin item - PITFALLS).
- After any full-suite run the docs/site_flow/307d_*.png goldens may re-encode (307d
  owner check, machine-specific): restore main's bytes before committing (PITFALLS).
