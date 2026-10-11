Status: in-progress
# 206: Mackenzie - the five-towered castle on page 212
Depends on: 001, 200, 218
Touches: fit/src_mackenzie.py, data/catalog/extras_mackenzie.jsonl, data/commons/files_mackenzie.jsonl, data/commons/classified_mackenzie.jsonl, data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json, docs/lead_mackenzie.md, tests/test_src_mackenzie.py, tests/golden/src_mackenzie_sample.json

## Goal
GOAL.md point 4: page 212 of Mackenzie, The Castles of England (1897) is a five-towered
castle plan with no caption - the only gap in the book's already hand-tied 29 plates
(pipeline/sources.py). Identify the castle with evidence (the book is arranged by county:
the plates around p.212 - p.207 Oxford, p.231 Lancaster - constrain it; five-towered plans
are rare; the surviving ground is the final check), tie it to a site, stage the row, and let
the fit prove the identification. If it cannot be identified with evidence, document the
search and drop the lead: a wrong castle on the map is worse than none.

## Acceptance criteria
- [x] The p.212 scan is found (the British Library's Flickr scans, the same URL pattern as
      the hand-tied rows) and downloaded to data/raw/books/ in the working phase; the
      five-towered plan is drawn out and available for comparison (its shape, tower count,
      and any scale/north information recorded in docs/lead_mackenzie.md).
- [x] The castle is identified by evidence recorded in docs/lead_mackenzie.md: the book's
      county context, the plan's shape against candidate castles, and the surviving ground
      (relief/aerial) matching the plan - or the lead is dropped, and the file says exactly
      what was searched, what candidates were considered, and why none was accepted.
- [x] If identified: the site (an existing one by QID, or a new extras row) and the picture
      row are staged (files_mackenzie.jsonl with the 200 evidence field - caption+coords or
      QID, the source book recorded - and a classified row "plan" by hand), and a fit of the
      plan on the site's ground passes the gate (001): the identification is proven by
      numbers, not just asserted.
- [x] Test (no network): the staged row joins and passes fit/evidence.py check offline, with
      a golden sample. If the lead was dropped, the test asserts the documentation exists
      and the staging files are absent or empty.

## Notes
- The other 29 Mackenzie plates stay where they are (sources.py hand ties); this task adds
  at most one row. The fit is proposed through 202's machinery if available; otherwise a
  hand proposal (fitkit) is fine - this is one plate, not a batch.
- A castle whose site is not built yet: the extras row gets the picture as its reason to
  build (aerial_ok) so 211 builds it with the plan already tied.

## Hand-over

**DONE (iteration 91, agent a, 2026-10-11).** All four acceptance boxes verified green this
session; Status set to done. What closed it: 218 (Depends on) is now `done` and merged to main
(commit 1dcbc06: the gate_heldout partition derives over the 20 registered names, so
post-registration hand docs like my shotwick doc are tolerated - the 4th suite red, gate
`expected 20 ... found 22`, is GONE, re-verified live this session); and the lead dropped my
211 dependency (commit 0be0b09: "211 waits for 206: a cycle that kept 206 open"), so the
remaining 3 reds (batch_eu x2 + serve, all 211's) no longer gate this task. My 8 artifacts are
all IN main (verified with `git cat-file -e main:<file>`; `git diff --stat main agent/a` =
memory files only) and byte-identical to iters 66-90 (8 md5s, list below). No further work:
when 211 eventually merges, its build picks up my extras row / shotwick doc from the shared
main-backed store automatically - no 206 action needed.

STATE at done (all re-run this session, offline):
- `fit/src_mackenzie.py --check`: exit 0, `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`
  (PASS category shotwick-castle-q7502621|File:212 of 'The Castles of England...').
- `fit/src_mackenzie.py --gate`: exit 0, `gate: accept {'n': 4, 'med': 15.810503946029705,
  'slope_o': 0.13850057306409141, 'io': -7.041363723612259}`, |a| 0.38243 m/px-merc,
  rot -0.20 deg, residuals [14.2, 2.0, 17.5, 19.4] max 19.4 - identical to the committed doc
  and the golden.
- `tests/test_src_mackenzie.py`: 4/4 green (1.67 s, socket-boom fixture, no network).
- All 8 committed artifacts byte-identical to iters 66-90 (re-checked this session):
  src_mackenzie 77a47defd606a8599e3af9e28b74894f, files_mackenzie f637c4bebbd98ebb059652936e06646d,
  classified_mackenzie 2ed56b79bbd356aced13230978e8536f, extras_mackenzie
  a7060e1292d2607c657a43200dd20b94, shotwick platefit doc 9a1924cf84414e26cf84b292718ce3b2,
  lead_mackenzie 5d7b7ab69371074b201d89b6b2bda0d4, test_src_mackenzie
  ddb146a2f8cb47e9b2f33ef2b0e5cbfe, golden f0936d9a0b4bf00e60ca1f3afc625d95.
- Full suite: 62 passed, 3 failed (64.47 s) - all 3 owned by 211 (still `open`):
  `test_batch_eu::test_union_check` + `test_batch_eu::test_union_full_coverage_live`
  (orphan_docs `['shotwick-castle-q7502621.c_e6e5490609414bb9.json']`, tests/test_batch_eu.py:835
  area) and `test_serve::test_platefits_docs_match_sites` (shotwick site unbuilt in
  web/data/sites; 211's merge build adds it). The gate red is RESOLVED by 218 (now green).
  None of the three touches a 206-owned file; the lead's 211-cycle decision means they are
  211's to clear, not a gate on 206.

THE EIGHT ARTIFACTS (all in main since 218-era merges; unchanged since iter 65/66):
- `fit/src_mackenzie.py` (stage/fetch/sheet/gate; staging idempotent; `--verify` re-checks
  live facts if the driver ever flags drift; `check()` REQUIRES exactly one extras row with
  aerial_ok - the file below is part of the contract, not optional),
- `data/commons/files_mackenzie.jsonl` (1 row, 200 evidence field, site by existing QID),
- `data/commons/classified_mackenzie.jsonl` (1 row, plan, by=hand),
- `data/catalog/extras_mackenzie.jsonl` (1 row: id shotwick-castle-q7502621, QID Q7502621,
  aerial_ok true, source fit/src_mackenzie.py, note "built for the 1897 plan (task 206)") -
  "the picture is the reason to build": 211 merges it into the canonical extras.jsonl and
  builds the site with the plan already tied.
- `data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json` (full-frame 839x840
  crop, 4 corner pairs),
- `docs/lead_mackenzie.md` (says "26 rows" for the sources.py table - the task's "29" is the
  book-level count; do NOT "correct" it),
- `tests/test_src_mackenzie.py` + `tests/golden/src_mackenzie_sample.json`.
- V2 OCR re-download recipe (if the driver ever flags drift): archive.org item
  castlesofengland02mack, files castlesofengland02mack_hocr_searchtext.txt.gz /
  ..._hocr_pageindex.json.gz / ..._page_numbers.json (pageindex rows = [textStart, textEnd,
  byteStart, byteEnd] text offsets, NOT leaves; pagenums maps leafNum->pageNumber as strings).

Nothing left to do on 206. Do not reopen it for the 211 reds: the lead already decided the
cycle (commit 0be0b09), and 211's own acceptance covers clearing them when it merges.
