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

(2026-10-12, iteration 118, agent a - still WAITING, now verified exact.) main is still
cf29be2 (`agent/a..main` empty; main's web/data/review.json md5 b6506007 == this branch's):
no 804/805/309 commits, the 3 stale-page failures stand, a re-claim now would fail the same
way (do not re-claim). Read agent/c as of the local snapshot (tip c24c135, work tip d413d0e,
~iteration 100): 804 is in-progress with ONLY the build() refactor in (new `_entry` helper,
per-site candidate maps gathered first - behavior-neutral); the two-phase wiring
(_place_store/_place_flags/_apply_flags) is not written yet (804's hand-over carries the
exact plan). THIS SESSION verified BY RUNNING that 804's planned _place_flags (their
committed tools/right_place.py, read-only /tmp copy + my branch's fit_queue helpers) over my
part-1 synthetic tree: the check runs there (index.jsonl present -> not the no-op-degrade
path; the degrade needs catalog, index AND lists all empty), 14 (site, candidate) pairs
checked, 0 flags, no exceptions (all 7 sites lack region/place -> bucket "other" -> fail
open; no caption carries a county/state/town word) - my pinned synthetic assertions survive
the merge unmodified, no test edit needed. Part-1 tests re-run green on this branch
(2 passed, 0.85 s). No code change this session; my state = cbb36c8 (boxes 1-3), 732fe57
(box 4), 7f7e7c0 (box 5).

**Wait condition (check in this order):**
1. `git log main --oneline -20`: still cf29be2 (no 804/805/309 commits)? Nothing to build -
   this task waits on agent c. Do NOT touch data/review, web/data/review.json or re-baseline
   any test (the stale page is a real store invariant; iteration-116 DECISIONS entry).
   Cheap unchanged-check: `git show main:web/data/review.json | md5sum` == b6506007.
2. main carries 804 and/or 805 (or 309 closed)? The driver has synced it into this branch:
   expect text conflicts in tools/fit_queue.py, tests/test_fit_queue.py, web/data/
   fit_queue.json (both sides rewrote them). Resolve with the recipe below and run `.venv/
   bin/python -m pytest -q`. Once 805's (or 220's) full export is in the synced tree:
   expect 73 passed + 1 skipped, no known failures -> re-claim done. If only 804 is in
   (805/220 not yet): the 3 review-page failures remain - wait, do not re-claim.

**Merge recipe (the next session that sees 804/805 on main executes it):**
- tools/fit_queue.py: take 804's FINAL build shape - `cands_by_site -> _place_flags ->
  _apply_flags -> entries via _entry` (d413d0e's refactor + the wiring its hand-over
  planned). Add MY propose as a POST-PASS over the final entries list inside build() (after
  the entries comprehension, before the final sort): for each e, `_entry_propose(root,
  e["site"], e["best"]["plan"])`; set `e["propose"]` when not None. NOT inside `_entry` (its
  signature has no root) and NOT "before entries.append" (that per-site loop no longer
  exists in their shape). The post-pass keeps the one invariant that matters: the propose is
  computed from the entry's FINAL best, so a move/drop that changes the best recomputes it;
  the key lands after "candidates" (dict insertion order - my part-1 key-order pin). Keep
  as-is: the `_entry_propose` helper, my `sys.path.insert(0, str(ROOT / "fit"))` +
  `import propose` lines (804 adds its own ROOT/tools + ROOT/fit inserts for
  right_place/review - all three stay; the runpy PITFALL is why each module self-inserts),
  the module docstring's propose paragraph (804's "candidate maps gathered first" docstring
  sentence stays too; the input list grows from my five to seven with 804's catalog + lists
  - reword to the merged truth).
- tests/test_fit_queue.py: UNION, not a choice. test_fit_queue_synthetic: MY 7-site stage-B
  version, unmodified (verified above: the wired build is a silent no-op on it - 0 flags; if
  804's wiring printed anything my `err == ""` pin would trip - their box 4.3 promises that
  test passes unmodified, so it is their contract too). Their new namesake test (box 4.1) is
  a separate function with its own tree - keep it as-is. test_fit_queue_real: the merged
  function = 804's copies (data/catalog + data/books/index.jsonl + lists/) + 804's
  CHECK-AWARE entry-set/candidate/review-upsert derivation (my naive `expected = (built &
  (row_sites | item_sites)) - hand` cannot survive: the 15 flagged dispositions can take a
  site's last candidate and drop the site from the queue) + MY per-entry propose block (it
  calls propose_for on the entry's ACTUAL best against the temp tree - move-proof; keep the
  floor assert) + my sort-key check + my checkout byte-identity check. Parts 2-3: mine
  unchanged; the part-2 open_after delta goes green with the in-sync page.
- web/data/fit_queue.json (both sides regenerated -> conflict): regenerate with the merged
  build `python3 tools/fit_queue.py --root .` and commit the joint file (805's right-place
  dispositions + my propose on the surviving entries; if 805's committed version lacks
  propose - its run predates my branch on main - the regeneration adds it back on top of the
  wired build). Expect ~116 entries: current data builds 116, not the stale committed 117
  (shotwick-castle-q7502621 is no longer built), minus the 15-flagged pairs'
  drops/moves/upserts; propose on every entry that anchors.
- web/data/review.json + data/review/: 805's/220's - take THEIRS (my branch's copies are
  main's stale ones); never edit them from this task.
- docs/site_flow.md: keep both sections (my "Ready to fit" propose paragraph, 805's
  namesake-report section) - disjoint regions, clean merge expected; flag any overlap in
  DECISIONS.
- fit/propose.py, web/fitkit.js, web/index.html: only mine - keep mine (804's spec forbids
  touching agent a's web files; web/index.html stays exactly one line over main and
  web/fitqueue.js byte-identical - the part-3 pin).

**Re-read (only when the 804/805 merge lands):** tools/fit_queue.py (the final build()
shape - find the post-pass insertion point); tests/test_fit_queue.py part 1 (where the
union lands); agent/c's 804 hand-over (the _place_store/_place_flags/_apply_flags plan - if
the merged file diverges from it, trust the file). The iteration-116 Re-read list
(fitkit, index.html ~832/902/1706, part 3, /tmp/fkprobe.mjs) belongs to 307bb, not this
task.
