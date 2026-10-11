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

**Iteration 74 (2026-10-11, agent a) - seventh early bring-back, but main HAS moved since iter
73 (f5ea863 -> cd104ca): 301's re-seed test landed (the 5th red, test_site_done, is now GREEN)
and a HUMAN commit cd104ca replaced Maiden Castle's batch auto-fit with a hand-placed DPLA
ground plan - cd104ca is NOT in my branch yet (driver merged main only up to 2eb60f2,
merge-base 2eb60f2; team rule: I never merge; the driver brings it next session). Re-ran the
full battery: all 206-owned artifacts md5-identical to iters 66-73, --check/--gate/4-tests
green, full suite now 60 passed / 4 failed (down from 59/5): batch_eu x2 + serve (211's) and
gate (218's). Deps 211+218 still open -> Status stays open.**

STATE at stop (all re-run this session, offline):
- `fit/src_mackenzie.py --check`: exit 0, `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`.
- `fit/src_mackenzie.py --gate`: exit 0, `gate: accept {'n': 4, 'med': 15.810503946029705,
  'slope_o': 0.13850057306409141, 'io': -7.041363723612259}`, similarity |a| 0.38243 m/px-merc, rot -0.20 deg,
  residuals [14.2, 2.0, 17.5, 19.4] max 19.4 - identical to the committed doc and the golden.
- `tests/test_src_mackenzie.py`: 4/4 green (1.56 s, socket-boom fixture, no network).
- All 7 committed artifacts md5-identical to iters 66-73: src_mackenzie 77a47defd606a8599e3af9e28b74894f,
  files_mackenzie f637c4bebbd98ebb059652936e06646d, classified_mackenzie 2ed56b79bbd356aced13230978e8536f,
  shotwick platefit doc 9a1924cf84414e26cf84b292718ce3b2, lead_mackenzie 5d7b7ab69371074b201d89b6b2bda0d4,
  test_src_mackenzie ddb146a2f8cb47e9b2f33ef2b0e5cbfe, golden f0936d9a0b4bf00e60ca1f3afc625d95.
- Full suite: 60 passed, 4 failed (62.68 s) - DOWN from 59/5:
  1. `test_batch_eu::test_union_check` (211's): `check["orphan_docs"] == []` fails with
     `['shotwick-castle-q7502621.c_e6e5490609414bb9.json']` (tests/test_batch_eu.py:835). NOTE: the
     assertion text moved vs iters 68-73 (`assert (not [...])` -> the `orphan_docs` check) - 301's
     f0d8c0b merged main through; the CAUSE is unchanged: the shotwick doc is not in the EU batch union.
  2. `test_batch_eu::test_union_full_coverage_live` (211's): same `orphan_docs` failure at :835, same
     shotwick doc. The test is NOT skipped this time (docs/batch_eu.md "Sites run" matches the live EU
     list), so the orphan check actually ran - the cause is still 211's merge adding the doc to the union.
  3. `test_gate::test_recorded_measurement_reproduces_and_agrees` (218's): `gate_heldout held failed:
     gate_heldout: expected 20 hand-fit documents in data/db/platefits/, found 21; the registered
     partition is void, see docs/gate.md section 1` (unchanged in MY checkout: 21 = 20 registered + shotwick;
     see the cd104ca note below - once the driver merges it the message will say **found 22**).
  4. `test_serve::test_platefits_docs_match_sites` (211's): `assert 'shotwick-castle-q7502621' in {site ids}`
     - site unbuilt (catalog row exists by QID, extras intentionally absent). 211's merge build adds it.
  5. `test_site_done::test_site_done_line` is NOW GREEN (passed, 3.93 s, verified in isolation): 301's
     a749aa5 re-seeded the 7 fabricated Stonehenge docs into tests/golden/stonehenge_linecheck_docs/ and the
     re-run is byte-identical - it landed on main and merged into my branch. The shared-store depictions.json
     (mtime still Oct 11 14:48:36.649, unchanged) no longer trips it. Resolved by 301, never 206's fix.

MAIN MOVED (since iter 73's f5ea863 head) - the commits and their effect on this task:
- a749aa5 (301): test_site_done re-seed (red #5 gone, above).
- f0d8c0b (301): Argentoratum through the line - all 8 batch docs were the fabricated pattern class,
  sent to the review item (34 -> 42) and DELETED from the platefits store. Together with 7 more
  Stonehenge-fabricated deletions that landed on main in the f5ea863..2eb60f2 window, the platefits
  store in my checkout shrank 131 -> 116 docs (95 `auto: true` + 21 non-auto; the 21 = the 20
  registered hand-fits + my shotwick doc - the SAME set the gate test observes).
- 2eb60f2 ([lead] 302): lead only, no data.
- **cd104ca (HUMAN, main head, NOT in my branch yet): "Maiden Castle: the owner placed the DPLA ground
  plan by hand on the Mac page (3e7daea), copied here; it replaces the batch automatic fit."** It edits
  `data/db/platefits/maiden-castle-q1232816.c_c20ff6b1f16d173d.json`: drops `"auto": true` and `"score"`,
  new crop [165,256,895,663] of the 1280x889 DPLA scan, 3 hand-placed pairs, `"book": "Wikimedia Commons"`,
  `at 2026-10-11T19:52:41Z`. CONSEQUENCES once the driver merges it into my branch (next session):
  (a) gate_heldout's non-auto count goes 21 -> 22, so red #3's message becomes "found 22" - 218's
  re-registration (its box 4) must absorb BOTH the shotwick and the maiden-castle-c_c20ff6b1f16d173d docs;
  (b) the doc leaves the batch-auto population, so the batch union/"Sites run" expectations (203b's
  fit/batch_eu.py - agent c, and 211's merge) may shift; that is their territory, never 206's to fix.
  My 206-owned files are untouched by cd104ca. I did NOT merge it into my branch (team rule: no git merge
  unless the prompt asks for merge resolution) - my checkout is at merge-base 2eb60f2, so all battery
  results above are pre-cd104ca.
- Deps status at stop: `tasks/211-merge-build.md` = open (Depends on 200, 204, 205, 206, 207, 208, 209, 210;
  207 still in flight: 207a+207b open, 207c blocked on the human's Roy 1793 copy; agent c on 207b/203b/302),
  `tasks/218-gate-holdout-new-hand-docs.md` = open (Depends on 001 only; waiting for an agent). Both already
  on the `Depends on:` line (001, 200, 211, 218) -> nothing to add; per the team rule no stand-ins built.
- Nothing in this task's files changed this session (verification only); working tree clean apart from this
  memory update.

ALL COMMITTED ARTIFACTS (unchanged since iter 66/67):
- `fit/src_mackenzie.py` (stage/fetch/sheet/gate; staging idempotent; `--verify` re-checks live facts if the
  driver ever flags drift), `data/commons/files_mackenzie.jsonl` (1 row, 200 category evidence, site by
  existing QID - NOT in extras), `data/commons/classified_mackenzie.jsonl` (1 row, plan, by=hand),
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
   also re-run the full suite once and note the reds (211 should clear batch_eu + serve; 218 the gate one -
   and if cd104ca has merged by then the gate red's "found N" should read 22 with 218's re-registration
   covering shotwick AND maiden-castle-c_c20ff6b1f16d173d; test_site_done is green since 301's a749aa5 -
   if any red turns out to touch a 206 file, that is a regression to investigate, not a known-red to ignore);
2. if all green for this task: set `Status: done` and commit (`206: done - <one line>`). No further code
   work is expected.
