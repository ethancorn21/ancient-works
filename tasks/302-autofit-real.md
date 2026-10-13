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
- [ ] An automatic fit method whose matching points come from the pictures themselves (the drawing's ink against the
      site's LiDAR relief and/or aerial: edges, ridges, ditch lines - the 2026-10-09 Fudge proof fitted a plate by
      ridge contrast), not from a model's list of coordinates. A vision model may give a starting guess only.
- [ ] Measured against the hand fits as truth, held out (the method never sees the hand pairs): for each of the 20,
      the corner error of the automatic fit against the hand fit, in metres, in a table in docs/site_flow.md. The
      fabrication check passes every automatic fit it produces. Report the numbers as they are, good or bad.
- [ ] The method decides for itself when it is not sure (a score with a threshold set on the held-out table), and an
      unsure fit goes to the review queue with the reason, never to the map.
- [ ] Wired into tools/site_done.py's fit step; a test runs it end to end on one hand-fit site's files (no network).
- [ ] Run on Stonehenge: whatever it puts on the map, checked in a browser against the real stones (screenshot in
      docs/site_flow/); say plainly if it places nothing.

## Notes
- The 20 hand fits and their golden file stay untouched.
- Do not start 207 or any other task: the lead gives the next one when this is done.

## Hand-over

(2026-10-13, iteration 207, agent c - the driver returned the parent: 302a done, 302b done,
302c/302d dropped by the lead. This session verified the parent's boxes: 1-3 MET, 4 half-met,
5 not met, and created subtasks 302e/302f/302g for the rest. Status stays split. No code or data
touched this session; the suite was NOT run.)

**Box verdicts (each verified by reading/running this session):**
- **Box 1 MET.** Two methods whose matching points come from the pictures themselves: fit/inkfit.py
  (302a: the plate's ink skeleton vs the site's LiDAR relief, fit_plate's ridge-contrast objective,
  frozen no-model variant, model injectable - the 2026-10-09 Fudge proof done properly) and the
  lead's fit/matchfit.py (pretrained MatchAnything ELoFTR/RoMa correspondences between the plan and
  the LiDAR relief / aerial / OS sheets - computed from the images, never a vision model's list of
  coordinates). Fresh-eyes re-reads DONE (items from the old hand-over, resolved): fit/inkfit.py's
  _keep_pieces (no-model fallback keeps every surviving piece - labelled variant "no-model"),
  choose_points (0.23/0.71-quantile picks per piece, never a fixed stride; jittered redraw until
  plan_fit.fabrication_pattern is silent, 8 attempts; concedes with "not enough wall ink (2
  candidate points, need 4)" below 4 points - exactly 302b table row 10), scramble_pieces (frozen
  null recipe as registered); _doc builds the fitter:"ink" doc but RETURNS it, never writes it -
  the write/decision was 302c's and the lead dropped that, so no ink doc exists in the store and
  plan_fit.build's "how" string ("Fitted automatically by the batch..." for auto+score, lines
  300-306) never meets an ink doc: the old Re-read item is moot - do not "fix" the wording, the
  lead's own matcher docs carry it and the 306 audit accepted it. site_done._fit's
  covered-pictures rule and the 2/1/0 exit codes verified intact in the current code.
- **Box 2 MET.** docs/site_flow.md "The one-shot held-out measurement of the ink fit (task 302b)"
  carries the 21-row table (the 20 originals + the lead's 21st), corner errors reported verbatim
  (231-2204 m, mostly wrong - reported as they are), the fabrication column silent on every fit
  produced, and the registered statement that the method never sees the hand pairs. Checkpoint
  data/inkfit/heldout/results.json: 21 entries, 0 errors, one fixed at 2026-10-11T22:47:37.081160+00:00;
  entry fields: corner_error_m, drot_deg, scale_ratio, objective{fit,scramble,shifted}, null,
  confidence, gate{verdict,n,med,slope_o,io}, fabrication, seed, n_pieces, n_points, model
  "no-model", reruns 0. docs/matchfit.md section 2 carries the matcher's own table on the same 21
  (7/21 accepted at >=10 inliers, 0 wrong, worst centre 55 m).
- **Box 3 MET.** fit/matchfit.judge() is the method's self-decision: ELoFTR inliers>=10 and
  |rot|<=30 (lead pre-set on a few hand fits before the run, confirmed by the held-out sweep, kept);
  RoMa inlier fraction >=0.4 (read off the held-out + queue tables; docs/matchfit.md sections 7-8,
  "Adopted rule (line lead, 2026-10-12 ~01:00)"); both plus the spread guard (ratio>=0.1, sd>=20 px
  - the Aesica near-line case). Human-readable "not sure: ..." reasons. matchfit.run writes a
  document only when judge is silent, so an unsure fit never reaches the map; it stays in the
  owner's queue / review item with the reason (0.3-0.4 band: "stays in the queue with the candidate
  shown"). Second line of defence: site_done._sync_doc applies the spread guard instead of the
  ladder clause to fitter:"matcher" docs before any build.
- **Box 4: wiring MET, TEST HALF NOT MET.** site_done._fit calls matchfit.run first on every
  undocumented picture (review-item ones too) whenever matchfit.reachable(); confident fits become
  fitter:"matcher" docs; _sync handles them (spread guard, then build). But no test references
  matchfit at all (grep of tests/ is empty): tests/test_site_done.py runs the line on stonehenge
  (NOT a hand-fit site) with the matcher unreachable, so the matcher station is never exercised
  end to end, on any hand-fit site's files. -> subtask 302f.
- **Box 5 NOT MET.** No post-matcher Stonehenge run is recorded: the existing
  docs/site_flow/stonehenge.png (2026-10-11) predates the matcher and shows 13 candidates; the item
  now has 14. The only matcher-on-Stonehenge records are docs/matchfit.md section 8 ("Stonehenge
  earthworks 0.26" near-miss, below RoMa's 0.4 bar) and the "matcher fit" section of
  docs/site_flow.md (6 confident queue fits, Stonehenge not among them) - neither is the box's
  line-run + browser screenshot + plain statement. Current Stonehenge state (verified this
  session): 0 drawings, 1 overlay, 14 candidates in
  data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json (7 "line check: fabricated...",
  4 "median residual > 45", 2 feature-based, 1 "no model answer"), no matcher doc. The lead dropped
  302d because the INK method was dead; box 5 is method-agnostic and was never commented on by him
  - 302g is the box-5 run with the current matcher-first line, explicitly NOT a revival of the
  dropped ink work.
- **Notes hold.** All 40 lines of tests/golden/hand_fit_docs.sha256 verify in this checkout (sha256sum
  -c: 0 bad). The golden was re-keyed by 303 (1f562ca, 2026-10-11) to 21 hand docs + 19 site.json
  (by:hand stamped on the 21 incl. the lead's 21st; the original 20 hashes from fe84152 unchanged;
  shotwick excluded). The 21st doc on disk: by:hand, no auto flag, 3 pairs. The parent Notes' "20
  hand fits" world is superseded by this lead-approved re-key; the held-out truth set is now simply
  "the golden's platefit docs".

**LIVE DEFECT found this session (fixed in 302e):** fit/inkfit_heldout.py::golden_docs() hard-
asserts "expected the 20 golden hand-fit documents" but the golden now has 21 ->
`.venv/bin/python fit/inkfit_heldout.py table` (and any run/precheck) dies with SystemExit
"expected the 20 golden hand-fit documents, found 21" (verified by running, exit 1). The one-shot
run is SPENT (checkpoint + committed table) so this is a compatibility fix, not a re-measurement;
fit/matchfit_heldout.py imports inkfit_heldout as ih and will hit the same wall when it calls
the golden set (verify which functions - likely golden_docs/heldout-docs - and fix them too).
Fix: held-out set = the golden's platefit docs as-is (keep the byte-verify + no-auto-flag
precheck), drop/dedupe the now-redundant MAIDEN constant (it is in the golden since 1f562ca), and
`table` must still print the committed 21-row table verbatim from the checkpoint (the checkpoint's
21 docs == the current golden's 21 docs, so nothing in the table changes). Never re-run the
one-shot; never edit the docs/site_flow.md table.

**Environment (verified this session):** .venv is present and current (numpy 2.5.4 + scikit-image;
ALWAYS .venv/bin/python - system python3 has no numpy). ELoFTR matcher REACHABLE from this VM:
127.0.0.1:8091/health answers {model: zju-community/matchanything_eloftr, device: RTX 5060 Ti};
RoMa 127.0.0.1:8092 NOT reachable (connection refused) - so 302g's live run gets ELoFTR only
(matchfit.run degrades: use_roma=False; fit_row's RoMa second pass is skipped). Suite last known
(306d note, 2026-10-12/13, main): 10 failed / 130 passed / 1 skipped of 141 (test_fit_queue
placement dep:null + agent a's in-flight 307 work) - re-run and diff against the NEWEST driver
loop-start note before any claim.

**Next (driver order):** 302e (small) -> 302f (no-network e2e test of the matcher station on ONE
hand-fit site's files - recommend badbury-rings-q798831: best held-out matcher result, OS six-inch
sheet, 22 inliers, 58.6 m corner / 2.9 m centre; working phase records the ELoFTR responses per
(ground, window) to a committed fixture, the test serves them from a stub on an EPHEMERAL loopback
port - team rule: no fixed ports - and drives tools/site_done.py --root <tmp copy>) -> 302g
(Stonehenge: live ELoFTR run of the line, browser screenshot against the real sarsens via the 301
shot.mjs pattern, plain record in docs/site_flow.md - "the method placed nothing" is a fine answer).

**Re-read:** fit/matchfit_heldout.py - exactly which inkfit_heldout functions it calls (302e); the
stub-server pattern in tests/test_fit_queue.py (302f: how it runs a server in-process without a
fixed port - copy the idiom); tools/shot.mjs (302g).
