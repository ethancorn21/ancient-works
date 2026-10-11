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

**Iteration 75 (2026-10-11, agent a) - eighth early bring-back; the driver DID merge main into
my branch (2224d94): the HUMAN commit cd104ca (Maiden Castle hand-placed DPLA plan) is now IN
my tree, and everything the hand-over predicted about it held. All 206-owned work re-verified
green and md5-identical to iters 66-74; the 4 suite reds are unchanged in cause (211 x3,
218 x1) and 218's gate red now reads "found 22" exactly as predicted. Deps 211+218 still
open -> Status stays open. Re-run the same battery at the next bring-back; when 211+218
have merged, expect 0 reds (or reds no longer touching this task's files) and set done.**

STATE at stop (all re-run this session, offline):
- `fit/src_mackenzie.py --check`: exit 0, `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`.
- `fit/src_mackenzie.py --gate`: exit 0, `gate: accept {'n': 4, 'med': 15.810503946029705,
  'slope_o': 0.13850057306409141, 'io': -7.041363723612259}`, similarity |a| 0.38243 m/px-merc, rot -0.20 deg,
  residuals [14.2, 2.0, 17.5, 19.4] max 19.4 - identical to the committed doc and the golden.
- `tests/test_src_mackenzie.py`: 4/4 green (1.64 s, socket-boom fixture, no network).
- All 7 committed artifacts md5-identical to iters 66-74: src_mackenzie 77a47defd606a8599e3af9e28b74894f,
  files_mackenzie f637c4bebbd98ebb059652936e06646d, classified_mackenzie 2ed56b79bbd356aced13230978e8536f,
  shotwick platefit doc 9a1924cf84414e26cf84b292718ce3b2, lead_mackenzie 5d7b7ab69371074b201d89b6b2bda0d4,
  test_src_mackenzie ddb146a2f8cb47e9b2f33ef2b0e5cbfe, golden f0936d9a0b4bf00e60ca1f3afc625d95.
- Full suite: 60 passed, 4 failed (62.79 s) - same 4 as iter 74, causes unchanged:
  1. `test_batch_eu::test_union_check` (211's): `assert not check["orphan_docs"]` fails with
     `['shotwick-castle-q7502621.c_e6e5490609414bb9.json']` (tests/test_batch_eu.py:811).
  2. `test_batch_eu::test_union_full_coverage_live` (211's): same orphan_docs failure (not skipped;
     the live EU list matches docs/batch_eu.md "Sites run").
  3. `test_gate::test_recorded_measurement_reproduces_and_agrees` (218's): now
     `gate_heldout: expected 20 hand-fit documents in data/db/platefits/, found 22` (was "found 21"
     pre-cd104ca). Verified store state: 116 docs, 22 non-auto = 20 registered hand-fits + my
     shotwick doc + the human's maiden-castle-c_c20ff6b1f16d173d doc. 218's box 4 re-registration
     must absorb BOTH new docs; 218 still open, Depends on 001 only.
  4. `test_serve::test_platefits_docs_match_sites` (211's): `assert 'shotwick-castle-q7502621' in
     {site ids}` - site unbuilt (catalog row exists by QID, extras intentionally absent). 211's
     merge build adds it.
- test_site_done still green (301's a749aa5 landed on main in the f5ea863..cd104ca window; the
  re-seeded Stonehenge line docs stayed byte-identical through this merge - it passed in the run).

WHAT MOVED (cd104ca, the only main commit after f5ea863 besides driver/lead bookkeeping):
- `data/db/platefits/maiden-castle-q1232816.c_c20ff6b1f16d173d.json`: dropped `"auto": true` and
  `"score"`, crop [165,256,895,663] of the 1280x889 DPLA scan, 3 hand-placed pairs, book
  "Wikimedia Commons". It is now a hand-fit in the store. Its only effects on this task:
  (a) the gate red's count 21 -> 22 (as above - expected and predicted in the iter-74 hand-over);
  (b) it leaves the batch-auto population, so 203b/211's union/"Sites run" expectations may shift -
  their territory, never 206's to fix (verified above: the batch_eu reds are unchanged in cause).
  cd104ca touched NO 206-owned file (its diff is that one doc only).
- Deps status at stop: `tasks/211-merge-build.md` = open (Depends on 200, 204, 205, 206, 207, 208,
  209, 210; agent c on 207b/203b/302a, 207c blocked on the human's Roy 1793 copy),
  `tasks/218-gate-holdout-new-hand-docs.md` = open (Depends on 001; waiting for an agent).
  Both already on my `Depends on:` line (001, 200, 211, 218) -> nothing to add; per the team
  rule no stand-ins built. Branch is fully in sync with main (main is 0 commits ahead of agent/a
  at stop; my 78 commits sit on top).

ALL COMMITTED ARTIFACTS (unchanged since iter 66/67):
- `fit/src_mackenzie.py` (stage/fetch/sheet/gate; staging idempotent; `--verify` re-checks live
  facts if the driver ever flags drift), `data/commons/files_mackenzie.jsonl` (1 row, 200 category
  evidence, site by existing QID - NOT in extras), `data/commons/classified_mackenzie.jsonl`
  (1 row, plan, by=hand), `data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json`
  (full-frame 839x840 crop, 4 corner pairs), `docs/lead_mackenzie.md` (says "26 rows" for the
  sources.py table - the task's "29" is the book-level count; do not "correct" it),
  `tests/test_src_mackenzie.py` + `tests/golden/src_mackenzie_sample.json`.
  `data/catalog/extras_mackenzie.jsonl` intentionally absent (site is in the catalog by QID).
- V2 OCR re-download recipe (if the driver ever flags drift): archive.org item castlesofengland02mack,
  files castlesofengland02mack_hocr_searchtext.txt.gz / ..._hocr_pageindex.json.gz / ...
  _page_numbers.json (pageindex rows = [textStart, textEnd, byteStart, byteEnd] text offsets, NOT
  leaves; pagenums maps leafNum->pageNumber as strings).

WHEN THE DRIVER BRINGS THIS BACK (after 211 + 218 merged): the ONLY remaining step is
1. `timeout 300 .venv/bin/python fit/src_mackenzie.py --check` (expect exit 0, 1 pass) and
   `timeout 300 .venv/bin/python -m pytest -q tests/test_src_mackenzie.py` (expect 4 passed);
   also re-run the full suite once and note the reds - if 211+218 have merged, expect 0 reds
   (211 clears batch_eu x2 + serve; 218's re-registration clears the gate one with 22 docs:
   20 registered + shotwick + maiden-castle-c_c20ff6b1f16d173d; if more reds appear, they must
   come from other in-flight tasks - any red touching a 206-owned file is a regression to
   investigate, not a known-red to ignore);
2. if all green for this task: set `Status: done` and commit (`206: done - <one line>`). No
   further code work is expected.
