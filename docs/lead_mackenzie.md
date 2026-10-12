# Mackenzie, The Castles of England (1897), page 212: the captionless plan (task 206, GOAL point 4)

GOAL point 4: page 212 of the book is a castle plan with no caption - the only gap in the book's
already hand-tied plates: the MACKENZIE table in `pipeline/sources.py` (26 rows: 21 BL page scans plus
5 separately uploaded "Plan of ..." crops; six further plates were already harvested for their sites
before that table) names it in its comment: "Left out: ... page 212 (a five-towered castle with no
caption)." This document is the record of the identification: **Shotwick Castle, Q7502621** (Saughall
and Shotwick Park, Cheshire; the existing catalog row in `data/catalog/sites.jsonl`; the site is
built - this task ran `pipeline/build_catalog.py --ids shotwick-castle-q7502621`, so the fit doc
below names a built site and is not orphaned in the shared store).
The evidence chain is §3 - the file's Commons category is the site's own P373, the book's index and
V2 chapter text name Shotwick, the plate sits in V2's Cheshire/Wirral zone nineteen leaves before the
Lancashire part, and the surviving ground matches the plan - and the fit proves the identification by
numbers (§4): the plan's pentagon bank and the ground's pentagon solve one similarity (rotation
-0.20 deg, i.e. the plan is printed north-up) with a median residual of 15.8 m, and the gate (001)
accepts. One row was staged and the site built by `fit/src_mackenzie.py` (§5); 211 only
consolidates the rows (the site is already built, so its build skips it).

## 1. The scan (checked 2026-10-11 live; `fit/src_mackenzie.py --verify` re-checks the live title, size, description and categories and fails loud on drift)

- **File:** `File:212 of 'The Castles of England- their story and structure ... With ... illustrations
  and ... plans' (11296081346).jpg` - the British Library's 2013 "Flickr's The Commons" dump, the same
  title pattern as the 26 hand-tied plates. The 2013 upload date ("2013-12-09 20:43") is kept raw in the
  staged row's `date`; the year 1897 comes out of `commons.year_of` from the file's description
  ("Date of Publishing : 1897"), so no `date_commons` swap was needed.
- **Size:** 839x840 - the smallest of the book's hand-tied scans (p.207 is 895x781). Artist "The
  British Library", license "No restrictions".
- **Description (verbatim in the staged row):** BL shelfmark HMNTS 10369.v.7; **Volume : 02, Page :
  212**; "The Castles of England: their story and structure ... With ... illustrations and ... plans",
  MACKENZIE, James Dixon - Sir, Bart; W. Heinemann, London; "Date of Publishing : 1897"; "View this map
  on the BL Georeferencer service" (id 11296081346).
- **Original:** `https://upload.wikimedia.org/wikipedia/commons/3/37/212_of_%27The_Castles_of_England-_their_story_and_structure_..._With_..._illustrations_and_..._plans%27_%2811296081346%29.jpg`
- **Commons page:** `https://commons.wikimedia.org/wiki/File:212_of_%27The_Castles_of_England-_their_story_and_structure_..._With_..._illustrations_and_..._plans%27_(11296081346).jpg`
- **Categories (2026-10-11):** `Shotwick Castle` (the site's own P373, §3a), `Floor plans of castles`,
  `The Castles of England: their story and structure (1897)`, `Images from the British Library`,
  `Images released by British Library Images Online`, `Set of Maps`, `Files from Flickr's 'The
  Commons'`, plus two upload-review categories.
- **Downloaded (working phase, gitignored):** `data/raw/books/mackenzie/212.jpg` (the book copy) and
  `data/raw/commons/shotwick-castle-q7502621/e6e5490609414bb9.jpg` (the machinery's slot that
  `fitkit.plan_image` and `export_plans` look up; re-fetch with `--fetch`). The 211 overlay will use
  this original: no bigger render exists for the BL Flickr file (839 px over ~740 px of plan is still
  ~1 m per 5-6 px, fine for point-pair matching).

## 2. The plan (from the image; the drawing spans the whole page)

The 839x840 scan is a full-page plan - the ink spans x 9..829, y 10..832, so the platefit doc's crop is
the whole frame (the alligator/barnard full-frame convention). **No caption, no scale bar** - the gap
the book left, and why the page number, not a caption, names the row.

Features, in page px of the 839x840 frame. (Corrected page map: an earlier session's reading placed
the drawing in the page's top-left quadrant; that was a misread and is void - the drawing fills the
page.)

- A thick-lined **pentagonal bank** (the earthwork) with corners TOP (405,25), RIGHT (827,570), BOTTOM
  (620,835), LOWER-LEFT (30,690) and LEFT (50,430). The left edge is solid (an earlier session's
  suspected gap there was a misread, verified on a 2x left-edge crop).
- **Six horseshoe round towers** - the book's own words, §3c: "a pentagon strengthened by six towers"
  (the task's "five-towered" was an early count that missed the top one): top (the largest)
  (350-470, 30-160); upper-left, mid the upper-left edge (95-230, 150-280); upper-right, mid the
  upper-right edge (740-880, 190-310); right, at the right corner (780-900, 510-660); lower-right
  (525-690, 675-830), its opening facing the gate; lower-left, at the lower-left corner (40-180,
  590-770).
- A **hall** in thin lines, upper centre (410-540, 180-310): a gabled block with corner turrets and a
  door stub at bottom-centre.
- A **second, small building** in thin lines, lower centre-left (290-390, 640-780), tilted ~20 deg,
  with a **dashed** conjectural line from its top-left corner to the bank's left corner - the
  draughtsman's own uncertainty, not a wall.
- A **gate gap** in the thick bank at lower centre (620-655, 825-845), at the bottom corner, with small
  square teeth on the bank's underside near it.
- A **compass** at centre-right (355-605, y~472): a thin horizontal line with an open-V arrowhead at
  its LEFT end (pointing page-left), a vertical crossbar at x~455, four small curved corner-marks
  round the intersection and a small filled wedge just left of the crossbar. The arrow's page-left
  north is 90 deg off: the corner fit (§4) solves a rotation of -0.20 deg, i.e. the plan is printed
  NORTH-UP as a normal map - the arrow marks something else (or is simply wrong).

## 3. The identification (the evidence chain; every fact re-verifiable - checked 2026-10-11)

**Decision: IDENTIFIED - Shotwick Castle, Q7502621** (Saughall and Shotwick Park, Cheshire; the catalog
row in `data/catalog/sites.jsonl`: kind "motte", scheduled monument, NHLE 1016616 / HE 67153; enwiki:
"a Norman medieval fortification near the village of Saughall, Cheshire ... No masonry features remain
above ground except for earthworks.").

**(a) The file's Commons category is the site's own P373.** The 2013 Flickr-dump file sits in the
Commons category `Shotwick Castle` - exactly Q7502621's P373 value (both verified live 2026-10-11;
`--verify` re-checks both and fails loud if the file leaves the category). A human had already filed
the BL scan under the castle - the tie the 200 records on the staged row: kind `category`, checked
2026-10-11 (the 26 hand-tied rows carry a different tie, kind `hand_tied` with `cat` null: a different
tie, a different field).

**(b) The book's own index names Shotwick in volume 2.** The V2 scan's index (archive.org
`castlesofengland02mack`, OCR; leaf 539 = printed 447) reads "Shotlack, ii. 179, **Shotwick, ii.
180**." (Compare "Windsor, i. 180" and "Winchester, i. 214" in the same list - i. and ii. both occur,
so the volume markers are genuine.)

**(c) The V2 chapter text is the plan's own provenance.** Printed p.180 (heading "S H O T W I C K
(non-existent)" at the bottom of leaf 228; the chapter continues on leaf 229 under the running head
CHESHIRE 181; the next chapter, STOCKPORT, starts on 181). Verbatim (OCR, lightly cleaned):

> THIS was one of the Norman forts erected by the Earls of Chester to protect their frontier from the
> Welsh, Shotwick being intended to guard the shallow channel of Dee in the Wirral Hundred. ... Leland
> speaks of it as existing in his day. 'A myle lower is Shottewik Castle, on the very shore, longing to
> the king, and therby ys a parke.' In the Harleian MSS. (2073) is a drawing and plan of this fortress
> by Kendle Holme, as it appeared then, in a ruinous condition. Its trace was a pentagon strengthened
> by six towers, one of which, according to Camden, was five storeys high. The wash of the tides, and
> the cultivation of the lands, have not quite obliterated these remains, those seen at present
> consisting merely of a large mound, supported by a huge earthwork of crescent form, and two deep
> entrenchments on the land side.

The plate is Holme's c.1600 drawing of the ruin - which explains the schematic thick bank, the six
towers, and why the 1897 ground carries only mound + crescent + entrenchments.

**(d) The county context - the true layout (a correction of the task's framing).** The task says
p.212 is bracketed by p.207 Oxford and p.231 Lancaster. Only half true: the two IA volumes paginate
separately (V1 = 548 leaves, printed 3..475; V2 = 504 leaves, printed 5..448), so a file number is a
leaf number *within its volume*. The live BL "Volume" tags (verified 2026-10-11 in one batched
`commons.info` call over the 26 hand-tied plates and p.212) put p.207 Oxford in volume 1 and **p.212
and p.231 Lancaster both in volume 2, nineteen leaves apart**. The tags are otherwise mixed and
incomplete (01: p.42, 120, 132, 134, 207, 252, 337, 356, 378, 393, 480, 528, 533; 02: p.87, 135, 145,
175, 188, 231, 349; missing: p.106 and four of the five "Plan of" crops, only Caister tagged 01) - so
the county context rests on the book's own OCR (running heads, index, chapter text), not on the Flickr
metadata. The V2 county sequence (running heads CHESHIRE 163..181 verified in the OCR): Aldford
(162-164), Brimstage (166), Chester (167-169), Dodleston (170), Dunham Massey (171), Frodsham (172),
[175-178], Shotlack (179), **SHOTWICK (180-181)**, Stockport (181), Houghton Tower (182), Bury (182) -
then the LANCASHIRE part opens on printed 183 (= leaf 231, the Lancaster plate's leaf: "Henry VII.
conferred the estate on his supporter, Lord Stanley, afterwards first Earl of Derby"; Clitheroe
forfeited on 184) - Liverpool (198-199), Manchester (200). The plate sits in V2's Cheshire/Wirral
zone, nineteen leaves before the Lancashire part.

**(e) The surviving ground carries the plan's features.** The 800 m aerial (Esri World Imagery at
1 m/px - the machine's normal build image: the site row is kind "motte" with `aerial_ok`; the EA LiDAR
relief is flaky on this box, see PITFALLS) shows a grassed oval earthwork with a faint ring in its
eastern part (= the C11 motte, ~40x20 m, at (80, -5) m from the catalog point), a standing building
cluster NW of centre (the hall's 1897 successor, dark tree clumps around it), a road on the west,
open fields; **no visible towers or hall footprint** - matching the book's own "merely a large mound
... crescent ... two deep entrenchments" (§3c). The machine-checkable part of this is the fit, §4.

**(f) Candidates considered.** The only plan in V2's Cheshire/Wirral zone is this one: within
nineteen leaves of p.212 the only other captioned V2 plate is the Lancaster plate (p.231, the
Lancashire part's opening leaf, hand-tied to Lancaster Castle Q2969640 in sources.py). No other county
castle in V2 has a pentagon-with-six-towers plan matching all of a-e - and the book's own text (§3c)
independently records "a pentagon strengthened by six towers" for Shotwick. **No candidate was
rejected; the identification is accepted.**

## 4. The fit (the platefit doc; the gate proves the identification by numbers)

**Doc:** `data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json` (plan id = `c_` +
sha1-16(title), the export_plans rule; written 2026-10-11T19:04:44+00:00; src "commons", book
"Wikimedia Commons", size [839,840], crop = the whole frame, model "similarity", label "1897").

**Pairs** (page px of the 839x840 frame -> ground; four of the five plan corners - the NW corner,
the ground pentagon's weakest-prominence peak, is dropped; with exactly three pairs any similar
triangle fits both orientation conventions, so four were recorded):

| Feature (page) | page px | ground (lon, lat) | ground peak (m E/N from the catalog point) | residual |
|---|---|---|---|---|
| TOP corner of the pentagonal bank | (405, 25) | (-2.9756073, 53.2282398) | N (+31.5, +115.8) | 14.2 m |
| RIGHT corner | (827, 570) | (-2.974283, 53.2272404) | E (+119.8, +4.5) | 2.0 m |
| BOTTOM corner | (620, 835) | (-2.9747557, 53.2267733) | S-SW (+88.2, -47.5) | 17.5 m |
| LOWER-LEFT corner | (30, 690) | (-2.977288, 53.2270046) | W-SW (-80.5, -21.8) | 19.4 m |

**The ground pentagon:** measured from the segmentation of the 800 m aerial (2.19 ha, centroid
(27.2, 9.4) m); r_out(phi) = the max boundary radius per 1-degree bin around the centroid, 5-pt
circular smooth, peaks of prominence >= 3 m and >= 20 deg apart: N, E, S-SW, W-SW (used) and NW
(-27.2, +53.5) (dropped, weakest prominence). The clockwise gaps between the ground peaks
(89/41/121/53/56 deg) track the plan's pentagon (95.6/46.5/98.9/40.2/78.8 deg) - the ground is a
rounded, squashed version of the plan's pentagon.

**Gate (001; docs/gate.md section 2 rule, section 4 "true case"):** `fit_gate.gate(doc pairs,
transform=None)` - no placement is claimed, so the gate solves the canonical similarity from the
pairs, exactly `plan_fit.similarity`; the hand fit's own residual is the claim. **ACCEPT**: n 4,
med 15.81 m (<= 45), slope_o 0.1385 (<= 0.145 - but inside the 0.11-0.145 "usable, must be said" band:
the attenuated region where a 15% scale error at n = 3-6 sits, so the gate cannot vouch for the
fit's scale beyond that band; the review queue and the human's 18/20 sample are the backstop,
gate.md sections 7 and 9), io -7.04 (the second clause, slope_o > 0.11 with io < -10, is not
triggered). `plan_fit.similarity`: rotation -0.20 deg (north-up, §2), ground scale 0.229 m/px (=
|a| x cos 53.2272 deg; a is Mercator m/px), residuals 14.2 / 2.0 / 17.5 / 19.4 m (max 19.4 < 45).

**Rejected sets (recorded, never used):** all five corners (med 14.96 but slope_o 0.167 > 0.145,
io +17.7); five corners + the gate gap (slope_o 0.315, gap residual 76.8 m - the ground's local
radius minimum in that sector is the cleft between the E lobe and the NE tangle, not the plan's gate
gap). **Predictions (recorded, not pairs):** the solved pentagon centre (20.5, 17.4) vs the
segmentation centroid (27.2, 9.4); the C11 motte ring (80, -5) sits 63.6 m from the predicted centre,
in the eastern bailey; the hall (475, 245) maps to (+41, +78) m, on tree clumps, not a standing
building.

## 5. Decision (identified - one row staged; what 211 must know)

**IDENTIFIED, not dropped.** a-f all hold and the gate accepts. Staged 2026-10-11 by
`fit/src_mackenzie.py` (idempotent on (site, title); `--check` re-verifies the join and the evidence
offline, exit 0):

- `data/commons/files_mackenzie.jsonl` - one row: site `shotwick-castle-q7502621`, qid Q7502621,
  title = the file's title, year 1897, cat "Shotwick Castle", name "Shotwick Castle, plan from
  Mackenzie, The Castles of England (1897)", by "fit/src_mackenzie.py", the Commons metadata fields,
  evidence {rec "evidence/1", kind "category", checked 2026-10-11, site_cat = file_cat "Shotwick
  Castle", via []}.
- `data/commons/classified_mackenzie.jsonl` - one row: p_plan 1.0, by "hand".
- `data/catalog/extras_mackenzie.jsonl` - one row: aerial_ok true, source "fit/src_mackenzie.py" -
  the reason to build (task Notes): this task built the site itself on 2026-10-11 (the lead
dropped the 211 dependency and the shared-store tests require every fit doc to name a built
  site); 211 merges the row into extras.jsonl, sees the site already built and skips it; the
catalog's sites.jsonl row carries the same id and the full record (admin, heritage, designation)
  and reads first in the merge (211 logs the duplicate).

**What 211 must know:** the doc id `c_e6e5490609414bb9`
(`data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json`, committed); the image
`data/raw/commons/shotwick-castle-q7502621/e6e5490609414bb9.jpg` (gitignored, re-fetch via
`--fetch`); the three staged rows above; and that this doc is the **first hand-fit doc after the
gate registration** - 218 (the gate-holdout tolerance for post-registration hand docs) covers the
gate test, and this task built the site on 2026-10-11 (`pipeline/build_catalog.py --ids shotwick-
castle-q7502621`: Environment Agency 1 m LiDAR relief and block diagram, the Ordnance Survey
six-inch 1st edition map from NLS; `data/sites/shotwick-castle-q7502621/site.json` committed, the
`web/data/sites.json` entry is the 385th site, per-site images gitignored and rebuilt by the
pipeline), which turned test_serve's platefits-docs check and test_batch_eu's temp-tree union
test green on this task's merge. The live full-coverage union test stays skip-gated until 203b's
`docs/batch_eu.md` "Sites run" matches the grown EU list (212 re-covers the growth). 211's merge
builds no site here - build_catalog skips an already-built site - and only consolidates the rows.
