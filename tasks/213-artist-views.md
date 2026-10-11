Status: done
# 213: Artists' views - Leonardo's Imola, Barbari's Venice, Braun & Hogenberg, Merian
Depends on: 200
Touches: fit/src_artists.py, data/catalog/extras_artists.jsonl, data/commons/files_artists.jsonl, data/commons/classified_artists.jsonl, data/books/triage/civitatesorbiste00brau.A.jsonl, data/books/triage/civitatesorbiste00brau.F.jsonl, data/books/lists/civitatesorbiste00brau.json, data/books/lists/civitatesorbiste00brau.map.json, docs/lead_artists.md, tests/test_src_artists.py, tests/golden/src_artists_sample.json

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
- [x] Verified before use (docs/lead_artists.md): for each source, what it is, where its
      files live, the drawing's date (recorded on the row - where a repository only has
      an upload date, the known drawing date is used and noted), and exactly which files
      are staged; unusable sources or files (paywalled, too small, no place tie) are
      listed with the reason - a documented drop beats a guessed row.
- [x] Imola staged as a new site: an extras_artists.jsonl entry (id, name, place,
      lon/lat, region, kind, QID, wikipedia), a files_artists.jsonl row for the plan in
      the files.jsonl shape with the 200 evidence field, and a classified_artists.jsonl
      row; the row notes no open LiDAR here (aerial-photograph ground,
      FITKIT_GROUND=aerial). fit/evidence.py check passes offline on every staged row.
- [x] The hand-checked file -> QID table lives in fit/src_artists.py (the sources.py
      pattern): every QID verified against its label and coordinates - a name search
      alone gives the wrong place (the Barnard Castle trap); a picture of a site whose
      QID is already in the catalog gets a picture row for that existing site id, no new
      catalog entry.
- [x] At least Imola plus one further source (Venice, one Civitates town, or one Merian
      view) is staged, or docs/lead_artists.md accounts for each unstaged source with a
      verified reason.
- [x] If Civitates Orbis Terrarum or the Topographia turn out to be Internet Archive
      books indexable with pipeline/books.py, work in per-book files only
      (triage/<ia>.*, lists/<book>.json) and add those exact paths to this task's
      Touches line before writing them - never the shared index.jsonl or
      validation.json (211 rebuilds both).
- [x] Test (no network): the staged files join (every file row names a staged or
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
**Iteration 39 (2026-10-11): 213 DONE** - all six boxes ticked, Status: done. Subtasks 213a (civitates
hand list + lead-doc books section) and 213b (the seven book-town QIDs, --golden, the test, lead-doc
final) were already done and committed; this session verified the parent's own boxes fresh and closed
the task. No Re-read items left.

**What this session verified (all re-run today, all passed):**
- `.venv/bin/python fit/src_artists.py --check`: exit 0, no join problems, 2/2 PASS caption_coords
  (imola-q50195, venice-q641).
- `.venv/bin/python fit/src_artists.py --golden`: ZERO diff on tests/golden/src_artists_sample.json -
  the golden pins the staged rows exactly (regenerate only for an intended change).
- `.venv/bin/python -m pytest tests/ -q`: 33/33 green (incl. tests/test_src_artists.py: the join, the
  table, the offline evidence check with the Cervia negative control, the golden compare, under the
  socket-blocking fixture).
- Box 4 (the count, checked last): Imola (the anchor, Leonardo 1502 RCIN 912284) + Venice (Barbari
  1500, Museo Correr) = two sources staged, 2 rows per staging file; the lead doc accounts for every
  unstaged source (the other five IA books: present as BookReader streams, untriaged - 216/217).
- Box 5: the four civitates per-book paths (triage A/F, lists .json/.map.json) are written and
  declared in the parent's Touches line; `git diff main...HEAD` over index.jsonl / validation.json /
  pipeline/ / fit/evidence.py is empty (no shared-module writes).
- Box 1: docs/lead_artists.md read in full - complete for all four sources (what/where/dating with
  the upload-only note/exactly-staged files/drops with reasons; the 8-QID verification table with the
  search traps; the six-book cite table; the per-book status).

**Owed work, now done here:** the R6 note is written in tasks/211-merge-build.md ## Hand-over (merge
the *_artists* staging files; the civitates index rows wait on 217 - zero rows from the book before
217 is not a 211 failure). PITFALLS: the four entries filed (LLM ports 8080-8082 vs books.py's stale
18080/18081; civitates hOCR index misaligned 0-2 leaves; A/F plan labels unreliable in both
directions; long background data jobs outlive sessions - the driver snapshot can commit a mid-growth
file). The corrected Q50195-Imola entry (P625 is the correct city point; the prep's point was Cervia)
was already in place.

**State (for anyone re-entering this thread):** the staged files (extras/files/classified
*_artists.jsonl) and the civitates per-book files are FINAL - do not re-stage or re-triage. 211
consolidates (its Depends omits 213 by design; wave order 2 -> 4 covers it). 215 -> 216 -> 217 extend
the book machinery so Liber secundus's views index as drawings. 212's cover then fits the two new
sites: Imola is the aerial-photograph anchor (walled-centre 11.7112/44.3535; the Rocca Sforzesca is
the strongest anchor pair; the Santerno crossing and church footprints carry the fit), Venice is
likely a review item (R2: the woodcut spans ~8 km against the 2000 m box).
