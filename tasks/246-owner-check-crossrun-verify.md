Status: done
Depends on: none
Touches: (none - verification only; runs tests/test_owner_check.py as merged and changes no file)
Split: no - atomic single-session verification: BOTH unflagged pair runs must be inside one session (the /tmp lane dies at the session boundary, PITFALLS; a green run rmtree's the whole pytest basetemp at its end, so run 1's views only survive by being copied out before run 2), and the cross-run compare needs both runs' views together; there is no subpart that can be built in parallel in another checkout (no code is written - the task runs the merged tree twice and records numbers in DECISIONS); the whole task is one ~3-minute session of two ~75 s pair runs plus a PIL compare

# 246: The 307d owner check - prove the settled regime across two unflagged pair runs (cross-run stability, the byte-identical snapshot)

Part 1 of 2 of 810's split (2026-10-15, iteration 254, per the driver: agent c had had
nothing to build for 32 minutes while every open task in the chain - 811, then 242 - waited
on 810 alone, and nothing of 810 had been built yet, so 810 now WAITS on these parts). This
task is the cross-run half of 810's verification; **247** (the full-suite green run) is the
other half and can be built in parallel in another checkout - the two share no files and
the test binds only ephemeral ports (the 307bb part-4 recipe), so concurrent checkouts are
safe (the team-mode rule). The code it verifies is all merged and final (main, synced into
every checkout): 814's settle gate (before every capture the probe waits until the page's
own map.isMoving() is false and no new map frame has been drawn for ~700 ms, under a
20 s budget), 812's in-run double shot (each of the ten views shot twice, <0.5% differing
pixels at threshold 32), 813's pinned-snapshot regime (AW_OWNER_REFRESH=1, the ten
docs/site_flow/307d_*.png in the write-surface proof, an unflagged run never touches the
checkout's snapshot), plus 815's page hunk and 245's saveFit fix. Background: 242's goal
(the measured 28.6-33.6% drift on the four saved/reload views, the mid-transition
signature, the pair flake) and 814's header. Baseline on this tree (DECISIONS 2026-10-15 +
the 813 merge commit d3223f6a): five consecutive green pair runs; all 50 in-run double-shot
pairs 0.0000%; zero [warn] settle; it.245's cross-run compare of two saved runs: 9/10 views
byte-identical, worst B 1-card 0.0447% (the known card band) - expect the same band,
comfortably under 0.5%.

## Goal

Prove across runs, without changing anything, what 814+812+813 promise: two consecutive
unflagged runs of the owner_check pair (one pytest invocation per run; the pair always
runs as one invocation, A then B) with the map settled before every capture, showing
(a) the two runs' ten views match each other run-to-run - the cross-run half of the
stability proof, 812's in-run double shot already covers within a run - (b) the pair stays
green end to end with the pick still derived from the queue and no existing check changed,
and (c) an unflagged run leaves the checkout's pinned snapshot byte-identical (813's
write-surface proof, checked externally). The pick is derived and moves with the queue:
whatever this run derives is what it compares; record the picks in DECISIONS.

## Acceptance criteria

- [x] Two consecutive unflagged pair runs (`.venv/bin/python -m pytest
      tests/test_owner_check.py -q -p no:cacheprovider`, one invocation each) both pass end
      to end; in each run every in-run double-shot pair differs by <0.5% of pixels at
      threshold 32, the probe logs show no `[settle] TIMED OUT` / `[warn]` settle lines
      (the 1-card and 5-reload labels included), the pick is still derived from the queue
      (named in the run's card/log lines - never pinned), and the module is the merged
      version with no local diff (`git diff main -- tests/test_owner_check.py` empty).
- [x] Cross-run: for each of the ten views (A and B x 1-card, 2-placed, 3-gestured,
      4-saved, 5-reload), run 1's primary shot vs run 2's differs by <0.5% of pixels at
      threshold 32 (PIL per-channel max, the module's `_shot_diff` semantics); the per-view
      percentages are recorded in DECISIONS - the card view is the known noise band
      (~0.05%), the four saved/reload views must sit in the stable band, not the old
      28.6-33.6% drift.
- [x] After EACH run, `git status` on `docs/site_flow/` is clean (the ten 307d PNGs
      byte-identical to the committed bytes; the in-test write-surface assert already
      proves it per run - this is the external view). Nothing is restored, renamed or
      committed here: this task changes no file.

## Notes

- Test functions: test_owner_save_bar_scale (A), test_owner_save_site_size_fallback (B);
  each run is one invocation (~70-80 s measured). Do BOTH runs and the compare in ONE
  session - the /tmp lane dies at the session boundary (PITFALLS).
- Temp-tree retention (corrected 246 it.255): a GREEN run rmtree's its whole pytest basetemp in
  `pytest_sessionfinish` - BEFORE the process exits (PITFALLS: the pytest entries) - and the
  numbered-dir cleanup (pytest.ini count=1, mirrored in the driver's
  PYTEST_ADDOPTS) prunes everything but the newest pytest-N. The original recipe's "or run with
  `-o tmp_path_retention_count=2`" alternative is INVALID for a green run (the count is not in
  the rmtree condition; only the policy and an explicit `--basetemp` gate it - source-verified
  it.255). The recipe that worked (it.255): a 0.1 s os.walk watcher process per run, started
  BEFORE pytest, copying that run's ten primary views, its ten double shots and its probe log
  into `$TMPDIR/owner-xrun/run<k>/` (a sibling of pytest-of-agent, so the loop's
  /tmp/loop-*/pytest-of-agent wiper leaves it alone DURING the session) while the run is alive;
  a fresh watcher per run (the pytest-0 numbering restarts after each green wipe), flattened
  relpath keys, re-copy on size/mtime change, stop-file + 3 s grace. The lane dies with the
  session-boundary recreation of /tmp/loop-<checkout>, so the numbers are recorded in DECISIONS
  in the same session that made them. The views live at <pytest-N>/owner{A,B}0/ as 1-card.png
  ... 5-reload.png (the <name>b.png double shots are covered in-run; compare only the primaries
  cross-run); owner_probe.log carries the [settle] lines and the picks.
- If it flakes (never weaken or delete a test; log in DECISIONS and re-file the fix into
  the owning task, pointing at this run's evidence): a `[settle] TIMED OUT` (20 s budget) =
  the settle gate (814's lane - isMoving() false + no new frame for ~700 ms; the maplibre
  5.6.0 idle semantics evidence is in the DECISIONS "2026-10-15 810 DECISION" entry); a
  double-shot assert failure naming a view = a straggler tile/ink between the two shots
  (widen the settle; never weaken the 0.5% line); a cross-run diff in a saved/reload view
  back near the old 28.6-33.6% drift = the settle is not holding on the live page (814's
  lane); a tier-check red = 245's lane (point at its file with the probe's [eval] effects
  block); a red at the old ratio step = 816's lane (point at 814/816).

## Hand-over

(2026-10-15, iteration 255, agent a - **DONE and claimed.** All three acceptance boxes ticked
from this session's direct evidence, recorded in the DECISIONS entry "2026-10-15 246 DECISION":
two consecutive unflagged pair runs (the task's exact command, one invocation each, both in one
session: 80.51 s and 80.77 s, 2 passed each) with the cross-run compare done in the same session
(the /tmp lane dies at the session boundary). Results: 9/10 views byte-identical across runs, the
only diff B 1-card 0.0452% (the known card band; it.245 measured 0.0447% on the same view); the
four saved/reload views byte-identical - the old 28.6-33.6% mid-transition drift (242's
measurement) does not reproduce, so the settled-capture regime holds across runs; all 20 in-run
double-shot pairs 0.0000%; zero `[settle]`/`[warn]` lines in all four probe logs; the picks were
derived from the queue and identical in both runs (A = richard-s-castle-q17650937 /
earthworkenglan01allcgoog_n0453_1, B = devil-s-dyke-q3307343 / earthworkenglan01allcgoog_n0662_1,
named in each run's card and [eval] lines); `git status` on docs/site_flow/ clean after EACH run
(the ten pinned 307d PNGs byte-identical to the committed bytes); the module was the merged bytes
with no local diff at session start and after both runs. No flake, no red, nothing to re-file.

**The one correction this session found (in the task's own Notes, now fixed):** the recipe
"or run with `-o tmp_path_retention_count=2`" cannot work for a green run - the green-run
whole-basetemp rmtree fires in `pytest_sessionfinish` BEFORE the process exits and is gated on
`policy == "failed"` and an explicit `--basetemp` only (source-verified in the .venv's
`_pytest/tmpdir.py`), while retention_count only sets keep= for numbered-dir pruning. A
post-invocation copy (the original "right after each invocation" recipe) therefore also finds
nothing. The recipe that worked: a 0.1 s os.walk watcher per run (the 814/816 recipe widened
from the probe log to the PNGs) copying all 22 files per run (ten primaries, ten double shots,
two probe logs) out to $TMPDIR/owner-xrun/run{k}/ WHILE the run was alive; fresh process per
run, flattened relpath keys, re-copy on size/mtime change. The lane dies with the
session-boundary /tmp/loop-<checkout> recreation, so the DECISIONS entry's numbers are the
record. The PITFALLS pytest section carries the lasting fact (new entry) plus the corrected
"What to do" of the neighbour entry.

**Next (NOT this task's work):** the 810 gate (Depends: 307d, 812, 813, 246, 247) now waits only
on 247 (the full-suite green run - open, claimable in any checkout, shares no files with this
lane, binds only ephemeral ports). When 247 lands with its boxes ticked, 810 ticks its two
gate boxes from the two DECISIONS entries and claims (the 812/245 memory-only-claim pattern);
then 811 (the one-time refresh, the docs note, the PITFALLS rewrite of the per-run re-render
entry) and 242 (the family's final check) unblock in that order. Nothing further to do here.)
