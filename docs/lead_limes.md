# The German Limes - fort plans from the old reports (task 208)

GOAL.md point 4 (the least certain of the seven leads, PLAN.md assumption 7): fort plans from the
German Limes reports. **ORL** = *Der obergermanisch-raetische Limes des Roemerreichs*, the
Reichs-Limes-Kommission's 56-volume series (1894-1937). This document records the verification
sweep of box 1 (which sources exist, are free, are machine-readable, and hold named fort plans),
the plate inventory of the one ORL volume on the Internet Archive, the census of the
de.wikipedia/Commons ORL plate set, and the proceed/drop decision against the box-3 rule:
**proceed iff >= 10 verifiable named fort plans are reachable from >= 2 free machine-readable
sources**. Staging goes to this task's own files only (`data/commons/files_limes.jsonl`,
`data/commons/classified_limes.jsonl`, `data/catalog/extras_limes.jsonl`, via `fit/src_limes.py`);
211 merges. All checks below are dated **2026-10-12**, run from the project VM.

## 1. The verification sweep (checked 2026-10-12)

| # | Source | URL | Dates | Free? | Machine-readable? | Named fort plans? | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | ORL, Lieferung II = Band IV Abt B Nr. 40, *Das Kastell Osterburken* (O. von Sarwey, O. Hettner ed.; Verlag Otto Petters, Heidelberg) | `archive.org/details/derobergermanis00fabrgoog` | 1895 | yes - public domain (Google's PD notice on leaves 1-2; the scan is downloadable: PDF, djvu OCR text+XML, per-page images) | yes - 64-leaf Google scan; PDF and `page/n{N}.jpg` full-res images (5398x7526) work from this VM; djvu XML gives per-leaf OCR | yes - 2 of its 7 plates are plans (Situationskarte, fort plan), both of Osterburken; inventory in section 2 | **SOURCE 1 - stage** |
| 2 | Any other ORL volume on the Internet Archive | archive.org advanced search (2026-10-12: title "obergermanisch" / "obergermanisch-raetische", "Limes der Roemer", (Kastell) AND (Limes), per-fort titles) | - | - | - | **none** - the only hits are source 1 and `limes90deroberge00henr` (a 2009 colour photo book, not a report) | no supply |
| 3 | Limesblatt = *Mitteilungen der Streckenkommissare*, Trier (the RLK's 35 Hefte of excavation reports) | `archive.org/details/limesblatt00unkngoog` (499 p) and `limesblattmitte00germgoog` (506 p, Harvard Pierce bequest) - two scans of the same series | 1892-1903 | yes (Google scans, downloadable) | yes (djvu OCR) | **none** - pure text reports; every one of the 46 "Tafel"/"Karte" OCR hits is a *reference to* another publication, never a plate of the Heft itself | no stageable plans (documented, not a block) |
| 4 | de.wikipedia ORL image set | `de.wikipedia.org/w/api.php?action=query&list=allimages&aiprefix=ORL` (pagination via the `aicontinue` continue key - neither `aifrom` nor `aipfrom` advances; 4 API calls refetch the whole list) | plates from the ORL Lieferungen 1894-1937 | yes - sampled licenses all free (`Bild-PD-alt`, `PD-alt-100`, `Bild-frei` on the sampled files) | yes - 874 files under `upload.wikimedia.org/wikipedia/de/` | yes - 165 files named "Grundriss" across 46 fort numbers, every one with long edge >= 1000 px; census in section 3 | **SOURCE 2 - stage the Commons twins** (R5: the same plates exist on Commons with space naming; the P373 category is the cleaner evidence; the de.wiki twins are noted on the rows) |
| 5 | Commons twins of the ORL plates | `commons.wikimedia.org` search "ORL Grundriss" (2026-10-12): found `File:ORL 12 tab 02 pic 01 Grundriss und Profile.jpg`, `ORL 33 tab 02 pic 01 Grundriss.jpg`, `ORL 01 tab 02 pic 01 Grundriss.jpg`, `ORL 33 tab 03 pic 05 Porta Praetoria Grundriss.jpg`; also a differently-named variant `ORL B 2 3b Taf 1/2/9 Kastell Wiesbaden.jpg` (band/section of that volume not yet resolved) | 1894-1937 | yes (Commons PD, same plates as #4) | yes | presence confirmed by search; **per-file metadata (size, categories, P373) is the gated step** - the paced Commons leg of session 3 verifies >= 10 of them fit-sized and tied to a fort (section 4) | **source 2 leg, gated** |
| 6 | UB Heidelberg Limesblatt digitisation (the complete 35 Hefte) | `limesblatt.uni-hd.de` | 1892-1903 | - | **blocked** - TCP connect fails on both http and https (DNS resolves to 129.206.119.232; two attempts 2026-10-12) | unknown | blocked at check time (recorded; the IA Limesblatt scans in row 3 already showed no plates, so the loss is none) |
| 7 | DNB portal | `portal.dnb.de` (SRU `/sru`, `/opac/sru`, `simpleSearch`) | - | - | **blocked** - behind an Anubis/Techaro JS proof-of-work wall: SRU paths 404, the search page is a honeypot regardless of user agent (machine fact, same class as the hathitrust 403) | unknown | blocked at check time |
| 8 | Deutsche Digitale Bibliothek; UB Heidelberg digital collection | `www.deutschedigitalebibliothek.de`, `digital.ub.uni-heidelberg.de` | - | - | **blocked** - no DNS entry for either host on this VM | unknown | blocked at check time (nothing Limes-specific known to exist there beyond what rows 6-7 would have shown) |
| 9 | RLK's other publications (Berichte de Gruyter/Reimer 1892-1903, Jahresberichte der Dirigenten, Arbeitsplan) and the successor RGK/DAI reports (1937+) | de.wikipedia "Reichs-Limeskommission" (checked 2026-10-12); reprint editions (Codex 1973, Greiner 2005ff.) are NOT public domain | 1892-1937+ | no free machine-readable copies found | - | the RGK reports would carry the LOWER Germanic Limes (out of the RLK's upper/rhaetian scope) - a growth area, not this lead (prep R4) | out of scope, recorded |

The two blocked rows (6-8) are recorded so the sweep is complete; none of them is on the critical
path: rows 1 and 4-5 already reach the box-3 threshold on paper (2 sources, 2 + 165 named plans),
and the blocked hosts only carry *more of the same* (Limesblatt text reports, more ORL volumes).

## 2. The 1895 ORL volume (source 1) - plate inventory (all 7 plates viewed at full resolution, 2026-10-12)

Book: 64 leaves. Title page (leaf 5, read from the djvu OCR): "DER OBERGERMANISCH-RAETISCHE
LIMES DES ROEMERREICHES ... IM AUFTRAGE DER REICHS-LIMESKOMMISSION HERAUSGEGEBEN VON DEM
MILITAEARISCHEN UND DEM ARCHAEOLOGISCHEN DIRIGENTEN ... LIEFERUNG II. ENTHALT: AUS BAND IV,
ABTEILUNG B, Nr. 40 KASTELL OSTERBURKEN. HEIDELBERG VERLAG VON OTTO PETTERS 1895". The monograph
text (Petters) describes the fort from the **Mannheimer Plan** (the 1867 Mannheimer-Verein
excavation, original held in Mannheim) plus the Reichsgrabungen of 19 Aug 1892 - 1894; several
unexcavated parts were "im Wesentlichen nach dem Mannheimer Plan ... erschlossen".

**Correction to the session-1 hand-over:** its leaf-to-Tafel mapping was off by one plate (its
"Taf. II" at leaf 55 is printed **TAFEL III**; its "Taf. III" at leaf 57 is printed **TAFEL IV**)
and both plate scales were misread at 40 dpi (the Situationskarte is 1:5000, not 1:3000; the fort
plan is 1:1000, not ~1:500). The table below was read off the full-resolution page images
(`archive.org/download/derobergermanis00fabrgoog/page/n{N}.jpg`) and the djvu OCR per leaf; the
djvu pages are numbered 1-64 and map to BookReader's 0-based `n` by `n = djvu - 1` (plate leaves
are the odd djvu pages, their versos blank).

| Plate | Leaf (djvu / n) | Content | Scale printed | Stageable? |
|---|---|---|---|---|
| Tafel I | 51 / n50 | 2 photographs of the fort area (a landscape-rotated plate; its two labels name a modern farm and a nearby place, partly legible at this resolution) | - | no (photos) |
| Tafel II | 53 / n52 | excavation photograph (the "Flankenthor des Anbaus, Schwelle von innen gesehen") + "Fig. 2. Mithrasrelief" (a photo of the relief) | - | no (photos) |
| Tafel III | 55 / n54 | **Situationskarte**: "Nr 40. KASTELL OSTERBURKEN", the fort, its Limes road, the railway, the town, field boundaries | MAASSTAB 1:5000 | **yes** - a plan-kind drawing of the fort area (a "Situationskizze") |
| Tafel IV | 57 / n56 | **THE fort plan (Grundriss)**: both fort lines (the large main fort and the smaller Anbau/annex), lettered gates, the Roman road and "Weg nach Adelsh(e)heim / Germersheim / Osterburken", the excavated buildings 1-18, a legend distinguishing Reichsgrabung wall states; "Aufg. von Lehramtspraktikant H. Leutz und Prof. K. Schumacher, gez. von A. Ebertz, Trier" | **MAASSTAB 1:1000** (metre + Roman-foot bar) | **yes** - the anchor plan |
| Tafel V | 59 / n58 | bronze finds (Fig. 11-17 after Prof. Schumacher, Fig. 18-25 v. K. Leutz; medallions, fibulae, inscribed fragments) | 1:1000 / 1:200 | no (finds) |
| Tafel VI | 61 / n60 | iron finds I (fibulae, buckles; "gez. von A. Gasel, in Karlsruh") | natural size | no (finds) |
| Tafel VII | 63 / n62 | iron finds (spearheads and arrowheads; "gez. von A. Gasel, in Karlsruh") | - | no (finds) |

(Leaf 64 is a blank plate verso.) Two of the seven plates are stageable drawings, both of one
fort (Osterburken): the situation map (Tafel III) and the fort plan (Tafel IV). **Staging
caveat:** in the scanned book Tafel IV is a landscape plate rotated 90 degrees (its top edge is
the page's right edge; rotate the page image **clockwise** to get it upright) - the staging step
must record this. The de.wiki twin `ORL_40_tab_04_pic_01_Grundriss.jpg` (3466 px) is probably
upright already; confirm in the Commons leg.

## 3. The de.wikipedia / Commons ORL plate set (source 2) - census (list checked 2026-10-12)

Method: MediaWiki `list=allimages&aiprefix=ORL` on de.wikipedia, 4 paged calls (continue key
`aicontinue`). **874 files** total; **824 plate files** (name contains "tab"); **165 files named
"Grundriss" or "Grundrisse", every one with long edge >= 1000 px**; **55 fort-number tokens**
(42 two-digit main numbers + 11 sub-numbers like `02a`, `05a`, `46b`, `61a/b`, `62a`, `66a/b`,
`71a`, `05.10`; the two one-digit tokens `4` and `7` are stray files of forts 04/07, merged into
those rows in the table). Four files do not carry a fort number at all: two "ORL A Strecke 1 ... KK
Anhausen" plates (a Lage and a Grundriss, 2819x2823 and 3111x3130 px - stageable candidates once
Anhausen's ORL fort number is resolved), one "ORL Strecke 8 Wp 8-28" map fragment (1772x2202 px),
and one unrelated "ORLEN Lietuva" logo (a modern Lithuanian organisation, not an ORL plate).

Naming: `ORL_<nr>_tab_<n>_pic_<m>_<content>.jpg` (Abt B), `ORL_A_<nr>_...` (Abt A),
`ORL<NR>_<name>.jpg` for undated/odd items (e.g. `ORL_49_Wuerzberg_Therme_1800.jpg` - the file
NAME itself records a date: 1800; `ORL_62a_Horreum_Frick_1824.jpg`: 1824). The tab-plate
numbering restarts per volume (each Lieferung is a volume), so the same `tab_02` means different
things in different fort numbers - the fort number in the name is the tie, never the plate
number alone (R6). The Commons twins use spaces: `ORL 12 tab 02 pic 01 Grundriss und Profile.jpg`
etc.

Per-fort census (files = all ORL files of that fort number; grund = named "Grundriss"; max px =
longest edge of any file of the fort; a fort with no "Grundriss" may still hold stageable Lage
or detail drawings - that check happens per candidate in the Commons leg):

| Fort nr | Files | Grundriss | Max px |
|---|---|---|---|
| 01 (Heddesdorf, today Kastellbad) | 78 | 10 | 5608 |
| 01a | 1 | 0 | 1965 |
| 02 | 52 | 7 | 7612 |
| 02a | 8 | 2 | 5466 |
| 03 | 93 | 16 | 18207 |
| 04 (incl. the stray one-digit "4" file) | 38 | 3 | 17535 |
| 05 | 18 | 3 | 16510 |
| 05.10 | 104 | 20 | 9456 |
| 05a | 4 | 2 | 4263 |
| 06 (Holzhausen) | 19 | 0 | 4955 |
| 07 (incl. the stray one-digit "7" file) | 42 | 8 | 12176 |
| 08 | 17 | 2 | 12278 |
| 12 | 9 | 1 | 4100 |
| 14 | 90 | 23 | 17977 |
| 15 | 49 | 22 | 22857 |
| 18 | 15 | 3 | 16138 |
| 19 | 1 | 0 | 1962 |
| 32 | 2 | 0 | 10429 |
| 33 | 48 | 5 | 26160 |
| 34 | 6 | 1 | 19833 |
| 39 | 3 | 1 | 3567 |
| 40 (Osterburken = source 1) | 6 | 1 | 3660 |
| 41 | 6 | 2 | 3832 |
| 42 | 6 | 2 | 2899 |
| 44 | 2 | 1 | 3988 |
| 45 | 7 | 2 | 3750 |
| 46 | 9 | 1 | 5472 |
| 46b | 5 | 1 | 2408 |
| 47 | 8 | 2 | 6285 |
| 48 | 2 | 1 | 1747 |
| 49 | 5 | 1 | 3629 |
| 50 | 5 | 2 | 8887 |
| 51 | 4 | 1 | 2473 |
| 52 | 5 | 1 | 3120 |
| 53 | 9 | 2 | 2868 |
| 54 | 3 | 0 | 3655 |
| 56 | 2 | 1 | 2849 |
| 57 | 3 | 1 | 3744 |
| 58 | 3 | 1 | 3421 |
| 59 | 7 | 1 | 3965 |
| 60 | 5 | 1 | 3602 |
| 61a | 3 | 1 | 3644 |
| 61b | 4 | 1 | 3764 |
| 62a | 2 | 0 | 1250 |
| 63 | 2 | 1 | 3673 |
| 64 | 5 | 1 | 3395 |
| 65 | 2 | 1 | 3556 |
| 66a | 8 | 1 | 3699 |
| 66b | 4 | 1 | 4071 |
| 67 | 4 | 1 | 13000 |
| 69 | 1 | 0 | 726 |
| 71a | 8 | 1 | 11189 |
| 72 | 28 | 1 | 17382 |
| no fort nr (Anhausen x2, Wp 8-28 map fragment) | 3 | 1 | 3130 |

**46 of the 55 fort numbers have at least one "Grundriss" file.** The fort's modern name appears
in only a few file names (01 and 05a "Kastellbad", the 05.10 sub-forts KK Robern/Trienz, 07 KK
Haselburg/Hoenehaus); the fort-number-to-name map (ORL Band I-XVI Abt B = the numbered
Hauptkastelle; the three known examples: 01 = Heddesdorf (today Kastellbad), 06 = Holzhausen,
40 = Osterburken) is built in the staging session from the ORL article's list - never guessed -
together with the QIDs (R3: Saalburg Q542329 and Eining Q1735352 are known to exist; the rest are verified per
fort via pageprops, and forts without a QID stage on name+report coordinates, recorded as such).

Licenses: the sampled de.wiki files (the 2026-10-12 imageinfo extmetadata check) were all free -
`Bild-PD-alt` (e.g. the Bodewig files), `PD-alt-100` (Conrady, Lehner, Dahm files), `Bild-frei`.
Every file staged gets its own license re-checked from the COMMONS twin's metadata (the staged
file), not the de.wiki copy.

## 4. The decision

Rule (box 3): proceed iff >= 10 verifiable named fort plans from >= 2 free machine-readable
sources ("source" = a distinct ORL volume: source 1 is one 1895 volume; source 2's files span
the whole series, so any Commons-verified fort from another Band already is the second volume).

Evidence on 2026-10-12:

- **Source 1 is done and verified**: free, machine-readable, 2 stageable drawings (Tafel III
  1:5000, Tafel IV 1:1000), one fort, one volume (Band IV Abt B, 1895).
- **Source 2 is confirmed to exist and to be free and machine-readable** (824 plates, 165 named
  Grundrisse across 46 fort numbers, all >= 1000 px, free licenses sampled), and 4 of its Commons
  twins were already seen in the Commons search. The only unverified step is that the Commons
  twins carry the metadata (P373 categories, size, date, license) the staging rows need.

**Decision (provisional, 2026-10-12): PROCEED.** It becomes final when the paced Commons leg
verifies >= 10 stageable Commons files (fit-sized, free, each name- or category-tied to its
fort, from >= 2 distinct ORL volumes); if that leg fails, this lead is dropped per the rule and
section 1 already documents every source checked, as box 1 requires of a dropped lead.

Staging plan for the sessions after the Commons leg (module mirrors `fit/src_artists.py`):
a hand-checked FORTS table (fort number, modern name, QID or none, report coordinates, the
volume and its publication year as the row date - plans of structures are 150-year-exempt, the
date is recorded anyway) and a SOURCES table (source 1 = the IA volume; source 2 = the
Commons ORL set); `stage()` writes this task's three staging files idempotently by
(site, title); file rows of the shape of `data/commons/files.jsonl` (site, qid, title, year,
wd_plan, cat, name, by `fit/src_limes.py`, url/thumb (the Commons twin, or the archive.org
`page/n{N}.jpg` for the two 1895-plate rows), w/h, mime, date = the plate/volume date, desc
(naming the fort), license, page); extras rows of the shape of `data/catalog/extras.jsonl`
(id `<slug>-<qid lower>` or slug when no QID, kind "roman fort", region "germany", aerial_ok
true, lon/lat from the report cross-checked against P625 where a QID exists); classified rows
`p_plan 1.0, by hand`. Evidence per `fit/evidence.py` (filled last, per the 200 contract):
Commons plates in the fort's P373 category -> kind `category` (site_cat/file_cat/via chain);
the 1895-plate rows and any Commons plate without a usable P373 tie -> kind `caption_coords`
(named_place the fort name as printed on the plate - "NR 40. KASTELL OSTERBURKEN" - place QID
and coordinates of the fort or its town, site coordinates, dist_m; check requires the named place
within 50 km, `DIST_TOL_M`). `check_staged()` = the offline join + `evidence.check(FILES_LIMES,
NO_BOOKS, catalog=EXTRAS_LIMES)` with NO_BOOKS = `data/books/.no-books` (never created, so the
book leg is skipped) - the OQ-1 resolution, same as 204/205/213. The test
(`tests/test_src_limes.py`, no network: a socket-blocking fixture) joins the staged files,
runs the check, runs a built-in negative control (a caption naming the wrong fort / 10 km off)
and compares a golden sample; box 3's count (>= 10 plans, >= 2 volumes) is asserted from the
staged rows themselves.
