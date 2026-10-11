"""Johannes Kip's (and Kip & Knyff's) bird's-eye views of UK country houses and their formal gardens
(task 205, GOAL.md point 4): the large scans in the Commons categories "Johannes Kip" (root + its
5 subcategories) and "Britannia Illustrata" - 132 distinct files, every one given a verdict in
INVENTORY. This module stages the fit-sized (long edge >= 1000 px) house/garden views into THIS
task's own staging files - one picture row per staged view (the files.jsonl shape + 200's
evidence field, kind caption_coords from the view's own caption, by "fit/src_kip.py"), one
hand classification (p_birdseye 1.0) and one new "garden" site row per view whose fixed landmark
(the house, the garden's axes, the park) can carry a fit - and 211 consolidates and builds.

The six views already hand-tied in pipeline/sources.py (KIP) are NOT re-staged: their evidence
kind stays "hand-tied QID". The Hampton Court trap applies to every candidate: the place is what
the CAPTION says (the Rijksmuseum's "Gezicht op Hampton Court" is in Herefordshire, not the
palace on the Thames). A view whose house is gone and nothing fixed remains on the ground is a
review-queue candidate recorded in docs/lead_kip.md (201 owns the queue), never a new site.
"Britannia Illustrata" (1707-09) and Kip's later plates (e.g. in Harris's History of Kent) are the
same kind of material: one row per picture, never per book.

usage: src_kip.py --list [--out FILE]   live (paced): list every file of the lead categories with
                                        its metadata; assert the live set and sizes against
                                        INVENTORY (the committed 132-row table; a renamed,
                                        re-filed or replaced file fails loud); JSON lines to FILE (stdout if omitted)
       src_kip.py --verify               live: re-verify every SITES entry (the 8 QID-bearing: Wikidata label,
                                        every P625 value vs the landmark point, P373, P131, enwiki, the first
                                        name-search hit with coordinates - what record --live would resolve; the 3
                                        without a QID: the stored source note) plus the known_sites() collision
                                        check; exits 1 on a collision, a >50 km P625 flag or a missing item
       src_kip.py [--dry]                stage the table rows into the staging files
       src_kip.py --check                offline (no network): join the staged files, run
                                        fit/evidence.py's check over every staged row
       src_kip.py --golden               write tests/golden/src_kip_sample.json

Staging writes only this task's files (append-only, idempotent on (site, title)). The system
python3 has no numpy (commons -> aw), so the live commands run under .venv/bin/python; the module
top stays stdlib-only (lazy imports, the fit/src_artists.py pattern).
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

EXTRAS_KIP = os.path.join(ROOT, "data", "catalog", "extras_kip.jsonl")
FILES_KIP = os.path.join(ROOT, "data", "commons", "files_kip.jsonl")
CLASSIFIED_KIP = os.path.join(ROOT, "data", "commons", "classified_kip.jsonl")
SITES_JSONL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
EXTRAS = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
WEB_SITES = os.path.join(ROOT, "web", "data", "sites.json")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

# The lead categories (verified live 2026-10-10, one paced read-only run; list_files() re-checks the
# root's subcategory set every run so a re-filed or renamed category fails loud). Out of scope,
# checked and recorded in docs/lead_kip.md: Category:Jan Kip (5 files, all photos of the artist or
# a 1953 flood - no prints) and Category:History of Kent (29 files, all non-Kip).
CATS = ["Johannes Kip",
        "Britannia Illustrata",
        "Prints by Johannes Kip in the Rijksmuseum Amsterdam",
        "The Ancient and Present State of Glocestershire",
        "The history of nature, 1720",
        "Wilderness (garden history)"]

# Fit-sized = long edge >= 1000 px: the smallest staged view (Kingsweston) is 1375 px, the largest
# drop (the 982 px Fairlawne crop) is 63 px below the threshold, and nothing in the lead categories
# falls in 900-1000 px, so the cut needs no exception list (docs/lead_kip.md).
MIN_EDGE = 1000

# The verdicts: "staged" (a staging row goes into this task's files) / "hand-tied" (one of the six
# already in the canonical files - never re-staged) / "drop: <group>" (a documented drop, reason in
# docs/lead_kip.md). INVENTORY is (title, w, h, verdict, reason): the live list_files() run asserts
# the live set and the sizes against it, so a renamed, re-filed or replaced file fails loud.
INVENTORY = [
    ('File:(Chart of part of the Coast of Sierra Leone and Liberia from Los Islands (Guinea) to River Cess (Liberia)) RMG F0418.tiff', 7165, 5818, 'drop: foreign', "a 1732 chart of the Sierra Leone coast (from Kip's Guinea book)"),
    ('File:+++Toddington Manor, by Kip (detail).jpg', 638, 456, 'drop: too small', '638 px detail of the Toddington plate'),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268744.jpg", 1955, 1414, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268745.jpg", 1957, 1405, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268746.jpg", 1955, 1405, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268747.jpg", 1957, 1395, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268748.jpg", 1957, 1396, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268749.jpg", 1955, 1418, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268750.jpg", 1957, 1412, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268751.jpg", 1957, 1404, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268752.jpg", 1957, 1425, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ("File:A Prospect of the City of London, Westminster and St. James' Park MET DP268753.jpg", 1957, 1415, 'drop: city prospect', "one of the MET's ten impressions of the 1710 London city prospect"),
    ('File:AMH-8134-KB Map of part of the west coast of Africa, with an inset showing the coast of Sierra Leone.jpg', 2400, 1783, 'drop: foreign', 'a 1732 map of the west coast of Africa (Sierra Leone inset)'),
    ('File:AlvestonCourtKipCol2.jpg', 401, 338, 'drop: too small', '401 px impression of the Alveston Court plate'),
    ('File:An engraving of Chevening by Johannes Kip (d.1722) after Thomas Badeslade (d.1742), published (in History of Kent) 1719 by John Harris.jpg', 2112, 1743, 'hand-tied', 'sources.py KIP: Chevening (Q1070927)'),
    ('File:Beaufort House Kip 1708.jpg', 700, 513, 'drop: too small', '700 px impression of the Chelsea seat plate'),
    ('File:Beaufort House, Chelsea from the series Britannia Illustrata 2020.163.jpg', 3400, 2455, 'drop: review-queue', 'Beaufort House (Chelsea) demolished 1739-40; nothing fixed remains on the ground'),
    ('File:Berkley Castle by Jan Kip 1712.jpg', 452, 364, 'drop: too small', '452 px impression of the Berkeley Castle plate'),
    ('File:Birdseye view of Chatsworth in 1699.jpg', 800, 592, 'drop: too small', '800 px impression of the Chatsworth plate'),
    ('File:Cassiobury Park by Kip and Knyff.jpg', 3231, 2330, 'hand-tied', 'sources.py KIP: Cassiobury House (Q5049456)'),
    ('File:Cassiobury-1707.jpg', 582, 400, 'drop: too small', '582 px impression from the French edition (Les delices)'),
    ('File:ClearwellByKip.png', 452, 362, 'drop: too small', '452 px impression of the Clearwell plate'),
    ('File:Coley Park, 1700-1709 by L. Knyff.jpg', 682, 569, 'drop: too small', '682 px impression of the Coley Park plate'),
    ('File:Colombo, after Kip.jpg', 973, 657, 'drop: foreign', 'Colombo (Ceylon), after a c.1680 Kip engraving'),
    ('File:Combe Abbey Brit Ill.jpg', 502, 378, 'drop: too small', '502 px impression of the Combe Abbey plate'),
    ('File:Dam in Amsterdam, RP-P-OB-47.598.jpg', 7868, 5404, 'drop: foreign', 'Amsterdam (the Dam), 1685'),
    ('File:Didmarton, by Kip.jpg', 610, 496, 'drop: too small', '610 px impression of the Didmarton plate'),
    ('File:Dumbleton, by Kip.jpg', 458, 400, 'drop: too small', '458 px impression of the Dumbleton plate'),
    ('File:Eaton Hall by Kip 1708 edited.jpg', 595, 430, 'drop: too small', '595 px impression of the Eaton Hall plate'),
    ('File:Flaxley Abbey Kip.jpg', 540, 475, 'drop: too small', '540 px impression of the Flaxley Abbey plate'),
    ('File:Garden at Ham House, Surrey - geograph.org.uk - 2042063.jpg', 3872, 2592, 'drop: photo', 'a 2010 geograph photo of the Ham House garden'),
    ('File:Gezicht op Amsterdam vanaf het IJ, RP-P-2019-2636.jpg', 5746, 4456, 'drop: foreign', 'Amsterdam from the IJ (one of a six-plate panorama)'),
    ('File:Gezicht op Hampton Court, RP-P-1905-194.jpg', 7032, 5258, 'hand-tied', 'sources.py KIP: Hampton Court, Herefordshire (Q1443802)'),
    ('File:Gezicht op Musschat, RP-P-1905-3935.jpg', 6856, 4686, 'drop: foreign', 'Muscot (Arabia), 1682'),
    ('File:Gezicht op Stanway, RP-P-1949-369.jpg', 6140, 5562, 'staged', 'BI 49/61 1709; the Jacobean manor (Charteris) and its baroque water gardens survive'),
    ('File:Gezicht op Stoke Bishop, RP-P-1949-367.jpg', 7018, 5576, 'staged', 'BI 52/61 1709; the Cann seat at Stoke Bishop still stands (rebuilt c.1765-73)'),
    ('File:Gezicht op Stoke Gifford, RP-P-1949-368.jpg', 6486, 5318, 'drop: review-queue', 'the seat was rebuilt 1750 (Wright) and is lost; the estate built over; house survival unverified'),
    ('File:Gezicht op Tegepatnam, een Moors kasteel en de Nederlandse loge, RP-P-1935-790.jpg', 6762, 4582, 'drop: foreign', 'Tegnapatnam (Kormandel coast), 1676'),
    ("File:Gezicht op de kapel van King's College, Cambridge (linkerdeel), RP-P-2018-833.jpg", 5162, 6408, 'drop: church', "King's College Chapel, Cambridge (left half)"),
    ("File:Gezicht op de kapel van King's College, Cambridge (rechterdeel), RP-P-2018-834.jpg", 5428, 6478, 'drop: church', "King's College Chapel, Cambridge (right half)"),
    ("File:Gezicht op de kapel van King's College, Cambridge, bestaande uit twee delen, RP-P-2018-832.jpg", 10326, 6390, 'drop: church', "King's College Chapel, Cambridge (the two-part plate)"),
    ('File:Gezicht op de stad Cranganoor, RP-P-OB-47.597.jpg', 7044, 4764, 'drop: foreign', 'Cranganore (Malabar coast), 1676'),
    ('File:Gezicht op eiland en Kasteel Tenos, RP-P-1905-3936.jpg', 6820, 4670, 'drop: foreign', 'Tennore island and castle (Malabar), 1682'),
    ('File:Gezicht op het eiland Ternate, RP-P-OB-47.595.jpg', 7080, 4780, 'drop: foreign', 'Ternate (Moluccas), 1682'),
    ('File:Gezicht op het landgoed Badminton, RP-P-1949-370.jpg', 7010, 5310, 'drop: duplicate impression', 'same plate as Landgoed Badminton RP-P-1949-371 (the staged impression)'),
    ('File:Gott Collection at Hepworth Gallery (112a).JPG', 3576, 2700, 'staged', 'the full Temple Newsam plate; the house still stands (National Trust)'),
    ('File:Gott Collection at Hepworth Gallery (113a).JPG', 2796, 2176, 'drop: duplicate impression', 'detail crop of the Temple Newsam plate (112a is the staged impression)'),
    ('File:Gott Collection at Hepworth Gallery (114).JPG', 4000, 3000, 'drop: duplicate impression', 'detail crop of the Temple Newsam plate (112a is the staged impression)'),
    ('File:Gott Collection at Hepworth Gallery (115).JPG', 4000, 3000, 'drop: duplicate impression', 'detail crop of the Temple Newsam plate (112a is the staged impression)'),
    ('File:Gott Collection at Hepworth Gallery (31).JPG', 3576, 2448, 'drop: not a house', "Sedbergh School master's-house plans - a school, not a country house"),
    ('File:Gott Collection at Hepworth Gallery (32).jpg', 3592, 1976, 'drop: not a house', 'Sedbergh School plans - a school, not a country house'),
    ('File:Gott Collection at Hepworth Gallery (33).JPG', 2616, 1708, 'drop: not a house', 'Sedbergh School engraving (authorship detail) - a school, not a country house'),
    ('File:Gott Collection at Hepworth Gallery (80a).JPG', 3328, 2468, 'drop: review-queue', 'Swillington Hall (Lowther) demolished 1952 (mineworkings); no fixed landmark remains'),
    ('File:Gott Collection at Hepworth Gallery (81).JPG', 3000, 4000, 'drop: duplicate impression', 'detail crop of the Swillington plate (80a is the review-queue impression)'),
    ('File:Gott Collection at Hepworth Gallery (82a).JPG', 3792, 2732, 'drop: duplicate impression', 'detail crop of the Swillington plate (80a is the review-queue impression)'),
    ('File:Gott Collection at Hepworth Gallery (83a).JPG', 3564, 2496, 'drop: duplicate impression', 'detail crop of the Swillington plate (80a is the review-queue impression)'),
    ('File:Gott Collection at Hepworth Gallery (84).JPG', 4000, 3000, 'drop: duplicate impression', 'detail crop of the Swillington plate (80a is the review-queue impression)'),
    ('File:Gott Collection at Hepworth Gallery (85).JPG', 4000, 3000, 'drop: duplicate impression', 'detail crop of the Swillington plate (80a is the review-queue impression)'),
    ('File:Ham House 05.JPG', 2592, 1944, 'drop: photo', 'a 2011 photo of Ham House'),
    ('File:Ham House London 04.JPG', 1944, 2592, 'drop: photo', 'a 2011 photo of Ham House'),
    ('File:Hampton Court Key.jpg', 781, 537, 'drop: too small', '781 px plan (key) of Hampton Court Palace'),
    ('File:HamptonCourtKipKnyff1708.jpg', 643, 475, 'drop: too small', '643 px impression of the Herefordshire Hampton Court plate'),
    ('File:Henbury, by Kip.jpg', 595, 484, 'drop: too small', '595 px impression of the Henbury plate'),
    ('File:Hutton Hall Kip.jpg', 3796, 2739, 'staged', 'BI 1709; the Cumbrian Fletcher seat still stands (Grade I: pele tower, 1680 hall, walled garden)'),
    ('File:Interieur van de Deense Kerk te Londen, RP-P-1911-286.jpg', 5098, 7288, 'drop: church', 'interior of the Danish Church, London (demolished 1870)'),
    ('File:Jan Kip - A Prospect of the House at Windsor, Belonging to his Grace Charles Beauclerck - B2017.35.1 - Yale Center for British Art.jpg', 1920, 1427, 'staged', "1707; the duke of St Albans' house - the view is locked to standing Windsor Castle"),
    ('File:Jan Kip - Burlington House in Piccadilly - B1977.14.17783 - Yale Center for British Art.jpg', 1920, 1400, 'hand-tied', 'sources.py KIP: Burlington House (Q225471)'),
    ('File:Jan Kip - Fair Lawn in ye County of Kent - B2017.35.2 - Yale Center for British Art (cropped).jpg', 982, 715, 'drop: duplicate impression', '982 px crop of the hand-tied Fairlawne original (B2017.35.2)'),
    ('File:Jan Kip - Fair Lawn in ye County of Kent - B2017.35.2 - Yale Center for British Art.jpg', 1920, 1626, 'hand-tied', 'sources.py KIP: Fairlawne (Q17530246)'),
    ('File:Jan Kip - Lambeth, His Grace the Lord Archbishop of Canterbury Palace - B1977.14.17372 - Yale Center for British Art.jpg', 1920, 1427, 'staged', 'Lambeth Palace stands'),
    ('File:Jan Kip - Somerset House - B1977.14.18272 - Yale Center for British Art.jpg', 1920, 1413, 'staged', 'part of the old Somerset House complex survives (LSE)'),
    ('File:Jan Kip - St James^s House, Le Palais Royal de St James - B2017.35.3 - Yale Center for British Art.jpg', 1920, 1407, 'staged', "1707; St James's Palace stands"),
    ('File:Jan Kip - The Danish Church in London - 1696.png', 1894, 1438, 'drop: church', 'the Danish Church, Wellclose Square (demolished 1870)'),
    ('File:Jan Kip - The House at Chiswick in the County of Middlesex one of the Seats of the Rt Hon Charles Boyle - B1977.14.18672 - Yale Center for British Art.jpg', 1920, 1386, 'hand-tied', 'sources.py KIP: Chiswick House (Q1074877)'),
    ("File:Jan Kip - The Palace and Park of St James's - B1977.14.18146 - Yale Center for British Art.jpg", 1920, 1367, 'staged', "St James's Palace and its park stand"),
    ('File:Jan Kip - The Prospect of Bridewell - B1977.14.17792 - Yale Center for British Art.jpg', 1920, 1256, 'drop: not a house', 'Bridewell (the old London hospital), not a house or garden'),
    ("File:Jan Kip - The South Prospect of the Church of St Clement's Danes - B1977.14.16033 - Yale Center for British Art.jpg", 1920, 1407, 'drop: church', "south prospect of St Clement's Danes, London"),
    ('File:Jan Kip - The Tower of London, Commanded in Chief by the Rt Hon Robert Ld Lucas - B1977.14.18612 - Yale Center for British Art.jpg', 1920, 1384, 'drop: not a house', 'the Tower of London is a fortress, not a house or garden'),
    ('File:Jan Kip - The Tower of London, Commanded in Chief by the Rt Honorable Robert Ld Lucas - B1977.14.18611 - Yale Center for British Art.jpg', 1920, 1404, 'drop: not a house', 'the Tower of London is a fortress, not a house or garden'),
    ('File:Jan Kip - View of Beaufort House and Chelsea 1699 - B1977.14.15680 - Yale Center for British Art.jpg', 1920, 1404, 'drop: review-queue', 'the same demolished Chelsea seat (1699 impression)'),
    ('File:Jan kip per david mortier, hampton court (da leonard mortier), dalla britannia illustrata, 1707.jpg', 2560, 1912, 'staged', 'clean single-plate impression of the royal Hampton Court palace; palace and parterres stand'),
    ('File:Johannes Kip after Leendert Knijff, The North Prospect of the New Quadrangle of Christ Church in Oxford, 1707, NGA 200835.jpg', 4000, 3253, 'drop: not a house', 'Oxford NGA print: a cathedral or college quadrangle, not a house'),
    ('File:Johannes Kip after Leendert Knijff, The South Prospect of the New Quadrangle of Christ Church in Oxford, 1707, NGA 200836.jpg', 4000, 3263, 'drop: not a house', 'Oxford NGA print: a cathedral or college quadrangle, not a house'),
    ('File:Johannes Kip, after Leendert Knijff, The North Prospect of the Cathedral Church of Oxford, 1707, NGA 200834.jpg', 4000, 3216, 'drop: not a house', 'Oxford NGA print: a cathedral or college quadrangle, not a house'),
    ('File:Kensington.Palace.by.Kip.1724.jpg', 600, 379, 'drop: too small', '600 px impression of the Kensington Palace plate'),
    ('File:Ki BrymptonInSomersetShire.jpg', 450, 336, 'drop: too small', '450 px impression of the Brympton plate'),
    ('File:Kingsweston Kip.jpg', 1375, 1127, 'staged', "Atkyns 1710; the house (rebuilt 1720) and the estate's gardens and trees survive"),
    ("File:Kip St James's Palace and Park.jpg", 614, 453, 'drop: too small', "614 px impression of the St James's plate"),
    ('File:Kip and Knyff Windsor.jpg', 810, 596, 'drop: too small', '810 px impression of the Windsor plate'),
    ('File:Knole - Britannia Illustrata 1709.JPG', 655, 482, 'drop: too small', '655 px impression of the Knole plate'),
    ('File:Landgoed Badminton, RP-P-1949-371.jpg', 7054, 5328, 'staged', 'BI 9/61 1709; the house and its formal park survive (National Trust)'),
    ('File:Landschap met fazanten en snippen, RP-P-1894-A-18342.jpg', 6660, 4764, 'drop: not a house', 'a pheasant landscape, no house or garden'),
    ('File:Londesborough.jpg', 321, 247, 'drop: too small', '321 px impression of the Londesborough plate'),
    ('File:Longleat by Knyff edited.JPG', 361, 269, 'drop: too small', '361 px impression of the Longleat plate'),
    ('File:Map of Amsterdam with the New Plantage by Johannes Kip.jpg', 1803, 1480, 'drop: foreign', 'a plan of Amsterdam, 1686-88'),
    ('File:Nibley House, by Kip.jpg', 595, 486, 'drop: too small', '595 px impression of the Nibley plate'),
    ('File:Nouveau Theatre de la Grande Bretagne- Ou Description Exacte des Palais de La Reine, et des Maisons les plus considerables...de la Grande Bretagne MET DP105010.jpg', 3979, 2936, 'drop: duplicate impression', 'the Hampton Court palace view photographed as a two-page book spread with gutter; duplicate of the AIC impression'),
    ('File:Nouveau theatre de la Grande Bretagne- ou description exacte des villes, et palais du Roy, et les ports de mer, etc Fleuron T202131-7.png', 5781, 1075, 'drop: not a house', 'decorative title cartouche (fleuron) of the Nouveau Theatre plate, no view'),
    ('File:Ogrod2.jpg', 1200, 900, 'drop: photo', 'a 2006 photo of the Branicki Palace parterre (Bialystok, Poland) - not Kip, not UK'),
    ('File:Portret van Marcello Malpighi, RP-P-1878-A-2155.jpg', 4618, 6330, 'drop: not a house', 'a portrait (Malpighi, Bologna)'),
    ('File:PowisHousebyKip.jpg', 510, 473, 'drop: too small', '510 px impression of the Powis House plate'),
    ("File:Queen's Chapel Jan Kip 1688.jpg", 730, 977, 'drop: church', "interior of the Queen's Chapel, St James's Palace"),
    ('File:Ragleyhall by Kip edited.jpg', 791, 590, 'drop: too small', '791 px impression of the Ragley Hall plate'),
    ('File:Shipton Moyne, by Kip.jpg', 487, 400, 'drop: too small', '487 px impression of the Shipton Moyne plate'),
    ('File:Sierra Leone Johannes 1732.jpg', 1020, 745, 'drop: foreign', 'the Bay of Sierra Liona, 1732'),
    ('File:Sistoncourtkip.jpg', 822, 584, 'drop: too small', '822 px impression of the Siston Court plate'),
    ('File:Somerset House by Kip 1722.JPG', 400, 296, 'drop: too small', '400 px impression of the Somerset House plate'),
    ("File:St James's Palace and The Mall Kip 1715.jpg", 600, 443, 'drop: too small', "600 px impression of the St James's plate"),
    ('File:Stadsarchief Amsterdam, Afb ANWG00357000001.jpg', 4953, 3606, 'drop: foreign', "a c.1930 reproduction of Kip's Amsterdam profile, not a Kip impression"),
    ('File:StokeGiffordParkByKip.jpg', 482, 392, 'drop: too small', '482 px impression (1724 edition) of the Stoke Gifford plate'),
    ('File:Temple Newsam Kip.jpg', 566, 419, 'drop: too small', '566 px impression of the Temple Newsam plate (the Gott 112a impression is the staged one)'),
    ('File:The Cascade and Wilderness Garden, Shibden Park - geograph.org.uk - 1746869.jpg', 640, 480, 'drop: photo', 'a 2010 geograph photo of the Shibden Park cascade'),
    ('File:The South Front Of Ham House Seen From The Wilderness, Richmond - London. (14848176574).jpg', 3792, 2496, 'drop: photo', 'a 2014 Flickr photo of Ham House (based on a 1675-79 painting)'),
    ('File:The Statue Of Mercury In Ham House Gardens, Richmond - London. (14847544601).jpg', 3000, 4000, 'drop: photo', 'a 2014 Flickr photo of a Ham House garden statue'),
    ("File:The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14561621598).jpg", 1816, 2826, 'drop: not a house', 'emblem plate from The History of Nature (1720), no house or garden'),
    ("File:The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14745913654).jpg", 1816, 3226, 'drop: not a house', 'emblem plate from The History of Nature (1720), no house or garden'),
    ("File:The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14747981482).jpg", 1840, 2868, 'drop: not a house', 'emblem plate from The History of Nature (1720), no house or garden'),
    ("File:The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14748332675).jpg", 1830, 2820, 'drop: not a house', 'emblem plate from The History of Nature (1720), no house or garden'),
    ("File:The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14768166443).jpg", 1870, 2908, 'drop: not a house', 'emblem plate from The History of Nature (1720), no house or garden'),
    ("File:The history of nature, in two parts - emblematically express'd in near a hundred folio copper-plates - wherein are also represented all the operations, facultys, and passions of the mind, &c. (14768195323).jpg", 2535, 4143, 'drop: not a house', 'emblem plate from The History of Nature (1720), no house or garden'),
    ('File:Uppark Kip.jpg', 563, 411, 'drop: too small', '563 px impression of the Uppark plate'),
    ('File:Wandelrit van prins Willem III buiten Den Haag (blad linksboven), 1686, RP-P-OB-82.545A.jpg', 7046, 5498, 'drop: foreign', 'the 1686 Den Haag carriage-ride panorama (six plates)'),
    ('File:Wandelrit van prins Willem III buiten Den Haag (blad linksonder), 1686, RP-P-OB-82.545D.jpg', 7028, 5432, 'drop: foreign', 'the 1686 Den Haag carriage-ride panorama (six plates)'),
    ('File:Wandelrit van prins Willem III buiten Den Haag (blad middenboven), 1686, RP-P-OB-82.545B.jpg', 7114, 5500, 'drop: foreign', 'the 1686 Den Haag carriage-ride panorama (six plates)'),
    ('File:Wandelrit van prins Willem III buiten Den Haag (blad middenonder), 1686, RP-P-OB-82.545E.jpg', 7018, 5424, 'drop: foreign', 'the 1686 Den Haag carriage-ride panorama (six plates)'),
    ('File:Wandelrit van prins Willem III buiten Den Haag (blad rechtsboven), 1686, RP-P-OB-82.545C.jpg', 7142, 5506, 'drop: foreign', 'the 1686 Den Haag carriage-ride panorama (six plates)'),
    ('File:Wandelrit van prins Willem III buiten Den Haag, 1686, RP-P-OB-82.545.jpg', 7006, 5426, 'drop: foreign', 'the 1686 Den Haag carriage-ride panorama (six plates)'),
    ('File:WansteadPre1715.jpg', 492, 337, 'drop: too small', '492 px detail of the Wanstead plate'),
    ('File:West prospect of Gloucester by Kip, c.1725..jpg', 1065, 865, 'drop: city prospect', 'a c.1725 prospect of Gloucester, a city view'),
    ('File:Wilderness Garden, Witley Court.jpg', 2048, 1536, 'drop: photo', 'a 2011 photo of the Witley Court wilderness garden'),
    ('File:Wimpole Kip and Knyff edited.jpg', 389, 275, 'drop: too small', '389 px impression of the Wimpole plate'),
    ('File:Windsor Kip and Knyff trimmed.jpg', 757, 210, 'drop: too small', '757 px trimmed impression of the Windsor plate'),
]


# Hand-verified site facts (verified 2026-10-13, --verify re-checks; docs/lead_kip.md §2 records the checked date
# and the per-site notes). Keyed by site id, since 3 of the 11 have no Wikidata item at all (qid None; the model
# handles it - 42 of the 78 extras.jsonl rows carry no qid). id = name slug for those three, name slug + "-" +
# qid-lower for the rest (the pipeline/sources.py rule, as in the six hand-tied: chevening-q1070927). kind
# "garden" builds with the 1600 m box (build_catalog.BOX), aerial_ok from the aerial without LiDAR. The lon/lat
# is the fixed landmark that carries the fit (the house, the palace, the park) - never the QID's municipality
# point (the Gouda 800 m lesson). The view's age (c. 1696-1725) is recorded per row by stage(); views are exempt
# from the 150-year survey rule, recorded anyway. The six hand-tied sites (pipeline/sources.py KIP) are NOT here:
# their rows are never re-staged (their evidence kind stays hand_tied).
SITES = {
    "badminton-house-q2628510": dict(qid="Q2628510", name="Badminton House", lon=-2.28045, lat=51.5455,
        place="Wiltshire", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Badminton_House",
        note="1709 Britannia Illustrata plate ('one of the Seats of the Most Noble & Potent Prince Henry Duke of "
             "Beaufort'); the house and its formal park survive (National Trust); the second impression "
             "(RP-P-1949-370) is the documented duplicate drop; the point is the house's P625"),
    "temple-newsam-q2748017": dict(qid="Q2748017", name="Temple Newsam", lon=-1.4595, lat=53.7842,
        place="North Yorkshire", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Temple_Newsam",
        note="Britannia Illustrata plate 42, 1707-09 ('the Seat of the Rt. Hon. ble Arthur Lord Ingram Viscount "
             "Irwin'); the house survives (National Trust). The Commons description is Hepworth boilerplate with "
             "no place name and the file's MediaInfo item carries no P180 from this VM (checked 2026-10-13, also "
             "on a file with a rich item), so the staged row's desc is enriched with the plate's own printed title "
             "(verified against the British Museum M,21.42 and five other sources); the point is the house's P625"),
    "hutton-hall-q5951100": dict(qid="Q5951100", name="Hutton Hall", lon=-2.839, lat=54.714,
        place="Cumbria", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Hutton_in_the_Forest",
        note="1709 Britannia Illustrata plate ('Hutton-in-the-Forest Hall, seat of Sir George Fletcher'); the "
             "Cumbrian Fletcher-Vane seat (pele tower, 1680 hall, 1730s walled garden, all Grade I) - NOT the "
             "Derbyshire parish of the same name; the point is the house's P625"),
    "stanway-house-q7600303": dict(qid="Q7600303", name="Stanway House", lon=-1.9122, lat=51.9899,
        place="Gloucestershire", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Stanway_House",
        note="1709 Britannia Illustrata plate ('the seat of John Tracey Esq'); the Jacobean manor and its baroque "
             "water gardens survive ('Charteris' in the Rijksmuseum note is the Wemyss surname of the present "
             "owners, the TRACYS of Stanway); the point is the house's P625"),
    "st-james-palace-q272162": dict(qid="Q272162", name="St James's Palace", lon=-0.137778, lat=51.504722,
        place="City of Westminster", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/St_James%27s_Palace",
        note="two 1707 plates (Yale B2017.35.3 'Le Palais Royal de St James' and B1977.14.18146 'The Palace and "
             "Park of St James's') - one site, one row per plate; the palace and its park stand; the point is the "
             "palace's P625"),
    "lambeth-palace-q1130266": dict(qid="Q1130266", name="Lambeth Palace", lon=-0.11972, lat=51.49556,
        place="City of London", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Lambeth_Palace",
        note="1711-12 plate (Yale B1977.14.17372, 'His Grace the Lord Archbishop of Canterbury Palace'); the "
             "palace stands (the archbishop of Canterbury's London residence); the point is the palace's P625"),
    "somerset-house-q1344889": dict(qid="Q1344889", name="Somerset House", lon=-0.117778, lat=51.511111,
        place="City of Westminster", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Somerset_House",
        note="1711-31 plate (Yale B1977.14.18272); the QID is the 1964 LSE rebuilding on the 1711-31 original's "
             "site (part of the original Strand-side complex survives); Q110073896 is the item for the KIP "
             "ENGRAVING (not usable) and Q17542634 is a different Somerset House (Whitehaven) - the name-search "
             "trap check shows what the live caption route would resolve; the point is the site's P625"),
    "hampton-court-palace-q205666": dict(qid="Q205666", name="Hampton Court Palace", lon=-0.337499, lat=51.4034,
        place="Kingston upon Thames", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Hampton_Court_Palace",
        note="1707 plate (the AIC's clean single-plate impression); the palace and its parterres stand. The "
             "Hampton Court trap in reverse: THIS is the palace on the Thames - a new site, distinct from the "
             "hand-tied Q1443802 'Hampton Court' in Herefordshire; the point is the palace's P625"),
    # The three without a QID: no Wikidata item exists for the house (checked 2026-10-13). The point is the
    # surviving landmark, cross-checked 2026-10-13 (Nominatim for the first two; WGS-84 EXIF geograph photos for
    # the last; docs/lead_kip.md §2 records the details).
    "kings-weston-house": dict(qid=None, name="Kings Weston House", lon=-2.661541, lat=51.494382,
        place="Bristol", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Kings_Weston_House",
        note="1710 plate ('Birds-eye view of the Kingsweston estate', Atkyns' Glocestershire); the house Kip drew "
             "(Elizabethan, on the site of the Vanbrugh house rebuilt 1712-19) still stands. No Wikidata item for "
             "the house (not the Bristol suburb Q6413746, not the hill Q6413747); the point is the enwiki infobox "
             "WGS84 51.494382, -2.661541: Nominatim 'Kings Weston House, Bristol' resolves 4 m from it, and the "
             "article's grid ref ST529771 = 352900, 177100 (the ST 100 km square's origin is 300000, 100000) agrees "
             "with it within the WGS84/OSGB36 datum offset"),
    "stoke-house": dict(qid=None, name="Stoke House", lon=-2.6294812, lat=51.4767404,
        place="Bristol", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Stoke_Bishop",
        note="1709 Britannia Illustrata plate ('the seat of Sr. Thomas Cann' - son of Sir Robert Cann, Bristol MP "
             "and Mayor, who built the manor 1669); the house (Grade II*) still stands, now Trinity Theological "
             "College, Bristol. No Wikidata item for the house (the suburb is Q7618438; the enwiki article is "
             "'Stoke Bishop'); the point is the Nominatim/OSM amenity point 51.4767404, -2.6294812 (checked "
             "2026-10-13, 0 m)"),
    "burford-house-windsor": dict(qid=None, name="Burford House", lon=-0.6056, lat=51.4810,
        place="Windsor and Maidenhead", region="england", kind="garden",
        wikipedia="https://en.wikipedia.org/wiki/Nell_Gwyn",
        note="1707 plate (Yale B2017.35.1, 'the House at Windsor, Belonging to his Grace Charles Beauclerck' - the "
             "duke of St Albans' house, Nell Gwyn's former house on the edge of Home Park); the house is GONE "
             "(sold to George III 1779, absorbed into the Royal Mews) but the view is locked to the standing "
             "Windsor Castle (Q42646) in the same view. No enwiki article ('Burford House' is a 4-way disambiguation "
             "with a red Windsor link; the house is described in the 'Nell Gwyn' article, which this row's "
             "wikipedia carries). The point is the Mews/Saint Alban's Street site from two geograph photos' WGS-84 "
             "EXIF (51.481051,-0.605551 / 51.480870,-0.605556; Nominatim 'Royal Mews, Windsor' 72 m from it, same "
             "street), ~325 m SOUTH of the castle's P625, checked 2026-10-13"),
}


def now():
    return time.strftime("%Y-%m-%d")


def _datavalues(claims):
    return [x["mainsnak"]["datavalue"]["value"] for x in claims if "datavalue" in x.get("mainsnak", {})]


def _ids(claims):
    return [v.get("id") for v in _datavalues(claims) if isinstance(v, dict) and v.get("id")]


def _commons():
    import commons  # lazy: commons -> aw needs numpy (absent from the system python3)
    return commons


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def list_files():
    """Live (paced): every file of the lead categories with its metadata, JSON lines to stdout.
    The root category's live subcategory set must equal CATS[1:] (drift fails loud); when INVENTORY
    is non-empty, the live title set and every (w, h) must equal it. Returns {title: (meta, cats)}."""
    c = _commons()
    subs = [s.split(":", 1)[1] for s in c.members(CATS[0], "subcat")]
    if sorted(subs) != sorted(CATS[1:]):
        raise SystemExit(f"subcategory drift: live {sorted(subs)} != {sorted(CATS[1:])}")
    by_cat = {}
    for cat in CATS:
        for t in c.members(cat, "file"):  # file members carry the "File:" prefix, unlike subcats
            by_cat.setdefault(t, []).append(cat)
    titles = sorted(by_cat)
    if INVENTORY:
        inv = {r[0]: r for r in INVENTORY}
        extra = [t for t in titles if t not in inv]
        gone = [t for t in inv if t not in by_cat]
        if extra or gone:
            raise SystemExit(f"INVENTORY drift: new files {extra}; vanished {gone}")
    meta = c.info(titles)
    for t in titles:
        m = meta.get(t) or {}
        if INVENTORY:
            r = next(x for x in INVENTORY if x[0] == t)
            if (m.get("w"), m.get("h")) != (r[1], r[2]):
                raise SystemExit(f"size drift for {t}: live {(m.get('w'), m.get('h'))} != {(r[1], r[2])}")
        print(json.dumps({"title": t, "w": m.get("w"), "h": m.get("h"), "date": m.get("date"),
                          "cats": by_cat[t], "desc": m.get("desc")}, ensure_ascii=False))
    return {t: (meta.get(t) or {}, by_cat[t]) for t in titles}


def known_sites():
    """{qid: site id} over the built sites, the catalog and the extras (a source never makes a second site)."""
    out = {}
    for p in (SITES_JSONL, EXTRAS):
        for s in _load(p):
            if s.get("qid") and s["qid"] not in out:
                out[s["qid"]] = s["id"]
    for s in json.load(open(WEB_SITES, encoding="utf-8"))["sites"]:
        if s.get("qid") and s["qid"] not in out:
            out[s["qid"]] = s["id"]
    return out


def verify_sites():
    """Live (paced): re-verify every SITES entry and print the facts for the lead doc's §2. The QID-bearing
    entries: the Wikidata label, every P625 value (flagged when >50 km from the landmark point - that is a wrong
    item, not a different point of the same house), P373, P131 (with labels), the enwiki title, and the first
    name-search hit with coordinates (what record --live would resolve for the caption route). The three without
    a QID: the stored source note (there is nothing on Wikidata to check). Plus the known_sites() collision
    check: a QID already in the catalog means the picture stages under the existing site id, not a new one.
    Exits 1 on a collision, a >50 km P625 flag or a missing item."""
    import evidence  # hav_m (the fit/ sibling; needs numpy, run under .venv)
    c = _commons()
    qids = sorted({s["qid"] for s in SITES.values() if s["qid"]})
    known = known_sites()
    problems = []
    for q in qids:
        if q in known:
            problems.append(f"QID {q} already in the catalog ({known[q]}): the view must stage under the "
                            f"existing site, not a new one")
    print(f"checked {now()} - {len(SITES)} sites ({len(qids)} with a QID, {len(SITES) - len(qids)} without)")
    print(f"known_sites() collision over the {len(qids)} QIDs: " + ("; ".join(problems) if problems else "none"))
    ents = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(qids),
                        "props": "claims|sitelinks|labels", "languages": "en"}).get("entities", {})
    p131s = sorted({i for q in qids for i in _ids(ents.get(q, {}).get("claims", {}).get("P131", []))})
    labels = {}
    for i in range(0, len(p131s), 50):  # wbgetentities takes at most 50 ids per call
        d2 = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(p131s[i:i + 50]), "props": "labels", "languages": "en"})
        labels.update({k: v.get("labels", {}).get("en", {}).get("value") for k, v in d2.get("entities", {}).items()})
    for sid in sorted(SITES):
        s = SITES[sid]
        if not s["qid"]:
            print(f"  {sid}: no QID (no Wikidata item for the house) - {s['note']}")
            continue
        e = ents.get(s["qid"])
        if not e:
            problems.append(f"{s['qid']} ({sid}) not found on Wikidata")
            print(f"  {s['qid']}  MISSING on Wikidata  [{sid}]")
            continue
        cl = e.get("claims", {})
        print(f"  {s['qid']}  {e.get('labels', {}).get('en', {}).get('value')!r}  [{sid}]")
        p625 = [(v["longitude"], v["latitude"]) for v in _datavalues(cl.get("P625", [])) if v]
        print(f"      landmark: {s['lon']}, {s['lat']}   P625: {p625}")
        for lon, lat in p625:
            dist = evidence.hav_m(lon, lat, s["lon"], s["lat"])
            if dist > 50e3:
                problems.append(f"{s['qid']}: a P625 is {dist / 1000:.0f} km from the landmark point (wrong item?)")
                print(f"      FLAG: a P625 is {dist / 1000:.0f} km from the landmark point (wrong item?)")
            else:
                print(f"      P625 distance to landmark: {dist / 1000:.2f} km")
        print(f"      P373: {_datavalues(cl.get('P373', []))}")
        print(f"      P131: {[(labels.get(i), i) for i in _ids(cl.get('P131', []))]}  (table place: {s.get('place')!r})")
        print(f"      enwiki: {e.get('sitelinks', {}).get('enwiki', {}).get('title')!r}  (table wikipedia: {s.get('wikipedia')!r})")
        sr = c.get(c.WD, {"action": "wbsearchentities", "search": s["name"], "language": "en", "limit": "5"})
        ids = [x["id"] for x in sr.get("search", [])]
        if ids:
            d3 = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(ids), "props": "claims|labels", "languages": "en"})
            for q in ids:
                hits = [(v["longitude"], v["latitude"]) for v in _datavalues(
                    d3.get("entities", {}).get(q, {}).get("claims", {}).get("P625", [])) if v]
                if hits:
                    lon, lat = hits[0]
                    dist = evidence.hav_m(lon, lat, s["lon"], s["lat"])
                    flag = "" if dist <= 50e3 else f"   <- TRAP: {dist / 1000:.0f} km, the live caption route would store a conflict (kind none)"
                    lab = d3["entities"][q].get("labels", {}).get("en", {}).get("value", "")
                    print(f"      search {s['name']!r}: first hit with P625 is {q} {lab!r} ({lon}, {lat}){flag}")
                    break
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        return 1
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--list":
        out = a[a.index("--out") + 1] if "--out" in a else None
        if out:
            f = open(out, "w", encoding="utf-8")
            import contextlib
            with contextlib.redirect_stdout(f):
                list_files()
        else:
            list_files()
    elif a and a[0] == "--verify":
        raise SystemExit(verify_sites())
    else:
        raise SystemExit(__doc__.strip().split("usage:")[1].strip())
