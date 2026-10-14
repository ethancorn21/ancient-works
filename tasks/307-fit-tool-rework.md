Status: done
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
- [x] Right place (carved to 309 - agent c, 2026-10-12; the rest of 307 is page work only): every queue entry's
      candidate is checked to show the same place as its site, not just the same name (the book's caption/place
      words and county against the site's place, region and coordinates; Wikidata where it helps). A mismatch leaves the queue and goes to the review queue with the reason "same name, other
      place: <caption place> vs <site place>"; where the right site exists in the catalog, the candidate is moved to
      it instead. Report how many of the queue's entries were wrong. Devil's Dyke Camp near Brighton must not be
      paired with the Cambridgeshire dyke. Verified 2026-10-14 (iteration 200): the build's own check
      (tools/fit_queue._place_flags over the committed 180-entry queue) finds 0 residual namesake pairs; n0686_1
      sits on the unbuilt Sussex hillfort's review item with the reason "same name, other place: near Brighton vs
      Stetchworth, Cambridgeshire, England"; docs/site_flow.md reports the 15 wrong pairings over 9 sites.
- [x] Place mode opens ON the works: the map flies to the site's own box (the built site's extent), centred, zoomed
      so the works fill the view, before the drawing appears. Verified 2026-10-14 (iteration 200): part 4 of
      tests/test_fit_queue.py (green in this session's full-suite run) opens the placement with the map at the
      site's box before the drawing appears.
- [x] Place mode hides every overlay already on the site (survey sheets, earlier drawings) while it is open, and
      brings back what was showing when it closes. Verified the same way: part 4's seed check sees the seeded
      dep layer hidden (incl. visibility) while place mode is open, and the second run's Cancel restores it
      exactly.
- [x] The drawing starts ON the map: semi-transparent over the ground at the site, sized from its scale bar where it
      has one, otherwise from the site's known size, north-up (or by its north arrow). The owner moves it by dragging,
      scales and rotates it with handles (or modifier+drag / wheel), with an opacity slider. Saving works from this
      direct placement alone. Pinning exact spots (a point on the drawing to a point on the ground) stays available as
      a refinement on top, not as the only way in. Verified 2026-10-14 (iteration 200): part 4 - the drawing is
      on the map from the first frame at the propose anchor; drag/wheel/shift+wheel and the pin refinement are
      checked against the page's own fit; Save from the placement alone reads back the 17-key by:hand doc from
      the temp store.
- [x] Working space: the map is the main surface in place mode. The page picture is a small, collapsible reference
      (or not needed at all once the drawing is on the map); the side panel holds only what placing needs. Before
      and after screenshots at 1440x900 in docs/site_flow/. Verified 2026-10-14 (iteration 200):
      place_before.png / place_after.png measured 1440x900; the "The working space (task 307c)" docs section
      cites them; every other page layout keeps its pinned footprints (green in the same suite run).
- [x] Saving still writes "by": "hand" and runs the one-site line (305), and the existing hand fits load and save
      unchanged. Checked in a real browser on two queue sites the way the owner uses it (place, move, scale, save,
      see it on the map), then the test fits reverted. Tests cover the queue place-check and the save path.
      Verified 2026-10-14 (iteration 200): tests/test_owner_check.py (two derived queue sites, real headless
      Chrome, the one-site line, the revert proven) green in this session's suite run; the place-check tests
      are 309's (804's namesake + real tests, 805's drift test) and green too; the golden hand-fit hashes and
      test_fit_provenance stay green.

## Notes
- Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-14, iteration 200, agent a - **TASK DONE.** The driver returned the parent after
all four subtasks (307a, 307b, 307c, 307d) and the carved 309 (via 804/805) had merged to
main (this branch = driver sync a237650 over the 307bc close 4549978). This session
verified the parent's six boxes on the merged tree and set Status: done; no code, data or
other-task files changed. Full evidence in the ticked boxes and the 2026-10-14 307
DECISIONS entry.

What was verified:
- Box 1 (right place, 309/804/805): ran the build's own check (tools/fit_queue.
  _place_flags with _place_store('.') over the committed 180-entry queue) -> 0 residual
  namesake pairs. n0686_1 ("The Devil's Dyke Camp, near Brighton") is out of the queue -
  the candidate on the unbuilt Sussex hillfort's review item (data/review/
  devil-s-dyke-hillfort-q17674160.earthworkenglan01allcgoog_n0686_1.json, reason "same
  name, other place: near Brighton vs Stetchworth, Cambridgeshire, England"); the
  Cambridgeshire site keeps only n0662_1 ("SWEALD"). docs/site_flow.md's 309 section
  reports the 15 wrong pairings over 9 sites the rebuild found, with the list and the
  H1/H2 rules.
- Boxes 2-4 (open on the works, hide/restore overlays, on-map drawing + gestures +
  save): re-proven by this session's full-suite run (177 passed / 1 skipped / 0 failed,
  497.6 s) - part 4 of tests/test_fit_queue.py, the card tests, the part-1 propose
  tests, test_fit_provenance and the golden hand-fit set.
- Box 5 (working space): place_before.png / place_after.png measured 1440x900; the
  "The working space (task 307c)" docs section cites them; the pinned footprints of every
  other page layout are green in the same run.
- Box 6 (by:hand, the one-site line, two queue sites in a real browser, then reverted):
  tests/test_owner_check.py (two DERIVED queue sites, real headless Chrome, the one-site
  line, the shared store proven byte-identical after) green in the run; the place-check
  tests are 309's (804's namesake + real tests, 805's drift test) and green too.

Nothing left on this task. The one open follow-on from the 307 line is tasks/242 (the
307d owner-check screenshot drift, filed by 307bc - its own owner; it postdates the six
boxes - screenshot stability, not a box requirement - and does not block done).
