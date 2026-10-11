Status: open
# 206: Mackenzie - the five-towered castle on page 212
Depends on: 001, 200
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
**Iteration 59 (2026-10-11, agent a) - measurement session. BIG FIX: my iter-58 PAGE coordinates are VOID (I misread a shrunken 2x sheet: the drawing spans the WHOLE 839x840 page, not the top-left quadrant). Corrected page map below. Ground re-measured with corrected labels. EA LiDAR is now 500-erroring (it worked at session start - space requests). Nothing written yet: no platefit doc, no staging, no lead doc, no test. Module + raw files already committed (iter 57/58, driver commit 59bb954).**

State now:
- `fit/src_mackenzie.py` as committed (fetch/verify/sheet/zoom/write-doc/gate/stage/check/golden; 499 lines). Raw fetched in this checkout: `data/raw/books/mackenzie/212.jpg` (839x840), `data/raw/commons/shotwick-castle-q7502621/e6e5490609414bb9.jpg`, Esri 800 m aerial `data/raw/aerial/shotwick-castle-q7502621.jpg`. Network works ONLY with `aw.UA` (plain urllib → 403).
- Test suite was green at session start; .venv present.
- The identification chain (book evidence) is UNCHANGED and strong: p.212 = Shotwick, V2 leaf 212 = printed 164, CHESHIRE running head, Shotwick chapter p.180, Holme 1600 drawing "pentagon strengthened by six towers", 1897 remains = mound + crescent + two entrenchments (OCR quotes in DECISIONS.md). Only the page-px measurements are new.

**CORRECTED PAGE MAP (page px of the raw 839x840; measured this session from a dark-pixel census + 3x quadrant crops with 25 px grids - recipe /tmp/page_quads.py, crops /tmp/pg_TL|TR|BL|BR.jpg):**
- The pentagonal earthwork (THICK line ~30-40 px wide) occupies the whole page. Vertices: TOP (405,25); RIGHT (827,570); BOTTOM (620,835); LOWER-LEFT (30,690); LEFT (50,430).
- The five towers are HORSeshoe C's on the bank edges (openings face the interior/along the bank, NOT the plan centre):
  - T-top (on the top-right edge): C centre ≈ (725,235), outer Ø ≈ 130 px, opens toward lower-left (gap ≈ (655-700, 270-320)).
  - T-top-left (on the top-left edge): C centre ≈ (185,195), outer Ø ≈ 160 px, opens right (gap ≈ (230-265, 165-250)).
  - T-right (at/below the right corner): C centre ≈ (795,560)?? - READ /tmp/pg_BR.jpg to confirm exact centre (BR upper-right shows the bank entering the corner then a C whose opening faces left/lower-left ≈ (680-720, 590-630)).
  - T-bottom (on the bottom edge, right of centre): C centre ≈ (640,760), opens upper-left (gap ≈ (545-575, 690-730)); the bottom bank runs from (420,760) east into it, and a second segment continues east of it (BR: (650-700, 745-800)).
  - T-bottom-left (at/below the lower-left corner): C centre ≈ (105,680), opens right (gap ≈ (150-230, 640-720)); the left edge comes down into it, the bottom edge leaves it.
- HALL (thin double-line building, upper centre): rectangle ≈ (430-525, 185-305) with a small wing on the right ≈ (525-545, 210-285); interior partition lines at x ≈ 455 and ≈ 490. Centre ≈ (475, 245).
- SMALL BUILDING (thin lines, partly DASHED = conjectural, lower left): dashed outline descends from ≈ (225-290, 420-580); solid part ≈ (255-360, 575-750) (L/T-shape with a wing ≈ (330-360, 600-650)). Centre ≈ (300, 660).
- NORTH ARROW (thin, lower-centre, INSIDE the pentagon): long horizontal line at y ≈ 472 from x ≈ 355 to ≈ 605; a vertical crossbar at x ≈ 455 spanning y ≈ 425-510 with serifs (a small filled wedge sits on the line at ≈ (445-455, 462) - likely a letter/monogram to read at 8x: crop (430,420)-(480,520)); the arrowhead is at the LEFT end (≈ (355-395, 455-490)). So the printed arrow points WEST (page left) - consistent with the iter-58 finding that the plan is NORTH-UP (arrow 90° off or marks something else).
- GATE GAP: a break in the thick bank on the lower-left edge between the T-bottom-left C and the bottom band: census gap at ≈ (300-335, 745-765). (Not bottom-centre as iter 58 said.)
- No caption, no scale bar anywhere on the page (whole page census checked).

**GROUND (re-measured this session on the 200 m crop = 800 px at 0.25 m/px, centre = catalog point (0,0) = (-2.97608, 53.2272); 10 m grid, labels 5 decimals via the crop's OWN mercator corners - recipes /tmp/mack_full.py, /tmp/mack_quad.py; quadrant images /tmp/qNW|qNE|qSW|qSE.jpg (aerial) and /tmp/rqNW|... (relief) exist from this session but /tmp may be gone):**
- IMPORTANT: my earlier "P2 motte at (E +0..+11, N -46..-48)" read was from a 900 px sheet with the 4x-label bug and is NOT trustworthy. Re-identify on the quadrants.
- A = the bright building cluster (the hall candidate): upper-centre of the grassed field, ≈ (E -20±10, N +60±10) (200 crop frame ≈ (280-320, 140-200)); the strongest bright stone feature on ground.
- The site field: a large grassed enclosure (crescent earthwork area) inside a tree belt; a dark watercourse/ditch runs NW of centre; a dark valley (old Dee) SW; tree belts W and SE; a small bright speck B ≈ (E -68, N -8)?? (unconfirmed - was on the buggy sheet; re-check on /tmp/qSW.jpg); another bright speck C ≈ (E +84, N -20) (later building, NOT on plan).
- The book says the 1897 remains = "a large mound, supported by a huge earthwork of crescent form, and two deep entrenchments on the land side" - expect the MOTTE (40x20 m, Gatehouse 212) as a ring in the LiDAR relief, plus the crescent bank and two entrenchments.

**EA LiDAR service state this session:** the 800 m box fetch worked at session start (640000/640000 px, elevations 3.8-25.3 m), but later ALL sizes (200/400/800 m) returned HTTP 500 (tried 6+ times) - it is flaky/rate-limited. `aw.fetch_dem` for the 800 m box RAISES when EA 500s (no static S3 source for Cheshire). WAIT between DEM requests; the 200 m relief quadrants can be regenerated once it recovers (recipe in /tmp/mack_relq.py - note it must skip NaNs: `dem=(dem-nan-safe)`; also `Image.fromarray` of NaNs gives black images - guard with np.nanmin/nanmax).

**THE FIT (box 3) - plan for the next session, in order:**
1. Regenerate: `MACK_OUT=/tmp .venv/bin/python fit/src_mackenzie.py --sheet --zoom`, then /tmp/mack_quad.py-style 4x quadrants (aerial + relief once EA answers) with 10 m grids labelled via the 200 m crop's OWN mercator corners (cx±100m/ground_scale). Do NOT reuse any iter-58 900 px sheets or their coordinates.
2. Pick pairs (page px from the CORRECTED map above → lon/lat on ground): (a) hall (475,245) → A; (b) small building (300,660) → its ground feature (find on qSW/qSE; if none, drop the pair); (c) T-bottom-left (105,680) → the motte if the motte sits south-west of centre (the book's mound); (d) T-top (725,235) or T-right (795,560) → the NE end of the crescent bank (the thick bank in the relief); (e) gate gap (315,755) → the entrenchment gap in the NE bank (the book's "two deep entrenchments on the land side"). n = 4-6; the orientation is NORTH-UP (page top = north) per iter 58's geometry proof, but with the CORRECTED page map re-derive the rotation from the pairs - do not assume.
3. `--write-doc <crop> u,v=lon,lat ...` (crop = the drawn pentagon's bbox ≈ (25,5)-(835,840), i.e. essentially the whole page - measure exactly) then `--gate`; if REJECT iterate on anchor choice, never move pairs to force a pass; if still honest-reject → R2 route (review item + `## Proposed changes`; box 3 stays unticked; identification stands on the documentary chain).
4. `--dry` then stage for real; write `docs/lead_mackenzie.md` (prep section 3 structure; section 3(d) county context from the OCR findings in DECISIONS.md; 3(e) surviving ground; 4 fit table with gate stats + the orientation/arrow finding + the 6-vs-5-towers note (book says six, plan shows five C's); 5 decision). The doc's `at`/`checked`/`date_commons` are normalized in the golden.
5. Test per prep section 3 (socket-blocking fixture; join; evidence.check over the staging file; negative-control row must FAIL; gate re-run; golden via `--golden`). `.venv/bin/python -m pytest -q` green; tick boxes (box 3 last, on the committed doc); one commit: module + staging rows + doc + lead + test + golden.

**PITFALLS still to add before committing (queued from iter 58, NOT yet in PITFALLS.md):** (1) under fit/: gridded sheets of a SUB-CROP must map pixels→lon/lat through the crop's OWN bbox corners (the 800 m box's corners for a 200 m crop give 4x-too-spread labels - that bug caused this session's P2 misread); also my own throwaway /tmp/mack_800.py had a TL/BR y-swap that flipped N labels - `aw.corners()` returns [TL,TR,BR,BL] so to_merc(TL).y is NORTH and to_merc(BR).y is SOUTH. (2) archive.org hocr: `*_page_numbers.json` is format v2 ({identifier, format-version, confidence, pages:[{leafNum,pageNumber}]}), `*_hocr_pageindex.json` rows are [leafStart, leafEnd, textStart, textEnd]. (3) NEW this session: EA WCS (environment.data.gov.uk lidar DTM) is flaky - returns all-zeros or 500s after ~15 requests in a session; space DEM calls, retry later; an all-zero 800 m box means "no data", not real terrain (elevations here are 4-25 m). (4) NEW: a 1200 px rendered sheet viewed by the agent is shown shrunken - I misjudged a 1678 px 2x page sheet as a smaller drawing and measured the phantom half-size pentagon of iter 58; verify page measurements with a dark-pixel census (run/merge per row band) and 3x quadrant crops, not one big shrunken view.

**If the network is down:** --check/--gate on an existing doc/--golden work offline; the fit needs `data/raw/books/mackenzie/212.jpg` (persisted here) + the Esri aerial (also persisted) + EA relief (re-fetch when it recovers). The 29 hand-tied plates and the 25 existing hand fits stay untouched.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/206-mackenzie-p212.md` (open) - hand-over: **Iteration 58 (2026-10-11, agent a) - fit session: plan + ground measured, ORIENTATION RESOLVED (page top = north); next: measure 3 anchors precisely
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and

## Next open tasks
- `tasks/215-books-llm-ports.md`
- `tasks/216-view-books-entries.md`
- `tasks/217-view-books-lists.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 206 DECISION: evidence kind for the p.212 row is "category", and an extras row IS staged (R3 resolved)
    Two prep assumptions settled against the merged code: (1) OQ-1 - fit/evidence.py `check(files, books,
    catalog)` takes file paths (CLI --files/--books/--catalog), so the 206 test runs the real check over the
    staging file, no re-implementation; the row's own evidence field is kind "category" (the file's Commons
    category == Q7502621's P373 "Shotwick Castle", both verified live 2026-10-11), so row.cat must be
    "Shotwick Castle" (the 29 hand-tied rows are cat null + kind hand_tied: different tie, different field).
    (2) R3/OQ-2 - build_catalog.main() has NO picture-based selection over the 12,603-row sites.jsonl (it
    builds whatever --ids/region/top/min-p picks; both files read into one row list), and 211's box 3 builds
    the extras-derived new sites, so the prep's "no new extras row needed" is superseded: stage an extras row
    {id shotwick-castle-q7502621, qid Q7502621, aerial_ok: true, source: fit/src_mackenzie.py} exactly as the
    task Notes prescribe for an unbuilt castle; build_catalog reads the catalog row first (CAT before EXTRAS)
    and its `sid in built` skip makes the duplicate harmless; 211 logs the duplicate.

### 2026-10-11 206 DECISION: the p.212 plate is Volume 2, not bracketed by Oxford p.207 as the task framing said
    The live file description (verified 2026-10-11) says "Volume : 02, Page : 212" for p.212 while the p.207
    Oxford row says "Volume : 01": the two IA volumes paginate separately, so a file number is a leaf number
    WITHIN its volume. The task's "p.207 Oxford / p.231 Lancaster bracket it" is only half true: p.212 and
    p.231 are both V2, 19 leaves apart, and the plate sits in V2's Cheshire section (the V2 chapter text and
    index name Shotwick: "Shotwick, ii. 180"). The lead doc must record the true layout (OQ-3: the actual
    county headings in the V2 OCR, from archive.org castlesofengland02mack hocr) - it still constrains the
    plate, just not the way the task file phrases it.

### 2026-10-11 206 DECISION: the p.212 plan is printed NORTH-UP (page top = north), not north-left as the arrow suggests; the surviving ring is the C11 motte
    Two findings from measuring the fetched page against the ground (details in the task hand-over): (1) The book's p.212 drawing (pentagon, five towers, hall, dashed building, gate) sits in the page's top-left quadrant (bbox ~(10,0)-(425,425) of the 839x840 frame). The only clear surviving ring on the LiDAR/aerial is a ~40 m ditched mound at (E +0..+11 m, N -46..-48 m) from the catalog point - the size and ditch match the C11 MOTTE (Gatehouse 212: 40x20 m hexagonal mound, 25 m ditch), not a 12 m castle tower. With the three reliable anchors (plan hall -> the bright building cluster NW of centre; plan dashed building -> the speck W; plan T4 (bottom horseshoe) -> the motte) the solved similarity under the printed orientation (page left = N, per the arrow) is rotated ~90 deg off the ground, while under north-up it comes out with rotation ~0 deg, scale ~0.41 m/px, the pentagon's south corner due south on the motte and the hall on the NW building: the plan is a normal north-up map and the printed left-pointing arrow is 90 deg off (or marks something else - /tmp/arrow_crop.jpg, 4x zoom of page (170,235)-(345,290), to be re-read; /tmp may be gone). CAVEAT recorded for the fit: with exactly 3 pairs any similar triangle fits both conventions to ~0 residual (6 eqs, 4 params) - the final doc needs >= 4 pairs so the gate is not degenerate.

### 2026-10-11 206 DECISION: the book's own V2 text identifies the plate's castle (OQ-3 resolved); the plan is the 1600 Randle Holme drawing, a pentagon with SIX towers, five drawn
    Re-downloaded the V2 OCR (archive.org castlesofengland02mack: hocr searchtext/pageindex + page_numbers; the page_numbers file is format v2 {identifier, format-version, confidence, pages:[{leafNum, pageNumber}]} and pageindex rows are [leafStart, leafEnd, textStart, textEnd] - the prep's "leaf->printed map" guess was wrong). The Shotwick chapter (printed p.180, running head CHESHIRE 181 on the continuation page; next chapter STOCKPORT) says: the plan is "a drawing and plan of this fortress by Kendle [Randle] Holme, as it appeared then, in a ruinous condition. Its trace was a pentagon strengthened by six towers, one of which, according to Camden, was five storeys high", and of the 1897 remains: "those seen at present consisting merely of a large mound, supported by a huge earthwork of crescent form, and two deep entrenchments on the land side". The index reads "Shotlack, ii. 179, Shotwick, ii. 180". So the p.212 plate (leaf 212 = printed 164; the Lancaster plate leaf 231 = printed 183, 19 pages on) is a plan of Shotwick drawn from Holme's c.1600 depiction of the ruined fortress - which explains the five (of six) towers, the thick bank, and why the modern ground only carries the motte + crescent + entrenchments. This is the backbone of docs/lead_mackenzie.md section 3 (evidence chain a-f) and of the fit's expectations.

## Project-wide driver notes (newest)

### 2026-10-10 DRIVER: .venv could not be built from requirements.txt
    ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    Every package needs a pinned version and hash (AGENTS.md, Research and packages); full pip output: .agent/reports/venv.txt

## Agent a current position (206, iteration 59)
Fit-measurement session, interrupted at context limit. FINDING: iter-58 page coordinates are VOID - the p.212 drawing spans the whole 839x840 page (I misread a shrunken 2x sheet); corrected full page map (pentagon vertices, 5 C-towers, hall, dashed building, west-pointing arrow with crossbar at (455,472), gate gap (300-335,745-765)) is in the task hand-over and DECISIONS.md. Ground re-measured with corrected 10 m grids (200 m crop is authoritative; 800 m = context). EA LiDAR now 500-erroring (space requests). Nothing written yet (no doc/staging/test); module + raw files committed. NEXT: fit session per task hand-over step list - regenerate sheets, re-pick 4-6 pairs on the corrected map (n>=4, re-derive orientation), --write-doc + --gate, then stage + lead doc + test + golden.
