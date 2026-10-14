Status: open
# 306g: Look at the remaining on-map agent fits - the lead-port matcher re-fits (16 docs)
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, web/data/sites/, tools/audit_306a.mjs, PITFALLS.md, DECISIONS.md

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
