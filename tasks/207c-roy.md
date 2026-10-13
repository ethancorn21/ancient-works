Status: dropped
# 207c: Roy, Military Antiquities of the Romans in North Britain (1793)
Depends on: 200
Touches: fit/src_roman_roy.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_roy.py, tests/golden/src_roman_roy_sample.json, PLAN.md, tasks/207-roman-books.md

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

(2026-10-13, iteration 214, agent c - FINAL session: task DROPPED on the owner's answer to
ask_human 008. No work was ever done on this task (the blank slate below); this is the
record of its end state, in the 209a pattern.)

**What happened.** The owner answered request 008 (filed by iteration 205: (1) does the
owner's "Stop 207" cover this subtask, (2) the NLS facsimile into data/raw/books/roy1793/ or
a drop decision) on 2026-10-13 14:36 (console): "drop Roy. I dont want to have to ever go
out and get a file. If you need it get it. If you can't get it, then you don't need it." It
is the same standing refusal recorded in PITFALLS ("The human will not download books for
this project", the 001/002 Hoare/Petrie refusals - that entry even predicted this outcome
for this task). The "get it" leg addresses the loop, so this session re-verified it for
this book before dropping: (1) NLS maps.nls.uk/roy/antiquities/ -> HTTP 405 AWS-WAF
"Human Verification" again (browser UA, today; first checked 10-11); (2) NLS S3
mapseries-tilesets -> roy/ still 1747-55 military-survey tiles only, no antiquities set;
(3) Google Books API -> HTTP 429, anonymous consumer quota 0 queries/day
(quota_limit_value: 0 - a hard refusal, the same wall the Wiltshire lead hit for Hoare on
10-12/13); IA has been exhaustively empty since 10-11 (attempts 1-2: title phrases,
creator, year range, ten identifier patterns). The book is unobtainable from this VM by
any known source, and the owner says it is not needed: **207c is DROPPED**. No re-ask will
ever be filed (PITFALLS standing rule); the record is in docs/lead_roman.md's Roy section.

**State left behind.** None - the iteration-205 blank slate stands: no fit/src_roman_roy.py,
no per-book artifacts (data/books/ has no roy rows), no staging rows (data/commons/ has no
*_roman.jsonl files at all yet - 207a/207b create them when they stage), no test, no
data/raw/books/roy1793/. Nothing to unwind. No code was changed in any 207c session, so no
tests ran in this session either; the newest full-suite measurement on record (307d, this
day, agent a's checkout: 159 passed, 1 skipped, 1 failed - the pre-existing 235 red)
stands. The catalog's four no-QID Antonine Wall camps (bar-hill-fort, inchtuthil,
raedykes, rough-castle-fort in extras.jsonl) are untouched and stay catalog-only: Roy's 51
plates were the only planned source of early Scottish camp plans, so no such plans enter
the map from this book, and no new Scottish roman_fort rows will be staged by this task.

**What changed this session (all of it).** tasks/207c-roy.md (Status: dropped + this
record; the Touches line gained PLAN.md and tasks/207-roman-books.md, the only two files
beyond the original list that the drop record needed); docs/lead_roman.md created with the
Roy section (source, the owner's answer, recall n/a, the effect on the lead - note the
file is 207a/207b's too, so its header carries a layout note for their sections); the
parent's (207) hand-over updated in place (dated update line, State paragraph, and
exact-next-steps item 3, which now holds the full resume recipe); PLAN.md (point-5 row,
module-map cell, new Deviations entry); PITFALLS (the two book-source entries corrected to
this outcome); DECISIONS (this entry's header block).

**If this task is ever reopened** (a complete scan of the book - any layout, full PDF or
page images - lands in data/raw/books/roy1793/): resume per the parent's (207) hand-over,
"Mechanics for every subtask" plus its exact-next-steps item 3 (the local-file fetch leg
on the Wiltshire-Hoare 3-point in-process wrap, triage A/B, the printed 51-plate list
transcribed by eye from the arrived pages, recall in the lead doc, rows tagged with this
book, tests, golden). The parent's hand-over keeps that recipe; it is the single source of
truth, so it is not restated here.
