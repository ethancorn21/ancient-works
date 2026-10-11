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
- [x] `BOOKS["civitates"]["sites"]`: seven towns, each {qid, name, lon, lat, place, wikipedia,
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

## Hand-over
**Iteration 37 (2026-10-11): 213b item (1) DONE - the seven book-town QIDs are verified live and in the
table; lead doc's QID section rewritten. Box 1 ticked. UNCOMMITTED on disk: fit/src_artists.py +
docs/lead_artists.md (the harness saves them - commit them first thing with this task's id).**

**What was done (all verified by running, not reasoning):**
- `fit/src_artists.py:BOOKS["civitates"]["sites"]` = the seven hand-verified towns, keyed by QID in the
  book's plate order, each {name, lon, lat, place, wikipedia, cat}: Q239 Brussels (fig 85 BRVXELLA),
  Q12892 Antwerp (98 ANVERPIA), Q1741 Vienna (193/194 VIENNA AVSTRIAE), Q490 Milan (198/199 MEDIOLANVM),
  Q641 Venice (201/202 VENETIA - same values as SITES), Q2044 Florence (205/206 FLORENTIA), Q220 Rome
  (209 ROMA). Table point = the verified P625 city point (the book views centre on the walled old towns,
  within a few km - recorded in the lead doc). `table_sites()` added (SITES + book towns, SITES wins the
  Q641 clash); `verify_qids()` now covers both tables (8 unique QIDs) with P131-label fetch chunked at 50
  (wbgetentities max); docstring usage line updated.
- `.venv/bin/python fit/src_artists.py --verify` (live, paced, 2026-10-11): exit 0, 8/8 QIDs verified
  (label + every P625 + P373 + P131 + enwiki + search trap per town); **no P625 >50 km flag fired**
  (all within 0.27 km of their table point). Search traps found: **Florence** first hit with P625 =
  Q597842 Florence, South Carolina (7538 km); **Venice** = Q773853 Venice, Los Angeles (9891 km, the
  known one). **Brussels data trap**: the enwiki "Brussels" article is the region Q240; the city is Q239
  ("City of Brussels", P373 "Brussels (municipality)") - Q240's P625 is only 85 m away, so only the
  P373/enwiki check separates them. (My own memory-guessed QIDs - Q374 "Rome", Q2140 "Vienna" - were
  WRONG: Q374 is vodka; the real ones are Q220/Q1741. Search + the five-fact verification is the only
  route; memory is not a source.)
- `docs/lead_artists.md`: the QID-verification section now carries the full 8-QID --verify output (checked
  2026-10-11) + per-town trap notes; intro paragraph points 216/217 at the table; the per-book status
  bullet for civitatesorbiste00brau now names the table and what 216/217 take from it.
- `.venv/bin/python fit/src_artists.py --check` re-run after the edits: exit 0, no join problems, 2/2 PASS
  caption_coords. Full suite: 29 passed in 37.22 s under .venv.

**Prep assumptions checked against main (say in the done-claim):** all of prep §1 holds on the current
(801-merged) code - `evidence.check(files, books, catalog=...)` is offline and check_caption (fit/
evidence.py L190-207) fails when stored dist_m doesn't reproduce ±1 km OR distance > 50 km, so the
Cervia-point negative control (44.245/12.367, ~53.5 km from Imola's site point) fails on BOTH clauses;
the "wait for 801" is over (801 done/merged); the 2026-10-10 driver note about the .venv rebuild is stale
(800 done; .venv works, numpy present). Prep §2's Imola "bad P625 / 53 km NW" was already corrected before
this task (that point is Cervia; 213b's task file carries the corrected negative control). One
unexplained transient: a throwaway discovery script's last P131-label batch came back empty (no 429, no
error key) after ~13 paced calls; NOT reproducible, and an A/B test proved `language` (singular) is simply
ignored by wbgetentities (returns ALL labels) while `languages` (plural) filters - the parameter is not
the cause; the canonical verify_qids uses `languages` and ran clean three times this session.

**Remaining (213b items 2-4, then the parent):** (2) run `.venv/bin/python fit/src_artists.py --golden`
ONCE to create tests/golden/src_artists_sample.json (it does not exist yet; staging files are final, so
this is the intended first write - never hand-edit afterwards); (3) write tests/test_src_artists.py per
prep §4 + this task's boxes: socket-blocking fixture (tests must not touch the network); the join over the
staged files (re-check what check_staged() enforces: file rows name staged-or-existing sites, no staged
id/QID pre-exists, every staged site has a picture, (site,title) unique, no clash with canonical
files.jsonl, classified 1:1); table completeness (SITES + the BOOKS towns); offline evidence check
(import fit/evidence.py, check(FILES_ARTISTS, an absent books path, catalog=EXTRAS_ARTISTS) -> exit 0,
zero FAIL, every staged row PASS caption_coords); the NEGATIVE CONTROL built in-test (copy of the Imola
files row with evidence place_* = Cervia 44.245/12.367, site_* unchanged, dist_m 0.0 -> must be reported
FAIL, never written to any file); golden comparison (keys sorted, checked/date_commons normalized the way
src_artists._norm does). Run under .venv/bin/python. (4) final read of docs/lead_artists.md against the
parent's box 1 (what/where/date/staged/drops for all four sources - it looks complete already: Imola,
Venice and the books sections + this session's QID section). Then commit: "213b: ... - ...". The parent
213 then does boxes 1/5/6, box 4 last, the 211 R6 note, done. Invariants: staging files never re-staged;
no shared-module writes (fit/evidence.py, pipeline/*, data/books/index.jsonl, validation.json are off
limits); tests: no fixed ports, no network, no writes outside project+temp.

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
