Status: open
# 212: Cover - the last uncovered sites, the final sync, the report
Depends on: 203a, 203b, 211
Touches: fit/cover.py, data/db/platefits/ (the loop's matcher writes docs; the line check may delete a pattern doc; the sync may stamp by:agent into an unmarked auto doc), data/review/, web/data/review.json, data/commons/files.jsonl, data/commons/classified.jsonl, web/data/plans.json, web/data/sites.json, web/data/sites/, docs/batch.md, tests/test_cover.py

## Goal
The last pass of GOAL.md point 1 and its evidence for the human. For every built site
still without a fit (after the batch, 203a/203b, and the new pictures, 211): a targeted
picture search (the site's QID Commons category, P180 depictions, a title search) with the
search recorded; a found picture becomes a candidate through the normal loop (fitkit sheet ->
model fit -> fit -> gate); a site where nothing is found gets a review item marked "no picture found"
with exactly what was searched. Then the one and only page-facing sync: every fit
document (the 20 hand fits, the automatic ones, the human-saved ones) becomes its site's
overlay and its drawings count in web/data/sites.json, through the existing plan_fit
machinery; web/data/review.json becomes the current open list for the page's review
section (201). Finally docs/batch.md: the report the human reads - counts per outcome,
the seeded 20-sample of automatically accepted fits (a page URL each) for the 18/20
check, and the "no picture found" list.

## Acceptance criteria
- [ ] fit/cover.py runs the targeted search for every built site without a fit and without
      a candidate: the searches (categories, P180 queries, date) are recorded; a found
      picture is staged in the canonical files (files.jsonl + classified.jsonl, with the
      200 evidence field) and its row added to web/data/plans.json; the site goes through
      the normal loop (fitkit sheet -> model fit -> fit -> gate) and ends with an automatic document or a
      review item.
- [ ] A site with nothing found gets a review item marked "no picture found" with exactly
      what was searched (assumption 3 of PLAN.md); the human can drop the site or name a
      source from the item.
- [ ] The page-facing sync (the only task that runs it): every fit document produces its
      site's overlay (web/data/sites/<id>/depictions.json) and its drawings count in
      web/data/sites.json, through the existing plan_fit machinery; the 25 hand fits'
      overlays are unchanged (000's golden test still passes).
- [ ] web/data/review.json is the current open list for the page's review section:
      resolved items out, new items in; the served page shows the right count (checked
      through the page, not the file).
- [ ] docs/batch.md: the final report - counts per outcome (fit: hand / automatic /
      human-saved; review item; no picture found), the seeded 20-sample of automatically
      accepted fits (page URL each, fixed and reproducible from the recorded seed) for
      the human's 18/20 check, and the "no picture found" list with what was searched per
      site.
- [ ] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item (GOAL.md point 1, in full); the
      25 hand fits are intact (the golden test); the sample in docs/batch.md is
      reproducible from the recorded seed.

## Notes
- This task runs last on purpose: it alone writes web/data/review.json, the per-site
  depictions and the drawings counts, so no other in-flight task can collide with it.
- The sync runs plan_fit.main() by hand (the way serve.py's after_write does it in
  production); the tests never start the server's platefits path for this - they check
  the served result.
- The 20-sample must stay a fixed record: the human's 18/20 check (GOAL.md point 3) is
  the project's acceptance, and a moving sample would make it unrepeatable.

## Hand-over

(2026-10-13, iteration 207, agent a - task-file session. Step (1) of the iter-206
hand-over is DONE: 231 corrected, 232/233/234 written, /tmp/awmain+/tmp/awhead
worktrees removed, the export_plans machine-dependence filed in PITFALLS
(### tools/export_plans.py), DECISIONS updated. No 212 code work this session;
cover.py is still DONE (863 lines, 55678e3). The iter-205 test design below stays
in force; its full text is in git: `git show 953d9ab:tasks/212-cover-final.md`.)

**New task files (all Status: open):**
- 231 (corrected): covers ONLY test_commons_yeared_title_drops_the_repeated_year -
  re-point the year-once pin off the deleted bethlehem doc to a surviving batch doc
  with a year-titled title (40 candidates measured; the Mackenzie (1897) set,
  "York Castle in 1820", ...). Chosen AFTER 306c-f settle. Does NOT touch case b.
- 232: re-pin the shared Stonehenge snapshot in test_site_done + fit_provenance b
  to the POST-212 live state (14th plans row c_61b86efb4511e099 came in with the 211
  pictures, main f970500, not a batch run; the live loop may place a matcher doc,
  which would resolve the item - re-derive mechanically, recipe in the file).
  Depends on 212, 231.
- 233 (RE-SPECED - the iter-206 note was wrong): the numancia exclusion is
  MACHINE-DEPENDENT (export_plans includes a row only where its local copy exists;
  data/raw is gitignored). The files/classified rows never changed; the local jpg
  is in this VM's shared store (210 staged it); the lead's Mac lacked it, so f970500
  dropped the row. It is a COMMONS row (book "Wikimedia Commons", c_0fa271e2444f7bfc
  = sha16 of the title) - NOT a books-index row; the memoriasdelareal009real index
  row is not involved (the earlier "book = the ia id" guess was wrong). After 212's
  fetch+re-export on this machine the row returns unchanged and the test should
  pass; 233 = verify + record (docstring/PITFALLS). Depends on 212.
- 234: change test_fit_queue_real's key to the generator's documented
  (view, -px, plan, name) - do NOT touch tools/fit_queue.py's sort (307bb's
  page-card pins depend on it); then regenerate web/data/fit_queue.json (committed
  at 229 entries, at 2026-10-13T04:09:15) after 212 + 306c-f settle the live
  inputs; byte-reproducibility check. Depends on 212, 306c-f.

**Measured this session (facts for the live run, all on the merged tree):**
- export_plans on THIS machine (in-memory probe, real file untouched and restored
  after - probe truncated it once, see DECISIONS) = 953d9ab's 1168-row plans.json
  BYTE-IDENTICAL: numancia in, all 307 of HEAD's 1474-only rows (the 211 pictures,
  the Civitates/Merian full pages) ABSENT - they have no local copies on this
  machine yet. 212's fetch phase (1/s pace, resumable, skips rows that already have
  a copy) fetches every missing kept row BEFORE the re-export, so the live run's
  export regains both sides; LIVE-RUN RULE: before the final re-export record the
  committed (id, sites[0]) key set, after the re-export diff it - any lost key is a
  fetch failure to record as a data finding (never silently drop or re-add).
- The stonehenge published review.json entry matches its 13-candidate item file
  (order, set and bytes) - the only currently-failing precondition in both
  pinned tests is the 13-row plans check (14 rows).
- worktrees /tmp/awmain, /tmp/awhead removed (agent c's /tmp/aw306cab left alone).

**EXACT NEXT STEPS (unchanged from iter 205/206, step 1 now done):**
(2) run the one blocked measurement from CORRECTION 4 (bethlehem/shotwick coverage
after the sync's prune - it decides a box-6 edge case; command in the superseded
iter-205 text below);
(3) write tests/test_cover.py per the settled design in that text (corrections 1-5
incorporated - (b)/(c) seeds on fake sites, (a) on the first nofit-no-row site,
fakes as pure functions of the tree's live state, own tree + own port-0 server,
checkout-integrity hashes, box 6 through the served page, report re-run
byte-identical);
(4) run it alone (`.venv/bin/python -m pytest tests/test_cover.py -q`), fix what it
exposes, then the full suite;
(5) the live run (network allowed): fetch (1/s) -> search -> stage (ask_human ONLY
if new files are found and clef 127.0.0.1:18083 is still down: tunnel, or approve
the LLM on 8081 as one-off classifier) -> loop (ELoFTR 8091; RoMa 8092 down,
skipped by design; LLM 8081 FORBIDDEN for placement) -> nopicture -> sync (check
`ls data/raw/commons/big | wc -l` first) -> export (with the key-set diff rule
above) -> report (seed 20261012) -> commit everything -> `sha256sum -c
tests/golden/hand_fit_docs.sha256` must pass 40/40 -> suite green.

**My Depends on line stays "203a, 203b, 211"** (203a/211 done, 203b in flight - the
live run genuinely needs the batch done; 232-234 depend on ME, not the other way
round). If the driver's done-claim check counts the merge-induced reds (231's case
e, 232's two tests, 233's test, 234's test) against my claim, add them to the line.

---

### (superseded - iteration 205 hand-over: the full test design and corrections 1-5;
complete text also in git: `git show 953d9ab:tasks/212-cover-final.md`)
