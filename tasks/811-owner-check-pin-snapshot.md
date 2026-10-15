Status: open
Depends on: 810
Touches: docs/site_flow/307d_*.png, docs/site_flow.md, PITFALLS.md

# 811: The 307d owner check - pin the ten 307d PNGs under 810's regime: the one-time refresh, the docs pinned-snapshot note, the PITFALLS rewrite

Part 2 of 242's split (2026-10-15): the one-time refresh of the pinned snapshot and the record of
it - no test-code change (242 waits on this and on 810; this waits on 810, which waits on
812 + 813: the refresh flag it runs is 813's, and the snapshot it burns must be what the
verified 810 regime produces). Background: 242's goal and the 2026-10-14 307bc DECISIONS
entry (now in the
archive): the ten PNGs in docs/site_flow/ no longer correspond to the 307d-acceptance bytes they
replaced - every suite run re-rendered them (often mid-transition), so the committed bytes are just
the last run's, not a stable snapshot.

## Goal

1. **Regenerate once, under the new regime.** With 810 merged, run the explicit refresh (the env
   var / pytest flag named in tests/test_owner_check.py's docstring) once on the current tree and
   commit the regenerated ten `docs/site_flow/307d_*.png` - they become the pinned snapshot the
   docs cite. The picks are derived and move with the queue: if they shifted since the 2026-10-13
   run (the 2026-10-15 owner_check reds picked A = richard-s-castle n0453_1, not oswestry), the
   pinned set is what this run captures, and the note names those picks.
2. **Docs.** The 307d section of docs/site_flow.md ("The owner's check: two queue sites end to
   end, then reverted (task 307d, 2026-10-13)") gains one short note: the screenshots are a pinned
   snapshot (date + how to refresh, i.e. 810's flag). The existing text (dated "on the 241-entry
   queue of 2026-10-13") stays - the picks it names are still the derived picks (oswestry n0119_1
   bar / devil-s-dyke n0662_1 picture_size), only the queue indices shifted with re-exports
   (38/45 -> 3/8 on the 180-entry queue) - and the picks move with the queue, so a snapshot's
   picks are whatever that run derived.
3. **PITFALLS.** Rewrite the What-to-do of the entry "test_owner_check re-renders all ten 307d
   golden PNGs into docs/site_flow/ on EVERY run..." to describe the new design and point at the
   refresh flag (an unflagged run leaves the ten byte-identical, proven by the test's write-surface
   hash; the restore-main-bytes workaround is retired; the b14918f merge-conflict history stands).
   Keep the Symptom/Why history lines (the 28.6-33.6% drift measurement, the pointer to agent c's
   302f iter-127 entry). Also correct the stale pointers in the neighbouring B-test entry: "The
   stability fix (settle before shooting) is task 242's; 230's done-claim is gated on it (Depends
   on: 242)" -> name the 242 split (814 does the settle, 812 the double-shot assert, 813 the
   regime; 810/811/242 carry the waits).

## Acceptance criteria

- [ ] The ten PNGs are regenerated once under the new regime (810's explicit refresh) and
      committed; an unflagged full-suite run on the committed tree leaves `git status` on
      `docs/site_flow/` clean (byte-identical) - the pinned snapshot is what an ordinary run
      produces.
- [ ] The 307d section of docs/site_flow.md carries the pinned-snapshot note with the refresh
      command (date + flag); the existing text stays, including that the picks it names are the
      derived picks (oswestry n0119_1 bar / devil-s-dyke n0662_1 picture_size; 38/45 on the
      241-entry queue, 3/8 on the 180-entry queue) and move with the queue.
- [ ] The PITFALLS entry's What-to-do is rewritten to the new design (unflagged runs
      byte-identical, the refresh flag, the restore-main-bytes workaround retired), the history
      lines kept, and the stale "task 242's" pointers in the same section corrected to the
      810/811/242 split.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).
