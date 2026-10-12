Status: split
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
- [ ] Right place (carved to 309 - agent c, 2026-10-12; the rest of 307 is page work only): every queue entry's
      candidate is checked to show the same place as its site, not just the same name (the book's caption/place
      words and county against the site's place, region and coordinates; Wikidata where it helps). A mismatch leaves the queue and goes to the review queue with the reason "same name, other
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

## Hand-over

(2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,
no code written. This is the plan for the remaining work; the driver hands out the subtasks
in order. Box map: 1 -> 307a (itself re-split: the live work is the lead's 309, agent c);
2-4 -> 307b (SPLIT 2026-10-12 iteration 110 into 307ba = 307b's boxes 1-2, 307bb = 307b's
boxes 3-6 - see the note at the end of this hand-over); 5 -> 307c; 6 -> 307d (the
place-check tests are 309's; 307d proves the save path and the revert).

**Key ground truth (measured this session; the DECISIONS entry has the evidence):**
- The wrong pair in the owner's words: the queue's #1 is earthworkenglan01allcgoog_n0686_1
  ("The Devil's Dyke Camp, near Brighton") on devil-s-dyke-q3307343 (Stetchworth,
  Cambridgeshire). The row's evidence ties it by the name "Devil's Dyke" only (place: {});
  its title names Brighton. The catalog DOES have the right site: devil-s-dyke-hillfort-
  q17674160 (Poynings, West Sussex) - unbuilt (no web/data/sites/<id>/), so 307a moves the
  candidate to a review item on it, not into the queue. Allcroft n0354 ("ARDOCH,
  PERTHSHIRE.", row place field "PERTHSHIRE") is the candidate for Coria and Vindomora
  (both Spain); the catalog has no Ardoch site (12,603 rows, name+aliases), so it goes to
  review with the reason, not a move. The queue is 117 entries today.
- fit/propose.py already computes the anchor the page needs; propose_for works for n0686
  (bar scale '0 100 200 300 400 Yards' with a scale_bar box, north arrow 0 deg ->
  scale_m_px 0.3621, 5 pairs centred on the site, coarse false). fit/propose.py and
  fit/review.py are stdlib-only: tools/fit_queue.py may import both, the check may not
  import pipeline/ (numpy).
- The page already draws ink on the map: index.html refit() maps P.inkUrl (survey-red on
  transparent, makeInk) onto the map's 'fit-prev' image source from the least-squares
  similarity of P.pairs. So "the drawing starts on the map" = on open, set P.pairs to the
  proposal's 5 pairs (the least squares recovers the anchor exactly) + handlers that edit
  the anchor (drag/scale/rotate) and re-emit pairs. The saved doc stays pairs-shaped;
  review.js already shows the pattern for pre-placing pairs on open (RV.pending).
- The review item contract is data/review/README.md (candidate = plan/title/url/evidence/
  pairs/producer extras; resolved write-once); fit/review.py upsert_item is the writer;
  only fit/review.py export writes web/data/review.json (307a calls it in-process from
  the check CLI). The page's review list (web/review.js) gets the reason shown in 307c.
- Baseline on this branch (iteration 107): .venv/bin/python -m pytest -q -> 73 passed,
  1 skipped, green.

**Re-read:** none yet; each subtask writes its own. If 307b turns out bigger than its
3-session budget, split its fly-to/hide-restore from its gestures - but do not reorder
the letters without a note here.

309 note (iteration 109, agent a): the number 309 was briefly claimed twice (my
tasks/309-place-check.md vs the lead's tasks/309-queue-right-place.md - see the 307a
record). Mine is dropped and kept as reference; the lead's file is canonical and agent
c works from it. The reference file carries the implementation notes the lead's shorter
spec leaves to the implementer: the fail-open rule, the re-verified verdict record,
the measured n0686/n0354 cases, the 117-entry count, the 305-shape survival.

307b split note (iteration 110, agent a): 307b is SPLIT into 307ba (its boxes 1-2: the
queue carries the proposal, fit/propose.py root-aware, place mode opens on the works) and
307bb (its boxes 3-6: the gestures, the save, the headless part 4, the docs). No letter
reorder - the driver hands out 307ba then 307bb in order, then 307c, then 307d. The full
design (box 1 implementation plan, the anchor/gesture/wrap sketch, the headless-test
fixture plan) is in 307b's own ## Hand-over and the 2026-10-12 307b DECISIONS entry.
If 307bb itself exceeds its budget, its headless test splits off (307bb's notes say so).
