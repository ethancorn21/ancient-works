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

(2026-10-11, iteration 74, agent c - session 2: scikit-image pinned, venv rebuilt, suite proven green modulo one pre-existing failure. NEXT: write fit/inkfit.py.)

**State.**
- Parent plan step (1) VERIFIED after the driver's main sync: `data/db/platefits/maiden-castle-q1232816.c_c20ff6b1f16d173d.json` is the no-auto version (no `auto` key; pairs `[[551.9,461.3,-2.4691357,50.6948631],[310.1,422.5,-2.4746373,50.695179],[738,516.1,-2.4649471,50.6941682]]`; crop [165,256,895,663]; size [1280,889]). `tests/golden/hand_fit_docs.sha256` (20 docs + 19 site.json) and `hand_fit_sites.txt` are byte-identical to origin/main; the new commons doc is NOT in the golden. Never edit those goldens (task Notes).
- Step (2) DONE this session: `requirements.in` now lists `scikit-image`; `requirements.txt` regenerated with `/tmp/aw-pto/bin/pip-compile --generate-hashes --no-emit-index-url` (pip-tools 7.6.2, Python 3.12, throwaway venv outside the project). Diff vs old file: ONLY additions - `scikit-image==0.26.0`, `imageio==2.38.1`, `lazy-loader==0.6`, `networkx==3.7`; all 10 existing direct pins kept their exact versions (PyPI's current latests matched the earlier compilation, so no re-pinning in requirements.in was needed). `.venv` rebuilt with the driver's exact command `.venv/bin/pip install --require-hashes -r requirements.txt` (clean); import check OK: skimage 0.26.0 beside numpy 2.5.4 / scipy 1.18.1 / PIL 12.3.0 / rasterio 1.5.2 / pyproj 3.8.0 / laspy 2.7.0. Both files committed.
- Suite `.venv/bin/python -m pytest -q`: **59 passed, 1 failed - the failure is PRE-EXISTING, not caused by this pin** (the driver's `.agent/reports/last-failing-tests.txt`, recorded before this session's venv change, lists the same single test with the same message): `tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees` - `gate_heldout` aborts with "expected 20 hand-fit documents in data/db/platefits/, found 21" because post-registration hand fits now count (lead's cd104ca maiden-castle doc; 206's shotwick adds another). Owned by tasks/218 (agent a, open). I did not touch `tools/gate_heldout.py` or `tests/test_gate.py` (not in my Touches); do not "fix" it here - see PITFALLS entry "gate_heldout hard-fails while ANY post-registration hand fit exists".

**Files this task may change (Touches):** `fit/inkfit.py` (new), `requirements.in`, `requirements.txt` (done), `data/inkfit/` (new; committed relief caches are `.npz` under it - `.npy` is gitignored globally, `data/autofit/*.npz` is ignored but `data/inkfit/` is not). `tests/` is off-limits in 302a (the e2e test lands in 302c, which also builds the committed `data/inkfit/relief/<site>.npz`).

**Next step (the whole of it): write `fit/inkfit.py` per the parent's frozen design** (re-read the method paragraph in tasks/302-autofit-real.md ## Hand-over first; the frozen extractor config is docs/autofit.md section 3). Shape: `fit(site, picture, model=None)` callable; imports `aw`, `pipeline/autowalls` (frozen extractor), `pipeline/autofit` (coarse-FFT + refine machinery), `pipeline/fit_plate` (ridge-contrast objective), `pipeline/plan_fit` (`similarity`, `load_picture`, `fabrication_pattern`), `fit/propose` (the seed: scale/north/centre), `dem_sources` (relief fetch), all read-only. Model steps injectable with a deterministic no-model fallback (the AI box is unreachable from this VM). Relief cache path order: `data/inkfit/relief/<site>.npz` (loader must ACCEPT a seeded npz; the file itself is built in 302c) -> `data/sites/<id>/dem.npy` local cache -> `dem_sources` fetch (working phase only; tests are hermetic). Output: placement (Mercator similarity), N ink-point pairs (plate px in the doc's size frame -> lon/lat; irregularly chosen - NEVER evenly stepped along one straight wall, fabrication_pattern clause (b) fires on >=3 anchors sharing one coordinate with near-arithmetic spacing), `auto: true`, `fitter: "ink"`, and a confidence score built on the search-matched null (same search on a scrambled template and a shifted DEM box, whichever scores higher).

After writing it: smoke-run on 1-2 NON-held-out sites (stonehenge, or a US site) in the working phase and eyeball the overlay via tools/composite.py - development data only; NO parameter may be chosen using any of the 19 held-out sites (their plate images/reliefs are off-limits for tuning until 302b's one-shot run), and keep every parameter FROZEN before 302b's registration commit; the frozen configuration (extractor params, no-model fallback rule, search window, objective, null recipe) must be recorded in DECISIONS.md (acceptance box 4) before 302b.

**Re-read:** fit/inkfit.py:template_of - does the no-model fallback keep pieces that would make fabrication_pattern clause (b) fire (evenly spaced collinear points)? pipeline/plan_fit.py:build - the "how" string for fitter:"ink" docs (build's wording is keyed on auto:true alone today and would say "by the batch"; the wording fix is 302c's, but build must at least read my doc's fields without breaking). tools/site_done.py:_fit - the 302c replacement of the batch model loop must keep the covered-pictures rule (never re-fit a doc or an item's candidate) and the exit codes.
