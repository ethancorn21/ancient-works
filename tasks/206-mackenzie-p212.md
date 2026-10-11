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

**Iteration 71 (2026-10-11, agent a) - re-verified the full state (the driver brought 206 back early, 211+218
STILL open): main has not moved since iter 70 (`git log agent/a..main` empty, head f5ea863), all 206-owned
artifacts md5-identical to iters 66-70, --check/--gate/4-tests green with byte-identical stats, full suite
59/5 with the same dependency-owned reds (211 x3, 218 x1, 300/301 x1). Deps already on the `Depends on:`
line, so nothing to add and no stand-ins (team rule). Status stays open.**

STATE at stop (all re-run this session, offline):
- `fit/src_mackenzie.py --check`: exit 0, `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`.
- `fit/src_mackenzie.py --gate`: exit 0, `gate: accept {'n': 4, 'med': 15.810503946029705,
  'slope_o': 0.13850057306409141, 'io': -7.041363723612259}`, similarity |a| 0.38243 m/px-merc, rot -0.20 deg,
  residuals [14.2, 2.0, 17.5, 19.4] max 19.4 - identical to the committed doc and the golden.
- `tests/test_src_mackenzie.py`: 4/4 green (1.63 s, socket-boom fixture, no network).
- All 7 committed artifacts md5-identical to iters 66/67/68/69/70: src_mackenzie 77a47defd606a8599e3af9e28b74894f,
  files_mackenzie f637c4bebbd98ebb059652936e06646d, classified_mackenzie 2ed56b79bbd356aced13230978e8536f,
  shotwick platefit doc 9a1924cf84414e26cf84b292718ce3b2, lead_mackenzie 5d7b7ab69371074b201d89b6b2bda0d4,
  test_src_mackenzie ddb146a2f8cb47e9b2f33ef2b0e5cbfe, golden f0936d9a0b4bf00e60ca1f3afc625d95.
- Full suite: 59 passed, 5 failed (75 s) - the same set as iters 68/69/70, each red's live cause re-confirmed
  this session (failure text below; none touches a 206 file):
  1. `test_gate::test_recorded_measurement_reproduces_and_agrees` (218): `gate_heldout held failed: expected
     20 hand-fit documents in data/db/platefits/, found 21; the registered partition is void,
     see docs/gate.md section 1`. The 21st doc is 206's shotwick doc; 218's box 4 names exactly this red (218 relaxes
     the expected-count check). Not a 206 fix; 206 never touches tools/gate_heldout.py or tests/test_gate.py.
  2. `test_serve::test_platefits_docs_match_sites` (211): `'shotwick-castle-q7502621' not in sites.json ids` -
     re-confirmed live this session (site unbuilt; the catalog row exists by QID, extras intentionally absent).
     211's merge build adds the site.
  3. `test_batch_eu::test_union_check` (211): union must contain `shotwick-castle-q7502621.c_e6e5490609414bb9.json`.
  4. `test_batch_eu::test_union_full_coverage_live` (211): same missing doc.
  5. `test_site_done::test_site_done_line` (300's file, in 301's Touches): still the depictions.json byte
     compare at index 35 (b'p' != b'm', plan vs map). Its compare target `web/data/sites/stonehenge-q39671/
     depictions.json` (reached THROUGH the per-site directory symlink into the shared main-branch store -
     the directory is the symlink; the file itself is a regular file there - PITFALLS "This machine and
     its environment") STILL carries the pre-sync state: mtime 2026-10-11 14:48:36 (unchanged since the
     iter-67 observation), 2 entries, first kind "map". Agent c is still mid-301 (the prompt lists 301 in
     c's work). It settles when 301 lands; NOT 206's to fix; do not "fix" it.
- Deps status at stop: `tasks/211-merge-build.md` = open (it Depends on 207, which is still split/in flight
  via 207a/207b/207c - agent c is on 207b now), `tasks/218-gate-holdout-new-hand-docs.md` = open (Depends on
  001 only; waiting for an agent to pick it up). Both are already on the `Depends on:` line (001, 200, 211,
  218) -> nothing to add; per the team rule no stand-ins were built; the driver gives this agent other
  work and brings 206 back once both merge.
- Main-branch check: `git log agent/a..main` empty at session start (main head f5ea863, a lead web-only
  commit, unchanged since iter 70); nothing merged since iter 70 touched 206's files.
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
