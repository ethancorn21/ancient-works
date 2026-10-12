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

## Hand-over
(2026-10-12, iteration 142, agent c - fourth session. All 42 shots done and clean; argentoratum (10/10 docs) judged; 11 docs left to judge, then lines, then removals, then tests.)

**State of the audit run.** Both runs finished: the original 42-shot run (pid 3719656, log
/tmp/audit_306b.log) completed this session, and the 9 queue-contaminated docs were re-shot with
the FIXED driver (log /tmp/audit_306b_reshoot.log, "all shots written"). docs/site_flow/agent_fits/
has 87 files (306a's 45 + my 42). No failures in either log (only transient Esri tile aborts).

**The 307 trap (discovered + fixed this session - the key fact).** web/fitkit.js (agent a's 307,
NOT mine to edit) pre-places a machine candidate whenever web/data/fit_queue.json carries a queue
entry that proposes the same site's plan: `_fkActivate` clears pairs, seeds 5 anchor pairs from
the entry's `propose`, sets P.placed. My 8 doc pairs then push on top -> a 13-point least squares
blends the queue's anchor with the doc's pairs, and the preview ink + fithint show the BLEND, not
the document. 9 of my 21 docs match a queue entry: c_436bea, c_c280ff, n0110_1, c_be12fb, n0325,
c_e66ec, c_804aa7, c_b52dd, c_f9cdda (the other 12 were clean: n=8, resid ~0). FIX (in MY driver
tools/audit_306b.mjs, uncommitted - the harness keeps it): the IIFE waits for FQ.loaded then does
`FQ.entries.length = 0` before openPlan (fitkit finds no entry and falls open); the [eval] line
now reports `fqEntries` (count before emptying - 114 in the reshoot), `placed`, `anchor`. All 18
reshoots verified clean: placed:false, anchor:false, n:8, resid all ~0 (each now shows the doc's
own transform; mpx/rot per doc are in the reshoot log's [eval] lines). If you ever re-shoot, run
`node tools/audit_306b.mjs <doc-id>` (idempotent: rm the doc's two pngs first).

**JUDGING - argentoratum done (10/10, ALL STAYS).** The section "## The agent fits, looked at
(task 306)" of docs/site_flow.md starts at line 702; the last 306a line is bethlehem fc4566d6947287f4
at line 800 (file is 800 lines) - APPEND below it. My lines are NOT written yet (session hit the
context limit in the middle of judging). All 10 argentoratum docs STAY, per-doc (fit stats = the
doc's own transform from the [eval] lines; "item cand" = the item's coarse candidate that the
review tab WOULD show - today all 10 items are RESOLVED by my docs, so the tab shows nothing):
- c_191c6221a81caad0 (Villot 1833 réduit, score 7.8; resid 0.0-0.1, mpx 2.17, rot -32.3): star-fort
  ring + street grid on the real town, etatmajor ink (the 19th-c survey, still the visible texture)
  follows it. Verified twice (iter 141 + this session's reshoot-free original shots). Item cand:
  coarse anchor, median resid 54.8>45 rejected.
- c_436bea5010beea89 (1852 Krutenau (12), 4.3; reshoot: resid 0, mpx 0.55, rot -36.3): the Krutenau
  island district - Ill running through the plate's middle, Porte des Pêcheurs top, dense 1852
  streets - sits on the real eastern old town; the red plate lands on the real streets and its Ill
  on the real river (aerial + relief). Same 1852 survey as (13)/(15); the three crops' placements
  agree (centres 7.75274/7.75375/7.75374). Item cand: coarse, median 133.4>45.
- c_5badc8c867ef5d98 (Conrath 1880, 9.2; 0.1-0.2, mpx 4.03, rot 1.6): old town + star fort ring on
  the real core/ring; item cand coarse, median 122.7>45.
- c_5bfb0472f266c056 (1831 Villot redrawn, 10.0; 0.0-0.2, mpx 2.99, rot -32.1): same source as
  c_191c; item cand REJECTED AS FABRICATED (grid-round 10/10 anchors, gate 0.0 - the item's own
  version is a fabrication, the doc's is the real fit).
- c_6acfd94dec8c011b (Strassburg und seine Bauten p.91, "Argentoratum nach v. Appell" 1894, 1.8;
  0.0, mpx 0.62, rot 32.2): the Roman castrum (wall rectangle, Decumane/Kreuzgasse grid, cathedral
  inside, Ill south) on the real built-up core, grid on the real streets; agrees with c_8bdbe's
  independent 1775 wall drawing at the same place. Item cand coarse, median 47.8>45.
- c_87dc28a9645f0e59 (1852 (15), 4.6; 0.0-0.1, mpx 0.99, rot -36.3): Krutenau strip on the real
  eastern old town; item cand coarse, median 78.8>45.
- c_8bdbed9b69d51319 (1775 "Plan mur et tours" Weiss, 2.5; 0.0, mpx 0.55, rot 39.0): Roman wall
  with towers + hatched interior blocks (cathedral etc.) on the real core; item cand coarse,
  median 65.8>45.
- c_b3533cd48dfc6452 (1852 (13), 4.9; 0.0, mpx 0.58, rot -35.3): third crop of the same 1852
  survey; item cand coarse, median 101.6>45.
- c_e882645cc479c889 (1819 "quatre Cantons", 9.0; 0.0-0.1, mpx 2.56, rot -10.7): the 1819
  star-fort line on the real ring (today's park ring) around the core. THIS IS THE RECORDED
  RESOLVER of the argentoratum item - verified right, so the item stays resolved by a real fit.
  NOTE for the line: its item candidate carries a 200-evidence CONFLICT ("Ville" Q1165252, ~350 km
  west near Paris) - a sheet-level red herring (the plate is titled "Strasbourg", placement
  verified); the doc matcher was weak (32/1822 inliers) - judged on the image, which is right.
- c_ec1930f8ba9bbabb (1870 Villot "le Plan général ... 1870", 8.7; 0.1, mpx 2.23, rot -32.3):
  four-canton plan, fort line on the real ring; item cand rejected (features 38% textured).
Line format (306a's): `<doc id> - <source>, <fit kind> (<score>, <mpx>, <rot>): what the lines
sit on. STAYS.` - plus the item-version note (one short clause each: what the item's own candidate
was and why it was rejected). Consider one short preamble line for the 306b block: all 10 items
are resolved by my docs, so the review tab shows nothing for these sites today; the item-version
clause is what it would show when/if the item reopens.

**REMAINING: judge 11 docs (all reshoot-clean; images in docs/site_flow/agent_fits/, mpx/rot from
/tmp/audit_306b_reshoot.log, doc-matcher + item-cand detail in /tmp/306b_judge.md - both persist
in /tmp across iterations).** Earthwork sites: judge the RELIEF image first (the aerial is often
uniform there; 306a precedent - forthill). Per doc: read the pngs, write its line, REMOVED ones go
the 303 way (below). The 11 (doc: mpx/rot of the doc's own fit; item cand = what the tab would
show):
- carisbrooke-q328595.c_c280ff908ad8318d (Mackenzie 1897, 3.0; 0.5/16.2; weak-ish 3783/5000 inliers;
  item cand coarse 0.695, stated scale 0.415 vs points 0.901, hand_tied evidence; castle site -
  moat/court on the real castle? the doc centre (-1.31198,50.68765) is ~140 m from the item's)
- castle-neroche-q5050201.c_44529cdbe2d10a9c (Somerset Map, 3.6; 0.86/1.8; WEAK 52/98 - judge image;
  item cand REJECTED AS FABRICATED grid-round 8/8)
- castle-neroche-q5050201.earthworkenglan01allcgoog_n0110_1 (Allcroft 1908, 6.5; 0.39/-3.1; WEAK
  15/26 - judge image; THE ONLY doc whose item pairs EQUAL the doc's (offset 0 m); item cand
  REJECTED AS FABRICATED 1D-ladder)
- castra-lemanis-q499898.c_be12fb0f9a87000b (Plan Portus Lemanis, 2.0; 0.76/0.5; WEAK 15/25 - judge
  image; item cand coarse 2.667, median 63>45; Roman port at Dover - fort on the real headland?)
- cawthorne-q5055239.earthworkenglan01allcgoog_n0325_1 (Pickering, 2.2; 0.3/0.4; STRONG 4625/4997
  over relief.jpg; item cand NOT coarse: scale-bar 0.259 vs points 0.790; enclosure rings on the
  real triple camp?)
- cenabum-q2710144.c_e73dc8c09b2fea43 (1828, 9.3; 5.41/1.1, clean n:8; item cand coarse 161.9>45
  WITH CONFLICT "Epinal" Q173695 ~350 km NE - same red-herring pattern as c_e8826? plate titled
  "Cenabum" (Tours) - check it lands on the real old Tours, not Epinal)
- dudley-q5311832.c_e66ec095ee45aed0 (Illustrated Guide p.45, 2.5; 0.69/24.9; item cand coarse
  0.4379, features 33% textured; castle on the real castle rock?)
- ferme-d-azincourt-q20669811.c_804aa7af3eb2ac7c (cadastre 1810, 4.7; 1.23/-1.5; WEAK 11/203 -
  judge image; item cand coarse 0.7246, stated 0.55 vs 1.171; Azincourt farm + battlefield ground)
- watson-brake-q2552689.c_5e7bb19c79b509ed (Watson Brake - Map, 4.4; 1.28/-0.9, clean n:8; item
  cand coarse 0.625, stated vs 1.448; mounds on the real earthworks? RELIEF decides)
- watson-brake-q2552689.c_b52ddcad2ee295c4 (Mounds - Map, 2.2; 0.52/-1.6; item cand coarse 0.625,
  features 0% textured - the strongest reject; RELIEF decides)
- zwolle-q793.c_f9cddae6b944a648 (van Deventer 1563, 10.2; 2.53/-6.2; item cand coarse 1.5625,
  features 38% textured; 16th-c town plan on the real medieval core? note zoom 14.82 = site
  span 2000 m)

**WRONG fits - the 303 way (do it only when the image proves a miss).** For a REMOVED doc D of
site S: (1) `review.upsert_item('.', S, [entry])` with entry = the FULL doc record plus `why` =
the audit reason (this REPLACES the item's same-plan coarse candidate in place - fit/review.py
upsert_item); (2) `rm data/db/platefits/<doc>.json`; (3) site-scoped re-export: the fit/review.py
`export` with the site id (as tools/site_done.py does internally - re-derives web/data/review.json
open list, touches ONLY that site's item file). NEVER run tools/site_done.py on these 10 sites
(206 trap: its fit phase would place a new unaudited fit). Deleting a site's LAST remaining doc
reopens its item (resolved_doc fallback - all store docs for these 10 sites are my 21, no by:hand);
deleting some keeps the item resolved by the rest. Coverage is union-safe no matter what
(fit/batch_eu.py union_check: covered by ANY doc OR ANY item file; upsert never deletes an item
file; the 10 item files always exist). Sites with multiple docs: argentoratum x10 (resolver
c_e8826 - deleting it re-points resolution to the next remaining doc, any one), neroche x2,
watson-brake x2; the other 7 sites have exactly 1 doc each - deleting it reopens the site's item
(it re-enters web/data/review.json with the upserted candidate - that IS the 303 outcome, like
306a's bethlehem). `by: hand` docs: none exist on these 10 sites - nothing to protect beyond my 21.

**Tests.** Not run yet this session (only png/driver changes so far; suite was green at 306a's
done commit 4ca9e2c: 128 passed, 1 skipped, test_gate pre-existing red). Due once the removals
(and any docs/site_flow.md lines) land: `.venv/bin/python -m pytest tests/ -q --ignore=tests/
test_gate.py`. If a deletion breaks a test that pins a removed doc (306a broke 5: mackenzie
doc_record, provenance source-line pins), grep tests/ for the doc id and re-point at a surviving
doc - do NOT loosen the tests.

**ACCEPTANCE BOXES.** None ticked yet. Box 1 (42 screenshots) is effectively DONE (verify all 87
files present: `ls docs/site_flow/agent_fits | wc -l` = 87) - tick it once you have; box 2 (21
lines) after all judging; box 3 after removals; box 4 (no by:hand touched - true by construction;
suite green) after the test run. Tick, set Status: done, commit.
