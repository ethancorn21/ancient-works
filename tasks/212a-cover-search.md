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

(2026-10-13, iteration 216, agent a - investigation + verification session; NO test
file written yet, session hit the context limit after the 233/234 verification and the
live-state re-measurement. **EXACT NEXT STEP: (1) mark tasks/233 + tasks/234
Status: done, all boxes ticked (lead's instruction, verified this session - evidence
below); (2) write tests/test_cover.py per the settled 212a design below; (3) run it
alone, fix, run the full suite; (4) the live run (box 4) is a LATER session and waits
for 203b - see end.**)}

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
