# Book plates and figures: index summary

Built 2026-10-10 by `pipeline/books.py` (+ `books_ia.py`, `books_lists.py`, `books_mills.py`, `books_match.py`,
`books_summary.py`). Every number below was measured on the real scans; the tables come from `books_summary.py`.

Status: complete. The first run stopped Qwen (the vision model) mid-run because it was slowing Ethan's other
agents. A rerun later on 2026-10-10, on both 3090s, finished the missing stages. What is still open is under
"Not done" at the end.

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

- `index.jsonl`: 890 rows, one per site plan (one per plan or list entry on a page), 675 distinct pages.
  - Fields: book, ia_id, leaf_n (0-based BookReader index = `page/n{N}.jpg`), leaf_jp2, plate/sub/fig, title and
    title_source, numbers_on_page, captions_ocr, site_names, place, scale_text, north_angle_deg, map_box,
    blank_boxes, full_url, full_local, full_size.
  - Title source per row: transcribed list of plates, OCR list of figures (OCR errors kept), the page caption in
    IA OCR, or "page, read by Qwen". 848 of 890 rows have a title.
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
- Full-res site-plan pages: `data/raw/books/<ia_id>/full/n{NNNN}.jpg`. All 675 index pages are present and pass a
  PIL verify, 0 download failures, about 580 MB in total (Mills folder: 88 county maps + 26 site plans). One
  Lapham page left over from an earlier index build is not in the index.
- Triage-size pages (1400 px long side): `data/raw/books/<ia_id>/triage/`.

| book | pages | stage A | stage F | stage B | index rows | site-plan pages | by Qwen | by list only |
|---|---|---|---|---|---|---|---|---|
| squier_davis_1848 | 452 | 452 | 125 | 65 | 145 | 68 | 67 | 1 |
| lapham_1855 | 230 | 230 | 38 | 68 | 115 | 68 | 65 | 3 |
| thomas_1894 | 896 | 896 | 302 | 196 | 197 | 193 | 187 | 6 |
| fowke_1902 | 788 | 788 | 216 | 75 | 88 | 75 | 71 | 4 |
| squier_1851 | 222 | 222 | 41 | 34 | 55 | 33 | 33 | 0 |
| whittlesey_1850 | 54 | 54 | 0 | 7 | 18 | 7 | 7 | 0 |
| allcroft_1908 | 743 | 743 | 211 | 205 | 235 | 205 | 200 | 5 |
| mills_1914 | 206 | 206 | 13 | 26 | 37 | 26 | 26 | 0 |

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
| lapham_1855 | 52 | 51 | 0.98 | 0.98 | 0/2 |
| whittlesey_1850 | 7 | 7 | 1.0 | 1.0 | 0/0 |
| squier_1851 | 14 | 14 | 1.0 | 1.0 | 0/0 |
| thomas_1894 | 29 | 29 | 1.0 | 0.759 | 0/6 |

Lapham:
- Miss: XXVI (n166), which Qwen typed as other. (XVII, missed before the rerun, is now found.)
- One plate is not mapped to a leaf: XI "Ancient Works, Township 12, Range 20, east" (not located; it may share a
  sheet with X or be missing from the scan).

Thomas:
- Qwen misread some plate numerals (e.g. XXX as XXV). The OCR and caption anchors fix the mapping (29/29).
- Qwen invented captions on the blank show-through backs of the fold-outs. An ink filter (0.005) drops those pages.

Figures (text pages with a site-plan figure, judged at page level):

| book | figures parsed / listed | site-plan pages in list | recall A | recall A+Clef | recall A+Clef (+-1 leaf) | precision A (strict/lenient) | precision A+Clef (strict/lenient) |
|---|---|---|---|---|---|---|---|
| squier_davis_1848 | 196/207 | 15 | 0.733 | 0.933 | 0.933 | 0.647/0.882 | 0.583/0.833 |
| lapham_1855 | 50/61 | 14 | 0.643 | 0.857 | 0.857 | 0.692/0.692 | 0.857/0.929 |
| thomas_1894 | 325/344 | 113 | 0.938 | 0.947 | 0.973 | 0.658/0.733 | 0.677/0.759 |
| fowke_1902 | 298/303 | 69 | 0.971 | 0.942 | 0.986 | 0.957/0.971 | 0.915/0.944 |
| allcroft_1908 | 162/224 | 139 | 0.964 | 0.964 | 0.993 | 0.67/0.67 | 0.67/0.67 |

How to read the figure table:
- Precision here is a lower bound. A flagged page counts as wrong whenever the parsed list has no site-plan figure
  on it, and the parsed lists are incomplete.
- Allcroft: 66 of the 200 flagged pages are not in the parsed list, because 62 list entries have no parsed page.
  - Before the rerun I viewed 20 such pages by eye, picked across the book (not a random sample). All 20 were real
    site plans; one, a hut plan (n247), is borderline. That check was not redone on the new set of 66.
  - So 0.67 is a floor; most of the 66 are probably real plans, but they are unchecked.
- Allcroft recall A is now 0.964 (it was 0.525 when Qwen had stopped at page 391); misses are n530, n552, n577,
  n580 and n603.
- Clef alone on all of Allcroft: recall 0.899, precision 0.676 (lower bound).

Typical model errors:
- Misses: small figures inside text, and pages that mix a plan with a view or an artifact.
- False flags: plans of natural features (beaver dam, windfalls, serpentine ridges) and an altar plan.

## Boxes, scale, north arrow (stage B)

- Stage B now covers every book: 850 of 890 rows have a map box, 508 have scale text, 589 have a north arrow
  end-point pair.
- Box convention confirmed by drawing: Qwen's boxes are 0-1000 per axis. Stored as page fractions
  [x0, y0, x1, y1], origin top-left.
- First check on 6 S&D plates: map box good on 5 of 6 (Newark cut off). Titles read 6/6.
- North angle compared with the fitted rotations of the same 6 plates. Errors: 8.9, 1.7, 11.6, 95.4, 4.3, 1.8 deg.
  - Newark's arrow is horizontal; Qwen gave about 0.
  - A rerun flipped Hopeton to 131 deg.
  - So north_angle_deg is a hint only and must not be used to rotate without a check.

## Catalog match (`matches.jsonl`)

Rule-based matching, no model.

| book | matched | ambiguous | no candidate | generic title |
|---|---|---|---|---|
| allcroft_1908 | 73 | 106 | 52 | 2 |
| fowke_1902 | 23 | 8 | 56 | 1 |
| lapham_1855 | 2 | 9 | 99 | 5 |
| mills_1914 | 6 | 3 | 26 | 1 |
| squier_1851 | 0 | 0 | 44 | 11 |
| squier_davis_1848 | 13 | 11 | 69 | 52 |
| thomas_1894 | 18 | 21 | 157 | 0 |
| whittlesey_1850 | 0 | 3 | 14 | 1 |

- Overall: 135 of 890 rows matched (0.152), 89 distinct catalog sites. 0.165 of the rows that have a distinctive name.
  The denominator is index rows (one per plan or list entry, 675 distinct pages), not plates or sites.
- Hand overrides (`HAND` in books_match.py) are keyed on the title with case and punctuation ignored, so a rerun
  that re-reads "Banwell Cross" as "BANWELL CROSS." keeps the override.
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

## Not done

- The 2026-10-10 rerun finished what Qwen had not reached: Allcroft stage A (pages 391-742), stage B and stage F
  on all 8 books. Numbers above are after that rerun.
- 42 rows are still untitled: S&D 22, Squier NY 16 (their figure numbers are in numbers_on_page), Allcroft 4.
- Mills site-plan titles are Qwen-read. Mills has no OCR per page to cross-check them.
