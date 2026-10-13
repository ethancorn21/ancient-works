Status: open
# 212: Cover - the last uncovered sites, the final sync, the report
Depends on: 203a, 203b, 211
Touches: fit/cover.py, data/db/platefits/ (the loop's matcher writes docs; the line check may delete a pattern doc; the sync may stamp by:agent into an unmarked auto doc), data/review/, web/data/review.json, data/commons/files.jsonl, data/commons/classified.jsonl, web/data/plans.json, web/data/sites.json, web/data/sites/, docs/batch.md, tests/test_cover.py

## Goal
The last pass of GOAL.md point 1 and its evidence for the human. For every built site
still without a fit (after the batch, 203a/203b, and the new pictures, 211): a targeted
picture search (the site's QID Commons category, P180 depictions, a title search) with the
search recorded; a found picture becomes a candidate through the normal loop (fitkit sheet ->
model fit -> fit -> gate); a site where nothing is found gets a review item marked "no picture found"
with exactly what was searched. Then the one and only page-facing sync: every fit
document (the 20 hand fits, the automatic ones, the human-saved ones) becomes its site's
overlay and its drawings count in web/data/sites.json, through the existing plan_fit
machinery; web/data/review.json becomes the current open list for the page's review
section (201). Finally docs/batch.md: the report the human reads - counts per outcome,
the seeded 20-sample of automatically accepted fits (a page URL each) for the 18/20
check, and the "no picture found" list.

## Acceptance criteria
- [ ] fit/cover.py runs the targeted search for every built site without a fit and without
      a candidate: the searches (categories, P180 queries, date) are recorded; a found
      picture is staged in the canonical files (files.jsonl + classified.jsonl, with the
      200 evidence field) and its row added to web/data/plans.json; the site goes through
      the normal loop (fitkit sheet -> model fit -> fit -> gate) and ends with an automatic document or a
      review item.
- [ ] A site with nothing found gets a review item marked "no picture found" with exactly
      what was searched (assumption 3 of PLAN.md); the human can drop the site or name a
      source from the item.
- [ ] The page-facing sync (the only task that runs it): every fit document produces its
      site's overlay (web/data/sites/<id>/depictions.json) and its drawings count in
      web/data/sites.json, through the existing plan_fit machinery; the 25 hand fits'
      overlays are unchanged (000's golden test still passes).
- [ ] web/data/review.json is the current open list for the page's review section:
      resolved items out, new items in; the served page shows the right count (checked
      through the page, not the file).
- [ ] docs/batch.md: the final report - counts per outcome (fit: hand / automatic /
      human-saved; review item; no picture found), the seeded 20-sample of automatically
      accepted fits (page URL each, fixed and reproducible from the recorded seed) for
      the human's 18/20 check, and the "no picture found" list with what was searched per
      site.
- [ ] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item (GOAL.md point 1, in full); the
      25 hand fits are intact (the golden test); the sample in docs/batch.md is
      reproducible from the recorded seed.

## Notes
- This task runs last on purpose: it alone writes web/data/review.json, the per-site
  depictions and the drawings counts, so no other in-flight task can collide with it.
- The sync runs plan_fit.main() by hand (the way serve.py's after_write does it in
  production); the tests never start the server's platefits path for this - they check
  the served result.
- The 20-sample must stay a fixed record: the human's 18/20 check (GOAL.md point 3) is
  the project's acceptance, and a moving sample would make it unrepeatable.

## Hand-over

(2026-10-12, iteration 204, agent a - session spent RE-READING every module the test drives
and MEASURING cost centres on a scratch tree; NO test file written yet, NO suite run.
**EXACT NEXT STEP: write tests/test_cover.py** per the design below, run it alone (then the
full suite once it is green), and fix any fit/cover.py bugs it exposes. cover.py is DONE
(863 lines, committed 55678e3) and was verified symbol-by-symbol this session against the
real APIs - all match. The previous session's design survives, corrected in four places
marked CORRECTION - read those first.)

**Branch state (NEW this session):** origin/main moved a858f48 -> **f970500** ("plans.json:
1474 rows (211 pictures + 175 Civitates/Merian full pages fetched locally)" - web/data/
plans.json only). f970500 is NOT in my branch (merge-base still a858f48); I cannot merge
it (the driver does, before the next session). **The test must stay state-aware: every
expectation recomputed from the tree's live files, never from pinned counts - it must pass
on both the 1168-row and the 1474-row plans.json.** All numbers below were measured on the
CURRENT branch tree (1168 rows); recompute, don't pin.

**Measured live state (this session, current branch):** 499 built sites; **120 docs =
21 by:hand + 99 by:agent, 0 unmarked** (all 21 hand docs byte-match
tests/golden/hand_fit_docs.sha256, verified; the golden file = 21 docs + 19
data/sites/*/site.json = 40 lines); 413 no-fit = 359 no-row (search set) + 54 with-row;
search set = 313 qid sites (313 distinct qids) + 46 no-qid; 346 item files (246 carry
no_picture_found); books index 1068 rows, **0 missing the evidence rec field** (so
evidence.record in stage will NOT rewrite the tree's book index - the chg-empty path
holds); files.jsonl 1623 titled rows, 1057 with a local jpg (~566 the fake fetch must
produce); classified.jsonl 930 rows. CHOOSE (first 4 nofit-WITH-row, sorted) =
aesica-q4688554, alauna-q4708853, alesia-q835966, angel-mounds-q4530064 (recompute in
setup). Seed sites (first 3 nofit-no-row, sorted) = aalsum-q3902030, aardenburg-q955,
abbotsbury-castle-q3662453 (all qid-carrying, but EXCLUDED from the search set once they
carry seed docs - _no_fit_sites drops doc'd sites; that is intended). First no-qid
search-set site = aggersborg. **OPEN QUESTION (check first next session):** does aggersborg
(or some no-qid search-set site) have an EXISTING files.jsonl title for the dedupe case?
The failure-site fake returns that existing title (or []) and then raises; if the
designated site has no existing title, pick the first no-qid search-set site that does; a
no-title site just gets [] from the fake search (n_title_hits 0 - still a valid record).
The assertion that the failure site's failed[] is non-empty must survive either choice.

**CORRECTION 1 - the scratch tree CRASHED in export_plans.main: specs/ was missing.**
export_plans reads ROOT/specs/aliases.json (line 70). **The test's tree MUST hard-link
specs/ too** (it is also in the checkout-integrity hash set). My scratch at
/tmp/aw212measure/scratch is probably gone; rebuilding takes 1 s. export_plans.main's total
time is still UNMEASURED - measure it next session before relying on the budget (expect
tens of seconds: commons_rows PIL-opens every local jpg for its size, ~1600-2200 opens
after stage).

**CORRECTION 2 - data/raw, measured and settled:** data/raw IS a symlink to the shared
store /home/agent/projects/ancient-works/data/raw (verified). The test tree: create a REAL
data/raw dir and hard-link the shared store's subdirs (books/, commons/, ...) into it
(reads only); all new writes (data/raw/commons/big/<plan>.jpg stand-ins, staged
<site>/<sha16>.jpg) are new inodes inside the real dir - the shared store is never
touched. test_batch_us re-links data/raw as a symlink, but 212 WRITES there, so do not
copy that behaviour.

**CORRECTION 3 - docs/batch.md and data/cover/ do NOT exist in the checkout** (verified).
So the in-place real-copy set is exactly {web/data/plans.json, data/commons/files.jsonl,
data/commons/classified.jsonl}; docs/batch.md and data/cover/searches.json are NEW files
(new inodes, hard-link-safe). Everything else writes tmp+os.replace (new inode): item
files, review.json, sites.json, depictions.json, docs, searches.json - all safe on hard
links (verified: review._save_json, aw.save_json, batch_us._save_json are os.replace
based).

**CORRECTION 4 - the prune measurement found live drift:** plan_fit.prune on the scratch
tree pruned bethlehem-q2523914 and shotwick-castle-q7502621 (stale overlays of the 3
deleted Bethlehem docs, a858f48). The final sync's prune will do the same in the test
tree: expected, not a failure. Do NOT assert "prune changed nothing".

**Design of tests/test_cover.py (settled last session, corrections above incorporated):**
1. OWN module-scoped tree + OWN server (NOT conftest's session `served` - 7 other test
   files pin it, my 8-phase run would mutate it). Tree: hard-link every file of web/
   data/ docs/ specs/ (1 s, metadata only - even the 1.6G .npy); real copies ONLY for the
   in-place set (CORRECTION 3); data/raw = real dir + hard-linked shared-store subdirs
   (CORRECTION 2); copy server/ into the tree. Server: Popen [sys.executable,
   "server/serve.py", "--port", "0"] cwd=tree (venv python); parse "Ancient Works on
   (\S+)" from stdout (conftest's pattern); the server is a SEPARATE process, so the
   in-test time.sleep patch does not affect it; terminate+kill in teardown.
   tmp_path_retention_policy "failed" (already in pytest.ini). Seed stand-ins in setup:
   (a) data/raw/commons/big/<plan>.jpg for EVERY commons-src doc that will be built
   (simplest: seed for all commons-src docs, size = doc.get("size") or the crop max,
   solid-colour PIL jpg, EXCLUDING the deliberate bad-commons seed doc); (b) staged files
   get their jpg from the fake _fetch_one (fixed 1280x960 - plans size comes from it; no
   build ever uses them). Book docs read data/raw/books/<ia>/full/<file> from the
   hard-linked shared store; PRECONDITION: every book doc that will build has its file
   present in the shared store (assert in setup).
2. Seeded docs before the phases on the 3 seed sites (aalsum/aardenburg/abbotsbury):
   (a) UNMARKED-AUTO (auto:True, no by, src commons, non-pattern pairs) -> stamped
   by:agent + built; (b) NO-PROVENANCE (no by, no auto, src commons) -> refused, doc
   kept, item entry why == plan_fit.NO_PROVENANCE, site stays drawings 0 + open item;
   (c) BAD-COMMONS (by:agent, no fitter, src commons, big stand-in deliberately absent)
   -> line check passes, build dies on the dead socket, cover.sync's `except Exception`
   catches -> item entry "sync failed: ...", doc kept, sweep goes on.
   CHOOSE = first 4 nofit-WITH-row (sorted, recomputed): the FAKE matchfit.run(root,
   site_ids) writes a matcher doc (batch_us.write_doc + fitter:"matcher") for the
   site's first candidate row: CHOOSE[0..2] = well-spread non-grid-round pairs, score
   25.0 (built); CHOOSE[3] = near-collinear (spread guard trips at sync -> "sent": doc
   deleted, item "matcher points nearly on a line"). PRECONDITION-VERIFY in setup:
   plan_fit.fabrication_pattern(confident pairs) is None and matchfit.spread(
   near-collinear) trips (ratio < 0.1 or sd < 20) - fail loudly if the real functions
   drifted. Non-pattern recipe: 4 anchors, coords off the 10-px grid (x.3/x.7 style),
   3+ distinct u and v with gap ratios outside [0.67, 1.3], no 3+ sharing one coord
   within 2px.
3. Recorded network world (monkeypatch.setattr on the shared module objects -
   cover/site_done/batch_us/evidence import the SAME module instances; import site_done
   the way cover does: sys.path.insert fit/ + pipeline/ + tools/): autouse no_network
   (socket.socket.connect AND socket.create_connection -> AssertionError);
   cover.time.sleep -> no-op (NOTE: cover.time IS the global time module - the patch is
   process-wide during the test; my own fixture wait loops use time.time() so that is
   fine); cover._fetch_one -> write stand-in jpg to dst, return True, record (url, dst);
   commons.wd_claims -> {qid: {cat, plan: [new claims title], image: []}};
   commons.files_of -> [one new cat-file title]; commons.search(name) -> the site's one
   EXISTING files.jsonl title (dedupe) or [] (no-qid sites) - RAISES for the designated
   failure site; commons.info -> keep-passing metadata for NEW-pool titles ("(c. 1701)"/
   "(c. 1850)" in the title, mime image/jpeg, date/desc free of the NO regex -
   PRECONDITION: assert commons.keep(title, meta) for every fake title) and default
   keep-passing metadata otherwise; evidence.fetch_page_ids -> {t: 1000+i};
   evidence.fetch_file_entities -> {t: {"item": "M<id>", "p180": [site's qid]}} (the
   fake keeps a title->qid map built from wd_claims); matchfit.reachable -> True;
   matchfit.run -> the CHOOSE writer, returns [paths]. New pool: 2 files per
   qid-carrying search-set site, 0 for no-qid -> ~626 new files (recompute; the fakes
   are pure functions of their inputs so they stay consistent across calls).
4. Drive in-process on the tree: cover.fetch -> search -> stage(classifier=lambda
   rows: aligned fake {p_plan: 0.8, p_birdseye: 0.1, p_photo: 0.1} - passes the plans
   thresholds p_photo<0.5, max(p_plan,p_birdseye)>=0.3) -> loop() -> nopicture -> sync
   -> export -> report. NOTE: cover._regen_plans re-points export_plans.ROOT/BOOKS and
   commons.OUT/RAW itself (no extra monkeypatching needed); the tree must contain
   specs/ (CORRECTION 1) plus data/catalog and data/books (export_plans reads both).
5. Assertions (ALL state-aware):
   (i) searches.json: one record per search-set site (recomputed); fields incl.
   title_queries == [q.format(n=name) for q in commons.SEARCHES], failed (failure site
   non-empty), date; union of records' new == by:"212" files.jsonl rows ==
   classified.jsonl rows (fake p values) == the new local jpgs.
   (ii) plans.json grew vs pre-run; every by:212 title has a row (c_<sha16>, sites
   [site]); (id, sites[0]) unique (the test_data contract - re-check because I add rows).
   (iii) CHOOSE outcomes as in 2.; other with-row nofit sites: open item with "no model
   answer" entries for their candidates.
   (iv) sync: golden 40 files byte-identical tree-vs-checkout (box 3; 20/21 hand docs
   are is_done - the maiden-castle-q1232816.c_c20ff6b1f16d173d overlay rebuilds, the
   golden FILES stay put; do NOT require all-golden is_done as a precondition); seed
   outcomes as in 2.; no pattern doc left built.
   (v) THROUGH THE SERVED PAGE (port 0, http only): GET / -> 200 "Ancient Works"; GET
   /data/review.json -> items equal the open items recomputed from the tree's item
   files with review.resolved_doc, same fields and order (also GET /index.html and
   /review.js -> 200); GET /data/sites.json -> for EVERY built site: drawings >= 1 OR
   its item is in the served open list (box 6 = GOAL point 1 in full); golden sites
   drawings >= 1.
   (vi) report: docs/batch.md (tree) - sample rows == random.Random(20261012).sample(
   sorted auto-doc ids, min(20, n)) recomputed from the tree's FINAL docs (auto =
   plan_fit.who_placed == "agent"); seed line names 20261012; each row's page ==
   "#<site>", gate == the doc's score; the no-picture table == the served open
   no_picture items (same searched strings, same order); the counts section == the
   buckets recomputed from the tree (independent of cover.report's code); re-run
   cover.report(tree) -> the sample section byte-identical (fixed & reproducible - the
   human's 18/20 check).
   (vii) CHECKOUT INTEGRITY: sha256 every file under the checkout's data/ (skip .npy/
   .npz; data/raw is a symlink, skip it) + web/data/** + docs/ + specs/ + tests/ before
   and after the phases; they must be identical (catches any write leaking through a
   hard link or the data/raw symlink - the web/data/sites 179MB hash is ~10 s).
6. Suite: run `.venv/bin/python -m pytest tests/ -q` (NEVER bare pytest - system python
   has no numpy/PIL) AFTER test_cover.py is green - one combined run covers both
   (last known green 150 passed/1 skipped at 9590abf; branch drift since = driver files
   only). If the combined run outruns ~10 min, run my test alone this session and the
   full suite next.

**Cost measurements this session (scratch tree, venv python):** hard-link web/ + data/
= **1 s**; _find_item (346 items) 5 ms; scoped review.export 0.34 s; full export 0.32 s;
set_drawings 0.04 s; plan_fit.prune (full) 0.14 s; site_done.main per nofit site
(matcher down, items pre-existing) 0.42-0.46 s -> **the 413-site loop phase is the cost
centre: expect ~3 min** (plus run_sites + propose where new candidates exist -
propose.propose_for is called WITHOUT root: checkout reads, safe; it re-parses the
checkout's plans.json per candidate); build of a commons doc (stand-in) 1.2-2.2 s x ~25
builds ~ 1 min; export_plans.main UNMEASURED (crashed, CORRECTION 1). Total expected
~5-6 min - inside the ~10 min budget.

**Then (after the test is green):** the WORKING run on the live tree (network allowed):
fetch -> search -> stage (ask_human ONLY if new files found and clef still down: tunnel
or approve the LLM as one-off classifier - clef 18083 is down here and the tunnel cannot
be opened: aibox unresolvable, ~/.ssh keys forced-command) -> loop (ELoFTR
127.0.0.1:8091 UP - the real matcher places; RoMa 8092 down, skipped by design; LLM 8081
FORBIDDEN for placement, the lead) -> nopicture -> sync (check
`ls data/raw/commons/big | wc -l` first - the big-jpg cache decides download cost) ->
export -> report -> commit everything (grown files.jsonl/classified.jsonl/plans.json,
review items, review.json, sites.json, overlays, docs/batch.md); finish with
`sha256sum -c tests/golden/hand_fit_docs.sha256` (must pass 40/40) and the suite green.

**Known traps (keep in the test's docstring):** propose.propose_for is called by
batch_us.run_sites WITHOUT root -> checkout reads (safe; the optional proposal field is
not pinned by the test); evidence.record live=False records NO evidence field for
by:"212" rows (record_commons_row only hand-ties names in source_tables()) - assert
staged rows' shape but NOT an evidence field (the 200 field comes in the live run via
record_live); fit/evidence.py is NOT in my Touches - drive it through evidence.record
only; upsert_item(entries non-empty) CLEARS no_picture_found - staged sites that gain
candidates lose the no-picture mark before the nopicture phase runs (intended);
review.export scoped (site_id) records resolved only into that site's item file (the
loop calls it per site - 413 scoped exports are part of the cost centre); the 3 seed
sites keep their pre-existing no_picture items even with a doc (an item with no
candidates never resolves - the report's "a fitted site can also carry an item" bucket).

**Do NOT touch:** requirements.in/.txt (302a/304 hold them), tests/conftest.py, and the
modules I only call (tools/site_done.py, fit/batch_us.py, fit/matchfit.py,
fit/review.py, pipeline/plan_fit.py, pipeline/commons.py, tools/export_plans.py,
server/serve.py, fit/evidence.py): if one needs a hook to make a phase testable,
monkeypatch in MY test or file a new task - never edit it in passing. My Touches already
cover data/db/platefits/, data/review/, web/data/review.json, web/data/plans.json,
web/data/sites.json, web/data/sites/, data/commons/files.jsonl,
data/commons/classified.jsonl, docs/batch.md, fit/cover.py, tests/test_cover.py.
data/cover/ (searches.json) is a new 212 output dir - add it to Touches if the driver's
file check complains. data/raw/ is the gitignored shared store (no Touches needed).

### Lead note (2026-10-12, after 211) - the lead's steering, read before design (verbatim from ef84a05)
- The fit in this task's loop is the MATCHER, not a vision-model fit: tools/site_done.py already runs
  fit/matchfit.py first on every picture without a document whenever the matcher answers (ELoFTR on
  127.0.0.1:8091 is reachable from this VM; RoMa on 8092 is not, and site_done works without it).
  The vision-model batch fit invented its points (301) and must not place anything. An unsure matcher
  result goes to the review item, as site_done already does.
- 211's new pictures are in the canonical files but most have no local copy, so they are not in
  web/data/plans.json yet (still 1168 rows on main): `python pipeline/commons.py thumbs` fetches rows
  with a `thumb`; the Limes rows carry only a full-file `url` (upload.wikimedia.org) - fetch those too
  (the original, or a standard thumbnail width), then `tools/export_plans.py`. The lead did this on the
  owner's Mac (1168 -> 1296 rows, plus the Civitates/Merian full pages); data/raw is gitignored, so
  this checkout needs its own copies.
