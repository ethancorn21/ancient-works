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
  full recipe is in the hand-over. 805's in-run full review export would have subsumed my
  220 filing - overtaken: the lead ran that export themselves (c5250a4) before 309 closed
  and ordered a resume without waiting for c's chain; 220 closed as done (iteration 121);
  805's rebuild is now a later snapshot update, not a precondition for my re-claim.
- The stage-B row shape: data/books/index.jsonl (scale_text, blank_boxes[{kind:"scale_bar",
  box}], north_angle_deg, north_arrow, map_box, full_size). fit/ has no __init__.py; import
  via sys.path.insert(0, str(ROOT / "fit")) like tools/site_done.py:43.
- Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-12, iteration 121, agent a - the wait is over on the main side. 220's export is
on main (the lead's own commit c5250a4), and the lead ordered a resume WITHOUT waiting
for c's 309/804/805 chain. The driver has not yet synced main into this branch
(agent/a..main = 4 lead commits at the time of writing) - the re-claim is ONE step after
that sync: verify the sync, run the suite, expect green, set done. No code change this
session; my 220 filing closed as done.)

**The main side (read, never merged - main tip 57b3988 = cf29be2 + 4 lead commits):**
- c5250a4 = 220's full review export: web/data/review.json md5 2609ecef (page 335 open of
  341, `at` 2026-10-12T05:02:09); the 6 item files each only gain the write-once resolved
  record (alligator n0214_2 -> c_618a6be74dfaff32, argentoratum -> c_e882645cc479c889,
  castle-neroche n0110_1 -> its own doc, castra-lemanis -> c_be12fb0f9a87000b,
  ferme-d-azincourt -> c_804aa7af3eb2ac7c, forthill n0068_1 -> b24849959_n0269_1). The
  lead's own words in the commit: "The lead placed matcher docs without a full export;
  that staled the page."
- 5c153b9 (214: Italy+Luxembourg in REGION_NAME; tests/test_region.py +2 tests),
  2dd6596 (215: pipeline/books.py probes the live Qwen ports 8080-8082), 57b3988 (a
  PITFALLS fold). None touches my files. tools/right_place.py and the 804 wiring are
  still agent/c only.
- The lead's override (their 2026-10-12 message): "220 done on main (full review export,
  335 open of 341). Your 3 stale-page failures should clear on the next sync. Resume 307ba
  now: build on main, do not wait for c 309/804/805; if their merge conflicts later, the
  second to land resolves it." -> my 220 dependency is satisfied; c's chain is no longer a
  precondition for my re-claim (it remains a future merge-conflict source - recipe below).

**Verified by running (this session):**
- Scratch copy of main's exact tree (git archive main -> /tmp/mn121, seeded with the
  gitignored store elements: web/data/sites copy + the data/raw symlink into the main
  checkout - the data/raw du=0 symlink PITFALLS): the 3 stale-page tests all PASS
  (25.5 s); the full seeded suite = 75 passed + 1 skipped, 0 failed = the main baseline;
  a re-export over that state is a no-op (only the page's `at` moves) - the page is in
  sync as of c5250a4.
- This branch before the sync: the 3 failures re-measured = pure stale-page arithmetic,
  machinery intact (the fixture pick works, the one-site line ~18 s, the page re-exports
  in the temp tree): test_line_refuses_unmarked_non_auto_doc "334 vs 339",
  test_site_done_line "335 vs 340", test_save_runs_the_one_site_line "334 vs
  (340-1)=339". Post-sync the expectation side becomes 335 -> all three flip green with
  no test change.
- Merge preview (read-only git merge-tree from merge-base cf29be2): no conflict markers;
  only PITFALLS.md changed on both sides (different sections) -> the driver's sync
  should be clean and automatic.

**The next session (after the driver syncs main into agent/a) - the re-claim, one step:**
1. `git log agent/a..main` -> must be empty (the at-writing tip was 57b3988; if more lead
   commits have landed, the same check applies to the new tip).
2. `.venv/bin/python -m pytest -q` -> expect **75 passed, 1 skipped, 0 failed (76
   total)** (= main's 76 tests; my test_fit_queue.py wins the merge unchanged - main
   never touched it - and my part-1 tests are already green; the 3 stale-page tests flip
   green; 214's 2 region tests green per the scratch).
3. Set Status: done; commit "307ba: re-claim done - 220's export (c5250a4) synced, the 3
   stale-page failures cleared, full suite green (75+1)". Do NOT re-claim in a session
   where agent/a..main is non-empty (the claim would fail the same way; the sync clears
   it).

**If the numbers differ at the re-claim (diagnose before touching anything):**
- (a) c's 309 chain (804/805) landed on main in the same sync: text conflicts in
  tools/fit_queue.py, tests/test_fit_queue.py, web/data/fit_queue.json (both sides
  rewrote them) - the driver hands the conflict to the second to land (me, if my
  re-claim merges after theirs): resolve with the merge recipe (the full re-pinned
  recipe is in the 2026-10-12 307ba DECISIONS iteration-120 entry; essence: their
  two-phase build() as the base, my `_entry_propose` as a POST-PASS between the entries
  comprehension and the sort, one pair of path-inserts + three imports, tests are a
  union, the queue file regenerated with the merged build - expect 114 entries at their
  data state, never pinned; their review.json/data/review win; my fitkit.js/index.html/
  propose.py win).
- (b) 203b/207/805 wrote new data/review item files (or new fit docs) after c5250a4's
  snapshot: the page goes stale again with numbers OTHER than 335/334 -> the fix is
  another full export (`fit/review.py export --root .` in the checkout, commit the two
  store paths) - diagnose first with a scratch copy (the 220 mechanism); never a
  re-baseline.

**Re-read (only when c's 309 chain lands):** tools/fit_queue.py (the actual build()
shape), agent/c's 804 hand-over (the box-4 namesake test), tools/right_place.py (load's
per-store optional degrade). The iteration-116 Re-read list (fitkit, index.html
~832/902/1706, part 3, /tmp/fkprobe.mjs) belongs to 307bb, not this task.
