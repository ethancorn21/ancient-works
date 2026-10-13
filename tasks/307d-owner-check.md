Status: open
# 307d: The owner's check - two queue sites end to end, then reverted
Depends on: 307c
Touches: tests/, docs/site_flow.md, docs/site_flow/

## Goal
The last box of 307: "Saving still writes "by": "hand" and runs the one-site line (305),
and the existing hand fits load and save unchanged. Checked in a real browser on two queue
sites the way the owner uses it (place, move, scale, save, see it on the map), then the
test fits reverted. Tests cover the queue place-check and the save path." The place-check
tests are 309's; this task proves the save path end to end in a real browser on two queue
sites and proves the shared store comes back byte-identical.

## Acceptance criteria
- [ ] A new tests/ file runs the owner's flow in a real headless browser (Chrome, the
      305-part-3 pattern) against the real server on a private copy of the tree (the 305
      part-2 precedent: real data, no network, ephemeral port): on two queue sites (pick
      ones with a recorded bar scale and a site-size-only fallback, and different ground
      where possible - LiDAR relief vs aerial photograph) the test does what the owner
      does: open the queue, place the drawing (the on-map start), move it, scale it,
      save; then verifies the saved doc carries "by": "hand" and the one-site line ran
      (the overlay on the map in the site's depictions, the site square coloured, the
      review item resolved, the queue moved on), and after a page reload the fit loads
      back unchanged (same placement, same overlay).
- [ ] The test fits are reverted before the test ends: the private tree is discarded, and
      the shared store in the repo is proven byte-identical to before the test (the golden
      hand-fit hash check tests/golden/hand_fit_docs.sha256 and test_fit_provenance stay
      green; web/data/fit_queue.json and the review exports untouched).
- [ ] docs/site_flow.md: the verification section (what was checked, on which two sites,
      which way, and the screenshots), closing the parent's last box.

## Notes
- The parent's note stands: do not touch fit/surveyfit.py or task 304 (agent c).

## Hand-over

(2026-10-13, iteration 249, agent a - NINTH session. The probe is now FULLY GREEN (first
time in the file's life): run 5 (pytest-3) printed RESULT PASS on BOTH sites - every
in-page check passes (boot, card1, place, seed, drag, wheel, shift+wheel, save, all four
line effects, card2, reload, card3, no pageerror, no non-tile reqfail). The test still
fails because the PYTHON-side checks (never executed in runs 1-4 - the probe assert fired
first) fail in check 4 for both sites. Nothing is ticked yet; no boxes. The DECISIONS
entry (ninth session) has the full evidence; this is the working state.

**Working tree (UNCOMMITTED - the harness saved it; do not lose):**
- `tests/test_owner_check.py`: (a) the probe's stdout+stderr now dumped to
  `outdir/owner_probe.log` before the assert (evidence survives failures); (b) all three
  marker-class comparisons (effects ok, effect-(b) check, reload ok) and python check-4's
  two asserts changed from full-string equality to CLASS-MEMBERSHIP: the page sets
  `marker <tier>` but MapLibre's Marker constructor ADDS `maplibregl-marker
  maplibregl-marker-anchor-bottom` to freshly-created elements (post-reload), while the
  page's post-save sync REPLACES the list (post-save) - both states carry the tier class;
  the page was never wrong. `node --check` on the regenerated probe passes.
- `PITFALLS.md`: committed with the hand-over below (3 new entries: web/ page-fetch
  limits; tests/playwright no-fs-in-evaluate; raw-string JS-escape trap).

**Where the test stands (5 runs total, this file):** 1-2 (sessions 247/248): probe died
early (syntax, then effects-poll 404/in-page readFileSync - both fixed, see the 7th/8th
DECISIONS entries). 3-4 (this session, before the class fix): the ONLY failing in-page
check = the reload check (markerClass string mismatch). 5 (this session, after the fix):
probes PASS; failure moved to the Python checks.

**The only remaining failure - check 4 (both A and B, AssertionError with NO message).**
Check 4 = the site's marker fields in the tree's sites.json. Its message-bearing asserts
(drawings, score) pass (check 8 cross-confirms the page's reload drawings/score equal the
tree's entry, and check 8 PASSES). So the culprit is one of the message-less asserts:
`entry["overlays"] == len(ovs)` or `entry["oldest"] == min(y for y, _, _ in ovs)` (the
two new markerClass membership asserts are the least likely - the [eval] markerClass
strings contain `marker` and `t2` in both phases; 248's evidence says both entries ended
as {drawings 1, score 1.45, oldest 1842, overlays 2}). LEADING SUSPECT: `_score_of_deps`
is MY OWN port of build_site's formula inside the test - its `ovs` list must count
exactly what `pipeline/build_site.py`'s set_drawings/score counts as overlays (if the
port counts only kind plan/drawing/view or only depictions with a fit key it returns 1
instead of 2 for the six-inch + new plan).

**Retained evidence (COPY IT BEFORE THE NEXT FAILED RUN - pytest retention is 1, the next
failed run deletes pytest-3):** /tmp/loop-ancient-works.a/pytest-of-agent/pytest-3/ -
`awowner0/` (the full private tree: both docs by:hand 5-pairs in data/db/platefits, both
overlays in the site dirs, both items resolved by the right doc, tree page file 455 open
of 480, sites.json entries), `ownerA0/` + `ownerB0/` (owner_probe.mjs, the five .png
shots each, owner_probe.log = full probe stdout incl. the [eval] dump). The repro script
/tmp/loop-ancient-works.a/repro307d.py may be gone; its method: import tests.test_owner_check
(sys.path the tests dir), recompute picks via _picker/_item_of exactly as the fixture,
read the [eval] line from each owner{tag}0/owner_probe.log, exec the numbered `# N.`
blocks of _run_one textwrap.dedent'ed in ONE persistent merged namespace
(globals==locals, or comprehension free-vars NameError; runlog=None). Result there:
checks 1, 2, 3, 5 PASS both; 8 PASS both; 7 unverifiable offline; 6-PASS for B, 6-FAIL
for A = REPRO ARTIFACT ONLY (the script evaluates A against the FINAL page file after B's
run; in the real test A's check 6 runs against the post-A page file where B's site is
still open - I verified the page file is in perfect sync with the store: checkout
457-open page = 480 store items minus 23 store-resolved, symmetric diff 0, so check 6
passes in the real test).

**INSTRUMENT CHECK 4 EXACTLY (I was doing this when the limit hit; do it first):** for
each pick's site (A oswestry-castle-q20713795, B devil-s-dyke-q3307343) in the retained
tree print: (a) the tree's sites.json entry {drawings,score,oldest,overlays}; (b)
`toc._score_of_deps(deps)` -> (score, ovs), len(ovs), min year over ovs; (c) every
depiction's (file, kind, year, fit-doc); (d) the markerClass strings from the [eval]
line. Compare (a)/(b) to name the failing assert, then read pipeline/build_site.py's
set_drawings + score computation and make the test's `_score_of_deps` mirror the real
code exactly (or assert the page's own fields against each other). Fix the TEST ONLY -
do not touch the page or build code (not in my Touches).

**Exact next step (one session, in order):**
(1) Copy the retained tree (cp -a pytest-3/awowner0 -> a safe path) and instrument check
    4 as above; fix the test's `_score_of_deps` / check-4 asserts accordingly.
(2) Add a runlog dump so check 7 (the server runlog - NOT verifiable offline; the server
    stdout lives in the fixture's in-memory `out`) is diagnosable after any failure: in
    _run_one right after `runlog = out[n0:]`, add
    `(outdir / "server_runlog.log").write_text("\n".join(runlog) + "\n", encoding="utf-8")`.
    248's exact-match asserts to satisfy: exactly `  one-site line for {site}: finished
    (exit 0)`; exactly two `fit  ` lines = the no-model line + the no-batch line with
    counts from the tree's plans rows (A: 1/1/0, B: 3/1/2); no 'matcher'; no 'attempted a
    network connection'; no refused/FAILED/sent sync lines. (Run-tail evidence shows
    these lines appear, incl. plan_fit's `{sid} {plan}: {n} pairs, similarity, residuals
    m [...]` print at pipeline/plan_fit.py:370 - it starts with the site id, so it does
    not pollute the `fit  ` filter.)
(3) `node --check` the regenerated probe; run `.venv/bin/python -m pytest
    tests/test_owner_check.py -q` (~3-4 min now the probe passes fast) - EXPECT GREEN.
(4) If green: full suite `.venv/bin/python -m pytest -q` (~6 min) - expected 157 passed /
    1 skipped / 1 failed, the ONLY red 235's tests/test_fit_queue.py::
    test_placement_gestures_and_save_in_the_browser (pre-existing since iter 161,
    documented in PITFALLS); tests/golden/hand_fit_docs.sha256 and test_fit_provenance
    must be green (my test's revert proof asserts the checkout write surface - every
    platefits doc, every review item, sites.json, review.json, fit_queue.json, both
    picks' site dirs - byte-identical around each run; it has held in all 5 runs).
(5) docs/site_flow.md: append the verification section AFTER the 308 section ("## The
    site markers become arrowheads (task 308, 2026-10-13)" at ~L1485): what was checked
    and how (owner's flow in headless Chrome on a private tree: card -> place on the
    works -> drag -> wheel -> shift+wheel -> save -> the line's four effects -> reload
    unchanged -> card still moved on), the two DERIVED picks (A [38] oswestry bar
    0.1646, Allcroft 1908 "Camp, Old Oswestry, Salop"; B [45] devil-s-dyke picture_size
    0.7201 "SWEALD") + picker rules, the four effects with measured values (overlay
    plan_<plan>.webp ink on the map, square 1.1->1.45 t1->t2 on both, item resolved
    write-once, card moves on to [39]/[46]), reload unchanged (persisted depSel = the
    overlay ink, ground 'imagery' page contract, done map kept), the revert proof, the
    ten screenshots (docs/site_flow/307d_A_1-card..5-reload.png, 307d_B_* - the test
    copies them on success; they do not exist yet), and STATE PLAINLY: both sites sit on
    LiDAR relief (lidar null) because no aerial-photograph-only (lidar false) site is
    line-eligible today - the task's "different ground where possible" hedge is not
    satisfiable.
(6) Tick all three acceptance boxes, set Status: done, DECISIONS entry, commit
    EVERYTHING (test file, docs, screenshots, task file - all uncommitted in the working
    tree now).

**Picks (unchanged; re-verified this session):** A = [38] oswestry-castle-q20713795 /
earthworkenglan01allcgoog_n0119_1 (bar, scale_m_px 0.1646 rot 0, book 'Allcroft 1908',
title 'Camp, Old Oswestry, Salop'); B = [45] devil-s-dyke-q3307343 /
earthworkenglan01allcgoog_n0662_1 (picture_size 0.7201, title 'SWEALD'; its item file is
named after lead n0599_1). Both: LiDAR relief (lidar null, EA credit), sites.json before
{drawings 0, score 1.1 (t1), oldest 1842, overlays 1}, auto dep six-inch-1st.webp,
both items UNRESOLVED in the checkout, whys clean (no 'matcher'/'network'). Queue 241
entries at 2026-10-13T14:34:09.559141+00:00; next pendings [39] Neckarburken-West /
[46] Richard's Castle.

**Do not touch:** fit/surveyfit.py or task 304 (agent c); web/* (not in my Touches - the
page behaviour this task checks is done); tests/test_fit_queue.py (235 owns it - its red
test stays the only suite red); tests/conftest.py; any data file in the checkout (the
test writes only into its private tmp tree; the revert proof checks that); the other
agents' in-flight files (207a/302/306 are agent c's, on its own branch). The test binds
no fixed port (ephemeral, GUARD'd) and writes only into its tmp tree + docs/site_flow/ -
team-mode safe.
