Status: in-progress
# 207: Roman sites - Roy (1793), Horsley (1732), Maclauchlan (1857)
Depends on: 200, 807, 808, 809, 817
Touches: fit/src_roman_horsley.py, fit/src_roman_maclauchlan.py, fit/src_roman_roy.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_horsley.py, tests/test_src_roman_maclauchlan.py, tests/test_src_roman_roy.py, tests/golden/, tasks/807-horsley-list-correction.md, tasks/808-horsley-stage.md, tasks/809-horsley-check.md

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
- [ ] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.
      (Horsley 5/5 green. Maclauchlan 3/4: test_check_staged_joins_and_passes red on the
      (e)-join checked-date skew - fresh stage() stamps today, the canonical row carries
      230's 2026-10-14 re-stamp. Root-caused 809@199; the permanent fix is 817 (Depends on),
      agent a's 230 interim CHECKED-constant patch is not on main yet. Ticked when 817 lands.)

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
(2026-10-15, iteration 200, agent c - the driver returned the parent after all subtasks
(207a done, 207b done, 207c dropped, 807/808/809 done). Re-verified every box on the tree
this session and TICKED 1-3. Box 4 is the only one left and it waits on open task 817
(the maclauchlan (e)-join checked-date fix) - Depends on now carries 817, so the driver
brings this task back once 817 merges. Status: in-progress (no open subtask family of its
own anymore; the one outstanding piece lives in 817).

**What was verified this session (2026-10-15, on this branch = main synced):**
- Box 1: fetch artifacts for both books in data/raw/books/ (britanniaromanao00hors,
  memoirwrittendu00maclgoog); triage A/B + list artifacts (data/books/triage/<ia>.A/.B,
  lists/<ia>.json+.map.json); docs/lead_roman.md has complete Horsley (936/936 A, B 17/0,
  24-entry list corrected in 807, recall 1.0/1.0/1.0/1.0) and Maclauchlan (171/171 A, B
  3/0, 6-line hand list, recall 1.0/1.0/1.0/1.0) sections; `git log --all` on
  data/books/index.jsonl and validation.json shows only 211/217/200-family + driver sync
  commits - no 207/807/808/809 commit ever wrote them. Roy half: 207c dropped per owner
  ask 008 ("drop Roy..."), the lead records the boxes stand on the two books alone.
- Box 2: data/commons/files_roman.jsonl = 18 rows (17 Horsley year 1732 + 1 Maclauchlan
  year 1858; all evidence.kind=caption_coords with named_place/place_*/site_*/dist_m,
  url/thumb = the stable IA /download/ page image, by= the book module);
  classified_roman.jsonl = 18 rows all p_plan=1.0 by=hand; data/catalog/extras_roman.jsonl
  = 9 new sites (luguvallium-q71551754 with QID + 8 no-QID, region lowercase, kind
  "roman fort"/"roman site", location_check checked). The four no-QID Antonine camps stay
  in extras.jsonl (reused, never re-created).
- Box 3: `fit/src_roman_maclauchlan.py --check` RC=0 (1/1 evidence, no join lines) and
  `fit/src_roman_horsley.py --check` RC=0 (17/17 evidence, no join lines), both offline.
  90%: Horsley 100% (17/17); Maclauchlan 1/3, the two missing (n0078, n0111) blank in this
  copy - each accounted in the lead's 90%-box subsection per the box's disjunct.
- Box 4 (the one left): tests/test_src_roman_horsley.py = 5/5 GREEN (register / offline
  check / non-vacuous join / negative controls / golden). tests/test_src_roman_maclauchlan.py
  = 3/4: test_check_staged_joins_and_passes RED with `join: staged site
  luguvallium-q71551754 differs from its canonical row in extras.jsonl` - the daily
  (e)-join red: stage() stamps `checked = now()` (today 2026-10-15) while the canonical
  row in extras.jsonl carries 230's 2026-10-14 re-stamp, and _canon_norm is a full-row dump
  that does not zero the date. Root-caused at 809@199 (DECISIONS); the permanent fix is
  open task 817 (zero location_check.checked in _canon_norm, the module's golden _norm
  already does exactly this; twin latent in the horsley module = 818, not a 207 blocker).
  Agent a's 230 also carries an interim patch (stored CHECKED constant, commit fa230d24)
  but that is on agent/a only, not main, and it self-ages again at the next 230 re-stamp
  - 817 is the fix 207 waits on.

**Exact next step (the driver brings this task back once 817 is on main):**
1. Confirm 817 landed: `git log --oneline main | grep 817` (and 818 if present); glance at
   fit/src_roman_maclauchlan.py _canon_norm for the `0000-00-00` zeroing of
   location_check.checked.
2. `.venv/bin/python -m pytest tests/test_src_roman_maclauchlan.py -q -p no:cacheprovider`
   -> all 4 green (incl. the new date-only-differs-does-not-fire control).
3. Re-run tests/test_src_roman_horsley.py + `fit/src_roman_horsley.py --check` (if 818 or
   230's CHECKED-constant patch touched the module on the way to main, confirm the
   17/17 + no join lines and the golden file is byte-stable).
4. Tick box 4, set Status: done. If anything in 1-3 surprises (a new red not in
   PITFALLS/DECISIONS), stop and file the blocker per the stuck rule.

**Standing facts (keep):**
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
