Status: done
# 207a: Horsley, Britannia Romana (1732)
Depends on: 200
Touches: fit/src_roman_horsley.py, data/books/triage/, data/books/lists/, data/raw/books/britanniaromanao00hors/

## Goal
Subtask of 207 (the parent's Hand-over has the full mechanics): index John Horsley's
*Britannia Romana* (1732) with the existing book machinery and stage its site-plan rows tied
to Roman sites. Chosen IA copy: `britanniaromanao00hors` (Google Books scan, 936 leaves,
median 2237x3861 px, hOCR page text + djvu.txt present). Alternatives (only if specific pages
of the Google copy are unreadable): `bim_eighteenth-century_britannia-romana-or-the_horsley-john_1732`
(British Museum, 831 leaves, median 7984x13809 px) and the `..._0` copy (827 leaves,
8328x14257 px) - much larger images.
Note: this book's ~121 engraved plates are mostly Roman inscriptions and sculptures (list
kind "o"); its true site plans are the few maps (kind "s"). Stage the site plans; the
inscription plates are indexed in the list mapping (each names the site where the stone was
found) but are not staged as picture rows.

## Acceptance criteria
- [x] The book is fetched from the Internet Archive (data/raw/books/britanniaromanao00hors/)
      and triaged with the existing machinery, per-book artifacts only
      (triage/britanniaromanao00hors.*.jsonl, lists/britanniaromanao00hors.json,
      lists/britanniaromanao00hors.map.json); the shared data/books/index.jsonl and
      validation.json are NOT written by this subtask.
      (done 212-220: fetch 936, A 936/0err, B 17/0err, lists the 22-entry version)
- The remaining boxes were MOVED to the split parts (2026-10-14, iteration 221, driver
  instruction: this task kept what is already built and committed; the parts depend on this
  task, then on each other in order 807 -> 808 -> 809; together they cover these boxes):
  - the list transcription/mapped to leaves + the stage-A/B recall recorded in the Horsley
    section of docs/lead_roman.md -> tasks/807 (the list corrected to 24 entries: the 219
    version's 22 + n0114/n0185, proven genuine site plans at 220)
  - the staged rows (files_roman/classified_roman/extras_roman, rows tagged with this book,
    200 evidence field, 1732) -> tasks/808
  - the fit/evidence.py check passing offline on every staged row + at least 90% of the
    verified site-plan pages staged, or each missing one accounted for in the lead doc ->
    808 + 809
  - the no-network test (the staged files join, the evidence check passes, a golden sample
    of rows) -> tasks/809

## Notes
- The LLM replicas serve on 127.0.0.1:8080-8082 (model qwen3.8-27b); since 215 re-pointed
  pipeline/books.py's LLM_PORTS to 8080,8081,8082,18080,18081, no in-process LLM_URLS patch is
  needed. (Superseded for the remaining work: every leg left for this book is offline - the
  triage stages that needed the replicas are done; the parts 807/808/809 use no LLM.)
- The catalog already holds the major British Roman forts with QIDs (305 roman_fort rows:
  206 England, 54 Wales, 22 Netherlands, 17 France, plus 6 no-QID extras: vindolanda and the
  four Antonine Wall camps, aventicum). (Now carried per site in 808's Notes.)
- The LLM triage of 936 pages was the long pole: run it as a resumable background job (the
  stage jsonl is append-only and skips done pages; see the "long background data jobs"
  PITFALLS entry). (Done: A 936/0err, B 17/0err - no long pole remains.)

## Hand-over
(2026-10-13, iteration 120, agent c - DONE, 3rd done-filing. Session hit the context limit
while writing memory; Goal/Acceptance/Notes above are final, everything below is the state
snapshot. All measurements were COMPLETED before the limit; nothing is left half-run.)

**Where I am.** The driver's two rejections (464a2c1, 2a0b228) both named
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser in its 3c91518-era
form (the loop-start red d14577e). Since those rejections main gained three lead ports -
d286196 (GOAL point 2: image-matcher-only placement), bba5961 (owner's Mac 9680a17: fit
tool rework, e2e-only fit tests parts 4-5, notthis hook, fit_queue drops dropped) and
c72706b (307d end-to-end-only; Fort Ancient joins the hand-fit golden) - NOT yet merged
here (merge-base still 3c91518); the driver's done-verification merges all of main first,
so it will run bba5961's REWRITTEN test, which no longer fails.

**Tests (last runs, in-checkout; backups /tmp/ab207a_c120; tree restored byte-clean).**
- A (branch as-is, pre-port test): FAIL 50.15 s - seed-check signature + 404s on
  GET /tiles/relief/12/1121/1559.webp (same pick as 222/d14577e).
- B (my 207a files at main's state: 215-era module, no britanniaromanao00hors lists/triage):
  FAIL 52.45 s, byte-identical signature -> the red is NOT my combination (the 222 A/B
  conclusion re-confirmed on the current tree).
- C (verification-tree preview: all 30 files main changed since 3c91518 swapped in from
  main; my branch touches none of them, so the driver's merge is clean): the rewritten test
  PASSES 77.65 s; FULL suite (.venv, tests/ --ignore=tests/test_gate.py
  -p no:cacheprovider) = 158 passed / 1 skipped / 0 failed, 430 s. The named red no longer
  exists on the tree the driver will verify; the 3rd filing rests on that measurement, not
  a blind retry.

**Hypothesis.** The driver's re-check passes (green on the merged tree). If a 4th rejection
comes, it will name a NEW tree (the lead ports keep moving main under the branches) - then
follow the 222 plan: ask_human to the lead with the 306c/306d precedent (their 2026-10-13
acceptance of the identical red, 12b2274) + this session's A/B and full-suite evidence.
No ask is filed now: the 222 trigger (the same named red still failing) does not hold.

**GOAL point 2 (d286196; the lead's message this iteration).** The image matcher
(fit/matchfit.py: RoMa + ELoFTR) is the ONLY automatic placement; the local Qwen models
never place a drawing and never write point pairs; the batch_us/batch_eu model-fitting
passes are retired; automatic fitting runs on LiDAR sites only. No impact on 207a's
remaining work: 807/808/809 (blocked by the owner's stop on 207, 06c1aa8) are offline book
staging - stage pictures, never placement (the same shape the lead's message described for
236b, "stage pictures only").

**Exact next steps (fresh agent).**
1. Check whether the driver accepted or rejected the 3rd filing: `git log --oneline -15`
   for [driver] commits naming 207a, the Status line of this file, and this task's newest
   notes in DECISIONS.md / PROGRESS.md. If ACCEPTED: 207a is fully closed (box 1 committed;
   boxes 2-5 live in the blocked 807/808/809 - no further 207a work until the owner lifts
   the 207 stop). If REOPENED: go to step 2.
2. If rejected: read the driver's DECISIONS note (it names the failing test(s)). Run the
   named test(s) on the current tree; if one is red, A/B my 207a files in/out (idiom in
   PITFALLS "A/B-testing a change against a pristine tree"; my files = fit/src_roman_
horsley.py + data/books/lists|triage/britanniaromanao00hors.*) - if the red survives
  without my files it is not mine -> ask_human per above (3rd failed attempt -> ask + set
   this task Status: blocked).
3. The 222 hand-over's full "Built and committed" inventory is recoverable with
   `git show 89de0b1:tasks/207a-horsley.md`; all reasoning is in the DECISIONS entries
   "207a 215/218/220(inside 221)/221/222/120" and the 207 parent's hand-over; the 807/808/
   809 task files + tasks/prep/807.md carry the mechanics of the remaining (blocked) work.
