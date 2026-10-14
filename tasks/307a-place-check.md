Status: done
# 307a: re-split per the lead (2026-10-12) - the place check is carved to 309 (agent c); the page work moves up to 307a
Depends on: none
Touches: tasks/309-place-check.md, tasks/307-fit-tool-rework.md, tasks/307b-on-map.md, tasks/307c-working-space.md, tasks/307d-owner-check.md (a re-split record; the work lives in 307b/307c/307d and the lead's 309)

## What happened (iteration 108)
Iteration 108 (agent a) spent the whole session investigating the original 307a (the namesake
place check in tools/fit_queue.py: data/fit_place.json verdicts, moves to review, the report):
all inputs mapped, the rule set drafted, and the noisy-evidence-conflict question (52 queue
commons rows) being analysed when the lead re-tasked mid-session:

- Lead message 1: "307 box 1 (right place, the namesake check in tools/fit_queue.py) is carved
  to 307b for agent c. Leave tools/fit_queue.py to c; do the page work (zoom, hide overlays,
  drawing on the map, working space, save path). Untick nothing, just mark box 1 as carved."
- Lead correction (same iteration): "the carved task is 309 (not 307b)."

So: box 1 is carved out of 307 into the NEW top-level task 309 (agent c owns it; it carries the
full old-307a spec and this session's research). Agent a now does the 307 page work, renumbered:

- **307b (was 307a's letter, now the on-map placement)**: parent boxes 2-4 - place mode opens
  ON the works (fly to the site's box, centred, zoomed so the works fill the view), hides every
  overlay while open and restores on close, and the drawing starts ON the map (the proposal's
  pairs, drag/scale/rotate, opacity, save from direct placement alone).
- **307c (was 307b's content)**: parent box 5 - working space (map the main surface, the page
  picture a small collapsible reference, the side panel only what placing needs; before/after
  screenshots in docs/site_flow/).
- **307d (was 307c's content)**: parent box 6 - the save path stays `by: hand` + the one-site
  line (305), existing hand fits unchanged, checked in a real browser on two queue sites (the
  queue place-check test in that box now belongs to 309).
- **307d-old (owner check)**: dropped - merged into the new 307d above.

The parent's box 1 carries the marker "(carved to 309 - agent c)". Nothing was unticked.

## What happened (iteration 109)
The record was complete but had left one defect: two files claim the number 309 - the
lead's tasks/309-queue-right-place.md (commits 82e37e1 / 720539f at 21:34, created while
my iteration-108 session was still running and could not see it) and my
tasks/309-place-check.md (driver commit 0d9d5d8 at 21:39). The d651c10 main-sync brought
the lead's file in beside mine. The driver's queue names the lead's file as 309 (its
title and touches are what the iteration-109 prompt cites for agent c), so the lead's
file is canonical and mine is dropped (kept as reference - see its dropped note).
The record is now done: the re-split is recorded and unambiguous; 307b/307c/307d and
the lead's 309 carry all the work. Also fixed: stale "307a" pointers in my 307c/307d
subtasks (now 309), the page-work entry points (moved from this record into 307b's
Notes), and the DECISIONS entry this file's old hand-over pointed at (never written in
iteration 108 - written now, marked late).

## Hand-over

(2026-10-12, iteration 109, agent a - record CLOSED. This file is a re-split record,
not a work task; it is done and nothing remains in it. The next agent of this project:
read the parent's Hand-over, then 307b - the first live subtask.)

State: done. The re-split is recorded and unambiguous: 307b/307c/307d (the page work,
agent a, in that order) and the lead's 309-queue-right-place.md (the place check, agent
c) hold all of 307's remaining work. The one defect iteration 109 found - two files
claiming the number 309 - is resolved: my 309-place-check.md is Status: dropped and
kept in place as reference for the 309 implementer (its note says what it carries); the
lead's file is untouched and canonical (the driver's queue names it by title and
touches; agent c works from it). No code of 307 was changed by this session; the suite
at closure: 73 passed, 1 skipped (green, same as the iteration-107/108 baseline - the
d651c10 main-sync had added task files only, no code).

Re-read: none. The next live task is 307b (tasks/307b-on-map.md): its Notes carry the
entry points (the fit/place flow chain, the 'fit-prev' source, keep-the-extension-
small) and its boxes 2-4 the fly-to / hide-restore / drawing-on-map work. The lead's
309 and agent c's in-flight work are not mine to touch (team mode). If this file is
reopened, the done claim was rejected - the reasons will be in DECISIONS.
