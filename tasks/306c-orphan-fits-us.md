Status: open
# 306c: Look at the orphan agent fits, US - 16 docs, 9 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 16
US platefit documents with `by: agent` that are ORPHANS - in the store, but with no overlay
built on the site and not referenced by any review item, so a visitor sees them not at all.
Render each the way the page would if it ever showed it: the fit tool over the aerial
photograph, and over the LiDAR relief (every site here has a `relief.jpg`), with the doc's
stored pairs placed. The verdict records where the doc stands today (invisible) and whether
the placement is good enough to keep.

## Acceptance criteria
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief), taken with `tools/shot.mjs` against `server/serve.py --port 0` on this checkout
      (recipe in the parent's Hand-over; GET only, ephemeral port).
- [ ] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on (the real mounds, banks, ditches) and
      the verdict (keeps its document / deleted - and it is an orphan today, invisible on the
      page).
- [ ] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (`fit/review.py upsert_item`
      pattern), the document is deleted, and the site's review page file is re-exported scoped
      to the site (never another site's item file). The site stays covered for the union check
      (an open item counts). A fit that sits right keeps its document, and its line says so.
- [ ] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (16, 9 sites)
- cahokia-q333661.annualreportofbu1218901891smit_n0200_1 - Map of Cahokia group, Madison county, Illinois
- etowah-indian-mounds-q4533107.annualreportofbu1218901891smit_n0386_1 - Plat of the Etowah group (original)
- fort-ancient-q5470727.b24849959_n0264_1 - Fort Ancient, Warren county (Squier & Davis)
- hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1 - Plan of Cemetery Mound, Mt. Vernon
- hodgen-s-cemetery-mound-q5876069.b24849959_n0353_1 - Plan of mound at Mt. Vernon (Squier & Davis)
- marietta.b24849959_n0195_1 - The Marietta works (Squier & Davis)
- mound-cemetery-q6919104.annualreportofbu1218901891smit_n0563_1 - Plan of Cemetery mound, Mt. Vernon, Knox county
- mount-horeb-earthworks-complex-q6921321.c_d1dff07f0da57b0e - Peter Village enclosure, Squier & Davis Plate XIV fig 3
- pyramid-mound-q7263260.ancientmonuments00squi_n0134_1 - (Squier & Davis, untitled)
- serpent-mound-q968802.b24849959_n0313_1 - Serpent Mound; from Holmes
- serpent-mound-q968802.c_15ff865e5f3d8ddb - Serpent Mound by William Jacob Baer
- serpent-mound-q968802.c_2c260a03d1f8df1c - SD35 Serpent Mound, Squier & Davis Plate XXXV
- serpent-mound-q968802.c_52dfe1fc979edf2c - Harper's New Monthly Magazine, vol 104
- serpent-mound-q968802.c_7b01a4bb50d68b56 - 26 of A School History of the United States
- serpent-mound-q968802.c_8ebd42607fbb96d8 - 26 of A School History of the United States (2nd copy)
- serpent-mound-q968802.c_dd2c553d611e610b - 26 of A School History of the United States (3rd copy)

## Notes
- serpent-mound carries the site's one hand fit (n0210_1) on the map; its 7 agent docs are all
  orphans. The hand doc is never touched and its overlay stays whatever this audit decides about
  the agent docs.
