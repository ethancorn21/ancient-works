Status: blocked
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
- [ ] A complete copy of the 1880 book is in data/raw/books/petrie1880/ (human-downloaded,
      per the open ask_human request); per-book artifacts only (triage/<id>.*.jsonl,
      lists/<id>.json, lists/<id>.map.json) are written; the shared data/books/index.jsonl
      and validation.json are NOT written. (Fallback variant: the verified Commons files
      only, no book artifacts.)
- [ ] The book's printed list of plates/figures is transcribed (the books_lists PLATES
      pattern, from the copy's own list pages) and mapped to leaves; the stage-A/B recall
      against that list is recorded in the Petrie section of docs/lead_wiltshire.md (instead
      of the shared validation.json).
- [ ] Staged rows (appended to the shared-per-suffix staging files, rows tagged with this
      book): files_wiltshire_c.jsonl for every verified site-plan plate tied to an existing
      site (by QID) - each with the 200 evidence field (the book's printed list names the
      place; the specific check - list entry, caption, coordinates distance - recorded on
      the row) and a classified row by hand ("plan"); the book's date (1880) is recorded on
      the row. A new extras_wiltshire_c.jsonl entry (add the path to Touches first) only for
      a plate showing a Wiltshire earthwork not in the catalog.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one is accounted for in
      docs/lead_wiltshire.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site)
      and the evidence check passes; a golden sample of rows
      (tests/golden/src_wiltshire_petrie_sample.json).

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

(2026-10-12, iteration 146, agent a - from 209b's Commons check; written by 209b, not this
task's own session.)

**The Commons Flickr check (209b's job) is done, and it unblocks your fallback.** Both
unlabeled fit-sized files are Petrie 1880 plates, visually verified (W.M.F.P. signature,
plate numbers, scales):
- `File:47 of 'Stonehenge- plans, descriptions and theories' (11135894643).jpg` (2245x2852)
  = **Pl. I** - the Stonehenge stone-by-stone plan, scale 1:350, the sarsen/bluestone key
  (Standing 1880 / Standing 1747 / Overthrown) and the outlying-stones forms 91/93/95/96.
- `File:49 of 'Stonehenge- plans, descriptions and theories' (11133409654).jpg` (4641x2874)
  = **Pl. II** - Stonehenge with the Avenue, the Cursus inset, the parallel banks,
  scale 1:1500, "Petrie levels in inches by numbering of stones".

**They are ALSO already in the canonical data/commons/files.jsonl** (rows 713/714,
stonehenge-q39671, year 1880, caption_coords evidence checked 2026-10-10, the British
Library Georeferencer description naming PETRIE / shelfmark HMNTS 10352.i.12 / page 47 /
E. Stanford 1880; machine-classified p_plan 0.94/0.92). So:
- If the human answers ask_human 002 with the downloaded 1880 book -> run the normal
  local-copy leg (data/raw/books/petrie1880/, the 207c/209a pattern).
- If the human declines ("use the Commons files") -> the Commons leg IS those two canonical
  rows already on the map: do NOT re-stage them into files_wiltshire_c (the Kip-pattern
  check fails loud on a title already canonical). Your boxes then read: verify the two
  canonical rows (evidence check offline), record that in the Petrie section of
docs/lead_wiltshire.md (stage-A/B recall: n/a - no book), and close what the Commons leg
covers. The book's other plates (Avebury, Silbury, West Kennet) are NOT in Commons and stay
undelivered unless the human downloads the book.
- The full findings and the Petrie note are in the Stukeley section of docs/lead_wiltshire.md
  and in 209b's DECISIONS entries (2026-10-12). Your Status stays blocked on 002 until the
  driver flips it.
