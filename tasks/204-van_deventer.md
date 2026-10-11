Status: in-progress
# 204: Van Deventer - the remaining town plans (c. 1550s)
Depends on: 200
Touches: fit/src_van_deventer.py, data/catalog/extras_van_deventer.jsonl, data/commons/files_van_deventer.jsonl, data/commons/classified_van_deventer.jsonl, docs/lead_van_deventer.md, tests/test_src_van_deventer.py

## Goal
GOAL.md point 4: Jacob van Deventer's town plans, drawn c. 1545-1565 for Charles V and Philip
II. The Commons category "Maps by Jacob van Deventer" holds about 70 town categories; six are
already hand-tied in pipeline/sources.py (including the hand-fitted Bergues), leaving ~64 towns
not on the map yet. For each: verify the Wikidata item by hand (a name search alone gives the
wrong place - the Barnard Castle trap), tie the picture with machine-checkable evidence (200),
and stage the catalog entry and the picture rows in this task's own staging files. 211
consolidates the staging into the canonical files and builds the sites.

## Acceptance criteria
- [ ] Verified before use (docs/lead_van_deventer.md): the Commons category exists and its
      town list is recorded; every staged picture is a Van Deventer plan (the drawing's date
      c. 1545-1565 is recorded on the row - where Commons only has an upload date, the known
      drawing date is used and noted); unusable files (photos, modern reprints, too small) are
      listed with the reason, not staged.
- [ ] The hand-checked file -> QID table lives in fit/src_van_deventer.py (the sources.py
      pattern): every QID verified against its label and coordinates, with the town-centre
      lon/lat recorded on the row, not just the municipality point (Gouda misses by up to
      800 m). Towns whose QID cannot be verified are listed in docs/lead_van_deventer.md with
      the reason.
- [ ] Staged rows: extras_van_deventer.jsonl (one entry per new town: id, name, place,
      lon/lat of the old town, region, kind "town", QID, wikipedia) and
      files_van_deventer.jsonl (one row per staged picture, in the files.jsonl shape, with the
      200 evidence field - P373 category / P180 / caption+coords - and a classified row "plan"
      by hand). fit/evidence.py check passes offline on every staged row.
- [ ] No duplicate sites: a town whose QID is already in the catalog gets its picture row for
      that existing site id, no new catalog entry.
- [ ] At least 50 of the ~64 towns are staged, or docs/lead_van_deventer.md accounts for each
      missing one with a verified reason (a documented drop beats a guessed row).
- [ ] Test (no network): the staged files join (every file row names a staged or existing
      site; every new catalog entry has at least one picture) and the evidence check passes;
      a golden sample of rows.

## Notes
- The six already hand-tied towns are NOT re-staged here (their rows exist in the canonical
  files via sources.py); this task is the remaining ~64.
- If the work grows past a few sessions: split into subtasks 204a-... by country
  (Netherlands / Belgium / France / Germany + other), ~16 towns each, same shape of boxes per
  subtask (each with its own extras_/files_/classified_ staging files suffixed by the
  subtask, e.g. files_van_deventer_a.jsonl, and its own docs/lead_van_deventer_a.md); record
  the town list per subtask in this parent's hand-over. 211 consolidates whatever staging
  files exist.

## Hand-over
(2026-10-11, iteration 50 - **FR+LU re-verify DONE (clean) and lead doc updated; all committed**). The
iter-49 TOWNS edit arrived already driver-committed (6b8f85a); parse-check passed (66 towns, 32 stageable).
The 23-town re-verify run was clean: every label matches, every P373 ok, every enwiki matches, first hit
with P625 = the recorded QID for all 23, P625→site 0.00-0.01 km everywhere except Le Rœulx 0.91 km (rounded
item-P625 offset, explained in the doc). Bergues (done) re-confirmed (Q244934, P625 2.434167, 50.968611 →
site 0.00 km, P373 'Bergues', enwiki 'Bergues'). Lead doc now has: Commons counts BE 23 / FR 23 (Le Rœulx
moved), the Belgium section with Le Rœulx's row, and the full '## QID verification - France, Luxembourg'
section (method, the 3 prep-list changes incl. Luxembourg City = Q1842 not Q1564 and Beaumont pending, the
23-row table, the name-search traps). PITFALLS: the parentheses-search quirk filed. Tests green (38 passed).

**State of the table (verify any doubt with `python3 -c "import sys; sys.path.insert(0,'fit'); import
src_van_deventer as m; print(len(m.TOWNS), len(m.stageable()))"` - expect 66, 32):**
- TOWNS: NL 19 (13 staged + 3 drops + 3 done), BE 23 (20 staged incl. Le Rœulx's entry + Aarschot drop +
  2 done), FR 23 (21 verified QIDs + Beaumont pending + Bergues done), LU 1 (Q1842 verified).
  `stageable()` = 32 (NL 13 + BE 19). FR/LU + Le Rœulx have no file= yet, so stage still runs only after
  the --files picks.
- Staging files (extras_/files_/classified_van_deventer.jsonl) hold only the 32 NL+BE rows; FR/LU/Le Rœulx
  rows come after the --files batch. No staging file has been created for Beaumont.
- Beaumont: TOWNS keeps region="france" + note= pending. The --files run (desc/eye check of its 1545 BNE
  atlas plate) settles Hainaut (Q95100, on the Sambre at the French border) vs Nord (inland near Seclin);
  if Hainaut wins, region flips to belgium and QID=Q95100 (then re-verify it once, as its own fact sheet).
- Box 5 math: 32 of 60 stageable categories staged (32 of 59 town plans). >= 50 still needs >= 18 more
  stages (or documented drops for each gap) - the FR/LU file batch decides it.

**EXACT NEXT STEP (one session, one long run):**
1. The FR/LU --files batch (same shape as the BE iter-46 run):
   `.venv/bin/python fit/src_van_deventer.py --files "Aire-sur-la-Lys" "Arras" "Avesnes-sur-Helpe" "Bapaume"
   "Bavay" "Beaumont" "Bouchain" "Béthune" "Cambrai" "Condé-sur-l'Escaut" "Douai" "Gravelines" "Hesdin"
   "Landrecies" "Le Cateau-Cambrésis" "Le Quesnoy" "Le Rœulx" "Lille" "Maubeuge" "Saint-Omer" "Thérouanne"
   "Valenciennes" "Vieil-Hesdin" "Luxembourg City" > /tmp/vd_files_fr_iter50.txt`
   (24 towns: the 22 FR to stage incl. Beaumont + Le Rœulx + Luxembourg City; expect the 1545 BNE atlas
   plates as the picks, per the collection section; all names quoted - the Le X unquote trap).
2. Eye-check the ambiguous candidates (1200 px thumbs + full-size crops via commons.info + aw.UA, then the
   `read` tool views images): the double plates `Aire-sur-la-Lys - Deventer.jpg` (3395x2614, "Aire-sur-la-Lys
   & Thérouanne") and `Hesdin - Deventer.jpg` (3408x2614, "Hesdin & Vieil-Hesdin") - pick the true primary
   (stage ONCE; the second gets its own row only if a full plan of its own exists); Beaumont's plate decides
   Hainaut vs Nord; Luxembourg City (KBR / National Library scan expected; the Landrecies atlas subcat's 5
   KBR details, 1091-1805 px, are the fallback if its town-category file is weak).
3. Record the picks in TOWNS (file=/date=/caption= + note= per town; the c. 1545-1565 window gates the date,
   the Aarschot 1570 precedent), update the lead doc's per-town FR/LU bullets, then the ONE long run:
   --chain per newly staged town, `stage` (NOT --dry), `--check`, then write tests/test_src_van_deventer.py
   (pattern: tests/test_src_artists.py - the socket-blocking no_network fixture, check_staged(), subprocess
   `fit/evidence.py check --files ... --books <absent path>`, golden sample, negative control; the box-6
   date rule: year_of of every staged row's date in 1545-1565), `--golden`, full pytest.

**Pitfalls (all in PITFALLS.md):** (1) the trailing-comment-in-unbalanced-braces rule for EVERY TOWNS edit;
(2) wbsearchentities limit=5 misses well-known short names - follow up at limit 20/50; (3) raw Wikimedia
API calls need the aw.UA User-Agent or they 403; (4) a wbsearchentities label search containing parentheses
returns EMPTY (this session's filing - the 'Luxembourg (city)' case). Team mode: agent c on 203b
(fit/batch_eu.py, data/db/platefits, data/review, docs/batch_eu.md, tests/test_batch_eu.py) - untouched.
My Touches: fit/src_van_deventer.py, the 3 staging jsonl (created by stage), docs/lead_van_deventer.md,
tests/test_src_van_deventer.py, tests/golden/src_van_deventer_sample.json, plus this task file.
