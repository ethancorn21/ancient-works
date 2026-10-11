Status: open
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

**Iteration 64 (2026-10-11, agent a) - the missing part is filed: tasks/218-gate-holdout-new-hand-docs.md is in the queue (Status: open, Depends on: 001, Touches: tools/gate_heldout.py + tests/test_gate.py - one tool and its test, the 802 pattern; state-agnostic, so it does not wait on 206 or 207). Audited 206's boxes/Touches against it: nothing moves - no 206 box describes gate_heldout work (box 4 is 206's own test file), and 218's two files were never in 206's Touches line (all eight of 206's paths stay its own); the done-claim's suite-green requirement stays on the Depends on line (001, 200, 211, 218) - the driver holds the claim until 211 and 218 are in main. Working tree clean (the driver committed the platefit doc in d7dde6f). The 4 known-red tests are unchanged: (1) tests/test_serve.py::test_platefits_docs_match_sites, (2)+(3) the two union tests in tests/test_batch_eu.py - owned by 211 (it builds shotwick's site); (4) tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - owned by 218 (21 non-auto docs in data/db/platefits: the 20 registered + shotwick; partition()'s "expected 20" SystemExit). Next session: the staging session, steps 1-6. No Re-read items pending.**

**Facts the lead doc and the test need (all verified; the full detail is in the DECISIONS entry "the corner-based fit is resolved"):**

- The doc (committed d7dde6f): data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json -
  crop [0,0,839,840] (the ink spans the whole page: full-frame, the alligator/barnard convention),
  size [839,840], src "commons", book "Wikimedia Commons", label 1897, title "Shotwick Castle, plan
  from Mackenzie, The Castles of England (1897)", ref = the file title "File:212 of 'The Castles of
  England- ... plans' (11296081346).jpg", cite "by The British Library; No restrictions; <commons
  url>", pairs [405,25,-2.9756073,53.2282398] [827,570,-2.9742830,53.2272404] [620,835,
  -2.9747557,53.2267733] [30,690,-2.9772880,53.2270046] (page px -> lon/lat: catalog point + ground
  metres via to_merc).
- The fit: 4 ground corners, dropping the weakest-prominence corner (NW) -> ACCEPT: n 4, med 15.81,
  slope_o 0.1385 (the 0.11-0.145 band - the lead doc must say so), io -7.04 (no second clause),
  residuals N 14.2 / E 2.0 / S-SW 17.5 / W-SW 19.4, rotation -0.20 deg, ground scale 0.229 m/px
  (= |a|*k, k = cos 53.2272; a is MERCATOR m/px). Rejected sets to record: 5 corners (med 14.96,
  slope_o 0.167 > 0.145, io +17.7) and 5+gate-gap (slope_o 0.315; the phi-27 cleft between the E
  lobe and the NE finger tangle is NOT the plan's gate gap). Ground: segmentation verbatim from
  mack_poly5 (2.19 ha, centroid (27.2,9.4)); radial r_out, peaks prominence >= 3 m and >= 20 deg
  apart: N (31.5,115.8), E (119.8,4.5), S-SW (88.2,-47.5), W-SW (-80.5,-21.8), NW (-27.2,53.5);
  clockwise gaps 89/41/121/53/56 vs the plan's 95.6/46.5/98.9/40.2/78.8. Predicted (recorded, not
  pairs): pentagon centre (20.5,17.4) vs the centroid (27.2,9.4); the C11 motte ring at (80,-5),
  63.6 m from the centre (in the eastern bailey); the hall (41,78) on the dark tree clumps, NOT a
  building; centre160 crops: a grassed oval + a faint ring in its eastern part, no towers or hall -
  matching the book's own 1897 words ("a large mound ... a huge earthwork of crescent form, and two
  deep entrenchments").
- The evidence chain (prep section 3.3, items a-f): (a) the file's Commons category = Q7502621's
  P373 "Shotwick Castle" (verified live 2026-10-11; row cat "Shotwick Castle", evidence kind
  "category" - the 29 hand-tied rows are kind hand_tied with cat null: different tie, different
  field); (b) the book's index "Shotwick, ii. 180"; (c) the V2 chapter (printed p.180, running head
  CHESHIRE 181 on the continuation page, next chapter STOCKPORT): the plan is Holme's c.1600
  drawing, "a pentagon strengthened by six towers"; (d) the county context: p.212 and p.231
  Lancaster are both V2, 19 leaves apart; p.207 Oxford is V1 - the task's bracket is half true;
  the actual V2 county headings around printed pp.~179-199 (OQ-3) get filled in from the V2 OCR
  (recipe in prep section 6); (e) the surviving ground as above (no standing towers, no visible
  hall); (f) candidates: no five-towered pentagon plan in the V2 county range matches a-f ->
  Shotwick is unique.
- The page: data/raw/books/mackenzie/212.jpg (persisted). /tmp artifacts (if still there):
  mack_poly6.py (offline-rerunnable corner fit), mack_fit_poly6.json/.jpg (the overlay),
  mack_centre160b.jpg, mack_centre160_eq.jpg (the faint motte ring), mack_400z.jpg, mack_poly5.py;
  re-fetch: fit/src_mackenzie.py --zoom (deterministic).

**Next session (in order):**
1. `.venv/bin/python fit/src_mackenzie.py --dry`, then without the flag (network; re-verifies the
   live Commons file; idempotent, keep/keep-extras) -> writes data/commons/files_mackenzie.jsonl,
   data/commons/classified_mackenzie.jsonl and data/catalog/extras_mackenzie.jsonl (the extras row
   aerial_ok: the picture is the reason to build - 211 builds the site with the plan already tied).
2. `.venv/bin/python fit/src_mackenzie.py --verify` (network: the Q7502621 fact sheet + the live
   file facts, with the checked date the lead doc records).
3. Write docs/lead_mackenzie.md per prep section 3 (the five sections; the fit section = the
   numbers above + the rejected sets + the predictions/why-not-pairs; the county context from
   step 2 + the V2 OCR).
4. Write tests/test_src_mackenzie.py per prep section 3 (the socket-blocking fixture; the join;
   evidence.check offline over the staged row + the negative control; the gate re-run on the
   committed doc -> accept; the golden via --golden). My test does NOT need the site built.
5. `.venv/bin/python -m pytest -q` - expect my test green and the 4 known-red still red until
   211 + 218 merge into main (the driver's sync then turns the suite green). Do not touch the 4.
6. Tick the boxes: 1 and 2 with the lead doc, 3 LAST (on the committed doc), 4 when my test is
   green. Status: done only with the full suite green (after 211 + 218 merge - the driver brings
   the task back).
