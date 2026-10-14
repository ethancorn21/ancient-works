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
- [ ] The book is fetched from the Internet Archive (data/raw/books/memoirwrittendu00maclgoog/)
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
(2026-10-13, iteration 122, agent c - investigation session; the 204 hand-over's "waiting
on the lift" text is OBSOLETE: the stop is lifted (asks 006/007 both answered "b", 10-13
14:35 console). No code changed this session, no tests run (suite last green 158
passed/1 skipped on the merged tree, 7e9c829; this task's files untouched). The session
established that the previous plan's list-source premise is WRONG and changed the plan -
see Findings below.)

**State (verified on this branch this session).**
- `fit/src_roman_maclauchlan.py` EXISTS (240 lines; built after the 204 hand-over went
  stale): register/fetch/status/triage/djvu/list legs done; `MACLAUCHLAN_PLATES = None`
  (list not transcribed); --stage/--check/--golden "not built yet". Its docstring still
  claims the list comes from the 1971 reprint's hOCR - that premise is now known to be
  WRONG (Finding 1); the module needs the pivot to the HAND_FIGS pattern.
- 1858 original `memoirwrittendu00maclgoog`: ALL 171 triage pages fetched (gitignored raw
  store); stage A done: 171 rows / 0 errors in
  `data/books/triage/memoirwrittendu00maclgoog.A.jsonl` (row: {n, leaf, out:{page_type,
  numbers, caption}, parse, s, img_size}; n = 0-based triage-file index = bookreader flat
  index; leaf = leafNum = n+1). Non-text flags: n78 plate_site_plan "BRAMPTO"; n90
  other_illustration (Willow Holm caption); n93 plate_site_plan "FIG. 4 / Sandridge & Co.
  Litho London"; n111 figure_site_plan (Housesteads gateway 1856); n129
  other_illustration ("MARKS ON ROMAN TILES, BINCHESTER"). No stage F/B yet; no
  `data/books/lists/memoirwrittendu00maclgoog.*`; NO roman staging files exist yet
  (files_roman/classified_roman/extras_roman all absent); docs/lead_roman.md exists but
  holds only the dropped-Roy section (no Maclauchlan section yet).
- LLM replicas: 8080 and 8081 answer, 8082 down (checked this session).

**Findings (all verified this session; they change the plan).**
1. **`memoirwrittendur0000henr` (the "1971 reprint") is NOT Maclauchlan.** Its IA record
   title claims Maclauchlan's Watling Street survey (1971), but the actual scan content
   (hOCR leaves AND the cached djvu.txt) is Linda Nochlin's *Realism* (1971 Pelican).
   The item was re-scanned 2024-01-31 (RePublisher log) - contaminated/mislabeled.
   UNUSABLE; the reprint-based list-OCR strategy of the 204 hand-over is dead.
2. **The 1858 original has NO printed list of plates.** Full djvu.xml digest of all 171
   leaves: Google notice (leaf 1), blank leaves, title page (~leaf 10-12, Bradbury &
   Evans, Whitefriars), preface, two memoirs (Roman Wall n~14-119; Watling Street
   n~120-165), TABLE OF STATIONS (n116), INDEX OF NAMES OF PLACES (n117-119), trailing
   blanks (n166-171). No LIST/PLATES heading anywhere. So per books_lists' own fallback
   (the 207a/Horsley precedent, accepted that way): **list = the plates' own printed
   headings, transcribed by eye, as a `books_lists.HAND_FIGS[IA]` table**
   (`fig|title|page|kind|kind_by`, copy the `HORSEY_FIGS` shape from
   fit/src_roman_horsley.py) - NOT `books_lists.PLATES`. Task box 2's wording ("printed
   list / PLATES pattern") is satisfied in intent this way (same as 207a); note the
   deviation in the lead doc.
3. **Exactly FIVE small-format plate leaves exist** (bookreader.json: all other leaves
   3290-3294x5178-5190; these five are 985x1431): **n0078, n0090, n0093, n0111, n0115**
   (0-based triage indices). Front-matter blanks (n0001-0003, 0005-0006, 0008) and the
   trailing n0165-n0170 are full-size blanks; n0004 = a handwritten collection slip
   ("Roman Wall... Watling Street... Maclauchlan", "9188"), n0007 = a handwritten
   presentation page ("Presented to Wesleyan College by the Duke of Northumberland... 19th
   July 1859") - neither is a plate. n0128 = the Watling Street memoir's display title
   page (full-size, not a plate). So the complete plate set of the book is those five
   leaves; the only other illustration is n129's inline "marks on Roman tiles,
   Binchester" (full-size page, needs an eye check).
4. **Plate inventory by eye so far** (contact sheet of all candidates built this session
   at /tmp/macl_candidates.png, plus direct full reads):
   - **n0090 (leaf 91) READ IN FULL = the Willow Holm plate**: caption "Plan, Section,
     and Elevation of the Roman Wall, in Willow Holm, Carlisle, on the line of outlet
     Sewer, 440 Yards from the West mouth of the Sewer. Reduced from M'Me Kie's Section,
     taken Sep't 7th 1858." - an ELEVATION + transverse SECTION of the WALL (labels A-F,
     "Scale, 4 Feet to an Inch", "H. M. L. delin. / Sandridge & Co. Litho. London").
     **A wall section, NOT a named-fort plan -> kind o, NOT staged** (parent Notes: wall
     sections are not sites; it depicts the wall at a place, not a fort structure).
   - **n0078 (leaf 79) = the BRAMPTON plan** (rectangular fort plan, "BRAMPTON" label +
     scale bar; between printed pages 64 and 65; the book's next heading is "BRAMPTON. -
     DOUBTFUL POSITION OF ABALLAVA") - **kind s candidate** (a named place with a
     location: Brampton, doubtful site of Aballava).
   - **n0093 (leaf 94) = the FIG. 4 lithograph** (stage A saw two figures: a small plan
     upper-left, a larger drawing lower-right; "FIG. 4" + "Sandridge & Co. Litho
     London") - **kind s candidate; caption NOT yet transcribed by eye** (read it next
     session).
   - **n0111 (leaf 112) = the GATEWAY plate**: "GATEWAY RECENTLY DISCOVERED NEAR
     HOUSESTEADS (Borcovicus) in 1856, represented on Trajan's Column..." + Horsley /
     Archaeologia refs - **kind s candidate** (a named structure: the gateway at
     Housesteads = Borcovicus, an existing catalog site) - verify by eye next session.
   - **n0115 (leaf 116) = the TABLE OF STATIONS** (small landscape table) - kind o,
     never staged.
   - **djvu.xml leaf text DRIFTS ~1 from the bookreader/physical sequence in the Willow
     Holm region**: the caption's OCR sits at djvu leaf 90 and the page-75 STANWIX text
     at leaf 91, while the actual plate is on the neighbouring bookreader leaf (n0089
     read nearly blank; n0090 = the Willow Holm plate). The civitates hOCR-drift pitfall,
     in its djvu-variant form. **Consequence: for this book, trust the IMAGES (and
     bookreader leafNum) for plate identity, not djvu.xml per-leaf text; cross-check
     image-to-image.** The Brampton region is unaffected (both leaves there OCR-blank).
5. **Only other Maclauchlan on IA: `henrymaclauchlan0000macl`** (2015 Wanney Books,
   "Henry MacLauchlan's Dere Street: a new presentation of his 1851 'Memoir ... Watling
   Street'"; hOCR + djvu present, but LCP/ACS lending-restricted - images probably not
   downloadable). Optional secondary cross-check for the Watling Street memoir only; NOT
   for the Roman Wall part; don't block on it.
6. **Stage A under-calling is ~0 among the plate leaves** (it flagged 4 of the 5 small
   leaves + the one full-size inline illustration), and the size census shows no hidden
   full-size plates - **stage F is probably not needed**; stage B still runs on the
   kind-s leaves.

**Exact next steps (in order).**
1. Read the full triage images of n0078, n0093, n0111 (and n0129, n0115 for the record)
   and transcribe each plate's printed caption/heading verbatim (the five small leaves
   are 985x1431 native, so triage size is near full-res; if a caption is still
   unreadable, fetch via `books.iiif_url(page, k)`).
2. Fix each plate's kind: s = named fort/structure plan to stage (n0078, n0093, n0111
   expected; n0090 = o wall section; n0115 = o table; n129 = o inline, unless its image
   shows a real plan of a named place).
3. Rewrite the module's list leg to the HAND_FIGS pattern: `MACLAUCHLAN_FIGS` string
   (the 5 small leaves + n129 if it qualifies), register() injects
   `books_lists.HAND_FIGS[IA]` (drop the PLATES injection and the djvu page_texts swap -
   first confirm in `books_lists.cmd_ocrmap` that HAND_FIGS books map by leaf n with no
   OCR; the Horsley module relies on that branch); update the module docstring (Finding
   1: the reprint is Nochlin's Realism; Finding 2: no printed list; Finding 4: the djvu
   drift).
4. `--list` -> `data/books/lists/memoirwrittendu00maclgoog.json` + `.map.json` (commit
   both); then `books.cmd_triage_b([KEY])` (8080/8081 up) on A's site pages + the kind-s
   leaves; then `books_lists.validate_book(KEY)` recall -> a NEW "## Maclauchlan" section
   in docs/lead_roman.md (never the shared validation.json / index.jsonl - 211 owns
   those).
5. Stage the kind-s rows (n0078, n0093, n0111) into files_roman.jsonl +
   classified_roman.jsonl ("plan" by hand) + extras_roman.jsonl only for sites not in the
   catalog (Brampton/Aballava: check data/catalog/sites.jsonl + extras.jsonl first - the
   206 England roman_fort rows and the 6 no-QID extras per the parent hand-over;
   Housesteads/Borcovicus = existing QID row; n0093 depends on its caption). 200
   evidence field per row (the plate's printed caption is the tie: list entry / caption
   / coordinates distance + checked date); book date 1858 on the row (title page; the
   survey ran 1857-59 - record the discrepancy in the lead doc). Append-only, idempotent
   (204/205 pattern); rows tagged with this book's key. 207a's 807-809 tasks will add
   Horsley rows to the same shared files - keep appending only, never rewrite existing
   lines.
6. `--check` (offline join + fit/evidence.py over this book's rows) + `--golden` +
   `tests/test_src_roman_maclauchlan.py` (no_network fixture as in
   tests/test_src_van_deventer.py; join + evidence check + golden sample
   tests/golden/src_roman_maclauchlan_sample.json). The 90% box: 3 kind-s plans staged of
   3 staged-eligible plates (n0090 wall section + n0115 table + n129 inline = the
   accounted-for rest, each named in the lead doc) = 100%.

**Re-read next session:** `pipeline/books_lists.py:cmd_ocrmap` - confirm the HAND_FIGS
branch maps by leaf n without any OCR/page_texts (the Horsley module relies on it);
`fit/src_roman_horsley.py` - the exact pattern to copy (register/list_cmd shapes);
`data/catalog/sites.jsonl` + `data/catalog/extras.jsonl` - look up the Borcovicus /
Housesteads QID row and check whether an Aballava/Brampton entry already exists before
creating an extras row.

**PITFALLS to add** (once the steps settle): (a) `memoirwrittendur0000henr` = Linda
Nochlin's *Realism* (1971), NOT the 1971 Maclauchlan facsimile - IA item title/content
mismatch; never use it. (b) Maclauchlan 1858 original: no printed plate list; exactly
five small-format (985x1431) plate leaves n0078/n0090/n0093/n0111/n0115; its djvu.xml
per-leaf text drifts ~1 from bookreader leafNum in the Willow Holm region (leaf 90/91) -
key per-leaf lookups on the images, not the djvu text.

**State (verified on this branch this session; a true blank slate, nothing to unwind).**
- No `fit/src_roman_maclauchlan.py`; no `data/books/triage/memoirwrittendu00maclgoog.*`,
  no `data/books/lists/memoirwrittendu00maclgoog.*`;
  `data/commons/files_roman.jsonl`, `classified_roman.jsonl` and
  `data/catalog/extras_roman.jsonl` do not exist yet; `docs/lead_roman.md` does not exist.
- `data/raw/books/` holds only cached `bookreader.json` + `metadata.json` for BOTH IA copies:
  `memoirwrittendu00maclgoog` (1858 original, 171 leaves, djvu.txt only, no hOCR) and
  `memoirwrittendur0000henr` (1971 reprint, 292 leaves, hOCR present). No triage images
  fetched for either; no LLM minutes spent.
- Waiting on: request 007 (this task) and 006 (207a), both open, both recommend (a) the stop
  stands; the loop's 120-minute default answers (a) if the human never replies, and the task
  stays parked on the lead note.

**Resume recipe (start ONLY after the owner's lift - a 007/006 answer of "lifted", or the
lead unblocking on main with the owner's word; read the parent 207 Hand-over's "Mechanics for
every subtask" first; its numbers/IA choices are current).**
1. Confirm the lift, then delete/rewrite this hand-over's waiting text.
2. `fit/src_roman_maclauchlan.py`: register the book in `books.BOOKS` in-process (ia=
   memoirwrittendu00maclgoog, region england, year = the title-page year, cite/why). No
   in-process `books.LLM_URLS` patch needed since 215 (207a session, 10-13: replicas
   8080/8081 up, 8082 down).
3. Fetch: `books.cmd_fetch([key])` -> `data/raw/books/memoirwrittendu00maclgoog/triage/`
   (171 pages, IIIF 1400px, append-only/resumable; long background job, see the PITFALLS
   "long background data jobs" entry).
4. Printed plate list: transcribe from the 1971 reprint's hOCR (memoirwrittendur0000henr),
   cross-check against the 1858 original's list-page images; inject `books_lists.PLATES[ia]`
   in-process; `books_lists.cmd_ocrmap([key])` -> `lists/*.json` + `.map.json` (per-book,
   committed); `books_lists.validate_book(key)` recall recorded in the Maclauchlan section of
   `docs/lead_roman.md` - do NOT write the shared validation.json / index.jsonl (211/230
   own the shared rebuild and the Roman re-run).
5. Triage A/B on the 1858 original; stage ONLY site-plan pages of a named fort/structure
   with a location (wall sections alone are NOT sites, per the parent Notes); stage images
   from the 1858 original only. Rows -> `files_roman.jsonl` (200 evidence field: list entry
   / caption / distance specifics, checked date) + `classified_roman.jsonl` ("plan" by
   hand), book date on the row; new sites -> `extras_roman.jsonl` (kind "roman fort",
   QID where it exists - most wall forts already carry QIDs in the 206 England roman_fort
   rows: hardknott, concangis, glannoventa, whitley-castle, milecastles; vindolanda is the
   known QID-less extra - lon/lat from the book's list or a cross-check).
6. `tests/test_src_roman_maclauchlan.py` (no network; the no_network socket-blocking
   fixture as in test_src_van_deventer.py; offline join of staged rows + fit/evidence.py
   check + golden sample `tests/golden/src_roman_maclauchlan_sample.json`).
7. Date note: the survey ran 1857-59 and the volume published 1858 - record the title-page
   year on the rows and note the discrepancy in `docs/lead_roman.md`.
