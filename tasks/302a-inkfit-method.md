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

(2026-10-11, iteration 76, agent c - session 4: geometry derivation VERIFIED with a critical b-convention
correction; smoke targets confirmed; fit/inkfit.py fully designed but NOT yet written. NEXT: write the
module per the design below, smoke-run 2 sites, pytest, commit, tick boxes 1+3.)

**State.** Boxes: 2 (scikit-image pin) and 4 (frozen config in DECISIONS) are done (sessions 2-3, committed); 5 holds (tests/ untouched). Box 1 (two non-held-out site runs) and box 3 (hermetic loader check) need the module written - that is this task's remaining work. This session verified the placement->similarity derivation by running it (DECISIONS entry below): the session-3 script had TWO bugs, not one - besides the noted broadcast fix it applied M to [du, dv] instead of the autofit convention d = [du, −dv]. With both fixed: a = k·s·e^{iθ} recovered to 7e-6 relative (the 1dp/7dp rounding limit), residuals 1.4-4.6 mm, gate accepts. **CRITICAL CORRECTION:** b = zc − a·complex(u0c, **−v0c**) — the minus-v form (propose's `wc = complex(u0, -v0)`). The session-3 script used +v0c and only "agreed" to 1.3e-4 relative because |b| ≈ 6.6e6 m absorbs an 860 m error. Also verified: re-fitting propose._anchor_pairs' 5 pairs recovers its a and b exactly. Test suite last run in session 2: 59 passed / 1 pre-existing test_gate failure (owned by 218); nothing this session changed any code.

**Smoke targets (CONFIRMED, both non-held-out, non-10-10, images local, index.jsonl rows exist):**
- stonehenge-q39671 (1000×1000 m, EA 1 m): book row `earthworkenglan01allcgoog_n0582_1` (Allcroft 1908; leaf 3367×5050; map_box [0.19,0.32,0.78,0.62]; north_angle 64.3° → propose rejects (>60) → north-up; no scale_text → coarse picture-size scale).
- pyramid-mound-q7263260 (800×800 m, USGS 3DEP): book row `ancientmonuments00squi_n0134_1` (Squier-Davis 1848; leaf 2884×4064; map_box [0.125,0.55,0.44,0.68]; no scale/north → coarse, north-up).
plans.json rows carry `map_box` as FRACTIONS (row `sites` list links sites; `site` is null). propose.propose_for works for both from this checkout; in a hermetic temp root it raises FileNotFoundError (no data/books/index.jsonl) → seed fallback must catch **Exception** (not just ValueError/KeyError) and use propose._picture_scale(site, size, box) + rot 0.

**Module design (fit/inkfit.py; all frozen params as named module constants, comment each "frozen, docs/autofit.md section 3 / 10-10 run"). The frozen values themselves live in the session-3 DECISIONS entry - do not change any of them without labelling it exploratory:**
- `fit(site, picture, model=None, root=None, n_refine=8, null=True, at=None, log=print) -> dict`. site: entry dict (id/lon/lat/size_m) or id str; picture: plans row dict ("id") or id str. Result keys: site, plan, model (variant str: "no-model" or model name + suffixes), reason (None or review reason), n_pieces, n_points, seed {s_m_px, rot_deg, source, note}, objective {fit[, scramble, shifted]}, null (max or None), confidence (obj_fit − null or None), placement {a:[re,im], b:[re,im], s_m_px, rot_deg, t_m, u0v0, k}, corners (4 panel-corner lon/lat under the final placement - the eyeball aid; tools/composite needs a built site, so print these instead), gate {verdict,n,med,slope_o,io}, fabrication (None), pairs ([[u,v,lon,lat] 1dp/7dp size frame]), doc (full platefit doc), seconds. Pure except: relief fetch saves <root>/data/sites/<sid>/dem.npy; the modern-mask OSM fetch is try/except → None (recorded). Early returns (reason set, no doc): no pieces "no wall ink extracted"; obj_fit ≤ −9 "search found no valid placement"; < 4 points "not enough wall ink (N candidate points, need 4)"; fabrication pattern after 8 attempts.
- load_panel: book → data/raw/books/<ia>/full/<file> (clear FileNotFoundError); commons → big/<id>.jpg, else data/raw/commons/<url-tail>, else plan_fit.load_picture(pseudo-doc {src:"commons",plan:id,ref,size,ia,file}, root) (network). fs = im.width/size[0]; fractional map_box → crop size-frame [x0*w, y0*h, x1*w, y1*h] (extent <2 px → full frame); panel = im.crop(int(c*fs)); panel px → size frame: uv/fs + crop[:2].
- relief: bbox = aw.site_bbox(site.lon, site.lat, w_m, h_m), w_m/h_m = size_m else (1000,1000); w,h = round(m/1.0). Loader: <root>/data/inkfit/relief/<sid>.npz (z float64 h×w NaN=nodata; px_m present ⇒ must equal 1.0; bbox 4 floats validated vs expected to ~1 m; optional `modern` bool array, shape-checked) → <root>/data/sites/<sid>/dem.npy (single array, exact (h,w) else refetch) → aw.fetch_dem(bbox, w, h) (working phase; saves dem.npy). water = aw.water_mask(z, 1.0); modern = npz key else aw.modern_mask(bbox, w, h, 1.0) in try/except → None.
- build_lrm: zf = aw.fill_nan(z); lrm = clip(aw.local_relief(zf, 1.0, radius_m=24.0), −1.0, 1.0); then lrm[modern]=NaN (if not None), lrm[water]=NaN.
- class InkSite(site, lrm, bbox, w_m, h_m, c0, s, rot, t=(0,0)): cx,cy = bbox centre; w,h = lrm.shape; px_m=1.0; W_m,H_m; side_m=20; c0 (size frame); hand_s/hand_rot/hand_t = s, rot, t (fit_site is driven with the single seed dict {scale_factor:1.0, rot_offset_deg:0.0, centre_offset_m:[0,0]}). Methods mirror autofit.Site EXACTLY: to_ground (d = [u−c0x, −(v−c0y)] @ M.T + t), relief_at (col=(e+W/2)/px_m, row=(H/2−n)/px_m, valid 0≤·<w−1 / h−1, map_coordinates order=0), contrast (n = [N0,−N1] @ inv(M) normalised; on − max(a,b) at ±side_m), score, corners_ground.
- template_pieces(panel, model): no-model (frozen): boxes=[]; model: boxes from model.boxes(panel) (kind in autowalls.P["box_kinds"], 0-1000 → panel px) in try/except → []. (pts, nrm, wt), dbg = autowalls.extract(panel, boxes, p=autowalls.P, debug=True) (P UNCHANGED); pieces = 8-connected components (ndi.label structure=np.ones((3,3))) of dbg["keep"] grouping the extracted points; each {idx, len (mask px count), pts, nrm, w}; sorted (−len, idx). Model labels: model.label_pieces(panel, pieces) in try/except → None; dict with entries ⇒ keep only kind=="wall" (empty ⇒ keep all, variant "... (rejected every piece; all kept)"; None ⇒ "... (no piece labels; all kept)").
- seed_for(site, row): try propose.propose_for(site["id"], row["id"]) (catch Exception; needs scale_m_px) → (s0, rot_deg, scale_source, note); fallback (s0 = propose._picture_scale({"size_m": size_m or [1000,1000]}, row.size, fractional box), 0.0, "picture_size", note). t0 = (0,0) always.
- run_search(S, P, N, w, n_refine, log): autofit.fit_site(S, P, N, w, [single seed], n_refine, log) → result[0] {obj, coarse_obj, s, rot, t, top_coarse}. Reuse autofit's frozen WIN_ROT/WIN_LOGS/WIN_T/ROT_STEP/LOGS_STEP/CELL_M/NEG_FLOOR/K_BINS by reference (autofit.py's module constants).
- null (only if null=True and obj_fit > −9): (a) scramble: rng = np.random.default_rng(20261012); per piece (in panel px): rigid rotate U(0,2π) about piece centroid, translate centroid U(−0.4,0.4)×(W,H) panel px, clip per axis to [0,W]×[0,H]; normals rotated; → size frame; same InkSite. (b) shifted lrm = ndi.shift(lrm, (H_m/2/1.0, W_m/2/1.0), order=0, cval=nan) (box half north + half east; masks unchanged - frozen), new InkSite, same template. null = max of the two objs; confidence = obj_fit − null; record per-null valid flags (obj > −9).
- choose_points(pieces, to_size, seed=20261012, attempts=8): work in SIZE frame (fabrication clauses are frame-dependent: gap thresholds, 10-px grid rounding). Per piece: PCA principal axis of its points; project; pick points nearest the 0.23 and 0.71 quantiles (attempt 0 exact; attempts ≥1: quantiles jittered ±0.03 by rng(20261012+attempt)); ≤2 per piece, longest first, stop at 10. < 4 total → (None, reason). plan_fit.fabrication_pattern on [[u,v,0,0]...]: None → done; else re-draw; after 8 → (None, last pattern).
- map_pairs(S, uv, s, rot, t): M = autofit.sim(s, rot); en = S.to_ground(uv, M, t); k = 1/aw.ground_scale(site.lat); lon/lat = aw.to_lonlat(S.cx + e·k, S.cy + n·k); round 1dp/7dp.
- placement_of(S, s, rot, t): k = 1/ground_scale(lat); a = k·s·e^{iθ}; **b = complex(S.cx + k·t[0], S.cy + k·t[1]) − a·complex(S.c0[0], −S.c0[1])** (MINUS-v, verified this session). corners: 4 crop corners z = a·(u − iv) + b → lon/lat.
- gate: fit_gate.gate(pairs, (a, b)) → record (accepts by construction - residuals 0; defence layer per gate section 7). doc: batch_us.write_doc's fields + "fitter":"ink" (book: ia/file/book; commons: ia/file None, model "similarity", src "commons", url/ref/size); crop = _crop_px rule; score = gate med rounded 1 dp; at = ISO now or passed.
- CLI: `python3 fit/inkfit.py <site> <plan> [--no-null]` → JSON result (numpy scalars → float). Imports: sys.path.insert pipeline/ (aw, autofit, autowalls, fit_gate, plan_fit) and fit/ (propose); no network at import time (verified session 3).

**Next steps (in order):** (1) write fit/inkfit.py per the design (one job per function, ~350 lines; keep frozen constants named); (2) smoke-run `.venv/bin/python fit/inkfit.py stonehenge-q39671 earthworkenglan01allcgoog_n0582_1` and `... pyramid-mound-q7263260 ancientmonuments00squi_n0134_1` (model=None, ~1-3 min each; expect OSM modern-mask fetch or a graceful None; eyeball: print result corners vs the site's box corners - the panel corners should land inside the site box for a plausible fit; a false peak is EXPECTED and fine - box 1 only requires the machinery runs end to end and produces a placement + pairs; record n_pieces/n_points and wall-vs-junk look in DECISIONS); (3) quick hermetic check for box 3: temp tree with a synthetic site dict, a small drawn image, a seeded data/inkfit/relief/<sid>.npz (z, px_m, bbox, modern zeros) → fit(...) completes offline; (4) `.venv/bin/python -m pytest -q` (expect 59/1 - tests/ is this task's no-go); (5) if smoke reveals BUGS (not tuning), fix and re-run; any parameter change is forbidden without labelling it exploratory in DECISIONS; then commit the module (+ tick box 1, and 3 if the hermetic check passed) with the usual memory-file updates.

**Costs:** 10-10 run: 8 seeds = 45-132 s/site; single-seed search ≈ 26 rot × ~17 scale maps per Coarse → expect ~1-3 min per site including 2 null searches (scramble reuses the ground; shifted needs a new Coarse). OSM modern-mask fetch adds seconds (or fails → None). No fixed ports, no writes outside project+temp.

**Re-read (next session):** fit/inkfit.py:placement_of - b uses complex(u0c, −v0c) (MINUS-v); InkSite.to_ground uses d = [du, −dv]; relief - the npz loader validates shape + px_m=1.0 + bbox before use; choose_points - fabrication check on SIZE-frame coords, ≤2 per piece; run_search - InkSite exposes everything autofit's Coarse/objective/refine/fit_site touch (px_m, h, w, lrm, side_m, W_m, H_m, c0, to_ground, relief_at, contrast, score, hand_s/rot/t). pipeline/plan_fit.py:build - the "how" string for fitter:"ink" docs is still batch wording (302c's fix; build must read my doc fields without breaking: site/plan/crop/pairs/model/auto/score + label/title/book/ia/file/src/cite/url/ref/size/at). tools/site_done.py:_fit - the 302c replacement of the batch model loop must keep the covered-pictures rule and the exit codes.
