Status: blocked
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

## BLOCKED (2026-10-11, iteration 63): the book is not on the Internet Archive
Searched IA: advancedsearch by exact title, by creator, full-text phrases, a 1790-1800 year
range, and ten guessed identifier patterns (militaryantiquit00roy*) - no hit. The only IA
item is a 1917 dissertation ABOUT Roy (macdonald-1917-roy, ~76 leaves, journal pagination
161-228): not the book (no facsimile pages, no plate list) and not a substitute.
The only complete online facsimile is the National Library of Scotland
(https://maps.nls.uk/roy/antiquities/ - "174 pages, 51 map plates", a complete electronic
facsimile), but maps.nls.uk serves an AWS-WAF captcha challenge (HTTP 405 "Human
Verification") on every path from this VM (HTML, guessed image URLs, several UAs); NLS's
open S3 tile bucket (mapseries-tilesets) does not hold this book's plates (only the 1747-55
military-survey roy/lowlands + roy/highlands, which pipeline/nls.py already uses as a
background map). A real browser must pass the WAF - the open ask_human request asks the
human to provide the copy.

## Waiting on
A human-provided copy placed in data/raw/books/roy1793/ (gitignored raw; any layout: full
page images or the book's PDF - the 51 plates plus the printed list of plates are the
minimum). When it arrives: adapt fetch to the local files (the machinery's fetch is
IA-specific), then run the same pipeline as 207a/207b (the parent's Hand-over has the
recipe). Until then: do not build stand-ins.

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
