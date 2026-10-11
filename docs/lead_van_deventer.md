# Van Deventer's town plans - the remaining towns (task 204)

GOAL.md point 4: Jacob van Deventer's town plans, drawn c. 1545-1565 for Charles V and Philip II. The Commons
category "Maps by Jacob van Deventer" holds 70 subcategories: 66 town categories and 4 collection categories
(section 1). Six towns are already hand-tied in `pipeline/sources.py` (Gouda, Zwolle, Venlo, Damme, Binche,
Bergues) - their canonical rows keep that hand-tie and are NOT re-staged here - leaving 60 town categories for
this task (59 stageable towns + the Groningen-province category, a documented drop: it is a province map, not
a town plan).

The hand-checked file -> QID table lives in `fit/src_van_deventer.py` (the `pipeline/sources.py` pattern): every
recorded QID is verified against its label, every P625 value, its P373 and its enwiki link, because a name
search alone gives the wrong place (the Barnard-Castle trap; the NL traps below are live examples). Each staged
picture carries task-200 machine-checkable evidence: the P373 category chain where the live walk holds (kind
`category`), else the caption route (kind `caption_coords` - the file names the town and the stored resolution
is the verified site point itself, never a bare name-search hit); a file with neither route is a documented
drop, never a guessed row. This task stages into its own files only (`data/catalog/extras_van_deventer.jsonl`,
`data/commons/files_van_deventer.jsonl`, `data/commons/classified_van_deventer.jsonl`); 211 consolidates them
into the canonical files and builds the sites. Live commands (run under `.venv/bin/python`): `--list` the
category census, `--verify [towns...]` the QID fact sheets, `--files [towns...]` the file inventories,
`--chain <town>` the category walk, `stage [--dry]`, `--check`, `--golden`.

## The Commons category (checked 2026-10-11)

`Category:Maps by Jacob van Deventer`
(https://commons.wikimedia.org/wiki/Category:Maps_by_Jacob_van_Deventer) holds exactly **70 subcategories:
66 town categories + 4 collection categories**. `fit/src_van_deventer.py --list` fetches the live list and
asserts it against the module's TOWNS table (a rename or a new category fails loud); it passed on 2026-10-11 and
is re-run in every session since (the latest run, 2026-10-11, is after the `town_files` extension to the
collection categories), each time re-confirming the old prep's 2026-10-10 census.

The 66 town categories, by country (the TOWNS table in `fit/src_van_deventer.py` is the source of this list;
"(done)" = already hand-tied in `pipeline/sources.py`, not re-staged here; every title carries " by Jacob van
Deventer" except where noted):

- **Netherlands (19 = 16 to stage + 3 done):** Map of Aardenburg; Maps of Alkmaar; Maps of Amsterdam; Map of
  Enkhuizen; Map of Goes; Map of Groningen (city); Map of Groningen (province) - a province map, a documented
  drop, not a town plan; Maps of Haarlem; Map of Leeuwarden; Map of Middelburg; Map of Reimerswaal; Maps of
  Rotterdam; Map of Sluis; Map of The Hague; Maps of Utrecht (city); Map of Valkenburg, Limburg; (done) Map of
  Gouda; Map of Zwolle; Map of Venlo.
- **Belgium (22 = 20 to stage + 2 done):** Map of Ath; Map of Braine-le-Comte; Maps of Bruges; Maps of Brussels;
  Map of Chimay; Map of Chièvres; Map of Enghien; Map of Ghent; Map of Halle; Map of Kortrijk; Map of Lessines;
  Map of Leuze; Map of Mechelen; Map of Mons; Map of Ostend; Map of Saint-Ghislain; Map of Soignies; Map of
  Tournai; Maps of Aarschot; Maps of Oudenaarde; (done) Map of Damme; Map of Binche.
- **France (24 = 23 to stage + 1 done):** Map of Aire-sur-la-Lys; Map of Arras; Map of Avesnes-sur-Helpe; Map of
  Bapaume; Map of Bavay; Map of Beaumont; Map of Bouchain; Map of Béthune; Map of Cambrai; Map of
  Condé-sur-l'Escaut; Map of Douai; Map of Gravelines; Map of Hesdin; Map of Landrecies; Map of
  Le Cateau-Cambrésis; Map of Le Quesnoy; Map of Le Rœulx; Map of Lille; Map of Maubeuge; Map of Saint-Omer;
  Map of Thérouanne; Map of Valenciennes; Map of Vieil-Hesdin; (done) Map of Bergues.
- **Luxembourg (1 to stage):** Maps of Luxembourg City Jacob van Deventer (no "by" - the only irregular title).

The 4 collection categories: `Maps by Jacob van Deventer (Biblioteca Nacional de España)`, `Maps by Jacob van
Deventer (Nationaal Archief)`, `Maps by Jacob van Deventer (Rijksdienst voor het Cultureel Erfgoed)`, and
`Atlas des villes des Pays-Bas : 73 places levées entre 1550 et 1565 sur les ordres de Charles Quint et de
Philippe II` (per-town plate subcategories at depth 1). What each holds and which town's picture it supplied:
the "The collection categories" section below (the `--files` run of 2026-10-11).

## QID verification - the Netherlands (checked 2026-10-11; re-run with `.venv/bin/python fit/src_van_deventer.py --verify`)

Method: per town the Wikidata search candidates (label-based search), then for every candidate the label, every
P625, P373, P131 and the enwiki link; the hand check records the item whose label is the town, whose P625 sits
at the town, and whose P373 is its category. The recorded QIDs were then re-verified as one batch (22 towns,
2026-10-11, no >50 km P625 flag fired): **every label matches, every P373 equals the recorded category string
(the category route's target), every P625 sits within 0.74 km of the recorded site point**. The site point is
the old-town centre the plan is centred on, hand-recorded on the row; the P625 (municipality point) is recorded
beside it, and the last column is the distance between them - the Gouda 800 m class of offset, computed rather
than eyeballed (Gouda's own is in `pipeline/sources.py`). The enwiki column is the staged `wikipedia` field
(absent when the verified item has no enwiki link - sources.py's rule).

| Town | QID | Label | P625 (lon, lat) | Site point (lon, lat) | P625 → site | enwiki |
|---|---|---|---|---|---|---|
| Aardenburg | Q955 | Aardenburg | 3.445278, 51.274444 | 3.4453, 51.2744 | 0.01 km | Aardenburg |
| Alkmaar | Q972 | Alkmaar | 4.744, 52.6289 | 4.7427, 52.6285 | 0.10 km | Alkmaar |
| Amsterdam | Q727 | Amsterdam | 4.883333, 52.366667 | 4.8865, 52.3725 | 0.68 km | Amsterdam |
| Enkhuizen | Q9918 | Enkhuizen | 5.283333, 52.7 | 5.286, 52.7025 | 0.33 km | Enkhuizen |
| Goes | Q81220 | Goes | 3.883333, 51.5 | 3.885, 51.5043 | 0.49 km | Goes |
| Groningen | Q749 | Groningen | 6.5675, 53.218889 | 6.571, 53.2197 | 0.25 km | Groningen |
| Groningen (province) | Q752 | Groningen | 6.737778, 53.258056 | 6.7378, 53.2581 | 0.01 km | Groningen (province) - drop: province map, no site |
| Haarlem | Q9920 | Haarlem | 4.635556, 52.381389 | 4.634, 52.388 | 0.74 km | Haarlem |
| Leeuwarden | Q25390 | Leeuwarden | 5.783333, 53.2 | 5.793, 53.2007 | 0.65 km | Leeuwarden |
| Middelburg | Q52101 | Middelburg | 3.613611, 51.499722 | 3.614, 51.5006 | 0.10 km | Middelburg, Zeeland |
| Reimerswaal | Q2590944 | Reimerswaal | 4.172486, 51.507539 | 4.172486, 51.507539 | 0.00 km | Reimerswaal (city) |
| Rotterdam | Q34370 | Rotterdam | 4.48, 51.92 | 4.4745, 51.9155 | 0.63 km | Rotterdam |
| Sluis | Q10080 | Sluis | 3.5, 51.35 | 3.493, 51.347 | 0.59 km | Sluis |
| The Hague | Q36600 | The Hague | 4.31, 52.08 | 4.305, 52.079 | 0.36 km | The Hague |
| Utrecht | Q803 | Utrecht | 5.121667, 52.090833 | 5.1185, 52.091 | 0.22 km | Utrecht |
| Valkenburg | Q100076 | Valkenburg | 5.83205, 50.86523 | 5.83205, 50.86523 | 0.00 km | (none on the item) |

The 3 done NL towns (Gouda Q84125, Zwolle Q793, Venlo Q9777) were re-confirmed in the same run (label match,
P373 the plain town category); their rows stay in `pipeline/sources.py`. No NL QID is already in the built
catalog (checked against the 12575-site catalog on 2026-10-11), so every NL town gets a new catalog entry -
the BE/FR/LU batches re-check this per town, since `stage()` reuses an existing site id automatically when a
QID already has one.

### Name-search traps - the Netherlands

A bare name search is not verification: all three traps below sit within 10 km of the true town (the >50 km
distance guard would not have flagged them) - the label + P373 + enwiki checks are what caught them. The
caption route stores the verified site point, so the exposure of a mis-resolution is documentary only, but
these are the cases where a first-search hit is the WRONG item:

- **Sluis** - the search resolves FIRST to Q2065987 'Sluis', a distinct item (a fortified town with town
  rights; no enwiki; P625 3.3883, 51.3089, 9.0 km SW of the town; P373 'Sluis (city)'). The recorded Q10080 is
  the town (P373 'Sluis', enwiki 'Sluis').
- **Reimerswaal** - the search resolves first to the municipality Q10078 (P625 4.1167, 51.4333, 9.1 km away; it
  shares the P373 'Reimerswaal' category with the city, so even the P373 check cannot tell them apart). The
  recorded Q2590944 is the city (enwiki 'Reimerswaal (city)'), and its P625 is the recorded site point itself.
- **Valkenburg** - the search resolves first to the modern town Q9771 'Valkenburg aan de Geul' (0.14 km from
  the old town, the same spot). The recorded Q100076 is the old town (P373 'Valkenburg, Limburg'); it has no
  enwiki link, so its staged row carries no wikipedia field.

## QID verification - Belgium (checked 2026-10-11; re-run with `.venv/bin/python fit/src_van_deventer.py --verify`)

Method: the same as the NL batch - discovery for the 19 towns without a recorded QID (the search candidates
with their label, every P625, P373, P131 and enwiki; transcript /tmp/vd_verify_be_iter45.txt) plus Ghent Q1296,
already hand-verified in the prep (2026-10-11 01:32), recorded as is and re-confirmed by the same run. Mons was
the one town the module's 5-candidate search missed: the label search 'Mons' ranks the planetary nomenclature
term and ten French communes above the Belgian city (11th in the en results, 4th in the fr), so a follow-up
search at limit 20 found Q83407, whose facts (label 'Mons', P625 at the town, P373 'Mons (Hainaut)', enwiki
'Mons, Belgium') confirm it. All 20 were then re-verified in one batch (transcript
/tmp/vd_verify_be_recheck_iter45.txt): **every label matches, every P373 equals the recorded category string,
every P625 sits within 0.01 km of the recorded site point** (the site point is the P625 rounded - the hand
check found no offset from the old-town centre, unlike the NL Gouda 800 m case). The enwiki column is the
staged `wikipedia` field. Four items carry a disambiguated P373 ('Brussels (municipality)', 'Halle
(Belgium)', 'Mons (Hainaut)', 'Leuze-en-Hainaut') - the category route's target is that exact string, so the
chain walk must reach it (the --chain step of each of these four towns is the watch item). Saint-Ghislain's
item (Q668950) has no en label on Wikidata (the re-check prints an empty label, not a mismatch: the search
API's label and the enwiki article 'Saint-Ghislain' both confirm it). No BE QID is in the built catalog
(checked against the 12575-site catalog on 2026-10-11): all 20 get new catalog entries.

| Town | QID | Label | P625 (lon, lat) | Site point (lon, lat) | P625 → site | enwiki |
|---|---|---|---|---|---|---|
| Ath | Q95096 | Ath | 3.776941, 50.631139 | 3.7769, 50.6311 | 0.01 km | Ath |
| Braine-le-Comte | Q95129 | Braine-le-Comte | 4.136111, 50.609722 | 4.1361, 50.6097 | 0.00 km | Braine-le-Comte |
| Bruges | Q12994 | Bruges | 3.224167, 51.208889 | 3.2242, 51.2089 | 0.00 km | Bruges |
| Brussels | Q239 | Brussels | 4.351667, 50.846667 | 4.3517, 50.8467 | 0.00 km | City of Brussels |
| Chimay | Q95380 | Chimay | 4.317334, 50.047927 | 4.3173, 50.0479 | 0.00 km | Chimay |
| Chièvres | Q95318 | Chièvres | 3.8, 50.583333 | 3.8, 50.5833 | 0.00 km | Chièvres |
| Enghien | Q666238 | Enghien | 4.041111, 50.695556 | 4.0411, 50.6956 | 0.01 km | Enghien |
| Ghent | Q1296 | Ghent | 3.725278, 51.053611 | 3.7253, 51.0536 | 0.00 km | Ghent |
| Halle | Q210003 | Halle | 4.237222, 50.736111 | 4.2372, 50.7361 | 0.00 km | Halle, Belgium |
| Kortrijk | Q12995 | Kortrijk | 3.265833, 50.8275 | 3.2658, 50.8275 | 0.00 km | Kortrijk |
| Lessines | Q667790 | Lessines | 3.83, 50.7117 | 3.83, 50.7117 | 0.00 km | Lessines |
| Leuze | Q667862 | Leuze-en-Hainaut | 3.616667, 50.6 | 3.6167, 50.6 | 0.00 km | Leuze-en-Hainaut |
| Mechelen | Q162022 | Mechelen | 4.480278, 51.028056 | 4.4803, 51.0281 | 0.01 km | Mechelen |
| Mons | Q83407 | Mons | 3.9525, 50.454722 | 3.9525, 50.4547 | 0.00 km | Mons, Belgium |
| Ostend | Q12996 | Ostend | 2.919444, 51.225833 | 2.9194, 51.2258 | 0.00 km | Ostend |
| Saint-Ghislain | Q668950 | Saint-Ghislain (no en label on Wikidata) | 3.816667, 50.45 | 3.8167, 50.45 | 0.00 km | Saint-Ghislain |
| Soignies | Q462985 | Soignies | 4.066667, 50.566667 | 4.0667, 50.5667 | 0.00 km | Soignies |
| Tournai | Q173219 | Tournai | 3.388056, 50.605556 | 3.3881, 50.6056 | 0.01 km | Tournai |
| Aarschot | Q273442 | Aarschot | 4.8333, 50.9842 | 4.8333, 50.9842 | 0.00 km | Aarschot |
| Oudenaarde | Q12992 | Oudenaarde | 3.6, 50.85 | 3.6, 50.85 | 0.00 km | Oudenaarde |

The 2 done BE towns (Damme Q323408, Binche Q95121) stay in `pipeline/sources.py`; no BE QID collides with the
catalog, so no BE town stages under an existing site id.

### Name-search traps - Belgium

- **Mons** - the batch's biggest trap, and the one the module's search could not see: 'Mons' (limit 5, en)
  returns the planetary nomenclature term 'mons' and the French communes (Var, Hérault, Charente, Gard) - the
  Belgian city is 11th. A follow-up search at limit 20 (the fr search ranks it 4th) found Q83407; its P373
  'Mons (Hainaut)' and enwiki 'Mons, Belgium' confirm it. The re-check shows what a bare resolution would do:
  first hit Q1108786 (Mons, Var) 780 km away.
- **Leuze** - the first search hit with coordinates is the French Leuze (Aisne) Q326134, 92 km away (the
  >50 km guard would have flagged it; the label check would too - the true item's label is the official
  disambiguated 'Leuze-en-Hainaut', not the bare 'Leuze').
- **Bruges** - the first search hit with coordinates is the French Bruges (Gironde) Q327025, 759 km away
  (P373 'Bruges (Gironde)' separates it from the verified Q12994, P373 'Bruges').
- **Mechelen** - no trap on the first hit, but the third candidate is the Dutch Mechelen (Gulpen-Wittem,
  Q100020) - the label + P373 checks ('Mechelen' vs 'Mechelen (Netherlands)') separate them.

## France, Luxembourg (pending)

24 towns left to verify with the same method (FR 23 + LU 1); this section grows per batch, and every
unverifiable QID lands here with its reason (box 2).

- **Beaumont's country settles at verification**: the candidate list holds a Hainaut (Belgium) town and
  northern-France towns - the Barnard-Castle-style trap. The TOWNS region value is the `france` guess; it
  flips to `belgium` if the verified item is the Hainaut one.
- **Luxembourg City** (Q1564 expected from the search 'Luxembourg (city)'): the staged row's region will be a
  NEW lowercase value `luxembourg`. `build_catalog`'s REGION_NAME has keys for belgium/netherlands/france but
  no luxembourg, so the site display falls back to the raw value (its line-91 default) - acceptable, but a
  REGION_NAME key is a small follow-on task.
- The prep's "from general knowledge" candidates are all discarded: Brussels Q239 is now the verified BE row
  above (its P373 is 'Brussels (municipality)', not 'Brussels'); Lille (the prep's Q1793) waits for the FR
  batch; The Hague Q36600 and Groningen Q749 are the verified NL rows (neither is the prep's guess).

## Per town: staged picture or documented drop

The `--files` inventory (the 60 town categories + the 4 collections) supplies the picks, one best full plan
per town: the drawing's date c. 1545-1565 on every staged row (the file's own date when it is the drawing's;
else the known drawing date with the Commons date kept as `date_commons` - the Gouda/Zwolle precedent in
sources.py). Unusable files (photos, modern reprints, detail crops, redrawn models, too small) and misfiled
files (a plan found in another town's category - staged once under the true town) are listed here with their
specific reason.

### The Netherlands (16 categories: 13 staged, 3 documented drops; checked 2026-10-11, `--files` transcript
`/tmp/vd_files_nl_iter43.txt` - re-run: `.venv/bin/python fit/src_van_deventer.py --files <towns>`)

- **Aardenburg** - staged `Aardenburg 1560.jpg` (500x500, "circa 1560"): the only Aardenburg plan on Commons
  and a full plan - staged despite the <~1000 px size heuristic (the one such case, noted here).
- **Alkmaar** - staged `Kaart van Alkmaar en Oudorp door Jacob van Deventer 01.jpg` (5019x4971, 1550-1570,
  the drawing itself). Not staged: the BNE atlas plate (2572x2859, c. 1560), the RAA 1900 redraw after it
  (6204x4091, "depicted 1560; reproduction 1900"), the c. 1920 "kleine kaartje" redrawn after Deventer
  (2873x2142, uploaded 2016), the RCE album reproduction (2886x2110, undated) - all copies, the original wins.
- **Amsterdam** - staged `Kaart van Amsterdam c1550 (City Map) Jacob van Deventer.jpg` (4283x5229,
  between 1550 and 1570 - the first map of Amsterdam in the true sense, the drawing). Not staged: the BNE
  atlas plate (1190x932, 1560-61), the GAA partial after Nijhoff (2468x3076, undated), the RCE album
  reproduction ("Scan 1980 (origineel circa 1550)", 2118x2891).
- **Enkhuizen** - staged `Jacob van Deventer Enkhuizen 1558-1560.jpg` (2514x2387, 1558-1560). Not staged: its
  detail twin (1056x1053, same dates).
- **Goes** - staged `Goes 1572 Bijkrt v Deventer.jpg` (1412x1784, page date 1560): the only Goes row inside
  the c. 1545-1565 window. Not staged: the minuutkaart (1572), the netkaart (dated 1572/1575 - a later
  revision, also in the BNE category), the 1988 RCE stadhuis-interior drawing (3072x3072).
- **Groningen (city)** - staged `Jacob van Deventer - Groningen volledig.jpg` (6568x5088, between c. 1563 and
  c. 1567): the netkaart with its attached carton. Not staged: the BNE plate (1282x1320, c. 1565), the carton
  crop (2435x1789 png, 1563-67).
- **Groningen (province)** - DROP: a province map, not a town plan (no site, no picture). Its two files are
  crops of the Friesland gewestkaart: `... - Groningen.jpg` (4821x4969, 1559 - the province visible on it) and
  `... - Klooster Maria ten Hoorn.jpg` (1006x1020 - the abbey detail).
- **Haarlem** - staged `...Inventarisnummer NL-HlmNHA 1100 KNA006000046.JPG` (2359x2272, 1565): the Haarlem
  municipal collection's scan of the drawing. Not staged: `Kaart van Haarlem door Jacob van Deventer.jpg` and
  `Jacob-van-deventer1560.jpg` (two identical 3306x8152 no-desc uploads of a tall sheet), the municipal
  "Kopie" (10966x7872, 1565), the "volgens de oude teekening" reproduction (6927x3701, 1565), an undated
  1213x1332 scan, the northern-gracht crop (1302x578, 1560).
- **Leeuwarden** - DROP: its only file `Ontstaan leeuwardendelen.jpg` (593x636) is a 1975 redrawn model by
  J.R.G. Schuur after Deventer's drawing (the desc says so) - not the plan itself; `commons.keep()`'s
  "model" no-word drops it independently.
- **Middelburg** - DROP: its only file (20154723 - RCE, 2412x3233, 1942) is a detail crop of the stadhuis from
  the RCE album; no full Middelburg plan on Commons.
- **Reimerswaal** - staged `Reimerswaal 1560 Minuut v Deventer.jpg` (3501x2541, 1560): the original
  minuutkaart. Not staged: the bijkaart (1550x1476, 1560), the netkaart (2541x3095, 1560), the "circa 1560"
  plate (1464x1444), the BNE atlas plate "Manuscrito 13" (1617x2513, 1545).
- **Rotterdam** - staged `Map of Rotterdam around 1560s by Jacob van Deventer.jpg` (2953x2033). The page's
  year-only date is 1563 (one year of the drawing's 1558-1563 window, which the desc dates via the 1563 city
  fire); the row carries the known "circa 1560" (the title's own "around 1560s") and keeps 1563 as
  `date_commons` - the Gouda/Zwolle precedent. Not staged: the uitsnede (947x948, 1563), a 2025 Piet Ratsma
  photo (3543x3543), the 1918 book-page crop (1189x1535), a 1911 scan (1911x1921, 1550).
- **Sluis** - staged `...Zeist en Sint Anna ter Muiden - Sluis - 20201361 - RCE.jpg` (2900x2137, 1980): the
  RCE album reproduction - the only full-plan candidate (the Zwolle done-row precedent). The row carries the
  known drawing window "circa 1545-1565" and keeps 1980 as `date_commons`. Misfiled (R5): the Sluis category
  also holds `227 Damme.jpg` (2684x2606, 1545) - Damme's netkaart, also in the BNE category; Damme is a done
  town whose canonical row uses its own file, so note only, never staged here.
- **The Hague** - staged `1558, Den Haag. Jacob van Deventer.jpg` (4413x4705, 1558): the drawing itself
  (autograph; the same file also sits in the Nationaal Archief collection category).
- **Utrecht** - staged `Utrecht.jpg` (2164x2155, between 1565 and 1570): the full plan. Not staged: three RCE
  album reproductions (1955, 1955-glasplaat, 1982) and the 1000x557 Buiten-Wittevrouwen suburb map (1569).
- **Valkenburg** - staged `...te Zeist - Valkenburg - 20237999 - RCE.jpg` (2878x2102, 1980): the RCE album
  reproduction - the only full-plan candidate (also in the RCE category). The row carries "circa 1545-1565"
  and keeps 1980 as `date_commons`. Not staged: the other nine files (346-2658 px: Limburgish-dialect wiki
  crops, the 1961/1955 RCE details, two 2013/2014 photos, the 500x501 "16th century" scan).

### Belgium (20 categories: 19 staged, 1 documented drop; checked 2026-10-11, `--files` transcript
`/tmp/vd_files_be_iter46.txt` - re-run: `.venv/bin/python fit/src_van_deventer.py --files <towns>`)

One 1545 BNE atlas plate per town (page date 1545 = the drawing's date, no `date` swap), except the four named
below: Brussels and Mechelen are KBR autographs (their own page dates are the drawing's), Bruges is the full
plan dated by its own caption, Ostend the BNE plate (circa 1562). Every ambiguous candidate (Ghent BN 1 vs
BN 2, Mons (1) vs (2), the three Brussels sheet versions, Bruges full vs detail, Aarschot) was eye-checked
from 1200 px thumbs + full-size crops before being picked or rejected (the /tmp/vd_be_thumbs/ set of 2026-10-11;
re-download via `commons.info` with the `aw.UA` User-Agent - the Commons API 403s without one).

- **Ath** - staged `Ath - Deventer.jpg` (3438x2614, 1545). Not staged: `Plan Ath Deventer.jpg` (2055x2098,
  "before 1575" QS) - a later revision.
- **Braine-le-Comte** - staged `Braine-le-Comte - Deventer.jpg` (1816x2614, 1545): the only file.
- **Bruges** - staged `Map of Bruges by Jacob van Deventer.jpg` (2770x4659): the full plan. The page date
  2013-01-17 12:04:47 is an upload timestamp, but the sheet's OWN caption block (bottom edge, partly torn
  away) reads "Brugge (West Flan...) ... en omgeving omstreeks den jare 1550. Plattegrond in kleuren.
  Originalade Teckening van den be-Keizerlijken..." - the drawing dates itself c. 1550, so the row carries
  `date` "circa 1550" and keeps 2013 as `date_commons` (the Gouda/Zwolle precedent). The three category detail
  files carry QS 'circa 1558' for the same map - the sheet's own caption wins. Not staged: the five detail
  crops (846x522, 1180x668 x2, 573x564, 650x832) and `Plan Brugge Jacob van Deventer ca.1560.jpg` (1400x1867,
  a published reproduction per C. Ruelen).
- **Brussels** - staged `... 73 places levées, ca. 1555 (2) 01.png` (8908x10941, page 'circa 1555' = the
  drawing's date): the KBR autograph, cleanly cropped. Not staged: `...(2).png` (9216x12288) - the same sheet
  WITH a TIFFEN colour-calibration strip (the ugly duplicate); `...(2) 02.png` (5580x5478) - an explicit
  detail; `Brussel 1550 v Deventer¹.JPG` (470x561), `Brussel 1555 Deventer.jpg` (600x752) and `Brussel 1560 v
  Deventer.jpg` (1233x1479, the 'minuut' per the desc) - three small scans; `Molenbeek.1550.jpg` (378x565,
  Molenbeek + the west of the 2e enceinte - a partial: the work list's 'Brussel, 1550 (westelijk gedeelte)').
- **Chimay** - staged `Chimay - Deventer.jpg` (1816x2614, 1545): the only file.
- **Chièvres** - staged `Chièvres - Deventer.jpg` (1816x2614, 1545): the only file.
- **Enghien** - staged `Enghien - Deventer.jpg` (3425x2614, 1545): the only file.
- **Ghent** - staged `Ghent by Jacob Van Deventer, BN 1.jpg` (4919x5046, 1545): the sheet labelled 'Gande'
  (the city between its two rivers). Not staged: `... BN 2.jpg` (2834x3631, 1545) - a DIFFERENT unlabelled
  sheet (a fortified town, no city label in the centre crop); `Map of Ghent, Belgium, Donato Buoni di
  Pellezuoli.jpg` (1600x1600, 1559) - a later print by another cartographer; five small 2007-2012
  scans/crops (457-1510 px).
- **Halle** - staged `Halle - Deventer.jpg` (1816x2614, 1545; the desc names the town 'Hal'): the only file.
- **Kortrijk** - staged `Kortrijk, map by Jacob van Deventer.JPG` (3753x2614, 1545): the only file.
- **Lessines** - staged `Lessines - Deventer.jpg` (1816x2614, 1545): the only file.
- **Leuze** - staged `Leuze - Deventer.jpg` (1816x2614, 1545, desc 'Leuze'): the only file. The caption route
  names the town 'Leuze' - as the file prints it, not the item's official label 'Leuze-en-Hainaut'.
- **Mechelen** - staged `Mechelen, Belgium, Deventer, 1550.png` (3558x3305, page date 1550 = the drawing's;
  the work list 'Mechelen, 1550' agrees): the KBR autograph (the desc names the atlas the KBR bought in 1866).
- **Mons** - staged `Mons (2) - Deventer.jpg` (4393x2614, 1545): the wide two-page sheet labelled 'Mons en
  Henault' (Ocidente/Oriens/Meridies/Septentrio). Not staged: `Mons (1) - Deventer.jpg` (1816x2614, 1545) -
  a portrait plate of the same fortified town.
- **Ostend** - staged `Oostende map Jacob van Deventer.png` (872x1255, page 'circa 1562' = the drawing's
  date): the full BNE atlas plate (the town + a harbour detail box, labelled 'Oostende') - the ONLY Ostend
  plan on Commons, staged despite the <~1000 px width heuristic (the Aardenburg case; this is the caveat).
- **Saint-Ghislain** - staged `Saint-Ghislain - Deventer.jpg` (1816x2614, 1545): the only file.
- **Soignies** - staged `Soignies - Deventer.jpg` (1816x2614, 1545). Not staged: `Carte de Soignies
  d'après la carte Deventer.jpg` (2362x2468, 2011 - a redrawn copy) and `Carte jacques deventer
  soignies.jpg` (291x298, 2011 - a tiny scan).
- **Tournai** - staged `Tournai - Deventer.jpg` (3296x2608, 1545): the only file.
- **Oudenaarde** - staged `Oudenaarde, map by Jacob van Deventer, Version Madrid.JPG` (3368x2614; the page
  date 1545 is kept - the nl.wikipedia work list dates the netkaart 1564, noted here). Not staged: the detail
  (710x564, QS 'circa 1558'), `Oudenaarde plan Deventer DI-676.jpg` (986x1000, uploaded 2005) and `... Version
  Brussels.jpg` (948x1070, uploaded 2012) - copies.
- **Aarschot** - DROP (no site, no picture): both files are dated **1570** - `Aarschot 1570.png` (5877x6291,
  a genuine autograph: the town labelled 'Aersfot' on the Dijle, the fortress on the north bank) and its
  `Aarschot, Belgium, Jacob van Deventer, 1570.jpg` copy (1278x1024). 1570 is outside this task's c. 1545-1565
  drawing window, so no row can be staged honestly (box 6 checks the row date's year in the window); the
  documented drop (box 5) beats a guessed date. Cross-checked on the web: the nl.wikipedia article 'Jacob
  van Deventer (cartograaf)' lists 'Aarschot, 1570' in its work list (the Philip II period; his career ran to
  his death in 1575, and the Rutte & Vannieuwenhuyze Stedenatlas covers 1545-1575 overall).

### France, Luxembourg (pending)

24 towns left (FR 23 + LU 1), one bullet per town as the `--files` inventories run; the BNE atlas plates are
the expected picks there (the collection section below), and the Aire+Thérouanne and Hesdin+Vieil-Hesdin
double plates the watch items (stage once under the true primary, note the second).

## The collection categories (checked 2026-10-11, the `--files` run)

- **BNE - 61 files**: the "Planos de ciudades de los Países Bajos" atlas (Part II and III); nearly all
  page-date 1545 (the Charles V campaign) - the expected picks for the FR/BE batches. It covers all 23 FR
  towns (Arras, Douai, Lille, Mons, Saint-Omer, Valenciennes as (1)/(2) double plates) and 16 of the 20 BE
  towns (Ath, Braine-le-Comte, Chimay, Chièvres, Enghien, Ghent as BN 1/2, Halle as "Hal", Kortrijk, Lessines,
  Leuze, Mons, Ostend, Oudenaarde as the "Version Madrid" plate, Saint-Ghislain, Soignies, Tournai; Bruges,
  Brussels, Mechelen and Aarschot are not there; plus done Binche). Double plates - one file, two towns (stage
  once under the true primary town, note the second): `Aire-sur-la-Lys - Deventer.jpg` (3395x2614) is
  "Aire-sur-la-Lys & Thérouanne"; `Hesdin - Deventer.jpg` (3408x2614) is "Hesdin & Vieil-Hesdin" (French desc,
  odd date field: Hesdin 1554-1575, Vieil-Hesdin "probablement 1545"). Files that duplicate a town-category
  file (the inventory's `[also in: ...]` tag): Alkmaar, Damme, Goes, Reimerswaal, Amsterdam - same files, not
  double-staged. Out of scope (no town category among the 66): Appingedam, IJlst, Woudrichem/Gorinchem
  (2 files), Nieuwpoort+Dunkerque (Manuscrito 75, 2 files), Hontscoten+Veurne (Manuscrito 74, 3 files), plus
  done Venlo.
- **NA - 2 files**: the The Hague autograph (the staged file; the same file also sits in The Hague's town
  category) and the Schoonhoven & Nieuwpoort two-town sheet (c. 1550, 5161x4430 - out of scope, neither town
  has a category).
- **RCE - 69 files**: reproductions of the Zeist (Monumenten Zorg) album, 1955-1981 plus a few 1912-1963
  scans. Supplied the staged rows for Sluis and Valkenburg (each the only full-plan candidate), the done Zwolle
  row (20228487, the same file) and the done Venlo row (20241009, plus the Hertogenhof and Picardiemolen
  details); the Middelburg file is detail-only (the drop above). The rest are other NL towns outside the 60
  (Almelo, Amersfoort, Arnhem, Bergen op Zoom, Bolsward, Bredevoort, Brielle, Buren, Culemborg, Deventer,
  Dokkum, Franeker, Geervliet, Harlingen, Hasselt, Heusden, Hindeloopen, IJlst, Medemblik, Montfoort, Muiden,
  Nijmegen, Ootmarsum, Oudewater, Roermond, Schiedam, Stavoren, Tholen, Tiel, Veere, Vianen, Vlaardingen,
  Vollenhove, Woerden, Workum, Woudrichem, 's-Hertogenbosch, Zaltbommel, Zutphen) or duplicates of
  town-category files (tagged `[also in: ...]`).
- **Atlas - 6 files (1 root + 5 in one subcategory)**: the root holds `Deventer-Dionantum.jpg` (6144x6144,
  1550-1565 - Deventer is not among the 66, out of scope) and a single subcategory, `Map of Landrecies by
  Jacob van Deventer (Atlas des villes des Pays-Bas : ...)`, with 5 KBR detail scans (1091-1805 px,
  1550-1565). That subcategory double-parents: it also hangs under the plain Landrecies town category (why
  `town_files` inventories each town category's own subcategories at depth 1) - the Landrecies batch picks
  from the town category, the KBR details are the fallback candidates.

## Summary (pending - the NL and BE subtotals are in, the FR/LU batches fill the rest)

Netherlands: 13 of 16 staged, 3 documented drops (Groningen province, Leeuwarden, Middelburg). Belgium:
19 of 20 staged, 1 documented drop (Aarschot - both files dated 1570, outside the c. 1545-1565 window). So
far 32 of 59 stageable towns staged (NL 13 + BE 19). France, Luxembourg: 24 towns pending (the BNE atlas
plates are the expected picks there). Box 5: >= 50 of 60 staged, or every missing one accounted for in the
sections above; every unverifiable QID named with its reason (box 2). The six done towns appear nowhere in
this task's staging files.
