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
- Read the parent hand-over (tasks/213-artist-views.md ## Hand-over) first: it holds the 16 leaves
  already read by eye (iteration 27) - do not re-read them unless the list needs a correction.
- A's `out.caption` is image-based (the LLM reads the leaf image) and is the ground truth for
  inscriptions here; the hOCR page index is misaligned by 0-2 leaves (PITFALLS) - never use
  `books_ia.page_texts()`/ocr_captions for this book.
- A's `plate_site_plan` typing is wrong for n187/n199 (blank versos) and n238 is the only correct
  one; F's 11 "plan" figure readings of 239 under-detect the 7 confirmed plans - kind s is trusted
  only from a hand read here (PITFALLS).
