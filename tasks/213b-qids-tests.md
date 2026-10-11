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
