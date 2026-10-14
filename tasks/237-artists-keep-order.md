Status: open
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

- [ ] In `fit/src_artists.py:stage` move the known-date swap ahead of the `c.keep()` gate (the sources.py /
      vdD order), with the same Zwolle-precedent comment as src_van_deventer.py.
- [ ] No staged row changes: re-run `.venv/bin/python fit/src_artists.py --check` and `--golden` and confirm
      the golden sample is byte-identical (the swap does not fire for the two staged rows).
- [ ] `tests/test_src_artists.py` still passes unchanged.

## Notes
- Filed from 236a (2026-10-13): 236a's own module uses the sources.py / vdD order (swap before keep), so
  this aligns the sibling module with the established pattern instead of letting two stage()s disagree.
- Do not touch the staged rows or the golden file; the change is the two statements' order in stage().
