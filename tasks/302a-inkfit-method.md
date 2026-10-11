Status: in-progress
# 302a: The ink-fit method - plate ink against LiDAR relief, no model coordinates
Depends on: 211
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

(2026-10-12, iteration 79, agent c - session 8: **Status: code complete, done-claim pending 211.**
The driver rejected the session-7 done claim (95e3c79), naming three tests as new for this task;
this session diagnosed all three as the shared store's shotwick orphan (206's committed doc,
site unbuilt) - reds owned by 211's merge build, not a 302a defect. No code or data change; per
the team rule (no stand-ins) the task now carries `Depends on: 211`. When 211 has merged, the next
session re-runs the suite and re-claims done.)

**Why the done claim failed (correction to session 7's record).**
Session 7 compared the suite against the WRONG driver note: the older "loop start (4 tests)"
note (3c8af47) listed the three orphans, so "no new failures" looked true. The driver's baseline
for a done claim is its OWN newest loop-start run - the "loop start (1 test: test_gate)" note at
the top of PROGRESS.md's "Project-wide driver notes (newest)" - and there the three orphans were
PASSING. That run must have used a tree that predates the shared store's current state (shotwick
doc absent from data/db/platefits; only the lead's 21st maiden-castle hand doc breaking the
gate's 20-doc count): no live checkout can produce that combination (this checkout: 3 reds;
agent a's: 4 reds per its iter-89 entry). Lesson filed in PITFALLS (This machine and its
environment): diff claims against the NEWEST loop-start note only.

**Root cause, verified live this session.**
- Full suite: 62 passed / 3 failed (64.3 s) - exactly the three the driver named, all on
  shared-store state: 206's committed doc data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json
  points at a site absent from web/data/sites.json -> orphan_docs in batch_eu.union_check (both
  test_batch_eu reds) and `d["site"] in {site ids}` (test_serve::test_platefits_docs_match_sites).
- None of the three touches a 302a file. Since session 7's commit the only 302a-owned change is
  f7dbba6 = session 6's two bug fixes, already verified by session 7; fit/inkfit.py imports
  cleanly (the fit(site, picture, model=None, ...) contract intact) and the scikit-image==0.26.0
  pin is intact (requirements.in line 15, requirements.txt line 555). No frozen parameter moved
  in any session of this task.
- Ownership is 211's, per 206's own archived entries: "(1)-(3) fixed by 211 building shotwick ->
  211 added to my Depends on." web/data/sites.json has a single writer (211's goal: "Nothing else
  in the project writes these files"), and 211's box 3 "Every new site is built" covers shotwick -
  its row is staged in all three *_mackenzie jsonl files (grep-verified this session). Building
  the site myself would break 211's one-writer rule and collide with agent a's in-flight 206.

**Chain to green (no stand-ins possible, hence the dependency).**
206 (open; its deps 001/200/218 are all done now - 218 merged to main as 1dcbc06 - so its next
bring-back should close it) -> 207a/207b (open), 207c (blocked on the human's Roy 1793 copy),
208/209/210 (open) -> 211 (open) merges the build into main -> the driver syncs and the orphans
disappear in every checkout (the per-site dirs are symlinks into the main checkout, PITFALLS).

**Next session (after 211 has merged): exactly three steps.**
1. `.venv/bin/python -m pytest -q`: expect 0 failures (the 218 red is already fixed in this
   branch by 1dcbc06; the three orphans die with 211's build). Any remaining red: if it touches
   a file in THIS task's Touches it is my regression - fix it; if not, record it against the
   owning task and do NOT claim done.
2. Re-verify the five boxes from HEAD (all still ticked, unchanged since session 7): end-to-end
   on two non-held-out sites; scikit-image pinned + venv green; hermetic fit(site, picture,
   model=None) + data/inkfit/relief/<site>.npz loader; the frozen-config DECISIONS entry (before
   any tuning); tests/ untouched (the e2e test lands in 302c).
3. Set Status: done, remove the now-satisfied `Depends on: 211` line, re-tick nothing (all boxes
   stay ticked), re-claim.

**State handed to 302b/302c (unchanged since session 7; full details in the DECISIONS session-6
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
