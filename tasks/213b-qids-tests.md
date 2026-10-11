Status: done
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
- [x] `BOOKS["civitates"]["sites"]`: seven towns, each {qid, name, lon, lat, place, wikipedia,
      cat}, no name-search-only QID; docs/lead_artists.md records the checked date, the P625 values
      and the search-trap notes for each.
- [x] `.venv/bin/python fit/src_artists.py --check`: exit 0, no join problems, 2/2 PASS.
- [x] `.venv/bin/python fit/src_artists.py --golden` regenerates tests/golden/src_artists_sample.json
      only for an intended change; the test compares the staged rows against it (keys sorted,
      checked/date_commons normalized).
- [x] tests/test_src_artists.py passes under `.venv/bin/python` with no network (the
      socket-blocking fixture), including the negative control; the full pytest suite stays green.
- [x] docs/lead_artists.md is complete for all four sources (box 1): 213a's books section plus the
      QID-table section; every staged file, every documented drop, every date.

## Notes
- The staged files (extras/files/classified_artists.jsonl) are append-only and final (boxes 2/3):
  do not re-stage; stage() is idempotent on (site, title) if it must ever run again - expect it to
  stage nothing.
- After this task the parent 213 comes back: its session verifies --check/test/golden/lead doc,
  ticks the parent's boxes 1, 5, 6 and then box 4 (the count check) LAST, writes the R6 note in
  211's ## Hand-over (the *_artists* staging files + the civitates per-book files must be merged
  into the canonical ones), and sets the parent done.

## Hand-over
**Iteration 38 (2026-10-11): 213b DONE - all five boxes ticked, Status: done.** Item (1) landed in
iteration 37 (the seven book-town QIDs in `BOOKS["civitates"]["sites"]`, --verify clean, lead-doc QID
section; the driver committed that work). This session: box 2 (--check re-run), box 3 (--golden first
write), box 4 (tests/test_src_artists.py), box 5 (lead-doc final read). Everything is committed in this
session's commit; the parent 213 picks up next.

**What was done (all verified by running):**
- **Box 2:** `.venv/bin/python fit/src_artists.py --check` re-run today: exit 0, no join problems,
  `evidence: 2 rows, 2 pass, 0 fail, 0 no-tie` (both rows PASS caption_coords).
- **Box 3:** `tests/golden/src_artists_sample.json` created by ONE `--golden` run (it did not exist;
  the staging files are final, so this was the intended first write - never hand-edit afterwards).
  `_norm` normalized two `"checked"` fields to `0000-00-00` (one per files-row evidence field; neither
  files row has a `date_commons` - Imola's file page has no DateTimeOriginal, Venice's date sits in
  `date`).
- **Box 4:** `tests/test_src_artists.py` - 4 tests, all offline. Autouse `no_network` fixture
  (module-scoped: monkeypatches `socket.socket`/`create_connection`/`getaddrinfo` to raise
  AssertionError, so any fetch in this file's tests fails loud; no conftest.py edit - 000 owns it, and
  the module scope leaves test_serve's ephemeral-port server untouched):
  (1) `test_check_staged_files_join_and_pass` - calls `src_artists.check_staged()` (the same function
  the `--check` branch runs) -> 0, no "join:" lines, the 2/2 PASS summary, both PASS lines;
  (2) `test_qid_table_and_staged_rows` - `table_sites()` = the 8 expected QIDs, the book towns in
  plate order (Q239/Q12892/Q1741/Q490/Q641/Q2044/Q220), every table entry complete
  (name/lon/lat/place/wikipedia/cat), extras rows complete + matching SITES, file rows = the SOURCES
  titles with the known drawing dates 1502/1500;
  (3) `test_evidence_offline_and_negative_control` - `evidence.check(FILES_ARTISTS, NO_BOOKS,
  catalog=EXTRAS_ARTISTS)` -> (0, "2 pass, 0 fail"); the NEGATIVE CONTROL built in-test (copy of the
  Imola row with evidence `place_*` = the Cervia point 44.245 N/12.367 E, `site_*` unchanged,
  `dist_m` 0.0, written only to tmp_path) -> check (1, FAIL `imola-q50195 ... does not reproduce
  (53566 m)`) - 53.6 km, both fail clauses fire, the reproduction clause is reported first; asserts
  the staged row's own evidence is untouched;
  (4) `test_golden_sample_matches_staged_rows` - the golden file == `_norm` of the three staged files.
  Full suite: **33 passed** under .venv (was 29 before this file).
- **Box 5:** final read of `docs/lead_artists.md` against the parent's box 1 - COMPLETE for all four
  sources, no edits needed: Imola (what/where/date incl. the upload-only case, four documented drops,
  the site point with the prep correction); Venice (three drops, the Q2194/Q773853 traps, the R2 fit
  caveat); Civitates (the six-IA table with dates + cite strings, the Liber secundus structure, triage
  stats, the 121-entry hand-list scheme + tally, both pitfalls, per-book status, the documented
  "no staged rows" reason); Merian (two IA items; not triaged yet = the 216/217 follow-on).
- **Trivia (cost one failed assert):** `evidence._line` is `f"{v:4s} {kind:15s} {key}"` - a PASS line
  prints as `PASS caption_coords  <site|title>` (1 space after the verdict, 2 after the kind).
  Don't eyeball the spacing; run it once.
- **The done-claim, per the prep's "say in the done-claim":** all prep §1 assumptions hold on the
  current (801-merged) code, re-verified this session: `evidence.check(files, books, catalog=)` is
  offline and `check_caption` fails on a stored-dist reproduction miss (±1 km) OR distance >50 km -
  the Cervia control (53.6 km) fails both; the 2026-10-10 driver .venv note is stale (.venv builds,
  numpy present, suite green). (The iteration-37 unexplained transient - one throwaway script's last
  P131-label batch came back empty, not reproducible, `language` vs `languages` ruled out - is in the
  iteration-37 DECISIONS entry.)

**Next (the parent 213's session, not this task):** verify --check/test/golden/lead-doc, tick the
parent's boxes 1, 5, 6, then box 4 (the count check) LAST, write the R6 note in 211's ## Hand-over
(the *_artists* staging files + the civitates per-book files must be merged into the canonical ones),
set the parent done. Invariants (unchanged): staging files append-only, never re-staged; no
shared-module writes (fit/evidence.py, pipeline/*, data/books/index.jsonl, validation.json); tests:
no fixed ports, no network, no writes outside project+temp.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/213-artist-views.md` (open) - hand-over: **Iteration 27 (2026-10-11): triage run FINISHED (A 292/292 + F 118/118, both complete & stable, process exited - COMMIT THEM FIRST THING: they are un

## Next open tasks
- `tasks/213b-qids-tests.md`
- `tasks/215-books-llm-ports.md`
- `tasks/216-view-books-entries.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 213 DECISION: iteration 25's orphaned triage process kept appending after the driver's snapshot commit
The driver's "uncommitted work after iteration 25" commit captured civitatesorbiste00brau.A.jsonl at 191
lines; the orphaned run kept appending until 04:03 (211 pages, n 0-210 complete, no error rows) and exited.
Nothing was corrupt: the file is append-only and run_stage/latest() is re-runnable (done = rows without
error). Lesson: before committing (or trusting) a data file a background job may still be writing, check
its mtime against now and whether a writer process is alive; otherwise the driver's snapshot commits
mid-growth states. (Recorded here because the context-limit step allowed only DECISIONS/tasks edits; the
next agent files the PITFALLS entry.)

### 2026-10-11 213 DECISION: civitates triage COMPLETE (A 292/292 + F 118/118, zero error rows) - committed; list transcription is image-based, hOCR abandoned for this book
The iteration-26 background run (/tmp/civitates_triage.py, LLM ports 8080-8082 patched in-process) printed
DONE and exited: data/books/triage/civitatesorbiste00brau.A.jsonl = 292 unique rows (complete, no errors,
no duplicates) and .F.jsonl = 118 rows (0 error rows; 239 figure readings: 222 view / 11 plan / 6 other).
Both committed with this entry - the append-only files are final, no re-run needed. While it ran I read the
cached triage images (LOCAL: data/raw/books/civitatesorbiste00brau/triage/nNNNN.jpg = leaf n+1) for 16
figure leaves. Findings: n58 = bird's-eye PLAN of Paris (poem cartouche); n85/n90/n98/n109 = bird's-eye
PLANS (Flemish/German; n98 = the famous Antwerp plan, n109 = Amsterdam, whose plate PRECEDES its title
leaf n110); n237/238 = the two Jerusalem PLANS (old city numbered walls/Temple/Tower of David + new city
Declaratio A-Z). Corrected the iteration-26 hand-over: n157/n158 ("DECEM ET TRIA LOCA" / "FEDERATORVM
HELVETIAE") are NOT maps - sheets of small town VIEWS of the 13 Swiss cantons (kind o). Views confirmed:
n194 (two Vienna views, S. Steffans labelled), n202 (the famous oblique bird's-eye VIEW of Venice,
153-item Italian legend), n214 (Ancona), n217/n218 (two Naples views), n225 (Messina view; title leaf
n226 follows it - sections interleave both ways). n52 = double title page (Burgos + S. Sebastian), n54 =
their two views; n53 = two more plates (46-item Dutch legend view + sea view) - likely the 2nd/3rd
Barcelona plates, confirm with n50/n51. n187/n199 = faded blank VERSO of the fold-outs (plates n186
Augsburg, n198 Milan; "RFPCB" stamp). TWO PITFALLS (next agent files them in PITFALLS.md): (1) the hOCR
page index for this book is MISALIGNED with the jp2 leaf sequence by a drifting 0-2 leaves (hOCR leaf 85
holds the Brussels title text that A reads on leaf 87; leaf 53 matches; leaf 109 off by 2) -
books_ia.page_texts()/ocr_captions are UNRELIABLE here; the image-based A rows are the ground truth and
217 must not use page_texts for civitates. (2) Stage F under-detects plans: its earthwork-biased prompt
flagged only 11/121 figure pages as containing a "plan" while 7+ are visually confirmed plans - 217 must
not trust F's "plan" label for kind calls on this book.

### 2026-10-11 213 DECISION: list structure decided - one entry per figure leaf keyed on leaf n, title = the plate's own inscription or the section's title leaf, kind o/s/u with kind_by hand|A
The book has no printed town list (confirmed: no list leaf in the A data). Each city section = a TITLE
LEAF (big Latin title + history text; A reads it) + 1-3 PLATE leaves (views/plans; A caption = the
plate's own inscription, often a legend or poem, often empty), interleaved both ways, so a plate's city =
its section (nearest title leaf either side). Printed page numbers exist ONLY on leaves 193-196 (1-4)
and 280-284 (I-V) (data/raw/books/civitatesorbiste00brau/civitatesorbiste00brau_page_numbers.json) - all
other `page` values null. Plan for data/books/lists/civitatesorbiste00brau.json: {"plates": null,
"figures": [{"fig": <0-based leaf n>, "title": <inscription as printed, or the city name from the section
title leaf when the plate has none>, "page": null-or-printed, "kind": "o"|"s"|"u",
"kind_by": "hand" (I read the image) or "A" (derived from stage A, unverified)}]} covering all 121 figure
leaves; .map.json = [] (list_pages maps only kind s/u and has no printed page numbers for these leaves,
so it is honestly empty - 217 extends the machinery, not 213). Visually confirmed so far: plans
n58/85/90/98/109/237/238 (s); views n194/202/214/217/218/225/157/158 (o). Remaining reads (cheap - the
images are local): n209 Rome, n205/n206 Florence, n198 Milan fold-out (view or plan?), n197 Milan arms
(excluded from drawings), n86/n97/n193 title leaves, n186 Augsburg fold-out, n50/n51. Then: 7
verified-town QIDs (Rome, Vienna, Florence, Milan, Venice, Brussels, Antwerp; paced Wikidata incl.
search-trap check) into fit/src_artists.py:BOOKS["civitates"]["sites"] + lead doc; update the lead-doc
books section (FEDERATORVM = views, fold-out versos, the two pitfalls); --check (last passed 2/2 in
iteration 24, staging files untouched since); --golden; tests/test_src_artists.py per prep §4 (negative
control: Imola row with the Cervia point 44.245/12.367 must FAIL); tick boxes 1, 5, 6 then box 4 LAST;
211's hand-over note (R6); PITFALLS entries (LLM ports, hOCR misalignment, F under-detection, background
jobs outlive sessions).

## Project-wide driver notes (newest)

### 2026-10-10 DRIVER: .venv could not be built from requirements.txt
    ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    Every package needs a pinned version and hash (AGENTS.md, Research and packages); full pip output: .agent/reports/venv.txt

### 2026-10-11 agent/a (213b) status (iteration 37, moved here by the driver)
213b item (1) done: 7 book-town QIDs verified live (Q239/Q12892/Q1741/Q490/Q641/Q2044/Q220) in
BOOKS["civitates"]["sites"]; --verify exit 0 (8 QIDs; traps: Florence-SC, Venice-LA, Brussels enwiki
data); --check 2/2; suite 29/29; lead-doc QID section rewritten; box 1 ticked. fit/src_artists.py +
docs/lead_artists.md uncommitted (harness-saved). Next: --golden (first write), tests/test_src_artists.py
(negative control = Imola row with the Cervia point), lead-doc box-1 final read.
