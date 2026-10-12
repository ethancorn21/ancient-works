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

(2026-10-12, iteration 99, agent c - session 8 on 309's lane; first session of 804. The driver
handed me 309 (the split parent) again - 804 still was not in Next-open-tasks - so I started
804 in the owner lane (it is my subtask; the module fc67bb9 is on my branch) and set it
in-progress. Step done: the AGENTS.md refactor-first commit - build() now gathers the per-site
candidate map first and derives each entry through the new _entry() helper; behavior-neutral,
committed on its own (the old build, taken from git show HEAD:tools/fit_queue.py, and the new
build run on the same temp tree produced identical 116-entry outputs; test_fit_queue_synthetic
and test_fit_queue_real pass unmodified in 0.69 s).

Box state: 1 (the two-phase wiring) and 2 (the dispositions) - only their prerequisite (the
refactor) is in; the wiring itself is NOT written. 3 (the README note), 4 (the tests),
5 (no new failures) - not started.

NEXT STEP (next session, this lane): write boxes 1+2 in tools/fit_queue.py:
- imports: sys.path.insert(0, str(ROOT / "tools")) then import right_place; and
  sys.path.insert(0, str(ROOT / "fit")) then import review (the site_done.py pattern). Needed
  because the test GUARD runs the script via runpy.run_path, which does NOT put the script
  dir on sys.path (new PITFALLS entry, verified this session: the sibling import fails with
  ModuleNotFoundError under runpy, works under plain python3).
- _place_store(root): right_place.load(root); return None when catalog, index AND lists are
  all empty (the no-op degrade; keeps 305's synthetic tree - no catalog/books - byte-identical).
- _place_flags(root, rp_data, cands_by_site): per site in the map: its record from sites.json
  (build the by-id map here or pass it in), one right_place.site_facts, then per candidate
  right_place.picture_facts + check_pairing; returns {(sid, plan): reason}. All decisions are
  over the PRE-MUTATION maps (box 1's two-phase rule: a move into a site must never feed that
  site's own flag decision in the same build).
- _apply_flags(root, rp_data, cands_by_site, flags): for each (sid, plan, reason): drop the
  plan from cands_by_site[sid]; right_place.find_right_site(rp_data, facts, exclude=sid):
  top T built (web/data/sites/<T>/ exists) -> cands_by_site.setdefault(T, {})[plan] = the row
  with sites narrowed to [T] (the plans row as-is; an item candidate synthesized via
  _synth_row from the item's stored fields); T unbuilt -> review.upsert_item(root, T,
  [entry]) where entry = the candidate's stored fields + the reason; no passing T ->
  review.upsert_item into sid's own item (skip the upsert when that item already holds the
  plan: the intended steady state - re-flagged every build, never churned). Build the upsert
  entry deterministically from stored fields + the reason key so a same-value re-upsert is
  byte-identical (upsert_item replaces a same-plan entry in place; resolved stays write-once;
  the file-name lead follows candidates[0].plan - a moved candidate becoming lead renames the
  item file; a no-picture item gaining a first candidate gains <site>.<plan>.json and its
  no_picture record clears).
- build(): cands_by_site (today's shape) -> _place_flags -> _apply_flags -> entries via
  _entry. Keep the final sort and the {"at", "entries"} envelope untouched (the 305 contract;
  the page reads the file tolerantly).
Then: run the part-1 tests (they must pass as today - the synthetic tree has no catalog/books,
so the check is a no-op there), and re-run `python3 tools/right_place.py --all`: it must still
flag the same 15 pairings (the build's flags and the CLI's must agree on identical inputs).
Session after that: box 4 (the new synthetic namesake test + the real-tree re-derivation with
data/catalog and data/books copied in) and box 3 (the data/review/README.md pass-through note
naming the reason extra, the 203a gate_score/why pattern).

Facts this session:
- runpy.run_path does not put the script dir on sys.path (new PITFALLS, Python section) - the
  wiring's imports must insert tools/ and fit/ themselves; right_place's own main() already
  does this for fit_queue.
- The committed web/data/fit_queue.json is STALE: 117 entries, but the current data builds 116
  (old and new code agree: 116) - the extra committed entry is shotwick-castle-q7502621, no
  longer built from current data (the same site is the orphan-platefit-doc behind the
  main-side failures test_serve::test_platefits_docs_match_sites / test_batch_eu). 805's
  rebuild fixes the committed file; 804 never writes it.
- The 15-flag module baseline (324 pairings) stands; the full list is in 309's hand-over.
- fit/review.upsert_item(root, site_id, entries, no_picture=None): merges by plan (same-plan
  replaces in place, new plans append); no_picture=None keeps an existing no-picture record, a
  non-empty entries list clears it (README: once candidates exist it is null); resolved is
  write-once; the lead (candidates[0].plan) drives the file name and renames on change.

Re-read:
- tools/fit_queue.py: build / _entry / _candidates / _synth_row - the wiring's insertion
  points; the stdlib-only contract (owner's Mac, no PIL, no pipeline/ imports).
- tools/right_place.py: load (all stores optional), site_facts (needs the full site record:
  id/name/region/place), picture_facts, check_pairing, find_right_site (min_score 0.5); the
  docstring states the fail-open rules and the six baked-in spec deviations - do not "fix"
  them.
- fit/review.py: upsert_item (as above); export is never called by the build (only the
  one-site line publishes review.json).
- tests/test_fit_queue.py: the GUARD (runpy + dead sockets), _build_synthetic_tree (the
  no-op-degrade tree - must stay catalog-less), test_fit_queue_real (the box-4.2 extension:
  copy data/catalog + data/books/index.jsonl + data/books/lists into the temp tree and
  re-derive WITH the check).
