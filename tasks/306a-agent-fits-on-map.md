Status: open
# 306a: Look at the agent fits that are ON the map - the 23 built overlays
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/sites.json, web/data/review.json, web/data/sites/, tools/audit_306a.mjs

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 23
platefit documents with `by: agent` that are currently on the map - their overlay is built in
`web/data/sites/<site>/depictions.json` (the depiction's `fit.doc` names the doc) - over 12
sites. Open each the way a visitor sees it (site open, the depiction active, over the aerial
photograph, and over the LiDAR relief where the site has a `relief.jpg`) and judge whether the
drawing's lines sit on the real works. These are the fits the parent's title means by "none
reaches the map unseen" (Shotwick is here: 206's `by: agent` fit, 14-19 m residuals, never looked
at).

## Acceptance criteria
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open with its overlay active over the aerial photograph; plus a second shot over the LiDAR
      relief where the site has a `relief.jpg` - shotwick has none), taken with `tools/shot.mjs`
      against `server/serve.py --port 0` on this checkout (the driver recipe is in the parent's
      Hand-over; GET only, ephemeral port).
- [ ] A new section "## The agent fits, looked at (task 306)" in `docs/site_flow.md` holding one
      line per doc: what the drawing's lines sit on (the real banks, walls, ditches, streets) and
      the verdict. This subtask writes the section header and the 23 lines; the later subtasks
      append theirs.
- [ ] A fit whose drawn works visibly miss the real ones (wrong size, shifted, rotated) leaves
      the map: the picture is upserted into the site's review item with the reason (the
      `fit/review.py upsert_item` pattern 300/303 use for fabrication hits), the document is
      deleted, and the site is rebuilt with `.venv/bin/python tools/site_done.py <site>` (the
      overlay leaves `depictions.json`, the `drawings` count refreshes, the item is re-exported).
      Check the big picture is already cached in `data/raw/commons/big/` before a rebuild so no
      download hits the shared `data/raw` dir.
- [ ] A fit that sits right stays on the map, and its line says so. No `by: hand` document is
      touched; no new test failures against the driver's newest loop-start note (the suite was
      green in this checkout 2026-10-12: 123 passed, 1 skipped, test_gate pre-existing red).

## Docs (23, 12 sites)
- aldenhaag-q23650779.c_71c4ef3170b44288 - Aldenhaag detail kadasterkaart 1832 (Netherlands)
- alligator-effigy-mound-q4732645.c_618a6be74dfaff32 - Historical Collections of Ohio (US)
- avaricum-q281826.c_d457524470ca0ab3 - Caesar's Gallic war, Allen & Greenough (France)
- barnard-castle-q4185811.c_eacf8c673afcd863 - Alnmouth Tithe Map 1843 (UK)
- barwick-in-elmet-castle-q4865964.c_81c1ff143a862ee7 - Gott Collection at Hepworth Gallery (UK)
- bethlehem-q2523914.c_075db5049e2fb635 - Survey of Palestine, Bethlehem 01-beit-jala
- bethlehem-q2523914.c_1c20017970e54a01 - Survey of Palestine, Bethlehem 06
- bethlehem-q2523914.c_5ce1836b12e8e294 - Survey of Palestine, Bethlehem 03
- bethlehem-q2523914.c_67ed5d45466db19e - Plan of the Basilica of the Nativity, Sandys
- bethlehem-q2523914.c_7ee79582ebdab559 - (1881) PLAN SOUTERRAINS DE LA BASILIQUE
- bethlehem-q2523914.c_993872ffecfce2cf - Survey of Palestine, Bethlehem 11
- bethlehem-q2523914.c_a164ee440558d66c - Plan de Maestricht et environs 1748, detail Severen
- bethlehem-q2523914.c_a42a93d9589acd4d - Plan de Maestricht et environs 1748, detail Limmel
- bethlehem-q2523914.c_a8499553451a203c - Survey of Palestine, Bethlehem 09
- bethlehem-q2523914.c_ba63da7d782b9648 - Survey of Palestine, Bethlehem 08
- bethlehem-q2523914.c_d624c308cd860a1e - Plan de Maestricht et environs 1748, detail Limmel/Jerusalem
- bethlehem-q2523914.c_fc4566d6947287f4 - Survey of Palestine, Bethlehem 05-beit-jala
- binche-q95121.c_957d7ce2933eb332 - Binche, town plan by Jacob van Deventer (Belgium)
- bolsover-castle-q2968590.c_5531262b52faaea8 - Bolsover Castle, Mackenzie 1897 (UK)
- burlington-house-q225471.c_17e8fb3cf9037e19 - Burlington House, bird's-eye view by Johannes Kip (UK)
- forthill.b24849959_n0269_1 - Fort Hill, Highland county (Fowke 1902; US)
- newark.ArcheologicalAtlasOfOhio_n0098_1 - Earthworks at Newark (Mills 1914; US)
- shotwick-castle-q7502621.c_e6e5490609414bb9 - Shotwick Castle, Mackenzie 1897 (UK; aerial-only, no relief)


## Hand-over
(2026-10-12, iteration 136, agent c - session 2 of 306a. Audit run FINISHED, shotwick REMOVED, 11/23
lines written; cut at the context limit with a MAJOR finding on the bethlehem site that must be
settled before the bethlehem lines are written.)

**State.**
- All 45 screenshots are done and verified: the session-1 background run survived and completed
  ("[audit] all shots written", 45 [audit] shot lines, 45 [eval] confirmations all present:true /
  visible, zero pageerror/MISSING). `docs/site_flow/agent_fits/` has 45 PNGs (shotwick aerial-only;
  the earlier log had 47 [audit]-prefixed lines = 45 shots + "server on" + "all shots written").
- **shotwick is REMOVED from the map** (judged WRONG SIZE, evidence below). Done: (1) upserted an
  entry into `data/review/shotwick-castle-q7502621.earthworkenglan01allcgoog_n0575_1.json` via
  `review.upsert_item('.', sid, [entry])` - the entry keeps the existing lead (earthwork... is
  candidates[0], my candidate c_e6e5490609414bb9 appended second) with plan/title/url/pairs and
  `why` = the 306a audit reason (full text in the site_flow.md line and in the item file);
  (2) deleted `data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json`;
  (3) `plan_fit.prune('.', 'shotwick-castle-q7502621')` (depictions.json now `{"depictions": []}`,
  both webp files deleted); (4) `review.export('.', site_id=sid)` (page re-published: 333 open of
  346 items - the count moved from other agents' batch work, the 220/221 third-trigger pattern;
  shotwick item is OPEN, resolved:None, both candidates). `tests/test_serve.py::test_platefits_docs_match_sites` passes after.
  **Why NOT `tools/site_done.py` as the task text suggests:** its `_fit` phase calls `matchfit.run`
  whenever the matcher is reachable (it IS: 127.0.0.1 /health true this session) and the site has a
  row without a doc (the earthwork candidate) - that would place a NEW unaudited agent fit on the
  map, the exact thing 306 exists to prevent. The 4 product calls above are the same calls site_done
  itself makes (upsert_item / prune / export), minus the fit phase, and produce exactly the stated
  outcome. Logged in DECISIONS.md.
- `docs/site_flow.md` now ends with the new section **"## The agent fits, looked at (task 306)"**
  holding the intro + 11 lines (aldenhaag, alligator, avaricum, barnard, barwick, binche, bolsover,
  burlington, forthill, newark = all STAY; shotwick = REMOVED with the full reason). 12 bethlehem
  lines NOT yet written (see finding below). Later subtasks append below the section.
- PITFALLS.md: both session-1 entries filed (the [js]-as-expression IIFE trap, and S-not-on-window)
  - uncommitted, in the working tree.

**THE FINDING (verify before writing any bethlehem line): the site bethlehem-q2523914 is the DUTCH
village, not the biblical one.** The c_a164 screenshot (read at the limit, first bethlehem aerial
actually viewed) shows the page header "BETHLEHEM / Het Hogeland, Groningen, Netherlands" over a
Dutch polder aerial, and the active drawing's ink reads "Severen", "Cantel", "C. Harnesstg" - all
real Het Hogeland hamlets (Cantel is beside Bethlehem-Groningen). So: (a) the 1748 "Plan de
Maestricht et environs" details (c_a164, c_a42a, c_d624) are LOCAL maps of the Dutch site and look
like they sit on the right ground (c_a164: Severen hamlet, the village centre, field boundaries all
aligned on the polder - judge properly next session); (b) the 7 "Survey of Palestine, Bethlehem 01/03/05/06/08/09/11" ground sheets are maps of JUDEAN
Bethlehem fitted onto a site 2000 km away - a toponymic collision - and (c) the 2 basilica plans
(c_67ed Sandys 1615, c_7ee7 1881 souterrains) are building-interior plans fitted as ground maps
(wrong kind; the 1881 one is rotated -18.4 deg). Their
residuals (0 m on most, up to 41 m) measure only the local pattern match (SoP sheet grid vs polder
grid), not the truth. **Next session, FIRST:** confirm which place Q2523914 is (Wikidata; also read
`data/sites/bethlehem-q2523914/site.json` place field and the 12 docs' pairs: if the pairs' lon/lat
cluster around 53.3N/6.3E (Groningen) the fits were placed on Dutch ground; if around 31.7N/35.2E
the doc is geographically true and the SITE is the wrong half of the collision). Then decide per
doc: a true-judaea doc on a dutch site = wrong site = leaves the map (same removal recipe as
shotwick); a local-1748 doc = judge normally. The parent 306 hand-over's "bethlehem x12 (mix...)"
assumption was based on the doc TITLES only - it was never checked against the site's place field.
Note for the verdict lines: if some bethlehem docs are removed, the site stays built (it has other
local content) - just prune per doc and refresh via build_site.set_drawings (site_done's _entry
logic) or plan_fit.prune (which already calls set_drawings).

**Judged so far (aerials read, all but shotwick STAY):**
- aldenhaag 1832 kadaster detail, alligator-effigy-mound 1891 map, avaricum Caesar (Allen &
  Greenough) map, barnard-castle 1843 tithe map - georeferenced sheets (session 1, all STAY).
- barwick-in-elmet-castle (Gott Coll. 116): hachures track the real hill on aerial AND LiDAR
  (summit on summit, rampart/ditch rings on the real earthworks). STAY.
- binche (van Deventer 1545): medieval town core + streets on the real urban core, frame over
  surrounding farmland (gate 0.2 m). STAY.
- bolsover (Mackenzie 1897): drawn moat on the real moat ring (aerial + LiDAR), Great House range
  on the park's east side. STAY.
- burlington-house (Kip c.1707): Thames-with-barges on the real river, street grid parallel incl.
  the upper-right diagonal (gate 0.0 m). STAY.
- forthill (Fowke 1902): hachured oval/inner works/causeway exactly on the LiDAR ridge and
  earthworks (aerial is uniform forest - the relief decides). STAY.
- newark (Mills 1914): 1848-survey earthworks (circles, Mound City, octagon) on the modern park
  grounds, sheet grid on the city grid (resid <=0.1 m). STAY.
- shotwick (Mackenzie 1897): REMOVED - drawn moated ring 188 m x 188 m (measured: ink bbox 822 x
  822 px of the 839x840 plate at the fitted 0.2289 m/px) vs real earthworks at most ~90 m (40x20 m
  hexagonal motte + 25 m ditch + 38 m bailey per NHLE 1016616, confirmed via Wayback of the NHLE
  listing description, which 403s direct; NHLE and heritagegateway both 403 from this VM, wayback
  works). The 4 turret anchors' 2-19 m residuals are the ~2x scale mismatch (the fit_gate
  n=3-6 blind spot, PITFALLS). Aerial-only site: earthworks invisible under lawn even at zoom 18
  (the page caps at zoom 18 - jumpTo(18.3) clamps; also the depiction deselects to "None" after a
  manual jumpTo - it is view-scoped, so judge size from the stored fit stats + the listing,
  which is decisive here).
- bethlehem x12: PENDING - see THE FINDING. Split to verify: 7 SoP ground sheets (c_075db=01,
  c_5ce18=03, c_fc456=05, c_1c200=06, c_ba63d=08, c_a8499=09, c_99387=11) = maps of Judaea (wrong
  place if the site is Dutch); c_67ed (Sandys 1615) + c_7ee7 (1881 souterrains, rot -18.4 deg) =
  basilica BUILDING INTERIOR plans fitted as ground maps (wrong kind); c_a164, c_a42a, c_d624
  (1748 details) = local maps, c_a164 looked ALIGNED on the Dutch polder (Severen/Cantel labels on
  the real hamlets, village centre on the village, field boundaries tracking) - likely a true local
  fit; its 34-112 m residuals need explaining (a 1748 map is not a survey: the residual probably
  reflects the map's own inaccuracy, not a placement error - check where its 4 anchors are).
  Confirm Q2523914's place + each doc's pairs' lon/lat cluster BEFORE judging.

**Tests.** Full suite NOT re-run since the shotwick removal (last full run: parent's baseline
123 passed / 1 skipped / test_gate pre-existing red, 2026-10-12). The shotwick-touching test
(test_serve::test_platefits_docs_match_sites) passes standalone. Next session: run `.venv/bin/python
-m pytest tests/ -q --ignore=tests/test_gate.py` before further removals (the review-page export
could also touch tests/test_review.py, tests/test_fit_queue.py, tests/test_site_done.py - the
PITFALLS "review.json is a derived page" entry names them; if they go red on the 333/346 count
move it is the population-staleness pattern, not my edit).

**Exact next step (session 3).** (1) Verify the bethlehem site identity: Wikidata Q2523914 +
`data/sites/bethlehem-q2523914/site.json` place + each bethlehem doc's pairs (lon/lat cluster).
(2) Judge c_a164 properly (anchors + the 1748 map's own scale bar if visible) and read the other
11 bethlehem aerials in batches of 4-6 (relief where the aerial is inconclusive); write the 12
bethlehem lines into the existing site_flow.md section, keeping 306a's lines grouped at the top
(append after the newark/shotwick lines). Any WRONG doc: the shotwick removal recipe (upsert
entry with the reason - for a wrong-site doc the reason is "drawn work is of <real place>, not
this site; toponymic collision" - delete doc, plan_fit.prune('.' , site) per removal, then ONE
final `review.export('.', site_id='bethlehem-q2523914')` at the end of the batch). (3) Stale
drawings counts: sites in the A-group with overlays but drawings=0 (alligator, avaricum, barnard,
barwick, bethlehem-if-stays, binche, bolsover, burlington) need a count refresh -
`build_site.set_drawings(sid, '.')` per site (that is site_done's _entry logic; do NOT run
site_done: matcher would fire - it is reachable). forthill=2 and newark=2 already correct. (4)
Full suite, update this hand-over, commit.

**State.**
- `tools/audit_306a.mjs` is built (added to this task's `Touches:` line). One `server/serve.py --port 0`
  for the whole run; per shot it loads the page, then the IIFE: poll `S.byId[site]` (typeof-guarded -
  `S` is a top-level `const`, NOT on `window`), `select(site)`, `await loadDeps(s)`,
  `S.depSel[site] = <the doc's depiction file>`, `setGround('imagery'|'relief', s)`, `applyDep(s)`, and it
  returns `{present, ground, layer, visible, active, zoom}` as the `[eval]` line. The script prints an
  `[audit]` line per shot with the stored fit stats from depictions.json (resid_m, m_per_px, rot_deg,
  label). 1440x900, POSTWAIT 12 s (aerial) / 7 s (relief). Re-run is idempotent (same PNGs). Run from the
  project root: `node tools/audit_306a.mjs [site ...]` (default: all 12 A-group sites). It spawns
  `tools/shot.mjs` with `NODE_PATH=/home/agent/tools/shot/node_modules` (Chrome 155, see PITFALLS).
- The full run was launched in the background: `nohup node tools/audit_306a.mjs > /tmp/audit_306a.log
  2>&1 &` (started ~12:1x, PID 3468347). At context-limit: 16/45 shots done, all `file=written`, no
  pageerrors. The run takes ~25 min total; it is almost certainly finished by the next session. Check the
  log; if it is dead or the log is gone (tmp wiped), just re-run the command - nothing is lost.
- Screenshots: `docs/site_flow/agent_fits/<site>_<plan>.png` (aerial) + `..._relief.png` where the site has
  a relief.jpg. Expect **45** files: 23 aerial + 22 relief (shotwick is aerial-only). (I wrote 44 in the
  parent's hand-over; the true count is 45: bethlehem 12x2 = 24, ten single-doc sites x2 = 20, shotwick 1.)
- Parent 306's split is COMPLETE this session: 306d-orphan-fits-uk-1 (18 docs, sites a-l),
  306e-orphan-fits-uk-2 (17 docs, o-y), 306f-orphan-fits-continental (17 docs, 7 sites) created; 306c
  corrected to 16 docs (it already listed marietta.b24849959_n0195_1 but the header said 15); parent
  hand-over updated with the corrected counts (23+21+16+18+17+17 = 112). The re-derivation method:
  orphan = doc in data/db/platefits whose (site,plan) is neither a fit.doc in that site's
  depictions.json nor a candidate plan in that site's data/review item; UK/US/continental by the
  sites.json `region` (marietta has no region field but is a US site).

**Judged so far (aerials read):**
- aldenhaag-q23650779.c_71c4ef3170b44288 (1832 kadasterkaart detail; identity fit: resid 0, 1 m/px,
  gate 0.0): ink follows the real village, roads and the terp ring exactly. STAYS.
- alligator-effigy-mound-q4732645.c_618a6be74dfaff32 (1891 Historical Collections of Ohio map; identity
  fit, gate 0.0): georeferenced town map; the effigy-mound park (looped paths) is the covered centre.
  STAYS.
- avaricum-q281826.c_d457524470ca0ab3 (Caesar, Allen & Greenough 1898; near-identity, gate 0.1): map of
  modern Cher with the Roman castra box drawn over the real town centre. STAYS.
- barnard-castle-q4185811.c_eacf8c673afcd863 (Alnmouth Tithe Map 1843; identity fit, gate 0.0):
  georeferenced; ink on the real streets and river; "Barnard Castle" label area over the real castle
  position by the river bend. STAYS.

**Still to judge:** barwick-in-elmet-castle (shot taken, aerial read next - it is the only non-georeferenced
non-Bethlehem doc after bethlehem; expect a true similarity fit), bethlehem x12 (mix: some identity fits,
some small-residual: c_5ce1836b12e8e294 has resid [25.7, 6.4, 10.2, 10.2], rot 4.7 - the biggest residuals
so far; judge each), binche (van Deventer town plan), bolsover-castle (Mackenzie 1897), burlington-house
(Kip bird's-eye), forthill (Fowke 1902), newark (Mills 1914), shotwick (Mackenzie 1897; 14-19 m residuals;
smoke-test shot looked roughly on the earthworks - judge properly).

**Tests.** Not re-run in full this session (baseline from parent: 123 passed, 1 skipped, test_gate
pre-existing red). `tests/test_serve.py::test_platefits_docs_match_sites` passed standalone when I ran it
(all 133 store docs' sites are in web/data/sites.json - a false alarm I raised earlier was my own typo in a
probe list: 'fort-ancient' without the qid). Next session: run `.venv/bin/python -m pytest tests/ -q
--ignore=tests/test_gate.py` before acting on anything.

**PITFALLS to file next session (I could not edit PITFALLS.md after the context-limit message):**
1. `tools/shot.mjs` / Playwright 1.63: `page.evaluate('<js string>')` treats the string as an EXPRESSION;
   a bare function string like `async () => {...}` evaluates to a function value and returns `undefined`
   (it is NOT auto-invoked). Wrap it: `(async () => {...})()`. (Verified with a throwaway probe:
   `page.evaluate('async () => ({a:42})')` -> undefined; the IIFE-wrapped form -> {"a":42}.)
2. In shot.mjs IIFEs, page globals declared with top-level `const`/`let` in index.html (like `S`) are NOT
   on `window` (page-wide lexical environment): use the bare name with a `typeof S !== 'undefined'`
   guard; `window.S` is undefined. (Extends the existing pitfall about extension scripts.)

**Exact next step (session 2).** (1) Check /tmp/audit_306a.log (re-run the command if needed); verify 45
PNGs in docs/site_flow/agent_fits/. (2) File the two PITFALLS entries above. (3) Read the rest of the
aerials in batches of ~4-6 (each `read` of a PNG is heavy - a session judges ~8-12 docs) and write the
docs/site_flow.md section at the END of the file: "## The agent fits, looked at (task 306)" with one line
per doc: what the lines sit on + verdict (306a writes the header + its 23 lines; later subtasks append
theirs - keep 306a's lines grouped at the top so appending stays clean). Tick box 1 when all 23 lines +
45 shots exist. (4) Any doc judged WRONG: upsert the picture into the site's review item with the reason
(`fit/review.py upsert_item(root, site_id, [entry])`, entry carries plan/title/url/... plus the reason,
as 300/303's fabrication path did), delete data/db/platefits/<doc>.json, then
`.venv/bin/python tools/site_done.py <site>` (check the big picture is already in data/raw/commons/big/
before running so no download hits the shared raw dir; the line rebuilds depictions.json, refreshes the
site's `drawings` count in web/data/sites.json, re-exports web/data/review.json). (5) Sites that STAY but
whose `drawings` count is stale (0 despite the overlay: all of the A-group except aldenhaag=1, forthill=2,
newark=2) get the same site_done run to refresh the count (part of "sits right"). (6) Re-run the suite,
update this hand-over, commit. Note web/data/sites.json is a real tracked file (the per-site dirs are the
symlinks); site_done.py's writes to it are the product's own (see 219's note in the git log).
