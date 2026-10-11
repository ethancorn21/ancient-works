Status: open
# 216: Book machinery - BOOKS entries for the six artists'-view books (Civitates, Merian)
Depends on: 213, 215
Touches: pipeline/books.py

## Goal
The book machinery (`pipeline/books.py:BOOKS`) has no entries for the artists'-view books, so their
per-book files (213's `data/books/triage/civitatesorbiste00brau.A.jsonl`/`.F.jsonl`) cannot be driven by
`books.py` commands (fetch/triageA/B/F/ocrmap/validate/index all key on BOOKS). Add entries for the six
Internet Archive books task 213 verified - all BookReader streams, all free, metadata cached in
`data/raw/books/<ia>/` on this machine:

| key (suggest) | ia id | book |
|---|---|---|
| civitates_liber2 | civitatesorbiste00brau | Civitates Orbis Terrarum, Liber secundus (1575) - 292 leaves |
| civitates_liber4 | ARes73114 | Civitates Orbis Terrarum, Tomus quartus (1586) |
| civitates_liber5 | ARes73115 | Civitates Orbis Terrarum, Liber quintus (1597) |
| civitates_liber1 | 17095748888888bsb-00105587 | Civitates Orbis Terrarum, Liber primus (BSB scan, 1600) |
| merian_helvete00zeil | topographiahelve00zeil | Merian, Topographia Helvetiae (1654) |
| merian_panb665 | rcin.org.pl.WA51_13719_PANB665-r1642_Topographia-Helvetia_152915 | Topographia Helvetiae (PAN Poland, 1642) |

Region "Italy" is wrong for the German/Swiss/Austrian towns these books cover - use the region the
machinery expects for a book (see the existing entries' convention; the town's region comes from the
row, not the book, so pick the dominant one and say so in the `cite` string). The `cite` strings come
from `docs/lead_artists.md` (task 213).

## Acceptance criteria
- [ ] The six entries exist in BOOKS (ia, region, year, cite); `books.py fetch <key>` works for at least
      civitates_liber2 (its 292 triage images already cached in data/raw - no re-download).
- [ ] `books.py ocrmap civitates_liber2` and `validate civitates_liber2` run without KeyError (they may
      report "no list yet" - 217 adds the lists; do not add list data here, that is 217's module).
- [ ] The existing BOOKS entries are untouched; `validate` over them gives the same results as before.
