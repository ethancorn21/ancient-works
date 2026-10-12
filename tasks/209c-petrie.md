Status: done
# 209c: Petrie, Stonehenge/Avebury (1880)
Depends on: 200
Touches: fit/src_wiltshire_petrie.py, data/books/triage/, data/books/lists/, data/commons/files_wiltshire_c.jsonl, data/commons/classified_wiltshire_c.jsonl, docs/lead_wiltshire.md, tests/test_src_wiltshire_petrie.py, tests/golden/src_wiltshire_petrie_sample.json

## Goal
Subtask of 209 (the parent's Hand-over has the full mechanics - read it): index Flinders
Petrie's *Stonehenge, Avebury, and other Stone Age monuments of the British Isles* (Macmillan
1880) and stage its plates tied to the existing sites (stonehenge-q39671, avebury-q661855,
silbury-hill-q225896, west-kennet-long-barrow-q541312, windmill-hill-q4348373 and the other
catalog Wiltshire earthworks its plates show). The book is NOT on IA (verified 2026-10-13)
and HathiTrust/Google Books are unreachable from this VM, so the subtask runs the 207c-Roy
local-copy leg: a human-downloaded copy is placed in data/raw/books/petrie1880/ (one page
image per file), the module adapts the fetch to those files, and the rest of the book
machinery (triageA/B, list transcription, staging, tests) runs unchanged. Fallback (only if
the human says no download): the two unlabeled fit-sized Commons files from the Flickr set
"Stonehenge- plans, descriptions and theories" (see 209b's Notes) - if 209b's visual check
proves one or both to be Petrie 1880 plates, this subtask becomes an open Commons-lead on
just those files instead.

## Acceptance criteria
- [x] (Fallback variant - ask_human 002 refused before iteration 151): the verified Commons files
      only, no book artifacts - the two canonical files.jsonl rows (209b visually verified as Petrie
      1880 Pl. I/II) pass fit/src_wiltshire_petrie.py --check offline (2/2 PASS); no triage/lists
      files, no data/raw/books/petrie1880/, no books.BOOKS registration.
- [x] No book artifacts to transcribe: the stage-A/B recall is recorded as n/a (no book - the
      refusal) in the Petrie section of docs/lead_wiltshire.md, in place of the shared validation.json
      (which was never written).
- [x] The two verified site-plan plates are tied to the existing site (stonehenge-q39671, by QID)
      with the 200 evidence field (caption_coords: the BL Georeferencer description names PETRIE /
      shelfmark / page / E. Stanford 1880; dist_m 0.0) and the book's date (1880) on each row - they
      are already canonical in data/commons/files.jsonl and are NOT re-staged into
      files_wiltshire_c.jsonl (the module's never-re-staged guard fails loud); no extras row
      (both plates show Stonehenge, a catalog site).
- [x] fit/evidence.py check passes offline on every row (2/2 PASS); 100% of the verified site-plan
      plates are on the map (both canonical) - nothing missing, nothing else stageable from Commons
      (the undelivered rest of the book is accounted for in docs/lead_wiltshire.md).
- [x] Test (no network, socket-blocked): tests/test_src_wiltshire_petrie.py - the table matches the
      canonical rows, --check passes, the negative controls (a missing canonical title, a re-staged
      Petrie title) fail loud, no book artifacts, the golden sample
      tests/golden/src_wiltshire_petrie_sample.json matches, the lead doc records the outcome.


## Notes
- BLOCKED on the open ask_human request (file it this session, the 207c pattern): the human
  downloads the 1880 book in a real browser (HathiTrust full-view - US public domain - or
  Google Books, which serves a PDF for it) and places one page image per file in
  data/raw/books/petrie1880/ (any resolution; the module re-encodes to triage size).
  Fallbacks in the request: (a) if the 209b visual check identifies the Commons Flickr
  files as Petrie's 1880 plates, stage those (no download needed); (b) drop 209c (then this
  lead stands on 209a/209b). How it is done: the file count matches the book's leaf count
  and the list pages are legible. If the human answers "drop", set Status: dropped and note
  it in docs/lead_wiltshire.md.
- The existing hand fits (Allcroft Avebury, Allcroft Windmill Hill - see 209b's Notes) are
  never re-staged or re-fitted: new rows only.
- LLM triage ports and background-job rules: see the parent's mechanics.

## Hand-over

(2026-10-13, iteration 156, agent a - task COMPLETE via the Commons fallback; Status: done.)

**What happened.** ask_human 002 (the human-downloaded 1880 book) was refused before iteration 151
(the 001 pattern; PITFALLS: "the human will not download books for this project"), so the book leg
is gone for good and the Commons fallback (a) - already satisfied by 209b's visual verification of
the two unlabeled Flickr files as Petrie 1880 Pl. I/II - is the final form of the task. This session
delivered it: fit/src_wiltshire_petrie.py (--check offline: PETRIE_ROWS table match +
never-re-staged guard + join + fit/evidence.py over both rows from stored fields; --golden),
tests/test_src_wiltshire_petrie.py (7 socket-blocked tests incl. two negative controls on tmp
files), tests/golden/src_wiltshire_petrie_sample.json, and the Petrie section of
docs/lead_wiltshire.md (the refusal verbatim, the two-row table with the W.M.F.P. identifications,
n/a recall, the undelivered rest of the book). All 5 boxes ticked (boxes 1-3 reworded to the
fallback variant the task's own Notes design; 209b's box-2 reword is the precedent), Status: done,
suite green (baseline 112 passed 1 skipped 0 failed; re-run green after these files).

**If this task is ever reopened** (only by a real copy of the book landing in
data/raw/books/petrie1880/ - a library digitisation, NOT a new human download ask): build the
209a-style local-copy wrap in fit/src_wiltshire_petrie.py (register in books.BOOKS + the 3-point
in-process wrap for pages/page_texts/fetch_triage), then triage A/F/B, list transcription from the
copy's own list pages, staging into files_wiltshire_c.jsonl (the module already holds the
staging-file constants and the join), the stage-A/B recall in the lead doc, and first reword
test_no_book_artifacts and the lead-doc test (they currently assert the no-book state).
