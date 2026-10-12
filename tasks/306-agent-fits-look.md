Status: split
# 306: Look at every agent-placed fit on the page - none reaches the map unseen
Depends on: 303
Touches: data/db/platefits/, data/review/, web/data/sites.json, web/data/review.json, web/data/sites/, docs/site_flow.md, docs/site_flow/

## Goal
Low residuals do not prove a fit is in the right place: Stonehenge's fabricated fits had 0-44 m residuals and sat
2-3x too big. Shotwick (206, `by: agent`) is on the map with 14-19 m residuals and nobody has looked at it.
Every fit not placed by the owner gets looked at the way a visitor sees it before it stays on the map.

## Acceptance criteria
- [ ] Every platefit document with `by` other than "hand" is opened in a browser over the aerial photograph (and the
      LiDAR where there is some), one screenshot each in docs/site_flow/agent_fits/, with one line each in
      docs/site_flow.md: what the drawing's lines sit on (the real banks, walls, ditches) and the verdict.
- [ ] A fit whose drawn works visibly miss the real ones (wrong size, shifted, rotated) leaves the map: its picture goes
      to the site's review item with the reason, the document is removed, and the site's entry is rebuilt with
      tools/site_done.py. A fit that sits right stays, and says so.

## Notes
- Do not change any `by: hand` document. Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over
(2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
context limit before the subtask files could be written; see the next-step below.)

**State.** No files of this task touched yet. Full inventory of the 112 non-hand docs
(`by` values in the store: 112 `agent`, 21 `hand`; all 112 point at built sites -
`test_platefits_docs_match_sites` passes in this checkout) - classified by what a visitor sees:

- **A: ON-MAP (23 docs, 12 sites)** - the doc's overlay is built in `web/data/sites/<site>/depictions.json`
  (`fit.doc` == the doc id): aldenhaag-q23650779.c_71c4ef3170b44288; alligator-effigy-mound-q4732645.
c_618a6be74dfaff32; avaricum-q281826.c_d457524470ca0ab3; barnard-castle-q4185811.c_eacf8c673afcd863;
  barwick-in-elmet-castle-q4865964.c_81c1ff143a862ee7; bethlehem-q2523914 x12 (c_075db5049e2fb635, c_1c20017970e54a01,
  c_5ce1836b12e8e294, c_67ed5d45466db19e, c_7ee79582ebdab559, c_993872ffecfce2cf, c_a164ee440558d66c, c_a42a93d9589acd4d,
  c_a8499553451a203c, c_ba63da7d782b9648, c_d624c308cd860a1e, c_fc4566d6947287f4); binche-q95121.c_957d7ce2933eb332;
  bolsover-castle-q2968590.c_5531262b52faaea8; burlington-house-q225471.c_17e8fb3cf9037e19;
  forthill.b24849959_n0269_1; newark.ArcheologicalAtlasOfOhio_n0098_1; shotwick-castle-q7502621.c_e6e5490609414bb9.
- **B: REVIEW (21 docs, 10 sites)** - the doc's plan is a candidate of the site's review item (no overlay):
  argentoratum-q2361353 x10 (c_191c6221a81caad0, c_436bea5010beea89, c_5badc8c867ef5d98, c_5bfb0472f266c056,
  c_6acfd94dec8c011b, c_87dc28a9645f0e59, c_8bdbed9b69d51319, c_b3533cd48dfc6452, c_e882645cc479c889, c_ec1930f8ba9bbabb);
  carisbrooke-castle-q328595.c_c280ff908ad8318d; castle-neroche-q5050201 (c_44529cdbe2d10a9c +
  earthworkenglan01allcgoog_n0110_1); castra-lemanis-q499898.c_be12fb0f9a87000b; cawthorne-camp-q5055239.
  earthworkenglan01allcgoog_n0325_1; cenabum-q2710144.c_e73dc8c09b2fea43; dudley-castle-q5311832.c_e66ec095ee45aed0;
  ferme-d-azincourt-q20669811.c_804aa7af3eb2ac7c; watson-brake-q2552689 (c_5e7bb19c79b509ed + c_b52ddcad2ee295c4);
  zwolle-q793.c_f9cddae6b944a648.
- **C: ORPHAN (68 docs, 47 sites)** - in the store, no overlay, not in any review item (invisible to visitors):
  US (15): cahokia-q333661.annualreportofbu1218901891smit_n0200_1; etowah-indian-mounds-q4533107.
  annualreportofbu1218901891smit_n0386_1; fort-ancient-q5470727.b24849959_n0264_1; hodgen-s-cemetery-mound-q5876069
  (ArcheologicalAtlasOfOhio_n0092_1, b24849959_n0353_1); marietta.b24849959_n0195_1; mound-cemetery-q6919104.
  annualreportofbu1218901891smit_n0563_1; mount-horeb-earthworks-complex-q6921321.c_d1dff07f0da57b0e;
  pyramid-mound-q7263260.ancientmonuments00squi_n0134_1; serpent-mound-q968802 (b24849959_n0313_1, c_15ff865e5f3d8ddb,
  c_2c260a03d1f8df1c, c_52dfe1fc979edf2c, c_7b01a4bb50d68b56, c_8ebd42607fbb96d8, c_dd2c553d611e610b).
  UK (35, sites in alphabetical order 1 doc each unless noted): bury-castle-q5001077.c_de779031cda8a0dc;
  cassiobury-house-q5049456.c_3446adfe7a8ed6c7; chevening-q1070927.c_6049b89e4ab0570c; cooling-castle-q5167493.
c_7ebc7630f3197364; coria-q3819299.c_d66bfb0db805d2cd; daw-s-castle-q5242247.c_8d2281628567a166;
  desborough-castle-q5263651.earthworkenglan01allcgoog_n0465_1; devil-s-dyke-q3307343.earthworkenglan01allcgoog_
n0662_1; duffield-castle-q2073299.c_e915cbfd3af009b4; eaton-socon-castle-q5331372.c_beefc3808de9b125;
  framlingham-castle-q2524183.c_f43bc6196e097819; goodrich-castle-q5583571.c_cd89cb69f385859b; gurnard-s-head-
  q5620199.earthworkenglan01allcgoog_n0262_1; hardknott-roman-fort-q1584994.c_7dcdfcc9aceb62ec; herstmonceux-castle-
  q2652207.c_8eb122e93e31c3f6; king-arthur-s-round-table-q283800.c_cfc493f72253fa8e; leicester-castle-q6519156.
c_581a9f82b6a805a0; ludlow-castle-q576369.c_b24730fd9038ae4a; offa-s-dyke-q1127343.c_1cca85e7b4b5a89e;
  okehampton-castle-q1419982.c_0edd7f87db67ff20; old-sarum-q782719 (c_041083ec68b532f8, c_ff62c9585a92b375); oxford-
  castle-q2600886.c_ba6b308580428184; pilsbury-castle-q7194511.c_7ff765c177ca7bae; pontefract-castle-q1949590
  (c_3213330a52fe6018, c_d135fb32326df430); portus-adurni-q762664 (c_42bedb90fffce1d4, c_4912bb54aa79f3ea); raby-
  castle-q4583646.c_fe1d6c7f0ba858cb; richborough-roman-fort-q1309736.c_edad7da41d234534; stanton-drew-stone-circles-
  q1516300.c_59a5c636a9e00703; taunton-castle-q7688781.c_05cb4a02bd58e82e; windmill-hill-q4348373.
  earthworkenglan01allcgoog_n0558_2; york-castle-q80637 (c_8dac5aacd73916b8, c_a7db545536f13e24).
  Continental (17): de-thombe-q2359601.c_b438f78e39a1aaec; durocortorum-q4896307 (c_08d995eb23a685c2,
  c_262c52de83d336bf, c_369f6580712b35a7, c_a60f570e6ce08f39); fletio-q2072212.c_80f1e15c04bc5035; gouda-q84125.
c_ba646ea988fc6bc8; traiectum-q2199749 (c_437d1d60e38020f7, c_5d442b3b66839fa3, c_6713f5e6c6b11f1f,
  c_8a2055d5929c4c5d, c_94f82fd629d1ed30, c_a65b37aa773876a5, c_e5e4b5c0234373cb); uxellodunum-q1290232
  (c_bafa9634c5b30b62, c_f9dcb2863628ff11); venlo-q9777.c_4fb122992c1574b2.

Re-derive any list with: overlay == a plan/view depiction in web/data/sites/<site>/depictions.json whose
`fit.doc` == "<site>.<plan>"; review == a candidate with that `plan` in the site's data/review/*.json item;
else orphan. (A throwaway python script did this; ~2 min to rewrite.)

**Machine facts (all verified this session).** (1) THIS VM HAS INTERNET: Esri World_Imagery returns 200 in
0.17 s - the "no internet" pitfall applies only to the no-network test runs; a headless page on this machine
shows the real aerial (docs/site_flow/argentoratum.png is the proof, 2026-10-11). (2) LiDAR relief on the page
is the per-site prebuilt `web/data/sites/<site>/relief.jpg` (index.html L367-368), NOT the live /tiles/relief
(that one is off here, `aw` Mac-only); shotwick has no relief.jpg (aerial-only) - every other site in the list
above has one (checked via file existence). (3) The fit tool renders a saved placement headless: after boot,
`select(site)` -> `setGround('imagery'|'relief', site)` -> `startFit(site)` -> `openPlan(row)` (row = the
plans.json row or the doc's own fields as a synthetic row, as web/review.js rvResolveRow does) and once `P.img`
is loaded push `{u,v,lon,lat}` for each of the doc's pairs + `addPairMarker(p)` + `refit()` - `refit()` draws the
fitted plate as the map source `fit-prev` and the status line shows residuals (review.js does exactly this for
item pairs; L142-146, L189-196). On-map docs are instead shown the visitor's way: open the site and activate the
depiction button (applyDep). Drive with `tools/shot.mjs <url> <out.png> <waitMs> 1440 900 '<IIFE doing all this>'`
(NODE_PATH=/home/agent/tools/shot/node_modules; serve the tree once with `server/serve.py --port 0` - ephemeral
port, GET-only, safe for parallel checkouts). (4) All four spot-checked raw images serve through the data/raw
symlink (books full/ + commons thumbs). (5) B-group: the doc's stored pairs DIFFER from the review item's
candidate pairs for all 21 except castle-neroche n0110_1 (the visitor of the review tab would see the item's
version) - audit the DOC's own pairs (that is the document), note in the verdict where the item's differ.
(6) All 112 docs carry 4+ pairs, so every one renders as a fitted plate (simFit needs 3). (7) sites.json `drawings`
are STALE for most A-group sites (0 despite the overlay present; only aldenhaag=1, forthill=2, newark=2 are
non-zero) - box 2's "rebuild with tools/site_done.py" fixes the counts for a site whose doc we delete; the line's
sync step rebuilds depictions.json (dropping the deleted doc's overlay) and set_drawings refreshes the count.
(8) Removal recipe for a wrong fit: upsert the picture into the site's review item with the reason
(fit/review.py upsert_item, as 300/303's fabrication path does), delete the doc file, run
`.venv/bin/python tools/site_done.py <site>` (verify the big picture is already cached in data/raw/commons/big/
before the run so no download lands in the shared raw dir).

**Tests.** Last run this session: `.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py` =
123 passed, 1 skipped (198 s) in this checkout; test_gate's failure is the pre-existing driver-baseline red
(see PROGRESS loop-start notes) - not mine. The driver's newest loop-start note (2026-10-11, 1 red) matches:
note the reports/ files under .agent/reports/ can be stale, I ran the suite myself.

**NEXT STEP (this session died at the context limit before writing the split):** create the six subtask files
- 306a agent-fits-on-map (the 23 A docs; highest priority: they are ON the map), 306b agent-fits-in-review
  (21 B docs), 306c orphan-fits-us (16, incl. marietta), 306d orphan-fits-uk-1 (bury..ludlow, 18),
  306e orphan-fits-uk-2 (offa..york, 17), 306f orphan-fits-continental (17) - each `Status: open`, NO `Depends on:` pointing at the
parent (that deadlocks; the driver hands them out in a-f order), a `Touches:` line (docs/site_flow.md,
docs/site_flow/ for all; 306a adds data/db/platefits/, data/review/, web/data/sites.json, web/data/review.json,
web/data/sites/ because it may remove wrong fits; the others keep the doc set as-is, verdicts only), each
listing its exact docs above, each with the acceptance: one screenshot per doc in docs/site_flow/agent_fits/
(named <site>_<plan>.png) over the aerial (and the LiDAR relief where the site has relief.jpg) + one line per
doc in docs/site_flow.md (a table under a new "## The agent fits, looked at (task 306)" section: doc, what the
lines sit on, verdict stays/leaves + reason). 306a alone performs the removals (box 2). Set the parent to
`Status: split` with this Hand-over as the plan, commit, done. Then 306a starts: build the shot.mjs IIFE driver,
serve --port 0, audit the 23, act on the wrong ones.

(2026-10-12, iteration 135, agent c - SPLIT COMPLETED; 306a audit run started.) The split is now complete:
306a/306b/306c/306d/306e/306f all exist. Count corrections vs the plan above (re-derived from the live
store, method in the inventory note): 306c US is 16 docs (the plan's 15 dropped marietta.b24849959_n0195_1,
a US site - it is in 306c); 306e UK part 2 (o-y) is 17 docs, not 15 (old-sarum x2, pontefract x2,
portus-adurni x2, york-castle x2). Total 23+21+16+18+17+17 = 112. This hand-over is the source of truth
for the counts. 306a (me, iteration 135): the headless driver `tools/audit_306a.mjs` is built and running
(one `server/serve.py --port 0` for the whole run; per shot it opens the site the visitor's way -
select -> the doc's depiction selected -> setGround('imagery'|'relief') -> applyDep - and reports the
stored fit stats from depictions.json; 44 shots: 23 aerial + 21 relief, shotwick aerial-only). Next session:
check the full run finished, then judge in batches of ~8 docs (read the shots, decide, write the
docs/site_flow.md section - header + lines - and tick box 1), then the removals of the wrong fits (box 3)
and the count refreshes of the right ones (box 4).