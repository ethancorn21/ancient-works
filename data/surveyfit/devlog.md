# Task 304 devlog (development record of the survey-sheet fit)

Reference for `tests/test_surveyfit.py` (the stub world and its measured outcomes) and for the
304 pre-registration in `docs/site_flow.md` ("development and smoke tests use only non-held-out
pictures of sheet-carrying sites, recorded here"). The method under development is
`fit/surveyfit.py`; every number below was measured on this machine, none chosen by inspection.

## The stub world (frozen constants, `tests/test_surveyfit.py`)

- Sheet: 400x400 px; its corners georeference a 2 km x 2 km box centred at (lon 2.0, lat 50.0)
  through the real `aw.corners`/`aw.to_merc` geometry (a square box, so the sheet's Web-Mercator
  similarity is exact).
- 14 feature glyphs on the sheet: a 7x2 grid, 25 px pitch in x / 30 px in y, centred at
  (195, 235) (close enough to the sheet centre that the plan frame holds the grid at every test
  rotation; far enough off it that the 302b half-box shift keeps exactly 8 glyphs).
- Plan: 320x320 px (the doc's size frame), the same 14 glyphs under the known true similarity
  `z = a*w + b` with `a = (M_PX/k0) * e^{i theta_d}` (the 302b anchor form), `M_PX = 4.0` ground
  m/px, `k0 = aw.ground_scale(50.0)`; the plan's north is `theta_d` deg clockwise of page-up.
  Plus 4 junk glyphs (the four 15/305 px corners) with no sheet counterpart, kept >= 25 px from
  every true centre at every test rotation.
- Glyph rendering: discs of sheet radius 3.5 px (the plan discs scaled by the true similarity),
  rasterised at 4x supersampling, box-downsampled, ink at coverage >= 0.3, black on white.
  The plan picture is a lossy JPEG q95; the sheet a lossy WEBP q95 (the real delivery paths).
- The stub matcher decodes the two sent images, resolves the sent panel's rotation by matching
  connected-component centroids against the expected glyph positions (2 deg candidate grid, a
  glyph counts as seen within `HIT_PX = 2.0` px, a recognisably rotated plan needs
  `ORIENTED_MIN = 8` seen glyphs), classifies the sheet (real / 302b-shifted / unknown), and
  answers with the true pairs of the band plus a fixed junk set
  (`JUNK_SEED = 304777`, 12 pairs). Band: all 14 glyphs at the true rotation, the first 6 one
  fine step (2 deg) away, none beyond; each returned plan-side point = the glyph's expected
  sub-pixel position in the sent frame + angular-quality jitter
  (`JITTER_SEED = 304778`, `JITTER_PX_PER_DEG = 0.6` px/deg, deterministic per (theta, i)) +
  intrinsic matcher wobble (`WOBBLE_PX = 0.25`, a separate deterministic stream per (theta, i))
  - a model of a good sub-pixel matcher's keypoint regression, not of a thresholded-blob
  centroid (the measured centroids stay the stub's glyph DETECTION only).

## Measured outcomes (all stub worlds; the suite is `tests/test_surveyfit.py`, 7 tests)

| world | rotation used | fit (score) | null (higher of the two) | margin | confidence | db (m) | da (m/px) | worst panel corner (m) |
|---|---|---|---|---|---|---|---|---|
| theta_d = 42, fixed rot = 42 | 42 | 0.5385 | — (no null) | — | — | 0.624 | 0.00273 | 0.797 |
| theta_d = 0, sweep | 0 | 0.5278 | 0.3923 | 0.1355 | 0.0715 | 0.461 | 0.00137 | 0.460 |
| theta_d = 6, sweep | 6 (recovered exactly) | 0.5278* | 0.3923* | 0.1355* | 0.0715* | 0.466 | 0.00230 | 0.597 |

*the null phase reuses the fit's chosen theta; the numbers are the theta_d = 0 world's (the
theta_d = 6 null run measures the same stub response families).

- Sweep call count: 30 coarse + 13 fine = 43 match calls per fit; the fine grid around a
  coarse best at 0 wraps (348..12) and re-sends duplicate payloads (the fine list dedups only
  within itself) - the stub counts them.
- Fixture pin (`data/surveyfit/fixture_match.json`, the test_gate pattern): the ideal
  north-42 response (14 true pairs + 12 junk) through the module's own `ransac` + `score`:
  26 pairs, 14 inliers, rms 3.6e-12, score 0.538462; the test re-runs the frozen core and
  requires exact equality (a drift in any constant fails it).
- Tolerances assert ~2x the observed worst: db < 1.3 m, da < 0.006 m/px, panel corners
  < 1.6 m, fit > null, margin > 0, confidence > 0, and 500-health is a method reason with no
  /match attempted.

## Per-disc centroid bias (why the stub does not return blob centroids)

The thresholded-blob centroid of a small disc is biased 0.3-0.9 px at any supersample: the
0.3 coverage threshold cuts the disc edge asymmetrically about a sub-pixel centre (a
threshold-edge effect, not quantisation). Measured (rasterise -> lossy save -> [plan] PIL
bicubic rotate -> connected-component centroid vs the expected position), full path:

| disc radius | 4x supersample | 8x supersample |
|---|---|---|
| 3.5 px (sheet and plan) | 0.33-0.68 px | 0.43-0.76 px (worse) |
| 5 px (plan-only probe) | 0.37-0.70 px | 0.49-0.88 px (worse) |
| 3.5 px integer-centred (sheet) | 0.329 px | 0.707 px (worse) |

JPEG q95 (plan path) and WEBP q95 (sheet path) add at most ~0.05 px on top. Consequence: a
trained sub-pixel regressor (what the real matcher returns) is far more accurate than a
thresholded blob centroid, so the stub answers with the expected sub-pixel positions plus the
two small noise terms above, while the measured centroids still drive detection. 8x
supersampling was tried and discarded (worse: it only changes which edge pixels land inside
the threshold).

## scipy 1.18.1 gotchas hit while building (full entries in `PITFALLS.md`)

- `ndi.center_of_mass` with a label-index array returns one (cy, cx) tuple per label (not two
  arrays) - `ValueError: too many values to unpack` when unpacking; the labelled form was hit
  in the stub's `_centroids`.
- `ndi.shift` requires the shift sequence to match the array rank - a 2-element shift on the
  RGB (rank-3) sheet image in `fit/surveyfit.shift_sheet_image` raised
  `RuntimeError: sequence argument must have length equal to input rank` on the first null
  run ever; the fix is a 3-element shift (0.0 on the channel axis).

## Live-service canaries (2026-10-12, against the real ELoFTR at 127.0.0.1:8091, all --no-null)

The service: `zju-community/matchanything_eloftr` on the RTX 5060 Ti. Three sheet-carrying
sites, each a full 30+13 sweep (none of the three has a trustworthy recorded north arrow; the
commons plans carry no scale bar, so no scale band). **The maiden row is the lead's held-out
document #14; it was canaried on the lead's explicit direction as a pipeline check, its numbers
were confirmation only (the lead's own raw smoke: 633 matches, 31 inliers, rotation 0.0 deg,
20-35-53 m at the three hand points), and no parameter was chosen or adjusted from any number
on this page, before or after the freeze.**

| site (doc) | sheet (px) | calls | seconds | best theta | pairs | inliers | rms (px) | score | confidence | placement (rot deg, m/px) | eyeball: reported panel corners on the sheet |
|---|---|---|---|---|---|---|---|---|---|---|---|
| maiden-castle-q1232816 (c_c20ff6b1f16d173d, held-out #14) | six-inch-1st.webp (1:10,560, 1842) 1066x1066 | 43 | 215.2 | 94 | 20 | 6 | 3.72 | 0.2048 | 0.0419 (null 0) | 99.18, 0.7276 | ~1 km NW of the hillfort (off) - the sweep's inlier-fraction score preferred a small tight cluster at 94 deg; at theta 0 the same run found 625 pairs / 31 inliers / rms 4.76 / score 0.0311, the lead's raw-smoke similarity (his 633 pairs: a few pairs drift between calls, GPU non-determinism) |
| barnard-castle-q4185811 (c_eacf8c673afcd863, not held-out) | six-inch-1st.webp (1:10,560, 1842) 533x533 | 43 | 44.4 | 216 | 3 | 3 | 3.02 | 0.7262 | 0.5274 (null 0) | 166.31, 0.2922 | on the hillfort's earthworks (landed) |
| avaricum-q281826 (c_d457524470ca0ab3, not held-out) | cassini.webp (no scale string; beats etatmajor.webp on the file-order tie) 1600x1600 | 43 | 98.4 | 0 | 9 | 3 | 3.28 | 0.2364 | 0.0559 (null 0) | -162.1, 0.0761 | on the hillfort's earthworks (landed) |

Per-call wall time scales with the sheet's PNG re-encode + payload: ~1.0 s (533 px), ~2.3 s
(1600 px), ~5.0 s (1066 px, the densest content). Confirmed live: sheet loading through
`load_sheet` (scale-denominator selection, ties by kind then file), the scale-band absence
(note lines), the sweep, RANSAC, the georeference carry-over and the panel corners.

Observations recorded, not tuned from (all three docs are inputs the 304 method saw exactly as
the one run will use them, except the maiden one-shot measurement which happens after the
freeze): (a) the inlier-fraction score can prefer a small tight cluster over the correct
rotation with many inliers (maiden); (b) a 3-pair similarity scores 0.73 (barnard) - the
frozen score has no minimum-pair floor, so the null and the confidence threshold are what
separate a good placement from a lucky 3-pair one; (c) the matcher's pair count drifts a few
percent between calls of the same images.

## The freeze

`fit/surveyfit.py` is frozen as of commit 737508d (restated in the 304 section of
`docs/site_flow.md`, which is amended at the freeze commit and at the run only). The stub
suite is frozen as it stands (the lead, 2026-10-12): a test that runs end to end is enough;
it proves the plumbing, not a reproduction of the real matcher's bias.
