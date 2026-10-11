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
# chain: the verified category chain (the file category's parents up to p373; the category evidence kind).
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
    # -- Belgium (22 categories: 20 to stage + the 2 done). QIDs hand-verified 2026-10-11 in one --verify
    # discovery run (transcript /tmp/vd_verify_be_iter45.txt): every label matches the town (Leuze's
    # verified item carries the official disambiguated name 'Leuze-en-Hainaut'), every P373 is its exact
    # recorded string, every P625 sits at the town; the site point is the P625 rounded (the hand check
    # found no offset from the old-town centre, unlike the NL Gouda 800 m case). Four items carry a
    # disambiguated P373 (Brussels 'Brussels (municipality)', Halle 'Halle (Belgium)', Mons
    # 'Mons (Hainaut)', Leuze 'Leuze-en-Hainaut') - the category route targets that exact string, the
    # chain walk must reach it. Mons was NOT in its search's top 5 (the French communes outrank it - the
    # batch's biggest trap, found by a follow-up search at limit 20; lead doc). No BE QID is in the built
    # catalog (the 12575-site check of 2026-10-11): all 20 get new catalog entries. --
    "Ath": dict(region="belgium", cat="Map of Ath by Jacob van Deventer",
                qid="Q95096", label="Ath", lon=3.7769, lat=50.6311, p625=(3.776941, 50.631139),
                place="Arrondissement of Ath", wikipedia="https://en.wikipedia.org/wiki/Ath", p373="Ath"),
    "Braine-le-Comte": dict(region="belgium", cat="Map of Braine-le-Comte by Jacob van Deventer",
                            qid="Q95129", label="Braine-le-Comte", lon=4.1361, lat=50.6097, p625=(4.136111, 50.609722),
                            place="Arrondissement of Soignies", wikipedia="https://en.wikipedia.org/wiki/Braine-le-Comte",
                            p373="Braine-le-Comte"),
    "Bruges": dict(region="belgium", cat="Maps of Bruges by Jacob van Deventer",
                   qid="Q12994", label="Bruges", lon=3.2242, lat=51.2089, p625=(3.224167, 51.208889),
                   place="Arrondissement of Bruges", wikipedia="https://en.wikipedia.org/wiki/Bruges", p373="Bruges"),
    "Brussels": dict(region="belgium", cat="Maps of Brussels by Jacob van Deventer",
                     qid="Q239", label="Brussels", lon=4.3517, lat=50.8467, p625=(4.351667, 50.846667),
                     place="Arrondissement of Brussels-Capital",
                     wikipedia="https://en.wikipedia.org/wiki/City_of_Brussels", p373="Brussels (municipality)"),
    "Chimay": dict(region="belgium", cat="Map of Chimay by Jacob van Deventer",
                   qid="Q95380", label="Chimay", lon=4.3173, lat=50.0479, p625=(4.317334, 50.047927),
                   place="Arrondissement of Thuin", wikipedia="https://en.wikipedia.org/wiki/Chimay", p373="Chimay"),
    "Chièvres": dict(region="belgium", cat="Map of Chièvres by Jacob van Deventer",
                     qid="Q95318", label="Chièvres", lon=3.8, lat=50.5833, p625=(3.8, 50.583333),
                     place="Arrondissement of Ath", wikipedia="https://en.wikipedia.org/wiki/Chièvres", p373="Chièvres"),
    "Enghien": dict(region="belgium", cat="Map of Enghien by Jacob van Deventer",
                    qid="Q666238", label="Enghien", lon=4.0411, lat=50.6956, p625=(4.041111, 50.695556),
                    place="Arrondissement of Soignies", wikipedia="https://en.wikipedia.org/wiki/Enghien", p373="Enghien"),
    "Ghent": dict(region="belgium", cat="Map of Ghent by Jacob van Deventer",
                  qid="Q1296", label="Ghent", lon=3.7253, lat=51.0536, p625=(3.725278, 51.053611),
                  place="East Flanders", wikipedia="https://en.wikipedia.org/wiki/Ghent", p373="Ghent"),
                  # Q1296 was already hand-verified in the prep (2026-10-11 01:32: label, P373, P625 at the city
                  # centre, enwiki) - the only QID verified before the batch; this run re-confirms it
    "Halle": dict(region="belgium", cat="Map of Halle by Jacob van Deventer",
                  qid="Q210003", label="Halle", lon=4.2372, lat=50.7361, p625=(4.237222, 50.736111),
                  place="Arrondissement of Halle-Vilvoorde",
                  wikipedia="https://en.wikipedia.org/wiki/Halle,_Belgium", p373="Halle (Belgium)"),
    "Kortrijk": dict(region="belgium", cat="Map of Kortrijk by Jacob van Deventer",
                     qid="Q12995", label="Kortrijk", lon=3.2658, lat=50.8275, p625=(3.265833, 50.8275),
                     place="Arrondissement of Kortrijk", wikipedia="https://en.wikipedia.org/wiki/Kortrijk",
                     p373="Kortrijk"),
    "Lessines": dict(region="belgium", cat="Map of Lessines by Jacob van Deventer",
                     qid="Q667790", label="Lessines", lon=3.83, lat=50.7117, p625=(3.83, 50.7117),
                     place="Arrondissement of Soignies", wikipedia="https://en.wikipedia.org/wiki/Lessines",
                     p373="Lessines"),
    "Leuze": dict(region="belgium", cat="Map of Leuze by Jacob van Deventer",
                  qid="Q667862", label="Leuze-en-Hainaut", lon=3.6167, lat=50.6, p625=(3.616667, 50.6),
                  place="Arrondissement of Tournai", wikipedia="https://en.wikipedia.org/wiki/Leuze-en-Hainaut",
                  p373="Leuze-en-Hainaut"),
                  # the verified item's label is the official disambiguated name (the search 'Leuze' first hits
                  # the French Leuze (Aisne), Q326134 - the trap, lead doc)
    "Mechelen": dict(region="belgium", cat="Map of Mechelen by Jacob van Deventer",
                     qid="Q162022", label="Mechelen", lon=4.4803, lat=51.0281, p625=(4.480278, 51.028056),
                     place="Arrondissement of Mechelen", wikipedia="https://en.wikipedia.org/wiki/Mechelen",
                     p373="Mechelen"),
    "Mons": dict(region="belgium", cat="Map of Mons by Jacob van Deventer",
                 qid="Q83407", label="Mons", lon=3.9525, lat=50.4547, p625=(3.9525, 50.454722),
                 place="County of Hainaut", wikipedia="https://en.wikipedia.org/wiki/Mons,_Belgium",
                 p373="Mons (Hainaut)"),
                 # the search 'Mons' (limit 5) returns only the planetary term and French communes; the Belgian
                 # city is 11th in the en results (4th in the fr) - found by a follow-up search at limit 20 (lead doc)
    "Ostend": dict(region="belgium", cat="Map of Ostend by Jacob van Deventer",
                   qid="Q12996", label="Ostend", lon=2.9194, lat=51.2258, p625=(2.919444, 51.225833),
                   place="Arrondissement of Ostend", wikipedia="https://en.wikipedia.org/wiki/Ostend", p373="Ostend"),
    "Saint-Ghislain": dict(region="belgium", cat="Map of Saint-Ghislain by Jacob van Deventer",
                           qid="Q668950", label="Saint-Ghislain", lon=3.8167, lat=50.45, p625=(3.816667, 50.45),
                           place="Arrondissement of Mons", wikipedia="https://en.wikipedia.org/wiki/Saint-Ghislain",
                           p373="Saint-Ghislain"),
    "Soignies": dict(region="belgium", cat="Map of Soignies by Jacob van Deventer",
                     qid="Q462985", label="Soignies", lon=4.0667, lat=50.5667, p625=(4.066667, 50.566667),
                     place="Arrondissement of Soignies", wikipedia="https://en.wikipedia.org/wiki/Soignies",
                     p373="Soignies"),
    "Tournai": dict(region="belgium", cat="Map of Tournai by Jacob van Deventer",
                    qid="Q173219", label="Tournai", lon=3.3881, lat=50.6056, p625=(3.388056, 50.605556),
                    place="Arrondissement of Tournai", wikipedia="https://en.wikipedia.org/wiki/Tournai",
                    p373="Tournai"),
    "Aarschot": dict(region="belgium", cat="Maps of Aarschot by Jacob van Deventer",
                     qid="Q273442", label="Aarschot", lon=4.8333, lat=50.9842, p625=(4.8333, 50.9842),
                     place="Arrondissement of Leuven", wikipedia="https://en.wikipedia.org/wiki/Aarschot",
                     p373="Aarschot"),
    "Oudenaarde": dict(region="belgium", cat="Maps of Oudenaarde by Jacob van Deventer",
                       qid="Q12992", label="Oudenaarde", lon=3.6, lat=50.85, p625=(3.6, 50.85),
                       place="Arrondissement of Oudenaarde", wikipedia="https://en.wikipedia.org/wiki/Oudenaarde",
                       p373="Oudenaarde"),
    "Damme": dict(region="belgium", cat="Map of Damme by Jacob van Deventer", qid="Q323408", done=True),
    "Binche": dict(region="belgium", cat="Map of Binche by Jacob van Deventer", qid="Q95121", done=True),
    # -- France (24 categories: 23 to stage + the 1 done; Beaumont's country settles at verification: the
    # Hainaut candidate (Belgium) vs the northern-France candidates decide it, the Barnard-Castle-style trap) --
    "Aire-sur-la-Lys": dict(region="france", cat="Map of Aire-sur-la-Lys by Jacob van Deventer"),
    "Arras": dict(region="france", cat="Map of Arras by Jacob van Deventer"),
    "Avesnes-sur-Helpe": dict(region="france", cat="Map of Avesnes-sur-Helpe by Jacob van Deventer"),
    "Bapaume": dict(region="france", cat="Map of Bapaume by Jacob van Deventer"),
    "Bavay": dict(region="france", cat="Map of Bavay by Jacob van Deventer"),
    "Beaumont": dict(region="france", cat="Map of Beaumont by Jacob van Deventer"),
    "Bouchain": dict(region="france", cat="Map of Bouchain by Jacob van Deventer"),
    "Béthune": dict(region="france", cat="Map of Béthune by Jacob van Deventer"),
    "Cambrai": dict(region="france", cat="Map of Cambrai by Jacob van Deventer"),
    "Condé-sur-l'Escaut": dict(region="france", cat="Map of Condé-sur-l'Escaut by Jacob van Deventer",
                               search="Condé-sur-l'Escaut"),
    "Douai": dict(region="france", cat="Map of Douai by Jacob van Deventer"),
    "Gravelines": dict(region="france", cat="Map of Gravelines by Jacob van Deventer"),
    "Hesdin": dict(region="france", cat="Map of Hesdin by Jacob van Deventer"),
    "Landrecies": dict(region="france", cat="Map of Landrecies by Jacob van Deventer"),
    "Le Cateau-Cambrésis": dict(region="france", cat="Map of Le Cateau-Cambrésis by Jacob van Deventer"),
    "Le Quesnoy": dict(region="france", cat="Map of Le Quesnoy by Jacob van Deventer"),
    "Le Rœulx": dict(region="france", cat="Map of Le Rœulx by Jacob van Deventer", search="Le Rœulx"),
    "Lille": dict(region="france", cat="Map of Lille by Jacob van Deventer"),
    "Maubeuge": dict(region="france", cat="Map of Maubeuge by Jacob van Deventer"),
    "Saint-Omer": dict(region="france", cat="Map of Saint-Omer by Jacob van Deventer"),
    "Thérouanne": dict(region="france", cat="Map of Thérouanne by Jacob van Deventer"),
    "Valenciennes": dict(region="france", cat="Map of Valenciennes by Jacob van Deventer"),
    "Vieil-Hesdin": dict(region="france", cat="Map of Vieil-Hesdin by Jacob van Deventer"),
    "Bergues": dict(region="france", cat="Map of Bergues by Jacob van Deventer", qid="Q244934", done=True),
    # -- Luxembourg (1 category; the city) --
    "Luxembourg City": dict(region="luxembourg", cat="Maps of Luxembourg City Jacob van Deventer",
                            search="Luxembourg (city)"),
}

# The verified category chains, per town: the parents of the town file category up to the town's P373 category
# (live-walked by --chain; via[-1] == p373, the file category is not in via). Recorded in the TOWNS entry as
# "chain" once the walk succeeds; a failed walk goes to the caption route (or a documented drop).


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
    P373 category: BFS over the category page's containing categories, town-name parents first (they shorten
    the walk), depth cap 6, a visited set. Prints the walked via list as JSON (record it in the TOWNS entry as
    "chain": via[-1] == the P373 string, the file category NOT in via - check_category re-verifies the shape,
    the walk is the verification), or reports the failed walk (the town then rides the caption route)."""
    c = _commons()
    t = TOWNS[town]
    if not t.get("p373"):
        raise SystemExit(f"{town}: no p373 recorded yet (--verify first)")
    target = t["p373"]
    start = t.get("filecat") or t["cat"]
    queue, visited = [start], set()
    via = {start: []}
    depth = 0
    while queue and depth <= 6:
        nxt = []
        for cat in queue:
            if cat == target:
                chain = via[cat]
                print(f"{town}: chain holds ({len(chain)} hops): {start} -> " + " -> ".join(chain))
                print("record: \"chain\": " + json.dumps(chain))
                return chain
            d = c.get(c.CM, {"action": "query", "titles": "Category:" + cat,
                             "prop": "categoryinfo", "cicategories": "1", "ciclimit": "500"})
            pages = d.get("query", {}).get("pages", {}).values()
            parents = [p.get("allcategories", [{}])[i].get("title", "").split(":", 1)[-1]
                       for p in pages for i in range(len(p.get("allcategories", [])))]
            for p in sorted(parents, key=lambda n: (t.get("label") or town).lower() not in n.lower()):
                if p not in visited:
                    visited.add(p)
                    via[p] = via[cat] + [p]
                    nxt.append(p)
        queue = nxt
        depth += 1
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
    if t.get("chain"):
        return {"rec": "evidence/1", "kind": "category", "checked": now(),
                "site_cat": t["p373"], "file_cat": t["cat"], "via": t["chain"]}
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
             "wd_plan": False, "cat": t["p373"] if t.get("chain") else None,
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
