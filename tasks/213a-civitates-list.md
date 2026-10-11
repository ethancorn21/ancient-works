Status: done
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
**DONE (iteration 36, 2026-10-11).** All six boxes verified true from scratch and `Status: done`
set. The iteration-35 session had ticked the boxes and committed the lead-doc rewrite but left the
status "open"; this session re-checked every box against the committed files (not the notes) and
changed only the status line + this section. Verification detail is in the DECISIONS entry
"213a DECISION: iteration-36 re-verification...".

**State of the files (final, committed):**
- `data/books/lists/civitatesorbiste00brau.json` = `{"plates": null, "figures": [121]}` sorted by
  unique fig; fig set = exactly the A file's 118 other_illustration + 3 plate_site_plan leaves
  (A187/A199/238); kinds s 7 (58/85/90/98/109/237/238, all hand) / u 3 (187/197/199, hand) / o 111
  (hand 20 incl. the two caption corrections fig 50 "Cum Privilegio", fig 198 "MEDIOLANVM", and the
  FEDERATORVM sheets 157/158; A-derived 91); the 14 empty-caption leaves carry the section city
  name; double-plate leaves 50/54/193/205/206 carry the second plate's inscription in a
  `[other plate: ...]` bracket; `page` non-null only for fig 193 ("2") and 194 ("3") - matches the
  source page-numbers file (whose `leafNum` is 1-based, so fig 193 = leaf 194); no figure leaf
  falls in leaves 279-283 (the I-V pages).
- `data/books/lists/civitatesorbiste00brau.map.json` = `[]` (honestly empty: `list_pages` maps
  kind s/u BY PRINTED PAGE NUMBER and no figure leaf of this book carries one; extending the
  machinery is 217, not 213a).
- `docs/lead_artists.md` books section = the lead-doc home of every 213a finding: the six-item
  table WITH THE CITE-STRING COLUMN 216 takes verbatim; triage numbers; section structure (strict
  title-then-plates; the six blank versos; the three fold-outs incl. Venice = views on both
  sides, recto A201 = the famous view); the two pitfalls for 216/217 (hOCR page index misaligned
  0-2 leaves -> `page_texts()`/`djvu_txt()` unreliable for this book, image-based A rows are
  ground truth; machines under-detect plans in BOTH directions -> the hand list's kind s is the
  only plan source); the corrections (FEDERATORVM = views not maps; the 7 true plans; A187/197/
  199 versos+arms; the two caption fixes); the transcription scheme + tally (121 = s7/u3/o111,
  hand 30 / A 91, map `[]`); per-book status of all six IA items.

**Re-verification notes (iteration 36):** full test suite green in the existing .venv (29/29,
~36 s) - note the driver's .venv REBUILD from requirements.txt is failing project-wide (unpinned
hashes, driver note 2026-10-10); the existing .venv lacks pyshp but no test imports it. git log
of the four 213a commits: only the three Touches files + task file + DECISIONS.md touched - no
shared module (books.py, books_lists.py, index.jsonl, validation.json, triage A/F, fit/,
PITFALLS.md). No network, no ports, no writes outside the project, at any point in the task.

**Nothing left for 213a.** If ever reopened: the list file is self-documenting (each entry's
kind/kind_by/title per the scheme above); a correction = edit the JSON, then re-check the
invariants against the A file (fig set = A's 118+3; tally s7/u3/o111; hand set 30; pages only
193/194). The parent 213 still owes its own boxes (QID table in fit/src_artists.py, --check/
--golden, the test, PITFALLS entries) - 213a never owned those.
