Status: split
# 207: Roman sites - Roy (1793), Horsley (1732), Maclauchlan (1857)
Depends on: 200
Touches: fit/src_roman_horsley.py, fit/src_roman_maclauchlan.py, fit/src_roman_roy.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_horsley.py, tests/test_src_roman_maclauchlan.py, tests/test_src_roman_roy.py, tests/golden/

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
(2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
work that every subtask reads. Order was deliberately changed from the Notes: a = Horsley
(first unblocked and the biggest), b = Maclauchlan, c = Roy (blocked, waiting on a
human-provided copy).)

(2026-10-13, iteration 214, agent c - 207c DROPPED on the owner's answer to ask 008 ("drop
Roy"); the State paragraph and exact-next-steps item 3 below are updated to that; everything
else stands as written.)

**Tests:** none run this session (an investigation/split session - no code written; the last
suite state is the 50 passed recorded in 204's hand-over in PROGRESS). 207a's first session
re-baselines the suite, then starts the fetch.

**State.** (updated 2026-10-13, iteration 214) 207a in progress (stage A complete; the
printed plate-list transcription is next), 207b in progress, 207c DROPPED: the owner's answer
to ask 008 (2026-10-13 14:36, console) was "drop Roy. I dont want to have to ever go out and
get a file. If you need it get it. If you can't get it, then you don't need it." - the book
is unobtainable from this VM (NLS WAF 405, no IA copy, HathiTrust 403, Google Books quota 0;
all re-verified that day) and the owner declined to supply it (the standing refusal of
209a/209c). The record is in docs/lead_roman.md's Roy section and 207c's own hand-over; if a
complete scan ever lands in data/raw/books/roy1793/ the subtask resumes per
exact-next-steps item 3. The parent's boxes 1-4 stand on the two remaining books.

### Per-book facts (measured this session, via books_ia + IA searches)
- **Horsley** -> ia=`britanniaromanao00hors` (Google Books, 936 leaves, median 2237x3861 px,
  hOCR + djvu.txt). Alternatives: `bim_eighteenth-century_britannia-romana-or-the_horsley-john_1732`
  (831 leaves, 7984x13809) and `..._0` (827, 8328x14257) - far larger images. The ~121
  engraved plates are mostly inscriptions/sculptures (kind o); the site plans are the few
  maps.
- **Maclauchlan** -> ia=`memoirwrittendu00maclgoog` (the 1858 original, Google, 171 leaves,
  3290x5182, djvu.txt only, no hOCR); for list-page OCR use the 1971 reprint
  `memoirwrittendur0000henr` (292 leaves, 1625x2697, hOCR). Detailed fort plans; wall
  sections are not sites (parent Notes).
- **Roy** -> NOT on IA (see 207c). NLS holds the complete facsimile (174 pp + 51 map plates)
  but maps.nls.uk is WAF-blocked from this VM; the NLS S3 tile bucket has no antiquities
  set. The 1917 dissertation `macdonald-1917-roy` on IA is not the book.

### Mechanics for every subtask (the book machinery without editing pipeline/)
- In-process registration in the module: `books.BOOKS[key] = dict(ia=..., region=..., year=...,
  cite=..., why=...)` and, when the built-in ports are down, `books.LLM_URLS = [127.0.0.1:8080,
  :8081, :8082]/v1/chat/completions` (live, model qwen3.8-27b, verified up this session;
  the 213 /tmp/civitates_triage.py pattern; 215 re-points books.py properly). Do not edit
  pipeline/ files - they are owned by other tasks.
- `books.cmd_fetch([key])` -> data/raw/books/<ia>/triage/ (gitignored raw, resumable).
  `books.cmd_triage_a([key])` -> data/books/triage/<ia>.A.jsonl (per-book, committed); then
  stage F (figure pages) and/or clef C if A under-calls; `books.cmd_triage_b([key])` ->
  <ia>.B.jsonl (runs on A's site pages + the map's site_plan pages).
- List mapping: transcribe the printed plate list (books_lists PLATES string format
  `plate||title[|sub]|page|kind`), inject it in-process as `books_lists.PLATES[ia]`, then
  `books_lists.cmd_ocrmap([key])` writes lists/<ia>.json and lists/<ia>.map.json (per-book,
  committed). Recall/precision: call `books_lists.validate_book(key)` and record the numbers
  in docs/lead_roman.md's book section - do NOT write the shared validation.json or
  index.jsonl (211 rebuilds the shared index from the per-book files once; its hand-over
  says the *_roman staging is consolidated by it).
- Staging (append-only, idempotent, the 204/205 pattern): all three subtasks append to the
  parent's shared staging files, each row tagged with its book: data/commons/files_roman.jsonl
  (row shape follows data/commons/files.jsonl; the 200 evidence field: kind
  caption_coords/hand_tied with the list entry / caption / distance specifics + checked
  date), data/commons/classified_roman.jsonl ("plan" by hand), data/catalog/extras_roman.jsonl
  (new sites only: kind "roman fort"/"roman site", QID where it exists, lon/lat, region in the
  catalog's lowercase convention - scotland for Roy, england for the rest; NOTE the extras.jsonl
  rows use capitalized regions and sites.jsonl lowercase - 211 normalizes).
- Catalog context for tying: 305 roman_fort rows exist (301 with QID: 206 England, 54 Wales,
  22 Netherlands, 17 France in sites.jsonl; 6 no-QID extras: vindolanda + four Antonine Wall
  camps + aventicum). Horsley/Maclauchlan mostly tie to existing QIDs; Roy mostly creates
  new Scottish sites.
- Tests (no network): offline join + fit/evidence.py check over the staged rows + a golden
  sample (tests/golden/src_roman_<book>_sample.json); the no_network socket-blocking fixture
  as in test_src_van_deventer.py. LLM calls never run in tests.

### Exact next steps (per subtask)
1. **207a (Horsley):** fetch britanniaromanao00hors triage pages -> triageA (936 pages: long
   pole, run resumable in the background) -> transcribe the printed list of plates (hOCR
   page text, verify against the list-page images) -> cmd_ocrmap -> validate_book recall in
   the lead doc -> triageB on the plan pages -> stage rows -> check -> tests -> golden.
2. **207b (Maclauchlan):** same; the 1858 original has no hOCR, so transcribe its list from
   the 1971 reprint's OCR (memoirwrittendur0000henr) and cross-check against the original's
   list-page image; stage images from the 1858 original only.
3. **207c (Roy):** DROPPED 2026-10-13 (owner, ask 008 - see the State above and
   docs/lead_roman.md). If a complete copy ever lands in data/raw/books/roy1793/ (any
   layout: full PDF or page images): adapt the fetch to the local files (the Wiltshire-Hoare
   3-point in-process wrap: books_ia.pages / books_ia.page_texts / books.fetch_triage for
   this id only, re-encoded into the books.triage_path slots), then the same pipeline;
   transcribe the book's printed 51-plate list by eye from the arrived pages (no OCR text
   for the book exists in any accessible copy); rows tagged with this book (region
   scotland, year 1793), mostly NEW Scottish fort sites in extras_roman.jsonl - tie to the
   four no-QID Antonine Wall camps (bar-hill-fort, inchtuthil, raedykes, rough-castle-fort)
   where a plate matches; stage-A/B recall in the Roy section of docs/lead_roman.md; tests +
   golden as for the other books.
