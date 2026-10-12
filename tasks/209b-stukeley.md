Status: open
# 209b: Stukeley (1740s) - the Temple Restor'd scan on IA + his Commons plates
Depends on: 200
Touches: fit/src_wiltshire_stukeley.py, data/books/triage/, data/books/lists/, data/commons/files_wiltshire_b.jsonl, data/commons/classified_wiltshire_b.jsonl, docs/lead_wiltshire.md, tests/test_src_wiltshire_stukeley.py, tests/golden/src_wiltshire_stukeley_sample.json

## Goal
Subtask of 209 (the parent's Hand-over has the full mechanics - read it): get Stukeley's
drawings of the Wiltshire sites onto the map. Two legs, both from sources reachable from this
VM: (1) the complete British Museum scan of *Stonehenge, a Temple Restor'd to the British
Druids* (1740), ia=`bim_eighteenth-century_stonehenge-a-temple-rest_stukeley-william_1740`
(BookReader pages + hOCR verified 2026-10-13), indexed with the standard book machinery -
its plates (Stukeley's numbered Stonehenge plan, the Avenue plan, the Wiltshire map) tie to
stonehenge-q39671; (2) the Commons-hosted Stukeley plates (the 205-Kip pattern, no book
machinery) - first the 1740 Avebury plan `File:Houghton Arc 855.214 - Stukely, the Druid
temple of Abury.jpg` (2269x1362, visually verify first - it has no description metadata),
then every other fit-sized (>= 1000 px) Stukeley plate in `Category:William Stukeley` that
shows a catalog site. If the human also delivers *A survey of Wilts* (1740, the true
Wiltshire volume - see the open ask_human in 209a/209c), it is added here as a second
local-copy book.

## Acceptance criteria
- [ ] The BMB 1740 scan is fetched from IA (data/raw/books/bim_eighteenth-century_stonehenge-
      a-temple-rest_stukeley-william_1740/) and triaged with the existing machinery, per-book
      artifacts only (triage/<ia>.*.jsonl, lists/<ia>.json, lists/<ia>.map.json); the shared
      data/books/index.jsonl and validation.json are NOT written.
- [ ] The book's printed plate list is transcribed (the books_lists PLATES pattern, from the
      hOCR; the book is short - check the leaf count from scandata first) and mapped to
      leaves; the stage-A/B recall against that list is recorded in the Stukeley section of
      docs/lead_wiltshire.md (instead of the shared validation.json).
- [ ] Staged rows (appended to the shared-per-suffix staging files, rows tagged with this
      book): files_wiltshire_b.jsonl for every verified site-plan plate - the IA book's
      Stonehenge/Avenue plans (site stonehenge-q39671) and the Commons plates (the 1740
      Avebury plan -> avebury-q661855; the 1722 Stonehenge drawing and any other fit-sized
      verified Stukeley plate -> its site) - each with the 200 evidence field (the book's
      printed list entry for the IA rows; for the Commons rows the hand verification or the
      caption names the place - the specific check recorded on the row) and a classified row
      by hand ("plan"); the work's date (1740/1722) is recorded on the row.
- [ ] The existing hand fits are NOT re-staged or re-fitted (the Allcroft fig. 187 Avebury
      fit in data/db/platefits/avebury-q661855.earthworkenglan01allcgoog_n0581_1.json, the
      Allcroft Windmill Hill fit): new rows only.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages/plates are staged, or each missing one is accounted for in
      docs/lead_wiltshire.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site)
      and the evidence check passes; a golden sample of rows
      (tests/golden/src_wiltshire_stukeley_sample.json).

## Notes
- First session: re-baseline the test suite, then VISUALLY verify the Commons candidates by
  downloading them (Commons API `url` field) and looking at them: the Houghton Avebury plan
  (expect Stukeley's 1740 plan of the circle with numbered stones and the Longstones),
  `File:Stonehenge Dessin Stukeley 1722 03547.jpg` (4620x2430, expect the 1722 Itinerarium
  drawing), `File:Stonehenge Stukley Oxford 03543.jpg` (3606x2976, source unverified -
  identify it), and the two unlabeled Flickr files
  `File:47 of 'Stonehenge- plans, descriptions and theories' (11135894643).jpg`
  (2245x2852) / `File:49 of '...' (11133409654).jpg` (4641x2874) - if either is the Petrie
  1880 plan, that finding unblocks 209c (tell the 209c agent / the driver) and the file is
  NOT staged here. Everything else in Category:William Stukeley is <1000 px (too small) or
  not a site drawing (the Clarendon palace ruins 1723 is Roman/medieval - check whether it is
  a catalog site before any staging).
- The Commons leg needs no LLM; only the IA book leg uses the triage stages (ports per the
  parent's mechanics; the book is short, so no long background job expected).
- LLM calls never run in tests (the no_network socket-blocking fixture as in
  tests/test_src_kip.py).
