Status: done
# 203: The batch - every built site gets a fit or a ready review item
Depends on: 001, 200, 201, 202
Touches: tests/test_batch.py

## Goal
The heart of GOAL.md points 1 and 2. For every built site in web/data/sites.json: take its candidate
pictures (web/data/plans.json, evidence-checked by 200), and have the local model fit each one the way
the 25 hand fits were made — fitkit sheet, grid labels, at least four matched-feature pairs, 202's
scale/north/centre seed as the starting point (never the fit). The fitted pairs go through the existing
plan_fit similarity solver and then the gate (001): accepted -> an automatic platefit document with the
gate's score; refused or could-not-fit -> a review item (201's format) the human finishes by dragging in
under a minute. The 25 hand fits are never touched. Split into 203a (US built sites) and 203b (all the
rest); this parent comes back when both are done and verifies the whole original site set.

## Acceptance criteria
- [x] (203a) every built site with region "US" (90 of 384) has run through the loop: at least one
      automatic platefit document (the gate's score recorded in the document) in
      data/db/platefits/ or an open review item in data/review/ - or an existing hand fit (that
      site stays exactly as it is).
- [x] (203b) the same for every other built site: region != "US" plus the 6 sites with no region
      field at all (they must not be skipped).
- [x] (203a) the hand fits are byte-identical after the batch: tests/golden/hand_fit_docs.sha256
      (created before the first batch write) records all 20 pre-batch platefit documents, and the
      test asserts every one of them is still byte-identical and the batch added files, none
      rewritten.
- [x] (203a) docs/batch_us.md: how many US sites got an automatic fit / a review item / were
      already hand-fitted / had no candidate, the recorded seed, and the seeded sample list of
      automatically accepted fits (20 where there are at least 20, a page URL each) for the
      human's 18/20 check.
- [x] (203b) the same report as docs/batch_eu.md; and the two reports agree on the union: every
      built site is covered exactly once, no site in both.
- [x] (203, on return) the final coverage check over the original site set: every built site that
      existed before the source growth (204-210) has a fit (hand or automatic) or an open review
      item - tests/test_batch.py. Coverage of the new sites built by 211 is asserted by 212, not
      here (212 runs after the parent and re-covers the new material itself).

## Notes
- The shared loop (candidates -> fitkit sheet -> model fit -> fit -> gate -> document or item) lives
  in fit/batch_us.py (203a's); 203b imports it and does not rewrite it.
- A site whose pictures all fail the gate gets its review item anyway: GOAL.md wants a fit OR a
  ready item, and the human's drag is the authority. A site with no candidate at all gets a
  review item marked "no picture found" (212 later searches harder).
- The automatic documents use the page's existing platefit format (site, plan, pairs, crop,
  size) plus a recorded score and an "auto" mark, so the page's fit tool and 212's sync treat
  them exactly like a human save minus the authority (a human save bypasses the gate, 001's
  scope).
- Tests are hermetic: they run the loop on a fixed sample of sites that have in-repo ground
  (the tracked hand-fit sites), never the full 90/294 (most have no ground in this checkout and
  the tests have no network); the full runs are working-phase commands recorded in the reports.

## Hand-over

(2026-10-13, iteration 206, agent c - DONE, all six boxes ticked, done claim filed this session.
Both subtasks were accepted before I got the parent back; I re-verified their boxes live and
wrote the parent's own box 6.)

What this session did (one step, committed):
- Wrote tests/test_batch.py (the box-6 final coverage check over the original 384-site set):
  - the original set is reconstructed from the two committed batch reports' "Per candidate"
    tables (90 US + 294 EU, disjoint, each matching its "Sites run" line, union = 384 = the
    pre-growth population); test 1 also asserts the 6 region-less originals sit in the EU table
    and no original site was lost from sites.json by the later merges (211 grew the live set to
    499; all 384 still present);
  - test 2: every original site still has a fit (any platefits doc naming it, auto or hand,
    or the old-style data/sites/<id>/site.json plate fit) OR an OPEN review item - "open" is
    201's derivation (fit/review.resolved_doc is None), NOT the recorded `resolved` field;
    plus a page check: every site covered by an open item only must appear in
    web/data/review.json (what the human sees in the Review section).
- The trap this session hit (now in PITFALLS, tools/site_done.py, fit/review.py section): a
  first pass that checked the raw `resolved` field flagged aesica-q4688554 and
  alligator-effigy-mound-q4732645 as uncovered - both are 203a batch auto docs that were later
  rejected on sight and DELETED (b22a2d2's rule: a recorded resolution counts only while its
  doc exists), so their items went back to the queue and 201 counts them open again. Both are
  in the exported open list (page = derived: 457/457 equal). Using resolved_doc, live coverage
  of the original 384 = 41 with a doc, 6 old-style hand fit, 348 with an open item, 0 missing.
- Re-verified boxes 1-5 against the live tree: golden tests/golden/hand_fit_docs.sha256 =
  40/40 OK (21 hand docs incl. maiden's DPLA plan + 19 site.json); batch_us.md 9 auto / 8 item /
  2 hand / 71 no-picture = 90, seed 20261010, sample = all 16 auto docs with page URLs (16 < 20);
  batch_eu.md 54/47/18/175 = 294, same seed, seeded 20-sample (of 94) with page URLs, run-time
  union section clean (384 covered, 0 missing, 0 in both, 130 docs, 340 items, 6 hand, no
  anomalies).

Suite (full, this branch, .venv/bin/python -m pytest -q -p no:cacheprovider):
1 failed, 157 passed, 1 skipped (319 s). The 1 failed = agent a's in-flight 307 placement test
(test_fit_queue.py::test_placement_gestures_and_save_in_the_browser, "seed: the gestures own the
mouse" - documented red since iter 161, "signature unchanged" per the 207a merge note; 307d is
agent a's current work - not mine to fix). The 1 skipped = test_batch_eu.test_union_full_
coverage_live, its by-design skip gate (report "Sites run: 294" vs live EU partition 409 after
211's growth; 212 re-covers the growth). My two new tests pass in 0.2 s.

Nothing pending. If this task is ever reopened (e.g. a batch re-run regenerates the reports, or
the original set legitimately changes), the first thing to look at is test_original_set_is_the_
reports_union: it pins 384 and the two reports' tables as the record of the pre-growth
population, so an intended change updates the reports first, then this test.
