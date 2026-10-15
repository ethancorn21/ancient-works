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
- [x] The 307d section of docs/site_flow.md carries the pinned-snapshot note with the refresh
      command (date + flag); the existing text stays, including that the picks it names are the
      derived picks (oswestry n0119_1 bar / devil-s-dyke n0662_1 picture_size; 38/45 on the
      241-entry queue, 3/8 on the 180-entry queue) and move with the queue.
- [x] The PITFALLS entry's What-to-do is rewritten to the new design (unflagged runs
      byte-identical, the refresh flag, the restore-main-bytes workaround retired), the history
      lines kept, and the stale "task 242's" pointers in the same section corrected to the
      810/811/242 split.
- [ ] The full suite is green (`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider`).

## Hand-over

(2026-10-15, iteration 257, agent a) **Refresh executed; docs + PITFALLS records committed; the unflagged full-suite run is the only remaining step (boxes 1's second half + 4).**

Done this session (one commit):
- **Flagged refresh run (box 1's first half):** `AW_OWNER_REFRESH=1 .venv/bin/python -m pytest tests/test_owner_check.py -q -p no:cacheprovider --basetemp=/tmp/aw811-refresh/basetemp` -> **2 passed in 76.34 s**, zero [warn]/TIMED OUT settle lines in both probe logs (logs at /tmp/aw811-refresh/basetemp/owner{A,B}0/ if the lane survives). Derived picks confirmed from the probe [eval] + runlog: **A = richard-s-castle-q17650937 / earthworkenglan01allcgoog_n0453_1 (bar scale), B = devil-s-dyke-q3307343 / n0662_1 (site-size fallback)** - same as the 246/247/814 it.242 runs. **All ten re-rendered PNGs came back BYTE-IDENTICAL to the committed bytes** (`sha256sum -c` on pre-run hashes: 10/10 OK) - confirms 813's it.256 finding: the committed snapshot is already the settled-era render of exactly these derived picks, so the re-pin is byte-level only (no new PNG bytes to commit). Queue check: 180 entries; oswestry n0119_1 now index 3, devil-s-dyke n0662_1 index 8, richard-s-castle n0453_1 index 9 (the picker derives 9 for A, not 3 - the 2026-10-13 text's picks are history).
- **Box 2 (done, committed):** docs/site_flow.md 307d section gained the pinned-snapshot note after the "Ten views" paragraph: date (2026-10-15), the refresh command (AW_OWNER_REFRESH=1 ...), both derived picks named (richard-s-castle n0453_1 entry 9 / devil-s-dyke n0662_1 entry 8), the 2026-10-13 picks' index shift (38/45 -> 3/8), and the byte-identical re-pin. Existing text untouched.
- **Box 3 (done, committed):** PITFALLS 307d entry: header rewritten to the pinned-snapshot fact (history marked pre-813), Symptom/Why kept as history (28.6-33.6% drift, b14918f, the 302f iter-127 pointer all kept), What-to-do rewritten to the new design (unflagged runs byte-identical per the write-surface hash, the refresh flag, restore-main-bytes RETIRED). The neighbouring B-test entry's stale last sentence now names the 242 split (814 settle, 812 double-shot, 813 regime; 810/811/242 carried the waits). NOTE: the third 307d entry ("branch's COMMITTED PNGs can be stale vs main's") was left as-is (outside this task's scope; its restore-from-main recipe is still valid defensive hygiene, though re-encode dirt can no longer arise from a run).

Next step (boxes 1's second half + 4): run the unflagged full suite ONCE on the committed tree - `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` - expect **195 passed / 1 skipped / 0 failed** (247's baseline on this exact tree, ~600-1000 s; machine contention with the parallel checkouts slows it, 814 measured 865 s). After the run: `git status` must be clean on docs/site_flow/ (byte-identical - the write-surface proof is in-test, this is the external view). If green: tick boxes 1 and 4, set Status: done, commit (memory-only: boxes + this hand-over + DECISIONS), and 242's gate unblocks. If a red: it is foreign unless it is the owner_check pair (a settle flake - 814's lane; retry once before suspecting anything). 242 then re-does final verification on the merged tree (its own boxes), so 811's claim needs the suite green + the records above.

Re-read: none (no product code changed; tests/test_owner_check.py stays byte-identical to main).
