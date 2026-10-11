# Johannes Kip's bird's-eye views of houses and gardens: the Commons inventory (task 205)

GOAL.md point 4: Kip's (and Kip & Knyff's) bird's-eye views of UK country houses and their formal gardens - the large scans in the Commons categories `Johannes Kip` (root + its 5 subcategories) and `Britannia Illustrata`. This document is the record of `fit/src_kip.py`'s `INVENTORY` - 132 distinct files, every one given a verdict (§3) - and of what the staging does with the fit-sized ones: 12 staged views (one picture row per view, evidence kind `caption_coords` from the view's own caption, classified `p_birdseye 1.0` by hand) and new `garden` sites only where a fixed landmark (the house, the garden's axes, the park) survives to carry a fit; 211 consolidates and builds. The six views already hand-tied in `pipeline/sources.py` (KIP) are never re-staged - their canonical rows keep the evidence kind `hand_tied` ("hand-tied QID"). The Hampton Court trap applies to every candidate: the place is what the CAPTION says, never the famous namesake (the Rijksmuseum's "Gezicht op Hampton Court" is in Herefordshire, not the palace on the Thames). §3 mirrors the `INVENTORY` constant row for row (title, size, verdict, reason); the live `--list` run asserts the live Commons set and sizes against it (drift fails loud), `tests/test_src_kip.py` enforces the mirror, and the full per-file metadata (date, description, categories, URLs) is in the `--list` JSONL dump, not in this table.

## 1. Where the large scans are (checked 2026-10-13: 4th live census of the same 132 files, first 2026-10-10, re-checked 2026-10-12; `list_files()` re-checks set and sizes on every live run)

The lead categories are `Category:Johannes Kip` (the root) and its five subcategories. 13 files sit in two categories each (145 memberships): 6 root files are also in the Wilderness subcategory (Chevening, Chatsworth, Temple Newsam, Fair Lawn ×2, St James's Palace and Park), 5 Britannia Illustrata files are also in Wilderness (Beaufort House 2020.163, Cassiobury, Coley Park, Combe Abbey, Didmarton), the AIC Hampton Court photo is in the root and in Britannia Illustrata, and Siston Court is in the root and in the Glocestershire subcategory.

| Category | Files | Fit-sized (≥ 1000 px long edge) |
|---|---|---|
| `Johannes Kip` (root) | 65 | 51 |
| `└ Britannia Illustrata` | 26 | 4 |
| `└ Prints by Johannes Kip in the Rijksmuseum Amsterdam` | 24 | 24 |
| `└ The Ancient and Present State of Glocestershire` | 5 | 1 |
| `└ The history of nature, 1720` | 6 | 6 |
| `└ Wilderness (garden history)` | 19 | 12 |
| **distinct** | **132** | **92** |

**Fit-sized = long edge ≥ 1000 px** (`MIN_EDGE` in `fit/src_kip.py`): 92 of the 132 files are fit-sized, 40 are under 1000 px. The threshold needs no exception list: the largest file dropped as "too small" is 822 px (Siston Court), the smallest staged view is 1375 px (Kingsweston), and no "too small" file falls in the 900-1000 px band - the only three files there are dropped for their own reasons (the 973 px Colombo engraving - foreign; the 982 px Fair Lawn crop - a duplicate of the hand-tied 1920 px original; the 977 px Queen's Chapel - a church). Most Britannia Illustrata files are indeed 300-800 px, confirming the GOAL.md premise that they are too small to lay over the ground.

Out-of-scope sibling categories (checked 2026-10-10, re-checked 2026-10-13; not part of the inventory, and `list_files()` never reads them):

- `Category:Jan Kip` = 5 files, all Anefo/Elsevier news photos of a 108-year-old Dutch man nicknamed "Opa Kip" and of the 1953 flood - no prints of the artist.
- `Category:History of Kent` = 29 files, all non-Kip (an 1829 Virtue's church engraving, an 1832 county map, an 1855 newspaper page, a 1799 Hasted fragment, the 1646-49 Cantium armorial plate, a 1667 Rijks text leaf, geograph/Flickr photos, WW2 photos, postcards, book scans, SVG maps).

**The six hand-tied views (never re-staged).** They are already in the canonical `files.jsonl` (rows with `by: "pipeline/sources.py kip"` and evidence `kind: hand_tied`, "hand-tied QID") and in `extras.jsonl`; the staging's have-set check keeps all six titles out of this task's files.

| File | Site (QID) |
|---|---|
| An engraving of Chevening by Johannes Kip (d.1722) after Thomas Badeslade (d.1742), published (in History of Kent) 1719 by John Harris.jpg | Chevening (Q1070927) |
| Cassiobury Park by Kip and Knyff.jpg | Cassiobury House (Q5049456) |
| Gezicht op Hampton Court, RP-P-1905-194.jpg | Hampton Court, Herefordshire (Q1443802) |
| Jan Kip - Burlington House in Piccadilly - B1977.14.17783 - Yale Center for British Art.jpg | Burlington House (Q225471) |
| Jan Kip - Fair Lawn in ye County of Kent - B2017.35.2 - Yale Center for British Art.jpg | Fairlawne (Q17530246) |
| Jan Kip - The House at Chiswick in the County of Middlesex one of the Seats of the Rt Hon Charles Boyle - B1977.14.18672 - Yale Center for British Art.jpg | Chiswick House (Q1074877) |

## 2. Verified sites (checked 2026-10-13: `fit/src_kip.py --verify` live run - no duplicate, no >50 km P625 flag, no missing item; `--verify` re-runs all of it on every live run)

The 12 staged views verify against **eleven sites** - one new `garden` site per view, St James's Palace shared by its two 1707 plates. Eight carry a Wikidata QID; three have **no** item for the house at all (checked 2026-10-13) and carry `qid=None`, which the model handles (42 of the 78 extras.jsonl rows carry no qid). Duplicate check: `known_sites()` over the eight QIDs against the current catalog (sites.jsonl + extras.jsonl + web/data/sites.json = 12,575 known QIDs at check time): **none** - no new site collides with an existing one, so all eleven are genuinely new. (A future catalog growth that adds a colliding QID fails the next `--verify` loudly.)

| id | QID | Label | Landmark (lon, lat) | P625 Δ | P373 | P131 | enwiki | First name-search hit with P625 |
|---|---|---|---|---|---|---|---|---|
| badminton-house-q2628510 | Q2628510 | Badminton House | -2.28045, 51.5455 | 0.00 km | Badminton House | Badminton (village) | Badminton House | itself |
| temple-newsam-q2748017 | Q2748017 | Temple Newsam | -1.4595, 53.7842 | 0.00 km | Temple Newsam | Leeds | Temple Newsam | itself |
| hutton-hall-q5951100 | Q5951100 | Hutton in the Forest | -2.839, 54.714 | 0.00 km | Hutton-in-the-Forest | Skelton | Hutton in the Forest | **Q5951058 'Hutton Hall' - 116 km away (trap)** |
| stanway-house-q7600303 | Q7600303 | Stanway House | -1.9122, 51.9899 | 0.00 km | Stanway House | Stanway | Stanway House | itself |
| st-james-palace-q272162 | Q272162 | St James's Palace | -0.137778, 51.504722 | 0.00 km | St. James's Palace | City of Westminster | St James's Palace | itself |
| lambeth-palace-q1130266 | Q1130266 | Lambeth Palace | -0.11972, 51.49556 | 0.00 km | Lambeth Palace | LB Lambeth + Lambeth (historic) | Lambeth Palace | itself |
| somerset-house-q1344889 | Q1344889 | Somerset House | -0.117778, 51.511111 | 0.00 km | Somerset House | City of Westminster | Somerset House | itself |
| hampton-court-palace-q205666 | Q205666 | Hampton Court Palace | -0.337499, 51.4034 | 0.00 km | Hampton Court Palace | LB Richmond upon Thames | Hampton Court Palace | itself |

Every P625 of every item coincides with the recorded landmark point (Δ = 0.00 km; a >50 km value would flag the entry as a wrong item and fail the run). The landmark point is the fixed thing that carries the fit - the house or palace itself, never the QID's municipality point. P131 is the item's current administrative division; the table's `place` is the county the plate describes (the palace sits on the Richmond-upon-Thames/Kingston-upon-Thames boundary; its item carries the former). The one live name-search trap: a caption route that resolved "Hutton Hall" by name would pick Q5951058 (a different Hutton Hall near Guisborough, 116 km away) - the staged rows therefore carry the verified QID and the plate's caption, never a name lookup; the other seven searches return the correct item first.

The three without a QID (no Wikidata item for the house, checked 2026-10-13):

| id | Landmark (lon, lat) | Source of the point |
|---|---|---|
| kings-weston-house | -2.661541, 51.494382 | enwiki infobox (WGS84) of the "Kings Weston House" article; Nominatim/OSM "Kings Weston House, Bristol" (51.4944124, -2.6614991) confirms it to 4 m (re-checked today). The article's own grid ref ST529771 converts to 1.3 km W (OSGB36 to WGS84, no grid shift) - the article's two position statements disagree, so the grid ref is NOT a confirmation; the infobox/OSM pair is. (Not the Bristol suburb Q6413746, not the hill Q6413747.) The house Kip drew was the earlier Elizabethan house; the house standing on the site is the Vanbrugh rebuild of 1712-19 for the Southwells. |
| stoke-house | -2.6294812, 51.4767404 | Nominatim/OSM amenity point of "Trinity Theological College, Bristol" - the house is the Grade II* Stoke Bishop manor (built 1669 for Sir Robert Cann, Bristol MP and Mayor; the 1709 plate's "Sr. Thomas Cann" is his son), now the college. Re-checked today: 0 m. (The suburb Q7618438 is not the house; the enwiki article is "Stoke Bishop".) |
| burford-house-windsor | -0.6056, 51.4810 | the Mews / Saint Alban's Street site: two geograph photos in the Commons category "Burford House, Windsor" carry WGS-84 EXIF GPS (51.481051, -0.605551 and 51.480870, -0.605556); Nominatim "Royal Mews, Windsor" is 72 m away, same street (re-checked today). The house (the duke of St Albans', Nell Gwyn's former house) is GONE - sold to George III in the 1770s, absorbed into the Royal Mews - but the 1707 view is locked to the standing Windsor Castle (Q42646, ~325 m N of the site point) in the same view. No enwiki article ("Burford House" is a 4-way disambiguation with a red Windsor link); the house is described in the "Nell Gwyn" article, which the site row's wikipedia carries. |

The four review-queue views (Beaufort House, both impressions; Swillington; Stoke Gifford) get no site row here - 201 owns the queue; this document only names them.

## 3. The 132-file verdict table

Verdicts: **staged** (a row goes into this task's staging files, §4) · **hand-tied** (tied in `pipeline/sources.py`; never re-staged) · **drop: review-queue** (the house is gone or its survival is unverified and nothing fixed is confirmed to remain - named to the review queue, never a new site) · **drop: duplicate impression** (the same plate/picture as another file; one row per picture, the sibling is named in the reason) · **drop: not a house** (no house or garden: a fortress, a college quadrangle, a portrait, an emblem, a decorative leaf, a landscape) · **drop: church** (a church view - out of scope) · **drop: foreign** (outside the UK: the East Indies, Amsterdam, the Den Haag panorama, the Guinea charts) · **drop: city prospect** (a city view, not a house or garden) · **drop: photo** (a modern photograph of a Kip subject, not a drawing) · **drop: too small** (under 1000 px, cannot be laid over the ground).

Tally: staged 12 · hand-tied 6 · drop: review-queue 4 · drop: duplicate impression 11 · drop: not a house 18 · drop: church 7 · drop: foreign 19 · drop: city prospect 11 · drop: photo 8 · drop: too small 36 = 132.

The date column is the file's `DateTimeOriginal` as stored in Commons metadata (blank = none; the full raw value and description are in the `--list` dump). It is the plate's date in most files; in a few it is not: the AIC Hampton Court impression records the 2016 photo date (the plate's 1707 is in the title), the Hampton Court Key plan a 2009 scan date, the Colombo plate a publication sentence (Reistogt, c. 1775), and the Brympton and Wanstead details upload dates (2005, 2010) - the true plate dates for those files are in the reason column.

| File | W × H | Date | Verdict | Reason |
|---|---|---|---|---|
| (Chart of part of the Coast of Sierra Leone and Liberia from Los Islands (Guinea) to River Cess (Liberia)) RMG F0418.tiff | 7165 × 5818 | 1732 | drop: foreign | a 1732 chart of the Sierra Leone coast (from Kip's Guinea book) |
| +++Toddington Manor, by Kip (detail).jpg | 638 × 456 | circa 1708 | drop: too small | 638 px detail of the Toddington plate |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268744.jpg | 1955 × 1414 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268745.jpg | 1957 × 1405 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268746.jpg | 1955 × 1405 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268747.jpg | 1957 × 1395 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268748.jpg | 1957 × 1396 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268749.jpg | 1955 × 1418 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268750.jpg | 1957 × 1412 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268751.jpg | 1957 × 1404 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268752.jpg | 1957 × 1425 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| A Prospect of the City of London, Westminster and St. James' Park MET DP268753.jpg | 1957 × 1415 | 1710 | drop: city prospect | one of the MET's ten impressions of the 1710 London city prospect |
| AMH-8134-KB Map of part of the west coast of Africa, with an inset showing the coast of Sierra Leone.jpg | 2400 × 1783 | 1732 | drop: foreign | a 1732 map of the west coast of Africa (Sierra Leone inset) |
| AlvestonCourtKipCol2.jpg | 401 × 338 | 1712 | drop: too small | 401 px impression of the Alveston Court plate |
| An engraving of Chevening by Johannes Kip (d.1722) after Thomas Badeslade (d.1742), published (in History of Kent) 1719 by John Harris.jpg | 2112 × 1743 | 1719 | hand-tied | sources.py KIP: Chevening (Q1070927) |
| Beaufort House Kip 1708.jpg | 700 × 513 | 1708 | drop: too small | 700 px impression of the Chelsea seat plate |
| Beaufort House, Chelsea from the series Britannia Illustrata 2020.163.jpg | 3400 × 2455 | between 1707 and 1709 | drop: review-queue | Beaufort House (Chelsea) demolished 1739-40; nothing fixed remains on the ground |
| Berkley Castle by Jan Kip 1712.jpg | 452 × 364 | 1712 | drop: too small | 452 px impression of the Berkeley Castle plate |
| Birdseye view of Chatsworth in 1699.jpg | 800 × 592 | 1699 | drop: too small | 800 px impression of the Chatsworth plate |
| Cassiobury Park by Kip and Knyff.jpg | 3231 × 2330 | 1707 | hand-tied | sources.py KIP: Cassiobury House (Q5049456) |
| Cassiobury-1707.jpg | 582 × 400 | 1707 | drop: too small | 582 px impression from the French edition (Les delices) |
| ClearwellByKip.png | 452 × 362 | circa 1712 | drop: too small | 452 px impression of the Clearwell plate |
| Coley Park, 1700-1709 by L. Knyff.jpg | 682 × 569 | between 1700 and 1709 | drop: too small | 682 px impression of the Coley Park plate |
| Colombo, after Kip.jpg | 973 × 657 | Published in  Reistogt naar en door Oostindien , Amsterdam, c. 1775 | drop: foreign | Colombo (Ceylon), after a c.1680 Kip engraving |
| Combe Abbey Brit Ill.jpg | 502 × 378 | 1708 | drop: too small | 502 px impression of the Combe Abbey plate |
| Dam in Amsterdam, RP-P-OB-47.598.jpg | 7868 × 5404 | 1685 | drop: foreign | Amsterdam (the Dam), 1685 |
| Didmarton, by Kip.jpg | 610 × 496 | circa 1708 | drop: too small | 610 px impression of the Didmarton plate |
| Dumbleton, by Kip.jpg | 458 × 400 | circa 1708 | drop: too small | 458 px impression of the Dumbleton plate |
| Eaton Hall by Kip 1708 edited.jpg | 595 × 430 | — | drop: too small | 595 px impression of the Eaton Hall plate |
| Flaxley Abbey Kip.jpg | 540 × 475 | 1712 | drop: too small | 540 px impression of the Flaxley Abbey plate |
| Garden at Ham House, Surrey - geograph.org.uk - 2042063.jpg | 3872 × 2592 | 2010-08-21 | drop: photo | a 2010 geograph photo of the Ham House garden |
| Gezicht op Amsterdam vanaf het IJ, RP-P-2019-2636.jpg | 5746 × 4456 | between 1662 and 1722 | drop: foreign | Amsterdam from the IJ (one of a six-plate panorama) |
| Gezicht op Hampton Court, RP-P-1905-194.jpg | 7032 × 5258 | 1709 | hand-tied | sources.py KIP: Hampton Court, Herefordshire (Q1443802) |
| Gezicht op Musschat, RP-P-1905-3935.jpg | 6856 × 4686 | 1682 | drop: foreign | Muscot (Arabia), 1682 |
| Gezicht op Stanway, RP-P-1949-369.jpg | 6140 × 5562 | 1709 | staged | BI 49/61 1709; the Jacobean manor (Charteris) and its baroque water gardens survive |
| Gezicht op Stoke Bishop, RP-P-1949-367.jpg | 7018 × 5576 | 1709 | staged | BI 52/61 1709; the Cann seat at Stoke Bishop still stands (rebuilt c.1765-73) |
| Gezicht op Stoke Gifford, RP-P-1949-368.jpg | 6486 × 5318 | 1709 | drop: review-queue | the seat was rebuilt 1750 (Wright) and is lost; the estate built over; house survival unverified |
| Gezicht op Tegepatnam, een Moors kasteel en de Nederlandse loge, RP-P-1935-790.jpg | 6762 × 4582 | 1676 | drop: foreign | Tegnapatnam (Kormandel coast), 1676 |
| Gezicht op de kapel van King's College, Cambridge (linkerdeel), RP-P-2018-833.jpg | 5162 × 6408 | in of na 1707 | drop: church | King's College Chapel, Cambridge (left half) |
| Gezicht op de kapel van King's College, Cambridge (rechterdeel), RP-P-2018-834.jpg | 5428 × 6478 | in of na 1707 | drop: church | King's College Chapel, Cambridge (right half) |
| Gezicht op de kapel van King's College, Cambridge, bestaande uit twee delen, RP-P-2018-832.jpg | 10326 × 6390 | in of na 1707 | drop: church | King's College Chapel, Cambridge (the two-part plate) |
| Gezicht op de stad Cranganoor, RP-P-OB-47.597.jpg | 7044 × 4764 | 1676 | drop: foreign | Cranganore (Malabar coast), 1676 |
| Gezicht op eiland en Kasteel Tenos, RP-P-1905-3936.jpg | 6820 × 4670 | 1682 | drop: foreign | Tennore island and castle (Malabar), 1682 |
| Gezicht op het eiland Ternate, RP-P-OB-47.595.jpg | 7080 × 4780 | 1682 | drop: foreign | Ternate (Moluccas), 1682 |
| Gezicht op het landgoed Badminton, RP-P-1949-370.jpg | 7010 × 5310 | 1709 | drop: duplicate impression | same plate as Landgoed Badminton RP-P-1949-371 (the staged impression) |
| Gott Collection at Hepworth Gallery (112a).JPG | 3576 × 2700 | between 1680 and 1722 | staged | the full Temple Newsam plate; the house still stands (National Trust) |
| Gott Collection at Hepworth Gallery (113a).JPG | 2796 × 2176 | between 1680 and 1722 | drop: duplicate impression | detail crop of the Temple Newsam plate (112a is the staged impression) |
| Gott Collection at Hepworth Gallery (114).JPG | 4000 × 3000 | between 1680 and 1722 | drop: duplicate impression | detail crop of the Temple Newsam plate (112a is the staged impression) |
| Gott Collection at Hepworth Gallery (115).JPG | 4000 × 3000 | between 1680 and 1722 | drop: duplicate impression | detail crop of the Temple Newsam plate (112a is the staged impression) |
| Gott Collection at Hepworth Gallery (31).JPG | 3576 × 2448 | before 1722 | drop: not a house | Sedbergh School master's-house plans - a school, not a country house |
| Gott Collection at Hepworth Gallery (32).jpg | 3592 × 1976 | before 1722 | drop: not a house | Sedbergh School plans - a school, not a country house |
| Gott Collection at Hepworth Gallery (33).JPG | 2616 × 1708 | before 1722 | drop: not a house | Sedbergh School engraving (authorship detail) - a school, not a country house |
| Gott Collection at Hepworth Gallery (80a).JPG | 3328 × 2468 | before 1722 | drop: review-queue | Swillington Hall (Lowther) demolished 1952 (mineworkings); no fixed landmark remains |
| Gott Collection at Hepworth Gallery (81).JPG | 3000 × 4000 | before 1722 | drop: duplicate impression | detail crop of the Swillington plate (80a is the review-queue impression) |
| Gott Collection at Hepworth Gallery (82a).JPG | 3792 × 2732 | before 1722 | drop: duplicate impression | detail crop of the Swillington plate (80a is the review-queue impression) |
| Gott Collection at Hepworth Gallery (83a).JPG | 3564 × 2496 | before 1722 | drop: duplicate impression | detail crop of the Swillington plate (80a is the review-queue impression) |
| Gott Collection at Hepworth Gallery (84).JPG | 4000 × 3000 | before 1722 | drop: duplicate impression | detail crop of the Swillington plate (80a is the review-queue impression) |
| Gott Collection at Hepworth Gallery (85).JPG | 4000 × 3000 | before 1722 | drop: duplicate impression | detail crop of the Swillington plate (80a is the review-queue impression) |
| Ham House 05.JPG | 2592 × 1944 | 2011-08-29 | drop: photo | a 2011 photo of Ham House |
| Ham House London 04.JPG | 1944 × 2592 | 2011-08-29 | drop: photo | a 2011 photo of Ham House |
| Hampton Court Key.jpg | 781 × 537 | 2009-03-27 | drop: too small | 781 px plan (key) of Hampton Court Palace |
| HamptonCourtKipKnyff1708.jpg | 643 × 475 | — | drop: too small | 643 px impression of the Herefordshire Hampton Court plate |
| Henbury, by Kip.jpg | 595 × 484 | circa 1708 | drop: too small | 595 px impression of the Henbury plate |
| Hutton Hall Kip.jpg | 3796 × 2739 | by 1709 | staged | BI 1709; the Cumbrian Fletcher seat still stands (Grade I: pele tower, 1680 hall, walled garden) |
| Interieur van de Deense Kerk te Londen, RP-P-1911-286.jpg | 5098 × 7288 | 1697 | drop: church | interior of the Danish Church, London (demolished 1870) |
| Jan Kip - A Prospect of the House at Windsor, Belonging to his Grace Charles Beauclerck - B2017.35.1 - Yale Center for British Art.jpg | 1920 × 1427 | 1707 | staged | 1707; the duke of St Albans' house - the view is locked to standing Windsor Castle |
| Jan Kip - Burlington House in Piccadilly - B1977.14.17783 - Yale Center for British Art.jpg | 1920 × 1400 | — | hand-tied | sources.py KIP: Burlington House (Q225471) |
| Jan Kip - Fair Lawn in ye County of Kent - B2017.35.2 - Yale Center for British Art (cropped).jpg | 982 × 715 | — | drop: duplicate impression | 982 px crop of the hand-tied Fairlawne original (B2017.35.2) |
| Jan Kip - Fair Lawn in ye County of Kent - B2017.35.2 - Yale Center for British Art.jpg | 1920 × 1626 | 1707 | hand-tied | sources.py KIP: Fairlawne (Q17530246) |
| Jan Kip - Lambeth, His Grace the Lord Archbishop of Canterbury Palace - B1977.14.17372 - Yale Center for British Art.jpg | 1920 × 1427 | — | staged | Lambeth Palace stands |
| Jan Kip - Somerset House - B1977.14.18272 - Yale Center for British Art.jpg | 1920 × 1413 | — | staged | part of the old Somerset House complex survives (LSE) |
| Jan Kip - St James^s House, Le Palais Royal de St James - B2017.35.3 - Yale Center for British Art.jpg | 1920 × 1407 | 1707 | staged | 1707; St James's Palace stands |
| Jan Kip - The Danish Church in London - 1696.png | 1894 × 1438 | 1696 | drop: church | the Danish Church, Wellclose Square (demolished 1870) |
| Jan Kip - The House at Chiswick in the County of Middlesex one of the Seats of the Rt Hon Charles Boyle - B1977.14.18672 - Yale Center for British Art.jpg | 1920 × 1386 | 1715 | hand-tied | sources.py KIP: Chiswick House (Q1074877) |
| Jan Kip - The Palace and Park of St James's - B1977.14.18146 - Yale Center for British Art.jpg | 1920 × 1367 | — | staged | St James's Palace and its park stand |
| Jan Kip - The Prospect of Bridewell - B1977.14.17792 - Yale Center for British Art.jpg | 1920 × 1256 | — | drop: not a house | Bridewell (the old London hospital), not a house or garden |
| Jan Kip - The South Prospect of the Church of St Clement's Danes - B1977.14.16033 - Yale Center for British Art.jpg | 1920 × 1407 | — | drop: church | south prospect of St Clement's Danes, London |
| Jan Kip - The Tower of London, Commanded in Chief by the Rt Hon Robert Ld Lucas - B1977.14.18612 - Yale Center for British Art.jpg | 1920 × 1384 | — | drop: not a house | the Tower of London is a fortress, not a house or garden |
| Jan Kip - The Tower of London, Commanded in Chief by the Rt Honorable Robert Ld Lucas - B1977.14.18611 - Yale Center for British Art.jpg | 1920 × 1404 | — | drop: not a house | the Tower of London is a fortress, not a house or garden |
| Jan Kip - View of Beaufort House and Chelsea 1699 - B1977.14.15680 - Yale Center for British Art.jpg | 1920 × 1404 | 1699 | drop: review-queue | the same demolished Chelsea seat (1699 impression) |
| Jan kip per david mortier, hampton court (da leonard mortier), dalla britannia illustrata, 1707.jpg | 2560 × 1912 | 2016-10-26 | staged | clean single-plate impression of the royal Hampton Court palace; palace and parterres stand |
| Johannes Kip after Leendert Knijff, The North Prospect of the New Quadrangle of Christ Church in Oxford, 1707, NGA 200835.jpg | 4000 × 3253 | 1707 | drop: not a house | Oxford NGA print: a cathedral or college quadrangle, not a house |
| Johannes Kip after Leendert Knijff, The South Prospect of the New Quadrangle of Christ Church in Oxford, 1707, NGA 200836.jpg | 4000 × 3263 | 1707 | drop: not a house | Oxford NGA print: a cathedral or college quadrangle, not a house |
| Johannes Kip, after Leendert Knijff, The North Prospect of the Cathedral Church of Oxford, 1707, NGA 200834.jpg | 4000 × 3216 | 1707 | drop: not a house | Oxford NGA print: a cathedral or college quadrangle, not a house |
| Kensington.Palace.by.Kip.1724.jpg | 600 × 379 | 1724 | drop: too small | 600 px impression of the Kensington Palace plate |
| Ki BrymptonInSomersetShire.jpg | 450 × 336 | 5 December 2005 (original upload date) | drop: too small | 450 px impression of the Brympton plate |
| Kingsweston Kip.jpg | 1375 × 1127 | 1710 | staged | Atkyns 1710; the house (rebuilt 1720) and the estate's gardens and trees survive |
| Kip St James's Palace and Park.jpg | 614 × 453 | — | drop: too small | 614 px impression of the St James's plate |
| Kip and Knyff Windsor.jpg | 810 × 596 | — | drop: too small | 810 px impression of the Windsor plate |
| Knole - Britannia Illustrata 1709.JPG | 655 × 482 | 1709 | drop: too small | 655 px impression of the Knole plate |
| Landgoed Badminton, RP-P-1949-371.jpg | 7054 × 5328 | 1709 | staged | BI 9/61 1709; the house and its formal park survive (National Trust) |
| Landschap met fazanten en snippen, RP-P-1894-A-18342.jpg | 6660 × 4764 | between 1662 and 1722 | drop: not a house | a pheasant landscape, no house or garden |
| Londesborough.jpg | 321 × 247 | — | drop: too small | 321 px impression of the Londesborough plate |
| Longleat by Knyff edited.JPG | 361 × 269 | — | drop: too small | 361 px impression of the Longleat plate |
| Map of Amsterdam with the New Plantage by Johannes Kip.jpg | 1803 × 1480 | from 1686 until 1688 | drop: foreign | a plan of Amsterdam, 1686-88 |
| Nibley House, by Kip.jpg | 595 × 486 | circa 1708 | drop: too small | 595 px impression of the Nibley plate |
| Nouveau Theatre de la Grande Bretagne- Ou Description Exacte des Palais de La Reine, et des Maisons les plus considerables...de la Grande Bretagne MET DP105010.jpg | 3979 × 2936 | 1708 | drop: duplicate impression | the Hampton Court palace view photographed as a two-page book spread with gutter; duplicate of the AIC impression |
| Nouveau theatre de la Grande Bretagne- ou description exacte des villes, et palais du Roy, et les ports de mer, etc Fleuron T202131-7.png | 5781 × 1075 | 1729 | drop: not a house | decorative title cartouche (fleuron) of the Nouveau Theatre plate, no view |
| Ogrod2.jpg | 1200 × 900 | 2006 | drop: photo | a 2006 photo of the Branicki Palace parterre (Bialystok, Poland) - not Kip, not UK |
| Portret van Marcello Malpighi, RP-P-1878-A-2155.jpg | 4618 × 6330 | 1694 | drop: not a house | a portrait (Malpighi, Bologna) |
| PowisHousebyKip.jpg | 510 × 473 | — | drop: too small | 510 px impression of the Powis House plate |
| Queen's Chapel Jan Kip 1688.jpg | 730 × 977 | 1688 | drop: church | interior of the Queen's Chapel, St James's Palace |
| Ragleyhall by Kip edited.jpg | 791 × 590 | — | drop: too small | 791 px impression of the Ragley Hall plate |
| Shipton Moyne, by Kip.jpg | 487 × 400 | circa 1708 | drop: too small | 487 px impression of the Shipton Moyne plate |
| Sierra Leone Johannes 1732.jpg | 1020 × 745 | 1732 | drop: foreign | the Bay of Sierra Liona, 1732 |
| Sistoncourtkip.jpg | 822 × 584 | circa 1712 | drop: too small | 822 px impression of the Siston Court plate |
| Somerset House by Kip 1722.JPG | 400 × 296 | 1722 | drop: too small | 400 px impression of the Somerset House plate |
| St James's Palace and The Mall Kip 1715.jpg | 600 × 443 | 1715 | drop: too small | 600 px impression of the St James's plate |
| Stadsarchief Amsterdam, Afb ANWG00357000001.jpg | 4953 × 3606 | circa 1930 | drop: foreign | a c.1930 reproduction of Kip's Amsterdam profile, not a Kip impression |
| StokeGiffordParkByKip.jpg | 482 × 392 | 1724 | drop: too small | 482 px impression (1724 edition) of the Stoke Gifford plate |
| Temple Newsam Kip.jpg | 566 × 419 | — | drop: too small | 566 px impression of the Temple Newsam plate (the Gott 112a impression is the staged one) |
| The Cascade and Wilderness Garden, Shibden Park - geograph.org.uk - 1746869.jpg | 640 × 480 | 2010-01-02 | drop: photo | a 2010 geograph photo of the Shibden Park cascade |
| The South Front Of Ham House Seen From The Wilderness, Richmond - London. (14848176574).jpg | 3792 × 2496 | 2014-08-06 | drop: photo | a 2014 Flickr photo of Ham House (based on a 1675-79 painting) |
| The Statue Of Mercury In Ham House Gardens, Richmond - London. (14847544601).jpg | 3000 × 4000 | 2014-08-06 | drop: photo | a 2014 Flickr photo of a Ham House garden statue |
| The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14561621598).jpg | 1816 × 2826 | 1720 | drop: not a house | emblem plate from The History of Nature (1720), no house or garden |
| The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14745913654).jpg | 1816 × 3226 | 1720 | drop: not a house | emblem plate from The History of Nature (1720), no house or garden |
| The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14747981482).jpg | 1840 × 2868 | 1720 | drop: not a house | emblem plate from The History of Nature (1720), no house or garden |
| The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14748332675).jpg | 1830 × 2820 | 1720 | drop: not a house | emblem plate from The History of Nature (1720), no house or garden |
| The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14768166443).jpg | 1870 × 2908 | 1720 | drop: not a house | emblem plate from The History of Nature (1720), no house or garden |
| The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14768195323).jpg | 2535 × 4143 | 1720 | drop: not a house | emblem plate from The History of Nature (1720), no house or garden |
| Uppark Kip.jpg | 563 × 411 | — | drop: too small | 563 px impression of the Uppark plate |
| Wandelrit van prins Willem III buiten Den Haag (blad linksboven), 1686, RP-P-OB-82.545A.jpg | 7046 × 5498 | 1686 | drop: foreign | the 1686 Den Haag carriage-ride panorama (six plates) |
| Wandelrit van prins Willem III buiten Den Haag (blad linksonder), 1686, RP-P-OB-82.545D.jpg | 7028 × 5432 | 1686 | drop: foreign | the 1686 Den Haag carriage-ride panorama (six plates) |
| Wandelrit van prins Willem III buiten Den Haag (blad middenboven), 1686, RP-P-OB-82.545B.jpg | 7114 × 5500 | 1686 | drop: foreign | the 1686 Den Haag carriage-ride panorama (six plates) |
| Wandelrit van prins Willem III buiten Den Haag (blad middenonder), 1686, RP-P-OB-82.545E.jpg | 7018 × 5424 | 1686 | drop: foreign | the 1686 Den Haag carriage-ride panorama (six plates) |
| Wandelrit van prins Willem III buiten Den Haag (blad rechtsboven), 1686, RP-P-OB-82.545C.jpg | 7142 × 5506 | 1686 | drop: foreign | the 1686 Den Haag carriage-ride panorama (six plates) |
| Wandelrit van prins Willem III buiten Den Haag, 1686, RP-P-OB-82.545.jpg | 7006 × 5426 | 1686 | drop: foreign | the 1686 Den Haag carriage-ride panorama (six plates) |
| WansteadPre1715.jpg | 492 × 337 | 11 June 2010 (original upload date) | drop: too small | 492 px detail of the Wanstead plate |
| West prospect of Gloucester by Kip, c.1725..jpg | 1065 × 865 | circa 1725 | drop: city prospect | a c.1725 prospect of Gloucester, a city view |
| Wilderness Garden, Witley Court.jpg | 2048 × 1536 | 2011-06-03 | drop: photo | a 2011 photo of the Witley Court wilderness garden |
| Wimpole Kip and Knyff edited.jpg | 389 × 275 | — | drop: too small | 389 px impression of the Wimpole plate |
| Windsor Kip and Knyff trimmed.jpg | 757 × 210 | 2010-11-14 | drop: too small | 757 px trimmed impression of the Windsor plate |

### The 22 relevant views: their captions (the evidence the staged rows will carry)

One line per view whose verdict is staged, hand-tied or review-queue. The caption is the file's `ImageDescription` where Commons has one (truncated here; full text in the `--list` dump); the Yale files carry no description, so their named place is in the title itself.

- **An engraving of Chevening by Johannes Kip (d.1722) after Thomas Badeslade (d.1742), published (in History of Kent) 1719 by John Harris.jpg** (hand-tied): My photograph ( Rodolph  ( talk ) 01:30, 13 March 2014 (UTC)) of an engraving of Chevening by Johannes Kip (d.1722) after Thomas Badeslade (d.1742), published (in History of Kent) 1719 by John Harris. ( w:Jan Kip , (1652…
- **Beaufort House, Chelsea from the series Britannia Illustrata 2020.163.jpg** (drop: review-queue): (no description; the named place is in the title)
- **Cassiobury Park by Kip and Knyff.jpg** (hand-tied): (no description; the named place is in the title)
- **Gezicht op Hampton Court, RP-P-1905-194.jpg** (hand-tied): Identificatie    Titel(s):  Gezicht op Hampton Court Hampton Court in Herefordfhire the Seat of the R.t Hon.ble: Tho: Lord Coningesby Baron of Clanbrazell in the Kingdom of Ireland (titel op object) Britannia Illustrata …
- **Gezicht op Stanway, RP-P-1949-369.jpg** (staged): Identificatie    Titel(s):  Gezicht op Stanway Stanway the seat of John Tracey Esq (titel op object) Britannia Illustrata (serietitel)  Objecttype:  prent   Serienummer:  49/61  Objectnummer:  RP-P-1949-369  Catalogusref…
- **Gezicht op Stoke Bishop, RP-P-1949-367.jpg** (staged): Identificatie    Titel(s):  Gezicht op Stoke Bishop Stoke Bishop the seat of Sr. Thomas Cann (titel op object) Britannia Illustrata (serietitel)  Objecttype:  prent   Serienummer:  52/61  Objectnummer:  RP-P-1949-367  Ca…
- **Gezicht op Stoke Gifford, RP-P-1949-368.jpg** (drop: review-queue): Identificatie    Titel(s):  Gezicht op Stoke Gifford Stoke Gifford The Seat of John Berkeley Esq (titel op object) Britannia Illustrata (serietitel)  Objecttype:  prent   Serienummer:  50/61  Objectnummer:  RP-P-1949-368…
- **Gott Collection at Hepworth Gallery (112a).JPG** (staged): Part of the Gott Collection at the Hepworth Gallery, Wakefield, West Yorkshire, England. The collection was originally held by Leeds industrialist William Gott, and sold in 1908 and 1912 after the 1906 death of William G…
- **Gott Collection at Hepworth Gallery (80a).JPG** (drop: review-queue): Part of the Gott Collection at the Hepworth Gallery, Wakefield, West Yorkshire, England. The collection was originally held by Leeds industrialist William Gott, and sold in 1908 and 1912 after the 1906 death of William G…
- **Hutton Hall Kip.jpg** (staged): Hutton-in-the-Forest Hall, seat of  w:Sir George Fletcher, 2nd Baronet  (1633–1700), drawn by Kniff, engraved by Kip, published 1709. Showing arms of Fletcher impaling Hare, for his first wife Alice Hare, daughter of Hug…
- **Jan Kip - A Prospect of the House at Windsor, Belonging to his Grace Charles Beauclerck - B2017.35.1 - Yale Center for British Art.jpg** (staged): (no description; the named place is in the title)
- **Jan Kip - Burlington House in Piccadilly - B1977.14.17783 - Yale Center for British Art.jpg** (hand-tied): (no description; the named place is in the title)
- **Jan Kip - Fair Lawn in ye County of Kent - B2017.35.2 - Yale Center for British Art.jpg** (hand-tied): (no description; the named place is in the title)
- **Jan Kip - Lambeth, His Grace the Lord Archbishop of Canterbury Palace - B1977.14.17372 - Yale Center for British Art.jpg** (staged): (no description; the named place is in the title)
- **Jan Kip - Somerset House - B1977.14.18272 - Yale Center for British Art.jpg** (staged): (no description; the named place is in the title)
- **Jan Kip - St James^s House, Le Palais Royal de St James - B2017.35.3 - Yale Center for British Art.jpg** (staged): (no description; the named place is in the title)
- **Jan Kip - The House at Chiswick in the County of Middlesex one of the Seats of the Rt Hon Charles Boyle - B1977.14.18672 - Yale Center for British Art.jpg** (hand-tied): (no description; the named place is in the title)
- **Jan Kip - The Palace and Park of St James's - B1977.14.18146 - Yale Center for British Art.jpg** (staged): (no description; the named place is in the title)
- **Jan Kip - View of Beaufort House and Chelsea 1699 - B1977.14.15680 - Yale Center for British Art.jpg** (drop: review-queue): (no description; the named place is in the title)
- **Jan kip per david mortier, hampton court (da leonard mortier), dalla britannia illustrata, 1707.jpg** (staged): European prints in the Art Institute of Chicago
- **Kingsweston Kip.jpg** (staged): Birds-eye view of the Kingsweston estate from  The Ancient and Present State of Glocestershire , first published 1710
- **Landgoed Badminton, RP-P-1949-371.jpg** (staged): Identificatie    Titel(s):  Landgoed Badminton Badminton in the Country of Gloucester one of the Seats of the Most Noble & Potent Prince Henry Duke of Beaufort, Marquesse & Earle of Worcester (titel op object) Britannia …

## 4. Staged vs verified large-scan views (the half-or-more check)

_(pending - sessions 2-3, once §2's QID verification is done.)_ Expected: 22 verified large-scan UK house/garden views in the inventory = 6 hand-tied + 12 staged + 4 review-queue; 12 of 22 are staged (≥ half), and every view that is not staged is named in §3 with its verified reason, so the box is met.
