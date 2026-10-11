# The one-site line: finish a site all the way to the map (task 300)

From 2026-10-11 (Ethan) the work goes one site at a time, all the way to the map: fit its old
drawings, put them over the ground, count them in its entry, publish its review item. The batch
(203a/203b) stops at writing documents and review items; this line is the rest of the way, as
one command the next site's session reuses:

```
.venv/bin/python tools/site_done.py <site id> [--working | --model-json FILE]
```

`--root DIR` redirects the data paths (the test runs the line on a copy of one site's files).
Exit codes: 2 = the site is not built, 1 = a document failed to sync, 0 = done.

## The line, step by step (as the next site's session runs it)

1. **fit** — `fit/batch_us.py run_sites`, but only when the site has candidate pictures in
   `web/data/plans.json` that have NEITHER a platefit document (`data/db/platefits/<site>.<plan>.json`)
   NOR a review-item entry yet. Covered pictures are never re-fitted: the batch's item upsert
   replaces a candidate's entry whole, so a blind re-run would swap the rich entries (gate
   scores, pairs, the why) for "no model answer" stubs. A site whose candidates are all covered
   skips the batch run entirely (Stonehenge: 13 candidates, 7 documented, 6 in the item).
   A brand-new site needs a model here: `--working` (the local vision model on the AI box) or
   `--model-json` (recorded answers, a dry run); with neither, unfitted pictures land in the
   review item as "no model answer".
2. **sync** — `pipeline/plan_fit.py build` for every one of the site's fit documents: the big
   picture (a Commons file is downloaded once and cached in `data/raw/commons/big/`, paced like
   `pipeline/commons.py`), the similarity or homography fit, `plan_<id>.webp` + `plan_<id>_ink.webp`
   in `web/data/sites/<site>/`, and the entry in its `depictions.json` (kind "plan"/"view",
   corners, fit record, the source line). A document whose overlay is already current (same
   `at`, same doc id) is skipped, so re-running the line is a no-op.
3. **entry** — `pipeline/build_site.py set_drawings`: the site's drawing count in
   `web/data/sites.json` (plate + plans + views; survey maps don't count). The page colours
   the site's square by it — this is what makes a site a flagship on the map.
4. **review** — `fit/review.py export`, scoped to the site: it writes `web/data/review.json`
   (the whole open queue, as always) but records a resolving document into item files only for
   this site, so a one-site run never touches another site's files.

The output names every picture of the site and where it ended up: *synced to the map (gate X m)*,
*sent to the review queue (why)*, or *skipped: overlay already current*.

Stonehenge (the first site through the line, 2026-10-11): all 13 candidates were already covered
by the batch (7 automatic documents, 6 in one review item), so the line synced the 7 documents,
took the entry from 0 to 7 drawings, and published the item (the page then has 339 open of
340 items). What the page shows:

- `docs/site_flow/stonehenge.png` — the site open on the aerial photograph with the 1800
  Rijksmuseum plan in red ink over the ground (its circles and stones sit on the real sarsens),
  the site panel listing all 7 drawings, and its map square coloured (7 drawings).

## What broke on Stonehenge, and the fix (so the next site does not meet it again)

- **The download burst got 429'd.** `plan_fit.load_picture` used bare `urllib` for the Commons
  API answer and the big picture; seven back-to-back fits are 14 requests and Wikimedia 429s
  bursts (PITFALLS). Fix: `_fetch` in `pipeline/plan_fit.py` paces like `commons.get`
  (1 s apart, honours `Retry-After`, backoff on 5xx). The next site's pictures download the same
  way; no flag, no work.
- **The source line lied.** `plan_fit.build` said "Placed by hand..." for the batch's automatic
  fits too. Fix: a document with `"auto": true` gets "Fitted automatically by the batch on N
  matching points ... (gate score X m)"; hand fits keep their old string.
- **The drawings line showed 7 -> 7.** `build` already refreshes the count after each fit, so a
  "before" read after the sync sees the final value. Fix: `site_done` reads the entry before the
  sync; the line then prints the true journey (0 -> 7).
- **A one-site run must not write other sites' files.** `review.export` records a derived
  `resolved` into any item file that has one; one other site (alligator-effigy-mound) had a
  derivable but unrecorded resolution, so a global export would have rewritten its item. Fix:
  `export(root, site_id)` scopes the record to that site (the page file is still the whole
  queue). The batch keeps calling it global.
- **Not a bug, a page rule:** survey maps younger than 150 years are hidden from the site panel
  (only plans/drawings and 150+ year-old surveys show). Stonehenge's 1900 OS map therefore never
  appears; its 1842 six-inch map does. A site with only recent maps will look aerial-only in the
  panel even though the files are built.

## Files the line touches (one site only)

`web/data/sites/<site>/**` (the overlays, `depictions.json`), the site's entry in
`web/data/sites.json`, `web/data/review.json` (always the whole queue), the site's own item in
`data/review/` (only to record a resolution), new big-picture caches in
`data/raw/commons/big/`. It never rewrites a fit document (`data/db/platefits/` is byte-
identical across runs), never another site's files, and never the 20 hand-fit documents
(`tests/golden/hand_fit_docs.sha256` stays green).
