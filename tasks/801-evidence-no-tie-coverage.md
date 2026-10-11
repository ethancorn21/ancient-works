Status: open
# 801: Evidence coverage for the 280 no-tie picture rows (OS-sheet maps and book scans)
Depends on: 200
Touches: fit/evidence.py

## Goal
Task 200 (done) records machine-checkable ties on every picture row; 280 of the 1381 commons rows
carry kind `none` *without* a stored conflict - the caption names no full site name, so the
conservative full-name route of `named_places_in` finds no place to resolve. Most are Ordnance-Survey
sheet maps ("Ordnance Survey Drawings - <town>") whose description enumerates many places, and book
plate scans. The acceptance wording of 200 allows reported no-tie rows, but GOAL.md's intent is that
*every picture* be tied to its place - so improve the coverage while staying fail-closed: a row only
gets a passing field when the named place actually resolves near the site, and a resolved place that
is far away must keep the row `none` with the conflict stored (the existing 74 conflict rows show the
mechanics).

## Acceptance criteria
- [ ] `fit/evidence.py` records a passing evidence kind (caption+coords, or a new well-named kind such
      as "sheet mention") for a majority of the currently no-tie rows whose title/description genuinely
      names the site (the OS sheets that list it among the places on the map qualify; a sheet that does
      not name the site does not), with the specifics and checked date stored as before
- [ ] It stays fail-closed: re-run `fit/evidence.py record --live` then `check`; every row whose named
      place resolves more than 50 km from the site is recorded `none` with the conflict (never a pass);
      `check` exits 0 on the committed files; the sample golden (tests/golden/evidence_check.txt) is
      unchanged or regenerated only for an intended change
- [ ] The row count, the byte-preservation of every existing field and the 12/12 test suite are
      preserved (the record test's fixture stays valid)

## Notes
- The caption route matches only a full site name/alias as a substring of title+description
  (`named_places_in`); that conservatism is what leaves the OS sheets un-tied (their captions name the
  sheet's town, and the site appears at most in a place list). The book matcher
  (pipeline/books_match.py) already has token-level matching machinery; reuse its rules rather than
  inventing looser ones, and keep the distance check (50 km) as the guard.
- A sheet-index alternative: the OS sheet description's place list can be parsed and each entry
  resolved, like the current route, but that multiplies network calls - the batched prefetch of
  task 200's `record_live` (one search per unique name, one batched claims fetch) must stay the shape.
- Rerunning `record --live` is idempotent for recorded rows; to re-evaluate only the no-tie rows a
  `--only`-style filter or a kind-based skip is needed - add it in this task if useful.
- Filed by agent c (task 200) from the measured outcome: 1338 live-recorded rows = 825 category,
  164 caption_coords, 38 hand_tied, 354 none (74 with stored conflicts, 280 plain).
