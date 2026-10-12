Status: open
# 306a: Look at the agent fits that are ON the map - the 23 built overlays
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/sites.json, web/data/review.json, web/data/sites/

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 23
platefit documents with `by: agent` that are currently on the map - their overlay is built in
`web/data/sites/<site>/depictions.json` (the depiction's `fit.doc` names the doc) - over 12
sites. Open each the way a visitor sees it (site open, the depiction active, over the aerial
photograph, and over the LiDAR relief where the site has a `relief.jpg`) and judge whether the
drawing's lines sit on the real works. These are the fits the parent's title means by "none
reaches the map unseen" (Shotwick is here: 206's `by: agent` fit, 14-19 m residuals, never looked
at).

## Acceptance criteria
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open with its overlay active over the aerial photograph; plus a second shot over the LiDAR
      relief where the site has a `relief.jpg` - shotwick has none), taken with `tools/shot.mjs`
      against `server/serve.py --port 0` on this checkout (the driver recipe is in the parent's
      Hand-over; GET only, ephemeral port).
- [ ] A new section "## The agent fits, looked at (task 306)" in `docs/site_flow.md` holding one
      line per doc: what the drawing's lines sit on (the real banks, walls, ditches, streets) and
      the verdict. This subtask writes the section header and the 23 lines; the later subtasks
      append theirs.
- [ ] A fit whose drawn works visibly miss the real ones (wrong size, shifted, rotated) leaves
      the map: the picture is upserted into the site's review item with the reason (the
      `fit/review.py upsert_item` pattern 300/303 use for fabrication hits), the document is
      deleted, and the site is rebuilt with `.venv/bin/python tools/site_done.py <site>` (the
      overlay leaves `depictions.json`, the `drawings` count refreshes, the item is re-exported).
      Check the big picture is already cached in `data/raw/commons/big/` before a rebuild so no
      download hits the shared `data/raw` dir.
- [ ] A fit that sits right stays on the map, and its line says so. No `by: hand` document is
      touched; no new test failures against the driver's newest loop-start note (the suite was
      green in this checkout 2026-10-12: 123 passed, 1 skipped, test_gate pre-existing red).

## Docs (23, 12 sites)
- aldenhaag-q23650779.c_71c4ef3170b44288 - Aldenhaag detail kadasterkaart 1832 (Netherlands)
- alligator-effigy-mound-q4732645.c_618a6be74dfaff32 - Historical Collections of Ohio (US)
- avaricum-q281826.c_d457524470ca0ab3 - Caesar's Gallic war, Allen & Greenough (France)
- barnard-castle-q4185811.c_eacf8c673afcd863 - Alnmouth Tithe Map 1843 (UK)
- barwick-in-elmet-castle-q4865964.c_81c1ff143a862ee7 - Gott Collection at Hepworth Gallery (UK)
- bethlehem-q2523914.c_075db5049e2fb635 - Survey of Palestine, Bethlehem 01-beit-jala
- bethlehem-q2523914.c_1c20017970e54a01 - Survey of Palestine, Bethlehem 06
- bethlehem-q2523914.c_5ce1836b12e8e294 - Survey of Palestine, Bethlehem 03
- bethlehem-q2523914.c_67ed5d45466db19e - Plan of the Basilica of the Nativity, Sandys
- bethlehem-q2523914.c_7ee79582ebdab559 - (1881) PLAN SOUTERRAINS DE LA BASILIQUE
- bethlehem-q2523914.c_993872ffecfce2cf - Survey of Palestine, Bethlehem 11
- bethlehem-q2523914.c_a164ee440558d66c - Plan de Maestricht et environs 1748, detail Severen
- bethlehem-q2523914.c_a42a93d9589acd4d - Plan de Maestricht et environs 1748, detail Limmel
- bethlehem-q2523914.c_a8499553451a203c - Survey of Palestine, Bethlehem 09
- bethlehem-q2523914.c_ba63da7d782b9648 - Survey of Palestine, Bethlehem 08
- bethlehem-q2523914.c_d624c308cd860a1e - Plan de Maestricht et environs 1748, detail Limmel/Jerusalem
- bethlehem-q2523914.c_fc4566d6947287f4 - Survey of Palestine, Bethlehem 05-beit-jala
- binche-q95121.c_957d7ce2933eb332 - Binche, town plan by Jacob van Deventer (Belgium)
- bolsover-castle-q2968590.c_5531262b52faaea8 - Bolsover Castle, Mackenzie 1897 (UK)
- burlington-house-q225471.c_17e8fb3cf9037e19 - Burlington House, bird's-eye view by Johannes Kip (UK)
- forthill.b24849959_n0269_1 - Fort Hill, Highland county (Fowke 1902; US)
- newark.ArcheologicalAtlasOfOhio_n0098_1 - Earthworks at Newark (Mills 1914; US)
- shotwick-castle-q7502621.c_e6e5490609414bb9 - Shotwick Castle, Mackenzie 1897 (UK; aerial-only, no relief)

## Notes
- The `drawings` counts in `web/data/sites.json` are stale for most of these sites (0 although
  the overlay is built; only aldenhaag=1, forthill=2, newark=2 are non-zero): rebuilding a site
  via `tools/site_done.py` refreshes its count; a site whose overlay is judged right but whose
  count is 0 gets refreshed too (that is part of "sits right").
- The doc's stored pairs are the placement to look at: the overlay was built from them.
