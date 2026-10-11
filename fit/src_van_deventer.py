"""Van Deventer's remaining town plans (task 204, GOAL.md point 4): the ~60 town plans of c. 1545-1565 that
pipeline/sources.py's deventer table does not cover (the six already hand-tied there - Gouda, Zwolle, Venlo,
Damme, Binche, Bergues - are NOT re-staged here; their canonical rows keep the sources.py hand-tie).

The Commons category "Maps by Jacob van Deventer" holds 70 subcategories: 66 town categories and 4 collection
categories (the BNE autographs, the Nationaal Archief, the RCE scans, and the BNE atlas with its per-town plate
subcategories). For every new town this module records the hand-checked facts (the QID verified against its
label, every P625 value, its P373, P131 and its enwiki link - a name search alone gives the wrong place, the
Barnard Castle trap), the one picture staged for it (the best full plan of the town's own Commons category),
and its machine-checkable evidence (task 200): the P373 category chain where the walk holds, else the caption
(the file names the town; the stored resolution is the verified site point, never a bare name-search hit),
else a documented drop in docs/lead_van_deventer.md.

usage: src_van_deventer.py --list              live: assert the 70 subcategories against the TOWNS table
       src_van_deventer.py --files [towns...]  live: the file inventory of the towns' categories (own files +
                                             subcategories at depth 1) and of the 4 collection categories (lead doc)
       src_van_deventer.py --verify [towns...] live: per town the QID fact sheet (discovery when the town has
                                             no QID yet, re-verification when it does; no args = the table)
       src_van_deventer.py --chain <town>      live: walk the town file category's parent chain up to the
                                             P373 category (depth cap 6) and print the via list
       src_van_deventer.py stage [--dry]      stage the verified towns into this task's own staging files
       src_van_deventer.py --check            offline: join the staged files and run fit/evidence.py's check
       src_van_deventer.py --golden           write tests/golden/src_van_deventer_sample.json

The live commands run under .venv/bin/python (commons -> aw needs numpy, absent from the system python3); the
module top stays stdlib-only. Staging writes only this task's files (append-only, idempotent on (site, title));
211 consolidates them into the canonical ones and builds the sites.
"""
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

EXTRAS = os.path.join(ROOT, "data", "catalog", "extras_van_deventer.jsonl")
FILES = os.path.join(ROOT, "data", "commons", "files_van_deventer.jsonl")
CLASSIFIED = os.path.join(ROOT, "data", "commons", "classified_van_deventer.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

CATALOG_PARENT = "Maps by Jacob van Deventer"
CHAIN_FETCH_CAP = 60  # the --chain BFS's per-town fetch budget: measured chains are 3-5 hops and a few
                      # dozen fetches, but a frontier the map tree does not close within 6 hops (a
                      # disambiguated p373) explodes - the cap sends that town to the caption route
COLLECTIONS = [
    "Maps by Jacob van Deventer (Biblioteca Nacional de España)",
    "Maps by Jacob van Deventer (Nationaal Archief)",
    "Maps by Jacob van Deventer (Rijksdienst voor het Cultureel Erfgoed)",
    "Atlas des villes des Pays-Bas : 73 places levées entre 1550 et 1565 sur les ordres de Charles Quint et de Philippe II",
]

# The 66 town categories of CATALOG_PARENT (list_categories() asserts the live list against this table).
# region: the catalog's lowercase value (build_catalog.REGION_NAME has netherlands/belgium/france; "luxembourg"
# has no key yet - the display falls back to the raw value, the 213 "Italy" pattern before 214).
# qid/label/lon/lat/p625/place/wikipedia/p373/date: recorded by the hand check after --verify prints the fact
# sheet (discovery when qid is absent, re-verification when present). lon/lat is the old-town centre, not just
# the municipality point (Gouda misses by up to 800 m; p625 records the municipality value). p373 is the exact
# P373 category string (the category route's target and the staged row's "cat"). date is the known drawing date
# used when the file page carries only an upload date (the Gouda/Zwolle precedent). done: the six already
# hand-tied in pipeline/sources.py (never re-staged here). file: the one staged picture (the best full plan).
# chain: the verified category chain (the file category's parents up to p373; the category evidence kind),
# kept in the CHAINS table below (one place for the walked paths) and read through chain_of().
# caption: the place string the file's title/desc actually prints (the caption route's named_place).
TOWNS = {
    # -- the Netherlands (19 categories: 16 to stage + the 3 done; "Groningen (province)" is a province map, a
    # documented drop: it is not a town plan). QIDs hand-verified 2026-10-11 (--verify: label, P625, P373, enwiki;
    # the P373 of every city item is its own town category - the category route's target). lon/lat is the
    # old-town centre the plan is centred on; p625 records the municipality point (the Gouda 800 m case); the
    # per-town distances are in docs/lead_van_deventer.md. file/date recorded 2026-10-11 from the live --files
    # inventory (the 16 NL towns + the 4 collection categories): 13 of the 16 carry their one staged picture;
    # the other 3 (Groningen (province), Leeuwarden, Middelburg) are documented drops, the reason in `note` and
    # in docs/lead_van_deventer.md (Per town). date = the known drawing date used when the file page carries
    # only its own (upload/scan) date: the row then keeps the page value as date_commons. --
    "Aardenburg": dict(region="netherlands", cat="Map of Aardenburg by Jacob van Deventer",
                       qid="Q955", label="Aardenburg", lon=3.4453, lat=51.2744, p625=(3.445278, 51.274444),
                       place="Sluis", wikipedia="https://en.wikipedia.org/wiki/Aardenburg", p373="Aardenburg",
                       file="File:Aardenburg 1560.jpg"),
    "Alkmaar": dict(region="netherlands", cat="Maps of Alkmaar by Jacob van Deventer",
                    qid="Q972", label="Alkmaar", lon=4.7427, lat=52.6285, p625=(4.744, 52.6289),
                    place="North Holland", wikipedia="https://en.wikipedia.org/wiki/Alkmaar", p373="Alkmaar",
                    file="File:Kaart van Alkmaar en Oudorp door Jacob van Deventer 01.jpg"),
    "Amsterdam": dict(region="netherlands", cat="Maps of Amsterdam by Jacob van Deventer",
                      qid="Q727", label="Amsterdam", lon=4.8865, lat=52.3725, p625=(4.883333, 52.366667),
                      place="North Holland", wikipedia="https://en.wikipedia.org/wiki/Amsterdam", p373="Amsterdam",
                      file="File:Kaart van Amsterdam c1550 (City Map) Jacob van Deventer.jpg"),
    "Enkhuizen": dict(region="netherlands", cat="Map of Enkhuizen by Jacob van Deventer",
                      qid="Q9918", label="Enkhuizen", lon=5.286, lat=52.7025, p625=(5.283333, 52.7),
                      place="North Holland", wikipedia="https://en.wikipedia.org/wiki/Enkhuizen", p373="Enkhuizen",
                      file="File:Jacob van Deventer Enkhuizen 1558-1560.jpg"),
    "Goes": dict(region="netherlands", cat="Map of Goes by Jacob van Deventer",
                 qid="Q81220", label="Goes", lon=3.885, lat=51.5043, p625=(3.883333, 51.5),
                 place="Goes", wikipedia="https://en.wikipedia.org/wiki/Goes", p373="Goes",
                 file="File:Goes 1572 Bijkrt v Deventer.jpg"),  # the only Goes row in the c. 1545-1565 window
                 # (page date 1560); the netkaart (1572/1575) is a later revision - lead doc
    "Groningen": dict(region="netherlands", cat="Map of Groningen (city) by Jacob van Deventer",
                      qid="Q749", label="Groningen", lon=6.571, lat=53.2197, p625=(6.5675, 53.218889),
                      place="Groningen (province)", wikipedia="https://en.wikipedia.org/wiki/Groningen",
                      p373="Groningen (city)", file="File:Jacob van Deventer - Groningen volledig.jpg"),
    "Groningen (province)": dict(region="netherlands", cat="Map of Groningen (province) by Jacob van Deventer",
                                 search="Groningen province",
                                 qid="Q752", label="Groningen", lon=6.7378, lat=53.2581, p625=(6.737778, 53.258056),
                                 place="Netherlands", wikipedia="https://en.wikipedia.org/wiki/Groningen_(province)",
                                 p373="Groningen (province)",
                                 note="a province map, not a town plan: a documented drop (no site, no picture); "
                                      "its two files are crops of the Friesland gewestkaart (the province of Groningen "
                                      "visible on it, and the Maria-ten-Hoorn abbey detail)"),
    "Haarlem": dict(region="netherlands", cat="Maps of Haarlem by Jacob van Deventer",
                    qid="Q9920", label="Haarlem", lon=4.634, lat=52.388, p625=(4.635556, 52.381389),
                    place="North Holland", wikipedia="https://en.wikipedia.org/wiki/Haarlem", p373="Haarlem",
                    file="File:Kaart van de stad Haarlem, waarop de kerken, kloosters, stadspoorten en "
                         "invalswegen staan aangegeven kartografisch document door Jacobus van Deventer vervaardigd "
                         "voor Filips II, Inventarisnummer NL-HlmNHA 1100 KNA006000046.JPG"),  # 1565, the Haarlem
                    # municipal collection's scan of the drawing (lead doc)
    "Leeuwarden": dict(region="netherlands", cat="Map of Leeuwarden by Jacob van Deventer",
                       qid="Q25390", label="Leeuwarden", lon=5.793, lat=53.2007, p625=(5.783333, 53.2),
                       place="Friesland", wikipedia="https://en.wikipedia.org/wiki/Leeuwarden", p373="Leeuwarden",
                       note="drop: its only file (Ontstaan leeuwardendelen.jpg, 593x636) is a 1975 redrawn model "
                            "(J.R.G. Schuur) after Deventer's drawing, not the plan itself - lead doc"),
    "Middelburg": dict(region="netherlands", cat="Map of Middelburg by Jacob van Deventer",
                       qid="Q52101", label="Middelburg", lon=3.614, lat=51.5006, p625=(3.613611, 51.499722),
                       place="Zeeland", wikipedia="https://en.wikipedia.org/wiki/Middelburg,_Zeeland", p373="Middelburg",
                       note="drop: its only file (20154723 - RCE, 1942) is a detail crop of the stadhuis from the "
                            "RCE album; no full Middelburg plan on Commons - lead doc"),
    "Reimerswaal": dict(region="netherlands", cat="Map of Reimerswaal by Jacob van Deventer",
                        qid="Q2590944", label="Reimerswaal", lon=4.172486, lat=51.507539,
                        p625=(4.172486, 51.507539),
                        place="Zeeland", wikipedia="https://en.wikipedia.org/wiki/Reimerswaal_(city)",
                        p373="Reimerswaal", file="File:Reimerswaal 1560 Minuut v Deventer.jpg"),  # the original
                        # minuutkaart (3501x2541, 1560); the bijkaart/netkaart/1545-BNE copies not staged
    "Rotterdam": dict(region="netherlands", cat="Maps of Rotterdam by Jacob van Deventer",
                      qid="Q34370", label="Rotterdam", lon=4.4745, lat=51.9155, p625=(4.48, 51.92),
                      place="South Holland", wikipedia="https://en.wikipedia.org/wiki/Rotterdam", p373="Rotterdam",
                      file="File:Map of Rotterdam around 1560s by Jacob van Deventer.jpg",
                      date="circa 1560"),  # the page's year-only date is 1563 (one year of the drawing's 1558-1563
                      # window); the row carries the known "circa 1560" (the title's own "around 1560s"), keeping
                      # 1563 as date_commons - the Gouda/Zwolle precedent, lead doc
    "Sluis": dict(region="netherlands", cat="Map of Sluis by Jacob van Deventer",  # the name search "Sluis"
                  # resolves FIRST to Q2065987 (no enwiki, P625 8 km SW, P373 'Sluis (city)') - the trap, lead doc
                  qid="Q10080", label="Sluis", lon=3.493, lat=51.347, p625=(3.5, 51.35),
                  place="Zeeland", wikipedia="https://en.wikipedia.org/wiki/Sluis", p373="Sluis",
                  file="File:Plattegrond van J. van Deventer, reproductie uit album Rijksdienst voor de Monumenten "
                       "Zorg te Zeist en Sint Anna ter Muiden - Sluis - 20201361 - RCE.jpg",
                  date="circa 1545-1565"),  # the 1980 RCE album reproduction (the only full-plan candidate; the
                  # Zwolle done-row precedent) - the known drawing window goes on the row, date_commons keeps 1980;
                  # its category also holds 227 Damme.jpg (Damme's netkaart, misfiled here - lead doc)
    "The Hague": dict(region="netherlands", cat="Map of The Hague by Jacob van Deventer",
                      qid="Q36600", label="The Hague", lon=4.305, lat=52.079, p625=(4.31, 52.08),
                      place="South Holland", wikipedia="https://en.wikipedia.org/wiki/The_Hague", p373="The Hague",
                      file="File:1558, Den Haag. Jacob van Deventer.jpg"),  # the same file (the autograph) is in
                      # the Nationaal Archief collection category
    "Utrecht": dict(region="netherlands", cat="Maps of Utrecht (city) by Jacob van Deventer", search="Utrecht",
                    qid="Q803", label="Utrecht", lon=5.1185, lat=52.091, p625=(5.121667, 52.090833),
                    place="Utrecht (province)", wikipedia="https://en.wikipedia.org/wiki/Utrecht",
                    p373="Utrecht (city)", file="File:Utrecht.jpg"),  # 1565-1570, the full plan; the three RCE
                    # album reproductions (1955/1982) and the Buiten-Wittevrouwen suburb map are not staged
    "Valkenburg": dict(region="netherlands", cat="Map of Valkenburg, Limburg by Jacob van Deventer",
                       qid="Q100076", label="Valkenburg", lon=5.83205, lat=50.86523, p625=(5.83205, 50.86523),
                       place="Limburg", p373="Valkenburg, Limburg",
                       file="File:Plattegrond van J. van Deventer, reproductie uit album Rijksdienst voor de "
                            "Monumenten Zorg te Zeist - Valkenburg - 20237999 - RCE.jpg",
                       date="circa 1545-1565"),  # the 1980 RCE album reproduction (the only full-plan candidate;
    # the same file is in the RCE category) - the known drawing window goes on the row, date_commons keeps 1980;
    # the other nine files (detail crops, 346-944 px) are not staged (lead doc)
    "Gouda": dict(region="netherlands", cat="Map of Gouda by Jacob van Deventer", qid="Q84125", done=True),
    "Zwolle": dict(region="netherlands", cat="Map of Zwolle by Jacob van Deventer", qid="Q793", done=True),
    "Venlo": dict(region="netherlands", cat="Map of Venlo by Jacob van Deventer", qid="Q9777", done=True),
    # -- Belgium (24 categories: 22 to stage + the 2 done; Le Rœulx joined from the prep's France list in
    # iter 49 - its verified item sits in Hainaut, Belgium - and Beaumont joined in iter 52, its atlas plate
    # showing the Sambre bisecting the town and the counts' chateau (Beaumont (Nord) has neither)). QIDs
    # hand-verified 2026-10-11 in one --verify discovery run (transcript /tmp/vd_verify_be_iter45.txt;
    # Beaumont re-verified in iter 52 - the first search hit WITH a P625 is Q128282 'Beaumont' (Texas),
    # ~7000 km away, the trap; the recorded label, P373 and enwiki confirm Q95100): every label matches the
    # town (Leuze's verified item carries the official disambiguated name 'Leuze-en-Hainaut'), every P373 is
    # its exact recorded string, every P625 sits at the town; the site point is the P625 rounded (the hand
    # check found no offset from the old-town centre, unlike the NL Gouda 800 m case). Five items carry a
    # disambiguated P373 (Brussels 'Brussels (municipality)', Halle 'Halle (Belgium)', Mons 'Mons (Hainaut)',
    # Leuze 'Leuze-en-Hainaut', Beaumont 'Beaumont (Hainaut)') - the category route targets that exact
    # string, the chain walk must reach it. Mons was NOT in its search's top 5 (the French communes outrank
    # it - the batch's biggest trap, found by a follow-up search at limit 20; lead doc). file/date recorded
    # 2026-10-11 (iter 46) from the live --files inventory (transcript /tmp/vd_files_be_iter46.txt) plus a
    # 1200 px thumb eye check of every ambiguous candidate; Le Rœulx's and Beaumont's file= came in iter 52
    # (the 1545 BNE atlas plates; transcript /tmp/vd_files_fr_iter50.txt + the 1280 px eye check
    # /tmp/vd_fr_thumbs/): 21 of the 22 carry their one staged picture (17 of the BNE atlas 1545 sheets +
    # the Ostend plate, circa 1562 + the KBR Brussels and Mechelen autographs and the full, caption-dated
    # Bruges plan); Aarschot is the documented drop (both files dated 1570, outside the c. 1545-1565 window
    # - the reason in `note` and the lead doc). No BE QID is in the built catalog (the 12575-site check of
    # 2026-10-11): all 22 get new catalog entries. --
    "Ath": dict(region="belgium", cat="Map of Ath by Jacob van Deventer",
                qid="Q95096", label="Ath", lon=3.7769, lat=50.6311, p625=(3.776941, 50.631139),
                place="Arrondissement of Ath", wikipedia="https://en.wikipedia.org/wiki/Ath", p373="Ath",
                file="File:Ath - Deventer.jpg"),  # the 1545 BNE atlas plate (3438x2614; page date 1545 = the drawing's)
    "Braine-le-Comte": dict(region="belgium", cat="Map of Braine-le-Comte by Jacob van Deventer",
                            qid="Q95129", label="Braine-le-Comte", lon=4.1361, lat=50.6097, p625=(4.136111, 50.609722),
                            place="Arrondissement of Soignies", wikipedia="https://en.wikipedia.org/wiki/Braine-le-Comte",
                            p373="Braine-le-Comte",
                            file="File:Braine-le-Comte - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Bruges": dict(region="belgium", cat="Maps of Bruges by Jacob van Deventer",
                   qid="Q12994", label="Bruges", lon=3.2242, lat=51.2089, p625=(3.224167, 51.208889),
                   place="Arrondissement of Bruges", wikipedia="https://en.wikipedia.org/wiki/Bruges",
                   p373="Bruges", file="File:Map of Bruges by Jacob van Deventer.jpg",
                   date="circa 1550"),  # the full plan (2770x4659): the page date 2013-01-17 12:04:47 is an upload
                   # timestamp, but the sheet's own caption block (bottom edge, partly torn away) reads "en
                   # omgeving omstreeks den jare 1550. Plattegrond in kleuren. Originalade Teckening van den
                   # be-Keizerlijken..." - the drawing dates itself c. 1550, so the row carries the known date
                   # and keeps the page value as date_commons (the Gouda/Zwolle precedent). Not staged: the five
                   # detail crops (573-1180 px; their QS 'circa 1558' loses to the sheet's own caption) and
                   # 'Plan Brugge Jacob van Deventer ca.1560.jpg' (1400x1867, a published reproduction per
                   # C. Ruelen) - lead doc
    "Brussels": dict(region="belgium", cat="Maps of Brussels by Jacob van Deventer",
                     qid="Q239", label="Brussels", lon=4.3517, lat=50.8467, p625=(4.351667, 50.846667),
                     place="Arrondissement of Brussels-Capital",
                     wikipedia="https://en.wikipedia.org/wiki/City_of_Brussels", p373="Brussels (municipality)",
                     file="File:Brussels map by Jacob van Deventer, Atlas des villes des Pays-Bas, 73 places levées, ca. 1555 (2) 01.png"),
                     # the KBR autograph (8908x10941), page 'circa 1555' = the drawing's date, cleanly cropped.
                     # Not staged: the same sheet WITH a TIFFEN colour-calibration strip ('(2).png', 9216x12288),
                     # the '(2) 02' detail (5580x5478), the three small Brussel 1550/1555/1560 scans (470-1233 px;
                     # the 1560 one is the 'minuut' per the desc) and Molenbeek.1550.jpg (378x565, Molenbeek +
                     # the west of the 2e enceinte - a partial, the work list's 'Brussel, 1550 (westelijk gedeelte)')
    "Chimay": dict(region="belgium", cat="Map of Chimay by Jacob van Deventer",
                   qid="Q95380", label="Chimay", lon=4.3173, lat=50.0479, p625=(4.317334, 50.047927),
                   place="Arrondissement of Thuin", wikipedia="https://en.wikipedia.org/wiki/Chimay", p373="Chimay",
                   file="File:Chimay - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Chièvres": dict(region="belgium", cat="Map of Chièvres by Jacob van Deventer",
                     qid="Q95318", label="Chièvres", lon=3.8, lat=50.5833, p625=(3.8, 50.583333),
                     place="Arrondissement of Ath", wikipedia="https://en.wikipedia.org/wiki/Chièvres", p373="Chièvres",
                     file="File:Chièvres - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Enghien": dict(region="belgium", cat="Map of Enghien by Jacob van Deventer",
                    qid="Q666238", label="Enghien", lon=4.0411, lat=50.6956, p625=(4.041111, 50.695556),
                    place="Arrondissement of Soignies", wikipedia="https://en.wikipedia.org/wiki/Enghien", p373="Enghien",
                    file="File:Enghien - Deventer.jpg"),  # the 1545 BNE atlas plate (3425x2614)
    "Ghent": dict(region="belgium", cat="Map of Ghent by Jacob van Deventer",
                  qid="Q1296", label="Ghent", lon=3.7253, lat=51.0536, p625=(3.725278, 51.053611),
                  place="East Flanders", wikipedia="https://en.wikipedia.org/wiki/Ghent", p373="Ghent",
                  file="File:Ghent by Jacob Van Deventer, BN 1.jpg"),  # the 1545 BNE plate (4919x5046): the sheet
                  # labelled 'Gande', the city between its two rivers. BN 2 (2834x3631, 1545) is a DIFFERENT
                  # unlabelled sheet (a fortified town, no city label in the centre crop) - not staged; neither are
                  # the 1559 Donato Buoni print (another cartographer) and the five small 2007-2012 scans/crops
                  # (457-1510 px) - lead doc
                  # Q1296 was already hand-verified in the prep (2026-10-11 01:32: label, P373, P625 at the city
                  # centre, enwiki) - the only QID verified before the batch; the iter-45 run re-confirms it
    "Halle": dict(region="belgium", cat="Map of Halle by Jacob van Deventer",
                  qid="Q210003", label="Halle", lon=4.2372, lat=50.7361, p625=(4.237222, 50.736111),
                  place="Arrondissement of Halle-Vilvoorde",
                  wikipedia="https://en.wikipedia.org/wiki/Halle,_Belgium", p373="Halle (Belgium)",
                  file="File:Halle - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614; the desc names it 'Hal')
    "Kortrijk": dict(region="belgium", cat="Map of Kortrijk by Jacob van Deventer",
                     qid="Q12995", label="Kortrijk", lon=3.2658, lat=50.8275, p625=(3.265833, 50.8275),
                     place="Arrondissement of Kortrijk", wikipedia="https://en.wikipedia.org/wiki/Kortrijk",
                     p373="Kortrijk", file="File:Kortrijk, map by Jacob van Deventer.JPG"),  # the 1545 BNE plate (3753x2614)
    "Lessines": dict(region="belgium", cat="Map of Lessines by Jacob van Deventer",
                     qid="Q667790", label="Lessines", lon=3.83, lat=50.7117, p625=(3.83, 50.7117),
                     place="Arrondissement of Soignies", wikipedia="https://en.wikipedia.org/wiki/Lessines",
                     p373="Lessines", file="File:Lessines - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Le Rœulx": dict(region="belgium", cat="Map of Le Rœulx by Jacob van Deventer",
                     qid="Q668861", label="Le Rœulx", lon=4.1116, lat=50.5036, p625=(4.1, 50.5),
                     place="Arrondissement of Soignies", wikipedia="https://en.wikipedia.org/wiki/Le_R%C5%93ulx",
                     p373="Le Roeulx",
                     file="File:Le Rœulx - Deventer.jpg"),  # discovered in the FR batch (iter 49) and moved
    # here: the item is in Hainaut, Belgium (the enwiki lead: "a city and municipality of Wallonia ... in the
    # province of Hainaut, Belgium") - the prep's france region guess was wrong. The recorded item's P625
    # (4.1, 50.5) is a rounded value; the site point is the precise P625 of its subdivision item Q21764574
    # (4.11163, 50.50365) - the town centre. P373 is 'Le Roeulx' without the diaeresis. file= (iter 52,
    # transcript /tmp/vd_files_fr_iter50.txt): the 1545 BNE atlas plate (1816x2614, desc 'Le Rœulx')
    "Leuze": dict(region="belgium", cat="Map of Leuze by Jacob van Deventer",
                  qid="Q667862", label="Leuze-en-Hainaut", lon=3.6167, lat=50.6, p625=(3.616667, 50.6),
                  place="Arrondissement of Tournai", wikipedia="https://en.wikipedia.org/wiki/Leuze-en-Hainaut",
                  p373="Leuze-en-Hainaut", file="File:Leuze - Deventer.jpg",
                  caption="Leuze"),  # the 1545 BNE atlas plate (1816x2614, desc 'Leuze'): the caption route
                  # names the town as the file prints it - the item's official label 'Leuze-en-Hainaut' is not in
                  # the title/desc, so without caption= the caption check would fail
                  # the verified item's label is the official disambiguated name (the search 'Leuze' first hits
                  # the French Leuze (Aisne), Q326134 - the trap, lead doc)
    "Mechelen": dict(region="belgium", cat="Map of Mechelen by Jacob van Deventer",
                     qid="Q162022", label="Mechelen", lon=4.4803, lat=51.0281, p625=(4.480278, 51.028056),
                     place="Arrondissement of Mechelen", wikipedia="https://en.wikipedia.org/wiki/Mechelen",
                     p373="Mechelen", file="File:Mechelen, Belgium, Deventer, 1550.png"),  # the KBR autograph
                     # (3558x3305; page date 1550 = the drawing's - the work list 'Mechelen, 1550' agrees;
                     # the desc names the atlas the KBR bought in 1866)
    "Mons": dict(region="belgium", cat="Map of Mons by Jacob van Deventer",
                 qid="Q83407", label="Mons", lon=3.9525, lat=50.4547, p625=(3.9525, 50.454722),
                 place="County of Hainaut", wikipedia="https://en.wikipedia.org/wiki/Mons,_Belgium",
                 p373="Mons (Hainaut)", file="File:Mons (2) - Deventer.jpg"),  # the 1545 BNE wide two-page sheet
                 # (4393x2614) labelled 'Mons en Henault' (Ocidente/Oriens/Meridies/Septentrio); (1)
                 # (1816x2614, 1545) is a portrait plate of the same fortified town - not staged (lead doc)
                 # the search 'Mons' (limit 5) returns only the planetary term and French communes; the Belgian
                 # city is 11th in the en results (4th in the fr) - found by a follow-up search at limit 20 (lead doc)
    "Ostend": dict(region="belgium", cat="Map of Ostend by Jacob van Deventer",
                   qid="Q12996", label="Ostend", lon=2.9194, lat=51.2258, p625=(2.919444, 51.225833),
                   place="Arrondissement of Ostend", wikipedia="https://en.wikipedia.org/wiki/Ostend",
                   p373="Ostend", file="File:Oostende map Jacob van Deventer.png"),  # the BNE plate (872x1255;
                   # page 'circa 1562' = the drawing's date): the ONLY Ostend plan on Commons - staged despite
                   # the <~1000 px width heuristic (the Aardenburg case; the caveat is in the lead doc)
    "Saint-Ghislain": dict(region="belgium", cat="Map of Saint-Ghislain by Jacob van Deventer",
                           qid="Q668950", label="Saint-Ghislain", lon=3.8167, lat=50.45, p625=(3.816667, 50.45),
                           place="Arrondissement of Mons", wikipedia="https://en.wikipedia.org/wiki/Saint-Ghislain",
                           p373="Saint-Ghislain", file="File:Saint-Ghislain - Deventer.jpg"),  # the 1545 BNE plate (1816x2614)
    "Soignies": dict(region="belgium", cat="Map of Soignies by Jacob van Deventer",
                     qid="Q462985", label="Soignies", lon=4.0667, lat=50.5667, p625=(4.066667, 50.566667),
                     place="Arrondissement of Soignies", wikipedia="https://en.wikipedia.org/wiki/Soignies",
                     p373="Soignies", file="File:Soignies - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614);
                     # the two 2011 copies (a 'd'apres' redraw, 2362x2468, and a 291x298 scan) are not staged
    "Tournai": dict(region="belgium", cat="Map of Tournai by Jacob van Deventer",
                    qid="Q173219", label="Tournai", lon=3.3881, lat=50.6056, p625=(3.388056, 50.605556),
                    place="Arrondissement of Tournai", wikipedia="https://en.wikipedia.org/wiki/Tournai",
                    p373="Tournai", file="File:Tournai - Deventer.jpg"),  # the 1545 BNE atlas plate (3296x2608)
    "Aarschot": dict(region="belgium", cat="Maps of Aarschot by Jacob van Deventer",
                     qid="Q273442", label="Aarschot", lon=4.8333, lat=50.9842, p625=(4.8333, 50.9842),
                     place="Arrondissement of Leuven", wikipedia="https://en.wikipedia.org/wiki/Aarschot",
                     p373="Aarschot",
                     note="drop: both files carry page date 1570 ('Aarschot 1570.png', 5877x6291, a genuine autograph"
                          " with the town labelled 'Aersfot' on the Dijle, and its 1278x1024 jpg copy) - outside"
                          " the c. 1545-1565 drawing window: no site, no picture. Cross-checked against the"
                          " nl.wikipedia work list ('Aarschot, 1570', the Philip II period) - lead doc"),
    "Beaumont": dict(region="belgium", cat="Map of Beaumont by Jacob van Deventer",
                     qid="Q95100", label="Beaumont", lon=4.2383, lat=50.2355, p625=(4.2383115, 50.2355294),
                     place="Arrondissement of Thuin", wikipedia="https://en.wikipedia.org/wiki/Beaumont,_Belgium",
                     p373="Beaumont (Hainaut)",
                     file="File:Beaumont - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614, desc
    # 'Beaumont'): a fortified town BISECTED by a river (the Sambre) with a bridge, the moated square chateau
    # of the counts of Hainaut (the sheet's lower-left inset = that chateau; confirmed by the 1049x932
    # '...detail - City and Chateau de Beaumont.jpg' - not staged, a detail crop) on the west bank and
    # Charles V's new walled grid town on the east bank. Beaumont (Nord) has no river and no chateau: the
    # drawing settles the Hainaut identification, so the region flipped france -> belgium in iter 52
    # (lead doc). The Q128282 'Beaumont' (Texas) ~7000 km trap is the first P625 search hit (--verify
    # Beaumont, iter 52); the recorded label, P373 and enwiki confirm Q95100
    "Oudenaarde": dict(region="belgium", cat="Maps of Oudenaarde by Jacob van Deventer",
                       qid="Q12992", label="Oudenaarde", lon=3.6, lat=50.85, p625=(3.6, 50.85),
                       place="Arrondissement of Oudenaarde", wikipedia="https://en.wikipedia.org/wiki/Oudenaarde",
                       p373="Oudenaarde",
                       file="File:Oudenaarde, map by Jacob van Deventer, Version Madrid.JPG"),  # the 1545 BNE
                       # plate (3368x2614; the page date 1545 is kept - the work list dates the netkaart 1564,
                       # noted in the lead doc). Not staged: the detail (710x564, QS 'circa 1558'), the DI-676
                       # copy (986x1000, uploaded 2005) and the Version Brussels copy (948x1070, uploaded 2012)
    "Damme": dict(region="belgium", cat="Map of Damme by Jacob van Deventer", qid="Q323408", done=True),
    "Binche": dict(region="belgium", cat="Map of Binche by Jacob van Deventer", qid="Q95121", done=True),
    # -- France (22 categories: 21 to stage + the 1 done; Le Rœulx moved to the Belgium section above: its
    # verified item sits in Hainaut, Belgium - the prep's france guess was wrong, iter 49 - and Beaumont
    # moved there too, its atlas plate settling the Hainaut identification, iter 52). QIDs hand-verified
    # 2026-10-11 (iter 49) in one --verify discovery run (transcript /tmp/vd_verify_fr_iter49.txt; the
    # Luxembourg City and Beaumont follow-up: /tmp/vd_lu_iter49.txt): every label matches the town, every
    # P373 is its exact recorded string, every P625 sits at the town (the site point is the P625 rounded -
    # the BE convention), every item has an enwiki link. None of the 22 QIDs is in the built catalog (the
    # 12575-site check of 2026-10-11): all get new entries. file= for the 21 recorded 2026-10-11 (iter 52)
    # from the live --files inventory (transcript /tmp/vd_files_fr_iter50.txt) plus a 1280 px thumb eye
    # check of every ambiguous candidate (/tmp/vd_fr_thumbs/): the 1545 BNE atlas plate is the pick in every
    # category, but the five (1)/(2) pairs stage the (2) wide sheet (the full two-page drawing with the town
    # label, shield, compass points and scale; (1) is a single page of the same drawing), the
    # Aire/Thérouanne and Hesdin/Vieil-Hesdin double sheets stage once under the first-named town (each
    # also gets its own standalone plan where one exists - Thérouanne, Vieil-Hesdin), and Thérouanne and
    # Vieil-Hesdin carry the <~1000 px size caveat (the only plans of those towns on Commons). No date=
    # swap is needed in this batch: every page date is 1545 = the drawing's (the Hesdin double sheet carries
    # a French page note - year_of takes the min, 1545). --
    "Aire-sur-la-Lys": dict(region="france", cat="Map of Aire-sur-la-Lys by Jacob van Deventer",
                            qid="Q259903", label="Aire-sur-la-Lys", lon=2.3967, lat=50.6386, p625=(2.396667, 50.638611),
                            place="Pas-de-Calais", wikipedia="https://en.wikipedia.org/wiki/Aire-sur-la-Lys",
                            p373="Aire-sur-la-Lys",
                            file="File:Aire-sur-la-Lys - Deventer.jpg"),  # the 1545 two-page spread (3395x2614,
    # desc 'Aire-sur-la-Lys & Thérouanne'): RIGHT page = the full Aire plan (label 'Aire.', the town on its Lys
    # peninsula, compass points, page no. 33); LEFT page = two framed insets, 'Terwan' (the Thérouanne
    # pentagon) and a second small settlement. Staged ONCE under Aire; Thérouanne gets its own standalone row
    # (iter 52, eye check /tmp/vd_fr_thumbs/, lead doc). Not staged: the two SVG redraws (900x768, 2540x2677)
    # and the 992x800 '...Plan de Deventer.jpg' (QS 1550-1565, a grainy halftone book reproduction - redundant
    # with this sheet)
    "Arras": dict(region="france", cat="Map of Arras by Jacob van Deventer",
                  qid="Q131329", label="Arras", lon=2.78, lat=50.2892, p625=(2.78, 50.289167),
                  place="Pas-de-Calais", wikipedia="https://en.wikipedia.org/wiki/Arras", p373="Arras",
                  file="File:Arras (2) - Deventer.jpg"),  # the wide sheet (3184x2614): the full two-page
    # drawing with the town label, shield, compass points and scale; (1) (1816x2614) is a single page of the
    # same drawing (the old town cut off at the right edge) - not staged (the Mons (1)/(2) precedent; iter 52)
    "Avesnes-sur-Helpe": dict(region="france", cat="Map of Avesnes-sur-Helpe by Jacob van Deventer",
                              qid="Q217178", label="Avesnes-sur-Helpe", lon=3.9327, lat=50.1224, p625=(3.932676, 50.122394),
                              place="Nord", wikipedia="https://en.wikipedia.org/wiki/Avesnes-sur-Helpe",
                              p373="Avesnes-sur-Helpe",
                              file="File:Avesnes-sur-Helpe - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Bapaume": dict(region="france", cat="Map of Bapaume by Jacob van Deventer",
                    qid="Q317235", label="Bapaume", lon=2.8511, lat=50.1036, p625=(2.851111, 50.103611),
                    place="Pas-de-Calais", wikipedia="https://en.wikipedia.org/wiki/Bapaume", p373="Bapaume",
                    file="File:Bapaume - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Bavay": dict(region="france", cat="Map of Bavay by Jacob van Deventer",
                  qid="Q477176", label="Bavay", lon=3.7981, lat=50.2975, p625=(3.798056, 50.2975),
                  place="Nord", wikipedia="https://en.wikipedia.org/wiki/Bavay", p373="Bavay",
                  file="File:Bavay - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Bouchain": dict(region="france", cat="Map of Bouchain by Jacob van Deventer",
                     qid="Q632348", label="Bouchain", lon=3.3169, lat=50.2842, p625=(3.316944, 50.284167),
                     place="Nord", wikipedia="https://en.wikipedia.org/wiki/Bouchain", p373="Bouchain",
                     file="File:Bouchain - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Béthune": dict(region="france", cat="Map of Béthune by Jacob van Deventer",
                    qid="Q207145", label="Béthune", lon=2.6393, lat=50.531, p625=(2.639326, 50.53095),
                    place="Pas-de-Calais", wikipedia="https://en.wikipedia.org/wiki/B%C3%A9thune", p373="Béthune",
                    file="File:Béthune - Deventer.jpg"),  # the 1545 wide sheet (3442x2614); the two SVG
    # redraws (656x687, 2585x2477) are not staged
    "Cambrai": dict(region="france", cat="Map of Cambrai by Jacob van Deventer",
                    qid="Q181285", label="Cambrai", lon=3.2347, lat=50.1758, p625=(3.234722, 50.175833),
                    place="Nord", wikipedia="https://en.wikipedia.org/wiki/Cambrai", p373="Cambrai",
                    file="File:Cambrai - Deventer.jpg"),  # the 1545 wide sheet (3722x2614)
    "Condé-sur-l'Escaut": dict(region="france", cat="Map of Condé-sur-l'Escaut by Jacob van Deventer",
                               search="Condé-sur-l'Escaut",
                               qid="Q494533", label="Condé-sur-l'Escaut", lon=3.5906, lat=50.4492,
                               p625=(3.590556, 50.449167),
                               place="Nord", wikipedia="https://en.wikipedia.org/wiki/Cond%C3%A9-sur-l%27Escaut",
                               p373="Condé-sur-l'Escaut",
                               file="File:Condé-sur-l'Escaut - Deventer.jpg"),  # the 1545 wide sheet (3529x2614)
    "Douai": dict(region="france", cat="Map of Douai by Jacob van Deventer",
                  qid="Q193826", label="Douai", lon=3.0792, lat=50.3708, p625=(3.079167, 50.370833),
                  place="Nord", wikipedia="https://en.wikipedia.org/wiki/Douai", p373="Douai",
                  file="File:Douai (2) - Deventer.jpg"),  # the wide sheet (3665x2614): the full two-page
    # drawing (the town label, shield, compass points and scale); (1) (1816x2614) is the drawing on its own
    # page (larger scale, no label/compass) - not staged (iter 52). P131 also carries the historical
    # 'County of Flanders' (the c. 1550 context of the drawing); the row's place is the modern department
    # (lead doc)
    "Gravelines": dict(region="france", cat="Map of Gravelines by Jacob van Deventer",
                       qid="Q323399", label="Gravelines", lon=2.1275, lat=50.9864, p625=(2.1275, 50.986389),
                       place="Nord", wikipedia="https://en.wikipedia.org/wiki/Gravelines", p373="Gravelines",
                       file="File:Gravelines - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Hesdin": dict(region="france", cat="Map of Hesdin by Jacob van Deventer",
                   qid="Q467366", label="Hesdin", lon=2.0367, lat=50.3742, p625=(2.036667, 50.374167),
                   place="Pas-de-Calais", wikipedia="https://en.wikipedia.org/wiki/Hesdin", p373="Hesdin",
                   file="File:Hesdin - Deventer.jpg"),  # the double sheet (3408x2614, page 30): LEFT = the big
    # bastioned star fort labelled 'Hesdyn fort.' + a blank shield (the 1554-1575 fortification) + a small
    # framed inset; RIGHT = the framed pentagon 'Hesdyn' (the moated old town with its hill-top fort) = the
    # Vieil-Hesdin plan. The page date is a French note (Hesdin plan 1554-1575; Vieil-Hesdin 'probablement
    # 1545') - kept as-is, year_of takes the min (1545, in the c. 1545-1565 window). Staged ONCE under Hesdin;
    # Vieil-Hesdin gets its own standalone scan (iter 52, eye check, lead doc)
    "Landrecies": dict(region="france", cat="Map of Landrecies by Jacob van Deventer",
                       qid="Q632808", label="Landrecies", lon=3.69, lat=50.1256, p625=(3.69, 50.125556),
                       place="Nord", wikipedia="https://en.wikipedia.org/wiki/Landrecies", p373="Landrecies",
                       file="File:Landrecies - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614). Not
    # staged: the five 'Plan de Landrecies, détail ... KBR' files (1091-1805 px, QS 1550-1565, detail crops,
    # two of them annotated) - lead doc
    "Le Cateau-Cambrésis": dict(region="france", cat="Map of Le Cateau-Cambrésis by Jacob van Deventer",
                                qid="Q329103", label="Le Cateau-Cambrésis", lon=3.5411, lat=50.1053,
                                p625=(3.541111, 50.105278),
                                place="Nord", wikipedia="https://en.wikipedia.org/wiki/Le_Cateau-Cambr%C3%A9sis",
                                p373="Le Cateau-Cambrésis",
                                file="File:Le Cateau-Cambrésis - Deventer.jpg"),  # the 1545 BNE atlas plate (1816x2614)
    "Le Quesnoy": dict(region="france", cat="Map of Le Quesnoy by Jacob van Deventer",
                       qid="Q180067", label="Le Quesnoy", lon=3.6375, lat=50.2489, p625=(3.6375, 50.248889),
                       place="Nord", wikipedia="https://en.wikipedia.org/wiki/Le_Quesnoy", p373="Le Quesnoy",
                       file="File:Le Quesnoy - Deventer.jpg"),  # the 1545 wide sheet (3447x2614); the two
    # SVG redraws (760x686, 2624x2352) are not staged
    "Lille": dict(region="france", cat="Map of Lille by Jacob van Deventer",
                  qid="Q648", label="Lille", lon=3.0575, lat=50.6319, p625=(3.0575, 50.631944),
                  place="Nord", wikipedia="https://en.wikipedia.org/wiki/Lille", p373="Lille",
                  file="File:Lille (2) - Deventer.jpg"),  # the wide sheet (3614x2614): the full two-page
    # drawing (the town label, shield, compass points and scale); (1) (1816x2614) is the drawing on its own
    # page - not staged. Also not staged: 'Lille vers 1550 sur plan Deventer.png' (625x452, uploaded 2022)
    # and the two SVG redraws of (2) (1340x1410, 3800x3055)
    "Maubeuge": dict(region="france", cat="Map of Maubeuge by Jacob van Deventer",
                     qid="Q138648", label="Maubeuge", lon=3.9725, lat=50.2769, p625=(3.9725, 50.276944),
                     place="Nord", wikipedia="https://en.wikipedia.org/wiki/Maubeuge", p373="Maubeuge",
                     file="File:Maubeuge - Deventer.jpg"),  # the 1545 wide sheet (3481x2614)
    "Saint-Omer": dict(region="france", cat="Map of Saint-Omer by Jacob van Deventer",
                       qid="Q208793", label="Saint-Omer", lon=2.2608, lat=50.7483, p625=(2.260833, 50.748333),
                       place="Pas-de-Calais", wikipedia="https://en.wikipedia.org/wiki/Saint-Omer",
                       p373="Saint-Omer",
                       file="File:Saint-Omer (2) - Deventer.jpg"),  # the wide sheet (3449x2614): the full
    # two-page drawing, sheet label 'S. Omeri', page 34; (1) (1816x2614) is the drawing on its own page -
    # not staged
    "Thérouanne": dict(region="france", cat="Map of Thérouanne by Jacob van Deventer",
                       qid="Q261399", label="Thérouanne", lon=2.2589, lat=50.6367, p625=(2.258889, 50.636667),
                       place="Pas-de-Calais", wikipedia="https://en.wikipedia.org/wiki/Th%C3%A9rouanne",
                       p373="Thérouanne",
                       file="File:Thérouanne - Deventer.jpg"),  # the standalone 'Terwan' plan (986x867, 1545:
    # pentagon, compass, bridge) - the ONLY Thérouanne plan on Commons, staged with the Ostend/Aardenburg
    # size caveat; the 3395x2614 Aire/Thérouanne spread is staged under Aire (its left-page inset), iter 52
    "Valenciennes": dict(region="france", cat="Map of Valenciennes by Jacob van Deventer",
                         qid="Q163795", label="Valenciennes", lon=3.5233, lat=50.3581, p625=(3.523333, 50.358056),
                         place="Nord", wikipedia="https://en.wikipedia.org/wiki/Valenciennes", p373="Valenciennes",
                         file="File:Valenciennes (2) - Deventer.jpg"),  # the wide sheet (4156x2614): the full
    # two-page drawing with the cursive town label; (1) (1816x2614) is the drawing on its own page - not
    # staged
    "Vieil-Hesdin": dict(region="france", cat="Map of Vieil-Hesdin by Jacob van Deventer",
                         qid="Q1022768", label="Vieil-Hesdin", lon=2.0989, lat=50.3575, p625=(2.098889, 50.3575),
                         place="Pas-de-Calais", wikipedia="https://en.wikipedia.org/wiki/Vieil-Hesdin",
                         p373="Vieil-Hesdin",
                         file="File:Vieil-Hesdin - Deventer.jpg"),  # the standalone scan (757x857, 1545) of
    # the right-page inset of the Hesdin double sheet (compared pixel-for-pixel, iter 52) - the only
    # standalone Vieil-Hesdin plan, staged with the size caveat
    "Bergues": dict(region="france", cat="Map of Bergues by Jacob van Deventer", qid="Q244934", done=True),
    # -- Luxembourg (1 category; the city). file= recorded in iter 52 (transcript /tmp/vd_files_fr_iter50.txt
    # + the 1280 px eye check /tmp/vd_fr_thumbs/): the 1550 hand-coloured drawing, desc 'Lutzenburg'. --
    "Luxembourg City": dict(region="luxembourg", cat="Maps of Luxembourg City Jacob van Deventer",
                            search="Luxembourg City",
                            qid="Q1842", label="Luxembourg", lon=6.13, lat=49.6114, p625=(6.13, 49.611389),
                            place="Canton of Luxembourg", wikipedia="https://en.wikipedia.org/wiki/Luxembourg_City",
                            p373="Luxembourg City",
                            file="File:Luxemburg 1550 65 v Deventer.jpg", caption="Lutzenburg"),  # the city's
    # item is Q1842 (the hand-over's Q1564 now holds 'Borgfelde', Hamburg - that id was merged away; the search
    # 'Luxembourg (city)' returned EMPTY, the parenthesized-label quirk, so search="Luxembourg City" - it hits
    # Q1842 first; transcript /tmp/vd_lu_iter49.txt). region "luxembourg" is a NEW value build_catalog's
    # REGION_NAME has no key for (the display falls back to the raw value - flagged in the lead doc). Q1842 is
    # not in the built catalog. file= (iter 52): the 2261x1878 hand-coloured drawing on laid paper (page date
    # 1550 = the drawing's, desc 'Lutzenburg'): the label 'Lutzenburg' + a blank shield, the Dutch compass
    # Noorde/West/Oost/Zuydt, the Alzette with the Bock rock and the old castle, the new bastioned fort to the
    # west. caption="Lutzenburg" is REQUIRED: the label 'Luxembourg' is not in the title/desc (the file prints
    # the historical spelling) - without it the caption check fails. Not staged: 'Lutzenburg.jpg' (1600x1200,
    # uploaded 2005, desc 'published first 1609'), 'Lutzenburg 1581 Sanderus.jpg' (1909x1599, the 1581 Sanderus
    # print) and 'Couvent Knödler 1550.jpg' (644x468, a detail crop)
}

# The verified category chains, per town: the parents of the town file category up to the town's P373 category
# (live-walked by --chain on 2026-10-11, iteration 55; transcript /tmp/vd_chains_iter55.txt). Each value is the
# walked via list EXACTLY as --chain prints it: via[-1] == p373, the file category is not in via.
# check_category re-verifies only the chain's shape, so the walked path recorded here IS the verification -
# never type or edit one by hand. A town absent from this table failed its walk (depth cap 6 or the fetch
# cap) and rides the caption route; the per-town reasons are in docs/lead_van_deventer.md.
CHAINS = {
}


def chain_of(town):
    """The verified category chain of the town's staged file (the CHAINS table, or an inline TOWNS "chain"): None
    when the walk failed - the town then rides the caption route."""
    return TOWNS[town].get("chain") or CHAINS.get(town)


def now():
    return time.strftime("%Y-%m-%d")


def _commons():
    import commons  # lazy: commons -> aw needs numpy (absent from the system python3)
    return commons


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def _datavalues(claims):
    return [x["mainsnak"]["datavalue"]["value"] for x in claims if "datavalue" in x.get("mainsnak", {})]


def _ids(claims):
    return [v.get("id") for v in _datavalues(claims) if isinstance(v, dict) and v.get("id")]


def known_sites():
    """{qid: site id} over the built sites, the catalog and the extras (a source never makes a second site for a
    place: a town whose QID is already cataloged gets its picture row under that existing site id, no new row)."""
    out = {}
    for p in (os.path.join(ROOT, "data", "catalog", "sites.jsonl"), os.path.join(ROOT, "data", "catalog", "extras.jsonl")):
        for s in _load(p):
            if s.get("qid") and s["qid"] not in out:
                out[s["qid"]] = s["id"]
    for s in json.load(open(os.path.join(ROOT, "web", "data", "sites.json"), encoding="utf-8"))["sites"]:
        if s.get("qid") and s["qid"] not in out:
            out[s["qid"]] = s["id"]
    return out


def stageable():
    """The towns this task stages: verified (a QID and a picture recorded), not one of the six done."""
    return [t for t, d in TOWNS.items() if d.get("qid") and d.get("file") and not d.get("done")]


# ---------------------------------------------------------------- the live commands (run under .venv/bin/python)

def list_categories():
    """Live: the subcategories of CATALOG_PARENT must be exactly the 66 town categories + the 4 collections
    (renames or new categories fail loud: the TOWNS table is the assertion constant)."""
    c = _commons()
    subs = [t.split(":", 1)[1] for t in c.members(CATALOG_PARENT, "subcat")]
    expect = set(t["cat"] for t in TOWNS.values()) | set(COLLECTIONS)
    if set(subs) != expect:
        print(f"checked {now()}: {len(subs)} subcategories (expected {len(expect)})")
        print("added (not in the table):", sorted(set(subs) - expect))
        print("missing (in the table):  ", sorted(expect - set(subs)))
        raise SystemExit(1)
    print(f"checked {now()}: {len(subs)} subcategories of {CATALOG_PARENT} "
          f"({len(TOWNS)} town categories + {len(COLLECTIONS)} collections) - matches the table")


def _search_candidates(c, town, t):
    """The Wikidata search candidates for the town (label-based search, the R1 recipe): the query is the town
    key, parenthesized qualifiers stripped, an explicit "search" key wins (Groningen province, Utrecht)."""
    name = t.get("search") or re.sub(r"\s*\(.*?\)", "", town).strip()
    d = c.get(c.WD, {"action": "wbsearchentities", "search": name, "language": "en", "limit": "5"})
    return [(e["id"], e.get("label") or e.get("description", {}).get("en", {}).get("value", ""))
            for e in d.get("search", [])]


def verify_qids(only=None):
    """Live: per town the QID fact sheet. Discovery (no qid recorded): the search candidates with their label,
    P625, P373, P131, enwiki - the hand check picks the right item and records it in TOWNS. Re-verification
    (a qid recorded, or no args = the whole table): the recorded item's facts plus the distance from every P625
    to the table point, the P373 match, and the first name-search hit with coordinates (the resolution a bare
    record --live would store; >50 km away is the trap)."""
    import evidence  # hav_m
    c = _commons()
    towns = list(only) if only else [t for t in TOWNS if TOWNS[t].get("qid")]
    for town in towns:
        if town not in TOWNS:
            raise SystemExit(f"unknown town {town!r} (not a TOWNS key)")
    search = {}
    for town in towns:
        search[town] = _search_candidates(c, town, TOWNS[town])
    qids = sorted({q for cands in search.values() for q, _ in cands}
                 | {TOWNS[t]["qid"] for t in towns if TOWNS[t].get("qid")})
    ents = {}
    for i in range(0, len(qids), 50):
        ents.update(c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]),
                                 "props": "claims|sitelinks|labels", "languages": "en"}).get("entities", {}))
    p131s = sorted({i for q, e in ents.items() for i in _ids(e.get("claims", {}).get("P131", []))})
    labels = {}
    for i in range(0, len(p131s), 50):
        d = c.get(c.WD, {"action": "wbgetentities", "ids": "|".join(p131s[i:i + 50]),
                         "props": "labels", "languages": "en"})
        labels.update({k: v.get("labels", {}).get("en", {}).get("value") for k, v in d.get("entities", {}).items()})
    print(f"checked {now()} - {len(towns)} towns (Wikidata)")
    for town in towns:
        t = TOWNS[town]
        if not t.get("qid"):
            print(f"  {town} (no QID yet): search candidates with P625 or enwiki:")
            for q, lab in search.get(town, []):
                e = ents.get(q) or {}
                cl = e.get("claims", {})
                p625 = [(v["longitude"], v["latitude"]) for v in _datavalues(cl.get("P625", [])) if v]
                if not p625 and not e.get("sitelinks", {}).get("enwiki"):
                    continue
                print(f"    {q}  {e.get('labels', {}).get('en', {}).get('value', lab)!r}"
                      f"  P625 {p625}  P373 {_datavalues(cl.get('P373', []))}"
                      f"  P131 {[labels.get(i) for i in _ids(cl.get('P131', []))]}"
                      f"  enwiki {e.get('sitelinks', {}).get('enwiki', {}).get('title')!r}")
            continue
        e = ents.get(t["qid"]) or {}
        cl = e.get("claims", {})
        p625 = [(v["longitude"], v["latitude"]) for v in _datavalues(cl.get("P625", [])) if v]
        en = e.get("labels", {}).get("en", {}).get("value", "")
        tbl = t.get("label")  # the six done towns have no label/point/p373 here (sources.py verifies them)
        have_pt = "lon" in t and "lat" in t
        print(f"  {town}  {t['qid']}  {en!r}" + (f"  (table: {tbl!r})" if tbl is not None else "")
              + ("" if tbl is None or not en or en.lower() == tbl.lower() else "   <- LABEL CHECK"))
        for lon, lat in p625:
            if have_pt:
                dist = evidence.hav_m(lon, lat, t["lon"], t["lat"])
                flag = "" if dist <= 50e3 else f"   <- a P625 is {dist / 1000:.0f} km from the table point (recorded)"
                print(f"      P625: ({lon}, {lat})  table point ({t['lon']}, {t['lat']}), {dist / 1000:.2f} km{flag}")
            else:
                print(f"      P625: ({lon}, {lat})  (no table point here: recorded in pipeline/sources.py)")
        p373 = _datavalues(cl.get("P373", []))
        ok = ("ok" if p373 and p373[0] == t["p373"] else f"MISMATCH (table: {t['p373']!r})") if t.get("p373") else "(none recorded)"
        print(f"      P373: {p373}  ({ok})   P131: {[labels.get(i) for i in _ids(cl.get('P131', []))]}"
              f"  (table place: {t.get('place')!r})")
        print(f"      enwiki: {e.get('sitelinks', {}).get('enwiki', {}).get('title')!r}  (table: {t.get('wikipedia')!r})")
        for q, _ in search.get(town, []):
            p = [(v["longitude"], v["latitude"]) for v in _datavalues((ents.get(q) or {}).get("claims", {}).get("P625", [])) if v]
            if p:
                flag = ""
                if have_pt:
                    d = evidence.hav_m(p[0][0], p[0][1], t["lon"], t["lat"])
                    flag = "" if d <= 50e3 else f"   <- TRAP: a name search would resolve {q} {d / 1000:.0f} km away"
                print(f"      search: first hit with P625 is {q} "
                      f"{(ents.get(q) or {}).get('labels', {}).get('en', {}).get('value')!r} ({p[0]}){flag}")
                break
    return 0


def town_files(only=None):
    """Live: the file inventory of the towns' categories (the lead-doc material and the source of the one staged
    picture per town): each file with its size, mime, date and description, plus which other town categories
    also hold it (misfiled files: a file in two town categories maps to its true town by its own title/desc,
    the R5 cases). A town category's own subcategories are inventoried at depth 1 and tagged [sub: ...] -
    the BNE atlas keeps its per-place plate subcategories inside the towns' categories (verified 2026-10-11:
    Landrecies's 5 plates, the only one so far). After the towns: the 4 collection categories, the same line
    format (the BNE autographs, the NA and the RCE scans flat; the BNE atlas at depth 1); a collection file
    that also sits in an inventoried town category gets the [also in: ...] tag - the R5 cross reference (a
    copy of, or a better scan of, the town's own plan)."""
    c = _commons()
    towns = list(only) if only else list(TOWNS)
    per, seen = {}, {}
    for town in towns:
        cat = TOWNS[town]["cat"]
        files = [(None, f) for f in c.members(cat, "file")]
        for sub in c.members(cat, "subcat"):
            name = sub.split(":", 1)[1]
            files += [(name[len(cat):].strip() or name, f) for f in c.members(name, "file")]
        per[town] = files
        for _, f in files:
            seen.setdefault(f, set()).add(town)
    cols = {}
    for col in COLLECTIONS:
        files = [(None, f) for f in c.members(col, "file")]
        for sub in c.members(col, "subcat"):
            name = sub.split(":", 1)[1]
            files += [(name, f) for f in c.members(name, "file")]
        cols[col] = files
    titles = sorted({f for fl in per.values() for _, f in fl} | {f for fl in cols.values() for _, f in fl})
    meta = c.info(titles) if titles else {}
    for town in towns:
        print(f"  {town}:")
        for sub, f in per[town]:
            m = meta.get(f) or {}
            tag = f"  [sub: {sub}]" if sub else ""
            extra = f"  [also in: {', '.join(sorted(seen[f] - {town}))}]" if len(seen[f]) > 1 else ""
            print(f"    {f}{tag}  {m.get('w')}x{m.get('h')} {m.get('mime')}  date {m.get('date')!r}"
                  f"  {m.get('desc', '')[:120]!r}{extra}")
    print(f"collections (checked {now()}):")
    for col in COLLECTIONS:
        print(f"  {col}:")
        for sub, f in cols[col]:
            m = meta.get(f) or {}
            tag = f"  [sub: {sub}]" if sub else ""
            extra = f"  [also in: {', '.join(sorted(seen.get(f, ())))}]" if f in seen else ""
            print(f"    {f}{tag}  {m.get('w')}x{m.get('h')} {m.get('mime')}  date {m.get('date')!r}"
                  f"  {m.get('desc', '')[:120]!r}{extra}")


def cat_chain(town):
    """Live: walk the parents of the town file's category (the town's van Deventer category) up to the town's
    P373 category: BFS over the category page's containing categories (prop=categories), town-name parents
    first (they shorten the walk), depth cap 6, CHAIN_FETCH_CAP fetches, a visited set. Prints the walked via
    list as JSON (record it in the CHAINS table: via[-1] == the P373 string, the file category NOT in via -
    check_category re-verifies the shape, the walk is the verification), or reports the failed walk (the town
    then rides the caption route)."""
    c = _commons()
    t = TOWNS[town]
    if not t.get("p373"):
        raise SystemExit(f"{town}: no p373 recorded yet (--verify first)")
    target = t["p373"]
    start = t.get("filecat") or t["cat"]
    queue, visited = [start], set()
    via = {start: []}
    fetches, depth = 0, 0
    while queue and depth <= 6:
        nxt = []
        for cat in queue:
            if cat == target:  # checked before the cap: a budget overrun never hides a hit
                chain = via[cat]
                print(f"{town}: chain holds ({len(chain)} hops): {start} -> " + " -> ".join(chain))
                print("record: \"chain\": " + json.dumps(chain))
                return chain
            if fetches >= CHAIN_FETCH_CAP:
                break
            # prop=categories lists the CONTAINING categories of a category page; the old categoryinfo
            # cicategories/ciclimit parameters are unrecognized by the current MediaWiki and are ignored
            # with a warning (the walk would then see zero parents and silently fail for every town).
            d = c.get(c.CM, {"action": "query", "titles": "Category:" + cat,
                             "prop": "categories", "cllimit": "500"})
            if "error" in d or d.get("warnings"):
                raise SystemExit(f"{cat}: API shape change - the walk is not verified: "
                                 f"{d.get('error') or d.get('warnings')}")
            fetches += 1
            parents = [pc.get("title", "").split(":", 1)[-1]
                       for p in d.get("query", {}).get("pages", {}).values()
                       for pc in p.get("categories", [])]
            for p in sorted(parents, key=lambda n: (t.get("label") or town).lower() not in n.lower()):
                if p not in visited:
                    visited.add(p)
                    via[p] = via[cat] + [p]
                    nxt.append(p)
        print(f"  {town} level {depth}: queue {len(queue)}, next {len(nxt)}, fetches {fetches}", flush=True)
        queue, depth = nxt, depth + 1
    if target in visited:  # added by a real fetch (every edge of via[target] was returned by an API response),
        chain = via[target]  # so the path is the walked one even if the fetch cap stopped the pops first
        if len(chain) <= 6:
            print(f"{town}: chain holds ({len(chain)} hops): {start} -> " + " -> ".join(chain))
            print("record: \"chain\": " + json.dumps(chain))
            return chain
        print(f"{town}: {target!r} sits {len(chain)} hops out, beyond the depth cap (the caption route)")
    elif fetches >= CHAIN_FETCH_CAP:
        print(f"{town}: walk capped at {CHAIN_FETCH_CAP} fetches without reaching {target!r} (the caption route)")
    else:
        print(f"{town}: no chain from {start} to {target} within 6 hops (the caption route)")
    return None


# ---------------------------------------------------------------- staging (this task's own files only)

def _site_row(town, t):
    sid = re.sub(r"[^a-z0-9]+", "-", town.lower()).strip("-") + "-" + t["qid"].lower()
    row = {"id": sid, "qid": t["qid"], "name": town, "lon": t["lon"], "lat": t["lat"],
           "region": t["region"], "kind": "town", "aerial_ok": True, "source": "fit/src_van_deventer.py"}
    if t.get("place"):
        row["place"] = t["place"]
    if t.get("wikipedia"):
        row["wikipedia"] = t["wikipedia"]
    return row


def evidence_for(town, m):
    """The offline evidence for the town's staged file (task 200's stored shapes): the category route when the
    walked chain is recorded (the file category runs to the town's P373 category), else the caption route (the
    file names the town; the stored resolution is the verified site point itself - record --live would take the
    first name-search hit instead, the trap), else None (a documented drop, never staged)."""
    import books_match
    t = TOWNS[town]
    chain = chain_of(town)
    if chain:
        return {"rec": "evidence/1", "kind": "category", "checked": now(),
                "site_cat": t["p373"], "file_cat": t["cat"], "via": chain}
    named = t.get("caption") or t.get("label") or town
    hay = books_match.norm(t["file"] + " " + (m.get("desc") or ""))
    if books_match.norm(named) not in hay:
        return None
    return {"rec": "evidence/1", "kind": "caption_coords", "checked": now(),
            "named_place": named, "place_qid": t["qid"], "place_label": t.get("label") or named,
            "place_lon": t["lon"], "place_lat": t["lat"],
            "site_lon": t["lon"], "site_lat": t["lat"], "dist_m": 0.0}


def stage(dry=False):
    """Stage every verified town (a QID, the one picture, and the evidence route) into this task's own staging
    files (append-only, idempotent on (site, title)); 211 consolidates them. Drift fails loud: a title that
    vanished from Commons, or a file commons.keep() would drop (a detail crop or a photo: record the drop in
    docs/lead_van_deventer.md instead)."""
    c = _commons()
    known = known_sites()
    have = {(r.get("site"), r.get("title")) for r in _load(FILES)}
    staged_ids = {s["id"] for s in _load(EXTRAS)}
    titles = [TOWNS[t]["file"] for t in stageable()]
    meta = c.info(titles) if titles else {}
    new_sites, new_files, new_cls, to_build = [], [], [], []
    for town in stageable():
        t = TOWNS[town]
        sid = known.get(t["qid"]) or _site_row(town, t)["id"]
        if known.get(t["qid"]) is None and sid not in staged_ids:
            new_sites.append(_site_row(town, t))
            staged_ids.add(sid)
            to_build.append(sid)
        if (sid, t["file"]) in have:
            continue
        m = meta.get(t["file"]) or {}
        if not m.get("url"):
            raise SystemExit(f"not on Commons (title changed?): {t['file']}")
        want = t.get("date")
        if want and c.year_of(t["file"], m) != c.year_of(t["file"], {"date": want}):
            # the known drawing date on the row, the page value kept as date_commons (the Gouda/Zwolle precedent:
            # Zwolle's 1980 RCE-album reproduction row reads date "circa 1560", date_commons 1980). keep() must
            # see this m: it judges the DRAWING's year, so a post-1925 reproduction of a c. 1550 drawing passes
            # exactly as the done Zwolle row did (sources.py swaps before its keep() gate).
            m = dict(m, date=want, date_commons=m.get("date"))
        if not c.keep(t["file"], m):
            raise SystemExit(f"commons.keep() would drop {t['file']!r}: fix the table or record the drop "
                             f"in docs/lead_van_deventer.md")
        if not evidence_for(town, m):
            raise SystemExit(f"{town}: no evidence route (chain missing and the file does not name the town) - "
                             f"pick a file that does, or record the drop in docs/lead_van_deventer.md")
        f = {"site": sid, "qid": t["qid"], "title": t["file"], "year": c.year_of(t["file"], m),
             "wd_plan": False, "cat": t["p373"] if chain_of(town) else None,
             "name": f"{t.get('label') or town}, town plan by Jacob van Deventer",
             "by": "fit/src_van_deventer.py", **m}
        f["evidence"] = evidence_for(town, m)
        new_files.append(f)
        new_cls.append({"site": sid, "title": t["file"], "p_plan": 1.0, "p_birdseye": 0.0, "p_photo": 0.0,
                        "by": "hand"})
    print(f"staged: {len(new_sites)} new sites, {len(new_files)} new pictures")
    for s in new_sites:
        print("   ", s["id"], s["lon"], s["lat"], s.get("place"))
    if to_build:
        print("build (211):", ",".join(to_build))
    if dry:
        return
    if new_sites:
        with open(EXTRAS, "a", encoding="utf-8") as f:
            for s in new_sites:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
    if new_files:
        with open(FILES, "a", encoding="utf-8") as f:
            for r in new_files:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if new_cls:
        with open(CLASSIFIED, "a", encoding="utf-8") as f:
            for r in new_cls:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


def check_staged():
    """Offline (no network): join the staged files (every file row names a staged or existing site, no staged
    id/QID pre-exists, the six done towns are not re-staged, every staged site has a picture, (site, title)
    unique, no clash with the canonical files.jsonl, the file rows agree with the TOWNS table, classified rows
    1:1) and run fit/evidence.py's check over the staged rows. Returns the exit code (0 iff no problem, no FAIL)."""
    import evidence
    files = _load(FILES)
    sites = _load(EXTRAS)
    cls = _load(CLASSIFIED)
    known = known_sites()
    problems = []
    staged_ids = {s["id"] for s in sites}
    if staged_ids & set(known.values()):
        problems.append(f"staged site ids collide with existing sites: {sorted(staged_ids & set(known.values()))}")
    for s in sites:
        if s.get("qid") in known:
            problems.append(f"staged site {s['id']} re-uses existing QID {s['qid']} ({known[s['qid']]})")
    done = {TOWNS[t]["qid"] for t in TOWNS if TOWNS[t].get("done")}
    if done & {s.get("qid") for s in sites}:
        problems.append(f"the six done towns are re-staged: {sorted(done & {s.get('qid') for s in sites})}")
    pics = {s["id"]: 0 for s in sites}
    valid = set(pics) | set(known.values())
    town_of = {}  # staged site id -> TOWNS key, over the fully recorded towns (slug id and, when the QID is
    # already cataloged, the existing site id it stages under; the six done towns are never staged)
    for tn, td in TOWNS.items():
        if td.get("qid") and "lon" in td and not td.get("done"):
            town_of[_site_row(tn, td)["id"]] = tn
            if known.get(td["qid"]):
                town_of[known[td["qid"]]] = tn
    seen, canonical = set(), {(r.get("site"), r.get("title")) for r in _load(FILES_CANONICAL)}
    for r in files:
        sid = r.get("site")
        if sid not in valid:
            problems.append(f"file row names a site that is neither staged nor existing: {sid!r} ({r.get('title')!r})")
            continue
        if sid in pics:
            pics[sid] += 1
        k = (sid, r.get("title"))
        if k in seen:
            problems.append(f"duplicate staged row {k}")
        if k in canonical:
            problems.append(f"staged title already in the canonical files.jsonl: {k}")
        seen.add(k)
        town = town_of.get(sid)
        if town and r.get("qid") != TOWNS[town]["qid"]:
            problems.append(f"file row {k} carries QID {r.get('qid')}, the table has {TOWNS[town]['qid']}")
        if town and r.get("title") != TOWNS[town].get("file"):
            problems.append(f"file row {k} is not the table's file for {town}")
    for sid in pics:
        if not pics[sid]:
            problems.append(f"staged site {sid} has no staged picture")
    if {(r.get("site"), r.get("title")) for r in cls} != seen:
        problems.append("the classified rows are not 1:1 with the staged file rows")
    for p in problems:
        print("join:", p)
    code, text = evidence.check(FILES, NO_BOOKS, catalog=EXTRAS)
    print(text)
    return 1 if problems else code


def _norm(rows):
    """The rows for the golden file: keys sorted by the dump, "checked" and "date_commons" normalized (they vary
    with the staging date)."""
    out = []
    for r in rows:
        r = dict(r)
        if isinstance(r.get("date_commons"), str):
            r["date_commons"] = "0000-00-00"
        ev = r.get("evidence")
        if isinstance(ev, dict) and ev.get("checked"):
            r["evidence"] = dict(ev, checked="0000-00-00")
        out.append(r)
    return out


def golden(path=None):
    """Write tests/golden/src_van_deventer_sample.json: a sample of the staged rows - the first two towns per
    evidence kind (category, then caption_coords, in the TOWNS order) - plus the full staged row counts.
    Regenerate only for an intended change."""
    p = path or os.path.join(ROOT, "tests", "golden", "src_van_deventer_sample.json")
    files = _load(FILES)
    sites = _load(EXTRAS)
    cls = _load(CLASSIFIED)
    known = known_sites()
    files_by_site = {r.get("site"): r for r in files}
    row_of = {}  # TOWNS key -> its staged file row (under the slug id or the existing site id)
    for town, t in TOWNS.items():
        if t.get("qid") and t.get("file") and not t.get("done"):
            row_of[town] = files_by_site.get(known.get(t["qid"]) or _site_row(town, t)["id"])
    picks = []
    for kind in ("category", "caption_coords"):
        picks += [t for t in TOWNS if (row_of.get(t) or {}).get("evidence", {}).get("kind") == kind][:2]
    out = {"count": {"extras": len(sites), "files": len(files), "classified": len(cls)},
           "extras": _norm([s for s in sites if any(s["id"] == r.get("site") for r in files
                                                   and r.get("title") in (TOWNS.get(t, {}).get("file") for t in picks))]),
           "files": _norm([r for r in files if any(r.get("title") == TOWNS[t].get("file") for t in picks)]),
           "classified": _norm([c for c in cls if any(c.get("title") == TOWNS[t].get("file") for t in picks)])}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", p)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("stage",):
        stage("--dry" in a)
    elif a[0] == "--list":
        list_categories()
    elif a[0] == "--files":
        town_files(a[1:] or None)
    elif a[0] == "--verify":
        raise SystemExit(verify_qids(a[1:] or None))
    elif a[0] == "--chain":
        if len(a) < 2:
            raise SystemExit(__doc__.split("usage:")[1].strip())
        cat_chain(a[1])
    elif a[0] == "--check":
        raise SystemExit(check_staged())
    elif a[0] == "--golden":
        golden()
    else:
        raise SystemExit(__doc__.split("usage:")[1].strip())
