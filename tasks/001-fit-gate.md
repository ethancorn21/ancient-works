Status: open
# 001: The fit gate, measured on held-out hand fits
Depends on: none
Touches: pipeline/, tools/, docs/gate.md, tests/

## Goal
A program decides whether a proposed fit of an old drawing (point pairs, or a placement found by a search) is good
enough to show on the map without the human looking at it. It must be measured on the existing hand fits before it
is trusted: the hand fits are the only fits known to be right. Everything the gate does not accept goes to the review
queue (GOAL.md point 1), so a strict gate is fine; a gate that accepts wrong fits is not.

## Acceptance criteria
- [ ] `docs/gate.md`, written and committed BEFORE the gate is first run on the held-out set, says: which hand fits
      are held out (at least 8, chosen by a recorded random seed, never looked at while building the gate), the rule
      the gate applies, its thresholds, and how a wrong fit is made for the test
- [ ] Wrong fits for the test are made from each held-out hand fit at least these ways: moved 60 m, turned 10
      degrees, scaled 15%, and the best placement the same search finds on a different site's ground. On these the
      gate accepts at most 1 in 20
- [ ] On the held-out hand fits themselves the gate accepts at least half (if it cannot, `docs/gate.md` says so with
      the numbers, and the project sends every fit to the review queue instead)
- [ ] The results table is in `docs/gate.md`, with the command that reproduces it, and a test re-runs it

## Notes
- `docs/autofit.md` section 4, finding 2: random placements are not a fair null; a searched fit beats them easily.
- The numbers here are the owner's intuition; settle a different number only with evidence of what he would notice.

## Hand-over (iteration 6, agent c)

**Where I am.** Steps of the plan: (1) fit_gate.py = DONE this session, committed; (2) tools/gate_heldout.py
= next; (3) one-shot run = the session after (or the same, after committing the tool); (4) tests/test_gate.py
= after the run. `docs/gate.md` remains as committed in iteration 5 (the registered version); only its
section 9 may change later (append-only, separate commit). The 8 held-out docs remain UNREAD — the one-shot
run is still the authorized first look; do not open any held-out file by hand before it (names only, as the
selection rule needs).

**What iteration 6 did.** Wrote `pipeline/fit_gate.py` implementing gate.md §2 exactly:
`gate(pairs, transform=None) -> (verdict, stats)`, stats = {n, med, slope_o, io} (ground metres); transform is
a Web-Mercator similarity (a, b) scored as T(w) = k(a w + b), k = cos(mean anchor latitude); transform None =
the canonical `plan_fit.similarity` (read-only import, same code path — canonical r equals plan_fit's own
residuals to 6e-10 m); constants N_MIN=3, RHO2_MIN=1.0 m², MED_MAX=45, SLOPE_MAX=0.145, SLOPE_PATTERN=0.11,
IO_MIN=−10, verbatim from §2; n<3 or Σρ²<1 → REJECT with nan pattern stats. Proven correct without touching
held-out data: a throwaway script ran all 12 dev docs × the 5 placements and reproduced every number recorded
in gate.md §5 to its stated precision (true 10/12 accepted, rejected = berkhamsted slope 0.2297 and old-sarum
c_8192 0.1611/io −20.3; moved med 59.1–68.5; rot10 med 12.3–75.9, slope 0.1747–0.2296 with floor 2·sin5°=0.1747
exact; scale15 slope 0.1305–0.2399, the 2 accepted = castle-rising 15.8/0.1409/−8.7 and whitley
11.7/0.1355/−7.4 = 2/48 wrongs = 1 in 24; xsite med 19.5 km–7734 km). Existing suite (8 tests of other
tasks) passes, 2.45 s.

**Next step: write `tools/gate_heldout.py` (step 2), commit it, then in the SAME or NEXT session do the
one-shot run (step 3).** The tool (deterministic, offline, numpy-only, no ports, no writes outside the repo;
usage `tools/gate_heldout.py [--set held|dev]`, default held):
1. Re-derive the partition: names = sorted basenames (minus .json) of `data/db/platefits/*.json` (20);
   held = {names[int(i)] for i in numpy.random.default_rng(20260108).choice(20, 8, replace=False)} — index
   the list element by element, a Python list does not accept a numpy-array index; dev = the complement.
   With `--set held` assert the derived 8 equal the names listed in gate.md §3 (fail loudly if not).
2. For each doc D of the set, read its JSON (pairs = D's own pairs — the doc's `site` field is its site id).
   Canonical: a, b = plan_fit.similarity(pairs)[:2]; k = aw.ground_scale(mean anchor lat); C = mean(k(a w + b))
   (ground-metre centroid); C_m = C/k. The five placements, as (a', b') in Web-Mercator (verified this
   session to reproduce §5; the full-transform form is a PITFALLS entry — do not use the short form):
   - true: (a, b)
   - moved: (a, b + 60/√2·(1+1j)/k)
   - rot10: (e^(i·10°)·a, e^(i·10°)·b + (1 − e^(i·10°))·C_m)
   - scale15: (1.15·a, 1.15·b − 0.15·C_m)
   - xsite: (a, b + (C_next − C)/k), C_next = ground-metre box centre of the NEXT site of THIS set: site ids
     of the set (doc["site"]), sorted, next index cycling (8th wraps to 1st for held; 12 dev docs for dev);
     box centre = mean of the site's `corners` ([[lon, lat]...] in web/data/sites.json) → aw.to_merc → ×
     aw.ground_scale(site lat).
   Score each with fit_gate.gate(pairs, (a', b')).
3. Print, for docs in sorted order and cases in order true, moved, rot10, scale15, xsite, one fixed-format
   line each: `<doc>  <case>  n=<n>  med=<x.1f>  slope_o=<y.4f>  io=<z.1f>  <verdict>` (the exact stdout is
   what gets appended to §9, so keep it machine-stable; no timestamps, no absolute paths).
4. ONE-SHOT RUN (exactly once, first read of held-out contents, only AFTER the tool is committed):
   `.venv/bin/python tools/gate_heldout.py`. Capture the stdout verbatim; in a SEPARATE commit append it to
   gate.md §9 (replacing the placeholder) with a summary line: how many of the 32 wrong rows were accepted
   and which, how many of the 8 true rows, and the verdict on §6's pass criteria (wrong ≤ 1/32; true ≥ 4/8).
   Then evaluate §6: true < 4 → project sends every fit to the review queue (no auto-accept); wrong > 1/32 →
   DO NOT re-tune (that voids the registration) — record the numbers, the review queue absorbs it. Do not
   "peek" at held-out docs to check the outcome: the numbers come from the run.

**Step 4 (after §9 is committed):** `tests/test_gate.py` — re-run the conjunction on dev AND held-out via
tools/gate_heldout (import it or call fit_gate directly), compare the generated table against the committed
golden (e.g. tests/golden/gate_heldout.txt: the 40 held-out rows + 60 dev rows) and pin fit_gate's constants
to gate.md §2 (a drift in a constant fails the test). No fixed ports, no network, writes only in project +
temp dir. Note conftest.py exists but this test needs no server fixture — plain pytest is fine (pytest 9.1.1
is in requirements.txt; the driver's venv rebuild picks it up).

**Team-mode boundaries (unchanged):** I own pipeline/fit_gate.py, tools/gate_heldout.py, docs/gate.md
(§9 append only — never touch §1–8), tests/test_gate.py, tests/golden/. The 20 hand-fit docs in
data/db/platefits/ and web/data/sites.json are READ-ONLY (never change/delete — GOAL).

**Environment note:** .venv here is current (numpy 2.5.4, scipy 1.18.1, pytest 9.1.1 — I installed pytest
into the LOCAL venv this session for my own runs; the driver rebuilds its venv from requirements.txt before
its test runs regardless). The driver's "requirements.txt not pinned" note in PROGRESS is stale for this
checkout, confirmed twice (0 unpinned requirement lines; the `# via` lines are comments). If the driver
re-flags it, check whether a merge into main changed requirements.txt — it is not in my Touches, so I cannot
fix it in my branch.
