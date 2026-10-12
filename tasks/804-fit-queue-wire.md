Status: in-progress
# 804: the queue build applies the right-place check - wiring in tools/fit_queue.py, namesake tests
Depends on: none
Carved from: 309 (box 1, the wiring half; box 3)
Touches: tools/fit_queue.py, data/review/README.md, tests/test_fit_queue.py

## Goal
tools/right_place.py (309's committed module: the offline right-place check; its verified run on
the current data flags 15 queue pairings over 9 sites as namesake mismatches, the Brighton vs
Cambridgeshire Devil's Dyke among them) is a read-only CLI today. This task wires it into
tools/fit_queue.py build() so the generated queue never pairs a picture with a namesake site again:
every (site, candidate) pair the build would emit is checked against the stored metadata (the
caption's explicit county/state word and its towns resolved to classic counties through the
catalog, against the site's county/state; an unknown place never flags - the module's documented
rules, re-read its docstring). A flagged candidate leaves the source site's queue; where the
module's find_right_site (min_score 0.5) finds the right site in the catalog the candidate is
moved there instead; otherwise it is recorded in a review item with the reason "same name, other
place: <caption place> vs <site place>". The queue file's entry shape (the 305 contract:
{site, name, best{plan,reason,row}, candidates[...]} in {"at", "entries"} form) is unchanged; a
tree without the catalog/book stores runs the check as a no-op, so 305's synthetic test keeps
passing unmodified. Rebuilding the committed data files is 805.

## Acceptance criteria
- [ ] build() in tools/fit_queue.py: for every built site without a hand fit, each candidate of
      _candidates() is checked with tools/right_place (one site_facts per site, then
      picture_facts/check_pairing per candidate) and the build is two-phase - every flag decision
      is computed over the pre-mutation candidate sets first, and only then are the drops, moves
      and upserts applied and the entries recomputed - so a move into a site can never feed that
      site's own flag decision in the same build. A flagged candidate is dropped from its source
      site's entry (the best recomputed over the remainder; a site with no candidate left leaves
      the queue entirely). The check runs only when right_place.load(root) finds a catalog, a book
      index or book lists; with none of them the build behaves exactly as today (the no-op
      degrade that keeps 305's synthetic test green unmodified). tools/fit_queue.py stays
      stdlib-only (tools/right_place.py and fit/review.py are; no pipeline/ import - import
      fit/review the way tools/site_done.py does, sys.path insert of ROOT/fit).
- [ ] Disposition of a flagged candidate (source site S, candidate P, facts F):
      1. find_right_site(data, F, exclude=S) returns a catalog site T (top of its scored list,
         min_score 0.5):
         - T is built (web/data/sites/<T>/ exists): P joins T's queue entry as a candidate with
           the same stored fields and sites narrowed to [T] (the row itself when P came from
           plans.json, the item-candidate fields when P came from an item);
         - T is not built: P is upserted into T's review item (fit/review.upsert_item) with the
           reason.
      2. No passing T: P is upserted into S's own review item with the reason.
      The reason is check_pairing's string, deterministic from stored fields; re-running the
      build over unchanged inputs never duplicates or churns (an upsert of a candidate the item
      already holds is byte-identical; upsert_item's write-once resolved and its lead-plan file
      rename are honoured - check the no-picture item whose first candidate is a moved one: the
      file name gains the lead plan). A flagged candidate that is already one of S's own item
      candidates stays out of S's queue and is not re-upserted (it is re-flagged every build:
      the intended steady state).
- [ ] data/review/README.md: the candidate pass-through line names the new extra (the 309
      place-check reason, the 203a gate_score/why pattern; the page's Review list shows it in
      307c, not here).
- [ ] tests/test_fit_queue.py (hermetic, dead-socket guard, no network):
      1. A new synthetic-tree namesake test: a small catalog plus book index/list where one
         picture's caption place contradicts the paired site's county (the Brighton-vs-
         Cambridgeshire shape): the pair leaves the source site's queue; with the right site
         built the candidate lands in that site's entry; with it unbuilt the right site's item
         gains the candidate with the reason; with no right site in the catalog the source
         site's item gains it; a site with an unknown county is never flagged (fail open).
      2. test_fit_queue_real re-derived WITH the check: the temp tree also copies
         data/catalog/ and data/books/ (index.jsonl + lists/); the test's independent derivation
         runs the same right_place check over the same inputs (importing tools/right_place,
         stdlib) and matches the generator's output - entry set, per-entry candidate sets, the
         review-item upserts in the tree; the checkout itself stays byte-identical; the
         dead-socket guard stays.
      3. test_fit_queue_synthetic passes unmodified.
- [ ] The three pre-existing main-side failures (test_fit_provenance::
      test_line_refuses_unmarked_non_auto_doc, test_fit_queue::
      test_save_runs_the_one_site_line, test_site_done::test_site_done_line - the lead's
      matcher-fit wiring fallout) are left failing: do not edit their assertions; the rest of
      the suite stays at its current pass count (no new failures).

## Notes
- The module tools/right_place.py is 309's deliverable (commit fc67bb9 on agent/c; it lands on
  main when 309 closes out as split). This task runs in 309's owner lane (agent c), whose
  branch already has the module. If your branch does not have it (a different agent's branch
  was handed the task), 309 is not merged yet: add `Depends on: 309` to this file, commit, and
  wait - do not rebuild a copy of the module here.
- Do not touch agent a's files (web/index.html, web/fitqueue.js, web/review.js, web/fitkit*.js)
  and do not write the real checkout's data/review/ items or web/data/fit_queue.json: the build
  runs on temp trees in the tests; the committed rebuild is 805.

## Hand-over

(2026-10-12, iteration 100, agent c - session 9 on 309's lane. Step done: 804 boxes 1+2 -
the two-phase right-place wiring is IN tools/fit_queue.py and verified (see below and the
iteration-100 DECISIONS entry). The code change is uncommitted in the checkout at hand-over
(harness saves it); the next session commits it with the box-3/box-4 work or on its own.
NEXT STEP (next session, same lane): commit the wiring, then 804 box 4 (tests, sketch below)
and box 3 (the README note); then 805 (the rebuild). When 804+805 are done the driver
returns 309 and I tick its three carved boxes and set it done.)

Box state: 1 (two-phase wiring) and 2 (dispositions) - IN and verified. 3 (README note),
4 (tests) - not started. 5 (no new failures) - verified at the last suite run (baseline
3 failed / 77 passed / 1 skipped, the same three pre-existing main-side failures); leave
unticked until the box-4 tests land and a final run is green at the same count.

**What is in tools/fit_queue.py now (all verified this session):**
- Header docstring: namesake-rule paragraph; stdlib-only line names right_place/review as
  the only imports (both stdlib-only, no pipeline/).
- After ROOT: sys.path.insert of ROOT/tools and ROOT/fit, then import right_place / import
  review (noqa E402, the site_done.py pattern - required: runpy.run_path leaves the script
dir off sys.path under the test GUARD; PITFALLS entry exists).
- _site_records(root): sites.json keyed by id (site_facts' input).
- _place_store(root): right_place.load; None when catalog AND index AND lists all empty ->
  build is exactly 305's (no-op degrade; keeps the synthetic test green).
- _place_flags(root, store, cands): one site_facts per site, picture_facts + check_pairing
  per candidate, over the PRE-MUTATION maps -> {(sid, plan): (facts, reason)}.
- _item_candidate(item_cands, sid, plan): the item candidate a queue candidate came from.
- _place_entry(plan, row, item_cand, reason): the review-item candidate for a moved
  picture - the item's own stored fields (dict copy: pairs/evidence/why travel with it)
  when item-origin, the row's fields (batch_us._entry's shape, books/<ia>/<file> url
  fallback) when plans-origin - plus plan and the reason under the key place_reason (new;
  the batch's why/gate_score stay untouched). Deterministic from stored fields.
- _apply_flags(root, store, cands, rows, item_cands, hand, built, flags) (sorted flag
  order): drops the plan (site leaves the queue when emptied); top of find_right_site
  (min_score 0.5) = T: T QUEUE-ELIGIBLE (in sites.json, dir exists, no hand doc - the
  eligible set from built/hand; NOT merely "dir exists" - see DECISIONS) -> dict-copy of
  the row with sites narrowed to [T] joins T's map; else upsert into T's item (or S's own
  item when no passing T) - SKIPPED when that item already holds the plan (zero churn);
  per-build moved set so the same (target, plan) is upserted at most once.
- build(): maps -> _place_store (None -> no-op) -> _place_flags -> _apply_flags -> entries
  via _entry; final sort and {at, entries} envelope untouched. The build never calls
  review.export and never removes a candidate from an item (the flag+drop is recomputed
  from stored fields every build - the queue stays clean forever).

**Real-data verification (temp tree: four 305 inputs + data/catalog + data/books, build()
in-process, run twice):** flags == the CLI's set exactly (15; `python3 tools/right_place.py
--all` still 324 checked / 15 flagged). Queue 116 -> 114 entries: vindomora and
windmill-hill leave entirely; the other seven flagged sites stay (devil-s-dyke keeps only
n0662_1 - the owner's Brighton case is out of the Cambridgeshire dyke's entry; bokerley-
dyke keeps n0174_1; must-not-flag set untouched). EXACTLY 5 new review-item files / 6
upserts, each with place_reason and the row's url: a-saucer-barrow-and-a-bowl-barrow-600m-
n-q17677473.earthworkenglan01allcgoog_n0558_1.json (carries n0558_1 AND n0558_2), castle-
dyke-q31112898.earthworkenglan01allcgoog_n0599_1.json, devil-s-dyke-hillfort-q17674160.
earthworkenglan01allcgoog_n0686_1.json, down-end-castle-q5302812.earthworkenglan01allcgoog
_n0285_1.json, oval-barrow-and-adjacent-bowl-barrow-220-q17672356.earthworkenglan01allcgoog
_n0557_1.json (805's rebuild must reproduce exactly these; 341 existing item files
unchanged). Second build: queue identical (ex-at) and all item files byte-identical (zero
churn). Part 1 tests pass UNMODIFIED in 0.68 s (synthetic = pure no-op; current
four-inputs-only test_fit_queue_real = no-op too). Full suite at the last run: 3 failed /
77 passed / 1 skipped = baseline.

**NEXT STEP detail - box 4 (tests/test_fit_queue.py; it already has the GUARD,
_build_synthetic_tree, _run_generator, test_fit_queue_synthetic, test_fit_queue_real):**
1. A NEW synthetic namesake test (hermetic, dead-socket, no network): its own small tree
   with a tiny data/catalog/sites.jsonl (id/qid/name/aliases/region/admin records), a
   data/books/index.jsonl (id, book, ia_id, fig, title) and a data/books/lists/<ia>.json
   (figures [{fig, title}]). Book must be in right_place.BOOK_SCOPE (use "allcroft_1908" -
   regions {england, wales}, no default state; H2 book_row requires it). Cases, one
   picture each: (a) H2 flag (caption "... near Brighton"; Brighton -> sussex through a
   catalog site's admin parish/district word_counties; source site admin county
   "Cambridgeshire") with the right site in the catalog (admin county "West Sussex" ->
   classic sussex) AND BUILT (sites.json + dir) -> candidate leaves the source entry and
   lands in the right site's entry, sites narrowed to [it]; (b) same flag, right site
   UNBUILT (no dir) -> the right site's item gains the candidate with place_reason;
   (c) flag, NO passing catalog site -> the source site's own item gains it with
   place_reason; (d) fail-open: a site whose admin county is in neither CLASSIC_UNITS nor
   IDENTITY is never flagged even with a contradicting caption; (e) a source site whose
   ONLY candidate is flagged leaves the queue entirely; (f) second run: byte-identical
   queue (ex-at) and items (steady state). test_fit_queue_synthetic stays UNMODIFIED
   (that tree must stay catalog-less: it asserts the no-op degrade) - the new case is its
   own function with its own tree.
2. test_fit_queue_real re-derived WITH the check (box 4.2): copy data/catalog/ and
   data/books/ (index.jsonl + lists/) into the temp tree; the test's independent
   derivation imports tools/right_place (stdlib) and re-runs the same two-phase logic
   over the same inputs (its own map gathering via fit_queue._candidates/_plans_rows/
   _item_candidates + right_place.site_facts/picture_facts/check_pairing/find_right_site
   + fit/review.upsert_item), then matches the generator's output: entry set, per-entry
   candidate sets, the review-item upserts in the tree (derive, never pin - 803
   precedent; with today's data: the 5 files / 6 entries above, 114 entries), checkout
   byte-identical, dead-socket GUARD stays.
3. Box 3: data/review/README.md - add "309's place_reason" to the pass-through line
   ("...203a's gate_score/why, 309's place_reason, the row's ia/file/...") + one sentence
   on what it holds (the check's reason string; written by tools/fit_queue.py's build,
   never by the page).

**Shared ground truth (re-verify at session start):**
- Worktree warning (STILL APPLIES): all work belongs in /home/agent/projects/ancient-
  works.c (branch agent/c); the three worktrees (.a, .c, main) share one repo; never
  commit in the main worktree (PITFALLS entry covers the mixup).
- The module tools/right_place.py (696 lines, stdlib, fc67bb9; on agent/c only - lands on
  main when 309 closes out): load/picture_facts/site_facts/check_pairing/find_right_site.
  Its verbatim matcher core spans lines 33-223 (17 top-level names); 805's drift test
  compares those against pipeline/books_match.py; the six iteration-95 spec deviations
  are baked in - do not "fix" them.
- Suite baseline on agent/c: 3 failed / 77 passed / 1 skipped - the 3 pre-exist on main
  (the lead's matcher-fit wiring b22a2d2/9324f8b: test_fit_provenance::
  test_line_refuses_unmarked_non_auto_doc, test_fit_queue::test_save_runs_the_one_site_
  line, test_site_done::test_site_done_line). Neither 804 nor 805 edits their
  assertions; both leave the rest green.
- The committed web/data/fit_queue.json is STALE: 117 entries vs 114 that the wired build
  now produces (the old unwired build made 116; the extra committed entry is
  shotwick-castle-q7502621, no longer built from current data; the same site is the
  orphan-platefit-doc behind the main-side test_serve/test_batch_eu failures). 805's
  rebuild fixes it; 804 never writes the file.
- Agent a (306/307) reads web/data/fit_queue.json tolerantly and must never write it; if
  their merge lands while 805's rebuild is in flight, expect driver reconciliation - flag
  any hit on this task's files in DECISIONS.
- The dropped reference spec tasks/309-place-check.md (agent a's, kept as reference) holds
  the background: the fail-open rule (an unknown place never mismatches), the --live
  Wikidata human path (pipeline/catalog_wd.py; tests never call it), "the 305 queue shape
  and tests must survive". Its data/fit_place.json committed-verdict design was
  deliberately NOT adopted (the module re-checks from stored fields on every run) - if a
  future session revives it, data/fit_place.json + tests/test_fit_place.py must be added
  to the relevant task's Touches first.

Re-read:
- tools/fit_queue.py: _place_store/_place_flags/_place_entry/_apply_flags/build - the
  wiring this session put in (uncommitted at hand-over; verify it is intact before
  building on it). Invariants: flags over pre-mutation maps; never rewrite an item that
  already holds the plan; the entry join uses a dict copy (shared plans rows are never
  mutated); the build never removes from items.
- fit/review.py: upsert_item (write-once resolved; merges by plan, same-plan replaces in
  place, new plans append; no_picture=None clears the record once candidates exist; the
  file name's lead follows candidates[0].plan and renames on change - a no-picture item
  gaining a moved first candidate gains <site>.<plan>.json); export is never called by
  the build (only the one-site line publishes web/data/review.json).
- tests/test_fit_queue.py: the GUARD (runpy + dead sockets), _build_synthetic_tree (must
  stay catalog-less: the no-op degrade), test_fit_queue_real (the box-4.2 extension
  point).
