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
- [x] The book's own printed list of plates is transcribed (the books_lists PLATES pattern)
      and mapped to leaves; the stage-A/B recall against that list is recorded in the
      Maclauchlan section of docs/lead_roman.md (instead of the shared validation.json).
      (The book has NO printed plate list - its only list is the binder's directions, djvu leaf
      119; the ground truth is the per-leaf hand table per the 207a/Horsley fallback, 131's
      decision; transcribed + mapped + recall recorded as decided.)
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
(2026-10-14, iteration 133, agent c - the validate_book / lead-doc session. READ THIS FIRST.)

**What happened this session.**
1. Ran `validate_book` OFFLINE: socket-blocking wrapper (import urllib.request/ssl/socket
   FIRST; patch socket.socket.connect + connect_ex, socket.create_connection, socket.getaddrinfo
   to raise; then importlib-load fit/src_roman_maclauchlan.py, register(), books_lists.
   validate_book(KEY)). No network, no LLM. Output matched the 132 hand-over's hand-computed
   expectations EXACTLY: pages 171, triaged_A 171, flagged_site_pages_stageA 3, stageF_pages 0,
   flagged_site_pages 3; figures listed 6 / site 3 / other 3 / unsure 0 / expected None,
   gt_site_pages 3, recall_pages 1.0 (±1: 1.0), flagged_nonplate_pages 3, precision_strict
   1.0, precision_lenient 1.0, flagged_on_other_only_pages [], flagged_not_in_list [],
   missed_pages [], stage_A_only {recall 1.0, flagged 3}; no "plates" key (no printed list -
   the figs branch is the list). Mechanism verified in source: `flagged` = site_pages_qwen =
   stage-A SITE_TYPES rows surviving ink >= BLANK_INK (0.005); measured ink 0.0102 (n0078),
   0.0352 (n0093), 0.1048 (n0111) -> all three in; 90/129 other_illustration, 115 text_only ->
   never flagged. Filed as a PITFALLS entry (validate_book offline-safe + the ink-drop trap).
2. Wrote the "## Maclauchlan" section into docs/lead_roman.md, inserted after the lead header,
   BEFORE "## Roy" (subtask order; if a merge brings 807's Horsley section, mine moves AFTER
   it - never edit 807's text; the lead's own title line still says 1857-58 - I left the
   header untouched and the section records the corrected date). Contents: source (1858
   original the only readable copy; Nochlin mislabel + Wanney LCP-restriction, PITFALLS),
   DATE (survey 1852-1854 + imprint MDCCCLVIII 1858 vs the parent's 1857-59; the 1858 printing
   carries later 1857-58 work - Willow Holm section Sep't 7th 1858, the Carlisle great sewer;
   gift leaf n0007, 1859), the no-list finding (binder's directions verbatim + the hand-table
   fallback), the 6-leaf inventory with per-leaf verdicts (n0078 BLANK, n0090 wall section,
   n0093 the only legible plan - the one that gets staged, n0111 BLANK, n0115 table, n0129
   tiles), the unprinted Figs 2/3/5/6 (122 size census), the stage-A/B recall numbers, and
   the 90% accounting (1 of 3 = 33% < 90%; the two missing each accounted for as blank in
   this copy - the box's disjunct).
3. Box 2 ticked: the list (binder's directions -> per-leaf hand table, 131's decision) is
   transcribed and mapped to leaves (lists/*.json + .map.json, byte-stable since 131), and the
   stage-A/B recall is recorded in the lead doc's Maclauchlan section.
4. Suite NOT run this session (doc/offline-run session; no code changed, no new test). The
   driver's 2026-10-13 baseline 159/1/1 (lone red = agent a's 307d placement test) stands.

**Acceptance boxes:** box 1 (132), box 2 (this session) ticked. Boxes 3-5 untouched.

**Exact next steps (134+, in order).**
1. **Build `--stage`** in fit/src_roman_maclauchlan.py (read tasks/808-horsley-stage.md in
   full first for the row-content conventions; re-read data/commons/files.jsonl row shape,
   a no-QID row of data/catalog/extras.jsonl (the location_check field), fit/evidence.py
   with fresh eyes): create the three shared staging files (ABSENT on this branch) with the
   decided rows - extras_roman.jsonl +1 (Luguvallium (Carlisle), Q71551754, lon/lat
   54.896187/-2.94077, kind "roman fort" SPACE form, region england, place "Carlisle,
   Cumberland, England", location_check per 130's Decision 2); files_roman.jsonl +1 (n0093:
   site = the new extras id, qid Q71551754, title/desc carrying "Carlisle" + the binder's-
   list entry + the p.77 reference; year 1858; url/thumb the IA page image
   https://archive.org/download/memoirwrittendu00maclgoog/page/n0093.jpg; w/h 964x1400 from
   the triage row; map_box [100,405,830,880] from this book's B row; evidence kind
   caption_coords: named_place Carlisle, place Q192896 P625 54.894722/-2.936389, dist_m
   324.1); classified_roman.jsonl +1 ((site,title), class "plan" by hand). Append-only,
   idempotent (a second run changes no byte), rows tagged memoirwrittendu00maclgoog, --dry
   previews. Then verify the lead doc's n0093 line (written this session) matches what was
   actually staged (the tie to the new Luguvallium site).
2. **`--check` (offline: join staged rows to catalog+extras - every row names an existing or
   staged site, every new site has its plans; fit/evidence.py check over this book's rows)
   + `--golden` (tests/golden/src_roman_maclauchlan_sample.json) + tests/
   test_src_roman_maclauchlan.py** (the no_network socket-blocking fixture as in
   tests/test_src_van_deventer.py; no LLM calls in tests; no fixed ports; writes only
   inside the project). Then run the suite (baseline 159/1/1; my tests all pass, the lone
   307d red stays) and re-baseline in the notes.
3. **Boxes 4-5 -> done**: box 4's evidence check is covered by --check's test; the 90%
   accounting is already in the lead doc (the box's disjunct). When boxes 3+4+5 all pass:
   Status: done (the driver re-checks every box + the suite).

**Re-read next session:** `fit/src_roman_maclauchlan.py` (--stage/--check/--golden NOT built
- main() rejects them with the docstring pointer; MACLAUCHLAN_FIGS + docstring current);
`tasks/808-horsley-stage.md` (in full - row-content conventions); `data/commons/files.jsonl`
(row shape); `data/catalog/extras.jsonl` (no-QID row shape, location_check field);
`fit/evidence.py` (check/check_commons/check_caption); `data/books/triage/
memoirwrittendu00maclgoog.B.jsonl` (n0093 map_box [100,405,830,880]); `docs/lead_roman.md`
(the Maclauchlan section written this session - keep it in sync if the staged row differs);
PITFALLS' new validate_book entry (the offline wrapper recipe).
