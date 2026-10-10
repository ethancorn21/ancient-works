# Book plates and figures: index summary

Built 2026-10-10 by `pipeline/books.py` (+ `books_ia.py`, `books_lists.py`, `books_mills.py`, `books_match.py`,
`books_summary.py`). Every number below was measured on the real scans; the tables come from `books_summary.py`.

Status: partial. Qwen (the vision model) was stopped mid-run on the lead's order because it was slowing Ethan's
other agents. What it had not done is listed under "Not done" at the end.

## Books and scans

All scans were picked through the IA advancedsearch and metadata APIs, comparing every copy on IA (reasons per
book are in `BOOKS` in `pipeline/books.py`).

| key | IA id | why this copy |
|---|---|---|
| squier_davis_1848 | ancientmonuments00squi | LoC scan, 500 ppi, highest of 4 copies; already used by the fitted plates |
| lapham_1855 | antiquitiesofwis00saph | LoC scan, fold-outs scanned unfolded (up to 5768x5906 px) |
| thomas_1894 | annualreportofbu1218901891smit | Smithsonian, 360 ppi, the only copy with fold-outs scanned unfolded (UC copy is 500 ppi but folded) |
| fowke_1902 | b24849959 | Wellcome, 500 ppi colour |
| squier_1851 (NY) | b30449492 | Wellcome, largest copy (3113x4653 median) |
| whittlesey_1850 | descriptionsofan00whit | Smithsonian/BHL, largest of 2 copies |
| allcroft_1908 | earthworkenglan01allcgoog | Google/NYPL, 600 ppi greyscale (the Harvard copy is bitonal) |
| mills_1914 | ArcheologicalAtlasOfOhio | lead's request; only copy on IA; 150 ppi two-page openings; no hOCR per-page text |

Not done: Colt Hoare, Ancient Wiltshire, is not on IA as a usable scan (decision for the lead: HathiTrust or
Wikimedia Commons source).

## Files

- `index.jsonl`: 813 rows, one per site plan (one per plan or list entry on a page), 670 distinct pages.
  - Fields: book, ia_id, leaf_n (0-based BookReader index = `page/n{N}.jpg`), leaf_jp2, plate/sub/fig, title and
    title_source, numbers_on_page, captions_ocr, site_names, place, scale_text, north_angle_deg, map_box,
    blank_boxes, full_url, full_local, full_size.
  - Title source per row: transcribed list of plates, OCR list of figures (OCR errors kept), the page caption in
    IA OCR, or "page, read by Qwen". 770 of 813 rows have a title.
- `mills_county_maps.jsonl`: 88 rows, page type "county site map", one per Ohio county (88/88 distinct, no
  duplicates, every name checked against the atlas's own OCR headings).
  - All 88 have scale text "Scale, one inch equals three miles".
  - All 88 are downloaded at full resolution in `data/raw/books/ArcheologicalAtlasOfOhio/full/`.
  - No symbols were extracted.
- `matches.jsonl`: index row to catalog site.
- `validation.json`: the validation numbers below.
- `lists/`: the parsed lists of plates and figures.
- `triage/`: raw stage outputs.
- `checks/`: 6 box drawings, under 90 KB each.
- Full-res site-plan pages: `data/raw/books/<ia_id>/full/n{NNNN}.jpg`. All 670 index pages are present and pass a
  PIL verify, 0 download failures, about 590 MB in total (Mills folder: 88 county maps + 26 site plans). One
  Lapham page left over from an earlier index build is not in the index.
- Triage-size pages (1400 px long side): `data/raw/books/<ia_id>/triage/`.

| book | pages | stage A | stage F | stage B | index rows | site-plan pages | by Qwen | by list only |
|---|---|---|---|---|---|---|---|---|
| squier_davis_1848 | 452 | 452 | 0 | 6 | 129 | 65 | 60 | 3 |
| lapham_1855 | 230 | 230 | 0 | 0 | 98 | 68 | 61 | 7 |
| thomas_1894 | 896 | 896 | 0 | 0 | 195 | 194 | 184 | 6 |
| fowke_1902 | 788 | 788 | 0 | 0 | 86 | 75 | 70 | 1 |
| squier_1851 | 222 | 222 | 0 | 0 | 49 | 34 | 34 | 0 |
| whittlesey_1850 | 54 | 54 | 0 | 0 | 17 | 7 | 7 | 0 |
| allcroft_1908 | 743 | 391 | 0 | 0 | 213 | 201 | 95 | 8 |
| mills_1914 | 206 | 206 | 13 | 0 | 26 | 26 | 26 | 0 |

Pipeline stages:
- Stage A: Qwen page type and the numbers printed on the page.
- Stage F: Qwen per-figure type.
- Stage B: Qwen per-plan reading (boxes, scale text, north arrow, on-page title, site names).
- Clef-flash: p(plan) on 1219 pages. All 743 Allcroft pages, plus the pages Qwen typed "other illustration" in the
  other books. Threshold 0.5, fixed in advance.

## Validation against each book's own list of plates / figures

Ground truth:
- Plate lists were transcribed from the list pages (read from the page images where the OCR was garbled).
- Figure lists were parsed from IA OCR.
- Kinds (site plan / other / unsure) were judged from the printed titles, with hand overrides.
- Squier NY has no list of plates; its 14 plates come from the "PLATE X. No. n" headings in the text.

Plates mapped to leaves by an ordered chain over three anchors: the numerals Qwen read, "PL. X" in the OCR, and
caption-to-title similarity.

| book | site plates listed | mapped to a leaf | Qwen typed site plan | Qwen read the numeral | other plates called site plan |
|---|---|---|---|---|---|
| squier_davis_1848 | 43 | 43 | 1.0 | 1.0 | 0/4 |
| lapham_1855 | 52 | 51 | 0.961 | 0.98 | 0/2 |
| whittlesey_1850 | 7 | 7 | 1.0 | 1.0 | 0/0 |
| squier_1851 | 14 | 14 | 1.0 | 1.0 | 0/0 |
| thomas_1894 | 29 | 29 | 1.0 | 0.759 | 0/6 |

Lapham:
- Misses: XVII (n148) and XXVI (n166), which Qwen typed as other.
- One plate is not mapped to a leaf: XI "Ancient Works, Township 12, Range 20, east" (not located; it may share a
  sheet with X or be missing from the scan).

Thomas:
- Qwen misread some plate numerals (e.g. XXX as XXV). The OCR and caption anchors fix the mapping (29/29).
- Qwen invented captions on the blank show-through backs of the fold-outs. An ink filter (0.005) drops those pages.

Figures (text pages with a site-plan figure, judged at page level):

| book | figures parsed / listed | site-plan pages in list | recall A | recall A+Clef | recall A+Clef (+-1 leaf) | precision A (strict/lenient) | precision A+Clef (strict/lenient) |
|---|---|---|---|---|---|---|---|
| squier_davis_1848 | 196/207 | 15 | 0.733 | 0.8 | 0.8 | 0.647/0.882 | 0.632/0.842 |
| lapham_1855 | 50/61 | 14 | 0.643 | 0.643 | 0.786 | 0.692/0.692 | 0.75/0.75 |
| thomas_1894 | 325/344 | 113 | 0.938 | 0.947 | 0.973 | 0.658/0.733 | 0.673/0.761 |
| fowke_1902 | 298/303 | 69 | 0.971 | 0.986 | 1.0 | 0.957/0.971 | 0.919/0.946 |
| allcroft_1908 | 162/224 | 139 | 0.525 | 0.942 | 0.993 | 0.768/0.768 | 0.679/0.679 |

How to read the figure table:
- Precision here is a lower bound. A flagged page counts as wrong whenever the parsed list has no site-plan figure
  on it, and the parsed lists are incomplete.
- Allcroft: 62 of the 193 flagged pages are not in the parsed list, because 62 list entries have no parsed page.
  - I viewed 20 of the 62 by eye, picked across the book (not a random sample). All 20 are real site plans; one,
    a hut plan (n247), is borderline.
  - So Allcroft precision is at least (131+20)/193 = 0.78. That is a floor, not an estimate; the other 42 pages are
    unchecked.
- Allcroft recall A is 0.525 only because Qwen stopped at page 391 of 743; on the first half Qwen's recall was 1.0.
- Clef alone on all of Allcroft: recall 0.899, precision 0.676 (lower bound).

Typical model errors:
- Misses: small figures inside text, and pages that mix a plan with a view or an artifact.
- False flags: plans of natural features (beaver dam, windfalls, serpentine ridges) and an altar plan.

## Boxes, scale, north arrow (stage B, only 6 S&D plates)

- Box convention confirmed by drawing: Qwen's boxes are 0-1000 per axis. Stored as page fractions
  [x0, y0, x1, y1], origin top-left.
- Map box good on 5 of 6 (Newark cut off). Titles read 6/6.
- North angle compared with the fitted rotations of the same 6 plates. Errors: 8.9, 1.7, 11.6, 95.4, 4.3, 1.8 deg.
  - Newark's arrow is horizontal; Qwen gave about 0.
  - A rerun flipped Hopeton to 131 deg.
  - So north_angle_deg is a hint only and must not be used to rotate without a check.

## Catalog match (`matches.jsonl`)

Rule-based matching, no model.

| book | matched | ambiguous | no candidate | generic title |
|---|---|---|---|---|
| allcroft_1908 | 50 | 86 | 54 | 23 |
| fowke_1902 | 18 | 7 | 61 | 0 |
| lapham_1855 | 2 | 9 | 78 | 9 |
| mills_1914 | 4 | 5 | 14 | 3 |
| squier_1851 | 0 | 0 | 34 | 15 |
| squier_davis_1848 | 16 | 3 | 38 | 72 |
| thomas_1894 | 13 | 22 | 157 | 3 |
| whittlesey_1850 | 0 | 3 | 13 | 1 |

- Overall: 103 of 813 rows matched (0.127), 65 distinct catalog sites. 0.150 of the rows that have a distinctive name.
  The denominator is index rows (one per plan or list entry, 670 distinct pages), not plates or sites.
- Checked by eye against the names: 3 clearly wrong (now `status: rejected_by_eye` with a note; the 2 doubtful
  ones are `status: doubtful`).
  - Mills "Map of Serpent Mound, Warren Co." went to the Adams County Serpent Mound. It is a different effigy;
    US catalog rows have no county, and such rows are flagged `county_unchecked`.
  - Allcroft "Banwell Cross" and "Cruciform earthwork at Banwell" both went to Banwell Camp, the hillfort.
- 2 doubtful: Thomas's Kanawha group near Charleston went to Criel Mound, one mound of that group; "The Old Pale,
  Eddisbury" went to Eddisbury hill fort.

The low US rate is mainly the catalog. It has 337 US sites and lacks:
- Hopeton, High Bank, Cedar Bank, Mound City (only the umbrella "Hopewell Culture NHP").
- Junction Group, Baum, Liberty/Harness, and the Newark Octagon.

These important plates stay unmatched because of that:
- S&D: Hopeton, High Bank, Mound City, Cedar Bank, Junction Group.
- Thomas: High Bank, Hopeton, Baum, Liberty.
- Fowke: Clark's/Hopewell group.
- Most of Lapham's Wisconsin effigy groups.

Allcroft's ambiguous rows are mostly:
- Same-name sites in different counties (Maiden Castle, Cadbury Castle, Bury Castle) where the title names only a
  town.
- Historic England records named after a hillfort (barrows "near Cissbury").
- Scottish sites outside the catalog.
- OCR-garbled names.

Rows with no place word in the title get a default state for the US books where the title page fixes it: Lapham
Wisconsin; Fowke, Whittlesey and Mills Ohio; Squier 1851 New York.

## Not done (Qwen stopped)

- Stage B (map box, scale bar, scale text, north arrow, on-page title and site names per plan) for all but 6 S&D
  pages: 9 of 813 rows have a box, 7 have scale text.
- Stage F (per-figure check on mixed pages) everywhere except Mills (13 pages). This is the step that recovered
  missed small figures in the test (6 of 8).
- Qwen stage A on Allcroft pages 391-742. Clef-flash classified them instead, which is weaker on precision.
- Titles read off the page by a model for pages missing from the book's list:
  - Allcroft unlisted figures: 20 got a caption from IA OCR; 23 rows are still untitled.
  - Squier NY in-text figures: 15 untitled; their figure numbers are in numbers_on_page.
- Mills site-plan titles are Qwen-read (stage A, before the stop). Mills has no OCR per page to cross-check them.
