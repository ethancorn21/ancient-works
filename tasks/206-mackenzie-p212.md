Status: open
# 206: Mackenzie - the five-towered castle on page 212
Depends on: 001, 200, 211, 218
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

**Iteration 68 (2026-10-11, agent a) - re-verified the full state after the driver's main sync: everything
this task owns is green and byte-identical to iter 67; the suite still fails only on the 5 dependency-owned
reds; 211 and 218 are both still `open`, so the done-claim stays held (no stand-ins, per the rule).**

STATE at stop (all re-run this session, offline):
- `fit/src_mackenzie.py --check`: exit 0, `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`.
- `fit/src_mackenzie.py --gate`: exit 0, `gate: accept {'n': 4, 'med': 15.810503946029705,
  'slope_o': 0.13850057306409141, 'io': -7.041363723612259}`, similarity |a| 0.38243 m/px-merc, rot -0.20 deg,
  residuals [14.2, 2.0, 17.5, 19.4] - identical to the committed doc and the golden.
- `tests/test_src_mackenzie.py`: 4/4 green (1.63 s, socket-boom fixture, no network).
- Full suite: 59 passed, 5 failed - EXACTLY the iter-67 set, none owned by 206:
  1. `test_batch_eu::test_union_check` + `test_union_full_coverage_live` - owned by 211.
  2. `test_serve::test_platefits_docs_match_sites` - owned by 211.
  3. `test_gate::test_recorded_measurement_reproduces_and_agrees` - owned by 218.
  4. `test_site_done::test_site_done_line` - 300's hermetic test; its compare target
     `web/data/sites/stonehenge-q39671/depictions.json` (a SYMLINK into the shared main-branch store in
     every checkout - see the PITFALLS entry "This machine and its environment") was still in the
     pre-sync state this session (mtime 2026-10-11 14:48, first entry kind "map" not "plan" - same as the
     reset observed in iter 67 while agent c was mid-301; agent c is on 301 still). 301's Touches include
     that dir and docs/site_flow; it settles when 301 lands. NOT 206's to fix; do not "fix" it.
- Deps status at stop: `tasks/211-merge-build.md` = open, `tasks/218-gate-holdout-new-hand-docs.md` = open.
  Both in the Depends on line, so no action: the done-claim waits; no stand-ins built (per the rule).
- Nothing in this task's files changed this session (verification only); working tree clean apart from
  this memory update.

ALL COMMITTED ARTIFACTS (unchanged since iter 66/67):
- `fit/src_mackenzie.py` (stage/fetch/sheet/gate; staging idempotent; `--verify` re-checks live facts if
  the driver ever flags drift), `data/commons/files_mackenzie.jsonl` (1 row, 200 category evidence,
  site by existing QID - NOT in extras), `data/commons/classified_mackenzie.jsonl` (1 row, plan, by=hand),
  `data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json` (full-frame 839x840 crop, 4 corner
  pairs), `docs/lead_mackenzie.md` (says "26 rows" for the sources.py table - the task's "29" is the
  book-level count; do not "correct" it), `tests/test_src_mackenzie.py` + `tests/golden/src_mackenzie_
  sample.json`. `data/catalog/extras_mackenzie.jsonl` intentionally absent (site is in the catalog by QID).
- V2 OCR re-download recipe (if the driver ever flags drift): archive.org item castlesofengland02mack,
  files castlesofengland02mack_hocr_searchtext.txt.gz / ..._hocr_pageindex.json.gz / ...
  _page_numbers.json (pageindex rows = [textStart, textEnd, byteStart, byteEnd] text offsets, NOT leaves;
  pagenums maps leafNum->pageNumber as strings).

WHEN THE DRIVER BRINGS THIS BACK (after 211 + 218 merged): the ONLY remaining step is
1. `timeout 300 .venv/bin/python fit/src_mackenzie.py --check` (expect exit 0, 1 pass) and
   `timeout 300 .venv/bin/python -m pytest -q tests/test_src_mackenzie.py` (expect 4 passed);
   also re-run the full suite once and note the reds (211 should clear batch_eu + serve, 218 the gate one;
   test_site_done should be green once 301 has settled the shared Stonehenge store - if it is still red,
   it is 300/301's to fix, never 206's; if any red turns out to touch a 206 file, that is a regression to
   investigate, not a known-red to ignore);
2. if all green for this task: set `Status: done` and commit (`206: done - <one line>`). No further code
   work is expected.
