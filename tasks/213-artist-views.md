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
**Step 2 done (iteration 24, 2026-10-11): Imola pinned, triaged, staged; Venice staged; boxes 2 + 3 ticked.**
UNCOMMITTED (harness-saved, next agent commits with the rest): `fit/src_artists.py` (SITES[Q50195] centre now
the walled town 11.7112/44.3535; docstring + drop comments corrected), the three staging files (2 sites /
2 pictures / 2 classified rows), `docs/lead_artists.md` (full Imola + Venice sections, the 2026-10-11
`--verify` block verbatim, book stub, offline-check output).

**MAJOR CORRECTION (the prep was wrong):** the prep's "Imola old-town centre ~ 44.245 N, 12.367 E" was
CERVIA on the Ravenna coast (~50 km SE of Imola); the prep then mislabelled Q50195's P625 as "bad, 53 km NW
of the town". The truth (verified live this session): real Imola = 44.353 N, 11.715 E (NE of Bologna, on the
Santerno); enwiki infobox 44°21'11"N 11°42'53"E == Q50195 P625 == OSM town node (with the F1 circuit beside
it); P625 was never bad. OSM's comune boundary is mis-drawn (Nominatim shows the urban area as "Imola,
Nuovo Circondario Imolese") - never geocode Imola from OSM/Nominatim, use enwiki/P625. The river in the
drawing is the **Santerno** (Leonardo labels it "Sant'Arno", mirror script - read off the sheet; the prep's
"Savena crossing" was a second error). The sheet: south-up (per the literature), walled town at the centre
of the circular view, Rocca Sforzesca at its edge = the identifying feature. **The PITFALLS entry at line
~209 ("Q50195 (Imola) carries a bad P625 (~53 km NW)...") is now WRONG in its Imola half - fix it in your
first session** (keep the Venice half: search "Venice" hits Q773853 LA 9891 km first; that trap is real and
is why the hand record stands). New pitfall worth an entry: Nominatim `viewbox` is left,top,right,bottom =
min_lon,MAX_lat,max_lon,min_lat (I burned a session passing lon,lat,lon,lat).

**Triage verdicts (one paced commons.info run, 2026-10-11, all PD, all pass keep()):** "File:Leonardo da
vinci, Town plan of Imola.jpg" (1030x774, circa 1502) = ANOTHER SCAN OF THE SAME RCIN 912284 SHEET (verified
visually) -> drop, one row per picture; "File:...RCIN 912686, Recto Sketches..." (1517x2000 portrait,
undated) = different work (the measured survey sketches) -> drop; "File:Imola 1705.jpg" (942x710, 1705,
Antonio Ferri) = flat plan, other hand, other century -> drop. GAp Imola scan (6164x4545) stays a
commons.NO "google" drop. All five verdicts are in docs/lead_artists.md.

**State:** `--check` PASSES (2/2 caption_coords, no join problems, exit 0) - last test run. Boxes 2, 3
TICKED. Boxes 1, 4, 5, 6 open. Imola row: date "" year 1502 (file page has no DateTimeOriginal - the noted
box-1 case, documented in the lead doc); Venice row: date 1500. Staged region "Italy" (built sites show
"US" until 214 merges - transient, DECISIONS 2026-10-11).

**Next step - session 3:** (0) Add `tests/golden/src_artists_sample.json` to this task's `Touches:` line (a new
artifact of this task, not yet listed) and commit, before any golden write. (1) Fix the PITFALLS line-209 entry as above (+ optional Nominatim-viewbox entry).
(2) Books (box 5, stretch): check IA metadata for the BOOKS-table ids (208's OQ-2 recipe in tasks/prep/208.md
for BookReader vs .pdf); if indexable: add `data/books/triage/<ia>.*` + `data/books/lists/<ia>.json` (the
exact ia ids you write) to THIS task's Touches line FIRST, then work one book, a few hand-verified towns, or
document a drop; the books.py:BOOKS entry is a shared-module change -> file a new task (lowest free 2xx,
Depends on: none, Touches: pipeline/books.py etc.), never write it. (3) `--golden` (writes
tests/golden/src_artists_sample.json from the staged rows - path in Touches after step (0)). (4) Session 4: tests/test_src_artists.py per prep plan section 4 - the join; table completeness (rows' qid
== the module table; dates 1502/1500; extras rows complete incl. region "Italy", kind "town"); offline
evidence check (check(FILES_ARTISTS, NO_BOOKS, catalog=EXTRAS_ARTISTS) exit 0, zero FAIL) with a NEGATIVE
CONTROL built in-test: the Imola row with the WRONG centre 44.245/12.367 (Cervia - the prep's error, now
~53 km from the site point) must be reported FAIL, not kept; golden compare. Socket-blocking fixture; run
under .venv/bin/python. (5) Tick the rest: box 1 (when the book section is final), box 5, box 6, box 4 LAST
(the count check). (6) At the done-claim: record in 211's Hand-over that the *_artists* staging files (+ any
per-book files) exist and must be merged (prep R6). 801 is DONE (its evidence.py is on main - part/sheet
kinds exist; my rows are unaffected).

**Re-read on return:** fit/src_artists.py:stage (idempotent on (site,title) - re-running is a no-op now the
files exist; `--dry` shows "staged: 0"); fit/evidence.py:check_caption (caption_coords: named in
norm(title+desc), stored dist reproduces dist_m ±1 km, ≤50 km - my rows store dist 0.0, place = site point);
fit/evidence.py:record (skips rec==evidence/1 - 211's record runs leave my rows alone); fit/evidence.py:
source_tables (hand_tied registry = pipeline/sources.py only - I use caption_coords, not hand_tied).

**Invariants:** staged files append-only + idempotent - never rewrite an existing line; do not touch
fit/evidence.py (not in my Touches); GAp scans never staged; per-book paths into the Touches line BEFORE
writing; box 4 last; the golden file regenerates only via `--golden` for an intended change.
