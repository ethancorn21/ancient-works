Status: split
# 306: Look at every agent-placed fit on the page - none reaches the map unseen
Depends on: 303
Touches: data/db/platefits/, data/review/, web/data/sites.json, web/data/review.json, web/data/sites/, docs/site_flow.md, docs/site_flow/

## Goal
Low residuals do not prove a fit is in the right place: Stonehenge's fabricated fits had 0-44 m residuals and sat
2-3x too big. Shotwick (206, `by: agent`) is on the map with 14-19 m residuals and nobody has looked at it.
Every fit not placed by the owner gets looked at the way a visitor sees it before it stays on the map.

## Acceptance criteria
- [ ] Every platefit document with `by` other than "hand" is opened in a browser over the aerial photograph (and the
      LiDAR where there is some), one screenshot each in docs/site_flow/agent_fits/, with one line each in
      docs/site_flow.md: what the drawing's lines sit on (the real banks, walls, ditches) and the verdict.
- [ ] A fit whose drawn works visibly miss the real ones (wrong size, shifted, rotated) leaves the map: its picture goes
      to the site's review item with the reason, the document is removed, and the site's entry is rebuilt with
      tools/site_done.py. A fit that sits right stays, and says so.

## Notes
- Do not change any `by: hand` document. Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over
(2026-10-14, iteration 139, agent c - driver returned the parent after 306a-f all finished.
Verified the parent's two boxes with fresh eyes in this checkout (main merged at f31c874);
306a-f deliverables hold; found the one remaining gap (16 lead-port docs, no record) and
filed subtask 306g. Parent stays `Status: split` until 306g is done, then it can close.)

**State (verified this session, by running code - store census 2026-10-14).**
- Store: 71 docs = 49 `by: agent` (ALL `fitter: matcher`, and ALL on the map - each is a
  `fit.doc` overlay in its site's depictions.json) + 22 `by: hand` (out of scope, untouched).
- Box 2 (wrong fits leave the map) VERIFIED for everything that ever reached the map:
  shotwick's item (data/review/shotwick-...n0575_1.json) holds c_e6e5490609414bb9 with the
  "306a audit 2026-10-12: the drawn moated ring spans ~188 m..." reason, the doc is gone
  from the store, shotwick's depictions.json carries no fit overlay; bethlehem's item
  (data/review/bethlehem-q2523914.c_b31c3de3630246bc.json) holds all 12 removed docs with
  reasons (7 "306a audit ... wrong place", 2 "306a audit ... wrong kind", 3 212b line-check
  fabrication entries), bethlehem's depictions.json is empty of fits; '306c audit' = 9,
  '306d audit' = 14, '306e audit' = 10 occurrences across data/review/ (the orphan 303-way
  upserts). No wrong fit remains on the map.
- Box 1 (every non-hand doc: browser shot + one line): HOLDS for 33 of the 49 current
  docs - per-doc verified that each has its bullet in the section AND its aerial shot
  AND (where the site has relief.jpg) its relief shot in docs/site_flow/agent_fits/.
  The 16 without any record: arras, avesnes-sur-helpe, bavay, burcht-van-leiden x2,
  cahokia c_1a7c2a11c3a0dd21, douai, gouda (306f survivor), gravelines, groningen,
  le-cateau-cambresis, lille, saint-omer, utrecht, valenciennes, old-sarum c_b2701b5231da42f2
  (= 14 new lead ports + gouda + the old-sarum coarse candidate that 77405cf turned into a
  doc). They are the lead's own ports (20277f3, 0685a4c, 77405cf - the last stated
  "eye-checked"; the 306f lead close records the same practice) -> subtask 306g.
- Original 112 at the split, fully accounted for: 34 still in the store (the 33 with
  records + gouda), 78 deleted (13 by 306a's audit removals; the rest by 212b's final
  sync 6ce742f, whose deletion list included every 306c/d/e/f doc). The 306e/306f
  populations are closed by the lead's own ruling (10dcb23: "306e + 306f done
  (superseded) ... survivors are eye-checked matcher re-fits"; 306f file: "Nothing left
  to audit") - no lines were written for their 20 docs (3 306e + 17 306f), and none are
  re-audited: that was the lead's decision.
- 306e's last-3 gap: windmill-hill n0558_2 (DELETED - Lewes Down toponymic collision) and
  york x2 (c_8dac KEPT in item - owner's call; c_a7db DELETED) were judged in 49ca718 but
  their 3 section lines and 303-way item upserts never ran before the lead's close (the
  items still hold the 212b line-check entries). 306g backfills the 3 lines only (no item
  edits - the lead closed 306e with those entries as-is).
- Suite baseline here: the driver's newest loop-start note (1 red: agent a's in-flight
  307 tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, 159
  passed, 1 skipped) matches the 306d/306c hand-over experience; test_gate.py stays
  excluded (pre-existing driver-baseline red). No 306 file is touched by agent a's work,
  so my red set = {that one 307 test}.

**NEXT (when the driver brings the parent back after 306g is done).**
1. Re-run the box-1 census (the re-derivation script in 306g's Notes: every `by != hand`
   store doc must be the head of a bullet in the section; per-doc: aerial shot present,
   relief shot where the site has relief.jpg). Expect 0 gaps. If any gap remains
   (e.g. a further lead/batch port landed since 306g), file one more audit subtask before
   ticking - do not tick over a gap.
2. Tick box 1 (wording note: the 13 deleted 306f docs have no lines by the lead's explicit
   close, recorded in the 306f file; every doc that EXISTS has shot + line). Tick box 2
   (re-spot-check bethlehem/shotwick items + depictions while at it - they can only lose
   entries, not gain wrong fits, but confirm no 306g removal was botched). Set
   `Status: done`.
3. Do not touch `by: hand` docs, the lead-closed 306e/306f item entries, or agent a's
   in-flight files (web/fitkit*, tests/test_fit_queue.py).
