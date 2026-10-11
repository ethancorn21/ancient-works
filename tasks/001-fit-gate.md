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

## Hand-over (iteration 5, agent c)

**Where I am.** `docs/gate.md` (pre-registration) is WRITTEN, VERIFIED and COMMITTED in this session — this
commit is the registered version; it contains no held-out numbers (§9 is a placeholder). The 8 held-out docs
remain UNREAD: this session touched only their file names (to re-verify the seed partition, which reproduced
exactly: seed 20260108 → the 8 names in gate.md §3, dev = exact complement of 12). The one-shot run is the
AUTHORIZED FIRST LOOK and must happen AFTER this commit (it does: next session).

**Next steps, in order (each can be its own session; gate.md §6/§8 define the rest):**
1. `pipeline/fit_gate.py` — implement EXACTLY gate.md §2. Thresholds as module constants matching §2 verbatim:
   N_MIN=3, RHO2_MIN=1.0 (m², degenerate: dev min Σρ² ≈ 7.5k m², so 1 m² is orders below any real input),
   MED_MAX=45, SLOPE_MAX=0.145, SLOPE_PATTERN=0.11, IO_MIN=−10 (m). `gate(pairs, transform=None) →
   (verdict, stats)`; transform None → canonical `plan_fit.similarity` (Web-Mercator complex LS, k =
   cos(mean-lat)); stats dict = {n, med, slope_o, io}. No images, no network, numpy-only; imports
   `aw`/`plan_fit` read-only; header comment for CODEMAP.
2. `tools/gate_heldout.py` — re-derives the partition from `data/db/platefits/` filenames with the EXACT rng
   call of gate.md §3 (`default_rng(20260108).choice(20, 8, replace=False)` over sorted names); for each doc of
   `--set {held (default), dev}` builds the 5 placements of §4 (true, moved 60/√2·(1+i) NE, rot10 about C,
   scale15 about C, xsite = shift to next site's box-centre C_next = mean of that site's `corners` in
   `web/data/sites.json`, Mercator ×k, held-out site ids sorted + cyclic — see §4 for the exact cycle) and
   prints the table: doc | case | n | med | slope_o | io | verdict. Deterministic, offline, no writes outside
   the repo, no ports.
3. ONE-SHOT RUN (exactly once, this is the first look at held-out): `.venv/bin/python tools/gate_heldout.py`.
   Capture output; append it as gate.md §9 in a SEPARATE commit; then evaluate §6: wrong ≤ 1 of 32 accepted,
   true ≥ 4 of 8. If true < half: record numbers in §9, project sends every fit to the review queue (no
   auto-accept). If wrong > 1-in-20: DO NOT re-tune (that voids the registration) — record in §9, review queue
   absorbs it. Expected from dev: 0–2 wrong, 6–7 true.
4. `tests/test_gate.py` — re-runs the same conjunction on dev + held-out (both in-repo, offline) and compares
   against the committed golden (e.g. tests/golden/gate_heldout.txt: 40 held-out + 60 dev rows, from step 3's
   `--set held` and `--set dev` output); also pins fit_gate's constants to gate.md §2. No fixed ports, no
   network, writes only in project + temp dir.

**Team-mode boundaries (unchanged):** I own `pipeline/fit_gate.py`, `tools/gate_heldout.py`, `docs/gate.md`,
`tests/test_gate.py` only. The 20 hand-fit docs in `data/db/platefits/` and `web/data/sites.json` are READ-ONLY
(never change/delete — GOAL). The held-out docs' contents must first be read by the one-shot run, never by
hand before it.

**Environment note:** `.venv` builds and works here (numpy 2.5.4, scipy 1.18.1, PIL import fine); the
PROGRESS driver note "requirements.txt not pinned" is stale for this checkout (verified: every requirement
pinned `==` with sha256 hashes; the unpinned-looking lines are `# via` comments). If the driver re-flags it
after a merge, check whether another task's merge unpinned something in main first — requirements.txt is not
in my Touches.

**Key facts (unchanged from iteration 4, authoritative record = DECISIONS.md spike-7 entry):** rule =
REJECT if n<3 or Σρ²<1 or med>45 m or slope_o>0.145 or (slope_o>0.11 and io<−10); dev calibration: 48 wrong →
2 accepted (castle-rising/whitley scale15, indistinguishable at n=4–6), 12 true → 10 (berkhamsted, old-sarum
c_8192 have genuinely radial own-residuals); dev n = 3–6, max ρ = 86.6–530.5 m (checked this session,
dev-only). Gate's documented blind spot = consistent global error (anchors AND placement off together) →
backstop: GOAL pt 3 human 18/20 sample + review queue. Re-read after step 3: gate.md §9 — confirm the
committed table matches a fresh `tools/gate_heldout.py` run (determinism check), and that no step-1/2 code was
looked at for tuning (if you were tempted to, stop: it voids the registration).
