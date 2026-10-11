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
Session 1 (2026-10-11, iteration 49). State: fit/batch_eu.py built, verified, committed.

What exists now (all in the checkout):
- fit/batch_eu.py: eu_sites(root) (294 ids, region != "US", the 6 region-less included),
  run_eu(root, model) (thin wrapper over batch_us.run_sites), union_check(root) (box 2:
  partition from sites.json alone, per-site coverage from docs/items/old-style site.json
  fits, orphans + bad doc names, in_both), union_section (markdown appended to the report),
  write_report (batch_us's writer, title "The batch, EU (203b)", default path pinned to
  docs/batch_eu.md - see the PITFALLS entry on the path=None trap), CLI (--root/--sites/
  --working/--model-json/--report).
- Verified: dry run on a hard-linked temp tree of the 6 region-less sites with 202's
  proposals as recorded answers -> 29 new auto docs (newark 21, forthill 4, marietta 4),
  0 items, 3 sites classified already hand-fitted; golden 39/39 byte-identical in the
  temp tree; report byte-identical across two fresh trees; union section renders.
- Pre-EU-run union state of this checkout: 112 covered (90 US + 15 golden-doc EU +
  6 old-style + 1 bibracte item), 272 missing, 0 anomalies.

NEXT STEP (session 2): write tests/test_batch_eu.py, then run the suite with
.venv/bin/python -m pytest -q (the venv is green again since 800). Design, per prep
section 3 with the corrections learned this session:
- Sample = the 6 region-less sites (the only non-US ground tracked in git). Recorded
  answers = 202's proposals (all 29 pass the real gate - DECISIONS 2026-10-11). EXPECT:
  29 new auto docs, ZERO items, fudge/highbank/hopeton classified already hand-fitted
  (NO no-picture items for them - the merged loop's `and not rec["pre_fit"]` guard).
- The no-picture branch: add bibracte-q650053 to the sample (France, zero candidates,
  pre-existing 201-era no-picture item): assert the upsert re-stamps no_picture_found
  with the batch's searched wording, candidates stays [], resolved stays null.
- Optional stretch: avebury (6 cands, 1 pre-doc -> skip) and old-sarum (5 cands, 2
  pre-docs -> skip) for the doc-skip path; record short (2-pair) answers for their
  fresh commons rows to exercise the could-not-fit item entries (mirror test_batch_us's
  _answers fallback; propose_for may raise for commons rows - the loop's try/except
  already routes that to the item).
- Stub-gate cases: monkeypatch batch_us.gate_placement (203a's pattern; the patch is
  visible to run_sites' global lookup) for always-accept / always-reject on an EU site
  with >=2 fresh candidates and no pre-fit (compute it in the test, don't pin a name).
- Golden invariance: the 39 golden files + the 6 old-style site.json (pre/post hashes -
  they are NOT in the golden); allow re-saves only of the sample sites' own item files
  (bibracte's included), exactly as test_batch_us's review_before allowance.
- CRITICAL for the tree fixture: _WRITE_IN_PLACE must include "docs/batch_eu.md" -
  after the session-3 working run that file exists in the checkout, and write_report
  truncates its target in place, so a hard-linked copy would land in this checkout.
- Union check: weaker form in the temp tree (see DECISIONS); the full live-checkout
  assertion (0 missing, 0 in both, 0 orphans) is skip-gated until docs/batch_eu.md
  shows "Sites run: 294". Never pin the live population (211 will grow sites.json).
- Hermetic: socket-blocking autouse fixture, no server (the loop never PUTs - 203a's
  R5 read the box's "port 0" the same way; if the driver reads it literally, one GET of
  a test-written doc through the session served fixture settles it).

Session 3 (working phase): .venv/bin/python fit/batch_eu.py --working over all 294
(AI-box tunnel needed as in 203a's run; it fetches book page images, commons pictures
and Esri aerials for the ~17 lidar:false EU sites - those fetches land in the
gitignored cache, never in git). Afterwards: sha256sum -c the golden, hash-compare the
6 old-style site.json pre/post, read the report's union section (should read "384
covered, 0 missing, 0 in both" if both batches are complete), commit docs + items +
report, and tick the boxes in order (loop runs / union / report / golden+test).

For 212 (write into its hand-over when done): shared SEED 20261010; the EU sample in
docs/batch_eu.md is reproducible from it and disjoint from the US list; the no-picture
item list (175 sites incl. bibracte's 201-era item) is its search-harder list; 212 must
re-export web/data/review.json (the batch never writes it).

Re-read: fit/batch_eu.py:union_check - the coverage rules (item keyed by site field;
doc name-prefix check) and what counts as a hand fit; fit/batch_us.py:run_sites - the
`and not rec["pre_fit"]` guard that decides when a no-picture item is written.
