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
(iteration 69, agent c - fabrication_pattern IMPLEMENTED in pipeline/plan_fit.py and validated;
suite green 60 passed after the change. The code change was UNCOMMITTED at session end (harness
saves it - re-verify it is there first). Order: wire into site_done._sync -> run line on
Stonehenge -> docs -> test -> Argentoratum.)

**What is done and committed (iteration 69):** pipeline/plan_fit.py now has
`fabrication_pattern(pairs) -> None | reason` - pure numpy, no download; docstring carries the
calibration summary. Clauses: (a) 2D lattice (>=4 anchors, >=3 distinct u AND v, per-axis
distinct-value gaps max/med <= 1.3 AND min/med >= 0.67); (b) 1D ladder (>=3 anchors sharing one
coord, spread <= 2 px, other-axis gaps max/med <= 1.5 AND min/med >= 0.9); (c) grid-round (>=4
anchors, >=90% of PER-AXIS distinct coords within 0.5 of a multiple of 10 px). VALIDATED against
the real function: fires 15/15 stonehenge + argentoratum auto docs (c_098c fires all three;
reason strings name each clause) and 110/110 repo batch docs, 0/20 hand fits. Suite 60 passed
after the change. The code edit was uncommitted at session end (harness saved it): FIRST verify
pipeline/plan_fit.py still contains fabrication_pattern (grep it; if the harness dropped it,
re-add per the DECISIONS 2026-10-11 entry).

**Decision made (was open):** standalone-round, no frame-identity -> the function takes pairs
only (no crop/size/box). (b) kept: pontefract c_3213 (22% round) is a ladder, so the union
catches every batch doc. See DECISIONS 2026-10-11 301 third entry.

**State on disk (verified this session):**
- stonehenge-q39671: sites.json drawings 7; depictions = 7 plan webps + 2 maps (six-inch-1st,
  os1inch); item data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json has 6
candidates (5 with gate scores, 2 "no model answer"); the 7 auto docs are NOT in the item.
- argentoratum-q2361353: sites.json drawings 0; depictions = 3 maps only (cassini, etatmajor,
  fr_ortho1950); item data/review/argentoratum-q2361353.c_6acfd94dec8c011b.json has 34
candidates; the 8 auto docs are NOT in the item.
- web/data/review.json items: {site, name, lead, candidates, no_picture_found}. Candidate entry
  shape (batch's write_item): plan, title, url, pairs, gate_score, why, note, evidence, ground,
  coarse, rot_deg, scale_m_px, scale_source. review.upsert_item merges by plan (same-plan
  replaced, new appended, never clears resolved) - safe to add the 8/7 pattern candidates.
- review.export derives resolution from platefits docs: deleting a doc keeps its item open
  (correct: the human's drag resolves it).

**Next step (ONE step, then commit):** wire the check into tools/site_done.py:_sync. For each
doc, BEFORE the is_done/build branch: `why = plan_fit.fabrication_pattern(doc["pairs"])`; on a
hit: (1) upsert_item the candidate into the site's item (preserve existing entries: merge by
plan; candidate carries plan/title/url/pairs/gate_score/why where why = "line check: " +
reason + "; the gate's X m measures internal consistency of the anchors, not their truth");
(2) DELETE the doc file from data/db/platefits/ so plan_fit.prune() (which keys on the
doc-file set) drops the existing overlay and so no future plan_fit.main/serve.py run rebuilds
it - the item is the record; (3) print a summary line "sent to the review queue (line check: ...)",
never count it as synced. Do NOT build, do NOT touch non-hit docs. Then re-run the line on
stonehenge: `.venv/bin/python tools/site_done.py stonehenge-q39671` (no --model; all 13
candidates covered -> no batch run) - expected: exit 0, 7 plan webps pruned, depictions = 2
maps, drawings 7 -> 0, item 6 -> 13 candidates (7 with the pattern reason), web/data/review.json
republished, second run idempotent.

**Then (order):** docs - correct docs/site_flow.md's Stonehenge paragraph ("its circles and
stones sit on the real sarsens" is false), replace docs/site_flow/stonehenge.png (server/serve.py
+ tools/shot.mjs, true one-line caption), add the entry under "What broke". Test - extend
tests/test_site_done.py's hermetic harness (socket-dead child, tmp copy): the check fires on all
7 stonehenge docs and none of the 20 hand docs; the line run: exit 0, 0 plan webp, depictions =
the 2 maps, sites.json drawings 0, item 13 candidates, review.json republished, second run
idempotent; REWRITE the existing goldens that pin the OLD 7-synced state. Then ARGENTORATUM:
`.venv/bin/python tools/site_done.py argentoratum-q2361353` - all 8 auto docs fire the check
(all 100% round, verified) -> all 8 upserted to the item (34 -> 42 candidates, resolved stays
None), 0 drawings, exit 0; the "browser-check each synced drawing" box is satisfied vacuously
(0 synced); screenshot the site page to docs/site_flow/argentoratum.png (the state a visitor
sees: 0 drawings, item in the review queue) with a one-line caption; add anything that broke in
the line to "What broke". The 20 hand fits and their golden file stay untouched.

**Re-read:**
- Re-read: tools/site_done.py:_fit + _sync + _summary - when a doc is deleted after being in
  pre_docs, confirm the candidate is covered via item_cands so no batch run is triggered, and
  that _summary's per-picture lines come from the item (pid in item_cands) not the docs dict.
- Re-read: fit/review.py:upsert_item + export - merge-by-plan keeps the 6/34 existing candidates;
  export(root, site_id) writes web/data/review.json over the WHOLE queue but records resolution
  only into this site's item file.
- Re-read: plan_fit.prune - keys on the set of existing doc file names, so the overlay removal
  depends on the doc file being deleted first.

**Environment:** .venv/bin/python for anything importing pipeline/ or fit/ (system python3 has no
numpy; the venv builds fine - the driver's 2026-10-10 note is stale). No fixed network ports in
tests; do not write outside project + temp dir. Do not run git merge/rebase/reset/stash/branch
switches. Agent a works on 206 in its own checkout; 207/207a/b/c wait on the human - neither is
yours. Do not start other tasks.

