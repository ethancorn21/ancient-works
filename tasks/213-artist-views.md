Status: open
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
**Iteration 27 (2026-10-11): triage run FINISHED (A 292/292 + F 118/118, both complete & stable, process exited - COMMIT THEM FIRST THING: they are uncommitted on disk, no errors in either file). List transcription started: 16 leaves visually read (findings below) - no list file written yet. Context limit hit mid-image-reading.**

**The background run:** /tmp/civitates_triage.py finished: DONE printed; A = 292 unique rows (no gaps, no errors, no dupes), F = 118 rows (0 error rows; 239 figure readings: 222 view / 11 plan / 6 other). No re-run needed. Files: data/books/triage/civitatesorbiste00brau.{A,F}.jsonl.

**What I read (triage images are LOCAL: data/raw/books/civitatesorbiste00brau/triage/nNNNN.jpg = leaf n+1; re-reading is cheap - the harness drops old images from context, so re-read any leaf you need):**
- **n58 = bird's-eye PLAN of Paris** (poem cartouche, Cum Privilegio) -> kind s. **n85, n90, n98, n109 = bird's-eye PLANS** (Flemish/German: n85 arms + 46-item Dutch street legend; n90 two arms; n98 = the famous Antwerp plan, cartouche "...nobile in Brabantia oppidum...", n109 = Amsterdam plan, saltire arms, "DEN AEM STEL", 32-item legend; note n109's plate PRECEDES its title leaf n110 AMSTELEDAVM, and n225 Messina view precedes title n226 - sections interleave both ways). **n237/238 = the two Jerusalem PLANS** (old: numbered walls/Temple/Tower of David/36-item legend + top text block; new: "Nova urbis Hierosolymitanae descriptio", Declaratio A-Z, Cum Privilegio vignette) -> kind s.
- **n157/158 are NOT maps**: sheets of small town VIEWS of the 13 Swiss cantons (n157: Schwyz, Underwalden, Tugium, Zug, Bern, Fryburg, Solothurn; n158: Glaris, Basel, Lucern, Uri, Schaffhausen, Appenzell + one cut off; titles "DECEM ET TRIA LOCA CON[...]/FEDERATORVM HELVETIAE") -> kind o. (The iteration-26 hand-over called these maps - corrected.)
- **n202 = the famous oblique BIRD'S-EYE VIEW of Venice** (153-item Italian legend) -> kind o. **n194 = two Vienna views** (top: S. Steffans labelled + imperial double-headed eagle; bottom: cartouche "prima & regia... ad Danubium") -> o. **n214 = Ancona view** (star fort, 35-item legend), **n217 = Naples view 1** (cartouche "Hæc est nobilis & floris illa NEAPOLIS...Parthenope", 52 items), **n218 = Naples view 2** (104 items), **n225 = Messina view** (106 items; title leaf n226) -> all o.
- **n52 = double title page** (CIVITAS BVRGENSIS + S. SEBASTIANI OPP., printed page 6 at bottom); **n54 = the two matching views** (Burgos, inscription read by A = "bVRGOS celebris et antiqua Hispaniae civitas, quae Auca, Brautum, Masburgi, Li conitiurgis, nomina habet"; San Sebastián "SANCT. SEBASTIANVM vulgo Donostien..."). **n53 = two more plates** (a view with a 46-item Dutch legend + a sea view with a gallows galleon) - probably the 2nd/3rd Barcelona plates (section: n49 BARCELONA title, n50 "Cum Pristelio"): CONFIRM by reading n50/n51. **n187/n199 = the faded BLANK VERSO of the fold-outs** (plates are n186 Augsburg, n198 Milan; "RFPCB" library stamp) - they are figure leaves but carry no picture; record them honestly in the list (kind u, title = verso of the fold-out).

**Structure rule found:** each city section = a TITLE LEAF (big Latin title + history text; A reads it) + 1-3 PLATE leaves (views/plans; A caption = the plate's own inscription, legend or poem, often empty). A plate's city = its section (nearest title leaf, either side). The book has NO printed town list, so `figures` entries key on leaf n, `page` = printed number ONLY for leaves 193-196 (1-4) and 280-284 (I-V) (data/raw/books/civitatesorbiste00brau/civitatesorbiste00brau_page_numbers.json; all other leaves null).

**Pitfalls learned (write to PITFALLS.md):** (1) the hOCR page index for civitatesorbiste00brau is MISALIGNED with the jp2 leaf sequence (drift 0-2 leaves; e.g. hOCR leaf 85 = the Brussels title text that A reads on leaf 87) - `books_ia.page_texts()`/ocr_captions are UNRELIABLE for this book; the image-based A rows are the ground truth (217 must not use page_texts for civitates). (2) Stage F under-detects plans in this book (its prompt is earthwork-biased: only 11/121 flagged plan while I visually confirmed n58/n85/n90/n98/n109/n237/n238 are plans) - 217's view-as-drawing index should not trust F's "plan" label here.

**Still to do (order):** (1) COMMIT the A/F triage files (+ any lead-doc state). (2) Finish the visual set: n209 (Rome), n205/n206 (Florence), n198 (Milan fold-out: view or plan?), n197 (Armes de Milan - arms page, excluded from drawings), n86/n97/n193 (Brussels/Antwerp/Vienna title leaves), n186 (Augsburg fold-out), n50/n51 (confirm n53 = Barcelona). (3) Write data/books/lists/civitatesorbiste00brau.json: {"plates": null, "figures": [{"fig": <leaf n 0-based>, "title": <inscription as printed, or city name from the section title leaf when the plate has none>, "page": null-or-printed, "kind": "o"|"s"|"u", "kind_by": "hand" for leaves I read / "A" for the rest (documented in the lead doc)}]} - every one of the 121 figure leaves gets an entry; + .map.json = [] (list_pages maps only kind s/u and has no page numbers for these leaves). (4) Fix the lead-doc books section: list written per this scheme; FEDERATORVM = views not maps; n187/n199 = fold-out versos; the hOCR/F pitfalls; the verified-towns QIDs (next). (5) Hand-verified towns (7): Rome, Vienna, Florence, Milan, Venice, Brussels, Antwerp - paced Wikidata (label/P625/P373; search-trap check like Venice-CA) -> record in fit/src_artists.py:BOOKS["civitates"]["sites"] + lead doc. (6) `.venv/bin/python fit/src_artists.py --check` (last passed 2/2 iteration 24; staging files untouched since) + `--golden` -> tests/golden/src_artists_sample.json (never hand-edited). (7) Write tests/test_src_artists.py per prep §4 (join; table completeness; offline evidence check exit 0 + NEGATIVE CONTROL: Imola row with the Cervia point 44.245/12.367 must FAIL; golden compare; socket-blocking fixture; run under .venv). (8) Tick boxes 1, 5, 6, then box 4 LAST. (9) Note in 211's Hand-over: *_artists* staging files + the civitates per-book files (triage A/F + lists) must be merged (R6). (10) PITFALLS entries: LLM ports 8080-8082 vs books.py 18080/18081 (do once, here or in 215), the hOCR misalignment, the F under-detection, long data jobs outlive sessions (check file stability before committing).

**State of the boxes:** 2, 3 ticked. Box 5 in progress (triage done & ready to commit; list transcription half-read; lead doc has iteration-26 books section that must be updated per (4) above). Boxes 1, 4, 6 open.

**Invariants (unchanged):** staged files append-only + idempotent; never touch fit/evidence.py, pipeline/books.py, pipeline/books_lists.py, data/books/index.jsonl, validation.json (215/216/217 own the shared modules); GAp scans never staged; box 4 last; golden only via `--golden`; the LLM service on 8080-8082 is shared (the run is done now - no more load from this task).

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/213-artist-views.md` (open) - hand-over: **Step 2 done (iteration 24, 2026-10-11): Imola pinned, triaged, staged; Venice staged; boxes 2 + 3 ticked.**

## Next open tasks
- `tasks/202-propose.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 213 DECISION: module shape - SITES table + per-source row tuples, stdlib-only at the top
fit/src_artists.py: SITES{qid: site facts (id/name/lon/lat/place/region/kind/wikipedia/cat/p625/note)};
SOURCES{name: rows + display label + p-field} for the two image-level sources (row tuple (title, qid, label,
opts) - a variant of sources.py: the region lives on the site, since all its rows share it); BOOKS{civitates,
merian} with the IA identifiers (per-book flow is session 4; the books.py:BOOKS entry is a shared-module
change -> file a task, never write it). Top-level imports are stdlib only (json/os/sys/time); commons/evidence
are imported lazily inside functions because commons->aw needs numpy (absent from the system python3) - live
commands run under .venv/bin/python. CLI: --verify (live QID re-check, prints the search traps next to the
table values for the lead doc), [--dry] (stage), --check (offline join + evidence.check over the staged rows;
books arg = a never-existing path), --golden (normalized staged rows -> tests/golden/src_artists_sample.json,
checked/date_commons zeroed). check_staged() join: file rows may name staged OR existing sites (box-3 rule:
existing QID -> picture row on the existing site id, no new catalog entry); staged ids/QIDs must not pre-exist;
classified rows 1:1 with file rows.

### 2026-10-11 213 DECISION: the prep's Imola "centre 44.245 N, 12.367 E / bad P625 53 km NW" was wrong - that point is Cervia; P625 is the correct city point
The prep notes placed Imola's old town at 44.245 N, 12.367 E and, seeing Q50195's P625 (44.353, 11.715) far
from it, called the P625 "bad, ~53 km NW of the town". Verified live (2026-10-11): the prep point is CERVIA
on the Ravenna coast (~50 km SE of Imola); the real city is at 44.353 N, 11.715 E, where THREE independent
sources agree: the enwiki infobox (44°21'11"N 11°42'53"E), Wikidata P625, and the OSM town node (with the F1
circuit beside it and the Santerno - "Fiume Santerno" at 44.3606/11.7104 - running through the urban area).
So the "53 km trap" was the distance between two wrong values. Consequences: (a) the site point is the
walled town's centre, 11.7112/44.3535 (Piazza del Duomo, OSM) - the centre of the sheet's circular view, not
the modern city point; (b) the prep's "Savena crossing" was a second error - the drawing's river is the
Santerno, which Leonardo labels "Sant'Arno" (mirror script, read off the sheet); the view is south-up per
the literature; (c) the evidence story changes: for Imola the live record route resolves the RIGHT QID (the
hand record still stands to pin the walled centre, deterministic and offline); the name-search trap that is
REAL and documented is Venice (first hit with P625 = Q773853 Venice, California, 9891 km). Side note: OSM's
comune boundary for Imola is mis-drawn (Nominatim displays the urban area as "Imola, Nuovo Circondario
Imolese", and the admin relation's centre sits 8 km north of the city) - a reason never to geocode Imola
from OSM/Nominatim. The PITFALLS entry "Q50195 (Imola) carries a bad P625..." must be corrected accordingly
(pending in the next session; I cannot edit PITFALLS from the context-limit hand-over step).

### 2026-10-11 213 DECISION: Imola triage (one paced commons.info run) + staged both image-level sites; --check 2/2 PASS
Triage of the Imola candidates (all Public domain, all pass commons.keep()): "File:Leonardo da vinci, Town
plan of Imola.jpg" (1030x774, circa 1502) verified by eye to be ANOTHER SCAN OF THE SAME RCIN 912284 SHEET
(same view, walls, river, margin legend/notes) -> dropped as a duplicate picture; "File:...RCIN 912686, Recto
Sketches of the street plan of Imola.jpg" (1517x2000 portrait, undated) = a different work (measured survey
sketches with block grids and fortress details) -> dropped; "File:Imola 1705.jpg" (942x710, 1705, Antonio
Ferri) = a flat plan by another hand from another century -> dropped (not one of the task's four GOAL
sources). The GAp Imola scan stays a commons.NO "google" drop. Staging (`.venv/bin/python fit/src_artists.py`)
wrote extras_artists.jsonl (imola-q50195, venice-q641; region "Italy" - transient "US" display until 214
merges), files_artists.jsonl (2 rows with hand-recorded caption_coords evidence; Imola date ""/year 1502 -
the file page has no DateTimeOriginal, the noted box-1 case; Venice date 1500) and classified_artists.jsonl
(2 rows, p_birdseye 1.0, by hand). `--check` then passed: 2/2 caption_coords, no join problems, exit 0
(offline). Boxes 2 and 3 ticked (the hand-checked table + existing-QID rule were done in session 1 and are
unchanged in shape). Remaining: box 5 (Civitates/Merian book work or documented status), box 6
(tests/test_src_artists.py + golden), box 1 (lead doc final), box 4 (count check, last). docs/lead_artists.md
is written for Imola + Venice (uncommitted, harness-saved).

## Project-wide driver notes (newest)

### 2026-10-10 DRIVER: .venv could not be built from requirements.txt
    ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    Every package needs a pinned version and hash (AGENTS.md, Research and packages); full pip output: .agent/reports/venv.txt

### 2026-10-11 agent/a (213) hand-over status
    Books step pushed: civitatesorbiste00brau = Liber secundus (1575); stage-A triage running in background
    (pid 1657419, /tmp/civitates_triage.py, LLM ports 8080-8082 patched in-process - books.py's 18080/18081
    are stale, filed as task 215; A was 262/292 at hand-over, F pending). Tasks 215/216/217 filed (shared
    book-machinery gaps). Lead-doc books section rewritten (UNCOMMITTED: docs/lead_artists.md, task files).
    data/books/triage/civitatesorbiste00brau.A.jsonl is still growing from the background run - wait for
    DONE in /tmp/civitates_triage.log before committing it. Next: hand list transcription, --golden, test.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/213-artist-views.md` (open) - hand-over: **Iteration 27 (2026-10-11): civitates triage COMPLETE (A 292/292 + F 118/118, zero errors) and committed; 16 figure leaves visually read (7 plans incl. both Jerusalem plans; FEDERATORVM = views not maps; n187/n199 = fold-out versos); list structure decided, list file NOT yet written. Next: finish ~10 image reads, write lists/civitatesorbiste00brau.json + .map.json, 7 verified-town QIDs, --golden, test, boxes 1/5/6 then 4. PITFALLS owed: hOCR misalignment, F plan under-detection, LLM ports 8080-8082.** (iteration 26: books step resumed, lead-doc books section rewritten, tasks 215-217 filed)

## Next open tasks
- `tasks/202-propose.md`
- `tasks/215-books-llm-ports.md`
- `tasks/216-view-books-entries.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 213 DECISION: books step (box 5) - civitates worked in per-book files; views can't pass the machinery's plan-only index; shared-module gaps filed as 215/216/217
civitatesorbiste00brau identified as **Liber secundus (1575)**, 292 leaves (from its imperial-privilege OCR
page: "PRIVILEGIUM CAESAREAE MAJESTATIS ... Hogenberg ... vanden Noeurt ... Bruin ... Ciuitates Orbis
Terrarum"). All six IA items in the BOOKS table are BookReader streams (jp2 + PDF + hocr OCR, unrestricted)
- the OQ-2 style question is settled: every one is indexable by fetch/triageA. Stage A triaged the volume
(background run this session; 262/292 at hand-over, 0 errors so far) - view plates come back
other_illustration, the Jerusalem plan (n237/238) plate_site_plan. The DECISIVE fact: books_lists's
taxonomy is kind s = plan view, kind o = "views, sections alone, ..." and cmd_index emits rows only for
kind s - so a book of town views triages cleanly but indexes to nothing; the views cannot reach the map
through the machinery as it stands. GOAL point 5 (2026-10-10) says views count as drawings, so the gap is
real, not a 213 problem to fix inside its Touches. Decision: 213 owns the per-book files only (triage
A/F, the hand list, the lead-doc status); the machinery extension is filed as three one-module tasks -
215 (books.py LLM ports; no deps), 216 (books.py BOOKS entries for the six items; Depends 213+215), 217
(books_lists lists + view-as-drawing index; Depends 216). No picture rows are staged by 213 for the books
(there is no per-file Commons row to stage; the rows come via 211's rebuild once 217 lands).

### 2026-10-11 213 DECISION: books.py LLM_URLS (18080/18081) are stale - the replicas serve on 8080-8082; 213 works around in-process
books.py run_stage() exits "LLM tunnels 127.0.0.1:18080/18081 are down" on this machine: ss -ltnp shows no
listener on 18080/18081, while the llmtunnel ssh forwarders (user llmtunn, running since Oct 6: -L
127.0.0.1:8080/8081/8082 -> 10.0.10.75) answer /v1/models 200 on all three ports. 213 cannot edit
pipeline/books.py (not in its Touches), so the throwaway driver /tmp/civitates_triage.py patches
books.LLM_URLS in-process to the three live ports and injects BOOKS["civitates"] = dict(ia=
"civitatesorbiste00brau", region="Italy", year=1575); the run is idempotent (latest row per n; error rows
excluded from done). Filed as task 215 (port fix + a PITFALLS entry). The same trap will hit 207/208/209
when they reach their triage B/F stages - 215 is their unblock.

### 2026-10-11 213 DECISION: iteration 25's orphaned triage process kept appending after the driver's snapshot commit
The driver's "uncommitted work after iteration 25" commit captured civitatesorbiste00brau.A.jsonl at 191
lines; the orphaned run kept appending until 04:03 (211 pages, n 0-210 complete, no error rows) and exited.
Nothing was corrupt: the file is append-only and run_stage/latest() is re-runnable (done = rows without
error). Lesson: before committing (or trusting) a data file a background job may still be writing, check
its mtime against now and whether a writer process is alive; otherwise the driver's snapshot commits
mid-growth states. (Recorded here because the context-limit step allowed only DECISIONS/tasks edits; the
next agent files the PITFALLS entry.)

## Project-wide driver notes (newest)

### 2026-10-10 DRIVER: .venv could not be built from requirements.txt
    ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    Every package needs a pinned version and hash (AGENTS.md, Research and packages); full pip output: .agent/reports/venv.txt
