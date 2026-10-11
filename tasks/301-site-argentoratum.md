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
(iteration 72, agent c - tests/test_site_done.py rewritten golden-seeded and passing: the test recovers
the 7 fabricated Stonehenge docs (tests/golden/stonehenge_linecheck_docs/, verbatim from git b84d147^),
re-seeds the pre-line state (7 docs + the item's 6 batch candidates) in the temp tree, runs the copied
line, and pins the whole incident: byte-identical 13-candidate item upsert, 0 drawings, pattern docs
deleted, no other site's file touched, second run idempotent. Suite 60 green. Next: Argentoratum
through the line.)

**What was done and committed (iteration 72):**
- tests/golden/stonehenge_linecheck_docs/: the 7 deleted stonehenge docs, verbatim from
  `git show b84d147^:data/db/platefits/stonehenge-q39671.<plan>.json` (plans c_022604d2be0becdc
  c_098c4cb138676939 c_20f9f11153a0b7f0 c_6933e3a931a0240a c_83b4d6df7a6d2383 c_897a5c1632e2fdd6
  c_f8386b6404e4ee63; scores 23.2/7.4/44.1/26.8/16.7/38.0/0.0).
- tests/test_site_done.py rewritten (same GUARD socket-dead harness, copied code + copied data):
  preconditions fail loudly if the pinned repo state drifts (0 stonehenge docs; item = 7
  "line check:" + 6 batch candidates; fabrication_pattern still fires on each golden doc AND
  the recorded entry == SITE_DONE._pattern_entry(doc, pattern, repo) - so drift in the check,
  a golden doc, or a files.jsonl evidence row fails before seeding; plans.json's 13 rows ==
  7+6; the published page matches the item). The tree seeds the 7 docs + the item rewound to
  its 6 batch candidates (the upsert only appended, so removing them restores the batch's file)
  and copies data/commons/files.jsonl (the OLD tree omitted it: _pattern_entry records the 200
  evidence field from that row store, and without it the upserted item cannot be byte-identical).
  First run: asserts the ENTIRE output line by line (fit "13 ... 7 fitted (doc), 6 in the review
  item -> no batch run needed"; 7 exact sync lines with the pattern reason; entry 0 -> 0; review
  line; 13 summary lines; done), no plan webps, site dir/sites.json byte-identical to the repo
  (0 drawings), the upserted item BYTE-IDENTICAL to the repo's 13-candidate item (the run
  reproduces the live run), the 7 docs gone, every other item/doc byte-identical, review page
  items == the repo's. Second run: 0 docs -> no batch run (13 in the item), 13 summary lines
  (the 7 with "gate X m - line check: ..."), only review.json's "at" changed. No image seeding:
  pattern docs never reach load_picture (a failed check would attempt a download and die on the
  socket guard). Module level: loads tools/site_done.py via importlib (unique name
  "site_done_under_test") - same sys.path pattern as test_batch_us; fit/ and pipeline/ have no
  module-name collisions, so this cannot perturb the later test_src_* imports.
- Suite: 60 passed (64.7 s), count unchanged.

**State on disk (unchanged this session, re-verified in the test preconditions):**
- stonehenge-q39671: 0 docs in data/db/platefits; item
  data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json = 13 candidates
  (6 batch first, then the 7 line-check in sorted plan order), resolved None; web entry 0
  drawings; depictions = 2 maps (six-inch-1st, os1inch); review.json: 339 open of 340.
- argentoratum-q2361353: 8 auto docs (c_0a017388dd93d0a0 c_13994601c91902bc c_1cb3168933122090
  c_5bfb0472f266c056 c_6ba6bb7b49a78014 c_751f9350136c699c c_7e281c4136c9f7f5
  c_cd8109001e6616f1 - all 8 fire fabrication_pattern at calibration), item
  data/review/argentoratum-q2361353.c_6acfd94dec8c011b.json = 34 candidates (0 line check),
  resolved None; entry 0 drawings; dep = 2 maps + 1 aerial.

**Next step (ONE step, then commit): ARGENTORATUM through the line**
`.venv/bin/python tools/site_done.py argentoratum-q2361353` (LIVE checkout, no model flag:
all 42 candidates are covered - 8 docs + 34 item - so no batch run, no network; the 8 pattern
docs must all hit the pre-sync check -> each upserted into the item with "line check: ..." +
gate score, each doc deleted, scoped prune; expect: 8 "sent to the review queue (line check: ...)"
sync lines; entry drawings 0 -> 0; item 34 -> 42 (the 34 originals byte-identical and in order,
the 8 new ones appended in sorted plan order); review.json republished (still 339 open of 340 -
the argentoratum item was already open, only its candidate list grows); exit 0). Then box 2's
browser part: 0 drawings synced, so "each synced drawing opened over the ground" is satisfied
vacuously - say so in the task file when ticking. Screenshot the site page (same recipe as
stonehenge: server/serve.py --port 0 +
`NODE_PATH=/home/agent/tools/shot/node_modules node tools/shot.mjs <url> docs/site_flow/argentoratum.png
1000 1200 800 "<probe>"`, probe: poll S.ready && S.sites.length, select('argentoratum-q2361353'),
await loadDeps(S.byId[...]), POSTWAIT=8000 for the 4.5 s flyTo; ArcGIS ERR_ABORTED in flight is
normal) and one line on what it shows (aerial ground, its maps/aerials group in the panel,
uncoloured marker, the 42 candidates waiting in its review item). Then docs/site_flow.md gets the
Argentoratum paragraph (like Stonehenge's) if nothing else broke: box 3's "one line under What
broke" already exists (the fabrication-check entry) and box 3 otherwise rests on the test step +
the full suite (if something DID break in the line on this site: fix it in the line, with a test,
not by hand - box 3). Tick boxes only as verified; box 1 also needs the sites.json entry count
(stays 0).

**Re-read (carried over, still fresh-eyes due):**
- Re-read: fit/review.py:upsert_item - merges by plan; a same-plan candidate is REPLACED whole, so
  a later re-upsert (e.g. a batch run that re-fits the picture) overwrites the "line check:" entry -
  intended: the newest word wins until a human saves.

**Environment:** .venv/bin/python for anything importing pipeline/ or fit/ (the venv builds fine;
the driver's 2026-10-10 note is stale). Screenshot recipe: server/serve.py --port 0 (ephemeral, no
fixed ports) + node tools/shot.mjs with NODE_PATH=/home/agent/tools/shot/node_modules and
POSTWAIT>=8000 (map flyTo is 4.5 s). Nothing writes outside project + temp dir. Do not run git
merge/rebase/reset/stash/branch switches. Agent a works on 206 in its own checkout (its files:
fit/src_mackenzie.py etc. - not yours). Do not start other tasks (207 etc.); the lead gives the
next site when this one is done.
