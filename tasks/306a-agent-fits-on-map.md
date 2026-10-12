Status: done
# 306a: Look at the agent fits that are ON the map - the 23 built overlays
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/sites.json, web/data/review.json, web/data/sites/, tools/audit_306a.mjs, fit/src_mackenzie.py, tests/test_src_mackenzie.py, tests/test_fit_provenance.py, tests/golden/src_mackenzie_sample.json

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
- [x] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open with its overlay active over the aerial photograph; plus a second shot over the LiDAR
      relief where the site has a `relief.jpg` - shotwick has none), taken with `tools/shot.mjs`
      against `server/serve.py --port 0` on this checkout (the driver recipe is in the parent's
      Hand-over; GET only, ephemeral port).
- [x] A new section "## The agent fits, looked at (task 306)" in `docs/site_flow.md` holding one
      line per doc: what the drawing's lines sit on (the real banks, walls, ditches, streets) and
      the verdict. This subtask writes the section header and the 23 lines; the later subtasks
      append theirs.
- [x] A fit whose drawn works visibly miss the real ones (wrong size, shifted, rotated) leaves
      the map: the picture is upserted into the site's review item with the reason (the
      `fit/review.py upsert_item` pattern 300/303 use for fabrication hits), the document is
      deleted, and the site is rebuilt with `.venv/bin/python tools/site_done.py <site>` (the
      overlay leaves `depictions.json`, the `drawings` count refreshes, the item is re-exported).
      Check the big picture is already cached in `data/raw/commons/big/` before a rebuild so no
      download hits the shared `data/raw` dir.
- [x] A fit that sits right stays on the map, and its line says so. No `by: hand` document is
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


## Hand-over
(2026-10-12, iteration 138, agent c - session 4. TASK DONE: all four boxes ticked, Status: done,
committed. The session-3 bethlehem audit was already committed by the driver (406562b), so this
session fixed the 5 tests the removals broke, re-baselined the mackenzie golden, ran the full
suite green, and closed the task.)

**What session 4 changed (all committed).**
- `fit/src_mackenzie.py`: new `doc_record()` (stdlib-only): the doc's dict from the store file if
  present, else from the review item (scans data/review/*.json for item["site"] == SITE and the
  candidate with plan == PLAN). `gate()` reads `doc_record()["pairs"]`; `check()` treats an
  item-resident record as the doc (no more "not written yet" in that state); `golden()` writes
  `doc_record()` with `at` normalized; docstring updated on the --gate/--check/--golden lines.
- `tests/test_src_mackenzie.py`: all three doc-reading tests use `mack.doc_record()`;
  `test_staged_row_and_join` additionally asserts, when the store file is absent, that the record's
  `why` is the 306a audit reason; docstrings note the record is the review item's candidate after
  the audit and that the gate accepting the ~2x fit's pairs IS the documented n=3-6 blind spot.
- `tests/test_fit_provenance.py` (section e, both commons cases re-pointed - verified strings by
  running `_build_source` myself before pinning): the yeared-title case now pins
  bethlehem-q2523914.c_a164ee440558d66c (title states 1748; the label "c. 1748" parenthesis is
  dropped; batch how-clause with gate score 39.3 m; guard ` (c. 1748)" not in src` - NOTE the year
  still occurs twice in the line, title and file URL: the hand-over's `count("1748") == 1` was
  wrong, the rule drops the label parenthesis only). The yearless/undated case keeps bergues and
  re-points the second half from the audited-out bethlehem c_075db to
  durocortorum-q4896307.c_08d995eb23a685c2 (batch-marked, no label, no year in title:
  "Plan-Reims-Bas-Empire (undated), ... within 1 m (gate score 0.0 m)").
- `tests/golden/src_mackenzie_sample.json`: regenerated with the module's own
  `.venv/bin/python fit/src_mackenzie.py --golden`. The diff is exactly one field: golden["doc"]
  is now the review item's candidate record (the store file deleted), so it carries `why` (the
  306a audit reason); `at` normalizes to the same 0000-00-00 as before; files/classified/extras
  rows unchanged.
- Suite (`.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py`): **128 passed,
  1 skipped, 0 failed** (202 s). test_gate.py stays the pre-existing driver-baseline red, excluded
  as before.

**Facts for 306b-f and any follow-up.**
- The `docs/site_flow.md` section "## The agent fits, looked at (task 306)" (line ~702) holds
  306a's 23 lines at the top, in this order: aldenhaag, alligator-effigy-mound, avaricum, barnard,
  barwick, binche, bolsover, burlington, forthill, newark, shotwick, then the 12 bethlehem lines.
  306b-f APPEND their lines below the bethlehem lines (the intro says so). Screenshots go in
  `docs/site_flow/agent_fits/<site>_<plan>.png` (306a's 45 are there; same naming).
- Removal recipe used (in case a later audit needs it and the parent's hand-over is gone):
  `review.upsert_item('.', sid, [entry])` with entry = the FULL doc record (every store field)
  plus `why` = the audit reason (the 206 mackenzie tests need the full doc; a reviewer of a 2x fit
  needs the anchors/size); delete data/db/platefits/<site>.<plan>.json; `plan_fit.prune('.', sid)`
  (drops the overlay + webps, refreshes `drawings` via build_site.set_drawings); then ONE
  `review.export('.')` at the end of the batch. Do NOT run tools/site_done.py on a site whose
  matcher is reachable: its fit phase would place a NEW unaudited fit (the 206 trap, session 2).
  web/data/sites/<site>/ dirs are symlinks to the shared /home/agent/projects/ancient-works tree
  and are gitignored (except the 6 hand sites) - depiction changes there are NOT part of any
  commit; only the jsonl/store/json files in this checkout are.
- The agent-session how-clause of plan_fit.source_line ("Fitted automatically on N matching
  points", no "by the batch", no gate score) is no longer pinned by any store doc: shotwick was
  the only by:agent non-auto document and it is in the review item now, not the store. The rule
  still lives in plan_fit.source_line (L297-306) and its docstring; a future agent creating a
  fresh agent fit (no batch mark) could re-pin it if one lands in the store.
- web/data/fit_queue.json (derived by tools/fit_queue.py; agent a's 307 rework owns the fit tool
  and its regeneration) still lists the removed bethlehem SoP docs among the bethlehem entry's
  candidates - that is CORRECT after the audit, not a dangling reference: the queue is rebuilt
  from plans.json + review items, and the items now hold those candidates with their audit `why`.
  No 306a action was possible on it anyway (not on my Touches line; 307 is mid-rework).
- The headless audit driver remains `tools/audit_306a.mjs` (visitor's way: select -> the doc's
  depiction -> setGround -> applyDep; 1440x900; idempotent re-run; one `server/serve.py --port 0`
  for the whole run; NODE_PATH=/home/agent/tools/shot/node_modules for shot.mjs/Chrome). A later
  subtask driving on-map docs the same way can copy it; the parent's hand-over holds the
  fit-tool (orphan) variant of the recipe.
