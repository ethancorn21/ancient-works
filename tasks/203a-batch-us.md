Status: open
# 203a: The batch, US - the 90 US built sites
Depends on: 001, 200, 201, 202
Touches: fit/batch_us.py, data/db/platefits/, data/review/, docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256

## Goal
Run the whole loop for every US built site in web/data/sites.json (region "US", 90 of 384):
candidates = the plans.json rows whose "sites" contains the site (with 200's evidence field
where present) -> proposed pairs (202) -> fit (the existing plan_fit solver) -> gate (001).
Accepted fits become automatic platefit documents in data/db/platefits/ with the gate's score;
everything else becomes a review item in data/review/ in 201's format. The 20 existing
hand-fit documents are never touched. 203b (the rest of the world) reuses this module's loop.

## Acceptance criteria
- [ ] Before the first batch write: tests/golden/hand_fit_docs.sha256 is committed, listing all
      20 pre-batch platefit documents (file name + sha256) and the 19 hand-fit sites'
      data/sites/<id>/site.json files.
- [ ] fit/batch_us.py runs the loop for a set of US sites: for each site, every candidate
      picture goes propose -> fit -> gate; the accepted ones write automatic platefit documents
      (existing format + score + "auto" mark) and the rest become review items; a site with no
      candidate at all gets an item marked "no picture found". The loop is a function 203b can
      import and point at its own site list.
- [ ] In the full working-phase run (all 90 US sites, recorded in the report), every US site
      ends with at least one automatic document or an open review item - or an existing hand
      fit.
- [ ] After the run the 20 hand-fit documents and the 19 site files are byte-identical to the
      golden hashes; the batch added files, it rewrote none.
- [ ] docs/batch_us.md: counts (automatic fit / review item / already hand-fitted / no picture
      found), the recorded seed, and the seeded sample of automatically accepted fits (20 where
      there are at least 20; a page URL each) for the human's 18/20 check.
- [ ] Test (no network, port 0): the loop run on a fixed sample of US sites with in-repo ground
      produces, per site, a document or an item in the right format; the hand-fit files are
      byte-identical; the report's sample is reproducible from the recorded seed.

## Notes
- Ground: the in-repo images (web/data/sites/<id>/) carry the test fits (fitkit convention:
  relief where there is, aerial otherwise). The full run uses the same convention per site;
  fetches happen only in the working phase, never in tests.
- The page-facing sync (overlays, drawings counts) is NOT this task's job: the documents sit
  in data/db/platefits/ and 212 syncs them to the page in one pass.
- The golden hashes cover the pre-batch state of THIS checkout; regenerate them if the batch
  has already been partially run, but never edit them to make a failure pass.

## Hand-over
