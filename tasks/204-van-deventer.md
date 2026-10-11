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
(2026-10-11, iteration 44 - module fix + lead-doc NL/collection sections written; the module and doc changes
are in the working tree, harness-saved (commit them with your first edit); DECISIONS/PITFALLS/hand-over are
committed; next: the BE batch)

**Written this session** (`fit/src_van_deventer.py` + `docs/lead_van_deventer.md`, in the working tree): stage() now applies the
date/date_commons swap BEFORE commons.keep() (the sources.py pattern; the old order dropped the Sluis and
Valkenburg 1980 RCE reproductions on their scan year - the done Zwolle row, date "circa 1560" /
date_commons "1980", is the template that proved the intended behavior). Rotterdam TOWNS comment corrected
(page date = the year-1563 field, one year of the drawing's 1558-1563 window - not an upload timestamp).
Lead doc fully written for NL: Per-town section (13 staged with file/size/row-date and the not-staged
candidates named briefly; 3 drops with reasons - Groningen province = province map, Leeuwarden = 1975
redrawn model, Middelburg = stadhuis detail crop only; the R5 Damme misfiled in the Sluis cat); The
collection categories section (BNE 61 / NA 2 / RCE 69 / Atlas 6, counts verified against the iter-43
transcript); category section records the re-runs; Summary carries the NL subtotal (13 of 16 staged, 3
documented drops) and stays (pending) until all 60 are in. PITFALLS.md: new pipeline/commons.py section on
the keep()/swap order.

**Verified this session (run, not reasoned):** `stage --dry` -> "staged: 13 new sites, 13 new pictures"
(13 slugs + build list; transcript /tmp/vd_stage_dry_iter44.txt); `--check` exit 0 (the 3 staging files still
absent - joins empty, 0 evidence rows); pytest 33/33; `--list` passed again (fifth live run of 2026-10-11,
after the town_files extension). The staging jsonl files are created only by a non-dry `stage`.

**Transcripts** (/tmp may be wiped - re-run the commands): /tmp/vd_files_nl_iter43.txt (--files over the 16
NL towns + 4 collections, 217 lines, ~2 min at 429 pacing) is the source of every lead-doc fact this
session; /tmp/vd_verify_iter41.txt (the 22-town re-verification); /tmp/vd_list_iter44.txt (--list).

**Next step - the BE batch** (previous hand-over step 3, unchanged):
1. `.venv/bin/python fit/src_van_deventer.py --verify <the 20 BE towns>` (discovery mode: search candidates
   with P625/P373/P131/enwiki; record qid/label/lon/lat/p625/place/wikipedia/p373 per town in TOWNS). The 20
   = Ath, Braine-le-Comte, Bruges, Brussels, Chimay, Chièvres, Enghien, Ghent, Halle, Kortrijk, Lessines,
   Leuze, Mechelen, Mons, Ostend, Saint-Ghislain, Soignies, Tournai, Aarschot, Oudenaarde (the TOWNS table;
   the done Damme/Binche stay out). Ghent Q1296 is ALREADY verified in prep - record it as is (the lead doc's
   pending section says so). Beaumont's TOWNS region is the `france` guess; it flips to `belgium` if the
   verified item is the Hainaut one (the Barnard-Castle-style trap - check label + P373 + enwiki, never the
   first search hit).
2. Then `--files <same 20>`: the BNE atlas 1545 plates are the expected picks (16 of the 20 are in BNE:
   Ath, Braine-le-Comte, Chimay, Chièvres, Enghien, Ghent, Halle, Kortrijk, Lessines, Leuze, Mons, Ostend,
   Oudenaarde, Saint-Ghislain, Soignies, Tournai) - Bruges, Brussels, Mechelen and Aarschot must come from
   their own town categories. Record the picks in TOWNS (file=, +date= where the page date is not the
   drawing's), write the lead-doc BE per-town bullets + the BE subsection of the QID-verification section
   (the "pending" section grows per batch), commit.
3. Then FR (23 towns: the BNE plates cover all of them; watch the Aire+Thérouanne and Hesdin+Vieil-Hesdin
   double plates - one file, two towns: stage once under the true primary town, note the second), then
   Luxembourg City (search "Luxembourg (city)", Q1564 expected, region `luxembourg` - no REGION_NAME key,
   the display fallback is noted in the lead doc).
4. Then the one long run (unchanged from iteration 42): `--chain <town>` per staged town (depth cap 6;
   paste the printed JSON list into TOWNS["chain"]; for towns whose picked file sits in a collection cat,
   record `filecat` = that cat - cat_chain starts from filecat), then `stage` (NOT dry), `--check`, write
   `tests/test_src_van_deventer.py` (pattern tests/test_src_artists.py: socket-blocking fixture,
   check_staged, subprocess `fit/evidence.py check --files ... --books <absent>`, golden sample via
   --golden, negative control; box-6 date rule: year_of of the row date must land in 1545-1565 - "circa
   1545-1565" parses to 1545, "circa 1560" to 1560) and `--golden`. If a batch overruns the session budget,
   split per the task Notes (204b BE / 204c FR / 204d LU, per-subtask staging files) - note the NL picks are
   already in the parent's TOWNS and its lead doc, so a split would only cover BE/FR/LU.

**Tests:** suite 33/33 green. tests/test_src_van_deventer.py not created yet; the 3 staging jsonl absent
until the first non-dry stage().

**Pitfalls:** the keep()/swap-order trap is now filed (new pipeline/commons.py section in PITFALLS.md). The
existing ones still apply (trailing-comment-joins-lines - each TOWNS comment starts on its own line inside
dict(...) calls; Wikimedia 429 + Retry-After via commons.get; check_category is shape-only so the walk is
the verification). Team mode: agent c on 203a (fit/batch_us.py, data/db/platefits, data/review,
docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256, tasks/802-*, tasks/803-*) -
untouched; my Touches: fit/src_van_deventer.py, the 3 staging jsonl, docs/lead_van_deventer.md,
tests/test_src_van_deventer.py.
