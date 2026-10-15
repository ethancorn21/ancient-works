Status: open
Depends on: none
Touches: (none - verification only; runs tests/test_owner_check.py as merged and changes no file)

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

- [ ] Two consecutive unflagged pair runs (`.venv/bin/python -m pytest
      tests/test_owner_check.py -q -p no:cacheprovider`, one invocation each) both pass end
      to end; in each run every in-run double-shot pair differs by <0.5% of pixels at
      threshold 32, the probe logs show no `[settle] TIMED OUT` / `[warn]` settle lines
      (the 1-card and 5-reload labels included), the pick is still derived from the queue
      (named in the run's card/log lines - never pinned), and the module is the merged
      version with no local diff (`git diff main -- tests/test_owner_check.py` empty).
- [ ] Cross-run: for each of the ten views (A and B x 1-card, 2-placed, 3-gestured,
      4-saved, 5-reload), run 1's primary shot vs run 2's differs by <0.5% of pixels at
      threshold 32 (PIL per-channel max, the module's `_shot_diff` semantics); the per-view
      percentages are recorded in DECISIONS - the card view is the known noise band
      (~0.05%), the four saved/reload views must sit in the stable band, not the old
      28.6-33.6% drift.
- [ ] After EACH run, `git status` on `docs/site_flow/` is clean (the ten 307d PNGs
      byte-identical to the committed bytes; the in-test write-surface assert already
      proves it per run - this is the external view). Nothing is restored, renamed or
      committed here: this task changes no file.

## Notes

- Test functions: test_owner_save_bar_scale (A), test_owner_save_site_size_fallback (B);
  each run is one invocation (~70-80 s measured). Do BOTH runs and the compare in ONE
  session - the /tmp lane dies at the session boundary (PITFALLS).
- Temp-tree retention: a GREEN session rmtree's its whole pytest basetemp at session end,
  and the numbered-dir cleanup (pytest.ini count=1, mirrored in the driver's
  PYTEST_ADDOPTS) prunes everything but the newest pytest-N even with policy=all (both
  entries in PITFALLS). Recipe: right after each invocation, copy that run's ten primary
  views and its probe log out to a persistent lane inside the checkout's TMPDIR (e.g.
  $TMPDIR/owner-xrun/run<k>/ - a sibling of pytest-of-agent survives the loop's
  /tmp/loop-*/pytest-of-agent wiper), or run with `-o tmp_path_retention_count=2`. The
  views live at <pytest-N>/owner{A,B}0/ as 1-card.png ... 5-reload.png (the <name>b.png
  double shots are covered in-run; compare only the primaries cross-run); owner_probe.log
  carries the [settle] lines and the picks.
- If it flakes (never weaken or delete a test; log in DECISIONS and re-file the fix into
  the owning task, pointing at this run's evidence): a `[settle] TIMED OUT` (20 s budget) =
  the settle gate (814's lane - isMoving() false + no new frame for ~700 ms; the maplibre
  5.6.0 idle semantics evidence is in the DECISIONS "2026-10-15 810 DECISION" entry); a
  double-shot assert failure naming a view = a straggler tile/ink between the two shots
  (widen the settle; never weaken the 0.5% line); a cross-run diff in a saved/reload view
  back near the old 28.6-33.6% drift = the settle is not holding on the live page (814's
  lane); a tier-check red = 245's lane (point at its file with the probe's [eval] effects
  block); a red at the old ratio step = 816's lane (point at 814/816).
