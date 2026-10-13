Status: split
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
- [ ] Wired into tools/site_done.py's fit step; a test runs it end to end on one hand-fit site's files (no network).
- [ ] Run on Stonehenge: whatever it puts on the map, checked in a browser against the real stones (screenshot in
      docs/site_flow/); say plainly if it places nothing.

## Notes
- The 20 hand fits and their golden file stay untouched.
- Do not start 207 or any other task: the lead gives the next one when this is done.

## Hand-over

(2026-10-13, iteration 208, agent c - the driver returned the parent: all existing subtasks
(302a/302b done, 302c/302d dropped) were terminal, so this session re-verified the parent's
boxes with fresh eyes and ticked 1-3. **Correction to the 207 hand-over:** it claimed
subtasks 302e/302f/302g were "created", but no such files existed on disk (the driver's
post-207 commit 745056e touched only this file) - this session WROTE them for real:
tasks/302e-heldout-runner-21.md, tasks/302f-matcher-station-test.md,
tasks/302g-stonehenge-matcher-run.md. Status stays split (4 and 5 open). No code or data
touched this session; the suite was NOT run (bookkeeping step; each subtask diffs against
the NEWEST driver loop-start note in its own PROGRESS.md - 306d-era baseline: 10 failed /
130 passed / 1 skipped of 141, 2026-10-12/13).)

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
