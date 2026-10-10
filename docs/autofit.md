# Auto template + auto fit: does it replace hand tracing?

Test of the bet behind PLAN.md phase 2 ("no cap on full-depth sites"): the wall template can be extracted
automatically from a plate's ink and fitted from a rough seed, with no hand-traced walls and no hand blank boxes.

## 1. Pre-registered criterion (written 2026-10-10 before any fit was run; not to be changed)

Sites: fudge, hopeton, newark, forthill, highbank. Marietta is excluded (urban, fitted from control points only).

Reference: the hand fit stored in `data/sites/<id>/site.json["plate"]["fit"]["affine"]` (for the warped sites,
hopeton and newark, this is the global similarity before the per-feature warp, which is what an auto global fit
is comparable to). It is itself a fit to relief, not ground truth.

**Seeds.** 8 seeds per site from `numpy.random.default_rng(20261010)`, drawn per site in the order listed above.
Each seed perturbs the hand fit:
- scale: hand m/px times U(0.75, 1.25) (scale bar misread or missing);
- rotation: hand rotation plus U(-20, +20) deg (north arrow misread);
- centre: the ground position of the plate-image centre moved by a point drawn uniformly over a 150 m disc
  (vague site coordinates).

The fitter only sees the seed, never the hand fit. Its search window is fixed relative to the seed:
rotation seed +-25 deg, scale seed x 0.74 .. x 1.36, plate-centre shift +-200 m (so every perturbation is inside
the window with a margin).

**Per-seed pass** requires all three:
1. RMS distance between the four plate-image corners mapped by the auto fit and by the hand fit
   <= max(15 m, 2% of the plate-image diagonal in ground metres at the hand-fit scale).
   Diagonal, not long side, because corner error is about half-diagonal x angle, so 2% of the diagonal matches the
   2 deg rotation tolerance (a pure 2 deg error gives 1.75% of the diagonal).
2. |auto rotation - hand rotation| <= 2 deg, rotation measured as atan2(M[1,0], M[0,0]) exactly as fit_plate.py
   reports it.
3. Auto-fit score > null p99. Score = fit_plate's: median over template points of (relief on the line minus the
   higher of the two sides side_m away), LRM clipped, modern features and hydro-flattened water masked.
   Null = 1000 random placements of the same auto template at the auto-fit scale, rotation U(-180, 180) deg,
   centre shift U(-1/3, +1/3) of the site box (as fit_plate.py, but 1000 draws instead of 300 because it is a pass bar).

Tolerances computed from the hand fits (code: `pipeline/autofit.py`, printed values pasted here):

| site | plate px | hand m/px | hand rot deg | plate ground m | diagonal m | corner RMS tol m |
|---|---|---|---|---|---|---|
| fudge | 1580 x 1500 | 0.4633 | 1.81 | 732 x 695 | 1009 | 20.2 |
| hopeton | 1950 x 3060 | 0.3939 | -33.70 | 768 x 1205 | 1429 | 28.6 |
| newark | 2250 x 3150 | 1.0395 | -95.39 | 2339 x 3274 | 4024 | 80.5 |
| forthill | 2570 x 3320 | 0.4134 | -6.17 | 1062 x 1373 | 1736 | 34.7 |
| highbank | 2350 x 3320 | 0.4446 | -1.73 | 1045 x 1476 | 1808 | 36.2 |

**Site pass:** at least 6 of 8 seeds pass. **Bet holds:** at least 4 of 5 sites pass. Anything less is a fail.

## 2. Pre-registered protocol

- **Input to the extractor:** the same crop as `plate_scan.jpg` (same pixel frame, so corners are comparable) but
  rebuilt from the leaf scan and the spec's crop box *without* the hand `blank` boxes (forthill, highbank and newark have them;
  hopeton has none). Fudge has no spec; its `plate_scan.jpg` has no blanked areas (section, title and lettering are still on
  it), so it is used as is. The crop box itself is still hand input. The plan gives that job to Qwen page triage;
  here it is an accepted precondition, not a solved problem.
- **Relief settings:** each site's existing relief knobs are used (forthill: lrm_radius_m 8, clip_m 3, side_m 12;
  all others default 24 / 1 / 20). This is relief-side hand tuning that stays in the pipeline; it is flagged, not
  solved.
- **Control run:** the hand-traced walls go through the same wide-range fitter from the same seeds, scored by the
  same criterion. This separates "the extractor failed" from "the fitter cannot handle seeds this rough".
- **Leakage:** these five sites are both the development set and the test set. The extractor's parameters are
  frozen by looking at the extracted ink maps only (never at fit results or at overlap with the hand traces) before
  the first fit run, and the frozen configuration is written in section 3 before that run. After the first run,
  bug fixes are allowed; any parameter change is labelled exploratory and reported separately. The verdict is
  stated on the frozen run.
- **Qwen boxes:** if used, they are part of the frozen configuration; the run without them is also reported.

## 3. Frozen configuration (written before the first fit run on the five test sites)

Only marietta (excluded) and synthetic random lines were used to smoke-test the fitter before this point.

**Extractor** (`pipeline/autowalls.py`, parameters in `P`), tuned by looking at ink maps only:
1. Ink level 0..1 from grey (paper = 85th percentile, ink = 1st percentile). A 20 px crop margin is zeroed
   (plate border lines).
2. Qwen boxes (see below) of kind title, north_arrow, scale, section, frame are zeroed. Text boxes are not used:
   labels are written along and across walls ("1320 ft", "Parallels 2400 ft long"), so blanking them cuts walls.
3. Frangi ridge filter (bright ridges on the ink map), sigmas 4, 6, 9 px, beta 0.5, gamma fixed at 0.013.
   Dropping sigmas 2-3 is what removes the engraver's ground-tint dashes, thin field lines and hachure strokes.
4. Threshold 0.25, skeletonise, drop pieces under 50 skeleton px or 50 px bounding box.
5. Orientation coherence of the centre lines over a 25 px window; pixels under 0.6 are dropped (junctions,
   lettering, wiggly streams), then the length filter again.
6. Normal = dominant gradient direction of the blurred centre line (structure tensor, 4 px window). About one
   skeleton pixel in two becomes a template point, weight 1.

Known junk that survives (visible in `data/autofit/<id>_walls.jpg`): rivers and creeks drawn as smooth bands
(fudge's White River and Sugar Creek, Fort Hill's Brush Creek, Newark's Raccoon Creek and the Ohio Canal), pond
rims. Forthill's walls come through as the two outlines of the unshaded wall band. No geometric cue I found
separates a smooth river bank from a wall; that is left to the fitter.

**Qwen** (Qwen3.8-27B via `llm.ask_json`, tunnel up on 2026-10-10): one call per plate asking for boxes around
title, text, north arrow, scale, sections and inset frames, 0-1000 normalised. The convention was verified by
drawing the boxes on the plates: they sit on the elements. Fudge, hopeton and highbank answered in 8-14 s.
Newark and forthill looped until max_tokens (517 s and 349 s, boxes marching off the page); rule: one retry with
a smaller image (1280 px) and "at most 40 boxes", which answered in 57-59 s. Hopeton's answer labels the real
300 ft small circle as "scale", so that wall is blanked: a real cost of trusting the boxes.

**Fitter** (`pipeline/autofit.py`):
- Objective = mean over template points of max(contrast, -0.2 m), contrast as fit_plate (line minus the higher
  side, side_m away, LRM clipped, modern and water masked); at least 50% of points must land on valid relief.
  The -0.2 m floor stops junk lines in stream channels from outweighing walls. Selection uses this objective;
  the median score in criterion 3 is computed afterwards.
- Coarse: for every (rotation, scale) on an absolute grid (2 deg, 4% log steps) the objective for all shifts at
  once by FFT correlation of the rendered template against 8 per-direction contrast images on a 4 m grid
  (4.4 m on newark). Run once over the union of the 8 seed windows; each seed keeps only peaks inside its own
  window (rotation +-25 deg, scale x0.74-x1.36, centre +-200 m). Top 3 peaks per map per seed, then the 8 best
  distinct candidates (apart by >4 deg, >8% scale or >30 m).
- Refine each candidate by pattern search on full-resolution relief (steps 1/0.5/0.25 deg, 2/1/0.5% scale,
  4/2/1 m) and keep the best objective.
- No per-feature warp (only if the global fit works).

**Planted-signal check of the fitter** (synthetic relief: 0.4 m ridges along 25 random lines under a known
transform, plus 0.1 m smoothed noise, seeds drawn as pre-registered): highbank grid with its real mask, 4/4 seeds
recovered at 1.5 m corner RMS and 0.02 deg; newark grid (1.1 m px, mask off because 42% of that box is masked and
the random lines landed mostly on it) 4/4 at 4.3 m and 0.11 deg. So the window, index and sign handling work.

**Runs:** primary = auto template with Qwen boxes (`results_auto.json`); also auto without Qwen
(`results_auto_noqwen.json`) and the control with the hand walls (`results_hand.json`), same seeds and fitter.

## 4. Results of the pre-registered runs

Contact sheets: `data/autofit/<id>_sheet.jpg` (left: relief, hand fit in blue, the 8 auto-fit plate frames in thin
red and the auto template under the median seed's fit; right: what the extractor kept). Raw numbers:
`data/autofit/results_<tag>.json`, logs `data/autofit/run_<tag>.log`. Tables printed by
`pipeline/autofit_sheet.py <tag>`.

Seeds passing out of 8 (a site passes at 6/8):

| run | fudge | hopeton | newark | forthill | highbank | sites passing |
|---|---|---|---|---|---|---|
| **auto + Qwen boxes (primary)** | 0 | 0 | 0 | 0 | 0 | **0/5** |
| auto, no Qwen | 0 | 0 | 0 | 0 | 0 | 0/5 |
| hand walls, same fitter (control) | 8 | 0 | 0 | 0 | 0 | 1/5 |

Primary run in detail:

| site | tol m | pass | corner RMS m, median of 8 (range) | rot error deg, median abs | median contrast at fit / null p99 | objective at fit / at hand fit |
|---|---|---|---|---|---|---|
| fudge | 20.2 | 0/8 | 132 (132-336) | 8.2 | 0.044 / -0.036 | 0.116 / 0.037 |
| hopeton | 28.6 | 0/8 | 369 (292-559) | 25.3 | -0.011 / -0.038 | 0.066 / -0.030 |
| newark | 80.5 | 0/8 | 382 (263-583) | 9.4 | no valid fit | no valid fit |
| forthill | 34.7 | 0/8 | 39 (all 8 the same) | 2.4 | -0.160 / -0.117 | 0.337 / 0.167 |
| highbank | 36.2 | 0/8 | 406 (295-589) | 16.3 | -0.017 / -0.046 | 0.032 / -0.037 |

**Verdict: FAIL.** 0 of 5 sites, 0 of 40 seeds. The bet as stated (auto template + fit from a rough seed replaces
hand tracing) does not hold on these plates.

What the numbers say, site by site:
- **fudge** (the easiest plate: one rectangle, hand control 8/8 at 4 m): the auto template is 72% junk by point
  count (White River and Sugar Creek banks, drawn as long smooth lines; the dashed wall pieces are the minority).
  At the hand fit it scores 0.037; the fitter finds placements scoring 0.12 by laying the river lines on other
  relief. Pure extraction failure.
- **hopeton**: auto fits are 300-560 m and up to 42 deg off. The hand control also fails (154 m, scale x1.2):
  this plate drifts (it needed the warp), so its global similarity is not where the objective peaks.
- **newark**: no valid placement at all. 42% of the 4.4 x 3.8 km box is masked (city), and the auto template
  spreads over the whole plate (walls under the town, canal, creeks), so fewer than half its points ever land on
  open ground. The "fits" are the seeds. The null is undefined here too (fewer than 100 of 1000 random placements
  are valid).
- **forthill**: the closest miss, and visually a decent fit: all 8 seeds land on the same placement, 39 m corner
  RMS (tol 34.7), 2.4 deg (tol 2.0), scale within 1.3%. It still fails all three conditions, criterion 3 because
  the median is dragged down by Brush Creek and the stream lines. The hand control fails here as well (112 m,
  scale x0.89): comparing the two on the relief, the hand fit sits on the east and south walls and the control fit
  on the west wall. The plate needs a warp; no single similarity is right everywhere.
- **highbank**: auto fits 300-590 m off. The hand control also fails from wide seeds (scale x1.2-1.27): the
  enlarged circle sits on the terrace scarp, which scores like a wall.

Three findings that matter beyond this test:
1. **The search works; the score has false peaks.** In every failed control seed the fitter found a placement
   that scores higher than the hand fit (e.g. newark 0.46 vs 0.34, forthill 0.75 vs 0.54). The search works; over
   a window this wide the relief score has false peaks (terrace scarps, one dominant feature such as Newark's Great
   Circle leaving rotation free, partial fits of distorted plates). fit_plate.py works because each site got a
   hand guess, a 3-8 deg rotation limit, a 60-160 m shift limit and sometimes control points.
2. **The null check cannot accept or reject fits.** Of the 40 primary seeds, 21 wrong fits beat null p99 (31 of 40
   in the hand control). Random placements are not a fair null for a searched fit; the plan's "contact sheet
   against a null distribution" step needs a search-matched null (the best score the same search finds with a
   scrambled template or on a shifted DEM).
3. **The extractor finds the walls but cannot tell them from rivers.** 68-92% of the hand-traced walls have auto
   points within 15 px, but only 21-30% of the auto points are near a hand-traced wall (a lower bound: untraced
   real walls count as junk). Qwen boxes barely change this (1-2 points of precision): they remove sections,
   arrows and titles, which the length filter already mostly dropped. The junk that matters is water.
   The coarse candidates show where it bites: on fudge the hand-fit basin was among the 8 coarse candidates for
   4/8 seeds and the junk-driven placement still scored higher after refinement; on hopeton, newark and highbank
   it never surfaced (0/8); on forthill it did for 8/8, which is why that site came close.

Caveats: the five sites were dev and test set at once (extractor tuned by eye on these plates before the runs).
The corner-RMS reference is the hand global similarity, which on drifting plates (hopeton, forthill, newark) is
one compromise among several; the hand control failing there shows the criterion is strict for those plates, not
that the auto fits were secretly right (they are hundreds of metres off on four sites). For newark the hand-run
null p99 was computed before the empty-null fix from fewer than 100 valid draws; it changes no pass/fail.

## 5. Exploratory runs (after the verdict; parameters chosen after seeing results, so not evidence of a pass)

`pipeline/autofit_explore.py`, results in `data/autofit/results_x_<seeds>_<template>.json`. Same fitter.
"Tight" seeds: scale x U(0.95, 1.05), rotation +-3 deg, centre within 50 m (a scale bar and north arrow read
correctly, coordinates good to 50 m), window +-6 deg / x0.92-1.09 / +-80 m, about what fit_plate.py was given by hand.
"Oracle" template: the auto template's points within 15 px of a hand-traced wall, i.e. perfect junk rejection,
as if a person clicked the wall pieces (uses the hand traces: an upper bound). "Qwen pieces": the auto template
split into 465 pieces over the five plates; each piece shown to Qwen as a crop with the piece traced in red and
labelled wall / water / road / hill / other (`pipeline/autofit_pieces.py`); pieces labelled wall are kept.

Seeds passing out of 8:

| run | fudge | hopeton | newark | forthill | highbank |
|---|---|---|---|---|---|
| hand walls, tight seeds | 8 | 0 | 0 | 0 | 6 |
| auto, tight seeds | 0 | 0 | 0 | 0 | 0 |
| auto oracle pieces, wide seeds | 6 | 5 | 0 | 0 | 0 |
| auto oracle pieces, tight seeds | 8 | 8 | 0 | 0 | 1 |
| auto Qwen pieces, wide seeds | 6 | 0 | 0 | 0 | 0 |
| auto Qwen pieces, tight seeds | 8 | 0 | 0 | 0 | 0 |

Qwen piece labels (point recall = share of auto points near hand walls that Qwen kept; precision = share of
kept points near hand walls, a lower bound because untraced real walls count against it):

| site | pieces | labelled wall | labelled water | point recall | point precision (all auto points) |
|---|---|---|---|---|---|
| fudge | 55 | 27 | 26 | 0.98 | 0.54 (0.28) |
| hopeton | 60 | 52 | 3 | 1.00 | 0.34 (0.29) |
| newark | 137 | 73 | 26 | 0.97 | 0.39 (0.21) |
| forthill | 132 | 88 | 44 | 0.92 | 0.33 (0.27) |
| highbank | 81 | 70 | 10 | 0.67 | 0.25 (0.30) |

Readings:
- **Junk rejection is the binding problem for the auto template.** Even from tight seeds the raw auto template
  passes 0/40. With the junk removed by hand selection, fudge and hopeton pass 16/16 from tight seeds and 11/16
  from the pre-registered wide seeds.
- **Qwen piece labels are not good enough yet.** They fix fudge (it calls the rivers "water": 6/8 wide, 8/8
  tight, at 19-20 m against a 20.2 m tolerance) but call almost every piece on hopeton and highbank a "wall", so
  those still fail. On forthill the Qwen-pieces fit is 32 m and 1.9 deg (inside both tolerances) but its median
  contrast stays under null p99 (-0.121 vs -0.106), so it fails criterion 3.
- **Seed quality matters even with perfect walls.** Highbank's hand walls go from 0/8 (wide seeds) to 6/8 (tight).
- **Newark and Fort Hill fail every configuration**, including hand walls from tight seeds that start 20-60 m from
  the reference: the fitter walks away to 105-108 m because a single similarity cannot fit a drifting plate (Newark
  needed control points and a per-feature warp; on Fort Hill hand and control fits each fit different walls).
  Corner RMS against a global hand similarity is the wrong yardstick for such plates; a per-feature fit and a
  wall-position metric would be needed to judge them.

## 6. What would be needed (evidence above, not hope)

1. **A per-piece keep/drop step on the extracted ink.** Required: the raw template fails even from good seeds.
   A person clicking wall pieces (the oracle) works on the two undistorted plates; Qwen's labels as prompted here
   only work where the junk is obviously water. So: semi-automatic. The extractor proposes pieces, a person
   (or Qwen, then a person correcting it) keeps the walls. That replaces tracing with clicking, not with nothing.
2. **Seeds about +-3 deg, +-5%, 50 m.** Seed roughness alone is shown on highbank: its hand walls fail from the
   pre-registered +-20 deg / +-25% / 150 m seeds and pass 6/8 from tight ones. Hopeton, newark and forthill fail
   the hand control from tight seeds too, for distortion (item 3), so seeds are not their problem. Either read the scale bar and north arrow reliably (Qwen reading them is untested) or
   click 2-3 control points per plate, as was done for Newark, Fort Hill and Marietta.
3. **Per-feature fitting for drifting plates** (hopeton, newark, forthill), seeded from the global fit, as
   fit_plate.py already does with its warp model.
4. **A search-matched null for accept/reject.** Random placements are beaten by 15-31 wrong fits out of 40 in
   every run, so "above null p99" accepts wrong fits.
5. **Qwen reliability**: the box call looped to max_tokens on 2 of 5 plates (6-9 minutes each) and needed a
   retry rule; it labelled a real wall ring as a scale bar.

Net: the "no cap" bet does not hold. A cheaper semi-automatic pipeline (auto ink + clicked pieces + clicked or
read seeds + existing per-feature warp) is supported by the oracle runs on the two undistorted plates only;
that is 2 plates, chosen by me, so it is a lead to test on new plates, not a result.
