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
**Iteration 58 (2026-10-11, agent a) - fit session: plan + ground measured, ORIENTATION RESOLVED (page top = north); next: measure 3 anchors precisely, fit, gate.**

State now:
- Module `fit/src_mackenzie.py` (499 lines) committed in iter 57 + this session's two bug fixes (UNCOMMITTED, harness saves): (1) `zoom()` labeled the 200 m crop with the 800 m box extent (labels 4x too far apart) - now uses the crop's own mercator corners; (2) `sheet()` relief block treated the `dem_sources.source_for_bbox` name as a dict - now `src` is a string, DEM via `aw.fetch_dem(bbox,800,800)`. ReliED on both working: English LiDAR "ea" covers the whole box (640000/640000 px).
- FETCHED (data/raw, gitignored): `data/raw/books/mackenzie/212.jpg` (839x840) + `data/raw/commons/shotwick-castle-q7502621/e6e5490609414bb9.jpg`; desc re-verified: "Volume : 02, Page : 212, HMNTS 10369.v.7, W. Heinemann 1897". Esri 800 m aerial cached `data/raw/aerial/shotwick-castle-q7502621.jpg`; zoom aerial at `/tmp/zoom_shotwick-castle-q7502621.jpg`.
- NOTHING else written yet: no staging rows, no platefit doc, no lead doc, no test. Test suite was green at session start (driver note); nothing of mine under pytest yet.
- Task `Touches:` line UPDATED (committed with this file) to include `data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json` and `tests/golden/src_mackenzie_sample.json`.

**THE PLAN (measured from `data/raw/books/mackenzie/212.jpg` with a 25 px grid sheet; the drawing sits in the page's TOP-LEFT quadrant, rest blank):**
- bbox (crop for the doc): x0=10, y0=0, x1=425, y1=425 (page px; measure exactly on /tmp/page_fine.jpg recipe below).
- Towers (page px centres): T1 (195,55) full circle, top; T2 (345,130) full circle, upper right; T3 (350,265) horseshoe C open inwards, right; T4 (320,380) horseshoe C open upwards, bottom; T5 (75,340) horseshoe C open up-right, left. Edge T5->T1 is the long left edge; T1->T2->T3 the top/right; T3->T4 lower right; T4->T5 the bottom edge.
- Hall (thin lines, upper centre of the pentagon): centre (225,168), spans (135-330, 130-210) with an attached wing on its right.
- Small building (THIN lines, partly DASHED = conjectural): centre (155,340), L/T-shaped, lower left.
- GATE GAP in the bottom bank: (275,395) (between T5 and T4, near T4).
- The "north arrow": a long HORIZONTAL arrow (185-330, 255-270) with the arrowhead at the LEFT end and a small cross/monogram near (250,265). **/tmp/arrow_crop.jpg** = 4x zoom of (170,235)-(345,290) - READ IT: determine whether it is truly an N-arrow or an initials/W-mark; if it truly points left, the printed arrow is 90deg off the fit (see below) - record that in the lead doc.

**THE GROUND (catalog point (0,0) = lon -2.97608, lat 53.2272; 200 m crop at 0.25 m/px = ground px 800x800; 800 m box at 1 m/px):**
- **P2 = the MOTTE, not a tower**: ring/dark-ditch with bright raised centre at (E +0..+11 m, N -46..-48 m), ~40 m across -> lon/lat ~(-2.9761, 53.22679). Matches the C11 motte (40x20 m hexagonal mound, 25 m ditch - Gatehouse 212) far better than a 12 m tower.
- **A (hall candidate)**: bright building patch NW of centre, (E -30+/-10, N +59+/-5) - MEASURE PRECISELY next (it is the only bright stone feature near where the fit wants it).
- **B**: small bright speck (E -68, N -8). **C**: small bright speck (E +84, N -20) - NOT on the plan (the fitted map puts no plan feature near C; later building - do not use it).
- Bright broad band (the "crescent" bank / escarpment crest) wraps NE->E->SE of the motte from ~(N +55, E -33) to ~(N -45, E +100). Dark watercourse NW (the north flank ditch), dark valley SW (old Dee / south flank), dark tree belt west. The four OTHER tower positions have no clear visible ring on ground (grass or diffuse bright band) - the earthwork is mostly gone, consistent with the book: 1897 remains = "a large mound, supported by a huge earthwork of crescent form, and two deep entrenchments on the land side".

**ORIENTATION (the key finding):** the book's own text (see below) + geometry show the plan is printed **NORTH UP** (page top = north, right = east), NOT north-left as the arrow suggests. Proof: with the three reliable anchors (hall->A, small-building->B, T4->motte) the solved similarity under north-up gives rotation ~0deg, scale ~0.41 m/px, and puts the pentagon's SOUTH corner T4 due south on the motte and the hall (page upper centre = north, slightly west) on A; under north-left the same fit is rotated 90deg and puts T4 21 m off the motte with the hall's direction wrong. **Caveat: with exactly 3 pairs the fit is degenerate** (3 non-collinear points = 6 eqs vs 4 params: any similar triangle fits to ~0 residual under BOTH conventions - the orientation is discriminated only by which convention the anchor directions come out of, and by a 4th pair). So the final doc needs >= 4-5 pairs and the gate verdict on >= 4.

**BOOK EVIDENCE (fetched this session - V2 OCR, re-download recipe WORKS):** `https://archive.org/download/castlesofengland02mack/` files: `castlesofengland02mack_hocr_searchtext.txt.gz` (full OCR text), `castlesofengland02mack_hocr_pageindex.json.gz` (4-tuples [leafStart, leafEnd, textStart, textEnd]), `castlesofengland02mack_page_numbers.json` (format v2: {identifier, format-version, confidence, pages:[{leafNum, pageNumber,...}]}). Findings (verbatim in /tmp/v2_ocr.txt if still there, else re-fetch):
- Chapter (printed p.180): "S H O T W I C K ... THIS was one of the Norman forts erected by the Earls of Chester to protect their frontier from the Welsh, Shotwick being intended to guard the shallow channel of Dee in the Wirral Hundred. ... In the Harleian MSS. (2073) is a drawing and plan of this fortress by Kendle [Randle] Holme, as it appeared then, in a ruinous condition. **Its trace was a pentagon strengthened by six towers**, one of which, according to Camden, was five storeys high. **The wash of the tides, and the cultivation of the lands, have not quite obliterated these remains, those seen at present consisting merely of a large mound, supported by a huge earthwork of crescent form, and two deep entrenchments on the land side.**"
- Running head **"CHESHIRE 181"** appears immediately after the Shotwick chapter (next chapter = STOCKPORT, p.181): OQ-3 answered - the plate (leaf 212 = printed 164) sits in V2's CHESHIRE section; the book's index: "Shotlack, ii. 179, Shotwick, ii. 180" (both confirmed in OCR). Leaf 231 (Lancaster plate) = printed 183: the two plates are 19 pages apart in print, with the Shotwick chapter (180-181) between them.
- So: the p.212 plan IS a plan of Shotwick, drawn from the 1600 Randle Holme drawing (Harleian MS 2073) of the ruined fortress, and it shows FIVE towers although the book says SIX (one vanished; the plan's T1/T2 drawn as full circles vs T3/T4/T5 horseshoes = standing vs ruinous, or the sixth was entirely lost). Record all this in docs/lead_mackenzie.md section 3(e)/(f).

**EXACT NEXT STEPS (in order):**
1. Re-run `MACK_OUT=/tmp .venv/bin/python fit/src_mackenzie.py --sheet --zoom` (fresh /tmp sheets; /tmp files from this session may be gone). Make the fine sheets like this session's throwaway scripts: (a) page 2x with `m._grid(z,0,0,2,50,lambda v,_:str(v//2))` -> /tmp/page_fine.jpg (25 px grid); (b) 200 m aerial+relief at 900 px with `m._grid(c,0,0,900/800,40,lab)` where lab uses the 200 m crop's own mercator corners (x0,y0,x1,y1 = aw.site_bbox(LON,LAT,200,200), y-up) -> /tmp/fine_aerial.jpg /tmp/fine_relief.jpg (10 m grid, lon/lat labels 5 decimals). Read /tmp/arrow_crop.jpg (regenerate: page crop (170,235)-(345,290) at 4x).
2. Measure precisely on the 10 m grid sheets: A centre (bright building NW), B centre (speck W), motte P2 centre (bright centre of the ring). Record as lon/lat via the labels (or (E,N) offsets + aw.to_lonlat).
3. Page-side pairs (page px, the 839x840 frame - measure on page_fine): hall (225,168); small building (155,340); T4 (320,380); and for the 4th/5th pair use the crescent bank: a point on the plan's T2->T3 or T3->T4 edge (e.g. (350,200)) vs a point on the ground bright band NE of the motte (only if the band is clearly a bank there; the H_up fit predicts the T3->T4 edge runs (N +23,E +13)->(N -25,E 0) - check the band against that line on the 800 m LiDAR relief). Keep n = 4-5. Compute the doc's `crop` = the measured bbox (10,0,425,425).
4. `--write-doc <crop> u,v=lon,lat ...` then `--gate`. If REJECT: re-measure / re-pick (the three building/motte anchors are the strong ones); NEVER move pairs to force a pass. If still rejected after honest iteration: R2 route - review item + `## Proposed changes` on the task; box 3 stays unticked; the identification still stands on the documentary chain (which is now very strong: the book names the castle on the very pages before the plate, gives the pentagon+towers shape, and the Commons category = P373).
5. `--dry` then stage for real; write docs/lead_mackenzie.md (prep section 3 structure; fill section 3(d) county context from this session's OCR findings: CHESHIRE running head, Shotwick p.180, Stockport p.181, Lancaster plate 19 pages on, Oxford p.207 is V1; section 3(e) surviving ground with the motte/crescent/entrenchments book quote + what the fit showed; section 4 fit table with gate stats + the orientation finding + the 6-vs-5-towers note; section 5 decision). Note the 211-relevant facts: extras row staged with aerial_ok (the catalog row is NOT in extras.jsonl); doc id `shotwick-castle-q7502621.c_e6e5490609414bb9`; image at data/raw/commons/<site>/<plan>.jpg; the 800 m aerial is already cached at data/raw/aerial/<site>.jpg.
6. Test tests/test_src_mackenzie.py per prep section 3 (socket-blocking fixture as in tests/test_src_van_deventer.py; join assertions; evidence check over the staging file; in-memory negative-control row must FAIL; gate re-run on the committed doc; golden via `--golden`). `.venv/bin/python -m pytest -q` green; tick boxes (box 3 last, on the committed doc); rewrite this hand-over; one commit: module + staging rows + doc + lead + test + golden. Never run tests that bind fixed ports or write outside project+temp.

Notes: module `check()` treats a missing platefit doc as a problem (expected before step 4); `stage()` asserts the live file is still 839x840; `--gate` fails loud (exit 1) on REJECT; `--golden` normalizes `at`, `checked`, `date_commons`. If the network is down, --check/--gate on an existing doc/--golden still work, but the fit needs the fetched page (already in data/raw/books/mackenzie/212.jpg if the VM persisted). The 29 hand-tied plates and the 25 existing hand fits stay untouched.
