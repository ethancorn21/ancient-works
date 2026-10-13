Status: in-progress
# 207a: Horsley, Britannia Romana (1732)
Depends on: 200
Touches: fit/src_roman_horsley.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_horsley.py, tests/golden/src_roman_horsley_sample.json

## Goal
Subtask of 207 (the parent's Hand-over has the full mechanics): index John Horsley's
*Britannia Romana* (1732) with the existing book machinery and stage its site-plan rows tied
to Roman sites. Chosen IA copy: `britanniaromanao00hors` (Google Books scan, 936 leaves,
median 2237x3861 px, hOCR page text + djvu.txt present). Alternatives (only if specific pages
of the Google copy are unreadable): `bim_eighteenth-century_britannia-romana-or-the_horsley-john_1732`
(British Museum, 831 leaves, median 7984x13809 px) and the `..._0` copy (827 leaves,
8328x14257 px) - much larger images.
Note: this book's ~121 engraved plates are mostly Roman inscriptions and sculptures (list
kind "o"); its true site plans are the few maps (kind "s"). Stage the site plans; the
inscription plates are indexed in the list mapping (each names the site where the stone was
found) but are not staged as picture rows.

## Acceptance criteria
- [ ] The book is fetched from the Internet Archive (data/raw/books/britanniaromanao00hors/)
      and triaged with the existing machinery, per-book artifacts only
      (triage/britanniaromanao00hors.*.jsonl, lists/britanniaromanao00hors.json,
      lists/britanniaromanao00hors.map.json); the shared data/books/index.jsonl and
      validation.json are NOT written by this subtask.
- [ ] The book's own printed list of plates is transcribed (the books_lists PLATES pattern)
      and mapped to leaves; the stage-A/B recall against that list is recorded in the
      Horsley section of docs/lead_roman.md (instead of the shared validation.json).
- [ ] Staged rows (appended to the parent's shared staging files, rows tagged with this
      book): files_roman.jsonl for every verified site-plan page tied to a Roman site - an
      existing catalog site by QID where one exists, or a new extras_roman.jsonl entry
      (kind "roman fort" / "roman site", QID where it exists, lon/lat from the book's list
      or a cross-check) - each with the 200 evidence field (the book's printed list names
      the place; the specific check - list entry, caption, coordinates distance - recorded
      on the row) and a classified row by hand ("plan"); the book's date (1732) is recorded
      on the row.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one is accounted for in docs/lead_roman.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.

## Notes
- The LLM replicas serve on 127.0.0.1:8080-8082 (model qwen3.8-27b); since 215 re-pointed
  pipeline/books.py's LLM_PORTS to 8080,8081,8082,18080,18081, no in-process LLM_URLS patch is
  needed (verified 10-13: 8080/8081 answer, 8082 down). This subtask's module registers the
  book in books.BOOKS in-process only; it does not edit pipeline/ (the parent's Hand-over has
  the full recipe).
- The catalog already holds the major British Roman forts with QIDs (305 roman_fort rows:
  206 England, 54 Wales, 22 Netherlands, 17 France, plus 6 no-QID extras: vindolanda and the
  four Antonine Wall camps, aventicum). Tie Horsley's maps to those where the site matches;
  stage a new site only for a place not already in the catalog.
- The LLM triage of 936 pages is the long pole: run it as a resumable background job (the
  stage jsonl is append-only and skips done pages; see the "long background data jobs"
  PITFALLS entry).

## Hand-over
(2026-10-13, iteration 212, agent c - the owner LIFTED the stop: request 006 (filed by iteration
203) was answered "b" on 10-13; the driver resumed all three 207 subtasks on that answer
(commits 84a7897/d959afe/7457317 flipped only the Status lines). The old "## Lead note" block
("Stop 207 ... Do not start until the owner lifts it") is removed here: it no longer stands -
the owner's answer is the newest word on record. This session = resume-recipe step 1: stage-A
triage ran to completion and its file is committed. Nothing else (one step): no code changes,
suite not re-run (last baseline is iteration 203's 1 failed / 155 passed / 1 skipped; the lone
red is agent a's in-flight 307 placement test, not this task).)

**Stage A: COMPLETE and committed this session.** Ran 14:38-14:55 (17 min: 8080+8081 live, x 4
workers each = 8 concurrent; the old "~1 h" estimate assumed a busier GPU; 8082 still down).
`data/books/triage/britanniaromanao00hors.A.jsonl`: 936/936 rows, 0 error rows; writer process
gone + mtime settled before commit (the long-background-job PITFALLS check; log
/tmp/horsley_triageA.log). Page types: text_only 703, other_illustration 151, plate_site_plan 80,
unparsed 2 (n349 and n391 - markdown-fenced JSON the parser dropped; both look like plate/LIST
pages, not plans). **DO NOT TRUST A's captions/numbers on this book**: Qwen's parametric memory
leaked in - most "plate_site_plan" captions are Squier & Davis hallucinations ("MAP OF THE
VALLEY OF THE CHAMBERLAIN RIVER, ILLINOIS", "MOUND CITY, OHIO", "HERCULANEUM, CAMP OF CAESAR",
"DELAVAR"; "PLATE XXV" repeated verbatim on unrelated pages). The genuinely plausible cluster:
n236-n287 = the Roman-wall maps ("A general map of the Roman walls in the north of England"
N.1-N.8, "A general map of Antoninus Pius's wall in Scotland" N.1-N.2, "A map of the Roman wall
in Scotland ... to Bemulie / to Crowy-hill / to Falkirk / to the east end"). Kind decisions come
from the printed plate list (transcribed by eye) + the triage images, never from A's text.

**Next session - recipe step 2: transcribe the printed list of plates (independent of A, done):**
1. `--status` (offline sanity: leaf count, A line count, which LLM ports answer).
2. View triage images data/raw/books/britanniaromanao00hors/triage/n0047-n0070 (the hOCR-silent
   i53-i68 = printed pages xxv-xxxii; i63's OCR garbage is NOT part of the list; the hOCR
   pageindex is 6 pages skewed against the 936 leaves - the leaf images are the ground truth).
   Transcribe the list into the module's HORSEY_PLATES (format plate|sub|title|page|kind; kind
   judged from the printed title: s = maps/site plans, o = inscriptions/sculptures/views,
   u = unsure) and commit the module; then `--list` once -> lists/britanniaromanao00hors.json +
   .map.json (the map fills from A + the list). Also: read the leaf-15 title-page image to
   finalize CITE (Re-read below), and confirm no Google-scan pages are unreadable (the Bim
   copies are alternates only for that case).
3. Then: `--triage B` (resumable; covers A's site pages + the list's kind-s extras - re-run it
   after ocrmap, it picks up the mapping's new pages), and build the `--stage`/`--check`/
   `--golden` legs (they raise "not built yet"): stage the VERIFIED kind-s rows - book date
   1732 on every row, the 200 evidence field naming the check (list entry / caption /
   coordinates distance) - into data/commons/files_roman.jsonl + classified_roman.jsonl ("plan",
   p_plan 1.0, by hand) + extras_roman.jsonl (new sites only: kind "roman fort"/"roman site",
   QID where one exists - the catalog's 299 roman_fort rows all have QIDs, so most plans tie to
   existing sites). -> --check (offline join + fit/evidence.py) -> --golden ->
   tests/test_src_roman_horsley.py (no network: the no_network socket-blocking fixture pattern;
   LLM never in tests) -> stage-A/B recall against the list via books_lists.validate_book
   recorded in a new Horsley section of docs/lead_roman.md (NEVER the shared
   validation.json/index.jsonl - 211/230 own those; 230 re-runs the Roman consolidation once the
   207 subtasks land). Row shape: the two Stukeley rows in data/commons/files.jsonl (site, qid,
   id=<ia>_n%04d, book, ia_id, cite, title, plate, plate_page, leaf_n, leaf_n2, page_type, year,
   wd_plan, cat, name, by, desc, evidence) + classified twin.

**Module state (unchanged this session):** fit/src_roman_horsley.py (KEY=horsley_britannia_romana_1732,
ia=britanniaromanao00hors): --fetch/--status/--triage A|F|B/--list all work; HORSEY_PLATES=None
(step 2 above); --stage/--check/--golden raise "not built yet". No books.py LLM patch needed
(215 re-pointed LLM_PORTS to 8080,8081,8082,18080,18081; run_stage uses whichever answer - here
8080/8081).

**Re-read: fit/src_roman_horsley.py:list_cmd - when transcribing, verify the hOCR-vs-bookreader
skew (hOCR i vs bookreader n) from the list-page images, and that i63's OCR garbage is not part
of the list. Also read the leaf-15 title page to finalize CITE (currently the IA-record title).

**Stage-A recall preview (for step 2's cross-check, not evidence):** of the 80 plate_site_plan
candidates the Roman-wall map cluster n236-n287 is the only one that looks Horsley-true; the
remaining candidates scatter across the book (n60-n65, n112-n115, n184-n187, n234-n257, n278-
n287, n319-n515, n732-n735, n833) mostly with hallucinated captions - the list transcription
decides which of them are kind s.**/
