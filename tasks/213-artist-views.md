Status: open
# 213: Artists' views - Leonardo's Imola, Barbari's Venice, Braun & Hogenberg, Merian
Depends on: 200
Touches: fit/src_artists.py, data/catalog/extras_artists.jsonl, data/commons/files_artists.jsonl, data/commons/classified_artists.jsonl, docs/lead_artists.md, tests/test_src_artists.py

## Goal
The new lead of GOAL.md point 5 (the 2026-10-10 change; the owner, of Leonardo's 1502
plan of Imola: "should 100% be on our map"): artists' aerial and bird's-eye views count
as drawings as much as surveys do. The sources to verify: Leonardo da Vinci's aerial
plan of Imola (1502, Royal Collection, RCIN 912284); Jacopo de' Barbari's view of
Venice (1500); Braun and Hogenberg, Civitates Orbis Terrarum (1572-1617, hundreds of
walled towns); Merian, Topographia (1640s-1680s). For each: verify it exists, is old
enough (views of the structure are exempt from the 150-year rule) and is freely
machine-readable; tie every picture with 200's machine-checkable evidence; stage the
rows in this task's own files. 211 consolidates and builds the new sites; 212's cover
pass runs the model's fitting loop over the staged pictures. Imola is the anchor: a new
site with no open LiDAR here, so it is an aerial-photograph site (FITKIT_GROUND=aerial)
and its streets carry the fit.

## Acceptance criteria
- [ ] Verified before use (docs/lead_artists.md): for each source, what it is, where its
      files live, the drawing's date (recorded on the row - where a repository only has
      an upload date, the known drawing date is used and noted), and exactly which files
      are staged; unusable sources or files (paywalled, too small, no place tie) are
      listed with the reason - a documented drop beats a guessed row.
- [ ] Imola staged as a new site: an extras_artists.jsonl entry (id, name, place,
      lon/lat, region, kind, QID, wikipedia), a files_artists.jsonl row for the plan in
      the files.jsonl shape with the 200 evidence field, and a classified_artists.jsonl
      row; the row notes no open LiDAR here (aerial-photograph ground,
      FITKIT_GROUND=aerial). fit/evidence.py check passes offline on every staged row.
- [ ] The hand-checked file -> QID table lives in fit/src_artists.py (the sources.py
      pattern): every QID verified against its label and coordinates - a name search
      alone gives the wrong place (the Barnard Castle trap); a picture of a site whose
      QID is already in the catalog gets a picture row for that existing site id, no new
      catalog entry.
- [ ] At least Imola plus one further source (Venice, one Civitates town, or one Merian
      view) is staged, or docs/lead_artists.md accounts for each unstaged source with a
      verified reason.
- [ ] If Civitates Orbis Terrarum or the Topographia turn out to be Internet Archive
      books indexable with pipeline/books.py, work in per-book files only
      (triage/<ia>.*, lists/<book>.json) and add those exact paths to this task's
      Touches line before writing them - never the shared index.jsonl or
      validation.json (211 rebuilds both).
- [ ] Test (no network): the staged files join (every file row names a staged or
      existing site; every new catalog entry has at least one picture), the evidence
      check passes on the staged rows, and a golden sample of rows is pinned.

## Notes
- Leonardo (Royal Collection, per GOAL.md) and de' Barbari are image-level leads like
  204-206 (one file row per view); Civitates and Merian are book-scale (hundreds of
  views). If this grows past a few sessions: split into subtasks 213a-... by source,
  each with its own staging-file suffix and docs/lead_artists_<source>.md; 211
  consolidates whatever staging files exist.
- Imola's aerial-photograph ground (Esri World Imagery, tools/fitkit.py) means the
  model's fit reads what has not moved: roads, the river crossing, church footprints -
  the feature pairs the sheet shows on both sides, not walls in relief.

## Hand-over
**Step 1 done (iteration 23, 2026-10-11): module + verified table + live checks.** `fit/src_artists.py` exists
(uncommitted, saved by the harness): SITES table (Q50195 Imola, Q641 Venice - QIDs verified live this session:
labels, enwiki, P373 'Imola'/'Venice', P131 provinces, P625 traps recorded), SOURCES (leonardo_imola: RCIN
912284 file; barbari_venice: Museo Correr file), BOOKS (civitates/merian IA ids), and verify_qids / stage / 
check_staged / golden with CLI `--verify` / `[--dry]` / `--check` / `--golden`. All smoke-tested under
`.venv/bin/python`: `--verify` clean (search traps confirmed: Imola -> Q50195's bad P625 53 km; Venice ->
Q773853 LA 9891 km); `--check` exit 0 (0 rows staged yet); `--dry` stages 2 sites / 2 pictures, both files
pass commons.keep(). File metadata verified live: RCIN 912284 = 2000x1483, NO DateTimeOriginal/desc, year
1502 from the title (so stage() fires no date/date_commons override; the row's `date` stays "" and `year`
1502 - note that in the lead doc), public domain; Correr Venice = 11800x5856, DateTimeOriginal 1500, public
domain. Task 214 filed (REGION_NAME "italy"->"Italy" + tests/test_region.py; the staged rows use region
"Italy" - built sites will show "US" until 214 lands, transient and fine). No acceptance boxes ticked yet.

**Next step - session 2: Imola (box 2, the anchor).** (1) Settle Imola's old-town centre: the table holds the
prep's placeholder (12.367, 44.245). The enwiki/Wikidata coords are the SAME bad value (P625), so pin the
centre from the drawing itself (the sheet shows the walled town + Savena crossing) or another reliable
geographic reference, and record the value + source in docs/lead_artists.md. (2) Triage the remaining Imola
candidates live (one paced commons.info run, record verdicts in the lead doc): File:Leonardo da vinci, Town
plan of Imola.jpg (possibly a third scan of the same sheet - check w/h/license); File:...RCIN 912686 (different
work: recto sketches - drop); File:Imola 1705.jpg (1705, not Leonardo - drop). (3) Stage: `.venv/bin/python
fit/src_artists.py` (stages BOTH sites' rows - that also stages Venice, which is correct; box 4 needs it);
then `--check` must pass with one PASS line per staged row (kind caption_coords). (4) Tick box 2 and box 3
(the table is done - QIDs verified, existing-QID rule in stage()/check_staged()).

**Then (plan, from tasks/prep/213.md):** session 3 Venice (box 4) - rows already staged with Imola; this is
the Venice-side documentation (NGA block files = detail crops - drop; GAp scan - drop; the R2 fit-scale
caveat: the woodcut spans ~8 km vs the 2000 m town box, the fit likely ends a review item in 212). Session 4
(stretch, box 5): Civitates/Merian book work - check IA metadata first (BookReader vs .pdf: 208's OQ-2 recipe
in its prep notes); per-book files (data/books/triage/<ia>.*, data/books/lists/<ia>.json) ONLY after adding
those exact paths to this task's Touches line (box 5); the books.py:BOOKS entry is a SHARED-module change ->
file a new task for it, never write it; scope = one book, a few hand-verified towns, or a documented status
(R3 - Venice already meets box 4). Session 5 (boxes 1 + 6): docs/lead_artists.md (per source: what it is,
where the files live (URLs/categories/IA ids), the drawing's date (+ the noted upload-only case), exactly which
files staged, documented drops, the --verify output (re-run it - it is deterministic) with the checked date,
the Q50195/Q773853/Q16139 trap notes) + tests/test_src_artists.py (prep plan section 4: the join; the table
completeness; the offline evidence check over the staged files with a NEGATIVE CONTROL built in-test - the
Imola row with the bad P625 44.353/11.715, never written, must be reported not kept; the golden file via
--golden, checked/date_commons normalized; run under .venv/bin/python, socket-blocking fixture) + tick the
rest (box 4 last - it is the count check).

**Re-read on return:** fit/evidence.py:check_caption (my caption_coords rows check offline from stored fields
only: norm(named) in norm(title+desc), stored distance reproduces dist_m +/-1 km, <=50 km); fit/evidence.py:
source_tables (hand_tied registry = pipeline/sources.py only; if it ever extends to fit/src_*.py, convert my
rows to hand_tied and drop the hand record); fit/evidence.py:record (skips rows with rec==evidence/1, so
211's record runs leave my rows alone).

**Invariants:** staged files are append-only + idempotent on (site,title) - never rewrite an existing line;
do not touch fit/evidence.py (not in my Touches); the GAp scans must never be staged (commons.NO "google" +
commons.rows() re-drop, DECISIONS 2026-10-11); Civitates/Merian per-book paths go in the Touches line BEFORE
writing them.
