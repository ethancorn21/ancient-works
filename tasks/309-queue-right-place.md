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

(2026-10-12, iteration 101, agent c - session 10 on the 309 lane. The driver handed me 309
again; 804 is in-progress in this lane. Done this session: 804 box 4 (the tests) WRITTEN into
tests/test_fit_queue.py - UNCOMMITTED in the working tree, the harness saves it; NOT yet run
(context limit hit before the first pytest run). Box 3 (the data/review/README.md note) NOT
started. Everything below the line is the state of the 804 work in detail.)

State of 804's five boxes:
1. two-phase wiring in tools/fit_queue.py - IN, verified (iteration 100), committed by the
   driver as 077ccb8 "[driver] uncommitted work after iteration 100" (131 insertions).
2. dispositions - IN, verified with 1. Same commit.
3. data/review/README.md pass-through note - NOT STARTED (see next step 4 below).
4. tests/test_fit_queue.py - WRITTEN, not yet run (see below).
5. no new failures vs baseline - last full run (iteration 100): 3 failed / 77 passed / 1
   skipped = baseline (the three pre-existing main-side failures). Re-run after the new
   tests land: expect 3 failed / 78 passed / 1 skipped (one new test function added).

What is in tests/test_fit_queue.py now (working tree, uncommitted):
- Module docstring: new lines for test_fit_queue_namesake; the test_fit_queue_real line
  now says the catalog/books stores are copied so the check runs for real.
- `_derive_with_check(root)` (new, after `_h`): the 804 orchestration restated
  independently - fit_queue's own input readers (_plans_rows/_item_candidates/
  _hand_sites/_built_sites/_candidates) + right_place's committed API (load/site_facts/
  picture_facts/check_pairing/find_right_site) + fit_queue._place_entry/_item_candidate/
  _entry/_best_key. Two-phase: flags over PRE-MUTATION maps, then drop/move/upsert in
  sorted(flags) order with the same `moved` set and same pristine-item skip rule as the
  wiring. -> (expected entries in build order, {target: [entries in processing order]})
  or (None, {}) for the no-op degrade.
- test_fit_queue_real REWRITTEN: raw_in/before/after now include data/catalog/sites.jsonl
  + data/books/index.jsonl + data/books/lists/ (the checkout-untouched check extended);
  the temp tree copies all of them (shutil.copytree catalog; copy2 index.jsonl;
  copytree lists - the .map.json files ride along, load() ignores them); the entry set is
  now the FULL list `entries == expected` from _derive_with_check (not just the set);
  the upserts are re-applied to a SECOND pristine copy (tmp_path/"derive") through
  fit/review.upsert_item (one entry per call, the module's call shape) and every item
  file is byte-compared between the generator's tree and the derive tree (file set +
  bytes). The old entry-set derivation survives as the no-op-degrade branch.
- test_fit_queue_namesake (new, "Part 1b") + helpers _build_namesake_tree/_namesake_row/
  _namesake_item: five built sites (allcroft_1908 book rows p1-p4, ia "allcroft1908book",
  lists file with the printed captions) + six catalog records. Cases: (a) p1 caption
  "The Devil's Dyke Camp, near Brighton" (H2: brighton->sussex) vs dyke-cambs-q1
  (Cambridgeshire) -> flagged, top right site dyke-sussex-q2 (West Sussex, BUILT) ->
  candidate joins q2's entry, sites narrowed, q1 leaves; (b) p2 "Bokerley Dyke, near Hove"
  vs dyke2-cambs-q10 -> flagged, top right site dyke2-sussex-q11 (in catalog, NOT in
  sites.json -> unbuilt) -> q11's item gains p2 with place_reason, q10 leaves; (c)+(e) p3
  "Wickham Camp, near Hove" vs dyke3-cambs-q20 -> flagged, NO passing right site (the
  only other Wickham Camp fails the county gate) -> q20's own item gains p3, q20 (its
  only candidate) leaves; (d) p4 "Wickham Camp, in Kent" (explicit word) vs
  dyke4-unknown-q30 (county "Xshire" in neither CLASSIC_UNITS nor IDENTITY) -> never
  flagged (fail open), q30 keeps it; (f) second generator run: queue identical ex-at, item
  files byte-identical (zero churn). Item files byte-pinned via _namesake_item (the
  expected dict must match the module's key order: book/ia/file/title/label/size/
  map_box/cite/url/view/ref/plan/place_reason).

KNOWN BUG TO FIX FIRST (found while reviewing the written code): in
_build_namesake_tree, `for s, _ in sites:` unpacks a list of DICTS -> ValueError at tree
build time. Must become `for s in sites: (wd / "sites" / s["id"]).mkdir(parents=True)`.

Verification evidence this session (throwaway /tmp/proto804/proto.py, not in repo -
rebuild it from the notes if needed): the exact synthetic tree above, run through
right_place's API, flags exactly as the test pins (p1/p2/p3 flagged with reasons "same
name, other place: near Brighton vs Cambridgeshire" / "near Hove vs Cambridgeshire" /
"near Hove vs Cambridgeshire", p4 not flagged; find_right_site tops: q2 0.917 / q11 1.25 /
none); then the real CLI on that tree twice: run 1 -> queue [q2 (p1, sites narrowed),
q30 (p4)] exactly, items dyke2-sussex-q11.p2.json + dyke3-cambs-q20.p3.json each with the
place_reason and url fallback "books/allcroft1908book/p21x.jpg"; run 2 -> identical queue
and items (zero churn). Baseline CLI still 324 checked / 15 flagged.

PITFALLS (new, add on commit): web/data/sites.json records MUST carry "region"
("England"/"Wales"/"US"/... - capitalized in the real file) for the right-place check:
site_facts buckets the region; a synthetic tree without it buckets "other" and H1/H2
never fire (looked like "the check is broken" - the flag is silently off).

EXACT NEXT STEP (next session, same lane):
1. Fix the unpack bug in _build_namesake_tree (above).
2. Run the two new/changed tests fast:
   `.venv/bin/python -m pytest tests/test_fit_queue.py::test_fit_queue_namesake \
    tests/test_fit_queue.py::test_fit_queue_real -q`
   (the .venv exists in this checkout; the file also holds the slow Part-2 line test
   ~23-180 s and Part-3 browser tests - skip those in the fast loop).
3. Expected failure modes if the real test fails: (i) `entries == expected` diff ->
   print the first differing entry, compare against the module's _apply_flags (the
   `moved` set, the pristine-item skip, eligible = built minus hand); (ii) item-file
   bytes differ -> read the generator's file and the derive file, they diverge in key
   order only when _place_entry's dict order changed (it did not this session);
   (iii) namesake item bytes differ -> copy the actual key order into _namesake_item.
4. Then run the WHOLE file once (`... pytest tests/test_fit_queue.py -q`) and then the
   full suite (`.venv/bin/python -m pytest -q`): must be 3 failed (the pre-existing
   main-side trio: test_fit_provenance::test_line_refuses_unmarked_non_auto_doc,
   test_fit_queue::test_save_runs_the_one_site_line, test_site_done::test_site_done_line)
   / 78 passed / 1 skipped.
5. Then 804 box 3: data/review/README.md - in the Item-shape JSON block's pass-through
   line ("...202's ground/scale_m_px/rot_deg/scale_source/note, 203a's gate_score/why,
   the row's ia/file/book/label/cite/map_box/view/size when known); the page and export
   ignore unknown keys") add ", 309's place_reason" after the gate_score/why mention,
   and add one bullet to the Rules list: place_reason holds the check's reason string
   ("same name, other place: <caption place> vs <site place>"), written by
   tools/fit_queue.py's build when the right-place check moves a candidate; the page's
   Review list shows it (307c) and neither the page nor a human save writes it.
6. Then tick 804 boxes 1-5 (all verified), commit ("804: ..."), and take 805 (the
   rebuild of web/data/fit_queue.json + data/review/ + the site_flow report + the
   verbatim-core drift test; its hand-over has the exact 5 item files / 6 upserts the
   rebuild must reproduce - the Brighton case leaves the Cambridgeshire dyke's entry).

Carve state: 309 box 1 (wiring) = 804 done 4/5 (box 3 pending); 309 box 2 (site_flow
report) = 805 not started; 309 box 3 (namesake tests) = 804 box 4 (written, unrun).
When 804+805 are done the driver returns 309 and I tick its three carved boxes.


