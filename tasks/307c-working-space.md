Status: open
# 307c: The working space - in place mode the map is the surface
Depends on: 307b
Touches: web/index.html, web/fitkit.js, web/review.js, docs/site_flow.md, docs/site_flow/

## Goal
"It's super cluttered ... there's like no working space" (screenshot: the page picture sits
in a big middle panel between the side panel and a thin strip of map). In place mode the
map is the main surface: the page picture becomes a small, collapsible reference (or is not
needed at all once the drawing is on the map), and the side panel holds only what placing
needs. Parent 307 box 5, with its before/and-after screenshots at 1440x900 in
docs/site_flow/.

## Acceptance criteria
- [ ] In place mode (a plan open, with or without a proposal): the map is the main
      surface - it takes the width the big middle panel (.fitpane, left:398px,
      min(46vw,780px)) used to; the page picture is a small collapsible reference (the
      existing canvas with its zoom/crop tools, shrunk and tucked to a corner, expandable
      back to the old size on demand - the old three-point flow still has to work); the
      side panel shows only what placing needs: the plan's title and book, the live
      scale/rotation readout from 307b, the opacity slider, the interaction help line,
      and Save/Cancel. Everything else in the page (the home view, the site list, the
      review tab, the Finder, the block view, non-place-mode site browsing) is byte-for-
      byte the layout it had before - the pinned footprints (test_review, test_fit_queue,
      the index.html one-liner tests) stay green.
- [ ] The 307b interactions work at the new size: the drag/scale/rotate targets and the
      fly-to padding adapt to the layout (no dead zones where a drag does nothing, the
      site's box still fills the visible map on open, narrow/mobile widths degrade
      sensibly).
- [ ] If the review list needs to show 307a's reason ("same name, other place: ..."), the
      minimal change to web/review.js lands here (it is the only remaining file of the
      parent's Touches that still needs work).
- [ ] Before/and-after screenshots at 1440x900 in docs/site_flow/ (the old three-point
      layout and the new place mode, same site, both from the headless browser) and the
      docs/site_flow.md section describing the new working space, citing them.

## Notes
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).
