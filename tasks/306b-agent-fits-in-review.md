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
(2026-10-12, iteration 141, agent c - third session. Audit run in flight; judging-prep sheet
built; the resolution/coverage picture of the 10 items was discovered and verified.)

**State.** The audit run is alive: pid 3719656 (nohup, launched last session 13:46 CDT; its own
`server/serve.py --port 0` was on 44225 at launch). At 13:49 CDT this session: 12/21 docs
(24 pngs) done, ZERO failures - argentoratum x10 + carisbrooke written; next docs in flight:
castle-neroche x2, castra-lemanis, cawthorne, cenabum, dudley, ferme, watson-brake x2, zwolle.
~45-50 s/doc (the 22 s estimate was optimistic) -> ~20 min to finish. Log: /tmp/audit_306b.log.
docs/site_flow/agent_fits/ has 67 files now (306a's 45 + my 22); 87 expected at completion.

**NEXT STEPS (in order).**
1. `ps -ef | grep audit_306b` and `tail -20 /tmp/audit_306b.log`: if the process is alive, let it
   finish (or wait); if it died, just re-run `node tools/audit_306b.mjs` (idempotent: skips pngs
   that exist). Confirm all 42 of my pngs exist (2 per doc, _relief pair for all 10 sites).
2. JUDGE in batches, starting argentoratum (10 docs / 20 pngs - c_191c6221a81caad0 was visually
   validated last session: 1833 Villot plate fitted over the site's etatmajor ink, resid 0.0-0.1 m,
   mpx 2.17, rot -32.3, looks right). Per doc read both pngs, then APPEND its line to the END of
   docs/site_flow.md: section "## The agent fits, looked at (task 306)" starts at line 702, the
   file is 800 lines, the last line (800) is bethlehem-q2523914.c_fc4566d6947287f4 - append below
   it. Line format (306a's): `<doc id> - <source>, <fit kind> (<score>, <resid/mpx/rot>): what the
   lines sit on. STAYS.` / `... REMOVED (wrong place).` NOTE in the line where the item's own
   version of the same plan differs (the item's coarse candidate + its rejection `why` - the
   /tmp/306b_judge.md sheet has all of it; it is what the review tab would show when/if the item
   reopens; today the tab shows NOTHING for these 10 sites because all are resolved - see below).
3. Wrong fits: the 303 way (306a did it): `review.upsert_item('.', sid, [entry])` with entry =
   the FULL doc record + `why` = the audit reason (replaces the item's same-plan coarse
   candidate in place); delete `data/db/platefits/<doc>.json`; then site-scoped
   `review.export('.', sid)` (fit/review.py export with site_id - re-derives open list into
   web/data/review.json, touches only that site's item file). NEVER tools/site_done.py on these
   sites (206 trap: its fit phase would place a new unaudited fit). Right fits stay; their line
   says STAYS.
4. Tick the boxes, run `.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py`
   (baseline at 306a's done commit 4ca9e2c: 128 passed, 1 skipped, test_gate pre-existing red per
   the driver's loop-start note). If a deletion breaks a test that pins one of my 21 docs
   (306a broke 5: mackenzie doc_record, provenance source-line pins), search tests/ for the doc
   id first and re-point it at a surviving doc.

**Resolution / coverage facts discovered this session (all verified; the judging prep sheet
/tmp/306b_judge.md holds the full per-doc detail - /tmp persists across iterations):**
- ALL 10 item files have `resolved` recorded (write-once), and EVERY resolver is one of my 21
  docs (argentoratum: c_e882645cc479c889; each of the other 9 sites: its own doc). So none of
  the 10 sites is in web/data/review.json today (333 open items, file written 18:01 UTC) and the
  review tab shows nothing for them. The goal's "the review tab would pre-place the item's
  version" is a counterfactual - say so in the lines (the item's coarse candidate + its `why`).
- `resolved_doc` fallback (fit/review.py): deleting a doc reopens the item ONLY if no remaining
  candidate has a store doc. Every store doc for these 10 sites is one of my 21 (no `by: hand`):
  deleting a site's LAST doc reopens its item (306a precedent: bethlehem - all its docs removed,
  item open, it is in today's open list); deleting some keeps the item resolved by the rest.
- union check (fit/batch_eu.py union_check): a site is covered by ANY doc OR ANY item file (open
  or resolved). The 10 item files survive upsert/deletion -> my deletions never lose coverage.
- All 10 sites have ZERO depictions in web/data/sites/<site>/depictions.json - "the fit never
  reached the map" holds for all of them.
- Judge the IMAGE, not the stats, for 5 docs with weak matcher evidence (few inliers):
  c_e882645 (32/1822), castle-neroche c_44529 (52/98) and n0110_1 (15/26), castra-lemanis
  c_be12fb (15/25), ferme c_804aa7 (11/203). Two candidates carry 200-evidence CONFLICTS worth
  noting in the lines: c_e882645 (evidence kind=none, named_place "Ville" Q1165252, ~350 km west
  near Paris) and cenabum c_e73dc8 (kind=none, "Epinal" Q173695 ~350 km NE).
- castle-neroche n0110_1 is the one doc whose item pairs EQUAL the doc's pairs exactly (offset
  0 m) - the only "same version" line.
- Item candidates: most are `coarse: true` ("commons row: no stage-B fields: coarse anchor",
  scale_m_px from picture size, rejected by median residual > 45 m); a few are stage-B rejects
  (cawthorne n0325: scale-bar scale 0.259 vs its own points 0.790; dudley/ferme/watson-brake x2:
  stated-scale disagree or features not visible; a couple: fabricated grid-round / 1D-ladder
  anchor patterns).

**Driver / traps (kept from last session; tools/audit_306b.mjs is MY file and encodes both
workarounds in its IIFE - web/*.js is agent a's 307 territory, do not edit from this task):**
(1) wait for S.ready before select(), re-arm ensureSite(s); applyAll() after setGround (else the
per-site relief.jpg layer is never added and the relief shot shows the aerial - the live
/tiles/relief is OFF on this machine); (2) poll until map.getZoom() is within 0.1 of the target
(`15 - Math.max(0, Math.log2(span/1800))`, span = max(s.size_m)) BEFORE startFit (openPlan's
trailing easeTo keeps the CURRENT zoom - mid-flight flyTo lands at country zoom, observed 6.38
pre-fix), and re-issue the site easeTo WITH the explicit target zoom after refit if off by >0.2.
Re-shoot a wrong doc by id: rm its two pngs, then `node tools/audit_306b.mjs <doc-id>`.
Raw images: Commons `<sha1[:16]>.jpg` (NO c_ prefix) under data/raw/commons/<site>/ (served at
/media/commons/...); the two IA book pages under data/raw/books/earthworkenglan01allcgoog/full/
(both present). data/raw is the shared symlink; GET-only, ephemeral port - safe for parallel
checkouts.
