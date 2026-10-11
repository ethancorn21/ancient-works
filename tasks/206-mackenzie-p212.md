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
**Iteration 60 (2026-10-11, agent a) - fit session, interrupted at context limit. KEY REVISION: iter-59's GROUND anchor "A = bright building cluster (E -20, N +60)" is VOID - there are NO buildings inside the 200 m box; the bright spots were mown grass, the pale band is a road. Surviving ground is faint: flat grass, a NW-SE ditch/valley, a C-shaped shallow ditch band S of centre, no visible 40 m mound in the 1 m DTM. EA LiDAR is working again (space requests). Nothing written to the repo this session (module still as committed). 800 m sheets regenerated in /tmp. NEXT: read the 800 m sheet to locate the hall OUTSIDE the 200 m box, then decide the pair set (or take the R2 route).**

State:
- `fit/src_mackenzie.py` + raw files committed (driver 59bb954); test suite green at session start; .venv present. Human note (iter 60): the lead wants 206 finished one-castle-at-a-time before the next site (300 Stonehenge goes to agent c).
- /tmp artifacts (may be gone; recipes below): 200 m quadrants `mack_aer200_{NW,NE,SW,SE}.jpg` (aerial) and `mack_rel200_*` (relief), DEM high-pass `mack_dem_hp_{g12,g38}_*.jpg`, centre-100 m DEM `mack_dem_centre.jpg`, 75 m site aerial `mack_site4x.jpg`, and the regenerated 800 m pair `mackenzie_212_sheet.jpg` + `mackenzie_212_relief.jpg` (EA 800 m answered: 640000/640000 px, 3.8-25.3 m). Scripts: `/tmp/mack_fit.py` (200 m quadrants, 10 m grids through the crop's OWN mercator corners - keep this recipe), `/tmp/mack_reveal.py` (DEM high-pass: Gaussian 12 m / 38 m backgrounds, percentile stretch, autocontrast), `/tmp/mack_measure.py` (bright clusters, bump candidates, ring-band test).

Ground facts measured this session (200 m crop = 800 px at 4 px/m, centre = catalog point (-2.97608, 53.2272)):
- NO building anywhere in the 200 m box (checked b>130 and colour classes). The pale tan band (col ~[152,136,110]) is a road/gravel strip running NNE-SSW on the west side (px x 0..160, y 15..265 = (E -100..-60, N +35..+95)) running NW out of the box - likely the access to Shotwick Hall, which sits OUTSIDE the box NW of the tree belt.
- Bright green patches (col ~[120,155,125]) = mown grass: (E -9..-13, N +61..+65), (E -26, N +51), (E +7..+29, N -71..-80). Iter-59's "A" was one of these - void.
- Tree belt: one big dark belt runs NW-SE through the box (from ~(E -95, N +95) toward ~(E -20, N -70)) plus a W edge belt.
- Site centre ±37 m (mack_site4x.jpg): uniform green grass; one faint brighter patch at (E -15, N -20); no bank, no ring, no building visible in the 0.6 m aerial.
- DEM (1 m LiDAR, 5.2-14.3 m over the box; the regional gradient is 9 m and dominates): a NW-SE valley band (the watercourse, dark in high-pass); a C-shaped shallow ditch band enclosing a brighter area centred ≈ (E -12, N -3), radius 15-20 m (band passes (E -12, N +12) and (E +9, N -6) and continues SE out of the box); strongest local bump +1.13 m at (E -41, N +45) = the valley edge, not clearly a mound; ring-band test (15-60 m annulus vs 30 m background) ±0.08 m on all four sides = no crescent bank at 30 m scale. The 1897 remains (mound + crescent + two entrenchments) are faint on both the 1 m DTM and the 0.6 m aerial - the honest ground evidence is the ditch system, the belts and the road, NOT a visible motte.

Fit strategy for the next session, in order:
1. READ `/tmp/mackenzie_212_sheet.jpg` (800 m aerial gridded; regenerate with `MACK_OUT=/tmp .venv/bin/python fit/src_mackenzie.py --sheet` if gone) + `mackenzie_212_relief.jpg`: locate (a) the hall/country house following the pale road NW of the box, (b) the full ditch course, (c) any polygonal earthwork at 800 m scale. Also OSM: `pipeline/finder_osm.py` can name mapped buildings (Shotwick Hall?) - the hall's position decides whether it can be the plan's hall at all (plan hall is ~265 px above the pentagon centre; at the pentagon's implied scale s≈0.22-0.25 m/px that is 60-70 m; if the house is 120 m+ away it is a different building and the hall pair is off the table).
2. TEST pair sets numerically (write a small /tmp script: solve the similarity from the pairs, print rotation/scale/residuals - do not eyeball): set A = hall (475,245)→house (if close enough), T-bottom-left (105,680)→mound candidate (E -41, N +45) or the C-band centre (E -12, N -3), T-bottom (640,760)→C-band south end, gate gap (315,755)→ditch gap/valley bend, small building (300,660)→(E -64, N -74) grass patch only if it is actually a building. Accept a set only if n>=4, residuals small, rotation near 0 (north-up) or a consistent ±90 (arrow convention), and every pair is an honest feature-to-feature match.
3. If an honest set passes `--gate`: `--write-doc` (crop = the drawn pentagon bbox, measure it exactly on the page first) then `--gate`. If no honest set passes (likely, given how faint the ground is): R2 route - a review item (201's queue if it exists) + `## Proposed changes` on the task; the identification stands on the documentary chain; box 3 stays unticked. NEVER move pairs to force a pass.
4. Then: `--dry` → stage for real → write `docs/lead_mackenzie.md` (prep §3 structure; section 3(e) must state the TRUE ground: faint earthworks, ditch system, no visible motte; section 4 the fit stats or the R2 note; 5 decision) → test per prep §3 (socket-blocking fixture, join, evidence.check, negative control, gate re-run, golden via `--golden`) → `.venv/bin/python -m pytest -q` green → tick boxes (box 3 last, on the committed doc) → one commit: staging rows + doc + lead + test + golden (module stays as committed).

**PAGE MAP (iter-59, still valid - page px of the raw 839x840):** pentagon (thick bank 30-40 px) vertices TOP (405,25), RIGHT (827,570), BOTTOM (620,835), LOWER-LEFT (30,690), LEFT (50,430); five C-towers: T-top (725,235) Ø130, T-top-left (185,195) Ø160, T-right ≈(795,560) (unconfirmed - re-read the BR corner), T-bottom (640,760), T-bottom-left (105,680); hall centre (475,245) box (430-525,185-305); small dashed building centre (300,660); west-pointing arrow, crossbar at (455,472); gate gap (300-335,745-765); no caption, no scale bar. Orientation: NORTH-UP per iter-58 geometry (the printed arrow is 90° off or marks something else) - re-derive from pairs, don't assume.

**PITFALLS still to add before committing (queued, NOT yet in PITFALLS.md):** (1) fit/: gridded sheets of a SUB-CROP must map px→lon/lat through the crop's OWN bbox corners (the 800 m box's corners on a 200 m crop = 4x-spread labels); `aw.corners()` returns [TL,TR,BR,BL] so to_merc(TL).y is NORTH. (2) archive.org hocr: `*_page_numbers.json` format v2 {identifier, format-version, confidence, pages:[{leafNum,pageNumber}]}; `*_hocr_pageindex.json` rows [leafStart, leafEnd, textStart, textEnd]. (3) EA WCS (environment.data.gov.uk LiDAR DTM) is flaky - 500s after ~15 requests in a session; space calls, retry later; an all-zero box = no data (real elevations here 4-25 m); it recovered between sessions on its own. (4) agent-viewed sheets larger than ~1200 px are shown shrunken - verify page measurements with dark-pixel censuses + quadrant crops, never one big shrunken view. (5) NEW: per-quadrant ImageOps.equalize/autocontrast on a 0.6 m aerial turns mown grass and roads into fake "white buildings" - before trusting a bright feature, sample raw pixel values (stone ≈ [150,135,110]-ish tan vs grass ≈ [120,155,125] green vs road tan).

If the network is down: `--gate`/`--check`/`--golden` work offline; the fit needs `data/raw/books/mackenzie/212.jpg` (persisted) + the Esri 800 m aerial (persisted, data/raw/aerial/) + EA relief (re-fetch when it answers). The 29 hand-tied plates and the 25 existing hand fits stay untouched.

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
