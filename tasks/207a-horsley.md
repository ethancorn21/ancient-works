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

## Hand-over
(2026-10-13, iteration 202, agent c - FIRST session. Module created, all 936 triage images fetched
and verified. Next session: start triage A in the background, transcribe the plate list while it runs.)

**Suite baseline** (this session, `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`, 312 s):
1 failed, 155 passed, 1 skipped. The lone failure = agent a's in-flight 307 work on main
(test_fit_queue.py::test_placement_gestures_and_save_in_the_browser; same signature as 306d's 161/201
records: "seed: the gestures own the mouse..." + /tiles/relief 404). No new red from my changes.

**State.**
- `fit/src_roman_horsley.py` exists (KEY=horsley_britannia_romana_1732, ia=britanniaromanao00hors).
  Built legs: `--fetch`, `--status`, `--triage A|F|B`, `--list` (prints front-matter hOCR until
  HORSEY_PLATES is set). NOT built yet: `--stage`/`--check`/`--golden` (raise "not built yet").
  The module top is stdlib-only; books/books_ia/books_lists import lazily.
- All 936 triage images fetched and verified: data/raw/books/britanniaromanao00hors/triage/n0000-n0935.jpg,
  every one 812-1400 x 1051-1401 px (median 812x1400 portrait), zero failures, the fetch process is gone
  (log /tmp/horsley_fetch.log). data/raw is the shared symlinked store (PITFALLS line 170/230).
- Triage stages NOT run yet. LLM replicas checked this session: 8080 and 8081 up, 8082 down; books.LLM_URLS'
  default port list (215 re-pointed books.py) covers the live ones, so NO in-process LLM_URLS patch is
  needed - the parent's "patch LLM_URLS" mechanics note is stale on that point.

**Book facts (measured this session from the cached bookreader.json + the hOCR pair, both now local):**
- 936 bookreader leaves (long side 2576-4116 px; 5 landscape). The hOCR pageindex has 942 pages - SIX more
  than the leaves - the civitates-style misalignment (PITFALLS): text looked up by page index can land on
  the wrong leaf; the leaf IMAGES are the ground truth. Verify the exact skew when you first view images.
- Title page = hOCR leaf 15 (full title + "In three books"); dedication/preface i16-i52 (preface ends on
  printed page xxxii, i52); the body starts i69 ("BOOK THE FIRST").
- **The printed list of plates is the hOCR-SILENT leaves i53-i68** (16 leaves between preface and body; zero
  hOCR text except garbage on i63). Read it BY EYE from the triage images - the Stukeley/213 hand-list pattern.
  These are hOCR indices; in bookreader n they sit in the same front-matter region (locate visually among
  n0047-n0070). The 1732 list runs printed pages xxv-xxxii (~8 pages), so only part of i53-i68 is list -
  the rest may be blank leaves or early plates; confirm visually.
- Plates are numbered "PL. <roman numeral>"; the ~121 plates are mostly inscriptions/sculptures (kind o),
  the site plans are the few maps (kind s) - only those get staged.

**Catalog context for the later tie work:** data/catalog/sites.jsonl has 299 roman_fort rows, ALL with QID
(206 england, 54 wales, 22 netherlands, 17 france). extras.jsonl carries ~45 german Limes forts (kind
"roman fort", region "Germany" capitalized - the parent's hand-over says extras rows use capitalized
regions and 211 normalizes). files_roman.jsonl / classified_roman.jsonl / extras_roman.jsonl do NOT exist
yet - the first --stage creates them; tag every row book=horsley_britannia_romana_1732 (207b/207c append
their own tagged rows to the same files). The canonical book-row shape to follow: the two Stukeley rows in
data/commons/files.jsonl (site, qid, id=<ia>_n%04d[_n%04d], book, ia_id, cite, title, plate, plate_page,
leaf_n, leaf_n2, page_type, year, wd_plan, cat, name, by, desc, evidence) and their classified twin
(p_plan 1.0, by hand).

**Re-read: fit/src_roman_horsley.py:list_cmd - when transcribing the list, verify the hOCR-vs-bookreader
skew (hOCR i vs bookreader n) from the list-page images, and that i63's OCR garbage is not part of the
list. Also read the leaf-15 title page to finalize CITE (currently the IA-record title).**

**Exact next steps.**
1. Start triage A in the background: `nohup .venv/bin/python fit/src_roman_horsley.py --triage A >
   /tmp/horsley_triageA.log 2>&1 &` (936 pages, 8080+8081 x 4 workers each; append-only, resumable;
   check `--status`). Commit the A file only when complete (the long-background-job pitfall: process gone
   + 936 rows + mtime settled) - a partial A file is fine to resume, but don't present it as complete.
2. While A runs: view the front-matter triage images (n0047-n0070 region), locate and transcribe the
   printed list of plates into HORSEY_PLATES (format plate|sub|title|page|kind; kind judged from the
   printed title - s = maps/site plans, o = inscriptions/sculptures/views, u = unsure), set the constant,
   then `--list` once stage A exists (map_plates needs A) -> lists/britanniaromanao00hors.json + .map.json.
   Also verify no specific Google-scan pages are unreadable (the Bim copies are the alternates for that).
3. Then: triage B on the plan pages -> stage the verified kind-s rows (--stage, append-only idempotent,
   200 evidence field naming the list entry/caption/coordinates distance, 1732 on every row) into
   files_roman.jsonl + classified_roman.jsonl + extras_roman.jsonl (new sites only, kind
   "roman fort"/"roman site", QID where one exists) -> --check (offline join + fit/evidence.py) ->
   --golden (tests/golden/src_roman_horsley_sample.json) -> tests/test_src_roman_horsley.py (no-network,
   the test_fit_queue/no_network socket-blocking fixture pattern; LLM calls never in tests) -> record the
   stage-A/B recall against the list in a new Horsley section of docs/lead_roman.md via
   books_lists.validate_book (NEVER the shared validation.json/index.jsonl - 211 rebuilds those).
