Status: in-progress
# 207b: Maclauchlan, the survey of the Roman Wall (1857-58)
Depends on: 200
Touches: fit/src_roman_maclauchlan.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_maclauchlan.py, tests/golden/src_roman_maclauchlan_sample.json

## Goal
Subtask of 207 (the parent's Hand-over has the full mechanics): index Maclauchlan's survey of
Hadrian's Wall with the existing book machinery and stage its site-plan rows tied to the
forts on the wall. The parent's task says 1857: the survey of the wall's eastern branch ran
1857-59 and the volume was published 1858 - use the year printed on the title page and note
the discrepancy in the lead doc. Chosen IA copy: `memoirwrittendu00maclgoog` (the 1858
original, Google scan, 171 leaves, median 3290x5182 px; djvu.txt only, NO hOCR page index).
Alternative for reading text/list pages: `memoirwrittendur0000henr` (1971 reprint, 292
leaves, 1625x2697 px, hOCR present) - use it to transcribe the book's list, but stage images
only from the 1858 original.
The book's plates include detailed plans of the forts on the wall (Vindolanda, Vercovicium,
etc.) alongside wall cross-sections and stretches of the wall itself. Per the parent's
Notes: wall sections are not sites and are not staged, unless a named fort/structure with a
location is in the plate.

## Acceptance criteria
- [ ] The book is fetched from the Internet Archive (data/raw/books/memoirwrittendu00maclgoog/)
      and triaged with the existing machinery, per-book artifacts only
      (triage/memoirwrittendu00maclgoog.*.jsonl, lists/memoirwrittendu00maclgoog.json,
      lists/memoirwrittendu00maclgoog.map.json); the shared data/books/index.jsonl and
      validation.json are NOT written by this subtask.
- [ ] The book's own printed list of plates is transcribed (the books_lists PLATES pattern)
      and mapped to leaves; the stage-A/B recall against that list is recorded in the
      Maclauchlan section of docs/lead_roman.md (instead of the shared validation.json).
- [ ] Staged rows (appended to the parent's shared staging files, rows tagged with this
      book): files_roman.jsonl for every verified site-plan page of a named fort/structure
      tied to a Roman site - an existing catalog site by QID where one exists, or a new
      extras_roman.jsonl entry (kind "roman fort" / "roman site", QID where it exists,
      lon/lat from the book's list or a cross-check) - each with the 200 evidence field
      (list entry, caption, coordinates distance recorded on the row) and a classified row
      by hand ("plan"); the book's date (title-page year, 1857/1858) is recorded on the row.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one (wall sections, sections alone) is
      accounted for in docs/lead_roman.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.

## Notes
- Same mechanics as 207a: in-process book registration in books.BOOKS, books.LLM_URLS
  patched to the live replicas (127.0.0.1:8080-8082) when the built-in ports are down,
  per-book triage/lists artifacts only, shared staging files tagged per book.
- Most wall forts are already in the catalog (the 206 England roman_fort rows include the
  wall forts with QIDs, e.g. vindolanda QID-less extra plus hardknott, concangis, glannoventa,
  whitley-castle, milecastles). Tie to them where the plate's site matches; stage a new site
  only for a named place not in the catalog.

## Lead note (2026-10-13)
Blocked: the owner said "Stop 207". Do not start until the owner lifts it.

## Hand-over
(2026-10-13, iteration 204, agent c - NO work on this task. The driver auto-put it back to
in-progress because no open request was registered against 207b itself; that is a mechanical
safety valve, not a lift of the owner's stop. The lead's block (62455ad, "the owner said
'Stop 207'. Do not start until the owner lifts it.") and the owner's word are the newest on
record, and no lift has come through (checked inbox, lead notes, DECISIONS). This session
filed ask_human request 007 (.agent/asks/007.md) against this task - the same question as
open request 006 (sibling 207a, 10-13 17:19 UTC), which covers both subtasks; one answer
applies to both. Status is set back to blocked, which is stable now that a request is open
against the task (driver rule: a blocked task waits while its request is open). Tests:
none run this session - no code written (task file + journal only); the suite is unchanged
at the recorded baseline 1/155/1 (the lone red is agent a's in-flight 307 placement test).)

**State (verified on this branch this session; a true blank slate, nothing to unwind).**
- No `fit/src_roman_maclauchlan.py`; no `data/books/triage/memoirwrittendu00maclgoog.*`,
  no `data/books/lists/memoirwrittendu00maclgoog.*`;
  `data/commons/files_roman.jsonl`, `classified_roman.jsonl` and
  `data/catalog/extras_roman.jsonl` do not exist yet; `docs/lead_roman.md` does not exist.
- `data/raw/books/` holds only cached `bookreader.json` + `metadata.json` for BOTH IA copies:
  `memoirwrittendu00maclgoog` (1858 original, 171 leaves, djvu.txt only, no hOCR) and
  `memoirwrittendur0000henr` (1971 reprint, 292 leaves, hOCR present). No triage images
  fetched for either; no LLM minutes spent.
- Waiting on: request 007 (this task) and 006 (207a), both open, both recommend (a) the stop
  stands; the loop's 120-minute default answers (a) if the human never replies, and the task
  stays parked on the lead note.

**Resume recipe (start ONLY after the owner's lift - a 007/006 answer of "lifted", or the
lead unblocking on main with the owner's word; read the parent 207 Hand-over's "Mechanics for
every subtask" first; its numbers/IA choices are current).**
1. Confirm the lift, then delete/rewrite this hand-over's waiting text.
2. `fit/src_roman_maclauchlan.py`: register the book in `books.BOOKS` in-process (ia=
   memoirwrittendu00maclgoog, region england, year = the title-page year, cite/why). No
   in-process `books.LLM_URLS` patch needed since 215 (207a session, 10-13: replicas
   8080/8081 up, 8082 down).
3. Fetch: `books.cmd_fetch([key])` -> `data/raw/books/memoirwrittendu00maclgoog/triage/`
   (171 pages, IIIF 1400px, append-only/resumable; long background job, see the PITFALLS
   "long background data jobs" entry).
4. Printed plate list: transcribe from the 1971 reprint's hOCR (memoirwrittendur0000henr),
   cross-check against the 1858 original's list-page images; inject `books_lists.PLATES[ia]`
   in-process; `books_lists.cmd_ocrmap([key])` -> `lists/*.json` + `.map.json` (per-book,
   committed); `books_lists.validate_book(key)` recall recorded in the Maclauchlan section of
   `docs/lead_roman.md` - do NOT write the shared validation.json / index.jsonl (211/230
   own the shared rebuild and the Roman re-run).
5. Triage A/B on the 1858 original; stage ONLY site-plan pages of a named fort/structure
   with a location (wall sections alone are NOT sites, per the parent Notes); stage images
   from the 1858 original only. Rows -> `files_roman.jsonl` (200 evidence field: list entry
   / caption / distance specifics, checked date) + `classified_roman.jsonl` ("plan" by
   hand), book date on the row; new sites -> `extras_roman.jsonl` (kind "roman fort",
   QID where it exists - most wall forts already carry QIDs in the 206 England roman_fort
   rows: hardknott, concangis, glannoventa, whitley-castle, milecastles; vindolanda is the
   known QID-less extra - lon/lat from the book's list or a cross-check).
6. `tests/test_src_roman_maclauchlan.py` (no network; the no_network socket-blocking
   fixture as in test_src_van_deventer.py; offline join of staged rows + fit/evidence.py
   check + golden sample `tests/golden/src_roman_maclauchlan_sample.json`).
7. Date note: the survey ran 1857-59 and the volume published 1858 - record the title-page
   year on the rows and note the discrepancy in `docs/lead_roman.md`.
