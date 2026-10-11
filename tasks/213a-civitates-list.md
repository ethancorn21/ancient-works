Status: open
# 213a: Civitates Liber secundus - the hand list file and the lead-doc books section
Depends on: none
Touches: data/books/lists/civitatesorbiste00brau.json, data/books/lists/civitatesorbiste00brau.map.json, docs/lead_artists.md

## Goal
Complete the per-book files of `civitatesorbiste00brau` (Civitates Orbis Terrarum, Liber secundus,
1575, 292 leaves; its triage A/F is committed, zero errors). The book has no printed town list, so
213 hand-writes `data/books/lists/civitatesorbiste00brau.json` - in the machinery's own dump shape
(`{"plates": ..., "figures": [...]}`, books_lists line 757): exactly 121 figure leaves (118
`other_illustration` + 3 `plate_site_plan` of stage A), one entry per leaf:
`{"fig": <0-based leaf n>, "title": ..., "page": ..., "kind": "o"|"s"|"u", "kind_by": "hand"|"A"}` -
title = the plate's own printed inscription (stage A reads it off the leaf image into
`A[n].out.caption`; when that is empty, the city name from the section's title leaf), page = the
printed number only for leaves 193-196 (1-4) and 280-284 (I-V)
(`data/raw/books/civitatesorbiste00brau/civitatesorbiste00brau_page_numbers.json`), else null; kind
o = view, s = plan, u = other (fold-out versos, an arms page); kind_by = "hand" for leaves read by
eye, "A" for the rest (kind derived from stage A's typing, unverified - documented in the lead
doc). `data/books/lists/civitatesorbiste00brau.map.json` = `[]` (list_pages maps only kind s/u and
these leaves carry no page number to map - honestly empty; 217 extends the machinery, not 213).
Then rewrite the lead-doc books section (docs/lead_artists.md): the section structure (title leaf +
1-3 plate leaves, interleaved both ways), the hOCR-misalignment and A/F-plan-under-detection
pitfalls, FEDERATORVM = views not maps, n187/n199 = versos, the transcription scheme + kind tally,
and the per-book status of all six items (216 takes its cite strings from that section). 216/217
consume this list file as the single source of truth - they must not have to guess.

## Acceptance criteria
- [ ] `data/books/lists/civitatesorbiste00brau.json` = `{"plates": null, "figures": [...]}` with
      exactly 121 entries (the 118 other_illustration + 3 plate_site_plan leaves of A), each with
      `fig` (0-based leaf n), `title` (the printed inscription, or the section's city name when
      absent), `page` (null except leaves 193-196 / 280-284), `kind` o|s|u, `kind_by` hand|A.
- [ ] All 11 unread leaves are read by eye (local images:
      `data/raw/books/civitatesorbiste00brau/triage/nNNNN.jpg` = leaf n+1) and their kind/title
      recorded with kind_by "hand": n209 (Rome), n205/n206 (Florence), n198 (Milan fold-out: view or
      plan?), n197 (Armes de Milan - an arms page, kind u), n86/n97/n193 (Brussels/Antwerp/Vienna
      title leaves - the section names), n186 (Augsburg fold-out), n50/n51 (confirm n53 = the
      2nd/3rd Barcelona plates).
- [ ] The 7 confirmed plans n58/n85/n90/n98/n109/n237/n238 carry kind s (kind_by hand); n187/n199
      are kind u (fold-out versos - A misread them as plate_site_plan); the FEDERATORVM sheets
      n157/n158 are kind o (views of the 13 Swiss cantons, not maps).
- [ ] `data/books/lists/civitatesorbiste00brau.map.json` = `[]`.
- [ ] docs/lead_artists.md books section rewritten per the goal (structure, pitfalls, corrections,
      scheme, kind tally, per-book status for all six items - the cite strings 216 needs).
- [ ] No shared-module writes: books.py, books_lists.py, data/books/index.jsonl, validation.json and
      the committed triage A/F files untouched.

## Notes
- Read the parent hand-over (tasks/213-artist-views.md ## Hand-over
**Iteration 33 (2026-10-11): mapping DEFINITIVELY RESOLVED - triage file nNNNN.jpg = A-row NNNN = 1-based
leaf NNNN+1 (DECISIONS: four evidence lines: code naming, 292/292 aspect ratios, leafNum identity, seven
direct image re-reads). Iteration-29's ten "off-by-one" reads were each one leaf wrong; the parent's 19
reads all stand. ALL 11 planned leaves of acceptance box 2 are now read by eye (13 images this session).
Next step is mechanical: write the two list files + validate, then the lead-doc rewrite.**

**This session's reads (file = A-row; kinds final):** n0197 (A197): Armes-de-Milan page (mirror Milan view
+ arms + poem + French cartouche "Armes de ceste Ville de Milan") -> u. n0198 (A198): CRISP Milan fold-out
(bird's-eye: walls/Duomo/Adda bridge/Abbiategrasso; big MEDIOLANVM cartouche = A's "METOLACOL"; Visconti
serpent; CVM PRIVILEGIO) -> o (task question answered: VIEW, not plan). n0199 (A199): faded verso (RFPCB
stamp, ghost image) -> u. n0186 (A186): CRISP Augsburg fold-out (bird's-eye + "HABET DELINE" banner +
Latin cartouche) -> o. n0187 (A187): faded verso (RFPCB) -> u. n0205 (A205): double plate 1 (top Genoa
harbour: "La sfortina", ships; bottom Florence with big "FLORENTIA urbs est suffragio..." legend) -> o.
n0206 (A206): double plate 2 (top Genoa coast "GENVEA Ligurum..." + Cum Privilegio; bottom Florence: walls,
Arno, figures; corner "VA."+"FLORENTIA") -> o. BOTH crisp (parent's "n206 faded" was wrong). n0207 (A207)
and n0051 (A51): blank/faded versos (RFPCB), text_only rows - NOT figure leaves, not in the list.
n0209 (A209): Rome plate 1 (bird's-eye: Aurelian walls/Tiber/Colosseum; "RO[MA]" title box; 40-item
antiquities legend TORTVAE/PONTES/MONTES/AQVA/DVCV/THERMAE/AMPHITHEATRA ET THEATRA) -> o. n0086 (A86):
Brussels VIEW (bird's-eye, arms, big "BRVXELLA, vrbs aulico rum frequentia..." cartouche) -> o.
n0097 (A97): Antwerp VIEW ("ANVERPIA PARS FLANDRIAE" cartouche + arms, Scheldt with ships, citadel with
lettered bastion-plan inset A-E + "Les noms des Boux leziers" legend) -> o. n0193 (A193): Vienna plate 1
(double views: top bird's-eye w/ imperial eagle + "VIENNA AVSTRIAE ORBE NOTISSIMA..." cartouche; bottom
"Danubius flu." panorama + "BVDA, vul[go]..." cartouche) -> o, printed page "2". n0050 (A50): Barcelona
plate 2, CRISP double view (top harbour w/ rainbow + "Cum Privilegio" = A's "Cum Pristelio"; bottom
inland: river/tower/sheepfold/cross, "Depingit G. Gorizius 1587") -> o.

**Corrections to the section map (iteration-29 version):** Barcelona = A48 title, A49/A50 plates (2, not 3),
A51 verso. Burgos/S. Sebastian = A52 DOUBLE TITLE (both cities on one leaf, printed page 6), A53/A54 plates
(n53/n54 are NOT Barcelona's). Genoa+Florence = A204 title, A205/A206 double plates, A207 verso. Milan =
A196 title, A197 arms (u), A198 fold-out (o), A199 verso (u). Amsterdam = A108 title, A109 plan (s),
A110 plate, A111 verso (text) - parent's "n109 precedes title n110" was the faded A111 verso misread.
Messina = A224 title, A225 plate, A226 history continuation ("MESSANÆ urbs est..."), A227 verso. STRUCTURE
IS STRICTLY title leaf -> 1-3 plates -> (more history text); versos type in A as text_only (A51/A111/
A207/A227) or plate_site_plan (A187/A199) - inconsistently. The parent's "sections interleave both ways"
is dropped as a faded-plate misread.

**F data verified:** field is "shows" (not "show"): 239 figure readings (222 view / 11 plan / 6 other) over
118 rows, 0 errors. F "plan" leaves: A30/62/65/66/90/93/105/186/229(x2)/237. Only A90 (Ghent) and A237
(Jerusalem old) are true plans among them; F MISSES all five other confirmed plans (A58/85/98/109/238) and
flags A186 (a view) - unreliable in BOTH directions (lead-doc pitfall; 217 uses hand kind s only).

**LIST FILE plan (next step):** data/books/lists/civitatesorbiste00brau.json = {"plates": null,
"figures": [121 entries sorted by fig]}, matching the machinery dump shape (books_lists line ~757 - check
exact field names there when writing). fig = A-row n (0-based). page: "2" for A193, "3" for A194, null for
all other 119 (printed pages exist only on leaves 193-196/280-284; only A193/A194 are figure leaves).
kind: s(7, hand): A58, A85, A90, A98, A109, A237, A238; u(3, hand): A187, A197, A199; o(111): hand for the
19 hand-read o's (parent's 10: A53/54/157/158/194/202/214/217/218/225 + my 9: A50/86/97/186/193/198/205/
206/209), kind_by "A" for the other 92. title = the A caption as printed (for double-plate leaves A50/
A193/A205/A206 add the second plate's inscription in square brackets; A205 = "FLORENTIA urbs est..." +
[Genoa harbour], A206 = "VA. FLORENTIA" + [GENVEA...], A193 = "VIENNA AVSTRIAE" + [BVDA...], A50 =
"Cum Pristelio" + [inland view]); the 14 empty-caption figure leaves [53,58,85,90,98,109,187,194,199,202,
214,217,218,225] take the section city name: A53 = Burgos + S. Sebastian (title leaf A52), A58 = LVTETIA
PARISIORVM (A56), A85 = BRVXELLA (A86), A90 = GANDANVM (A89), A98 = ANVERPIA (A96), A109 = AMSTELEDAVM
(A108/A110), A187 = "AVGVSTA, verso of the fold-out" (A184/A185), A194 = VIENNA AVSTRIAE (A193),
A199 = "MEDIOLANVM, verso of the fold-out" (A196), A202 = VENETIA (A201), A214 = Ancona (section title
leaf ~A212 - check caption when writing), A217/A218 = NEAPOLIS (A216), A225 = MESSANA (A224). VALIDATION
(system python3, stdlib): 121 entries; fig set == the 121 figure A-rows; kind in {o,s,u}; page null except
A193/A194; kind_by in {hand,A}; hand set == the 29 above; s/u == the 10 above. .map.json = [].

**LEAD-DOC rewrite (docs/lead_artists.md, next or following step):** books section per the task goal:
structure (title leaf -> 1-3 plates -> sometimes more history; versos type inconsistently; ~60 figure
runs); FEDERATORVM n157/158 = views of the 13 Swiss cantons (o), NOT maps; the 7 plans (incl. both
Jerusalem); versos (A187/A199 + the text versos A51/A111/A207/A227); transcription scheme + kind tally
(121: s7/u3/o111; hand 29 / A 92); the pitfalls: (a) hOCR page index misaligned 0-2 leaves from the
jp2 sequence -> books_ia.page_texts()/ocr_captions UNRELIABLE for this book (image-based A is ground
truth); (b) F's "plan" label unreliable in both directions (flags A186, misses five famous plans);
per-book status of all six IA items (civitatesorbiste00brau = fully worked: triage A 292 + F 118, list
121, map []; the other five = metadata verified, not yet triaged - 216/217 follow-on scope) - the cite
strings 216 needs. Keep the existing IA-id table. PITFALLS.md itself is NOT in 213a's Touches: the
parent 213 owns those entries (its step 10); the lead doc carries the same content meanwhile.

**Remaining (order):** (1) write lists/civitatesorbiste00brau.json + .map.json + run the validation;
tick boxes 1, 2, 3, 4. (2) rewrite the lead-doc books section; tick box 5. (3) box 6 (no shared-module
writes) is self-evident - tick at the end. No QID or test work belongs to 213a (parent 213 + 213b own
those).

**Invariants:** Touches only the 3 files (both lists + lead doc); never the triage A/F files, books.py,
books_lists.py, index.jsonl, validation.json, fit/src_artists.py, PITFALLS.md; no network, no ports, no
writes outside the project; all images local under data/raw/books/civitatesorbiste00brau/triage/.
