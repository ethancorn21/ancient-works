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
**Iteration 61 (2026-10-11, agent a) - ground-mapping session. TWO decisive findings: (1) THERE IS NO HALL ON THE GROUND - the hall pair is dead (see DECISIONS); (2) the castle's PENTAGON IS VISIBLE on the aerial as a grassed polygon with straight edges. NEXT: run /tmp/mack_poly3.py (written, NOT yet run) to fit the plan pentagon as a true similarity to the grassed region, then build the corner pair set for the gate.**

Findings this session (all in DECISIONS.md):
- **Hall = dead anchor, for a stronger reason than 'too far': there is no building at all.** No building anywhere within 400 m of the catalog point (cached 800 m Esri aerial + a fresh 400 m crop at 0.25 m/px, both checked). Wikidata's 'Shotwick Hall' = Q7502620, an English country house (P131 Puddington style) at (53.2413, -2.99426) = E -1212 m / N +1559 m (~2 km, the Trelawney seat the book's chapter ends with); its predecessor stood on a moated site 150 m further west (enwiki). The pale road along the west side of the grassed pentagon terminates without a house. The plan's hall + dashed building are lost structures of Holme's c.1600 view of the ruin. **The hall pair and the dashed-building pair are OFF THE TABLE.**
- **Castle layout (book V2 chapter, re-read this session + enwiki, both verified):** plan = Holme, Harleian MSS 2073, c.1600, 'as it appeared then, in a ruinous condition. Its trace was a pentagon strengthened by six towers, one of which, according to Camden, was five storeys high'. 1897 remains: 'merely of a large mound, supported by a huge earthwork of crescent form, and two deep entrenchments on the land side'. enwiki: built c.1093 (Hugh Lupus); 'an earthen HEXAGONAL MOTT with an outer bailey'; 'two large defensive ditches (25 m wide and 3 m deep) that became flooded at high tide'; on a promontory of two watercourses into the Dee; the Dee diverted south in the 18th c.; demolished 17th c. => pentagon = the bailey/enclosure (the grassed polygon); hexagonal motte = the 'large mound' (Gatehouse: 40x20 m, 25 m ditch); the two entrenchments = the 25 m ditches on the land (east) side.
- **The pentagon on the ground is visible:** in both aerials a grassed polygon ~150-180 m across centred ~10 m E of the catalog point, with STRAIGHT hedged edges on its NW, S and SW sides (irregular where the belt is broken to the NE); a concentric ring feature (mound + ditch) in its eastern half centred ~ (E +80, N -5) m; the pale road NNE-SSW along its west side.
- **Segmentation worked but leaks:** on this Esri tile the castle grass is DARK (mean RGB ~[32,61,34]) and colour-indistinguishable from the surrounding park grass (it is Trelawney parkland). Texture works: 9-px-window local sd < 14 = mown grass, >= 22 = tree; morphological close (2x5) then flood from (800,800) of the 400 m crop, hole-fill -> 4.2 ha castle region, BUT the flood LEAKS through a real gap in the NE belt into the NE park pasture (region runs to the crop edge). A fit on that leaked boundary gave scale 0.16 / rot +10 deg / centre (18.7,-24.7) - UNRELIABLE, do not use it.
- **Network notes:** overpass-api.de 504s (4 tries); overpass.kumi.systems DNS failure on this machine; nominatim.openstreetmap.org /search returns a 'Nominatim Demo' HTML page, not JSON; api.openstreetmap.org /api/0.1/map = 410 Gone. OSM building names are NOT reachable from here; Wikidata + Wikipedia APIs work. historicengland.org.uk and pastscape.org.uk are 403 to our UAs (use enwiki/Wikidata for the record text).

State: fit/src_mackenzie.py as committed (unchanged this session); test suite green at session start (not re-run - no repo change yet). No repo files touched this session.

/tmp artifacts (may be gone): mack_400z.jpg (1600x1600 at 0.25 m/px - THE working crop), mack_400z_view.jpg, mack_400centre.jpg / mack_NW.jpg / mack_800_aerial_sheet.jpg (800 m-box views), mack_castle_mask.jpg / mack_castle_mask2.jpg (flooded masks; the NE leak is visible), mack_boundary.json / mack_castle_boundary.json / mack_cbx.npy / mack_cby.npy (leaked boundary, metres E/N), mack_poly2.py (fit on the leaked boundary - superseded), **mack_poly3.py = THE next step: 120 m-disc-constrained flood (kills the leak) + true-similarity pentagon fit (one common translation C found by iterative median shifts, per-edge support >= 0.35 required), writes /tmp/mack_fit_result.json + /tmp/mack_castle_mask3.jpg**, mack_osm.py (the failed OSM attempt). Re-fetch recipe for mack_400z.jpg if /tmp is gone: Esri AERIAL_URL (module constant), bbox = centre mercator +/- 200/ground_scale(LAT), size 1600,1600 - deterministic, one request (same as module zoom() but half-width 200 m and 1600 px).

**NEXT (iter 62), in order:**
1. `ls /tmp/mack_400z.jpg`; if gone, re-fetch per the recipe. Run `.venv/bin/python /tmp/mack_poly3.py`. Read /tmp/mack_fit_result.json + /tmp/mack_castle_mask3.jpg (the mask shows whether the leak is gone).
2. Judge the fit: expect s ~0.18-0.25 m/px and a small rotation (north-up per the iter-58/59 geometry work) - if the best rot is far off, widen the grid (th step 1 deg) before trusting it. The printed ground corners must sit ON the visible straight edges (NW, S, SW first). For the predicted HALL position, check what is on the ground there: the ring/mound centre? plain grass? (the hall of a motte castle stood ON the mound - if the predicted hall lands on the ring centre that is a meaningful coincidence to record, but the mound is NOT drawn on the plan, so it cannot be a pair either).
3. Build the pair set from what survives: the pentagon corners (plan vertices -> ground corners from the mask3 boundary; the NW, S, SW edges are the strong ones - use at least those 3 corners, add NE/E corners only if the belt actually shows them) + possibly the gate gap -> the gap in the S-SW edge. n >= 4, every pair an honest feature-to-feature match, then `MACK_OUT=/tmp .venv/bin/python fit/src_mackenzie.py --write-doc <crop> ...` and `--gate`. If reject after honest iteration: R2 route (201 review item if it exists, else the lead doc says so + `## Proposed changes` on the task); NEVER move pairs to force a pass.
4. Then: `--dry` -> stage for real -> docs/lead_mackenzie.md (prep section-3 structure; 3(e) must state the TRUE ground: pentagonal grassed bailey earthwork with straight hedged edges + hexagonal-motte ring + crescent bank + the two 25 m ditches on the land side, NO standing towers, NO standing hall, the named 'Shotwick Hall' is the Trelawney seat 2 km away; section 4 = the fit stats or the R2 note; 5 = decision) -> test per prep section 3 (socket-blocking fixture, join, evidence.check, negative control, gate re-run, golden via --golden) -> `.venv/bin/python -m pytest -q` green -> tick boxes (box 3 last, on the committed doc) -> one commit: staging rows + doc + lead + test + golden.

**PAGE MAP (iter-59, still valid - page px of the raw 839x840):** pentagon (thick bank 30-40 px) vertices TOP (405,25), RIGHT (827,570), BOTTOM (620,835), LOWER-LEFT (30,690), LEFT (50,430); five C-towers: T-top (725,235) Ø130, T-top-left (185,195) Ø160, T-right ≈(795,560) (unconfirmed - re-read the BR corner), T-bottom (640,760), T-bottom-left (105,680); hall centre (475,245) box (430-525,185-305); small dashed building centre (300,660); west-pointing arrow, crossbar at (455,472); gate gap (300-335,745-765); no caption, no scale bar. Orientation: NORTH-UP per iter-58 geometry (the printed arrow is 90° off or marks something else) - re-derive from pairs, don't assume.

**PITFALLS still to add before committing (queued, NOT yet in PITFALLS.md):** (1) fit/: gridded sheets of a SUB-CROP must map px→lon/lat through the crop's OWN bbox corners (the 800 m box's corners on a 200 m crop = 4x-spread labels); `aw.corners()` returns [TL,TR,BR,BL] so to_merc(TL).y is NORTH. (2) archive.org hocr: `*_page_numbers.json` format v2 {identifier, format-version, confidence, pages:[{leafNum,pageNumber}]}; `*_hocr_pageindex.json` rows [leafStart, leafEnd, textStart, textEnd]. (3) EA WCS (environment.data.gov.uk LiDAR DTM) is flaky - 500s after ~15 requests in a session; space calls, retry later; an all-zero box = no data (real elevations here 4-25 m); it recovered between sessions on its own. (4) agent-viewed sheets larger than ~1200 px are shown shrunken - verify page measurements with dark-pixel censuses + quadrant crops, never one big shrunken view. (5) per-quadrant ImageOps.equalize/autocontrast on a 0.6 m aerial turns mown grass and roads into fake 'white buildings' - sample raw pixel values first (stone ≈ [150,135,110]-ish tan vs grass ≈ [120,155,125] green vs road tan). (6) NEW (iter 61): OSM is unreachable from this machine as of 2026-10-11: overpass-api.de 504, kumi.systems DNS-fail, nominatim.openstreetmap.org /search -> 'Nominatim Demo' HTML (not JSON), api.openstreetmap.org /api/0.1/map -> 410 Gone. Use Wikidata (P625) + Wikipedia for named places; historicengland.org.uk and pastscape.org.uk 403 our UAs. (7) NEW (iter 61): Esri World Imagery serves DIFFERENT tile dates for different zoom levels (the 800 m 1 m/px fetch is much darker than the 0.25 m/px fetch of the same ground) - colour thresholds calibrated on one fetch do NOT transfer to the other; calibrate per fetch. The castle grass is dark green and colour-indistinguishable from park grass: segment by texture (local sd), not colour.

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
