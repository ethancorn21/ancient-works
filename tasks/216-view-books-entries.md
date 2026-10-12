Status: done
# 216: Book machinery - BOOKS entries for the six artists'-view books (Civitates, Merian)
Depends on: 213, 215
Touches: pipeline/books.py, pipeline/books_lists.py

## Goal
The book machinery (`pipeline/books.py:BOOKS`) has no entries for the artists'-view books, so their
per-book files (213's `data/books/triage/civitatesorbiste00brau.A.jsonl`/`.F.jsonl`) cannot be driven by
`books.py` commands (fetch/triageA/B/F/ocrmap/validate/index all key on BOOKS). Add entries for the six
Internet Archive books task 213 verified - all BookReader streams, all free, metadata cached in
`data/raw/books/<ia>/` on this machine:

| key (suggest) | ia id | book |
|---|---|---|
| civitates_liber2 | civitatesorbiste00brau | Civitates Orbis Terrarum, Liber secundus (1575) - 292 leaves |
| civitates_liber4 | ARes73114 | Civitates Orbis Terrarum, Tomus quartus (1586) |
| civitates_liber5 | ARes73115 | Civitates Orbis Terrarum, Liber quintus (1597) |
| civitates_liber1 | 17095748888888bsb-00105587 | Civitates Orbis Terrarum, Liber primus (BSB scan, 1600) |
| merian_helvete00zeil | topographiahelve00zeil | Merian, Topographia Helvetiae (1654) |
| merian_panb665 | rcin.org.pl.WA51_13719_PANB665-r1642_Topographia-Helvetia_152915 | Topographia Helvetiae (PAN Poland, 1642) |

Region "Italy" is wrong for the German/Swiss/Austrian towns these books cover - use the region the
machinery expects for a book (see the existing entries' convention; the town's region comes from the
row, not the book, so pick the dominant one and say so in the `cite` string). The `cite` strings come
from `docs/lead_artists.md` (task 213).

## Acceptance criteria
- [x] The six entries exist in BOOKS (ia, region, year, cite); `books.py fetch <key>` works for at least
      civitates_liber2 (its 292 triage images already cached in data/raw - no re-download).
- [x] `books.py ocrmap civitates_liber2` and `validate civitates_liber2` run without KeyError (they may
      report "no list yet" - 217 adds the lists; do not add list data here, that is 217's module).
- [x] The existing BOOKS entries are untouched; `validate` over them gives the same results as before.

## Hand-over
**2026-10-12, iteration 112 (agent c): DONE.** All three boxes verified (see DECISIONS entry for outputs).

What landed (commit on agent/c, merge into main):
- `pipeline/books.py:BOOKS` += six entries, appended after `mills_1914`: `civitates_liber2` (civitatesorbiste00brau,
  1575), `civitates_liber4` (ARes73114, 1586), `civitates_liber5` (ARes73115, 1597), `civitates_liber1`
  (17095748888888bsb-00105587, 1600 BSB scan), `merian_helvete00zeil` (topographiahelve00zeil, 1654),
  `merian_panb665` (rcin.org.pl.WA51_13719_PANB665-r1642_Topographia-Helvetia_152915, 1642). All region
  "Europe" (the book-level field is coarse, the US/Europe convention of the existing entries; each cite
  string says what the volume covers - the four volumes whose lead-doc cite already carries a coverage
  tail keep it verbatim, the three without one get "towns of Europe (the dominant region; ...)" - the
  cached IA metadata for those three has no title/description, and 213 verified the town list for Liber
  secundus only). cite = verbatim from the docs/lead_artists.md table, markdown asterisks stripped to match
  the dict's plain-text cite convention. `why` records each book's verified status (all free BookReader
  streams, metadata cached 2026-10-11; liber2 = the only triaged volume).
- `pipeline/books_lists.py` (added to this task's Touches - 217's file, 217 builds on top, order 215->216->217):
  (a) the LIVE `cmd_ocrmap` now guards: for a book with no OCR list source (not in PLATES nor FIG_LISTS) it
  prints "no list yet (no OCR list source)" and does NOT write its `lists/<ia>.json[.map.json]` - the old code
  clobbered 213's 121-entry hand list with `{"plates": null, "figures": []}`. (b) Removed the DEAD duplicate
  `cmd_ocrmap` def (the first of two module-level defs; the second always shadowed it - a trap for 217).

Verified (all on this machine, .venv):
- `fetch civitates_liber2` -> "292 pages, 0 to fetch" (0.2 s, offline: bookreader.json + 292 triage images cached).
- `ocrmap civitates_liber2` -> "no list yet (no OCR list source); keeping the existing data/books/lists/civitatesorbiste00brau.json";
  hand-list .json/.map.json md5-identical after the run.
- `ocrmap` (no args, all 14 books) -> the eight existing books regenerate byte-identical list files (git status clean);
  mills_1914 also hits the guard (it never had a list source; its committed file IS the empty dump the old code
  wrote - no data drift, only the printed message changed).
- `validate civitates_liber2` -> no KeyError: {pages: 292, triaged_A: 292, flagged_site_pages_stageA: 3, stageF_pages: 118,
  flagged_site_pages: 11} - matches 213's record (A's 3 plate_site_plan = A187/A199 blank versos + A238).
- `validate` (no args, all books) -> all 8 existing book reports BYTE-IDENTICAL to committed validation.json;
  exactly one new entry (civitates_liber2). Per the 207 precedent the shared validation.json stays untouched until
  211's rebuild: I restored it after the run (git checkout -- data/books/validation.json). 217: same convention.
- `pytest tests/ -q` -> 100 passed, 1 skipped, 0 failed.

Notes for 217 (the follow-on, Depends on: 216):
- The guard fires only while a book has no PLATES/FIG_LISTS entry: once you lift 213's hand list into the module
  (217 box 1), `ocrmap civitates_liber2` regenerates the file from the module as 217 box 1 specifies - compatible.
- `books.py index <subset>` TRUNCATES the shared index.jsonl (writes only the args' books' rows) - run it with no
  args only, at the 211/217 rebuild stage (pitfall filed).
- `books_match.BOOK_SCOPE` still has no entry for the six keys: a missing scope means no region/state filter in the
  matcher (not an error); 217 decides whether the view books need scope entries once index rows exist.
- The five untriaged books need fetch (downloads bookreader.json for the BSB + PAN-Poland items; then triage images)
  then triageA/F (LLM ports 8080-8082 live per 215) and hand lists - same flow as Liber secundus; the A/F plan-label
  bias pitfall applies to all of them.
