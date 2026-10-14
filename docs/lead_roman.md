# Roman books: Horsley (1732), Maclauchlan (1857-58), Roy (1793) - old site plans of Roman forts and camps (task 207; the Roman-sites lead of GOAL.md's "the map grows" list)

GOAL: every picture tied to its place with machine-checkable evidence. This lead indexes three
books with the book machinery (pipeline/books.py: fetch, triage A/B, list mapping, validate) -
one book per subtask (207a Horsley, 207b Maclauchlan, 207c Roy) - and stages their site-plan
pages tied to Roman sites (an existing catalog site by QID where one exists, or a new extras
row). One section per book below, in subtask order; a section appears when its subtask starts
work and stays where it lands. Each book keeps its own per-book artifacts only
(`data/books/triage/<ia>.*.jsonl`, `data/books/lists/<ia>.json` + `.map.json`) and appends to
the lead's shared staging files (`data/commons/files_roman.jsonl` + `classified_roman.jsonl`,
rows tagged with the book; new sites in `data/catalog/extras_roman.jsonl`): the shared
`data/books/index.jsonl` and `validation.json` are never written by this lead - 211 rebuilds
the shared index from the per-book files once. The stage-A/B recall against each book's own
printed list of plates is recorded in that book's section, in place of the shared
validation.json.

## Horsley, Britannia Romana (1732) - 207a (list corrected 807)

**Source (207, verified 2026-10-13):** the Internet Archive's Google Books scan
britanniaromanao00hors - 936 leaves, BookReader page images + hOCR text (long
side 2576-4116 px) - the book really is on IA, so the standard book machinery
runs unmodified (no local-copy wrap). The scan IS the British Museum volume:
shelf mark 'RB DA 145. H 86 folio, May 25 1883' on leaf n0015 (the title page's
verso); CITE from the title page n0014: 'BRITANNIA ROMANA: OR THE Roman
Antiquities OF BRITAIN: In THREE BOOKS. By JOHN HORSLEY, M.A. and F.R.S.
LONDON: Printed for JOHN OSBORN and THOMAS LONGMAN, at the Ship in Pater-Noster
Row. M.DCC.XXXII.' The British Museum copies
(bim_eighteenth-century_britannia-romana-or-the_horsley-john_1732, 831 leaves;
the _0 copy, 827) stay the alternates only.

**The no-list discovery (215, 2026-10-13; verified on both the Google and the
BM copies):** the book has NO printed list of plates - the earlier premise (a
front-matter list at hOCR i53-i68) was wrong: that span is the preface's end,
blank leaves and the Ptolemy fold-outs; the Google hOCR's 942 pages hold no
LIST/PLATES heading, and the BM copy's 831 leaves were searched one by one. Per
books_lists' own fallback ('where the book has none, the plate headings printed
in its text'), the list is the plates' own printed headings, transcribed by eye
from the full-size page images into the per-leaf table HORSEY_FIGS in
fit/src_roman_horsley.py (24 entries; written offline into
data/books/lists/britanniaromanao00hors.json + .map.json).

**The 24-entry list (17 kind-s / 7 kind-o; corrected to 24 in 807,
2026-10-14):** 219 transcribed 22 entries (15 kind-s). Two more are genuine
site-plan plates, verified 220 on the full-size images and the book's own text,
and added to the table 2026-10-14: n0114 (P.44) 'Innerpeffery camp.' + 'Ardoch
camp.' - the two legionary camps of the Mons Graupius campaign (the text
pp.43-44: 'the legions might poflibly have been at Ardoch, or Innerpeffery,
before they marched to the battle'; each plan with its scale of 200/300 yards,
the Ruchel and Knoch rivers, a military way and a Praetorium box); n0185
(P.113) 'The five fecondary ftations per lineam valli' - five fort plans, I
GLANNIBANTA (Lanchester), II ALIONE (Whitley Castle), III BREMETEN RACUM (Old
Penrith), IV OLENACUM (Old Carlisle), V VIROSIDUM (Elenborough). The 219
mislabel: 219 dismissed stage A's flags on both leaves as parametric
hallucinations - the flags were right, only the invented captions were not.
Completeness (220): a whole-book hOCR sweep (every page with text <700 chars
listed, every page scanned for plan vocabulary: camp/ftation/fort/fecondary/map
of/plan/scale of/section) found no further kind-s leaf in the book - the
remaining short pages are front matter, the Book-II letter-table (hocr 306),
the altar-instruments plate (312), the Book-II collection title (315), the
chronological table (885), the index (895) and the hOCR-silent fold-outs (hocr
63/705/834/868) - so 24 is complete. The 7 kind-o leaves (n0060/n0062 the
Ptolemy fold-outs; n256 the N.11 wall section; n0706/n0734/n0832/n0867 the four
country maps) are indexed, never staged.

**Stage A (936/936 triaged, 0 errors, 2026-10-13; recall against the list
measured offline, 219's run 2026-10-13 reproduced with the corrected-list run
2026-10-14, books_lists.validate_book - the shared validation.json is never
written):** page types 703 text_only / 151 other_illustration / 80
plate_site_plan / 2 unparsed. A typed 80 pages plate_site_plan, but the ink
floor (BLANK_INK=0.005) keeps exactly 17 - the 63 others are blank/ghost
show-through versos (their engraved border frames alone fooled the model).
Stage-A-only (no floor) against the 22-entry list is precision 0.188 (15/80) -
exactly why the ink floor is what makes the flagged set usable on this book
(stage-A-only against the corrected list: recall 1.0, precision 0.212 = 17/80).
Against the 22-entry list (219): recall_pages 1.0, recall_pages_pm1 1.0,
precision 0.882 (15/17), flagged_not_in_list [114, 185] = the mislabel. Against
the corrected 24-entry list: recall_pages 1.0, recall_pages_pm1 1.0,
precision_strict = precision_lenient 1.0 (17/17); flagged_not_in_list [],
flagged_on_other_only_pages [], missed_pages [] - the ink-filtered flagged set
(17) of stage-A's 80 of 936 triaged matches the list's 17 kind-s leaves
exactly. Stage F was never needed (no figure_site_plan / F / C rows exist for
this book).

**Stage B (2026-10-14: 17 pages, 0 errors, 18 s, on replicas 8080/8081 - 8082
was down):** B re-read all 17 flagged leaves as plans (B's schema has no kind
field - its verdict is a non-empty plans[]; 31 plan boxes in total). B's
printed titles and site_names feed the staging rows: n0114 the two camp titles
(each with a 200-yard scale bar and a north arrow); n0185 the five Roman names
with their modern names (B spells it 'Old Penreth' - 808's staging source of
truth; the list keeps the transcribed 'Penrith'); the 15 wall maps their
segment fort names (1-4 plans each). B's set is unchanged by the list
correction (A's ink-filtered 17 already included n0114/n0185), so no re-run was
needed.

**Staging (the 17-row plan that 808 executes; every row year 1732 + the 200
evidence field - kind caption_coords, named_place = the plate's printed list
entry; url/thumb = the stable IA full-page image):** the 15 wall maps on the
216 QID/extras design - multi-fort maps tie to the 216-verified catalog QID
site where one exists (castrum-segedunum-q637958 SEGEDUNVM,
pons-aelius-q7227963 PONSAELIVM,
rudchester-roman-fort-associated-civil-s-q17669775 VINDOBALA,
haltonchesters-roman-fort-settlement-and-q17648018 HANNAVVM, aesica-q4688554
the Aesica plan on N.7, birdoswald-roman-fort-and-the-section-of-q17650767
BORCOVACEVS), otherwise to an existing-or-new extras row, the other fort names
recorded in desc. n0114: ONE row tied to a NEW no-QID Ardoch 'roman site'
extras row, the Innerpeffery camp recorded on the row. n0185: ONE row tied to
the principal of the five P.113 forts' new no-QID 'roman fort' extras row, the
other four forts' names on desc (the choice recorded there + in a DECISIONS
entry). Extras rows for all five P.113 forts only if 809's join requires each
new site to have a plan; the four Antonine camps (bar-hill-fort, inchtuthil,
raedykes, rough-castle-fort) are REUSED from extras.jsonl, not re-created. The
220 catalog check (12603 sites + 193 extras, keyed by name): none of the seven
P.113/Ardoch/Innerpeffery sites exists yet - all new no-QID rows.

**Staged (808, 2026-10-14 - the plan above, executed):** all 17 kind-s leaves staged = 100%
of the list's kind-s (207a's moved 90% box met with nothing missing, so no drop reasons): the
15 wall maps on the ties above, n0114 to the new Ardoch row (the Innerpeffery camp recorded on
that row's desc - no row of its own, the box), n0185 to the new VIROSIDUM row - the P.113
principal, the only one of the five without a catalog row (I-IV =
longovicium/whitley-castle/voreda/luguvallium; the join check said a NEW row needs a staged plan,
so only the principal gets one - DECISIONS 808 147 item 4). Eight new no-QID extras_roman rows
(region lowercase, kind space-form, cross-checked location_check): cilurni (Chesters, confirmed;
the catalog's Q17650519 sits 300 m away - the row stays no-QID), petriana (Horsley's HYPOTHETICAL
N.8 Solway-coast station, approx), congavata (Castlesteads, confirmed; catalog's Q17650705 200 m
away), tunnocelum (Boulneis per the N.10 plate, approx), kirkintilloch (the Peel, confirmed;
Q2422689 town item, precision 30 m), carriden (the Antonine Wall's east end near Bo'ness,
confirmed; Q81445376, precision 1e-6, kind 'roman site' - no fort plan on the N.5 plate; renamed
from falkirk-end when the Wikipedia Antonine Wall article fixed the east end), ardoch (the Braco
camp, Gask Ridge, confirmed; Q4788225, precision 1e-6, kind 'roman site' - the Knoch stream
proved unlocated in the sources checked), virosidum (near Maryport per the N.1 map, approx).
bar-hill-fort and rough-castle-fort REUSED from extras.jsonl, not re-created. Every row: year
1732, the 200 evidence field (kind caption_coords, named_place = the row's title, place_* =
site_* = the tied site's own coordinates, dist_m 0.0 - re-verifiable offline from stored fields;
evidence.check over the 17 rows: 17 pass / 0 fail), url/thumb = the stable /download/ page
image. The book's IA metadata has no license flag (checked 2026-10-14, live + cached), so the
license field reads 'public domain (the 1732 original, pre-copyright era)' (DECISIONS 808 152).

**Deferred (never staged):** the ~121 inscription/sculpture plates (Roman
numerals I-CXXI) trail as HORSEY_PLATES (kind o - indexed in the list mapping,
each naming the site where the stone was found); not transcribed yet, and not
blocking: the 90%-of-site-plans box counts only kind-s leaves, and 808 stages
all 17 (100%, nothing missing).

## Maclauchlan, Memoir, Written During a Survey of the Roman Wall (1858) - 207b (in progress)

**Source (verified 2026-10-13/14):** one readable IA copy only - memoirwrittendu00maclgoog, the
1858 original (Google scan, 171 leaves, median 3290x5182 px; djvu.txt + djvu.xml, NO hOCR page
index - per-leaf OCR comes from the djvu.xml OBJECTs, leafNum = n+1, aligned 1:1 with the
bookreader leaves). The other copies are unusable: memoirwrittendur0000henr, the "1971 reprint"
candidate, is a MISLABELED item (its pages are Linda Nochlin's *Realism*), and
henrymaclauchlan0000macl (the 2015 Wanney presentation) is lending-restricted (LCP/ACS) and
unreadable from this machine (both PITFALLS) - so fetch, triage and every staged image come from
the 1858 original, and the text is read from its djvu.xml and triage images.

**Date (settled by reading the title pages from the triage images, iterations 130-131):** the
short and full title pages both print "A SURVEY OF THE ROMAN WALL, THROUGH THE COUNTIES OF
NORTHUMBERLAND AND CUMBERLAND, IN THE YEARS 1852-1854" and end "LONDON: PRINTED FOR PRIVATE
CIRCULATION. MDCCCLVIII" (the printer's line on the verso: Bradbury and Evans, Whitefriars). The
preface dates the survey: Wallsend summer 1852, to Carvoran 1853, completed to Bowness by winter
1854. So the survey ran 1852-1854 and the volume was printed 1858 - NOT the 1857-59 this lead's
title line (and the parent task file) assumed; the 1858 printing does carry later work (the
Willow Holm section taken Sep't 7th 1858, the Carlisle plan's 1857-58 great sewer), and a gift
leaf (n0007, presented by the Duke of Northumberland, Alnwick Castle, 17 July 1859) shows the
volume circulating by 1859. Staged rows carry 1858, the year printed on the title page.

**List (the book has no printed plate list):** a privately-circulated original - no LIST / PLATES
heading anywhere in the front or back matter. Its only list is the DIRECTIONS TO THE BINDER (djvu
leaf 119), verbatim: "The Plans, Fig. 1, 2, 3, and 6, showing the Mote, Brampton, &c., to be
inserted at page 65. The Plans, &c. of the Roman Wall in Willow Holm, at page 76. The Plans, Fig.
4, 6, Carlisle and the Camp on Skew Hill at page 76." Per books_lists' own fallback ("where the
book has none, the plate headings printed in its text"), the ground truth is the per-leaf hand
table (the six lines of MACLAUCHLAN_FIGS in fit/src_roman_maclauchlan.py): each plate/figure
leaf's own printed heading/caption, transcribed by eye from the triage images + djvu.xml - the
book's list, mapped to leaves in data/books/lists/memoirwrittendu00maclgoog.json + .map.json
(written offline, byte-stable).

**Inventory (the six leaves, per-leaf verdicts):**
- **n0078** Fig. 1, Brampton (p.65) - plan of the Brampton camp (the doubtful position of
  Aballava). **BLANK in this copy** (frame, compass, labels and scale bar survive; the drawing
  faded) - verified site plan (stage A plate_site_plan), nothing left to stage.
- **n0090** Willow Holm (p.76) - plan, section and elevation of the Roman Wall in Willow Holm
  (440 yards from the west mouth of the sewer; reduced from M'Me Kie's section taken Sep't 7th
  1858). A wall section - not a site (207 Notes) - not staged (stage A other_illustration).
- **n0093** Fig. 4, Carlisle (p.76) - plan of Carlisle: course of the Wall and the Vallum between
  Stanwix and the Castle, with the 1857-58 great sewer and its drain; scale of chains and scale
  of feet; "H M^L delin", Sandridge & Co. Litho London. **The only site plan legible in this copy
  - the one that gets staged** (staged 2026-10-14 by the module's offline --stage leg: one
  files_roman row (year 1858, the IA stable /download/ page image, w/h 964x1400 from the stage-B
  row) + one "plan" classified row, tied to the NEW extras_roman site luguvallium-q71551754
  "Luguvallium (Carlisle)" Q71551754 - the fort's own item, not Carlisle Castle (Q614836); 200
  evidence kind caption_coords: the named place "Carlisle" (the binder's list) resolves to the
  city's P625 (Q192896), 324.1 m from the fort's P625 point - fit/evidence.py check PASSES
  offline; idempotent append, a second run changes no byte).
- **n0111** gateway near Housesteads (p.93) - the gateway of 1856 near the station of Borcovicus
  in the Knag Burn valley (caption "Gateway discovered near Housesteads (Borcovicus) in 1856.").
  **BLANK in this copy** (faint frame only) - verified site plan (stage A figure_site_plan),
  nothing left to stage.
- **n0115** Table of Stations (p.97) - printed table of the stations of the Notitia, the Ravenna
  and the Chorographus, with their distances. A text table, not a plan (stage A text_only) - not
  staged.
- **n0129** marks on Roman tiles, Binchester (p.7 of the Watling Street memoir) - two boxed
  letter-marks from Roman tiles with a 6-inches bar. An artifact figure, not a site plan (stage A
  other_illustration) - not staged.

**Unprinted figures:** Figs 2, 3 and 5/6 (the Mote, the Camp on Skew Hill) were never printed in
this copy - the 122 size census (all 171 triage images) leaves no room for hidden plates. They
count against no box.

**Stage-A/B recall against the list** (books_lists.validate_book, run OFFLINE 2026-10-14 with
the network blocked; the shared validation.json is not written - 211 rebuilds it): 171 pages,
171 triaged (A, 0 errors); stage F never needed (A's site set equals the list's kind-s set
exactly). Against the six-line hand list (3 kind-s site pages: 78, 93, 111; 3 kind-o: 90, 115,
129): flagged site pages 3 (stage-A-only 3), recall_pages 1.0 (±1: 1.0), precision_strict 1.0,
precision_lenient 1.0, missed_pages [], no false positives (90/129 both read other_illustration,
115 text_only; flagged_on_other_only_pages [], flagged_not_in_list []). Stage B read all three
site leaves (3/3 ok, 0 errors, ~10 s on the two live replicas): n0093's map_box
[100,405,830,880] norm1000 (label "FIG. 4" and both scale bars read) is what the staged row
uses; n0078/n0111's boxes are record-only.

**90% box (staged vs verified site-plan pages):** 1 of 3 (n0093) = 33% < 90%; the two missing are
accounted for individually per the box's disjunct: n0078 (Brampton) and n0111 (the Housesteads
gateway) are blank in this copy - the drawings faded (only frame/labels/scale bar survive), so
there is nothing to stage from them, and no other IA copy is readable (Source, above).

## Roy, Military Antiquities of the Romans in North Britain (1793) - 207c (dropped)

**Source (verified 2026-10-11, re-verified 2026-10-13):** NOT on the Internet Archive -
exhaustive advancedsearch (the exact title, title phrases, creator "Roy, William", a
1790-1800 year-range text query, ten guessed identifier patterns - all empty; the only
related item is the 1917 dissertation ABOUT Roy, macdonald-1917-roy: no facsimile, no plate
list, not the book). The National Library of Scotland holds the only complete online
facsimile (maps.nls.uk/roy/antiquities/: 174 text pages + 51 map plates of the Roman camps
and forts of Scotland) but it refuses this VM: AWS-WAF "Human Verification", HTTP 405 on
every path with browser user agents (checked 10-11 and again 10-13, the drop-decision day);
the open NLS S3 tile bucket holds no antiquities set (roy/ = 1747-55 military-survey tiles
only, the background maps of pipeline/nls.py). HathiTrust 403s this VM and the Google Books
API answers 429 with a 0-queries/day anonymous quota (both recorded 10-12/13 for the
Wiltshire lead; the same wall, re-verified for this book 10-13) - so no complete copy of the
book can be fetched from this VM at all, and the human has declined to download books for
this project (the standing refusal of 209a/209c, PITFALLS).

**Outcome (ask_human 008, answered 2026-10-13 14:36, console):** the request (filed
2026-10-13 from 207c's session: confirm the owner's "Stop 207" covers this subtask, and
either the NLS facsimile into data/raw/books/roy1793/ - any layout, minimum the 51 map
plates plus the printed list of plates - or a drop decision) was answered: "drop Roy. I
dont want to have to ever go out and get a file. If you need it get it. If you can't get
it, then you don't need it." **Task 207c is DROPPED.** No Roy rows exist in any staging
file, and none will be staged unless a complete scan of the book ever appears in the repo
(data/raw/books/roy1793/, any layout); if it does, the resume recipe is the parent
hand-over's (207) "Mechanics for every subtask" plus its exact-next-steps item 3.

**Stage-A/B recall against the printed list of plates:** n/a - the book was never obtained;
207c was dropped before any triage stage ran.

**Effect on the lead:** the Roman lead stands on 207a (Horsley 1732: the engraved maps and
fort plans of England, Wales and the two walls) and 207b (Maclauchlan 1857-58: the
Hadrian's Wall forts); the parent's acceptance boxes 1-4 are met by those two books alone.
The map does not gain Roy's early Scottish camp plans: the catalog's four no-QID Antonine
Wall camps (bar-hill-fort, inchtuthil, raedykes, rough-castle-fort in extras.jsonl) stay
without plans from this book, and no new Scottish roman_fort rows are staged by this lead
(Scottish sites Horsley or Maclauchlan do show are staged by their own subtasks as usual).
