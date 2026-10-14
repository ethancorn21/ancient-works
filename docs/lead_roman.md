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
  - the one that gets staged** (a new site row in extras_roman.jsonl, 207b's stage leg).
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
