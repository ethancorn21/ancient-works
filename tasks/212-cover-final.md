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

(2026-10-12, iteration 205, agent a - investigation session: every API the test drives was
re-verified against the real code; the open question (no-qid failure site) is RESOLVED;
ONE design correction found (seed docs (b)/(c) must move to FAKE sites, CORRECTION 5);
export_plans.main MEASURED at 0.65 s (not the cost centre). NO test file written, NO suite
run. **EXACT NEXT STEP: (1) run the one blocked measurement (bethlehem/shotwick coverage
after the sync's prune - it decides a box-6 edge case; command in CORRECTION 4);
(2) write tests/test_cover.py per the settled design; (3) run it alone
(`.venv/bin/python -m pytest tests/test_cover.py -q`), fix what it exposes, then the full
suite.** cover.py is DONE (863 lines, committed 55678e3) and re-verified symbol-by-symbol
this session - all match the design.)

**Branch state:** HEAD f070d75 (driver files only above a858f48); merge-base with
origin/main is still a858f48. origin/main = **f970500** ("plans.json: 1474 rows (211
pictures + 175 Civitates/Merian full pages fetched locally)" - web/data/plans.json only,
verified `git diff --stat a858f48 f970500`). The driver merges it into my branch before
the next session; I cannot merge it now. **The test stays state-aware: every expectation
recomputed from the tree's live files, never pinned counts - it must pass on both the
1168-row (my branch) and the 1474-row (main) plans.json.** plans.json is a single-line
JSON dict {"cols":[id,book,ia,file,title,label,size,map_box,sites,cite,url,view,ref],
"rows":[...]}; my branch: 1168 rows.

**Measured live state (this session, current branch tree):** 499 built sites; 120 docs =
21 by:hand + 99 by:agent + 0 unmarked (all 21 hand docs byte-match
tests/golden/hand_fit_docs.sha256; the golden file = 21 platefits docs + 19
data/sites/*/site.json = 40 lines - the 19 site.json are in data/sites/ (the per-site
data dir; web/data/sites/<id> is a SYMLINK into the shared store /home/agent/projects/
ancient-works/web/data/sites/, which is a real dir there)). 413 nofit = 359 no-row
(search set) + 54 with-row. Search set = 313 qid sites + 46 no-qid. files.jsonl 1623
rows (1514 titled; ALL 1514 + all 1068 books-index rows carry the evidence rec field ->
evidence.record in stage rewrites NOTHING); classified.jsonl 930 rows.
**CHOOSE** (first 4 with-row nofit, sorted) = aesica-q4688554 (1 row, commons
c_e28ed261168b49c9), alauna-q4708853 (5 rows; FIRST is BOOK
earthworkenglan01allcgoog_n0438_1, then 4 commons), alesia-q835966 (3 rows, first
commons c_58e0eb394bdd9f1a), angel-mounds-q4530064 (2 BOOK rows, first
annualreportofbu1218901891smit_n0701_1). Both needed book files EXIST in the shared store
(verified). So the matcher-fake's doc: aesica/alesia = commons (big stand-in required),
alauna/angel-mounds = book (shared-store file, hard-linked in the tree; angel-mounds'
n0701 is never built - it is the near-collinear "sent" doc, deleted at sync). Expected
end states: aesica covered no item (its only row becomes the doc); alauna doc built +
open item with its 4 other candidates; alesia doc built + open item with 2;
angel-mounds doc sent+deleted (spread guard) + open item with n0702 ("no model answer").
Seed site for (a) = first nofit-no-row, sorted = aalsum-q3902030 (recompute).
**Open question RESOLVED:** the no-qid search-set sites with an existing files.jsonl
title are exactly 5: burford-house-windsor, kastell-buch, kastell-schirenhof,
kings-weston-house, stoke-house (aggersborg has none). **Designated failure site =
burford-house-windsor** (first, sorted): the fake commons.search RAISES for it (its
record gets failed non-empty, n_title_hits 0, new []). Other no-qid sites' fake search
returns their existing titles (dedupe) or []; qid sites' fake search returns their
existing title (dedupe) PLUS their 2 new-pool titles.

**CORRECTION 1 - the scratch tree needs specs/ (and the in-place set):**
export_plans.main reads ROOT/specs/aliases.json, data/books/{index,matches}.jsonl,
data/catalog/sites.jsonl, and writes web/data/plans.json with **json.dump(open(dst,"w"))
- an IN-PLACE write** (that is why plans.json is in the real-copy set). **MEASURED:
export_plans.main on the completed scratch tree = 0.65 s** (all local copies present;
PIL-opens every commons row with a local jpg) - NOT the cost centre. Scratch at
/tmp/aw212measure/scratch now has web/ data/ docs/ specs/ tests/ hard-linked, real copies
of plans.json/files.jsonl/classified.jsonl; it is missing nothing else, so it can be
reused for the next measurement.

**CORRECTION 2 - data/raw:** the checkout's data/raw is a symlink to the shared store
/home/agent/projects/ancient-works/data/raw. The test tree: a REAL data/raw dir whose
subdirs (books/, commons/, aerial/, ...) are hard-linked from the shared store (reads
only); all new writes (the big/ stand-ins, staged jpgs) are new inodes inside the real
dir - the shared store is never touched. (test_batch_us re-links data/raw as a symlink;
212 WRITES there, so do not copy that.)

**CORRECTION 3 - in-place real-copy set = EXACTLY {web/data/plans.json,
data/commons/files.jsonl, data/commons/classified.jsonl}** (all three are written in
place: export_plans json.dump open("w"); stage open("a") twice). Everything else in the
product writes tmp+os.replace (verified this session: review._save_json, aw.save_json,
batch_us._save_json, **evidence.rewrite is ALSO tmp+os.replace** - my earlier worry
about it was unfounded). docs/batch.md and data/cover/searches.json are NEW files (new
inodes). web/data/sites/<id> is a symlink in the checkout; the hard-link builder must
FOLLOW it (os.path.realpath) and create a REAL per-site dir in the tree - then any
delete (prune's os.remove of a webp) or replace lands in the tree only.

**CORRECTION 4 - the sync's prune drops stale live overlays (bethlehem/shotwick) -
MEASURE THAT BEFORE WRITING THE TEST.** The previous session found plan_fit.prune on
the scratch prunes bethlehem-q2523914 and shotwick-castle-q7502621 (stale overlays of
docs deleted by a858f48). The sync phase's final full prune will do the same in the
tree, resetting those sites' drawings to 0. THE RISK (not yet measured - the context
limit cut the session before this ran): if either site ends with drawings 0, NO doc and
NO open item, box 6 ("every built site: drawings >= 1 or an open review item") fails.
They are excluded from the search/loop/nopicture sets (drawings > 0 until the prune),
so only a PRE-EXISTING item or the loop's earlier processing can cover them. **Run
first:**
```
cd <checkout> && python3 - <<'EOF'
import json, os
smap={s['id']:s for s in json.load(open('web/data/sites.json'))['sites']}
d=json.load(open('web/data/plans.json'))
cols={c:i for i,c in enumerate(d['cols'])}
rows=[{k:r[i] for k,i in cols.items()} for r in d['rows']]
for sid in ("bethlehem-q2523914","shotwick-castle-q7502621"):
    s=smap[sid]
    rws=[r['id'] for r in rows if sid in (r.get('sites') or [])]
    it=None; itfile=None
    for p in os.listdir('data/review'):
        if p.endswith('.json'):
            i=json.loads(open(os.path.join('data/review',p)).read())
            if i.get('site')==sid: it, itfile = i, p; break
    docs=[p for p in os.listdir('data/db/platefits') if p.startswith(sid+'.')]
    dep=os.path.realpath(os.path.join('web/data/sites',sid,'depictions.json'))
    ndep=len(json.load(open(dep))['depictions']) if os.path.exists(dep) else -1
    print(sid, "| drawings:", s.get('drawings'), "| qid:", s.get('qid'), "| rows:", rws,
          "| item:", itfile, "| cands:", len((it or {}).get('candidates') or []),
          "| no_picture:", bool((it or {}).get('no_picture_found')), "| resolved:",
          (it or {}).get('resolved'), "| docs:", docs, "| dep entries:", ndep)
EOF
```
If a site is left uncovered by the prune: that is a genuine 212 finding (the sync's
prune can uncover a site the batch left covered) - record it in DECISIONS and add the
site's item via the nopicture-phase convention (a no_picture re-record with the search
record if it has one, else the batch's generic one) - decide from the measured numbers,
and note in the test docstring that the test then expects it.

**CORRECTION 5 (NEW THIS SESSION) - seeds (b) and (c) must live on FAKE sites, not real
ones.** 201's derived resolution (pinned end-to-end by tests/test_fit_provenance.py
cases b/c, re-read this session): an item RESOLVES when any of its candidates has a doc
in the store - the doc's build status is irrelevant. (b) NO-PROVENANCE: _sync_doc
upserts a candidate with the refused doc's plan; the doc is KEPT -> item resolved, OFF
the open list (the previous hand-over's "site stays drawings 0 + open item" is WRONG).
(c) BAD-COMMONS: _fail_entry upserts a candidate with the failed doc's plan; the doc is
kept -> resolved, off the open list. On a REAL built site either seed therefore breaks
box 6 (drawings 0, no open item) and the report's bucketing ((c) would count as
"fit: automatic" because who_placed(doc)=agent even though nothing was built; (b) as
"uncovered (needs attention)"). So: **(a) UNMARKED-AUTO stays on ONE real seed site**
(first nofit-no-row, sorted = aalsum-q3902030, recompute) - stamped by:agent then BUILT
(drawings 1, covered; its pre-existing no_picture item, if any, stays open - no
candidate is upserted on a successful build) - and **(b)/(c) move to FAKE site ids not
in sites.json** (e.g. "cover-fake-unmarked-q0", "cover-fake-fail-q0"): cover.sync
iterates _all_docs and calls site_done._sync_doc(root, sid, plan, doc) directly - no
_site_built check - so the sweep reaches them. (b) needs no site dir (refused before
any build); its item (new file data/review/<fake>.<plan>.json) resolves via 201's
derivation. (c) needs a web/data/sites/<fake>/ dir with a bare depictions.json AND a
commons-src doc whose big stand-in is deliberately ABSENT: build -> load_picture ->
cache missing -> _fetch (4 retries; time.sleep is patched to a no-op, so they are
instant) -> the socket guard raises -> AssertionError (NOT a SystemExit) escapes
_sync_doc -> cover.sync's `except Exception` -> _fail_entry upsert + "sync failed"
record, sweep goes on. GOTCHA: a build that raises SystemExit (e.g. missing site dir)
makes _sync_doc RETURN ("failed", msg) - cover.sync does NOT upsert on that path - so
(c) must fail on the network, with the site dir present. Both fake items are resolved
(off the page) and the fake sites are not in sites.json -> not report-bucketed -> the
box-6 invariant over BUILT sites is untouched. The report's doc counts DO include the
fake docs (n_auto) - recompute state-aware.

**Design of tests/test_cover.py (settled; corrections 1-5 incorporated):**
1. OWN module-scoped tree + OWN server (NOT conftest's session `served` - 7 other test
   files pin it; my run mutates it). Tree under tmp_path_factory.mktemp: hard-link
   every file of web/ data/ docs/ specs/ tests/ (follow symlinks via realpath; skip
   .npy/.npz; skip data/raw; ~1 s), real data/raw + hard-linked shared-store subdirs,
   REAL COPIES of the 3 in-place files (correction 3), shutil.copytree(ROOT/server)
   (NO pipeline/fit/tools in the tree - the server's fit worker dies on import by
   design, proven in test_fit_provenance d; all in-process code runs from the
   CHECKOUT's modules). Seed stand-ins: data/raw/commons/big/<plan>.jpg for EVERY
   commons-src doc in the store EXCEPT (c)'s fake doc (solid-colour PIL jpg at the
   doc's size), PLUS the two CHOOSE commons plans (aesica c_e28ed261168b49c9, alesia
   c_58e0eb394bdd9f1a - plan = the plans row id; size = the row's size). Server:
   Popen [venv python, "server/serve.py", "--port", "0"] cwd=tree; parse "Ancient
   Works on (\S+)" from stdout; start it AFTER the phases (right before the page
   checks); terminate+kill in teardown. Run with `.venv/bin/python -m pytest` (never
   bare pytest - system python has no numpy/PIL; .venv exists in this checkout).
   PRECONDITIONS in setup (fail loudly): golden 40 files byte-match; every agent doc
   passes its own check (fitter==matcher -> matchfit.spread(pairs) ratio >= 0.1 and
   sd >= 20.0; else fabrication_pattern(pairs) is None); every book-src doc has its
   shared-store file; every fake title passes commons.keep; the 5 no-qid-with-title
   sites match the measurement.
2. Seed docs: (a) on the real seed site: {site, plan "c_a122212221222121" (new, no
   collision), src commons, ref/url fake, size [1280,960], crop [0,0,1280,960], at
   fixed, auto: True, NO by, score 25.0, pairs = well-spread non-pattern 4 anchors};
   (b) fake site: same shape minus auto (NO by, NO auto); (c) fake site: by:"agent",
   NO fitter, size [1280,960], big stand-in ABSENT. Non-pattern recipe (validated set
   from test_fit_provenance: [[13.4,22.6],[27.9,55.1],[88.2,60.8],[121.7,134.3]] -
   fabrication_pattern None; verify spread also passes for (a); near-collinear for
   CHOOSE[3]: e.g. [[100.3,5.1],[130.7,7.9],[161.2,10.7],[191.6,13.5]] - verify
   ratio < 0.1 or sd < 20).
3. Fakes (monkeypatch.setattr on the SHARED module objects - cover/site_done/batch_us/
   review/plan_fit/evidence/commons/matchfit all share one instance each): autouse
   no_network (socket.socket.connect AND socket.create_connection -> AssertionError);
   cover.time.sleep -> no-op (that IS the global time module - my server wait loop
   must poll on time.time(), not sleep); cover._fetch_one -> write stand-in 1280x960
   jpg to dst, record (url, dst), True; commons.wd_claims -> {qid: {cat, plan:[T1
   bare], image:[]}} for every search-set qid (T1 = "Plan of <Name> (c. 1701).jpg",
   T2 = "View of <Name> (c. 1850).jpg" - 2 per site, name-embedded, unique, NO-regex
   clean); commons.files_of(cat) -> ["File:"+T2]; commons.search(name) -> raises for
   burford-house-windsor, else existing title(s) + (T1,T2 for qid sites); commons.info
   -> keep-passing meta for EVERY title (new pool: date "", desc "", mime
   image/jpeg, url + thumb fake, w/h 1280/960; existing titles: any keep-passing
   meta); evidence.fetch_page_ids -> {t: 1000+i}; evidence.fetch_file_entities ->
   {t: {"item":"M<id>", "p180":[qid]}} for T1 only (others get [] or no entry);
   matchfit.reachable -> True; matchfit.run(root, site_ids) -> for each CHOOSE site
   in the list: batch_us.write_doc(root, sid, first candidate row, pairs, 25.0) then
   set fitter:"matcher" in the written doc (re-save with batch_us._save_json) and
   append path; return paths (non-CHOOSE: []). The world is computed ONCE in setup
   from the tree's live state (search set, CHOOSE, existing titles) and the fakes
   stay pure functions of their inputs.
4. Drive in-process (each takes the tree root): cover.fetch -> cover.search ->
   cover.stage(classifier=fake aligned {p_plan:.8, p_birdseye:.1, p_photo:.1},
   live=False) -> cover.loop() -> cover.nopicture -> cover.sync -> cover.export ->
   cover.report(at="2026-10-12T00:00:00+00:00"). cover._regen_plans re-points
   export_plans.ROOT/BOOKS and commons.OUT/RAW itself. The tree needs specs/,
   data/books, data/catalog (all hard-linked).
5. Assertions (ALL state-aware - recomputed from the tree's live files):
   (i) data/cover/searches.json: one record per search-set site (recomputed
   pre-run); fields: qid ("no qid" for 46), cat, n_cat_files (1 qid / 0 no-qid),
   n_p180 (1 qid), n_p180_gathered (2 + has-existing-title), title_queries ==
   [q.format(n=name) for q in commons.SEARCHES], n_title_hits (0 failure site, else
   1+2 or existing-only), n_kept, new (2 per qid site, 0 no-qid; union of new == by:
   "212" files.jsonl rows == new classified rows == new local jpgs), failed
   (burford non-empty, all others empty), date; records resumable (re-run search ->
   same file, no new).
   (ii) plans.json grew vs pre-run; every by:212 title has a row (c_<sha16>, sites
   [site], size [1280,960]); (id, sites[0]) unique (the test_data contract - I add
   rows); pre-existing rows keep their ids.
   (iii) CHOOSE outcomes as measured (aesica doc+built, no item; alauna/alesia
   doc+built + open item with the other candidates "no model answer"; angel-mounds:
   NO doc, item candidate why "line check: matcher points nearly on a line..." -
   recompute the exact string from matchfit.spread at runtime). Other with-row nofit
   sites: open item, every candidate "no model answer".
   (iv) sync results dict: (a) stamped (doc bytes == {**seed, "by":"agent"}, key last,
   indent=1, no trailing newline) + "synced"; (b) "refused", doc byte-identical, item
   why == plan_fit.NO_PROVENANCE, item resolved == that doc; (c) "failed", item why
   startswith "sync failed:", doc kept, sweep continued (later docs still synced);
   20/21 hand docs "skipped" (is_done), the 1 stale one "synced" (maiden-castle
   c_c20ff6b1f16d173d - recompute which golden hand doc is not is_done);
   agent docs: "skipped" or "synced" (CHOOSE's); NO "sent" among pre-existing agent
   docs (precondition 1); the 40 golden files byte-identical tree-vs-checkout (21
   docs + 19 site.json); prune dropped the bethlehem/shotwick stale overlays
   (per correction 4's measurement).
   (v) THROUGH THE SERVED PAGE (port 0, GET only): / -> 200 "Ancient Works";
   /data/review.json -> items == the open items recomputed from the tree's item files
   with review.resolved_doc, same fields and name order; /data/sites.json -> for
   EVERY built site: drawings >= 1 OR its item in the served open list (box 6 = GOAL
   point 1 in full); golden sites drawings >= 1; /index.html and /review.js -> 200.
   (vi) docs/batch.md (tree): sample rows == random.Random(20261012).sample(sorted
   auto-doc ids, min(20,n)) recomputed from the tree's FINAL docs (auto =
   plan_fit.who_placed == "agent"); the seed line says 20261012; each row's page ==
   "#<site>", gate == the doc's score; no-picture table == the served open
   no_picture items (same searched strings, same order); counts section == the
   buckets recomputed independently from the tree (built sites: hand-golden /
   hand-saved / automatic / review item / no picture found / uncovered); re-run
   cover.report(at=...) -> the file BYTE-IDENTICAL (fixed & reproducible - the
   human's 18/20 check).
   (vii) CHECKOUT INTEGRITY: sha256 every file under the checkout's data/ (skip
   .npy/.npz; data/raw is a symlink - skip) + web/data/** + docs/ + specs/ + tests/
   before and after the phases; identical (catches any write leaking through a hard
   link or the data/raw symlink; web/data/sites ~179 MB, ~10 s).
6. Suite: run the full `.venv/bin/python -m pytest tests/ -q` AFTER test_cover.py is
   green in a combined run (last known green 150 passed/1 skipped at 9590abf; branch
   drift since = driver files only). If the combined run outruns ~10 min, run my test
   alone this session and the full suite next.

**Cost measurements (venv python):** hard-link tree ~1 s (239 files specs/docs/tests +
web/data previously measured 1 s); export_plans.main **0.65 s**; scoped review.export
0.34 s, full 0.32 s; set_drawings 0.04 s; prune (full) 0.14 s; site_done.main per
nofit site (matcher fake, no model) 0.42-0.46 s -> **the 413-site loop is the cost
centre, expect ~3 min** (it includes 413 scoped exports, _find_item scans of ~1000
item files, set_drawings each); fetch stand-in writes ~566-1200 x ~10 ms; stage
evidence.record scans both jsonl files (fast, no rewrites - 0 missing rec). Total
expected ~5-6 min for the whole test - inside the ~10 min budget; if it is not, the
loop is where the time goes (do not try to shrink the site set: the test must cover
all 413).

**Then (after the test is green):** the WORKING run on the live tree (network
allowed): fetch -> search -> stage (ask_human ONLY if new files found and clef still
down: tunnel or approve the LLM on 8081 as one-off classifier - clef 127.0.0.1:18083
is down here and the tunnel cannot be opened: aibox unresolvable, ~/.ssh keys are
forced-command) -> loop (ELoFTR 127.0.0.1:8091 UP - the real matcher places; RoMa
8092 down, skipped by design; LLM 8081 FORBIDDEN for placement, the lead) ->
nopicture -> sync (check `ls data/raw/commons/big | wc -l` first - the big-jpg cache
decides download cost) -> export -> report -> commit everything (grown
files.jsonl/classified.jsonl/plans.json, review items, review.json, sites.json,
overlays, docs/batch.md); finish with `sha256sum -c tests/golden/hand_fit_docs.sha256`
(must pass 40/40) and the suite green.

**Known traps (keep in the test's docstring):** the (b)/(c) fake sites' items RESOLVE
(201's derived resolution - correction 5) and leave the open list: that is the pinned
product contract, not a bug; _sync_doc RETURNS ("failed", msg) for a SystemExit build
failure (cover.sync does not upsert on that path) - only a RAISED exception (the dead
network) reaches cover.sync's containment; evidence.record live=False records NO
evidence field for by:"212" rows (record_commons_row only hand-ties names in
source_tables(); "212" is not one - verified) and rewrites nothing (0 rows missing
rec - measured); upsert_item(entries non-empty) CLEARS no_picture_found - staged
sites that gain candidates lose the no-picture mark before the nopicture phase runs
(intended; nopicture then skips them: they are in cand); review.export scoped (site_id)
records resolution only into that site's item file (the loop calls it per site - 413
scoped exports are part of the cost centre); a fitted site can also carry an item
(the seed site's pre-existing no_picture item stays open - the report's "a fitted
site can also carry an item" note); propose.propose_for is called by batch_us.run_sites
WITHOUT root -> checkout reads (safe; the optional proposal field is not pinned);
patching cover.time.sleep patches the GLOBAL time module for the test's duration -
wait loops must poll time.time().

**Do NOT touch:** requirements.in/.txt (302a/304 hold them), tests/conftest.py, and the
modules I only call (tools/site_done.py, fit/batch_us.py, fit/matchfit.py,
fit/review.py, pipeline/plan_fit.py, pipeline/commons.py, tools/export_plans.py,
server/serve.py, fit/evidence.py, fit/propose.py, pipeline/build_site.py): if one
needs a hook to make a phase testable, monkeypatch in MY test or file a new task -
never edit it in passing. My Touches already cover data/db/platefits/, data/review/,
web/data/review.json, web/data/plans.json, web/data/sites.json, web/data/sites/,
data/commons/files.jsonl, data/commons/classified.jsonl, docs/batch.md, fit/cover.py,
tests/test_cover.py. data/cover/ (searches.json) is a new 212 output dir - add it to
Touches if the driver's file check complains. data/raw/ is the gitignored shared
store (no Touches needed).

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
