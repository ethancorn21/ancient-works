Status: split
# 309: The queue pairs a drawing with the right place, not a namesake
Carved from: 307 (box 1)
Touches: tools/fit_queue.py, tools/right_place.py, web/data/fit_queue.json, data/review/, web/data/review.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
307 box 1, carved out so it runs in parallel with 307's page work (agent a). The queue's first entry paired
Allcroft 1908 Fig. 217, "The Devil's Dyke Camp, near Brighton" (a Sussex hillfort), with devil-s-dyke-q3307343, the
Devil's Dyke in Cambridgeshire, 150 km away. The owner could not find it on the map.

## Acceptance criteria
- [ ] (carved to 804 - the wiring in tools/fit_queue.py build(); 805 - the rebuild of the committed
      queue/review data) Every queue entry's candidate is checked to show the same place as its site, not just
      the same name: the caption/place words, county and region in the picture's metadata against the site's
      place, region and coordinates (Wikidata where it helps). A mismatch leaves the queue and goes to the review
      queue with the reason "same name, other place: <caption place> vs <site place>"; where the right site
      exists in the catalog, the candidate is moved to it instead.
- [ ] (carved to 805) docs/site_flow.md: how many of the queue's entries were wrong, and the list. Devil's Dyke
      Camp near Brighton is not paired with the Cambridgeshire dyke.
- [ ] (carved to 804) tests/test_fit_queue.py covers a namesake mismatch (no network).

## Notes
- Do not touch web/index.html, web/fitqueue.js (agent a, 307) or fit/ (the lead is building the matcher fit
  there). The subtasks' own Touches lines are authoritative for their files; 804 also carries
  data/review/README.md (the reason extra in the pass-through list) and 805 carries
  tests/test_right_place_drift.py.

## Hand-over

(2026-10-12, iteration 103, agent c - session 12 on the 309 lane. FIRST session of
805. The committed rebuild (805 box 1's data writes) is DONE in the worktree but
UNCOMMITTED: the full suite shows 3 failures, all caused by the rebuild, all sharing
one root cause (new item kind: review items for unbuilt CATALOG sites). The fix is
designed below; it edits fit/review.py + fit/batch_eu.py, NOT the failing tests.)

CARVE STATE: 309 box 1 wiring = 804 DONE; box 3 (namesake tests) = 804 box 4 DONE;
box 2 (site_flow report + rebuild) = 805: box 1's data writes DONE (uncommitted),
box 1's stability verified, 3 suite failures to fix, box 2 (docs/site_flow.md
section) NOT STARTED, box 3 (tests/test_right_place_drift.py) NOT STARTED.

WHAT THE REBUILD DID (verified in scratch /tmp/scratch805 AND on the checkout;
second run byte-stable - zero churn; the /tmp trees still exist if you need them;
/tmp/baseline805 = the pre-rebuild state of the checkout, for A/B runs - it has no
.venv, use /home/agent/projects/ancient-works.c/.venv/bin/python):
- web/data/fit_queue.json: 117 -> 114 entries (107 entries byte-identical, 7 narrowed,
  3 left). Left: vindomora-q7932358 (only cand n0354_1), windmill-hill-q4348373
  (n0557_1/n0558_1/n0558_2), shotwick-castle-q7502621 (n0575_1). Narrowed: alauna,
  bokerley-dyke (n0599_1 gone), castle-neroche, clun-castle, coria, devil-s-dyke
  (n0686_1+n0599_1 gone; best is now n0662_1 "the only candidate"), eaton-socon
  (n0285_1/n0557_1/n0558_1/n0558_2 gone). ZERO candidates moved into a built site
  (no flagged row's top right site is built - re-derived, the iteration-102 guess
  that the hillfort was built was wrong).
- 15 flags: 10 upserted into 5 NEW item files for unbuilt catalog right sites; 5
  skipped (target item already holds the plan - the intended steady state, zero
  writes: alauna/castle-neroche <- n0438_1 into their own items; clun-castle <-
  n0575_1; coria/vindomora <- n0354_1 - all "self, item holds"). The moved-set
  dedup means windmill-hill's three flags write nothing (same (target, plan) pairs
  as eaton-socon's, which sort first). New files in data/review/:
  a-saucer-barrow-and-a-bowl-barrow-600m-n-q17677473.earthworkenglan01allcgoog_n0558_1.json
  (cands n0558_1+n0558_2, both reason "LEWES DOWN vs St Neots, Cambridgeshire, England"),
  castle-dyke-q31112898.earthworkenglan01allcgoog_n0599_1.json ("Aysgai-th, Yorks,
  Aysgarth vs Dorset, England" - reason's vs-side is the SOURCE site bokerley-dyke's
  sites.json place; see data quirk below),
  devil-s-dyke-hillfort-q17674160.earthworkenglan01allcgoog_n0686_1.json ("near
  Brighton vs Stetchworth, Cambridgeshire, England" - THE owner's case),
  down-end-castle-q5302812.earthworkenglan01allcgoog_n0285_1.json ("Bath vs St Neots
  ..."), oval-barrow-and-adjacent-bowl-barrow-220-q17672356.earthworkenglan01allcgoog_n0557_1.json
  ("FIRLE HILL vs St Neots ..."). All resolved: None, no_picture: None.
- web/data/review.json: 335 -> 340 open of 346 total (the 5 new items open; none left
  open; NO write-once resolved records touched - the six c5250a4 files untouched).
- Export prints 5 stderr warnings (one per new item): "review: site '<id>' not in
  web/data/sites.json; using the id as name" - these 5 sites are in the CATALOG
  (data/catalog/sites.jsonl) but not in web/data/sites.json (unbuilt).

TEST STATE (full suite, .venv, 123.7 s): 80 passed / 1 skipped / 3 FAILED - the 3
failures are ALL caused by the rebuild (verified: all 3 PASS on /tmp/baseline805,
the checkout minus my 8 changed files, 7.45 s):
- tests/test_site_done.py::test_site_done_line and tests/test_fit_provenance.py::
  test_line_refuses_unmarked_non_auto_doc: both assert err == "" on the one-site
  line (tools/site_done.py -> review.export), and the export's 5 warnings break it.
- tests/test_batch_eu.py::test_union_check: union_check (fit/batch_eu.py:91-102) flags
  every item whose site field is not in sites.json as orphan_items -> my 5 items.

ROOT CAUSE + THE FIX (designed, NOT yet implemented - this is the exact next step):
The 309 chain made "a review item for an unbuilt catalog site" a LEGITIMATE new
item kind (804's rule, pinned by test_fit_queue_namesake). Two data-integrity
contracts still assume every item site is in sites.json: (a) fit/review.py export's
warning + id-as-name, (b) fit/batch_eu.py union_check's orphan_items. The fix makes
both catalog-aware WITHOUT editing any test file: fit/review.py: export reads
data/catalog/sites.jsonl (stdlib json; absent file = degrade to today's behavior -
synthetic temp trees have no catalog, so test_review's pinned cases keep passing -
CHECK test_review.py L191 test_export_cli and L228 first) and, for an item site not
in sites.json: in the catalog -> use the catalog record's NAME as the page name and
no warning (also a page improvement: review.json currently shows the truncated id
for these 5); in neither -> keep the warning. fit/batch_eu.py: union_check treats an
item as an orphan only when its site is in NEITHER sites.json nor the catalog; an
catalog item is skipped from the coverage counts exactly as before (no behavior
change for sites that are in sites.json). No catalog in the tree -> old behavior
byte-identical. Then: extend 805's Touches line with fit/review.py and
fit/batch_eu.py (AGENTS.md: add a path first if your task really needs it - it does;
note: the 309 Notes' "do not touch fit/" was about the lead's in-flight matcher fit
= fit/matchfit.py; review.py and batch_eu.py are separate files - flag this in
DECISIONS). Re-run the full suite (expect the 3 to pass, 83+ passed / 1 skipped /
0 failed), re-verify the rebuild's stability once more, then commit the data files
+ the two fit/ edits as 805 box 1.

NEXT STEPS (in order):
1. Fix fit/review.py export (catalog-aware name + warning) and fit/batch_eu.py
   union_check (catalog-aware orphan), per the design above. Read test_review.py
   and tests/test_batch_eu.py's temp-tree builder FIRST to confirm the no-catalog
   degrade keeps every pinned case (the batch temp tree: check whether it copies
   data/catalog/ - if it does, a deliberately-created orphan in that test would be
   a site in NEITHER file - re-read how the test builds its tree before editing).
2. Add fit/review.py, fit/batch_eu.py to 805's Touches; run the full suite;
   re-run build+export stability; commit "805: rebuild ..." (data files + the two
   fit/ fixes together - the data is meaningless without the contract fix).
3. Box 2: docs/site_flow.md namesake section - report the ACTUAL numbers: 15 pairs
   over 9 sites wrong (list: site, caption, reason as in the items above); 10 went
   to review items on 5 unbuilt right sites (named), 5 were already parked in the
   source item (no write); queue 117 -> 114; how the check decides (stored fields
   only: explicit county/state word, towns resolved to classic counties through the
   catalog, fail open; --live is a human re-run, never in the build). Read
   docs/site_flow.md's structure first (agent a's 306 also touches it - append a
   clearly separate section, do not reflow theirs).
4. Box 3: tests/test_right_place_drift.py (hermetic, stdlib, no network): for each
   of the 17 top-level names between tools/right_place.py's VERBATIM markers
   (US_STATES, ABBR, UK_ABBR, UK_COUNTIES, GENERIC, norm, name_keys, tokens,
   place_of, site_place, site_toks, name_lookup_keys, row_inputs, score_candidate,
   BOOK_SCOPE, PLACE_WORDS, phrases) extract the block from both that file and
   pipeline/books_match.py, assert byte-identical. Extraction rule that works (both
   files checked this session): a block = from the name's start line ("^NAME = " for
   assignments, "^def NAME(" for functions) to the end of its logical statement -
   assignments: consecutive non-blank lines; functions: up to the first
   non-blank line at column 0. Verify norm/name_keys/... all match (they do today -
   187fd66's refactor kept them in sync; the test must PASS before any future
   drift). Note SUFFIX sits inside right_place's verbatim region but is NOT in the
   17-name list - the box's list governs. Do NOT edit pipeline/books_match.py (the
   source of truth; a real drift is fixed there - it is not agent a's/lead's in
   flight as of this session, but re-check git log -- pipeline/books_match.py
   first).
5. Full suite green; tick 805's boxes; 805's hand-over; then the driver returns 309
   for its three carved-box ticks (box 2's "Devil's Dyke not paired" is proven by
   the rebuilt queue file: n0686_1 is on the hillfort's review item, off the dyke's
   entry).

DATA QUALITY NOTES (for DECISIONS / the lead, NOT mine to fix - web/data/sites.json
is agent a's 306 lane): bokerley-dyke-q891218's sites.json place is "Dorset,
England" though the catalog says Cambridgeshire (Bokerley Dyke IS in
Cambridgeshire) - the check (catalog) flagged correctly, only the reason string's
vs-side shows the bad sites.json place; vindomora-q7932358's place "County Durham,
England" (Vindomora is Northumberland). The review page shows the 5 new items by
their truncated id (export's fallback) until box 1's catalog-name fix lands.

WORKTREE (still true): commit only in /home/agent/projects/ancient-works.c
(branch agent/c); data/raw is a symlink into the shared store (the rebuild never
opens images). My branch has NOT received main's latest (agent a's 307ba done-claim
8a8b6f6 and after are on main, not here - the driver synced 9be7094 before
iteration 102 but not before this session): if the next session's merge brings
conflicts on web/data/fit_queue.json or web/data/review.json, reconcile by
re-running the build (it is deterministic and stable) rather than hand-merging.

Re-read (when touching the wiring again):
- tools/fit_queue.py: _apply_flags <-> tests/test_fit_queue.py: _derive_with_check
  must stay in lockstep (same two-phase, sorted flag order, `moved` set,
  pristine-item skip, eligible = built minus hand). A change to one needs the other.
- fit/review.py: upsert_item (write-once resolved; merges by plan; the file name's
  lead follows candidates[0].plan) and export (never called by the build).
- The six baked-in right_place spec deviations (DECISIONS, iteration 95) are pinned
  by the namesake test's outcomes - changing any rule changes the pinned bytes.

Carve state: 309 box 1 (wiring) = 804 DONE; 309 box 3 (namesake tests) = 804 box 4 DONE;
309 box 2 (site_flow report + rebuild) = 805 NOT STARTED. When 805 is done the driver
returns 309 and I tick its three carved boxes.

WHAT CHANGED THIS SESSION (all in agent/c's worktree; 804's boxes 1+2 were already
committed as 077ccb8 before this session):
- tests/test_fit_queue.py: fixed three latent bugs in the written (unrun) code -
  (1) _build_namesake_tree unpacked the site dicts as pairs (`for s, _ in sites` ->
  `for s in sites: ... s["id"]`); (2) the namesake tree never created data/books/lists
  before _save_json (mkdir parents=True on lists); (3) test_fit_queue_real did
  shutil.copy2 into data/books/ before any copytree created that dir (explicit mkdir
  now). Plus one assertion fix: Path.glob is filesystem-ordered, not sorted - the
  namesake test's item-file list now sorts its glob.
- data/review/README.md (804 box 3): the pass-through line names 309's place_reason
  (after the 203a gate_score/why mention) and the Rules list gained a bullet
  (the reason string, written only by tools/fit_queue.py's build; the page's Review
  list shows it in 307c; neither the page nor a human save writes it). No test pins
  the README text (grep confirmed).

TEST STATE (verified by running):
- tests/test_fit_queue.py: 6/6 pass in 52 s (synthetic unmodified; namesake + real new;
  the slow Part-2 line test and both Part-3 browser tests pass).
- FULL SUITE: 83 passed / 1 skipped / 0 FAILED in 133 s. The three pre-existing
  main-side failures (test_fit_provenance::test_line_refuses_unmarked_non_auto_doc,
  test_fit_queue::test_save_runs_the_one_site_line, test_site_done::test_site_done_line)
  were FIXED MAIN-SIDE by the lead's matcher-fit commits (b22a2d2 "matcher fit
  wired into site_done", cf29be2 "matcher spread guard", ...) that landed in agent/c
  via the driver merge 9be7094 this session. Nothing I wrote touched those tests;
  the baseline for "no new failures" is now the green suite.

POST-MERGE BASELINE (re-verified this session, still the ground truth for 805):
- Read-only CLI on the checkout: 324 pairings checked, 15 flagged - identical to
  iterations 100/101. The 15 flags match 805's criteria list exactly (devil-s-dyke <-
  n0686_1 Brighton + n0599_1 Aysgarth; bokerley-dyke <- n0599_1; coria + vindomora <-
  n0354_1; eaton-socon <- n0285_1 + n0557_1 + n0558_1/2; windmill-hill <- n0557_1 +
  n0558_1/2; alauna + castle-neroche <- n0438_1; clun-castle <- n0575_1).
- The merge c5250a4 ("full review export under the current resolution rules", task 220
  on agent/a) touched SIX data/review/ item files (write-once resolved records) and
  web/data/review.json (340 -> 335 open of 341). It changed none of the flags, but
  805's rebuild must be re-derived against the POST-MERGE data: the iteration-100
  note's "5 new item files / 6 upserts" predates that export. The build's upserts
  never write `resolved` (write-once), so the six touched files are only at risk if
  they are also upsert targets - check on the run.

EXACT NEXT STEP (next session: take 805, `Depends on: 804` satisfied by the acceptance
merge of 804's work):
1. Re-run the wired build on the REAL checkout: `python3 tools/fit_queue.py --root .`
   (writes web/data/fit_queue.json + the item upserts into data/review/), then re-export
   in the same run window: `python3 fit/review.py export` (web/data/review.json). Do not
   hand-edit any item file or the page file.
2. Verify the rebuild: 15 flagged pairs disposed per 804's rule (the built right site
   devil-s-dyke-hillfort-q17674160 gains n0686_1 in its queue entry, sites narrowed;
   n0558_1/2 -> the unbuilt a-saucer-barrow item etc. - re-derive the exact list from
   THIS run's flags, do not trust the iteration-100 file list); second build run
   byte-identical (zero churn); export a no-op on re-run.
3. docs/site_flow.md: the namesake section (how many of the queue's entries were wrong
   and the list: site, caption, reason; which candidate moved where vs review; queue
   size before/after - report the ACTUAL numbers of this run; the criteria's "117" is
   the pre-split figure and the queue has moved under the batch tasks since, 803
   precedent: derive, never pin). State how the check decides (stored fields only;
   fail open; the --live Wikidata path is a human re-run, never in the build).
4. tests/test_right_place_drift.py: for each of the 17 top-level names between the two
   VERBATIM markers of tools/right_place.py (US_STATES, ABBR, UK_ABBR, UK_COUNTIES,
   GENERIC, norm, name_keys, tokens, place_of, site_place, site_toks,
   name_lookup_keys, row_inputs, score_candidate, BOOK_SCOPE, PLACE_WORDS, phrases),
   extract the block from both that file and pipeline/books_match.py and assert
   byte-identical. Do NOT edit either file: a real drift is fixed in books_match (the
   source of truth) - if that file is agent a's/lead's in flight, log in DECISIONS
   instead.
5. Full suite green (83/1/0 as of this session), commit "805: ...".

Worktree warning (still true): all three worktrees share one repo; commit only in
/home/agent/projects/ancient-works.c (branch agent/c); data/raw is a symlink into the
shared store - the build never opens images (sizes come from the json files), so a
rebuild cannot write through it, but never run the batch/line tools in the main
worktree.

Re-read (when touching the wiring again):
- tools/fit_queue.py: _apply_flags <-> tests/test_fit_queue.py: _derive_with_check
  must stay in lockstep (same two-phase, sorted flag order, `moved` set,
  pristine-item skip, eligible = built minus hand). A change to one needs the other.
- The six baked-in right_place spec deviations (DECISIONS, iteration 95) are pinned by
  the namesake test's outcomes - changing any rule changes the pinned bytes.
