Status: done
# 306b: Look at the agent fits that sit in review items - 21 docs, 10 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306b.mjs, PITFALLS.md, DECISIONS.md

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
- [x] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief where the site has one), taken with `tools/shot.mjs` against `server/serve.py
      --port 0` on this checkout (recipe in the parent's Hand-over; GET only, ephemeral port).
- [x] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on and the verdict, noting where the
      review item's own version of the placement differs (it is what the review tab shows the
      owner today).
- [x] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (replacing/sitting beside the
      item's own candidate for the same plan as `fit/review.py upsert_item` does), the document
      is deleted, and the site's review page file is re-exported scoped to the site
      (`fit/review.py export --site` semantics, as tools/site_done.py does - never another
      site's item file). The site stays covered (an open item counts in the union check). A fit
      that sits right stays where it is, and its line says so.
- [x] No `by: hand` document is touched; no new test failures against the driver's newest
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

## Hand-over
(2026-10-12, iteration 145, agent c - SEVENTH session, task DONE. All boxes ticked, committed.)

**Result.** 21/21 docs STAYS, zero removals: no `fit/review.py upsert_item`, no doc deletion, no
site re-export - the 303-way removal path (box 3) was never needed. All 21 verdict lines are in
docs/site_flow.md's "## The agent fits, looked at (task 306)" section (the 306b block, preamble +
21 lines, after 306a's last line bethlehem c_fc4566d6947287f4); the preamble's stale "All fifteen
judged so far stay" was corrected to "All twenty-one stay (2026-10-12: judged from the 42 shots,
none removed)". 42 shots in docs/site_flow/agent_fits/ (2 per doc: aerial + relief; the 9
fit-queue-contaminated ones re-shot clean via the driver fix). Every doc is `by: agent`; the
branch has no diff under data/ or web/data/ vs main (verified `git diff --stat main..agent/c`);
no by:hand doc touched. Suite green at the 306a-done baseline: 128 passed, 1 skipped in 204 s
(`.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py`; test_gate excluded,
pre-existing red per the driver's loop-start note).

**PITFALLS filed (5)** so 306c-f (the orphan subtasks the parent 306 returns after this one) do
not re-discover them: (1) corrected the stale "the machine has no internet" sentence in the Esri
entry - this VM HAS internet (tile 200 in 0.2 s, re-verified this session); (2) extended the
Nominatim entry (plain `curl -H 'User-Agent: ...'` works, not only commons.get; `/search` 400s
without a `q`); (3) new web/ entry - `web/data/sites/<site>/` survey layers (etatmajor, cassini,
tmk1850, fr_ortho1950) are site-sized georeferenced blocks, 1 px = 1 m for sites <= 2400 m
across, centred on the site point (pipeline/depict.py `build`/`sample_xyz`; `depictions.json`
`corners` give the block's [lon,lat] corners) - ideal local ground truth for judging fits with
no network; (4) new web/ entry - driving the fit tool headlessly with your own pairs: a fitqueue
entry for the opened plan seeds 5 anchor pairs into the least squares (fitkit.js `_fkActivate`);
empty `FQ.entries` before `openPlan` and check `placed`/`n` in the shot log; (5) new
`### data/sites.json (site points)` subsection - a site's canonical point can be a real modern
city (cenabum-q2710144 at (1.909, 47.9025) IS Orléans; my 2.09°E memory was wrong): reverse-
geocode the site's own point before judging placement.

**For 306c-f.** `tools/audit_306b.mjs` is site- and queue-independent (doc-id positional args;
it waits for `FQ.loaded` and empties `FQ.entries` before `openPlan`): reuse it verbatim as the
orphan-audit driver, `node tools/audit_306b.mjs <doc-id> ...` against `server/serve.py --port 0`
(ephemeral port, GET-only - parallel-checkout safe). Orphan docs have NO review item, so their
verdict lines note "no review item - not shown to the owner at all" instead of an item-cand
comparison. Judging technique that settled the 306b scale questions: measure the plate's OWN
scale bar (PIL: crop the plate's lower region at 3x and read it); a doc whose fitted m/px
matches its scale bar/stated scale within ~20% is trustworthy. /tmp materials may persist:
/tmp/306b_judge.md, /tmp/audit_306b.log, /tmp/audit_306b_reshoot.log.
