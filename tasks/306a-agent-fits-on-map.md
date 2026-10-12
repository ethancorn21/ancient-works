Status: open
# 306a: Look at the agent fits that are ON the map - the 23 built overlays
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/sites.json, web/data/review.json, web/data/sites/, tools/audit_306a.mjs, fit/src_mackenzie.py, tests/test_src_mackenzie.py, tests/test_fit_provenance.py, tests/golden/src_mackenzie_sample.json

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
(2026-10-12, iteration 137, agent c - session 3 of 306a. BETHLEHEM AUDIT FINISHED AND REMOVED (9 of 12
docs); all 23 lines now in site_flow.md. The session cut at the context limit right after, with 5 test
fixes designed but NOT yet written - see "Exact next step".)

**State.**
- All 45 screenshots verified (sessions 1-2). `docs/site_flow.md` section "## The agent fits, looked at
  (task 306)" now has ALL 23 of 306a's lines (10 STAY + shotwick REMOVED + 12 bethlehem: 3 STAY + 9
  REMOVED) - box 1 is done (23 lines + 45 shots).
- **bethlehem verdicts (all 12 judged this session, screenshots read; the 9 removals at 720x450
  downscales for context, the 3 stays at full 1440x900):** the site is the Dutch hamlet (Wikidata
  Q2523914 = "hamlet in Het Hogeland, Netherlands", enwiki "Bethlehem, Groningen"; site.json place/
  coords/wiki confirm). ALL 12 docs' pairs cluster at 53.38N/6.61E = placed on the Dutch ground; the
  collision is in the docs' provenance. (a) 7 SoP ground sheets (c_075db=01, c_1c200=06, c_5ce18=03,
  c_99387=11, c_a8499=09, c_ba63d=08, c_fc456=05) = maps of the Judean Bethlehem/Beit Jala area fitted
  onto the polder: the sheet frame spans the whole 1.2 km site, the Beit Jala hamlet/field hatching
  lands on the polder's parcel grid by local pattern coincidence (several are identity fits, 0.0 m
  residuals - the anchors were picked exactly where the far sheet grid coincides with the polder grid;
  that is the 2000 km trap, and why 306 exists). (b) 2 basilica plans (c_67ed Sandys 1615; c_7ee7 1881
  souterrains, rotated -18.4 deg) = building INTERIOR plans fitted as ground maps (wrong kind). (c) 3
  local 1748 details (c_a164 Severen & Kanjel; c_a42a titled "Limmel" but the ink shows the local
  Bethlehem/Jerusalem/Leumel area; c_d624 Limmel/Jerusalem/Bethlehem) = TRUE local maps of this polder:
  drawn Severen/Cantel hamlets on the real hamlets (church+houses match), village centre on the village,
  houses on the real village centre, watercourse on the watercourse, field parcels on the parcels; the
  residuals (3-112 m) are the 1748 map's own hand-drawn inaccuracy, not placement. So: 9 REMOVED
  (7+2), 3 STAY.
- **Removal executed (UNCOMMITTED in the working tree - the harness saves it; commit it first next
  session).** Ran /tmp/remove_beth_306a.py (the script may be gone from /tmp; the logic is below). For
  each of the 9 docs: (1) the review item `data/review/bethlehem-q2523914.c_b31c3de3630246bc.json`
  upserted with the FULL doc record (every store field: site/plan/crop/pairs/label/title/cite/at/auto/
  score/ia/file/model/src/url/ref/size/by) + `why` = the 306a audit reason (wrong place / wrong kind
  text is in the item file and in the site_flow.md lines); item now has 19 candidates, lead unchanged
  (c_b31c3de3630246bc - the file never moved). (2) doc file deleted from data/db/platefits/. After all
  9: `plan_fit.prune('.', 'bethlehem-q2523914')` (depictions.json now = the 3 1748 plan deps + the
  tmk1850 map view; the 18 removed webps deleted; prune itself called set_drawings so bethlehem
drawings=3) and ONE full `review.export('.')` -> 333 open of 346 (unchanged from session 2: the item
  was already open and stays open - open = no doc for any candidate). Design note: audit-removal item
  entries are FULL doc records, not the slim 300/303 shape, on purpose (see DECISIONS) - the 206
  mackenzie tests need the full doc, and a reviewer of a 2x fit needs the anchors/size. The shotwick
  item entry was ENRICHED the same way this session: full doc record restored from git (`git show
  6841f07^:data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json` - the file was deleted in
  6841f07; /tmp/shotwick_doc.json may be gone, re-run the git show), upserted in place with session 2's
  `why` kept verbatim, re-exported (333/346). Doc facts: by:agent, no auto/score (agent fit, the
  provenance no-batch-mark case), at 2026-10-11T19:04:44Z, 4 pairs.
- **Drawings counts refreshed** (build_site.set_drawings per site; all verified in web/data/sites.json
  now): alligator/avaricum/barnard/barwick/binche/bolsover/burlington 0->1; bethlehem 0->3 (via prune);
  aldenhaag=1, forthill=2 (site id is just 'forthill'), newark=2 ('newark') already correct; shotwick=0.
- **Tests (last full run this session, BEFORE the removals): 4 failed, 124 passed, 1 skipped in 193 s**
  - ALL 4 failures are caused by MY session-2 shotwick deletion: tests/test_fit_provenance.py::
  test_commons_yeared_title_drops_the_repeated_year + tests/test_src_mackenzie.py::
  {test_staged_row_and_join, test_gate_accepts_the_committed_doc, test_golden_sample_matches_staged}
  (all read data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json). test_gate.py is safe
  (it only uses the shotwick name as a tmp-tree stub, never reads the store). NEW breakage this session
  (will appear on the next run): test_fit_provenance.py::test_commons_yearless_title_keeps_the_label
  reads bethlehem c_075db (deleted today). The other failures seen in old driver notes (test_batch_eu,
  test_serve::test_platefits_docs_match_sites) now PASS in this checkout; test_gate stays the pre-existing
  red (excluded). NOTHING ELSE in the suite reads the 12 bethlehem or shotwick docs (grep'd).

**Exact next step (session 4).** (1) Commit the working tree (the bethlehem audit): `git add -A && git
commit -m "306a: bethlehem audit - 9 wrong docs removed (7 SoP of Judaea + 2 basilica interiors), 3 local
1748 stay; 12 lines in site_flow.md; counts refreshed"` (the tree contains the 9 doc deletions, 2 review
item files, sites.json, review.json, the bethlehem site dir, site_flow.md, this task file). (2) Fix the 5
broken tests (design settled this session; all three mackenzie + both provenance tests are on the task's
Touches line already): (a) test_fit_provenance::test_commons_yeared_title_drops_the_repeated_year - re-point
from shotwick to `bethlehem-q2523914.c_a164ee440558d66c` (year in title, batch-marked, STAYS on the map):
pin the built source line (verify by running the test's _build_source; the stored line is in depictions.json:
"...Fitted automatically by the batch on 4 matching points; one rotation and scale fits them within 113 m
(gate score 39.3 m)") and assert the year appears exactly once (`src.count("1748") == 1`) instead of the
"(1897) (1897)" check; docstring: the 303 live shotwick case is audited out, the rule stays pinned on the
surviving year-titled doc. (b) test_commons_yearless_title_keeps_the_label - keep the bergues half; re-point
the "(undated)" half (was bethlehem c_075db) to a surviving batch-marked, yearless-title, labelless doc:
candidates found (auto+score, label=None, no 4-digit year in title): durocortorum-q4896307.c_08d995eb23a685c2
(score 0.0), traiectum-q2199749.c_437d1d60e38020f7 (25.9), watson-brake-q2552689.c_5e7bb19c79b509ed (4.4),
watson-brake c_b52ddcad2ee295c4 (2.2) - pick one, verify the rebuilt line against its stored depiction line.
(c) fit/src_mackenzie.py - add `doc_record()`: the doc's dict from the store file if it exists, else from the
review item (scan data/review/*.json for item["site"]==SITE and the candidate with plan==PLAN; keep the module
top stdlib-only - no fit/review import). Re-point: gate() reads doc_record()["pairs"]; check() treats an
item-resident record as the doc (drop the "not written yet" problem in that state; keep the size/pairs
checks); golden() writes doc_record() with at normalized. Update the module docstring's --gate/--check/
--golden lines. (d) tests/test_src_mackenzie.py - all three: `d = mack.doc_record()` instead of
`json.load(open(mack.DB_DOC))`; existing assertions unchanged (the item entry carries every doc field);
add in test_staged_row_and_join: when the store file is absent, assert `d["why"]` non-empty and mentions
the audit; update docstrings (the committed doc was removed by the 306a audit as ~2x too big; its record is
the review item's candidate; the gate ACCEPTING its pairs is exactly the gate's blind spot - 4 corners of a
2x ring pass with 2-19 m residuals). (e) Regenerate the golden: `.venv/bin/python fit/src_mackenzie.py
--golden` (the module's own intended-change mechanism; 303's commit 1f562ca last re-baselined it the same
way) and commit tests/golden/src_mackenzie_sample.json (golden["doc"] is now the full item entry with at
normalized). (3) Full suite `.venv/bin/python -m pytest tests/ -q --ignore=tests/test_gate.py` - target:
124+ passed, 0 failed, 1 skipped. (4) Tick boxes 1+2 (the removals are done: shotwick + the 9 bethlehem docs,
all with the item record + prune + export, counts refreshed; box 2's site_done text was replaced by the 4
calls for the documented matcher reason - see session 2's DECISIONS), set Status: done, and note in the
hand-over that 306b-f can append below the section. Section order now: aldenhaag, alligator, avaricum,
barnard, barwick, binche, bolsover, burlington, forthill, newark, shotwick, then the 12 bethlehem lines -
all 23 contiguous at the top; later subtasks append below the bethlehem lines.

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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/306a-agent-fits-on-map.md` (open) - hand-over: (2026-10-12, iteration 135, agent c - session 1 of 306a; cut at the context limit during the visual
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/221-review-stats-test.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-12 306 DECISION: split into six look-audits by visibility class and region
- Box 1 of 306 covers ALL 112 non-hand docs (23 on-map, 21 in review items, 68 orphans - the orphan
  class is new to the project: in the store but neither built as an overlay nor referenced by any
  review item, so a visitor can see them not at all; audited by rendering the doc's saved pairs in
  the fit tool). Six subtasks: 306a on-map (23), 306b review (21), 306c orphan US (15), 306d orphan
  UK part 1 (18), 306e orphan UK part 2 (15), 306f orphan continental (17). A before B before C:
  only A sits on the map (the title's "none reaches the map unseen"); only 306a performs the
  removals (box 2). No subtask carries `Depends on: 306` (a split parent deadlocks its own
  subtasks - PITFALLS); the driver hands them out a-f.
- The audit is headless-browser work, not a test: serve the tree once (server/serve.py --port 0,
  ephemeral port, GET-only - safe for parallel checkouts) and drive the real page through
  tools/shot.mjs's [js] argument: select(site) -> setGround('imagery'|'relief', site) ->
  startFit(site) -> openPlan(row) -> push the doc's pairs as {u,v,lon,lat} + addPairMarker +
  refit (refit renders the fitted plate as the fit-prev map source; web/review.js does exactly
  this for item pairs, L142-146/L189-196). On-map docs go the visitor's way instead: open the
  site, activate the depiction (applyDep). This VM HAS internet (Esri World_Imagery 200 in 0.17 s,
  verified this session): the "no-internet headless" pitfall applies only to the no-network test
  runs. LiDAR on the page is the per-site prebuilt relief.jpg (index.html L367-368), not the live
  /tiles/relief (off here, `aw` is Mac-only); shotwick has no relief.jpg (aerial-only).
- For the 21 B docs the doc's stored pairs DIFFER from the review item's candidate pairs (except
  castle-neroche n0110_1): the audit renders the DOC's own pairs (the document is the artifact)
  and the verdict notes where the item's version differs.
- All 112 docs carry 4+ pairs, so every one renders as a fitted plate (simFit needs 3). sites.json
  `drawings` are stale for most A-group sites (0 despite the overlay present; only aldenhaag=1,
  forthill=2, newark=2 non-zero) - 306a's rebuild via tools/site_done.py fixes the counts for the
  sites it changes.

### 2026-10-12 306a DECISION: audit driver built and the full 45-shot run launched in the background; four docs judged (all stays); parent split completed (306d/306e/306f created, 306c count fixed to 16)
- tools/audit_306a.mjs: one `server/serve.py --port 0` for the whole run; per shot the page is driven
  the visitor's way (select -> S.depSel = the doc's depiction file -> setGround -> applyDep) and shot.mjs
  screenshots at 1440x900. The [eval] line confirms the active depiction; the [audit] line prints the
  stored fit stats from depictions.json. Run: `node tools/audit_306a.mjs [site ...]` from the project
  root; re-run is idempotent. Background run: `nohup node tools/audit_306a.mjs > /tmp/audit_306a.log
  2>&1 &` (16/45 at context-limit, all written, no pageerrors).
- FAILED (twice, same root causes, both fixed): (1) shot.mjs's `page.evaluate(js)` with `js =
  'async () => {...}'` returned undefined - Playwright 1.63 treats the string as an expression and does
  NOT auto-invoke a function string; fix: wrap as an IIFE `(async () => {...})()` (verified with a
  throwaway probe page). (2) `window.S` is undefined in page context - S is a top-level const (page-wide
  lexical environment, not globalThis); fix: bare `S` with a typeof guard. Both are now PITFALLS
  candidates (filed in the 306a hand-over; the context-limit message barred editing PITFALLS.md).
- Judged (aerials): aldenhaag 1832 kadaster detail, alligator-effigy-mound 1891 map, avaricum Caesar
  (Allen & Greenough) map, barnard-castle 1843 tithe map - all four are georeferenced sheets
  (identity or near-identity fits, gate <= 0.1 m) whose ink sits on the real ground (village/terp,
  mound park, Cher town centre, Alnmouth streets+river). All STAY. The interesting cases are the rest
  (true similarity fits): bethlehem x12 (up to 25.7 m resid, rot 4.7), shotwick (14-19 m), binche,
  bolsover, burlington, forthill, newark.
- The parent's split counts were off: UK part 2 (o-y) is 17 docs, not 15 (old-sarum/pontefract/
  portus-adurni/york-castle carry two each), and the US orphan set is 16 (marietta.b24849959_n0195_1 -
  a US site, already in 306c's list but not its 15 header). Created 306d (UK a-l, 18), 306e (UK o-y,
  17), 306f (continental, 17); corrected 306c to 16. Total 23+21+16+18+17+17 = 112 = all non-hand docs.
- False alarm I nearly logged: fort-ancient-q5470727 looked missing from web/data/sites.json, which
  would have failed test_platefits_docs_match_sites - it was a typo in my own probe list ('fort-ancient'
  without the qid). The test passes; all 133 store docs' sites are in sites.json.

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (1 tests)
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_gate.py:36: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    1 failed, 59 passed in 63.50s (0:01:03)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

## 306a session note (iteration 136, agent c) - where the work stands
Session 2 of 306a (full detail in tasks/306a-agent-fits-on-map.md ## Hand-over): the 45-shot audit
run finished clean; 11/23 lines written in docs/site_flow.md (10 STAY + shotwick REMOVED - the
2x-too-big fit, proven from the plate's measured extent and NHLE 1016616; removed via upsert_item +
doc delete + plan_fit.prune + review.export, NOT site_done, because the reachable matcher would
have placed a new unaudited fit). MAJOR OPEN FINDING: the bethlehem-q2523914 site is the DUTCH
village (Het Hogeland, Groningen), so its 7 "Survey of Palestine" ground sheets look like a
toponymic collision (maps of Judaea fitted ~2000 km away), its 2 basilica plans are building
interiors fitted as ground maps (wrong kind), and its 3 1748 map details look like true local maps;
next session confirms Q2523914 + the docs' pairs' lon/lat cluster before any bethlehem doc is
judged or touched.
