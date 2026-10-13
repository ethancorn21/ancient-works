Status: in-progress
# 212b: The page-facing sync - every fit is an overlay, review.json is the open list
Depends on: 212a
Touches: fit/cover.py, web/data/sites.json, web/data/sites/, web/data/review.json, data/db/platefits (the sync stamps by:agent into an unmarked auto doc and deletes a pattern doc), data/review/ (the sync's per-doc failure containment upserts item entries; the trailing export records write-once resolutions), tests/test_cover.py

## Goal
The one page-facing sync from 212: every fit document becomes its site's overlay
(web/data/sites/<id>/depictions.json) and drawings count in web/data/sites.json through
the existing plan_fit machinery (plan_fit.main(), the way serve.py's after_write does);
web/data/review.json is regenerated (python3 fit/review.py export).

## Acceptance criteria
- [ ] `python3 fit/cover.py sync` runs plan_fit for every site with a fit doc and the review export.
- [ ] The hand fits' overlays are unchanged (000's golden test still passes).
- [ ] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item; the page's review count
      matches review.json (checked through the served page).

## Hand-over

(2026-10-13, iteration 226, agent a - LIVE SYNC IN FLIGHT at the context limit: nohup
`.venv/bin/python -X faulthandler -u fit/cover.py sync` (pid 1967760) started 06:01:48
CDT, log /tmp/aw212b-live.out, expected done ~06:17-06:20; by 06:01:48 it had processed
through argentoratum with exactly the right first 2 sends (platefits 131 -> 129).
**NEXT: `ps aux | grep 'cover.py sync' | grep -v grep; tail -20 /tmp/aw212b-live.out`**
(sleep 120 between checks); if it died, re-run the same command (idempotent: pattern
check pure, item upsert in-place, export derived), then NEXT STEPS 2-5.

**NEW FACTS learned mid-run (they change the verification - read first):**
(a) My checkout's data/db/platefits files are HARD LINKS into the shared store (link
   count 3 = store + me + agent c) - the driver re-hardlinked the store's state around
   session start, and the store carries 3 docs my 05:58 preflight lacked: argentoratum
   c_191c6221 / c_436bea50 / c_5badc8c8 (the lead's Oct-12 Mac placements; store total
   ~134 - VERIFY the exact count at check time). So the run starts from ~134 docs, not
   131: the 3 new ones are matcher docs (spread check, not the lattice check) and are
   already current in the store's argentoratum depictions -> skips. Expected final
   platefits count ~134 - 76 = 58.
(b) ACTION COUNTS WILL DIFFER from the dry run's 76/25/30 (more skips, fewer rebuilds):
   is_done runs against the store's CURRENT depictions (via the 80 site symlinks), and
   agent c's suite (running in checkout ancient-works.c since 06:00, incl. hermetic
   port-0 serve tests for 306) is a CONCURRENT writer through those same symlinks - the
   store's argentoratum depictions was rewritten 06:02. Both sides write JSON atomically
   (tmp + os.replace); webp saves are in-place but byte-deterministic (same risk the
   batches and the 225 dry run ran). VERIFY THE FINAL STATE, NOT THE ACTION COUNTS:
   depictions entries, sites.json drawings, review.json open list, item files, the 76
   platefits deletions.
(c) The 76 sends are unchanged in kind (all fabricated-pattern: grid-round / 1D-ladder /
   2D-lattice anchors - the 301 vision-model tells): each = doc deleted + a review item
   entry (why = the pattern) + its overlay pruned. Expected final: 365 open items
   (333 + 32 gained, 0 lost), ~13 sites.json drawing changes (12 sites 0->1, maiden
   1->2, aldenhaag 1->0), shotwick map-only, golden 40/40, bibracte item untouched,
   store git status still clean (only ?? .venv). The 3 new argentoratum docs may need
   one-off big downloads - _fetch paces and honours Retry-After; if any doc logs
   "failed" that is the designed per-doc containment (a review entry records it) -
   note it in the commit message, don't panic.
(d) old-sarum self-heal: both its agent docs are pattern -> sent; prune drops the c_0410
   webps the 225 bench wrote through the symlink; the sites.json entry returns to the
   pre-bench 2 drawings / 3 overlays / score 2.86 (the net diff vs HEAD undoes bc83645).
)

**World / prior state (reconstructed - iter 225 was unlogged, see DECISIONS):**
- 212a DONE (lead marked it, a31c5bc). 231/232/233/234 all Status: done now (lead's
  233+234 = aeeb5aa, in my history; no marking work left for me).
- Iter 224 (184a43e + driver 6c7682b): the sync code is committed: sync() ends with
  plan_fit.prune + the full review.export (box 1's "and the review export").
- Iter 225: ran the dry run to COMPLETION (/tmp/aw212b-dryrun2.out, full results below)
  and ran a plan_fit.build bench against the LIVE tree. The bench rebuilt old-sarum's
  c_041083ec68b532f8 overlay THROUGH the site symlink into the shared store (3
  gitignored files: depictions.json + 2 webps) and updated this checkout's
  web/data/sites.json (old-sarum 2->3 drawings, 3->4 overlays, score 2.86->3.15;
  driver committed it as bc83645). The live sync self-heals all of it: both old-sarum
  agent docs are pattern -> sent, prune drops the c_0410 webps, and the entry returns
  to the pre-bench 2/3/2.86 (the net diff vs HEAD undoes bc83645).
- Dry run results = the live run's STATE expectations (the action counts will differ -
  see the NEW FACTS above):
  actions **sent 76, skipped 25, synced 30, refused 0** (131 docs); golden 40/40
  unchanged; 0 docs changed; **76 docs DELETED** (all fabricated-pattern: grid-round /1D-ladder/
  2D-lattice anchor signatures - the 301 vision-model tells; incl. both old-sarum agent
  docs, marietta, serpent-mound x7, traiectum x7, old-sarum...); item files 24 changed
  (incl. alligator's write-once RE-resolution to the doc the sync just sent) + ~32 new;
  **review.json 333 -> 365 open (32 gained, 0 lost)**; sites.json drawings: 12 sites
  0->1 + maiden-castle 1->2, aldenhaag 1->0; depictions.json 31 changed, 18 webps
  pruned (the sent docs'), 60 new webps (30 built x2), shotwick now map-only (expected
  prune of the stale plan entry); box-6 probe: **103 built sites with no drawings, no
  doc, no open item** (that is the loop phase's job in the TEST, not the live run -
  the lead runs the matcher loop live, per the parent's lead note).

**Live-run preflight (this session, .venv):**
- Docs: 131 = 21 by:hand + 110 by:agent + 0 unmarked. NOTE: the doc field is `by`,
  NOT `author` (a wrong-key one-liner misreports "0 hand" - measured it both ways).
- Offline recompute of the same _sync_doc decisions (who_placed -> matcher?spread:
  fabrication_pattern -> is_done) reproduces the dry run EXACTLY: 76/25/30/0.
- **Downloads needed: 0.** 224's "54 will download" assumed all 105 commons docs get
  built; only 30 are built, 29 of them commons, ALL already in the big cache (now 73
  files, data/raw is the store's shared cache). So the live run is ~16 min pure compute,
  no network, no 429 risk (_fetch has Retry-After handling anyway).
- _sync_doc never calls matchfit.run (only the pure spread / pattern checks) -> no
  ELoFTR dependency in sync.
- data/review = REAL tracked dir in this checkout (347 tracked: 346 items + README) ->
  item upserts/creates are committable and never touch the store. data/db/platefits =
  hard-linked into the store (see NEW FACT (a)): my sends delete MY checkout's dir
  entries only - the store keeps its own entries for the 76 docs until main lands there
  (306a's audit set the precedent); any in-place write through the platefits would reach
  the store, but _sync_doc only deletes or stamps those files (stamps use atomic
  writes; this run stamps 0 docs - none are unmarked).
- Store (/home/agent/projects/ancient-works) is clean (only ?? .venv). Writes through
  the 80 symlinked doc-site dirs land in the store's gitignored site dirs (accepted
  concurrency, same as the batches); the 14 real doc-site dirs (incl. tracked
  forthill/marietta/newark) are written in the checkout only.
- git HEAD is clean before the run (baseline = committed state).

**NEXT STEPS (in order):**
1. Wait for the run: `ps aux | grep 'cover.py sync' | grep -v grep; tail -20
   /tmp/aw212b-live.out` (sleep 120 between checks; done ~06:17-06:20 CDT; if dead,
   re-run the same command). Last lines: `sync: N document(s) over M site(s)` then
   `sync: 365 open of 378 item(s) -> web/data/review.json` (N ~134 - the
   store-refreshed count, not 131; 378 = 346 + 32 new items - if it differs, check
   review.export's printed total against the item dir count).
2. Verify against the dry-run expectations:
   - `sha256sum -c tests/golden/hand_fit_docs.sha256` -> 40/40 (box 2; find and run the
     000 golden test that consumes this file too - it is 000's golden test per the box).
   - bibracte item untouched: `git diff -- data/review/bibracte-q650053.json` empty
     (no doc on it -> sync never upserts it; the export's write-once guard means no
     resolution write either).
   - Store still clean: `cd /home/agent/projects/ancient-works && git status --short`
     -> only `?? .venv` (agent c may have dirtied gitignored files too - ignore those;
     any TRACKED change there = investigate before committing mine; its old-sarum files
     are gitignored and should be pruned/rewritten by the sync).
   - review.json 365 open / 32 gained / 0 lost (diff vs dryrun2.out's lists).
   - sites.json: ~13 entries differ from HEAD (the exact set can shift with concurrent
     store writes), old-sarum back to 2/3/2.86; shotwick map-only; every sent doc's
     webps gone, every built doc's webps present (dryrun2.out's lists are the template).
3. Commit (git add -A): the 76 platefits deletions, web/data/sites.json, web/data/
   review.json, data/review/* (24 changed + ~32 new), web/data/sites/{forthill,
   marietta,newark}/* if changed, memory files. Message: `212b: live sync ran - 76
   fabricated-pattern docs sent to review and deleted, rebuilt the rest, 365-open
   list; boxes 1+2`.
4. Suite: `.venv/bin/python -m pytest tests/ -q` (~5 min). Expect ONLY 203b's two reds
   (test_sample_run_real_gate, test_batch_adds_files_rewrites_none - the bibracte
   FileNotFoundError; in flight with agent c, who extends the pins per the test's own
   docstring). If my done claim is rejected on them, add 203b to my Depends on (the
   212a precedent). Any OTHER red = mine to fix (PITFALLS 1171: a doc change without a
   matching export/page state leaves count-deriving tests red - but my sync carries the
   export, so check what state the red test reads).
5. Tick boxes 1+2, keep box 3 (the test) open, rewrite this hand-over around the
   parent's box-3 design (below), commit, done.

**BOX 3 (next sessions) - the test in tests/test_cover.py**, per the PARENT design (full
text: `git show 953d9ab:tasks/212-cover-final.md`, esp. the D1-D5 + CHOOSE recipe
sections and the 7 numbered assertion groups): extend the existing 212a fixture with
include_sites=True (real hard-linked site dirs), PHASES + "loop" + "sync" (report is
212c's), matcher fakes monkeypatched on the shared module objects (site_done.
matchfit.reachable -> False OR matchfit.run -> a fake writing the CHOOSE docs;
matchfit.spread stays real - pure), big stand-ins for the CHOOSE commons docs -
**RE-MEASURE CHOOSE first: the live run deleted 76 docs and re-derived review.json,
so the parent's CHOOSE ids (aardenburg/aesica/aire-sur-la-lys/alauna) may have moved
or their rows' items changed**; port-0 served page (Popen [.venv python, server/
serve.py, --port 0] cwd=tree, parse "Ancient Works on (\S+)"), checked: (v) EVERY
built site in the served sites.json has drawings>=1 OR is in the served open list, and
the page's review count matches review.json (through the served page, not the file).
Socket guard stays on; tmp_path_retention_policy "failed" (the 48 GB box). The test's
loop phase makes the box-6 invariant TRUE in the tree (fresh all-rows items for the
103 no-item sites etc.); sync in the test uses stand-ins (no downloads).

**Depends on stays "212a"** (done; in this branch). 203b (agent c) in flight: its two
reds are not mine to fix; add to Depends on only if the driver rejects my claim on
them.
