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
**Iteration 62 (2026-10-11, agent a) - fit-pivot session. The pentagon on the ground is ROUNDED, not made of straight edges: all three "fit the edges" strategies failed this session (details in DECISIONS). NEXT: the corner-based fit - plan vertices <-> the 5 farthest ground points in the corner directions, similarity in Mercator, then the real fit_gate.gate() on the corner pairs.**

Findings this session (details in DECISIONS.md):
1. **poly3 (iter-61's written-not-run script) ran:** unconstrained pentagon-vs-region-boundary fit -> spurious local optimum: s 0.18, rot -16 deg, centre (E+144, N+80) = ~130 m from the true castle centre; the N and E corners land OUTSIDE the region. The blob boundary gives false per-edge support to shifted pentagons. Mask3 (120 m-disc flood) confirmed clean: 2.19 ha, the NE leak is gone, extent E -80..120 N -74..116 (clipped by the disc at the NE - the broken-belt zone - which is fine).
2. **poly4 (centre fixed at the region centroid (27.2, 9.4), rotation grid widened to 1 deg steps):** still spurious - best at the grid boundary (rot -29 deg), E corner outside. The blob supports a shifted pentagon at ANY rotation; the centre prior alone does not fix it.
3. **poly5 (straight-edge theta-sweep: project all boundary cells onto the perpendicular axis rho for each theta in 0.5 deg steps and look for tight bands):** ZERO runs at band <= 2.5 m AND at <= 6 m (n>=60, spread>=15 m). Diagnosis from /tmp/mack_boundary_scatter.png (2.5x scale, red cross = catalog point) and /tmp/mack_castle_zoom.jpg (a 210x200 m crop of the 0.25 m/px fetch, crop corner (460,316) px): the ground is a ROUNDED pentagon - gently bowed sides, rounded corners. The only prominent straight feature is the SW hedgerow (~113 deg, ~122 m: (-85,-29) -> (+27.5,-76.5)), which matches NONE of the plan's 5 edge angles (142.2/38.0/103.8/4.4/41.2 deg) within 8 deg. Also visible: the NE tangle (jagged fingers), a faint straight track NE of centre, and a NOTCH on the E side at ~(105-115, 15-30) (the candidate ground counterpart of the plan's gate gap).
4. **Boundary ordering is a dead end** (and is not needed for the next step): Moore trace breaks instantly (4 px - invalid initial state), a KDTree NN walk stalls at 202/4973 pts, radial-around-centroid zigzags in the west notch (max gap 31.8 m; the region is NOT star-shaped there).
5. **The merged 001 gate read (pipeline/fit_gate.py + docs/gate.md):** gate(pairs, transform=None) solves the canonical Web-Mercator similarity from the pairs (complex LSQ, exactly plan_fit.similarity: z = to_merc(lon,lat), w = u - iv, a,b; residual r_i = |a w_i + b - z_i| * k, k = cos(mean lat)) and scores THAT against the same pairs. REJECT if n<3 or sum(rho^2)<1 or med>45 or slope_o>0.145 or (slope_o>0.11 and io<-10). Held-out TRUE fits: med 2.5-31.9, 7/8 accept (cadbury's own fit rejects on its genuinely radial own-residual pattern). => if the ground pentagon is a true similarity of the plan pentagon, the corner-to-corner self-residuals are small and non-radial -> accept. If the shapes disagree, the residuals grow with radius -> reject -> R2 route.

**NEXT (iter 63) - the corner-based fit, write /tmp/mack_poly6.py** (copy the segmentation block VERBATIM from /tmp/mack_poly5.py: texture sd<14 -> 2x5 morph close -> 120 m disc -> flood from (800,800) -> hole-fill; region 2.19 ha, centroid (27.2,9.4), boundary = 4-neighbour cells):
1. Radial profile r_out(phi): 1 deg phi grid over 360 deg; per bin take the MAX radius of boundary cells within +/-1 deg (a ray from an interior centroid exits at the outer boundary - safe vs the west notch AND vs any holes: the max radius always wins; NO ordering needed).
2. Smooth (5-pt moving average), find local maxima; keep peaks with prominence >= 3 m and >= 20 deg apart, top 5 by prominence (PRINT all peaks + prominences for judgement - the NE fingers give small spurious peaks; the 5 pentagon corners should dominate). Corner point = the max-radius boundary cell within +/-3 deg of the peak phi.
3. Assignment (cyclic): plan vertices, page px of the 839x840 scan, north-up frame, PCTR = (386.4,510) = vertex mean: N (405,25) 87.8 deg, E (827,570) 352.3, S-SW (620,835) 305.6, W-SW (30,690) 206.5, NW (50,430) 166.7 (deg E/N from PCTR; clockwise order from N = N, E, S-SW, W-SW, NW). Ground peaks: clockwise from the one nearest 90 deg. Pair 1:1 in that order.
4. Fit in Mercator EXACTLY as plan_fit.similarity (pipeline/plan_fit.py:35): corner lon/lat = catalog point (lon -2.97608, lat 53.2272) + the E/N metres; to_merc(x,y) = (R*rad(lon), R*ln(tan(pi/4 + rad(lat)/2))), R = 6378137; invert to lon/lat numerically (e.g. Newton) or via pipeline/aw.py to_lonlat. Residuals * k = cos(lat0).
5. Call fit_gate.gate(pairs, transform=None) (pipeline/fit_gate.py, import with sys.path insert of pipeline/) on: (a) the 5-corner set; (b) 5 corners + the gate-gap pair (plan (317,755) -> ground E-side notch = local MIN of r_out in phi in [-10, 60] deg, ~(105-115, 15-30)); (c) the 4-corner set dropping the weakest corner (smallest prominence). Print per-corner residuals, the solved (s, theta), predicted pentagon centre vs the ring centre (80, -5), the predicted hall position (plan (475,245) - NO building on the ground there: record it, do NOT use it as a pair). Save overlay (boundary white, ground corners red, fitted plan pentagon green, hall blue, ring magenta, centroid yellow) + a result JSON.
6. JUDGE: clean accept if med <= ~15 m and slope_o <= 0.11 (compare avebury true: med 6.0, slope_o 0.035). An accept with slope_o 0.11-0.145 and io > -10 is usable but must be said in the lead doc. REJECT after honest corner-set choice -> R2 route (201 review item if it exists, else the lead doc says so + ## Proposed changes on the task; NEVER move pairs to force a pass).
7. Then the old iter-62 step 4, unchanged: `MACK_OUT=/tmp .venv/bin/python fit/src_mackenzie.py --write-doc <crop> ...` -> stage for real (`--dry` first) -> docs/lead_mackenzie.md (prep section-3 structure; 3(e) must state the TRUE ground: rounded-pentagonal grassed bailey earthwork (hedged, NW/S/SW sides the straightest) + hexagonal-motte ring at (80,-5) + crescent bank + the two 25 m ditches on the land (east) side, NO standing towers, NO standing hall, the named 'Shotwick Hall' is the Trelawney seat 2 km away; section 4 = the fit stats or the R2 note; 5 = decision) -> test per prep section 3 (socket-blocking fixture, join, evidence.check, negative control, gate re-run, golden via --golden) -> `.venv/bin/python -m pytest -q` green -> tick boxes (box 3 last, on the committed doc) -> one commit: staging rows + doc + lead + test + golden.

/tmp artifacts this session: mack_poly3.py (spurious result in mack_fit_result.json), mack_poly4.py, mack_poly5.py (theta-sweep; CONTAINS THE VERBATIM SEGMENTATION BLOCK TO COPY), mack_boundary_scatter.png (THE diagnostic image - rounded pentagon, E-side notch, SW hedgerow), mack_castle_zoom.jpg, mack_400z.jpg (THE 0.25 m/px 1600x1600 crop - still there), mack_castle_mask3.jpg. Re-fetch recipe for mack_400z.jpg if /tmp is gone: Esri AERIAL_URL (module constant in fit/src_mackenzie.py), bbox = centre mercator +/- 200/ground_scale(LAT), size 1600,1600 - deterministic, one request.

Failed approaches - do not retry (full records in DECISIONS.md): (a) unconstrained blob-boundary similarity fit (spurious centre 130 m off); (b) centre-constrained full (s,theta) grid fit (spurious at the grid boundary); (c) straight-edge theta-sweep on the mask boundary (no >=15 m sub-6 m bands exist - the pentagon is rounded); (d) ANY boundary ordering (Moore / KDTree-NN / radial all break on this region - not star-shaped at the west notch). numpy 2.x: np.cross on 2-D vectors raises ValueError - use the manual cross product (x1*y2 - y1*x2).

State: NO repo files touched this session (all work in /tmp scripts). Test suite: 59 passed at session start (not re-run; no repo change).

If the network is down: `--gate`/`--check`/`--golden` work offline; the fit needs `data/raw/books/mackenzie/212.jpg` (persisted) + the Esri aerials (persisted, data/raw/aerial/) + EA relief (re-fetch when it answers). The 29 hand-tied plates and the 25 existing hand fits stay untouched.

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
