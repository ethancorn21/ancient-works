Status: open
# 307d: The owner's check - two queue sites end to end, then reverted
Depends on: 307c
Touches: tests/, docs/site_flow.md, docs/site_flow/

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

(2026-10-13, iteration 245, agent a - FIFTH session; investigation only, NO code written, NO tests run. Re-verified every mechanism against the current code by reading whole: tests/test_fit_queue.py (all 1765 lines: GUARD L98-115, AT L725, _h L365, _item_of L728, _rows_naming L741, _review_items L748, _line_eligible L758, _pick_site L776, line_served L803, part 2 test, CHROME/NODE_MODULES L1024-1025, _headless_or_skip L1130, part 4 PLACE_PROBE L1289-1650, _pick_place L1653, place_served L1673, _write_surface L1723, part 4 test), web/fitqueue.js whole, tests/conftest.py (copy_web), pipeline/build_site.py whole, web/index.html L312-319 (S init), L425-478 (loadDeps/surveyOldEnough/applyDep/TIERS/tierOf/markers), L750-845 (renderSite/setGround/select), L864-960 (startFit/endFit/openPlan), L1004-1181 (simFit/need/refit/saveFit), L1690-1749 (start(), script order index->review->fitqueue->fitkit); web/fitkit.js whole; tools/site_done.py whole; fit/review.py whole; fit/matchfit.py reachable L103-108; pipeline/plan_fit.py build L310-370, source_line L274-309, similarity L94-104, _year4 L267-271, MAX_PX=2400 L44; pipeline/aw.py to_merc/ground_scale (R=6378137); server/serve.py L215-257 (PUT stamps by:hand then after_write -> _fit_line; log "  one-site line for <site>: finished (exit N)" with TWO-space indent, "failed" and "unavailable" variants); pipeline/depict.py MIN_AGE_YEARS=150. Then re-ran the pick scan (below). NEXT SESSION: write tests/test_owner_check.py straight from the spec below, run it, then the docs section. One correction to 243's fact 6 is flagged first.)

**CORRECTION TO 243 FACT 6 (tier BEFORE the run):** both picks' current score is 1.1 in the checkout's sites.json, and the page's tierOf (TIERS [[2.5,'t4'],[1.6,'t3'],[1.2,'t2'],[0.01,'t1']], index.html L475-476) gives 1.1 -> **t1**, not t2 (243 said "1.1 -> t2 BEFORE" - arithmetic slip, 1.1 < 1.2). Recomputed AFTER the run (build_site.score port: overlays = [(1908, rms(resid_m of the 5 pairs), True) (new drawing) + (1842, 8, False) (six-inch, SERIES_ERR_M 'Ordnance Survey six-inch':8); the 1900 os1inch is excluded: 2026-1900=126 < 150; vals desc, score = round(best + 0.25*sum(rest), 2)): for year_now=2026 -> 1.18*1 + 0.25*1.10 = ~1.45 -> **t2**. So the square's tier CHANGES t1 -> t2 after the save (that is the parent box's "site square coloured"); the probe must assert className === 'marker ' + tierOf(the fresh score) computed in-page with the page's own tierOf (never hardcode a tier - year_now moves), and the docs section states the observed t1->t2.

**New session-245 facts (add to 243's list; 1-10 of 243 all stand, re-verified this session):**
11. **Boot with a hash never runs renderList** (start() L1703-1711: S.byId[id] ? select(id) : renderList()): after page.reload() on '#<site>' the site view renders but FQ.loaded stays FALSE and FQ.entries stays [] until the first #back -> renderList (the _fqRenderList wrapper then fires fqLoad async). So the RELOAD boot poll must be only S.ready && S.sites.length (NOT FQ.loaded/FQ.entries - it would time out), and card3 must POLL for #fqcard to appear after the #back click (the fetch is local, a few seconds). FQ.done itself is fine after reload: it is initialised from localStorage at script load (fitqueue.js L21).
12. **Next pending entries (today; the fixture recomputes from the tree's fit_queue.json, never pins):** A [38] -> entries[39] neckarburken-west-q1343017 'Neckarburken-West'; B [45] -> entries[46] richard-s-castle-q17650937 "Richard's Castle". The picker must require an entry to follow the pick in file order (both do; queue 241, at 2026-10-13T14:34:09.559141+00:00, unchanged this session).
13. **Both site dirs are symlinks in the checkout (re-verified islink True); size_m: oswestry [800,800], devil-s-dyke [2000,2000]** (only used via the sites.json entry; the doc size is the image's natural size = the row's size [3367,5050]).
14. **saveFit success path re-confirmed verbatim (index.html L1151-1181):** page poll 60x1.5s for a depiction with fit.at === the page's at; then S.dep[site] = fresh depictions, S.depSel[site] = overlay.file + lsSet('aw.depSel'), fetch data/sites.json and copy drawings/score/oldest/overlays into S.byId[site], mk.el.className = 'marker ' + tierOf(s), removes the dep source/layer, endFit() (the fitkit wrapper re-applies applyDep) + its own applyDep -> the overlay is ALREADY the visible dep after save (depMode 'ink' -> ink url). On poll timeout it keeps the pane open with 'Saved, but the overlay has not appeared yet' - the probe's !P.active poll (120 s) is the guard.
15. **fitkit endFit wrapper + _fkActivate re-confirmed:** on close (save included) applyDep(site) runs with S.depSel/depMode/ground untouched; while placed the dep layer is 'none' (243's seed check) and _fkActivate flies to the site's own corners box with duration 900 (hence the 2500 ms settle sleep after the placed poll, and ~5 s before the reload screenshot for select's 4500 ms flyTo).

**Spec for tests/test_owner_check.py (the one step to write next; everything it needs is in this hand-over + 243's):**

Module header: task 307d (the parent 307's last box): the owner's flow in a real headless browser on two derived queue sites - place on the works (the card's Place), move (one drag), scale (wheel), turn (shift+wheel), Save - then verify through the page and the tree: the saved doc by:hand, the overlay on the map, the site square recoloured (t1->t2), the review item resolved, the card moved on; reload shows the fit unchanged; the private tree is discarded and the checkout's write surface hashes byte-identical (the golden hand_fit_docs.sha256 + test_fit_provenance stay green in the full suite for the same reason). Screenshots land in docs/site_flow/ as 307d_{A,B}_<name>.png.

Imports/constants: json, math, os, re, shutil, subprocess, sys, threading, time, datetime (for at parse), pathlib.Path; pytest; from conftest import copy_web, get, get_json, put_json; ROOT; CHROME = "/opt/google/chrome/chrome"; NODE_MODULES = "/home/agent/tools/shot/node_modules"; AT = "2026-10-12T00:00:00.000Z". COPY into the new file (do NOT import from test_fit_queue.py - 235 owns it): GUARD (verbatim), _h, _item_of, _rows_naming (root-parameterized), _review_items, _line_eligible (verbatim, it reads ROOT/data/raw), _headless_or_skip. NEW helpers below.

NEW helper _auto_dep(sd): mirror the page's loadDeps+select default-pick: read sd/depictions.json; keep kind not in ('map','aerial','topo') OR (year and year <= current year - 150); return first kind in ('plan','drawing','view') else LAST kind 'map'; None when nothing remains (243's page-showable auto dep).

NEW helper _derive_picks(): read the CHECKOUT's web/data/fit_queue.json + _review_items() + sites.json (for lidar_credit). eligible = entry has propose AND isinstance(_line_eligible(e, items.get(e['site'])), list) (the uncovered-rows list, which must be EMPTY for the no-batch log assert - require li == [] for the pick: both current picks satisfy it, and it is what makes the line's no-model path the only path) AND _auto_dep(the site dir) is not None AND no pre-existing depiction with kind in DRAWING AND an entry follows it in file order. A = first eligible with propose['scale_source'] == 'bar'; B = first eligible with 'picture_size' whose sites.json lidar_credit differs from A's, ELSE first eligible 'picture_size'. If A or B missing: return (None, '<clear message with what was found>'). Per pick record: {site, name, entry, row (best.row), plan (best.plan), item (the review item dict), itemFile (path in CHECKOUT), depFile (the _auto_dep file), before (the sites.json entry dict verbatim), scale_source, done (None yet)}. Return (picks dict {'A':..., 'B':...}, error or None).

Fixture owner_served (module scope): _headless_or_skip(); picks, err = _derive_picks(); assert picks, err. a, b = picks['A'], picks['B']; tree = tmp_path_factory.mktemp('awowner'); copy_web(tree, real={a['site'], b['site']}) (both site dirs materialised into the tree); copy server/, tools/, fit/, pipeline/ into the tree; shutil.copytree(ROOT/data -> tree/data) with ignore = data/raw + .npy/.npz (307bb's recipe); materialise BOTH book pages into the tree's OWN data/raw/books/<ia>/full/<file> (shutil.copy2 from the checkout's data/raw) and record their Image.open(dst).size per pick. Start ONE guarded server: Popen [sys.executable, "-c", GUARD, "server/serve.py", "--port", "0"] cwd=tree, stdout=PIPE stderr=STDOUT text=True; reader thread appends to `out`; poll "Ancient Works on (\S+)" 90 s; then GET / 30 s. Read the TREE's web/data/fit_queue.json (byte-identical to the checkout's) and set picks[t]['done'] = {e['site']: AT for e in entries[:i]} where i = the index of t's entry (the card's seed past every earlier entry; A's done map has 38 entries, B's 45 - B's includes A's site). yield {base, tree (Path), proc, out, picks}. Teardown: terminate, wait 10 s, kill on timeout.

Two test functions, file order A then B (B's run sees A's tree state by design; the fixture is module-scoped so ONE server serves both):

def test_owner_flow_A(owner_served, tmp_path_factory): _run_one(owner_served, 'A', tmp_path_factory, prev_item_bytes=None)
def test_owner_flow_B(owner_served, tmp_path_factory): _run_one(owner_served, 'B', tmp_path_factory, prev_item_bytes=owner_served['picks']['A']['itemAfterA_bytes'])

_run_one(served, tag, tmp_path_factory, prev_item_bytes):
  p = served['picks'][tag]; site, plan = p['site'], p['plan']; doc_id = f"{site}.{plan}"; outdir = tmp_path_factory.mktemp(f'owner{tag}shot')
  surface = _write_surface(served)  # BEFORE
  (outdir/owner_probe.mjs).write_text(OWNER_PROBE); p2 = subprocess.run(["node", str(outdir/"owner_probe.mjs"), base, site, plan, str(tree), str(outdir), json.dumps(p['done']), str(p['itemFile'])], cwd=str(ROOT), env=dict(os.environ, NODE_PATH=NODE_MODULES), capture_output=True, encoding='utf-8', errors='replace', timeout=600)
  assert p2.returncode == 0 and "RESULT PASS" in p2.stdout, (p2.returncode, p2.stdout[-4000:], p2.stderr[-2000:], served['out'][-30:])
  data = the [eval] json line
  Then the Python-side checks (each with a clear assert message):
  1. DOC (tree data/db/platefits/<doc_id>.json): by=='hand'; site/plan/ia/file == row's; model 'similarity'; src 'book'; url is None; ref is None; label/title/book/cite == row's; size == data['imgSize'] == row['size']; crop == [round(mb[0]*W), round(mb[1]*H), round(mb[2]*W), round(mb[3]*H)] from row['map_box'] (or [0,0,W,H] when absent); pairs == data['pairsBefore'] EXACTLY; at parses with datetime.fromisoformat and matches /^2026-/ (the page's clock).
  2. FIT (stdlib port of the page's simFit - index.html L1004-1021: W=[u,-v]; Z=merc R=6378137; centred least squares a=(nr/d,ni/d), b=[zm0-(a0*wm0-a1*wm1), zm1-(a0*wm1+a1*wm0)]; at(u,v)=[a0*u+a1*v+b0, a1*u-a0*v+b1]; k=cos(lat0 rad) with lat0 = mean lat for the plan_fit-style checks and pairs[0].lat for the page-style one); over doc['pairs']: mpx within 1e-3 of data['anchorBeforeSave']['mpx']; rot within 0.01 deg of data['anchorBeforeSave']['rot']; max resid < 2 m.
  3. OVERLAY (tree web/data/sites/<site>/depictions.json): the entry with fit.doc==doc_id: kind 'plan'; file 'plan_<plan>.webp'; ink 'plan_<plan>_ink.webp'; BOTH webps exist, os.path.realpath under the tree, and the site dir is not a symlink (fixture materialised it); fit: pairs 5, model 'similarity', at == doc['at'], doc == doc_id, resid_m len 5 all < 1, rot_deg within 0.01 of anchor rot (build rounds 2dp), m_per_px within 1e-3 of anchor.mpx * fs/f with fs = imgSize[0]/doc.size[0] (=1) and f = min(1, MAX_PX/max(crop px) * fs...) computed EXACTLY as plan_fit.build L339-344: f = min(1.0, MAX_PX/max(crop.size)) with crop in fs-scaled px, m_px = |a|*k/fs... (mirror the probe's check: wantMpx = anchor.mpx * fs / f, MAX_PX read BY REGEX ^MAX_PX = (\d+) from the TREE's pipeline/plan_fit.py); source ENDS WITH f"Placed by hand on 5 matching points; one rotation and scale fits them within {m} m." with m = math.ceil(max resid in metres over the fs-scaled pairs, k = cos(mean lat)); year == int(first (?<!\d)(1[2-9]\d\d)(?!\d) in doc['book'] + ' ' + str(doc['label'] or '')) (= 1908 today); label field == f"{book}: {title or label}".
  4. SITES (tree web/data/sites.json entry for site): drawings == p['before']['drawings'] + 1; score == recomputed with the build_site.score port (overlays from the TREE's depictions.json: DRAWING kinds -> (year, rms(resid_m) or 30, True); others only when year <= now-150 -> (year, next((e for k,e in SERIES_ERR_M.items() if k in label), 100), False); vals desc, round(best + 0.25*sum(rest), 2), year_now = time.gmtime().tm_year); oldest == min years; overlays == len(ovs); and the entry equals {**p['before'], drawings/score/oldest/overlays: recomputed} (the line only touches those four fields). Also data['sitesEntry'] (the page's post-reload S.byId[site]) matches score/drawings.
  5. ITEM (tree data/review/<itemFile name>): resolved == {doc: doc_id, at: doc['at']}; for B only: A's item file bytes in the tree == prev_item_bytes (B's export must not rewrite A's resolved item - write-once condition in review.export).
  6. REVIEW EXPORT (tree web/data/review.json): after A: open-site list == before-list minus A (count -1); after B: minus A and B (count -2 vs the fixture's before-state); other sites' entries byte-identical (compare the items entries for sites not in {A,B} by name+lead+candidates).
  7. SERVER LOG (served['out']): exactly one line matching r"one-site line for (\S+):" per run and it names this site with "finished (exit 0)" (note the two-space indent in the raw line); no line contains 'attempted a network connection'; no 'one-site line' line contains 'failed'; if p's pre-run uncovered list is [] (both picks): assert the no-batch line f"fit  {n_rows} candidate picture(s): 1 fitted (doc), {n_rows-1} in the review item -> no batch run needed" where n_rows = len(_rows_naming(checkout, site)) - (1 if A already has its doc in the tree when B runs: for B, docs include A's doc but A's plan does not name B's site, so n_rows = 3 for B, 1 for A) - i.e. computed from the tree's pre-run plans/item state.
  8. REVERT PROOF: _write_surface(served) == surface (the checkout never moved: the tree is discarded when the session ends - the temp dir rmtree is the discard).
  9. SCREENSHOTS: for n in ('1-card','2-placed','3-gestured','4-saved','5-reload'): shutil.copy2(outdir/f"{n}.png", ROOT/'docs'/'site_flow'/f"307d_{tag}_{n}.png"); store A's item bytes into p['itemAfterA_bytes'] after A's run (for step 5 of B).

_write_surface(picks): {str(p): _h(p) for p in: every data/db/platefits/*.json + every data/review/*.json in the CHECKOUT + web/data/sites.json + web/data/review.json + web/data/fit_queue.json + EVERY file under web/data/sites/<A>/ and web/data/sites/<B>/ in the CHECKOUT (symlinks into the shared store - hashing through them proves the store never moved)} - 307bb's _write_surface extended with fit_queue.json and the two site dirs.

OWNER_PROBE (node, new file; copy 307bb's PLACE_PROBE shape and its HELPERS/_fkvAnchorAt/_fkvFitChecks/drag/wheel/shift+wheel blocks VERBATIM; args <base> <site> <plan> <tree> <outdir> <done_json> <item_file>): addInitScript seeds aw.fitQueue.done=doneJson -> goto base (NO hash: the home view boots renderList -> fqLoad, so the boot poll S.ready && S.sites.length && FQ.loaded && FQ.entries.length works) -> card1 = #fqcard: assert in-page it names the pick (e = FQ.entries.find(x=>x.site===site); text contains e.name && (e.best.row.title||e.best.row.id)) -> shot 1-card.png -> #fqplace -> poll P.placed===true && P.img (60 s) -> sleep 2500 (fitBounds 900 + settle) -> the 243 seed checks VERBATIM (anchor == propose's LAST pair to 1e-9 mpx/rot/centre; n===5 pairs+marks; fitPrev source; gestures [dragPan,scrollZoom,touchZoomRotate,doubleClickZoom,boxZoom] all disabled; dep layer 'dep-<site>' visibility 'none'; hint contains anchor.mpx.toFixed(2) + 'm per page pixel') -> shot 2-placed.png -> inject HELPERS -> drag (307bb verbatim: clear-point candidates [1075,1105,1040,1140,1000] at y 400, down/move +30/+20 in 2 steps/up, the 7 drag checks incl. pair5 at doc rounding, dmpx<1e-3 drot<0.01, maxResid<2, maxCorner<0.2 closure<0.2) -> wheelBase = simFit(P.pairs).mpx FIRST then mouse.wheel(0,-100) (mpx *= exp(0.15), centre/rot held) -> shift+wheel +100 (rot += 1.0, scale held 1e-3) -> shot 3-gestured.png -> record anchorBeforeSave = P.anchor, pairsBefore = P.pairs.map([u,v,lon,lat]), imgSize = [P.img.naturalWidth, P.img.naturalHeight] -> #fsave -> poll !P.active (120 s) -> **site-view effects** (one in-page async poll, 120 s, until ALL true): doc = JSON.parse(readFileSync(tree/data/db/platefits/<docId>.json)); deps = fetch data/sites/<site>/depictions.json?t= -> overlay = find fit.doc===docId; sites = fetch data/sites.json?t= -> entry; item = fetch data/review/<itemFile>?t=; rv = fetch data/review.json?t=; conditions: overlay exists && overlay.fit.at===doc.at && kind 'plan' && file/ink names match; map layer 'dep-<site>' visibility 'visible' && source url === 'data/sites/<site>/plan_<plan>_ink.webp' && S.depSel[site]===overlay.file; entry.drawings === S.byId[site].drawings (the page's own copy, updated by saveFit) and entry.score !== (page's S.byId[site].score before the save - capture it in the placed stage as beforeScore); marker el (markers.find(k=>k.id===site).el).className === 'marker ' + tierOf(entry); item.resolved === {doc: docId, at: doc.at}; rv.items.map(x=>x.site) does NOT contain site; FQ.done[site] is a string and !isNaN(Date.parse(FQ.done[site])) (NEVER compare it to doc.at - the wrapper's own clock) -> shot 4-saved.png (the site view: the new overlay on the map) -> click #back (the site view's '← All sites') -> poll #fqcard presence (20 s; on this page FQ was already loaded at boot so it appears at once) -> card2: next = FQ.entries.filter(e=>e && e.site && S.byId[e.site] && !(e.site in FQ.done) && !FQ.skipped.includes(e.site))[0] (the page's own fqPending rule, in-page); assert next.site === passed nextSite arg AND card text contains next.name AND does NOT contain the pick's e.name -> page.reload() (same context: aw.depSel + aw.fitQueue.done persist) -> boot poll ONLY S.ready && S.sites.length (fact 11: FQ is NOT loaded after a hash boot; 60 s) -> sleep 5000 (select's 4500 ms flyTo) -> shot 5-reload.png (site view) -> RELOAD checks (in-page): S.sel===site; S.ground==='imagery'; S.depMode==='ink'; S.depMode==='ink'... (plateMode==='ink' too); S.depSel[site]===overlay.file (fetch deps again to get the file); dep layer 'visible' with the ink url; markers.find(k=>k.id===site).el.className === 'marker ' + tierOf(S.byId[site]); S.byId[site].drawings === entry.drawings from the pre-reload fetch; S.byId[site].score === the pre-reload entry.score; FQ.done[site] still set -> #back -> poll #fqcard (NOW the fetch really happens: fqLoad is async after this reload; 20 s) -> card3: same fqPending rule -> next.name in text, pick's name not in text -> print [eval] {boot, card1, seed, anchorBeforeSave, pairsBefore, imgSize, doc, overlay, sitesEntry, item, reviewOpenSites, done, card2: {text, nextSite: next && next.site, nextName: next && next.name}, card3: {text, nextSite, nextName}, reload: {sel, ground, depMode, plateMode, depSel, depVis, depSrc, markerClass, score, drawings, doneSet}, beforeScore} -> print all console non-'[console' lines (pageerror/reqfail) -> check no pageerror, reqfails only '/tiles/','arcgisonline','MapServer/tile/' -> RESULT PASS/FAIL -> exit 0/1.

**Exact next step (one session):** (0) add `docs/site_flow/` to this task's `Touches:` line (step 0 of 243; not yet done); (1) write tests/test_owner_check.py per the spec above (the new file; suite baseline to beat: 155 passed / 1 skipped / 1 failed - the one red is 235's test_placement_gestures_and_save_in_the_browser, unrelated, must stay the ONLY red; .venv/bin/python -m pytest); (2) run `.venv/bin/python -m pytest tests/test_owner_check.py -q` (~5-10 min: two browser runs; the first line's heavy import ~23 s, second cached; the fixture serves BOTH picks, so the second run is cheaper) - if a check fails: commit the test AS-IS and name the failing check + the probe's [eval] dump in DECISIONS (307bb's rule), fix next session; (3) run the full suite once (confirm only 235's red remains; tests/golden/hand_fit_docs.sha256 + test_fit_provenance stay green - they run on the checkout, which the revert proof shows untouched); (4) docs/site_flow.md section AFTER the 308 section: what was checked, the two derived picks + the picker rules, the line's four effects (overlay on the map, square recoloured t1->t2 with the score 1.1->~1.45, item resolved write-once, card moved on to the next queue entry), the reload unchanged, the revert proof, the five screenshots per site - and state PLAINLY that both sites sit on LiDAR relief (lidar None) because no aerial-photograph-only (lidar False) site is line-eligible today: every aerial-only queue site is a commons-row candidate with no local book page (243's first-session finding, re-verified 244/245); tick the boxes; DECISIONS entry; commit.

**Picks (unchanged from 242/244; re-scanned this session, queue at the same `at`, 241 entries):** A (bar) = queue [38] oswestry-castle-q20713795 / row earthworkenglan01allcgoog_n0119_1 (bar mpx 0.1646 rot 0, book 'Allcroft 1908', label 'Fig. 17', title 'Camp, Old Oswestry, Salop', map_box [0.198,0.168,0.875,0.778], size [3367,5050], url/ref null); item data/review/oswestry-castle-q20713795.earthworkenglan01allcgoog_n0119_1.json (ONE candidate n0119_1, 3 pairs, unresolved). B (picture_size) = queue [45] devil-s-dyke-q3307343 / row earthworkenglan01allcgoog_n0662_1 (coarse mpx 0.7201 rot 0, label '', title 'SWEALD', map_box [0.2,0.15,0.85,0.7], same book/size); item data/review/devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0599_1.json (3 candidates: n0599 lead 3 pairs, n0686 4 pairs 'median residual 50.8m > 45', n0662 4 pairs 'line check: fabricated anchor pattern...'; UNRESOLVED). Both: lidar None, lidar_credit 'Environment Agency, Crown copyright, Open Government Licence v3.0'; sites.json {drawings:0, score:1.1 (=> tier t1, see correction), oldest:1842, overlays:1}; depictions = [six-inch-1st.webp map 1842, os1inch.webp map 1900 (excluded: 2026-1900=126 < 150)] -> page auto-dep six-inch-1st.webp, no drawing dep; both site dirs symlinks into the shared store; both pages natural (3367,5050) = row.size -> frame scale 1. B's line: 3 rows naming the site, all three in the item -> uncovered [] -> no batch run, but matchfit.reachable() IS called (any row not in docs) - under the GUARD its AssertionError is swallowed -> False, silent (243 fact 3, re-verified against matchfit.py L103-108). A's line: its 1 row in docs -> reachable never called.

**Do not touch:** fit/surveyfit.py or task 304 (agent c); tests/test_fit_queue.py (235's file); tests/conftest.py (ask for shared fixtures in DECISIONS instead); any data file in the checkout (the test writes only into its private tree); the other agents' in-flight files (203b/207a/302a/306 are on agent c's branch). Suite baseline (driver notes, re-run before claiming): 155 passed / 1 skipped / 1 failed (235's red).

--- iteration 243 (previous session, kept for reference; everything below it superseded by the above where they differ) ---

(2026-10-13, iteration 243, agent a - FOURTH session; re-ran the pick scan (picks unchanged, queue at the same `at` 2026-10-13T14:34:09.559141+00:00, 241 entries; eligible set identical to 242's list) and re-verified EVERY remaining page/line fact against the current code (all confirmed true this session, listed below). The full 307bb template (tests/test_fit_queue.py: GUARD L98-115, PLACE_PROBE L1289-1650, place_served L1673-1720, _line_eligible L758, _write_surface L1723, CHROME/NODE_MODULES L1024-1025, _headless_or_skip L1130) was read whole. **NO code written, NO tests run. NEXT SESSION: write tests/test_owner_check.py from the spec below, run it, then the docs section.**

**Picks (unchanged from 242, re-verified):** A (bar) = queue [38] oswestry-castle-q20713795 / row earthworkenglan01allcgoog_n0119_1 (bar mpx 0.1646 rot 0, book 'Allcroft 1908', label 'Fig. 17', title 'Camp, Old Oswestry, Salop', map_box [0.198,0.168,0.875,0.778], size [3367,5050], url/ref null); item data/review/oswestry-castle-q20713795.earthworkenglan01allcgoog_n0119_1.json (ONE candidate n0119_1, 3 pairs, unresolved). B (picture_size) = queue [45] devil-s-dyke-q3307343 / row earthworkenglan01allcgoog_n0662_1 (coarse mpx 0.7201 rot 0, label '', title 'SWEALD', map_box [0.2,0.15,0.85,0.7], same book/size); item data/review/devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0599_1.json (3 candidates: n0599 lead 3 pairs, n0686 4 pairs 'median residual 50.8m > 45', n0662 4 pairs 'line check: fabricated anchor pattern...'; UNRESOLVED). Both: lidar None, lidar_credit 'Environment Agency, Crown copyright, Open Government Licence v3.0' (field name IS `lidar_credit` in sites.json), sites.json {drawings:0, score:1.1, oldest:1842, overlays:1}; depictions = [six-inch-1st.webp map 1842 label 'Ordnance Survey six-inch map, England and Wales, 1st edition', os1inch.webp map 1900 (excluded: 2026-1900=126 < 150)] → auto dep six-inch-1st.webp, no drawing dep; both site dirs are symlinks into the shared store (/home/agent/projects/ancient-works); both pages natural (3367,5050) = row.size → frame scale 1; review.json 457 open incl. both; uncovered=0 for both. **B's line details (measured this session):** plans.json rows naming devil-s-dyke = 3 (n0599_1, n0662_1, n0686_1); after the save docs={n0662_1} so `any(row not in docs)` is TRUE → matchfit.reachable() IS called (urlopen http://127.0.0.1:8091/health; the GUARD's AssertionError is swallowed by its try/except → False, offline-safe, no log line); uncovered=[] (all 3 rows are item candidates) → no batch run, log 'fit 3 candidate picture(s): 1 fitted (doc), 2 in the review item -> no batch run needed'; the hand doc n0662_1 is built with NO fabrication check (who_placed=='hand' despite the candidate's old pattern why); resolution = first item candidate WITH a doc = n0662_1 (n0599/n0686 have none) → item gets resolved {doc: devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0662_1, at: doc.at}; A's run: all rows in docs → matchfit not called at all, log 'fit 1 candidate picture(s): 1 fitted (doc), 0 in the review item -> ...'.

**Picker (derived, never pin ids; implement in the test):** eligible = propose present AND _line_eligible(e, item) is a list (NOT None: book row ia/file, page file in CHECKOUT data/raw/books/<ia>/full/, unresolved item carrying that row as a candidate with >=3 pairs, no platefits docs for the site) AND page-showable auto dep (mirror loadDeps: keep kind not in (map,aerial,topo) OR (year and year <= now-150); auto = first drawing-kind (plan/drawing/view) else LAST map-kind; must exist) AND no pre-existing drawing-kind dep AND an entry follows it in file order (the card must be able to move on). A = first eligible with scale_source 'bar'; B = first eligible with 'picture_size' whose lidar_credit differs from A's, ELSE first eligible 'picture_size' (today all EA → B is the fallback pick [45]). Fixture fails with a clear message if A or B cannot be derived. Per-site done seed (probe arg): {entries[i].site: AT for i < that site's index} read from the TREE's fit_queue.json (AT = "2026-10-12T00:00:00.000Z", 307bb's convention).

**Fixture `owner_served` (module scope):** 307bb's place_served recipe with BOTH site dirs in copy_web(tree, real={A,B}) and BOTH book pages materialised into the tree's own data/raw; one GUARD'd server (ephemeral port, reader thread, 90 s poll); yield {base, tree, proc, out, picks: {A/B: {entry, row, plan, site, item, itemFile, depFile, sitesBefore, done, scale_source}}}; teardown terminate/kill. B's run sees A's tree state by design (pytest file order A then B; both dirs are real copies).

**THE NEW FACTS THIS SESSION FOUND (beyond the 242 hand-over - the probe MUST follow these):**
1. **The card is NOT in the DOM on the site view** (#body is fully replaced by renderSite; fqPatch removes the card when the home stats line is absent). After save the page sits on the SITE view; the "queue moves on" check therefore requires: on the site view read effects (a)-(d) + screenshot 4-saved.png, THEN click the site view's own #back button (text '← All sites') → home → #fqcard appears → it must name the NEXT pending entry (page's own fqPending rule: first entry with S.byId[site] && !(site in FQ.done) && !skipped) and NOT name the pick. After page.reload() (hash '#<site>' → select() → site view again) do the same: verify site-view state, screenshot 5-reload.png, then #back → home → card again.
2. **_fqSaveFit writes FQ.done[siteId] = new Date().toISOString()** (the WRAPPER's own clock - fitqueue.js L125 - NOT the doc's at) then fqPatch. Poll that FQ.done[site] is a parseable ISO string; never assert equality with doc.at.
3. **Page saveFit success path (index.html L1151-1181):** when the page's own poll finds the overlay (fit.at === the page's at) it sets S.dep[s.id] = fresh depictions, S.depSel[s.id] = overlay.file, **lsSet('aw.depSel', S.depSel)** (persisted → survives reload; select() only default-picks when `!(s.id in S.depSel)`), fetches data/sites.json and copies drawings/score/oldest/overlays into S.byId[s.id], updates the marker el.className = 'marker ' + tierOf(s), then endFit()+applyDep. So after the page's save the overlay is ALREADY the visible dep (S.depMode==='ink' → ink url).
4. **select() (L823-845) sets S.ground='imagery', S.plateMode='ink', S.depMode='ink' UNCONDITIONALLY** (no lsSet for ground; fqPlace's setGround('relief') persisted 'aw.ground'='relief' to localStorage during the run, but select overwrites the runtime value on every open). Reload therefore shows ground 'imagery', depMode 'ink', plateMode 'ink' - assert exactly that (the page contract, not 'relief').
5. Boot: start() (L1703-1711) - `S.byId[id] ? select(id) : renderList()` on the hash; so after reload S.sel===site and the site view renders (flyTo 4.5 s - sleep ~5 s before the reload screenshot).
6. **Marker:** page global `markers` array ({id, el}); class = 'marker ' + tierOf(s); TIERS [[2.5,'t4'],[1.6,'t3'],[1.2,'t2'],[0.01,'t1']] else 'plain' (index.html L475-476). Both picks: 1.1 → t2 BEFORE, ~1.45 → t2 AFTER (tier unchanged, score/drawings move - the check is className === 'marker ' + tierOf(the fresh S.byId score)).
7. **Expected post-run scores (recompute in the test with the build_site formula ported to stdlib, year_now = current year):** overlays = [(1908, rms(resid_m of the 5 page pairs), True), (1842, 8, False)] (six-inch via SERIES_ERR_M {'Ordnance Survey six-inch':8}; os1inch 1900 excluded <150 yr); val = (year_now-y)/100/(1+(e/100)^2)*(1 if drawing else 0.6) desc; score = round(best + 0.25*sum(rest), 2) ≈ 1.45 for both (resid_m all < 1). drawings: 0→1. Assert the tree's sites.json entry equals the recomputation AND the page's marker class matches tierOf of the page's own S.byId score.
8. **Overlay entry (plan_fit.build L310-375):** kind 'plan', file plan_<plan>.webp, ink plan_<plan>_ink.webp, year = _year4(book+' '+label) = 1908 (regex (?<!\d)(1[2-9]\d\d)(?!\d)), label 'Allcroft 1908: <title or label>', source ends with 'Placed by hand on 5 matching points; one rotation and scale fits them within <m> m.' (m = ceil(max resid)); fit = {pairs:5, model:'similarity', resid_m: [round(1dp)]×5, m_per_px: round(|a|*k/fs→ /f, 4) with f = min(1, MAX_PX/max crop px) (MAX_PX=2400, read from the TREE's pipeline/plan_fit.py by regex), rot_deg: round(deg,2), at: doc.at, doc: '<site>.<plan>'}; depictions re-sorted by year; then build_site.set_drawings. The webps exist in the tree; assert realpath under the tree and not sd.is_symlink().
9. **Review flow (fit/review.export L189-243):** open = resolved not recorded AND no doc for any candidate; it writes resolved {doc, at: doc.at} into the item file WRITE-ONCE (only for site_id-scoped runs) and publishes web/data/review.json over the WHOLE queue (457 → 456 after A → 455 after B; A absent after A, B absent after B; the other 455 untouched). B's export must NOT rewrite A's item file (already resolved) → assert A's item bytes identical after A's run and after B's run.
10. **Line log (server out, two-space indent):** '  one-site line for <site>: finished (exit 0)'; assert no 'failed', no 'attempted a network connection', and no other site's line ran.

**Probe (node, copy of 307bb's PLACE_PROBE shape; new file, do NOT import from test_fit_queue.py - 235 owns it; COPY GUARD/CHROME/NODE_MODULES/_headless_or_skip/_line_eligible/_item_of/_rows_naming/_review_items into the new file):** args <base> <site> <plan> <tree> <outdir> <done_json> <item_file>. addInitScript seeds aw.fitQueue.done=doneJson → goto → boot poll (S.ready && S.sites.length && FQ.loaded && FQ.entries.length) → card1 read (must name the pick: entry = FQ.entries.find(x=>x.site===site); assert card text contains e.name AND (e.best.row.title || e.best.row.id)) → shot 1-card.png → #fqplace → poll P.placed===true && P.img → sleep 2500 → VERBATIM 307bb seed checks (anchor vs propose last pair 1e-9 mpx/rot/centre; n===5 pairs+marks; fitPrev source; 5 gestures all disabled; dep layer 'dep-<site>' visibility 'none'; hint contains anchor.mpx.toFixed(2) + 'm per page pixel') → shot 2-placed.png → inject 307bb's HELPERS (_fkvAnchorAt/_fkvFitChecks verbatim) → 307bb drag (clear canvas point, down/move(+30,+20, 2 steps)/up; all 7 drag checks) → wheel -100 (wheelBase = simFit(P.pairs).mpx first; mpx *= exp(0.15); centre/rot held) → shift+wheel +100 (rot += 1.0; scale held 1e-3) → shot 3-gestured.png → record anchorBeforeSave = P.anchor, pairsBefore (5), imgSize [naturalW,naturalH] → #fsave → poll !P.active 120 s → **site-view effects (in-page, poll all until true, 120 s):** (a) fetch data/sites/<site>/depictions.json?t= → overlay = entry with fit.doc===docId: assert fit.at=== (fresh doc read from the tree via readFileSync tree/data/db/platefits/<docId>.json).at, kind 'plan', file/ink names; page's dep layer 'dep-<site>' visibility 'visible' with source url 'data/sites/<site>/plan_<plan>_ink.webp' and S.depSel[site]===overlay.file; (b) fetch data/sites.json?t= → entry.drawings===before+1 && entry.score!==before; marker class === 'marker ' + tierOf(entry); (c) fetch data/review/<item_file>?t= → item.resolved==={doc:docId, at:doc.at}; fetch data/review.json?t= → site NOT in items[].site; (d) FQ.done[site] is a parseable ISO string (NOT compared to doc.at) → shot 4-saved.png (site view: the new overlay on the map) → **click #back (the '← All sites' site-view button) → home → card2 = #fqcard text: contains the next pending entry's name (page's own fqPending rule computed in-page from FQ.entries/FQ.done/FQ.skipped) and does NOT contain the pick's name** → **page.reload() (same context: aw.depSel, aw.fitQueue.done, aw.ground persist) → boot poll → RELOAD checks:** S.sel===site; S.ground==='imagery'; S.depMode==='ink'; S.plateMode==='ink'; S.depSel[site]===overlay.file; dep layer 'visible' with the ink url; marker class === 'marker ' + tierOf(S.byId[site]) (fresh sites.json); S.byId[site].drawings===before+1; S.byId[site].score===afterScore (from the pre-reload fetch); FQ.done[site] still set → shot 5-reload.png (site view) → #back → home → card3 must still name the next pending, not the pick → print [eval] {boot, card1, seed, anchorBeforeSave, pairsBefore, imgSize, doc (fs read), overlay, sitesBefore, sitesEntry, item, reviewOpenSites, done, card2, card3, reload:{sel,ground,depMode,plateMode,depSel,depVis,depSrc,markerClass,score,drawings,card}, markerClass} → console non-'[console' lines → RESULT PASS/FAIL + exit 0/1. Allowed reqfails ONLY '/tiles/', 'arcgisonline', 'MapServer/tile/'; no pageerror.

**Python-side checks per site (read from the TREE; the probe's [eval] for page-side values):** 1) doc at tree/data/db/platefits/<site>.<plan>.json: by==='hand', site/plan/ia/file, model 'similarity', src 'book', url null, ref null, size===imgSize===row.size, crop===[round(mb[0]*W),round(mb[1]*H),round(mb[2]*W),round(mb[3]*H)], pairs===pairsBefore EXACTLY, at ISO 2026. 2) stdlib port of the page's simFit (index.html L1004-1021: W=[u,-v], Z=merc with R=6378137; a=(nr/d,ni/d), nr=Σ(zr*wr+zi*wi), ni=Σ(zi*wr-zr*wi), d=Σ(wr²+wi²) over centred pairs; b=[zm0-(a0*wm0-a1*wm1), zm1-(a0*wm1+a1*wm0)]; at(u,v)=[a0*u+a1*v+b0, a1*u-a0*v+b1]; k=cos(lat0 rad); mpx=hypot(a)*k; rot=deg(atan2(a1,a0)); resid per pair hypot(at-Z)*k): mpx within 1e-3 of anchorBeforeSave.mpx, rot within 0.01 deg, max resid < 2. 3) overlay per fact 8 (incl. webp existence, realpath under the tree, sd not a symlink, source ends with the hand clause, year 1908). 4) sites.json entry === recomputed (fact 7) + oldest 1842 + overlays 2. 5) item resolved (fact 9) + (B only) A's item bytes unchanged after B's run. 6) review.json open-list/count transitions (457→456→455 style: relative to the tree's before-state, A absent after A, B absent after B). 7) server out (fact 10). 8) REVERT PROOF: _write_surface(picks) before and after each run EQUAL - sha/bytes of: every data/db/platefits/*.json + data/review/*.json + web/data/sites.json + web/data/review.json + web/data/fit_queue.json + EVERY file under web/data/sites/<A>/ and web/data/sites/<B>/ in the CHECKOUT (symlinks into the shared store - hashing through them proves the store never moved). 9) copy the probe's 5 PNGs from the tmp outdir into docs/site_flow/ as 307d_A_<name>.png / 307d_B_<name>.png (1-card, 2-placed, 3-gestured, 4-saved, 5-reload).

**Exact next step (one session):** (0) add `docs/site_flow/` to this task's `Touches:` line (the screenshots belong to docs/site_flow/; the line currently only names docs/site_flow.md); (1) write tests/test_owner_check.py per the spec above (new file; the suite baseline to beat: 155 passed / 1 skipped / 1 failed - the one red is 235's test_placement_gestures_and_save_in_the_browser, unrelated, must stay the ONLY red); (2) run `.venv/bin/python -m pytest tests/test_owner_check.py -q` (~5-10 min: two browser runs; first line ~23 s incl. heavy imports, second cached); if a check fails: commit the test AS-IS and name the failing check + the probe's [eval] dump in DECISIONS (307bb's rule), fix next session; (3) run the full suite once (confirm only 235's red remains; the golden hand_fit_docs.sha256 + test_fit_provenance stay green - they run on the checkout, which the revert proof shows untouched); (4) docs/site_flow.md section AFTER the 308 section: what was checked, the two derived picks + the picker rules, the line's four effects, the reload, the revert proof, the screenshots - and state PLAINLY that both sites sit on LiDAR relief (lidar None) because no aerial-photograph-only (lidar False) site is line-eligible today: every aerial-only queue site is a commons-row candidate with no local book page; tick the boxes; DECISIONS entry; commit.

**Do not touch:** fit/surveyfit.py or task 304 (agent c); tests/test_fit_queue.py (235's file); tests/conftest.py (ask for shared fixtures in DECISIONS instead); any data file in the checkout (the test writes only into its private tree); the other agents' in-flight files (203b/207a/302a/306 are on agent c's branch). investigation completed: picks re-verified
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
