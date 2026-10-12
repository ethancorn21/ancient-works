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

(2026-10-12, iteration 101, agent c - session 10 on 309's lane. Boxes 1+2 (the two-phase
wiring + dispositions) are IN tools/fit_queue.py, verified on real data (iteration 100)
and committed by the driver as 077ccb8. Box 4 (tests) is now WRITTEN into
tests/test_fit_queue.py but UNCOMMITTED and NOT YET RUN - one known bug to fix first
(dict-unpack in _build_namesake_tree, in 309's hand-over), then run the two fast tests,
then the full suite, then box 3 (the README note). 805 follows. The full current state,
the written test's design, the verification evidence and the exact next steps are in
PARENT 309's hand-over - read it first. Condensed state here:)

Box state: 1 + 2 done (committed 077ccb8). 3 (data/review/README.md place_reason note)
not started. 4 (tests) written, unrun. 5 (no new failures) last verified at baseline
(3 failed / 77 passed / 1 skipped); re-run after box 4 lands -> expect 3 failed /
78 passed / 1 skipped.

What is in tools/fit_queue.py (committed; re-read before touching):
_header docstring namesake-rule paragraph; sys.path.insert of ROOT/tools and ROOT/fit
before `import right_place` / `import review` (noqa E402 - required: runpy.run_path
leaves the script dir off sys.path under the test GUARD; PITFALLS entry exists);
_site_records/_place_store (None when catalog AND index AND lists all empty = no-op
degrade)/_place_flags (flags over PRE-MUTATION maps; one site_facts per site, picture
facts per candidate)/_item_candidate/_place_entry (stored fields + plan + place_reason;
plans-origin: row fields with url fallback books/<ia>/<file>; item-origin: the item
candidate's dict copy)/_apply_flags (sorted flag order: drop; top of find_right_site
min_score 0.5 = T; T eligible (in sites.json + dir + no hand) -> dict-copy of the row
with sites narrowed joins T's map; else upsert into T's item or S's own item; SKIPPED
when the pristine item already holds the plan; per-build moved set)/build() two-phase.
The build never calls review.export and never removes a candidate from an item.

What is in tests/test_fit_queue.py now (working tree, UNCOMMITTED):
- `_derive_with_check(root)`: independent re-derivation of the wiring (fit_queue input
  readers + right_place API + fit_queue._place_entry/_entry/_best_key; two-phase,
  sorted flags, moved set, pristine-item skip) -> (expected entries, upserts) or
  (None, {}) for the no-op degrade.
- test_fit_queue_real: copies data/catalog/ + data/books/ (index.jsonl + lists/) into
  the temp tree; asserts the FULL entry list equals _derive_with_check's; re-applies
  the derived upserts to a second pristine copy via fit/review.upsert_item and
  byte-compares every item file; checkout-untouched check extended to the new inputs;
  old entry-set derivation kept as the no-op-degrade branch.
- test_fit_queue_namesake + _build_namesake_tree/_namesake_row/_namesake_item: the
  Brighton-vs-Cambridgeshire synthetic tree, cases (a) move into built right site,
  (b) upsert into unbuilt right site's item, (c)+(e) source-own item + site leaves
  queue, (d) fail-open unknown county, (f) second run byte-identical. Item files
  byte-pinned (the expected dict's key order must match _place_entry's).
- KNOWN BUG: `for s, _ in sites:` in _build_namesake_tree unpacks dicts -> ValueError;
  fix to `for s in sites: (wd / "sites" / s["id"]).mkdir(parents=True)` before running.

Real-data verification (iteration 100, still the ground truth for 805): flags == the
CLI's 15 exactly (324 checked); queue 116 -> 114 (vindomora + windmill-hill leave;
devil-s-dyke keeps only n0662_1 - the Brighton case is out); exactly 5 new item files
/ 6 upserts, each with place_reason + row url: a-saucer-barrow-and-a-bowl-barrow-600m-
n-q17677473.earthworkenglan01allcgoog_n0558_1.json (n0558_1 AND n0558_2), castle-dyke-
q31112898.earthworkenglan01allcgoog_n0599_1.json, devil-s-dyke-hillfort-q17674160.
earthworkenglan01allcgoog_n0686_1.json, down-end-castle-q5302812.earthworkenglan01allc
goog_n0285_1.json, oval-barrow-and-adjacent-bowl-barrow-220-q17672356.earthworkenglan01
allcgoog_n0557_1.json; 341 existing item files unchanged; second build byte-identical
(zero churn). 805's rebuild must reproduce exactly these.

Shared ground truth (re-verify at session start):
- All work belongs in /home/agent/projects/ancient-works.c (branch agent/c); the three
  worktrees share one repo; never commit in the main worktree (PITFALLS).
- tools/right_place.py (696 lines, stdlib, committed fc67bb9 on agent/c, lands on main
  when 309 closes): load/picture_facts/site_facts/check_pairing/find_right_site; the
  verbatim matcher core spans lines 33-223 (17 top-level names); the six iteration-95
  spec deviations are baked in - do not "fix" them.
- Suite baseline on agent/c: 3 failed / 77 passed / 1 skipped - the 3 pre-exist on
  main (the lead's matcher-fit wiring: test_fit_provenance::
  test_line_refuses_unmarked_non_auto_doc, test_fit_queue::
  test_save_runs_the_one_site_line, test_site_done::test_site_done_line). Never edit
  their assertions; leave the rest green.
- The committed web/data/fit_queue.json is STALE: 117 entries vs 114 the wired build
  produces (the extra is shotwick-castle-q7502621, also behind the main-side
  test_serve/test_batch_eu failures). 805 fixes it; 804 never writes it.
- web/data/sites.json records must carry "region" (capitalized: "England", "Wales",
  "US", ...) for the check to bucket the site - without it H1/H2 never fire
  (PITFALLS entry added this session).
- Agent a (306/307) reads web/data/fit_queue.json tolerantly and must never write it;
  if their merge lands while 805's rebuild is in flight, expect driver reconciliation.
- The dropped reference spec tasks/309-place-check.md (agent a's) holds the fail-open
  rule background; its data/fit_place.json committed-verdict design was NOT adopted.

Re-read:
- tools/fit_queue.py: _place_store/_place_flags/_place_entry/_apply_flags/build -
  invariants: flags over pre-mutation maps; never rewrite an item that already holds
  the plan; the entry join uses a dict copy (shared plans rows never mutated); the
  build never removes from items.
- fit/review.py: upsert_item (write-once resolved; merges by plan, same-plan replaces
  in place, new plans append; no_picture=None clears once candidates exist; the file
  name's lead follows candidates[0].plan and renames on change - a no-picture item
  gaining a moved first candidate gains <site>.<plan>.json); export never called by
  the build.
- tests/test_fit_queue.py: _build_namesake_tree (fix the dict-unpack bug),
  test_fit_queue_namesake (byte-pinned items), _derive_with_check (the mirror of the
  wiring - keep it in lockstep with _apply_flags if either changes),
  test_fit_queue_real (the no-op-degrade branch must stay).
