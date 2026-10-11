Status: done
# 206: Mackenzie - the five-towered castle on page 212
Depends on: 001, 200, 218
Touches: fit/src_mackenzie.py, data/catalog/extras_mackenzie.jsonl, data/commons/files_mackenzie.jsonl, data/commons/classified_mackenzie.jsonl, data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json, data/sites/shotwick-castle-q7502621/, web/data/sites.json, docs/lead_mackenzie.md, tests/test_src_mackenzie.py, tests/golden/src_mackenzie_sample.json

## Goal
GOAL.md point 4: page 212 of Mackenzie, The Castles of England (1897) is a five-towered
castle plan with no caption - the only gap in the book's already hand-tied 29 plates
(pipeline/sources.py). Identify the castle with evidence (the book is arranged by county:
the plates around p.212 - p.207 Oxford, p.231 Lancaster - constrain it; five-towered plans
are rare; the surviving ground is the final check), tie it to a site, stage the row, and let
the fit prove the identification. If it cannot be identified with evidence, document the
search and drop the lead: a wrong castle on the map is worse than none.

## Acceptance criteria
- [x] The p.212 scan is found (the British Library's Flickr scans, the same URL pattern as
      the hand-tied rows) and downloaded to data/raw/books/ in the working phase; the
      five-towered plan is drawn out and available for comparison (its shape, tower count,
      and any scale/north information recorded in docs/lead_mackenzie.md).
- [x] The castle is identified by evidence recorded in docs/lead_mackenzie.md: the book's
      county context, the plan's shape against candidate castles, and the surviving ground
      (relief/aerial) matching the plan - or the lead is dropped, and the file says exactly
      what was searched, what candidates were considered, and why none was accepted.
- [x] If identified: the site (an existing one by QID, or a new extras row) and the picture
      row are staged (files_mackenzie.jsonl with the 200 evidence field - caption+coords or
      QID, the source book recorded - and a classified row "plan" by hand), and a fit of the
      plan on the site's ground passes the gate (001): the identification is proven by
      numbers, not just asserted.
- [x] Test (no network): the staged row joins and passes fit/evidence.py check offline, with
      a golden sample. If the lead was dropped, the test asserts the documentation exists
      and the staging files are absent or empty.

## Notes
- The other 29 Mackenzie plates stay where they are (sources.py hand ties); this task adds
  at most one row. The fit is proposed through 202's machinery if available; otherwise a
  hand proposal (fitkit) is fine - this is one plate, not a batch.
- A castle whose site is not built yet: the extras row gets the picture as its reason to
  build (aerial_ok) so 211 builds it with the plan already tied.

## Hand-over

**DONE (iteration 92, agent a, 2026-10-11) - the driver's rejected done-claim is fixed, not
argued.** Iter 91 claimed done; the driver rejected it: 3 tests failing that were not failing
before 206's merge (test_batch_eu::test_union_check, test_batch_eu::test_union_full_coverage_
live, test_serve::test_platefits_docs_match_sites). Root cause (verified in code): all three
enforce the shared-store invariant "every doc in data/db/platefits/ names a site in
web/data/sites.json" (batch_eu.union_check orphan_docs, batch_eu.py:87; test_serve.py:53) -
my doc named the UNBUILT shotwick site. The lead had cut 211 off my Depends on (0be0b09, the
cycle), so waiting was not an option: 206 built the site.

**The fix (the only new artifacts):** `.venv/bin/python pipeline/build_catalog.py --ids
shotwick-castle-q7502621` (17 s, the project's own machinery): EA Environment Agency 1 m
LiDAR (source "ea") -> relief.jpg + block diagram (relief clip 1.2 m, z 3.97-25.25 m); nls ->
Ordnance Survey six-inch 1st edition 1842 (NLS tiles os/six-inch-cheshire + -flintshire,
coverage 1.0) -> six-inch-1st.webp + ink; Wikipedia summary (enwiki lead paragraph).
build_site.write_entry appended the 385th entry to web/data/sites.json (drawings 0,
lidar_credit EA; the other 384 entries byte-identical, verified by parsed diff). Committed:
`data/sites/shotwick-castle-q7502621/site.json` (new; dem.npy/dem_box.json/dem_credit.json
gitignored) + `web/data/sites.json` - both added to this task's Touches. Per-site web images
are gitignored (rebuilt by the pipeline in any checkout). The 8 fit/staging/test artifacts are
unchanged; only the lead doc's §1/§5 changed (they now say the site is built).

**Verification (all re-run this session):** test_union_check PASSES (shotwick is in the EU
partition - region "England" != "US" - and covered by my doc; 0 orphans);
test_union_full_coverage_live SKIPS on its own gate (docs/batch_eu.md "Sites run: 294" vs the
grown live EU list 295 - a skip is not a failure; 203b/212 re-covers the growth);
test_platefits_docs_match_sites PASSES. Full suite: **64 passed, 1 skipped, 0 failed**
(63.91 s; was 62/3 before the build). My 4 tests 4/4; test_gate all pass.
`fit/src_mackenzie.py --check` exit 0; `--gate` accept (stats in the doc and the golden,
unchanged).

**If the driver rejects again:** the remaining question would be policy, not red tests (the
lead cut the 211 cycle; the suite is fully green on this branch) - next step is ask_human
with this evidence, not another re-verification pass. 211's merge needs no 206 action:
build_catalog skips the built site, its "every new site built" box holds from the existing
entry, it merges the 3 staging rows and the extras row (duplicate logged against the
catalog's sites.jsonl row).

MD5s: src_mackenzie 77a47defd606a8599e3af9e28b74894f, files_mackenzie
f637c4bebbd98ebb059652936e06646d, classified_mackenzie 2ed56b79bbd356aced13230978e8536f,
extras_mackenzie a7060e1292d2607c657a43200dd20b94, platefit doc
9a1924cf84414e26cf84b292718ce3b2, test_src_mackenzie ddb146a2f8cb47e9b2f33ef2b0e5cbfe,
golden f0936d9a0b4bf00e60ca1f3afc625d95 (all unchanged since iter 66); lead_mackenzie
fc38137c988f1479b804781a30095e88 (this session's §1/§5 build-status update; was
5d7b7ab69371074b201d89b6b2bda0d4). The V2 OCR re-download recipe stays in tasks/prep/206.md §6.
