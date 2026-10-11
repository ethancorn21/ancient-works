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
- [x] `fit/inkfit.py` runs end to end in the working phase on at least two real built sites that are NOT
      among the 19 hand-fit sites (e.g. stonehenge, a US site): ink template from the plate image,
      search against that site's real 1 m-class relief (dem_sources), and a placement with ink pairs,
      all without reading any platefit document.
- [x] scikit-image pinned: added to `requirements.in`, `requirements.txt` regenerated with
      pip-compile --generate-hashes from a throwaway venv outside the project, both committed; the
      driver's .venv build and the full test suite are green with the pin.
- [x] The method is hermetically testable: a callable `fit(site, picture, model=None)` whose model
      parameter is injectable, and a relief-cache path the tests can seed offline (a committed
      `data/inkfit/relief/<site>.npz` for the test site is fine, built in 302c; this task only needs
      the loader to accept it).
- [x] A DECISIONS.md entry records the frozen configuration (extractor params, no-model fallback rule,
      search window, objective, null recipe) before any parameter was tuned on a held-out site.
- [x] tests/ is untouched by this task (its e2e test lands in 302c).

## Hand-over

(2026-10-11, iteration 78, agent c - session 6: **ALL FIVE BOXES TICKED - 302a is done.**
fit/inkfit.py is verified end to end hermetically AND on two real non-held-out sites in the working
phase; two real bugs were found and fixed along the way. Uncommitted at hand-over time: fit/inkfit.py
(the two fixes) and PITFALLS.md (new Frangi-ghost entry) - the harness saved them; COMMIT THEM next
session (they are ready: no further changes needed). The DECISIONS session-6 entry is committed.

**State.** Box 1 (two real non-held-out sites, end to end, no platefit read) and box 3 (hermetic:
injectable model + seeded-npz loader) ticked this session after the runs below; boxes 2 and 4 were
done in sessions 2-3; box 5 holds (tests/ untouched by this task; its e2e test lands in 302c).
Suite at last run this session: `.venv/bin/python -m pytest -q` -> 59 passed / 1 failed, the failure
being the PRE-EXISTING tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees (218 owns
it: gate_heldout expects 20 hand-fit docs but main has 21). No new failures from this module. No
frozen parameter of the method was changed in any session.

**This session (verified by running):**
- Bug fix 1 (fit/inkfit.py:template_pieces): it returned `_keep_pieces(...)` as the first element,
  but that function returns a (list, label) TUPLE, so fit() got pieces=(list_of_dicts, "") and
  crashed ("list indices must be integers or slices, not str") the first time a non-empty piece
  list was produced (masked in session 5 by the "no wall ink extracted" early return, whose [] is
  falsy). Now unpacked inside template_pieces.
- Bug fix 2 (fit/inkfit.py:main): the CLI let the search progress and aw's fetch chatter (overpass
  504 retries) land on stdout, corrupting the JSON result file. main() now points sys.stdout at
  stderr around the fit() call (print() resolves sys.stdout dynamically, so aw.py's own prints are
  caught too) and emits only the JSON document on stdout (verified on the pyramid-mound run).
- Hermetic run: the 8 px SHARP drawing was not the fix - a razor-sharp 0/1 step makes the frozen
  Frangi (gamma 0.013, calibrated on soft real-scan edges) ghost-echo a ring ~5-8 px OUTSIDE the
  drawn walls (even inside the zeroed margin), and a blurred 8 px line falls under the ridge
  threshold. The scan-realistic fixture (8 px rectangle [62,52,178,128] + 12 px interior line
  [70,90,170,90], gaussian_filter 2.5, +-2/255 paper noise, rng seed 7; 12 px is inside the real
  6-20 px wall band) gives exactly the 3 true centre lines, no ghosts, fully deterministic. fit()
  ran fully offline in 8.1 s against the seeded data/inkfit/relief/herm-site-q1.npz (shape/px_m/
  bbox validated, modern from the npz, zero network): 3 pieces/81 pts, seed 0.75 (hermetic
  picture-size fallback), search on the TRUE placement (s 0.7408, rot -0.5 deg, t [-17,0] vs true
  0.75/0/0), both nulls recorded (scramble 0.7404, shifted -9/invalid - see below), gate accept
  (n 6, 4 mm), fabrication silent, doc returned (fitter "ink", batch_us field shape, "at"
  injectable). Confidence NEGATIVE (-0.025) - the method answered "not confident", which is the
  decision layer working, not a failure.
- Smoke 1: `.venv/bin/python fit/inkfit.py stonehenge-q39671 earthworkenglan01allcgoog_n0582_1`
  (site NOT among the 19 held-out - checked against tests/golden/hand_fit_sites.txt): 134.5 s,
  19 pieces/1952 pts, seed 0.5034 (picture_size; the 64.3 deg north hint rejected, north-up),
  FALSE peak at the window edge (s 0.3716, rot +25.5 deg, t [177,-149]) exactly as 10-10 predicted;
  fit 0.0468 vs scramble 0.1227 (null) vs shifted 0.0114 -> confidence -0.076 -> "not confident";
  gate accept (n 10, 12 mm); fabrication silent (10 irregular pairs); corners inside the 1000x1000 m
  site box; OSM modern mask after 3 overpass 504 retries then OK; DEM 8.0 MB to
  data/sites/stonehenge-q39671/dem.npy (gitignored).
- Smoke 2: `.venv/bin/python fit/inkfit.py pyramid-mound-q7263260 ancientmonuments00squi_n0134_1`
  (also not held-out): 74.4 s, 4 pieces/273 pts, seed 0.8806, placement s 0.752 / rot 10 deg /
  t [-123,-197] (inside window, near the seed), fit 0.311 vs null 0.442 vs shifted 0.1703 ->
  confidence -0.131, gate accept (n 8, 4 mm), fabrication silent, 8 pairs, DEM 5.1 MB to
  data/sites/pyramid-mound-q7263260/dem.npy.
  Both sites answering "not confident" is consistent with the 10-10 pre-registration (relief scores
  have false peaks; only a search-matched null can say so) and with this task's remit (box 1 asks
  for machinery end to end + placement + pairs, which both deliver; neither site is held-out, so
  nothing was tuned to these outcomes). The held-out table (302b) shows whether the margin is
  positive on the truth sites; if the no-model variant stays negative there, that IS the reported
  result (302: report the numbers as they are).

**For 302b/302c (reading the method's output):** fit() result keys - site, plan, model (variant
label: "no-model" or the model's name/label), reason (None or the review reason: "no wall ink
extracted", "search found no valid placement", the fabrication string), n_pieces, n_points, seed
{s_m_px, rot_deg, source, note}, objective {fit[, scramble, shifted, scramble_valid,
shifted_valid]}, null (the higher null objective or None), confidence (obj_fit - null or None;
NEGATIVE = not confident - no threshold yet: 302b sets it on the held-out table, 302c applies it),
placement {a, b, s_m_px, rot_deg, t_m, u0v0, k}, corners (panel corners' lon/lat), gate {verdict,
n, med, slope_o, io}, fabrication (None on success), pairs [[u,v,lon,lat]...], doc (UNWRITTEN:
batch_us.write_doc fields + "fitter":"ink"; "at" injectable via fit(at=...)), notes, seconds.
fit(site, picture, model=None, root=None, n_refine=8, null=True, at=None, log=print): root lets
tests redirect the data tree; the npz loader (data/inkfit/relief/<site>.npz: z, px_m, bbox,
optional modern) accepts a seeded cache, so 302c's committed test-site npz makes the whole method
hermetic. fit() is deterministic for a fixed input image (fixed seeds 20261012; frangi/skeletonize
deterministic). It never writes except work-phase dem.npy caches; it never reads data/db/platefits/.

**302c test-fixture lessons (from the hermetic run):** (a) the half-box-shift null goes -9 (invalid)
when the box is small: shifting the 120x100 m toy box leaves a 60x40 m valid region smaller than
the 120x90 m template -> < 50% valid -> -9 (recorded as designed, shifted_valid:false). Make the
test site box ~1000 m-class with a ~100 m earthwork so both nulls stay valid. (b) A template of one
two long straight pieces keeps SCRAMBLE signal (a long wall re-aligned to any one ridge side still
scores high) - use several pieces of differing lengths/angles so the null discriminates.

**Costs/limits (measured):** 1000x1000 m site + 3 searches ~135 s; 800x800 ~75 s (the OSM
modern-mask fetch with overpass retries is the variable part; 14 GB RAM / 6 cores, headroom to
spare; no fixed ports; writes only data/sites/<sid>/dem.npy in the work phase and, in tests, the
seeded npz under the test root).

**Re-read (for 302c, not 302a's job):** pipeline/plan_fit.py:build (lines ~290-292) - the "how"
string for auto:true docs still says "Fitted automatically by the batch..." for a fitter:"ink" doc;
302c's wording fix (plan_fit.py is in the parent's Touches, not this task's). tools/site_done.py:
_fit - the 302c replacement of the batch model loop must keep the covered-pictures rule and the
exit codes. fit/inkfit.py:fit - the review reason should name the margin and which null beat the
fit when 302c routes an unsure fit to the queue. Also commit this task's two uncommitted files
(fit/inkfit.py, PITFALLS.md) if the harness did not already.
