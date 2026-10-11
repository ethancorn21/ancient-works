Status: done
# 203a: The batch, US - the 90 US built sites
Depends on: 001, 200, 201, 202, 802, 803
Touches: fit/batch_us.py, data/db/platefits/, data/review/, docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256, tasks/802-gate-holdout-auto-docs.md, tasks/803-review-queue-rebaseline.md

## Goal
GOAL.md point 2: the local model does the fitting itself, the way the 25 hand fits were made. For
every US built site in web/data/sites.json (region "US", 90 of 384): candidates = the plans.json
rows whose "sites" contains the site (with 200's evidence field where present). For each candidate
picture: build the fitkit sheet (`tools/fitkit.py sheet` - the picture's crop next to the site's
ground, relief or the aerial photograph where there is no LiDAR, both gridded) and let the local
vision model (`pipeline/llm.py`) read the grid labels, find the same features on both sides (wall
corners, gate gaps, bastion tips, road junctions, church footprints, river crossings), and record at
least four point pairs (202's seed is its starting point where one exists; a
code/north/centre-only placement is never the fit). The pairs go through the existing `plan_fit`
similarity solver and then the gate (001): accepted fits become automatic platefit documents in
data/db/platefits/ with the gate's score and an "auto" mark; a gate refusal, or a picture the model
could not fit (fewer than four pairs), becomes a review item in data/review/ in 201's format
carrying those pairs; a site with no candidate at all gets an item marked "no picture found"
(point 1: fit or item). The 20 existing hand-fit documents are never touched. 203b (the rest of
the world) reuses this module's loop.

## Acceptance criteria
- [x] Before the first batch write: tests/golden/hand_fit_docs.sha256 is committed, listing all
      20 pre-batch platefit documents (file name + sha256) and the 19 hand-fit sites'
      data/sites/<id>/site.json files.
- [x] fit/batch_us.py runs the loop for a set of US sites: for each site, every candidate picture
      goes fitkit sheet -> model (>= 4 matched-feature pairs, 202's seed as starting point) -> fit
      -> gate; the accepted ones write automatic platefit documents (existing format + score +
      "auto" mark) and the rest become review items (the model's pairs where it made any); a site
      with no candidate at all gets an item marked "no picture found". The loop is a function 203b
      can import and point at its own site list, with the model step injectable.
- [x] In the full working-phase run (all 90 US sites, recorded in the report), every US site
      ends with at least one automatic document or an open review item - or an existing hand
      fit.
- [x] After the run the 20 hand-fit documents and the 19 site files are byte-identical to the
      golden hashes; the batch added files, it rewrote none.
- [x] docs/batch_us.md: counts (automatic fit / review item / already hand-fitted / no picture
      found), the recorded seed, and the seeded sample of automatically accepted fits (20 where
      there are at least 20; a page URL each) for the human's 18/20 check.
- [x] Test (no network, port 0, no model-server call): the loop run on a fixed sample of US sites
      with in-repo ground, the model step supplied a fixed recorded answer, produces, per site, a
      document or an item in the right format; the hand-fit files are byte-identical; the report's
      sample is reproducible from the recorded seed.

## Notes
- Ground: the in-repo images (web/data/sites/<id>/) carry the test fits (fitkit convention:
  relief where there is, aerial otherwise). The full run uses the same convention per site;
  fetches happen only in the working phase, never in tests.
- The page-facing sync (overlays, drawings counts) is NOT this task's job: the documents sit
  in data/db/platefits/ and 212 syncs them to the page in one pass.
- The golden hashes cover the pre-batch state of THIS checkout; regenerate them if the batch
  has already been partially run, but never edit them to make a failure pass.
- The model call is injectable by design: the working phase calls `pipeline/llm.py` on the fitkit
  sheet; tests supply a fixed recorded answer so no test touches the model server (GOAL: what the
  model says is a lead to check, not a fact — the gate is the check).

## Hand-over

Session 4j (iteration 48). Status: DONE - the done claim is filed this session; the
driver re-checks (all boxes ticked + full suite green on my branch). If it rejects,
the reason lands in DECISIONS.md or this file's Notes - read that first, fix, re-file.

The human's 002 answer ("approved, your recommendation: you get 802 as a job now,
then 803, then 203a again to re-file the done claim") is fully spent: iteration 47
implemented 803 on top of 802 and verified both states; the driver committed 47's
uncommitted tests/test_review.py (be70182, that file only), accepted both done
claims, and merged agent/c into main (main's top is be70182; my branch = main +
driver housekeeping). Both task files: Status: done, every box ticked.

Re-verified this session on the post-merge checkout (fresh eyes, before filing):
- Full suite `.venv/bin/python -m pytest -q`: 38 passed / 0 failed (43 s) - 802's
  recorded-measurement test and 803's three derived review tests all green.
- Golden: sha256sum -c tests/golden/hand_fit_docs.sha256 = 39/39 OK.
- 802's live invariant: 36 docs = 16 auto (all with a numeric score) + 20 non-auto
  whose names set-equal the golden's 20 hand-fit names.
- 803's live premise: 89 review items, 88 derived open through 201's export rule.
- docs/batch_us.md unchanged since the working run: 9 auto / 8 item / 2 hand-fitted
  / 71 no-picture = 90 sites; seed 20261010; sample = all 16 auto fits (16 < 20, so
  the "20 where >=20" bar is met by listing all), each row with a page URL.
All six boxes were verified in 4e/4f (working run + golden + report); nothing of
this task changed since, and the re-verification above re-proves boxes 1, 4, 5
against the post-merge state. Box 3 arithmetic: every site's candidates end as
auto, reject-item, could-not-fit-item, skip (existing doc) or no-picture; 9 + 8 +
2 + 71 = 90, so every US site ends with a fit or an open item - or an existing
hand fit.

For 203b (the other 294 built sites; imports run_sites/write_report from
fit/batch_us.py): site list = region != "US" plus the 6 region-less sites; keep
is_pre_fit's site.json["plate"]["fit"] branch (the region-less hand fits live
there); report docs/batch_eu.md; shared SEED 20261010; the texture-presence check
degrades to a no-op on aerial ground (documented in the module docstring; the gate
+ human sample remain the authority). Its run will extend data/review/ and
data/db/platefits/ again: 803's derived tests and 802's non-auto filter are
state-agnostic by design and absorb that. For any test that builds a human-save
document: read the row from web/data/plans.json, not the item's stored entry (the
batch's upsert wrote slim entries; see PITFALLS, fit/).
