Status: in-progress
# 207b: Maclauchlan, the survey of the Roman Wall (1857-58)
Depends on: 200
Touches: fit/src_roman_maclauchlan.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_maclauchlan.py, tests/golden/src_roman_maclauchlan_sample.json

## Goal
Subtask of 207 (the parent's Hand-over has the full mechanics): index Maclauchlan's survey of
Hadrian's Wall with the existing book machinery and stage its site-plan rows tied to the
forts on the wall. The parent's task says 1857: the survey of the wall's eastern branch ran
1857-59 and the volume was published 1858 - use the year printed on the title page and note
the discrepancy in the lead doc. Chosen IA copy: `memoirwrittendu00maclgoog` (the 1858
original, Google scan, 171 leaves, median 3290x5182 px; djvu.txt only, NO hOCR page index).
Alternative for reading text/list pages: `memoirwrittendur0000henr` (1971 reprint, 292
leaves, 1625x2697 px, hOCR present) - use it to transcribe the book's list, but stage images
only from the 1858 original.
The book's plates include detailed plans of the forts on the wall (Vindolanda, Vercovicium,
etc.) alongside wall cross-sections and stretches of the wall itself. Per the parent's
Notes: wall sections are not sites and are not staged, unless a named fort/structure with a
location is in the plate.

## Acceptance criteria
- [x] The book is fetched from the Internet Archive (data/raw/books/memoirwrittendu00maclgoog/)
      and triaged with the existing machinery, per-book artifacts only
      (triage/memoirwrittendu00maclgoog.*.jsonl, lists/memoirwrittendu00maclgoog.json,
      lists/memoirwrittendu00maclgoog.map.json); the shared data/books/index.jsonl and
      validation.json are NOT written by this subtask.
- [ ] The book's own printed list of plates is transcribed (the books_lists PLATES pattern)
      and mapped to leaves; the stage-A/B recall against that list is recorded in the
      Maclauchlan section of docs/lead_roman.md (instead of the shared validation.json).
- [ ] Staged rows (appended to the parent's shared staging files, rows tagged with this
      book): files_roman.jsonl for every verified site-plan page of a named fort/structure
      tied to a Roman site - an existing catalog site by QID where one exists, or a new
      extras_roman.jsonl entry (kind "roman fort" / "roman site", QID where it exists,
      lon/lat from the book's list or a cross-check) - each with the 200 evidence field
      (list entry, caption, coordinates distance recorded on the row) and a classified row
      by hand ("plan"); the book's date (title-page year, 1857/1858) is recorded on the row.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one (wall sections, sections alone) is
      accounted for in docs/lead_roman.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.

## Notes
- Same mechanics as 207a: in-process book registration in books.BOOKS, books.LLM_URLS
  patched to the live replicas (127.0.0.1:8080-8082) when the built-in ports are down,
  per-book triage/lists artifacts only, shared staging files tagged per book.
- Most wall forts are already in the catalog (the 206 England roman_fort rows include the
  wall forts with QIDs, e.g. vindolanda QID-less extra plus hardknott, concangis, glannoventa,
  whitley-castle, milecastles). Tie to them where the plate's site matches; stage a new site
  only for a named place not in the catalog.

## Lead note (2026-10-13)
Blocked: the owner said "Stop 207". Do not start until the owner lifts it.
(2026-10-13: LIFTED - the owner answered ask_human 006/007 (both asking whether the stop
still stands) with "b" = the stop is lifted; 207a was completed on that lift (7e9c829) and
207c dropped on the owner's answer to ask 008. This note records the stop as made.)

## Hand-over
(2026-10-14, iteration 132, agent c - the stage-B session. READ THIS FIRST.)

**What happened this session.**
1. 131's uncommitted work is safely committed by the driver (66530ec "[driver] uncommitted
   work after iteration 131"): working tree was clean at session start and both list
   artifacts md5-match 131's recorded values (8479d53f196fed1fa2bb0d7159b58257 /
   f6593c9e01c19157daf997e7a03bb04a). Hand-over item 1 is DONE - nothing owed on it.
2. `--status`: replicas 8080/8081 UP (8082 down), 171/171 leaves fetched, stage A 171/0.
3. **`--triage B` live (131's item 2): 3 pages (78, 93, 111 = A's site set ∪ list's kind-s
   set), 3/3 ok, 0 errors, 9.7 s on the two live replicas.** Sole new file:
   `data/books/triage/memoirwrittendu00maclgoog.B.jsonl` (per-book, committed this
   session). Rows (map_box = norm1000 over each triage image, 964x1400):
   - **n0093 (the Carlisle plan - the one that gets staged):** map_box **[100,405,830,880]**
     (= px 96,567-800,1232 on 964x1400), label "FIG. 4", scale_text "Scale of Chains. 0 5
     10 Chains. Scale of Feet. 0 100 ... 1000 Feet."; the LLM's site_names are street
     labels (Trinity Church, Bury Street, New Sewer) - the row's named place comes from
     the binder's list (130's Decision 3), not from B.
   - n0078 (Brampton, blank, not staged): map_box [160,98,875,860], site_names [BRAMPTO] -
     record only.
   - n0111 (the 1856 Housesteads gateway, blank, not staged): map_box [338,495,595,512] is
     the scale-bar strip, not the small blank figure - record only.
4. **Box 1 ticked in the task file**: fetched 171/171 + triage A 171/0 + B 3/0 + per-book
   lists (131); the shared data/books/index.jsonl and validation.json were NOT written
   (git status showed only the B file). No stage F needed: A's site set equals the list's
   kind-s set exactly (nothing missed).

**Suite state:** not run this session (data-only leg; no test reads the B jsonl -
test_merge.py joins only stage-A `.A.jsonl` files; my own test file is not built yet).
The driver's 2026-10-13 baseline 159/1/1 stands (the lone red is agent a's 307d
placement test).

**Acceptance boxes:** box 1 ticked this session. Box 2 half (lists on disk; the
stage-A/B recall record in docs/lead_roman.md is what remains - next step 1). Boxes
3-5 untouched.

**Exact next steps (133+, in order).**
1. **validate_book offline -> the NEW "## Maclauchlan" section in `docs/lead_roman.md`,
   inserted after the lead's header, BEFORE the "## Roy" section** (subtask order
   Horsley, Maclauchlan, Roy; 807's Horsley section is absent while 807 is blocked - if
   a merge brings it, move my section AFTER it and NEVER edit 807's text). Run it the
   131 offline way: a socket-blocking wrapper (import urllib.request/ssl/socket FIRST,
   patch socket.socket.connect + socket.create_connection to raise), then
   importlib-load fit/src_roman_maclauchlan.py, register(), books_lists.validate_book(KEY).
   EXPECTED (hand-computed from validate_book's source, pipeline/books_lists.py:895-994,
   the HAND_FIGS figs branch - record what actually runs): pages 171, triaged_A 171,
   flagged_site_pages 3 (stage F 0), figures: listed 6 / site 3 / other 3 / unsure 0 /
   expected None, gt_site_pages 3, recall_pages 1.0 (±1: 1.0), flagged_nonplate_pages 3,
   precision_strict 1.0, precision_lenient 1.0, flagged_on_other_only_pages [] (90/129
   are other_illustration), missed_pages [], stage_A_only {recall 1.0, flagged 3}.
   Section contents: source (the 1858 original is the only readable IA copy; the
   Nochlin mislabel + the lending-restricted 2015 Wanney presentation, both unusable -
   PITFALLS), the no-list discovery (no printed plate list anywhere; the binder's
   directions, djvu leaf 119, are the book's list verbatim - quoted in the module
   docstring), the 6-line inventory with per-leaf verdicts, the blank-plate findings
   (n0078, n0111), the unprinted Figs 2/3/5/6 (the 122 size census), the DATE
   DISCREPANCY (title-page survey 1852-1854 + imprint MDCCCLVIII 1858 vs the parent's
   1857-59; the 1858 printing carries later 1857-58 work - the Willow Holm section taken
   Sep't 7th 1858, the Carlisle plan's 1857-58 great sewer; gift leaf n0007 1859), the
   stage-A/B recall numbers, and the 90% accounting (1 staged of 3 verified site plans
   = 33% < 90%; n0078 and n0111 each accounted for individually as blank in this copy -
   the box's disjunct).
2. **Build `--stage`** (read tasks/808-horsley-stage.md in full first for the
   row-content conventions; re-read data/commons/files.jsonl's row shape, a
   no-QID row of data/catalog/extras.jsonl (the location_check field), fit/evidence.py
   with fresh eyes): create the three shared files (absent on this branch) with the
   decided rows - extras_roman.jsonl +1 (Luguvallium (Carlisle), Q71551754,
   lon/lat 54.896187/-2.94077, kind "roman fort" SPACE form, region england, place
   "Carlisle, Cumberland, England", location_check per 130's Decision 2); files_roman.
   jsonl +1 (n0093: site = the new extras id, qid Q71551754, title/desc carrying
   "Carlisle" + the binder's-list entry + the p.77 reference; year 1858; url/thumb the
   IA page image https://archive.org/download/memoirwrittendu00maclgoog/page/n0093.jpg;
   w/h from the triage row [964,1400]; map_box from this session's B row
   [100,405,830,880]; the caption_coords evidence of 130's Decision 3: named_place
   Carlisle, place Q192896 P625 54.894722/-2.936389, dist_m 324.1); classified_roman.
   jsonl +1 ((site,title), class "plan" by hand). Append-only, idempotent (a second run
   changes no byte), rows tagged memoirwrittendu00maclgoog, --dry previews.
3. **`--check` (offline: join staged rows to catalog+extras - every row names an
   existing or staged site, every new site has its plans; fit/evidence.py check over
   this book's rows) + `--golden` (tests/golden/src_roman_maclauchlan_sample.json) +
   tests/test_src_roman_maclauchlan.py** (the no_network socket-blocking fixture as in
   tests/test_src_van_deventer.py - monkeypatch socket.socket/create_connection/
   getaddrinfo; no LLM calls in tests; no fixed ports; writes only inside the project).
   Then run the suite (baseline 159/1/1; my tests must all pass, the lone 307d red
   stays) and re-baseline in the notes.

**Re-read next session:** `fit/src_roman_maclauchlan.py` (--stage/--check/--golden NOT
built - main() rejects them with the docstring pointer; MACLAUCHLAN_FIGS + docstring
current); `tasks/808-horsley-stage.md` (in full - row-content conventions);
`data/commons/files.jsonl` (row shape); `data/catalog/extras.jsonl` (no-QID row shape,
location_check field); `fit/evidence.py` (check/check_commons/check_caption);
`pipeline/books_lists.py:895-994` (validate_book, the HAND_FIGS figs branch - expected
numbers above); `data/books/triage/memoirwrittendu00maclgoog.B.jsonl` (this session's 3
rows); the djvu text is cached at data/raw/books/memoirwrittendu00maclgoog/
memoirwrittendu00maclgoog_djvu.xml (leafNum = n+1, aligned 1:1).
