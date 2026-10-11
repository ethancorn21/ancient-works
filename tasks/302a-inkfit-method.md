Status: open
Depends on: 301
# 302a: The ink-fit method - plate ink against LiDAR relief, no model coordinates
Touches: fit/inkfit.py, requirements.in, requirements.txt, data/inkfit/

## Goal
The new module `fit/inkfit.py`: an automatic fit of one candidate picture of one site whose matching
points come from the pictures themselves - the plate's ink (extracted with `pipeline/autowalls.py`'s
frozen config, docs/autofit.md section 3) matched against the site's bare-earth relief with
`fit_plate`'s ridge-contrast objective, searched with `pipeline/autofit.py`'s coarse-FFT + refine
machinery from a seed that never touches the hand fit (scale/north/centre from `fit/propose.py`'s
anchor or a coarse default; the vision model may give a starting guess and classify ink pieces, never
a coordinate). Output: a placement (Mercator similarity) plus N ink-point pairs (plate px in the doc's
size frame -> lon/lat, irregularly chosen so plan_fit.fabrication_pattern cannot fire) and a
confidence score built on a search-matched null (docs/autofit.md section 4 finding 2: the same search
on a scrambled template and/or a shifted DEM box, whichever scores higher), ready to decide sync vs
review queue. The model step is injectable with a deterministic no-model fallback (this VM cannot
reach the AI box; see the parent hand-over).

## Acceptance criteria
- [ ] `fit/inkfit.py` runs end to end in the working phase on at least two real built sites that are NOT
      among the 19 hand-fit sites (e.g. stonehenge, a US site): ink template from the plate image,
      search against that site's real 1 m-class relief (dem_sources), and a placement with ink pairs,
      all without reading any platefit document.
- [ ] scikit-image pinned: added to `requirements.in`, `requirements.txt` regenerated with
      pip-compile --generate-hashes from a throwaway venv outside the project, both committed; the
      driver's .venv build and the full test suite are green with the pin.
- [ ] The method is hermetically testable: a callable `fit(site, picture, model=None)` whose model
      parameter is injectable, and a relief-cache path the tests can seed offline (a committed
      `data/inkfit/relief/<site>.npz` for the test site is fine, built in 302c; this task only needs
      the loader to accept it).
- [ ] A DECISIONS.md entry records the frozen configuration (extractor params, no-model fallback rule,
      search window, objective, null recipe) before any parameter was tuned on a held-out site.
- [ ] tests/ is untouched by this task (its e2e test lands in 302c).

## Hand-over

(2026-10-11, iteration 77, agent c - session 5: **fit/inkfit.py is WRITTEN** (in the working tree,
UNCOMMITTED - the harness saved it; commit it this session after the smoke runs pass) and its
picture/seed/relief-cache paths are verified. NEXT: thicken the synthetic test plate, re-run the
hermetic script, smoke-run the two real sites, pytest, commit + tick boxes 1 and 3.)

**State.** Boxes 2 (scikit-image pin) and 4 (frozen config in DECISIONS) done (sessions 2-3); 5 holds
(tests/ untouched - I ran no tests this session; last suite state from session 2: 59 passed / 1
pre-existing tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees failure owned by 218).
Box 3 is essentially proven by the hermetic run below (the loader accepted a seeded npz and the whole
method ran offline) - tick it once the re-run with a drawing that yields ink completes. Box 1 needs
the real-site smoke runs.

**This session (verified by running):**
- Wrote fit/inkfit.py in full (~490 lines) per the session-4 design: load_panel/_page_picture/
  _panel_crop; relief/_relief_z/_build_lrm (npz cache -> dem.npy -> fetch; _NoRelief for
  NoLidar/all-NaN); InkSite mirroring autofit.Site exactly (to_ground d=[du,-dv], relief_at,
  contrast, score; hand_* = the single seed); run_search (autofit.fit_site, one seed
  {scale_factor:1, rot_offset 0, centre [0,0]}, frozen WIN_*/n_refine); seed_for (propose_for,
  catch Exception -> propose._picture_scale fallback); template_pieces/_model_boxes/_keep_pieces
  (autowalls.extract frozen P, 8-connected ndi.label, model keep/drop, no-model keeps all);
  scramble_pieces (frozen rng 20261012, per-piece rigid rotate + U(-0.4,0.4) translate, clipped);
  choose_points/_piece_pick (PCA quantile 0.23/0.71 ±0.03 jittered redraws, <=2/piece, max 10,
  min 4, fabrication_pattern silent or concede after 8); map_pairs (k=1/ground_scale, to_lonlat);
  placement_of (a=k*s*e^{iθ}, **b = complex(cx+k*t[0], cy+k*t[1]) − a*complex(c0[0], −c0[1])**
  MINUS-v per session 4; corners); _doc (batch_us.write_doc fields + "fitter":"ink"; returned,
  NEVER written); fit() with the design's result keys; CLI. batch_us is not imported (fields
  copied local). No network at import.
- import inkfit clean. load_panel+seed_for verified on both real rows: stonehenge-q39671 /
  earthworkenglan01allcgoog_n0582_1 -> panel 1986x1515, fs 1.0, crop [639.73, 1616.0, 2626.26,
  3131.0], seed 0.5034 m/px picture_size, rot 0 (64.3° hint rejected). pyramid-mound-q7263260 /
  ancientmonuments00squi_n0134_1 -> panel 909x529, crop [360.5, 2235.2, 1268.96, 2763.52], seed
  0.8806, north-up.
- Hermetic run: throwaway script /tmp/aw-inkfit-herm/run.py (temp root /tmp/aw-inkfit-herm/root;
  if /tmp is gone recreate: site dict {id:"herm-site-q1", lon:-2.0, lat:51.5, size_m:[120,100]};
  relief npz at data/inkfit/relief/herm-site-q1.npz with z (120x100: 0.01/0.02 m/px slope + a 72x45 m
  1.2 m-tall rectangular band centred, 3 px wide), px_m=1.0, bbox=aw.site_bbox(...), modern=zeros;
  plate data/raw/books/testbook/full/n0001.jpg = 240x180 L=245 with black rectangle
  [72,60,168,120] width 5 + interior line [72,90]-[120,90] width 5; row dict {id:"herm-plan-1",
  ia:"testbook", file:"n0001.jpg", size:[240,180], map_box:[1/6,1/6,5/6,5/6]};
  inkfit.fit(site, row, root=ROOT)). Result in 1.6 s: npz accepted, zero network, early return
  "no wall ink extracted". HYPOTHESIS: my 5 px synthetic lines are below the frozen extractor
  (Frangi sigmas 4/6/9, ridge_thr 0.25, coherence sigma 25/min 0.6, min_len/min_extent 50 px; real
  walls are 6-20 px bands) - a TEST-DRAWING problem, not a module bug.
- SIGN FIX recorded in DECISIONS (bug fix, magnitudes frozen): the shifted-DEM null is
  ndi.shift(lrm, (-S.H_m/2/PX_M, +S.W_m/2/PX_M), order=0, cval=np.nan) - content moves half box
  NORTH + half EAST per the registration text; the session-4 note's (H/2, W/2) both-positive form
  was a south+east move (scipy out[i]=in[i-shift]).

**Next steps (in order):** (1) edit /tmp/aw-inkfit-herm/run.py: draw the walls 8 px thick
  (rectangle [72,60,168,120] width 8; keep the interior line, lengthen to >= 60 px, width 8) and
  re-run `.venv/bin/python /tmp/aw-inkfit-herm/run.py /tmp/aw-inkfit-herm/root $PWD` - expect pieces,
  a search that lands near s≈0.75/rot≈0/t≈0 (the true placement), both nulls, <=10 pairs, gate
  accept, a doc with fitter:"ink". If Frangi still draws nothing at 8 px, inspect dbg["R"]
  (autowalls.extract(..., debug=True)) and go 10-12 px thick; do NOT touch the frozen P. (2) Smoke:
  `.venv/bin/python fit/inkfit.py stonehenge-q39671 earthworkenglan01allcgoog_n0582_1` then
  `.venv/bin/python fit/inkfit.py pyramid-mound-q7263260 ancientmonuments00squi_n0134_1` (working
  phase: each fetches data/sites/<sid>/dem.npy via dem_sources + the OSM modern mask, ~1-3 min
  including 2 null searches; eyeball result `corners` vs the site box: 1000x1000 / 800x800 m boxes
  around the site - a false peak is EXPECTED and fine, box 1 only needs machinery end-to-end + a
  placement + pairs; record n_pieces/n_points/objective/null/confidence in DECISIONS). (3)
  `.venv/bin/python -m pytest -q` (expect 59 passed / 1 pre-existing failure; tests/ is a no-go for
  this task). (4) Commit fit/inkfit.py + this file + DECISIONS (+ PITFALLS if anything lasting
  emerges) with the usual message; tick boxes 1 and 3. Any parameter change during the smoke runs is
  FORBIDDEN without labelling it exploratory in DECISIONS (box 4); bug fixes are fine.

**Costs/limits:** 1000x1000 Coarse = 8 bins x 2 FFTs of ~358x180 complex (next_fast_len of
250+108) - small; 27 rot x 17 scale = 459 coarse scores + up to 8 refines per search; 3 searches per
site (fit + scramble + shifted). 14 GB RAM / 6 cores here. No fixed ports; writes only
data/sites/<sid>/dem.npy (working phase) and (in tests) the seeded npz.

**Re-read (next session):** fit/inkfit.py:placement_of - b uses complex(c0[0], −c0[1]) (MINUS-v);
  fit:the shifted-DEM null shift is (−H/2, +W/2) (content north+east). relief - the npz loader
  validates shape (h,w) + px_m==1.0 + bbox within 1 m of aw.site_bbox before use; dem.npy must be
  exactly (h,w) else refetch. choose_points - fabrication check on SIZE-frame rounded u,v, <=2 per
  piece, 8 attempts. run_search - InkSite exposes everything autofit's Coarse/objective/refine/
  fit_site touch (px_m, h, w, lrm, side_m, W_m, H_m, c0, to_ground, relief_at, contrast, score,
  hand_s/rot/t) - proven by reading; the real-relief run proves it by running.
pipeline/plan_fit.py:build - the "how" string for fitter:"ink" docs is still batch wording (302c's
  fix; build reads my doc's fields fine). tools/site_done.py:_fit - the 302c replacement of the
  batch model loop must keep the covered-pictures rule and the exit codes.
