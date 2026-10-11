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
(2026-10-11, iteration 41 - module bug-fixed, NL table RE-VERIFIED clean; next: the lead doc.)

**Where I am.** `fit/src_van_deventer.py` (committed c58e127; this session fixed 4 fresh-eyes bugs, see
DECISIONS): TOWNS table of all 66 town categories (list_categories asserts the live 70-subcat list -
re-checked this session, still matches), COLLECTIONS (4), verify_qids (discovery/re-verification),
town_files, cat_chain (now returns the via list as JSON for pasting into TOWNS["chain"]), evidence_for
(category/caption_coords/None), stage, check_staged, golden, CLI. Stdlib-only top; run live commands
under .venv/bin/python.

**Verified (live, 2026-10-11):**
- `--list` PASSES (70 = 66 town + 4 collections).
- **The 16 NL towns are now RE-VERIFIED** (`--verify` no args, exit 0, 28 s; transcript
  /tmp/vd_verify_iter41.txt, re-run is cheap): all labels match, every P625 within 0.74 km of the
  recorded old-town point (Haarlem 0.74 / Amsterdam 0.68 / Leeuwarden 0.65 / Rotterdam 0.63 / Sluis 0.59 /
  Goes 0.49; the rest <= 0.33), all 16 P373 match the table strings, enwiki all match (Valkenburg
  Q100076 has none, recorded). The 6 done towns re-confirm the P373 pattern. Name-search traps recorded:
  Sluis -> Q2065987 (distinct item, no enwiki, 8 km SW, P373 'Sluis (city)' - noted on the TOWNS row),
  Reimerswaal -> municipality Q10078, Valkenburg -> modern town Q9771.
- Box 4 checked for NL: only the 6 done QIDs are in the 12575-site catalog; no NL collision yet.
  **Re-check per town when doing BE/FR/LU** (stage() reuses the existing site id automatically).

**NOT done yet:** the lead doc; town_files inventory (16 NL cats + 4 collections, BNE atlas depth 1, R4);
file picks (no TOWNS town has a "file" yet); the chain walks; staging; the test file; the BE/FR/LU QID
batches (Ghent Q1296 verified in the prep, still unrecorded in TOWNS - record it with the BE batch;
Beaumont's BE-vs-FR region settles in the BE batch).

**Tests:** none of mine yet (tests/test_src_van_deventer.py is in my Touches; pattern =
tests/test_src_artists.py: socket-blocking fixture, check_staged assertions, golden sample, negative
control). Suite 33/33 green after this session's module fixes.

**Next step (exact):**
1. Write `docs/lead_van_deventer.md`: (1) the category section (name/URL, 70 = 66 + 4, check date,
   the list_categories pass this session); (2) the NL QID table (town, QID, label, P625, recorded
   lon/lat, computed p625->site distance, check date 2026-10-11, enwiki) - take the distances from the
   /tmp transcript or re-run --verify (28 s); (3) the NL search-trap notes (the three above).
2. `.venv/bin/python fit/src_van_deventer.py --files <the 16 NL towns>` for the NL file inventory
   (~17 calls): hand-pick one file per town (best full plan; detail crops/photos/reprints too small ->
   documented drops in the lead doc; the misfiled-file "[also in:]" notes from R5 - the Sluis cat held a
   "Damme" file in the old prep: the true town's row gets it). Record picks as TOWNS[...]["file"] +
   drawing date (the file's DateTimeOriginal when it is the drawing's; else the known drawing date with
   date_commons noted - stage() does that swap).
3. Then the BE batch (19 towns incl. recording Ghent Q1296; Beaumont's country settles here: BE Hainaut
   vs FR - its region in TOWNS is still the "france" guess; flip it if the verified item is Hainaut),
   then FR (24), then Luxembourg City (1: search 'Luxembourg (city)', Q1564 expected - region value
   "luxembourg" has no build_catalog.REGION_NAME key: the display falls back to the raw lowercase value,
   the 213 "Italy"/214 situation - note it in the lead doc; a REGION_NAME key would be a follow-on task).
4. Then the one long run: chain walks (cat_chain per town, depth cap 6 - paste the printed JSON via list
   into TOWNS["chain"]) + stage() + check + test file + golden. If the QID batches overrun sessions,
   split per the task Notes (204a NL / 204b BE / 204c FR / 204d LU) with per-subtask staging files
   files_van_deventer_<x>.jsonl etc.; the module stages whichever towns are verified, so a split is a
   hand-over + filenames change, and this parent file's Touches line grows with the subtask files.

**Pitfalls:** all filed in PITFALLS.md this session: Python trailing-comment-joins-lines (new, bit me on the
Sluis TOWNS row), dict.update 2-tuples (iter 40), Wikimedia 429 + Retry-After (iter 40), check_category's
via contract (new - see the fit/evidence.py subsection).
- `check_category` re-verifies only the SHAPE of the stored chain: via[-1] == row's cat and file_cat not in
  via. The walk itself is the verification - a recorded chain that was never actually walked (or that skips
  the file category, or is a " -> " string instead of a list) passes check but is a lie. Paste only the
  cat_chain JSON list into TOWNS["chain"].

**Environment:** .venv OK. Team mode: agent c works 203a in its own checkout - do not touch its files; my
Touches are only this task's (module + 3 staging jsonl + lead doc + test). Staging files do not exist yet
(created by stage()).
