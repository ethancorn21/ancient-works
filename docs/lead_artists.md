# Artists' views as sources of old pictures (task 213)

GOAL.md point 5 (the 2026-10-10 change): artists' aerial and bird's-eye views count as drawings as much as
surveys do - of Leonardo's 1502 plan of Imola the owner says it "should 100% be on our map". The four
sources: Leonardo da Vinci's aerial plan of **Imola** (1502, Royal Collection RCIN 912284), Jacopo de'
Barbari's view of **Venice** (1500), Braun & Hogenberg's **Civitates Orbis Terrarum** (1572-1617), and
Merian's **Topographia** (1640s-1680s). The image-level sources are staged in this task's own files
(`data/catalog/extras_artists.jsonl`, `data/commons/files_artists.jsonl`, `data/commons/classified_artists.jsonl`);
211 consolidates and builds the sites, 212's cover runs the fitting loop.

Both sites are **aerial-photograph ground** (no open LiDAR here: `FITKIT_GROUND=aerial`, `tools/fitkit.py`).
The `evidence` field on every staged row is **hand-recorded** `caption_coords` in the exact key order of
`fit/evidence.py:caption_route`; `fit/evidence.py check` passes offline from the stored fields, and the
module's `--check` re-runs it. `record --live` would re-resolve the caption by name search: for Venice the
first search hit with coordinates is the trap (Q773853 "Venice", Los Angeles, 9891 km), so the hand record
is what stands; for Imola the live route resolves the right QID but to the modern city point, while the
hand record pins the sheet's own centre (the walled old town).

The hand-checked file → site table lives in `fit/src_artists.py` (the `pipeline/sources.py` pattern). A
picture of a site whose QID is already in the catalog gets a picture row for that existing site id, never a
new catalog entry (`stage()`/`check_staged()` enforce it).

## QID verification (checked 2026-10-11, re-run with `.venv/bin/python fit/src_artists.py --verify`)

```
checked 2026-10-11 - 2 QIDs (Wikidata)
  Q50195  'Imola'
      P625: [(11.714722222222, 44.353055555556)]  (table site point: 11.7112, 44.3535)
      P373: ['Imola']  (table cat: 'Imola')
      P131: [('Province of Bologna', 'Q16139'), ('Metropolitan City of Bologna', 'Q18288145')]  (table place: 'Emilia-Romagna, Italy')
      enwiki: 'Imola'  (table wikipedia: 'https://en.wikipedia.org/wiki/Imola')
      search 'Imola': first hit with P625 is Q50195 'Imola' (11.714722222222, 44.353055555556)
  Q641  'Venice'
      P625: [(12.331944444444, 45.439722222222)]  (table site point: 12.331944, 45.439722)
      P373: ['Venice']  (table cat: 'Venice')
      P131: [('Venetian Province', 'Q6360367'), ('province of Venice', 'Q3924689'), ('Province of Venice', 'Q16310'), ('Metropolitan City of Venice', 'Q3678587')]  (table place: 'Veneto, Italy')
      enwiki: 'Venice'  (table wikipedia: 'https://en.wikipedia.org/wiki/Venice')
      search 'Venice': first hit with P625 is Q773853 'Venice' (-118.45916666666666, 33.990833333333335)   <- TRAP: 9891 km, the live record would store a conflict (kind none)
```

Trap notes: a **name search alone gives the wrong place** - "Venice" resolves to Venice, California first
(9891 km), and "Imola" is a common toponym (Hungary, California; and an OSM hamlet near Vergato that
Nominatim ranks first). The table points are hand-checked against the enwiki/Wikidata values above, never
taken from a name search.

## Imola - Leonardo da Vinci, aerial plan, 1502 (the anchor)

- **What it is.** A bird's-eye aerial plan of the walled town of Imola, drawn by Leonardo in 1502
  (Royal Collection, RCIN 912284; the sheet is oriented with the south toward the top). The walled town
  sits at the centre of the sheet's circular view: the street grid and blocks inside the walls, gates
  puncturing the perimeter, the **Rocca Sforzesca** fortress projecting from one edge (drawn in detail -
  its corner towers and court make it the sheet's identifying feature), and the **Santerno** river
  (labelled "Sant'Arno" in Leonardo's own mirror script, read off the sheet) meandering past with the road
  crossing beyond the wall. Old enough: a 1502 view of the structure, exempt from the 150-year rule;
  freely machine-readable: public-domain scans on Commons.
- **Where the files live.** Commons, category-linked to the Royal Collection object:
  - **STAGED** - `File:Leonardo da Vinci - RCIN 912284, A map of Imola 1502.jpg` (2000x1483, Public domain,
    artist Leonardo da Vinci; the file page has **no DateTimeOriginal** - upload 2020 - so the known
    drawing date is used and noted here, exactly the box-1 case: the staged row carries `year: 1502`
    (from the file title "A map of Imola 1502") with `date` left empty).
  - DROP - `File:Leonardo da Vinci - Plan of Imola - Google Art Project.jpg` (6164x4545, DateTimeOriginal
    1502): fails `commons.keep()` (the "google" NO rule is a harvest heuristic against map screenshots),
    and 211's merge re-judges every row with `commons.rows()` and would drop it anyway - a dead row.
  - DROP - `File:Leonardo da vinci, Town plan of Imola.jpg` (1030x774, Public domain, circa 1502):
    verified live 2026-10-11 to be **another scan of the same RCIN 912284 sheet** (same view, walls,
    river, margin legend and notes) - a second row for the same picture adds nothing; one row per picture.
  - DROP - `File:Leonardo da Vinci - RCIN 912686, Recto Sketches of the street plan of Imola.jpg`
    (1517x2000 portrait, Public domain, undated): a **different work** - the measured survey sketches
    (block grids with measurements, small fortress details) the sheet was made from, not the bird's-eye
    view itself.
  - DROP - `File:Imola 1705.jpg` (942x710, Public domain, 1705, Antonio Ferri): a flat plan by another
    hand from another century - not one of this task's four GOAL sources.
- **The site point.** `imola-q50195` is pinned at **11.7112 E, 44.3535 N - Piazza del Duomo, the centre of
  the walled old town** (OSM), which is also the sheet's own centre (the walled town is at the middle of
  the circular view). Q50195's P625 (11.7147, 44.3531) equals the enwiki infobox
  (44°21'11"N 11°42'53"E) - the correct modern city point, 0.27 km east of the walled centre; the site
  uses the walled centre so the 2000 m fit box sits on the drawn town. **Correction of the prep notes:**
  the prep's "old town centre ≈ 44.245 N, 12.367 E" was wrong - that point is Cervia on the Ravenna
  coast (~50 km SE); the prep then misread Q50195's P625 as "a bad value ~53 km NW of the town". The
  P625 was never bad; three independent sources (enwiki infobox, Wikidata P625, the OSM town node with
  the F1 circuit and the Santerno beside it) agree on 44.353 N, 11.715 E. (Side note: OSM's administrative
  boundary for the comune is mis-drawn - Nominatim displays the urban area as "Imola, Nuovo Circondario
  Imolese" - so the site was never geocoded from OSM; the record above is the source.)
- **Staged rows.** `extras_artists.jsonl`: `imola-q50195` (name, place "Emilia-Romagna, Italy",
  lon/lat above, region "Italy", kind "town" = 2000 m box, QID, wikipedia, `aerial_ok: true`, note: no
  open LiDAR here - aerial-photograph ground, FITKIT_GROUND=aerial; the walled town's street grid, the
  Santerno crossing, the Rocca Sforzesca and church footprints carry the fit). `files_artists.jsonl`:
  the row above with the hand-recorded `evidence` (`caption_coords`, `named_place` "Imola",
  `place_qid` Q50195, place = site = the walled centre, dist 0). `classified_artists.jsonl`:
  `p_birdseye: 1.0, by: "hand"` (a bird's-eye view, not a flat plan).
- **Fit note for 212.** The sheet's readable features are the walled town's street grid, the river
  crossing and the church footprints - both-sides-of-the-wall features that do not move. The view is
  from a height with the south up, so a similarity fit (rotation-free, scale+translation about the
  centroid) is the right model; the Rocca Sforzesca at the town's edge is the strongest anchor pair.

## Venice - Jacopo de' Barbari, bird's-eye view, 1500

- **What it is.** Barbari's monumental bird's-eye view of Venice (1500), the whole lagoon city from a
  high vantage point; the Museo Correr holds the sheet. Old enough (a view of the structure) and freely
  machine-readable (public-domain scans on Commons).
- **Where the files live.**
  - **STAGED** - `File:(Venice) View of Venice by Jacopo de' Barbari - Museo Correr.jpg` (11800x5856,
    Public domain, DateTimeOriginal 1500 - the best scan of the sheet).
  - DROP - `File:Jacopo de' Barbari - View of Venice - Google Art Project.jpg` (6727x3222, 1500):
    fails `commons.keep()` (the "google" NO rule), would be re-dropped by `commons.rows()` at 211's
    merge - a dead row.
  - DROP - the NGA "block" files (37052, 37054, ...): **detail crops** of the same woodcut, not separate
    pictures.
- **The site point.** `venice-q641` at Q641's P625 (12.331944, 45.439722) = the enwiki Venice point
  (verified above); kind "town", region "Italy", aerial-photograph ground. The QID is Q641 Venice -
  **not** Q2194 (Windows Media Audio); the "Venice" name-search trap is Q773853 (Los Angeles), which is
  why the evidence is hand-recorded (a live record would store a 9891 km conflict, kind none).
- **Staged rows.** As for Imola: `extras_artists.jsonl` (venice-q641), `files_artists.jsonl`
  (`year: 1500`, `date: "1500 date QS:..."` from the file page's DateTimeOriginal, hand-recorded
  `caption_coords` evidence), `classified_artists.jsonl` (`p_birdseye: 1.0, by: "hand"`).
- **Fit caveat for 212 (R2).** The woodcut spans the whole lagoon city (~8 km) against the 2000 m town
  box, so 212's similarity fit is likely to end as a **review item**, not a fitted plan - staging is
  what this task owes, not a fit. If the overlay looks wrong on a wider box, `specs/site_boxes.json`
  is where the box gets adjusted (211's territory).

## Civitates Orbis Terrarum (1572-1617) and Merian's Topographia (1640s-1680s)

Book-scale sources (hundreds of views each). Status: **pending** - worked through per-book files only
(`data/books/triage/<ia>.*`, `data/books/lists/<ia>.json`) after those exact paths are added to this
task's Touches line; the `books.py:BOOKS` entry is a shared-module change and is filed as its own task.
Internet Archive identifiers are recorded in `fit/src_artists.py:BOOKS` (Civitates: `civitatesorbiste00brau`,
`ARes73114`, `ARes73115`, `17095748888888bsb-00105587`; Merian: `topographiahelve00zeil`,
`rcin.org.pl.WA51_13719_PANB665-r1642_Topographia-Helvetia_152915`). Caveat already known: the book
machinery's triage is plan-centric, while these books are mostly bird's-eye views - so at most a few
hand-verified towns per book, or a documented drop (box 4 is already met by Imola + Venice).

## Offline check

`.venv/bin/python fit/src_artists.py --check` (2026-10-11): no join problems, and

```
PASS caption_coords  imola-q50195|File:Leonardo da Vinci - RCIN 912284, A map of Imola 1502.jpg
PASS caption_coords  venice-q641|File:(Venice) View of Venice by Jacopo de' Barbari - Museo Correr.jpg
evidence: 2 rows, 2 pass, 0 fail, 0 no-tie
```

The join rules it enforces: every staged file row names a staged or existing site, no staged id or QID
pre-exists, every staged site has a picture, (site, title) unique, no clash with the canonical
`files.jsonl`, classified rows 1:1 with the file rows.
