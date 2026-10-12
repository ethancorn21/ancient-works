Status: done
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
- [x] build() in tools/fit_queue.py: for every built site without a hand fit, each candidate of
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
- [x] Disposition of a flagged candidate (source site S, candidate P, facts F):
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
- [x] data/review/README.md: the candidate pass-through line names the new extra (the 309
      place-check reason, the 203a gate_score/why pattern; the page's Review list shows it in
      307c, not here).
- [x] tests/test_fit_queue.py (hermetic, dead-socket guard, no network):
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
- [x] The three pre-existing main-side failures (test_fit_provenance::
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

(2026-10-12, iteration 102, agent c - session 11 on the 309 lane. 804 is DONE: all
five boxes verified and ticked. The remaining work in the 309 lane is 805 (the
rebuild); its next steps and the post-merge baseline are in PARENT 309's hand-over.)

What is in tools/fit_queue.py (committed 077ccb8, verified this session):
- _site_records / _place_store (None when catalog AND index AND lists all absent =
  no-op degrade) / _place_flags (flags over PRE-MUTATION maps; one site_facts per
  site, picture facts per candidate) / _item_candidate / _place_entry (stored fields
  + plan + place_reason; plans-origin: row fields with url fallback
  books/<ia>/<file>; item-origin: the item candidate's dict copy) / _apply_flags
  (sorted flag order: drop; top of find_right_site min_score 0.5 = T; T eligible
  (in sites.json + dir + no hand) -> dict-copy of the row with sites narrowed joins
  T's map; else upsert into T's item or S's own item; SKIPPED when the pristine
  item already holds the plan; per-build moved set) / build() two-phase. The build
  never calls review.export and never removes a candidate from an item.

Tests (all verified running, iteration 102): tests/test_fit_queue.py 6/6 pass in
52 s - synthetic (unmodified, no-op degrade pinned), namesake (new: every
disposition byte-pinned, fail-open, zero churn), real (full entry list + item
upserts re-derived independently through right_place's API and fit/review.
upsert_item, byte-compared; checkout byte-identical). Fixes made to the written
code this session: the namesake tree's dict-unpack, two missing mkdirs
(data/books/lists; data/books before the copy2), and a sorted glob for the
item-file list (Path.glob is filesystem-ordered). data/review/README.md names
place_reason in the pass-through line and the Rules list (box 3; no test pins
that text).

Suite: fully green at session end (83 passed / 1 skipped / 0 failed) - the three
pre-existing main-side failures were fixed main-side (lead's matcher-fit commits,
driver merge 9be7094); their assertions were never edited here.

Re-read (only if the wiring changes again; 805's rebuild re-runs this code on the
real checkout):
- tools/fit_queue.py: _apply_flags <-> tests/test_fit_queue.py: _derive_with_check
  must stay in lockstep (same two-phase, sorted flag order, moved set,
  pristine-item skip, eligible = built minus hand).
- fit/review.py: upsert_item (write-once resolved; merges by plan; the file
  name's lead follows candidates[0].plan and renames on change - a no-picture
  item gaining a moved first candidate gains <site>.<plan>.json); export is
  never called by the build.
- web/data/sites.json records must carry "region" (capitalized) for the check to
  bucket a site (PITFALLS).
