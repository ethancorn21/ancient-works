Status: open
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

- [ ] `addPairMarker` creates its markers with `subpixelPositioning: true`, and
      the owner check (`pytest tests/test_owner_check.py`) still passes end to
      end unchanged - its probe's setSubpixelPositioning call is idempotent
      with this page-side fix.
- [ ] The audit decision for the other Marker sites is recorded in this task's
      hand-over.
- [ ] The full suite shows no new red against main
      (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).
