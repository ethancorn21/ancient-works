Status: in-progress
# 307ba: Open the map - the queue carries the proposal, and place mode opens ON the works
Depends on: 307a, 220
Touches: fit/propose.py, tools/fit_queue.py, web/fitkit.js, web/index.html, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md, tasks/220-review-page-reexport.md (my own filing - kept in sync with the 309 split)

## Goal
Parent 307 (and 307b) boxes 1-2, as renumbered there. The "Ready to fit" queue file carries a
starting placement for each entry (the proposal fit/propose.py already computes: the anchor
mapping the picture's panel centre onto the site at the recorded scale and rotation, re-emitted
as 3-5 page-px -> lon/lat pairs), and opening a queue site with a proposal puts the drawing ON
the map before any clicking: the map flies to the site's own box, the site's earlier overlays
are hidden, the ink appears at the anchor, and closing brings everything back exactly as it was.
A site or plan without a proposal opens exactly as today (the three-point flow, byte-identical -
305 part 3 pins it). The owner's words: "when I go to place the plan onto the map it already
needs to be overlaid onto the map ... the overlay that's already there doesn't disappear from
the map ... As soon as you go into that place mode the already placed overlay needs to go."

## Acceptance criteria
- [x] The queue file carries the proposal: every entry whose best row admits one gets
      propose: {pairs, scale_m_px, rot_deg, scale_source, coarse, note} computed by
      fit/propose.propose_for (bar scale where recorded, ratio at the book's ppi, the
      site-size fallback, the north arrow where trustworthy). A row the proposal cannot
      anchor (no size, no size_m, no stage-B row) gets no propose, and the page falls back
      to the existing three-point flow for it. tools/fit_queue.py stays stdlib-only
      (fit/propose.py is); the committed web/data/fit_queue.json is regenerated (all 117
      current entries anchor: 20 bar, 4 ratio, 93 picture_size).
- [x] fit/propose.py gains an optional root (default: this checkout): its data loaders read
      from it and its cache is keyed by it, so the generator and the tests run it against a
      temp tree; every existing 2-arg caller (batch_us, inkfit, the tests) and
      tests/test_propose.py's golden file stay green unchanged.
- [x] tests/test_fit_queue.py part 1: the synthetic tree gains stage-B index rows and
      site sizes covering every path (a bar + trustworthy north arrow, a ratio without a
      recorded ppi -> the site-size fallback, a no-scale site without size_m -> no propose,
      a sizeless row -> no propose, an item candidate with no index row -> no propose);
      the propose field is checked against the same propose_for called on the tree, plus
      hand-pinned constants. The real test derives per-entry admissibility (never a pinned
      count) and checks presence/equality/key order. Parts 2-3 are untouched and stay green.
- [x] Opening a queue site with a proposal (the card's "Place the drawing", or the site
      panel's "Place an old plan" when the site's queued plan is the one picked): the map
      flies to the site's box (its four corners) centred, before the drawing appears; while
      place mode is open, the site's earlier overlay (the dep-* fitted drawing or survey
      sheet applyDep was showing) is hidden; on close (back button, Cancel, or saving) it
      comes back exactly as it was (same depiction selected, same ground). web/fitkit.js is
      a new extension in the fitqueue/review pattern (loads after them, wraps openPlan last
      in the chain and endFit; the <style> injection the pattern names stays out until
      307bb's gestures need one - box 4 adds no visible UI, recorded in DECISIONS;
      _fk-prefixed saved names);
      web/index.html changes by the one script tag alone; web/fitqueue.js stays
      byte-identical.
- [x] docs/site_flow.md's "Ready to fit" section: the entry's new propose field (what it is,
      where the anchor comes from, the fail-open to the three-point flow). The full place-mode
      section (gestures, save, screenshots) is 307bb/307c's.

## Notes
- The full box-1 design and the page-side design sketch (anchor model, wrap points, hide/
  restore, the no-propose byte-identity rule) are in the parent 307b's ## Hand-over and the
  2026-10-12 307b DECISIONS entry (iteration 110) - implement from there, they are precise.
- Agent c's 309 is SPLIT (on agent/c; main still shows it open) into 804 (the right-place
  wiring in tools/fit_queue.py) and 805 (the rebuild of the committed queue/review data;
  depends on 804): expect their merge of build() and the queue file; keep the propose wiring
  localized (one helper, one key per entry, docstrings) so the merge stays trivial - the
  full recipe is in the hand-over. 805's in-run full review export subsumes my 220 filing.
- The stage-B row shape: data/books/index.jsonl (scale_text, blank_boxes[{kind:"scale_bar",
  box}], north_angle_deg, north_arrow, map_box, full_size). fit/ has no __init__.py; import
  via sys.path.insert(0, str(ROOT / "fit")) like tools/site_done.py:43.
- Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-12, iteration 120, agent a - still WAITING; re-verified, no code change. New this
iteration: agent/c's snapshot advanced - 804's two-phase wiring is WRITTEN and verified on
real data, so the merge recipe below is re-pinned to that actual code.)

**Wait state (verified by running):** main still cf29be2 (no 804/805/309 commit on it),
`git show main:web/data/review.json | md5sum` = b6506007 (the stale 340-open-of-341 page),
`git log agent/a..main` empty (nothing to sync). My branch's code state is byte-identical
to the one the full suite verified at iteration 119 (ffd88ab..HEAD touches only driver
bookkeeping: PROGRESS/DECISIONS/DECISIONS-archive) -> the 3 stale-page failures stand
unchanged; no suite re-run this session, no re-claim (it would fail the same way).

**What changed on agent/c since iteration 119 (read via `git show agent/c`, NOT merged):**
- New commits 7fd3ef5 ("804/309: hand-over - boxes 1+2 (the two-phase right-place wiring)
  in and verified on real data; code uncommitted (harness-saved); next: box 4 tests + box 3
  README note, then 805"), f746c04 (its DECISIONS entry) and 077ccb8 ([driver] uncommitted
  work = the wiring: tools/fit_queue.py +131/-5). 804's remaining steps: commit the wiring,
  box 4 (tests), box 3 (README note), then 805 (the rebuild). 309's closure - hence my 220
  and my re-claim - is still ahead.
- The FINAL build() shape (agent/c:tools/fit_queue.py): rows/item_cands/hand/built ->
  `cands` map gathered over `built` -> `_place_store(root)` (right_place.load; every store
  optional - a missing file stays empty and the check degrades to a no-op) ->
  `_place_flags` (one site_facts per site, check_pairing per candidate, over PRE-MUTATION
  maps) -> `_apply_flags` (sorted flag order: drop the plan; the top of find_right_site
  (min_score 0.5) = T is QUEUE-ELIGIBLE (in sites.json + dir exists + no hand doc) -> a
  copy of the row (sites narrowed to [T]) joins T's map; else upsert into T's (or the
  source's) review item with place_reason; skipped when that item already holds the plan)
  -> `entries = [_entry(sid, name, cands[sid]) for sid, name in built if sid in cands]`
  -> `entries.sort(...)` -> the {at, entries} envelope. New helpers: _site_records,
  _place_store, _place_flags, _item_candidate, _place_entry, _entry (the entry dict, no
  propose key yet).
- 804's measured real-data verification (temp tree, build in-process, run twice): flags ==
  the CLI's set exactly (15; `python3 tools/right_place.py --all` still 324 checked /
  15 flagged); queue 116 -> 114 entries (vindomora and windmill-hill leave entirely;
  devil-s-dyke keeps only n0662_1 - the owner's Brighton case; bokerley-dyke keeps
  n0174_1; the must-not-flag set untouched); EXACTLY 5 new review item files / 6 upserts,
  each with place_reason (a-saucer-barrow-...-n0558_1 [carries n0558_1 AND n0558_2],
  castle-dyke-...-n0599_1, devil-s-dyke-hillfort-...-n0686_1, down-end-castle-...-n0285_1,
  oval-barrow-...-n0557_1); 341 existing item files unchanged; second build
  byte-identical (zero churn). 804's own FULL suite run with the wiring in: 3 failed /
  77 passed / 1 skipped = its baseline (the same 3 main-side stale-page failures) - i.e.
  parts 2-3, whose full-tree fixtures DO copy data/catalog and therefore run the live
  check, are empirically green with the wiring.
- NEW DEPENDENCY FACT: `tools/right_place.py` exists ONLY on agent/c (checked: missing on
  main AND agent/a). The merged tools/fit_queue.py imports it unconditionally, so the
  driver's sync of the 309 chain into my branch must bring the module file together with
  the rewired fit_queue.py - one atomic step; never cherry-pick one without the other.
  right_place.load degrades gracefully (catalog/index/lists each optional; missing ->
  empty -> no flags), which is why the no-catalog temp trees (my synthetic; my real test's
  copy list, which takes index.jsonl but not data/catalog) stay pure no-ops, while the
  full-tree fixtures (parts 2-3, 805's rebuild) run the live check.

**Merge recipe (the next session that sees 804/805 on main executes it) - RE-PINNED to the
actual code above:**
- tools/fit_queue.py: take 804's file as the base. (a) Imports: keep THEIR block
  (`sys.path.insert(0, str(ROOT / "tools"))` + `sys.path.insert(0, str(ROOT / "fit"))`,
  then `import right_place` / `import review`, both noqa E402) and ADD my line
  `import propose as _propose  # noqa: E402` after it; DROP my separate
  `sys.path.insert(0, str(ROOT / "fit"))` (their block already inserts ROOT/fit - one
  insert per dir, three imports; the runpy PITFALL is why they self-insert). (b) Keep MY
  `_entry_propose(root, site_id, plan)` helper verbatim (my file line 182: propose_for in
  try/except -> None fail-open, six keys in entry order, "ground" dropped). (c) build():
  insert the POST-PASS between the two existing lines `entries = [_entry(sid, name,
  cands[sid]) for sid, name in built if sid in cands]` and `entries.sort(key=lambda e:
  _best_key(e["best"]["plan"], e["best"]["row"]) + (e["name"],))`:

      for e in entries:  # 307ba: the proposal on the entry's FINAL best (moves/drops recompute it)
          p = _entry_propose(root, e["site"], e["best"]["plan"])
          if p is not None:
              e["propose"] = p

  NOT inside `_entry` (its signature has no root). The post-pass keeps my one invariant:
  the propose is computed from the entry's FINAL best, so a move/drop that changes the best
  recomputes it; the key lands after "candidates" (dict insertion order - my part-1
  key-order pin). (d) Docstrings: keep their build() two-phase docstring and namesake-rule
  paragraph; keep my module-docstring propose paragraph; reword the stdlib-only line to
  name all three imports (right_place, review, propose - all stdlib-only, no pipeline/).
- tests/test_fit_queue.py: UNION, not a choice. test_fit_queue_synthetic: MY 7-site
  stage-B version, unmodified (both sides verified: 804 ran it unmodified in 0.68 s -
  pure no-op, its tree has index rows but no catalog/lists; if the wiring printed anything
  my `err == ""` pin would trip). 804's box-4 new namesake test: a separate function with
  its own tree (tiny data/catalog/sites.jsonl + data/books/index.jsonl +
  data/books/lists/<ia>.json; the book must be in right_place.BOOK_SCOPE - its hand-over
  picks "allcroft_1908"), cases a-f per its hand-over sketch - keep as-is when it lands.
  test_fit_queue_real: the merged function = 804's copies (data/catalog +
  data/books/index.jsonl + lists/) + 804's CHECK-AWARE entry-set/candidate/review-upsert
  derivation (my naive `expected = (built & (row_sites | item_sites)) - hand` cannot
  survive: the 15 flagged dispositions can take a site's last candidate and drop the site
  from the queue) + MY per-entry propose block (it calls propose_for on the entry's
  ACTUAL best against the temp tree - move-proof; keep the floor assert) + my sort-key
  check + my checkout byte-identity check. Parts 2-3: mine unchanged (804's full-suite run
  proves they stay green with the check live).
- web/data/fit_queue.json (both sides regenerated -> conflict): regenerate with the merged
  build `python3 tools/fit_queue.py --root .` on the synced branch; commit the joint file
  (805's right-place dispositions + my propose on the surviving entries). Expect 114
  entries at agent/c's iteration-100 data state (its measured 116 -> 114); if 203b (EU
  batch) or 207 (Roman books) land on main before 805's rebuild the population shifts
  (new index rows / review items) - regenerate, never pin the count.
- web/data/review.json + data/review/: 805's/220's - take THEIRS (my branch's copies are
  main's stale ones); never edit them from this task.
- docs/site_flow.md: keep both sections (my "Ready to fit" propose paragraph, 805's
  namesake-report section) - disjoint regions, clean merge expected; flag any overlap in
  DECISIONS.
- fit/propose.py, web/fitkit.js, web/index.html: only mine - keep mine (804's spec forbids
  touching agent a's web files; web/index.html stays exactly one line over main and
  web/fitqueue.js byte-identical - the part-3 pin).

**Wait condition (check in this order):**
1. `git log main --oneline -20` still cf29be2 (no 804/805/309 commits)? Nothing to build -
   this task waits on agent c. Do NOT touch data/review, web/data/review.json or
   re-baseline any test (the stale page is a real store invariant; iteration-116
   DECISIONS entry). Cheap unchanged-check: `git show main:web/data/review.json | md5sum`
   == b6506007.
2. main carries 804 and/or 805 (or 309 closed)? The driver has synced it into this branch
   (right_place.py + the rewired fit_queue.py together - see NEW DEPENDENCY FACT): expect
   text conflicts in tools/fit_queue.py, tests/test_fit_queue.py, web/data/fit_queue.json
   (both sides rewrote them) - resolve with the recipe above and run `.venv/bin/python -m
   pytest -q`. Once 805's (or 220's) full export is in the synced tree: expect 73 passed +
   1 skipped, no known failures -> re-claim done. If only 804 is in (805/220 not yet): the
   3 review-page failures remain - wait, do not re-claim. A failure with DIFFERENT numbers
   than 335/334 (the page population changed) means a merge AFTER the export wrote new
   data/review item files (agent c's 203b EU batch writes them for unplaceable sites) -
   the page snapshot is stale again: diagnose with a scratch full export (`fit/review.py
   export --root <copy of the store>`) and, if that is the cause, the fix is another full
   export (220's runner note covers it) - never re-baseline the three tests.

**Re-read (only when the 804/805 merge lands):** tools/fit_queue.py (confirm the actual
build() matches the shape above - if it diverged, trust the file; the post-pass goes
between the entries comprehension and the sort); agent/c's 804 hand-over (the box-4
namesake test: its own tree needs catalog + index + lists, book in BOOK_SCOPE); tools/
right_place.py (load's per-store optional degrade, check_pairing, find_right_site
min_score 0.5). The iteration-116 Re-read list (fitkit, index.html ~832/902/1706, part 3,
/tmp/fkprobe.mjs) belongs to 307bb, not this task.
