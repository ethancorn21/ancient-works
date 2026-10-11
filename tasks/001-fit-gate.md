Status: open
# 001: The fit gate, measured on held-out hand fits
Depends on: none
Touches: pipeline/, tools/, docs/gate.md, tests/

## Goal
A program decides whether a proposed fit of an old drawing (point pairs, or a placement found by a search) is good
enough to show on the map without the human looking at it. It must be measured on the existing hand fits before it
is trusted: the hand fits are the only fits known to be right. Everything the gate does not accept goes to the review
queue (GOAL.md point 1), so a strict gate is fine; a gate that accepts wrong fits is not.

## Acceptance criteria
- [ ] `docs/gate.md`, written and committed BEFORE the gate is first run on the held-out set, says: which hand fits
      are held out (at least 8, chosen by a recorded random seed, never looked at while building the gate), the rule
      the gate applies, its thresholds, and how a wrong fit is made for the test
- [ ] Wrong fits for the test are made from each held-out hand fit at least these ways: moved 60 m, turned 10
      degrees, scaled 15%, and the best placement the same search finds on a different site's ground. On these the
      gate accepts at most 1 in 20
- [ ] On the held-out hand fits themselves the gate accepts at least half (if it cannot, `docs/gate.md` says so with
      the numbers, and the project sends every fit to the review queue instead)
- [ ] The results table is in `docs/gate.md`, with the command that reproduces it, and a test re-runs it

## Notes
- `docs/autofit.md` section 4, finding 2: random placements are not a fair null; a searched fit beats them easily.
- The numbers here are the owner's intuition; settle a different number only with evidence of what he would notice.

## Hand-over (iteration 3, agent c)

**Where I am.** All six image-structure metric experiments (spikes 1-6) FAILED to separate the four wrong-fit
types on dense old maps (numbers in DECISIONS.md). The gate is now pivoted to PURE GEOMETRY on the pair set:
magnitude of the solved-transform residuals (catches 60 m move + cross-site) plus a residual-vs-radius pattern
(should catch 10 deg / 15% scale). No code in the repo yet; all evidence is in /tmp + this file.
`docs/gate.md` is NOT written yet and must be committed BEFORE any held-out number is looked at.

**The 20 hand-fit docs** (`data/db/platefits/*.json`, read-only): 19 sites, old-sarum has 2. (The old hand-over
said 21 - miscount.) n_pairs is 3-6 (aztalan/mayburgh/serpent-mound have 3).

**Held-out selection (FIXED, to be written into gate.md).** Design set = the 4 docs inspected while developing
metrics: bergues.c_4bbca705be732b1c, castle-rising.c_70f937b71ae63d6a, maiden-castle.earthworkenglan01allcgoog_n0124_1,
serpent-mound.ancientmonuments00squi_n0210_1. Rule: try seeds 20260101, 20260102, ... ascending; first seed whose
`np.random.default_rng(seed).choice(20, 8, replace=False)` over the sorted doc names is disjoint from the design
set wins. Seeds ...0101-...0107 all overlap; **20260108 wins**:
- held-out (8, DO NOT INSPECT until after gate.md is committed): arbor-low (earthworkenglan01allcgoog_n0597_1),
  avebury (n0581_1), aztalan (antiquitiesofwis00saph_n0182_1), badbury (n0132_1), cadbury (c_1fab2a0abe5b99d7),
  cahokia (c_aff1b996dce7fe3a), camp-d-attila (c_6a912845c1e1aa28), old-sarum (earthworkenglan01allcgoog_n0142_1)
- dev (12, threshold tuning allowed): the other 12 (includes all 4 design docs + old-sarum c_8192abb966d030a3)

**Dev pair-residual probe (done this session, all 12 dev docs, held-out untouched).** Solved
`plan_fit.similarity` transform, per-pair residual in Web-Mercator metres: median 3.7-53.1, max 4.6-86.7
(old-sarum c_8192: 53.1/86.7; hembury 40.3/53.3; little-solsbury 46.8/65.0; bergues 29.9/51.7; castle-rising
12.0/19.0; mayburgh 3.8/4.6; mound-bottom 3.7/6.5; serpent-mound 6.8/8.1; whitley 8.8/10.6; calleva 27.0/37.1;
berkhamsted 28.1/35.3; maiden-castle 26.6/43.0). So: 60 m move => median EXACTLY 60 (all points equal) =>
separable from dev max 53.1 by a threshold ~57; cross-site => km-scale, trivially separable. But 10 deg /
x1.15 add only 0.1745 r / 0.15 r per point (9-15 m on a 100 m-radius site) - INSIDE the dev true-fit spread,
so magnitude alone cannot kill them. That is what spike 7 measures.

**Spike results (scripts + outputs in /tmp: spike_gate.py, spike_gate2-6.py, spike4/5/6_out.txt).**
- S1 DEM ridge contrast, S2 DEM wall-template contrast (bergues true = worst, -0.205), S3 ink proximity
  (saturated at 1.0 on dense maps): all FAIL (details in DECISIONS.md + archive).
- S4 corr of blurred plate ink vs blurred map ink over overlap, vs a 81-cell search-matched null: null >= true
  at every site; cross-site searches +0.653 / +0.972. FAIL.
- S5 wall points within 10 m of map strokes (density-filtered skeleton, runs >= 30 px): no separation (castle
  true 0.718 vs moved 0.720 / x0.85 0.841). FAIL.
- S6 = S5 + wall-normal parallel to stroke across-direction (|cos| >= 0.7, 15 m window): castle true 0.420 vs
  x0.85 0.450; bergues true 0.056 (23% of wall pts in-box); maiden-castle true 0.259 vs x0.85 0.331;
  serpent-mound true 0.252 vs x1.15 0.338; cross castle-on-bergues 0.457. corr_ws n/a everywhere. FAIL.
  (Cross searches took 617 s / 289 s - keep any future search coarse; per-site sections are fast, 4-31 s.)

**Exact next step (one session).** Spike 7 (`/tmp/spike_gate7.py`, seconds per doc, no images): for each of the
12 DEV docs solve the similarity transform, then score the 4 wrong types made from it - (i) moved 60 m NE
(du=dv=42.4 m), (ii) turned 10 deg about the ink centroid, (iii) scaled x1.15, (iv) cross-site = the true
transform re-centred on the NEXT dev site's box centre (km-scale) - with statistics: median_r, max_r,
slope of linear fit residual~radius-from-centre, and (inner-half mean - outer-half mean). Read which statistic
separates all four from all 12 dev true fits; that fixes the conjunction and its thresholds (dev-only).
Then: 1) write + commit `docs/gate.md` (pre-registration: selection rule + seed 20260108 + the 8 names, the
rule/thresholds, wrong-fit recipes, reproduce command) BEFORE any held-out look; 2) implement
`pipeline/fit_gate.py` (pure geometry: reads `data/db/platefits/*.json` + `web/data/sites.json`; gate input =
(site, plate, pairs or transform); no skimage/images -> no requirements.txt change); 3) `tools/gate_heldout.py`
one-shot held-out run -> results table appended to `docs/gate.md`; 4) `tests/test_gate.py` re-runs the gate
offline (no ports, no writes outside project/tmp, golden-compare the table).

**Warnings.**
(a) The 8 held-out docs listed above stay untouched until after `docs/gate.md` is committed; the one-shot run
is the ONLY allowed look. (b) If held-out acceptance < 50%, the criteria allow documenting it (with numbers)
and sending every fit to review - do not chase it by re-tuning on held-out. (c) GOAL.md was renumbered by the
human: point 2 is now "the local model does the fitting itself" (>= 4 point pairs on matching features, fitkit
sheets) and point 3 = the gate with a 20-sample human check (18/20 right). The gate stays numbers-only, input
is (site, plate, pairs-or-transform); n_pairs as low as 3 exists in real docs, so threshold statistics must
work at n=3-4 (correlations are noisy that small - prefer slope/inner-outer-difference over Pearson r).
(d) Per TEAM MODE: my files are pipeline/fit_gate.py, tools/gate_heldout.py, docs/gate.md, tests/test_gate.py
only (all inside the task's `Touches:`); `tests/conftest.py` is 000's. (e) The driver rebuilds `.venv` from the
pinned `requirements.txt` before test runs - it is now valid (000 fixed it); keep the test importable with
numpy/scipy/PIL only. (f) `data/db/platefits/` and `web/data/sites.json` are read-only human/build artifacts.
