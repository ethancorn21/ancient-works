Status: dropped
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
- DROPPED (iteration 151, journal date 2026-10-13): ask_human 001 closed with "No. If you can't find the book
  at all, then i am not going to go get it. Just skip it." - the human will not download books
  for this project (PITFALLS), so the task's own "drop" fallback ran. The fetch leg
  (fit/src_wiltshire_hoare.py + tests/test_src_wiltshire_hoare.py) stays in the tree DORMANT:
  --fetch/--status/--triage work as-is if a complete scan of the Cherhill volume ever appears in
  data/raw/books/hoare_cherhill1821/ (one image per leaf page, filenames sorting in book order);
  the deferred legs (--list/--stage/--check/--golden) were never built. The Wiltshire lead stands
  on 209b (Stukeley) and 209c (Petrie - Commons leg; its download ask 002 was refused the same
  way, but 209b's Commons check had already satisfied its fallback).
- The existing hand fit on avebury-q661855 (Allcroft fig. 187,
  data/db/platefits/avebury-q661855.earthworkenglan01allcgoog_n0581_1.json) and the one on
  windmill-hill-q4348373 (Allcroft fig. 186) are never re-staged or re-fitted: new rows only.
- LLM triage ports: see the parent's mechanics (live replicas 127.0.0.1:8080-8082, in-process
  books.LLM_URLS patch; long triage runs are resumable nohup background jobs).

## Hand-over

(2026-10-13, iteration 151, agent a - FINAL session: task DROPPED on the human's answer to ask_human 001. No further work is planned for this task; what follows is the record of its end state.)

**What happened.** ask_human 001 (filed 2026-10-12 from the previous session: the human downloads the Cherhill volume 1821 -> data/raw/books/hoare_cherhill1821/, one image per leaf page, or says drop) was refused: "No. If you can't find the book at all, then i am not going to go get it. Just skip it." The companion request 002 (Petrie 1880, for 209c) was refused the same way. The task's own designed fallback therefore ran: Status: dropped, noted in docs/lead_wiltshire.md (the Hoare section records the refusal, the dormant fetch leg, and "stage-A/B recall: n/a").

**State left behind.** fit/src_wiltshire_hoare.py (--fetch/--status/--triage, the 207c 3-point in-process wrap) + tests/test_src_wiltshire_hoare.py (3 green hermetic tests; the register test now manages books.BOOKS via monkeypatch.setitem, closing the cross-test leak 209b diagnosed) STAY in the tree, marked DORMANT in the module header: --fetch/--status/--triage work as-is if a complete scan of the Cherhill volume ever lands in data/raw/books/hoare_cherhill1821/ (a library digitisation, an IA acquisition; one image per leaf page, filenames sorting in book order). The deferred legs (--list/--stage/--check/--golden) were never built, and no Hoare row exists in any staging file. The Wiltshire lead (209) stands on 209b (Stukeley: the IA book leg + the Commons leg) and 209c (Petrie: its Commons fallback is satisfied - 209b verified the two unlabeled Commons Flickr files as Petrie 1880 Pl. I/II, already canonical rows 713/714 in files.jsonl; 209c's session finalizes from its own hand-over - I did not edit 209c's files here, team mode).

**PITFALLS filed this session.** The one still-missing of the four drafted entries: "The human will not download books for this project - book leads stand on IA and Commons only" (the other three - the HathiTrust/Google 403/429 fact, the fit/ sys.path CLI trap, the book-machinery 3-point wrap - were already filed by other tasks). That entry also records: 207c's Roy 1793 request 003 (still open) will presumably get the same answer - if so, drop rather than re-ask.

**Suite state at drop time.** `.venv/bin/python -m pytest`: 109 passed, 1 skipped, 2 failed - both failures are 209b's own never-run session-4 tests (its files, which I did not touch - team mode): (a) `test_canonical_title_clash_fails_loud` calls `monkeypatch.setitem` on `src.STAGED`, but STAGED is a list, not a Mapping (`AttributeError: 'list' object has no attribute 'get'` in _pytest/monkeypatch.py:290); (b) `test_status_offline_fabricated_cache` fabricates bookreader pages carrying only `leafNum`, but `src_wiltshire_stukeley.status()` indexes `p["n"]` (`KeyError: 'n'` at fit/src_wiltshire_stukeley.py:187). 209b's Hand-over already names "run the tests" as its next session's first step, so the fixes land there. My three Hoare tests pass.

**If this task is ever reopened** (a copy materialises): the previous hand-over's runbook is in git history (this file before the drop; the 2026-10-12 209a DECISIONS entries): verify the leaf count -> --fetch -> --triage A (resumable nohup background job) -> list transcription into data/books/lists/hoare_cherhill1821.json -> --triage F/B -> stage / check / golden -> stage-A/B recall in the lead doc.
