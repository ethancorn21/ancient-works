Status: split
# 209: Wiltshire - Hoare, Stukeley, Petrie for Stonehenge and Avebury
Depends on: 200
Touches: fit/src_wiltshire.py, data/books/triage/, data/books/lists/, data/commons/files_wiltshire.jsonl, data/commons/classified_wiltshire.jsonl, docs/lead_wiltshire.md, tests/test_src_wiltshire.py

## Goal
GOAL.md point 4: old drawings of the two most famous sites on the map - Stonehenge and
Avebury - from Hoare, Ancient Wiltshire (1812-21), Stukeley's Wiltshire volume (1740s) and
Petrie's Stonehenge (1880). Index the relevant plates with the existing book machinery
(per-book files only; the shared index.jsonl and validation.json are rebuilt by 211), and
stage the rows tied to the existing sites (stonehenge, avebury, and the other Wiltshire
henges the plates show). The sites are already built; this task adds their pictures. An
extras file is only needed if a plate shows a Wiltshire earthwork not in the catalog yet.

## Acceptance criteria
- [ ] The three works are fetched from the Internet Archive (data/raw/books/<ia>/) and
      triaged with the existing machinery, per-book artifacts only (lists/<key>.json,
      triage/<ia>.*); the shared data/books/index.jsonl and validation.json are NOT written
      by this task. Each work's printed list of plates is mapped (the books_lists pattern)
      and the stage-A/B recall recorded in docs/lead_wiltshire.md per work.
- [ ] Staged rows: files_wiltshire.jsonl for every staged Stonehenge / Avebury / Wiltshire
      earthwork plate tied to an existing site (by QID, or by the work's printed list where
      no QID exists), each with the 200 evidence field (the specific check - list entry,
      caption, coordinates distance - recorded on the row) and a classified row by hand
      ("plan"); the work's date (1740-1880) recorded on the row.
- [ ] The human's existing hand fits on these sites (already in data/db/platefits/ and
      fitted onto the pages) are not re-staged or re-fitted by this task: new rows only.
- [ ] fit/evidence.py check passes offline on every staged row; test (no network): the
      staged files join (every row names an existing site, or a staged extras row if any)
      and the evidence check passes, with a golden sample of rows.

## Notes
- Stukeley's Wiltshire (1740s) has several volumes/editions on IA: use the one with the
  complete plate set, recorded in docs/lead_wiltshire.md.
- If the three works are too much for a few sessions: split into 209a (Hoare), 209b
  (Stukeley), 209c (Petrie) - one work per subtask, each with its own per-book artifacts and
  its own staging suffix (files_wiltshire_a.jsonl etc.), same shape of boxes; record the
  per-work page list in this parent's hand-over. 211 consolidates whatever staging exists.
- A plate that shows a site outside Wiltshire (Stukeley travelled) is still staged, with the
  right site - the task is named for the lead, not a boundary.

## Proposed changes

Acceptance box 1 says 'fetched from the Internet Archive (data/raw/books/<ia>/)'. Investigation (2026-10-13, iteration 144) found **none of the three works is on IA** (exhaustive advancedsearch: title phrases, description phrases, identifier prefixes, author, year; the 2026-10-10 data/books/summary.md already said the same for Hoare). The VM also cannot reach the fallback sources itself: HathiTrust 403s every request (our UA and the harness web_fetch), the Google Books API 429s (both our UA and a browser UA). Same situation as 207c (Roy): the human must obtain the copies. Proposed: (a) for Hoare (209a) and Petrie (209c) the human downloads the books in a real browser (HathiTrust full-view or Google Books) and places the page images under data/raw/books/<id>/; the subtasks adapt fetch to the local files (the 207c recipe) and run the rest of the book machinery unchanged; (b) for Stukeley (209b) use what IS on IA - the complete BMB scan of *Stonehenge, a Temple Restor'd to the British Druids* (1740), ia=bim_eighteenth-century_stonehenge-a-temple-rest_stukeley-william_1740 (BookReader pages + hOCR verified working) - plus Commons-hosted Stukeley plates (his 1740 Avebury plan among them) staged as a Commons-lead (the 205 pattern); if the human can also get *A survey of Wilts* (1740, the true Wiltshire volume), 209b takes it as a second book. If a download is not obtainable, the affected subtask is dropped and this lead stands on the rest. The boxes keep their shape (per-book artifacts, staged rows, offline tests) - only the fetch source changes.

## Hand-over

(2026-10-12, iteration 145, agent a - update on the 144 split; the per-book facts below stand.)

**State.** 209a (Hoare) in-progress, waiting on **ask_human 001** (filed 2026-10-12 from 209a's own session: human downloads the Cherhill volume -> data/raw/books/hoare_cherhill1821/; fallbacks drop/other scan); its fetch leg is BUILT and tested (fit/src_wiltshire_hoare.py --fetch/--status/--triage, the 207c 3-point in-process wrap; tests/test_src_wiltshire_hoare.py 3 green; docs/lead_wiltshire.md created with the Hoare section) - see 209a's Hand-over for the on-arrival runbook. 209c (Petrie) blocked, now with **ask_human 002** open (filed from 209a's session too: the plan here had assigned both filings to 209b's session, which never ran; 002 asks for the 1880 book -> data/raw/books/petrie1880/, fallbacks "hold" for 209b's Commons Flickr visual check then "drop"). Suite state at 209a's session: 104 passed, 1 skipped, 0 failed.

**Next: 209b first** (the only subtask that can run without a human: the Stukeley IA book leg + the Commons leg; its Notes carry the file list). Read the per-book facts below before starting any subtask.

### Per-book facts (measured this session)

- **Hoare, Ancient Wiltshire (1812-21)** - NOT on IA (advancedsearch 2026-10-13: title 'ancient wiltshire' -> only two modern books; the hundreds 'hundred of pewmarsh/pewsey/cherhill' -> 0; identifier patterns -> 0). On HathiTrust (a 2025 blog links babel mdp.39015023917472 for an 'Ancient Wiltshire, North' volume) but HathiTrust 403s from this VM. Commons Category:Richard Colt Hoare has portraits/views only; the only *Ancient Wiltshire* plate found is a Normanton Down barrow-find illustration (no site plans). The volume that carries the Stonehenge/Avebury/Silbury plans is vol. 3, *The Hundred of Cherhill* (1821) - VERIFY the plate contents from the human-downloaded copy (list-of-plates transcription is the subtask's job). => 209a BLOCKED on ask_human (207c pattern: human downloads, places files in the repo, or says drop).
- **Stukeley (1740s)** - the true Wiltshire volume (*A survey of Wilts*, 1740) is NOT on IA (title/description searches: 0) and not on Commons as a book. BUT: (1) **IA HAS a complete BMB scan of *Stonehenge, a Temple Restor'd to the British Druids* (1740)**: ia=bim_eighteenth-century_stonehenge-a-temple-rest_stukeley-william_1740 - verified this session: 21 files incl. hOCR (14.7 MB), DjVuTXT, scandata, JP2 zip; page/n0.jpg and n1.jpg download at ~8 MB each (re-encode to triage size); a second copy exists: bim_eighteenth-century_i-having-been-sollicited_stukeley-william_1741. Its plates include Stukeley's famous numbered Stonehenge plan, the Avenue plan and a Wiltshire map - they tie to stonehenge-q39671. (2) **Commons has the 1740 Avebury plan**: File:Houghton Arc 855.214 - Stukely, the Druid temple of Abury.jpg (2269x1362, fit-sized, NO description metadata - VISUALLY VERIFY before staging). Also fit-sized: File:Stonehenge Dessin Stukeley 1722 03547.jpg (4620x2430, the 1722 Itinerarium drawing) and File:Stonehenge Stukley Oxford 03543.jpg (3606x2976, source unverified). Everything else in Category:William Stukeley is <1000 px (e.g. Stonehenge Stukeley.jpg 773x404 = the 1740 plan, too small) or not a site drawing (Clarendon palace ruins 1723 = Roman/medieval, check whether it is a catalog site). => 209b OPEN: IA book leg (standard machinery) + Commons-leg rows; if the human also delivers *A survey of Wilts*, add it as a second local-copy book to 209b.
- **Petrie, *Stonehenge, Avebury, and other Stone Age monuments of the British Isles* (1880)** - NOT on IA (title/description/identifier searches: 0; the only 1880 'stonehenge' item is an Oxfordshire Rollright pamphlet) and NOT in Commons Category:Books by Flinders Petrie (71 files, all his Egypt books). Two unlabeled fit-sized files sit in Commons from the Flickr set 'Stonehenge- plans, descriptions and theories': File:47 of '...' (11135894643).jpg (2245x2852) and File:49 of '...' (11133409654).jpg (4641x2874) - both have EMPTY description metadata; VISUALLY CHECK whether either is the Petrie 1880 Stonehenge plan (209b does the check; that finding flips 209c to an open Commons-lead). The 1880 book (Macmillan; US public domain) should be on HathiTrust/Google Books for a human browser. => 209c BLOCKED on ask_human (recommend: human downloads the 1880 book -> data/raw/books/petrie1880/; fallback: the Commons Flickr files if they prove to be Petrie's, or drop).
