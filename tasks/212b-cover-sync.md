Status: open
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

(2026-10-13, iteration 224, agent a - CODE DONE, dry run not yet run. 212a is my own prior
task (reopened by the driver only over 203b's two reds - see its journal); its work is
already in this branch, so I proceed on 212b. I accidentally overwrote 212a's hand-over
mid-session and restored it byte-identical (verified: git diff clean).)

**What changed this session (fit/cover.py is UNCOMMITTED - the harness saved it):**
- `sync()` now ends with the full review export: after `plan_fit.prune(root)` it calls
  `n_open, n_total = review.export(root)` and prints `sync: %d open of %d item(s) ->
  web/data/review.json`. Box 1's "and the review export". PITFALLS 1171: doc changes
  without a full export leave three count-deriving tests red, so sync (the one writer of
  the doc world) carries the export.
- Module docstring's sync phase line + sync()'s own docstring updated to match.
- My `Touches:` gained `data/db/platefits` (sync stamps by:agent into an unmarked auto
  doc, deletes a pattern doc) and `data/review/` (per-doc failure containment upserts
  entries; the trailing export records write-once resolutions) - added before touching.
- `ast.parse` passes; NO tests run this session (last suite state on this branch, from
  212a's done claim: 2 failed = 203b's pinned bibracte case in tests/test_batch_eu.py,
  153 passed, 1 skipped; golden 40/40).

**Re-measured live world (this branch, .venv/bin/python):** 131 docs = 21 by:hand + 110
by:agent + 0 unmarked; src: 105 commons + 26 book(s); ALL docs have ref + crop; ALL book
local files present (data/raw/books via the store). big cache has 72 files -> 54 commons
docs will DOWNLOAD in the live sync (paced ~1/s + one API call each). 94 doc sites: 80
symlinked to the store, 14 real dirs in the checkout (separate copies, not hard links).
is_done == 0 for ALL 131 docs in the checkout view -> the live sync REBUILDS every
overlay. 499 built sites; 36 with drawings>0. web/data/review.json: 333 open of 346 item
files (14 carry recorded resolutions). The store /home/agent/projects/ancient-works is a
git checkout of main at tip 77bdf5d, clean except .venv: writes through my checkout's 382
site symlinks land in ITS working tree (the shared canonical home; other agents' checkouts
symlink to it too - accepted concurrency, same as the batches did). Git tracks only 6
site dirs (forthill fudge highbank hopeton marietta newark; doc sites among them:
forthill, marietta, newark - all real dirs) -> the live run's committable web/data/sites
artifacts are those three dirs' rebuilt overlays + web/data/sites.json + review.json +
any data/review/ or data/db/platefits changes. All JSON writers verified atomic
(aw.save_json, review._save_json, batch_us._save_json: tmp + os.replace) -> hard-link
scratch trees are safe.

**NEXT STEP 1 - dry run (script exists, NOT yet run): /tmp/aw212b-dryrun.py.**
BUG TO FIX FIRST: line 24 `TREE = os.path.mkdtemp("aw212b-dry")` ->
`import tempfile` + `TREE = tempfile.mkdtemp("aw212b-dry")` (os.path has no mkdtemp;
I hit the context limit before the first run). What it does: builds a hard-linked tree
of web/data (FOLLOWING the 382 site symlinks into real hard-linked dirs, so nothing
reaches the store) + data/db, data/review, data/commons, data/books, data/catalog +
data/raw from the store; seeds a solid 2400x1600 JPEG big stand-in for every commons doc
(load_picture cache hit -> zero network); socket guard (create_connection + socket.connect
raise); time.sleep no-op; snapshots all tree files + the store's web/data,
data/db/platefits, data/review before/after; runs `cover.sync(TREE)` and prints: action
counts + every non-skip doc with its detail, store files changed (expect 0), golden 40
in-tree vs the sha256 file (expect 0 mismatches), docs added/removed/changed, item files
changed (with their new resolved field), review.json open count before/after (vs git
HEAD) + lost/gained open sites, sites.json drawings diffs, depictions.json changes
incl. shotwick's expected prune (stale plan_c_e6e5490609414bb9 entry + both webps
dropped, dep 2->1), and a box-6 probe: built sites with no drawings, no doc, no open
item (expect ~114: the 103 no-item with-row sites + 11 found-picture sites - the loop
phase's job in the TEST, not the live run: the lead runs the matcher loop live).
Run: `.venv/bin/python /tmp/aw212b-dryrun.py` (~2-4 min; tail -100 the output).

**NEXT STEP 2 - the LIVE run** (network allowed): `.venv/bin/python fit/cover.py sync` in
this checkout. Expect: 131 built (54 downloads), maybe a few "sent" (pattern check
fires -> doc deleted + item entry) - the one-site line's decision, not a bug; the
trailing export rewrites web/data/review.json (the open list may SHRINK: export records
write-once resolutions for items whose candidate has a doc - which ones: the dry run
tells you) and may change a handful of data/review/ item files. VERIFY before
committing: `sha256sum -c tests/golden/hand_fit_docs.sha256` 40/40 (box 2 - hand docs
all marked, no check applies, build/skip never rewrites a golden file); bibracte's item
file (data/review/bibracte-*.json) stays as 212a left it (no doc -> no resolution
write). COMMIT: fit/cover.py (the harness-saved edit), web/data/sites.json,
web/data/review.json, changed data/review/* item files, data/db/platefits/* if any
stamped/deleted, web/data/sites/{forthill,marietta,newark}/* (tracked; the other real
site dirs are gitignored). Then the suite (`.venv/bin/python -m pytest tests/ -q`):
expect exactly the two known 203b reds (if my claim is rejected on them, add 203b to my
Depends on - the 212a precedent).

**NEXT STEP 3 - box 3, the test in tests/test_cover.py** (the big remaining piece, 1-2
sessions). Extend the existing 212a fixture per the PARENT design (full text:
`git show 953d9ab:tasks/212-cover-final.md`, esp. the D1-D5 + CHOOSE recipe sections and
the 7 numbered assertion groups): fixture gains include_sites=True (real hard-linked
site dirs), PHASES extended with "loop" + "sync" (report is 212c's), matcher fakes
(monkeypatch on the shared module objects: site_done.matchfit.reachable -> False OR
matchfit.run -> a fake writing the CHOOSE docs; matchfit.spread stays real - it is
pure), big stand-ins for the CHOOSE commons docs (c_d0a020dec428fa00 /
c_e28ed261168b49c9 / c_d1ca997e67377769 - but RE-MEASURE CHOOSE first: the live world
changed after the 212a run, so the parent's CHOOSE ids may have shifted), then a port-0
served page (Popen [.venv python, server/serve.py, --port 0] cwd=tree, parse "Ancient
Works on (\S+)") checked with: (v) EVERY built site in the served sites.json has
drawings>=1 OR is in the served open list, and the page's review count matches
review.json (through the served page, not the file). Socket guard stays on;
tmp_path_retention_policy "failed" (the 48 GB box). The test's loop phase is what makes
the box-6 invariant TRUE in the tree (fresh all-rows items for the 103 no-item sites
etc.); sync in the test uses the stand-ins (no downloads).

**Depends on stays "212a"** (212a's work is in this branch; its reopening is only over
203b's two reds, which are not mine to fix). 203b in flight with agent c (they extend
the bibracte pins per the test's own docstring).
