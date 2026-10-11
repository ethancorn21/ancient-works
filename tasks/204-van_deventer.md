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
(2026-10-11, iteration 49 - **FR+LU QID discovery DONE and TOWNS edited (edit uncommitted - the harness saved it for
you; parse-check the module FIRST)**: 22 of 23 FR QIDs + Luxembourg City recorded in TOWNS; Le Rœulx moved
france->belgium (its item is in Hainaut, Belgium); Beaumont stays PENDING the atlas-plate settlement. Lead doc
NOT yet updated; re-verify run NOT yet done; nothing committed yet (the module edit is the only uncommitted
change - verify it parses, then commit it with the lead-doc updates).

**State of the table now (re-verify with a one-liner importing the module if in doubt):**
- TOWNS: NL 19 (13 staged + 3 drops + 3 done), BE 23 (20 staged incl. Le Rœulx's new entry + Aarschot drop +
  2 done), FR 23 (22 verified QIDs, no file= yet + Beaumont pending + Bergues done), LU 1 (Q1842 verified,
  no file= yet). `stageable()` = 32 (NL 13 + BE 19) - FR/LU/Le Rœulx have no file= yet, so stage still runs only
  after the --files picks (the one long run).
- **This session's findings (all from /tmp/vd_verify_fr_iter49.txt - 24 towns, the discovery run - and
  /tmp/vd_lu_iter49.txt, the follow-up script still at /tmp/vd_lu_iter49.py):**
  - **Luxembourg City = Q1842, NOT Q1564** (the hand-over's guess): Q1564 now holds 'Borgfelde', Hamburg - that
    id was merged away. Q1842: label 'Luxembourg', P625 (6.13, 49.611389), P373 'Luxembourg City', P131 'Canton
    of Luxembourg', enwiki 'Luxembourg City'. The TOWNS search= key was "Luxembourg (city)" which returns EMPTY
    (parenthesized label search) - now set to "Luxembourg City" (hits Q1842 first).
  - **Le Rœulx is BELGIAN, not French** (the prep's FR-list guess was wrong): Q668861, enwiki lead "a city and
    municipality of Wallonia located in the province of Hainaut, Belgium", P131 Arrondissement of Soignies (same
    as Lessines/Soignies). Recorded in the BE section: site point (4.1116, 50.5036) = the precise P625 of its
    subdivision item Q21764574 (the recorded item's P625 (4.1, 50.5) is rounded; the re-verify will print ~1.06
    km for it - expected, explained in the lead doc). P373 is 'Le Roeulx' WITHOUT the diaeresis (exact string).
  - **Beaumont pending**: the en search top 20 holds only the Hainaut (Belgium) item Q95100 as plausible (P625
    4.2383, 50.2355, P373 'Beaumont (Hainaut)', enwiki 'Beaumont, Belgium'); the northern-France Beaumont (Nord)
    is ABSENT from the en top 20 (a follow-up at limit 50 or the fr search is needed if it wins). The TOWNS
    entry keeps region="france" + note= pending; the --files run (desc/eye check of the atlas plate: the Hainaut
    town sits on the Sambre at the French border, the Nord one is inland near Seclin) settles it; if Hainaut
    wins, region flips to belgium and the QID is Q95100.
  - **None of the 23 QIDs is in the built catalog** (checked live against the 12575-site catalog this session):
    all get new entries (box 4, no existing-site reuse).
  - Wikipedia URL convention confirmed percent-encoded (Apuol%C4%97, Las_M%C3%A9dulas in extras.jsonl) - the FR
    entries use it (B%C3%A9thune, Cond%C3%A9-sur-l%27Escaut, Le_Cateau-Cambr%C3%A9sis, Th%C3%A9rouanne, Le_R%C5%93ulx).
  - The first --verify attempt of this session failed locally with "unknown town 'Le'" (shell quoting: the Le X
    names were unquoted) - no API calls happened; the re-run with everything quoted succeeded (exit 0).

**EXACT NEXT STEPS (one session, in order):**
1. `python3 -c "import sys; sys.path.insert(0,'fit'); import src_van_deventer as m; print(len(m.TOWNS), len(m.stageable()))"`
   (expect 66, 32) - the TOWNS edit is uncommitted and has NOT been parse-checked (PITFALLS comment-glue rule:
   every new entry's dict must close with `),` before any comment; a dropped comma glues the next key).
2. Re-verify run (24 towns with a QID): `.venv/bin/python fit/src_van_deventer.py --verify "Aire-sur-la-Lys"
   "Arras" "Avesnes-sur-Helpe" "Bapaume" "Bavay" "Bouchain" "Béthune" "Cambrai" "Condé-sur-l'Escaut" "Douai"
   "Gravelines" "Hesdin" "Landrecies" "Le Cateau-Cambrésis" "Le Quesnoy" "Le Rœulx" "Lille" "Maubeuge"
   "Saint-Omer" "Thérouanne" "Valenciennes" "Vieil-Hesdin" "Luxembourg City" > /tmp/vd_verify_fr_recheck_iter49.txt`
   (Beaumont has no QID - omit it; it prints its candidates in discovery mode if listed). Expect: every label
   matches, every P373 'ok', every P625 near the site point (Le Rœulx ~1.06 km, explained), enwiki matches;
   note the "first hit with P625" trap lines for the lead doc.
3. Lead doc (docs/lead_van_deventer.md): (a) 'The Commons category' section: BE line 22->23 categories (add Map
   of Le Rœulx), FR line 24->23 (remove it); (b) 'QID verification - Belgium': add the Le Rœulx row to the table
   (+ method sentence: discovered in the FR batch, moved from the prep's France list); (c) REPLACE '## France,
   Luxembourg (pending)' with '## QID verification - France, Luxembourg (checked 2026-10-11 (iter 49); re-run
   with ...)': method, a 23-row table (22 FR + Luxembourg City: Town|QID|Label|P625|Site point|P625→site|enwiki
   from the re-verify distances), the Beaumont-pending paragraph (Q95100 the only plausible candidate; Nord item
   absent from en top 20; the plate settlement decides; region flips if Hainaut wins), and '### Name-search
   traps - France, Luxembourg' (Le Quesnoy: the Somme twin Q109413780 shares the exact label 'Le Quesnoy' -
   first hit was the right one; Lille: the Belgian Lille Q725235 candidate; Saint-Omer: Calvados Q844283 +
   Quebec Q3463075; Thérouanne: the river Q428296 in Seine-et-Marne; Bapaume: the Queensland one Q48807630;
   Beaumont + Luxembourg City as above; the parenthesized-search-empty quirk); (d) the per-town '### France,
   Luxembourg (pending)' subsection: QIDs now verified, file= pending the --files run (keep the double-plate
   watch items); (e) Summary: NL 13/16, BE 19/21 (Le Rœulx not staged yet), FR 0/22, LU 0/1 - running total 32
   of 60, box 5 unchanged.
4. Commit everything (module + lead doc): `204: FR+LU QID table recorded (22 FR + Luxembourg City Q1842; Le
   Rœulx moved to Belgium) + lead-doc section - ...`. File the PITFALLS entry then: a wbsearchentities label
   search containing parentheses returns EMPTY (the 'Luxembourg (city)' case; follow the prep's known quirk -
   search the unparenthesized form). The /tmp transcripts (vd_verify_fr_iter49.txt, vd_lu_iter49.txt) may be
   wiped - the lead doc carries the results.
5. **Following session - the FR/LU --files batch** (the step AFTER this one; same shape as the BE iter-46 run):
   `.venv/bin/python fit/src_van_deventer.py --files <24 FR/LU towns> > /tmp/vd_files_fr_iter50.txt`: the 1545
   BNE atlas plates cover all 23 FR towns (collections section) as `<Town> - Deventer.jpg`, (1)/(2) pairs for
   Arras/Douai/Lille/Saint-Omer/Valenciennes (pick the labelled wide sheet, the Mons pattern); the double plates
   (one file, two towns - stage ONCE under the true primary, the second gets its own row only if a full plan of
   its own exists): `Aire-sur-la-Lys - Deventer.jpg` (3395x2614) = "Aire-sur-la-Lys & Thérouanne", `Hesdin -
   Deventer.jpg` (3408x2614) = "Hesdin & Vieil-Hesdin" (French desc: Hesdin 1554-1575, Vieil-Hesdin
   "probablement 1545") - eye-check both (commons.info + aw.UA download, then the `read` tool views images) to
   pick the primary. Beaumont: the plate's desc/eye check settles Hainaut vs Nord (see the note in TOWNS).
   Luxembourg City: its file from the run (the KBR / National Library scan expected); the Landrecies atlas
   subcat (5 KBR details, 1091-1805 px) is the fallback if the town-category file is weak. Then record the
   file=/date=/caption= picks, the lead-doc per-town bullets, and run the ONE long run: --chain per staged town,
   stage (NOT --dry), --check, tests/test_src_van_deventer.py (pattern: tests/test_src_artists.py: the
   socket-blocking no_network fixture, check_staged, subprocess evidence.py check --files ... --books <absent>,
   golden sample, negative control; box-6 date rule: year_of of every staged row's date in 1545-1565), --golden.

**Pitfalls (all in PITFALLS.md):** (1) the trailing-comment-in-unbalanced-braces rule for EVERY TOWNS edit;
(2) wbsearchentities limit=5 misses well-known short names - follow up at limit 20/50 (this session: the FR
Beaumont absent from even the top 20 en search); (3) raw Wikimedia API calls need the aw.UA User-Agent or they
403 (commons.get sets it; the /tmp/vd_lu_iter49.py script does too); (4) the parenthesized-label search returns
EMPTY (file it this session, see 4). Team mode: agent c on 203b (fit/batch_eu.py, data/db/platefits,
data/review, docs/batch_eu.md, tests/test_batch_eu.py) - untouched. My Touches: fit/src_van_deventer.py, the 3
staging jsonl (created by stage), docs/lead_van_deventer.md, tests/test_src_van_deventer.py,
tests/golden/src_van_deventer_sample.json, plus this task file.
