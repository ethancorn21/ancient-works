Status: done
# 237: src_artists' known-date swap sits behind the keep() gate - align with sources.py / vdD
Depends on: none
Touches: fit/src_artists.py

## Goal
`fit/src_artists.py:stage` runs `c.keep(title, m)` BEFORE the known-drawing-date swap, the reverse of
`pipeline/sources.py` (L186-191) and `fit/src_van_deventer.py:stage` (swap first, with the Zwolle
precedent explained in a comment: keep() must judge the drawing's year, so a post-1925 scan of an old
drawing passes). For a staged row whose file page lost the drawing's date AND whose title carries no
plan word and no year, keep() sees year None (or a modern upload year) and fails loud instead of ever
reaching the swap - the known-date feature (the Leonardo/Imola precedent in this very module's rows) is
unreachable for that shape. The artists rows as staged today all pass keep() pre-swap (the Imola title
carries its own year), so this is latent, not broken.

- [x] In `fit/src_artists.py:stage` move the known-date swap ahead of the `c.keep()` gate (the sources.py /
      vdD order), with the same Zwolle-precedent comment as src_van_deventer.py.
- [x] No staged row changes: re-run `.venv/bin/python fit/src_artists.py --check` and `--golden` and confirm
      the golden sample is byte-identical (the swap does not fire for the two staged rows).
- [x] `tests/test_src_artists.py` still passes unchanged.

## Notes
- Filed from 236a (2026-10-13): 236a's own module uses the sources.py / vdD order (swap before keep), so
  this aligns the sibling module with the established pattern instead of letting two stage()s disagree.
- Do not touch the staged rows or the golden file; the change is the two statements' order in stage().

## Hand-over
(2026-10-14, iteration 153, agent c - DONE, all boxes ticked; this session did the whole task in one step)
- State: `fit/src_artists.py:stage` now runs the known-date swap (the `want = x.get("date")` block) BEFORE
  the `c.keep(title, m)` gate, with the Zwolle-precedent comment copied verbatim from
  fit/src_van_deventer.py:stage (keep() must see the swapped m: it judges the DRAWING's year). This matches
  pipeline/sources.py L186-191 and vdD. The old one-line trailing comment on the swap is gone (superseded by
  the multi-line one).
- Verification (all passed, in this session, this branch): `--check` exit 0 (2/2 PASS, offline);
  `--golden` output byte-identical to the committed tests/golden/src_artists_sample.json (cp + diff; the swap
  does not fire for the two staged rows - Imola's title carries "1502" so year_of already equals the known
  date, Venice has no override); tests/test_src_artists.py 5/5 (it never calls stage()). git status clean
  apart from the intended edit (restored agent a's 307d_*.png re-encoding jitter to main's bytes first).
- Nothing left for a later session. If a future row for this module ever has a file page that lost the
  drawing's date AND a title with no year and no plan word, stage() will now pass it (keep() sees the known
  date) instead of failing loud before the swap.
