Status: in-progress
# 212b: The page-facing sync - every fit is an overlay, review.json is the open list
Depends on: 212a
Touches: fit/cover.py, web/data/sites.json, web/data/sites/, web/data/review.json, data/db/platefits (the sync stamps by:agent into an unmarked auto doc and deletes a pattern doc), data/review/ (the sync's per-doc failure containment upserts item entries; the trailing export records write-once resolutions), tests/test_cover.py, tests/test_fit_provenance.py (212b's sync deleted the yearless-title test's pinned durocortorum doc; the pin moves to the surviving watson-brake doc)

## Goal
The one page-facing sync from 212: every fit document becomes its site's overlay
(web/data/sites/<id>/depictions.json) and drawings count in web/data/sites.json through
the existing plan_fit machinery (plan_fit.main(), the way serve.py's after_write does);
web/data/review.json is regenerated (python3 fit/review.py export).

## Acceptance criteria
- [x] `python3 fit/cover.py sync` runs plan_fit for every site with a fit doc and the review export.
- [x] The hand fits' overlays are unchanged (000's golden test still passes).
- [ ] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item; the page's review count
      matches review.json (checked through the served page).

## Hand-over

(2026-10-13, iteration 228, agent a - STEP 4 (the post-sync suite) ran and is classified; the red my
sync caused is FIXED, the other red is a proven pre-existing 307-series one, and the hand-over's
expected 203b reds are GONE (green). Boxes 1+2 committed via the driver's 6ce742f. **NEXT: box 3 -
write tests/test_cover.py per the parent design, RE-MEASURING CHOOSE first (the live sync changed
the world: 57 docs / 365 open / 377 items).**

**Suite (this session, .venv, 324.45 s, log /tmp/aw212b-suite.out): 2 failed, 153 passed,
1 skipped (156 total = agent c's 9f92b3a "154/1/1" total).**

**Red 1 (MINE - fixed this session):** test_fit_provenance.py::test_commons_yearless_title_
keeps_the_label pinned the yearless-no-label case on durocortorum c_08d995eb23a685c2, one of the
76 docs my live sync sent/deleted -> FileNotFoundError. Re-pinned to watson-brake-q2552689.
c_5e7bb19c79b509ed (surviving matcher doc: yearless title + label None -> the line renders
"(undated)" per plan_fit L290-291; built line measured with the test's own _build_source:
"Watson Brake - Map (undated), Wikimedia Commons: by Maximilian Dörrbecker ( Chumwa );
CC BY-SA 2.5; https://commons.wikimedia.org/wiki/File:Watson_Brake_-_Map.png. Fitted automatically
by the batch on 8 matching points; one rotation and scale fits them within 1 m (gate score 4.4
m)"). Docstring now records both pin moves (306a bethlehem, 212b durocortorum). File now 7/7.
tests/test_fit_provenance.py is on this task's Touches line for exactly this reason. The sister
pin (yeared, argentoratum c_ec1930f8) and the bergues hand pin still exist and pass; no other test
referenced a deleted doc (the full run proves it).

**Red 2 (PRE-EXISTING - not fixed here):** test_fit_queue.py::test_placement_gestures_and_save_in_
the_browser = 307bb's part-4 headless test (lead's 081c773, green on the lead's Mac). Fails at the
first seed check "seed: the gestures own the mouse (map pan/zoom off), the earlier overlay hidden"
(probe: seed.gestures.every(v => v === false) && seed.dep === 'none'); the /tiles/relief 404s in
the log are by design (the temp tree skips .npy/.npz grids; the probe's reqfail check excludes
'/tiles/'). Three independent pre-existence proofs (full text in the DECISIONS entry): (a) agent
c's branch recorded exactly this red in fdfeddf (05:24) and 9f92b3a (06:19), both before my live
run (06:01) and my artifact commit (06:31), on a branch that could not contain my work; (b) my sync
changed none of the test's inputs - pick entries[3] oswestry-castle-q20713795: its item file
byte-identical pre/post (0fbea54 vs HEAD), no platefits doc in either state, fit_queue.json
unchanged, no oswestry overlay written by the sync; (c) it is a headless-Chrome page-state check
on this VM. Ownership: the 307 series - 307d (open, "the owner's check - two queue sites end to
end", Touches tests/) is the natural fix home; no new task filed. If my done claim is re-checked
while it is still red, the DECISIONS entry carries the attribution (driver note mechanism).

**203b's two reds (the iter-227 expectation) did NOT materialize:** test_batch_eu.py passes fully
- the lead's 0685a4c moved the no-picture fixture bibracte -> Yeavering Bell (212a found 18
pictures of bibracte) and agent c's in-flight 203b work tracks the rest. `Depends on` stays
"212a" (done, in-branch); 203b was never added.

**State of the tree:** driver's 6ce742f committed the sync artifacts (29 A item files, 71 D
platefits = 76 sends minus 5 already in 4e1dabf, 23 M = 21 items + review.json + sites.json);
platefits = 57 (21 by:hand + 36 by:agent), data/review = 377 items + README, review.json 365
open / at 2026-10-13T11:26:15Z. Working tree before this session: clean. This session's delta:
tests/test_fit_provenance.py (the re-pin), this file (Touches + hand-over), DECISIONS.md.

**BOX 3 (next sessions) - tests/test_cover.py**, per the PARENT design (full text: `git show
953d9ab:tasks/212-cover-final.md` - D1-D5 + CHOOSE recipe + the 7 numbered assertion groups - and
the parent's current ## Hand-over). Recap: extend the existing 212a fixture with include_sites=True
(real hard-linked site dirs; the measured D3 build is ~0.7 s); PHASES + "loop" + "sync" (report is
212c's); matcher fakes monkeypatched on the shared module objects (site_done.matchfit.reachable ->
False or matchfit.run -> a fake writing the CHOOSE docs; matchfit.spread stays real - pure); big
stand-ins for the CHOOSE commons docs; port-0 served page (Popen [.venv python, server/serve.py,
--port 0] cwd=tree, parse "Ancient Works on (\S+)"); socket guard on; tmp_path_retention_policy
"failed" (the 48 GB box). Checked through the served page: (v) EVERY built site in the served
sites.json has drawings>=1 OR is in the served open list, and the page's review count matches
review.json. **RE-MEASURE CHOOSE before writing: the live run deleted 76 docs and re-derived
review.json at 365, so the parent's CHOOSE ids (aardenburg/aesica/aire-sur-la-lys/alauna) and
their item rows may have moved.** World now (post-sync, measured this session): 57 docs =
21 by:hand + 36 by:agent; review.json 365 open; 377 item files. Re-derive the populations with the
PRODUCT definitions (nofit = drawings==0 AND no doc; search set = nofit minus plans-row sites;
with-row nofit = nofit with a plans row, split all-rows-in-item / partial / no-item; CHOOSE =
first 4 with-row nofit, sorted) against THIS tree before pinning anything. The test's loop phase
makes the box-6 invariant true in the tree; sync in the test uses stand-ins (no downloads). The
76 deleted docs are gone from this tree's platefits - the test's world must not depend on their
presence (CHOOSE picks nofit sites; the matcher fakes write fresh docs).

---
(superseded - iteration 227 note, full text in git: `git show 2216b8a:tasks/212b-cover-sync.md`.
Its iter-226 block is superseded by it; the 05:58-era preflight numbers there are stale where
they conflict with the above.)
