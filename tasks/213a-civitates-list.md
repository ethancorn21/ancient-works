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
- [x] `data/books/lists/civitatesorbiste00brau.json` = `{"plates": null, "figures": [...]}` with
      exactly 121 entries (the 118 other_illustration + 3 plate_site_plan leaves of A), each with
      `fig` (0-based leaf n), `title` (the printed inscription, or the section's city name when
      absent), `page` (null except leaves 193-196 / 280-284), `kind` o|s|u, `kind_by` hand|A.
- [x] All 11 unread leaves are read by eye (local images:
      `data/raw/books/civitatesorbiste00brau/triage/nNNNN.jpg` = leaf n+1) and their kind/title
      recorded with kind_by "hand": n209 (Rome), n205/n206 (Florence), n198 (Milan fold-out: view or
      plan?), n197 (Armes de Milan - an arms page, kind u), n86/n97/n193 (Brussels/Antwerp/Vienna
      title leaves - the section names), n186 (Augsburg fold-out), n50/n51 (confirm n53 = the
      2nd/3rd Barcelona plates).
- [x] The 7 confirmed plans n58/n85/n90/n98/n109/n237/n238 carry kind s (kind_by hand); n187/n199
      are kind u (fold-out versos - A misread them as plate_site_plan); the FEDERATORVM sheets
      n157/n158 are kind o (views of the 13 Swiss cantons, not maps).
- [x] `data/books/lists/civitatesorbiste00brau.map.json` = `[]`.
- [x] docs/lead_artists.md books section rewritten per the goal (structure, pitfalls, corrections,
      scheme, kind tally, per-book status for all six items - the cite strings 216 needs).
- [x] No shared-module writes: books.py, books_lists.py, data/books/index.jsonl, validation.json and
      the committed triage A/F files untouched.

## Notes
- Read the parent hand-over (tasks/213-artist-views.md ## Hand-over) - the parent owns boxes 1/4/6
  of 213 (QIDs, golden, test); 213a owns only the two list files and the lead-doc books section.

## Hand-over
**Iteration 35 (2026-10-11): ALL SIX BOXES DONE - 213a is finished.** Box 5: rewrote the books
section of `docs/lead_artists.md` (only change this session; ~80/19 lines). Content: the six-item
table gained a **cite-string column for 216** (verbatim `BOOKS` values, backed by the cached IA
metadata: publisher Rade 1575 / Zeiller+Merian-Frankfurt 1654 / Merian-PAN 1642; region notes:
western Europe + Mediterranean for liber2, Swiss cantons for the Merian volumes; the book-level
`region` is 216's call - the doc says so); new **Triage** paragraph (A 171/118/3 typing, F 239
readings, 121 figure leaves = exactly the list's set); **Section structure** (strict
title-then-plates - the interleave note was a faded-verso misread; six blank versos typed
inconsistently A51/111/207/227 vs A187/199; the three fold-outs incl. Venice = views on BOTH
sides, recto A201 is the famous view); **two pitfalls for 216/217** (hOCR page index misaligned
0-2 leaves -> page_texts/djvu_txt unreliable, image-based A rows are ground truth; machines
under-detect plans in BOTH directions - A typed only 3/121, F's 10 plan leaves hold only 2 true
plans A90/A237, the hand list's kind s is the only plan source); **corrections** (FEDERATORVM =
views not maps, the 7 true plans, A187/197/199 versos+arms, the two caption fixes); the
**transcription scheme + tally** (121 = s7/u3/o111, hand 30/A 91, pages only fig 193/194, map []
honestly empty); **per-book status of all six** (liber2 fully worked; the other five metadata
verified, untriaged = 216/217 scope) - 216 takes its cite strings from this section. Box 6:
`git status --short` = only docs/lead_artists.md; books.py/books_lists.py/index.jsonl/
validation.json/triage A/F untouched (verified with a scoped diff).

**State of the files (all committed with this session):**
- `data/books/lists/civitatesorbiste00brau.json` = `{"plates": null, "figures": [121]}` sorted by
  fig; kinds o=111 / s=7 / u=3; kind_by hand=30 / A=91; `page` non-null only for fig 193 ("2") and
  194 ("3") (strings, as in the page_numbers file; no figure leaf falls in leaves 280-284).
- `data/books/lists/civitatesorbiste00brau.map.json` = `[]` (honestly empty: `list_pages` maps
  only kind s/u BY PRINTED PAGE NUMBER and no figure leaf carries one; 217 extends the machinery).
- `docs/lead_artists.md` books section = the lead-doc home of every 213a finding (structure,
  pitfalls, corrections, scheme, tally, per-book status). The parent 213 still owes: its QID table
  for the 7 verified towns (fit/src_artists.py + lead doc), --check/--golden, the test, and the
  PITFALLS.md entries (its step 10) - the lead doc carries the same content meanwhile.

**Nothing left for 213a.** If reopened: the list file is self-documenting (each entry's
kind/kind_by/title per the scheme); a future correction = edit the JSON, then re-check the
invariants against the A file (fig set = A's 118 other_illustration + 3 plate_site_plan; tally
s7/u3/o111; pages only 193/194). Invariants held throughout: Touches = the 3 files; never the
triage A/F, books.py, books_lists.py, index.jsonl, validation.json, fit/, PITFALLS.md; no network,
no ports, no writes outside the project; triage images local (nNNNN.jpg = leaf n+1 = A row NNNN).

**Iteration 34 (2026-10-11): the two list files are WRITTEN + VALIDATED - boxes 1-4 ticked.**

**State of the files (committed with this session):**
- `data/books/lists/civitatesorbiste00brau.json` = `{"plates": null, "figures": [121]}` sorted by
  fig; kinds o=111 / s=7 / u=3; kind_by hand=30 / A=91; `page` non-null only for fig 193 ("2") and
  194 ("3") (strings, as in the page_numbers file; no figure leaf falls in leaves 280-284).
  Shape matches the machinery dump (books_lists.py:757) + the extra `kind_by` field; `list_pages`
  consumes `page`/`kind` fine.
- `data/books/lists/civitatesorbiste00brau.map.json` = `[]` (honestly empty: `list_pages` maps only
  kind s/u BY PRINTED PAGE NUMBER and no figure leaf of this book carries one; 217 extends the
  machinery, 213a does not).
- The build script `/tmp/build_civitates_list.py` (stdlib; regenerates the file deterministically
  from the committed A file + override tables) is EPHEMERAL - /tmp does not survive. The override
  tables are fully recorded in the file itself (each entry's kind/kind_by/title is self-documenting
  per the scheme below); a future correction = edit the JSON directly, then re-check the invariants
  against the A file with a small ad-hoc script.
- git status after this step: only the two new list files; no shared module touched (box 6 holds so
  far - re-verify at the end with `git status --short`).

**Corrections made this session (the lead doc must carry all of them):**
- **The Venice plate is a two-sided FOLD-OUT.** A201 (A: other_illustration, caption "VENETIA" = the
  plate's own printed title, top right) = the RECTO: the famous bird's-eye view, legend items
  1-~52, "Cum Privilegio" cartouche. A202 (A: other_illustration, empty caption) = the VERSO: a
  second full view of Venice (legend items 53-153 + ALTRI CHIESE + DELLE COSE PIÙ NOTABILI). Both
  are real pictures (unlike the blank versos A187/A199) -> both kind o, both hand (the parent read
  the verso in iteration 27 as "n202 = the famous view" - that read was right about the file; I
  read the recto this session). The iteration-33 plan note "A202 = VENETIA (A201 = title leaf)" was
  wrong on the parenthetical: A201 is the recto plate, not a title leaf; the section's
  title/history leaf is A200 (A caption empty). Section order stays strictly title -> plates:
  A200 -> A201/202 (fold-out) -> A203/A204 (text) -> A204-ish Genoa/Florence title -> A205/206.
- **A54** (Burgos/S. Sebastian double plate): the full bottom inscription was captured on the leaf
  image: "SANCT. SEBASTIANVM vulgo Donostien ad mare Oceanum insigne regni Guipuzcoa oppidum"
  (engraver signature "Depingebat Georgius Hoynge Antuerpianus") - appended as the `[other plate:
  ...]` bracket in the file.
- **Two A captions were garbles of the true printed inscription and were corrected in the file**
  (both verified on the leaf image): fig 50 "Cum Pristelio" -> "Cum Privilegio" (Barcelona plate
  banner); fig 198 "METOLACOL" -> "MEDIOLANVM" (Milan fold-out cartouche).
- The **hand set grew 29 -> 30** (A201 read this session): o-hand = 50,53,54,86,97,157,158,186,193,
  194,198,201,202,205,206,209,214,217,218,225 (20); s-hand = 58,85,90,98,109,237,238 (7);
  u-hand = 187,197,199 (3). A-derived kinds: the other 91 o's (kind_by "A").

**Prep-notes check (tasks/prep/213.md, per the iteration-34 prompt):** the assumptions that bear on
213a were verified correct against current main: the list dump shape (books_lists.py:757,
`{"plates","figures"}`, indent=0 - my file matches its 12 siblings), `.map.json` is a list (so
`[]` is a valid value), the per-book file pattern `data/books/{triage,lists}/<ia>.*`, and the
stdlib-only system python3 (the build script ran under plain python3). Nothing the prep claimed was
wrong for 213a's scope. The prep's evidence/801/211/212/.venv assumptions belong to the parent 213
and 213b - no action here. (The parent's iteration-27 claim "sections interleave both ways" was
already dropped in iteration 33 as a faded-plate misread; this session found no new interleaving -
the Venice case is a fold-out, not an interleave.)

**Next step (box 5): rewrite the books section of `docs/lead_artists.md`.** First Re-read: the
current `docs/lead_artists.md` (the iteration-26 books section) and the parent hand-over (its
step 4 lists what the section must contain). Content per the goal:
(a) book identity: civitatesorbiste00brau = Liber secundus, 1575, 292 leaves, IA BookReader stream
(jp2 + hOCR, unrestricted); triage A 292/292 + F 118/118 committed (239 figure readings: 222 view /
11 plan / 6 other); (b) section structure: title leaf (big Latin title + history text) -> 1-3 plate
leaves -> sometimes more history; versos type inconsistently in A (text_only: A51/A111/A207/A227;
plate_site_plan: A187/A199); the three fold-outs: Augsburg (A186 recto view / A187 blank verso),
Milan (A198 recto view / A199 blank verso), Venice (A201/A202 = views on BOTH sides);
(c) pitfalls: the hOCR page index is misaligned with the jp2 leaf sequence by a drifting 0-2 leaves
(hOCR leaf 85 holds the Brussels title text A reads on leaf 87) -> books_ia.page_texts()/
ocr_captions are UNRELIABLE for this book, the image-based A rows are ground truth, 217 must not
use page_texts for civitates; F's "plan" label is unreliable in BOTH directions (F flagged only
11/121 figure pages as containing a plan; of F's plan leaves A30/62/65/66/90/93/105/186/229(x2)/
237 only A90 (Ghent) and A237 (Jerusalem old) are true plans - F misses five of the seven hand-
verified plans A58/85/98/109/238 and mis-flags A186, a view); (d) corrections: FEDERATORVM sheets
A157/A158 = views of the 13 Swiss cantons (kind o), NOT maps; the 7 plans incl. both Jerusalem
(A237 old city, A238 new city); A187/A199 = blank fold-out versos (kind u, carry no picture);
A197 = the Milan arms page (kind u, an image but not a view/plan); the two caption corrections
above; (e) the transcription scheme + tally: 121 figure leaves, one entry per leaf, title = the
plate's printed inscription (A caption, corrected where the image showed a garble) or the
section's city name when empty (14 such leaves: the city map is in the file itself); double-plate
leaves 50/54/193/205/206 carry the second half's inscription in `[other plate: ...]`;
kinds s7/u3/o111; kind_by hand 30 / A 91; printed pages only on fig 193/194; (f) per-book status of
ALL SIX IA items (216 takes its cite strings from here): civitatesorbiste00brau (1575, Liber
secundus) = FULLY WORKED (triage A/F + list 121 + map []); the other five = verified present on IA
as BookReader streams, metadata checked, NOT yet triaged (216/217 follow-on scope): ARes73114
(1586, Tomus quartus), ARes73115 (1597, Liber quintus), 17095748888888bsb-00105587 (1600, BSB,
Liber Primus), topographiahelve00zeil (1654, Merian Topographia Helvetiae),
rcin.org.pl.WA51_13719_PANB665-r1642_Topographia-Helvetia_152915 (1642, PAN Poland). Keep the
existing IA-id table in the lead doc; only replace the books section - the Imola/Venice
image-source parts belong to the parent (213) and 213b.
After writing the doc: tick box 5, then box 6 (verify `git status --short` shows nothing outside
Touches), tick the parent's box 5 only if 213b's work is in (it is not yet - leave it).

**Human message (disk, iteration-34 prompt):** the VM disk filled this morning; the lead says any
213 test that copies the data tree must link read-only data (symlink or hard link) instead.
213a is not affected (this step wrote 12.6 KB total; the validation read the triage jsonl in place).
Carry it to 213b: if a test needs the data tree, `ln -s` / hard-link it into the temp dir, never
`cp` (data/raw is large).

**Invariants (unchanged):** Touches only the 3 files (both lists + lead doc); never the triage A/F
files, books.py, books_lists.py, index.jsonl, validation.json, fit/src_artists.py, PITFALLS.md
(parent 213 owns the PITFALLS entries - its step 10 - the lead doc carries the same content
meanwhile); no network, no ports, no writes outside the project; all images local under
data/raw/books/civitatesorbiste00brau/triage/ (file nNNNN.jpg = A-row NNNN = 1-based leaf NNNN+1 -
settled in iteration 33, four lines of evidence).
