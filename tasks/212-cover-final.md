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

(2026-10-13, iteration 208, agent a - measurement session. Step (2) of the
iter-207 hand-over is DONE: the CORRECTION 4 measurement ran on the merged tree
and the box-6 risk did NOT materialize (both sites keep their open audit items -
full results in DECISIONS and below). NO test file written yet. The settled
iter-205 test design (full text: `git show 953d9ab:tasks/212-cover-final.md`) stays
in force, with the deltas in this note. cover.py is still DONE (863 lines,
55678e3).)

**Measured this session (merged tree, HEAD f62d50c, plans.json 1474 rows, 499 built):**

bethlehem / shotwick (the CORRECTION 4 question) - box 6 is safe, no action needed:
- bethlehem-q2523914: drawings 0, no docs; dep already map-only (tmk1850 1850) -
  its plan entries were pruned on this machine ~1h after the 306a audit a858f48
  (dep mtime Oct 12 22:38 CDT), drawings reset with them. Item: 22 candidates with
  306a audit whys + detail fields (coarse/ground/rot_deg/scale/note), no_picture
  None, resolved None -> OPEN, published in the 333-item review.json. Sync's prune
  leaves it byte-identical (prune only drops kind plan/view entries).
- shotwick-castle-q7502621: drawings 0, no docs; dep = map (six-inch-1st 1842) +
  the STALE plan entry of the doc deleted at 6841f07 (after iter 136) -
  plan_c_e6e5490609414bb9.webp + its _ink.webp still on disk (dep mtime Oct 11
  18:47, never re-pruned here). Item: 2 candidates (audit whys), OPEN, published.
  The sync's full prune drops the plan entry and BOTH webps; set_drawings ->
  drawings stays 0 (map is not a DRAWING kind, no plate).
- Both are in the 52-site "all rows already item candidates" population: site_done
  fit() re-fits only rows with NEITHER doc NOR item entry (docstring: a blind
  re-run would swap the audit entries whole) -> the loop leaves both item files
  BYTE-IDENTICAL. New PITFALLS entry filed on this (### tools/site_done.py,
  fit/review.py). Neither site is in the search set (both have rows) -> nopicture
  does not touch them.

Re-measured population (PRODUCT definitions; the iter-205 numbers were the 1168
pre-merge tree): nofit (drawings 0 and no doc) = 402 (94 sites have docs); search
set (no plans row) = 246 - ALL already carry the batch-era no_picture mark -> the
nopicture phase re-records all 246 with the exact searched string, 0 bare. (fudge/
highbank/hopeton look bare under a looser no-doc definition but are drawings-1
site.json-plate sites -> covered, outside _no_fit_sites.) with-row nofit = 156 =
52 all-rows-in-item (item untouched) + 1 partial overlap (upsert "no model answer"
only for the uncovered rows, in place) + 103 no item (fresh all-rows item).

CHOOSE on THIS tree (first 4 with-row nofit, sorted) = aardenburg-q955 (1 commons
row, no item), aesica-q4688554 (1 commons row, 1-cand item), aire-sur-la-lys-
q259903 (1 commons row, no item), alauna-q4708853 (5 rows, first = BOOK Allcroft
1908 n0438_1, 5-cand item). alesia (withrow[4]) and angel-mounds (withrow[7]) fell
out of the first 4 (211 gave aardenburg/aire their rows; the lead's Mac port
20277f3 added 11 matcher docs on 11 newly built sites).

**EXACT NEXT STEPS:**
(3) write tests/test_cover.py per the settled iter-205 design (`git show
    953d9ab:tasks/212-cover-final.md`) WITH these deltas:
    - assertion (iv) is now concrete: bethlehem's dep + item byte-identical after
      the sync; shotwick's dep 2->1 entries (plan entry + both webps gone), item
      byte-identical; both items on the served open list. Correction 4's open
      question is resolved: no nopicture re-record for either.
    - CHOOSE stays state-aware (first 4 with-row nofit, sorted), but the matcher
      fake assigns the pair recipes by POSITION: CHOOSE[0..2] well-spread
      non-pattern pairs on their first candidate row (doc built; source = that
      row's own src - here 3 commons; the shared-store book file of a book first
      row must be hard-linked in the tree), CHOOSE[3] (here alauna, book first row
      n0438_1) near-collinear -> doc written, then sent+deleted by the loop's
      per-site line check; item why = the line-check string recomputed from
      matchfit.spread at runtime.
    - Item end states per 201's derivation, computed from the live item: doc on an
      in-item row -> item resolved write-once, OFF the open list (here: aesica);
      doc on a not-in-item row or no item -> item, if any, stays open (here:
      aardenburg/aire have no item; alauna stays open with the line-check why on
      n0438_1). Everything else stays exactly as settled (state-aware fakes and
      assertions; own tree + own port-0 server; checkout-integrity hashes; box 6
      through the served page; report re-run byte-identical).
(4) run it alone (`.venv/bin/python -m pytest tests/test_cover.py -q`), fix what it
    exposes, then the full suite.
(5) the live run (network allowed) - unchanged from the iter-207 hand-over: fetch
    (1/s) -> search -> stage (ask_human ONLY if new files are found and clef
    127.0.0.1:18083 is still down: tunnel, or approve the LLM on 8081 as one-off
    classifier) -> loop (ELoFTR 8091; RoMa 8092 down, skipped by design; LLM 8081
    FORBIDDEN for placement) -> nopicture -> sync (check `ls data/raw/commons/big |
    wc -l` first) -> export (with the key-set diff rule) -> report (seed 20261012)
    -> commit everything -> `sha256sum -c tests/golden/hand_fit_docs.sha256` must
    pass 40/40 -> suite green. LIVE-RUN NOTE from this session: the 103 no-item
    with-row sites gain fresh all-rows "no model answer" items; the 1 partial site's
    uncovered rows are upserted in place; the 52 all-in-item sites' items (incl.
    bethlehem/shotwick's audit whys) stay byte-identical; all 246 search-set sites
    get the nopicture re-record with the exact searched string.
    EXPORT-PHASE RULE (still in force, from the iter-207 hand-over): a bare
    re-export on THIS machine yields 953d9ab's 1168-row plans.json byte-identical
    (numancia's c_0fa271e2444f7bfc in as a COMMONS row; the 307 rows that exist only
    in HEAD's 1474 - the 211 pictures, the Civitates/Merian full pages - have no
    local copies here yet). The fetch phase (1/s, resumable, skips rows that already
    have a copy) fills every missing kept row BEFORE the re-export, so the live
    export regains both sides; before the final re-export record the committed
    (id, sites[0]) key set and diff it after - any LOST key is a fetch failure to
    record as a data finding (never silently drop or re-add), expected growth is
    pure adds.

**My Depends on line stays "203a, 203b, 211"** (203a/211 done, 203b in flight - the
live run genuinely needs the batch done; 232-234 depend on ME, not the other way
round). If the driver's done-claim check counts the merge-induced reds (231's case
e, 232's two tests, 233's test, 234's test) against my claim, add them to the line.

---

### (superseded - iteration 207 hand-over; its step (1) is done: 231 corrected,
232/233/234 written, probe worktrees removed. Complete text in git:
`git show 2eef3ce:tasks/212-cover-final.md`; the iter-205 design text it pointed to
is `git show 953d9ab:tasks/212-cover-final.md`.)
