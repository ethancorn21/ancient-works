Status: done
Depends on: 814
Touches: web/index.html

# 815: The fit tool's pair markers at subpixel precision (the 1-px jitter the owner sees)

The fit tool's pair markers are born in `addPairMarker` (web/index.html:1136,
`new maplibregl.Marker({ element: el, draggable: true })`) without the
subpixelPositioning option, and MapLibre 5.6.0's default is false: its `_update`
rounds the marker's DOM position to integer pixels on every setLngLat and
moveend update (vendor line:
`this._subpixelPositioning||(e&&"moveend"!==e.type)||(this._pos=this._pos.round())`).
While the camera stands still, every marker therefore jitters in 1-px steps on
each drag, toolbar scale/turn and re-emission, and any pixel-level check of the
corner handles quantises: 814 measured exactly this (true q1 edge 82.9807 px read
82.0, true q2 edge 87.1384 read 87.0057, so the 1.05 ratio check reads 1.06105 -
the value the 230/239/241 flake recorded; the true ratio 1.0501 passes). 814's
probe works around it from the test side (`setSubpixelPositioning(true)` on the
live markers, a public vendored API); this is the page-side fix that removes the
owner-visible jitter and makes the workaround unneeded.

## Goal

Pass `subpixelPositioning: true` in `addPairMarker`'s Marker options, so the
re-emitted corner handles (and the owner's own pins) track their true projected
point instead of snapping to whole pixels. Audit the page's other
`new maplibregl.Marker` sites (line 513, the site squares; line 1245, the plan
preview's corner markers) and extend the option only where integer-pixel
rounding is user-visible; the site squares anchor at designed integer positions
and the preview corners sit in a fixed pane, so they are expected to stay as
they are - record the audit and the decision in this task's hand-over.

## Acceptance criteria

- [x] `addPairMarker` creates its markers with `subpixelPositioning: true`, and
      the owner check (`pytest tests/test_owner_check.py`) still passes end to
      end unchanged - its probe's setSubpixelPositioning call is idempotent
      with this page-side fix.
- [x] The audit decision for the other Marker sites is recorded in this task's
      hand-over.
- [x] The full suite shows no new red against main
      (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).

## Hand-over

(2026-10-15, iteration 212, agent c) **DONE - all three boxes verified this session; ready for the driver to re-check and merge.**

**The fix (one hunk, web/index.html `addPairMarker`, the only pair-marker constructor on the page):**
`new maplibregl.Marker({ element: el, draggable: true, subpixelPositioning: true })` + a 3-line why-comment.
Committed as `815: addPairMarker passes subpixelPositioning: true` (branch agent/c). `git diff main -- web/`
shows exactly this hunk; `git diff main -- tests/` is empty (the probe is byte-identical, as box 1 requires).

**Box 1 evidence (runs, not new tests):** four pair runs, two before the edit and two after (one invocation
each, the 194/814 recipe): before 72.83 s / 73.97 s, after 69.63 s / 69.38 s, all `2 passed`; every captured
probe log (0.1 s watcher, flattened keys - the PITFALLS recipe) shows 16 `[ok]` / 0 `[warn]` / `RESULT PASS`
with the ratio check `toolbar scale and turn change the drawing on screen` `[ok]`. Pixel compare: before
run-vs-run 9/10 views byte-identical (B_5 0.0010%); after run-vs-run 9/10 (B_5 0.0004%); **before-vs-after
b1/p1 all ten byte-identical, b2/p2 nine byte-identical + B_5 0.0006%** - the page change altered no captured
pixel, exactly as predicted, because the probe's `subpixel()` already forces the same state (its
`if (!m._subpixelPositioning)` guard skips the setter now; the forced `setLngLat` no longer rounds) and both
regimes converge on the same fractional `_pos`. Direct scratch proof (not committed, /tmp rig):
- **T2a** real page, fresh profile, no probe helper: queue card 'Place the drawing' (Fort Ancient) seeds all
  5 markers through `addPairMarker` with `_subpixelPositioning === true`, corner-handle rect fractional
  (604.608, 326.554); survives a `setLngLat` round-trip; one `#fkbar [data-a="s+"]` click (`_fkApply`
  recreates every marker through `addPairMarker`) leaves all 5 `true` and fractional again (601.613, 322.654).
- **T2b** minimal page on the same vendored 5.6.0: a no-option marker (the pre-fix page behavior) sits at
  integer (642, 382) on add AND after `setLngLat` (re-rounded every update); the option marker holds
  fractional (641.511, 381.648) through both - the 0.489/0.352 px rounding is the very quantisation 814
  measured into the 1.06105 ratio artifact.

**Box 2 - the audit of the other `new maplibregl.Marker` sites (grep of web/ excl. vendor: only three exist):**
| site (function) | line | what it is | decision |
|---|---|---|---|
| `addMarkers` | 513 | the site square/pin (`anchor:'bottom', offset:[0,0]`), one per site, at the real coordinates | **STAY integer** - pure display pins: the fit math uses lngLat pairs, clustering uses `map.project` not the marker's `_pos`, and no test reads their pixels. Subpixel'ing them would only shift the site-map pixels the site golden tests compare - risk without benefit. (The 1-px cosmetic jitter under a hard pan, if anyone ever cares, is a later task's call - the task text expects these to stay.) |
| `addScanAreas` | 1255 (the task file's 1245 is stale: the 245 fix added 10 lines above; the function starts at 1243) | the Finder scan-area label tag (a `.marker.scan` button: square + label), `anchor:'left', offset:[-6,0]`, at the designed corner `[x0, y1]` of the scan rectangle. Note: the task file called these "the plan preview's corner markers" - they are the scan-area labels, not plan-preview markers; nothing on the page labels a plan-preview corner | **STAY integer** - the rectangle itself is drawn full-precision as a geojson line; the tag is anchored at a designed corner and no check reads its pixel position. |

`fitkit.js` constructs no markers of its own (it calls `addPairMarker` for every pair marker - initial clicks,
`_fkApply` full rebuilds, `_fkReemitLive` slides the existing ones via `setLngLat`). The other
`subpixelPositioning` hits inside web/vendor/maplibre-gl-5.6.0.js belong to the Popup class - untouched.

**Box 3:** full suite on the fixed tree, the driver's exact command: **195 passed, 1 skipped, 0 failed in
631 s** - identical to the current main baseline (236c it.210: 195P/1S/0F). No new red.

**PNG discipline (R5):** the owner-check pair re-encodes all ten docs/site_flow/307d_*.png on every run; after
each of the five runs here they were restored to main's bytes, and the final commit carries that restore (my
branch's HEAD had inherited three re-encoded PNGs from a previous session's run, committed by the driver -
verified re-encode-level against main's goldens: 0.0022-0.0094%, no content shift). Net `git diff main --
docs/site_flow/` after this task: empty. 813's refresh flag retires this discipline once it lands.

**Housekeeping found this session:** two orphaned infinite poller loops (PIDs 3250557/3260862, `while true`
`find … owner_probe.log` watchers from a previous session whose pytests finished long ago) were still running
in this lane's TMPDIR; killed. Lesson: the poller-kill line of an old runpair script does not survive session
teardown - the subshell outlives it (see DECISIONS).

**Prep-note assumption verdicts (tasks/prep/815.md):** A1 (the 814/816 probe recipe on main, verbatim),
A2 (the 245 page fix on main; 1245→1255 shift), A3 (pair green), A5 (816 no-op-closed, e7c3a75e),
A7 (818 on main), A8 (245's `Depends: 815` and its hunk in `saveFit`, disjoint from mine), A9 (812/813/810
still open on agent a's lane; tests/ diff vs main 0/0) - all confirmed as written. A4: 814 is DONE on main
(999e5bf3) and 816 closed - the gate this task waited on is satisfied, so the build proceeded. A6: 817/818
are on main (the roman reds are dead - the suite is green). No assumption forced a plan change beyond what
the prep itself flagged (stale line numbers; use function names).

**State for the next agent:** nothing left on this task. The driver merges; 245's claim (Depends: 815) is
unblocked - its hunk sits in `saveFit`, ~60 lines below mine, and my diff cannot collide with it. If a future
task revisits marker positioning, the vendor's `_update` rounds only when `subpixelPositioning` is false and
the event is absent or `moveend` ('move'-type updates keep subpixel); the Popup class has its own option.
