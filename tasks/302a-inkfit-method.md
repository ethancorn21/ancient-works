Status: done
# 302a: The ink-fit method - plate ink against LiDAR relief, no model coordinates
Depends on: none
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

(2026-10-12, iteration 80, agent c - session 9: **DONE.** The 211 block lifted by 206's merged
site build (465db31), not by 211 itself; the suite is fully green against the driver's newest
loop-start baseline; all five boxes re-verified from HEAD. `Depends on: 211` removed: the blocker
it guarded is resolved, and 211 itself still waits on the human-blocked 207c, so keeping the
line would block a done task forever. If the driver reopens: the only way red can return is the
shared store's state (the batch_eu/serve tests key on data/db/platefits + web/data/sites.json,
both main-branch-backed) - re-run `.venv/bin/python -m pytest -q` and diff against the NEWEST
loop-start note only (PITFALLS, This machine and its environment).)

**Correction to session 8's diagnosis.** Session 8 added `Depends on: 211` because the 3
driver-rejection reds (the shotwick orphans) looked fixable only by 211's merge build. Wrong:
206 itself built the shotwick site in 465db31 (build_catalog: EA 1 m LiDAR + OS six-inch 1st ed;
web/data/sites.json 384->385), on main, synced into this branch by 1cbc048 before this session -
206's own done entry (iter 92, below mine in DECISIONS.md) states the 3 reds are gone and the
suite is 64 passed / 1 skipped / 0 failed, exactly what I measured here. 211's consolidation
never did the work; it is still open, waiting on a chain that includes the human-blocked 207c.
Lesson: a "can only come from X" argument must name the commit that actually does the work; here
206's own goal (build the site it fits) was the right owner, and the lead's cycle-cut (0be0b09)
had already cut 211 out of 206's deps.

**Verified live this session (all from HEAD; no code or data change):**
- Full suite: 64 passed, 1 skipped, 0 failed (63.7 s). The one skip is test_batch_eu's
  union_full_coverage_live self-check (docs/batch_eu.md "Sites run: 294" vs the live EU list 295 -
  population drift owned by 211; it skips by design, it is not a failure). Against the driver's
  newest loop-start note (1 failed: test_gate / 59 passed): the gate red is fixed in this branch
  by 1dcbc06 (merged 218: gate_heldout derives over the 20 registered names, post-registration
  hand docs tolerated - per 206's done entry), and the three orphans are gone with the
  sites.json entry. No red at all, new or old.
- Box 1 (end-to-end, two real non-held-out sites): verified in sessions 5-6 (stonehenge + a US
  1848 site; ink template from the plate image, real 1 m-class relief via dem_sources, placement
  with ink pairs, no platefit read). The only change to fit/inkfit.py since is f7dbba6 (the
  driver's commit of session 6's two bug fixes: template_pieces tuple unpack, CLI stdout
  redirect); no frozen parameter moved in any session of this task.
- Box 2 (scikit-image pinned): scikit-image==0.26.0 in requirements.in:15 and
  requirements.txt:555 (the last commit to touch either file is e46f5fd, this task's pin commit);
  the driver's .venv build is green (the suite ran on it this session).
- Box 3 (hermetic fit + npz loader): fit(site, picture, model=None, ...) intact at
  fit/inkfit.py:527; the loader accepts data/inkfit/relief/<site>.npz (z, px_m, bbox, optional
  modern). The data/inkfit/ directory does not exist in the repo yet - 302c creates it with the
  committed test-site npz; the box only needs the loader to accept it.
- Box 4 (frozen-config DECISIONS entry): the sessions 2/3 registration stands untouched; nothing
  was tuned in any session of this task.
- Box 5 (tests/ untouched): this task wrote nothing under tests/ (the e2e test lands in 302c);
  the skip and every test above touch no 302a file.

**State handed to 302b/302c (unchanged since session 7; full details in the DECISIONS session-6
entry and the parent hand-over):** fit(site, picture, model=None, root=None, n_refine=8,
null=True, at=None, log=print) -> result dict (site, plan, model variant, reason, n_pieces,
n_points, seed, objective {fit, scramble, shifted, ...valid}, null, confidence [NEGATIVE = not
confident; no threshold yet - 302b sets it on the held-out table, 302c applies it], placement
{a, b, s_m_px, rot_deg, t_m, u0v0, k}, corners, gate, fabrication, pairs [[u,v,lon,lat]...], doc
[UNWRITTEN, fitter "ink"], notes, seconds). The npz loader reads data/inkfit/relief/<site>.npz
(z, px_m, bbox, optional modern), so 302c's committed test-site npz makes the method fully
hermetic. fit() is deterministic for a fixed image (seed 20261012), never reads
data/db/platefits/, and only writes work-phase dem.npy caches. 302c's committed test-site
lessons: box ~1000 m-class around a ~100 m earthwork (keeps the half-box-shift null valid), and
a template with several pieces of differing lengths/angles (keeps the scramble null
discriminating). Measured costs: 1000x1000 m site + 3 searches ~135 s; no fixed ports; writes
only data/sites/<sid>/dem.npy (work phase) and, in tests, the seeded npz under the test root.

**Re-read (for 302c, not this task's job):** pipeline/plan_fit.py:build - the "how" string for
auto:true docs still says "Fitted automatically by the batch..." for a fitter:"ink" doc (the
wording fix is 302c's; plan_fit.py is in the parent's Touches). tools/site_done.py:_fit - the
302c replacement of the batch model loop must keep the covered-pictures rule and the exit codes.
fit/inkfit.py:fit - when 302c routes an unsure fit to the queue, the review reason should name
the margin and which null beat the fit.
