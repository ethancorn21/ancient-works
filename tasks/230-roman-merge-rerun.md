Status: open
# 230: The Roman staging into the canonical data - the 211 consolidation re-run
Depends on: 211, 207a, 207b, 807, 808
Touches: fit/merge.py, data/catalog/extras.jsonl, data/commons/files.jsonl, data/commons/classified.jsonl, data/merge/, data/books/index.jsonl, data/books/validation.json, data/books/matches.jsonl, data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py

## Goal
211's lead note: the 211 consolidation ran without the Roman books (207 was stopped by
the owner at merge time) and "207a/207b staging, if it ever resumes, goes through a
later re-run of this step." This task is that re-run. Once 211 is done and the Roman
staging (extras_roman.jsonl / files_roman.jsonl / classified_roman.jsonl plus the three
books' per-book lists/triage artifacts) has landed on main, re-run the consolidation:
fold the Roman rows into data/catalog/extras.jsonl, data/commons/files.jsonl and
classified.jsonl; rebuild data/books/index.jsonl and validation.json from ALL books'
per-book artifacts (including the three Roman books) with the existing machinery;
update the Roman row of docs/sources.md section 9; build any new Roman sites (207c's
are mostly new no-QID Scottish forts) and refresh web/data/sites.json and
web/data/plans.json. The page renders the result with no page change (GOAL.md point 5).

If a 207 subtask is dropped before this task runs, edit the Depends on line to the
surviving subtasks and run against the staging that exists (the boxes hold with the
books that landed).

## Acceptance criteria
- [ ] The fit/merge.py re-run: every Roman staging row is in the canonical files; every
      pre-run canonical row is still byte-identical (pure growth); a second run changes
      nothing (idempotent); the run is logged in data/merge/log.jsonl (0 refused, or
      each refusal logged with its reason).
- [ ] data/books/index.jsonl is rebuilt from the per-book files of all books (the
      post-211 set plus the three Roman books); validation.json regenerated; every row
      that reaches the plan list carries the 200 evidence field; fit/evidence.py check
      passes offline on the merged set including the Roman rows.
- [ ] Every new Roman site id has web/data/sites/<id>/; web/data/sites.json grows by
      exactly the new sites and the pre-run entries are unchanged (except the 212-owned
      marker fields); web/data/plans.json: every pre-run (id, sites[0]) key still
      present, (id, sites[0]) still unique, the new Roman picture rows present
      (tools/export_plans.py re-run).
- [ ] docs/sources.md section 9: the Roman lead row records what was staged and what
      was dropped, per book, sourced from docs/lead_roman.md and the merge log
      (replacing the "NONE in this merge" row 211 wrote).
- [ ] The human's reference is untouched: the 25 hand fits and their 19 sites
      (tests/test_serve.py::test_hand_fits_are_the_reference) still pass after the
      re-run; the re-run's tests are hermetic (port 0, temp tree, no network).

## Notes
- Same invariants as 211: row conflicts (a Roman row equal to a canonical row or to a
  row staged by another source) resolve first-wins, recorded in data/merge/log.jsonl -
  never a silent rewrite.
- Building sites is the slow part (DEM fetch, images); it is a working-phase command.
  The test asserts the data-level result (entries, joins, idempotence) on the served
  data, not a full rebuild.
- When this task runs, tests/test_merge.py's frozen pre-merge baseline (the 385
  entries) shifts to the post-211 state (the 499 entries); update the baseline in the
  test for this intended change.

## Hand-over
(2026-10-14, iteration 213, agent a - step 4 (the 9 site builds) FINISHED by the background process; the plans.json half is 80% done: 44 roman matcher rows appended, export_plans re-run but found the NO-regex trap that silently drops 17 of the 18 roman commons rows; the fix (refine commons.NO's bare `google` to product names) is DECIDED and scoped, NOT yet applied. The harness saved this session's uncommitted files; the next session commits them after applying the fix.)

**State at hand-over (iteration 213):**
- Tree was clean at session start (d3eff2d, driver-merged main). The it.212 nohup'd `data/merge/run_build.py` process RAN TO COMPLETION in the background: `ps` now shows nothing; data/merge/build_sites.log has ALL 9 `=== <id> ok ===` (luguvallium, ardoch, virosidum, cilurni, petriana, congavata, tunnocelum, kirkintilloch, carriden; last one 21:54:31Z). web/data/sites.json = 508 (499+9), all 9 per-site dirs complete and self-consistent (6 english = ea relief.jpg + lidar_credit; kirkintilloch/carriden = scot 0.5m relief; ardoch = aerial-only, lidar_credit None, 2 depictions incl roy_ink + scot-6-first). The driver committed all of it in 0e0372d - the build half of box 3 is DONE and closed; the frozen baselines (data/merge/sites_premerge_baseline.jsonl = 499, plans_premerge_keys.jsonl = 1510) were already re-baselined earlier and current data is pure-growth against both (verified: 0 lost keys, 0 id losses).
- **Step 5 (this session, uncommitted - the harness saved it):**
  1. Ran /tmp/230_romans_full.py (I FIXED two bugs in its copy step first: ia = parts[4] not parts[3]; leaf = int(leafname[1:].split(".")[0]) because basename keeps the .jpg). Result: 30 full images downloaded (24 horsley + 6 maclauchlan - the it.212 "23 leaves" estimate was wrong: cmd_full downloads EVERY leaf referenced by the book's index rows, kind-s AND kind-o, 24 distinct for horsley) + the 18 staged pages copied to data/raw/commons/<site>/<sha16(title)>.jpg + 0/44 roman index rows missing a local full image. All data/raw/ (gitignored, no commit). The script is now correct + idempotent.
  2. `data/books/matches.jsonl` ADDED to my Touches line (done in the task file). Appended the 44 roman rows with /tmp/230_matches_append.py (mirrors books_match.main() row-for-row: match_row -> update(row_id/book/title/site_names) -> HAND (no-op for roman) -> json.dumps+"\n"; skips existing row_ids, so idempotent). File now 934 rows (was 890); the 308166-byte prefix is byte-identical (sha256-verified). Statuses: 6 matched (n0185_3->bremetennacum-q4960578, n0185_5->glannoventa-q16839208, n0244_1->whitehouse-camp-q17678709, n0248_1->brimstone-hill-q24660840, n0248_3->aesica-q4688554, n0286_1->mill-mount-q24661439 - exactly it.210's 6 ties), 25 ambiguous (candidates recorded, incl n0185_4/n0236_1 alauna Q4708853 vs Q7996561 at 1.0/1.0), 13 no_candidate.
  3. Ran tools/export_plans.py -> web/data/plans.json = 1555 rows (was 1510): the 44 roman book rows all present, but only 1 of the 18 roman commons rows (luguvallium, Maclauchlan 1858 - its desc has no "google").
- **THE DISCOVERY (the whole remaining work): commons.NO's bare `google` (re.I) silently re-drops 17 roman files rows.** pipeline/commons.py line 47: NO = re.compile(r"reconstruct|\.svg$|model|diorama|artist'?s impression|google|openstreetmap|..."). keep() (line 192) checks NO against title AND desc. The 17 Horsley files_roman rows' desc all end "...leaf nNNNN of the 936-leaf Google scan (British Museum volume)" - that "Google scan" provenance text matches the bare `google` (the documented harvest heuristic against Google-MAPS map-screenshot junk, DECISIONS-archive 213: the "Google Art Project" drops). So commons.rows() (line 254-261, re-judges every files.jsonl row with the current keep()) drops them, and export_plans' commons_rows() never sees them. The Maclauchlan row's provenance wording has no "Google" - that's the 1 that got through.
- **Blast radius measured (all by running):** (a) the ONLY files.jsonl rows with "google" in title/desc are these 17 roman rows - a refined pattern changes NOTHING else's behavior; (b) refined `google (?:maps?|earth|art|street view|satellite)` (re.I) STILL drops the 2 documented GAp drops (their titles say "Google Art Project" -> hits "google art") so src_artists.py:71's rationale survives; the GAp files were never staged so export_plans can't resurrect them anyway; (c) NO test asserts a google-titled row is dropped (checked test_src_artists/kip/limes/numancia; test_src_kip:233 just wraps keep); (d) keep() only gets more PERMISSIVE, so no staged row flips the other way; (e) batch tests are growth-tolerant by design (test_batch_us/eu docstrings), site-pinned tests (site_done/fit_provenance/owner_check/review/cover) pin only their own sites, which are not roman; (f) side benefit: fit/cover.py:238 (_files_rows+keep) will now count the 9 roman sites as having pictures, so cover won't waste searches re-finding Horsley's own plans. The fix belongs in 230: the box says "the new Roman picture rows present", my it.212 expectation was all 18, and the Goal says "the page renders the result" - the 8 new no-QID sites (cilurni/petriana/congavata/tunnocelum/kirkintilloch/carriden + bar-hill/rough-castle) currently get NO book picture on their fit panel ("None of the plans is matched to this site") because their only picture rows are the dropped files rows (the book rows' sites come from the matcher, which can only tie catalog sites - the 8 no-QID sites have no book-row tie).

**EXACT NEXT STEPS (one remaining chunk):**
1. Add `pipeline/commons.py` to the task's Touches line (first entry after fit/merge.py).
2. Edit NO in pipeline/commons.py: replace the bare `google|` alternative with `google (?:maps?|earth|art|street view|satellite)|` and put a why-comment on/above it: bare "google" also hit book provenance text ("936-leaf Google scan") and silently dropped 17 of the 18 staged roman files rows after the 230 merge (2026-10-14); the junk the rule targets names its product (Google Maps/Earth/Art Project). Quick verify after: a one-liner over files.jsonl - the 17 roman rows pass keep(), a fake title "... - Google Art Project.jpg" still fails.
3. Re-run `tools/export_plans.py` -> expect 1572 rows (1510 + 44 book + 18 commons). Verify: every data/merge/plans_premerge_keys.jsonl key still present, (id, sites[0]) unique, and a SECOND run is byte-identical (sha256 twice - the 211 idempotence precedent). /tmp/plans_before.json holds the 1510-row pre-run snapshot if you need a diff.
4. Run tests/test_merge.py - expect 10/10 (the it.211 open gate test_new_sites_are_complete closes: all 9 built sites exist and are complete; ardoch is the aerial-only/NoLidar case: relief.jpg absent + lidar_credit None = consistent, depictions.json present). Then tests/test_data.py (book rows join index by id; commons rows join files by (sites[0], ref) + sha16; len>=1100 lower bound only - 1572 is fine). Then the full suite `.venv/bin/python -m pytest -p no:cacheprovider` (expect: only the pre-existing red test_fit_queue::test_placement_gestures_and_save_in_the_browser; the last full-suite baseline is 185P/1S/0F from 240's run on a near-identical tree - if docs/site_flow/307d_*.png go dirty from churn, `git checkout main -- docs/site_flow/307d_*.png` and keep them out of the commit, PITFALLS 307d-PNG).
5. GREEN => tick all 5 boxes, Status: done, done claim. COMMIT (team hygiene - NEVER git add -A): only the task's Touches files: pipeline/commons.py, data/books/matches.jsonl, web/data/plans.json, docs/sources.md (unchanged this session - skip if clean), tests/test_merge.py (unchanged - skip if clean), data/merge/ (log/build log changed? build_sites.log grew with the 5 late builds - include data/merge/ if dirty), the 3 canonical files + data/books/index.jsonl + validation.json only if dirty (they should be clean - the merge/index steps were committed earlier). data/raw/ is gitignored (no commit). Message: "230: step 5 - plans.json re-run + the commons.NO google-refinement...".

**PITFALLS to file (next session, under the pipeline/ or a new "pipeline/commons.py" subsection):** (1) commons.NO's bare `google` (now refined to product names) - a book-derived row whose desc carries "Google Books scan" provenance used to be silently dropped after staging because commons.rows() re-judges every files row with the current keep(); the fix keeps product-name junk (Google Maps/Earth/Art Project - the 213 documented GAp drops) out while letting book scans through. (2) books.cmd_full downloads EVERY leaf referenced by the book's index rows (kind-s AND kind-o: 24 for horsley, not the 17 kind-s) - budget downloads accordingly; the /tmp/230_romans_full.py copy step indexes the /download/ URL as parts[4]=ia, parts[6]=leaf filename (https://archive.org/download/<ia>/page/nNNNN.jpg - six path parts after the scheme). (3) books_match.main() must NOT be re-run on the whole index while the file is 890 rows: it would give matches to the 178 civitates/merian index rows that deliberately have none, moving their frozen (id, None) plans keys - append the new book's rows in-process instead (the /tmp/230_matches_append.py pattern).

**Files changed this session (UNCOMMITTED - the harness saved them; commit per step 5):** pipeline/commons.py NOT yet edited (that is next step 2); data/books/matches.jsonl (934 rows); web/data/plans.json (1555 rows - will become 1572 after the NO fix + re-run); tasks/230-roman-merge-rerun.md (Touches line + this hand-over); data/raw/ gitignored (30 full + 18 commons copies); /tmp/230_romans_full.py (fixed), /tmp/230_matches_append.py, /tmp/matches_before.{sha,bytes}, /tmp/plans_before.json.

Re-read: pipeline/commons.py:keep+NO (the refined pattern's comment) and fit/src_artists.py:71 (the GAp-drop rationale that must stay true); web/index.html planMatches()/P.bySite (~line 900: the fit panel lists only plans.json rows whose sites include the site - why the dropped files rows left the 8 no-QID sites with an empty plan list).

**Done (committed earlier):** step 1 (the scoped merge, 45 roman rows, 0 refused, idempotent, 37edbfb), step 2 (index 1068->1112, validation 12 books, evidence re-recorded, check rc 0), step 3 (docs/sources.md section 9 Roman row, ce4ed0b), step 4 (the 9 site builds - the background run finished all of them; the driver committed the result in 0e0372d).

**State at hand-over:**
- Tree clean at session start (d0f0d30). Deps all landed: 211, 207a(done), 207b(done), 207c(dropped), 807/808 done; 809 (horsley-check, agent c) is OPEN but NOT in my Depends line and does not block me (it touches staging files + the horsley fit module/tests/golden - none in my Touches; my remaining work reads canonical data only). The prompt's "agent c on 207a" note = that same 207-family work.
- STEP 4 running: `nohup .venv/bin/python data/merge/run_build.py luguvallium-q71551754 ardoch virosidum cilurni petriana congavata tunnocelum kirkintilloch carriden &` (launched 21:44:10Z, pid 2594083; appends to data/merge/build_sites.log). DONE at session end: luguvallium (26s: ea relief + OS 6-inch, 1 dep), ardoch (40s: scot NoLidar -> aerial-only + roy_ink + scot-6-first, 2 dep), virosidum (25s: ea + 6-inch, 1 dep), cilurni (326s: first ea fetch is the slow one; ea + 6-inch, 1 dep). IN FLIGHT: petriana (started 21:51:11Z); NOT STARTED: congavata, tunnocelum, kirkintilloch, carriden. The nohup'd process may still be alive after this session ends - that's FINE (idempotent per site) but check before relaunching.
- Probes this session (all verified by running, per AGENTS.md): kirkintilloch (1600m box) = scot Phase 5 0.5m coverage 1.00, read_dem 576/576 in 2.9s; carriden (1200m) = Phase 5 1.00, 576/576 in 3.1s -> BOTH build WITH relief.jpg (correction: it.211 hand-over guessed kirkintilloch probably has no tiles - it has 100%); ardoch = NoLidar (aerial-only, as predicted). ea reachable from this VM NOW (luguvallium 60m probe 576/576). box_m: "fort" kind -> 1600m; "roman site" (no keyword hit) -> default 1200m. None of the 9 ids in specs/aliases.json or site_boxes.json.
- Tests when last run: test_merge.py 9 passed / 1 failed (it.211, the open build gate) - not re-run this session.

**EXACT NEXT STEPS (step 4 finish, then step 5):**
1. `ps aux | grep -E "run_build|build_catalog" | grep -v grep`. If a run_build/build_catalog is alive in THIS checkout: just `tail -f` data/merge/build_sites.log and wait (do NOT launch a second). If none: read the log, take the list of ids still not finished (of the 9; done = "=== <id> ok ===" lines), and relaunch `nohup .venv/bin/python data/merge/run_build.py <remaining ids...> &`. A site that died mid-build has data/sites/<id>/ but is NOT in sites.json -> the runner rebuilds it naturally (not skipped); use --force only if a rebuild misbehaves.
2. When all 9 show "=== <id> ok ===": expect web/data/sites.json 499 -> 508, data/merge/build_sites.log has 9 ok-blocks. Then the plans.json half of box 3 (step 5):
3. Run `/tmp/230_romans_full.py` (written this session, NOT yet run; re-run it if cut - it is idempotent): registers both roman fit modules in-process (it.210 pattern: importlib + register()), then books.cmd_full per key (downloads the 23 distinct leaves = 17 horsley + 6 maclauchlan to data/raw/books/<ia>/full/nNNNN.jpg via BookReaderImages.php scale=1), then copies the 18 staged files_roman pages to data/raw/commons/<site>/<sha1(title)[:16]>.jpg, and prints how many of the 44 roman index rows still lack their full image (must end 0). archive.org only.
4. Add `data/books/matches.jsonl` to this task's Touches line FIRST (team rule: add a path before touching it). Then compute the matcher's rows for ONLY the 44 roman index rows in-process (`sys.path.insert(0, pipeline); import books_match; sites,idx,by_name = books_match.load_catalog(); books_match.match_row(r, idx, by_name)` and add row_id/book/title/site_names exactly as books_match.main() does; NO HAND overrides - none apply to roman) and APPEND them to data/books/matches.jsonl. **Do NOT run books_match.main() on the whole index**: it rewrites all rows, and the current 890-row file predates the 178 civitates+merian index rows - a full re-run would give those rows matches, turning their frozen (id, None) plans keys into (id, site) and breaking test_merge.test_plan_list_refresh_is_pure_growth + test_data (the 772 of 1510 baseline keys are site=None). Appending the 44 roman rows is pure growth and keeps all existing bytes.
5. Re-run `tools/export_plans.py` -> web/data/plans.json: expect 1510 + 44 roman book rows + 18 roman commons rows; every pre-run (id, sites[0]) key still present, (id, sites[0]) unique; roman book rows' `book` column shows the raw key (horsley_britannia_romana_1732 / maclauchlan_roman_wall_1858 - not in export_plans' SHORT dict, same as civitates_liber2/merian - acceptable, page shows keys verbatim); roman book rows get sites only where the matcher ties a QID catalog site (load_catalog reads sites.jsonl ONLY - the 8 new no-QID sites are not candidates, so most roman book rows have empty sites: that matches the 772 existing untied rows and is fine - the site ties for the page live in the 18 commons rows' sites=[files row site]).
6. Run `tests/test_merge.py` (expect 10/10: the open gate test_new_sites_are_complete closes once the 9 built sites are in the served data - it checks dir + fields + relief.jpg iff lidar_credit + depictions.json for coverable old-map sites; ardoch has depictions, no relief.jpg, lidar_credit None -> consistent) and `tests/test_data.py` (book rows join index by id; commons rows join files by (sites[0], ref) with sha1(name) id; both safe per this session's reading). If green: tick all 5 boxes, Status: done, done claim. Full suite (`.venv/bin/python -m pytest -p no:cacheprovider`) as the final check - if docs/site_flow/307d_*.png go dirty from churn, `git checkout main -- docs/site_flow/307d_*.png` and keep them out of commits (PITFALLS 307d-PNG). Note the driver flagged test_fit_queue::test_placement_gestures_and_save_in_the_browser as failing at loop start (not my task; if it stays red, record it as pre-existing in the done claim).

**Key facts learned (keep in DECISIONS if not logged yet):** data/raw/ is 100% gitignored (0 tracked files) - no other checkout's raw images ever reach mine; roman triage jpgs (936+171) are here from earlier local fetches, full/ was empty. matches.jsonl is 890 rows (pre-civitates/merian). export_plans includes EVERY index row whose full image is local (no kind filter) - the 10-book precedent is 1068/1068 in the list, so all 44 roman rows belong.

**Commit hygiene (team mode):** never `git add -A`; commit only this task's Touches files (fit/merge.py, the 3 canonical data files, data/merge/, data/books/index.jsonl, data/books/validation.json, data/books/matches.jsonl [after adding to Touches], data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py). data/raw/ is gitignored - its downloads need no commit.

Re-read: data/merge/run_build.py:main - what it does after build_catalog per site (set_drawings marks; --force rebuilds a half-built id) if a build misbehaves on resume; pipeline/books_match.py:main - the exact per-row dict it writes (status + row_id/book/title/site_names + tokens/place/qid/name/score/runner_up/site_id/lon/lat, why+candidates when ambiguous) so the appended roman rows match the machinery's format byte-for-byte.

**Done (committed):**
- Steps 1-2 (it.208-210): the scoped merge (45 roman rows into the 3 canonical files, 0 refused,
  idempotent) + the book-index rebuild (index 1068 -> 1112, validation 12 books, 200 evidence re-recorded
  on all 1112 rows, check rc 0). The driver committed them (37edbfb).
- Step 3 (this session): docs/sources.md section 9 - the Roman lead row now reads "Horsley (1732) and
  Maclauchlan (1858); Roy (1793) dropped" (207a/207b, both fit modules, lead_roman.md) and records per
  book: staged = 45 rows all merged / 0 refused (the log is that run's snapshot; Horsley 17 kind-s =
  100% of the list, 8 new no-QID extras rows, Maclauchlan 1 of 3 kind-s -> new luguvallium-q71551754 row;
  every row caption_coords); dropped = n0078/n0111 blank in this copy, 10 kind-o leaves indexed-only,
  Horsley's ~121 inscription plates deferred, Roy DROPPED (owner, ask 008). The row also records the
  evidence re-record on all 1,112 book rows and the matcher's 6 one-pair ties (2 genuine / 4
  questionable, never silently kept). The section intro line notes the 2026-10-14 re-run (230).
  test_merge.py: 9 passed / 1 failed - the one red is the EXPECTED open build gate
  (test_new_sites_are_complete: "no new sites: the build phase produced nothing"), closing at step 4.
- Corrections logged in DECISIONS it.211: the it.210 hand-over's tie counties were wrong -
  whitehouse-camp-q17678709 is HEREFORDSHIRE (Michaelchurch Escley), mill-mount-q24661439 is SUFFOLK
  (Redisham); sources.md records the catalog's counties.

**STEP 4 (next session) - build the 9 new Roman sites (box 3). Open question RESOLVED (probes, it.211):**
1. Check `ps aux | grep run_build` first (PITFALLS: only one run_build at a time).
2. `nohup .venv/bin/python data/merge/run_build.py luguvallium-q71551754 ardoch virosidum cilurni
   petriana congavata tunnocelum kirkintilloch carriden &` - one process per site, appends to
   data/merge/build_sites.log; a kill leaves a clean boundary at the last finished site (build_catalog
   skips already-built ids; --force rebuilds a half-built one). Expect web/data/sites.json 499 -> 508.
3. What each site gets (probed):
   - 6 ENGLISH (luguvallium, virosidum, cilurni, petriana, congavata, tunnocelum): source "ea"
     (Environment Agency composite DTM, EPSG 27700) - reachable from this VM (cilurni probe: finite data
     in 1.0 s) -> relief.jpg + lidar_credit.
   - 3 SCOTTISH (ardoch, kirkintilloch, carriden): main ORDER -> None; the STATIC fallback picks "scot"
     (pipeline/lidar_scot.py - a local S3 mirror of the Scottish national LiDAR, no service/key).
     ardoch (Gask Ridge) throws aw.NoLidar "no Scottish LiDAR tiles on this box" (the mirror holds
     selected tiles only) -> it builds AERIAL-ONLY + the NLS 1747-55 military-survey overlay
     (depictions.json present, no relief.jpg - the test's self-consistency holds). Before starting,
     probe the other two the same way (5 s each): `.venv/bin/python -c` with sys.path pipeline,
     `import lidar_scot, aw; lidar_scot.read_dem(aw.site_bbox(lon,lat,60,60),24,24,lon,lat)` on the
     kirkintilloch and carriden coords from extras.jsonl (carriden is near Bo'ness - same region as the
     four built Antonine Wall camps, which carry scot-6-first.webp; kirkintilloch (Badenoch) probably has
     no tiles). nls.covers() is True for all 3 Scottish sites (and all 9), so NONE can end up
     "NOT BUILT" (that needs no LiDAR AND no old map).
4. If a session is cut mid-build: `ps` for run_build, kill it, commit what finished, resume the remaining
   ids next session (the runner and build_catalog are both idempotent per site).

**Then (same or later sessions):**
5. `tools/export_plans.py` re-run: plans.json (1,510 baseline keys) pure growth - the roman picture rows
   (17 horsley + 1 maclauchlan; the files/classified rows for the 1510-era catalog QID sites included)
   appear; test_merge.py asserts pure growth + uniqueness.
6. Full suite `.venv/bin/python -m pytest -p no:cacheprovider` - expect ALL green (the open gate closes).
   If docs/site_flow/307d_*.png go dirty from suite churn (PITFALLS 307d-PNG), restore main's bytes
   (`git checkout main -- docs/site_flow/307d_*.png`) and leave them out of the commit. Then tick all 5
   boxes, Status: done, done claim.

**Commit hygiene (team mode):** never `git add -A`; commit only this task's Touches files
(fit/merge.py, the 3 canonical data files, data/merge/, data/books/index.jsonl, data/books/validation.json,
data/sites/, docs/sources.md, web/data/sites.json, web/data/sites/, web/data/plans.json, tests/test_merge.py).

Re-read: data/merge/run_build.py:main - what it does after build_catalog per site (set_drawings marks
refresh; --marks-only mode) if a build misbehaves; pipeline/nls.py:covers - the exact coverage ring, if a
Scot site unexpectedly lands "NOT BUILT".
