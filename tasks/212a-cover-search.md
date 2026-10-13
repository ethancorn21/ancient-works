Status: open
# 212a: Cover search - a targeted picture search for every uncovered site, "no picture found" items
Depends on: 211
Touches: fit/cover.py, data/review/, data/commons/files.jsonl, data/commons/classified.jsonl, data/raw/commons/, web/data/plans.json, tests/test_cover.py

## Goal
For every built site with no fit document and no plan candidate in web/data/plans.json:
one targeted search (the site's QID Commons category, P180 depicts, a title search),
recorded. A found picture is staged the normal way (files.jsonl + classified.jsonl with
the 200 evidence field, a local copy under data/raw/commons/, its row in plans.json via
tools/export_plans.py). A site where nothing is found gets a review item marked
"no picture found" with exactly what was searched. The fit itself is NOT this task: the
lead runs fit/matchfit.py + tools/site_done.py over the found pictures afterwards (lead
note ef84a05 - the matcher is the fit, never the vision-model fit).

## Acceptance criteria
- [ ] fit/cover.py search: lists the uncovered sites (no platefit doc, no plans.json row),
      searches each, writes found pictures into the canonical files and a local copy,
      re-exports plans.json; prints counts (searched / found / nothing).
- [ ] fit/cover.py nothing-found: a review item per site, marked "no picture found",
      listing the queries and the date.
- [ ] tests/test_cover.py (no network: a recorded fake search response, sockets dead):
      one site with a hit gets staged rows + a plans row; one site without gets the
      review item with its queries.
- [ ] Run it for real once and commit the results.

## Notes
- Commit working code every session. Notes-only sessions end the job (212 ended that way).

## Hand-over

(2026-10-13, iteration 217, agent a - **tests/test_cover.py WRITTEN (uncommitted, in the
working tree) but NOT YET RUN; the session hit the context limit right after writing
it.** Box 1 of my task file is now substantially in place (the search/stage/nopicture
test). **EXACT NEXT STEP: (A) fix the KNOWN DEFECTS in tests/test_cover.py listed
below (they are marked with "placeholder" comments and I list them all - the file will
not pass as-is); (B) `git add DECISIONS.md tasks tests/test_cover.py && git commit`;
(C) mark tasks/233 + tasks/234 Status: done, all boxes ticked (lead's instruction,
verified iter-216, still valid - re-verify with a 30-second test run first: `.venv/bin/python -m pytest tests/test_merge.py::test_plan_list_refresh_is_pure_growth tests/test_fit_queue.py::test_fit_queue_real -q`); (D) run
`.venv/bin/python -m pytest tests/test_cover.py -q`, fix what it exposes (expect
iteration on the fakes' edge cases), then the full suite in the FOREGROUND (PITFALLS:
basetemp race); (E) live run (box 4) remains a LATER session, waits for 203b.**

**KNOWN DEFECTS in tests/test_cover.py (written, unrun - fix before first run):**
1. `test_counts`: the first two asserts on the fetch line are GARBAGE placeholders (one
   with `or True`, one dead `if False else None`) - DELETE them; keep only the final
   checked line, and fix its numbers to the product's own arithmetic: expected =
   "fetch: %d row(s) with a local copy, %d without a source, fetched %d thumb(s) + %d
   url-only" % (world["n_have"] + world["n_nosrc"], world["n_nosrc"], world["n_thumb"],
   world["n_url"]) (product's n_have counts the nosrc rows too: len(rows) - thumb -
   url; n_thumb/n_url = world's missing-fetchable counts - the fake fetch never fails).
2. `test_stage`: the last 4 lines contain two GARBAGE placeholder asserts (`"files_bytes"
   if False else "searches_bytes"` etc.) - DELETE them; keep only the final
   byte-identical re-export check.
3. **before/after item key mismatch**: `run["before"]["items"]` is keyed by CHECKOUT
   paths (world's snapshot) but `run["after"]["items"]` by TREE paths - test_nopicture's
   per-file identity compares them and will fail on key mismatch (before.get(tree_path)
   -> None). FIX: in the `run` fixture, build `before["items"]` from the TREE after
   build_tree (same shape as `after`), keep world["items"] only for the
   candidates/resolved pre-values (its `_pre_by_site` lookup is path-agnostic).
4. `build_tree` web-branch: with include_sites=False it links the whole web/ then
   rmtree's web/data/sites contents (works, ~3147 wasted links); with
   include_sites=True the `if top != "web"` fall-through means **web/ is never linked
   at all** - broken seam for 212b. Clean it up when 212b flips it (or now): one
   builder with a per-top skip list for web/data/sites.
5. Minor: `run` fixture does `out["ss_at_search"] = cover._search_set(tree)` inside the
   try block before `cover.search` - fine, but it is only set if fetch didn't raise;
   the fixtures' world["ss"] (checkout) equals it on the current machine.

**VERIFIED THIS SESSION (all on the current merged tree, main tip 206e4b5 IN my branch
via merge-base == main; aeeb5aa (lead's 233+234) present):**
- Live state re-measured, MATCHES iter-216: built 499; docs 131; nofit 402; cand sites
  601; plans 1475 rows; search set 245 = 204 qid + 41 no-qid; no-qid-with-title set
  EMPTY (D1: every record's failed == []); hit = aalsum-q3902030 (Q3902030, name
  "Aalsum", no existing titles, pre-existing BARE item aalsum-q3902030.json with the
  batch-era no_picture string); all 245 search-set sites have bare plain-named items
  (246 bare total, 100 candidate/lead-named among 346 item files).
- **PURE GROWTH HOLDS ON THIS MACHINE**: all 405 committed commons keys and all 1068
  committed book keys have local copies in the VM store (aeeb5aa's Mac<->VM sync held
  for both branches) - the key-set assertions' lost/gained sets are empty today
  (they stay armed as state-aware guards for future store drift). The one kept
  files.jsonl row missing a copy ("The Geometrical Ground of the Plan of Stonehenge",
  Stukeley TAB XI, by fit/src_wiltshire_stukeley.py, sha c_3e7c76bf954bd4d3) has no
  thumb AND no url (a book-derived 211-consolidation row) - the fetch phase counts it
  "without a source" and it is NOT in the committed plans.json (its book has 0 rows in
  data/books/index.jsonl on this machine) - so it neither fetches nor drops anything.
  328 titled rows lack copies but 327 of those are non-kept (the 216 note's "328"
  counted titled rows; only kept rows matter to fetch/export).
- **fit/cover.py re-read in full (863 lines, unchanged since 55678e3)**: exact
  signatures verified for the fakes - _search_site's record fields; keep/NO mime
  filter order (mime before keep); _stage_row's field order (site,qid,title,year,
  wd_plan,cat,by,**meta 10 keys) -> the test builds the expected files.jsonl line
  bytes from that exact dict; stage appends json.dumps rows; evidence.record(live=False)
  is a NO-OP here (by:"212" not in source_tables() - {pipeline/sources.py deventer,
  kip, mackenzie} - and every book row already carries rec "evidence/1" (1068/1068)
  -> neither file is rewritten); _regen_plans re-points export_plans.ROOT/BOOKS +
  commons.OUT/RAW and restores (the fixture uses it for the pre-phase baseline
  re-export, then restores the committed plans bytes); _searched_string format
  (mirrored in expected_searched; spot-checks pin the wording literally);
  nopicture upserts via review.upsert_item (entries=[] keeps candidates, dict sets
  no_picture_found, resolved write-once, lead=None -> <site>.json, atomic new inode);
  _claims does one batched wd_claims call for all 204 qids; search() skips
  already-recorded sites (resumable) and writes searches.json per site via
  batch_us._save_json (atomic).
- **commons.py re-read**: search()/files_of() return "File:"-prefixed titles (the
  real convention; the fakes match it); MAX_YEAR=1925; year_of/keep on the fake
  titles verified by hand (1701/1850 kept via title year; 2010 dropped; the special
  title-year override does NOT fire for (c. 2010)); info() returns the 10-key meta
  the record stores verbatim; export_plans' commons_rows skips unclassified rows
  (min_p=0.3) and PIL-opens every local copy for [w,h] (the fake JPEGs are real
  1280x960); new plans row shape = [c_sha16, "Wikimedia Commons", None, None,
  name, when, [1280,960], None, [site], cite, media url, False, title] with
  when="1701"/"1850" (when_of on empty date) and cite = the page url only.
- **evidence.py fetch_page_ids -> {title: pageid}; fetch_file_entities(page_ids)
  -> {title: {item, p180}}** (title-keyed - the fakes match); review._find_item
  measured at **4 ms** (not 216's 200-300 ms estimate) -> nopicture ~2 s, the whole
  test module should run in ~15-20 s.
- conftest.py re-read: my test does NOT use the session `served` fixture (212a has no
  server; the parent's page checks will start their own port-0 server after the
  phases, per the parent hand-over) and does not edit conftest. The basetemp-race
  PITFALLS (pytest 9.1.1, shared TMPDIR basetemp, green session rmtree's it) means:
  run the suite in the FOREGROUND, never a second concurrent pytest in this
  checkout; the module fixture's tree lives under basetemp and is hard-linked
  (near-zero disk; retention "failed" already in pytest.ini, re-declared per module).
- data/cover/ does not exist in the checkout yet (the builder unlinks the tree's
  searches.json defensively for the post-live-run state); the store (real dir behind
  the data/raw symlink) has 0 symlinks, 0 .npy/.npz, ~11531 files, 3.8 G (growing -
  other agents write to it, so NO store file-count assertions; the only store check
  is that no <hit> dir appears in data/raw/commons). checkout_hashes() covers data/
  (raw symlink skipped), web/data top level (6 files: catalog.json fit_queue.json
  plans.json review.json sites.json sites.json.lock world.jpg), docs/ specs/ tests/
  (skips __pycache__, .npy/.npz, symlinks).

**212a DESIGN AS COMMITTED IN THE TEST (settled iter-216, encoded now):** one
module-scoped fixture builds the tree (hard-link web/data/docs/specs/tests EXCEPT
the 3 in-place files copied; data/raw a REAL dir of hard links to the store; web/
/data/sites skipped) + world + baseline re-export + fakes (socket guard + time.sleep
no-op + Fakes class patched onto the shared module objects), runs fetch->search->
stage(classifier fake, live=False)->nopicture, re-runs search/stage/nopicture,
snapshots before/after; 5 test functions assert (i) searches.json per-site records +
resumability (ii) stdout counts (iii) stage bytes/rows/plans keys + exact new rows
(iv) nopicture items with the exact searched string (spot-checked literally) +
byte-identity of everything else (v) checkout integrity. No loop/sync/export/report
- those are 212b/212c extending this same file (seams: PHASES, include_sites).

**LIVE RUN (box 4) - later sessions, genuinely waits for 203b (agent c, in flight):**
fetch (1/s paced, resumable; today: 0 fetches - everything fetchable already has a
copy; 1 "without a source" row, the Stukeley TAB XI - if the live run's key-set
diff ever shows it lost, record it as a data finding per the 212 hand-over's rule;
it is not in the committed plans.json so its loss is not a committed-key loss) ->
search (real Commons/Wikidata, resumable via data/cover/searches.json) ->
stage --live (evidence record for the new rows; ask_human ONLY if new files found and
clef 127.0.0.1:18083 still down: tunnel, or approve the LLM on 8081 as one-off
classifier) -> nopicture -> commit (searches.json, grown files/classified.jsonl,
new raw copies (data/raw gitignored - note it), item files, re-exported plans.json -
record the (id, sites[0]) key-set diff: lost keys = data finding, expected pure
adds) -> `sha256sum -c tests/golden/hand_fit_docs.sha256` must pass 40/40.
The loop is the LEAD's (ELoFTR 8091; RoMa 8092 down, skipped; LLM 8081 forbidden
for placement); sync/export are 212b's; report is 212c's.

---
(iteration 216 hand-over, superseded sections kept in git: `git show
590284f:tasks/212a-cover-search.md`.)}

**233/234 VERIFIED THIS SESSION (lead instructed marking them done once main merged;
aeeb5aa IS in my branch via 400431f):**
- 233: `test_plan_list_refresh_is_pure_growth` PASSES (0.07 s, green, .venv). aeeb5aa
  re-exported plans.json (1474 -> 1475 rows, numancia row back). PITFALLS already has
  the machine-dependence entry (### tools/export_plans.py, ~line 1256, added by my
  212 investigation) -> box 3 satisfied. The test's docstring note (box 3's other
  half) is the lead's to add if he wants; the lead said done, so tick it.
- 234: `test_fit_queue_real` PASSES (4.1 s, green). The (view, -px, plan, name) key
  change is in aeeb5aa; tools/fit_queue.py untouched. Box 2 verified on the VM with a
  scratch tree (hard-linked web/ + data/, data/raw re-linked as symlink; generator
  never opens images): two regenerations byte-identical apart from "at" (timestamps
  only); entries: committed 229 vs VM-regenerated 230 - the ONLY diff is the site
  'numancia' (in regen, not committed): machine-dependent 'built' rule (VM's shared
  store holds the numancia site dir, the lead's Mac did not) - the same environment
  effect 233 documents, not a state drift. Box 2 holds on the machine the committed
  file was generated on -> tick.
- When marking done, also record this verification in DECISIONS.md.

**Live state re-measured THIS session (merged tree, aeeb5aa present; use for the
test's state-aware preconditions - they are computed at run time anyway):** built
499; docs 131; nofit 402; plans rows **1475**; search set **245** = 204 qid + 41
no-qid (numancia DROPPED OUT - it has its plans row back); with-row nofit **157**
(numancia back in it); CHOOSE unchanged (aardenburg-q955, aesica-q4688554,
aire-sur-la-lys-q259903, alauna-q4708853); **first qid search-set site (the fake's
HIT site) = aalsum-q3902030, qid Q3902030, NO existing files.jsonl titles**;
**no-qid-with-title set is now EMPTY (numancia was the only one) -> per D1 the test
asserts it is empty: no failure site, every record's failed == []** (the fake's
commons.search RAISES branch only fires if the set is non-empty again - code both
branches); all 245 search-set sites already carry the batch-era no_picture mark;
**328 titled files.jsonl rows lack a local copy** (the live fetch phase's work;
in the test the fake _fetch_one fills all of them, ~10 ms each).

**SETTLED 212a TEST DESIGN (tests/test_cover.py does NOT exist yet):**
1. One module-scoped fixture builds the tree and runs the phases ONCE; test
   functions assert groups (module-scoped = manual save/restore monkeypatching in
   try/finally, not pytest's function-scoped monkeypatch). Run under
   `.venv/bin/python -m pytest`; tmp_path_retention_policy "failed" (48 GB box).
   Tree (D3, 212a-scoped): hard-link every file of web/ data/ docs/ specs/ tests/
   EXCEPT (a) data/raw - build a REAL dir walking the shared store
   (/home/agent/projects/ancient-works/data/raw, the symlink target; makedirs +
   os.link every file, skip .npy/.npz) - stage/fetch write new inodes there; (b)
   the 3 IN-PLACE files as REAL copies (shutil.copy2): web/data/plans.json
   (export_plans json.dump open("w")), data/commons/files.jsonl + classified.jsonl
   (stage open("a")); (c) web/data/sites/<id> subdirs SKIPPED entirely (212a's
   phases never touch them - fetch/search/stage/nopicture read only web/data/
   sites.json; the builder takes an include flag so 212b can flip it for the sync).
   Everything else writes atomic tmp+os.replace (verified: batch_us._save_json,
   review._save_json, evidence.rewrite) -> hard-link-safe. **Before running: delete
   the tree's data/cover/searches.json if present (live tree will carry my live-run
   records after box 4; the search phase skips already-recorded sites, which would
   break the fake-hit site - unlink is safe: the live file keeps its own dir
   entry). Then the search re-runs the whole set under the fakes - deterministic
   before AND after the live run.**
2. Fakes (pure functions of inputs, monkeypatched on the SHARED module objects -
   cover imports commons/evidence/aw etc. once; patch the attributes): no_network
   (socket.socket.connect AND socket.create_connection -> AssertionError);
   cover.time.sleep -> no-op (it IS the global time module); cover._fetch_one ->
   write a valid solid-colour 1280x960 JPEG via PIL (export_plans commons_rows
   PIL-opens every local copy - invalid bytes would crash the re-export) and return
   True; commons.wd_claims(qids) -> for the HIT qid {cat: "Fake category of <name>",
   plan: [T1 bare title], image: []}, every other qid -> {} (falsy: _search_site
   skips the cat/P180 block); commons.files_of(cat) -> ["File:"+T1, T2, T3modern,
   T4video] for the hit cat, else []; commons.search(name) -> [T1, T2] for the hit
   name, else [] (RAISES RuntimeError only for a failure site, if D1's set is
   non-empty); commons.info(titles) -> T1/T2: {url/thumb fake, w/h 1280/960, mime
   image/jpeg, date "", desc "", artist "", license "", page ""} (year from the
   title: 1701/1850 -> kept), T3: date 2010 (dropped by keep), T4: mime video/mp4
   (dropped by the mime filter); evidence.fetch_page_ids -> {t: 1000+i};
   evidence.fetch_file_entities -> T1: {"item": "M<id>", "p180": [hit qid]}, others
   {"item": "M<id>", "p180": []}. Titles: T1 = "Plan of <name> (c. 1701).jpg",
   T2 = "View of <name> (c. 1850).jpg" (name = the hit site's name from
   sites.json; NO-regex-clean; verified not in existing files.jsonl). Precondition
   checks (fail loudly): search set non-empty; hit site has a qid and is in the set;
   T1/T2 pass commons.keep with the fake meta; T1/T2 not already in files.jsonl;
   the no-qid-with-title set == the measured set (currently empty).
3. Drive in-process (each takes the tree root): cover.fetch (the 328 missing copies
   via the fake, then _regen_plans) -> cover.search -> cover.stage(classifier=fake,
   live=False) -> cover.nopicture. The injected classifier returns one
   {p_plan: 0.9, p_birdseye: 0.1, p_photo: 0.1} per row aligned with the todo list
   (stage's contract: classifier receives [r for r in rows if r["local"]]).
   cover._regen_plans re-points export_plans.ROOT/BOOKS + commons.OUT/RAW itself.
   Do NOT run loop/sync/export/report here - the loop is the lead's (matcher on
   8091, live only); sync+export are 212b; report is 212c. They extend this same
   file later (fixture seams: the phase list and the sites-view flag).
4. Assertions (ALL state-aware - world computed once in setup from the checkout's
   live files; the tree is a byte-copy so checkout values == tree values pre-run):
   (i) searches.json: keys == exactly the search set; hit record: qid == Q3902030,
       cat == the fake cat, n_cat_files 4, n_p180 1, n_p180_gathered 4, title_queries
       == [q.format(n=name) for q in commons.SEARCHES], n_title_hits 2, n_gathered
       4, n_kept 2, new == [T1, T2] (sorted-title order; via tags; wd_plan True for
       T1), failed []; every other record: new [], failed [], cat "none" (qid sites:
       qid recorded, n_* 0; no-qid: qid "no qid"); date parseable ISO; re-run
       cover.search -> "0 site(s) to search", file byte-identical (resumable).
   (ii) stdout counts (capture each phase): search "245 site(s) to search" (or the
       measured N) + "2 new file(s)"; stage "2 file(s) staged (2 classified)";
       nopicture "<N-1> item(s) marked" (the box's searched/found/nothing).
   (iii) stage: files.jsonl gained exactly T1/T2 rows: {site: hit, qid, title,
       year 1701/1850, wd_plan True/False, cat, by "212", url/thumb/w/h/mime/date/
       desc/artist/license/page} and NO evidence field (live=False; record()
       no-ops on by:"212" - verified: source_tables() keys are
       "pipeline/sources.py <name>"); classified.jsonl gained the 2 rows (0.9/
       0.1/0.1); local copies data/raw/commons/<hit>/<sha16>.jpg exist, PIL-opens at
       1280x960; plans.json: pre-run (id, sites[0]) key set fully present (pure
       growth), new rows [c_<sha16(Ti)>, "Wikimedia Commons", None, None, name,
       when, [1280,960], None, [hit], cite, "media/commons/<hit>/<sha16>.jpg",
       False, title]; re-run stage -> "nothing new to stage", returns 0, files.jsonl
       + classified.jsonl byte-identical.
   (iv) nopicture: EVERY search-set site except the hit (now in cand via its plans
       row) gets item data/review/<sid>.json (no candidates -> bare name):
       no_picture_found == {searched: _searched_string(record) EXACT, at: ISO};
       spot-check the exact searched string for one qid site (contains "wikidata
       <qid>; no Commons category; P180 depictions of <qid>: 0 of 0 file(s)
       checked; title searches: "<3 queries>" (0 hits); <date>") and one no-qid
       site ("no wikidata item; ..."). The hit site: no item created (none before
       aalsum) or, if one pre-existed, byte-identical; nopicture re-run: same
       count, searched strings unchanged (the at re-stamp is the 201 contract - do
       NOT assert byte-identity of a re-stamped item).
   (v) CHECKOUT INTEGRITY: sha256 every file under the checkout's data/ (skip
       .npy/.npz; data/raw is a symlink - skip), the checkout's web/data/**
       (the per-site subdirs are NOT in my tree - hash what the tree contains:
       web/data top-level files; the sites subdirs are store symlinks the phases
       never touch), docs/ specs/ tests/ - before and after the phases, identical
       (catches any write leaking through a hard link).
5. Costs (measured/estimated): tree ~0.7-1.5 s (incl. the store's data/raw,
   11196 files, hard-linked); fetch fake ~328 x 10 ms + plans export ~1-2 s
   (PIL-opens ~1514+2 local copies); search < 1 s (pure fakes, sleep no-op); stage
   trivial (2 files); **nopicture ~245 upserts x _find_item scanning ~1000 item
   files each (~0.2-0.3 s) ~= 1-2 min - the cost centre, once per session, fine**.
   Then the full suite (`.venv/bin/python -m pytest tests/ -q`); known merge-induced
   reds after 233/234 marking should be GONE (231's case-e pin still mine to fix
   later - it depends on 306c-f settling; 232 waits for 212).

**LIVE RUN (box 4) - later sessions, genuinely waits for 203b (agent c, in flight):**
fetch (1/s paced, resumable; the 328 missing copies now) -> search (real
Commons/Wikidata, resumable via data/cover/searches.json) -> stage --live (evidence
record for the new rows; ask_human ONLY if new files found and clef 127.0.0.1:18083
still down: tunnel, or approve the LLM on 8081 as one-off classifier) -> nopicture
-> commit (searches.json, grown files/classified.jsonl, new raw copies' gitignore
note, item files, re-exported plans.json - record the (id, sites[0]) key-set diff:
lost keys = fetch failures to record, expected pure adds) ->
`sha256sum -c tests/golden/hand_fit_docs.sha256` must pass 40/40. The loop is the
LEAD's (ELoFTR 8091; RoMa 8092 down, skipped; LLM 8081 forbidden for placement);
sync/export are 212b's; report is 212c's. If the live run proves blocked by 203b
when it is time: add 203b to my Depends on line, commit, end (team-mode rule).
