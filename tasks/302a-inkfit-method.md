Status: in-progress
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

(2026-10-11, iteration 78, agent c - session 7: **Status: done.** This session changed no code:
it verified from HEAD that session 6's uncommitted work had already landed (the driver committed
it as f7dbba6 "uncommitted work after iteration 78"; the Frangi entry survived the subsequent
PITFALLS sync cfc85d5 and the main merge 6571004), confirmed the suite has no new failures, and
closed the task (dependency 301 is done, so the `Depends on:` line was removed). IF the driver
rejects this done claim, its reasons will be in DECISIONS.md - re-read this section plus the
session-6 entry there, fix, re-run the suite, re-tick.)

**Verified this session (from HEAD, nothing re-touched):**
- fit/inkfit.py carries both session-6 fixes: template_pieces unpacks `kept, label =
  _keep_pieces(...)` (no more (list, label) tuple reaching fit()), and main() points sys.stdout at
  sys.stderr around the fit() call (restored in a finally) so the JSON on stdout stays parseable.
- PITFALLS.md keeps the Frangi-ghost entry (line 727).
- scikit-image==0.26.0 in requirements.in (line 15) and requirements.txt (line 555, pinned +
  hashed); imports clean in the driver's .venv (the driver's pre-session venv build succeeded -
  that is box 2's venv proof).
- `.venv/bin/python -m pytest -q`: 62 passed / 3 failed (64.7 s) vs 4 failed / 60 passed at loop
  start (driver note, 3c8af47): the 218 gate red is gone (merged fix 1dcbc06); the remaining three
  (test_batch_eu::test_union_check, test_batch_eu::test_union_full_coverage_live, test_serve::
  test_platefits_docs_match_sites) are all 211-owned (shotwick doc orphaned / site unbuilt in this
  checkout's web/data/sites.json), per 218's own session entry. No new failures; this task adds no
  tests/ tests (box 5 - the e2e test lands in 302c), so nothing here can regress.
- No frozen parameter of the method was changed in any session of this task.

**State handed to 302b/302c (unchanged from session 6; full details in the DECISIONS session-6
entry and the parent hand-over):** fit(site, picture, model=None, root=None, n_refine=8,
null=True, at=None, log=print) -> result dict (site, plan, model variant, reason, n_pieces,
n_points, seed, objective {fit, scramble, shifted, ...valid}, null, confidence [NEGATIVE = not
confident; no threshold yet - 302b sets it on the held-out table, 302c applies it], placement
{a, b, s_m_px, rot_deg, t_m, u0v0, k}, corners, gate, fabrication, pairs [[u,v,lon,lat]...], doc
[UNWRITTEN, fitter "ink"], notes, seconds). The npz loader reads data/inkfit/relief/<site>.npz
(z, px_m, bbox, optional modern), so 302c's committed test-site npz makes the method fully
hermetic; the data/inkfit/ directory does not exist in the repo yet - 302c creates it. fit() is
deterministic for a fixed image (seed 20261012), never reads data/db/platefits/, and only writes
work-phase dem.npy caches. 302c's committed test-site lessons: box ~1000 m-class around a ~100 m
earthwork (keeps the half-box-shift null valid), and a template with several pieces of differing
lengths/angles (keeps the scramble null discriminating). Measured costs: 1000x1000 m site +
3 searches ~135 s; no fixed ports; writes only data/sites/<sid>/dem.npy (work phase) and, in
tests, the seeded npz under the test root.

**Re-read (for 302c, not this task's job):** pipeline/plan_fit.py:build - the "how" string for
auto:true docs still says "Fitted automatically by the batch..." for a fitter:"ink" doc (the
wording fix is 302c's; plan_fit.py is in the parent's Touches). tools/site_done.py:_fit - the
302c replacement of the batch model loop must keep the covered-pictures rule and the exit codes.
fit/inkfit.py:fit - when 302c routes an unsure fit to the queue, the review reason should name
the margin and which null beat the fit.
