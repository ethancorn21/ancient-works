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
(2026-10-11, iteration 42 - lead doc written: category census + NL QID section + NL traps; next: close the
town_files collections gap, then the NL file inventory.)

**Where I am.** `docs/lead_van_deventer.md` now holds all the verified material so far: (1) the category
section (name/URL, 70 = 66 town + 4 collections, the --list assertion note, all 66 town categories listed by
country with the 6 done marked, the 4 collection names); (2) the NL QID table (16 rows: QID/label/P625/
site-point/distance/enwiki; distances from the iter-41 transcript /tmp/vd_verify_iter41.txt - if it is gone,
re-run --verify, 28 s; all <= 0.74 km, labels and P373 clean, the 3 done NL towns re-confirmed); (3) the
three NL name-search traps with measured distances (Sluis Q2065987 9.0 km SW / Reimerswaal municipality
Q10078 9.1 km / Valkenburg modern Q9771 0.14 km). Four sections are marked (pending): BE/FR/LU QID batches
(Ghent Q1296 already verified in the prep - record with the BE batch; Beaumont's region flips to belgium if
the verified item is the Hainaut one; Luxembourg City Q1564 expected, region value luxembourg has no
build_catalog.REGION_NAME key - the line-91 fallback to the raw value, confirmed in the doc), per-town file
picks/drops, the collection categories, the summary (box 5: >= 50 of 60 staged or each missing one
accounted). `fit/src_van_deventer.py`: this session only fixed two stale TOWNS section-header counts
(BE 22 = 20 to stage + 2 done, FR 24 = 23 + 1; the comments had said 21/19 and 25/24) - everything else is
as of iteration 41 (module functions, NL table re-verified, 4 bug fixes). The live `--list` passed AGAIN this
session (70 = 66 + 4, the third live confirmation).

**GAP (next session's first act): town_files() lists only the towns' own categories - the 4 collection
categories are NOT covered (the prep §2.1 spec had them in).** Needed for the lead doc's collections section
and the R5 misfiled-file mapping (a file that lives in a collection cat but belongs to a town - the old prep
saw the Sluis town cat holding a "Damme" file). Fix: extend town_files() with a COLLECTIONS block (c.members
per collection cat; the BNE atlas at depth 1 - list its subcats, then their files, R4). Small change, keep
the towns' output format, stdlib top + lazy imports as the module already has.

**Next step (exact):**
1. Close the gap (above): add the collection inventory to town_files; re-run --list first (2 calls, keeps
   the census fresh).
2. `.venv/bin/python fit/src_van_deventer.py --files <the 16 NL towns>` (the 16 = every non-done NL TOWNS
   key: Aardenburg Alkmaar Amsterdam Enkhuizen Goes Groningen "Groningen (province)" Haarlem Leeuwarden
   Middelburg Reimerswaal Rotterdam Sluis "The Hague" Utrecht Valkenburg) plus the collections from step 1.
   Hand-pick the one best full plan per town (a detail crop / photo / modern reprint / <~1000 px -> a
   documented drop in the lead doc's (pending) "Per town" section, replacing the placeholder); record each
   pick as TOWNS[...]["file"] and the drawing date as TOWNS[...]["date"] (stage() swaps a scan whose page
   lost the drawing's date into date_commons). R5: watch the "[also in:]" notes for misfiled files - stage
   once under the true town, note every anomaly in the lead doc.
3. Then the BE batch (20 towns incl. recording Ghent Q1296; Beaumont's BE-vs-FR settles here), then FR (23),
   then Luxembourg City (1: search "Luxembourg (city)", Q1564 expected).
4. Then the one long run: --chain per town (depth cap 6; paste the printed JSON via list into TOWNS["chain"])
   + stage() + --check + tests/test_src_van_deventer.py (pattern = tests/test_src_artists.py: socket-blocking
   fixture, check_staged assertions, subprocess fit/evidence.py check --files, golden sample, negative
   control) + --golden. If a batch overruns the session budget, split per the task Notes (204a NL / 204b BE /
   204c FR / 204d LU) with per-subtask staging files files_van_deventer_<x>.jsonl etc. (the module stages
   whichever towns are verified; a split is a hand-over + filenames change, and this parent's Touches line
   grows with the subtask files).

**Tests:** none of mine yet (tests/test_src_van_deventer.py is in my Touches; the 3 staging jsonl files do
not exist yet - created by stage()). Suite 33/33 green this session (comment-only module change).

**Pitfalls:** filed in PITFALLS.md: Python trailing-comment-joins-lines (iter 41, bit on the Sluis TOWNS
row), dict.update 2-tuples (iter 40), Wikimedia 429 + Retry-After via commons.get (iter 40), and
check_category re-verifies only the SHAPE of the stored chain (the walk is the verification: paste only the
cat_chain JSON list into TOWNS["chain"] - a " -> " string or a skipped hop passes check but is a lie).

**Environment:** .venv OK. Team mode: agent c works 203a in its own checkout (fit/batch_us.py, data/db/
platefits, data/review, docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256,
tasks/802-*, tasks/803-*) - do not touch its files; my Touches are only this task's (module + 3 staging
jsonl + lead doc + test).
