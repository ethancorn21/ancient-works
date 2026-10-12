# Wiltshire: Hoare, Stukeley, Petrie - old drawings of Stonehenge and Avebury (task 209, GOAL point 4)

GOAL point 4: the old drawings of the two most famous sites on the map. This lead stages the
site-plan plates of three works - Hoare's *Ancient Wiltshire* (1812-21), Stukeley's Wiltshire work
(1740s) and Petrie's *Stonehenge, Avebury, and other Stone Age monuments of the British Isles*
(1880) - one book per subtask (209a/b/c; 209a/Hoare is dropped - its section below), each into
its own per-suffix staging files
(`data/commons/files_wiltshire_{a,b,c}.jsonl` + `classified_wiltshire_{a,b,c}.jsonl`, rows tagged
with the book; a `*_wiltshire_{a,b,c}` extras file only if a plate shows a Wiltshire earthwork not in
the catalog yet). Per-book book artifacts only (`data/books/triage/<id>.*.jsonl`,
`data/books/lists/<id>.json` + `.map.json`): the shared `data/books/index.jsonl` and
`validation.json` are never written by this lead - 211 rebuilds the shared index from the per-book
files once. The existing hand fits (Allcroft Avebury fig. 187, Allcroft Windmill Hill fig. 186, in
`data/db/platefits/`) are never re-staged or re-fitted: new rows only. The stage-A/B recall against
each book's own printed list of plates is recorded in that book's section below, in place of the
shared validation.json.

## Hoare, Ancient Wiltshire (1812-21) - 209a (dropped)

**Source (verified 2026-10-13, re-verified 2026-10-12):** NOT on the Internet Archive - exhaustive
advancedsearch (the title phrase returns only two modern books; the hundred names Pewmarsh/Pewsey/
Cherhill return nothing). HathiTrust holds the work (public domain, full view) and Google Books
serves it, but both refuse this VM: HathiTrust answers HTTP 403 to every request (checked with
several user agents, including a browser UA, on both 2026-10-12 and -13) and the Google Books API
429s it. So the copy arrives human-downloaded, the 207c pattern: **ask_human 001 (filed 2026-10-12)**
asks for **volume 3, *The Hundred of Cherhill* (1821)** - the volume that carries the
Stonehenge/Avebury/Silbury/West Kennet plans - placed in `data/raw/books/hoare_cherhill1821/` as one
image per leaf page, filenames sorting in book order (covers included; the module re-encodes to
triage size). Vols. 1-2 (Pewmarsh 1812, Pewsey 1819) are a bonus, same placement in their own
folders. Fallbacks in the request: "drop" (this lead then stands on 209b/209c) or any other complete
scan of the Cherhill volume.

**The fetch leg (built 2026-10-12, `fit/src_wiltshire_hoare.py`, tested in
`tests/test_src_wiltshire_hoare.py`):** the module registers the book in process
(`books.BOOKS["hoare_cherhill1821"]`, ia/region/year/cite/why) and wraps the machinery's three
IA-only calls (`books_ia.pages`, `books_ia.page_texts`, `books.fetch_triage`) for this id only: the
local leaf list (n = 0-based leaf index, leafNum = 1-based) and the local re-encode (1400 px long
side, JPEG q88) land at the exact `books.triage_path` slot, so `books.run_stage` (triage A/F/B on
the live Qwen replicas, 127.0.0.1:8080-8082) and everything after it run UNMODIFIED. No per-page
OCR exists for a local copy (`page_texts -> {}`): the plate anchors come from Qwen's stage A
(`map_plates` handles that - its OCR-only evidence simply stays empty). Commands: `--fetch`
(local, resumable, idempotent), `--status` (offline: leaf count, triage progress, LLM ports),
`--triage A|F|B` (working phase). The remaining legs - list transcription (`--list`, the
books_lists PLATES pattern from the copy's own list pages), staging (`--stage`, 200 evidence field:
list entry names the place, caption / coordinates distance recorded on the row; the 1821 date on
every row), `--check` (offline join + fit/evidence.py) and `--golden`
(`tests/golden/src_wiltshire_hoare_sample.json`) - were never built (the copy never arrived): the
module is DORMANT, and they would be added if it is ever revived with a real scan.

**Outcome (ask_human 001 refused, iteration 151, journal date 2026-10-13):** the request (filed 2026-10-12 from
209a's session: the human downloads the Cherhill volume in a real browser from HathiTrust - public
domain, full view - or Google Books, places one image per leaf page in
`data/raw/books/hoare_cherhill1821/`, vols. 1-2 a bonus; fallbacks "drop" or any other complete
scan) was refused: "No. If you can't find the book at all, then i am not going to go get it. Just
skip it." **Task 209a is DROPPED** (its own designed fallback): no Hoare rows exist in any staging
file, and none will be staged unless a complete scan of the volume appears in the repo later (the
dormant fetch leg above works as-is for that: `--fetch`, then `--triage A` as a resumable
background job, the remaining legs added then). The Wiltshire lead stands on 209b (Stukeley: the
IA book leg + the Commons leg) and 209c (Petrie: its own download ask 002 was refused the same
way, but 209b's Commons check had already satisfied its fallback - the two canonical
`files.jsonl` rows are Petrie 1880 Pl. I/II, see the Petrie note in the Stukeley section).

**Stage-A/B recall against the printed list of plates:** n/a - the copy was never obtained; 209a
was dropped before any triage stage ran.

## Stukeley, 1740s - 209b

**Sources (2026-10-12, iteration 146):** (1) the Internet Archive BMB scan of *Stonehenge, a
Temple Restor'd to the British Druids* (1740), ia=`bim_eighteenth-century_stonehenge-a-temple-rest_stukeley-william_1740` -
BookReader list verified: **166 leaves** (n0-n165, leafNum == n, ~8657x13266 full-res); hOCR
(14.7 MB) + searchtext + pageindex, DjVuTXT, scandata all downloadable - the standard book
machinery runs unmodified (unlike 209a: this book really is on IA, so no local-copy wrap). Its
plates (Stukeley's numbered Stonehenge plan, the Avenue plan, the Wiltshire map) tie to
stonehenge-q39671. (2) Commons-hosted Stukeley plates - the 205-Kip pattern, no book machinery.

**Commons candidates, visually verified 2026-10-12** (every fit-sized file in
Category:William Stukeley + its subcategories - 266 files total - downloaded and looked at or
ruled out by the live metadata):

| File | Size | What it is | Disposition |
|---|---|---|---|
| `File:Houghton Arc 855.214 - Stukely, the Druid temple of Abury.jpg` | 2269x1362 | Stukeley's **TAB. VIII, p.14** of his Wiltshire volume: "A Scenographic view of the Druid temple of ABVRY in north Wiltshire, as in its original" (W. Stukeley Delin.; dedication to Sir Phillip Packer, Lord Chancellor). The henge circle with the ditch and the inner circles, Windmill Hill, the West Kennet long barrow, Silbury, the Longstones, Temple Downs, Overton. Houghton's copy (Arc 855.214) is the **1743 second edition** ("Abury, a temple of the British druids, and some others described", London 1743 - per the Commons description) of the 1740 first edition. | **Stage** -> avebury-q661855, kind plan, date 1743. Evidence: caption_coords, the title/description spell "Abury" (Stukeley's spelling of Avebury), place = Avebury's own Q661855 coordinates, dist 0. |
| `File:Stonehenge Dessin Stukeley 1722 03547.jpg` | 4620x2430 | The 1722 Itinerarium drawing: "An inward view of Stonehenge Aug. 1722 from the north" (perspective view of the standing stones; Commons: 1722, CC BY-SA 3.0, a scan by G. Garitan). | **Stage** -> stonehenge-q39671, kind view, date 1722. Evidence: caption_coords, "Stonehenge" in the title, place = the site's own coordinates, dist 0. |
| `File:Stukelykitscoty.jpg` | 1020x320 | Stukeley's pen drawing of the Uffington scene: "The upper Kitts Cate house" (the long barrow), "The Grave", Fedderham place and the White Horse country. Hand style identical to his 1722 Itinerarium drawings (the Stonehenge Dessin above); Commons has no date or description. | **Stage** -> kit-s-coty-house-q4222497 (a catalog site), kind view, date 1722 (attribution above). Evidence: caption_coords, the filename's mangled "kitscoty" spelling of Kitts Coty, place = the site's own coordinates, dist 0. |
| `File:47 of 'Stonehenge- plans, descriptions and theories' (11135894643).jpg` | 2245x2852 | **Petrie 1880 Pl. I** - the Stonehenge stone-by-stone plan: "W.M.F.P. mense et del.", scale 1:350, sarsen/bluestone key (Standing 1880 / Standing 1747 / Overthrown), "Forms of outlying stones". | **NOT staged here** - it is a Petrie plate; it **already sits in the canonical files.jsonl** (stonehenge-q39671, 1880, caption_coords "Stonehenge", the British Library Georeferencer description naming PETRIE, shelfmark HMNTS 10352.i.12, p.47, E. Stanford 1880). This finding satisfies 209c's fallback (a) - see the Petrie note below. |
| `File:49 of 'Stonehenge- plans, descriptions and theories' (11133409654).jpg` | 4641x2874 | **Petrie 1880 Pl. II** - Stonehenge with the Avenue, the Cursus inset, the parallel banks; scale 1:1500; "Petrie levels in inches by numbering of stones"; W.M.F.P. | **NOT staged here** - same as above (already canonical, row 714). |
| `File:Stonehenge Stukley Oxford 03543.jpg` | 3606x2976 | Identified: "DRUIDS SACRIFICING TO THE SUN IN THEIR TEMPLE CALLED STONEHENGE - The Building taken from the Model according to Dr Stukeley's Plan of Stonehenge restored in the Ashmolean Mus. Oxford; Designed, Engraved & Published by W. Whistock, High Street, Oxford". A romantic view of Stukeley's **conjectural restored temple** with a crowd of druids - not a drawing of the actual monument. The Commons date 1722 is wrong for this print (it post-dates the Ashmolean model). | **Not staged** (a model, not the site); identification recorded here. |
| everything else in the category (266 files) | | portraits/engravings (the Kneller portrait CIPB0894, Herman Moll, Wellcome engravings), the *Memoirs of Sir Isaac Newton* (1752) page scans and fleurones, the Jewry Wall (Leicester) elevations (Roman/medieval, not a catalog site), the Clarendon palace ruins (1723 - Roman/medieval; **no clarendon row in data/catalog/sites.jsonl**, checked 2026-10-12 -> not a catalog site), the Lincoln shrine, the Sumatra earthquake letter, and the fit-sized-but-<1000 px Stonehenge/cursus drawings (Stonehenge Stukeley.jpg 773x404, Stonehenge-cursus-stukeley.jpg 638x377). The Stonehenge-Mod KSA.jpg (2002x1498) is a 1996 PHOTOGRAPH of the Salisbury Museum restoration model. `ThesanctuaryWilliamStukeley.jpg`, `Stukeley fire at Avebury.JPG`, `Cadbury Castle Stukeley.jpg` and the DPLA Wood/Jones/Smith/Stukeley view are already tied in the canonical files.jsonl. | not site drawings of catalog works, or already canonical - nothing else to stage. |

Both legs are done (209b, committed): `fit/src_wiltshire_stukeley.py` stages **5 rows** into
`data/commons/files_wiltshire_b.jsonl` - the 3 Commons rows above plus the IA book's two verified
site-plan plates (below) - with classified rows (the Avebury plan p_plan 1.0, the two views
p_birdseye 1.0, the two book plans p_plan 1.0). All 5 pass `fit/evidence.py` offline from stored
fields alone (`--check`: 5 rows, 5 pass, 0 fail, 0 no-tie; golden:
tests/golden/src_wiltshire_stukeley_sample.json; tests/test_src_wiltshire_stukeley.py, 8 tests).
Per-book artifacts only: triage/<ia>.*.jsonl (A/F/B), lists/<ia>.json + .map.json - the shared
index.jsonl and validation.json were never written (211 rebuilds them).

**IA book leg, *Stonehenge, a Temple Restor'd* (BMB scan, 166 leaves, fetched 2026-10-13):**
fetched all triage pages (IIIF 1400 px); stage A 166/166, 0 errors; stage F on the 41
other_illustration leaves; stage B on the 6 stage-A plan leaves + 2; `--list` (books_lists
cmd_ocrmap over the transcribed list) wrote only the per-book lists files.

**The plate list:** the book has **no printed list of plates** (leaves 10-12 are blank/preface;
all 166 leaves walked visually) - the plates' own engraved headers ("P. <n>. TAB. <roman>") are
the only list, and the BMB hOCR of the engraved plates is garbage (the title page reads only
"By VILEIAM STUKELEY..."). So the transcription is the 213/civitates **hand-list** pattern:
31 entries (33 plate impressions - TAB. II and III each twice, XXI/XXIV absent from this copy,
XXXIIII old-style; STUKLEY_PLATES in the module), read by eye from each plate leaf at triage
size, the roman numerals resolved on 2x label crops. The book's own pagination is the plates'
"P. <n>" headers only (no page numbers in the text leaves' running heads matched them).

**Stage-A/B recall against that list** (in place of the shared validation.json):
- **Stage A** flagged exactly 6 leaves as plate_site_plan: **all 3 leaves of the two plan-view
  plates** (TAB. XI the numbered plan as a fold-out, n56+n57; TAB. XXIII the Area plan, n111)
  plus 3 false positives on perspective views (n123 XXVI, n135 XXIX, n143 XXXI) - recall on plan
  leaves 3/3, precision 3/6; no other plate leaf was flagged.
- **Stage F** (41 leaves) read the plate headers with their kind, incl. n61 "TAB. XII ->
  section" - an independent confirmation of the XII reclassification below.
- **Stage B** (8 leaves) read both plan leaves as plans: n111 cleanly ("The Area of STONEHENGE",
  scale "50 100 150 Cubits / 50 100 150 300 Feet", map box); n57's banner title correct but its
  label numeral misread "TAB. XL" (resolved by the zoomed crop + the plate sequence VII..XII: it
  is XI); n56 (the XI fold-out's left half) is label-garbled ("the Cuts") but shows the 0-100 feet
  scale and the north arrow.
- **ocrmap** (list -> leaves) matched 2 of the 31 entries: XI -> n57 (title) and XXIII -> n115
  (qwen+title) - the latter is the **wrong of the two XXIII impressions** (n115 is the Avenue
  track *view*, kind o; the real Area-plan leaf n111's header OCR "P.44. TAB.XXIII" lost the
  anchor). Staging never consults the map (leaf numbers are hand-set), so this affects only the
  .map.json attribution, not the staged rows.
- **TAB. XII (The Orthography of Stonehenge) is NOT staged:** first read as a plan at triage
  size, re-checked against the leaf image 2026-10-14 - it is an orthographic *section* (the
  elevation with the "The Front" scale bar), so its kind was set to o and it is the one
  plan-like plate deliberately left out (the only one not staged, accounted for here).
- **No Wiltshire map in this scan** (every leaf checked; the map, if it exists at all, belongs
  to *A survey of Wilts*, which is not on IA) and **no standalone Avenue plan** - the Avenue
  shows in the XXIII area plan and in the perspective views only.

**Petrie note (209c):** the two unlabeled Flickr files are Petrie 1880 plates (Pl. I and Pl. II,
visually confirmed above) AND are already in the canonical files.jsonl with caption_coords
evidence (checked 2026-10-10, the BL Georeferencer description names Petrie/1880). 209c's
Commons fallback is therefore satisfied: if the human declines the 1880 download (ask_human
002), those two canonical rows are the Commons leg and nothing more is stageable from Commons;
the rest of the book (Avebury, Silbury, West Kennet plates) still needs the human-downloaded
copy.

**The existing hand fits** (Allcroft Avebury fig. 187, Allcroft Windmill Hill fig. 186 in
data/db/platefits/) are untouched: new rows only.

**Stage-A/B recall against the plate list:** see the Stage-A/B recall record above (the book has no
printed list of plates - the transcribed headers ARE the list; the transcription and the recall
live in this section, in place of the shared validation.json).
