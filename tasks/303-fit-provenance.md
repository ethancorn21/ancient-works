Status: done
# 303: Every fit says who placed it - no agent fit passes as a hand fit
Depends on: none
Touches: data/db/platefits/, pipeline/plan_fit.py, tools/site_done.py, tests/test_fit_provenance.py, docs/site_flow.md, fit/batch_us.py, tests/golden/hand_fit_docs.sha256, tests/golden/src_mackenzie_sample.json, server/serve.py, web/data/sites.json, web/data/review.json, data/review/

## Goal
The line's fabrication check (301) looks only at documents marked `"auto": true`; a document without the mark is
treated as the owner's hand fit and goes straight to the map. 206 wrote
data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json with 4 pairs placed by an agent session
(round page pixels: 405,25 / 827,570 / 620,835 ...) and no mark. The owner's hand fits are listed in
tests/golden/hand_fit_docs.sha256 (20), plus Maiden Castle's DPLA plan placed on the Mac page 2026-10-11 (main cd104ca).

## Acceptance criteria
- [x] Every platefit document carries who placed it: `"by": "hand"` (the page's save, the owner) or `"by": "agent"`
      (anything a script or a session wrote). The page's save path (server/serve.py -> plan_fit) writes "hand"; every
      agent/script path writes "agent". Existing documents: the 21 hand fits get "hand"; every other one gets "agent".
- [x] The line treats a document without "by": "hand" as automatic: the fabrication check and everything else that
      applies to automatic fits applies to it. Shotwick's 206 fit goes through that check, and the result (map or
      review queue, with the reason) is recorded in docs/site_flow.md.
- [x] tests/test_fit_provenance.py: every document in data/db/platefits/ has "by"; the hand ones match the golden list
      plus Maiden Castle; a document without "by" is refused by the line.

## Notes
- Do not change the pairs of any hand fit, and do not touch fit/inkfit.py or the 302 tasks (agent c's job).

## Hand-over

(done 2026-10-11, iteration 98, agent a - all boxes ticked, task complete; nothing pending)

**Step 5 (this session), the live run, verified:** `.venv/bin/python tools/site_done.py
shotwick-castle-q7502621` in this checkout, exit 0, exactly as predicted: who=agent (by present,
no auto, no score -> no stamp); the fabrication check ran on the 4 stored pairs and did not
fire (nearest margins: lattice u max/med 1.744 vs <=1.3, v 3.759; 1D max run 1 vs 3; grid-round
4/8 = 0.5 vs 0.9); the big Commons jpg downloaded once (paced, cached in data/raw/commons/big/);
`sync ...: synced to the map (plan_c_e6e5490609414bb9.webp, 4 pairs)` with residuals
14.2/2.0/17.5/19.4 m (0.2289 m/px, rot -0.2 deg); `entry ... drawings 0 -> 1`; the site's new
review item (its one plans.json candidate, the Allcroft 1908 "EARTHWORKS" plate, no model
answer) went to the queue open: page 339 -> 340 open of 341 items. A second run is a no-op
(`skipped: overlay already current`, `drawings 1 -> 1`, item and depictions byte-identical).
The outcome (map, with the reason and the nearest margins) is recorded in docs/site_flow.md,
section "Shotwick Castle: the first agent-placed fit through the line (task 303, 2026-10-11)".
Tracked-file effects, all in Touches (web/data/review.json + data/review/ were added to
Touches for the run): web/data/sites.json (drawings 0 -> 1), web/data/review.json (the new
shotwick item on the page), the new item file data/review/shotwick-castle-q7502621.
earthworkenglan01allcgoog_n0575_1.json. The platefit document itself is byte-unchanged.
Full suite after the run: 68 passed, 1 skipped, 0 failed (the loop-start test_gate red went
green; no new reds).

**Follow-up filed, not built here (a human may drop it):** tasks/219 - the commons source
line's doubled year ("... (1897) (1897), Wikimedia Commons: ...": the title's year and the
document's label are the same fact). Depends on 302c (both touch pipeline/plan_fit.py);
shotwick's built depictions.json is gitignored, so the fix is a string in build() plus a
one-off re-bake of that entry's source field.

**If this task ever reopens:** the 303 tests pin the repo's 21-hand set and the stonehenge
13-candidate item; extend them on purpose (re-key the golden the way iter 93 did). The 201
contract still hides a refused doc's candidate from the page's Review tab (the refusal is
write-once-resolved); that is a 201 product decision, not 303's.
