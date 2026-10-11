Status: in-progress
# 301: Argentoratum (Strasbourg), finished on the map - the second site through the line
Depends on: 300
Touches: web/data/sites.json, web/data/sites/argentoratum-q2361353/, web/data/sites/stonehenge-q39671/, web/data/review.json, data/review/, data/db/platefits/, docs/site_flow.md, docs/site_flow/, tools/site_done.py, pipeline/plan_fit.py, pipeline/build_site.py, tests/test_site_done.py

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
(iteration 70, agent c - the line's fabrication check is WIRED and the line ran on Stonehenge;
Stonehenge is now on the map as 0 drawings / 13 review candidates. Suite 60 green. The docs and
test steps of the hand-over's order remain, then Argentoratum.)

**What was done and committed (iteration 70):**
- tools/site_done.py: `_sync` runs `plan_fit.fabrication_pattern(doc["pairs"])` on every doc
  BEFORE the is_done/build branch. On a hit: `_pattern_entry` upserts the candidate into the
  site's item (plan/title/url/pairs/evidence/gate_score; why = "line check: <reason>; the gate's
  X m measures internal consistency of the anchors, not their truth"), the doc file is deleted,
  the line prints "sent to the review queue (line check: ...)" and never counts it synced; after
  the loop `plan_fit.prune(root, sid)` drops any existing overlay. `_sync` returns (failed, sent).
  `main` re-reads the item after the sync (upserts during sync are invisible to `_fit`'s snapshot)
  so `_review`/`_summary`/`resolved` see the new candidates. Module docstring documents the check.
- pipeline/plan_fit.py: `prune(root=None, site=None)` - the `site` param restricts the sweep to
  one site's dep file (the CLI keeps the global sweep via site=None). Added because the line's
  first run used the global prune and it dropped a stale orphan dep entry of alligator-effigy-mound
  (see DECISIONS) - the line must not write other sites' files.
- The line was run on the real checkout: `.venv/bin/python tools/site_done.py stonehenge-q39671`
  (twice; second run idempotent). All 7 stonehenge auto docs hit the check and were deleted;
  their 14 plan webps + dep entries pruned; drawings 7 -> 0; item 6 -> 13 candidates; review.json
  republished (339 open of 340). The 6 original item candidates are byte-identical; the 7 new ones
  are appended after them (lead unchanged, item file name unchanged).

**Verified state on disk (this commit):**
- stonehenge-q39671: 0 docs in data/db/platefits (the 7 deleted docs survive in git history -
  `git show <parent of this commit>:data/db/platefits/stonehenge-q39671.<plan>.json`, plans
  c_022604d2be0becdc c_098c4cb138676939 c_20f9f11153a0b7f0 c_6933e3a931a0240a c_83b4d6df7a6d2383
  c_897a5c1632e2fdd6 c_f8386b6404e4ee63); dep = 2 maps (six-inch-1st, os1inch); drawings 0;
  item data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json = 13 candidates
  (6 originals + 7 with "line check:" whys), resolved None; review.json stonehenge entry = 13.
- alligator-effigy-mound-q4732645: its dep file (gitignored, local) lost one stale orphan entry
  during the FIRST run's global prune (a plan overlay referencing a doc that no longer exists in
  the store - pre-existing before this task; the only alligator doc is the batch's c_618a, which
  prune kept). Left as-is: it was dead weight, the file is local and pipeline-rebuilt, and the
  module's own next global prune (any page save/delete) would have dropped it anyway. Do not try
  to restore it or file a task for it.
- argentoratum-q2361353: untouched so far - 8 auto docs, item with 34 candidates, drawings 0,
  dep = 2 maps + 1 aerial. All 8 docs hit the pattern check (verified this session).

**Next step (ONE step, then commit): DOCS.** docs/site_flow.md: correct the now-false Stonehenge
paragraph (it says the line "synced the 7 documents, took the entry from 0 to 7 drawings" and the
png caption says "its circles and stones sit on the real sarsens" - both false: all 7 were the
batch's fabricated pattern class; the site shows 0 drawings and all 13 candidates sit in its review
item until a human fits at least one). Replace docs/site_flow/stonehenge.png (server/serve.py
`--port 0` + tools/shot.mjs, probe `select('stonehenge-q39671')`): the state a visitor sees now -
0 drawings, marker uncoloured, the review item reachable from the page - with the true one-line
caption. Add the entry under "What broke on Stonehenge": the gate passed 7 fabricated pattern
fits by construction (docs/gate.md s.7 blind spot); the line's fabrication check (plan_fit.
fabrication_pattern, wired into tools/site_done.py:_sync) now catches this class before it reaches
the map - pattern docs go to the review item with the reason and are deleted, never synced.
Also update the "Files the line touches" paragraph if it claims platefits is byte-identical (the
line now deletes pattern docs).

**Then (order):**
1. TESTS - rewrite tests/test_site_done.py for the new state: it must SEED the 7 pattern docs
   from a new golden (recover them from git history, e.g. tests/golden/ - add the golden path to
   the task's Touches when you create it) plus the PRE-run item (derive it by dropping the 7
   "line check:" candidates from the current 13-candidate item - deterministic, since the upsert
   only appended) plus the pre-sync site dir (2 maps, drawings 0), run the copied line (the
   socket-dead GUARD harness stays), and assert: exit 0; fit line "13 candidate picture(s): 7
   fitted (doc), 6 in the review item -> no batch run needed"; 7 "sync ... sent to the review
   queue (line check: ...)" lines; NO plan webps; dep byte-identical to the repo's (2 maps);
   sites.json byte-identical (drawings 0); the upserted item byte-identical to the repo's 13-
   candidate item; the 7 golden docs GONE from the tree's platefits; review.json items == repo's;
   no other site's file touched (this is what pins the scoped-prune fix); second run idempotent
   (0 docs -> no batch run; 13 summary lines; only review.json's "at" changes). Keep the existing
   precondition style (fail loudly if the repo drifts). The old test currently passes vacuously
   (0 docs in the repo) - that is not coverage; the rewrite makes it coverage again.
2. ARGENTORATUM - `.venv/bin/python tools/site_done.py argentoratum-q2361353`: all 8 auto docs
   hit the check -> upserted to the item (34 -> 42 candidates, resolved stays None, originals
   untouched), 0 docs left, 0 drawings (0 -> 0), exit 0; the "browser-check each synced drawing"
   box is satisfied vacuously (0 synced) - document that. Screenshot the site page to
   docs/site_flow/argentoratum.png (visitor's state: 0 drawings, item in the review queue) with a
   one-line caption (box 2). Tick the boxes as they are verified.

**Re-read:**
- Re-read: tools/site_done.py:_fit - on a re-run after a pattern doc was deleted, the picture is
  covered via item_cands (not docs), so no batch run re-fits it with a model (verified on the
  second stonehenge run: "0 fitted (doc), 13 in the review item").
- Re-read: fit/review.py:upsert_item - merges by plan; a same-plan candidate is REPLACED whole, so
  a later re-upsert (e.g. a batch run that re-fits the picture and the model now answers badly or
  well) overwrites the "line check:" entry - intended: the newest word wins until a human saves.

**Environment:** .venv/bin/python for anything importing pipeline/ or fit/ (numpy/PIL; the driver's
2026-10-10 venv note is stale, the venv builds). No fixed network ports in tests; nothing writes
outside project + temp dir. Do not run git merge/rebase/reset/stash/branch switches. Agent a works
on 206 in its own checkout (its 206 files: fit/src_mackenzie.py etc. - not yours); 207/207a/b/c
wait on the human. Do not start other tasks; the lead gives the next site when this one is done.


