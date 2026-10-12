Status: in-progress
# 307ba: Open the map - the queue carries the proposal, and place mode opens ON the works
Depends on: 307a, 220
Touches: fit/propose.py, tools/fit_queue.py, web/fitkit.js, web/index.html, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md

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
- Agent c's 309 works on tools/fit_queue.py / web/data/fit_queue.json / tests/test_fit_queue.py
  in its own branch (the place check): expect a merge of its build() change; keep the propose
  wiring localized (one helper, one key per entry, docstrings) so the merge stays trivial.
- The stage-B row shape: data/books/index.jsonl (scale_text, blank_boxes[{kind:"scale_bar",
  box}], north_angle_deg, north_arrow, map_box, full_size). fit/ has no __init__.py; import
  via sys.path.insert(0, str(ROOT / "fit")) like tools/site_done.py:43.
- Do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-12, iteration 116, agent a - the done claim (9efb944) was REJECTED by the driver
for 3 suite failures that are NOT this task's work; the root cause is pinned and the fix
filed as task 220 (Depends on: 309 - agent c's module). 220 is on this task's Depends on
line now. All five boxes remain ticked and everything remains committed; when main carries
220 into this branch, re-verify the suite and re-claim done. Nothing else to build.)

**The rejection and its mechanism (all verified by running, DECISIONS 2026-10-12 307ba
iteration-116 entry).** The driver (be251b8) lists: test_fit_provenance::
test_line_refuses_unmarked_non_auto_doc, test_fit_queue::test_save_runs_the_one_site_line,
test_site_done::test_site_done_line. Cause: the committed web/data/review.json (340 open of
341, published Oct 11 18:48) is STALE relative to the committed code. The lead's b22a2d2
(22:27) + cf29be2 (22:35, the main tip) changed fit/review.py::resolved_doc (a recorded
resolution counts only while its document exists) and placed 5 matcher fit documents into
data/db/platefits, but neither commit re-exported the page (no web/data/review.json in
either diff). The current export would print 335 open of 341 (the 5 resolved items hidden)
and record write-once `resolved` into 6 item files (those 5 + alligator n0214_2). The 3
tests all derive the expected count from the LIVE page (340) while running the CURRENT
code in a temp tree: test_site_done's line prints 335 (expected 340); test_fit_provenance's
seeded refusal doc resolves one more item -> 334 (expected 339 = 340-1); test_fit_queue's
page save resolves one more -> 334 (expected 339). Verified the fix in a scratch copy of
the store: `fit/review.py export --root <scratch>` -> 335 open of 341, the 6 records
exactly as above, second export a no-op. With that page the 3 tests' expectations agree by
construction. None of this task's files (fitkit/propose/fit_queue/tests part 1) is on any
of the 3 tests' path - the failing asserts are pure page-count arithmetic in the
one-site line's review export.

**State of the branch (all committed, unchanged by this session).** cbb36c8 (boxes 1-3);
732fe57 (box 4: web/fitkit.js + the one script tag); 7f7e7c0 (box 5: docs/site_flow.md);
9efb944 (the rejected done claim). Against main (cf29be2): web/fitqueue.js
byte-identical, web/index.html exactly one added line.

**Next session (after 220 has merged into main and the driver synced this branch):**
re-run `.venv/bin/python -m pytest -q` (expect 73 passed + 1 skipped, no known failures)
and re-claim done. If the driver brings this task back BEFORE 220 merged: there is nothing
to do but wait - do NOT touch data/review or web/data/review.json (309/220's files), do
not re-baseline any test (that would paper over a genuinely stale page: the owner's
Review tab is currently advertising 5 items whose fits are already on the map), and do not
re-claim done (it fails the same way).

**Re-read (only if reopened):** web/fitkit.js (its header comment is the design doc);
web/index.html ~832 endFit, ~902 openPlan, 1706-1710 (the script tags);
tests/test_fit_queue.py part 3 (~716+, the byte-identity pin) and ~700-712 (the part-2
save test whose open_after delta trips on the stale page - expect it green after 220);
/tmp/fkprobe.mjs (the throwaway probe - the template 307bb's committed part-4 test adapts;
its playwright require path and the direct `map` reference are this-VM fixes). The data
side needs no re-read: it is as committed.
