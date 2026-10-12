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
211 merges them into the canonical files. All checks below are dated **2026-10-12**, run from the
project VM.

**Decision final (2026-10-12): PROCEED.** 56 named fort plans from 43 ORL fort numbers
(45 staging items: 43 numbered forts + the Kleinkastell Anhausen of Strecke 1) were staged from
**3 free machine-readable collections** - the 1895 Internet Archive volume (2 plans), the
de.wikipedia ORL image set (45 plans) and the Commons ORL set (9 plans) - spanning **9 distinct
ORL volumes**. Box 3 (>= 10 plans from >= 2 free machine-readable sources) passes under any
reading of "source" (3 collections / 9 volumes / 43 forts).

## 1. The verification sweep (checked 2026-10-12)

| # | Source | URL | Dates | Free? | Machine-readable? | Named fort plans? | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | ORL, Lieferung II = Band IV Abt B Nr. 40, *Das Kastell Osterburken* (O. von Sarwey, O. Hettner ed.; Verlag Otto Petters, Heidelberg) | `archive.org/details/derobergermanis00fabrgoog` | 1895 | yes - public domain (Google's PD notice on leaves 1-2; the scan is downloadable: PDF, djvu OCR text+XML, per-page images) | yes - 64-leaf Google scan; PDF and `page/n{N}.jpg` full-res images (5398x7526) work from this VM; djvu XML gives per-leaf OCR | yes - 2 of its 7 plates are plans (Situationskarte, fort plan), both of Osterburken; inventory in section 2 | **SOURCE 1 - stage** |
| 2 | Any other ORL volume on the Internet Archive | archive.org advanced search (2026-10-12: title "obergermanisch" / "obergermanisch-raetische", "Limes der Roemer", (Kastell) AND (Limes), per-fort titles) | - | - | - | **none** - the only hits are source 1 and `limes90deroberge00henr` (a 2009 colour photo book, not a report) | no supply |
| 3 | Limesblatt = *Mitteilungen der Streckenkommissare*, Trier (the RLK's 35 Hefte of excavation reports) | `archive.org/details/limesblatt00unkngoog` (499 p) and `limesblattmitte00germgoog` (506 p, Harvard Pierce bequest) - two scans of the same series | 1892-1903 | yes (Google scans, downloadable) | yes (djvu OCR) | **none** - pure text reports; every one of the 46 "Tafel"/"Karte" OCR hits is a *reference to* another publication, never a plate of the Heft itself | no stageable plans (documented, not a block) |
| 4 | de.wikipedia ORL image set | `de.wikipedia.org/w/api.php?action=query&list=allimages&aiprefix=ORL` (pagination via the `aicontinue` continue key - neither `aifrom` nor `aipfrom` advances; 4 API calls refetch the whole list) | plates from the ORL Lieferungen 1894-1937 | yes - all 45 staged picks verified via their own fileinfo (`Bild-PD-alt`, `PD-alt-100`; section 3) | yes - 874 files under `upload.wikimedia.org/wikipedia/de/` | yes - 167 files named "Grundriss" (57 Abt B / 110 Abt A), every one with long edge >= 1000 px (min 1538); 837 of the 874 are plate files; census in section 3 | **SOURCE 2 - stage the de.wiki files** (45 of 874; every staged desc names the fort; the Commons set turned out DISJOINT, section 3) |
| 5 | The Commons ORL set - a DISJOINT collection (not the de.wiki twins) | Commons search "ORL" / `aiprefix=ORL` (2026-10-12): one page = 262 files, of which 103 are ORL-ish (the rest ORLANDO/ORLA/ORLEY/ORLEN/Disney/Hall noise) | plates 1894-1937 + modern photos | yes - all 9 staged picks "Public domain" (fileinfo re-verified 2026-10-12) | yes | **zero name overlap with the 874 de.wiki names, both directions (the session-2 twins assumption is FALSE)**; 9 stageable plans (01x2, 12, 33x5, 31x2), each description naming its fort; per-file metadata in section 3 | **SOURCE 3 - stage the 9** |
| 6 | UB Heidelberg Limesblatt digitisation (the complete 35 Hefte) | `limesblatt.uni-hd.de` | 1892-1903 | - | **blocked** - TCP connect fails on both http and https (DNS resolves to 129.206.119.232; two attempts 2026-10-12) | unknown | blocked at check time (recorded; the IA Limesblatt scans in row 3 already showed no plates, so the loss is none) |
| 7 | DNB portal | `portal.dnb.de` (SRU `/sru`, `/opac/sru`, `simpleSearch`) | - | - | **blocked** - behind an Anubis/Techaro JS proof-of-work wall: SRU paths 404, the search page is a honeypot regardless of user agent (machine fact, same class as the hathitrust 403) | unknown | blocked at check time |
| 8 | Deutsche Digitale Bibliothek; UB Heidelberg digital collection | `www.deutschedigitalebibliothek.de`, `digital.ub.uni-heidelberg.de` | - | - | **blocked** - no DNS entry for either host on this VM | unknown | blocked at check time (nothing Limes-specific known to exist there beyond what rows 6-7 would have shown) |
| 9 | RLK's other publications (Berichte de Gruyter/Reimer 1892-1903, Jahresberichte der Dirigenten, Arbeitsplan) and the successor RGK/DAI reports (1937+) | de.wikipedia "Reichs-Limeskommission" (checked 2026-10-12); reprint editions (Codex 1973, Greiner 2005ff.) are NOT public domain | 1892-1937+ | no free machine-readable copies found | - | the RGK reports would carry the LOWER Germanic Limes (out of the RLK's upper/rhaetian scope) - a growth area, not this lead (prep R4) | out of scope, recorded |

The blocked rows (6-8) are recorded so the sweep is complete; none is on the critical path: rows 1,
4 and 5 together give 3 free machine-readable sources - 2 + 45 + 9 = 56 named plans - and the
blocked hosts only carry *more of the same* (Limesblatt text reports, more ORL volumes). Box 3
(>= 10 verifiable named fort plans from >= 2 free machine-readable sources) passes under any
reading of "source" (3 collections / 9 ORL volumes / 43 fort numbers).

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
caveat (recorded on the staged row):** in the scanned book Tafel IV is a landscape plate rotated
90 degrees (its top edge is the page's right edge; rotate the page image **clockwise** to get it
upright). The de.wiki twin `ORL_40_tab_04_pic_01_Grundriss.jpg` (3466x2838) is verified upright in
its own fileinfo and is staged as its own row (source 2): the same plate on a different host -
different URL, name and collection tie, so it is not a double count.

## 3. The de.wikipedia / Commons ORL plate set (sources 2 and 3) - census (lists checked 2026-10-12)

Method: MediaWiki `list=allimages&aiprefix=ORL` on de.wikipedia, 4 paged calls (continue key
`aicontinue`). **874 files** total; **837 plate files** (name contains "tab" case-INsensitively -
13 use a capital "Tab": 8x `ORL_66a`, 4x `ORL_66b`, 1x `ORL_A_03`; the case-sensitive count is
824); **167 files named "Grundriss"** (110 Abt A + 57 Abt B), **every one with long edge >=
1000 px (min 1538)**.

Classification (authoritative rule, re-verified 2026-10-12): the name is decoded (%2C -> ",",
%20 -> " "), spaces -> "_", lowercased; `orl_a_...` -> **Abt A** (token = 3rd field),
`orl_...` -> **Abt B** (token = 2nd field), else unnumbered. The earlier per-fort table of this
document merged Abt A SECTION files (`ORL_A_<n>_...` = the Limes stretches themselves) with Abt B
FORT files (`ORL_<n>_...`) and counted 3 compact-named modern photos under fort numbers 52/53;
the corrected split follows. No staged pick is affected (43 pure `ORL_<nr>_tab...` names + the
2 `ORL_A_Strecke_1` Anhausen files).

Naming: `ORL_<nr>_tab_<n>_pic_<m>_<content>.jpg` (Abt B), `ORL_A_<nr>_...` (Abt A),
`ORL<NR>_<name>.jpg` for undated/odd items (e.g. `ORL_49_Wuerzberg_Therme_1800.jpg` - the file
NAME itself records a date: 1800; `ORL_62a_Horreum_Frick_1824.jpg`: 1824). The tab-plate
numbering restarts per volume (each Lieferung is a volume), so the same `tab_02` means different
things in different fort numbers - the fort number in the name is the tie, never the plate
number alone (R6).

**Abt B (the numbered forts): 305 files across 49 number tokens, 57 named "Grundriss"**
(files / Grundriss / max px of the token; one-digit tokens 4 and 7 are stray files of forts 04
and 07; 54-55 = the one Wimpfen monograph covering both forts):

| ORL nr (Abt B) | Files | Grundriss | Max px |
|---|---|---|---|
| 4 | 1 | 0 | 2843 |
| 01 | 6 | 1 | 4472 |
| 01a | 1 | 0 | 1965 |
| 02a | 8 | 2 | 5466 |
| 03 | 6 | 1 | 3965 |
| 04 | 2 | 0 | 3804 |
| 05 | 2 | 1 | 4269 |
| 05a | 4 | 2 | 4263 |
| 06 | 18 | 2 | 4955 |
| 07 | 3 | 1 | 6030 |
| 08 | 4 | 1 | 12278 |
| 12 | 8 | 1 | 4100 |
| 18 | 15 | 3 | 16138 |
| 32 | 2 | 0 | 10429 |
| 33 | 48 | 5 | 26160 |
| 34 | 6 | 1 | 19833 |
| 39 | 3 | 1 | 3567 |
| 40 | 6 | 1 | 3660 |
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
| 52 | 4 | 1 | 3120 |
| 53 | 5 | 2 | 2868 |
| 54-55 | 3 | 0 | 3655 |
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

**Abt A (the Limes stretches): 561 files, 110 named "Grundriss"** (files / Grundriss / max px):

| Strecke (Abt A) | Files | Grundriss | Max px |
|---|---|---|---|
| 01 | 72 | 9 | 5608 |
| 02 | 51 | 7 | 7612 |
| 02.2 | 1 | 0 | 3363 |
| 03 | 87 | 15 | 18207 |
| 04 | 35 | 3 | 17535 |
| 05 | 16 | 2 | 16510 |
| 05.10 | 104 | 20 | 9456 |
| 06 | 1 | 0 | 4645 |
| 07 | 38 | 7 | 12176 |
| 7-9 | 1 | 0 | 781 |
| 08 | 13 | 1 | 10025 |
| 12 | 1 | 0 | 2410 |
| 14 | 90 | 23 | 17977 |
| 15 | 49 | 22 | 22857 |
| strecke | 2 | 1 | 3130 |

Abt A notes: 05.10 is the Wetterau section (article line 24: Abt A Band 2 = Strecken 3-5, incl.
"Die Wetteraulinie"); **14 and 15 are pure Abt A (Strecken 14/15 = the Rhaetian Limes) - the
874-file set holds ZERO Abt B files for 14 (Butzbach) and 15 (Grüningen)**, which is the drop
reason for those two forts; Abt A and Abt B numbers 01-08 overlap (e.g. token 01 = 72 A + 6 B
files; the staged file is the B one); token `strecke` = the two staged Anhausen files
(`ORL_A_Strecke_1_tab_12_pic_01/02_...`) - a third Anhausen file,
`ORL_A_01_tab_12_pic_01(a-c)_KK_Anhausen_Zusammenhang.jpg` (a context drawing), counts in token
01 and is not staged.

**8 unnumbered files** (none an ORL plate, none staged): the `ORL,_Strecke_8,_Wp_8-28.jpg` map
fragment; 6 modern photos (`ORL19_Ober-Florstadt`, `ORL52_Infotafel`,
`ORL53_Infotafel_Kastelle/_Numeruskastell/_Therme`, `ORL53_Lageplan`); and the
`ORLEN_Lietuva_Logo.svg` (a Lithuanian fuel company - modern-organisation noise, like the
ORLANDO/ORLA files on Commons). Note there are no `ORL_19` files at all (only the modern
photo) - the drop reason for Ober-Florstadt.

**42 of the 49 Abt B fort numbers hold a "Grundriss" file** (none: 4, 01a, 04, 32, 54-55, 62a,
69; token 19 is absent entirely); 167 Grundriss-named files = 110 Abt A + 57 Abt B, every one
with long edge >= 1000 px (min 1538).

The fort-number-to-name map is the ORL article's Abteilung B list (verified 2026-10-12 against
the article wikitext and stored in `fit/src_limes.py`'s FORTS table) plus the Abteilung A line
23 (Abt A Band 1 = Strecke 1, 1915 = Anhausen) - never guessed. **41 of the 43 staged ORL
numbers have a QID** (Wikidata); **64 (Kastell Schirenhof) and 67 (Kastell Buch) have no QID**
and stage on name+coordinates per the task Notes, recorded as such on the row (the place tie is
name+coords, not a QID).

Licenses (each staged file re-verified from its own fileinfo, 2026-10-12): all 45 de.wiki picks
free - `Bild-PD-alt` on 01, 05, 05a, 12, 64; `PD-alt-100` on the rest. All 9 Commons files
"Public domain". The 2 IA rows come from the public-domain Google scan.

### The Commons ORL set (source 3) - 262 files, 9 staged

The Commons `aiprefix=ORL` page (2026-10-12) returned **262 files**; **103 are ORL-ish** (the
other 159 are ORLANDO/ORLA/ORLEY/ORLEN/Disney/Hall/Orlando-Magic noise). **Zero name overlap
with the 874 de.wiki names, both directions** (names normalized: decode, spaces<->underscores,
lower) - the session-2 assumption that the Commons files are the de.wiki twins is FALSE: they
are distinct uploads of the same ORL plates. 9 are stageable plans, each with a description
naming its fort; all metadata below was verified against the Commons file pages:

| File (Commons) | Fort | w x h | Commons description (verbatim) | Commons date |
|---|---|---|---|---|
| ORL 01 tab 01 pic 01 Lageplan.jpg | 01 Heddesdorf | 2961x4223 | Lageplan des Kastells Heddesdorf, ORL 1 | August 1903 (Publikation) |
| ORL 01 tab 02 pic 01 Grundriss.jpg | 01 Heddesdorf | 4435x3197 | Grundriss des Kastells und des Kastellbades von Heddesdorf, ORL 1 | August 1903 (Publikation) |
| ORL 12 tab 02 pic 01 Grundriss und Profile.jpg | 12 Kapersburg | 2799x2824 | Grundriss und Geländeprofile des Kastells Kapersburg, ORL 12 | "Zwischen 1896-1905 (Ausgrabungen) und Ju..." (truncated in the metadata) |
| ORL 33 tab 02 pic 01 Grundriss.jpg | 33 Stockstadt | 8070x11328 | Fort Stockstadt layout | "I don't know." |
| ORL 33 tab 03 pic 05 Porta Praetoria Grundriss.jpg | 33 Stockstadt | 6816x3024 | Layout of the porta praetoria of Fort Stockstadt. | "Unknown." |
| ORL 33 tab 04 pic 01-09 Thermen.jpg | 33 Stockstadt | 8680x12600 | Layout of the baths at Stockstadt Roman Fort. | "Unknown" |
| ORL 33 tab 05 pic 01 Mithraeum und Dolichenum Lage.jpg | 33 Stockstadt | 15023x4840 | Plan of the Mithraeum and Dolichenum at Stockstadt Roman Fort | "Unknown" |
| ORL B 2 3b Taf 1 Kastell Wiesbaden.jpg | 31 Wiesbaden | 2292x3288 | Plan of Wiesbaden in Roman Times. | 1909 |
| ORL B 2 3b Taf 2 Kastell Wiesbaden.jpg | 31 Wiesbaden | 2328x3276 | Plan of Roman castle in Wiesbaden. | 1909 |

Date handling: the Commons dates of the 33 and 12 files are junk or truncated ("I don't know.",
"Unknown.", "Zwischen 1896-1905 ... und Ju..."), so the staged rows carry the **monograph year
from the band table** as `date`/`year` (the 150-year rule: fort plans of structures are exempt,
recorded anyway) and the meaningful Commons dates ("August 1903 (Publikation)", "1909") as
`date_commons`. `B 2 3b` is the plate-header band coding (Abt B, Band 2, plate 3b): fort 31
(Wiesbaden) is Band 2b in the band table (1909), and both the name and the description of the
two files say "Kastell Wiesbaden" - that is the tie.

**Dropped (the remaining 94 of the 103, exactly):** 4 Abt A section plates (A 01 tab 09
Limesprofil bei Rheinbrohl 3558x2594; A 04 tab 7 pic 10 Wp 4/48 3344x1824; A 04 tab 10 pic 3 KK
Feldheimer Wald 672x740; A 05 tab 14 pic 06 KK Langendiebach 2108x1192); 5 genuine non-plan
plates (33 tab 03 pic 03+04 Grabenprofile 7645x6669; 33 tab 06 Anlegestelle 5940x8313, a 2009
photo; 33 tab 16 Steindenkmäler 8319x12078; 56 tab 03 Metallfunde 1531x2170; B 2 3b Taf 9 Nr 1 =
a photo of a military diploma, 2214x2178); 1 derivative (B 2 3b Taf 1 "Verlauf Heidenmauer"
1250x918 = a crop of the staged Taf 1); 3 Tabula Peutingeriana fragments (ORL 61/66a/67b,
934-1235 px, too small); 1 modern logo (ORL Logo ZhWN.png, 100x100, CC BY 2.5 - the description
is the Orlando Magic basketball logo, not ORL); 80 modern photos (the 30-file ORL 40
"Annexkastell"/Infopavillon/Limeskongress-2012 set = the ANNEX fort of Osterburken; 10 ORL 49
Würzberg; 8 ORL 23; 4 ORL 21; 4 ORL 32; 3 ORL 20; 3 ORL 22; 6 ORL 53; 2 ORL 11 (Saalburg);
2 ORL 52; one each ORL 14 Butzbach, ORL 18 Echzell, ORL 33, ORL 34; ORL A Kleinkastell
Hunnenkirchhof 1446x1371 - below the 1538 px floor and a fortlet = growth area anyway; one
Flickr photo (ORL 210112); two ORL T(p&q) pngs). Growth area, not a block.

**The P373 route is dead (final):** among the 103 ORL-ish Commons files there are exactly 2
direct P373 category memberships, and both are non-plans: "ORL53 Kastell Neckarburken 1.jpg" (a
MODERN photo, category "Kastell Neckarburken", Q1343017) and "ORL 56 tab 03 pic 02-15
Metallfunde.jpg" (a FINDS plate, category "Kastell Heilbronn-Böckingen", Q1735374). Neither is
staged, so **all 56 staged rows use the evidence kind `caption_coords`** - no category chain
exists for any staged file.

## 4. The decision - FINAL PROCEED (2026-10-12)

**Rule (box 3):** proceed iff >= 10 verifiable named fort plans are reachable from >= 2 free
machine-readable sources. **Evidence:** 56 named plans from 43 ORL fort numbers (45 staging
items) from 3 free machine-readable collections (the 1895 IA volume; the de.wiki ORL set; the
Commons ORL set) spanning 9 distinct ORL volumes - box 3 passes under any reading of "source"
(3 collections / 9 volumes / 43 forts). Every staged row carries the 200 evidence: the
report's list/caption names the fort (the `desc` field), and the coordinates are cross-checked
against the QID's P625 where a QID exists.

**(b) The 9-volume spread** (row date = the monograph year; the 150-year rule: fort plans of
structures are exempt, recorded anyway):

| Volume (ORL band) | Forts staged (monograph year) |
|---|---|
| Abt B, Band 1 | 01 (1903), 02a (1900), 03 (1900), 05 (1897), 05a (1903), 07 (1901) |
| Abt B, Band 2a | 08 (1909), 12 (1906), 18 (1903) |
| Abt B, Band 2b | 31 (1909) |
| Abt B, Band 3 | 33 (1914), 34 (1896) |
| Abt B, Band 4 | 39 (1904), 40 (1895), 41 (1909), 42w (1897), 42o (1897), 44 (1894), 45 (1904), 45a (1904) |
| Abt B, Band 5 | 46 (1904), 46b (1914), 47 (1897), 48 (1896), 49 (1896), 50 (1896), 51 (1900), 52 (1897), 53 (1898), 56 (1898), 57 (1897), 58 (1902), 59 (1907), 60 (1907), 61a (1897), 61b (1897) |
| Abt B, Band 6 | 63 (1897), 64 (1897), 65 (1894), 66a (1904), 66b (1900), 67 (1896) |
| Abt B, Band 7 | 71a (1905), 72 (1906) |
| Abt A, Band 1 (Strecke 1) | Anhausen (1915) |

**(c) Evidence:** `caption_coords` for EVERY row (the P373 route is dead, section 3):
`named_place` = the fort name as printed in the plate/description ("Osterburken",
"Heddesdorf", "Öhringen", "Stockstadt", "Wiesbaden", "Kastell Schirenhof", "Kastell Buch",
...); `place` = QID + the item's raw first P625 value, or name+coordinates for 64/67 (recorded
on the row as such); the site point is the same point, so `dist_m` = 0.0; `check_caption`
reproduces `hav_m` offline, and the <= 50 km tolerance (`DIST_TOL_M`) is trivially met.

**(d) The FORTS table** (45 staging items; lon/lat = the raw first P625 value, shown rounded,
or the report coordinates for 64/67; the module stores the raw values):

| ORL nr | Fort | QID | lon, lat | Volume (year) | Staged files |
|---|---|---|---|---|---|
| 01 | Heddesdorf | Q1735373 | 7.46931, 50.4365 | Abt B, Band 1 (1903) | dewiki-orl 1, commons-orl 2 |
| 02a | Niederberg | Q1670400 | 7.62734, 50.3689 | Abt B, Band 1 (1900) | dewiki-orl 1 |
| 03 | Arzbach | Q1735331 | 7.74565, 50.3753 | Abt B, Band 1 (1900) | dewiki-orl 1 |
| 05 | Hunzel | Q1240802 | 7.82785, 50.2467 | Abt B, Band 1 (1897) | dewiki-orl 1 |
| 05a | Marienfels | Q1359182 | 7.81076, 50.2403 | Abt B, Band 1 (1903) | dewiki-orl 1 |
| 07 | Kemel | Q1725806 | 8.01606, 50.1655 | Abt B, Band 1 (1901) | dewiki-orl 1 |
| 08 | Zugmantel | Q1727277 | 8.20364, 50.18977 | Abt B, Band 2a (1909) | dewiki-orl 1 |
| 12 | Kapersburg | Q1735382 | 8.63650, 50.31271 | Abt B, Band 2a (1906) | dewiki-orl 1, commons-orl 1 |
| 18 | Echzell | Q1657587 | 8.88322, 50.393 | Abt B, Band 2a (1903) | dewiki-orl 1 |
| 31 | Wiesbaden | Q622981 | 8.241862, 50.086375 | Abt B, Band 2b (1909) | commons-orl 2 |
| 33 | Stockstadt | Q1735421 | 9.06737, 49.9774 | Abt B, Band 3 (1914) | dewiki-orl 1, commons-orl 4 |
| 34 | Niedernberg | Q1735399 | 9.14105, 49.9141 | Abt B, Band 3 (1896) | dewiki-orl 1 |
| 39 | Walldürn (Alteburg) | Q1735436 | 9.38674, 49.5785 | Abt B, Band 4 (1904) | dewiki-orl 1 |
| 40 | Osterburken | Q1243550 | 9.42364, 49.42753 | Abt B, Band 4 (1895) | ia-1895 2 (n54/n56; n56 rotated 90° CW), dewiki-orl 1 |
| 41 | Jagsthausen | Q1735380 | 9.46917, 49.3109 | Abt B, Band 4 (1909) | dewiki-orl 1 |
| 42w | Bürgkastell Öhringen | Q86069877 | 9.497397, 49.205444 | Abt B, Band 4 (1897) | dewiki-orl 1 |
| 42o | Rendelkastell Öhringen | Q91949042 | 9.513369, 49.199514 | Abt B, Band 4 (1897) | dewiki-orl 1 |
| 44 | Murrhardt | Q1735397 | 9.5823, 48.97696 | Abt B, Band 4 (1894) | dewiki-orl 1 |
| 45 | Welzheim-West | Q32064057 | 9.63234, 48.87218 | Abt B, Band 4 (1904) | dewiki-orl 1 |
| 45a | Welzheim-Ost | Q1735441 | 9.64224, 48.87122 | Abt B, Band 4 (1904) | dewiki-orl 1 |
| 46 | Lützelbach | Q1735392 | 9.088611, 49.779444 | Abt B, Band 5 (1904) | dewiki-orl 1 |
| 46b | Seckmauern | Q1735419 | 9.117361, 49.799028 | Abt B, Band 5 (1914) | dewiki-orl 1 |
| 47 | Hainhaus | Q1735367 | 9.08319, 49.7328 | Abt B, Band 5 (1897) | dewiki-orl 1 |
| 48 | Eulbach | Q1735359 | 9.077917, 49.68 | Abt B, Band 5 (1896) | dewiki-orl 1 |
| 49 | Würzberg | Q1445553 | 9.075278, 49.634167 | Abt B, Band 5 (1896) | dewiki-orl 1 |
| 50 | Hesselbach | Q1411006 | 9.090556, 49.57625 | Abt B, Band 5 (1896) | dewiki-orl 1 |
| 51 | Schlossau | Q1735418 | 9.14944, 49.5406 | Abt B, Band 5 (1900) | dewiki-orl 1 |
| 52 | Oberscheidental | Q1735404 | 9.15278, 49.5064 | Abt B, Band 5 (1897) | dewiki-orl 1 |
| 53 | Neckarburken-West | Q1343017 | 9.170278, 49.376667 | Abt B, Band 5 (1898) | dewiki-orl 1 |
| 56 | Böckingen | Q1735374 | 9.188611, 49.133888 | Abt B, Band 5 (1898) | dewiki-orl 1 |
| 57 | Walheim | Q1669086 | 9.15444, 49.0107 | Abt B, Band 5 (1897) | dewiki-orl 1 |
| 58 | Benningen | Q1735337 | 9.24931, 48.9439 | Abt B, Band 5 (1902) | dewiki-orl 1 |
| 59 | Cannstatt | Q1735423 | 9.21083, 48.8133 | Abt B, Band 5 (1907) | dewiki-orl 1 |
| 60 | Köngen | Q1735387 | 9.36007, 48.6773 | Abt B, Band 5 (1907) | dewiki-orl 1 |
| 61a | Sulz | Q1735424 | 8.63667, 48.3597 | Abt B, Band 5 (1897) | dewiki-orl 1 |
| 61b | Waldmössingen | Q1735435 | 8.49333, 48.2739 | Abt B, Band 5 (1897) | dewiki-orl 1 |
| 63 | Lorch | Q1433981 | 9.68855, 48.7981 | Abt B, Band 6 (1897) | dewiki-orl 1 |
| 64 | Kastell Schirenhof | (none) | 10.03, 48.73 | Abt B, Band 6 (1897) | dewiki-orl 1 (name+coords) |
| 65 | Unterböbingen | Q1424499 | 9.9228301, 48.8181017 | Abt B, Band 6 (1894) | dewiki-orl 1 |
| 66a | Urspring | Q1735430 | 9.90069, 48.55 | Abt B, Band 6 (1904) | dewiki-orl 1 |
| 66b | Heidenheim | Q128401126 | 10.153667, 48.679083 | Abt B, Band 6 (1900) | dewiki-orl 1 |
| 67 | Kastell Buch | (none) | 10.136429, 48.909531 | Abt B, Band 6 (1896) | dewiki-orl 1 (name+coords) |
| 71a | Theilenhofen | Q1214616 | 10.84716, 49.08952 | Abt B, Band 7 (1905) | dewiki-orl 1 |
| 72 | Weißenburg | Q638525 | 10.9625, 49.0308 | Abt B, Band 7 (1906) | dewiki-orl 1 |
| Anhausen | Kleinkastell Anhausen | Q1746855 | 7.53841, 50.4813 | Abt A, Band 1, Strecke 1 (1915) | dewiki-orl 2 |

**(e) Drop reasons, per number (all verified):** 53-Ost - the single Wikidata item (Q1343017
"Kastell Neckarburken") covers both Neckarburken forts; the staged plan is the Westkastell and
the Ostkastell has no separate item nor a standalone-named plan. 14 Butzbach / 15 Grüningen -
ZERO Abt B files for these numbers in the 874 (all their files are Abt A Rhaetian Strecken
14/15); the monographs exist (Band 2a: 1894 / 1913) - growth area. 04 Ems - the QID flag is
unresolved (its P625 matches neither Alzey-Ems nor Bad Ems) - not staged. 06 Holzhausen - 18
Abt B files but no standalone-named whole-fort plan (the "Grundriss" hits are compound sheets:
a Kastellgrundriss sheet and a profile sheet that references it). 19 Ober-Florstadt - no
`ORL_19` files at all (only a modern photo). 32 Seligenstadt - 2 files (Lageplan + Therme), no
Grundriss. 54-55 Wimpfen - one monograph for both numbers: Lageplan + finds/architecture only.
62a Hüfingen - 2 x 1824 photographs, not ORL plates. 69 - a single photo (726 px). 05.10 - not
a fort (the Wetterau section, Wp/KK plates). All remaining Abt A Wp/KK files (section drawings
- growth area); the modern Commons photos/logo/Peutingeriana/derivative (section 3); the 1895
volume's Tafel I/II (photos) and Tafel V-VII (finds).

**(f) The staging as built:** `fit/src_limes.py` mirrors `fit/src_artists.py` (stdlib at module
top; `pipeline.commons`/`fit.evidence` imported lazily inside `check_staged`; `SOURCES =
{ia-1895, dewiki-orl, commons-orl}`; `FORTS` = the 45-row table above; `stage()` idempotent on
(site, title); `by` = "fit/src_limes.py <source>"; `--golden` writes
`tests/golden/src_limes_sample.json`). `check_staged()` = the offline join (every file row's
site names a staged extras row; every extras row has >= 1 picture; (site, title) unique;
classified 1:1 with p_plan 1.0 by "hand") + `evidence.check(FILES_LIMES, NO_BOOKS,
catalog=EXTRAS_LIMES)` with NO_BOOKS = `data/books/.no-books` (never created, so the book leg
is skipped) - the OQ-1 resolution, same as 204/205/213. `tests/test_src_limes.py` (no network,
socket-blocking fixture) = 5 tests: join + evidence (56 rows, 56 pass, 0 fail, 0 no-tie),
FORTS-vs-staged field for field, the box-3 machine check (>= 10 plans from >= 2 distinct
sources - 56/3), a negative control (a caption naming the wrong fort / 10 km off -> reported,
never written), and a golden comparison. Results (2026-10-12): `--check` exit 0; full suite
**0 failed / 131 passed / 1 skipped**. 211 merges the `*_limes*` staging files into the
canonical `files.jsonl` / `extras.jsonl` / `classified.jsonl`.
