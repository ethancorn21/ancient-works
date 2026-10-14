Status: split
# 207: Roman sites - Roy (1793), Horsley (1732), Maclauchlan (1857)
Depends on: 200, 807, 808, 809
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
(2026-10-14, iteration 137, agent c - the driver returned the parent after 207a (done),
207b (done), 207c (dropped). All four boxes were re-verified against the tree: NONE can be
ticked yet, because every box's Horsley half sits in the continuation chain 807 -> 808 ->
809, which the lead had blocked (commit 06c1aa8) on the owner's "Stop 207". The owner's own
recorded answers supersede that block (asks 006/007 answered "b" = the stop is LIFTED,
explicitly including "its site-plan pages staged onto the map"; ask 008: "If you need it get it. If you can't get it, then you don't need it."), and the block had no open request
attached (AGENTS.md: a blocked task waits only while its request is open), so this session
unblocked the three (Status: open) and wired them into this task (Depends on + Touches).
Bookkeeping only: no code, no data; no test reads tasks/*.md (verified), so the suite is
unaffected and the driver's loop-start baseline stands (1 failed / 159 passed / 1 skipped;
the red = agent a's 307bb placement test, known pre-existing). Next session the driver
hands out 807 first.)

**Ask 003 (the one the loop flagged this session), read to the end:** the owner approved
the recommendation ("Use your recommendation.") = download the NLS facsimile of Roy into
data/raw/books/roy1793/. The files never arrived (verified this session: the directory
does not exist), and ask 008 (2026-10-13 14:36) is the owner's final word on it: "drop
Roy. I dont want to have to ever go out and get a file. ..." 207c stays DROPPED; no
re-ask (the standing rule, 207c's hand-over).

**Box state of this task (verified on the tree, 2026-10-14):**
- Box 1 (fetch/triage, per-book list + recall in docs/lead_roman.md; shared
  data/books/index.jsonl and validation.json NOT written): Maclauchlan DONE (171 fetch,
  A 171/0, B 3/0, the 6-line hand list, recall 1.0/1.0/1.0/1.0, section written; git shows
  no 207-family commit ever touched the two shared files). Horsley PENDING 807: 936 fetch +
  A 936/0 + B 17/0 are done, but the list is still the 22-entry version (n0114/n0185 were
  proven genuine site plans at 220) and the Horsley lead section is not written yet.
- Box 2 (staged rows with the 200 evidence field and the book's date): Maclauchlan DONE
  (one row n0093, 1858, new extras site luguvallium-q71551754 + the "plan" classified row).
  Horsley's 17 rows PENDING 808.
- Box 3 (fit/evidence.py passes offline on every staged row; >=90% of the verified
  site-plan pages staged, or each missing one accounted for in the lead doc): Maclauchlan
  DONE (check rc=0; 1 of 3 staged - the two missing are blank plates, accounted in the
  lead section, the box's disjunct). Horsley PENDING 808 (100% of 17 staged) + 809.
- Box 4 (no-network test: the join + the evidence check + a golden sample): Maclauchlan
  DONE (4/4 + golden). Horsley PENDING 809.
When the driver returns this task after 807/808/809 merge: re-verify each box on the tree
(re-run 809's --check offline, read the Horsley lead section, git-check the shared files
again) and tick what verifies, then set done.

**Exact next steps (the chain; the driver hands 807 out first).**
1. **807 (all offline, no LLM):** add the two list entries to HORSEY_FIGS (verbatim in
   807's Notes; leaf-order after the 62 line, before 236) -> update the module
   docstring/comment block 22/15 -> 24/17 with the 219 mislabel correction -> run the
   module's --list under the socket-block wrapper (807's Notes) -> the validate_book
   one-liner (807's Notes) must report recall_pages 1.0, recall_pages_pm1 1.0,
   precision_strict = precision_lenient 1.0 (17/17), no flags -> write the "## Horsley"
   section into docs/lead_roman.md BEFORE "## Roy" (807's box 3 spells out every number to
   record; the completeness proof, the catalog check and the stage-A/B numbers are in
   807's Notes). If /tmp/horsley_full is gone, re-download per 807's Notes (curl -L +
   browser UA). Stage B is already done (17/0) - do not re-run it.
2. **808 (after 807):** read fit/evidence.py IN FULL first (only skimmed at 220:
   check_caption ~line 190 / check_book ~265 / check_book_caption ~290). Build --stage per
   808's boxes: 17 rows (the 15 wall maps on the 216 QID/extras design - the mapping is in
   DECISIONS, search "castrum-segedunum"; n0114 -> the new Ardoch "roman site" row with
   Innerpeffery on desc; n0185 -> ONE row on the principal P.113 fort's new "roman fort"
   row, the other four names on desc); new extras_roman rows lowercase region
   (england/scotland), kind "roman fort"/"roman site"; REUSE the four no-QID Antonine
   camps from extras.jsonl, never re-create them. Append-only, idempotent, --dry; re-run
   after any merge.
3. **809 (after 808):** --check (the join over the whole staged roman set + the
   fit/evidence.py check on this book's 17 rows, fully offline), --golden,
   tests/test_src_roman_horsley.py (the no_network fixture per 809's Notes), then the
   full-suite re-baseline (the split baseline is stale; the current one = the driver's
   loop-start note above; the lone red = agent a's 307bb placement test, known
   pre-existing).
4. **Roy (207c, DROPPED - this recipe is the single source of truth per 207c's
   hand-over):** if a complete scan of the book (any layout: full PDF or page images) ever
   lands in data/raw/books/roy1793/: adapt the fetch to the local files (the
   Wiltshire-Hoare 3-point in-process wrap: books_ia.pages / books_ia.page_texts /
   books.fetch_triage for this id only, re-encoded into the books.triage_path slots;
   pipeline/books.py's LLM ports are already correct per 215 - no in-process patch
   needed), then the same pipeline; transcribe the book's printed 51-plate list by eye
   from the arrived pages (no OCR text for the book exists in any accessible copy); rows
   tagged with this book (region scotland, year 1793), mostly NEW Scottish fort sites in
   extras_roman.jsonl - tie to the four no-QID Antonine Wall camps (bar-hill-fort,
   inchtuthil, raedykes, rough-castle-fort) where a plate matches; stage-A/B recall in the
   Roy section of docs/lead_roman.md; tests + golden as for the other books. (The owner's
   008 policy makes this a maybe-not: the book is unobtainable from this VM and the owner
   declined to supply it.)

**Per-book facts (corrected state as of 2026-10-14):**
- Horsley -> ia=britanniaromanao00hors (Google Books, 936 leaves, hOCR + djvu.txt; the
  Google scan IS the British Museum volume - shelf mark RB DA 145. H 86 folio on n0015;
  CITE from the title page n0014). The ~121 engraved inscription plates (Roman numerals
  I-CXXI) are kind o: indexed, never staged.
- Maclauchlan -> ia=memoirwrittendu00maclgoog (the 1858 original, 171 leaves, djvu.txt/xml
  only, no hOCR). The "1971 reprint" memoirwrittendur0000henr is a MISLABELED item (Linda
  Nochlin's Realism) - PITFALLS; the book's list is the per-leaf hand table.
- Roy -> not on IA; NLS maps.nls.uk WAF-blocked from this VM; HathiTrust 403; Google Books
  quota 0 (207c's hand-over; re-verified on the drop day).

**Suite baseline (for the 807-809 sessions):** the driver's loop-start note before
iteration 137: 1 failed / 159 passed / 1 skipped (the red =
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, agent a's 307bb
work on merged main - known pre-existing, PITFALLS). No test reads tasks/*.md (verified
this session), so the bookkeeping above cannot move the suite; the 807-809 sessions
re-baseline on their final run per their own Notes.
