"""Fort plans of the German Limes from the old reports (task 208, GOAL.md point 4): the free, machine-readable
fort plans of the ORL series - "Der obergermanisch-raetische Limes des Roemerreiches" (Reichs-Limes-Kommission,
1893-1915, public domain). Three verified sources (docs/lead_limes.md): the Internet Archive's 1895 scan of
ORL Lieferung II = Band IV Abt B Nr. 40 "Das Kastell Osterburken" (two plan plates), the 45 de.wikipedia
files of the Abt B fort monographs (Grundrisse and the Anhausen fortlet pair), and the 9 disjoint Commons
plates (01x2, 12, 33x5, 31x2) - 56 plans of 43 ORL forts, staged here with hand-recorded caption+coordinates
evidence (the P373 category route is dead: of 103 ORL-ish Commons files only two direct category
memberships exist, both on non-plan files; the 64/67 forts have no Wikidata item and stage on
name+coordinates per the task Notes). The staging is fully offline: every value below was verified against
the live file pages in the research sessions (the artifacts live in /tmp, the verification trail in
docs/lead_limes.md and DECISIONS.md), so stage() makes no network calls; fit/evidence.py re-verifies the
stored ties offline (200's fail-closed box). 211 consolidates the staging files into the canonical ones.

usage: src_limes.py [--dry]     stage the 56 file rows + 45 extras rows + 56 classified rows into this task's
                                own staging files (append-only, idempotent on (site, title)); --dry prints
                                what would be written
       src_limes.py --check     offline (no network): join the staged files and run fit/evidence.py's check
                                over every staged row
       src_limes.py --golden    write tests/golden/src_limes_sample.json (one staged file row per source,
                                normalized; regenerate only for an intended change)
"""
import json
import os
import re
import sys
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))

SITES_JSONL = os.path.join(ROOT, "data", "catalog", "sites.jsonl")
EXTRAS = os.path.join(ROOT, "data", "catalog", "extras.jsonl")
EXTRAS_LIMES = os.path.join(ROOT, "data", "catalog", "extras_limes.jsonl")
FILES_LIMES = os.path.join(ROOT, "data", "commons", "files_limes.jsonl")
CLASSIFIED_LIMES = os.path.join(ROOT, "data", "commons", "classified_limes.jsonl")
FILES_CANONICAL = os.path.join(ROOT, "data", "commons", "files.jsonl")
NO_BOOKS = os.path.join(ROOT, "data", "books", ".no-books")  # never exists: check() skips an absent books file

# The three verified free sources (docs/lead_limes.md section 1 rows 1, 4, 5; all public domain).
SOURCES = {
    "ia-1895": dict(name="ORL Lieferung II = Band IV Abt B Nr. 40, Das Kastell Osterburken (O. Petters, Heidelberg, 1895)",
                    kind="book scan", url="https://archive.org/details/derobergermanis00fabrgoog",
                    dates="1895", access="full-res page images page/n{N}.jpg (5398x7526); public domain (PD notice in the item)"),
    "dewiki-orl": dict(name="de.wikipedia ORL plate set (874 files; the 45 staged are the Abt B fort plans and the Anhausen fortlet pair)",
                       kind="wikimedia images", url="https://de.wikipedia.org/wiki/Der_obergermanisch-raetische_Limes_des_Roemerreiches",
                       dates="1893-1915", access="upload.wikimedia.org/wikipedia/de/; licenses Bild-PD-alt (01, 05, 05a, 12, 64) and PD-alt-100 (the rest)"),
    "commons-orl": dict(name="Commons ORL plate set (262 files under aiprefix=ORL; the 9 staged are disjoint from the de.wiki set)",
                        kind="wikimedia images", url="https://commons.wikimedia.org/w/index.php?search=aiprefix:ORL&title=Special:AllImages",
                        dates="1893-1915", access="upload.wikimedia.org/wikipedia/commons/; public domain"),
}

# The 45 staging forts: 42 ORL numbers (42 and 45 each split into two fort items) + the Anhausen fortlet.
# name/qid/lon/lat/place/wikipedia verified against Wikidata and the de.wikipedia articles (sessions 4-7;
# lon/lat = the item's raw first P625 claim, so the evidence's place point is the site point, dist 0.0);
# band/year = the ORL article's Abteilung B list (bands.json; Anhausen = Abt A Band 1 = Strecke 1, 1915).
# 64/67 have no Wikidata item: name+coordinates from their de.wikipedia articles, recorded as such (task 208
# Notes). The place labels are the ORL names, NOT the odd Wikidata labels (47 "Castra of Vielbrunn", 60
# "Castrum Grinario", 66a "Castra Ad Lunam", 66b "Castra Aquileia", 71a "Castrum Iciniacum").
FORTS = {
    "01": dict(name="Heddesdorf", qid="Q1735373", lon=7.46931, lat=50.4365, place="Rhineland-Palatinate", wikipedia="https://de.wikipedia.org/wiki/Kastell_Heddesdorf", band="Abt B, Band 1", year=1903, note="ORL 01 (Abt B, Band 1), monograph 1903; point = the item's P625"),
    "02a": dict(name="Niederberg", qid="Q1670400", lon=7.62734, lat=50.3689, place="Rhineland-Palatinate", wikipedia="https://de.wikipedia.org/wiki/Kastell_Niederberg", band="Abt B, Band 1", year=1900, note="ORL 02a (Abt B, Band 1), monograph 1900; point = the item's P625"),
    "03": dict(name="Arzbach", qid="Q1735331", lon=7.74565, lat=50.3753, place="Rhineland-Palatinate", wikipedia="https://de.wikipedia.org/wiki/Kastell_Arzbach", band="Abt B, Band 1", year=1900, note="ORL 03 (Abt B, Band 1), monograph 1900; point = the item's P625"),
    "05": dict(name="Hunzel", qid="Q1240802", lon=7.82785, lat=50.2467, place="Rhineland-Palatinate", wikipedia="https://de.wikipedia.org/wiki/Kastell_Hunzel", band="Abt B, Band 1", year=1897, note="ORL 05 (Abt B, Band 1), monograph 1897; point = the item's P625"),
    "05a": dict(name="Marienfels", qid="Q1359182", lon=7.81076, lat=50.2403, place="Rhineland-Palatinate", wikipedia="https://de.wikipedia.org/wiki/Kastell_Marienfels", band="Abt B, Band 1", year=1903, note="ORL 05a (Abt B, Band 1), monograph 1903; point = the item's P625"),
    "07": dict(name="Kemel", qid="Q1725806", lon=8.01606, lat=50.1655, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Kemel", band="Abt B, Band 1", year=1901, note="ORL 07 (Abt B, Band 1), monograph 1901; point = the item's P625"),
    "08": dict(name="Zugmantel", qid="Q1727277", lon=8.20364, lat=50.18977, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Zugmantel", band="Abt B, Band 2a", year=1909, note="ORL 08 (Abt B, Band 2a), monograph 1909; point = the item's P625"),
    "12": dict(name="Kapersburg", qid="Q1735382", lon=8.636502423992, lat=50.31270674931, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Kapersburg", band="Abt B, Band 2a", year=1906, note="ORL 12 (Abt B, Band 2a), monograph 1906; point = the item's P625"),
    "18": dict(name="Echzell", qid="Q1657587", lon=8.88322, lat=50.393, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Echzell", band="Abt B, Band 2a", year=1903, note="ORL 18 (Abt B, Band 2a), monograph 1903; point = the item's P625"),
    "31": dict(name="Wiesbaden", qid="Q622981", lon=8.241862, lat=50.086375, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Wiesbaden", band="Abt B, Band 2b", year=1909, note="ORL 31 (Abt B, Band 2b), monograph 1909; item Q622981 is the Roman settlement and fort (Aquae Mattiacorum) of Wiesbaden"),
    "33": dict(name="Stockstadt", qid="Q1735421", lon=9.06737, lat=49.9774, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Stockstadt", band="Abt B, Band 3", year=1914, note="ORL 33 (Abt B, Band 3), monograph 1914; point = the item's P625"),
    "34": dict(name="Niedernberg", qid="Q1735399", lon=9.14105, lat=49.9141, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Niedernberg", band="Abt B, Band 3", year=1896, note="ORL 34 (Abt B, Band 3), monograph 1896; point = the item's P625"),
    "39": dict(name="Walldürn (Alteburg)", qid="Q1735436", lon=9.38674, lat=49.5785, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Walldürn", band="Abt B, Band 4", year=1904, note="ORL 39 (Abt B, Band 4), monograph 1904; point = the item's P625"),
    "40": dict(name="Osterburken", qid="Q1243550", lon=9.42364, lat=49.42753, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Osterburken", band="Abt B, Band 4", year=1895, note="ORL 40 (Abt B, Band 4), monograph 1895; point = the item's P625"),
    "41": dict(name="Jagsthausen", qid="Q1735380", lon=9.46917, lat=49.3109, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Jagsthausen", band="Abt B, Band 4", year=1909, note="ORL 41 (Abt B, Band 4), monograph 1909; point = the item's P625"),
    "42w": dict(name="Bürgkastell Öhringen", qid="Q86069877", lon=9.497397222222222, lat=49.205444444444446, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Öhringen-West", band="Abt B, Band 4", year=1897, note="ORL 42 (Abt B, Band 4), monograph 1897; ORL number 42 covers two forts (Bürgkastell west, Rendelkastell east), one Wikidata item each"),
    "42o": dict(name="Rendelkastell Öhringen", qid="Q91949042", lon=9.51336944444444, lat=49.1995138888889, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Öhringen-Ost", band="Abt B, Band 4", year=1897, note="ORL 42 (Abt B, Band 4), monograph 1897; ORL number 42 covers two forts (Bürgkastell west, Rendelkastell east), one Wikidata item each"),
    "44": dict(name="Murrhardt", qid="Q1735397", lon=9.5823, lat=48.97696, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Murrhardt", band="Abt B, Band 4", year=1894, note="ORL 44 (Abt B, Band 4), monograph 1894; point = the item's P625"),
    "45": dict(name="Welzheim-West", qid="Q32064057", lon=9.63234, lat=48.87218, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastelle_von_Welzheim", band="Abt B, Band 4", year=1904, note="ORL 45 (Abt B, Band 4), monograph 1904; ORL number 45 covers the Welzheim West- and Ostkastell, one Wikidata item each"),
    "45a": dict(name="Welzheim-Ost", qid="Q1735441", lon=9.64224, lat=48.87122, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastelle_von_Welzheim", band="Abt B, Band 4", year=1904, note="ORL 45 (Abt B, Band 4), monograph 1904; ORL number 45 covers the Welzheim West- and Ostkastell, one Wikidata item each"),
    "46": dict(name="Lützelbach", qid="Q1735392", lon=9.08861111, lat=49.77944444, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Lützelbach", band="Abt B, Band 5", year=1904, note="ORL 46 (Abt B, Band 5), monograph 1904; point = the item's P625"),
    "46b": dict(name="Seckmauern", qid="Q1735419", lon=9.11736111, lat=49.79902778, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Seckmauern", band="Abt B, Band 5", year=1914, note="ORL 46b (Abt B, Band 5), monograph 1914; point = the item's P625"),
    "47": dict(name="Hainhaus", qid="Q1735367", lon=9.08319, lat=49.7328, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Hainhaus", band="Abt B, Band 5", year=1897, note="ORL 47 (Abt B, Band 5), monograph 1897; point = the item's P625"),
    "48": dict(name="Eulbach", qid="Q1735359", lon=9.07791667, lat=49.68, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Eulbach", band="Abt B, Band 5", year=1896, note="ORL 48 (Abt B, Band 5), monograph 1896; point = the item's P625"),
    "49": dict(name="Würzberg", qid="Q1445553", lon=9.07527778, lat=49.63416667, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Würzberg", band="Abt B, Band 5", year=1896, note="ORL 49 (Abt B, Band 5), monograph 1896; point = the item's P625"),
    "50": dict(name="Hesselbach", qid="Q1411006", lon=9.09055556, lat=49.57625, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Hesselbach", band="Abt B, Band 5", year=1896, note="ORL 50 (Abt B, Band 5), monograph 1896; point = the item's P625"),
    "51": dict(name="Schlossau", qid="Q1735418", lon=9.14944, lat=49.5406, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Schlossau", band="Abt B, Band 5", year=1900, note="ORL 51 (Abt B, Band 5), monograph 1900; point = the item's P625"),
    "52": dict(name="Oberscheidental", qid="Q1735404", lon=9.15278, lat=49.5064, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastell_Oberscheidental", band="Abt B, Band 5", year=1897, note="ORL 52 (Abt B, Band 5), monograph 1897; point = the item's P625"),
    "53": dict(name="Neckarburken-West", qid="Q1343017", lon=9.170278, lat=49.376667, place="Hesse", wikipedia="https://de.wikipedia.org/wiki/Kastelle_von_Neckarburken", band="Abt B, Band 5", year=1898, note="ORL 53 (Abt B, Band 5), monograph 1898; item Q1343017 'Kastelle von Neckarburken' covers both forts; the staged plan is the Westkastell"),
    "56": dict(name="Böckingen", qid="Q1735374", lon=9.188611, lat=49.133888, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Böckingen", band="Abt B, Band 5", year=1898, note="ORL 56 (Abt B, Band 5), monograph 1898; point = the item's P625"),
    "57": dict(name="Walheim", qid="Q1669086", lon=9.15444, lat=49.0107, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Walheim", band="Abt B, Band 5", year=1897, note="ORL 57 (Abt B, Band 5), monograph 1897; item Q1669086 'Kastelle von Walheim' covers both Walheim forts, P625 is the village point"),
    "58": dict(name="Benningen", qid="Q1735337", lon=9.24931, lat=48.9439, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Benningen", band="Abt B, Band 5", year=1902, note="ORL 58 (Abt B, Band 5), monograph 1902; point = the item's P625"),
    "59": dict(name="Cannstatt", qid="Q1735423", lon=9.21083, lat=48.8133, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Stuttgart-Bad_Cannstatt", band="Abt B, Band 5", year=1907, note="ORL 59 (Abt B, Band 5), monograph 1907; point = the item's P625"),
    "60": dict(name="Köngen", qid="Q1735387", lon=9.36007, lat=48.6773, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Köngen", band="Abt B, Band 5", year=1907, note="ORL 60 (Abt B, Band 5), monograph 1907; point = the item's P625"),
    "61a": dict(name="Sulz", qid="Q1735424", lon=8.63667, lat=48.3597, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Sulz", band="Abt B, Band 5", year=1897, note="ORL 61a (Abt B, Band 5), monograph 1897; point = the item's P625"),
    "61b": dict(name="Waldmössingen", qid="Q1735435", lon=8.49333, lat=48.2739, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Waldmössingen", band="Abt B, Band 5", year=1897, note="ORL 61b (Abt B, Band 5), monograph 1897; point = the item's P625"),
    "63": dict(name="Lorch", qid="Q1433981", lon=9.68855, lat=48.7981, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Lorch", band="Abt B, Band 6", year=1897, note="ORL 63 (Abt B, Band 6), monograph 1897; point = the item's P625"),
    "64": dict(name="Kastell Schirenhof", qid=None, lon=10.03, lat=48.73, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Schirenhof", band="Abt B, Band 6", year=1897, note="ORL 64 (Abt B, Band 6), monograph 1897; no Wikidata item: name + coordinates from the de.wikipedia article 'Kastell Schirenhof', recorded as such (task 208 Notes)"),
    "65": dict(name="Unterböbingen", qid="Q1424499", lon=9.9228301, lat=48.8181017, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Unterböbingen", band="Abt B, Band 6", year=1894, note="ORL 65 (Abt B, Band 6), monograph 1894; point = the item's P625"),
    "66a": dict(name="Urspring", qid="Q1735430", lon=9.90069, lat=48.55, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Urspring", band="Abt B, Band 6", year=1904, note="ORL 66a (Abt B, Band 6), monograph 1904; point = the item's P625"),
    "66b": dict(name="Heidenheim", qid="Q128401126", lon=10.153666666666666, lat=48.67908333333333, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Heidenheim", band="Abt B, Band 6", year=1900, note="ORL 66b (Abt B, Band 6), monograph 1900; point = the item's P625"),
    "67": dict(name="Kastell Buch", qid=None, lon=10.136429, lat=48.909531, place="Baden-Württemberg", wikipedia="https://de.wikipedia.org/wiki/Kastell_Buch", band="Abt B, Band 6", year=1896, note="ORL 67 (Abt B, Band 6), monograph 1896; no Wikidata item: name + coordinates from the de.wikipedia village page 'Buch (Rainau)', recorded as such (task 208 Notes)"),
    "71a": dict(name="Theilenhofen", qid="Q1214616", lon=10.84716, lat=49.08952, place="Bavaria", wikipedia="https://de.wikipedia.org/wiki/Kastell_Theilenhofen", band="Abt B, Band 7", year=1905, note="ORL 71a (Abt B, Band 7), monograph 1905; point = the item's P625"),
    "72": dict(name="Weißenburg", qid="Q638525", lon=10.9625, lat=49.0308, place="Bavaria", wikipedia="https://de.wikipedia.org/wiki/Kastell_Weißenburg", band="Abt B, Band 7", year=1906, note="ORL 72 (Abt B, Band 7), monograph 1906; point = the item's P625"),
    "Anhausen": dict(name="Kleinkastell Anhausen", qid="Q1746855", lon=7.53841, lat=50.4813, place="Rhineland-Palatinate", wikipedia="https://de.wikipedia.org/wiki/Kleinkastell_Anhausen", band="Abt A, Band 1 (Strecke 1)", year=1915, note="ORL Abt A, Band 1 (Strecke 1), monograph 1915; the fortlet (Kleinkastell) of the Rhenish Limes, north of the Abt B series"),
}

# The 56 staged plans. desc = the file page's own caption verbatim FIRST (fit/evidence.py's check_caption
# re-verifies that the named fort is printed in title+desc) then the source note; every desc is clean of
# pipeline/commons.py's NO and PUBLISHED regexes (the 211 gate re-runs keep()/year_of() on the rows: the
# monograph year in `date` is the year used, 1894-1915, all <= 1925). date_page = the page's own raw date
# string when the research dump holds it complete and meaningful (omitted where the dump truncated it or it
# is junk like "Unknown" - the monograph year in `date` is the gate's value either way). artist = None: the
# ORL plates carry no per-file author metadata (the Reichs-Limes-Kommission's draughtsmen are named in the
# plate legends, e.g. Tafel IV "gez. von A. Ebertz"). thumb = None for both wikimedia sets (every fileinfo
# had no thumbnail); for the IA rows the page image IS the file.
FILES = [
    dict(
        source="dewiki-orl",
fort="01",
title="File:ORL_01_tab_03_pic_01_Grundriss_Kastellbad.jpg",
w=4472,
h=2867,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/c/c6/ORL_01_tab_03_pic_01_Grundriss_Kastellbad.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_01_tab_03_pic_01_Grundriss_Kastellbad.jpg",
license="Bild-PD-alt",
date_page="August 1903 (Publikation)",
desc="Grundriss des Kastellbades von Heddesdorf, ORL 1 ORL Abt B, Band 1, monograph 1903 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss des Kastellbades",
named="Heddesdorf",
    ),
    dict(
        source="dewiki-orl",
fort="02a",
title="File:ORL_02a_tab_01_pic_02_Principia,_Grundriss.jpg",
w=1780,
h=2040,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/f/f2/ORL_02a_tab_01_pic_02_Principia%2C_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_02a_tab_01_pic_02_Principia,_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss der Principia des Kastells Niederberg, ORL 2a, nach den Grabungsergebnissen der Reichs-Limes-Kommission von 1895 ORL Abt B, Band 1, monograph 1900 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss der Principia",
named="Niederberg",
    ),
    dict(
        source="dewiki-orl",
fort="03",
title="File:ORL_03_tab_02_pic_01_Grundriss_und_Geländeprofile.jpg",
w=2093,
h=3129,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/5/5b/ORL_03_tab_02_pic_01_Grundriss_und_Gel%C3%A4ndeprofile.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_03_tab_02_pic_01_Grundriss_und_Geländeprofile.jpg",
license="PD-alt-100",
date_page="Zwischen 1894 (Ausgrabung) und 1900 (Publikation)",
desc="Grundriss und Geländeschnitte des Kastells Arzbach, ORL 3, nach den Befunden der  Reichs-Limes-Kommission  1894 ORL Abt B, Band 1, monograph 1900 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Geländeprofile",
named="Arzbach",
    ),
    dict(
        source="dewiki-orl",
fort="05",
title="File:ORL_05_tab_02_pic_01-06_Grundriss_und_Profile.jpg",
w=3178,
h=3306,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/1/1a/ORL_05_tab_02_pic_01-06_Grundriss_und_Profile.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_05_tab_02_pic_01-06_Grundriss_und_Profile.jpg",
license="Bild-PD-alt",
date_page="Zwischen 1896 (Ausgrabung) und 1897 (Publikation)",
desc="Grundriss und Geländeprofile des Kastells Hunzel, ORL 5, zur Zeit der Grabungen der Reichs-Limes-Kommission 1896 ORL Abt B, Band 1, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Profile",
named="Hunzel",
    ),
    dict(
        source="dewiki-orl",
fort="05a",
title="File:ORL_05a_tab_02_pic_01_Grundriss_Kastell.jpg",
w=2965,
h=4044,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/4/47/ORL_05a_tab_02_pic_01_Grundriss_Kastell.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_05a_tab_02_pic_01_Grundriss_Kastell.jpg",
license="Bild-PD-alt",
date_page=None,
desc="Grundriss des Kastells Marienfels, ORL 5a, zur Zeit der Ausgrabungen durch die Reichs-Limes-Kommission 1896–1903 ORL Abt B, Band 1, monograph 1903 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss des Kastells",
named="Marienfels",
    ),
    dict(
        source="dewiki-orl",
fort="07",
title="File:ORL_07_tab_01_pic_02_Grundriss.jpg",
w=1832,
h=1949,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/2/24/ORL_07_tab_01_pic_02_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_07_tab_01_pic_02_Grundriss.jpg",
license="PD-alt-100",
date_page="Zwischen 1898/99 (Ausgrabungen) und November 1901 (Publikation)",
desc="Grundriss des Kastells Kemel, ORL 7 ORL Abt B, Band 1, monograph 1901 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Kemel",
    ),
    dict(
        source="dewiki-orl",
fort="08",
title="File:ORL_08_tab_02_pic_01_Grundriss.jpg",
w=8530,
h=12278,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/1/11/ORL_08_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_08_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page="Zwischen 1894 und 1908",
desc="Grundriss des  Kastells Zugmantel  am  Obergermanischen Limes ORL Abt B, Band 2a, monograph 1909 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Zugmantel",
    ),
    dict(
        source="dewiki-orl",
fort="12",
title="File:ORL_12_tab_04_pic_01-06_Therme,_Grundriss_und_Profile.jpg",
w=2747,
h=4100,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/9/92/ORL_12_tab_04_pic_01-06_Therme%2C_Grundriss_und_Profile.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_12_tab_04_pic_01-06_Therme,_Grundriss_und_Profile.jpg",
license="Bild-PD-alt",
date_page=None,
desc="Bade- und ein weiteres Gebäude des Kastells Kapersburg, ORL 12 ORL Abt B, Band 2a, monograph 1906 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Thermen-Grundriss und Profile",
named="Kapersburg",
    ),
    dict(
        source="dewiki-orl",
fort="18",
title="File:ORL_18_tab_01_pic_01_Lage_und_Grundriss.jpg",
w=8245,
h=11245,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/d/d9/ORL_18_tab_01_pic_01_Lage_und_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_18_tab_01_pic_01_Lage_und_Grundriss.jpg",
license="PD-alt-100",
date_page="1887",
desc="Kastell Echzell  (ORL 18) am  Obergermanisch-Raetischen Limes , Lage und Grundriss ORL Abt B, Band 2a, monograph 1903 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Lage und Grundriss",
named="Echzell",
    ),
    dict(
        source="dewiki-orl",
fort="33",
title="File:ORL_33_tab_03_pic_06_PPD_Schnitt_und_Grundriss.jpg",
w=5726,
h=5521,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/6/68/ORL_33_tab_03_pic_06_PPD_Schnitt_und_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_33_tab_03_pic_06_PPD_Schnitt_und_Grundriss.jpg",
license="PD-alt-100",
date_page="zwischen 1885 und 1909",
desc="Schnitt und Grundriss der  Porta Principalis Dextra  des  Kastells Stockstadt  des  Obergermanisch-Raetischen Limes ORL Abt B, Band 3, monograph 1914 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Schnitt und Grundriss der Porta P. D.",
named="Stockstadt",
    ),
    dict(
        source="dewiki-orl",
fort="34",
title="File:ORL_34_tab_01_pic_01_Grundriss.jpg",
w=9643,
h=10608,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/2/2d/ORL_34_tab_01_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_34_tab_01_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page="zwischen 1896 und 1903",
desc="Grundriss des  Kastells Niedernberg  an der Mainlinie des  Obergermanisch-Raetischen Limes ORL Abt B, Band 3, monograph 1896 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Niedernberg",
    ),
    dict(
        source="dewiki-orl",
fort="39",
title="File:ORL_39_tab_02_pic_01-11_Grundriss_und_Details.jpg",
w=2543,
h=3567,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/c/ca/ORL_39_tab_02_pic_01-11_Grundriss_und_Details.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_39_tab_02_pic_01-11_Grundriss_und_Details.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss, Profile und Details des Kastells von Walldürn, ORL 39 ORL Abt B, Band 4, monograph 1904 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss, Profile und Details",
named="Walldürn",
    ),
    dict(
        source="dewiki-orl",
fort="40",
title="File:ORL_40_tab_04_pic_01_Grundriss.jpg",
w=3466,
h=2838,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/6/6f/ORL_40_tab_04_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_40_tab_04_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells von Osterburken, ORL 40 ORL Abt B, Band 4, monograph 1895 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Osterburken",
    ),
    dict(
        source="dewiki-orl",
fort="41",
title="File:ORL_41_tab_02_pic_01_Grundriss.jpg",
w=2541,
h=3663,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/8/86/ORL_41_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_41_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page="Zwischen 1892 und 1906",
desc="Grundriss des  Kastells Jagsthausen , ORL 41 ORL Abt B, Band 4, monograph 1909 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Jagsthausen",
    ),
    dict(
        source="dewiki-orl",
fort="42w",
title="File:ORL_42_tab_03_pic_01_Bürgkastell_Grundriss.jpg",
w=2766,
h=2603,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/c/cd/ORL_42_tab_03_pic_01_B%C3%BCrgkastell_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_42_tab_03_pic_01_Bürgkastell_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Bürgkastells von Öhringen, ORL 42 ORL Abt B, Band 4, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss des Bürgkastells",
named="Öhringen",
    ),
    dict(
        source="dewiki-orl",
fort="42o",
title="File:ORL_42_tab_02_pic_01,_04-05_Rendelkastell,_Grundriss_und_Grabenschnitte.jpg",
w=2800,
h=2809,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/7/74/ORL_42_tab_02_pic_01%2C_04-05_Rendelkastell%2C_Grundriss_und_Grabenschnitte.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_42_tab_02_pic_01,_04-05_Rendelkastell,_Grundriss_und_Grabenschnitte.jpg",
license="PD-alt-100",
date_page="Zwischen 1892-94 (Grabungen) und 1897 (Publikation)",
desc="Grundriss und Profile des Rendelkastells von Öhringen, ORL 42 ORL Abt B, Band 4, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Grabenschnitte des Rendelkastells",
named="Öhringen",
    ),
    dict(
        source="dewiki-orl",
fort="44",
title="File:ORL_44_tab_01_pic_01_Grundriss_und_Details.jpg",
w=2910,
h=3988,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/3/3b/ORL_44_tab_01_pic_01_Grundriss_und_Details.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_44_tab_01_pic_01_Grundriss_und_Details.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss und Details des Kastells Murrhardt, ORL 44 ORL Abt B, Band 4, monograph 1894 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Details",
named="Murrhardt",
    ),
    dict(
        source="dewiki-orl",
fort="45",
title="File:ORL_45_tab_02_pic_01_Grundriss_Westkastell.jpg",
w=2715,
h=3750,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/e/ee/ORL_45_tab_02_pic_01_Grundriss_Westkastell.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_45_tab_02_pic_01_Grundriss_Westkastell.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Westkastells von Welzheim, ORL 45/45a ORL Abt B, Band 4, monograph 1904 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss des Westkastells",
named="Welzheim",
    ),
    dict(
        source="dewiki-orl",
fort="45a",
title="File:ORL_45_tab_03_pic_01-08_Grundriss_und_Schnitte_Ostkastell.jpg",
w=2513,
h=3615,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/e/ef/ORL_45_tab_03_pic_01-08_Grundriss_und_Schnitte_Ostkastell.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_45_tab_03_pic_01-08_Grundriss_und_Schnitte_Ostkastell.jpg",
license="PD-alt-100",
date_page="Zwischen 1894-96 (Grabungen) und 1904 (Publikation)",
desc="Grundriss und Schnitte des Ostkastells von Welzheim, ORL 45/45a ORL Abt B, Band 4, monograph 1904 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Schnitte des Ostkastells",
named="Welzheim",
    ),
    dict(
        source="dewiki-orl",
fort="46",
title="File:ORL_46_tab_1_pic_2_Grundriss.jpg",
w=1380,
h=1818,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/f/f4/ORL_46_tab_1_pic_2_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_46_tab_1_pic_2_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells Lützelbach, ORL 46 ORL Abt B, Band 5, monograph 1904 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Lützelbach",
    ),
    dict(
        source="dewiki-orl",
fort="46b",
title="File:ORL_46b_tab_01_pic_02a_Grundriss.jpg",
w=1611,
h=1577,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/3/38/ORL_46b_tab_01_pic_02a_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_46b_tab_01_pic_02a_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells Seckmauern, ORL 46b ORL Abt B, Band 5, monograph 1914 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Seckmauern",
    ),
    dict(
        source="dewiki-orl",
fort="47",
title="File:ORL_47_tab_01_pic_01_Grundriss.jpg",
w=1350,
h=1902,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/6/62/ORL_47_tab_01_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_47_tab_01_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells Hainhaus, ORL 47 ORL Abt B, Band 5, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Hainhaus",
    ),
    dict(
        source="dewiki-orl",
fort="48",
title="File:ORL_48_tab_01_pic_01_Grundriss.jpg",
w=1380,
h=1747,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/a/ac/ORL_48_tab_01_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_48_tab_01_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells Eulbach, ORL 48 ORL Abt B, Band 5, monograph 1896 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Eulbach",
    ),
    dict(
        source="dewiki-orl",
fort="49",
title="File:ORL_49_tab_01_pic_01_Grundriss.jpg",
w=1756,
h=2201,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/0/0c/ORL_49_tab_01_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_49_tab_01_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells von Würzberg, ORL 49 ORL Abt B, Band 5, monograph 1896 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Würzberg",
    ),
    dict(
        source="dewiki-orl",
fort="50",
title="File:ORL_50_tab_01_pic_01_Grundriss_1.jpg",
w=8887,
h=8277,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/a/a5/ORL_50_tab_01_pic_01_Grundriss_1.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_50_tab_01_pic_01_Grundriss_1.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells Hesselbach, ORL 50 ORL Abt B, Band 5, monograph 1896 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Hesselbach",
    ),
    dict(
        source="dewiki-orl",
fort="51",
title="File:ORL_51_tab_02_pic_01_Grundriss.jpg",
w=1290,
h=1538,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/5/59/ORL_51_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_51_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells Schloßau, ORL 51 ORL Abt B, Band 5, monograph 1900 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Schloßau",
    ),
    dict(
        source="dewiki-orl",
fort="52",
title="File:ORL_52_tab_02_pic_01-03_Grundriss_und_Schnitte.jpg",
w=2647,
h=3120,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/c/c9/ORL_52_tab_02_pic_01-03_Grundriss_und_Schnitte.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_52_tab_02_pic_01-03_Grundriss_und_Schnitte.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss und Schnitte des Kastells Oberscheidental, ORL 52 ORL Abt B, Band 5, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Schnitte",
named="Oberscheidental",
    ),
    dict(
        source="dewiki-orl",
fort="53",
title="File:ORL_53_tab_02_pic_01_Westkastell_Grundriss.jpg",
w=2379,
h=2859,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/b/bc/ORL_53_tab_02_pic_01_Westkastell_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_53_tab_02_pic_01_Westkastell_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Westkastells von Neckarburken, ORL 53 ORL Abt B, Band 5, monograph 1898 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss des Westkastells",
named="Neckarburken",
    ),
    dict(
        source="dewiki-orl",
fort="56",
title="File:ORL_56_tab_02_pic_01_Grundriss.jpg",
w=2849,
h=2622,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/0/00/ORL_56_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_56_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells Böckingen, ORL 56 ORL Abt B, Band 5, monograph 1898 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Böckingen",
    ),
    dict(
        source="dewiki-orl",
fort="57",
title="File:ORL_57_tab_02_pic_01_Grundriss.jpg",
w=2333,
h=3248,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/4/4e/ORL_57_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_57_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells Walheim, ORL 57 ORL Abt B, Band 5, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Walheim",
    ),
    dict(
        source="dewiki-orl",
fort="58",
title="File:ORL_58_tab_02_pic_01_Grundriss.jpg",
w=2631,
h=3421,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/b/bb/ORL_58_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_58_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells Benningen, ORL 58 ORL Abt B, Band 5, monograph 1902 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Benningen",
    ),
    dict(
        source="dewiki-orl",
fort="59",
title="File:ORL_59_tab_02_pic_01_Grundriss_und_Schnitte.jpg",
w=2590,
h=3556,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/6/68/ORL_59_tab_02_pic_01_Grundriss_und_Schnitte.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_59_tab_02_pic_01_Grundriss_und_Schnitte.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss und Schnitte des Kastells von Stuttgart-Bad Cannstatt, ORL 59 ORL Abt B, Band 5, monograph 1907 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Schnitte",
named="Stuttgart-Bad Cannstatt",
    ),
    dict(
        source="dewiki-orl",
fort="60",
title="File:ORL_60_tab_02_pic_01_Grundriss_und_Profile.jpg",
w=2493,
h=3602,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/1/1a/ORL_60_tab_02_pic_01_Grundriss_und_Profile.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_60_tab_02_pic_01_Grundriss_und_Profile.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss und Profile des Kastells von Köngen, ORL 60 ORL Abt B, Band 5, monograph 1907 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Profile",
named="Köngen",
    ),
    dict(
        source="dewiki-orl",
fort="61a",
title="File:ORL_61a_tab_02_pic_01_Grundriss_und_Schnitte.jpg",
w=2927,
h=3519,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/8/82/ORL_61a_tab_02_pic_01_Grundriss_und_Schnitte.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_61a_tab_02_pic_01_Grundriss_und_Schnitte.jpg",
license="PD-alt-100",
date_page=None,
desc="Lageplan des Kastells Sulz, ORL 61a ORL Abt B, Band 5, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Lageplan",
named="Sulz",
    ),
    dict(
        source="dewiki-orl",
fort="61b",
title="File:ORL_61b_tab_02_pic_01_Grundriss.jpg",
w=2827,
h=3764,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/a/a2/ORL_61b_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_61b_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells von Waldmössingen, ORL 61b ORL Abt B, Band 5, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Waldmössingen",
    ),
    dict(
        source="dewiki-orl",
fort="63",
title="File:ORL_63_tab_02_pic_01_Grundriss.jpg",
w=2732,
h=3049,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/9/9b/ORL_63_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_63_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page="Zwischen 1893 und 1896",
desc="Grundriss des  Kastells Lorch , ORL 63 ORL Abt B, Band 6, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Lorch",
    ),
    dict(
        source="dewiki-orl",
fort="64",
title="File:ORL_64_tab_02_pic_01_Grundriss.jpg",
w=2014,
h=2408,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/6/6a/ORL_64_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_64_tab_02_pic_01_Grundriss.jpg",
license="Bild-PD-alt",
date_page="Zwischen 1886 und 1888",
desc="Grundriss des  Kastells Schirenhof ORL Abt B, Band 6, monograph 1897 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Schirenhof",
    ),
    dict(
        source="dewiki-orl",
fort="65",
title="File:ORL_65_tab_01_pic_01_Grundriss_und_Profile.jpg",
w=2884,
h=3556,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/4/45/ORL_65_tab_01_pic_01_Grundriss_und_Profile.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_65_tab_01_pic_01_Grundriss_und_Profile.jpg",
license="PD-alt-100",
date_page="1892–1894",
desc="Grundriss und Geländeprofile des  Kastells Unterböbingen ORL Abt B, Band 6, monograph 1894 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Geländeprofile",
named="Unterböbingen",
    ),
    dict(
        source="dewiki-orl",
fort="66a",
title="File:ORL_66a_Tab_01_pic_03-04_Grundriss.jpg",
w=2469,
h=2144,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/6/69/ORL_66a_Tab_01_pic_03-04_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_66a_Tab_01_pic_03-04_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss und Geländeprofil des Kastells von Urspring, ORL 66a ORL Abt B, Band 6, monograph 1904 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Geländeprofil",
named="Urspring",
    ),
    dict(
        source="dewiki-orl",
fort="66b",
title="File:ORL_66b_Tab_02_pic_01_Grundriss.jpg",
w=2963,
h=4071,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/e/ed/ORL_66b_Tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_66b_Tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page=None,
desc="Grundriss des Kastells von Heidenheim, ORL 66b ORL Abt B, Band 6, monograph 1900 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Heidenheim",
    ),
    dict(
        source="dewiki-orl",
fort="67",
title="File:ORL_67_tab_02_pic_01_Grundriss.jpg",
w=9310,
h=9759,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/a/a0/ORL_67_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_67_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page="1897-1898",
desc="Grundriss des  Kastells Buch ORL Abt B, Band 6, monograph 1896 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Buch",
    ),
    dict(
        source="dewiki-orl",
fort="71a",
title="File:ORL_71a_tab_02_pic_01_Grundriss.jpg",
w=7400,
h=10271,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/f/f2/ORL_71a_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_71a_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page="Zwischen 1892 und 1895",
desc="Grundriss des  Kastells Theilenhofen ORL Abt B, Band 7, monograph 1905 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Theilenhofen",
    ),
    dict(
        source="dewiki-orl",
fort="72",
title="File:ORL_72_tab_02_pic_01_Grundriss.jpg",
w=9037,
h=10101,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/1/19/ORL_72_tab_02_pic_01_Grundriss.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_72_tab_02_pic_01_Grundriss.jpg",
license="PD-alt-100",
date_page="Zwischen 1890 und 1905",
desc="Grundriss des  Kastells Weißenburg ORL Abt B, Band 7, monograph 1906 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss",
named="Weißenburg",
    ),
    dict(
        source="dewiki-orl",
fort="Anhausen",
title="File:ORL_A_Strecke_1_tab_12_pic_01_KK_Anhausen_Lage_HR.jpg",
w=2819,
h=2823,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/4/42/ORL_A_Strecke_1_tab_12_pic_01_KK_Anhausen_Lage_HR.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_A_Strecke_1_tab_12_pic_01_KK_Anhausen_Lage_HR.jpg",
license="PD-alt-100",
date_page="Zwischen 1893 und 1899",
desc="Lageplan des Kleinkastells Anhausen ORL Abt A, Band 1 (Strecke 1), monograph 1915 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Lageplan des Kleinkastells",
named="Anhausen",
    ),
    dict(
        source="dewiki-orl",
fort="Anhausen",
title="File:ORL_A_Strecke_1_tab_12_pic_02_KK_Anhausen_Grundriss_und_Schnitt_HR.jpg",
w=3111,
h=3130,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/de/e/ef/ORL_A_Strecke_1_tab_12_pic_02_KK_Anhausen_Grundriss_und_Schnitt_HR.jpg?utm_source=de.wikipedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://de.wikipedia.org/wiki/File:ORL_A_Strecke_1_tab_12_pic_02_KK_Anhausen_Grundriss_und_Schnitt_HR.jpg",
license="PD-alt-100",
date_page="Zwischen 1893 und 1899",
desc="Grundriss und Geländeprofil des Kleinkastells Anhausen ORL Abt A, Band 1 (Strecke 1), monograph 1915 (Reichs-Limes-Kommission); de.wikipedia file page.",
what="Grundriss und Geländeprofil des Kleinkastells",
named="Anhausen",
    ),
    dict(
        source="commons-orl",
fort="01",
title="File:ORL 01 tab 01 pic 01 Lageplan.jpg",
w=2961,
h=4223,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/commons/c/c2/ORL_01_tab_01_pic_01_Lageplan.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://commons.wikimedia.org/wiki/File:ORL_01_tab_01_pic_01_Lageplan.jpg",
license="Public domain",
date_page="August 1903 (Publikation)",
desc="Lageplan des Kastells Heddesdorf, ORL 1 ORL Abt B, Band 1 plate, monograph 1903 (Reichs-Limes-Kommission); Commons file page.",
what="Lageplan",
named="Heddesdorf",
    ),
    dict(
        source="commons-orl",
fort="01",
title="File:ORL 01 tab 02 pic 01 Grundriss.jpg",
w=4435,
h=3197,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/commons/e/e9/ORL_01_tab_02_pic_01_Grundriss.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://commons.wikimedia.org/wiki/File:ORL_01_tab_02_pic_01_Grundriss.jpg",
license="Public domain",
date_page="August 1903 (Publikation)",
desc="Grundriss des Kastells und des Kastellbades von Heddesdorf, ORL 1 ORL Abt B, Band 1 plate, monograph 1903 (Reichs-Limes-Kommission); Commons file page.",
what="Grundriss von Kastell und Kastellbad",
named="Heddesdorf",
    ),
    dict(
        source="commons-orl",
fort="12",
title="File:ORL 12 tab 02 pic 01 Grundriss und Profile.jpg",
w=2799,
h=2824,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/commons/d/de/ORL_12_tab_02_pic_01_Grundriss_und_Profile.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://commons.wikimedia.org/wiki/File:ORL_12_tab_02_pic_01_Grundriss_und_Profile.jpg",
license="Public domain",
date_page=None,
desc="Grundriss und Geländeprofile des Kastells Kapersburg, ORL 12 ORL Abt B, Band 2a plate, monograph 1906 (Reichs-Limes-Kommission); Commons file page.",
what="Grundriss und Geländeprofile",
named="Kapersburg",
    ),
    dict(
        source="commons-orl",
fort="33",
title="File:ORL 33 tab 02 pic 01 Grundriss.jpg",
w=8070,
h=11328,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/commons/2/2a/ORL_33_tab_02_pic_01_Grundriss.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://commons.wikimedia.org/wiki/File:ORL_33_tab_02_pic_01_Grundriss.jpg",
license="Public domain",
date_page=None,
desc="Fort Stockstadt layout ORL Abt B, Band 3 plate, monograph 1914 (Reichs-Limes-Kommission); Commons file page.",
what="fort layout",
named="Stockstadt",
    ),
    dict(
        source="commons-orl",
fort="33",
title="File:ORL 33 tab 03 pic 05 Porta Praetoria Grundriss.jpg",
w=6816,
h=3024,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/commons/8/80/ORL_33_tab_03_pic_05_Porta_Praetoria_Grundriss.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://commons.wikimedia.org/wiki/File:ORL_33_tab_03_pic_05_Porta_Praetoria_Grundriss.jpg",
license="Public domain",
date_page=None,
desc="Layout of the porta praetoria of Fort Stockstadt. ORL Abt B, Band 3 plate, monograph 1914 (Reichs-Limes-Kommission); Commons file page.",
what="porta praetoria layout",
named="Stockstadt",
    ),
    dict(
        source="commons-orl",
fort="33",
title="File:ORL 33 tab 04 pic 01-09 Thermen.jpg",
w=8680,
h=12600,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/commons/8/85/ORL_33_tab_04_pic_01-09_Thermen.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://commons.wikimedia.org/wiki/File:ORL_33_tab_04_pic_01-09_Thermen.jpg",
license="Public domain",
date_page=None,
desc="Layout of the baths at Stockstadt Roman Fort. ORL Abt B, Band 3 plate, monograph 1914 (Reichs-Limes-Kommission); Commons file page.",
what="baths layout",
named="Stockstadt",
    ),
    dict(
        source="commons-orl",
fort="33",
title="File:ORL 33 tab 05 pic 01 Mithraeum und Dolichenum Lage.jpg",
w=15023,
h=4840,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/commons/f/fd/ORL_33_tab_05_pic_01_Mithraeum_und_Dolichenum_Lage.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://commons.wikimedia.org/wiki/File:ORL_33_tab_05_pic_01_Mithraeum_und_Dolichenum_Lage.jpg",
license="Public domain",
date_page=None,
desc="Plan of the Mithraeum and Dolichenum at Stockstadt Roman Fort ORL Abt B, Band 3 plate, monograph 1914 (Reichs-Limes-Kommission); Commons file page.",
what="Mithraeum and Dolichenum plan",
named="Stockstadt",
    ),
    dict(
        source="commons-orl",
fort="31",
title="File:ORL B 2 3b Taf 1 Kastell Wiesbaden.jpg",
w=2292,
h=3288,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/commons/6/68/ORL_B_2_3b_Taf_1_Kastell_Wiesbaden.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://commons.wikimedia.org/wiki/File:ORL_B_2_3b_Taf_1_Kastell_Wiesbaden.jpg",
license="Public domain",
date_page="1909",
desc="Plan of Wiesbaden in Roman Times. ORL Abt B, Band 2b plate, monograph 1909 (Reichs-Limes-Kommission); Commons file page.",
what="plan, Tafel 1",
named="Wiesbaden",
    ),
    dict(
        source="commons-orl",
fort="31",
title="File:ORL B 2 3b Taf 2 Kastell Wiesbaden.jpg",
w=2328,
h=3276,
mime="image/jpeg",
url="https://upload.wikimedia.org/wikipedia/commons/0/08/ORL_B_2_3b_Taf_2_Kastell_Wiesbaden.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original",
thumb=None,
page="https://commons.wikimedia.org/wiki/File:ORL_B_2_3b_Taf_2_Kastell_Wiesbaden.jpg",
license="Public domain",
date_page="1909",
desc="Plan of Roman castle in Wiesbaden. ORL Abt B, Band 2b plate, monograph 1909 (Reichs-Limes-Kommission); Commons file page.",
what="plan, Tafel 2",
named="Wiesbaden",
    ),
    dict(
        source="ia-1895",
fort="40",
title="Das Kastell Osterburken, Tafel III - Situationskarte (1895)",
w=5398,
h=7526,
mime="image/jpeg",
url="https://archive.org/download/derobergermanis00fabrgoog/page/n54.jpg",
thumb="https://archive.org/download/derobergermanis00fabrgoog/page/n54.jpg",
page="https://archive.org/details/derobergermanis00fabrgoog",
license="public domain (1895 scan; PD notice on the item's first leaves)",
date_page=None,
desc="Tafel III 'Nr 40. KASTELL OSTERBURKEN': Situationskarte with the fort, its Limes road, the railway, the town and field boundaries, MAASSTAB 1:5000. ORL Lieferung II, Band IV Abt B Nr. 40 (O. Petters, Heidelberg, 1895); Internet Archive scan derobergermanis00fabrgoog, leaf 55.",
what="Situationskarte, Tafel III (1:5000)",
named="Osterburken",
    ),
    dict(
        source="ia-1895",
fort="40",
title="Das Kastell Osterburken, Tafel IV - Grundriss (1895)",
w=5398,
h=7526,
mime="image/jpeg",
url="https://archive.org/download/derobergermanis00fabrgoog/page/n56.jpg",
thumb="https://archive.org/download/derobergermanis00fabrgoog/page/n56.jpg",
page="https://archive.org/details/derobergermanis00fabrgoog",
license="public domain (1895 scan; PD notice on the item's first leaves)",
date_page=None,
desc="Tafel IV: the fort plan (Grundriss) of Osterburken with both fort lines (main fort and annex), lettered gates, the Roman road and excavated buildings 1-18, MAASSTAB 1:1000; the scanned plate is rotated 90° clockwise. ORL Lieferung II, Band IV Abt B Nr. 40 (O. Petters, Heidelberg, 1895); Internet Archive scan derobergermanis00fabrgoog, leaf 57.",
what="Grundriss, Tafel IV (1:1000)",
named="Osterburken",
    ),
]

# The golden sample: one staged file row per source (plus their extras + classified rows).
GOLDEN_ROWS = [
    "Das Kastell Osterburken, Tafel III - Situationskarte (1895)",  # ia-1895
    "File:ORL_01_tab_03_pic_01_Grundriss_Kastellbad.jpg",          # dewiki-orl
    "File:ORL 01 tab 01 pic 01 Lageplan.jpg",                      # commons-orl
]


def now():
    return time.strftime("%Y-%m-%d")


def _load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def _append(path, rows):
    if not rows:
        return
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _slug(label):
    """The pipeline/sources.py slug rule (lowercase ASCII, runs of anything else -> "-"), with NFKD
    ASCII-folding first so German names slug cleanly (Öhringen -> ohringen, Weißenburg -> weissenburg)."""
    a = unicodedata.normalize("NFKD", label.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", a).strip("-")


def fort_id(num):
    f = FORTS[num]
    s = _slug(f["name"])
    return s if f["qid"] is None else s + "-" + f["qid"].lower()


def evidence_for(num, fort, named):
    """The hand-recorded caption_coords tie (the only live route that holds these rows): the caption names
    the fort and the stored coordinates are the verified place - the item's P625 (site point = place point,
    dist 0.0) or, for the two item-less forts, the article's coordinates recorded as such."""
    if fort["qid"] is None:
        label = f"{fort['name']} (no Wikidata item: name+coords from the de.wikipedia article)"
    else:
        label = fort["name"]
    return {"rec": "evidence/1", "kind": "caption_coords", "checked": now(), "named_place": named,
            "place_qid": fort["qid"], "place_label": label,
            "place_lon": fort["lon"], "place_lat": fort["lat"],
            "site_lon": fort["lon"], "site_lat": fort["lat"], "dist_m": 0.0}


def extras_row(num, fort):
    row = {"id": fort_id(num), "qid": fort["qid"], "name": fort["name"], "lon": fort["lon"], "lat": fort["lat"],
           "region": "germany", "kind": "roman fort", "aerial_ok": True, "source": "fit/src_limes.py",
           "place": fort["place"], "wikipedia": fort["wikipedia"]}
    row["note"] = fort["note"]
    return row


def file_row(e):
    fort = FORTS[e["fort"]]
    src_short = {"ia-1895": "Internet Archive", "dewiki-orl": "de.wikipedia", "commons-orl": "Commons"}[e["source"]]
    r = {"site": fort_id(e["fort"]), "qid": fort["qid"], "title": e["title"], "year": fort["year"],
         "wd_plan": False, "cat": None,
         "name": f"{fort['name']}, {e['what']}, ORL {e['fort']}, {fort['year']} ({src_short})",
         "by": f"fit/src_limes.py {e['source']}", "url": e["url"], "thumb": e["thumb"], "w": e["w"], "h": e["h"],
         "mime": e["mime"], "date": str(fort["year"]), "desc": e["desc"], "artist": None,
         "license": e["license"], "page": e["page"]}
    if e["date_page"]:
        r["date_commons"] = e["date_page"]
    r["evidence"] = evidence_for(e["fort"], fort, e["named"])
    return r


def _gate(c, r, e):
    """The 211 gate, run on every row before it is written: keep() and year_of() must pass with the stored
    fields, and the caption must actually name the recorded fort (what check_caption re-verifies offline)."""
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.abspath(c.__file__)))
    import books_match
    if not c.keep(r["title"], r):
        raise SystemExit(f"commons.keep() would drop {r['title']!r} - fix the table or record the drop in docs/lead_limes.md")
    if c.year_of(r["title"], r) != r["year"]:
        raise SystemExit(f"commons.year_of() gives {c.year_of(r['title'], r)}, not the monograph year {r['year']}: {r['title']!r}")
    if books_match.norm(e["named"]) not in books_match.norm(r["title"] + " " + r["desc"]):
        raise SystemExit(f"the caption does not name the recorded fort {e['named']!r}: {r['title']!r}")


def stage(dry=False):
    """Stage the 56 file rows + 45 extras rows + 56 classified rows into this task's own files (append-only,
    idempotent on (site, title)). Offline by construction (all values hand-recorded above)."""
    c = __import__("commons")
    have = {(r.get("site"), r.get("title")) for r in _load(FILES_LIMES) + _load(CLASSIFIED_LIMES)}
    new_files, new_cls, new_sites, seen = [], [], [], set()
    for e in FILES:
        f = file_row(e)
        _gate(c, f, e)
        if (f["site"], f["title"]) in have:
            continue
        new_files.append(f)
        new_cls.append({"site": f["site"], "title": f["title"], "p_plan": 1.0, "p_birdseye": 0.0, "p_photo": 0.0,
                        "by": "hand"})
        if f["site"] not in seen:
            new_sites.append(extras_row(e["fort"], FORTS[e["fort"]]))
            seen.add(f["site"])
    print(f"staged: {len(new_sites)} new sites, {len(new_files)} new pictures (of {len(FILES)} total)")
    for s in new_sites:
        print("   ", s["id"])
    if dry:
        return
    _append(EXTRAS_LIMES, new_sites)
    _append(FILES_LIMES, new_files)
    _append(CLASSIFIED_LIMES, new_cls)


def check_staged():
    """Offline (no network): join the staged files (every file row names a staged extras row; every staged
    extras row has a picture; a staged id/QID is a problem only when a DIFFERENT site holds it - the
    module's own rows already merged by 211 are a no-op, not a collision; (site, title) unique; a staged row
    whose key is in the canonical files.jsonl must be identical to the canonical row (211's first-row-wins
    merge) - a same-key different row still fails loud; classified rows 1:1; rows complete) and run
    fit/evidence.py's check over the staged rows. Returns the exit code (0 iff no problem and no FAIL)."""
    import evidence
    files = _load(FILES_LIMES)
    sites = _load(EXTRAS_LIMES)
    cls = _load(CLASSIFIED_LIMES)
    known_ids, known_qids = set(), {}
    for p in (SITES_JSONL, EXTRAS):
        for s in _load(p):
            known_ids.add(s["id"])
            if s.get("qid"):
                known_qids[s["qid"]] = s["id"]
    problems = []
    staged_ids = {s["id"] for s in sites}
    # after 211's merge the module's own staged sites sit in the canonical extras (known): a staged id/QID
    # is a problem only when it resolves to a DIFFERENT site (the pre-merge clash protection)
    if staged_ids & (known_ids - staged_ids):
        problems.append(f"staged site ids collide with existing sites: "
                        f"{sorted(staged_ids & (known_ids - staged_ids))}")
    for s in sites:
        if s.get("qid") in known_qids and known_qids[s["qid"]] != s["id"]:
            problems.append(f"staged site {s['id']} re-uses existing QID {s['qid']} ({known_qids[s['qid']]})")
    for s in sites:
        for k in ("id", "name", "lon", "lat", "region", "kind", "aerial_ok", "source", "place", "wikipedia"):
            if s.get(k) is None:
                problems.append(f"staged site {s['id']} missing field {k}")
        if s.get("region") != "germany" or s.get("kind") != "roman fort":
            problems.append(f"staged site {s['id']} has region {s.get('region')!r} / kind {s.get('kind')!r}")
    pics = {s["id"]: 0 for s in sites}
    seen, canonical = set(), {}
    for r in _load(FILES_CANONICAL):
        k = (r.get("site"), r.get("title"))
        if k not in canonical:  # first row wins, as in the 211 merge
            canonical[k] = _canon_norm(r)
    for r in files:
        sid = r.get("site")
        if sid not in pics:
            problems.append(f"file row names a site that is not staged: {sid!r} ({r.get('title')!r})")
            continue
        pics[sid] += 1
        for k in ("qid", "title", "year", "by", "date", "desc", "evidence"):
            if k == "qid" and r.get("qid") is not None:
                continue
            if k != "qid" and not r.get(k) and k != "qid":
                problems.append(f"file row {r.get('title')!r} missing field {k}")
        k = (sid, r.get("title"))
        if k in seen:
            problems.append(f"duplicate staged row {k}")
        if k in canonical and canonical[k] != _canon_norm(r):
            problems.append(f"staged title already in the canonical files.jsonl: {k}")
        seen.add(k)
    for sid in pics:
        if not pics[sid]:
            problems.append(f"staged site {sid} has no staged picture")
    if {(r.get("site"), r.get("title")) for r in cls} != seen:
        problems.append("the classified rows are not 1:1 with the staged file rows")
    for c in cls:
        if c.get("p_plan") != 1.0 or c.get("by") != "hand":
            problems.append(f"classified row {c['site']}|{c['title']} is not p_plan 1.0 by hand")
    for p in problems:
        print("join:", p)
    code, text = evidence.check(FILES_LIMES, NO_BOOKS, catalog=EXTRAS_LIMES)
    print(text)
    return 1 if (problems or code) else 0


def _canon_norm(r):
    """Row identity under the 211 merge rule (the same norm fit/merge.py uses on the line): key order and
    ASCII escaping don't matter, content does."""
    return json.dumps(r, sort_keys=True, ensure_ascii=False)


def _norm(rows):
    """The rows for the golden file: keys are sorted by the dump, "checked" and "date_commons" normalized
    (they vary with the staging date)."""
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
    """Write tests/golden/src_limes_sample.json: one staged file row per source (GOLDEN_ROWS) plus their
    extras and classified rows, normalized. Regenerate only for an intended change."""
    p = path or os.path.join(ROOT, "tests", "golden", "src_limes_sample.json")
    files = [r for r in _load(FILES_LIMES) if r.get("title") in GOLDEN_ROWS]
    if len(files) != len(GOLDEN_ROWS):
        raise SystemExit(f"golden rows missing from the staging files: {[t for t in GOLDEN_ROWS
                             if t not in {r.get('title') for r in files}]}")
    sites = {r["site"] for r in files}
    extras = [s for s in _load(EXTRAS_LIMES) if s["id"] in sites]
    cls = [c for c in _load(CLASSIFIED_LIMES) if (c["site"], c["title"]) in {(r["site"], r["title"]) for r in files}]
    out = {"extras": _norm(extras), "files": _norm(files), "classified": _norm(cls)}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", p)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        stage(False)
    elif a[0] == "--dry":
        stage(True)
    elif a[0] == "--check":
        raise SystemExit(check_staged())
    elif a[0] == "--golden":
        golden()
    else:
        raise SystemExit(__doc__.split("usage:")[1].strip())
