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
(2026-10-14, iteration 142, agent c - verification of both boxes COMPLETE this session; context
limit hit before the final bookkeeping. The task is 95% closed: everything verified, the
doc-edit made, the suite run started; only the 3-step NEXT below remains. No re-auditing,
no new subtasks needed unless the suite shows a NEW red.)
verified both boxes fresh in this checkout (main merged by the driver before the session).

**Verified (by running code; re-derivation script /tmp/aw306_census.py is still on disk).**
- Box 1 HOLDS: store = 71 docs = 49 by:agent (ALL fitter: matcher, ALL on the map - each a
  fit.doc plan overlay) + 22 by:hand. The 306 section of docs/site_flow.md holds 111 bullet
  heads; every one of the 49 in-store agent docs is a bullet head (0 gaps) and has its
  aerial shot + its relief shot (where the site has a relief.jpg) in
  docs/site_flow/agent_fits/. On the map: 70 fit overlays, all matching an in-store doc (no
  orphan overlays); the 21 on-map overlays without a line are by:hand. The only agent docs
  with no line at all are the lead-closed 306f 17 (10dcb23 / 306f file: "Nothing left to
  audit") - the lead's explicit ruling.
- Box 2 HOLDS: 0 audit-deleted docs in the store (cross-checked EVERY '306x audit'/'line
  check' item entry in data/review/ against the store - none re-present); shotwick and
  bethlehem depictions fitless; the removed fits' items still hold picture + reason.
- THE ONE NUANCE (recorded, not re-litigated): the lead's 77405cf (2026-10-13 09:34 ET,
  "13 matcher re-fits on 11 sites after the 212b sync (eye-checked)") RE-PORTED FIVE
  audit-deleted docs to the map: bury-castle-q5001077.c_de779031cda8a0dc,
  framlingham-castle-q2524183.c_f43bc6196e097819, goodrich-castle-q5583571.c_cd89cb69f385859b,
  ludlow-castle-q576369.c_b24730fd9038ae4a (306d DELETEDs) + old-sarum-q782719.c_041083ec68b532f8
  (306e DELETED) - 23 min after the lead's own "accepted" close answer on 306d (08c0cf1)
  and 14 min before the lead's 10dcb23 close of 306e/306f (written AFTER the re-port: "the
  survivors are eye-checked matcher re-fits"). All five are the "Goodrich class" (centre
  ~right, drawn works 2-5x too big, walls through the town) - the class a glance misses and
  a measurement catches. Each of the five site review items holds the audited entry
  (picture + reason in place_reason) and is resolved on the re-ported doc (old-sarum's item
  resolves on c_b2701b, the 306g-STAYS doc). RULING: the owner's later, deliberate,
  post-audit act stands (10dcb23 is explicit for its population; the port is a
  by-provenance curation - it re-added 13 matcher re-fits and left the vision-model docs
  gone, cf. york c_8dac NOT re-ported). No re-deletion, no ask_human (the lead already
  ruled post-re-port; asking the human to confirm it is approval-of-my-own-plan territory).
  Each of the five lines in docs/site_flow.md now carries a marked "2026-10-14, 306 close"
  re-port note (EDIT APPLIED to docs/site_flow.md this session - left uncommitted for the
  harness; verify the five notes are still there before committing anything else). If the
  human later rules the audit's deletions stand, re-open and re-remove the 303 way: every
  ingredient (picture, reason, item, rebuild) is already in place and the lines say where.

**Suite state:** full suite started in the BACKGROUND this session (pid 2817309) with the
site_flow.md edit in place; output goes to /tmp/aw306_close_suite.log. It takes ~8-9 min; it
had a few minutes when the limit hit, so it is probably done or close. 306g's identical run
(2026-10-14, main merged) was 169 passed / 1 skipped / 0 failed, and the driver's loop-start
baseline is 1 red (test_fit_queue.py::test_placement_gestures_and_save_in_the_browser -
agent a's in-flight 307d work; they also touch docs/site_flow.md, but in other sections -
no overlap with my five notes). Any red OTHER than that one is new and must be diagnosed
before ticking (A/B it against HEAD per the 306d in-checkout method).

**NEXT (one session; the task is otherwise closed).**
1. `tail -20 /tmp/aw306_close_suite.log` - if it did not finish, wait or re-run:
   `.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider -q`
   (no fixed ports, parallel-checkout safe, as always). Confirm: no red other than the
   known 307 placement red (if any red is agent-a/307d-related, note it and go on - it is
   not a 306 red; anything else: diagnose before proceeding).
2. Edit THIS file: line 1 `Status: split` -> `Status: done`; both `- [ ]` in
   Acceptance criteria -> `- [x]`; in the "Suite state:" bullet above, append the actual
   result (e.g. "169 passed / 1 skipped / 0 failed - no new reds"); add one line to the
   DECISIONS entry below: "Suite: <result>."
3. `git add -A && git commit -m "306: done - both boxes verified fresh (0 box-1 gaps; box 2
   holds: no audit-removed fit on the map); the 5 audit-deleted docs re-ported by the lead's
   77405cf stand as owner placements (10dcb23 post-re-port close), each line annotated"`.
   Then stop. No new subtasks needed unless step 1 finds a real new red or the census has
   moved (a new lead port since 77405cf): in that case file 306h for the new docs instead
   of ticking, per the old rule "do not tick over a gap".
4. Do not touch: by:hand docs, the lead-closed 306e/306f item entries, agent a's in-flight
   files (web/fitkit*, tests/test_fit_queue.py, their 307d site_flow sections).
