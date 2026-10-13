Status: in-progress
# 207c: Roy, Military Antiquities of the Romans in North Britain (1793)
Depends on: 200
Touches: fit/src_roman_roy.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_roy.py, tests/golden/src_roman_roy_sample.json

## Goal
Subtask of 207: index William Roy's *Military Antiquities of the Romans in North Britain*
(1793; the Society of Antiquaries folio: 174 text pages + 51 map plates of the Roman camps
and forts of Scotland) with the book machinery and stage its site-plan rows tied to Roman
sites (mostly NEW Scottish sites - the catalog has no QID-carrying Scottish roman_fort yet,
only the four no-QID Antonine Wall camps in extras.jsonl: bar-hill-fort, inchtuthil, raedykes,
rough-castle-fort).

## Acceptance criteria
- [ ] The book is fetched (the human-provided copy in data/raw/books/roy1793/) and triaged
      with the existing machinery, per-book artifacts only; the shared
      data/books/index.jsonl and validation.json are NOT written by this subtask.
- [ ] The book's own printed list of plates (51) is mapped to its pages; the stage-A/B
      recall against that list is recorded in the Roy section of docs/lead_roman.md
      (instead of the shared validation.json).
- [ ] Staged rows (appended to the parent's shared staging files, rows tagged with this
      book): files_roman.jsonl for every verified site-plan page tied to a Roman site - an
      existing catalog site by QID where one exists, or a new extras_roman.jsonl entry
      (kind "roman fort" / "roman site", QID where it exists, lon/lat from the book or a
      cross-check) - each with the 200 evidence field (list entry, caption, coordinates
      distance recorded on the row) and a classified row by hand ("plan"); the book's date
      (1793) is recorded on the row.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one is accounted for in docs/lead_roman.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.

## Hand-over
(2026-10-13, iteration 205, agent c - NO work on this task. The driver auto-put it back to
in-progress (0500b36) because its only request, 003, had been answered and closed; that is
its no-open-request safety valve, not a lift of the owner's stop and not the arrival of the
book. WAITING ON request 008 (.agent/asks/008.md, filed by this session, human_only /
outside-vm, blocking): (1) does the owner's "Stop 207" (lead block 62455ad, 10-13 11:19 -
"the owner said 'Stop 207'. Do not start until the owner lifts it.") also cover this
subtask? - my recommendation (a): it stands, consistent with the parked siblings 207a/207b
(open requests 006/007, same answer applies); and (2) the book itself: request 003 was
answered 10-11 "Use your recommendation" (= the human downloads the NLS facsimile into
data/raw/books/roy1793/) but that directory still does not exist - 008 re-asks for the
download (any layout: full PDF or page images; minimum the 51 map plates plus the page
holding the printed list of plates) or a "drop Roy" decision.) When 008 is answered:
"lifted" + book in place -> run the resume recipe below; "drop Roy" -> set Status:
dropped and record it in the Roy section of docs/lead_roman.md, per the parent's
Hand-over; "stop stands" (or the loop's default answers it) -> stays parked here.

**Why no work is possible (both verified this session; nothing to unwind):**
1. **The owner's stop.** "Stop 207" names the parent task, hence all its subtasks; the lead
   recorded it 10-13 11:19 (commit 62455ad) and blocked 207a + 207b (their requests 006/007
   are open, both recommend the stop stands). 207c was already blocked for a different
   reason when the lead wrote the block, so the commit only named the other two - it does
   not exclude this one. No lift has come through (checked inbox, lead notes, DECISIONS,
   git log through today).
2. **The book never arrived.** Request 003 (10-11, human_only) was answered "Use your
   recommendation" (console) - i.e. the human would download the NLS facsimile (https://
   maps.nls.uk/roy/antiquities/, "174 pages, 51 map plates", the only complete online
   facsimile; the Internet Archive does not hold the book - DECISIONS 10-11 attempts 1-2;
   NLS serves an AWS-WAF captcha, HTTP 405 "Human Verification", on every path from this
   VM - attempt 3; its open S3 tile bucket holds no antiquities set, only the 1747-55
   military survey already used as background maps in pipeline/nls.py) and place it in
   data/raw/books/roy1793/ - but that directory does not exist (verified this session;
   data/raw/books/ holds only a metadata.json cache for the 1917 dissertation
   macdonald-1917-roy, which is ABOUT Roy and is not the book: no facsimile pages, no
   plate list).

**Blank slate (verified this session):** no fit/src_roman_roy.py; no data/books/triage/
roy* or data/books/lists/roy*; data/commons/files_roman.jsonl, classified_roman.jsonl and
data/catalog/extras_roman.jsonl do not exist yet; docs/lead_roman.md does not exist; no
tests/test_src_roman_roy.py. Nothing to build or undo until the two blockers clear.

**Resume (ONLY when 008 is answered with a lift AND the book is in
data/raw/books/roy1793/):**
1. Read the parent 207 Hand-over "Mechanics for every subtask" (its per-book facts and
   choices are current as of 10-11) and use fit/src_roman_horsley.py (on this branch since
   10-13) as the module pattern: legs --fetch/--status/--triage A|F|B/--list, in-process
   books.BOOKS registration, lazy imports, no LLM_URLS patch needed since 215.
2. fit/src_roman_roy.py: register the book in books.BOOKS in-process (KEY=
   roy_military_antiquities_1793, year 1793, region scotland, cite from the title page).
   Its fetch leg is LOCAL (the machinery's fetch is IA-specific and the book is not on
   IA): read whatever layout arrived in data/raw/books/roy1793/ (full PDF or page images)
   and normalize it to the triage image set books.cmd_triage_a/b consume.
3. Triage A (-> data/books/triage/<key>.A.jsonl, per-book only), stage F/C if A
   under-calls, then B on the plan pages. Transcribe the printed plate list (51 entries)
   by eye from the arrived pages into the books_lists PLATES format, inject in-process,
   cmd_ocrmap -> lists/<key>.json + .map.json; record stage-A/B recall via
   books_lists.validate_book in the Roy section of docs/lead_roman.md - NEVER write the
   shared validation.json / index.jsonl (211/230 own the shared rebuild and the Roman
   re-run; 230 re-runs the consolidation once the 207 subtasks land).
4. Stage the verified site-plan rows (append-only, idempotent, every row tagged with this
   book): files_roman.jsonl (row shape per the two Stukeley rows in data/commons/files.jsonl
   + the 200 evidence field: list entry / caption / coordinates distance + checked date;
   year 1793 on every row), classified_roman.jsonl ("plan" by hand), extras_roman.jsonl
   for NEW sites only (kind "roman fort"/"roman site", QID where one exists, lon/lat from
   the book or a cross-check - mostly NEW Scottish sites; the four no-QID Antonine Wall
   camps already in extras.jsonl: bar-hill-fort, inchtuthil, raedykes, rough-castle-fort -
   tie to those where the plate matches; the catalog has no QID-carrying Scottish
   roman_fort yet).
5. tests/test_src_roman_roy.py (no network; the no_network socket-blocking fixture as in
   tests/test_src_van_deventer.py; LLM calls never in tests): offline join of the staged
   rows + fit/evidence.py check + golden sample tests/golden/src_roman_roy_sample.json.
