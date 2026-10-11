Status: open
# 206: Mackenzie - the five-towered castle on page 212
Depends on: 001, 200
Touches: fit/src_mackenzie.py, data/catalog/extras_mackenzie.jsonl, data/commons/files_mackenzie.jsonl, data/commons/classified_mackenzie.jsonl, docs/lead_mackenzie.md, tests/test_src_mackenzie.py

## Goal
GOAL.md point 4: page 212 of Mackenzie, The Castles of England (1897) is a five-towered
castle plan with no caption - the only gap in the book's already hand-tied 29 plates
(pipeline/sources.py). Identify the castle with evidence (the book is arranged by county:
the plates around p.212 - p.207 Oxford, p.231 Lancaster - constrain it; five-towered plans
are rare; the surviving ground is the final check), tie it to a site, stage the row, and let
the fit prove the identification. If it cannot be identified with evidence, document the
search and drop the lead: a wrong castle on the map is worse than none.

## Acceptance criteria
- [ ] The p.212 scan is found (the British Library's Flickr scans, the same URL pattern as
      the hand-tied rows) and downloaded to data/raw/books/ in the working phase; the
      five-towered plan is drawn out and available for comparison (its shape, tower count,
      and any scale/north information recorded in docs/lead_mackenzie.md).
- [ ] The castle is identified by evidence recorded in docs/lead_mackenzie.md: the book's
      county context, the plan's shape against candidate castles, and the surviving ground
      (relief/aerial) matching the plan - or the lead is dropped, and the file says exactly
      what was searched, what candidates were considered, and why none was accepted.
- [ ] If identified: the site (an existing one by QID, or a new extras row) and the picture
      row are staged (files_mackenzie.jsonl with the 200 evidence field - caption+coords or
      QID, the source book recorded - and a classified row "plan" by hand), and a fit of the
      plan on the site's ground passes the gate (001): the identification is proven by
      numbers, not just asserted.
- [ ] Test (no network): the staged row joins and passes fit/evidence.py check offline, with
      a golden sample. If the lead was dropped, the test asserts the documentation exists
      and the staging files are absent or empty.

## Notes
- The other 29 Mackenzie plates stay where they are (sources.py hand ties); this task adds
  at most one row. The fit is proposed through 202's machinery if available; otherwise a
  hand proposal (fitkit) is fine - this is one plate, not a batch.
- A castle whose site is not built yet: the extras row gets the picture as its reason to
  build (aerial_ok) so 211 builds it with the plan already tied.

## Hand-over
**Iteration 57 (2026-10-11, agent a) - module built, live verify done; the fit session is next.**

State now:
- `fit/src_mackenzie.py` EXISTS (uncommitted at this cut - the harness saved it). Full module, modeled on
  fit/src_artists.py, stdlib-only top (system python3 has no numpy; run EVERYTHING under `.venv/bin/python`):
  `--fetch` (the 839x840 scan -> data/raw/books/mackenzie/212.jpg + data/raw/commons/shotwick-castle-q7502621/
  e6e5490609414bb9.jpg, asserts live size), `--verify` (QID fact sheet + file cats), `--sheet` (800 m box
  aerial 1 m/px + best-effort LiDAR relief + the page, all gridded with lon/lat / page-px labels -> $MACK_OUT,
  default /tmp), `--zoom` (200 m crop at 0.25 m/px), `--write-doc x0,y0,x1,y1 u,v=lon,lat ...` (the platefit
  doc, castle-rising shape), `--gate` (fit_gate.gate on the doc's own pairs, transform=None; fails loud on
  REJECT), `--dry`/stage (the 3 staging rows, idempotent), `--check` (join + fit/evidence.py check), `--golden`.
  Ran `--verify` live: Q7502621 confirmed (label, P625 == catalog point, P373 ['Shotwick Castle'], P31
  Q92062, P131, enwiki) and the file confirmed (839x840, desc Volume 02/Page 212/HMNTS 10369.v.7/1897, cats
  include 'Shotwick Castle') - NO drift from prep section 6. All prep assumptions re-checked against main:
  001 gate API, 200 check(files,books,catalog), 211 merge/build (extras row is how the site gets built),
  dem_sources 'ea' covers England (OQ-5), plan-id c_e6e5490609414bb9, export_plans url rule.
- Files touched so far: only fit/src_mackenzie.py. No staging files, no lead doc, no doc, no test yet.
  Test suite was green before this session (driver note); nothing of mine has run under pytest yet.

Decisions made this session (in DECISIONS.md):
- Evidence kind for the row = "category" (site's P373 == file's category 'Shotwick Castle'); row.cat must be
  'Shotwick Castle' (the 29 hand-tied rows differ: cat null + hand_tied). OQ-1 settled: the 200 check takes
  file paths, so the test runs the real check over files_mackenzie.jsonl.
- The extras row IS staged (aerial_ok: true) - build_catalog has no picture-based selection and 211 builds
  the extras-derived new sites. The prep's "no new extras row needed" was wrong on R3; the task Notes' own
  prescription (the picture as reason to build) wins. The catalog sites.jsonl row keeps the same id (read
  first in build_catalog; 211 logs the duplicate).
- County context corrected: p.212 is Volume 2 (p.207 Oxford is Volume 1; separate pagination) - see the
  206 entry in DECISIONS.md. OQ-3 (actual V2 county headings from the archive.org hocr) is still open for
  the lead doc.

Exact next steps (in order):
1. FIRST: add to this task's `Touches:` line the two paths it needs but does not yet name:
   `data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json` and `tests/golden/src_mackenzie_sample.json`
   (team rule: a path must be in Touches before it is written).
2. `.venv/bin/python fit/src_mackenzie.py --fetch` then `--sheet` and `--zoom`; READ the /tmp sheets
   (mackenzie_212_sheet.jpg, mackenzie_212_relief.jpg, zoom_*_sheet.jpg) with the read tool. The page's north
   arrow points to the page's LEFT (page top = east) - expect ~90 deg rotation in the similarity. Pick 4-6
   anchors, best first: the 3 surviving round towers (aerial/relief circles + the plan's corner towers), the
   hall footprint (upper centre of the page; the standing building cluster), the gate gap (bottom centre),
   a pentagon bank corner as fallback. Pairs are [u, v (page px of the 839x840 frame), lon, lat]; compute
   lon/lat from the grid labels' box corners, never from the sheet's own pixels (fitkit's warning).
   `--write-doc` (crop = the drawn plan's bbox, measure it on the page sheet), then `--gate`. If REJECT:
   re-pick anchors (R2: the plan is a thick-lined schematic, 10-35% axis mismatch is normal for Mackenzie
   plates) - never move pairs to force a pass; if still rejected after honest iteration, go the R2 route:
   review item + `## Proposed changes` on this task, box 3 stays unticked.
3. `--dry`, then stage for real; write docs/lead_mackenzie.md in full (prep section 3's structure: scan /
   plan / identification a-f / fit / decision; the county context (d) from the V2 OCR - re-download recipe
   in prep section 6: archive.org castlesofengland02mack hocr pageindex+searchtext; the fit section records
   gate stats, similarity residuals, aerial-vs-relief choice).
4. tests/test_src_mackenzie.py per prep section 3 (socket-blocking fixture as in tests/test_src_van_deventer.py;
   join assertions; evidence check over the staging file; in-memory negative control row (wrong QID/cat) must
   FAIL; gate re-run over the committed doc; golden via `--golden`, normalized at/checked) ; `.venv/bin/python
   -m pytest -q` green; tick boxes (box 3 last, on the committed doc); rewrite this hand-over; commit
   (one commit: the module + staging rows + doc + lead + test + golden; the 29 plates and the 25 hand fits
   are untouched).

Notes for the next session: the module's `check()` treats a missing platefit doc as a problem (expected
before step 2); `stage()` asserts the live file is still 839x840 before writing (R4); the golden's `at` and
`evidence.checked` are normalized; the test must never write outside the project + temp dir and never bind
a fixed port (204/205/213 pattern). If the network is unavailable, the offline commands (--check, --gate on
an existing doc, --golden) still work - but the fit needs the fetched page first.
