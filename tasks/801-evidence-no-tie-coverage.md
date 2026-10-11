Status: done
# 801: Evidence coverage for the 280 no-tie picture rows (OS-sheet maps and book scans)
Depends on: 200
Touches: fit/evidence.py data/commons/files.jsonl tests/test_evidence_801.py tests/golden/evidence_801_check.txt

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
- [x] `fit/evidence.py` records a passing evidence kind (caption+coords, or a new well-named kind such
      as "sheet mention") for a majority of the currently no-tie rows whose title/description genuinely
      names the site (the OS sheets that list it among the places on the map qualify; a sheet that does
      not name the site does not), with the specifics and checked date stored as before - iter 22:
      90 of the 354 no-tie rows now pass (40 part_mention + 50 sheet_mention) out of ~88-105 genuinely
      naming rows (~90%); the shortfall rows and the new name-sharing classes are logged in DECISIONS
      (2026-10-11, iter 22)
- [x] It stays fail-closed: re-run `fit/evidence.py record --live` then `check`; every row whose named
      place resolves more than 50 km from the site is recorded `none` with the conflict (never a pass);
      `check` exits 0 on the committed files; the sample golden (tests/golden/evidence_check.txt) is
      unchanged or regenerated only for an intended change - iter 22: `record --live --redo-none`
      re-evaluated all 354 (1047 names / 4679 candidates); whole-file re-check: 254 passes, 0 resolving
      >50 km; 247 conflicts (173 sheet + 74 caption), 0 resolving <=50 km; the 74 stored caption
      conflicts all re-verify as conflicts (none promoted); check exit 0, 0 FAIL, no-tie 1109 -> 1019;
      the sample golden stayed byte-identical
- [x] The row count, the byte-preservation of every existing field and the 12/12 test suite are
      preserved (the record test's fixture stays valid) - iter 22: 1490 rows before and after; the
      diff touches only the 354 none rows' evidence field (line-index audit vs git HEAD, every other
      byte preserved); the suite is now 13 tests (12 pre-existing + this task's check test) and all
      13 pass

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

## Hand-over

**DONE (iteration 22, agent a).** All three boxes verified and ticked; Status: done.

Final state: the live redo (started iter 21, finished 02:23) re-evaluated all 354 no-tie rows:
90 now pass (40 part_mention = Clifford's Tower on york-castle, 6.1 m; 50 sheet_mention -
argentoratum 33, cenabum 2, blestium 2, dudley-castle 2, plus one each Darlington/Barkhale/
Nijmegen/Gorton/Musis Sacrum/Somerset/Alfred Jewel/Pontefract/Peterborough Cathedral x2/
Braunstone Hall) and 264 stay none (247 with a stored conflict: 173 sheet + the 74 caption
conflicts re-verified; 17 plain). Whole-file fail-closed re-verified: 254 passes, 0 >50 km;
247 conflicts, 0 <=50 km. `fit/evidence.py check`: exit 0, 0 FAIL, no-tie 1109 -> 1019.
13/13 tests; tests/golden/evidence_check.txt byte-identical. Row count 1490 preserved;
line-index audit vs git HEAD: only the 354 none rows' evidence field changed.

If the driver bounces this task: read the DECISIONS.md 2026-10-11 iter-22 entry (audit
details, the three shortfall classes, the accepted name-sharing classes, and the
recommendation that the 3 weak landmark rows - 2 Peterborough-Cathedral-on-fotheringhay,
1 Braunstone-Hall-on-leicester - go to the 201 human review queue) and the rejection
reason in DECISIONS.md. Known follow-ups NOT done (would be new tasks, none filed):
(a) a disambiguation upgrade for the sheet walk (multi-hit or region-biased resolution)
to recover the ~10-15 genuinely-naming rows lost to first-hit failures (Cranbourne ->
Australia, "City" -> Paris, "Wit" -> Isle of Wight, Leffingwell/Morse/Peutinger); (b) the
Durocortorum site point (4.8422E) is 59 km east of Reims centre - a catalog fix; (c) the
all-caps title limitation (e.g. "(1881) PLAN SOUTERRAINS DE LA BASILIQUE") stays a known
limit - do not loosen without a per-row re-review.

**Lasting gotchas (keep if this task is ever reopened):** run everything through
.venv/bin/python; tests: no network, no fixed ports, no writes outside project + /tmp (a
live run is a MANUAL step, not a test); never rebase/merge/stash/switch branches (the
driver handles them); do not touch agent c's 201 files; this task file is agent c's -
write only this hand-over and the Touches/Depends lines; the STOP list in fit/evidence.py
is the extractor's source of truth (any change needs a fresh dump-vs-real review);
NFKD-normalize BEFORE tokenizing; desc truncation at a word boundary at 600; keep the
batched prefetch shape (one search per unique name + one batched claims fetch per 50);
audit files.jsonl by LINE INDEX, not title (1490 rows, 1357 unique titles - duplicates
exist); the row key is "title" (there is no "file" field); the "400/352" log line is a
cosmetic overshoot in the batch print, not an error.
