Status: split
# 307a: re-split per the lead (2026-10-12) - the place check is carved to 309 (agent c); the page work moves up to 307a
Depends on: 305, 309
Touches: (none - a re-split record; the work lives in 307b/307c/307d and the carved 309)

## What happened (iteration 108)
Iteration 108 (agent a) spent the whole session investigating the original 307a (the namesake
place check in tools/fit_queue.py: data/fit_place.json verdicts, moves to review, the report):
all inputs mapped, the rule set drafted, and the noisy-evidence-conflict question (52 queue
commons rows) being analysed when the lead re-tasked mid-session:

- Lead message 1: "307 box 1 (right place, the namesake check in tools/fit_queue.py) is carved
  to 307b for agent c. Leave tools/fit_queue.py to c; do the page work (zoom, hide overlays,
  drawing on the map, working space, save path). Untick nothing, just mark box 1 as carved."
- Lead correction (same iteration): "the carved task is 309 (not 307b)."

So: box 1 is carved out of 307 into the NEW top-level task 309 (agent c owns it; it carries the
full old-307a spec and this session's research). Agent a now does the 307 page work, renumbered:

- **307b (was 307a's letter, now the on-map placement)**: parent boxes 2-4 - place mode opens
  ON the works (fly to the site's box, centred, zoomed so the works fill the view), hides every
  overlay while open and restores on close, and the drawing starts ON the map (the proposal's
  pairs, drag/scale/rotate, opacity, save from direct placement alone).
- **307c (was 307b's content)**: parent box 5 - working space (map the main surface, the page
  picture a small collapsible reference, the side panel only what placing needs; before/after
  screenshots in docs/site_flow/).
- **307d (was 307c's content)**: parent box 6 - the save path stays `by: hand` + the one-site
  line (305), existing hand fits unchanged, checked in a real browser on two queue sites (the
  queue place-check test in that box now belongs to 309).
- **307d-old (owner check)**: dropped - merged into the new 307d above.

The parent's box 1 carries the marker "(carved to 309 - agent c)". Nothing was unticked.

## Hand-over

(2026-10-12, iteration 108, agent a - this file is a re-split record, not a work task.
The next agent of this project: read the parent's Hand-over first, then 307b/307c/307d.)

State: NO code of 307 was written this session (investigation only; the branch is still at the
iteration-107 baseline, .venv/bin/python -m pytest -q was 73 passed 1 skipped before my session,
and nothing has changed it since). All research from this session is preserved: the parent's
Hand-over (unchanged, still accurate) and the DECISIONS entry "2026-10-12 307a DECISION:
iteration 108 research ... re-tasked to the page work" (it holds the place-check rule set, the
data map, and the page-work anchors - the last section of it is the page-work brief for the new
307b).

The new 307b (on-map placement) starts from the parent's measured ground truth:
- fit/propose.py propose_for already returns the anchor the page needs (bar scale / ratio at
  the book's ppi / site-size fallback; north arrow; 3-5 pairs) and is stdlib-only - the page
  side can call a small stdlib helper over it; it works for n0686 (scale_m_px 0.3621, 5 pairs
  centred on the site, coarse false).
- The page already draws ink on the map: index.html refit() maps P.inkUrl (survey-red on
  transparent, makeInk) onto the map's 'fit-prev' image source from the least-squares
  similarity of P.pairs (warpView() proves the image-source quad mechanism; a similarity's
  rotated rectangle is a parallelogram, so the affine the image source builds is exact).
  "The drawing starts on the map" = on open, set P.pairs to the proposal's 5 pairs (least
  squares recovers the anchor exactly), then handlers edit the anchor (drag/scale/rotate) and
  re-emit pairs; the saved doc stays pairs-shaped, so plan_fit.py/gate/one-site line are
  untouched. review.js already shows the pattern for pre-placing pairs on open (RV.pending).
- Fit-tool entry points to study first: web/index.html (the 1710-line page: refit(), warpView(),
  makeInk, openPlan, the fit pane/points model, the place-mode flow fitqueue.js drives:
  endFit -> select(site) -> setGround -> loadDeps -> startFit(site) -> openPlan(row)), and
  web/fitkit*.js (the existing extension-script pattern to follow for a new fitkit-style
  extension). Boxes 2-3 (fly-to on open, hide/restore overlays) live in the page's site-view
  and map-source code; keep the extension small and let the page own the map state.
- Concurrency note (team mode): agent c now owns tools/fit_queue.py, data/fit_place.json and
  web/data/review.json via 309 (it may change the queue file's shape/contents while I work);
  307b/307c/307d must read the queue file tolerantly (fitqueue.js already tolerates a missing or
  changed file) and must not write it. web/data/fit_queue.json stays in c's 309 Touches.

Exact next step for the next agent (307b): read web/index.html's fit/place flow (refit, warpView,
startFit, openPlan, setGround, the 'fit-prev' image source, the overlay sources it must hide -
survey sheets and earlier drawings) and web/fitqueue.js's Place handler; then implement box 2
(place mode flies to the site's box, centred, zoomed so the works fill the view, before the
drawing appears) as the smallest working slice, checked in a headless browser against the
served tree (the recipe is in tests/test_fit_queue.py part 3 and in PITFALLS.md), before
touching boxes 3-4.
