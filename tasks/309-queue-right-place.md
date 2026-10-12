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

(2026-10-12, iteration 104, agent c - session 13 on the 309 lane. The merge of main
into agent/c is COMMITTED as cef2402 (union of 804's right-place wiring and 307ba's
propose wiring). The full suite has NOT been run since the merge - that is the next
session's first step. 805 box 1's data writes are committed (2ab6cbf); its contract
fix (fit/review.py + fit/batch_eu.py) is NOT started; boxes 2+3 not started.)

MERGE cef2402 - WHAT WAS RESOLVED (re-read if anything looks off):
- tools/fit_queue.py: union. Docstring = the 309 "And one rule more" paragraph +
  307b's propose paragraph + a merged stdlib-only paragraph (four 305 inputs +
  data/books/index.jsonl + optional catalog/books for the check; imports right_place,
  review, propose). Both sys.path inserts kept (the tools one is needed by the
  runpy.run_path guard). All 804 helpers kept; _entry_propose (307b) added after
  _entry. build() = 804's two-phase (gather cands -> flags over pre-mutation maps
  -> _apply_flags) then an entry loop: _entry(...) then the propose key appended
  AFTER "candidates" (the page's order). _entry's signature (sid, name, cands) is
  unchanged - _derive_with_check relies on it.
- tests/test_fit_queue.py: git auto-merged most; the one hunk (real test's
docstring + raw_in) resolved to the union: raw_in = [sites.json, plans.json,
  catalog/sites.jsonl, books/index.jsonl]; the duplicated tree-copy block deduped
  (books/index.jsonl = raw_in[3]; catalog, books/lists, review, platefits). I also
  extended _derive_with_check: the derived entries now carry the propose key too
  (fit_queue._entry_propose(root, sid, best plan) - same run, same inputs) so the
  `entries == expected` comparison holds against the built file. Agent a's synthetic
  (13 sites, 7 entries, propose hand-pinned) replaced my 6-site one: it is a strict
  superset (every old case present), its tree has no catalog -> check no-op, and its
  site records have no region/place -> fail-open, no flags. Agent a's per-entry
  propose derivation (propose_for on the same tree + `assert anchored` floor) sits
  next to my check-aware comparison in test_fit_queue_real. My namesake test is
  untouched: in the merged build its two surviving entries (dyke-sussex-q2/p1,
  dyke4-unknown-q30/p4) get NO propose key - their index rows have no stage-B fields
  and their sites no size_m, so propose_for raises ValueError and _entry_propose's
  try/except swallows it (verified by reading fit/propose.py L396-411).
- web/data/fit_queue.json: took ours (my 805 rebuild, 114 entries), then re-ran the
  MERGED build on the checkout -> regenerated: 114 entries + the propose keys. The
  build's item upserts wrote nothing (steady state; post-commit status was clean,
  so zero churn confirmed). How many of the 114 carry a propose key: NOT counted
  this session (main's 117 were 117/117; expect ~all of the 114) - check in the
  next session before the suite run if curious. The entry ORDER is unchanged from
  my rebuild (the build's own sort; the propose key is appended per entry, not a
  sort input).

WHAT THE NEXT SESSION DOES (in order):
1. Full suite: `.venv/bin/python -m pytest` (last full run: 124 s). EXPECT exactly
   the 3 known failures, all caused by my 805 rebuild's new item kind (items for
   unbuilt catalog sites), all passing on /tmp/baseline805 (the pre-rebuild state;
   it has no .venv, use the project's): tests/test_site_done.py::test_site_done_line
   and tests/test_fit_provenance.py::test_line_refuses_unmarked_non_auto_doc (the
   export's 5 "site not in sites.json; using the id as name" warnings break
   err == ""), tests/test_batch_eu.py::test_union_check (union_check flags the 5
   new items as orphan_items). ALL of tests/test_fit_queue.py (8 tests: synthetic,
   real, namesake, line, 2 card tests - the card tests need Chrome, present here)
   must be green: that is the merge verification. Any OTHER failure is new and
   must be diagnosed against cef2402 (the 805 box-4 contract in 307's file says
   agent a's page work reads the queue tolerantly; the entry shape is unchanged -
   the propose key is additive, after "candidates").
2. 805 box 1, part 2 - the contract fix (designed iteration 103, NOT started):
   fit/review.py export: read data/catalog/sites.jsonl (stdlib; absent file =
   degrade to today's behavior - synthetic temp trees have no catalog, so
   test_review's pinned cases keep passing - READ tests/test_review.py L191 and
   L228 first); for an item site not in sites.json: in the catalog -> use the
   catalog record's NAME as the page name and NO warning (also fixes the truncated-
   id display of the 5 new items); in neither -> keep the warning. fit/batch_eu.py
   union_check (L45-124; the orphan check ~L91-102): an item is an orphan only when
   its site is in NEITHER sites.json nor the catalog; catalog items stay out of the
   coverage counts exactly as before. No catalog in the tree -> old behavior
   byte-identical. FIRST read tests/test_batch_eu.py's temp-tree builder (tree(),
   L160-169): check whether it copies data/catalog/ - if it does, an orphan the
   test deliberately creates must be a site in NEITHER file. Add fit/review.py +
   fit/batch_eu.py to 805's Touches line (the 309 Notes' "do not touch fit/" was
   about the lead's in-flight matcher fit/matchfit.py only). Then: full suite
   (expect 0 failed), re-verify the rebuild's stability (build twice: entries
   stable, zero item writes), commit the two fit/ fixes + a re-check that the data
   files are unchanged as 805 box 1 done.
3. 805 box 2: docs/site_flow.md namesake section. Report the ACTUAL numbers:
   15 pairs over 9 sites wrong; 10 upserted into 5 NEW item files for unbuilt
   catalog right sites (a-saucer-barrow-and-a-bowl-barrow-600m-n-q17677473 [n0558_1
   + n0558_2], castle-dyke-q31112898 [n0599_1], devil-s-dyke-hillfort-q17674160
   [n0686_1 - the owner's Brighton case], down-end-castle-q5302812 [n0285_1],
   oval-barrow-and-adjacent-bowl-barrow-220-q17672356 [n0557_1]); 5 already parked
   in the source item (zero writes); queue 117 -> 114 (left: vindomora, windmill-
   hill, shotwick-castle; narrowed: alauna, bokerley-dyke, castle-neroche, clun-
   castle, coria, devil-s-dyke [best now n0662_1], eaton-socon); ZERO moves into
   built sites (none of the 15 rows' top right site is built). How the check
   decides: stored fields only (explicit county/state word; towns resolved to
   classic counties through the catalog; fail open); --live is a human re-run,
   never in the build. Agent a's 306/307 also touch this file: APPEND a clearly
   separate section, do not reflow theirs (it has grown since: 307ba added a
   Ready-to-fit section; read the file first).
4. 805 box 3: tests/test_right_place_drift.py (hermetic, stdlib, no network): for
   each of the 17 top-level names between tools/right_place.py's VERBATIM markers
   (US_STATES, ABBR, UK_ABBR, UK_COUNTIES, GENERIC, norm, name_keys, tokens,
   place_of, site_place, site_toks, name_lookup_keys, row_inputs, score_candidate,
   BOOK_SCOPE, PLACE_WORDS, phrases) extract the block from both that file and
   pipeline/books_match.py, assert byte-identical. Extraction rule (verified both
   files iteration 103): a block = from the name's start line ("^NAME = " for
   assignments, "^def NAME(" for functions) to the end of its logical statement -
   assignments: consecutive non-blank lines; functions: up to the first non-blank
   line at column 0. The test must PASS before any future drift. SUFFIX sits
   inside right_place's verbatim region but is NOT in the 17-name list - the
   box's list governs. Do NOT edit pipeline/books_match.py (source of truth; a
   real drift is fixed there) - re-check `git log --oneline -5 -- pipeline/
   books_match.py` first (it is agent a's lane only if 307bb/306 touch it).
5. Tick 805's boxes, update 805's hand-over, then the driver returns 309 for its
   three carved-box ticks (box 2's "Devil's Dyke not paired" is proven by the
   committed queue: n0686_1 is on the hillfort's review item, off the dyke's
   entry).

THE 805 REBUILD (committed in 2ab6cbf; still the ground truth): queue 117 -> 114
(107 entries byte-identical, 7 narrowed, 3 left); 15 flags -> 10 upserts into the
5 new item files above + 5 skips (target item already holds the plan - the
intended steady state); web/data/review.json 335 -> 340 open of 346; the six
c5250a4 write-once resolved records untouched; the moved-set dedup means
windmill-hill's three flags write nothing (eaton-socon's identical (target, plan)
pairs sort first). The 5 new items are all resolved: None, no_picture: None.

DATA QUALITY NOTES (for DECISIONS / the lead / agent a's 306, NOT mine to fix -
web/data/sites.json is agent a's lane): bokerley-dyke-q891218's sites.json place
is "Dorset, England" though the catalog says Cambridgeshire (Bokerley Dyke IS in
Cambridgeshire) - the check (catalog-driven) flagged correctly, only the reason
string's vs-side inherits the bad sites.json place (castle-dyke's item reads
"Aysgai-th, Yorks, Aysgarth vs Dorset, England"); vindomora-q7932358's place is
"County Durham, England" though Vindomora is Northumberland.

WORKTREE (still true): commit only in /home/agent/projects/ancient-works.c
(branch agent/c); data/raw is a symlink into the shared store - the queue build
never opens images (sizes come from the json files), so a rebuild cannot write
through it; never run the batch/line tools in the main worktree.

Re-read (when touching the wiring again):
- tools/fit_queue.py: _apply_flags <-> tests/test_fit_queue.py: _derive_with_check
  must stay in lockstep (same two-phase, sorted flag order, `moved` set, pristine-
  item skip, eligible = built minus hand, and NOW the propose key attached to the
  derived entries). A change to one needs the other.
- fit/propose.py: propose_for RAISES (ValueError) when it cannot anchor; only
  _entry_propose's try/except turns that into "no propose key". Never let a raw
  propose_for call reach a row it cannot anchor.
- fit/review.py: upsert_item (write-once resolved; merges by plan; the file name's
  lead follows candidates[0].plan) and export (never called by the build).
- The six baked-in right_place spec deviations (DECISIONS, iteration 95) are
  pinned by the namesake test's outcomes - changing any rule changes the pinned
  bytes.

Carve state: 309 box 1 (wiring) = 804 DONE; box 3 (namesake tests) = 804 box 4
DONE; box 2 (site_flow report + rebuild) = 805: box 1's data writes committed
(2ab6cbf) and re-stamped by the merge build (cef2402); box 1's contract fix
(fit/review.py export + fit/batch_eu.py union_check, catalog-aware) NOT STARTED;
box 2 (docs/site_flow.md section) NOT STARTED; box 3 (tests/test_right_place_drift.py)
NOT STARTED. When 805 is done the driver returns 309 and I tick its three carved boxes.

