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

Book-scale sources (hundreds of bird's-eye town views each). Both **exist and are freely
machine-readable** - all six Internet Archive copies are BookReader streams (jp2 + PDF + hocr OCR,
not restricted; metadata cached 2026-10-11 in `data/raw/books/<ia>/`). The **cite string** column is
what 216 puts into `books.py:BOOKS` (take it verbatim). The book-level `region` is 216's call:
the town's region comes from the row, not the book, so 216 picks the dominant one for the volume and
says so in the cite string (for the untriaged books, from the triaged town names).

| IA id | book | drawing date | cite string (for 216) |
|---|---|---|---|
| `civitatesorbiste00brau` | Civitates Orbis Terrarum, **Liber secundus** (292 leaves) | 1575 (the volume) | Georg Braun and Frans Hogenberg, *Civitates Orbis Terrarum*, Liber secundus, Antwerp 1575 (Aegidius Rade) - towns of western Europe and the Mediterranean |
| `ARes73114` | Civitates Orbis Terrarum, Tomus quartus | 1586 | Georg Braun and Frans Hogenberg, *Civitates Orbis Terrarum*, Tomus quartus, 1586 |
| `ARes73115` | Civitates Orbis Terrarum, Liber quintus | 1597 | Georg Braun and Frans Hogenberg, *Civitates Orbis Terrarum*, Liber quintus, 1597 |
| `17095748888888bsb-00105587` | Civitates Orbis Terrarum, Liber primus (BSB scan) | 1600 | Georg Braun and Frans Hogenberg, *Civitates Orbis Terrarum*, Liber primus, 1600 (BSB scan) |
| `topographiahelve00zeil` | Merian, Topographia Helvetiae, Rhaetiae et Valesiae (Zeiller) | 1654 | Matthaeus Merian and Martin Zeiller, *Topographia Helvetiae, Rhaetiae et Valesiae*, Frankfurt 1654 (Merianischen Erben) - the Swiss cantons |
| `rcin.org.pl.WA51_13719_PANB665-r1642_Topographia-Helvetia_152915` | Topographia Helvetiae (PAN Poland) | 1642 | Matthaeus Merian, *Topographia Helvetiae, Rhaetiae et Valesiae*, 1642 (PAN Poland) - the Swiss cantons |

**What `civitatesorbiste00brau` is** (verified from the item's own OCR, 2026-10-11): Braun & Hogenberg's
*Civitates Orbis Terrarum*, **Liber secundus (1575)** - the volume opens with the Imperial Privilege
(`PRIVILEGIUM CAESAREAE MAJESTATIS`) granted to Hogenberg, vanden Noeurt and Braun, then town after town:
a large engraved **bird's-eye view** (the town named in a Latin inscription over/under the plate: VIENNA,
MEDIOLANVM, VENETIA, FLORENTIA, ROMA, ISTANBOLIS, ...) plus the town's history text. Liber secundus covers
the towns of western Europe and the Mediterranean: Lisbon, Seville, London, Toledo, Granada, Malaga,
Barcelona, Paris, Aachen, Antwerp, Bruges, Ghent, Amsterdam, Hamburg, Nuremberg, Strasbourg, Ratisbon,
Vienna, Milan, Venice, Innsbruck, Florence, Rome, Parma, Messina, Malta, Constantinople, Jerusalem
(the last also as a plan, "Nova urbis Hierosolymitanae descriptio") and East-African ports. Every view
is old enough (a view of the structure, exempt from the 150-year rule) and freely machine-readable
(public-domain scans, BookReader images).

**Triage (committed, zero error rows).** `data/books/triage/civitatesorbiste00brau.A.jsonl` types all
292 leaves: 171 `text_only`, 118 `other_illustration`, 3 `plate_site_plan` (A187/A199 = the blank
fold-out versos, A238 = the Jerusalem-new plan). `.F.jsonl` is the per-figure pass over the 118
illustration leaves: 239 figure readings, 222 view / 11 plan / 6 other. **The figure leaves are 121**
(118 other_illustration + 3 plate_site_plan) and the hand list below covers exactly those.

**Section structure.** Each city is a section: a **title leaf** (big Latin title + history text; A
reads the city name) -> **1-3 plate leaves** (A's `caption` = the plate's own printed inscription - a
legend, a poem, or empty) -> sometimes more history. The order is strictly title-then-plates (an
earlier "sections interleave both ways" note was a misread of faded versos). Verso leaves type
inconsistently in A: `text_only` (A51, A111, A207, A227) and `plate_site_plan` (A187, A199) - all six
faded blank fold-out versos. Three fold-outs: **Augsburg** (A186 recto view / A187 blank verso),
**Milan** (A198 recto view / A199 blank verso) and **Venice** (A201/A202 = a real view on BOTH sides -
the famous bird's-eye view is the recto A201, caption "VENETIA"; the verso A202 is a second view
continuing the legend at item 53, not a blank).

**Pitfalls for 216/217 (each cost a session of re-reads - do not repeat):**
- **The hOCR page index is MISALIGNED** with the jp2 leaf sequence by a drifting 0-2 leaves (e.g. hOCR
  leaf 85 holds the Brussels title text that A reads on leaf 87). `books_ia.page_texts()`/`djvu_txt()`
  are **unreliable for this book**; the image-based A rows are the ground truth. 217 must not use
  page_texts for civitates.
- **The machines under-detect plans in BOTH directions.** A typed only 3 of the 121 figure leaves as
  `plate_site_plan`, and F's "plan" flag is unreliable too: F flags 11 of the 121 figure pages as
  containing a plan, and of F's ten distinct plan leaves (A30, 62, 65, 66, 90, 93, 105, 186, 229x2,
  237) only A90 (Ghent) and A237 (Jerusalem old) are true plans - F misses the five famous plans
  A58/85/98/109/238 and flags A186 (a view). The hand list's kind "s" (the seven verified plans)
  is the only source for plan calls on this book.

**Corrections of the machine readings** (all read by eye on the local triage images,
`data/raw/books/civitatesorbiste00brau/triage/nNNNN.jpg` = leaf n+1 = A row NNNN):
- A157/A158 "DECEM ET TRIA LOCA" / "FEDERATORVM HELVETIAE" = sheets of small town **views** of the 13
  Swiss cantons - kind o, **not maps**.
- The seven true plans: A58 (Paris), A85 (Brussels), A90 (Ghent), A98 (Antwerp), A109 (Amsterdam),
  A237 (Jerusalem old city), A238 (Jerusalem new city).
- A187/A199 = blank fold-out versos (kind u, carry no picture); A197 = the Milan arms page (kind u,
  an image but neither view nor plan).
- Two garbled A captions corrected against the plate images: fig 50 "Cum Pristelio" ->
  "Cum Privilegio" (the Barcelona banner) and fig 198 "METOLACOL" -> "MEDIOLANVM" (the Milan
  fold-out cartouche).

**The hand list (the single source of truth for 216/217).** `data/books/lists/civitatesorbiste00brau.json`
= `{"plates": null, "figures": [...]}` - the book has no printed town list, so one entry per figure
leaf: `fig` = 0-based leaf n; `title` = the plate's printed inscription (A's caption, corrected where
the image showed a garble) or the section's city name where the plate has no inscription (14 such
leaves: 53 Burgos + S. Sebastian, 58 Lutetia Parisiorum, 85 Bruxella, 90 Gandanum, 98 Anverpia, 109
Amsteladum, 187 Augusta verso, 194 Vienna, 199 Mediolanum verso, 202 Venetia verso, 214 Ancona, 217/218
Neapolis, 225 Messina); the five double-plate leaves (50, 54, 193, 205, 206) carry the second plate's
inscription in a `[other plate: ...]` bracket; `page` = the printed number only for fig 193 ("2") and
194 ("3") - the only printed page numbers in the whole book are on leaves 193-196 (1-4) and 280-284
(I-V), and no figure leaf falls in 280-284; `kind` = o view / s plan / u other; `kind_by` = `hand`
(read the leaf image) or `A` (derived from stage A's typing, unverified). Tally: **121 entries =
s 7 / u 3 / o 111; kind_by hand 30 / A 91**. `data/books/lists/civitatesorbiste00brau.map.json` = `[]`
- honestly empty: `books_lists.list_pages` maps kind s/u entries BY PRINTED PAGE NUMBER and no figure
leaf of this book carries one; extending the machinery for page-less figures is 217, not 213.

**Per-book status (all six items):**
- **`civitatesorbiste00brau` (1575, Liber secundus) = fully worked.** Triage A 292/292 + F 118/118
  committed; the hand list (121 entries) + the map `[]` written; the seven hand-verified towns
  (Rome, Vienna, Florence, Milan, Venice, Brussels, Antwerp) are what 213's hand-checked QID table
  in `fit/src_artists.py` covers.
- **The other five** (`ARes73114`, `ARes73115`, `17095748888888bsb-00105587`, `topographiahelve00zeil`,
  `rcin.org.pl.WA51_13719_PANB665-r1642_Topographia-Helvetia_152915`) = verified present on IA as
  BookReader streams (table above; metadata cached, unrestricted) but **not triaged yet** - the
  follow-on scope of 216/217 (fetch -> triageA/F -> hand list, the same flow as Liber secundus). The
  Merian volumes are the same bird's-eye-view genre, so both pitfalls above apply to them as well.

**Status: worked in per-book files, not staged as rows.** **No picture rows are staged by this task**
(there are no per-file Commons rows to stage; the book flow goes through 211's index rebuild). Why the
rows cannot come out of the machinery yet: its list taxonomy classifies views as kind "o" ("other: views,
sections alone, ...") and `books_lists.cmd_index` emits an index row only for kind "s" (site plan) - so a
book of views triages cleanly but indexes to nothing. Extending the machinery (BOOKS entries, the view
lists, the view-as-drawing index, plus the stale LLM tunnel ports that currently block every book task's
triage stages) is shared-module work, filed as tasks **215** (books.py ports), **216** (books.py BOOKS
entries for the six items above) and **217** (books_lists.py lists + taxonomy), in the order 215 -> 216
-> 217 with 216 depending on this task's verified facts.

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
