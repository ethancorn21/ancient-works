Status: done
Depends on: none
Touches: pipeline/plan_fit.py, tests/test_fit_provenance.py

# 219: The page's source line states the book's year once (the commons case)

## Goal
303's live shotwick run (docs/site_flow.md, 2026-10-11) exposed a blemish in `plan_fit.build`'s
commons source line:

    Shotwick Castle, plan from Mackenzie, The Castles of England (1897) (1897), Wikimedia
    Commons: by The British Library; No restrictions; ...

The picture's title already states the book's year, and the document's label (`"1897"`) repeats
it. A source line should state each fact once: when the label's year is already in the title,
drop the label's parenthesis; only a title without a year shows the label (or "undated"). The
book branch (`{book}: {title or label}`) and the who-placed clause (303) are not touched.

## Acceptance criteria
- [x] `plan_fit.build`'s commons branch prints `TITLE (LABEL), Wikimedia Commons: CITE.` with the
      `(LABEL)` parenthesis dropped when the title already contains that year, and "undated" only
      when the title carries no year at all; the book branch and the how-clause are byte-identical
      for every existing document (a test proves it for a book doc and for a yearless commons
      title).
- [x] The built commons depictions in the repo carry the fixed line - at minimum shotwick's
      `web/data/sites/shotwick-castle-q7502621/depictions.json` (gitignored; its overlay is
      current, so a one-off re-bake of the entry's `source` field is the smallest honest
      re-bake: same corners, same fit record, only the string changes) - and a hermetic test
      pins the new string for the shotwick document end to end.
- [x] The full suite is green (the 303 tests' pinned strings stay intact: none of them pin the
      commons how-clause with a doubled year).

## Notes
- Filed by 303 (agent a), whose live run produced the string; not fixed there (a string-format
  change in `plan_fit.build` is outside 303's provenance scope).
- Depends on 302c only because both touch `pipeline/plan_fit.py` (keep the edits disjoint; 302c
  is the 302 decision/wiring task).

## Hand-over

(2026-10-12, iteration 133, agent c - TASK COMPLETE, done claimed. All three boxes verified this session; suite green 126 passed / 1 skipped, run twice (before and after the re-bake).)

**Committed this session (1fde00e + the done commit):** (1) section e of `tests/test_fit_provenance.py` - the hermetic proof: `no_net` fixture (in-process socket guard), a flat stand-in picture at each doc's OWN frame size (fs=1 => the least-squares fit math is exactly the doc's: corners, residuals, m all exact, no download), `plan_fit.build` on the real store docs, entry's `source` pinned: book byte-identical (arbor-low), yearless commons byte-identical (bergues + bethlehem "undated"), and the fix (shotwick: year-in-title drops the repeated parenthesis; `"(1897) (1897)"` absent). Note: the previous hand-over's shotwick string had `File/` where the doc's cite says `File:` - pinned to what the code actually prints. (2) Re-baked this checkout's built commons depictions whose title carries a year: the 14 built ones (aldenhaag, avaricum, barnard, bethlehem x5, bolsover, cahokia, castle-rising, mayburgh, mound-bottom, whitley) + shotwick (never built HERE - created its site dir; its big picture was already cached, so ZERO downloads). Proof: every rebuilt entry identical to the stored one in every field except `source`; a second identical run is byte-stable (the fixed state is a fixed point); shotwick's rebuilt entry matches agent a's built entry (corners, fit, year, label, scale, coverage, kind, file, ink) with only the source fixed.

**web/data/sites.json (tracked, in 306's Touches):** each build's trailing `build_site.set_drawings` refreshed the five affected sites' marker fields (the committed bookkeeping was STALE: drawings 0 despite built plans - bethlehem 0->12, avaricum/barnard/bolsover/shotwick 0->1). I restored the committed bytes: a gitignored build does not change committed bookkeeping (agent a's checkout shows the same convention: shotwick built on disk, its sites.json entry still 0). The product refreshes it on its own next (any platefits save's sweep, or build_catalog's write_entry) - so do not "fix" it from a fit task.

**If this reopens / for the other checkouts:** agent a's and the lead's checkouts keep the old doubled strings in their OWN gitignored web/data - do not touch them from here; a one-off `plan_fit.build(doc)` per stale entry re-bakes them (the 15-doc list is derivable: every built depictions entry whose `fit.doc` is a commons doc with `_year4(title)`; the re-bake script pattern is /tmp/rebake_219.py if the VM still has it, or see the DECISIONS entry). `docs/site_flow.md`'s 303 section quotes the doubled line as a historical record - intentionally not changed.

**Re-read:** `web/data/sites.json` (the shotwick entry: drawings 0 / oldest None despite the built plan on disk in this and agent a's checkouts) - if you touch it, it is the page's bookkeeping (306's file), refreshed by the product, never hand-edited from a fit task.
