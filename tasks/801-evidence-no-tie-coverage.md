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

**Where I am (iteration 14, agent c).** No code written yet - this session was the census + design
step. I read fit/evidence.py end to end, books_match.py, the test + golden, the harvest in
pipeline/commons.py, and reviewed all 280 plain-none rows individually (dump at /tmp/no_tie_rows.txt,
generated from data/commons/files.jsonl; regenerate with the same filter if lost).

**Census of the 280 plain-none rows (per site):**
- york-castle 40: "Clifford's Tower Survey (...)" photos, desc "...on site at Clifford's Tower...";
  Clifford's Tower is a has_part of the site (Q113551546).
- argentoratum 39: old maps of Strasbourg (titles "1831. Strasbourg...", "Strasbourg-Krutenau-Plan de
  1852 (N)", "Plan de Strasbourg...", "Plattegrond van Straatsburg..."). Site coords (7.751, 48.5827)
  ARE Strasbourg; catalog aliases are Roman names only, so the full-name caption route never fires.
- durocortorum 4 (Reims/Rheims maps; site coords = Reims) + 1 junk; cenabum 5 (Orléans maps; site coords
  = Orléans) + 13 New-Orleans junk rows (DPA photo, "Prospect EveryOne - NoLA", Gunn diaries, Spanish
  planos) - the NoLA rows resolve ~8000 km away -> should become CONFLICT none.
- bethlehem 32: catalog site is a NETHERLANDS Bethlehem (Q2523914, 6.61, 53.38 - NOT the Holy Land). The
  12 "Survey of Palestine" sheets, the Maastricht detail maps, the Mount Airy/Germantown (Philadelphia)
  rows and the "Bethléem basilique" plan are all mis-harvests (Commons search on "Bethlehem"); all
  resolve far -> conflict none. (Note: row "BethleemPlan.png" desc names "Bethléem" = Q16489, far.)
- Small genuine ties (1-2 rows each): fletio/Weesp (~19 km), duno/Arnhem (~9 km),
  castrum-levefanum/"Peutinger Casaromago" desc "centered on Casaromago (beauvais)" (Beauvais ~ the site;
  the SAME file sits on fletio too -> ~440 km -> must stay none there: per-site verdicts),
  badbury-rings/"Ordnance Survey Drawings - Cranbourne, Hampshire (OSD 65)" (~15 km),
  barnard-castle/"Ordnance Survey One-inich Sheet 14 Darlington" (~29 km) and "Alnmouth Tithe Map" (~98 km ->
  conflict), barkhale/"Barkhale camp plan and excavations" (title names the site itself, shortened),
  blestium/"Monmouth Castle - architectural details" (~23 km), cahokia/"Leffingwell's map of the city of
  St. Louis... Sugar Loaf Mound" (~12 km), mamucium/"Beyer... Gorton Foundry... Manchester" (~0.8 km),
  noviomagus/"Glass pisspot... found in Nijmegen" (~1.7 km), dudley/"Plan of Birmingham by Thomas Hanson"
  (~13 km; also Bristol/Stoke Gifford/Newport Pagnell junk -> far), fotheringhay/Peterborough (~62 km ->
  conflict), stonehenge/Bristol rows (far), glevum/Bristol (far), norwich/Bristol (far),
  dunster/Boughton House (~310 km far), crayke/"...Cathedral Church of St. Peter, York" (~69 km far),
  offa-s-dyke 3x/"Chirk Castle, NT, Chirk, Clywd, Wales" (Chirk ~57 km from the site's point - the site
  stores the Dyke's southern end; expect conflict-none, do not special-case), gondole/Venice rows (far).
- The rest (~180): Internet-Archive book scans (desc = book metadata), seed catalogues (arbeia 28),
  Bowes-Museum paintings (barnard ~34), Naturalis specimens, newspaper/diary clippings - they name NO
  place near the site; they stay plain none (that is correct, fail-closed).

**So: ~85-90 rows genuinely name the site (site's modern city, a has_part, or a shortened site name);
planned passes ~80 of them if resolutions come back as expected - a majority, box 1. Another ~50 junk
rows should gain a stored CONFLICT (box 2's explicit ask).**

**Design decided (implement in fit/evidence.py next session, keep it one module - Touches stays):**
1. Two new kinds, same storage shape as caption_coords (`named_place, place_qid, place_label,
   place_lon, place_lat, site_lon, site_lat, dist_m`; part adds `part_qid`):
   - `part_mention`: caption names a has_part of the site (norm substring, like named_places_in); the
     part's item (has_part qid from the catalog) has P625 within 50 km. CHECK: **does Q113551546
     (Clifford's Tower) actually carry P625?** If not, those 40 rows fail-closed stay none - measure
     first, then decide (do not invent a looser substitute without logging it).
   - `sheet_mention`: a proper-noun place phrase from the caption resolves (search + batched claims) to
     within 50 km of the site coords (catalog lon/lat, else item P625, else skip).
2. Candidate extraction (deterministic, title + first ~600 chars of desc): split on non-letters AND on
   case/digit boundaries ("Maastricht1749LarcherDAubencourt2" -> Maastricht/Larcher/Aubencourt,
   "BethleemPlan" -> Bethleem/Plan); keep capitalized words len>=3; drop all-caps words (acronyms:
   HMS, BHL, KB, PPN, DPLA, NARA, IA, NT, OSD, RMNH, WAPAMA, WILLIAM...); drop a STOP word-list of
   non-place capitalized words (The, A, An, In, Of, De, Van, La, Le, Plan, Plans, Atlas, Survey,
   Ordnance, Drawings, Sheet, One-inich, Published, Map, Carte, Plattegrond, Reproductie, Gezicht?,
   Identificatie, Titel, Objecttype, Objectnummer, Vervaardiging, Vervaardiger, Sujet, Echelle,
   Couverture, Langue, Editeur, Appartient...). Leading word kept only if the 2nd word is also a kept
   capitalized word ("Maastricht1749..." keeps, "The history..." drops). Merge runs into phrases of
   <=3 words; per row keep <=12 candidates in order of appearance. Global unique set -> ONE
   wbsearchentities per name + ONE batched claims fetch (resolve_places shape, reuse it) + one batched
   claims fetch for all has_part qids.
3. Verdict per row (live_evidence, after the existing category/depicts/caption routes): nearest
   <=50 km resolution wins -> part_mention or sheet_mention; else nearest far resolution ->
   kind "none" with the conflict stored (existing mechanics); else plain none (reason updated to say
   the sheet/part routes were tried).
4. record CLI: add `--redo-none` (with --live): rows whose stored kind == "none" re-run the full live
   route; all other recorded rows untouched (byte preservation holds - set_field is the existing
   mechanism). Plain `record` (no --live) output stays EXACTLY "evidence recorded: ..." - the record
   test asserts it.
5. check(): add both kinds to the whitelist; checkers mirror check_caption (caption still names the
   place: norm substring; stored distance reproduces within 1000 m; <=50 km). Update the module
docstring kind list and header comment (CODEMAP regenerates from it).
6. Golden (tests/golden/evidence_check.txt): the sample files contain no new kinds -> check output over
   the sample stays byte-identical; do NOT regenerate. Row count stays 1490.

**Exact next step:** with `.venv/bin/python` (system python3 lacks PIL; books_match imports books which
imports PIL - run everything through .venv/bin/python): (1) fetch claims for Q113551546 + the
part-qids of all catalog sites (one batched wbgetentities) and confirm which have P625 near their
site; (2) prototype the extraction above over the 354 none rows, print the unique candidate count and
the per-row expected verdicts, run the live resolution (commons.get paces at 1 req/s, 429-safe; a few
hundred candidates = a few minutes), and compare with the census above; (3) implement in
fit/evidence.py (refactor live_evidence into small helpers first if it grows >50 lines), run
`record --live --redo-none` on the real files, then `check` (must exit 0, no FAIL, row count 1490,
only the 354 rows' evidence field changed - diff before/after), then the 12/12 suite (.venv/bin/python
-m pytest -q); (4) if the pass count lands below a majority of the ~85-90 genuinely-naming rows, log
why in DECISIONS.md before relaxing anything.

**Gotchas:** do not `pip install --break-system-packages`; tests must not touch the network (record
--live is a manual pipeline run, not a test); other agents' branches run tests concurrently - no
fixed ports, no writes outside the project/temp dir; never rebase/merge (driver handles branches);
the 74 existing conflict rows must keep re-verifying (their stored conflicts still conflict - check
re-derives distance; a stored conflict that no longer conflicts is FAIL, so re-recording must only
write a conflict when the resolution is still >50 km).