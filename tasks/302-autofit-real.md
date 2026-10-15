Status: done
# 302: An automatic fit that is not made up - the station that feeds the line
Depends on: 301
Touches: fit/, pipeline/plan_fit.py, tools/site_done.py, tests/, docs/site_flow.md, docs/site_flow/, docs/gate.md, requirements.in, requirements.txt, data/inkfit/, data/review/, data/db/platefits/, web/data/sites.json, web/data/review.json, web/data/sites/stonehenge/

## Goal
The line works, but nothing reaches the end of it: 301 found every one of the batch's 110 automatic fits is the vision
model's fabricated pattern (Stonehenge 0 drawings, Argentoratum 0 drawings). Sending more sites down the line now
only fills the review queue. Under one-piece flow the defect is fixed at the station that makes it: the automatic
fit itself.

The owner's hand fits (20 of them, tests/golden/hand_fit_*; Maiden Castle's DPLA plan was added on the Mac
2026-10-11) are what a right answer looks like: click a few matching spots on the drawing and on the ground, solve
the similarity. An automatic fit must find spots that really match, not invent them.

## Acceptance criteria
- [x] An automatic fit method whose matching points come from the pictures themselves (the drawing's ink against the
      site's LiDAR relief and/or aerial: edges, ridges, ditch lines - the 2026-10-09 Fudge proof fitted a plate by
      ridge contrast), not from a model's list of coordinates. A vision model may give a starting guess only.
- [x] Measured against the hand fits as truth, held out (the method never sees the hand pairs): for each of the 20,
      the corner error of the automatic fit against the hand fit, in metres, in a table in docs/site_flow.md. The
      fabrication check passes every automatic fit it produces. Report the numbers as they are, good or bad.
- [x] The method decides for itself when it is not sure (a score with a threshold set on the held-out table), and an
      unsure fit goes to the review queue with the reason, never to the map.
- [x] Wired into tools/site_done.py's fit step; a test runs it end to end on one hand-fit site's files (no network).
      302f delivered it: site_done._fit:82-84 calls matchfit.run first on every undocumented picture when the
      matcher answers /health, and tests/test_matchfit_station.py runs the whole line as a hermetic subprocess on
      badbury-rings-q798831's files (the golden's 21 include its hand doc) against committed ELoFTR fixtures served
      from an ephemeral-port stub, RoMa at a dead port, and a socket guard that dies loudly on any other connection -
      confident branch (doc written, built, queue untouched) and unsure branch (no doc, the candidate in the review
      item with its reason, page grows by exactly it). Both pass on the current tree (55.3 s, this session's run).
- [x] Run on Stonehenge: whatever it puts on the map, checked in a browser against the real stones (screenshot in
      docs/site_flow/); say plainly if it places nothing. 302g delivered it: the live ELoFTR-only run of 2026-10-14
      (RoMa down) was unsure or empty on all 14 candidates (best 7 of the 10 consistent points it requires), wrote
      0 documents, left every item entry byte-identical, and the map stands as before; checked in headless Chrome
      against the sarsens (the 1842 six-inch sheet's ink circle and Avenue ride on the real stones) - the plain
      statement, "the method placed nothing on Stonehenge", is in docs/site_flow.md's task-302g section, with the
      run recorded in docs/site_flow/stonehenge-matcher-2026-10-14.log and the shot in
      docs/site_flow/stonehenge-matcher-2026-10-14.png.

## Notes
- The 20 hand fits and their golden file stay untouched.
- Do not start 207 or any other task: the lead gives the next one when this is done.

## Hand-over

(2026-10-14, iteration 138, agent c - driver returned the parent after all subtasks
reached terminal states (302a/302b/302e/302f/302g done, 302c/302d dropped). This session
re-verified boxes 4 and 5 with fresh eyes and ticked them: **task 302 is DONE** - all five
boxes ticked, full suite green, no remaining work. If the driver's re-check reopens it, the
verdicts below are the state of the tree at this commit.)

**Box verdicts (re-verified this session on the current tree):**
- **Box 1 MET** (ticked at 208, re-confirmed): fit/inkfit.py (302a: plate ink skeleton vs LiDAR
  relief, ridge-contrast objective, frozen no-model variant) and fit/matchfit.py (the lead's
  pretrained MatchAnything ELoFTR/RoMa correspondences - points computed from the images, never a
  vision-model list) both exist on this tree; the line is matcher-first, site_done._fit:82-84
  (read this session: matchfit.run first on every undocumented picture when matchfit.reachable()).
- **Box 2 MET** (ticked at 208, checkpoint re-run this session): docs/site_flow.md:129 (pre-
  registered protocol, "the method never sees the hand fits") and the 21-row table at :226-248
  (corner errors reported as they are; fabrication column silent on every placed fit; the lone
  non-silent cell camp-d-attila "not enough wall ink"). Checkpoint re-checked by script: data/
  inkfit/heldout/results.json has 21 doc entries, 0 errors, 0 re-runs, all model "no-model",
  all at 2026-10-11T22:47:37.081160+00:00; the 21 == exactly the golden's platefit documents
  MINUS fort-ancient-q5470727.ancientmonuments00squi_n0076_1, which joined the golden AFTER the
  one-shot was spent (lead commit c72706b, 2026-10-14) - the one-shot is frozen, never re-run.
  The matcher's own held-out tables (data/matchfit/heldout{,_located,_roma}, docs/matchfit.md)
  remain in place.
- **Box 3 MET** (ticked at 208, re-confirmed by reading fit/matchfit.py:81-110 this session):
  judge() - ELoFTR inliers>=10 & |rot|<=30 deg, RoMa inlier fraction >= 0.4, both plus the spread
  guard (ratio>=0.1, sd>=20 px); "not sure: ..." reasons; matchfit.run writes a document only
  when judge is silent; second line of defence at site_done._sync_doc:204-206 (spread guard on
  fitter:"matcher" docs before any build). The 302f unsure test proves the queue path end to end.
- **Box 4 MET (ticked this session, via 302f).** Wiring: site_done._fit:82-84 (above). Test:
  tests/test_matchfit_station.py (340 lines, committed fde3954/330a9f4) - BOTH tests pass on
  this tree in 55.32 s (run this session). The hand-fit site is badbury-rings-q798831 (its hand
  doc is in the golden's 21): a throwaway tree of its files with the doc deleted, tools/
  site_done.py driven as a subprocess, ELoFTR replayed from committed fixtures (records.json /
  records_unsure.json, keyed by sha256 of the exact request body, recorded live against
  127.0.0.1:8091) served from an in-process stub on an ephemeral loopback port, RoMa pinned at
  a dead ephemeral port, and a socket guard (a pass-through variant of test_fit_queue's) that
  raises AssertionError on any connection other than the stub's port - the no-network proof.
  Confident: 11-line stdout ending in the built fit (22/61 six-inch x0.35, rot 3.6 deg), matcher
  doc written (by:agent/auto/fitter:matcher + matcher block), built, queue and site entry
  untouched. Unsure: 8-line stdout ("not sure: 8 consistent points (need 10) [six-inch-1st .webp
  x0.7, rot -44]"), no doc, the candidate in the new review item with the batch's "no model
  answer" plus the scale-bar proposal, the published page grown by exactly that one item, all
  other queue files byte-identical. Drift detection: each fixture header carries sha256 of every
  repo input it was recorded from; the test fails with "rerun record.py" (working phase, live
  matcher) when the repo moves. Fixtures and recorder live under tests/fixtures/matchfit_/
  station/ (record.py, records.json, records_unsure.json).
- **Box 5 MET (ticked this session, via 302g).** All deliverables present and verified this
  session: (a) docs/site_flow/stonehenge-matcher-2026-10-14.log (committed 92565b6) - run date
  2026-10-14 02:06-02:10 CDT exit 0, ELoFTR up / RoMa down stated with the verbatim probes, the
  14-entry pre-run snapshot verbatim, all 14 per-candidate verdicts (matcher: 3 empty / 11
  unsure, best 7 of 10; batch: not run - every candidate already a review-item entry; docs:
  none written or deleted; item entries byte-identical), post-run state, the plain statement,
  and the full stdout+stderr verbatim (14 per-picture matcher lines, 0 fitted, 456 open of 480).
  (b) docs/site_flow/stonehenge-matcher-2026-10-14.png (committed e8dddee) - headless Chrome on
  server/serve.py --port 0, the #stonehenge-q39671 page: the map's only overlay is the 1842
  six-inch sheet in ink at 85%, and I viewed the shot: the red-ink circle sits on the visible
  standing-stone circle, the ink Avenue on the avenue earthwork running SW, "14 old plans" in
  the book panel. [eval] numbers per the log: corners identical to depictions.json, extent
  998.8 x 996.2 m on the 1000 m box, sarsen centre = sheet centre, no plan/drawing depiction.
  (c) The new section at the end of docs/site_flow.md (appended after agent a's 307d section,
  append-only as required) states plainly: **the method placed nothing on Stonehenge** - the
  a-priori expectation the matcher's own held-out tables predicted, met by the live line.
  Repo state cross-checked against the log this session: the 14 review-item candidates are
  exactly as the log's snapshot (7 fabricated-line, 4 median-residual, 2 feature-based, 1 no-
  model-answer), the site entry {drawings 0, score 1.1, oldest 1842, overlays 1} unchanged, no
  stonehenge platefit document, 1 published stonehenge item.

**Notes hold:** the golden hand-fit files are untouched by this task and verify 41/41 OK
(sha256sum -c this session; the golden is now 22 platefit docs - Fort Ancient joined in lead
c72706b - plus 19 site.json, since 303's re-key 1f562ca; the "20 of them" in the goal text is
the pre-maiden-castle world). No other task was started or touched.

**Tests (full suite, this branch, this session, .venv current):** 172 passed, 1 skipped,
0 failed in 502.11 s (log /tmp/aw302_parent_suite.log) - against the newest driver loop-start
note (2026-10-13: 1 failed / 159 passed / 1 skipped of 161): the note's lone failure (tests/
test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, agent a's 307bb work) is
green on main, and the suite has since grown to 173 tests (211/223/224/212/236/307/302f/302g
work merged). No new reds.

**Team-mode caution for any re-open:** the working tree carries four MODIFIED agent-a 307d
PNGs (docs/site_flow/307d_{A,B}_{4-saved,5-reload}.png) - 307d's Touches, regenerated by its
test on every full-suite run in this checkout. They are NOT part of this task: never commit
them from this branch (this session's commit covers only the task file + DECISIONS.md,
exPLICIT paths). web/data/review.json is a generated whole-queue publish shared with agent a's
212 work: on any merge conflict regenerate it with fit/review.py export, never hand-merge.

**Re-read (if anything reopens this task):** tests/test_matchfit_station.py + tests/fixtures/
matchfit_station/record.py (the hermetic-stub + guard design; rerun record.py in the working
phase if the drift detector fires - it needs live ELoFTR at 127.0.0.1:8091); fit/matchfit.py
judge/fit_row/run (thresholds and the document-only-when-silent contract); tools/site_done.py
_fit/_sync_doc (the matcher-first wiring and the spread-guard second line); tools/shot.mjs
(Chrome 155 + NODE_PATH=/home/agent/tools/shot/node_modules + POSTWAIT recipe) and server/
serve.py --port 0 (the browser-check pattern); the 302g section of docs/site_flow.md and the
log file it points at.

**Box verdicts (re-verified this session, fresh eyes, on the current tree):**
- **Box 1 MET (ticked).** Two methods whose matching points come from the pictures themselves:
  fit/inkfit.py (302a: the plate's ink skeleton vs the site's LiDAR relief, ridge-contrast
  objective, frozen no-model variant, model injectable - the Fudge proof done properly) and the
  lead's fit/matchfit.py (pretrained MatchAnything ELoFTR/RoMa correspondences between the plan
  and the relief / aerial / OS sheets - computed from the images, never a vision-model list of
  coordinates). The line is matcher-first: site_done._fit:78-84. The lead since added
  fit/matchfit2.py (two-stage: coarse whole-ground hit, then windows centred on the hit) and
  fit/matchfit_queue.py (accept-rule sweep over a recorded queue run) plus fit/surveyfit* -
  LEAD work; none of it is part of a box here, and 302c/302d (the dropped ink decision/wiring/
  Stonehenge chain) stay dropped.
- **Box 2 MET (ticked).** docs/site_flow.md line 129, "The one-shot held-out measurement of the
  ink fit (task 302b, pre-registered before the run)": the frozen protocol, the 21 sorted docs,
  "The method never sees the hand fits", then the 21-row table at lines 226-248 (corner errors
  231.2-2203.6 m, reported as they are; fabrication column silent on every placed fit; the only
  non-silent cell is camp-d-attila "not enough wall ink (2 candidate points, need 4)").
  Checkpoint re-verified this session: data/inkfit/heldout/results.json has 21 entries == the
  golden's 21 exactly (set-equal, checked by script), 0 errors, 0 re-runs, all model "no-model",
  one fixed at 2026-10-11T22:47:37.081160+00:00. The matcher's own held-out table is
  docs/matchfit.md (ELoFTR 7/21 accepted at >=10 inliers, 0 wrong, worst centre 55 m) with its
  checkpoints under data/matchfit/heldout{,_located,_roma}.
- **Box 3 MET (ticked).** fit/matchfit.judge(): ELoFTR inliers>=10 & |rot|<=30; RoMa inlier
  fraction >=0.4 (thresholds set on the held-out + queue tables - the docstring cites
  docs/matchfit.md sections 7-8); both plus the spread guard (ratio>=0.1, sd>=20 px, the Aesica
  near-line case); human-readable "not sure: ..." reasons. matchfit.run writes a document ONLY
  when judge is silent (an unsure candidate is just printed and stays in the queue / review item
  with a reason - no doc, so nothing can be built); second line of defence: site_done._sync_doc
  (tools/site_done.py:204-206) applies the spread guard to fitter:"matcher" docs before any
  build.
- **Box 4: wiring MET, TEST not met -> 302f.** site_done._fit:78-84 calls matchfit.run first on
  every undocumented picture (review-item ones too) whenever matchfit.reachable(); _sync handles
  the docs it writes. But `grep matchfit tests/` is EMPTY: test_site_done.py runs the line on
  stonehenge (not a hand-fit site) with the matcher unreachable, so the matcher station has never
  been exercised end to end. 302f's site: badbury-rings-q798831 (one candidate picture - a
  confident fit empties `uncovered`, so the vision batch never runs and the only network in the
  test is the stub; all ground images local; the golden's 21 include its doc, deleted in the tmp
  copy only; its ELoFTR held-out best is six-inch-1st.webp x0.35, 22 inliers, 3.62 deg, 58.6 m
  corner / 2.9 m centre - verified this session from data/matchfit/heldout/results.json, which
  also has heldout_located and heldout_roma variants).
- **Box 5 not met -> 302g.** No post-matcher Stonehenge run is recorded: stonehenge-q39671 =
  0 drawings, 1 overlay (checked in sites.json this session), 14 candidates in
  data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json (7 "line check:
  fabricated...", 4 "median residual > 45 m", 2 feature-based, 1 "no model answer"), no matcher
  doc; the only screenshot (docs/site_flow/stonehenge.png, 2026-10-11) predates the matcher. The
  lead dropped 302d because the INK method was dead; box 5 is method-agnostic and was never
  commented on - 302g runs the current matcher-first line (the a-priori expectation from the
  queue run is "places nothing", which the box accepts - it must be said plainly, with a
  screenshot of whatever is on the map).
- **Notes hold.** All 40 lines of tests/golden/hand_fit_docs.sha256 verify in this checkout
  (sha256sum -c: 40 OK, run this session). The golden = 21 hand docs + 19 site.json since 303's
  re-key 1f562ca; the held-out truth set is "the golden's platefit docs"; the 20-of-the-parent-
  world is superseded.

**LIVE DEFECT (302e, re-confirmed by running this session):**
`.venv/bin/python fit/inkfit_heldout.py table` -> SystemExit "expected the 20 golden hand-fit
documents, found 21" (golden_docs() still asserts 20). `run` and `selfcheck` call the same
function, so all three commands die. RESOLUTION of the 207 Re-read item: fit/matchfit_heldout.py
does NOT call golden_docs() - it uses ih.GOLDEN (reads the golden file itself), ih.MAIDEN,
ih.hand_similarity, ih.corner_metrics and ih.precheck; its own doc_ids() and its table/load
read its own data/matchfit/ checkpoints. So the assert breaks only inkfit_heldout's own
commands; the fix scope is exactly fit/inkfit_heldout.py's golden_docs/doc_ids/precheck
(302e's boxes). The one-shot is SPENT: compatibility fix only, never re-measure, never edit the
docs table. (The 207 hand-over's "fit/matchfit_heldout will hit the same wall" was wrong -
noted here so the 302e session does not "fix" matchfit_heldout's doc_ids.)

**Environment (verified this session):** .venv current (numpy 2.5.4, scikit-image; ALWAYS
.venv/bin/python). ELoFTR REACHABLE: 127.0.0.1:8091/health ->
{model: zju-community/matchanything_eloftr, device: RTX 5060 Ti}. RoMa :8092 REFUSED (302g's
live run degrades to ELoFTR only; 302f pins ROMA_URL to a dead ephemeral port so the test is
deterministic either way). Suite NOT run this session (bookkeeping step) - last known baseline
(306d note, 2026-10-12/13, main): 10 failed / 130 passed / 1 skipped of 141 (test_fit_queue
placement dep:null + agent a's in-flight 307 work).

**Next (driver order, all three subtask files now exist on disk):** 302e (small compatibility
fix) -> 302f (no-network e2e test of the matcher station) -> 302g (Stonehenge live run +
browser check + plain statement). Team-mode caution for 302g: agent a's 307d also writes
docs/site_flow.md (its changes revert per its task, but the section must be APPEND-only and
touch no other section); web/data/review.json is a generated whole-queue publish shared with
agent a's 212 work - regenerate via fit/review.py export on any merge conflict, never hand-
merge.

**Re-read:** 302e: fit/inkfit_heldout.py golden_docs/doc_ids/precheck (the fix) plus 302b's
"Do NOT touch (frozen by 302b)" list in tasks/302b-heldout-table.md. 302f: tests/test_fit_queue.py
GUARD at line ~99 (socket-dead subprocess guard - 302f needs a variant that allows ONLY the
stub's loopback port) + conftest.py's served fixture (ephemeral-port server idiom) +
fit/matchfit.py match()/fit_row (the exact /match request: base64 PNG, threshold 0.2, max_side
1024) + the data/matchfit/heldout/results.json candidate schema. 302g: tools/shot.mjs (Chrome
155 + NODE_PATH recipe in PITFALLS) + docs/matchfit.md's Stonehenge lines + the current 14-
entry review item.
