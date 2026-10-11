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
