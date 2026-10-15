Status: done
# 236: US cities - old plans and bird's-eye views of New York, Washington, San Francisco, Nashville and more
Depends on: none
Touches: tasks/236a-us-city-plans.md, tasks/236b-us-birdseye.md, tasks/236c-us-cities-merge.md

## Goal
The owner (2026-10-13): "lets also add US cities like nashville or dc or SF or New York. Those had to have
had some survey stuff as well." GOAL.md point 5 (the map grows): US cities come with old town plans, city
surveys and artists' bird's-eye views, and those count as drawings (town plans and views are exempt from the
150-year rule). Split by source so two agents work in parallel without touching the same files:
- 236a: named city plans (manuscript and engraved plans, 1660-1880) - its own staging files.
- 236b: bird's-eye / panoramic views (1847-1929) of the same and other US cities - its own staging files.
- 236c: consolidate both into the canonical data with fit/merge.py (the 211 machinery), build the new sites.

## Acceptance criteria
- [x] 236a, 236b and 236c are done.

## Notes
- The owner's standing rules: historical depictions only (no modern maps, no modern redraws presented as old);
  plain survey sheets (Coast Survey charts, USGS topo quads) are background, not drawings - a city plan or a
  fortification plan is a drawing.
- The four cities the owner named come first: New York, Washington DC, San Francisco, Nashville.

## Proposed changes
(2026-10-14, iteration 195, agent a - the 236b split, driver instruction.) 236b closed done at 16 cities;
its remaining nine (to the 25-city total) were split out of it into top-level tasks 240 (batch 4: Denver,
St. Paul, Minneapolis, Cleveland) and 241 (batch 5: the final five, after 240), each with its own module
(fit/src_us_birdseye_batch4/5.py), staging files (*_us_birdseye_batch4/5.jsonl), lead doc
(docs/lead_us_birdseye_batch4/5.md) and test, so the two agents build in parallel. They gate 236c through
its Depends on. Suggest box 1 read "236a, 236b, 240, 241 and 236c are done." The 25-city total check moved
to 236c (its Proposed changes, same date).

## Hand-over

(2026-10-15, iteration 211, agent c). **Claimed `Status: done` this session.** All five delivering subtasks
are done and driver-accepted on main; the sole acceptance box is ticked - and its stronger form (agent a's
it.195 suggested wording, "236a, 236b, 240, 241 and 236c are done") is true too. No build work remains.

**Verification done this session (evidence for the tick):**
- Task files ON MAIN (not just this branch): 236a, 236b, 236c, 240, 241 all `Status: done`; zero unchecked
  boxes in each (`grep -c '^- \[ \]'` = 0 on all five).
- Built data, checked by running code: `web/data/sites.json` is a dict `{"sites": [...]}` (a list assumption
  crashed on the shape in the first pass) with 533 sites; ALL 25 US ids present in it and as on-disk dirs
  (`web/data/sites/<id>/`, 25/25 here); all four owner-named cities in (new-york-q60, washington-q61,
  san-francisco-q62, nashville-q23197); ZERO duplicate QIDs across the 472 qid-bearing sites (236c box 1's
  no-two-sites-per-QID intent holds after consolidation).
- Newest full-suite evidence on THIS exact tree (my branch == main + driver bookkeeping only; main HEAD =
  2004ac87): 236c's it.210 run 2 = 195P/1S/0F (RC=0, 1008.95 s) = main's 194P/1S/0F baseline + 236c's one new
  test; main has had no code/data changes since (agent a's 242/810-816 work is still in flight on their
  branch, not on main). No suite re-run this session: the driver re-runs the suite for my claim gate anyway.

**If the driver reopens this (e.g. a rejected done claim):** nothing to build. If the rejection is a 900 s
budget timeout: the suite ran 668 s (it.210 run 1) and 1009 s (run 2, under agent-a load) both all-green on
this machine - re-run `.venv/bin/python -m pytest -q` in a quiet window and re-claim. If a specific test is
red: check whether it belongs to agent a's 242 family (the in-flight 812/813/814 owner_check 307d settle
work) or is a known-stale red, and record it per AGENTS.md - do not absorb another task's red into this claim.

**Team-mode hygiene (still applies to this checkout):** this task's Touches = the 236-family task files only.
The ten `docs/site_flow/307d_*.png` are agent a's lane (242/810-816): after ANY test run restore all ten to
main's bytes (`for p in docs/site_flow/307d_*.png; do git show main:"$p" > "$p"; done`) and NEVER commit them.
This session restored all ten; three still show `M` vs HEAD because the driver's ce75eda3 uncommitted-work
commit baked in stale re-encoded bytes (a sync commit aligns HEAD); the working tree now equals main's bytes
for all ten.
