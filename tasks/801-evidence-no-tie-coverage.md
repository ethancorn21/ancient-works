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

## Hand-over

**Where I am (iteration 17, agent c).** Extractor v3 FINAL (offline, verified over all 354 none rows) +
verdict-logic design settled (fixes the iter-16 contradiction) + one census correction (castrum-levefanum
is the Dutch site, not Beauvais). No repo changes this session (all work in /tmp; repo byte-identical to
iter-16's commit e6ebbaa; tests not re-run because nothing in the repo changed - last full run was 12/12
green in the 800 verification). NEXT = the live resolution run, then the fit/evidence.py implementation.

**Prototype (recreate if /tmp wiped):** /tmp/sheet_proto2.py = v3 (final rules); /tmp/sheet_proto2_out_v3.txt
= its frequency list; /tmp/sheet_proto2_dump.txt = per-row candidates for all 354 none rows (94 KB);
/tmp/sheet_proto2_v2.py + /tmp/sheet_proto2_out_v2.txt = iter-16 version (kept to diff). v3 deltas vs v2:
(1) digits never kept (t[0].isalpha()) and a digit between two kept words BREAKS a run (kills NYPL
barcodes "11707950 000", year-range pairs "1806 1820", hex-fragment glue); (2) the St-merge marker now
accepts mixed-case "St" too (v2 matched only "ST" - "St. Louis" was silently LOST; the cahokia row needs
it) and merges only when no comma / len>=3 lowercase word / digit sits between "St" and the next kept
word; (3) STOP extended: iter-16's pending words (prepositions the/van/les/des/and/for/with/from/bij/met/
naar/per + harmless 2-letters; ordnance quartier house design pattern textile numerisation onderdeel
english roman) PLUS words mined from the v2 dump (full list in DECISIONS 2026-10-11 801). Measured: 1483
unique candidates (was 2078; iter-16 expected ~1400-1600), 346/354 rows with >=1 sheet candidate, EXACTLY
40 part hits (all Clifford's Tower, unchanged). The 8 rows now with zero candidates are legit: 6 BHL
garden-manual book scans (name nothing) + 2 all-caps titles ("PLAN BASILIQUE DE BETHLÉHEM",
"PLAN SOUTERRAINS DE LA BASILIQUE") - all-caps is dropped as acronym, so they stay none; KNOWN
LIMITATION, do not loosen the acronym rule without a per-row re-review. Tail = person names (Seyboth,
Dennis, Robert, Adam, Mignon...) - expected, harmless (no P625; one search each; ~25-35 min one-off at
1 req/s). STOP only cuts cost - the distance guard is the mechanism.

**Verdict logic (FINAL - supersedes iter-16's "nearest <=50 km wins" wording; iter-16 finding #4 only
makes sense with a walk):** routes cascade; the first route to return pass or conflict decides the row:
(1) caption - UNCHANGED (site names printed -> best<=50km pass / nearest-far conflict / none; keeps the
74 stored conflicts re-verifying); (2) part - a site has_part name printed (norm substring) -> its P625
(site's own coords when the part has none) -> nearest <=50 km PASS kind part_mention / nearest far
CONFLICT / none; (3) sheet - WALK the ordered candidates (per run: 2-word pairs, then 3-word phrases,
then singles; title before desc; <=12, deduped); the FIRST candidate that resolves decides: <=50 km
PASS kind sheet_mention, >50 km CONFLICT (store that resolution). Why not "any-nearest<=50km wins"
(data-verified false passes the walk prevents): "York" (a word inside "New York") resolves ~2 km from
york-castle and would pass the 4 NYC "Castle Garden" rows; "Orleans" (inside "New Orleans") resolves
onto cenabum itself and would pass the 13 New-Orleans rows; "York Castle" (glued from "New York. Castle
Garden") resolves to the site itself and would pass those same rows - the walk stops at the first
resolution ("New York" / "New Orleans" / "Peutinger"), all far -> conflict. Both new kinds store the
caption_coords shape (named_place, place_qid, place_label, place_lon/lat, site_lon/lat, dist_m);
check_part additionally re-verifies part_qid in the catalog site's has_part at check time; check_sheet
re-verifies the norm-substring of named_place in title+desc (candidates are norm-substrings by
construction and check() normalizes both sides).

**Live-run expectations (distances measured this session vs stored site coords):**
- part PASS: 40 Clifford's Tower rows on york-castle (Q113551546, 6 m).
- sheet PASS (~60-65): Strasbourg 36-39 (argentoratum; "Strasbourg"/"Strabourg" old spelling), Reims 4-5
  (durocortorum; incl. "Val Mont"), Orleans 1-5 (cenabum: "d'Orleans" NFKD -> 0.4 km), St Louis 1
  (cahokia, via the merged "St Louis"), Barkhale 1, Weesp 1 (fletio, 25 km), Arnhem 1 (duno, 5.5 km),
  Cranbourne 1 (badbury-rings, 21 km), Darlington 1 (barnard-castle, 33 km), Monmouth 2 (blestium, 25 km),
  Birmingham 1 (dudley-castle, 13 km), York 1 (york-castle 1914 tin - the accepted name-sharing class).
- CONFLICT: New-Orleans-on-cenabum (~13), the bethlehem-q2523914 rows naming Bethlehem/Palestine/
  Jerusalem/Maastricht/Prospect House (~30; "Bethlehem" -> Q5776 Holy Land 4700 km is ALREADY stored in
  the existing conflicts, no new search needed; Maastricht is ~290 km from the site's stored point -
  bethlehem-q2523914 sits at 6.61E 53.38N, NOT near Maastricht), Bristol (4 sites), Venice/Gondole (7),
  Chirk (2, 57 km), Coria rows (5; person name "Lorenzo Coria" -> "Coria" decides), Castle Garden (4;
  "New York" decides), Morse-atlas cahokia row ("New Haven"), Britannia-on-alauna row ("Britain").
- plain none: the remaining book-scan/painting rows where nothing resolves.
- WATCH for the live run: (a) "Bethleem" search first hit (File:BethleemPlan.png - a plan of the site's
  own basilica; PASSES if it resolves to the Dutch site, conflicts if to the Holy Land); (b) "Coria"
  first hit (Spain? Mexico? Corbridge?); (c) any NEW name-sharing pass beyond the accepted class - log
  each before keeping it. If passes land below a majority of the ~85-90 genuinely-naming rows, log the
  shortfall in DECISIONS before relaxing anything.

**Exact next step (iter 18):** (1) LIVE prototype (manual, paced via commons.get, ~25-35 min one-off):
resolve the 1483 uniques exactly like resolve_places (one wbsearchentities per unique name, then ONE
batched wbgetentities claims 50/batch), apply the walk per row, dump to /tmp/sheet_verdicts.txt; compare
with the expectations above - especially the WATCH items. (2) IMPLEMENT in fit/evidence.py (Touches):
refactor-first commit - extract live_evidence's caption block into _caption_route, zero behavior change,
tests green; then part/sheet routes + kinds part_mention/sheet_mention + check_part/check_sheet + docstring
kind list + `--redo-none` (live-only; plain `record` stdout must stay exactly "evidence recorded: N
hand-tied, N book, N live"). (3) Run `record --live --redo-none` on the real files (diff: ONLY the 354
none rows' evidence field changes; a stored conflict is rewritten only when the walk still yields a
conflict, else per the verdict) then `check` (exit 0, 1490 rows, zero FAIL) then
.venv/bin/python -m pytest -q (12/12). The golden sample (tests/evidence_sample/*, 15 rows:
old-sarum/hampton-court/caister fixtures + book fixtures) contains NONE of the 354 none rows, so it must
stay byte-identical - verify, do not regenerate. (4) Add the two pending PITFALLS entries (context
limit cut them last session): "Latin Peutinger names (Casaromago, Sammarobriva) have no Wikidata items;
'Peutinger' resolves to Q2081791 Ellwangen gymnasium 475-500 km from the Dutch Limes sites" under the
Wikimedia-APIs subsection, and "catalog castrum-levefanum-q1309559 is the DUTCH Limes fort (5.35E 51.96N),
not Beauvais (1.99E 49.42N) - don't assume geography from the name" under This codebase.

**Gotchas (unchanged + new):** run everything through .venv/bin/python (books_match imports PIL); do NOT
touch requirements.* (agent a's task 800); tests: no network, no fixed ports, no writes outside project
+ /tmp; never rebase/merge/stash (driver handles branches); set_field preserves line bytes; the 74
existing conflict rows must keep re-verifying after the run; desc truncation is at a WORD boundary at 600
(a cut-off word like "Bethl" becomes a phantom candidate); NFKD-normalize BEFORE tokenizing (v1's
"Orléans" disaster); keep the batched prefetch shape (one search per unique name + one batched claims);
the iter-14 census in DECISIONS (2026-10-10 801) is still the best per-site reference, with this
hand-over's corrections (castrum-levefanum Dutch; bethlehem far-from-Maastricht).
