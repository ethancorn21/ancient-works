Status: in-progress
# 301: Argentoratum (Strasbourg), finished on the map - the second site through the line
Depends on: 300
Touches: web/data/sites.json, web/data/sites/argentoratum-q2361353/, web/data/sites/stonehenge-q39671/, web/data/review.json, data/review/, docs/site_flow.md, docs/site_flow/, tools/site_done.py, pipeline/plan_fit.py, pipeline/build_site.py, tests/test_site_done.py

## Goal
One site at a time, all the way to the map (owner, 2026-10-11). Stonehenge went through first and left the line
as one command (docs/site_flow.md). Argentoratum is next: the batch left 8 automatic fit documents for it
(data/db/platefits/argentoratum-q2361353.*.json, best gate 8.7 m). Take it all the way with the line, and look at
the result the way a visitor does before calling it done.

## Acceptance criteria
- [ ] `tools/site_done.py argentoratum-q2361353` run; every picture of the site is synced to the map or an open
      review item, and its entry in web/data/sites.json counts the synced drawings.
- [ ] Checked in a browser: each synced drawing opened over the ground. A drawing that is visibly in the wrong place
      (streets/walls of the drawing not on the real ones) goes to the review queue with the reason, even if its gate
      passed: a gate of 0.0 m means the points were not checked, not that the fit is right. Screenshot of the best
      drawing at docs/site_flow/argentoratum.png with one line on what it shows.
- [ ] Anything that broke in the line on this site is fixed in the line (not by hand for this site), with a test,
      and one line under "What broke" in docs/site_flow.md. The full suite passes.

## Notes
- The 20 hand fits and their golden file stay untouched.
- Do not start 207 or any other task: the lead gives the next site when this one is done.

## Hand-over
(iteration 67, agent c - investigation done, NO code changed this session; tests last run at
iteration 66: 60 passed, suite not re-run here because only markdown changed. Order: the line's fix
-> run it on Stonehenge -> Argentoratum.)

**The lead's redirect (2026-10-11, mid-session):** before Argentoratum, Stonehenge is not done:
(1) check each of its 7 synced drawings the way a visitor does; anything visibly off goes to the review
queue WITH THE REASON (a gate of 0.0 m means unchecked, not right); (2) find why the gate passed the
Rijksmuseum plan and make the LINE catch it, with a test; (3) correct the false sentence in
docs/site_flow.md; (4) then Argentoratum.

**Findings (full write-up: DECISIONS 2026-10-11 301, two entries):**
- All 7 auto docs are the model's documented fabrication class (batch_us.llm_model docstring, pilots
  4a/4c: identity maps, corner-to-corner, diagonal ladders): round page-px ladders mapped to round
  ground ladders (anchors 100-450 m from the centre on shared lon/lat lines; 4 of 7 have an anchor
  within ~1 m of the site's NOMINAL centre - the catalog coordinate, not a feature); implied scale
  0.80-1.07 m/px = box width / page px (the page frame treated as the 1000x1000 m site box). Docs:
  c_0226 23.2 m, c_098c 7.4 m, c_20f9 44.1 m, c_6933 26.8 m, c_83b4 16.7 m (the Rijksmuseum one),
  c_897a 38.0 m, c_f838 0.0 m (0.0 = its 4 anchors are perfectly consistent - the weakest possible
  evidence, exactly the gate's registered blind spot, gate.md s.7).
- Visually confirmed (composites over relief.jpg; the real sarsens are the small ring at the centre):
  NONE of the 7 sits on the sarsens. c_83b4 is 2-3x too big AND ~70 m off-centre (the lead's exact
  description); the rest are likewise off in scale and/or position. All 7 go to the review queue; the
  site ends with 0 drawings (lead-accepted: the human's drag is the last word). The 6 already in the
  item stay (their why's are fine); the item grows to 13 candidates.
- Why the gate passed: run_sites SOLVES the similarity from the model's own pairs and the gate scores
  that least-squares fit against the same points (docs/gate.md s.2 "true case") - residuals are only
  the ladder's anisotropy/jitter -> med 0-44 m < 45, slope_o 0.02-0.12 < 0.145 -> ACCEPT. The batch's
  3 pre-gate counterchecks pass BY CONSTRUCTION on this class (stated scale == the ladder's own
scale; texture passes: ladder points over structureless plain sit at/above the 400-point null median).
The gate did its registered job; the gate stays frozen (test_gate pins it); the fix belongs in the line.

**Next step (one session): implement the pattern check.**
1. pipeline/plan_fit.py: new pure function `fabrication_pattern(pairs, crop, size, box) -> None | reason`
   (no network; box from data/sites/<sid>/site.json). Any one of:
   (a) 2D lattice: >=3 distinct u AND >=3 distinct v, consecutive gaps near-arithmetic on both axes
       (max/median <= 1.5 AND min/median >= 0.67), >=4 anchors. Fires: c_098c, c_83b4.
   (b) 1D ladder: >=3 anchors collinear (du~0 or dv~0, within a few px) with near-arithmetic spacing
       (same gap rule). Fires: c_0226.
   (c) frame-identity: the solved similarity maps the crop frame onto the site box: centre offset <=
       25% of the box side per axis AND size ratio per axis in [0.7, 1.4]. Fires: c_20f9, c_6933,
       c_897a, c_f838 (and the a/b ones too).
   Validate tolerances: fire on all 7 stonehenge docs AND on none of the 20 hand-fit docs (the golden
   reference, tests/golden/hand_fit_docs.sha256; they are 3-6 irregular feature points - 2x2 corner
   fits exist, which is why (a) needs 3+ per axis). If a hand fit fires, tighten; never loosen so a
   stonehenge doc slips through.
2. tools/site_done.py `_sync`: run the check BEFORE any download for each doc; on a hit: skip the
   build, prune any existing overlay (plan_fit.prune), upsert the review candidate (plan, title, url,
   the doc's pairs, gate_score, why = "line check: fabricated anchor pattern - <which>; the gate's X m
   measures internal consistency of the anchors, not their truth"), include it in the review step and
   the per-picture summary ("sent to the review queue (line check: ...)"). `_entry`/`_review` recompute
   (drawings 7 -> 0; item 6 -> 13 candidates; republish web/data/review.json). Idempotent re-run.
   Then RUN `.venv/bin/python tools/site_done.py stonehenge-q39671` (no --model: all 13 candidates
   covered -> no batch run, no network - pattern docs are rejected before any fetch; the 2 maps need
   no download: the files are already built).
3. Docs: correct the Stonehenge paragraph of docs/site_flow.md ("its circles and stones sit on the real
   sarsens" is false), replace docs/site_flow/stonehenge.png (it shows the wrong fit as if right; the
   page after the fix has no plans for the site - shoot the new state with server/serve.py +
   tools/shot.mjs and give it a true one-line caption), and add the entry under "What broke".
4. Test: extend tests/test_site_done.py in its existing hermetic harness (socket-dead child, tmp copy,
   pinned preconditions): (i) the pattern check fires on the 7 stonehenge docs and on none of the 20
   hand docs; (ii) the line run on the copied site: exit 0, 0 plan webp (pruned), depictions = the 2
   maps, sites.json drawings 0, the item has 13 candidates (7 with the pattern reason), review.json
   republished, second run idempotent. The existing test's goldens pin the OLD (wrong) 7-synced state -
   rewrite them to the new behaviour (the old golden was false, the lead said so).
5. Then ARGENTORATUM (the original goal): `.venv/bin/python tools/site_done.py argentoratum-q2361353`.
   8 auto docs (c_0a0173, c_139946, c_1cb316, c_5bfb04, c_6ba6bb 6 pairs, c_751f93 6 pairs, c_7e281c,
   c_cd8109; best gate 8.7 m) - the pattern check applies to them too; whatever passes both goes on the
   map, the rest to the queue with the reason. Browser-check every synced drawing; screenshot the best
   one to docs/site_flow/argentoratum.png + one line; add anything that broke in the line to "What
   broke". CAUTION: its web/data/sites.json entry is MISSING (s.get returned null) while
   web/data/sites/argentoratum-q2361353/ exists (cassini, etatmajor, fr_ortho1950 maps + relief) - the
   line exits 2 "not built" until the entry exists (box 1600x1600 m, kind roman_fort, Q2361353).
   Re-read: pipeline/build_site.py:entry_of/write_entry - how one site's entry is built without touching
   other sites' entries, and check git log (`git log --oneline -- web/data/sites.json | head`) for when
   the other built sites' entries were written (212?) - the entry may simply never have been built for
   this site yet.

**Re-read:**
- Re-read: fit/batch_us.py:llm_model + _parse_answer + _feature_present - confirm the new line check
  (a/b/c) is independent of (not a copy of) those three pre-gate checks, and that the 7 docs are the
  ones the pre-gate checks let through (not the 6 in the item).
- Re-read: pipeline/plan_fit.py:prune - exactly what it removes (webp, ink, depiction entry, count
  refresh) so the line's prune path leaves no stale files or stale depiction rows.
- Re-read: tools/site_done.py:_fit - `need_fit` for a site whose docs all pattern-reject (they still
  cover their candidates via pre_docs, so no batch run; confirm the covered count and the summary still
  hold when a doc is both in pre_docs and (newly) in the item).

**Environment:** system python3 has NO numpy - use .venv/bin/python for anything importing pipeline/ or
fit/. The driver's ".venv could not be built" note (2026-10-10, PROGRESS.md) is STALE: task 800 pinned
requirements.txt and the venv builds; the suite ran green (60 passed) at iteration 66. Do not run git
merge/rebase/reset/stash/branch switches. Agent a works on 206 in its own checkout; 207 waits on the
human - neither is yours.
