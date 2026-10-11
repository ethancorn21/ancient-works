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

**Iteration 87 (2026-10-11, agent a) - TWENTIETH early bring-back; main UNMOVED since
iter 75 (head still cd104ca; `git rev-list --left-right --count main...agent/a` = 0/114,
the +3 over iter 86 = my iter-86 commit 49be73c + driver bookkeeping c5093e2, 7221539
- zero tree change since iter 86's stop). FULL battery re-run this session INCLUDING
--gate (accept, stats identical to the committed doc). All 206-owned work green and
byte-identical to iters 66-86 (all 8 md5s stable). The 4 suite reds unchanged in cause
(211 x3, 218 x1; store re-counted 116 docs / 94 auto / 22 non-auto, gate still
"expected 20 ... found 22"). Deps 211+218 still open -> Status stays open.
No code or data change this session (none available: the only remaining work is owned
by 211/218; per the team rule no stand-ins). Re-run the same battery at the next
bring-back; when 211+218 have merged, expect 0 reds and set done.**

STATE at stop (all re-run this session, offline):
- `fit/src_mackenzie.py --check`: exit 0, `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`
  (PASS category shotwick-castle-q7502621|File:212 of 'The Castles of England...').
- `fit/src_mackenzie.py --gate`: exit 0 this session,
  `gate: accept {'n': 4, 'med': 15.810503946029705,
  'slope_o': 0.13850057306409141, 'io': -7.041363723612259}`, similarity |a| 0.38243 m/px-merc,
  rot -0.20 deg, residuals [14.2, 2.0, 17.5, 19.4] max 19.4 - identical to the committed doc
  and the golden (also iters 78-86; re-run this session).
- `tests/test_src_mackenzie.py`: 4/4 green (1.57 s, socket-boom fixture, no network).
  - re-run this session.
- All 8 committed artifacts byte-identical to iters 66-86 (re-checked this session):
  md5sum output identical to iters 66-86's list; no file moved.
  src_mackenzie 77a47defd606a8599e3af9e28b74894f, files_mackenzie f637c4bebbd98ebb059652936e06646d,
  classified_mackenzie 2ed56b79bbd356aced13230978e8536f, extras_mackenzie
  a7060e1292d2607c657a43200dd20b94, shotwick platefit doc 9a1924cf84414e26cf84b292718ce3b2,
  lead_mackenzie 5d7b7ab69371074b201d89b6b2bda0d4, test_src_mackenzie
  ddb146a2f8cb47e9b2f33ef2b0e5cbfe, golden f0936d9a0b4bf00e60ca1f3afc625d95.
- Full suite: 60 passed, 4 failed (62.72 s) - the same 4 as iters 74-86, causes re-verified live:
  1. `test_batch_eu::test_union_check` (211's): `assert not check["orphan_docs"]` fails with
     `['shotwick-castle-q7502621.c_e6e5490609414bb9.json']` (tests/test_batch_eu.py:811).
  2. `test_batch_eu::test_union_full_coverage_live` (211's): same orphan_docs failure (not
     skipped; the live EU list matches docs/batch_eu.md "Sites run").
  3. `test_gate::test_recorded_measurement_reproduces_and_agrees` (218's):
     `gate_heldout: expected 20 hand-fit documents in data/db/platefits/, found 22` - 20
     registered hand-fits + my shotwick doc + the human's maiden-castle-c_c20ff6b1f16d173d doc
     (store re-counted this session: 116 docs, 94 with auto:true, 22 without
     = 20 registered + shotwick + maiden-castle). 218's box 4
     re-registration must absorb BOTH new docs.
  4. `test_serve::test_platefits_docs_match_sites` (211's): `assert 'shotwick-castle-q7502621'
     in {site ids}` - the site is unbuilt in web/data/sites; 211's merge build adds it (it
     reads the extras row below; the catalog's sites.jsonl already carries the same id by QID
     with the fuller record).
- test_site_done still green.
- Deps re-checked this session: tasks/211-merge-build.md = Status open; tasks/218-gate-holdout-new-hand-docs.md = Status open.
- Nothing on main moved since iter 75 (head cd104ca; `git diff --stat main agent/a` = the 8
  206-owned files + memory-file diffs only, i.e. my 206 work awaiting acceptance). The shared
  store (data/db/platefits, web/data/sites) is main-branch-backed: my shotwick doc and the
  human's maiden-castle doc are both visible to every agent's suite, which is exactly what
  the gate/batch/serve reds key on. (No red touches a 206-owned file.)

ALL COMMITTED ARTIFACTS (unchanged since iter 65/66; the eight-file list is the corrected one
from iter 76):
- `fit/src_mackenzie.py` (stage/fetch/sheet/gate; staging idempotent; `--verify` re-checks
  live facts if the driver ever flags drift; `check()` REQUIRES exactly one extras row with
  aerial_ok - the file below is part of the contract, not optional),
- `data/commons/files_mackenzie.jsonl` (1 row, 200 evidence field, site by existing QID),
- `data/commons/classified_mackenzie.jsonl` (1 row, plan, by=hand),
- `data/catalog/extras_mackenzie.jsonl` (1 row: id shotwick-castle-q7502621, QID Q7502621,
  aerial_ok true, source fit/src_mackenzie.py, note "built for the 1897 plan (task 206)").
  This is the task Notes' "the picture is the reason to build": 211 merges it into the
  canonical extras.jsonl and builds the unbuilt site with the plan already tied. It coexists
  with (does not duplicate) the catalog's sites.jsonl row of the same id: check() only
  forbids the id in the canonical extras.jsonl, and the note says the fuller sites.jsonl
  record reads first. Tracked since ab899eb (driver commit after iter 65); never modified.
- `data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json` (full-frame 839x840
  crop, 4 corner pairs),
- `docs/lead_mackenzie.md` (says "26 rows" for the sources.py table - the task's "29" is the
  book-level count; do not "correct" it; L195-196 document the extras row),
- `tests/test_src_mackenzie.py` + `tests/golden/src_mackenzie_sample.json`.
- V2 OCR re-download recipe (if the driver ever flags drift): archive.org item
  castlesofengland02mack, files castlesofengland02mack_hocr_searchtext.txt.gz /
  ..._hocr_pageindex.json.gz / ..._page_numbers.json (pageindex rows = [textStart, textEnd,
  byteStart, byteEnd] text offsets, NOT leaves; pagenums maps leafNum->pageNumber as strings).

DEPS at stop (all already on my `Depends on:` line 001, 200, 211, 218 - nothing to add, no
stand-ins per the team rule; re-checked this session, both still `open`):
- `tasks/211-merge-build.md` = open (Depends on 200, 204, 205, 206, 207, 208, 209, 210; agent c
  on 203b/207/302a, 207c blocked on the human's Roy 1793 copy - re-checked this session; its
  hand-over (from 213's done-claim) lists the staging files to merge: extras/files/classified
  *_artists.jsonl (2 new town sites + 2 picture rows) and the civitates books files) - owns 3 of the 4 reds
  (batch_eu x2 + serve): its merge build adds the shotwick doc to the batch union and builds
  the site.
- `tasks/218-gate-holdout-new-hand-docs.md` = open (Depends on 001) - owns the 4th:
  re-registers the 22-doc hand-fit partition (20 registered + shotwick + maiden-castle).

WHEN THE DRIVER BRINGS THIS BACK (after 211 + 218 merged): the ONLY remaining step is
1. `timeout 300 .venv/bin/python fit/src_mackenzie.py --check` (expect exit 0, 1 pass) and
   `timeout 300 .venv/bin/python -m pytest -q tests/test_src_mackenzie.py` (expect 4 passed);
   also re-run the full suite once and note the reds - if 211+218 have merged, expect 0 reds
   (211 clears batch_eu x2 + serve; 218's re-registration clears the gate one with 22 docs:
   20 registered + shotwick + maiden-castle-c_c20ff6b1f16d173d; if more reds appear, they
   must come from other in-flight tasks - any red touching a 206-owned file is a regression
   to investigate, not a known-red to ignore);
2. if all green for this task: set `Status: done` and commit (`206: done - <one line>`). No
   further code work is expected.
