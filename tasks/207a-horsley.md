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
(2026-10-13, iteration 121, agent c - DONE re-filed. The driver's 129af49 note was NOT a
test rejection: "Accepted, but it cannot go into main yet: your branch conflicts with main
(the other agent's finished work) in: docs/site_flow/307d_{A_1-card, A_2-placed, A_3-
gestured, B_2-placed, B_3-gestured}.png. Run `git merge main`, resolve each conflict keeping
both sides' intent, run the tests, commit, then set the task done again." All of that is
done this session: merge committed 4cc34aa, suite green on the real verification tree,
Status: done.)

**The conflict and its resolution (4cc34aa).** Both sides' last changes to the five PNGs
descend from f516b1e: main's are 9c8a46a (307d done, agent a) + c72706b (lead port of the
owner's Mac work: 307d e2e-only; Fort Ancient joins the hand-fit golden) - the finished
307d test captures; our side's are the [driver] snapshot commits 464a2c1/d14577e - byte-
different re-encodings of the same test-generated docs (the 3c91518-era suite regenerates
all 10 docs/site_flow/307d_*.png on every run; my 207a work never wrote them). "Keeping
both sides' intent" = main's bytes for all 10: the 5 conflicted taken --theirs, the other
5 auto-merged to main's already (my branch had only re-encoded the 5 the driver's runs
touched). My side's contribution was a test-run side effect with no intent of its own;
main's is the finished work. Keeping the branch byte-identical to main on these files
makes the driver's later merge-into-main conflict-free on them (both sides identical
merges cleanly); the fresh captures my green run left in the working tree (re-encode
jitter only) were restored away before the merge commit. No test pins their bytes:
test_owner_check overwrites all 10 on every run by design (not part of its write-surface
byte-identity check); the rewritten test_fit_queue only reads them.

**Tests (this session, in-checkout, the REAL merged tree - not the 120 preview).** Full
suite `.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider`
after the merge: 158 passed / 1 skipped / 0 failed, 432.40 s - identical shape to
iteration 120's C preview (158/1, 430 s), now measured on the actual merge: bba5961's
rewritten test_fit_queue (e2e-only) green, c72706b's test_owner_check (2 e2e runs) green,
the Fort Ancient hand-fit golden (tests/golden/hand_fit_docs.sha256) green. The driver's
loop-start red note (the 3c91518-era test_placement_gestures_and_save_in_the_browser,
1 failed / 159 passed, d14577e) names a test that no longer exists on this tree -
bba5961 replaced it.

**State.** 207a's own work (box 1: fetch + triage A 936/0err + B 17/0err + the 22-entry
list; full inventory recoverable via `git show 89de0b1:tasks/207a-horsley.md`) stands
committed; boxes 2-5 live in the blocked 807/808/809 (owner's stop on 207, 06c1aa8) - no
further 207a work until the owner lifts it. Merge-base with main is now c72706b (main's
tip): my branch adds only my own files - 207a (fit/src_roman_horsley.py,
data/books/lists|triage/britanniaromanao00hors.*), 207b in-flight (fit/src_roman_
maclauchlan.py, its triage, docs/lead_roman.md), 807-809 and 302f task files + fixtures,
plus the shared memory files - and the planning record my branch wrote (PLAN.md's 207-
split/207c-drop rows and Deviations entry, which main's 000 rework for the changed
GOAL.md does not touch; GOAL.md itself is identical to main's).

**If another driver note arrives.** A named red in the OLD test_placement_gestures
signature is stale (bba5961 cleared it - PITFALLS tests/test_fit_queue.py entry,
corrected this session): run the named test on the merged tree and answer with that
measurement. A NEW red or a new tree: the iteration-120 step-2 idiom - A/B my 207a files
in/out in-checkout (PITFALLS "A/B-testing a change against a pristine tree"; my files =
fit/src_roman_horsley.py + data/books/lists|triage/britanniaromanao00hors.*), then the
306c/306d precedent (12b2274, the lead accepted the identical red on A/B evidence) -
three failed attempts at the same blocker -> ask_human + Status: blocked per AGENTS.md.
