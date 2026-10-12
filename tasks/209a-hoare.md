Status: blocked
# 209a: Hoare, Ancient Wiltshire (1812-21)
Depends on: 200
Touches: fit/src_wiltshire_hoare.py, data/books/triage/, data/books/lists/, data/commons/files_wiltshire_a.jsonl, data/commons/classified_wiltshire_a.jsonl, docs/lead_wiltshire.md, tests/test_src_wiltshire_hoare.py, tests/golden/src_wiltshire_hoare_sample.json

## Goal
Subtask of 209 (the parent's Hand-over has the full mechanics and the source-availability
findings - read it): index Hoare's *Ancient Wiltshire* (the three hundreds: Pewmarsh 1812,
Pewsey 1819, Cherhill 1821) and stage its plates tied to existing sites. The volume that
carries the Stonehenge/Avebury/Silbury/West-Kennet plans is vol. 3 (*The Hundred of Cherhill*,
1821). The book is NOT on IA (verified 2026-10-13) and HathiTrust/Google Books are unreachable
from this VM, so the subtask runs the 207c-Roy local-copy leg: a human-downloaded copy of the
book is placed in data/raw/books/hoare_cherhill1821/ (one page image per file), the module
adapts the fetch to those files, and the rest of the book machinery (triageA/B, list
transcription, staging, tests) runs unchanged.

## Acceptance criteria
- [ ] A complete copy of the Cherhill volume (and, if obtained, vols. 1-2) is in
      data/raw/books/hoare_cherhill1821/ (human-downloaded, per the open ask_human request);
      per-book artifacts only (triage/<id>.*.jsonl, lists/<id>.json, lists/<id>.map.json) are
      written; the shared data/books/index.jsonl and validation.json are NOT written.
- [ ] The book's printed list of plates is transcribed (the books_lists PLATES pattern, from
      the copy's own list pages) and mapped to leaves; the stage-A/B recall against that list
      is recorded in the Hoare section of docs/lead_wiltshire.md (instead of the shared
      validation.json).
- [ ] Staged rows (appended to the shared-per-suffix staging files, rows tagged with this
      book): files_wiltshire_a.jsonl for every verified site-plan plate tied to an existing
      site (by QID; the Cherhill volume's plates tie to stonehenge-q39671, avebury-q661855,
      silbury-hill-q225896, west-kennet-long-barrow-q541312, windmill-hill-q4348373 and other
      catalog Wiltshire earthworks) - each with the 200 evidence field (the book's printed
      list names the place; the specific check - list entry, caption, coordinates distance -
      recorded on the row) and a classified row by hand ("plan"); the book's date (1812-21)
      is recorded on the row. A new extras_wiltshire_a.jsonl entry (add the path to Touches
      first) only for a plate showing a Wiltshire earthwork not in the catalog.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one is accounted for in
      docs/lead_wiltshire.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site)
      and the evidence check passes; a golden sample of rows
      (tests/golden/src_wiltshire_hoare_sample.json).

## Notes
- BLOCKED on the open ask_human request (file it this session, the 207c pattern): the human
  downloads the Cherhill volume (1821) in a real browser from HathiTrust (full-view public
  domain) or Google Books and places one page image per file in
  data/raw/books/hoare_cherhill1821/ (any resolution; the module re-encodes to triage size);
  vols. 1-2 are a bonus, same folder or hoare_pewmarsh1812/ / hoare_pewsey1819/. Fallbacks in
  the request: drop 209a (then this lead stands on 209b/209c), or provide another scan. How
  it is done: the file count matches the book's leaf count and the list pages are legible.
  If the human answers "drop", set Status: dropped and note it in docs/lead_wiltshire.md.
- The existing hand fit on avebury-q661855 (Allcroft fig. 187,
  data/db/platefits/avebury-q661855.earthworkenglan01allcgoog_n0581_1.json) and the one on
  windmill-hill-q4348373 (Allcroft fig. 186) are never re-staged or re-fitted: new rows only.
- LLM triage ports: see the parent's mechanics (live replicas 127.0.0.1:8080-8082, in-process
  books.LLM_URLS patch; long triage runs are resumable nohup background jobs).
