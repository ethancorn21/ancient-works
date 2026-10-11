Status: done
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
- [x] fit/batch_eu.py imports the loop from fit/batch_us.py and runs it over every non-US built
      site; every such site ends with at least one automatic platefit document (score
      recorded) or an open review item - or an existing hand fit.
- [x] The union of the two batch outputs covers every built site exactly once: a check against
      sites.json over the documents and items both tasks wrote - no site in both, none missing
      (the 6 region-less sites must appear in the EU list, not be dropped).
- [x] docs/batch_eu.md in the same format as docs/batch_us.md: counts (automatic fit / review
      item / already hand-fitted / no picture found), the recorded seed, and the seeded sample
      of automatically accepted fits (20 where there are at least 20, a page URL each).
- [x] After the run the hand-fit documents are still byte-identical to
      tests/golden/hand_fit_docs.sha256; the test (no network, port 0) runs the loop on a
      fixed sample of non-US sites with in-repo ground and asserts the invariants.

## Notes
- Do not re-implement the loop in fit/batch_eu.py: import it. If a change to the loop itself
  is genuinely needed, request it in a DECISIONS entry to the owner of fit/batch_us.py rather
  than copying it (one place for each piece of knowledge).
- The 20-sample lists of the two reports are separate (one per region); 212 picks the final
  combined 20-sample for the human's 18/20 check from the whole set.

## Hand-over

Session 3 (2026-10-11, iteration 50) - WORKING RUN DONE; task COMPLETE (all 4 boxes ticked,
Status: done, done claim filed). This is the final state; nothing is pending. If this task is
ever reopened (e.g. a 212-era re-coverage run changes the tree), re-verify the checks below.

Final state (all committed in this task's commit):
- docs/batch_eu.md: "Sites run: 294". Counts: 54 automatic fit, 47 review item, 18 already
  hand-fitted, 175 no picture found, 0 error; 252 review items written. Seed: 20261010
  (shared with 203a). Sample: the seeded 20 of the 94 EU auto docs (reproducible from the
  seed over the EU doc set), a page URL each.
- data/db/platefits/: 130 docs = 36 pre-batch (20 golden hand fits + 16 US auto from 203a)
  + 94 new EU auto docs (auto: true, gate score recorded).
- data/review/: 341 files = 340 items (252 EU + 88 US) + README.md. Every EU item is open
  (resolved null). The 175 no-picture EU items (no_picture_found set) are 212's
  search-harder list; bibracte's 201-era item was re-upserted with the batch's searched
  wording.
- Union section (in the report): 384 built sites, 384 covered, 0 missing, 0 in both, 0
  orphan docs, 0 orphan items, no bad doc names; the 6 region-less sites in the EU list.
- Golden intact: sha256sum -c tests/golden/hand_fit_docs.sha256 = 39/39 both BEFORE and
  AFTER the run; the 6 old-style site.json (newark/forthill/marietta/fudge/highbank/
  hopeton) byte-identical (pre/post hashes were /tmp/oldstyle6.sha256).
- Suite: 46 passed, 0 skipped (test_union_full_coverage_live un-skipped and passed: the
  report's "Sites run: 294" equals the live EU partition size).

Session 3 did: (1) pre-checks - AI-box tunnel up (qwen3.8-27b on 127.0.0.1:8080/8081 vLLM,
8082 llama.cpp), golden 39/39, the 6 old-style hashes captured, all 306 fresh-candidate
images already local in the shared data/raw store; (2) the run: AW_LLM_URL=
http://127.0.0.1:8081/v1/chat/completions .venv/bin/python fit/batch_eu.py --working under
nohup (~30 min, 306 model calls, log /tmp/batch_eu_50.log; the only network was 17 Esri
aerial fetches for the lidar:false sites into the gitignored shared data/raw/aerial cache);
(3) the one code change of the session: tests/test_batch_eu.py's
test_hand_fitted_sites_get_items_for_their_other_pictures went STATE-AWARE (the run made 2
of old-sarum's 3 pinned short-answer plans into auto docs, so the recorded run now skips
them as pre-docs - pinned = short-list ∩ fresh, expected item = live ∪ fresh, lead = the
post-run invariant; see the DECISIONS entry and the new PITFALLS entry on state-dependent
recorded-answer tests); (4) verification and the single commit (docs + items + report +
test fix), all 4 boxes ticked.

For 212 (combined sample / re-coverage / review.json re-export):
- The US sample (16 docs, docs/batch_us.md) and the EU sample (20 of 94, docs/batch_eu.md)
  are each reproducible from the shared SEED 20261010 over their disjoint doc sets.
- The final combined 20-sample for the human's 18/20 check: 110 auto docs total (16 US +
  94 EU); 212 picks from that union with its own seed and writes docs/batch.md.
- 212's re-coverage run over grown sites must re-export web/data/review.json (the batch
  never writes it; 201's export owns it) and re-run 001's held-out check if it touches the
  non-automatic reference (802's partition filters auto docs - it is state-agnostic).
- The 203b tests are state-aware: a 212 re-coverage run that adds docs/items will NOT break
  test_hand_fitted_sites_get_items_for_their_other_pictures (fresh is computed from the
  live tree); the live union test's skip gate is dynamic (report's "Sites run" vs the live
  EU partition size), so it stays correct when 211/212 grow sites.json - a re-run of the
  EU batch that changes "Sites run" re-gates it correctly.
