# Bird's-eye views of US cities, batch 5 (task 241): the final five cities of the 25-city total

GOAL.md point 5 (the 2026-10-13 owner change): the map grows with US cities, and artists' aerial
and bird's-eye views count as much as surveys. Batch 5 is the FINAL FIVE cities of the 25-city
total (16 from 236b + 4 from 240 + 5 here) after 236b's sixteen and 240's four (Denver, St. Paul,
Minneapolis, Cleveland), each a new site of its own in this task's own staging files. The source
is the **Library of Congress "Panoramic Maps" collection** (loc.gov/collections/panoramic-maps):
about 1,500 US bird's-eye views, 1847-1929, public domain. One own module
(`fit/src_us_birdseye_batch5.py`), one own staging file set (`*_us_birdseye_batch5.jsonl`) - the
module is a copy of 240's `fit/src_us_birdseye_batch4.py` (itself a copy of 236b's
`fit/src_us_birdseye.py`, the template it keeps in sync with); 236c consolidates every staging
set into the canonical data and checks the 25 total. Candidate order (240's lead-doc "Not done
yet" pointer, continuing the 181 candidate list of the 236b lead doc: "...Kansas City, Omaha,
St. Paul/Minneapolis, Indianapolis, Columbus, Memphis, New Orleans, ..."): **Omaha (skipped in
236b with no recorded drop reason - re-run its pool search and record the verdict),
Indianapolis, Columbus, Memphis**, then whatever the collection's search order adds to reach
five. The task owes FIVE staged cities, not specifically these - a city with no usable view gets
a note here and the next candidate.

## Fetch route (same as 236b's, re-verified for the batch-5 cities)

The route is the 236b one (full detail in docs/lead_us_birdseye.md, section "Fetch route"):
loc.gov is unreachable from this machine (403, CloudFront bot block), so the files are fetched
from their **Wikimedia Commons mirrors only**; the candidate pool per city is the Commons
file-namespace full-text search in the six plain-phrase forms ("bird's-eye view of <city>", "bird's
eye view of <city>", "birdseye view of <city>", "<city> bird's eye", "<city> birdseye", "Birds' eye
view of <city>", each + ` filetype:bitmap`, srnamespace 6, srlimit 40), deduped, then the gates:
`commons.keep()` (judged AFTER any known-date swap) AND the caption names the city (books_match.norm
over title + description) AND the license is **Public domain** AND the width is **>= 4000 px**.
Re-verified live for each batch-5 city at its landing (the per-city pool counts and verdicts land
in the city sections below).

## QID verification (`.venv/bin/python fit/src_us_birdseye_batch5.py --verify`)

The batch-5 QIDs are verified when their cities are added (label, every P625 value - flagged when
>50 km from the table point, P373, P131 with labels, the enwiki article, and the first name-search
hit with coordinates - what `record --live` would resolve for the caption route). The verbatim
transcript lands here with each landing (the 240 pattern: re-run with every landing and appended).

## The evidence field (as in 236a/236b/240)

As in the 236b and 240 docs: every staged row carries a hand-recorded `caption_coords` tie in the
exact key order of `fit/evidence.py:caption_route` - the caption names the city and the stored
coordinates are the verified site point itself (dist 0); `record --live` would take the first
name-search hit instead, which is why every QID is verified above and the stage fails loud when a
caption does not print the city. A scan whose file page lost the drawing's date gets the known
drawing/publication date on the row and the page value kept as `date_commons` (the Zwolle
precedent; the keep() gate is judged after the swap).

## Staging and checks (2026-10-14)

Nothing is staged yet at module creation (the per-city sections and the verbatim `--check`
transcript land here with each landing, the 240 pattern; the counts end at FIVE views / FIVE
site rows when all five land). All batch-5 cities, when they land, stage in this task's own
files only: `data/catalog/extras_us_birdseye_batch5.jsonl` (the site rows - region "United
States", kind "town", aerial_ok true, the point = the city's verified P625 or a recorded
refinement, the note recording the staged view's apparent angle so 236c / the matcher can
order the oblique views), `data/commons/files_us_birdseye_batch5.jsonl` (files.jsonl shape +
the 200 evidence field) and `data/commons/classified_us_birdseye_batch5.jsonl` (p_birdseye 1.0,
by "hand"). The golden sample `tests/golden/src_us_birdseye_batch5_sample.json` pins the staged
rows (regenerated only via the module's `--golden` for an intended change).

**Not done yet - this task's five (batch 5, the final five of the 25 total):** in the candidate
order above: **Omaha (skipped in 236b with no recorded drop reason - re-run its pool search and
record the verdict), Indianapolis, Columbus, Memphis**, then whatever the collection's search
order adds to reach five (the 181 candidate list continues past Memphis; the collection has
~1,500 views, so any US city not already staged - the skip list: 236a's four, 236b's sixteen,
240's four, the catalog, web/data/sites.json - is fair game as the search continues). **236c**
consolidates every staging set into the canonical data and checks the 25 total (16 + 4 + 5, or a
recorded shortfall for a city whose pool yields no usable view). **Do NOT write the canonical
files - that is 236c; do NOT re-stage the sixteen cities in 236b or the four in 240's doc.**
