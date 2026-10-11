Status: open
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

## Hand-over

**Where I am (iteration 21, agent a).** The live run is RUNNING in the background: `nohup .venv/bin/python
fit/evidence.py record --live --redo-none > /tmp/redo_none_run.log 2>&1 &` (started this session, PID
1032856; at session end still in the prefetch phase - log tail "file entities 400/352" is a cosmetic
overshoot print; next stages: part coordinates, then ~1484 paced name searches, ~25 min). It writes
data/commons/files.jsonl only AFTER the prefetch, in 25-row chunks, so the working tree was
data-clean at session end and the next driver merge will not race it. Before starting I verified all
1381 titled rows carry rec "evidence/1" -> --redo-none re-evaluates exactly the 354 none rows (74 with
stored conflicts). Committed this session: tests/test_evidence_801.py + tests/golden/evidence_801_check.txt
(7 tmp-dir rows through the real CLI `check --files F --books <absent> --catalog C`: part PASS/FAIL/FAIL-trap,
sheet PASS/FAIL, none+sheet-conflict, none+part-conflict; exit 1; golden from one real run: "evidence: 7
rows, 2 pass, 3 fail, 2 no-tie"). 13/13 tests pass; the 15-row sample golden (tests/golden/evidence_check.txt)
stayed byte-identical (it contains none of the 354). The two PITFALLS entries iter 17 left PENDING were
already committed (feddcf0, iter 18) - verified, no action.

**EXACT NEXT STEPS (in order):**
1. Poll the run: `tail -20 /tmp/redo_none_run.log; ps aux | grep "record --live" | grep -v grep`. Expected
   final line: "evidence recorded: 0 hand-tied, 0 book, 354 live". If the process is dead: read the log
   tail for the cause; a network death mid-way is resumable - re-run the same command (flipped rows are
   skipped, remaining none rows re-evaluate; the ~25 min search cost repeats for their candidates). If it
   is still running at session end, note that here and stop - do not touch files.jsonl meanwhile.
2. Audit `git diff data/commons/files.jsonl`: ONLY the 354 none rows may have changed, and only their
   "evidence" field (set_field preserves every other byte and the line terminator). WATCH: (a) "Bethleem"
   first search hit (PASS if the Dutch bethlehem-q2523914, CONFLICT if the Holy Land); (b) "Coria" first
   hit (Spain? Mexico? Corbridge?); (c) any NEW name-sharing pass beyond the accepted class (Clifford's
   Tower on york-castle) - log each in DECISIONS before keeping it. The 74 stored conflicts must keep
   re-verifying (same or improved verdict).
3. `.venv/bin/python fit/evidence.py check` -> exit 0, 0 FAIL, no-tie < 1109; `.venv/bin/python -m pytest
   -q` -> 13/13; tests/golden/evidence_check.txt byte-identical.
4. Commit data/commons/files.jsonl (explicit path, not -A, if the run wrote during another session) with
   the box ticks. Box 1: majority of the ~85-90 genuinely-naming rows pass - expect 40 part + ~60-65 sheet
   ~ 100-105; log the exact count in DECISIONS; if below majority, log the shortfall before relaxing
   anything. Box 2: every >50 km resolution is none+conflict, check exit 0, old golden unchanged. Box 3:
   row count preserved (1381 titled), every non-evidence byte preserved, suite green (now 13 tests).
5. Rewrite this hand-over; keep the gotchas.

**Verdict logic (final; unchanged since iter 17/20):** routes cascade; the first route to return pass or
conflict decides the row: (1) caption - unchanged (site names printed -> best <=50 km pass / nearest-far
conflict / none; keeps the 74 stored conflicts re-verifying); (2) part - a site has_part name printed
(norm substring) -> its P625 (the site's own point when the part has none) -> nearest <=50 km PASS
part_mention / nearest far CONFLICT / none; (3) sheet - WALK the ordered candidates (per run: pairs, then
3-word phrases, then singles; title before desc; <=12, deduped); the FIRST candidate that resolves decides
(<=50 km PASS sheet_mention, >50 km CONFLICT, store that resolution). "Nearest <=50 km wins" is
data-verified WRONG: "York" (inside "New York") would pass the 4 NYC Castle Garden rows, "Orleans" (inside
"New Orleans") the 13 New-Orleans rows, glued "York Castle" the same 4. Both new kinds store the
caption_coords shape (named_place, place_qid, place_label, place_lon/lat, site_lon/lat, dist_m); check_part
additionally re-verifies part_qid in the catalog site's has_part at check time; check_sheet RE-RUNS the
extractor (a glued candidate like "York Castle" is not a norm-substring); check_none prints the conflict
with its `route` (defaulting to "caption" so the 74 old conflicts print exactly as before).

**Live-run expectations (distances vs stored site coords, from iter 17/18):** part PASS: the 40 Clifford's
Tower rows on york-castle (Q113551546, ~6 m). sheet PASS (~60-65): Strasbourg 36-39 (argentoratum, incl.
old "Strabourg"), Reims 4-5 (durocortorum), Orleans 1-5 (cenabum, "d'Orleans"), St Louis 1 (cahokia, via
merged "St Louis"), Barkhale 1, Weesp 1 (fletio 25 km), Arnhem 1 (duno 5.5 km), Cranbourne 1 (badbury-rings
21 km), Darlington 1 (barnard-castle 33 km), Monmouth 2 (blestium 25 km), Birmingham 1 (dudley-castle 13
km), York 1 (york-castle 1914 tin - accepted name-sharing class). CONFLICT: New-Orleans-on-cenabum (~13),
the bethlehem-q2523914 rows naming Bethlehem/Palestine/Jerusalem/Maastricht/Prospect House (~30; the site
is stored at 6.61E 53.38N - NOT near Maastricht), Bristol (4 sites), Venice/Gondole (7), Chirk (2, 57 km),
Coria rows (5, "Coria" decides), Castle Garden (4, "New York" decides), Morse-atlas cahokia ("New Haven"),
Britannia-on-alauna ("Britain"). plain none: the remaining book-scan/painting rows (incl. the 6 BHL garden
manuals + 2 all-caps Bethlehem-basilica titles: all-caps is dropped as an acronym - KNOWN limitation, do
NOT loosen without a per-row re-review).

**Gotchas:** run everything through .venv/bin/python; tests: no network, no fixed ports, no writes outside
project + /tmp (the live run is a MANUAL step, not a test - the pytest suite is safe to run concurrently:
its record test reads rows the run never touches, and rewrite() is atomic via os.replace); never
rebase/merge/stash/switch branches (the driver handles them); do not touch agent c's 201 files
(fit/review.py web/review.js web/index.html data/review web/data/review.json tests/test_review.py); this
task file is agent c's - I may write only this hand-over and the Touches/Depends lines (Touches already
lists all four paths: fit/evidence.py data/commons/files.jsonl tests/test_evidence_801.py
tests/golden/evidence_801_check.txt); the STOP list is the source of truth in fit/evidence.py (any change
to it needs a fresh dump-vs-real review like the 1483-count check); NFKD-normalize BEFORE tokenizing; the
desc truncation is at a word boundary at 600; keep the batched prefetch shape (one search per unique name +
one batched claims fetch per 50); the iter-14 census in DECISIONS-archive.md (search "801") is the per-site
reference, corrected by the castrum-levefanum-is-Dutch entry in PITFALLS.md; the sheet extractor now lives
in the repo (fit/evidence.py sheet_candidates, ported verbatim) - the /tmp/sheet_proto2* files are
diff-history only; the "400/352" log line is a cosmetic overshoot in the batch print (i+50 past the end),
not an error.
