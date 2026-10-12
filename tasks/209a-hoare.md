Status: in-progress
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

## Hand-over

(2026-10-12, iteration 145, agent a - first working session after the 144 split. Task now WAITS ON ask_human 001; the fetch leg is built and tested.)

**This session (done):**
1. Re-verified the blocker: IA title-phrase search -> only two modern books (Hoare absent); HathiTrust babel 403 from this VM (browser UA + plain UA); LLM replicas 8080/8081 up, 8082 resetting, 18080/8081 down (books.LLM_PORTS covers 8080-8082; run_stage uses whichever answers).
2. **Filed ask_human 001** (human_only: outside-vm, blocking): human downloads the Cherhill volume (1821) into data/raw/books/hoare_cherhill1821/ (one image per leaf page, filenames sorting in book order; a PDF is OK if said in the reply; vols 1-2 bonus -> hoare_pewmarsh1812/ + hoare_pewsey1819/); fallbacks "drop" (-> Status: dropped + lead-doc note) or any other complete scan. **Also filed 002 for 209c (Petrie 1880 -> data/raw/books/petrie1880/; fallbacks "hold" for 209b's Commons Flickr check, then "drop")** - the parent's plan assigned both filings to 209b's session, which never ran; 209c stays Status: blocked, now with an open request (driver holds it until the answer).
3. **Built the fetch leg (the 207c local-copy pattern):** `fit/src_wiltshire_hoare.py` - in-process `books.BOOKS["hoare_cherhill1821"]` registration + a 3-point wrap of the machinery's IA-only calls (books_ia.pages / books_ia.page_texts / books.fetch_triage; for this id only, idempotent via `books_ia._hoare_wrapped`, pass-through for every other id); the local re-encode (1400 px long side, JPEG q88, .part+rename) lands at the exact `books.triage_path` slot (DIR/triage; for the default DIR that IS ia.RAW/ID/triage), so `books.run_stage` A/F/B runs UNMODIFIED. `page_texts -> {}` for the local copy (no per-page OCR; map_plates then works on Qwen anchors alone - verified: empty text leaves sw=0, so inked pages stay candidates). Commands: `--fetch` (local, resumable, idempotent; missing/empty book dir fails loud naming ask_human 001), `--status` (offline: leaves, triage progress, LLM ports), `--triage A|F|B`. `tests/test_src_wiltshire_hoare.py` - 3 hermetic tests (natural ordering 1/2/10/11 + downscale + byte-identical idempotent rerun; missing book dir absent OR empty fails loud; register pass-through with recording fakes + the triage-slot invariant vs books.triage_path). `docs/lead_wiltshire.md` created (lead doc: the per-suffix staging rules; the Hoare section records source status, the request, the fetch leg; the "Stage-A/B recall" line is the placeholder).
4. **Tests last run (after all code edits):** full suite **104 passed, 1 skipped, 0 failed** (~177 s); the three new tests pass.

**Waiting on:** ask_human 001 (the human downloads the book; hours to days). The code is NOT committed by me - the harness saved it; it is in the working tree (new files fit/src_wiltshire_hoare.py, tests/test_src_wiltshire_hoare.py, docs/lead_wiltshire.md).

**Next steps when the answer arrives (in order):**
1. **Book placed** in data/raw/books/hoare_cherhill1821/: if it is a PDF, unpack first (`sudo apt-get install -y poppler-utils`; `pdftoppm -jpeg -r 150 <pdf> leaf-`; record the new package in PITFALLS when doing it), then `--status` (verify: file count = the book's leaf count, list page legible) -> `--fetch` -> `--triage A` as a resumable nohup background job (207c pattern for long triage runs).
2. Transcribe the printed list of plates from the copy's own list pages (books_lists PLATES pattern `plate||title[|sub]|page|kind`, kind s/o/u) -> data/books/lists/hoare_cherhill1821.json; inject `books_lists.PLATES[ia]` in-process, then `books_lists.cmd_ocrmap([KEY])` -> lists/<id>.map.json (per-book artifacts only; the 216 guard in cmd_ocrmap keeps nothing else).
3. `--triage F`/`B` on the plan pages; measure recall/precision against the list (map_plates / validate_book logic, per-book) -> record the numbers in the "Stage-A/B recall" line of docs/lead_wiltshire.md (NEVER write the shared validation.json/index.jsonl - 211 rebuilds).
4. Add the module's `--stage`/`--check`/`--golden` legs (spec in the module header): rows into data/commons/files_wiltshire_a.jsonl + classified_wiltshire_a.jsonl (200 evidence field: the list entry names the place; the specific check - list entry / caption / coordinates distance - on the row; the 1821 date), extras_wiltshire_a.jsonl ONLY for a plate showing a Wiltshire earthwork not in the catalog (add that path to the task's Touches first). Sites to tie: stonehenge-q39671, avebury-q661855, silbury-hill-q225896, west-kennet-long-barrow-q541312, windmill-hill-q4348373 + other catalog Wiltshire earthworks. check = offline join + fit/evidence.py; golden = tests/golden/src_wiltshire_hoare_sample.json; extend tests/test_src_wiltshire_hoare.py with the staging/check/golden tests (keep the fetch-leg tests as they are). Acceptance box 4: >= 90% of verified site-plan pages staged or each missing one accounted for in the lead doc.
5. Never re-stage or re-fit the existing hand fits (Allcroft Avebury fig. 187, Allcroft Windmill Hill fig. 186 in data/db/platefits/).
- **If "drop":** set this file's Status to dropped; note it in the Hoare section of docs/lead_wiltshire.md; the lead stands on 209b/209c.
- **If "other scan":** same flow as "book placed" (one image per leaf page).

**Do not:** write the shared data/books/index.jsonl / validation.json; re-stage the hand fits; edit pipeline/ files (owned by other tasks); run git merge/rebase/reset/stash/branch-switch.

**PITFALLS entries drafted but NOT yet filed (add them verbatim-ish to PITFALLS.md next session):**
(a) under "This machine and its environment": *HathiTrust and Google Books refuse this VM - books not on IA need a human download (the 207c pattern)* - Where: any fetch from babel.hathitrust.org / the Google Books API (207c Roy 1793, 209a Hoare Cherhill 1821, 209c Petrie 1880); Symptom: HTTP 403 from babel.hathitrust.org with every UA (including a full browser UA) and HTTP 429 from the Google Books API with our and a browser UA; IA advancedsearch empty for these titles; Why: bot walls that a real browser passes and this VM cannot; consequence: the copy arrives human-downloaded (ask_human human_only: outside-vm) into data/raw/books/<id>/, one image per leaf page, filenames sorting in book order, and the consuming module adapts the fetch locally (fit/src_wiltshire_hoare.py; 207c's will do the same). Verified 2026-10-11 (Roy) and 2026-10-12 (Hoare).
(b) under "### fit/": *a fit/src_*.py CLI that lazily imports pipeline modules needs its own sys.path insert at module top - tests hide it* - Where: fit/src_wiltshire_hoare.py (status()/register() import books lazily; src_mackenzie.py does the insert at top); Symptom: `python fit/src_wiltshire_hoare.py --status` -> ModuleNotFoundError: No module named 'books' while pytest passes; Why: the test file inserts pipeline/ (and fit/) into sys.path before importing the module, but bare `python <script>` puts only the script's own dir on the path; do the `sys.path.insert(0, <root>/pipeline)` at module top like src_mackenzie.py (this module already has it).
(c) under "### pipeline/books.py, pipeline/books_ia.py (the book machinery)": *a human-downloaded book (not on IA) runs the UNMODIFIED machinery through a 3-point in-process wrap* - Where: fit/src_wiltshire_hoare.py register(); books.py run_stage; books_ia.pages/page_texts; books_lists.map_plates (207c's Roy module will do the same); Symptom: cmd_fetch/ia.pages/ia.page_texts hit the network for an ia id that is really a local directory name; Why: the machinery is IA-only in exactly three places - page list (ia.pages), per-page OCR (ia.page_texts), page-image fetch (books.fetch_triage) - and wrapping those for one id plus a BOOKS entry whose ia field is the local dir name (so books.triage_path lands at data/raw/books/<id>/triage/) is all that triage A/F/B, map_plates and staging need: page_texts -> {} (Qwen anchors only; empty text keeps inked pages as map_plates candidates), fetch re-encodes the local files into the triage slot (1400 px long side, q88); a test monkeypatches the module's book DIR (the triage tree follows it) + the socket-blocking fixture -> hermetic.
