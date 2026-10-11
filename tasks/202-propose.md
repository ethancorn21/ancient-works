Status: open
# 202: Proposed point pairs — a placement a person finishes in a minute
Depends on: none
Touches: fit/propose.py, tests/test_propose.py

## Goal
Given a site and an old picture, produce the STARTING POINT for the fit: the anchor (scale bar and
north arrow where recorded, else the site centre) plus 3-5 pairs on drawn features. Since the GOAL
change of 2026-10-10 (point 2), the primary consumer is the model's fitting pass (203a/203b): the
model starts from this anchor and the few pairs, then looks at the fitkit sheet and records at least
four matched-feature pairs of its own. A review item (201) shows the same starting point to the human
when the model could not fit. Explicitly: a placement from a scale bar, a north arrow and the site
centre alone is a starting point, not a fit — it never goes to the gate as a fit and never becomes a
platefit on its own. Fitting by matching point pairs works (25 hand fits); the fully automatic
fitting bet (docs/autofit.md, 0/5) is not re-run.

## Acceptance criteria
- [ ] For a book plate with a scale bar and north arrow (the stage-B fields of data/books/index.jsonl:
      `scale_bar`, `scale_text`, `north_angle_deg`, `map_box`): the placement anchors the plate at the site
      centre with the recorded scale and rotation; 3-5 proposed pairs on drawn features of the plate
      (plan corners, straight lines), in page pixels.
- [ ] For a picture with no scale information (bird's-eye views, engravings): a coarse anchor (site centre,
      picture centre, scale from the picture size where possible) with 3-5 pairs flagged coarse — the human
      drag is expected to do the work (fixed landmarks carry these fits: roads, churches, river crossings,
      field edges).
- [ ] Pairs are page px → lon/lat exactly as a platefit doc stores them; the ground they refer to is the
      site's ground image (relief, or aerial for a site with no LiDAR — the fitkit `FITKIT_GROUND`
      convention). Pairs are proposed, never snapped.
- [ ] Test (no network): a fixed sample of (site, picture) pairs using in-repo ground (the six tracked
      hand-fit sites) → golden file of the proposed placements; sanity check in the golden file: a re-fit
      from the proposals of a hand-fit site lands within the hand fit's own residual range.

## Notes
- Import the shared helpers read-only: `pipeline/aw.py` (Mercator), `pipeline/plan_fit.py` (the solver, to
  evaluate your own proposals in the test).
- The proposal is deliberately crude where the evidence is crude: a scale-bar anchor beats a texture
  search, which is the bet that already failed.
- The model's own pair recording (203a/203b) supersedes this seed wherever the model does better; this
  output is never treated as the fit (GOAL point 2).

## Hand-over

Iteration 26 (agent c). Step done: prep §6.1 verification — re-measured the §2 table against current main
(all confirmed), fixed one wrong assumption (fudge row, below), and probed the cross-scan bridge (R4).
Nothing committed to fit/ or tests/ yet; no test written yet. Baseline suite state: not run this session
(prep says 12 passed; .venv exists and imports numpy/PIL fine).

### Prep assumptions checked against main (2026-10-11, iter 26)
- **WRONG: fudge's row.** The fudge site (data/sites/fudge/site.json; plate_scan = crop of Plate XXXIII
  No. 2, "ANCIENT WORK, NEAR WINCHESTER, INDIANA") corresponds to the stage-B row **n0203_2**
  (map_box [0.075,0.49,0.62,0.895], scale_text "SCALE 500 ft to the Inch.", blank_boxes []), NOT n0203_1
  as prep said. n0203_1 is panel No. 1 (Brush Creek, KENTUCKY — a different place entirely). Leaf n0203
  has three rows (_1/_2/_3). The other five sample pairs stand: (forthill,n0068_1), (highbank,n0126_1),
  (hopeton,n0129_1 — the main plan; n0129_2 is the inset, not it), (newark,n0161_1), (marietta,n0169_1).
  Note n0203_1 also has TWO scale_bar boxes (prep said one); irrelevant once fudge uses _2.
- **Small deltas (data moved since prep, not contract-relevant):** scale_bar None 15→26, map_box None
  29→40, scale_text None 371→382 (of 890). Everything else in §2 re-verified exactly: the 20 docs (9 book
  + 11 commons) and their recomputed m/px/rot/maxres (hembury 0.2354/0.6/33.7 … arbor-low 0.0363/−3.4/5.1;
  serpent doc has size:null AND src:null — src:null still takes the book branch in plan_fit.load_picture),
  the six old-style sites (all have tracked relief.jpg + data/sites/<id>/site.json + plate_scan.jpg),
  sites.json (384 sites, 17 lidar:false, 90 US, the six region-less), plans.json (1166 rows, same cols),
  summary.md ppi (squier_davis_1848 500, thomas_1894 360, fowke_1902 500, allcroft_1908 600, mills_1914 150;
  lapham_1855/squier_1851/whittlesey_1850 unrecorded → 8 books total in index.jsonl).
- **201 is MERGED now** (prep assumed open): fit/review.py is on main. Its seed items
  (data/review/alligator-effigy-mound-q4732645.ancientmonuments00squi_n0214_2.json + bibracte-q650053.json)
  already use the EXACT dict contract 202 must emit: {pairs [[u,v,lon,lat] 3-5, 1dp/7dp], coarse, ground,
  scale_m_px, rot_deg, scale_source, note}, and their notes say "202's propose_for replaces these pairs when
  it lands" (the replacement happens when 203a upserts — 202 itself must NOT write data/review/ or
  web/data/review.json: outside my Touches). fit/review.py never imports propose; R5 (contract drift) is
  resolved: keep propose_for(site_id, plan_id) -> dict with exactly those 7 keys.
- **data/raw/ is gitignored** (but present on this machine): full-page scans are NOT in-repo. The test
  therefore must NOT read data/raw at run time: hardcode calibrated coordinates into the test file with
  "calibrated <date>" comments (tracked files only: index.jsonl, plans.json, sites.json, site.json,
  plate_scan.jpg, platefits docs, golden).

### Cross-scan bridge (R4) — measured, forthill in depth
- The two forthill scans (LoC full page n0068.jpg 2844×4064; plate_scan.jpg 2570×3320) are the SAME ink
  (same labels/etching) but DIFFERENT physical copies: a 4-point procrustes fit on my eyeballed earthwork
  vertices (s=1.05, θ=0.7°) then a local NCC search (scale ±4%, rot ±1.5°, translation ±16) on the
  650×900 earthwork patch found NO match (NCC −0.02; best anywhere 0.19 on a 360×360 S-V-bend patch at
  scale 1.0). Side-by-side crops prove real local geometric difference: the S V-bend is longer/flatter in
  the full scan, steeper/shorter in plate_scan. A 4-point HOMOGRAPHY through the same eyeballed points is
  unphysical (implied scale 1.51 vs true ~1.06, 5th point off 116 px) and its wall overlay bulges off the
  drawn wall along the long sides: the distortion is not projective either. Whole-plate FFT NCC sweeps
  (scale 0.85–1.2) peaked at 0.24–0.37 (highbank best) — diluted, no clean win; fudge 0.036 (its
  plate_scan is a third-source crop, as prep said).
- **Conclusion:** the two copies differ by smooth-but-non-projective paper distortion. A global similarity
  or projective bridge is NOT clean (prep's Option A, as specified, fails). Eyeballed point picks from
  1.6–2× zoomed crops are only ±20–30 px and too coarse to condition a homography on a 1500-px span.
  The plate_scan crop also does NOT contain the plate's ruled frame (corner crops checked: blank; only a
  cut line at the bottom edge) — only the full-page side has frame corners (n0068 inner frame ≈
  (197,348)/(2640,3663)), so frame-pair calibration is impossible.
- **Next session DECISION (prep's A/B, now informed):** Option A as specified is out. Two viable shapes:
  (i) **A′ per-site calibrated similarity** fit by least squares over MANY correspondence pairs where the
  plate_scan side is exact (wall polyline points from site.json, ~35-155 pts) and the full-page side is
  auto-extracted (the wall is a white gap between two hatched lines: threshold the full-page earthwork
  region, extract the gap centerline, and match it to the wall polyline by a coarse-to-fine NCC
  registration that returns (s,θ,t) — no eyeballing; validate by the wall's overall length/aspect in both
  frames). Feasible but non-trivial code; do it in scratch first, commit only if it lands a consistent
  (s,θ,t) with small residuals for all six.
  (ii) **B metric-space checks** (prep's fallback, no bridge): scale ratio proposed-vs-hand within 50%
  (mind the frame: proposed m/px is full-page px, hand m/px is plate_scan px — compare via the cross-scan
  scale factor ≈1.06 eyeballed, or compare the proposed PANEL size in m vs the hand-fit earthwork bbox in
  m within 0.2–3×), rotation in the per-hint bands (prep §3.2: trusted hint ±15° or 70–110°; rejected hint
  ±35° or 70–110°), and panel-centre distance (site centre vs hand-fit placement of the map_box centre) ≤
  max(3×hand maxresid, 100 m, 1.0×hand panel diagonal — prep's borderline fix). For the centre term without
  a bridge use the hand fit's earthwork-centre as the panel-centre proxy (record the assumption).
  Leaning (ii) unless (i) proves cheap: the box only asks that the re-fit "lands within the hand fit's own
  residual range", and (ii) says that in metric space with honest envelopes. Decide, record in DECISIONS,
  then build.

### Scale reality (drives the design; measured this session)
- Printed scale ≠ true scale for the six: ratio-text@500ppi vs hand-fit truth gives truth/printed =
  forthill 2.26×, highbank 1.46×, hopeton 1.29×, newark 1.31×, marietta 1.20×, fudge 1.52× (implied ppi
  222–417, not constant → variable plate reduction; prep's "2–17×" was aztalan's 8–14× + a typo). So box 1's
  "recorded scale" anchor is 16–56% small vs truth, and box 4's literal reading (proposal lands within the
  hand fit's 2–20 m residual) CANNOT hold for a recorded-scale proposal (earthwork-position error = scale
  error × distance ≈ 100s of m). The sane reading (prep §3.2 envelopes) is what the test asserts. Do NOT
  "fix" the scale by peeking at site.json fits (circular: the proposal must be usable for sites with no fit).

### Exact next steps
1. Re-read this hand-over + prep/202.md §3-4. Decide A′ vs B (lean B) → DECISIONS entry.
2. Write fit/propose.py per prep §3.1 (stdlib-only; propose_for(site_id, plan_id) -> dict with the 7 keys;
   scale priority bar-box+text > ratio+BOOK_PPI (5 known books; the 3 unknown → coarse) > picture_size;
   rotation: north hint iff north_arrow and |θ|≤60 else 0, rejected hint kept in note; centre = map_box
   centre (page centre if none) → site lon/lat; pairs = 4 panel corners + panel centre, u/v 1dp, lon/lat
   7dp, in the row's size frame; ground = relief unless site lidar:false → aerial; deterministic; CLI
   python3 fit/propose.py <site> <plan id>... ). Add tests/golden/propose_202.json to the task's Touches line.
3. tests/test_propose.py + golden per prep §4 (sample: the six pairs as corrected above + the nine QID book
   docs + castle-rising c_70f937b71ae63d6a + mayburgh c_984782b9e35e8ded + bibracte aerial rule; exclusions:
   calleva scale (box over-covers, −73% measured) and whitley-castle rotation (118.8° hand fit); parse_scale
   table incl. the known-bad → None → coarse cases). Run .venv/bin/python -m pytest tests/test_propose.py -q
   then the full suite (baseline 12 passed).
4. Tick boxes in order; hand-over; commit per step.

Re-read: pipeline/plan_fit.py:similarity - the solver's convention (merc = a*(u - i v) + b; v down; k =
aw.ground_scale); fit/review.py:candidate_evidence - how source rows are looked up (book by id, commons by
c_+sha1(title)[:16] over the FULL title with File: prefix).
