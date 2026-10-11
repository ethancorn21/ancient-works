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

Iteration 28 (agent c). Step done: **tests + golden built and passing** (`tests/test_propose.py` 11 passed;
golden `tests/golden/propose_202.json` generated). Both files are NEW and **UNCOMMITTED** (harness saves
them; commit with the ticks). Full suite NOT yet run; boxes NOT yet ticked.

### What is on disk
- `fit/propose.py` — unchanged this session (committed in the driver's aeb433d after iter 27).
- `tests/test_propose.py` — 11 tests: parse_scale table (27 corpus cases, known-bad -> None); sample format
  (18 proposals: 3-5 pairs, px 1dp/lonlat 7dp, in-frame, coarse flag, scale_source, ground relief); no-snap
  (emitted u/v == recorded map_box corners+centre, or page corners+centre); aerial rule on bibracte
  (rule-level: **bibracte has NO plans row** - re-verified this session, 0 rows - so the aerial branch stays
  a rule check per prep, and the golden sample is 18, not the iter-27 count of 19); self-consistency
  (re-fit via plan_fit.similarity recovers the anchor: measured worst 5.2e-5 m/px, 0.0003 deg -> test
  tolerances 1e-3 m/px or 2%, 0.1 deg); QID-nine + old-style-six + commons-three sanity (Option B);
  byte-exact golden; CLI; 20 platefit docs byte-identical through the run. `--regen` mode regenerates the
  golden (run with .venv/bin/python). Import pattern: sys.path to fit/ and pipeline/; plan_fit imported in
  try/except (R6: if the venv is ever red, the 8 fit-dependent tests skip, the 4 stdlib ones run).
- `tests/golden/propose_202.json` — 18 sample proposals + measured sanity sections (qid/old_style/commons):
  hand m_per_px/rot/maxresid + measured dev/drot/dist/envelope + checks (null = not applied: coarse rows
  by design; exclusions calleva R2, marietta - see below). Regenerate only for an intended change.

### Measurements this session (against CURRENT data; all supersede iter-27 numbers where they differ)
- **Iter-27 hand-over typo:** fudge's S&D ratio is **0.2438** m/px (400 ft/500 ppi), not the 0.3048 listed.
- QID nine re-fit == prep table exactly (hembury 0.2354/0.6/33.7 ... arbor 0.0363/-3.4/5.1); all 9 frames
  identical to their row frame (serpent's doc size is its full_size [2884,4064]); centre dists 3.2-297.4 m
  all inside max(3*maxresid, 100, 1.0x panel diag) (arbor 107.3 <= 1329.5, the measured near-call, is fine).
- **NEW EXCLUSION - marietta** (old-style side-ratio check): its `plate.walls` is ONE 73-pt polyline spanning
  only 110 px (80.3 m at 0.7296 m/px) inside a 1535x2091 m panel -> side ratios 0.052/0.038, outside the
  0.2-3 envelope. The wall trace is a single wall segment, not the drawn extent (same honest-exclusion rule
  as calleva R2: record the measurement, never loosen the envelope). The other 5 old-style pass:
  ratios 0.48-1.54. Rotation: hopeton +33.7 in the rejected-hint 35 band, newark +95.4 in the 70-110 band.
- **Coarse rows are NOT held to the hand-fit scale** (prep's rule, applied in code+golden): serpent +198.7%,
  arbor +970.1%, aztalan +32.3% -> checks.scale null, not failures.
- **old-sarum COMMONS doc is a 90-degree class**: hand fit rot 86.1 -> drot -86.1 falls in the 70-110 band
  (not ±15) - the commons sanity uses the same band rule (`_band_ok`), no hint = trusted band.
- parse_scale: all 27 table cases behave as recorded in the iter-27 entry (incl. equals-form, compound
  mills, known-bad -> None). plate.walls shape: list of polylines, each a list of [u,v] points.

### Exact next step (ONE small step)
1. Run the full suite: `.venv/bin/python -m pytest -q` (expect 29: the 18 baseline of the driver's last note
   + the 11 new; no fixed ports, no writes outside project+temp - my tests are read-only + subprocess CLI).
2. Tick the four boxes in order in this file and set `Status: done`:
   - box 1 <- test_sample_format + test_no_snapping + test_self_consistency + golden (12 non-coarse book rows:
     6 S&D ratio + 6 Allcroft bar, anchored at site centre, rot from hint, 3-5 pairs in page px);
   - box 2 <- golden coarse rows (serpent/arbor/aztalan picture_size + 3 commons) + test_ground_rule_aerial;
   - box 3 <- test_no_snapping (pairs exactly on the recorded box geometry, px 1dp/lonlat 7dp as a platefit
     doc stores them) + ground assertions (18 relief + aerial rule = FITKIT_GROUND);
   - box 4 <- test_golden (byte-exact) + the three sanity tests = the Option B reading of "re-fit from the
     proposals lands within the hand fit's own residual range" (DECISIONS entry 2026-10-11).
3. Commit: `git add -A && git commit -m "202: tests + golden for fit/propose.py - the proposed starting point is pinned and sanity-checked"`.
4. If a box turns out to need a box-level reinterpretation, add `## Proposed changes` instead of ticking -
   but nothing found so far forces that (coarse-row deviations are the box's own "human drag does the work").

Re-read: tests/test_propose.py:build_sanity_qid - the doc-frame premise assert (doc size in (None, frame));
tests/test_propose.py:EXCLUDE_SCALE - marietta's exclusion assert (min ratio < 0.2) must stay true.
