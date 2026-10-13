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

(2026-10-12, iteration 201, agent a - SYNCED main per the lead: merged origin/main (a858f48, the Bethlehem doc
removals) + the lead note ef84a05 into this branch (merge commits 906b332 + 1e016af; conflict in this file
resolved by keeping the hand-over and folding the lead note in verbatim at the end). Re-measured the live
tree. **The fit/cover.py design is now settled in DECISIONS.md (three 2026-10-12 212 entries: the design,
the matcher-as-fit decision, the fetch/clef availability decision) - no code written yet.** Next session
WRITES fit/cover.py from that design.)

**Live state after the sync (measured this session - the numbers to work from):**
- data/db/platefits: **120 docs = 21 by:hand (all 21 byte-identical to tests/golden/hand_fit_docs.sha256,
  verified this session) + 99 by:agent** (3 Bethlehem agent docs deleted by the line, a858f48; no unmarked
  docs). The golden 40-line sha256 file (21 docs + 19 site.json) must stay byte-identical; verify with
  `sha256sum -c tests/golden/hand_fit_docs.sha256` after every live run.
- web/data/sites.json: **499** built sites. Covered (drawings >= 1 or a doc): **86** (83 have a doc).
  No fit: 413. No fit AND no plans.json candidate: **359** (this set SHRINKS once phase 1 fetches the
  131 classified rows - recompute it after the fetch, do not pin it).
- web/data/plans.json: **1168** rows (574 with non-empty sites). The lead's Mac run got 1296: the gap is
  exactly the 131 classified rows with no local copy (all meet the thresholds, none in plans yet).
- data/review: **346** item files (246 carry no_picture_found). web/data/review.json: at=2026-10-12T18:34:20,
  333 open (the Mac's export; my phase 6 rewrites it).
- Local-copy gap (the lead's second point): files.jsonl 1623 titled rows = 1457 with `thumb` (1056 have a
  local jpg -> **401 to fetch via the commons.thumbs behaviour**) + 54 url-only rows (the ORL/Limes set;
  1 has a copy -> **53 to fetch via commons.info's 1280 thumburl, NEW step**) + 2 neither.

**Ports on this VM (measured):** ELoFTR 127.0.0.1:8091 **UP** (matchanything_eloftr, RTX 5060 Ti - the
matcher WILL run in the working phase); LLM 8081 UP (qwen3.8-27b - FORBIDDEN for placement, the lead);
RoMa 8092 **down** (matchfit.run skips its second pass - by design); clef 18083 **down** and the tunnel
(`ssh -N -L 18083:127.0.0.1:8083 aibox`) cannot be opened here: `aibox` does not resolve and every ~/.ssh
key is forced-command. Consequence: newly-found pictures (phase 3) cannot be clef-classified in this
checkout; if the search finds new files while clef is down -> ask_human (tunnel, or approve the LLM as
one-off classifier). The 211 rows need NO classification (all 930 classified rows are already in
files.jsonl).

**Next session (ONE step): write fit/cover.py** from the DECISIONS design (six phases + CLI, each phase
taking `root` so tests drive it on a temp tree; import pattern copied from tools/site_done.py:
sys.path.insert fit/ + pipeline/). Per-phase notes the design does not spell out:
- fetch: re-implement commons.thumbs' behaviour (1/s pace, .part->rename, skip existing) WITH a root
  parameter (commons.thumbs is bound to module-level RAW/OUT); url-only rows: commons.info([title]) ->
  thumburl (iiurlwidth=1280) -> same fetch; then regenerate plans.json via tools/export_plans.main()
  in-process - its ROOT/BOOKS and the pipeline/commons module constants (OUT/RAW) are module-level, so
  a temp-tree test monkeypatches them (setup, allowed). Verify what commons_rows() reads when writing
  (it is defined in export_plans itself, line 18).
- search: commons.wd_claims([qid]) -> cat; commons.files_of(cat, depth=1); commons.search(name) (3
  queries, SEARCHES); commons.info (batches of 50) for keep(); evidence.fetch_page_ids +
  evidence.fetch_file_entities for the P180 re-test. Per-site SEARCH RECORD: {cat (name or "none"),
  n_cat_files, qid (or "no qid"), n_p180, title_queries (the 3 patterns), n_title_hits, failed routes,
  date}. Dedupe against existing files.jsonl titles. Paced; 429s recorded, not hidden.
- stage: files.jsonl row = the harvest row shape (re-read commons.harvest for the exact field set) +
  qid + by:"212"; local copy (fetch); classified.jsonl via the injectable classifier (default clef
  batch = commons.classify's questions; test: recorded p_* JSON); evidence.record(files, books, live,
  only=new sites); export_plans again.
- loop: for every built site still without a fit: import site_done and call site_done.main(
  [sid, "--root", root]) in-process WITHOUT --working/--model-json (model=None: matcher pass first,
  then batch_us.run_sites upsert "no model answer" for the rest; zero candidates -> the batch's
  no_picture item, which phase 5 re-records). site_done syncs each new doc itself (matcher docs get
  the spread guard, not the ladder clause). Collect each site's outcome (return code 0/1/2 + printed
  lines) for the report.
- nopicture: for search-set sites ending without candidates or a fit: review.upsert_item(root, sid,
  [], no_picture={"searched": <exact record string>, "at": now}) - entries=[] + dict keeps existing
  candidates (upsert_item's dict branch wins) and rewrites the batch's generic searched string.
- sync: cover owns the sweep loop; import plan_fit primitives (who_placed, is_done, build, prune,
  NO_PROVENANCE) and batch_us._doc_path/_save_json for the by:agent stamp. Per doc: hand -> build;
  agent -> build; unmarked-auto -> stamp then build; no provenance -> refuse (item entry, doc kept);
  ANY exception (catch Exception, not just SystemExit) -> record, upsert the site's item with the
  build-failure reason, continue. prune(root) at the end. This is the fix for the serve worker's
  give-up-whole-sweep weakness (PITFALLS pipeline/plan_fit.py).
- report: docs/batch.md in batch_us.write_report's shape but final: counts per outcome over all built
  sites (fit hand = the golden 21; fit automatic = every by:agent doc; human-saved = by:hand outside
  the golden 21 - compute, do not guess; review item; no picture found), the 20-sample of the WHOLE
  auto-doc union drawn with **SEED_212 = 20261012** (recorded in the doc; batch 20261010, null
  20261011 - the date convention), page URL + gate score per pick, and the no-picture list with each
  site's exact searched record.
- CLI: `python fit/cover.py <fetch|search|stage|loop|nopicture|sync|export|report|all> [--root DIR]
  [--working | --model-json F]` (the model flags are the loop's only; --working must refuse to pass
  the vision model for placement - it may stay in the parser for the batch-compat but 212 never
  passes it; document that in the module docstring).

**Session after that:** tests/test_cover.py per the design (hermetic; the served fixture, port 0;
monkeypatched network/classifier/matcher/export constants; box-6 invariant checked through the served
page; golden re-run; sample reproducibility). **Then the working run** (network allowed): fetch ->
search -> stage (ask_human only if new files need clef) -> loop (ELoFTR) -> nopicture -> sync (check
`ls data/raw/commons/big | wc -l` first - the big-jpg cache decides download cost) -> export ->
report -> commit everything (grown files.jsonl/classified.jsonl/plans.json, review items, review.json,
sites.json, the overlays, docs/batch.md); finish with `sha256sum -c tests/golden/hand_fit_docs.sha256`
and the suite green.

**Do NOT touch:** requirements.in/.txt (302a/304 hold them), tests/conftest.py, and the modules of the
phases I only call (tools/site_done.py, fit/batch_us.py, fit/matchfit.py, fit/review.py,
pipeline/plan_fit.py, pipeline/commons.py, tools/export_plans.py, server/serve.py): if one of them
needs a hook to make a phase testable, monkeypatch in MY test or file a new task - never edit it in
passing. My Touches now include data/db/platefits/ (added this session: the loop's matcher writes
docs, the line check may delete a pattern doc, the sync stamps by:agent). data/raw/ is the gitignored
shared store (no Touches needed).

**Suite:** not run on this synced tree yet - first act next session: `.venv/bin/python -m pytest
tests/ -q` (NEVER bare pytest - system python has no numpy/PIL; pytest.ini now keeps only failed
temp trees, 1 run - the disk-filling fix from 5961a64). Last known green: 150 passed, 1 skipped at
9590abf (the 1 skip is the standing baseline).

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
