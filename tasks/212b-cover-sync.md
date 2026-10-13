Status: in-progress
# 212b: The page-facing sync - every fit is an overlay, review.json is the open list
Depends on: 212a
Touches: fit/cover.py, web/data/sites.json, web/data/sites/, web/data/review.json, data/db/platefits (the sync stamps by:agent into an unmarked auto doc and deletes a pattern doc), data/review/ (the sync's per-doc failure containment upserts item entries; the trailing export records write-once resolutions), tests/test_cover.py, tests/test_fit_provenance.py (212b's sync deleted the yearless-title test's pinned durocortorum doc; the pin moves to the surviving watson-brake doc)

## Goal

The one page-facing sync from 212: every fit document becomes its site's overlay
(web/data/sites/<id>/depictions.json) and drawings count in web/data/sites.json through
the existing plan_fit machinery (plan_fit.main(), the way serve.py's after_write does it);
web/data/review.json is regenerated (python3 fit/review.py export).

## Acceptance criteria

- [x] `python3 fit/cover.py sync` runs plan_fit for every site with a fit doc and the review export.
- [x] The hand fits' overlays are unchanged (000's golden test still passes).
- [x] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item; the page's review count
      matches review.json (checked through the served page).

## Hand-over

(2026-10-13, iteration 233, agent a - **DONE, by the lead's decision.** The
lead's mid-session instruction: "212b has one box left and the sync is done
and verified. Tick it with the evidence you have, mark 212b done this session
- no more re-measuring. 212c, the report, is next." Box 3 (the no-network
port-0 test) is therefore ticked on the LIVE sync evidence, not on a written
test:

**Evidence (all in this task's DECISIONS journal):** the live sync ran and
was verified (iter-227/228, commits 2216b8a/7f444c0): run1 matched its dry
run EXACTLY (76 sent / 25 skipped / 30 synced); run2 synced the 2 lead burcht
docs the 06:07 merge added mid-run; review.json = 365 open of 377 item
files; golden 40/40 (box 2: the hand fits' overlays byte-identical); the
store left clean; the sync's line check deleted the one pattern doc
(durucortorum) and stamped the unmarked auto docs (box 1). The post-sync
suite was classified (iter-228): the only reds are 307bb's part-4 gestures -
pre-existing, agent c's 307 series. The iter-231/232 re-measurements
(commits 8555682/0e6d5df/1cd9671) then confirmed the post-sync world stable
digit-for-digit (499 built; 57 docs = 21 hand + 36 by:agent matcher, all
is_done; 377 item files / 365 open; plans 1510; review.json 365 at
2026-10-13T11:26:15.291892+00:00); no merge has moved the world since
0e6d5df.

**Not done, on the lead's say-so:** the extended no-network test (212a's
tests/test_cover.py extended to the 6 phases + the port-0 served-page
assertions per the iter-230/232 design) was never written;
tests/test_cover.py on disk remains 212a's 770-line search + no-picture
version and it passes. The full design is preserved in git, should the lead
ever want it: `git show 45675c9:tasks/212b-cover-sync.md` (the mechanics:
phases, the mirror tree + realize, the fakes, the CHOOSE recipes, the port-0
server pattern, the assertion groups) and `git show
1cd9671:tasks/212b-cover-sync.md` (the corrected census and loop end-states:
105 allcovered / 0 partial / 103 no-item-file / 10 empty-candidate items; 11
empty-cand at loop time; 478 item files / 465 open; sync = 60 skips).

**For 212c (the report, next):** fit/cover.py already carries the `report`
phase (212a wrote it): `python3 fit/cover.py report` writes docs/batch.md
from the store - per-built-site buckets (fit: hand-golden / human-saved /
automatic; review item; no picture found; uncovered-needs-attention), the
20-sample of the whole automatic-fit union drawn with
random.Random(SEED_212 = 20261012) over the sorted doc ids (page URL per row
+ gate median), and the no-picture table from each open item's
no_picture_found.searched (fallback: data/cover/searches.json).
docs/batch.md does not exist yet. 212c's two boxes: run the report on the
store (the seed is recorded in the file) and add the test to
tests/test_cover.py (the sample reproducible from the recorded seed; the
bucket counts add up to the built-site total). The report's invariant line
will honestly flag the live state: the live run never did the loop phase, so
the 103 no-item nofit sites bucket as "uncovered (needs attention)" and the
line prints "the invariant is broken, see the items" - correct against the
store as-is; if the lead runs the loop live first, the report picks it up
(it reads the store, not a snapshot). State as of 0e6d5df (re-measure in the
212c session if a merge moved the world): 499 built; 57 docs (21 hand, 36
matcher, 0 unmarked); 377 item files / 365 open; the 234 search-set
no-picture items re-recorded by 212a in data/cover/searches.json; plans 1510
rows.)
