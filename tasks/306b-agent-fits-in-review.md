Status: open
# 306b: Look at the agent fits that sit in review items - 21 docs, 10 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306b.mjs

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

## Hand-over
(2026-10-12, iteration 143, agent c - fifth session. 15/21 judged - ALL STAYS - and 15 lines written
into docs/site_flow.md; 6 docs left to judge, then their 6 lines, then boxes/tests. Session hit the
context limit right after the 15-line append landed; that edit is UNCOMMITTED - the harness keeps it,
commit it with the next work.)

**State.** Box 1 ticked (all 42 pngs present in docs/site_flow/agent_fits/ - 87 files total - and the
9 fit-queue-contaminated ones verified clean in the reshoot: placed:false, n:8, resid 0). In
docs/site_flow.md (now 891 lines) the 306b block is appended AFTER the last 306a line (bethlehem
c_fc4566d6947287f4; section header "## The agent fits, looked at (task 306)" starts line 702): a
short preamble (all 10 items resolved by my 21 docs today, tab shows nothing; each line's item-cand
clause = the version the tab would pre-place if/when the item reopens) + 15 lines, all STAYS:
argentoratum x10 (judged last session) + carisbrooke + neroche x2 + lemanis + cawthorne (judged this
session, from their clean reshoot shots; per-doc details are in the lines and in DECISIONS). No
removals so far - no miss among the 15 judged.

**This session's 5 verdicts (STAYS each).** carisbrooke c_c280ff (0.50 m/px, +16.2°): keep, both
gates, K. Charles prison, Tilt yard sit on the 1842 OS 6-inch first-edition's same-named features
(3783/5000 line inliers against that surveyed map; 0.50 within 20% of the plate's stated 0.415);
item cand = coarse 0.695 whose 8 hand-tied features (0.901 vs stated 0.415) the gate rejected. Neroche
c_44529 (0.86, +1.8): hachured hillfort - summit platform, ditches, NE Plantation - on the real hill
(aerial + relief); item cand fabricated grid-round 8/8. Neroche n0110_1 (0.39, -3.1): summit +
ditches + Castle Farm on the real summit/ditch ring/farm; 0.39 matches the plate's own 300-ft scale
bar (0.397); item pairs == doc pairs (offset 0 m - the only 306b doc whose versions agree) but the
gate flagged them a 1D-ladder pattern (placement verified on the image anyway). Lemanis c_be12fb
(0.76, +0.5): port quadrangle on the real headland slope above the sea, NE corner on the 1848
red-ink 'STVTFAE CASTLE / Roman port' identification, SW ('Cutle') on 'PORTVS LEMANIS (Site of)';
0.76 vs its 500-ft scale bar 0.726; item cand coarse 2.667 (median 63>45) = ~3.5x too big. Cawthorne
n0325 (0.30, +0.4): the three drawn camps on the real camps as the 1848 Squire & Davis map records
them (red-ink 'C A M P S' sits on anchor 6); 4625/4997 = 93% inliers against the LiDAR relief - the
strongest of the batch - and 0.30 = the plate's 300-ft scale bar; item cand (not coarse) 0.790 vs
scale bar 0.259 gate-rejected and 644 m north, off the 1848 camps.

**Judging technique that worked (reuse for the last 6).** (1) Earthwork sites: read the RELIEF shot
first (aerial is uniform there). (2) Scale trap check: measure the plate's own scale bar - PIL:
crop the plate's lower region 3x and read it (worked for lemanis/n0110_1/cawthorne); a doc whose
fitted mpx matches its scale bar (or stated scale) within ~20% is trustworthy, a gate rejection of
'stated X disagrees with its own points (Y)' means the DOC's near-stated fit is the one to believe.
(3) The 6-inch/1-inch/1848 red-ink maps are georeferenced ground truth (their labels sit on the real
features in the shots) - anchors landing on same-named red-ink labels = placement verified.
(4) Coarse item candidates store only 3-6 rectangle points (NOT the hand-tied feature points - those
names live in `why`), so don't compare feature positions between doc and item pairs; compare centers
+ scales + what the image shows.

**REMAINING: 6 docs (all shot clean; per-doc numbers below; full item-cand detail in
/tmp/306b_judge.md, [eval] mpx/rot in /tmp/audit_306b.log (c_5e7bb) and /tmp/audit_306b_reshoot.log
(the other five) - both persist in /tmp):**
- cenabum-q2710144.c_e73dc8c09b2fea43 - 1828 (score 9.3; resid 0.1-0.3, mpx 5.41, rot +1.1; matcher
  strong 2537/5000): item cand coarse median 161.9>45 WITH a 200-sheet conflict 'Epinal' Q173695
  ~350 km NE - the same red-herring pattern as argentoratum c_e882645 (sheet-level named place);
  check the plate (titled 'Cenabum' = Tours) lands on the real old Tours (site canonical point in
  web/data/sites.json), not Epinal. The mpx 5.41 is big - cross-check against the plate's scale
  statement if printed.
- dudley-castle-q5311832.c_e66ec095ee45aed0 - Illustrated Guide p.45 (score 2.5; 0 m, mpx 0.69,
  rot +24.9): item cand coarse 0.4379, features 33% textured; castle on the real castle rock?
- ferme-d-azincourt-q20669811.c_804aa7af3eb2ac7c - cadastre 1810 (score 4.7; 0-0.1, mpx 1.23,
  rot -1.5; WEAK 11/203 - judge image): item cand coarse 0.7246, stated 0.55 vs points 1.171;
  farm + battlefield ground.
- watson-brake-q2552689.c_5e7bb19c79b509ed - Watson Brake - Map (score 4.4; 0-0.1, mpx 1.28,
  rot -0.9): item cand coarse 0.625, stated vs points 1.448; mounds on the real earthworks -
  RELIEF decides.
- watson-brake-q2552689.c_b52ddcad2ee295c4 - Mounds - Map (score 2.2; 0, mpx 0.52, rot -1.6): item
  cand coarse 0.625, features 0% textured (strongest rejection of the batch) - RELIEF decides.
- zwolle-q793.c_f9cddae6b944a648 - van Deventer 1563 (score 10.2; 0-0.1, mpx 2.53, rot -6.2): item
  cand coarse 1.5625, features 38% textured; 16th-c town plan on the real medieval core (note
  zoom 14.82 = the 2000 m site span).

**NEXT STEP (in order).** (1) Judge the 6 (read their pngs: docs/site_flow/agent_fits/
<site>_<plan>.png + _relief.png; relief first for watson-brake x2 and any earthwork). (2) Append
their 6 lines to the END of the 306b block in docs/site_flow.md (the block currently ends at the
cawthorne line; same format, in this doc order). (3) Any miss goes the 303 way: fit/review.py
upsert_item('.', <site>, [full doc record + `why`]) - it replaces the item's same-plan candidate in
place; `rm data/db/platefits/<doc>.json`; site-scoped re-export = fit/review.py `export` with the
site id (as tools/site_done.py does internally) - NEVER run tools/site_done.py on these 10 sites
(206 trap: its fit phase places a new unaudited fit). Deleting a site's LAST doc reopens its item
(union-safe: item files always exist; all store docs of the 10 sites are my 21; no by:hand). (4)
Tick boxes 2/3 (box 3: if all 6 stay it is satisfied - no removals, lines say so) and box 4, then
run the suite: `.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py` (baseline at 306a's
done commit 4ca9e2c: 128 passed, 1 skipped, test_gate pre-existing red; the only test touching
site_flow is test_fit_queue.py - queue docs, not these lines - so the append broke nothing; if a
deletion breaks a test pinning a removed doc, grep tests/ for the doc id and re-point at a
surviving doc - never loosen). (5) Status: done, commit.

**If you ever re-shoot** (should not be needed): `node tools/audit_306b.mjs <doc-id>` - the fixed
driver (307 trap: waits FQ.loaded, empties FQ.entries before openPlan, reports fqEntries/placed/
anchor in [eval]); check placed:false, n:8 in the log.
