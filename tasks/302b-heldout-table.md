Status: in-progress
Depends on: 302a
# 302b: The one-shot held-out measurement - 21 hand fits, corner error against the method
Touches: fit/inkfit_heldout.py, data/inkfit/, docs/site_flow.md

## Goal
Measure the ink-fit method against the hand fits as truth, held out (the method never reads the hand
pairs; only the evaluator does), and record the numbers in docs/site_flow.md, good or bad - the
acceptance of the whole task is read off this table. The runner `fit/inkfit_heldout.py` (checkpointing
per site, like autofit.run, so a cut session continues) takes the 21 hand-fit documents (the original
20 of tests/golden/hand_fit_docs.sha256 plus the lead's 21st, maiden-castle-q1232816.c_c20ff6b1f16d173d,
no auto flag on main), runs the frozen method of 302a on each (the method sees only the site, the plate
image and the relief), and for each writes: the corner error in metres (RMS over the 4 full-image
corners mapped to ground, autofit.Site.corner_rms convention) between the method's similarity and the
hand fit's similarity (plan_fit.similarity on the doc's pairs), plus rotation error, scale ratio, the
frozen gate's verdict on the method's own pairs, whether plan_fit.fabrication_pattern is silent on them,
and the search-matched-null margin.

## Acceptance criteria
- [x] BEFORE the run: a committed section in docs/site_flow.md registering the protocol - the frozen
      configuration, the 21 sorted document ids, the corner-error metric, the null recipe, and the
      statement that the method never sees the hand pairs. The run may only happen after this commit.
- [ ] The one-shot run completed on all 21 documents (network for DEMs/pictures allowed in the working
      phase; results checkpointed under data/inkfit/heldout/).
- [ ] The table in docs/site_flow.md: one row per document with the numbers above, reported verbatim as
      measured (no cherry-picking, no re-tuning of anything on this table except the 302c confidence
      threshold, which box 3 of the parent authorises).
- [ ] The fabrication check passes every automatic fit the method produced (every row: fabrication_pattern
      silent). If any row fired, that is recorded here as a method defect, not fixed by editing the table.
- [ ] A DECISIONS.md entry: the table summary, which sites fit and which did not, and what that means
      for the 302c threshold.

## Hand-over

(2026-10-11, iteration 81, agent c - session 1. Box 1 DONE: the pre-registration is committed; nothing else touched.)

**State.** `Status: in-progress`. Box 1 is ticked and verified: docs/site_flow.md ends with the
pre-registered protocol section (commit 9e078c8, after HEAD 606e518): the 21 sorted no-auto doc
ids (the 20 of tests/golden/hand_fit_docs.sha256 + the lead's 21st), the frozen config (as of
fit/inkfit.py @ f7dbba6: extractor, no-model variant, relief 1 m/px LRM 24 m clip 1 m, propose
seed, window +-25 deg / x0.74..x1.36 / +-200 m, coarse 2 deg / 0.04 log / 4 m + 8-candidate
refine, objective mean(max(contrast,-0.2)) with -9.0 floor, search-matched null = max of
scrambled-template (seed 20261012) and DEM shifted half-box N/E, point recipe 0.23/0.71 quantiles
<=2/piece <=10 >=4 with 8 fabrication-pattern redraws, frozen gate, one-shot checkpointing into
data/inkfit/heldout/results.json), the corner-error metric, and the statement that the method
never reads the hand pairs. **The one-shot run may not start until that commit exists (it does);
the next session's step is box 2.**

**Verified facts this session (trust them):**
- 302a is done/merged; fit/inkfit.py is complete and frozen (last commit f7dbba6). This checkout
  already has the driver's main sync (1cbc048): data/db/platefits/maiden-castle-...c20ff6b1f16d173d.json
  is the no-auto version (3 hand pairs, crop [165,256,895,663]); all 21 held-out docs verified
  auto=None by script.
- All 21 docs resolve for the runner: `plan = doc.split(".", 1)[1]`, `site = doc.split(".", 1)[0]`;
  `propose._plans_row(plan, site)` finds a row for all 21; `propose._site(site)` finds all 19
  sites, every one with `size_m` (800-2400 m). Book docs: 9 (earthworkenglan01allcgoog pages
  n0597/n0581/n0132/n0360/n0108/n0124/n0142, antiquitiesofwis00saph n0182, ancientmonuments00squi
  n0210) - scans present in data/raw/books/<ia>/full/. Commons: 12; the 11 originals have their
  big in data/raw/commons/big/, the 21st (maiden-castle c_c20ff6b1f16d173d) needs the on-demand
  big fetch (network, working phase).
- `aw.ground_scale(lat)` = GROUND metres per Mercator metre (= cos lat, checked numerically:
  0.6335 at 50.69 deg). So the corner-error formula in the protocol multiplies the
  Mercator-space corner difference by `aw.ground_scale(lat0)` (NOT its reciprocal - inkfit's
  map_pairs divides because it goes the other way). My first draft had the reciprocal; caught
  before committing.
- `plan_fit.similarity(pairs)` -> (a, b, residuals_ground_m, k) with merc = a*(u - i v) + b -
  the SAME convention as inkfit's placement dict {a: [re, im], b: [re, im]}, so the evaluator
  needs no conversion between the two.
- autofit constants (resolved values for the runner's reference, all imported by inkfit by
  reference): WIN_ROT = radians(25), WIN_LOGS = (log(0.74), log(1.36)), WIN_T = 200.0,
  ROT_STEP = radians(2), LOGS_STEP = 0.04, CELL_M = 4.0, NEG_FLOOR = -0.2; autofit.run
  (pipeline/autofit.py ~line 365) is the checkpoint pattern to mirror: one results_<tag>.json,
  one entry per unit, rewritten after each unit, json.dump with default= for numpy scalars.
- inkfit.fit result fields the table uses: reason (None on success), model (variant label),
  n_points, objective {fit, scramble, shifted}, null, confidence (= fit objective - null, the
  "search-matched-null margin" of the task), placement {a, b, ...}, gate {verdict, n, med,
  slope_o, io} (the frozen gate on the method's own pairs), fabrication (None = silent;
  otherwise the fired clause string = the method-defect record for box 4), pairs.
- DEM fetches: 19 sites, 800-2400 px at 1 m/px, sources ea/usgs/ign (all reachable from this VM
  per the parent hand-over); cached to data/sites/<id>/dem.npy (gitignored) so a resumed
  session does not refetch.

**The runner (fit/inkfit_heldout.py - box 2, write it next session).**
1. DOC_IDS = sorted(the 20 ids parsed from tests/golden/hand_fit_docs.sha256 + the literal
   "maiden-castle-q1232816.c_c20ff6b1f16d173d") - must equal the 21 in the protocol section
   (assert that).
2. results file data/inkfit/heldout/results.json: {"docs": {doc: entry}}; resume = skip an
   entry that has no "error" key; an entry WITH "error" (an exception, never a completed
   measurement) MAY be re-run once, and every such re-run must be disclosed in a footnote of
   the final table.
3. Per doc: se = propose._site(site); row = propose._plans_row(plan, site); r =
   inkfit.fit(se, row, model=None, null=True, at=<fixed iso timestamp for the run>); wrap in
   try/except and record {"error": repr(e)} on exception. Evaluator (the ONLY reader of the
   hand doc): doc = json.load(data/db/platefits/<doc>.json); a_h, b_h, _, _ =
   plan_fit.similarity(doc["pairs"]); W,H = doc.get("size") or the row's size;
   a_m, b_m from r["placement"] (or absent); corners (0,0),(W,0),(W,H),(0,H) as w=u-iv;
   k0 = aw.ground_scale(mean hand-pair lat); corner_error_m = k0*sqrt(mean|dm*w+db|^2);
   drot_deg = wrap180(degrees(arg(a_m)-arg(a_h))); scale_ratio = |a_m|/|a_h|;
   gate_silent = r["fabrication"] is None; gate = r["gate"]; null margin = r["confidence"].
4. Print one progress line per doc; finish by printing the full table in markdown (to paste
   into docs/site_flow.md verbatim - box 3).

**Traps.**
- docs/site_flow.md is shared with agent a (task 303 touches it too). My section is at the END
  of the file; my table will be appended under it. Do not reflow anything above - merge
  conflicts are the driver's to resolve.
- The golden file tests/golden/hand_fit_docs.sha256 is parsed but NEVER edited (20 docs).
- A single doc takes minutes (3 searches on a 800-2400 px grid; the 10-10 run did similar).
  21 docs will span sessions - that is why the checkpoint exists. Do not "warm up" or
  re-measure any completed doc; the only permitted re-run is an exception entry.
- The table reports verbatim what the checkpoints say, including any failed-to-place docs
  (reason in the row) and any fired fabrication clause (that is a method defect, box 4, not
  something to fix by editing).

**Exact next step (session 2):** write fit/inkfit_heldout.py per the runner design above
(the Touches line already names it), sanity-check the evaluator on ONE already-fitted doc by
comparing its hand similarity against itself (corner error must be 0.0) - that self-check
uses no network and no method call; then start the one-shot run (docs in the protocol's
sorted order) and let it checkpoint. When all 21 rows exist: box 3 (paste the verbatim
markdown table into the site_flow section, with a footnote disclosing any exception re-runs
and the run's at-timestamp), box 4 (state for each row whether fabrication_pattern was
silent - every automatic fit the method produced must be silent; any firing stays recorded as
a method defect), box 5 (DECISIONS.md entry: table summary, which sites fit/did not, and what
it means for the 302c confidence threshold).

**Re-read:** fit/inkfit_heldout.py:resume - skip logic (no "error" = done; "error" = may
re-run once, footnote). fit/inkfit.py:choose_points + the final fabrication re-check in
fit() - both must be silent on every produced doc (box 4). docs/site_flow.md:the table -
verbatim match against data/inkfit/heldout/results.json (the driver re-checks the claim).
