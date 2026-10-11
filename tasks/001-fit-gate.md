Status: done
# 001: The fit gate, measured on held-out hand fits
Depends on: none
Touches: pipeline/, tools/, docs/gate.md, tests/, PLAN.md

## Goal
A program decides whether a proposed fit of an old drawing (point pairs, or a placement found by a search) is good
enough to show on the map without the human looking at it. It must be measured on the existing hand fits before it
is trusted: the hand fits are the only fits known to be right. Everything the gate does not accept goes to the review
queue (GOAL.md point 1), so a strict gate is fine; a gate that accepts wrong fits is not.

## Acceptance criteria
- [x] `docs/gate.md`, written and committed BEFORE the gate is first run on the held-out set, says: which hand fits
      are held out (at least 8, chosen by a recorded random seed, never looked at while building the gate), the rule
      the gate applies, its thresholds, and how a wrong fit is made for the test
- [x] Wrong fits for the test are made from each held-out hand fit at least these ways: moved 60 m, turned 10
      degrees, scaled 15%, and the best placement the same search finds on a different site's ground. On these the
      gate accepts at most 1 in 20, or the measured numbers are recorded in docs/gate.md section 9 and the review
      queue absorbs the difference (re-worded per the owner's ruling, .agent/asks/001.md: option (a), the
      registered contract)
- [x] On the held-out hand fits themselves the gate accepts at least half (if it cannot, `docs/gate.md` says so with
      the numbers, and the project sends every fit to the review queue instead)
- [x] The results table is in `docs/gate.md`, with the command that reproduces it, and a test re-runs it

## Notes
- `docs/autofit.md` section 4, finding 2: random placements are not a fair null; a searched fit beats them easily.
- The numbers here are the owner's intuition; settle a different number only with evidence of what he would notice.

## Proposed changes

Box 2 ("on these the gate accepts at most 1 in 20") cannot be met by this gate, and the
registration forbids making it so: the one-shot run (recorded in `docs/gate.md` section 9)
accepted 4 of 32 wrong placements (1 in 8), all 15% scale errors, and section 6 says the
thresholds must not be re-tuned on the held-out set (that would void the measurement). The
misses are the documented limit of section 7: at n = 3-6 anchors a 15% scale's residual
pattern is indistinguishable from a true fit's own scatter (the dev set shows the same
2 of 12, section 5). Options:

- (recommend) Accept the gate as measured. It does what the gate is for: the true fits it
  must not mangle pass 7/8 (the one refusal, cadbury-castle, is a genuinely radial fit the
  gate cannot see as true at n = 4), and moved / rotated / cross-site wrong fits pass 0/24.
  The residual 1-in-8 acceptance of 15% scale errors is exactly what GOAL point 1's review
  queue and GOAL point 3's 18/20 human sample of auto-accepted fits are the check for.
  Re-word box 2 to the registered contract: "wrong fits: at most 1 in 20, or the measured
  numbers are recorded in docs/gate.md section 9 and the review queue absorbs the
  difference".
- (alternative) Keep box 2 as written: the task stays not-done, and a tighter rule can
  only be derived later on fresh documents (new hand fits as they are made in production,
  a fresh seed — section 9's last line). That would be a future task, and the gate stays
  at 1 in 8 until it.

**Resolved 2026-10-11 (owner, .agent/asks/001.md: "Use your recommendation")**: (a) applied - box 2
re-worded to the registered contract and ticked; task done; no task 801 filed.

## Hand-over (iteration 19, agent c)

**Task done.** The owner ruled on request 001 (.agent/asks/001.md, closed): "Use your
recommendation" = option (a), accept the gate as measured. Applied this session, in the task
file only:
- box 2 re-worded to the registered contract: "On these the gate accepts at most 1 in 20, or
  the measured numbers are recorded in docs/gate.md section 9 and the review queue absorbs the
  difference"; first part of the box (how the wrong fits are made) unchanged; ticked.
- all four boxes now ticked; `Status: done`.
- `## Proposed changes` marked resolved ((a) applied; no task 801 filed - (b) was not chosen).
- PLAN.md `## Deviations from GOAL.md` bullet updated to the applied ruling.
- DECISIONS.md entry logging the ruling and the application.

No code, docs/gate.md or tests changed this session: nothing needed changing - the re-worded
box references the already-frozen section 9 record (measured: 4 of 32 wrong placements
accepted, all 15% scale; 7 of 8 held-out hand fits accepted; 0 of 24 moved/rotated/cross-site
accepted). Verification after the main merge: `.venv/bin/python -m pytest -q` -> 12 passed,
8.9 s (iteration 9 had 10; the two extra tests come from other tasks' work merged into main).

**If anything reopens this task** (docs discipline, unchanged): docs/gate.md sections 1-8 are
the frozen pre-registration - never edit them (a change voids the measurement); section 9 is
the spent one-shot record - never edit it either; future gate work may only add NEW numbered
sections (>= 10, additive). The held-out documents' contents were read by the one-shot run
only: use them as a fixed measurement, never as tuning data. A tighter rule, if ever wanted,
is a fresh top-level task re-derived on fresh hand-fit documents with a fresh seed - none is
filed.

**Team-mode boundaries (unchanged):** I own pipeline/fit_gate.py, tools/gate_heldout.py,
docs/gate.md, tests/test_gate.py, tests/golden/, and the PLAN.md Deviations section. The 20
hand-fit docs in data/db/platefits/ and web/data/sites.json are READ-ONLY.
