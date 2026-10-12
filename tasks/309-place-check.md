Status: open
# 309: The queue's namesake check - a queue candidate must show the site's place, not just its name (carved from 307 box 1, 2026-10-12, for agent c)
Depends on: 305
Touches: tools/fit_queue.py, web/data/fit_queue.json, data/fit_place.json, data/review/, data/review/README.md, web/data/review.json, tests/test_fit_place.py, docs/site_flow.md

## Goal
The queue's first entry pairs Allcroft 1908 Fig. 217 "The Devil's Dyke Camp, near Brighton"
(a Sussex hillfort) with the Devil's Dyke in Cambridgeshire - same name, 150 km apart, and no
zoom could have helped the owner ("it doesn't zoom me into the Devil's Dyke, so I don't know
where it is"). So every queue candidate is checked to show the same place as its site, not
just the same name (the book's caption/place words and county against the site's place,
region and coordinates; Wikidata where it helps). A mismatch leaves the queue and goes to
the review queue with the reason "same name, other place: <caption place> vs <site place>";
where the right site exists in the catalog, the candidate is moved to it instead. This is
307's box 1, including its "report how many of the queue's entries were wrong". Carved out
of 307 by the lead so agent c (who owns the data-side tasks) takes it; 307 keeps the page
work only.

## Acceptance criteria
- [ ] tools/fit_queue.py check: for every (site, candidate) pair of the built queue, a place
      verdict computed from the stored fields alone (hermetic, stdlib): the caption's place
      words (the book row's place field and county, title words like "near Brighton", and the
      recorded evidence field of fit/evidence.py - a caption_coords pass or a stored conflict
      with its resolved coordinates) against the site's place/region/county/coordinates
      (the web/data/sites.json entry, the catalog row and its admin county). A verdict is a
      mismatch only when a KNOWN place contradicts the site's (a different county within one
      country, a different country, or resolved coordinates far outside the site's region);
      an unknown place never mismatches (fail open), and a place that contains the site
      (a country-level word, the site's own county, the site's own name resolving near the
      site) is not a mismatch. --live re-resolves caption place words through the cached
      Wikidata (pipeline/catalog_wd.py) and commits the resolved coordinates into the
      verdicts; it is for the human, the tests never call it.
- [ ] The verdicts are the committed record data/fit_place.json: per (plan, site) the
      caption place (word + resolved label/lon/lat/qid where known), the site place, the
      verdict (mismatch | ok), the reason, and the right site id where one was found - the
      file re-verifies from stored fields on every build (like fit/evidence.py check
      re-verifies recorded facts: a recorded mismatch whose stored coordinates no longer
      contradict is flagged, not silently kept).
- [ ] The queue build applies the verdicts: a mismatched (site, candidate) leaves the queue;
      the site stays if it still has a candidate (its best recomputed over the remainder),
      and a site with no candidate left leaves entirely. Every entry that is not a known
      mismatch stays in the file, in the same order. Devil's Dyke Camp near Brighton
      (earthworkenglan01allcgoog_n0686_1) is no longer paired with devil-s-dyke-q3307343.
- [ ] Where the right site exists in the catalog, the candidate is moved to it instead of
      review: upserted (fit/review.py upsert_item) into that site's review item with the
      row's stored fields plus the reason. Allcroft n0686 moves to
      devil-s-dyke-hillfort-q17674160 (Poynings, West Sussex - the catalog's Devil's Dyke
      hillfort; it is unbuilt, so it appears in the review list, not the queue). Where no
      catalog site fits (Allcroft n0354 "ARDOCH, PERTHSHIRE." on the Spanish Coria and
      Vindomora: the catalog has no Ardoch), the mismatched candidate goes into the
      site's own review item instead, with the reason "same name, other place:
      <caption place> vs <site place>".
- [ ] The reason is a candidate extra documented in data/review/README.md's producer list,
      and the page's Review list shows it on the item (the minimal change to web/review.js
      if it needs one belongs to 307c, not here - only the item file and the export).
      web/data/review.json is re-exported by fit/review.py export (called in-process from
      the check CLI; this task never writes the page file itself).
- [ ] The report: docs/site_flow.md gains a section stating how many of the queue's 117
      entries were wrong (pairs and sites, both counts), which candidates moved and which
      went to review, and how the check decides (stored fields only; --live for humans).
- [ ] tests/test_fit_place.py (hermetic, no network, temp tree, ephemeral port where a
      server is needed): a synthetic tree where the only mismatch is a caption place
      contradicting the site's county (caught, pair dropped, right site's review item gains
      the candidate with the reason); a real-tree snapshot (the committed data files as
      fixtures): the regenerated web/data/fit_queue.json does not pair n0686 with the
      Cambridgeshire dyke, the Sussex item carries it, n0354 is out of the Coria/Vindomora
      entries, and the committed data/fit_place.json re-verifies from stored fields
      (including one deliberately stale record that no longer contradicts: flagged).

## Notes
- stdlib-only constraint on tools/fit_queue.py holds: fit/review.py and fit/propose.py are
  both stdlib-only and importable; the check itself must not import pipeline/ (numpy) -
  except the --live path, which may import the stdlib-only pipeline/catalog_wd.py (cached
  on disk) for its human runs.
- The parent 307's page subtasks (307b/307c/307d, agent a) must not be blocked by this task
  and must not write web/data/fit_queue.json or data/fit_place.json; they read the queue
  file tolerantly (fitqueue.js already does).
- The queue file's entry shape (305 contract: {site, name, best{plan,reason,row},
  candidates[...]} - pinned by tests/test_fit_queue.py part 1) stays as is; this task only
  drops mismatched pairs and emptied sites, so 305's tests (which run on trees without
  data/fit_place.json: no records -> no drops) must keep passing unchanged.
