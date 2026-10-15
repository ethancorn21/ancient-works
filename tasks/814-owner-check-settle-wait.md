Status: open
Depends on: 307d
Touches: tests/test_owner_check.py

# 814: The 307d owner check - settle the map view before every capture (the mid-transition flake fix)

Part 1 of 812's split (2026-10-15, iteration 191, driver instruction: agent a had nothing to
build for 76 minutes, and every open task in the chain waited on 812 alone): the flake fix
out of 812, the settle wait. Depends only on done 307d, so it is STARTABLE IMMEDIATELY - the
first claimable unit of the 242 family again. 812 (narrowed to the in-run double-shot
stability assert that proves this fix; Depends: 814; same file) runs after this; 813 (the
pinned-snapshot regime; same file) runs after 812; 810 keeps the final verification and
waits on 812 + 813; 811 then 242 wait on 810. Chain: 814 -> 812 -> 813 -> 810 -> 811 -> 242
-> {230, 241} -> 236c. The waiters 230 and 241 carry this number on their Depends lines
directly - they are held on the mid-transition flake this part fixes (230: the owner_check
A/B pair red a 3rd consecutive time at it.214-216, its done-claim gate; 241: red at
it.187/188). Background: 242's goal and the 2026-10-14 307bc DECISIONS entry (now in the
archive); the drift is measured, not guessed:

- On the IDENTICAL tree, runs an hour apart differ by 28.6-33.6% of pixels (threshold >32) on
  the four saved/reload views (A_4/A_5/B_4/B_5) - the captures land mid-transition: the
  placement chains the 4.5 s site flyTo (web/index.html:874) with a 900 ms fitBounds
  (web/fitkit.js:573) and the probe's fixed sleeps never wait for `moveend`; visually the
  overlay rectangle shifts slightly relative to the ground imagery. The card/placed/gestured
  views stay 0-1.25% (encoding noise).
- The same mid-transition signature flakes the owner_check A/B pair itself (the gesture check
  `toolbar scale and turn change the drawing on screen`, e2/e1 = 1.06105 ~= 1.05 x 82.863):
  230 it.214-216, 239 it.226-228, 241 it.187-188.

## Goal

In tests/test_owner_check.py and its embedded PROBE. The pick (derived, never pinned) and
every existing check stay exactly as they are; this is a capture-timing fix, not a flow
change. Do not touch tests/test_fit_queue.py (the 307/235 family) or the page (the served
private tree the test already builds is the place to intervene, not web/index.html or
web/fitkit.js on disk). The pair always runs as one invocation, A then B (PITFALLS: the B
test cannot run in isolation).

1. **Stable captures.** Wherever the map can still be moving at capture time, wait for the
   map view to settle first: the quad reads q0 (after the place chain), q1 (after the drag),
   q2 (after the toolbar scale/turn) - where the pair flake shows up - and the `2-placed`
   shot and the `4-saved` / `5-reload` shots, which follow the 4.5 s flyTo + 900 ms
   fitBounds chain (the reload re-fires the flyTo via the deep link). The `1-card` and
   `3-gestured` shots measured stable (0-1.25%) but a uniform settle before all five shots
   is fine if it is cheap. Mechanism options: the page exposes the maplibre `map` global to
   `page.evaluate` (the probe already reads `map.getCanvas()` / `map.project`), so e.g. wait
   on `!map.isMoving()` / a `moveend` event with a timeout after each interaction chain, or
   run the page with its camera transitions disabled in the test view (zero durations in the
   served tree). Keep any wait bounded (a timeout must not hang the test).

## Acceptance criteria

- [ ] Two consecutive unflagged runs of `pytest tests/test_owner_check.py` on the same tree
      produce byte-identical (or <0.5% differing pixels at threshold 32) A_4/A_5/B_4/B_5
      views in the temp tree (all ten stable, not just the four - the other six stay at
      their historical 0-1.25% encoding noise); both tests still pass end to end and the
      write-once / shared-store / golden-hash checks stay green.
- [ ] The pick is still derived and no existing check changed (same flow, same asserts); the
      settle wait is additive.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).

## Hand-over

(2026-10-15, iteration 192, agent c) **Session hit the context limit mid-fix; read this first.**

**Where I am.** The settle wait (the task's headline) is BUILT in `tests/test_owner_check.py`'s
embedded PROBE: a bounded `settle()` helper (`page.evaluate(() => !map.isMoving())` polled at 150 ms,
20 s budget, `[warn]` log on timeout) called before all five shots and before the q0/q1/q2 quad reads
(inserted after the existing fixed sleeps; nothing else touched; `node --check` on the extracted probe
passes). BUT measuring it showed the settle is **necessary but not sufficient**: the q1/q2 pair flake
(the check that has red 230/239/241) is NOT a moving camera. Both tests still FAIL in this session,
4/4 runs, at `toolbar scale and turn change the drawing on screen :: {"e1":82,"e2":87.00574693662483}`
(ratio 1.06105 = the exact recorded flake value 1.05×82.863/82).

**Root cause (proven by instrumentation, details in the DECISIONS entry):** the camera was fully
stationary at q1 and q2 (zoom 15.03110021085413 identical to 10 digits, zero move/zoom/resize events
between the reads; camera settled ~4.3 s, q1 read 6.9 s, q2 read 7.6 s). The flake is **integer-pixel
rounding of the marker DOM positions**: MapLibre 5.6.0 defaults `subpixelPositioning` to false
(vendor: `this._subpixelPositioning=e&&e.subpixelPositioning||!1`) and `Marker._update` rounds
`_pos` on direct-`setLngLat` and `moveend` updates (`this._subpixelPositioning||(e&&"moveend"!==e.type)||(this._pos=this._pos.round())`).
The page creates the 5 pair markers via `addPairMarker` (web/index.html:1134, `new
maplibregl.Marker({ element: el, draggable: true })` - no subpixel option). Measured: true q1 top edge
82.9807 px -> rounded 82.0 (endpoints +0.49/−0.49); true q2 edge 87.1384 -> 87.0057 (dx 87.0, dy 1.0).
True ratio 1.0501 (would pass); rounded ratio 1.06105 (fails the 1% tolerance). Rounding error up to
~1 px per edge exceeds 1% of an 83-px edge.

**Current file state (IMPORTANT):** `tests/test_owner_check.py` in the working tree = the good settle
change **plus TEMP INSTRUMENTATION that must be REVERTED before committing**: a `// TEMP
INSTRUMENTATION` block (~line 313: `window.__cam` listener registration, `cam()` and `dumpHandles()`
helpers), `await cam('read:' + 'q1');` / `await dumpHandles('q1')` + the q2 equivalents, and a
`console.log('[camlog] ' + JSON.stringify(camLog));` line before the `[eval]` dump. A clean copy of
the settle-only version is at **/tmp/test_owner_check.py.bak** (verify it, then restore it - do NOT
restore blindly if you changed anything else). The settle change and the instrumentation both live
only inside the PROBE raw string; the Python side of the test is untouched and valid. ALSO: this
session's test runs dirtied `docs/site_flow/307d_B_4-saved.png` and `307d_B_5-reload.png` in the
working tree, and the context-limit harness AUTO-SAVES uncommitted changes, so my branch will
probably carry both the instrumented test file and the two dirty PNGs - **your FIRST act** (before
anything else, in one commit): `git diff main -- docs/site_flow/307d_*.png` and
`git checkout main --` every differing one (all ten may differ, check them all), plus restore
`tests/test_owner_check.py` to the .bak. That commit makes the branch merge-clean again (the
6af207b R5 rule: branch PNGs must equal main's bytes).

**Next steps (in order):**
1. Restore tests/test_owner_check.py to the settle-only version (/tmp/test_owner_check.py.bak, or
   manually delete the TEMP block/cam/dumpHandles/[camlog] lines). `node --check` the extracted probe.
2. Add the q1/q2 fix. RECOMMENDED (probe-only, additive, served page stays byte-identical to the
   checkout): right after page boot in the probe (before the place flow),
   `page.evaluate(() => { P.marks.forEach(m => m.setSubpixelPositioning(true)); });` -
   `setSubpixelPositioning` is the VENDORED PUBLIC Marker API (maplibre-gl-5.6.0.js, `setSubpixelPositioning(e){this._subpixelPositioning=e}`);
   `P` (the fit state, top-level const in web/index.html) is reachable from `page.evaluate` exactly
   like `map` is. Re-call it after `_fkApply` rebuilds markers if a run shows the flake persist
   (marker objects are recreated by `_fkApply` - check whether the 4 corner markers are ever
   re-created after boot; `_fkReemitLive` mutates in place and `_fkActivate`'s seed uses
   `addPairMarker` once at placement, so one call after placement may be the minimal safe point).
   After any `setSubpixelPositioning(true)` on already-positioned markers, force one re-position
   with `m._update()` (private, but the probe already pokes `P.marks` internals) or simply read the
   quads once more after a 2nd `setLngLat(m.getLngLat())`. Fallback if probe-only proves flaky: patch
   the served PRIVATE tree's web/index.html in the `owner_served` fixture (after `copy_web`, string-patch
   `addPairMarker`'s Marker options to add `subpixelPositioning: true`) - the task explicitly names the
   served tree "the place to intervene"; never web/index.html on disk. AVOID: changing what `quad()`
   reads (DOM rects) to `map.project(lngLat)` - that changes an existing check's measurement, against
   the task's "no existing check changed" rule.
3. Re-run the pair (`.venv/bin/python -m pytest tests/test_owner_check.py -q -p no:cacheprovider -o
   tmp_path_retention_policy=all`); the retention flag keeps the `ownerA*/ownerB*` outdirs (with all
   five PNGs each) in `$TMPDIR/pytest-of-agent/pytest-*` so I can compare. Repeat a 2nd run on the
   same tree; compare all ten views run1 vs run2 with a small throwaway PIL script (count pixels
   differing by >32 on any channel, same size; pass = <0.5%, byte-identical expected). Acceptance box
   1 wants A_4/A_5/B_4/B_5 stable and the other six at their historical 0-1.25%. The settle should
   already have made the four saved/reload views stable - VERIFY it did (307bc measured 28.6-33.6%
   there pre-fix); if they still drift, that is camera mid-transition the settle missed - re-check
   with the `[warn] settle:` line (it appears in owner_probe.log if a budget was exhausted).
4. File a new top-level task (lowest free number in 800-1099; 809/810/811/812/813/814 exist - check
   the tasks/ dir; needs `Depends on:` + one-module `Touches:`): the PAGE defect this session proved -
   fit-tool markers use MapLibre's default integer-pixel positioning (`subpixelPositioning` false),
   so the owner's drag/steps jitter in 1-px increments and any pixel-level check of corner handles is
   quantised; fix in web/index.html's `addPairMarker` (and any other Marker creation in the fit tool)
   by adding `subpixelPositioning: true`. web/index.html is the 307/fit-tool family's file (agent a's
   lane) - file it, don't fix it here. It is also the permanent home for the owner-visible jitter.
5. (The PNG restore is now the FIRST act above - the harness auto-saved the dirty bytes.) Then the
two-run verification of step 3, then file the page-defect task of step 4, then full suite
`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (expect only the known pre-existing reds
on main: agent a's in-flight fit_queue/merge family; record whatever reds appear and cross-check
against DECISIONS-archive baselines - my change must add none). Before committing anything after
any further owner_check run, re-restore the ten PNGs to main's bytes again.

**Test state at context limit:** pair red 4/4 in this session, all at the q2 ratio check, with the
TEMP instrumentation still in the file (so the next agent's first act is the revert, step 1). The
settle mechanism itself is verified to be correct and harmless (no check regressions: every other
check passed in every run, including the write-once/shared-store/golden-hash ones, and the 4-saved
and 5-reload shots now land after the camera settles per the camlog: moveend 4307, q1 6943, q2 7649,
idle events only after).

**Re-read:**
- tests/test_owner_check.py:PROBE (the settle helper + its 8 call sites) - verify the revert kept
  exactly those and the instrumentation is gone
- web/vendor/maplibre-gl-5.6.0.js Marker._update (search `_subpixelPositioning||`) and
  `setSubpixelPositioning` - the two lines the fix hinges on
- web/index.html:1134 `addPairMarker` - where the page's markers are born
- DECISIONS.md entry for this iteration (the full measurement: camlog timeline, the true-vs-rounded
  edge arithmetic 82.9807->82.0 / 87.1384->87.0057)

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-14, iteration 137, agent c - the driver returned the parent after 207a (done),
- `tasks/230-roman-merge-rerun.md` (in-progress) - hand-over: (2026-10-14, iteration 216, agent a - the 5 acceptance boxes were ticked in it.215 and
- `tasks/236-us-cities.md` (split)
- `tasks/241-us-birdseye-batch5.md` (in-progress) - hand-over: (2026-10-15, iteration 191, agent c) **191 note:** the 242 family was re-split - the fix
- `tasks/242-owner-check-stable-shots.md` (open) - hand-over: (2026-10-15, iteration 189, agent c) **SPLIT per the driver's instruction** (agent a's 230 and my
- `tasks/810-owner-check-settle-captures.md` (open) - hand-over: (2026-10-15, iteration 190, agent c; re-split again at iteration 191: the flake fix moved out
- `tasks/812-owner-check-settle-shots.md` (open) - hand-over: (2026-10-15, iteration 191, agent c) Narrowed by this split; nothing built yet on either
- `tasks/814-owner-check-settle-wait.md` (open) - hand-over: (2026-10-15, iteration 191, agent c) Created by the driver's split of 812; nothing built yet.

## Next open tasks
- `tasks/236c-us-cities-merge.md`
- `tasks/809-horsley-check.md`
- `tasks/811-owner-check-pin-snapshot.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

(no entries yet)

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)
- Re-verified the 160 hand-over's numbers with fresh measurements BEFORE deleting (AGENTS.md: check facts by running code). Confirmed: 8 pairs = 4 distinct points on a 100-px grid ladder (three on u=100; the 200-px and 100-px lat steps span 0.0053896/0.0017967 deg = 1.5:1 per pixel, no similarity can hit; the page's simFit (exact port) gives resid 10.9-39 m, 2.634 m/px, +1.06 deg - identical to the committed shot's [eval] line). CORRECTIONS to the 160 hand-over: the real hillfort is ~20 m NW of the site point (not '+22 E / -55 N'), its hachured ring is ~80-90 m across (not ~130 m), so the drawn ring (277-342 m at 2.634 m/px, centred at raw (240-248,115) -> (-3.5187, 51.0370) = E -218..-239, N +531) is ~3.5x too big and 554-582 m N-NW (N23-25W) of the real one - on a small hachured wood hill. The 160 '~2x / 535-576 m' survives as a range (540-576 -> 554-582), the direction and the verdict are unchanged. Extra independent check: the plate's own 'SCALE OF FEET 0-300' bar measures ~1.45 m/px vs the fit's 2.634 (1.8x). Distances must be geographic (dx=dlon*111194.9266*cos(lat0), dy=dlat*110900), NOT raw Mercator units (my first pass computed 916 m for the 576 m distance that way).
- Executed the 303 way exactly as 306c did (fit/review.py API, no hand-edited JSON): upsert_item(root,'bury-castle-q5001077',[entry]) with entry = {plan, title, url, pairs (the doc's 8), coarse:false, evidence (from the data/commons/files.jsonl row: rec evidence/1, kind category, checked 2026-10-10, site_cat/file_cat 'Bury Castle, Somerset'), label '1911', cite, ref, size, place_reason '306d audit 2026-10-12: ... Document deleted.'} appended to the existing item (lead n0136_1 kept first, filename unchanged), then deleted data/db/platefits/bury-castle-q5001077.c_de779031cda8a0dc.json, then export(root,'bury-castle-q5001077') (333 open of 346). Only 3 files changed (D doc, M item, M web/data/review.json) - no other site's item touched; the site was already covered for the union check (its item was already open in the page file before the upsert).
- Wrote the 306d block (header + the bury-castle line) into docs/site_flow.md after the 306c block (header is tense-neutral: 17 more lines to come in batches; box 1 ticked - 36 shots re-listed this session).
- TESTS (full suite, main checkout, --ignore=tests/test_gate.py, -p no:cacheprovider, with my changes): 10 failed, 130 passed, 1 skipped (251 s). The 10: test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (FAILED at the seed check, dep:null) + 9 that are agent a's in-flight work already on main (test_merge new_sites_are_complete/new_site_golden_samples = 211's open 222-228 gate; src_artists/limes/mackenzie/numancia/wiltshire_stukeley stage+check tests = the 224 family). Baseline in my task file (123/1, 2026-10-12) is STALE - main has since merged 211/223/224/307 work and the suite grew to 141 tests.
- A/B attempt 1 (worktree at HEAD in /tmp/aw306d_ab): INVALID - web/data/sites/ is mostly gitignored (58 tracked files vs 389 site dirs in the main checkout; the per-site web data + data/raw are local build artifacts), so a fresh worktree lacks stonehenge etc. and fails 3 tests deterministically (site_done_line FileNotFoundError '/tmp/aw306d_ab/web/data/sites/stonehenge-q39671', fit_provenance line_refuses_unmarked_non_auto_doc, fit_queue save_runs) that pass in the main checkout; its placement_gestures 'vacuous ERROR' there is also unprovable (no local depictions). PITFALLS candidate: never A/B this project in a bare worktree/checkout - do it in the main checkout with the changed files temporarily at HEAD. (The worktree is still registered; remove it: git worktree remove --force /tmp/aw306d_ab && git worktree prune.)
... (1.9 KB more: `grep -n -A 200 -F '## 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)' DECISIONS.md`)

### 2026-10-13 DRIVER: test suite failing at loop start (1 tests)
    tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    tests/test_fit_queue.py:1749: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser
    1 failed, 159 passed, 1 skipped in 424.53s (0:07:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-15 814 (agent c, iteration 192) HAND-OVER IN PROGRESS (context limit)
    Task 814 (settle wait for the 307d owner check): the settle() helper is built in the probe (tests/test_owner_check.py) but the session hit its context limit. Key finding: the q1/q2 pair flake is NOT a moving camera (proven settled) - it is MapLibre 5.6.0 default integer-pixel marker rounding (subpixelPositioning=false). Next session: FIRST revert the TEMP instrumentation (clean copy at /tmp/test_owner_check.py.bak) and restore the ten docs/site_flow/307d_*.png to main's bytes (harness auto-saved the instrumented test file + dirty B_4/B_5 PNGs); THEN the probe-side subpixel fix (marker.setSubpixelPositioning(true) on P.marks - public vendored API); THEN the two-run pixel comparison (the 814 acceptance). Full detail: tasks/814-owner-check-settle-wait.md hand-over + DECISIONS.md 2026-10-15 814 entry.
