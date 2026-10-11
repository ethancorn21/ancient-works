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
(2026-10-11, iteration 40, after the first working session - module built, NL batch QIDs hand-verified.)

**Where I am.** `fit/src_van_deventer.py` EXISTS (saved uncommitted by the harness - commit it with the next
step). It is the full module per tasks/prep/204.md: TOWNS table of all 66 town categories (list_categories
asserts the live 70-subcat list against it), COLLECTIONS (4), verify_qids (search + batched claims fact
sheet; discovery when a town has no qid, re-verification when it does), town_files (per-town file inventory
+ misfiled-file cross-listing), cat_chain (upward parent walk to the P373 category, depth cap 6),
evidence_for (category route from a recorded chain / caption route in 213's hand-recorded pattern /
None=drop), stage, check_staged, golden, CLI (--list --files --verify --chain stage --check --golden).
Stdlib-only module top; commons/evidence imported lazily (run under .venv/bin/python; system python3 can
import the top only).

**Verified so far (live, 2026-10-11):**
- `--list` PASSES: 70 subcategories == 66 town cats + 4 collections (the prep's 2026-10-10 list still holds).
- The 16 NL towns' QIDs are hand-checked and RECORDED in the TOWNS table (qid/label/lon/lat/p625/place/
  wikipedia/p373): Aardenburg Q955, Alkmaar Q972, Amsterdam Q727, Enkhuizen Q9918, Goes Q81220, Groningen
  (city) Q749, Groningen (province) Q752 (documented drop: province map, not a town - note= set, no file),
  Haarlem Q9920, Leeuwarden Q25390, Middelburg Q52101, Reimerswaal Q2590944 (the city item, not the
  municipality Q10078), Rotterdam Q34370, Sluis Q10080 (city, not BE Mol Q2289934), The Hague Q36600,
  Utrecht Q803, Valkenburg Q100076 (the OLD town, P373 'Valkenburg, Limburg'; the modern town is Q9771 -
  no enwiki on Q100076, so no wikipedia field). Every city item's P373 is its own town category (the
  category route works for NL).
- The 6 done towns (Gouda Q84125, Zwolle Q793, Venlo Q9777, Damme Q323408, Binche Q95121, Bergues Q244934)
  are in TOWNS with done=True - never re-staged.

**NOT done yet:** the re-verification run of the recorded table; the lead doc; town_files inventory (incl.
the 4 collection cats + BNE atlas subcats at depth 1, R4); file picks (the TOWNS "file" key is set for no
town yet); the chain walks; staging; the test file; BE/FR/LU QID batches (Ghent Q1296 was pre-verified in
the prep and is still unrecorded in TOWNS - record it when doing BE).

**Tests:** none of mine yet (tests/test_src_van_deventer.py is in my Touches; pattern =
tests/test_src_artists.py: socket-blocking fixture, check_staged assertions, golden sample, negative
control). The pre-existing suite was green per the driver before my session; I changed no existing file.

**Next step (exact):**
1. `.venv/bin/python fit/src_van_deventer.py --verify` (no args = re-verify the recorded table): read the
   per-town label/P625-distance/P373/enwiki lines and the first-search-hit trap lines; any MISMATCH/TRAP
   flag gets investigated (the distances >50 km are auto-flagged; the ~800 m old-town vs P625 offsets are
   the Gouda precedent and are recorded, not failures).
2. Write `docs/lead_van_deventer.md`: (1) the category section (name/URL, 70 = 66 + 4, check date, the
   list_categories pass); (2) the NL QID table with the p625 <-> site-point distances (compute them in a
   small .venv script with fit/evidence.hav_m from the table's lon/lat and p625 - do not eyeball them).
3. `.venv/bin/python fit/src_van_deventer.py --files <the 16 NL towns>` for the NL file inventory (~17
   calls), hand-pick one file per town (best full plan; detail crops/photos/reprints too small -> documented
   drops in the lead doc; the misfiled-file "[also in:]" notes from R5: the Sluis cat held a "Damme" file
   in the old prep - the true town's row gets it), record picks as TOWNS[...]["file"] + drawing date (the
   file's DateTimeOriginal when it is the drawing's; else the known drawing date with date_commons noted).
4. Then the BE batch (19 towns incl. recording Ghent Q1296; Beaumont's country settles here: BE Hainaut vs
   FR - its region in TOWNS is still the "france" guess), then FR (24), then Luxembourg City (1: search
   'Luxembourg (city)', Q1564 expected - region value "luxembourg" has no build_catalog.REGION_NAME key:
   the display falls back to the raw lowercase value, the 213 "Italy"/214 situation - note it in the lead
doc; file a REGION_NAME key task only if the owner cares).
5. Then the one long run: chain walks (cat_chain per town, depth cap 6) + stage() + check + test file +
   golden. If the QID batches alone overrun sessions, split per the task Notes (204a NL / 204b BE / 204c
   FR / 204d LU) with per-subtask staging files files_van_deventer_<x>.jsonl etc.; the module stages
   whichever towns are verified, so a split is a hand-over + filenames change, and this parent file's
   Touches line grows with the subtask files.

**Pitfalls found this session (file them in PITFALLS.md):**
- `dict.update(list_of_2_tuples)` builds {first: second} pairs - I wrote cands.update(_search_candidates(...))
  expecting {town: [candidates]} and got {qid: label} (crash "too many values to unpack"). Use a real dict
  of lists (fit/src_van_deventer.py:verify_qids, fixed).
- wikimedia commons.get 429s even at 1 s pacing after ~12 back-to-back calls (prep 1.3); it is
  Retry-After-aware, so just let it sleep - the 16-town --verify ran ~20 calls in ~1-2 min fine.

**Environment:** .venv OK (numpy 2.5.4 imports). Team mode: agent c works 203a in its own checkout - do not
touch its files; my Touches are only this task's (module + 3 staging jsonl + lead doc + test). Staging files
do not exist yet (created by stage()).
