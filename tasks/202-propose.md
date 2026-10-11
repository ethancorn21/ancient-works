Status: done
# 202: Proposed point pairs — a placement a person finishes in a minute
Depends on: none
Touches: fit/propose.py, tests/test_propose.py, tests/golden/propose_202.json

## Goal
Given a site and an old picture, produce the STARTING POINT for the fit: the anchor (scale bar and
north arrow where recorded, else the site centre) plus 3-5 pairs on drawn features. Since the GOAL
change of 2026-10-10 (point 2), the primary consumer is the model's fitting pass (203a/203b): the
model starts from this anchor and the few pairs, then looks at the fitkit sheet and records at least
four matched-feature pairs of its own. A review item (201) shows the same starting point to the human
when the model could not fit. Explicitly: a placement from a scale bar, a north arrow and the site
centre alone is a starting point, not a fit — it never goes to the gate as a fit and never becomes a
platefit on its own. Fitting by matching point pairs works (25 hand fits); the fully automatic
fitting bet (docs/autofit.md, 0/5) is not re-run.

## Acceptance criteria
- [x] For a book plate with a scale bar and north arrow (the stage-B fields of data/books/index.jsonl:
      `scale_bar`, `scale_text`, `north_angle_deg`, `map_box`): the placement anchors the plate at the site
      centre with the recorded scale and rotation; 3-5 proposed pairs on drawn features of the plate
      (plan corners, straight lines), in page pixels. [verified: test_sample_format + test_no_snapping +
      test_self_consistency + golden; 12 non-coarse book rows: 6 S&D ratio + 6 Allcroft bar, anchored at site
      centre, rot from hint, 3-5 pairs in page px]
- [x] For a picture with no scale information (bird's-eye views, engravings): a coarse anchor (site centre,
      picture centre, scale from the picture size where possible) with 3-5 pairs flagged coarse — the human
      drag is expected to do the work (fixed landmarks carry these fits: roads, churches, river crossings,
      field edges). [verified: golden coarse rows serpent/arbor-low/aztalan picture_size + 3 commons
      picture_size; test_ground_rule_aerial for the no-LiDAR aerial branch]
- [x] Pairs are page px → lon/lat exactly as a platefit doc stores them; the ground they refer to is the
      site's ground image (relief, or aerial for a site with no LiDAR — the fitkit `FITKIT_GROUND`
      convention). Pairs are proposed, never snapped. [verified: test_no_snapping (pairs exactly on the
      recorded map_box geometry, px 1 dp / lon lat 7 dp as a platefit doc stores them) + ground assertions:
      18 relief + the aerial rule for a no-LiDAR site]
- [x] Test (no network): a fixed sample of (site, picture) pairs using in-repo ground (the six tracked
      hand-fit sites) → golden file of the proposed placements; sanity check in the golden file: a re-fit
      from the proposals of a hand-fit site lands within the hand fit's own residual range. [verified:
      test_golden (byte-exact) + the three sanity tests — QID nine / old-style six (marietta excluded,
      measurement recorded) / commons three — the Option B reading of "re-fit from the proposals lands
      within the hand fit's own residual range", DECISIONS entry 2026-10-11; full suite 29 passed]

## Notes
- Import the shared helpers read-only: `pipeline/aw.py` (Mercator), `pipeline/plan_fit.py` (the solver, to
  evaluate your own proposals in the test).
- The proposal is deliberately crude where the evidence is crude: a scale-bar anchor beats a texture
  search, which is the bet that already failed.
- The model's own pair recording (203a/203b) supersedes this seed wherever the model does better; this
  output is never treated as the fit (GOAL point 2).

## Hand-over

DONE (iteration 29, agent c). All four boxes ticked, `Status: done`, full suite 29 passed, committed.

### Final state (for anyone re-opening this task)
- `fit/propose.py` (committed aeb433d, iter 27): stdlib-only; `propose_for(site_id, plan_id)` returns the
  7-key contract dict; the 203a/203b model path feeds its pairs to `plan_fit.similarity` verbatim.
- `tests/test_propose.py` (11 tests, no network/server/writes; import sys.path to fit/ + pipeline/;
  plan_fit in try/except so a red venv skips the 8 fit-dependent tests, the 4 stdlib ones run):
  parse_scale table (27 corpus cases, known-bad -> None); sample format (18 proposals: 3-5 pairs,
  px 1 dp / lon lat 7 dp, in-frame, coarse flag, scale_source, ground); no-snap (u/v == recorded
  map_box corners + centre, or page corners + centre); aerial rule on bibracte (rule-level: bibracte
  has NO plans row - re-verified, 0 rows - so the aerial branch is a rule check, golden sample is 18);
  self-consistency (re-fit recovers the anchor: worst 5.2e-5 m/px, 0.0003 deg vs tolerances
  1e-3 m/px or 2%, 0.1 deg); QID-nine + old-style-six + commons-three sanity; byte-exact golden; CLI;
  20 platefit docs byte-identical through the run.
- `tests/golden/propose_202.json`: 18 sample proposals + measured sanity (hand m_per_px/rot/maxresid +
  measured dev/drot/dist/envelope + checks; null = not applied). Regenerate ONLY for an intended change:
  `.venv/bin/python tests/test_propose.py --regen`.
- Verified facts to keep: bibracte-q650053 has no plans.json row (aerial = rule-level check, never a
  golden pair); fudge's S&D ratio is 0.2438 m/px (400 ft / 500 ppi); serpent's doc size is its
  full_size [2884, 4064]; marietta's old-style exclusion is guarded by an assert (min ratio < 0.2) and
  calleva's QID exclusion by one too (dev > 50%) - if a data fix ever makes one pass, delete the
  exclusion, never loosen the envelope.
