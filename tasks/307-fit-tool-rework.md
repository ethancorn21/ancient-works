Status: open
# 307: The fit tool, reworked from the owner's first real use - right place, drawing already on the map, room to work
Depends on: 305
Touches: web/index.html, web/fitqueue.js, web/review.js, web/fitkit*.js, tools/fit_queue.py, web/data/fit_queue.json, tests/, docs/site_flow.md, docs/site_flow/

## Goal
The owner opened the Ready-to-fit queue (2026-10-11) and could not fit its first site. His words, in short:
- "it doesn't zoom me into the Devil's Dyke, so I don't know where it is". The real cause is worse: the queue's first
  entry pairs Allcroft 1908 Fig. 217, "The Devil's Dyke Camp, near Brighton" (a Sussex hillfort), with the site
  devil-s-dyke-q3307343, the Devil's Dyke in Cambridgeshire (the map shows Burwell, Reach, Swaffham Prior Fen).
  Same name, different place, 150 km apart. No zoom could have helped.
- "when I go to place it ... it'll move near it but it does not accurately move over".
- "the overlay that's already there doesn't disappear from the map ... you have two overlays. As soon as you go into
  that place mode the already placed overlay needs to go."
- "when I go to place the plan onto the map it already needs to be overlaid onto the map ... I can move it around I
  can scale it around ... instead of click on the point and then click on the map ... three points. It should
  already be on the map ... then pinpoint this exact spot to here."
- "it's super cluttered ... there's like no working space" (screenshot: the page picture sits in a big middle panel
  between the side panel and a thin strip of map).

## Acceptance criteria
- [ ] Right place: every queue entry's candidate is checked to show the same place as its site, not just the same
      name (the book's caption/place words and county against the site's place, region and coordinates; Wikidata
      where it helps). A mismatch leaves the queue and goes to the review queue with the reason "same name, other
      place: <caption place> vs <site place>"; where the right site exists in the catalog, the candidate is moved to
      it instead. Report how many of the queue's entries were wrong. Devil's Dyke Camp near Brighton must not be
      paired with the Cambridgeshire dyke.
- [ ] Place mode opens ON the works: the map flies to the site's own box (the built site's extent), centred, zoomed
      so the works fill the view, before the drawing appears.
- [ ] Place mode hides every overlay already on the site (survey sheets, earlier drawings) while it is open, and
      brings back what was showing when it closes.
- [ ] The drawing starts ON the map: semi-transparent over the ground at the site, sized from its scale bar where it
      has one, otherwise from the site's known size, north-up (or by its north arrow). The owner moves it by dragging,
      scales and rotates it with handles (or modifier+drag / wheel), with an opacity slider. Saving works from this
      direct placement alone. Pinning exact spots (a point on the drawing to a point on the ground) stays available as
      a refinement on top, not as the only way in.
- [ ] Working space: the map is the main surface in place mode. The page picture is a small, collapsible reference
      (or not needed at all once the drawing is on the map); the side panel holds only what placing needs. Before
      and after screenshots at 1440x900 in docs/site_flow/.
- [ ] Saving still writes "by": "hand" and runs the one-site line (305), and the existing hand fits load and save
      unchanged. Checked in a real browser on two queue sites the way the owner uses it (place, move, scale, save,
      see it on the map), then the test fits reverted. Tests cover the queue place-check and the save path.

## Notes
- Do not touch fit/surveyfit.py or task 304 (agent c).
