Status: open
# 306g: Look at the remaining on-map agent fits - the lead-port matcher re-fits (16 docs)
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, web/data/sites/, tools/audit_306a.mjs, tools/audit_306g.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the audit recipe and the original 112-doc inventory live in the parent's
Hand-over): the last platefit documents a visitor sees that have no audit record in this
repo. 306 split (iteration 134) against a store of 112 non-hand docs; all of those are now
dealt with (306a-f; the 306e/306f populations were closed by the lead as superseded,
commit 10dcb23). Since the split the lead's own port commits placed new `by: agent`
(`fitter: matcher`) documents on the map: 20277f3 (11 matcher fits on newly built sites),
0685a4c (Burcht van Leiden x2), 77405cf (13 matcher re-fits after the 212b sync, stated
"eye-checked" on the Mac). As of 2026-10-14 the store holds 49 non-hand docs, all on the
map; 33 have the audit record (bullet line + shots); these 16 (verified this session;
re-derive at start, see Notes) have neither:

- arras-q131329.c_4e242bc2623751a0
- avesnes-sur-helpe-q217178.c_61fbbcd3d6051cd9
- bavay-q477176.c_e8345a33509010ae
- burcht-van-leiden.c_2ed7167f77ea05d4
- burcht-van-leiden.c_b790b0ce40d7d26b
- cahokia-q333661.c_1a7c2a11c3a0dd21
- douai-q193826.c_661c074bcd04d49a
- gouda-q84125.c_ba646ea988fc6bc8 (306f survivor, re-ported by 77405cf)
- gravelines-q323399.c_173e0d61c038bada
- groningen-q749.c_498f9aa12d03fc30
- le-cateau-cambresis-q329103.c_f613a7c2165ba280
- lille-q648.c_1f7cce1c856a7bcb
- saint-omer-q208793.c_df791c935a4905f7
- utrecht-q803.c_f5f96070065c0763
- valenciennes-q163795.c_0b5e6f27e6aeba51
- old-sarum-q782719.c_b2701b5231da42f2 (306e's coarse candidate, re-ported by 77405cf)

All 16 sit on the map (their overlay is built in the site's `depictions.json`), so they
are audited the visitor's way: open the site, activate the doc's own depiction, over the
aerial photograph, and over the LiDAR relief where the site has a `relief.jpg` (10 of the
15 sites have one: arras, burcht-van-leiden, cahokia, douai, gouda, gravelines, groningen,
saint-omer, utrecht, old-sarum; avesnes-sur-helpe, bavay, le-cateau-cambresis, lille,
valenciennes are aerial-only). The lead already looked at these on the Mac (77405cf says
so; the 306f lead close describes the same practice for its siblings); this audit is the
repo record of the page's own rendering and the second pair of eyes the parent's title
asks for ("none reaches the map unseen"). Most are georeferenced atlas town plans (van
Deventer, Atlas de Wit, Civitates): the identity fit (resid ~0, gate ~0) is expected, so
the question for a sheet is whether its content (town core, river, walls, labels) sits on
the real town, not the anchor arithmetic.

## Acceptance criteria
- [ ] Re-derive the gap list at start (script in Notes): every platefit document with `by`
      other than "hand" that has no bullet line in the "## The agent fits, looked at
      (task 306)" section of `docs/site_flow.md`; the expected set is the 16 above. Audit
      each the visitor's way (the `tools/audit_306a.mjs` pattern: `select(site)` -> the
      doc's depiction activated -> `setGround('imagery'|'relief', site)` -> `applyDep`,
      driven with `tools/shot.mjs` 1440x900 against `server/serve.py --port 0` - GET only,
      ephemeral port, parallel-checkout safe) and take one screenshot per doc in
      `docs/site_flow/agent_fits/<site>_<plan>.png` (plus a `_relief.png` where the site
      has a `relief.jpg`).
- [ ] A "306g - the 16 lead-port on-map matcher re-fits" block appended to the "## The
      agent fits, looked at (task 306)" section of `docs/site_flow.md` (after the 306e
      block, before "## The site markers become arrowheads"), one line per doc in the
      established shape: doc id - source (fit stats: pts, resid, m/px, rot): what the
      lines sit on - verdict. Each line notes that the doc is a lead-port matcher re-fit
      (its commit) and that this is the visitor-view record.
- [ ] A fit whose drawn works visibly miss the real ones (wrong size, shifted, rotated)
      leaves the map the 303 way: the picture is upserted into the site's review item
      with the reason (`fit/review.py upsert_item` pattern), the document is deleted, the
      site is rebuilt with `.venv/bin/python tools/site_done.py <site>` (the overlay
      leaves `depictions.json`, the counts refresh, the item re-exported, the site stays
      covered). A fit that sits right stays, and its line says so.
- [ ] Backfill the 3 missing 306e lines in the same section (marked "306e, backfilled
      2026-10-14"; the docs are gone from the store by the 212b sync, so no new shots and
      no item edits - the lead closed 306e with the 212b item entries as-is, 10dcb23):
      windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 (DELETED - wrong place and
      kind: Allcroft 1908 'WINDMILL SITES, LEWES DOWN', a hachured barrow hill ~one
      hill-width W-NW of the real Windmill Hill causewayed enclosure, East-Sussex vs
      Wiltshire toponymic collision; fit 1.0000 m/px, resid 0.0, grid-ladder anchors),
      york-castle-q80637.c_8dac5aacd73916b8 (KEPT in the item - the owner's call: a
      genuine 1820 Waud watercolour perspective view of this castle, Clifford's Tower on
      its motte, the 1820 curtain walls and the Foss; 4-point perspective fit
      1.0507 m/px, rot +7.03 deg, unverifiable by construction; the 212b sync deleted it
      as a fabricated-anchor-pattern document), york-castle-q80637.c_a7db545536f13e24
      (DELETED - the 306e verdict recorded in the 306e hand-over, commit 49ca718: fit
      0.9742 m/px, +0.38 deg, site point -> page (298.3, 384.9); copy the verdict from
      that hand-over, do not re-judge).
- [ ] No `by: hand` document is touched; no new test failures against the driver's
      newest loop-start note (the one known red:
      tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser - agent
      a's in-flight 307 work; run the suite with `--ignore=tests/test_gate.py` as the
      other 306 subtasks did; any other red is new and must be diagnosed).

## Notes
- Re-derive at start (the store may have moved again): list store docs with `by !=
  "hand"`; a doc needs a line iff its id is not the head of a bullet in the section
  (bullets match `^- <doc id> - ` inside "## The agent fits, looked at (task 306)").
  Expected: exactly the 16 above. Include any other non-hand doc without a line; skip
  docs that were deleted since (a deleted doc with a line is fine).
- The 306f population (17 continental docs, task file 306f) is closed by the lead's
  explicit 2026-10-13 ruling ("Nothing left to audit": the vision-model docs came off
  the map through the 212b line check; the surviving matcher re-fits were eye-checked
  by the lead). Do NOT re-audit those 17; the only one of them in the store is gouda
  c_ba646ea988fc6bc8, which is in this list as a 77405cf re-port. Likewise do not touch
  the lead-closed 306e item entries (box 4 is lines-only).
- Judging aids (the 306b-f technique, parent Hand-over + docs/site_flow.md "The matcher
  fit (the lead, 2026-10-11)"): the site's own survey sheets (web/data/sites/<site>/
  etatmajor/cassini/tmk1850/fr_ortho1950 where present; the 1842 six-inch for UK sites),
  the plate's own scale bar, fitted m/px vs the drawn scale (within ~20% = trustworthy),
  reverse-geocode the site point before judging (a site's canonical point can be a
  modern city). For georeferenced town-plan sheets (van Deventer / Atlas de Wit /
  Civitates): the identity fit is the expected shape; judge the sheet content against
  the real town on the aerial (core, river, walls) and note the sheet's frame extent.
- old-sarum's item (data/review/old-sarum-q782719*.json) already holds c_b2701b as a
  candidate beside the 306e audit entries; if that doc is judged wrong, upsert the
  reason beside it (replace in place, keep the item open - the site stays covered by
  its two hand-built depictions).
- Driver: `tools/audit_306a.mjs` (306a's visitor-view driver; takes doc ids) is the
  starting point; the parent Hand-over holds the full headless recipe (the fit-tool
  variant, `tools/audit_306b.mjs`, is NOT what you want here - these docs are on the
  map, so the depiction-activation path is the visitor's view).

## Hand-over
(2026-10-14, iteration 140, agent c - session cut at the context limit mid-audit. The 27
shots and the audit driver are DONE and on disk; judging is 1/16 done; the docs/site_flow.md
edit has NOT started. Next session: finish judging the 15 remaining shots, write the 306g
block + the 3 306e backfill lines, remove any wrong fit the 303 way, run the suite, tick boxes.)

**State (all verified this session by running code).**
- Box-1 re-derivation at start: EXACTLY the expected 16 (inline script: store docs with
  by != "hand" minus bullet heads `^- <id> - ` inside "## The agent fits, looked at (task
  306)"; 92 bullet heads, 59 of them for docs deleted by the 212b sync - fine to keep).
- All 16 confirmed as overlays: each is the fit.doc of an entry in its site's
  web/data/sites/<site>/depictions.json. Fit stats (dep.fit): 8 pairs each, resid <=0.3 m,
  m_per_px 0.77-2.22, rot -0.26 to -25.56 deg. These are GEOREFERENCED sheets (the
  depictions.json corners are the placement; the matcher re-fit reproduces that georef -
  not grid-ladder anchors), so the question per sheet is whether its content (town core,
  river, walls, labels) sits on the real town, per the task Notes.
- tools/audit_306g.mjs WRITTEN (modeled on tools/audit_306a.mjs; (site,doc) pairs; visitor
  way: select -> doc's depiction -> setGround imagery|relief -> applyDep; shot.mjs 1440x900
  against server/serve.py --port 0; the [eval] line confirms the doc's depiction is the
  active layer on screen). Added to the task's Touches line. FULL RUN DONE: 27 shots
  written (16 aerials + 11 reliefs: arras, burcht x2, cahokia, douai, gouda, gravelines,
  groningen, saint-omer, utrecht, old-sarum; the 5 aerial-only sites avesnes/bavay/
  le-cateau/lille/valenciennes have no relief.jpg - matches the task file). All [eval]
  lines: present=true, layer=true, visible="visible", active = the doc's own _ink.webp.
  ArcGIS [reqfail] ERR_ABORTED lines are harmless (flyTo-canceled tiles; final tiles land -
  verified on the arras aerial, which renders fully).
- Shot files on disk (names: site_plan, dot->underscore) in docs/site_flow/agent_fits/:
  arras-q131329_c_4e242bc2623751a0; avesnes-sur-helpe-q217178_c_61fbbcd3d6051cd9;
  bavay-q477176_c_e8345a33509010ae; burcht-van-leiden_c_2ed7167f77ea05d4{,_relief};
  burcht-van-leiden_c_b790b0ce40d7d26b{,_relief}; cahokia-q333661_c_1a7c2a11c3a0dd21{,_relief};
  douai-q193826_c_661c074bcd04d49a{,_relief}; gouda-q84125_c_ba646ea988fc6bc8{,_relief};
  gravelines-q323399_c_173e0d61c038bada{,_relief}; groningen-q749_c_498f9aa12d03fc30{,_relief};
  le-cateau-cambresis-q329103_c_f613a7c2165ba280; lille-q648_c_1f7cce1c856a7bcb;
  saint-omer-q208793_c_df791c935a4905f7{,_relief}; utrecht-q803_c_f5f96070065c0763{,_relief};
  valenciennes-q163795_c_0b5e6f27e6aeba51; old-sarum-q782719_c_b2701b5231da42f2{,_relief}.png
- Judging so far (1 of 16): ARRAS - the 1545 van Deventer ink (red over the aerial) follows
  the real Arras street grid, the Scarpe/Deule rivers and the old-town core; STAYS.
- Judging aids: /tmp/aw306g_composite.py (throwaway, NOT in the repo) builds two views per
  doc: (A) 2000px: the site's prebuilt ground raster (imagery.jpg > relief.jpg >
  block_top.jpg > coloured etatmajor.webp) + the doc ink in red; (B) 800px: independent
  survey ink RED (etatmajor_ink 1840 FR / tmk1850_ink 1850 NL / topo_1888_62500_ink US /
  six-inch-1st_ink 1842 UK) + doc ink BLUE, 100 m grid + 200 m bar. BUG TO FIX FIRST: mode
  B crashed for avesnes (no relief.jpg AND no block_top.jpg) - give base2 the same
  fallback chain as mode A (next existing of relief.jpg/block_top.jpg/etatmajor.webp).
  Only arras's A+B exist so far; re-run for the other 15. Learnings baked in: the ink file
  is dep.file.replace('.webp','_ink.webp') (same pixel size as the plan webp - verified all
  16); corners order TL,TR,BR,BL; affine warp dev <=0.1 m for these quads (the script
  prints it - a big dev would mean a wrong corner order). FINDING: mode B (1840 etatmajor
  red) is too sparse to act as a pixel-alignment reference against the dense 1545 sheets -
  for the FR/NL towns the browser aerial shot (above) is the deciding evidence, plus, for
  ambiguous ones, a zoomed page shot (js: after the iife's applyDep call
  map.jumpTo({center:[s.lon,s.lat],zoom:17}); GET-only, still the visitor's view). Mode B is
  worth it where the survey is fine-grained: old-sarum (1842 six-inch), burcht-van-leiden
  (TMK 1850 1:10,000), cahokia (1888 USGS 62500).
- old-sarum c_b2701b ('Plan of Old Sarum' 1916): 8 SCATTERED pairs (not a ladder), all
  resid 0.0, 1.4747 m/px, -0.26 deg; sheet 500x436 px covers ~737x643 m at the fit. It is
  306e's coarse candidate re-ported by 77405cf; the old-sarum review item already holds it
  as a candidate (task Notes: if judged wrong, upsert the reason IN PLACE beside it, keep
  the item open - the site stays covered by its two hand-built depictions - then delete the
  doc and .venv/bin/python tools/site_done.py old-sarum-q782719). Judge from its aerial +
  relief shots + the 1842 six-inch composite: the drawn rampart ring vs the real earthwork
  (the 1842 shows it clearly, and so does the relief).
- 306e backfill (box 4): verdicts are in tasks/306e-orphan-fits-uk-2.md ## Hand-over (read
  it): windmill-hill n0558_2 DELETED (Lewes Down toponymic collision, 1.0000 m/px
  grid-ladder, sheet ~one hill-width W-NW of the real enclosure); york-castle
  c_8dac5aacd73916b8 KEPT in the item (owner's call; 1820 Waud watercolour perspective,
  1.0507 m/px +7.03 deg, site point -> page (412.9,91.5)); york-castle c_a7db545536f13e24
  DELETED (the village of Center, Broome County NY; 0.9742 m/px +0.38 deg; site point ->
  page (298.3,384.9)). Lines only, no item edits, marked "306e, backfilled 2026-10-14".
  WHERE: the section "## The agent fits, looked at (task 306)" starts at L701 of
  docs/site_flow.md and ends at L1483 (last 306e line = taunton-castle c_05cb4a02bd58e82e);
  "## The site markers become arrowheads (task 308, 2026-10-13)" is at L1484. Append after
  the taunton line: the 3 backfill lines, then the 306g block (header + 16 lines, the
  established shape: doc id - source (fit stats: pts, resid, m/px, rot): what the lines sit
  on - verdict; each line notes it is a lead-port matcher re-fit (commit: 20277f3 for the
  11 new ports, 0685a4c for the 2 Leiden, 77405cf for the 13 re-fits incl. gouda +
  old-sarum) and that this is the visitor-view record).
- Site points (web/data/sites.json is a dict {"sites": [...]}): all 15 are the real
  towns/sites (arras 2.78/50.2892 town; ...; old-sarum -1.804722/51.093333 hillfort;
  burcht-van-leiden 4.493/52.159 motte in central Leiden; cahokia -90.0635/38.6572).
  No toponymic surprises found.

**Tests.** Not run this session. Baseline = the driver's newest loop-start note
(2026-10-13): 1 red (tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_
browser - agent a's in-flight 307 work), 159 passed, 1 skipped; run with
--ignore=tests/test_gate.py -p no:cacheprovider. My files (docs/site_flow.md, the pngs,
tools/audit_306g.mjs) are not read by any test, so expected result = baseline unchanged;
any other red is new and must be diagnosed. (docs/site_flow/307d_*.png show as modified in
git status in this checkout - agent a's 307d tests regenerate them; they are NOT mine:
do not edit them; if `git add -A` sweeps their changes into my commit that only affects my
branch - note it in the commit message and the driver merges per task.)

**NEXT (fresh agent, one step at a time).**
1. Fix the mode-B base2 fallback in /tmp/aw306g_composite.py (one line), re-run it for the
   15 remaining docs (idempotent; arras done). If /tmp was cleared, regenerate the crops:
   each 1440x900 shot -> map area = im.crop((390,0,1440,900)) saved as
   /tmp/aw306g/<site>_<plan>{,_relief}_map.png (system python3 has no PIL - use
   .venv/bin/python).
2. Look at the remaining 15 aerials (and reliefs where they add something: old-sarum,
   cahokia; the FR/NL cities are flat - the aerial decides). For the 11 van Deventer
   towns: check river + town core + walls + labels against the real town (arras done =
   STAYS; expect the rest to sit on their real towns too - but check each, esp. small
   towns like le-cateau-cambresis where the sheet's frame extends over farmland). Zoomed
   page shots (map.jumpTo zoom ~17, GET-only) if a shot is ambiguous.
3. Write the docs/site_flow.md edits (box 2 + box 4 above). Keep lines factual: cite what
   the lines sit on; STAYS or REMOVED (the 303 way: fit/review.py upsert_item the
   picture+reason into the site's review item, delete data/db/platefits/<doc>.json, then
   .venv/bin/python tools/site_done.py <site>; for old-sarum: replace its entry in place
   in the existing item, keep the item open, then delete the doc + site_done).
4. Run the suite as in Tests; tick boxes 1-4 as verified; rewrite this hand-over; append
   the DECISIONS entry; commit (git add -A; note the 307d pngs if swept in).

Re-read: tools/audit_306g.mjs - the DOCS (site,doc) list vs the 16 in box 1; the [eval]
contract of the iife (present/layer/visible/active) - what to trust in the shot logs.
Re-read: web/index.html:applyDep/select (L446-478, L851-880) - verified this session that
the page still matches the iife's assumptions; re-verify only if a shot shows the wrong
layer active.
Re-read: data/review/old-sarum-q782719*.json - the item's existing candidates (c_041083ec,
c_8192abb9, earthwork n0142_1, c_b2701b) before deciding whether c_b2701b goes 303-way;
upsert_item replaces an existing plan's entry in place (lead and file name stay).
