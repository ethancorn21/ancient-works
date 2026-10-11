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
asserts it against the module's TOWNS table (a rename or a new category fails loud); it passed on 2026-10-11,
re-confirming the old prep's 2026-10-10 census (two more live runs on 2026-10-11).

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
Philippe II` (per-town plate subcategories at depth 1). What each holds and which town's picture it supplies:
the "The collection categories" section (pending the `--files` inventory).

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

## Belgium, France, Luxembourg (pending)

44 towns left to verify with the same method (BE 20 + FR 23 + LU 1), in three batches; this section grows per
batch, and every unverifiable QID lands here with its reason (box 2).

- **Ghent Q1296 is already verified** (prep, 2026-10-11: label 'Ghent', P373 'Ghent' the plain town category,
  P625 3.7253, 51.0536 at the city centre, enwiki 'Ghent') and will be recorded in the TOWNS table with the BE
  batch. The prep's other "from general knowledge" candidates (Brussels, Lille, and an older The-Hague/Groningen
  guess) are discarded as candidates - each is fetched and checked like the rest (The Hague Q36600 and
  Groningen Q749 are the verified NL rows above, and neither is the prep's guess).
- **Beaumont's country settles at verification**: the candidate list holds a Hainaut (Belgium) town and
  northern-France towns - the Barnard-Castle-style trap. The TOWNS region value is the `france` guess; it
  flips to `belgium` if the verified item is the Hainaut one.
- **Luxembourg City** (Q1564 expected from the search 'Luxembourg (city)'): the staged row's region will be a
  NEW lowercase value `luxembourg`. `build_catalog`'s REGION_NAME has keys for belgium/netherlands/france but
  no luxembourg, so the site display falls back to the raw value (its line-91 default) - acceptable, but a
  REGION_NAME key is a small follow-on task.

## Per town: staged picture or documented drop (pending)

The `--files` inventory (the 60 town categories + the 4 collections) supplies the picks, one best full plan
per town: the drawing's date c. 1545-1565 on every staged row (the file's own date when it is the drawing's;
else the known drawing date with the upload date kept as `date_commons` - the Gouda/Zwolle precedent in
sources.py). Unusable files (photos, modern reprints, detail crops, too small) and misfiled files (a plan found
in another town's category - staged once under the true town) are listed here with their specific reason.

## The collection categories (pending)

The BNE autographs, the NA scans, the RCE scans and the BNE atlas (73 places, of which some towns have no town
category of their own and stay out of scope, documented here). Per collection: what it holds and which town's
staged picture it supplied, if any.

## Summary (pending)

staged N of 60 town categories (box 5: >= 50 staged, or every missing one accounted for in the sections above);
every unverifiable QID named with its reason (box 2). The six done towns appear nowhere in this task's staging
files.
