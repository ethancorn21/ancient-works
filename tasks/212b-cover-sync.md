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

(2026-10-13, iteration 232, agent a - **WORLD RE-MEASURED AT HEAD 0e6d5df + EVERY MODULE THE TEST
DRIVES RE-READ (fit/cover.py, tools/site_done.py, fit/batch_us.py, fit/review.py,
pipeline/plan_fit.py, fit/matchfit.py, fit/propose.py, tests/conftest.py, tests/test_fit_queue.py,
tests/test_batch_eu.py::_corner_pairs, the golden files). NO CODE WRITTEN this session (hit the
context limit after the measurements); tests/test_cover.py is STILL 212a's 770-line version.
**ONE CORRECTION to the iter-231 census, then all its pins hold. The iter-230 note with the
full design (recipes, the mirror, the GUARD pattern, the end-state derivations) is
`git show 45675c9:tasks/212b-cover-sync.md` - read it first; this note updates it.**)

**THE CORRECTION (everything else in the iter-231 note holds, re-verified digit by digit this
session):** the "10 partial" sites are NOT partial-overlap items. The true census of the 218
with-row nofit sites: **105 allcovered + 0 partial + 103 no-item-file + 10
item-file-with-EMPTY-candidates**. The 10 empty-candidate items (all resolved None, all
carrying the batch-era no_picture "web/data/plans.json (1166 rows, matched by the sites
field)"): aventicum, bibracte-q650053 (16 rows), hopewell-mound-group, los-millares, maeshowe,
motte-castrale-quiquempois-q22961457, numancia, stones-of-stenness,
the-roman-fort-vicus-bridge-abutments-an-q17650519, trundle-q7847949. (The iter-231 note's
"partial" bucket evidently counted these empty-candidate items.) CONSEQUENCE FOR THE DESIGN:
at loop time there are **11** empty-candidate item sites with rows (the 10 + the hit aalsum
after staging). Each goes through run_sites with uncovered = ALL its rows (no docs, item_cands
{} -> the keep-restore restores nothing): every row upserted "no model answer" + the
propose-for-checkout extras, or coarse when propose raises (the hit's two staged rows - not in
the checkout's plans.json -> ValueError -> coarse); no_picture_found CLEARED (entries
non-empty); resolved stays (write-once; None for all 11); the file MOVES to
<site>.<lead>.json (lead = candidates[0].plan = the first of the site's rows in the TREE's
plans.json order - read it, don't pin the order; the old <site>.json is unlinked). End shape =
identical to the 103 no-file sites' fresh items ({site, candidates, no_picture_found None,
resolved None}) except the rename and the surviving write-once fields. The 105 allcovered,
the sync phase, aesica's D2, beth/shotwick, the CHOOSE sites and every other iter-231 pin:
UNCHANGED (all re-verified this session: docs 57 = 21 hand + 36 by:agent matcher, ALL is_done,
0 line-check failures; CHOOSE = aardenburg-q955 / aesica-q4688554 / aire-sur-la-lys-q259903 /
alauna-q4708853 with the pinned row ids/sizes/map_box - CHOOSE dirs = 2 real (aardenburg, aire)
+ 2 symlinked (aesica, alauna) -> the realize converts all 382 symlinks anyway; aesica item
1-cand with the STALE recorded resolution {doc: aesica-q4688554.c_e28ed261168b49c9, at:
2026-10-12T03:13:35.590448+00:00} -> D2 (byte-identical, drops off the open list); alauna
5-cand item resolved None, first row = book earthworkenglan01allcgoog_n0438_1 [3367,5050]
map_box [0.12,0.25,0.83,0.66]; bethlehem dep map-only (tmk1850.webp, item 22 cands) and
shotwick dep map-only (six-inch-1st.webp, item 2 cands), both drawings 0; item files 377, open
365; web/data/review.json at 2026-10-13T11:26:15.291892+00:00 with 365; plans 1510 rows; store
big cache 75 (aesica's c_e28ed261168b49c9.jpg present; aardenburg's c_d0a020dec428fa00.jpg and
aire's c_d1ca997e67377769.jpg ABSENT -> seed; web/data/sites = 382 symlinks + 121 real dirs;
hit aalsum-q3902030 (item aalsum-q3902030.json, candidates [], batch-era no_picture); fail
site = craig-phadrig (the ONLY no-qid search-set site with a files.jsonl title); spot_n =
aggersborg).

**LOOP END STATES (replaces the iter-231 "10 partial" paragraph; the rest of that note
stands):** after loop + nopicture - 105 allcovered: item byte-identical EXCEPT aesica (still
byte-identical - D2 write-once) and alauna (the n0438_1 candidate REPLACED in place by the
line-check pattern entry: why = "line check: matcher points nearly on a line (spread 0.00,
0 px): the scale is not pinned; the gate's 25.0 m measures internal consistency of the anchors,
not their truth" - recompute (ratio, sd) with matchfit.spread on the fake's normalized pairs
and format like site_done._sync_doc/_pattern_entry does; the other 4 cands + resolved None
untouched); bethlehem/shotwick byte-identical (audit whys survive). 11 empty-candidate sites
(the 10 + the hit): as above (all rows re-upserted, file moved, no_picture cleared, resolved
None) - open. 103 no-file sites: fresh <site>.<lead>.json, all rows "no model answer" + propose
extras or coarse, open. aardenburg/aire (the 2 CHOOSE no-item sites): NO item created
(need_fit False once the fake matcher wrote the doc), each gains its matcher doc
(by:agent, fitter:matcher, auto True, score 25.0) and drawings 0->1; aesica: doc built, item
byte-identical, drawings 0->1, OFF the open list. 233 non-hit search-set sites: item
byte-identical through the loop, then the nopicture phase marks them (the record's searched
string + new at; candidates/resolved untouched). Item files after the loop = 377 - 11 (old <site>.json unlinked for the 10 empty-cand + the
hit) + 112 (new/moved: 101 = the 103 no-file minus the 2 CHOOSE, which get docs not items, +
11 renames) = 478; OPEN = 365 - aesica + 101 = 465 (recompute with review.resolved_doc - do
NOT pin the arithmetic; the 11 renamed were already open, only the 101 fresh files add). SYNC:
60 docs (57 pre + 3 CHOOSE) ALL "skipped" (the 3 were built in the loop; the 57 are is_done)
-> stdout "sync: 60 document(s) over N site(s)" (N = the recomputed distinct doc sites) +
"sync: 465 open of 478 item(s)"; NO
"pruned" line (beth/shotwick deps map-only - the live sync already pruned the stale plan
entries); beth/shotwick dep files byte-identical; the full export is the only page-file
writer. SERVED (port 0, our own loopback only): every built site drawings>=1 OR in the served
review.json items; the 19 golden sites (tests/golden/hand_fit_sites.txt) drawings>=1;
aardenburg/aesica/aire 0->1; every other site's drawings == the committed (checkout) value
(assert the field, not whole-entry bytes - set_drawings re-stamps score/oldest/overlays from
the site's own dep); served review.json items == the open items recomputed from the tree's
final item files (fields site/name/lead/candidates/no_picture_found, name order) == the
tree's on-disk web/data/review.json.

**EXACT NEXT STEP: write the extended tests/test_cover.py** (keep 212a's 770-line structure -
it is on disk; the full mechanics are the iter-230 note's "EXACT NEXT STEP" sections 1-6 in
`git show 45675c9:tasks/212b-cover-sync.md`, applied with the corrected census above):
PHASES = ["fetch","search","stage","loop","nopicture","sync"] (NO separate export phase - it
duplicates sync's trailing export; report stays 212c's); build_tree(include_sites=True) then
REALIZE (walk the tree, each symlink -> os.unlink + _link_dir(realpath(target), entry); the
121 real dirs stay as built); shutil.copytree checkout server/ -> tree/server/; seed the two
big stand-ins AFTER build_tree (tree/data/raw/commons/big/c_d0a020dec428fa00.jpg 500x500 +
c_d1ca997e67377769.jpg 1280x986, solid-colour PIL JPEGs - new inodes; plan_fit.load_picture's
os.path.exists short-circuits the download); Fakes gains matchfit.reachable ->
lambda url=None: True and matchfit.run -> the fake with the REAL signature
run(root, site_ids, dry=False, url=None, roma_url=None): for each CHOOSE sid, write
batch_us.write_doc(tree, sid, first-candidate-row, recipe-by-position, 25.0) +
doc.update({"fitter":"matcher","matcher":{small fixed dict}}) + batch_us._save_json, return
paths (copy matchfit.run's doc shape); non-CHOOSE -> []; recipes: CHOOSE[0..2] =
test_batch_eu._corner_pairs COPIED (5%-frame corners on the site's 4 [lon,lat] corners -
verify at setup: fabrication_pattern None AND spread ratio>=0.1 sd>=20), CHOOSE[3] = u
500/900/1300/1700 v 1300/1320/1340/1360 (exactly collinear -> spread (0.0, 0.0)) with lon/lat
interpolated along the site's corners; setup preconditions fail loudly (40 golden files
byte-match; all 57 docs pass the line check AND are is_done; CHOOSE == the pinned 4 with
pinned row ids/sizes/map_box; the recipe checks; beth/shotwick map-only; store big has
aesica's stand-in; the 10 empty-candidate list above); run the 6 phases in-process (the
socket guard stays up THROUGH loop/sync - the only network the phases would use is what the
fakes/stand-ins remove); then the server per tests/test_fit_queue.py's pattern
(subprocess.Popen([sys.executable, "-c", GUARD, "server/serve.py", "--port", "0"], cwd=tree)
- under .venv/bin/python sys.executable IS the venv python, so relief_tiles imports - a
reader thread appends stdout, poll for "Ancient Works on (\S+)" with a 90 s deadline, then GET
/ until 200; LIFT the in-process socket guard before the urllib GETs of /, /data/sites.json,
/data/review.json from our own 127.0.0.1:PORT; terminate+kill in teardown); assertion
functions per the "LOOP END STATES" + "SERVED" paragraphs above, PLUS 212a's (i)-(iii)
search/counts/stage assertions (unchanged) and (viii) checkout integrity = 212a's hashing
(data/ minus raw, web/data top-level files, docs/ specs/ tests/) PLUS the 121 REAL per-site
dirs (computed dynamically: the non-symlink entries of the checkout's web/data/sites) hashed
before/after, and assert the tree's site dirs are all real dirs after realize. RUN:
`.venv/bin/python -m pytest tests/test_cover.py -q` (never bare pytest - no numpy/PIL);
budget ~5-7 min (the loop = 452 in-process site_done calls, each with a scoped review export
~0.32 s + the propose calls for the 114 no-file/empty-cand sites' rows; the 3 CHOOSE builds).
Then the FULL suite `.venv/bin/python -m pytest tests/ -q` - known non-212b red on this VM:
test_fit_queue.py part-4 gestures (307bb, pre-existing, belongs to the 307 series).

**RISKS (check in this order if an assertion bites):** (a) the loop's per-site scoped
review.export rewrites the tree's web/data/review.json 452 times - the sync's full export is
the last writer, so the served file is the sync's; (b) set_drawings creates
web/data/sites.json.lock ONLY in the tree (a new file appearing in the CHECKOUT would trip
the integrity diff - it won't: the lock is created only under the tree root); (c) propose's
_CACHE keyed (str(root), kind): the mirror must call propose_for WITHOUT root (the checkout),
exactly as batch_us.run_sites does; (d) if a merge moved the world again, the setup
preconditions fail loudly - re-measure (the census one-liner this session ran; the
iter-229 note has the originals) and update the pins; (e) bibracte's 16 rows -> 16 propose
calls in the loop (runtime fine); (f) the 10 empty-candidate sites include numancia - its
c_0fa271e2444f7bfc row (233) is a COMMONS row: the entry mirror must call
review.candidate_evidence(row_id, tree) for the 200 evidence field (same bytes as the
checkout); (g) the served-page "review count" contract = the served review.json's item count
is what web/review.js's rvOpen renders for a fresh client (seen={} -> all items) - checked
through the served file, no browser needed.

**Do NOT touch:** requirements.in/.txt (302a/304), tests/conftest.py, and any module the test
only calls (site_done, batch_us, matchfit, review, plan_fit, build_site, propose, evidence,
commons, export_plans, serve.py) - monkeypatch in the test or file a new task. Agent c's
in-flight 203b/207/302a/304/306 work is other tasks' business.
