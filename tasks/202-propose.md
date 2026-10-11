Status: open
# 202: Proposed point pairs — a placement a person finishes in a minute
Depends on: none
Touches: fit/propose.py, tests/test_propose.py, tests/golden/propose_202.json

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

Iteration 27 (agent c). Step done: **decided Option B** (metric-space sanity checks, no cross-scan
bridge; DECISIONS entry below the iter-26 BLOCKER) and **built fit/propose.py in full** (UNCOMMITTED -
the harness saved it; it is on disk). No test file yet. Suite when last run: **18 passed** (baseline
moved from 12 - merged work of other tasks added tests; no failures).

### fit/propose.py - what is on disk (stdlib-only; deterministic; CLI `python3 fit/propose.py <site> <plan id>...`)
- `propose_for(site_id, plan_id) -> {pairs, coarse, ground, scale_m_px, rot_deg, scale_source, note}`
  = exactly the 201 seed-item contract (pairs [[u,v,lon,lat]] 3-5, u/v 1dp, lon/lat 7dp; scale 4dp;
  rot 2dp). 201 is merged; fit/review.py never imports propose (R5 closed). 202 writes nothing
  (data/review/, web/data/review.json are outside Touches; 203a's upsert does the replacement).
- Scale: bar box in blank_boxes (box presence beats the boolean) + tick-list text -> span/bar_len_px
  (bar_len = max(box w,h) in the row's size frame - maiden/old-sarum bars are VERTICAL); ratio text at
  BOOK_PPI -> m/px; a bar box holding RATIO text (all six S&D rows: "SCALE N ft. to the Inch.") takes
  the ratio value, source "ratio" (note says the box holds the ratio text, not ticks); unparseable ->
  never a guess -> coarse: picture_size = max(size_m)/max(panel px). BOOK_PPI: 5 recorded from
  data/books/summary.md (squier_davis_1848 500, thomas_1894 360, fowke_1902 500, allcroft_1908 600,
  mills_1914 150); lapham_1855/squier_1851/whittlesey_1850 = None (no published ppi - web lookup
  2026-10-11 found nothing) -> their ratio rows (incl. aztalan "Scale 20 ft. to an inch.") coarse.
- Rotation: north_angle_deg iff north_arrow true and |deg|<=60, else 0 north-up with the rejected hint
  kept in note (hopeton 131.1 is the only rejected one in the sample). ground: site lidar false ->
  "aerial" else "relief". Pairs: 4 panel corners + panel centre (page centre if no map_box), in the
  row's size frame (book rows: plans size == full_size; serpent's index size null falls back to
  full_size). Anchor = the exact form plan_fit.similarity inverts: z = a*(w-w0)+z0, w = u - i v (v
  down), a = (m_per_px/ground_scale(lat0))*e^(i theta); Mercator one-liners inlined (R=6378137.0)
  because **pipeline/aw.py is NOT stdlib** (numpy/PIL/scipy at its top - the prep's "pure stdlib"
  assumption is wrong for current aw.py; task Notes say "import read-only" - the formulas are mirrored,
  aw.py untouched).
- `parse_scale(text) -> ("span", metres, unit) | ("ratio", metres_per_inch, None) | None`. Handles the
  measured 508-value corpus: tick lists ("0 100 200 300 Feet", fractions "0 1/2 1 mile", unit anywhere
  "0 100 feet 200 300", "... Scale of Feet"), single "N <unit>" = whole bar ("SCALE 500 FEET"),
  "N <unit> to a/the/an inch" (incl. "2 Ch. (352 Ft.)", "12 Rods 200 feet" -> FIRST quantity, "Forty",
  "1/2 Miles", "1000 ft. to Inch."), "Scale[:.] 1 in[.] = N <unit>" (incl. compound mills "1 in. =
  100 ft. 1/2 in. = 50 ft. 1/4 in. = 25 ft." -> first statement), "one inch equals three miles",
  "1/32m" (32 m/inch), "1/20 OF NATURE" (0.508 m/inch). Sweep result: 488/508 parsed (222 ratio,
  266 span), 20 -> None; known-bad ("0 1/4 1/2", "no. 10 to one inch", "scale miles", "Scale") all ->
  None. Fixed in-session: the equals-form regex had to accept "in" (not just "inch"), an optional colon
  after "scale", a dotted "in.", and compound statements. Optional polish only if a test needs it:
  reorder inch alternations to (?:inches|inch|in) in the equals + "to" regexes.

### Verified this session (scratch, .venv/bin/python)
- 19 sample proposals (six S&D rows, nine QID book rows, castle-rising + mayburgh + old-sarum-commons,
  bibracte): re-fit via plan_fit.similarity recovers scale/rot for ALL 19; scales match the prep
  exactly (hembury 0.1579 -33%, avebury 0.1886 -14%, badbury 0.1902 -20%, calleva 0.2469 -73%, maiden
  0.2263 -19%, old-sarum 0.1646 -23%, S&D ratios 0.1829/0.3048/0.3048/0.7925/0.6096/0.3048, aztalan
  0.2225 +32%, serpent 0.4921 ~3x, arbor-low 0.3883 ~10x); rot deltas all in the 70-110 or +/-15 bands
  (aztalan -75, maiden/old-sarum +90.6); bibracte -> aerial; two CLI runs byte-identical.
- **TEST-TOLERANCE CORRECTION (the prep's "within 1e-6" re-fit check CANNOT hold):** the emitted pairs
  round lon/lat to 7dp = ~0.11 m, so a re-fit of the EMITTED (rounded) pairs deviates from the anchor
  by ~1e-4 m/px absolute at most (measured, forthill; relative ~6e-4) and <0.05 deg rotation. Test
  tolerances: scale 1e-3 m/px absolute (or 2% relative), rotation 0.1 deg; the byte-exact golden test
  is the primary determinism check.

### Exact next step (ONE step: tests + golden, then tick the four boxes)
1. tests/golden/propose_202.json: the 19 proposals above (json.dumps indent=1 sort_keys=True per pair,
   keys sorted), plus a small per-site "sanity" section recording the measured hand-fit numbers
   (m/px, rot, maxresid) so the file is self-explaining. Regenerate only for an intended change.
2. tests/test_propose.py (no network, no server, no data/raw reads; .venv/bin/python): (a) golden
   byte-compare; (b) coarse/ground (commons/serpent/arbor-low/aztalan coarse:true, 3-5 pairs;
   bibracte aerial; six + QID relief); (c) self-consistency (pairs inside size frame, 1dp/7dp,
   re-fit within the corrected tolerances above); (d) parse_scale table (pin the corpus forms incl.
   known-bad -> None and the equals/compound forms); (e) all 20 platefit docs byte-identical
   before/after; (f) SANITY per DECISIONS Option B: same-frame QID nine - scale within 50% (minus
   calleva, logged R2), rot bands (trusted +/-15 or 70-110; rejected +/-35 or 70-110), centre distance
   site vs hand-fit map_box-centre <= max(3x maxresid, 100 m, 1.0x panel diagonal); OLD-STYLE SIX (no
   cross-scan bridge): (i) proposed panel physical size (m, from the proposal's own anchor) vs
   hand-fit earthwork bbox (m) per side within 0.2-3x, (ii) same rot bands, (iii) distance site
   centre vs hand-fit earthwork centre (the recorded proxy) <= same envelope. Hand fit from
   data/sites/<sid>/site.json plate.fit: affine M=[m00,m01;m10,m11], t, u0v0 with ground_metres(E,N) =
   M @ [u-u0, -(v-v0)] + t relative to the relief-image centre (= site centre) -> a_h = m00 + 1j*m10,
   b_h = t + M@[u0, -v0] as complex E + iN, true metres about site centre (proposal side: Mercator ->
   true metres via ground_scale). Earthwork centre/bbox from plate.walls polylines (plate-scan px)
   x fit m_per_px. maxresid: read site.json's fit fields (control_resid_m list or null_p99_m etc.)
   for each of the six and record which field you used. whitley-castle stays OUT of the rotation
   sample (118.8 deg hand fit).
3. Run `.venv/bin/python -m pytest tests/test_propose.py -q`, then the full suite (baseline 18
   passed; no fixed ports, no writes outside project+temp). Tick the four boxes in order; hand-over;
   commit per step.

Re-read: fit/propose.py:parse_scale + _ratio_m_per_inch (the equals-form fix: colon, dotted in.,
compound statements); fit/propose.py:propose_for (book vs commons branches); pipeline/plan_fit.py:
similarity (merc = a*(u - i v) + b; v down; k = aw.ground_scale); data/sites/fudge/site.json - the
plate.fit field shapes for the Option B checks.
