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

## Hand-over (iteration 1, agent c)

**Where I am.** Recon done (no code in the repo yet; everything below is findings + a half-built experiment).
Next step is the next session: run spike 4, settle the gate's metric conjunction, then write `docs/gate.md`
(pre-registered) and commit it BEFORE any held-out run.

**The 21 hand fits** (all `model=similarity`; serpent-mound lacks `model`/`src` keys -> default similarity; whitley
lacks `src`): arbor-low, avebury, aztalan, badbury, bergues, berkhamsted, cadbury, cahokia, calleva, camp-d-attila,
castle-rising, hembury, little-solsbury, maiden-castle, mayburgh, mound-bottom, old-sarum x2, serpent-mound,
whitley. 20 sites, 21 docs. All have `web/data/sites/<site>/relief.jpg` (all LiDAR ground; none aerial-only here).
All 21 have old-map ink webps in the site dir: England `six-inch-1st_ink` (+`os1inch_ink`), US
`topo_1888/1891/1915/1930_62500_ink`, France/Belgium `cassini_ink` + `etatmajor_ink`. Ink webp = RGBA,
`alpha>8` = ink; built over the site box by `pipeline/nls.py` / `pipeline/topo.py` (webp px covers the box
corners exactly).

**Fit representation.** `data/db/platefits/<site>.<plan>.json`: `{site, plan, ia, file, crop[x0,y0,x1,y1] page px,
pairs [[u,v,lon,lat]], ...}`. `plan_fit.similarity` solves complex least squares `z = a*(u - 1j*v) + b` in Web
Mercator metres (a = scale*e^{i*rot}); a proposed placement = (site, plate crop, transform). Gate input = that
triple; the page's fit tool saves pairs, the search saves a transform.

**Environment (verified this session):** `.venv` created in the checkout (gitignored) with numpy scipy pillow
tifffile pyproj rasterio requests **scikit-image** (autowalls needs skimage; it is NOT in requirements.txt -> if
the gate keeps using `autowalls.extract`, add it to requirements.txt AND add `requirements.txt` to this task's
`Touches:` first). DEM fetch works here: England=EA, France=IGN, US=3DEP (spikes cache /tmp/dem_<site>.npy;
`*.npy` is gitignored so committed gate input caches must be `.npz`). `web/data/sites/*` and `data/raw/` exist on
this VM but are gitignored (raw scans/aerials are NOT here; the built webps are). The full-size plate image is
unavailable -> use the built `plan_<pid>.webp` (the crop, rescaled by f=min(1, 2400/max(crop))); webp px -> page
px: `u = x0 + x/f`.

**Key math (verified):** site web entry has `size_m` (not width_m); `corners[0]`=NW, `corners[2]`=SE; Mercator row
0 = north: `row = (Y_NW - y)/(Y_NW - Y_SE)*H`. Plate normal (nx,ny) (x right, y down) -> ground normal
`(c*nx + sn*ny, sn*nx - c*ny)` (matches `fit_plate.py`; sign irrelevant, we take max of both sides).

**Spike results (the evidence so far):**
- Spike 1, ALL ink pixels, 4-neighbour contrast, LRM r24 clip 1: castle-rising true -0.653 = WORST (wrong
  -0.13..-0.30, searched mirrored null -0.07). **Fail** - ink is mostly text/sections; median is noise.
- Spike 2, `autowalls.extract` wall template + stroke-normal contrast (fit_plate's metric, min 30 in-box points;
  null = mirrored template (u->2*mean-u) searched on a coarse grid ±25°/×0.74-1.36/±200 m @50 m): castle-rising
  true **+0.000** > wrong (-0.19..-0.32) but null also +0.000 (margin 0, fragile); bergues true **-0.205 = worst**
  (wrong -0.05..-0.10, null +0.002) **FAIL** (flat town, ploughed walls); cross-site best: bergues template on
  castle-rising ground **+0.528** - the one-sided ridge metric lets ANY template score high on hilly ground.
  **Conclusion: DEM score alone cannot be the gate's acceptance evidence; at best one conjunct, and only where
  relief is strong.**
- Spike 3, plate-ink proximity to old-map ink (fraction within 30 m): saturated at 1.000 on every dense map
  (etatmajor 48.6% ink; six-inch 20.7%), maiden-castle true 0.312 / wrong 0.25-0.37 / null 0.865. **Fail** -
  proximity measures map density, not correspondence.
- Spike 4 (WRITTEN, NOT RUN - context limit): correlation metrics. `corr_ink` = Pearson corr of the full plate ink
  (resampled through the perturbed transform onto the map grid, blurred 20 m at plate resolution) vs the old-map
  ink blurred 30 m, over the overlapping footprint; `wall_on_mapstroke` = median over the extracted wall points of
  the map's stroke-blur (map strokes = `autowalls.extract` on the map's ink, min_len/min_extent 80). Script at
  `/tmp/spike_gate4.py`. Its transform perturb: `a' = e^{i*drot}*scale*a`, `b' = c' + a'*(u0 - i*v0) - a*(u0 - i*v0)`
  with c' = the (perturbed) placement centre, (u0,v0) = ink centroid. Cases: castle-rising (six-inch), bergues
  (etatmajor AND cassini), maiden-castle (six-inch), serpent-mound (topo_1915_48000); plus cross-site: castle-rising
  plate searched on bergues etatmajor, bergues plate on castle-rising six-inch, at ±25°/×0.74-1.36/±400 m @100 m,
  best corr. **If /tmp/spike_gate4.py is gone, rewrite it from this description** (it imports aw + autowalls the
  same way as the pipeline scripts; `map_coordinates` resamples the blurred plate ink through the transform onto
  the map grid).

**Current hypothesis.** Gate rule = conjunction of numeric checks, thresholds chosen on the 13 NON-held-out dev
fits only: (1) pair-consistency residuals (from the solved transform; catches sloppy pair sets); (2) old-map
correlation vs a search-matched null (the main discriminator for 60 m / 10° / 15% / cross-site - old maps have
dense linear structure the plate must match); (3) DEM ridge score vs search-matched null as a bonus conjunct
where relief is strong (helps the 15% case on relief-rich sites). Cross-site wrong fits must fail on (2) (no
matching structure) - this is the open risk spike 4 checks: a town plan (bergues) may still correlate with another
town's map (dense grids). If correlation alone cannot kill cross-site, add: placement centroid vs the site's
catalog position, and plate-content-extent vs site-box size (a 3.3 km town plate centred on an 800 m castle box
overflows it). The gate may accept only some held-out fits (≥ half is the bar; the rest go to the review queue -
designed behaviour, GOAL.md point 1).

**Exact next step.** 1) Run `/tmp/spike_gate4.py` (or rewrite it) and read the corr numbers per site. 2) Pick the
conjunction + thresholds from dev fits (start: corr_ink ≥ null_corr + margin AND wall_on_mapstroke ≥ threshold;
tune on the 13 dev fits, never the held-out 8). 3) Write + commit `docs/gate.md` (pre-registration): held-out
selection = `numpy.random.default_rng(20260101).choice` over the 21 sorted docs, 8 indices, listed by name in the
doc; the rule + thresholds; wrong-fit recipes (60 m = NE 42.4/42.4 m; 10°; ×1.15; cross-site = next held-out
site's ground, search window ±25°/×0.74-1.36/±200 m, template = autowalls extract of the plate webp). 4) Implement
`pipeline/fit_gate.py` (gate + wrong-fit maker, reads the committed input cache) + `data/gate/*.npz` caches (DEM
grid, map ink, plate ink, template, pairs - committed; `.npz` outside `data/autofit/` is NOT gitignored) so the
test is offline. 5) One-shot held-out run -> results table into docs/gate.md + `tests/test_gate.py` (re-runs the
gate from cache, golden-compares the table; no ports, writes only to project/tmp). If the 8 held-out yields <50%
acceptance, the doc says so with the numbers and the project sends every fit to review (acceptable per the
criteria - document it, don't chase it).

**Warnings.** (a) `docs/gate.md` must be committed BEFORE the first held-out run - the pre-registration is the whole
point (docs/autofit.md is the model). (b) Never tune on held-out data; leakage = invalid result. (c) Agent a
(task 000) may create `tests/` infra - my test is one file `tests/test_gate.py`, no conftest (deps via sys.path
insert like the pipeline scripts). (d) `data/db/platefits/` is human-owned: read-only. (e) The spike scripts live
in /tmp; the final implementations go in `pipeline/fit_gate.py` + `tools/` per the Touches line.
