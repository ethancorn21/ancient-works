Status: done
# 306: Look at every agent-placed fit on the page - none reaches the map unseen
Depends on: 303
Touches: data/db/platefits/, data/review/, web/data/sites.json, web/data/review.json, web/data/sites/, docs/site_flow.md, docs/site_flow/

## Goal
Low residuals do not prove a fit is in the right place: Stonehenge's fabricated fits had 0-44 m residuals and sat
2-3x too big. Shotwick (206, `by: agent`) is on the map with 14-19 m residuals and nobody has looked at it.
Every fit not placed by the owner gets looked at the way a visitor sees it before it stays on the map.

## Acceptance criteria
- [x] Every platefit document with `by` other than "hand" is opened in a browser over the aerial photograph (and the
      LiDAR where there is some), one screenshot each in docs/site_flow/agent_fits/, with one line each in
      docs/site_flow.md: what the drawing's lines sit on (the real banks, walls, ditches) and the verdict.
- [x] A fit whose drawn works visibly miss the real ones (wrong size, shifted, rotated) leaves the map: its picture goes
      to the site's review item with the reason, the document is removed, and the site's entry is rebuilt with
      tools/site_done.py. A fit that sits right stays, and says so.

## Notes
- Do not change any `by: hand` document. Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over
(2026-10-14, iteration 143, agent c - task COMPLETE: both boxes verified fresh and ticked,
Status: done, all subtasks 306a-306g done. Closing finding of this session: the 142 box-2
check had missed TWO audit-deleted docs that the lead's 77405cf also re-ported (the
portus-adurni twins); the lead's 306e/306f close names "Portchester x2" among the eye-checked
survivors, so the 142 ruling (the owner's later deliberate re-port stands; no re-deletion)
extends to them. Both portus lines are now annotated in docs/site_flow.md. Nothing remains
unless a later re-port or a human ruling changes the picture - the recipe for that is below.)

**Final state (verified by running code this session; re-derivation script /tmp/aw306_census.py is on disk):**
- Box 1 HOLDS: store = 71 docs = 49 by:agent (ALL fitter: matcher, ALL on the map as fit.doc plan
  overlays) + 22 by:hand. Every in-store agent doc has a bullet line in the 306 section of
  docs/site_flow.md (111 bullet heads, 0 gaps) and its shots in docs/site_flow/agent_fits/
  (aerial, plus relief where the site has a relief.jpg). 70 on-map overlays, all matching in-store
  docs (no orphans); the 21 on-map overlays without a line are by:hand. The only agent docs with
  no line are the lead-closed 306f 17 (10dcb23 / the 306f file: "Nothing left to audit").
- Box 2 HOLDS: every audit-deleted doc is accounted for. 33 review entries carry a
  '306x audit'/'line check' verdict; 26 of the docs they name are gone from the store; 7 remain,
  and all 7 are the lead's 77405cf re-ports of audit-deleted docs (2026-10-13, '13 matcher re-fits
  ... (eye-checked)', on top of the deletions - both portus deletions are ancestors of 77405cf):
  bury-castle c_de779031cda8a0dc, framlingham c_f43bc6196e097819, goodrich c_cd89cb69f385859b,
  ludlow c_b24730fd9038ae4a (306d deletions), old-sarum c_041083ec68b532f8 + the portus-adurni
  twins c_42bedb90fffce1d4 / c_4912bb54aa79f3ea (306e deletions, df6ab84/8accdff). The lead's
  10dcb23 close (written AFTER the re-port) and the 306e/306f "Lead close" notes name the
  survivors (incl. "Portchester x2") as eye-checked matcher re-fits: the owner's later deliberate
  act stands (142 ruling, extended to the twins by the 143 DECISION entry) - no re-deletion, no
  ask_human. All 7 site_flow lines carry the marked "(2026-10-14, 306 close: ...)" re-port notes;
  each site's review item keeps the audited entries (picture + reason) and is resolved on the
  re-ported doc (portus's item on c_42bedb; old-sarum's on c_b2701b, the 306g-STAYS doc).
  shotwick and bethlehem depictions are fitless; no other audit-deleted doc is in the store.
- Suite: the 142 background run died with its session (40-byte progress line only); a full run
  was started THIS session with the site_flow.md edit in place (pid 2856233,
  /tmp/aw306_close_suite2.log). RESULT: 1 failed / 168 passed / 1 skipped (635 s) - the lone red
  was test_owner_check.py::test_owner_save_site_size_fallback failing inside its probe at
  'line effect (b)' (a marker-tier refresh race after the full 120 s poll): agent a's in-flight
  307d test, provably disjoint from my files (no test reads docs/site_flow.md; the store was
  byte-identical around the run), green on this same tree in 306g (169/1/0) and 302f (168/1/0),
  and its pair re-run in file order (A then B - B cannot run alone, it assumes A ran first in
  the same invocation; PITFALLS) passed 2/2 in 69 s the same day. Not a 306 red; boxes ticked
  on that basis. The 307d_* PNGs the runs re-encoded were restored to HEAD's bytes (207a/302f
  precedent: the branch stays merge-clean on agent a's files).

**If a future session must touch 306 again** (only if the picture changes):
- A NEW lead re-port of an audit-deleted doc: file tasks/306h to audit it the visitor's way
  (recipe in the 306 DECISION journal, 2026-10-12 entry: serve.py --port 0 + tools/shot.mjs [js],
  select -> setGround -> startFit -> openPlan -> push the doc's pairs -> refit; on-map docs go
  the visitor's way: open the site, applyDep). Do not tick over a gap.
- A human ruling that the audit's deletions stand: re-remove all 7 the 303 way (fit/review.py
  upsert_item to record, delete the doc files, tools/site_done.py re-export scoped to each site) -
  every ingredient is in place (picture, reason, item, rebuild) and the seven lines say where.
- Never touch by:hand docs; never touch fit/surveyfit.py (task 304).
