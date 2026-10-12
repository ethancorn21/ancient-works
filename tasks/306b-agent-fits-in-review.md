Status: open
# 306b: Look at the agent fits that sit in review items - 21 docs, 10 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 21
platefit documents with `by: agent` whose plan is a candidate of the site's review item (the doc
is in the store, but the site's overlay is not built - the fit never reached the map). Render
each the way a visitor would see it if the page showed it: the fit tool over the aerial
photograph, and over the LiDAR relief where the site has a `relief.jpg`, with the DOC's stored
pairs placed. For these 21 the doc's pairs DIFFER from the review item's candidate pairs (the
review tab would pre-place the item's version instead - only castle-neroche n0110_1 matches), so
the verdict must say which placement was looked at.

## Acceptance criteria
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief where the site has one), taken with `tools/shot.mjs` against `server/serve.py
      --port 0` on this checkout (recipe in the parent's Hand-over; GET only, ephemeral port).
- [ ] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on and the verdict, noting where the
      review item's own version of the placement differs (it is what the review tab shows the
      owner today).
- [ ] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (replacing/sitting beside the
      item's own candidate for the same plan as `fit/review.py upsert_item` does), the document
      is deleted, and the site's review page file is re-exported scoped to the site
      (`fit/review.py export --site` semantics, as tools/site_done.py does - never another
      site's item file). The site stays covered (an open item counts in the union check). A fit
      that sits right stays where it is, and its line says so.
- [ ] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (21, 10 sites)
- argentoratum-q2361353.c_191c6221a81caad0 - Plan de Strasbourg, réduit (d'après Villot)
- argentoratum-q2361353.c_436bea5010beea89 - Strasbourg-Krutenau-Plan de 1852 (12)
- argentoratum-q2361353.c_5badc8c867ef5d98 - Plan Strasbourg projet Conrath 1880
- argentoratum-q2361353.c_5bfb0472f266c056 - 1831. Strasbourg (Tirage avec changement)
- argentoratum-q2361353.c_6acfd94dec8c011b - 91 of Strassburg und seine Bauten
- argentoratum-q2361353.c_87dc28a9645f0e59 - Strasbourg-Krutenau-Plan de 1852 (15)
- argentoratum-q2361353.c_8bdbed9b69d51319 - Plan mur et tours Argentoratum
- argentoratum-q2361353.c_b3533cd48dfc6452 - Strasbourg-Krutenau-Plan de 1852 (13)
- argentoratum-q2361353.c_e882645cc479c889 - Plan topographique de la Ville de Strasbourg, 4 cantons
- argentoratum-q2361353.c_ec1930f8ba9bbabb - Strasbourg plan 1870
- carisbrooke-castle-q328595.c_c280ff908ad8318d - Carisbrooke Castle, Mackenzie 1897 (UK)
- castle-neroche-q5050201.c_44529cdbe2d10a9c - Castle Neroche Somerset Map (UK)
- castle-neroche-q5050201.earthworkenglan01allcgoog_n0110_1 - Castle Neroche, Somerset (Allcroft 1908)
- castra-lemanis-q499898.c_be12fb0f9a87000b - Plan Portus Lemanis (UK)
- cawthorne-camp-q5055239.earthworkenglan01allcgoog_n0325_1 - Cawthorn Camps, Pickering, Yorks (UK)
- cenabum-q2710144.c_e73dc8c09b2fea43 - Plan général de la ville et des environs en 1828 (France)
- dudley-castle-q5311832.c_e66ec095ee45aed0 - 45 of An Illustrated Guide to Dudley Castle (UK)
- ferme-d-azincourt-q20669811.c_804aa7af3eb2ac7c - Azincourt - cadastre de 1810 (France)
- watson-brake-q2552689.c_5e7bb19c79b509ed - Watson Brake - Map (US)
- watson-brake-q2552689.c_b52ddcad2ee295c4 - Watson Brake Mounds - Map (US)
- zwolle-q793.c_f9cddae6b944a648 - Zwolle, town plan by Jacob van Deventer (Netherlands)
