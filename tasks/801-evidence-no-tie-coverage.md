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

**Where I am (iteration 15, agent c).** Measurement step done (no code yet). RESOLVED the iter-14 open
risk in the good direction: Clifford's Tower Q113551546 HAS P625 (-1.0800092, 53.9558873) = 6 m from
york-castle's stored point (Curtain Wall Q17530656 = 149 m). Exactly 40 of the 354 stored-none rows name
a has_part of their own site - all "Clifford's Tower Survey" titles on york-castle - so part_mention adds
40 passes; the remaining ~45 genuinely-naming rows must pass via sheet_mention. Expected total passes
~85 of the ~85-90 genuinely-naming rows -> box 1 is reachable without loosening any guard.

**Measured part census (343 unique part qids; 2 full batch runs + 5 spot checks, all agree):**
332 have P625; 311 within 50 km of their own site; 19 far (stay fail-closed if a caption names them; no
linear-site special-casing): 14 on lower-german-limes (Fossa Corbulonis 148, Forum Hadriani 151, Matilo
143, Praetorium Agrippinae 150, Laurium 118, Traiectum 103, Fectio 99, Castra Herculis 53, Temple of Elst
50.5, Castra Novaesium 56, Reckenberg 58, Durnomagus 69, Castra Divitia 89, Q1430260 92, Rigomagus 132 km
from the stored end), hopewell-ceremonial-earthworks x3 (89-158 km), poundbury-hill 168. Parts WITHOUT
P625 (11): Q110065002 (stonehenge), Q131296685 + Q131379956 (avebury), Q137911205/219/222 (windmill-hill),
Q131300617 (two-bowl), Q1165437 (vix), Q135830814 (causse), Q81103 + Q1416685 (fort-totten). Design: a
part without P625 uses the SITE's own coords (catalog has_part = spatially inside the site => 0 km);
no current none-row names such a part, so it is a safety net only.

**Run-1 anomaly (not a pitfall, unreproduced):** first batch run counted 13 parts w/o P625; every later
run gives 11 and 0 ids dropped from the batch response. The new part prefetch re-fetches ids missing
from a batch response (one-line insurance; the batched shape stays).

**Census of the 280 plain-none rows (kept from iter 14; dump regenerable from data/commons/files.jsonl
with kind==none and no conflict):**
- york-castle 40 "Clifford's Tower Survey" -> part_mention PASS (measured 6 m).
- argentoratum 39 Strasbourg maps (site coords ARE Strasbourg; catalog aliases are Roman-only) ->
  sheet_mention PASS if "Strasbourg"/"Straatsburg" resolves nearby.
- durocortorum 4 (Reims/Rheims maps) + 1 junk; cenabum 5 (Orleans maps) + 13 New-Orleans JUNK (~8000 km
  -> CONFLICT none); bethlehem 32 all JUNK on the NETHERLANDS Bethlehem Q2523914 (12 Palestine surveys,
  Maastricht maps, Mount Airy/Germantown, "BethleemPlan" names Bethleem Q16489 - all far -> CONFLICT).
- Small genuine (1-2 rows): fletio/Weesp ~19, duno/Arnhem ~9, castrum-levefanum/"Peutinger Casaromago"
  desc names Beauvais (same file on fletio ~440 km -> must stay none THERE: per-site verdicts),
  badbury-rings/Cranbourne ~15, barnard-castle/Darlington ~29 + "Alnmouth Tithe Map" ~98 (CONFLICT),
  barkhale/"Barkhale camp plan" (title names the site itself, shortened), blestium/Monmouth ~23,
  cahokia/"...city of St. Louis... Sugar Loaf" ~12, mamucium/Manchester ~0.8, noviomagus/Nijmegen ~1.7,
  dudley/Birmingham ~13 (also Bristol/Newport Pagnell junk -> far), fotheringhay/Peterborough ~62
  (CONFLICT), offa-s-dyke 3x/Chirk ~57 from the stored end (CONFLICT, no special-casing), gondole/Venice
  far, dunster/Boughton ~310, crayke/York ~69, stonehenge+glevum+norwich/Bristol far.
- The rest (~180): IA book scans, seed catalogues (arbeia 28), Bowes-Museum paintings (barnard ~34),
  Naturalis specimens, newspaper/diary clippings - name NO place near the site; stay plain none (correct).

**Design (final, implement in fit/evidence.py - Touches stays one module):**
1. New kinds `part_mention` and `sheet_mention`, stored with the caption_coords shape ({named_place,
   place_qid, place_label, place_lon, place_lat, site_lon, site_lat, dist_m}; part_mention adds
   part_qid). check(): add both to the whitelist; check_part/check_sheet mirror check_caption (caption
   still names the phrase, norm substring of title+desc; distance reproduces within 1000 m; <=50 km)
   plus: check_part verifies part_qid is in the catalog site's has_part qids (re-derived from the
   catalog file at check time).
2. Candidate extraction (deterministic, title + first ~600 chars of desc): split on non-letters AND
   case/digit boundaries ("Maastricht1749LarcherDAubencourt2" -> Maastricht/Larcher/Aubencourt); keep
   capitalized words len>=3; drop all-caps (acronyms: HMS, BHL, KB, PPN, DPLA, NARA, IA, NT, OSD, RMNH,
   WAPAMA, WILLIAM...); drop the STOP list of non-place capitalized words (The A An In Of De Van La Le
   Plan Plans Atlas Survey Ordnance Drawings Sheet One-inich Published Map Carte Plattegrond
   Reproductie Identificatie Titel Objecttype Objectnummer Vervaardiging Vervaardiger Sujet Echelle
   Couverture Langue Editeur Appartient...); keep a leading word only if the 2nd is also a kept word;
   merge runs into phrases of <=3 words; <=12 candidates per row in order of appearance.
3. Prefetch (one shape, batched, paced): ctx["part_coords"] = {qid: (label, lon, lat|None)} for the part
   qids of the sites appearing in the pending rows (one batched wbgetentities, re-fetch dropped ids);
   ctx["places"] = resolve_places(named-site-names UNION sheet candidates) - one search per unique
   name, one batched claims fetch (the existing function, unchanged shape).
4. live_evidence (refactor FIRST, per the 50-line rule): extract the caption-route block into
   _caption_route(row, slon, slat, res); add _part_route (caption names a has_part of the site by norm
   substring; coords = part P625, else the site's own) and _sheet_route (a sheet candidate resolves
   <=50 km); route order: category -> depicts -> caption -> part -> sheet -> none. A far resolution
   (any route) stores kind none WITH the conflict (existing mechanics); only write a conflict when the
   resolution is still >50 km (check FAILs a stored conflict that no longer conflicts). Plain none's
   reason lists the routes tried.
5. record: add `--redo-none` (only with --live): rows with stored kind == "none" re-run the full live
   route; all other recorded rows untouched (set_field keeps bytes). Plain `record` (no --live) must
   print EXACTLY "evidence recorded: N hand-tied, N book, N live" - test_record asserts the exact string
   and runs without --live. --redo-none output may differ (manual run).
6. check(): add the two kinds to the whitelist + checkers; update the module docstring's kind list and
   the header comment (CODEMAP regenerates from it). Golden (tests/golden/evidence_check.txt): the
   sample rows carry no new kind -> check output over the sample stays byte-identical; do NOT
   regenerate; row count stays 1490.

**Exact next step:** (1) offline prototype of the candidate extractor over the 354 none rows (no
network): print unique candidate count + the per-row candidates, eyeball 20 rows against the census;
(2) run the live resolution (commons.get at 1 req/s; a few hundred unique names = a few minutes - let
it run, dump the per-row verdicts to /tmp/sheet_verdicts.txt) and compare with the census; (3) implement
in fit/evidence.py (refactor-first commit, then the routes, then --redo-none); (4) run
`record --live --redo-none` on the real files (diff before/after: ONLY the 354 none rows' evidence
field may change), then `check` (must exit 0, 1490 rows, no FAIL; the 74 existing conflicts re-verify),
then the 12/12 suite via .venv/bin/python -m pytest -q; (5) if passes land below a majority of the
~85-90 genuinely-naming rows, log why in DECISIONS before relaxing anything.

**Gotchas:** .venv works (PIL importable) - run everything through .venv/bin/python; the driver's
requirements.txt note is agent a's task 800 - do NOT touch requirements.* (not in my Touches). Tests
never touch the network (record --live is a manual pipeline run); no fixed ports, no writes outside
the project/temp dir (other agents' branches test concurrently); never rebase/merge (driver handles
branches); the 74 existing conflict rows must keep re-verifying - re-recording must only store a
conflict when the resolution is still >50 km; set_field preserves the line terminator; the record test
asserts the exact plain-record stdout string.
