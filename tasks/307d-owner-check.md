Status: done
# 307d: The owner's check - two queue sites end to end, then reverted
Depends on: 307c
Touches: tests/, docs/site_flow.md, docs/site_flow/

## Goal
The last box of 307: "Saving still writes "by": "hand" and runs the one-site line (305),
and the existing hand fits load and save unchanged. Checked in a real browser on two queue
sites the way the owner uses it (place, move, scale, save, see it on the map), then the
test fits reverted. Tests cover the queue place-check and the save path." The place-check
tests are 309's; this task proves the save path end to end in a real browser on two queue
sites and proves the shared store comes back byte-identical.

## Acceptance criteria
- [x] A new tests/ file runs the owner's flow in a real headless browser (Chrome, the
      305-part-3 pattern) against the real server on a private copy of the tree (the 305
      part-2 precedent: real data, no network, ephemeral port): on two queue sites (pick
      ones with a recorded bar scale and a site-size-only fallback, and different ground
      where possible - LiDAR relief vs aerial photograph) the test does what the owner
      does: open the queue, place the drawing (the on-map start), move it, scale it,
      save; then verifies the saved doc carries "by": "hand" and the one-site line ran
      (the overlay on the map in the site's depictions, the site square coloured, the
      review item resolved, the queue moved on), and after a page reload the fit loads
      back unchanged (same placement, same overlay).
- [x] The test fits are reverted before the test ends: the private tree is discarded, and
      the shared store in the repo is proven byte-identical to before the test (the golden
      hand-fit hash check tests/golden/hand_fit_docs.sha256 and test_fit_provenance stay
      green; web/data/fit_queue.json and the review exports untouched).
- [x] docs/site_flow.md: the verification section (what was checked, on which two sites,
      which way, and the screenshots), closing the parent's last box.

## Notes
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-13, iteration 251, agent a - ELEVENTH session. **TASK DONE: all three boxes ticked,
Status: done, committed.** Nothing more to do on this task; the parent 307's last box is closed
by it (docs section: "The owner's check: two queue sites end to end, then reverted (task 307d,
2026-10-13)" at the end of docs/site_flow.md, with the ten screenshots in docs/site_flow/).

What this session did (the tenth session's exact next steps, in order):
1. Re-ran the test IN SESSION before ticking (verify, not on faith):
   `.venv/bin/python -m pytest tests/test_owner_check.py -q` -> **2 passed in 71.30 s** on this
   exact tree (the driver committed the tenth session's uncommitted work as f516b1e; only driver
   bookkeeping since - no code/data change, no main merge). Also re-ran box 2's fast checks in
   session: `-k hand_fit` (the golden tests/golden/hand_fit_docs.sha256 checks) 2 passed;
   `tests/test_fit_provenance.py` 7 passed. Disk 61% / 30G free; ps showed no pytest/serve/chrom
   processes running (no concurrent agent-c run to race for the disk).
2. Added the two PITFALLS entries the tenth session earned: (a) under `tools/site_done.py,
   fit/review.py`: the one-site line prints its own HEADER `site <sid>: the one-site line
   (fit -> sync -> entry -> review)` (site_done.py:326) BEFORE its work, and the server worker
   prints TWO-SPACE-INDENTED reports (serve.py:251/255/257) - filter runlogs by the indented
   shape `  one-site line for `, never the bare phrase. (b) under "Agent tools and harness":
   in team mode each checkout has its OWN /tmp/loop-<checkout> TMPDIR (verified: mine
   /tmp/loop-ancient-works.a, agent c's /tmp/loop-ancient-works.c, no bare /tmp/loop-<project>)
   - the tenth hand-over's "/tmp/pytest-of-agent is SHARED by every agent" claim is CORRECTED
   there; /tmp trees are short-lived under two independent wipers anyway (a green run's own
   retention cleanup; the loop's /tmp/loop-* wildcard wipe at disk pressure) - dump evidence
   into the repo or read it in the session it was made.
3. Ticked all three acceptance boxes, set Status: done, committed. The test file, docs section
   and screenshots were already committed (f516b1e); this session's commit touches only the
   task file, DECISIONS.md and PITFALLS.md.

If the driver re-verifies: the full suite should be **159 passed / 1 skipped / 1 failed** - the
single failure is 235's pre-existing red tests/test_fit_queue.py::test_placement_gestures_and_
save_in_the_browser (documented in PITFALLS, in the driver's loop-start baseline; it clears
only with 307's merge, not with this task). No code, data or other-task files changed in any of
this task's eleven sessions.

Retained facts (for the parent's 999 goal check, if ever needed): picks A = [38] oswestry-
castle-q20713795 / earthworkenglan01allcgoog_n0119_1 (bar 0.1646 rot 0, Allcroft 1908 "Camp,
Old Oswestry, Salop"); B = [45] devil-s-dyke-q3307343 / n0662_1 (picture_size 0.7201, "SWEALD").
Both LiDAR (lidar null, EA credit); before {drawings 0, score 1.1 (t1), oldest 1842, overlays 1}
-> after {drawings 1, score 1.45 (t2), oldest 1842, overlays 2}; item resolved write-once; card
moves on (39 / 46); review.json 457 -> 456 -> 455; reload unchanged. Queue 241 at
2026-10-13T14:34:09.559141+00:00.
