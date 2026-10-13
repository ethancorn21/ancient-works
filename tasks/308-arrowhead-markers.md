Status: open
# 308: Site markers as small arrowheads, not squares
Touches: web/index.html, web/*.css, web/vendor/, docs/site_flow.md, docs/site_flow/

## Goal
The owner (2026-10-11): "instead of the squares we're going to move to a new shape ... keep the color gradient and all
that stuff ... a shape that says this is a point of interest ... like an old arrowhead ... a notched arrowhead ... it
would need to be small though, like a contracting stem arrowhead".

## Acceptance criteria
- [ ] Every site marker on the map and in the legend/list is a small contracting-stem (or notched) arrowhead
      silhouette, point down onto the site's location, with the existing colour gradient (older/truer darker) and the
      existing size tiers. Readable at the smallest tier on a phone and a 1440x900 screen, crisp on retina.
- [ ] The point of the arrowhead is the site's coordinate (the marker anchors at its tip, not its centre); clicking
      and the label placement/collision rules work as before.
- [ ] Screenshots before/after (the globe view, a zoomed region with many sites, the legend) in docs/site_flow/.

## Lead note (2026-10-13)
Dependency on 307 removed: 307's only open part is 307d, the owner's own check, which the markers do not need. Marker code only; commit working code each session.
