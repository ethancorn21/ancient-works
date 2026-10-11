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

## Hand-over (iteration 4, agent c)

**Where I am.** Spike 7 (pure geometry, dev-only) is DONE and the gate conjunction is FROZEN (numbers below;
full 60-row table in `/tmp/spike7_out.txt`, script `/tmp/spike_gate7.py` — both /tmp, so the DECISIONS.md entry
is the authoritative record). Next session: (1) write + COMMIT `docs/gate.md` (pre-registration), (2) implement
`pipeline/fit_gate.py`, (3) `tools/gate_heldout.py` one-shot run → results table appended to `docs/gate.md`,
(4) `tests/test_gate.py`.

**HARD RULE: the 8 held-out docs stay UNREAD until `docs/gate.md` is committed** (re-verified this session,
seed rule holds: 20 docs, design set = bergues / castle-rising / maiden-castle / serpent-mound, seed 20260108
wins): arbor-low-q630312.earthworkenglan01allcgoog_n0597_1, avebury-q661855.earthworkenglan01allcgoog_n0581_1,
aztalan-state-park-q4832928.antiquitiesofwis00saph_n0182_1, badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1,
cadbury-castle-q1025082.c_1fab2a0abe5b99d7, cahokia-q333661.c_aff1b996dce7fe3a,
camp-d-attila-q18749222.c_6a912845c1e1aa28, old-sarum-q782719.earthworkenglan01allcgoog_n0142_1.
Dev = the other 12. This session read dev docs only.

**The gate contract (frozen).** Input: (site, plate, anchor pairs, optional placement). Anchors =
plate-pixel ↔ ground-point pairs (the doc's `pairs`; n = 3..6 in real docs, GOAL wants ≥ 4 from the model).
If no placement is given, the gate solves it with the canonical `plan_fit.similarity` (Web-Mercator complex
least squares; k = cos(lat0) ground metres per Mercator metre; a*w+b, residuals ×k). Per anchor i:
r_i = |T(w_i) − k·z_i| (ground m); C = centroid of the PROPOSED placement; ρ_i = |T(w_i) − C|; med = median(r);
slope_o = Σ r_i·ρ_i / Σ ρ_i² (through-origin fit of r on ρ); io = mean(r, inner half by ρ) − mean(r, outer half)
(odd n: drop the middle anchor).

**THE RULE (frozen, all values ground metres; dev-only tuning):**
  REJECT if  med > 45   OR   slope_o > 0.145   OR   (slope_o > 0.11 AND io < −10)
  else ACCEPT.  (Also reject n < 3 or degenerate/degenerate-ρ input — document in gate.md.)
Layer rationale: (a) med > 45 catches 60 m move (dev moved-med 59.1–68.5; dev true-med max 33.3; margin
~30% both sides) and cross-site (km–thousands km) and large rot/scale; (b) slope_o > 0.145 catches 10° turns
(dev min 0.1747 ≈ 2·sin5° — pinned by theory, margin ~20%); (c) the second pattern clause catches 15% scale
whose through-origin slope is attenuated by noise below 0.145: dev scale15 slopes are 0.130–0.240 (mass
0.130–0.141, BELOW the 0.15 theory — classical attenuation of an origin fit), so (c) uses io < −10 m as the
tie-breaker (a radial gradient lowers the inner-outer difference).

**Spike 7 results (12 dev docs × {true, moved60NE, rot10, scale15, xsite-next-dev-box}, all ground m):**
- true (12): med 2.2–33.3; slope_o 0.0075–0.230; io −20.3–+4.2. (Verified identical to the canonical
  `depictions.json fit.resid_m`: bergues 18.8/32.6, berkhamsted 17.4/21.8, old-sarum c_8192 33.3/54.4 — the old
  hand-over's 53.1/86.7 etc. were WEB-MERCATOR metres = these ×1/cos(lat) ≈ ×1.59; use ground m only.)
- moved 60 m NE (12): med 59.1–68.5 → ALL rejected by (a).
- xsite (12): med 19,461–7,734,073 m → ALL rejected by (a).
- rot 10° (12): slope_o 0.1747–0.230 → ALL rejected by (b); med 12.3–75.9 (3 also hit (a)).
- scale ×1.15 (12): 10 rejected; 2 ACCEPTED — castle-rising (med 15.8, slope_o 0.141, io −8.7) and
  whitley (med 11.7, slope_o 0.136, io −7.4): both small sites whose radial pattern falls inside true-fit
  scatter; genuinely indistinguishable at n=4–6.
- Totals: 48 wrong → 2 accepted = 1 in 24 (≤ 1 in 20 ✓); 12 true → 10 accepted (≥ half ✓). The 2 true
  rejections (berkhamsted slope_o 0.230; old-sarum c_8192 slope_o 0.161 + io −20.3) are fits whose OWN residual
  pattern is radial — indistinguishable from a 15% scale error; a strict gate may cost them.
- Thin margins to keep in mind (do NOT re-tune on held-out): calleva scale15 io −10.1 vs threshold −10;
  whitley scale15 io −7.4 vs the −10 band (it passed on slope 0.136 < 0.145); castle-rising scale15 slope
  0.141 vs 0.145. Expected held-out outcome: wrong ≤ 1–2 in 32, true ~6–7 in 8. If held-out wrong exceeds
  1-in-20, DO NOT re-tune: document the numbers in gate.md (the criterion's fallback is the review queue).

**Wrong-fit recipes (for gate.md; deterministic, no images):** take the held-out doc; true placement
Z = k(a·w + b), centroid C. moved: Z + 60/√2·(1+i) ground m NE. rot10: C + e^{i10°}(Z−C). scale15: C + 1.15(Z−C).
xsite: Z + (C_next − C), C_next = ground-metre centre of the NEXT held-out site's box (held-out site ids sorted,
cyclic). The xsite re-centre stands in for "the best placement the same search finds on a different site's
ground": the real search needs DEMs this VM lacks (and is the failed autofit machinery), but ANY placement on
another site's ground is kilometres away and is killed by (a) regardless of the exact target — state that in
gate.md. For the "true fit itself" case: placement = the transform solved from the doc's own pairs, anchors =
the same pairs → the gate scores the canonical self-residuals.

**Production use + limit (state in gate.md).** The model (GOAL pt 2) records ≥ 4 anchor pairs AND the placement
it found; the gate checks the claimed placement against the recorded anchors. It cannot see a CONSISTENT global
error (anchors and placement both 60 m off together: residuals ~0) — pure geometry cannot; that is the case
GOAL's 18/20 human sample + the review queue backstop. The 4 tested wrong types are exactly the
placement-vs-anchors disagreements the gate measures.

**Implementation notes for next session.** `pipeline/fit_gate.py`: no images, no network, numpy only (imports
`aw` + `plan_fit` read-only like the spikes); public function e.g. `gate(site, plate, pairs, transform=None) →
(verdict, stats)`; header comment for CODEMAP. `tools/gate_heldout.py`: re-derives the 20260108 partition,
builds the 4 wrong placements + true per held-out doc, prints the 32+8-row table exactly as gate.md's
reproduce command (append the table to gate.md once, after the run). `tests/test_gate.py`: offline, no ports,
no writes outside project/tmp — golden-compare the dev table (dev docs are in-repo; the held-out table is
re-runnable too since held-out docs are also in-repo — that's fine: the PRE-REGISTRATION protects the
thresholds, not the data files). Keep thresholds as module constants; the test re-runs the SAME conjunction and
compares against a committed golden file. Team-mode files I own: pipeline/fit_gate.py, tools/gate_heldout.py,
docs/gate.md, tests/test_gate.py ONLY. The 20 hand-fit docs + sites.json are read-only. `.venv` rebuilds from
pinned requirements.txt (valid since 000); keep imports numpy/scipy/PIL-level only.
