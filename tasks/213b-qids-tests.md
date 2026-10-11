Status: open
# 213b: The seven verified town QIDs, the golden sample and the test - the lead doc final
Depends on: 213a
Touches: fit/src_artists.py, docs/lead_artists.md, tests/test_src_artists.py, tests/golden/src_artists_sample.json

## Goal
Finish 213's remaining work. (1) The seven hand-verified towns of Liber secundus (Rome, Vienna,
Florence, Milan, Venice, Brussels, Antwerp) go into `fit/src_artists.py:BOOKS["civitates"]["sites"]`
as a hand-checked QID table - paced Wikidata per town (the label, every P625 value flagged when
>50 km off, P373, P131, enwiki, and the first name-search hit with coordinates - the search-trap
check that caught Venice, California for Venice); the checked date, coordinates and traps are
recorded in docs/lead_artists.md (216 takes its cite strings from there; 217 takes these QIDs to
match the book-index rows to the catalog). (2) `.venv/bin/python fit/src_artists.py --check`
passes (exit 0, no join problems, 2/2 PASS caption_coords) and `--golden` regenerates
`tests/golden/src_artists_sample.json` (only for an intended change; never hand-edited).
(3) `tests/test_src_artists.py` per the prep §4 (tasks/prep/213.md): the join over the staged files
(every file row names a staged or existing site; no staged id or QID pre-exists; every staged site
has a picture; (site,title) unique; no clash with the canonical files.jsonl; classified rows 1:1),
the table completeness (SITES + the BOOKS towns), the offline evidence check (import
fit/evidence.py, exit 0, zero FAIL, every staged row PASS caption_coords) plus the negative control
(the Imola row with the Cervia point 44.245/12.367 is reported FAIL, never written), and the golden
comparison; a socket-blocking fixture makes any network fetch fail loud; run under
.venv/bin/python (the system python3 has no numpy). (4) The lead doc is complete (box 1): for each
source what it is, where its files live (URLs, category names, IA identifiers), the drawing's date
(the upload-only cases noted), exactly which files are staged, and every documented drop with its
reason.

## Acceptance criteria
- [ ] `BOOKS["civitates"]["sites"]`: seven towns, each {qid, name, lon, lat, place, wikipedia,
      cat}, no name-search-only QID; docs/lead_artists.md records the checked date, the P625 values
      and the search-trap notes for each.
- [ ] `.venv/bin/python fit/src_artists.py --check`: exit 0, no join problems, 2/2 PASS.
- [ ] `.venv/bin/python fit/src_artists.py --golden` regenerates tests/golden/src_artists_sample.json
      only for an intended change; the test compares the staged rows against it (keys sorted,
      checked/date_commons normalized).
- [ ] tests/test_src_artists.py passes under `.venv/bin/python` with no network (the
      socket-blocking fixture), including the negative control; the full pytest suite stays green.
- [ ] docs/lead_artists.md is complete for all four sources (box 1): 213a's books section plus the
      QID-table section; every staged file, every documented drop, every date.

## Notes
- The staged files (extras/files/classified_artists.jsonl) are append-only and final (boxes 2/3):
  do not re-stage; stage() is idempotent on (site, title) if it must ever run again - expect it to
  stage nothing.
- After this task the parent 213 comes back: its session verifies --check/test/golden/lead doc,
  ticks the parent's boxes 1, 5, 6 and then box 4 (the count check) LAST, writes the R6 note in
  211's ## Hand-over (the *_artists* staging files + the civitates per-book files must be merged
  into the canonical ones), and sets the parent done.
