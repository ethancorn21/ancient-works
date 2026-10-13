Status: in-progress
# 207a: Horsley, Britannia Romana (1732)
Depends on: 200
Touches: fit/src_roman_horsley.py, data/books/triage/, data/books/lists/, data/catalog/extras_roman.jsonl, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, docs/lead_roman.md, tests/test_src_roman_horsley.py, tests/golden/src_roman_horsley_sample.json

## Goal
Subtask of 207 (the parent's Hand-over has the full mechanics): index John Horsley's
*Britannia Romana* (1732) with the existing book machinery and stage its site-plan rows tied
to Roman sites. Chosen IA copy: `britanniaromanao00hors` (Google Books scan, 936 leaves,
median 2237x3861 px, hOCR page text + djvu.txt present). Alternatives (only if specific pages
of the Google copy are unreadable): `bim_eighteenth-century_britannia-romana-or-the_horsley-john_1732`
(British Museum, 831 leaves, median 7984x13809 px) and the `..._0` copy (827 leaves,
8328x14257 px) - much larger images.
Note: this book's ~121 engraved plates are mostly Roman inscriptions and sculptures (list
kind "o"); its true site plans are the few maps (kind "s"). Stage the site plans; the
inscription plates are indexed in the list mapping (each names the site where the stone was
found) but are not staged as picture rows.

## Acceptance criteria
- [ ] The book is fetched from the Internet Archive (data/raw/books/britanniaromanao00hors/)
      and triaged with the existing machinery, per-book artifacts only
      (triage/britanniaromanao00hors.*.jsonl, lists/britanniaromanao00hors.json,
      lists/britanniaromanao00hors.map.json); the shared data/books/index.jsonl and
      validation.json are NOT written by this subtask.
- [ ] The book's own printed list of plates is transcribed (the books_lists PLATES pattern)
      and mapped to leaves; the stage-A/B recall against that list is recorded in the
      Horsley section of docs/lead_roman.md (instead of the shared validation.json).
- [ ] Staged rows (appended to the parent's shared staging files, rows tagged with this
      book): files_roman.jsonl for every verified site-plan page tied to a Roman site - an
      existing catalog site by QID where one exists, or a new extras_roman.jsonl entry
      (kind "roman fort" / "roman site", QID where it exists, lon/lat from the book's list
      or a cross-check) - each with the 200 evidence field (the book's printed list names
      the place; the specific check - list entry, caption, coordinates distance - recorded
      on the row) and a classified row by hand ("plan"); the book's date (1732) is recorded
      on the row.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages are staged, or each missing one is accounted for in docs/lead_roman.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site;
      every new site has its plans) and the evidence check passes; a golden sample of rows.

## Notes
- The LLM replicas serve on 127.0.0.1:8080-8082 (model qwen3.8-27b); since 215 re-pointed
  pipeline/books.py's LLM_PORTS to 8080,8081,8082,18080,18081, no in-process LLM_URLS patch is
  needed (verified 10-13: 8080/8081 answer, 8082 down). This subtask's module registers the
  book in books.BOOKS in-process only; it does not edit pipeline/ (the parent's Hand-over has
  the full recipe).
- The catalog already holds the major British Roman forts with QIDs (305 roman_fort rows:
  206 England, 54 Wales, 22 Netherlands, 17 France, plus 6 no-QID extras: vindolanda and the
  four Antonine Wall camps, aventicum). Tie Horsley's maps to those where the site matches;
  stage a new site only for a place not already in the catalog.
- The LLM triage of 936 pages is the long pole: run it as a resumable background job (the
  stage jsonl is append-only and skips done pages; see the "long background data jobs"
  PITFALLS entry).

## Hand-over
(2026-10-13, iteration 215, agent c - recipe step 2 ran as an investigation and CHANGED the
approach: the book has NO printed list of plates (verified on BOTH copies), so the list is
transcribed by eye from the plates' own printed headings (the books_lists "plate headings
printed in its text" case). CITE is finalized from the title page (n0014). The wall-map
corner marks (P.158 N.1-10 / P.176 N.1-5) are mostly read (see below). NO code changes this
session (the module edit is pending, in-flight at the context limit - git has the working tree
only if anything was saved; the module on disk is still the iteration-212 version: all legs
work, HORSEY_PLATES=None, --stage/--check/--golden raise "not built yet"). Suite not re-run
(last baseline: iteration 203's 1 failed / 155 passed / 1 skipped; the lone red = agent a's
in-flight 307 placement test).)

**1. --status sanity (passed):** 936 leaves, triage 936/936, stage A 936 rows / 0 errors;
LLM 8080+8081 answer (8082 down). A rows carry BOTH n (bookreader index, 0-based) and leaf
(= n+1, delta always 1): triage files n0000-n0935 = the n index, so the title page is
n0014.jpg. (My 212 note "i63's OCR garbage" = hOCR i63 = leaf n0062 = the Ptolemy map's hOCR
fragment, not a list page.)

**2. CITE finalized (title page n0014, read at triage size, fully legible):** "BRITANNIA
ROMANA: OR THE Roman Antiquities OF BRITAIN: In THREE BOOKS. ... By JOHN HORSLEY, M.A. and
F.R.S. ... LONDON: Printed for JOHN OSBORN and THOMAS LONGMAN, at the Ship in Pater-Noster
Row. M.DCC.XXXII." Set the module's CITE to this (year 1732 already set). The verso n0015
carries the British Museum shelf mark "RB DA 145. H 86 folio / May 25 1883" (the Google copy
is a BM volume).

**3. FRONT MATTER MAP (Google copy leaf n = the ground truth):** n0012 half-title; n0014
title; n0015 verso; n0016 engraved vignette + DEDICATION to Sir Richard Ellys, Bart.;
n0017-18 dedication end (signed "Morpeth, Jan. 2, 1732 1/2 ... John Horsley"); n0019 blank
ghost; n0020-0051 = THE PREFACE, 32 printed pages i-xxxii (hOCR i21-52, offset 1 here);
n0052 blank; n0053 FAINT (preface's final paragraph + start of an "EPISTLE" section);
n0054-0059 + n0061 = BLANK leaves (no ink even at full size - verified: full-size jpgs are
170-218KB = blank-paper size, vs ~850KB for faint text pages); n0060 = the Ptolemy map in a
faded landscape capture ("A CORRECTED MAP OF BRITAIN ACCORDING TO PTOLEMY"); n0062 = the
same map as a full spread ("A Corrected MAP of BRITAIN according to Ptolemy's, or
Rectified"); n0063-65 plate_site_plan (empty captions); n0066 = the big "BRITANNIA ROMANA"
plate (612KB - probably the engraved Book-I title); n0067+ = Book I text. The book ENDS
with a GENERAL INDEX (hOCR i920-924), then blanks.

**4. THE LIST IS NOT IN THE BOOK (the pivot).** Searched every hOCR page of BOTH copies:
Google (942 pages) has no LIST/PLATES heading at all; the BM copy (bim_eighteenth-century_
britannia-romana-or-the_horsley-john_1732, 831 leaves, HAS hOCR - download + page_texts
cached under data/raw/books/) has i0 half-title, i2-4 dedication, i6-37 preface, i38-41 the
Ptolemy map (3 hOCR pages of one fold-out), i43 the engraved "BRITANNIA ... BOOK THE FIRST"
title, i44+ text - and its only "list" hits are incidental prose (i124/i138/i732). So the
books_lists ground truth for this book = the plate headings printed ON the plates (its
docstring's own fallback: "or, where the book has none, the plate headings printed in its
text"); the parent's acceptance-box wording "the book's own printed list of plates" is
satisfied by those printed headings (each plate prints its title box + number). The 213/
civitates hand-list pattern is the model: civitates used HAND_FIGS (fig = the leaf's n).

**5. PLATE NUMBERING (read from the images):** inscription/sculpture plates = Roman
numerals I-CXXI (the preface cites them as "N. xiix", "N. LxIII"). The Book-II wall maps
use ARABIC series numbers in a corner mark: "P.158 N.k" (k = 1..10, the Hadrian's-wall
series; P.158 = the book's page where the series is introduced, same for all ten) and
"P.176 N.k" (the Scottish/Antonine series). Corner marks read THIS session:
n236 = P.158 N.1 (the general map: title box "A general map of the Roman walls in the north
of England, and so much of the adjacent countries as includes the auxiliary stations
pertaining to the wall", scale "one mile = 3.82 inches", "J. Mande sc."); n238 = N.2;
n240 = N.3; n242 = N.4; n244 = N.5; n246 = N.6; n248 = N.7; n250 = N.8; n252 = N.9;
n254 = N.10; n278 = P.176 N.1 (the general Antonine map); n280 = P.176 N.2; n282 = P.176
N.3. NOT yet read: n284, n286, n287 (expect P.176 N.4, N.5 + a blank verso) and n256's
corner (n256 = a wall detail drawing, "The south agger" section visible in its corner crop;
A: "A drawing of part of the walls from one castellum to another between Towter..." -
probably kind o = a section, not a site plan). The BLANK/ghost frames (no corner mark, faint
or empty): n239, n243, n249, n253 (versos between the P.158 maps) and n287 (?). Note
stage-A flagged those versos as plate_site_plan with empty captions - expect it: they carry
only the map's engraved border frame. A's captions on the N-numbered maps are the
reliable ones (the "from SEGEDVNVM to CONDERCVS" series); its other captions in n234-287
are Squier & Davis hallucinations (n234 Ohio, n241 Crook, n245 Delaware, n247 CHILKIN,
n251 CUMBERLAND, n255 Cumberland river, n257 Mound City, n279 Wabash, n281 Scotts Run,
n283 Little Rhine, n285 Cwmystwyth hillfort).

**6. HOW TO FEED THE MACHINERY (no pipeline/ edits - in-process injection from the module):**
- Inscription plates -> books_lists.PLATES[IA] string (format plate|sub|title|page|kind;
  plate = the Roman numeral as printed; page = the printed page number; kind mostly o).
  map_plates() then tracks them by numeral (Qwen 'numbers' + ocr_numerals + caption
  similarity + monotone chain) exactly as for civitates/Squier.
- The wall maps (Arabic N numbers, NO roman numeral) -> a HAND_FIGS-style per-leaf table
  injected as books_lists.HAND_FIGS[IA] (format fig|title|page|kind|kind_by; fig = the
  leaf's n; page = the printed "P.158" string or ''; kind s for the wall maps, o for the
  Ptolemy/Itinerary/Notitia/Peutinger country maps; kind_by hand). list_pages() maps
  HAND_FIGS entries by their own n and includes kind s AND o for HAND_FIGS books;
  validate_book() counts their fig-n as gt pages. register() currently injects only
  PLATES - extend it to inject HAND_FIGS too (the module owns both strings).
- register() must inject BOTH before cmd_ocrmap/cmd_validate; --list currently calls
  cmd_ocrmap after register() - that stays, and validate_book (for the lead-doc recall)
  needs the same injection.

**EXACT NEXT STEP (iteration 216, step = finish the map transcription + first commit of the
module):**
1. Read corner crops of n284/n286/n287 (full-size files are in /tmp/horsley_full/n02xx.jpg -
   /tmp is wiped between loop restarts only on disk pressure; if gone, re-download via the
   books_ia page-URL pattern https://archive.org/download/britanniaromanao00hors/page/nNNNN.jpg
   with UA, the way iteration 215 did) to close P.176 N.4-N.5 and settle n287 (map or
   verso). Also n256's title box (bottom-left of the sheet - the maps are rotated landscape
   in portrait sheets: title box on the sheet's BOTTOM edge, corner mark on the TOP edge).
2. Read each map's TITLE BOX (bottom ~16% crop, rotated 90 deg) for the exact printed titles
   of N.1-N.10 / P.176 N.1-5; the A captions already give most ("from SEGEDVNVM to
   CONDERCVS" etc.) - verify, don't trust blindly; also note each map's scale bar text.
3. Edit fit/src_roman_horsley.py: CITE -> the title-page text (point 2 above); add the map
   table as the module's map-list string + extend register() to inject books_lists.HAND_FIGS[IA]
   (leave HORSEY_PLATES=None until the inscription-plate transcription starts); update the
   module docstring (the list-mechanics paragraph + usage) to record the no-list discovery
   and the two-table design; commit "207a: map list transcribed from the plates' own headings
   (the book has no plate list) - CITE from the title page".
4. Then --list (cmd_ocrmap) once -> lists/britanniaromanao00hors.json (+.map.json should list
   the map leaves); check the map.json entries carry the right n's.
5. Then --triage B (resumable, 8080/8081): it covers A's 80 site pages + the map leaves;
   run in the background (nohup, the long-background-job PITFALLS: writer gone + mtime
   settled before commit).
6. Then the --stage/--check/--golden legs + the no-network test + the Horsley section of
   docs/lead_roman.md with the validate_book recall (record that the list is the printed
   plate headings because the edition has no list; kind-o country maps - Ptolemy n0060/n0062,
   Book III's Mercator-Ptolemy n0706, Antonine-Itinerary n0734, Notitia n0832, Peutinger
   n0867 - are in the list but NOT staged as site rows).
7. Later sessions: transcribe the ~121 inscription plates (Roman numerals, from each plate's
   heading; scattered through n0067-n0900) into HORSEY_PLATES in batches - the 90%-of-site-
   plans box concerns only the kind-s maps, so the inscription list can trail without
   blocking staging.

**Full-size images fetched this session (for the transcription): /tmp/horsley_full/n0047-
n0070 + n0236-n0287 (2427x3893-class jpgs) and derived crops (t*/b* = top/bottom 16% 2x,
c4_* = corner contact sheets, ghost_* = contrast-enhanced blanks, corner_* = single
corner 2x). If /tmp is gone, re-download the same range with the page-URL pattern above.
