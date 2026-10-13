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
(2026-10-13, iteration 216, agent c - map transcription FINISHED: all 15 map titles + corner marks read
from the images (table below); staging design decided (files_roman.jsonl rows, evidence kind
caption_coords, verified offline by fit/evidence.py check); NO code changes this session - the module
on disk is still the iteration-212 version (HORSEY_PLATES=None, no map table, CITE = the IA-record
placeholder, --stage/--check/--golden raise "not built yet"). Next session = the module edit (step 3
of the 215 recipe). /tmp/horsley_full/ still holds every full-size image + all crops made in 215/216
(t*/b* = top/bottom 16% 2x; ro_*/up_* = rotated/portrait overviews; tt_*/tb_*/ov_* = title strips).
Last suite baseline: iteration 203 (1 failed / 155 passed / 1 skipped; the lone red = agent a's in-flight
307 placement test).

**ALL 15 MAPS (the complete transcription, read this session from the images):**
P.158 series = Hadrian's Wall, Book II. N.1-N.10 are ROTATED landscape sheets (portrait capture
text rotated 90deg; rotate CW to read; title box then sits at the bottom of the landscape map;
corner mark at the sheet's top-right). N.11 is an upright portrait SECTION drawing (no title box).
  n236  P.158 N.1   s  "A general map of the Roman walls in the north of England, and so much of the
                       adjacent countryes as includes the secondary stations per lineam valli."
                       [A's caption said "pertaining thereto" - the printed ending is the Latin
                       "per lineam valli"; A is close but not verbatim] scale "two miles"; J. Mande sc.
  n238  P.158 N.2   s  "A map of the Roman walls from SEGEDV[NAVM] to CONDERCV[VM]."
                       [eastern half of the wall: plans of SEGEDUNVM (Wallsend), PONSAELIVM (Newcastle),
                       CONDERCVVM ("now Benwell hill"); Tyne; HADRIAN'S VALLVM + SEVERVS'S WALL; scale
                       "two miles"]  (the ro_n0238 overview is fully legible)
  n240  P.158 N.3   s  "A map of the Roman wall, from CONDERCVVM to VINDOBALA." [plan of VINDOBALA
                       "now Rutchester", own scale 100 yards]
  n242  P.158 N.4   s  "A map of the Roman wall, from VINDOBALA to HANNAVVM." [plan of HANNAVVM
                       "now Halton Cheisters"]
  n244  P.158 N.5   s  "A map of the Roman wall, from HANNAVVM to CILVRNVA." [plan of CILVRNVA
                       "now West Chesters" (the fort plan; the modern town is Chesters)]
  n246  P.158 N.6   s  "A map of the Roman wall, from CILVRNVA to BORCOVACEVS." [plans of PROCO[LTIA]
                       ("now West Wall"? near Stanwix) and BORCOVACEVS "now Birdoswald"; Bowness; the
                       Solway end]
  n248  P.158 N.7   s  "A map of the Roman walls from BORCOVACEVS to MAGNA." [plan of MAGNA (Bowness-on-
                       Solway area); also VINDOLANA "now Vindolane cheisters" (= Vindolanda) and a plan of
                       A[ESICA] "now Birn Cheisters" (= Birnchester, Aesica)]
  n250  P.158 N.8   s  "A map of the Roman walls from MAGNA to PETRIANA." ["PART of CUMBERLAND" /
                       "PART of NORTHUMBERLAND" coast map; plans of AMBOLIANA and PETRIANA (Horsley's
                       hypothetical Solway-coast stations); Longhope, the Cark? etc.]
  n252  P.158 N.9   s  "A map of the Roman walls in the north of England, from PETRIANA to CONGAVATA."
                       [Petriana "now ...", UBILAVRA?, CONGAVATA "now Somersets" (Castlesteads), Ithen
                       (Irthing/Eamont) rivers]
  n254  P.158 N.10  s  "A map of the Roman walls in the north of England, from CONGAVATA to
                       TVNNOCELVVM." [CONGAVATA "now Somersets", AXELODVNVM "now Bright Monomeby", the
                       Solway Frith, ITVNAE AESTVARIVM, TVNNOCELIVM "now Bonholm" (near the Esk mouth),
                       "GA RBOS ENTVVM"? a coastal station, Longfowlis, Burghall]
  n256  P.158 N.11  o  UPRIGHT portrait SECTION of both walls between castella: labels Castellum,
                       "The south agger", "Severus's ditch/vallum", "Hadrian's north agger / ditch /
                       principal vallum / south agger", "A scale of 9 paces or 15 yards". NOT a site
                       plan (a cross-section) -> kind o, indexed but not staged.
P.176 series = the Antonine ("Severus's") wall, Scotland. N.1 is a ROTATED landscape sheet; N.2-N.5 are
UPRIGHT portrait sheets (title box at the sheet's bottom, read from the b* crops).
  n278  P.176 N.1   s  "A general map of Antoninus's wall in Scotland." [the whole wall: New Kilpatrick
                       ("Old Kilpatrick"?) to Falkirk; Barhill, Kinknittoch, Archindavay, Rough castle,
                       Camelon, Falkirk; Clyde and Forth; scale 10 miles; legend "An explanation of
                       the Figures"]
  n280  P.176 N.2   s  "A map of the Roman wall in Scotland from the west end to Bemulie." [New
                       Kilpatrick fort plan (cross inside the plan), the Clyde (Dunglass, Auchintorly,
                       Dunnerbuck, Free-land, Church), the wall east to Bemulie; scale 10 miles]
  n282  P.176 N.3   s  "A map of the Roman wall in Scotland from Bemulie to Crowy-hill." [the Peel of
                       Kirkintilloch (concentric square plans + compass), ANTONINVS'S W[ALL], Balmure/
                       Bemulie fort plan, Kelvin; scale 1 mile?]
  n284  P.176 N.4   s  "A map of the Roman wall in Scotland from Crowy-hill to Falkirk." [Crawy-hill
                       (Crowry), Mailling-house (Milton?), Dillater (Dilston), Rough hill (Rough
                       Castle), Falkirk fort plan, Westburn, Stinghouse]
  n286  P.176 N.5   s  "A map of the Roman wall in Scotland from Falkirk to the east end." [Falkirk,
                       Callender-house, Deadarse, the wall drawn down to the Forth at Cumbernauld
                       ("Cuffabout"?), "Old Park", "Church", Caer-ridden; scale "two English miles"]
  n287  verso (no corner mark; faint ink show-through of N.5) - NOT a list page
Versos with no mark (faint/empty frames, stage-A flags them plate_site_plan on the engraved border -
expected, not recall misses): n239, n243, n249, n253, n287.
Country maps (kind o, IN the list, NOT staged): n0060/n0062 the Ptolemy map (front matter), n0706
Mercator-Ptolemy (Book III), n0734 the Antonine Itinerary map, n0832 the Notitia, n0867 the Peutinger.

**STAGING DESIGN (decided this session):** one files_roman.jsonl row per map leaf that is kind s, tied
to the named fort(s) of its title: site = the catalog row where the fort has a QID (verified in
data/catalog/sites.jsonl this session: castrum-segedunum-q637958 = Segedunum/Wallsend; pons-aelius-
q7227963 = Pons Aelius/Newcastle; rudchester-roman-fort-associated-civil-s-q17669775 = Vindobala/
Rudchester; haltonchesters-roman-fort-settlement-and-q17648018 = Hannavam/Onnum (West Chesters);
aesica-q4688554 = Aesica (Great Chesters, for N.7's Aesica plan); birdoswald-roman-fort-and-the-
section-of-q17650767 = Borcovaceus/Birdoswald) or a new extras_roman.jsonl entry where not (Condercum,
Cilurni/Chesters, Procolitia, the Solway-coast hypotheticals Magna/Petriana/Congavata/Tunnocelum if
staged, and the Antonine forts: Old Kilpatrick (check extras.jsonl bar-hill-fort), Kirkintilloch,
Balmuildie, Rough Castle (check extras.jsonl rough-castle-fort), Falkirk-end). extras.jsonl holds the
no-QID row shape (id, qid null, name, lon, lat, region lowercase, kind "roman fort", source,
place, wikipedia, note) - extras_roman.jsonl rows follow it (parent hand-over: kind "roman fort" /
"roman site", QID where it exists, lon/lat from the book's list or a cross-check). Row shape:
site, qid, title (the plate's printed title + book/series), year 1732, url/thumb (the IA page), w/h,
desc (the book's printed list entry = the plate heading, the 200 evidence's "list entry"), evidence
= {rec evidence/1, kind caption_coords, checked, named_place (the fort as printed, e.g. "Vindobala"),
place_qid/place_label/place_lon/place_lat (the resolved coordinates), site_lon/site_lat (the catalog
row's), dist_m} - fit/evidence.py check_caption verifies this OFFLINE from stored fields only
(named place in norm(title+desc), stored distance reproduces within 1 km, <=50 km), so the check leg
needs no network even for new extra sites. classified_roman.jsonl: one row per staged map, "plan" by
hand. For each kind-s map with a single principal fort (N.3-N.6, N.8-N.10, P.176 N.2-N.5) one row to
that fort; N.1/N.2 and the multi-fort maps: tie to the most-named/planned fort and record the others
in desc (decide the exact row split when building --stage; at minimum every map leaf with a real fort
gets at least one row, and the 90% box counts verified site-plan leaves staged).

**EXACT NEXT STEP (iteration 217 = the module edit, recipe step 3):**
1. Edit fit/src_roman_horsley.py: (a) CITE -> the title-page text: "John Horsley, Britannia Romana, or
   the Roman Antiquities of Britain: in three books, printed for John Osborn and Thomas Longman, at the
   Ship in Pater-Noster Row, London, 1732 (M.DCC.XXXII); the Google scan is the British Museum volume
   (shelf mark RB DA 145. H 86 folio, May 25 1883, on leaf n0015)"; (b) add the MAP list as a module
   constant in books_lists HAND_FIGS format (read pipeline/books_lists.py first for the exact field
   spec - the 215 hand-over says fig|title|page|kind|kind_by, fig = the leaf's n, page = the printed
   "P.158"/"P.176" string or "", kind s/o, kind_by hand) covering the 15 maps above PLUS the 5 country
   maps as kind o; (c) extend register() to inject books_lists.HAND_FIGS[IA] in-process (keep
   HORSEY_PLATES=None until the inscription-plate transcription starts - the inscription list can
   trail: the 90% box concerns kind-s maps only); (d) update the module docstring (the no-list
   discovery: the book has NO printed plate list, the list = the plates' own printed headings, the
   books_lists docstring's "headings printed in its text" fallback; usage lines). Commit:
   "207a: map list transcribed from the plates' own headings (the book has no plate list) - CITE from
   the title page".
2. Then --list (books_lists.cmd_ocrmap) once -> lists/britanniaromanao00hors.json + .map.json; verify
   the map.json entries carry the right n's (236..256, 278..286 + the country maps). Note: --list is a
   live call (Qwen 8080/8081) but only over the mapped pages - should be minutes, not the 936-page pole.
3. Then --triage B (resumable background, nohup; the long-background-job PITFALLS: writer gone +
   mtime settled before commit): covers A's 80 site pages + the mapped leaves.
4. Then build the --stage/--check/--golden legs (staging design above; --check runs fit/evidence.py
   check over files_roman.jsonl + the join test: every row names an existing or staged site, every new
   extra has its plans) + tests/test_src_roman_horsley.py (no_network socket-blocking fixture as in
   tests/test_src_van_deventer.py) + tests/golden/src_roman_horsley_sample.json + the Horsley section
   of docs/lead_roman.md (validate_book recall; record that the list = the printed plate headings
   because the edition has no list, and that N.11 is a section drawing, kind o).
5. Later sessions: transcribe the ~121 inscription plates (Roman numerals I-CXXI, scattered through
   n0067-n0900) into HORSEY_PLATES in batches (kind o, each names the site where the stone was found);
   the 90%-of-site-plans box is already covered by the maps, so this can trail without blocking.

**Full-size images on disk this session: /tmp/horsley_full/** - n0047-n0070, n0236-n0287, n0706,
n0734, n0832, n0867 (2427x3893-class jpgs) + crops: t*/b* (top/bottom 16% 2x), ro_* (CW-rotated
overviews of the rotated sheets), up_* (portrait overviews of the upright Antonine sheets), ov_*
(quarter-scale overviews), tt_*/tb_* (top/bottom title strips), corner_*/ghost_*/c4_*/csheet*/m*/pv*.
If /tmp is gone: re-download via https://archive.org/download/britanniaromanao00hors/page/nNNNN.jpg
with a browser UA (the way 215 did). Re-reading any title: rotated sheets = rotate -90 (CW) then read
the bottom strip; upright sheets = the b* bottom 16% 2x crop.

### Also written to PROGRESS.md (moved here by the driver)

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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207a-horsley.md` (in-progress) - hand-over: (2026-10-13, iteration 212, agent c - the owner LIFTED the stop: request 006 (filed by iteration
- `tasks/207b-maclauchlan.md` (in-progress) - hand-over: (2026-10-13, iteration 204, agent c - NO work on this task. The driver auto-put it back to
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/212-cover-final.md` (split) - hand-over: (2026-10-13, iteration 234, agent a - **212a done, 212b done (lead), 212c done - the
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-13, iteration 208, agent c - the driver returned the parent: all existing subtasks
- `tasks/302f-matcher-station-test.md` (open) - hand-over: (2026-10-13, iteration 211, agent c - all code read and traced THIS session (fresh eyes, current
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/235-placement-test-dep-pick.md`
- `tasks/302g-stonehenge-matcher-run.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 207 DECISION: split into 207a (Horsley), 207b (Maclauchlan), 207c (Roy); reordered so the unblocked books go first
Chose per-book subtasks over one task: the three-book pipeline (fetch + triage A/F/C/B + list mapping + recall + staging + tests + lead doc) is far beyond a few sessions, and the task's own Notes anticipate the split. Reordered from the Notes' (Roy, Horsley, Maclauchlan) to (Horsley, Maclauchlan, Roy): the driver hands out subtasks in a/b/c order, and Roy (207c) is blocked waiting on a human-provided copy (BLOCKER below), so putting it last keeps the pipeline moving.
Copy choices (measured this session via books_ia): Horsley -> `britanniaromanao00hors` (Google Books, 936 leaves, median 2237x3861 px, hOCR + djvu.txt; alternates the bim British Museum copies, 831/827 leaves, ~14000 px images - only if the Google pages are unreadable). Maclauchlan -> `memoirwrittendu00maclgoog` (the 1858 original, 171 leaves, 3290x5182 px, djvu.txt only, no hOCR; the 1971 reprint `memoirwrittendur0000henr`, 292 leaves 1625x2697, has hOCR and is the OCR source for the book's list; stage images only from the 1858 original). Mechanics: each subtask's module registers its book in `books.BOOKS` and patches `books.LLM_URLS` in-process to the live replicas (127.0.0.1:8080-8082, model qwen3.8-27b, verified up this session) - no edits to pipeline/ (215 re-points books.py properly); per-book artifacts only (triage/<ia>.*, lists/<ia>.json/.map.json via `books_lists.cmd_ocrmap` after in-process `books_lists.PLATES[ia]` injection); recall recorded per book in docs/lead_roman.md via `books_lists.validate_book` (the shared validation.json/index.jsonl stay untouched until 211); staging appends to the parent's shared files (files_roman.jsonl etc.) with rows tagged per book, the 204/205 append-only idempotent pattern.

### 2026-10-11 207 BLOCKER: Roy 1793 "Military Antiquities of the Romans in North Britain" is not on the Internet Archive
- Attempt 1: IA advancedsearch by exact title, "romans in north britain", "antiquities of the romans in north britain", creator "Roy, William" (fuzzy: unrelated hits), title:"military antiquities" (20 hits: Grose et al., never Roy), a 1790-1800 year-range text query -> the only related item is a 1917 dissertation ABOUT Roy (macdonald-1917-roy, ~76 journal leaves, no facsimile, no plate list) - not the book
- Attempt 2: ten guessed identifier patterns (militaryantiquit00roy, ...u, ...0, ...w, ...goog, ...0000roy, ...0000royw, militaryantiquities00{,00}roy{,w}, militaryantiquiti00roy, militaryantiquit01roy) -> all return `{}`
- Attempt 3: the NLS complete facsimile (maps.nls.uk/roy/antiquities/, "174 pages, 51 map plates") via web_fetch and curl with three browser UAs, HTML and guessed image paths alike -> HTTP 405 AWS-WAF "Human Verification" captcha challenge on every path; the NLS open S3 tile bucket (mapseries-tilesets) lists fine but holds no antiquities set (roy/ = 1747-55 military survey only, already used by pipeline/nls.py as background maps)
Needed: a human with a real browser to download the NLS facsimile and place it in data/raw/books/roy1793/ (or a decision to drop Roy). Filed ask_human (request 003, open, human_only); 207c set to blocked. 207a/207b proceed independently: the subtasks run in sequence, so the shared staging files (files_roman.jsonl etc.) carry per-book tagged rows without conflict; each subtask's module, triage/lists artifacts and tests are disjoint.

### 2026-10-13 207a DECISION: first session - module fit/src_roman_horsley.py created (register/fetch/status/triage/list legs); all 936 triage pages fetched; next step is triage A in the background
- Module pattern: 209b's Stukeley (the book really is on IA: no local-copy wrap, the machinery runs unmodified; register() only adds the BOOKS entry, and - once HORSEY_PLATES is transcribed - injects it into books_lists.PLATES in-process). NO LLM_URLS patch: books.py's default LLM_PORTS is now "8080,8081,8082,18080,18081" (215 re-pointed it), and 8080/8081 answer (8082 down) - the parent's "patch books.LLM_URLS" mechanics note is stale on that point.
- Fetch measured: 936 pages in ~10 min at 2 workers (~4 s/page, IIIF 1400 px JPEG q88; median output 812x1400, every file 1300+ px long side, zero failures, one auto-retry after an SSL handshake timeout - books.get tries=2). No IIIF problem like Allcroft's NO_IIIF case.
- The hOCR pageindex has 942 pages against the bookreader's 936 leaves (6 extra) - the civitates-style misalignment: text looked up by hOCR index can land on the wrong leaf; the leaf images are the ground truth. The printed list of plates is hOCR-silent (i53-i68, between the preface ending i52/printed xxxii and the body starting i69) and must be transcribed by eye from the triage images (the Stukeley/213 hand-list pattern).
- Suite re-baseline this session (the parent's hand-over asked for it): 1 failed / 155 passed / 1 skipped (312 s); the lone red is agent a's in-flight 307 placement test, the same signature 306d recorded at 161/201.

### 2026-10-13 207a DECISION: iteration 203 - main merge: the owner's "Stop 207" (the lead's 62455ad block) reached this branch; the conflict resolved by keeping the block and the lead note verbatim; no further work started; waiting on request 006 (recommendation: the stop stands)
- Timeline (verified in git): the owner's stop reached the lead ~10-12 (the lead's 12:46 note "211 runs without 207 (stopped by the owner)" - 558ef46); the lead blocked 207a + 207b on main at 10-13 11:19 (62455ad: "the owner said 'Stop 207'. Do not start until the owner lifts it."). My branch's last main merge was 09:36 (055dea1), so iteration 202 (11:49-12:08, f6ef27d) ran in the gap before the block was visible here and completed the module + all 936 fetched pages - harmless finished work (public-domain scan into the shared gitignored raw store; nothing published or staged). The long LLM triage (~1 h of shared GPU) had not started and this session did not start it: the owner's word outranks the driver's dispatch.
- Resolution (keeping both sides' intent): Status: blocked + the lead note VERBATIM (the owner's word is the newest on record - no lift in any HUMAN commit, lead note or answered ask; GOAL.md's Roman point 4 is unchanged, so the stop reads as a pause, not a drop), then my hand-over (what is done + a verbatim resume recipe) after the note. The old hand-over was replaced whole, nothing lost. The driver's blocked-without-request flip (which handed out this task 30 min after the lead's block, causing the original overstart) is now countered by the open request: a blocked task waits while its request is open.
- Filed ask_human request 006 (blocking): does the stop still stand? (a) it stands = my recommendation (nothing is lost - everything is resumable, and the one LLM hour is not charged while waiting); (b) lifted = this task resumes at the hand-over's resume recipe step 1 (triage A in the background) and 207b unblocks to follow (the lead/owner's word, not for me to set - 207b is not on my Touches). The loop's 120-minute default answers (a) if the human does not respond; the task then stays parked on the lead note.
- The merge itself was bookkeeping-only (staged diff: DECISIONS, CODEMAP, PROGRESS, the archive, task files 207a/207b/221/306c/306e/306f/806 + new task 235): 207b now blocked on this branch (the lead's 62455ad), 221's final state (5187baf: done, box 3 re-worded), 235 (the placement-test seed fix, agent a's 307d lane) landed. No data/, fit/ or tests/ changes came from main, so no new red could come from the merge; the full suite post-merge = 1 failed / 155 passed / 1 skipped (317 s) - byte-for-byte the iteration-202 baseline (lone red = agent a's in-flight 307 placement test, signature unchanged: seed check + /tiles/relief 404).
- Also recorded as a PITFALLS entry (Agent tools and harness): a lead block on main can lag an agent branch; a session in the gap works on a "blocked" task in good faith - resolve such a merge by keeping the block + note, and file a blocking ask to stop the driver's re-flip.

### 2026-10-13 207a DECISION: iteration 212 - the owner lifted "Stop 207" (request 006 answered "b"); the lead-note block was removed from the task file; stage-A triage of all 936 pages completed and was committed (0 errors); A's captions found to be hallucinated on this book
- The driver's resume commits (84a7897 for 207a, plus d959afe/7457317 for 207b/207c) flipped only the Status lines; the lead's "## Lead note" ("Stop 207 ... Do not start until the owner lifts it", 62455ad) was still in the task file. Removed it: the owner's 006 answer (b = lifted, 10-13 14:35 console) is the newest word on record and outranks the lead's 10-13 11:19 block. Also corrected the task's Notes LLM-URLS bullet (stale since 215 re-pointed books.py's LLM_PORTS).
- Stage A ran 14:38-14:55 (17 min; 8080+8081 x 4 workers = 8 concurrent - the hand-over's "~1 h" estimate assumed a busier GPU): data/books/triage/britanniaromanao00hors.A.jsonl = 936/936 rows, 0 error rows; writer gone + mtime settled before commit (the long-background-job check; log /tmp/horsley_triageA.log). Page types: text_only 703 / other_illustration 151 / plate_site_plan 80 / unparsed 2 (n349, n391: markdown-fenced JSON the parser dropped; both look like plate/LIST pages, not plans - stage F over other_illustration is the fallback second pass if a verified plan page is ever missing).
- Finding (new PITFALLS entry): stage-A captions/numbers are NOT reliable on this book - Qwen's parametric memory leaked in (Squier & Davis titles: MOUND CITY OHIO, CHAMBERLAIN RIVER ILLINOIS, HERCULANEUM; "PLATE XXV" repeated verbatim on unrelated pages). The only plausible Horsley cluster: n236-n287, the Roman-wall maps (general map of the Roman walls in the north of England N.1-N.8, Antonine wall N.1-N.2, the wall-in-Scotland series). Hence the kind decisions and the 200 evidence must come from the printed plate list transcribed by eye from the triage images (n0047-n0070) plus the images themselves, never from A's text.
- Next session (recipe step 2, in the task's hand-over): transcribe the printed plate list into HORSEY_PLATES, commit the module, run --list (ocrmap, which also fills the list map from A); then --triage B (re-run after ocrmap for the mapping's extra pages); then build --stage/--check/--golden, the no-network test, and the stage-A/B recall section of docs/lead_roman.md.

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)
- Re-verified the 160 hand-over's numbers with fresh measurements BEFORE deleting (AGENTS.md: check facts by running code). Confirmed: 8 pairs = 4 distinct points on a 100-px grid ladder (three on u=100; the 200-px and 100-px lat steps span 0.0053896/0.0017967 deg = 1.5:1 per pixel, no similarity can hit; the page's simFit (exact port) gives resid 10.9-39 m, 2.634 m/px, +1.06 deg - identical to the committed shot's [eval] line). CORRECTIONS to the 160 hand-over: the real hillfort is ~20 m NW of the site point (not '+22 E / -55 N'), its hachured ring is ~80-90 m across (not ~130 m), so the drawn ring (277-342 m at 2.634 m/px, centred at raw (240-248,115) -> (-3.5187, 51.0370) = E -218..-239, N +531) is ~3.5x too big and 554-582 m N-NW (N23-25W) of the real one - on a small hachured wood hill. The 160 '~2x / 535-576 m' survives as a range (540-576 -> 554-582), the direction and the verdict are unchanged. Extra independent check: the plate's own 'SCALE OF FEET 0-300' bar measures ~1.45 m/px vs the fit's 2.634 (1.8x). Distances must be geographic (dx=dlon*111194.9266*cos(lat0), dy=dlat*110900), NOT raw Mercator units (my first pass computed 916 m for the 576 m distance that way).
- Executed the 303 way exactly as 306c did (fit/review.py API, no hand-edited JSON): upsert_item(root,'bury-castle-q5001077',[entry]) with entry = {plan, title, url, pairs (the doc's 8), coarse:false, evidence (from the data/commons/files.jsonl row: rec evidence/1, kind category, checked 2026-10-10, site_cat/file_cat 'Bury Castle, Somerset'), label '1911', cite, ref, size, place_reason '306d audit 2026-10-12: ... Document deleted.'} appended to the existing item (lead n0136_1 kept first, filename unchanged), then deleted data/db/platefits/bury-castle-q5001077.c_de779031cda8a0dc.json, then export(root,'bury-castle-q5001077') (333 open of 346). Only 3 files changed (D doc, M item, M web/data/review.json) - no other site's item touched; the site was already covered for the union check (its item was already open in the page file before the upsert).
- Wrote the 306d block (header + the bury-castle line) into docs/site_flow.md after the 306c block (header is tense-neutral: 17 more lines to come in batches; box 1 ticked - 36 shots re-listed this session).
- TESTS (full suite, main checkout, --ignore=tests/test_gate.py, -p no:cacheprovider, with my changes): 10 failed, 130 passed, 1 skipped (251 s). The 10: test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (FAILED at the seed check, dep:null) + 9 that are agent a's in-flight work already on main (test_merge new_sites_are_complete/new_site_golden_samples = 211's open 222-228 gate; src_artists/limes/mackenzie/numancia/wiltshire_stukeley stage+check tests = the 224 family). Baseline in my task file (123/1, 2026-10-12) is STALE - main has since merged 211/223/224/307 work and the suite grew to 141 tests.
- A/B attempt 1 (worktree at HEAD in /tmp/aw306d_ab): INVALID - web/data/sites/ is mostly gitignored (58 tracked files vs 389 site dirs in the main checkout; the per-site web data + data/raw are local build artifacts), so a fresh worktree lacks stonehenge etc. and fails 3 tests deterministically (site_done_line FileNotFoundError '/tmp/aw306d_ab/web/data/sites/stonehenge-q39671', fit_provenance line_refuses_unmarked_non_auto_doc, fit_queue save_runs) that pass in the main checkout; its placement_gestures 'vacuous ERROR' there is also unprovable (no local depictions). PITFALLS candidate: never A/B this project in a bare worktree/checkout - do it in the main checkout with the changed files temporarily at HEAD. (The worktree is still registered; remove it: git worktree remove --force /tmp/aw306d_ab && git worktree prune.)

### 2026-10-13 207a (agent c, iteration 215)
- The 1732 Britannia Romana (britanniaromanao00hors) has NO printed list of plates - verified on both the Google copy (942 hOCR pages, no LIST heading; book ends with a GENERAL INDEX) and the BM copy bim_eighteenth-century_britannia-romana-or-the_horsley-john_1732 (831 leaves, hOCR fetched+cached; only incidental "list" prose). The books_lists list for this book is therefore a hand transcription from each plate's own printed heading (the docstring's "headings printed in its text" fallback; the 213/civitates hand-list pattern). CITE finalized from the title page (n0014: printed for John Osborn and Thomas Longman, M.DCC.XXXII). Wall-map corner marks read: P.158 N.1-N.10 (leaves n236-n254, Hadrian's-wall series) and P.176 N.1-N.3 (n278/n280/n282, Antonine series; n284/n286/n287 + n256 pending). Plan: inscription plates -> books_lists.PLATES[IA] (Roman numerals I-CXXI), wall maps -> a HAND_FIGS-style per-leaf table (fig = leaf n) injected in-process; both via register(). Next: finish map titles, commit the module, --list, --triage B, then --stage/--check/--golden + test + lead-doc. Full detail: DECISIONS.md entry + the 207a task hand-over.
... (1.9 KB more: `grep -n -A 200 -F '## 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)' DECISIONS.md`)
