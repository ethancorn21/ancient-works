Status: open
# 307d: The owner's check - two queue sites end to end, then reverted
Depends on: 307c
Touches: tests/, docs/site_flow.md

## Goal
The last box of 307: "Saving still writes 'by': 'hand' and runs the one-site line (305),
and the existing hand fits load and save unchanged. Checked in a real browser on two queue
sites the way the owner uses it (place, move, scale, save, see it on the map), then the
test fits reverted. Tests cover the queue place-check and the save path." The place-check
tests are 309's; this task proves the save path end to end in a real browser on two queue
sites and proves the shared store comes back byte-identical.

## Acceptance criteria
- [ ] A new tests/ file runs the owner's flow in a real headless browser (Chrome, the
      305-part-3 pattern) against the real server on a private copy of the tree (the 305
      part-2 precedent: real data, no network, ephemeral port): on two queue sites (pick
      ones with a recorded bar scale and a site-size-only fallback, and different ground
      where possible - LiDAR relief vs aerial photograph) the test does what the owner
      does: open the queue, place the drawing (the on-map start), move it, scale it,
      save; then verifies the saved doc carries "by": "hand" and the one-site line ran
      (the overlay on the map in the site's depictions, the site square coloured, the
      review item resolved, the queue moved on), and after a page reload the fit loads
      back unchanged (same placement, same overlay).
- [ ] The test fits are reverted before the test ends: the private tree is discarded, and
      the shared store in the repo is proven byte-identical to before the test (the golden
      hand-fit hash check tests/golden/hand_fit_docs.sha256 and test_fit_provenance stay
      green; web/data/fit_queue.json and the review exports untouched).
- [ ] docs/site_flow.md: the verification section (what was checked, on which two sites,
      which way, and the screenshots), closing the parent's last box.

## Notes
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-13, iteration 242, agent a - THIRD session; investigation completed: picks re-verified
by re-running the scan AND re-checking every page/server/line mechanism against the CURRENT
code on this branch (307c merged - refs re-confirmed, none shifted). NO files changed, NO
tests run. The entire spec the test must implement is verified below. NEXT SESSION: write
tests/test_owner_check.py straight from this hand-over (every fact it needs is listed), run
it, fix what fails (lead's rule: commit a failing test as-is), then the docs section.)

**State:** all boxes unticked; tests/test_owner_check.py does not exist yet. Suite baseline
(driver notes, re-run before claiming): 155 passed / 1 skipped / 1 failed - the one red is
235's test_placement_gestures_and_save_in_the_browser (its `_pick_place` lands on marietta;
my test does not touch it and must not depend on its fix).

**Picks (re-verified this session; queue 241 entries, `at` 2026-10-13T14:34:09.559141+00:00,
file did not move):**
- A (bar scale) = [38] oswestry-castle-q20713795 / row earthworkenglan01allcgoog_n0119_1:
  bar mpx 0.1646 rot 0; row book 'Allcroft 1908', label 'Fig. 17', title 'Camp, Old Oswestry,
  Salop', map_box [0.198,0.168,0.875,0.778], size [3367,5050], url null; page n0119.jpg natural
  (3367,5050) (frame scale 1); item file data/review/oswestry-castle-q20713795.
  earthworkenglan01allcgoog_n0119_1.json (ONE candidate = the queue row, 3 pairs, unresolved);
  depictions.json = [six-inch-1st.webp map 1842, os1inch.webp map 1900] (1900 DROPPED by the
  150-yr filter: 2026-1900=126) -> page auto-dep six-inch-1st.webp; sites.json: drawings 0,
  score 1.1, oldest 1842, lidar None, credit 'Environment Agency, Crown copyright, Open
  Government Licence v3.0'; open in web/data/review.json (457 open, at 2026-10-13T14:34:07).
- B (site-size fallback) = [45] devil-s-dyke-q3307343 / row earthworkenglan01allcgoog_n0662_1:
  picture_size coarse mpx 0.7201 rot 0; row book 'Allcroft 1908', label '', title 'SWEALD',
  map_box [0.2,0.15,0.85,0.7], size [3367,5050]; page n0662.jpg natural (3367,5050); item file
  data/review/devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0599_1.json (3 candidates:
  lead n0599 3 pairs, n0686 4 pairs, n0662 4 pairs 'line check: fabricated anchor pattern...';
  UNRESOLVED); same deps/sites.json/credit as A; open in review.json. uncovered=0 for both.
- PICKER (derived, never pinned): eligible = line-eligible (book row ia/file; page file in
  CHECKOUT data/raw/books/<ia>/full/; unresolved item carrying the row with >=3 pairs; no
  platefits docs for the site) AND a page-showable auto dep (first drawing-kind or LAST
  map-kind after the surveyOldEnough filter) AND no pre-existing drawing-kind dep. A = first
  eligible with scale_source 'bar'; B = first eligible with 'picture_size' whose lidar_credit
  differs from A's, ELSE fallback first qualifying. Today: 25 raw line-eligibles ([28],[29],
  [38],[45],[46],[47],[48],[49],[50],[52],[53],[55],[59],[62]-[66],[70],[100],[102],[104],[105],
  [185],[204] - [49] beam-farm and [50] piketon are NEW this session but have NO showable dep
  (topo-only-young / no depictions.json) so they drop out of the picker; the 15 with a
  showable dep are all EA-credit -> B is the fallback pick. The test's picker recomputes this
  at run time from the CHECKOUT (never pin ids). Done seed for a site's run =
  {entries[i].site: AT for i < the site's index} from the tree's own fit_queue.json.
- Both picks: lidar=None (LiDAR relief; page ground in place mode = 'relief'). NO `lidar:
  False` aerial-only site is line-eligible (every aerial-only queue site is a commons-row
  candidate, no local page) -> the task's "different ground" hedge is NOT satisfiable; both
  picks sit on LiDAR relief. SAY SO PLAINLY in the docs section.

**Template (307bb part 4, tests/test_fit_queue.py - READ IT WHOLE FIRST):** `place_served`
L1673-1720 (the fixture recipe: conftest.copy_web(tree, real={site}) + copy server/tools/fit/
pipeline + data minus data/raw and .npy/.npz; materialise the book page into the tree's OWN
data/raw; Popen `[sys.executable, "-c", GUARD, "server/serve.py", "--port", "0"]` cwd=tree;
GUARD L98-115 kills every socket in the server process; reader thread appends to `out`; poll
"Ancient Works on (\S+)" 90 s then GET / 30 s) and `PLACE_PROBE` L1289-1650 (node;
`createRequire(process.env.NODE_PATH + '/')` -> playwright-core; CHROME
/opt/google/chrome/chrome; NODE_MODULES /home/agent/tools/shot/node_modules; run: node
<probe> <base> <site> <plan> <tree> <outdir> <doneJson> cwd=ROOT env NODE_PATH, timeout 600;
parses one `[eval]` JSON line; RESULT PASS/FAIL + exit code). `_headless_or_skip` L1130,
`_write_surface` L1723, `AT` L725, `_h` L365, `_line_eligible` L758, `_item_of` L728,
`_rows_naming` L741, `_review_items` L748. COPY GUARD/CHROME/NODE_MODULES/_headless_or_skip
into my new file (do NOT import from test_fit_queue.py - 235 owns it).

**The probe flow to write (mirrors 307bb's, then adds the line's four effects + reload):**
addInitScript seed aw.fitQueue.done=doneJson -> goto -> boot poll (S.ready && S.sites.length
&& FQ.loaded && FQ.entries.length) -> card1 read (assert in-page: names the pick's e.name and
row title - get them from FQ.entries.find(x=>x.site===site).best) -> screenshot 1-card.png ->
#fqplace click -> poll P.placed===true && P.img -> sleep 2500 (fly-to) -> seed checks
(verbatim 307bb: anchor == propose's LAST pair to 1e-9 in mpx/rot/centre; n===5 pairs and
marks; fitPrev source; gestures [dragPan,scrollZoom,touchZoomRotate,doubleClickZoom,boxZoom]
all disabled; dep layer 'dep-<site>' visibility 'none'; hint contains anchor.mpx.toFixed(2)
+ 'm per page pixel') -> screenshot 2-placed.png -> inject 307bb's HELPERS (_fkvAnchorAt,
_fkvFitChecks) -> drag: pick a clear canvas point (307bb's candidate list + marker-distance
check), mouse down/move(+30,+20,2 steps)/up; expected anchor = anchor-at-down + pointer
Mercator delta (307bb's dragStart evaluate); checks (anchor delta <1e-6; mpx/rot/u0/v0
unchanged; pair5 == anchor at doc rounding; fit dmpx<1e-3 drot<0.01; maxResid<2; maxCorner
<0.2 closure<0.2) -> wheel -100 (wheelBase = simFit(P.pairs).mpx FIRST - the absorbed fit;
mpx *= exp(0.15); centre/rot held) -> shift+wheel +100 (rot += 1.0; scale held to 1e-3)
-> record pairsBefore (5 final) + imgSize [naturalW,naturalH] -> #fsave -> poll !P.active
120 s -> then in-page poll (120 s total) the LINE's four effects through fetches to the tree:
  (a) `data/sites/<site>/depictions.json?t=`: entry with fit.doc===docId (kind 'plan', file
  plan_<plan>.webp, ink plan_<plan>_ink.webp) and fit.at === the page's doc at; page's dep
  layer 'dep-<site>' now 'visible' with source url `data/sites/<site>/plan_<plan>_ink.webp`
  and S.depSel[site] === overlay.file;  (b) `data/sites.json?t=`: entry.drawings === before+1,
  entry.score changed; page marker el.className === `marker ` + tierOf(S.byId[site]) (TIERS
  [[2.5,'t4'],[1.6,'t3'],[1.2,'t2'],[0.01,'t1']] else 'plain');  (c) `data/review/<itemFile>`
  (pass itemFile as probe arg): item.resolved === {doc: docId, at: docAt}; `data/review.json?t=`:
  site NOT in items[].site;  (d) FQ.done[site] set in localStorage (the _fqSaveFit wrapper;
poll it) and #fqcard now names the NEXT pending = FQ.entries.filter(e => e && e.site &&
  S.byId[e.site] && !(e.site in FQ.done) && !FQ.skipped.includes(e.site))[0] (the page's own
  fqPending rule) and does NOT name the pick -> screenshots 3-gestured.png (before save),
  4-saved.png -> page.reload() (SAME context: aw.depSel + aw.fitQueue.done persist) -> boot
  poll -> RELOAD checks: S.sel===site (hash '#<site>' drove select); S.ground==='imagery'
  (select L828 unconditionally resets it - the page contract, NOT 'relief'); S.depMode==='ink',
  S.plateMode==='ink'; S.depSel[site]===overlay file (the persisted depSel beat select's
  default-pick); dep layer 'dep-<site>' 'visible' src the ink url; marker className ===
  'marker ' + tierOf(S.byId[site]) (the fresh sites.json score); S.byId[site].drawings ===
  before+1; FQ.done[site] still set and card still names the next pending (not the pick)
  -> screenshot 5-reload.png -> print [eval] {anchor, pairs, imgSize, doc (fs read of the
  tree doc), overlay, sitesEntry, item, reviewOpenSites, done, card1, card2, reload{...},
  markerClass, markerClassReload} -> console all non-console lines -> RESULT PASS/FAIL ->
  exit 0/1. Allowed reqfails only: '/tiles/', 'arcgisonline', 'MapServer/tile/' (MapLibre
  aborted tile fetches; the page's live Esri base) - no other reqfail, no pageerror.

**Python-side checks per site (read from the TREE, not the checkout):**
1. doc at tree/data/db/platefits/<docId>.json: by==='hand' (the store stamped it), site/plan/
   ia/file, model 'similarity', src 'book', url null, ref, size === imgSize === row.size,
   crop === [round(mb[0]*W), round(mb[1]*H), round(mb[2]*W), round(mb[3]*H)] (row.map_box
   [0.198,0.168,0.875,0.778]x[3367,5050] etc; [0,0,W,H] when a row has no map_box), pairs ===
   the probe's final 5 EXACTLY, at ISO 2026.
2. stdlib simFit of doc.pairs (the page's simFit L1004-1021 ported: W=[u,-v]; Z=merc
   (R=6378137, L359-361); a=(nr/d,ni/d), nr=Σ zr*wr+zi*wi, ni=Σ zi*wr-zr*wi, d=Σ wr²+wi²
   over centred pairs; b=(zm-(a*wm conj), zm-(a*wm imag part)); at(u,v)=(a0*u+a1*v+b0,
   a1*u-a0*v+b1); k=cos(pairs[0].lat rad); mpx=hypot(a)*k; rot=deg(atan2(a1,a0)); resid per
   pair hypot(at-Z)*k): mpx within 1e-3 of the placed anchor, rot within 0.01 deg, max resid
   < 2.
3. overlay (tree depictions.json): kind 'plan', file/ink names, webps exist and realpath in
   the tree (fixture materialised the site dir - assert not sd.is_symlink()); fit: doc,
   at===doc.at, pairs 5, model, resid_m len 5 all <1 (rounded 1dp by build), rot_deg within
   0.01 of anchor.rot (build rounds to 2dp), m_per_px within 1e-3 of anchor.mpx*fs/f with
   fs=natural/size(=1) and f=min(1, MAX_PX/max crop px) - READ MAX_PX BY REGEX from the
   tree's pipeline/plan_fit.py (L44, =2400); source contains 'Placed by hand'; year ===
   first 4-digit year in book+' '+label (regex r"(?<!\d)(1[2-9]\d\d)(?!\d)") = 1908.
4. sites.json (tree) entry: drawings === before+1; score === recomputed build_site.score:
   overlays = (1908, rms(resid_m), True) + (1842, 8, False) [the six-inch's SERIES_ERR_M is 8
   via label 'Ordnance Survey six-inch map...'; the 1900 os1inch is <150 old -> excluded]
   -> vals desc; score = round(best + 0.25*sum(rest), 2) (expect ~1.46, tier t2 - the 1842
   map alone gave 1.1/t2, so the square's tier is unchanged but its size/score move);
   oldest 1842; overlays count 2. Assert the page's marker class (probe) === tierOf(score)
   with the same TIERS.
5. item (tree): resolved === {doc: docId, at: doc.at} (write-once; file name unchanged).
6. review.json (tree): after A's run: A NOT in open list, B STILL in it (open count -1);
   after B's run: neither in it (count -2 vs before both). A's item already recorded -> B's
   export does not rewrite A's item file (write-once condition `not resolved.doc`).
7. server `out` log: for each run a line 'one-site line for <site>: finished (exit 0)' (note
   the two-space indent in the print), no 'failed', no 'attempted a network connection'.
8. REVERT PROOF: _write_surface(picks) before and after each run equal - hash (sha or raw
   bytes) of: all data/db/platefits/*.json + all data/review/*.json + web/data/sites.json +
   web/data/review.json + web/data/fit_queue.json + every file under web/data/sites/<A>/ and
   web/data/sites/<B>/ in the CHECKOUT (they are symlinks into the shared store at
   /home/agent/projects/ancient-works - hashing through them proves the shared store never
   moved). tests/golden/hand_fit_docs.sha256 + test_fit_provenance stay green in the full
   suite for the same reason (they run on the checkout; it is untouched).
9. Screenshots: copy the probe's outdir PNGs into docs/site_flow/ as
   307d_A_<name>.png / 307d_B_<name>.png (1-card, 2-placed, 3-gestured, 4-saved, 5-reload).

**Fixture:** one module-scoped `owner_served` = line_served's recipe with BOTH site dirs in
`real` and BOTH pages materialised; ONE server; yield {base, tree, proc, out, picks:{site:
{entry, row, plan, site, item, itemFile, depFile('six-inch-1st.webp'), sitesBefore (the
sites.json entry), done (map of all earlier queue sites -> AT), scale_source}}}; teardown
terminate/kill. Two test functions (A then B, file order = pytest order; B's run sees A's
tree state - by design, both sites' dirs are real copies in the tree). Each runs its probe
(timeout 600), then the Python checks 1-8, then copies screenshots (9). If a check fails:
commit the test AS-IS, name the failing check + probe [eval] dump in DECISIONS (lead's
307bb rule), fix next session.

**Exact next step (one session):** (1) re-run /tmp/aw307d/scan_picks.py once (population
drifts under merges; if A or B no longer qualifies, the test's picker re-derives - the
fixture must fail with a clear message if NO pick qualifies, never pin ids); (2) write
tests/test_owner_check.py per the spec above; (3) run `.venv/bin/python -m pytest
tests/test_owner_check.py -q` (~5-10 min: two browser runs + two lines; the first line is
~23 s with its heavy imports, the second is cached); (4) run the full suite once to confirm
only 235's red remains; (5) docs/site_flow.md section (after the 308 section): what was
checked, the two derived sites and the picker rules, both on LiDAR relief (state plainly
that no aerial-photograph ground was available this session and why), the line's four
effects, the reload, the revert proof, the screenshots; tick the boxes; DECISIONS entry;
commit.

**Do not touch:** fit/surveyfit.py or task 304 (agent c); tests/test_fit_queue.py (235's
file); tests/conftest.py (ask for shared fixtures in DECISIONS instead); any data file in
the checkout (the test writes only into its private tree).
