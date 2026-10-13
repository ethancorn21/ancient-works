Status: split
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
- [ ] 236a, 236b and 236c are done.

## Notes
- The owner's standing rules: historical depictions only (no modern maps, no modern redraws presented as old);
  plain survey sheets (Coast Survey charts, USGS topo quads) are background, not drawings - a city plan or a
  fortification plan is a drawing.
- The four cities the owner named come first: New York, Washington DC, San Francisco, Nashville.
