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
- [x] `docs/gate.md`, written and committed BEFORE the gate is first run on the held-out set, says: which hand fits
      are held out (at least 8, chosen by a recorded random seed, never looked at while building the gate), the rule
      the gate applies, its thresholds, and how a wrong fit is made for the test
- [ ] Wrong fits for the test are made from each held-out hand fit at least these ways: moved 60 m, turned 10
      degrees, scaled 15%, and the best placement the same search finds on a different site's ground. On these the
      gate accepts at most 1 in 20
- [x] On the held-out hand fits themselves the gate accepts at least half (if it cannot, `docs/gate.md` says so with
      the numbers, and the project sends every fit to the review queue instead)
- [ ] The results table is in `docs/gate.md`, with the command that reproduces it, and a test re-runs it

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

## Hand-over (iteration 7, agent c)
## Hand-over (iteration 7, agent c)

**Where I am.** Steps: (1) fit_gate.py = DONE (iter 6); (2) tools/gate_heldout.py = DONE,
committed 67c9f14; (3) ONE-SHOT RUN = DONE this session, results recorded in gate.md §9,
committed fdc37a0 (separate commit, as the registration demands); (4) tests/test_gate.py =
NEXT step. Docs discipline now: gate.md §1–8 are the frozen registration (7d51438) — never
change them (the registration is void if they do); §9 is the final, spent record — don't
alter it either. The held-out documents have been read (by the one-shot run, as
authorized): any future work on this gate must use them only as a fixed measurement, never
as tuning data.

**What iteration 7 did.**
- `tools/gate_heldout.py` exactly per the previous hand-over spec: re-derives the
  seed-20260108 partition from the directory listing and asserts it against the registered
  §3 names (fails loudly on any universe drift, including a 21st document); builds the
  five §4 placements as Web-Mercator (a, b) with the full a*w + b composition (PITFALLS
  recipes); prints one fixed-format line per (doc, case) — `<doc>  <case>  n=<n>  med=<x.1f>
  slope_o=<y.4f>  io=<z.1f>  <verdict>` — docs in sorted order, cases in §4 order; no
  writes, no network, no ports. Before committing, its `--set dev` run reproduced the §5
  calibration exactly (true 10/12; wrong 2/48 = castle-rising + whitley scale15; moved
  med 59.1–68.5; rot10 slope 0.1747–0.2296; scale15 band 0.1305–0.2399; xsite 19.5
  km–7734 km).
- ONE-SHOT RUN (first and only read of the held-out contents): `.venv/bin/python
  tools/gate_heldout.py`. Results: **true 7/8 accepted** (rejected: cadbury-castle's own
  fit, med 31.9, slope_o 0.1792, io −15.3 — genuinely radial, same class as the 2 dev true
  rejections); **wrong 4/32 accepted = 1 in 8** (target ≤ 1, §6 expected 0–2) — all
  scale15: avebury (28.3/0.1324/−4.9), badbury-rings (36.8/0.1310/−0.5), camp-d-attila
  (43.5/0.1438/−9.2), old-sarum n0142 (29.2/0.1344/+6.5) — the attenuated 0.131–0.144 band
  under the frozen 0.145 (dev: 0.130–0.141); moved/rot10/xsite = 0 of 24. §6 verdict:
  true passes (auto-accept stands), wrong misses → the registered no-re-tuning clause
  applies; the review queue absorbs it. Verbatim stdout + summary + verdict appended to
  §9 (fdc37a0).
- Acceptance boxes: 1 and 3 ticked (both verified). Box 2 (≤ 1 in 20) is NOT met and not
  re-tunable — see `## Proposed changes` for the decision I ask of the human. Box 4:
  table + reproduce command are in §9; the test that re-runs it is next.
- Created `tasks/800-requirements-pinned.md`: the driver's venv-build note is REAL for
  main (main's requirements.txt is the unpinned 9-line source list from e2d4060; the
  pinned compiled file lives only on this branch since iteration 1). Not in my Touches,
  so a task, not a fix (details in DECISIONS).
- Existing suite (8 tests of other tasks) still passes in the local .venv (numpy 2.5.4,
  scipy 1.18.1, pytest 9.1.1).

**Next step: write `tests/test_gate.py` (step 4), run it, tick box 4, commit.** Plan
(unchanged from last hand-over): a plain-pytest test (no server fixture needed) that
subprocess-runs the committed tool with `sys.executable` (`--set held`, then `--set
dev`), captures stdout, and compares it byte-for-byte against a committed golden
`tests/golden/gate_heldout.txt` (40 held-out lines then 60 dev lines — generate the
golden WITH the committed tool, never hand-type it); plus a check that `fit_gate`'s
frozen constants equal the ones stated in gate.md §2 (N_MIN=3, RHO2_MIN=1.0, MED_MAX=45,
SLOPE_MAX=0.145, SLOPE_PATTERN=0.11, IO_MIN=−10) so code drift from the doc fails.
No ports, no network, writes only in project + temp. After it passes: box 4 is
tickable. Then the task waits on the human's call in `## Proposed changes` (box 2): do
NOT mark the task done myself while box 2 is unticked; if the human rewords or drops
it, tick per their wording and close.

**Team-mode boundaries (unchanged):** I own pipeline/fit_gate.py, tools/gate_heldout.py,
docs/gate.md (§1–8 frozen, §9 final), tests/test_gate.py, tests/golden/. The 20
hand-fit docs in data/db/platefits/ and web/data/sites.json are READ-ONLY.
