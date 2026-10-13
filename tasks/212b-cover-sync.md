Status: in-progress
# 212b: The page-facing sync - every fit is an overlay, review.json is the open list
Depends on: 212a
Touches: fit/cover.py, web/data/sites.json, web/data/sites/, web/data/review.json, data/db/platefits (the sync stamps by:agent into an unmarked auto doc and deletes a pattern doc), data/review/ (the sync's per-doc failure containment upserts item entries; the trailing export records write-once resolutions), tests/test_cover.py, tests/test_fit_provenance.py (212b's sync deleted the yearless-title test's pinned durocortorum doc; the pin moves to the surviving watson-brake doc)

## Goal
The one page-facing sync from 212: every fit document becomes its site's overlay
(web/data/sites/<id>/depictions.json) and drawings count in web/data/sites.json through
the existing plan_fit machinery (plan_fit.main(), the way serve.py's after_write does it);
web/data/review.json is regenerated (python3 fit/review.py export).

## Acceptance criteria
- [x] `python3 fit/cover.py sync` runs plan_fit for every site with a fit doc and the review export.
- [x] The hand fits' overlays are unchanged (000's golden test still passes).
- [ ] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item; the page's review count
      matches review.json (checked through the served page).

## Hand-over

(2026-10-13, iteration 230, agent a - **INVESTIGATION session, hit the context limit before
writing code. Every API the test drives was re-read and verified against the current tree
(clean at 724559f; tests/test_cover.py is still 212a's 770-line version). NOTHING changed on
disk. NEXT: extend tests/test_cover.py per the verified design below (ONE step), run it
alone, fix what it exposes, then the full suite. The iter-229 hand-over (still the source of
the measured world + design decisions 1-8) is in git: `git show
8c65465:tasks/212b-cover-sync.md`; the parent's 953d9ab settled design: `git show
953d9ab:tasks/212-cover-final.md`.)**

**VERIFIED THIS SESSION (the deltas vs the iter-229 note - read these first):**

1. **THE MIRROR MUST CALL PROPSE WITHOUT A ROOT (corrects the iter-229 mirror note).**
   batch_us.run_sites calls `propose.propose_for(sid, row["id"])` with NO root arg
   (fit/propose.py:393, default ROOT = this checkout). The hit site's two STAGED rows are not
   in the checkout's plans.json -> `_plans_row` raises **ValueError** (not KeyError - it says
   "no plans row for %r") -> run_sites' `except (ValueError, KeyError)` -> prop=None ->
   batch_us._entry writes `"coarse": True` and NO proposal extras. So the hit's two item
   candidates are COARSE entries. The iter-229 note said mirror with `root=tree` - that would
   compute a proposal the product never computes -> mismatch. Mirror the product exactly:
   same call, same try/except. For every EXISTING row (the 111 batch-run sites' rows) the
   checkout and the tree agree (data/books, data/catalog, sites.json hard-linked; baseline
   plans rows identical; propose's _CACHE keyed (root,kind) makes repeat calls stable) -> the
   mirror is deterministic and equals the product. propose is stdlib-only, ~0.2 s/call.
2. **aw.save_json is tmp+os.replace (pipeline/aw.py:199)** -> build_site.set_drawings
   (flock + save_json) replaces the sites.json inode -> the hard-linked tree sites.json is
   SAFE under the loop's 452 set_drawings calls; the checkout file is never written.
   marks() (build_site.py:241) updates drawings/score/oldest/overlays from the site's own
   depictions.json only.
3. **POST-LIVE-RUN: there are NO stale plan/view overlays left in the world.** The live sync
   (committed 6ce742f) pruned them: shotwick-castle-q7502621's dep is map-only (1 entry,
   six-inch-1st 1842), bethlehem-q2523914's dep map-only (tmk1850 1850). So the test's sync
   prune drops NOTHING: assert the sync stdout has no "pruned" line, both dep files
   byte-identical before/after the sync, both sites' drawings stay 0, and both items stay
   OPEN and on the served open list (box-3 coverage for them, the CORRECTION-4 contract,
   now via the "no stale overlay" shape).
4. **server/serve.py**: `--port 0` binds 127.0.0.1 and prints "Ancient Works on
   http://127.0.0.1:PORT/"; ROOT = the server dir's parent (the tree when we copy
   server/ in); the fit worker's after_write fires ONLY on platefits PUT/DELETE - GET-only
   traffic never triggers it (no site_done/plan_fit from the server side); relief_tiles
   imports only under .venv python (numpy/scipy) - start the server with
   `[venv_python, tree/server/serve.py, --port, 0]` cwd=tree and pull its stdout in a
   reader thread (test_fit_queue's pattern - a blocking readline on a buffered reader misses
   lines; give 90 s). The tree needs its own server/ (shutil.copytree checkout server/ ->
   tree/server/; web/ was already linked so web/ + server/ are both under the tree root).
5. **matchfit.run (fit/matchfit.py:269)** is what the real matcher does per written doc:
   `batch_us.write_doc(root, sid, row, pairs, score)` then `doc.update({"fitter": "matcher",
   "matcher": {model, inliers, matches, ground, window, rot_deg, spread}})` then
   `batch_us._save_json(path, doc)`; returns the list of paths. The fake copies this shape
   (the matcher sub-dict can carry small fixed values - nothing downstream reads it;
   site_done only keys off `fitter == "matcher"`).
6. **site_done._sync_doc (tools/site_done.py:197)**: who None -> refused (upsert
   _provenance_entry, doc kept); unmarked auto -> _stamp_agent (by:agent, key last); agent
   with fitter matcher -> matchfit.spread(SAVED 1dp pairs) vs SPREAD_MIN_RATIO 0.1 /
   SPREAD_MIN_SD_PX 20.0 -> pattern string "matcher points nearly on a line (spread
   {ratio:.2f}, {sd:.0f} px): the scale is not pinned" -> _pattern_entry (why = "line check: "
   + pattern + (", score sentence" = "; the gate's %s m measures internal consistency of the
   anchors, not their truth" % score when score not None)) upserted + doc UNLINKED + return
   ("sent", pattern); else is_done? skipped : plan_fit.build. build (plan_fit.py:310) needs
   the site dir, pairs >= 2 (similarity), load_picture (commons: data/raw/commons/big/
   <plan>.jpg cache, os.path.exists first -> NO network when the stand-in is present),
   writes depictions.json entry (fit.at = doc.at, fit.doc = "<sid>.<plan>") + 2 webps, then
   set_drawings. is_done compares fit.at == doc.at and fit.doc == "<sid>.<plan>".
7. **review.py**: upsert_item merges by plan (same-plan REPLACE in place, new append),
   no_picture dict always set, entries non-empty clears no_picture, resolved write-once,
   file lead = candidates[0].plan (a changed lead MOVES the file, old unlinked).
   resolved_doc: recorded resolution counts only while its doc file exists; else first
   candidate with a doc. export(root, site_id=None) writes web/data/review.json {"at",
   "items"} over the WHOLE queue every call, records resolution write-once (only into
   site_id's item file when scoped), items = {site, name, lead, candidates (verbatim),
   no_picture_found}, sorted by name.lower(). _find_item scans sorted data/review/*.json
   for item["site"] == sid (377-378 files).
8. **cover.loop (fit/cover.py:531)**: for each sid in sorted(_no_fit_sites(root)) at phase
   start (452): `site_done.main([sid, "--root", root])` IN-PROCESS (stdout captured,
   SystemExit/Exception caught into rc) - no subprocess, so the fakes monkeypatched on the
   shared modules apply. cover.sync (fit/cover.py:633): one-shot `for name, doc in
   _all_docs(root)` (sorted by id), _sync_doc per doc, bare-exception containment ->
   ("failed", ...) + _fail_entry upsert, then plan_fit.prune(root) (full), then
   review.export(root) (full). PHASES for the test = fetch, search, stage, LOOP, nopicture,
   SYNC (212a runs fetch/search/stage/nopicture today; the separate export phase is a
   duplicate of sync's trailing export - skip it; report stays 212c's).

**THE MEASURED WORLD (iter-229, re-verify at setup - the test computes it live; the pins
below fail loudly if a merge moved it):** built 499; docs 57 (21 by:hand = ALL the golden
set, ALL is_done; 36 by:agent = ALL (by:agent, fitter:matcher, auto:True), ALL pass the
line check, ALL is_done -> the sync of the pre-existing 57 = 57 skips, 0 network); nofit
452 = search set 234 (ALL with item files) + with-row 218 = 105 allcovered + 10 partial +
103 no-item; item files 377 (one per site); open 365 (12 truly resolved = recorded AND doc
exists; aesica + alligator carry STALE recorded resolutions -> still open); plans rows
1510; web/data/review.json at 2026-10-13T11:26:15 with 365; store big cache
(data/raw/commons/big) 75 files (includes aesica's c_e28ed261168b49c9.jpg - hard-linked
into the tree, no seed needed).

**CHOOSE (first 4 with-row nofit, sorted - pin these exactly in setup, fail loudly if
different):** [0] aardenburg-q955 (NO item; 1 row c_d0a020dec428fa00, commons, local copy
in store, BIG stand-in MISSING -> seed it; row size [500,500], map_box None -> crop
[0,0,500,500]); [1] aesica-q4688554 (item aesica-q4688554.c_e28ed261168b49c9.json, 1
candidate = its only row, STALE recorded resolution {doc: aesica-q4688554.c_e28ed261168b49c9,
at: 2026-10-12T03:13:35.590448+00:00} -> D2 holds; row c_e28ed261168b49c9 size [1280,947]);
[2] aire-sur-la-lys-q259903 (NO item; 1 row c_d1ca997e67377769, local present, BIG MISSING
-> seed; size [1280,986]); [3] alauna-q4708853 (item ...earthworkenglan01allcgoog_n0438_1.json,
5 candidates; first row = BOOK earthworkenglan01allcgoog_n0438_1, local in store; size
[3367,5050], map_box [0.12,0.25,0.83,0.66] -> crop px [404,1262,2795,3333]). Every CHOOSE
site has 4 [lon,lat] "corners" in its sites.json entry (verified for all four this
session). **HIT = aalsum-q3902030** (first qid search-set site; item aalsum-q3902030.json,
candidates [], no_picture re-stamped by the live 212a run). **FAIL site = craig-phadrig**
(first no-qid search-set site with a files.jsonl title). **spot_n (no-qid literal) =
aggersborg** (the first 8 no-qid search-set sites have 0 files titles - aggersborg,
antequera-menga-dolmen, apuole-hillfort, balfarg-henge, bar-hill-fort, biggs-site,
borgring, burnswark-hill). Make the spot picks state-aware (iter-229 note): prefer a
non-failed site for the clean string; if none, pin the fail site's string WITH the
"FAILED routes: title search: 429 Too Many Requests (the recorded failure)" clause.

**RECIPES (verified arithmetic - compute at setup from the live rows, assert the checks
hold before writing any doc):** [0..2] = test_batch_eu._corner_pairs COPIED into
test_cover (do not import across tasks): the 5%-frame page corners ((0.05w,0.05h),(0.95w,
0.05h),(0.95w,0.95h),(0.05w,0.95h)) on the site's 4 corners -> a true similarity: spread
ratio 1.0, sd = sqrt(0.2*max(w^2,h^2)) (aardenburg 223.6, aesica 452.5, aire 572.4 - all
>= 20) and fabrication_pattern None (2 distinct u/v -> (a)/(b) can't fire; (c): no
coordinate within 0.5px of a 10-multiple for any of the three row sizes). [3] =
perfectly collinear: u 500/900/1300/1700, v 1300/1320/1340/1360 (slope 0.05, all inside
the crop), lon/lat interpolated along the site's corners (values irrelevant to the spread
check - it reads px only - but keep them plausible; _norm_pairs rounds to 7dp). After
_norm_pairs' 1dp rounding the (u,v) are unchanged -> spread = (0.0, 0.0) exactly (the
covariance det is 0 in exact float arithmetic) -> the pattern string is
"matcher points nearly on a line (spread 0.00, 0 px): the scale is not pinned" and the
entry's why = "line check: " + that + "; the gate's 25.0 m measures internal consistency
of the anchors, not their truth" (score 25.0, %s format).

**EXACT NEXT STEP - extend tests/test_cover.py (keep 212a's structure; one module-scoped
run fixture, several test functions over it):**
1. PHASES = ["fetch","search","stage","loop","nopicture","sync"]. build_tree: call with
   include_sites=True, then REALIZE web/data/sites (design 2): walk the tree dir; each
   entry that is a SYMLINK -> os.unlink + _link_dir(os.path.realpath(target), entry)
   (file hard links, .npy/.npz skipped; ~0.11 s, near-zero disk). Copy the checkout
   server/ into the tree (shutil.copytree). Seed the two BIG stand-ins AFTER build_tree,
   BEFORE the loop: tree/data/raw/commons/big/c_d0a020dec428fa00.jpg +
   c_d1ca997e67377769.jpg (solid-colour PIL JPEGs at the row's OWN size - [500,500] and
   [1280,986] - new inodes; plan_fit.load_picture's os.path.exists short-circuits the
   download). Everything else in build_tree stays (3 in-place real copies, data/raw
   hard-linked from the store, searches.json dropped, the 306a-era data/cover note).
2. Fakes: add matchfit.reachable -> lambda url=None: True and matchfit.run -> the fake
   (design: for each CHOOSE sid in site_ids: row = the FIRST candidate row with no doc
   (cands = batch_us.candidates(sid, batch_us._plans_rows(root)); CHOOSE sites have none);
   pairs = the recipe for that position; path = batch_us.write_doc(root, sid, row,
   pairs, 25.0); doc = json load; doc.update({"fitter":"matcher","matcher":{...small
   fixed dict...}}); batch_us._save_json(path, doc); append path. Non-CHOOSE sids -> [].
   Return the list. NO prints needed (the loop captures stdout; the 212a-style presence
   assertions don't depend on the fake's lines). Save/restore both in Fakes.install/
   restore. time.sleep no-op stays (cover.time IS the global time - poll on time.time()
   for the server wait).
3. Setup preconditions (fail loudly, before any phase): the 40 golden files
   (tests/golden/hand_fit_docs.sha256: 21 docs + 19 site.json) byte-match the tree; every
   pre-existing agent doc passes the line check (fitter matcher -> spread ok; else
   fabrication_pattern None) and ALL 57 are is_done in the tree (so the sync phase is
   build-free and network-free); CHOOSE sids == the 4 pinned; the CHOOSE recipe checks
   hold (above); bethlehem/shotwick deps are map-only (the new prune expectation); the
   store's big dir has aesica's stand-in.
4. Run the phases in-process as 212a does (stdout captured per phase; _no_network guard
   up for all of them - it stays up THROUGH the loop/sync: the only network the phases
   would use is what the fakes/stand-ins remove). After the phases: start the server
   (Popen, venv python, --port 0, cwd=tree, reader thread, parse "Ancient Works on
   (\S+)"); LIFT the socket guard only around the page GETs (urllib to our own loopback
   port - that IS the box's "port 0"); GET / (200 "Ancient Works"), /data/sites.json,
   /data/review.json; terminate+kill in teardown.
5. Assertions (all state-aware - recompute from the tree's final files):
   (i)-(iii) 212a's search/counts/stage assertions STAY (fetch/search/stage are unchanged;
   note the search-set size is 234 and the marked set 233 in the current world - the
   code already computes them, just re-run to confirm).
   (iv) THE ITEMS AFTER LOOP + NOPICURE (rewrite 212a's test_nopicture per the 212b hand-over design 1):
   marked = search set at search time MINUS the hit (= 233; the loop changes nothing in
   that set - the CHOOSE sites are all with-row, outside the search set): each marked
   item's no_picture_found = {searched: expected_searched(record), at: <new ISO>} with
   candidates/resolved equal to the pre-run item; SPOT checks as 212a but state-aware
   spot picks (aggersborg clean no-qid string; the qid spot a non-failed qid site).
   THE HIT: its item file MOVED aalsum-q3902030.json ->
   aalsum-q3902030.c_<sha16(fakes.t_plan)>.json (lead = candidates[0].plan = the first
   staged row in the tree's plans.json order - read it, don't pin the order); content =
   exactly the two "no model answer" COARSE entries (mirror batch_us._entry(tree, row, [],
   "no model answer", None, None) - prop None per verified delta 1), no_picture_found
   None, resolved None. ALL OTHER item files: byte-identical EXCEPT the 101 new no-item
   files, the 10 partial re-upserts, and alauna (see below).
   (v) LOOP BRANCH END STATES (compute the census from the pre-loop world in setup):
   - 105 allcovered (incl. aesica, alauna, bethlehem, shotwick): item byte-identical
     EXCEPT aesica (byte-identical TOO - the write-once guard: a recorded resolution is
     present, so the scoped export never writes) and alauna (the n0438_1 candidate
     REPLACED in place by the pattern entry of verified delta 6; the other 4 candidates
     and resolved None untouched); bethlehem/shotwick byte-identical (audit whys survive
     - the box-6 contract).
   - 10 partial: item = pre-run item with exactly the uncovered rows' entries upserted in
     place (mirror _entry per product call; covered entries restored = unchanged), stays
     open.
   - 103 no-item MINUS the 2 CHOOSE (aardenburg/aire): a FRESH item <site>.<lead>.json
     (lead = first plans-row id in the tree's plans order), every candidate "no model
     answer" (+propose extras or coarse), open.
   - aardenburg/aire: NO item file exists for the site; each has its matcher doc (by:agent,
     fitter:matcher, auto True, score 25.0, at ISO) in the tree's data/db/platefits;
     drawings 0 -> 1 in the tree's sites.json.
   - aesica: doc built (same), item byte-identical, drawings 0 -> 1, OFF the open list
     (the stale recorded resolution now points at an existing doc - D2).
   - the 234 no-row sites (search set): item byte-identical EXCEPT the 233 marked
     (the hit's handled above).
   (vi) SYNC: results dict = every one of the 60 docs (57 pre-existing + 3 CHOOSE) with
     action "skipped", detail None (recompute the doc list from the tree's platefits dir
     at sync time); stdout has the "sync: 60 document(s) over N site(s)" + "sync: 365 open
     of 378 item(s)" lines (n_total = 377 + 101; the hit's file moved, not added); NO
     "pruned" line (verified delta 3); bethlehem/shotwick dep files byte-identical; the
     40 golden files byte-identical tree-vs-checkout (21 docs + 19 site.json - the hand
     overlays are untouched); the 3 CHOOSE site dirs each gained exactly their 2 webps +
     the depictions entry (fit.doc = "<sid>.<plan>", fit.at = the doc's at, kind "plan").
   (vii) THE SERVED PAGE (box 3 - the acceptance criterion): from the GETted
   /data/sites.json: EVERY built site has drawings >= 1 OR its id is among the GETted
   /data/review.json items; golden sites (tests/golden/hand_fit_sites.txt) all
   drawings >= 1; aardenburg/aesica/aire 0 -> 1; every OTHER site's drawings == the
   committed (checkout) value (assert the field, not whole-entry bytes - design 7(a)).
   From the GETted /data/review.json: items == the open items RECOMPUTED from the tree's
   final item files with review.resolved_doc(item, tree), same fields (site, name, lead,
   candidates, no_picture_found) and name order; len(items) == that recomputed count ==
   the len(items) of the tree's ON-DISK web/data/review.json (365 = 365 - aesica + 101;
   recompute, don't pin the arithmetic); that len is what the page's #rvcount badge
   renders for a fresh client (web/review.js rvOpen: seen = {} -> all items) - the
   "checked through the served page" contract.
   (viii) CHECKOUT INTEGRITY: keep 212a's hashing (data/ minus the raw symlink, web/data
   top-level files, docs/ specs/ tests/) BEFORE and AFTER everything (server included);
   PLUS for web/data/sites: hash only the files under the 121 REAL per-site dirs (the
   symlinked entries are shared store views that concurrent agents' tests write; the run's
   own overlay writes land only in the realized copies - also assert the realized dirs
   are now real dirs, no symlinks left).
6. RUN: `.venv/bin/python -m pytest tests/test_cover.py -q` (never bare pytest - no
   numpy/PIL). Budget ~5-7 min (the loop = 452 in-process site_done calls, each with a
   scoped review export ~0.32 s + two _find_item scans over 377-378 files; build of the
   3 CHOOSE docs adds a few s; the 212a phases are as before). Then the FULL suite
   `.venv/bin/python -m pytest tests/ -q` - known non-212b red: test_fit_queue.py part-4
   gestures (307bb, pre-existing on this VM, proven mine-independent; belongs to the 307
   series, NOT to fix here).

**RISKS (check in this order if an assertion bites):** (a) the loop's per-site scoped
review.export rewrites the tree's web/data/review.json 452 times (atomic, fine) - the
sync's full export is the last writer, so the served file is the sync's; (b) set_drawings
flocks the tree's sites.json.lock - the lock file is created in the tree (a new file,
gitignored-shaped; it lands in web/data/ - make sure the checkout-integrity walk doesn't
trip on .lock files: the 212a walk only hashed existing files before/after, a new .lock
appearing in the CHECKOUT would be a red - it won't: the lock is created only in the
tree); (c) if a merge changed the world (CHOOSE rows/sizes/items), the setup preconditions
fail loudly - re-measure (the one-liners are in the iter-229 note) and update the pins;
(d) bibracte's 16 uncovered rows -> propose called 16x in the loop; runtime fine;
(e) propose's _CACHE: the mirror calls it after the product did with the same keys -
safe, but if you ever call propose for a (sid,row) the product didn't, it only adds to
the cache, never changes it.
(f) test_counts' search lines stay exact (234 searched, 0 recorded, hit line "4 gathered,
2 kept old, 2 new"); the loop phase's 452-site stdout is captured but only presence-checked
(a couple of "done" lines per site).

**Do NOT touch:** requirements.in/.txt (302a/304), tests/conftest.py, and any module the
test only calls (site_done, batch_us, matchfit, review, plan_fit, build_site, propose,
evidence, commons, export_plans, serve.py) - monkeypatch in the test or file a new task.
The 307bb red and agent c's in-flight 203b/302a/304/306 work are other tasks' business.

---
(superseded - iteration 229 hand-over, full text in git: `git show
8c65465:tasks/212b-cover-sync.md`; its iter-228 block is superseded by it via `git show
7f444c0:tasks/212b-cover-sync.md`, and the 212a-era iter-205 design text by `git show
953d9ab:tasks/212-cover-final.md`. The 05:58-era preflight numbers there are stale where
they conflict with the above.)
