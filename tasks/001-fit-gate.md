Status: blocked
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
- [ ] Wrong fits for the test are made from each held-out hand fit at least these ways: moved 60 m, turned 10
      degrees, scaled 15%, and the best placement the same search finds on a different site's ground. On these the
      gate accepts at most 1 in 20
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

## Hand-over (iteration 9, agent c)

**Where I am.** The build is complete and verified; the task is now formally waiting on the
owner's ruling on box 2. Boxes 1, 3, 4 ticked. Box 2 (at most 1 in 20 wrong fits) measures 1 in
8 on the one-shot held-out run (all four misses are 15% scale; docs/gate.md section 9). The
registration forbids re-tuning on the spent set, so box 2 as written is unmeetable - that is the
owner's call, now filed two ways: `## Proposed changes` (iteration 7) and a **blocking
ask_human** (this iteration, same two options, recommendation (a); filed as request 001,
.agent/asks/001.md). Status is `blocked` while that request is open, so the driver waits for
the answer instead of re-handing a complete task.

**What iteration 9 did.**
- Verified the post-merge state: `.venv/bin/python -m pytest -q` -> 10 passed in 6.5 s. The
  project-wide driver note about a failed .venv build is NOT this checkout: requirements.txt
  here is fully pinned with hashes, the local .venv works, and there is no .agent/reports/
  here. It belongs to another checkout (main's unpinned file is task 800).
- Filled PLAN.md `## Deviations from GOAL.md` (it was still "(empty)" although box 2's number
  has settled): point, what GOAL point 3 says, what the project does (1-in-8, all scale15;
  0/24 for moved/rotated/cross-site), evidence (gate.md section 7 structural limit at n=3-6,
  section 9 one-shot record, dev corroboration 2/12, the review queue and the 18/20 human
  sample as the production checks), and that it awaits the owner's ruling. Added PLAN.md to
  this task's Touches.
- Filed the blocking ask_human (recommendation: (a) accept the gate as measured) and set
  Status: blocked. No code, docs or tests changed this session.

**Next step: apply the answer to request 001.** When the task comes back with the owner's reply
(or the loop's 120-minute answer, which goes with the recommendation):
- **(a)** accept as measured: re-word box 2 to the registered contract: "On these the gate
  accepts at most 1 in 20, or the measured numbers are recorded in docs/gate.md section 9 and
  the review queue absorbs the difference" (keep the first part of the box about how the wrong
  fits are made). Tick it, set Status: done, commit.
- **(b)** keep box 2 as written: leave it unticked, set Status: open, and file a new
  top-level task **801** (next free number in 800-1099) for a tighter rule re-derived on fresh
  documents (new hand fits as they are made in production, fresh seed; Depends on: none;
  Touches: its own new module + a NEW section >= 10 of docs/gate.md, additive - never edit
  sections 1-9).
- Anything else: follow the ruling literally and record it in DECISIONS.md.

**Docs discipline (critical, unchanged):** docs/gate.md sections 1-8 are the frozen
pre-registration - never edit them (a change voids the measurement); section 9 is the spent
one-shot record - never edit that either. The held-out documents' contents were read by the
one-shot run only; any future gate work uses them as a fixed measurement, never as tuning data.

**Team-mode boundaries (unchanged):** I own pipeline/fit_gate.py, tools/gate_heldout.py,
docs/gate.md, tests/test_gate.py, tests/golden/, and the PLAN.md Deviations section. The 20
hand-fit docs in data/db/platefits/ and web/data/sites.json are READ-ONLY.
