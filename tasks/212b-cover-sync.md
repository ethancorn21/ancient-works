Status: in-progress
# 212b: The page-facing sync - every fit is an overlay, review.json is the open list
Depends on: 212a
Touches: fit/cover.py, web/data/sites.json, web/data/sites/, web/data/review.json, data/db/platefits (the sync stamps by:agent into an unmarked auto doc and deletes a pattern doc), data/review/ (the sync's per-doc failure containment upserts item entries; the trailing export records write-once resolutions), tests/test_cover.py, tests/test_fit_provenance.py (212b's sync deleted the yearless-title test's pinned durocortorum doc; the pin moves to the surviving watson-brake doc)

## Goal
The one page-facing sync from 212: every fit document becomes its site's overlay
(web/data/sites/<id>/depictions.json) and drawings count in web/data/sites.json through
the existing plan_fit machinery (plan_fit.main(), the way serve.py's after_write does);
web/data/review.json is regenerated (python3 fit/review.py export).

## Acceptance criteria
- [x] `python3 fit/cover.py sync` runs plan_fit for every site with a fit doc and the review export.
- [x] The hand fits' overlays are unchanged (000's golden test still passes).
- [ ] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item; the page's review count
      matches review.json (checked through the served page).

## Hand-over

(2026-10-13, iteration 229, agent a - **RE-MEASUREMENT DONE** (the box-3 precondition step); no
code written this session (the 212a test_cover was green in the last suite, 324 s run; nothing
has run since). **NEXT: write tests/test_cover.py per the design below + the parent's `git show
953d9ab:tasks/212-cover-final.md` (D1-D5 + the 7 numbered groups); 212b's scope = extend the
212a fixture with the loop + sync phases and the served-page box-3 check; report stays 212c's.**
Boxes 1+2 already committed (driver 6ce742f; my 7f444c0 for the re-pin). Tree at 36b583d clean.
This session's throwaway measurement scripts live in /tmp/aw212b-remeasure{,2,3,4}.py (not in
the repo - the numbers below are the record; re-run equivalent one-liners if a merge changed the
world before you pin).

**MEASURED WORLD (this tree; the test must stay STATE-AWARE - recompute at setup; the numbers
pin the current shape):** built 499; docs 57 (21 by:hand = ALL the golden set, ALL is_done;
36 by:agent = ALL (by:agent, fitter:matcher, auto:True), ALL pass the line check, ALL is_done
-> the test's sync of the pre-existing 57 = 57 skips, 0 builds/sends/fails, 0 network);
nofit 452; search set 234 (EVERY one has an item file); with-row nofit 218 = 105 all-rows-in-item
+ 10 partial + 103 no-item; item files 377 (one per site); open 365 (12 truly resolved =
recorded AND doc exists; aesica + alligator carry STALE recorded resolutions -> still open);
plans rows 1510; web/data/review.json at 2026-10-13T11:26:15 with 365; store big cache
(data/raw/commons/big) 75 files.

**CHOOSE (first 4 with-row nofit, sorted - UNCHANGED from the parent's measurement):**
[0] aardenburg-q955: NO item; 1 row c_d0a020dec428fa00 (commons, local copy in store, BIG
STAND-IN MISSING -> the test seeds it); row size [500,500], map_box None.
[1] aesica-q4688554: item aesica-q4688554.c_e28ed261168b49c9.json, 1 candidate (= its only row),
STALE recorded resolved {doc: aesica-q4688554.c_e28ed261168b49c9, at:
2026-10-12T03:13:35.590448+00:00} -> D2 HOLDS in this tree; row c_e28ed261168b49c9 size
[1280,947] map_box None; big stand-in ALREADY in the store (no seed needed).
[2] aire-sur-la-lys-q259903: NO item; 1 row c_d1ca997e67377769 (local present, BIG MISSING ->
seed); size [1280,986], map_box None.
[3] alauna-q4708853: item ...earthworkenglan01allcgoog_n0438_1.json, 5 candidates; first row =
BOOK Allcroft 1908 n0438.jpg (local in store); size [3367,5050], map_box [0.12,0.25,0.83,0.66]
-> crop px [404,1262,2795,3333]; near-collinear pairs must sit inside that crop (e.g. u
500/900/1300/1700, v 1300/1320/1340/1360, lon/lat interpolated along the site's corners; verify
ratio<0.1 and sd<20 at runtime before writing the doc).

**HIT = aalsum-q3902030** (first qid search-set site; item aalsum-q3902030.json, candidates [],
no_picture_found re-stamped by the live 212a run; no fake-title collision in files.jsonl).
**D1 failure site = craig-phadrig** (first no-qid search-set site with a files.jsonl title).
**spot_n (212a's literal no-qid spot check) = aggersborg** - NOT the fail site (the first 8
no-qid search-set sites - aggersborg, antequera-menga-dolmen, apuole-hillfort, balfarg-henge,
bar-hill-fort, biggs-site, borgring, burnswark-hill - all have 0 files titles) -> reconciles the
last green 212a run. Make the spot picks state-aware: prefer a NON-failed site for the clean
string; if none exists, pin the fail site's string WITH the "FAILED routes: title search: 429
Too Many Requests (the recorded failure)" clause.

**PARTIAL sites (10; the loop re-upserts exactly their uncovered rows in place - "no model
answer" + propose extras - covered entries restored, item stays OPEN):** aventicum
(c_0bdbfc863ce80b51, c_9ff8c52c90f4413a), bibracte-q650053 (16 rows), hopewell-mound-group
(c_613c225484b8fb63, c_88eb3b885c312dc2, c_8e1c72af5f821dae), los-millares
(c_1d89be22583fc871, c_93254f4d88a8afcb), maeshowe (c_9dd03a4a57bb7c05),
motte-castrale-quiquempois-q22961457 (c_e61f01cc894e88ea), numancia
(c_0fa271e2444f7bfc), stones-of-stenness (c_fd337c0a99e335bd),
the-roman-fort-vicus-bridge-abutments-an-q17650519 (c_4585b3fd9e23c6fa), trundle-q7847949
(c_7143c9206fa76ffd, c_d0416f3835753b0f). **NO-ITEM 103** (aardenburg/aire among them until the
matcher docs): a fresh all-rows "no model answer" item per site, OPEN (lead = first plans-row id;
file <site>.<lead>.json). Expected entries computed by MIRRORING batch_us._entry(tree, row, [],
"no model answer", None, propose.propose_for(sid, row_id, root=tree)) - propose is hermetic
(stdlib-only, deterministic, ~0.2 s/call, verified on 3 sample rows) so the mirror is safe.

**LOOP BRANCH CENSUS (the 452 nofit):** 234 no-rows (matcher not called - no rows; need_fit
False because every one has an item -> NO batch run, item byte-identical) + 105 allcovered
(matcher fake called for the doc-less-row sites -> returns []; no batch run; items unchanged)
+ 10 partial + 103 no-item (CHOOSE: aesica/alauna inside the 105, aardenburg/aire inside the
103 - the matcher fake writes their docs, so they get NO batch item).

**DESIGN DECISIONS (the test's shape - do not re-litigate):**
1. Phase order = the product's `all` order: fetch -> search -> stage -> **loop** -> nopicture
-> **sync** (the 212a fixture runs fetch/search/stage/nopicture today: move nopicture AFTER
loop; the separate export phase is a duplicate of sync's trailing review.export - skip it;
report is 212c's). Consequences 212a's assertions must absorb: (a) the hit's item GAINS 2
"no model answer" candidates (its staged fake rows) in the loop, no_picture_found CLEARED
(review.upsert clears it when entries are present), and the item file MOVES
aalsum-q3902030.json -> aalsum-q3902030.c_<sha16(t_plan)>.json - so test_nopicture's "hit item
byte-identical" becomes "hit item = exactly those 2 entries, no_picture None"; (b) "every other
item file byte-identical" becomes "unchanged EXCEPT: the 103 new no-item files, the 10 partial
re-upserts, the hit, alauna (n0438_1 replaced in place by the line-check entry); aesica's item
BYTE-IDENTICAL (D2: the stale recorded resolved blocks the write-once; the item still drops OFF
the open list because the derived doc now exists)" + the 233 marked re-stamps (nopicture after
loop: marked set = search set at search time minus the hit, unchanged by the loop).
2. include_sites=True: the tree's web/data/sites (a real dir of 503 entries: 382 per-site
SYMLINKS into the store + 121 real dirs) must be REALIZED - current _link_dir re-links symlinks
as-is, which would route the run's writes into the shared store. Add: after linking web/, walk
tree/web/data/sites; each symlink entry -> os.unlink + _link_dir(realpath(target), entry) (file
hard links, .npy/.npz skipped; measured ~0.11 s, near-zero disk).
3. Served page: the tree gets its OWN server/ (copy the checkout's server/serve.py +
relief_tiles.py into tree/server/ - serve.py binds ROOT to ITS OWN directory, not cwd; the
.venv python has numpy/scipy so the relief tiles import; only GETs are made, so after_write
never fires). Popen [.venv/bin/python, <tree>/server/serve.py, --port 0] cwd=<tree>; parse
"Ancient Works on http://127.0.0.1:(\d+)/" (loopback-only by default). The socket guard MUST
BE LIFTED before starting the server and the page GETs (the test's own urllib would trip it;
the only traffic is loopback to our own ephemeral port - that IS the box's "port 0").
4. Matcher fake on the shared module object (site_done.matchfit IS fit/matchfit.py's module):
matchfit.reachable -> lambda: True; matchfit.run -> fake(root, site_ids) that for CHOOSE sids
in site_ids writes the doc on the site's FIRST candidate row (batch_us.write_doc(root, sid,
row, pairs, score) - commons rows get model/src/url/ref/size, book rows ia/file/book - then
doc.update({"fitter": "matcher", "matcher": {...}}) + batch_us._save_json) and returns the
paths; non-CHOOSE sids -> []. matchfit.spread stays REAL (pure numpy; both the line check and
the expected why-string use it on the doc's SAVED 1dp-rounded pairs - compute the expected
why exactly like site_done._sync_doc/_pattern_entry). Recipes: [0..2] the four 5%-frame
corners -> the site's corners (a true similarity: ratio~1, sd~hundreds px - copy
tests/test_batch_eu.py::_corner_pairs into test_cover, do NOT import across tasks); [3] the
near-line inside alauna's crop.
5. Big stand-ins seeded BEFORE loop: tree/data/raw/commons/big/c_d0a020dec428fa00.jpg +
c_d1ca997e67377769.jpg (solid-colour JPEGs at the row's own size, like 212a's fetch fake; new
inodes - the store's big dir is never touched). plan_fit.load_picture checks os.path.exists
first -> no network. No other stand-ins needed (all 57 pre-existing docs are is_done -> skip;
aesica's big is already in the store; alauna's doc is sent before any build).
6. BOX-3 CHECK through the served page: GET /data/sites.json -> EVERY built site has
drawings >= 1 OR its id is among the served /data/review.json items (the box itself); GET
/data/review.json -> len(items) == the open items RECOMPUTED from the tree's item files with
review.resolved_doc (the page's #rvcount badge renders exactly len(items) for a fresh client -
web/review.js rvOpen) == len(items) of the tree's on-disk web/data/review.json; the golden 21
hand sites drawings >= 1 in the served file; aardenburg/aesica/aire 0->1.
7. Keep 212a's groups (i)-(iv) + the checkout-integrity group as-is EXCEPT the two assertions
called out in 1(a)/(b). Checkout-integrity scope: keep hashing data/ (raw symlink skipped) +
web/data top-level files + docs/ specs/ tests/ as before; for web/data/sites keep the 212a
rule (the per-site dirs are store views SHARED with concurrent agents' tests - hash only the
121 REAL dirs' files, skip the symlinked ones; the run's own overlay writes land only in the
tree's realized copies).
8. tmp_path_retention_policy "failed" stays; the module runs once (~5-6 min expected - the loop
is the big phase: 452 site_done.main calls, each ~2 full item-dir scans (~377 files) + a scoped
review export + set_drawings).

**RISKS / OPEN (check in this order when writing):** (a) set_drawings rewrites the tree's
sites.json 452 times (flock, atomic save_json) - fine, but for UNCHANGED sites assert the
drawings field (not whole-entry bytes): if a later merge changed committed score/oldest values
elsewhere in the file, whole-entry byte pins would be the wrong assertion. (b) The loop's
per-site scoped review.export rewrites web/data/review.json on every CHOOSE-with-item site -
the sync's final full export is the last writer. (c) If the driver merged main before your
session, RE-MEASURE the world (the one-liners: cover._sites/_no_fit_sites/_search_set/_cand_sites
+ the CHOOSE row sizes/items from the data files) before pinning any number - the test
computes the world at setup, but the CHOOSE recipes (pair coordinates) depend on the rows' size
frames. (d) bibracte's 16 uncovered rows -> propose called 16x in the loop; runtime fine.
(e) 212a's test_counts lines for nopicture stay exact (marked = ss minus hit, same count);
the loop phase's stdout (452 site lines) is captured but not asserted beyond presence.

---
(superseded - iteration 228 note, full text in git: `git show 7f444c0:tasks/212b-cover-sync.md`;
its iter-227 block is superseded by it via `git show 2216b8a:tasks/212b-cover-sync.md`. The
05:58-era preflight numbers there are stale where they conflict with the above.)
