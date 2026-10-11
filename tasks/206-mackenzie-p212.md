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

**Iteration 67 (2026-10-11, agent a) - the test is written and green; all four boxes ticked. Status stays
open: the done-claim waits on 211 (site build) + 218 (gate registration for the 21st hand doc) per the
Depends on line; a later session (after the driver brings the task back) sets done.**

STATE at stop:
- `tests/test_src_mackenzie.py`: WRITTEN and committed this session, exactly per the iter-66 TEST SPEC
  (module docstring; fit/+pipeline/ sys.path inserts; `evidence`, `fit_gate`, `plan_fit`, `sources`,
  `src_mackenzie as mack` imports; `NO_BOOKS = data/books/.no-books` absent-on-purpose; autouse
  `no_network` socket-boom fixture). Four tests, all green (1.6 s):
  1. `test_staged_row_and_join` - one row per staging file with every field pinned (incl. the 200
     category evidence), site existing-by-QID in sites.jsonl and NOT in extras.jsonl, no clash with the
     canonical files or the 26-row sources.py MACKENZIE table, classified 1:1 (plan, by=hand), and the
     platefit doc's plan id / full-frame crop / 4 in-frame pairs each < 200 m from the catalog point.
  2. `test_evidence_offline_and_negative_control` - `evidence.check(FILES, NO_BOOKS)` exit 0 with the
     exact PASS line; never-written copy with `file_cat="Not the Castle's Category"` -> FAIL
     ("differs from the site's with no recorded chain"), staged row provably untouched.
  3. `test_gate_accepts_the_committed_doc` - `fit_gate.gate(doc pairs)` ACCEPT, n 4, med 15.81
     (abs 0.01), slope_o 0.1385 (abs 0.001, the 0.11-0.145 "must be said" band), io -7.04 (abs 0.01);
     `plan_fit.similarity` residuals finite, max 19.36 < 45, rotation -0.20 deg (abs 0.05, north-up).
  4. `test_golden_sample_matches_staged` - golden == `_norm(staged rows)` and doc with at=normalized
     (mirrors the module's `golden()`).
- Full suite: 59 passed, 5 failed = the 4 known-reds (test_serve::test_platefits_docs_match_sites,
  test_batch_eu::test_union_check + test_union_full_coverage_live, test_gate::test_recorded_
  measurement_reproduces_and_agrees - owned by 211/218, DO NOT "fix") + ONE NEW red,
  `test_site_done::test_site_done_line` (iter-67 session's 5th failure): NOT caused by this branch and
  NOT fixable from it (see the DECISIONS entry of this date). It compares the freshly rebuilt
  Stonehenge depictions.json (with the 7 plan entries) against `web/data/sites/stonehenge-q39671/
  depictions.json`, which in every checkout is a SYMLINK into the shared main-branch store
  (/home/agent/projects/ancient-works/...); that store file was reset to the pre-sync state (2 maps,
  no plans, no plan_*.webp overlays) at 14:48 local during this session's window - while agent c was
  actively in 301 (whose Touches explicitly include web/data/sites/stonehenge-q39671 and docs/site_flow;
  c's checkout had docs/site_flow/stonehenge.png modified). Transient 301/lead shared-store churn; it
  should settle when 301 lands. My branch diff vs main is exactly the mackenzie artifacts + memory
  files (the 8-line web/index.html hunk in `git diff main` is the lead's 14:58 commit f5ea863, newer
  than this checkout's local main ref - not mine).
- Boxes 1-4 all ticked this session (box 3 last: the gate is proven on the committed doc). Everything
  else from iter 65/66 unchanged and committed: fit/src_mackenzie.py, the 3 staged files, the platefit
  doc, docs/lead_mackenzie.md (says "26 rows" for the sources.py table - the task's "29" is the
  book-level count; do not "correct" it), tests/golden/src_mackenzie_sample.json.

WHEN THE DRIVER BRINGS THIS BACK (211 + 218 merged): the only remaining step is
1. re-run `timeout 300 .venv/bin/python fit/src_mackenzie.py --check` (offline) and
   `timeout 300 .venv/bin/python -m pytest -q tests/test_src_mackenzie.py` (expect green);
   also re-run the full suite once and note the reds (the 4 known-reds should be gone by then:
   211 clears the batch_eu/serve ones, 218 the gate one; test_site_done should be green once 301
   has settled the shared Stonehenge store - if it is still red, it is 300/301's to fix, not 206's);
2. if all green for this task: set `Status: done` and commit (`206: done - <one line>`); no further
   code work is expected.

Re-verify recipe (offline): `timeout 300 .venv/bin/python fit/src_mackenzie.py --check` and `--gate`
(both must be exit 0; --gate prints accept n 4 med 15.810503946029705 slope_o 0.13850057306409141
io -7.041363723612259, similarity rotation -0.2005 deg, residuals 14.16/1.98/17.46/19.36). Staging is
idempotent (re-running stage() is a no-op). `--verify` re-checks the live facts (network, paced) if
the driver ever flags drift. V2 OCR re-download recipe: archive.org item castlesofengland02mack,
files castlesofengland02mack_hocr_searchtext.txt.gz / ..._hocr_pageindex.json.gz /
..._page_numbers.json (pageindex rows = [textStart, textEnd, byteStart, byteEnd] text offsets, NOT
leaves; pagenums maps leafNum->pageNumber as strings).
