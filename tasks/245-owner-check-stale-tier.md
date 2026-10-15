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
- [ ] The owner_check pair passes with the fix: in two or three consecutive unflagged runs
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

(2026-10-15, iteration 213, agent c - **box 1 verified and ticked this session**; boxes
2-4 remain; the it.249 carve session may have moved some of them - re-read first).

**State:** branch agent/c = main (HEAD 747ca6fb) + driver bookkeeping. 815 (subpixel
`addPairMarker`) is DONE on main (f160ae5a; audit: site squares 513 and scan-area labels
1255 stay integer). 814/816 done (the probe carries the 816 recipe: JS `settle` 292 +
`subpixel` 310, awaited at the eight sites 334-422; the "line effect (b)" check at 417).
812/813/810/811 OPEN - agent a runs 810/812 (the it.235 double-shot + refresh-flag build
survives verbatim at 3579c22b; the file was replaced by 693b0ea3 = "814 taken over from
agent c"). **Regime = old R5:** zero `AW_OWNER_REFRESH|SNAPSHOT_VIEWS|_shot_diff` hits in
the file -> unflagged runs still re-copy all ten 307d PNGs -> after EVERY run restore each
to main's bytes (box 4; 813's refresh flag retires this once it lands).

**Box 1 (ticked this session, evidence in DECISIONS):** (a) `git diff ab57da1b^..ab57da1b
-- web/index.html` = only the `saveFit` hunk (one-shot fetch -> bounded re-fetch loop);
(b) `git diff ab57da1b..HEAD -- web/index.html` = only 815's 4-line `addPairMarker` hunk
(disjoint function) -> no other line moved; (c) re-read the loop where it now sits
(function at 1186, loop 1208-1217): `prevOverlays = s.overlays`; <=8 fetches of
`data/sites.json?t=` at 250 ms; each fetch adopts drawings/score/oldest/overlays; break on
`prevOverlays == null || s.overlays == null || s.overlays > prevOverlays` (missing on
either side = pre-fix single-fetch behaviour); marker-class line, source cleanup,
`endFit(); applyDep(s); return;` and the 60x1.5 s timeout fallback all unchanged;
(d) node --check: all six script blocks OK (inline + review/fitqueue/fitkit + 2 vendor).

**PNG state (box 4's subject; why the worktree shows three modified 307d PNGs that are
correct, not dirt):** my branch's HEAD carried three re-encoded 307d PNGs (A_1-card,
B_1-card, B_5-reload) diverging from main - the driver's bookkeeping commit 23574871
swallowed re-encodings from my it.212 815 lane (this VM's re-encode differs from main's;
B_1-card is NOT immune on this VM, contrary to agent a's observation). All ten are now at
main's bytes in the worktree (`git show main:<f> > <f>` on the three differing; the other
seven already matched), left UNSTAGED: my commits carry no PNG hunks (a 245 commit
carrying a web/ or PNG hunk is a red flag); the driver's next snapshot commits the
restorations and the branch's PNG state converges to main. The it.249 carve prompt lists
exactly these three files as staying with 245 - box 4 is the discipline over them.

**Carve in flight (read this first next session):** an it.249 CARVE session was running
concurrently at my orient (ps); it carves 245's unticked boxes into new 200-499 top-level
tasks that other agents build beside me, and the driver marks the moved boxes in this
file when it lands (the carve never writes into my checkout). Next session: re-read the
box list below and the driver's notes in PROGRESS.md; run ONLY what is still mine. If a
box was carved out, its new task owns it - do not re-run it.

**Remaining work (only for boxes still in this file):**
- **Box 2:** three consecutive unflagged pair runs, one invocation each (A then B inside
  each): `TMPDIR=/tmp/loop-ancient-works.c .venv/bin/python -m pytest
  tests/test_owner_check.py -q -p no:cacheprovider -o tmp_path_retention_policy=all`
  (TMPDIR = my lane, confirmed in the session env; `--tmp-retention-policy` is NOT a valid
  pytest 9.1.1 flag). Per run: both tests pass; in BOTH probe logs
  (`$TMPDIR/pytest-of-agent/pytest-<N>/owner{A,B}0/owner_probe.log`) `line effect (b): the
  site's square takes its new score's tier` is `[ok]`; record any `[warn] settle`. After
  EACH run: `git diff main --name-only -- docs/site_flow/` -> for every differing 307d PNG
  `git show main:docs/site_flow/<f> > docs/site_flow/<f>` (check ALL ten, not just the
  known three). Expect ~65 s per run (it.236: 64.5/65.9/66.7; 815: 69-74), zero [warn]
  settle. Optional: throwaway PIL cross-run compare (ten views, per-channel >32) - expect
  ~0.000%; never commit the script.
- **Box 3:** full suite, the driver's exact command: `TMPDIR=/tmp/loop-ancient-works.c
  .venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~10.5 min; last baseline
  195P/1S/0F, 631 s). Before starting: `ps -eo pid,ppid,etime,args | grep -E
  "pytest|serve.py|runpy|watchlogs"` (no live run in another checkout; kill only MY
  checkout's PPID-1 orphans) and `df -h /` (a run needs ~3.5G headroom; <2G free = Errno
  28 cascade, PITFALLS 377-380). Attribute reds: a red also on the same-day main baseline
  (driver's newest loop-start note in PROGRESS) = not mine (log it); a red naming
  tests/test_owner_check.py or the 307d PNGs = my lane - fix or block, never weaken.
- **Claim:** tick the remaining boxes, `Status: done`; the commit carries the task file +
  DECISIONS.md only (no web/, no PNGs).

**If "line effect (b)" reds again after the fix:** (carried from it.236) the re-fetch
signal misfired (most likely: the pre-save in-memory entry lacked `overlays`, so the loop
broke after the first fetch) - record the probe's [eval] effects block (markerClass vs
tier vs score) in DECISIONS and re-derive; the diagnostic signature is effects-RED /
reload-GREEN (the reload section fetches fresh and passes). Never clear it by loosening
the check or moving the wait to the test side - the one-shot adoption is a fact by then;
a longer poll cannot un-adopt it.

**it.236 evidence (kept as history):** pre-fix run 1: A passed, B RED at "line effect (b)"
(markerClass "marker t1" vs tier "t2"; pre-save 1.1 -> post 1.45; the probe's 120 s poll
never saw a change - the one-shot adoption was done; 186 s, the poll ran out). Post-fix
runs 2-3: both passed (64.5/65.9 s), `[ok]` for A and B in EVERY run, zero [warn] settle;
cross-run all ten views 0.000% (PIL per-channel >32). Those runs predate the 815 hunk
(page hunk byte-identical since; R5: fresh runs at claim time).
