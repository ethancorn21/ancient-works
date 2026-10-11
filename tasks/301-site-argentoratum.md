Status: in-progress
# 301: Argentoratum (Strasbourg), finished on the map - the second site through the line
Depends on: 300
Touches: web/data/sites.json, web/data/sites/argentoratum-q2361353/, web/data/sites/stonehenge-q39671/, web/data/review.json, data/review/, data/db/platefits/, docs/site_flow.md, docs/site_flow/, tools/site_done.py, pipeline/plan_fit.py, tests/test_site_done.py, tests/golden/

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
(iteration 71, agent c - Stonehenge's docs are TRUE again: site_flow.md corrected and stonehenge.png replaced
with the current visitor state (0 drawings, uncoloured marker, 13 candidates in the review item). Suite 60
green. Next: the golden-seeded rewrite of tests/test_site_done.py, then Argentoratum through the line.)

**What was done and committed (iteration 71):**
- docs/site_flow/stonehenge.png replaced: served the LIVE checkout (server/serve.py --port 0, ephemeral
  port) and shot with `NODE_PATH=/home/agent/tools/shot/node_modules node tools/shot.mjs <url> <out>
  1000 1200 800 "<probe>"`, POSTWAIT=8000 (the probe awaits loadDeps, then the 4.5 s map flyTo must
  finish). Probe: poll until S.ready && S.sites.length, then select('stonehenge-q39671'),
  await loadDeps(S.byId[...]). Its [eval] reported drawings: 0, depFiles: ["map:six-inch-1st.webp"],
  ground: "imagery", RV loaded with 339 open items. The photo shows exactly that: aerial ground,
  panel group "Old maps and aerials" with only the 1842 six-inch OS map (the 1900 one-inch is hidden
  by the 150-year rule), no drawings group, uncoloured map markers. ArcGIS World_Imagery
  ERR_ABORTED lines during the flyTo are normal in-flight aborts; the photograph loads anyway.
- docs/site_flow.md: (1) the Stonehenge paragraph rewritten - no batch run (13/13 covered), the line's
  pre-sync check found all 7 docs to be the fabrication class, all 7 upserted to the item with the
  reason and deleted, site ends 0 drawings, entry stays 0, item 6 -> 13 candidates, 339 open of 340,
  a human's saved fit puts the first drawing on; (2) the png caption bullet is now true; (3) new
  "What broke" entry: the gate passed the 7 fabricated fits by construction (gate.md s.7's registered
  limit; residuals 0-44 m; one fit 2-3x too large and ~70 m off-centre) and the line's
  plan_fit.fabrication_pattern (grid roundness + 2D lattice + 1D ladder on stored page-px pairs, pure)
  now catches the class before sync - fires on all 110 batch docs (at calibration), none of the 20
  hand docs; (4) "Files the line touches" no longer claims data/db/platefits is byte-identical (the
  line deletes pattern docs after upserting the candidate); (5) step 2 (sync) describes the pre-sync
  check before the build.
- Suite: 60 passed, unchanged.

**State on disk (unchanged since the previous commit, re-verified):**
- stonehenge-q39671: 0 docs in data/db/platefits (the 7 deleted ones live in git: git show
  b84d147^:data/db/platefits/stonehenge-q39671.<plan>.json, plans c_022604d2be0becdc
  c_098c4cb138676939 c_20f9f11153a0b7f0 c_6933e3a931a0240a c_83b4d6df7a6d2383
  c_897a5c1632e2fdd6 c_f8386b6404e4ee63); dep = six-inch-1st.webp + os1inch.webp; drawings 0; item
  data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json = 13 candidates (6 originals
  byte-identical + 7 with whys starting "line check:"), resolved None; review.json stonehenge =
  13, 339 open of 340.
- argentoratum-q2361353: 8 auto docs (all 8 hit fabrication_pattern - verified in the calibration
  session), item with 34 candidates, drawings 0, dep = 2 maps + 1 aerial.

**Next step (ONE step, then commit): TESTS - rewrite tests/test_site_done.py** (it currently passes
vacuously: 0 docs in the repo -> nothing to check). Make it coverage of the check by seeding the
pre-run state:
1. New goldens (add `tests/golden/` to the Touches line first): (a) the 7 deleted stonehenge docs -
   recover verbatim from git history (`git show b84d147^:data/db/platefits/stonehenge-q39671.<plan>.json`
   for the 7 plans above) into tests/golden/ (e.g. stonehenge_linecheck_docs/, one file per doc,
   keeping the original file names); (b) the PRE-run item = the current 13-candidate item minus its
   7 candidates whose why starts with "line check:" (deterministic: the upsert only appended) -
   derive it in the test (or commit it as a golden too); (c) the EXPECTED post-run item = the repo's
   current 13-candidate item itself (the assertion target).
2. Test body (keep the existing socket-dead GUARD harness and temp-tree copy): seed the 7 docs into
   the tree's data/db/platefits and the pre-run item into the tree's data/review; the site dir and
   sites.json stay as in the repo (2 maps, 0 drawings); run the copied line
   (`site_done.py --root <tree>`); assert: exit 0; the fit line "13 candidate picture(s): 7 fitted
   (doc), 6 in the review item -> no batch run needed"; 7 "sent to the review queue (line check:
   ...)" lines; NO plan webps created in the site dir; the site's depictions.json byte-identical to
   the repo's; sites.json byte-identical (drawings 0); the upserted item file byte-identical to the
   repo's current 13-candidate item; the 7 seeded docs GONE from the tree's platefits; review.json's
   items identical to the repo's; no other site's file touched anywhere in the tree (this pins the
   scoped-prune fix); second run idempotent (0 docs -> no batch run; 13 summary lines; only
   review.json's "at" changes). Keep the existing loud-fail precondition style if the repo drifts
   (e.g. a doc reappears, the item candidate count changes).

**Then (order):**
1. ARGENTORATUM: `.venv/bin/python tools/site_done.py argentoratum-q2361353` (live checkout): expect
   all 8 auto docs to hit the check -> upserted into the item (34 -> 42 candidates, resolved stays
   None, the 34 originals byte-identical and in order), 0 docs left, drawings 0 -> 0, exit 0. The
   "browser-check each synced drawing" part of box 2 is satisfied vacuously (0 drawings synced) -
   document that when ticking. Screenshot the site page (same shot recipe as stonehenge, probe
   select('argentoratum-q2361353')) to docs/site_flow/argentoratum.png with a one-line caption on
   what it shows (box 2).
2. Tick the boxes only as they are verified; box 3's "one line under What broke" is already written
   (the fabrication-check entry) - if nothing else breaks on Argentoratum, box 3 rests on the test
   step + the full suite.

**Re-read (carried over, still fresh-eyes due):**
- Re-read: tools/site_done.py:_fit - on a re-run after a pattern doc was deleted, the picture is
  covered via item_cands (not docs), so no batch run re-fits it with a model (verified on the
  second stonehenge run: "0 fitted (doc), 13 in the review item").
- Re-read: fit/review.py:upsert_item - merges by plan; a same-plan candidate is REPLACED whole, so
  a later re-upsert (e.g. a batch run that re-fits the picture) overwrites the "line check:" entry -
  intended: the newest word wins until a human saves.

**Environment:** .venv/bin/python for anything importing pipeline/ or fit/ (the venv builds fine;
the driver's 2026-10-10 note is stale). Screenshot recipe: server/serve.py --port 0 (ephemeral, no
fixed ports) + node tools/shot.mjs with NODE_PATH=/home/agent/tools/shot/node_modules and
POSTWAIT>=8000 (map flyTo is 4.5 s). Nothing writes outside project + temp dir. Do not run git
merge/rebase/reset/stash/branch switches. Agent a works on 206 in its own checkout (its files:
fit/src_mackenzie.py etc. - not yours). Do not start other tasks; the lead gives the next site when
this one is done.
