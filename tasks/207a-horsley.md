Status: blocked
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
- pipeline/books.py's LLM_URLS (18080/18081) are dead until 215 re-points them; the live
  replicas (model qwen3.8-27b) serve on 127.0.0.1:8080-8082. This subtask's module registers
  the book in books.BOOKS and patches books.LLM_URLS in-process only (the 213
  /tmp/civitates_triage.py pattern); it does not edit pipeline/ (parent's Hand-over has the
  full recipe).
- The catalog already holds the major British Roman forts with QIDs (305 roman_fort rows:
  206 England, 54 Wales, 22 Netherlands, 17 France, plus 6 no-QID extras: vindolanda and the
  four Antonine Wall camps, aventicum). Tie Horsley's maps to those where the site matches;
  stage a new site only for a place not already in the catalog.
- The LLM triage of 936 pages is the long pole: run it as a resumable background job (the
  stage jsonl is append-only and skips done pages; see the "long background data jobs"
  PITFALLS entry).

## Lead note (2026-10-13)
Blocked: the owner said "Stop 207". Do not start until the owner lifts it.

## Hand-over
(2026-10-13, iteration 203, agent c - the main merge brought the owner's "Stop 207" onto this
branch (it had not been visible here: my last main merge was 09:36, the lead's block landed 11:19).
The conflict is resolved by keeping the block: the owner's word is the newest on record and no
lift has come through. WAITING ON request 006 (.agent/asks/006.md, filed by this session): the
owner is asked whether "Stop 207" still stands; my recommendation is (a) it stands, and the loop
defaults to that after 120 minutes without an answer. NO work on this task until the owner lifts
the stop (006 answered "lifted", or the lead unblocks on main with the owner's word).)

**Why finished work is already on this branch (record for the owner/lead).** Iteration 202
(11:49-12:08, f6ef27d) ran on a branch that did not yet carry the 11:19 block and completed:
the book module + all 936 fetched triage pages. That is harmless finished work - a public-domain
Internet Archive scan into the shared gitignored raw store, zero failures, nothing published or
served. The expensive next step (LLM triage of all 936 pages on the shared Qwen replicas, ~1 h
of GPU) was NOT started, and this session did not start it either. Nothing to unwind; everything
is resumable from here.

**State (frozen since iteration 202).**
- `fit/src_roman_horsley.py` (KEY=horsley_britannia_romana_1732, ia=britanniaromanao00hors).
  Legs: `--fetch`, `--status`, `--triage A|F|B`, `--list` (prints front-matter hOCR until
  HORSEY_PLATES is set). NOT built yet: `--stage`/`--check`/`--golden` (raise "not built yet").
  The module top is stdlib-only; books/books_ia/books_lists import lazily.
- All 936 triage images fetched: data/raw/books/britanniaromanao00hors/triage/n0000-n0935.jpg
  (812-1400 x 1051-1401 px, median 812x1400 portrait, zero failures; log /tmp/horsley_fetch.log).
  Triage stages NOT run. LLM replicas (checked 10-13): 8080/8081 up, 8082 down; since 215
  re-pointed books.py, no in-process LLM_URLS patch is needed.
- Book facts (measured from the cached bookreader.json + hOCR pair): 936 leaves; the hOCR
  pageindex has 942 pages - SIX more than the leaves (the civitates-style misalignment, PITFALLS:
  the leaf IMAGES are the ground truth). Title page = hOCR leaf 15 (finalize CITE on resume);
  body starts i69; the printed list of plates is the hOCR-SILENT leaves i53-i68 (1732 list =
  printed pages xxv-xxxii; i63's OCR garbage is not part of the list) - transcribe BY EYE from
  the triage images in the n0047-n0070 region (the Stukeley/213 hand-list pattern). Plates are
  numbered "PL. <roman>"; ~121, mostly inscriptions/sculptures (kind o); the site plans are the
  few maps (kind s) - only those get staged.
- Catalog context (parent hand-over): data/catalog/sites.jsonl has 299 roman_fort rows, ALL with
  QID (206 england / 54 wales / 22 netherlands / 17 france); extras.jsonl carries the german Limes
  forts + 6 no-QID British extras (vindolanda, four Antonine Wall camps, aventicum).
  files_roman.jsonl / classified_roman.jsonl / extras_roman.jsonl do NOT exist yet - the first
  --stage creates them; tag every row book=horsley_britannia_romana_1732 (207b/207c append their
  own tagged rows to the same files). Row shape: the two Stukeley rows in data/commons/files.jsonl
  (site, qid, id=<ia>_n%04d[_n%04d], book, ia_id, cite, title, plate, plate_page, leaf_n, leaf_n2,
  page_type, year, wd_plan, cat, name, by, desc, evidence) + classified twin (p_plan 1.0, by hand).

**Resume ONLY when the owner lifts the stop** (006 answered "lifted", or the lead unblocks on
main with the owner's word):
1. Triage A in the background: `nohup .venv/bin/python fit/src_roman_horsley.py --triage A >
   /tmp/horsley_triageA.log 2>&1 &` (936 pages, 8080+8081 x 4 workers each; append-only, resumable;
   check `--status`). Commit the A file only when complete (the long-background-job pitfall:
   process gone + 936 rows + mtime settled) - a partial A file is fine to resume, but do not
   present it as complete.
2. While A runs: view the front-matter triage images (n0047-n0070), locate and transcribe the
   printed list of plates into HORSEY_PLATES (format plate|sub|title|page|kind; kind judged from
   the printed title - s = maps/site plans, o = inscriptions/sculptures/views, u = unsure), set
   the constant, then `--list` once stage A exists (map_plates needs A) ->
   lists/britanniaromanao00hors.json + .map.json. Also verify no specific Google-scan pages are
   unreadable (the Bim copies are the alternates for that).
3. Then: triage B on the plan pages -> stage the verified kind-s rows (--stage, append-only
   idempotent; 200 evidence field naming the list entry/caption/coordinates distance; 1732 on
   every row) into files_roman.jsonl + classified_roman.jsonl ("plan" by hand) +
   extras_roman.jsonl (new sites only, kind "roman fort"/"roman site", QID where one exists) ->
   --check (offline join + fit/evidence.py) -> --golden (tests/golden/src_roman_horsley_sample.json)
   -> tests/test_src_roman_horsley.py (no network; the test_fit_queue/no_network socket-blocking
   fixture pattern; LLM calls never in tests) -> record the stage-A/B recall against the list in
   a new Horsley section of docs/lead_roman.md via books_lists.validate_book (NEVER the shared
   validation.json/index.jsonl - 211/230 own those; 230 re-runs the Roman consolidation once the
   207 subtasks land).

**Re-read: fit/src_roman_horsley.py:list_cmd - when resuming, verify the hOCR-vs-bookreader skew
(hOCR i vs bookreader n) from the list-page images, and that i63's OCR garbage is not part of the
list. Also read the leaf-15 title page to finalize CITE (currently the IA-record title).**

**Suite baseline (iteration 203, post-merge, `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`):
1 failed, 155 passed, 1 skipped (317 s) - byte-for-byte the iteration-202 baseline; the lone red is
agent a's in-flight 307 work on main (test_fit_queue placement test, same signature: seed check +
/tiles/relief 404; owned by 235/307d, not this task). No new red from the merge (it brought no
data/, fit/ or tests/ changes). **/
