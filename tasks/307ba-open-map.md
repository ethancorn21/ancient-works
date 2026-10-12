Status: in-progress
# 307ba: Open the map - the queue carries the proposal, and place mode opens ON the works
Depends on: 307a
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
- [ ] Opening a queue site with a proposal (the card's "Place the drawing", or the site
      panel's "Place an old plan" when the site's queued plan is the one picked): the map
      flies to the site's box (its four corners) centred, before the drawing appears; while
      place mode is open, the site's earlier overlay (the dep-* fitted drawing or survey
      sheet applyDep was showing) is hidden; on close (back button, Cancel, or saving) it
      comes back exactly as it was (same depiction selected, same ground). web/fitkit.js is
      a new extension in the fitqueue/review pattern (loads after them, wraps openPlan last
      in the chain and endFit, injects its own <style>, _fk-prefixed saved names);
      web/index.html changes by the one script tag alone; web/fitqueue.js stays
      byte-identical.
- [ ] docs/site_flow.md's "Ready to fit" section: the entry's new propose field (what it is,
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

(2026-10-12, iteration 111, agent a - the DATA side is done: boxes 1-3 ticked, ALL committed
in cbb36c8 (fit/propose.py, tools/fit_queue.py, web/data/fit_queue.json,
tests/test_fit_queue.py, plus DECISIONS/PITFALLS/task files). No page code written yet.
NEXT = box 4 (the page: web/fitkit.js), then box 5 (docs/site_flow.md).)

**Tests when last run:** full `.venv/bin/python -m pytest -q` green AFTER the final code
change (the loader-defaults fix): 73 passed, 1 skipped = the iteration-110 baseline
(identical counts); tests/test_fit_queue.py alone: 5 passed in 51.6 s (part 1 both tests
in ~1 s; part 2 the one-site line; part 3 both headless card tests on Chrome). The
2-arg behaviour of propose_for was verified byte-identical against the git-HEAD module
(9 sample pairs across all three scale sources, identical JSON).

**State.** fit/propose.py is root-aware (loaders take `root=ROOT`, `_CACHE` keyed
`(str(root), kind)`, `propose_for(site, plan, root=ROOT)`); tools/fit_queue.py carries
the propose (one localized `_entry_propose` helper + one key per entry after "candidates"
+ docstrings - kept trivial for the 309 merge); web/data/fit_queue.json regenerated on
THIS branch (117/117 entries carry propose: 20 bar, 4 ratio, 93 picture_size; Devil's
Dyke 0.3621/rot 0, note names the bar '0 100 200 300 400 Yards'); part-1 tests pin every
propose path (synthetic: bar+arrow 0.1306/rot 20 hand-pinned, ratio-fallback 0.2, the
no-propose trio no-size_m/no-size/no-index-row; real: per-entry derived with an
anchored>=1 floor). PITFALLS: the private propose loaders are a de facto external API
(inkfit, inkfit_heldout, test_propose call them) - keep their defaults.

**Watch first:** has agent c's 309 (the place check) merged into main by now? It also
rewrites tools/fit_queue.py's build(), web/data/fit_queue.json and tests/test_fit_queue.py.
If yes: run `python3 tools/fit_queue.py` once on the merged branch (the queue file is a
joint artifact - regenerate on top of whatever the branch shows) and re-run
tests/test_fit_queue.py; the propose wiring is isolated in `_entry_propose`, so any
build() merge conflict left for me is small. If not merged, proceed as is.

**Box 4 (the page, next step).** web/fitkit.js is a new extension in the fitqueue/review
pattern (see the parent 307b hand-over's "Page-side design sketch" - it is precise: wrap
openPlan LAST in the chain and endFit; `_fk`-prefixed names - one global lexical scope per
page, do not redeclare review.js's `_renderList`/`_openPlan`; reach P/map/S/select by name;
inject its own `<style>`). web/index.html gains exactly one script tag, after fitqueue.js
(the tags are at index.html:1707-1708). Activation: the opened row is the site's queue
entry's best plan AND the entry carries a propose. On open: map.fitBounds to the site's
corners FIRST (fly to the site's box before the ink appears; padding left ~390 when
!narrow()), hide the `dep-<site.id>` layer (visibility 'none' if present), seed
`P.anchor = {u0, v0, lon, lat, mpx, rot}` from the propose (pair[4] is the panel centre;
u0/v0 derived exactly as propose._anchor_pairs does: the index row's map_box* size or
the page frame) and `P.pairs = re-emit(anchor)` (port `_anchor_pairs`'s math:
`merc = a*(w-w0)+z0`, `a = (m_per_px/ground_scale(lat))*e^{i*rot}`, u/v 1 dp, lon/lat
7 dp) so the existing refit()/simFit() preview shows the drawing ON the site. On close
(back/Cancel/save): restore the dep layer exactly (S.depSel/ground/etc are never
 touched), clear P.placed/anchor/pins. GATE: only activate when P.img has loaded - the
305 part-3 card test's served tree 404s the page scan, and that test (which opens the
FIRST entry, which now HAS a propose) must stay byte-identical green; without the image
there is no ink to place, so not activating is the right behaviour, not a shortcut.

**Box 4 verification (no new headless test yet - that is 307bb's box 5).** Check:
`git diff web/fitqueue.js` empty; `git diff web/index.html` = one script tag line; full
suite green (305 part-3 card tests pin the no-propose byte-identity; the with-propose
browser behaviour is proven by 307bb's headless part 4 - do not add a headless test here).

**Box 5 (docs, after box 4).** docs/site_flow.md's "Ready to fit" section: the entry's new
propose field (what it is: the starting placement, anchor at the panel centre, the scale
ladder bar/ratio-at-ppi/site-size, the north arrow where trustworthy; where it comes
from: data/books/index.jsonl stage-B fields; the fail-open: a row that cannot anchor gets
no key and the page does the ordinary three-point flow). Do NOT write the full place-mode
section (gestures, save, screenshots) - that is 307bb/307c's.

**Re-read** (for the box-4 session): web/index.html ~340-420 (the deps model: applyDep
manages one `dep-<site.id>` layer; select() sets ground), ~832 endFit, ~902 openPlan,
~1000-1150 (startFit, makeInk, simFit, refit, saveFit, the map-click pin flow) and
1707-1708 (the fitqueue/review script tags); web/fitqueue.js in full (fqLoad/fqPatch/
fqPlace, the renderList/saveFit wrap pattern to imitate); web/review.js (the earlier
extension: how it wraps openPlan before fitkit's); the parent 307b hand-over's page-side
design sketch (the authoritative source); tests/test_fit_queue.py part 3 (what stays
byte-identical).
