Status: open
Depends on: none
# 302f: The matcher station end to end - the line on one hand-fit site's files, no network
Touches: tests/

## Goal
Parent box 4: "Wired into tools/site_done.py's fit step; a test runs it end to end on one
hand-fit site's files (no network)". The wiring exists (site_done._fit calls matchfit.run
first on every undocumented picture when ELoFTR answers /health - tools/site_done.py:78-84;
_sync_doc applies the spread guard to fitter:"matcher" docs before any build), but it has
never been tested: `grep matchfit tests/` is empty, and tests/test_site_done.py runs the
line on stonehenge (not a hand-fit site) with the matcher unreachable. This task adds the
test: a throwaway copy of one hand-fit site's files in a tmp root, an in-process stub
serving recorded ELoFTR responses on an ephemeral loopback port (team rule: no fixed
ports), and `tools/site_done.py --root <tmp>` driven as a subprocess whose sockets die
loudly except to the stub.

The site is badbury-rings-q798831: a hand-fit site (the golden's 21 include
badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1) with exactly one candidate
picture (earthworkenglan01allcgoog_n0132_1, n0132.jpg) and no review item. All ground
images are local (web/data/sites/badbury-rings-q798831/: relief.jpg, six-inch-1st.webp,
os1inch.webp). Its frozen ELoFTR held-out run (data/matchfit/heldout/results.json, at
2026-10-12T02:58:37.021604+00:00) gave this plate the best matcher result of the 21:
six-inch-1st.webp x0.35, 61 matches, 22 inliers, rot 3.62 deg, 58.6 m corner / 2.9 m
centre - far past judge()'s bar (10 inliers, 30 deg). Because the site has ONE candidate,
a confident fit empties `uncovered`, so the vision batch never runs at all: the only
network the line touches in the test is the stub itself.

## Acceptance criteria
- [ ] Committed fixture from a one-off working-phase run against the live ELoFTR
      (127.0.0.1:8091; verified reachable at iteration 208): the raw /match responses for
      every (plan image, ground image, window) pair of badbury's fit_row, keyed by the
      sha256 of the exact PNG bytes matchfit.match sends (plus threshold 0.2 / max_side
      1024), under tests/fixtures/matchfit_station/ (new directory; the JSON carries a
      header recording run date, matcher model, and the frozen held-out numbers the
      replay must reproduce - badbury 22 inliers / 58.6 m on six-inch x0.35). If the live
      replay disagrees with the frozen checkpoint, record the discrepancy; regenerate
      only if the matcher's output is stably different.
- [ ] tests/test_matchfit_station.py (new file): starts the stub in-process on an
      ephemeral loopback port (conftest.py's server idiom, bind port 0), points the
      subprocess's MATCHER_URL at it and ROMA_URL at a dead ephemeral port (RoMa
      deterministically absent: matchfit.run's second pass skips), and runs
      tools/site_done.py --root <tmp> as a subprocess. The tmp root copies badbury's
      files (the site dir, the site's sites.json entry, the plans row, the golden
      document) with the document DELETED so the single candidate is uncovered.
- [ ] Subprocess socket guard (a variant of tests/test_fit_queue.py's GUARD): any
      connection attempt to anything other than the stub's loopback port fails loudly -
      that is the "no network" proof.
- [ ] Confident branch: the stub replays the recorded 22-inlier six-inch candidate (and
      the rest of badbury's recorded responses). The test asserts: site_done exits 0;
      the subprocess stdout carries the matcher's FIT (eloftr) line for n0132_1; the tmp
      root gained a document badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1.json
      with by:"agent", auto:true, fitter:"matcher" and its matcher block (model, inliers,
      matches, ground, window, rot_deg, spread); the line's sync built it into the tmp map
      (the spread guard passes on the recorded spread, so no refusal); exit code 0.
- [ ] Unsure branch (a fresh tmp copy, fixture variant with the best candidate under 10
      inliers): the test asserts: the subprocess stdout carries the matcher's
      "not sure: N consistent points (need 10)" line for that candidate; no document is
      written for it; the candidate appears in the tmp review item with a reason (the
      batch's own, e.g. "no model answer", from the socket-dead vision pass); no map
      overlay for it; exit code 0 - that is the parent's box-3 contract "unsure goes to
      the queue with the reason, never to the map", end to end.
- [ ] The real checkout stays byte-identical after the test (the tmp root is the only
      writer; git status clean), and the suite has no new reds against the newest driver
      loop-start note.
