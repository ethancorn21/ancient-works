Status: open
# 306f: Look at the orphan agent fits, continental - 17 docs, 7 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 17
continental-Europe platefit documents with `by: agent` (Netherlands, France; the Marietta works
is US and sits in 306c) that are ORPHANS - in the store, but with no overlay built on the site
and not referenced by any review item, so a visitor sees them not at all. Render each the way
the page would if it ever showed it: the fit tool over the aerial photograph, and over the LiDAR
relief where the site has a `relief.jpg`, with the doc's stored pairs placed. The verdict
records where the doc stands today (invisible) and whether the placement is good enough to keep.

## Acceptance criteria
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief where the site has one), taken with `tools/shot.mjs` against `server/serve.py
      --port 0` on this checkout (recipe in the parent's Hand-over; GET only, ephemeral port).
- [ ] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on (the real banks, walls, ditches,
      streets) and the verdict (keeps its document / deleted - and it is an orphan today,
      invisible on the page).
- [ ] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (`fit/review.py upsert_item`
      pattern), the document is deleted, and the site's review page file is re-exported scoped
      to the site (never another site's item file). The site stays covered for the union check
      (an open item counts). A fit that sits right keeps its document, and its line says so.
- [ ] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (17, 7 sites)
- de-thombe-q2359601.c_b438f78e39a1aaec - Maastricht map detail: De Tombe & southern pontoon bridge, 1632
- durocortorum-q4896307.c_08d995eb23a685c2 - Plan-Reims-Bas-Empire
- durocortorum-q4896307.c_262c52de83d336bf - MoSaïque archeveche 41825
- durocortorum-q4896307.c_369f6580712b35a7 - MoSaïque rue Jacquart 41825
- durocortorum-q4896307.c_a60f570e6ce08f39 - Plan monumental de Reims et ses caves de champagne, 1894
- fletio-q2072212.c_80f1e15c04bc5035 - Atlas de Wit 1698, pl 033, Weesp
- gouda-q84125.c_ba646ea988fc6bc8 - Gouda, town plan by Jacob van Deventer
- traiectum-q2199749.c_437d1d60e38020f7 - Plan van de Bataille Laefelt (estampe)
- traiectum-q2199749.c_5d442b3b66839fa3 - Traiectum (1 of 2)
- traiectum-q2199749.c_6713f5e6c6b11f1f - Traiectum ad Mosam. Maestricht (1 of 2)
- traiectum-q2199749.c_8a2055d5929c4c5d - Atlas Beudeker: Traiectum ad Mosam
- traiectum-q2199749.c_94f82fd629d1ed30 - Traiectum ad Mosam (2 of 3)
- traiectum-q2199749.c_a65b37aa773876a5 - Maastricht 1749 (detail Vrijthof & 1e stadsmuur)
- traiectum-q2199749.c_e5e4b5c0234373cb - Atlas Beudeker: Traiectum ad Mosam, Bouillonstraat
- uxellodunum-q1290232.c_bafa9634c5b30b62 - Plan et vue du Puy d'Issolu
- uxellodunum-q1290232.c_f9dcb2863628ff11 - Plan geometrique du puy d'Issolus (Uxellodunum)
- venlo-q9777.c_4fb122992c1574b2 - Venlo, town plan by Jacob van Deventer
