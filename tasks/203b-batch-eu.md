Status: open
# 203b: The batch, rest of world - every non-US built site
Depends on: 203a
Touches: fit/batch_eu.py, data/db/platefits/, data/review/, docs/batch_eu.md, tests/test_batch_eu.py

## Goal
The same model-fitting loop as 203a (fitkit sheet -> model -> solver -> gate), for every other built
site: all sites with region != "US" plus the 6 sites with no region field at all (294 of 384) - none
of them may be skipped. The shared loop is imported from fit/batch_us.py (203a's module); this task
writes only the non-US documents and items. 203a's US output is already merged into this branch when
the task starts.

## Acceptance criteria
- [ ] fit/batch_eu.py imports the loop from fit/batch_us.py and runs it over every non-US built
      site; every such site ends with at least one automatic platefit document (score
      recorded) or an open review item - or an existing hand fit.
- [ ] The union of the two batch outputs covers every built site exactly once: a check against
      sites.json over the documents and items both tasks wrote - no site in both, none missing
      (the 6 region-less sites must appear in the EU list, not be dropped).
- [ ] docs/batch_eu.md in the same format as docs/batch_us.md: counts (automatic fit / review
      item / already hand-fitted / no picture found), the recorded seed, and the seeded sample
      of automatically accepted fits (20 where there are at least 20, a page URL each).
- [ ] After the run the hand-fit documents are still byte-identical to
      tests/golden/hand_fit_docs.sha256; the test (no network, port 0) runs the loop on a
      fixed sample of non-US sites with in-repo ground and asserts the invariants.

## Notes
- Do not re-implement the loop in fit/batch_eu.py: import it. If a change to the loop itself
  is genuinely needed, request it in a DECISIONS entry to the owner of fit/batch_us.py rather
  than copying it (one place for each piece of knowledge).
- The 20-sample lists of the two reports are separate (one per region); 212 picks the final
  combined 20-sample for the human's 18/20 check from the whole set.

## Hand-over
Session 2 (2026-10-11, iteration 49). State: tests/test_batch_eu.py WRITTEN and GREEN;
the working run (session 3) is the next step. Nothing of this session is committed yet:
the harness saves tests/test_batch_eu.py (new) and the PITFALLS.md edit; session 1's
fit/batch_eu.py is committed (2fd1138).

Test suite as last run: `.venv/bin/python -m pytest -q` = 45 passed, 1 skipped
(47 s). The 1 skip is test_union_full_coverage_live, correctly skip-gated
docs/batch_eu.md does not exist yet). All 8 new tests of tests/test_batch_eu.py
pass. The other 38 pre-existing tests are unchanged and green.

What session 2 did:
- Wrote tests/test_batch_eu.py (8 tests, self-contained helpers - deliberately NOT
  importing test_batch_us's; the two files change for different reasons; see the
  DECISIONS entry). Design: sample = the 6 region-less sites (newark 21 candidates,
  forthill 4, marietta 4, fudge/highbank/hopeton 0 + old-style fit) + bibracte-q650053
  (no-picture re-upsert of its 201-era item) + avebury-q661855 / old-sarum-q782719
  (pre-docs skipped, fresh commons rows get short 2-pair answers -> could-not-fit
  item entries). Tests: sample run under the real gate (29 auto docs expected, 0
  items from the region-less three, no items for the three no-candidate hand-fitted,
  bibracte re-stamped with the batch's searched wording); hand-fit skip +
  could-not-fit; stub accept/reject gates on a COMPUTED EU site (today
  alauna-q4708853) monkeypatching batch_us.gate_placement; golden invariance (39
  golden + the 6 old-style site.json pre/post, only new files = auto docs / sample
  items); report (byte-identical twice, shared SEED 20261010, the EXACT seeded sample
  list re-computed, page URL per doc, union section == union_section(union_check(tree))
  appended at the end, default path pinned to docs/batch_eu.md, never batch_us.md);
  union check (weaker form in the temp tree); full live union test (skip-gated).
- CORRECTION to session 1's DECISIONS note "Avebury's duplicate-id Larned row no
  longer exists (one c_ffb3daac218b481f row now)": WRONG. Two rows still share that
  id - one per site (avebury-q661855 and stonehenge-q39671) with DIFFERENT per-site
  urls; c_984782b9e35e8ded does the same (mayburgh-henge + king-arthur-s-round-table).
  The first test run tripped on it (a stonehenge url asserted against the avebury
  entry). Fix: per-site row lookup _row_for(sid, plan) from the site's own candidates
  (never a global id dict). PITFALLS.md's plans.json entry was updated accordingly
  (that edit is uncommitted - the harness saves it).

NEXT STEP (session 3, the working phase): `.venv/bin/python fit/batch_eu.py --working`
over all 294 (AI-box tunnel needed as in 203a's run; network only for fetching book
page images, commons pictures and Esri aerials for the ~17 lidar:false EU sites -
they land in the gitignored cache, never in git). Before the run: capture sha256 of
the 6 old-style site.json (data/sites/{newark,forthill,marietta,fudge,highbank,hopeton}/
site.json) and sha256sum -c tests/golden/hand_fit_docs.sha256 (must be 39/39 before).
Afterwards: sha256sum -c the golden again (39/39), hash-compare the 6 old-style
site.json, read docs/batch_eu.md (union section should read 384 built sites, 0 in
both, and - since 203a's US output is already in this branch - 0 missing if the EU
run covered everything; pre-EU state was 112 covered / 272 missing / 0 anomalies),
commit docs + items + report, run the full suite (test_union_full_coverage_live
should now UN-skip and pass), tick the four boxes in order (loop runs / union /
report / golden+test), file the done claim.

For 212 (write into its hand-over when done): shared SEED 20261010; the EU sample in
docs/batch_eu.md is reproducible from it and disjoint from the US list (212 picks the
final combined 20 from the union with its own seed); the no-picture item list (175
sites incl. bibracte's 201-era item) is its search-harder list; 212 must re-export
web/data/review.json (the batch never writes it).

Re-read: tests/test_batch_eu.py:test_union_full_coverage_live - the skip-gate
condition (the report's "Sites run" must equal the live EU partition size, 294 today)
and the full assertion (0 missing / 0 in both / 0 orphans / no bad doc names) - after
the working run it must un-skip and pass; fit/batch_eu.py:write_report - the default
path pin and the union section appended after batch_us.write_report.
