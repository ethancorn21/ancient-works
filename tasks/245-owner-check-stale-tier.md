Status: open
Depends on: 815
Touches: web/index.html

# 245: The 307d owner check - the marker keeps the pre-rescore tier: saveFit's one-shot sites.json fetch

Filed 2026-10-15 (iteration 236, agent a, on the 230/242/810-814 cycle branch): the owner_check
pair, with the 814/816 settle + subpixel fix in, passed A end to end and red'd B for the first
time at a NEW step - "line effect (b): the site's square takes its new score's tier" - so this
is not the mid-transition flake (that one is fixed) and not a test defect: it is a product
race the test caught, and the cycle's green-suite gate (230's claim, 810's box 3, 242's box 2)
cannot be reliable while it stands. Built on agent/a's branch this iteration (the driver
carried the whole cycle to one agent so the tests pass with all of it in place); the 815 lane
(the page-side subpixel, same file) is what this task waits on for the claim.

## Why this task exists (the measured race, do not re-derive)

The save path (the test's hermetic server is the real one: `server/serve.py` runs
`tools/site_done.py`'s one-site line in a worker thread, which builds the overlay first and
re-scores the site second - the score is computed FROM the built overlays, so the order is
mandatory, `pipeline/build_site.py::marks`):

1. page PUTs the platefit doc; the worker syncs it: the site's `depictions.json` gains the new
   depiction entry (B's run: 01:57:23.310);
2. the worker then runs `build_site.set_drawings`, rewriting `web/data/sites.json` with the
   re-scored entry (01:57:23.429) - **119 ms later** (the ink build itself takes ~6.5 s, but the
   gap the page can land in is the depiction->re-score beat).

`saveFit()` (web/index.html) polls `depictions.json` every 1.5 s for the saved depiction and,
the moment it appears, fetches `data/sites.json` ONCE, adopts `drawings/score/oldest/overlays`
into the in-memory entry and sets the marker class from that fetch, then stops. A poll landing
in the 119 ms gap adopts the PRE-rescore score and the marker keeps its old tier until a
reload. Measured on 2026-10-15 (devil-s-dyke-q3307343, the pair's derived B pick): pre-save
score 1.1 (tier t1), post-save 1.45 (tier t2); the page's fetch landed in the gap, the live
marker read "marker t1" for the probe's full 120 s poll, and only the reloaded page showed the
correct "marker t2". The same run's A pick (richard-s-castle) won the race: its fetch landed
after the re-score and the class came out t2. The window is small (P per save ~10%) but it is
on the owner's own save path: the owner would see the wrong square tier until a manual reload.
The one-site line's own print ("plan_fit.py has re-scored the site in sites.json: take its new
tier") states the page's intent - taking the stale score is not a design, it is a race.

The pipeline order cannot be changed (the re-score reads the built depictions), the server
cannot push (the page polls files over HTTP; sockets are dead in the hermetic run by design),
so the fix is the page's adoption: re-fetch until the re-score has landed, bounded, before
setting the marker class.

## Goal

In `saveFit()` in web/index.html only. When the saved depiction appears in `depictions.json`,
replace the one-shot `sites.json` fetch with a bounded re-fetch loop: adopt
`drawings/score/oldest/overlays` from each fetch, and stop as soon as the fetched entry's
`overlays` count exceeds the in-memory pre-save value (the re-score ran for this save: the new
depiction is counted by `overlays()`); a missing `overlays` on either side keeps today's
single-fetch behaviour (no wait). Budget: 8 fetches at 250 ms (the re-score finishes within a
second of the depiction; the page must never hang on it - after the budget the existing
proceeds with what it has, exactly as today when the entry was missing). No other change: the
marker-class line, `endFit()`, `applyDep(s)` and the timeout fallback keep their behaviour; no
other function touched; the 815 page-side subpixel (same file, different function) is a
separate task this one depends on.

## Acceptance criteria

- [x] The fix is applied in `saveFit()` as designed (the one-shot fetch becomes the bounded
      re-fetch loop; everything else in the function and the file unchanged - diff review:
      no other line moved); the page still passes its own syntax check (extract the script
      block, `node --check`).
- [x] The owner_check pair passes with the fix: in two or three consecutive unflagged runs
      (one invocation each, A then B) the check "line effect (b): the site's square takes its
      new score's tier" is `[ok]` in EVERY run (pre-fix it red's when the 1.5 s poll lands in
      the depiction->re-score gap - measured 119 ms on 2026-10-15; the page's own adoption
      then takes the stale score no matter how long the probe polls, so no test-side wait can
      clear it - this check is the pair's regression gate for the race).
- [ ] No new red against the branch's suite at claim time
      (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).
- [ ] After ANY owner_check run the ten docs/site_flow/307d_*.png are restored to the
      committed bytes before committing (R5; 813's refresh flag retires this once it lands).

## Notes

- The reload-side check already asserts the same tier after a full page load (it fetches
  fresh), so a race that survives this fix would show as effects-red/reload-green - that
  split is the diagnostic signature if the loop's signal ever misfires.
- The signal choice: `overlays` (the built-overlay count, always incremented by the saved
  depiction) rather than `score` (which can stay value-equal across a rescore) or `drawings`
  (which only moves for drawing-kind fits). `marks()` sets all three from `overlays()`/
  `drawings()`; the page already copies all four fields.
- B's run artifacts that prove the timeline (retained 2026-10-15, /tmp/loop-ancient-works.a,
  pytest-of-agent/pytest-0/awowner0): doc write 01:57:15.802, base overlay 01:57:16.816, ink
  overlay 01:57:23.309, depictions.json 01:57:23.310, sites.json 01:57:23.429, review.json
  01:57:23.846.

## Hand-over

(2026-10-15, iteration 214, agent c - **box 2 verified and ticked this session**;
boxes 3-4 remain; the next step is the box 3 full suite).

**State:** branch agent/c = main (HEAD 747ca6fb) + driver bookkeeping only. The it.249
carve did NOT move a box (no carve marks in this file, no new 200-499 tasks, no driver
note in PROGRESS) -> boxes 2-4 all still mine. Regime = old R5 (zero
AW_OWNER_REFRESH|SNAPSHOT_VIEWS|_shot_diff hits in tests/test_owner_check.py) ->
unflagged runs re-copy all ten docs/site_flow/307d_*.png -> after EVERY owner_check run
restore each to main's bytes before committing (box 4; this retires once 813's refresh
flag lands). 815 DONE on main (f160ae5a); 812/813/810/811 OPEN - agent a runs 810/812 in
its own checkout; the three PPID-1 `816-verify/watchlogs.py` orphans under
/tmp/loop-ancient-works.a (up to 4 h old at it.214 orient) are ITS lane - leave them.
My TMPDIR = /tmp/loop-ancient-works.c (session env).

**Box 1 (ticked it.213):** the saveFit bounded re-fetch loop is on main exactly as
designed (fix commit ab57da1b = one hunk; diff since = only 815's 4-line
addPairMarker hunk; six script blocks node --check clean; the loop re-verified intact
at web/index.html 1211/1215 this session, no web/ delta since).

**Box 2 (ticked this session):** three consecutive unflagged pair runs, one
invocation each (A then B inside each): `TMPDIR=/tmp/loop-ancient-works.c
.venv/bin/python -m pytest tests/test_owner_check.py -q -p no:cacheprovider -o
tmp_path_retention_policy=all` -> 2 passed each (65.02 / 66.70 / 66.06 s). In BOTH
probe logs of ALL six probes (`$TMPDIR/pytest-of-agent/pytest-{0,1,2}/owner{A,B}0/
owner_probe.log`) `line effect (b): the site's square takes its new score's tier`
is `[ok]`; zero `[warn] settle` in all six. After each run exactly the three known
dirty PNGs (A_1-card, B_1-card, B_5-reload) -> all ten restored to main's bytes after
each run; `git diff main -- docs/site_flow/` empty before this commit. it.236's
pre-815 green runs stay as history below; these it.214 runs supersede them for the
claim (R5).

**The optional cross-run PIL compare was NOT possible this session (do not
re-derive):** this environment keeps only the LATEST run's pytest-N dir after each
green run, no matter what `-o tmp_path_retention_policy=all` does. Measured
(it.214): my three owner runs left only pytest-2 at the end; a 4-run dummy loop left
one dir per run; adding `-o tmp_path_retention_count=10` kept all (and pruned the
stale older ones exactly per the keep arithmetic). Cause (verified in pytest 9.1.1
source): the policy knob only gates the green-run whole-basetemp rmtree ("failed");
the numbered-dir cleanup always uses `keep = retention_count` (all and failed alike;
only "none" sets 0) and deletes dirs numbered <= max-keep whose lock file is
gone/stale - and every session unlinks its own lock at exit, so the next session
prunes all but the newest. The count comes from pytest.ini (1/failed), mirrored by
the driver's agent-loop export PYTEST_ADDOPTS (the same two -o flags) for every
session child. PITFALLS entry added under `### pytest (9.1.1, project .venv)`:
cross-run compares need `-o tmp_path_retention_count=N` or copy-out after each run.
If the PIL compare is still wanted for the claim: two runs with `-o
tmp_path_retention_count=10`, then a throwaway per-channel >32 compare of the ten
views (expect ~0.000%); never commit the script.

**Remaining work:**
- **Box 3 (next step):** the driver's exact full-suite command: `TMPDIR=
  /tmp/loop-ancient-works.c .venv/bin/python -m pytest tests/ -q -p
  no:cacheprovider` (~10.5 min; last baseline on main: 195P/1S/0F, 631 s, f160ae5a).
  Before starting: `ps -eo pid,ppid,etime,args | grep -E "pytest|serve\.py|runpy|
  watchlogs"` (no live run in another checkout; kill only MY checkout's PPID-1
  orphans - never agent a's lane) and `df -h /` (a run needs ~3.5G headroom; <2G free
  = Errno 28 cascade, PITFALLS). Attribute reds per the house rule: a red also on the
  same-day main baseline (the driver's newest loop-start note in PROGRESS) = not mine
  (log it in DECISIONS); a red naming tests/test_owner_check.py or the 307d PNGs = my
  lane - fix or block, never weaken. If the suite's own owner_check run reds at "line
  effect (b)": the diagnostic signature is effects-RED / reload-GREEN (the reload
  section fetches fresh and passes) -> the re-fetch signal misfired (most likely the
  pre-save in-memory entry lacked `overlays`, so the loop broke after the first
  fetch); record the probe's [eval] effects block (markerClass vs tier vs score) in
  DECISIONS and re-derive. NEVER clear it by loosening the check or moving the wait
  to the test side - the adoption is a fact by then; a longer poll cannot un-adopt it.
- **Box 4 (discipline - observed on every run so far, claimed last):** after the
  box 3 suite run (it includes owner_check) too: `git diff --name-only --
  docs/site_flow/`, and for every differing 307d PNG `git show
  main:docs/site_flow/<f> > docs/site_flow/<f>` (check ALL ten, not just the known
  three); `git diff main --stat -- docs/site_flow/` must be empty before the claim
  commit.
- **Claim (after box 3):** tick boxes 3 and 4, `Status: done`; DECISIONS entry with
  the suite result + the PNG cleanliness; the commit carries ONLY the task file +
  DECISIONS.md (+ PITFALLS.md if new) - no web/, no PNGs (a 245 commit carrying a
  web/ or PNG hunk is a red flag for the driver).

**it.236 evidence (kept as history):** pre-fix run 1: A passed, B RED at "line effect
(b)" (markerClass "marker t1" vs tier "t2"; pre-save 1.1 -> post 1.45; the probe's
120 s poll never saw a change - the one-shot adoption was done; 186 s, the poll ran
out). Post-fix runs 2-3: both passed (64.5/65.9 s), `[ok]` for A and B in EVERY run,
zero [warn] settle; cross-run all ten views 0.000% (PIL per-channel >32). Those runs
predate 815 (the page hunk is byte-identical since) - superseded by the it.214 runs.
